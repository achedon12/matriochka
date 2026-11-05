"""Seeded composer for the mod's music: folk phrases on Slavic modes, played by plucked strings, a music box,
a wooden flute, a bayan and a frame drum.

A theme is a small score built from a seed: a chord progression per phrase, a melody that walks the scale and
lands on chord tones, an oom-pah bass and a drone. Phrases are written in scale degrees, independent of the mode,
so the same phrase can be played in another mode or key: the lullaby of World 0 is the motif the boss, World 10
and the endings come back to.
"""
import numpy as np

import synth as S

MODES = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "harmonic": [0, 2, 3, 5, 7, 8, 11],
    "phrygian_dom": [0, 1, 4, 5, 7, 8, 10],
}

# folk rhythms in eighth notes, per bar length (2, 3 or 4 beats)
RHYTHMS = {
    4: [[2, 2, 2, 2], [2, 1, 1, 2, 2], [3, 1, 2, 2], [1, 1, 2, 1, 1, 2], [2, 2, 1, 1, 2], [3, 1, 3, 1]],
    3: [[2, 2, 2], [3, 1, 2], [2, 1, 1, 2], [1, 1, 2, 2], [4, 2]],
    2: [[1, 1, 2], [2, 2], [1, 1, 1, 1], [3, 1]],
}
CADENCE = {4: [[2, 2, 4], [4, 4], [6, 2]], 3: [[2, 4], [6], [4, 2]], 2: [[4], [2, 2]]}

INSTR = {
    "pluck": lambda f, d, v, rng: S.pluck(f, d, v, rng=rng),
    "pluck_soft": lambda f, d, v, rng: S.pluck(f, d, v * 0.9, bright=0.3, pos=0.3, rng=rng),
    "tremolo": lambda f, d, v, rng: S.tremolo_pluck(f, d, v, rng=rng) if d > 0.3 else S.pluck(f, d, v, rng=rng),
    "box": lambda f, d, v, rng: S.music_box(f, d, v, rng=rng),
    "box_rev": lambda f, d, v, rng: reverse_note(S.music_box(f, d, v, rng=rng), d),
    "flute": lambda f, d, v, rng: S.flute(f, d, v, rng=rng),
    "reed": lambda f, d, v, rng: S.reed(f, d, v, rng=rng),
    "bell": lambda f, d, v, rng: S.bell(f, max(2.5, d * 2), v * 1.4, rng=rng),
}


def reverse_note(x, d):
    """A music box note played backwards: it swells in instead of fading out (World 6)."""
    keep = min(len(x), S.secs(max(0.35, d * 1.4)))
    y = x[:keep][::-1].copy()
    y *= S.perc(len(y), 0.01, 1e9, 0.03)
    return y


class Theme:
    """One piece of music: everything is a field so a world can change only what makes it itself."""

    def __init__(self, seed, tonic=62, mode="aeolian", bpm=90, beats=4, prog=None, prog_b=None,
                 lead="box", lead_vel=0.9, counter=None, bass="pluck_soft", drone=True, pad=False,
                 drum=None, ticks=False, passes=2, swing=0.0, octave=12, reverb=(1.8, 0.22),
                 motif_seed=None, lowpass=None, transpose_pass=0, heartbeat=False, intro=1, rit=True):
        self.__dict__.update(locals())
        del self.__dict__["self"]
        self.prog = prog or [0, 6, 5, 4]
        self.prog_b = prog_b or [3, 0, 6, 4]


def chord(root):
    return [root, root + 2, root + 4]


