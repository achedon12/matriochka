"""Hand-designed boss models for Matriochka (GeckoLib / Blockbench format).

Each boss is a real rig: joints at the pivots, overlapping parts so rotations open no gaps, secondary bones
(tails, capes, wings, chains, orbiting stones) and painted materials with an emissive glow mask.
Animations are keyframed poses with catmullrom curves: anticipation before every strike, follow-through after,
offset timing between parent and child bones. Files open as-is in Blockbench (GeckoLib entity models).
"""
import json
import math
import os
import random
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
A = os.path.join(ROOT, "src/main/resources/assets/matriochka")


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mixc(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


# ---------------------------------------------------------------- materials
# name: (base, accent, pattern, emissive)
MAT = {
    "stone": ("6f6a66", "9a948c", "blocks", False),
    "stone_dark": ("4a4644", "6f6a66", "blocks", False),
    "rune": ("2a2f3a", "7fd3ff", "rune", True),
    "lacquer": ("b3261e", "e8c050", "lacquer", False),
    "lacquer_black": ("1e1410", "e8c050", "lacquer", False),
    "gold": ("d9a441", "f6d68a", "metal", False),
    "face": ("f0d6ba", "e8a090", "skin", False),
    "chitin": ("3f6b2a", "b7e04a", "chitin", False),
    "chitin_dark": ("24391a", "6b3f8a", "chitin", False),
    "membrane": ("8fbf3a", "d8f080", "membrane", False),
    "spore": ("b7e04a", "f4ff9a", "spots", True),
    "ash": ("2b2220", "4a3a34", "metal", False),
    "magma": ("ff7a1c", "ffd060", "magma", True),
    "iron": ("5a5a62", "8a8f9a", "metal", False),
    "chain": ("7a7f88", "b8bcc4", "chain", False),
    "robe": ("2a2a33", "5a5a62", "cloth", False),
    "ice_glow": ("7fd3ff", "e0f8ff", "glow", True),
    "storm": ("3a7ac8", "d8e8f8", "cloth", False),
    "cloud": ("d8e8f8", "ffffff", "cloud", False),
    "lightning": ("ffe14a", "fffbd0", "glow", True),
    "shadow": ("15151f", "2a2a44", "fur", False),
    "maw": ("3a0a14", "c84a5a", "flesh", False),
    "void_eye": ("6a8aff", "e0e8ff", "glow", True),
    "mirror": ("6a5a8a", "b8a8d8", "crystal", False),
    "mirror_glow": ("4ad8c8", "e0fffa", "glow", True),
    "abyss": ("0a3a5a", "1ab0b0", "scales", False),
    "abyss_belly": ("1a6a7a", "9af0ff", "scales", False),
    "lure": ("9af0ff", "ffffff", "glow", True),
    "bark": ("5a3a22", "8a5a32", "bark", False),
    "leaf_spring": ("6ac84a", "c8f0a0", "leaf", False),
    "leaf_autumn": ("d86a2a", "f0b040", "leaf", False),
    "season_glow": ("f0f0ff", "ffffff", "glow", True),
    "rock_flesh": ("6a3a2a", "a84a3a", "flesh", False),
    "vein": ("e8503a", "ffb090", "vein", True),
    "earth": ("4a2a1e", "6a3a2a", "blocks", False),
}


def paint_face(img, glow, x0, y0, w, h, mat, face, rnd):
    base, acc, pat, emis = MAT[mat]
    base, acc = hx(base), hx(acc)
    light = {0: 1.18, 1: 0.62, 2: 0.86, 3: 1.0, 4: 0.86, 5: 0.92}[face]
    for x in range(w):
        for y in range(h):
            u, v = x / max(1, w - 1), y / max(1, h - 1)
            f = light * (1.06 - 0.16 * v) * (0.93 + 0.1 * rnd.random())
            c = shade(base, f)
            e = False
            if pat == "blocks":
                if (x % 8 == 0) or (y % 8 == 0) or ((x + y * 3) % 17 == 0 and rnd.random() < 0.5):
                    c = shade(c, 0.72)
                elif rnd.random() < 0.06:
                    c = shade(acc, f)
            elif pat == "rune":
                if (x + y) % 6 == 0 or (abs(x - w // 2) < 1 and y % 3 != 0):
                    c, e = acc, True
            elif pat == "lacquer":
                if x in (0, w - 1) or y in (0, h - 1) or x in (1, w - 2) and w > 6:
                    c = shade(acc, 0.9)
                elif (x * 7 + y * 5) % 13 == 0:
                    c = acc
            elif pat == "metal":
                if y in (0, h - 1) or x in (0, w - 1):
                    c = shade(c, 0.65)
                elif (x % 6 == 2 and y % 6 == 2):
                    c = shade(acc, 1.1)
                elif y < 2:
                    c = shade(c, 1.15)
            elif pat == "skin":
                c = shade(base, 0.98 + 0.04 * rnd.random())
            elif pat == "chitin":
                if y % 4 == 0:
                    c = shade(c, 0.7)
                elif (x + y) % 9 == 0:
                    c = shade(acc, f)
            elif pat == "membrane":
                c = shade(base, 0.9 + 0.2 * rnd.random())
                if (x * 3 + y) % 7 == 0 or x % 5 == 0:
                    c = shade(acc, 0.9)
            elif pat == "spots":
                if rnd.random() < 0.25:
                    c, e = acc, True
            elif pat == "magma":
                c = shade(base, 0.8 + 0.4 * rnd.random())
                e = True
            elif pat == "chain":
                if (y // 2) % 2 == 0:
                    c = shade(acc, f)
                else:
                    c = shade(c, 0.6)
            elif pat == "cloth":
                if x % 4 == 0:
                    c = shade(c, 0.8)
                if y >= h - 2:
                    c = shade(acc, f)
            elif pat == "glow":
                c, e = shade(base, 0.9 + 0.2 * rnd.random()), True
                if x in (0, w - 1) or y in (0, h - 1):
                    c = shade(acc, 1.0)
            elif pat == "cloud":
                c = shade(base, 0.92 + 0.12 * rnd.random())
            elif pat == "fur":
                if rnd.random() < 0.3:
                    c = shade(acc, f)
                if (x + y * 2) % 5 == 0:
                    c = shade(c, 0.6)
            elif pat == "flesh":
                if rnd.random() < 0.15:
                    c = shade(acc, f)
            elif pat == "crystal":
                if (x + y) % 5 == 0:
                    c = shade(acc, 1.0)
                elif (x - y) % 7 == 0:
                    c = shade(c, 1.3)
            elif pat == "scales":
                if (x + (y % 2) * 2) % 4 == 0:
                    c = shade(c, 0.7)
                elif rnd.random() < 0.08:
                    c = shade(acc, f)
            elif pat == "bark":
                if x % 3 == 0:
                    c = shade(c, 0.7)
                elif rnd.random() < 0.08:
                    c = shade(acc, f)
            elif pat == "leaf":
                c = shade(base if rnd.random() < 0.6 else acc, 0.85 + 0.3 * rnd.random())
            elif pat == "vein":
                c, e = shade(base, 0.85 + 0.3 * rnd.random()), True
            img.putpixel((x0 + x, y0 + y), c + (255,))
            if e or emis:
                glow.putpixel((x0 + x, y0 + y), c + (255,))
    # rim: a dark contour on every face edge reads well at distance
    if w > 2 and h > 2:
        for x in range(w):
            for y in (0, h - 1):
                p = img.getpixel((x0 + x, y0 + y))
                img.putpixel((x0 + x, y0 + y), shade(p[:3], 0.75) + (255,))


# ---------------------------------------------------------------- rig DSL
class Rig:
    def __init__(self, name):
        self.name = name
        self.bones = []  # dict(name, parent, pivot, rot, cubes)
        self.roles = {}

    def bone(self, name, parent=None, pivot=(0, 0, 0), rot=None, role=None):
        b = {"name": name, "parent": parent, "pivot": list(pivot), "cubes": []}
        if rot:
            b["rotation"] = list(rot)
        self.bones.append(b)
        if role:
            self.roles.setdefault(role, []).append(name)
        return name

    def cube(self, bone, origin, size, mat, inflate=0.0, rot=None, pivot=None, mirror_face=False):
        b = next(x for x in self.bones if x["name"] == bone)
        c = {"origin": [round(v, 3) for v in origin], "size": [round(v, 3) for v in size], "mat": mat}
        if inflate:
            c["inflate"] = inflate
        if rot:
            c["rotation"] = list(rot)
            c["pivot"] = list(pivot or b["pivot"])
        b["cubes"].append(c)

    def limb(self, prefix, parent, top, segs, mat, joint_mat=None, side=0, role=None, splay=0):
        """A chain of segments hanging down from `top`: [(w, h, d), ...]. Joints overlap by one pixel."""
        x, y, z = top
        par = parent
        names = []
        for i, (w, h, d) in enumerate(segs):
            nm = self.bone(f"{prefix}{i}", par, (x, y, z), rot=[0, 0, splay] if (i == 0 and splay) else None,
                           role=(f"{role}{i}" if role else None))
            self.cube(nm, (x - w / 2, y - h, z - d / 2), (w, h + (1 if i < len(segs) - 1 else 0), d), mat)
            if joint_mat and i < len(segs) - 1:
                self.cube(nm, (x - w / 2 - 0.5, y - h - 1, z - d / 2 - 0.5), (w + 1, 2, d + 1), joint_mat)
            par = nm
            names.append(nm)
            y -= h
        return names


def pack_and_paint(rig, seed):
    cubes = [c for b in rig.bones for c in b["cubes"]]

    def uv_size(c):
        w, h, d = [max(1, int(math.ceil(v))) for v in c["size"]]
        return 2 * (d + w), d + h, (w, h, d)

    tw = 128
    while True:
        x = y = rowh = 0
        ok = True
        for c in sorted(cubes, key=lambda c: -uv_size(c)[1]):
            uw, uh, _ = uv_size(c)
            if uw > tw:
                ok = False
                break
            if x + uw > tw:
                x, y, rowh = 0, y + rowh, 0
            c["uv"] = [x, y]
            x += uw
            rowh = max(rowh, uh)
        if ok and y + rowh <= tw:
            break
        tw *= 2
    img = Image.new("RGBA", (tw, tw), (0, 0, 0, 0))
    glow = Image.new("RGBA", (tw, tw), (0, 0, 0, 0))
    rnd = random.Random(seed)
    for c in cubes:
        u, v = c["uv"]
        _, _, (w, h, d) = uv_size(c)
        faces = [(u + d, v, w, d), (u + d + w, v, w, d), (u, v + d, d, h), (u + d, v + d, w, h), (u + d + w, v + d, d, h), (u + 2 * d + w, v + d, w, h)]
        for fi, (x0, y0, ww, hh) in enumerate(faces):
            if ww > 0 and hh > 0:
                paint_face(img, glow, x0, y0, ww, hh, c["mat"], fi, rnd)
    return img, glow, tw


def write(rig, anims, seed):
    img, glow, tw = pack_and_paint(rig, seed)
    bones = [{"name": "root", "pivot": [0, 0, 0]}]
    for b in rig.bones:
        jb = {"name": b["name"], "parent": b["parent"] or "root", "pivot": b["pivot"], "cubes": []}
        if "rotation" in b:
            jb["rotation"] = b["rotation"]
        for c in b["cubes"]:
            jc = {"origin": c["origin"], "size": c["size"], "uv": c["uv"]}
            for k in ("inflate", "rotation", "pivot"):
                if k in c:
                    jc[k] = c[k]
            jb["cubes"].append(jc)
        bones.append(jb)
    top = max(c["origin"][1] + c["size"][1] for b in rig.bones for c in b["cubes"])
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {
        "identifier": f"geometry.{rig.name}", "texture_width": tw, "texture_height": tw,
        "visible_bounds_width": 8, "visible_bounds_height": max(4, top / 16 + 2), "visible_bounds_offset": [0, top / 32, 0]},
        "bones": bones}]}
    json.dump(geo, open(os.path.join(A, f"geckolib/models/entity/{rig.name}.geo.json"), "w"), indent=1)
    json.dump({"format_version": "1.8.0", "animations": anims}, open(os.path.join(A, f"geckolib/animations/entity/{rig.name}.animation.json"), "w"), indent=1)
    img.save(os.path.join(A, f"textures/entity/{rig.name}.png"))
    glow.save(os.path.join(A, f"textures/entity/{rig.name}_glowmask.png"))
    w = max(abs(v) for b in rig.bones for c in b["cubes"] for v in (c["origin"][0], c["origin"][0] + c["size"][0], c["origin"][2], c["origin"][2] + c["size"][2]))
    return w * 2 / 16, top / 16


# ---------------------------------------------------------------- animation helpers
def kf(times_values, lerp="catmullrom"):
    """{t: [x,y,z]} -> GeckoLib keyframe dict with a lerp mode."""
    return {f"{t:.2f}": {"post": list(v), "lerp_mode": lerp} for t, v in times_values}


def chan(anim, bone, channel, keys, lerp="catmullrom"):
    anim["bones"].setdefault(bone, {})[channel] = kf(keys, lerp)


def new(length, loop):
    return {"loop": loop, "animation_length": length, "bones": {}}


def sine_loop(anim, bone, channel, amp, period, phase=0.0, steps=8, axis=0):
    keys = []
    for i in range(steps + 1):
        t = period * i / steps
        v = [0, 0, 0]
        v[axis] = round(amp * math.sin(2 * math.pi * (i / steps) + phase), 3)
        keys.append((t, v))
    chan(anim, bone, channel, keys)


def roles(rig, r):
    return rig.roles.get(r, [])


def standard_anims(rig, gait="biped", heavy=1.0):
    """Builds the 8 boss animations from the rig's roles. heavy > 1 makes everything slower and weightier."""
    A_ = {}
    T = 1.0 * heavy
    # --- idle: breathing on the spine, head looks around, secondary bones lag behind
    idle = new(4.0, True)
    for b in roles(rig, "body"):
        sine_loop(idle, b, "position", 0.6, 4.0, axis=1)
        sine_loop(idle, b, "rotation", 1.5, 4.0, phase=0.5, axis=0)
    for b in roles(rig, "head"):
        chan(idle, b, "rotation", [(0, [0, 0, 0]), (1.0, [3, 12, 0]), (2.0, [0, 0, 0]), (3.0, [2, -12, 0]), (4.0, [0, 0, 0])])
    for i, b in enumerate(roles(rig, "tail") + roles(rig, "chain") + roles(rig, "cape")):
        sine_loop(idle, b, "rotation", 6 + i, 4.0, phase=i * 0.6, axis=0)
    for i, b in enumerate(roles(rig, "seg")):
        sine_loop(idle, b, "rotation", 7, 4.0, phase=i * 0.7, axis=1)
    for b in roles(rig, "wing_l"):
        sine_loop(idle, b, "rotation", 10, 2.0, axis=2)
    for b in roles(rig, "wing_r"):
        sine_loop(idle, b, "rotation", 10, 2.0, phase=math.pi, axis=2)
    for i, b in enumerate(roles(rig, "orbit")):
        chan(idle, b, "rotation", [(0, [0, 0, 0]), (4.0, [0, 360 if i % 2 == 0 else -360, 0])], "linear")
        sine_loop(idle, b, "position", 1.2, 2.0, phase=i, axis=1)
    for b in roles(rig, "jaw"):
        chan(idle, b, "rotation", [(0, [0, 0, 0]), (2.6, [0, 0, 0]), (3.0, [-14, 0, 0]), (3.4, [0, 0, 0]), (4.0, [0, 0, 0])])
    for b in roles(rig, "pulse"):
        chan(idle, b, "scale", [(0, [1, 1, 1]), (0.25, [1.08, 1.08, 1.08]), (0.5, [1, 1, 1]), (0.75, [1.05, 1.05, 1.05]), (1.2, [1, 1, 1]), (4.0, [1, 1, 1])])
    A_["misc.idle"] = idle

    # --- walk: legs with knee bend and contact, arms counter-swing, body bob twice per cycle
    walk = new(T, True)
    for side, sgn in (("l", 1), ("r", -1)):
        for b in roles(rig, f"leg_{side}0"):
            chan(walk, b, "rotation", [(0, [28 * sgn, 0, 0]), (T / 2, [-28 * sgn, 0, 0]), (T, [28 * sgn, 0, 0])])
        for b in roles(rig, f"leg_{side}1"):
            chan(walk, b, "rotation", [(0, [0, 0, 0]), (T / 4, [30 if sgn > 0 else 5, 0, 0]), (T / 2, [0, 0, 0]), (3 * T / 4, [5 if sgn > 0 else 30, 0, 0]), (T, [0, 0, 0])])
        for b in roles(rig, f"arm_{side}0"):
            chan(walk, b, "rotation", [(0, [-22 * sgn, 0, 0]), (T / 2, [22 * sgn, 0, 0]), (T, [-22 * sgn, 0, 0])])
        for b in roles(rig, f"arm_{side}1"):
            chan(walk, b, "rotation", [(0, [-12, 0, 0]), (T / 2, [-20, 0, 0]), (T, [-12, 0, 0])])
    for i in range(3):
        for side, sgn in (("l", 1), ("r", -1)):
            for b in roles(rig, f"insect_{side}{i}"):
                ph = sgn * (1 if i % 2 == 0 else -1)
                chan(walk, b, "rotation", [(0, [0, 20 * ph, 0]), (T / 2, [0, -20 * ph, 0]), (T, [0, 20 * ph, 0])])
    for b in roles(rig, "body"):
        chan(walk, b, "position", [(0, [0, 0, 0]), (T / 4, [0, 1.2 / heavy, 0]), (T / 2, [0, 0, 0]), (3 * T / 4, [0, 1.2 / heavy, 0]), (T, [0, 0, 0])])
        chan(walk, b, "rotation", [(0, [0, 4, 2]), (T / 2, [0, -4, -2]), (T, [0, 4, 2])])
    for i, b in enumerate(roles(rig, "seg")):
        sine_loop(walk, b, "rotation", 14, T, phase=i * 0.8, axis=1)
    for i, b in enumerate(roles(rig, "tail") + roles(rig, "cape") + roles(rig, "chain")):
        sine_loop(walk, b, "rotation", 10, T, phase=1 + i * 0.5, axis=0)
    for b in roles(rig, "wing_l"):
        sine_loop(walk, b, "rotation", 28, T / 2, axis=2)
    for b in roles(rig, "wing_r"):
        sine_loop(walk, b, "rotation", 28, T / 2, phase=math.pi, axis=2)
    A_["move.walk"] = walk

    arms = roles(rig, "arm_r0") or roles(rig, "arm_l0")
    fore = roles(rig, "arm_r1") or roles(rig, "arm_l1")
    lead = arms or roles(rig, "head") or roles(rig, "body")

    # --- strike (light attack): small wind-up, fast hit, follow-through, settle
    st = new(0.7, False)
    for b in lead:
        chan(st, b, "rotation", [(0, [0, 0, 0]), (0.15, [-70, 10, 0]), (0.25, [40, -10, 0]), (0.45, [25, 0, 0]), (0.7, [0, 0, 0])])
    for b in fore:
        chan(st, b, "rotation", [(0, [0, 0, 0]), (0.15, [-30, 0, 0]), (0.25, [0, 0, 0]), (0.7, [0, 0, 0])])
    for b in roles(rig, "body"):
        chan(st, b, "rotation", [(0, [0, 0, 0]), (0.15, [0, 18, 0]), (0.28, [6, -14, 0]), (0.7, [0, 0, 0])])
    for b in roles(rig, "jaw"):
        chan(st, b, "rotation", [(0, [0, 0, 0]), (0.12, [-40, 0, 0]), (0.3, [0, 0, 0]), (0.7, [0, 0, 0])])
    A_["attack.strike"] = st

    # --- charge (telegraph): crouch, raise arms, tremble, hold
    ch = new(1.0, "hold_on_last_frame")
    for b in roles(rig, "body"):
        chan(ch, b, "position", [(0, [0, 0, 0]), (0.5, [0, -2.5, 0]), (1.0, [0, -3, 0])])
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (0.5, [-10, 0, 0]), (0.62, [-10, 2, 0]), (0.74, [-10, -2, 0]), (0.86, [-10, 2, 0]), (1.0, [-12, 0, 0])])
    for b in roles(rig, "arm_l0") + roles(rig, "arm_r0"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (0.6, [-150, 0, 0]), (1.0, [-160, 0, 0])])
    for b in roles(rig, "head"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (0.5, [-18, 0, 0]), (1.0, [-22, 0, 0])])
    for b in roles(rig, "jaw"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (1.0, [-50, 0, 0])])
    for b in roles(rig, "wing_l"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (1.0, [0, -20, 45])])
    for b in roles(rig, "wing_r"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (1.0, [0, 20, -45])])
    for b in roles(rig, "orbit"):
        chan(ch, b, "rotation", [(0, [0, 0, 0]), (1.0, [0, 540, 0])], "linear")
    for b in roles(rig, "pulse"):
        chan(ch, b, "scale", [(0, [1, 1, 1]), (1.0, [1.15, 1.15, 1.15])])
    A_["attack.charge"] = ch

    # --- slam: release from the charge pose, impact squash, recover
    sl = new(0.8, False)
    for b in roles(rig, "body"):
        chan(sl, b, "position", [(0, [0, -3, 0]), (0.12, [0, 1.5, 0]), (0.2, [0, -1.5, 0]), (0.5, [0, 0, 0]), (0.8, [0, 0, 0])])
        chan(sl, b, "scale", [(0, [1, 1, 1]), (0.2, [1.06, 0.93, 1.06]), (0.4, [1, 1, 1]), (0.8, [1, 1, 1])])
        chan(sl, b, "rotation", [(0, [-12, 0, 0]), (0.18, [14, 0, 0]), (0.5, [4, 0, 0]), (0.8, [0, 0, 0])])
    for b in roles(rig, "arm_l0") + roles(rig, "arm_r0"):
        chan(sl, b, "rotation", [(0, [-160, 0, 0]), (0.16, [20, 0, 0]), (0.3, [10, 0, 0]), (0.8, [0, 0, 0])])
    for b in roles(rig, "jaw"):
        chan(sl, b, "rotation", [(0, [-50, 0, 0]), (0.2, [0, 0, 0]), (0.8, [0, 0, 0])])
    for b in roles(rig, "pulse"):
        chan(sl, b, "scale", [(0, [1.15, 1.15, 1.15]), (0.15, [0.9, 0.9, 0.9]), (0.4, [1, 1, 1]), (0.8, [1, 1, 1])])
    A_["attack.slam"] = sl

    # --- cast: arms open, body rises, orbiting parts accelerate
    ca = new(1.4, False)
    for b in roles(rig, "arm_l0"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (0.35, [-150, 0, -35]), (1.0, [-150, 0, -35]), (1.4, [0, 0, 0])])
    for b in roles(rig, "arm_r0"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (0.35, [-150, 0, 35]), (1.0, [-150, 0, 35]), (1.4, [0, 0, 0])])
    for b in roles(rig, "body"):
        chan(ca, b, "position", [(0, [0, 0, 0]), (0.5, [0, 2.5, 0]), (1.0, [0, 2.5, 0]), (1.4, [0, 0, 0])])
    for b in roles(rig, "head"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (0.5, [-25, 0, 0]), (1.0, [-25, 0, 0]), (1.4, [0, 0, 0])])
    for b in roles(rig, "orbit"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (1.4, [0, 720, 0])], "linear")
        chan(ca, b, "scale", [(0, [1, 1, 1]), (0.6, [1.4, 1.4, 1.4]), (1.4, [1, 1, 1])])
    for b in roles(rig, "wing_l"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (0.5, [0, 0, 60]), (1.0, [0, 0, 60]), (1.4, [0, 0, 0])])
    for b in roles(rig, "wing_r"):
        chan(ca, b, "rotation", [(0, [0, 0, 0]), (0.5, [0, 0, -60]), (1.0, [0, 0, -60]), (1.4, [0, 0, 0])])
    for b in roles(rig, "shell_top"):
        chan(ca, b, "position", [(0, [0, 0, 0]), (0.5, [0, 6, 0]), (1.0, [0, 6, 0]), (1.4, [0, 0, 0])])
    A_["attack.cast"] = ca

    # --- phase change: roar with swelling scale; shells open
    ph = new(2.2, False)
    for b in roles(rig, "body"):
        chan(ph, b, "rotation", [(0, [0, 0, 0]), (0.4, [8, 0, 0]), (0.8, [-14, 0, 0]), (1.8, [-14, 0, 0]), (2.2, [0, 0, 0])])
        chan(ph, b, "scale", [(0, [1, 1, 1]), (0.8, [1.1, 1.1, 1.1]), (1.8, [1.1, 1.1, 1.1]), (2.2, [1, 1, 1])])
    for b in roles(rig, "head"):
        chan(ph, b, "rotation", [(0, [0, 0, 0]), (0.8, [-40, 0, 0]), (1.0, [-38, 6, 0]), (1.2, [-38, -6, 0]), (1.8, [-40, 0, 0]), (2.2, [0, 0, 0])])
    for b in roles(rig, "jaw"):
        chan(ph, b, "rotation", [(0, [0, 0, 0]), (0.8, [-60, 0, 0]), (1.8, [-60, 0, 0]), (2.2, [0, 0, 0])])
    for b in roles(rig, "arm_l0") + roles(rig, "arm_r0"):
        chan(ph, b, "rotation", [(0, [0, 0, 0]), (0.8, [-40, 0, 0]), (1.8, [-40, 0, 0]), (2.2, [0, 0, 0])])
    for b in roles(rig, "shell_top"):
        chan(ph, b, "position", [(0, [0, 0, 0]), (0.8, [0, 14, 0]), (1.8, [0, 14, 0]), (2.2, [0, 0, 0])])
        chan(ph, b, "rotation", [(0, [0, 0, 0]), (0.8, [0, 90, 0]), (1.8, [0, 180, 0]), (2.2, [0, 360, 0])])
    for b in roles(rig, "shell_bottom"):
        chan(ph, b, "position", [(0, [0, 0, 0]), (0.8, [0, -3, 0]), (1.8, [0, -3, 0]), (2.2, [0, 0, 0])])
    for b in roles(rig, "pulse"):
        chan(ph, b, "scale", [(0, [1, 1, 1]), (0.8, [1.3, 1.3, 1.3]), (1.8, [1.3, 1.3, 1.3]), (2.2, [1, 1, 1])])
    A_["misc.phase"] = ph

    # --- rest (opening): exhausted, sagging, vulnerable
    re = new(2.4, False)
    for b in roles(rig, "body"):
        chan(re, b, "rotation", [(0, [0, 0, 0]), (0.3, [18, 0, 6]), (2.0, [16, 0, 6]), (2.4, [0, 0, 0])])
        chan(re, b, "position", [(0, [0, 0, 0]), (0.3, [0, -3, 0]), (2.0, [0, -3, 0]), (2.4, [0, 0, 0])])
    for b in roles(rig, "head"):
        chan(re, b, "rotation", [(0, [0, 0, 0]), (0.3, [25, 0, 0]), (2.0, [22, 0, 0]), (2.4, [0, 0, 0])])
    for b in roles(rig, "arm_l0") + roles(rig, "arm_r0"):
        chan(re, b, "rotation", [(0, [0, 0, 0]), (0.3, [10, 0, 0]), (2.0, [8, 0, 0]), (2.4, [0, 0, 0])])
    A_["misc.rest"] = re
    # GeckoLib turns X the other way from Blockbench's preview: a lower jaw opens with a positive angle in game
    for anim in A_.values():
        for b in roles(rig, "jaw"):
            ch = anim["bones"].get(b, {}).get("rotation")
            if ch:
                for k in ch.values():
                    k["post"][0] = -k["post"][0]
    return A_


