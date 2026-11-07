"""The world blocks of Matriochka, painted the way Minecraft's own blocks are: a few hard tones per material, clusters
instead of noise, light from the top left, and a shape for every material (courses of brick, grains of sand, blades of
moss, the facets of an ore, the frame of a lamp). Every texture tiles on all four sides.

paint(style, pal, block_id, path): the world's palette (primary, secondary, accent, dark) gives the ramp; the block's
id picks its own pattern within the style (rootstone has roots, ashrock columns, cloudstone puffs...).
"""
import math

from PIL import Image

from paint import hx, mix, rng

N = 16
GOLD, GOLD_D, RED, RED_D, RED_L = hx("e8b850"), hx("9a6a20"), hx("a8231a"), hx("5a1210"), hx("d24a32")


def ramp(base, n=5, lo=0.55, hi=1.25):
    """n tones of one colour, dark to light, the dark ones a little cooler and the light ones a little warmer."""
    out = []
    for i in range(n):
        f = lo + (hi - lo) * i / (n - 1)
        if f < 1:
            c = mix((12, 10, 22), base, f)
        else:
            c = mix(base, (255, 246, 226), (f - 1) * 0.9)
        out.append(c)
    return out


class Tex:
    def __init__(self):
        self.px = [[(0, 0, 0, 0)] * N for _ in range(N)]

    def set(self, x, y, c, a=255):
        self.px[y % N][x % N] = (c[0], c[1], c[2], a)

    def get(self, x, y):
        return self.px[y % N][x % N]

    def fill(self, c):
        for y in range(N):
            for x in range(N):
                self.set(x, y, c)

    def save(self, path):
        im = Image.new("RGBA", (N, N))
        for y in range(N):
            for x in range(N):
                im.putpixel((x, y), self.px[y][x])
        im.save(path)


def wrapd(x0, y0, x1, y1):
    dx = min(abs(x0 - x1), N - abs(x0 - x1))
    dy = min(abs(y0 - y1), N - abs(y0 - y1))
    return math.hypot(dx, dy)


