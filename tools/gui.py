"""GUI art for Matriochka: lacquered wood, gold leaf, khokhloma painting, parchment, ribbons and dolls.

Every sprite is painted at S texels per GUI pixel (S = 2), so details stay crisp at the usual GUI scales: at GUI
scale 2 a texel is one screen pixel, at scale 4 it is a clean 2x2 block. Nine-slice sprites declare their logical
size in the .mcmeta, the texture itself is S times larger. Centres and edges of nine-slice sprites are painted
with noise that is periodic over exactly one tile, so tiling never shows a seam.

    python3 tools/gui.py              writes src/main/resources/assets/matriochka/textures/gui/sprites
    python3 tools/gui.py --preview D  also writes contact sheets of every sprite into directory D
"""
import json
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import WORLDS, STATIONS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "src/main/resources/assets/matriochka/textures/gui/sprites")
S = 2
SAVED = []


# =================================================================== maths and noise
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def smooth(t):
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    t = clamp(t)
    return (int(a[0] + (b[0] - a[0]) * t + .5), int(a[1] + (b[1] - a[1]) * t + .5), int(a[2] + (b[2] - a[2]) * t + .5))


def ramp(stops, t):
    t = clamp(t)
    p = t * (len(stops) - 1)
    i = min(int(p), len(stops) - 2)
    return mix(stops[i], stops[i + 1], p - i)


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def scale_c(c, f):
    return tuple(int(clamp(v * f, 0, 255)) for v in c)


def _h(ix, iy, seed):
    n = (ix * 374761393 + iy * 668265263 + seed * 2246822519 + 97) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffffff) / 0xffffff


def vnoise(x, y, seed=0, px=0, py=0):
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = smooth(x - ix), smooth(y - iy)

    def g(a, b):
        if px:
            a %= px
        if py:
            b %= py
        return _h(a, b, seed)

    a = g(ix, iy) + (g(ix + 1, iy) - g(ix, iy)) * fx
    b = g(ix, iy + 1) + (g(ix + 1, iy + 1) - g(ix, iy + 1)) * fx
    return a + (b - a) * fy


def fbm(x, y, seed=0, octaves=4, px=0, py=0):
    s, amp, f, tot = 0.0, 0.5, 1, 0.0
    for o in range(octaves):
        s += amp * vnoise(x * f, y * f, seed + o * 31, px * f, py * f)
        tot += amp
        amp *= 0.5
        f *= 2
    return s / tot


# =================================================================== palette
INK = (52, 30, 18)
OUTLINE = (20, 11, 8)
GOLD = [(46, 26, 8), (96, 60, 18), (150, 104, 34), (198, 150, 58), (228, 188, 98), (248, 222, 150), (255, 244, 208)]
RED = [(50, 6, 6), (96, 14, 12), (140, 24, 20), (176, 38, 28), (206, 70, 48), (236, 132, 98)]
BLACK = [(7, 5, 5), (15, 10, 9), (24, 17, 14), (36, 26, 21), (58, 44, 36), (96, 78, 66)]
WOOD = [(52, 28, 14), (88, 52, 26), (124, 78, 40), (156, 104, 56), (190, 138, 80), (222, 176, 116)]
PAPER = [(150, 112, 70), (194, 160, 112), (220, 194, 148), (234, 214, 174), (244, 230, 198), (250, 242, 220)]
BERRY = [(54, 4, 4), (120, 12, 10), (178, 26, 18), (222, 52, 34), (250, 120, 90), (255, 214, 196)]
LEAF_G = [(10, 22, 10), (26, 50, 20), (48, 82, 32), (82, 120, 46), (130, 162, 70)]
SKIN = (246, 214, 182)
BOLE = (128, 44, 26)


def world_style(w):
    """Accent colours for a world's station: accent (bright), second, enamel (dark plate), leaf and berry ramps."""
    if w == 0:
        return dict(accent=(214, 58, 40), second=(232, 190, 98), enamel=(92, 14, 12), liquid=(222, 52, 34),
                    leaf=GOLD[2:6], berry=BERRY)
    pal = [hx(c) for c in WORLDS[w - 1]["pal"]]
    base, second, bright, dark = pal
    custom = {
        1: dict(accent=bright, second=second, enamel=(30, 52, 22), liquid=(150, 214, 60)),
        2: dict(accent=(240, 120, 40), second=bright, enamel=(84, 26, 10), liquid=(255, 140, 40)),
        3: dict(accent=bright, second=(150, 156, 170), enamel=(34, 38, 50), liquid=(127, 211, 255)),
        4: dict(accent=bright, second=second, enamel=(22, 48, 104), liquid=(255, 225, 74)),
        5: dict(accent=bright, second=(60, 80, 160), enamel=(14, 18, 46), liquid=(106, 138, 255)),
        6: dict(accent=base, second=second, enamel=(64, 18, 84), liquid=(200, 74, 216)),
        7: dict(accent=second, second=bright, enamel=(6, 44, 64), liquid=(60, 200, 210)),
        8: dict(accent=second, second=base, enamel=(78, 44, 14), liquid=(232, 140, 50)),
        9: dict(accent=bright, second=second, enamel=(78, 30, 20), liquid=(232, 160, 112)),
        10: dict(accent=(214, 66, 44), second=(80, 120, 200), enamel=(96, 22, 16), liquid=(232, 192, 112)),
    }[w]
    c = custom
    c["leaf"] = [scale_c(c["second"], 0.35), scale_c(c["second"], 0.6), c["second"], mix(c["second"], (255, 255, 255), 0.35)]
    c["berry"] = [scale_c(c["accent"], 0.22), scale_c(c["accent"], 0.5), scale_c(c["accent"], 0.78), c["accent"],
                  mix(c["accent"], (255, 255, 255), 0.4), mix(c["accent"], (255, 255, 255), 0.8)]
    return c


# =================================================================== canvas
class Cv:
    def __init__(self, w, h, fill=None):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (fill + (255,)) if fill else (0, 0, 0, 0))
        self.p = self.im.load()

    def ok(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, c, a=1.0):
        x, y = int(x), int(y)
        if a <= 0 or not (0 <= x < self.w and 0 <= y < self.h):
            return
        if a >= 1:
            self.p[x, y] = (c[0], c[1], c[2], 255)
            return
        r, g, b, da = self.p[x, y]
        da /= 255.0
        oa = a + da * (1 - a)
        k = da * (1 - a)
        self.p[x, y] = (int((c[0] * a + r * k) / oa + .5), int((c[1] * a + g * k) / oa + .5),
                        int((c[2] * a + b * k) / oa + .5), int(oa * 255 + .5))

    def get(self, x, y):
        return self.p[int(x), int(y)]

    def alpha(self, x, y):
        return self.p[x, y][3] if self.ok(x, y) else 0

    def tint(self, x, y, c, a):
        """Blends the colour of an existing pixel toward c, keeping its alpha."""
        if not self.ok(x, y):
            return
        r, g, b, al = self.p[x, y]
        if al == 0:
            return
        m = mix((r, g, b), c, a)
        self.p[x, y] = m + (al,)

    def mul(self, x, y, f):
        if not self.ok(x, y):
            return
        r, g, b, al = self.p[x, y]
        if al:
            self.p[x, y] = (int(clamp(r * f, 0, 255)), int(clamp(g * f, 0, 255)), int(clamp(b * f, 0, 255)), al)

    def layer(self, other, ox=0, oy=0):
        self.im.alpha_composite(other.im, (int(ox), int(oy)))

    def disc(self, cx, cy, r, c, a=1.0):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= r * r:
                    self.put(x, y, c, a)

    def rect(self, x0, y0, x1, y1, c, a=1.0):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)):
                self.put(x, y, c, a)

    def glow(self, cx, cy, r, c, a=1.0, power=2.0):
        for y in range(int(cy - r), int(cy + r + 1)):
            for x in range(int(cx - r), int(cx + r + 1)):
                d = math.hypot(x + .5 - cx, y + .5 - cy) / r
                if d < 1:
                    self.put(x, y, c, a * (1 - d) ** power)


