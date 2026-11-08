"""The Nesting Cradle as an animated GeckoLib block (Blockbench format): its model, its texture and glowmask, and its
animations, all generated from the tables below and tools/content.py CRADLE_TIMELINE.

The cradle is a great carved matryoshka on a lacquered foot, about two blocks tall, opened at its waist: its upper
half leans ajar on a hinge at the back, a glow breathes inside the bowl, and a ring of gold beads with ten sockets,
one per world, turns round its waist. An ore set in it lights its world's socket (slot.<w>.on, then slot.<w>.lit).
The ritual (one animation, synced from the server's start tick) spins the ring up and draws it in, throws the upper
half wide open, raises a nest of ten smaller dolls (the hidden dolls' worlds, from the largest to the smallest, in the
order they nest: content.NEST_ORDER) that fan out and spin, closes them one over the next, sinks the last one into the
bowl, slams the doll shut, makes it jump, shake and glow, and opens it a last time on the Matriochkite Ingot, which
rises and spins before the server pops it out.

Conventions (GeckoLib, the model's own coordinates, as tools/boss_moves.py): front is -Z, up is +Y, 16 units to a
block, the block's bottom centre at the origin; a bone standing up from its pivot leans forward with a positive X
rotation; a positive Y rotation turns the front toward +X; positions are added in model units.

  python3 tools/cradle_geo.py <png>   writes a contact sheet of the texture for looking at it
"""
import json
import math
import os

import craft
from craft import GOLD, PAPER, SKIN, INK, CHEEK, hramp, hx, mix, pnoise, style
from content import NEST_ORDER, WORLDS, CRADLE_TIMELINE as TL

NS = "matriochka"
ID = "nesting_cradle"
SEC = 20.0  # ticks per second

LACQUER = [(52, 6, 12), (102, 14, 20), (150, 24, 28), (194, 38, 36), (226, 78, 60), (248, 146, 116)]
LEAF = [(92, 56, 14), (150, 104, 30), (204, 154, 50), (238, 194, 82), (252, 224, 140), (255, 246, 206)]
CREAM = [(150, 112, 80), (206, 172, 130), (236, 214, 176), (248, 236, 210), (255, 250, 236)]
FLOWER = [(120, 20, 40), (196, 40, 58), (236, 96, 96)]

# the doll's profile turned on the lathe, over a height of 16: (y0, y1, radius); its halves meet at WAIST
PROFILE = [(0.0, 0.8, 3.8), (0.8, 2.2, 4.9), (2.2, 4.4, 5.6), (4.4, 7.4, 5.8), (7.4, 8.4, 5.5), (8.4, 9.4, 4.8),
           (9.4, 10.2, 4.1), (10.2, 14.2, 3.9), (14.2, 15.2, 3.0), (15.2, 16.0, 1.8)]
WAIST = 7.4

FOOT = 3.0                # the lacquered foot the doll stands on
SCALE = 1.75              # the great doll: 28 units tall
WAIST_Y = FOOT + WAIST * SCALE
RING_R, RING_IN = 15.0, 11.5   # the ring's radius at rest, and drawn in by the ritual
BEADS = 30
NEST_H = [18.0 * 0.89 ** k for k in range(10)]   # the ten nested dolls, the largest first
FAN_R = 15.0
NEST_UP = 22.0            # how high the nest rises out of the bowl
OPEN = 112.0              # the upper half thrown open (leaning back on its hinge, away from its face)
AJAR = 9.0                # and at rest


def ring_world(i):
    """The world of socket i (0 to 9) round the ring: 1 to 10."""
    return i + 1


def nest_world(k):
    """The world of nested doll k (0 the largest): the hidden dolls nest from content.NEST_ORDER's last."""
    return NEST_ORDER[::-1][k]


# =================================================================== the model
class Cube:
    def __init__(self, o, s, mat, faces=None, glow=False, rot=None, pivot=None, inflate=0.0, w=0):
        self.o, self.s, self.mat, self.faces, self.glow = o, s, mat, faces or {}, glow
        self.rot, self.pivot, self.inflate, self.w = rot, pivot, inflate, w
        self.uv = None


class Bone:
    def __init__(self, name, parent, pivot, rot=None):
        self.name, self.parent, self.pivot, self.rot = name, parent, pivot, rot
        self.cubes = []


