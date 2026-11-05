#!/usr/bin/env python3
"""Builds the static Matriochka website (GitHub Pages, served from /docs).

Usage: python3 tools/site.py   (from the repository root, or anywhere)

Reads tools/content.py, the generated lang files, the Java recipes and the
in-game screenshots (build/run/clientGameTest/screenshots, optional), then
writes docs/ in English and docs/fr/ in French. Re-run it whenever the
content changes. Pillow is used to resize screenshots when available.
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

DOCS = os.path.join(ROOT, "docs")
RES = os.path.join(ROOT, "src/main/resources/assets/matriochka")
TEX = os.path.join(RES, "textures")
SHOTS_SRC = os.path.join(ROOT, "build/run/clientGameTest/screenshots")
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
    "leather_boots": ("Leather Boots", "Bottes en cuir"),
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


# ---------------------------------------------------------------- assets
ITEM_TEX = set()
ENTITY_TEX = set()
SHOTS = {}


def copy_assets():
    a = os.path.join(DOCS, "assets")
    for sub, src, keep in (("items", "item", ITEM_TEX), ("entities", "entity", ENTITY_TEX), ("blocks", "block", None)):
        dst = os.path.join(a, sub)
        os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(os.path.join(TEX, src))):
            if f.endswith(".png"):
                shutil.copy2(os.path.join(TEX, src, f), os.path.join(dst, f))
                if keep is not None:
                    keep.add(f[:-4])
    shutil.copy2(os.path.join(RES, "icon.png"), os.path.join(a, "icon.png"))
    process_shots(os.path.join(a, "shots"))


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


# Test captures that do not show what the page describes (fog, full-bright test client, boss hidden
# behind a marker column). Edit this set when better screenshots are captured.
SKIP_SHOTS = {"w03_view", "w05_view", "w03_boss", "w05_boss", "w06_boss", "w08_boss", "w09_boss"}


def process_shots(dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    if not os.path.isdir(SHOTS_SRC):
        return
    os.makedirs(dst, exist_ok=True)
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for f in sorted(os.listdir(SHOTS_SRC)):
        m = re.match(r"(w\d\d_(?:view|boss|threshold)|gui_[\w]+)\.png$", f)
        if not m:
            continue
        key = m.group(1)
        if key in SKIP_SHOTS or key.endswith("_threshold"):
            continue
        src = os.path.join(SHOTS_SRC, f)
        if Image is None:
            shutil.copy2(src, os.path.join(dst, f))
            SHOTS[key] = (f, 1920, 1080)
            continue
        img = Image.open(src)
        if key.startswith("gui_"):
            box = _gui_bbox(img)
            g = img.crop(box).convert("RGB")
            out = key + ".png"
            g.save(os.path.join(dst, out), optimize=True)
            SHOTS[key] = (out, g.width, g.height)
        else:
            v = img.convert("RGB").resize((1280, 720), Image.LANCZOS)
            out = key + ".jpg"
            v.save(os.path.join(dst, out), quality=82, optimize=True, progressive=True)
            SHOTS[key] = (out, 1280, 720)


# ---------------------------------------------------------------- small render helpers
def icon(n, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[n]}</svg>')


def light(n):
    """The glow colour of a world (0 = Surface)."""
    if n == 0:
        return "#D9A441"
    pal = C.WORLDS[n - 1]["pal"]
    pick = {6: 0, 8: 2, 10: 1}.get(n, 2)
    return "#" + pal[pick]


def tex(id_, A, size=32, cls="px", alt=""):
    if id_ in ITEM_TEX:
        return f'<img class="{cls}" src="{A}items/{id_}.png" width="{size}" height="{size}" alt="{e(alt)}" loading="lazy">'
    if id_.startswith("minecraft:"):
        return f'<span class="{cls} px-vanilla" style="width:{size}px;height:{size}px" aria-hidden="true"></span>'
    if os.path.exists(os.path.join(TEX, "block", id_ + ".png")):
        return f'<img class="{cls}" src="{A}blocks/{id_}.png" width="{size}" height="{size}" alt="{e(alt)}" loading="lazy">'
    return f'<span class="{cls} px-vanilla" style="width:{size}px;height:{size}px" aria-hidden="true"></span>'


def ingredients(inputs, A):
    parts = []
    for i, n in inputs:
        parts.append(f'<li class="ing">{tex(i, A, 24)}<span class="ing-n">{n}</span><span class="ing-name">{e(name(i))}</span></li>')
    return '<ul class="ings">' + "".join(parts) + "</ul>"


def shot(key, A, caption, cls="shot"):
    if key not in SHOTS:
        return ""
    f, w, h = SHOTS[key]
    pix = " shot-gui" if key.startswith("gui_") else ""
    return (f'<figure class="{cls}{pix}"><img src="{A}shots/{f}" width="{w}" height="{h}" alt="{e(caption)}" loading="lazy">'
            f'<figcaption>{e(caption)}</figcaption></figure>')


def fmt(x):
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    s = f"{x:,}" if isinstance(x, int) else f"{x}"
    if LANG == "fr":
        s = s.replace(",", " ").replace(".", ",")
    return s


def pct(x):
    return f"{fmt(x)} %" if LANG == "fr" else f"{fmt(x)}%"


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


# ---------------------------------------------------------------- page frame
def page(slug, title, desc, body, extra_head=""):
    A = "assets/" if LANG == "en" else "../assets/"
    other = ("fr/" if LANG == "en" else "../") + f"{slug}.html"
    other_label = "Français" if LANG == "en" else "English"
    other_lang = "fr" if LANG == "en" else "en"
    nav = []
    for p in PAGES:
        cur = ' aria-current="page"' if p == slug else ""
        nav.append(f'<li><a href="{p}.html"{cur}>{e(t(*NAV[p]))}</a></li>')
    full_title = "Matriochka" if slug == "index" else f"{title} | Matriochka"
    en_url = SITE + ("" if slug == "index" else f"{slug}.html")
    fr_url = SITE + "fr/" + ("" if slug == "index" else f"{slug}.html")
    return f"""<!doctype html>
<html lang="{LANG}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="author" content="achedon12">
<meta name="theme-color" content="#141210">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}assets/icon.png">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="fr" href="{fr_url}">
<link rel="icon" type="image/png" href="{A}icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&amp;family=Yeseva+One&amp;display=swap">
<link rel="stylesheet" href="{A}site.css">
{extra_head}</head>
<body class="page-{slug}">
<a class="skip" href="#main">{e(t("Skip to content", "Aller au contenu"))}</a>
<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="index.html"><img class="px" src="{A}icon.png" width="28" height="28" alt=""><span>Matriochka</span></a>
    <nav class="nav" aria-label="{e(t('Main', 'Principale'))}"><ul>{''.join(nav)}</ul></nav>
    <div class="top-tools">
      <a class="lang" href="{other}" hreflang="{other_lang}" lang="{other_lang}">{icon('languages')}<span>{other_label}</span></a>
      <a class="gh" href="{REPO}" aria-label="{e(t('Source code on GitHub', 'Code source sur GitHub'))}">{icon('github')}</a>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-in">
    <div class="foot-brand"><img class="px" src="{A}icon.png" width="40" height="40" alt=""><div><strong>Matriochka</strong><p>{e(t("A Fabric mod by achedon12, for Minecraft 26.3. Released under the MIT licence.", "Un mod Fabric d'achedon12 pour Minecraft 26.3, publié sous licence MIT."))}</p></div></div>
    <ul class="foot-links">
      <li><a href="{RELEASES}">{icon('download')}{e(t("Releases", "Versions"))}</a></li>
      <li><a href="{WIKI}">{icon('book-open')}{e(t("Wiki", "Wiki"))}</a></li>
      <li><a href="{REPO}">{icon('github')}GitHub</a></li>
      <li><a href="{REPO}/issues">{icon('bug')}{e(t("Report a bug", "Signaler un bug"))}</a></li>
    </ul>
    <p class="foot-note">{e(t("Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.", "Ce n'est pas un produit officiel Minecraft. Non approuvé par Mojang ou Microsoft, et sans lien avec eux."))}</p>
  </div>
