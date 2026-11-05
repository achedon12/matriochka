"""World 1, Toxic Jungle."""
from common import Rig, mat

mat("cap_toxic", "8a3a9a", "d8f04a", "spots")
mat("gill", "e8d0a0", "a89060", "cloth")
mat("w1_toxic", "b8f030", "d8ff60", "glow", True)
mat("w1_eye_violet", "c070ff", "d8a0ff", "glow", True)
mat("w1_eye_green", "8aff3a", "b8ff70", "glow", True)
mat("w1_eye_amber", "ffa020", "ffc850", "glow", True)
mat("sporeling_skin", "c8d89a", "9ab060", "skin")
mat("w1_cap_rim", "5a2066", "9a4aa8", "skin")
mat("w1_gill_dark", "8a6a48", "a88a60", "bark")
mat("w1_belly", "e0e8b8", "c8d89a", "spots")

# root creeper
mat("w1_root_dark", "4a3220", "6a4a2c", "bark")
mat("w1_root", "8a6038", "b08450", "bark")
mat("w1_root_tip", "c8b48a", "e8dab4", "skin")
mat("w1_thorn", "d8cca0", "f4ecc8", "skin")
mat("w1_sap", "c8f03a", "e0ff70", "glow", True)
mat("w1_maw", "1a0e08", "3a1a10", "flesh")

# snare flower
mat("w1_petal", "8a1438", "f0d040", "spots")
mat("w1_petal_edge", "c83a5a", "f08aa0", "leaf")
mat("w1_sepal", "2a5a1e", "5a8a2a", "leaf")
mat("w1_stalk", "2e4e1a", "5a7a2a", "bark")
mat("w1_nectar", "e8ff4a", "f8ff80", "glow", True)
mat("w1_leaf_big", "2a6a2a", "6ab04a", "leaf")
mat("w1_vein_leaf", "9ad060", "c8f080", "skin")

# spore bearer
mat("w1_hide", "4a3a50", "6a5a74", "flesh")
mat("w1_hide_pale", "8a7a90", "a898ac", "skin")
mat("w1_sac", "b8e040", "f4ffa0", "membrane", True)
mat("w1_sac_vein", "3a2a40", "5a4a62", "skin")
mat("w1_pore", "2a1a2a", "4a2a3a", "flesh")

# chitin guard
mat("w1_plate", "1e3a24", "3a6a30", "chitin")
mat("w1_plate_rim", "c8d040", "f0f090", "metal")
mat("w1_shell", "22402a", "6ab03a", "chitin")
mat("w1_shell_dark", "142218", "2e4a2a", "chitin")
mat("w1_stud", "b8c890", "e8f0c0", "skin")
mat("w1_weak", "ff8a1a", "ffb040", "glow", True)
mat("w1_claw", "141a12", "2a3422", "skin")
mat("w1_scratch", "0e1a10", "1a2a1a", "skin")


def _eye(r, bone, x, y, z, w, h, glow, slit=False, pupil=True):
    """A glowing eye set in a dark socket on a face whose front is at depth z, with a pupil."""
    r.cube(bone, (x - w / 2 - 0.3, y - h / 2 - 0.3, z - 0.2), (w + 0.6, h + 0.6, 0.4), "pupil")
    r.cube(bone, (x - w / 2, y - h / 2, z - 0.35), (w, h, 0.4), glow)
    if not pupil:
        return
    if slit:
        r.cube(bone, (x - 0.15, y - h / 2, z - 0.45), (0.3, h, 0.2), "pupil")
    else:
        r.cube(bone, (x - w * 0.15, y - h * 0.2, z - 0.45), (w * 0.35, h * 0.45, 0.2), "pupil")


