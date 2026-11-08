"""Hand-crafted pixel art for the most visible Matriochka items and blocks.

Every sprite is drawn in a 16 x 16 unit space and rasterized at any resolution: 16 for the mod itself, 32 for the
optional Matriochka HD resource pack (tools/hdpack.py). The style follows the vanilla items:

- clean silhouettes closed by a dark outline taken from the darkest tone of the part it surrounds;
- three to four tones per material, lit from the top left, quantized (no gradients, no noise smear);
- shadows shifted toward violet-blue and highlights toward warm yellow, so a ramp never reads as "just darker";
- highlights placed sparingly where the form faces the light;
- each world's objects share that world's palette (WORLD_STYLE), and its glyph (GLYPHS).

Everything is deterministic: there is no unseeded randomness, so regenerating gives the same bytes.
"""
import colorsys
import math

from PIL import Image

# =================================================================== colour
LIGHT = (-0.52, -0.62, 0.59)  # top-left, slightly in front
_ln = math.sqrt(sum(v * v for v in LIGHT))
LIGHT = tuple(v / _ln for v in LIGHT)


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def mix(a, b, t):
    t = clamp(t)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _hue_toward(h, target, amount):
    d = (target - h + 0.5) % 1.0 - 0.5
    step = max(-amount, min(amount, d))
    return (h + step) % 1.0


def hramp(base, n=6, dl=0.105, hs=0.03, sat=0.05, top=0.93, bottom=0.05, at=None):
    """A hue-shifted ramp from dark to light around `base`: darker tones lean toward violet-blue and gain a little
    saturation, lighter ones lean toward warm yellow and lose some. `at` is the index the base lands on."""
    if isinstance(base, str):
        base = hx(base)
    r, g, b = [c / 255 for c in base]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    at = n - 3 if at is None else at
    out = []
    for i in range(n):
        k = i - at
        if k < 0:
            hh = _hue_toward(h, 0.70, -k * hs)
            ll = l + k * dl * (0.55 + 0.45 * l)
            ss = clamp(s + (-k) * sat * 0.6)
        else:
            hh = _hue_toward(h, 0.13, k * hs)
            ll = l + k * dl * (1.15 - 0.5 * l)
            ss = clamp(s - k * sat)
        ll = clamp(ll, bottom, top)
        rr, gg, bb = colorsys.hls_to_rgb(hh, ll, ss)
        out.append((int(round(rr * 255)), int(round(gg * 255)), int(round(bb * 255))))
    return out


# curated ramps shared with the GUI (tools/gui.py): gold leaf, red lacquer, painted wood, parchment
GOLD = [(54, 30, 10), (110, 70, 22), (168, 118, 40), (214, 166, 66), (240, 204, 112), (255, 238, 176)]
RED = [(46, 6, 10), (98, 16, 18), (146, 28, 24), (190, 44, 32), (222, 84, 56), (246, 150, 110)]
WOOD = [(46, 24, 14), (84, 48, 26), (122, 76, 40), (158, 106, 58), (192, 142, 84), (222, 180, 120)]
PAPER = [(96, 64, 40), (164, 128, 86), (206, 176, 128), (230, 208, 166), (244, 230, 198), (252, 246, 228)]
IRON = [(30, 32, 40), (64, 68, 80), (108, 114, 128), (152, 158, 172), (196, 202, 214), (236, 240, 246)]
SKIN = [(120, 70, 50), (196, 136, 104), (232, 184, 150), (246, 214, 186), (255, 236, 216)]
INK = (40, 22, 18)
CHEEK = (224, 98, 92)

# per world: body (lacquer of dolls, seeds, cores), second (painted bands), glow (accent light), metal (gear),
# leaf (small greens), glyph colour on cream
_WS = {
    0: ("c22e26", "e0b050", "f6d68a", "b8bcc4", "5a8a34"),
    1: ("3d7a2c", "7c4a9c", "b7e04a", "6a8a4a", "86b83a"),
    2: ("3e2c26", "e0661c", "ffb347", "5a4a44", "a0641c"),
    3: ("5c6474", "9aa2b0", "7fd3ff", "8a92a0", "5a7a8a"),
    4: ("3a78c6", "dce8f6", "ffe14a", "c8d8ec", "6aa0d0"),
    5: ("22305a", "141420", "6a8aff", "2c3450", "3a4a8a"),
    6: ("b44ccc", "4ac8c0", "f4eefa", "d8b0e8", "4ab8b0"),
    7: ("0f4c6c", "1ab0b0", "9af0ff", "2a6a8a", "2a9a8a"),
    8: ("c89a3c", "d86a2a", "f0f0ff", "b08a4a", "6aa040"),
    9: ("84462e", "b85a3e", "ffa860", "7a5040", "8a6a3a"),
    10: ("b0402a", "3a6ab8", "e8c070", "c8a070", "5a8a4a"),
    11: ("8a1c14", "e8c070", "f6ecd8", "a08060", "6a7a3a"),
}
WORLD_STYLE = {}
for _w, (_b, _s, _g, _m, _l) in _WS.items():
    WORLD_STYLE[_w] = dict(body=hramp(_b), second=hramp(_s), glow=hramp(_g, dl=0.08), metal=hramp(_m), leaf=hramp(_l, n=5))
WORLD_STYLE[0]["body"] = RED
WORLD_STYLE[0]["second"] = GOLD
WORLD_STYLE[5]["body"] = hramp("22305a", dl=0.09, bottom=0.04)
WORLD_STYLE[5]["second"] = hramp("1a1a2a", dl=0.08, bottom=0.03)


def style(w):
    return WORLD_STYLE[w]


