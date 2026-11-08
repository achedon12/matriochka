"""Recipes of the Nesting Cradle's sounds and of the Matriarch Armour's: the ten notes of the lullaby the ores sing when
they take their place on the ring, the chord the ten dolls close on, the wooden clack of a golden shell shutting and
the crack of the outer doll giving way (see tools/sound.py, block/NestingCradle.java and gear/Matriarch.java).

Kept apart from sfx.py like relic_sfx.py, so adding them does not render the whole library again: these recipes are
hashed with this file on top. Each recipe takes a seeded numpy Generator (and its own arguments) and returns a mono
buffer.
"""
import zlib

import numpy as np

import music as M
import synth as S
from sfx import hollow_pop, wood_clack, wood_crack

# the lullaby's key (A ionian, like the relics): the cradle belongs to the whole nest of worlds
TONIC, MODE = 69, "ionian"
# the scale degree each world's ore sings, World 1 to World 10: set in order, they climb the lullaby's scale
NOTE_DEGREES = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]


def _f(deg, octave=0):
    return S.mtof(M.to_midi(TONIC + octave, MODE, deg))


def cradle_note(rng, world=1):
    """An ore takes its place: one music box tine of the lullaby, a soft bell an octave below it and a glassy shimmer."""
    f = _f(NOTE_DEGREES[world - 1])
    tine = S.music_box(f, vel=0.9, rng=rng)
    under = S.bell(f / 2, 2.4, 0.35)
    shim = S.lowpass(S.music_box(f * 2, vel=0.25, rng=rng), 6000)
    x = S.place([(0, tine), (0.0, under), (0.06, shim)])
    return S.reverb(S.tail(x, 0.6), 2.2, 0.32, bright=0.7)


def cradle_chord(rng):
    """The ten dolls have closed: the lullaby's tonic chord struck on bells, a run of the music box up through it,
    and a warm swell under them."""
    bells = [(i * 0.04, S.bell(f, 4.0, 0.5 - i * 0.05)) for i, f in enumerate([_f(0, -12), _f(4, -12), _f(7, -12), _f(0)])]
    run = [(0.2 + i * 0.07, S.music_box(f, vel=0.45, rng=rng)) for i, f in enumerate(_f(d, 12) for d in (0, 2, 4, 7, 9, 11, 14))]
    swell = S.add(S.pad(_f(0, -24), 3.2, 0.5, rng, a=0.15, r=2.2, bright=0.3), S.pad(_f(4, -12), 3.2, 0.3, rng, a=0.2, r=2.2, bright=0.3))
    x = S.place(bells + run + [(0, swell), (0, hollow_pop(rng, 220, 0.8))])
    return S.reverb(S.tail(x, 1.2), 3.6, 0.38, bright=0.75)


def shell_clack(rng):
    """A golden doll shell shutting: two lacquered rims meeting, a hollow knock inside and a small ring of gold."""
    p = rng.uniform(560, 820)
    x = S.place([(0, wood_clack(rng, 1.0, p)), (0.004, S.thump(0.55, rng.uniform(130, 170), 0.18)),
                 (0.01, S.lowpass(S.bell(rng.uniform(1400, 1800), 0.8, 0.12), 5000))])
    return S.reverb(S.tail(x, 0.25), 0.6, 0.2, bright=0.6)


def matriarch_crack(rng):
    """The Nested Shell takes a deadly blow: the outer doll's lacquer splits, gold shards ring as they fall, a low
    bell holds."""
    shards = [(0.06 + i * rng.uniform(0.03, 0.06), S.lowpass(S.music_box(rng.uniform(1800, 3200), vel=0.25, rng=rng), 7000)) for i in range(6)]
    x = S.place([(0, wood_crack(rng, 0.55, 1.0)), (0.02, S.bell(_f(0, -12), 2.6, 0.55))] + shards)
    return S.reverb(S.tail(x, 0.6), 1.8, 0.3, bright=0.55)


RECIPES = {"cradle_note": cradle_note, "cradle_chord": cradle_chord, "shell_clack": shell_clack, "matriarch_crack": matriarch_crack}


def render(entry, variant):
    """Renders one file of a sound. Returns (buffer, vorbis quality)."""
    seed = zlib.crc32(f"{entry['id']}#{variant}".encode())
    rng = np.random.default_rng(seed)
    x = RECIPES[entry["recipe"]](rng, **entry["args"])
    x = S.trim(S.fade(S.clean(x), 0.002, 0))
    return S.normalize(x, 0.89), 3