# ---------------------------------------------------------------- the eleven bosses
def humanoid(r, scale=1.0, torso_mat="stone", head_mat="stone", arm_mat="stone", leg_mat="stone", joint="stone_dark",
             shoulders=None, wide=1.0):
    s = scale
    hip_y = 18 * s
    r.bone("body", None, (0, hip_y, 0), role="body")
    r.cube("body", (-6 * s * wide, hip_y, -3.5 * s), (12 * s * wide, 14 * s, 7 * s), torso_mat)
    r.cube("body", (-5 * s * wide, hip_y - 3 * s, -3 * s), (10 * s * wide, 4 * s, 6 * s), joint)
    neck = hip_y + 14 * s
    r.bone("head", "body", (0, neck, 0), role="head")
    r.cube("head", (-4.5 * s, neck, -4.5 * s), (9 * s, 9 * s, 9 * s), head_mat)
    for side, sgn in (("l", 1), ("r", -1)):
        sx = sgn * (6 * s * wide + 2.5 * s)
        r.limb(f"arm_{side}", "body", (sx, neck - 1 * s, 0), [(5 * s, 9 * s, 5 * s), (4.5 * s, 9 * s, 4.5 * s)], arm_mat, joint, role=f"arm_{side}")
        if shoulders:
            r.cube(f"arm_{side}0", (sx - 3.5 * s, neck - 3 * s, -3.5 * s), (7 * s, 5 * s, 7 * s), shoulders)
        lx = sgn * 3 * s
        r.limb(f"leg_{side}", None, (lx, hip_y, 0), [(5.5 * s, 9 * s, 5.5 * s), (5 * s, 9 * s, 5 * s)], leg_mat, joint, role=f"leg_{side}")
        r.cube(f"leg_{side}1", (lx - 3 * s, 0, -4 * s), (6 * s, 2 * s, 7.5 * s), joint)
    return neck