def doll(bone, base_y, h, w, half=None, cx=0.0, cz=0.0, face=True):
    """The cubes of a turned doll of height h standing at base_y in the colours of World w; half: 'lower', 'upper'
    or None (whole). Its face looks to +Z, the way the cradle faces, its apron below."""
    k = h / 16.0
    for (y0, y1, r) in PROFILE:
        if half == "lower" and y0 >= WAIST or half == "upper" and y1 <= WAIST:
            continue
        head = y0 >= 10.2 and y1 <= 14.2
        apron = 2.2 <= y0 and y1 <= WAIST
        faces = {"south": "face"} if head and face else {"south": "apron"} if apron else {}
        rr = r * k
        mat = "gold" if (y0, y1) in ((7.4, 8.4), (0.0, 0.8)) else "lacquer"
        bone.cubes.append(Cube([cx - rr, base_y + y0 * k, cz - rr], [2 * rr, (y1 - y0) * k, 2 * rr], mat, faces, w=w))


def build():
    bones = []

    def B(name, parent, pivot, rot=None):
        b = Bone(name, parent, pivot, rot)
        bones.append(b)
        return b

    root = B("root", None, [0, 0, 0])
    foot = B("foot", "root", [0, 0, 0])
    for (y0, y1, r, mat) in ((0.0, 1.0, 11.0, "gold"), (1.0, 2.2, 10.0, "lacquer_dark"), (2.2, FOOT, 10.6, "gold")):
        foot.cubes.append(Cube([-r, y0, -r], [2 * r, y1 - y0, 2 * r], mat))
    body = B("body", "root", [0, FOOT, 0])
    lower = B("lower", "body", [0, FOOT, 0])
    doll(lower, FOOT, 16 * SCALE, 10, half="lower")
    # the open bowl: its dark lacquered inside just under the rim
    rim = 5.5 * SCALE
    lower.cubes.append(Cube([-rim + 1, WAIST_Y - 0.6, -rim + 1], [2 * rim - 2, 0.5, 2 * rim - 2], "inside"))
    glow = B("glow", "body", [0, WAIST_Y - 2, 0])
    glow.cubes.append(Cube([-5, WAIST_Y - 1.4, -5], [10, 0.8, 10], "light", glow=True))
    # the upper half, hinged at the back of the waist
    upper = B("upper", "body", [0, WAIST_Y, 5.5 * SCALE])
    doll(upper, FOOT, 16 * SCALE, 10, half="upper")
    # the nest of ten dolls inside the bowl: each on an arm turned to its place in the fan
    nest = B("nest", "body", [0, FOOT + 2, 0])
    for k, h in enumerate(NEST_H):
        a = k * 36.0
        arm = B(f"arm{k}", "nest", [0, FOOT + 2, 0], rot=[0, a, 0])
        nd = B(f"nd{k}", f"arm{k}", [0, FOOT + 2, 0])
        doll(nd, FOOT + 2, h, nest_world(k))
    # the ingot, waiting deep in the bowl
    ingot = B("ingot", "body", [0, WAIST_Y - 3, 0])
    ingot.cubes.append(Cube([-3.5, WAIST_Y - 4.5, -1.6], [7, 2.2, 3.2], "ingot", glow=True))
    ingot.cubes.append(Cube([-2.7, WAIST_Y - 2.3, -1.0], [5.4, 0.8, 2.0], "ingot", glow=True))
    ingot.cubes.append(Cube([-3.6, WAIST_Y - 3.9, -1.7], [7.2, 0.8, 3.4], "lacquer"))
    # the ring of beads and sockets round the waist
    ring = B("ring", "root", [0, WAIST_Y, 0])
    for i in range(BEADS):
        if i % 3 == 0:
            continue
        a = math.radians(i * 360.0 / BEADS)
        x, z = math.sin(a) * RING_R, -math.cos(a) * RING_R
        ring.cubes.append(Cube([x - 0.6, WAIST_Y - 0.6, z - 0.6], [1.2, 1.2, 1.2], "bead"))
    for i in range(10):
        w = ring_world(i)
        arm = B(f"sarm{w}", "ring", [0, WAIST_Y, 0], rot=[0, i * 36.0, 0])
        sock = B(f"sock{w}", f"sarm{w}", [0, WAIST_Y, -RING_R])
        sock.cubes.append(Cube([-1.6, WAIST_Y - 1.6, -RING_R - 1.6], [3.2, 1.0, 3.2], "gold"))
        sock.cubes.append(Cube([-1.1, WAIST_Y - 2.4, -RING_R - 1.1], [2.2, 0.8, 2.2], "gold_dark"))
        gem = B(f"gem{w}", f"sock{w}", [0, WAIST_Y + 0.4, -RING_R])
        gem.cubes.append(Cube([-1.1, WAIST_Y - 0.7, -RING_R - 1.1], [2.2, 2.2, 2.2], "gem", glow=True, w=w,
                              rot=[45, 0, 45], pivot=[0, WAIST_Y + 0.4, -RING_R]))
    return bones


