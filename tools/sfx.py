"""Recipes of the mod's sound effects, ambient loops and music (see tools/sound.py for the table).

Each recipe takes a seeded numpy Generator and returns a mono buffer. Nesting dolls are lacquered linden wood:
their sounds are wooden twists, hollow pops and clicks, with a music box note or a bell where something magical
happens. The worlds borrow their palettes from the design document (Direction artistique et immersion).
"""
import zlib

import numpy as np

import music as M
import synth as S
from sound import PIECES, WORLD_THEMES

# key (tonic, mode) of each world, shared by its telegraph and its station flourishes
KEY = {w: (th["tonic"], th["mode"]) for w, th in WORLD_THEMES.items()}


def notes(world, degrees, octave=12):
    tonic, mode = KEY[world]
    return [S.mtof(M.to_midi(tonic + octave, mode, d)) for d in degrees]


# ------------------------------------------------------------------ nesting dolls
def doll_twist(rng, dur=0.28, up=True):
    """Two lacquered halves turning against each other: a dry wooden friction that rises (opening)."""
    n = S.secs(dur)
    base = S.crackle(rng, dur, density=420, lo=900, hi=5000)
    sweep = np.linspace(0.6, 1.0, n) if up else np.linspace(1.0, 0.6, n)
    body = S.resonance(base, 1400 * (1.1 if up else 0.9), q=4, gain=3)
    return body * S.adsr(n, 0.03, 0.05, 0.8, 0.06) * sweep


def hollow_pop(rng, pitch=330, vel=1.0):
    """The suction pop of a doll lifted open: a short tone rising in pitch inside a hollow body."""
    n = S.secs(0.22)
    t = np.arange(n) / S.SR
    f = pitch * (0.7 + 0.5 * (1 - np.exp(-t / 0.015)))
    tone = np.sin(S.phase_of(f)) * np.exp(-t / 0.05)
    tone += 0.35 * np.sin(S.phase_of(f * 2.02)) * np.exp(-t / 0.03)
    air = S.bandpass(rng.standard_normal(n), 400, 2500) * np.exp(-t / 0.012) * 0.4
    return (tone + air) * S.perc(n, 0.001, 1e9, 0.02) * vel


def wood_clack(rng, vel=1.0, pitch=None):
    """Two lacquered rims meeting."""
    p = pitch or rng.uniform(780, 980)
    return S.add(S.click(rng, vel, tone=3200, body=p, length=0.09), S.wood_block(vel * 0.4, rng, pitch=p * 1.6))


def doll_open(rng):
    x = S.place([(0, doll_twist(rng, 0.26, True) * 0.5), (0.25, hollow_pop(rng, rng.uniform(300, 360)))])
    return S.reverb(S.tail(x, 0.2), 0.5, 0.18)


def doll_close(rng):
    x = S.place([(0, doll_twist(rng, 0.22, False) * 0.5), (0.21, wood_clack(rng, 1.0)), (0.24, S.thump(0.4, 160, 0.15))])
    return S.reverb(S.tail(x, 0.2), 0.5, 0.18)


def doll_click(rng):
    return S.reverb(S.tail(wood_clack(rng, 1.0, rng.uniform(900, 1200)), 0.15), 0.4, 0.15)


def doll_rattle(rng):
    parts = [(i * 0.055 + rng.uniform(0, 0.012), wood_clack(rng, rng.uniform(0.4, 0.8), rng.uniform(1100, 1500))) for i in range(6)]
    return S.reverb(S.tail(S.place(parts), 0.2), 0.4, 0.15)


def wood_crack(rng, dur=0.5, vel=1.0):
    """Lacquer and wood splitting: a sharp snap, then a run of fibre crackles."""
    n = S.secs(dur)
    t = np.arange(n) / S.SR
    snap = S.bandpass(rng.standard_normal(n), 600, 6000) * np.exp(-t / 0.012)
    fib = S.crackle(rng, dur, density=160, lo=1200, hi=7000) * np.exp(-t / (dur * 0.35)) * 0.8
    body = S.thump(0.6, 120, dur)
    return (snap + fib + body[:n]) * S.perc(n, 0.0005, 1e9, 0.03) * vel