# =================================================================== the canvas
class Spr:
    """A sprite in 16-unit space, `res` pixels wide. Parts are filled in order; `finish` closes the silhouette
    with an outline made of the darkest tone of the part each outline pixel touches."""

    def __init__(self, res=16, w=16, h=16):
        self.res = res
        self.k = res / 16.0
        self.W, self.H = int(round(w * self.k)), int(round(h * self.k))
        self.px = {}
        self.rim = {}
        self.glow = set()

    # ---- masks (pixel sets) from unit-space predicates
    def mask(self, inside):
        k = self.k
        return {(i, j) for j in range(self.H) for i in range(self.W) if inside((i + 0.5) / k, (j + 0.5) / k)}

    def ell(self, cx, cy, rx, ry):
        return self.mask(lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0)

    def disc(self, cx, cy, r):
        return self.ell(cx, cy, r, r)

    def rect(self, x0, y0, x1, y1):
        """Unit rectangle [x0, x1) x [y0, y1)."""
        return self.mask(lambda x, y: x0 <= x < x1 and y0 <= y < y1)

    def poly(self, pts):
        def inside(x, y):
            c = False
            n = len(pts)
            for i in range(n):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
                if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                    c = not c
            return c
        return self.mask(inside)

    def capsule(self, x0, y0, x1, y1, r):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-9

        def inside(x, y):
            t = clamp(((x - x0) * dx + (y - y0) * dy) / L2)
            return (x - x0 - t * dx) ** 2 + (y - y0 - t * dy) ** 2 <= r * r
        return self.mask(inside)

    def path(self, pts, r):
        m = set()
        for a, b in zip(pts, pts[1:]):
            m |= self.capsule(a[0], a[1], b[0], b[1], r)
        return m

    def ring(self, cx, cy, r0, r1):
        return self.mask(lambda x, y: r0 * r0 <= (x - cx) ** 2 + (y - cy) ** 2 <= r1 * r1)

    # ---- painting
    def put(self, p, col, a=255):
        if 0 <= p[0] < self.W and 0 <= p[1] < self.H:
            self.px[p] = (col[0], col[1], col[2], a)

    def fill(self, m, col, rim=None, glow=False, a=255):
        for p in m:
            c = col(p) if callable(col) else col
            if c is None:
                continue
            self.put(p, c, a)
            if rim is not None:
                self.rim[p] = rim
            elif p in self.rim:
                pass
            if glow:
                self.glow.add(p)
        return m

    def shade(self, m, ramp, normal, rim=True, lo=1, hi=None, bias=0.0, spec=0.0, glow=False, levels=None):
        """Lights mask m with the given normal field (callable (x, y) in units -> (nx, ny, nz)) and quantizes onto
        ramp[lo..hi]. spec > 0 adds the top highlight tone where the surface faces the light within that margin."""
        hi = len(ramp) - 2 if hi is None else hi
        k = self.k
        for (i, j) in m:
            n = normal((i + 0.5) / k, (j + 0.5) / k)
            d = n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2]
            t = clamp((d + 0.35) / 1.25 + bias)
            if levels:
                t = round(t * (levels - 1)) / (levels - 1)
            idx = lo + int(round(t * (hi - lo)))
            if spec and d > 1.0 - spec:
                idx = len(ramp) - 1
            self.put((i, j), ramp[idx])
            if glow:
                self.glow.add((i, j))
        if rim:
            for p in m:
                self.rim[p] = ramp[0] if rim is True else rim
        return m

    def dot(self, x, y, col, size=1.0, glow=False, a=255):
        """A square of `size` units whose top-left corner is unit (x, y)."""
        k = self.k
        n = max(1, int(round(size * k)))
        i0, j0 = int(math.floor(x * k + 1e-6)), int(math.floor(y * k + 1e-6))
        for di in range(n):
            for dj in range(n):
                self.put((i0 + di, j0 + dj), col, a)
                if glow:
                    self.glow.add((i0 + di, j0 + dj))

    def fine(self, x, y, col, glow=False):
        """A single pixel at unit (x, y), whatever the resolution: for hairline details."""
        p = (int(math.floor(x * self.k + 1e-6)), int(math.floor(y * self.k + 1e-6)))
        self.put(p, col)
        if glow:
            self.glow.add(p)

    def line(self, pts, col, r=0.5, glow=False):
        return self.fill(self.path(pts, r), col, glow=glow)

    def glyph(self, rows, x, y, cols, glow=False):
        """A small pixel motif given in 16-res rows ('.' is empty, other characters index cols)."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != "." and ch in cols:
                    self.dot(x + i, y + j, cols[ch], glow=glow and ch in "#*")

    def edge(self, m, col, sides=("r", "b"), only_inside=None):
        """Darkens the pixels of m that border the outside of m on the given sides (an inner shadow line)."""
        dirs = {"r": (1, 0), "l": (-1, 0), "b": (0, 1), "t": (0, -1)}
        out = []
        for (i, j) in m:
            for s in sides:
                di, dj = dirs[s]
                if (i + di, j + dj) not in m and (only_inside is None or (i + di, j + dj) in only_inside):
                    out.append((i, j))
                    break
        for p in out:
            self.put(p, col)
        return out

    def outline(self, rim_override=None, corners=False):
        add = {}
        nb = ((1, 0), (-1, 0), (0, 1), (0, -1)) + (((1, 1), (-1, -1), (1, -1), (-1, 1)) if corners else ())
        for j in range(self.H):
            for i in range(self.W):
                if (i, j) in self.px:
                    continue
                best = None
                for di, dj in nb:
                    q = (i + di, j + dj)
                    if q in self.px and q in self.rim:
                        c = self.rim[q]
                        if best is None or sum(c) < sum(best):
                            best = c
                if best is not None:
                    add[(i, j)] = rim_override or best
        for p, c in add.items():
            self.put(p, c)

    def image(self):
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        for (i, j), c in self.px.items():
            img.putpixel((i, j), c)
        return img

    def glow_image(self):
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        for p in self.glow:
            if p in self.px:
                img.putpixel(p, self.px[p])
        return img


# =================================================================== normal fields
def n_sphere(cx, cy, rx, ry=None, flat=0.0):
    ry = ry or rx

    def f(x, y):
        nx, ny = (x - cx) / rx, (y - cy) / ry
        q = nx * nx + ny * ny
        if q > 1:
            s = 1 / math.sqrt(q)
            nx, ny, q = nx * s, ny * s, 1.0
        nz = math.sqrt(max(0.0, 1 - q)) + flat
        L = math.sqrt(nx * nx + ny * ny + nz * nz)
        return nx / L, ny / L, nz / L
    return f


def n_cyl(cx, rx, tilt=0.0):
    def f(x, y):
        nx = clamp((x - cx) / rx, -1, 1)
        nz = math.sqrt(max(0.0, 1 - nx * nx))
        return nx * 0.95, tilt, nz
    return f


def n_flat(nx=0.0, ny=0.0):
    L = math.sqrt(nx * nx + ny * ny + 1)
    return lambda x, y: (nx / L, ny / L, 1 / L)


def n_bevel(spr, m, depth=1.4, flat=0.25):
    """Normals of a pillow-shaped part: flat in the middle, curving down within `depth` units of the border."""
    k = spr.k
    dist = {}
    rad = int(math.ceil(depth * k)) + 1
    border = [p for p in m if any((p[0] + a, p[1] + b) not in m for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for p in m:
        best = rad
        for q in border:
            d = abs(p[0] - q[0]) + abs(p[1] - q[1])
            if d < best:
                best = d
        dist[p] = best

    def h(p):
        d = dist.get(p)
        if d is None:
            return 0.0
        return min(1.0, (d + 0.5) / (depth * k))

    cache = {}
    for p in m:
        gx = h((p[0] + 1, p[1])) - h((p[0] - 1, p[1]))
        gy = h((p[0], p[1] + 1)) - h((p[0], p[1] - 1))
        nx, ny, nz = -gx * 1.1, -gy * 1.1, flat + 0.6
        L = math.sqrt(nx * nx + ny * ny + nz * nz)
        cache[p] = (nx / L, ny / L, nz / L)

    def f(x, y):
        return cache.get((int(x * k), int(y * k)), (0, 0, 1))
    return f


# =================================================================== world glyphs (16-res rows)
GLYPHS = {
    0: [".#.#.", "#####", ".#y#.", "l.#.l", ".lgl."],   # a bouquet: berries over leaves
    1: [".###.", "#####", "#g#g#", "..#..", ".###."],   # a toadstool
    2: ["..#..", ".##..", ".###.", "##g##", ".###."],   # a flame
    3: [".###.", "##g##", ".#g#.", ".#g#.", ".###."],   # a keyhole plate
    4: ["...##", "..##.", ".####", ".##..", "##..."],   # a lightning bolt
    5: [".....", ".###.", "##g##", ".###.", "....."],   # an open eye
    6: ["#####", ".###.", "..#..", ".###.", "#####"],   # two mirrored triangles
    7: ["...#.", "..#.#", ".....", "#..#.", ".##.#"],   # bubbles over a wave
    8: ["...##", "..###", ".###.", "##g..", "#...."],   # a leaf
    9: [".#.#.", "#####", "#g###", ".###.", "..#.."],   # a beating heart of stone
    10: ["#####", ".g#g.", ".###.", ".g#g.", "#####"],  # a thread spool
    11: ["..#..", ".#g#.", "#ggg#", ".#g#.", "..#.."],  # the Artisan's star
}


def glyph(spr, w, x, y, col, dark, glow=False):
    spr.glyph(GLYPHS[w], x, y, {"#": col, "g": dark, "l": (70, 120, 40), "y": GOLD[4]}, glow=glow)


# =================================================================== dolls
def doll(spr, cx, base, h, body, *, second=None, trim=GOLD, apron=None, motif=None, motif_col=None, crack=False,
         faded=False, face=True, joint=True, open_top=False, bands=True):
    """A painted matryoshka seen from the front, standing on `base`, `h` units tall. body is its lacquer ramp."""
    rh = h * 0.225
    hy = base - h + rh + 0.15
    by, brx, bry = base - h * 0.31, h * 0.34, h * 0.36
    my, mrx, mry = base - h * 0.6, h * 0.25, h * 0.2
    cut = base

    def inside(x, y):
        if y > cut:
            return False
        if ((x - cx) / brx) ** 2 + ((y - by) / bry) ** 2 <= 1:
            return True
        if ((x - cx) / mrx) ** 2 + ((y - my) / mry) ** 2 <= 1:
            return True
        return ((x - cx) / rh) ** 2 + ((y - hy) / rh) ** 2 <= 1
    m = spr.mask(inside)
    if open_top:
        m = {p for p in m if (p[1] + 0.5) / spr.k > base - h * 0.48}
    nb = n_sphere(cx - 0.2, by - 0.6, brx * 1.05, bry * 1.15)
    nh = n_sphere(cx - 0.1, hy, rh * 1.1, rh * 1.1)
    head_cut = base - h * 0.62

    def normal(x, y):
        return nh(x, y) if y < head_cut else nb(x, y)
    if faded:
        body = [mix(c, (150, 140, 130), 0.55) for c in body]
    spr.shade(m, body, normal, lo=1, spec=0.07)
    # the face: cream oval set in the scarf, a fringe of hair, two eyes and rosy cheeks
    if face and not open_top:
        fr_x, fr_y, fy = rh * 0.7, rh * 0.66, hy + rh * 0.14
        if h >= 12.5:
            # the scarf's painted rim around the face
            frame = spr.ell(cx, fy, fr_x + 0.9, fr_y + 0.9)
            spr.fill(frame, (second[3] if second else body[4]) if not faded else (150, 140, 130))
        fm = spr.ell(cx, fy, fr_x, fr_y)
        skin = SKIN if not faded else [mix(c, (170, 160, 150), 0.5) for c in SKIN]
        spr.shade(fm, skin, n_sphere(cx - 0.3, fy - 0.3, fr_x * 1.6, fr_y * 1.6), rim=False, lo=2, hi=4)
        hair = spr.mask(lambda x, y: ((x - cx) / fr_x) ** 2 + ((y - fy) / fr_y) ** 2 <= 1 and y < fy - fr_y * 0.42 + abs(x - cx) * 0.25)
        spr.fill(hair, (92, 50, 30))
        ey = fy + fr_y * 0.05
        if h >= 11:
            spr.dot(cx - fr_x * 0.55, ey, INK)
            spr.dot(cx + fr_x * 0.55 - 1, ey, INK)
            if spr.res >= 32:
                spr.fine(cx - fr_x * 0.55 - 0.5, ey + 1.0, CHEEK)
                spr.fine(cx + fr_x * 0.55 + 0.5 - 1, ey + 1.0, CHEEK)
                spr.fine(cx - 0.25, ey + 1.5, (190, 40, 40))
                spr.fine(cx + 0.25, ey + 1.5, (190, 40, 40))
        else:
            spr.dot(cx - 1.0, ey, INK)
            spr.dot(cx, ey, INK)
    # the joint where the two halves nest: a dark seam under a gold fillet
    jy = base - h * 0.47
    if joint:
        seam = {p for p in m if abs((p[1] + 0.5) / spr.k - jy) < 0.5 / spr.k + 0.01}
        if spr.res >= 32 or h >= 12:
            spr.fill(seam, body[0])
            above = {(i, j - 1) for (i, j) in seam if (i, j - 1) in m}
            spr.fill(above, trim[4] if not faded else mix(trim[4], (160, 150, 140), 0.5))
    # the apron (painted front), with the world's motif
    if apron is not False:
        ay, arx, ary = base - h * 0.25, brx * 0.74, bry * 0.58
        am = spr.ell(cx, ay, arx, ary)
        am = {p for p in am if p in m}
        ap = apron or PAPER
        if faded:
            ap = [mix(c, (170, 160, 150), 0.5) for c in ap]
        spr.shade(am, ap, n_sphere(cx - 0.6, ay - 0.8, arx * 1.8, ary * 1.8), rim=False, lo=3, hi=4)
        ring = spr.edge(am, trim[2], sides=("r", "b", "l", "t"))
        if motif is not None:
            gx = cx - 2.5
            gy = ay - 2.5
            glyph(spr, motif, round(gx), round(gy), motif_col or body[2], body[0])
    # gold band at the hem
    if bands:
        hem = {p for p in m if base - 1.0 <= (p[1] + 0.5) / spr.k < base}
        spr.fill(hem, lambda p: trim[3] if (p[0] // max(1, int(spr.k))) % 3 else trim[5])
    if crack:
        spr.line([(cx - 2.2, base - h + 2.5), (cx - 0.6, base - h * 0.62), (cx + 0.8, base - h * 0.5), (cx - 0.4, base - h * 0.3), (cx + 1.2, base - 1.5)],
                 (26, 16, 14), r=0.42)
    return m


# =================================================================== item recipes
# the glyph's colour when painted on a cream apron: the world's strongest readable tone
MOTIF_COL = {0: RED[3], 1: hx("5a8a1e"), 2: hx("e0601a"), 3: hx("3a8ac8"), 4: hx("e8b81a"), 5: hx("3a4ab8"), 6: hx("b040c8"),
             7: hx("1a8aa0"), 8: hx("d06a20"), 9: hx("a83a2a"), 10: hx("2a5ab0"), 11: RED[2]}

def it_hidden_doll(res, w, rank):
    """A hidden doll: the world's lacquer and glyph; its height grows with its rank in the nest (smallest inside)."""
    st = style(w)
    s = Spr(res)
    h = 9.0 + rank * 0.62
    doll(s, 8, 15.5, h, st["body"], second=st["second"], motif=w if h >= 11.5 else None, motif_col=MOTIF_COL[w])
    if h < 11.5:
        # too small for the glyph: a single bead of the world's light on the apron
        ay = 15.5 - h * 0.24
        s.dot(7.5 - 0.5, ay - 0.5, st["glow"][4])
        s.dot(8.5 - 0.5, ay - 0.5, st["glow"][2])
    s.outline()
    return s


