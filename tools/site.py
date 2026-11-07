#!/usr/bin/env python3
"""Exports the data and assets of the Matriochka website (the Next.js app in site/).

Usage: python3 tools/site.py   (run automatically by `npm run build` in site/, through scripts/build-data.mjs)

Reads tools/content.py, the generated lang files, the Java recipes, the biome spawn tables, the GeckoLib
models and animations, the logo in branding/ and the in-game screenshots (build/run/clientGameTest/screenshots,
optional), then writes site/data/{en,fr,shared}.json and copies everything the pages show into site/public.
Pillow is used to crop screenshots and make icons; without it, the files already in site/public are kept.
"""
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import content as C  # noqa: E402
import attacks as ATK  # noqa: E402

RES = os.path.join(ROOT, "src/main/resources/assets/matriochka")
TEX = os.path.join(RES, "textures")
SHOTS_SRC = os.path.join(ROOT, "media/gui")
# In-game stills of every boss attack, moves_<boss>_<slug>_<windup|strike>.png (optional, not in the repo)
MOVES_SRC = os.environ.get("MATRIOCHKA_MOVES", os.path.join(ROOT, "media/moves"))
RECIPES_JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Recipes.java")

REPO = "https://github.com/achedon12/matriochka"
RELEASES = REPO + "/releases"
WIKI = REPO + "/wiki"
SITE = "https://achedon12.github.io/matriochka/"
DISCORD = "https://discord.gg/SPVCf5hRuh"
# the version shown on the site follows gradle.properties
VERSION = next(l.split("=", 1)[1].strip() for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gradle.properties")) if l.startswith("mod_version="))
# Shell Shards every boss leaves to each fighter (entity/MatrioBoss.java)
SHELL_SHARDS = int(re.search(r"SHELL_SHARDS = (\d+);", open(os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/entity/MatrioBoss.java"), encoding="utf-8").read()).group(1))

# Lucide icons (lucide-static 0.460.0, ISC licence), inner SVG markup only.
ICONS = {
    'book-open': '<path d="M12 7v14"/> <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    'bug': '<path d="m8 2 1.88 1.88"/> <path d="M14.12 3.88 16 2"/> <path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1"/> <path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6"/> <path d="M12 20v-9"/> <path d="M6.53 9C4.6 8.8 3 7.1 3 5"/> <path d="M6 13H2"/> <path d="M3 21c0-2.1 1.7-3.9 3.8-4"/> <path d="M20.97 5c0 2.1-1.6 3.8-3.5 4"/> <path d="M22 13h-4"/> <path d="M17.2 17c2.1.1 3.8 1.9 3.8 4"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'circle-alert': '<circle cx="12" cy="12" r="10"/> <line x1="12" x2="12" y1="8" y2="12"/> <line x1="12" x2="12.01" y1="16" y2="16"/>',
    'clock': '<circle cx="12" cy="12" r="10"/> <polyline points="12 6 12 12 16 14"/>',
    'cpu': '<rect width="16" height="16" x="4" y="4" rx="2"/> <rect width="6" height="6" x="9" y="9" rx="1"/> <path d="M15 2v2"/> <path d="M15 20v2"/> <path d="M2 15h2"/> <path d="M2 9h2"/> <path d="M20 15h2"/> <path d="M20 9h2"/> <path d="M9 2v2"/> <path d="M9 20v2"/>',
    'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/> <polyline points="7 10 12 15 17 10"/> <line x1="12" x2="12" y1="15" y2="3"/>',
    'droplets': '<path d="M7 16.3c2.2 0 4-1.83 4-4.05 0-1.16-.57-2.26-1.71-3.19S7.29 6.75 7 5.3c-.29 1.45-1.14 2.84-2.29 3.76S3 11.1 3 12.25c0 2.22 1.8 4.05 4 4.05z"/> <path d="M12.56 6.6A10.97 10.97 0 0 0 14 3.02c.5 2.5 2 4.9 4 6.5s3 3.5 3 5.5a6.98 6.98 0 0 1-11.91 4.97"/>',
    'eye': '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/> <circle cx="12" cy="12" r="3"/>',
    'external-link': '<path d="M15 3h6v6"/> <path d="M10 14 21 3"/> <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    'flame': '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    'gem': '<path d="M6 3h12l4 6-10 13L2 9Z"/> <path d="M11 3 8 9l4 13 4-13-3-6"/> <path d="M2 9h20"/>',
    'github': '<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/> <path d="M9 18c-4.51 2-5-2-7-2"/>',
    'hammer': '<path d="m15 12-8.373 8.373a1 1 0 1 1-3-3L12 9"/> <path d="m18 15 4-4"/> <path d="m21.5 11.5-1.914-1.914A2 2 0 0 1 19 8.172V7l-2.26-2.26a6 6 0 0 0-4.202-1.756L9 2.96l.92.82A6.18 6.18 0 0 1 12 8.4V10l2 2h1.172a2 2 0 0 1 1.414.586L18.5 14.5"/>',
    'heart': '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    'hourglass': '<path d="M5 22h14"/> <path d="M5 2h14"/> <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22"/> <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2"/>',
    'info': '<circle cx="12" cy="12" r="10"/> <path d="M12 16v-4"/> <path d="M12 8h.01"/>',
    'key': '<path d="m15.5 7.5 2.3 2.3a1 1 0 0 0 1.4 0l2.1-2.1a1 1 0 0 0 0-1.4L19 4"/> <path d="m21 2-9.6 9.6"/> <circle cx="7.5" cy="15.5" r="5.5"/>',
    'languages': '<path d="m5 8 6 6"/> <path d="m4 14 6-6 2-3"/> <path d="M2 5h12"/> <path d="M7 2h1"/> <path d="m22 22-5-10-5 10"/> <path d="M14 18h6"/>',
    'layers': '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/> <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/> <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    'map-pin': '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/> <circle cx="12" cy="10" r="3"/>',
    'menu': '<line x1="4" x2="20" y1="12" y2="12"/> <line x1="4" x2="20" y1="6" y2="6"/> <line x1="4" x2="20" y1="18" y2="18"/>',
    'moon': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    'mountain': '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    'package': '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/> <path d="M12 22V12"/> <path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"/> <path d="m7.5 4.27 9 5.15"/>',
    'scale': '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/> <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/> <path d="M7 21h10"/> <path d="M12 3v18"/> <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    'shield': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    'skull': '<path d="m12.5 17-.5-1-.5 1h1z"/> <path d="M15 22a1 1 0 0 0 1-1v-1a2 2 0 0 0 1.56-3.25 8 8 0 1 0-11.12 0A2 2 0 0 0 8 20v1a1 1 0 0 0 1 1z"/> <circle cx="15" cy="12" r="1"/> <circle cx="9" cy="12" r="1"/>',
    'sparkles': '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/> <path d="M20 3v4"/> <path d="M22 5h-4"/> <path d="M4 17v2"/> <path d="M5 18H3"/>',
    'sprout': '<path d="M7 20h10"/> <path d="M10 20c5.5-2.5.8-6.4 3-10"/> <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/> <path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    'swords': '<polyline points="14.5 17.5 3 6 3 3 6 3 17.5 14.5"/> <line x1="13" x2="19" y1="19" y2="13"/> <line x1="16" x2="20" y1="16" y2="20"/> <line x1="19" x2="21" y1="21" y2="19"/> <polyline points="14.5 6.5 18 3 21 3 21 6 17.5 9.5"/> <line x1="5" x2="9" y1="14" y2="18"/> <line x1="7" x2="4" y1="17" y2="20"/> <line x1="3" x2="5" y1="19" y2="21"/>',
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/> <circle cx="9" cy="7" r="4"/> <path d="M22 21v-2a4 4 0 0 0-3-3.87"/> <path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'wind': '<path d="M12.8 19.6A2 2 0 1 0 14 16H2"/> <path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/> <path d="M9.8 4.4A2 2 0 1 1 11 8H2"/>',
    'x': '<path d="M18 6 6 18"/> <path d="m6 6 12 12"/>',
    'play': '<polygon points="6 3 20 12 6 21 6 3"/>',
    'rotate-3d': '<path d="M16.466 7.5C15.643 4.237 13.952 2 12 2 9.239 2 7 6.477 7 12s2.239 10 5 10c.342 0 .677-.069 1-.2"/> <path d="m15.194 13.707 3.814 1.86-1.86 3.814"/> <path d="M19 15.57c-1.804.885-4.274 1.43-7 1.43-5.523 0-10-2.239-10-5s4.477-5 10-5c4.838 0 8.873 1.718 9.8 4"/>',
}


# ---------------------------------------------------------------- language plumbing
LANG = "en"


def t(en, fr=None):
    """Pick the string of the current language."""
    if isinstance(en, dict):
        return en[LANG]
    return en if LANG == "en" or fr is None else fr


def e(s):
    return html.escape(str(s), quote=True)


def load_lang(code):
    p = os.path.join(RES, "lang", code + ".json")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


LANGS = {"en": load_lang("en_us"), "fr": load_lang("fr_fr")}

VANILLA = {
    "arrow": ("Arrow", "Flèche"), "baked_potato": ("Baked Potato", "Pomme de terre cuite"), "blaze_powder": ("Blaze Powder", "Poudre de blaze"),
    "chorus_fruit": ("Chorus Fruit", "Chorus"), "cooked_cod": ("Cooked Cod", "Morue cuite"), "cookie": ("Cookie", "Cookie"),
    "copper_ingot": ("Copper Ingot", "Lingot de cuivre"), "echo_shard": ("Echo Shard", "Éclat d'écho"), "emerald": ("Emerald", "Émeraude"),
    "enchanted_book": ("Enchanted Book", "Livre enchanté"), "experience_bottle": ("Bottle o' Enchanting", "Fiole d'expérience"),
    "glow_berries": ("Glow Berries", "Baies lumineuses"), "glowstone_dust": ("Glowstone Dust", "Poudre lumineuse"), "gold_block": ("Block of Gold", "Bloc d'or"),
    "golden_apple": ("Golden Apple", "Pomme dorée"), "golden_carrot": ("Golden Carrot", "Carotte dorée"), "heart_of_the_sea": ("Heart of the Sea", "Cœur de la mer"),
    "lead": ("Lead", "Laisse"), "mushroom_stew": ("Mushroom Stew", "Ragoût de champignons"), "name_tag": ("Name Tag", "Étiquette"),
    "netherite_scrap": ("Netherite Scrap", "Fragment de netherite"), "prismarine_shard": ("Prismarine Shard", "Éclat de prismarine"),
    "pumpkin_pie": ("Pumpkin Pie", "Tarte à la citrouille"), "shulker_shell": ("Shulker Shell", "Carapace de shulker"), "spyglass": ("Spyglass", "Longue-vue"),
    "torch": ("Torch", "Torche"), "totem_of_undying": ("Totem of Undying", "Totem d'immortalité"),
    "iron_ingot": ("Iron Ingot", "Lingot de fer"), "oak_log": ("Oak Log", "Bûche de chêne"),
    "oak_planks": ("Oak Planks", "Planches de chêne"), "white_wool": ("White Wool", "Laine blanche"),
    "ender_pearl": ("Ender Pearl", "Perle de l'Ender"), "red_dye": ("Red Dye", "Teinture rouge"),
    "gold_ingot": ("Gold Ingot", "Lingot d'or"), "paper": ("Paper", "Papier"),
    "smithing_table": ("Smithing Table", "Table de forge"), "crying_obsidian": ("Crying Obsidian", "Obsidienne pleureuse"),
    "chest": ("Chest", "Coffre"), "honeycomb": ("Honeycomb", "Rayon de miel"), "cauldron": ("Cauldron", "Chaudron"),
    "blast_furnace": ("Blast Furnace", "Haut fourneau"), "lightning_rod": ("Lightning Rod", "Paratonnerre"),
    "obsidian": ("Obsidian", "Obsidienne"), "observer": ("Observer", "Observateur"), "piston": ("Piston", "Piston"), "iron_pickaxe": ("Iron Pickaxe", "Pioche en fer"),
    "clock": ("Clock", "Horloge"), "anvil": ("Anvil", "Enclume"), "loom": ("Loom", "Métier à tisser"),
    "dirt": ("Dirt", "Terre"), "bone_meal": ("Bone Meal", "Poudre d'os"), "glass_bottle": ("Glass Bottle", "Fiole"),
    "string": ("String", "Ficelle"), "bowl": ("Bowl", "Bol"), "stick": ("Stick", "Bâton"), "ice": ("Ice", "Glace"),
    "redstone": ("Redstone Dust", "Poudre de redstone"), "bread": ("Bread", "Pain"),
    "iron_nugget": ("Iron Nugget", "Pépite de fer"), "gold_nugget": ("Gold Nugget", "Pépite d'or"),
    "cooked_beef": ("Steak", "Steak"), "apple": ("Apple", "Pomme"), "lantern": ("Lantern", "Lanterne"),
    "amethyst_shard": ("Amethyst Shard", "Éclat d'améthyste"), "honey_bottle": ("Honey Bottle", "Fiole de miel"),
    "brown_mushroom": ("Brown Mushroom", "Champignon brun"), "diamond": ("Diamond", "Diamant"),
    "quartz": ("Nether Quartz", "Quartz du Nether"), "kelp": ("Kelp", "Algue"),
    "prismarine_crystals": ("Prismarine Crystals", "Cristaux de prismarine"), "dried_kelp": ("Dried Kelp", "Algue séchée"),
    "glass": ("Glass", "Verre"), "sweet_berries": ("Sweet Berries", "Baies sucrées"),
    "leather_boots": ("Leather Boots", "Bottes en cuir"), "iron_chain": ("Iron Chain", "Chaîne en fer"),
}


def name(id_):
    """Display name of an item, block or entity id, in the current language."""
    if id_.startswith("minecraft:"):
        v = VANILLA.get(id_[10:])
        if not v:
            print(f"site.py: no French name for {id_}, add it to VANILLA", file=sys.stderr)
        return t(*v) if v else id_[10:].replace("_", " ").capitalize()
    d = LANGS[LANG]
    for k in ("item", "block", "entity"):
        if f"{k}.matriochka.{id_}" in d:
            return d[f"{k}.matriochka.{id_}"]
    return id_.replace("_", " ").capitalize()


def world_name(n):
    if n == 0:
        return t("The Surface", "La Surface")
    w = C.WORLDS[n - 1]
    return w[LANG]


# ---------------------------------------------------------------- recipes from the Java source
def parse_recipes():
    src = open(RECIPES_JAVA, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'^\s*(?:for \(.*?\) )?r\((W|"(\w+)"), "(\w+)"(?: \+ i)?, (\d+), (-?\w+), (.*?)\);', src, re.M):
        station = "matrix_workbench" if m.group(1) == "W" else m.group(2)
        out_id = m.group(3)
        if "world_soil_" in out_id:
            continue
        args = re.findall(r'"([\w:]+)", (\d+)', m.group(6))
        out.setdefault(station, []).append(dict(out=out_id, count=int(m.group(4)), inputs=[(a, int(b)) for a, b in args]))
    for m in re.finditer(r'gear\("(\w+)", (\d+), "(\w+)", "(\w+)", "(\w+)"\);', src):
        st, _, weapon, set_, res = m.groups()
        lst = out.setdefault(st, [])
        if not any(r["out"] == weapon for r in lst):
            lst.append(dict(out=weapon, count=1, inputs=[(res, 8), ("minecraft:stick", 1)]))
        for piece, n in (("helmet", 5), ("chestplate", 8), ("leggings", 7), ("boots", 4)):
            lst.append(dict(out=f"{set_}_{piece}", count=1, inputs=[(res, n)]))
    # the explicit sporite sword recipe replaces the generic one
    for st, lst in out.items():
        seen = {}
        for r in lst:
            seen[r["out"]] = r
        out[st] = list(seen.values())
    return out


RECIPES = parse_recipes()


def recipe_for(out_id):
    for st, lst in RECIPES.items():
        for r in lst:
            if r["out"] == out_id:
                return st, r
    return None, None


# ---------------------------------------------------------------- output folders of the Next.js site
APP = os.path.join(ROOT, "site")
PUBLIC = os.path.join(APP, "public")
DATA = os.path.join(APP, "data")
GEO = os.path.join(RES, "geckolib/models/entity")
ANIM = os.path.join(RES, "geckolib/animations/entity")
BIOMES = os.path.join(ROOT, "src/main/resources/data/matriochka/worldgen/biome")
BRANDING = os.path.join(ROOT, "branding")
TRAILER_SRC = os.path.join(ROOT, "media/trailer/matriochka-trailer-web.mp4")
REEL_SRC = os.path.join(ROOT, "media/trailer/reel.mp4")
TRAILER_POSTER = os.path.join(ROOT, "media/brag-output/brag.jpg")

try:
    from PIL import Image
except ImportError:  # the site still builds; screenshots and icons already in site/public are kept
    Image = None

ITEM_TEX = set()
VANILLA_TEX = set()
STATION_IMG = set()
CUBE_TEX = set()
ENTITY_TEX = set()
BLOCK_TEX = set()
SHOTS = {}


def _copy_dir(src, dst, suffix):
    os.makedirs(dst, exist_ok=True)
    out = set()
    for f in sorted(os.listdir(src)):
        if f.endswith(suffix):
            shutil.copy2(os.path.join(src, f), os.path.join(dst, f))
            out.add(f[: -len(suffix)])
    return out


def copy_assets():
    ITEM_TEX.update(_copy_dir(os.path.join(TEX, "item"), os.path.join(PUBLIC, "items"), ".png"))
    ENTITY_TEX.update(_copy_dir(os.path.join(TEX, "entity"), os.path.join(PUBLIC, "entities"), ".png"))
    BLOCK_TEX.update(_copy_dir(os.path.join(TEX, "block"), os.path.join(PUBLIC, "blocks"), ".png"))
    _copy_dir(GEO, os.path.join(PUBLIC, "models"), ".geo.json")
    _copy_dir(ANIM, os.path.join(PUBLIC, "animations"), ".animation.json")
    # recipe cards: vanilla ingredient icons, block cubes and the sculpted stations
    import site_visuals
    vanilla = {i for st in RECIPES.values() for r in st for i, _n in r["inputs"] if i.startswith("minecraft:")}
    VANILLA_TEX.update(site_visuals.vanilla_icons(PUBLIC, vanilla))
    station_ids = [s[0] for s in C.STATIONS]
    STATION_IMG.update(site_visuals.station_renders(PUBLIC, station_ids))
    CUBE_TEX.update(site_visuals.block_icons(PUBLIC, os.path.join(TEX, "block"), [b["id"] for b in C.BLOCKS], set(station_ids)))
    process_shots(os.path.join(PUBLIC, "shots"))
    process_moves(os.path.join(PUBLIC, "shots", "moves"))
    process_frames(os.path.join(PUBLIC, "shots"))
    if os.path.exists(TRAILER_SRC):
        shutil.copy2(TRAILER_SRC, os.path.join(PUBLIC, "trailer.mp4"))
        poster = os.path.join(ROOT, "media/trailer/poster.jpg")
        if Image is not None and os.path.exists(poster):
            Image.open(poster).convert("RGB").resize((1280, 720), Image.LANCZOS).save(
                os.path.join(PUBLIC, "trailer.jpg"), quality=84, optimize=True, progressive=True)
    if os.path.exists(REEL_SRC):
        shutil.copy2(REEL_SRC, os.path.join(PUBLIC, "reel.mp4"))
        shutil.copy2(REEL_SRC.replace(".mp4", ".jpg"), os.path.join(PUBLIC, "reel.jpg"))
    branding()


def branding():
    """The official logo: site mark, favicons and the Open Graph card."""
    logo = os.path.join(BRANDING, "logo-256.png")
    if not os.path.exists(logo):
        return
    for size in (128, 256, 512):
        src = os.path.join(BRANDING, f"logo-{size}.png")
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(PUBLIC, f"logo-{size}.png"))
    if Image is None:
        return
    im = Image.open(logo).convert("RGBA")
    for s in (16, 32, 48, 192):
        im.resize((s, s), Image.LANCZOS).save(os.path.join(PUBLIC, f"favicon-{s}.png"), optimize=True)
    im.save(os.path.join(PUBLIC, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
    sq = Image.open(os.path.join(BRANDING, "icon-square-1024.png")).convert("RGB")
    sq.resize((180, 180), Image.LANCZOS).save(os.path.join(PUBLIC, "apple-touch-icon.png"), optimize=True)
    og = Image.new("RGB", (1200, 630), (0x17, 0x10, 0x0D))
    band = Image.new("RGB", (1200, 470), (0xA8, 0x23, 0x1A))
    og.paste(band, (0, 80))
    big = Image.open(os.path.join(BRANDING, "logo-512.png")).convert("RGBA").resize((520, 520), Image.LANCZOS)
    og.paste(big, (340, 55), big)
    og.save(os.path.join(PUBLIC, "og.png"), optimize=True)


def _gui_bbox(img):
    """The mod's GUI is drawn in the top-left 854x480 area of test captures; find its lacquer frame."""
    region = img.crop((0, 0, min(854, img.width), min(480, img.height))).convert("RGB")
    px = region.load()
    xs, ys = [], []
    for y in range(0, region.height, 2):
        for x in range(0, region.width, 2):
            r, g, b = px[x, y]
            if r > 140 and g < 70 and b < 60:
                xs.append(x)
                ys.append(y)
    if len(xs) < 50:
        return (0, 0, region.width, region.height)
    pad = 8
    return (max(0, min(xs) - pad), max(0, min(ys) - pad), min(region.width, max(xs) + pad), min(region.height, max(ys) + pad))


# Test captures draw the HUD, the hotbar and the chat in the top-left 854x480 area, and the player's arm
# from x 1400. These crops keep clear of both, so no chat line and no player name is ever shown.
CROP_TALL = (760, 150, 1360, 1050)   # 600x900: the doll-shaped windows
CROP_WIDE = (620, 60, 1900, 1020)    # 1280x960: boss plates and the home page
# Captures that do not show what the page describes (fog, full-bright test client, boss hidden behind a
# marker column). Threshold captures carry advancement chat lines and are never used.
SKIP_SHOTS = {"w03_view", "w05_view", "w03_boss", "w05_boss", "w06_boss", "w08_boss", "w09_boss"}


SEQ_FRAME = 35  # a settled frame of each cinematic sequence
# Cinematic frames are used only for the keys listed here, once checked by eye: takes are recorded and
# re-recorded in the same folder, and an unchecked frame can be black or mid-transition.
SEQ_USE = {"00_surface"}


def _sources():
    """key -> (path, HUD-free). Cinematic frames (seq_wNN_a/c_XXXX) win over the older test captures."""
    out = {}
    if not os.path.isdir(SHOTS_SRC):
        return out
    files = sorted(os.listdir(SHOTS_SRC))
    for f in files:
        m = re.match(r"(w\d\d_boss|gui_[\w]+)\.png$", f)
        if m and m.group(1) not in SKIP_SHOTS:
            out[m.group(1)] = (os.path.join(SHOTS_SRC, f), False)
    seqs = {}
    for f in files:
        m = re.match(r"seq_w(\d\d)_([ac])_(\d{4})\.png$", f)
        if m:
            seqs.setdefault((m.group(1), m.group(2)), []).append((int(m.group(3)), f))
    for (nn, kind), frames in seqs.items():
        frames.sort()
        if frames[-1][0] < SEQ_FRAME + 5:  # sequence still being recorded, or too short to have settled
            continue
        pick = min(frames, key=lambda x: abs(x[0] - SEQ_FRAME))[1]
        key = ("00_surface" if nn == "00" else f"w{nn}_view") if kind == "a" else f"w{nn}_boss"
        if key not in SEQ_USE:
            continue
        out[key] = (os.path.join(SHOTS_SRC, pick), True)
    return out


def process_shots(dst):
    os.makedirs(dst, exist_ok=True)
    # keep what earlier runs produced: CI has no game captures, and the capture folder gets cleared
    for f in os.listdir(dst):
        if os.path.isfile(os.path.join(dst, f)):
            SHOTS[f.rsplit(".", 1)[0]] = f
    if Image is None:
        return
    for key, (src, clean) in sorted(_sources().items()):
        try:
            img = Image.open(src)
            img.load()
        except OSError:
            continue
        if key.startswith("gui_"):
            # the whole 854x480 interface area, doubled pixel for pixel so the art stays crisp
            box = (0, 0, 290, 105) if key.startswith("gui_hud") else (0, 0, min(854, img.width), min(480, img.height))
            g = img.crop(box).convert("RGB")
            g = g.resize((g.width * (3 if key.startswith("gui_hud") else 2), g.height * (3 if key.startswith("gui_hud") else 2)), Image.NEAREST)
            g.save(os.path.join(dst, key + ".png"), optimize=True)
            SHOTS[key] = key + ".png"
            continue
        rgb = img.convert("RGB")
        W, H = rgb.size
        tall = (W // 2 - H // 3, 0, W // 2 + H // 3, H) if clean else CROP_TALL
        wide = (W // 2 - H * 2 // 3, 0, W // 2 + H * 2 // 3, H) if clean else CROP_WIDE
        if key.endswith("_view") or key == "00_surface":
            rgb.crop(tall).resize((480, 720), Image.LANCZOS).save(
                os.path.join(dst, key + "_tall.jpg"), quality=82, optimize=True, progressive=True)
            SHOTS[key + "_tall"] = key + "_tall.jpg"
        rgb.crop(wide).resize((960, 720), Image.LANCZOS).save(
            os.path.join(dst, key + ".jpg"), quality=82, optimize=True, progressive=True)
        SHOTS[key] = key + ".jpg"


# ---------------------------------------------------------------- boss attack stills
MOVES = set()  # "<boss>_<slug>_<windup|strike>" present in site/public/shots/moves


def _body_box(img, S=4):
    """Box of the boss in a test capture (sky and stone floor are left out; sparse particles do not count)."""
    sm = img.convert("RGB").resize((480, 270), Image.NEAREST)
    px = sm.load()
    gw, gh = -(-480 // S), -(-270 // S)
    fill = [[0] * gw for _ in range(gh)]
    for y in range(270):
        for x in range(480):
            r, g, b = px[x, y]
            sky = b > r + 15 and b > 150 and g > r
            grey = max(r, g, b) - min(r, g, b) < 16 and max(r, g, b) > 70
            if not (sky or grey):
                fill[y // S][x // S] += 1
    on = {(x, y) for y in range(gh) for x in range(gw) if fill[y][x] >= S * S // 2}
    comps, seen = [], set()
    for c in on:
        if c in seen:
            continue
        stack, comp = [c], []
        seen.add(c)
        while stack:
            x, y = stack.pop()
            comp.append((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in on and n not in seen:
                        seen.add(n)
                        stack.append(n)
        comps.append(comp)
    if not comps:
        return None
    comps.sort(key=len, reverse=True)
    keep = [p for c in comps if len(c) >= len(comps[0]) * 0.15 for p in c]
    k = img.width / 480
    xs, ys = [p[0] for p in keep], [p[1] for p in keep]
    return (min(xs) * S * k, min(ys) * S * k, (max(xs) + 1) * S * k, (max(ys) + 1) * S * k)


def process_moves(dst):
    """Wind-up and strike of each attack of the bosses on the site, cropped around the boss (same box for both
    frames, so the swap does not jump), 360x270 WebP. Without the captures (CI) the committed files are kept:
    nothing here ever deletes a file."""
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(dst):
        if f.endswith(".webp"):
            MOVES.add(f[:-5])
    if Image is None or not os.path.isdir(MOVES_SRC):
        return
    for b in C.BOSSES:
        for slug, _seq in boss_moves(b["id"]):
            src = [os.path.join(MOVES_SRC, f"moves_{b['id']}_{slug}_{ph}.png") for ph in ("windup", "strike")]
            if not all(os.path.exists(p) for p in src):
                continue
            ims = [Image.open(p).convert("RGB") for p in src]
            boxes = [x for x in (_body_box(im) for im in ims) if x]
            if not boxes:
                continue
            x0, y0 = min(x[0] for x in boxes), min(x[1] for x in boxes)
            x1, y1 = max(x[2] for x in boxes), max(x[3] for x in boxes)
            W, H = ims[0].size
            h = min(H, max((y1 - y0) * 1.16, (x1 - x0) * 1.16 * 3 / 4, H * 0.3))
            w = h * 4 / 3
            left = min(max(0, (x0 + x1 - w) / 2), W - w)
            top = min(max(0, (y0 + y1 - h) / 2), H - h)
            box = tuple(int(round(v)) for v in (left, top, left + w, top + h))
            for im, ph in zip(ims, ("windup", "strike")):
                key = f"{b['id']}_{slug}_{ph}"
                night = _lacquer_sky(im.crop(box).resize((720, 540), Image.BOX))
                night.resize((360, 270), Image.LANCZOS).save(os.path.join(dst, key + ".webp"), quality=72, method=6)
                MOVES.add(key)


def _lacquer_sky(img):
    """The pale test sky, filled from the top edge (so a blue part of a boss is never touched), becomes the
    dark lacquer of the posters, a little warmer toward the horizon."""
    px = img.load()
    W, H = img.size

    def sky(p):
        r, g, b = p
        return b > r + 12 and b > 130 and g >= r

    seen = bytearray(W * H)
    stack = []
    for x in range(W):
        if sky(px[x, 0]):
            seen[x] = 1
            stack.append((x, 0))
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and sky(px[nx, ny]):
                seen[ny * W + nx] = 1
                stack.append((nx, ny))
    for y in range(H):
        k = y / H
        c = (int(30 + 46 * k), int(17 + 12 * k), int(13 + 8 * k))
        row = y * W
        for x in range(W):
            if seen[row + x]:
                px[x, y] = c
    return img


def move_shot(boss, slug, ph):
    key = f"{boss}_{slug}_{ph}"
    return f"shots/moves/{key}.webp" if key in MOVES else None


# World views picked by eye among the structure photos (media/structures): world -> structure id.
# Worlds missing here wait for frames of the trailer capture (FRAME_PICKS) and show their own block meanwhile.
STRUCT_VIEW = {1: "gatherer_village", 4: "cloud_garden", 6: "reflection_refuge", 7: "diving_bell", 8: "frozen_garden",
               9: "anchored_fort", 10: "city_of_giants"}
# Other pictures of the site, each used once: key -> structure photo.
STRUCT_ART = {"hero": "collapsed_doll", "head_worlds": "impossible_stair", "head_bestiary": "ray_nest", "head_bosses": "creature_throne",
              "head_systems": "solar_observatory", "head_download": "root_temple", "verb_survive": "hanging_ruin", "verb_fight": "stable_sanctuary"}
# Frames picked by eye from the trailer capture (media/trailer/frames): key -> (sequence, frame).
FRAMES = os.path.join(ROOT, "media/trailer/frames")
FRAME_PICKS = {
    "w00_view": ("w00_a", 30), "w02_view": ("w02_d", 40), "w03_view": ("w03_a", 30), "w05_view": ("w05_d", 40),
    "w00_boss": ("w00_c", 100), "w01_boss": ("w01_c", 40), "w02_boss": ("w02_c", 10), "w03_boss": ("w03_c", 10),
    "w04_boss": ("w04_c", 40), "w05_boss": ("w05_c", 40), "w06_boss": ("w06_c", 125), "w07_boss": ("w07_c", 10),
}


def _views(img, key, dst):
    """A 21:9 banner, a 4:3 card and a tall doll-window crop of one picture."""
    W, H = img.size
    bh = int(W * 9 / 21)
    img.crop((0, (H - bh) // 2, W, (H + bh) // 2)).resize((1920, 823), Image.LANCZOS).save(os.path.join(dst, key + "_banner.jpg"), quality=80, optimize=True, progressive=True)
    SHOTS[key + "_banner"] = key + "_banner.jpg"
    cw = H * 4 // 3
    img.crop(((W - cw) // 2, 0, (W + cw) // 2, H)).resize((960, 720), Image.LANCZOS).save(os.path.join(dst, key + ".jpg"), quality=82, optimize=True, progressive=True)
    SHOTS[key] = key + ".jpg"
    tw = H * 2 // 3
    img.crop(((W - tw) // 2, 0, (W + tw) // 2, H)).resize((480, 720), Image.LANCZOS).save(os.path.join(dst, key + "_tall.jpg"), quality=82, optimize=True, progressive=True)
    SHOTS[key + "_tall"] = key + "_tall.jpg"


def process_frames(dst):
    """Each picked frame becomes a 21:9 banner, a 4:3 card and a tall doll-window crop; structure photos become cards."""
    st_dir = os.path.join(ROOT, "media/structures")
    # world views are rebuilt from scratch each run: no stale or doubled capture survives.
    # Only where the sources are present (media/ is not in the repo: CI keeps the committed views)
    if Image is None or not (os.path.isdir(st_dir) and os.path.isdir(FRAMES)):
        return
    for f in os.listdir(dst):
        if re.match(r"(w\d\d_view|00_surface)", f):
            os.remove(os.path.join(dst, f))
            SHOTS.pop(f.rsplit(".", 1)[0], None)
    if Image is not None and os.path.isdir(st_dir):
        for n, sid in STRUCT_VIEW.items():
            src = os.path.join(st_dir, f"struct_{sid}.png")
            if os.path.exists(src):
                _views(Image.open(src).convert("RGB"), f"w{n:02d}_view", dst)
        for key, sid in STRUCT_ART.items():
            src = os.path.join(st_dir, f"struct_{sid}.png")
            if os.path.exists(src):
                _views(Image.open(src).convert("RGB"), key, dst)
        for f in sorted(os.listdir(st_dir)):
            if f.startswith("struct_") and f.endswith(".png"):
                key = "st_" + f[7:-4]
                Image.open(os.path.join(st_dir, f)).convert("RGB").resize((800, 450), Image.LANCZOS).save(
                    os.path.join(dst, key + ".jpg"), quality=80, optimize=True, progressive=True)
                SHOTS[key] = key + ".jpg"
    if Image is None or not os.path.isdir(FRAMES):
        return
    # worlds whose structure photos failed (caves and ceilings): ten different frames of that world instead
    for w in (2, 3, 5):
        takes = ([("d", 0, 71), ("b", 0, 71), ("c", 0, 20)] if w == 2 else [("a", 0, 119), ("d", 0, 71), ("b", 0, 71), ("c", 0, 20)])
        for k, (sid, *_rest) in enumerate(C.STRUCTURES[w]):
            seq, lo, hi = takes[k % len(takes)]
            n = lo + (k // len(takes)) * 25 + 10
            src = os.path.join(FRAMES, f"seq_w{w:02d}_{seq}_{min(n, hi):04d}.png")
            if os.path.exists(src):
                Image.open(src).convert("RGB").resize((800, 450), Image.LANCZOS).save(
                    os.path.join(dst, f"st_{sid}.jpg"), quality=80, optimize=True, progressive=True)
                SHOTS[f"st_{sid}"] = f"st_{sid}.jpg"
    for key, (seq, n) in FRAME_PICKS.items():
        src = os.path.join(FRAMES, f"seq_{seq}_{n:04d}.png")
        if os.path.exists(src):
            _views(Image.open(src).convert("RGB"), key, dst)


def shot(key):
    f = SHOTS.get(key)
    return f"shots/{f}" if f else None


def tex(id_):
    """Public path of the picture of an item or block id: its item texture, the cube of a block, the render of a
    station, or the icon of a vanilla ingredient (None when there is none)."""
    if id_.startswith("minecraft:"):
        return f"vanilla/{id_[10:]}.png" if id_ in VANILLA_TEX else None
    if id_ in STATION_IMG:
        return f"stations/{id_}.png"
    if id_ in CUBE_TEX and id_ not in ITEM_TEX:
        return f"cubes/{id_}.png"
    if id_ in ITEM_TEX:
        return f"items/{id_}.png"
    if id_ in BLOCK_TEX:
        return f"blocks/{id_}.png"
    return None


def fmt(x):
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    s = f"{x:,}" if isinstance(x, int) else f"{x}"
    if LANG == "fr":
        s = s.replace(",", " ").replace(".", ",")
    return s


def pct(x):
    return f"{fmt(x)} %" if LANG == "fr" else f"{fmt(x)}%"


def secs(x):
    return f"{fmt(round(x, 2))} s"


def ing(inputs):
    return [dict(id=i, tex=tex(i), n=n, name=name(i)) for i, n in inputs]


# the Matrix Workbench's grids, read from the file the game reads (tools/patterns.py writes it)
_PATTERNS = os.path.join(ROOT, "src/main/resources/data/matriochka/workbench_patterns.json")
PATTERNS = json.load(open(_PATTERNS)) if os.path.exists(_PATTERNS) else {}


def grid(out_id, station):
    """The nine cells of a workbench recipe ({id, tex, name, n} or None), or None for the other stations."""
    if station != "matrix_workbench" or out_id not in PATTERNS:
        return None
    return [dict(id=c[0], tex=tex(c[0]), name=name(c[0]), n=c[1]) if c else None for c in PATTERNS[out_id]]


def rec(r):
    return dict(out=r["out"], tex=tex(r["out"]), name=name(r["out"]), count=r["count"], inputs=ing(r["inputs"]))


# ---------------------------------------------------------------- world copy (numbers from rules/WorldRules.java)
RULE_SHORT = {
    0: ("Iron is the ceiling. Find the Guardian.", "Le fer comme plafond. Trouve le Gardien."),
    1: ("The air poisons you. Water washes it off.", "L'air t'empoisonne. L'eau te lave."),
    2: ("Lava and depth cook you slowly.", "La lave et la profondeur te cuisent lentement."),
    3: ("No sky, only halls. And the halls move.", "Pas de ciel, que des salles. Et elles bougent."),
    4: ("Gusts throw you off the islands.", "Les rafales te jettent hors des îles."),
    5: ("Total darkness. Every step makes noise, every light you bring dies.", "Le noir complet. Chaque pas fait du bruit, chaque lumière apportée s'éteint."),
    6: ("Up becomes down, one column at a time.", "Le haut devient le bas, une colonne à la fois."),
    7: ("A world under water. Breathe through your helmet.", "Un monde sous l'eau. Respire par ton casque."),
    8: ("A day lasts eight minutes. A season, two.", "Une journée dure huit minutes. Une saison, deux."),
    9: ("Every minute, the ground moves under you.", "Toutes les minutes, le sol bouge sous tes pieds."),
    10: ("Every old rule, in a workshop built for giants.", "Toutes les anciennes règles, dans un atelier de géants."),
}

RULE_LONG = {
    0: ("You wake up on the Surface with the Artisan's Scroll and a sketched map. Progression stops at iron until you "
        "earn more: enchanting, anvils and the Nether answer only once World 2 is done, the End once World 8 is. The "
        "Guardian's Sanctuary waits a few hundred blocks from spawn. Use its altar to wake the Block Guardian.",
        "Tu te réveilles sur la Surface avec le Parchemin de l'artisan et une carte esquissée. La progression s'arrête "
        "au fer tant que tu n'as rien prouvé : enchantements, enclumes et Nether ne répondent qu'après le monde 2, l'End "
        "après le monde 8. Le Sanctuaire du Gardien t'attend à quelques centaines de blocs du point de départ. Active son "
        "autel pour réveiller le Gardien du bloc."),
    1: ("A toxin gauge rises by 1 every second you breathe the jungle air and falls by 2 in water or rain. At 50 you "
        "slow down, at 75 you weaken, at 100 it eats your health. A Filter Mask halves the gain, Root Broth halves it "
        "again for five minutes, and an Antidote takes 50 off at once.",
        "Une jauge de toxine monte de 1 par seconde tant que tu respires l'air de la jungle, et baisse de 2 dans l'eau "
        "ou sous la pluie. À 50 tu ralentis, à 75 tu t'affaiblis, à 100 elle ronge ta vie. Le Masque filtrant divise la "
        "montée par deux, la Bouillie de racines encore par deux pendant cinq minutes, et un Antidote retire 50 d'un coup."),
    2: ("Heat climbs by 1 per second within three blocks of lava and by 0.5 below y 40. Higher up and away from lava "
        "it drops by 1, in water by 2. Past 50 you get hungry, past 75 your pickaxe drags, at 100 you burn. Each piece "
        "of the Thermal set cuts the gain by 12.5%, Cooling Water takes 50 off, Ice Bread slows it for five minutes.",
        "La chaleur monte de 1 par seconde à moins de trois blocs de la lave, et de 0,5 sous y 40. Plus haut et loin de "
        "la lave, elle redescend de 1, de 2 dans l'eau. Au-delà de 50 tu as faim, de 75 ta pioche traîne, à 100 tu "
        "brûles. Chaque pièce de l'ensemble thermique réduit la montée de 12,5 %, l'Eau de refroidissement retire 50, "
        "le Pain de glace la freine pendant cinq minutes."),
    3: ("There is no surface and no sky, only dungeon. Sealed doors give way to Dungeon Keys, made at the Jailer's "
        "Table once you have reproduced the lock pattern. Every five minutes the halls rearrange themselves: 8 x 8 "
        "sections 16 to 40 blocks from you swap places or turn, and dust falls on them ten seconds before. Rooms, locks, "
        "chests and anything you built never move. Light is scarce, so bring your own.",
        "Ici, ni surface ni ciel : rien que le donjon. Les portes scellées cèdent aux Clés de donjon, fabriquées à la "
        "Table du Geôlier une fois le motif de la serrure reproduit. Toutes les cinq minutes, les salles se "
        "réorganisent : des sections de 8 x 8 situées entre 16 et 40 blocs de toi échangent leur place ou pivotent, et "
        "de la poussière tombe sur elles dix secondes avant. Les salles fermées, les serrures, les coffres et tout ce "
        "que tu as construit ne bougent jamais. La lumière est rare : apporte la tienne."),
    4: ("Floating islands under a permanent storm. Every 30 seconds a gust hits anyone under the open sky unless they "
        "crouch or take shelter, and you hear it two seconds early. Every 45 seconds lightning marks a spot near exposed "
        "players with sparks, then strikes three seconds later. Elytra stay grounded here until the Master of Seasons "
        "falls: the Glider and the Grappling Hook are how you cross.",
        "Des îles flottantes sous un orage permanent. Toutes les 30 secondes, une rafale frappe quiconque se tient à ciel "
        "ouvert, sauf accroupi ou à l'abri, et tu l'entends arriver deux secondes avant. Toutes les 45 secondes, la "
        "foudre marque un point près des joueurs exposés par des étincelles, puis tombe trois secondes plus tard. Les "
        "élytres restent clouées au sol tant que le Maître des saisons n'est pas tombé : on traverse en Planeur et au "
        "Grappin."),
    5: ("No light, and a noise gauge. Every light you place burns out after a minute: torches crumble to sticks, "
        "campfires and candles are snuffed, glowing blocks turn to Spent Glow. Only the Deep's own Faint Glow lasts, and "
        "a lit Solar Lantern carries twenty minutes of light with you. Sprinting adds 4 noise per second, walking 0.6; "
        "standing still removes 1.5, sneaking 3. Above 50, every creature within 28 blocks comes for you. Silence Balm "
        "wipes your noise.",
        "Aucune lumière, et une jauge de bruit. Chaque lumière que tu poses s'éteint au bout d'une minute : les torches "
        "tombent en bâtons, les feux de camp et les bougies s'étouffent, les blocs lumineux deviennent de la Lueur "
        "éteinte. Seule la Lueur faible des profondeurs dure, et une Lanterne solaire allumée emporte vingt minutes de "
        "lumière avec toi. Courir ajoute 4 de bruit par seconde, marcher 0,6 ; rester immobile retire 1,5, s'accroupir "
        "3. Au-dessus de 50, toutes les créatures à moins de 28 blocs viennent te chercher. Le Baume de silence efface "
        "ton bruit."),
    6: ("The realm is cut into 32 x 32 columns, and about a third of them are upside down. Inside one, gravity points "
        "up: you, the creatures and the items fall toward the sky and walk on ceilings, up to 16 blocks above the "
        "ground. Purple sparks trace the borders. Every 90 seconds the pattern changes, five seconds after a warning; if "
        "your column turns back you drift down slowly. Gravity Boots ignore the flips entirely; a Stabilizer or a "
        "Flipped Apple keeps you steady for 30 seconds.",
        "Le royaume est découpé en colonnes de 32 x 32, et environ un tiers d'entre elles sont à l'envers. À "
        "l'intérieur, la gravité pointe vers le haut : toi, les créatures et les objets tombez vers le ciel et marchez "
        "au plafond, jusqu'à 16 blocs au-dessus du sol. Des étincelles violettes dessinent les frontières. Toutes les 90 "
        "secondes, la carte change, cinq secondes après un avertissement ; si ta colonne se retourne, tu redescends "
        "lentement. Les Bottes de gravité ignorent les inversions ; un Stabilisateur ou une Pomme retournée te gardent "
        "stable 30 secondes."),
    7: ("The whole world is sea, up to y 240, with no dry land. You arrive in a diving chamber on the sea floor. "
        "Without a helmet your breath lasts about half a minute under water; a snorkel helmet, one for each ore of the "
        "world, breathes for you from a tank of 3 to 12 minutes that refills in air pockets, bubble columns, over Air "
        "Vents, with an Oxygen Capsule or at the Abyssal Press. The helmets are fragile: hits wear them fast. Below "
        "y 110 the pressure crushes you; each Diving piece and a better helmet let you dive deeper.",
        "Le monde entier est une mer, jusqu'à y 240, sans terre ferme. Tu arrives dans une chambre de plongée sur le "
        "fond. Sans casque, ton souffle tient environ une demi-minute sous l'eau ; un casque-tuba, un par minerai du "
        "monde, respire pour toi grâce à une réserve de 3 à 12 minutes qui se remplit dans les poches d'air, les "
        "colonnes de bulles, au-dessus des Évents d'air, avec une Capsule d'oxygène ou à la Presse abyssale. Les casques sont "
        "fragiles : les coups les usent vite. Sous y 110, la pression t'écrase ; chaque pièce de scaphandre et un "
        "meilleur casque te laissent descendre plus bas."),
    8: ("Time runs two and a half times faster: a full day and night take eight minutes, each season two. Summer leaves you "
        "hungry, winter slows you down, spring and autumn are your windows. A Season Preserve shields you for two "
        "minutes, the Hourglass holds the clock for 90 seconds, and the Time Workshop only accepts recipes at dawn and "
        "dusk.",
        "Le temps passe deux fois et demie plus vite : un jour et une nuit tiennent en huit minutes, chaque saison en deux. "
        "L'été te creuse l'estomac, l'hiver te ralentit, le printemps et l'automne sont tes fenêtres. Une Conserve de "
        "saison te protège deux minutes, le Sablier retient l'horloge 90 secondes, et l'Atelier du temps n'accepte de "
        "recettes qu'à l'aube et au crépuscule."),
    9: ("Every 60 seconds the ground heaves: around you, up to three 16 x 16 zones rise, sink, slide sideways or close "
        "their chasms, and everything on them rides along, you and your builds included. You get three seconds of "
        "warning and are never buried. Within 16 blocks of a Terrain Anchor nothing moves; an Anchor holds the ground "
        "within 4 blocks of you for ten minutes, and Grip Boots hold the zone under your feet.",
        "Toutes les 60 secondes, le sol se soulève : autour de toi, jusqu'à trois zones de 16 x 16 montent, "
        "s'enfoncent, glissent de côté ou referment leurs gouffres, et tout ce qui s'y trouve suit le mouvement, toi et "
        "tes constructions compris. Tu as trois secondes de préavis et tu n'es jamais enseveli. À moins de 16 blocs "
        "d'une Ancre de terrain, rien ne bouge ; une Ancre retient le sol à moins de 4 blocs de toi pendant dix "
        "minutes, et les Bottes d'accroche retiennent la zone sous tes pieds."),
    10: ("You step out of the last block into the Artisan's workshop, seen by a doll: spools, nails, pins and thimbles "
         "many times your height lie on the felt, and on the Titanic Workbench stands the Maquette, a quarter-scale model "
         "of your own base. The world is cut into nine zones of 256 blocks, each running the rule of one earlier world, "
         "from toxin to moving ground. Every piece of old gear earns its place again.",
         "Tu sors du dernier bloc dans l'atelier de l'artisan, vu par une poupée : bobines, clous, épingles et dés à "
         "coudre bien plus hauts que toi jonchent le feutre, et sur l'Établi titanesque trône la Maquette, ta propre "
         "base au quart de sa taille. Le monde est découpé en neuf zones de 256 blocs, chacune rejouant la règle d'un "
         "monde précédent, de la toxine au sol mouvant. Chaque ancien équipement retrouve sa place."),
}

TIER = {"learning": ("Learning", "Apprentissage"), "mastery": ("Mastery", "Maîtrise"),
        "expertise": ("Expertise", "Expertise"), "final": ("Final exam", "Examen final")}

ROLE = {"combat": ("Combat", "Combat"), "exploration": ("Exploration and loot", "Exploration et butin"),
        "story": ("Story", "Histoire"), "utility": ("Utility", "Utilité"), "secret": ("Secret", "Secret")}

STATION_OF = {w: sid for (sid, en, fr, w, nen, nfr) in C.STATIONS if w > 0}
STATION_NOTE = {sid: (nen, nfr) for (sid, en, fr, w, nen, nfr) in C.STATIONS}
BOSS_OF = {b["world"]: b for b in C.BOSSES}
MOBS_OF = {}
for _m in C.MOBS:
    MOBS_OF.setdefault(_m["world"], []).append(_m)

PAGES = ["index", "worlds", "bestiary", "bosses", "systems", "download"]
NAV = {"index": ("Home", "Accueil"), "worlds": ("Worlds", "Mondes"), "bestiary": ("Bestiary", "Bestiaire"),
       "bosses": ("Bosses", "Boss"), "items": ("Items", "Objets"), "systems": ("Systems", "Systèmes"), "download": ("Download", "Télécharger")}




# ---------------------------------------------------------------- palette (lacquer, gold leaf, the doll's face)
RED, RED_B, BLACK, GOLD, GOLD_B, PAPER = "#5E1E1A", "#A33A2A", "#17100D", "#D9A441", "#F0C960", "#F3E2C2"


def light(n):
    """The signature colour of a world (0 = Surface)."""
    if n == 0:
        return GOLD
    pal = C.WORLDS[n - 1]["pal"]
    return "#" + pal[{6: 0, 8: 2, 10: 1}.get(n, 2)]


def _doll_colours(n):
    """Body, scarf and apron flower of a world's doll, from the palette in content.py."""
    if n == 0:
        return RED_B, BLACK, RED_B
    p = C.WORLDS[n - 1]["pal"]
    pick = {1: (0, 3, 2), 2: (1, 3, 0), 3: (0, 3, 2), 4: (1, 3, 2), 5: (1, 3, 2), 6: (0, 3, 1),
            7: (0, 3, 1), 8: (1, 3, 0), 9: (1, 3, 0), 10: (2, 3, 1)}[n]
    return tuple("#" + p[i] for i in pick)


def _mix(a, b, k):
    ca = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * k):02x}" for x, y in zip(ca, cb))


def world_bg(n):
    """Lacquer red stained by a world's darkest colour: the page shifts as you go down the worlds."""
    return RED if n == 0 else _mix(RED, "#" + C.WORLDS[n - 1]["pal"][3], 0.42)


WORLD_BLOCK = {0: "painted_wood", 1: "spore_moss", 2: "ashrock", 3: "dungeon_brick", 4: "cloudstone", 5: "umbral_stone",
               6: "inverted_stone", 7: "trench_rock", 8: "hourstone", 9: "living_rock", 10: "giant_plank"}

# The figures of each rule, restated from RULE_LONG (rules/WorldRules.java).
RULE_NUMS = {
    0: [("2", "2", "worlds before enchanting, anvils and the Nether", "mondes avant enchantements, enclumes et Nether"),
        ("8", "8", "worlds before the End", "mondes avant l'End")],
    1: [("+1/s", "+1/s", "toxin while you breathe the air", "de toxine tant que tu respires l'air"),
        ("−2/s", "−2/s", "in water or under rain", "dans l'eau ou sous la pluie"),
        ("100", "100", "toxin, and it eats your health", "de toxine, et elle ronge ta vie")],
    2: [("+1/s", "+1/s", "heat within 3 blocks of lava", "de chaleur à moins de 3 blocs de la lave"),
        ("+0.5/s", "+0,5/s", "heat below y 40", "de chaleur sous y 40"),
        ("−12.5%", "−12,5 %", "heat gain per Thermal piece", "de montée par pièce thermique")],
    3: [("5 min", "5 min", "between two rearrangements of the halls", "entre deux réorganisations des salles"),
        ("10 s", "10 s", "of warning, dust on the moving halls", "de préavis, la poussière sur les salles qui bougent"),
        ("16-40", "16-40", "blocks from you: where the halls move", "blocs de toi : là où les salles bougent")],
    4: [("30 s", "30 s", "between two gusts", "entre deux rafales"),
        ("45 s", "45 s", "between two lightning strikes", "entre deux éclairs"),
        ("3 s", "3 s", "from the sparks to the strike", "entre les étincelles et l'impact")],
    5: [("60 s", "60 s", "before a brought light burns out", "avant qu'une lumière apportée s'éteigne"),
        ("50", "50", "noise, and everything comes for you", "de bruit, et tout vient te chercher"),
        ("20 min", "20 min", "of light carried by the Solar Lantern", "de lumière portée par la Lanterne solaire")],
    6: [("90 s", "90 s", "between two changes of the gravity columns", "entre deux changements des colonnes de gravité"),
        ("32", "32", "blocks per column", "blocs par colonne"),
        ("16", "16", "blocks: how high a flipped column pulls", "blocs : la hauteur où tire une colonne inversée")],
    7: [("33 s", "33 s", "of breath without a helmet", "de souffle sans casque"),
        ("12 min", "12 min", "of air in a Pearl Snorkel Helmet", "d'air dans un Casque-tuba de perle"),
        ("y 110", "y 110", "where the pressure starts", "où commence la pression")],
    8: [("×3", "×3", "the speed of time", "la vitesse du temps"),
        ("8 min", "8 min", "a day and a night", "un jour et une nuit"),
        ("2 min", "2 min", "a season", "une saison")],
    9: [("60 s", "60 s", "between two heaves", "entre deux secousses"),
        ("16", "16", "blocks of calm around a Terrain Anchor", "blocs de calme autour d'une Ancre de terrain"),
        ("16 × 16", "16 × 16", "blocks per moving zone", "blocs par zone qui bouge")],
    10: [("9", "9", "zones, each with an earlier rule", "zones, chacune avec une ancienne règle"),
         ("256", "256", "blocks per zone", "blocs par zone")],
}

# What each behaviour key really does, read from entity/MatrioMob.java (customServerAiStep, hurtServer,
# doHurtTarget, die). Ticks are converted at 20 per second.
BEHAVIOUR = {
    "melee": ("A plain melee fighter: it walks up to you and strikes.",
              "Un combattant au corps à corps : il s'approche et frappe."),
    "melee_reach": ("A melee fighter with no extra trick: everything is in its health and damage.",
                    "Un combattant au corps à corps sans autre ruse : tout est dans sa vie et ses dégâts."),
    "swarm": ("Quick on its feet and spawns in packs of two to four.",
              "Rapide, il apparaît en meutes de deux à quatre."),
    "swarm_toxin": ("Quick on its feet, spawns in packs of two to four, and every hit that lands adds 5 to your toxin gauge.",
                    "Rapide, il apparaît en meutes de deux à quatre, et chaque coup qui porte ajoute 5 à ta jauge de toxine."),
    "ambush_root": ("Lies invisible and motionless until a player comes within 3.5 blocks, or hits it. When it springs, the player is pinned by Slowness VI for 3 seconds.",
                    "Reste invisible et immobile jusqu'à ce qu'un joueur approche à moins de 3,5 blocs, ou le frappe. Quand il surgit, le joueur est cloué par une Lenteur VI pendant 3 secondes."),
    "mimic": ("Stays invisible and never walks. It wakes when a player comes within 3.5 blocks or hits it, then strikes anyone in reach. Revealing one in World 3 earns It Won't Open.",
              "Reste invisible et ne marche jamais. Il s'éveille quand un joueur approche à moins de 3,5 blocs ou le frappe, puis frappe tout ce qui passe à portée. En démasquer un dans le monde 3 rapporte Ça ne s'ouvre pas."),
    "puller": ("Rooted in place and never strikes in melee. Every 3 seconds, if you are within 14 blocks and in its line of sight, it yanks you toward it. Getting snared ten times earns Friend of Flowers.",
               "Enraciné, il ne frappe jamais au corps à corps. Toutes les 3 secondes, si tu es à moins de 14 blocs et dans sa ligne de vue, il te tire vers lui. Te faire attraper dix fois rapporte Ami des fleurs."),
    "harpoon": ("Fights in melee, and every 3 seconds, within 14 blocks and in line of sight, it harpoons you toward it with a stronger pull than a Snare Flower.",
                "Combat au corps à corps et, toutes les 3 secondes, à moins de 14 blocs et en ligne de vue, il te harponne vers lui avec une traction plus forte que celle d'une fleur-piège."),
    "flee_cloud": ("Keeps its distance: when you come within 5 blocks it backs away. Every 2.5 seconds it leaves a poison cloud 2.5 blocks wide that lasts 5 seconds.",
                   "Garde ses distances : à moins de 5 blocs, il recule. Toutes les 2,5 secondes, il laisse un nuage de poison de 2,5 blocs de rayon qui dure 5 secondes."),
    "digger": ("Tunnels toward you: every 1.5 seconds, while you are more than 2 blocks away, it breaks the two blocks in front of it if they are soft (hardness under 3).",
               "Creuse vers toi : toutes les 1,5 seconde, tant que tu es à plus de 2 blocs, il casse les deux blocs devant lui s'ils sont tendres (dureté inférieure à 3)."),
    "charger": ("Every 4 seconds, within 16 blocks, it dashes at you in a burst of flame.",
                "Toutes les 4 secondes, à moins de 16 blocs, il fonce sur toi dans une gerbe de flammes."),
    "charger_cage": ("Dashes at you every 4 seconds within 16 blocks, and every 10 seconds, if you are within 3 blocks, it locks you in a cage of iron bars.",
                     "Fonce sur toi toutes les 4 secondes à moins de 16 blocs et, toutes les 10 secondes, si tu es à moins de 3 blocs, t'enferme dans une cage de barreaux de fer."),
    "caller": ("Every 10 seconds it rings out: every Matriochka creature within 24 blocks that has no target turns on you.",
               "Toutes les 10 secondes, il sonne l'alerte : chaque créature de Matriochka à moins de 24 blocs sans cible se tourne vers toi."),
    "chain_ranged": ("Every 2.5 seconds, within 20 blocks and in line of sight, it lashes you with a chain for 60% of its damage and Slowness III for 2 seconds.",
                     "Toutes les 2,5 secondes, à moins de 20 blocs et en ligne de vue, il te fouette d'une chaîne pour 60 % de ses dégâts et une Lenteur III de 2 secondes."),
    "flyer_push": ("Flies about 4 blocks above you and swoops in. Within 2 blocks it strikes once a second and throws you back hard.",
                   "Vole à environ 4 blocs au-dessus de toi et fond sur toi. À moins de 2 blocs, il frappe une fois par seconde et te projette violemment."),
    "diver": ("Hovers about 4 blocks above you and dives down for one second out of every five. Within 2 blocks it strikes once a second.",
              "Plane à environ 4 blocs au-dessus de toi et plonge une seconde sur cinq. À moins de 2 blocs, il frappe une fois par seconde."),
    "exploder": ("Drifts straight at you and explodes once it is about 2.4 blocks away, destroying itself. The blast hurts but breaks no blocks.",
                 "Dérive droit vers toi et explose à environ 2,4 blocs, en se détruisant. L'explosion blesse mais ne casse aucun bloc."),
    "gravity_orb": ("Floats toward a point 2 blocks above you. When it dies, every player within 6 blocks levitates for 3 seconds and earns Ceiling Walk.",
                    "Flotte vers un point à 2 blocs au-dessus de toi. À sa mort, chaque joueur à moins de 6 blocs lévite pendant 3 secondes et obtient Marcher au plafond."),
    "area_slam": ("Every 4.5 seconds, if you are within 6 blocks, it slams the ground: full damage to everything within 4 blocks, thrown into the air.",
                  "Toutes les 4,5 secondes, si tu es à moins de 6 blocs, il frappe le sol : dégâts complets à tout ce qui est à moins de 4 blocs, projeté en l'air."),
    "light_eater": ("Every 2 seconds it snuffs out torches and lanterns within 4 blocks, and blinds you with Darkness for 5 seconds if you are within 8 blocks.",
                    "Toutes les 2 secondes, il éteint torches et lanternes à moins de 4 blocs, et t'aveugle d'Obscurité pendant 5 secondes si tu es à moins de 8 blocs."),
    "lurer": ("Every 6 seconds, within 24 blocks, it cries out with the voice of a hurt player. Following it to within 4 blocks earns It Was You.",
              "Toutes les 6 secondes, à moins de 24 blocs, il pousse le cri d'un joueur blessé. Le suivre à moins de 4 blocs rapporte C'était toi."),
    "statue": ("Does not walk. While you stand still or sneak it freezes; when you move within 2 blocks of it, it strikes once a second.",
               "Ne marche pas. Tant que tu restes immobile ou accroupi, il se fige ; si tu bouges à moins de 2 blocs, il frappe une fois par seconde."),
    "pressure_aura": ("Its pressure reaches 7 blocks: every second there it gives Slowness II and Mining Fatigue II and takes 2 of your breath.",
                      "Sa pression porte à 7 blocs : chaque seconde passée là donne Lenteur II et Fatigue de minage II, et retire 2 de souffle."),
    "slowing_aura": ("Its aura reaches 7 blocks: every second there gives Slowness II and Mining Fatigue II.",
                     "Son aura porte à 7 blocs : chaque seconde passée là donne Lenteur II et Fatigue de minage II."),
    "swimmer": ("In water it homes in on you and keeps facing you as it swims.",
                "Dans l'eau, il fond sur toi et nage sans te quitter des yeux."),
    "swimmer_oxygen": ("A quick swimmer that homes in on you, and within 3 blocks it drains 3 of your breath every second.",
                       "Un nageur rapide qui fond sur toi et, à moins de 3 blocs, te retire 3 de souffle par seconde."),
    "grabber": ("Every 3.5 seconds, if you are within about 2.4 blocks, it grabs you: Slowness VII for 2.5 seconds and Wither for 2 seconds.",
                "Toutes les 3,5 secondes, si tu es à environ 2,4 blocs, il t'agrippe : Lenteur VII pendant 2,5 secondes et Flétrissement pendant 2 secondes."),
    "grower": ("Grows while it fights: every 5 seconds it gains a tenth of its size, up to 1.8 times, and 8% damage each time. Letting it reach full size earns Grandpa.",
               "Grandit en combattant : toutes les 5 secondes, il prend un dixième de sa taille, jusqu'à 1,8 fois, et 8 % de dégâts à chaque fois. Le laisser atteindre sa taille adulte rapporte Grand-père."),
    "block_eater": ("Every 1.25 seconds it eats the block beneath it (hardness under 5), unless a Terrain Anchor stands within 6 blocks.",
                    "Toutes les 1,25 seconde, il dévore le bloc sous lui (dureté inférieure à 5), sauf si une Ancre de terrain se trouve à moins de 6 blocs."),
    "splitter": ("When it dies it bursts into three Sporelings.",
                 "À sa mort, il éclate en trois Sporelins."),
    "seasonal": ("Every 5 seconds, within 5 blocks, it inflicts the ailment of the season for 4 seconds at level II: poison, then weakness, slowness and hunger, changing every 2 minutes.",
                 "Toutes les 5 secondes, à moins de 5 blocs, il inflige le mal de la saison pendant 4 secondes au niveau II : poison, puis faiblesse, lenteur et faim, qui changent toutes les 2 minutes."),
    "cycle": ("Every 5 seconds, within 5 blocks, it inflicts the ailment of the current cycle for 4 seconds at level II: poison, then weakness, slowness and hunger, changing every 2 minutes.",
              "Toutes les 5 secondes, à moins de 5 blocs, il inflige le mal du cycle en cours pendant 4 secondes au niveau II : poison, puis faiblesse, lenteur et faim, qui changent toutes les 2 minutes."),
    "wall_crawler": ("Climbs straight up any wall it runs into.",
                     "Escalade tout mur qu'il rencontre."),
    "sound_hunter": ("Hunts by sound: it never picks a player who is sneaking as its target.",
                     "Chasse au son : il ne choisit jamais pour cible un joueur accroupi."),
    "shielded": ("Hits that come from in front of it deal only a quarter of their damage. Go around it.",
                 "Les coups portés de face ne font qu'un quart de leurs dégâts. Contourne-le."),
    "hardening": ("Takes 40% less damage unless it is burning or standing in lava.",
                  "Subit 40 % de dégâts en moins, sauf s'il brûle ou se tient dans la lave."),
    "reflect": ("Sends 30% of the damage it takes back to its attacker.",
                "Renvoie 30 % des dégâts reçus à son agresseur."),
    "copycat": ("Copies your strength: its damage rises to match the hardest hit it has taken.",
                "Copie ta force : ses dégâts montent jusqu'au plus gros coup qu'il a reçu."),
    "lava_heat": ("Every hit that lands adds 6 to your heat gauge, and fire does not hurt it.",
                  "Chaque coup qui porte ajoute 6 à ta jauge de chaleur, et le feu ne le blesse pas."),
}

SPEED = {"puller": 0.0, "statue": 0.0, "mimic": 0.0, "swarm": 0.33, "swarm_toxin": 0.33, "swimmer_oxygen": 0.33,
         "lurer": 0.33, "flee_cloud": 0.30, "charger": 0.30, "sound_hunter": 0.30}

# Achievements granted by a creature's own mechanic (MatrioMob.java) or named after a boss fight.
CUSTOM_ACH = {"puller": ["snared"], "mimic": ["key_on_lock"], "lurer": ["lured"], "grower": ["child_old"], "gravity_orb": ["flipped"]}
BOSS_ACH = {"spore_queen": ["queen_no_mask"], "ash_titan": ["titan_no_lava"], "storm_king": ["king_no_bolt"],
            "light_eater": ["eater_no_light"], "your_double": ["double_swap"], "pressure_leviathan": ["levi_low_o2"],
            "seasons_master": ["master_four"], "terrain_heart_boss": ["heart_no_anchor"], "the_unfinished": ["ten_shells"]}

STRUCTURE_OF_ROLE = ROLE


def spawns():
    """Natural spawn entries per world, read from the generated biome files."""
    out = {}
    for n in range(1, 11):
        p = os.path.join(BIOMES, f"world_{n}.json")
        if not os.path.exists(p):
            continue
        bio = json.load(open(p, encoding="utf-8"))
        cats = bio["attributes"]["minecraft:gameplay/natural_mob_spawns"]["argument"]["spawns_by_category"]
        mons = cats.get("monster", [])
        total = sum(s["weight"] for s in mons)
        for s in mons:
            c = s["count"]
            lo, hi = (c, c) if isinstance(c, int) else (c["min_inclusive"], c["max_inclusive"])
            out[s["type"].split(":")[1]] = dict(world=n, weight=s["weight"], total=total, min=lo, max=hi)
    return out


SPAWNS = spawns()


def speed_mult(w):
    return 1.0 if w <= 0 else 1 + 0.06 * (w - 1)


def ach_list(pred):
    out = []
    for w, lst in C.ACH.items():
        for a in lst:
            if pred(a):
                cat = {"progress": t("Progress", "Progression"), "explore": t("Exploration", "Exploration"),
                       "combat": t("Combat", "Combat"), "hidden": t("Hidden", "Caché")}[a[0]]
                out.append(dict(world=w, cat=cat, hidden=a[0] == "hidden", name=a[1] if LANG == "en" else a[2],
                                desc=a[3] if LANG == "en" else a[4]))
    return out


def quest_list(mid):
    out = []
    for q in C.QUESTS:
        if q[3][0] == "kill" and q[3][1] == mid:
            out.append(dict(world=q[1], name=q[4] if LANG == "en" else q[5], desc=q[6] if LANG == "en" else q[7],
                            count=q[3][2]))
    return out


def doll(n):
    b, s, o = _doll_colours(n)
    return dict(body=b, scarf=s, orn=o)


def tier_ticks(world):
    tele = 30 if world <= 3 else 20 if world <= 6 else 15 if world <= 9 else 12
    opening = 60 if world <= 3 else 50 if world <= 6 else 40 if world <= 9 else 30
    return tele, opening


# ---------------------------------------------------------------- data builders
def build_worlds():
    out = []
    surface_recipes = [r for r in RECIPES.get("matrix_workbench", []) if r["out"] in ("class_table", "soul_altar", "soul_cradle", "return_thread", "chance_doll", "spore_vat")]
    for n in range(0, 11):
        w = C.WORLDS[n - 1] if n else None
        boss = BOSS_OF[n]
        d = dict(n=n, name=world_name(n), short=t(*RULE_SHORT[n]), long=t(*RULE_LONG[n]),
                 nums=[dict(v=(a if LANG == "en" else b), l=(c if LANG == "en" else dd)) for a, b, c, dd in RULE_NUMS[n]],
                 doll=doll(n), light=light(n), bg=world_bg(n), block=f"blocks/{WORLD_BLOCK[n]}.png",
                 tall=shot(f"w{n:02d}_view_tall"),
                 banner=shot(f"w{n:02d}_view_banner"), hud=shot(f"gui_hud_w{n}"),
                 wide=None if n == 0 else shot(f"w{n:02d}_view"),
                 boss=dict(id=boss["id"], name=boss[LANG], hp=fmt(boss["hp"]), core=boss["core"], coreTex=tex(boss["core"]), coreName=name(boss["core"])),
                 mobs=[dict(id=m["id"], name=name(m["id"]), elite=m["elite"], tex=tex(m["drop"])) for m in MOBS_OF.get(n, [])])
        if n == 0:
            d.update(rule=None, tier=t("Where it starts", "Là où tout commence"), seed=None, station=None,
                     surface=[rec(r) for r in surface_recipes],
                     bossNote=t("It drops the Guardian Core, the Matrix Workbench and four World Soil 0. Your Scroll becomes the Artisan's Journal.",
                                "Il laisse le Noyau du Gardien, l'Établi matriciel et quatre Terres de monde 0. Ton Parchemin devient le Journal de l'artisan."),
                     items=[], armor=None, structures=[], codex=codex(0))
            out.append(d)
            continue
        st, seed = recipe_for(f"seed_{n}")
        station = STATION_OF[n]
        st_make = recipe_for(station)[1]
        items = [it for it in C.ITEMS if it["world"] == n and it["kind"] not in ("armorset", "seed", "secret", "core", "food")]
        item_list = [dict(id=it["id"], tex=tex(it["id"]), name=name(it["id"]), effect=it["effect_" + LANG]) for it in items]
        food = next((f for f in C.FOODS if f[3] == n), None)
        if food:
            item_list.append(dict(id=food[0], tex=tex(food[0]), name=name(food[0]), effect=food[4] if LANG == "en" else food[5]))
        armor = next((it for it in C.ITEMS if it["world"] == n and it["kind"] == "armorset"), None)
        armor_d = None
        if armor:
            gw = C.GEAR[n]
            armor_d = dict(pieces=[dict(tex=tex(f'{armor["id"]}_{p}'), name=name(f'{armor["id"]}_{p}')) for p in armor.get("pieces", PIECES)],
                           text=(t(f"{gw[1]} armour, {gw[2]} toughness, a {gw[0]}-damage weapon at this tier.",
                                   f"{gw[1]} d’armure, {gw[2]} de robustesse, une arme à {gw[0]} de dégâts à ce palier.")
                                 if "helmet" in armor.get("pieces", PIECES) else
                                 t(f"Three pieces and no helmet: the head slot belongs to the snorkel helmets. A {gw[0]}-damage weapon at this tier.",
                                   f"Trois pièces et pas de casque : la tête revient aux casques-tubas. Une arme à {gw[0]} de dégâts à ce palier."))
                           + ((" " + armor["effect_" + LANG]) if armor.get("effect_" + LANG) else ""))
        structs = {}
        for (sid, en, fr, role, size, rarity, arch) in C.STRUCTURES[n]:
            structs.setdefault(role, []).append(en if LANG == "en" else fr)
        d.update(rule=C.RULES[w["rule"]][LANG], tier=t(*TIER[w["tier"]]),
                 seed=dict(id=f"seed_{n}", tex=tex(f"seed_{n}"), name=name(f"seed_{n}"), grid=grid(f"seed_{n}", "matrix_workbench"),
                           # World 1 grows from its Seed on World Soil; every other world opens with its own rite
                           soil=(t("Plant on tilled World Soil 0.", "Se plante sur une Terre de monde 0 bêchée.") if n == 1
                                 else LANGS[LANG].get(f"item.matriochka.seed_{n}.desc", "")),
                           cond=(LANGS[LANG].get("message.matriochka.seed_planted.1", "") if n == 1 else ""),
                           inputs=ing(seed["inputs"]) if seed else []),
                 station=dict(id=station, tex=tex(station), img=f"stations/{station}.png" if station in STATION_IMG else None, name=name(station), note=t(*STATION_NOTE[station]), shot=shot(f"gui_station_{station}"),
                              make=ing(st_make["inputs"]) if st_make else [], makeGrid=grid(station, "matrix_workbench"),
                              recipes=[rec(r) for r in RECIPES.get(station, [])]),
                 items=item_list, armor=armor_d,
                 structures=[dict(role=t(*ROLE[r]), names=structs[r]) for r in ROLE if r in structs],
                 bossNote=t(f"It drops the {name(boss['core'])}.", f"Il laisse le {name(boss['core'])}."), codex=codex(n),
                 sites=structures_of(n), loot=loot(n))
        out.append(d)
    return out


RARITY = {"common": ("Common", "Commun"), "rare": ("Rare", "Rare"), "epic": ("Epic", "Épique"), "legendary": ("Legendary", "Légendaire"), "none": ("", "")}
STATION_NAME = lambda st: name(st) if st else None  # noqa: E731


def _sources_of(item_id):
    """Where an item comes from: the creatures that drop it, the boss that leaves it."""
    out = []
    for m in C.MOBS:
        if m["drop"] == item_id or m["rare_drop"] == item_id:
            out.append(name(m["id"]))
    for b in C.BOSSES:
        if b["core"] == item_id:
            out.append(name(b["id"]))
    for blk, drop in C.ORE_DROPS.items():
        if drop == item_id:
            out.append(name(blk))
    # what a boss leaves besides its core (entity/MatrioBoss.java): the Guardian the Matrix Workbench, every boss
    # but the last four soils of its world
    for b in C.BOSSES:
        if (item_id == "matrix_workbench" and b["world"] == 0) or (item_id == "world_soil_0" and b["world"] == 0):
            out.append(name(b["id"]))
    return out


# The four armour pieces of a set; a set may have fewer (the Diving suit leaves the head to the snorkel helmets).
PIECES = ("helmet", "chestplate", "leggings", "boots")


# ---------------------------------------------------------------- item stats (the game's own numbers)
# Gear stats follow content/ModContent.java and item/ReplayGear.java from the GEAR table of tools/content.py:
# a world's weapon deals GEAR[w][0] at 1.6 attacks a second; its armour splits GEAR[w][1] points 18/38/28/16 % over
# helmet, chestplate, leggings and boots, with GEAR[w][2] / 4 toughness, 2 % knockback resistance per world and
# GEAR[w][3] extra health split 15/40/30/15 %; tools and weapons last 300 + 180 w uses, armour (20 + 6 w) times
# vanilla's per-piece base. The base stats are shown: a class rolled at crafting raises them.
_ARMOR_BASE = {"helmet": 11, "chestplate": 16, "leggings": 15, "boots": 13}
_HEALTH_SHARE = {"helmet": 0.15, "chestplate": 0.4, "leggings": 0.3, "boots": 0.15}
# the replay gear's own numbers: (damage offset from the world's, attack speed, reach bonus, thrown)
_REPLAY_WEAPON = {"magma_flail": (2, 1.0, 0, False), "key_chain_whip": (-2, 1.8, 2.5, False),
                  "storm_javelin": (-1, 1.4, 0, True), "tide_harpoon": (-2, 1.4, 0, True)}
# what using or eating an item does (item/MatrioItem.java): (EN, FR) lines
_MIN = ("min", "min")
EFFECTS = {
    "antidote": [("Toxin -50", "Toxine -50")],
    "cooling_water": [("Heat -50", "Chaleur -50")],
    "silence_balm": [("Noise -100", "Bruit -100")],
    "oxygen_capsule": [("Fills half a snorkel helmet's tank", "Remplit la moitié du réservoir d'un casque-tuba"), ("Without one: +60 breath", "Sans casque : +60 de souffle")],
    "stabilizer": [("Stable for 30 s", "Stable pendant 30 s")],
    "season_preserve": [("The season holds for 2 min", "La saison tient 2 min")],
    "anchor": [("Anchored for 10 min", "Ancré pendant 10 min")],
    "solar_lantern": [("Night Vision for 20 min", "Vision nocturne pendant 20 min"), ("Cooldown 1 min", "Recharge 1 min")],
    "sonar": [("Reveals creatures within 32 blocks for 8 s", "Révèle les créatures à 32 blocs pendant 8 s"), ("Cooldown 10 s", "Recharge 10 s")],
    "hourglass": [("Lasts 90 s", "Dure 90 s"), ("Cooldown 5 min", "Recharge 5 min")],
    "grappling_hook": [("Cooldown 1.5 s", "Recharge 1,5 s")],
    "thruster": [("Cooldown 0.75 s", "Recharge 0,75 s")],
    "labyrinth_map": [("Cooldown 2 s", "Recharge 2 s")],
    "root_broth": [("Lasts 5 min", "Dure 5 min")],
    "ice_bread": [("Lasts 5 min", "Dure 5 min")],
    "cell_ration": [("Saturation for 2 s", "Saturation pendant 2 s")],
    "cloud_fruit": [("Slow Falling for 3 min", "Chute lente pendant 3 min")],
    "mute_mushroom": [("Silent for 5 min", "Silencieux pendant 5 min")],
    "flipped_apple": [("Lasts 30 s", "Dure 30 s")],
    "apnea_kelp": [("Lasts 5 min", "Dure 5 min"), ("+30 breath", "+30 de souffle")],
    "season_jam": [("Lasts 3 min", "Dure 3 min")],
    "anchor_bread": [("Anchored for 5 min", "Ancré pendant 5 min")],
    "workshop_feast": [("Every world dish's effect for 2 min", "L'effet de chaque plat des mondes pendant 2 min"), ("Slow Falling for 2 min", "Chute lente pendant 2 min")],
}


def _num(x):
    return fmt(round(x, 2))


def item_stats(iid, kind, w, piece=None):
    """[{k, v}] of an item's numbers in the game, or []: gear, snorkels, food and what using an item does."""
    out = []

    def add(en, fr, v):
        out.append(dict(k=t(en, fr), v=v))
    g = C.GEAR.get(max(1, min(10, w))) if hasattr(C, "GEAR") else None
    tool_dur = 300 + 180 * max(1, min(10, w))
    if iid in _REPLAY_WEAPON and g:
        d, spd, reach, thrown = _REPLAY_WEAPON[iid]
        add("Attack damage", "Dégâts", _num(g[0] + d))
        add("Attack speed", "Vitesse d'attaque", _num(spd))
        if reach:
            add("Reach", "Portée", "+" + _num(reach))
        if thrown:
            add("Thrown", "Se lance", t("yes", "oui"))
        add("Durability", "Durabilité", _num(tool_dur))
    elif iid == "quake_pick":
        add("Attack damage", "Dégâts", "3")
        add("Attack speed", "Vitesse d'attaque", "1,1" if LANG == "fr" else "1.1")
        add("Mining speed", "Vitesse de minage", _num(7 + 9 * 0.6))
        add("Mines", "Mine", t("up to netherite blocks", "jusqu'aux blocs de netherite"))
        add("Durability", "Durabilité", _num(300 + 180 * 9))
    elif iid == "drill":
        add("Attack damage", "Dégâts", "2")
        add("Attack speed", "Vitesse d'attaque", "1,2" if LANG == "fr" else "1.2")
        add("Mining speed", "Vitesse de minage", _num(7 + 2 * 0.6))
        add("Mines", "Mine", t("up to iron-tier blocks", "jusqu'aux blocs de niveau fer"))
        add("Durability", "Durabilité", _num(300 + 180 * 2))
    elif iid == "lantern_shield":
        add("Blocks", "Bloque", t("90 % of a hit", "90 % d'un coup"))
        add("Durability", "Durabilité", "560")
    elif iid == "spore_bow":
        add("Durability", "Durabilité", "480")
    elif kind == "weapon" and g:
        add("Attack damage", "Dégâts", _num(g[0]))
        add("Attack speed", "Vitesse d'attaque", "1,6" if LANG == "fr" else "1.6")
        add("Durability", "Durabilité", _num(tool_dur))
    elif kind == "armor" and g and piece in _ARMOR_BASE:
        total = int(g[1])
        h, c, b = round(total * 0.18), round(total * 0.38), round(total * 0.16)
        pts = {"helmet": h, "chestplate": c, "boots": b, "leggings": total - h - c - b}[piece]
        add("Armor", "Armure", _num(pts))
        add("Toughness", "Robustesse", _num(g[2] / 4))
        if w > 0:
            add("Knockback resistance", "Résistance au recul", f"{2 * w} %")
        hp = round(g[3] * _HEALTH_SHARE[piece])
        if hp > 0:
            add("Max health", "Vie max", "+" + _num(hp))
        add("Durability", "Durabilité", _num((20 + 6 * w) * _ARMOR_BASE[piece]))
    elif kind == "snorkel":
        sn = next((x for x in C.SNORKELS if x[0] == iid), None)
        if sn:
            _sid, _en, _fr, _ore, _tier, tank, dur, arm, tough, _wear, depth, *_ = sn
            add("Armor", "Armure", _num(arm))
            if tough:
                add("Toughness", "Robustesse", _num(tough))
            add("Air tank", "Réservoir d'air", t(f"{tank // 60} min", f"{tank // 60} min"))
            add("Durability", "Durabilité", _num(dur * _ARMOR_BASE["helmet"]))
    if kind == "food":
        add("Food", "Nourriture", t("6 (3 shanks)", "6 (3 cuisses)"))
        add("Saturation", "Saturation", _num(6 * 0.8 * 2))
    for en, fr in EFFECTS.get(iid, []):
        out.append(dict(k=t("Effect", "Effet"), v=t(en, fr)))
    return out


def codex(n):
    """Everything a world holds: every item and block, how you get it, its quests and its achievements."""
    items = []
    for it in C.ITEMS:
        if it["world"] != n or it["kind"] == "armorset":
            continue
        st, r = recipe_for(it["id"])
        items.append(dict(id=it["id"], tex=tex(it["id"]), name=name(it["id"]), kind=it["kind"], rarity=t(*RARITY.get(it["rarity"], ("", ""))),
                          effect=it.get("effect_" + LANG, ""), stats=item_stats(it["id"], it["kind"], n), station=STATION_NAME(st), stationTex=tex(st) if st else None, stationId=st, grid=grid(it["id"], st), inputs=ing(r["inputs"]) if r else [],
                          count=r["count"] if r else 1, drops=_sources_of(it["id"])))
    armor = next((it for it in C.ITEMS if it["world"] == n and it["kind"] == "armorset"), None)
    if armor:
        for p in armor.get("pieces", PIECES):
            pid = f'{armor["id"]}_{p}'
            st, r = recipe_for(pid)
            items.append(dict(id=pid, tex=tex(pid), name=name(pid), kind="armor", rarity=t(*RARITY.get(armor["rarity"], ("", ""))),
                              effect=armor.get("effect_" + LANG, ""), stats=item_stats(pid, "armor", n, p), station=STATION_NAME(st), stationTex=tex(st) if st else None, stationId=st, grid=grid(pid, st), inputs=ing(r["inputs"]) if r else [],
                              count=r["count"] if r else 1, drops=[]))
    for f in C.FOODS:
        if f[3] == n and all(x["id"] != f[0] for x in items):
            st, r = recipe_for(f[0])
            items.append(dict(id=f[0], tex=tex(f[0]), name=name(f[0]), kind="food", rarity="", effect=f[4] if LANG == "en" else f[5], stats=item_stats(f[0], "food", n),
                              station=STATION_NAME(st), stationTex=tex(st) if st else None, stationId=st, grid=grid(f[0], st), inputs=ing(r["inputs"]) if r else [], count=r["count"] if r else 1, drops=[]))
    blocks = []
    for b in C.BLOCKS:
        if b["world"] != n:
            continue
        st, r = recipe_for(b["id"])
        blocks.append(dict(id=b["id"], tex=tex(b["id"]) or f"blocks/{b['id']}.png", name=name(b["id"]), kind=b["kind"], effect=b.get("note_" + LANG, ""),
                           stationTex=tex(st) if st else None, stationId=st, grid=grid(b["id"], st),
                           station=STATION_NAME(st), inputs=ing(r["inputs"]) if r else [], count=r["count"] if r else 1,
                           drops=_sources_of(b["id"]), yields=name(C.ORE_DROPS[b["id"]]) if b["id"] in C.ORE_DROPS else None))
    quests = [dict(name=q[4] if LANG == "en" else q[5], desc=q[6] if LANG == "en" else q[7]) for q in C.QUESTS if q[1] == n]
    ach = ach_list(lambda a, n=n: False) if False else [
        dict(cat={"progress": t("Progress", "Progression"), "explore": t("Exploration", "Exploration"), "combat": t("Combat", "Combat"),
                  "hidden": t("Hidden", "Caché")}[a[0]], hidden=a[0] == "hidden", name=a[1] if LANG == "en" else a[2], desc=a[3] if LANG == "en" else a[4])
        for a in C.ACH.get(n, [])]
    return dict(items=items, blocks=blocks, quests=quests, ach=ach)


ARCH = {
    "tower": ("A tower with a spiral stair and a different room on every floor.", "Une tour à escalier en colimaçon, avec une pièce différente à chaque étage."),
    "lighthouse": ("A striped lighthouse with a gallery, a glazed lantern room and the keeper's cottage.", "Un phare rayé avec galerie, lanterne vitrée et maison du gardien."),
    "clock": ("A square clock tower with four faces, a pendulum and a belfry over a gear-paved court.", "Une tour d'horloge carrée à quatre cadrans, balancier et beffroi sur une cour pavée d'engrenages."),
    "temple": ("A stepped temple with a grand stair, a summit shrine and a pillared inner hall.", "Un temple à degrés avec grand escalier, sanctuaire au sommet et salle à colonnes."),
    "cathedral": ("A cathedral with nave, transept, buttresses, twin towers, a rose window and a guarded crypt.", "Une cathédrale avec nef, transept, arcs-boutants, tours jumelles, rosace et crypte gardée."),
    "throne": ("A pillared throne hall; the carpet before the throne hides a hatch to the treasure room.", "Une salle du trône à colonnes ; le tapis devant le trône cache une trappe vers la salle au trésor."),
    "library": ("A two-level library with book walls, a mezzanine and reading tables.", "Une bibliothèque sur deux niveaux, murs de livres, mezzanine et tables de lecture."),
    "lab": ("A laboratory of strange instruments, its upper floor furnished on the ceiling.", "Un laboratoire aux instruments étranges, son étage meublé au plafond."),
    "shrine": ("A shrine on a stepped platform, with a pavilion, an altar, a gate and stone lanterns.", "Un sanctuaire sur une plateforme à degrés, avec pavillon, autel, portail et lanternes de pierre."),
    "sanctuary": ("The Guardian's Sanctuary: three tiers, eight great pillars with braziers, the altar at the top.", "Le Sanctuaire du Gardien : trois niveaux, huit grands piliers à braseros, l'autel au sommet."),
    "village": ("Houses around a fountain plaza, with paths, garden plots, lamps and a belfry.", "Des maisons autour d'une place à fontaine, avec allées, potagers, lampadaires et beffroi."),
    "camp": ("A fire ring with log benches, tents, a cooking corner and a lookout post.", "Un foyer entouré de bancs, des tentes, un coin cuisine et un poste de guet."),
    "market": ("Two rows of awninged stalls under lantern strings, a covered hall and an entrance arch.", "Deux rangées d'étals à auvents sous des guirlandes de lanternes, une halle et une arche d'entrée."),
    "city": ("A walled city with corner towers, gates, avenues, houses and a guarded keep.", "Une cité fortifiée avec tours d'angle, portes, avenues, maisons et un donjon gardé."),
    "fort": ("A fort with curtain walls, four towers, a gatehouse with portcullis and a three-floor keep.", "Un fort avec courtines, quatre tours, châtelet à herse et donjon de trois étages."),
    "arena": ("A sunken arena with tiered seats, gates, a champion's box and beast pens.", "Une arène enterrée avec gradins, portes, loge du champion et enclos à bêtes."),
    "garden": ("A glass greenhouse with planters and a fountain.", "Une serre de verre avec jardinières et fontaine."),
    "ruin": ("Broken walls, a colonnade, a fallen column, a standing arch and a vaulted cellar.", "Des murs brisés, une colonnade, une colonne tombée, une arche debout et une cave voûtée."),
    "bridge": ("An arched bridge on piers with lamps, a broken gap, gate towers and a room inside a pier.", "Un pont en arches sur piles, avec lampes, une brèche, tours de garde et une salle dans une pile."),
    "rail": ("A trestle line with a broken end, a roofed station and a signal post.", "Une voie sur tréteaux à l'extrémité brisée, une gare couverte et un poteau de signal."),
    "stair": ("A looping stair whose last flight runs upside down, around a reading pavilion.", "Un escalier en boucle dont la dernière volée est à l'envers, autour d'un pavillon de lecture."),
    "vault": ("A kiosk over a spiral stair down to an antechamber; a mural wall hides the way to the pedestal room.", "Un kiosque sur un escalier en spirale vers une antichambre ; un mur peint cache le chemin de la salle du piédestal."),
    "crypt": ("A graveyard and mausoleum over a crypt of burial niches, sarcophagi and an ossuary.", "Un cimetière et un mausolée au-dessus d'une crypte de niches, de sarcophages et d'un ossuaire."),
    "cell": ("A two-storey prison with galleries, barred cells, the warden's office and a watchtower.", "Une prison sur deux étages avec coursives, cellules à barreaux, bureau du gardien et tour de guet."),
    "maze": ("A generated labyrinth with a central chamber, barred windows and, in the large ones, pit traps.", "Un labyrinthe généré avec chambre centrale, fenêtres à barreaux et, dans les grands, des fosses piégées."),
    "mine": ("A headframe with its wheel, a shaft with ladder, timbered galleries with rails and ore veins.", "Un chevalement et sa roue, un puits à échelle, des galeries boisées avec rails et filons."),
    "forge": ("A forge hall around a stepped furnace and chimney, with a lava channel and a barred vault.", "Une forge autour d'un fourneau à degrés et sa cheminée, avec canal de lave et chambre forte."),
    "well": ("A pavilion over a shaft with niches, down to a domed chamber with a pool and pillars.", "Un pavillon sur un puits à niches, jusqu'à une salle en coupole avec bassin et piliers."),
    "chasm": ("A jagged rift crossed by an arch bridge, with ledges, scaffolding and a grotto at the bottom.", "Une faille déchiquetée franchie par un pont, avec corniches, échafaudages et grotte au fond."),
    "nest": ("A crater with a lined bowl, eggs, bone ribs and burrows ending in dens.", "Un cratère au nid tapissé, avec œufs, côtes d'os et terriers menant à des tanières."),
    "hive": ("Lumpy domes with comb terraces, spore blossoms and a queen chamber.", "Des dômes bosselés aux terrasses d'alvéoles, fleurs à spores et chambre de la reine."),
    "cocoon": ("A great cocoon or crystal core with egg sacs around it.", "Un grand cocon ou un cœur de cristal entouré de poches d'œufs."),
    "wreck": ("A wrecked hull with a sterncastle cabin, a hold, masts and torn sails.", "Une coque échouée avec cabine de poupe, cale, mâts et voiles déchirées."),
    "bastion": ("A walled courtyard with corner towers, a gatehouse with its portcullis and a keep at the back.", "Une cour fortifiée avec tours d'angle, un châtelet à herse et un donjon au fond."),
    "circle": ("A ring of standing stones and lintels around a sunken altar where the guarded chest waits.", "Un cercle de pierres levées et de linteaux autour d'un autel enfoncé où attend le coffre gardé."),
    "outpost": ("A lookout hut on stilts over a supply yard, with a signal fire on its deck.", "Une cabane de guet sur pilotis au-dessus d'une cour de ravitaillement, un feu de signal sur sa plateforme."),
    "caravan": ("Covered wagons drawn up around a fire, with a stall and a hitching rail.", "Des chariots bâchés en cercle autour d'un feu, avec un étal et une barre d'attache."),
    "bell": ("A copper diving bell with portholes, a chain up to a buoy, crates and an anchor.", "Une cloche de plongée en cuivre à hublots, une chaîne vers une bouée, des caisses et une ancre."),
}
INSIDE = {
    "combat": ("A guarded loot room: spawners of the world's creatures around a rare chest (a vault chest in large ones), plus common chests.",
               "Une salle au butin gardée : des générateurs de créatures du monde autour d'un coffre rare (un coffre au trésor dans les grandes), plus des coffres communs."),
    "exploration": ("Two to four chests hidden around: under tables, behind bookshelves, in cellars, in dead ends. The first is rare in medium and large ones.",
                    "Deux à quatre coffres cachés : sous les tables, derrière les bibliothèques, dans les caves, au fond des impasses. Le premier est rare dans les moyennes et grandes."),
    "story": ("A reading nook with a lectern and candles around a rare chest holding a page of the Journal.",
              "Un coin lecture avec lutrin et bougies autour d'un coffre rare qui contient une page du Journal."),
    "utility": ("The people of the world live here and trade with you, beside a common chest.",
                "Le peuple du monde vit ici et commerce avec toi, près d'un coffre commun."),
    "secret": ("A puzzle or hidden passage leads to a vault chest with the world's hidden doll and a Journal page.",
               "Une énigme ou un passage caché mène à un coffre au trésor avec la poupée cachée du monde et une page du Journal."),
}
ROLE_LABEL = {"combat": ("Combat", "Combat"), "exploration": ("Exploration", "Exploration"), "story": ("Story", "Histoire"),
              "utility": ("People", "Peuple"), "secret": ("Secret", "Secret")}
SIZE_LABEL = {"small": ("Small", "Petite"), "medium": ("Medium", "Moyenne"), "large": ("Large", "Grande")}
RARITY_S = {"common": ("Common", "Courante"), "rare": ("Rare", "Rare"), "epic": ("Very rare", "Très rare"), "legendary": ("Unique", "Unique")}
VAN_FOOD = {1: "glow_berries", 2: "baked_potato", 3: "bread", 4: "apple", 5: "mushroom_stew", 6: "chorus_fruit", 7: "cooked_cod", 8: "pumpkin_pie", 9: "cooked_beef", 10: "cookie", 0: "bread"}
VAN_FLAV = {1: ("sweet_berries", "emerald"), 2: ("blaze_powder", "netherite_scrap"), 3: ("arrow", "name_tag"), 4: ("copper_ingot", "spyglass"), 5: ("glowstone_dust", "echo_shard"),
            6: ("ender_pearl", "shulker_shell"), 7: ("prismarine_crystals", "heart_of_the_sea"), 8: ("honey_bottle", "clock"), 9: ("lead", "totem_of_undying"), 10: ("gold_nugget", "gold_block"), 0: ("iron_ingot", "iron_ingot")}


def _van(i):
    return dict(id="minecraft:" + i, tex=None, name=t(*VANILLA[i]) if i in VANILLA else i.replace("_", " ").capitalize())


def loot(n):
    """What each chest tier of a world can hold, read from structure/Rewards.java."""
    def mods(kinds, rare):
        return [dict(id=it["id"], tex=tex(it["id"]), name=name(it["id"])) for it in C.ITEMS
                if it["world"] == n and it["kind"] in kinds and ((it["rarity"] not in ("common", "none")) if rare else it["rarity"] == "common")]
    common = mods({"resource", "food", "consumable"}, False) + [_van(VAN_FOOD[n]), _van("iron_nugget"), _van("prismarine_shard" if n == 7 else "torch"), _van("arrow"), _van("iron_ingot")]
    rare = mods({"resource", "gem", "ingot", "dust", "consumable", "key", "tool", "thread"}, True) + [_van(x) for x in ("iron_ingot", "gold_ingot", "emerald", "enchanted_book", "experience_bottle", "golden_carrot")] + [_van(VAN_FLAV[n][0])]
    vault = [_van(x) for x in ("diamond", "gold_ingot", "emerald", "enchanted_book", "golden_apple", "experience_bottle")] + [_van(VAN_FLAV[n][1])]
    gear = [dict(id=it["id"], tex=tex(it["id"]), name=name(it["id"])) for it in C.ITEMS if it["world"] == n and it["kind"] in
            {"weapon", "armor", "boots", "mask", "glider", "hook", "lantern", "sonar", "drill", "thruster", "anchor", "hourglass"} and it["rarity"] != "legendary"]
    seen = set()
    def uniq(lst):
        out = []
        for x in lst:
            if x["id"] not in seen:
                seen.add(x["id"]); out.append(x)
        return out
    tiers = [dict(tier=t("Common chest", "Coffre commun"), note=t("3 to 5 stacks", "3 à 5 piles"), items=uniq(common)),
             dict(tier=t("Rare chest", "Coffre rare"), note=t("often an enchanted book", "souvent un livre enchanté"), items=uniq(rare)),
             dict(tier=t("Vault chest", "Coffre au trésor"), note=t("rare items too, and a 30% chance of one piece of the world's gear", "les objets rares aussi, et 30 % de chances d'une pièce d'équipement du monde")
                  + (t(", 8% of an enchanted golden apple", ", 8 % d'une pomme dorée enchantée") if n >= 7 else ""), items=uniq(vault) + uniq(gear))]
    return tiers


def structures_of(n):
    out = []
    for (sid, en, fr, role, size, rarity, arch) in C.STRUCTURES[n]:
        out.append(dict(id=sid, name=en if LANG == "en" else fr, role=t(*ROLE_LABEL[role]), roleKey=role, size=t(*SIZE_LABEL[size]), rarity=t(*RARITY_S.get(rarity, ("", ""))),
                        desc=t(*ARCH.get(arch, ("", ""))), inside=t(*INSIDE[role]), img=shot(f"st_{sid}")))
    return out


def role_tags(m):
    tags = []
    if m.get("elite"):
        tags.append(t("Elite", "Élite"))
    if m.get("nesting") or m.get("behavior") == "splitter":
        tags.append(t("Nesting", "Gigogne"))
    if m.get("flying"):
        tags.append(t("Flying", "Volant"))
    if m.get("aquatic"):
        tags.append(t("Aquatic", "Aquatique"))
    if not tags:
        tags.append(t("Normal", "Normal"))
    return tags


def anim_names(eid):
    p = os.path.join(ANIM, f"{eid}.animation.json")
    if not os.path.exists(p):
        return []
    return list(json.load(open(p, encoding="utf-8"))["animations"].keys())


ANIM_LABEL = {"misc.idle": ("Idle", "Repos"), "move.walk": ("Walk", "Marche"), "attack.strike": ("Attack", "Attaque"),
              "attack.charge": ("Charge", "Charge"), "attack.slam": ("Slam", "Frappe au sol"), "attack.cast": ("Cast", "Incantation"),
              "misc.phase": ("Phase change", "Changement de phase"), "misc.rest": ("Opening", "Ouverture")}



def anims(eid):
    if eid in BOSS_IDS:
        return boss_anims(eid)
    labels = {f"attack.{a['slug']}": (a["en"], a["fr"]) for a in ATK.full(eid)} if eid in ATK.A else {}
    out = []
    for full in anim_names(eid):
        short = full.split(".", 1)[1] if full.startswith("animation.") else full
        lab = labels.get(short) or ANIM_LABEL.get(short)
        if not lab:
            raise SystemExit(f"site.py: no label for the animation {full} of {eid}")
        out.append(dict(key=full, label=t(*lab)))
    return out


# ---------------------------------------------------------------- boss moves (tools/boss_moves*.py)
ALL_BOSSES = C.BOSSES + [C.WORLD_ZERO_BOSS]
BOSS_IDS = {b["id"] for b in ALL_BOSSES}
# The Unfinished replays "Shell Attack" three times in content.py; its three cuts have their own names
MOVE_NAMES = {"the_unfinished": [("Shell Stroke", "Trait d'enveloppe"), ("Shell Lift", "Envol d'enveloppe"), ("Shell Burst", "Éclat d'enveloppe")]}
MOVE_SUFFIX = {"artisan_shadow": ".w1"}  # one cut per timing tier; the site shows the first


def boss_moves(eid):
    """[(slug, [windup, strike, recover])] in the order of the animation file (light, medium, signature)."""
    names = anim_names(eid)
    sfx = MOVE_SUFFIX.get(eid, "")
    slugs = []
    for n in names:
        m = re.fullmatch(rf"attack\.{eid}\.(\w+)\.windup" + re.escape(sfx), n)
        if m:
            slugs.append(m.group(1))
    out = []
    for slug in slugs:
        seq = [f"attack.{eid}.{slug}.{part}{sfx}" for part in ("windup", "strike", "recover")]
        missing = [k for k in seq if k not in names]
        if missing:
            raise SystemExit(f"site.py: {eid} misses {', '.join(missing)}")
        out.append((slug, seq))
    return out


def move_names(b):
    return MOVE_NAMES.get(b["id"]) or [tuple(a) for a in b["atk"][:3]]


def boss_anims(eid):
    b = next(x for x in ALL_BOSSES if x["id"] == eid)
    names = anim_names(eid)
    out = [dict(key="misc.idle", label=t("Idle", "Repos")), dict(key="move.walk", label=t("Walk", "Marche"))]
    for (slug, seq), nm in zip(boss_moves(eid), move_names(b)):
        out.append(dict(key=f"attack.{eid}.{slug}", label=t(*nm), seq=seq, slug=slug))
    for part, lab in (("phase", ("Phase change", "Changement de phase")), ("death", ("Fall", "Chute"))):
        k = f"misc.{eid}.{part}"
        if k not in names:
            raise SystemExit(f"site.py: {eid} misses {k}")
        out.append(dict(key=k, label=t(*lab), seq=[k], slug=part))
    return out


def check_boss_anims():
    for b in ALL_BOSSES:
        moves = boss_moves(b["id"])
        if len(moves) != 3:
            raise SystemExit(f"site.py: {b['id']} has {len(moves)} attack animations, not 3")
        boss_anims(b["id"])


def build_mobs():
    out = []
    for w in range(1, 11):
        lst = MOBS_OF[w]
        for i, m in enumerate(lst):
            mult = speed_mult(w)
            interval = max(6, int(20 / mult))
            beh = m["behavior"]
            melee = beh not in ("puller", "statue")
            spd = SPEED.get(beh, 0.26)
            sp = SPAWNS.get(m["id"])
            drops = [dict(id=m["drop"], tex=tex(m["drop"]), name=name(m["drop"]),
                          chance=pct(100) if m["elite"] else pct(60),
                          note=t("1 or 2", "1 ou 2") if m["elite"] else "1")]
            if m["rare_drop"] and tex(m["rare_drop"]):
                drops.append(dict(id=m["rare_drop"], tex=tex(m["rare_drop"]), name=name(m["rare_drop"]),
                                  chance=pct(5) if m["rare_drop"] == "terrain_heart" else pct(15), note="1"))
            if w == 1:
                drops.append(dict(id="roots", tex=tex("roots"), name=name("roots"), chance=pct(25), note="1",
                                  bonus=t("dropped by every World 1 creature", "laissées par toute créature du monde 1")))
            facts = []
            if m["elite"]:
                facts.append(t("Elites drop their common loot every time and give 5 souls to the player who lands the killing blow.",
                               "Les élites laissent toujours leur butin courant et donnent 5 âmes au joueur qui porte le coup fatal."))
            if m["nesting"]:
                facts.append(t("Nesting: when it dies it opens and releases two smaller copies with 40% of its health, 60% of its size and 30% more speed. The copies drop nothing.",
                               "Gigogne : à sa mort, elle s'ouvre et libère deux copies plus petites avec 40 % de sa vie, 60 % de sa taille et 30 % de vitesse en plus. Les copies ne laissent rien."))
            if m["flying"]:
                facts.append(t("It flies, ignores gravity and never takes fall damage.", "Il vole, ignore la gravité et ne subit jamais de dégâts de chute."))
            if w == 7:
                facts.append(t("Like every World 7 creature, it swims, never drowns and spawns in open water.",
                               "Comme toutes les créatures du monde 7, il nage, ne se noie jamais et apparaît en eau libre."))
            if w == 2 and beh != "lava_heat":
                facts.append(t("Like every World 2 creature, it is immune to fire.", "Comme toutes les créatures du monde 2, il est insensible au feu."))
            facts.append(t(f"{6 if m['elite'] else 2} armour, {pct(60 if m['elite'] else 10)} knockback resistance, {20 if m['elite'] else 6} experience. It notices players up to 32 blocks away.",
                           f"{6 if m['elite'] else 2} d'armure, {pct(60 if m['elite'] else 10)} de résistance au recul, {20 if m['elite'] else 6} points d'expérience. Il repère les joueurs jusqu'à 32 blocs."))
            facts.append(t("Elites never despawn." if m["elite"] else "It despawns when no player is within 128 blocks.",
                           "Les élites ne disparaissent jamais." if m["elite"] else "Il disparaît quand aucun joueur n'est à moins de 128 blocs."))
            ach = ach_list(lambda a, m=m: a[5] == ("kill", m["id"]) or (a[5][0] == "custom" and a[5][1] in CUSTOM_ACH.get(m["behavior"], []) and (m["behavior"] != "mimic" or m["world"] == 3)))
            out.append(dict(
                id=m["id"], kind="mob", name=name(m["id"]), en=m["en"], fr=m["fr"], world=w, worldName=world_name(w),
                light=light(w), bg=world_bg(w), doll=doll(w), desc=m["desc_" + LANG], tags=role_tags(m), elite=m["elite"],
                hp=fmt(m["hp"]), dmg=fmt(m["dmg"]), hpRaw=m["hp"], dmgRaw=m["dmg"],
                speedMult="×" + fmt(round(mult, 2)), attackEvery=secs(interval / 20) if melee else None, attackTicks=interval if melee else None,
                moveSpeed=fmt(spd),
                behaviour=t(*BEHAVIOUR[beh]), facts=facts, drops=drops,
                moves=[dict(key=f"attack.{a['slug']}", name=t(a["en"], a["fr"]), desc=t(ATK.describe(a, "en"), ATK.describe(a, "fr")),
                            cooldown=secs(a["cd"] / mult)) for a in ATK.full(m["id"])],
                spawn=None if not sp else dict(weight=sp["weight"], share=pct(round(100 * sp["weight"] / sp["total"])), min=sp["min"], max=sp["max"]),
                quests=quest_list(m["id"]), ach=ach,
                tex=f"entities/{m['id']}.png" if m["id"] in ENTITY_TEX else None,
                dropTex=tex(m["drop"]), anims=anims(m["id"]),
                prev=lst[i - 1]["id"] if i > 0 else None, next=lst[i + 1]["id"] if i + 1 < len(lst) else None,
                prevName=name(lst[i - 1]["id"]) if i > 0 else None, nextName=name(lst[i + 1]["id"]) if i + 1 < len(lst) else None))
    return out


LAIR_NAME = {"spore_queen": ("The Hive", "La Ruche"), "ash_titan": ("The Forge-Hall", "La Halle-forge"), "light_eater": ("The Lightless Pit", "La Fosse sans lumière"),
             "your_double": ("The Hall of Mirrors", "La Galerie des glaces"), "pressure_leviathan": ("The Sunken Trench Temple", "Le Temple englouti de la fosse"),
             "terrain_heart_boss": ("The Living Cavern", "La Caverne vivante")}


def meet(b):
    """How to meet a boss, for its poster, its sheet and its world page."""
    if b.get("meet") == "lair":
        return dict(mode="lair", modeLabel=t("Lair boss", "Boss d'antre"), place=t(*LAIR_NAME[b["id"]]),
                    steps=[t("Walk 160 blocks south of the Threshold to its lair gate.", "Marche 160 blocs au sud du Seuil, jusqu'à la porte de son antre."),
                           t("Come within 10 blocks of the lair heart at the centre of the chamber.", "Approche-toi à moins de 10 blocs du cœur d'antre, au centre de la salle."),
                           t("It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.", "Il s'éveille après trois secondes de secousse. Bats-le et l'alcôve au trésor s'ouvre : trois coffres du meilleur butin du monde."),
                           t("The heart wakes again ten minutes later, for a second fight.", "Le cœur se réveille dix minutes plus tard, pour un nouveau combat.")],
                    heartTex="blocks/lair_heart.png", heartName=name("lair_heart"))
    if b.get("offering"):
        st, r = recipe_for(b["offering"])
        return dict(mode="altar", modeLabel=t("Altar boss", "Boss d'autel"), place=t("The arena altar", "L'autel de l'arène"),
                    offering=dict(id=b["offering"], tex=tex(b["offering"]), name=name(b["offering"]), station=name(st) if st else None,
                                  inputs=ing(r["inputs"]) if r else []),
                    steps=[t(f"Craft a {name(b['offering'])} at the {name(st)}." if st else f"Get a {name(b['offering'])}.", f"Fabrique l'offrande {name(b['offering'])} à la station {name(st)}." if st else f"Obtiens l'offrande {name(b['offering'])}."),
                           t("Walk 160 blocks south of the Threshold to the arena.", "Marche 160 blocs au sud du Seuil, jusqu'à l'arène."),
                           t("Hold the offering and use the altar on its dais: a three-second ritual summons the boss.", "Tiens l'offrande et utilise l'autel sur son estrade : un rituel de trois secondes invoque le boss."),
                           t("Every fight, the first and the next ones, costs one offering.", "Chaque combat, le premier comme les suivants, coûte une offrande.")])
    return dict(mode="altar", modeLabel=t("Altar boss", "Boss d'autel"), place=t("The Guardian's Sanctuary", "Le Sanctuaire du Gardien"),
                steps=[t("Follow your Scroll's sketch to the Guardian's Sanctuary on the Surface.", "Suis le croquis du Parchemin jusqu'au Sanctuaire du Gardien, sur la Surface."),
                       t("Use the sanctuary altar: the Block Guardian rises. No offering needed.", "Utilise l'autel du sanctuaire : le Gardien du bloc se dresse. Aucune offrande n'est nécessaire."),
                       t("Sneak while using the altar to fight it again.", "Accroupis-toi en utilisant l'autel pour le combattre à nouveau.")])


def build_bosses():
    labels = [t("Light", "Légère"), t("Medium", "Moyenne"), t("Signature", "Signature"), t("Final phase", "Phase finale")]
    out = []
    order = sorted(C.BOSSES, key=lambda b: b["world"])
    for i, b in enumerate(order):
        w = b["world"]
        tele, opening = tier_ticks(w)
        if b["id"] == "the_unfinished":
            phases = t("Ten shells, one every 10% of its health", "Dix enveloppes, une tous les 10 % de sa vie")
            atks = [dict(label=t("Shells 1 to 9", "Enveloppes 1 à 9"),
                         name=t("Each broken shell takes the face of an earlier world and replays its attacks.", "Chaque enveloppe brisée prend le visage d’un monde précédent et rejoue ses attaques.")),
                    dict(label=labels[3], name=b["atk"][3][0 if LANG == "en" else 1])]
        else:
            phases = t("Phases at ", "Phases à ") + (t(" and ", " et ").join(pct(int(p * 100)) for p in b["phases"])) + t(" of its health", " de sa vie")
            atks = [dict(label=labels[k], name=a[0] if LANG == "en" else a[1]) for k, a in enumerate(b["atk"])]
        timings = [
            dict(label=t("Light attack, warning", "Attaque légère, annonce"), v=secs(max(6, tele // 2) / 20)),
            dict(label=t("Medium attack, warning", "Attaque moyenne, annonce"), v=secs(tele / 20)),
            dict(label=t("Signature attack, warning", "Attaque signature, annonce"), v=secs(tele * 2 / 20)),
            dict(label=t("Opening after a medium attack", "Ouverture après une attaque moyenne"), v=secs(opening / 20)),
            dict(label=t("Opening after the signature", "Ouverture après la signature"), v=secs(opening / 2 / 20)),
            dict(label=t("Pause while changing phase", "Pause au changement de phase"), v=secs(2)),
        ]
        cooldown = [t("Signature attack at most every 20 seconds, 1 second sooner per phase.", "Attaque signature au plus toutes les 20 secondes, 1 seconde plus tôt par phase."),
                    t("Medium attack at most every 8 seconds, light attack every 4 seconds when you are close; both come a little sooner each phase.", "Attaque moyenne au plus toutes les 8 secondes, attaque légère toutes les 4 secondes quand tu es proche ; les deux reviennent un peu plus vite à chaque phase."),
                    t("Each phase makes it 10% faster.", "Chaque phase le rend 10 % plus rapide.")]
        moves = [dict(slug=slug, anim=f"attack.{b['id']}.{slug}", name=t(*nm), label=labels[k], warn=timings[k]["v"],
                      windup=move_shot(b["id"], slug, "windup"), strike=move_shot(b["id"], slug, "strike"))
                 for k, ((slug, _seq), nm) in enumerate(zip(boss_moves(b["id"]), move_names(b)))]
        passive = atks if b["id"] == "the_unfinished" else atks[3:]
        drops = [dict(id=b["core"], tex=tex(b["core"]), name=name(b["core"]), note="1")]
        if w == 0:
            drops += [dict(id="matrix_workbench", tex=tex("matrix_workbench"), name=name("matrix_workbench"), note="1"),
                      dict(id="world_soil_0", tex=tex("world_soil_0"), name=name("world_soil_0"), note="4")]
        elif w < 10:
            drops.append(dict(id=f"world_soil_{w}", tex=tex(f"world_soil_{w}"), name=name(f"world_soil_{w}"), note="4"))
            if w == 9:
                drops.append(dict(id="last_doll_key", tex=tex("last_doll_key"), name=name("last_doll_key"), note="1"))
        unlocks = []
        if w < 10:
            unlocks.append(t(f"Its core opens the way into World {w + 1}.", f"Son noyau ouvre le chemin du monde {w + 1}."))
        if w == 0:
            unlocks.append(t("Your Scroll becomes the Artisan's Journal.", "Ton Parchemin devient le Journal de l'artisan."))
        if w in (1, 5, 8):
            unlocks.append(t("Your Doll of Life gains a layer.", "Ta Poupée de vie gagne une couche."))
        else:
            unlocks.append(t("Your Doll of Life gets one layer back.", "Ta Poupée de vie récupère une couche."))
        if w == 2:
            unlocks.append(t("Enchanting, anvils and the Nether open.", "Enchantements, enclumes et Nether s'ouvrent."))
        if w == 8:
            unlocks.append(t("The End opens, and elytra fly again.", "L'End s'ouvre, et les élytres volent de nouveau."))
        special = []
        if b.get("meet") == "lair":
            special.append(t("It sleeps in its lair, 160 blocks south of the Threshold. Come within 10 blocks of the lair heart at the centre to wake it. When it falls, the seal of the treasure alcove breaks and its chests fill with the world's best loot; the heart wakes again 10 minutes later.",
                             "Il dort dans son antre, à 160 blocs au sud du Seuil. Approche-toi à moins de 10 blocs du cœur d'antre, au centre, pour le réveiller. Quand il tombe, le sceau de l'alcôve au trésor se brise et ses coffres se remplissent du meilleur butin du monde ; le cœur se réveille 10 minutes plus tard."))
        elif b.get("offering"):
            special.append(t(f"Wake it at the arena altar, 160 blocks south of the Threshold, while holding a {name(b['offering'])}. The offering is consumed and a three-second ritual summons it; every fight costs one offering.",
                             f"Réveille-le à l'autel d'arène, à 160 blocs au sud du Seuil, en tenant l'offrande {name(b['offering'])}. Elle est consommée et un rituel de trois secondes l'invoque ; chaque combat coûte une offrande."))
        if b["id"] == "spore_queen":
            special.append(t("At her last phase she calls three Chitin Guards; her cocoon holds until those nodes are broken.", "À sa dernière phase, elle appelle trois Gardiens de chitine ; son cocon tient tant que ces nœuds ne sont pas brisés."))
        if b["id"] == "block_guardian":
            special.append(t("At half health it rebuilds itself from the arena and heals 10% of its health.", "À mi-vie, il se reconstruit avec l'arène et regagne 10 % de sa vie."))
        if b["id"] == "ash_titan":
            special.append(t("In its last phase its armour has melted: it takes 30% more damage on top of the usual multiplier.", "Dans sa dernière phase, son armure a fondu : il subit 30 % de dégâts en plus du multiplicateur habituel."))
        ach = ach_list(lambda a, b=b: a[5] == ("kill", b["id"]) or (a[5][0] == "custom" and a[5][1] in BOSS_ACH.get(b["id"], [])))
        out.append(dict(
            meet=meet(b), id=b["id"], kind="boss", name=b[LANG], en=b["en"], fr=b["fr"], world=w, worldName=world_name(w), light=light(w), bg=world_bg(w), doll=doll(w),
            hp=fmt(b["hp"]), dmg=fmt(b["dmg"]), phases=phases, atks=atks, moves=moves, passive=passive, timings=timings, cooldown=cooldown,
            mp=[dict(p=p, mult="×" + fmt(round(1 + 0.6 * (p - 1), 1)), hp=fmt(int(round(b["hp"] * (1 + 0.6 * (p - 1)))))) for p in (1, 2, 4, 8)],
            drops=drops, souls=t("100 souls for every player within 64 blocks", "100 âmes pour chaque joueur à moins de 64 blocs"),
            unlocks=unlocks, special=special, story=LANGS[LANG].get(f"message.matriochka.boss_down.{w}", ""),
            shot=shot(f"w{w:02d}_boss"), block=f"blocks/{WORLD_BLOCK[w]}.png",
            coreTex=tex(b["core"]), tex=f"entities/{b['id']}.png" if b["id"] in ENTITY_TEX else None,
            anims=anims(b["id"]), quests=quest_list(b["id"]), ach=ach,
            prev=order[i - 1]["id"] if i > 0 else None, next=order[i + 1]["id"] if i + 1 < len(order) else None,
            prevName=order[i - 1][LANG] if i > 0 else None, nextName=order[i + 1][LANG] if i + 1 < len(order) else None))
    return out


# ---------------------------------------------------------------- page copy
def build_copy():
    d = LANGS[LANG]
    ui = dict(
        skip=t("Skip to content", "Aller au contenu"), main=t("Main", "Principale"), other=t("Français", "English"),
        github=t("Source code on GitHub", "Code source sur GitHub"),
        footer=t("A Fabric mod by achedon12, for Minecraft 26.3. Released under the MIT licence.", "Un mod Fabric d'achedon12 pour Minecraft 26.3, publié sous licence MIT."),
        notOfficial=t("Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.", "Ce n'est pas un produit officiel Minecraft. Non approuvé par Mojang ou Microsoft, et sans lien avec eux."),
        releases=t("Releases", "Versions"), wiki="Wiki", bug=t("Report a bug", "Signaler un bug"),
        world=t("World", "Monde"), health=t("Health", "Vie"), damage=t("Damage", "Dégâts"), boss=t("Boss", "Boss"),
        creatures=t("Creatures", "Créatures"), rule=t("Rule", "Règle"), stage=t("Stage", "Palier"),
        seed=t("Opening it", "L'ouvrir"), station=t("Station", "Station"), workbench=name("matrix_workbench"), builtFrom=t("Built at the Matrix Workbench from", "Se fabrique à l'Établi matriciel avec"),
        carry=t("What you'll carry", "Ce que tu emporteras"), structures=t("Eleven structures", "Onze structures"), armour=t("Armour set", "Armure"),
        madeAt=t("Made at the Matrix Workbench", "Fabriqué à l'Établi matriciel"), moreAbout=t("Everything about this world", "Tout sur ce monde"),
        allWorlds=t("All worlds", "Tous les mondes"), back=t("Back to the bestiary", "Retour au bestiaire"), backBosses=t("Back to the bosses", "Retour aux boss"),
        backWorlds=t("Back to the ten worlds", "Retour aux dix mondes"),
        prev=t("Previous", "Précédent"), next=t("Next", "Suivant"), sheet=t("Technical sheet", "Fiche technique"),
        view3d=t("View in 3D", "Voir en 3D"), loading3d=t("Opening the model", "Ouverture du modèle"),
        no3d=t("This browser cannot draw the 3D model. Here is its texture, as the game paints it.", "Ce navigateur ne peut pas afficher le modèle 3D. Voici sa texture, telle que le jeu la peint."),
        dragHint=t("Drag to turn it, scroll or pinch to zoom.", "Fais glisser pour le tourner, molette ou pincement pour zoomer."),
        animations=t("Animations", "Animations"), see3d=t("See it in 3D", "Voir en 3D"), windup=t("Wind-up", "Annonce"), strike=t("Strike", "Frappe"),
        warning=t("warning", "d'annonce"), inGame=t("In game", "En jeu"), autoRotate=t("Turn slowly", "Tourner lentement"),
        role=t("Role", "Rôle"), attackSpeed=t("Attack speed", "Vitesse d'attaque"), attackEvery=t("one hit every", "un coup toutes les"),
        noMelee=t("no melee attack", "aucune attaque au corps à corps"), moveSpeed=t("Movement speed", "Vitesse de déplacement"),
        behaviour=t("How it fights", "Comment il combat"), moves=t("Attacks", "Attaques"), openSheet=t("Open its technical sheet", "Ouvrir sa fiche technique"), howMeet=t("How to meet it", "Comment le rencontrer"), offering=t("Offering", "Offrande"), explore=t("Explore", "Explorer"), pause=t("Pause the worlds", "Mettre les mondes en pause"), play=t("Play the worlds", "Faire défiler les mondes"),
        search=t("Search the bestiary", "Chercher dans le bestiaire"), searchPh=t("A creature or an attack…", "Une créature ou une attaque…"),
        elitesOnly=t("Elites only", "Élites seulement"), elite=t("Elite", "Élite"),
        noMatch=t("No creature matches. Clear the search or pick another world.", "Aucune créature ne correspond. Vide la recherche ou choisis un autre monde."), movesLead=t("Its own attacks, shared with no other creature. It picks among them, never the same one twice in a row, and each has a wind-up you can read before it lands.", "Ses attaques à elle, qu'aucune autre créature ne partage. Elle choisit parmi elles, jamais deux fois la même d'affilée, et chacune a une préparation lisible avant de frapper."), recharge=t("Recharge", "Recharge"), drops=t("Drops", "Butin"), chance=t("Chance", "Chance"), count=t("Count", "Quantité"),
        spawns=t("Where it spawns", "Où il apparaît"), spawnWeight=t("spawn weight", "poids d'apparition"),
        spawnShare=t("of the creatures that spawn in its world", "des créatures qui apparaissent dans son monde"),
        group=t("per group", "par groupe"), quests=t("Quests", "Quêtes"), achievements=t("Achievements", "Succès"),
        noQuests=t("No quest asks for this one.", "Aucune quête ne la demande."), noAch=t("No achievement is tied to it.", "Aucun succès n'y est lié."),
        killN=t("to defeat", "à vaincre"), phases=t("Phases", "Phases"), attacks=t("Attacks", "Attaques"), timings=t("Reading the fight", "Lire le combat"),
        inGroup=t("In a group", "En groupe"), players=t("Players nearby", "Joueurs à proximité"), bossHealth=t("Boss health", "Vie du boss"),
        reward=t("Reward", "Récompense"), unlocks=t("What its fall opens", "Ce qu'ouvre sa chute"), reveal=t("What its fall reveals", "Ce que révèle sa chute"),
        solo=t("Health, solo", "Vie, en solo"), heavy=t("Heavy hit", "Coup fort"), arena=t("Spawns in its arena, woken at the altar. It never despawns.", "Apparaît dans son arène, réveillé à l'autel. Il ne disparaît jamais."),
        filter=t("Filter by world", "Filtrer par monde"), all=t("All", "Tous"), creature=t("Creature", "Créature"), traits=t("Traits", "Traits"),
        open=t("Open the sheet", "Ouvrir la fiche"), specimen=t("Specimen", "Spécimen"), worldsLink=t("Walk through the ten worlds", "Parcourir les dix mondes"),
        download=t("Download", "Télécharger"), surface=t("The Surface", "La Surface"), inArena=t("in its arena", "dans son arène"),
        multiplier=t("Multiplier", "Multiplicateur"), bossOf=t("Guardian of", "Gardien de"),
    )
    nav = {k: t(*v) for k, v in NAV.items()}
    home = dict(
        tagline=t("Every block can hold a world.", "Chaque bloc peut contenir un monde."),
        intro=t("A Fabric mod for Minecraft 26.3. Ten worlds, each sealed inside a single block and nested in the one before it. Every world has its own rule, its own creatures, its own station, and a boss guarding the core that opens the next.",
                "Un mod Fabric pour Minecraft 26.3. Dix mondes, chacun scellé dans un seul bloc et emboîté dans le précédent. Chaque monde a sa règle, ses créatures, sa station, et un boss qui garde le noyau ouvrant le suivant."),
        facts=t(f"Minecraft 26.3 on Fabric, version {VERSION}. Solo and multiplayer.", f"Minecraft 26.3 sous Fabric, version {VERSION}. Solo et multijoueur."),
        dollsTitle=t("A set of eleven nesting dolls, just opened: the Surface, then worlds 1 to 10, from the largest to the smallest",
                     "Un jeu de onze poupées gigognes qu'on vient d'ouvrir : la Surface, puis les mondes 1 à 10, de la plus grande à la plus petite"),
        dollsCaption=t("The Surface, then the ten worlds it holds. Pick a doll to open its world.", "La Surface, puis les dix mondes qu'elle contient. Choisis une poupée pour ouvrir son monde."),
        trailerH=t("The trailer", "La bande-annonce"),
        trailerFallback=t("Download the trailer (MP4)", "Télécharger la bande-annonce (MP4)"),
        loopH=t("How a world opens", "Comment s'ouvre un monde"),
        loopP=t("One loop, ten times over. Each pass asks you to unlearn the last world.", "Une seule boucle, dix fois de suite. Chaque tour te demande d'oublier le monde d'avant."),
        loop=[dict(tex=tex(i), h=h, p=p) for i, h, p in [
            ("guardian_core", t("Wake the Guardian", "Réveille le Gardien"),
             t("Follow the Scroll's sketch to the Guardian's Sanctuary and beat the Block Guardian. It drops its core, the Matrix Workbench and your first World Soil.",
               "Suis le croquis du Parchemin jusqu'au Sanctuaire du Gardien et bats le Gardien du bloc. Il laisse son noyau, l'Établi matriciel et ta première Terre de monde.")),
            ("seed_1", t("Craft a Seed", "Fabrique une Graine"),
             t("At the Matrix Workbench: the last boss's core plus resources from its world. The World 1 Seed asks for the Guardian Core, 16 iron ingots and 16 oak logs.",
               "À l'Établi matriciel : le noyau du dernier boss et des ressources de son monde. La Graine du monde 1 demande le Noyau du Gardien, 16 lingots de fer et 16 bûches de chêne.")),
            ("world_soil_0_tilled", t("Plant it on World Soil", "Plante-la sur une Terre de monde"),
             t("Till World Soil with a hoe and plant the Seed, with water within four blocks. What you feed it decides whether its world hatches calm or wild.",
               "Bêche une Terre de monde à la houe et plantes-y la Graine, avec de l'eau à moins de quatre blocs. Ce que tu lui donnes décide si son monde éclot apaisé ou sauvage.")),
            ("world_block", t("Enter the block", "Entre dans le bloc"),
             t("The Seed hatches into a World Block. Use it and you shrink inside, onto a Threshold that brings you back out.",
               "La Graine éclot en Bloc-monde. Utilise-le et tu rétrécis à l'intérieur, sur un Seuil qui te ramène dehors.")),
            ("filter_mask", t("Survive its rule", "Survis à sa règle"),
             t("Toxin, heat, wind, noise, gravity, pressure: each world changes how you play. Its station turns local resources into the gear that answers the rule.",
               "Toxine, chaleur, vent, bruit, gravité, pression : chaque monde change ta façon de jouer. Sa station transforme les ressources locales en équipement qui répond à la règle.")),
            ("queen_core", t("Beat the boss, take its core", "Bats le boss, prends son noyau"),
             t("Every attack is announced, then leaves an opening. Read the pattern, punish the opening, take the core.",
               "Chaque attaque est annoncée, puis laisse une ouverture. Lis le schéma, punis l'ouverture, prends le noyau.")),
            ("seed_2", t("Go deeper", "Descends encore"),
             t("The core opens the way into the next world, and every world has its own rite: an Ember Heart near lava, a key in an iron door, a rod in a storm, a lantern in the dark. Ten times, until the last block opens onto something much larger.",
               "Le noyau ouvre le chemin du monde suivant, et chaque monde a son rite : un Cœur de braise près de la lave, une clé dans une porte en fer, un paratonnerre sous l'orage, une lanterne dans le noir. Dix fois, jusqu'à ce que le dernier bloc s'ouvre sur quelque chose de bien plus grand."))]],
        worldsH=t("Ten worlds, ten rules", "Dix mondes, dix règles"),
        worldsP=t("Learning, then mastery, then expertise. World 10 tests everything at once.", "Apprentissage, puis maîtrise, puis expertise. Le monde 10 vérifie tout à la fois."),
        sysH=t("Built to be survived", "Pensé pour qu'on y survive"),
        sysP=t("Death teaches. It does not erase hours of progress.", "La mort apprend. Elle n'efface pas des heures de progression."),
        sysLink=t("How the systems work", "Comment marchent les systèmes"),
        systems=[dict(tex=tex(i), h=h, p=p) for i, h, p in [
            ("life_doll", t("Doll of Life", "Poupée de vie"),
             t("A nested doll you wear. When you die, a layer breaks instead and you get back up. It gains layers after Worlds 1, 5 and 8.",
               "Une poupée gigogne que tu portes. Quand tu meurs, une couche se brise à ta place et tu te relèves. Elle gagne des couches après les mondes 1, 5 et 8.")),
            ("soul_altar", t("Souls and karma", "Âmes et karma"),
             t("Every item holds a soul. At the Soul Altar, purify it for karma or devour it for power. Karma moves prices, quests and the ending.",
               "Chaque objet porte une âme. À l'Autel des âmes, purifie-la pour le karma ou dévore-la pour la puissance. Le karma change les prix, les quêtes et la fin.")),
            ("chance_doll", t("Gear classes", "Classes d'équipement"),
             t("Every weapon, tool and armour piece is born with one of six classes. Raise it to level 5 with souls, or gamble on a Chance Doll.",
               "Chaque arme, outil ou pièce d'armure naît avec l'une des six classes. Monte-la au niveau 5 avec des âmes, ou tente ta chance avec une Poupée du hasard.")),
            ("return_thread", t("Play as a group", "Joue en groupe"),
             t("Up to eight players share a group, its worlds and its defeated bosses. Bosses grow tougher with every player who joins the fight.",
               "Jusqu'à huit joueurs partagent un groupe, ses mondes et ses boss vaincus. Les boss se renforcent à chaque joueur qui rejoint le combat.")),
            ("class_table", t("Talents", "Talents"),
             t("Each class has three branches of four talents at the Class Table, bought with souls and Shell Shards and opened as your group goes deeper.",
               "Chaque classe a trois branches de quatre talents à la Table de classe, achetés avec des âmes et des Éclats d'enveloppe, et ouverts à mesure que ton groupe descend.")),
            ("trophy_doll_gauntlet", t("Trials and world events", "Épreuves et événements"),
             t("After an ending, race each world's trial or the Gauntlet of the eleven bosses for the server's board. In the worlds, invasions, surges of the rule and travelling merchants come and go.",
               "Après une fin, cours l'épreuve de chaque monde ou l'Épreuve des onze boss pour le tableau du serveur. Dans les mondes, invasions, poussées de la règle et marchands itinérants vont et viennent."))]],
        reelWatch=t("Watch the trailer", "Voir la bande-annonce"),
        heroGenre=t("A Minecraft mod of ten worlds, each sealed inside a block of the one before.",
                    "Un mod Minecraft de dix mondes, chacun scellé dans un bloc du précédent."),
        heroStatus=t("alpha, out now for Minecraft 26.3 on Fabric. Free and open source.",
                     "alpha, disponible pour Minecraft 26.3 sur Fabric. Gratuit et open source."),
        heroImg=shot("hero_banner"),
        surfaceLabel=t("The Surface", "La Surface"),
        openWorld=t("Open", "Ouvrir"),
        verbsH=t("What you do in Matriochka", "Ce que tu fais dans Matriochka"),
        verbsP=t("Four things, over and over, ten worlds deep.", "Quatre choses, encore et encore, sur dix mondes de profondeur."),
        verbs=[dict(verb=t("Open a world", "Ouvre un monde"), p=t("Plant the first Seed, then perform each world's own rite: fire, a key, a storm, darkness, mirrors, the deep. The block that appears holds a world.",
                                                                      "Plante la première Graine, puis accomplis le rite de chaque monde : le feu, une clé, l'orage, le noir, des miroirs, les abysses. Le bloc qui apparaît contient un monde."),
                    img=shot("gui_station_matrix_workbench"), href="systems/"),
               dict(verb=t("Survive its rule", "Survis à sa règle"), p=t("Toxic air, rising heat, total darkness, upside-down gravity: each world bends one rule.",
                                                                         "Air toxique, chaleur, obscurité totale, gravité inversée : chaque monde tord une règle."),
                    img=shot("verb_survive"), href="worlds/"),
               dict(verb=t("Fight what lives there", "Affronte ce qui y vit"), p=t("Fifty creatures with their own attacks, and a boss that guards the core of the next world.",
                                                                                 "Cinquante créatures aux attaques propres, et un boss qui garde le noyau du monde suivant."),
                    img=shot("verb_fight"), href="bestiary/"),
               dict(verb=t("Craft what it gives", "Fabrique ce qu'il donne"), p=t("Each world has its station, its armour and its tools, the ones you need for the world below.",
                                                                                  "Chaque monde a sa station, son armure et ses outils, ceux qu'il te faut pour le monde suivant."),
                    img=shot("gui_station_spore_vat"), href="worlds/1/")],
        allCreatures=t("See all fifty creatures", "Voir les cinquante créatures"),
        sysImg=shot("gui_journal_1"),
        getH=t("Get Matriochka", "Obtenir Matriochka"),
        getP=t("Install it on the client to play solo, and on both server and clients to play together.",
               "Installe-le sur le client pour jouer seul, et sur le serveur comme sur les clients pour jouer ensemble."),
        platforms=[dict(name="GitHub", note=t(f"Version {VERSION}, changelog and source", f"Version {VERSION}, journal des changements et code source"), href=RELEASES, icon="github"),
                   dict(name="Modrinth", note=t("In review, coming soon", "En cours de validation, bientôt"), href=None, icon="package"),
                   dict(name="CurseForge", note=t("In review, coming soon", "En cours de validation, bientôt"), href=None, icon="package"),
                   dict(name="Matriochka Pack", note=t("A ready modpack (.mrpack), normal or hard, on every release", "Un modpack prêt (.mrpack), normal ou difficile, à chaque version"), href=RELEASES, icon="package"),
                   dict(name="Discord", note=t("News, help and screenshots", "Nouvelles, aide et captures"), href=DISCORD, icon="users")],
        faqH=t("Questions", "Questions"),
        faq=[dict(q=t("Where do I start?", "Par où commencer ?"),
                  a=t("Read the Artisan's Scroll you spawn with, then find the Guardian's Sanctuary on the Surface and wake the Block Guardian.",
                      "Lis le Parchemin de l'artisan reçu au départ, puis trouve le Sanctuaire du Gardien sur la Surface et réveille le Gardien du bloc.")),
             dict(q=t("My world does not open.", "Mon monde ne s'ouvre pas."),
                  a=t("Smoke puffs mean the rite is still waiting: stand close and it tells you what it lacks. The World 1 Seed wants tilled World Soil 0 and water; each other object's description says where it goes and what it waits for.",
                      "Des volutes de fumée veulent dire que le rite attend encore : approche-toi, il te dit ce qui lui manque. La Graine du monde 1 veut une Terre de monde 0 bêchée et de l'eau ; la description de chaque autre objet dit où le poser et ce qu'il attend.")),
             dict(q=t("I died inside a world. Are my things gone?", "Je suis mort dans un monde. Mes affaires sont perdues ?"),
                  a=t("No. A death chest keeps them where you fell, and a Soul Cradle placed beforehand lets you wake up inside the world.",
                      "Non. Un coffre de mort les garde là où tu es tombé, et un Berceau d'âmes posé avant te fait renaître dans le monde.")),
             dict(q=t("Does it work on servers?", "Ça marche en multijoueur ?"),
                  a=t("Yes, with the mod on the server and on every client. Up to eight players share a group, its worlds and its bosses.",
                      "Oui, avec le mod sur le serveur et sur chaque client. Jusqu'à huit joueurs partagent un groupe, ses mondes et ses boss.")),
             dict(q=t("Does it work on Lunar Client?", "Ça marche sur Lunar Client ?"),
                  a=t("Through Lunar Client's Fabric profile for 26.3, with Fabric API and GeckoLib.", "Via le profil Fabric de Lunar Client pour la 26.3, avec Fabric API et GeckoLib.")),
             dict(q=t("Does it work with Sodium, Iris and minimaps?", "Ça marche avec Sodium, Iris et les minicartes ?"),
                  a=t("Yes. It was checked with Sodium, Iris, Xaero's Minimap and World Map, JourneyMap, VoxelMap and Traveler's Backpack. Xaero's cave view and radar switch off in the Lightless Deep, where they would show what the dark hides.",
                      "Oui. Il a été vérifié avec Sodium, Iris, Xaero's Minimap et World Map, JourneyMap, VoxelMap et Traveler's Backpack. La vue des grottes et le radar de Xaero s'éteignent dans la Profondeur sans lumière, où ils montreraient ce que le noir cache.")),
             dict(q=t("Is there a modpack?", "Y a-t-il un modpack ?"),
                  a=t("The Matriochka Pack, a Modrinth .mrpack with the mod, its libraries, Just Enough Items and client performance mods, in a normal and a hard version. It is attached to every GitHub release, with the optional Matriochka HD resource pack.",
                      "Le Matriochka Pack, un .mrpack Modrinth avec le mod, ses bibliothèques, Just Enough Items et des mods de performance, en version normale et difficile. Il est joint à chaque version GitHub, avec le pack de ressources facultatif Matriochka HD.")),
             dict(q=t("Which languages does it speak?", "Dans quelles langues ?"),
                  a=t("English, French, Spanish, German and Brazilian Portuguese: names, interface, quests, the Scroll, the fifty Journal pages, endings and subtitles.",
                      "Anglais, français, espagnol, allemand et portugais du Brésil : noms, interface, quêtes, Parchemin, les cinquante pages du Journal, fins et sous-titres.")),
             dict(q=t("Can I fight a boss again?", "Je peux refaire un boss ?"),
                  a=t("Yes. Its altar wakes it again, and it drops its core, soil and souls again.", "Oui. Son autel le réveille à nouveau, et il laisse encore son noyau, sa terre et ses âmes."))],
        stripH=t("Ten worlds, one inside the other", "Dix mondes, l'un dans l'autre"),
        stripP=t("Every world is sealed in a block you grow inside the world before it. Open one.",
                 "Chaque monde est scellé dans un bloc que tu fais pousser dans le monde précédent. Ouvre-en un."),
        bossesH=t("Eleven bosses stand in your way", "Onze boss te barrent la route"),
        bossesP=t("Each one guards the core that opens the next world, warns you before its worst blow, then leaves an opening.",
                  "Chacun garde le noyau qui ouvre le monde suivant, prévient avant son pire coup, puis laisse une ouverture."),
        lifeH=t("Fifty creatures, 160 attacks", "Cinquante créatures, 160 attaques"),
        lifeP=t("No two creatures fight alike. Each has its own attacks, drawn from what it is: the rat gnaws, the executioner passes its verdict, the watcher snuffs out the light.",
                "Aucune créature ne se bat comme une autre. Chacune a ses propres attaques, tirées de ce qu'elle est : le rat ronge, le bourreau rend son verdict, le guetteur éteint la lumière."),
        lifePicks=["executioner", "sky_harpooner", "shadow_mother", "hour_keeper", "mimic", "trench_eel"],
        galleryH=t("Inside the blocks", "Dans les blocs"),
        galleryP=t("Captures from the mod running in Minecraft 26.3.", "Captures du mod en jeu, sous Minecraft 26.3."),
        gallery=[],
        ctaH=t("Ready to shrink?", "Prêt à rétrécir ?"),
        ctaP=t("Minecraft 26.3, Fabric Loader 0.20 or newer, Fabric API, GeckoLib 5.5.7 and Java 25. In English, French, Spanish, German and Brazilian Portuguese.", "Minecraft 26.3, Fabric Loader 0.20 ou plus récent, Fabric API, GeckoLib 5.5.7 et Java 25. En anglais, français, espagnol, allemand et portugais du Brésil."),
        ctaBtn=t(f"Get version {VERSION}", f"Obtenir la version {VERSION}"),
        download=t(f"Download {VERSION}", f"Télécharger la {VERSION}"),
        desc=t("Matriochka, a Fabric mod for Minecraft 26.3: ten nested worlds, each sealed in a block, each with its own rule and boss.",
               "Matriochka, un mod Fabric pour Minecraft 26.3 : dix mondes emboîtés, chacun scellé dans un bloc, avec sa règle et son boss."),
    )
    worlds = dict(
        headImg=shot("head_worlds_banner"),
        lifeH=t("Who lives here", "Qui vit ici"),
        lifeP=t("Pick a creature to watch it move and use its own attacks. The boss guards the core that opens the next world.",
                "Choisis une créature pour la voir bouger et lancer ses propres attaques. Le boss garde le noyau qui ouvre le monde suivant."),
        codexH=t("Everything in this world", "Tout ce que contient ce monde"),
        codexP=t("Every item and block, how to make or find it, and what the world asks of you.",
                 "Chaque objet et chaque bloc, comment le fabriquer ou le trouver, et ce que le monde attend de toi."),
        cItems=t("Items", "Objets"), cBlocks=t("Blocks", "Blocs"), cQuests=t("Quests", "Quêtes"), cAch=t("Achievements", "Succès"),
        cMade=t("Made at", "Fabriqué à"), cFound=t("Found on", "Obtenu sur"), cGives=t("Mined, it gives", "Miné, il donne"),
        cMakes=t("makes", "donne"), sitesH=t("Structures and their loot", "Structures et leur butin"),
        sitesP=t("Eleven structures generate across every world, each with its own purpose. Here is where to look, what waits inside, and what the chests can hold.",
                 "Onze structures apparaissent dans chaque monde, chacune avec son rôle. Voici où chercher, ce qui t'attend dedans et ce que les coffres peuvent contenir."),
        lootH=t("What the chests can hold", "Ce que les coffres peuvent contenir"), cHidden=t("Hidden until you earn it", "Caché jusqu'à ce que tu l'obtiennes"),
        h=t("The ten worlds", "Les dix mondes"),
        lead=t("Each world is planted inside the one before it, and each one bends a rule you thought you knew. Numbers below come straight from the mod's code.",
               "Chaque monde est planté dans le précédent, et chacun tord une règle que tu croyais connaître. Les chiffres ci-dessous viennent directement du code du mod."),
        desc=t("The ten worlds of Matriochka: rules, the way into each, stations, recipes, creatures, bosses and structures.",
               "Les dix mondes de Matriochka : règles, l'accès à chacun, stations, recettes, créatures, boss et structures."),
        noShot=t("No clear capture of this world yet: its signature block stands in.", "Pas encore de capture nette de ce monde : son bloc emblématique la remplace."),
        inGame=t("in game", "en jeu"),
    )
    bestiary = dict(
        headImg=shot("head_bestiary_banner"),
        h=t("Bestiary", "Bestiaire"),
        lead=t("Fifty creatures, five per world. Health and damage already include the world's multiplier: health grows by 35% and damage by 20% with every world you go down.",
               "Cinquante créatures, cinq par monde. La vie et les dégâts incluent déjà le multiplicateur du monde : la vie augmente de 35 % et les dégâts de 20 % à chaque monde franchi."),
        nesting=t("Nesting creatures split open when they die and release a smaller, faster one. Elites guard the world's best drops.",
                  "Les créatures gigognes s'ouvrent à leur mort et libèrent une version plus petite et plus rapide. Les élites gardent les meilleurs butins du monde."),
        peoplesH=t("The peoples", "Les peuples"),
        peoplesP=t("Every world has its own people, with villages, traders and quest givers. How they greet you depends on your karma. On the Surface, the Doll Peddler wanders between villages.",
                   "Chaque monde a son peuple, avec ses villages, ses marchands et ses donneurs de quêtes. Leur accueil dépend de ton karma. Sur la Surface, le Colporteur de poupées erre de village en village."),
        peoples=[dict(id=pid, name=en if LANG == "en" else fr, world=w, worldName=world_name(w)) for pid, en, fr, w in C.PEOPLES],
        desc=t("Every creature of Matriochka with its health, damage, behaviour and drops.",
               "Toutes les créatures de Matriochka, avec leur vie, leurs dégâts, leur comportement et leur butin."),
        rare=t("rare", "rare"),
    )
    bosses = dict(
        headImg=shot("head_bosses_banner"),
        h=t("Bosses", "Boss"),
        lead=t("Eleven fights, each built the same way: an announcement you can read, a fast and dangerous attack, then an opening. Hit a boss during its opening and it takes 1.5 times the damage; outside of it, only three quarters. Every attack has its own animation: the boss shows the blow coming during the warning, strikes, then stays open and spent for exactly as long as the opening lasts. Each fight opens on a short cinematic: letterbox bars, the camera turning to the boss, its title card.",
               "Onze combats, tous construits pareil : une annonce lisible, une attaque rapide et dangereuse, puis une ouverture. Frappé pendant son ouverture, un boss subit 1,5 fois les dégâts ; en dehors, seulement les trois quarts. Chaque attaque a son animation : le boss montre le coup qui vient pendant l'annonce, frappe, puis reste ouvert et épuisé exactement le temps de l'ouverture. Chaque combat s'ouvre sur une courte cinématique : bandes noires, la caméra qui se tourne vers le boss, sa carte-titre."),
        tiers=[dict(tier=tr, warn=secs(tier_ticks(wn)[0] / 20), sig=secs(tier_ticks(wn)[0] * 2 / 20), opening=secs(tier_ticks(wn)[1] / 20))
               for tr, wn in ((t("Surface to World 3", "Surface au monde 3"), 0), (t("Worlds 4 to 6", "Mondes 4 à 6"), 4),
                              (t("Worlds 7 to 9", "Mondes 7 à 9"), 7), (t("World 10", "Monde 10"), 10))],
        tierCols=[t("Tier", "Palier"), t("Warning", "Annonce"), t("Signature warning", "Annonce signature"), t("Opening", "Ouverture")],
        tierNote=t("Bosses never take damage while changing phase. The Spore Queen's cocoon holds until its nodes are broken.", "Un boss ne prend aucun dégât pendant un changement de phase. Le cocon de la Reine des spores tient tant que ses nœuds ne sont pas brisés."),
        mp=[dict(p=p, mult="×" + fmt(round(1 + 0.6 * (p - 1), 1))) for p in (1, 2, 4, 8)],
        mpNote=t("Counted within 48 blocks when the boss wakes. Its attacks also come 5% faster per extra player, recounted during the fight. Everyone within 64 blocks at its death shares the victory.", "Compté dans un rayon de 48 blocs au réveil du boss. Ses attaques viennent aussi 5 % plus vite par joueur en plus, recompté pendant le combat. Tous ceux à moins de 64 blocs à sa mort partagent la victoire."),
        rewardNote=t(f"plus 100 souls and {SHELL_SHARDS} Shell Shards for every player in the fight", f"et 100 âmes et {SHELL_SHARDS} Éclats d'enveloppe pour chaque joueur présent au combat"),
        desc=t("The eleven bosses of Matriochka: health, attacks, phases, timings and rewards.", "Les onze boss de Matriochka : vie, attaques, phases, timings et récompenses."),
    )
    items = dict(
        h=t("Items and blocks", "Objets et blocs"),
        lead=t("Everything Matriochka adds, world by world: what it does, the station that makes it and the exact recipe, or the creature that drops it.",
               "Tout ce qu'ajoute Matriochka, monde par monde : ce que ça fait, la station qui le fabrique et la recette exacte, ou la créature qui le laisse."),
        search=t("Search an item or a block", "Chercher un objet ou un bloc"),
        all=t("Everything", "Tout"), onlyItems=t("Items", "Objets"), onlyBlocks=t("Blocks", "Blocs"), allWorlds=t("All worlds", "Tous les mondes"),
        none=t("Nothing matches that search.", "Rien ne correspond à cette recherche."),
        count=t("{n} shown", "{n} affichés"),
        made=t("Made at", "Fabriqué à"), found=t("Dropped by", "Laissé par"), gives=t("Mined, it gives", "Miné, il donne"),
        noRecipe=t("Not crafted at a station.", "Ne se fabrique pas à une station."),
        noCraft=t("No recipe: you find it.", "Pas de recette : il se trouve."),
        stationsH=t("The thirteen stations", "Les treize stations"),
        stationsP=t("Every world has its own. Pick one to see what it takes to build and what it makes.",
                    "Chaque monde a la sienne. Choisis-en une pour voir ce qu'il faut pour la construire et ce qu'elle fabrique."),
        aBlock=t("Block", "Bloc"), anItem=t("Item", "Objet"), world=t("World", "Monde"),
        statsH=t("Stats", "Caractéristiques"),
        statsNote=t("Base values: the class rolled when it is crafted raises them.", "Valeurs de base : la classe tirée à la fabrication les augmente."),
        recipeH=t("Recipe", "Recette"), usesH=t("Used to make", "Sert à fabriquer"), makesH=t("What it makes", "Ce qu'elle fabrique"),
        desc=t("Every item and block Matriochka adds, with its recipe drawn slot by slot and the station that makes it.",
               "Tous les objets et blocs qu'ajoute Matriochka, avec leur recette dessinée case par case et la station qui les fabrique."),
    )
    return dict(ui=ui, nav=nav, home=home, worlds=worlds, bestiary=bestiary, bosses=bosses, items=items, systems=build_systems(d), download=build_download())


def slot_label(slot):
    return {"armor": t("Armour", "Armures"), "weapon_armor": t("Weapons, armour", "Armes, armures"),
            "armor_weapon": t("Armour, light weapons", "Armures, armes légères"), "tool": t("Tools", "Outils")}[slot]


def talent_effect(effect, value):
    tmpl = C.TALENT_EFFECTS[effect][0 if LANG == "en" else 1]
    if "%s" not in tmpl:
        return tmpl.replace("%%", "%")
    v = round(value * 100, 1) if effect in C.TALENT_PERCENT else value
    return tmpl % fmt(float(v))


def boss_name(w):
    b = BOSS_OF.get(w) or next(b for b in C.BOSSES if b["world"] == 0)
    return b["en"] if LANG == "en" else b["fr"]


def mmss(secs_):
    return f"{secs_ // 60}:{secs_ % 60:02d}"


def build_talents():
    names = {cid: (en if LANG == "en" else fr) for (cid, en, fr, *_rest) in C.CLASSES}
    tree = [dict(cls=names[cid], branches=[dict(name=ben if LANG == "en" else bfr,
                                                talents=[dict(name=ten if LANG == "en" else tfr, eff=talent_effect(eff, val)) for (_tid, ten, tfr, eff, val) in tal])
                                           for (_bid, ben, bfr, tal) in branches])
            for cid, branches in C.TALENTS.items()]
    tiers = [dict(lv=str(i + 1), souls=str(so), shards=str(sh), gate=boss_name(g)) for i, (so, sh, g) in enumerate(C.TALENT_TIERS)]
    return tree, tiers


def build_gear():
    out = []
    for (gid, en, fr, w, kind, rarity, shape, een, efr, st, inputs) in C.REPLAY_GEAR:
        out.append(dict(tex=tex(gid), h=en if LANG == "en" else fr,
                        p=(een if LANG == "en" else efr) + " " + t(f"World {w}.", f"Monde {w}."),
                        inputs=ing(inputs), station=dict(tex=tex(st), name=name(st)), grid=grid(gid, st)))
    return out


def build_systems(d):
    _, cradle = recipe_for("soul_cradle")
    _, chance = recipe_for("chance_doll")
    _, thread = recipe_for("return_thread")
    rar = [("common", t("Common", "Commun")), ("rare", t("Rare", "Rare")), ("epic", t("Epic", "Épique")), ("legendary", t("Legendary", "Légendaire"))]
    karma = [("+50", "light2"), ("+25", "light1"), ("0", "neutral"), ("−25", "dark1"), ("−50", "dark2")]
    nq = len(C.QUESTS)
    nach = sum(len(v) for v in C.ACH.values())
    tree, ttiers = build_talents()
    ntal = sum(len(b[3]) for v in C.TALENTS.values() for b in v)
    ts = C.TRIAL_SCALE
    inv = C.INVASION
    return dict(
        tiles=[dict(id="survival", icon="heart", stat=t("3 layers", "3 couches"), line=t("A doll that breaks so you don't, and ways back in.", "Une poupée qui se brise à ta place, et des moyens de revenir.")),
               dict(id="souls", icon="sparkles", stat=t("-100 to +100", "-100 à +100"), line=t("Souls are the currency; karma decides how people treat you.", "Les âmes sont la monnaie ; le karma décide comment on te traite.")),
               dict(id="classes", icon="swords", stat=t(f"6 classes, {ntal} talents", f"6 classes, {ntal} talents"), line=t("Every crafted weapon and armour is born with a class; talents shape how you play it.", "Chaque arme et armure fabriquée naît avec une classe ; les talents décident de ta façon de la jouer.")),
               dict(id="workshop", icon="hammer", stat=t(f"{len(C.REPLAY_GEAR)} new pieces", f"{len(C.REPLAY_GEAR)} nouvelles pièces"), line=t("Weapons that behave like their world, and stations that run on hoppers.", "Des armes qui se comportent comme leur monde, et des stations qui tournent avec des entonnoirs.")),
               dict(id="nesting", icon="layers", stat=t("Inside everything", "Partout dedans"), line=t("Chests in chests, creatures in creatures, worlds in worlds.", "Des coffres dans des coffres, des créatures dans des créatures, des mondes dans des mondes.")),
               dict(id="groups", icon="users", stat=t("Up to 8 players", "Jusqu'à 8 joueurs"), line=t("Share worlds and bosses with your friends.", "Partage mondes et boss avec tes amis.")),
               dict(id="journal", icon="book-open", stat=t(f"{nq} quests", f"{nq} quêtes"), line=t("Objectives, quests, achievements and titles.", "Objectifs, quêtes, succès et titres.")),
               dict(id="trials", icon="hourglass", stat=t(f"{len(C.TRIALS)} trials", f"{len(C.TRIALS)} épreuves"), line=t("Races against the clock after the story, and events in the worlds.", "Des courses contre la montre après l'histoire, et des événements dans les mondes.")),
               dict(id="comfort", icon="eye", stat=t("5 languages", "5 langues"), line=t("Comfort options, cinematics, music that follows the fight, a light per world.", "Options de confort, cinématiques, une musique qui suit le combat, une lumière par monde."))],
        h=t("Systems", "Systèmes"), headImg=shot("head_systems_banner"),
        lead=t("What keeps you alive, what you trade for power, how your gear grows, and what waits after the story. Everything here works the same in solo and on a server.",
               "Ce qui te garde en vie, ce que tu échanges contre de la puissance, comment ton équipement grandit, et ce qui t'attend après l'histoire. Tout fonctionne pareil en solo et sur serveur."),
        desc=t("Doll of Life, death and respawn, souls and karma, gear classes and talents, new gear and station automation, groups, quests, trials, world events and comfort options in Matriochka.",
               "Poupée de vie, mort et réapparition, âmes et karma, classes et talents, nouvel équipement et automatisation des stations, groupes, quêtes, épreuves, événements des mondes et options de confort dans Matriochka."),
        onPage=t("On this page", "Sur cette page"),
        toc=[("survival", t("Survival", "Survie")), ("souls", t("Souls and karma", "Âmes et karma")), ("classes", t("Classes and talents", "Classes et talents")),
             ("workshop", t("Gear and stations", "Équipement et stations")), ("nesting", t("Nesting", "Gigogne")), ("groups", t("Groups", "Groupes")),
             ("journal", t("Journal", "Journal")), ("trials", t("Trials and events", "Épreuves et événements")), ("comfort", t("Comfort and atmosphere", "Confort et ambiance"))],
        survivalH=t("Survival", "Survie"),
        lifeDoll=dict(tex=tex("life_doll"), h=name("life_doll"), p=t("You carry a doll made of layers. It gets its first layer when the Spore Queen falls, a second after the Light Eater and a third after the Master of Seasons. Every boss you beat restores one layer, and the Soul Altar rebuilds one for 50 souls and 4 rare resources of the world you are in.",
                                                                    "Tu portes une poupée faite de couches. Elle reçoit sa première couche à la chute de la Reine des spores, une deuxième après le Mangeur de lumière et une troisième après le Maître des saisons. Chaque boss vaincu restaure une couche, et l'Autel des âmes en reconstruit une pour 50 âmes et 4 ressources rares du monde où tu es.")),
        deathH=t("When you die", "Quand tu meurs"),
        death=[t("If your Doll of Life has a layer left, it breaks and you get back up on the spot. A doll can save you at most once a minute.",
                 "Si ta Poupée de vie a encore une couche, elle se brise et tu te relèves sur place. Une poupée peut te sauver au plus une fois par minute."),
               t("Otherwise you die, and a death chest keeps your inventory where you fell. It never despawns; inside a boss arena it waits at the entrance.",
                 "Sinon tu meurs, et un coffre de mort garde ton inventaire là où tu es tombé. Il ne disparaît jamais ; dans une arène de boss, il t'attend à l'entrée."),
               t("If you placed a charged Soul Cradle in that world, you wake up next to it.", "Si tu as posé un Berceau d'âme chargé dans ce monde, tu te réveilles à côté."),
               t("If not, you are sent back outside, to your usual spawn point.", "Sinon, tu es renvoyé dehors, à ton point de réapparition habituel.")],
        features=[
            dict(tex=tex("soul_cradle"), h=name("soul_cradle"), p=t("A small painted cradle that lets you respawn inside a world. It holds 3 charges; feed it one resource from that world and 5 souls to add another. One active cradle per player and per world.",
                                                                  "Un petit berceau en bois peint qui te permet de réapparaître dans un monde. Il contient 3 charges ; donne-lui une ressource de ce monde et 5 âmes pour en ajouter une. Un seul berceau actif par joueur et par monde."),
                 inputs=ing(cradle["inputs"]) if cradle else []),
            dict(tex=tex("return_thread"), h=name("return_thread"), p=t("Pulls you back to the World Block. You can also simply walk back onto the Threshold where you arrived.", "Te ramène au Bloc-monde. Tu peux aussi simplement revenir sur le Seuil où tu es arrivé."),
                 inputs=ing(thread["inputs"]) if thread else []),
            dict(tex=tex("cracked_doll"), h=t("A broken World Block", "Un Bloc-monde cassé"), p=t("Break a World Block and everyone inside is pushed out safely. The block becomes a Cracked Doll tied to that exact world: set it down again and the world comes back with its bases and chests, unstable for 20 minutes. It is also how you move a world.",
                                                                                               "Casse un Bloc-monde et tous ceux qui sont dedans sont expulsés sans dommage. Le bloc devient une Poupée fêlée liée à ce monde précis : repose-la et le monde revient avec ses bases et ses coffres, instable pendant 20 minutes. C'est aussi comme ça qu'on déplace un monde."), inputs=[])],
        soulsH=t("Souls and karma", "Âmes et karma"),
        soulsLead=t("Every item carries a soul whose weight depends on its rarity. Put it on the Soul Altar and choose, for good: purify it to free the soul and gain karma, or devour it to absorb the soul and lose karma. Either way you keep the souls, which pay for class upgrades, talents, cradle charges and doll layers. Structure chests also keep Soul Shards (5 souls) and Soul Vessels (20), about 10 souls a chest.",
                    "Chaque objet porte une âme dont le poids dépend de sa rareté. Pose-le sur l'Autel des âmes et choisis, définitivement : purifie-le pour libérer l'âme et gagner du karma, ou dévore-le pour absorber l'âme et perdre du karma. Dans les deux cas tu gardes les âmes, qui paient les améliorations de classe, les talents, les charges de berceau et les couches de poupée. Les coffres des structures gardent aussi des Éclats d'âme (5 âmes) et des Vaisseaux d'âme (20), environ 10 âmes par coffre."),
        rarCols=[t("Rarity", "Rareté"), t("Souls", "Âmes")],
        rarity=[dict(k=l, v=str(C.RARITY_SOUL[k])) for k, l in rar] + [dict(k=t("Any boss", "Un boss"), v="100")],
        karmaNote=t("Karma runs from −100 to +100. An item gives one point of karma per 10 souls, and less each time you repeat the same offering. Quests with a choice move it by 5 or 10.",
                    "Le karma va de −100 à +100. Un objet rapporte un point de karma par tranche de 10 âmes, et de moins en moins si tu répètes la même offrande. Les quêtes à choix le déplacent de 5 ou 10."),
        altarShot=dict(src=shot("gui_station_soul_altar"), caption=t("The Soul Altar", "L'Autel des âmes")),
        karmaH=t("What karma changes", "Ce que change le karma"),
        karma=[dict(v=v, p=d["journal.matriochka.karma." + k]) for v, k in karma],
        karmaEnd=t("At ±100, karma also tilts the variants of the worlds you open, and it decides between two of the three endings: seal the creature away, or absorb its power.",
                   "À ±100, le karma oriente aussi les variantes des mondes que tu ouvres, et il départage deux des trois fins : sceller de nouveau la créature, ou absorber son pouvoir."),
        classesH=t("Gear classes", "Classes d'équipement"),
        classesLead=t("Every weapon, tool and armour piece gets a random class when it is crafted. The Class Table raises its level with souls and Shell Shards; your progression caps how far you can go.",
                      "Chaque arme, outil ou pièce d'armure reçoit une classe au hasard à sa fabrication. La Table de classe monte son niveau avec des âmes et des Éclats d'enveloppe ; ta progression limite jusqu'où tu peux aller."),
        clsCols=[t("Class", "Classe"), t("Bonuses", "Bonus"), t("Found on", "Sur")],
        classes=[dict(name=en if LANG == "en" else fr, bonus=den if LANG == "en" else dfr, slot=slot_label(slot)) for (cid, en, fr, slot, den, dfr) in C.CLASSES],
        upH=t("Upgrading", "Améliorer"), upCols=[t("Level", "Niveau"), t("Total bonus", "Bonus total"), t("Souls", "Âmes")],
        up=[dict(lv=str(lv), bonus="+" + pct(b), souls=str(c)) for lv, b, c in ((2, 10, 10), (3, 20, 30), (4, 35, 90), (5, 50, 270))],
        upNote=t(f"Level 1 to 5 costs 400 souls and 6 Shell Shards per piece (1, 1, 2, 2). Every boss leaves {SHELL_SHARDS} Shell Shards to each player who fought it: enough to bring its world's weapon to the cap.",
                 f"Du niveau 1 au niveau 5 : 400 âmes et 6 Éclats d'enveloppe par pièce (1, 1, 2, 2). Chaque boss laisse {SHELL_SHARDS} Éclats d'enveloppe à chaque joueur qui l'a combattu : de quoi monter l'arme de son monde au plafond."),
        capH=t("Level cap", "Niveau maximal"), capCols=[t("Progression", "Progression"), t("Max level", "Niveau max")],
        cap=[dict(k=t(f"World {w} done", f"Monde {w} terminé"), v=str(lv)) for w, lv in ((2, 2), (4, 3), (6, 4), (8, 5))],
        chance=dict(tex=tex("chance_doll"), h=name("chance_doll"), p=t("Rerolls an item into a different class it can hold, and keeps its level. The first reroll costs 20 souls, and the price doubles each time on the same item: 20, 40, 80, 160.",
                                                                       "Relance un objet vers une autre classe compatible, en gardant son niveau. Le premier changement coûte 20 âmes, et le prix double à chaque fois sur le même objet : 20, 40, 80, 160."),
                    inputs=ing(chance["inputs"]) if chance else []),
        classShot=dict(src=shot("gui_station_class_table"), caption=t("The Class Table", "La Table de classe")),
        talentsH=t("Talents", "Talents"),
        talentsLead=t(f"The Class Table also holds a cabinet of talent trees: three branches of four talents for each of the six classes, {ntal} in all. A branch is learnt in order; the first two talents cost souls, the last two souls and Shell Shards, and each tier opens as your group beats deeper bosses. A class's talents act while you wear or hold its gear (any tool counts for the Prospector).",
                      f"La Table de classe abrite aussi un cabinet d'arbres de talents : trois branches de quatre talents pour chacune des six classes, {ntal} en tout. Une branche s'apprend dans l'ordre ; les deux premiers talents coûtent des âmes, les deux derniers des âmes et des Éclats d'enveloppe, et chaque palier s'ouvre quand ton groupe bat des boss plus profonds. Les talents d'une classe agissent tant que tu portes ou tiens son équipement (n'importe quel outil compte pour le Prospecteur)."),
        talentCols=[t("Tier", "Rang"), t("Souls", "Âmes"), t("Shell Shards", "Éclats d'enveloppe"), t("Opens after", "S'ouvre après")],
        talentTiers=ttiers,
        talentTree=tree,
        talentNote=t(f"The Forget button unlearns every talent and gives back {int(C.TALENT_REFUND * 100)}% of the souls spent, never the shards.",
                     f"Le bouton Oublier désapprend tous les talents et rend {int(C.TALENT_REFUND * 100)} % des âmes dépensées, jamais les éclats."),
        gearH=t("New gear", "Nouvel équipement"),
        gearLead=t(f"{len(C.REPLAY_GEAR)} weapons and tools that behave like the world they come from, each crafted at its world's station and drawn by hand. They are born with a class like any other gear.",
                   f"{len(C.REPLAY_GEAR)} armes et outils qui se comportent comme le monde d'où ils viennent, chacun fabriqué à la station de son monde et dessiné à la main. Ils naissent avec une classe comme tout autre équipement."),
        gear=build_gear(),
        autoH=t("Stations on hoppers", "Des stations sur entonnoirs"),
        auto=[t("Every station with recipes works with hoppers. It keeps one recipe: the last one crafted there by hand, or the one picked with the small gilded funnel that shows on a recipe under the cursor.",
                "Chaque station à recettes fonctionne avec des entonnoirs. Elle garde une recette : la dernière fabriquée à la main, ou celle choisie avec le petit entonnoir doré qui apparaît sur une recette au survol."),
              t("Ingredients go in from the top and the sides, each into its own slots; anything else is refused. The result comes out from below, and a comparator reads how full the station is.",
                "Les ingrédients entrent par le dessus et les côtés, chacun dans ses cases ; tout le reste est refusé. Le résultat sort par le dessous, et un comparateur lit le remplissage de la station."),
              t("Each station keeps its condition: heat for the Ash Foundry, a charge for the Lightning Forge (lightning, or Storm Essence in its fuel slot), darkness, deep water, dawn and dusk. The Spore Vat waits for a ripe brew, and the Jailer's Table makes one batch per lock pattern entered.",
                "Chaque station garde sa condition : la chaleur pour la Fonderie de cendre, une charge pour la Forge-éclair (la foudre, ou de l'Essence d'orage dans sa case de combustible), l'obscurité, l'eau profonde, l'aube et le crépuscule. La Cuve à spores attend une infusion mûre, et la Table du geôlier fait une fournée par motif de serrure entré."),
              t("The Soul Altar and the Class Table stay manual. Breaking a station drops its buffer.", "L'Autel des âmes et la Table de classe restent manuels. Casser une station fait tomber sa réserve.")],
        autoShot=dict(src=shot("sys_stations_night"), caption=t("The stations' lit faces glow in the dark", "Les faces allumées des stations luisent dans le noir")),
        shake=dict(tex=tex("doll_mallet"), h=t("Shake a World Block", "Secouer un Bloc-monde"),
                   p=t("From outside, a player of the owning group can sneak and use the World Block with empty hands to help those inside: creatures stunned and thrown off their feet for 3 seconds, a boss staggered and open. Strike it with the Doll Mallet instead and the world quakes, loose blocks falling over their heads. One shake per world every 30 seconds.",
                       "De dehors, un joueur du groupe propriétaire peut s'accroupir et utiliser le Bloc-monde à mains nues pour aider ceux qui sont dedans : créatures étourdies et jetées à terre pendant 3 secondes, boss ébranlé et ouvert. Frappe-le plutôt au Maillet de poupée et le monde tremble, des blocs tombant sur leurs têtes. Une secousse par monde toutes les 30 secondes."),
                   inputs=[]),
        nestingH=t("Things inside things", "Des choses dans des choses"),
        nestingLead=t("The name is the rule: something can always hold something else. These systems unlock as the story goes on.", "Le nom est la règle : une chose peut toujours en contenir une autre. Ces systèmes se débloquent au fil de l'histoire."),
        nestCols=[t("System", "Système"), t("Effect", "Effet"), t("Unlocked", "Déblocage")],
        nest=[dict(a=a, b=b, c=c) for a, b, c in [
            (t("Doll of Life", "Poupée de vie"), t("Each layer survives one death", "Chaque couche survit à une mort"), t("Worlds 1, 5, 8", "Mondes 1, 5, 8")),
            (t("Nesting chests", "Coffres gigognes"), t("Three sizes: a chest holds the smaller ones and sorts items into them", "Trois tailles : un coffre contient les plus petits et y range les objets"), t("World 2", "Monde 2")),
            (t("Nesting creatures", "Créatures gigognes"), t("A defeated mob releases a smaller one", "Un mob vaincu en libère un plus petit"), t("World 2", "Monde 2")),
            (t("Refuge doll", "Poupée-refuge"), t("A pocket base for your group, that grows after Worlds 5, 7 and 9", "Une base de poche pour ton groupe, qui s'agrandit après les mondes 5, 7 et 9"), t("World 3", "Monde 3")),
            (t("Layered armour", "Armures à couches"), t("Lacquer Layers laid on armour: when the outer one breaks, the next takes over", "Des Couches laquées posées sur l'armure : quand celle du dessus casse, la suivante prend le relais"), t("World 4", "Monde 4")),
            (t("The final boss", "Le boss final"), t("Ten shells, one per world", "Dix enveloppes, une par monde"), t("World 10", "Monde 10")),
            (t("Hidden dolls", "Poupées cachées"), t("Nested in order, the ten open World 0, the smallest doll", "Emboîtées dans l'ordre, les dix ouvrent le monde 0, la plus petite poupée"), t("After World 10", "Après le monde 10"))]],
        gatesH=t("Gates", "Verrous"),
        gates=[t("Enchanting, anvils and the Nether open after World 2.", "Enchantements, enclumes et Nether s'ouvrent après le monde 2."),
               t("Diamonds come back in World 5: four Diamond Fragments make one at the Dark Altar. Until then villagers keep their diamond trades aside.", "Le diamant revient dans le monde 5 : quatre Fragments de diamant en donnent un à l'Autel obscur. D'ici là, les villageois gardent de côté leurs échanges de diamant."),
               t("Elytra stay grounded in Worlds 4, 6 and 9 until World 8 is done.", "Les élytres restent clouées au sol dans les mondes 4, 6 et 9 tant que le monde 8 n'est pas terminé."),
               t("The End opens after World 8.", "L'End s'ouvre après le monde 8.")],
        groupsH=t("Groups and servers", "Groupes et serveurs"),
        groupsLead=t("A player alone is a group of one. Worlds, progression and permissions belong to the group: up to eight players by default. Each group gets its own 3,000 by 3,000 block parcel in every world, walled off from the others, and a World Block can only be used by its group.",
                     "Un joueur seul forme un groupe d'une personne. Les mondes, la progression et les permissions appartiennent au groupe : jusqu'à huit joueurs par défaut. Chaque groupe reçoit sa propre parcelle de 3 000 sur 3 000 blocs dans chaque monde, séparée des autres, et un Bloc-monde ne sert qu'à son groupe."),
        cmds=[dict(c=c, d=x) for c, x in [
            ("/matriochka group info", t("Your group, its members and defeated bosses", "Ton groupe, ses membres et ses boss vaincus")),
            ("/matriochka group invite <player>", t("Leader: invite a player into your group", "Chef : inviter un joueur dans ton groupe")),
            ("/matriochka group join", t("Accept the pending invitation", "Accepter l'invitation en attente")),
            ("/matriochka group leave", t("Leave your group", "Quitter ton groupe")),
            ("/matriochka group kick <player>", t("Leader: send a member out", "Chef : renvoyer un membre")),
            ("/matriochka group transfer <player>", t("Leader: hand over the lead", "Chef : passer la main")),
            ("/matriochka group disband", t("Leader: dissolve the group", "Chef : dissoudre le groupe")),
            ("/matriochka karma show", t("Your karma and souls", "Ton karma et tes âmes"))]],
        serverNote=t("The mod runs on the server and on every client. All rules, damage and rewards are decided by the server; nothing needs an online account or service.",
                     "Le mod s'installe sur le serveur et sur chaque client. Règles, dégâts et récompenses sont décidés par le serveur ; aucun compte ni service en ligne n'est nécessaire."),
        journalH=t("The Journal, quests and achievements", "Le Journal, les quêtes et les succès"),
        journalLead=t(f"The Artisan's Scroll arrives on your first login and turns into the Journal when the Guardian falls. Its tabs track your objective, quests, karma and worlds. There are {nq} optional quests (4 on the Surface, 6 per world and 6 on the paths of karma) and {nach} achievements, 10 per world, two of them hidden. Fifty Journal pages, read in the Pages tab, and ten hidden dolls are scattered through the worlds; nest the dolls in order and something smaller opens. After the last boss, your karma chooses your ending, and a New Cycle starts the worlds over, stronger.",
                      f"Le Parchemin de l'artisan arrive à ta première connexion et devient le Journal quand le Gardien tombe. Ses onglets suivent ton objectif, tes quêtes, ton karma et tes mondes. Il y a {nq} quêtes facultatives (4 sur la Surface, 6 par monde et 6 sur les chemins du karma) et {nach} succès, 10 par monde dont deux cachés. Cinquante pages du Journal, à lire dans l'onglet Pages, et dix poupées cachées sont dispersées dans les mondes ; emboîte les poupées dans l'ordre et quelque chose de plus petit s'ouvre. Après le dernier boss, ton karma choisit ta fin, et un Nouveau Cycle rouvre les mondes, plus forts."),
        journalShots=[dict(src=shot(k), caption=c) for k, c in (("gui_journal_0", t("The Journal's objective tab", "L'onglet objectif du Journal")), ("gui_journal_1", t("Quests", "Les quêtes"))) if shot(k)],
        firstSteps=dict(tex=tex("artisan_scroll") or tex("journal"), h=t("First steps", "Premiers pas"),
                        p=t("Until you enter World 1, a small lacquered card under the HUD plaque shows the next of ten steps, from reading the Scroll to planting the first Seed, with its item, a short hint and a compass needle toward the nearest Guardian's Sanctuary. Each step is detected from what you really do, and the Guide button on the Scroll or the Journal hides it.",
                            "Jusqu'à ton entrée dans le monde 1, une petite carte laquée sous la plaque du HUD montre la prochaine des dix étapes, de la lecture du Parchemin à la plantation de la première Graine, avec son objet, un court indice et une aiguille de boussole vers le Sanctuaire du Gardien le plus proche. Chaque étape est détectée d'après ce que tu fais vraiment, et le bouton Guide du Parchemin ou du Journal la masque."),
                        inputs=[]),
        titlesH=t("Titles you can earn", "Titres à gagner"),
        titles=[v for k, v in d.items() if k.startswith("title.matriochka.")],
        titlesNote=t("Titles are worn from the Trials book, quest titles included.", "Les titres se portent depuis le livre des Épreuves, titres de quêtes compris."),
        trialsH=t("Trials", "Épreuves"),
        trialsLead=t("Once you have seen an ending, the Trials open: a rush per world (two waves of its creatures, the second led by its elites, then its boss) and the Gauntlet of the eleven bosses, fought against the clock on a lacquered stage inside the Refuge doll, painted for each world. Open them from the Journal's Objective page, a Trial Altar or /matriochka trials start. Falling carries you out instead of killing you.",
                     "Une fois une fin vue, les Épreuves s'ouvrent : une course par monde (deux vagues de ses créatures, la seconde menée par ses élites, puis son boss) et l'Épreuve des onze boss, combattues contre la montre sur une scène laquée dans la poupée-refuge, peinte pour chaque monde. Ouvre-les depuis la page Objectif du Journal, un Autel des épreuves ou /matriochka trials start. Une chute te ramène dehors au lieu de te tuer."),
        trialFacts=[dict(k=t("Trial bosses", "Boss d'épreuve"), v=f"×{fmt(ts['health'])} / ×{fmt(ts['damage'])}", d=t(f"health and damage, ×{fmt(ts['gauntlet_health'])} / ×{fmt(ts['gauntlet_damage'])} in the Gauntlet; always mutated, no introduction, no story reward", f"vie et dégâts, ×{fmt(ts['gauntlet_health'])} / ×{fmt(ts['gauntlet_damage'])} dans l'Épreuve des onze ; toujours mutés, sans introduction ni récompense d'histoire")),
                    dict(k=t("Every clear", "Chaque victoire"), v=str(C.TRIAL_SOULS), d=t("souls", "âmes")),
                    dict(k=t("First win", "Première victoire"), v=t("Trophy", "Trophée"), d=t("its Trophy Doll and a title", "sa Poupée-trophée et un titre")),
                    dict(k=t("Under par", "Sous le temps de référence"), v=t("Swift Hand", "Main preste"), d=t("a title for beating the par time", "un titre pour battre le temps de référence"))],
        trialCols=[t("Trial", "Épreuve"), t("Par time", "Temps de référence")],
        trialList=[dict(name=t(*C.TRIAL_NAMES[k]), tex=tex(f"trophy_doll_{k if k == 'gauntlet' else w}"), par=mmss(par)) for k, w, par in C.TRIALS],
        boardH=t("The board", "Le tableau"),
        board=t("A clock on the HUD runs green while you are under par. Best times are kept per player and per group, and the server keeps a board of the ten best groups for every trial, in the Trials book and with /matriochka trials top.",
                "Une horloge sur le HUD reste verte tant que tu es sous le temps de référence. Les meilleurs temps sont gardés par joueur et par groupe, et le serveur tient un tableau des dix meilleurs groupes pour chaque épreuve, dans le livre des Épreuves et avec /matriochka trials top."),
        eventsH=t("World events", "Événements des mondes"),
        eventsLead=t("While you are in a world, now and then something happens around you. A boss bar follows each event. Never in peaceful; operators can start one with /matriochka event.",
                     "Pendant que tu es dans un monde, il se passe de temps en temps quelque chose autour de toi. Une barre de boss suit chaque événement. Jamais en paisible ; les opérateurs peuvent en lancer un avec /matriochka event."),
        events=[dict(icon="swords", h=t("Invasion", "Invasion"), p=t(f"{inv['waves']} waves of the world's creatures, more for every player nearby; the last is led by a glowing warlord. A reward chest waits at the end.",
                                                                   f"{inv['waves']} vagues de créatures du monde, plus nombreuses pour chaque joueur proche ; la dernière est menée par un seigneur de guerre luisant. Un coffre de récompense attend à la fin.")),
                dict(icon="flame", h=t("Surge", "Poussée"), p=t(f"The world's rule grows {'twice' if C.SURGE['strength'] == 2 else fmt(C.SURGE['strength']) + ' times'} as strong for {C.SURGE['duration'] // 60} minutes, with its own effect and particles. Ride it out for {C.SURGE['souls']} souls.",
                                                              f"La règle du monde devient {fmt(C.SURGE['strength'])} fois plus forte pendant {C.SURGE['duration'] // 60} minutes, avec son effet et ses particules. Tiens bon pour {C.SURGE['souls']} âmes.")),
                dict(icon="package", h=t("Travelling merchant", "Marchand itinérant"), p=t("A wanderer of the world's people sets up for a while, with special trades: its world's new gear, Shell Shards, rare pieces.",
                                                                                           "Un vagabond du peuple du monde s'installe un moment, avec des échanges spéciaux : le nouvel équipement de son monde, des Éclats d'enveloppe, des pièces rares."))],
        surges=[dict(w=w, name=en if LANG == "en" else fr, p=pen if LANG == "en" else pfr) for w, (_sid, en, fr, pen, pfr) in sorted(C.SURGES.items())],
        eventsNote=t("Frequency and weights live in config/matriochka.json: worldEvents, worldEventChance, worldEventCooldown and the three weights.",
                     "La fréquence et les poids se règlent dans config/matriochka.json : worldEvents, worldEventChance, worldEventCooldown et les trois poids."),
        comfortLead=t("Opened from the Journal's Comfort button (or from Mod Menu), saved per player in config/matriochka-client.json.",
                      "Ouvertes depuis le bouton Confort du Journal (ou depuis Mod Menu), enregistrées par joueur dans config/matriochka-client.json."),
        comfortH=t("Comfort options", "Options de confort"),
        comfort=[t("Screen shake strength and flashes", "Force des secousses d'écran et des flashs"),
                 t("Soft effects: no Nausea or Darkness, a gentle tint instead; the server skips those effects for you", "Effets doux : ni Nausée ni Obscurité, une teinte légère à la place ; le serveur te les épargne"),
                 t("Cinematics on or off", "Cinématiques activées ou non"),
                 t("Large subtitles for boss attacks", "Grands sous-titres pour les attaques de boss"),
                 t("Fewer particles", "Moins de particules"),
                 t("Colour-blind patterns on the world gauges", "Motifs pour daltoniens sur les jauges des mondes"),
                 t("HUD plaque size and corner", "Taille et coin de la plaque du HUD"),
                 t("A volume per kind of music", "Un volume par type de musique")],
        comfortShot=dict(src=shot("sys_comfort"), caption=t("The comfort options", "Les options de confort")),
        cineH=t("Cinematics and music", "Cinématiques et musique"),
        cine=[t("Boss introductions: letterbox bars, the camera turning toward the boss with a slow push-in, and a framed title card.", "Introductions de boss : bandes noires, la caméra qui se tourne vers le boss en avançant lentement, et une carte-titre encadrée."),
              t("A title card the first time you enter each world, with its rule medallion and a line about its law.", "Une carte-titre à ta première entrée dans chaque monde, avec le médaillon de sa règle et une ligne sur sa loi."),
              t("Phase breaks freeze the frame with a flash and the shell's number; heavy blows and moving ground shake the camera.", "Les changements de phase figent l'image avec un flash et le numéro de l'enveloppe ; les coups lourds et le sol qui bouge secouent la caméra."),
              t("Adaptive music: a danger theme while creatures hunt you, boss themes, a heartbeat at low health or breath, and stings for a structure, a Journal page or a quest. Themes fade into one another.", "Musique adaptative : un thème de danger quand des créatures te traquent, les thèmes de boss, un battement de cœur à faible vie ou souffle, et des ponctuations pour une structure, une page du Journal ou une quête. Les thèmes se fondent l'un dans l'autre.")],
        cineShots=[dict(src=shot(k), caption=c) for k, c in (("sys_boss_intro", t("A boss introduction", "Une introduction de boss")), ("sys_world_card", t("Entering World 1", "L'entrée dans le monde 1"))) if shot(k)],
        atmosH=t("A light for every world", "Une lumière pour chaque monde"),
        atmos=t("Every world has its own light, fog and particles: spore haze, falling embers, cold dust, a storm sky, near-black fog where a lantern reads across a cavern, an inverted pastel sky, deep blue water, light tinted by the season, rust haze, warm workshop light, and World 0's red lacquer dusk. Items, blocks and stations are hand-painted in the vanilla style, and their lit faces glow in the dark. Matriochka HD, an optional 32 x 32 resource pack, is attached to every release; Iris shader packs work through vanilla light.",
                "Chaque monde a sa lumière, son brouillard et ses particules : brume de spores, braises qui tombent, poussière froide, ciel d'orage, brouillard presque noir où une lanterne porte à travers une caverne, ciel pastel inversé, eau d'un bleu profond, lumière teintée par la saison, brume de rouille, lumière chaude de l'atelier, et le crépuscule de laque rouge du monde 0. Objets, blocs et stations sont peints à la main dans le style vanilla, et leurs faces allumées luisent dans le noir. Matriochka HD, un pack de ressources facultatif en 32 x 32, est joint à chaque version ; les shaders Iris fonctionnent avec la lumière vanilla."),
        atmosShots=[dict(src=shot(k), caption=c) for k, c in (("sys_atmos_w2", world_name(2)), ("sys_atmos_w8", t(f"Autumn in {world_name(8)}", f"L'automne : {world_name(8)}"))) if shot(k)],
        langH=t("Five languages", "Cinq langues"),
        lang=t("English, French, Spanish, German and Brazilian Portuguese: every name, the interface, quests, achievements, the Scroll, the fifty Journal pages, endings, credits and subtitles. A string missing from a language shows in English, and labels shrink to fit when a language runs longer.",
               "Anglais, français, espagnol, allemand et portugais du Brésil : chaque nom, l'interface, les quêtes, les succès, le Parchemin, les cinquante pages du Journal, les fins, le générique et les sous-titres. Un texte manquant dans une langue s'affiche en anglais, et les libellés rétrécissent quand une langue est plus longue."),
    )


def build_download():
    return dict(
        h=t("Download", "Télécharger"), headImg=shot("head_download_banner"),
        lead=t(f"Version {VERSION} for Minecraft 26.3 on Fabric. Install it on the client to play solo, and on both server and clients to play together.",
               f"Version {VERSION} pour Minecraft 26.3 sous Fabric. Installe-la côté client pour jouer en solo, et sur le serveur et chaque client pour jouer ensemble."),
        desc=t("Download Matriochka for Minecraft 26.3 on Fabric: requirements, installation, Lunar Client and server configuration.",
               "Télécharger Matriochka pour Minecraft 26.3 sous Fabric : prérequis, installation, Lunar Client et configuration serveur."),
        sources=[dict(name="GitHub", note=t("Releases, changelog and source", "Versions, changements et code source"), href=RELEASES),
                 dict(name="Matriochka Pack", note=t("Modrinth modpack (.mrpack), normal and hard, attached to each release", "Modpack Modrinth (.mrpack), normal et difficile, joint à chaque version"), href=RELEASES),
                 dict(name="Matriochka HD", note=t("Optional 32 x 32 resource pack, attached to each release", "Pack de ressources facultatif en 32 x 32, joint à chaque version"), href=RELEASES),
                 dict(name="Modrinth", note=t("Coming soon", "Bientôt disponible"), href=None),
                 dict(name="CurseForge", note=t("Coming soon", "Bientôt disponible"), href=None)],
        reqH=t("Requirements", "Prérequis"),
        reqs=[dict(n=n, v=v, s=s) for n, v, s in [
            ("Minecraft", "26.3", t("Java Edition", "Édition Java")),
            ("Fabric Loader", "0.20+", t("Install it for 26.3 with the Fabric installer", "À installer pour la 26.3 avec l'installeur Fabric")),
            ("Fabric API", "0.165.2+", t("Built for 26.3, goes in the mods folder", "Pour la 26.3, dans le dossier mods")),
            ("GeckoLib", "5.5.7", t("Animated models of bosses and creatures", "Modèles animés des boss et créatures")),
            ("Java", "25", t("Bundled with the official launcher", "Fourni avec le launcher officiel")),
            ("Just Enough Items", t("optional", "facultatif"), t("Recipe pages for every station", "Pages de recettes pour chaque station")),
            ("Mod Menu", t("optional", "facultatif"), t("Summary, links and a shortcut to the comfort options", "Résumé, liens et accès direct aux options de confort"))]],
        installH=t("Installing", "Installation"),
        steps=[t("Install Fabric Loader for Minecraft 26.3.", "Installe Fabric Loader pour Minecraft 26.3."),
               t(f"Download matriochka-{VERSION}+26.3.jar from the GitHub releases.", f"Télécharge matriochka-{VERSION}+26.3.jar depuis les versions GitHub."),
               t("Put it in your mods folder with Fabric API and GeckoLib.", "Place-le dans ton dossier mods avec Fabric API et GeckoLib."),
               t("Launch the Fabric profile and create a new world. The Artisan's Scroll is waiting in your inventory.", "Lance le profil Fabric et crée un nouveau monde. Le Parchemin de l'artisan t'attend dans l'inventaire.")],
        lunarH="Lunar Client",
        lunar=t("Matriochka is built on Fabric so that it can run on Lunar Client, whose mod loading relies on Fabric. Support for Minecraft 26.3 together with GeckoLib is still being confirmed there: if the mod does not load, play it with the official launcher or Prism Launcher on a Fabric profile in the meantime.",
                "Matriochka repose sur Fabric pour pouvoir tourner sur Lunar Client, dont le chargement de mods s'appuie sur Fabric. La prise en charge de Minecraft 26.3 avec GeckoLib y est encore en cours de vérification : si le mod ne se charge pas, joue en attendant avec le launcher officiel ou Prism Launcher sur un profil Fabric."),
        packH=t("The Matriochka Pack", "Le Matriochka Pack"),
        pack=t("Rather not gather the mods yourself? Every GitHub release carries a Modrinth modpack (.mrpack) for Prism Launcher, the Modrinth App or any launcher that reads the format: the mod, Fabric API, GeckoLib, Just Enough Items (optional) and client performance mods (Sodium, Lithium, FerriteCore, Entity Culling, ImmediatelyFast, Dynamic FPS, Krypton, Mod Menu, Iris as an option), in a normal and a hard (nightmare) version.",
               "Pas envie de rassembler les mods toi-même ? Chaque version GitHub contient un modpack Modrinth (.mrpack) pour Prism Launcher, l'application Modrinth ou tout launcher qui lit ce format : le mod, Fabric API, GeckoLib, Just Enough Items (facultatif) et des mods de performance (Sodium, Lithium, FerriteCore, Entity Culling, ImmediatelyFast, Dynamic FPS, Krypton, Mod Menu, Iris en option), en version normale et difficile (nightmare)."),
        compatH=t("Works with", "Compatible avec"),
        compat=t("Checked with Sodium, Iris (through vanilla light: emissive faces, full-bright particles), Xaero's Minimap and World Map, JourneyMap, VoxelMap and Traveler's Backpack for 26.3: no conflict found, and no backpack way around the progression. Xaero's cave view and entity radar switch off in the Lightless Deep, where they would show what the darkness hides, and come back when you leave.",
                 "Vérifié avec Sodium, Iris (par la lumière vanilla : faces émissives, particules pleinement lumineuses), Xaero's Minimap et World Map, JourneyMap, VoxelMap et Traveler's Backpack pour la 26.3 : aucun conflit, et aucun moyen de contourner la progression avec un sac à dos. La vue des grottes et le radar de Xaero s'éteignent dans la Profondeur sans lumière, où ils montreraient ce que l'obscurité cache, et reviennent quand tu en sors."),
        langsH=t("Languages", "Langues"),
        langs=t("English, French, Spanish, German and Brazilian Portuguese, following the game's language setting.", "Anglais, français, espagnol, allemand et portugais du Brésil, selon la langue choisie dans le jeu."),
        wikiH=t("Wiki", "Wiki"), wiki=t("Recipes, step-by-step guides and answers to common questions live on the GitHub wiki.", "Recettes, guides pas à pas et réponses aux questions courantes sont sur le wiki GitHub."),
        wikiBtn=t("Open the wiki", "Ouvrir le wiki"),
        earlyH=t("Early version", "Version précoce"),
        early=t("Names, numbers and balance can still change between versions. Back up your worlds before updating, and report anything odd on the issue tracker.", "Les noms, les chiffres et l'équilibrage peuvent encore changer d'une version à l'autre. Sauvegarde tes mondes avant de mettre à jour, et signale tout comportement étrange sur le suivi des tickets."),
        cfgH=t("Server configuration", "Configuration du serveur"),
        cfgNote=t("The file config/matriochka.json is created on first launch. Edit it with the server stopped.", "Le fichier config/matriochka.json est créé au premier lancement. Modifie-le serveur arrêté."),
        cfgCols=[t("Key", "Clé"), t("Default", "Défaut"), t("What it does", "Rôle")],
        cfg=[dict(k=k, v=v, d=dd) for k, v, dd in [
            ("progressionGates", "true", t("Lock enchanting, the Nether, the End and elytra behind progression", "Verrouille enchantements, Nether, End et élytres derrière la progression")),
            ("mobHealthMultiplier", "1.0", t("Scales the health of every creature and boss", "Ajuste la vie de toutes les créatures et des boss")),
            ("mobDamageMultiplier", "1.0", t("Scales the damage of every creature and boss", "Ajuste les dégâts de toutes les créatures et des boss")),
            ("maxGroupSize", "8", t("Players per group", "Joueurs par groupe")),
            ("difficulty", '"normal"', t("story (70% damage, nothing lost on death), normal, nightmare (130% damage, one charge per Soul Cradle) or hardcore (as nightmare, death is permanent, the Doll of Life never saves you and a broken World Block deletes its world)",
                                         "story (70 % des dégâts, rien n'est perdu à la mort), normal, nightmare (130 % des dégâts, une charge par Berceau d'âme) ou hardcore (comme nightmare, la mort est définitive, la Poupée de vie ne te sauve plus et un Bloc-monde cassé efface son monde)")),
            ("karma", "true", t("false freezes every karma change (the Journal still shows the value)", "false fige tout changement de karma (le Journal affiche toujours la valeur)")),
            ("soulGainMultiplier", "1.0", t("Scales every soul gain", "Ajuste tous les gains d'âmes")),
            ("maxActiveGroups", "0", t("How many groups may hold worlds (0: no limit); a Seed over the limit waits, unhatched", "Combien de groupes peuvent avoir des mondes (0 : sans limite) ; une Graine au-delà attend sans éclore")),
            ("maxParcels", "0", t("How many parcels the server may hand out (0: no limit)", "Combien de parcelles le serveur peut attribuer (0 : sans limite)")),
            ("worldEvents", "true", t("Invasions, surges and travelling merchants in the worlds", "Invasions, poussées et marchands itinérants dans les mondes")),
            ("worldEventChance", "0.06", t("Chance that an event starts around a player, rolled once a minute", "Chance qu'un événement démarre autour d'un joueur, tirée chaque minute")),
            ("worldEventCooldown", "10", t("Minutes of quiet in a world after an event", "Minutes de calme dans un monde après un événement")),
            ("invasionWeight, surgeWeight, merchantWeight", "3, 3, 2", t("Relative weights of the three events", "Poids relatifs des trois événements"))]],
    )


# ---------------------------------------------------------------- main
def main():
    global LANG
    os.makedirs(PUBLIC, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    check_boss_anims()
    copy_assets()
    shared = dict(version=VERSION, discord=DISCORD, repo=REPO, releases=RELEASES, wiki=WIKI, site=SITE, icons=ICONS,
                  hasTrailer=os.path.exists(os.path.join(PUBLIC, "trailer.mp4")),
                  hasReel=os.path.exists(os.path.join(PUBLIC, "reel.mp4")))
    for lang in ("en", "fr"):
        LANG = lang
        worlds = build_worlds()
        # the catalogue: every world's items and blocks, in world order
        catalog = [dict(n=w["n"], name=w["name"], items=w["codex"]["items"], blocks=w["codex"]["blocks"]) for w in worlds]
        data = dict(lang=lang, copy=build_copy(), worlds=worlds, mobs=build_mobs(), bosses=build_bosses(), catalog=catalog)
        with open(os.path.join(DATA, f"{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATA, "shared.json"), "w", encoding="utf-8") as f:
        json.dump(shared, f, ensure_ascii=False, indent=1)
    n_mobs = len(C.MOBS)
    print(f"site data: 2 languages, 11 worlds, {n_mobs} creatures, {len(C.BOSSES)} bosses, {len(SHOTS)} screenshots")


if __name__ == "__main__":
    main()
