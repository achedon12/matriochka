"""The mod's own sounds and music, synthesized from seeded recipes.

Every sound event is declared in SOUNDS below: its id, its kind (sfx, ambient loop, music), its subtitle in
English and French, and the recipe that renders it. gen.py calls gen(), which writes sounds.json, the subtitles,
the generated Java constants (content/Sounds.java) and, when a recipe changed, the .ogg files.

Rendering needs numpy and ffmpeg (libvorbis). A lock file (tools/sounds.lock.json) stores a hash of each
recipe and of the synthesizer sources: a sound is only rendered again when its hash changes, so gen.py runs
without numpy or ffmpeg as long as no recipe changed (the CI only has Pillow).

Output: mono 44.1 kHz Ogg Vorbis in assets/matriochka/sounds/<group>/<name>.ogg.
"""
import hashlib
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "sounds.lock.json")
NS = "matriochka"

# ------------------------------------------------------------------ the world palettes of music
# Each world's theme: a seed, a key and mode, a tempo and meter, and what plays it. The lullaby of World 0 is
# the motif (motif_seed=1000) the giant world, the boss and the endings come back to.
LULLABY = 1000
WORLD_THEMES = {
    0: dict(seed=1000, tonic=69, mode="ionian", bpm=84, beats=3, prog=[0, 3, 4, 0], prog_b=[5, 3, 4, 4],
            lead="box", bass="pluck_soft", drone=False, reverb=(2.0, 0.25)),
    1: dict(seed=1100, tonic=62, mode="dorian", bpm=96, beats=4, prog=[0, 3, 0, 6], prog_b=[2, 3, 6, 4],
            lead="flute", counter="box", bass="pluck_soft", swing=0.12, reverb=(1.6, 0.25)),
    2: dict(seed=1200, tonic=64, mode="phrygian_dom", bpm=112, beats=2, prog=[0, 6, 5, 0], prog_b=[3, 2, 1, 0],
            lead="tremolo", bass="pluck", drum="dance", reverb=(1.2, 0.18)),
    3: dict(seed=1300, tonic=57, mode="harmonic", bpm=70, beats=4, prog=[0, 5, 3, 4], prog_b=[5, 2, 3, 4],
            lead="bell", bass=None, pad=True, reverb=(3.2, 0.35), octave=12),
    4: dict(seed=1400, tonic=67, mode="mixolydian", bpm=88, beats=3, prog=[0, 6, 3, 0], prog_b=[3, 6, 4, 0],
            lead="flute", counter="box", bass="pluck_soft", reverb=(2.4, 0.3)),
    5: dict(seed=1500, tonic=60, mode="aeolian", bpm=58, beats=4, prog=[0, 5, 3, 4], prog_b=[5, 3, 6, 4],
            lead="box", bass=None, passes=1, reverb=(4.0, 0.45), lead_vel=0.7),
    6: dict(seed=1600, tonic=65, mode="lydian", bpm=76, beats=3, prog=[0, 1, 4, 0], prog_b=[1, 5, 4, 1],
            lead="box_rev", counter="box", bass="pluck_soft", reverb=(2.8, 0.35)),
    7: dict(seed=1700, tonic=50, mode="aeolian", bpm=64, beats=4, prog=[0, 5, 6, 0], prog_b=[3, 5, 4, 0],
            lead="bell", bass=None, pad=True, reverb=(3.6, 0.4), lowpass=2600, octave=12),
    8: dict(seed=1800, tonic=64, mode="aeolian", bpm=120, beats=4, prog=[0, 3, 6, 4], prog_b=[5, 6, 3, 4],
            lead="box", counter="pluck_soft", bass="pluck_soft", ticks=True, drone=False, passes=3, transpose_pass=5),
    9: dict(seed=1900, tonic=61, mode="phrygian", bpm=72, beats=4, prog=[0, 1, 0, 6], prog_b=[5, 1, 6, 0],
            lead="pluck", bass="pluck", heartbeat=True, reverb=(2.0, 0.25)),
    10: dict(seed=2000, motif_seed=LULLABY, tonic=62, mode="harmonic", bpm=92, beats=3, prog=[0, 3, 4, 0], prog_b=[5, 3, 4, 4],
             lead="tremolo", counter="box", bass="pluck", pad=True, drum="march", reverb=(2.6, 0.3)),
}
# Each world's two lesser biomes (tools/gen.py SUB_BIOMES) play a variation of the world's theme: the same key,
# mode and opening motif (the world's A phrase), with another seed for the rest and their own tempo, lead or colour.
# The first lesser biome sits on the world's wet edge, the second on its warm one.
SUB_THEMES = {
    1: {"bloom_hollow": dict(bpm=106, lead="box", counter="flute", reverb=(1.4, 0.22)),
        "rot_marsh": dict(bpm=76, lead="reed", counter=None, octave=0, swing=0.0, lowpass=2400, reverb=(2.6, 0.35))},
    2: {"ember_fields": dict(bpm=128, lead="pluck", counter="box"),
        "ash_drifts": dict(bpm=84, lead="reed", drum=None, drone=True, lowpass=3000, reverb=(2.4, 0.32))},
    3: {"mossy_cells": dict(bpm=62, lead="box", reverb=(3.8, 0.42)),
        "crumbling_wing": dict(bpm=78, lead="tremolo", octave=0, bass="pluck_soft", lowpass=3200)},
    4: {"hail_meadows": dict(bpm=96, lead="box", counter="flute", reverb=(2.8, 0.34)),
        "thunder_heights": dict(bpm=100, lead="reed", counter="box", drum="march")},
    5: {"hushed_hollow": dict(bpm=52, lead="bell", pad=True, lowpass=2200),
        "bare_dark": dict(bpm=64, lead="pluck_soft", octave=0, reverb=(4.6, 0.5))},
    6: {"crystal_fields": dict(bpm=72, lead="bell", counter="box"),
        "mirror_flats": dict(bpm=84, lead="box", counter="box_rev")},
    7: {"coral_shelf": dict(bpm=72, lead="box", counter="pluck_soft", octave=24, lowpass=4200, reverb=(3.0, 0.35)),
        "black_trench": dict(bpm=52, lead="reed", lowpass=1800, reverb=(4.6, 0.5))},
    8: {"hourglass_dunes": dict(bpm=104, lead="pluck", swing=0.1),
        "rust_grove": dict(bpm=92, lead="reed", counter="box", ticks=False)},
    9: {"flesh_mire": dict(bpm=60, lead="reed", lowpass=2400),
        "bare_rock": dict(bpm=84, lead="tremolo", drum="march", heartbeat=False)},
    10: {"plank_floor": dict(bpm=84, lead="box", counter="pluck_soft", drum=None),
         "lacquer_tray": dict(bpm=100, lead="bell", counter="box", drum="dance")},
}
# special pieces
PIECES = {
    "boss": dict(seed=3000, motif_seed=LULLABY, tonic=57, mode="harmonic", bpm=138, beats=2, prog=[0, 3, 4, 0], prog_b=[5, 3, 4, 4],
                 lead="tremolo", counter="box", bass="pluck", drum="drive", drone=True, reverb=(1.4, 0.2), passes=2, intro=2),
    "boss_final": dict(seed=3100, motif_seed=LULLABY, tonic=58, mode="phrygian_dom", bpm=152, beats=2, prog=[0, 6, 5, 0], prog_b=[3, 2, 1, 0],
                       lead="tremolo", counter="bell", bass="pluck", drum="drive", pad=True, reverb=(1.6, 0.22), passes=2, intro=1),
    "endings": dict(seed=3200, motif_seed=LULLABY, tonic=65, mode="ionian", bpm=66, beats=3, prog=[0, 3, 4, 0], prog_b=[5, 3, 1, 4],
                    lead="box", counter="flute", bass="pluck_soft", pad=True, reverb=(3.0, 0.35), passes=3, transpose_pass=0),
    # the adaptive music's tense variant, while creatures hunt the player: the lullaby in a dark mode, muffled
    "danger": dict(seed=3300, motif_seed=LULLABY, tonic=57, mode="phrygian", bpm=104, beats=4, prog=[0, 1, 0, 6], prog_b=[5, 1, 6, 0],
                   lead="tremolo", bass="pluck", drum="march", drone=True, reverb=(2.2, 0.3), passes=2, lowpass=3400, lead_vel=0.75),
}
# each boss fights to its own theme: the boss piece (the lullaby at a fighting tempo, driven by the drum) in its
# world's key and mode, led by its world's instrument; boss_final (below a third of its health) stays shared
_FIGHT_LEAD = {"box": "tremolo", "box_rev": "tremolo", "flute": "reed", "pluck_soft": "pluck"}
for _w, _t in WORLD_THEMES.items():
    PIECES[f"boss_w{_w}"] = dict(PIECES["boss"], seed=3000 + _w * 11, tonic=_t["tonic"] if _t["tonic"] >= 55 else _t["tonic"] + 12,
                                 mode=_t["mode"], bpm=max(124, min(150, int(_t["bpm"] * 1.45))),
                                 lead=_FIGHT_LEAD.get(_t["lead"], _t["lead"]),
                                 counter="bell" if _t["lead"] == "bell" else "box",
                                 pad=bool(_t.get("pad")), lowpass=_t.get("lowpass"),
                                 reverb=(max(1.2, _t.get("reverb", (1.6, 0.25))[0] * 0.6), 0.2))