</footer>
<script src="{A}site.js" defer></script>
</body>
</html>
"""


def page_head(title, lead, accent=None, extra=""):
    style = f' style="--accent:{accent}"' if accent else ""
    return (f'<section class="phead"{style}><div class="wrap"><h1>{e(title)}</h1>'
            f'<p class="lead">{lead}</p>{extra}</div></section>')


# ---------------------------------------------------------------- hero: nested dolls
DOLL = ("M100,12 C128,12 146,34 146,64 C146,82 140,96 131,106 C166,124 184,166 184,212 "
        "C184,262 150,292 100,292 C50,292 16,262 16,212 C16,166 34,124 69,106 C60,96 54,82 54,64 "
        "C54,34 72,12 100,12 Z")


def hero_svg():
    parts = []
    n = 11
    for i in range(n):
        s = 1 - i * 0.078
        col = light(i)
        tr = f"translate({100 - 100 * s:.2f},{196 - 196 * s:.2f}) scale({s:.3f})"
        fill = ' fill="#B3261E"' if i == n - 1 else ' fill="none"'
        parts.append(f'<g class="doll" data-w="{i}" style="--i:{i};--c:{col}" transform="{tr}">'
                     f'<path d="{DOLL}"{fill} pathLength="1" stroke-width="{1.7 / s:.2f}"/></g>')
    # the innermost doll gets a face and a gold band
    s = 1 - (n - 1) * 0.078
    face = (f'<g class="doll-face" transform="translate({100 - 100 * s:.2f},{196 - 196 * s:.2f}) scale({s:.3f})">'
            f'<circle cx="100" cy="66" r="30" fill="#E8D2A6"/><circle cx="90" cy="64" r="3.5" fill="#3A2416"/>'
            f'<circle cx="110" cy="64" r="3.5" fill="#3A2416"/><circle cx="86" cy="76" r="5" fill="#d8402f" opacity=".55"/>'
            f'<circle cx="114" cy="76" r="5" fill="#d8402f" opacity=".55"/>'
            f'<path d="M48,212 C70,232 130,232 152,212" fill="none" stroke="#D9A441" stroke-width="10"/></g>')
    return (f'<svg class="dolls" viewBox="0 0 200 300" role="img" aria-labelledby="dolls-t">'
            f'<title id="dolls-t">{e(t("Eleven nested dolls: the Surface, then worlds 1 to 10, each inside the last", "Onze poupées emboîtées : la Surface, puis les mondes 1 à 10, chacun dans le précédent"))}</title>'
            f'{"".join(parts)}{face}</svg>')


def hero_legend():
    out = []
    for i in range(11):
        href = "worlds.html#world-%d" % i
        num = "0" if i == 0 else str(i)
        out.append(f'<li><a href="{href}" data-w="{i}" style="--c:{light(i)}"><span class="led"></span>'
                   f'<span class="ln">{num}</span><span class="lt">{e(world_name(i))}</span></a></li>')
    return f'<ol class="legend" aria-label="{e(t("The worlds, outermost first", "Les mondes, du plus grand au plus petit"))}">{"".join(out)}</ol>'


# ---------------------------------------------------------------- index
def render_index():
    A = "assets/" if LANG == "en" else "../assets/"
    loop = [
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
           "Le noyau est l'ingrédient clé de la Graine suivante. Dix fois, jusqu'à ce que le dernier bloc s'ouvre sur quelque chose de bien plus grand.")),
    ]
    steps = "".join(
        f'<li class="step"><div class="step-ic">{tex(i, A, 40)}</div><div><h3>{e(h)}</h3><p>{e(p)}</p></div></li>'
        for i, h, p in loop)

    worlds = []
    for w in C.WORLDS:
        n = w["n"]
        worlds.append(
            f'<li><a class="wcard" href="worlds.html#world-{n}" style="--accent:{light(n)}">'
            f'<img class="px wsoil" src="{A}blocks/world_soil_{n - 1}.png" width="16" height="16" alt="">'
            f'<span class="wnum">{n}</span><span class="wname">{e(w[LANG])}</span>'
            f'<span class="wrule"><span class="led"></span>{e(C.RULES[w["rule"]][LANG])}</span>'
            f'<span class="wline">{e(t(*RULE_SHORT[n]))}</span></a></li>')

    systems = [
        ("heart", t("Doll of Life", "Poupée de vie"),
         t("A nested doll you wear. When you die, a layer breaks instead and you get back up. It gains layers after Worlds 1, 5 and 8.",
           "Une poupée gigogne que tu portes. Quand tu meurs, une couche se brise à ta place et tu te relèves. Elle gagne des couches après les mondes 1, 5 et 8.")),
        ("scale", t("Souls and karma", "Âmes et karma"),
         t("Every item holds a soul. At the Soul Altar, purify it for karma or devour it for power. Karma moves prices, quests and the ending.",
           "Chaque objet porte une âme. À l'Autel des âmes, purifie-la pour le karma ou dévore-la pour la puissance. Le karma change les prix, les quêtes et la fin.")),
        ("shield", t("Gear classes", "Classes d'équipement"),
         t("Every weapon, tool and armour piece is born with one of six classes. Raise it to level 5 with souls, or gamble on a Chance Doll.",
           "Chaque arme, outil ou pièce d'armure naît avec l'une des six classes. Monte-la au niveau 5 avec des âmes, ou tente ta chance avec une Poupée du hasard.")),
        ("users", t("Play as a group", "Joue en groupe"),
         t("Up to eight players share a group, its worlds and its defeated bosses. Bosses grow tougher with every player who joins the fight.",
           "Jusqu'à huit joueurs partagent un groupe, ses mondes et ses boss vaincus. Les boss se renforcent à chaque joueur qui rejoint le combat.")),
    ]
    sys_cards = "".join(
        f'<li class="panel sys"><div class="sys-ic">{icon(ic)}</div><h3>{e(h)}</h3><p>{e(p)}</p></li>' for ic, h, p in systems)

    gallery_keys = [("w01_view", t("World 1, the Toxic Jungle, seen from its Threshold", "Monde 1, la Jungle toxique, vue depuis son Seuil")),
                    ("w02_view", t("World 2, the Giant Veins, under an ember sky", "Monde 2, les Filons géants, sous un ciel de braise")),
                    ("w01_boss", t("The Spore Queen wakes in her arena", "La Reine des spores s'éveille dans son arène")),
                    ("gui_scroll", t("The Artisan's Scroll, first page", "Le Parchemin de l'artisan, première page")),
                    ("gui_station_matrix_workbench", t("The Matrix Workbench and its Seed recipes", "L'Établi matriciel et ses recettes de Graines")),
                    ("gui_journal_2", t("The Journal's karma tab", "L'onglet karma du Journal"))]
    figs = "".join(shot(k, A, c) for k, c in gallery_keys)
    gallery = ""
    if figs:
        gallery = (f'<section class="band"><div class="wrap"><h2>{e(t("Inside the blocks", "Dans les blocs"))}</h2>'
                   f'<p class="sub">{e(t("Captures from the mod running in Minecraft 26.3.", "Captures du mod en jeu, sous Minecraft 26.3."))}</p>'
                   f'<div class="gallery">{figs}</div></div></section>')

    body = f"""
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <h1>Matriochka</h1>
      <p class="tagline">{e(t("Every block can hold a world.", "Chaque bloc peut contenir un monde."))}</p>
      <p class="hero-p">{e(t("A Fabric mod for Minecraft 26.3. Ten worlds, each sealed inside a single block and nested in the one before it. Every world has its own rule, its own creatures, its own station, and a boss guarding the core that opens the next.",
                             "Un mod Fabric pour Minecraft 26.3. Dix mondes, chacun scellé dans un seul bloc et emboîté dans le précédent. Chaque monde a sa règle, ses créatures, sa station, et un boss qui garde le noyau ouvrant le suivant."))}</p>
      <div class="cta">
        <a class="btn btn-primary" href="download.html">{icon('download')}{e(t("Download", "Télécharger"))}</a>
        <a class="btn" href="worlds.html">{icon('layers')}{e(t("Explore the ten worlds", "Explorer les dix mondes"))}</a>
      </div>
      <ul class="chips"><li>Minecraft 26.3</li><li>Fabric</li><li>{e(t("Version", "Version"))} {VERSION}</li><li>{e(t("Solo and multiplayer", "Solo et multijoueur"))}</li></ul>
    </div>
    <div class="hero-art">
      {hero_svg()}
      {hero_legend()}
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>{e(t("How a world opens", "Comment s'ouvre un monde"))}</h2>
    <p class="sub">{e(t("One loop, ten times over. Each pass asks you to unlearn the last world.", "Une seule boucle, dix fois de suite. Chaque tour te demande d'oublier le monde d'avant."))}</p>
    <ol class="steps">{steps}</ol>
  </div>
