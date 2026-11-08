"""The ten world ores, the Matriochkite Ingot, the Nesting Cradle and the Matriarch Armour, painted with the
hand-crafted sprite tools (craft.py) so they share the mod's palettes and its manner: hard tones lit from the top left,
dark outlines taken from the part they close, a few bright glints, a shape of its own for every material.

crafted_item / crafted_block are asked first by craft.py (so the HD pack gets them at 32 px too); gen() writes what
the generic generator does not: the cradle's sculpted model, the Time Sprout's stages, the golden doll shells the
cradle's ritual closes round the ores (item models shown by display entities), and the Journal lines of the ores.
"""
import math
import os

import craft
from craft import (Spr, GOLD, RED, WOOD, PAPER, SKIN, INK, CHEEK, hramp, mix, hx, n_sphere, n_flat, n_bevel, pnoise, tile,
                   style, _rows_mask, ARMOR_ROWS)

NS = "matriochka"

# the Matriarch's lacquer: a deeper, richer red than the Artisan's, and a brighter leaf of gold
LACQUER = [(40, 4, 10), (88, 10, 18), (138, 20, 26), (184, 34, 34), (220, 70, 56), (248, 138, 108)]
LEAF = [(70, 38, 8), (130, 84, 20), (190, 136, 40), (232, 182, 64), (252, 220, 120), (255, 246, 196)]
CREAM = [(150, 112, 80), (206, 172, 130), (236, 214, 176), (248, 236, 210), (255, 250, 236)]
FLOWER = [(120, 20, 40), (196, 40, 58), (236, 96, 96)]


# =================================================================== small shapes
def facet_crystal(s, cx, base, top, w, ramp, lean=0.0, down=False, glow=False):
    """A pointed crystal column: a lit left face, a shaded right face and a bright ridge between them. `down` points it
    down (base above, tip below)."""
    d = 1 if not down else -1
    tip_y = top
    shoulder = top + d * w * 1.25
    pts = [(cx - w, base), (cx - w + lean * 0.7, shoulder), (cx + lean, tip_y), (cx + w + lean * 0.7, shoulder), (cx + w, base)]
    m = s.poly(pts)
    def ridge_x(y):
        return cx + lean * ((y - base) / (tip_y - base))
    left = {p for p in m if (p[0] + 0.5) / s.k < ridge_x((p[1] + 0.5) / s.k)}
    right = m - left
    s.fill(left, ramp[4], rim=ramp[0], glow=glow)
    s.fill(right, ramp[2], rim=ramp[0], glow=glow)
    ridge = {p for p in m if abs((p[0] + 0.5) / s.k - ridge_x((p[1] + 0.5) / s.k)) < 0.5 / s.k + 0.26}
    s.fill(ridge, ramp[5], rim=ramp[0], glow=glow)
    # the tip facet catches the light
    tipm = {p for p in m if abs((p[1] + 0.5) / s.k - tip_y) < abs(shoulder - tip_y) * 0.7}
    s.fill({p for p in tipm if p in left}, ramp[5], rim=ramp[0], glow=glow)
    return m


def pebble(s, cx, cy, rx, ry, ramp, spec=0.05):
    m = s.ell(cx, cy, rx, ry)
    s.shade(m, ramp, n_sphere(cx - rx * 0.25, cy - ry * 0.3, rx * 1.1, ry * 1.1), spec=spec)
    return m


# =================================================================== the ten ores
def it_spore_crystal(res):
    """Three green crystals of spore growing out of a violet bloom, the bloom's spots glowing."""
    s = Spr(res)
    green = hramp("5ab83a", dl=0.11)
    violet = hramp("7c4a9c")
    lime = hramp("d8ff6a", dl=0.07)
    facet_crystal(s, 4.6, 12.0, 5.0, 1.6, green, lean=-1.4)
    facet_crystal(s, 11.6, 12.0, 6.0, 1.5, green, lean=1.4)
    s.outline()
    facet_crystal(s, 8.1, 12.4, 1.4, 2.3, hramp("b0e83a", dl=0.1))
    cap = s.ell(8, 13.3, 5.8, 2.3)
    s.shade(cap, violet, n_sphere(7.0, 12.2, 6.0, 3.0), spec=0.05)
    for (x, y) in ((3.6, 12.8), (6.6, 12.2), (10.2, 12.6), (12.4, 13.4), (8.4, 14.0)):
        s.dot(x, y, lime[4])
    s.outline()
    for (x, y) in ((2.0, 3.0), (13.6, 2.4)):
        s.dot(x, y, lime[5])
    return s


def it_living_ember(res):
    """A lump of coal that still burns: a black crust split by fissures of fire, flames licking its top."""
    s = Spr(res)
    crust = [(18, 10, 10), (34, 20, 18), (54, 32, 26), (78, 48, 36), (104, 66, 46), (130, 90, 62)]
    fire = hramp("ff8a1a", dl=0.08)
    yellow = hramp("ffd84a", dl=0.06)
    body = s.poly([(3.0, 10.0), (4.6, 6.6), (7.6, 5.4), (11.2, 6.2), (13.4, 9.0), (12.8, 12.8), (9.4, 14.6), (5.0, 14.0)])
    s.shade(body, crust, n_bevel(s, body, 2.4, flat=0.3), lo=1, hi=4)
    for path in ([(4.4, 9.6), (6.6, 10.4), (8.0, 9.0), (10.4, 10.6), (12.4, 10.0)],
                 [(8.0, 9.0), (7.6, 12.0), (9.2, 13.6)],
                 [(6.0, 7.0), (7.2, 8.2)], [(10.4, 10.6), (11.6, 12.4)]):
        s.line(path, fire[3], r=0.42)
    for (x, y) in ((6.4, 10.0), (8.0, 9.0), (10.4, 10.4), (7.6, 12.0)):
        s.dot(x, y, yellow[4])
    # flames
    for (x0, h, w) in ((5.6, 3.6, 1.3), (8.4, 5.4, 1.6), (11.0, 3.2, 1.2)):
        f = s.poly([(x0 - w, 7.2), (x0 - w * 0.4, 7.2 - h * 0.55), (x0 + 0.2, 7.2 - h), (x0 + w * 0.6, 7.2 - h * 0.45), (x0 + w, 7.2)])
        s.fill(f, fire[3], rim=fire[1])
        s.fill(s.poly([(x0 - w * 0.45, 7.2), (x0, 7.2 - h * 0.62), (x0 + w * 0.45, 7.2)]), yellow[4])
    s.outline()
    for (x, y) in ((2.4, 4.0), (13.8, 3.0), (10.6, 0.8)):
        s.dot(x, y, yellow[5])
    return s


def it_golden_ward(res):
    """A lock's golden bolt, cut with the teeth of a ward: a heavy bar with a ring knob and a keyhole of cold light."""
    s = Spr(res)
    gold = GOLD
    blue = hramp("7fd3ff", dl=0.08)
    a = -math.pi / 4

    def rot(x, y):
        cx, cy = 8.0, 8.0
        dx, dy = x - cx, y - cy
        return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)
    bar = s.poly([rot(x, y) for x, y in ((1.6, 6.6), (13.0, 6.6), (14.4, 8.0), (13.0, 9.4), (1.6, 9.4))])
    s.shade(bar, gold, n_flat(0.0, -0.5), lo=2, hi=4)
    teeth = set()
    for x0 in (3.0, 6.0, 9.4):
        teeth |= s.poly([rot(x, y) for x, y in ((x0, 9.2), (x0 + 1.6, 9.2), (x0 + 1.6, 11.6), (x0, 11.6))])
    s.shade(teeth, gold, n_flat(0.2, 0.4), lo=1, hi=3)
    rx, ry = rot(1.8, 8.0)
    ring = s.ring(rx, ry, 1.5, 2.9)
    s.shade(ring, gold, n_sphere(rx - 0.8, ry - 0.8, 3.4), lo=1, hi=5)
    hole = s.disc(*rot(10.6, 8.0), 1.0)
    s.fill(hole, blue[4])
    s.dot(*rot(10.0, 7.2), blue[5])
    for x0 in (3.6, 7.4):
        s.dot(*rot(x0, 7.2), gold[5])
    s.outline()
    return s