def phrase(rng, prog, beats, end_on=0, start=4, lo=0, hi=11):
    """Four bars of melody in scale degrees: [(start eighth, length in eighths, degree)]."""
    notes = []
    d = start
    for bar, root in enumerate(prog):
        last = bar == len(prog) - 1
        choices = (CADENCE if last else RHYTHMS)[beats]
        pattern = choices[int(rng.integers(len(choices)))]
        pos = bar * beats * 2
        tones = chord(root)
        for i, ln in enumerate(pattern):
            strong = (pos - bar * beats * 2) in ((0, 4) if beats == 4 else (0,))
            if last and i == len(pattern) - 1:
                # cadence: the nearest tonic (or the requested degree) in range
                cands = [end_on + 7 * k for k in range(-1, 3) if lo <= end_on + 7 * k <= hi]
                d = min(cands, key=lambda c: abs(c - d))
            elif strong:
                cands = [t + 7 * k for t in tones for k in range(-1, 3) if lo <= t + 7 * k <= hi]
                step = int(rng.choice([-2, -1, 0, 1, 2], p=[0.15, 0.3, 0.1, 0.3, 0.15]))
                d = min(cands, key=lambda c: abs(c - (d + step)))
            else:
                step = int(rng.choice([-2, -1, 1, 2, 3, -3], p=[0.12, 0.36, 0.34, 0.1, 0.04, 0.04]))
                d = int(np.clip(d + step, lo, hi))
            notes.append((pos, ln, d))
            pos += ln
    return notes


