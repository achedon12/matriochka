"""Boss models, part B: worlds 6 to 10 (your_double, pressure_leviathan, seasons_master, terrain_heart_boss,
the_unfinished). Each function returns a Rig built with the bosses_hd DSL; animations come from
bosses_hd.standard_anims(rig) through the bone roles (body, head, jaw, arm_*, leg_*, tail, seg, cape, wing_*, orbit,
pulse, shell_top, shell_bottom).

Conventions: front is -Z, up is +Y, feet on y = 0, 16 units = 1 block. Structural parts stay axis-aligned and stepped;
rotated cubes are kept for cracks, shards, spikes, leaves and other details where the sign of a tilt does not matter.
Every material added here is prefixed with bb_ so it cannot clash with the creatures' palettes.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from bosses_hd import Rig, MAT  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mobs_hd'))
import common  # noqa: E402,F401  (registers the shared creature materials: eye_white, pupil, tooth, brass...)


def M(name, base, accent, pattern="skin", emissive=False):
    MAT[name] = (base, accent, pattern, emissive)
    return name


def B(r, bone, xa, xb, ya, yb, za, zb, m, **kw):
    """A cube between two corners, in any order."""
    r.cube(bone, (min(xa, xb), min(ya, yb), min(za, zb)), (abs(xb - xa), abs(yb - ya), abs(zb - za)), m, **kw)


def octo(r, bone, cx, cz, ya, yb, w, d, cut, m, m2=None):
    """A bevelled block (an octagon seen from above) out of two crossed cubes."""
    B(r, bone, cx - w / 2, cx + w / 2, ya, yb, cz - d / 2 + cut, cz + d / 2 - cut, m)
    B(r, bone, cx - w / 2 + cut, cx + w / 2 - cut, ya, yb, cz - d / 2, cz + d / 2, m2 or m)


def seg2d(r, bone, a, b, z, m, t=0.35, dz=0.3):
    """A thin straight line from a=(x, y) to b=(x, y) lying on the plane z (a crack, a painted stroke)."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0) + t * 0.6
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    r.cube(bone, (mx - L / 2, my - t / 2, z), (L, t, dz), m, rot=[0, 0, round(ang, 2)], pivot=(mx, my, z))


def poly2d(r, bone, pts, z, m, t=0.35, dz=0.3):
    for a, b in zip(pts, pts[1:]):
        seg2d(r, bone, a, b, z, m, t, dz)


def segside(r, bone, a, b, x, m, t=0.35, dx=0.3):
    """A thin line on a side plane x, from a=(z, y) to b=(z, y)."""
    (z0, y0), (z1, y1) = a, b
    L = math.hypot(z1 - z0, y1 - y0) + t * 0.6
    mz, my = (z0 + z1) / 2, (y0 + y1) / 2
    ang = math.degrees(math.atan2(y1 - y0, z1 - z0))
    r.cube(bone, (x, my - t / 2, mz - L / 2), (dx, t, L), m, rot=[-round(ang, 2), 0, 0], pivot=(x, my, mz))


# =====================================================================================================================
# World 6 - Your Double
# =====================================================================================================================
M("bb_dbl_glass", "b4c2dc", "eef4ff", "crystal")        # the lit half: silver mirror glass
M("bb_dbl_dark", "262040", "5e5296", "crystal")         # the inverted half: the same glass as a negative
M("bb_dbl_shirt", "3e9cb4", "a8eef4", "crystal")
M("bb_dbl_shirt_n", "14303e", "3a8296", "crystal")
M("bb_dbl_pants", "3c4aa8", "8c9cf0", "crystal")
M("bb_dbl_pants_n", "141638", "34407a", "crystal")
M("bb_dbl_hair", "2a2044", "4a3a72", "crystal")
M("bb_dbl_hair_n", "dcd4f4", "ffffff", "crystal")
M("bb_dbl_shoe", "3a3448", "6a6080", "metal")
M("bb_dbl_shoe_n", "c8c4d8", "ffffff", "metal")
M("bb_dbl_silver", "d4dbe6", "ffffff", "metal")
M("bb_crack", "5ae8f4", "8af4ff", "glow", True)
M("bb_crack_v", "b47aff", "c89aff", "glow", True)
M("bb_dbl_face", "c4d0e6", "e0e8f8", "skin")
M("bb_dbl_face_n", "2c2646", "3a3258", "skin")       # violet cracks on the dark half
M("bb_dbl_void", "0c0820", "8a6aff", "spots")           # the nothing showing where glass broke away
M("bb_dbl_eye_n", "f4fbff", "ffffff", "glow", True)     # the negative's pupil: light where yours is dark
M("bb_dbl_frame", "c89a3e", "f4d88a", "metal")
M("bb_dbl_frame_d", "7a5a24", "b08a44", "metal")
M("bb_dbl_core", "8af8ff", "ffffff", "glow", True)