def block_guardian():
    r = Rig("block_guardian")
    neck = humanoid(r, 1.25, "stone", "stone", "stone", "stone", "stone_dark", shoulders="stone_dark", wide=1.25)
    r.cube("head", (-1.5, neck + 4.5, -6.2), (3, 3.5, 1), "rune")
    r.cube("body", (-2.5, 26, -5), (5, 5, 1), "rune")
    for i in range(4):
        a = i * math.pi / 2
        nm = r.bone(f"stone{i}", "body", (0, 34, 0), role="orbit")
        r.cube(nm, (math.cos(a) * 28 - 3, 30 + (i % 2) * 6, math.sin(a) * 28 - 3), (6, 6, 6), "stone")
        r.cube(nm, (math.cos(a) * 28 - 1, 32 + (i % 2) * 6, math.sin(a) * 28 - 3.2), (2, 2, 0.4), "rune")
    for side in ("l", "r"):
        r.cube(f"arm_{side}1", ((-9 if side == "r" else 9) - 4, 10, -4), (8, 6, 8), "stone_dark")
    return r, standard_anims(r, heavy=1.25)


def spore_queen():
    r = Rig("spore_queen")
    r.bone("body", None, (0, 16, 0), role="body")
    r.cube("body", (-6, 12, -7), (12, 11, 12), "chitin")
    for i in range(3):
        nm = r.bone(f"abdomen{i}", "body" if i == 0 else f"abdomen{i - 1}", (0, 16 - i * 1.5, 5 + i * 8), role="tail")
        w = 15 - i * 3
        r.cube(nm, (-w / 2, 10 - i * 2, 5 + i * 8), (w, w - 2, 9), "chitin_dark" if i % 2 else "chitin")
        r.cube(nm, (-w / 2 + 2, 10 - i * 2 + w - 3, 6 + i * 8), (w - 4, 2, 7), "spore")
    r.bone("head", "body", (0, 21, -7), role="head")
    r.cube("head", (-5, 18, -16), (10, 9, 9), "chitin")
    r.cube("head", (-4, 21, -16.6), (2.5, 2, 1), "spore")
    r.cube("head", (1.5, 21, -16.6), (2.5, 2, 1), "spore")
    for i, x in enumerate((-4, 0, 4)):
        r.cube("head", (x - 1, 27, -12), (2, 5 + (2 if i == 1 else 0), 2), "gold")
    for side, sgn in (("l", 1), ("r", -1)):
        nm = r.bone(f"mandible_{side}", "head", (sgn * 3, 19, -16), role="jaw")
        r.cube(nm, (sgn * 3 - 1, 16, -21), (2, 2, 6), "chitin_dark", rot=[0, sgn * -15, 0], pivot=(sgn * 3, 17, -16))
        w = r.bone(f"wing_{side}", "body", (sgn * 5, 23, -2), role=f"wing_{side}")
        r.cube(w, (sgn * 5 + (0 if sgn > 0 else -20), 22.5, -4), (20, 0.5, 16), "membrane")
        for i in range(3):
            z = -5 + i * 5
            r.limb(f"insect_{side}{i}_", "body", (sgn * 6, 14, z), [(3, 7, 3), (2.5, 8, 2.5)], "chitin_dark", role=None, splay=sgn * 40)
            r.roles.setdefault(f"insect_{side}{i}", []).append(f"insect_{side}{i}_0")
        r.limb(f"arm_{side}", "body", (sgn * 6, 20, -6), [(2.5, 6, 2.5), (2, 7, 2)], "chitin_dark", role=f"arm_{side}")
    return r, standard_anims(r, heavy=1.1)


