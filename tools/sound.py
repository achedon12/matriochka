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
# special pieces
PIECES = {
    "boss": dict(seed=3000, motif_seed=LULLABY, tonic=57, mode="harmonic", bpm=138, beats=2, prog=[0, 3, 4, 0], prog_b=[5, 3, 4, 4],
                 lead="tremolo", counter="box", bass="pluck", drum="drive", drone=True, reverb=(1.4, 0.2), passes=2, intro=2),
    "boss_final": dict(seed=3100, motif_seed=LULLABY, tonic=58, mode="phrygian_dom", bpm=152, beats=2, prog=[0, 6, 5, 0], prog_b=[3, 2, 1, 0],
                       lead="tremolo", counter="bell", bass="pluck", drum="drive", pad=True, reverb=(1.6, 0.22), passes=2, intro=1),
    "endings": dict(seed=3200, motif_seed=LULLABY, tonic=65, mode="ionian", bpm=66, beats=3, prog=[0, 3, 4, 0], prog_b=[5, 3, 1, 4],
                    lead="box", counter="flute", bass="pluck_soft", pad=True, reverb=(3.0, 0.35), passes=3, transpose_pass=0),
}

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
    # stations
    for st in ("matrix_workbench", "class_table", "soul_altar", "spore_vat", "ash_foundry", "jailer_table", "lightning_forge",
               "dark_altar", "inverter", "abyssal_press", "time_workshop", "terrain_anchor", "final_loom"):
        en, fr = STATION_SUB[st]
        s(f"station.{st}", "sfx", "station_" + st, 2, en, fr)
    s("station.soul_altar.devour", "sfx", "station_devour", 1, "Soul Altar devours", "L'Autel des âmes dévore")
    s("station.jailer_table.pin", "sfx", "jailer_pin", 3, "Lock pin clicks", "Une goupille cède")
    # bosses
    s("boss.awaken", "sfx", "boss_awaken", 1, "Boss awakens", "Un boss s'éveille")
    s("boss.phase", "sfx", "boss_phase", 1, "Boss shell cracks", "La coque du boss se fend")
    s("boss.defeat", "sfx", "boss_defeat", 1, "Boss defeated", "Boss vaincu")
    for w in range(0, 11):
        s(f"boss.telegraph.w{w}", "sfx", "telegraph", 2, "Boss prepares an attack", "Le boss prépare une attaque", world=w)
    # world rules
    s("world.gust", "sfx", "gust", 2, "Gust of wind", "Bourrasque")
    s("world.gravity_shift", "sfx", "gravity_shift", 1, "Gravity wavers", "La gravité vacille")
    s("world.quake", "sfx", "quake", 1, "Ground heaves", "Le sol se soulève")
    s("world.rumble", "sfx", "rumble", 2, "Ground rumbles", "Le sol gronde")
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
def biome_audio(n):
    """The biome attributes that give world n its music and ambience."""
    loop, adds = WORLD_AMBIENT[n]
    amb = {"additions": [{"sound": f"{NS}:ambient.{a}", "tick_chance": c} for a, c in adds]}
    if loop:
        amb["loop"] = f"{NS}:ambient.{loop}.loop"
    # under water and in creative mode the default track plays too
    music = {"default": {"sound": f"{NS}:music.world_{n}", "min_delay": 3600, "max_delay": 12000}}
    return {"minecraft:audio/ambient_sounds": amb, "minecraft:audio/background_music": music}


# ------------------------------------------------------------------ outputs
def _hash(entry):
    src = b"".join(open(os.path.join(HERE, f), "rb").read() for f in ("synth.py", "music.py", "sfx.py"))
    spec = json.dumps({k: entry[k] for k in ("id", "kind", "recipe", "variants", "args")}, sort_keys=True)
    if entry["kind"] == "music":
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
    import sfx
    for e in todo:
        for i, f in enumerate(_files(e)):
            x, q = sfx.render(e, i)
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