def it_whole_matryoshka(res):
    s = Spr(res)
    doll(s, 8, 15.5, 15.2, RED, motif=0, motif_col=RED[3])
    # gold scrollwork on the shoulders
    for sx in (-1, 1):
        s.line([(8 + sx * 3.2, 7.4), (8 + sx * 4.4, 8.6), (8 + sx * 4.2, 10.0)], GOLD[4], r=0.42)
    s.outline()
    for (x, y) in ((1.2, 2.0), (13.6, 4.2), (2.4, 12.6)):
        s.dot(x, y, GOLD[5])
    return s


def it_nested_dolls(res):
    """An opened doll: its lower half, with the next doll standing inside, the lid set down beside it."""
    s = Spr(res)
    # the lid lying to the right, seen tipped
    lid = s.ell(12.2, 5.4, 2.6, 2.4) | s.ell(12.2, 7.6, 3.0, 1.4)
    lid = {p for p in lid if (p[1] + 0.5) / s.k < 8.6}
    s.shade(lid, RED, n_sphere(11.6, 5.2, 3.2, 3.0), spec=0.05)
    s.fill({p for p in lid if abs((p[1] + 0.5) / s.k - 8.1) < 0.5}, GOLD[4])
    # the inner doll
    st = style(1)
    doll(s, 6.0, 12.4, 10.5, st["body"], motif=None, bands=False)
    # the lower half of the big doll in front of it
    base, h, cx = 15.6, 13.0, 6.0
    lower = s.mask(lambda x, y: ((x - cx) / (h * 0.36)) ** 2 + ((y - (base - h * 0.32)) / (h * 0.36)) ** 2 <= 1 and base - h * 0.42 <= y <= base)
    s.shade(lower, RED, n_sphere(cx - 0.3, base - h * 0.4, h * 0.4, h * 0.38), spec=0.05)
    s.fill({p for p in lower if (p[1] + 0.5) / s.k < base - h * 0.42 + 0.75}, GOLD[4])
    am = s.ell(cx, base - 2.6, 2.6, 1.6)
    s.shade(am, PAPER, n_sphere(cx - 0.4, base - 3.2, 4.0, 3.0), rim=False, lo=2, hi=4)
    s.edge(am, GOLD[2], sides=("r", "b", "l", "t"))
    s.dot(cx - 0.5, base - 3.0, RED[3])
    s.outline()
    return s


def it_life_doll(res):
    s = Spr(res)
    doll(s, 8, 15.5, 14.0, RED, motif=None)
    # a heart on the apron, and a thin gold halo over the head
    s.glyph([".#.#.", "#####", "#####", ".###.", "..#.."], 5.5, 10.4, {"#": (214, 36, 40)})
    s.dot(6.5, 10.4, (255, 150, 140))
    s.outline()
    halo = s.ring(8, 4.2, 4.2, 5.0)
    halo = {p for p in halo if (p[1] + 0.5) / s.k < 2.4}
    s.fill(halo, GOLD[4])
    return s


def it_chance_doll(res):
    s = Spr(res)
    body = hramp("6a3a9a")
    doll(s, 8, 15.5, 11.5, body, motif=None)
    # three dice pips on a gold apron
    for (x, y) in ((6.6, 10.6), (7.6, 11.6), (8.6, 12.6)):
        s.dot(x, y, GOLD[5])
    s.outline()
    return s


def it_cracked_doll(res):
    s = Spr(res)
    doll(s, 8, 15.5, 13.5, RED, motif=0, faded=True, crack=True, motif_col=(150, 120, 110))
    s.outline()
    return s


def it_refuge_doll(res):
    s = Spr(res)
    st = style(3)
    doll(s, 8, 15.5, 14.0, st["body"], motif=None)
    # a little lit doorway on the apron: the pocket base inside
    door = s.poly([(6.5, 13.4), (6.5, 11.0), (8.0, 9.8), (9.5, 11.0), (9.5, 13.4)])
    s.fill(door, (40, 28, 26))
    s.fill(s.rect(7.0, 11.2, 9.0, 13.4), GOLD[4], glow=True)
    s.dot(7.0, 11.2, GOLD[5], glow=True)
    s.outline()
    return s


