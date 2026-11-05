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
RECIPES_JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Recipes.java")

REPO = "https://github.com/achedon12/matriochka"
RELEASES = REPO + "/releases"
WIKI = REPO + "/wiki"
SITE = "https://achedon12.github.io/matriochka/"
VERSION = "0.1.0"

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
    "obsidian": ("Obsidian", "Obsidienne"), "observer": ("Observer", "Observateur"), "piston": ("Piston", "Piston"),
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
    process_shots(os.path.join(PUBLIC, "shots"))
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
    """Public path of the texture of an item or block id, or None for vanilla ingredients."""
    if id_.startswith("minecraft:"):
        return None
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


def rec(r):
    return dict(out=r["out"], tex=tex(r["out"]), name=name(r["out"]), count=r["count"], inputs=ing(r["inputs"]))


# ---------------------------------------------------------------- world copy (numbers from rules/WorldRules.java)
RULE_SHORT = {
    0: ("Iron is the ceiling. Find the Guardian.", "Le fer comme plafond. Trouve le Gardien."),
    1: ("The air poisons you. Water washes it off.", "L'air t'empoisonne. L'eau te lave."),
    2: ("Lava and depth cook you slowly.", "La lave et la profondeur te cuisent lentement."),
    3: ("No sky, only halls. And the halls move.", "Pas de ciel, que des salles. Et elles bougent."),
    4: ("Gusts throw you off the islands.", "Les rafales te jettent hors des îles."),
    5: ("Total darkness. Every step makes noise.", "Le noir complet. Chaque pas fait du bruit."),
    6: ("Every 90 seconds, up becomes down.", "Toutes les 90 secondes, le haut devient le bas."),
    7: ("Your oxygen runs out. The pressure crushes.", "L'oxygène s'épuise. La pression écrase."),
    8: ("A day lasts eight minutes. A season, two.", "Une journée dure huit minutes. Une saison, deux."),
    9: ("The ground heaves every minute.", "Le sol se soulève toutes les minutes."),
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
        "Table once you have reproduced the lock pattern. Every five minutes the halls rearrange themselves, with a "
        "ten-second warning. Light is scarce, so bring your own.",
        "Ici, ni surface ni ciel : rien que le donjon. Les portes scellées cèdent aux Clés de donjon, fabriquées à la "
        "Table du Geôlier une fois le motif de la serrure reproduit. Toutes les cinq minutes, les salles se "
        "réorganisent, avec dix secondes de préavis. La lumière est rare : apporte la tienne."),
    4: ("Floating islands under a permanent storm. Every 30 seconds a gust hits anyone under the open sky unless they "
        "crouch or take shelter, and you hear it two seconds early. Every 45 seconds lightning marks a spot near exposed "
        "players with sparks, then strikes three seconds later. Elytra stay grounded here until the Master of Seasons "
        "falls: the Glider and the Grappling Hook are how you cross.",
        "Des îles flottantes sous un orage permanent. Toutes les 30 secondes, une rafale frappe quiconque se tient à ciel "
        "ouvert, sauf accroupi ou à l'abri, et tu l'entends arriver deux secondes avant. Toutes les 45 secondes, la "
        "foudre marque un point près des joueurs exposés par des étincelles, puis tombe trois secondes plus tard. Les "
        "élytres restent clouées au sol tant que le Maître des saisons n'est pas tombé : on traverse en Planeur et au "
        "Grappin."),
    5: ("No light, and a noise gauge. Sprinting adds 4 per second, walking 0.6; standing still removes 1.5, sneaking "
        "3. Above 50, every creature within 28 blocks comes for you. Darkness washes over your sight every ten seconds "
        "unless you carry a lit Solar Lantern (20 minutes of light) or night vision. Silence Balm wipes your noise.",
        "Aucune lumière, et une jauge de bruit. Courir ajoute 4 par seconde, marcher 0,6 ; rester immobile retire 1,5, "
        "s'accroupir 3. Au-dessus de 50, toutes les créatures à moins de 28 blocs viennent te chercher. L'obscurité "
        "envahit ta vue toutes les dix secondes, sauf si tu portes une Lanterne solaire allumée (20 minutes) ou une "
        "vision nocturne. Le Baume de silence efface ton bruit."),
    6: ("Every 90 seconds gravity flips: you float upward for six seconds, then drift back down for twelve. A warning "
        "comes five seconds before. Gravity Boots ignore the flip entirely; a Stabilizer or a Flipped Apple keeps you "
        "steady for 30 seconds.",
        "Toutes les 90 secondes, la gravité s'inverse : tu montes pendant six secondes, puis tu redescends lentement "
        "pendant douze. Un avertissement tombe cinq secondes avant. Les Bottes de gravité ignorent l'inversion ; un "
        "Stabilisateur ou une Pomme retournée te gardent stable 30 secondes."),
    7: ("Under water you breathe from your own oxygen gauge: about 50 seconds without a suit, five minutes in the full "
        "Diving set. Surfacing refills 10 per second. Below y 110 the pressure starts to crush you; the full Diving set "
        "pushes that limit down to y 40. Oxygen Capsules and Apnea Kelp buy time, the Thruster brings you back up fast.",
        "Sous l'eau, tu respires sur ta propre jauge d'oxygène : environ 50 secondes sans équipement, cinq minutes avec "
        "le scaphandre complet. Remonter à la surface la recharge de 10 par seconde. Sous y 110, la pression commence à "
        "t'écraser ; le scaphandre complet repousse cette limite à y 40. Capsules d'oxygène et Algue d'apnée font gagner "
        "du temps, le Propulseur te ramène vite en haut."),
    8: ("Time runs three times faster: a full day and night take eight minutes, each season two. Summer leaves you "
        "hungry, winter slows you down, spring and autumn are your windows. A Season Preserve shields you for two "
        "minutes, the Hourglass holds the clock for 90 seconds, and the Time Workshop only accepts recipes at dawn and "
        "dusk.",
        "Le temps passe trois fois plus vite : un jour et une nuit tiennent en huit minutes, chaque saison en deux. "
        "L'été te creuse l'estomac, l'hiver te ralentit, le printemps et l'automne sont tes fenêtres. Une Conserve de "
        "saison te protège deux minutes, le Sablier retient l'horloge 90 secondes, et l'Atelier du temps n'accepte de "
        "recettes qu'à l'aube et au crépuscule."),
    9: ("Every 60 seconds the ground heaves: you are thrown and nauseous, and up to four loose blocks around you "
        "collapse. You get three seconds of warning. Within 16 blocks of a Terrain Anchor nothing moves; an Anchor in "
        "hand steadies you for ten minutes, and Grip Boots keep you on your feet.",
        "Toutes les 60 secondes, le sol se soulève : tu es projeté, pris de nausée, et jusqu'à quatre blocs mal "
        "accrochés autour de toi s'effondrent. Tu as trois secondes de préavis. À moins de 16 blocs d'une Ancre de "
        "terrain, rien ne bouge ; une Ancre utilisée te stabilise dix minutes, et les Bottes d'accroche te gardent "
        "debout."),
    10: ("You step out of the last block into a workshop built for giants, where your own base sits on a workbench "
         "like an object. The world is cut into nine zones of 256 blocks, each running the rule of one earlier world, "
         "from toxin to tremors. Every piece of old gear earns its place again.",
         "Tu sors du dernier bloc dans un atelier bâti pour des géants, où ta propre base trône sur un établi comme un "
         "simple objet. Le monde est découpé en neuf zones de 256 blocs, chacune rejouant la règle d'un monde "
         "précédent, de la toxine aux secousses. Chaque ancien équipement retrouve sa place."),
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
       "bosses": ("Bosses", "Boss"), "systems": ("Systems", "Systèmes"), "download": ("Download", "Télécharger")}




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
        ("10 s", "10 s", "of warning before they move", "de préavis avant qu'elles bougent")],
    4: [("30 s", "30 s", "between two gusts", "entre deux rafales"),
        ("45 s", "45 s", "between two lightning strikes", "entre deux éclairs"),
        ("3 s", "3 s", "from the sparks to the strike", "entre les étincelles et l'impact")],
    5: [("+4/s", "+4/s", "noise while sprinting", "de bruit en courant"),
        ("50", "50", "noise, and everything comes for you", "de bruit, et tout vient te chercher"),
        ("28", "28", "blocks: how far they come from", "blocs : la distance d'où elles viennent")],
    6: [("90 s", "90 s", "between two gravity flips", "entre deux inversions de gravité"),
        ("6 s", "6 s", "floating upward", "à monter"),
        ("12 s", "12 s", "drifting back down", "à redescendre")],
    7: [("50 s", "50 s", "of oxygen without a suit", "d'oxygène sans équipement"),
        ("5 min", "5 min", "in the full Diving set", "avec le scaphandre complet"),
        ("y 110", "y 110", "where the pressure starts", "où commence la pression")],
    8: [("×3", "×3", "the speed of time", "la vitesse du temps"),
        ("8 min", "8 min", "a day and a night", "un jour et une nuit"),
        ("2 min", "2 min", "a season", "une saison")],
    9: [("60 s", "60 s", "between two heaves", "entre deux secousses"),
        ("3 s", "3 s", "of warning", "de préavis"),
        ("16", "16", "blocks of calm around a Terrain Anchor", "blocs de calme autour d'une Ancre de terrain")],
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
    "pressure_aura": ("Its pressure reaches 7 blocks: every second there it gives Slowness II and Mining Fatigue II and takes 2 of your oxygen.",
                      "Sa pression porte à 7 blocs : chaque seconde passée là donne Lenteur II et Fatigue de minage II, et retire 2 d'oxygène."),
    "slowing_aura": ("Its aura reaches 7 blocks: every second there gives Slowness II and Mining Fatigue II.",
                     "Son aura porte à 7 blocs : chaque seconde passée là donne Lenteur II et Fatigue de minage II."),
    "swimmer": ("In water it homes in on you and keeps facing you as it swims.",
                "Dans l'eau, il fond sur toi et nage sans te quitter des yeux."),
    "swimmer_oxygen": ("A quick swimmer that homes in on you, and within 3 blocks it drains 3 of your oxygen every second.",
                       "Un nageur rapide qui fond sur toi et, à moins de 3 blocs, te retire 3 d'oxygène par seconde."),
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
            armor_d = dict(pieces=[dict(tex=tex(f'{armor["id"]}_{p}'), name=name(f'{armor["id"]}_{p}')) for p in ("helmet", "chestplate", "leggings", "boots")],
                           text=t(f"{gw[1]} armour, {gw[2]} toughness, a {gw[0]}-damage weapon at this tier.",
                                  f"{gw[1]} d’armure, {gw[2]} de robustesse, une arme à {gw[0]} de dégâts à ce palier.")
                           + ((" " + armor["effect_" + LANG]) if armor.get("effect_" + LANG) else ""))
        structs = {}
        for (sid, en, fr, role, size, rarity, arch) in C.STRUCTURES[n]:
            structs.setdefault(role, []).append(en if LANG == "en" else fr)
        d.update(rule=C.RULES[w["rule"]][LANG], tier=t(*TIER[w["tier"]]),
                 seed=dict(id=f"seed_{n}", tex=tex(f"seed_{n}"), name=name(f"seed_{n}"),
                           soil=t(f"Plant on tilled World Soil {n - 1}.", f"Se plante sur une Terre de monde {n - 1} bêchée."),
                           cond=LANGS[LANG].get(f"message.matriochka.seed_planted.{n}", ""),
                           inputs=ing(seed["inputs"]) if seed else []),
                 station=dict(id=station, tex=tex(station), name=name(station), note=t(*STATION_NOTE[station]), shot=shot(f"gui_station_{station}"),
                              make=ing(st_make["inputs"]) if st_make else [],
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
    return out


def codex(n):
    """Everything a world holds: every item and block, how you get it, its quests and its achievements."""
    items = []
    for it in C.ITEMS:
        if it["world"] != n or it["kind"] == "armorset":
            continue
        st, r = recipe_for(it["id"])
        items.append(dict(id=it["id"], tex=tex(it["id"]), name=name(it["id"]), kind=it["kind"], rarity=t(*RARITY.get(it["rarity"], ("", ""))),
                          effect=it.get("effect_" + LANG, ""), station=STATION_NAME(st), inputs=ing(r["inputs"]) if r else [],
                          count=r["count"] if r else 1, drops=_sources_of(it["id"])))
    armor = next((it for it in C.ITEMS if it["world"] == n and it["kind"] == "armorset"), None)
    if armor:
        for p in ("helmet", "chestplate", "leggings", "boots"):
            pid = f'{armor["id"]}_{p}'
            st, r = recipe_for(pid)
            items.append(dict(id=pid, tex=tex(pid), name=name(pid), kind="armor", rarity=t(*RARITY.get(armor["rarity"], ("", ""))),
                              effect=armor.get("effect_" + LANG, ""), station=STATION_NAME(st), inputs=ing(r["inputs"]) if r else [],
                              count=r["count"] if r else 1, drops=[]))
    for f in C.FOODS:
        if f[3] == n and all(x["id"] != f[0] for x in items):
            st, r = recipe_for(f[0])
            items.append(dict(id=f[0], tex=tex(f[0]), name=name(f[0]), kind="food", rarity="", effect=f[4] if LANG == "en" else f[5],
                              station=STATION_NAME(st), inputs=ing(r["inputs"]) if r else [], count=r["count"] if r else 1, drops=[]))
    blocks = []
    for b in C.BLOCKS:
        if b["world"] != n:
            continue
        st, r = recipe_for(b["id"])
        blocks.append(dict(id=b["id"], tex=f"blocks/{b['id']}.png", name=name(b["id"]), kind=b["kind"], effect=b.get("note_" + LANG, ""),
                           station=STATION_NAME(st), inputs=ing(r["inputs"]) if r else [], count=r["count"] if r else 1,
                           drops=[], yields=name(C.ORE_DROPS[b["id"]]) if b["id"] in C.ORE_DROPS else None))
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
    labels = {f"attack.{a['slug']}": (a["en"], a["fr"]) for a in ATK.full(eid)} if eid in ATK.A else {}
    out = []
    for full in anim_names(eid):
        short = full.split(".", 1)[1] if full.startswith("animation.") else full
        lab = labels.get(short) or ANIM_LABEL.get(short)
        out.append(dict(key=full, label=t(*lab) if lab else short))
    return out


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
            unlocks.append(t(f"Its core is the key ingredient of the World {w + 1} Seed.", f"Son noyau est l'ingrédient clé de la Graine du monde {w + 1}."))
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
            hp=fmt(b["hp"]), dmg=fmt(b["dmg"]), phases=phases, atks=atks, timings=timings, cooldown=cooldown,
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
        seed=t("Opening it", "L'ouvrir"), station=t("Station", "Station"), builtFrom=t("Built at the Matrix Workbench from", "Se fabrique à l'Établi matriciel avec"),
        carry=t("What you'll carry", "Ce que tu emporteras"), structures=t("Ten structures", "Dix structures"), armour=t("Armour set", "Armure"),
        madeAt=t("Made at the Matrix Workbench", "Fabriqué à l'Établi matriciel"), moreAbout=t("Everything about this world", "Tout sur ce monde"),
        allWorlds=t("All worlds", "Tous les mondes"), back=t("Back to the bestiary", "Retour au bestiaire"), backBosses=t("Back to the bosses", "Retour aux boss"),
        backWorlds=t("Back to the ten worlds", "Retour aux dix mondes"),
        prev=t("Previous", "Précédent"), next=t("Next", "Suivant"), sheet=t("Technical sheet", "Fiche technique"),
        view3d=t("View in 3D", "Voir en 3D"), loading3d=t("Opening the model", "Ouverture du modèle"),
        no3d=t("This browser cannot draw the 3D model. Here is its texture, as the game paints it.", "Ce navigateur ne peut pas afficher le modèle 3D. Voici sa texture, telle que le jeu la peint."),
        dragHint=t("Drag to turn it, scroll or pinch to zoom.", "Fais glisser pour le tourner, molette ou pincement pour zoomer."),
        animations=t("Animations", "Animations"), autoRotate=t("Turn slowly", "Tourner lentement"),
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
             t("Till World Soil with a hoe and plant the Seed. Each Seed wants the soil of the world before it, and one condition: water, heat, redstone, open sky, darkness, height.",
               "Bêche une Terre de monde à la houe et plantes-y la Graine. Chaque Graine veut la terre du monde précédent, et une condition : eau, chaleur, redstone, ciel ouvert, obscurité, hauteur.")),
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
             t("The core is the key ingredient of the next Seed. Ten times, until the last block opens onto something much larger.",
               "Le noyau est l'ingrédient clé de la Graine suivante. Dix fois, jusqu'à ce que le dernier bloc s'ouvre sur quelque chose de bien plus grand."))]],
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
               "Jusqu'à huit joueurs partagent un groupe, ses mondes et ses boss vaincus. Les boss se renforcent à chaque joueur qui rejoint le combat."))]],
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
        verbs=[dict(verb=t("Grow a world", "Fais pousser un monde"), p=t("Craft a Seed, plant it on World Soil, meet its condition. The block that hatches holds a world.",
                                                                      "Fabrique une Graine, plante-la sur une Terre de monde, remplis sa condition. Le bloc qui éclot contient un monde."),
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
                   dict(name="Modrinth", note=t("Coming soon", "Bientôt"), href=None, icon="package"),
                   dict(name="CurseForge", note=t("Coming soon", "Bientôt"), href=None, icon="package")],
        faqH=t("Questions", "Questions"),
        faq=[dict(q=t("Where do I start?", "Par où commencer ?"),
                  a=t("Read the Artisan's Scroll you spawn with, then find the Guardian's Sanctuary on the Surface and wake the Block Guardian.",
                      "Lis le Parchemin de l'artisan reçu au départ, puis trouve le Sanctuaire du Gardien sur la Surface et réveille le Gardien du bloc.")),
             dict(q=t("My Seed does not hatch.", "Ma Graine n'éclot pas."),
                  a=t("Check that it sits on tilled World Soil of the previous world and that its condition is met: smoke puffs mean it is still waiting.",
                      "Vérifie qu'elle est sur une Terre de monde du monde précédent, bêchée, et que sa condition est remplie : des volutes de fumée veulent dire qu'elle attend encore.")),
             dict(q=t("I died inside a world. Are my things gone?", "Je suis mort dans un monde. Mes affaires sont perdues ?"),
                  a=t("No. A death chest keeps them where you fell, and a Soul Cradle placed beforehand lets you wake up inside the world.",
                      "Non. Un coffre de mort les garde là où tu es tombé, et un Berceau d'âmes posé avant te fait renaître dans le monde.")),
             dict(q=t("Does it work on servers?", "Ça marche en multijoueur ?"),
                  a=t("Yes, with the mod on the server and on every client. Up to eight players share a group, its worlds and its bosses.",
                      "Oui, avec le mod sur le serveur et sur chaque client. Jusqu'à huit joueurs partagent un groupe, ses mondes et ses boss.")),
             dict(q=t("Does it work on Lunar Client?", "Ça marche sur Lunar Client ?"),
                  a=t("Through Lunar Client's Fabric profile for 26.3, with Fabric API and GeckoLib.", "Via le profil Fabric de Lunar Client pour la 26.3, avec Fabric API et GeckoLib.")),
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
        ctaP=t("Minecraft 26.3, Fabric Loader 0.20 or newer, Fabric API, GeckoLib 5.5.7 and Java 25.", "Minecraft 26.3, Fabric Loader 0.20 ou plus récent, Fabric API, GeckoLib 5.5.7 et Java 25."),
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
        sitesP=t("Ten structures generate across every world, each with its own purpose. Here is where to look, what waits inside, and what the chests can hold.",
                 "Dix structures apparaissent dans chaque monde, chacune avec son rôle. Voici où chercher, ce qui t'attend dedans et ce que les coffres peuvent contenir."),
        lootH=t("What the chests can hold", "Ce que les coffres peuvent contenir"), cHidden=t("Hidden until you earn it", "Caché jusqu'à ce que tu l'obtiennes"),
        h=t("The ten worlds", "Les dix mondes"),
        lead=t("Each world is planted inside the one before it, and each one bends a rule you thought you knew. Numbers below come straight from the mod's code.",
               "Chaque monde est planté dans le précédent, et chacun tord une règle que tu croyais connaître. Les chiffres ci-dessous viennent directement du code du mod."),
        desc=t("The ten worlds of Matriochka: rules, Seeds, stations, recipes, creatures, bosses and structures.",
               "Les dix mondes de Matriochka : règles, Graines, stations, recettes, créatures, boss et structures."),
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
        lead=t("Eleven fights, each built the same way: an announcement you can read, a fast and dangerous attack, then an opening. Hit a boss during its opening and it takes 1.5 times the damage; outside of it, only three quarters.",
               "Onze combats, tous construits pareil : une annonce lisible, une attaque rapide et dangereuse, puis une ouverture. Frappé pendant son ouverture, un boss subit 1,5 fois les dégâts ; en dehors, seulement les trois quarts."),
        tiers=[dict(tier=tr, warn=secs(tier_ticks(wn)[0] / 20), sig=secs(tier_ticks(wn)[0] * 2 / 20), opening=secs(tier_ticks(wn)[1] / 20))
               for tr, wn in ((t("Surface to World 3", "Surface au monde 3"), 0), (t("Worlds 4 to 6", "Mondes 4 à 6"), 4),
                              (t("Worlds 7 to 9", "Mondes 7 à 9"), 7), (t("World 10", "Monde 10"), 10))],
        tierCols=[t("Tier", "Palier"), t("Warning", "Annonce"), t("Signature warning", "Annonce signature"), t("Opening", "Ouverture")],
        tierNote=t("Bosses never take damage while changing phase. The Spore Queen's cocoon holds until its nodes are broken.", "Un boss ne prend aucun dégât pendant un changement de phase. Le cocon de la Reine des spores tient tant que ses nœuds ne sont pas brisés."),
        mp=[dict(p=p, mult="×" + fmt(round(1 + 0.6 * (p - 1), 1))) for p in (1, 2, 4, 8)],
        mpNote=t("Counted within 48 blocks when the boss wakes. Everyone within 64 blocks at its death shares the victory.", "Compté dans un rayon de 48 blocs au réveil du boss. Tous ceux à moins de 64 blocs à sa mort partagent la victoire."),
        rewardNote=t("plus 100 souls for every player in the fight", "et 100 âmes pour chaque joueur présent au combat"),
        desc=t("The eleven bosses of Matriochka: health, attacks, phases, timings and rewards.", "Les onze boss de Matriochka : vie, attaques, phases, timings et récompenses."),
    )
    return dict(ui=ui, nav=nav, home=home, worlds=worlds, bestiary=bestiary, bosses=bosses, systems=build_systems(d), download=build_download())


def slot_label(slot):
    return {"armor": t("Armour", "Armures"), "weapon_armor": t("Weapons, armour", "Armes, armures"),
            "armor_weapon": t("Armour, light weapons", "Armures, armes légères"), "tool": t("Tools", "Outils")}[slot]


def build_systems(d):
    _, cradle = recipe_for("soul_cradle")
    _, chance = recipe_for("chance_doll")
    _, thread = recipe_for("return_thread")
    rar = [("common", t("Common", "Commun")), ("rare", t("Rare", "Rare")), ("epic", t("Epic", "Épique")), ("legendary", t("Legendary", "Légendaire"))]
    karma = [("+50", "light2"), ("+25", "light1"), ("0", "neutral"), ("−25", "dark1"), ("−50", "dark2")]
    nq = len(C.QUESTS)
    nach = sum(len(v) for v in C.ACH.values())
    return dict(
        tiles=[dict(id="survival", icon="heart", stat=t("3 layers", "3 couches"), line=t("A doll that breaks so you don't, and ways back in.", "Une poupée qui se brise à ta place, et des moyens de revenir.")),
               dict(id="souls", icon="sparkles", stat=t("-100 to +100", "-100 à +100"), line=t("Souls are the currency; karma decides how people treat you.", "Les âmes sont la monnaie ; le karma décide comment on te traite.")),
               dict(id="classes", icon="swords", stat=t("6 classes, level 5", "6 classes, niveau 5"), line=t("Every crafted weapon and armour is born with a class.", "Chaque arme et armure fabriquée naît avec une classe.")),
               dict(id="nesting", icon="layers", stat=t("Inside everything", "Partout dedans"), line=t("Chests in chests, creatures in creatures, worlds in worlds.", "Des coffres dans des coffres, des créatures dans des créatures, des mondes dans des mondes.")),
               dict(id="groups", icon="users", stat=t("Up to 8 players", "Jusqu'à 8 joueurs"), line=t("Share worlds and bosses with your friends.", "Partage mondes et boss avec tes amis.")),
               dict(id="journal", icon="book-open", stat=t("64 quests", "64 quêtes"), line=t("Objectives, quests, achievements and titles.", "Objectifs, quêtes, succès et titres."))],
        h=t("Systems", "Systèmes"), headImg=shot("head_systems_banner"),
        lead=t("What keeps you alive, what you trade for power, and how your gear grows. Everything here works the same in solo and on a server.",
               "Ce qui te garde en vie, ce que tu échanges contre de la puissance, et comment ton équipement grandit. Tout fonctionne pareil en solo et sur serveur."),
        desc=t("Doll of Life, death and respawn, souls and karma, gear classes, groups and quests in Matriochka.",
               "Poupée de vie, mort et réapparition, âmes et karma, classes d'équipement, groupes et quêtes dans Matriochka."),
        onPage=t("On this page", "Sur cette page"),
        toc=[("survival", t("Survival", "Survie")), ("souls", t("Souls and karma", "Âmes et karma")), ("classes", t("Classes", "Classes")),
             ("nesting", t("Nesting", "Gigogne")), ("groups", t("Groups", "Groupes")), ("journal", t("Journal", "Journal"))],
        survivalH=t("Survival", "Survie"),
        lifeDoll=dict(tex=tex("life_doll"), h=name("life_doll"), p=t("You carry a doll made of layers. It gets its first layer when the Spore Queen falls, a second after the Light Eater and a third after the Master of Seasons. Every boss you beat restores one layer, and the Soul Altar rebuilds one for 50 souls.",
                                                                    "Tu portes une poupée faite de couches. Elle reçoit sa première couche à la chute de la Reine des spores, une deuxième après le Mangeur de lumière et une troisième après le Maître des saisons. Chaque boss vaincu restaure une couche, et l'Autel des âmes en reconstruit une pour 50 âmes.")),
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
        soulsLead=t("Every item carries a soul whose weight depends on its rarity. Put it on the Soul Altar and choose, for good: purify it to free the soul and gain karma, or devour it to absorb the soul and lose karma. Either way you keep the souls, which pay for class upgrades, cradle charges and doll layers.",
                    "Chaque objet porte une âme dont le poids dépend de sa rareté. Pose-le sur l'Autel des âmes et choisis, définitivement : purifie-le pour libérer l'âme et gagner du karma, ou dévore-le pour absorber l'âme et perdre du karma. Dans les deux cas tu gardes les âmes, qui paient les améliorations de classe, les charges de berceau et les couches de poupée."),
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
        classesLead=t("Every weapon, tool and armour piece gets a random class when it is crafted. The Class Table raises its level with souls; your progression caps how far you can go.",
                      "Chaque arme, outil ou pièce d'armure reçoit une classe au hasard à sa fabrication. La Table de classe monte son niveau avec des âmes ; ta progression limite jusqu'où tu peux aller."),
        clsCols=[t("Class", "Classe"), t("Bonuses", "Bonus"), t("Found on", "Sur")],
        classes=[dict(name=en if LANG == "en" else fr, bonus=den if LANG == "en" else dfr, slot=slot_label(slot)) for (cid, en, fr, slot, den, dfr) in C.CLASSES],
        upH=t("Upgrading", "Améliorer"), upCols=[t("Level", "Niveau"), t("Total bonus", "Bonus total"), t("Souls", "Âmes")],
        up=[dict(lv=str(lv), bonus="+" + pct(b), souls=str(c)) for lv, b, c in ((2, 10, 10), (3, 20, 30), (4, 35, 90), (5, 50, 270))],
        upNote=t("Level 1 to 5 costs 400 souls per piece.", "Du niveau 1 au niveau 5 : 400 âmes par pièce."),
        capH=t("Level cap", "Niveau maximal"), capCols=[t("Progression", "Progression"), t("Max level", "Niveau max")],
        cap=[dict(k=t(f"World {w} done", f"Monde {w} terminé"), v=str(lv)) for w, lv in ((2, 2), (4, 3), (6, 4), (8, 5))],
        chance=dict(tex=tex("chance_doll"), h=name("chance_doll"), p=t("Rerolls an item into a different class it can hold, and keeps its level. The first reroll costs 20 souls, and the price doubles each time on the same item: 20, 40, 80, 160.",
                                                                       "Relance un objet vers une autre classe compatible, en gardant son niveau. Le premier changement coûte 20 âmes, et le prix double à chaque fois sur le même objet : 20, 40, 80, 160."),
                    inputs=ing(chance["inputs"]) if chance else []),
        classShot=dict(src=shot("gui_station_class_table"), caption=t("The Class Table", "La Table de classe")),
        nestingH=t("Things inside things", "Des choses dans des choses"),
        nestingLead=t("The name is the rule: something can always hold something else. These systems unlock as the story goes on.", "Le nom est la règle : une chose peut toujours en contenir une autre. Ces systèmes se débloquent au fil de l'histoire."),
        nestCols=[t("System", "Système"), t("Effect", "Effet"), t("Unlocked", "Déblocage")],
        nest=[dict(a=a, b=b, c=c) for a, b, c in [
            (t("Doll of Life", "Poupée de vie"), t("Each layer survives one death", "Chaque couche survit à une mort"), t("Worlds 1, 5, 8", "Mondes 1, 5, 8")),
            (t("Nesting chests", "Coffres gigognes"), t("A chest that holds a smaller one", "Un coffre qui en contient un plus petit"), t("World 2", "Monde 2")),
            (t("Nesting creatures", "Créatures gigognes"), t("A defeated mob releases a smaller one", "Un mob vaincu en libère un plus petit"), t("World 2", "Monde 2")),
            (t("Refuge doll", "Poupée-refuge"), t("A pocket base you carry", "Une base de poche que tu transportes"), t("World 3", "Monde 3")),
            (t("Layered armour", "Armures à couches"), t("One layer protects the next", "Une couche protège la suivante"), t("World 4", "Monde 4")),
            (t("The final boss", "Le boss final"), t("Ten shells, one per world", "Dix enveloppes, une par monde"), t("World 10", "Monde 10"))]],
        gatesH=t("Gates", "Verrous"),
        gates=[t("Enchanting, anvils and the Nether open after World 2.", "Enchantements, enclumes et Nether s'ouvrent après le monde 2."),
               t("Diamonds come back in World 5: four Diamond Fragments make one at the Dark Altar.", "Le diamant revient dans le monde 5 : quatre Fragments de diamant en donnent un à l'Autel obscur."),
               t("Elytra stay grounded in Worlds 4, 6 and 9 until World 8 is done.", "Les élytres restent clouées au sol dans les mondes 4, 6 et 9 tant que le monde 8 n'est pas terminé."),
               t("The End opens after World 8.", "L'End s'ouvre après le monde 8.")],
        groupsH=t("Groups and servers", "Groupes et serveurs"),
        groupsLead=t("A player alone is a group of one. Worlds, progression and permissions belong to the group: up to eight players by default. Each group gets its own 3,000 by 3,000 block parcel in every world, walled off from the others, and a World Block can only be used by its group.",
                     "Un joueur seul forme un groupe d'une personne. Les mondes, la progression et les permissions appartiennent au groupe : jusqu'à huit joueurs par défaut. Chaque groupe reçoit sa propre parcelle de 3 000 sur 3 000 blocs dans chaque monde, séparée des autres, et un Bloc-monde ne sert qu'à son groupe."),
        cmds=[dict(c=c, d=x) for c, x in [
            ("/matriochka group info", t("Your group, its members and defeated bosses", "Ton groupe, ses membres et ses boss vaincus")),
            ("/matriochka group invite <player>", t("Invite a player into your group", "Inviter un joueur dans ton groupe")),
            ("/matriochka group join", t("Accept the pending invitation", "Accepter l'invitation en attente")),
            ("/matriochka group leave", t("Leave your group", "Quitter ton groupe")),
            ("/matriochka karma show", t("Your karma and souls", "Ton karma et tes âmes"))]],
        serverNote=t("The mod runs on the server and on every client. All rules, damage and rewards are decided by the server; nothing needs an online account or service.",
                     "Le mod s'installe sur le serveur et sur chaque client. Règles, dégâts et récompenses sont décidés par le serveur ; aucun compte ni service en ligne n'est nécessaire."),
        journalH=t("The Journal, quests and achievements", "Le Journal, les quêtes et les succès"),
        journalLead=t(f"The Artisan's Scroll arrives on your first login and turns into the Journal when the Guardian falls. Its tabs track your objective, quests, karma and worlds. There are {nq} optional quests (4 on the Surface, 6 per world) and {nach} achievements, 10 per world, two of them hidden. Fifty Journal pages and ten hidden dolls are scattered through the worlds; nest the dolls in order and something smaller opens.",
                      f"Le Parchemin de l'artisan arrive à ta première connexion et devient le Journal quand le Gardien tombe. Ses onglets suivent ton objectif, tes quêtes, ton karma et tes mondes. Il y a {nq} quêtes facultatives (4 sur la Surface, 6 par monde) et {nach} succès, 10 par monde dont deux cachés. Cinquante pages du Journal et dix poupées cachées sont dispersées dans les mondes ; emboîte les poupées dans l'ordre et quelque chose de plus petit s'ouvre."),
        journalShots=[dict(src=shot(k), caption=c) for k, c in (("gui_journal_0", t("The Journal's objective tab", "L'onglet objectif du Journal")), ("gui_journal_1", t("Quests", "Les quêtes"))) if shot(k)],
        titlesH=t("Titles you can earn", "Titres à gagner"),
        titles=[v for k, v in d.items() if k.startswith("title.matriochka.")],
    )


def build_download():
    return dict(
        h=t("Download", "Télécharger"), headImg=shot("head_download_banner"),
        lead=t(f"Version {VERSION} for Minecraft 26.3 on Fabric. Install it on the client to play solo, and on both server and clients to play together.",
               f"Version {VERSION} pour Minecraft 26.3 sous Fabric. Installe-la côté client pour jouer en solo, et sur le serveur et chaque client pour jouer ensemble."),
        desc=t("Download Matriochka for Minecraft 26.3 on Fabric: requirements, installation, Lunar Client and server configuration.",
               "Télécharger Matriochka pour Minecraft 26.3 sous Fabric : prérequis, installation, Lunar Client et configuration serveur."),
        sources=[dict(name="GitHub", note=t("Releases, changelog and source", "Versions, changements et code source"), href=RELEASES),
                 dict(name="Modrinth", note=t("Coming soon", "Bientôt disponible"), href=None),
                 dict(name="CurseForge", note=t("Coming soon", "Bientôt disponible"), href=None)],
        reqH=t("Requirements", "Prérequis"),
        reqs=[dict(n=n, v=v, s=s) for n, v, s in [
            ("Minecraft", "26.3", t("Java Edition", "Édition Java")),
            ("Fabric Loader", "0.20+", t("Install it for 26.3 with the Fabric installer", "À installer pour la 26.3 avec l'installeur Fabric")),
            ("Fabric API", "0.165.2+", t("Built for 26.3, goes in the mods folder", "Pour la 26.3, dans le dossier mods")),
            ("GeckoLib", "5.5.7", t("Animated models of bosses and creatures", "Modèles animés des boss et créatures")),
            ("Java", "25", t("Bundled with the official launcher", "Fourni avec le launcher officiel"))]],
        installH=t("Installing", "Installation"),
        steps=[t("Install Fabric Loader for Minecraft 26.3.", "Installe Fabric Loader pour Minecraft 26.3."),
               t(f"Download matriochka-{VERSION}.jar from the GitHub releases.", f"Télécharge matriochka-{VERSION}.jar depuis les versions GitHub."),
               t("Put it in your mods folder with Fabric API and GeckoLib.", "Place-le dans ton dossier mods avec Fabric API et GeckoLib."),
               t("Launch the Fabric profile and create a new world. The Artisan's Scroll is waiting in your inventory.", "Lance le profil Fabric et crée un nouveau monde. Le Parchemin de l'artisan t'attend dans l'inventaire.")],
        lunarH="Lunar Client",
        lunar=t("Matriochka is built on Fabric so that it can run on Lunar Client, whose mod loading relies on Fabric. Support for Minecraft 26.3 together with GeckoLib is still being confirmed there: if the mod does not load, play it with the official launcher or Prism Launcher on a Fabric profile in the meantime.",
                "Matriochka repose sur Fabric pour pouvoir tourner sur Lunar Client, dont le chargement de mods s'appuie sur Fabric. La prise en charge de Minecraft 26.3 avec GeckoLib y est encore en cours de vérification : si le mod ne se charge pas, joue en attendant avec le launcher officiel ou Prism Launcher sur un profil Fabric."),
        wikiH=t("Wiki", "Wiki"), wiki=t("Recipes, step-by-step guides and answers to common questions live on the GitHub wiki.", "Recettes, guides pas à pas et réponses aux questions courantes sont sur le wiki GitHub."),
        wikiBtn=t("Open the wiki", "Ouvrir le wiki"),
        earlyH=t("Early version", "Version précoce"),
        early=t("Names, numbers and balance can still change between versions. Back up your worlds before updating, and report anything odd on the issue tracker.", "Les noms, les chiffres et l'équilibrage peuvent encore changer d'une version à l'autre. Sauvegarde tes mondes avant de mettre à jour, et signale tout comportement étrange sur le suivi des tickets."),
        cfgH=t("Server configuration", "Configuration du serveur"),
        cfgNote=t("The file config/matriochka.json is created on first launch. Edit it with the server stopped.", "Le fichier config/matriochka.json est créé au premier lancement. Modifie-le serveur arrêté."),
        cfgCols=[t("Key", "Clé"), t("Default", "Défaut"), t("What it does", "Rôle")],
        cfg=[dict(k=k, v=v, d=dd) for k, v, dd in [
            ("progressionGates", "true", t("Lock enchanting, the Nether, the End and elytra behind progression", "Verrouille enchantements, Nether, End et élytres derrière la progression")),
            ("mobHealthMultiplier", "1.0", t("Scales the health of every creature", "Ajuste la vie de toutes les créatures")),
            ("mobDamageMultiplier", "1.0", t("Scales the damage of every creature", "Ajuste les dégâts de toutes les créatures")),
            ("maxGroupSize", "8", t("Players per group", "Joueurs par groupe")),
            ("screenShake", "true", t("Camera shake during big hits", "Tremblements de caméra lors des gros coups")),
            ("difficulty", '"normal"', t("Overall difficulty preset", "Préréglage général de difficulté"))]],
    )


# ---------------------------------------------------------------- main
def main():
    global LANG
    os.makedirs(PUBLIC, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    copy_assets()
    shared = dict(version=VERSION, repo=REPO, releases=RELEASES, wiki=WIKI, site=SITE, icons=ICONS,
                  hasTrailer=os.path.exists(os.path.join(PUBLIC, "trailer.mp4")),
                  hasReel=os.path.exists(os.path.join(PUBLIC, "reel.mp4")))
    for lang in ("en", "fr"):
        LANG = lang
        data = dict(lang=lang, copy=build_copy(), worlds=build_worlds(), mobs=build_mobs(), bosses=build_bosses())
        with open(os.path.join(DATA, f"{lang}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATA, "shared.json"), "w", encoding="utf-8") as f:
        json.dump(shared, f, ensure_ascii=False, indent=1)
    n_mobs = len(C.MOBS)
    print(f"site data: 2 languages, 11 worlds, {n_mobs} creatures, {len(C.BOSSES)} bosses, {len(SHOTS)} screenshots")


if __name__ == "__main__":
    main()