def your_double():
    """You, in mirror glass, split down the middle into a positive and its negative: the left half silver, teal and
    indigo, the right half the same body inverted into black glass with pale hair. A glowing mirror seam runs from
    the crown to the belt, cracks branch over the face and chest, glass has broken away from a corner of the head, a
    shoulder and a shin onto starry void, and a cracked heart of light beats in a hole in the chest. Its hair floats
    up (gravity is the other way here), splintered glass grows from its shoulders, it holds a glass copy of your
    sword, the copies of your other tools orbit it, and the broken gilded frame it stepped out of hangs behind it."""
    r = Rig("your_double")
    u = 1.35  # player pixels -> model units
    P = lambda v: v * u  # noqa: E731
    r.bone("body", None, (0, P(12), 0), role="body")
    bd = "body"
    # --- torso: two halves, a positive and a negative
    B(r, bd, 0, P(4), P(12), P(24), -P(2), P(2), "bb_dbl_shirt")
    B(r, bd, -P(4), 0, P(12), P(24), -P(2), P(2), "bb_dbl_shirt_n")
    B(r, bd, 0, P(4.2), P(12) - 0.4, P(13.6), -P(2.15), P(2.15), "bb_dbl_pants")      # waistband
    B(r, bd, -P(4.2), 0, P(12) - 0.4, P(13.6), -P(2.15), P(2.15), "bb_dbl_pants_n")
    B(r, bd, -1.4, 1.4, P(12.2), P(13.4), -P(2.15) - 0.3, -P(2.15), "bb_dbl_silver")   # buckle
    B(r, bd, -0.6, 0.6, P(12.5), P(13.1), -P(2.15) - 0.5, -P(2.15) - 0.2, "bb_crack")
    B(r, bd, 0, P(4.15), P(23.2), P(24.2), -P(2.15), P(2.15), "bb_dbl_silver")         # collar bevel
    B(r, bd, -P(4.15), 0, P(23.2), P(24.2), -P(2.15), P(2.15), "bb_dbl_shoe")
    zf = -P(2) - 0.25
    # V neck
    B(r, bd, -1.6, 1.6, P(22.4), P(24), zf - 0.05, zf + 0.3, "bb_dbl_glass")
    B(r, bd, -0.8, 0.8, P(21.6), P(22.5), zf - 0.05, zf + 0.3, "bb_dbl_glass")
    # the mirror seam down the middle
    poly2d(r, bd, [(0, P(23.9)), (0.4, P(21.5)), (-0.3, P(19.6)), (0.35, P(17.0)), (-0.25, P(15.2)), (0.2, P(13.6))], zf - 0.1, "bb_crack", 0.45)
    # hole in the chest and its heart of light
    B(r, bd, -3.2, 1.0, P(17.6), P(20.6), zf - 0.15, zf + 0.25, "bb_dbl_void")
    core = r.bone("heart", bd, (-1.1, P(19.1), -P(2)), role="pulse")
    r.cube(core, (-2.4, P(19.1) - 1.3, zf - 0.9), (2.6, 2.6, 1.6), "bb_dbl_core", rot=[0, 0, 45], pivot=(-1.1, P(19.1), zf))
    r.cube(core, (-1.7, P(19.1) - 0.6, zf - 1.15), (1.2, 1.2, 0.6), "eye_white", rot=[0, 0, 45], pivot=(-1.1, P(19.1), zf))
    for (x, y, w, h) in ((-3.5, P(17.4), 1.4, 0.6), (0.7, P(20.3), 0.9, 1.0), (-3.6, P(20.2), 0.8, 0.9), (0.6, P(17.3), 1.0, 0.7)):
        B(r, bd, x, x + w, y, y + h, zf - 0.4, zf + 0.1, "bb_dbl_silver")        # jagged glass rim
    # cracks branching from the hole
    poly2d(r, bd, [(1.0, P(19.5)), (2.6, P(20.4)), (3.4, P(22.6)), (4.6, P(23.4))], zf - 0.05, "bb_crack")
    poly2d(r, bd, [(1.0, P(18.2)), (2.8, P(17.0)), (2.4, P(15.0)), (4.0, P(14.0))], zf - 0.05, "bb_crack")
    poly2d(r, bd, [(-3.2, P(18.0)), (-4.0, P(16.0)), (-3.0, P(14.2))], zf - 0.05, "bb_crack_v")
    poly2d(r, bd, [(-3.2, P(20.4)), (-4.4, P(22.0)), (-3.6, P(23.4))], zf - 0.05, "bb_crack_v")
    # facets glinting on the glass
    r.cube(bd, (2.6, P(15.6), zf - 0.05), (1.6, 1.6, 0.3), "bb_dbl_silver", rot=[0, 0, 45], pivot=(3.4, P(15.6) + 0.8, zf))
    r.cube(bd, (-4.6, P(14.4), zf - 0.05), (1.2, 1.2, 0.3), "bb_dbl_dark", rot=[0, 0, 45], pivot=(-4, P(14.4) + 0.6, zf))
    # back: a flake missing, cracks
    zb = P(2) + 0.05
    B(r, bd, 1.0, 4.4, P(19), P(22.4), zb - 0.3, zb + 0.15, "bb_dbl_void")
    poly2d(r, bd, [(0, P(13)), (0.5, P(16)), (-0.4, P(19)), (0.3, P(23.5))], zb, "bb_crack", 0.45)
    poly2d(r, bd, [(-1, P(21)), (-3.4, P(18.6)), (-5, P(19.2))], zb, "bb_crack_v")
    # splintered glass growing from the shoulders
    for s, m, mc in ((1, "bb_dbl_glass", "bb_crack"), (-1, "bb_dbl_dark", "bb_crack_v")):
        for (dx, h, tilt, dz) in ((1.6, 6.0, -14, -1.2), (3.6, 4.4, -32, 0.6), (-0.2, 3.6, 6, 1.6)):
            x = s * (P(4) - 1.0 - dx * 0.4)
            y = P(24) - 0.6
            r.cube(bd, (x - 0.8, y, dz - 0.8), (1.6, h, 1.6), m, rot=[0, 0, s * tilt], pivot=(x, y, dz))
            r.cube(bd, (x - 0.25, y + 0.6, dz - 0.95), (0.5, h * 0.7, 0.3), mc, rot=[0, 0, s * tilt], pivot=(x, y, dz))

    # --- head
    h = r.bone("head", bd, (0, P(24), 0), role="head")
    B(r, h, 0, P(4), P(24), P(32), -P(4), P(4), "bb_dbl_face")
    B(r, h, -P(4), 0, P(24), P(32), -P(4), P(4), "bb_dbl_face_n")
    zh = -P(4)
    # hair: dark on the light half, pale on the dark half; it floats upward
    B(r, h, 0, P(4.2), P(30.2), P(32.4), -P(4.2), P(4.2), "bb_dbl_hair")
    B(r, h, -P(4.2), 0, P(30.2), P(32.4), -P(4.2), P(4.2), "bb_dbl_hair_n")
    B(r, h, 0, P(4.2), P(26), P(30.4), P(2.8), P(4.2), "bb_dbl_hair")
    B(r, h, -P(4.2), 0, P(26), P(30.4), P(2.8), P(4.2), "bb_dbl_hair_n")
    B(r, h, P(1.2), P(4.2), P(29.2), P(30.4), zh - 0.45, zh, "bb_dbl_hair")            # fringe, notch on the wrong side
    B(r, h, -P(4.2), -P(1.6), P(29.2), P(30.4), zh - 0.45, zh, "bb_dbl_hair_n")
    for (x, z, hh, tilt) in ((3.4, -3.2, 3.6, -16), (1.4, 0.6, 4.6, 8), (4.4, 3.0, 3.0, -28),
                             (-1.6, -2.4, 4.2, 14), (-3.8, 1.8, 3.4, 26), (-0.4, 3.4, 2.6, -6)):
        m = "bb_dbl_hair" if x > 0 else "bb_dbl_hair_n"
        r.cube(h, (x - 1.0, P(32.2), z - 1.0), (2.0, hh, 2.0), m, rot=[0, 0, tilt], pivot=(x, P(32.2), z))   # hair lifting
    # brow shadow and eyes
    #   left eye (positive): white, glowing teal iris, black pupil
    B(r, h, P(0.8), P(3.2), P(26.8), P(28.4), zh - 0.45, zh, "eye_white")
    B(r, h, P(0.9), P(2.2), P(26.8), P(28.4), zh - 0.65, zh - 0.3, "bb_crack")
    B(r, h, P(1.2), P(1.9), P(27.2), P(28.0), zh - 0.8, zh - 0.5, "pupil")
    #   right eye (negative): black, a white burning pupil
    B(r, h, -P(3.2), -P(0.8), P(26.8), P(28.4), zh - 0.45, zh, "pupil")
    B(r, h, -P(2.2), -P(0.9), P(26.8), P(28.4), zh - 0.65, zh - 0.3, "bb_crack_v")
    B(r, h, -P(1.9), -P(1.2), P(27.2), P(28.0), zh - 0.8, zh - 0.5, "bb_dbl_eye_n")
    r.cube(h, (P(0.9), P(28.7), zh - 0.55), (P(2.4), 0.6, 0.4), "bb_dbl_hair", rot=[0, 0, -12], pivot=(P(2), P(29), zh))   # brows, angry
    r.cube(h, (-P(3.3), P(28.7), zh - 0.55), (P(2.4), 0.6, 0.4), "bb_dbl_hair_n", rot=[0, 0, 12], pivot=(-P(2), P(29), zh))
    B(r, h, -P(1), P(1), P(25.8), P(27), zh - 0.4, zh, "bb_dbl_shirt")                 # nose
    B(r, h, -P(1), 0, P(25.8), P(27), zh - 0.42, zh - 0.1, "bb_dbl_shirt_n")
    # mouth: a flat line that cracks into a grin on one side
    B(r, h, -P(2), P(1.4), P(24.9), P(25.5), zh - 0.35, zh, "bb_dbl_void")
    poly2d(r, h, [(P(1.4), P(25.2)), (P(2.4), P(25.9)), (P(3.0), P(26.8))], zh - 0.4, "bb_crack", 0.4)
    # a crack across the face, through the eye
    poly2d(r, h, [(P(3.6), P(31.6)), (P(2.8), P(30.0)), (P(3.2), P(28.6)), (P(2.2), P(26.6)), (P(2.8), P(25.0)), (P(2.2), P(24.2))], zh - 0.5, "bb_crack")
    poly2d(r, h, [(-P(0.3), P(29.2)), (-P(1.2), P(30.6)), (-P(2.6), P(31.4))], zh - 0.5, "bb_crack_v")
    poly2d(r, h, [(-P(3.4), P(26.4)), (-P(2.4), P(25.4)), (-P(3.0), P(24.3))], zh - 0.5, "bb_crack_v")
    # a corner of the head broken away onto void, with a glint at the edge and the piece hovering off
    B(r, h, P(1.8), P(4.15), P(30.3), P(32.5), zh - 0.15, zh + 3.0, "bb_dbl_void")
    B(r, h, P(1.6), P(2.2), P(30.0), P(30.5), zh - 0.3, zh + 0.2, "bb_dbl_silver")
    B(r, h, P(4.0), P(4.3), P(29.8), P(30.4), zh - 0.3, zh + 3.0, "bb_dbl_silver")
    r.cube(h, (P(4.6), P(32.6), zh - 1.4), (2.4, 2.2, 2.2), "bb_dbl_hair", rot=[20, 30, 25], pivot=(P(4.6) + 1.2, P(32.6) + 1.1, zh - 0.3))
    r.cube(h, (P(4.6) + 0.2, P(32.6) - 0.6, zh - 1.6), (2.0, 0.8, 2.0), "bb_dbl_glass", rot=[20, 30, 25], pivot=(P(4.6) + 1.2, P(32.6) + 1.1, zh - 0.3))
    # back of the head: the seam continues
    poly2d(r, h, [(0, P(24.2)), (0.4, P(26)), (-0.3, P(28))], P(4.2) + 0.05, "bb_crack", 0.45)

    # --- arms
    for s, side in ((1, "l"), (-1, "r")):
        gm, sm = ("bb_dbl_glass", "bb_dbl_shirt") if s > 0 else ("bb_dbl_dark", "bb_dbl_shirt_n")
        cm = "bb_crack" if s > 0 else "bb_crack_v"
        x0, x1 = s * P(4), s * P(8)
        a0 = r.bone(f"arm_{side}0", bd, (s * P(6), P(22.5), 0), role=f"arm_{side}0")
        B(r, a0, x0, x1, P(17.5), P(24), -P(2), P(2), gm)
        B(r, a0, x0 - s * 0.1, x1 + s * 0.25, P(19.8), P(24.2), -P(2) - 0.25, P(2) + 0.25, sm)    # sleeve
        B(r, a0, x0 - s * 0.1, x1 + s * 0.3, P(19.5), P(20.1), -P(2) - 0.3, P(2) + 0.3, "bb_dbl_silver" if s > 0 else "bb_dbl_shoe")
        a1 = r.bone(f"arm_{side}1", a0, (s * P(6), P(18), 0), role=f"arm_{side}1")
        B(r, a1, x0 + s * 0.1, x1 - s * 0.1, P(12), P(18.3), -P(2) + 0.1, P(2) - 0.1, gm)
        B(r, a1, x0, x1, P(12), P(13.4), -P(2) - 0.05, P(2) + 0.05, gm)                  # hand
        poly2d(r, a1, [(s * P(6.4), P(17.6)), (s * P(5.6), P(15.6)), (s * P(6.6), P(13.8))], -P(2) - 0.15, cm)
    # shoulder chunk broken off the dark arm
    B(r, "arm_r0", -P(8) - 0.3, -P(6.2), P(22.4), P(24.3), -1.2, 1.6, "bb_dbl_void")
    B(r, "arm_r0", -P(8) - 0.35, -P(7.6), P(22.0), P(22.5), -1.4, 1.8, "bb_dbl_silver")
    # the copied sword in the dark hand: glass blade with a glowing fuller
    sw = r.bone("sword", "arm_r1", (-P(6), P(12.7), 0))
    sx = -P(6)
    yc = P(12.7)
    B(r, sw, sx - 0.9, sx + 0.9, yc - 0.9, yc + 0.9, -P(2) - 0.4, P(2) + 1.6, "bb_dbl_shoe")              # grip
    B(r, sw, sx - 1.2, sx + 1.2, yc - 1.2, yc + 1.2, P(2) + 1.4, P(2) + 2.8, "bb_dbl_silver")             # pommel
    B(r, sw, sx - 0.7, sx + 0.7, yc - 4.0, yc + 4.0, -P(2) - 1.8, -P(2) - 0.4, "bb_dbl_silver")           # crossguard
    B(r, sw, sx - 0.9, sx + 0.9, yc - 4.6, yc - 3.4, -P(2) - 2.0, -P(2) - 0.2, "bb_crack")
    B(r, sw, sx - 0.9, sx + 0.9, yc + 3.4, yc + 4.6, -P(2) - 2.0, -P(2) - 0.2, "bb_crack")
    zt = -P(2) - 1.8
    for i, (hw, ln) in enumerate(((2.0, 7.0), (1.7, 6.0), (1.3, 5.0), (0.8, 3.0))):
        B(r, sw, sx - 0.45, sx + 0.45, yc - hw, yc + hw, zt - ln, zt, "bb_dbl_glass" if i % 2 == 0 else "bb_dbl_dark")
        zt -= ln
    B(r, sw, sx - 0.55, sx + 0.55, yc - 0.3, yc + 0.3, zt + 2.0, -P(2) - 1.8, "bb_crack")               # fuller
    # legs (rooted, the body hangs between them)
    for s, side in ((1, "l"), (-1, "r")):
        pm, gm, shm = ("bb_dbl_pants", "bb_dbl_glass", "bb_dbl_shoe") if s > 0 else ("bb_dbl_pants_n", "bb_dbl_dark", "bb_dbl_shoe_n")
        cm = "bb_crack" if s > 0 else "bb_crack_v"
        l0 = r.bone(f"leg_{side}0", None, (s * P(2), P(12), 0), role=f"leg_{side}0")
        B(r, l0, 0, s * P(4), P(5.6), P(12.2), -P(2), P(2), pm)
        l1 = r.bone(f"leg_{side}1", l0, (s * P(2), P(6), 0), role=f"leg_{side}1")
        B(r, l1, s * 0.1, s * (P(4) - 0.1), 0, P(6.2), -P(2) + 0.1, P(2) - 0.1, pm)
        B(r, l1, -s * 0.05, s * (P(4) + 0.1), 0, P(1.8), -P(2) - 0.5, P(2) + 0.1, shm)             # shoes
        B(r, l1, -s * 0.05, s * (P(4) + 0.1), P(1.8), P(2.2), -P(2) - 0.5, -P(2) + 0.6, "bb_dbl_silver" if s > 0 else "bb_dbl_shoe")
        poly2d(r, l0, [(s * P(1), P(11.6)), (s * P(2.4), P(9.4)), (s * P(1.6), P(7))], -P(2) - 0.15, cm)
    B(r, "leg_r1", -P(3.4), -P(1.2), P(2.6), P(5.2), -P(2) - 0.2, -P(2) + 1.0, "bb_dbl_void")        # shin chipped away
    B(r, "leg_r1", -P(3.6), -P(3.0), P(5.0), P(5.4), -P(2) - 0.3, -P(2) + 1.0, "bb_dbl_shoe_n")

    # --- the broken gilded frame it stepped out of
    fr = r.bone("frame", bd, (0, P(12), P(6)))
    fz0, fz1 = P(5.4), P(5.4) + 2.4
    FX, FY0, FY1 = 15.5, 3.0, 46.0
    B(r, fr, -FX, FX, FY1 - 2.6, FY1, fz0, fz1, "bb_dbl_frame")                       # top rail
    B(r, fr, -FX + 1.4, FX - 1.4, FY1 - 3.4, FY1 - 2.6, fz0 + 0.3, fz1 - 0.3, "bb_dbl_frame_d")
    B(r, fr, FX - 2.6, FX, FY0, FY1, fz0, fz1, "bb_dbl_frame")                        # left post, whole
    B(r, fr, FX - 3.4, FX - 2.6, FY0 + 1.4, FY1 - 1.4, fz0 + 0.3, fz1 - 0.3, "bb_dbl_frame_d")
    B(r, fr, -FX, FX, FY0, FY0 + 2.6, fz0, fz1, "bb_dbl_frame")                       # bottom rail
    B(r, fr, -FX, -FX + 2.6, FY1 - 15, FY1, fz0, fz1, "bb_dbl_frame")                 # right post, snapped
    B(r, fr, -FX, -FX + 2.6, FY0, FY0 + 9, fz0, fz1, "bb_dbl_frame")
    r.cube(fr, (-FX - 0.4, FY0 + 14, fz0 + 0.2), (2.4, 6, 2.0), "bb_dbl_frame", rot=[0, 0, 28], pivot=(-FX + 0.8, FY0 + 17, fz0 + 1))   # the broken piece adrift
    r.cube(fr, (-FX - 2.4, FY0 + 22, fz0 + 0.4), (2.0, 3.2, 1.6), "bb_dbl_frame", rot=[0, 0, -40], pivot=(-FX - 1.4, FY0 + 23.6, fz0 + 1))
    # crest and corner rosettes
    B(r, fr, -4.5, 4.5, FY1, FY1 + 2.0, fz0 + 0.2, fz1 - 0.2, "bb_dbl_frame")
    B(r, fr, -2.5, 2.5, FY1 + 2.0, FY1 + 3.2, fz0 + 0.2, fz1 - 0.2, "bb_dbl_frame")
    B(r, fr, -1.0, 1.0, FY1 - 1.8, FY1 + 1.8, fz0 - 0.4, fz0, "bb_crack")
    for (cx, cy) in ((FX - 1.3, FY1 - 1.3), (-FX + 1.3, FY1 - 1.3), (FX - 1.3, FY0 + 1.3), (-FX + 1.3, FY0 + 1.3)):
        B(r, fr, cx - 1.8, cx + 1.8, cy - 1.8, cy + 1.8, fz0 - 0.5, fz0 + 0.5, "bb_dbl_frame")
    # shards of the mirror still caught in the corners
    for (x, y, w, hh, rz, m) in ((FX - 4.5, FY1 - 6, 3.0, 4.8, 30, "bb_dbl_glass"), (FX - 6.5, FY1 - 4.6, 2.4, 3.0, -20, "bb_dbl_dark"),
                                 (-FX + 4.0, FY1 - 6.4, 2.6, 5.0, -35, "bb_dbl_dark")):
        r.cube(fr, (x - w / 2, y - hh / 2, fz0 + 0.8), (w, hh, 0.6), m, rot=[0, 0, rz], pivot=(x, y, fz0 + 1))
        r.cube(fr, (x - 0.2, y - hh / 2 + 0.4, fz0 + 0.6), (0.4, hh * 0.7, 0.3), "bb_crack", rot=[0, 0, rz], pivot=(x, y, fz0 + 1))

    # --- glass copies of your gear circling it (pickaxe, axe, bow, shield), points turned downward
    def pick(o, x, y, z):
        B(r, o, x - 0.4, x + 0.4, y - 5, y + 3, z - 0.4, z + 0.4, "bb_dbl_frame_d")
        B(r, o, x - 3.4, x + 3.4, y + 2.4, y + 3.4, z - 0.5, z + 0.5, "bb_dbl_glass")
        B(r, o, x - 3.6, x - 2.6, y + 1.0, y + 2.6, z - 0.5, z + 0.5, "bb_dbl_glass")
        B(r, o, x + 2.6, x + 3.6, y + 1.0, y + 2.6, z - 0.5, z + 0.5, "bb_dbl_glass")
        B(r, o, x - 3.0, x + 3.0, y + 2.7, y + 3.1, z - 0.65, z - 0.45, "bb_crack")

    def axe(o, x, y, z):
        B(r, o, x - 0.4, x + 0.4, y - 4, y + 4, z - 0.4, z + 0.4, "bb_dbl_frame_d")
        B(r, o, x + 0.3, x + 3.2, y + 0.6, y + 3.8, z - 0.5, z + 0.5, "bb_dbl_dark")
        B(r, o, x + 3.0, x + 3.5, y + 0.2, y + 4.2, z - 0.55, z + 0.55, "bb_crack_v")

    def bow(o, x, y, z):
        for (dy, dx) in ((-4, 0.0), (-2.6, -1.2), (2.6, -1.2), (4, 0.0)):
            B(r, o, x + dx - 0.4, x + dx + 0.4, y + dy - 0.8, y + dy + 0.8, z - 0.4, z + 0.4, "bb_dbl_glass")
        B(r, o, x - 2.2, x - 1.4, y - 1.8, y + 1.8, z - 0.4, z + 0.4, "bb_dbl_glass")
        B(r, o, x + 0.25, x + 0.5, y - 4.4, y + 4.4, z - 0.15, z + 0.15, "bb_crack")

    def shield(o, x, y, z):
        B(r, o, x - 2.6, x + 2.6, y - 3.4, y + 3.4, z - 0.4, z + 0.4, "bb_dbl_dark")
        B(r, o, x - 2.9, x + 2.9, y - 3.7, y - 3.1, z - 0.5, z + 0.5, "bb_dbl_silver")
        B(r, o, x - 2.9, x + 2.9, y + 3.1, y + 3.7, z - 0.5, z + 0.5, "bb_dbl_silver")
        B(r, o, x - 0.4, x + 0.4, y - 3.0, y + 3.0, z - 0.6, z + 0.6, "bb_crack_v")
    for i, (fn, ang, y) in enumerate(((pick, 20, 34), (axe, 110, 22), (bow, 200, 30), (shield, 290, 18))):
        o = r.bone(f"copy{i}", bd, (0, y, 0), role="orbit")
        a = math.radians(ang)
        fn(o, math.cos(a) * 19, y, math.sin(a) * 19)
    # loose shards drifting up around its feet
    o = r.bone("shards", bd, (0, 10, 0), role="orbit")
    for (x, y, z, rz, m) in ((11, 6, -6, 30, "bb_dbl_glass"), (-12, 9, 4, -40, "bb_dbl_dark")):
        r.cube(o, (x - 0.7, y - 1.6, z - 0.3), (1.4, 3.2, 0.6), m, rot=[15, 25, rz], pivot=(x, y, z))
        r.cube(o, (x - 0.2, y - 1.0, z - 0.45), (0.4, 2.0, 0.3), "bb_crack", rot=[15, 25, rz], pivot=(x, y, z))
    return r