# =================================================================== the texture
def box_size(s):
    w, h, d = [max(1, int(math.ceil(v - 1e-6))) for v in s]
    return 2 * (d + w), d + h, (w, h, d)


def world_ramp(w):
    return style(w)["body"]


def paint(bones, texel_fn=None, start=128):
    """Packs every cube's box UV and paints its faces with its material (texel_fn, this file's texel by default);
    returns (texture, glowmask, size)."""
    texel_fn = texel_fn or texel
    from PIL import Image
    cubes = [c for b in bones for c in b.cubes]
    order = sorted(range(len(cubes)), key=lambda i: -box_size(cubes[i].s)[1])
    tw = start
    while True:
        x = y = rowh = 0
        place = {}
        for i in order:
            uw, uh, _ = box_size(cubes[i].s)
            if x + uw > tw:
                x, y, rowh = 0, y + rowh, 0
            place[i] = (x, y)
            x += uw
            rowh = max(rowh, uh)
        if y + rowh <= tw and all(box_size(c.s)[0] <= tw for c in cubes):
            break
        tw *= 2
    th = tw
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    glow = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    for i, c in enumerate(cubes):
        c.uv = list(place[i])
        u, v = c.uv
        _, _, (w, h, d) = box_size(c.s)
        faces = {"up": (u + d, v, w, d), "down": (u + d + w, v, w, d), "west": (u, v + d, d, h), "south": (u + d, v + d, w, h),
                 "east": (u + d + w, v + d, d, h), "north": (u + 2 * d + w, v + d, w, h)}
        for f, (x0, y0, fw, fh) in faces.items():
            mat = c.faces.get(f, c.mat)
            for yy in range(fh):
                for xx in range(fw):
                    col, lit = texel_fn(mat, f, xx, yy, fw, fh, c, i)
                    img.putpixel((x0 + xx, y0 + yy), col + (255,))
                    if lit or c.glow:
                        glow.putpixel((x0 + xx, y0 + yy), col + (255,))
    return img, glow, tw


def _face_sprite(fw, fh, ramp, xx, yy):
    """A doll's painted face filling a head's front: a cream oval in a scarf of its lacquer, hair, eyes, cheeks."""
    cx, cy = (fw - 1) / 2, fh * 0.56
    rx, ry = fw * 0.36, fh * 0.42
    dx, dy = (xx - cx) / rx, (yy - cy) / ry
    if dx * dx + dy * dy > 1:
        return (LEAF[3] if (xx in (0, fw - 1) or yy in (0, fh - 1)) else ramp[3]), False
    if yy < cy - ry * 0.35 + abs(xx - cx) * 0.35:
        return (92, 50, 30), False
    ey = int(round(cy + ry * 0.05))
    if yy == ey and abs(abs(xx - cx) - rx * 0.45) < 0.6:
        return INK, False
    if yy == ey + max(1, int(fh * 0.12)) and abs(abs(xx - cx) - rx * 0.62) < 0.6:
        return CHEEK, False
    if yy == int(round(cy + ry * 0.55)) and abs(xx - cx) < max(0.6, rx * 0.18):
        return (190, 40, 40), False
    return SKIN[3] if dx * dx + dy * dy < 0.5 else SKIN[2], False