# the lesser biomes' variations, played as music.world_<n>_<biome>
for _w, _subs in SUB_THEMES.items():
    _t = WORLD_THEMES[_w]
    for _i, (_sub, _over) in enumerate(_subs.items()):
        PIECES[f"world_{_w}_{_sub}"] = dict(_t, motif_seed=_t.get("motif_seed", _t["seed"]), seed=_t["seed"] + 37 + _i * 23, **_over)
# the adaptive music's layers and stings, rendered by tools/cues.py: (id, recipe)
# the wonders' recipes, rendered by tools/relic_sfx.py (hashed with that file, like the cues)
RELIC_RECIPES = ("reliquary_open", "reliquary_locked", "relic_use", "wonder_ambient")
# the Nesting Cradle's and the Matriarch Armour's recipes, rendered by tools/cradle_sfx.py (hashed with that file)
CRADLE_RECIPES = ("cradle_note", "cradle_chord", "shell_clack", "matriarch_crack")
CUES = [("music.layer_heartbeat", "layer_heartbeat"), ("music.sting_discovery", "sting_discovery"), ("music.sting_quest", "sting_quest")]

# ------------------------------------------------------------------ the table
# kind: sfx (one-shot), loop (ambient, seamless), music (streamed).
# (id, kind, recipe, variants, subtitle EN, subtitle FR)
def _sounds():
    t = []

    def s(sid, kind, recipe, variants=1, en=None, fr=None, **kw):
        t.append(dict(id=sid, kind=kind, recipe=recipe, variants=variants, en=en, fr=fr, args=kw))

    # nesting dolls
    s("doll.open", "sfx", "doll_open", 3, "Doll opens", "Une poupée s'ouvre")
    s("doll.close", "sfx", "doll_close", 3, "Doll closes", "Une poupée se referme")
    s("doll.click", "sfx", "doll_click", 3, "Doll clicks", "Clic de poupée")
    s("doll.rattle", "sfx", "doll_rattle", 2, "Doll rattles", "Une poupée cliquette")
    s("doll_of_life.break", "sfx", "doll_of_life", 1, "Doll of Life breaks", "La Poupée de vie se brise")
    # World Blocks
    s("world_block.enter", "sfx", "world_enter", 1, "World Block opens", "Le bloc-monde s'ouvre")
    s("world_block.form", "sfx", "world_form", 1, "World Block forms", "Un bloc-monde se forme")
    s("world_block.crack", "sfx", "world_crack", 2, "World Block cracks", "Le bloc-monde se fend")
    s("seed.pulse", "sfx", "seed_pulse", 1, "Seed hums", "La Graine vibre")
    # the rites that open Worlds 2 to 10: one sound while the rite is under way, one when it opens its world
    for w in range(2, 11):
        s(f"rite.w{w}", "sfx", "rite_layer", 2, "A rite stirs", "Un rite s'éveille", world=w)
        s(f"rite.open.w{w}", "sfx", "rite_open", 1, "A world opens", "Un monde s'ouvre", world=w)
    # stations
    for st in ("matrix_workbench", "class_table", "soul_altar", "spore_vat", "ash_foundry", "jailer_table", "lightning_forge",
               "dark_altar", "inverter", "abyssal_press", "time_workshop", "terrain_anchor", "final_loom"):
        en, fr = STATION_SUB[st]
        s(f"station.{st}", "sfx", "station_" + st, 2, en, fr)
    s("station.soul_altar.devour", "sfx", "station_devour", 1, "Soul Altar devours", "L'Autel des âmes dévore")
    s("station.grid.place", "sfx", "grid_place", 3, "Piece set on the grid", "Une pièce se pose sur la grille")
    s("station.grid.fill", "sfx", "grid_fill", 1, "The grid is laid out", "La grille se garnit")
    s("station.grid.ready", "sfx", "grid_ready", 1, "A recipe forms", "Une recette se forme")
    s("station.jailer_table.pin", "sfx", "jailer_pin", 3, "Lock pin clicks", "Une goupille cède")
    # bosses
    s("boss.awaken", "sfx", "boss_awaken", 1, "Boss awakens", "Un boss s'éveille")
    s("boss.phase", "sfx", "boss_phase", 1, "Boss shell cracks", "La coque du boss se fend")
    s("boss.defeat", "sfx", "boss_defeat", 1, "Boss defeated", "Boss vaincu")
    for w in range(0, 11):
        s(f"boss.telegraph.w{w}", "sfx", "telegraph", 2, "Boss prepares an attack", "Le boss prépare une attaque", world=w)
        s(f"boss.presence.w{w}", "sfx", "boss_presence", 3, "A boss breathes nearby", "Un boss respire tout près", world=w)
    # world rules
    s("world.gust", "sfx", "gust", 2, "Gust of wind", "Bourrasque")
    s("world.gravity_shift", "sfx", "gravity_shift", 1, "Gravity wavers", "La gravité vacille")
    s("world.quake", "sfx", "quake", 1, "Ground heaves", "Le sol se soulève")
    s("world.rumble", "sfx", "rumble", 2, "Ground rumbles", "Le sol gronde")
    # the wonders: the sealed reliquary, its relics and the hum around it (recipes in tools/relic_sfx.py)
    s("reliquary.open", "sfx", "reliquary_open", 1, "Reliquary unlocks", "Le reliquaire se déverrouille")
    s("reliquary.locked", "sfx", "reliquary_locked", 2, "Reliquary stays sealed", "Le reliquaire reste scellé")
    s("relic.use", "sfx", "relic_use", 1, "Relic taken in", "Une relique est absorbée")
    s("wonder.ambient", "sfx", "wonder_ambient", 3, "A wonder hums", "Une merveille fredonne")
    # the Nesting Cradle: a note of the lullaby per world's ore, the shells' clacks, the chord of the ten dolls; the
    # Matriarch Armour's outer doll cracking (recipes in tools/cradle_sfx.py)
    for w in range(1, 11):
        s(f"cradle.note.w{w}", "sfx", "cradle_note", 1, "An ore sings in the cradle", "Un minerai chante dans le berceau", world=w)
    s("cradle.clack", "sfx", "shell_clack", 3, "A golden doll closes", "Une poupée d'or se referme")
    s("cradle.chord", "sfx", "cradle_chord", 1, "The ten dolls close", "Les dix poupées se referment")
    s("matriarch.crack", "sfx", "matriarch_crack", 1, "The outer doll cracks", "La poupée extérieure se fend")
    # ambience: loops and one-shots per world
    for w in range(1, 11):
        s(f"ambient.w{w}.loop", "loop", "loop", 1, None, None, world=w)
    for sid, (recipe, variants, en, fr) in ADDITIONS.items():
        s(f"ambient.{sid}", "sfx", recipe, variants, en, fr)
    # music
    for w in WORLD_THEMES:
        s(f"music.world_{w}", "music", "theme", 1, None, None, world=w)
    for p in PIECES:
        s(f"music.{p}", "music", "piece", 1, None, None, piece=p)
    for sid, recipe in CUES:
        s(sid, "music", recipe, 1, None, None)
    return t