def ash_titan():
    r = Rig("ash_titan")
    neck = humanoid(r, 1.5, "ash", "ash", "ash", "ash", "magma", shoulders="ash", wide=1.2)
    r.cube("body", (-4, 33, -6), (8, 8, 1.2), "magma")
    r.cube("head", (-3.5, neck + 6, -7.2), (7, 2, 1), "magma")
    for x in (-6, 6):
        r.cube("body", (x - 1.5, neck - 2, 2), (3, 10, 3), "ash")
        r.cube("body", (x - 1, neck + 8, 2.5), (2, 1, 2), "magma")
    h = r.bone("hammer", "arm_r1", (-13, 10, 0))
    r.cube(h, (-16, 9, -1.5), (3, 18, 3), "iron")
    r.cube(h, (-22, -1, -7), (15, 11, 14), "ash")
    r.cube(h, (-21, 0, -7.6), (13, 9, 1), "magma")
    r.cube(h, (-21, 0, 6.6), (13, 9, 1), "magma")
    return r, standard_anims(r, heavy=1.5)


def grand_jailer():
    r = Rig("grand_jailer")
    r.bone("body", None, (0, 20, 0), role="body")
    r.cube("body", (-6, 20, -4), (12, 14, 8), "robe")
    nm = r.bone("robe0", "body", (0, 20, 0), role="cape")
    r.cube(nm, (-7, 10, -5), (14, 11, 10), "robe")
    nm2 = r.bone("robe1", "robe0", (0, 10, 0), role="cape")
    r.cube(nm2, (-8, 0, -6), (16, 11, 12), "robe")
    r.bone("head", "body", (0, 34, 0), role="head")
    r.cube("head", (-4, 34, -4), (8, 8, 8), "iron")
    r.cube("head", (-5, 33, -5), (10, 11, 10), "robe", inflate=0.3)
    r.cube("head", (-2.5, 37, -5.4), (5, 1.5, 1), "ice_glow")
    for side, sgn in (("l", 1), ("r", -1)):
        r.limb(f"arm_{side}", "body", (sgn * 8, 33, 0), [(4, 10, 4), (3.5, 10, 3.5)], "robe", "iron", role=f"arm_{side}")
    par = "arm_l1"
    for i in range(5):
        nm = r.bone(f"chain{i}", par, (10, 13 - i * 3, 0), role="chain")
        r.cube(nm, (9.5, 10 - i * 3, -0.5), (1, 3.2, 1), "chain")
        par = nm
    lan = r.bone("lantern", "arm_r1", (-10, 12, 0), role="chain")
    r.cube(lan, (-12, 4, -2), (4, 5, 4), "iron")
    r.cube(lan, (-11.5, 4.5, -1.5), (3, 4, 3), "ice_glow")
    for i in range(4):
        nm = r.bone(f"key{i}", "body", (0, 26, 0), role="orbit")
        a = i * math.pi / 2
        r.cube(nm, (math.cos(a) * 14 - 1, 25, math.sin(a) * 14 - 0.5), (2, 5, 1), "gold")
    return r, standard_anims(r, heavy=1.2)