def doll_of_life(rng):
    """The Doll of Life gives itself up: its shell cracks and a bright bell blooms (life given back)."""
    shim = sum(S.music_box(f, vel=0.5, rng=rng) for f in notes(0, [7, 9, 11, 14], 12)[:1])
    arp = [(0.12 + i * 0.07, S.music_box(f, vel=0.55, rng=rng)) for i, f in enumerate(notes(0, [4, 7, 9, 11, 14]))]
    x = S.place([(0, wood_crack(rng, 0.45, 1.0)), (0.1, S.bell(S.mtof(81), 2.5, 0.8)), (0.1, shim)] + arp)
    return S.reverb(S.tail(x, 0.6), 2.2, 0.3, bright=0.7)


# ------------------------------------------------------------------ World Blocks
def world_enter(rng):
    """Opening a World Block and shrinking into it: the doll opens, a whoosh falls in pitch and a music box runs
    down two octaves of the lullaby's scale."""
    n = S.secs(1.6)
    t = np.arange(n) / S.SR
    hiss = S.noise(rng, 1.6)
    # a falling band of air
    whoosh = np.zeros(n)
    for i, (a, b) in enumerate(((3000, 6000), (1500, 3000), (700, 1500), (300, 700))):
        env = np.exp(-((t - 0.2 - i * 0.3) / 0.22) ** 2)
        whoosh += S.bandpass(hiss, a, b) * env
    run = [(0.15 + i * 0.075, S.music_box(f, vel=0.5 - i * 0.025, rng=rng)) for i, f in enumerate(notes(0, [14, 13, 11, 9, 7, 6, 4, 2, 0, -3], 12))]
    x = S.place([(0, doll_open(rng)), (0.1, whoosh * 0.25)] + run)
    return S.reverb(S.tail(x, 0.8), 2.4, 0.3)


def world_form(rng):
    """A Seed becomes a World Block: a rising arpeggio and a wooden knock as the doll closes around it."""
    run = [(i * 0.09, S.music_box(f, vel=0.4 + i * 0.03, rng=rng)) for i, f in enumerate(notes(0, [0, 2, 4, 7, 9, 11, 14]))]
    x = S.place(run + [(0.7, doll_close(rng)), (0.72, S.bell(S.mtof(69), 2.0, 0.5))])
    return S.reverb(S.tail(x, 0.6), 2.0, 0.28)


def world_crack(rng):
    x = S.place([(0, wood_crack(rng, 0.6, 1.0)), (0.05, S.thump(0.7, 70, 0.6)), (0.15, wood_crack(rng, 0.3, 0.5))])
    return S.reverb(S.tail(x, 0.4), 1.2, 0.2)


def seed_pulse(rng):
    """A Seed growing hums once every half second (the game raises the pitch as it grows)."""
    f = notes(0, [0])[0]
    x = S.add(S.music_box(f, vel=0.6, rng=rng), 0.3 * S.pad(f / 2, 0.4, 0.6, rng, a=0.05, r=0.3))
    return S.reverb(S.tail(x, 0.3), 1.6, 0.3)


# ------------------------------------------------------------------ stations
def station_matrix_workbench(rng):
    knocks = [(i * 0.11, wood_clack(rng, 0.7 + 0.1 * i)) for i in range(3)]
    run = [(0.36 + i * 0.06, S.music_box(f, vel=0.45, rng=rng)) for i, f in enumerate(notes(0, [0, 4, 7, 11]))]
    return S.reverb(S.tail(S.place(knocks + run), 0.4), 1.4, 0.22)


def anvil(rng, f=1200, vel=1.0):
    n = S.secs(0.9)
    t = np.arange(n) / S.SR
    ring = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.3), (2.76, 0.5, 0.15), (5.4, 0.3, 0.08), (8.9, 0.15, 0.04)))
    hit = S.highpass(rng.standard_normal(n), 2500) * np.exp(-t / 0.004) * 0.6
    return (ring + hit) * S.perc(n, 0.0005, 1e9, 0.05) * vel * 0.35


def whetstone(rng, dur=0.35):
    n = S.secs(dur)
    x = S.colored(rng, dur, 2500, 9000) * S.adsr(n, 0.05, 0.05, 0.7, 0.1)
    return x * 0.25


def station_class_table(rng):
    x = S.place([(0, whetstone(rng)), (0.3, whetstone(rng, 0.25)), (0.6, anvil(rng, 1500, 0.8)),
                 (0.62, S.music_box(notes(0, [4])[0], vel=0.4, rng=rng)), (0.74, S.music_box(notes(0, [7])[0], vel=0.45, rng=rng))])
    return S.reverb(S.tail(x, 0.4), 1.2, 0.2)


