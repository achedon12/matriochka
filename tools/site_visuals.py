"""Pictures the site needs for its recipe cards that the mod does not ship:

- icons of the vanilla ingredients, taken from the local Minecraft client jar (items flat, blocks as a small
  three-quarter cube); without the jar (CI) the icons already in site/public/vanilla are kept;
- three-quarter renders of the thirteen sculpted stations, drawn from their block models (tools/model_preview.py).
"""
import glob
import io
import os
import zipfile

from PIL import Image

import model_preview

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JAR_GLOB = os.path.expanduser("~/.gradle/caches/fabric-loom/*/minecraft-client*.jar")

# blocks drawn as a cube: id -> (top texture, side texture); any other id is drawn flat from its item texture
CUBES = {
    "anvil": ("anvil_top", "anvil"), "blast_furnace": ("blast_furnace_top", "blast_furnace_front"),
    "cauldron": ("cauldron_top", "cauldron_side"), "crying_obsidian": ("crying_obsidian", "crying_obsidian"),
    "dirt": ("dirt", "dirt"), "glass": ("glass", "glass"), "ice": ("ice", "ice"), "loom": ("loom_top", "loom_front"),
    "oak_log": ("oak_log_top", "oak_log"), "oak_planks": ("oak_planks", "oak_planks"), "observer": ("observer_top", "observer_front"),
    "obsidian": ("obsidian", "obsidian"), "piston": ("piston_top", "piston_side"), "smithing_table": ("smithing_table_top", "smithing_table_front"),
    "white_wool": ("white_wool", "white_wool"),
}
# flat icons that live under another name
FLAT = {"clock": "item/clock_00", "glass_pane": "block/glass_pane_top", "brown_mushroom": "block/brown_mushroom",
        "lightning_rod": "block/lightning_rod"}


def _jar():
    jars = sorted(glob.glob(JAR_GLOB), key=os.path.getmtime)
    return jars[-1] if jars else None


def _read(z, path):
    try:
        im = Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/{path}.png"))).convert("RGBA")
    except KeyError:
        return None
    # animated strips: the first frame
    return im.crop((0, 0, im.width, im.width)) if im.height > im.width else im


def _cube(top, side, size=64):
    """A small three-quarter cube from a top and a side texture, the left face darker, like an inventory block."""
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    t = top.resize((16, 16), Image.NEAREST)
    s = side.resize((16, 16), Image.NEAREST)
    k = size / 32.0
    px = out.load()

    def blit(tex, mapping, shade):
        tp = tex.load()
        for v in range(16):
            for u in range(16):
                r, g, b, a = tp[u, v]
                if a < 16:
                    continue
                quad = [mapping(u + du, v + dv) for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1))]
                xs = [q[0] for q in quad]
                ys = [q[1] for q in quad]
                for y in range(int(min(ys) * k), int(max(ys) * k) + 1):
                    for x in range(int(min(xs) * k), int(max(xs) * k) + 1):
                        if 0 <= x < size and 0 <= y < size and _inside(x / k + 0.5 / k, y / k + 0.5 / k, quad):
                            px[x, y] = (int(r * shade), int(g * shade), int(b * shade), 255)

    blit(t, lambda u, v: (16 + (u - v) * 0.92, 2 + (u + v) * 0.46), 1.0)
    blit(s, lambda u, v: (16 - 14.7 + u * 0.92, 9.4 + u * 0.46 + v * 0.95 - 0.46 * 0), 0.62)  # left face
    blit(s, lambda u, v: (16 + u * 0.92, 16.76 - u * 0.46 + v * 0.95), 0.82)  # right face
    return out


def _inside(x, y, q):
    sign = None
    for i in range(4):
        x0, y0 = q[i]
        x1, y1 = q[(i + 1) % 4]
        c = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
        if abs(c) < 1e-9:
            continue
        s = c > 0
        if sign is None:
            sign = s
        elif s != sign:
            return False
    return True


def vanilla_icons(public, ids):
    """Writes vanilla/<id>.png for each vanilla id ("minecraft:x") it can find; returns the set of ids with an icon."""
    dst = os.path.join(public, "vanilla")
    os.makedirs(dst, exist_ok=True)
    jar = _jar()
    if jar:
        with zipfile.ZipFile(jar) as z:
            for full in sorted(ids):
                n = full.split(":", 1)[1]
                im = None
                if n in CUBES:
                    a, b = _read(z, "block/" + CUBES[n][0]), _read(z, "block/" + CUBES[n][1])
                    if a and b:
                        im = _cube(a, b)
                elif n == "chest":
                    ch = _read(z, "entity/chest/normal")
                    if ch:
                        k = ch.width // 64
                        im = _cube(ch.crop((14 * k, 0, 28 * k, 14 * k)), ch.crop((14 * k, 33 * k, 28 * k, 43 * k)))
                else:
                    im = _read(z, FLAT.get(n, "item/" + n)) or _read(z, "block/" + n)
                    if im:
                        im = im.resize((64, 64), Image.NEAREST)
                if im:
                    im.save(os.path.join(dst, n + ".png"), optimize=True)
    return {"minecraft:" + f[:-4] for f in os.listdir(dst) if f.endswith(".png")}


def station_renders(public, stations):
    """Writes stations/<id>.png: the sculpted station seen from the front-left, on a transparent ground."""
    import json
    dst = os.path.join(public, "stations")
    os.makedirs(dst, exist_ok=True)
    out = set()
    for sid in stations:
        path = os.path.join(model_preview.ROOT, "models/block", sid + ".json")
        if not os.path.exists(path):
            continue
        im = model_preview.render(json.load(open(path)), size=320, bg=None)
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
            side = max(im.width, im.height) + 16
            sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
            sq.resize((256, 256), Image.LANCZOS).save(os.path.join(dst, sid + ".png"), optimize=True)
            out.add(sid)
    return out


def block_icons(public, tex_dir, blocks, stations):
    """Writes cubes/<id>.png: each mod block as a three-quarter cube (its top and side textures); the stations take
    their sculpted render instead. Returns the ids written."""
    dst = os.path.join(public, "cubes")
    os.makedirs(dst, exist_ok=True)
    out = set()
    for bid in blocks:
        if bid in stations:
            continue
        side = os.path.join(tex_dir, bid + ".png")
        if not os.path.exists(side):
            continue
        top = next((os.path.join(tex_dir, bid + suf + ".png") for suf in ("_top", "_tilled") if os.path.exists(os.path.join(tex_dir, bid + suf + ".png"))), side)
        a = Image.open(top).convert("RGBA")
        b = Image.open(side).convert("RGBA")
        a = a.crop((0, 0, a.width, a.width))
        b = b.crop((0, 0, b.width, b.width))
        _cube(a, b).save(os.path.join(dst, bid + ".png"), optimize=True)
        out.add(bid)
    return out