def sporeling():
    """A walking toadstool the size of a child: a heavy spotted cap, gills, glowing eyes in its shadow, stubby claws."""
    r = Rig("sporeling")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-3, 5, -2.5), (6, 6, 5), "sporeling_skin")
    r.cube("body", (-2.2, 6, -2.8), (4.4, 4, 0.5), "w1_belly")         # pale spotted belly
    r.cube("body", (-2.5, 4.5, -2), (5, 1.5, 4), "gill")               # belt of gills at the waist
    r.cube("body", (-3.3, 9.5, -2.8), (6.6, 1.2, 5.6), "gill")         # collar ruff under the head
    r.cube("body", (2.2, 10.4, 0.5), (1.2, 1.4, 1.2), "fungus")        # a baby mushroom on the shoulder
    r.cube("body", (1.8, 11.6, 0.1), (2, 0.7, 2), "cap_toxic")
    r.bone("head", "body", (0, 11, 0), role="head")
    r.cube("head", (-3.5, 11, -3), (7, 4, 6), "sporeling_skin")        # face under the cap
    _eye(r, "head", -1.6, 13.2, -3, 1.8, 1.6, "w1_eye_violet")
    _eye(r, "head", 1.7, 13.1, -3, 1.6, 1.8, "w1_eye_violet")    # one eye a bit taller: asymmetry
    r.cube("head", (-3.2, 14.2, -3.3), (2.6, 0.5, 0.4), "w1_cap_rim")  # frowning brows
    r.cube("head", (0.6, 14.4, -3.3), (2.6, 0.5, 0.4), "w1_cap_rim")
    r.cube("head", (-6.5, 15, -6), (13, 3, 12), "cap_toxic")           # the cap
    r.cube("head", (-5, 18, -4.5), (10, 2, 9), "cap_toxic")
    r.cube("head", (-3, 20, -3), (6, 1, 6), "cap_toxic")
    r.cube("head", (-7, 14.6, -6.5), (14, 1, 1), "w1_cap_rim")          # drooping rim, front
    r.cube("head", (-7, 14.6, 5.5), (14, 1, 1), "w1_cap_rim")
    r.cube("head", (-7, 14.6, -5.5), (1, 1, 11), "w1_cap_rim")
    r.cube("head", (6, 14.6, -5.5), (1, 1, 11), "w1_cap_rim")
    r.cube("head", (-6, 14.5, -5.5), (12, 0.6, 11), "gill")             # gills under the brim
    for x in (-4.5, -2, 2, 4.5):
        r.cube("head", (x - 0.2, 14.3, -5.5), (0.4, 0.4, 11), "w1_gill_dark")   # gill ribs
    r.cube("head", (-5.8, 13.2, -6.3), (0.6, 1.4, 0.6), "w1_toxic")       # toxic drips off the rim
    r.cube("head", (4.6, 13.6, -6.3), (0.6, 1, 0.6), "w1_toxic")
    r.cube("head", (6.4, 12.8, 2), (0.6, 1.8, 0.6), "w1_toxic")
    r.cube("head", (4, 19.2, -1), (2, 1, 2), "w1_toxic")                   # spore sacs on top
    r.cube("head", (-5, 18.6, 2), (1.5, 1, 1.5), "w1_toxic")
    jaw = r.bone("jaw", "head", (0, 11.5, -2.5), role="jaw")
    r.cube(jaw, (-2.5, 10.4, -3.2), (5, 1.4, 1), "pupil")
    for x in (-2, -0.6, 0.8):
        r.cube(jaw, (x, 11.2, -3.4), (0.6, 0.8, 0.3), "tooth")
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 3.5, 10, 0), role=f"arm_{side}")
        r.cube(arm, (s * 3.5 - 1, 5.5, -1), (2, 5, 2), "sporeling_skin")
        r.cube(arm, (s * 3.5 - 1.2, 8.6, -1.2), (2.4, 1, 2.4), "gill")     # frilled cuff
        r.cube(arm, (s * 3.5 - 1.2, 4.5, -1.6), (2.4, 1.2, 1.2), "gill")   # little claws
        for dx in (-0.8, 0.5):
            r.cube(arm, (s * 3.5 + dx - 0.2, 3.7, -1.6), (0.5, 0.9, 0.5), "tooth")
        leg = r.bone(f"leg_{side}", None, (s * 1.6, 5, 0), role=f"leg_{side}")
        r.cube(leg, (s * 1.6 - 1.2, 0, -1.2), (2.4, 5.5, 2.4), "sporeling_skin")
        r.cube(leg, (s * 1.6 - 1.4, 0, -2), (2.8, 1, 3), "fungus")
        r.cube(leg, (s * 1.6 - 1.5, 3.2, -1.5), (3, 0.8, 3), "gill")      # gill anklet
    for i, (x, y, z) in enumerate(((7, 14, 1), (-7, 12, -1), (1, 22, 5))):
        o = r.bone(f"spore{i}", "head", (0, 14, 0), role="orbit")
        r.cube(o, (x - 0.5, y, z - 0.5), (1, 1, 1), "w1_toxic")
    return r