def field(r, blobs=10, rmin=1.5, rmax=3.6):
    """A tileable height field of soft blobs: 0..1 per pixel."""
    pts = [(r.uniform(0, N), r.uniform(0, N), r.uniform(rmin, rmax), r.uniform(-1, 1)) for _ in range(blobs)]
    f = [[0.0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            v = 0
            for (bx, by, br, bs) in pts:
                d = wrapd(x + 0.5, y + 0.5, bx, by)
                if d < br:
                    v += bs * (1 - d / br) ** 2
            f[y][x] = v
    lo = min(min(row) for row in f)
    hi = max(max(row) for row in f)
    return [[(v - lo) / (hi - lo + 1e-9) for v in row] for row in f]


def stone_base(t, r, tones, blobs=11, speck=0.03, emboss=True):
    """Clustered stone: the field cut into the ramp's tones, its bumps lit on top-left, a few pits."""
    f = field(r, blobs)
    k = len(tones)
    for y in range(N):
        for x in range(N):
            i = min(k - 1, int(f[y][x] * (k - 1) + 0.5 + (r.random() - 0.5) * 0.28))
            t.set(x, y, tones[max(0, min(k - 1, i))])
    if emboss:
        # an edge between a bump and a hollow: lit on the side facing the light, shaded on the other
        for y in range(N):
            for x in range(N):
                here, ul = f[y][x], f[(y - 1) % N][(x - 1) % N]
                if here - ul > 0.22:
                    t.set(x, y, tones[min(k - 1, k - 1)])
                elif ul - here > 0.22:
                    t.set(x, y, tones[0])
    for _ in range(int(N * N * speck)):
        x, y = r.randrange(N), r.randrange(N)
        t.set(x, y, tones[r.choice((0, 1))])


# ------------------------------------------------------------------ materials
def stone(t, r, pal, bid):
    p, s, a, d = pal
    tones = ramp(p, 5, 0.5, 1.18)
    stone_base(t, r, tones)
    if "root" in bid:
        # pale roots threading through the rock
        root = ramp(s, 3, 0.7, 1.15)
        for _ in range(3):
            x, y = r.randrange(N), r.randrange(N)
            for _ in range(r.randint(6, 11)):
                t.set(x, y, root[1])
                t.set(x, y + 1, root[0])
                x += r.choice((-1, 0, 1, 1))
                y += r.choice((0, 1, 1))
    elif "ash" in bid:
        # basalt columns: vertical seams, the top of each column a lighter cap
        for x in (0, 5, 10):
            for y in range(N):
                t.set(x, y, tones[0])
            for y in range(N):
                if r.random() < 0.25:
                    t.set(x + 1, y, tones[3])
        for x in range(N):
            if x % 5:
                t.set(x, 0, tones[4])
    elif "cloud" in bid:
        # puffs: round soft lumps with bright crowns
        for _ in range(5):
            cx, cy, rad = r.uniform(0, N), r.uniform(0, N), r.uniform(2.2, 3.6)
            for y in range(N):
                for x in range(N):
                    dd = wrapd(x + 0.5, y + 0.5, cx, cy)
                    if dd < rad:
                        t.set(x, y, tones[3] if dd < rad - 1 else tones[2])
                        if dd < rad * 0.45 and y + 0.5 < cy:
                            t.set(x, y, tones[4])
    elif "trench" in bid or "hour" in bid:
        # sedimentary bands with a few fossils / sand grains
        band = ramp(a if "hour" in bid else s, 4, 0.6, 1.1)
        for y in range(N):
            if y % 5 == 2:
                for x in range(N):
                    t.set(x, y, band[1] if (x + y) % 3 else band[2])
            if y % 5 == 3:
                for x in range(N):
                    if r.random() < 0.6:
                        t.set(x, y, tones[1])
    elif "living" in bid or "flesh" in bid:
        # veined organic rock
        vein = ramp(a, 3, 0.7, 1.2)
        for _ in range(2):
            x, y = r.randrange(N), r.randrange(N)
            for _ in range(14):
                t.set(x, y, vein[1])
                if r.random() < 0.3:
                    t.set(x + 1, y, vein[2])
                x += r.choice((-1, 1, 1))
                y += r.choice((-1, 0, 1, 1))
    elif "inverted" in bid or "umbral" in bid:
        # faint crystalline flecks of the accent
        for _ in range(7):
            x, y = r.randrange(N), r.randrange(N)
            t.set(x, y, mix(tones[3], a, 0.6))
    return t


def moss(t, r, pal, bid):
    """A living top: a dense carpet of blades over a darker mat, flowers or spores of the accent."""
    p, s, a, d = pal
    base = s if sum(s) > 150 and "spore" not in bid else p
    if "felt" in bid:
        # workshop felt: woven threads in two directions, a darker stitch every fourth row
        tones = ramp(p, 4, 0.7, 1.1)
        for y in range(N):
            for x in range(N):
                t.set(x, y, tones[1 + ((x + (y // 2)) % 2)])
        for y in range(0, N, 4):
            for x in range(N):
                if x % 2 == 0:
                    t.set(x, y, tones[0])
        return t
    tones = ramp(base, 5, 0.5, 1.22)
    stone_base(t, r, tones[:3], blobs=9, speck=0.05, emboss=False)
    # blades: short vertical strokes, light tip, dark root
    for _ in range(46):
        x, y = r.randrange(N), r.randrange(N)
        t.set(x, y, tones[4])
        t.set(x, y + 1, tones[3])
        t.set(x, y + 2, tones[2])
    # flowers / spores of the world's accent
    flower = ramp(a, 3, 0.75, 1.25)
    for _ in range(4 if "spore" in bid or "prism" in bid else 2):
        x, y = r.randrange(N), r.randrange(N)
        t.set(x, y, flower[2])
        t.set(x + 1, y, flower[1])
        t.set(x, y + 1, flower[0])
    if "flesh" in bid:
        for _ in range(8):
            t.set(r.randrange(N), r.randrange(N), mix(tones[1], RED, 0.5))
    return t


def soil(t, r, pal, bid, tilled=False):
    """World Soil: a rich loam of the world's dark tones, roots and pebbles; tilled, furrows across it."""
    p, s, a, d = pal
    tones = ramp(mix(hx("6a4a30"), p, 0.35), 5, 0.5, 1.15)
    stone_base(t, r, tones[:4], blobs=9, speck=0.02, emboss=True)
    peb = ramp(mix(p, (150, 150, 150), 0.4), 3, 0.7, 1.2)
    for _ in range(3):
        x, y = r.randrange(N), r.randrange(N)
        t.set(x, y, peb[2])
        t.set(x + 1, y + 1, peb[0])
    # a few motes of the world's accent: the soil remembers its world
    for _ in range(4):
        t.set(r.randrange(N), r.randrange(N), mix(a, tones[3], 0.3))
    if tilled:
        for y in range(1, N, 4):
            for x in range(N):
                t.set(x, y, tones[0])
                t.set(x, y + 1, tones[4] if x % 3 else tones[3])
    return t


def sand(t, r, pal, bid):
    p, s, a, d = pal
    base = a if "temporal" in bid else mix(p, a, 0.35)
    tones = ramp(base, 4, 0.72, 1.12)
    for y in range(N):
        for x in range(N):
            t.set(x, y, tones[1 + ((x * 7 + y * 3 + r.randint(0, 2)) % 3 == 0)])
    for _ in range(26):
        t.set(r.randrange(N), r.randrange(N), tones[r.choice((0, 3))])
    # ripples
    for k in range(3):
        y0 = r.randrange(N)
        for x in range(N):
            yy = y0 + round(math.sin((x + k * 5) / N * 2 * math.pi) * 1.2)
            t.set(x, yy, tones[3])
            t.set(x, yy + 1, tones[0])
    if "temporal" in bid:
        # grains of time: specks that shine
        for _ in range(4):
            x, y = r.randrange(N), r.randrange(N)
            t.set(x, y, (255, 248, 220))
    return t


def brick(t, r, pal, bid, sealed=False):
    """Courses of brick, 4 high and 8 long, staggered; each brick its own tone, lit on top-left, chipped."""
    p, s, a, d = pal
    tones = ramp(p, 5, 0.5, 1.15)
    mortar = tones[0]
    for row in range(4):
        y0 = row * 4
        off = 0 if row % 2 == 0 else 4
        for b in range(3):
            x0 = (off + b * 8) % N
            tone = r.choice((1, 2, 2, 3))
            for yy in range(y0, y0 + 4):
                for xx in range(x0, x0 + 8):
                    edge_t, edge_l = yy == y0, xx == x0
                    if edge_t or edge_l:
                        t.set(xx, yy, mortar)
                    elif yy == y0 + 1 or xx == x0 + 1:
                        t.set(xx, yy, tones[min(4, tone + 1)])
                    elif yy == y0 + 3 or xx == x0 + 7:
                        t.set(xx, yy, tones[max(0, tone - 1)])
                    else:
                        t.set(xx, yy, tones[tone] if r.random() > 0.1 else tones[tone - 1])
            if r.random() < 0.35:
                t.set(x0 + r.randint(2, 6), y0 + r.randint(1, 2), mortar)
    if sealed:
        # a gold seal pressed into the middle course
        for (x, y) in ((7, 6), (8, 6), (6, 7), (9, 7), (7, 8), (8, 8)):
            t.set(x, y, GOLD)
        t.set(7, 7, GOLD_D)
        t.set(8, 7, a)
    return t


def ore(t, r, pal, bid, big=False):
    """The world's stone with clusters of the ore: each cluster a few facets, outlined dark, one bright glint."""
    p, s, a, d = pal
    stone(t, r, pal, "plain")
    gem = ramp(a, 4, 0.6, 1.3)
    n = 4 if not big else 3
    spots = []
    for _ in range(n * 6):
        cx, cy = r.randrange(1, N - 1), r.randrange(1, N - 1)
        if all(wrapd(cx, cy, x, y) > (4.5 if not big else 6) for (x, y) in spots):
            spots.append((cx, cy))
        if len(spots) >= n:
            break
    for (cx, cy) in spots:
        rad = r.uniform(1.3, 1.9) if not big else r.uniform(2.4, 3.2)
        cells = {(x, y) for x in range(cx - 4, cx + 5) for y in range(cy - 4, cy + 5)
                 if math.hypot(x - cx, (y - cy) * 1.15) <= rad + r.uniform(-0.35, 0.35)}
        # dark rim
        for (x, y) in cells:
            for dx, dy in ((1, 0), (0, 1), (1, 1)):
                if (x + dx, y + dy) not in cells:
                    t.set(x + dx, y + dy, gem[0])
        for (x, y) in cells:
            lit = (x - cx) + (y - cy)
            t.set(x, y, gem[2] if lit <= 0 else gem[1])
        hx_, hy = min(cells, key=lambda c: c[0] + c[1])
        t.set(hx_, hy, gem[3])
    return t


def glow(t, r, pal, bid):
    """Light-giving blocks drawn with hard tones: a glowing heart, never a blur. Each has its own shape."""
    p, s, a, d = pal
    light = ramp(a, 5, 0.6, 1.45)
    dark = ramp(d if sum(d) < 200 else p, 4, 0.5, 1.0)
    if "lamp" in bid or "lacquer" in bid:
        # a lamp in its cage: a frame, bars, a glowing core
        frame = [GOLD_D, GOLD] if "lacquer" in bid else [dark[0], dark[2]]
        t.fill(dark[1])
        for i in range(N):
            for (x, y) in ((i, 0), (i, N - 1), (0, i), (N - 1, i)):
                t.set(x, y, frame[0])
            t.set(i, 1, frame[1])
            t.set(1, i, frame[1])
        for y in range(2, N - 2):
            for x in range(2, N - 2):
                dd = max(abs(x - 7.5), abs(y - 7.5))
                t.set(x, y, light[4] if dd < 2 else light[3] if dd < 3.5 else light[2] if dd < 5 else light[1])
        for x in (5, 10):
            for y in range(2, N - 2):
                t.set(x, y, frame[0] if "lacquer" not in bid else RED_D)
        if "lacquer" in bid:
            for (x, y) in ((7, 3), (8, 3), (7, 12), (8, 12), (3, 7), (3, 8), (12, 7), (12, 8)):
                t.set(x, y, GOLD)
        return t
    if "ember" in bid or "vein" in bid or "pulse" in bid:
        # dark rock split by glowing cracks, brightest where they cross
        stone_base(t, r, ramp(d if sum(d) < 260 else p, 4, 0.45, 0.95), blobs=10, emboss=True)
        for _ in range(2):
            x, y = r.randrange(N), r.randrange(N)
            dx = r.choice((-1, 1))
            for step in range(r.randint(18, 26)):
                t.set(x, y, light[3])
                t.set(x, y + 1, light[1])
                if step % 6 == 3:
                    # a short branch
                    bx, by = x, y
                    for _ in range(3):
                        bx -= dx
                        by += 1
                        t.set(bx, by, light[2])
                x += dx if r.random() < 0.7 else 0
                y += r.choice((0, 1)) if r.random() < 0.6 else -1
        for _ in range(4):
            t.set(r.randrange(N), r.randrange(N), light[4])
        return t
    if "bloom" in bid:
        # a mat of spore moss with glowing bulbs: each bulb a 2x2 of light with a bright crown and a dark stalk
        stone_base(t, r, ramp(s if sum(s) > 120 else p, 3, 0.45, 0.85), blobs=8, emboss=False)
        spots = []
        while len(spots) < 5:
            x, y = r.randrange(N), r.randrange(N)
            if all(wrapd(x, y, a2, b2) > 4 for a2, b2 in spots):
                spots.append((x, y))
        for (x, y) in spots:
            t.set(x, y + 2, dark[0])
            for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                t.set(x + dx, y + dy, light[2])
            t.set(x, y, light[4])
            t.set(x + 1, y + 1, light[1])
            t.set(x - 1, y + 1, light[0])
        return t
    if "coral" in bid:
        # branching coral: dark ground, three little trees of light, forked, with bright tips
        stone_base(t, r, dark[:3], blobs=8, emboss=False)
        for k in range(3):
            x, y = 2 + k * 5 + r.randint(0, 1), N - 1
            for h in range(r.randint(7, 10)):
                t.set(x, y, light[1])
                t.set(x + 1, y, light[0])
                if h in (3, 6):
                    side = 1 if h == 3 else -1
                    for j in range(1, 3):
                        t.set(x + side * j, y - j, light[2])
                    t.set(x + side * 3, y - 3, light[4])
                y -= 1
            t.set(x, y, light[4])
            t.set(x, y + 1, light[3])
        return t
    if "glass" in bid or "storm" in bid:
        # storm glass: a pale pane, a lightning fork caught inside
        for y in range(N):
            for x in range(N):
                t.set(x, y, mix(light[1], (230, 240, 255), 0.35), 170)
        for i in range(N):
            for (x, y) in ((i, 0), (i, N - 1), (0, i), (N - 1, i)):
                t.set(x, y, dark[2])
        x = 9
        for y in range(2, 14):
            t.set(x, y, (255, 255, 240))
            t.set(x + 1, y, light[3], 230)
            x += r.choice((-1, -1, 0, 1)) if y % 2 else 0
        return t
    # faint glow and the rest: a stone of glowing pores
    stone_base(t, r, ramp(p, 4, 0.45, 0.95), blobs=10)
    for _ in range(12):
        x, y = r.randrange(N), r.randrange(N)
        t.set(x, y, light[4])
        t.set(x + 1, y, light[2])
        t.set(x, y + 1, light[2])
        t.set(x + 1, y + 1, light[0])
    return t


def wood(t, r, pal, bid):
    """Planks: four boards, grain along them, dark seams, a nail at the ends; painted wood gets a folk rosette."""
    p, s, a, d = pal
    painted = "painted" in bid
    base = hx("b07848") if not painted else hx("c2884e")
    if "giant" in bid:
        base = mix(base, p, 0.25)
    tones = ramp(base, 5, 0.55, 1.15)
    for board in range(4):
        y0 = board * 4
        shift = r.randrange(N)
        tone = r.choice((2, 2, 3))
        for yy in range(y0, y0 + 4):
            for x in range(N):
                g = math.sin((x + shift) * 0.7 + yy * 1.3)
                c = tones[tone + (1 if g > 0.7 else 0) - (1 if g < -0.8 else 0)]
                t.set(x, yy, c)
            t.set(r.randrange(N), yy, tones[tone - 1])
        for x in range(N):
            t.set(x, y0, tones[0])
            t.set(x, y0 + 1, tones[min(4, tone + 1)])
        t.set((shift + 1) % N, y0 + 2, tones[0])
    if painted:
        # a red and gold khokhloma berry with two leaves, painted on the boards
        for (x, y) in ((7, 6), (8, 6), (7, 7), (8, 7), (6, 8), (9, 8)):
            t.set(x, y, RED)
        t.set(7, 6, RED_L)
        for (x, y) in ((5, 9), (4, 10), (10, 9), (11, 10), (7, 9), (8, 10)):
            t.set(x, y, GOLD)
        t.set(4, 9, hx("2c4a1c"))
        t.set(11, 9, hx("2c4a1c"))
    return t


def lacquer(t, r, pal, bid):
    """Red lacquer with gold leaf: khokhloma curls and berries around a central flower, on a deep glossy red."""
    reds = ramp(RED, 5, 0.55, 1.2)
    for y in range(N):
        for x in range(N):
            gloss = (x + y) % 9 == 0 and x < 8
            t.set(x, y, reds[3] if gloss else reds[1 + ((x * 3 + y * 5) % 7 == 0)])
    # gold border
    for i in range(N):
        for (x, y) in ((i, 0), (i, N - 1), (0, i), (N - 1, i)):
            t.set(x, y, GOLD_D)
        if i % 2 == 0:
            for (x, y) in ((i, 1), (i, N - 2), (1, i), (N - 2, i)):
                t.set(x, y, GOLD)
    # the central flower: four gold petals round a red heart
    for (x, y) in ((7, 4), (8, 4), (4, 7), (4, 8), (11, 7), (11, 8), (7, 11), (8, 11),
                   (6, 5), (9, 5), (5, 6), (10, 6), (5, 9), (10, 9), (6, 10), (9, 10)):
        t.set(x, y, GOLD)
    for (x, y) in ((7, 7), (8, 7), (7, 8), (8, 8)):
        t.set(x, y, reds[4])
    t.set(7, 7, (255, 220, 190))
    # curls in the corners
    for (cx, cy) in ((3, 3), (12, 3), (3, 12), (12, 12)):
        t.set(cx, cy, GOLD)
        t.set(cx + (1 if cx < 8 else -1), cy, GOLD_D)
    if "world_block" in bid or "threshold" in bid:
        for (x, y) in ((7, 2), (8, 2), (2, 7), (2, 8), (13, 7), (13, 8), (7, 13), (8, 13)):
            t.set(x, y, mix(GOLD, pal[2], 0.5))
    return t


def rune(t, r, pal, bid):
    """Carved temple stone: dressed slabs with a rune channel that glows cold blue."""
    tones = ramp(hx("70707a"), 5, 0.5, 1.15)
    stone_base(t, r, tones[1:4], blobs=8, emboss=True)
    for i in range(N):
        t.set(i, 0, tones[0])
        t.set(0, i, tones[0])
        t.set(i, 1, tones[4])
        t.set(1, i, tones[4])
    glowc = ramp(hx("7fd3ff"), 3, 0.7, 1.3)
    for (x, y) in [(8 + dx, 8 + dy) for dx in range(-4, 5) for dy in range(-4, 5) if abs(dx) + abs(dy) == 4]:
        t.set(x, y, glowc[1])
        t.set(x + 1, y + 1, tones[0])
    t.set(8, 8, glowc[2])
    return t


STYLES = {"stone": stone, "moss": moss, "sand": sand, "ore": ore, "glow": glow, "wood": wood, "lacquer": lacquer,
          "stone_rune": rune}


def paint(style, pal, bid, path, tilled=False):
    """Paints a block in the new style; returns False for the styles kept by paint.py (stations, specials)."""
    pals = [hx(x) for x in pal]
    r = rng("v2" + bid + style + ("t" if tilled else ""))
    t = Tex()
    if style == "soil":
        soil(t, r, pals, bid, tilled)
    elif style == "brick":
        brick(t, r, pals, bid)
    elif style == "brick_unbreakable":
        brick(t, r, pals, bid, sealed=True)
    elif style == "ore_big":
        ore(t, r, pals, bid, big=True)
    elif style in STYLES:
        STYLES[style](t, r, pals, bid)
    else:
        return False
    t.save(path)
    return True