# =====================================================================================================================
# World 7 - Pressure Leviathan
# =====================================================================================================================
M("bb_lev_scale", "1a4a66", "2a88a2", "scales")
M("bb_lev_scale_d", "102c40", "1c5a74", "scales")
M("bb_lev_belly", "2c7a88", "86dce4", "scales")
M("bb_lev_hull", "2c3848", "5a6e88", "metal")        # pressure-hull armour: riveted plates
M("bb_lev_hull_d", "1c2430", "3a4a5e", "metal")
M("bb_lev_rivet", "8a9cb2", "c8d8ea", "metal")
M("bb_lev_photo", "4af4ff", "a8fbff", "glow", True)  # photophores
M("bb_lev_photo2", "e04ae8", "f4a0ff", "glow", True)
M("bb_lev_eye", "e4ff3a", "f4ffa0", "glow", True)
M("bb_lev_fin", "16465e", "3aa0bc", "membrane")
M("bb_lev_gum", "5a1220", "a83a4a", "flesh")
M("bb_lev_barnacle", "8a8a7a", "c0c0aa", "blocks")


def _rivets(r, bone, x0, x1, y, z0, z1, n):
    """n rivets along a plate edge, on top of it at height y."""
    for i in range(n):
        z = z0 + (z1 - z0) * (i + 0.5) / n
        B(r, bone, x0, x1, y, y + 0.5, z - 0.35, z + 0.35, "bb_lev_rivet")


def pressure_leviathan():
    """A deep-sea leviathan grown under a crushing ocean: a long serpent body in black-teal scales, its back and skull
    sheathed in riveted pressure-hull plates like a bathyscaphe, barnacles crusted on the oldest plates. Its huge maw
    hangs open on a cage of needle fangs over a glowing throat; three pairs of acid eyes, gill slits burning cyan,
    glowing barbels and an angler's lure dangling before its mouth. Photophores run along the flanks to a crescent
    tail; armoured, swept-back pectoral fins carry glowing rays."""
    r = Rig("pressure_leviathan")
    cy = 11.0
    r.bone("body", None, (0, cy, -10), role="body")
    bd = "body"
    octo(r, bd, 0, -8, cy - 8.5, cy + 8.5, 19, 14, 3, "bb_lev_scale")
    B(r, bd, -6.5, 6.5, cy - 9.1, cy - 6, -14, -2, "bb_lev_belly")
    B(r, bd, -7.5, 7.5, cy + 7.5, cy + 9.4, -14.5, -1.5, "bb_lev_hull")              # collar plate
    _rivets(r, bd, -7.2, -6.4, cy + 9.4, -14, -2, 3)
    _rivets(r, bd, 6.4, 7.2, cy + 9.4, -14, -2, 3)
    # --- head: a great skull wider than the body, its maw hanging open
    h = r.bone("head", bd, (0, cy, -14), role="head")
    octo(r, h, 0, -25, 10.0, 19.5, 23, 24, 3.5, "bb_lev_scale")                      # cranium and upper jaw
    octo(r, h, 0, -38.5, 10.4, 17.0, 16, 5, 2, "bb_lev_scale_d")                     # snout
    for s_ in (1, -1):                                                              # gill covers flaring out
        B(r, h, s_ * 11.0, s_ * 13.6, 9.0, 18.0, -19.5, -13.5, "bb_lev_hull")
        B(r, h, s_ * 13.2, s_ * 15.2, 11.0, 17.0, -17.5, -13.0, "bb_lev_hull_d")
    B(r, h, -9.5, 9.5, 19.5, 21.0, -34, -14, "bb_lev_hull")                           # skull plate
    B(r, h, -7, 7, 17.0, 18.6, -41, -35, "bb_lev_hull")                               # snout plate
    _rivets(r, h, -9.2, -8.4, 21.0, -33, -15, 3)
    _rivets(r, h, 8.4, 9.2, 21.0, -33, -15, 3)
    for (z, hh) in ((-29, 2.4), (-23, 3.6), (-17, 2.8)):                              # crest of spines, tipped with light
        B(r, h, -0.9, 0.9, 21.0, 21.0 + hh, z - 1.8, z + 1.8, "bb_lev_hull_d")
        B(r, h, -0.5, 0.5, 20.8 + hh, 21.6 + hh, z - 0.7, z + 0.7, "bb_lev_photo2")
    B(r, h, 6.7, 8.5, 21.0, 22.4, -26.9, -25.1, "bb_lev_barnacle")
    for s_ in (1, -1):
        B(r, h, s_ * 7.5, s_ * 11.9, 15.6, 18.8, -35.5, -21, "bb_lev_hull")               # brow armour over the eyes
        # eyes: one great eye and two smaller ones each side, bulging so they show from the front
        for k, (z, y, e) in enumerate(((-34.0, 14.0, 3.6), (-28.0, 14.8, 2.4), (-23.6, 15.4, 1.7))):
            xo = s_ * 11.5
            if k == 0:   # the great eye sits in the bevelled corner of the skull, staring forward and sideways
                B(r, h, s_ * 7.0, s_ * 11.6, 11.8, 16.8, -37.2, -33.0, "bb_lev_hull_d")
                B(r, h, s_ * 7.6, s_ * 11.2, 12.4, 16.2, -37.7, -33.6, "bb_lev_eye")
                B(r, h, s_ * 9.0, s_ * 9.8, 12.8, 15.8, -37.95, -37.5, "pupil")
                B(r, h, s_ * 11.0, s_ * 11.4, 12.8, 15.8, -36.0, -35.2, "pupil")
                B(r, h, s_ * 7.2, s_ * 11.8, 16.4, 17.4, -38.0, -33.0, "bb_lev_hull")       # heavy lid
                continue
            B(r, h, xo - s_ * 2.0, xo + s_ * 0.6, y - e / 2, y + e / 2, z - e / 2, z + e / 2, "bb_lev_eye")
            B(r, h, xo + s_ * 0.5, xo + s_ * 0.8, y - e / 2 + 0.2, y + e / 2 - 0.2, z - 0.3, z + 0.3, "pupil")      # slit
        segside(r, h, (-29.6, 16.4), (-22, 13.0), s_ * 11.5 - (0.3 if s_ < 0 else 0), "bb_lev_photo", 0.4)
        segside(r, h, (-22, 13.0), (-14.5, 14.2), s_ * 11.5 - (0.3 if s_ < 0 else 0), "bb_lev_photo", 0.4)
        for i, z in enumerate((-18.6, -16.6, -14.6)):                                # gill slits under the covers
            B(r, h, s_ * 13.6 - 0.3, s_ * 13.6 + 0.3, 10.0, 16.0 - i * 0.8, z - 0.4, z + 0.4, "bb_lev_photo")
    # the open maw: throat, gums and a cage of needle fangs
    B(r, h, -8.5, 8.5, 4.0, 10.6, -28, -14, "maw")
    B(r, h, -4.5, 4.5, 4.6, 9.8, -28.6, -27.6, "bb_lev_photo")                       # the light deep in the throat
    B(r, h, -2.0, 2.0, 6.0, 9.8, -29.2, -28.4, "lure")
    B(r, h, -9.5, 9.5, 9.4, 10.2, -41, -15, "bb_lev_gum")
    for i, x in enumerate((-6.6, -3.2, -0.45, 2.3, 5.7)):
        ln = (3.4, 4.2, 2.0, 4.2, 3.4)[i]
        B(r, h, x, x + 0.9, 9.6 - ln, 9.6, -40.8, -39.9, "tooth")
    for s_ in (1, -1):
        for j, z in enumerate((-36.5, -32, -27.5, -23)):
            ln = (3.2, 2.4, 2.8, 1.8)[j]
            B(r, h, s_ * 9.0 - 0.45, s_ * 9.0 + 0.45, 9.6 - ln, 9.6, z - 0.45, z + 0.45, "tooth")
    # --- lower jaw, hinged at the back
    jw = r.bone("jaw", h, (0, 5.5, -15), role="jaw")
    octo(r, jw, 0, -29.0, 0.6, 4.6, 19, 27, 3, "bb_lev_scale_d")                      # an underbite, jutting past the snout
    B(r, jw, -8, 8, 4.2, 4.9, -41.5, -17, "bb_lev_gum")                               # gums and tongue
    B(r, jw, -3, 3, 4.6, 5.4, -36, -18, "maw")
    B(r, jw, -6.5, 6.5, 0.0, 1.2, -41.5, -18, "bb_lev_hull")                          # chin plate
    for i, x in enumerate((-5.6, -1.9, 1.0, 4.7)):
        ln = (3.4, 4.6, 4.6, 3.4)[i]
        B(r, jw, x, x + 0.9, 4.8, 4.8 + ln, -42.2, -41.3, "tooth")
    for s_ in (1, -1):
        for j, z in enumerate((-34, -29.5, -25)):
            ln = (3.0, 2.4, 2.0)[j]
            B(r, jw, s_ * 8.4 - 0.45, s_ * 8.4 + 0.45, 4.8, 4.8 + ln, z - 0.45, z + 0.45, "tooth")
        bx = s_ * 7.5                                                               # glowing barbels at the chin corners
        B(r, jw, bx - 0.35, bx + 0.35, 0.0, 1.6, -40.0, -39.3, "bb_lev_fin")
        B(r, jw, bx - 0.6, bx + 0.6, 0.0, 1.0, -41.2, -40.0, "bb_lev_photo")
    # --- the lure: a stalk from the brow that dangles a light before its mouth
    l0 = r.bone("lure0", h, (0, 18.5, -37), role="tail")
    B(r, l0, -0.6, 0.6, 18.0, 23.5, -37.6, -36.4, "bb_lev_hull_d")
    l1 = r.bone("lure1", l0, (0, 23, -37), role="tail")
    B(r, l1, -0.5, 0.5, 22.6, 23.6, -45, -36.8, "bb_lev_scale_d")
    l2 = r.bone("lure2", l1, (0, 23, -44.5), role="tail")
    B(r, l2, -0.4, 0.4, 18.5, 23.4, -44.9, -44.1, "bb_lev_fin")
    B(r, l2, -1.9, 1.9, 15.0, 18.8, -46.4, -42.6, "lure")
    B(r, l2, -1.3, 1.3, 14.4, 19.4, -45.8, -43.2, "lure")
    # --- the serpent body: a chain of segments, each plated, lit and finned
    par = bd
    widths = (17, 15, 12.6, 10.2, 8, 6)
    z0 = -3.0
    for i, w in enumerate(widths):
        hgt = w * 0.92
        nm = r.bone(f"seg{i}", par, (0, cy, z0), role="seg")
        ln = 10.0
        sy0, sy1 = cy - hgt / 2, cy + hgt / 2
        mat_ = "bb_lev_scale" if i % 2 == 0 else "bb_lev_scale_d"
        if i < 4:
            octo(r, nm, 0, z0 + ln / 2, sy0, sy1, w, ln, max(1.2, w * 0.16), mat_)
        else:
            B(r, nm, -w / 2, w / 2, sy0, sy1, z0, z0 + ln, mat_)
        B(r, nm, -w * 0.32, w * 0.32, sy0 - 0.5, sy0 + 1.5, z0 + 0.6, z0 + ln - 0.6, "bb_lev_belly")      # belly plate
        B(r, nm, -w * 0.4, w * 0.4, sy1 - 1.0, sy1 + 0.9, z0 + 0.4, z0 + ln - 1.4, "bb_lev_hull")          # hull plate
        sh = 4.2 - i * 0.45                                                         # dorsal spine and fin membrane
        B(r, nm, -0.7, 0.7, sy1 + 0.6, sy1 + 0.6 + sh, z0 + 1.0, z0 + 3.4, "bb_lev_hull_d")
        B(r, nm, -0.4, 0.4, sy1 + 0.4 + sh, sy1 + 1.2 + sh, z0 + 1.6, z0 + 2.8, "bb_lev_photo2" if i % 2 == 0 else "bb_lev_photo")
        B(r, nm, -0.25, 0.25, sy1 + 0.6, sy1 + 0.4 + sh * 0.6, z0 + 3.4, z0 + ln - 0.5, "bb_lev_fin")
        for s_ in ((1, -1) if i < 4 else ()):                                      # a photophore each side
            zz = z0 + 3.5 + (i % 2) * 3
            yy = cy - hgt * 0.12
            B(r, nm, s_ * w / 2 - 0.3, s_ * w / 2 + 0.3, yy - 0.55, yy + 0.55, zz - 0.8, zz + 0.8, "bb_lev_photo")
        if i in (0, 3):
            for s_, side in ((1, "l"), (-1, "r")):
                fl = 15 if i == 0 else 8
                f = r.bone(f"fin_{side}{i}", nm, (s_ * w / 2, cy - 2, z0 + 2), role=f"wing_{side}")
                xa = s_ * (w / 2 - 0.5)
                for k, (span, za, zb) in enumerate(((1.0, 0.5, 4.0), (0.8, 3.5, 7.5), (0.55, 7.0, 11.0))):   # swept back
                    B(r, f, xa, s_ * (w / 2 + fl * span), cy - 2.4, cy - 1.6, z0 + za + k * 0.0, z0 + zb, "bb_lev_fin")
                B(r, f, xa, s_ * (w / 2 + fl * 1.05), cy - 2.7, cy - 1.3, z0 + 0.2, z0 + 1.4, "bb_lev_hull")   # leading armour ray
                if i == 0:
                    B(r, f, xa, s_ * (w / 2 + fl * 0.8), cy - 1.7, cy - 1.3, z0 + 4.8, z0 + 5.3, "bb_lev_photo")
                    B(r, f, xa, s_ * (w / 2 + fl * 0.5), cy - 1.7, cy - 1.3, z0 + 8.4, z0 + 8.9, "bb_lev_photo")
                    B(r, f, s_ * (w / 2 + fl * 0.85), s_ * (w / 2 + fl * 1.1), cy - 2.9, cy - 1.1, z0 + 0.0, z0 + 1.6, "bb_lev_photo2")
        par = nm
        z0 += 8.5
    # crescent tail
    t = r.bone("fluke", par, (0, cy, z0 + 1.5), role="tail")
    B(r, t, -0.9, 0.9, cy - 2.5, cy + 2.5, z0 + 1, z0 + 5, "bb_lev_scale_d")
    for (y0, y1, za, zb) in ((cy + 1.5, cy + 6.5, z0 + 3, z0 + 7), (cy + 5.5, cy + 11.5, z0 + 5.5, z0 + 10), (cy - 6.5, cy - 1.5, z0 + 3, z0 + 7), (cy - 10.5, cy - 5.5, z0 + 5.5, z0 + 10)):
        B(r, t, -0.5, 0.5, y0, y1, za, zb, "bb_lev_fin")
    B(r, t, -0.7, 0.7, cy + 10.5, cy + 12.8, z0 + 8.5, z0 + 10.6, "bb_lev_photo")
    return r