</section>

<section class="band band-dark">
  <div class="wrap">
    <h2>{e(t("Ten worlds, ten rules", "Dix mondes, dix règles"))}</h2>
    <p class="sub">{e(t("Learning, then mastery, then expertise. World 10 tests everything at once.", "Apprentissage, puis maîtrise, puis expertise. Le monde 10 vérifie tout à la fois."))}</p>
    <ol class="wgrid">{''.join(worlds)}</ol>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2>{e(t("Built to be survived", "Pensé pour qu'on y survive"))}</h2>
    <p class="sub">{e(t("Death teaches. It does not erase hours of progress.", "La mort apprend. Elle n'efface pas des heures de progression."))}</p>
    <ul class="sys-grid">{sys_cards}</ul>
    <p class="more"><a class="btn" href="systems.html">{icon('book-open')}{e(t("How the systems work", "Comment marchent les systèmes"))}</a></p>
  </div>
</section>
{gallery}
<section class="band band-cta">
  <div class="wrap cta-band">
    <div>
      <h2>{e(t("Ready to shrink?", "Prêt à rétrécir ?"))}</h2>
      <p>{e(t("Minecraft 26.3, Fabric Loader 0.20 or newer, Fabric API, GeckoLib 5.5.7 and Java 25.", "Minecraft 26.3, Fabric Loader 0.20 ou plus récent, Fabric API, GeckoLib 5.5.7 et Java 25."))}</p>
    </div>
    <a class="btn btn-primary" href="download.html">{icon('download')}{e(t("Get version", "Obtenir la version"))} {VERSION}</a>
  </div>
</section>
"""
    return page("index", "Matriochka",
                t("Matriochka, a Fabric mod for Minecraft 26.3: ten nested worlds, each sealed in a block, each with its own rule and boss.",
                  "Matriochka, un mod Fabric pour Minecraft 26.3 : dix mondes emboîtés, chacun scellé dans un bloc, avec sa règle et son boss."),
                body)


# ---------------------------------------------------------------- worlds
def render_worlds():
    A = "assets/" if LANG == "en" else "../assets/"
    toc = [f'<li><a href="#world-0" style="--c:{light(0)}"><span class="led"></span><span class="ln">0</span>{e(world_name(0))}</a></li>']
    for w in C.WORLDS:
        toc.append(f'<li><a href="#world-{w["n"]}" style="--c:{light(w["n"])}"><span class="led"></span><span class="ln">{w["n"]}</span>{e(w[LANG])}</a></li>')

    sections = []
    # the Surface
    g = BOSS_OF[0]
    surface_recipes = [r for r in RECIPES.get("matrix_workbench", []) if r["out"] in ("class_table", "soul_altar", "soul_cradle", "return_thread", "chance_doll", "spore_vat")]
    sr = "".join(
        f'<li class="rec"><div class="rec-out">{tex(r["out"], A, 32)}<span>{e(name(r["out"]))}{" ×" + str(r["count"]) if r["count"] > 1 else ""}</span></div>{ingredients(r["inputs"], A)}</li>'
        for r in surface_recipes)
    sections.append(f"""
<section class="world panel" id="world-0" style="--accent:{light(0)}">
  <header class="world-h">
    <span class="world-n">0</span>
    <div><h2>{e(world_name(0))}</h2><p class="world-meta"><span class="led"></span>{e(t("Where it starts", "Là où tout commence"))}</p></div>
  </header>
  <p class="world-rule">{e(t(*RULE_LONG[0]))}</p>
  <div class="world-cols">
    <div class="block">
      <h3>{icon('skull')}{e(t("Boss", "Boss"))}</h3>
      <a class="boss-link" href="bosses.html#boss-{g['id']}">{tex(g['core'], A, 32)}<span><strong>{e(g[LANG])}</strong><small>{fmt(g['hp'])} {e(t("health", "PV"))}</small></span></a>
      <p class="muted">{e(t("It drops the Guardian Core, the Matrix Workbench and four World Soil 0. Your Scroll becomes the Artisan's Journal.", "Il laisse le Noyau du Gardien, l'Établi matriciel et quatre Terres de monde 0. Ton Parchemin devient le Journal de l'artisan."))}</p>
    </div>
    <div class="block">
      <h3>{icon('hammer')}{e(t("Made at the Matrix Workbench", "Fabriqué à l'Établi matriciel"))}</h3>
      <ul class="recs">{sr}</ul>
    </div>
  </div>
</section>""")

    for w in C.WORLDS:
        n = w["n"]
        acc = light(n)
        st, seed = recipe_for(f"seed_{n}")
        seed_html = ingredients(seed["inputs"], A) if seed else ""
        cond = LANGS[LANG].get(f"message.matriochka.seed_planted.{n}", "")
        station = STATION_OF[n]
        st_note = t(*STATION_NOTE[station])
        st_recipes = RECIPES.get(station, [])
        recs = "".join(
            f'<li class="rec"><div class="rec-out">{tex(r["out"], A, 32)}<span>{e(name(r["out"]))}{" ×" + str(r["count"]) if r["count"] > 1 else ""}</span></div>{ingredients(r["inputs"], A)}</li>'
            for r in st_recipes)
        st_make = recipe_for(station)[1]
        st_make_html = ingredients(st_make["inputs"], A) if st_make else ""
        items = [it for it in C.ITEMS if it["world"] == n and it["kind"] not in ("armorset", "seed", "secret", "core", "food")]
        item_html = "".join(
            f'<li class="item" title="{e(it["effect_" + LANG])}">{tex(it["id"], A, 32)}<span><strong>{e(name(it["id"]))}</strong>'
            f'{"<small>" + e(it["effect_" + LANG]) + "</small>" if it["effect_" + LANG] else ""}</span></li>' for it in items)
        armor = next((it for it in C.ITEMS if it["world"] == n and it["kind"] == "armorset"), None)
        armor_html = ""
        if armor:
            pieces = "".join(tex(f'{armor["id"]}_{p}', A, 32, alt=name(f'{armor["id"]}_{p}')) for p in ("helmet", "chestplate", "leggings", "boots"))
            gw = C.GEAR[n]
            armor_html = (f'<div class="armor">{pieces}<p><strong>{e(t("Armour set", "Armure"))}</strong> '
                          f'{e(t(f"{gw[1]} armour, {gw[2]} toughness, a {gw[0]}-damage weapon at this tier.", f"{gw[1]} d’armure, {gw[2]} de robustesse, une arme à {gw[0]} de dégâts à ce palier."))}'
                          f'{(" " + e(armor["effect_" + LANG])) if armor.get("effect_" + LANG) else ""}</p></div>')
        food = next((f for f in C.FOODS if f[3] == n), None)
        food_html = ""
        if food:
            food_html = f'<li class="item">{tex(food[0], A, 32)}<span><strong>{e(name(food[0]))}</strong><small>{e(food[4] if LANG == "en" else food[5])}</small></span></li>'
        mobs = "".join(
            f'<li><a class="chip-link" href="bestiary.html#mob-{m["id"]}">{e(name(m["id"]))}{"<em>" + e(t("elite", "élite")) + "</em>" if m["elite"] else ""}</a></li>'
            for m in MOBS_OF.get(n, []))
        boss = BOSS_OF[n]
        structs = {}
        for (sid, en, fr, role, size, rarity, arch) in C.STRUCTURES[n]:
            structs.setdefault(role, []).append(en if LANG == "en" else fr)
        struct_html = "".join(
            f'<div class="srole"><h4>{e(t(*ROLE[r]))}</h4><p>{e(", ".join(structs[r]))}</p></div>' for r in ROLE if r in structs)
        view = shot(f"w{n:02d}_view", A, t(f"World {n}, {w['en']}, in game", f"Monde {n}, {w['fr']}, en jeu"), "shot shot-wide")
        shots_html = f'<div class="world-shots">{view}</div>' if view else ""
        sections.append(f"""