def it_fulgurite(res):
    """Fused glass branching like the bolt that made it: pale tubes with a core of caught lightning."""
    s = Spr(res)
    glass = hramp("c4d6ee", dl=0.09)
    core = hramp("ffe14a", dl=0.06)
    trunk = [(4.0, 14.6), (5.4, 11.2), (7.2, 9.4), (8.2, 6.4), (10.6, 4.0), (12.6, 1.6)]
    forks = [[(7.2, 9.4), (10.0, 9.6), (12.8, 7.8)], [(8.2, 6.4), (6.8, 3.6), (5.4, 1.8)], [(5.4, 11.2), (2.6, 9.6)]]
    m = s.path(trunk, 1.35)
    for f in forks:
        m |= s.path(f, 0.95)
    s.shade(m, glass, n_bevel(s, m, 1.2, flat=0.4), lo=1, hi=4, spec=0.05)
    s.line(trunk, core[3], r=0.36)
    for f in forks:
        s.line(f, core[2], r=0.28)
    for (x, y) in ((8.2, 6.4), (5.4, 11.2), (10.6, 4.0)):
        s.dot(x - 0.5, y - 0.5, core[5])
    s.outline()
    for (x, y) in ((13.6, 4.8), (2.0, 6.0), (11.4, 12.0)):
        s.dot(x, y, hramp("8ad8ff")[4])
    return s


def it_silent_stone(res):
    """A smooth river pebble from the dark, ringed with pale bands like the circles a sound leaves, quite still."""
    s = Spr(res)
    ink = hramp("2c3462", dl=0.08, bottom=0.04)
    pale = hramp("c8ccf0", dl=0.07)
    m = pebble(s, 8.0, 9.0, 6.4, 4.8, ink, spec=0.04)
    for rr, t in ((1.9, 4), (3.5, 3), (5.0, 2)):
        ring = s.mask(lambda x, y, rr=rr: abs(math.hypot((x - 7.4) / 1.25, (y - 8.6)) - rr) < 0.32)
        s.fill({p for p in ring if p in m}, pale[t])
    s.fill(s.disc(7.4, 8.6, 0.7), pale[5])
    s.outline()
    return s


def it_inverted_ore(res):
    """A shard of the Upside Realm's rock with its crystals hanging from it, points down, and motes falling up."""
    s = Spr(res)
    rock = hramp("8a3a9a")
    teal = hramp("4ad8c8", dl=0.1)
    pink = hramp("ff7ae8", dl=0.08)
    facet_crystal(s, 5.0, 6.0, 12.6, 1.6, teal, lean=-0.6, down=True)
    facet_crystal(s, 11.2, 6.0, 12.0, 1.5, teal, lean=0.6, down=True)
    facet_crystal(s, 8.2, 6.2, 15.0, 2.0, hramp("6ae8d8", dl=0.1), down=True)
    top = s.poly([(2.0, 6.4), (3.4, 3.6), (7.0, 2.4), (11.6, 3.0), (14.2, 5.6), (13.0, 7.4), (3.4, 7.4)])
    s.shade(top, rock, n_bevel(s, top, 1.8, flat=0.3), lo=1, hi=4)
    for (x, y) in ((5.0, 4.4), (10.4, 4.0)):
        s.dot(x, y, pink[4])
    s.outline()
    for (x, y) in ((2.2, 1.2), (8.0, 0.4), (13.4, 1.4)):
        s.dot(x, y, pink[5])
    return s


def it_brine_crystal(res):
    """A hopper crystal of sea salt: a stepped cube, its faces sunk in square terraces, a bead of brine on it."""
    s = Spr(res)
    salt = hramp("bfeef4", dl=0.08)
    sea = hramp("1ab0b0")
    top = s.poly([(8.0, 2.6), (14.0, 5.6), (8.0, 8.6), (2.0, 5.6)])
    left = s.poly([(2.0, 5.6), (8.0, 8.6), (8.0, 15.0), (2.0, 12.0)])
    right = s.poly([(8.0, 8.6), (14.0, 5.6), (14.0, 12.0), (8.0, 15.0)])
    s.fill(top, salt[4], rim=sea[0])
    s.fill(left, salt[3], rim=sea[0])
    s.fill(right, salt[1], rim=sea[0])
    # the terraces of a hopper crystal
    for k, sc in enumerate((0.62, 0.32)):
        c = (8.0, 5.6)
        s.edge(s.poly([(c[0] + (x - c[0]) * sc, c[1] + (y - c[1]) * sc) for x, y in ((8.0, 2.6), (14.0, 5.6), (8.0, 8.6), (2.0, 5.6))]),
               salt[2 + k], sides=("r", "b", "l", "t"))
        cl = (5.0, 10.3)
        s.edge(s.poly([(cl[0] + (x - cl[0]) * sc, cl[1] + (y - cl[1]) * sc) for x, y in ((2.0, 5.6), (8.0, 8.6), (8.0, 15.0), (2.0, 12.0))]),
               salt[2], sides=("r", "b"))
    s.fill(s.rect(7.6, 8.6, 8.4, 15.0), salt[5])
    s.fill(s.disc(11.4, 8.8, 1.2), sea[3])
    s.dot(10.8, 8.0, salt[5])
    s.outline()
    return s


def it_time_seed(res):
    """A teardrop seed of amber husk with an hourglass of sand painted in it, a green shoot waiting at its tip."""
    s = Spr(res)
    husk = hramp("a8682a")
    sand = hramp("f0d070", dl=0.07)
    leaf = hramp("6aa040")
    m = s.mask(lambda x, y: ((x - 8.0) / 4.4) ** 2 + ((y - 10.4) / 4.4) ** 2 <= 1 or (y < 10.4 and y > 4.2 and abs(x - 8.0) <= (y - 4.2) * 0.72))
    s.shade(m, husk, n_sphere(6.8, 9.0, 5.6, 6.0), lo=1, hi=4, spec=0.05)
    # the hourglass inside: two sand triangles, a gold waist
    s.fill(s.poly([(6.2, 7.6), (9.8, 7.6), (8.0, 10.2)]), sand[3])
    s.fill(s.poly([(8.0, 10.6), (10.2, 13.2), (5.8, 13.2)]), sand[4])
    s.fill(s.rect(5.6, 13.2, 10.4, 13.9), GOLD[4])
    s.fill(s.rect(5.6, 7.0, 10.4, 7.6), GOLD[4])
    s.line([(8.0, 4.4), (8.6, 2.6), (9.8, 1.6)], leaf[2], r=0.45)
    s.fill(s.ell(11.0, 2.2, 1.6, 0.9), leaf[3], rim=leaf[0])
    s.outline()
    return s


def it_chrono_shard(res):
    """An amber crystal ripened from a Time Seed, a clock's face caught inside it."""
    s = Spr(res)
    amber = hramp("e0a030", dl=0.1)
    m = facet_crystal(s, 8.0, 15.0, 1.0, 4.6, amber)
    face = s.disc(7.6, 9.4, 2.6)
    s.fill(face, PAPER[4])
    s.edge(face, amber[1], sides=("r", "b", "l", "t"))
    s.line([(7.6, 9.4), (7.6, 7.6)], INK, r=0.3)
    s.line([(7.6, 9.4), (8.9, 10.2)], INK, r=0.3)
    s.dot(4.6, 4.6, amber[5])
    s.outline()
    for (x, y) in ((12.6, 3.0), (2.4, 9.6)):
        s.dot(x, y, hramp("f0f0ff")[4])
    return s


