"""Contact sheets of the boss animations, to judge a move without starting the game.

  python3 tools/anim_preview.py [boss_id ...] [--only slug] [--yaw 40] [--frames 7]

Reads the generated model, texture and animation file of each boss (run tools/gen.py or tools/bosses_hd.py
first) and evaluates the animations the way GeckoLib does: the static rotation of a bone plus its keyframed
rotation, X and Y turned the other way, Z as is; position offsets in model units; scale around the pivot;
catmullrom, linear, step and the named easings, each easing shaping the segment that ends on its keyframe.
Writes docs-wiki-drafts/boss-anims/<boss>/<attack>.png: one row per part (windup, strike, recover), frames
left to right, a fixed camera for the whole sheet so lunges, jumps and drops read against the ground line.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = os.path.join(ROOT, "src/main/resources/assets/matriochka")
OUT = os.path.join(ROOT, "docs-wiki-drafts/boss-anims")


# ---------------------------------------------------------------- easing (GeckoLib names, lower case)
def _back_in(x):
    c = 1.70158
    return (c + 1) * x ** 3 - c * x ** 2


def _bounce_out(x):
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d
        return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d
        return n * x * x + 0.9375
    x -= 2.625 / d
    return n * x * x + 0.984375


def _elastic_out(x):
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1


BASE = {
    "sine": lambda x: 1 - math.cos(x * math.pi / 2),
    "quad": lambda x: x * x,
    "cubic": lambda x: x ** 3,
    "quart": lambda x: x ** 4,
    "quint": lambda x: x ** 5,
    "expo": lambda x: 0 if x == 0 else 2 ** (10 * x - 10),
    "circ": lambda x: 1 - math.sqrt(max(0.0, 1 - x * x)),
    "back": _back_in,
    "elastic": lambda x: 1 - _elastic_out(1 - x),
    "bounce": lambda x: 1 - _bounce_out(1 - x),
}


def ease_fn(name):
    n = name.lower()
    for kind, f in BASE.items():
        if n == "easein" + kind:
            return f
        if n == "easeout" + kind:
            return lambda x, f=f: 1 - f(1 - x)
        if n == "easeinout" + kind:
            return lambda x, f=f: f(2 * x) / 2 if x < 0.5 else 1 - f(2 - 2 * x) / 2
    return lambda x: x


# ---------------------------------------------------------------- channel evaluation
def channel_keys(ch):
    keys = []
    for t, k in sorted(ch.items(), key=lambda kv: float(kv[0])):
        if isinstance(k, list):
            keys.append((float(t), k, "linear"))
        else:
            keys.append((float(t), k["post"], k.get("lerp_mode") or k.get("easing") or "linear"))
    return keys


def sample(keys, t):
    if not keys:
        return None
    if t <= keys[0][0]:
        return list(keys[0][1])
    for i in range(1, len(keys)):
        t1, v1, mode = keys[i]
        t0, v0, _ = keys[i - 1]
        if t <= t1:
            p = 0 if t1 <= t0 else (t - t0) / (t1 - t0)
            if mode == "step":
                return list(v0)
            if mode == "catmullrom":
                vm = keys[i - 2][1] if i >= 2 else v0
                vp = keys[i + 1][1] if i + 1 < len(keys) else v1
                out = []
                for a, b, c, d in zip(vm, v0, v1, vp):
                    out.append(0.5 * ((2 * b) + (-a + c) * p + (2 * a - 5 * b + 4 * c - d) * p * p + (-a + 3 * b - 3 * c + d) * p ** 3))
                return out
            e = ease_fn(mode)(p) if mode != "linear" else p
            return [a + (b - a) * e for a, b in zip(v0, v1)]
    return list(keys[-1][1])


def rot_m(rx, ry, rz):
    rx, ry, rz = [math.radians(v) for v in (rx, ry, rz)]
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


def about(m3, pivot):
    m = np.eye(4)
    m[:3, :3] = m3
    p = np.array(pivot, float)
    m[:3, 3] = p - m3 @ p
    return m


def pose(geo, anim, t):
    """World matrix of every bone at time t of anim (None: the rest pose)."""
    bones = {b["name"]: b for b in geo["bones"]}
    chans = {}
    if anim:
        for bn, chs in anim.get("bones", {}).items():
            chans[bn] = {c: channel_keys(v) for c, v in chs.items()}
    mats = {}

    def world(name):
        if name in mats:
            return mats[name]
        b = bones[name]
        rot = list(b.get("rotation", [0, 0, 0]))
        pos, scl = [0, 0, 0], [1, 1, 1]
        c = chans.get(name, {})
        if "rotation" in c:
            rot = [a + d for a, d in zip(rot, sample(c["rotation"], t))]
        if "position" in c:
            pos = sample(c["position"], t)
        if "scale" in c:
            scl = sample(c["scale"], t)
        m3 = rot_m(-rot[0], -rot[1], rot[2]) @ np.diag(scl)
        local = about(m3, b["pivot"])
        local[:3, 3] += np.array(pos, float)
        par = b.get("parent")
        m = (world(par) if par else np.eye(4)) @ local
        mats[name] = m
        return m

    for n in bones:
        world(n)
    return mats


# ---------------------------------------------------------------- drawing
def face_colors(tex):
    px = np.asarray(tex.convert("RGBA")).astype(np.float32)
    cache = {}

    def col(u, v, w, h):
        key = (u, v, w, h)
        if key not in cache:
            sub = px[int(v):int(v + max(1, h)), int(u):int(u + max(1, w))]
            a = sub[..., 3:4] / 255
            cache[key] = (sub[..., :3] * a).sum((0, 1)) / max(1e-3, a.sum()) if a.sum() > 0 else np.array([128, 128, 128])
        return cache[key]
    return col


def cube_faces(c):
    (x, y, z), (w, h, d) = c["origin"], c["size"]
    i = c.get("inflate", 0)
    x0, y0, z0, x1, y1, z1 = x - i, y - i, z - i, x + w + i, y + h + i, z + d + i
    u, v = c["uv"]
    W, H, D = [max(1, math.ceil(s)) for s in (w, h, d)]
    return [
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (u + D, v, W, D), (0, 1, 0)),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)], (u + D + W, v, W, D), (0, -1, 0)),
        ([(x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (x1, y0, z0)], (u, v + D, D, H), (1, 0, 0)),
        ([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], (u + D, v + D, W, H), (0, 0, -1)),
        ([(x0, y1, z1), (x0, y1, z0), (x0, y0, z0), (x0, y0, z1)], (u + D + W, v + D, D, H), (-1, 0, 0)),
        ([(x1, y1, z1), (x0, y1, z1), (x0, y0, z1), (x1, y0, z1)], (u + 2 * D + W, v + D, W, H), (0, 0, 1)),
    ]


class Model:
    def __init__(self, eid):
        self.eid = eid
        self.geo = json.load(open(os.path.join(A, f"geckolib/models/entity/{eid}.geo.json")))["minecraft:geometry"][0]
        self.anims = json.load(open(os.path.join(A, f"geckolib/animations/entity/{eid}.animation.json")))["animations"]
        tex = Image.open(os.path.join(A, f"textures/entity/{eid}.png")).convert("RGBA")
        col = face_colors(tex)
        gp = os.path.join(A, f"textures/entity/{eid}_glowmask.png")
        glow = np.asarray(Image.open(gp).convert("RGBA")) if os.path.exists(gp) else None
        self.faces = []  # (bone, 4x4 corners (homogeneous), normal, colour, lit)
        for b in self.geo["bones"]:
            for c in b.get("cubes", []):
                cm = np.eye(4)
                if "rotation" in c:
                    rx, ry, rz = c["rotation"]
                    cm = about(rot_m(-rx, -ry, rz), c.get("pivot", b["pivot"]))
                for corners, (u, v, w, h), n in cube_faces(c):
                    pts = cm @ np.array([list(p) + [1] for p in corners], float).T
                    nn = cm[:3, :3] @ np.array(n, float)
                    lit = False
                    if glow is not None and w > 0 and h > 0:
                        sub = glow[int(v):int(v + h), int(u):int(u + w), 3]
                        lit = sub.size > 0 and sub.mean() > 100
                    self.faces.append((b["name"], pts, nn, col(u, v, w, h), lit))

    def project(self, mats, cam):
        polys = []
        for bone, pts, n, colour, lit in self.faces:
            m = mats[bone]
            wp = (m @ pts)[:3]
            wn = m[:3, :3] @ n
            cp = cam @ wp
            cn = cam @ wn
            if cn[2] > 0.01:
                continue
            nl = np.linalg.norm(cn) or 1
            light = 0.5 + 0.55 * max(0, (-cn[2] * 0.55 + cn[1] * 0.55) / nl + 0.15)
            c = colour * (1.15 if lit else light)
            polys.append((cp[2].mean(), cp, tuple(int(max(0, min(255, v))) for v in c)))
        return polys


def camera(yaw, pitch):
    return rot_m(pitch, 0, 0) @ rot_m(0, yaw, 0)


def render_frames(model, anim, times, cam, box, cell):
    (xmin, xmax, ymin, ymax) = box
    span = max(xmax - xmin, ymax - ymin)
    sc = cell * 2 * 0.92 / span
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    out = []
    ground = cam @ np.array([[-40, 40, 40, -40], [0, 0, 0, 0], [-40, -40, 40, 40]], float)
    for t in times:
        img = Image.new("RGB", (cell * 2, cell * 2), (30, 30, 34))
        dr = ImageDraw.Draw(img)
        g = [((p[0] - cx) * sc + cell, (cy - p[1]) * sc + cell) for p in ground.T]
        dr.polygon(g, fill=(46, 44, 42), outline=(70, 66, 60))
        polys = model.project(pose(model.geo, anim, t), cam)
        for _, cp, colour in sorted(polys, key=lambda p: -p[0]):
            pts = [((x - cx) * sc + cell, (cy - y) * sc + cell) for x, y in zip(cp[0], cp[1])]
            dr.polygon(pts, fill=colour)
        out.append(img.resize((cell, cell), Image.LANCZOS))
    return out


def bounds(model, anims_times, cam):
    xs, ys = [], []
    for anim, times in anims_times:
        for t in times:
            mats = pose(model.geo, anim, t)
            for bone, pts, _, _, _ in model.faces[::3]:
                cp = cam @ (mats[bone] @ pts)[:3]
                xs.extend(cp[0])
                ys.extend(cp[1])
    pad = 4
    return min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad


def sheet(model, rows, path, frames=7, yaw=40, pitch=-14, cell=190):
    """rows: [(label, anim name)]: one strip of `frames` frames per animation."""
    cam = camera(pitch=pitch, yaw=yaw)
    prepared = []
    for label, name in rows:
        anim = model.anims.get(name)
        if anim is None:
            continue
        L = float(anim.get("animation_length", 1.0))
        times = [L * i / (frames - 1) for i in range(frames)]
        prepared.append((label, name, anim, times, L))
    if not prepared:
        return False
    box = bounds(model, [(a, ts) for _, _, a, ts, _ in prepared] + [(None, [0])], cam)
    # parts flung far away (a thrown block, a charge) must not shrink the boss to a speck
    rest = bounds(model, [(None, [0])], cam)
    w, h = rest[1] - rest[0], rest[3] - rest[2]
    box = (max(box[0], rest[0] - 0.7 * w), min(box[1], rest[1] + 0.7 * w), max(box[2], rest[2] - 0.35 * h), min(box[3], rest[3] + 0.5 * h))
    lab = 150
    img = Image.new("RGB", (lab + cell * frames, cell * len(prepared)), (22, 22, 26))
    dr = ImageDraw.Draw(img)
    for r, (label, name, anim, times, L) in enumerate(prepared):
        for i, fr in enumerate(render_frames(model, anim, times, cam, box, cell)):
            img.paste(fr, (lab + i * cell, r * cell))
            dr.text((lab + i * cell + 4, r * cell + 4), f"{times[i]:.2f}s", fill=(200, 200, 190))
        dr.text((6, r * cell + 8), label, fill=(235, 220, 180))
        dr.text((6, r * cell + 24), f"{L:.2f}s  {anim.get('loop')}", fill=(160, 160, 150))
        words = name.split(".")
        dr.text((6, r * cell + 40), ".".join(words[2:]) if len(words) > 2 else name, fill=(120, 150, 170))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, optimize=True)
    return True


def boss_sheets(eid, only=None, frames=7, yaw=40):
    model = Model(eid)
    groups = {}
    for name in model.anims:
        p = name.split(".")
        if len(p) >= 4 and p[0] == "attack" and p[1] == eid:
            groups.setdefault(p[2], []).append(name)
        elif len(p) == 3 and p[0] == "misc" and p[1] == eid:
            groups.setdefault("phase_death", []).append(name)
    written = []
    for slug, names in groups.items():
        if only and slug not in only:
            continue
        order = {"windup": 0, "strike": 1, "recover": 2, "phase": 3, "death": 4}
        names.sort(key=lambda n: (n.split(".")[-1][:1] == "w" and n.split(".")[-1][1:].isdigit(), n.split(".")[4:] if len(n.split(".")) > 4 else [], order.get(n.split(".")[3] if len(n.split(".")) > 3 else n.split(".")[2], 9)))
        rows = [(n.split(".")[-1] if not (n.split(".")[-1][:1] == "w" and n.split(".")[-1][1:].isdigit()) else ".".join(n.split(".")[-2:]), n) for n in names]
        if slug == "phase_death":
            rows = [(n.split(".")[-1], n) for n in names]
        path = os.path.join(OUT, eid, f"{slug}.png")
        if sheet(model, rows, path, frames=frames, yaw=yaw):
            written.append(path)
    return written


def main():
    args = sys.argv[1:]
    only, frames, yaw, ids = None, 7, 40, []
    i = 0
    while i < len(args):
        if args[i] == "--only":
            only = set(args[i + 1].split(","))
            i += 2
        elif args[i] == "--frames":
            frames = int(args[i + 1])
            i += 2
        elif args[i] == "--yaw":
            yaw = float(args[i + 1])
            i += 2
        else:
            ids.append(args[i])
            i += 1
    if not ids:
        sys.path.insert(0, HERE)
        import content as C
        ids = [b["id"] for b in C.BOSSES] + [C.WORLD_ZERO_BOSS["id"]]
    for eid in ids:
        for p in boss_sheets(eid, only, frames, yaw):
            print(os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