<section class="world panel" id="world-{n}" style="--accent:{acc}">
  <header class="world-h">
    <span class="world-n">{n}</span>
    <div><h2>{e(w[LANG])}</h2>
    <p class="world-meta"><span class="led"></span>{e(t("Rule", "Règle"))}: {e(C.RULES[w["rule"]][LANG])}<span class="sep"></span>{e(t(*TIER[w["tier"]]))}</p></div>
  </header>
  <p class="world-rule">{e(t(*RULE_LONG[n]))}</p>
  {shots_html}
  <div class="world-cols">
    <div class="block">
      <h3>{icon('sprout')}{e(t("Opening it", "L'ouvrir"))}</h3>
      <div class="seed-row">{tex(f"seed_{n}", A, 40)}<div><strong>{e(name(f"seed_{n}"))}</strong><small>{e(t(f"Plant on tilled World Soil {n - 1}.", f"Se plante sur une Terre de monde {n - 1} bêchée."))} {e(cond)}</small></div></div>
      {seed_html}
    </div>
    <div class="block">
      <h3>{icon('skull')}{e(t("Boss", "Boss"))}</h3>
      <a class="boss-link" href="bosses.html#boss-{boss['id']}">{tex(boss['core'], A, 32)}<span><strong>{e(boss[LANG])}</strong><small>{fmt(boss['hp'])} {e(t("health", "PV"))}, {e(t("drops the", "laisse le"))} {e(name(boss['core']))}</small></span></a>
      <h3 class="h-gap">{icon('bug')}{e(t("Creatures", "Créatures"))}</h3>
      <ul class="chips chips-links">{mobs}</ul>
    </div>
  </div>
  <div class="block">
    <h3>{icon('hammer')}{e(name(station))}</h3>
    <p class="muted">{e(st_note)}</p>
    {('<div class="st-make"><span>' + e(t("Built at the Matrix Workbench from", "Se fabrique à l'Établi matriciel avec")) + "</span>" + st_make_html + "</div>") if st_make_html else ""}
    <ul class="recs">{recs}</ul>
  </div>
  <div class="world-cols">
    <div class="block">
      <h3>{icon('package')}{e(t("What you'll carry", "Ce que tu emporteras"))}</h3>
      <ul class="items">{item_html}{food_html}</ul>
      {armor_html}
    </div>
    <div class="block">
      <h3>{icon('map-pin')}{e(t("Ten structures", "Dix structures"))}</h3>
      {struct_html}
    </div>
  </div>
</section>""")

    body = page_head(t("The ten worlds", "Les dix mondes"),
                     e(t("Each world is planted inside the one before it, and each one bends a rule you thought you knew. Numbers below come straight from the mod's code.",
                         "Chaque monde est planté dans le précédent, et chacun tord une règle que tu croyais connaître. Les chiffres ci-dessous viennent directement du code du mod.")))
    body += f"""
<div class="wrap with-toc">
  <nav class="toc" aria-label="{e(t('Worlds', 'Mondes'))}"><ol>{''.join(toc)}</ol></nav>
  <div class="worlds">{''.join(sections)}</div>
</div>"""
    return page("worlds", t("Worlds", "Mondes"),
                t("The ten worlds of Matriochka: rules, Seeds, stations, recipes, creatures, bosses and structures.",
                  "Les dix mondes de Matriochka : règles, Graines, stations, recettes, créatures, boss et structures."), body)


# ---------------------------------------------------------------- bestiary
BEHAVIOUR_TAGS = [("elite", ("Elite", "Élite"), "shield"), ("nesting", ("Nesting", "Gigogne"), "layers"),
                  ("flying", ("Flying", "Volant"), "wind"), ("aquatic", ("Aquatic", "Aquatique"), "droplets")]


def render_bestiary():
    A = "assets/" if LANG == "en" else "../assets/"
    filt = [f'<button type="button" class="fbtn" aria-pressed="true" data-world="all">{e(t("All worlds", "Tous les mondes"))}</button>']
    groups = []
    for w in C.WORLDS:
        n = w["n"]
        filt.append(f'<button type="button" class="fbtn" aria-pressed="false" data-world="{n}" style="--c:{light(n)}"><span class="led"></span>{n}</button>')
        cards = []
        for m in MOBS_OF[n]:
            tags = "".join(f'<li>{icon(ic)}{e(t(*lab))}</li>' for k, lab, ic in BEHAVIOUR_TAGS if m[k])
            img = (f'<img class="px" src="{A}entities/{m["id"]}.png" width="96" height="96" alt="" loading="lazy">'
                   if m["id"] in ENTITY_TEX else "")
            rare = ""
            if m["rare_drop"] and m["rare_drop"] in ITEM_TEX:
                if True:
                    rare = f'<span class="drop drop-rare">{tex(m["rare_drop"], A, 24)}{e(name(m["rare_drop"]))}<em>{e(t("rare", "rare"))}</em></span>'
            cards.append(f"""
<li class="mob panel" id="mob-{m['id']}">
  <div class="plate">{img}</div>
  <div class="mob-body">
    <h3>{e(name(m['id']))}</h3>
    <p>{e(m['desc_' + LANG])}</p>
    <dl class="stats">
      <div><dt>{icon('heart')}<span>{e(t("Health", "Vie"))}</span></dt><dd>{fmt(m['hp'])}</dd></div>
      <div><dt>{icon('swords')}<span>{e(t("Damage", "Dégâts"))}</span></dt><dd>{fmt(m['dmg'])}</dd></div>
    </dl>
    <div class="drops"><span class="drop">{tex(m['drop'], A, 24)}{e(name(m['drop']))}</span>{rare}</div>
    {('<ul class="tags">' + tags + '</ul>') if tags else ''}
  </div>
</li>""")
        groups.append(f"""
<section class="mgroup" data-world="{n}" id="world-{n}" style="--accent:{light(n)}">
  <h2><span class="world-n sm">{n}</span>{e(w[LANG])}<span class="led"></span><small>{e(C.RULES[w['rule']][LANG])}</small></h2>
  <ul class="mobs">{''.join(cards)}</ul>
</section>""")

    peoples = []
    for pid, en, fr, w in C.PEOPLES:
        img = f'<img class="px" src="{A}entities/{pid}.png" width="64" height="64" alt="" loading="lazy">' if pid in ENTITY_TEX else ""
        peoples.append(f'<li class="person" style="--accent:{light(w)}"><div class="plate sm">{img}</div><div><strong>{e(en if LANG == "en" else fr)}</strong><small>{e(world_name(w))}</small></div></li>')

    body = page_head(t("Bestiary", "Bestiaire"),
                     e(t("Fifty creatures, five per world. Health and damage already include the world's multiplier: health grows by 35% and damage by 20% with every world you go down.",
                         "Cinquante créatures, cinq par monde. La vie et les dégâts incluent déjà le multiplicateur du monde : la vie augmente de 35 % et les dégâts de 20 % à chaque monde franchi.")))
    body += f"""
<div class="wrap">
  <div class="filters js-only" role="group" aria-label="{e(t('Filter by world', 'Filtrer par monde'))}">{''.join(filt)}</div>
  <div class="legend-tags">
    <p><strong>{e(t("Nesting", "Gigogne"))}</strong> {e(t("creatures split open when they die and release a smaller, faster one. Elites guard the world's best drops.", "les créatures gigognes s'ouvrent à leur mort et libèrent une version plus petite et plus rapide. Les élites gardent les meilleurs butins du monde."))}</p>
  </div>
  {''.join(groups)}
  <section class="mgroup peoples" id="peoples">
    <h2>{e(t("The peoples", "Les peuples"))}</h2>
    <p class="sub">{e(t("Every world has its own people, with villages, traders and quest givers. How they greet you depends on your karma. On the Surface, the Doll Peddler wanders between villages.",
                         "Chaque monde a son peuple, avec ses villages, ses marchands et ses donneurs de quêtes. Leur accueil dépend de ton karma. Sur la Surface, le Colporteur de poupées erre de village en village."))}</p>
    <ul class="people">{''.join(peoples)}</ul>
  </section>