# =================================================================== preview helpers
def sheet(sprites, scale=8, cols=None, bg=(52, 54, 60), extra=None, gap=1):
    """Lays sprites side by side, upscaled; `extra` are additional images (e.g. a vanilla item for scale)."""
    imgs = [sp.image() if isinstance(sp, Spr) else sp for sp in sprites] + list(extra or [])
    if not imgs:
        return Image.new("RGBA", (8, 8), bg + (255,))
    cols = cols or len(imgs)
    w = max(i.width for i in imgs)
    h = max(i.height for i in imgs)
    cell = (w + gap * 2) * scale
    rows = (len(imgs) + cols - 1) // cols
    out = Image.new("RGBA", (cols * cell, rows * (h + gap * 2) * scale), bg + (255,))
    for n, im in enumerate(imgs):
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        x = (n % cols) * cell + gap * scale + (w - im.width) * scale // 2
        y = (n // cols) * (h + gap * 2) * scale + gap * scale + (h - im.height) * scale // 2
        out.alpha_composite(big, (x, y))
    return out


from content import NEST_ORDER as NEST  # noqa: E402


def prev_dolls(res):
    return [it_hidden_doll(res, w, NEST.index(w)) for w in range(1, 11)] + [
        it_whole_matryoshka(res), it_nested_dolls(res), it_life_doll(res), it_chance_doll(res), it_cracked_doll(res), it_refuge_doll(res)]


# =================================================================== cores, seeds
def it_core(res, w):
    """A boss core: a lacquered shell in the world's colour, caged in gold, its heart glowing through a window."""
    st = style(w)
    s = Spr(res)
    cx, cy, r = 8.0, 8.8, 5.7
    shell = s.disc(cx, cy, r)
    ns = n_sphere(cx - 0.4, cy - 0.5, r * 1.02)
    s.shade(shell, st["body"], ns, spec=0.06)
    # the gold cage: two meridians and the equator, shaded with the sphere
    cage = s.mask(lambda x, y: (abs(((x - cx) / (r * 0.55)) ** 2 + ((y - cy) / r) ** 2 - 1) < 0.22 or abs(y - cy - 0.2) < 0.55)
                  and (x - cx) ** 2 + (y - cy) ** 2 <= r * r)
    s.shade(cage, GOLD, ns, rim=False, lo=1, hi=4, spec=0.05)
    # the window and the heart of light
    win = s.disc(cx, cy + 0.2, 2.45)
    s.fill(win, GOLD[1])
    heart = s.disc(cx, cy + 0.2, 1.85)
    s.shade(heart, st["glow"], n_sphere(cx - 0.6, cy - 0.4, 2.2), rim=False, lo=2, hi=5, glow=True)
    s.dot(cx - 1.0, cy - 0.8, (255, 255, 250), glow=True)
    # the crown that holds it
    crown = s.poly([(5.9, 3.6), (6.4, 2.0), (7.3, 2.9), (8.0, 1.2), (8.7, 2.9), (9.6, 2.0), (10.1, 3.6)])
    s.shade(crown, GOLD, n_flat(-0.2, -0.3), lo=2, hi=4)
    s.dot(7.5, 1.3, GOLD[5])
    s.outline()
    return s


def it_seed(res, w):
    """A World Seed: a lacquered kernel painted with the world's bands, set in a gold cup, sprouting."""
    st = style(w)
    s = Spr(res)
    cx = 7.6
    kernel = s.ell(cx, 9.6, 4.3, 4.6) | s.poly([(cx - 3.7, 8.2), (cx, 2.6), (cx + 3.7, 8.2)])
    kernel = {p for p in kernel if (p[1] + 0.5) / s.k < 14.6}
    s.shade(kernel, st["body"], n_sphere(cx - 0.5, 8.4, 4.6, 6.0), spec=0.06)
    # two painted bands that follow the kernel's curve
    bands = s.mask(lambda x, y: any(abs((y - c) - 0.18 * (x - cx) ** 2) < 0.55 for c in (7.0, 9.6)))
    bands &= kernel
    s.shade(bands, st["second"], n_sphere(cx - 0.5, 8.4, 4.6, 6.0), rim=False, lo=2, hi=4)
    # a bead of the world's light on the husk
    s.dot(cx + 1.2, 11.2, st["glow"][4], glow=True)
    s.dot(cx + 1.2, 12.0, st["glow"][2], glow=True)
    # the gold cup
    cup = s.mask(lambda x, y: ((x - cx) / 4.6) ** 2 + ((y - 11.8) / 3.4) ** 2 <= 1 and y >= 11.9)
    s.shade(cup, GOLD, n_sphere(cx - 0.8, 11.2, 4.8, 3.6), lo=1, hi=4)
    for i in range(5):
        s.dot(cx - 3.0 + i * 1.5, 13.0, GOLD[1])
    # the sprout
    leaf = s.path([(cx, 3.4), (cx + 1.0, 1.8), (cx + 2.6, 1.2)], 0.55) | s.ell(cx + 3.2, 1.6, 1.5, 0.9)
    s.shade(leaf, hramp("5a9a3a", n=5), n_flat(-0.3, -0.5), lo=1, hi=3)
    s.outline()
    return s


# =================================================================== writing: scroll, journal, pages
def _ink_lines(s, x0, x1, ys, col, seed=1):
    for n, y in enumerate(ys):
        x = x0
        h = seed * 7 + n * 13
        while x < x1:
            ln = 1.0 + ((h * 5 + int(x * 3)) % 3)
            s.fill(s.rect(x, y, min(x1, x + ln), y + 0.5 if s.res >= 32 else y + 1), col)
            x += ln + 1.0
            h += 3


def _rod(y0):
    return lambda x, y: (0.0, clamp((y - y0 - 0.9) / 0.9, -1, 1) * 0.9, 0.45)


def it_scroll(res, blank=False):
    s = Spr(res)
    sheet = s.rect(3.6, 3.4, 12.4, 12.8)
    s.shade(sheet, PAPER, n_bevel(s, sheet, 1.2), lo=2, hi=4)
    if not blank:
        _ink_lines(s, 5.0, 11.0, (5.0, 6.8, 8.6, 10.4), (110, 70, 50))
    for y0 in (2.0, 12.4):
        rod = s.rect(2.6, y0, 13.4, y0 + 1.8)
        s.shade(rod, WOOD, _rod(y0), lo=1, hi=4)
        for x in (1.6, 13.4):
            knob = s.rect(x, y0 + 0.2, x + 1.0, y0 + 1.6)
            s.shade(knob, GOLD, n_flat(-0.2, -0.3), lo=2, hi=4)
    if not blank:
        seal = s.disc(11.2, 11.6, 1.8)
        s.shade(seal, RED, n_sphere(10.6, 11.0, 2.2), lo=1, hi=4, spec=0.05)
        s.dot(10.7, 11.0, GOLD[4])
    else:
        rib = s.rect(7.4, 3.4, 8.6, 12.8)
        s.fill(rib, (236, 228, 214))
    s.outline()
    return s


def it_journal(res):
    s = Spr(res)
    pages = s.rect(4.2, 2.6, 13.6, 14.6)
    s.fill(pages, PAPER[4], rim=PAPER[0])
    for y in range(3, 14, 2):
        s.fill(s.rect(12.6, y + 0.2, 13.6, y + 0.7 if res >= 32 else y + 1), PAPER[2])
    cover = s.rect(2.4, 1.6, 12.6, 14.0)
    s.shade(cover, RED, n_bevel(s, cover, 1.3), lo=1, hi=4)
    spine = s.rect(2.4, 1.6, 4.0, 14.0)
    s.shade(spine, RED, lambda x, y: (-0.8, 0.0, 0.6), rim=False, lo=1, hi=3)
    for y in (3.4, 12.0):
        s.fill(s.rect(2.4, y, 4.0, y + 0.7), GOLD[3])
    # gold corners and the doll emblem
    for (x, y) in ((11.0, 1.6), (11.0, 12.6)):
        s.fill(s.rect(x, y, 12.6, y + 1.4), GOLD[3])
    emb = s.disc(8.3, 5.6, 1.4) | s.ell(8.3, 8.8, 2.1, 2.3)
    s.shade(emb, GOLD, n_sphere(7.8, 6.4, 2.4, 3.2), rim=False, lo=2, hi=5)
    s.dot(7.8, 5.2, SKIN[3])
    s.dot(8.0, 9.0, RED[2])
    # the ribbon bookmark
    rib = s.rect(9.6, 14.0, 10.6, 15.8)
    s.fill(rib, GOLD[3], rim=GOLD[0])
    s.outline()
    return s


def it_page(res):
    s = Spr(res)
    sheet = s.poly([(3.4, 2.4), (12.0, 2.0), (12.8, 5.0), (12.2, 7.0), (13.0, 9.6), (12.4, 13.6), (3.8, 14.2)])
    s.shade(sheet, PAPER, n_bevel(s, sheet, 1.0), lo=2, hi=4)
    corner = s.poly([(3.4, 2.4), (6.0, 2.3), (3.5, 4.8)])
    s.fill(corner & sheet, PAPER[1])
    _ink_lines(s, 5.2, 11.2, (5.2, 7.0, 8.8, 10.6), (110, 70, 50), seed=3)
    s.fill(s.disc(10.4, 12.2, 1.2), RED[3])
    s.dot(9.9, 11.7, RED[5])
    s.outline()
    return s


# =================================================================== offerings
def it_shackle(res):
    st = style(3)
    s = Spr(res)
    cuff = s.ring(6.2, 6.4, 2.4, 4.5)
    s.shade(cuff, IRON, n_sphere(5.6, 5.8, 5.0), spec=0.05)
    hinge = s.rect(5.0, 1.2, 7.4, 2.8)
    s.shade(hinge, IRON, n_flat(-0.3, -0.3), lo=1, hi=3)
    # the lock, glowing with the dungeon's cold light
    lock = s.rect(7.8, 7.8, 11.0, 11.0)
    s.shade(lock, IRON, n_bevel(s, lock, 1.0), lo=1, hi=4)
    s.fill(s.rect(9.0, 8.8, 10.0, 10.2), st["glow"][3], glow=True)
    # the chain
    for i, (x, y) in enumerate(((11.4, 11.4), (12.6, 12.6), (13.8, 13.8))):
        link = s.ring(x, y, 0.4, 1.0) if i % 2 == 0 else s.ell(x, y, 1.1, 0.6)
        s.shade(link, IRON, n_flat(-0.3, -0.3), lo=1, hi=4)
    s.outline()
    return s


def it_censer(res):
    st = style(4)
    s = Spr(res)
    s.line([(8.0, 0.4), (8.0, 4.0)], IRON[2], r=0.5)
    for y in (1.0, 2.6):
        s.dot(7.5, y, IRON[4])
    bowl = s.ell(8.0, 9.6, 4.8, 4.0)
    bowl = {p for p in bowl if (p[1] + 0.5) / s.k > 6.4}
    lid = s.ell(8.0, 6.4, 3.6, 2.4)
    body = bowl | lid
    s.shade(body, GOLD, n_sphere(7.4, 8.0, 5.0, 4.6), spec=0.05)
    s.fill({p for p in body if abs((p[1] + 0.5) / s.k - 7.4) < 0.5}, GOLD[1])
    # storm light leaking through three vents
    for x in (5.6, 7.6, 9.6):
        s.fill(s.rect(x, 9.0, x + 1.0, 11.0), st["glow"][3], glow=True)
        s.dot(x, 9.0, st["glow"][5], glow=True)
    foot = s.rect(6.4, 13.2, 9.6, 14.8)
    s.shade(foot, GOLD, n_flat(-0.2, -0.3), lo=1, hi=3)
    s.outline()
    for (x, y) in ((2.4, 4.2), (13.0, 3.0), (12.4, 6.6)):
        s.dot(x, y, st["glow"][4], glow=True)
    return s


def it_wreath(res):
    s = Spr(res)
    seasons = (hramp("6ab04a", n=5), hramp("e8b83a", n=5), hramp("d8602a", n=5), hramp("dce8f4", n=5, dl=0.06))
    ring = s.ring(8, 8, 3.2, 6.4)
    for q in range(4):
        part = {p for p in ring if (0 if (p[0] + 0.5) / s.k >= 8 else 1) + (0 if (p[1] + 0.5) / s.k < 8 else 2) == q}
        s.shade(part, seasons[(0, 3, 1, 2)[q]], n_sphere(7.4, 7.4, 7.2), lo=1, hi=3)
    for a in range(0, 360, 30):
        x, y = 8 + 4.8 * math.cos(math.radians(a)), 8 + 4.8 * math.sin(math.radians(a))
        s.dot(x - 0.5, y - 0.5, (40, 40, 30) if a % 60 else (255, 255, 240), a=110 if a % 60 else 160)
    for (x, y) in ((7.5, 1.2), (13.8, 7.5), (7.5, 13.8), (1.2, 7.5)):
        s.dot(x, y, GOLD[4])
    # the red ribbon tying it at the bottom
    s.fill(s.poly([(6.6, 12.6), (9.4, 12.6), (10.4, 15.6), (8.0, 14.0), (5.6, 15.6)]), RED[3], rim=RED[0])
    s.outline()
    return s


def it_effigy(res):
    s = Spr(res)
    m = doll(s, 8, 15.5, 14.4, RED, motif=None, bands=False)
    # the right half is bare wood: the brush strokes stop halfway
    bare = {p for p in m if (p[0] + 0.5) / s.k > 8.4}
    s.shade(bare, WOOD, n_sphere(7.6, 9.0, 5.4, 7.0), lo=1, hi=4)
    for y in range(4, 15, 2):
        s.dot(8.4, y, RED[2])
    # a thread still hangs from it
    s.line([(11.6, 6.4), (13.2, 9.0), (12.6, 12.6), (14.0, 15.2)], (236, 226, 206), r=0.4)
    s.outline()
    return s


# =================================================================== snorkel helmets
SNORKEL_STYLE = {
    "salt_snorkel": (hramp("c8ccc2"), hramp("9ab0b4"), IRON),
    "nacre_snorkel": (hramp("e0c4d8"), hramp("a8e0e0"), GOLD),
    "cobalt_snorkel": (hramp("2a4aa0"), hramp("3a7ae0"), GOLD),
    "pearl_snorkel": (hramp("9ae4f0"), hramp("1ab0b0"), hramp("f4f8fa")),
}


def _tube(x, y):
    return (0.6 if x > 13.6 else -0.5, 0.0, 0.7)


def it_snorkel(res, sid):
    shell, tube, trim = SNORKEL_STYLE[sid]
    s = Spr(res)
    dome = s.disc(7.4, 8.4, 5.6)
    dome = {p for p in dome if (p[1] + 0.5) / s.k < 13.4}
    s.shade(dome, shell, n_sphere(6.8, 7.6, 6.0), spec=0.06)
    collar = s.rect(2.2, 12.4, 12.6, 14.4)
    s.shade(collar, trim, n_bevel(s, collar, 0.8), lo=1, hi=4)
    for x in (3.4, 7.0, 10.6):
        s.dot(x, 13.0, trim[5])
    port = s.disc(7.4, 8.6, 3.0)
    s.fill(port, trim[2], rim=trim[0])
    glass = s.disc(7.4, 8.6, 2.3)
    s.shade(glass, hramp("4ab8d8"), n_sphere(6.4, 7.6, 3.2), rim=False, lo=1, hi=4)
    s.dot(6.2, 7.4, (240, 255, 255))
    s.dot(7.2, 7.0, (200, 240, 250))
    for (x, y) in ((4.4, 5.4), (9.8, 5.4), (4.4, 11.0), (9.8, 11.0)):
        s.dot(x, y, trim[4])
    # the breathing tube, up the right side
    t = s.path([(12.0, 9.0), (13.6, 7.6), (13.8, 3.0)], 0.75)
    s.shade(t, tube, _tube, lo=1, hi=3)
    for y in (3.6, 5.2, 6.8):
        s.dot(13.0, y, tube[1])
    s.fill(s.rect(12.6, 1.4, 15.0, 2.8), trim[3], rim=trim[0])
    if sid == "pearl_snorkel":
        s.fill(s.disc(7.4, 2.6, 1.2), (250, 252, 255), rim=(120, 150, 170))
    if sid == "salt_snorkel":
        for (x, y) in ((3.0, 7.0), (5.0, 3.6), (11.4, 10.0)):
            s.dot(x, y, (250, 250, 244))
    s.outline()
    return s


def prev_misc(res):
    out = [it_core(res, w) for w in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)]
    out += [it_seed(res, w) for w in range(1, 11)]
    out += [it_scroll(res), it_scroll(res, True), it_journal(res), it_page(res)]
    out += [it_shackle(res), it_censer(res), it_wreath(res), it_effigy(res)]
    out += [it_snorkel(res, k) for k in SNORKEL_STYLE]
    return out


