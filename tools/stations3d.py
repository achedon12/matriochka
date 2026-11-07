"""The 13 stations as sculpted block models: each one a small piece of furniture with its own silhouette, built from
vanilla model elements (boxes, a few turned by 22.5 or 45 degrees) and a shared set of painted materials.

Models face north (their front at z = 0); the blockstate turns them to face the player who placed them. The parts
that move (the matrix cube, the press ram, the loom shuttle...) are drawn by the station renderer on top of these.

Materials are painted with the hand-crafted sprite tools (craft.py) so they share the mod's palettes, at 16 px for
the mod and 32 px for the HD pack. Every face takes the pixels under it (vanilla-style UVs), so a small part never
stretches a texture.
"""
import math

import craft
from craft import Spr, GOLD, WOOD, IRON, RED, PAPER, hramp, pnoise, tile, style, STATION_WORLD

NS = "matriochka"

# ------------------------------------------------------------------ materials


def _noise_fill(s, ramp, seed, cells=4, lo=1, hi=3, streak=0.0):
    def f(x, y, i, j):
        g = pnoise(x * (1 + streak), y, cells, seed) * 0.65 + pnoise(x, y, cells * 2, seed + 7) * 0.35
        return ramp[lo + min(hi - lo, int(g * (hi - lo + 1)))]
    tile(s, f)


def m_gold(res):
    s = Spr(res)
    _noise_fill(s, GOLD, 41, lo=2, hi=4)
    for (x, y) in ((3.0, 4.0), (11.0, 2.5), (6.5, 11.0), (13.5, 12.5), (1.5, 14.0)):
        s.dot(x, y, GOLD[5])
    return s


def m_iron(res):
    s = Spr(res)
    _noise_fill(s, IRON, 43, cells=2, lo=1, hi=3, streak=3.0)
    for y in (0.5, 8.5):
        s.fill(s.rect(0, y - 0.5, 16, y), IRON[0])
    for (x, y) in ((2.0, 2.0), (14.0, 2.0), (2.0, 10.0), (14.0, 10.0)):
        s.dot(x, y, IRON[4])
    return s


def m_copper(res):
    s = Spr(res)
    ramp = hramp("b8693a")
    _noise_fill(s, ramp, 47, cells=4, lo=1, hi=4, streak=2.0)
    for (x, y) in ((4.0, 6.0), (12.0, 3.0), (9.0, 13.0)):
        s.dot(x, y, hramp("4aa88a")[3])
    return s


def m_wood(res):
    s = Spr(res)
    craft._wood(s, 51)
    return s


def m_dark_wood(res):
    s = Spr(res)
    craft._wood(s, 53, ramp=[(22, 12, 8), (40, 22, 14), (60, 34, 20), (82, 48, 28), (110, 66, 38), (140, 90, 52)])
    return s


def m_lacquer(res, w):
    s = Spr(res)
    body = style(w)["body"]
    _noise_fill(s, body, 61 + w, cells=4, lo=1, hi=3)
    s.fill(s.rect(0, 14.6, 16, 15.2), GOLD[3])
    for x in range(1, 16, 4):
        s.dot(x + 0.5, 1.2, style(w)["second"][3])
    return s