</div>"""
    return page("bestiary", t("Bestiary", "Bestiaire"),
                t("Every creature of Matriochka with its health, damage, behaviour and drops.",
                  "Toutes les créatures de Matriochka, avec leur vie, leurs dégâts, leur comportement et leur butin."), body)


# ---------------------------------------------------------------- bosses
def tier_timing(world):
    tele = 30 if world <= 3 else 20 if world <= 6 else 15 if world <= 9 else 12
    opening = 60 if world <= 3 else 50 if world <= 6 else 40 if world <= 9 else 30
    return tele / 20, tele * 2 / 20, opening / 20


def secs(x):
    s = fmt(round(x, 2))
    return f"{s} s"


def render_bosses():
    A = "assets/" if LANG == "en" else "../assets/"
    labels = [t("Light", "Légère"), t("Medium", "Moyenne"), t("Signature", "Signature"), t("Final phase", "Phase finale")]
    cards = []
    for b in C.BOSSES:
        w = b["world"]
        tele, tele_sig, opening = tier_timing(w)
        if b["id"] == "the_unfinished":
            phases = t("Ten shells, one every 10% of its health", "Dix enveloppes, une tous les 10 % de sa vie")
            atk = (f'<li><span class="atk-l">{e(t("Shells 1 to 9", "Enveloppes 1 à 9"))}</span>'
                   f'{e(t("Each broken shell takes the face of an earlier world and replays its attacks.", "Chaque enveloppe brisée prend le visage d’un monde précédent et rejoue ses attaques."))}</li>'
                   f'<li><span class="atk-l">{e(labels[3])}</span>{e(b["atk"][3][0 if LANG == "en" else 1])}</li>')
        else:
            phases = t("Phases at ", "Phases à ") + (t(" and ", " et ").join(pct(int(p * 100)) for p in b["phases"])) + t(" of its health", " de sa vie")
            atk = "".join(f'<li><span class="atk-l">{e(labels[i])}</span>{e(a[0] if LANG == "en" else a[1])}</li>' for i, a in enumerate(b["atk"]))
        img = f'<img class="px" src="{A}entities/{b["id"]}.png" width="128" height="128" alt="" loading="lazy">' if b["id"] in ENTITY_TEX else ""
        story = LANGS[LANG].get(f"message.matriochka.boss_down.{w}", "")
        bshot = shot(f"w{w:02d}_boss", A, t(f"{b['en']}, in its arena", f"{b['fr']}, dans son arène"), "shot shot-wide") if w > 0 else ""
        cards.append(f"""
<section class="boss panel" id="boss-{b['id']}" style="--accent:{light(w)}">
  <header class="boss-h">
    <div class="plate lg">{img}</div>
    <div>
      <p class="world-meta"><span class="led"></span>{e(world_name(w))}{('<span class="sep"></span>' + e(t("World", "Monde")) + " " + str(w)) if w else ""}</p>
      <h2>{e(b[LANG])}</h2>
      <dl class="stats stats-lg">
        <div><dt>{icon('heart')}<span>{e(t("Health, solo", "Vie, en solo"))}</span></dt><dd>{fmt(b['hp'])}</dd></div>
        <div><dt>{icon('swords')}<span>{e(t("Heavy hit", "Coup fort"))}</span></dt><dd>{fmt(b['dmg'])}</dd></div>
        <div><dt>{icon('clock')}<span>{e(t("Warning", "Annonce"))}</span></dt><dd>{secs(tele)}</dd></div>
        <div><dt>{icon('hourglass')}<span>{e(t("Opening", "Ouverture"))}</span></dt><dd>{secs(opening)}</dd></div>
      </dl>
    </div>
  </header>
  {bshot}
  <div class="world-cols">
    <div class="block"><h3>{icon('swords')}{e(t("Attacks", "Attaques"))}</h3><ul class="atks">{atk}</ul></div>
    <div class="block">
      <h3>{icon('layers')}{e(t("Phases", "Phases"))}</h3><p>{e(phases)}.</p>
      <h3 class="h-gap">{icon('gem')}{e(t("Reward", "Récompense"))}</h3>
      <p class="reward">{tex(b['core'], A, 32)}<span><strong>{e(name(b['core']))}</strong><small>{e(t("plus 100 souls for every player in the fight", "et 100 âmes pour chaque joueur présent au combat"))}</small></span></p>
      <details class="spoiler"><summary>{e(t("What its fall reveals", "Ce que révèle sa chute"))}</summary><p>{e(story)}</p></details>
    </div>
  </div>
</section>""")

    rows = []
    for tier, worlds, wn in ((t("Surface to World 3", "Surface au monde 3"), "0", 0), (t("Worlds 4 to 6", "Mondes 4 à 6"), "4", 4),
                             (t("Worlds 7 to 9", "Mondes 7 à 9"), "7", 7), (t("World 10", "Monde 10"), "10", 10)):
        a, s, o = tier_timing(wn)
        rows.append(f"<tr><th scope=\"row\">{e(tier)}</th><td>{secs(a)}</td><td>{secs(s)}</td><td>{secs(o)}</td></tr>")
    mp = "".join(f"<tr><th scope=\"row\">{p}</th><td>×{fmt(round(1 + 0.6 * (p - 1), 1))}</td></tr>" for p in (1, 2, 4, 8))

    body = page_head(t("Bosses", "Boss"),
                     e(t("Eleven fights, each built the same way: an announcement you can read, a fast and dangerous attack, then an opening. Hit a boss during its opening and it takes 1.5 times the damage; outside of it, only three quarters.",
                         "Onze combats, tous construits pareil : une annonce lisible, une attaque rapide et dangereuse, puis une ouverture. Frappé pendant son ouverture, un boss subit 1,5 fois les dégâts ; en dehors, seulement les trois quarts.")))
    body += f"""
<div class="wrap">
  <div class="world-cols rules-tables">
    <div class="panel block">
      <h3>{icon('clock')}{e(t("Reading the fight", "Lire le combat"))}</h3>
      <div class="tbl"><table>
        <thead><tr><th scope="col">{e(t("Tier", "Palier"))}</th><th scope="col">{e(t("Warning", "Annonce"))}</th><th scope="col">{e(t("Signature warning", "Annonce signature"))}</th><th scope="col">{e(t("Opening", "Ouverture"))}</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
      <p class="muted">{e(t("Bosses never take damage while changing phase. The Spore Queen's cocoon holds until its nodes are broken.", "Un boss ne prend aucun dégât pendant un changement de phase. Le cocon de la Reine des spores tient tant que ses nœuds ne sont pas brisés."))}</p>
    </div>
    <div class="panel block">
      <h3>{icon('users')}{e(t("In a group", "En groupe"))}</h3>
      <div class="tbl"><table>
        <thead><tr><th scope="col">{e(t("Players nearby", "Joueurs à proximité"))}</th><th scope="col">{e(t("Boss health", "Vie du boss"))}</th></tr></thead>
        <tbody>{mp}</tbody>
      </table></div>
      <p class="muted">{e(t("Counted within 48 blocks when the boss wakes. Everyone within 64 blocks at its death shares the victory.", "Compté dans un rayon de 48 blocs au réveil du boss. Tous ceux à moins de 64 blocs à sa mort partagent la victoire."))}</p>
    </div>
  </div>
  <div class="bosses">{''.join(cards)}</div>
