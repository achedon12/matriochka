"""Small offline synthesizer for the mod's sounds: oscillators, envelopes, filters, reverb and instruments.

Everything works on whole numpy buffers (mono, 44.1 kHz, float64). Filters run in the frequency domain, so they
are zero-phase and cost one FFT. Every random draw goes through a numpy Generator the caller seeds, so a sound is
rebuilt bit for bit from its recipe. Used by tools/sound.py; nothing here knows about Minecraft.
"""
import numpy as np

SR = 44100


def secs(n):
    return int(round(n * SR))


def time(dur):
    return np.arange(secs(dur)) / SR


def silence(dur):
    return np.zeros(secs(dur))


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ envelopes
def ramp(n, a):
    """Raised-cosine ramp of n samples (0 to 1)."""
    if n <= 0:
        return np.ones(0)
    return 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    """Attack, decay, sustain and release over n samples; the release always ends on zero."""
    e = np.full(n, s, dtype=float)
    na, nd, nr = secs(a), secs(d), secs(r)
    na = max(1, min(na, n // 3))
    nr = max(1, min(nr, n - na - 1))
    nd = max(0, min(nd, n - na - nr))
    e[:na] = ramp(na, 1)
    if nd:
        e[na:na + nd] = 1 - (1 - s) * ramp(nd, 1)
    e[n - nr:] *= ramp(nr, 1)[::-1]
    return e


def perc(n, a=0.002, tau=0.3, tail=0.02):
    """Struck envelope: fast attack, exponential decay, short fade to zero at the end."""
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    na = max(1, secs(a))
    e[:na] *= ramp(na, 1)
    nt = max(1, min(secs(tail), n))
    e[n - nt:] *= ramp(nt, 1)[::-1]
    return e


def fade(x, fin=0.01, fout=0.01):
    x = x.copy()
    ni, no = min(secs(fin), len(x)), min(secs(fout), len(x))
    if ni:
        x[:ni] *= ramp(ni, 1)
    if no:
        x[len(x) - no:] *= ramp(no, 1)[::-1]
    return x


def smooth_noise(rng, n, rate, lo=0.0, hi=1.0):
    """Slow random curve (rate in changes per second) between lo and hi, cosine-interpolated."""
    pts = max(2, int(n / SR * rate) + 2)
    v = rng.uniform(lo, hi, pts)
    pos = np.arange(n) / n * (pts - 1)
    i = np.floor(pos).astype(int)
    i = np.minimum(i, pts - 2)
    f = pos - i
    f = 0.5 - 0.5 * np.cos(np.pi * f)
    return v[i] * (1 - f) + v[i + 1] * f


# ------------------------------------------------------------------ filters (frequency domain)
def _shape(n, fn):
    f = np.fft.rfftfreq(n, 1 / SR)
    return fn(f)


def filt(x, fn):
    """Applies a magnitude response fn(freqs) to x, zero-phase."""
    if len(x) == 0:
        return x
    n = len(x)
    pad = 1 << int(np.ceil(np.log2(n + 2048)))
    X = np.fft.rfft(x, pad)
    X *= _shape(pad, fn)
    return np.fft.irfft(X, pad)[:n]


def lowpass(x, fc, order=2):
    return filt(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return filt(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def bandpass(x, lo, hi, order=2):
    return filt(x, lambda f: 1 / np.sqrt(1 + (f / hi) ** (2 * order)) / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order)))


def resonance(x, fc, q=8.0, gain=1.0):
    """Adds a resonant peak at fc (a body, a tube, a cavity)."""
    return filt(x, lambda f: 1 + gain / (1 + (q * (f / fc - fc / np.maximum(f, 1e-3))) ** 2))


def noise(rng, dur):
    return rng.standard_normal(secs(dur))


def colored(rng, dur, lo, hi, order=2):
    return bandpass(noise(rng, dur), lo, hi, order)


def brown(rng, dur, fc=300):
    return lowpass(noise(rng, dur), fc, 1)


# ------------------------------------------------------------------ oscillators
def phase_of(freq):
    """Phase (radians) of a time-varying frequency curve."""
    return 2 * np.pi * np.cumsum(freq) / SR


def sine_sweep(f0, f1, dur, curve=1.0):
    n = secs(dur)
    k = np.linspace(0, 1, n) ** curve
    f = f0 * (f1 / f0) ** k
    return np.sin(phase_of(f))


# ------------------------------------------------------------------ reverb
_IR = {}


def impulse(t60, bright=0.5, seed=7, pre=0.012):
    key = (t60, bright, seed, pre)
    if key in _IR:
        return _IR[key]
    rng = np.random.default_rng(seed)
    n = secs(t60 * 1.2)
    t = np.arange(n) / SR
    ir = np.zeros(n)
    # three bands with their own decay: highs die first, as in a wooden room
    for lo, hi, k in ((20, 700, 1.0), (700, 3500, 0.7), (3500, 16000, 0.35 + 0.4 * bright)):
        band = bandpass(rng.standard_normal(n), lo, hi, 2)
        ir += band * np.exp(-6.9 * t / (t60 * k))
    ir[:secs(0.004)] *= ramp(secs(0.004), 1)
    ir = np.concatenate([np.zeros(secs(pre)), ir])
    ir /= np.sqrt(np.sum(ir ** 2))
    _IR[key] = ir
    return ir


def reverb(x, t60=1.8, mix=0.25, bright=0.5, seed=7, pre=0.012):
    """Convolution reverb; the result is longer than x by the whole tail."""
    if mix <= 0:
        return x
    ir = impulse(t60, bright, seed, pre)
    n = len(x) + len(ir)
    pad = 1 << int(np.ceil(np.log2(n)))
    wet = np.fft.irfft(np.fft.rfft(x, pad) * np.fft.rfft(ir, pad), pad)[:n]
    dry = np.concatenate([x, np.zeros(len(ir))])
    return dry * (1 - mix * 0.5) + wet * mix


def trim(x, floor=0.001, fout=0.05):
    """Cuts the silent end of a sound (below floor of its peak) and fades the last fout seconds."""
    m = np.max(np.abs(x)) if len(x) else 0
    if m <= 0:
        return x
    loud = np.nonzero(np.abs(x) > m * floor)[0]
    end = min(len(x), (loud[-1] if len(loud) else len(x)) + secs(fout))
    return fade(x[:end], 0, fout)


def add(*xs):
    """Sums signals of different lengths (all start at zero)."""
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[:len(x)] += x
    return out


def tail(x, dur):
    """Room for a reverb tail."""
    return np.concatenate([x, silence(dur)])


# ------------------------------------------------------------------ mixing
def mix_into(buf, x, at):
    """Adds x into buf starting at sample index at, growing buf when needed. Returns buf."""
    end = at + len(x)
    if end > len(buf):
        buf = np.concatenate([buf, np.zeros(end - len(buf))])
    buf[at:end] += x
    return buf


def place(parts, dur=None):
    """parts: [(start seconds, signal)] mixed into one buffer."""
    buf = np.zeros(secs(dur) if dur else 1)
    for at, x in parts:
        buf = mix_into(buf, x, secs(at))
    return buf


def normalize(x, peak=0.89):
    m = np.max(np.abs(x)) if len(x) else 0
    return x if m < 1e-9 else x * (peak / m)


def soft_clip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


def loopify(x, xfade):
    """Makes a seamless loop: the extra tail (xfade seconds past the loop length) is cross-faded onto the head
    with equal power, so the end flows into the start without a click."""
    nx = secs(xfade)
    body = x[:len(x) - nx].copy()
    head_in = np.sin(np.linspace(0, np.pi / 2, nx))
    head_out = np.cos(np.linspace(0, np.pi / 2, nx))
    body[:nx] = body[:nx] * head_in + x[len(x) - nx:] * head_out
    return body


def clean(x):
    """Removes DC and sub-sonic rumble below 25 Hz (keeps speakers and Vorbis happy)."""
    return highpass(x - np.mean(x), 25, 2)


# ------------------------------------------------------------------ instruments
def pluck(f, dur, vel=1.0, bright=0.55, pos=0.2, ring=1.0, rng=None):
    """Plucked string (balalaika, gusli): additive partials, higher ones decay faster, slight inharmonicity.
    dur is how long the note is held; the string is damped after it."""
    total = dur + 0.25 * ring
    n = secs(total)
    t = np.arange(n) / SR
    out = np.zeros(n)
    tau0 = 0.9 * ring * (220 / max(f, 60)) ** 0.35
    ph = rng.uniform(0, 2 * np.pi, 40) if rng is not None else np.zeros(40)
    k = 1
    while k * f < 12000 and k <= 36:
        fk = k * f * np.sqrt(1 + 0.00012 * k * k)
        amp = abs(np.sin(np.pi * k * pos)) / k ** (1.35 - 0.6 * bright)
        tau = tau0 / (1 + 0.32 * (k - 1) * (1.2 - bright))
        out += amp * np.exp(-t / tau) * np.sin(2 * np.pi * fk * t + ph[k % 40])
        k += 1
    # the player's finger damps the string after dur
    nd = secs(dur)
    if nd < n:
        damp = np.ones(n)
        damp[nd:] = np.exp(-(t[nd:] - t[nd]) / 0.06)
        out *= damp
    out *= perc(n, 0.0015, 1e9, 0.02)
    return out * vel * 0.5


def tremolo_pluck(f, dur, vel=1.0, rate=11.0, rng=None, **kw):
    """Domra / balalaika tremolo: the same string picked fast, alternating strokes."""
    step = 1 / rate
    parts = []
    t = 0.0
    i = 0
    while t < dur - step * 0.5:
        v = vel * (0.85 if i % 2 else 1.0) * (0.9 + 0.1 * np.sin(t * 3))
        parts.append((t, pluck(f, step * 1.05, v * 0.75, ring=0.5, rng=rng, **kw)))
        t += step
        i += 1
    return place(parts)


def music_box(f, dur=None, vel=1.0, rng=None):
    """Music box comb tine: a pure fundamental, two faint inharmonic partials and a tiny metallic tick."""
    total = 2.6 * (440 / f) ** 0.4 + 0.2
    n = secs(total)
    t = np.arange(n) / SR
    s = (440 / f) ** 0.5
    out = (1.0 * np.exp(-t / (1.4 * s)) * np.sin(2 * np.pi * f * t)
           + 0.16 * np.exp(-t / (0.32 * s)) * np.sin(2 * np.pi * f * 3.01 * t + 0.3)
           + 0.07 * np.exp(-t / (0.11 * s)) * np.sin(2 * np.pi * f * 5.93 * t + 1.1)
           + 0.03 * np.exp(-t / (0.05 * s)) * np.sin(2 * np.pi * f * 9.42 * t + 2.0))
    if rng is not None:
        tick = highpass(rng.standard_normal(secs(0.004)), 4000) * ramp(secs(0.004), 1)[::-1] * 0.08
        out[:len(tick)] += tick
    out *= perc(n, 0.001, 1e9, 0.05)
    return out * vel * 0.45


def bell(f, dur=3.0, vel=1.0, rng=None):
    """Church bell (Risset's partials): bright strike, long hum."""
    ratios = [0.56, 0.92, 1.19, 1.71, 2.0, 2.74, 3.0, 3.76, 4.07]
    amps = [1, 0.67, 1, 1.8, 2.67, 1.67, 1.46, 1.33, 1.33]
    durs = [1, 0.9, 0.65, 0.55, 0.325, 0.35, 0.25, 0.2, 0.15]
    n = secs(dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for i, (r, a, d) in enumerate(zip(ratios, amps, durs)):
        fr = f * r + (1.0 if i == 1 else 0) + (1.7 if i == 0 else 0)
        if fr > 15000:
            continue
        out += a * np.exp(-t / (dur * d * 0.3)) * np.sin(2 * np.pi * fr * t + i)
    out *= perc(n, 0.002, 1e9, 0.1)
    return out / 13 * vel


def flute(f, dur, vel=1.0, rng=None, vib=0.004, breath=0.05):
    """Svirel / wooden flute: soft fundamental, a little breath, vibrato that blooms after the attack."""
    n = secs(dur + 0.12)
    t = np.arange(n) / SR
    bloom = np.clip((t - 0.15) / 0.3, 0, 1)
    freq = f * (1 + vib * bloom * np.sin(2 * np.pi * 5.2 * t))
    ph = phase_of(freq)
    out = np.sin(ph) + 0.28 * np.sin(2 * ph + 0.4) + 0.1 * np.sin(3 * ph + 0.9) + 0.03 * np.sin(4 * ph)
    if rng is not None and breath:
        out += breath * bandpass(rng.standard_normal(n), f * 1.2, f * 4, 2) * 3
    out *= adsr(n, 0.06, 0.1, 0.85, 0.14)
    return out * vel * 0.32


def reed(f, dur, vel=1.0, rng=None, bright=0.5, a=0.08, r=0.25, musette=4.0):
    """Bayan / accordion reed pair: two detuned reeds beat against each other (the musette tremolo)."""
    n = secs(dur + r)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-musette / 2, musette / 2):
        fr = f * 2 ** (det / 1200)
        k = 1
        while k * fr < 9000 and k <= 18:
            amp = (1 / k ** (1.6 - 0.7 * bright)) * (1.0 if k % 2 else 0.6)
            out += amp * np.sin(2 * np.pi * fr * k * t + k * 0.7 + det)
            k += 1
    out *= adsr(n, a, 0.15, 0.85, r)
    return out * vel * 0.12


def pad(f, dur, vel=1.0, rng=None, a=1.2, r=1.5, bright=0.3):
    """Soft choir-like pad: detuned reeds lowpassed, slow attack and release."""
    x = reed(f, dur, vel, rng, bright=bright, a=a, r=r, musette=7.0)
    return lowpass(x, 900 + 2500 * bright, 2) * 1.3


def frame_drum(vel=1.0, rng=None, pitch=70, dur=0.6):
    """Buben: a skin thump that drops in pitch, a slap and a few jingles."""
    n = secs(dur)
    t = np.arange(n) / SR
    f = pitch * (1 + 0.6 * np.exp(-t / 0.03))
    body = np.sin(phase_of(f)) * np.exp(-t / 0.22)
    out = body
    if rng is not None:
        slap = bandpass(rng.standard_normal(n), 250, 2200) * np.exp(-t / 0.025) * 0.35
        jingle = bandpass(rng.standard_normal(n), 5500, 12000) * np.exp(-t / 0.09) * 0.12
        out = out + slap + jingle
    out *= perc(n, 0.001, 1e9, 0.05)
    return out * vel * 0.7


def wood_block(vel=1.0, rng=None, pitch=900):
    """Lozhki (wooden spoons) / wood block: a short knock with a hollow body."""
    n = secs(0.18)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * pitch * t) * np.exp(-t / 0.025) + 0.5 * np.sin(2 * np.pi * pitch * 2.3 * t) * np.exp(-t / 0.012)
    if rng is not None:
        out += highpass(rng.standard_normal(n), 2000) * np.exp(-t / 0.004) * 0.4
    out *= perc(n, 0.0007, 1e9, 0.02)
    return out * vel * 0.5


def thump(vel=1.0, pitch=55, dur=0.5):
    n = secs(dur)
    t = np.arange(n) / SR
    f = pitch * (1 + 1.2 * np.exp(-t / 0.02))
    return np.sin(phase_of(f)) * perc(n, 0.002, 0.12, 0.05) * vel


def click(rng, vel=1.0, tone=2800, body=900, length=0.06):
    """A wooden or metal click: a noise snap and a short resonance."""
    n = secs(length)
    t = np.arange(n) / SR
    snap = bandpass(rng.standard_normal(n), tone * 0.6, tone * 1.8) * np.exp(-t / 0.003)
    res = np.sin(2 * np.pi * body * t) * np.exp(-t / 0.015) * 0.6
    return (snap + res) * perc(n, 0.0005, 1e9, 0.01) * vel * 0.6


def tick(rng, vel=1.0, pitch=2600):
    """Clock escapement tick."""
    n = secs(0.07)
    t = np.arange(n) / SR
    snap = highpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.0015) * 0.7
    ping = np.sin(2 * np.pi * pitch * t) * np.exp(-t / 0.012) + 0.4 * np.sin(2 * np.pi * pitch * 1.52 * t) * np.exp(-t / 0.007)
    return (snap + ping) * perc(n, 0.0004, 1e9, 0.01) * vel * 0.4