# =================================================================== gear: armor icons
ARMOR_ROWS = {
    "helmet": ["", "", "", "....########", "...##########", "..############", "..############", "..####....####",
               "..###......###", "..###......###"],
    "chestplate": ["", "..####....####", ".#####....#####", ".##############", ".##############", "..############",
                   "...##########", "...##########", "...##########", "...##########", "...##########", "...##########",
                   "....########"],
    "leggings": ["", "", "...##########", "...##########", "...##########", "...####..####", "...####..####",
                 "...###....###", "...###....###", "...###....###", "...###....###", "...###....###", "...###....###",
                 "...###....###"],
    "boots": ["", "", "", "", "", "", "", "...###....###", "...###....###", "...###....###", "...###....###",
              "..####...####", "..####...####", "..####...####"],
}

# per set: plate ramp, trim ramp, accent (glowing seams or gems), style of the detail
ARMOR_STYLE = {
    "chitin": (hramp("4e8a34"), hramp("7c4a9c"), hramp("b7e04a"), "plates"),
    "thermal": (hramp("4a3a34"), GOLD, hramp("ff8a2a"), "seams"),
    "jailer": (hramp("7a8292"), IRON, hramp("7fd3ff"), "rivets"),
    "celestial": (hramp("d4e2f4", dl=0.08), GOLD, hramp("ffe14a"), "star"),
    "nocturnal": (hramp("262e4c", dl=0.09), hramp("3a4a8a"), hramp("6a8aff"), "glints"),
    "mirror": (hramp("d4b4e6"), hramp("4ac8c0"), hramp("f4eefa"), "mirror"),
    "diving": (hramp("1e4c8a"), GOLD, hramp("9af0ff"), "ports"),
    "seasonal": (hramp("c89a3c"), hramp("d86a2a"), hramp("6aa040"), "leaf"),
    "living_rock": (hramp("7a5040"), hramp("5a3a2e"), hramp("ffa050"), "cracks"),
    "artisan": (RED, GOLD, hramp("f6d68a"), "ornament"),
}


def _rows_mask(s, rows):
    m = set()
    k = int(s.k)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                for a in range(k):
                    for b in range(k):
                        m.add((i * k + a, j * k + b))
    return m