def it_heartstone(res):
    """A ruby heart cut from the beating rock, its facets lit, a vein of light pulsing down its middle."""
    s = Spr(res)
    ruby = hramp("c42436", dl=0.1)
    rock = hramp("7a5040")

    def heart(x, y):
        X, Y = (x - 8.0) / 6.2, (9.0 - y) / 5.6
        return (X * X + Y * Y - 1) ** 3 - X * X * Y ** 3 <= 0
    m = s.mask(heart)
    left = {p for p in m if (p[0] + 0.5) / s.k < 8.0}
    s.fill(left, ruby[3], rim=ruby[0])
    s.fill(m - left, ruby[2], rim=ruby[0])
    # the facets: a lit crown on each lobe, a dark keel down the middle
    s.fill({p for p in left if (p[1] + 0.5) / s.k < 7.0}, ruby[4])
    s.fill({p for p in m - left if (p[1] + 0.5) / s.k < 6.4}, ruby[3])
    s.fill({p for p in m if abs((p[0] + 0.5) / s.k - 8.0) < 0.5 and (p[1] + 0.5) / s.k > 6.0}, ruby[1])
    s.dot(4.6, 4.8, ruby[5])
    s.dot(5.6, 4.0, ruby[5])
    s.line([(8.0, 7.2), (8.0, 11.4)], hramp("ffa860")[4], r=0.3)
    chips = s.poly([(1.6, 13.4), (3.6, 12.0), (5.0, 13.6), (3.0, 15.0)])
    s.shade(chips, rock, n_flat(-0.3, -0.4), lo=1, hi=3)
    s.outline()
    return s


def _ingot_body(s, x0, y0, x1, y1, depth):
    """A bevelled bar seen from the front and a little above: (x0, y0) to (x1, y1) the front face, `depth` the top."""
    top = s.poly([(x0 + depth, y0 - depth), (x1 - depth * 0.2, y0 - depth), (x1, y0), (x0, y0)])
    front = s.poly([(x0, y0), (x1, y0), (x1 - 0.6, y1), (x0 - 0.4, y1)])
    side = s.poly([(x0 + depth, y0 - depth), (x0, y0), (x0 - 0.4, y1), (x0 - 0.4 + depth * 0.4, y1 - depth * 0.9)])
    return top, front, side


def it_matriochkite_ingot(res):
    """The ingot the ten ores give: a core of red lacquer showing through a casing of gold leaf, every edge gilded and
    lit, a tiny painted doll in a cartouche on its face, the ten worlds glinting along its top, a star of light."""
    s = Spr(res)
    top, front, side = _ingot_body(s, 2.6, 7.4, 14.4, 12.8, 2.8)
    s.shade(top, LEAF, n_flat(-0.2, -0.9), lo=3, hi=5, rim=LEAF[0])
    s.fill(front, LEAF[3], rim=LEAF[0])
    s.fill(side, LEAF[2], rim=LEAF[0])
    # the lacquer core: a red panel sunk in the gold front, a dark lip below its top edge
    core = s.poly([(3.6, 8.4), (13.4, 8.4), (13.0, 12.0), (3.4, 12.0)])
    s.fill(core, LACQUER[3])
    s.fill({p for p in core if (p[1] + 0.5) / s.k < 9.1}, LACQUER[1])
    s.fill({p for p in core if (p[1] + 0.5) / s.k > 11.3}, LACQUER[4])
    # a gold cartouche with the painted doll in it
    cart = s.ell(8.4, 10.2, 2.0, 1.7)
    s.fill(cart, LEAF[4])
    s.fill(s.ell(8.4, 10.4, 1.3, 1.1), CREAM[3])
    s.fill(s.disc(8.4, 9.6, 0.55), LACQUER[3])
    s.fill(s.ell(8.4, 10.9, 0.8, 0.55), FLOWER[1])
    # gold flourishes either side
    for sx in (-1, 1):
        s.line([(8.4 + sx * 2.4, 10.2), (8.4 + sx * 3.6, 9.4), (8.4 + sx * 4.4, 10.4)], LEAF[4], r=0.32)
    # gilt edges lit, the bottom in shadow
    s.fill({p for p in front if (p[1] + 0.5) / s.k > 12.2}, LEAF[1])
    s.fill({p for p in top if abs((p[1] + 0.5) / s.k - 7.2) < 0.4}, LEAF[5])
    cols = [craft.WORLD_STYLE[w]["glow"][3] for w in range(1, 11)]
    for i, c in enumerate(cols[::2]):
        s.dot(5.6 + i * 1.7, 5.8, c)
    s.outline()
    # a star of light on the corner
    for (dx, dy) in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        s.dot(13.2 + dx, 4.4 + dy, LEAF[5] if (dx, dy) != (0, 0) else (255, 255, 255))
    return s


def it_matriochkite_nugget(res):
    """A nugget of Matriochkite: a gold pebble cracked open on its red lacquer heart, with a glint."""
    s = Spr(res)
    m = s.poly([(4.6, 9.0), (6.2, 6.4), (9.6, 5.8), (12.0, 7.6), (12.2, 10.6), (10.2, 12.6), (6.4, 12.4)])
    s.shade(m, LEAF, n_bevel(s, m, 1.8, flat=0.3), lo=2, hi=5)
    core = s.poly([(7.2, 9.4), (8.6, 7.8), (10.4, 8.6), (10.0, 10.6), (8.0, 10.8)])
    s.fill(core, LACQUER[3])
    s.fill(s.disc(8.9, 9.3, 0.7), LACQUER[4])
    s.edge(core, LACQUER[1], sides=("r", "b"))
    s.dot(6.4, 7.2, LEAF[5])
    s.outline()
    s.dot(12.6, 4.6, (255, 255, 255))
    s.dot(3.2, 12.6, LEAF[5])
    return s


def bl_matriochkite_block(res):
    """A block of Matriochkite: a red lacquer panel framed in gold leaf, a painted rosette of the ten worlds' colours
    round a gold doll, gold vines in the corners; the gold catches the light (it glows)."""
    s = Spr(res)

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 801) * 0.7 + pnoise(x, y, 8, 802) * 0.3
        return LACQUER[3] if g > 0.45 else LACQUER[2]
    tile(s, f)
    frame = s.mask(lambda x, y: x < 1.5 or x >= 14.5 or y < 1.5 or y >= 14.5)
    s.fill(frame, LEAF[3], glow=True)
    s.fill(s.mask(lambda x, y: (x < 0.6 or y < 0.6)), LEAF[5], glow=True)
    s.fill(s.mask(lambda x, y: (x >= 15.4 or y >= 15.4)), LEAF[1])
    s.fill(s.mask(lambda x, y: 1.5 <= x < 14.5 and 1.5 <= y < 14.5 and (x < 2.1 or x >= 13.9 or y < 2.1 or y >= 13.9)), LACQUER[0])
    # the rosette of the ten worlds
    for k in range(10):
        a = k * math.pi / 5
        x, y = 8 + math.sin(a) * 4.0, 8 - math.cos(a) * 4.0
        s.fill(s.disc(x, y, 0.9), craft.WORLD_STYLE[k + 1]["glow"][3], glow=True)
    s.fill(s.ring(8, 8, 2.6, 3.1), LEAF[3], glow=True)
    # the gold doll at its heart
    s.fill(s.ell(8, 9.0, 1.7, 1.6), LEAF[4], glow=True)
    s.fill(s.disc(8, 6.8, 1.1), LEAF[5], glow=True)
    s.fill(s.disc(8, 6.9, 0.6), CREAM[3])
    # gold vines in the corners
    for (cx, cy, sx, sy) in ((2.6, 2.6, 1, 1), (13.4, 2.6, -1, 1), (2.6, 13.4, 1, -1), (13.4, 13.4, -1, -1)):
        s.line([(cx, cy), (cx + sx * 1.6, cy + sy * 0.8), (cx + sx * 2.4, cy + sy * 2.0)], LEAF[4], r=0.3, glow=True)
        s.dot(cx + sx * 2.2 - 0.5, cy + sy * 2.2 - 0.5, FLOWER[2])
    return s