# =====================================================================================================================
# World 8 - Master of Seasons
# =====================================================================================================================
M("bb_sm_bark", "5e3e26", "7e5a36", "bark")
M("bb_sm_bark_d", "3a2618", "573a24", "bark")
M("bb_sm_face", "8a6844", "a8845a", "skin")
M("bb_sm_knot", "4a3020", "6a4a30", "skin")
M("bb_sm_spring", "5ab84a", "a8e870", "leaf")
M("bb_sm_blossom", "f08ab8", "ffd0e4", "leaf")
M("bb_sm_summer", "2e7a2a", "5aa83a", "leaf")
M("bb_sm_sun", "ffc23a", "ffe890", "glow", True)
M("bb_sm_autumn", "d8642a", "f0a83a", "leaf")
M("bb_sm_autumn_d", "a8381e", "d8642a", "leaf")
M("bb_sm_snow", "eaf2fa", "ffffff", "cloud")
M("bb_sm_ice", "9ae0fa", "d8f6ff", "glow", True)
M("bb_sm_dial", "efe4c4", "fff6e0", "skin")
M("bb_sm_q_spring", "8ad86a", "b8f09a", "skin")
M("bb_sm_q_summer", "f4cc4a", "ffe48a", "skin")
M("bb_sm_q_autumn", "e07a3a", "f0a060", "skin")
M("bb_sm_q_winter", "a8d8f0", "d8f0ff", "skin")
M("bb_sm_eye", "a8ff2a", "d8ff6a", "glow", True)
M("bb_sm_time", "ffe8a0", "fff8e0", "glow", True)     # the glow of time: sand, the clock's heart
M("bb_sm_gold", "c8963a", "f0cc70", "metal")
M("bb_sm_glass", "d8f0f4", "ffffff", "crystal")


def _ring(r, bone, cx, cy, z, radius, n, m, th=0.8, dz=0.6):
    """A ring standing in the XY plane, out of n rotated bars."""
    seg = 2 * math.pi * radius / n * 1.08
    for k in range(n):
        a = 2 * math.pi * k / n
        x, y = cx + math.cos(a) * radius, cy + math.sin(a) * radius
        r.cube(bone, (x - seg / 2, y - th / 2, z), (seg, th, dz), m, rot=[0, 0, round(math.degrees(a) + 90, 2)], pivot=(x, y, z))