</div>"""
    return page("bosses", t("Bosses", "Boss"),
                t("The eleven bosses of Matriochka: health, attacks, phases, timings and rewards.",
                  "Les onze boss de Matriochka : vie, attaques, phases, timings et récompenses."), body)


# ---------------------------------------------------------------- systems
def render_systems():
    A = "assets/" if LANG == "en" else "../assets/"
    d = LANGS[LANG]
    _, cradle = recipe_for("soul_cradle")
    _, chance = recipe_for("chance_doll")
    _, thread = recipe_for("return_thread")
    rar = [("common", t("Common", "Commun")), ("rare", t("Rare", "Rare")), ("epic", t("Epic", "Épique")), ("legendary", t("Legendary", "Légendaire"))]
    rar_rows = "".join(f"<tr><th scope=\"row\">{e(l)}</th><td>{C.RARITY_SOUL[k]}</td></tr>" for k, l in rar)
    karma = [("+50", "light2"), ("+25", "light1"), ("0", "neutral"), ("−25", "dark1"), ("−50", "dark2")]
    karma_rows = "".join(f'<li class="k k-{k}"><span class="kv">{v}</span><p>{e(d["journal.matriochka.karma." + k])}</p></li>' for v, k in karma)
    cls_rows = "".join(
        f"<tr><th scope=\"row\">{e(en if LANG == 'en' else fr)}</th><td>{e(den if LANG == 'en' else dfr)}</td><td>{e(slot_label(slot))}</td></tr>"
        for (cid, en, fr, slot, den, dfr) in C.CLASSES)
    up_rows = "".join(f"<tr><th scope=\"row\">{lv}</th><td>+{pct(b)}</td><td>{c}</td></tr>" for lv, b, c in ((2, 10, 10), (3, 20, 30), (4, 35, 90), (5, 50, 270)))
    cap_rows = "".join(f"<tr><th scope=\"row\">{e(t(f'World {w} done', f'Monde {w} terminé'))}</th><td>{lv}</td></tr>" for w, lv in ((2, 2), (4, 3), (6, 4), (8, 5)))
    titles = [v for k, v in d.items() if k.startswith("title.matriochka.")]
    nq = len(C.QUESTS)
    nach = sum(len(v) for v in C.ACH.values())

    death = [t("If your Doll of Life has a layer left, it breaks and you get back up on the spot. A doll can save you at most once a minute.",
               "Si ta Poupée de vie a encore une couche, elle se brise et tu te relèves sur place. Une poupée peut te sauver au plus une fois par minute."),
             t("Otherwise you die, and a death chest keeps your inventory where you fell. It never despawns; inside a boss arena it waits at the entrance.",
               "Sinon tu meurs, et un coffre de mort garde ton inventaire là où tu es tombé. Il ne disparaît jamais ; dans une arène de boss, il t'attend à l'entrée."),
             t("If you placed a charged Soul Cradle in that world, you wake up next to it.",
               "Si tu as posé un Berceau d'âme chargé dans ce monde, tu te réveilles à côté."),
             t("If not, you are sent back outside, to your usual spawn point.",
               "Sinon, tu es renvoyé dehors, à ton point de réapparition habituel.")]
    death_html = "".join(f"<li>{e(x)}</li>" for x in death)

    nesting = [(t("Doll of Life", "Poupée de vie"), t("Each layer survives one death", "Chaque couche survit à une mort"), t("Worlds 1, 5, 8", "Mondes 1, 5, 8")),
               (t("Nesting chests", "Coffres gigognes"), t("A chest that holds a smaller one", "Un coffre qui en contient un plus petit"), t("World 2", "Monde 2")),
               (t("Nesting creatures", "Créatures gigognes"), t("A defeated mob releases a smaller one", "Un mob vaincu en libère un plus petit"), t("World 2", "Monde 2")),
               (t("Refuge doll", "Poupée-refuge"), t("A pocket base you carry", "Une base de poche que tu transportes"), t("World 3", "Monde 3")),
               (t("Layered armour", "Armures à couches"), t("One layer protects the next", "Une couche protège la suivante"), t("World 4", "Monde 4")),
               (t("The final boss", "Le boss final"), t("Ten shells, one per world", "Dix enveloppes, une par monde"), t("World 10", "Monde 10"))]
    nest_rows = "".join(f"<tr><th scope=\"row\">{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in nesting)

    cmds = [("/matriochka group info", t("Your group, its members and defeated bosses", "Ton groupe, ses membres et ses boss vaincus")),
            ("/matriochka group invite <player>", t("Invite a player into your group", "Inviter un joueur dans ton groupe")),
            ("/matriochka group join", t("Accept the pending invitation", "Accepter l'invitation en attente")),
            ("/matriochka group leave", t("Leave your group", "Quitter ton groupe")),
            ("/matriochka karma show", t("Your karma and souls", "Ton karma et tes âmes"))]
    cmd_rows = "".join(f"<tr><th scope=\"row\"><code>{e(c)}</code></th><td>{e(x)}</td></tr>" for c, x in cmds)

    sh = lambda k, c: shot(k, A, c)
    body = page_head(t("Systems", "Systèmes"),
                     e(t("What keeps you alive, what you trade for power, and how your gear grows. Everything here works the same in solo and on a server.",
                         "Ce qui te garde en vie, ce que tu échanges contre de la puissance, et comment ton équipement grandit. Tout fonctionne pareil en solo et sur serveur.")))
    body += f"""