# =================================================================== the Matriarch Armour (items)
HELMET_ROWS = ["......##.......", "....######.....", "...########....", "..##########...", "..##########...",
               "..##########...", "..####..####...", "..###....###...", "..###....###...", "..###....###..."]


def it_matriarch(res, piece):
    """Red lacquer under heavy gold: the helmet a kokoshnik crowned with pearls, the chest a painted doll in a gold
    medallion, the legs and boots banded with gold leaf and little flowers."""
    s = Spr(res)
    k = s.k
    if piece == "helmet":
        m = s.mask(lambda x, y: (y >= 1.2 + 0.18 * (x - 8) ** 2 and y < 11.0 and 2.0 <= x < 14.0) and not (5.0 <= x < 11.0 and y >= 7.2))
    elif piece == "boots":
        m = s.mask(lambda x, y: (2.0 <= x < 7.0 or 9.0 <= x < 14.0) and 7.0 <= y < 14.0 and not ((x < 4.0 or 9.0 <= x < 11.0) and y < 10.0))
    else:
        m = _rows_mask(s, ARMOR_ROWS[piece])
    s.shade(m, LACQUER, n_bevel(s, m, 2.2, flat=0.35), lo=1, hi=4, spec=0.0)
    ys = sorted({p[1] for p in m})
    xs = sorted({p[0] for p in m})
    u = lambda p: ((p[0] + 0.5) / k, (p[1] + 0.5) / k)  # noqa: E731
    # a gold rim all round, lit on top
    rim = s.edge(m, LEAF[2], sides=("r", "b", "l", "t"))
    s.fill({p for p in rim if u(p)[1] < 7}, LEAF[4])
    if piece == "helmet":
        # the kokoshnik's arch: a band of gold under its edge, pearls along it, a jewel at its crown
        band = {p for p in m if any((p[0] + a, p[1] - b) not in m for a in (-1, 0, 1) for b in (1, 2)) and u(p)[1] < 7.2}
        s.fill(band, LEAF[3])
        for x in (4.0, 6.0, 10.0, 12.0):
            y = 1.2 + 0.18 * (x - 8) ** 2 + 1.3
            s.dot(x - 0.5, y - 0.5, CREAM[4])
        s.fill(s.disc(8.0, 4.4, 1.2), FLOWER[1])
        s.dot(7.5, 3.6, CREAM[4])
        s.fill({p for p in m if 6.6 <= u(p)[1] < 7.4}, LEAF[4])
    elif piece == "chestplate":
        s.fill({p for p in m if u(p)[1] < ys[0] / k + 1.6}, LEAF[3])
        s.fill({p for p in m if abs(u(p)[1] - 12.2) < 0.5}, LEAF[3])
        med = s.disc(8.0, 7.8, 2.6)
        s.fill(med, LEAF[4], rim=LEAF[1])
        s.edge(med, LEAF[1], sides=("r", "b"))
        # the painted doll inside the medallion
        s.fill(s.disc(8.0, 6.9, 0.95), CREAM[3])
        s.fill(s.ell(8.0, 8.9, 1.5, 1.0), LACQUER[3])
        s.dot(7.5, 8.4, CREAM[4])
        for (x, y) in ((4.0, 9.6), (11.0, 9.6), (4.0, 5.0), (11.0, 5.0)):
            s.dot(x, y, FLOWER[2])
            s.dot(x, y + 1, LEAF[4])
    elif piece == "leggings":
        s.fill({p for p in m if u(p)[1] < ys[0] / k + 1.4}, LEAF[3])
        for x0 in (4.0, 10.0):
            s.fill({p for p in m if abs(u(p)[0] - x0 - 0.5) < 0.5 and u(p)[1] > 5}, LEAF[3])
        for (x, y) in ((4.5, 8.0), (10.5, 8.0), (4.5, 11.5), (10.5, 11.5)):
            s.dot(x - 0.5, y - 0.5, FLOWER[2])
        s.fill({p for p in m if (p[1] + 0.5) / k > ys[-1] / k - 0.5}, LEAF[2])
    else:
        s.fill({p for p in m if u(p)[1] < 8.6}, LEAF[4])
        s.fill({p for p in m if u(p)[1] > 12.6}, LEAF[3])
        for x in (4.0, 10.5):
            s.dot(x, 10.0, FLOWER[2])
    s.outline()
    return s