def m_stone(res, w):
    s = Spr(res)
    m = style(w)["metal"]
    ramp = [craft.mix(c, (60, 56, 64), 0.45) for c in m]

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 71 + w) * 0.7 + pnoise(x, y, 8, 72 + w) * 0.3
        t = 1 if g < 0.38 else 2 if g < 0.7 else 3
        if (y % 8) < 0.6 or ((x + (8 if (y // 8) % 2 else 0)) % 16) < 0.6:
            t = 0
        return ramp[t]
    tile(s, f)
    return s


def m_glow(res, w, base=None):
    s = Spr(res)
    ramp = hramp(base, dl=0.09) if base else style(w)["glow"]

    def f(x, y, i, j):
        g = pnoise(x + 3 * math.sin(y / 3.0), y, 4, 81 + w)
        return ramp[2 + min(3, int(g * 4))]
    tile(s, f)
    s.glow = set(s.px)
    return s


def m_obsidian(res):
    s = Spr(res)
    ramp = [(8, 6, 14), (18, 12, 30), (30, 20, 50), (52, 34, 84), (96, 70, 150)]

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 91) * 0.6 + pnoise(x, y, 8, 92) * 0.4
        return ramp[0 if g < 0.3 else 1 if g < 0.62 else 2 if g < 0.9 else 3]
    tile(s, f)
    for (x, y) in ((3.0, 5.0), (12.0, 9.0), (7.0, 13.0)):
        s.dot(x, y, ramp[4])
    return s


def m_glass(res, w):
    s = Spr(res)
    g = style(w)["glow"]
    ramp = [craft.mix(c, (210, 230, 240), 0.55) for c in g]
    _noise_fill(s, ramp, 95 + w, cells=2, lo=1, hi=2)
    s.line([(3.0, 2.0), (1.5, 6.0)], ramp[5], r=0.4)
    s.line([(13.0, 9.0), (11.5, 14.0)], ramp[4], r=0.3)
    s.glow = set(s.px)
    return s


def m_threads(res):
    """Warp threads of the ten worlds, side by side."""
    s = Spr(res)
    for i in range(16):
        w = 1 + (i * 10 // 16)
        ramp = style(w)["body"]
        col = s.rect(i, 0, i + 1, 16)
        s.fill(col, lambda p, r=ramp: r[3] if (p[1] // max(1, s.res // 16)) % 3 else r[2])
    return s


def m_cloth(res):
    s = Spr(res)

    def f(x, y, i, j):
        w = 1 + int(x) * 10 // 16
        r = style(w)["body"]
        return r[3] if (int(x * 2) + int(y * 2)) % 2 else r[2]
    tile(s, f)
    s.fill(s.rect(0, 7.4, 16, 8.4), GOLD[3])
    return s


def m_clock(res):
    s = Spr(res)
    s.fill(s.rect(0, 0, 16, 16), PAPER[3])
    s.fill(s.ring(8, 8, 6.6, 7.6), GOLD[3])
    for k in range(12):
        a = k * math.pi / 6
        r0 = 5.2 if k % 3 else 4.6
        s.line([(8 + math.sin(a) * r0, 8 - math.cos(a) * r0), (8 + math.sin(a) * 6.2, 8 - math.cos(a) * 6.2)], craft.INK, r=0.35)
    # the dawn and dusk windows the workshop works in, lit
    for a0 in (-0.35, math.pi - 0.35):
        for t in range(8):
            a = a0 + t * 0.1
            s.dot(8 + math.sin(a + math.pi / 2) * 3.4, 8 - math.cos(a + math.pi / 2) * 3.4, hramp("f0a040")[4], glow=True)
    s.fill(s.disc(8, 8, 0.9), GOLD[2])
    return s


def m_paper(res):
    s = Spr(res)
    _noise_fill(s, PAPER, 101, cells=2, lo=3, hi=4)
    for y in (3.0, 5.0, 7.0, 9.0, 11.0, 13.0):
        s.fill(s.rect(2.0, y, 14.0, y + 0.4), PAPER[1])
    return s


def m_crystal(res, base):
    s = Spr(res)
    ramp = hramp(base, dl=0.1)

    def f(x, y, i, j):
        g = pnoise(x, y, 2, 111) * 0.6 + (x + y) / 32 * 0.4
        return ramp[1 + min(4, int(g * 5))]
    tile(s, f)
    s.line([(3.0, 2.0), (2.0, 7.0)], ramp[5], r=0.4)
    s.glow = set(s.px)
    return s


def m_soul(res):
    return m_glow(res, 0, "bfe8ff")


def m_lava(res):
    return m_glow(res, 2, "ff8a24")


def m_runes(res, w):
    """Stone with glowing world glyph lines."""
    s = m_stone(res, w)
    g = style(w)["glow"]
    for (x0, y0, x1, y1) in ((3, 3, 3, 8), (3, 8, 6, 11), (10, 2, 13, 5), (13, 5, 13, 10), (6, 13, 11, 13), (8, 5, 8, 9)):
        s.line([(x0 + 0.5, y0 + 0.5), (x1 + 0.5, y1 + 0.5)], g[4], r=0.4, glow=True)
    return s


def materials(res=16):
    """{texture name under block/station/: sprite}."""
    out = {"gold": m_gold(res), "iron": m_iron(res), "copper": m_copper(res), "wood": m_wood(res), "dark_wood": m_dark_wood(res),
           "obsidian": m_obsidian(res), "threads": m_threads(res), "cloth": m_cloth(res), "clock": m_clock(res),
           "soul": m_soul(res), "lava": m_lava(res), "paper": m_paper(res),
           "crystal_violet": m_crystal(res, "b44ccc"), "crystal_teal": m_crystal(res, "2ab8b0")}
    for w in sorted(set(STATION_WORLD.values())):
        out[f"lacquer_{w}"] = m_lacquer(res, w)
        out[f"stone_{w}"] = m_stone(res, w)
        out[f"glow_{w}"] = m_glow(res, w)
        out[f"glass_{w}"] = m_glass(res, w)
        out[f"runes_{w}"] = m_runes(res, w)
    return out


# ------------------------------------------------------------------ model building

class M:
    """Collects the elements of one station model."""

    def __init__(self, sid):
        self.sid, self.w = sid, STATION_WORLD[sid]
        self.el = []
        self.tex = {"particle": f"{NS}:block/{sid}"}

    def t(self, name):
        """A texture key: block/<sid>, block/<sid>_top, or a shared station material."""
        if name in ("front", "top"):
            path = f"{NS}:block/{self.sid}" + ("_top" if name == "top" else "")
        else:
            name = name.replace("{w}", str(self.w))
            path = f"{NS}:block/station/{name}"
        key = name.replace("/", "_")
        self.tex[key] = path
        return "#" + key

    def box(self, frm, to, tex, faces=None, rot=None, glow=False, full=(), skip=()):
        """A box from `frm` to `to` in 16 units. `tex` is a material or {face: material}; `full` lists faces that show
        the whole texture (the station's painted front plaque); `skip` faces are left out (hidden ones)."""
        x0, y0, z0 = frm
        x1, y1, z1 = to
        fs = {}
        for f in faces or ("north", "south", "east", "west", "up", "down"):
            if f in skip:
                continue
            mat = tex.get(f, tex.get("*")) if isinstance(tex, dict) else tex
            if mat is None:
                continue
            if f in ("north", "south"):
                uv = [x0, 16 - y1, x1, 16 - y0]
            elif f in ("east", "west"):
                uv = [z0, 16 - y1, z1, 16 - y0]
            else:
                uv = [x0, z0, x1, z1]
            uv = [max(0.0, min(16.0, v)) for v in uv]
            if uv[0] == uv[2]:
                uv[2] = min(16.0, uv[0] + 0.5)
            if uv[1] == uv[3]:
                uv[3] = min(16.0, uv[1] + 0.5)
            if f in full:
                uv = [0, 0, 16, 16]
            face = {"uv": uv, "texture": self.t(mat)}
            if (f == "down" and y0 <= 0) or (f == "up" and y1 >= 16) or (f == "north" and z0 <= 0 and not rot) or \
                    (f == "south" and z1 >= 16 and not rot) or (f == "west" and x0 <= 0 and not rot) or (f == "east" and x1 >= 16 and not rot):
                face["cullface"] = f
            fs[f] = face
        e = {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to], "faces": fs}
        if rot:
            axis, angle, origin = rot
            e["rotation"] = {"angle": angle, "axis": axis, "origin": list(origin)}
        if glow:
            e["light_emission"] = 15
        self.el.append(e)
        return e

    def json(self):
        return {"parent": "minecraft:block/block", "ambientocclusion": True, "textures": self.tex, "elements": self.el,
                "display": DISPLAY}


DISPLAY = {
    "gui": {"rotation": [30, 225, 0], "translation": [0, 0, 0], "scale": [0.625, 0.625, 0.625]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.25, 0.25, 0.25]},
    "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]},
    "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]},
    "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
    "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
}


def legs(m, x0, x1, z0, z1, h, s, mat):
    for (x, z) in ((x0, z0), (x1 - s, z0), (x0, z1 - s), (x1 - s, z1 - s)):
        m.box([x, 0, z], [x + s, h, z + s], mat, skip=("up",))


def rim(m, x0, y, z0, x1, z1, t, mat):
    """A thin moulding round a top surface."""
    m.box([x0, y, z0], [x1, y + t, z0 + 0.5], mat)
    m.box([x0, y, z1 - 0.5], [x1, y + t, z1], mat)
    m.box([x0, y, z0 + 0.5], [x0 + 0.5, y + t, z1 - 0.5], mat)
    m.box([x1 - 0.5, y, z0 + 0.5], [x1, y + t, z1 - 0.5], mat)


# ---- the thirteen stations

def matrix_workbench(m):
    # a lacquered joiner's bench with a gilded inlay top, a drawer front and a low shelf; the matrix floats above
    legs(m, 1, 15, 1, 15, 9, 2.5, "lacquer_{w}")
    m.box([0, 9, 0], [16, 12, 16], {"*": "wood", "up": "top", "north": "front"}, full=("north", "up"))
    rim(m, 0, 12, 0, 16, 16, 0.75, "gold")
    m.box([2, 3, 2], [14, 4, 14], "dark_wood")
    m.box([3.5, 4, 3.5], [7, 6.5, 7], "lacquer_{w}")
    m.box([9, 4, 9], [12.5, 5.5, 12.5], "gold")
    # the matrix dais the floating cube spins over
    m.box([5.5, 12.75, 5.5], [10.5, 13.5, 10.5], "gold")
    m.box([6.5, 13.5, 6.5], [9.5, 14, 9.5], "glow_{w}", glow=True)


def class_table(m):
    # a slanted lectern on a carved pillar, the class ladder of three medals up its spine
    m.box([2, 0, 2], [14, 2, 14], "dark_wood")
    m.box([3, 2, 3], [13, 3, 13], "gold")
    m.box([5.5, 3, 5.5], [10.5, 11, 10.5], "lacquer_{w}")
    for i, y in enumerate((4.5, 6.5, 8.5)):
        m.box([7, y, 5], [9, y + 1.5, 5.5], "gold" if i < 2 else "glow_{w}", glow=i == 2)
    m.box([1, 11, 1], [15, 13, 15], {"*": "wood", "up": "top"}, full=("up",), rot=("x", -22.5, (8, 12, 8)))
    m.box([1, 10.5, 0.5], [15, 11.5, 2], "gold", rot=("x", -22.5, (8, 12, 8)))
    # a book open on the desk
    m.box([3.2, 13, 3.5], [12.8, 13.3, 11.5], "lacquer_{w}", rot=("x", -22.5, (8, 12, 8)))
    m.box([3.5, 13.3, 4], [7.8, 13.8, 11], "paper", rot=("x", -22.5, (8, 12, 8)))
    m.box([8.2, 13.3, 4], [12.5, 13.8, 11], "paper", rot=("x", -22.5, (8, 12, 8)))
    m.box([7.8, 13.3, 3.5], [8.2, 13.9, 11.5], "gold", rot=("x", -22.5, (8, 12, 8)))


def soul_altar(m):
    # three stone steps, a gold-lipped bowl of soul fire and four candle posts
    m.box([0, 0, 0], [16, 3, 16], "stone_{w}")
    m.box([2, 3, 2], [14, 6, 14], {"*": "stone_{w}", "north": "front"}, full=("north",))
    m.box([3.5, 6, 3.5], [12.5, 9, 12.5], "stone_{w}")
    m.box([3, 9, 3], [13, 11, 13], "gold")
    m.box([4, 10.6, 4], [12, 11.2, 12], "soul", glow=True)
    m.box([5.5, 11.2, 5.5], [10.5, 13, 10.5], "soul", glow=True, rot=("y", 45, (8, 8, 8)))
    for (x, z) in ((0.5, 0.5), (13.5, 0.5), (0.5, 13.5), (13.5, 13.5)):
        m.box([x, 3, z], [x + 2, 8, z + 2], "gold")
        m.box([x + 0.5, 8, z + 0.5], [x + 1.5, 9, z + 1.5], "glow_{w}", glow=True)


def spore_vat(m):
    # an iron-hooped octagonal vat brimming with glowing brew, a tap at the front, mushrooms on the lid
    for a in (0, 45):
        m.box([2.5, 0, 2.5], [13.5, 12, 13.5], "dark_wood", rot=("y", a, (8, 8, 8)) if a else None)
    for y in (1.5, 6, 10.5):
        for a in (0, 45):
            m.box([2.2, y, 2.2], [13.8, y + 1, 13.8], "iron", rot=("y", a, (8, 8, 8)) if a else None, skip=("up", "down"))
    m.box([3.5, 11.5, 3.5], [12.5, 12.5, 12.5], "glow_{w}", glow=True)
    m.box([3.5, 11.5, 3.5], [12.5, 12.5, 12.5], "glow_{w}", glow=True, rot=("y", 45, (8, 8, 8)))
    m.box([7, 3, 0.5], [9, 5, 2.5], "copper")
    m.box([7.5, 2, 0], [8.5, 3, 1], "copper")
    for (x, z, h) in ((4, 9, 2), (10, 5, 1.5)):
        m.box([x + 0.6, 12.5, z + 0.6], [x + 1.4, 12.5 + h, z + 1.4], "wood")
        m.box([x, 12.5 + h, z], [x + 2, 13.5 + h, z + 2], "lacquer_1")


def ash_foundry(m):
    # a squat stone furnace with a glowing mouth, a crucible on top and a chimney at the back
    m.box([0, 0, 0], [16, 2, 16], "iron")
    m.box([1, 2, 1], [15, 11, 15], {"*": "stone_{w}", "north": "front"}, full=("north",))
    m.box([4, 3, 0.5], [12, 8, 1], "lava", glow=True)
    m.box([0.5, 11, 0.5], [15.5, 12, 15.5], "iron")
    m.box([3, 12, 2], [11, 15, 10], "iron")
    m.box([3.5, 14.5, 2.5], [10.5, 15.2, 9.5], "lava", glow=True)
    m.box([10.5, 13, 5], [13.5, 14, 7], "iron")
    m.box([11.5, 12, 11], [15, 16, 14.5], "stone_{w}")
    m.box([12, 15.4, 11.5], [14.5, 16, 14], "lava", glow=True)


def jailer_table(m):
    # a heavy iron-banded desk with a padlock on the apron and chains hanging from its corners
    legs(m, 0.5, 15.5, 0.5, 15.5, 8, 3, "iron")
    m.box([0, 8, 0], [16, 12, 16], {"*": "dark_wood", "north": "front"}, full=("north",))
    for z in (3, 12):
        m.box([-0.01, 8.5, z], [16.01, 11.5, z + 1], "iron", skip=("up", "down"))
    m.box([5.5, 12, 5.5], [10.5, 13, 10.5], "iron")
    # the lock plate on the desk, the key turning in it
    m.box([6.5, 13, 6.5], [9.5, 15, 9.5], "gold")
    m.box([7.5, 15, 7.5], [8.5, 16, 8.5], "glow_{w}", glow=True)
    # the great padlock hanging on the apron: iron shackle, gold body, lit keyhole
    m.box([6, 9.5, -1.5], [10, 11, -0.5], "iron")
    m.box([6, 11, -1.5], [7, 13, -0.5], "iron")
    m.box([9, 11, -1.5], [10, 13, -0.5], "iron")
    m.box([5, 6, -2], [11, 9.5, 0], "gold")
    m.box([7.5, 7, -2.1], [8.5, 8.5, -2], "glow_{w}", glow=True, faces=("north",))
    for x in (1.2, 13.8):
        for y in (2, 4.5):
            m.box([x, y, 1], [x + 1, y + 2, 1.6], "iron", rot=("z", 22.5 if x < 8 else -22.5, (x + 0.5, y + 1, 1.3)))


def lightning_forge(m):
    # an anvil on a stone plinth between two copper coils whose tips hold the storm
    m.box([1, 0, 1], [15, 5, 15], {"*": "stone_{w}", "north": "front"}, full=("north",))
    m.box([4, 5, 5], [12, 7, 11], "iron")
    m.box([5.5, 7, 6], [10.5, 9, 10], "iron")
    m.box([2.5, 9, 5], [13.5, 11.5, 11], "iron")
    m.box([0.5, 9.5, 6.5], [2.5, 11, 9.5], "iron")
    for x in (0.5, 13):
        m.box([x, 5, 12.5], [x + 2.5, 6, 15], "iron")
        for k, y in enumerate(range(6, 14, 2)):
            m.box([x + 0.5, y, 13], [x + 2, y + 1.4, 14.5], "copper")
            m.box([x + 0.25, y + 1.4, 12.75], [x + 2.25, y + 2, 14.75], "gold")
        m.box([x + 0.5, 14, 13], [x + 2, 15.5, 14.5], "glow_{w}", glow=True)


def dark_altar(m):
    # an obsidian slab altar flanked by two obelisks, a dark crystal hanging over it
    m.box([0, 0, 2], [16, 2, 14], "obsidian")
    m.box([2, 2, 3], [14, 8, 13], {"*": "obsidian", "north": "front"}, full=("north",))
    m.box([1, 8, 2], [15, 9.5, 14], "obsidian")
    for x in (0.5, 12.5):
        m.box([x, 2, 13.5], [x + 3, 13, 16], "obsidian")
        m.box([x + 0.5, 13, 14], [x + 2.5, 15.5, 15.5], "obsidian", rot=("y", 45, (x + 1.5, 14, 14.75)))
        m.box([x + 1, 10, 13.4], [x + 2, 11, 13.6], "glow_{w}", glow=True)
    m.box([6, 9.5, 6], [10, 10, 10], "glow_{w}", glow=True)


def inverter(m):
    # an hourglass of two mirrored pyramids in a gilded ring, their lit cores trading places
    m.box([1, 0, 1], [15, 2, 15], "lacquer_{w}")
    m.box([2, 14, 2], [14, 16, 14], "lacquer_{w}")
    for (x, z) in ((1.5, 1.5), (13, 1.5), (1.5, 13), (13, 13)):
        m.box([x, 2, z], [x + 1.5, 14, z + 1.5], "gold")
    for k, (y0, y1, s) in enumerate(((2, 4, 5), (4, 6, 3.5), (6, 7.5, 2), (8.5, 10, 2), (10, 12, 3.5), (12, 14, 5))):
        m.box([8 - s, y0, 8 - s], [8 + s, y1, 8 + s], "crystal_violet" if k < 3 else "crystal_teal", glow=True, rot=("y", 45, (8, 8, 8)) if k % 2 else None)
    m.box([7.25, 7.5, 7.25], [8.75, 8.5, 8.75], "gold")
    m.box([2.5, 2.5, 0.9], [13.5, 4, 1.5], "front", full=("north",), faces=("north",))


def abyssal_press(m):
    # a riveted hydraulic press: bed, two columns, a crossbeam; the ram moves between them
    m.box([0, 0, 0], [16, 3, 16], {"*": "iron", "north": "front"}, full=("north",))
    m.box([3, 3, 3], [13, 4, 13], "stone_{w}")
    for x in (0.5, 12.5):
        m.box([x, 3, 5], [x + 3, 16, 11], "iron")
    m.box([0, 13, 4], [16, 16, 12], "copper")
    # the pressure gauge on the right column
    m.box([15.5, 8, 6.5], [16.25, 11, 9.5], "gold")
    m.box([16.25, 8.5, 7], [16.5, 10.5, 9], "glow_{w}", glow=True)
    for y in (5, 9):
        m.box([0.2, y, 4.8], [3.8, y + 0.6, 11.2], "copper", skip=("up", "down"))


def time_workshop(m):
    # a clockmaker's cabinet: a clock face crowned with gold, gears on its flank, the pendulum swings below
    m.box([1, 0, 3], [15, 2, 13], "dark_wood")
    m.box([2, 2, 4], [14, 15, 12], {"*": "lacquer_{w}", "north": "dark_wood"})
    m.box([3, 7.5, 3.5], [13, 14.5, 4], "clock", full=("north",), glow=True)
    rim(m, 2.5, 14.5, 3.5, 13.5, 12.5, 0.5, "gold")
    m.box([4, 15, 5], [12, 16, 11], "gold")
    m.box([7, 15.5, 7], [9, 16, 9], "glow_{w}", glow=True)
    m.box([3.5, 2.5, 3.6], [12.5, 7, 4], "glass_{w}")
    for (y, z, r) in ((11, 6.5, 2.5), (6, 9, 2.0)):
        for a in (0, 45):
            m.box([14, y - r, z - r], [15, y + r, z + r], "gold", rot=("x", a, (14.5, y, z)) if a else None)


def terrain_anchor(m):
    # a stone pylon sunk in a heavy base, rune bands round it and four grounding stakes; a ring turns over it
    m.box([0, 0, 0], [16, 3, 16], "iron")
    m.box([1, 2.99, 1], [15, 3.4, 15], "lava", glow=True, faces=("up",))
    m.box([2, 3, 2], [14, 3.5, 14], "stone_{w}")
    for (x, z) in ((0, 0), (13, 0), (0, 13), (13, 13)):
        m.box([x + 0.5, 3, z + 0.5], [x + 2.5, 7, z + 2.5], "iron")
        m.box([x + 1, 7, z + 1], [x + 2, 8, z + 2], "lava", glow=True)
    m.box([3, 3, 3], [13, 6, 13], {"*": "stone_{w}", "north": "front"}, full=("north",))
    m.box([5, 6, 5], [11, 12, 11], "runes_{w}", glow=True)
    m.box([4.5, 8, 4.5], [11.5, 9, 11.5], "gold")
    m.box([4.5, 10.5, 4.5], [11.5, 11, 11.5], "gold")
    m.box([6, 12, 6], [10, 15, 10], "runes_{w}", glow=True, rot=("y", 45, (8, 8, 8)))
    m.box([7, 15, 7], [9, 16, 9], "glow_{w}", glow=True)


def final_loom(m):
    # a floor loom: two uprights, warp threads of every world, the woven cloth rolled at the front
    for x in (0.5, 13.5):
        m.box([x, 0, 2], [x + 2, 16, 4], "wood")
        m.box([x, 0, 12], [x + 2, 10, 14], "wood")
        m.box([x, 1, 4], [x + 2, 2.5, 12], "wood")
        m.box([x, 8, 4], [x + 2, 9.5, 12], "wood")
    m.box([2.5, 14, 2.5], [13.5, 15.5, 3.5], "gold")
    m.box([2.5, 4, 1.5], [13.5, 6, 3.5], "cloth")
    m.box([2.5, 6, 2.6], [13.5, 14, 3.0], "threads", faces=("north", "south"))
    m.box([2.5, 9, 3], [13.5, 9.5, 12.5], "threads", faces=("up", "down"))
    m.box([2.5, 9.5, 12.5], [13.5, 10, 13.5], "lacquer_10")
    # the heddle frame and the front plaque
    m.box([2.5, 10.5, 6.5], [13.5, 11.5, 7.5], "gold")
    m.box([4, 0.5, 4], [12, 1, 12], "front", faces=("up",), full=("up",))


BUILD = {"matrix_workbench": matrix_workbench, "class_table": class_table, "soul_altar": soul_altar, "spore_vat": spore_vat,
         "ash_foundry": ash_foundry, "jailer_table": jailer_table, "lightning_forge": lightning_forge, "dark_altar": dark_altar,
         "inverter": inverter, "abyssal_press": abyssal_press, "time_workshop": time_workshop, "terrain_anchor": terrain_anchor,
         "final_loom": final_loom}


def model(sid):
    m = M(sid)
    BUILD[sid](m)
    return m.json()


def blockstate(sid):
    return {"variants": {f"facing={f}": ({"model": f"{NS}:block/{sid}", "y": y} if y else {"model": f"{NS}:block/{sid}"})
                         for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}}


def bounds(sid):
    """Outer bounds of a station model in 16 units, (x0, y0, z0, x1, y1, z1), ignoring rotations."""
    el = model(sid)["elements"]
    lo = [min(e["from"][i] for e in el) for i in range(3)]
    hi = [max(e["to"][i] for e in el) for i in range(3)]
    return [max(0, round(v)) for v in lo] + [min(16, round(v)) for v in hi]