def storm_king():
    r = Rig("storm_king")
    neck = humanoid(r, 1.2, "storm", "cloud", "storm", "storm", "gold", shoulders="gold")
    r.cube("head", (-4.5, neck + 10.8, -4.5), (9, 3, 9), "gold")
    for x in (-4, -1, 2):
        r.cube("head", (x, neck + 13.5, -4.5), (2, 3, 1), "gold")
    r.cube("head", (-3, neck + 4, -5.6), (6, 1.5, 1), "lightning")
    cape = r.bone("cape0", "body", (0, neck, 4), role="cape")
    r.cube(cape, (-7, neck - 14, 4), (14, 15, 1), "storm")
    cape1 = r.bone("cape1", "cape0", (0, neck - 14, 4.5), role="cape")
    r.cube(cape1, (-7.5, neck - 26, 4), (15, 12.5, 1), "storm")
    for side, sgn in (("l", 1), ("r", -1)):
        par = "body"
        for i in range(3):
            nm = r.bone(f"wing_{side}{i}", par, (sgn * (4 + i * 9), neck - 2 + i * 2, 4), role=f"wing_{side}")
            r.cube(nm, (sgn * (4 + i * 9) + (0 if sgn > 0 else -10), neck - 14 + i * 2, 4), (10, 14 - i * 3, 1), "cloud")
            par = nm
    orb = r.bone("orb", "arm_r1", (-9, 6, 0), role="pulse")
    r.cube(orb, (-12.7, 11, -2.5), (5, 5, 5), "lightning")
    return r, standard_anims(r, heavy=1.0)


