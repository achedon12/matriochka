"""World 6, Upside Realm: inverted gravity, mirrors and glass.

The palette is cold silver, mirror teal and violet, with glowing cracks (mirror_glow) as the emissive accent.
Structural parts are axis-aligned (stepped), so the model looks the same in game as in the preview; rotated
cubes are only used for shards, rings and debris, where the sign of the tilt does not matter.
"""
import math

from common import Rig, mat

mat("refl_glass", "8ea8c8", "b4cce4", "crystal")
mat("refl_shirt", "348298", "5cb4c8", "crystal")
mat("refl_pants", "3a3e8a", "5a62b4", "crystal")
mat("refl_dark", "2e3450", "6a78a8", "crystal")
mat("refl_silver", "c4ccd8", "ffffff", "metal")
mat("refl_void", "0e0a20", "8a6aff", "spots")        # the nothing behind the glass, with a few stars in it
mat("crack", "5ae8d8", "b8fff4", "glow", True)


def _box(r, bone, xa, xb, ya, yb, za, zb, m):
    """A cube between two corners, in any order (handy for mirrored, stepped limbs)."""
    r.cube(bone, (min(xa, xb), min(ya, yb), min(za, zb)), (abs(xb - xa), abs(yb - ya), abs(zb - za)), m)


def reflection():
    """A mirror-glass copy of the player, flipped left for right: the familiar blocky body in teal and indigo glass,
    silver bevels, a glowing mirror seam down its middle, cracks running over the face and chest, a corner of the
    head and a chunk of the shin broken away onto starry void, a glass sword copied from yours and a shard buckler."""
    r = Rig("reflection")
    r.bone("body", None, (0, 18, 0), role="body")
    r.cube("body", (-4, 12, -2), (8, 12, 4), "refl_shirt")
    r.cube("body", (-4.2, 23.4, -2.2), (8.4, 0.8, 4.4), "refl_silver")    # collar bevel
    r.cube("body", (-4.2, 12, -2.2), (8.4, 0.8, 4.4), "refl_pants")       # belt line
    r.cube("body", (-0.15, 12.8, -2.25), (0.3, 10.6, 0.2), "crack")       # the mirror seam
    for (x, y, w, h) in ((1.0, 20.5, 2.2, 0.3), (2.9, 18.3, 0.3, 2.5), (1.6, 17.0, 1.6, 0.3), (-3.2, 15.2, 2.4, 0.3), (-1.2, 13.8, 0.3, 1.7)):
        r.cube("body", (x, y, -2.3), (w, h, 0.2), "crack")                # cracks over the chest
    r.cube("body", (-3, 17, -2.4), (2, 2, 0.4), "refl_glass", rot=[0, 0, 45], pivot=(-2, 18, -2.2))   # facets
    r.cube("body", (1.6, 21, -2.4), (1.4, 1.4, 0.4), "refl_glass", rot=[0, 0, 45], pivot=(2.3, 21.7, -2.2))
    r.cube("body", (-3.6, 21.8, 2.05), (2.6, 1.8, 0.2), "refl_void")      # a flake missing from the back
    # head
    r.bone("head", "body", (0, 24, 0), role="head")
    r.cube("head", (-4, 24, -4), (8, 8, 8), "refl_glass")
    r.cube("head", (-4.2, 30, -4.2), (8.4, 2.2, 8.4), "refl_dark")        # hair
    r.cube("head", (-4.2, 29, -4.2), (2.4, 1.0, 0.4), "refl_dark")        # fringe, notch on the wrong side
    r.cube("head", (-0.6, 29, -4.2), (4.8, 1.0, 0.4), "refl_dark")
    r.cube("head", (-4.2, 26, 3.8), (8.4, 4.2, 0.4), "refl_dark")         # back of the hair
    r.cube("head", (-4.0, 26.6, -4.3), (8, 1.8, 0.3), "refl_dark")        # shadowed eye line
    for s in (1, -1):                                                     # eyes, pupils on the inner side
        r.cube("head", (s * 2.4 - 1.0, 27, -4.5), (2, 1, 0.3), "eye_white")
        r.cube("head", (s * 1.9 - 0.5, 27, -4.6), (1, 1, 0.3), "crack")
    r.cube("head", (-1.0, 25.9, -4.4), (2, 0.8, 0.3), "refl_shirt")       # nose shadow
    r.cube("head", (-2.0, 24.9, -4.4), (4, 0.6, 0.3), "refl_dark")        # mouth
    for (x, y, w, h) in ((2.2, 30.0, 0.3, 1.5), (1.4, 28.2, 0.9, 0.3), (1.1, 26.4, 0.3, 1.9), (-1.6, 24.6, 2.7, 0.3)):
        r.cube("head", (x, y, -4.65), (w, h, 0.25), "crack")             # a crack across the face
    r.cube("head", (2.0, 30.2, -4.3), (2.3, 2.1, 2.3), "refl_void")       # corner broken away
    r.cube("head", (1.8, 30.0, -4.4), (0.4, 0.3, 0.3), "refl_silver")     # glints on the broken edge
    r.cube("head", (3.4, 29.9, -4.4), (0.6, 0.4, 0.3), "refl_silver")
    # arms
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 5, 22, 0), role=f"arm_{side}")
        r.cube(a, (s * 6 - 2, 12, -2), (4, 12, 4), "refl_glass")
        r.cube(a, (s * 6 - 2, 19.5, -2), (4, 4.5, 4), "refl_shirt")       # sleeve
        r.cube(a, (s * 6 - 2.2, 19.3, -2.2), (4.4, 0.5, 4.4), "refl_silver")
        r.cube(a, (s * 6 - 0.15, 13, -2.25), (0.3, 3.5, 0.2), "crack")
    # the copied sword, in the right hand
    _box(r, "arm_r", -7.6, -4.4, 12.0, 12.8, -3.0, -2.2, "refl_silver")  # crossguard
    _box(r, "arm_r", -6.4, -5.6, 12.0, 12.8, -2.2, 1.0, "refl_dark")     # grip
    _box(r, "arm_r", -6.3, -5.7, 11.6, 13.2, -11.5, -3.0, "refl_glass")  # glass blade
    _box(r, "arm_r", -6.35, -5.65, 12.25, 12.55, -11.6, -3.0, "crack")   # glowing edge
    _box(r, "arm_r", -6.2, -5.8, 11.9, 12.9, -12.6, -11.5, "refl_glass") # point
    # a shard buckler on the left forearm (reversed parry)
    _box(r, "arm_l", 8.0, 8.5, 13.2, 18.2, -2.6, 2.6, "refl_silver")
    _box(r, "arm_l", 8.4, 8.8, 13.8, 17.6, -2.0, 2.0, "refl_glass")
    _box(r, "arm_l", 8.75, 8.95, 15.5, 15.8, -1.6, 1.4, "crack")
    # legs
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 2, 12, 0), role=f"leg_{side}")
        r.cube(l, (s * 2 - 2, 0, -2), (4, 12, 4), "refl_pants")
        r.cube(l, (s * 2 - 2.1, 0, -2.3), (4.2, 1.6, 4.4), "refl_dark")   # shoes
    r.cube("leg_r", (-3.2, 4.0, -2.15), (2.0, 2.4, 0.3), "refl_void")     # chunk missing from the shin
    r.cube("leg_r", (-3.4, 6.3, -2.2), (0.6, 0.3, 0.3), "refl_silver")
    r.cube("leg_l", (2.4, 6.6, -2.2), (0.3, 3.0, 0.2), "crack")
    # glass shards circling
    for i, (x, y, z, rx) in enumerate(((9, 26, 3, 30), (-8.5, 21, -4, -40), (3, 33, 7, 60))):
        o = r.bone(f"shard{i}", "body", (0, y, 0), role="orbit")
        r.cube(o, (x - 0.4, y - 1, z - 0.15), (0.8, 2.2, 0.3), "refl_glass", rot=[rx, 25, 35], pivot=(x, y, z))
        r.cube(o, (x - 0.15, y - 0.5, z - 0.2), (0.3, 1.2, 0.35), "crack", rot=[rx, 25, 35], pivot=(x, y, z))
    return r


