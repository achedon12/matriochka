"""Procedural pixel-art painter for Matriochka item, block and entity textures."""
import math
import random
from PIL import Image


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    if f >= 1:
        return mix(c, (255, 255, 255), min(1, f - 1))
    return mix((0, 0, 0), c, max(0, f))


def rng(seed):
    return random.Random(hash(seed) & 0xFFFFFFFF)


class Canvas:
    def __init__(self, w=16, h=16):
        self.w, self.h = w, h
        self.px = {}

    def set(self, x, y, c, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[(int(x), int(y))] = (c[0], c[1], c[2], a)

    def get(self, x, y):
        return self.px.get((x, y))

    def fill_mask(self, mask, base, light_dir=(-1, -1), seed="", noise=0.12):
        """mask: set of (x,y). Shades by distance to the lit edge + noise, then outlines."""
        r = rng(seed)
        for (x, y) in mask:
            nx = (x - self.w / 2) / self.w
            ny = (y - self.h / 2) / self.h
            lit = 1.0 - (nx * light_dir[0] + ny * light_dir[1]) * 0.9
            f = 0.75 + 0.35 * lit + (r.random() - 0.5) * noise
            self.set(x, y, shade(base, f))
        self.outline(mask, shade(base, 0.35))

    def outline(self, mask, col):
        for (x, y) in list(mask):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (x + dx, y + dy)
                if p not in mask and 0 <= p[0] < self.w and 0 <= p[1] < self.h and p not in self.px:
                    self.set(p[0], p[1], col)

    def highlight(self, mask, col, n=3, seed=""):
        r = rng(seed + "h")
        pts = sorted(mask, key=lambda p: p[0] + p[1])[: max(1, len(mask) // 6)]
        for p in r.sample(pts, min(n, len(pts))):
            self.set(p[0], p[1], col)

    def save(self, path):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        for (x, y), c in self.px.items():
            img.putpixel((x, y), c)
        img.save(path)


# ------------------------------------------------------------------ shape masks (16x16)
def disc(cx, cy, r):
    return {(x, y) for x in range(16) for y in range(16) if (x - cx) ** 2 + (y - cy) ** 2 <= r * r}


def ellipse(cx, cy, rx, ry):
    return {(x, y) for x in range(16) for y in range(16) if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1}


def rect(x0, y0, x1, y1):
    return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}


def diamond(cx, cy, r):
    return {(x, y) for x in range(16) for y in range(16) if abs(x - cx) + abs(y - cy) <= r}


def line(x0, y0, x1, y1, w=1):
    pts = set()
    n = max(abs(x1 - x0), abs(y1 - y0)) * 2 + 1
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        for dx in range(-(w // 2), w - w // 2):
            for dy in range(-(w // 2), w - w // 2):
                pts.add((round(x + dx), round(y + dy)))
    return {p for p in pts if 0 <= p[0] < 16 and 0 <= p[1] < 16}


def poly(points):
    """Filled polygon by scanline (points in pixel coords)."""
    res = set()
    for y in range(16):
        xs = []
        n = len(points)
        for i in range(n):
            (x0, y0), (x1, y1) = points[i], points[(i + 1) % n]
            if (y0 <= y + 0.5 < y1) or (y1 <= y + 0.5 < y0):
                xs.append(x0 + (y + 0.5 - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            for x in range(int(math.ceil(a - 0.5)), int(math.floor(b - 0.5)) + 1):
                res.add((x, y))
    return res


def doll_mask(scale=1.0, cx=8, base=14):
    head = disc(cx, base - 9 * scale, 3.2 * scale)
    body = ellipse(cx, base - 3.5 * scale, 4.4 * scale, 4.4 * scale)
    return head | body


WOOD = hx("8a5a3a")
GOLD = hx("e8c050")
IRON = hx("b8bcc4")
DOLL_RED = hx("c8342a")


def paint_item(shape, pal, seed, path, rarity="common"):
    p, s, a, d = [hx(c) for c in pal]
    c = Canvas()
    r = rng(seed)
    if shape in ("gem", "crystal", "fragment", "shard"):
        if shape == "gem":
            m = diamond(8, 8, 6) & ellipse(8, 8, 6.5, 7)
        elif shape == "crystal":
            m = poly([(8, 1), (12, 5), (11, 14), (5, 14), (4, 5)])
        elif shape == "fragment":
            m = poly([(5, 4), (11, 3), (13, 9), (8, 13), (3, 10)])
        else:
            m = poly([(9, 1), (12, 7), (9, 15), (6, 9)])
        c.fill_mask(m, a, seed=seed)
        c.highlight(m, (255, 255, 255), 3, seed)
        for (x, y) in list(m):
            if (x + y) % 5 == 0:
                c.set(x, y, shade(a, 1.25))
    elif shape in ("ingot",):
        m = poly([(2, 10), (5, 6), (14, 6), (11, 10)]) | rect(2, 10, 11, 12)
        c.fill_mask(m, a, seed=seed)
        for x in range(5, 13):
            c.set(x, 7, shade(a, 1.4))
    elif shape in ("dust",):
        m = set()
        for i in range(22):
            x, y = r.randint(3, 12), r.randint(6, 13)
            m |= {(x, y), (x + 1, y)}
        m |= ellipse(8, 11, 5, 2.5)
        c.fill_mask(m, a, seed=seed, noise=0.4)
    elif shape in ("rock", "chunk"):
        m = poly([(3, 6), (7, 3), (12, 4), (14, 9), (11, 13), (5, 13), (2, 10)])
        c.fill_mask(m, s if shape == "rock" else p, seed=seed, noise=0.3)
        for i in range(5):
            x, y = r.randint(5, 11), r.randint(5, 11)
            c.set(x, y, a)
            c.set(x + 1, y, shade(a, 1.2))
    elif shape in ("stick",):
        m = line(3, 13, 12, 3, 2) | line(7, 9, 4, 6, 1) | line(10, 6, 13, 7, 1)
        c.fill_mask(m, p, seed=seed)
    elif shape in ("plate",):
        m = ellipse(8, 8, 6, 5) - ellipse(8, 11, 4, 2)
        c.fill_mask(m, a, seed=seed)
        for x in range(4, 13, 3):
            for y in range(5, 11):
                c.set(x, y, shade(a, 0.7))
    elif shape in ("potion", "jar", "capsule"):
        if shape == "potion":
            m = disc(8, 10, 4.6) | rect(7, 2, 9, 6)
            glass = disc(8, 10, 4.6)
        elif shape == "jar":
            m = rect(4, 5, 12, 14) | rect(5, 3, 11, 4)
            glass = rect(4, 6, 12, 14)
        else:
            m = ellipse(8, 8, 3.5, 6.5)
            glass = ellipse(8, 9, 3, 4)
        c.fill_mask(m, (200, 220, 230), seed=seed, noise=0.05)
        for (x, y) in glass:
            if y > 8:
                c.set(x, y, shade(a, 0.9 + 0.2 * ((x + y) % 2)))
        c.set(6, 8, (255, 255, 255))
        if shape == "potion":
            for (x, y) in rect(7, 1, 9, 2):
                c.set(x, y, WOOD)
    elif shape == "mask":
        m = ellipse(8, 8, 6.5, 5.5)
        c.fill_mask(m, p, seed=seed)
        for (x, y) in disc(5, 7, 1.5) | disc(11, 7, 1.5):
            c.set(x, y, (20, 30, 20))
        for (x, y) in ellipse(8, 12, 3, 2):
            c.set(x, y, shade(s, 0.9 + 0.2 * (x % 2)))
    elif shape in ("sword", "spear", "trident", "scythe", "hammer", "mace"):
        blade = a if shape != "hammer" else s
        if shape == "sword":
            m = line(4, 12, 13, 3, 2)
            c.fill_mask(m, blade, seed=seed)
            for (x, y) in line(2, 10, 6, 14, 1):
                c.set(x, y, GOLD)
            for (x, y) in line(1, 15, 4, 12, 1):
                c.set(x, y, WOOD)
        elif shape == "spear":
            for (x, y) in line(2, 14, 11, 5, 1):
                c.set(x, y, WOOD)
            m = poly([(10, 2), (14, 2), (14, 6), (11, 7), (9, 5)])
            c.fill_mask(m, blade, seed=seed)
        elif shape == "trident":
            for (x, y) in line(2, 14, 10, 6, 1):
                c.set(x, y, shade(s, 0.8))
            m = line(9, 7, 14, 2, 1) | line(8, 4, 11, 1, 1) | line(12, 9, 15, 6, 1) | line(8, 6, 12, 9, 1)
            c.fill_mask(m, blade, seed=seed)
        elif shape == "scythe":
            for (x, y) in line(3, 15, 9, 2, 1):
                c.set(x, y, WOOD)
            m = poly([(8, 2), (14, 3), (15, 7), (12, 5), (9, 4)])
            c.fill_mask(m, blade, seed=seed)
        else:
            for (x, y) in line(2, 14, 8, 8, 2):
                c.set(x, y, WOOD)
            m = rect(7, 2, 14, 8) if shape == "hammer" else disc(10, 6, 4.2)
            c.fill_mask(m, blade, seed=seed)
            if shape == "mace":
                for (x, y) in ((10, 1), (14, 6), (10, 11), (6, 6), (13, 3), (7, 3)):
                    c.set(x, y, shade(blade, 1.3))
    elif shape in ("drill",):
        m = poly([(2, 7), (9, 4), (9, 11), (2, 9)]) | poly([(9, 5), (15, 8), (9, 10)])
        c.fill_mask(m, p, seed=seed)
        for y in range(5, 11):
            c.set(11, y, a)
    elif shape == "key" or shape == "key_gold":
        col = GOLD if shape == "key_gold" else IRON
        m = disc(5, 5, 3) - disc(5, 5, 1) | line(7, 7, 13, 13, 2) | rect(10, 12, 11, 14) | rect(12, 10, 14, 11)
        c.fill_mask(m, col, seed=seed)
    elif shape == "map":
        m = rect(2, 3, 13, 13)
        c.fill_mask(m, hx("d8c8a0"), seed=seed, noise=0.05)
        for (x, y) in line(4, 11, 7, 6, 1) | line(7, 6, 11, 9, 1):
            c.set(x, y, hx("8a3a2a"))
        c.set(11, 9, (200, 30, 30))
    elif shape == "pick":
        m = line(3, 13, 12, 4, 1) | line(10, 3, 13, 6, 1)
        c.fill_mask(m, IRON, seed=seed)
        for (x, y) in rect(2, 12, 4, 14):
            c.set(x, y, WOOD)
    elif shape == "trap":
        m = ellipse(8, 9, 6, 4) - ellipse(8, 9, 3, 1.5)
        c.fill_mask(m, IRON, seed=seed)
        for x in range(3, 14, 2):
            c.set(x, 5, shade(IRON, 1.2))
    elif shape == "membrane":
        m = poly([(2, 8), (8, 3), (14, 8), (8, 12)])
        c.fill_mask(m, p, seed=seed)
        for (x, y) in line(2, 8, 14, 8, 1):
            c.set(x, y, shade(s, 0.9))
    elif shape in ("orb", "orb_small", "pearl"):
        rr = 5.5 if shape == "orb" else (3.5 if shape == "orb_small" else 4.5)
        m = disc(8, 8, rr)
        c.fill_mask(m, a if shape != "pearl" else hx("e8f0f8"), seed=seed, noise=0.05)
        c.set(6, 6, (255, 255, 255))
        c.set(7, 6, shade(a, 1.5))
        if shape == "orb":
            for (x, y) in line(6, 5, 10, 11, 1):
                c.set(x, y, shade(s, 1.4))
    elif shape == "glider":
        m = poly([(1, 9), (8, 4), (15, 9), (8, 7)])
        c.fill_mask(m, p, seed=seed)
        for (x, y) in line(8, 7, 8, 14, 1):
            c.set(x, y, WOOD)
    elif shape == "hook":
        m = line(3, 13, 10, 6, 1) | line(10, 6, 13, 3, 2) | line(10, 3, 13, 6, 1)
        c.fill_mask(m, IRON, seed=seed)
    elif shape == "lantern":
        m = rect(5, 4, 11, 13) | rect(6, 2, 10, 3)
        c.fill_mask(m, GOLD, seed=seed)
        for (x, y) in rect(6, 5, 10, 12):
            c.set(x, y, shade(a, 1.2 + 0.1 * (y % 2)))
    elif shape == "sonar":
        m = disc(8, 9, 5.5)
        c.fill_mask(m, shade(p, 0.8), seed=seed)
        for rr in (2, 4):
            for t in range(0, 360, 20):
                x = 8 + rr * math.cos(math.radians(t))
                y = 9 + rr * math.sin(math.radians(t))
                c.set(round(x), round(y), a)
    elif shape == "boots":
        m = rect(4, 3, 8, 11) | rect(4, 11, 13, 13) | rect(9, 3, 11, 9)
        c.fill_mask(m, a, seed=seed)
    elif shape == "thruster":
        m = rect(3, 5, 12, 11)
        c.fill_mask(m, IRON, seed=seed)
        for (x, y) in rect(12, 6, 14, 10):
            c.set(x, y, a)
    elif shape == "hourglass":
        m = poly([(4, 2), (12, 2), (9, 8), (12, 14), (4, 14), (7, 8)])
        c.fill_mask(m, (200, 220, 230), seed=seed, noise=0.02)
        for (x, y) in poly([(5, 11), (11, 11), (11.5, 13.5), (4.5, 13.5)]) | {(8, 8), (8, 9), (8, 10)}:
            c.set(x, y, a)
        for x in range(3, 14):
            c.set(x, 1, WOOD)
            c.set(x, 15, WOOD)
    elif shape == "leaf":
        m = ellipse(8, 8, 3.5, 6.5)
        m = {(x, y) for (x, y) in m}
        c.fill_mask(m, a, seed=seed)
        for (x, y) in line(8, 2, 8, 14, 1):
            c.set(x, y, shade(a, 0.6))
    elif shape == "heart":
        m = disc(6, 6, 3.2) | disc(10, 6, 3.2) | poly([(3, 7), (13, 7), (8, 14)])
        c.fill_mask(m, s, seed=seed)
        for (x, y) in line(6, 5, 9, 10, 1):
            c.set(x, y, a)
    elif shape == "anchor":
        m = line(8, 2, 8, 13, 1) | line(4, 10, 8, 13, 1) | line(12, 10, 8, 13, 1) | rect(5, 4, 11, 4) | disc(8, 2, 1.3)
        c.fill_mask(m, IRON, seed=seed)
    elif shape == "thread":
        m = rect(5, 3, 11, 13)
        c.fill_mask(m, WOOD, seed=seed)
        for y in range(4, 13):
            for x in range(5, 12):
                if y % 2 == 0:
                    c.set(x, y, shade(a, 0.95 + 0.1 * (x % 2)))
    elif shape == "core":
        m = disc(8, 8, 6)
        c.fill_mask(m, d if sum(d) > 60 else p, seed=seed)
        inner = disc(8, 8, 3.4)
        for (x, y) in inner:
            c.set(x, y, shade(a, 1.1 + 0.2 * ((x * y) % 3 == 0)))
        for t in range(0, 360, 45):
            x = 8 + 5 * math.cos(math.radians(t))
            y = 8 + 5 * math.sin(math.radians(t))
            c.set(round(x), round(y), GOLD)
    elif shape == "seed":
        m = ellipse(8, 9, 4.5, 6)
        c.fill_mask(m, p, seed=seed)
        for (x, y) in ellipse(8, 9, 2.5, 4):
            if (x + y) % 2 == 0:
                c.set(x, y, a)
        for (x, y) in line(8, 1, 10, 3, 1):
            c.set(x, y, hx("4a8a2a"))
    elif shape in ("doll", "doll_small", "doll_cracked"):
        sc = 1.0 if shape != "doll_small" else 0.8
        m = doll_mask(sc)
        col = DOLL_RED if shape != "doll_small" else a
        c.fill_mask(m, col, seed=seed, noise=0.05)
        cy = int(14 - 9 * sc)
        for (x, y) in disc(8, cy, 2.0 * sc):
            c.set(x, y, hx("f0d0b0"))
        c.set(7, cy, (20, 20, 20))
        c.set(9, cy, (20, 20, 20))
        for (x, y) in ellipse(8, 14 - 3 * sc, 2.4 * sc, 2.2 * sc):
            c.set(x, y, GOLD if (x + y) % 2 else hx("f0e0a0"))
        if shape == "doll_cracked":
            for (x, y) in line(6, 5, 9, 9, 1) | line(9, 9, 7, 13, 1):
                c.set(x, y, (30, 20, 20))
    elif shape == "scroll":
        m = rect(3, 3, 12, 12)
        c.fill_mask(m, hx("e8d8b0"), seed=seed, noise=0.05)
        for x in range(2, 14):
            c.set(x, 2, WOOD)
            c.set(x, 13, WOOD)
        for y in range(5, 11, 2):
            for x in range(5, 11):
                if (x * 7 + y) % 3:
                    c.set(x, y, hx("6a4a3a"))
        for (x, y) in doll_mask(0.35, 11, 12):
            c.set(x, y, DOLL_RED)
    elif shape == "book":
        m = rect(3, 2, 12, 14)
        c.fill_mask(m, DOLL_RED, seed=seed)
        for y in range(3, 14):
            c.set(12, y, hx("f0e8d0"))
        for (x, y) in doll_mask(0.45, 7, 11):
            c.set(x, y, GOLD)
    elif shape == "page":
        m = rect(4, 2, 12, 14)
        c.fill_mask(m, hx("e8dcc0"), seed=seed, noise=0.05)
        for y in range(4, 13, 2):
            for x in range(5, 11):
                if (x + y * 3) % 4:
                    c.set(x, y, hx("7a5a4a"))
    elif shape == "food":
        m = ellipse(8, 10, 6, 3.5) | ellipse(8, 8, 4.5, 3)
        c.fill_mask(m, WOOD, seed=seed)
        for (x, y) in ellipse(8, 8, 4, 2):
            c.set(x, y, shade(a, 0.9 + 0.2 * ((x + y) % 2)))
    elif shape == "armor":
        pass
    else:
        m = disc(8, 8, 5)
        c.fill_mask(m, a, seed=seed)
    if rarity == "legendary":
        for (x, y) in ((1, 1), (14, 2), (2, 14)):
            if not c.get(x, y):
                c.set(x, y, GOLD)
    c.save(path)


def paint_armor_item(piece, pal, seed, path):
    p, s, a, d = [hx(x) for x in pal]
    c = Canvas()
    if piece == "helmet":
        m = rect(3, 4, 12, 9) | rect(3, 10, 5, 12) | rect(10, 10, 12, 12)
    elif piece == "chestplate":
        m = rect(2, 2, 13, 5) | rect(4, 5, 11, 13)
        m -= rect(6, 2, 9, 3)
    elif piece == "leggings":
        m = rect(3, 2, 12, 5) | rect(3, 5, 6, 14) | rect(9, 5, 12, 14)
    else:
        m = rect(2, 8, 6, 13) | rect(9, 8, 13, 13) | rect(2, 12, 7, 14) | rect(9, 12, 14, 14)
    c.fill_mask(m, a, seed=seed)
    for (x, y) in list(m):
        if (x * 3 + y) % 7 == 0:
            c.set(x, y, shade(s, 1.1))
    c.save(path)


def paint_armor_layer(pal, seed, path, legs=False):
    """64x32 humanoid armor layer with a painted-doll motif."""
    p, s, a, d = [hx(x) for x in pal]
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    r = rng(seed)

    def box(u, v, w, h, dd, col):
        # standard box UV
        for (x0, y0, ww, hh) in ((u + dd, v, w, dd), (u + dd + w, v, w, dd), (u, v + dd, dd, h), (u + dd, v + dd, w, h),
                                 (u + dd + w, v + dd, dd, h), (u + dd + w + dd, v + dd, w, h)):
            for x in range(x0, x0 + ww):
                for y in range(y0, y0 + hh):
                    if 0 <= x < 64 and 0 <= y < 32:
                        f = 0.8 + 0.3 * r.random()
                        edge = x in (x0, x0 + ww - 1) or y in (y0, y0 + hh - 1)
                        cc = shade(col, 0.5 if edge else f)
                        if not edge and (x + y) % 6 == 0:
                            cc = shade(s, 1.1)
                        img.putpixel((x, y), cc + (255,))

    if not legs:
        box(0, 0, 8, 8, 8, a)        # head
        box(16, 16, 8, 12, 4, a)     # body
        box(40, 16, 4, 12, 4, mix(a, s, 0.3))  # arms
        box(0, 16, 4, 12, 4, mix(a, d, 0.3))   # legs (boots)
    else:
        box(16, 16, 8, 12, 4, mix(a, p, 0.3))
        box(0, 16, 4, 12, 4, mix(a, p, 0.3))
    img.save(path)


def paint_block(style, pal, seed, path, variant=0):
    p, s, a, d = [hx(x) for x in pal]
    c = Canvas()
    r = rng(seed)
    base = {"stone": shade(p, 0.9), "moss": s if sum(s) > 120 else p, "soil": hx("6a4a30"), "sand": shade(a, 0.85),
            "brick": shade(p, 0.95), "brick_unbreakable": shade(p, 0.7), "glow": a, "ore": shade(p, 0.85),
            "ore_big": shade(p, 0.8), "wood": hx("9a6a40"), "lacquer": DOLL_RED, "glass": shade(a, 1.1),
            "station": hx("9a6a40"), "special": DOLL_RED, "stone_rune": hx("6a6a72")}.get(style, p)
    for x in range(16):
        for y in range(16):
            f = 0.82 + r.random() * 0.28
            c.set(x, y, shade(base, f))
    if style in ("brick", "brick_unbreakable"):
        for y in range(0, 16, 4):
            for x in range(16):
                c.set(x, y, shade(base, 0.55))
            off = 0 if (y // 4) % 2 == 0 else 4
            for yy in range(y, y + 4):
                c.set((off) % 16, yy, shade(base, 0.55))
                c.set((off + 8) % 16, yy, shade(base, 0.55))
        if style == "brick_unbreakable":
            for (x, y) in ((7, 6), (8, 6), (7, 7), (8, 7), (7, 9), (8, 9)):
                c.set(x, y, a)
    elif style in ("ore", "ore_big"):
        n = 6 if style == "ore" else 12
        for i in range(n):
            x, y = r.randint(1, 13), r.randint(1, 13)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                if r.random() < 0.85:
                    c.set(x + dx, y + dy, shade(a, 0.9 + r.random() * 0.4))
    elif style == "moss":
        for x in range(16):
            for y in range(16):
                if r.random() < 0.18:
                    c.set(x, y, shade(a, 0.8 + r.random() * 0.4))
    elif style == "glow":
        for x in range(16):
            for y in range(16):
                dd = abs(x - 7.5) + abs(y - 7.5)
                c.set(x, y, shade(a, 1.25 - dd / 20 + r.random() * 0.1))
    elif style == "soil":
        for x in range(16):
            for y in range(16):
                if r.random() < 0.12:
                    c.set(x, y, shade(a, 0.9))
    elif style in ("wood", "station"):
        for y in range(16):
            for x in range(16):
                f = 0.85 + 0.15 * math.sin(x * 0.9 + r.random()) + (0.1 if y % 4 == 0 else 0)
                c.set(x, y, shade(base, f))
        for x in range(16):
            c.set(x, 0, shade(base, 0.5))
            c.set(x, 15, shade(base, 0.5))
        if style == "station":
            for (x, y) in doll_mask(0.6, 8, 14):
                c.set(x, y, DOLL_RED if (x + y) % 3 else GOLD)
            for x in range(16):
                c.set(x, 1, shade(a, 1.1))
    elif style == "lacquer":
        for x in range(16):
            for y in range(16):
                c.set(x, y, shade(DOLL_RED, 0.85 + 0.25 * ((x * 13 + y * 7) % 5) / 5))
        for t in range(0, 360, 30):
            x = 8 + 5 * math.cos(math.radians(t))
            y = 8 + 5 * math.sin(math.radians(t))
            c.set(round(x), round(y), GOLD)
        for (x, y) in disc(8, 8, 2.2):
            c.set(x, y, shade(a, 1.1))
    elif style == "glass":
        for x in range(16):
            for y in range(16):
                if x in (0, 15) or y in (0, 15):
                    c.set(x, y, shade(a, 0.7))
                else:
                    c.set(x, y, shade(a, 1.2), 90)
        for i in range(4):
            c.set(3 + i, 3 + i, (255, 255, 255), 200)
    elif style == "sand":
        for x in range(16):
            for y in range(16):
                if r.random() < 0.15:
                    c.set(x, y, shade(base, 1.15))
    elif style == "stone_rune":
        for (x, y) in diamond(8, 8, 5) - diamond(8, 8, 3):
            c.set(x, y, hx("7fd3ff"))
    c.save(path)


def paint_station_top(pal, seed, path):
    p, s, a, d = [hx(x) for x in pal]
    c = Canvas()
    r = rng(seed)
    for x in range(16):
        for y in range(16):
            edge = x in (0, 15) or y in (0, 15)
            c.set(x, y, shade(hx("9a6a40") if edge else shade(a, 0.7), 0.85 + r.random() * 0.2))
    for (x, y) in disc(8, 8, 4) - disc(8, 8, 2.5):
        c.set(x, y, GOLD)
    for (x, y) in disc(8, 8, 1.5):
        c.set(x, y, a)
    c.save(path)