def to_midi(tonic, mode, deg):
    sc = MODES[mode]
    return tonic + 12 * (deg // 7) + sc[deg % 7]


def compose(th):
    """Returns (melody phrases, chord per bar) for the whole form A A' B A', in scale degrees."""
    mrng = np.random.default_rng(th.motif_seed if th.motif_seed is not None else th.seed)
    rng = np.random.default_rng(th.seed + 1)
    a = phrase(mrng, th.prog, th.beats, end_on=4)
    # A': the same three bars, then an ending that comes home to the tonic
    tail_rng = np.random.default_rng(th.seed + 2)
    a2_last = [n for n in phrase(tail_rng, th.prog[:3] + [0], th.beats, end_on=0, start=a[-1][2]) if n[0] >= 3 * th.beats * 2]
    a2 = [n for n in a if n[0] < 3 * th.beats * 2] + a2_last
    b = phrase(rng, th.prog_b, th.beats, end_on=4, start=7, lo=3, hi=12)
    form = [(a, th.prog), (a2, th.prog[:3] + [0]), (b, th.prog_b), (a2, th.prog[:3] + [0])]
    return form


def render(th):
    """Renders a Theme to a mono buffer."""
    eighth = 60 / th.bpm / 2
    bar_len = th.beats * 2
    form = compose(th)
    prng = np.random.default_rng(th.seed + 3)
    parts = []
    t0 = 0.0
    # intro: the drone and one bar of bass alone
    intro_bars = th.intro
    for b in range(intro_bars):
        bt = t0 + b * bar_len * eighth
        if th.bass:
            for beat in range(th.beats):
                m = to_midi(th.tonic - 12, th.mode, 0) if beat == 0 else to_midi(th.tonic, th.mode, 2 if beat % 2 else 4)
                parts.append((bt + beat * 2 * eighth, INSTR[th.bass](S.mtof(m), 2 * eighth * 0.9, 0.7 if beat == 0 else 0.3, prng)))
        elif th.lead in ("bell", "box"):
            parts.append((bt, INSTR[th.lead](S.mtof(to_midi(th.tonic + th.octave, th.mode, 0)), bar_len * eighth, th.lead_vel * 0.6, prng)))
        if th.ticks:
            for e in range(bar_len):
                parts.append((bt + e * eighth, S.tick(prng, 0.35 if e % 2 == 0 else 0.2, 2600 if e % 2 == 0 else 2100)))
    for p in range(th.passes):
        tr = th.transpose_pass * p
        full = p > 0 or th.passes == 1
        for pi, (mel, prog) in enumerate(form):
            ph_start = t0 + (intro_bars + (p * len(form) + pi) * len(prog)) * bar_len * eighth
            for pos, ln, deg in mel:
                at = ph_start + pos * eighth
                if th.swing and pos % 2 == 1:
                    at += th.swing * eighth
                f = S.mtof(to_midi(th.tonic + th.octave + tr, th.mode, deg))
                v = th.lead_vel * (1.0 if pos % bar_len == 0 else 0.82) * prng.uniform(0.92, 1.05)
                parts.append((at, INSTR[th.lead](f, ln * eighth * 0.95, v, prng)))
            for b, root in enumerate(prog):
                bt = ph_start + b * bar_len * eighth
                root_m = to_midi(th.tonic - 12 + tr, th.mode, root)
                if th.bass:
                    # oom-pah: the root on the downbeat, the chord on the others (pah-pah in a waltz)
                    for beat in range(th.beats):
                        at = bt + beat * 2 * eighth
                        if beat == 0 or (th.beats == 4 and beat == 2):
                            m = root_m if beat == 0 else to_midi(th.tonic - 12 + tr, th.mode, root + 4)
                            parts.append((at, INSTR[th.bass](S.mtof(m), 2 * eighth * 0.9, 0.75, prng)))
                        elif full or th.passes == 1:
                            for deg in chord(root)[1:]:
                                m = to_midi(th.tonic + tr, th.mode, deg)
                                parts.append((at, INSTR[th.bass](S.mtof(m), eighth * 0.8, 0.28, prng)))
                if th.counter and full:
                    # a sparse arpeggio over the chord, an octave above the melody's range
                    for k, deg in enumerate(chord(root) + [root + 7]):
                        if prng.random() < 0.7:
                            m = to_midi(th.tonic + th.octave + 12 + tr, th.mode, deg)
                            at = bt + (k * bar_len // 4) * eighth + eighth
                            parts.append((at, INSTR[th.counter](S.mtof(m), eighth, 0.32, prng)))
                if th.pad and full:
                    for deg in chord(root):
                        m = to_midi(th.tonic + tr, th.mode, deg)
                        parts.append((bt, S.pad(S.mtof(m), bar_len * eighth, 0.5, prng, a=0.6, r=0.9)))
                if th.drum and full:
                    for beat in range(th.beats):
                        at = bt + beat * 2 * eighth
                        if th.drum == "dance":
                            parts.append((at, S.frame_drum(0.7 if beat == 0 else 0.35, prng, pitch=78 if beat == 0 else 110, dur=0.4)))
                        elif th.drum == "march" and beat % 2 == 0:
                            parts.append((at, S.frame_drum(0.75, prng, pitch=60, dur=0.6)))
                        elif th.drum == "drive":
                            parts.append((at, S.frame_drum(0.8 if beat % 2 == 0 else 0.45, prng, pitch=58 if beat % 2 == 0 else 95, dur=0.45)))
                            parts.append((at + eighth, S.wood_block(0.25, prng, pitch=1200)))
                if th.ticks:
                    for e in range(bar_len):
                        parts.append((bt + e * eighth, S.tick(prng, 0.35 if e % 2 == 0 else 0.2, 2600 if e % 2 == 0 else 2100)))
                if th.heartbeat and b % 2 == 0:
                    parts.append((bt, S.heartbeat(0.55, 46)))
    end_t = t0 + (intro_bars + th.passes * len(form) * len(form[0][1])) * bar_len * eighth
    # the last chord rings out
    final = S.mtof(to_midi(th.tonic + th.octave + th.transpose_pass * (th.passes - 1), th.mode, 0))
    parts.append((end_t, INSTR[th.lead](final, bar_len * eighth, th.lead_vel, prng)))
    if th.bass:
        parts.append((end_t, INSTR[th.bass](S.mtof(to_midi(th.tonic - 12 + th.transpose_pass * (th.passes - 1), th.mode, 0)), bar_len * eighth, 0.7, prng)))
    total = end_t + bar_len * eighth + 2.5
    if th.drone:
        # tonic and fifth held under everything, breathing slowly
        for deg in (0, 4):
            m = to_midi(th.tonic - 12, th.mode, deg)
            parts.append((0, S.pad(S.mtof(m), total - 1.5, 0.45 if deg == 0 else 0.3, prng, a=2.5, r=2.5, bright=0.15)))
    x = S.place(parts, total)
    if th.lowpass:
        x = S.lowpass(x, th.lowpass, 2)
    x = S.reverb(S.tail(x, 0.5), th.reverb[0], th.reverb[1], seed=th.seed % 97)
    x = S.clean(x)
    return S.fade(x, 0.05, 2.5)