STATION_SUB = {
    "matrix_workbench": ("Matrix Workbench crafts", "L'Établi matriciel fabrique"),
    "class_table": ("Class Table hones", "La Table de classe affûte"),
    "soul_altar": ("Soul Altar purifies", "L'Autel des âmes purifie"),
    "spore_vat": ("Spore Vat bubbles", "La Cuve de spores bouillonne"),
    "ash_foundry": ("Ash Foundry pours", "La Fonderie de cendre coule"),
    "jailer_table": ("Lock opens", "La serrure s'ouvre"),
    "lightning_forge": ("Lightning Forge strikes", "La Forge à foudre frappe"),
    "dark_altar": ("Dark Altar whispers", "L'Autel obscur murmure"),
    "inverter": ("Inverter swaps", "L'Inverseur échange"),
    "abyssal_press": ("Abyssal Press compresses", "La Presse abyssale comprime"),
    "time_workshop": ("Time Workshop ticks", "L'Atelier du temps cliquette"),
    "terrain_anchor": ("Terrain Anchor settles", "L'Ancre de terrain se pose"),
    "final_loom": ("Final Loom weaves", "Le Métier final tisse"),
}

# ambient one-shots: (recipe, variants, EN, FR)
ADDITIONS = {
    "w0.creak": ("creak", 3, "Painted wood creaks", "Le bois peint craque"),
    "w1.insects": ("insects", 2, "Insects buzz", "Des insectes bourdonnent"),
    "w1.spore": ("spore_puff", 2, "Spores puff", "Des spores éclatent"),
    "w2.hammer": ("hammers", 2, "Distant hammers", "Marteaux au loin"),
    "w2.crackle": ("embers", 2, "Embers crackle", "Des braises crépitent"),
    "w3.chains": ("chains", 2, "Chains rattle", "Des chaînes cliquettent"),
    "w3.door": ("far_door", 2, "A door slams far away", "Une porte claque au loin"),
    "w4.whistle": ("whistle", 2, "Wind whistles", "Le vent siffle"),
    "w4.thunder": ("far_thunder", 2, "Distant thunder", "Tonnerre lointain"),
    "w5.breath": ("breath", 3, "Something breathes", "Quelque chose respire"),
    "w5.steps": ("steps", 2, "Footsteps nearby", "Des pas tout près"),
    "w6.reverse": ("reverse_chime", 2, "Chime plays backwards", "Un carillon à l'envers"),
    "w7.drip": ("drips", 3, "Water drips", "L'eau goutte"),
    "w7.groan": ("pressure_groan", 3, "Pressure groans", "La pression gémit"),
    "w8.chime": ("clock_chime", 2, "A clock strikes", "Une horloge sonne"),
    "w8.cuckoo": ("cuckoo", 1, "Cuckoo clock", "Coucou d'horloge"),
    "w9.heartbeat": ("ground_beat", 2, "The ground beats", "Le sol bat"),
    "w9.grind": ("rock_grind", 2, "Rock grinds", "La roche grince"),
}