def seasons_master():
    """An ancient tree-sage who keeps the turning of the year: bark body, moss mantle, and a great clock on its chest
    whose dial is split into the four seasons. Everything on it goes round the year: a spring antler in leaf and
    blossom and a winter antler under snow and icicles, a summer sunflower on one shoulder and a heap of autumn
    leaves on the other, a cloak that greens at the collar and freezes at the hem, a beard of roots whose tips have
    gone white. Behind its head turns a clock-ring halo; it leans on a staff crowned with an hourglass of glowing
    sand, and the four seasons circle it as a blossom, a sun, a maple leaf and a snowflake."""
    r = Rig("seasons_master")
    # --- legs: trunks rooted in the ground
    for s, side in ((1, "l"), (-1, "r")):
        x = s * 5.5
        l0 = r.bone(f"leg_{side}0", None, (x, 24, 0), role=f"leg_{side}0")
        B(r, l0, x - 3.6, x + 3.6, 12, 24.5, -3.6, 3.6, "bb_sm_bark")
        B(r, l0, x - 4.1, x + 4.1, 11.2, 14.2, -4.1, 4.1, "bb_sm_bark_d")                # knee knot
        l1 = r.bone(f"leg_{side}1", l0, (x, 12.5, 0), role=f"leg_{side}1")
        B(r, l1, x - 3.2, x + 3.2, 1.5, 12.8, -3.2, 3.2, "bb_sm_bark")
        B(r, l1, x - 4.2, x + 4.2, 0, 2.2, -5.2, 4.2, "bb_sm_bark_d")                    # root foot
        for (dx, dz, w, ln) in ((-2.8, -7.8, 1.8, 2.8), (0.6, -8.6, 2.0, 3.4)):
            B(r, l1, x + dx, x + dx + w, 0, 1.2, dz, dz + ln, "bb_sm_bark_d")            # roots creeping out
        B(r, l1, x - 2.4, x + 1.8, 2.0, 3.0, -3.6, -1.4, "moss")
    # --- body
    r.bone("body", None, (0, 24, 0), role="body")
    bd = "body"
    B(r, bd, -8.6, 8.6, 20.5, 27, -5.2, 5.2, "bb_sm_bark_d")                             # pelvis
    for i, m in enumerate(("bb_sm_q_winter", "bb_sm_autumn", "bb_sm_summer", "bb_sm_spring")):   # leaf tassets, the year left to right
        x0 = -8.8 + i * 4.4
        B(r, bd, x0, x0 + 4.2, 16.5 + (i % 2) * 1.2, 25, -5.9, -4.9, m if i else "bb_sm_snow")
    octo(r, bd, 0, 0, 26, 40, 18, 10, 1.6, "bb_sm_bark")                                 # trunk
    octo(r, bd, 0, 0, 39, 47, 21, 11, 2, "bb_sm_bark")                                   # chest
    B(r, bd, -9.2, 9.2, 25.6, 27.6, -5.6, 5.6, "stem")                                   # vine belt
    B(r, bd, -11, 11, 45.5, 49, -6, 6, "moss")                                           # moss mantle
    B(r, bd, -8, 8, 48.5, 50, -4.6, 5.0, "moss")
    # --- the clock of the seasons
    cz = -5.6
    cxy = (0, 33.6)
    octo_front = [(-6.8, 6.8, cxy[1] - 5.2, cxy[1] + 5.2), (-5.2, 5.2, cxy[1] - 6.8, cxy[1] + 6.8)]
    for (xa, xb, ya, yb) in octo_front:
        B(r, bd, xa, xb, ya, yb, cz - 0.4, cz + 0.6, "bb_sm_gold")
    for (sx, sy, m) in ((1, 1, "bb_sm_q_spring"), (1, -1, "bb_sm_q_summer"), (-1, -1, "bb_sm_q_autumn"), (-1, 1, "bb_sm_q_winter")):
        B(r, bd, 0, sx * 5.6, cxy[1], cxy[1] + sy * 5.6, cz - 0.7, cz - 0.3, m)
    for (x, y, w, hh) in ((-0.5, cxy[1] + 4.4, 1.0, 1.6), (-0.5, cxy[1] - 6.0, 1.0, 1.6), (4.4, cxy[1] - 0.5, 1.6, 1.0), (-6.0, cxy[1] - 0.5, 1.6, 1.0)):
        B(r, bd, x, x + w, y, y + hh, cz - 0.95, cz - 0.6, "bb_sm_gold")                  # XII, III, VI, IX
    clk = r.bone("clock", bd, (0, cxy[1], cz - 1), role="pulse")
    r.cube(clk, (-0.4, cxy[1] - 0.4, cz - 1.3), (0.8, 5.2, 0.4), "pupil", rot=[0, 0, -35], pivot=(0, cxy[1], cz - 1.1))      # minute hand
    r.cube(clk, (-0.45, cxy[1] - 0.45, cz - 1.25), (0.9, 3.6, 0.4), "pupil", rot=[0, 0, 110], pivot=(0, cxy[1], cz - 1.1))   # hour hand
    B(r, clk, -1.2, 1.2, cxy[1] - 1.2, cxy[1] + 1.2, cz - 1.6, cz - 0.6, "bb_sm_time")
    # --- head: a carved, weathered face under a mossy brow
    h = r.bone("head", bd, (0, 48, 0), role="head")
    B(r, h, -6.6, 6.6, 47, 60, -6.6, 5.6, "bb_sm_face")
    B(r, h, -7.0, 7.0, 58, 60.6, -7.0, 6.0, "bb_sm_bark_d")                             # crown of bark
    B(r, h, -7.2, 7.2, 55.2, 57.4, -7.8, -6.0, "moss")                                  # heavy mossy brow
    B(r, h, -3.0, 3.0, 57.2, 58.4, -7.4, -6.2, "bb_sm_spring")
    r.cube(h, (-1.3, 56.0, -8.6), (2.6, 2.6, 1.0), "bb_sm_time", rot=[0, 0, 45], pivot=(0, 57.3, -8.1))   # a gem of time on the brow
    for s in (1, -1):
        B(r, h, s * 1.2, s * 5.0, 52.2, 55.4, -7.0, -6.4, "ink")                          # deep sockets
        B(r, h, s * 1.6, s * 4.6, 53.0, 54.6, -7.3, -6.8, "bb_sm_eye")
        B(r, h, s * 2.6, s * 3.4, 53.0, 54.6, -7.5, -7.2, "pupil")
        B(r, h, s * 5.0, s * 7.0, 49.6, 52.0, -7.0, -6.0, "bb_sm_knot")                  # cheek knots
    B(r, h, -1.1, 1.1, 49.6, 55.4, -8.0, -6.4, "bb_sm_bark")                            # long nose ridge
    B(r, h, -1.5, 1.5, 49.0, 50.6, -8.4, -6.8, "bb_sm_knot")
    B(r, h, -4.6, 4.6, 47.6, 49.4, -7.6, -6.4, "moss")                                  # moustache
    # a beard of moss and leaves that goes round the year: green at the chin, autumn below, snow at the tip
    for (x0, x1, y0, y1, z0, m) in ((-5.0, 5.0, 44.8, 48.2, -7.8, "bb_sm_summer"), (-4.0, 4.0, 42.6, 45.2, -7.4, "bb_sm_autumn"),
                                     (-2.6, 2.6, 40.8, 43.0, -7.0, "bb_sm_snow"), (-1.2, 1.2, 39.6, 41.0, -6.8, "bb_sm_ice")):
        B(r, h, x0, x1, y0, y1, z0, z0 + 2.6, m)
    for s in (1, -1):
        B(r, h, s * 4.4, s * 6.4, 43.6, 49.0, -7.2, -5.0, "bb_sm_summer")                 # side braids
        B(r, h, s * 4.7, s * 6.1, 42.0, 43.8, -7.0, -5.2, "bb_sm_autumn_d")
    # antlers spreading into a crown: spring on one side, winter on the other
    for s in (1, -1):
        for (xa, xb, ya, yb) in ((4.0, 6.4, 59.5, 65.0), (5.0, 12.6, 63.6, 65.6), (11.0, 13.2, 64.0, 72.0), (7.6, 9.4, 64.8, 69.6),
                                 (12.6, 16.6, 67.6, 69.2), (15.0, 16.8, 68.0, 73.0)):
            B(r, h, s * xa, s * xb, ya, yb, -1.1, 1.1, "bb_sm_bark_d")
        if s > 0:
            for (x, y, z, w, m) in ((12.1, 72.4, -0.6, 3.2, "bb_sm_spring"), (8.5, 70.2, 0.4, 2.6, "bb_sm_spring"), (16.0, 73.2, 0.0, 2.6, "bb_sm_spring"),
                                    (14.4, 70.6, -1.6, 1.6, "bb_sm_blossom"), (10.2, 73.6, 1.2, 1.4, "bb_sm_blossom"), (6.0, 66.6, -1.6, 1.6, "bb_sm_blossom")):
                B(r, h, x - w / 2, x + w / 2, y - w / 2, y + w / 2, z - w / 2, z + w / 2, m)
        else:
            for (xa, xb, y) in ((-13.6, -10.6, 72.0), (-9.8, -7.2, 69.6), (-17.2, -14.6, 73.0), (-12.0, -6.0, 65.6)):
                B(r, h, xa, xb, y, y + 0.9, -1.4, 1.4, "bb_sm_snow")                     # snow on every branch
            for (x, y, ln) in ((-6.8, 63.6, 2.2), (-10.0, 63.6, 1.6), (-14.0, 67.6, 2.0), (-16.0, 67.6, 1.2)):
                B(r, h, x - 0.4, x + 0.4, y - ln, y, -0.4, 0.4, "bb_sm_ice")              # icicles
    # clock-ring halo turning behind the head
    hl = r.bone("halo", h, (0, 56, 7.5), role="orbit")
    _ring(r, hl, 0, 56, 7.2, 11, 12, "bb_sm_gold", 0.9, 0.7)
    for k in range(4):
        a = math.pi / 2 * k
        x, y = math.cos(a) * 11, 56 + math.sin(a) * 11
        B(r, hl, x - 1.1, x + 1.1, y - 1.1, y + 1.1, 6.8, 8.2, ("bb_sm_q_spring", "bb_sm_q_winter", "bb_sm_q_autumn", "bb_sm_sun")[k])
    # --- arms
    for s, side in ((1, "l"), (-1, "r")):
        x = s * 12.2
        a0 = r.bone(f"arm_{side}0", bd, (x, 45, 0), role=f"arm_{side}0")
        B(r, a0, x - 3.0, x + 3.0, 33.5, 46.5, -3.0, 3.0, "bb_sm_bark")
        a1 = r.bone(f"arm_{side}1", a0, (x, 34, 0), role=f"arm_{side}1")
        B(r, a1, x - 3.4, x + 3.4, 31.8, 35.0, -3.4, 3.4, "bb_sm_bark_d")              # elbow knot
        B(r, a1, x - 2.6, x + 2.6, 22.5, 34.2, -2.6, 2.6, "bb_sm_bark")
        B(r, a1, x - 2.9, x + 2.9, 26.0, 27.2, -2.9, 2.9, "stem")                         # vine wrapped round the wrist
        B(r, a1, x - 3.2, x + 3.2, 19.0, 23.0, -3.2, 3.2, "bb_sm_bark_d")              # hand
        for dz in (-2.4, -0.4, 1.6):
            B(r, a1, x - s * 0.6 - 0.5, x - s * 0.6 + 0.5, 16.4, 19.2, dz, dz + 0.9, "bb_sm_bark_d")   # twig fingers
    #   summer shoulder: a sunflower; autumn shoulder: a heap of leaves and a mushroom
    a0 = "arm_l0"
    B(r, a0, 8.6, 15.8, 44.5, 48.2, -3.6, 3.6, "bb_sm_summer")
    B(r, a0, 9.4, 15.4, 44.2, 50.2, -4.8, -3.6, "bb_sm_sun")                            # a sunflower facing forward
    B(r, a0, 10.9, 13.9, 45.7, 48.7, -5.3, -4.6, "bb_sm_bark_d")
    for (x, y) in ((12.4, 51.0), (12.4, 43.4), (8.6, 47.2), (16.2, 47.2)):
        B(r, a0, x - 1.0, x + 1.0, y - 1.0, y + 1.0, -4.6, -3.8, "bb_sm_q_summer")
    a0 = "arm_r0"
    B(r, a0, -15.8, -8.6, 44.5, 48.0, -3.6, 3.6, "bb_sm_autumn_d")
    B(r, a0, -14.8, -9.6, 47.6, 49.4, -2.8, 3.0, "bb_sm_autumn")
    r.cube(a0, (-15.0, 45.0, -4.4), (3.6, 3.6, 0.8), "bb_sm_autumn", rot=[0, 0, 45], pivot=(-13.2, 46.8, -4))
    r.cube(a0, (-11.6, 46.6, -4.6), (2.6, 2.6, 0.8), "bb_sm_q_summer", rot=[0, 0, 30], pivot=(-10.3, 47.9, -4.2))
    # --- the hourglass staff in the spring hand
    st = r.bone("staff", "arm_l1", (12.2, 21, -1.5))
    B(r, st, 11.4, 13.0, 1.0, 63.0, -2.4, -0.8, "bb_sm_bark_d")
    B(r, st, 11.1, 13.3, 40.0, 42.0, -2.7, -0.5, "stem")
    B(r, st, 13.0, 14.6, 40.6, 42.0, -2.4, -1.0, "bb_sm_spring")
    for yy in (62.4, 71.6):
        B(r, st, 9.4, 15.0, yy, yy + 1.4, -4.4, 1.2, "bb_sm_gold")                       # hourglass caps
    for (dx, dz) in ((9.6, -4.2), (14.2, -4.2), (9.6, 0.4), (14.2, 0.4)):
        B(r, st, dx, dx + 0.6, 63.6, 71.8, dz, dz + 0.6, "bb_sm_gold")                    # posts
    B(r, st, 10.6, 13.8, 63.8, 67.0, -3.2, 0.0, "bb_sm_glass")                          # lower bulb
    B(r, st, 11.0, 13.4, 63.8, 65.6, -2.8, -0.4, "bb_sm_time")                          # sand piling up
    B(r, st, 11.6, 12.8, 66.8, 68.4, -2.2, -1.0, "bb_sm_time")                          # neck, a thread of falling sand
    B(r, st, 10.6, 13.8, 68.2, 71.6, -3.2, 0.0, "bb_sm_glass")                          # upper bulb
    B(r, st, 11.2, 13.2, 68.2, 69.2, -2.6, -0.6, "bb_sm_time")
    B(r, st, 11.8, 12.6, 73.0, 74.6, -2.0, -1.2, "bb_sm_blossom")                       # a bud on top
    # a leaf whirling over the winter palm
    B(r, "arm_r1", -13.6, -10.8, 14.0, 15.0, -3.4, -0.6, "bb_sm_ice")
    # --- cloak: green at the collar, autumn in the middle, frozen at the hem
    c0 = r.bone("cape0", bd, (0, 47, 5.4), role="cape")
    B(r, c0, -9.5, 9.5, 31, 47.5, 5.0, 6.6, "bb_sm_summer")
    B(r, c0, -9.8, 9.8, 42, 47.8, 5.4, 7.0, "bb_sm_spring")
    c1 = r.bone("cape1", c0, (0, 31.5, 5.8), role="cape")
    B(r, c1, -10.2, 10.2, 15.5, 32, 5.4, 7.0, "bb_sm_autumn")
    c2 = r.bone("cape2", c1, (0, 16, 6.2), role="cape")
    B(r, c2, -10.8, 10.8, 5.0, 16.5, 5.8, 7.4, "bb_sm_snow")
    for x in (-8.4, -3.0, 2.6, 8.0):
        B(r, c2, x - 0.4, x + 0.4, 2.4 + abs(x) * 0.12, 5.2, 6.4, 7.0, "bb_sm_ice")       # icicles on the hem
    # --- the wheel of the year: blossom, sun, maple leaf and snowflake circling it
    w = r.bone("year", bd, (0, 40, 0), role="orbit")
    R = 26
    x, z, y = R, 0, 40                                       # spring blossom
    B(r, w, x - 1, x + 1, y - 1, y + 1, z - 1, z + 1, "bb_sm_sun")
    for (dx, dy) in ((0, 1.8), (0, -1.8), (1.8, 0), (-1.8, 0)):
        B(r, w, x + dx - 1.1, x + dx + 1.1, y + dy - 1.1, y + dy + 1.1, z - 0.6, z + 0.6, "bb_sm_blossom")
    x, z, y = 0, -R, 43                                      # summer sun
    B(r, w, x - 1.8, x + 1.8, y - 1.8, y + 1.8, z - 1.8, z + 1.8, "bb_sm_sun")
    for k in range(4):
        r.cube(w, (x - 0.5, y + 2.0, z - 0.5), (1.0, 1.6, 1.0), "bb_sm_q_summer", rot=[0, 0, 45 + 90 * k], pivot=(x, y, z))
    x, z, y = -R, 0, 38                                      # autumn maple leaf
    r.cube(w, (x - 1.6, y - 1.6, z - 0.4), (3.2, 3.2, 0.8), "bb_sm_autumn", rot=[0, 0, 45], pivot=(x, y, z))
    r.cube(w, (x - 2.6, y - 0.4, z - 0.4), (5.2, 1.4, 0.8), "bb_sm_autumn_d")
    r.cube(w, (x - 0.3, y - 3.4, z - 0.3), (0.6, 2.4, 0.6), "bb_sm_bark_d")
    x, z, y = 0, R, 41                                       # winter snowflake
    for k in range(3):
        r.cube(w, (x - 2.8, y - 0.35, z - 0.35), (5.6, 0.7, 0.7), "bb_sm_ice", rot=[0, 0, 60 * k], pivot=(x, y, z))
    B(r, w, x - 0.8, x + 0.8, y - 0.8, y + 0.8, z - 0.8, z + 0.8, "bb_sm_snow")
    # little cogs of time drifting round its head the other way
    g = r.bone("cogs", h, (0, 60, 0), role="orbit")
    for (x, z, y) in ((15, -5, 62),):
        B(r, g, x - 1.4, x + 1.4, y - 1.4, y + 1.4, z - 0.4, z + 0.4, "bb_sm_gold")
        B(r, g, x - 2.2, x + 2.2, y - 0.5, y + 0.5, z - 0.3, z + 0.3, "bb_sm_gold")
        B(r, g, x - 0.5, x + 0.5, y - 2.2, y + 2.2, z - 0.3, z + 0.3, "bb_sm_gold")
        B(r, g, x - 0.5, x + 0.5, y - 0.5, y + 0.5, z - 0.6, z + 0.6, "bb_sm_time")
    return r


