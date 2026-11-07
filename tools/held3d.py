"""Doll items in 3D wherever they are held, worn, framed or dropped; their flat sprite in the inventory.

A matryoshka is turned on a lathe, so its model is too: every run of sprite rows of the same width becomes a round
slab (a square one, at this scale) as deep as it is wide, its front painted with those rows of the sprite itself, its
back and sides with the sprite's edge and middle columns (no face behind), its top and bottom with the row's middle.
Seen from the front the doll is exactly its sprite; turned, it has the body a carved doll has.

The item definition picks the model by where the item is drawn: the sprite in the inventory and on the hotbar
(gui), the turned doll everywhere else (hands, head, item frames, the ground, the shoulder doll).
"""
import json
import os

from PIL import Image

# the doll items: every trophy doll, every hidden doll and the doll-shaped tools
def doll_items(item_ids):
    keep = []
    for i in item_ids:
        if i.startswith(("trophy_doll_", "hidden_doll_")) or i in ("life_doll", "refuge_doll", "chance_doll", "cracked_doll", "nested_dolls"):
            keep.append(i)
    return keep


def _runs(im):
    """[(y0, y1, x0, x1)] runs of consecutive rows with the same opaque span, top to bottom."""
    rows = []
    for y in range(im.height):
        xs = [x for x in range(im.width) if im.getpixel((x, y))[3] > 0]
        rows.append((min(xs), max(xs) + 1) if xs else None)
    runs, y = [], 0
    while y < im.height:
        if rows[y] is None:
            y += 1
            continue
        y0, span = y, rows[y]
        while y < im.height and rows[y] == span:
            y += 1
        runs.append((y0, y, span[0], span[1]))
    return runs


def model(tex, im):
    """The turned doll's model for a sprite (16x16), its texture the sprite itself."""
    s = 16 / im.width
    els = []
    for y0, y1, x0, x1 in _runs(im):
        wdt = x1 - x0
        if wdt < 2:
            continue  # a one-pixel tuft (a ribbon end) has no body to turn
        cx = (x0 + x1) // 2
        z0, z1 = 8 - wdt * s / 2, 8 + wdt * s / 2
        front = [x0 * s, y0 * s, x1 * s, y1 * s]
        side = [x0 * s, y0 * s, (x0 + 1) * s, y1 * s]
        back = [cx * s, y0 * s, (cx + 1) * s, y1 * s]
        cap = [cx * s, y0 * s, (cx + 1) * s, (y0 + 1) * s]
        base = [cx * s, (y1 - 1) * s, (cx + 1) * s, y1 * s]
        els.append({
            "from": [x0 * s, 16 - y1 * s, z0], "to": [x1 * s, 16 - y0 * s, z1],
            "faces": {"south": {"uv": front, "texture": "#doll"}, "north": {"uv": back, "texture": "#doll"},
                      "east": {"uv": side, "texture": "#doll"}, "west": {"uv": side, "texture": "#doll"},
                      "up": {"uv": cap, "texture": "#doll"}, "down": {"uv": base, "texture": "#doll"}}})
    return {
        "textures": {"doll": tex, "particle": tex},
        "elements": els,
        "display": {
            "thirdperson_righthand": {"rotation": [0, 0, 0], "translation": [0, 2.5, 2], "scale": [0.5, 0.5, 0.5]},
            "thirdperson_lefthand": {"rotation": [0, 0, 0], "translation": [0, 2.5, 2], "scale": [0.5, 0.5, 0.5]},
            "firstperson_righthand": {"rotation": [0, -25, 0], "translation": [1.5, 3, 0], "scale": [0.55, 0.55, 0.55]},
            "firstperson_lefthand": {"rotation": [0, 25, 0], "translation": [1.5, 3, 0], "scale": [0.55, 0.55, 0.55]},
            "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
            "head": {"translation": [0, 13, 0], "scale": [0.8, 0.8, 0.8]},
            "fixed": {"rotation": [0, 0, 0], "scale": [0.9, 0.9, 0.9]},
        },
    }


def gen(assets, ns, item_ids, w):
    """Writes models/item/<id>_3d.json and items/<id>.json for every doll item. Returns how many."""
    n = 0
    for i in doll_items(item_ids):
        png = os.path.join(assets, f"textures/item/{i}.png")
        if not os.path.exists(png):
            continue
        im = Image.open(png).convert("RGBA")
        w(os.path.join(assets, f"models/item/{i}_3d.json"), model(f"{ns}:item/{i}", im))
        w(os.path.join(assets, f"items/{i}.json"), {"model": {
            "type": "minecraft:select", "property": "minecraft:display_context",
            "cases": [{"when": ["gui"], "model": {"type": "minecraft:model", "model": f"{ns}:item/{i}"}}],
            "fallback": {"type": "minecraft:model", "model": f"{ns}:item/{i}_3d"}}})
        n += 1
    return n
