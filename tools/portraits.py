"""Portraits of every creature and boss for the website: a z-buffered render of the real model,
front three-quarter, transparent background, glow mask lit. Writes site/public/portraits/<id>.png.

  python3 tools/portraits.py [id ...]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mobs_hd"))
from preview import rot_m, apply, faces_of, persp_coeffs  # noqa: E402

ROOT = os.path.dirname(HERE)
A = os.path.join(ROOT, "src/main/resources/assets/matriochka")
OUT = os.path.join(ROOT, "site/public/portraits")


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def render(geo, tex, glow, yaw=35, pitch=-18, size=1024):
    g = geo["minecraft:geometry"][0]
    bones = {b["name"]: b for b in g["bones"]}

    def chain(name):
        out = []
        while name:
            out.append(bones[name])
            name = bones[name].get("parent")
        return out

    cam = mul(rot_m(pitch, 0, 0), rot_m(0, yaw, 0))
    polys = []
    for b in g["bones"]:
        for c in b.get("cubes", []):
            for corners, uv, n in faces_of(c):
                pts, nn = list(corners), n
                if "rotation" in c:
                    rx, ry, rz = c["rotation"]
                    m = rot_m(-rx, -ry, rz); pv = c.get("pivot", b["pivot"])
                    pts = [[a + q for a, q in zip(apply(m, [p[i] - pv[i] for i in range(3)]), pv)] for p in pts]
                    nn = apply(m, nn)
                for bb in chain(b["name"]):
                    if any(bb.get("rotation", [0, 0, 0])):
                        rx, ry, rz = bb["rotation"]
                        m = rot_m(-rx, -ry, rz); pv = bb["pivot"]  # GeckoLib turns X and Y the other way
                        pts = [[a + q for a, q in zip(apply(m, [p[i] - pv[i] for i in range(3)]), pv)] for p in pts]
                        nn = apply(m, nn)
                cp = [apply(cam, p) for p in pts]
                cn = apply(cam, nn)
                if cn[2] > 0.01:
                    continue
                light = 0.5 + 0.55 * max(0, -cn[2] * 0.55 + cn[1] * 0.55 + 0.15)
                polys.append((cp, uv, light))
    xs = [p[0] for cp, _, _ in polys for p in cp]
    ys = [p[1] for cp, _, _ in polys for p in cp]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.08
    sc = size / span
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    img = np.zeros((size, size, 4), np.float32)
    zb = np.full((size, size), 1e9)
    YY, XX = np.mgrid[0:size, 0:size] + 0.5
    for cp, (u, v, w, h), light in polys:
        if w <= 0 or h <= 0:
            continue
        dst = [((p[0] - cx) * sc + size / 2, (cy - p[1]) * sc + size / 2) for p in cp]
        x0, x1 = int(max(0, min(p[0] for p in dst))), int(min(size, max(p[0] for p in dst) + 2))
        y0, y1 = int(max(0, min(p[1] for p in dst))), int(min(size, max(p[1] for p in dst) + 2))
        if x1 <= x0 or y1 <= y0:
            continue
        Amat = np.array([[dst[i][0], dst[i][1], 1] for i in range(3)])
        try:
            k = np.linalg.solve(Amat, np.array([cp[i][2] for i in range(3)]))
            local = [(x - x0, y - y0) for x, y in dst]
            co = persp_coeffs(local, [(u, v), (u + w, v), (u + w, v + h), (u, v + h)])
        except Exception:
            continue
        bw, bh = x1 - x0, y1 - y0
        face = np.asarray(tex.transform((bw, bh), Image.PERSPECTIVE, co, Image.NEAREST))
        gl = np.asarray(glow.transform((bw, bh), Image.PERSPECTIVE, co, Image.NEAREST)) if glow else None
        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).polygon(local, fill=255)
        m = (np.asarray(mask) > 0) & (face[..., 3] > 0)
        z = k[0] * XX[y0:y1, x0:x1] + k[1] * YY[y0:y1, x0:x1] + k[2] - 0.02
        m &= z < zb[y0:y1, x0:x1]
        zsub = zb[y0:y1, x0:x1]; zsub[m] = z[m]
        col = face[..., :3].astype(np.float32) * light
        if gl is not None:
            lit = gl[..., 3] > 0
            col[lit] = face[..., :3][lit].astype(np.float32) * 1.15
        sub = img[y0:y1, x0:x1]
        sub[m, :3] = col[m]
        sub[m, 3] = 255
    out = Image.fromarray(img.clip(0, 255).astype(np.uint8), "RGBA")
    out = out.resize((size // 2, size // 2), Image.LANCZOS)
    # crop to the creature itself so the bottom of the picture is where it stands
    box = out.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if box:
        pad = 6
        out = out.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(out.width, box[2] + pad), min(out.height, box[3] + 2)))
    return out


def portrait(eid):
    geo = json.load(open(os.path.join(A, f"geckolib/models/entity/{eid}.geo.json")))
    tex = Image.open(os.path.join(A, f"textures/entity/{eid}.png")).convert("RGBA")
    gp = os.path.join(A, f"textures/entity/{eid}_glowmask.png")
    glow = Image.open(gp).convert("RGBA") if os.path.exists(gp) else None
    if glow is not None and glow.getbbox() is None:
        glow = None
    return render(geo, tex, glow)


def main():
    sys.path.insert(0, HERE)
    import content as C
    ids = sys.argv[1:] or [m["id"] for m in C.MOBS] + [b["id"] for b in C.BOSSES]
    os.makedirs(OUT, exist_ok=True)
    for eid in ids:
        portrait(eid).save(os.path.join(OUT, f"{eid}.png"), optimize=True)
    print(len(ids), "portraits")


if __name__ == "__main__":
    main()
