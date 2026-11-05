"""Matriochka logo: a lacquer doll holding a smaller doll holding a block. Drawn at 4x and downsampled."""
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "branding")
RED, RED_D, RED_L = (176, 34, 26), (112, 18, 14), (214, 66, 48)
BLACK, GOLD, GOLD_L, GOLD_D = (24, 16, 12), (214, 160, 62), (246, 210, 120), (150, 102, 34)
FACE, CHEEK = (246, 222, 196), (222, 92, 80)
S = 4


def doll_shape(d, cx, top, h, fill, outline=None, width=0):
    """Matryoshka silhouette: head circle merged into a rounded belly."""
    w = h * 0.66
    head_r = h * 0.215
    hy = top + head_r
    belly_top = top + h * 0.30
    pts = []
    # build outline as a polygon (right side, then mirror)
    right = []
    for i in range(0, 181):
        a = math.radians(-90 + i)  # head from top to right side
        x = cx + math.cos(a) * head_r
        y = hy + math.sin(a) * head_r
        if y > hy + head_r * 0.55:
            break
        right.append((x, y))
    # neck into shoulders and belly (superellipse)
    for i in range(0, 101):
        t = i / 100
        ang = -math.pi / 2 + t * math.pi
        bx = cx + (w / 2) * (abs(math.cos(ang)) ** 0.82) * (1 if math.cos(ang) >= 0 else -1)
        by = belly_top + (h - (belly_top - top)) / 2 + (h - (belly_top - top)) / 2 * math.sin(ang)
        if by < right[-1][1]:
            continue
        right.append((bx, by))
    left = [(2 * cx - x, y) for (x, y) in reversed(right)]
    pts = right + left
    d.polygon(pts, fill=fill, outline=outline, width=width)
    return pts


def ornaments(d, cx, top, h, k):
    w = h * 0.66
    head_r = h * 0.215
    hy = top + head_r
    # face
    fr = head_r * 0.66
    d.ellipse([cx - fr, hy - fr * 0.82, cx + fr, hy + fr * 1.0], fill=FACE, outline=BLACK, width=max(2, int(3 * k)))
    # hair parting
    d.pieslice([cx - fr, hy - fr * 0.82, cx + fr, hy + fr * 0.6], 180, 360, fill=BLACK)
    d.ellipse([cx - fr * 0.92, hy - fr * 0.25, cx + fr * 0.92, hy + fr * 0.98], fill=FACE)
    # eyes, cheeks, mouth
    for sx in (-1, 1):
        ex = cx + sx * fr * 0.36
        d.ellipse([ex - fr * 0.09, hy + fr * 0.12, ex + fr * 0.09, hy + fr * 0.3], fill=BLACK)
        d.ellipse([cx + sx * fr * 0.55 - fr * 0.17, hy + fr * 0.42, cx + sx * fr * 0.55 + fr * 0.17, hy + fr * 0.62], fill=CHEEK)
    d.ellipse([cx - fr * 0.12, hy + fr * 0.6, cx + fr * 0.12, hy + fr * 0.76], fill=RED_D)
    # scarf line



def block(d, cx, cy, s):
    """Isometric grass-like block in the doll's colours (gold top, lacquer sides)."""
    t = [(cx, cy - s), (cx + s * 0.87, cy - s * 0.5), (cx, cy), (cx - s * 0.87, cy - s * 0.5)]
    l = [(cx - s * 0.87, cy - s * 0.5), (cx, cy), (cx, cy + s), (cx - s * 0.87, cy + s * 0.5)]
    r = [(cx, cy), (cx + s * 0.87, cy - s * 0.5), (cx + s * 0.87, cy + s * 0.5), (cx, cy + s)]
    d.polygon(t, fill=GOLD_L, outline=BLACK, width=max(2, int(s * 0.06)))
    d.polygon(l, fill=RED, outline=BLACK, width=max(2, int(s * 0.06)))
    d.polygon(r, fill=RED_D, outline=BLACK, width=max(2, int(s * 0.06)))
    # pixel speckles on the sides
    for i in range(3):
        for j in range(3):
            if (i + j) % 2 == 0:
                x = cx - s * 0.87 + (i + 0.5) * s * 0.29
                y = cy - s * 0.5 + (i + 0.5) * s * 0.165 + (j + 0.6) * s * 0.3
                d.rectangle([x - s * 0.05, y - s * 0.05, x + s * 0.05, y + s * 0.05], fill=RED_L)