# --- Ceiling Walker
mat("walker_shell", "2a2442", "6e5ca8", "chitin")
mat("walker_belly", "c8c2de", "f2eeff", "skin")
mat("walker_leg", "241e38", "5c5094", "chitin")
mat("walker_joint", "8a80b8", "c0b8e8", "skin")
mat("walker_mark", "d860ff", "f4c8ff", "glow", True)
mat("walker_eye", "ff4ad0", "ffb8ee", "glow", True)
mat("silk", "e4e4f0", "ffffff", "cloth")


def ceiling_walker():
    """A spider turned upside down: its pale belly with a glowing hourglass faces the sky, its dorsal spines point at
    the floor, its face is flipped (big eyes at the bottom, fangs curling upward), and half its legs reach up to
    grip a ceiling that is not there, while a silk line rises from its spinnerets."""
    r = Rig("ceiling_walker")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-3.6, 3.4, -0.2), (7.2, 5, 7.6), "walker_shell")      # abdomen
    r.cube("body", (-3.0, 8.4, 0.4), (6, 0.8, 6.4), "walker_belly")       # pale belly, on top
    r.cube("body", (-2.6, 4.0, -4.6), (5.2, 3.6, 4.8), "walker_shell")    # cephalothorax
    r.cube("body", (-2.0, 7.6, -4.2), (4, 0.5, 4), "walker_belly")
    for (x, z, w) in ((-1.4, 1.0, 2.8), (-0.9, 1.8, 1.8), (-0.4, 2.6, 0.8), (-0.9, 3.4, 1.8), (-1.4, 4.2, 2.8)):
        r.cube("body", (x, 9.15, z), (w, 0.3, 0.8), "walker_mark")       # glowing hourglass on the belly
    r.cube("body", (-1.5, 8.6, 6.4), (3, 1.4, 1.2), "walker_shell")      # spinnerets, pointing up
    r.cube("body", (-0.6, 9.8, 6.6), (1.2, 0.8, 0.8), "walker_joint")
    r.cube("body", (-0.15, 10.6, 6.85), (0.3, 4.4, 0.3), "silk")          # silk line rising to the "ceiling"
    for (x, y, w, h) in ((-1.1, 14.6, 1.0, 0.25), (0.15, 14.8, 1.1, 0.25), (-1.6, 15.0, 0.5, 0.25), (1.2, 15.2, 0.5, 0.25)):
        r.cube("body", (x, y, 6.85), (w, h, 0.25), "silk")               # strands fanning out where it anchors
    for (x, z, h) in ((-2.2, 1.0, 1.6), (0.6, 2.4, 2.0), (2.0, 4.4, 1.4), (-1.0, 5.2, 1.2)):
        r.cube("body", (x, 3.4 - h, z), (0.6, h, 0.6), "walker_leg")      # dorsal spines, pointing down
    r.cube("body", (-3.2, 3.0, 0.4), (6.4, 0.6, 6.6), "walker_shell")    # rounder underside
    r.cube("body", (-3.9, 4.0, 0.8), (7.8, 3.6, 5.8), "walker_shell")    # rounder flanks
    for (x, z) in ((-3.95, 2.0), (-3.95, 4.4), (3.75, 2.0), (3.75, 4.4)):
        r.cube("body", (x, 5.6, z), (0.2, 0.6, 1.0), "walker_mark")       # glowing chevrons down the flanks
    # head, flipped
    r.bone("head", "body", (0, 6, -4.4), role="head")
    r.cube("head", (-2.2, 3.6, -7.0), (4.4, 3.6, 2.8), "walker_shell")
    for (x, y, sz) in ((-1.7, 3.9, 1.3), (0.4, 3.9, 1.3), (-1.4, 5.4, 0.7), (0.7, 5.4, 0.7), (-0.35, 5.4, 0.7),
                       (-2.0, 6.3, 0.5), (1.5, 6.3, 0.5), (-0.25, 6.4, 0.5)):
        r.cube("head", (x, y, -7.25), (sz, sz, 0.3), "walker_eye")        # big eyes at the bottom of the face
        if sz > 1:
            r.cube("head", (x + 0.35, y + 0.75, -7.4), (0.5, 0.4, 0.2), "pupil")   # pupils looking "down", to the sky
    j = r.bone("jaw", "head", (0, 7, -6.5), role="jaw")                   # chelicerae, curling upward
    for s in (1, -1):
        _box(r, j, s * 0.3, s * 1.6, 7.0, 8.6, -7.2, -5.8, "walker_shell")
        _box(r, j, s * 0.5, s * 1.3, 8.6, 9.8, -7.4, -6.6, "walker_joint")   # fang
        _box(r, j, s * 0.5, s * 0.9, 9.8, 10.4, -7.0, -6.6, "walker_joint")  # fang hook
    # legs: pairs 2 and 4 stand on the floor, pairs 1 and 3 reach up for the ceiling
    hips = (-3.6, -2.4, -1.2, 0.0)
    splay = (-3.0, -1.0, 1.0, 3.0)
    for i, (z, dz) in enumerate(zip(hips, splay)):
        up = i in (0, 2)
        for s, side in ((1, "l"), (-1, "r")):
            role = f"arm_{side}" if up else f"leg_{side}"
            b = r.bone(f"leg{i}_{side}", "body" if up else None, (s * 2.4, 6, z), role=role)
            if up:   # hip, knee straight up, out along the ceiling, tip pressed against it
                pts = [(2.4, 6.6, z), (4.2, 6.6, z), (4.2, 11.6, z + dz * 0.3), (6.9, 11.6, z + dz * 0.7), (6.9, 14.6, z + dz)]
            else:    # hip, high knee, long shin down to the floor
                pts = [(2.4, 5.6, z), (5.2, 5.6, z), (5.2, 9.8, z + dz * 0.3), (7.6, 9.8, z + dz * 0.7), (7.6, 0.6, z + dz)]
            for k, ((x0, y0, z0), (x1, y1, z1)) in enumerate(zip(pts, pts[1:])):
                t = 1.0 if k < 2 else 0.8
                _box(r, b, s * (min(x0, x1) - t / 2), s * (max(x0, x1) + t / 2), min(y0, y1) - t / 2, max(y0, y1) + t / 2,
                     min(z0, z1) - t / 2, max(z0, z1) + t / 2, "walker_leg")
                if k in (1, 2):
                    _box(r, b, s * (x1 - 0.65), s * (x1 + 0.65), y1 - 0.65, y1 + 0.65, z1 - 0.65, z1 + 0.65, "walker_joint")
            x, y, zz = pts[-1]
            if up:
                _box(r, b, s * (x - 1.4), s * (x + 0.4), y + 0.2, y + 0.8, zz - 0.4, zz + 0.4, "walker_joint")   # hook gripping the ceiling
            else:
                _box(r, b, s * (x - 0.3), s * (x + 0.3), 0, 0.6, zz - 0.3, zz + 0.3, "walker_joint")             # claw tip
    return r