def station_soul_altar(rng):
    """Purify: a pure chord swells and a bell answers."""
    chordf = notes(0, [0, 2, 4, 7], 0)
    sw = sum(S.pad(f, 0.9, 0.5, rng, a=0.35, r=0.6, bright=0.4) for f in chordf)
    x = S.place([(0, sw), (0.4, S.bell(S.mtof(81), 2.2, 0.6))])
    return S.reverb(S.tail(x, 0.6), 2.6, 0.35, bright=0.7)


def station_devour(rng):
    """Devour: a low growl, a reversed swell sucked into the altar."""
    n = S.secs(1.2)
    t = np.arange(n) / S.SR
    f = 55 * (1 + 0.08 * np.sin(2 * np.pi * 7 * t))
    ph = S.phase_of(f)
    growl = S.lowpass(np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sign(np.sin(3 * ph)) * 0.3, 800) * S.adsr(n, 0.15, 0.2, 0.8, 0.4)
    swell = S.colored(rng, 1.2, 300, 3000) * np.linspace(0, 1, n) ** 3 * 0.4
    swell[-S.secs(0.04):] *= S.ramp(S.secs(0.04), 1)[::-1]
    x = growl * 0.6 + swell + 0.5 * M.reverse_note(S.bell(S.mtof(45), 2.0, 0.8), 1.0)[:n]
    return S.reverb(S.tail(x, 0.5), 1.8, 0.25)


def bubbles(rng, dur, rate=18, lo=300, hi=900):
    parts = []
    for at in np.sort(rng.uniform(0, dur, int(rate * dur))):
        parts.append((at, S.drip(rng, rng.uniform(0.2, 0.6), rng.uniform(lo, hi))))
    return S.place(parts, dur + 0.3)


def station_spore_vat(rng):
    x = S.place([(0, bubbles(rng, 0.9)), (0.9, hollow_pop(rng, 260, 0.8))])
    return S.reverb(S.tail(x, 0.3), 1.0, 0.25)


def station_ash_foundry(rng):
    """A roar of the furnace and molten metal hissing into the mould."""
    n = S.secs(1.3)
    t = np.arange(n) / S.SR
    roar = S.brown(rng, 1.3, 500) * S.adsr(n, 0.2, 0.2, 0.7, 0.4) * 1.5
    hiss = S.colored(rng, 1.3, 3000, 11000) * np.exp(-np.maximum(t - 0.5, 0) / 0.3) * (t > 0.5) * 0.35
    crk = S.crackle(rng, 1.3, density=60) * 0.5
    x = roar + hiss + crk
    return S.reverb(S.tail(S.fade(x, 0.01, 0.1), 0.3), 1.0, 0.18)


def station_jailer_table(rng):
    """The lock gives: three tumblers and the bolt sliding back."""
    parts = [(i * 0.13, S.click(rng, 0.8, tone=4000, body=1800 + 300 * i, length=0.07)) for i in range(3)]
    bolt = S.colored(rng, 0.25, 800, 3000) * S.adsr(S.secs(0.25), 0.02, 0.05, 0.7, 0.05) * 0.4
    parts += [(0.42, bolt), (0.66, S.click(rng, 1.0, tone=2500, body=600, length=0.12)), (0.66, S.thump(0.5, 140, 0.2))]
    return S.reverb(S.tail(S.place(parts), 0.4), 1.0, 0.2)


def jailer_pin(rng):
    return S.reverb(S.tail(S.click(rng, 1.0, tone=4500, body=rng.uniform(2000, 2400), length=0.08), 0.2), 0.6, 0.2)


def zap(rng, dur=0.35):
    n = S.secs(dur)
    t = np.arange(n) / S.SR
    f = 2400 * np.exp(-t / 0.08) + 120
    mod = np.sin(S.phase_of(f * 0.5)) * 3
    x = np.sin(S.phase_of(f) + mod) * np.exp(-t / 0.1)
    return x * S.perc(n, 0.0005, 1e9, 0.02) * 0.5


def station_lightning_forge(rng):
    x = S.place([(0, S.crackle(rng, 0.5, density=300, lo=2000, hi=10000) * 1.2), (0.3, zap(rng)), (0.45, anvil(rng, 1100, 1.0)),
                 (0.47, S.thump(0.6, 90, 0.3))])
    return S.reverb(S.tail(x, 0.5), 1.4, 0.22)