def _sac(r, bone, cx, cy, cz, s, m="w1_sac"):
    """A rounded bulb out of three crossed boxes."""
    a, b = s, s * 0.72
    r.cube(bone, (cx - a / 2, cy - b / 2, cz - b / 2), (a, b, b), m)
    r.cube(bone, (cx - b / 2, cy - a / 2, cz - b / 2), (b, a, b), m)
    r.cube(bone, (cx - b / 2, cy - b / 2, cz - a / 2), (b, b, a), m)


def root_creeper():
    """A creeping knot of roots that lies half-buried: a gnarled face split in the wood with sap-lit eyes, root legs
    clawing the soil, two grasping vines in front, trailing roots behind and a sapling growing on its back."""
    r = Rig("root_creeper")
    r.bone("body", None, (0, 4, 0), role="body")
    r.cube("body", (-4.5, 1.5, -4), (9, 5, 8.5), "w1_root_dark")          # the knot
    r.cube("body", (-3.5, 6.3, -3), (7, 1.4, 6.5), "w1_root_dark")
    r.cube("body", (-3, 7.4, -2.5), (6, 0.7, 5), "moss")                  # moss pad on top
    r.cube("body", (-4.9, 5.6, -3.5), (2.6, 1.2, 3), "moss")
    r.cube("body", (-4.9, 2.6, -1.8), (9.8, 1.2, 1.2), "w1_root")          # roots braided round the knot
    r.cube("body", (1.2, 1.4, -4.4), (1.2, 6.4, 1.2), "w1_root")
    r.cube("body", (-2.6, 1.4, 4.2), (1.2, 5.8, 1.2), "w1_root")
    r.cube("body", (4.3, 3.8, -3.3), (0.4, 0.6, 3.6), "w1_sap")          # sap glowing through the cracks
    r.cube("body", (-4.7, 4, 0.5), (0.4, 0.6, 2.8), "w1_sap")
    r.cube("body", (-1, 5.6, 4.3), (2.5, 0.5, 0.4), "w1_sap")
    r.cube("body", (1.5, 6.8, 0.5), (2.6, 1.2, 2.4), "dirt")              # a clod of earth it carried up
    r.cube("body", (-0.7, 7.8, 0.3), (0.8, 3, 0.8), "stem")              # the sapling
    r.cube("body", (-1.9, 10.4, -0.2), (1.6, 0.5, 1.4), "leaf_spring", rot=[0, 30, 0])
    r.cube("body", (0, 9.6, 0.3), (1.8, 0.5, 1.2), "leaf_spring", rot=[0, -20, 0])
    r.cube("body", (-5.6, 0, -3.5), (2.4, 1.2, 4), "dirt")               # the soil it heaved up
    r.cube("body", (3.4, 0, 1.5), (2.6, 1, 3.4), "dirt")
    r.cube("body", (-1.6, 7.6, -1.6), (0.8, 0.8, 0.8), "w1_root_tip")    # a mushroom in the moss
    r.cube("body", (-2, 8.3, -2), (1.6, 0.5, 1.6), "petal")
    # face: a split knot in the wood; the upper half lifts like a lid to bite
    r.bone("head", "body", (0, 3, -4), role="head")
    r.cube("head", (-3.6, 0.5, -8.2), (7.2, 2.4, 4.4), "w1_root")              # lower jaw
    r.cube("head", (-3.4, 2.4, -7.7), (6.8, 1.2, 2.5), "w1_maw")               # throat behind the teeth
    for x in (-3, -1.5, 0.6, 2.4):
        r.cube("head", (x - 0.2, 2.6, -8), (0.6, 0.9, 0.6), "w1_thorn")
    r.cube("head", (-3.9, 0.3, -8.5), (1.4, 0.9, 1.4), "moss")
    jaw = r.bone("jaw", "head", (0, 3.6, -4.2), role="jaw")
    r.cube(jaw, (-4, 3.4, -7.6), (8, 3.8, 4), "w1_root_dark")
    r.cube(jaw, (-4.4, 6.6, -8.2), (8.8, 1.3, 2.6), "w1_root")                 # heavy brow
    r.cube(jaw, (-3.8, 7.8, -7), (0.9, 2, 0.9), "w1_root")                     # twig horns, uneven
    r.cube(jaw, (2.6, 7.8, -6.6), (0.9, 2.8, 0.9), "w1_root")
    _eye(r, jaw, -1.8, 5.5, -7.6, 2, 1.3, "w1_sap")
    _eye(r, jaw, 1.9, 5.6, -7.6, 1.5, 1.1, "w1_sap")
    for x in (-2.6, -0.4, 1.8):
        r.cube(jaw, (x, 2.6, -7.9), (0.6, 1.2, 0.6), "w1_thorn")              # upper thorn teeth
    # root legs clawing the soil, three per side, splayed
    for side, s in (("l", 1), ("r", -1)):
        for i, (z, ang) in enumerate(((-2.6, 32), (0.6, 0), (3.6, -32))):
            pv = (s * 4.2, 3.6, z)
            leg = r.bone(f"leg_{side}{i}", None, pv, role=f"leg_{side}")
            a = [0, s * ang, 0]
            r.cube(leg, (4 if s > 0 else -7, 2.6, z - 0.7), (3, 1.4, 1.4), "w1_root", rot=a, pivot=pv)
            r.cube(leg, (6.4 if s > 0 else -7.8, 0.4, z - 0.6), (1.4, 3, 1.2), "w1_root", rot=a, pivot=pv)
            r.cube(leg, (7.4 if s > 0 else -9.6, 0, z - 0.4), (2.2, 0.6, 0.8), "w1_root_tip", rot=a, pivot=pv)
    # grasping vines in front of the face
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 3.4, 4.5, -4.5), role=f"arm_{side}")
        x = s * 5
        r.cube(arm, (x - 0.6, 3.8, -8), (1.2, 1.2, 4), "w1_root")
        r.cube(arm, (x - 0.5, 0.8, -8.9), (1, 3.6, 1), "w1_root")
        r.cube(arm, (x - 0.45, 0.2, -10.6), (0.9, 0.9, 2), "w1_root_tip")
        r.cube(arm, (x - 0.4, 1, -10.9), (0.8, 0.9, 0.8), "w1_root_tip")     # hooked tip
        r.cube(arm, (x + s * 0.4 - 0.2, 4.6, -6.2), (0.4, 0.9, 0.4), "w1_thorn")
    # trailing roots behind
    t = r.bone("tail", "body", (0, 2.5, 4), role="tail")
    r.cube(t, (-1, 1, 3.5), (2, 1.8, 4), "w1_root_dark")
    r.cube(t, (-0.7, 0.4, 7), (1.4, 1.2, 3.5), "w1_root")
    r.cube(t, (-0.4, 0, 10), (0.8, 0.7, 2.4), "w1_root_tip")
    r.cube(t, (0.6, 0.4, 6), (1, 0.9, 3.5), "w1_root", rot=[0, 35, 0], pivot=(0.6, 1, 6))
    r.cube(t, (-1.6, 0.4, 6), (1, 0.9, 3.5), "w1_root", rot=[0, -35, 0], pivot=(-1.6, 1, 6))
    return r