# --- Unstable Sphere
mat("sphere_shell", "2c2850", "8a7ae0", "crystal")
mat("sphere_core", "b866ff", "dca4ff", "glow", True)
mat("sphere_ring", "8a50e8", "b888ff", "glow", True)
mat("sphere_lens", "0a0818", "3a2a6a", "skin")
mat("w6_grass_top", "5a9a3a", "8ac85a", "leaf")
mat("stone_chip", "7a7a80", "a0a0a8", "blocks")
mat("torch_stick", "6a4a2a", "8a6438", "bark")
mat("water_drop", "3a7ae0", "a0d0ff", "glow", True)


def _tilted_ring(r, parent, name, cy, radius, tilt, m, th=0.45, role="orbit"):
    o = r.bone(name, parent, (0, cy, 0), role=role)
    t = r.bone(name + "_tilt", o, (0, cy, 0), rot=tilt)
    w = 2 * radius * 0.414 * 0.7
    for k in range(8):
        r.cube(t, (-w / 2, cy - th / 2, -radius - th / 2), (w, th, th), m, rot=[0, k * 45, 0], pivot=(0, cy, 0))
    return o


def unstable_sphere():
    """An orb of broken gravity: a dark glass shell split into plates that drift apart over a violet core, a lens on
    its face where space bends inward, tilted rings turning the wrong way, debris orbiting it (an upside-down grass
    block, a stone chip, a torch burning downward), rubble lifted off the floor and drops of water falling up."""
    r = Rig("unstable_sphere")
    r.bone("body", None, (0, 10, 0), role="body")
    r.cube("body", (-3.4, 6.6, -3.4), (6.8, 6.8, 6.8), "sphere_core")     # the core
    # a voxel sphere of dark glass, broken into fragments that drift off the core
    r.cube("body", (-5, 7, -3), (10, 6, 6), "sphere_shell")
    r.cube("body", (-3, 5, -3), (6, 10, 6), "sphere_shell")
    r.cube("body", (-3, 7, -5), (6, 6, 10), "sphere_shell")
    r.cube("body", (-3.8, 6.2, -3.8), (3.2, 3.2, 3.2), "sphere_shell")    # corner fragments, one pushed out of place
    r.cube("body", (0.6, 6.2, -3.8), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (-3.8, 10.6, 0.6), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (0.6, 10.6, 0.6), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (-3.8, 6.2, 0.6), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (0.6, 6.2, 0.6), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (-3.8, 10.6, -3.8), (3.2, 3.2, 3.2), "sphere_shell")
    r.cube("body", (1.6, 11.4, -5.6), (3.4, 3.4, 3.4), "sphere_shell", rot=[18, 24, 12], pivot=(3.3, 13.1, -3.9))   # torn loose
    r.cube("body", (-5.6, 3.6, -1.2), (2.2, 2.2, 2.2), "sphere_shell", rot=[30, 15, 40], pivot=(-4.5, 4.7, -0.1))  # a falling-up flake
    # the lens: space bending inward
    r.cube("body", (-2.6, 7.4, -5.4), (5.2, 5.2, 0.5), "sphere_core")
    r.cube("body", (-1.9, 8.1, -5.7), (3.8, 3.8, 0.5), "sphere_lens")
    r.cube("body", (-1.2, 8.8, -6.0), (2.4, 2.4, 0.5), "sphere_core")
    r.cube("body", (-0.6, 9.4, -6.3), (1.2, 1.2, 0.5), "sphere_lens")
    for (x, y, w, h) in ((-2.9, 12.6, 0.3, 0.8), (2.6, 6.4, 0.3, 1.0), (-4.6, 8.0, 0.3, 1.8)):
        r.cube("body", (x, y, -5.3), (w, h, 0.4), "sphere_core")          # cracks in the shell
    # rubble lifted off the floor, drops falling up
    for (x, y, z, sz) in ((0.6, 0.6, 0.4, 1.2), (-1.4, 2.2, -0.8, 0.9), (0.9, 3.6, -1.0, 0.7)):
        r.cube("body", (x, y, z), (sz, sz, sz), "stone_chip")
    for (x, y, z) in ((1.6, 16.2, -1.0), (-1.2, 17.4, 0.8), (0.2, 19.0, 0.0)):
        r.cube("body", (x, y, z), (0.6, 0.9, 0.6), "water_drop")
    # rings
    _tilted_ring(r, "body", "ring0", 10, 8.0, [24, 0, 0], "sphere_ring")
    _tilted_ring(r, "body", "ring1", 10, 6.8, [-10, 0, 62], "sphere_shell", th=0.6)
    # orbiting debris
    o = r.bone("debris0", "body", (0, 10, 0), role="orbit")
    r.cube(o, (8.0, 11.5, -1), (2.2, 1.6, 2.2), "dirt", rot=[0, 20, 180], pivot=(9.1, 12.4, 0.1))  # grass block, upside down
    r.cube(o, (8.0, 11.0, -1), (2.2, 0.6, 2.2), "w6_grass_top", rot=[0, 20, 0], pivot=(9.1, 12.4, 0.1))
    r.cube(o, (-10, 8, 3), (1.6, 1.4, 1.2), "stone_chip", rot=[30, 40, 15], pivot=(-9.2, 8.7, 3.6))
    o2 = r.bone("debris1", "body", (0, 10, 0), role="orbit")
    r.cube(o2, (-1.0, 14.5, 8.5), (0.5, 2.0, 0.5), "torch_stick")              # a torch burning downward
    r.cube(o2, (-1.1, 13.8, 8.4), (0.7, 0.7, 0.7), "ember")
    r.cube(o2, (2.0, 5.5, -8.8), (1.2, 1.2, 1.2), "stone_chip", rot=[45, 45, 0], pivot=(2.6, 6.1, -8.2))
    return r