def station_dark_altar(rng):
    n = S.secs(1.5)
    t = np.arange(n) / S.SR
    hum = S.lowpass(sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((49, 73.5, 98.6))), 400) * S.adsr(n, 0.5, 0.2, 0.8, 0.6) * 0.35
    whisper = S.colored(rng, 1.5, 1500, 6000) * S.smooth_noise(rng, n, 9, 0, 1) ** 2 * S.adsr(n, 0.3, 0.1, 0.8, 0.5) * 0.4
    x = hum + whisper
    x = S.mix_into(x, S.bell(S.mtof(48), 2.5, 0.5), S.secs(0.5))
    return S.reverb(S.tail(x, 0.6), 3.0, 0.4, bright=0.2)


def station_inverter(rng):
    """Two tones trade places: one glides up while the other glides down, through each other."""
    n = S.secs(1.0)
    t = np.arange(n) / S.SR
    k = 0.5 - 0.5 * np.cos(np.pi * np.clip(t / 0.9, 0, 1))
    a = 440 * (880 / 440) ** k
    b = 880 * (440 / 880) ** k
    x = (np.sin(S.phase_of(a)) + np.sin(S.phase_of(b))) * S.adsr(n, 0.05, 0.1, 0.8, 0.25) * 0.3
    x += S.colored(rng, 1.0, 2000, 8000) * np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 4 * 0.12
    return S.reverb(S.tail(x, 0.5), 2.0, 0.35)


def station_abyssal_press(rng):
    n = S.secs(1.2)
    t = np.arange(n) / S.SR
    hiss = S.colored(rng, 1.2, 1500, 7000) * np.exp(-t / 0.4) * S.adsr(n, 0.01, 0.05, 1, 0.1) * 0.35
    x = S.place([(0, hiss), (0.35, S.thump(1.0, 48, 0.8)), (0.35, S.click(rng, 0.6, 1800, 300, 0.2)), (0.5, bubbles(rng, 0.6, 14, 200, 600) * 0.7)])
    return S.reverb(S.tail(S.lowpass(x, 5000), 0.4), 1.5, 0.25)


def station_time_workshop(rng):
    gaps = [0.2, 0.16, 0.125, 0.1, 0.08, 0.065, 0.055]
    parts, at = [], 0.0
    for i, g in enumerate(gaps):
        parts.append((at, S.tick(rng, 0.7, 2600 if i % 2 == 0 else 2100)))
        at += g
    parts.append((at + 0.05, S.bell(S.mtof(88), 1.8, 0.5)))
    return S.reverb(S.tail(S.place(parts), 0.5), 1.4, 0.22)


def station_terrain_anchor(rng):
    n = S.secs(1.4)
    t = np.arange(n) / S.SR
    hum = (np.sin(2 * np.pi * 65.4 * t) + 0.5 * np.sin(2 * np.pi * 98 * t)) * np.exp(-t / 0.6) * S.adsr(n, 0.05, 0.1, 1, 0.3) * 0.3
    x = S.place([(0, S.thump(1.0, 42, 0.8)), (0, rock(rng, 0.4) * 0.6), (0.05, hum)])
    return S.reverb(S.tail(x, 0.5), 1.6, 0.25)


def station_final_loom(rng):
    """The shuttle crosses the warp: wooden clacks, then a gusli run up the whole lullaby scale."""
    parts = [(0, wood_clack(rng, 0.8, 700)), (0.18, wood_clack(rng, 0.8, 760)), (0.36, wood_clack(rng, 0.9, 700))]
    parts += [(0.5 + i * 0.05, S.pluck(f, 0.4, 0.6, rng=rng)) for i, f in enumerate(notes(10, [0, 2, 4, 5, 7, 9, 11, 14]))]
    return S.reverb(S.tail(S.place(parts), 0.6), 1.8, 0.28)


# ------------------------------------------------------------------ bosses
def boss_awaken(rng):
    """A boss stirs: a low drone swells, a bell tolls and its doll shell creaks open."""
    n = S.secs(2.6)
    drone = sum(S.pad(f, 2.0, 0.7, rng, a=1.2, r=0.6, bright=0.2) for f in (55, 82.4, 110))[:n]
    x = S.place([(0, drone), (1.3, S.bell(S.mtof(45), 3.5, 1.0)), (1.25, wood_crack(rng, 0.6, 0.7)), (1.3, S.thump(0.9, 45, 0.8))])
    return S.reverb(S.tail(x, 0.8), 3.0, 0.3)


def boss_phase(rng):
    """The outer shell breaks and a smaller, angrier doll steps out: a crack, a boom and a falling minor figure."""
    fig = [(0.25 + i * 0.09, S.bell(f, 1.8, 0.6)) for i, f in enumerate(notes(3, [7, 5, 4, 2, 0], 0))]
    x = S.place([(0, wood_crack(rng, 0.7, 1.0)), (0.02, S.thump(1.0, 40, 1.0)), (0.05, S.brown(rng, 0.8, 200) * S.perc(S.secs(0.8), 0.005, 0.25, 0.1) * 0.6)] + fig)
    return S.reverb(S.tail(x, 0.8), 2.5, 0.3)