def light_eater():
    r = Rig("light_eater")
    r.bone("body", None, (0, 18, 0), role="body")
    r.cube("body", (-7, 13, -10), (14, 11, 22), "shadow")
    r.cube("body", (-5, 24, -6), (10, 2, 14), "void_eye")
    r.bone("neck", "body", (0, 20, -10), role="head")
    r.cube("neck", (-5, 15, -16), (10, 9, 7), "shadow")
    r.bone("head", "neck", (0, 20, -16), role="head")
    r.cube("head", (-7, 16, -29), (14, 10, 14), "shadow")
    r.cube("head", (-6, 23, -29.6), (3, 2, 1), "void_eye")
    r.cube("head", (3, 23, -29.6), (3, 2, 1), "void_eye")
    r.cube("head", (-6, 16, -29.4), (12, 3, 1), "maw")
    jaw = r.bone("jaw", "head", (0, 17, -16), role="jaw")
    r.cube(jaw, (-6.5, 12, -28), (13, 4, 13), "shadow")
    r.cube(jaw, (-5.5, 15.5, -27.5), (11, 1, 11), "maw")
    for i in range(5):
        r.cube(jaw, (-5 + i * 2.4, 16, -27.6), (1, 2, 1), "cloud")
    for side, sgn in (("l", 1), ("r", -1)):
        for j, z in enumerate((-7, 8)):
            r.limb(f"leg_{side}{'f' if j == 0 else 'b'}", None, (sgn * 5.5, 14, z), [(4.5, 7, 4.5), (4, 7, 4)], "shadow", "maw",
                   role=f"leg_{side if j == 0 else ('r' if side == 'l' else 'l')}")
        t = r.bone(f"tendril_{side}", "body", (sgn * 6, 24, 0), role=f"wing_{side}")
        r.cube(t, (sgn * 6 + (0 if sgn > 0 else -14), 23.5, -1), (14, 1, 2), "void_eye")
    par = "body"
    for i in range(4):
        nm = r.bone(f"tail{i}", par, (0, 20 - i, 12 + i * 6), role="tail")
        r.cube(nm, (-2 + i * 0.3, 18 - i, 12 + i * 6), (4 - i * 0.6, 4 - i * 0.6, 7), "shadow")
        par = nm
    return r, standard_anims(r, heavy=1.1)


