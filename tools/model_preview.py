"""A quick offline preview of block models (vanilla JSON elements) for design review, without the game.

    python3 tools/model_preview.py out.png matrix_workbench soul_altar ...

Draws each model at three quarters from the front-left, lit from the top-left, texel by texel with the painter's
algorithm. Not a faithful renderer (no AO, no culling subtleties), only a fast way to judge silhouettes and colours.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), "..", "src/main/resources/assets/matriochka")


def tex(path, cache={}):
    if path not in cache:
        ns, p = path.split(":")
        cache[path] = Image.open(os.path.join(ROOT, "textures", p + ".png")).convert("RGBA")
    return cache[path]


def rot(v, axis, ang, o):
    a = math.radians(ang)
    x, y, z = v[0] - o[0], v[1] - o[1], v[2] - o[2]
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        y, z = y * c - z * s, y * s + z * c
    elif axis == "y":
        x, z = x * c + z * s, -x * s + z * c
    else:
        x, y = x * c - y * s, x * s + y * c
    return (x + o[0], y + o[1], z + o[2])


FACES = {  # corners (u0v0, u1v0, u1v1, u0v1) as functions of from/to, and the normal
    "north": (lambda f, t: [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])], (0, 0, -1)),
    "south": (lambda f, t: [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])], (0, 0, 1)),
    "west": (lambda f, t: [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])], (-1, 0, 0)),
    "east": (lambda f, t: [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])], (1, 0, 0)),
    "up": (lambda f, t: [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])], (0, 1, 0)),
    "down": (lambda f, t: [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])], (0, -1, 0)),
}


def render(model, size=360, yaw=-35.0, pitch=-28.0, bg=(54, 58, 66, 255)):
    textures = model["textures"]

    def resolve(ref):
        while ref.startswith("#"):
            ref = textures[ref[1:]]
        return ref

    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def view(p, d=False):
        # model space (north = -z faces the viewer), viewer turned by yaw about y, then tilted by pitch
        x, y, z = (p if d else (p[0] - 8, p[1] - 8, p[2] - 8))
        x, z = x * cy - z * sy, x * sy + z * cy
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z

    k = size / 28.0
    polys = []
    light = (-0.5, 0.75, -0.45)
    for e in model["elements"]:
        f, t = e["from"], e["to"]
        r = e.get("rotation")
        glow = e.get("light_emission", 0) > 0
        for name, face in e["faces"].items():
            corners, n = FACES[name][0](f, t), FACES[name][1]
            if r:
                corners = [rot(c, r["axis"], r["angle"], r["origin"]) for c in corners]
                n = rot(n, r["axis"], r["angle"], (0, 0, 0))
            vn = view(n, True)
            if vn[2] > 0.01:  # facing away (z grows away from the viewer)
                continue
            shade = 1.0 if glow else 0.55 + 0.45 * max(0.0, sum(a * b for a, b in zip(n, light)) / 1.05)
            img = tex(resolve(face["texture"]))
            u0, v0, u1, v1 = face["uv"]
            W, H = img.size
            nu = max(1, int(round(abs(u1 - u0) * W / 16)))
            nv = max(1, int(round(abs(v1 - v0) * H / 16)))
            P = [view(c) for c in corners]
            for i in range(nu):
                for j in range(nv):
                    a, b, c2, d = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv

                    def at(s, q):
                        top = [P[0][m] + (P[1][m] - P[0][m]) * s for m in range(3)]
                        bot = [P[3][m] + (P[2][m] - P[3][m]) * s for m in range(3)]
                        return [top[m] + (bot[m] - top[m]) * q for m in range(3)]
                    q = [at(a, c2), at(b, c2), at(b, d), at(a, d)]
                    px = u0 + (u1 - u0) * (i + 0.5) / nu
                    py = v0 + (v1 - v0) * (j + 0.5) / nv
                    col = img.getpixel((min(W - 1, int(px / 16 * W)), min(H - 1, int(py / 16 * H))))
                    if col[3] < 128:
                        continue
                    col = tuple(min(255, int(ch * shade)) for ch in col[:3])
                    depth = sum(v[2] for v in q) / 4
                    polys.append((depth, [(size / 2 + v[0] * k, size * 0.56 - v[1] * k) for v in q], col))
    polys.sort(key=lambda p: -p[0])
    im = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    for _, pts, col in polys:
        dr.polygon(pts, fill=col, outline=col)
    return im


if __name__ == "__main__":
    out, ids = sys.argv[1], sys.argv[2:]
    tiles = [render(json.load(open(os.path.join(ROOT, "models/block", i + ".json")))) for i in ids]
    cols = min(5, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * 360, rows * 360), (40, 42, 48, 255))
    for n, t in enumerate(tiles):
        sheet.paste(t, ((n % cols) * 360, (n // cols) * 360))
    sheet.save(out)