# which ambient plays where: (loop, [(addition, chance per tick)])
WORLD_AMBIENT = {
    0: (None, [("w0.creak", 0.004)]),
    1: ("w1", [("w1.insects", 0.006), ("w1.spore", 0.004)]),
    2: ("w2", [("w2.hammer", 0.004), ("w2.crackle", 0.008)]),
    3: ("w3", [("w3.chains", 0.004), ("w3.door", 0.002)]),
    4: ("w4", [("w4.whistle", 0.006), ("w4.thunder", 0.0015)]),
    5: ("w5", [("w5.breath", 0.003), ("w5.steps", 0.002)]),
    6: ("w6", [("w6.reverse", 0.004)]),
    7: ("w7", [("w7.drip", 0.012), ("w7.groan", 0.003)]),
    8: ("w8", [("w8.chime", 0.002), ("w8.cuckoo", 0.0008)]),
    9: ("w9", [("w9.heartbeat", 0.004), ("w9.grind", 0.004)]),
    10: ("w10", [("w1.insects", 0.002), ("w4.whistle", 0.002), ("w7.drip", 0.003), ("w8.chime", 0.001), ("w9.grind", 0.002)]),
}

SOUNDS = _sounds()


def path_of(sid):
    """assets path of a sound id: station.spore_vat -> station/spore_vat"""
    head, _, rest = sid.partition(".")
    return f"{head}/{rest.replace('.', '_')}"