def your_double():
    r = Rig("your_double")
    neck = humanoid(r, 1.0, "mirror", "mirror", "mirror", "mirror", "mirror_glow")
    r.cube("head", (-3, neck + 4, -4.7), (2, 1.5, 0.5), "mirror_glow")
    r.cube("head", (1, neck + 4, -4.7), (2, 1.5, 0.5), "mirror_glow")
    for i in range(5):
        nm = r.bone(f"shard{i}", "body", (0, 24, 0), role="orbit")
        a = i * math.tau / 5
        r.cube(nm, (math.cos(a) * 12 - 1, 24 + (i % 3) * 3, math.sin(a) * 12 - 0.5), (2, 4, 1), "mirror_glow", rot=[0, 0, 25], pivot=(math.cos(a) * 12, 26, math.sin(a) * 12))
    bl = r.bone("blade", "arm_r1", (-8.5, 4, 0))
    r.cube(bl, (-9.5, -1, -0.5), (2, 14, 1), "mirror_glow")
    r.cube(bl, (-11, 12, -1.5), (5, 1.5, 3), "mirror")
    return r, standard_anims(r, heavy=0.85)


def pressure_leviathan():
    r = Rig("pressure_leviathan")
    r.bone("body", None, (0, 10, 0), role="body")
    r.bone("head", "body", (0, 10, -12), role="head")
    r.cube("head", (-8, 2, -30), (16, 14, 18), "abyss")
    r.cube("head", (-7, 2, -30.5), (14, 4, 1), "abyss_belly")
    r.cube("head", (-7, 11, -30.6), (3, 3, 1), "lure")
    r.cube("head", (4, 11, -30.6), (3, 3, 1), "lure")
    jaw = r.bone("jaw", "head", (0, 4, -12), role="jaw")
    r.cube(jaw, (-7.5, -2, -29), (15, 5, 17), "abyss_belly")
    for i in range(6):
        r.cube(jaw, (-6 + i * 2.4, 3, -28.5), (1, 2, 1), "cloud")
    lure = r.bone("lure_stalk", "head", (0, 16, -20), role="tail")
    r.cube(lure, (-0.5, 16, -28), (1, 1, 9), "abyss")
    r.cube(lure, (-2, 14, -31), (4, 4, 4), "lure")
    par = "body"
    for i in range(7):
        z = -12 + i * 9
        w = 15 - i * 1.5
        nm = r.bone(f"seg{i}", par, (0, 10, z), role="seg")
        r.cube(nm, (-w / 2, 10 - w / 2, z), (w, w, 10), "abyss" if i % 2 else "abyss_belly")
        r.cube(nm, (-1, 10 + w / 2, z + 2), (2, 3, 8), "abyss")
        if i in (1, 4):
            for side, sgn in (("l", 1), ("r", -1)):
                f = r.bone(f"fin_{side}{i}", nm, (sgn * w / 2, 10, z + 4), role=f"wing_{side}")
                r.cube(f, (sgn * w / 2 + (0 if sgn > 0 else -12), 9.5, z + 1), (12, 1, 9), "abyss_belly")
        par = nm
    return r, standard_anims(r, heavy=1.3)