def _apron_sprite(fw, fh, ramp, accent, xx, yy):
    cx, cy = (fw - 1) / 2, fh * 0.55
    rx, ry = fw * 0.36, fh * 0.42
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    if d > 1:
        return ramp[3] if (xx + yy) % 5 else LEAF[3], False
    if d > 0.78:
        return LEAF[3], False
    fd = ((xx - cx) / (rx * 0.42)) ** 2 + ((yy - cy + ry * 0.1) / (ry * 0.42)) ** 2
    if fd <= 1:
        return accent, False
    if abs(yy - (cy + ry * 0.45)) < 0.8 and 0.15 < abs(xx - cx) / rx < 0.6:
        return (90, 140, 52), False
    return CREAM[3], False


def texel(mat, face, xx, yy, fw, fh, cube, seed):
    """The colour of one texel of a face, and whether it glows."""
    g = pnoise(xx + seed * 7.3, yy + seed * 3.1, 4, 900 + seed % 97)
    shade = {"up": 1, "down": -1}.get(face, 0)
    w = cube.w or 10
    if mat == "lacquer" or mat == "lacquer_dark":
        ramp = LACQUER if w == 10 else world_ramp(w)
        # the nested dolls a tone brighter, so their worlds read inside the great one's shadow
        lo = 2 if w == 10 else 3
        c = ramp[lo + 1] if g > 0.42 else ramp[lo]
        if mat == "lacquer_dark":
            c = ramp[1]
        # little gold flowers strewn on it, a gold line at the top of every band
        if ((xx * 73856093) ^ (yy * 19349663) ^ (seed * 83492791)) % 19 == 0 and fw > 3 and fh > 2:
            c = LEAF[4] if w == 10 else style(w)["glow"][3]
        if face in ("north", "south", "east", "west") and yy == 0 and w == 10:
            return LEAF[4], False
        if shade < 0:
            c = ramp[1]
        return c, False
    if mat in ("gold", "bead", "gold_dark"):
        c = LEAF[4] if g > 0.55 else LEAF[3]
        if mat == "gold_dark":
            c = LEAF[1]
        if mat == "bead" and face == "up":
            c = LEAF[5]
        if face in ("north", "south", "east", "west") and yy == fh - 1 and fh > 1:
            c = LEAF[2]
        return c, mat == "bead"
    if mat == "face":
        ramp = LACQUER if w == 10 else world_ramp(w)
        return _face_sprite(fw, fh, ramp, xx, yy)
    if mat == "apron":
        ramp = LACQUER if w == 10 else world_ramp(w)
        accent = FLOWER[1] if w == 10 else style(w)["glow"][3]
        return _apron_sprite(fw, fh, ramp, accent, xx, yy)
    if mat == "inside":
        r2 = ((xx - (fw - 1) / 2) ** 2 + (yy - (fh - 1) / 2) ** 2) / max(1, (fw / 2) ** 2)
        return ((LEAF[2] if 0.55 < r2 < 0.7 else (36, 8, 12) if g > 0.5 else (54, 12, 16)), False)
    if mat == "light":
        return (LEAF[5] if g > 0.5 else LEAF[4]), True
    if mat == "gem":
        ramp = style(cube.w)["glow"]
        c = ramp[4] if (xx + yy) % 3 else ramp[5]
        if face == "down":
            c = ramp[2]
        return c, True
    if mat == "ingot":
        c = LEAF[5] if face == "up" else LEAF[4] if g > 0.5 else LEAF[3]
        return c, True
    return (255, 0, 255), False


# =================================================================== geometry json
def geo_json(bones, tw):
    out = []
    for b in bones:
        jb = {"name": b.name, "pivot": [round(v, 3) for v in b.pivot]}
        if b.parent:
            jb["parent"] = b.parent
        if b.rot:
            jb["rotation"] = b.rot
        if b.cubes:
            jb["cubes"] = []
            for c in b.cubes:
                jc = {"origin": [round(v, 3) for v in c.o], "size": [round(v, 3) for v in c.s], "uv": c.uv}
                if c.rot:
                    jc["rotation"] = c.rot
                    jc["pivot"] = c.pivot
                if c.inflate:
                    jc["inflate"] = c.inflate
                jb["cubes"].append(jc)
        out.append(jb)
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{ID}", "texture_width": tw, "texture_height": tw,
                        "visible_bounds_width": 5, "visible_bounds_height": 5, "visible_bounds_offset": [0, 1.5, 0]},
        "bones": out}]}