def snare_flower():
    """A rooted carnivorous bloom: a gaping jaw of crimson petals lined with fangs and cilia, a pool of glowing
    nectar and a single eye in its throat, a thorny stalk with two lashing vines, a rosette of leaves at its foot."""
    r = Rig("snare_flower")
    r.bone("body", None, (0, 1, 0), role="body")
    r.cube("body", (-2.5, 0, -2.5), (5, 2.2, 5), "w1_root_dark")          # root knot
    r.cube("body", (-4.2, 0, -0.6), (2, 0.8, 1.2), "w1_root")
    r.cube("body", (2.2, 0, 0.4), (2.2, 0.8, 1.2), "w1_root")
    for i in range(5):                                                     # rosette of leaves on the ground
        ang = i * 72 + 36
        r.cube("body", (-1.6, 0.2, 2), (3.2, 0.6, 7), "w1_leaf_big", rot=[0, ang, 0], pivot=(0, 0.5, 0))
        r.cube("body", (-0.3, 0.5, 2.5), (0.6, 0.5, 6), "w1_vein_leaf", rot=[0, ang, 0], pivot=(0, 0.5, 0))
    r.cube("body", (-1.2, 1.5, -1.2), (2.4, 6, 2.4), "w1_stalk")          # stalk, leaning forward
    r.cube("body", (-1.1, 7, -2.1), (2.2, 4.5, 2.2), "w1_stalk")
    r.cube("body", (-1.6, 6.5, -1.8), (3.2, 1, 3.2), "w1_sepal")          # node
    for x, y, z in ((1.1, 4, -0.4), (-1.6, 5.5, 0.2), (0.6, 9, -2.6)):
        r.cube("body", (x, y, z), (0.5, 0.5, 0.5), "w1_thorn")
    r.cube("body", (1.2, 8.4, -1.8), (2.4, 0.4, 1.4), "w1_leaf_big")      # small stalk leaf
    # the bloom
    r.bone("head", "body", (0, 12, -1.5), role="head")
    r.cube("head", (-2.6, 10.8, -3.2), (5.2, 3.2, 3.8), "w1_sepal")       # calyx
    for x in (-3.2, 2.2):
        r.cube("head", (x, 10.4, -3.4), (1, 2.6, 1), "w1_sepal")         # sepal claws
    r.cube("head", (-3.4, 12.6, -3.8), (6.8, 3.6, 0.8), "maw")            # throat
    _eye(r, "head", 0, 14.3, -3.8, 2, 1.6, "w1_eye_green", slit=True)        # the eye deep in its throat
    for i, ang in enumerate((-60, -25, 25, 60)):                            # crown of petals behind
        r.cube("head", (-1.6, 12.5, -0.4), (3.2, 5.5 + (i % 2), 0.8), "w1_petal_edge", rot=[0, ang, 0], pivot=(0, 13, -2))
    r.cube("head", (-1.5, 13.5, 0.3), (3, 6.5, 0.8), "w1_petal_edge")
    r.cube("head", (-4, 10.6, -9.2), (8, 2.4, 7), "w1_petal")                # lower jaw
    r.cube("head", (-3.5, 12.6, -8.6), (7, 0.7, 5.4), "w1_nectar")           # nectar pool
    r.cube("head", (-0.6, 12.9, -7.6), (1.2, 0.6, 4.5), "petal_inner")       # stamen tongue
    r.cube("head", (-4.2, 12.6, -9.5), (8.4, 0.6, 0.6), "w1_petal_edge")
    for x in (-3, -1.5, 0, 1.5, 3):
        r.cube("head", (x - 0.25, 12.9, -9.4), (0.5, 1.1, 0.5), "tooth")
    r.cube("head", (-1.2, 9.6, -8.8), (0.6, 1, 0.6), "w1_nectar")            # nectar drips
    r.cube("head", (2, 9.9, -7), (0.5, 0.7, 0.5), "w1_nectar")
    jaw = r.bone("jaw", "head", (0, 16.2, -2.6), role="jaw")                # the upper trap snaps open upward
    r.cube(jaw, (-4.2, 16, -9.4), (8.4, 2.6, 8.2), "w1_petal")         # upper jaw
    r.cube(jaw, (-3.4, 18.4, -8.4), (6.8, 1.2, 6.6), "w1_petal")
    r.cube(jaw, (-3.7, 15.6, -8.9), (7.4, 0.6, 6), "maw")              # inner flesh
    r.cube(jaw, (-4.4, 15.8, -9.7), (8.8, 0.8, 0.6), "w1_petal_edge")   # lip
    for i, x in enumerate((-3.4, -2, -0.6, 0.8, 2.2, 3.4)):                # fangs hanging from the lip
        r.cube(jaw, (x - 0.3, 14.3 + (i % 2) * 0.4, -9.5), (0.6, 1.6 - (i % 2) * 0.4, 0.6), "tooth")
    for s in (1, -1):
        for z in (-7.2, -4.8):
            r.cube(jaw, (s * 3.8 - 0.3, 14.6, z), (0.6, 1.2, 0.6), "tooth")
        r.cube(jaw, (s * 4.3 - 0.2, 18, -8.4), (0.4, 2, 0.4), "w1_petal_edge")
    for i, x in enumerate((-3.8, -2.4, -1, 0.4, 1.8, 3.2)):               # cilia along the trap's rim
        r.cube(jaw, (x, 18.6, -9.6), (0.4, 2 + (i % 3) * 0.6, 0.4), "w1_petal_edge")
    # lashing vines
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 1, 7.5, -0.5), role=f"arm_{side}")
        x = s * 3.6
        r.cube(arm, (min(s * 0.8, x), 7, -1), (2.8, 1, 1), "w1_stalk")
        r.cube(arm, (x - 0.5, 2, -1), (1, 5.6, 1), "w1_stalk")
        r.cube(arm, (x - 0.45, 1, -2.6), (0.9, 1.4, 2.2), "w1_stalk")
        r.cube(arm, (x - 0.4, 2.2, -3.2), (0.8, 1.2, 0.8), "w1_sepal")    # hook
        r.cube(arm, (x + s * 0.5 - 0.2, 4.4, -0.7), (0.5, 0.5, 0.5), "w1_thorn")
        r.cube(arm, (x - s * 0.3 - 0.9, 5.8, -0.4), (1.8, 0.4, 1.2), "w1_leaf_big")
    for i, (x, y, z) in enumerate(((5, 15, -4), (-5.5, 13, -2))):        # drifting pollen
        o = r.bone(f"pollen{i}", "head", (0, 13, -3), role="orbit")
        r.cube(o, (x - 0.4, y, z - 0.4), (0.8, 0.8, 0.8), "w1_nectar")
    return r