def seasons_master():
    r = Rig("seasons_master")
    neck = humanoid(r, 1.4, "bark", "bark", "bark", "bark", "leaf_spring", shoulders="leaf_autumn", wide=1.15)
    r.cube("head", (-3, neck + 5, -6.6), (2, 2, 1), "season_glow")
    r.cube("head", (1, neck + 5, -6.6), (2, 2, 1), "season_glow")
    for side, sgn in (("l", 1), ("r", -1)):
        a = r.bone(f"antler_{side}", "head", (sgn * 3, neck + 12, 0), role="cape")
        r.cube(a, (sgn * 3 - 1, neck + 12, -1), (2, 10, 2), "bark")
        r.cube(a, (sgn * 3 + (1 if sgn > 0 else -6), neck + 17, -1), (5, 2, 2), "bark")
        r.cube(a, (sgn * 3 + (3 if sgn > 0 else -6), neck + 19, -1), (3, 5, 2), "leaf_spring")
    for i, mat in enumerate(("leaf_spring", "season_glow", "leaf_autumn", "cloud")):
        o = r.bone(f"orb{i}", "body", (0, 36, 0), role="orbit")
        a = i * math.pi / 2
        r.cube(o, (math.cos(a) * 24 - 3, 34, math.sin(a) * 24 - 3), (6, 6, 6), mat)
    return r, standard_anims(r, heavy=1.4)


def terrain_heart_boss():
    r = Rig("terrain_heart_boss")
    r.bone("body", None, (0, 22, 0), role="body")
    core = r.bone("core", "body", (0, 22, 0), role="pulse")
    r.cube(core, (-11, 10, -11), (22, 22, 22), "rock_flesh")
    r.cube(core, (-8, 13, -11.6), (16, 16, 1), "vein")
    r.cube(core, (-11.6, 13, -8), (1, 16, 16), "vein")
    r.cube(core, (10.6, 13, -8), (1, 16, 16), "vein")
    for i, (x, z) in enumerate(((-6, -4), (5, -2), (-2, 6))):
        art = r.bone(f"artery{i}", "body", (x, 32, z), role="tail")
        r.cube(art, (x - 2.5, 32, z - 2.5), (5, 10 - i * 2, 5), "rock_flesh")
        r.cube(art, (x - 1.5, 41 - i * 2, z - 1.5), (3, 2, 3), "vein")
    for i in range(6):
        a = i * math.pi / 3
        o = r.bone(f"chunk{i}", "body", (0, 22, 0), role="orbit")
        r.cube(o, (math.cos(a) * 20 - 3, 16 + (i % 2) * 8, math.sin(a) * 20 - 3), (6, 5, 6), "earth")
        r.cube(o, (math.cos(a) * 20 - 1, 21 + (i % 2) * 8, math.sin(a) * 20 - 1), (2, 1, 2), "vein")
    r.bone("head", "body", (0, 22, 0), role="head")
    return r, standard_anims(r, heavy=1.4)


def the_unfinished():
    r = Rig("the_unfinished")
    r.bone("body", None, (0, 0, 0), role="body")
    bot = r.bone("shell_bottom", "body", (0, 0, 0), role="shell_bottom")
    r.cube(bot, (-12, 0, -12), (24, 16, 24), "lacquer")
    r.cube(bot, (-12.5, 14, -12.5), (25, 2, 25), "gold")
    top = r.bone("shell_top", "body", (0, 16, 0), role="shell_top")
    r.cube(top, (-12, 16, -12), (24, 12, 24), "lacquer")
    r.cube(top, (-8, 28, -8), (16, 10, 16), "lacquer")
    r.cube(top, (-6, 30, -8.6), (12, 8, 1), "face")
    r.cube(top, (-4, 33, -8.9), (2, 2, 0.5), "void_eye")
    r.cube(top, (2, 33, -8.9), (2, 2, 0.5), "void_eye")
    r.cube(top, (-9, 36, -9), (18, 3, 18), "lacquer_black")
    inner = r.bone("inner", "body", (0, 4, 0), role="head")
    r.cube(inner, (-6, 4, -6), (12, 12, 12), "lacquer_black")
    r.cube(inner, (-4, 16, -4), (8, 8, 8), "lacquer_black")
    r.cube(inner, (-3, 17, -4.5), (6, 5, 1), "face")
    core = r.bone("core", "inner", (0, 10, 0), role="pulse")
    r.cube(core, (-2, 8, -2), (4, 4, 4), "magma")
    for side, sgn in (("l", 1), ("r", -1)):
        r.limb(f"arm_{side}", "body", (sgn * 14.5, 26, 0), [(5, 9, 5), (4.5, 9, 4.5)], "lacquer", "gold", role=f"arm_{side}")
        r.cube(f"arm_{side}1", (sgn * 14.5 - 3, 6, -3), (6, 3, 6), "gold")
    for i in range(10):
        o = r.bone(f"thread{i}", "body", (0, 20, 0), role="orbit")
        a = i * math.tau / 10
        r.cube(o, (math.cos(a) * 20 - 0.5, 10 + (i % 4) * 5, math.sin(a) * 20 - 0.5), (1, 6, 1), "gold")
    return r, standard_anims(r, heavy=1.3)


BUILDERS = [block_guardian, spore_queen, ash_titan, grand_jailer, storm_king, light_eater, your_double,
            pressure_leviathan, seasons_master, terrain_heart_boss, the_unfinished]


def build_all():
    dims = {}
    for i, f in enumerate(BUILDERS):
        rig, anims = f()
        dims[rig.name] = write(rig, anims, 9000 + i)
    return dims


if __name__ == "__main__":
    for k, v in build_all().items():
        print(k, "%.1f x %.1f" % v)