# =================================================================== the Matriarch Armour (worn)
def paint_matriarch_layer(path, legs=False):
    """64x32 humanoid layer, the most precious set of the mod: red lacquer strewn with little gold flowers, every edge
    bound in gold leaf; a kokoshnik arch with a row of pearls over the brow, the face left open; a caftan front with a
    gold placket and buttons, a painted doll in a gold medallion on the chest and a great gold doll down the back;
    gold bands of flowers at the shoulders, the waist and the knees, gilded cuffs and toes. Box UVs as vanilla's."""
    from PIL import Image
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # worn, the model is shaded by the world's light: the gold and the lacquer are laid a tone brighter than the items'
    LEAF = [(112, 70, 18), (172, 122, 36), (224, 172, 58), (248, 208, 96), (255, 234, 150), (255, 248, 212)]
    LACQUER = [(60, 8, 14), (118, 18, 24), (172, 30, 32), (206, 44, 40), (232, 84, 64), (250, 150, 120)]

    def put(x, y, c):
        if 0 <= x < 64 and 0 <= y < 32:
            img.putpixel((x, y), tuple(c[:3]) + (255,))

    def clear(x, y):
        if 0 <= x < 64 and 0 <= y < 32:
            img.putpixel((x, y), (0, 0, 0, 0))

    def face(x0, y0, w, h, kind):
        """Lacquer with a scatter of gold flowers, bound in gold on every edge (lit on top, deep at the bottom)."""
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                lx, ly = x - x0, y - y0
                g = pnoise(x * 0.9, y * 0.9, 4, 501)
                c = LACQUER[3] if g > 0.4 else LACQUER[2]
                if (lx + 2 * ly) % 5 == 0 and (2 * lx + ly) % 7 == 3:
                    c = LEAF[3]
                if kind != "top" and lx == w - 1:
                    c = LACQUER[1]
                if ly == 0:
                    c = LEAF[4]
                if ly == h - 1:
                    c = LEAF[1]
                put(x, y, c)

    def box(u, v, w, h, dd):
        """The six faces; returns the front's origin, the back's x and the sides' x."""
        face(u + dd, v, w, dd, "top")
        face(u + dd + w, v, w, dd, "top")
        face(u, v + dd, dd, h, "side")
        face(u + dd, v + dd, w, h, "front")
        face(u + dd + w, v + dd, dd, h, "side")
        face(u + dd + w + dd, v + dd, w, h, "back")
        return u + dd, v + dd, u + dd + w + dd, (u, u + dd + w)

    def band(spans, y, top, under=None, flowers=False):
        for (fx, fw) in spans:
            for x in range(fx, fx + fw):
                put(x, y, top)
                if under is not None:
                    put(x, y + 1, under)
                if flowers and (x - fx) % 3 == 1:
                    put(x, y, FLOWER[1])
                    if under is not None:
                        put(x, y + 1, LEAF[4])

    def doll(cx, cy, scale=1, gold=False):
        """A painted matryoshka: head of 2 (x scale), shoulders, a round body with an apron and a rose."""
        body = LEAF if gold else LACQUER
        rows = [".hh.", "hffh", "hffh", "bbbb", "bAAb", "bARb", "bAAb", ".bb."] if scale == 1 else \
               ["..hh..", ".hffh.", ".hffh.", "..hh..", ".bbbb.", "bbAAbb", "bARRAb", "bARRAb", "bbAAbb", ".bbbb."]
        cols = {"h": body[4] if not gold else LEAF[2], "f": CREAM[3] if not gold else LEAF[5], "b": body[3] if not gold else LEAF[3],
                "A": CREAM[3] if not gold else LEAF[4], "R": FLOWER[1] if not gold else LEAF[2]}
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in cols:
                    put(cx + i - len(row) // 2, cy + j, cols[ch])

    if not legs:
        # ---- helmet: the kokoshnik over the brow, pearls along its arch, a ruby at its crown; the face left open
        fx, fy, bx, (sr, sl) = box(0, 0, 8, 8, 8)
        for x in range(fx, fx + 8):
            arch = 3 + (1 if x in (fx, fx + 7) else 0)
            for y in range(fy, fy + 8):
                ly = y - fy
                if ly < arch:
                    put(x, y, LEAF[3] if ly < arch - 1 else LEAF[1])
                elif x in (fx, fx + 7):
                    put(x, y, LEAF[2])
                elif x in (fx + 1, fx + 6) and ly >= 5:
                    put(x, y, LACQUER[3])
                else:
                    clear(x, y)
        for x in (fx + 1, fx + 3, fx + 4, fx + 6):
            put(x, fy + 2, CREAM[4])
        put(fx + 3, fy + 1, FLOWER[1])
        put(fx + 4, fy + 1, FLOWER[2])
        put(fx + 3, fy, LEAF[5])
        put(fx + 4, fy, LEAF[5])
        # the crown of the head: a gold rosette
        for (x, y) in ((11, 3), (12, 3), (11, 4), (12, 4)):
            put(x, y, FLOWER[1])
        for (x, y) in ((10, 3), (13, 4), (11, 2), (12, 5), (10, 4), (13, 3), (11, 5), (12, 2)):
            put(x, y, LEAF[4])
        # the back of the head: a gold braid down its middle
        for y in range(fy, fy + 8):
            put(bx + 3, y, LEAF[3] if y % 2 else LEAF[4])
            put(bx + 4, y, LEAF[2] if y % 2 else LEAF[3])
        band(((sr, 8), (sl, 8), (bx, 8)), fy + 3, LEAF[3], flowers=True)
        # the crest on the hat layer, over the brow
        for x in range(40, 48):
            put(x, 8, LEAF[4])
            put(x, 9, LEAF[2] if x in (40, 47) else (CREAM[4] if x % 2 else LEAF[3]))
        # ---- the caftan
        fx, fy, bx, (sr, sl) = box(16, 16, 8, 12, 4)
        # a gold collar; on the breast a gold medallion with the painted doll in it
        band(((fx, 8), (bx, 8), (sr, 4), (sl, 4)), fy, LEAF[4], LEAF[2])
        ring = [(1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (5, 1), (0, 2), (5, 2), (0, 3), (5, 3), (0, 4), (5, 4), (1, 5), (2, 5), (3, 5), (4, 5)]
        mx, my = fx + 1, fy + 1
        for (x, y) in [(i, j) for i in range(1, 5) for j in range(1, 5)]:
            put(mx + x, my + y, LACQUER[1])
        for (x, y) in ring:
            put(mx + x, my + y, LEAF[4] if y < 3 else LEAF[2])
        for (x, y, c) in ((2, 1, CREAM[3]), (3, 1, CREAM[3]), (2, 2, CREAM[2]), (3, 2, CREAM[2]), (1, 3, LACQUER[4]), (2, 3, CREAM[4]),
                          (3, 3, FLOWER[1]), (4, 3, LACQUER[4]), (1, 4, LACQUER[3]), (2, 4, LACQUER[3]), (3, 4, LACQUER[3]), (4, 4, LACQUER[3])):
            put(mx + x, my + y, c)
        # gold buttons below it, down to the belt
        put(fx + 3, fy + 7, LEAF[4])
        put(fx + 4, fy + 7, LEAF[3])
        # below the belt, the caftan's skirt opens on a gold hem
        for y in range(fy + 10, fy + 12):
            put(fx + 3, y, LEAF[3])
            put(fx + 4, y, LEAF[2])
        # the waist: a belt of gold flowers
        band(((fx, 8), (bx, 8), (sr, 4), (sl, 4)), fy + 8, LEAF[4], LEAF[2], flowers=True)
        # the great gold doll down the back
        doll(bx + 4, fy + 1, scale=2, gold=True)
        # ---- the sleeves: flowered pauldrons, a band at the elbow, gilded cuffs
        fx, fy, bx, (sr, sl) = box(40, 16, 4, 12, 4)
        spans = ((sr, 4), (fx, 4), (sl, 4), (bx, 4))
        band(spans, fy, LEAF[4], LEAF[3], flowers=True)
        band(spans, fy + 10, LEAF[4], LEAF[2])
        # ---- boots: a flowered cuff, gilded toes
        fx, fy, bx, (sr, sl) = box(0, 16, 4, 12, 4)
        spans = ((sr, 4), (fx, 4), (sl, 4), (bx, 4))
        band(spans, fy + 6, LEAF[4], LEAF[2], flowers=True)
        for x in range(fx, fx + 4):
            put(x, fy + 10, LEAF[3])
            put(x, fy + 11, LEAF[2])
        for x in range(4, 8):
            put(x, 16, LEAF[4])
            put(x, 17, LEAF[3])
    else:
        # ---- the leggings: a belt of gold flowers, gold seams down the sides and the front, knee cups with a rose
        fx, fy, bx, (sr, sl) = box(16, 16, 8, 12, 4)
        band(((fx, 8), (bx, 8), (sr, 4), (sl, 4)), fy + 8, LEAF[4], LEAF[2], flowers=True)
        fx, fy, bx, (sr, sl) = box(0, 16, 4, 12, 4)
        for y in range(fy, fy + 12):
            put(sr, y, LEAF[3])
            put(sl + 3, y, LEAF[3])
            put(fx + 3, y, LEAF[2])
        band(((sr, 4), (fx, 4), (sl, 4), (bx, 4)), fy + 4, LEAF[4], LEAF[2])
        put(fx + 1, fy + 5, FLOWER[1])
        put(fx + 2, fy + 5, FLOWER[2])
        put(fx + 1, fy + 6, LEAF[4])
        put(fx + 2, fy + 6, LEAF[4])
    img.save(path)


# =================================================================== the ore blocks
def _host(s, ramp, seed):
    def f(x, y, i, j):
        g = pnoise(x, y, 4, seed) * 0.65 + pnoise(x, y, 8, seed + 1) * 0.35
        t = 1 if g < 0.34 else 2 if g < 0.66 else 3
        return ramp[t]
    tile(s, f)


def bl_living_ember_ore(res):
    """Ashrock split by veins of living fire, a few coals glowing in them."""
    s = Spr(res)
    _host(s, hramp("3e2c26", dl=0.08), 611)
    fire, yellow = hramp("ff6a1a", dl=0.07), hramp("ffd84a", dl=0.06)
    for path in ([(0.0, 5.0), (3.6, 6.4), (6.0, 4.4), (9.4, 6.0), (12.4, 4.8), (16.0, 5.0)],
                 [(6.0, 4.4), (5.4, 9.6), (7.8, 12.0), (7.2, 16.0)], [(9.4, 6.0), (11.6, 10.4), (16.0, 11.6)],
                 [(0.0, 11.6), (2.8, 12.8), (5.4, 9.6)], [(7.2, 0.0), (6.0, 4.4)]):
        s.line(path, fire[2], r=0.45, glow=True)
    for (x, y, r) in ((3.0, 2.6, 1.3), (11.4, 12.4, 1.5), (13.0, 2.4, 1.0), (2.4, 9.2, 1.1)):
        c = s.disc(x, y, r)
        s.fill(c, fire[3], glow=True)
        s.dot(x - 0.6, y - 0.6, yellow[4], glow=True)
    for (x, y) in ((6.0, 4.4), (9.4, 6.0), (5.4, 9.6)):
        s.dot(x - 0.5, y - 0.5, yellow[5], glow=True)
    return s


def bl_fulgurite_ore(res):
    """Cloudstone fused by a bolt: glassy forks of fulgurite in the pale stone, caught lightning down their cores."""
    s = Spr(res)
    _host(s, hramp("c8d8ec", dl=0.06), 621)
    glass, core = hramp("8ab4e4", dl=0.08), hramp("ffe14a", dl=0.06)
    forks = [[(8.0, 0.0), (7.0, 4.0), (9.0, 7.0), (7.4, 11.0), (8.6, 16.0)], [(9.0, 7.0), (12.6, 8.4), (16.0, 7.6)],
             [(7.0, 4.0), (3.0, 3.0), (0.0, 4.4)], [(7.4, 11.0), (3.4, 12.6), (1.0, 16.0)]]
    for f in forks:
        s.line(f, glass[2], r=0.9)
    for f in forks:
        s.line(f, core[3], r=0.35, glow=True)
    for (x, y) in ((9.0, 7.0), (7.0, 4.0), (7.4, 11.0)):
        s.dot(x - 0.5, y - 0.5, core[5], glow=True)
    return s


def bl_silent_stone_ore(res):
    """The Deep's black stone with pale pebbles set in it, each ringed like a still pool."""
    s = Spr(res)
    _host(s, hramp("1a1a2c", dl=0.06, bottom=0.03), 631)
    pale = hramp("c8ccf0", dl=0.07)
    for (x, y, rx, ry) in ((4.0, 4.4, 2.6, 1.9), (11.6, 7.4, 2.4, 1.8), (5.6, 12.2, 2.2, 1.6), (13.4, 13.6, 1.6, 1.2)):
        m = s.ell(x, y, rx, ry)
        s.shade(m, hramp("3a4478", dl=0.08), n_sphere(x - 0.6, y - 0.6, rx * 1.2, ry * 1.2), lo=1, hi=4)
        s.fill({p for p in m if abs(math.hypot(((p[0] + 0.5) / s.k - x) / rx, ((p[1] + 0.5) / s.k - y) / ry) - 0.62) < 0.18}, pale[3])
        s.dot(x - 0.8, y - 0.8, pale[5])
    return s


def bl_hanging_ore(res):
    """The Upside Realm's stone with crystals hanging in it, points down, their glow dripping upwards."""
    s = Spr(res)
    _host(s, hramp("b44ccc", dl=0.07), 641)
    teal, pink = hramp("4ad8c8", dl=0.09), hramp("ff9aee", dl=0.07)
    for (x, y, w, h) in ((3.6, 2.0, 1.4, 6.0), (10.6, 5.0, 1.6, 7.4), (6.6, 9.6, 1.2, 5.0), (13.6, 0.0, 1.0, 4.0)):
        m = s.poly([(x - w, y), (x + w, y), (x, y + h)])
        left = {p for p in m if (p[0] + 0.5) / s.k < x}
        s.fill(left, teal[4], glow=True)
        s.fill(m - left, teal[2], glow=True)
        s.dot(x - 0.5, y, teal[5], glow=True)
    for (x, y) in ((2.0, 12.4), (12.0, 14.0), (8.4, 3.0)):
        s.dot(x, y, pink[4], glow=True)
    return s


def bl_sprout(res, stage):
    """The Time Sprout, cross-shaped: a shoot, a seedling, a bud of amber, then the ripe Chrono Shard on its stem."""
    s = Spr(res)
    stem, leaf = hramp("4a7a2a"), hramp("6aa040")
    amber = hramp("e0a030", dl=0.1)
    h = (4.0, 7.0, 10.0, 11.0)[stage]
    s.line([(8.0, 16.0), (8.0, 16.0 - h)], stem[2], r=0.5)
    if stage >= 1:
        for sx in (-1, 1):
            m = s.ell(8 + sx * 2.4, 16.0 - h * 0.55, 2.2, 1.0)
            s.fill(m, leaf[3], rim=leaf[0])
    if stage >= 2:
        for sx in (-1, 1):
            m = s.ell(8 + sx * 2.0, 16.0 - h * 0.85, 1.8, 0.8)
            s.fill(m, leaf[4], rim=leaf[0])
    if stage == 2:
        bud = s.ell(8.0, 16.0 - h - 0.8, 1.4, 1.8)
        s.fill(bud, amber[3], rim=amber[0])
        s.dot(7.4, 16.0 - h - 1.6, amber[5])
    if stage == 3:
        facet_crystal(s, 8.0, 16.0 - h + 1.0, 1.2, 2.4, amber, glow=True)
        face = s.disc(7.8, 16.0 - h - 3.4, 1.2)
        s.fill(face, PAPER[4], glow=True)
        s.dot(7.4, 16.0 - h - 4.0, INK)
    s.outline()
    return s


# =================================================================== the Nesting Cradle
def m_cradle_lacquer(res):
    """Red lacquer with a scatter of little gold flowers."""
    s = Spr(res)

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 701) * 0.7 + pnoise(x, y, 8, 702) * 0.3
        return LACQUER[2] if g < 0.42 else LACQUER[3]
    tile(s, f)
    for (x, y) in ((3.0, 3.0), (11.0, 5.0), (6.0, 11.0), (14.0, 13.0)):
        for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            s.dot(x + dx, y + dy, LEAF[3])
        s.dot(x, y, FLOWER[2])
    return s


def m_cradle_apron(res):
    """The doll's painted front: a cream apron framed in gold, a red rose with green leaves on it."""
    s = m_cradle_lacquer(res)
    ap = s.ell(8.0, 8.6, 5.6, 5.2)
    s.fill(ap, CREAM[3])
    s.edge(ap, LEAF[3], sides=("r", "b", "l", "t"))
    s.fill(s.ring(8.0, 8.6, 5.6, 6.4), LEAF[2])
    s.fill(s.disc(8.0, 8.0, 2.2), FLOWER[1], rim=FLOWER[0])
    s.fill(s.disc(7.4, 7.4, 0.9), FLOWER[2])
    s.dot(8.4, 8.6, FLOWER[0])
    for sx in (-1, 1):
        s.fill(s.ell(8 + sx * 3.0, 10.6, 1.6, 0.8), hramp("5a8a34")[3])
    for (x, y) in ((5.0, 5.0), (11.0, 5.0), (8.0, 12.6)):
        s.dot(x, y, LEAF[4])
    return s


def m_cradle_face(res):
    """The doll's head on the lid: a red scarf, a cream face, dark hair parted, two eyes and rosy cheeks."""
    s = m_cradle_lacquer(res)
    fm = s.ell(8.0, 8.6, 5.0, 5.4)
    s.fill(s.ell(8.0, 8.6, 5.8, 6.2), LEAF[3])
    s.shade(fm, SKIN, n_sphere(7.0, 7.4, 7.0, 7.4), rim=False, lo=2, hi=4)
    hair = s.mask(lambda x, y: ((x - 8) / 5.0) ** 2 + ((y - 8.6) / 5.4) ** 2 <= 1 and y < 6.0 + abs(x - 8) * 0.45)
    s.fill(hair, (92, 50, 30))
    s.fill(s.rect(7.6, 3.2, 8.4, 5.4), (60, 30, 18))
    for x in (5.6, 9.6):
        s.fill(s.rect(x, 8.0, x + 1.0, 9.4), INK)
        s.dot(x - 0.6, 10.4, CHEEK)
        s.dot(x + 1.0, 10.4, CHEEK)
    s.fill(s.rect(7.4, 11.6, 8.8, 12.4), (190, 40, 40))
    return s


def m_cradle_top(res):
    """The open bowl seen from above: a gold rim, the dark lacquer inside with a painted gold ring."""
    s = Spr(res)

    def f(x, y, i, j):
        return (34, 8, 10) if pnoise(x, y, 4, 711) < 0.5 else (52, 12, 14)
    tile(s, f)
    s.fill(s.ring(8, 8, 4.4, 5.2), LEAF[2])
    s.fill(s.ring(8, 8, 6.6, 9.0), LEAF[3])
    s.fill(s.ring(8, 8, 6.6, 7.1), LEAF[1])
    s.fill(s.disc(8, 8, 1.2), LEAF[4])
    return s


def m_cradle_gold(res):
    """Gold leaf, burnished, with a fine engraved scroll."""
    s = Spr(res)

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 721) * 0.6 + pnoise(x, y, 8, 722) * 0.4
        return LEAF[3] if g < 0.5 else LEAF[4]
    tile(s, f)
    for x0 in range(0, 16, 4):
        s.line([(x0 + 0.5, 12.5), (x0 + 1.5, 11.0), (x0 + 3.0, 11.6)], LEAF[2], r=0.3)
    for (x, y) in ((2.0, 3.0), (9.0, 5.0), (13.0, 2.0)):
        s.dot(x, y, LEAF[5])
    return s