<div class="wrap sys-page">
  <nav class="subnav" aria-label="{e(t('On this page', 'Sur cette page'))}"><ul>
    <li><a href="#survival">{e(t("Survival", "Survie"))}</a></li><li><a href="#souls">{e(t("Souls and karma", "Âmes et karma"))}</a></li>
    <li><a href="#classes">{e(t("Classes", "Classes"))}</a></li><li><a href="#nesting">{e(t("Nesting", "Gigogne"))}</a></li>
    <li><a href="#groups">{e(t("Groups", "Groupes"))}</a></li><li><a href="#journal">{e(t("Journal", "Journal"))}</a></li>
  </ul></nav>

  <section class="panel sect" id="survival" style="--accent:#d8402f">
    <h2>{icon('heart')}{e(t("Survival", "Survie"))}</h2>
    <div class="world-cols">
      <div>
        <div class="feature">{tex('life_doll', A, 48)}<div><h3>{e(name('life_doll'))}</h3>
        <p>{e(t("You carry a doll made of layers. It gets its first layer when the Spore Queen falls, a second after the Light Eater and a third after the Master of Seasons. Every boss you beat restores one layer, and the Soul Altar rebuilds one for 50 souls.",
                 "Tu portes une poupée faite de couches. Elle reçoit sa première couche à la chute de la Reine des spores, une deuxième après le Mangeur de lumière et une troisième après le Maître des saisons. Chaque boss vaincu restaure une couche, et l'Autel des âmes en reconstruit une pour 50 âmes."))}</p></div></div>
        <h3>{e(t("When you die", "Quand tu meurs"))}</h3>
        <ol class="numbered">{death_html}</ol>
      </div>
      <div>
        <div class="feature">{tex('soul_cradle', A, 48)}<div><h3>{e(name('soul_cradle'))}</h3>
        <p>{e(t("A small painted cradle that lets you respawn inside a world. It holds 3 charges; feed it one resource from that world and 5 souls to add another. One active cradle per player and per world.",
                 "Un petit berceau en bois peint qui te permet de réapparaître dans un monde. Il contient 3 charges ; donne-lui une ressource de ce monde et 5 âmes pour en ajouter une. Un seul berceau actif par joueur et par monde."))}</p>
        {ingredients(cradle['inputs'], A) if cradle else ''}</div></div>
        <div class="feature">{tex('return_thread', A, 48)}<div><h3>{e(name('return_thread'))}</h3>
        <p>{e(t("Pulls you back to the World Block. You can also simply walk back onto the Threshold where you arrived.", "Te ramène au Bloc-monde. Tu peux aussi simplement revenir sur le Seuil où tu es arrivé."))}</p>
        {ingredients(thread['inputs'], A) if thread else ''}</div></div>
        <div class="feature">{tex('cracked_doll', A, 48)}<div><h3>{e(t("A broken World Block", "Un Bloc-monde cassé"))}</h3>
        <p>{e(t("Break a World Block and everyone inside is pushed out safely. The block becomes a Cracked Doll tied to that exact world: set it down again and the world comes back with its bases and chests, unstable for 20 minutes. It is also how you move a world.",
                 "Casse un Bloc-monde et tous ceux qui sont dedans sont expulsés sans dommage. Le bloc devient une Poupée fêlée liée à ce monde précis : repose-la et le monde revient avec ses bases et ses coffres, instable pendant 20 minutes. C'est aussi comme ça qu'on déplace un monde."))}</p></div></div>
      </div>
    </div>
  </section>

  <section class="panel sect" id="souls" style="--accent:#D9A441">
    <h2>{icon('scale')}{e(t("Souls and karma", "Âmes et karma"))}</h2>
    <p class="sect-lead">{e(t("Every item carries a soul whose weight depends on its rarity. Put it on the Soul Altar and choose, for good: purify it to free the soul and gain karma, or devour it to absorb the soul and lose karma. Either way you keep the souls, which pay for class upgrades, cradle charges and doll layers.",
                                "Chaque objet porte une âme dont le poids dépend de sa rareté. Pose-le sur l'Autel des âmes et choisis, définitivement : purifie-le pour libérer l'âme et gagner du karma, ou dévore-le pour absorber l'âme et perdre du karma. Dans les deux cas tu gardes les âmes, qui paient les améliorations de classe, les charges de berceau et les couches de poupée."))}</p>
    <div class="world-cols">
      <div>
        <div class="tbl"><table><thead><tr><th scope="col">{e(t("Rarity", "Rareté"))}</th><th scope="col">{e(t("Souls", "Âmes"))}</th></tr></thead><tbody>{rar_rows}<tr><th scope="row">{e(t("Any boss", "Un boss"))}</th><td>100</td></tr></tbody></table></div>
        <p class="muted">{e(t("Karma runs from −100 to +100. An item gives one point of karma per 10 souls, and less each time you repeat the same offering. Quests with a choice move it by 5 or 10.",
                               "Le karma va de −100 à +100. Un objet rapporte un point de karma par tranche de 10 âmes, et de moins en moins si tu répètes la même offrande. Les quêtes à choix le déplacent de 5 ou 10."))}</p>
        {sh('gui_station_soul_altar', t('The Soul Altar', "L'Autel des âmes"))}
      </div>
      <div>
        <h3>{e(t("What karma changes", "Ce que change le karma"))}</h3>
        <ul class="karma">{karma_rows}</ul>
        <p class="muted">{e(t("At ±100, karma also tilts the variants of the worlds you open, and it decides between two of the three endings: seal the creature away, or absorb its power.",
                               "À ±100, le karma oriente aussi les variantes des mondes que tu ouvres, et il départage deux des trois fins : sceller de nouveau la créature, ou absorber son pouvoir."))}</p>
      </div>
    </div>
  </section>

  <section class="panel sect" id="classes" style="--accent:#7fd3ff">
    <h2>{icon('shield')}{e(t("Gear classes", "Classes d'équipement"))}</h2>
    <p class="sect-lead">{e(t("Every weapon, tool and armour piece gets a random class when it is crafted. The Class Table raises its level with souls; your progression caps how far you can go.",
                                "Chaque arme, outil ou pièce d'armure reçoit une classe au hasard à sa fabrication. La Table de classe monte son niveau avec des âmes ; ta progression limite jusqu'où tu peux aller."))}</p>
    <div class="tbl"><table><thead><tr><th scope="col">{e(t("Class", "Classe"))}</th><th scope="col">{e(t("Bonuses", "Bonus"))}</th><th scope="col">{e(t("Found on", "Sur"))}</th></tr></thead><tbody>{cls_rows}</tbody></table></div>
    <div class="world-cols">
      <div><h3>{e(t("Upgrading", "Améliorer"))}</h3>
        <div class="tbl"><table><thead><tr><th scope="col">{e(t("Level", "Niveau"))}</th><th scope="col">{e(t("Total bonus", "Bonus total"))}</th><th scope="col">{e(t("Souls", "Âmes"))}</th></tr></thead><tbody>{up_rows}</tbody></table></div>
        <p class="muted">{e(t("Level 1 to 5 costs 400 souls per piece.", "Du niveau 1 au niveau 5 : 400 âmes par pièce."))}</p></div>
      <div><h3>{e(t("Level cap", "Niveau maximal"))}</h3>
        <div class="tbl"><table><thead><tr><th scope="col">{e(t("Progression", "Progression"))}</th><th scope="col">{e(t("Max level", "Niveau max"))}</th></tr></thead><tbody>{cap_rows}</tbody></table></div></div>
    </div>
    <div class="feature">{tex('chance_doll', A, 48)}<div><h3>{e(name('chance_doll'))}</h3>
      <p>{e(t("Rerolls an item into a different class it can hold, and keeps its level. The first reroll costs 20 souls, and the price doubles each time on the same item: 20, 40, 80, 160.",
               "Relance un objet vers une autre classe compatible, en gardant son niveau. Le premier changement coûte 20 âmes, et le prix double à chaque fois sur le même objet : 20, 40, 80, 160."))}</p>
      {ingredients(chance['inputs'], A) if chance else ''}</div></div>
    {sh('gui_station_class_table', t('The Class Table', 'La Table de classe'))}
  </section>

  <section class="panel sect" id="nesting" style="--accent:#B3261E">
    <h2>{icon('layers')}{e(t("Things inside things", "Des choses dans des choses"))}</h2>
    <p class="sect-lead">{e(t("The name is the rule: something can always hold something else. These systems unlock as the story goes on.", "Le nom est la règle : une chose peut toujours en contenir une autre. Ces systèmes se débloquent au fil de l'histoire."))}</p>
    <div class="tbl"><table><thead><tr><th scope="col">{e(t("System", "Système"))}</th><th scope="col">{e(t("Effect", "Effet"))}</th><th scope="col">{e(t("Unlocked", "Déblocage"))}</th></tr></thead><tbody>{nest_rows}</tbody></table></div>
    <h3>{e(t("Gates", "Verrous"))}</h3>
    <ul class="plain">
      <li>{e(t("Enchanting, anvils and the Nether open after World 2.", "Enchantements, enclumes et Nether s'ouvrent après le monde 2."))}</li>
      <li>{e(t("Diamonds come back in World 5: four Diamond Fragments make one at the Dark Altar.", "Le diamant revient dans le monde 5 : quatre Fragments de diamant en donnent un à l'Autel obscur."))}</li>
      <li>{e(t("Elytra stay grounded in Worlds 4, 6 and 9 until World 8 is done.", "Les élytres restent clouées au sol dans les mondes 4, 6 et 9 tant que le monde 8 n'est pas terminé."))}</li>
      <li>{e(t("The End opens after World 8.", "L'End s'ouvre après le monde 8."))}</li>
    </ul>
  </section>

  <section class="panel sect" id="groups" style="--accent:#9af0ff">
    <h2>{icon('users')}{e(t("Groups and servers", "Groupes et serveurs"))}</h2>
    <p class="sect-lead">{e(t("A player alone is a group of one. Worlds, progression and permissions belong to the group: up to eight players by default. Each group gets its own 3,000 by 3,000 block parcel in every world, walled off from the others, and a World Block can only be used by its group.",
                                "Un joueur seul forme un groupe d'une personne. Les mondes, la progression et les permissions appartiennent au groupe : jusqu'à huit joueurs par défaut. Chaque groupe reçoit sa propre parcelle de 3 000 sur 3 000 blocs dans chaque monde, séparée des autres, et un Bloc-monde ne sert qu'à son groupe."))}</p>
    <div class="tbl"><table><tbody>{cmd_rows}</tbody></table></div>
    <p class="muted">{e(t("The mod runs on the server and on every client. All rules, damage and rewards are decided by the server; nothing needs an online account or service.",
                           "Le mod s'installe sur le serveur et sur chaque client. Règles, dégâts et récompenses sont décidés par le serveur ; aucun compte ni service en ligne n'est nécessaire."))}</p>
  </section>

  <section class="panel sect" id="journal" style="--accent:#E8D2A6">
    <h2>{icon('book-open')}{e(t("The Journal, quests and achievements", "Le Journal, les quêtes et les succès"))}</h2>
    <p class="sect-lead">{e(t(f"The Artisan's Scroll arrives on your first login and turns into the Journal when the Guardian falls. Its tabs track your objective, quests, karma and worlds. There are {nq} optional quests (4 on the Surface, 6 per world) and {nach} achievements, 10 per world, two of them hidden. Fifty Journal pages and ten hidden dolls are scattered through the worlds; nest the dolls in order and something smaller opens.",
                                f"Le Parchemin de l'artisan arrive à ta première connexion et devient le Journal quand le Gardien tombe. Ses onglets suivent ton objectif, tes quêtes, ton karma et tes mondes. Il y a {nq} quêtes facultatives (4 sur la Surface, 6 par monde) et {nach} succès, 10 par monde dont deux cachés. Cinquante pages du Journal et dix poupées cachées sont dispersées dans les mondes ; emboîte les poupées dans l'ordre et quelque chose de plus petit s'ouvre."))}</p>
    <div class="world-cols">
      {sh('gui_journal_0', t("The Journal's objective tab", "L'onglet objectif du Journal"))}
      {sh('gui_journal_1', t('Quests', 'Les quêtes'))}
    </div>
    <h3>{e(t("Titles you can earn", "Titres à gagner"))}</h3>
    <ul class="chips">{''.join(f'<li>{e(x)}</li>' for x in titles)}</ul>
  </section>
