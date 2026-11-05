"""Boss models, v2, part A: the first six bosses (The Surface to the Lightless Deep).

Each function builds a Rig with the standard bone roles so bosses_hd.standard_anims animates it:
body, head, jaw, arm_l0/arm_l1, arm_r0/arm_r1, leg_*, tail, cape, chain, wing_*, orbit, pulse, insect_*.
Front is -Z, up +Y, feet on y = 0, 16 units = 1 block. New materials are prefixed `ba_`.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from bosses_hd import Rig, MAT  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mobs_hd'))
import common  # noqa: E402,F401  (registers the EXTRA materials: pupil, tooth, bone, eye_*, ...)


def M(name, base, accent, pattern="skin", emissive=False):
    MAT[name] = (base, accent, pattern, emissive)
    return name


def C(r, bone, cx, y, cz, w, h, d, m, **kw):
    """A cube centred on x/z, standing on y."""
    r.cube(bone, (cx - w / 2, y, cz - d / 2), (w, h, d), m, **kw)


def eye(r, bone, x, y, z, w, h, glow, pupil="dot", socket="pupil"):
    """A glowing eye in a dark socket on a face whose front plane is at depth z (facing -Z)."""
    r.cube(bone, (x - w / 2 - 0.4, y - h / 2 - 0.4, z - 0.2), (w + 0.8, h + 0.8, 0.4), socket)
    r.cube(bone, (x - w / 2, y - h / 2, z - 0.4), (w, h, 0.4), glow)
    if pupil == "dot":
        r.cube(bone, (x - w * 0.18, y - h * 0.25, z - 0.55), (w * 0.36, h * 0.5, 0.2), "pupil")
    elif pupil == "slit":
        r.cube(bone, (x - 0.18, y - h / 2, z - 0.55), (0.36, h, 0.2), "pupil")
    elif pupil == "ring":
        r.cube(bone, (x - w * 0.3, y - h * 0.3, z - 0.55), (w * 0.6, h * 0.6, 0.2), "pupil")
        r.cube(bone, (x - w * 0.12, y - h * 0.12, z - 0.7), (w * 0.24, h * 0.24, 0.2), glow)


def teeth(r, bone, x0, x1, y, z, n, h, m="tooth", down=False, w=0.8, d=0.8):
    """A row of n teeth between x0 and x1 at depth z; they hang down from y when down, else rise from y."""
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        hh = h * (0.75 + 0.25 * ((i * 7) % 3) / 2)
        r.cube(bone, (x - w / 2, y - hh if down else y, z - d / 2), (w, hh, d), m)


def rivets(r, bone, pts, m, s=0.7, face="front"):
    for (x, y, z) in pts:
        r.cube(bone, (x - s / 2, y - s / 2, z - s / 2), (s, s, s), m)


# =============================================================== The Surface: Block Guardian
M("ba_bg_stone", "7a7570", "a39d94", "blocks")
M("ba_bg_brick", "6c6863", "8e8880", "blocks")
M("ba_bg_cobble", "55524f", "77726c", "blocks")
M("ba_bg_deep", "3c3a3c", "5a575a", "blocks")
M("ba_bg_dirt", "7a5232", "9a6a42", "blocks")
M("ba_bg_grass", "5a9a34", "8ccc4e", "leaf")
M("ba_bg_moss", "3e7a2c", "6aa840", "leaf")
M("ba_bg_log", "6a4a2a", "8a6438", "bark")
M("ba_bg_leaves", "3e8a2a", "7ac44a", "leaf")
M("ba_bg_rune", "3ac8ff", "8ae4ff", "glow", True)
M("ba_bg_rune_dim", "2a4a5a", "6ad8ff", "rune")
M("ba_bg_core", "7aeaff", "c8f8ff", "glow", True)
M("ba_bg_diamond", "6a6864", "5ae8e0", "spots")
M("ba_bg_gold", "7a746c", "f8d040", "spots")
M("ba_bg_redstone", "6a625e", "ff3a2a", "spots")
M("ba_bg_iron", "7a7068", "d8b08a", "blocks")
M("ba_bg_poppy", "d82a2a", "ff6a5a", "skin")
M("ba_bg_tooth", "b8b2a6", "dcd6ca", "blocks")


def block_guardian():
    """A golem quarried out of the overworld itself: stone-brick trunk with dirt and deepslate strata, grass
    blocks for pauldrons (a sapling grows on one, a poppy on the other), ore veins in the chest, a rune core
    glowing through a split in the breastplate, a heavy brow over cyan rune eyes, square teeth, block fists
    with knuckle stones, and four torn terrain blocks circling it."""
    r = Rig("block_guardian")
    # ---- legs: brick thigh, cobble knee, block shin, wide mossy foot
    for side, s in (("l", 1), ("r", -1)):
        hx = s * 7.5
        l0 = r.bone(f"leg_{side}0", None, (hx, 21, 0), role=f"leg_{side}0")
        C(r, l0, hx, 10, 0, 8, 12, 8, "ba_bg_brick")
        C(r, l0, hx, 17, 0, 9, 2, 9, "ba_bg_cobble")                       # hip band
        C(r, l0, hx + s * 4.1, 12, -1, 0.4, 6, 0.5, "ba_bg_rune")          # crack of rune light on the outer thigh
        l1 = r.bone(f"leg_{side}1", l0, (hx, 11, 0), role=f"leg_{side}1")
        C(r, l1, hx, 3, 0, 9, 9, 9, "ba_bg_stone")
        C(r, l1, hx, 9.5, -0.5, 10, 3, 10, "ba_bg_cobble")                 # knee cap
        C(r, l1, hx, 10, -5.6, 4, 2.4, 1, "ba_bg_rune_dim")                # knee glyph
        C(r, l1, hx, 0, -1.5, 11, 4, 13, "ba_bg_deep")                     # foot
        C(r, l1, hx, 4, -1.5, 11, 0.8, 13, "ba_bg_moss")                   # moss on the foot
        for i in range(3):
            C(r, l1, hx - 3.6 + i * 3.6, 0, -8.4, 2.8, 2.6, 1.8, "ba_bg_cobble")  # toe stones
        C(r, l1, hx + s * 2, 4.6, -6, 0.8, 1.4, 0.8, "ba_bg_grass")        # grass tuft
    # ---- trunk
    b = r.bone("body", None, (0, 21, 0), role="body")
    C(r, b, 0, 17, 0, 20, 7, 11, "ba_bg_cobble")                            # pelvis
    C(r, b, 0, 19.5, 0, 20.6, 2.5, 11.6, "ba_bg_dirt")                      # a dirt stratum through it
    for x, ln in ((-6, 4), (-1.5, 6), (3, 3), (7, 5)):
        C(r, b, x, 17 - ln, -4.5, 0.8, ln + 0.5, 0.8, "ba_bg_log")          # roots torn out with it
    # a ridge of jutting blocks on the back, like a hillside
    for i, (x, y, rz) in enumerate(((-9, 38, 20), (0, 41, -8), (8.5, 37, -24), (-3, 31, 12))):
        C(r, b, x, y, 10.5, 6, 6, 6, "ba_bg_deep" if i % 2 else "ba_bg_stone", rot=[25, 10 * i, rz], pivot=(x, y, 9))
        C(r, b, x, y + 5.6, 10.5, 6.2, 1.2, 6.2, "ba_bg_grass", rot=[25, 10 * i, rz], pivot=(x, y, 9)) if i != 1 else None
    C(r, b, 0, 23.5, 0, 16, 5, 10, "ba_bg_deep")                            # waist: deepslate
    C(r, b, 0, 27, 0.5, 28, 9, 15, "ba_bg_brick")                           # lower chest
    C(r, b, 0, 35.5, 1, 32, 9, 16, "ba_bg_stone")                           # upper chest / shoulders
    C(r, b, 0, 43.5, 2.5, 22, 2.5, 11, "ba_bg_grass")                       # grass ledge behind the head
    C(r, b, 0, 42.5, 2.5, 22, 1.2, 11.4, "ba_bg_dirt")
    # breastplates split in the middle to show the core
    C(r, b, -7.5, 29, -7.4, 12, 13, 2, "ba_bg_stone")
    C(r, b, 7.5, 29, -7.4, 12, 13, 2, "ba_bg_stone")
    C(r, b, 0, 27.5, -7.2, 3.4, 15, 1, "ba_bg_deep")                         # dark slot behind the core
    core = r.bone("core", b, (0, 35, -8), role="pulse")
    C(r, core, 0, 32.5, -8, 2.6, 5, 1.6, "ba_bg_core")
    C(r, core, 0, 34.3, -8, 4.6, 1.4, 1.2, "ba_bg_core")                     # a rune cross
    C(r, core, 0, 31.6, -8.1, 1.2, 0.9, 1.0, "ba_bg_rune")
    C(r, core, 0, 37.6, -8.1, 1.2, 0.9, 1.0, "ba_bg_rune")
    # ores set in the chest
    C(r, b, -9.5, 37.5, -8.6, 3.2, 3.2, 1.2, "ba_bg_diamond")
    C(r, b, 10, 31, -8.6, 3.6, 2.8, 1.2, "ba_bg_gold")
    C(r, b, -11.5, 29.5, -8.4, 2.4, 2.4, 1, "ba_bg_redstone")
    C(r, b, 6.5, 38.5, -8.5, 2.4, 2.0, 1, "ba_bg_iron")
    # rune cracks running from the core
    r.cube(b, (2.0, 36.5, -8.5), (5.5, 0.5, 0.5), "ba_bg_rune", rot=[0, 0, 28], pivot=(2, 36.5, -8.3))
    r.cube(b, (-7.2, 33.0, -8.5), (5.2, 0.5, 0.5), "ba_bg_rune", rot=[0, 0, -22], pivot=(-2, 33, -8.3))
    r.cube(b, (3.5, 30.0, -8.5), (0.5, 3.5, 0.5), "ba_bg_rune")
    # belt of cobble with a carved keystone
    C(r, b, 0, 26, 0.5, 29, 2, 16, "ba_bg_cobble")
    C(r, b, 0, 25.4, -7.9, 4.4, 3.2, 1, "ba_bg_rune_dim")
    # back: stacked spine stones, vines
    for i in range(4):
        C(r, b, 0, 25 + i * 4.6, 9.4, 6 - i * 0.6, 3.6, 2, "ba_bg_cobble" if i % 2 else "ba_bg_deep")
        C(r, b, 0, 26.2 + i * 4.6, 10.5, 1.2, 1.2, 0.4, "ba_bg_rune")
    for x, ln in ((-12, 9), (-4.5, 6), (9, 11)):
        C(r, b, x, 43.5 - ln, 9.3, 1.2, ln, 0.6, "ba_bg_moss")
    C(r, b, -15.5, 36, -2, 1, 5, 6, "ba_bg_moss")                             # moss creeping on the flank
    # ---- head: sunk between the shoulders
    h = r.bone("head", b, (0, 43, -2), role="head")
    C(r, h, 0, 43.5, -3, 12, 9.5, 10, "ba_bg_stone")
    C(r, h, 0, 50.5, -4.5, 14, 3.4, 7.5, "ba_bg_brick")                      # heavy brow slab
    C(r, h, 0, 53.4, -3, 12.4, 1.4, 10.4, "ba_bg_grass")                     # turf on the skull
    C(r, h, 0, 52.9, -3, 12.6, 0.6, 10.6, "ba_bg_dirt")
    C(r, h, 3.5, 54.6, -1, 2, 0.8, 2, "ba_bg_grass")
    eye(r, h, -3.3, 48.0, -8.0, 3.0, 1.6, "ba_bg_rune", "slit", "ba_bg_deep")
    eye(r, h, 3.3, 48.0, -8.0, 3.0, 1.6, "ba_bg_rune", "slit", "ba_bg_deep")
    C(r, h, -3.6, 48.9, -8.9, 5.2, 1.6, 1.4, "ba_bg_cobble", rot=[0, 0, -16], pivot=(-1, 49.6, -8.6))  # angry brow, left
    C(r, h, 3.6, 48.9, -8.9, 5.2, 1.6, 1.4, "ba_bg_cobble", rot=[0, 0, 16], pivot=(1, 49.6, -8.6))
    C(r, h, 0, 46.0, -8.4, 2.2, 4.0, 1.4, "ba_bg_brick")                     # nose stone
    C(r, h, -5.2, 45.6, -8.2, 1.6, 1.6, 0.6, "ba_bg_cobble")                 # cheek stones
    C(r, h, 5.2, 45.6, -8.2, 1.6, 1.6, 0.6, "ba_bg_cobble")
    C(r, h, 5.8, 46.8, -8.45, 0.4, 3.0, 0.4, "ba_bg_rune")                   # glowing crack under the right eye
    C(r, h, -6.3, 51.4, -8.5, 1.8, 2.2, 1.0, "ba_bg_deep")                   # chipped corner
    C(r, h, 6.2, 44.5, -4, 0.8, 2.6, 2.6, "ba_bg_redstone")                  # ore in the cheek
    teeth(r, h, -4.2, 4.2, 44.4, -7.7, 5, 1.4, "ba_bg_tooth", down=True, w=1.2, d=1.0)
    jaw = r.bone("jaw", h, (0, 44.5, 1), role="jaw")
    C(r, jaw, 0, 40.6, -3.2, 11, 4.2, 9.6, "ba_bg_brick")
    C(r, jaw, 0, 40.0, -6.2, 8, 1.4, 3.4, "ba_bg_cobble")                    # chin block
    teeth(r, jaw, -4.4, 4.4, 44.6, -7.4, 4, 1.4, "ba_bg_tooth", w=1.3, d=1.0)
    C(r, jaw, 0, 43.4, -5, 8, 1.2, 5, "maw")                                 # dark mouth floor
    # ---- arms: grass-block pauldrons, brick upper arm, rune elbow, block forearm, fist
    for side, s in (("l", 1), ("r", -1)):
        sx = s * 18.5
        a0, a1 = r.limb(f"arm_{side}", b, (sx, 41, 0), [(8, 12, 8), (9, 11, 9)], "ba_bg_brick", "ba_bg_rune", role=f"arm_{side}")
        C(r, a0, sx + s * 0.5, 37, 0, 12, 6.5, 12, "ba_bg_dirt")              # pauldron: a grass block
        C(r, a0, sx + s * 0.5, 43.5, 0, 12, 1.6, 12, "ba_bg_grass")
        C(r, a0, sx + s * 0.5, 42.8, 0, 12.3, 1.0, 12.3, "ba_bg_grass")      # grass overhang
        for z in (-4, 0.5, 4):
            C(r, a0, sx + s * 6.3, 40.8 - abs(z) * 0.3, z, 0.6, 2.2, 1.4, "ba_bg_grass")  # grass dripping over the edge
        C(r, a1, sx, 25, -4.9, 4, 1.4, 0.6, "ba_bg_rune")                    # rune band at the elbow
        C(r, a1, sx, 10.5, -0.5, 12, 9, 11, "ba_bg_stone")                   # fist
        C(r, a1, sx, 18.5, -0.5, 12.6, 2, 11.6, "ba_bg_cobble")              # wrist cuff
        for i in range(4):
            C(r, a1, sx - 4.2 + i * 2.8, 11.2, -6.6, 2.4, 2.6, 1.6, "ba_bg_cobble")  # knuckle stones
        C(r, a1, sx + s * 6.3, 12, -2, 1.2, 3, 3.2, "ba_bg_cobble")          # thumb
        C(r, a1, sx - s * 2, 15, -6.2, 2.6, 2.6, 0.8, "ba_bg_gold" if s > 0 else "ba_bg_diamond")
    # the sapling and the poppy
    C(r, "arm_l0", 18.5, 44.5, 2, 1.4, 6, 1.4, "ba_bg_log")
    C(r, "arm_l0", 18.5, 49.5, 2, 5.5, 3.5, 5.5, "ba_bg_leaves")
    C(r, "arm_l0", 18.5, 52.6, 2, 3.2, 2, 3.2, "ba_bg_leaves")
    C(r, "arm_l0", 19.8, 47.0, 2, 2.2, 0.8, 0.8, "ba_bg_log")
    C(r, "arm_r0", -21, 44.5, -3, 0.4, 2.6, 0.4, "ba_bg_moss")
    C(r, "arm_r0", -21, 47.0, -3, 1.4, 1.1, 1.4, "ba_bg_poppy")
    C(r, "arm_r0", -15.5, 44.5, 3, 1.2, 1.0, 1.2, "ba_bg_moss")
    # ---- four torn terrain blocks orbiting it
    kinds = [("ba_bg_dirt", "ba_bg_grass"), ("ba_bg_stone", "ba_bg_diamond"), ("ba_bg_cobble", "ba_bg_moss"), ("ba_bg_deep", "ba_bg_gold")]
    for i, (m0, m1) in enumerate(kinds):
        a = i * math.pi / 2 + math.pi / 4
        ox, oz, oy = math.cos(a) * 25, math.sin(a) * 25, 30 + (i % 2) * 8
        o = r.bone(f"block{i}", b, (0, 34, 0), role="orbit")
        C(r, o, ox, oy, oz, 6, 6, 6, m0, rot=[12 * i, 20 + i * 25, 8], pivot=(ox, oy + 3, oz))
        if m1 == "ba_bg_grass":
            C(r, o, ox, oy + 5, oz, 6.2, 1.4, 6.2, m1, rot=[12 * i, 20 + i * 25, 8], pivot=(ox, oy + 3, oz))
        else:
            C(r, o, ox, oy + 2, oz, 6.3, 2.2, 2.4, m1, rot=[12 * i, 20 + i * 25, 8], pivot=(ox, oy + 3, oz))
        C(r, o, ox, oy + 2.3, oz, 6.5, 0.6, 0.6, "ba_bg_rune", rot=[12 * i, 110 + i * 25, 8], pivot=(ox, oy + 3, oz))
        C(r, o, ox * 0.86, oy - 3.5, oz * 0.86, 1.8, 1.8, 1.8, m0)          # crumbs falling from it
        C(r, o, ox * 1.08, oy - 1.8, oz * 1.08, 1.2, 1.2, 1.2, "ba_bg_cobble")
    return to_game(r)


# =============================================================== World 1, Toxic Jungle: Spore Queen
M("ba_sq_chitin", "34284a", "8ad040", "chitin")
M("ba_sq_chitin2", "243a20", "9ac83a", "chitin")
M("ba_sq_plate", "4e6a30", "b8e060", "chitin")
M("ba_sq_dark", "1a1424", "3a2a4a", "chitin")
M("ba_sq_cap", "8a1e4a", "d8ff5a", "spots")
M("ba_sq_cap2", "6a2a7a", "d8ff5a", "spots")
M("ba_sq_gill", "b8f04a", "e0ff8a", "glow", True)
M("ba_sq_stem", "d8ceb0", "efe6cc", "skin")
M("ba_sq_eye", "7aff3a", "c8ff7a", "crystal", True)
M("ba_sq_wing", "4e7a2a", "b8e050", "membrane")
M("ba_sq_wing2", "4a2e6a", "a880d8", "membrane")
M("ba_sq_vein", "1e2a14", "3a4a24", "chitin")
M("ba_sq_eyespot", "d8ff4a", "f4ffa0", "glow", True)
M("ba_sq_sac", "a8a060", "d8e080", "membrane")
M("ba_sq_pod", "8ac830", "e8ff7a", "spots")
M("ba_sq_fur", "d8d0b0", "fffbe8", "fur")
M("ba_sq_toxic", "9aff3a", "d0ff8a", "glow", True)
M("ba_sq_blade", "c8d8a0", "f0ffd0", "metal")


def mushroom(r, bone, x, y, z, stem_h, cap_w, cap_h, cap="ba_sq_cap", tilt=0):
    kw = {"rot": [0, 0, tilt], "pivot": (x, y, z)} if tilt else {}
    C(r, bone, x, y, z, max(0.8, cap_w * 0.28), stem_h + 0.3, max(0.8, cap_w * 0.28), "ba_sq_stem", **kw)
    C(r, bone, x, y + stem_h - 0.4, z, cap_w * 0.86, 0.5, cap_w * 0.86, "ba_sq_gill", **kw)
    C(r, bone, x, y + stem_h, z, cap_w, cap_h, cap_w, cap, **kw)
    if cap_w > 2.5:
        C(r, bone, x, y + stem_h + cap_h, z, cap_w * 0.6, cap_h * 0.5, cap_w * 0.6, cap, **kw)


def to_game(r):
    """The rigs here are authored in raw rotation math; GeckoLib (like Blockbench) inverts static X and Y
    rotations, so flip them once so that the game shows the authored pose."""
    for bn in r.bones:
        if "rotation" in bn:
            bn["rotation"] = [-bn["rotation"][0], -bn["rotation"][1], bn["rotation"][2]]
        for c in bn["cubes"]:
            if "rotation" in c:
                c["rotation"] = [-c["rotation"][0], -c["rotation"][1], c["rotation"][2]]
    return r


def scale_rig(r, f):
    """Scales a finished rig uniformly around the origin (feet stay on y = 0)."""
    for bn in r.bones:
        bn["pivot"] = [v * f for v in bn["pivot"]]
        for c in bn["cubes"]:
            c["origin"] = [round(v * f, 3) for v in c["origin"]]
            c["size"] = [round(v * f, 3) for v in c["size"]]
            if "pivot" in c:
                c["pivot"] = [v * f for v in c["pivot"]]
            if "inflate" in c:
                c["inflate"] *= f
    return r


def spore_queen():
    """A moth-mantis queen overgrown by her own fungus: a crown of glowing-gilled toadstools, huge faceted green
    eyes, feathered antennae, a pale fur ruff, four moth wings with toxic eye-spots, scythe forelimbs, six
    stilt legs, and a swollen egg-sac abdomen studded with glowing spore pods and mushrooms."""
    r = Rig("spore_queen")
    b = r.bone("body", None, (0, 18, 0), role="body")
    # ---- thorax and upper torso
    C(r, b, 0, 13, 0, 12, 11, 11, "ba_sq_chitin")
    C(r, b, 0, 22.5, 0, 13, 2, 12, "ba_sq_plate")                          # carapace rim
    C(r, b, 0, 15, -5.8, 8, 7, 1, "ba_sq_plate")                           # sternum plate
    C(r, b, 0, 24, -1, 9, 7, 8, "ba_sq_chitin2")                           # upper torso
    C(r, b, 0, 25, -5.2, 5, 5, 0.8, "ba_sq_plate")
    C(r, b, 0, 26.6, -5.7, 1.6, 1.6, 0.4, "ba_sq_toxic")                   # a throat gem of spores
    # fur ruff, the moth's collar, all round the neck
    C(r, b, 0, 30, -1, 13, 3, 11, "ba_sq_fur")
    C(r, b, 0, 29, -1, 11, 1.5, 9.5, "ba_sq_fur", inflate=0.4)
    # ---- head
    h = r.bone("head", b, (0, 32, -2), role="head")
    C(r, h, 0, 31.5, -4, 8, 6.5, 7, "ba_sq_chitin")
    C(r, h, 0, 31, -7.6, 5, 4, 2, "ba_sq_plate")                           # face plate / clypeus
    C(r, h, 0, 33.5, -8.4, 1.2, 3.5, 1, "ba_sq_dark")                       # central ridge
    for s in (1, -1):
        C(r, h, s * 3.8, 32.5, -5.5, 3.4, 4.6, 4.6, "ba_sq_eye")           # compound eyes bulging at the sides
        for j in range(3):
            C(r, h, s * 3.8 + s * 0.2, 33.2 + j * 1.3, -8.0, 0.5, 0.5, 0.4, "ba_sq_dark")  # facets
        C(r, h, s * 3.4, 34.2, -8.1, 1.2, 1.2, 0.4, "pupil")                # the dark pseudo-pupil
        C(r, h, s * 1.6, 36.6, -6.6, 1.6, 0.8, 1.6, "ba_sq_toxic")         # ocelli
        # feathered antennae sweeping back
        ant = r.bone(f"antenna_{'l' if s > 0 else 'r'}", h, (s * 1.8, 38, -5), role="tail")
        kw = {"rot": [-38, 0, -s * 30], "pivot": (s * 1.8, 38, -5)}
        r.cube(ant, (s * 1.8 - 0.4, 38, -5.4), (0.8, 9, 0.8), "ba_sq_dark", **kw)
        for k in range(5):
            yy = 39.5 + k * 1.6
            ln = 1.2 + 1.6 * math.sin(math.pi * (k + 0.5) / 5)
            r.cube(ant, (s * 1.8 - ln, yy, -5.3), (ln * 2, 0.4, 0.6), "ba_sq_wing", **kw)   # feathered pinnae
        r.cube(ant, (s * 1.8 - 0.5, 47, -5.5), (1, 1, 1), "ba_sq_toxic", **kw)
    # crown of toadstools
    mushroom(r, h, 0, 37.5, -3.5, 4.6, 4.6, 1.8, "ba_sq_cap")
    mushroom(r, h, -3.2, 37.6, -2.5, 2.6, 3.0, 1.2, "ba_sq_cap2", tilt=22)
    mushroom(r, h, 3.2, 37.6, -2.5, 2.8, 3.2, 1.2, "ba_sq_cap2", tilt=-22)
    mushroom(r, h, 1.6, 37.4, -0.4, 1.4, 1.8, 0.8, "ba_sq_cap")
    mushroom(r, h, -1.8, 37.4, -0.2, 1.0, 1.4, 0.7, "ba_sq_cap")
    C(r, h, 0, 37.2, -3.5, 7.4, 0.8, 5, "ba_sq_plate")                     # crown band
    for x in (-3, 0, 3):
        C(r, h, x, 37.6, -6.2, 0.8, 0.8, 0.6, "ba_sq_eyespot")             # glowing stones on the band
    # mouthparts: the jaw drops open, mandibles curve in
    jaw = r.bone("jaw", h, (0, 32, -6), role="jaw")
    C(r, jaw, 0, 29.6, -9.6, 3.6, 2.4, 3.6, "ba_sq_dark")
    for s in (1, -1):
        C(r, jaw, s * 2.4, 29.2, -10.4, 1.4, 2.6, 2.4, "ba_sq_plate", rot=[0, s * 20, 0], pivot=(s * 2, 30, -9))
        C(r, jaw, s * 1.3, 28.6, -11.6, 0.9, 1.6, 0.9, "ba_sq_blade")       # mandible hooks
        C(r, jaw, s * 1.0, 27.0, -9.4, 0.6, 2.6, 0.6, "ba_sq_chitin2")      # palps
    C(r, jaw, 0, 29.0, -11.0, 1.2, 0.6, 0.6, "ba_sq_toxic")                # a drop of venom
    # ---- egg-sac abdomen: three segments curving back
    par = b
    for i, (w, hh, d, y, z) in enumerate(((13, 11, 9, 13, 5), (16, 13, 10, 11.5, 13), (12, 10, 8, 12.5, 22))):
        seg = r.bone(f"abdomen{i}", par, (0, y + hh / 2, z), role="tail")
        C(r, seg, 0, y + 1, z + d / 2, w, hh - 2, d, "ba_sq_sac" if i == 1 else "ba_sq_chitin")
        C(r, seg, 0, y, z + d / 2, w - 2.4, hh, d - 1, "ba_sq_sac" if i == 1 else "ba_sq_chitin")
        C(r, seg, 0, y + hh - 0.5, z + d / 2, w - 2, 1.4, d - 1, "ba_sq_plate")     # dorsal plate
        C(r, seg, 0, y - 0.4, z + d / 2, w - 3, 1, d - 2, "ba_sq_dark")              # belly
        par = seg
    sac = "abdomen1"
    for (x, y, z, s) in ((-5, 19, 11, 2.4), (4.6, 20, 15, 2.8), (-2, 24, 17, 2.0), (6.8, 15, 11, 2.0), (-7.2, 14.5, 16, 2.2), (1.5, 23.8, 11, 1.6)):
        C(r, sac, x, y, z, s, s, s, "ba_sq_pod")                            # spore pods
    mushroom(r, sac, -3.5, 24.5, 14, 2.2, 3.0, 1.2, "ba_sq_cap")
    mushroom(r, sac, 4.5, 24.5, 18, 1.4, 2.2, 1.0, "ba_sq_cap2", tilt=-20)
    mushroom(r, "abdomen2", 0, 22.5, 25, 1.6, 2.6, 1.1, "ba_sq_cap", tilt=10)
    C(r, "abdomen2", 0, 13.5, 30, 3, 3, 1.6, "ba_sq_dark")                 # ovipositor
    C(r, "abdomen2", 0, 14.2, 31.2, 1.4, 1.4, 1, "ba_sq_toxic")
    # ---- four moth wings spread behind her like a royal fan (vertical planes facing forward)
    for s, side in ((1, "l"), (-1, "r")):
        for k, (y, z, ln, ht, lift, m, m2) in enumerate(((25, 6.5, 21, 14, 24, "ba_sq_wing", "ba_sq_wing2"),
                                                          (22, 7.5, 15, 10, -26, "ba_sq_wing2", "ba_sq_wing"))):
            piv = (s * 4, y, z)
            w = r.bone(f"wing_{side}{k}", b, piv, role=f"wing_{side}")
            rot = {"rot": [0, s * 14, s * lift], "pivot": piv}
            up = 1 if k == 0 else -1

            def wc(fx0, fx1, fy0, fy1, dz, th, mat):
                """A wing patch over fraction fx0..fx1 of the span and fy0..fy1 of the height."""
                xa, xb = s * 4 + s * ln * fx0, s * 4 + s * ln * fx1
                ya, yb = y + up * ht * fy0, y + up * ht * fy1
                r.cube(w, (min(xa, xb), min(ya, yb), z + dz), (abs(xb - xa), abs(yb - ya), th), mat, **rot)
            wc(0, 1, -0.15, 0.7, 0, 0.5, m)                                   # main membrane
            wc(0.3, 0.95, 0.7, 1.0, 0, 0.5, m)                               # rounded outer lobe
            wc(0.84, 1, -0.15, 0.7, -0.05, 0.6, m2)                          # banded tip
            wc(0, 0.92, 0.66, 0.74, -0.1, 0.6, "ba_sq_vein")                 # costal vein
            wc(0.05, 0.84, 0.25, 0.3, -0.1, 0.6, "ba_sq_vein")
            wc(0.5, 0.82, 0.12, 0.64, -0.15, 0.6, "ba_sq_dark")              # eye-spot ring
            wc(0.55, 0.77, 0.2, 0.56, -0.25, 0.6, "ba_sq_eyespot")
            wc(0.62, 0.7, 0.3, 0.46, -0.35, 0.6, "ba_sq_dark")               # its pupil
    # ---- scythe forelimbs
    for s, side in ((1, "l"), (-1, "r")):
        a0, a1 = r.limb(f"arm_{side}", b, (s * 6, 26, -4), [(3, 8, 3), (2.4, 8, 2.4)], "ba_sq_chitin2", "ba_sq_plate", role=f"arm_{side}")
        r.bones[[x["name"] for x in r.bones].index(a0)]["rotation"] = [30, 0, -s * 10]
        r.bones[[x["name"] for x in r.bones].index(a1)]["rotation"] = [-45, 0, 0]
        C(r, a0, s * 6, 24, -4, 4, 3, 4, "ba_sq_plate")                     # coxa
        C(r, a1, s * 6, 6, -5.2, 1.0, 12, 2.2, "ba_sq_blade")              # the scythe along the forearm
        C(r, a1, s * 6, 5, -7.2, 1.0, 2, 4, "ba_sq_blade")                 # hooked tip
        for k in range(3):
            C(r, a1, s * 6, 12 + k * 2.6, -3.0, 0.6, 0.8, 1.6, "ba_sq_dark")  # inner spines
    # ---- six stilt legs: femur up and out to a high knee, tibia down to the ground
    for s, side in ((1, "l"), (-1, "r")):
        for i, (z, yaw) in enumerate(((-4, 30), (1, 0), (6, -30))):
            hip = (s * 6, 16, z)
            nm = r.bone(f"insect_{side}{i}", b, hip, rot=[0, s * yaw, 0], role=f"insect_{side}{i}")
            ang = 45
            r.cube(nm, (s * 6 - (0 if s > 0 else 12), 15.1, z - 0.9), (12, 1.8, 1.8), "ba_sq_chitin", rot=[0, 0, s * ang], pivot=hip)
            r.cube(nm, (s * 6 - (0 if s > 0 else 4), 15.3, z - 1.2), (4, 1.4, 2.4), "ba_sq_plate", rot=[0, 0, s * ang], pivot=hip)
            knee = (s * 14.5, 24.5, z)
            tib = r.bone(f"shin_{side}{i}", nm, knee)
            kw = {"rot": [0, 0, s * 9], "pivot": knee}
            r.cube(tib, (s * 14.5 - 0.7, 3, z - 0.7), (1.4, 22, 1.4), "ba_sq_chitin2", **kw)
            r.cube(tib, (s * 14.5 - 1.2, 23.2, z - 1.2), (2.4, 2.4, 2.4), "ba_sq_dark", **kw)   # knee
            r.cube(tib, (s * 14.5 - 0.45, 0.1, z - 0.45), (0.9, 3.5, 0.9), "ba_sq_blade", **kw)  # claw tip
    return to_game(scale_rig(r, 0.86))


# =============================================================== World 2, Giant Veins: Ash Titan
M("ba_at_basalt", "3a3230", "5c4e46", "blocks")
M("ba_at_basalt2", "4a3c34", "6a5446", "blocks")
M("ba_at_plate", "3e3634", "62564c", "metal")
M("ba_at_crack", "ff5a10", "ffa030", "vein", True)
M("ba_at_magma", "ff6a14", "ffb83a", "magma", True)
M("ba_at_core", "ffb020", "ffe070", "glow", True)
M("ba_at_eye", "ffd040", "ffe48a", "glow", True)
M("ba_at_iron", "44464e", "767a84", "metal")
M("ba_at_rust", "6a3a22", "a8602e", "metal")
M("ba_at_obsidian", "1a1428", "4a3a6a", "crystal")
M("ba_at_gold", "d8a030", "f8e080", "crystal")
M("ba_at_copper", "b8603a", "e8a070", "crystal")
M("ba_at_smoke", "4a4442", "7a726c", "cloud")
M("ba_at_wood", "5a3a22", "7a5232", "bark")
M("ba_at_char", "1a1414", "2e2422", "skin")
M("ba_at_tooth", "2a2224", "ff8a30", "metal")


def ash_titan():
    """A hunched colossus of cooled basalt plates riveted over a living forge: lava seams in every joint, a
    furnace door in the chest with a grate over the molten heart, two smoking chimneys on the back, ore
    crystals bursting from the shoulders, obsidian horns on a crucible helmet with a burning visor slit,
    a molten jaw, and a mine-beam hammer with an anvil head dragging at its side."""
    r = Rig("ash_titan")
    # ---- legs
    for side, s in (("l", 1), ("r", -1)):
        hx = s * 8.5
        l0 = r.bone(f"leg_{side}0", None, (hx, 25, 0), role=f"leg_{side}0")
        C(r, l0, hx, 12.5, 0, 10, 13, 10, "ba_at_basalt")
        C(r, l0, hx + s * 0.5, 18, -0.5, 11, 6, 11, "ba_at_plate")            # thigh plate
        C(r, l0, hx + s * 5.6, 14, -1, 0.6, 9, 0.6, "ba_at_crack")            # seam
        C(r, l0, hx, 13, -5.3, 6, 0.6, 0.6, "ba_at_crack")
        l1 = r.bone(f"leg_{side}1", l0, (hx, 13.5, 0), role=f"leg_{side}1")
        C(r, l1, hx, 3, 0, 11, 11, 11, "ba_at_basalt2")
        C(r, l1, hx, 11, -1, 9, 4, 1.6, "ba_at_magma")                        # molten knee
        C(r, l1, hx, 10.5, -1.6, 10, 1, 2, "ba_at_iron")
        C(r, l1, hx, 0, -1.5, 14, 4, 15, "ba_at_basalt")                      # foot
        for i in range(3):
            C(r, l1, hx - 4.4 + i * 4.4, 0, -9.6, 3, 2.6, 2.8, "ba_at_obsidian")  # obsidian toe claws
        C(r, l1, hx, 4, -6, 12, 0.6, 0.6, "ba_at_crack")
        C(r, l1, hx - s * 5.8, 5, 0, 0.6, 6, 6, "ba_at_crack")
    # ---- trunk
    b = r.bone("body", None, (0, 25, 0), role="body")
    C(r, b, 0, 20, 0, 21, 8, 12, "ba_at_basalt")                               # pelvis
    C(r, b, 0, 22, -6.4, 12, 6, 1.2, "ba_at_plate")                           # loin plate
    C(r, b, 0, 27.5, 0, 19, 8.5, 12, "ba_at_basalt2")                          # belly
    C(r, b, 0, 29, -6.4, 14, 0.8, 0.8, "ba_at_crack")
    C(r, b, 0, 27.5, 0, 22, 2.2, 13.5, "ba_at_iron")                           # iron girdle
    C(r, b, 0, 26.8, -7.2, 4, 3.6, 1, "ba_at_rust")                            # buckle
    C(r, b, 0, 35, 0.5, 34, 15, 18, "ba_at_basalt")                            # barrel chest
    C(r, b, 0, 47.5, 3.5, 28, 8, 14, "ba_at_basalt2")                          # hunch
    C(r, b, 0, 44, -0.5, 30, 4, 19, "ba_at_plate")                             # collar plate
    # furnace door with the heart behind a grate
    C(r, b, 0, 35.5, -9.2, 14, 12, 1.4, "ba_at_iron")
    C(r, b, 0, 37, -9.4, 10, 9, 1.2, "ba_at_char")
    core = r.bone("heart", b, (0, 41.5, -9), role="pulse")
    C(r, core, 0, 37.4, -10.0, 9, 8.4, 1.4, "ba_at_core")
    C(r, core, 0, 39.2, -10.4, 5, 4.6, 1.2, "ba_at_magma")
    for x in (-3.6, -1.2, 1.2, 3.6):
        C(r, b, x, 36.6, -10.3, 0.8, 9.8, 0.8, "ba_at_iron")                   # grate bars
    C(r, b, 0, 41.8, -10.3, 10.6, 0.8, 0.8, "ba_at_iron")
    rivets(r, b, [(x, y, -10.0) for x in (-6.2, 6.2) for y in (36.5, 41.5, 46.5)], "ba_at_rust", 1.0)
    C(r, b, 7.8, 41, -9.8, 1.6, 3, 1.2, "ba_at_rust")                          # hinge
    # cracks spreading from the furnace across the chest plates
    r.cube(b, (7.5, 45, -9.3), (8, 0.7, 0.6), "ba_at_crack", rot=[0, 0, -24], pivot=(7.5, 45, -9))
    r.cube(b, (-15.5, 38, -9.3), (8, 0.7, 0.6), "ba_at_crack", rot=[0, 0, 30], pivot=(-7.5, 38, -9))
    r.cube(b, (9, 35.5, -9.3), (0.7, 5, 0.6), "ba_at_crack")
    C(r, b, -11, 46, -9.4, 5, 3, 1.2, "ba_at_plate")                           # a riveted patch
    rivets(r, b, [(-12.8, 47.5, -10.1), (-9.2, 47.5, -10.1)], "ba_at_rust", 0.8)
    # back: chimneys, ore crystals, spine seam
    for s in (1, -1):
        C(r, b, s * 7, 48, 9, 4.4, 12, 4.4, "ba_at_iron")
        C(r, b, s * 7, 59, 9, 5.4, 1.6, 5.4, "ba_at_rust")
        C(r, b, s * 7, 59.4, 9, 3.2, 1.0, 3.2, "ba_at_magma")                 # embers in the stack
        C(r, b, s * 7 + s * 0.8, 61.2, 9.6, 3.4, 2.4, 3.4, "ba_at_smoke")     # a puff of ash
        C(r, b, s * 7 + s * 1.8, 63.4, 10.4, 2.2, 1.8, 2.2, "ba_at_smoke")
        C(r, b, s * 7, 52, 6.6, 6, 1, 1, "ba_at_rust")                        # bracket
    C(r, b, 0, 30, 9.6, 1.2, 20, 0.8, "ba_at_crack")
    for (x, y, z, w, hh, m, rz) in ((-3, 49, 8, 3, 7, "ba_at_obsidian", 18), (2.5, 50, 9, 2.4, 6, "ba_at_gold", -14),
                                     (0, 42, 10, 2.4, 5, "ba_at_copper", 8)):
        C(r, b, x, y, z, w, hh, w, m, rot=[20, 0, rz], pivot=(x, y, z))
    # ---- head: crucible helmet pushed forward between the shoulders
    h = r.bone("head", b, (0, 48, -6), role="head")
    C(r, h, 0, 47, -9, 10, 9, 9, "ba_at_basalt2")
    C(r, h, 0, 52.5, -9, 12, 4.5, 10.5, "ba_at_iron")                           # crucible helmet
    C(r, h, 0, 56.6, -9, 10.5, 1.2, 9, "ba_at_rust")                            # its rim
    C(r, h, 0, 57.2, -9, 7, 0.6, 5.4, "ba_at_magma")                            # molten metal in the crucible
    C(r, h, 0, 51, -14.6, 9.4, 1.8, 0.6, "ba_at_char")                         # visor slit
    eye(r, h, -2.5, 51.9, -14.9, 2.6, 1.0, "ba_at_eye", None, "ba_at_char")
    eye(r, h, 2.5, 51.9, -14.9, 2.6, 1.0, "ba_at_eye", None, "ba_at_char")
    C(r, h, 0, 52.8, -14.7, 1.4, 3.6, 0.8, "ba_at_iron")                       # nose guard
    rivets(r, h, [(x, 55.6, -14.5) for x in (-4.5, -1.5, 1.5, 4.5)], "ba_at_rust", 0.8)
    for s in (1, -1):                                                          # obsidian horns
        C(r, h, s * 6.5, 52, -9, 3, 3, 3, "ba_at_obsidian", rot=[0, 0, -s * 30], pivot=(s * 6, 53.5, -9))
        r.cube(h, (s * 8.2 - 1, 54, -10), (2, 5, 2), "ba_at_obsidian", rot=[15, 0, -s * 35], pivot=(s * 8.2, 54, -9))
        r.cube(h, (s * 11 - 0.6, 57, -9.8), (1.2, 3.4, 1.2), "ba_at_obsidian", rot=[15, 0, -s * 10], pivot=(s * 11, 57, -9.2))
        C(r, h, s * 4.6, 47.5, -13.9, 0.6, 3.4, 0.6, "ba_at_crack")             # cheek seams
    jaw = r.bone("jaw", h, (0, 48.5, -6), role="jaw")
    C(r, jaw, 0, 44.6, -10.3, 9, 4, 8.5, "ba_at_basalt")
    C(r, jaw, 0, 47.6, -10.3, 7.6, 1.4, 7, "ba_at_magma")                      # molten mouth
    teeth(r, jaw, -3.6, 3.6, 48.4, -14.0, 5, 1.6, "ba_at_tooth", w=1.0, d=0.9)
    C(r, jaw, -2, 42.2, -14, 0.8, 2.6, 0.8, "ba_at_magma")                     # lava drool
    C(r, jaw, -2, 41.6, -14, 1.2, 0.8, 1.2, "ba_at_magma")
    teeth(r, h, -3.8, 3.8, 49.4, -14.2, 4, 1.4, "ba_at_tooth", down=True, w=1.1, d=0.9)
    # ---- arms
    for side, s in (("l", 1), ("r", -1)):
        sx = s * 21
        a0, a1 = r.limb(f"arm_{side}", b, (sx, 46, 0), [(9, 13, 9), (11, 13, 11)], "ba_at_basalt2", "ba_at_magma", role=f"arm_{side}", splay=s * 10)
        C(r, a0, sx + s * 0.5, 41.5, 0, 13, 10, 14, "ba_at_basalt")            # boulder pauldron
        C(r, a0, sx + s * 0.5, 47.5, 0, 11, 2, 12, "ba_at_plate")
        C(r, a0, sx + s * 4, 49, -2, 2.6, 6, 2.6, "ba_at_gold" if s > 0 else "ba_at_copper", rot=[0, 0, -s * 25], pivot=(sx + s * 4, 49, -2))
        C(r, a0, sx + s * 1, 49, 3, 2.0, 4.5, 2.0, "ba_at_copper" if s > 0 else "ba_at_gold", rot=[-15, 0, -s * 10], pivot=(sx + s, 49, 3))
        C(r, a0, sx - s * 2, 49, -3.5, 1.6, 3, 1.6, "ba_at_obsidian")
        C(r, a0, sx + s * 6.8, 43, -2, 0.6, 6, 0.6, "ba_at_crack")
        C(r, a1, sx, 26, 0, 12, 2.2, 12, "ba_at_iron")                         # forearm bands
        C(r, a1, sx, 21.5, 0, 12, 2.2, 12, "ba_at_iron")
        rivets(r, a1, [(sx + s * 6.2, 27.1, -3), (sx + s * 6.2, 22.6, -3), (sx + s * 6.2, 27.1, 3)], "ba_at_rust", 0.9)
        C(r, a1, sx, 11, -0.5, 13, 9, 12.5, "ba_at_basalt")                    # fist
        for i in range(4):
            C(r, a1, sx - 4.5 + i * 3, 11.5, -7.2, 2.6, 3, 1.6, "ba_at_plate")   # knuckles
            C(r, a1, sx - 4.5 + i * 3, 12.2, -7.6, 1.6, 1.4, 0.8, "ba_at_magma") # glowing knuckle seams
        C(r, a1, sx + s * 6.8, 13, -2, 1.2, 4, 3.6, "ba_at_basalt2")           # thumb
    # the hammer: a mine-beam handle gripped in the right fist, head swung forward onto the ground, an anvil
    # block with iron straps whose striking faces still glow from the last blow
    hm = r.bone("hammer", "arm_r1", (-21, 15, -0.5), rot=[48, 0, 0])
    C(r, hm, -21, 3, -0.5, 3, 23, 3, "ba_at_wood")
    for y in (8, 24):
        C(r, hm, -21, y, -0.5, 3.6, 1.2, 3.6, "ba_at_iron")
    C(r, hm, -21, 25.5, -0.5, 4.4, 2.4, 4.4, "ba_at_rust")                     # pommel
    C(r, hm, -21.5, -7, -0.5, 18, 10, 10, "ba_at_basalt")                      # head
    C(r, hm, -21.5, -7.6, -0.5, 9, 11.2, 11.2, "ba_at_iron")                   # strap round it
    C(r, hm, -21.5, -5.5, -6.2, 6, 6, 1.0, "ba_at_magma")                      # molten rune on the strap
    C(r, hm, -31.2, -6, -0.5, 1.6, 8, 8, "ba_at_plate")                        # striking faces
    C(r, hm, -11.8, -6, -0.5, 1.6, 8, 8, "ba_at_plate")
    C(r, hm, -32.2, -4, -0.5, 0.6, 4, 4, "ba_at_magma")
    C(r, hm, -10.8, -4, -0.5, 0.6, 4, 4, "ba_at_magma")
    rivets(r, hm, [(x, y, -5.8) for x in (-27.5, -15.5) for y in (-4.5, 0.5)], "ba_at_rust", 1.0)
    C(r, hm, -21.5, 3, -0.5, 4, 1.5, 4, "ba_at_iron")                          # collar
    for c in r.bones[-1]["cubes"]:
        c["origin"][1] += 4.5                                                  # slide the head up the haft: it rests on the ground
    return to_game(r)


# =============================================================== World 3, Endless Dungeon: Grand Jailer
M("ba_gj_robe", "3a3446", "564e66", "cloth")
M("ba_gj_robe2", "4c4458", "6c6280", "cloth")
M("ba_gj_lining", "5a1e22", "8a3030", "cloth")
M("ba_gj_iron", "50525a", "868a94", "metal")
M("ba_gj_dark", "2a2a30", "46464e", "metal")
M("ba_gj_rust", "6a3e26", "a0623a", "metal")
M("ba_gj_gold", "c8962e", "f0d070", "metal")
M("ba_gj_mask", "7a7c84", "a8acb4", "metal")
M("ba_gj_soul", "4ad8e8", "9af4ff", "glow", True)
M("ba_gj_eye", "8ae8ff", "c8f8ff", "glow", True)
M("ba_gj_chain", "6a6e78", "a4a8b2", "chain")
M("ba_gj_void", "0c0c12", "16161e", "skin")
M("ba_gj_bone", "c8c0a8", "e0d8c4", "skin")


def padlock(r, bone, x, y, z, s=1.0, m="ba_gj_iron", kw=None):
    kw = kw or {}
    C(r, bone, x, y, z, 2.4 * s, 2.2 * s, 1.0 * s, m, **kw)                 # body
    C(r, bone, x - 0.8 * s, y + 2.2 * s, z, 0.5 * s, 1.4 * s, 0.5 * s, "ba_gj_dark", **kw)   # shackle
    C(r, bone, x + 0.8 * s, y + 2.2 * s, z, 0.5 * s, 1.4 * s, 0.5 * s, "ba_gj_dark", **kw)
    C(r, bone, x, y + 3.1 * s, z, 2.1 * s, 0.5 * s, 0.5 * s, "ba_gj_dark", **kw)
    C(r, bone, x, y + 0.6 * s, z - 0.5 * s, 0.5 * s, 0.9 * s, 0.2, "ba_gj_void", **kw)   # keyhole


def key(r, bone, x, ytop, z, ln=3.0, m="ba_gj_gold"):
    C(r, bone, x, ytop - 1.6, z, 1.6, 1.6, 0.5, m)                           # bow
    C(r, bone, x, ytop - 1.6 - ln, z, 0.5, ln, 0.5, m)                         # shank
    C(r, bone, x + 0.5, ytop - 1.4 - ln, z, 0.8, 0.9, 0.4, m)                  # bit


def grand_jailer():
    """A towering warden whose ribcage is an iron cell with a prisoner's soul clinging to its bars: a deep
    hood over an iron mask pierced by a glowing keyhole, a crown of cell bars, a gorget shut with a padlock,
    a key-staff taller than a man, a ring of keys at the belt, a lantern of trapped light, chains dragging
    from the left hand, padlocks on the tattered hem and keys circling it."""
    r = Rig("grand_jailer")
    b = r.bone("body", None, (0, 22, 0), role="body")
    # ---- robe to the ground, in two swinging tiers
    r0 = r.bone("robe0", b, (0, 22, 0), role="cape")
    C(r, r0, 0, 10, 0.5, 15, 12.5, 12, "ba_gj_robe")
    C(r, r0, 0, 10, -5.7, 4, 12.5, 0.6, "ba_gj_lining")                        # red lining at the parting
    C(r, r0, 0, 16, 0.5, 15.6, 1.4, 12.6, "ba_gj_chain")                       # chain wrapped round the robe
    r1 = r.bone("robe1", r0, (0, 11, 0), role="cape")
    C(r, r1, 0, 1.5, 0.5, 18, 10, 15, "ba_gj_robe")
    C(r, r1, 0, 1.5, -7.1, 5, 10, 0.6, "ba_gj_lining")
    for i, x in enumerate((-7.5, -4, 3.5, 7.5)):
        C(r, r1, x, 0, -6.6, 2.6, 2 + (i % 2), 1.2, "ba_gj_robe2")             # ragged hem strips
    C(r, r1, 0, 0, 1, 21, 3, 17, "ba_gj_robe2")                                # flared hem
    C(r, r1, 0, 2.6, 1, 21.4, 0.8, 17.4, "ba_gj_gold")                         # gold trim
    padlock(r, r1, -6.2, 3, -7.6, 1.0)
    padlock(r, r1, 5.8, 4.5, -7.6, 0.8, "ba_gj_rust")
    # ---- belt, key ring, lantern
    C(r, b, 0, 21, 0.5, 15, 3, 12.5, "ba_gj_dark")
    C(r, b, 0, 21.2, -6, 3, 2.6, 1, "ba_gj_gold")                              # buckle
    C(r, b, -5, 18.2, -6.6, 3.6, 0.6, 0.5, "ba_gj_gold")                       # the key ring
    C(r, b, -5, 15, -6.6, 3.6, 0.6, 0.5, "ba_gj_gold")
    C(r, b, -6.6, 15, -6.6, 0.6, 3.8, 0.5, "ba_gj_gold")
    C(r, b, -3.4, 15, -6.6, 0.6, 3.8, 0.5, "ba_gj_gold")
    for i, x in enumerate((-6.4, -5, -3.6)):
        key(r, b, x, 16 - i * 0.4, -7.2, 2.6 + i * 0.5, "ba_gj_gold" if i != 1 else "ba_gj_iron")
    lan = r.bone("lantern", b, (5.5, 21, -5), role="chain")
    C(r, lan, 5.5, 17.5, -5, 0.5, 3.5, 0.5, "ba_gj_chain")
    C(r, lan, 5.5, 16.6, -5, 3.4, 1, 3.4, "ba_gj_dark")
    C(r, lan, 5.5, 12.4, -5, 2.6, 4.2, 2.6, "ba_gj_soul")
    for dx in (-1.4, 1.4):
        for dz in (-1.4, 1.4):
            C(r, lan, 5.5 + dx, 12.2, -5 + dz, 0.5, 4.6, 0.5, "ba_gj_dark")
    C(r, lan, 5.5, 11.6, -5, 3.4, 0.8, 3.4, "ba_gj_dark")
    # ---- the cell: a ribcage of bars around a captive soul
    C(r, b, 0, 23.5, 0.5, 15, 1.6, 12, "ba_gj_iron")                           # floor plate
    C(r, b, 0, 35, 0.5, 15, 1.6, 12, "ba_gj_iron")                             # ceiling plate
    C(r, b, 0, 25, 4.4, 13, 10, 3.6, "ba_gj_void")                             # dark back of the cell
    C(r, b, 0, 25, 0.5, 13, 0.6, 7, "ba_gj_void")
    for x in (-6, -3, 0, 3, 6):
        C(r, b, x, 25, -5.0, 1, 10.2, 1, "ba_gj_iron")                        # front bars
    for s in (1, -1):
        for z in (-1.5, 2.5):
            C(r, b, s * 6.8, 25, z, 1, 10.2, 1, "ba_gj_iron")                 # side bars
    C(r, b, 0, 29.8, -5.1, 14, 0.8, 1.1, "ba_gj_dark")                         # cross band
    C(r, b, 0, 23.5, 6.6, 15, 13, 1.2, "ba_gj_robe")                          # coat back over the cell
    sl = r.bone("soul", b, (0, 29, 0.5), role="pulse")
    C(r, sl, 0, 25.6, 1, 4.2, 4.4, 3.6, "ba_gj_soul")                         # the huddled prisoner
    C(r, sl, 0.6, 29.6, 0.2, 3, 3, 3, "ba_gj_soul")                           # its head
    C(r, sl, -0.1, 30.8, -1.35, 0.6, 0.8, 0.2, "ba_gj_void")                  # hollow eyes
    C(r, sl, 1.4, 30.8, -1.35, 0.6, 0.8, 0.2, "ba_gj_void")
    C(r, sl, -1.6, 28.6, -3.6, 1.0, 1.2, 4, "ba_gj_soul")                     # arms reaching to the bars
    C(r, sl, 2.0, 27.8, -3.6, 1.0, 1.2, 4, "ba_gj_soul")
    # ---- mantle, gorget and its padlock
    C(r, b, 0, 36, 0.8, 21, 4.5, 13.5, "ba_gj_robe2")
    C(r, b, 0, 35.2, 6.8, 19, 3, 1.6, "ba_gj_robe2")
    C(r, b, 0, 39, -0.5, 12, 3.2, 10.5, "ba_gj_iron")                          # gorget
    C(r, b, 0, 39.4, -0.5, 12.6, 0.7, 11.1, "ba_gj_dark")
    padlock(r, b, 0, 36.2, -6.4, 1.2)
    C(r, b, 0, 35.6, 0.8, 21.6, 0.8, 14.1, "ba_gj_gold")                      # gold edge of the mantle
    for s in (1, -1):
        C(r, b, s * 9.6, 39.6, 0.8, 5, 1.6, 7, "ba_gj_iron")                  # shoulder plates
        for z in (-1.5, 1, 3.5):
            C(r, b, s * 11.2, 40.5, z, 0.8, 3.2 - abs(z - 1) * 0.3, 0.8, "ba_gj_dark")  # bars rising from the shoulders
    # chains hanging from the shoulder blades
    for s, ln in ((1, 5),):
        par = b
        for i in range(ln):
            nm = r.bone(f"backchain_{'l' if s > 0 else 'r'}{i}", par, (s * 5, 37 - i * 2.2, 7.6), role="chain" if i == 0 else None)
            C(r, nm, s * 5, 35 - i * 2.2, 7.6, 0.6 if i % 2 else 1.4, 2.4, 1.4 if i % 2 else 0.6, "ba_gj_chain")
            par = nm
    # ---- head: deep hood, iron mask with a keyhole, crown of bars
    h = r.bone("head", b, (0, 41, -0.5), role="head")
    C(r, h, 0, 40.5, 0, 11, 11, 10.5, "ba_gj_robe")                            # hood
    C(r, h, 0, 50.5, 1.5, 7, 2, 6, "ba_gj_robe")                               # hood peak
    C(r, h, 0, 49.4, -6.4, 6, 1.6, 2, "ba_gj_robe2")                           # brim jutting over the mask
    C(r, h, 0, 40.5, -5.4, 11.4, 2, 1, "ba_gj_robe2")                          # hood rim, bottom
    for s in (1, -1):
        C(r, h, s * 5.0, 40.5, -5.4, 1.4, 10.4, 1.2, "ba_gj_robe2")           # hood rim, sides
    C(r, h, 0, 49.6, -5.4, 11.4, 1.6, 1.2, "ba_gj_robe2")                      # hood rim, top
    C(r, h, 0, 42.5, -5.0, 8.6, 7.4, 0.6, "ba_gj_void")                        # darkness inside the hood
    C(r, h, 0, 43.4, -5.3, 6.4, 6, 0.6, "ba_gj_mask")                          # the iron mask
    C(r, h, 0, 48.5, -5.3, 7, 1, 0.8, "ba_gj_dark")                            # its brow bar
    eye(r, h, -1.8, 47.6, -5.4, 1.6, 0.7, "ba_gj_eye", None, "ba_gj_void")
    eye(r, h, 1.8, 47.6, -5.4, 1.6, 0.7, "ba_gj_eye", None, "ba_gj_void")
    C(r, h, 0, 44.8, -5.8, 1.6, 1.6, 0.4, "ba_gj_soul")                       # the keyhole, glowing
    C(r, h, 0, 43.4, -5.8, 0.7, 1.6, 0.4, "ba_gj_soul")
    rivets(r, h, [(-2.6, 44.2, -5.7), (2.6, 44.2, -5.7), (-2.6, 46.3, -5.7), (2.6, 46.3, -5.7)], "ba_gj_dark", 0.5)
    C(r, h, 0, 51.2, 0, 10, 1, 8, "ba_gj_dark")                                # crown band
    for i, x in enumerate((-4, -2, 0, 2, 4)):
        C(r, h, x, 52, -3.5, 0.8, 2.6 + (1.4 if i == 2 else 0), 0.8, "ba_gj_iron")  # crown of cell bars
        C(r, h, x, 52, 3.5, 0.8, 2.4, 0.8, "ba_gj_iron")
    C(r, h, 0, 54.4, -3.5, 1.6, 1.6, 0.6, "ba_gj_soul")                       # soul gem on the crown
    jaw = r.bone("jaw", h, (0, 43.4, -3), role="jaw")
    C(r, jaw, 0, 41.2, -5.4, 5.4, 2.4, 1, "ba_gj_mask")                        # hinged chin of the mask
    C(r, jaw, 0, 41.6, -5.6, 4.0, 0.5, 0.4, "ba_gj_dark")                      # grille slots
    C(r, jaw, 0, 42.6, -5.6, 4.0, 0.5, 0.4, "ba_gj_dark")
    # ---- arms: long, gaunt, shackled
    for side, s in (("l", 1), ("r", -1)):
        sx = s * 11.5
        a0, a1 = r.limb(f"arm_{side}", b, (sx, 39, 0.5), [(4.4, 11, 4.4), (3.6, 11, 3.6)], "ba_gj_robe2", "ba_gj_iron", role=f"arm_{side}", splay=s * 6)
        C(r, a0, sx, 34, 0.5, 6.4, 6.4, 6.4, "ba_gj_robe")                     # sleeve top
        C(r, a1, sx, 20, 0.5, 5.4, 4, 5.4, "ba_gj_robe")                       # flared cuff
        C(r, a1, sx, 23, 0.5, 5.8, 1.4, 5.8, "ba_gj_iron")                     # shackle on the wrist
        C(r, a1, sx, 15.5, 0.5, 3.2, 4.6, 3.2, "ba_gj_bone")                   # bony hand
        for k in range(3):
            C(r, a1, sx - 1.0 + k, 14, -1.4, 0.6, 2.2, 0.6, "ba_gj_bone")     # fingers
    # key-staff in the right hand
    ks = r.bone("keystaff", "arm_r1", (-11.5, 17, -2))
    C(r, ks, -11.5, 2, -2.2, 1.4, 41, 1.4, "ba_gj_gold")                       # shank
    C(r, ks, -11.5, 39, -2.2, 6, 1.2, 1.4, "ba_gj_gold")                       # the bow, a ring
    C(r, ks, -11.5, 45, -2.2, 6, 1.2, 1.4, "ba_gj_gold")
    C(r, ks, -14, 39, -2.2, 1.2, 7.2, 1.4, "ba_gj_gold")
    C(r, ks, -9, 39, -2.2, 1.2, 7.2, 1.4, "ba_gj_gold")
    C(r, ks, -11.5, 41, -2.2, 2.2, 2.2, 0.8, "ba_gj_soul")                     # its gem
    C(r, ks, -11.5, 37.6, -2.2, 3, 1, 2, "ba_gj_gold")                         # collar
    C(r, ks, -9.6, 4, -2.2, 2.4, 1.6, 1, "ba_gj_gold")                         # the bit, cut like a cell key
    C(r, ks, -9.8, 6.4, -2.2, 2.0, 1.2, 1, "ba_gj_gold")
    C(r, ks, -9.4, 2, -2.2, 2.8, 1.0, 1, "ba_gj_gold")
    C(r, ks, -11.5, 9, -2.2, 2.2, 0.8, 2.2, "ba_gj_dark")
    # chain dragged from the left hand, ending in an open shackle
    par = "arm_l1"
    for i in range(6):
        nm = r.bone(f"chain{i}", par, (11.5, 15 - i * 2.4, 0.5), role="chain")
        C(r, nm, 11.5, 12.4 - i * 2.4, 0.5, 0.6 if i % 2 else 1.5, 2.8, 1.5 if i % 2 else 0.6, "ba_gj_chain")
        par = nm
    C(r, par, 11.5, -1.0, 0.5, 3, 0.7, 3, "ba_gj_iron")
    C(r, par, 10.3, -1.0, 0.5, 0.6, 1.6, 3, "ba_gj_iron")
    C(r, par, 12.7, -1.0, 0.5, 0.6, 1.6, 3, "ba_gj_iron")
    # ---- keys and padlocks circling it
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        ox, oz = math.cos(a) * 16, math.sin(a) * 16
        o = r.bone(f"orbit{i}", b, (0, 30, 0), role="orbit")
        if i % 2 == 0:
            key(r, o, ox, 34 + i, oz, 3.4)
        else:
            padlock(r, o, ox, 28 + i, oz, 1.1, "ba_gj_gold")
    return to_game(scale_rig(r, 0.92))


# =============================================================== World 4, Storm Archipelago: Storm King
M("ba_sk_skin", "8aa2bc", "aec4da", "skin")
M("ba_sk_armor", "2e4e82", "6a94cc", "metal")
M("ba_sk_silver", "6a80a8", "a8c0e0", "metal")
M("ba_sk_gold", "d6a23e", "f6d68a", "metal")
M("ba_sk_cloud", "f2f6fb", "ffffff", "cloud")
M("ba_sk_cloud2", "9ca8bc", "c4cede", "cloud")
M("ba_sk_storm", "4a5468", "687288", "cloud")
M("ba_sk_bolt", "ffe03a", "fff08a", "glow", True)
M("ba_sk_eye", "ffe84a", "fff4a0", "glow", True)
M("ba_sk_gem", "5ac8ff", "a8e8ff", "glow", True)
M("ba_sk_cape", "1c3666", "3a64a4", "cloth")
M("ba_sk_lining", "6a2a8a", "9a5ac0", "cloth")
M("ba_sk_feather", "e2eaf6", "ffffff", "cloud")
M("ba_sk_feather2", "7898c8", "b0c8ec", "scales")


def bolt(r, bone, x, y, z, s=1.0, m="ba_sk_bolt", d=0.5, down=True):
    """A small zig-zag lightning bolt of three strokes, hanging from (x, y)."""
    k = -1 if down else 1
    C(r, bone, x, y + (k * 2.2 * s if down else 0), z, 0.6 * s, 2.2 * s, d, m)
    C(r, bone, x + 0.7 * s, y + k * 2.2 * s - (0.6 * s if down else 0), z, 2.0 * s, 0.6 * s, d, m)
    C(r, bone, x + 1.4 * s, y + (k * 4.6 * s if down else 2.2 * s), z, 0.6 * s, 2.4 * s, d, m)


def storm_king():
    """A sky monarch who rides his own tornado: a funnel of storm cloud for legs with cloudlets circling it,
    blue and silver plate with a lightning emblem, a beard and mane of white cloud, burning yellow eyes, a
    gold crown of lightning spikes, feathered cloud wings, a cape hemmed with lightning, a trident of
    living bolts in one hand and a crackling storm orb in the other."""
    r = Rig("storm_king")
    b = r.bone("body", None, (0, 25, 0), role="body")
    # ---- the tornado he rides
    par = b
    for i, (y0, y1, w, dx) in enumerate(((16, 25, 13, 0), (9, 16.5, 9.5, 1.2), (3.5, 9.5, 6.5, -0.6), (0, 4, 3.5, 0.8))):
        t = r.bone(f"funnel{i}", par, (dx * 0.5, y1, 0), role="tail")
        C(r, t, dx, y0, 0, w, y1 - y0, w * 0.8, "ba_sk_storm")
        C(r, t, dx + w * 0.32, y0 + (y1 - y0) * 0.5, -w * 0.2, w * 0.55, (y1 - y0) * 0.4, w * 0.55, "ba_sk_cloud2")   # wisps
        C(r, t, dx - w * 0.35, y0 + (y1 - y0) * 0.15, w * 0.15, w * 0.5, (y1 - y0) * 0.45, w * 0.5, "ba_sk_cloud2")
        if i < 3:
            bolt(r, t, dx - w * 0.2, y1 - 1, -w * 0.4 - 0.3, 0.8 + 0.2 * (i == 0))
        par = t
    for i in range(3):
        a = i * math.tau / 3 + 0.4
        ox, oz = math.cos(a) * 13, math.sin(a) * 11
        o = r.bone(f"cloudlet{i}", b, (0, 12, 0), role="orbit")
        C(r, o, ox, 8 + i * 2, oz, 5, 2.6, 4, "ba_sk_cloud")
        C(r, o, ox + 1, 10.2 + i * 2, oz, 3, 1.6, 3, "ba_sk_cloud")
        C(r, o, ox - 0.6, 7.6 + i * 2, oz, 3.6, 0.8, 3.0, "ba_sk_storm")
        bolt(r, o, ox - 0.8, 7.8 + i * 2, oz, 0.7)
    # ---- waist and torso
    C(r, b, 0, 22, 0, 13, 6, 8, "ba_sk_cape")                                  # sash over the hips
    C(r, b, 0, 25.5, 0, 14, 2, 8.6, "ba_sk_gold")                              # belt
    C(r, b, 0, 25.2, -4.5, 3, 2.6, 0.8, "ba_sk_gem")                           # belt gem
    C(r, b, -3, 19, -4.3, 4, 6, 0.8, "ba_sk_cape")                             # sash tails
    C(r, b, -3, 18.6, -4.4, 4, 0.8, 0.8, "ba_sk_gold")
    C(r, b, 0, 27, 0, 15, 13, 8.5, "ba_sk_armor")                              # torso
    C(r, b, 0, 29, -4.4, 11, 9.5, 1, "ba_sk_silver")                           # breastplate
    C(r, b, 0, 38.6, -4.5, 11.6, 0.8, 1.2, "ba_sk_gold")                       # gold trims
    C(r, b, 0, 28.6, -4.5, 11.6, 0.8, 1.2, "ba_sk_gold")
    bolt(r, b, -0.8, 37, -5.1, 1.2, d=0.6)                                     # the lightning emblem
    for s in (1, -1):
        C(r, b, s * 6.3, 29.4, -4.6, 0.8, 9, 1.2, "ba_sk_gold")
    # ---- cape, hemmed with lightning
    c0 = r.bone("cape0", b, (0, 39, 4.6), role="cape")
    C(r, c0, 0, 25, 4.9, 16, 14.5, 1, "ba_sk_cape")
    C(r, c0, 0, 25, 4.3, 14, 14, 0.4, "ba_sk_lining")
    c1 = r.bone("cape1", c0, (0, 25.5, 5), role="cape")
    C(r, c1, 0, 12, 5.0, 17, 14, 1, "ba_sk_cape")
    C(r, c1, 0, 12, 4.4, 15, 13.5, 0.4, "ba_sk_lining")
    for i, x in enumerate((-6.5, -2, 2.5, 6.5)):
        bolt(r, c1, x - 0.8, 13.5 + (i % 2), 5.8, 0.7, d=0.4)                  # lightning stitched on the hem
    C(r, c1, 0, 11.6, 5.0, 17.4, 0.8, 1.2, "ba_sk_gold")
    # ---- wings of cloud and feathers (vertical planes behind the shoulders)
    for side, s in (("l", 1), ("r", -1)):
        piv = (s * 4, 37, 6)
        w = r.bone(f"wing_{side}", b, piv, role=f"wing_{side}")
        rot = {"rot": [0, s * 16, s * 18], "pivot": piv}
        for k, (ln, y0, ht, m) in enumerate(((22, 32, 9, "ba_sk_feather"), (19, 27, 6, "ba_sk_feather2"), (14, 23, 5, "ba_sk_feather"))):
            x0 = s * 3 if s > 0 else -3 - ln
            r.cube(w, (x0, y0, 6 + k * 0.3), (ln, ht, 0.8), m, **rot)
            for f in range(3):                                                 # feather tips along the lower edge
                fx = s * (3 + ln * (0.45 + 0.2 * f))
                r.cube(w, (fx - 1.2, y0 - 2 - f * 0.6, 6.1 + k * 0.3), (2.4, 2.4 + f * 0.6, 0.6), m, **rot)
        r.cube(w, (s * 3 if s > 0 else -26, 40, 5.6), (23, 2.6, 1.6), "ba_sk_cloud", **rot)        # cloud along the arm of the wing
        r.cube(w, (s * 12 - 2, 41.6, 5.6), (5, 2, 1.6), "ba_sk_cloud", **rot)
        r.cube(w, (s * 7 if s > 0 else -21, 34.5, 5.4), (14, 0.6, 0.4), "ba_sk_bolt", **rot)       # lightning veins
        r.cube(w, (s * 15 - 0.3, 29, 5.4), (0.6, 5.5, 0.4), "ba_sk_bolt", **rot)
    # ---- head
    h = r.bone("head", b, (0, 40, 0), role="head")
    C(r, h, 0, 39.5, 0, 4.6, 2, 4.6, "ba_sk_skin")                             # neck
    C(r, h, 0, 41, -0.5, 8, 8.5, 8, "ba_sk_skin")
    C(r, h, 0, 47.2, -4.7, 8.4, 1.2, 1.2, "ba_sk_cloud2")                       # stern brow
    C(r, h, -2, 46.2, -4.7, 2.8, 0.7, 0.8, "ba_sk_cloud2", rot=[0, 0, -14], pivot=(-0.6, 46.6, -4.5))
    C(r, h, 2, 46.2, -4.7, 2.8, 0.7, 0.8, "ba_sk_cloud2", rot=[0, 0, 14], pivot=(0.6, 46.6, -4.5))
    eye(r, h, -2.1, 45.3, -4.5, 2.0, 1.1, "ba_sk_eye", "dot", "ba_sk_armor")
    eye(r, h, 2.1, 45.3, -4.5, 2.0, 1.1, "ba_sk_eye", "dot", "ba_sk_armor")
    C(r, h, 0, 43.2, -5.3, 1.6, 2.6, 1.4, "ba_sk_skin")                         # nose
    C(r, h, 0, 42.4, -4.8, 4.6, 0.9, 0.6, "ba_sk_cloud")                        # moustache
    C(r, h, -2.8, 41.6, -4.8, 1.2, 1.6, 0.6, "ba_sk_cloud")
    C(r, h, 2.8, 41.6, -4.8, 1.2, 1.6, 0.6, "ba_sk_cloud")
    # mane of cloud streaming back
    C(r, h, 0, 44, 3.2, 10, 7, 4, "ba_sk_cloud")
    C(r, h, 0, 40, 5, 8, 5, 3, "ba_sk_cloud2")
    for s in (1, -1):
        C(r, h, s * 4.6, 42, 0.5, 2, 6.5, 6.5, "ba_sk_cloud")
    # crown: a gold circlet with lightning spikes and a sky gem
    C(r, h, 0, 49, -0.5, 9, 1.8, 9, "ba_sk_gold")
    C(r, h, 0, 49.2, -5.1, 2, 2, 0.6, "ba_sk_gem")
    for i, (x, hh) in enumerate(((-3.6, 3.5), (0, 5), (3.6, 3.5))):
        bolt(r, h, x - 0.7, 50.6, -4.4, 0.6 + hh * 0.06, down=False)
    for x in (-4.0, 4.0):
        C(r, h, x, 50.6, 2.5, 0.8, 2.4, 0.8, "ba_sk_gold")
    # jaw with the cloud beard: it opens with the roar
    jaw = r.bone("jaw", h, (0, 42, 1), role="jaw")
    C(r, jaw, 0, 40, -0.8, 7.2, 2.2, 7, "ba_sk_skin")
    C(r, jaw, 0, 41.6, -4.3, 4, 0.6, 0.4, "maw")
    C(r, jaw, 0, 36.5, -5.6, 8.8, 4.5, 2.6, "ba_sk_cloud")                      # beard of cloud
    C(r, jaw, 0, 33, -5.9, 6.4, 3.8, 2.2, "ba_sk_cloud")
    C(r, jaw, 0.5, 30.2, -6.0, 3.6, 3.0, 1.8, "ba_sk_cloud")
    C(r, jaw, 1, 28.6, -6.0, 1.6, 1.8, 1.4, "ba_sk_cloud2")
    C(r, jaw, -3.6, 38.2, -6.0, 2.4, 2.4, 2.2, "ba_sk_cloud2")
    C(r, jaw, -1.4, 30.5, -7.0, 0.6, 3.6, 0.4, "ba_sk_bolt")                     # a spark caught in the beard
    # ---- arms
    for side, s in (("l", 1), ("r", -1)):
        sx = s * 10
        a0, a1 = r.limb(f"arm_{side}", b, (sx, 38.5, 0), [(4.4, 9, 4.4), (4, 9, 4)], "ba_sk_armor", "ba_sk_gold", role=f"arm_{side}", splay=s * 8)
        C(r, a0, sx + s * 0.5, 35.5, 0, 7, 3.4, 6.6, "ba_sk_gold")             # pauldron
        C(r, a0, sx + s * 0.5, 38.6, 0, 6, 2.2, 5.6, "ba_sk_silver")
        C(r, a0, sx + s * 1.2, 40.6, 0, 4.6, 2.4, 4.4, "ba_sk_cloud")          # cloud curling on top
        C(r, a1, sx, 23, 0, 5, 3.6, 5, "ba_sk_silver")                         # vambrace
        C(r, a1, sx, 22.4, -2.6, 2, 1.6, 0.6, "ba_sk_gem")
        C(r, a1, sx, 18.5, 0, 3.6, 3.6, 3.6, "ba_sk_skin")                     # hand
    # the trident of living lightning
    tr = r.bone("trident", "arm_r1", (-10, 20, -2.6))
    C(r, tr, -10, 4, -2.6, 1.2, 42, 1.2, "ba_sk_gold")
    C(r, tr, -10, 44, -2.6, 7, 1.4, 1.6, "ba_sk_gold")                         # crossguard
    C(r, tr, -10, 43.2, -2.6, 2, 2, 2, "ba_sk_gem")
    for x, hh in ((-13, 6), (-10, 9), (-7, 6)):
        C(r, tr, x, 45.4, -2.6, 0.9, hh, 0.9, "ba_sk_bolt")                    # prongs of light
        C(r, tr, x, 45.4 + hh, -2.6, 0.5, 1.2, 0.5, "ba_sk_bolt")
    C(r, tr, -10, 3, -2.6, 2, 1.4, 2, "ba_sk_gold")                            # butt cap
    # the storm orb in the left palm
    orb = r.bone("orb", "arm_l1", (10, 15, -2.5), role="pulse")
    C(r, orb, 10, 11.5, -2.5, 4.4, 4.4, 4.4, "ba_sk_storm")
    C(r, orb, 10, 12.3, -2.5, 3.2, 2.8, 4.8, "ba_sk_bolt")
    C(r, orb, 10, 13.4, -2.5, 5.4, 0.8, 1.2, "ba_sk_cloud")
    C(r, orb, 10, 11.0, -2.5, 1.2, 0.8, 5.6, "ba_sk_cloud")
    return to_game(r)


# =============================================================== World 5, Lightless Deep: Light Eater
M("ba_le_fur", "1a1826", "3a3460", "fur")
M("ba_le_fur2", "262038", "4a4070", "fur")
M("ba_le_hide", "0e0d16", "24203a", "skin")
M("ba_le_bone", "b8b0a0", "d8d0c0", "skin")
M("ba_le_bone2", "6e685c", "8e8878", "skin")
M("ba_le_eye", "a682ff", "c4aaff", "glow", True)
M("ba_le_light", "ffd27a", "ffe8b0", "glow", True)
M("ba_le_light2", "ffa63a", "ffd080", "glow", True)
M("ba_le_throat", "2a0a1a", "6a1a3a", "flesh")
M("ba_le_gum", "4a1424", "7a2a3a", "flesh")
M("ba_le_smoke", "3a3a46", "5a5a68", "cloud")
M("ba_le_wax", "d8d0b8", "f0e8d4", "skin")
M("ba_le_claw", "26222c", "4a4452", "metal")
M("ba_le_wood", "3a2a1e", "54402c", "bark")


def light_eater():
    """A gaunt hound of the dark that feeds on light: void fur, a pale bone mask with a cluster of six small
    violet eyes, a maw of needle teeth opening on a glowing gullet, and a belly so full of swallowed light
    that it shines between the ribs with the shapes of eaten lanterns. Snuffed torches and dead candles are
    stuck in its back like trophies; feelers and a spined tail trail behind; the front claws are hooks."""
    r = Rig("light_eater")
    b = r.bone("body", None, (0, 19, 0), role="body")
    # ---- trunk: high shoulders, sunken loins
    C(r, b, 0, 19, -7, 14, 8, 13, "ba_le_fur")                                 # chest, upper
    C(r, b, 0, 25.5, -7.5, 11, 3.5, 9, "ba_le_fur2")                           # shoulder hump
    C(r, b, 0, 17, 6, 11, 7, 13, "ba_le_fur")                                  # loins
    C(r, b, 0, 13, 6.5, 9, 4.5, 11, "ba_le_hide")                              # tucked belly behind
    C(r, b, 0, 13.6, -6, 11.6, 5.6, 12, "ba_le_hide")                          # dark wall behind the light
    gl = r.bone("gorged", b, (0, 16, -6), role="pulse")
    C(r, gl, 0, 12.6, -6, 11.0, 6.6, 12.4, "ba_le_light")                      # the swallowed light
    C(r, gl, 0, 12.0, -6, 8, 1.2, 9, "ba_le_light2")
    for s in (1, -1):
        C(r, gl, s * 5.6, 13.6, -8.5, 0.3, 3.6, 2.2, "ba_le_hide")            # silhouette of an eaten lantern
        C(r, gl, s * 5.6, 17.2, -8.5, 0.3, 0.8, 1.2, "ba_le_hide")
        C(r, gl, s * 5.6, 14.0, -3.0, 0.3, 0.8, 4.4, "ba_le_hide")            # ...and a torch
    for s in (1, -1):
        for i, z in enumerate((-11, -8, -5, -2)):
            C(r, b, s * 5.8, 12.4 + i * 0.4, z, 1.0, 7.4 - i * 0.4, 1.2, "ba_le_bone")   # ribs over the glow
        C(r, b, s * 5.8, 18.6, -6.5, 1.0, 1.0, 11, "ba_le_bone2")              # rib spine bar
    C(r, b, 0, 12.2, -6, 1.6, 1.0, 12.6, "ba_le_bone2")                        # sternum
    # spines along the back, with dead lights stuck in them
    for i, (z, hh) in enumerate(((-10, 5), (-6, 6.5), (-2, 5.5), (2.5, 4), (6.5, 3.5), (10, 2.5))):
        y = 28.5 if i < 2 else 23.5 if i < 4 else 23.4
        C(r, b, 0, y if i >= 2 else 28.6, z, 1.2, hh, 1.6, "ba_le_bone2", rot=[-20, 0, 0], pivot=(0, y, z))
    r.cube(b, (3.2, 23.5, -3.5), (1, 8, 1), "ba_le_wood", rot=[0, 0, -24], pivot=(3.7, 24, -3))   # snuffed torch
    r.cube(b, (6.2, 30.2, -3.7), (1.4, 1.4, 1.4), "ba_le_hide", rot=[0, 0, -24], pivot=(3.7, 24, -3))
    C(r, b, 7.6, 32.2, -3, 1.6, 1.4, 1.6, "ba_le_smoke")
    C(r, b, 8.6, 33.8, -3.2, 1.0, 1.0, 1.0, "ba_le_smoke")
    r.cube(b, (-4.6, 22.5, 5), (1, 7, 1), "ba_le_wood", rot=[0, 0, 30], pivot=(-4, 23, 5.5))
    r.cube(b, (-5.0, 28.5, 4.8), (1.4, 1.4, 1.4), "ba_le_hide", rot=[0, 0, 30], pivot=(-4, 23, 5.5))
    for (x, z, hh) in ((-3.8, -10.5, 3), (-2.2, -8.6, 2)):                    # dead candles on the hump
        C(r, b, x, 28.8, z, 1.2, hh, 1.2, "ba_le_wax")
        C(r, b, x + 0.5, 28.6, z, 0.6, hh * 0.6, 1.3, "ba_le_wax")             # a wax drip
        C(r, b, x, 28.8 + hh, z, 0.3, 0.8, 0.3, "ba_le_hide")                  # black wick
    # ---- neck and head
    n = r.bone("neck", b, (0, 22, -13), role="head")
    C(r, n, 0, 16.5, -16, 8, 9, 7, "ba_le_fur")
    C(r, n, 0, 24.5, -15.5, 4, 2, 5, "ba_le_fur2")
    h = r.bone("head", n, (0, 21, -18), role="head")
    C(r, h, 0, 18, -21.5, 12, 8.5, 7, "ba_le_hide")                           # back of the skull
    C(r, h, 0, 25.5, -21, 12.6, 2.6, 7.6, "ba_le_fur")                        # mane
    C(r, h, 0, 18, -28.5, 8.4, 5.6, 8, "ba_le_hide")                          # long snout
    C(r, h, 0, 23.4, -28.5, 5, 1.0, 7.6, "ba_le_bone")                        # bone ridge plate on the snout
    C(r, h, 0, 22.8, -32.3, 6.6, 0.9, 0.6, "ba_le_bone2")
    C(r, h, 0, 26.6, -25.4, 11, 1.6, 1.6, "ba_le_bone")                       # bone brow
    for s in (1, -1):
        C(r, h, s * 4.8, 27.4, -24.6, 1.8, 2.4, 1.6, "ba_le_bone2", rot=[0, 0, -s * 25], pivot=(s * 4.8, 27.4, -24.6))  # brow horns
        C(r, h, s * 2.2, 21.8, -32.65, 1.0, 0.8, 0.4, "ba_le_throat")         # nostril slits
        C(r, h, s * 6.4, 20, -21.5, 1.4, 4.5, 5, "ba_le_fur2")                # cheek fur
        C(r, h, s * 6.6, 24.6, -19, 1.2, 3.6, 2.4, "ba_le_fur2", rot=[0, 0, -s * 20], pivot=(s * 6.6, 24.6, -19))  # torn ears
    C(r, h, 2.6, 26.6, -26.3, 0.4, 1.4, 0.3, "ba_le_hide")                     # a crack in the brow bone
    # six small eyes clustered on the brow, unevenly, the biggest with pupils
    for (x, y, s_) in ((-2.6, 25.4, 1.5), (2.7, 25.5, 1.3), (-0.1, 25.9, 0.8), (-4.6, 25.0, 1.0), (4.6, 24.9, 0.8), (0.9, 24.9, 0.6)):
        eye(r, h, x, y, -25.0, s_, s_ * 0.8, "ba_le_eye", "slit" if s_ > 1 else None, "ba_le_hide")
    C(r, h, 0, 18.4, -28.5, 7.8, 0.8, 7.4, "ba_le_throat")                     # roof of the maw
    teeth(r, h, -3.6, 3.6, 18.4, -32.85, 6, 3.4, "ba_le_bone", down=True, w=0.55, d=0.5)
    for s in (1, -1):
        for z in (-30.5, -28, -25.5, -23):
            C(r, h, s * 3.9, 16.2 + (z % 2) * 0.6, z, 0.5, 2.6, 0.5, "ba_le_bone")   # side needles
    C(r, h, 0, 16.8, -24.6, 6.6, 3.2, 1.0, "ba_le_light")                      # the glowing gullet at the back of the maw
    C(r, h, 0, 17.6, -25.3, 3.4, 1.6, 0.6, "ba_le_light2")
    jaw = r.bone("jaw", h, (0, 19, -19), role="jaw")
    C(r, jaw, 0, 14, -26.5, 8, 3.6, 12, "ba_le_hide")
    C(r, jaw, 0, 13.4, -31.0, 6, 1.6, 2, "ba_le_bone2")                        # bone chin
    C(r, jaw, 0, 17.4, -26.5, 6.6, 0.4, 10.5, "ba_le_throat")                  # tongue bed
    C(r, jaw, 0, 17.6, -28, 2.2, 0.6, 6, "ba_le_gum")                          # tongue
    teeth(r, jaw, -3.0, 3.0, 16.6, -32.95, 5, 3.0, "ba_le_bone", w=0.55, d=0.5)
    for s in (1, -1):
        for z in (-29.5, -27, -24.5):
            C(r, jaw, s * 3.6, 17.4, z, 0.5, 2.0, 0.5, "ba_le_bone")
        C(r, jaw, s * 4.8, 15, -20.5, 1.4, 1.4, 3, "ba_le_fur2")               # jaw hinge fur
    # three motes of light being drawn into the maw
    for i in range(3):
        o = r.bone(f"mote{i}", h, (0, 20, -26), role="orbit")
        a = i * math.tau / 3
        C(r, o, math.cos(a) * 9, 19 + i * 2.2, -26 + math.sin(a) * 9, 1.2 - i * 0.2, 1.2 - i * 0.2, 1.2 - i * 0.2, "ba_le_light")
    # ---- legs: front pair long with hooked claws, hind pair crouched (diagonal gait)
    for side, s in (("l", 1), ("r", -1)):
        diag = "r" if side == "l" else "l"
        fx = s * 7.5
        f0, f1 = r.limb(f"fleg_{side}", None, (fx, 18.5, -8), [(4.6, 9.5, 4.8), (3.4, 9, 3.4)], "ba_le_fur", "ba_le_fur2", role=f"leg_{side}")
        C(r, f0, fx, 13, -8, 5.4, 6, 5.6, "ba_le_fur2")                        # shoulder mass
        C(r, f1, fx, 0, -9, 4.4, 2.4, 5.6, "ba_le_hide")                      # paw
        for k in range(3):
            cx = fx - 1.5 + k * 1.5
            C(r, f1, cx, 0.6, -13.6, 0.8, 0.9, 3.4, "ba_le_claw")              # long claws...
            C(r, f1, cx, 0, -14.8, 0.8, 1.0, 1.0, "ba_le_claw")                # ...hooked at the tip
        C(r, f1, fx + s * 2, 6, -8, 0.8, 2.6, 0.8, "ba_le_bone2")             # dew claw spur
        hx = s * 6.2
        h0, h1 = r.limb(f"hleg_{side}", None, (hx, 17, 9), [(4.8, 8.5, 5.4), (3.2, 8.5, 3.2)], "ba_le_fur", "ba_le_fur2", role=f"leg_{diag}")
        C(r, h0, hx, 11, 9.5, 5.6, 6, 6.4, "ba_le_fur2")                      # haunch
        C(r, h1, hx, 0, 8.4, 4, 2, 5, "ba_le_hide")
        for k in range(3):
            C(r, h1, hx - 1.2 + k * 1.2, 0, 5.5, 0.7, 0.9, 1.6, "ba_le_claw")
    # ---- feelers from the shoulders, tips with a last stolen spark
    for side, s in (("l", 1), ("r", -1)):
        piv = (s * 5.5, 25, -8)
        w = r.bone(f"feeler_{side}", b, piv, role=f"wing_{side}")
        kw = {"rot": [0, s * -55, s * 24], "pivot": piv}
        r.cube(w, (s * 5.5 - (0 if s > 0 else 16), 24.6, -8.4), (16, 0.8, 0.8), "ba_le_hide", **kw)
        r.cube(w, (s * 5.5 + (15.4 if s > 0 else -16.8), 24.4, -8.6), (1.4, 1.2, 1.2), "ba_le_eye", **kw)
        kw2 = {"rot": [0, s * -75, s * 8], "pivot": piv}
        r.cube(w, (s * 5.5 - (0 if s > 0 else 11), 24.7, -8.3), (11, 0.6, 0.6), "ba_le_hide", **kw2)
        r.cube(w, (s * 5.5 + (10.6 if s > 0 else -11.6), 24.5, -8.5), (1, 1, 1), "ba_le_light2", **kw2)
    # ---- spined tail
    par = b
    for i in range(5):
        z = 12 + i * 5.5
        w = 4.6 - i * 0.7
        t = r.bone(f"tail{i}", par, (0, 20 - i * 0.8, z), role="tail")
        C(r, t, 0, 18 - i * 0.8 - w / 2 + 2, z + 3, w, w, 6.4, "ba_le_fur" if i % 2 == 0 else "ba_le_fur2")
        C(r, t, 0, 20 - i * 0.8 + w / 2 - 0.4, z + 2.5, 0.8, 2.2 - i * 0.25, 1.2, "ba_le_bone2")   # spine
        par = t
    C(r, par, 0, 15.6, 37, 3.6, 3.6, 4, "ba_le_hide")                          # tuft that drinks the light
    C(r, par, 0, 16.2, 39, 2.2, 2.2, 1.6, "ba_le_fur2")
    return to_game(scale_rig(r, 0.9))