def shape(cv, inside, bbox, color, outline=None, out_a=1.0):
    """Fills every pixel of bbox for which inside(x, y) holds with color(x, y); pixels on the rim get the outline."""
    x0, y0, x1, y1 = [int(v) for v in bbox]
    mask = {}
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if inside(x + .5, y + .5):
                mask[(x, y)] = True
    for (x, y) in mask:
        edge = outline is not None and not all((x + dx, y + dy) in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            cv.put(x, y, outline, out_a)
        else:
            c = color(x, y)
            if c is None:
                continue
            if len(c) == 4:
                cv.put(x, y, c[:3], c[3])
            else:
                cv.put(x, y, c)
    return mask


# =================================================================== brush work
def bez(p0, p1, p2, p3, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pts


def resample(pts, step=0.4):
    out = [pts[0]]
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d == 0:
            continue
        acc += d
        while acc >= step:
            t = 1 - (acc - step) / d
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            acc -= step
    out.append(pts[-1])
    return out


def stroke(cv, pts, r0, r1, col, a=1.0, taper=1.0):
    pts = resample(pts)
    n = max(1, len(pts) - 1)
    for i, (x, y) in enumerate(pts):
        t = (i / n) ** taper
        r = r0 + (r1 - r0) * t
        if r > 0.15:
            cv.disc(x, y, r, col, a)


def tube(cv, pts, r0, r1, ramp_cols, taper=1.0):
    """A painted, rounded stroke: a dark rim, the body, then a highlight that sits toward the light (top left)."""
    dark, mid, light = ramp_cols[0], ramp_cols[len(ramp_cols) // 2], ramp_cols[-1]
    stroke(cv, [(x + .5, y + .7) for x, y in pts], r0 + .6, r1 + .5, dark, 1, taper)
    stroke(cv, pts, r0, r1, mid, 1, taper)
    if r0 > 0.9:
        stroke(cv, [(x - r0 * .35, y - r0 * .4) for x, y in pts], r0 * .42, r1 * .42, light, 1, taper)


def spiral(cx, cy, r, turns=1.2, start=0.0, direction=1, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = start + direction * t * turns * 2 * math.pi
        rr = r * (1 - 0.82 * t)
        pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
    return pts


def curl(cv, x, y, r, ang, direction, cols, width=1.3):
    """A khokhloma 'travka' grass curl: a tapering stroke that winds into a little spiral."""
    sx, sy = x + math.cos(ang) * r * 2.2, y + math.sin(ang) * r * 2.2
    lead = bez((x, y), (x + math.cos(ang) * r, y + math.sin(ang) * r),
               (sx - math.cos(ang + direction * 1.6) * r, sy - math.sin(ang + direction * 1.6) * r), (sx, sy), 20)
    sp = spiral(sx + math.cos(ang + direction * 1.57) * r * .9, sy + math.sin(ang + direction * 1.57) * r * .9, r * .9,
                0.9, ang - direction * 1.57, direction, 40)
    tube(cv, lead + sp, width, 0.2, cols, 1.4)


def leaf(cv, base, tip, width, cols, outline=OUTLINE, vein=None, bend=0.0):
    """A pointed khokhloma leaf from base to tip, shaded across its width, with a midrib."""
    bx, by = base
    tx, ty = tip
    L = math.hypot(tx - bx, ty - by)
    if L < 1:
        return
    ux, uy = (tx - bx) / L, (ty - by) / L
    nx, ny = -uy, ux

    def coords(x, y):
        dx, dy = x - bx, y - by
        t = (dx * ux + dy * uy) / L
        s = dx * nx + dy * ny - bend * L * math.sin(math.pi * clamp(t)) * 0.5
        return t, s

    def half(t):
        return width * (math.sin(math.pi * clamp(t)) ** 0.75) * (1 - 0.35 * t)

    def inside(x, y):
        t, s = coords(x, y)
        return 0 <= t <= 1 and abs(s) <= half(t)

    def color(x, y):
        t, s = coords(x, y)
        h = max(0.01, half(t))
        tone = 0.55 + 0.4 * (s / h) * (1 if nx * -1 + ny * -1 > 0 else -1) - 0.15 * t
        return ramp(cols, tone)

    xs, ys = [bx, tx, bx + nx * width * 1.4, bx - nx * width * 1.4, tx + nx * width, tx - nx * width], \
        [by, ty, by + ny * width * 1.4, by - ny * width * 1.4, ty + ny * width, ty - ny * width]
    shape(cv, inside, (min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2), color, outline)
    if vein is not None:
        pts = [(bx + ux * L * t + nx * bend * L * math.sin(math.pi * t) * 0.5,
                by + uy * L * t + ny * bend * L * math.sin(math.pi * t) * 0.5) for t in [i / 20 for i in range(2, 17)]]
        stroke(cv, pts, 0.5, 0.3, vein)


def berry(cv, cx, cy, r, cols=BERRY, outline=(40, 4, 4)):
    """A rowan berry: lacquer-red sphere with a dark rim, a bright highlight and a black calyx dot."""
    def inside(x, y):
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

    def color(x, y):
        nx, ny = (x + .5 - cx) / r, (y + .5 - cy) / r
        light = clamp(0.62 - 0.45 * nx - 0.5 * ny - 0.15 * (nx * nx + ny * ny))
        return ramp(cols[1:5], light)

    shape(cv, inside, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), color, outline)
    if r >= 2:
        cv.put(cx - r * .42, cy - r * .45, cols[-1])
        if r >= 3.2:
            cv.put(cx - r * .42 + 1, cy - r * .45, cols[-2])
            cv.put(cx - r * .42, cy - r * .45 + 1, cols[-2])
        cv.put(cx + r * .35, cy + r * .4, outline)


def berries(cv, cx, cy, r, n, seed, cols=BERRY):
    pts = [(cx, cy)]
    for i in range(1, n):
        a = i * 2.4 + _h(i, seed, 3) * 0.6
        d = r * (1.5 + 0.4 * _h(i, seed, 4))
        pts.append((cx + math.cos(a) * d, cy + math.sin(a) * d))
    pts.sort(key=lambda p: p[1])
    for (x, y) in pts:
        berry(cv, x, y, r, cols)


def rivet(cv, cx, cy, r, cols=GOLD):
    def inside(x, y):
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

    def color(x, y):
        nx, ny = (x + .5 - cx) / r, (y + .5 - cy) / r
        return ramp(cols[1:], clamp(0.55 - 0.5 * nx - 0.55 * ny))

    shape(cv, inside, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), color, cols[0])
    cv.put(cx - r * .4, cy - r * .45, cols[-1])


def rosette(cv, cx, cy, r, petal=RED, centre=GOLD):
    """A painted rosette: eight petals around a gilded boss."""
    for i in range(8):
        a = i * math.pi / 4
        leaf(cv, (cx + math.cos(a) * r * .25, cy + math.sin(a) * r * .25), (cx + math.cos(a) * r, cy + math.sin(a) * r),
             r * .32, petal[1:5] if i % 2 == 0 else GOLD[2:6], OUTLINE)
    rivet(cv, cx, cy, r * .38, centre)


def star(cv, cx, cy, r, col, a=1.0):
    for i in range(int(-r), int(r) + 1):
        f = 1 - abs(i) / (r + 1)
        cv.put(cx + i, cy, col, a * f)
        cv.put(cx, cy + i, col, a * f)
    cv.put(cx, cy, (255, 255, 240), a)


# =================================================================== materials
def lacquer(cv, x0, y0, x1, y1, cols, seed, grain=0.35, gloss=0.10, px=0, py=0, wood=(84, 46, 22)):
    """Lacquer over carved wood: the grain shows through as warm streaks, a soft sheen crosses the surface."""
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            lx, ly = x - x0, y - y0
            warp = fbm(lx / 48, ly / 12, seed, 3, px // 48 if px else 0, py // 12 if py else 0) * 3.2
            ring = ly / 7.0 + warp
            g = abs((ring % 1.0) - 0.5) * 2
            line = smooth(clamp((g - 0.72) / 0.28))
            fib = fbm(lx / 24, ly / 1.5, seed + 5, 2, px // 24 if px else 0, py * 2 // 3 if py else 0)
            tone = 0.5 + (fib - 0.5) * 0.35
            col = ramp(cols, tone)
            col = mix(col, wood, grain * (0.35 * line + 0.25 * fib))
            if gloss and not px:
                d = ((lx - (x1 - x0) * 0.15) * 0.55 - ly) / ((y1 - y0) * 0.45 + 1)
                col = mix(col, cols[-1], gloss * math.exp(-d * d * 3))
            cv.put(x, y, col)


def gold_tone(x, y, t, seed=7, worn=True):
    t += (fbm(x / 6, y / 6, seed, 2) - 0.5) * 0.16 + (_h(x // 11, y // 11, seed) - 0.5) * 0.07
    c = ramp(GOLD, t)
    if worn and fbm(x / 3.2, y / 3.2, seed + 3, 3) > 0.72:
        c = mix(c, BOLE, 0.55)
    return c


def gilt_frame(cv, x0, y0, x1, y1, bw, seed=3, chase=True, outline=OUTLINE):
    """A carved, gilded moulding around a rectangle (x1/y1 exclusive), lit from the top left."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            dl, dt, dr, db = x - x0, y - y0, x1 - 1 - x, y1 - 1 - y
            d = min(dl, dt, dr, db)
            if d >= bw:
                continue
            side = 1 if min(dl, dt) <= min(dr, db) else -1
            if dl == d and db < bw and db < dl:
                side = -1
            if d == 0:
                cv.put(x, y, outline)
                continue
            if d == bw - 1:
                cv.put(x, y, outline)
                continue
            u = (d - 1) / max(1, bw - 2)
            along = x if d in (dt, db) else y
            if u < 0.34:
                v = u / 0.34
                t = 0.30 + 0.62 * math.sin(math.pi * v) + side * 0.14 * math.cos(math.pi * v)
            elif u < 0.42:
                t = 0.14
            elif u < 0.48:
                t = 0.82
            elif u < 0.78:
                t = 0.55 + side * 0.06
                if chase and abs(u - 0.63) < 0.08 and along % 5 == 0:
                    t = 0.22
            elif u < 0.84:
                t = 0.16
            else:
                v = (u - 0.84) / 0.16
                t = 0.30 + 0.5 * math.sin(math.pi * v) + side * 0.1
            cv.put(x, y, gold_tone(x, y, t, seed, worn=0.42 <= u < 0.78))


def thin_gilt(cv, x0, y0, x1, y1, inset=False):
    """A two-texel gilded fillet: lit edge and shaded edge swap when the rectangle is a recess."""
    for x in range(x0, x1):
        for y, top in ((y0, True), (y1 - 1, False)):
            lit = top != inset
            cv.put(x, y, gold_tone(x, y, 0.78 if lit else 0.3, 11, False))
    for y in range(y0 + 1, y1 - 1):
        for x, left in ((x0, True), (x1 - 1, False)):
            lit = left != inset
            cv.put(x, y, gold_tone(x, y, 0.72 if lit else 0.28, 11, False))


def inner_shadow(cv, x0, y0, x1, y1, depth=6, strength=0.55):
    """The shadow cast inside a recess by its top and left rims."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = min(x - x0, y - y0)
            dd = min(x1 - 1 - x, y1 - 1 - y)
            f = 1.0
            if d < depth:
                f *= 1 - strength * (1 - d / depth) ** 1.6
            if dd < 2:
                f *= 1.12
            cv.mul(x, y, f)


def paper(cv, x0, y0, x1, y1, seed, px=0, py=0, aged=1.0, edge=True, base=PAPER):
    """Parchment: long fibres, a mottled tone, foxing spots and darkened, slightly deckled edges."""
    w, h = x1 - x0, y1 - y0
    for y in range(y0, y1):
        for x in range(x0, x1):
            lx, ly = x - x0, y - y0
            m = fbm(lx / 20, ly / 20, seed, 4, px // 20 if px else 0, py // 20 if py else 0)
            fib = fbm(lx / 14, ly / 1.2, seed + 9, 2, px // 14 if px else 0, int(py / 1.2) if py else 0)
            fib2 = fbm(lx / 1.2, ly / 10, seed + 13, 2, int(px / 1.2) if px else 0, py // 10 if py else 0)
            t = 0.70 + (m - 0.5) * 0.30 + (fib - 0.5) * 0.18 + (fib2 - 0.5) * 0.10
            if _h(lx, ly, seed + 2) > 0.985:
                t -= 0.12
            fox = fbm(lx / 9, ly / 9, seed + 21, 3, px // 9 if px else 0, py // 9 if py else 0)
            col = ramp(base, t)
            if fox > 0.74:
                col = mix(col, (170, 118, 66), (fox - 0.74) * 2.2 * aged)
            if edge:
                d = min(lx, ly, w - 1 - lx, h - 1 - ly)
                if d < 10:
                    col = mix(col, (150, 104, 60), (1 - d / 10) ** 2 * 0.65 * aged)
            cv.put(x, y, col)


def satin(cv, inside, bbox, base, seed, folds=()):
    """Satin ribbon: sheen running along the weave, folds shading across it."""
    x0, y0, x1, y1 = bbox
    w = x1 - x0

    def color(x, y):
        u = (x - x0) / w
        sheen = math.exp(-((u - 0.32) / 0.12) ** 2) * 0.35 - math.exp(-((u - 0.85) / 0.1) ** 2) * 0.18
        t = 0.5 + sheen + (fbm(x / 1.5, y / 30, seed, 2) - 0.5) * 0.12
        for (fy, depth) in folds:
            dd = (y - fy) - (x - x0) * 0.35
            if 0 < dd < 6:
                t -= depth * (1 - dd / 6)
            elif -3 < dd <= 0:
                t += depth * 0.6 * (1 + dd / 3)
        return ramp(base, t)

    return shape(cv, inside, bbox, color, OUTLINE)


# =================================================================== saving
def save(name, cv, border=None, stretch_inner=False):
    """Writes a sprite; with border (logical px) it gets a nine-slice .mcmeta declaring its logical size."""
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    cv.im.save(path)
    meta = path + ".mcmeta"
    if border is not None:
        b = border if isinstance(border, dict) else {"left": border, "top": border, "right": border, "bottom": border}
        ns = {"type": "nine_slice", "width": cv.w // S, "height": cv.h // S, "border": b}
        if stretch_inner:
            ns["stretch_inner"] = True
        with open(meta, "w") as f:
            json.dump({"gui": {"scaling": ns}}, f)
    elif os.path.exists(meta):
        os.remove(meta)
    SAVED.append(name)


# =================================================================== ornaments
def sprig(cv, x, y, length, ang, seed, cols_leaf, cols_berry, direction=1, berries_at_end=True, scale=1.0,
          leaf_dark=False):
    """A khokhloma sprig: a gold stem bending from (x, y), alternating leaves, grass curls and a berry cluster."""
    ex, ey = x + math.cos(ang) * length, y + math.sin(ang) * length
    bend = direction * length * 0.35
    c1 = (x + math.cos(ang) * length * .3 - math.sin(ang) * bend, y + math.sin(ang) * length * .3 + math.cos(ang) * bend)
    c2 = (x + math.cos(ang) * length * .7 + math.sin(ang) * bend * .6, y + math.sin(ang) * length * .7 - math.cos(ang) * bend * .6)
    stem = bez((x, y), c1, c2, (ex, ey), 60)
    tube(cv, stem, 1.4 * scale, 0.7 * scale, GOLD[1:6])
    n = max(2, int(length / (11 * scale)))
    for i in range(1, n):
        t = i / n
        k = int(t * (len(stem) - 1))
        px_, py_ = stem[k]
        qx, qy = stem[min(len(stem) - 1, k + 2)]
        a = math.atan2(qy - py_, qx - px_)
        side = 1 if i % 2 else -1
        la = a + side * 0.9
        ll = (15 + 6 * _h(i, seed, 1)) * scale * (1 - 0.3 * t)
        if _h(i, seed, 2) < 0.3:
            curl(cv, px_, py_, 3.0 * scale, la, side, GOLD[1:6], 1.1 * scale)
        elif _h(i, seed, 6) < 0.2 and i > 1:
            tube(cv, bez((px_, py_), (px_ + math.cos(la) * ll * .4, py_ + math.sin(la) * ll * .4),
                         (px_ + math.cos(la) * ll * .7, py_ + math.sin(la) * ll * .7), (px_ + math.cos(la) * ll * .8, py_ + math.sin(la) * ll * .8), 16),
                 1.0 * scale, 0.6 * scale, GOLD[1:6])
            berries(cv, px_ + math.cos(la) * ll * .85, py_ + math.sin(la) * ll * .85, 2.6 * scale, 3, seed + i, cols_berry)
        else:
            cols = cols_leaf if not (leaf_dark and i % 3 == 0) else RED[1:5]
            leaf(cv, (px_, py_), (px_ + math.cos(la) * ll, py_ + math.sin(la) * ll), ll * 0.33, cols, OUTLINE,
                 vein=GOLD[5] if cols is not cols_leaf else scale_c(cols[0], 1.0), bend=0.12 * side)
    if berries_at_end:
        berries(cv, ex, ey, 3.0 * scale, 5, seed, cols_berry)
    return stem


def flame(cv, cx, by, w, h, seed, cols=((90, 10, 4), (200, 50, 14), (250, 140, 30), (255, 220, 110), (255, 250, 220))):
    """A lick of flame rising from (cx, by)."""
    def inside(x, y):
        t = (by - y) / h
        if t < 0 or t > 1:
            return False
        sway = math.sin(t * 3.2 + seed) * w * 0.25 * t
        hw = w * 0.5 * (math.sin(math.pi * (t * 0.85 + 0.15)) ** 0.8) * (1 - t) ** 0.4
        return abs(x - cx - sway) <= hw

    def color(x, y):
        t = (by - y) / h
        sway = math.sin(t * 3.2 + seed) * w * 0.25 * t
        hw = max(0.5, w * 0.5 * (math.sin(math.pi * (t * 0.85 + 0.15)) ** 0.8) * (1 - t) ** 0.4)
        core = 1 - abs(x - cx - sway) / hw
        return ramp(list(cols), clamp(0.25 + core * 0.7 - t * 0.35))

    shape(cv, inside, (cx - w, by - h - 1, cx + w, by + 1), color, scale_c(cols[0], 0.8))


def bolt(cv, pts, col=(255, 225, 74), edge=(120, 80, 10)):
    for a, b in zip(pts, pts[1:]):
        stroke(cv, [a, b], 1.8, 1.2, edge)
    for a, b in zip(pts, pts[1:]):
        stroke(cv, [a, b], 1.0, 0.6, col)
    for a, b in zip(pts, pts[1:]):
        stroke(cv, [a, b], 0.4, 0.3, (255, 255, 230))


def key_shape(cv, x, y, s, cols=GOLD):
    """A hanging key: ring bow, shaft and a toothed bit."""
    for a in range(0, 360, 6):
        r = math.radians(a)
        cv.disc(x + math.cos(r) * 3.2 * s, y + math.sin(r) * 3.2 * s, 1.1 * s, cols[2])
    for a in range(200, 340, 8):
        r = math.radians(a)
        cv.put(x + math.cos(r) * 3.2 * s, y + math.sin(r) * 3.2 * s, cols[5])
    tube(cv, [(x, y + 3.5 * s), (x, y + 14 * s)], 1.1 * s, 1.0 * s, cols[1:6])
    cv.rect(x + 1, y + 10 * s, x + 4 * s, y + 11.5 * s, cols[3])
    cv.rect(x + 1, y + 12.5 * s, x + 3.3 * s, y + 14 * s, cols[3])


def chain(cv, x, y0, y1, cols=((40, 42, 48), (90, 94, 104), (150, 156, 168), (210, 216, 226))):
    y = y0
    i = 0
    while y < y1:
        if i % 2 == 0:
            for a in range(0, 360, 10):
                r = math.radians(a)
                cv.put(x + math.cos(r) * 1.8, y + 3 + math.sin(r) * 3.2, cols[1 if a < 180 else 2])
        else:
            cv.rect(x - 0.6, y + 0.5, x + 0.8, y + 5.5, cols[3])
        y += 5
        i += 1


def cloud_curl(cv, cx, cy, r, cols):
    for i, (dx, dy, rr) in enumerate(((-1.1, 0.3, .7), (0, -0.2, 1), (1.1, 0.35, .75), (0.3, 0.6, .7))):
        cv.disc(cx + dx * r + .7, cy + dy * r + .8, rr * r, cols[0])
    for i, (dx, dy, rr) in enumerate(((-1.1, 0.3, .7), (0, -0.2, 1), (1.1, 0.35, .75), (0.3, 0.6, .7))):
        cv.disc(cx + dx * r, cy + dy * r, rr * r, cols[2])
        cv.disc(cx + dx * r - rr * r * .3, cy + dy * r - rr * r * .35, rr * r * .45, cols[3])
    tube(cv, spiral(cx - r * .2, cy - r * .1, r * .55, 1.0, 0, 1), 0.6, 0.2, (cols[0], cols[1], cols[1]))


def moon(cv, cx, cy, r, cols):
    def inside(x, y):
        return (x - cx) ** 2 + (y - cy) ** 2 <= r * r and (x - cx - r * .45) ** 2 + (y - cy + r * .2) ** 2 > (r * .8) ** 2

    shape(cv, inside, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1),
          lambda x, y: ramp(cols, clamp(0.8 - (x - cx + r) / (2 * r) * 0.6)), OUTLINE)


def bubble(cv, cx, cy, r, col):
    for a in range(0, 360, 4):
        rr = math.radians(a)
        cv.put(cx + math.cos(rr) * r, cy + math.sin(rr) * r, col, 0.9)
    cv.put(cx - r * .45, cy - r * .45, (255, 255, 255))
    for a in range(0, 360, 6):
        rr = math.radians(a)
        for k in range(int(r)):
            cv.put(cx + math.cos(rr) * k, cy + math.sin(rr) * k, col, 0.04)


def wave(cv, x0, x1, y, amp, cols, phase=0.0):
    pts = [(x, y + math.sin((x - x0) / 7 + phase) * amp) for x in range(int(x0), int(x1))]
    tube(cv, pts, 1.2, 1.0, cols)
    for k in range(int(x0) + 4, int(x1) - 4, 14):
        kk = k - int(x0)
        if 0 <= kk < len(pts):
            px_, py_ = pts[kk]
            tube(cv, spiral(px_ + 2, py_ - 3, 3, 0.9, math.pi / 2, -1), 0.8, 0.2, cols)


def spindle(cv, cx, cy, h, cols_wood=WOOD, thread=(220, 60, 40)):
    """A spinning spindle wrapped in a thread cop."""
    def inside(x, y):
        t = (y - (cy - h / 2)) / h
        if t < 0 or t > 1:
            return False
        hw = 1.2 + 4.5 * math.sin(math.pi * clamp((t - 0.2) / 0.6)) if 0.2 < t < 0.8 else 1.0
        return abs(x - cx) <= hw

    def color(x, y):
        t = (y - (cy - h / 2)) / h
        if 0.25 < t < 0.75:
            stripe = (int(y * 1.3 + x * .4) % 3 == 0)
            base = mix(thread, (255, 255, 255), 0.25) if stripe else thread
            return mix(base, (0, 0, 0), clamp((x - cx) / 10 + 0.15))
        return ramp(cols_wood[2:], clamp(0.6 - (x - cx) / 4))

    shape(cv, inside, (cx - 7, cy - h / 2 - 1, cx + 7, cy + h / 2 + 1), color, OUTLINE)
    rivet(cv, cx, cy + h / 2 - 1, 1.6)


def snowflake(cv, cx, cy, r, col):
    for i in range(6):
        a = i * math.pi / 3
        stroke(cv, [(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], 0.55, 0.4, col)
        mx, my = cx + math.cos(a) * r * .6, cy + math.sin(a) * r * .6
        for s in (-1, 1):
            stroke(cv, [(mx, my), (mx + math.cos(a + s * .8) * r * .3, my + math.sin(a + s * .8) * r * .3)], .45, .3, col)


def rock(cv, cx, cy, r, seed, cols=((40, 22, 16), (90, 50, 36), (140, 84, 60), (190, 130, 96))):
    pts = []
    for i in range(7):
        a = i / 7 * 2 * math.pi
        rr = r * (0.75 + 0.35 * _h(i, seed, 8))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * .8))

    def inside(x, y):
        c = False
        for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1]):
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                c = not c
        return c

    shape(cv, inside, (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2),
          lambda x, y: ramp(list(cols), clamp(0.7 - (x - cx) / r * .3 - (y - cy) / r * .4)), OUTLINE)


def world_motif(cv, x0, y0, x1, y1, w, mirror=False, seed=1):
    """Paints a world's ornament into a tall panel (the wings of a station), mirrored on the right side."""
    st = world_style(w)
    layer = Cv(x1 - x0, y1 - y0)
    W, H = layer.w, layer.h
    lc, bc = st["leaf"], st["berry"]
    cx = W * 0.5
    if w == 0:
        sprig(layer, cx - 6, H - 4, H * 0.62, -math.pi / 2 + 0.25, seed, GOLD[2:6], BERRY, 1, True, 1.1, leaf_dark=True)
        sprig(layer, cx + 4, H - 6, H * 0.4, -math.pi / 2 - 0.5, seed + 1, GOLD[2:6], BERRY, -1, True, 0.9, leaf_dark=True)
        curl(layer, cx + 10, H * 0.3, 3, -1.2, 1, GOLD[1:6])
        berries(layer, cx - 10, H * 0.55, 2.3, 3, seed + 3)
    elif w == 1:
        sprig(layer, cx - 4, H - 4, H * 0.7, -math.pi / 2 + 0.2, seed, lc, bc, 1, True, 1.1)
        for i, (fx, fy, r) in enumerate(((0.3, 0.78, 6), (0.72, 0.62, 4.5))):
            mx_, my_ = W * fx, H * fy
            shape(layer, lambda x, y, a=mx_, b=my_, r=r: (x - a) ** 2 / (r * r) + (y - b) ** 2 / (r * r * .45) <= 1 and y <= b,
                  (mx_ - r - 1, my_ - r, mx_ + r + 1, my_ + 1),
                  lambda x, y, a=mx_, r=r: ramp([(70, 30, 90), (107, 63, 138), (160, 110, 190)], clamp(0.8 - (x - a) / r * .4)), OUTLINE)
            layer.rect(mx_ - 1, my_, mx_ + 2, my_ + r * 1.2, (210, 220, 160))
            for k in range(3):
                layer.put(mx_ - r * .5 + k * r * .5, my_ - r * .4, (220, 255, 140))
        for i in range(9):
            layer.glow(W * _h(i, seed, 1), H * _h(i, seed, 2) * 0.8, 2.5, (183, 224, 74), 0.8)
    elif w == 2:
        sprig(layer, cx - 4, H - 4, H * 0.5, -math.pi / 2 + 0.3, seed, GOLD[2:6], bc, 1, False, 1.0)
        for i, (fx, fy, fw, fh) in enumerate(((0.5, 1.0, 26, 72), (0.24, 1.0, 15, 42), (0.78, 1.0, 16, 50))):
            flame(layer, W * fx, H - 2, fw, fh, i * 1.7)
        for i in range(4):
            gx, gy = W * (0.2 + 0.6 * _h(i, seed, 5)), H * (0.25 + 0.3 * i / 4)
            shape(layer, lambda x, y, a=gx, b=gy: abs(x - a) * 1.6 + abs(y - b) <= 4.5, (gx - 4, gy - 5, gx + 4, gy + 5),
                  lambda x, y, a=gx: ramp([(140, 50, 10), (240, 120, 40), (255, 200, 120)], clamp(0.7 - (x - a) / 4)), OUTLINE)
        berries(layer, W * 0.3, H * 0.15, 2.2, 3, seed + 4, bc)
    elif w == 3:
        chain(layer, W * 0.62, 0, H * 0.55)
        key_shape(layer, W * 0.62, H * 0.55 + 3, 1.4)
        sprig(layer, W * 0.3, H - 4, H * 0.6, -math.pi / 2 + 0.15, seed, GOLD[2:6], bc, -1, True, 1.0)
        chain(layer, W * 0.2, 0, H * 0.25)
    elif w == 4:
        cloud_curl(layer, W * 0.5, H * 0.16, 10, [(30, 50, 90), (90, 130, 190), (200, 220, 245), (250, 252, 255)])
        bolt(layer, [(W * .58, H * .25), (W * .3, H * .44), (W * .66, H * .47), (W * .3, H * .72)])
        sprig(layer, cx, H - 4, H * 0.35, -math.pi / 2 - 0.3, seed, lc, bc, 1, True, 0.9)
        cloud_curl(layer, W * 0.32, H * 0.84, 8, [(30, 50, 90), (90, 130, 190), (200, 220, 245), (250, 252, 255)])
    elif w == 5:
        moon(layer, W * 0.55, H * 0.17, 14, [(60, 80, 160), (130, 160, 255), (220, 230, 255)])
        for i in range(10):
            star(layer, W * (0.1 + 0.8 * _h(i, seed, 1)), H * (0.05 + 0.9 * _h(i, seed, 2)), 2.5 + 3 * _h(i, seed, 3), (170, 190, 255))
        sprig(layer, cx - 4, H - 4, H * 0.55, -math.pi / 2 + 0.2, seed, lc, bc, 1, True, 1.0)
    elif w == 6:
        stem = sprig(layer, cx + 2, 4, H * 0.7, math.pi / 2 - 0.2, seed, lc, bc, -1, True, 1.1)
        sprig(layer, cx - 6, 8, H * 0.38, math.pi / 2 + 0.5, seed + 1, GOLD[2:6], bc, 1, True, 0.85)
        for i in range(5):
            layer.disc(W * (0.15 + 0.7 * _h(i, seed, 7)), H * (0.6 + 0.35 * _h(i, seed, 8)), 1.2, (74, 216, 200))
    elif w == 7:
        for i in range(3):
            sx_ = W * (0.25 + 0.3 * i)
            pts = [(sx_ + math.sin(t / 6 + i) * 3, H - 2 - t) for t in range(0, int(H * (0.45 + 0.15 * i)), 2)]
            tube(layer, pts, 1.6, 0.4, [(10, 50, 40), (30, 110, 80), (80, 170, 120)], 1.0)
            for k in range(2, len(pts) - 2, 6):
                leaf(layer, pts[k], (pts[k][0] + (5 if k % 12 else -5), pts[k][1] - 4), 1.6,
                     [(10, 50, 40), (30, 110, 80), (80, 170, 120), (140, 220, 170)], OUTLINE)
        for i in range(8):
            bubble(layer, W * (0.1 + 0.8 * _h(i, seed, 4)), H * (0.08 + 0.5 * _h(i, seed, 5)), 1.5 + 2.5 * _h(i, seed, 6), (154, 240, 255))
        wave(layer, 2, W - 2, H * 0.62, 2, [(10, 60, 80), (26, 176, 176), (154, 240, 255)])
    elif w == 8:
        stem = bez((cx, H - 4), (cx - 14, H * .7), (cx + 14, H * .4), (cx - 2, H * .1), 60)
        tube(layer, stem, 1.6, 0.8, WOOD[1:6])
        seasons = [[(120, 30, 60), (220, 110, 150), (250, 200, 220), (255, 240, 245)],
                   [(20, 60, 20), (60, 130, 40), (130, 190, 70), (190, 230, 120)],
                   [(110, 40, 10), (216, 106, 42), (240, 170, 70), (255, 220, 140)],
                   [(70, 90, 120), (170, 190, 220), (230, 240, 255), (255, 255, 255)]]
        for i in range(8):
            k = int((0.15 + 0.8 * i / 8) * (len(stem) - 1))
            px_, py_ = stem[k]
            side = 1 if i % 2 else -1
            cols = seasons[3 - min(3, i // 2)]
            if i // 2 == 0:
                snowflake(layer, px_ + side * 7, py_, 3.4, (230, 240, 255))
            else:
                leaf(layer, (px_, py_), (px_ + side * 11, py_ - 4), 3.2, cols, OUTLINE, vein=cols[0], bend=0.2 * side)
        for i in range(3):
            layer.disc(stem[-1][0] + (i - 1) * 3.5, stem[-1][1] - 2 + abs(i - 1) * 2, 2.4, (240, 160, 190))
        layer.disc(stem[-1][0], stem[-1][1] - 1, 1.4, (255, 230, 120))
    elif w == 9:
        for i, fy in enumerate((0.55, 0.7, 0.85)):
            col = [(70, 34, 22), (106, 58, 42), (168, 74, 58)][i]
            for x in range(W):
                yy = H * fy + math.sin(x / 6 + i) * 2
                for y in range(int(yy), int(yy + 2)):
                    layer.put(x, y, col, 0.9)
        crack = [(W * .5, H * .4)]
        for i in range(8):
            px_, py_ = crack[-1]
            crack.append((px_ + (_h(i, seed, 9) - 0.5) * 10, py_ + H * 0.07))
        stroke(layer, crack, 1.2, 0.4, OUTLINE)
        stroke(layer, [(x + 1, y) for x, y in crack], 0.4, 0.3, (232, 160, 112))
        for i in range(4):
            rock(layer, W * (0.2 + 0.6 * _h(i, seed, 2)), H * (0.6 + 0.3 * _h(i, seed, 3)), 4 + 2 * _h(i, seed, 4), seed + i)
        sprig(layer, cx, H * 0.45, H * 0.4, -math.pi / 2 - 0.2, seed, lc, bc, 1, True, 0.9)
    elif w == 10:
        spindle(layer, W * 0.5, H * 0.4, 46)
        pts = bez((W * .5, H * .62), (W * .9, H * .7), (W * .1, H * .82), (W * .55, H - 4), 50)
        stroke(layer, pts, 0.7, 0.6, (220, 60, 40))
        pts = bez((W * .5, H * .2), (W * .1, H * .12), (W * .9, H * .05), (W * .3, 2), 50)
        stroke(layer, pts, 0.7, 0.6, (80, 120, 200))
        sprig(layer, W * .25, H - 4, H * 0.3, -math.pi / 2 + 0.4, seed, GOLD[2:6], BERRY, 1, True, 0.85)
        sprig(layer, W * .8, H - 4, H * 0.24, -math.pi / 2 - 0.4, seed + 2, GOLD[2:6], BERRY, -1, True, 0.8)
    if mirror:
        layer.im = layer.im.transpose(Image.FLIP_LEFT_RIGHT)
        layer.p = layer.im.load()
    cv.layer(layer, x0, y0)


def corner_ornament(cv, x, y, sx, sy, size, cols_leaf=GOLD[2:6], cols_berry=BERRY):
    """A painted khokhloma corner: two sprigs running along the edges from a rosette in the corner."""
    layer = Cv(size, size)
    sprig(layer, 6, 6, size * 0.8, 0.12, 4, cols_leaf, cols_berry, 1, True, 0.75, leaf_dark=True)
    sprig(layer, 6, 6, size * 0.8, math.pi / 2 - 0.12, 5, cols_leaf, cols_berry, -1, True, 0.75, leaf_dark=True)
    rosette(layer, 6, 6, 6)
    im = layer.im
    if sx < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if sy < 0:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    cv.im.alpha_composite(im, (int(x if sx > 0 else x - size), int(y if sy > 0 else y - size)))


# =================================================================== the doll
def doll(cv, ox, oy, w, h, body=RED, scarf=None, state="full", seed=0, apron=True):
    """A painted matryoshka seen from the front: lacquered body with a gloss, face, scarf rim, apron bouquet and
    the joint where the halves nest. state 'empty' is the bare, unpainted shell left when a layer is lost."""
    cx = ox + w / 2.0
    hy, hr_x, hr_y = oy + h * 0.29, w * 0.36, h * 0.28
    by, br_x, br_y = oy + h * 0.69, w * 0.5, h * 0.37
    base = oy + h - 0.5

    def inside(x, y):
        if y > base:
            return False
        return ((x - cx) / hr_x) ** 2 + ((y - hy) / hr_y) ** 2 <= 1 or ((x - cx) / br_x) ** 2 + ((y - by) / br_y) ** 2 <= 1

    def normal(x, y):
        if ((x - cx) / hr_x) ** 2 + ((y - hy) / hr_y) ** 2 <= 1 and y < oy + h * 0.47:
            return (x - cx) / hr_x, (y - hy) / hr_y
        return (x - cx) / br_x, (y - by) / br_y

    empty = state == "empty"
    cols = WOOD[1:] if empty else body

    def color(x, y):
        nx, ny = normal(x + .5, y + .5)
        light = clamp(0.62 - 0.38 * nx - 0.34 * ny - 0.12 * (nx * nx + ny * ny))
        if empty:
            light = 0.35 + light * 0.4 + (fbm(x / 3, y / 0.8, seed, 2) - 0.5) * 0.25
        c = ramp(cols, light)
        if not empty and (nx + 0.42) ** 2 + (ny + 0.45) ** 2 < 0.035 * (1 if w > 14 else 2):
            c = mix(c, (255, 240, 225), 0.7)
        return c

    shape(cv, inside, (ox - 1, oy - 1, ox + w + 1, oy + h + 1), color, OUTLINE)
    joint = oy + h * 0.52
    if empty:
        for x in range(int(ox), int(ox + w)):
            if cv.ok(x, int(joint)) and inside(x + .5, joint + .5):
                cv.put(x, joint, (30, 16, 8))
        # the dark hollow, seen through the open top of the shell
        shape(cv, lambda x, y: ((x - cx) / (hr_x * 0.7)) ** 2 + ((y - hy) / (hr_y * 0.6)) ** 2 <= 1,
              (ox, oy, ox + w, oy + h * 0.6), lambda x, y: mix((18, 10, 6), (50, 28, 14), clamp((y - hy) / hr_y + 0.5)))
        return
    # face
    fx_r, fy_r, fy = w * 0.21, h * 0.155, oy + h * 0.285
    if w >= 10:
        rim = scarf or GOLD
        shape(cv, lambda x, y: ((x - cx) / (fx_r + 1.2)) ** 2 + ((y - fy) / (fy_r + 1.2)) ** 2 <= 1,
              (cx - fx_r - 3, fy - fy_r - 3, cx + fx_r + 3, fy + fy_r + 3), lambda x, y: ramp(rim[2:], clamp(0.7 - (y - fy) / fy_r * .3)))
    shape(cv, lambda x, y: ((x - cx) / fx_r) ** 2 + ((y - fy) / fy_r) ** 2 <= 1,
          (cx - fx_r - 1, fy - fy_r - 1, cx + fx_r + 1, fy + fy_r + 1),
          lambda x, y: (98, 52, 30) if y < fy - fy_r * 0.35 + abs(x + .5 - cx) * 0.35 else mix(SKIN, (255, 236, 214), clamp(0.5 - (x - cx) / fx_r * .5)))
    ey = fy + fy_r * 0.05
    if w >= 12:
        for s in (-1, 1):
            ex_ = cx + s * fx_r * 0.42
            cv.put(ex_, ey, (24, 18, 30))
            cv.put(ex_ + (0 if s < 0 else -1), ey, (24, 18, 30))
            cv.disc(cx + s * fx_r * 0.6, fy + fy_r * 0.45, max(0.8, w * 0.035), (236, 120, 110), 0.85)
        cv.put(cx - .5, fy + fy_r * 0.68, (196, 30, 30))
        cv.put(cx + .5, fy + fy_r * 0.68, (196, 30, 30))
    else:
        cv.put(cx - fx_r * .45, ey, (24, 18, 30))
        cv.put(cx + fx_r * .45, ey, (24, 18, 30))
    # the joint between the nesting halves: a dark seam under a gold fillet
    for x in range(int(ox), int(ox + w + 1)):
        if inside(x + .5, joint + .5):
            cv.put(x, joint, OUTLINE)
            if inside(x + .5, joint - .5) and w >= 10:
                cv.put(x, joint - 1, GOLD[4])
    # the apron with its bouquet
    if apron and w >= 9:
        ax_r, ay_r, ay = w * 0.3, h * 0.2, oy + h * 0.745
        shape(cv, lambda x, y: ((x - cx) / ax_r) ** 2 + ((y - ay) / ay_r) ** 2 <= 1,
              (cx - ax_r - 1, ay - ay_r - 1, cx + ax_r + 1, ay + ay_r + 1),
              lambda x, y: mix((250, 232, 190), (220, 186, 120), clamp((y - ay) / ay_r * .5 + .4 + (x - cx) / ax_r * .2)),
              GOLD[2] if w >= 14 else None)
        if w >= 16:
            s = w / 40.0
            stem = [(cx, ay + ay_r * 0.8), (cx, ay - ay_r * 0.1)]
            stroke(cv, stem, max(0.5, .8 * s), max(0.4, .5 * s), (40, 90, 30))
            for side in (-1, 1):
                leaf(cv, (cx, ay + ay_r * 0.25), (cx + side * ax_r * 0.7, ay - ay_r * 0.05), max(1.2, 2.4 * s), LEAF_G[1:], OUTLINE)
            berries(cv, cx, ay - ay_r * 0.25, max(1.4, 2.6 * s), 3 if w < 30 else 4, seed)
        else:
            cv.disc(cx, ay - .5, max(1.0, w * 0.09), BERRY[3])
            cv.put(cx - w * .1, ay + 1, LEAF_G[3])
            cv.put(cx + w * .1, ay + 1, LEAF_G[3])
    # gold curls on the scarf, either side of the face
    if w >= 20:
        for s in (-1, 1):
            curl(cv, cx + s * (fx_r + 2.5), fy + fy_r * 0.9, max(1.2, w * 0.045), math.pi / 2 + s * 0.4, s, GOLD[1:6], max(0.6, w * 0.025))
    # hem band
    hem = oy + h * 0.94
    for x in range(int(ox), int(ox + w + 1)):
        if inside(x + .5, hem + .5) and inside(x + .5, hem - 1.5):
            cv.put(x, hem, GOLD[3] if (x % 3) else GOLD[5])


# =================================================================== sprites: panels and frames
def nine_lacquer(name, lw, lh, border, cols, rim_w, seed, rivets=True, accent=None):
    """A nine-slice lacquer panel with a gilded rim. The centre and edges tile seamlessly."""
    W, H, B = lw * S, lh * S, border * S
    cv = Cv(W, H)
    period_x, period_y = W - 2 * B, H - 2 * B
    # paint the lacquer as one period of a tileable field, shifted so the centre tile is exactly one period
    tmp = Cv(period_x, period_y)
    lacquer(tmp, 0, 0, period_x, period_y, cols, seed, 0.4, 0, period_x, period_y)
    for y in range(H):
        for x in range(W):
            cv.p[x, y] = tmp.p[(x - B) % period_x, (y - B) % period_y]
    gilt_frame(cv, 0, 0, W, H, rim_w, seed, chase=rim_w >= 10)
    if accent:
        for x in range(rim_w + 2, W - rim_w - 2):
            cv.put(x, rim_w + 1, accent)
            cv.put(x, H - rim_w - 2, accent)
        for y in range(rim_w + 2, H - rim_w - 2):
            cv.put(rim_w + 1, y, accent)
            cv.put(W - rim_w - 2, y, accent)
    inner_shadow(cv, rim_w, rim_w, W - rim_w, H - rim_w, 4, 0.35)
    if rivets:
        r = max(1.6, rim_w * 0.32)
        for (x, y) in ((rim_w * .5, rim_w * .5), (W - rim_w * .5, rim_w * .5), (rim_w * .5, H - rim_w * .5), (W - rim_w * .5, H - rim_w * .5)):
            rivet(cv, x, y, r)
    save(name, cv, border)
    return cv


def paper_sprite(name, lw, lh, border, seed, rim=True):
    W, H, B = lw * S, lh * S, border * S
    cv = Cv(W, H)
    px_, py_ = W - 2 * B, H - 2 * B
    tmp = Cv(px_, py_)
    paper(tmp, 0, 0, px_, py_, seed, px_, py_, 0.5, edge=False)
    for y in range(H):
        for x in range(W):
            cv.p[x, y] = tmp.p[(x - B) % px_, (y - B) % py_]
    # aged rim and a deckled edge
    for y in range(H):
        for x in range(W):
            d = min(x, y, W - 1 - x, H - 1 - y)
            along = x if d in (y, H - 1 - y) else y
            per = px_ if d in (y, H - 1 - y) else py_
            if d < B:
                cv.tint(x, y, (150, 100, 56), (1 - d / B) ** 2 * 0.6)
            deckle = vnoise(((along - B) % per) / 3.0, 0, seed + 40, per // 3 if per % 3 == 0 else 0)
            if d == 0 and deckle > 0.45:
                cv.p[x, y] = (0, 0, 0, 0)
            elif d == 0 or (d == 1 and deckle > 0.45):
                cv.put(x, y, (110, 72, 40))
    if rim:
        for x in range(4, W - 4):
            cv.put(x, 4, (178, 50, 36), 0.55)
            cv.put(x, H - 5, (178, 50, 36), 0.55)
        for y in range(4, H - 4):
            cv.put(4, y, (178, 50, 36), 0.55)
            cv.put(W - 5, y, (178, 50, 36), 0.55)
    save(name, cv, border)


def plate(name, st):
    """A title cartouche: gilded scroll ends with a berry, enamel field in the world's colour."""
    lw, lh, B = 64, 16, 12
    W, H = lw * S, lh * S
    cv = Cv(W, H)
    en = st["enamel"]
    for y in range(4, H - 4):
        for x in range(0, W):
            t = (y - 4) / (H - 8)
            cv.put(x, y, mix(scale_c(en, 1.35), scale_c(en, 0.7), t))
    for x in range(0, W):
        for y, tone in ((2, 0.32), (3, 0.8), (4, 0.6), (H - 5, 0.4), (H - 4, 0.65), (H - 3, 0.28)):
            cv.put(x, y, gold_tone(x, y, tone, 5, False))
        cv.put(x, 1, OUTLINE)
        cv.put(x, H - 2, OUTLINE)
        cv.put(x, 6, scale_c(en, 0.55))
    end = Cv(B * S, H)
    for y in range(H):
        for x in range(B * S):
            pass
    shape(end, lambda x, y: ((x - 15) / 13) ** 2 + ((y - H / 2) / (H / 2 - 0.5)) ** 2 <= 1 and x < 24 or (x >= 15 and 1 <= y <= H - 2),
          (0, 0, B * S, H), lambda x, y: gold_tone(x, y, 0.45 + 0.3 * math.cos((y - 4) / H * 3), 9, False), OUTLINE)
    shape(end, lambda x, y: ((x - 15) / 9) ** 2 + ((y - H / 2) / (H / 2 - 4.5)) ** 2 <= 1 or (x >= 15 and 5 <= y <= H - 5),
          (0, 0, B * S, H), lambda x, y: mix(scale_c(en, 1.35), scale_c(en, 0.7), (y - 4) / (H - 8)), GOLD[1])
    tube(end, spiral(9, H / 2, 5, 0.9, math.pi, -1), 1.2, 0.3, GOLD[1:6])
    berry(end, 9, H / 2, 2.6, st["berry"])
    cv.layer(end, 0, 0)
    flip = end.im.transpose(Image.FLIP_LEFT_RIGHT)
    cv.im.alpha_composite(flip, (W - B * S, 0))
    cv.p = cv.im.load()
    save(name, cv, {"left": B, "right": B, "top": 6, "bottom": 6})


def frieze(cv, x0, y0, x1, y1, st, seed=0):
    """A running khokhloma vine: a gold stem waving along a band, leaves in the world's colour, berry clusters."""
    lay = Cv(x1 - x0, y1 - y0)
    W, H = lay.w, lay.h
    mid = H / 2
    pts = [(x, mid + math.sin(x / 18.0) * H * 0.22) for x in range(0, W)]
    tube(lay, pts, 1.1, 1.1, GOLD[1:6])
    k = 0
    for x in range(9, W - 9, 18):
        y = mid + math.sin(x / 18.0) * H * 0.22
        up = math.cos(x / 18.0) > 0
        a = -math.pi / 2 - 0.7 if up else math.pi / 2 + 0.7
        if k % 3 == 0:
            leaf(lay, (x, y), (x + math.cos(a) * 11, y + math.sin(a) * 11 * 0.55), 3.4, st["leaf"], OUTLINE, vein=scale_c(st["leaf"][0], 1))
        elif k % 3 == 1:
            curl(lay, x, y, 2.4, a, 1 if up else -1, GOLD[1:6], 0.9)
        else:
            berries(lay, x + 2, y + (-5 if up else 5), 2.3, 3, seed + k, st["berry"])
        k += 1
    cv.layer(lay, x0, y0)


def station_panel(sid, w, slot_layout):
    """A full station cabinet, 256x222: lacquer on wood tinted by the world, a gilded frame, recesses for the
    recipe cabinet, the state niche and the inventory tray, a running vine and the world's painted wings."""
    st = world_style(w)
    W, H = 256 * S, 222 * S
    cv = Cv(W, H)
    cv.im.paste(BODY.im, (0, 0))
    cv.p = cv.im.load()
    acc, en = st["accent"], st["enamel"]
    tint = 0.0 if w == 0 else 0.22
    if tint:
        for y in range(H):
            for x in range(W):
                cv.tint(x, y, scale_c(en, 1.2), tint)
    deep = [scale_c(en, 0.25), scale_c(en, 0.5), scale_c(en, 0.8), scale_c(en, 1.1), scale_c(en, 1.5)]
    bw = 12

    def recess(x0, y0, x1, y1, kind):
        X0, Y0, X1, Y1 = x0 * S, y0 * S, x1 * S, y1 * S
        if kind == "wood":
            lacquer(cv, X0, Y0, X1, Y1, [(26, 14, 8), (42, 24, 12), (62, 36, 18), (84, 50, 26), (110, 70, 38)], 17 + x0, 0.5, 0.0)
        elif kind == "deep":
            lacquer(cv, X0, Y0, X1, Y1, deep, 23 + y0, 0.35, 0.06)
        inner_shadow(cv, X0, Y0, X1, Y1, 10, 0.65)
        for x in range(X0 - 1, X1 + 1):
            cv.put(x, Y0 - 2, OUTLINE)
        thin_gilt(cv, X0 - 1, Y0 - 1, X1 + 1, Y1 + 1, inset=True)

    def wing(x0, y0, x1, y1, mirror):
        """A gilt-framed painted inset with an arched top, enamel ground and the world's motif."""
        X0, Y0, X1, Y1 = x0, y0, x1, y1
        r = (X1 - X0) / 2
        cxw = (X0 + X1) / 2

        def inside(x, y):
            return X0 <= x < X1 and y < Y1 and (y >= Y0 + r or (x - cxw) ** 2 + (y - Y0 - r) ** 2 <= r * r)

        shape(cv, inside, (X0 - 1, Y0 - 1, X1 + 1, Y1 + 1),
              lambda x, y: mix(scale_c(en, 1.25), scale_c(en, 0.45), clamp((y - Y0) / (Y1 - Y0) * 0.8 + abs(x - cxw) / r * 0.2)), GOLD[4])
        for (x, y) in [(x, y) for y in range(int(Y0), int(Y1)) for x in range(int(X0), int(X1))]:
            if inside(x + .5, y + .5) and not inside(x + .5 - 2, y + .5 - 2):
                cv.mul(x, y, 0.7)
        world_motif(cv, int(X0) + 3, int(Y0) + 4, int(X1) - 3, int(Y1) - 3, w, mirror, 3)
        for (x, y) in [(x, y) for y in range(int(Y0) - 2, int(Y1) + 3) for x in range(int(X0) - 2, int(X1) + 3)]:
            if not inside(x + .5, y + .5) and any(inside(x + .5 + dx, y + .5 + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2))):
                cv.put(x, y, gold_tone(x, y, 0.75 if (x < cxw) else 0.4, 7, False))
        rivet(cv, cxw, Y0 + 1, 3.2)

    # accent pinstripe just inside the frame
    for x in range(bw + 3, W - bw - 3):
        for y in (bw + 3, H - bw - 4):
            cv.put(x, y, acc, 0.75)
    for y in range(bw + 3, H - bw - 3):
        for x in (bw + 3, W - bw - 4):
            cv.put(x, y, acc, 0.75)
    if slot_layout:
        recess(10, 20, 142, 124, "wood")
        recess(146, 20, 246, 124, "deep")
        shelf = Cv(98 * S, 102 * S)
        for side in (-1, 1):
            sprig(shelf, shelf.w / 2, shelf.h - 22, 88, math.pi / 2 - side * (math.pi / 2 - 0.12), 9 + side, GOLD[2:6], BERRY, side, True, 0.9, leaf_dark=True)
            sprig(shelf, shelf.w / 2 + side * 60, 10, 30, math.pi / 2 - side * 0.9, 12 + side, GOLD[2:6], BERRY, -side, True, 0.7, leaf_dark=True)
        berries(shelf, shelf.w / 2, shelf.h - 22, 3.2, 5, 4)
        shelf.im.putalpha(shelf.im.getchannel("A").point(lambda a: int(a * 0.8)))
        cv.layer(shelf, 147 * S, 21 * S)
    else:
        recess(10, 20, 194, 133, "wood")
        recess(195, 20, 248, 133, "deep")
        for y in range(22 * S, 130 * S):
            for x in range(189 * S, 192 * S):
                cv.put(x, y, (14, 8, 6))
            cv.put(189 * S - 1, y, GOLD[1])
            cv.put(192 * S, y, GOLD[4])
    recess(45, 137, 211, 216, "deep")
    wing(bw + 8, 140 * S, 43 * S - 4, H - bw - 8, False)
    wing(213 * S + 4, 140 * S, W - bw - 8, H - bw - 8, True)
    frieze(cv, bw + 6, bw + 5, W - bw - 6, 19 * S - 2, st, w)
    cv.p = cv.im.load()
    gilt_frame(cv, 0, 0, W, H, bw, 31)
    for (x, y) in ((6, 6), (W - 7, 6), (6, H - 7), (W - 7, H - 7)):
        rivet(cv, x, y, 4.2)
    for x in range(40, W - 40, 72):
        rivet(cv, x, H - 6, 2.4)
    save("station_" + sid, cv)


def book():
    """The Journal opened flat: red lacquer cover with a gilded edge and corner bosses, two parchment pages with
    page edges, a shaded gutter and a red and gold headband."""
    W, H = 340 * S, 214 * S
    cv = Cv(W, H)
    lacquer(cv, 0, 0, W, H, RED, 41, 0.35, 0.12)
    gilt_frame(cv, 0, 0, W, H, 8, 41, chase=False)
    # a gold vine running round the cover margin, and gilded corner guards
    st0 = world_style(0)
    frieze(cv, 24, 8, W - 24, 22, st0, 1)
    frieze(cv, 24, H - 22, W - 24, H - 8, st0, 2)
    for side in (0, 1):
        lay = Cv(H - 48, 14)
        frieze(lay, 0, 0, lay.w, lay.h, st0, 3 + side)
        im = lay.im.rotate(90 if side == 0 else -90, expand=True)
        cv.im.alpha_composite(im, (8 if side == 0 else W - 22, 24))
    cv.p = cv.im.load()
    for (x, y, sx, sy) in ((0, 0, 1, 1), (W - 1, 0, -1, 1), (0, H - 1, 1, -1), (W - 1, H - 1, -1, -1)):
        for i in range(30):
            for j in range(30 - i):
                xx, yy = x + sx * i, y + sy * j
                d = i + j
                t = 0.8 - d / 60 if d < 27 else 0.2
                cv.put(xx, yy, OUTLINE if d >= 28 else gold_tone(xx, yy, t + (0.1 if (i == 2 or j == 2) else 0), 5, False))
        rivet(cv, x + sx * 8, y + sy * 8, 3.2)
    pw = 155 * S
    for i, x0 in enumerate((11 * S, 174 * S)):
        y0, y1 = 11 * S, 203 * S
        # page block edges, stacked under the outer side of each page
        for k in range(4, 0, -1):
            ox = -k * 2 if i == 0 else k * 2
            for y in range(y0 + k, y1 + k):
                for x in (x0 + ox, x0 + pw - 1 + ox) if i == 0 else (x0 + pw - 1 + ox,):
                    pass
            cv.rect(x0 + ox, y0 + k, x0 + pw + ox, y1 + k, mix((200, 170, 120), (120, 86, 52), k / 4))
        paper(cv, x0, y0, x0 + pw, y1, 50 + i, aged=0.8)
        for y in range(y0, y1):
            for x in range(x0, x0 + pw):
                g = (x - x0) / pw if i == 0 else 1 - (x - x0) / pw
                f = 1 - 0.32 * smooth(clamp((g - 0.86) / 0.14)) - 0.06 * smooth(clamp((0.12 - g) / 0.12))
                cv.mul(x, y, f)
        # printed double rule in red ink with corner flourishes
        rx0, ry0, rx1, ry1 = x0 + 8, y0 + 8, x0 + pw - 9, y1 - 9
        for x in range(rx0, rx1 + 1):
            cv.put(x, ry0, (170, 40, 30), 0.7)
            cv.put(x, ry1, (170, 40, 30), 0.7)
            cv.put(x, ry0 + 3, (190, 140, 60), 0.6)
            cv.put(x, ry1 - 3, (190, 140, 60), 0.6)
        for y in range(ry0, ry1 + 1):
            cv.put(rx0, y, (170, 40, 30), 0.7)
            cv.put(rx1, y, (170, 40, 30), 0.7)
            cv.put(rx0 + 3, y, (190, 140, 60), 0.6)
            cv.put(rx1 - 3, y, (190, 140, 60), 0.6)
        for (cx, cy) in ((rx0, ry0), (rx1, ry0), (rx0, ry1), (rx1, ry1)):
            berry(cv, cx, cy, 2.6)
    # gutter and headband
    gx0, gx1 = 166 * S, 174 * S
    for y in range(11 * S - 3, 203 * S + 3):
        for x in range(gx0, gx1):
            u = (x - gx0) / (gx1 - gx0)
            cv.put(x, y, mix((46, 24, 14), (110, 70, 40), 1 - abs(u - 0.5) * 2))
        cv.put(gx0 + 7, y, GOLD[4])
        cv.put(gx0 + 8, y, GOLD[2])
    for y0 in (11 * S - 4, 203 * S - 2):
        for x in range(gx0 - 2, gx1 + 2):
            for y in range(y0, y0 + 6):
                cv.put(x, y, BERRY[3] if (x + y) % 4 < 2 else GOLD[4])
    save("book", cv)


def page_sheet():
    """A turning page seen from behind, shaded as it lifts: drawn stretched across while the page turns."""
    W, H = 155 * S, 192 * S
    cv = Cv(W, H)
    paper(cv, 0, 0, W, H, 77, aged=0.6)
    for y in range(H):
        for x in range(W):
            u = x / W
            cv.mul(x, y, 0.7 + 0.42 * math.sin(math.pi * (0.15 + 0.7 * u)) - 0.12 * u)
    save("page_sheet", cv)


def scroll_paper():
    W, H = 280 * S, 198 * S
    cv = Cv(W, H)
    paper(cv, 0, 0, W, H, 61, aged=1.0)
    # illuminated margins: a red and gold double rule and painted corners
    rx0, ry0, rx1, ry1 = 10, 10, W - 11, H - 11
    for x in range(rx0, rx1 + 1):
        for (y, c, a) in ((ry0, (170, 40, 30), .8), (ry0 + 3, (190, 140, 60), .7), (ry1, (170, 40, 30), .8), (ry1 - 3, (190, 140, 60), .7)):
            cv.put(x, y, c, a)
    for y in range(ry0, ry1 + 1):
        for (x, c, a) in ((rx0, (170, 40, 30), .8), (rx0 + 3, (190, 140, 60), .7), (rx1, (170, 40, 30), .8), (rx1 - 3, (190, 140, 60), .7)):
            cv.put(x, y, c, a)
    for (x, y, sx, sy) in ((2, 2, 1, 1), (W - 2, 2, -1, 1), (2, H - 2, 1, -1), (W - 2, H - 2, -1, -1)):
        corner_ornament(cv, x, y, sx, sy, 34)
    # a faint printed medallion behind the text: a wreath of sprigs round a rosette
    wm = Cv(200, 200)
    for i in range(6):
        a = i * math.pi / 3
        sprig(wm, 100 + math.cos(a) * 22, 100 + math.sin(a) * 22, 70, a + 0.2, 60 + i, RED[1:5], BERRY, 1, True, 1.0)
    rosette(wm, 100, 100, 20)
    wm.im.putalpha(wm.im.getchannel("A").point(lambda v: int(v * 0.09)))
    cv.layer(wm, 120, 110)
    save("scroll_paper", cv)


def rod():
    """The scroll's rod: a roll of paper on a turned axle with red lacquered finials banded in gold."""
    W, H = 316 * S, 14 * S
    cv = Cv(W, H)
    roll0, roll1 = 13 * S, W - 13 * S
    for y in range(2, H - 2):
        v = (y - 2) / (H - 4)
        for x in range(roll0, roll1):
            t = 0.25 + 0.75 * math.sin(math.pi * v) - 0.25 * v
            c = ramp(PAPER, t + (fbm(x / 10, y / 2, 3, 2) - 0.5) * 0.15)
            if y == int(2 + (H - 4) * 0.62):
                c = scale_c(c, 0.8)
            cv.put(x, y, c)
        cv.put(roll0, y, OUTLINE)
        cv.put(roll1 - 1, y, OUTLINE)
    for x in range(roll0, roll1):
        cv.put(x, 1, OUTLINE)
        cv.put(x, H - 2, OUTLINE)
    for side in (0, 1):
        end = Cv(13 * S, H)
        # collar, bulb, tip
        for x in range(end.w):
            u = x / end.w
            r = (H / 2 - 1) * (0.62 if u > 0.78 else 0.95 if 0.18 < u < 0.7 else 0.7)
            for y in range(H):
                dy = (y + .5 - H / 2) / r
                if abs(dy) <= 1:
                    light = clamp(0.62 - dy * 0.45 - dy * dy * 0.2)
                    if u > 0.78:
                        c = gold_tone(x, y, light, 13, False)
                    elif u < 0.18:
                        c = ramp(BLACK, light)
                    else:
                        c = ramp(RED, light)
                        if abs(u - 0.44) < 0.04:
                            c = gold_tone(x, y, light, 13, False)
                    end.put(x, y, c)
        for x in range(end.w):
            for y in range(H):
                if end.alpha(x, y) and (end.alpha(x, y - 1) == 0 or end.alpha(x, y + 1) == 0):
                    end.put(x, y, OUTLINE)
        im = end.im if side == 0 else end.im.transpose(Image.FLIP_LEFT_RIGHT)
        cv.im.alpha_composite(im, (0 if side == 0 else W - end.w, 0))
    cv.p = cv.im.load()
    save("scroll_rod", cv)


RIBBONS = [("objective", RED), ("quests", BLACK), ("karma", GOLD[1:]), ("worlds", [(12, 36, 22), (24, 62, 38), (40, 96, 58), (66, 132, 80), (110, 176, 120)]),
           ("scroll", [(14, 18, 44), (26, 36, 84), (44, 62, 128), (74, 96, 170), (130, 150, 210)]),
           ("pages", [(58, 32, 12), (104, 62, 28), (152, 100, 48), (198, 148, 82), (234, 200, 140)])]


def ribbons():
    W, H = 54 * S, 48 * S
    for i, (nm, cols) in enumerate(RIBBONS):
        for on in (False, True):
            cv = Cv(W, H)
            notch = 5

            def inside(x, y, notch=notch):
                if x < 1 or x >= W - 1 or y >= H:
                    return False
                depth = notch * (1 - abs(x - W / 2) / (W / 2))
                return y >= 1 + depth

            satin(cv, inside, (0, 0, W, H), cols, 30 + i, folds=((20, 0.18), (60, 0.12)))
            # stitched edges
            for y in range(4, H):
                if (y // 3) % 2 == 0:
                    for x in (4, W - 5):
                        cv.put(x, y, GOLD[5] if on else mix(cols[-1], (255, 255, 255), 0.2), 0.85)
            if on:
                # gold brocade bands and a berry
                for y in list(range(31, 35)) + list(range(H - 18, H - 14)):
                    for x in range(2, W - 2):
                        if cv.alpha(x, y):
                            cv.put(x, y, gold_tone(x, y, 0.4 + 0.4 * ((x + y) % 4 < 2), 3, False))
                for x in range(2, W - 2):
                    cv.put(x, 30, OUTLINE)
                    cv.put(x, 35, OUTLINE)
                for bx in range(10, W - 8, 14):
                    berry(cv, bx, 39, 2.2)
                for x in range(2, W - 2):
                    for y in range(1, H):
                        if cv.alpha(x, y):
                            cv.tint(x, y, (255, 230, 170), 0.12)
            save("ribbon_%d%s" % (i, "_on" if on else ""), cv)


def buttons():
    """Lacquer buttons, nine-slice 40x16 (border 5): normal, hover, pressed and disabled."""
    lw, lh, B = 40, 16, 5
    W, H = lw * S, lh * S
    variants = {
        "btn": (RED, 0.0, False),
        "btn_hover": ([mix(c, (255, 120, 80), 0.18) for c in RED], 0.12, False),
        "btn_pressed": ([scale_c(c, 0.78) for c in RED], -0.1, True),
        "btn_off": (BLACK, -0.2, False),
    }
    for name, (cols, gold_shift, pressed) in variants.items():
        cv = Cv(W, H)
        for y in range(H):
            for x in range(W):
                d = min(x, y, W - 1 - x, H - 1 - y)
                # rounded corners
                cx = min(x, W - 1 - x)
                cy = min(y, H - 1 - y)
                if cx < 3 and cy < 3 and (3 - cx) ** 2 + (3 - cy) ** 2 > 10:
                    continue
                if d == 0:
                    cv.put(x, y, OUTLINE)
                elif d <= 3:
                    top = y <= x and y <= H - 1 - y if False else (y < H / 2)
                    lit = (y <= 3 or x <= 3) != pressed
                    t = (0.78 if lit else 0.32) + gold_shift - (0.15 if name == "btn_off" else 0)
                    if d == 3:
                        t -= 0.35
                    cv.put(x, y, gold_tone(x, y % 8, t, 2, name == "btn_off"))
                else:
                    v = (y - 4) / (H - 8)
                    if pressed:
                        v = 1 - v
                    t = 0.62 - 0.3 * v + (0.18 if v < 0.22 else 0) + (fbm(0, y / 2, 4, 2) - 0.5) * 0.05
                    cv.put(x, y, ramp(cols, t))
        # gold beads at both ends
        for x in (6, W - 7):
            rivet(cv, x, H / 2 - .5, 1.6, GOLD if name != "btn_off" else [scale_c(c, 0.6) for c in GOLD])
        save(name, cv, B)


def slot():
    """A gilded socket: a carved ring of gold leaf around a dark, sunken well of wood."""
    W = 18 * S
    cv = Cv(W, W)
    for y in range(W):
        for x in range(W):
            d = min(x, y, W - 1 - x, W - 1 - y)
            lit = (x + y) < W - 1
            if d == 0:
                cv.put(x, y, OUTLINE)
            elif d <= 2:
                cv.put(x, y, gold_tone(x, y, (0.3 if lit else 0.82) + (0.12 if d == 1 else 0), 6, False))
            elif d == 3:
                cv.put(x, y, OUTLINE)
            else:
                t = 0.18 + 0.2 * clamp((min(x, y) - 3) / 8) + (fbm(x / 6, y / 1.5, 8, 2) - 0.5) * 0.1
                cv.put(x, y, ramp([(10, 6, 4), (26, 15, 9), (46, 28, 16), (70, 44, 26)], t))
    for (x, y) in ((2, 2), (W - 3, 2), (2, W - 3), (W - 3, W - 3)):
        cv.put(x, y, GOLD[6])
    save("slot", cv)


def drawers():
    """Recipe drawers, 174x21: honey wood under clear lacquer, a gilded cartouche for the result, a carved arrow,
    a progress groove under the ingredients and a painted berry knob at the end."""
    W, H = 174 * S, 21 * S
    for name in ("drawer", "drawer_ready"):
        cv = Cv(W, H)
        cols = [scale_c(c, 0.86) for c in WOOD[1:]] if name != "drawer_ready" else [mix(c, (236, 184, 72), 0.55) for c in WOOD[1:]]
        lacquer(cv, 0, 0, W, H, cols, 70, 0.7, 0.08, wood=(70, 38, 18))
        for x in range(W):
            cv.put(x, 0, OUTLINE)
            cv.put(x, H - 1, OUTLINE)
            cv.put(x, 1, scale_c(cols[-1], 1.1))
            cv.put(x, H - 2, scale_c(cols[0], 0.8))
        for y in range(H):
            cv.put(0, y, OUTLINE)
            cv.put(W - 1, y, OUTLINE)
            cv.put(1, y, scale_c(cols[-1], 1.05))
            cv.put(W - 2, y, scale_c(cols[0], 0.8))
        # result cartouche (2..33 logical)
        x0, x1 = 3 * S, 33 * S
        ready = name == "drawer_ready"
        for y in range(3, H - 3):
            for x in range(x0, x1):
                d = min(x - x0, y - 3, x1 - 1 - x, H - 4 - y)
                if d < 2:
                    cv.put(x, y, gold_tone(x, y, 0.85 if (d == 0) != ((x - x0) > (y - 3)) else 0.35, 4, False))
                else:
                    cv.put(x, y, ramp([(30, 12, 8), (60, 18, 14), (92, 26, 18)] if not ready else [(90, 60, 20), (150, 110, 40), (200, 160, 70)],
                                      0.3 + 0.4 * (1 - (y - 3) / H)))
        # carved chevron between result and ingredients, pointing at the result
        ax = 34 * S + 2
        for k in range(7):
            for dx, col in ((0, OUTLINE), (1, GOLD[5]), (2, GOLD[3]), (3, OUTLINE)):
                cv.put(ax + abs(k - 3) + dx, H / 2 - 4 + k, col)
        # progress groove (38..162 logical, y 18..19)
        for x in range(38 * S, 162 * S):
            cv.put(x, 18 * S - 1, OUTLINE)
            cv.put(x, 18 * S, (20, 10, 6))
            cv.put(x, 18 * S + 1, (28, 14, 8))
            cv.put(x, 18 * S + 2, scale_c(cols[-1], 0.95))
        # painted knob
        kx = 168 * S
        rivet(cv, kx, H / 2, 4.2)
        berry(cv, kx, H / 2, 2.4)
        for s in (-1, 1):
            curl(cv, kx - 7, H / 2 + s * 4, 1.6, math.pi + s * .3, -s, GOLD[1:6], 0.6)
        save(name, cv)
    # the drawer's dark side, seen when it slides out
    cv = Cv(8 * S, H)
    for y in range(H):
        for x in range(cv.w):
            cv.put(x, y, mix((10, 6, 4), (70, 44, 22), x / cv.w * (0.5 + 0.5 * math.sin(math.pi * y / H))))
    save("drawer_side", cv)
    # progress fill: a strip of gold leaf
    cv = Cv(124 * S, 2 * S)
    for y in range(cv.h):
        for x in range(cv.w):
            cv.put(x, y, gold_tone(x, y, 0.85 - y * 0.18, 12, False))
    save("drawer_fill", cv)


def thumb():
    cv = Cv(4 * S, 14 * S)
    for y in range(cv.h):
        for x in range(cv.w):
            d = min(x, y, cv.w - 1 - x, cv.h - 1 - y)
            cv.put(x, y, OUTLINE if d == 0 else gold_tone(x, y, 0.85 - x * 0.12 - (0.2 if d == 1 and x > 3 else 0), 8, False))
    rivet(cv, cv.w / 2, cv.h / 2, 1.5)
    save("thumb", cv, {"left": 1, "right": 1, "top": 3, "bottom": 3})


def divider():
    """A heading rule for the pages: two gold stems meeting at a berry cluster."""
    W, H = 120 * S, 10 * S
    cv = Cv(W, H)
    cx, cy = W / 2, H / 2
    for side in (-1, 1):
        pts = [(cx + side * (6 + t), cy + math.sin(t / 14) * 2 * (1 - t / (W / 2))) for t in range(0, int(W / 2 - 8))]
        tube(cv, pts, 1.1, 0.3, GOLD[1:6], 1.0)
        for k in range(18, int(W / 2 - 14), 22):
            curl(cv, cx + side * k, cy, 2.0, -math.pi / 2 if (k // 22) % 2 else math.pi / 2, side if (k // 22) % 2 else -side, GOLD[1:6], 0.7)
    berries(cv, cx, cy, 2.4, 3, 4)
    save("divider", cv)


def vessel():
    """The station's state indicator: a glass doll on a gold foot. Back (dark glass), liquid (tinted at run time)
    and the glass front with its highlights are separate so the liquid can rise between them."""
    lw, lh = 40, 56
    W, H = lw * S, lh * S
    cx = W / 2
    hy, hrx, hry = H * 0.25, W * 0.30, H * 0.20
    by, brx, bry = H * 0.62, W * 0.44, H * 0.32
    base = H - 8

    def inside(x, y):
        if y > base:
            return False
        return ((x - cx) / hrx) ** 2 + ((y - hy) / hry) ** 2 <= 1 or ((x - cx) / brx) ** 2 + ((y - by) / bry) ** 2 <= 1

    back = Cv(W, H)
    shape(back, inside, (0, 0, W, H), lambda x, y: (mix((214, 232, 240), (120, 150, 170), clamp(y / H * 0.8 + abs(x - cx) / W))) + (0.42,), GOLD[2])
    # foot
    for y in range(int(base) + 1, H):
        for x in range(int(cx - brx * 0.8), int(cx + brx * 0.8)):
            back.put(x, y, gold_tone(x, y, 0.75 - (y - base) * 0.06 - abs(x - cx) / W * 0.3, 2, False))
    for x in range(int(cx - brx * 0.8), int(cx + brx * 0.8)):
        back.put(x, H - 1, OUTLINE)
    save("vessel_back", back)
    liq = Cv(W, H)
    shape(liq, inside, (0, 0, W, H), lambda x, y: mix((255, 255, 255), (150, 150, 150), clamp(((x - cx) / brx + 1) / 2 * 0.7 + 0.15)))
    save("vessel_liquid", liq)
    front = Cv(W, H)
    mask = shape(front, inside, (0, 0, W, H), lambda x, y: None)
    for (x, y) in mask:
        edge = not all((x + dx, y + dy) in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            front.put(x, y, GOLD[2])
        else:
            nx = (x - cx) / brx
            if -0.72 < nx < -0.52 and y > hy:
                front.put(x, y, (255, 255, 255), 0.45)
            elif 0.62 < nx < 0.7:
                front.put(x, y, (255, 255, 255), 0.18)
    # gold painted on the glass: curls either side of the body, a scarf rim round the face
    for sd in (-1, 1):
        curl(front, cx + sd * brx * 0.55, by + bry * 0.55, 3.2, -math.pi / 2 - sd * 0.3, sd, GOLD[2:6], 1.0)
        leaf(front, (cx + sd * brx * 0.2, by + bry * 0.75), (cx + sd * brx * 0.62, by + bry * 0.25), 2.6, GOLD[2:6], GOLD[1])
    # painted face on the glass head and a gold seam
    doll_face = Cv(W, H)
    fx_r, fy_r, fy = W * 0.17, H * 0.11, hy + 2
    shape(doll_face, lambda x, y: ((x - cx) / fx_r) ** 2 + ((y - fy) / fy_r) ** 2 <= 1, (cx - fx_r - 1, fy - fy_r - 1, cx + fx_r + 1, fy + fy_r + 1),
          lambda x, y: (98, 52, 30) if y < fy - fy_r * 0.35 + abs(x + .5 - cx) * 0.35 else SKIN, GOLD[3])
    for k in range(-1, 2):
        berry(doll_face, cx + k * 4, fy + fy_r + 4 - abs(k), 2.0)
    for s in (-1, 1):
        doll_face.put(cx + s * fx_r * .42, fy + 1, (24, 18, 30))
        doll_face.disc(cx + s * fx_r * .62, fy + fy_r * .45, 1.0, (236, 120, 110))
    doll_face.put(cx, fy + fy_r * .68, (196, 30, 30))
    front.layer(doll_face)
    joint = int(H * 0.45)
    for x in range(W):
        if (x, joint) in mask:
            front.put(x, joint, GOLD[4])
            front.put(x, joint + 1, GOLD[1])
    save("vessel_front", front)
    # one rising bubble
    b = Cv(3 * S, 3 * S)
    bubble(b, b.w / 2, b.h / 2, 2.2, (255, 255, 255))
    save("bubble", b)


def nest_dolls():
    """Illustration dolls for the Journal pages, from the outer doll to the smallest."""
    bodies = [RED, BLACK, GOLD[1:], RED, BLACK]
    sizes = [(42, 64), (34, 52), (28, 42), (22, 33), (16, 25)]
    for i, ((lw, lh), body) in enumerate(zip(sizes, bodies)):
        cv = Cv(lw * S, lh * S)
        doll(cv, 1, 1, cv.w - 2, cv.h - 2, body, None, "full", i)
        save("nest_%d" % i, cv)


def life_dolls():
    """The Doll of Life for the HUD and the Journal: three nested layers, painted when held, bare when lost."""
    for i, (lw, lh) in enumerate(((12, 17), (10, 14), (8, 11))):
        for state in ("full", "empty"):
            cv = Cv(lw * S, lh * S)
            doll(cv, 1, 1, cv.w - 2, cv.h - 2, [RED, BLACK, RED][i], None, state, i, apron=True)
            save("life_%d_%s" % (i, state), cv)
    for state in ("full", "empty"):
        cv = Cv(8 * S, 11 * S)
        doll(cv, 1, 1, cv.w - 2, cv.h - 2, RED, None, state, 9)
        save("doll_small_%s" % state, cv)


def lantern():
    """A tiny soul lantern: gilded cage and cap, a glass that the flame lights from inside."""
    W, H = 9 * S, 13 * S
    cv = Cv(W, H)
    cx = W / 2
    for y in range(4, H - 3):
        for x in range(3, W - 3):
            cv.put(x, y, (60, 40, 30), 0.55)
    for y in range(4, H - 3):
        for x in (2, W - 3, int(cx)):
            cv.put(x, y, GOLD[3] if x != W - 3 else GOLD[2])
    for x in range(1, W - 1):
        cv.put(x, 3, GOLD[4])
        cv.put(x, 4, GOLD[2])
        cv.put(x, H - 3, GOLD[3])
        cv.put(x, H - 2, GOLD[1])
    for x in range(int(cx) - 2, int(cx) + 3):
        cv.put(x, 2, GOLD[3])
    for a in range(0, 360, 20):
        r = math.radians(a)
        if math.sin(r) < 0.1:
            cv.put(cx + math.cos(r) * 2, 1 + math.sin(r) * 1.5, GOLD[4])
    for x in range(1, W - 1):
        cv.put(x, H - 1, OUTLINE)
    save("lantern", cv)
    for f in range(3):
        fl = Cv(W, H)
        fl.glow(cx, H * 0.6, 6, (255, 170, 60), 0.55)
        flame(fl, cx - 0.5 + (f - 1) * 0.6, H - 4, 7 + f * 0.6, 13 + (f % 2) * 2, f * 2.1,
              ((120, 40, 10), (240, 120, 30), (255, 190, 80), (255, 236, 160), (255, 255, 230)))
        save("lantern_flame_%d" % f, fl)
    g = Cv(24 * S, 24 * S)
    g.glow(g.w / 2, g.h / 2, g.w / 2, (255, 190, 90), 1.0, 1.6)
    save("glow", g)


def sparkles():
    g = Cv(9 * S, 9 * S)
    c = g.w / 2
    for i in range(-8, 9):
        f = (1 - abs(i) / 9) ** 1.5
        g.put(c + i, c, (255, 246, 200), f)
        g.put(c, c + i, (255, 246, 200), f)
    for i in range(-3, 4):
        f = (1 - abs(i) / 4) * 0.6
        g.put(c + i, c + i, (255, 246, 200), f)
        g.put(c + i, c - i, (255, 246, 200), f)
    g.glow(c, c, 4, (255, 255, 255), 0.9)
    save("glint", g)
    sh = Cv(20 * S, 8 * S)
    for y in range(sh.h):
        for x in range(sh.w):
            u = x / sh.w - 0.5 - (y / sh.h - 0.5) * 0.35
            sh.put(x, y, (255, 240, 190), 0.55 * math.exp(-(u / 0.14) ** 2))
    save("sheen", sh)


RULE_EMBLEMS = ["toxin", "heat", "locks", "wind", "darkness", "gravity", "pressure", "time", "ground", "synthesis"]


def medallion(rule, w):
    """A gilt medallion with a painted enamel emblem for a world rule."""
    st = world_style(w)
    D = 22 * S
    cv = Cv(D, D)
    c = D / 2 - .5
    R = D / 2 - .5
    for y in range(D):
        for x in range(D):
            d = math.hypot(x - c, y - c)
            if d > R:
                continue
            if d > R - 1:
                cv.put(x, y, OUTLINE)
            elif d > R - 5:
                ang = math.atan2(y - c, x - c)
                lit = -math.sin(ang + math.pi / 4)
                t = 0.55 + 0.3 * lit * (1 if d > R - 3 else -1)
                if d > R - 3 and int((ang + math.pi) / (2 * math.pi) * 24) % 2 == 0 and abs(d - (R - 3.5)) < 0.8:
                    t = 0.2
                cv.put(x, y, gold_tone(x, y, t, 4, False))
            elif d > R - 6:
                cv.put(x, y, OUTLINE)
            else:
                cv.put(x, y, mix(scale_c(st["enamel"], 1.5), scale_c(st["enamel"], 0.55), clamp(d / (R - 6) * 0.7 + (y - c) / R * 0.3)))
    e = Cv(D, D)
    m = D / 2
    if rule == "toxin":
        shape(e, lambda x, y: (y > m - 9 and abs(x - m) <= (y - (m - 9)) * 0.55 and y < m + 2) or (x - m) ** 2 + (y - m - 2) ** 2 <= 30,
              (m - 7, m - 10, m + 7, m + 9), lambda x, y: ramp([(30, 70, 20), (110, 180, 50), (190, 240, 110)], clamp(0.8 - (x - m) / 8)), OUTLINE)
        e.put(m - 2, m + 1, (240, 255, 220))
        e.put(m - 3, m + 2, (240, 255, 220))
        bubble(e, m + 6, m - 6, 1.6, (200, 255, 150))
    elif rule == "heat":
        flame(e, m, m + 8, 13, 18, 0.3)
    elif rule == "locks":
        shape(e, lambda x, y: abs(x - m) <= 6 and m - 2 <= y <= m + 8, (m - 7, m - 3, m + 7, m + 9),
              lambda x, y: gold_tone(int(x), int(y), 0.7 - (y - m) / 20, 3, False), OUTLINE)
        for a in range(180, 361, 6):
            r = math.radians(a)
            e.disc(m + math.cos(r) * 4, m - 2 + math.sin(r) * 5, 1.1, (150, 156, 170))
        e.disc(m, m + 2, 1.6, OUTLINE)
        e.rect(m - .5, m + 2, m + 1, m + 6, OUTLINE)
    elif rule == "wind":
        for k, (yy, r) in enumerate(((m - 4, 5), (m + 1, 6.5), (m + 6, 4))):
            pts = [(m - 9 + t * 0.6, yy) for t in range(0, 22)]
            pts += spiral(pts[-1][0], yy - r * .55, r * .55, 0.85, math.pi / 2, -1)
            tube(e, pts, 1.1, 0.3, [(60, 90, 140), (200, 220, 245), (255, 255, 255)])
    elif rule == "darkness":
        shape(e, lambda x, y: (x - m) ** 2 + (y - m + 1) ** 2 <= 36 and y < m + 4 or (abs(x - m) <= 7 and m + 3 <= y <= m + 5),
              (m - 8, m - 8, m + 8, m + 6), lambda x, y: gold_tone(int(x), int(y), 0.75 - (x - m) / 14, 3, False), OUTLINE)
        e.disc(m, m + 7, 1.6, GOLD[4])
        for k in (1, 2):
            for a in range(-50, 51, 8):
                r = math.radians(a)
                e.put(m + 8 + k * 3 * math.cos(r), m + k * 3 * math.sin(r), (170, 190, 255))
                e.put(m - 8 - k * 3 * math.cos(r), m + k * 3 * math.sin(r), (170, 190, 255))
    elif rule == "gravity":
        for s in (-1, 1):
            pts = [(m + s * 3.5, m), (m + s * 3.5, m - s * 7)]
            tube(e, pts, 1.2, 1.2, [(80, 30, 100), (220, 140, 240), (255, 230, 255)])
            for k in range(4):
                e.rect(m + s * 3.5 - k - .5, m - s * (7 - k) - .5, m + s * 3.5 + k + 1.5, m - s * (7 - k) + .5, (240, 200, 250))
        e.rect(m - 8, m + (8 if True else 0), m + 9, m + 9, GOLD[4])
        e.rect(m - 8, m - 9, m + 9, m - 8, (74, 216, 200))
    elif rule == "pressure":
        for (bx, byy, r) in ((m - 3, m + 4, 3.6), (m + 4, m - 1, 2.6), (m - 1, m - 6, 2.0), (m + 5, m + 6, 1.6)):
            bubble(e, bx, byy, r, (154, 240, 255))
    elif rule == "time":
        quads = [(150, 210, 90), (240, 200, 70), (220, 110, 40), (210, 230, 250)]
        for y in range(D):
            for x in range(D):
                d = math.hypot(x - m + .5, y - m + .5)
                if d <= 9:
                    a = (math.atan2(y - m + .5, x - m + .5) + math.pi / 2) % (2 * math.pi)
                    q = int(a / (math.pi / 2)) % 4
                    e.put(x, y, mix(quads[q], (0, 0, 0), 0.15 + d / 30) if d < 8.5 else OUTLINE)
        for q in range(4):
            a = q * math.pi / 2 - math.pi / 2
            stroke(e, [(m - .5, m - .5), (m - .5 + math.cos(a) * 9, m - .5 + math.sin(a) * 9)], 0.5, 0.5, OUTLINE)
        rivet(e, m - .5, m - .5, 1.8)
    elif rule == "ground":
        rock(e, m, m + 2, 8, 5)
        crack = [(m - 1, m - 6), (m + 1, m - 2), (m - 2, m + 1), (m + 2, m + 5), (m, m + 8)]
        stroke(e, crack, 1.0, 0.5, OUTLINE)
        stroke(e, [(x + 1, y) for x, y in crack], 0.4, 0.3, (232, 160, 112))
    elif rule == "stillness":
        # World 0: an empty doll standing, a hammer laid down at its feet
        doll(e, m - 8, m - 14, 16, 22, state="empty", seed=5, apron=False)
        stroke(e, [(m - 12, m + 11), (m + 4, m + 11)], 1.2, 1.2, WOOD[4])
        e.rect(m + 3, m + 8, m + 10, m + 14, (170, 176, 190))
        e.rect(m + 3, m + 13, m + 10, m + 14, OUTLINE)
    elif rule == "synthesis":
        spindle(e, m, m, 18)
        stroke(e, bez((m, m + 2), (m + 10, m + 6), (m - 10, m + 8), (m + 6, m + 10), 30), 0.6, 0.5, (80, 120, 200))
    cv.layer(e)
    save("rule_" + rule, cv)


def pips():
    """Quest markers: an open berry, a gilded boss with a tick when done, a grey bead when locked."""
    D = 7 * S
    cv = Cv(D, D)
    berry(cv, D / 2, D / 2, 5.2)
    save("pip_open", cv)
    cv = Cv(D, D)
    rivet(cv, D / 2, D / 2, 5.6)
    for (x, y) in ((4, 7), (5, 8), (6, 9), (7, 8), (8, 7), (9, 6), (10, 5)):
        cv.put(x, y, (40, 90, 30))
        cv.put(x, y + 1, (20, 50, 14))
    save("pip_done", cv)
    cv = Cv(D, D)
    berry(cv, D / 2, D / 2, 5.0, [(40, 36, 34), (80, 74, 70), (120, 112, 106), (150, 142, 134), (180, 172, 164), (210, 204, 196)], (30, 26, 24))
    save("pip_locked", cv)


def needle():
    cv = Cv(2 * S, 10 * S)
    for y in range(cv.h):
        for x in range(cv.w):
            cv.put(x, y, OUTLINE if x in (0, cv.w - 1) else (250, 240, 220) if y < cv.h * 0.6 else GOLD[3])
    save("dial_needle", cv)


def vial():
    """A horizontal glass vial with gilded caps: back, liquid (tinted at run time) and glass front."""
    lw, lh = 80, 9
    W, H = lw * S, lh * S
    cap = 5 * S
    back = Cv(W, H)
    for y in range(2, H - 2):
        for x in range(cap, W - cap):
            back.put(x, y, mix((14, 10, 14), (36, 30, 38), 1 - (y - 2) / (H - 4)))
    for x in range(cap, W - cap):
        back.put(x, 1, OUTLINE)
        back.put(x, H - 2, OUTLINE)
    for side in (0, 1):
        for y in range(H):
            for x in range(cap):
                xx = x if side == 0 else W - 1 - x
                yy = abs(y + .5 - H / 2) / (H / 2)
                if yy > 0.95:
                    continue
                t = 0.7 - (y - H / 2) / H * 0.8
                if x in (3, 4):
                    t -= 0.35
                back.put(xx, y, gold_tone(xx, y, t, 5, False) if x > 0 else OUTLINE)
    save("vial_back", back, {"left": 5, "right": 5, "top": 0, "bottom": 0})
    liq = Cv(W - 2 * cap, H - 4)
    for y in range(liq.h):
        for x in range(liq.w):
            v = y / liq.h
            liq.put(x, y, mix((255, 255, 255), (130, 130, 130), v * 0.9) if y > 0 else (255, 255, 255))
    save("vial_liquid", liq)
    front = Cv(W, H)
    for x in range(cap, W - cap):
        front.put(x, 3, (255, 255, 255), 0.5)
        front.put(x, 4, (255, 255, 255), 0.15)
        front.put(x, H - 4, (255, 255, 255), 0.12)
    save("vial_front", front, {"left": 5, "right": 5, "top": 0, "bottom": 0})


def hud_plaque():
    nine_lacquer("hud_plaque", 48, 32, 7, BLACK, 6, 81, rivets=True, accent=(150, 30, 24))


def frames():
    nine_lacquer("frame", 64, 64, 10, BLACK, 10, 91, rivets=True, accent=(160, 32, 24))
    paper_sprite("paper", 48, 48, 6, 13)


BODY = None


def build():
    global BODY
    BODY = Cv(256 * S, 222 * S)
    lacquer(BODY, 0, 0, BODY.w, BODY.h, BLACK, 5, 0.45, 0.09)
    frames()
    hud_plaque()
    buttons()
    slot()
    drawers()
    thumb()
    divider()
    vessel()
    nest_dolls()
    life_dolls()
    lantern()
    sparkles()
    needle()
    pips()
    vial()
    book()
    page_sheet()
    scroll_paper()
    rod()
    ribbons()
    for w in range(0, 11):
        plate("plate_%d" % w, world_style(w))
    for rule, w in zip(RULE_EMBLEMS, range(1, 11)):
        medallion(rule, w)
    medallion("stillness", 0)
    for sid, _en, _fr, w, *_ in STATIONS:
        station_panel(sid, w, sid in ("soul_altar", "class_table"))
    keep = {n + ".png" for n in SAVED} | {n + ".png.mcmeta" for n in SAVED}
    for f in os.listdir(OUT):
        if f not in keep:
            os.remove(os.path.join(OUT, f))
    print("gui sprites ok (%d)" % len(SAVED))


def preview(directory):
    """Contact sheet of every sprite at 2x of its texture size, on a neutral grey."""
    os.makedirs(directory, exist_ok=True)
    ims = [(n, Image.open(os.path.join(OUT, n + ".png"))) for n in SAVED]
    big = [x for x in ims if x[1].width >= 300]
    small = [x for x in ims if x[1].width < 300]
    for i, (n, im) in enumerate(big):
        bg = Image.new("RGBA", (im.width * 2, im.height * 2), (90, 90, 96, 255))
        bg.alpha_composite(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
        bg.save(os.path.join(directory, "big_%s.png" % n))
    x = y = 0
    rowh = 0
    sheet = Image.new("RGBA", (1600, 1400), (90, 90, 96, 255))
    for n, im in small:
        im2 = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        if x + im2.width > 1600:
            x, y = 0, y + rowh + 8
            rowh = 0
        sheet.alpha_composite(im2, (x, y))
        x += im2.width + 8
        rowh = max(rowh, im2.height)
    sheet.save(os.path.join(directory, "small_sheet.png"))


if __name__ == "__main__":
    build()
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
