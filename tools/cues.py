"""Recipes of the adaptive music's layers and stings (see tools/sound.py and client/MusicThemes.java).

Kept apart from sfx.py on purpose: the lock file hashes sfx.py, music.py and synth.py into every sound, so adding
recipes there would render the whole library again. These recipes are hashed with this file on top of those three.

Each recipe takes a seeded numpy Generator and returns a mono buffer.
"""
import zlib

import numpy as np

import music as M
import synth as S

# the lullaby key of World 0 (A ionian): stings come back to it wherever they play
TONIC, MODE = 69, "ionian"


def _notes(degrees, octave=0):
    return [S.mtof(M.to_midi(TONIC + octave, MODE, d)) for d in degrees]


def layer_heartbeat(rng):
    """Low health or breath: a slow heartbeat over a muffled drone, an exact 9.6 second loop (eight beats)."""
    period, beats = 1.2, 8
    d = period * beats
    n = S.secs(d)
    parts = [(k * period, S.lowpass(S.heartbeat(0.9 if k % 2 == 0 else 0.8, 44), 260)) for k in range(beats + 2)]
    x = S.place(parts, d + 2.0)
    drone = S.pad(S.mtof(TONIC - 36), d + 2.0, 0.25, rng, a=0.5, r=0.5, bright=0.05)
    x = S.mix_into(x, S.lowpass(drone, 300), 0)
    x = S.loopify(S.clean(x[:n + S.secs(2.0)]), 2.0)
    return x[:n]


def sting_discovery(rng):
    """A place found: a music box climbs the lullaby's scale under a soft bell."""
    run = [(i * 0.11, S.music_box(f, vel=0.65, rng=rng)) for i, f in enumerate(_notes([0, 2, 4, 7, 9, 11], 12))]
    x = S.place(run + [(0.0, S.bell(S.mtof(TONIC), 2.6, 0.5)), (0.66, S.bell(S.mtof(TONIC + 7), 2.6, 0.45))])
    return S.reverb(S.tail(x, 1.0), 2.4, 0.32, bright=0.6)


def sting_quest(rng):
    """A quest done: a plucked cadence (fifth to tonic) and a bright chord with the frame drum."""
    fig = [(i * 0.14, S.pluck(f, 0.4, 0.7, rng=rng)) for i, f in enumerate(_notes([4, 3, 1, 4], 0))]
    chord = [(0.62, S.pluck(f, 1.6, 0.6, rng=rng)) for f in _notes([0, 2, 4, 7], 0)]
    x = S.place(fig + chord + [(0.62, S.music_box(S.mtof(TONIC + 24), vel=0.6, rng=rng)), (0.62, S.frame_drum(0.5, rng, 70, 0.5))])
    return S.reverb(S.tail(x, 1.0), 2.0, 0.28, bright=0.7)


RECIPES = {"layer_heartbeat": layer_heartbeat, "sting_discovery": sting_discovery, "sting_quest": sting_quest}
LOOPS = {"layer_heartbeat"}


def render(entry, variant):
    """Renders one file of a sound. Returns (buffer, vorbis quality)."""
    seed = zlib.crc32(f"{entry['id']}#{variant}".encode())
    rng = np.random.default_rng(seed)
    x = RECIPES[entry["recipe"]](rng)
    if entry["recipe"] in LOOPS:
        # a soft bed under the music, set by loudness like the ambient loops
        return x * min(0.12 / max(np.sqrt(np.mean(x ** 2)), 1e-9), 0.7 / np.max(np.abs(x))), 1
    x = S.trim(S.fade(S.clean(x), 0.002, 0))
    return S.normalize(x, 0.8), 2