# ------------------------------------------------------------------ biome attributes
def biome_audio(n, sub=None):
    """The biome attributes that give world n its music and ambience; sub: one of its lesser biomes, which plays its
    own variation of the world's theme (SUB_THEMES)."""
    loop, adds = WORLD_AMBIENT[n]
    amb = {"additions": [{"sound": f"{NS}:ambient.{a}", "tick_chance": c} for a, c in adds]}
    if loop:
        amb["loop"] = f"{NS}:ambient.{loop}.loop"
    # under water and in creative mode the default track plays too
    track = f"world_{n}_{sub}" if sub else f"world_{n}"
    if sub and track not in PIECES:
        raise KeyError(f"no theme for the lesser biome {track} (SUB_THEMES)")
    music = {"default": {"sound": f"{NS}:music.{track}", "min_delay": 3600, "max_delay": 12000}}
    return {"minecraft:audio/ambient_sounds": amb, "minecraft:audio/background_music": music}


# ------------------------------------------------------------------ outputs
def _hash(entry):
    src = b"".join(open(os.path.join(HERE, f), "rb").read() for f in ("synth.py", "music.py", "sfx.py"))
    spec = json.dumps({k: entry[k] for k in ("id", "kind", "recipe", "variants", "args")}, sort_keys=True)
    if entry["recipe"] in dict(CUES).values():
        src += open(os.path.join(HERE, "cues.py"), "rb").read()
    elif entry["recipe"] in RELIC_RECIPES:
        src += open(os.path.join(HERE, "relic_sfx.py"), "rb").read()
    elif entry["recipe"] in CRADLE_RECIPES:
        src += open(os.path.join(HERE, "cradle_sfx.py"), "rb").read()
    elif entry["kind"] == "music":
        spec += json.dumps(WORLD_THEMES.get(entry["args"].get("world"), PIECES.get(entry["args"].get("piece"))), sort_keys=True)
    return hashlib.sha256(src + spec.encode()).hexdigest()[:16]