# =================================================================== the animations
class Track:
    """Keyframes per bone and channel, in seconds; each key's easing shapes the motion that ends on it."""

    def __init__(self, length, loop):
        self.L, self.loop, self.ch = length, loop, {}

    def key(self, bone, chan, t, v, ease="linear"):
        self.ch.setdefault((bone, chan), {})[round(t, 3)] = (list(v), ease)
        return self

    def keys(self, bone, chan, ks):
        for k in ks:
            self.key(bone, chan, *k)
        return self

    def json(self):
        bones = {}
        for (bone, chan), d in sorted(self.ch.items()):
            o = {}
            for t, (v, ease) in sorted(d.items()):
                v = [round(x, 3) for x in v]
                o[f"{t:.3f}"] = {"post": v, "lerp_mode": ease} if ease in ("linear", "catmullrom", "step") else {"post": v, "easing": ease}
            bones.setdefault(bone, {})[chan] = o
        loop = {"hold": "hold_on_last_frame", True: True}.get(self.loop, False)
        return {"loop": loop, "animation_length": self.L, "bones": bones}


S0 = [0, 0, 0]
ONE = [1, 1, 1]
HIDE = [0, 0, 0]


def idle():
    """At rest: the upper half breathing ajar, the glow in the bowl breathing, the ring turning slowly; the nest and
    the ingot out of sight."""
    t = Track(20.0, True)
    t.keys("ring", "rotation", [(0, S0), (20.0, [0, 360, 0])])
    for s in range(0, 21, 2):
        t.key("upper", "rotation", s, [AJAR + (2.0 if s % 4 else 0), 0, 0], "easeInOutSine")
        t.key("glow", "scale", s, [1.0 + (0.18 if s % 4 else 0), 1, 1.0 + (0.18 if s % 4 else 0)], "easeInOutSine")
    t.keys("nest", "scale", [(0, HIDE, "step")])
    t.keys("ingot", "scale", [(0, HIDE, "step")])
    return t


def slot_anims(w):
    on = Track(0.8, False)
    on.keys(f"gem{w}", "scale", [(0, HIDE), (0.45, [1.5, 1.5, 1.5], "easeOutQuad"), (0.8, ONE, "easeOutBack")])
    on.keys(f"gem{w}", "position", [(0, [0, -9, RING_R * 0]), (0.45, [0, 1.5, 0], "easeOutCubic"), (0.8, S0, "easeOutBack")])
    on.keys(f"gem{w}", "rotation", [(0, S0), (0.8, [0, 360, 0], "easeOutCubic")])
    on.keys(f"sock{w}", "scale", [(0, ONE), (0.6, [1.25, 1.25, 1.25], "easeOutQuad"), (0.8, ONE, "easeOutBack")])
    lit = Track(3.0, True)
    lit.keys(f"gem{w}", "rotation", [(0, S0), (3.0, [0, 360, 0])])
    lit.keys(f"gem{w}", "scale", [(0, ONE), (1.5, [1.14, 1.14, 1.14], "easeInOutSine"), (3.0, ONE, "easeInOutSine")])
    lit.keys(f"gem{w}", "position", [(0, S0), (1.5, [0, 0.6, 0], "easeInOutSine"), (3.0, S0, "easeInOutSine")])
    off = Track(1.0, True)
    off.keys(f"gem{w}", "scale", [(0, HIDE, "step")])
    return on, lit, off