def boss_defeat(rng):
    """Victory: a music box and a gusli play the lullaby's cadence in major, under a bell."""
    run = [(i * 0.12, S.music_box(f, vel=0.6, rng=rng)) for i, f in enumerate(notes(0, [0, 2, 4, 7, 4, 7, 9, 14]))]
    chord = [(1.0, S.pluck(f, 1.5, 0.6, rng=rng)) for f in notes(0, [0, 2, 4, 7], 0)]
    x = S.place(run + chord + [(1.0, S.bell(S.mtof(69), 3.5, 0.9)), (1.0, S.frame_drum(0.6, rng, 70, 0.6))])
    return S.reverb(S.tail(x, 1.0), 2.6, 0.3, bright=0.7)


TEXTURE = {  # what each world adds to its boss warning
    0: lambda rng: S.place([(i * 0.18, wood_clack(rng, 0.9, 700)) for i in range(3)]),
    1: lambda rng: S.colored(rng, 0.8, 2000, 8000) * np.linspace(0, 1, S.secs(0.8)) ** 2 * 0.4,
    2: lambda rng: S.place([(0.0, anvil(rng, 900, 0.8)), (0.35, anvil(rng, 900, 0.9))]),
    3: lambda rng: chains(rng),
    4: lambda rng: S.wind(rng, 0.8, 400, 2400, 2.5) * np.linspace(0.2, 1, S.secs(0.8)) * 0.6,
    5: lambda rng: breath(rng, 1.0, inhale=True),
    6: lambda rng: M.reverse_note(S.music_box(S.mtof(89), vel=0.8, rng=rng), 0.8),
    7: lambda rng: S.place([(0, S.drip(rng, 0.8, 500)), (0.2, S.drip(rng, 0.6, 400))]),
    8: lambda rng: S.place([(i * 0.07, S.tick(rng, 0.6, 2400)) for i in range(10)]),
    9: lambda rng: S.place([(0, S.heartbeat(0.9, 44)), (0.1, rock(rng, 0.6) * 0.6)]),
    10: lambda rng: S.place([(0, S.bell(S.mtof(57), 1.5, 0.5)), (0, S.bell(S.mtof(58), 1.5, 0.4))]),
}


def telegraph(rng, world):
    """A boss is about to strike: its world's lead instrument climbs a tense figure over the world's texture."""
    w = world
    lead = WORLD_THEMES[w]["lead"]
    if lead in ("flute", "box_rev"):
        lead = "box"
    figure = notes(w, [0, 1, 4, 5] if w % 2 else [0, 2, 3, 7], 0)
    parts = [(i * 0.1, M.INSTR[lead](f, 0.12, 0.7, rng)) for i, f in enumerate(figure)]
    parts += [(0.0, TEXTURE[w](rng) * 0.8), (0.4, S.thump(0.6, 50, 0.4))]
    return S.reverb(S.tail(S.place(parts), 0.4), 1.2, 0.2)


# ------------------------------------------------------------------ world rules
def gust(rng):
    n = S.secs(1.6)
    x = S.wind(rng, 1.6, 300, 2500, 1.6, whistle=0.6) * S.adsr(n, 0.25, 0.3, 0.8, 0.7)
    return S.fade(x, 0.01, 0.05)


def gravity_shift(rng):
    """Gravity wavers: a pad bends up and down and a music box plays backwards into it."""
    n = S.secs(2.0)
    t = np.arange(n) / S.SR
    f = 220 * 2 ** (0.5 * np.sin(2 * np.pi * 0.7 * t) * t / 2)
    ph = S.phase_of(f)
    pad = (np.sin(ph) + 0.4 * np.sin(1.5 * ph) + 0.2 * np.sin(2 * ph)) * S.adsr(n, 0.6, 0.2, 0.8, 0.6) * 0.3
    x = pad + 0.6 * np.concatenate([M.reverse_note(S.music_box(S.mtof(84), vel=0.8, rng=rng), 1.2), S.silence(2.0)])[:n]
    return S.reverb(S.tail(x, 0.6), 2.5, 0.35)