# =====================================================================================================================
# World 9 - Heart of the Terrain
# =====================================================================================================================
M("bb_th_flesh", "9a2a34", "d0585e", "flesh")
M("bb_th_flesh_d", "641820", "983038", "flesh")
M("bb_th_vessel", "963440", "cc6068", "flesh")
M("bb_th_vein", "ff6a26", "ffb060", "vein", True)
M("bb_th_rock", "6e665e", "8e867a", "blocks")
M("bb_th_rock_d", "463f3a", "605852", "blocks")
M("bb_th_strata", "8a6a4a", "a88a64", "blocks")
M("bb_th_dirt", "5a3e2a", "7a5a3e", "blocks")
M("bb_th_grass", "5a8a32", "7eae48", "leaf")
M("bb_th_crystal", "ffae3a", "ffe6a0", "crystal", True)
M("bb_th_eye", "ffd83a", "fff2a8", "glow", True)
M("bb_th_maw", "ff5a1a", "ffb060", "magma", True)


def terrain_heart_boss():
    """The living heart of the restless ground: a huge anatomical heart of dark beating flesh, its atria, aorta and
    pulmonary trunk rising out of a carapace of rock and soil strata with grass still growing on top. Glowing veins
    of molten orange run over it, amber crystals grow through the stone, and a mask of rock is fused to its front,
    with burning eyes and a jaw of stalactites over a molten throat. Two arms of piled boulders bound by sinew end
    in crystal-knuckled fists; arteries plunge from its apex into the ground like roots, and torn-up chunks of
    earth orbit it."""
    r = Rig("terrain_heart_boss")
    # --- roots: arteries driven into the ground (rooted, they do not bob with the body)
    rt = r.bone("roots", None, (0, 0, 0))
    for (x0, x1, z0, z1, top, m) in ((-3.5, 3.5, -3.5, 3.5, 10.0, "bb_th_vessel"), (3, 6.5, -7, -3.5, 6.0, "bb_th_flesh_d"),
                                     (-8, -4.5, 2, 5.5, 6.5, "bb_th_flesh_d"), (5, 8, 4, 7, 5.0, "bb_th_vessel")):
        B(r, rt, x0, x1, 0, top, z0, z1, m)
    for (x0, x1, z0, z1) in ((4.5, 12, -6.5, -4), (-14, -6, 2.5, 5), (6, 13, 4.5, 6.5), (-3, -0.5, -13, -3)):
        B(r, rt, x0, x1, 0, 1.6, z0, z1, "bb_th_flesh_d")                                   # spreading over the floor
    B(r, rt, 9.5, 12.4, 0, 1.0, -6.0, -4.4, "bb_th_vein")
    B(r, rt, -1.8, -0.6, 0, 0.9, -12.6, -6, "bb_th_vein")
    for (x, z, w, hh, m) in ((-10, -8, 4.5, 2.6, "bb_th_rock"), (11, 9, 5, 3.2, "bb_th_rock_d"), (-12, 8, 3.5, 2.0, "bb_th_dirt"),
                             (9, -11, 3.2, 1.8, "bb_th_rock_d"), (0, 12, 4, 2.2, "bb_th_rock")):
        B(r, rt, x - w / 2, x + w / 2, 0, hh, z - w / 2, z + w / 2, m)                     # ground heaved up around it
    # --- body: the carapace of rock that does not beat
    r.bone("body", None, (0, 24, 0), role="body")
    bd = "body"
    B(r, bd, -10, 10, 14, 36, 7, 12, "bb_th_rock")                                         # back slab
    B(r, bd, -9, 9, 22, 30, 11.8, 13.4, "bb_th_strata")
    B(r, bd, -9.4, 9.4, 30, 31.6, 11.6, 13.2, "bb_th_dirt")
    B(r, bd, -12, -5, 29, 36, 1, 10, "bb_th_rock_d")                                       # rock gripping it from behind
    B(r, bd, 5, 12, 28, 34, 2, 9, "bb_th_rock")
    B(r, bd, -12.4, -5.4, 35.6, 37.0, 0.6, 10.4, "bb_th_grass")                              # grass still growing on top
    B(r, bd, -12.2, -11.6, 29.4, 35.4, 1.4, 9.4, "bb_th_strata")
    B(r, bd, 5.4, 11.6, 33.6, 35.0, 2.4, 8.6, "bb_th_grass")
    B(r, bd, -12.0, -9.2, 15, 27, 0, 8, "bb_th_rock")                                      # rock gripping its flanks
    B(r, bd, 9.4, 12.2, 15, 25, 0, 7, "bb_th_rock_d")
    B(r, bd, -12.4, -11.9, 20, 21.4, 0.6, 7.4, "bb_th_vein")
    # amber crystals forcing their way through the stone
    for (x, y, z, w, hh, tilt) in ((-8.5, 37.5, 3, 2.6, 7.0, 14), (-6.0, 37.5, 6, 1.8, 4.6, -10), (9.0, 35.5, 1, 2.2, 5.4, -18),
                                   (-12.4, 26, 0, 1.8, 4.0, 60), (7.5, 34, 6.5, 1.6, 3.6, 8), (0, 35.6, 10.5, 2.4, 6.0, 4)):
        r.cube(bd, (x - w / 2, y, z - w / 2), (w, hh, w), "bb_th_crystal", rot=[0, 0, tilt], pivot=(x, y, z))
    # --- the heart: it beats
    ht = r.bone("heart", bd, (0, 24, 0), role="pulse")
    octo(r, ht, 0, 0, 22, 33, 22, 18, 4, "bb_th_flesh")                                     # ventricles, tapering down
    octo(r, ht, 0.4, -0.2, 15.5, 22.4, 19.6, 16.6, 4, "bb_th_flesh")
    octo(r, ht, -5.6, 0, 32, 37.4, 10.6, 14, 3, "bb_th_flesh")                              # the two rounded lobes on top
    octo(r, ht, 5.8, 0.6, 32, 36.2, 10, 13, 3, "bb_th_flesh")
    octo(r, ht, 1.0, -0.4, 10.5, 15.9, 15.4, 13, 3.5, "bb_th_flesh")
    octo(r, ht, 2.0, -0.8, 6.0, 11.0, 9, 8, 2.5, "bb_th_flesh_d")                            # apex, off-centre
    octo(r, ht, -6.0, 4.5, 33, 39.5, 8, 8, 2, "bb_th_flesh_d")                              # atria behind
    B(r, ht, -1.4, 4.2, 34, 44, -1.6, 4.0, "bb_th_vessel")                                  # aorta rising
    B(r, ht, -7.4, 4.2, 41, 45.6, -1.6, 3.6, "bb_th_vessel")                                # ...and arching over
    B(r, ht, -7.6, -3.0, 36, 44, 3.0, 8.0, "bb_th_vessel")                                  # descending behind
    for (x, hh) in ((-4.6, 3.4), (-1.6, 4.6), (1.8, 3.0)):
        B(r, ht, x - 0.9, x + 0.9, 45.4, 45.4 + hh, -0.1, 1.7, "bb_th_vessel")              # branches torn off, still glowing
        B(r, ht, x - 0.6, x + 0.6, 45.2 + hh, 45.8 + hh, 0.2, 1.4, "bb_th_vein")
    B(r, ht, 4.0, 8.6, 34, 41, -5.4, -1.0, "bb_th_vessel")                                  # pulmonary trunk
    B(r, ht, 8.0, 12.6, 38.4, 41.0, -4.8, -1.6, "bb_th_vessel")
    B(r, ht, 12.2, 13.0, 38.6, 40.8, -4.6, -1.8, "bb_th_vein")
    # glowing coronary veins over the flesh, along the groove between the ventricles
    zf = -9.2
    poly2d(r, ht, [(-1.0, 36.6), (-2.6, 32.0), (-1.0, 29.4)], -7.2, "bb_th_vein", 0.6)
    poly2d(r, ht, [(-5.8, 21.0), (-3.4, 17.0), (-0.4, 13.6), (2.0, 9.6), (2.4, 7.2)], -9.4, "bb_th_vein", 0.6)
    poly2d(r, ht, [(5.6, 30.4), (6.4, 26.0), (4.6, 20.6), (5.8, 17.0)], zf, "bb_th_vein", 0.5)
    poly2d(r, ht, [(-5.0, 30.6), (-6.4, 27.6), (-5.4, 23.0)], zf, "bb_th_vein", 0.45)
    segside(r, ht, (-6, 30), (2, 22), 10.95, "bb_th_vein", 0.5)
    segside(r, ht, (2, 22), (-3, 15), 10.95, "bb_th_vein", 0.5)
    segside(r, ht, (-5, 28), (3, 18), -11.25, "bb_th_vein", 0.5)
    segside(r, ht, (-4, 35.6), (3, 33.4), 10.75, "bb_th_vein", 0.4)
    B(r, bd, -10.6, -5.4, 9.0, 15.0, -8.6, -4.0, "bb_th_rock")                             # a crust of stone grown over the apex
    B(r, bd, -9.6, -6.0, 8.0, 9.4, -7.6, -4.6, "bb_th_strata")
    r.cube(bd, (-9.6, 14.6, -7.4), (1.8, 3.6, 1.8), "bb_th_crystal", rot=[0, 0, 24], pivot=(-8.7, 14.6, -6.5))
    for (x, y, w) in ((6.2, 21.8, 2.6), (-5.0, 18.0, 2.2), (7.4, 14.0, 1.6)):
        B(r, ht, x - w / 2, x + w / 2, y - w / 2, y + w / 2, zf - 0.4, zf + 0.3, "bb_th_flesh_d")   # swellings
    # --- its face: burning eyes sunk in the flesh under a brow of rock, a mouth torn across the ventricles
    h = r.bone("head", bd, (0, 22, -9), role="head")
    B(r, h, -8.0, 8.0, 26.2, 28.8, -10.6, -8.6, "bb_th_rock_d")                             # brow of rock
    B(r, h, -5.6, 5.6, 28.8, 30.0, -10.0, -8.6, "bb_th_rock")
    B(r, h, -9.6, -7.6, 25.0, 29.4, -8.6, -4.8, "bb_th_rock")                               # where it is bolted into the flanks
    B(r, h, 7.6, 9.6, 25.4, 29.0, -8.6, -4.8, "bb_th_rock")
    for s in (1, -1):
        B(r, h, s * 1.2, s * 5.4, 22.0, 26.4, -9.6, -8.6, "ink")                             # sockets
        B(r, h, s * 1.6, s * 5.0, 22.6, 25.6, -9.95, -9.3, "bb_th_eye")
        B(r, h, s * 2.9, s * 3.7, 22.8, 25.4, -10.2, -9.8, "pupil")
        r.cube(h, (s * 3.3 - 2.6, 25.6, -11.2), (5.2, 1.4, 1.0), "bb_th_rock_d", rot=[0, 0, -14 * s], pivot=(s * 3.3, 26.3, -10.8))   # scowl
    B(r, h, -1.0, 1.0, 19.6, 26.4, -10.2, -8.6, "bb_th_rock")                               # a stone spur for a nose
    poly2d(r, h, [(-6.4, 28.6), (-4.4, 27.2), (-5.0, 26.4)], -10.8, "bb_th_vein", 0.4)       # cracks in the brow
    poly2d(r, h, [(5.4, 28.6), (6.6, 27.0)], -10.8, "bb_th_vein", 0.4)
    B(r, h, -6.0, 6.0, 15.6, 18.8, -9.6, -8.4, "bb_th_maw")                                  # molten throat
    B(r, h, -6.6, 6.6, 18.6, 19.6, -9.9, -8.6, "bb_th_flesh_d")                             # upper lip
    for x in (-5.4, -3.0, -0.6, 1.8, 4.2):
        B(r, h, x, x + 1.2, 16.8 + (0.6 if x in (-3.0, 1.8) else 0), 18.8, -10.2, -9.4, "bb_th_rock")   # stalactite teeth
    jw = r.bone("jaw", h, (0, 16, -8.4), role="jaw")
    B(r, jw, -7.0, 7.0, 13.4, 15.8, -9.9, -8.4, "bb_th_flesh_d")                           # lower lip
    for x in (-4.4, -1.8, 1.4, 4.0):
        B(r, jw, x, x + 1.2, 15.4, 17.0, -10.2, -9.4, "bb_th_rock")                        # stalagmite teeth
    B(r, jw, -0.6, 0.6, 15.4, 16.6, -10.3, -9.5, "bb_th_crystal")
    # --- arms of piled boulders bound by sinew
    for s, side in ((1, "l"), (-1, "r")):
        x = s * 15.0
        a0 = r.bone(f"arm_{side}0", bd, (x, 31, 0), role=f"arm_{side}0")
        B(r, a0, x - 2.2, x + 2.2, 19, 31, -2.2, 2.2, "bb_th_flesh_d")                       # sinew
        B(r, a0, x - 4.6, x + 4.6, 27, 34.4, -4.6, 4.6, "bb_th_rock")                       # shoulder boulder
        B(r, a0, x - 3.6, x + 3.6, 21, 25.6, -3.4, 3.8, "bb_th_rock_d")
        B(r, a0, x - 4.9, x + 4.9, 30.0, 30.8, -4.9, 4.9, "bb_th_vein")
        B(r, a0, s * 9.5, s * 12.0, 26.0, 28.6, -2.6, 0.4, "bb_th_vessel")                  # an artery feeding the arm
        B(r, a0, s * 9.3, s * 11.0, 26.6, 28.0, -2.9, -2.4, "bb_th_vein")
        a1 = r.bone(f"arm_{side}1", a0, (x, 19.5, 0), role=f"arm_{side}1")
        B(r, a1, x - 2.0, x + 2.0, 11, 20, -2.0, 2.0, "bb_th_flesh_d")
        B(r, a1, x - 3.4, x + 3.4, 13.4, 18.2, -3.4, 3.4, "bb_th_rock")
        B(r, a1, x - 5.0, x + 5.0, 2.0, 11.6, -5.0, 5.0, "bb_th_rock_d")                    # great fist
        B(r, a1, x - 5.4, x + 5.4, 6.0, 9.4, -5.6, 5.4, "bb_th_rock")
        for dz in (-3.4, 0.0, 3.4):                                                          # crystal knuckles
            r.cube(a1, (x - s * 0.6 - 0.9, 0.4, dz - 0.9), (1.8, 2.6, 1.8), "bb_th_crystal", rot=[0, 0, s * 20], pivot=(x, 2, dz))
        segside(r, a1, (-4.8, 10), (1, 4), x + s * 5.0 - (0.3 if s < 0 else 0), "bb_th_vein", 0.45)
        B(r, a1, x - 4.0, x + 4.0, 11.6, 12.4, -4.0, 4.0, "bb_th_grass" if s > 0 else "moss")
    # --- torn-up earth circling it
    for i in range(4):
        a = i * math.pi / 2 + 0.4
        o = r.bone(f"chunk{i}", bd, (0, 26, 0), role="orbit")
        cx, cz, y = math.cos(a) * 24, math.sin(a) * 24, 20 + (i % 2) * 12
        B(r, o, cx - 3, cx + 3, y - 2.4, y + 1.6, cz - 3, cz + 3, "bb_th_dirt")
        B(r, o, cx - 3.2, cx + 3.2, y + 1.6, y + 2.6, cz - 3.2, cz + 3.2, "bb_th_grass")
        B(r, o, cx - 1.6, cx + 1.4, y - 4.4, y - 2.2, cz - 1.6, cz + 1.4, "bb_th_rock_d")
        B(r, o, cx - 3.2, cx - 2.8, y - 1.8, y + 0.6, cz - 1, cz + 1.6, "bb_th_vein")
    return r