def crackle(rng, dur, density=40, lo=1500, hi=7000, vel=1.0):
    """Random sparse crackles (fire, sparks, wood fibres)."""
    n = secs(dur)
    out = np.zeros(n)
    count = int(density * dur)
    for at in rng.integers(0, max(1, n - secs(0.01)), count):
        ln = int(rng.integers(secs(0.001), secs(0.006)))
        out[at:at + ln] += rng.standard_normal(ln) * np.exp(-np.arange(ln) / (ln / 3)) * rng.uniform(0.2, 1)
    return bandpass(out, lo, hi) * vel


def drip(rng, vel=1.0, pitch=None):
    """A water drop: a short sine whose pitch rises as the bubble closes."""
    p = pitch or rng.uniform(900, 1800)
    n = secs(0.25)
    t = np.arange(n) / SR
    f = p * (1 + 1.4 * (1 - np.exp(-t / 0.02)))
    return np.sin(phase_of(f)) * perc(n, 0.0008, 0.035, 0.02) * vel * 0.5


def groan(rng, dur, pitch=48, vel=1.0):
    """Creaking metal hull under pressure: a low tone bent slowly, with rough friction partials."""
    n = secs(dur)
    t = np.arange(n) / SR
    bend = smooth_noise(rng, n, 1.5, -0.15, 0.12)
    f = pitch * (1 + bend)
    ph = phase_of(f)
    rough = 1 + 0.4 * smooth_noise(rng, n, 30, -1, 1)
    out = (np.sin(ph) + 0.5 * np.sin(2.01 * ph) + 0.3 * np.sin(3.03 * ph) * rough + 0.15 * np.sin(5.1 * ph) * rough)
    out = lowpass(out, 700, 2)
    fr = bandpass(rng.standard_normal(n), 300, 1400) * 0.25 * smooth_noise(rng, n, 6, 0, 1)
    return (out + fr) * adsr(n, dur * 0.3, 0.1, 0.9, dur * 0.4) * vel * 0.4


def heartbeat(vel=1.0, pitch=48):
    a = thump(vel, pitch, 0.35)
    b = thump(vel * 0.7, pitch * 0.92, 0.4)
    return place([(0, a), (0.24, b)])


def wind(rng, dur, lo=200, hi=1600, gust=0.25, whistle=0.0):
    """Wind: three noise bands with their own slow swells; an optional whistle that follows the gusts."""
    n = secs(dur)
    out = np.zeros(n)
    for i, (a, b) in enumerate(((lo, lo * 2.5), (lo * 2, hi), (hi * 0.8, hi * 3))):
        band = bandpass(rng.standard_normal(n), a, b, 2)
        env = smooth_noise(rng, n, gust * (1 + i * 0.6), 0.15, 1.0) ** 1.6
        out += band * env * (1.0, 0.7, 0.25)[i]
    if whistle:
        env = smooth_noise(rng, n, gust * 0.8, 0, 1) ** 3
        fw = 700 + 500 * smooth_noise(rng, n, gust * 1.3, 0, 1)
        out += np.sin(phase_of(fw)) * env * whistle * 0.3
    return out