def _files(entry):
    base = path_of(entry["id"])
    if entry["variants"] == 1:
        return [base]
    return [f"{base}_{i + 1}" for i in range(entry["variants"])]


def _encode(x, out, quality):
    import numpy as np
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pcm = np.clip(x, -1, 1).astype("<f4").tobytes()
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", "44100", "-ac", "1", "-i", "-",
           "-c:a", "libvorbis", "-q:a", str(quality), "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact", out]
    subprocess.run(cmd, input=pcm, check=True)


def render_all(sound_dir, force=False):
    """Renders every sound whose recipe hash changed. Returns how many were rendered."""
    lock = json.load(open(LOCK)) if os.path.exists(LOCK) else {}
    todo = [e for e in SOUNDS if force or lock.get(e["id"]) != _hash(e)
            or not all(os.path.exists(os.path.join(sound_dir, f + ".ogg")) for f in _files(e))]
    if not todo:
        return 0
    if shutil.which("ffmpeg") is None:
        print(f"sound: {len(todo)} sounds out of date, but ffmpeg is missing; keeping the committed files")
        return 0
    try:
        import numpy  # noqa: F401
    except ImportError:
        print(f"sound: {len(todo)} sounds out of date, but numpy is missing; keeping the committed files")
        return 0
    import cradle_sfx
    import cues
    import relic_sfx
    import sfx
    for e in todo:
        for i, f in enumerate(_files(e)):
            x, q = (cues if e["recipe"] in cues.RECIPES else relic_sfx if e["recipe"] in relic_sfx.RECIPES
                    else cradle_sfx if e["recipe"] in cradle_sfx.RECIPES else sfx).render(e, i)
            _encode(x, os.path.join(sound_dir, f + ".ogg"), q)
        lock[e["id"]] = _hash(e)
        print(f"sound: rendered {e['id']}")
    # drop files of sounds that no longer exist
    keep = {os.path.join(sound_dir, f + ".ogg") for e in SOUNDS for f in _files(e)}
    for root, _, names in os.walk(sound_dir):
        for nm in names:
            p = os.path.join(root, nm)
            if p.endswith(".ogg") and p not in keep:
                os.remove(p)
    lock = {e["id"]: lock[e["id"]] for e in SOUNDS if e["id"] in lock}
    with open(LOCK, "w") as fh:
        json.dump(lock, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return len(todo)


def sounds_json():
    out = {}
    for e in SOUNDS:
        entry = {"sounds": []}
        for f in _files(e):
            snd = {"name": f"{NS}:{f}"}
            if e["kind"] in ("music", "loop"):
                snd["stream"] = True
            entry["sounds"].append(snd)
        if e["en"]:
            entry["subtitle"] = f"subtitles.{NS}.{e['id']}"
        out[e["id"]] = entry
    return out


def java(package):
    """content/Sounds.java: one SoundEvent per sound id, registered on class load."""
    def const(sid):
        return sid.upper().replace(".", "_")
    L = [f"package {package};", "",
         "import fr.achedon12.matriochka.Matriochka;",
         "import net.minecraft.core.Registry;",
         "import net.minecraft.core.registries.BuiltInRegistries;",
         "import net.minecraft.sounds.SoundEvent;", "",
         "/** GENERATED by tools/gen.py from tools/sound.py. Do not edit by hand. */",
         "public final class Sounds {", "\tprivate Sounds() {}", ""]
    for e in SOUNDS:
        L.append(f"\tpublic static final SoundEvent {const(e['id'])} = register(\"{e['id']}\");")
    L += ["",
          "\tprivate static SoundEvent register(String id) {",
          "\t\tvar key = Matriochka.id(id);",
          "\t\treturn Registry.register(BuiltInRegistries.SOUND_EVENT, key, SoundEvent.createVariableRangeEvent(key));",
          "\t}", "",
          "\t/** The work sound of a station, by its block id. */",
          "\tpublic static SoundEvent station(String id) {",
          "\t\treturn switch (id) {"]
    for st in STATION_SUB:
        L.append(f"\t\t\tcase \"{st}\" -> STATION_{st.upper()};")
    L += ["\t\t\tdefault -> STATION_MATRIX_WORKBENCH;", "\t\t};", "\t}", "",
          "\t/** The warning a boss gives before its attacks, by world (0 to 10). */",
          "\tpublic static SoundEvent telegraph(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(1, 11):
        L.append(f"\t\t\tcase {w} -> BOSS_TELEGRAPH_W{w};")
    L += ["\t\t\tdefault -> BOSS_TELEGRAPH_W0;", "\t\t};", "\t}", "",
          "\t/** What a boss sounds like while it is near and idle, by world (0 to 10). */",
          "\tpublic static SoundEvent presence(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(1, 11):
        L.append(f"\t\t\tcase {w} -> BOSS_PRESENCE_W{w};")
    L += ["\t\t\tdefault -> BOSS_PRESENCE_W0;", "\t\t};", "\t}", "",
          "\t/** The sound of a world's rite under way (2 to 10), or the Seed's hum for World 1. */",
          "\tpublic static SoundEvent rite(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(2, 11):
        L.append(f"\t\t\tcase {w} -> RITE_W{w};")
    L += ["\t\t\tdefault -> SEED_PULSE;", "\t\t};", "\t}", "",
          "\t/** The sound of a world opening when its rite completes (2 to 10), or the World Block forming for World 1. */",
          "\tpublic static SoundEvent riteOpen(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(2, 11):
        L.append(f"\t\t\tcase {w} -> RITE_OPEN_W{w};")
    L += ["\t\t\tdefault -> WORLD_BLOCK_FORM;", "\t\t};", "\t}", "",
          "\t/** The fight theme of a world's boss (0 to 10); the shared boss theme for anything else. */",
          "\tpublic static SoundEvent bossMusic(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(0, 11):
        L.append(f"\t\t\tcase {w} -> MUSIC_BOSS_W{w};")
    L += ["\t\t\tdefault -> MUSIC_BOSS;", "\t\t};", "\t}", "",
          "\t/** The note of the lullaby the ore of World w sings in the Nesting Cradle (1 to 10). */",
          "\tpublic static SoundEvent cradleNote(int world) {",
          "\t\treturn switch (world) {"]
    for w in range(1, 11):
        L.append(f"\t\t\tcase {w} -> CRADLE_NOTE_W{w};")
    L += ["\t\t\tdefault -> CRADLE_NOTE_W1;", "\t\t};", "\t}", "",
          "\t/** Loads the class, which registers every sound. */",
          "\tpublic static void init() {}", "}"]
    return "\n".join(L) + "\n"


def gen(assets, java_path, lang, write):
    """Called by gen.py: sounds.json, subtitles, Sounds.java and the audio files that are out of date."""
    for e in SOUNDS:
        if e["en"]:
            lang(f"subtitles.{NS}.{e['id']}", e["en"], e["fr"])
    write(os.path.join(assets, "sounds.json"), sounds_json())
    write(java_path, java("fr.achedon12.matriochka.content"))
    return render_all(os.path.join(assets, "sounds"))