def rock(rng, dur=0.6):
    """Stone grinding on stone."""
    n = S.secs(dur)
    x = S.colored(rng, dur, 150, 1800) * (0.5 + 0.5 * S.smooth_noise(rng, n, 25, 0, 1)) + S.crackle(rng, dur, 80, 400, 3000) * 0.6
    return x * S.adsr(n, 0.05, 0.1, 0.8, dur * 0.3)


def quake(rng):
    n = S.secs(3.0)
    sub = S.brown(rng, 3.0, 90) * 4 * S.adsr(n, 0.4, 0.4, 0.8, 1.2)
    x = S.mix_into(sub + rock(rng, 3.0) * 0.4, S.thump(0.9, 38, 1.0), S.secs(0.3))
    return S.fade(S.reverb(S.tail(x, 0.6), 2.0, 0.2), 0.01, 0.3)


def rumble(rng):
    n = S.secs(1.2)
    return S.fade(S.brown(rng, 1.2, 120) * 3 * S.adsr(n, 0.2, 0.2, 0.8, 0.5) + rock(rng, 1.2) * 0.3, 0.01, 0.1)


# ------------------------------------------------------------------ ambience one-shots
def creak(rng):
    """Painted wood settling: a slow stick-slip creak."""
    dur = rng.uniform(0.6, 1.1)
    n = S.secs(dur)
    rate = 40 + 30 * S.smooth_noise(rng, n, 4, 0, 1)
    ph = S.phase_of(rate)
    pulses = np.maximum(0, np.sin(ph)) ** 12
    x = S.bandpass(pulses * (1 + 0.3 * rng.standard_normal(n)), 300, 2500)
    x = S.resonance(x, rng.uniform(500, 800), 6, 3)
    return S.reverb(S.tail(x * S.adsr(n, 0.1, 0.1, 0.8, 0.2) * 0.5, 0.4), 1.2, 0.25)


def insects(rng):
    dur = 2.4
    n = S.secs(dur)
    t = np.arange(n) / S.SR
    f = rng.uniform(3800, 5200)
    trem = (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(22, 36) * t)) ** 2
    x = np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 60 * t)) * trem * S.adsr(n, 0.4, 0.2, 0.7, 0.8) * 0.12
    x += S.colored(rng, dur, 150, 600) * S.smooth_noise(rng, n, 3, 0.3, 1) * 0.08 * S.adsr(n, 0.5, 0.2, 0.7, 0.8)
    return S.reverb(S.tail(x, 0.4), 1.6, 0.3)


def spore_puff(rng):
    parts = [(i * rng.uniform(0.08, 0.15), S.add(hollow_pop(rng, rng.uniform(140, 220), 0.4), S.colored(rng, 0.2, 800, 4000) * S.perc(S.secs(0.2), 0.005, 0.05, 0.02) * 0.4)) for i in range(3)]
    return S.reverb(S.tail(S.place(parts), 0.4), 1.4, 0.3)


def hammers(rng):
    parts = [(i * rng.uniform(0.45, 0.6), anvil(rng, rng.uniform(700, 900), 0.6)) for i in range(3)]
    x = S.lowpass(S.place(parts), 3000)
    return S.reverb(S.tail(x, 1.0), 2.8, 0.55)


def embers(rng):
    return S.fade(S.crackle(rng, 1.2, density=35, lo=1200, hi=6000) * 1.2, 0.02, 0.1)


def chains(rng):
    parts = []
    for i in range(int(rng.integers(5, 9))):
        parts.append((i * rng.uniform(0.04, 0.09), S.click(rng, rng.uniform(0.4, 0.9), tone=5000, body=rng.uniform(2800, 3800), length=0.08)))
    return S.reverb(S.tail(S.place(parts), 0.5), 1.8, 0.35)


def far_door(rng):
    x = S.place([(0, S.thump(1.0, 70, 0.6)), (0, S.click(rng, 0.8, 1500, 300, 0.2))])
    return S.reverb(S.tail(S.lowpass(x, 1500), 2.0), 3.5, 0.65, bright=0.2)


def whistle(rng):
    n = S.secs(2.5)
    t = np.arange(n) / S.SR
    f = rng.uniform(600, 900) * (1 + 0.15 * S.smooth_noise(rng, n, 1.5, -1, 1))
    x = np.sin(S.phase_of(f)) * S.adsr(n, 0.8, 0.2, 0.7, 1.0) * 0.15 + S.wind(rng, 2.5, 400, 2000, 1.2) * S.adsr(n, 0.6, 0.2, 0.7, 1.0) * 0.4
    return x