def spore_bearer():
    """A hunched pack-beast that carries swollen, glowing spore sacs on its back, strapped down by dark veins;
    it coughs spores through a tube snout and flees on stubby legs."""
    r = Rig("spore_bearer")
    r.bone("body", None, (0, 3.5, 0), role="body")
    r.cube("body", (-4, 2.2, -4), (8, 5, 9), "w1_hide")
    r.cube("body", (-3.4, 1.7, -3.4), (6.8, 1, 7.8), "w1_hide_pale")      # belly
    r.cube("body", (-3.5, 6.8, -3), (7, 1.2, 7), "w1_hide")
    for z in (-2.4, 0.4):
        r.cube("body", (-4.3, 3, z), (8.6, 0.5, 0.6), "w1_hide_pale")    # skin folds
    _sac(r, "body", -1, 10.2, -0.2, 5.6)                                   # big sac
    _sac(r, "body", 2.5, 9.2, 2.4, 4.2)                                    # second sac
    _sac(r, "body", -1.8, 8.8, 3.8, 3.4)                                   # back sac
    r.cube("body", (1.6, 11.6, -2.6), (2, 2, 2), "w1_sac")                # budding sac
    r.cube("body", (-4.1, 9.9, -2.25), (6.2, 0.5, 4.1), "w1_sac_vein")     # veins strapping the sacs
    r.cube("body", (-1.3, 7.3, -2.3), (0.5, 5.9, 4.2), "w1_sac_vein")
    r.cube("body", (0.3, 9, 0.85), (4.4, 0.45, 3.1), "w1_sac_vein")
    for x, y, z in ((-1, 13, -0.2), (2.5, 11.3, 2.4), (-1.8, 10.5, 3.8)):
        r.cube("body", (x - 0.6, y - 0.1, z - 0.6), (1.2, 0.4, 1.2), "w1_pore")    # pores leaking spores
        r.cube("body", (x - 0.3, y + 0.2, z - 0.3), (0.6, 0.5, 0.6), "w1_toxic")
    r.cube("body", (-4.4, 5.6, 1), (1, 1.4, 1), "w1_sac")                 # small sacs on the flank
    r.cube("body", (3.5, 4.4, -1.6), (1.2, 1.2, 1.2), "w1_sac")
    r.cube("body", (-4.3, 4.2, 2.5), (0.5, 1.2, 0.5), "w1_toxic")            # drip
    # head
    r.bone("head", "body", (0, 5, -4), role="head")
    r.cube("head", (-2.6, 3, -7.2), (5.2, 4, 3.6), "w1_hide")
    r.cube("head", (-2.9, 6.4, -7.3), (5.8, 0.8, 3), "w1_hide_pale")      # brow ridge
    r.cube("head", (-1.1, 3.8, -9.4), (2.2, 2.2, 2.4), "w1_hide_pale")    # tube snout
    r.cube("head", (-0.7, 4.2, -9.6), (1.4, 1.4, 0.4), "w1_pore")
    r.cube("head", (-0.35, 4.55, -9.7), (0.7, 0.7, 0.2), "w1_toxic")         # spores glowing in the snout
    _eye(r, "head", -1.7, 5.7, -7.2, 1.1, 1.1, "w1_eye_green", pupil=False)
    _eye(r, "head", 1.7, 5.7, -7.2, 1.1, 1.1, "w1_eye_green", pupil=False)
    r.cube("head", (-2.4, 4.6, -7.5), (0.6, 0.6, 0.3), "w1_eye_green")       # smaller extra eyes
    r.cube("head", (1.9, 4.7, -7.5), (0.5, 0.5, 0.3), "w1_eye_green")
    for s in (1, -1):                                                      # feelers with glowing tips
        r.cube("head", (s * 1.4 - 0.2, 7, -6.2), (0.4, 2.6, 0.4), "w1_hide_pale")
        r.cube("head", (s * 1.4 - 0.4, 9.4, -6.4), (0.8, 0.8, 0.8), "w1_toxic")
    jaw = r.bone("mandible", "head", (0, 3.4, -5))
    r.cube(jaw, (-2.2, 2.3, -7.6), (4.4, 1, 3), "w1_hide_pale")
    for s in (1, -1):
        r.cube(jaw, (s * 1.8 - 0.3, 2.4, -8.2), (0.6, 1.2, 0.6), "tooth")  # mandible hooks
    # stubby legs
    for i, z in enumerate((-2.4, 2.6)):
        for side, s in (("l", 1), ("r", -1)):
            role = f"leg_{side}" if i == 0 else f"leg_{'r' if side == 'l' else 'l'}"
            leg = r.bone(f"leg_{side}{i}", None, (s * 3, 3, z), role=role)
            r.cube(leg, (s * 3 - 1.1, 0.6, z - 1.1), (2.2, 3, 2.2), "w1_hide")
            r.cube(leg, (s * 3 - 1.3, 0, z - 1.5), (2.6, 0.8, 2.8), "w1_hide_pale")
            r.cube(leg, (s * 3 - 1, 0, z - 2), (2, 0.5, 0.6), "w1_claw")
    t = r.bone("tail", "body", (0, 3.5, 4.5), role="tail")                 # stub tail dragging a sac
    r.cube(t, (-1, 2.4, 4), (2, 1.6, 3), "w1_hide")
    r.cube(t, (-0.6, 2, 6.6), (1.2, 1.2, 1.6), "w1_hide")
    _sac(r, t, 0, 2.1, 8.5, 2)
    for i, (x, y, z) in enumerate(((5, 10, 1), (-5.5, 8, -1), (0.5, 14.5, 2))):
        o = r.bone(f"spore{i}", "body", (0, 9, 0), role="orbit")
        r.cube(o, (x - 0.4, y, z - 0.4), (0.8, 0.8, 0.8), "w1_toxic")
    return r