</div>"""
    return page("systems", t("Systems", "Systèmes"),
                t("Doll of Life, death and respawn, souls and karma, gear classes, groups and quests in Matriochka.",
                  "Poupée de vie, mort et réapparition, âmes et karma, classes d'équipement, groupes et quêtes dans Matriochka."), body)


def slot_label(slot):
    return {"armor": t("Armour", "Armures"), "weapon_armor": t("Weapons, armour", "Armes, armures"),
            "armor_weapon": t("Armour, light weapons", "Armures, armes légères"), "tool": t("Tools", "Outils")}[slot]


# ---------------------------------------------------------------- download
def render_download():
    reqs = [("Minecraft", "26.3", t("Java Edition", "Édition Java")),
            ("Fabric Loader", "0.20+", t("Install it for 26.3 with the Fabric installer", "À installer pour la 26.3 avec l'installeur Fabric")),
            ("Fabric API", t("latest for 26.3", "dernière pour la 26.3"), t("Goes in the mods folder", "Dans le dossier mods")),
            ("GeckoLib", "5.5.7", t("Animated models of bosses and creatures", "Modèles animés des boss et créatures")),
            ("Java", "25", t("Bundled with the official launcher", "Fourni avec le launcher officiel"))]
    req = "".join(f'<li class="req"><span class="req-n">{e(n)}</span><span class="req-v">{e(v)}</span><small>{e(s)}</small></li>' for n, v, s in reqs)
    steps = [t("Install Fabric Loader for Minecraft 26.3.", "Installe Fabric Loader pour Minecraft 26.3."),
             t(f"Download matriochka-{VERSION}.jar from the GitHub releases.", f"Télécharge matriochka-{VERSION}.jar depuis les versions GitHub."),
             t("Put it in your mods folder with Fabric API and GeckoLib.", "Place-le dans ton dossier mods avec Fabric API et GeckoLib."),
             t("Launch the Fabric profile and create a new world. The Artisan's Scroll is waiting in your inventory.", "Lance le profil Fabric et crée un nouveau monde. Le Parchemin de l'artisan t'attend dans l'inventaire.")]
    steps_html = "".join(f"<li>{e(s)}</li>" for s in steps)
    cfg = [("progressionGates", "true", t("Lock enchanting, the Nether, the End and elytra behind progression", "Verrouille enchantements, Nether, End et élytres derrière la progression")),
           ("mobHealthMultiplier", "1.0", t("Scales the health of every creature", "Ajuste la vie de toutes les créatures")),
           ("mobDamageMultiplier", "1.0", t("Scales the damage of every creature", "Ajuste les dégâts de toutes les créatures")),
           ("maxGroupSize", "8", t("Players per group", "Joueurs par groupe")),
           ("screenShake", "true", t("Camera shake during big hits", "Tremblements de caméra lors des gros coups")),
           ("difficulty", '"normal"', t("Overall difficulty preset", "Préréglage général de difficulté"))]
    cfg_rows = "".join(f"<tr><th scope=\"row\"><code>{k}</code></th><td><code>{e(v)}</code></td><td>{e(d)}</td></tr>" for k, v, d in cfg)
    body = page_head(t("Download", "Télécharger"),
                     e(t(f"Version {VERSION} for Minecraft 26.3 on Fabric. Install it on the client to play solo, and on both server and clients to play together.",
                         f"Version {VERSION} pour Minecraft 26.3 sous Fabric. Installe-la côté client pour jouer en solo, et sur le serveur et chaque client pour jouer ensemble.")))
    body += f"""
<div class="wrap dl">
  <div class="dl-main panel" style="--accent:#D9A441">
    <h2>{icon('package')}Matriochka {VERSION}</h2>
    <ul class="sources">
      <li><a class="src src-on" href="{RELEASES}">{icon('github')}<span><strong>GitHub</strong><small>{e(t("Releases, changelog and source", "Versions, changements et code source"))}</small></span>{icon('download', 'ic ic-end')}</a></li>
      <li><span class="src src-off" aria-disabled="true">{icon('package')}<span><strong>Modrinth</strong><small>{e(t("Coming soon", "Bientôt disponible"))}</small></span></span></li>
      <li><span class="src src-off" aria-disabled="true">{icon('package')}<span><strong>CurseForge</strong><small>{e(t("Coming soon", "Bientôt disponible"))}</small></span></span></li>
    </ul>
    <h3>{e(t("Requirements", "Prérequis"))}</h3>
    <ul class="reqs">{req}</ul>
    <h3>{e(t("Installing", "Installation"))}</h3>
    <ol class="numbered">{steps_html}</ol>
  </div>
  <aside class="dl-side">
    <div class="panel note" style="--accent:#7fd3ff">
      <h3>{icon('info')}Lunar Client</h3>
      <p>{e(t("Matriochka is built on Fabric so that it can run on Lunar Client, whose mod loading relies on Fabric. Support for Minecraft 26.3 together with GeckoLib is still being confirmed there: if the mod does not load, play it with the official launcher or Prism Launcher on a Fabric profile in the meantime.",
               "Matriochka repose sur Fabric pour pouvoir tourner sur Lunar Client, dont le chargement de mods s'appuie sur Fabric. La prise en charge de Minecraft 26.3 avec GeckoLib y est encore en cours de vérification : si le mod ne se charge pas, joue en attendant avec le launcher officiel ou Prism Launcher sur un profil Fabric."))}</p>
    </div>
    <div class="panel note" style="--accent:#b7e04a">
      <h3>{icon('book-open')}{e(t("Wiki", "Wiki"))}</h3>
      <p>{e(t("Recipes, step-by-step guides and answers to common questions live on the GitHub wiki.", "Recettes, guides pas à pas et réponses aux questions courantes sont sur le wiki GitHub."))}</p>
      <p><a class="btn" href="{WIKI}">{icon('external-link')}{e(t("Open the wiki", "Ouvrir le wiki"))}</a></p>
    </div>
    <div class="panel note" style="--accent:#d8402f">
      <h3>{icon('circle-alert')}{e(t("Early version", "Version précoce"))}</h3>
      <p>{e(t("Names, numbers and balance can still change between versions. Back up your worlds before updating, and report anything odd on the issue tracker.", "Les noms, les chiffres et l'équilibrage peuvent encore changer d'une version à l'autre. Sauvegarde tes mondes avant de mettre à jour, et signale tout comportement étrange sur le suivi des tickets."))}</p>
      <p><a class="btn" href="{REPO}/issues">{icon('bug')}{e(t("Report a bug", "Signaler un bug"))}</a></p>
    </div>
  </aside>
  <section class="panel dl-cfg">
    <h2>{icon('cpu')}{e(t("Server configuration", "Configuration du serveur"))}</h2>
    <p class="muted">{e(t("The file config/matriochka.json is created on first launch. Edit it with the server stopped.", "Le fichier config/matriochka.json est créé au premier lancement. Modifie-le serveur arrêté."))}</p>
    <div class="tbl"><table><thead><tr><th scope="col">{e(t("Key", "Clé"))}</th><th scope="col">{e(t("Default", "Défaut"))}</th><th scope="col">{e(t("What it does", "Rôle"))}</th></tr></thead><tbody>{cfg_rows}</tbody></table></div>
  </section>
</div>"""
    return page("download", t("Download", "Télécharger"),
                t("Download Matriochka for Minecraft 26.3 on Fabric: requirements, installation, Lunar Client and server configuration.",
                  "Télécharger Matriochka pour Minecraft 26.3 sous Fabric : prérequis, installation, Lunar Client et configuration serveur."), body)


# ---------------------------------------------------------------- main
RENDER = {"index": render_index, "worlds": render_worlds, "bestiary": render_bestiary,
          "bosses": render_bosses, "systems": render_systems, "download": render_download}


def main():
    global LANG
    os.makedirs(DOCS, exist_ok=True)
    copy_assets()
    web = os.path.join(HERE, "site")
    for f in ("site.css", "site.js"):
        shutil.copy2(os.path.join(web, f), os.path.join(DOCS, "assets", f))
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    written = []
    for lang in ("en", "fr"):
        LANG = lang
        out_dir = DOCS if lang == "en" else os.path.join(DOCS, "fr")
        os.makedirs(out_dir, exist_ok=True)
        for slug, fn in RENDER.items():
            p = os.path.join(out_dir, f"{slug}.html")
            with open(p, "w", encoding="utf-8") as f:
                f.write(fn())
            written.append(os.path.relpath(p, ROOT))
    print(f"{len(written)} pages, {len(SHOTS)} screenshots")
    for w in written:
        print(" ", w)


if __name__ == "__main__":
    main()