# =====================================================================================================================
# World 10 - The Unfinished (final boss)
# =====================================================================================================================
M("bb_un_lac", "b01e1a", "c8382a", "lacquer")
M("bb_un_lac_d", "8a1614", "a82a22", "lacquer")
M("bb_un_gold", "d8a440", "f6dc8a", "metal")
M("bb_un_gold_d", "a8782a", "d0a050", "metal")
M("bb_un_face", "f4dcc4", "fff0e0", "skin")
M("bb_un_cream", "f0e2c0", "fff4dc", "skin")
M("bb_un_wood", "d8b080", "e8c898", "bark")       # bare wood, never painted
M("bb_un_pencil", "3a3a46", "50505c", "skin")     # the sketch lines left on it
M("bb_un_hair", "2a1810", "40281a", "skin")
M("bb_un_cheek", "e8706a", "ffa098", "skin")
M("bb_un_lip", "c8202a", "e84a4a", "skin")
M("bb_un_iris", "1e3a8a", "3a5ac8", "skin")
M("bb_un_rose", "d8283a", "f05a6a", "skin")
M("bb_un_rose_d", "8a1020", "b02030", "skin")
M("bb_un_leaf", "2e8a3a", "5ab85a", "skin")
M("bb_un_blue", "2a4aa8", "5a7ad8", "lacquer")
M("bb_un_green", "1e6a3a", "3a9a5a", "lacquer")
M("bb_un_black", "1a1410", "3a2e22", "lacquer")
M("bb_un_core", "ffd27a", "fff4d0", "glow", True)
M("bb_un_core_hot", "ff8a2a", "ffd890", "glow", True)
M("bb_un_tape", "e8dcb0", "f8f0d0", "cloth")
M("bb_un_steel", "a8acb4", "e0e4ea", "metal")
M("bb_un_handle", "8a5a32", "a87a4a", "bark")
M("bb_un_socket", "1a0c08", "2a1810", "skin")
M("bb_un_gloss", "e0584a", "ee7a66", "skin")


def _mini_doll(r, bone, x, y, z, m, scale=1.0):
    """A small matryoshka: body, head, face, gold band."""
    s = scale
    octo(r, bone, x, z, y, y + 4.2 * s, 4.4 * s, 4.4 * s, 1.0 * s, m)
    B(r, bone, x - 1.6 * s, x + 1.6 * s, y + 4.2 * s, y + 7.0 * s, z - 1.6 * s, z + 1.6 * s, m)
    B(r, bone, x - 1.1 * s, x + 1.1 * s, y + 4.6 * s, y + 6.4 * s, z - 1.85 * s, z - 1.4 * s, "bb_un_face")
    B(r, bone, x - 2.3 * s, x + 2.3 * s, y + 0.4 * s, y + 1.2 * s, z - 2.3 * s, z + 2.3 * s, "bb_un_gold")