def m_shell_gold(res):
    """The golden doll shells of the ritual: gold leaf over the lacquer, painted with flowers and bands."""
    s = Spr(res)

    def f(x, y, i, j):
        g = pnoise(x, y, 4, 731) * 0.65 + pnoise(x, y, 8, 732) * 0.35
        return LEAF[2] if g < 0.42 else LEAF[3]
    tile(s, f)
    for y0 in (0.0, 8.0):
        s.fill(s.rect(0, y0, 16, y0 + 1.0), LEAF[2])
    for (x, y) in ((2.0, 4.0), (6.0, 4.0), (10.0, 4.0), (14.0, 4.0), (4.0, 12.0), (8.0, 12.0), (12.0, 12.0)):
        for (dx, dy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            s.dot(x + dx, y + dy, LEAF[4])
        s.dot(x, y, FLOWER[1])
    return s


def m_shell_face(res):
    """The front of the shells' heads, drawn tall because the head's face is twice as wide as it is high: a golden
    face framed by a scarf of red, eyes and cheeks engraved."""
    s = m_shell_gold(res)
    s.fill(s.rect(0, 0, 16, 16), LACQUER[3])
    fm = s.ell(8.0, 8.6, 4.6, 7.6)
    s.fill(fm, LEAF[5])
    s.edge(fm, LEAF[3], sides=("r", "b", "l", "t"))
    hair = s.mask(lambda x, y: ((x - 8) / 4.6) ** 2 + ((y - 8.6) / 7.6) ** 2 <= 1 and y < 4.6 + abs(x - 8) * 0.9)
    s.fill(hair, LEAF[2])
    for x in (5.8, 9.2):
        s.fill(s.rect(x, 7.4, x + 1.0, 10.2), LEAF[0])
        s.fill(s.rect(x - 0.6, 11.4, x + 1.2, 12.8), FLOWER[2])
    s.fill(s.rect(7.4, 13.0, 8.6, 14.4), FLOWER[1])
    for x in (1.0, 14.0):
        s.dot(x, 3.0, LEAF[4])
        s.dot(x, 12.0, LEAF[4])
    return s


def m_shell_apron(res):
    """The shells' painted fronts: a cream apron with a red rose and its leaves, on the gold, at the height of the
    lower half (the faces take the pixels under them)."""
    s = m_shell_gold(res)
    ap = s.ell(8.0, 11.0, 4.6, 3.8)
    s.fill(ap, CREAM[3])
    s.edge(ap, LEAF[1], sides=("r", "b", "l", "t"))
    s.fill(s.disc(8.0, 10.6, 1.7), FLOWER[1], rim=FLOWER[0])
    s.dot(7.4, 10.0, FLOWER[2])
    for sx in (-1, 1):
        s.fill(s.ell(8 + sx * 2.6, 12.4, 1.4, 0.7), hramp("5a8a34")[3])
    return s


def cradle_materials(res=16):
    """{texture name under block/cradle/: sprite}."""
    return {"lacquer": m_cradle_lacquer(res), "apron": m_cradle_apron(res), "face": m_cradle_face(res), "top": m_cradle_top(res),
            "gold": m_cradle_gold(res), "shell_gold": m_shell_gold(res), "shell_face": m_shell_face(res), "shell_apron": m_shell_apron(res)}


class _M:
    """The cradle's model elements, built like the stations' (tools/stations3d.py): boxes with vanilla-style UVs."""

    def __init__(self):
        self.el = []
        self.tex = {"particle": f"{NS}:block/cradle/lacquer"}

    def t(self, name):
        self.tex[name] = f"{NS}:block/cradle/{name}"
        return "#" + name

    def box(self, frm, to, tex, rot=None, full=(), faces=None, glow=False):
        x0, y0, z0 = frm
        x1, y1, z1 = to
        fs = {}
        for f in faces or ("north", "south", "east", "west", "up", "down"):
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
            face = {"uv": [round(v, 3) for v in uv], "texture": self.t(mat)}
            if f == "down" and y0 <= 0:
                face["cullface"] = "down"
            fs[f] = face
        e = {"from": [round(v, 3) for v in frm], "to": [round(v, 3) for v in to], "faces": fs}
        if rot:
            axis, angle, origin = rot
            e["rotation"] = {"angle": angle, "axis": axis, "origin": list(origin)}
        if glow:
            e["light_emission"] = 15
        self.el.append(e)

    def octagon(self, y0, y1, r, tex, lower=0.0, full=()):
        """An eight-sided slab of radius r round the block's middle: a box and the same box turned 45 degrees."""
        self.box([8 - r, y0, 8 - r], [8 + r, y1, 8 + r], tex, full=full)
        self.box([8 - r * 0.98, y0 + lower, 8 - r * 0.98], [8 + r * 0.98, y1 - lower, 8 + r * 0.98],
                 {k: v for k, v in (tex.items() if isinstance(tex, dict) else {"*": tex}.items()) if k != "north"} if isinstance(tex, dict) else tex,
                 rot=("y", 45, (8, 8, 8)))


def cradle_model():
    """The Nesting Cradle: an opened doll of red lacquer and gold. Its lower half stands as a bowl on a gilded foot, its
    painted rose to the front; its upper half, the head, leans open against the back. The ores ring above the bowl."""
    m = _M()
    m.octagon(0, 1.2, 4.6, "gold")
    m.octagon(1.2, 2.4, 4.0, "lacquer")
    m.octagon(2.4, 4.0, 5.2, {"*": "lacquer", "north": "apron", "up": "top"}, lower=0.01, full=("north",))
    m.octagon(4.0, 7.0, 6.1, {"*": "lacquer", "north": "apron", "up": "top"}, lower=0.01, full=("north",))
    m.octagon(7.0, 8.0, 6.5, {"*": "gold", "up": "top"}, lower=0.02)
    # the inside of the bowl, sunk below its rim
    m.box([3.0, 7.6, 3.0], [13.0, 8.05, 13.0], {"up": "top"}, faces=("up",), full=("up",))
    # the lid: the doll's upper half, its face to the front, leaning open against the back of the bowl
    lean = ("x", -22.5, (8, 8, 13.5))
    m.box([3.6, 7.6, 12.0], [12.4, 11.0, 15.4], {"*": "lacquer", "north": "lacquer"}, rot=lean)
    m.box([3.4, 7.4, 11.8], [12.6, 8.4, 15.6], "gold", rot=lean)
    m.box([4.6, 11.0, 12.4], [11.4, 16.0, 15.0], {"*": "lacquer", "north": "face", "up": "gold"}, rot=lean, full=("north",))
    m.box([4.2, 10.6, 12.2], [11.8, 11.2, 15.2], "gold", rot=lean)
    return {"parent": "minecraft:block/block", "ambientocclusion": True, "textures": m.tex, "elements": m.el,
            "display": {
                "gui": {"rotation": [30, 225, 0], "translation": [0, -1, 0], "scale": [0.625, 0.625, 0.625]},
                "ground": {"rotation": [0, 0, 0], "translation": [0, 3, 0], "scale": [0.25, 0.25, 0.25]},
                "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.5, 0.5, 0.5]},
                "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.375, 0.375, 0.375]},
                "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]},
                "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 0, 0], "scale": [0.4, 0.4, 0.4]}}}


# the profile of a golden doll shell, turned on the lathe: (y0, y1, radius) in model units, from its foot up. Its two
# halves meet at the waist (SHELL_WAIST): the ritual closes them round the ores.
SHELL_PROFILE = [(0.0, 0.8, 3.8), (0.8, 2.2, 4.9), (2.2, 4.4, 5.6), (4.4, 7.4, 5.8), (7.4, 8.4, 5.5), (8.4, 9.4, 4.8),
                 (9.4, 10.2, 4.1), (10.2, 14.2, 3.9), (14.2, 15.2, 3.0), (15.2, 16.0, 1.8)]
SHELL_WAIST = 7.4


def shell_model(half):
    """One half of a golden doll shell, as an item model shown by a display entity: 'top' (the head, its face to the
    south: the front of an item display) or 'bottom'. The model is centred like any item: its middle is the
    display's position."""
    m = _M()
    m.tex = {"particle": f"{NS}:block/cradle/shell_gold"}
    for (y0, y1, r) in SHELL_PROFILE:
        if (half == "top") != (y0 >= SHELL_WAIST):
            continue
        head = y0 >= 10.2 and y1 <= 14.2
        apron = 2.2 <= y0 and y1 <= SHELL_WAIST
        tex = {"*": "shell_gold", "south": "shell_face"} if head else {"*": "shell_gold", "south": "shell_apron"} if apron else "shell_gold"
        m.box([8 - r, y0, 8 - r], [8 + r, y1, 8 + r], tex, full=("south",) if head else ())
    # the gold fillet at the waist where the halves meet
    y = SHELL_WAIST
    if half == "bottom":
        m.box([2.0, y - 0.6, 2.0], [14.0, y, 14.0], "gold")
    else:
        m.box([2.2, y, 2.2], [13.8, y + 0.5, 13.8], "gold")
    return {"textures": m.tex, "elements": m.el}


# =================================================================== dispatch (craft.py)
_ITEMS = {"spore_crystal": it_spore_crystal, "living_ember": it_living_ember, "golden_ward": it_golden_ward, "fulgurite": it_fulgurite,
          "silent_stone": it_silent_stone, "inverted_ore": it_inverted_ore, "brine_crystal": it_brine_crystal, "time_seed": it_time_seed,
          "chrono_shard": it_chrono_shard, "heartstone": it_heartstone, "matriochkite_ingot": it_matriochkite_ingot,
          "matriochkite_nugget": it_matriochkite_nugget}
_BLOCKS = {"living_ember_ore": bl_living_ember_ore, "fulgurite_ore": bl_fulgurite_ore, "silent_stone_ore": bl_silent_stone_ore,
           "hanging_ore": bl_hanging_ore, "matriochkite_block": bl_matriochkite_block}


def crafted_item(it, res=16):
    if it["id"] in _ITEMS:
        return _ITEMS[it["id"]](res)
    if it.get("kind") == "armor" and it.get("set") == "matriarch":
        return it_matriarch(res, it["piece"])
    return None


def crafted_block(bid, res=16):
    if bid in _BLOCKS:
        return {"": _BLOCKS[bid](res)}
    return None


# =================================================================== gen.py
def gen(write, assets, lang, ore_how):
    """The cradle's materials and model, the Time Sprout's stages, the doll shells' item models, the ores' Journal lines."""
    d = os.path.join(assets, "textures/block/cradle")
    os.makedirs(d, exist_ok=True)
    for name, spr in cradle_materials(16).items():
        spr.image().save(os.path.join(d, name + ".png"))
    write(os.path.join(assets, "models/block/nesting_cradle.json"), cradle_model())
    write(os.path.join(assets, "blockstates/nesting_cradle.json"), {"variants": {
        f"facing={f}": ({"model": f"{NS}:block/nesting_cradle", "y": y} if y else {"model": f"{NS}:block/nesting_cradle"})
        for f, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270))}})
    for st in range(4):
        bl_sprout(16, st).image().save(os.path.join(assets, f"textures/block/time_sprout_{st}.png"))
        write(os.path.join(assets, f"models/block/time_sprout_{st}.json"),
              {"parent": "minecraft:block/cross", "textures": {"cross": f"{NS}:block/time_sprout_{st}"}})
    write(os.path.join(assets, "blockstates/time_sprout.json"), {"variants": {f"age={st}": {"model": f"{NS}:block/time_sprout_{st}"} for st in range(4)}})
    for half in ("top", "bottom"):
        write(os.path.join(assets, f"models/item/cradle_shell_{half}.json"), shell_model(half))
        write(os.path.join(assets, f"items/cradle_shell_{half}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:item/cradle_shell_{half}"}})
    sprites = os.path.join(assets, "textures/gui/sprites")
    for kind in ("empty", "full", "glint"):
        hud_shell(kind).save(os.path.join(sprites, f"matriarch_shell_{kind}.png"))
    for iid, (en, fr) in ore_how.items():
        lang(f"journal.{NS}.card.how.{iid}", en, fr)