def far_thunder(rng):
    n = S.secs(4.0)
    t = np.arange(n) / S.SR
    env = np.exp(-t / 1.2) * (1 - np.exp(-t / 0.08))
    rumbles = S.brown(rng, 4.0, 160) * env * 4 * (0.6 + 0.4 * S.smooth_noise(rng, n, 6, 0, 1))
    return S.fade(rumbles, 0.02, 0.5)


def breath(rng, dur=None, inhale=None):
    dur = dur or rng.uniform(1.4, 2.0)
    n = S.secs(dur)
    up = inhale if inhale is not None else rng.random() < 0.5
    x = S.colored(rng, dur, 300, 2200) * S.adsr(n, dur * (0.6 if up else 0.15), 0.1, 0.7, dur * (0.2 if up else 0.6)) * 0.4
    return S.resonance(x, 700, 3, 2)


def steps(rng):
    parts = []
    for i in range(int(rng.integers(2, 4))):
        n = S.secs(0.15)
        t = np.arange(n) / S.SR
        st = S.colored(rng, 0.15, 150, 1500) * np.exp(-t / 0.03) + S.thump(0.4, 90, 0.15)[:n]
        parts.append((i * rng.uniform(0.45, 0.55), st * 0.5))
    return S.reverb(S.tail(S.place(parts), 0.5), 0.9, 0.25)


def reverse_chime(rng):
    fs = notes(6, [int(d) for d in rng.choice([0, 2, 4, 6, 7, 9], 2, replace=False)], 12)
    x = S.place([(0, M.reverse_note(S.music_box(fs[0], vel=0.6, rng=rng), 1.0)), (0.5, M.reverse_note(S.music_box(fs[1], vel=0.5, rng=rng), 1.0))])
    return S.reverb(S.tail(x, 0.6), 2.8, 0.4)


def drips(rng):
    parts = [(i * rng.uniform(0.3, 0.7), S.drip(rng, rng.uniform(0.5, 1.0))) for i in range(int(rng.integers(1, 4)))]
    return S.reverb(S.tail(S.place(parts), 0.6), 2.2, 0.45, bright=0.6)


def pressure_groan(rng):
    dur = rng.uniform(2.2, 3.2)
    x = S.groan(rng, dur, rng.uniform(40, 60), 1.0)
    return S.reverb(S.tail(S.lowpass(x, 1200), 0.8), 3.0, 0.45, bright=0.2)


def clock_chime(rng):
    k = int(rng.integers(2, 4))
    parts = [(i * 0.9, S.bell(S.mtof(76 - 5 * (i % 2)), 2.2, 0.6)) for i in range(k)]
    return S.reverb(S.tail(S.place(parts), 0.5), 2.0, 0.3)


def cuckoo(rng):
    def coo(f):
        return S.flute(f, 0.22, 0.8, rng=rng, vib=0, breath=0.02)
    x = S.place([(0, coo(S.mtof(79))), (0.28, coo(S.mtof(75))), (0.8, coo(S.mtof(79))), (1.08, coo(S.mtof(75)))])
    x = S.place([(0, S.tick(rng, 0.4, 1800)), (0.05, x)])
    return S.reverb(S.tail(x, 0.4), 1.2, 0.22)


def ground_beat(rng):
    x = S.place([(0, S.heartbeat(1.0, 42)), (0.9, S.heartbeat(0.8, 42))])
    return S.reverb(S.tail(S.lowpass(x, 400), 0.5), 1.5, 0.2)


def rock_grind(rng):
    return S.reverb(S.tail(rock(rng, rng.uniform(0.8, 1.4)) * 0.8, 0.4), 1.6, 0.25)


# ------------------------------------------------------------------ ambient loops
LOOP = 24.0  # seconds; long enough not to be noticed
XF = 2.0