def the_unfinished():
    """The last doll of the workshop, never finished: a towering matryoshka in red lacquer and gold that opens at
    the waist. The maker painted it from the bottom up and stopped: the base is gilded and its apron carries a rose,
    but half the rose is still a pencil sketch; one side of its shoulders is bare wood ruled with guide lines and a
    gold band abandoned in mid-stroke, paint dripping, a chisel left stuck in it, the lathe
    spur still on its crown. Its sweet painted face has one finished blue eye and one that is only an outline, with a
    light burning where the pupil should be. Light leaks from the unglued seam. Inside waits a black-and-gold inner
    doll with gilded eyes and a glowing core in its chest. It moves on wooden mannequin arms, a dripping paintbrush in
    one hand and a tiny doll held out in the other, and the dolls of the earlier worlds circle it."""
    r = Rig("the_unfinished")
    r.bone("body", None, (0, 0, 0), role="body")
    bd = "body"
    # --- the inner doll and its core (hidden until the shell opens)
    inn = r.bone("inner", bd, (0, 2, 0))
    octo(r, inn, 0, 0, 2, 30, 19, 19, 4.5, "bb_un_black")
    octo(r, inn, 0, 0, 30, 40, 14, 14, 3.5, "bb_un_black")
    B(r, inn, -4.5, 4.5, 40, 42.4, -4.5, 4.5, "bb_un_black")
    B(r, inn, -4.2, 4.2, 31.6, 38.4, -7.4, -3.0, "bb_un_face")                      # its face, eyes shut and gilded
    for s in (1, -1):
        B(r, inn, s * 1.0, s * 3.4, 34.8, 35.6, -7.7, -7.2, "bb_un_core")
    B(r, inn, -1.0, 1.0, 32.6, 33.2, -7.7, -7.2, "bb_un_lip")
    B(r, inn, -9.8, 9.8, 28.6, 30.0, -5.2, 5.2, "bb_un_gold")                        # gold collar
    B(r, inn, -5.2, 5.2, 28.6, 30.0, -9.8, 9.8, "bb_un_gold")
    B(r, inn, -4.0, 4.0, 20.4, 29.6, -10.0, -9.4, "bb_un_gold")                      # setting of the core
    core = r.bone("core", inn, (0, 25, -10), role="pulse")
    r.cube(core, (-2.6, 22.4, -11.4), (5.2, 5.2, 2.2), "bb_un_core_hot", rot=[0, 0, 45], pivot=(0, 25, -10.3))
    r.cube(core, (-1.4, 23.6, -11.9), (2.8, 2.8, 1.0), "bb_un_core", rot=[0, 0, 45], pivot=(0, 25, -11.4))
    # --- the lower shell: finished, gilded, its apron painted with a rose (half of it still a sketch)
    lo = r.bone("shell_bottom", bd, (0, 0, 0), role="shell_bottom")
    octo(r, lo, 0, 0, 0, 2.2, 21, 21, 4.8, "bb_un_gold")                              # gilded foot, the egg narrowing to it
    octo(r, lo, 0, 0, 2.0, 6.4, 24.2, 24.2, 5.8, "bb_un_lac")
    octo(r, lo, 0, 0, 6.2, 11.2, 26.2, 26.2, 6.2, "bb_un_lac")
    octo(r, lo, 0, 0, 11.0, 19.6, 27, 27, 6.4, "bb_un_lac")
    octo(r, lo, 0, 0, 19.4, 21.0, 27.6, 27.6, 6.6, "bb_un_gold")                       # gold lip of the seam
    octo(r, lo, 0, 0, 21.0, 21.9, 26.3, 26.3, 6.1, "bb_un_core")                      # light leaking from the unglued seam
    B(r, lo, -6.4, 6.4, 2.6, 3.1, -12.5, -12.0, "bb_un_gold_d")
    zf = -13.7
    B(r, lo, -5.2, 5.2, 4.6, 19.0, zf, zf + 0.6, "bb_un_cream")                        # apron, an oval panel
    B(r, lo, -6.6, 6.6, 6.8, 16.6, zf + 0.1, zf + 0.6, "bb_un_cream")
    B(r, lo, -3.4, 3.4, 18.8, 19.6, zf + 0.1, zf + 0.6, "bb_un_cream")
    octo(r, lo, 0, 0, 10.7, 11.5, 27.3, 27.3, 6.5, "bb_un_gold_d")                     # gold band round the belly
    B(r, lo, -1.0, 2.8, 9.8, 15.2, zf - 0.4, zf, "bb_un_rose")                         # the painted half of the rose
    B(r, lo, 0.4, 4.4, 10.8, 14.2, zf - 0.3, zf, "bb_un_rose")
    B(r, lo, -0.2, 1.6, 11.6, 13.6, zf - 0.6, zf - 0.3, "bb_un_rose_d")
    B(r, lo, 0.6, 1.2, 12.2, 13.0, zf - 0.8, zf - 0.5, "bb_un_gold")
    r.cube(lo, (2.4, 6.6, zf - 0.3), (3.2, 1.6, 0.3), "bb_un_leaf", rot=[0, 0, 35], pivot=(3.6, 7.4, zf))
    r.cube(lo, (2.6, 15.4, zf - 0.3), (2.8, 1.4, 0.3), "bb_un_leaf", rot=[0, 0, -30], pivot=(3.6, 16.1, zf))
    B(r, lo, 1.0, 1.5, 6.0, 9.8, zf - 0.3, zf, "bb_un_leaf")                           # stem
    # the other half, only pencilled
    poly2d(r, lo, [(-1.0, 15.2), (-3.2, 15.4), (-4.4, 13.6), (-4.2, 11.0), (-2.8, 9.4), (-1.0, 9.8)], zf - 0.2, "bb_un_pencil", 0.3, 0.25)
    poly2d(r, lo, [(-1.2, 13.8), (-2.6, 13.2), (-2.6, 11.4)], zf - 0.2, "bb_un_pencil", 0.3, 0.25)
    poly2d(r, lo, [(0.8, 8.6), (-1.6, 7.0), (-4.2, 6.4)], zf - 0.2, "bb_un_pencil", 0.3, 0.25)
    # flowers on the flanks: gold and blue on one side, a sketch on the other
    B(r, lo, 13.4, 14.0, 10.6, 15.6, -2.5, 2.5, "bb_un_gold")
    B(r, lo, 13.8, 14.3, 11.8, 14.4, -1.3, 1.3, "bb_un_blue")
    poly2d_side = [(-2.4, 11.0), (0.0, 15.6), (2.4, 11.0), (-2.4, 11.0)]
    for a, b in zip(poly2d_side, poly2d_side[1:]):
        segside(r, lo, a, b, -14.0, "bb_un_pencil", 0.3, 0.3)
    # a crack in the belly, the core shining through
    poly2d(r, lo, [(-10.2, 18.6), (-9.0, 16.2), (-10.0, 13.6), (-8.8, 11.2)], -11.0, "bb_un_core", 0.5, 0.6)
    # a workshop tag tied at the back
    B(r, lo, -0.3, 0.3, 14.0, 19.6, 13.4, 13.9, "bb_un_tape")
    B(r, lo, -2.0, 2.0, 10.6, 14.2, 13.6, 14.1, "bb_un_gold_d")
    B(r, lo, -1.0, 0.2, 11.6, 13.2, 14.0, 14.3, "bb_un_black")
    # --- the upper shell: lacquer on one side, bare ruled wood on the other
    up = r.bone("shell_top", bd, (0, 21, 0), role="shell_top")
    octo(r, up, 0, 0, 21.6, 27.2, 26, 26, 6, "bb_un_lac")
    for (ya, yb, w, cut) in ((27.0, 32.2, 23, 5.4),):
        B(r, up, 0, w / 2, ya, yb, -w / 2 + cut, w / 2 - cut, "bb_un_lac")
        B(r, up, 0, w / 2 - cut, ya, yb, -w / 2, w / 2, "bb_un_lac")
        B(r, up, -w / 2, 0, ya, yb, -w / 2 + cut, w / 2 - cut, "bb_un_wood")
        B(r, up, -(w / 2 - cut), 0, ya, yb, -w / 2, w / 2, "bb_un_wood")
    B(r, up, -9.5, 0, 32.0, 34.2, -4.8, 4.8, "bb_un_wood")                             # neck
    B(r, up, -4.8, 0, 32.0, 34.2, -9.5, 9.5, "bb_un_wood")
    B(r, up, 0, 9.5, 32.0, 34.2, -4.8, 4.8, "bb_un_lac")
    B(r, up, 0, 4.8, 32.0, 34.2, -9.5, 9.5, "bb_un_lac")
    B(r, up, -0.25, 0.25, 21.8, 34.4, -13.25, -9.6, "bb_un_pencil")                    # where the paint stops
    for y in (29.0, 31.0):
        B(r, up, -11.7, -0.2, y, y + 0.3, -6.3, -6.0, "bb_un_pencil")                    # guide lines ruled on the wood
    B(r, up, -11.6, -0.2, 27.6, 28.4, -6.4, -6.0, "bb_un_gold")                        # a gold band abandoned mid-stroke
    B(r, up, -4.0, -3.2, 25.8, 27.8, -13.3, -12.9, "bb_un_lac")                        # paint drips
    B(r, up, -7.4, -6.8, 26.4, 27.8, -13.3, -12.9, "bb_un_lac")
    # a chisel left stuck in the wood
    r.cube(up, (-12.8, 30.2, 3.0), (3.0, 0.8, 1.6), "bb_un_steel", rot=[0, 0, -30], pivot=(-11.5, 30.6, 3.8))
    r.cube(up, (-18.4, 31.4, 2.9), (5.2, 1.6, 1.8), "bb_un_handle", rot=[0, 0, -30], pivot=(-13.0, 31.0, 3.8))
    r.cube(up, (-13.8, 31.0, 2.7), (1.0, 2.0, 2.2), "bb_un_gold_d", rot=[0, 0, -30], pivot=(-13.0, 31.0, 3.8))
    # a painted braid down the back of the scarf
    B(r, up, -1.6, 1.6, 22.4, 33.0, 11.0, 13.4, "bb_un_hair")
    B(r, up, -1.9, 1.9, 22.0, 23.2, 12.6, 13.8, "bb_un_gold")
    # scarf knot under the chin
    B(r, up, -2.6, 2.6, 31.6, 34.0, -10.6, -9.4, "bb_un_lac_d")
    # --- the head (turns on the upper shell)
    h = r.bone("head", up, (0, 34, 0), role="head")
    octo(r, h, 0, 0, 34.0, 43.4, 19, 19, 4.6, "bb_un_lac")
    octo(r, h, 0, 0, 43.2, 46.0, 15, 15, 3.6, "bb_un_lac")
    octo(r, h, 0, 0, 46.0, 47.4, 9, 9, 2.2, "bb_un_lac_d")
    B(r, h, -1.0, 1.0, 47.4, 48.6, -1.0, 1.0, "bb_un_wood")                             # lathe spur never cut off
    B(r, h, -1.8, 1.8, 46.9, 47.6, -1.8, 1.8, "bb_un_pencil")
    B(r, h, -9.4, 9.4, 33.8, 34.6, -4.6, 4.6, "bb_un_gold")                             # gold rim of the scarf
    B(r, h, -4.6, 4.6, 33.8, 34.6, -9.4, 9.4, "bb_un_gold")
    zf = -10.0
    B(r, h, -6.0, 6.0, 35.0, 42.4, zf, -4.5, "bb_un_face")                              # the face, an oval
    B(r, h, -4.8, 4.8, 34.4, 43.0, zf, -4.5, "bb_un_face")
    B(r, h, -6.6, 6.6, 42.4, 43.4, zf - 0.3, -4.5, "bb_un_gold")                        # gold edge of the scarf
    for s in (1, -1):
        B(r, h, s * 6.0, s * 6.8, 35.0, 42.6, zf - 0.3, -4.5, "bb_un_gold")
    B(r, h, -4.8, -0.3, 41.2, 42.4, zf - 0.3, zf, "bb_un_hair")                        # parted hair
    B(r, h, 0.3, 4.8, 41.2, 42.4, zf - 0.3, zf, "bb_un_hair")
    B(r, h, 4.8, 6.0, 37.4, 42.4, zf - 0.3, zf, "bb_un_hair")
    B(r, h, -6.0, -4.8, 37.4, 42.4, zf - 0.3, zf, "bb_un_hair")
    #   the finished eye: white, blue iris, pupil, a highlight, lashes, a brow
    zp = zf - 0.3
    B(r, h, 1.2, 4.4, 37.8, 40.0, zp, zf, "eye_white")
    B(r, h, 1.8, 3.8, 37.8, 40.0, zp - 0.2, zp + 0.1, "bb_un_iris")
    B(r, h, 2.4, 3.2, 38.2, 39.4, zp - 0.4, zp - 0.1, "pupil")
    B(r, h, 3.0, 3.5, 39.2, 39.7, zp - 0.55, zp - 0.3, "bb_un_core")
    B(r, h, 1.0, 4.6, 40.0, 40.5, zp - 0.2, zf, "bb_un_hair")
    r.cube(h, (1.2, 40.9, zp - 0.1), (3.4, 0.45, 0.3), "bb_un_hair", rot=[0, 0, 8], pivot=(2.9, 41.1, zp))
    #   the unfinished eye: an outline, and a light where the pupil should be
    poly2d(r, h, [(-1.2, 38.9), (-2.4, 40.1), (-3.8, 40.0), (-4.5, 38.9), (-3.5, 37.8), (-2.0, 37.8), (-1.2, 38.9)], zp, "bb_un_pencil", 0.28, 0.25)
    B(r, h, -3.2, -2.4, 38.4, 39.4, zp - 0.3, zf, "bb_un_core")
    r.cube(h, (-4.6, 40.9, zp - 0.1), (3.4, 0.3, 0.25), "bb_un_pencil", rot=[0, 0, -8], pivot=(-2.9, 41.1, zp))
    #   cheeks, nose, little red mouth (half of it pencilled)
    B(r, h, 3.0, 5.4, 35.6, 37.0, zp, zf, "bb_un_cheek")
    poly2d(r, h, [(-3.0, 37.0), (-5.0, 36.8), (-5.2, 35.6), (-3.2, 35.4)], zp, "bb_un_pencil", 0.25, 0.25)
    B(r, h, -0.5, 0.5, 36.8, 37.6, zp - 0.1, zf, "bb_un_cheek")
    B(r, h, 0.0, 1.4, 35.2, 36.2, zp, zf, "bb_un_lip")
    B(r, h, 0.2, 1.0, 36.2, 36.6, zp, zf, "bb_un_lip")
    poly2d(r, h, [(0.0, 36.4), (-0.8, 36.0), (-1.4, 35.6), (0.0, 35.2)], zp, "bb_un_pencil", 0.22, 0.25)
    #   gold flowers painted on the scarf
    for (x, y) in ((5.4, 44.0), (-5.0, 44.2)):
        B(r, h, x - 1.2, x + 1.2, y - 1.2, y + 1.2, -7.4, -6.9, "bb_un_gold" if x > 0 else "bb_un_cream")
    B(r, h, 4.9, 5.9, 43.5, 44.5, -7.6, -7.2, "bb_un_blue")
    # --- wooden mannequin arms (they belong to the inner doll and pass through the shell)
    for s, side in ((1, "l"), (-1, "r")):
        x = s * 15.6
        B(r, up, s * 11.4, s * 13.3, 22.6, 27.4, -2.4, 2.4, "bb_un_socket")                # hole in the shell
        B(r, up, s * 11.0, s * 13.1, 22.0, 28.0, -2.9, -2.3, "bb_un_gold")
        a0 = r.bone(f"arm_{side}0", inn, (x, 25, 0), role=f"arm_{side}0")
        octo(r, a0, x, 0, 22.4, 27.6, 5.2, 5.2, 1.3, "bb_un_wood")                        # ball joint
        B(r, a0, x - 1.9, x + 1.9, 14.0, 23.4, -1.9, 1.9, "bb_un_wood")
        B(r, a0, x - 2.2, x + 2.2, 19.0, 20.2, -2.2, 2.2, "bb_un_gold")
        poly2d(r, a0, [(x - 1.0, 22.8), (x + 0.6, 17.2)], -2.05, "bb_un_pencil", 0.22, 0.2)
        a1 = r.bone(f"arm_{side}1", a0, (x, 14.4, 0), role=f"arm_{side}1")
        octo(r, a1, x, 0, 12.2, 16.4, 4.4, 4.4, 1.1, "bb_un_wood")                        # elbow ball
        B(r, a1, x - 1.6, x + 1.6, 6.2, 13.0, -1.6, 1.6, "bb_un_wood")
        B(r, a1, x - 2.2, x + 2.2, 2.4, 6.8, -2.4, 2.4, "bb_un_wood")                    # hand
        B(r, a1, x - 2.0, x + 2.0, 6.6, 7.6, -2.0, 2.0, "bb_un_gold")
        B(r, a1, x - 1.8, x + 1.8, 1.0, 2.6, -2.6, -0.8, "bb_un_wood")                    # fingers
    # a dripping paintbrush in one hand
    br = r.bone("brush", "arm_r1", (-15.6, 4.6, 0))
    B(r, br, -16.4, -14.8, 3.8, 5.4, -1.0, 8.0, "bb_un_handle")
    B(r, br, -16.8, -14.4, 3.4, 5.8, -5.0, -1.0, "bb_un_gold")                          # ferrule
    B(r, br, -17.3, -13.9, 2.9, 6.3, -10.6, -5.0, "bb_un_wood")                         # bristles
    B(r, br, -17.1, -14.1, 3.1, 6.1, -13.8, -10.4, "bb_un_lac")                         # loaded with red lacquer
    B(r, br, -15.9, -15.3, 1.0, 3.2, -12.6, -12.0, "bb_un_lac")                         # a drip
    B(r, br, -15.8, -15.4, 0.0, 0.6, -12.5, -12.1, "bb_un_lac")
    # and, held out in the other, a tiny doll: the last form
    _mini_doll(r, "arm_l1", 15.6, 2.6, -4.6, "bb_un_lac", 0.6)
    # --- the dolls of the earlier worlds circling it
    for i, (m, ang, y, sc) in enumerate((("bb_un_blue", 30, 30, 1.0), ("bb_un_green", 150, 22, 0.85), ("bb_un_black", 250, 36, 0.75))):
        o = r.bone(f"doll{i}", bd, (0, y, 0), role="orbit")
        a = math.radians(ang)
        _mini_doll(r, o, math.cos(a) * 23, y, math.sin(a) * 23, m, sc)
    return r