# --- Inverted Strider
mat("istr_skin", "2c8c94", "6ad8d0", "flesh")
mat("istr_glass", "6ab8c8", "d8fbff", "crystal")      # the reflected half: same creature, in mirror glass
mat("istr_leg", "245a66", "4a98a4", "skin")
mat("istr_band", "1a3a44", "2a5a66", "skin")
mat("istr_hair", "c8e8ec", "ffffff", "cloth")
mat("istr_mouth", "0e2028", "2a4a52", "flesh")


def inverted_strider():
    """A strider built upside down around a glowing mirror line: two stilts on the floor and their reflection, in
    glass, standing on the sky with soles turned up. Its head hangs under the body on a long neck, face flipped
    (mouth and upward teeth above the eyes, pupils rolled to the top), and its hair hangs down while the
    reflected hair on top rises."""
    r = Rig("inverted_strider")
    r.bone("body", None, (0, 19, 0), role="body")
    r.cube("body", (-5, 15, -4), (10, 4, 8), "istr_skin")                 # real half
    r.cube("body", (-5, 19.4, -4), (10, 4, 8), "istr_glass")              # reflected half
    r.cube("body", (-5.3, 18.9, -4.3), (10.6, 0.6, 8.6), "crack")         # the mirror line
    r.cube("body", (-4.5, 14.4, -3.5), (9, 0.6, 7), "istr_band")
    r.cube("body", (-4.5, 23.4, -3.5), (9, 0.6, 7), "istr_glass")
    for (x, z, h) in ((-3.5, -2.5, 3.0), (-1.2, 1.0, 4.2), (1.5, -1.8, 3.4), (3.2, 2.0, 2.4), (0.2, -3.2, 2.0)):
        r.cube("body", (x, 24, z), (0.7, h, 0.7), "istr_hair")            # reflected hair, falling upward
    for (x, y, z) in ((-5.2, 16.5, -2), (5.0, 17.0, 1.5), (-5.2, 21.0, 1.5), (5.0, 20.5, -2)):
        r.cube("body", (x, y, z), (0.3, 1, 1), "istr_band")               # pores, mirrored above and below
    # head hanging below, flipped
    r.bone("head", "body", (0, 15, 0), role="head")
    r.cube("head", (-1, 10.5, -1), (2, 5, 2), "istr_skin")                # neck
    r.cube("head", (-3, 5, -3.2), (6, 6, 6), "istr_skin")
    r.cube("head", (-3.3, 9.8, -3.5), (6.6, 1.4, 6.6), "istr_band")       # the brow, now its chin
    r.cube("head", (-2.4, 8.4, -3.45), (4.8, 1.2, 0.3), "istr_mouth")     # mouth, above the eyes
    for x in (-2.0, -1.0, 0.0, 1.0, 1.8):
        r.cube("head", (x, 8.0, -3.55), (0.5, 0.8 if x in (-2.0, 1.8) else 0.5, 0.3), "tooth")   # teeth pointing up
    for s in (1, -1):
        r.cube("head", (s * 1.5 - 0.9, 6.0, -3.5), (1.8, 1.4, 0.3), "eye_white")
        r.cube("head", (s * 1.5 - 0.4, 6.8, -3.6), (0.8, 0.6, 0.3), "pupil")   # pupils rolled up
    for (x, z, h) in ((-2.6, -2.6, 3.0), (-0.8, -2.8, 4.0), (1.0, -2.6, 3.4), (2.4, -1.0, 2.6), (-2.2, 1.6, 3.6), (1.6, 2.0, 3.2), (0.0, 0.2, 4.5)):
        r.cube("head", (x, 5 - h, z), (0.7, h, 0.7), "istr_hair")         # hair hanging under the head
    j = r.bone("jaw", "head", (0, 9.6, -3), role="jaw")
    r.cube(j, (-2.6, 9.6, -3.5), (5.2, 0.4, 0.4), "istr_band")            # the lip that opens upward
    # stilts on the floor: thin, knees bent backward
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 4.2, 15.5, 0), role=f"leg_{side}")
        r.cube(l, (s * 4.2 - 0.9, 8, -0.9), (1.8, 8, 1.8), "istr_leg")
        r.cube(l, (s * 4.2 - 1.1, 7.0, -0.6), (2.2, 1.6, 2.2), "istr_band")   # knee, pushed back
        r.cube(l, (s * 4.2 - 0.7, 1, 0.0), (1.4, 6.6, 1.4), "istr_leg")
        r.cube(l, (s * 4.2 - 0.75, 3.8, -0.05), (1.5, 0.4, 1.5), "istr_band")
        r.cube(l, (s * 4.2 - 1.3, 0, -1.4), (2.6, 1.2, 3.0), "istr_band")     # splayed foot
        r.cube(l, (s * 4.2 - 1.1, 0, -2.2), (0.6, 0.6, 0.8), "mirror_claw")
        r.cube(l, (s * 4.2 + 0.5, 0, -2.2), (0.6, 0.6, 0.8), "mirror_claw")
    # their reflection in glass, standing on the sky
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 4.2, 22.5, 0), role=f"arm_{side}")
        r.cube(a, (s * 4.2 - 0.9, 22, -0.9), (1.8, 8, 1.8), "istr_glass")
        r.cube(a, (s * 4.2 - 1.1, 29.4, -0.6), (2.2, 1.6, 2.2), "istr_band")
        r.cube(a, (s * 4.2 - 0.7, 30.4, 0.0), (1.4, 6.6, 1.4), "istr_glass")
        r.cube(a, (s * 4.2 - 1.3, 36.8, -1.4), (2.6, 1.2, 3.0), "istr_band")  # sole turned up to the sky
        r.cube(a, (s * 4.2 - 1.1, 37.4, -2.2), (0.6, 0.6, 0.8), "mirror_claw")
        r.cube(a, (s * 4.2 + 0.5, 37.4, -2.2), (0.6, 0.6, 0.8), "mirror_claw")
        r.cube(a, (s * 4.2 - 0.15, 23, -1.05), (0.3, 5, 0.2), "crack")
        r.cube(a, (s * 4.2 - 0.6, 33.0, -0.1), (1.2, 0.3, 0.2), "crack")
    return r