def hud_shell(kind):
    """The Nested Shell beside the hearts, 9 x 11 like the vanilla icons: a doll outline ('empty'), the doll in red
    lacquer and gold ('full', drawn over the empty one from the foot up as the shell mends) and a glint ('glint')."""
    from PIL import Image
    rows = ["...###...", "..#####..", "..##f##..", "..#####..", "...###...", ".#######.", "#########", "###aaa###",
            "###aaa###", ".#######.", "..#####.."]
    img = Image.new("RGBA", (9, 11), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            edge = any(not (0 <= x + dx < 9 and 0 <= y + dy < 11) or rows[y + dy][x + dx] == "." for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if kind == "empty":
                c = (0, 0, 0) if edge else (40, 30, 30)
            elif kind == "full":
                if edge:
                    c = (60, 8, 12)
                elif ch == "f":
                    c = CREAM[3]
                elif ch == "a":
                    c = LEAF[4]
                elif y == 5:
                    c = LEAF[3]
                else:
                    c = LACQUER[4] if x < 4 else LACQUER[3]
            else:
                if edge or (x + y) % 4:
                    continue
                c = (255, 250, 220)
            img.putpixel((x, y), c + (255,))
    return img


def preview(out):
    """A sheet of every sprite here at 8x, for looking at them: python3 tools/ores_art.py <png>."""
    from PIL import Image
    sprites = [f(16) for f in _ITEMS.values()] + [it_matriarch(16, p) for p in ("helmet", "chestplate", "leggings", "boots")]
    sprites += [f(16) for f in _BLOCKS.values()] + [bl_sprout(16, i) for i in range(4)] + list(cradle_materials(16).values())
    cols = 10
    rows = (len(sprites) + cols - 1) // cols
    S = 8
    img = Image.new("RGBA", (cols * 17 * S, rows * 17 * S), (52, 54, 60, 255))
    for i, s in enumerate(sprites):
        im = s.image().resize((16 * S, 16 * S), Image.NEAREST)
        img.alpha_composite(im, ((i % cols) * 17 * S, (i // cols) * 17 * S))
    img.save(out)


if __name__ == "__main__":
    import sys
    preview(sys.argv[1] if len(sys.argv) > 1 else "ores_preview.png")