def it_armor(res, set_id, piece):
    plate, trim, acc, kind = ARMOR_STYLE[set_id]
    s = Spr(res)
    m = _rows_mask(s, ARMOR_ROWS[piece])
    s.shade(m, plate, n_bevel(s, m, 2.2, flat=0.35), lo=1, spec=0.0)
    ys = sorted({p[1] for p in m})
    top = ys[0]
    k = s.k
    # a trim band along the top edge of the piece
    band = {p for p in m if p[1] < top + max(1, int(k))}
    s.fill(band, trim[3])
    s.fill({p for p in band if (p[0] // max(1, int(k))) % 3 == 0}, trim[4])
    bottom = {p for p in m if p[1] >= ys[-1] - max(1, int(k)) + 1}
    s.fill(bottom, plate[1])
    u = lambda v: v  # noqa: E731
    if kind == "plates":
        for y in (6.0, 9.0, 12.0):
            s.fill({p for p in m if abs((p[1] + 0.5) / k - y) < 0.5 / k + 0.01}, trim[2])
    elif kind == "seams":
        for (x, y) in ((6.0, 6.0), (7.0, 7.0), (9.0, 6.0), (8.0, 8.0), (7.0, 10.0), (10.0, 9.0)):
            if (int(x * k), int(y * k)) in m:
                s.dot(x, y, acc[3], glow=True)
    elif kind == "rivets":
        for p in sorted(m):
            if (p[0] // int(k)) % 4 == 1 and (p[1] // int(k)) % 4 == 2:
                s.dot(p[0] / k, p[1] / k, IRON[5], size=1.0 / k)
    elif kind == "star":
        if piece in ("chestplate", "leggings"):
            s.glyph(["..#..", ".###.", "..#.."], 6.0, 5.0 if piece == "chestplate" else 3.0, {"#": acc[3]})
    elif kind == "glints":
        for (x, y) in ((5.0, 5.0), (10.0, 7.0), (7.0, 10.0), (11.0, 11.0)):
            if (int(x * k), int(y * k)) in m:
                s.dot(x, y, acc[4], glow=True)
    elif kind == "mirror":
        s.fill({p for p in m if 0 <= (p[0] - p[1]) / k + 2 < 2.2}, trim[3])
        s.fill({p for p in m if 0 <= (p[0] - p[1]) / k + 2 < 0.9}, acc[4])
    elif kind == "ports":
        for (x, y) in ((6.0, 6.0), (9.0, 6.0), (7.5, 9.5)):
            if (int((x + 0.5) * k), int((y + 0.5) * k)) in m:
                s.dot(x, y, GOLD[3])
                s.dot(x, y, acc[3], size=0.5 if res >= 32 else 1.0)
    elif kind == "leaf":
        cols = (hx("6ab04a"), hx("e8b83a"), hx("d8602a"), hx("e8eef8"))
        for i, (x, y) in enumerate(((5.0, 6.0), (9.0, 6.0), (6.0, 9.0), (10.0, 10.0))):
            if (int((x + 0.5) * k), int((y + 0.5) * k)) in m:
                s.dot(x, y, cols[i])
    elif kind == "cracks":
        s.line([(5.0, 5.0), (7.0, 7.4), (6.4, 9.4), (8.6, 11.8)], acc[3], r=0.35, glow=True)
        s.fill({p for p in s.path([(5.0, 5.0), (7.0, 7.4), (6.4, 9.4), (8.6, 11.8)], 0.35) if p not in m}, (0, 0, 0), a=0)
        for p in list(s.px):
            if s.px[p][3] == 0:
                del s.px[p]
    elif kind == "ornament":
        for (x, y) in ((5.0, 6.0), (10.0, 6.0), (7.5, 9.0)):
            if (int((x + 0.5) * k), int((y + 0.5) * k)) in m:
                s.dot(x, y, GOLD[4])
                s.dot(x + 0.5 if res >= 32 else x, y + 1, GOLD[2], size=0.5 if res >= 32 else 1.0)
    s.outline()
    return s


# =================================================================== gear: weapons
def _blade(s, p0, p1, w0, w1, ramp, tip=True, glow=False):
    """A straight blade from p0 (hilt) to p1 (tip): its upper-left half catches the light, the other half is shaded."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    pts = [(p0[0] + nx * w0, p0[1] + ny * w0)]
    end = (p1[0] - ux * (w1 * 1.6 if tip else 0), p1[1] - uy * (w1 * 1.6 if tip else 0))
    pts += [(end[0] + nx * w1, end[1] + ny * w1), p1, (end[0] - nx * w1, end[1] - ny * w1), (p0[0] - nx * w0, p0[1] - ny * w0)]
    m = s.poly(pts)

    def normal(x, y):
        side = (x - p0[0]) * nx + (y - p0[1]) * ny
        return (nx * (0.8 if side > 0 else -0.8) * -1, ny * (0.8 if side > 0 else -0.8) * -1, 0.6)
    s.shade(m, ramp, normal, lo=1, spec=0.0, glow=glow)
    # the fuller: a bright line down the middle
    core = s.path([(p0[0] + ux * 1.0, p0[1] + uy * 1.0), (end[0], end[1])], 0.3)
    s.fill(core & m, ramp[-2])
    return m


def _hilt(s, at, guard, grip=WOOD, pommel=GOLD, size=2.6):
    x, y = at
    g = s.path([(x - size * 0.7, y - size * 0.7), (x + size * 0.7, y + size * 0.7)], 0.65)
    s.shade(g, guard, n_flat(-0.3, -0.3), lo=1, hi=4)
    h = s.path([(x - 0.4, y + 0.4), (x - 2.4, y + 2.4)], 0.55)
    s.shade(h, grip, n_flat(-0.2, -0.2), lo=1, hi=3)
    s.fill(s.disc(x - 2.9, y + 2.9, 0.9), pommel[3], rim=pommel[0])


def it_weapon(res, wid, w):
    st = style(w)
    s = Spr(res)
    if wid == "sporite_sword":
        _blade(s, (5.2, 10.8), (14.0, 2.0), 1.1, 1.3, hramp("8ad03a"))
        _hilt(s, (5.0, 11.0), hramp("7c4a9c"))
    elif wid == "jailer_blade":
        _blade(s, (5.2, 10.8), (14.2, 1.8), 1.6, 1.2, IRON)
        s.dot(6.5, 9.0, hramp("7fd3ff")[3], glow=True)
        _hilt(s, (5.0, 11.0), IRON, grip=hramp("3a3a44"))
    elif wid == "shadow_blade":
        _blade(s, (5.2, 10.8), (14.4, 1.6), 1.2, 1.5, hramp("2c3456", dl=0.1))
        s.line([(6.8, 10.0), (13.4, 3.4)], hramp("6a8aff")[4], r=0.3, glow=True)
        _hilt(s, (5.0, 11.0), hramp("3a4a8a"), grip=hramp("1a1a24"))
    elif wid == "mirror_blade":
        _blade(s, (5.2, 10.8), (14.0, 2.0), 1.3, 1.3, hramp("e4cbef"))
        s.line([(7.0, 8.4), (12.4, 3.0)], hramp("4ac8c0")[3], r=0.35)
        _hilt(s, (5.0, 11.0), hramp("4ac8c0"), grip=hramp("8a3aa0"))
    elif wid == "artisan_blade":
        _blade(s, (5.2, 10.8), (14.2, 1.8), 1.3, 1.2, hramp("dcdce4", dl=0.09))
        _hilt(s, (5.0, 11.0), GOLD, grip=RED, pommel=RED)
        s.dot(5.0, 10.4, RED[4])
    elif wid == "ash_hammer":
        s.shade(s.path([(2.0, 14.2), (9.8, 6.4)], 0.65), WOOD, n_flat(-0.2, -0.2), lo=1, hi=4)
        head = s.poly([(6.4, 4.4), (10.6, 0.8), (15.0, 5.2), (11.4, 8.8)])
        s.shade(head, hramp("3e2c26"), n_bevel(s, head, 1.2), lo=1, hi=4)
        s.line([(8.6, 4.2), (10.4, 5.0), (11.6, 6.4)], hramp("ff8a2a")[3], r=0.35, glow=True)
    elif wid == "seismic_mace":
        s.shade(s.path([(2.0, 14.2), (8.8, 7.4)], 0.65), WOOD, n_flat(-0.2, -0.2), lo=1, hi=4)
        head = s.disc(10.4, 5.6, 4.0)
        for (x, y) in ((10.4, 0.8), (15.2, 5.6), (13.8, 2.2), (6.6, 2.2), (13.8, 9.0)):
            head |= s.disc(x, y, 0.9)
        s.shade(head, hramp("7a5040"), n_sphere(9.6, 4.8, 4.4), lo=1, spec=0.05)
        s.line([(8.6, 4.0), (10.4, 5.6), (9.6, 7.6)], hramp("ffa050")[4], r=0.35, glow=True)
    elif wid == "lightning_lance":
        s.shade(s.path([(1.6, 14.6), (10.0, 6.2)], 0.55), hramp("c8d8ec"), n_flat(-0.2, -0.2), lo=1, hi=4)
        s.fill(s.rect(8.6, 6.4, 10.4, 8.2), GOLD[3], rim=GOLD[0])
        bolt = s.poly([(10.0, 6.6), (12.0, 3.4), (11.0, 3.6), (14.8, 0.6), (12.6, 4.2), (13.6, 4.0), (10.8, 7.4)])
        s.shade(bolt, hramp("ffe14a", dl=0.08), n_flat(-0.3, -0.3), lo=1, hi=4, glow=True)
    elif wid == "trench_trident":
        s.shade(s.path([(1.6, 14.6), (9.4, 6.8)], 0.55), hramp("1ab0b0"), n_flat(-0.2, -0.2), lo=1, hi=4)
        prongs = s.path([(8.0, 7.6), (10.4, 5.2)], 0.6) | s.path([(10.4, 5.2), (14.4, 1.2)], 0.5)
        prongs |= s.path([(8.6, 4.6), (10.4, 5.2)], 0.5) | s.path([(8.6, 4.6), (9.6, 0.8)], 0.45)
        prongs |= s.path([(10.4, 5.2), (11.4, 7.0), (15.2, 6.4)], 0.45)
        s.shade(prongs, hramp("9af0ff", dl=0.08), n_flat(-0.3, -0.3), lo=1, hi=4)
    elif wid == "season_scythe":
        s.shade(s.path([(3.0, 15.2), (8.8, 1.8)], 0.6), WOOD, n_flat(-0.2, -0.2), lo=1, hi=4)
        m = s.mask(lambda x, y: y < 8.0 and x > 8.2 and math.hypot(x - 8.0, y - 9.6) < 7.6 and math.hypot(x - 6.6, y - 12.0) > 7.6)
        s.shade(m, hramp("d86a2a"), n_sphere(9.0, 6.0, 6.4), lo=1)
        s.dot(10.0, 2.6, hramp("6ab04a")[3])
    s.outline()
    return s


def prev_gear(res):
    out = []
    for sid in ARMOR_STYLE:
        for piece in ("helmet", "chestplate", "leggings", "boots"):
            out.append(it_armor(res, sid, piece))
    for wid, w in (("sporite_sword", 1), ("ash_hammer", 2), ("jailer_blade", 3), ("lightning_lance", 4), ("shadow_blade", 5),
                   ("mirror_blade", 6), ("trench_trident", 7), ("season_scythe", 8), ("seismic_mace", 9), ("artisan_blade", 10)):
        out.append(it_weapon(res, wid, w))
    return out


# =================================================================== blocks: tiling helpers
def _hash(ix, iy, seed):
    n = (ix * 374761393 + iy * 668265263 + seed * 2246822519 + 97) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffffff) / 0xffffff


def pnoise(x, y, cells, seed):
    """Value noise periodic over the 16-unit tile, `cells` cells across."""
    fx, fy = x / 16.0 * cells, y / 16.0 * cells
    ix, iy = int(math.floor(fx)), int(math.floor(fy))
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    g = lambda a, b: _hash(a % cells, b % cells, seed)  # noqa: E731
    a = g(ix, iy) + (g(ix + 1, iy) - g(ix, iy)) * tx
    b = g(ix, iy + 1) + (g(ix + 1, iy + 1) - g(ix, iy + 1)) * tx
    return a + (b - a) * ty


def tile(s, fn):
    k = s.k
    for j in range(s.H):
        for i in range(s.W):
            c = fn((i + 0.5) / k, (j + 0.5) / k, i, j)
            if c is not None:
                s.put((i, j), c)


EARTH = hramp("553624", n=5, dl=0.09)


def bl_soil(res, w, tilled=False):
    """World Soil: dark garden earth, flecked with the colours of the world it feeds."""
    st = style(w if w else 0)
    s = Spr(res)
    seed = 400 + w

    def f(x, y, i, j):
        n = pnoise(x, y, 4, seed) * 0.6 + pnoise(x, y, 8, seed + 1) * 0.4
        if tilled:
            row = (y % 4.0)
            n = n * 0.5 + (0.75 if row < 1.0 else 0.15 if row >= 3.0 else 0.45)
        t = 1 if n < 0.34 else 2 if n < 0.56 else 3
        c = EARTH[t]
        h = _hash(int(x * 2), int(y * 2), seed + 7)
        if h > 0.965:
            c = st["body"][3] if h > 0.985 else st["glow"][1]
        elif h < 0.03:
            c = EARTH[4]
        return c
    tile(s, f)
    if not tilled:
        # a few roots and pebbles
        for (x, y) in ((2.0, 11.0), (11.0, 4.0)):
            s.dot(x, y, EARTH[0])
            s.dot(x + 1, y, EARTH[4])
    return s


def bl_world_block(res):
    s = Spr(res)

    def f(x, y, i, j):
        sheen = (x + y) % 16
        t = 2 if sheen < 6 else 3 if sheen < 10 else 2
        if 2.0 < (x - y + 16) % 16 < 3.0:
            t = 4
        return RED[t]
    tile(s, f)
    frame = s.mask(lambda x, y: x < 1.5 or x >= 14.5 or y < 1.5 or y >= 14.5)
    s.shade(frame, GOLD, lambda x, y: (-0.6 if x < 1.5 or y < 1.5 else 0.6, 0, 0.6), rim=False, lo=1, hi=4)
    s.fill(s.mask(lambda x, y: (x < 0.6 or x >= 15.4 or y < 0.6 or y >= 15.4)), GOLD[1])
    for (x, y) in ((0.6, 0.6), (13.4, 0.6), (0.6, 13.4), (13.4, 13.4)):
        s.fill(s.rect(x, y, x + 2.0, y + 2.0), GOLD[4])
        s.dot(x + 0.5, y + 0.5, RED[2])
    # the doll emblem
    emb = s.disc(8, 5.8, 1.9) | s.ell(8, 9.8, 2.8, 3.0)
    s.shade(emb, GOLD, n_sphere(7.4, 7.0, 3.6, 4.6), rim=False, lo=2, hi=5)
    s.edge(emb, GOLD[1], sides=("r", "b", "l", "t"))
    face = s.ell(8, 6.0, 1.15, 1.0)
    s.fill(face, SKIN[3])
    s.dot(7.0, 5.0, (92, 50, 30))
    s.dot(8.0, 5.0, (92, 50, 30))
    s.dot(7.5, 9.2, RED[3])
    s.dot(7.5, 8.4, RED[5])
    # gold curls in the corners of the panel
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cx, cy = 8 + sx * 4.6, 8 + sy * 4.6
        s.line([(cx - sx * 1.6, cy), (cx, cy), (cx, cy - sy * 1.6)], GOLD[3], r=0.35)
    return s


def bl_threshold(res):
    s = Spr(res)
    lac = hramp("2a1a16", dl=0.08)

    def f(x, y, i, j):
        return lac[2] if pnoise(x, y, 4, 77) > 0.5 else lac[1]
    tile(s, f)
    arch = s.mask(lambda x, y: (3.0 <= x < 13.0 and 6.5 <= y < 15.0) or (x - 8) ** 2 + (y - 6.5) ** 2 <= 25)
    s.fill(arch, GOLD[3])
    inner = s.mask(lambda x, y: (4.2 <= x < 11.8 and 6.5 <= y < 15.0) or (x - 8) ** 2 + (y - 6.5) ** 2 <= 3.8 ** 2)
    light = hramp("f6c860", dl=0.07)

    def lit(p):
        y = (p[1] + 0.5) / s.k
        x = (p[0] + 0.5) / s.k
        d = math.hypot(x - 8, (y - 10) * 0.7)
        return light[5] if d < 1.6 else light[4] if d < 3.0 else light[3]
    s.fill(inner, lit, glow=True)
    s.edge(arch, GOLD[1], sides=("r", "b"))
    # the doll silhouette standing in the light
    sil = s.disc(8, 9.4, 1.1) | s.ell(8, 12.6, 1.8, 2.2)
    s.fill({p for p in sil if (p[1] + 0.5) / s.k < 15}, lac[1])
    s.fill(s.rect(0, 15.0, 16, 16), GOLD[2])
    s.fill(s.rect(0, 0, 16, 1.0), GOLD[2])
    return s


# =================================================================== stations
STATION_WORLD = {"matrix_workbench": 0, "class_table": 0, "soul_altar": 0, "spore_vat": 1, "ash_foundry": 2, "jailer_table": 3,
                 "lightning_forge": 4, "dark_altar": 5, "inverter": 6, "abyssal_press": 7, "time_workshop": 8,
                 "terrain_anchor": 9, "final_loom": 10}


def _wood(s, seed, ramp=WOOD, planks=True):
    def f(x, y, i, j):
        g = pnoise(x * 0.5, y * 4.0, 4, seed) * 0.7 + pnoise(x, y, 8, seed + 3) * 0.3
        t = 2 if g < 0.45 else 3
        if planks and (y % 5.33) < 0.7:
            t = 1
        return ramp[t]
    tile(s, f)


def _frame(s, w):
    """The painted wooden frame of a station face with a gold fillet and corner rivets."""
    st = style(w)
    border = s.mask(lambda x, y: x < 2 or x >= 14 or y < 2 or y >= 14)
    s.shade(border, WOOD, lambda x, y: (-0.7 if (x < 2 or y < 2) and not (x >= 14 or y >= 14) else 0.7 if (x >= 14 or y >= 14) else 0, 0, 0.6),
            rim=False, lo=1, hi=4)
    s.fill(s.mask(lambda x, y: x < 0.6 or x >= 15.4 or y < 0.6 or y >= 15.4), WOOD[0])
    fillet = s.mask(lambda x, y: (1.6 <= x < 14.4 and 1.6 <= y < 14.4) and not (2.3 <= x < 13.7 and 2.3 <= y < 13.7))
    s.fill(fillet, GOLD[3])
    for (x, y) in ((0.8, 0.8), (14.2, 0.8), (0.8, 14.2), (14.2, 14.2)):
        s.dot(x, y, GOLD[4])
    panel = s.rect(2.3, 2.3, 13.7, 13.7)
    enamel = st["body"]

    def f(p):
        x, y = (p[0] + 0.5) / s.k, (p[1] + 0.5) / s.k
        t = 1 if pnoise(x, y, 4, 9 + w) < 0.4 else 2
        return enamel[t]
    s.fill(panel, f)
    s.fill(s.mask(lambda x, y: 2.3 <= x < 13.7 and 2.3 <= y < 3.2), enamel[0])
    return st


def _side_icon(s, sid, st):
    g = st["glow"]
    if sid == "matrix_workbench":
        for r, t in ((4.6, 2), (3.2, 4), (1.8, 2)):
            sq = s.mask(lambda x, y, r=r: abs(x - 8) <= r and abs(y - 8.5) <= r and not (abs(x - 8) <= r - 0.8 and abs(y - 8.5) <= r - 0.8))
            s.fill(sq, GOLD[t])
        s.fill(s.disc(8, 8.5, 0.8), RED[4])
    elif sid == "class_table":
        sh = s.poly([(4.8, 4.6), (11.2, 4.6), (11.2, 8.6), (8.0, 12.6), (4.8, 8.6)])
        s.shade(sh, RED, n_bevel(s, sh, 1.0), rim=GOLD[1], lo=1, hi=4)
        s.line([(5.8, 6.8), (8.0, 9.0), (10.2, 6.8)], GOLD[4], r=0.45)
    elif sid == "soul_altar":
        fl = s.ell(8, 9.4, 2.6, 2.4) | s.poly([(5.6, 9.0), (8.0, 3.8), (10.4, 9.0)])
        soul = hramp("d8f0ff", dl=0.07)
        s.shade(fl, soul, n_sphere(7.6, 8.6, 3.0, 4.0), rim=False, lo=2, hi=5, glow=True)
        s.fill(s.rect(5.0, 12.0, 11.0, 13.0), GOLD[3])
    elif sid == "spore_vat":
        win = s.disc(8, 8.6, 3.8)
        s.fill(win, IRON[2])
        liq = s.disc(8, 8.6, 3.0)
        s.shade(liq, g, n_sphere(7.0, 7.6, 3.6), rim=False, lo=1, hi=4, glow=True)
        for (x, y) in ((6.5, 9.0), (8.6, 7.2), (9.0, 10.0)):
            s.dot(x, y, g[5], glow=True)
    elif sid == "ash_foundry":
        mouth = s.mask(lambda x, y: (4.6 <= x < 11.4 and 8.0 <= y < 12.6) or ((x - 8) ** 2 + (y - 8.0) ** 2 <= 3.4 ** 2 and y < 8.0))
        s.fill(mouth, (30, 20, 18))
        fire = s.mask(lambda x, y: 5.2 <= x < 10.8 and y < 12.6 and y > 8.2 + 1.6 * abs(math.sin(x * 1.3)))
        s.fill(fire, lambda p: g[5] if (p[1] + 0.5) / s.k > 11.0 else g[3] if (p[1] + 0.5) / s.k > 9.8 else g[1], glow=True)
        for x in (5.2, 7.6, 10.0):
            s.dot(x, 13.0, IRON[3])
    elif sid == "jailer_table":
        plate = s.rect(5.0, 4.6, 11.0, 12.8)
        s.shade(plate, IRON, n_bevel(s, plate, 1.0), rim=IRON[0], lo=1, hi=4)
        kh = s.disc(8, 7.6, 1.2) | s.poly([(7.2, 8.0), (8.8, 8.0), (9.3, 11.0), (6.7, 11.0)])
        s.fill(kh, g[3], glow=True)
    elif sid == "lightning_forge":
        anv = s.poly([(4.2, 9.6), (11.8, 9.6), (10.6, 11.0), (9.4, 11.0), (9.8, 13.0), (6.2, 13.0), (6.6, 11.0), (5.4, 11.0)])
        s.shade(anv, IRON, n_flat(-0.3, -0.4), rim=IRON[0], lo=1, hi=4)
        bolt = s.poly([(8.6, 3.0), (6.4, 6.6), (7.8, 6.6), (6.8, 9.4), (9.8, 5.6), (8.4, 5.6), (9.8, 3.0)])
        s.shade(bolt, g, n_flat(-0.3, -0.3), rim=False, lo=2, hi=5, glow=True)
    elif sid == "dark_altar":
        eye = s.ell(8, 8.6, 4.4, 2.2)
        s.fill(eye, (8, 8, 14))
        s.fill(s.disc(8, 8.6, 1.5), g[3], glow=True)
        s.fill(s.disc(8, 8.6, 0.6), (8, 8, 14))
        s.edge(eye, g[1], sides=("t", "b"))
    elif sid == "inverter":
        up = s.poly([(4.2, 8.2), (11.8, 8.2), (8.0, 3.8)])
        dn = s.poly([(4.2, 9.0), (11.8, 9.0), (8.0, 13.4)])
        s.shade(up, hramp("c84ad8"), n_flat(-0.2, -0.4), rim=False, lo=2, hi=4)
        s.shade(dn, hramp("4ac8c0"), n_flat(0.2, 0.4), rim=False, lo=2, hi=4)
    elif sid == "abyssal_press":
        dial = s.disc(8, 8.6, 4.0)
        s.fill(dial, GOLD[2])
        face = s.disc(8, 8.6, 3.2)
        s.fill(face, (236, 240, 232))
        for a in range(200, 341, 35):
            s.dot(8 + 2.4 * math.cos(math.radians(a)) - 0.5, 8.6 + 2.4 * math.sin(math.radians(a)) - 0.5, INK)
        s.line([(8.0, 8.6), (10.0, 6.8)], g[1], r=0.35)
        s.dot(7.5, 8.1, RED[3])
    elif sid == "time_workshop":
        face = s.disc(8, 8.6, 4.2)
        s.fill(face, GOLD[3])
        s.fill(s.disc(8, 8.6, 3.4), PAPER[4])
        for a in range(0, 360, 90):
            s.dot(8 + 2.7 * math.cos(math.radians(a)) - 0.5, 8.6 + 2.7 * math.sin(math.radians(a)) - 0.5, INK)
        s.line([(8.0, 8.6), (8.0, 6.2)], INK, r=0.35)
        s.line([(8.0, 8.6), (9.8, 8.6)], RED[3], r=0.35)
    elif sid == "terrain_anchor":
        anc = s.path([(8, 4.2), (8, 12.4)], 0.6) | s.path([(5.2, 6.0), (10.8, 6.0)], 0.5) | s.ring(8, 3.6, 0.6, 1.4)
        anc |= s.path([(4.6, 10.2), (5.6, 12.2), (8.0, 12.8), (10.4, 12.2), (11.4, 10.2)], 0.55)
        s.shade(anc, IRON, n_flat(-0.3, -0.3), rim=IRON[0], lo=1, hi=4)
        s.line([(3.6, 13.2), (5.0, 11.6)], g[3], r=0.3, glow=True)
        s.line([(12.4, 13.2), (11.0, 11.6)], g[3], r=0.3, glow=True)
    elif sid == "final_loom":
        cols = (hx("3d7a2c"), hx("e0661c"), hx("7fd3ff"), hx("ffe14a"), hx("6a8aff"), hx("b44ccc"), hx("1ab0b0"), hx("c89a3c"), hx("b85a3e"), hx("f4eefa"))
        for i in range(10):
            x = 3.2 + i * 1.0
            s.fill(s.rect(x, 3.6, x + 0.6 if res_of(s) >= 32 else x + 1, 13.0), cols[i])
        s.fill(s.rect(2.6, 7.6, 13.4, 8.8), GOLD[3])
        s.fill(s.rect(2.6, 3.2, 13.4, 3.8), WOOD[1])
        s.fill(s.rect(2.6, 12.8, 13.4, 13.6), WOOD[1])


def res_of(s):
    return s.res


def _top(s, sid, st):
    g = st["glow"]
    if sid == "matrix_workbench":
        for v in (5.0, 8.0, 11.0):
            s.fill(s.rect(v - 0.3, 3.2, v + 0.3 if s.res >= 32 else v + 0.7, 12.8), GOLD[3])
            s.fill(s.rect(3.2, v - 0.3, 12.8, v + 0.3 if s.res >= 32 else v + 0.7), GOLD[3])
        s.fill(s.ell(8.3, 8.3, 1.2, 1.5), st["body"][3])
    elif sid == "class_table":
        cloth = s.rect(3.4, 3.4, 12.6, 12.6)
        s.fill(cloth, RED[2])
        s.fill(s.edge(cloth, GOLD[3], sides=("r", "b", "l", "t")), GOLD[3])
        s.glyph(["..#..", ".###.", "#####", ".###.", "..#.."], 5.5, 5.5, {"#": GOLD[4]})
    elif sid == "soul_altar":
        bowl = s.disc(8, 8, 4.4)
        s.fill(bowl, hramp("8a8a92")[2])
        soul = s.disc(8, 8, 3.2)
        s.shade(soul, hramp("d8f0ff", dl=0.07), n_sphere(7.2, 7.2, 3.6), rim=False, lo=2, hi=5, glow=True)
    elif sid == "spore_vat":
        rim = s.disc(8, 8, 5.2)
        s.fill(rim, IRON[2])
        liq = s.disc(8, 8, 4.2)
        s.shade(liq, g, n_sphere(7.0, 7.0, 5.0), rim=False, lo=1, hi=3, glow=True)
        for (x, y) in ((6.0, 7.0), (9.0, 6.0), (8.0, 9.6), (10.0, 9.0)):
            s.dot(x, y, g[5], glow=True)
    elif sid == "ash_foundry":
        cru = s.disc(8, 8, 4.8)
        s.fill(cru, hramp("3e2c26")[1])
        melt = s.disc(8, 8, 3.6)
        s.shade(melt, g, n_sphere(7.0, 7.0, 4.2), rim=False, lo=2, hi=5, glow=True)
        s.line([(6.0, 8.4), (8.0, 7.2), (10.0, 8.6)], hramp("ff8a2a")[1], r=0.3)
    elif sid == "jailer_table":
        for i in range(3):
            for j in range(2):
                x, y = 4.6 + i * 2.6, 5.4 + j * 3.6
                s.fill(s.rect(x, y, x + 1.6, y + 2.4), IRON[1])
                s.fill(s.rect(x + 0.3, y + 0.3, x + 1.3, y + 1.4), g[3] if (i + j) % 2 == 0 else IRON[4], glow=(i + j) % 2 == 0)
    elif sid == "lightning_forge":
        face = s.rect(3.6, 5.2, 12.4, 10.8)
        s.shade(face, IRON, n_bevel(s, face, 1.0), rim=IRON[0], lo=1, hi=4)
        for (x, y) in ((6.0, 6.4), (9.4, 8.6), (7.6, 9.4), (10.4, 6.0)):
            s.dot(x, y, g[4], glow=True)
    elif sid == "dark_altar":
        s.fill(s.rect(2.4, 2.4, 13.6, 13.6), (14, 14, 22))
        rune = s.ring(8, 8, 3.6, 4.4) | s.path([(8, 3.8), (8, 12.2)], 0.3) | s.path([(3.8, 8), (12.2, 8)], 0.3)
        s.fill(rune, g[2], glow=True)
    elif sid == "inverter":
        s.fill(s.poly([(2.4, 2.4), (13.6, 2.4), (2.4, 13.6)]), hramp("c84ad8")[2])
        s.fill(s.poly([(13.6, 2.4), (13.6, 13.6), (2.4, 13.6)]), hramp("4ac8c0")[2])
        s.line([(3.2, 12.8), (12.8, 3.2)], (246, 240, 250), r=0.4)
    elif sid == "abyssal_press":
        plate = s.disc(8, 8, 5.0)
        s.shade(plate, IRON, n_sphere(7.0, 7.0, 6.0), rim=IRON[0], lo=1, hi=4)
        for a in range(0, 360, 60):
            s.dot(8 + 4.0 * math.cos(math.radians(a)) - 0.5, 8 + 4.0 * math.sin(math.radians(a)) - 0.5, GOLD[4])
        s.shade(s.disc(8, 8, 1.8), g, n_sphere(7.4, 7.4, 2.2), rim=False, lo=2, hi=5, glow=True)
    elif sid == "time_workshop":
        for (x, y, r) in ((6.2, 6.4, 2.6), (10.4, 9.8, 2.2)):
            gear = s.disc(x, y, r) | s.mask(lambda a, b, x=x, y=y, r=r: math.hypot(a - x, b - y) < r + 0.9 and int(math.degrees(math.atan2(b - y, a - x)) // 30) % 2 == 0)
            s.shade(gear, GOLD, n_sphere(x - 0.5, y - 0.5, r + 1), rim=GOLD[0], lo=1, hi=4)
            s.fill(s.disc(x, y, 0.7), GOLD[1])
    elif sid == "terrain_anchor":
        s.fill(s.ring(8, 8, 3.4, 4.6), IRON[2])
        s.line([(2.6, 3.4), (5.0, 6.0), (4.6, 8.4)], g[3], r=0.3, glow=True)
        s.line([(13.4, 12.6), (11.0, 10.4), (11.6, 8.4)], g[3], r=0.3, glow=True)
        s.fill(s.disc(8, 8, 1.4), g[4], glow=True)
    elif sid == "final_loom":
        cols = (hx("3d7a2c"), hx("e0661c"), hx("3a78c6"), hx("c89a3c"), hx("b44ccc"))
        for j in range(16):
            for i in range(16):
                x, y = (i + 0.5) / s.k, (j + 0.5) / s.k
                if 2.4 <= x < 13.6 and 2.4 <= y < 13.6:
                    pass
        k = s.k
        for j in range(s.H):
            for i in range(s.W):
                x, y = (i + 0.5) / k, (j + 0.5) / k
                if 2.4 <= x < 13.6 and 2.4 <= y < 13.6:
                    over = (int(x) + int(y)) % 2 == 0
                    c = cols[int(x) % 5] if over else cols[int(y) % 5]
                    s.put((i, j), mix(c, (0, 0, 0), 0.0 if over else 0.25))


def bl_station(res, sid, face):
    w = STATION_WORLD[sid]
    s = Spr(res)
    _wood(s, 30 + w)
    if face == "bottom":
        st = style(w)
        s.fill(s.rect(0, 7.0, 16, 9.0), st["body"][2])
        s.fill(s.rect(0, 7.0, 16, 7.5 if res >= 32 else 8.0), GOLD[3])
        return s
    st = _frame(s, w)
    if face == "side":
        _side_icon(s, sid, st)
        # a frieze of the world's second colour under the top fillet
        for i in range(6):
            s.dot(3.0 + i * 2.0, 2.6, st["second"][3])
    else:
        _top(s, sid, st)
    return s


def prev_blocks(res):
    out = [bl_soil(res, w) for w in range(10)] + [bl_soil(res, 0, True), bl_soil(res, 5, True), bl_world_block(res), bl_threshold(res)]
    for sid in STATION_WORLD:
        out += [bl_station(res, sid, "side"), bl_station(res, sid, "top")]
    out.append(bl_station(res, "spore_vat", "bottom"))
    return out


# =================================================================== dispatch (used by gen.py and hdpack.py)
WEAPON_WORLD = {"sporite_sword": 1, "ash_hammer": 2, "jailer_blade": 3, "lightning_lance": 4, "shadow_blade": 5,
                "mirror_blade": 6, "trench_trident": 7, "season_scythe": 8, "seismic_mace": 9, "artisan_blade": 10}
_SINGLE = {"whole_matryoshka": it_whole_matryoshka, "nested_dolls": it_nested_dolls, "life_doll": it_life_doll,
           "chance_doll": it_chance_doll, "cracked_doll": it_cracked_doll, "refuge_doll": it_refuge_doll,
           "artisan_scroll": it_scroll, "artisan_journal": it_journal, "journal_page": it_page,
           "sealed_shackle": it_shackle, "storm_censer": it_censer, "wreath_of_seasons": it_wreath, "unfinished_effigy": it_effigy}
CORE_WORLD = {"guardian_core": 0, "queen_core": 1, "titan_core": 2, "jailer_core": 3, "storm_king_core": 4, "light_eater_core": 5,
              "double_core": 6, "leviathan_core": 7, "seasons_core": 8, "terrain_core": 9, "unfinished_core": 10}


def crafted_item(it, res=16):
    """The hand-crafted sprite of an item (an ALL_ITEMS entry of gen.py), or None to keep the procedural painter."""
    import ores_art
    spr = ores_art.crafted_item(it, res)
    if spr is not None:
        return spr
    iid = it["id"]
    if iid.startswith("hidden_doll_"):
        w = int(iid.rsplit("_", 1)[1])
        return it_hidden_doll(res, w, NEST.index(w))
    if iid in _SINGLE:
        return _SINGLE[iid](res)
    if iid == "blank_scroll":
        return it_scroll(res, blank=True)
    if iid in CORE_WORLD:
        return it_core(res, CORE_WORLD[iid])
    if iid.startswith("seed_"):
        w = int(iid[5:])
        if w >= 2:
            # Worlds 2 to 10 open with their own object, not a Seed (tools/rites_art.py)
            import rites_art
            return rites_art.RITE_ART[w](res)
        return it_seed(res, w)
    if iid in SNORKEL_STYLE:
        return it_snorkel(res, iid)
    if it.get("kind") == "armor" and it.get("set") in ARMOR_STYLE:
        return it_armor(res, it["set"], it["piece"])
    if iid in WEAPON_WORLD:
        return it_weapon(res, iid, WEAPON_WORLD[iid])
    return None


def crafted_block(bid, res=16):
    """{texture suffix: sprite} of a hand-crafted block ('' is the main face), or None."""
    import ores_art
    if ores_art.crafted_block(bid, res) is not None:
        return ores_art.crafted_block(bid, res)
    if bid.startswith("world_soil_"):
        w = int(bid.rsplit("_", 1)[1])
        return {"": bl_soil(res, w), "_tilled": bl_soil(res, w, tilled=True)}
    if bid == "world_block":
        return {"": bl_world_block(res)}
    if bid == "threshold":
        return {"": bl_threshold(res)}
    if bid in STATION_WORLD:
        return {"": bl_station(res, bid, "side"), "_top": bl_station(res, bid, "top"), "_bottom": bl_station(res, bid, "bottom")}
    return None