def logo(size, background=None):
    N = size * S
    img = Image.new("RGBA", (N, N), background or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = N / 1024
    cx = N / 2
    top, h = N * 0.06, N * 0.90
    # shadow
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    doll_shape(ImageDraw.Draw(sh), cx + 10 * k, top + 16 * k, h, (0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * k)))
    # outer doll: black edge, gold ring, red lacquer
    doll_shape(d, cx, top, h, BLACK)
    doll_shape(d, cx, top + 12 * k, h - 24 * k, GOLD)
    doll_shape(d, cx, top + 22 * k, h - 44 * k, RED)
    # lacquer highlight
    hl = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.ellipse([cx - h * 0.27, top + h * 0.36, cx - h * 0.12, top + h * 0.82], fill=(255, 255, 255, 46))
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(18 * k)))
    ornaments(d, cx, top + 22 * k, h - 44 * k, k)
    # belly window: the next doll inside, then the block
    bw, btop = h * 0.40, top + h * 0.47
    d.ellipse([cx - bw / 2 - 10 * k, btop - 10 * k, cx + bw / 2 + 10 * k, btop + bw * 1.06 + 10 * k], fill=GOLD, outline=BLACK, width=int(6 * k))
    d.ellipse([cx - bw / 2, btop, cx + bw / 2, btop + bw * 1.06], fill=BLACK)
    ih = bw * 0.98
    doll_shape(d, cx, btop + bw * 0.04, ih, GOLD_D)
    doll_shape(d, cx, btop + bw * 0.04 + 6 * k, ih - 12 * k, (30, 22, 18))
    block(d, cx, btop + bw * 0.04 + ih * 0.62, ih * 0.22)
    # gold leaves around the belly window, like a painted wreath
    wcx, wcy = cx, btop + bw * 0.53
    rx, ry = bw / 2 + 34 * k, bw * 0.53 + 34 * k
    for i in range(18):
        a = i / 18 * math.tau
        lx, ly = wcx + math.cos(a) * rx, wcy + math.sin(a) * ry
        ang = a + math.pi / 2
        pts = []
        for t in range(13):
            u = t / 12
            wdt = math.sin(u * math.pi) * 9 * k
            L = 30 * k
            px_ = lx + math.cos(ang) * (u - 0.5) * L
            py_ = ly + math.sin(ang) * (u - 0.5) * L
            pts.append((px_ - math.sin(ang) * wdt, py_ + math.cos(ang) * wdt))
        for t in range(12, -1, -1):
            u = t / 12
            wdt = math.sin(u * math.pi) * 9 * k
            L = 30 * k
            px_ = lx + math.cos(ang) * (u - 0.5) * L
            py_ = ly + math.sin(ang) * (u - 0.5) * L
            pts.append((px_ + math.sin(ang) * wdt, py_ - math.cos(ang) * wdt))
        d.polygon(pts, fill=GOLD_L if i % 2 else GOLD, outline=BLACK)
        if i % 3 == 0:
            bx, by = wcx + math.cos(a) * (rx + 22 * k), wcy + math.sin(a) * (ry + 22 * k)
            rr = 9 * k
            d.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=RED_L, outline=BLACK, width=int(2 * k))
    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for s in (1024, 512, 256, 128):
        logo(s).save(os.path.join(OUT, f"logo-{s}.png"))
    # square icons on lacquer black for Discord / GitHub avatar
    bg = Image.new("RGBA", (1024, 1024), (24, 16, 12, 255))
    d = ImageDraw.Draw(bg)
    for i in range(0, 1024, 64):
        d.line([(i, 0), (i, 1024)], fill=(32, 22, 17), width=2)
    bg.alpha_composite(logo(1024).resize((900, 900), Image.LANCZOS), (62, 70))
    bg.save(os.path.join(OUT, "icon-square-1024.png"))
    logo(128).save(os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/matriochka/icon.png"))
    print("logo ok")