def loop(rng, world):
    d = LOOP + XF
    n = S.secs(d)
    t = np.arange(n) / S.SR
    if world == 1:
        # the jungle breathes: a slow swell of leaves and air, insects pulsing on top
        air = S.colored(rng, d, 200, 1800) * (0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 6.0 + 1))) * 0.3
        ins = sum(np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * np.sin(2 * np.pi * r * t)) ** 3 * S.smooth_noise(rng, n, 0.3, 0, 1) ** 2
                  for f, r in ((4300, 24), (5100, 31), (3700, 18))) * 0.025
        x = air + ins
    elif world == 2:
        heat = S.brown(rng, d, 160) * 2.2 * (0.7 + 0.3 * S.smooth_noise(rng, n, 0.4, 0, 1))
        x = heat + S.crackle(rng, d, density=12, lo=1500, hi=6000) * 0.5
    elif world == 3:
        drone = S.lowpass(sum(np.sin(2 * np.pi * f * t + i) * (0.6 + 0.4 * np.sin(2 * np.pi * t / p)) for i, (f, p) in enumerate(((55, 8), (82.5, 12), (110.3, 6)))), 400) * 0.12
        draft = S.colored(rng, d, 250, 900) * S.smooth_noise(rng, n, 0.25, 0.2, 1) * 0.25
        x = S.reverb(drone + draft, 3.0, 0.4)[:n]
    elif world == 4:
        x = S.wind(rng, d, 200, 1800, 0.35, whistle=0.25) * 0.55
    elif world == 5:
        x = S.colored(rng, d, 60, 300) * 0.25 * (0.6 + 0.4 * S.smooth_noise(rng, n, 0.2, 0, 1))
    elif world == 6:
        wob = 1 + 0.02 * np.sin(2 * np.pi * t / 4.0) + 0.01 * np.sin(2 * np.pi * t / 1.7)
        ph = S.phase_of(174.6 * wob)
        x = (np.sin(ph) + 0.4 * np.sin(1.5 * ph) + 0.25 * np.sin(2.01 * ph)) * 0.08 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 8.0))
        x += S.colored(rng, d, 800, 4000) * S.smooth_noise(rng, n, 0.3, 0, 1) ** 3 * 0.08
        x = S.reverb(x, 2.5, 0.4)[:n]
    elif world == 7:
        deep = S.brown(rng, d, 110) * 2.5 * (0.6 + 0.4 * S.smooth_noise(rng, n, 0.2, 0, 1))
        water = S.colored(rng, d, 200, 700) * 0.12
        x = S.lowpass(deep + water, 900)
    elif world == 8:
        # three clocks at their own pace: their ticks line up every 24 seconds, so the loop is exact
        x = np.zeros(n)
        for period, pitch, vel in ((1.0, 2600, 0.5), (0.75, 2100, 0.35), (1.2, 3100, 0.3)):
            k = 0
            while k * period < d - 0.1:
                x = S.mix_into(x, S.tick(rng, vel * (1 if k % 2 == 0 else 0.8), pitch if k % 2 == 0 else pitch * 0.85), S.secs(k * period + 0.013 * vel))
                k += 1
        x = S.reverb(x[:n], 1.4, 0.3)[:n]
        x += S.colored(rng, d, 100, 400) * 0.04
    elif world == 9:
        x = S.brown(rng, d, 80) * 3 * (0.7 + 0.3 * S.smooth_noise(rng, n, 0.3, 0, 1))
        k = 0
        while k * 2.0 < d - 0.6:
            x = S.mix_into(x, S.lowpass(S.heartbeat(0.35, 40), 300), S.secs(k * 2.0))
            k += 1
    else:  # world 10: the earlier worlds at once, far away
        x = S.wind(rng, d, 200, 1500, 0.3) * 0.3 + S.brown(rng, d, 100) * 1.0
        for k in range(int(d / 1.0)):
            x = S.mix_into(x, S.tick(rng, 0.12, 2400), S.secs(k * 1.0))
        x = S.reverb(x, 2.5, 0.35)[:n]
    x = x[:n]
    x = S.loopify(S.clean(x), XF)
    # loops are set by loudness, not by peak: a soft bed under the game
    return x * min(0.06 / max(np.sqrt(np.mean(x ** 2)), 1e-9), 0.5 / np.max(np.abs(x)))


# ------------------------------------------------------------------ entry point
RECIPES = {name: fn for name, fn in globals().items() if callable(fn)}
PEAK = {"sfx": 0.89, "music": 0.8}
QUALITY = {"sfx": 3, "loop": 1, "music": 2}


def render(entry, variant):
    """Renders one file of a sound. Returns (buffer, vorbis quality)."""
    seed = zlib.crc32(f"{entry['id']}#{variant}".encode())
    rng = np.random.default_rng(seed)
    kind = entry["kind"]
    if kind == "music":
        spec = WORLD_THEMES[entry["args"]["world"]] if "world" in entry["args"] else PIECES[entry["args"]["piece"]]
        x = M.render(M.Theme(**spec))
    elif entry["recipe"] == "loop":
        x = loop(rng, entry["args"]["world"])
    else:
        x = RECIPES[entry["recipe"]](rng, **entry["args"])
        x = S.trim(S.fade(S.clean(x), 0.002, 0))
    if kind != "loop":
        x = S.normalize(x, PEAK[kind])
    return x, QUALITY[kind]