def chitin_guard():
    """An armoured beetle sentinel: a heater-shield pronotum with a rim, a boss, studs, scratches and a horn
    covers it from the front; raptorial forelegs end in pincers; from behind, the split wing-cases show its
    glowing soft abdomen, the only place to break it."""
    r = Rig("chitin_guard")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-4.5, 3.6, -6), (9, 5.4, 7), "w1_shell_dark")         # thorax
    r.cube("body", (-5, 3, 0), (10, 5, 8.5), "w1_shell_dark")             # abdomen
    r.cube("body", (-4, 2.5, 0.5), (8, 0.8, 7.5), "w1_stud")              # banded underside
    r.cube("body", (-3.2, 3.2, 8.2), (6.4, 3, 1.6), "w1_weak")            # the glowing abdomen tip, the weak point
    r.cube("body", (-0.3, 3, 9.6), (0.6, 3.4, 0.4), "w1_shell_dark")
    for s in (1, -1):                                                      # wing-cases, slightly split
        x0 = 0.4 if s > 0 else -5.6
        r.cube("body", (x0, 6.6, -1), (5.2, 3, 9.8), "w1_shell")
        r.cube("body", (x0 + (0.4 if s > 0 else 0.4), 9.4, 0), (4.4, 1, 7.6), "w1_shell")
        r.cube("body", (x0 + (4.4 if s > 0 else -0.2), 6.3, -0.6), (1, 1, 9), "w1_plate_rim")   # gold edge
    r.cube("body", (-0.45, 6.8, 0), (0.9, 3.8, 8.6), "w1_weak")           # glow through the split
    r.cube("body", (-5, 9, -6.6), (10, 5.4, 5.6), "w1_shell")             # pronotum hump behind the shield
    r.cube("body", (-4, 14.2, -6.6), (8, 0.8, 4.6), "w1_shell")
    r.cube("body", (2.2, 10.2, 4.4), (2.2, 0.6, 2), "moss")               # moss grown on the old shell
    r.cube("body", (-5.8, 8.6, 2), (1.6, 0.8, 2), "moss")
    # the shield: a heater-shield pronotum rising over the head
    for x, y, w, h in ((-6.5, 9, 13, 5.6), (-5.5, 7, 11, 2.2), (-4, 5.6, 8, 1.6), (-2, 4.8, 4, 1)):
        r.cube("body", (x, y, -7.6), (w, h, 1.6), "w1_plate_rim")
    for x, y, w, h in ((-5.6, 9.4, 11.2, 4.4), (-4.6, 7.4, 9.2, 2), (-3.1, 6, 6.2, 1.4)):
        r.cube("body", (x, y, -8.1), (w, h, 0.6), "w1_plate")
    r.cube("body", (-1.7, 8.8, -8.8), (3.4, 3.4, 0.9), "w1_plate_rim")    # boss
    r.cube("body", (-0.8, 9.7, -9.2), (1.6, 1.6, 0.5), "w1_stud")
    for x, y in ((-4.8, 12), (3.6, 12), (-3.6, 7.6), (2.4, 7.6)):
        r.cube("body", (x, y, -8.4), (1.2, 1.2, 0.5), "w1_plate_rim")      # studs
    r.cube("body", (-4.4, 10.6, -8.3), (2.6, 0.3, 0.3), "w1_scratch")     # battle scratches
    r.cube("body", (2.2, 9.8, -8.3), (0.3, 2.2, 0.3), "w1_scratch")
    for s in (1, -1):
        r.cube("body", (s * 6.2 - 0.7, 14.4, -7.4), (1.4, 1.2, 1.4), "w1_plate_rim")   # crest spikes
    r.cube("body", (-1, 14.4, -7.4), (2, 1.6, 2), "w1_plate_rim")         # horn
    r.cube("body", (-0.7, 15.8, -8.4), (1.4, 1.2, 1.8), "w1_plate_rim")
    r.cube("body", (-0.4, 16.8, -9.4), (0.8, 0.8, 1.4), "w1_stud")
    # head peering out beneath the shield
    r.bone("head", "body", (0, 4, -6), role="head")
    r.cube("head", (-3.5, 1.4, -10.6), (7, 3.4, 4.4), "w1_shell")
    _eye(r, "head", -2.3, 3.3, -10.6, 1.6, 1.3, "w1_eye_amber")
    _eye(r, "head", 2.3, 3.3, -10.6, 1.6, 1.3, "w1_eye_amber")
    for s in (1, -1):                                                      # antennae
        r.cube("head", (s * 1.1 - 0.2, 3.8, -12), (0.4, 0.4, 1.6), "w1_claw")
        r.cube("head", (s * 1.1 - 0.2, 3.8, -12.2), (0.4, 1.8, 0.4), "w1_claw")
    jaw = r.bone("jaw", "head", (0, 2, -10), role="jaw")
    for s in (1, -1):                                                      # mandibles
        r.cube(jaw, (s * 1.7 - 0.6, 1, -12.8), (1.2, 1, 3), "w1_claw")
        r.cube(jaw, (s * 0.9 - 0.5, 1, -13.4), (1, 1, 1), "w1_claw")
    # raptorial forelegs with pincers
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 5, 6.5, -4), role=f"arm_{side}")
        x = s * 6
        r.cube(arm, (x - 1.2, 5, -5.2), (2.4, 2.4, 2.4), "w1_shell")
        r.cube(arm, (x - 0.8, 2, -4.9), (1.6, 3.6, 1.6), "w1_shell_dark")
        r.cube(arm, (x - 1.1, 0.8, -7.4), (2.2, 2, 3.4), "w1_shell")       # claw palm
        r.cube(arm, (x - 0.7, 2.4, -10), (1.4, 0.9, 2.8), "w1_claw")       # upper finger
        r.cube(arm, (x - 0.7, 0.4, -9.4), (1.4, 0.8, 2.2), "w1_claw")      # lower finger
        r.cube(arm, (x - 0.5, 1.7, -10.3), (1, 0.8, 0.6), "w1_claw")
        r.cube(arm, (x + s * 0.9 - 0.25, 4.2, -4.5), (0.5, 0.9, 0.5), "w1_stud")   # spur
    # four walking legs
    for i, (z, ang) in enumerate(((1.5, 0), (6, -28))):
        for side, s in (("l", 1), ("r", -1)):
            role = f"leg_{side}" if i == 0 else f"leg_{'r' if side == 'l' else 'l'}"
            pv = (s * 4.8, 4.5, z)
            leg = r.bone(f"leg_{side}{i}", None, pv, role=role)
            a = [0, s * ang, 0]
            r.cube(leg, (4.4 if s > 0 else -8, 3.6, z - 0.8), (3.6, 1.6, 1.6), "w1_shell", rot=a, pivot=pv)
            r.cube(leg, (7 if s > 0 else -8.4, 0.6, z - 0.6), (1.4, 3.6, 1.2), "w1_shell_dark", rot=a, pivot=pv)
            r.cube(leg, (7.2 if s > 0 else -8.6, 0, z - 1), (1.4, 0.7, 1.8), "w1_claw", rot=a, pivot=pv)
    return r