def ritual():
    """The ritual, CRADLE_TIMELINE's ticks turned into seconds."""
    s = lambda k: TL[k] / SEC  # noqa: E731
    L = s("end")
    t = Track(L, "hold")
    # ---- the ring spins up and draws in; it sinks into the doll as it slams, and comes back empty at the end
    t.keys("ring", "rotation", [(0, S0), (s("tighten") * 0.5, [0, 90, 0], "easeInQuad"), (s("tighten"), [0, 420, 0], "easeInQuad"),
                                (s("slam"), [0, 420 + 360 * 7, 0]), (s("slam") + 0.3, [0, 420 + 360 * 7 + 120, 0], "easeOutQuad"), (L, [0, 420 + 360 * 7 + 120, 0])])
    t.keys("ring", "scale", [(0, ONE), (s("slam") - 0.4, ONE), (s("slam"), [0.2, 0.2, 0.2], "easeInBack"), (s("slam") + 0.05, HIDE, "step"),
                             (L - 0.5, HIDE), (L, ONE, "easeOutBack")])
    t.keys("ring", "position", [(0, S0), (s("tighten"), [0, 4, 0], "easeInOutSine"), (s("slam") - 0.4, [0, 4, 0]), (s("slam"), [0, -4, 0], "easeInQuad"),
                                (L, S0)])
    for i in range(10):
        w = ring_world(i)
        # drawn in along its arm (its socket lies at -Z of its arm)
        t.keys(f"sock{w}", "position", [(0, S0), (s("tighten"), [0, 0, RING_R - RING_IN], "easeInOutCubic"), (L, [0, 0, RING_R - RING_IN])])
    # ---- the upper half thrown open, slammed shut, opened a last time on the ingot, ajar again at the end
    t.keys("upper", "rotation", [(0, [AJAR, 0, 0]), (s("open") - 0.3, [AJAR - 6, 0, 0], "easeInOutSine"), (s("open") + 0.5, [OPEN, 0, 0], "easeOutBack"),
                                 (s("descend") + 0.2, [OPEN, 0, 0]), (s("slam"), [0, 0, 0], "easeInExpo"),
                                 (s("reveal"), [0, 0, 0]), (s("reveal") + 0.4, [OPEN * 0.72, 0, 0], "easeOutBack"),
                                 (L - 0.35, [OPEN * 0.72, 0, 0]), (L, [AJAR, 0, 0], "easeInOutSine")])
    # ---- the glow inside: brighter while the doll is open, flaring when it shuts
    t.keys("glow", "scale", [(0, ONE), (s("open"), [1.5, 2, 1.5], "easeOutQuad"), (s("slam"), [1.1, 1, 1.1]),
                             (s("slam") + 0.15, [2.2, 3, 2.2], "easeOutExpo"), (s("reveal"), ONE, "easeInQuad"), (L, ONE)])
    # ---- the nest: it rises out of the bowl, the dolls fan out and spin; one by one they close, the smallest first,
    # each into the next larger, until the largest sinks back into the bowl
    t.keys("nest", "scale", [(0, HIDE, "step"), (s("rise") - 0.05, HIDE, "step"), (s("rise"), [0.6, 0.6, 0.6]),
                             (s("rise") + 0.6, ONE, "easeOutBack"), (s("descend") + 0.55, ONE), (s("descend") + 0.6, HIDE, "step"), (L, HIDE, "step")])
    t.keys("nest", "position", [(0, S0), (s("rise"), S0), (s("rise") + 1.0, [0, NEST_UP, 0], "easeOutBack"), (s("descend"), [0, NEST_UP, 0]),
                                (s("descend") + 0.6, [0, 0, 0], "easeInBack"), (L, S0)])
    t.keys("nest", "rotation", [(0, S0), (s("rise"), S0), (s("close"), [0, 360, 0], "easeInQuad"),
                                (s("descend"), [0, 360 * 5, 0]), (s("descend") + 0.6, [0, 360 * 5 + 180, 0], "easeOutQuad"), (L, [0, 360 * 5 + 180, 0])])
    for k in range(10):
        arrive = s("close") + (9 - k) * TL["clack_every"] / SEC
        fan = [0, 0, -FAN_R]  # out along the arm (to -Z of the arm)
        keys = [(0, S0), (s("rise") + 0.2, S0), (s("rise") + 1.0 + k * 0.04, fan, "easeOutBack"), (arrive - 0.18, fan), (arrive, S0, "easeInBack")]
        t.keys(f"nd{k}", "position", keys + [(L, S0)])
        # a little hop as it lands over the one before
        t.keys(f"nd{k}", "rotation", [(0, S0), (s("rise") + 1.0, S0), (s("rise") + 1.6, [0, -36 * k, 0], "easeInOutSine"), (arrive - 0.18, [0, -36 * k, 0]),
                                      (arrive, [0, -36 * k - 360, 0], "easeInQuad"), (L, [0, -36 * k - 360, 0])])
        sc = [(0, ONE), (arrive - 0.1, ONE), (arrive, [1.15, 0.85, 1.15], "easeInQuad"), (arrive + 0.12, ONE, "easeOutBack")]
        if k < 9:
            pass
        # the one it closes over goes inside it: the smaller doll k+1 vanishes as doll k lands
        t.keys(f"nd{k}", "scale", sc + [(L, ONE)])
    for k in range(1, 10):
        over = s("close") + (9 - (k - 1)) * TL["clack_every"] / SEC
        t.key(f"nd{k}", "scale", over - 0.01, ONE)
        t.key(f"nd{k}", "scale", over, HIDE, "step")
        t.key(f"nd{k}", "scale", L, HIDE, "step")
    # ---- the whole doll jumps, shakes and glows as it shuts
    sl = s("slam")
    t.keys("body", "position", [(0, S0), (sl, S0), (sl + 0.18, [0, 7, 0], "easeOutQuad"), (sl + 0.36, S0, "easeInQuad"),
                                (sl + 0.44, [0, 1.5, 0], "easeOutQuad"), (sl + 0.52, S0, "easeInQuad"), (L, S0)])
    t.keys("body", "scale", [(0, ONE), (sl, ONE), (sl + 0.04, [1.12, 0.86, 1.12], "easeOutQuad"), (sl + 0.18, [0.94, 1.08, 0.94], "easeOutQuad"),
                             (sl + 0.36, [1.1, 0.9, 1.1], "easeInQuad"), (sl + 0.5, ONE, "easeOutBack"), (L, ONE)])
    shake = [(0, S0), (sl + 0.36, S0)]
    for j in range(8):
        shake.append((sl + 0.4 + j * 0.05, [0, 0, (5 if j % 2 else -5) * (1 - j / 8)]))
    shake += [(sl + 0.8, S0), (L, S0)]
    t.keys("body", "rotation", shake)
    # ---- the ingot rises out of the doll, spins and hovers; the server pops it at the end
    rv = s("reveal")
    t.keys("ingot", "scale", [(0, HIDE, "step"), (rv, HIDE, "step"), (rv + 0.3, [1.5, 1.5, 1.5], "easeOutBack"), (L - 0.1, [1.5, 1.5, 1.5]), (L, HIDE, "easeInBack")])
    t.keys("ingot", "position", [(0, S0), (rv, S0), (rv + 0.5, [0, 16, 0], "easeOutCubic"),
                                 (rv + 0.8, [0, 14.5, 0], "easeInOutSine"), (L - 0.15, [0, 16.5, 0], "easeInOutSine"), (L, [0, 17, 0])])
    t.keys("ingot", "rotation", [(0, S0), (rv, S0), (L, [0, 720, 0], "easeOutQuad")])
    return t


