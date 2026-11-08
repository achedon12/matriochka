"""Recipes of the wonders' sounds: the sealed reliquary, the relics it gives and the hum of the wonder around it
(see tools/sound.py, block/Reliquary.java and world/Relics.java).

Kept apart from sfx.py for the same reason as cues.py: the lock file hashes sfx.py, music.py and synth.py into every
sound, so adding recipes there would render the whole library again. These recipes are hashed with this file on top.

Each recipe takes a seeded numpy Generator and returns a mono buffer. The reliquary is lacquered wood like the dolls,
so it knocks and clicks; what it holds answers with bells and a music box in the lullaby's key.
"""
import zlib

import numpy as np

import music as M
import synth as S
from sfx import doll_twist, hollow_pop, wood_clack

# the lullaby key of World 0 (A ionian), like the stings: the relics belong to the whole nest of worlds
TONIC, MODE = 69, "ionian"


def _notes(degrees, octave=0):
    return [S.mtof(M.to_midi(TONIC + octave, MODE, d)) for d in degrees]


def reliquary_open(rng):
    """The right cross key: the wooden latch lifts with two clicks and a turn, the lid sighs open, then a soft bell
    chord rises with a music box shimmer above it."""
    latch = [(0.0, wood_clack(rng, 0.9, 640)), (0.09, wood_clack(rng, 0.6, 920)),
             (0.14, doll_twist(rng, 0.3, True) * 0.45), (0.44, hollow_pop(rng, 260, 0.6))]
    bells = [(0.6 + i * 0.13, S.bell(f, 3.2, 0.42 - i * 0.03)) for i, f in enumerate(_notes([0, 2, 4, 7]))]
    shim = [(1.05 + i * 0.08, S.music_box(f, vel=0.32, rng=rng)) for i, f in enumerate(_notes([7, 9, 11, 14], 12))]
    bed = [(0.55, S.pad(_notes([0], -12)[0], 2.2, 0.35, rng, a=0.7, r=1.2, bright=0.2))]
    x = S.place(latch + bells + shim + bed)
    return S.reverb(S.tail(x, 0.8), 2.4, 0.3, bright=0.7)


def reliquary_locked(rng):
    """The wrong key: a dull wooden knock that does not give, the latch rattling once, and a low bell muffled by the
    lid."""
    knock = S.add(S.wood_block(0.9, rng, pitch=rng.uniform(380, 440)), S.thump(0.6, 110, 0.25))
    knock2 = S.add(S.wood_block(0.5, rng, pitch=rng.uniform(340, 380)), S.thump(0.35, 100, 0.2))
    bell = S.lowpass(S.bell(S.mtof(TONIC - 24 + int(rng.choice([0, -2]))), 1.8, 0.7), 650, 2)
    x = S.place([(0, knock), (0.15, knock2), (0.06, bell), (0.24, wood_clack(rng, 0.25, 1300))])
    return S.reverb(S.tail(x, 0.4), 0.9, 0.18, bright=0.4)


def relic_use(rng):
    """A relic taken in: a warm swell of the tonic and its fifth, one slow heartbeat, and a bell over the beat."""
    root, fifth = _notes([0, 4], -12)
    swell = S.add(S.pad(root, 1.4, 0.6, rng, a=0.7, r=0.9, bright=0.25), S.pad(fifth, 1.4, 0.4, rng, a=0.8, r=0.9, bright=0.25))
    beat = S.lowpass(S.heartbeat(1.0, 46), 420)
    chord = [(0.78 + i * 0.06, S.music_box(f, vel=0.4, rng=rng)) for i, f in enumerate(_notes([0, 4, 7], 12))]
    x = S.place([(0, swell), (0.7, beat), (0.72, S.bell(S.mtof(TONIC + 12), 3.0, 0.5))] + chord)
    return S.reverb(S.tail(x, 0.8), 2.2, 0.3, bright=0.6)


def wonder_ambient(rng):
    """Near a wonder: a few music box notes of the lullaby drift by far away, over a breath of air and a faint
    glassy hum (played now and then by the reliquary, block/Reliquary.java)."""
    k = int(rng.integers(3, 6))
    degs = [int(d) for d in rng.choice([0, 2, 4, 7, 9, 11], k, replace=False)]
    at = np.cumsum(rng.uniform(0.35, 0.8, k)) - 0.35
    run = [(float(t), S.lowpass(S.music_box(f, vel=rng.uniform(0.35, 0.55), rng=rng), 3200)) for t, f in zip(at, _notes(degs, 12))]
    dur = float(at[-1]) + 2.5
    hum = S.pad(_notes([0], 0)[0], dur, 0.18, rng, a=1.2, r=1.4, bright=0.1)
    air = S.bandpass(S.noise(rng, dur), 900, 3000) * 0.04 * S.adsr(S.secs(dur), 1.0, 0.2, 0.8, 1.2)
    x = S.place(run + [(0, hum), (0, air)], dur)
    return S.reverb(S.tail(x, 1.0), 3.4, 0.45, bright=0.5)


RECIPES = {"reliquary_open": reliquary_open, "reliquary_locked": reliquary_locked, "relic_use": relic_use,
           "wonder_ambient": wonder_ambient}


def render(entry, variant):
    """Renders one file of a sound. Returns (buffer, vorbis quality)."""
    seed = zlib.crc32(f"{entry['id']}#{variant}".encode())
    rng = np.random.default_rng(seed)
    x = RECIPES[entry["recipe"]](rng)
    x = S.trim(S.fade(S.clean(x), 0.002, 0))
    return S.normalize(x, 0.89), 3