# --- Broken Mirror
mat("bm_frame", "665e76", "d8d0e8", "metal")
mat("bm_glass", "9ab8d4", "e8f8ff", "crystal")
mat("bm_back", "3a2a22", "5a4232", "bark")
mat("mirror_claw", "c8ccd6", "ffffff", "skin")
mat("bm_gem", "c47aff", "f0d8ff", "glow", True)


def broken_mirror():
    """A tall standing mirror on clawed feet, its tarnished silver frame crowned with a violet gem. The glass is
    starred by an impact: glowing cracks run from a hole of starry void, a face stares out of the glass with one eye
    in the pane and the other peering from the hole, shards are stuck in the frame and a ring of them circles it."""
    r = Rig("broken_mirror")
    r.bone("body", None, (0, 8, 0), role="body")
    r.cube("body", (-5.5, 1.6, -2.4), (11, 1.8, 4.8), "bm_frame")         # pedestal
    r.cube("body", (-4.5, 3.2, -1.6), (9, 0.6, 3.2), "bm_frame")
    # frame
    r.cube("body", (-6, 15, -1), (12, 1.3, 2), "bm_frame")
    r.cube("body", (-6, 3.6, -1), (12, 1.2, 2), "bm_frame")
    r.cube("body", (-6, 3.6, -1), (1.3, 12.7, 2), "bm_frame")
    r.cube("body", (4.7, 3.6, -1), (1.3, 12.7, 2), "bm_frame")
    r.cube("body", (-2.6, 16.3, -0.8), (5.2, 1.0, 1.6), "bm_frame")       # crest
    r.cube("body", (-1.4, 17.3, -0.7), (2.8, 0.8, 1.4), "bm_frame")
    r.cube("body", (-0.6, 17.0, -1.1), (1.2, 1.2, 0.5), "bm_gem")
    for (x, y) in ((-6.3, 15.4), (5.3, 15.4), (-6.3, 3.2), (5.3, 3.2)):
        r.cube("body", (x, y, -1.2), (1, 1.2, 2.4), "bm_frame")           # corner bosses
    r.cube("body", (-4.8, 4.8, 0.5), (6.0, 10.2, 0.6), "bm_back")         # wooden back (two boards)
    r.cube("body", (1.2, 4.8, 0.5), (3.6, 5.4, 0.6), "bm_back")
    r.cube("body", (1.2, 10.2, 0.5), (3.6, 4.8, 0.6), "bm_back")
    r.cube("body", (-0.5, 4.8, 1.1), (1, 10.2, 0.5), "bm_back")           # brace
    r.cube("body", (-4.8, 9.4, 1.1), (9.6, 1, 0.5), "bm_back")
    for (x, y, w, h) in ((-4.8, 14.6, 9.6, 0.4), (-4.8, 4.8, 9.6, 0.4), (-4.8, 4.8, 0.4, 10.2), (4.4, 4.8, 0.4, 10.2)):
        r.cube("body", (x, y, -0.7), (w, h, 0.4), "refl_silver")          # silver bevel around the glass
    # glass, around a hole at the upper right
    r.cube("body", (-4.7, 4.8, -0.4), (5.9, 3.6, 0.8), "bm_glass")
    r.cube("body", (-4.7, 8.4, -0.4), (5.9, 6.6, 0.8), "bm_glass")
    r.cube("body", (1.2, 4.8, -0.4), (3.5, 5.4, 0.8), "bm_glass")
    r.cube("body", (1.2, 10.2, -0.4), (1.0, 2.6, 0.8), "bm_glass")        # jagged edge of the hole
    r.cube("body", (3.6, 13.8, -0.4), (1.1, 1.2, 0.8), "bm_glass")
    r.cube("body", (3.0, 10.2, -0.4), (1.7, 0.8, 0.8), "bm_glass")
    r.cube("body", (1.2, 10.2, 0.2), (3.5, 4.8, 0.4), "refl_void")        # starry nothing behind
    for (x, y, w, h) in ((0.6, 9.6, 0.3, 4.0), (-1.4, 9.4, 2.2, 0.3), (-1.6, 6.4, 0.3, 3.2), (-4.0, 6.2, 2.6, 0.3),
                         (2.6, 7.2, 0.3, 3.0), (2.6, 7.0, 1.8, 0.3), (-0.6, 13.2, 1.8, 0.3), (-2.6, 12.0, 0.3, 1.5),
                         (-4.4, 11.8, 1.8, 0.3)):
        r.cube("body", (x, y, -0.75), (w, h, 0.35), "crack")             # cracks radiating from the hole
    for (x, y, z, h) in ((-6.4, 9, -0.3, 2.0), (5.6, 6.5, -0.2, 1.6)):
        r.cube("body", (x, y, z), (0.9, h, 0.3), "bm_glass", rot=[0, 0, 35], pivot=(x, y, z))   # shards stuck in the frame
    r.cube("body", (-3.5, 3.4, -2.2), (1.4, 0.3, 0.8), "bm_glass")       # splinters fallen on the pedestal
    r.cube("body", (2.0, 3.4, -2.1), (0.8, 0.3, 1.2), "bm_glass")
    # the face in the glass
    r.bone("head", "body", (0, 9.5, -0.5), role="head")
    r.cube("head", (-3.8, 10.0, -0.95), (2.6, 1.6, 0.5), "eye_white")     # eye in the pane
    r.cube("head", (-3.0, 10.1, -1.15), (1.2, 1.4, 0.3), "mirror_glow")
    r.cube("head", (-2.7, 10.4, -1.3), (0.6, 0.8, 0.2), "pupil")
    r.cube("head", (-4.0, 11.8, -1.0), (3.2, 0.5, 0.5), "bm_frame")       # brow, frowning down
    r.cube("head", (-1.6, 11.5, -1.0), (0.8, 0.5, 0.5), "bm_frame")
    r.cube("head", (2.0, 11.2, -0.2), (1.8, 1.4, 0.4), "mirror_glow")     # the other eye, peering from the hole
    r.cube("head", (2.6, 11.4, -0.35), (0.6, 1.0, 0.2), "pupil")
    j = r.bone("jaw", "head", (0, 7.6, -0.6), role="jaw")
    r.cube(j, (-3.8, 6.4, -1.0), (6.6, 1.3, 0.55), "refl_void")           # grinning mouth, crooked
    r.cube(j, (2.4, 7.4, -1.0), (1.0, 0.6, 0.55), "refl_void")
    for k, x in enumerate((-3.4, -2.4, -1.4, -0.4, 0.6, 1.6)):
        r.cube(j, (x, 7.0 if k % 2 else 6.4, -1.15), (0.5, 0.7, 0.2), "bm_glass")   # glass teeth
    # clawed feet
    for i, (x, z) in enumerate(((4.4, -1.6), (-4.4, -1.6), (4.4, 1.6), (-4.4, 1.6))):
        side = "l" if x > 0 else "r"
        f = r.bone(f"foot{i}", None, (x, 2.5, z), role=f"leg_{side}")
        r.cube(f, (x - 1, 0.4, z - 1), (2, 2, 2), "bm_frame")
        for k in (-0.6, 0.2):
            r.cube(f, (x + k, 0, z - 1.8 if z < 0 else z + 0.8), (0.5, 0.6, 1.0), "mirror_claw")
    # shards circling
    for i, (ang, y, rad) in enumerate(((20, 14, 8.5), (110, 8, 9), (200, 12, 8), (290, 5, 8.5), (160, 17, 7))):
        o = r.bone(f"shard{i}", "body", (0, y, 0), role="orbit")
        x, z = math.cos(math.radians(ang)) * rad, math.sin(math.radians(ang)) * rad
        r.cube(o, (x - 0.5, y - 1.2, z - 0.15), (1.0, 2.6, 0.3), "bm_glass", rot=[15, ang, 30], pivot=(x, y, z))
        r.cube(o, (x - 0.15, y - 0.6, z - 0.2), (0.3, 1.4, 0.35), "crack", rot=[15, ang, 30], pivot=(x, y, z))
    return r

