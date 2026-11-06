"""Matriochka Pack icon: three lacquer dolls tied together with a gold ribbon, the mod's doll in front.

Same family as the mod's logo (tools/logo.py: red lacquer, gold leaf, the block in the belly window) but a bundle
of dolls, so the pack and the mod do not look alike in a launcher list. Drawn at 4x and downsampled.
    python3 tools/pack_icon.py      # branding/modpack/icon.png (512) and icon-64.png (preview)
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from logo import BLACK, GOLD, GOLD_D, GOLD_L, RED, RED_L, block, doll_shape, ornaments

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "branding", "modpack")
INK = (30, 22, 18)
GREEN = (38, 98, 64)
BLUE = (36, 66, 128)
S = 4


def silhouette(n, cx, top, h):
    m = Image.new("L", (n, n), 0)
    doll_shape(ImageDraw.Draw(m), cx, top, h, 255)
    return m


def doll(img, cx, top, h, body, ring, k, belly):
    """One doll: shadow, black edge, ring, lacquer body, highlight, face, then its belly motif."""
    n = img.size[0]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    doll_shape(ImageDraw.Draw(sh), cx + 8 * k, top + 12 * k, h, (0, 0, 0, 140))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * k)))
    d = ImageDraw.Draw(img)
    e = max(8, h * 0.014)
    doll_shape(d, cx, top, h, BLACK)
    doll_shape(d, cx, top + e, h - 2 * e, ring)
    doll_shape(d, cx, top + 1.8 * e, h - 3.6 * e, body)
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([cx - h * 0.27, top + h * 0.38, cx - h * 0.13, top + h * 0.80], fill=(255, 255, 255, 40))
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(16 * k)))
    ornaments(d, cx, top + 1.8 * e, h - 3.6 * e, k)
    belly(d, cx, top, h, k)
    return silhouette(n, cx, top, h)


def flower_belly(petal, heart):
    def draw(d, cx, top, h, k):
        fy, r = top + h * 0.64, h * 0.075
        for i in range(6):
            a = i / 6 * math.tau
            px, py = cx + math.cos(a) * r, fy + math.sin(a) * r
            d.ellipse([px - r * 0.62, py - r * 0.62, px + r * 0.62, py + r * 0.62], fill=petal, outline=BLACK, width=int(3 * k))
        d.ellipse([cx - r * 0.55, fy - r * 0.55, cx + r * 0.55, fy + r * 0.55], fill=heart, outline=BLACK, width=int(3 * k))
        for sx in (-1, 1):
            lx, ly = cx + sx * h * 0.2, top + h * 0.68
            d.ellipse([lx - h * 0.035, ly - h * 0.06, lx + h * 0.035, ly + h * 0.06], fill=petal, outline=BLACK, width=int(2 * k))
    return draw


def window_belly(d, cx, top, h, k):
    """The mod logo's belly: a window on the next doll holding the block."""
    bw, btop = h * 0.40, top + h * 0.47
    d.ellipse([cx - bw / 2 - 8 * k, btop - 8 * k, cx + bw / 2 + 8 * k, btop + bw * 1.06 + 8 * k], fill=GOLD, outline=BLACK, width=int(5 * k))
    d.ellipse([cx - bw / 2, btop, cx + bw / 2, btop + bw * 1.06], fill=BLACK)
    ih = bw * 0.98
    doll_shape(d, cx, btop + bw * 0.04, ih, GOLD_D)
    doll_shape(d, cx, btop + bw * 0.04 + 5 * k, ih - 10 * k, INK)
    block(d, cx, btop + bw * 0.04 + ih * 0.62, ih * 0.24)


def ribbon(img, mask, y, w, k):
    """A gold band around the bundle, drawn only over the dolls, with a knot in front."""
    n = img.size[0]
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, y - w / 2 - 5 * k, n, y + w / 2 + 5 * k], fill=BLACK)
    bd.rectangle([0, y - w / 2, n, y + w / 2], fill=GOLD)
    bd.rectangle([0, y - w / 2, n, y - w / 6], fill=GOLD_L)
    for x in range(0, n, int(28 * k)):
        bd.rectangle([x, y + w / 6, x + 10 * k, y + w / 2 - 4 * k], fill=GOLD_D)
    clip = Image.new("RGBA", img.size, (0, 0, 0, 0))
    clip.paste(band, (0, 0), mask)
    img.alpha_composite(clip)


def bow(img, cx, y, s, k):
    d = ImageDraw.Draw(img)
    lw = int(5 * k)
    for sx in (-1, 1):
        loop = [(cx, y), (cx + sx * s * 1.25, y - s * 0.75), (cx + sx * s * 1.4, y + s * 0.05), (cx + sx * s * 1.2, y + s * 0.7)]
        d.polygon(loop, fill=GOLD, outline=BLACK, width=lw)
        d.polygon([(cx, y), (cx + sx * s * 1.05, y - s * 0.42), (cx + sx * s * 1.05, y + s * 0.35)], fill=GOLD_D)
        tail = [(cx - sx * s * 0.1, y), (cx + sx * s * 0.55, y + s * 1.5), (cx + sx * s * 0.3, y + s * 1.7), (cx + sx * s * 0.05, y + s * 1.35)]
        d.polygon(tail, fill=GOLD_L, outline=BLACK, width=lw)
    d.rounded_rectangle([cx - s * 0.36, y - s * 0.4, cx + s * 0.36, y + s * 0.4], radius=s * 0.15, fill=GOLD_L, outline=BLACK, width=lw)


def icon(size=512):
    n = size * S
    k = n / 1024
    img = Image.new("RGBA", (n, n), INK + (255,))
    d = ImageDraw.Draw(img)
    for x in range(0, n, int(64 * k)):
        d.line([(x, 0), (x, n)], fill=(36, 26, 20), width=int(2 * k))
    # a warm glow behind the dolls
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([n * 0.12, n * 0.18, n * 0.88, n * 0.98], fill=(150, 40, 24, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90 * k)))
    # two smaller dolls behind, the mod's doll in front
    base = n * 0.955
    hs, hc = n * 0.60, n * 0.86
    m1 = doll(img, n * 0.235, base - hs, hs, GREEN, GOLD, k, flower_belly(GOLD_L, RED))
    m2 = doll(img, n * 0.765, base - hs, hs, BLUE, GOLD, k, flower_belly(GOLD_L, RED_L))
    back = ImageChops.lighter(m1, m2)
    ribbon(img, back, base - hs * 0.2, n * 0.05, k)
    mc = doll(img, n * 0.5, base - hc, hc, RED, GOLD, k, window_belly)
    ribbon(img, mc, base - hs * 0.2, n * 0.05, k)
    bow(img, n * 0.5, base - hs * 0.2, n * 0.072, k)
    # gold frame
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([18 * k, 18 * k, n - 18 * k, n - 18 * k], radius=60 * k, outline=GOLD_D, width=int(6 * k))
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    im = icon(512)
    im.save(os.path.join(OUT, "icon.png"))
    print("pack icon ok")
