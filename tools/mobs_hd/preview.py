"""Renders a GeckoLib model to PNG views so a design can be judged without the game.

  python3 tools/mobs_hd/preview.py <creature_id> [out_dir]
builds the creature from its module into a temporary asset folder (the real assets are untouched)
and writes <out_dir>/<id>.png: front three-quarter, side, and back three-quarter views.
"""
import json
import math
import os
import sys
import tempfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))


def rot_m(rx, ry, rz):
    rx, ry, rz = [math.radians(v) for v in (rx, ry, rz)]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    Y = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    Z = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mul(mul(Z, Y), X)


def apply(m, p):
    return [sum(m[i][k] * p[k] for k in range(3)) for i in range(3)]


def faces_of(c):
    (x, y, z), (w, h, d) = c["origin"], c["size"]
    i = c.get("inflate", 0)
    x0, y0, z0, x1, y1, z1 = x - i, y - i, z - i, x + w + i, y + h + i, z + d + i
    u, v = c["uv"]
    W, H, Dd = [max(1, math.ceil(s)) for s in (w, h, d)]
    # (corners, uv rect, normal)
    return [
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (u + Dd, v, W, Dd), (0, 1, 0)),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)], (u + Dd + W, v, W, Dd), (0, -1, 0)),
        ([(x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (x1, y0, z0)], (u, v + Dd, Dd, H), (1, 0, 0)),
        ([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], (u + Dd, v + Dd, W, H), (0, 0, -1)),
        ([(x0, y1, z1), (x0, y1, z0), (x0, y0, z0), (x0, y0, z1)], (u + Dd + W, v + Dd, Dd, H), (-1, 0, 0)),
        ([(x1, y1, z1), (x0, y1, z1), (x0, y0, z1), (x1, y0, z1)], (u + 2 * Dd + W, v + Dd, W, H), (0, 0, 1)),
    ]


def persp_coeffs(dst, src):
    import numpy as np
    A, B = [], []
    for (X, Y), (x, y) in zip(dst, src):
        A.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y]); B.append(x)
        A.append([0, 0, 0, X, Y, 1, -y * X, -y * Y]); B.append(y)
    return list(np.linalg.lstsq(np.array(A, float), np.array(B, float), rcond=None)[0])


def render(geo, tex, yaw, pitch=-22, size=420):
    g = geo["minecraft:geometry"][0]
    bones = {b["name"]: b for b in g["bones"]}

    def chain(name):
        out = []
        while name:
            b = bones[name]
            out.append(b)
            name = b.get("parent")
        return out

    polys = []
    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    cam = mul(rot_m(pitch, 0, 0), rot_m(0, yaw, 0))
    for b in g["bones"]:
        for c in b.get("cubes", []):
            for corners, uv, n in faces_of(c):
                pts = list(corners)
                nn = n
                if "rotation" in c:
                    m = rot_m(*c["rotation"]); pv = c.get("pivot", b["pivot"])
                    pts = [[a + bb for a, bb in zip(apply(m, [p[i] - pv[i] for i in range(3)]), pv)] for p in pts]
                    nn = apply(m, nn)
                for bb in chain(b["name"]):
                    if "rotation" in bb:
                        m = rot_m(*bb["rotation"]); pv = bb["pivot"]
                        pts = [[a + q for a, q in zip(apply(m, [p[i] - pv[i] for i in range(3)]), pv)] for p in pts]
                        nn = apply(m, nn)
                cp = [apply(cam, p) for p in pts]
                cn = apply(cam, nn)
                if cn[2] > 0.01:
                    continue
                light = 0.55 + 0.45 * max(0, -cn[2] * 0.6 + cn[1] * 0.5 + 0.2)
                polys.append((sum(p[2] for p in cp) / 4, cp, uv, light))
    if not polys:
        return Image.new("RGBA", (size, size))
    xs = [p[0] for _, cp, _, _ in polys for p in cp]; ys = [p[1] for _, cp, _, _ in polys for p in cp]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.1
    sc = size / span
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    img = Image.new("RGBA", (size, size), (34, 26, 22, 255))
    for _, cp, (u, v, w, h), light in sorted(polys, key=lambda p: -p[0]):
        dst = [((p[0] - cx) * sc + size / 2, (cy - p[1]) * sc + size / 2) for p in cp]
        if w <= 0 or h <= 0:
            continue
        src = [(u, v), (u + w, v), (u + w, v + h), (u, v + h)]
        try:
            co = persp_coeffs(dst, src)
        except Exception:
            continue
        face = tex.transform((size, size), Image.PERSPECTIVE, co, Image.NEAREST)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).polygon(dst, fill=255)
        alpha = face.getchannel("A").point(lambda a: 255 if a > 0 else 0)
        from PIL import ImageChops
        mask = ImageChops.multiply(mask, alpha)
        shaded = face.convert("RGB").point(lambda c: int(c * light))
        img.paste(shaded, (0, 0), mask)
    return img


def main():
    mid = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(tempfile.gettempdir(), "mob_previews")
    os.makedirs(out_dir, exist_ok=True)
    import bosses_hd
    import registry
    tmp = tempfile.mkdtemp()
    for sub in ("geckolib/models/entity", "geckolib/animations/entity", "textures/entity"):
        os.makedirs(os.path.join(tmp, sub), exist_ok=True)
    bosses_hd.A = tmp
    rig = registry.build(mid)
    geo = json.load(open(os.path.join(tmp, f"geckolib/models/entity/{mid}.geo.json")))
    tex = Image.open(os.path.join(tmp, f"textures/entity/{mid}.png")).convert("RGBA")
    views = [render(geo, tex, y) for y in (35, 90, 215)]
    sheet = Image.new("RGB", (420 * 3 + 20, 440), (20, 15, 12))
    for i, v in enumerate(views):
        sheet.paste(v, (i * 425 + 5, 10))
    big = Image.new("RGB", (sheet.width, sheet.height + tex.height * 2 + 20), (20, 15, 12))
    big.paste(sheet, (0, 0))
    big.paste(tex.resize((tex.width * 2, tex.height * 2), Image.NEAREST), (5, 450), tex.resize((tex.width * 2, tex.height * 2), Image.NEAREST))
    path = os.path.join(out_dir, f"{mid}.png")
    big.save(path)
    print(path, "dims", rig)


if __name__ == "__main__":
    main()