def animations():
    A = {"idle": idle().json(), "ritual": ritual().json()}
    for i in range(10):
        w = ring_world(i)
        on, lit, off = slot_anims(w)
        A[f"slot.{w}.on"], A[f"slot.{w}.lit"], A[f"slot.{w}.off"] = on.json(), lit.json(), off.json()
    return {"format_version": "1.8.0", "animations": A}


# =================================================================== gen.py
def gen(write, assets):
    bones = build()
    img, glow, tw = paint(bones)
    tex = os.path.join(assets, "textures/block")
    img.save(os.path.join(tex, f"{ID}.png"))
    glow.save(os.path.join(tex, f"{ID}_glowmask.png"))
    os.makedirs(os.path.join(assets, "geckolib/models/block"), exist_ok=True)
    os.makedirs(os.path.join(assets, "geckolib/animations/block"), exist_ok=True)
    write(os.path.join(assets, f"geckolib/models/block/{ID}.geo.json"), geo_json(bones, tw))
    write(os.path.join(assets, f"geckolib/animations/block/{ID}.animation.json"), animations())
    return len(bones)


if __name__ == "__main__":
    import sys
    from PIL import Image
    bones = build()
    img, glow, tw = paint(bones)
    img.resize((tw * 4, tw * 4), Image.NEAREST).save(sys.argv[1] if len(sys.argv) > 1 else "cradle_tex.png")
