"""World 10, The Giant Workshop: where the nesting dolls were made.

Its creatures are colossal versions of earlier ones, rebuilt by the workshop: stitched seams, cloth patches,
pins left in, painted wood and lacquer like a matryoshka, gold trim, wind-up keys. Hinge convention as in w09:
in game a negative X keyframe lifts the front of a back-hinged part, so lower jaws rest agape and snap shut.
"""
from common import Rig, mat

mat("thread", "e8e0cc", "ffffff", "skin")
mat("thread_red", "c0302a", "e86a5a", "skin")
mat("pin_head", "d8302a", "ff9080", "skin")
mat("pin_steel", "a8acb4", "e8ecf0", "metal")
mat("button", "3a2a5a", "8a6ab0", "metal")
mat("patch_check", "d8b878", "8a5a3a", "cloth")
mat("patch_blue", "3a5aa0", "8aa8e0", "cloth")
mat("doll_wood", "d8b080", "f0d0a0", "bark")
mat("lacquer_blue", "1e3a7a", "e8c050", "lacquer")
mat("lacquer_green", "1e5a34", "e8c050", "lacquer")
mat("cheek", "e0605a", "ff9a90", "skin")
mat("doll_face", "f2dcc0", "ffeedd", "skin")
mat("cap_giant", "a8282c", "c03a3a", "skin")
mat("cap_spot", "f0e6d0", "ffffff", "skin")
mat("cap_lacquer", "b3261e", "e8c050", "lacquer")
mat("spore_skin", "b8c886", "8aa050", "skin")
mat("gill_w", "e8d0a0", "a89060", "cloth")
mat("ash_body", "3a2e2a", "5a4a40", "metal")
mat("ash_crust", "3e3230", "a8481a", "blocks")
mat("forge_glow", "ff6a1a", "ffd060", "magma", True)
mat("robe_lacquer", "1e1c28", "2e2c3c", "cloth")
mat("hood_red", "a82020", "d04a3a", "cloth")
mat("lac_red", "b3261e", "d8483a", "skin")
mat("doll_hair", "2a1a12", "4a2e1e", "fur")
mat("canvas", "dccfb0", "b8a684", "cloth")
mat("canvas_storm", "2a426e", "4a6aa0", "cloth")
mat("storm_belly", "3a5a8a", "c8d8f0", "cloud")
mat("w10_prowler_hide", "262436", "302e44", "fur")
mat("plate_black", "16141c", "3a3444", "metal")
mat("prowler_skin", "2a2636", "46405a", "skin")
mat("ear_membrane", "5a3a5a", "a87aa8", "membrane")


def _stitch_row(r, bone, start, step, n, face_z=None, face_x=None, mat_="thread", vertical=False):
    """Cross stitches: n small bars along x (or along y if vertical), each a pair of bars like an X seen flat."""
    x, y, z = start
    for i in range(n):
        if vertical:
            r.cube(bone, (x - 0.5, y + i * step, z), (1.2, 0.3, 0.3) if face_z is not None else (0.3, 0.3, 1.2), mat_)
        else:
            r.cube(bone, (x + i * step, y - 0.5, z), (0.3, 1.2, 0.3) if face_z is not None else (0.3, 1.2, 0.3), mat_)


def _pin(r, bone, x, y, z, h=3.0, head="pin_head", up=True):
    """A dressmaker's pin pushed into the creature."""
    r.cube(bone, (x - 0.2, y, z - 0.2), (0.4, h, 0.4), "pin_steel")
    r.cube(bone, (x - 0.6, y + h, z - 0.6), (1.2, 1.2, 1.2), head)


# ================================================================== Giant Sporeling
def giant_sporeling():
    """A sporeling grown to giant size and mended by the workshop: one glowing eye and one sewn-on button,
    rosy painted cheeks, a lacquered cap patch with gold trim, pins left in the cap, a wooden replacement arm
    and peg leg, a brass wind-up key in its back and little sporelings budding on its shoulders."""
    r = Rig("giant_sporeling")
    r.bone("body", None, (0, 7, 0), role="body")
    r.cube("body", (-5, 6, -4), (10, 8.5, 8), "spore_skin")
    r.cube("body", (-4.6, 5.4, -3.6), (9.2, 1.6, 7.2), "gill_w")          # belt of gills
    r.cube("body", (-3.2, 7.4, -4.4), (5, 4.6, 0.5), "patch_check")       # a sewn-on patch
    for y in (7.6, 9.2, 10.8):
        r.cube("body", (-3.5, y, -4.6), (0.4, 0.4, 0.3), "thread_red")
        r.cube("body", (1.6, y, -4.6), (0.4, 0.4, 0.3), "thread_red")
    for y in (7.4, 8.8, 10.2, 11.6, 13.0):                                 # a long seam down its side
        r.cube("body", (4.85, y, -1), (0.4, 0.3, 2), "thread")
    r.cube("body", (4.9, 7, -0.15), (0.3, 6.8, 0.3), "maw")
    # brass wind-up key in its back
    r.cube("body", (-0.6, 9.4, 4), (1.2, 1.2, 3), "brass")
    r.cube("body", (-3.2, 8.4, 6.8), (2.8, 3.2, 0.8), "brass")
    r.cube("body", (0.4, 8.4, 6.8), (2.8, 3.2, 0.8), "brass")
    r.cube("body", (-2.4, 9.2, 6.6), (1.2, 1.6, 1.2), "gold")
    r.cube("body", (1.2, 9.2, 6.6), (1.2, 1.6, 1.2), "gold")
    # head under the cap
    h = r.bone("head", "body", (0, 14, 0), role="head")
    r.cube(h, (-5.5, 14, -4.8), (11, 7.2, 9.6), "spore_skin")
    r.cube(h, (-4.6, 16.2, -5.2), (3.6, 3.0, 0.6), "ink")                  # the real eye, glowing in its socket
    r.cube(h, (-4.2, 16.6, -5.4), (2.8, 2.2, 0.5), "eye_violet")
    r.cube(h, (-3.2, 16.6, -5.5), (0.8, 2.2, 0.3), "pupil")
    r.cube(h, (-5.6, 13.6, -5.0), (11.2, 0.8, 9.8), "gold")               # gold collar where the head was sewn on
    r.cube(h, (1.0, 16.4, -5.4), (3.2, 3.0, 0.8), "button")                # a button sewn on in place of the other
    r.cube(h, (1.4, 17.7, -5.7), (2.4, 0.4, 0.3), "thread")
    r.cube(h, (2.4, 16.8, -5.7), (0.4, 2.2, 0.3), "thread")
    r.cube(h, (-5.2, 15.0, -5.1), (2, 1.2, 0.4), "cheek")                  # painted matryoshka cheeks
    r.cube(h, (3.2, 15.0, -5.1), (2, 1.2, 0.4), "cheek")
    jaw = r.bone("jaw", h, (0, 14.8, -3), role="jaw")
    r.cube(jaw, (-3, 13.2, -5.4), (6, 1.6, 1.4), "maw")                    # mouth hangs open
    for x in (-2.6, -1.0, 0.6, 2.0):
        r.cube(jaw, (x, 14.6, -5.6), (0.7, 0.9, 0.4), "tooth")
    r.cube(h, (-2.8, 14.4, -5.0), (5.6, 0.6, 0.3), "pupil")
    # the cap: spotted, a lacquered patch, gold trim, pins and a stitched tear
    hb = next(b for b in r.bones if b["name"] == h)
    n0 = len(hb["cubes"])
    r.cube(h, (-10, 19.6, -9.5), (20, 3.6, 19), "cap_giant")
    r.cube(h, (-10.2, 19.4, -9.7), (20.4, 0.8, 19.4), "gold")              # gold trim at the brim
    r.cube(h, (-8, 23.2, -7.5), (16, 2.8, 15), "cap_giant")
    r.cube(h, (-5, 26, -4.5), (10, 1.6, 9), "cap_giant")
    r.cube(h, (-9.4, 19.2, -9), (18.8, 0.6, 18), "gill_w")                 # gills under the brim
    r.cube(h, (1.5, 23.0, -7.9), (6, 3.2, 6), "cap_lacquer")               # a painted lacquer patch
    for z in (-7.4, -5.4, -3.4):
        r.cube(h, (1.2, 25.8, z), (0.4, 0.4, 1), "thread")
    for x in (2.0, 4.0, 6.0):
        r.cube(h, (x, 25.8, -8.1), (1, 0.4, 0.4), "thread")
    for x in (-7, -5, -3, -1):                                             # stitched tear on the cap
        r.cube(h, (x, 23.0, -8.2), (0.4, 1.4, 1.2), "thread_red")
    r.cube(h, (-7.6, 23.6, -8.0), (7.4, 0.3, 0.5), "maw")
    for x, y, z, w in ((-8.4, 22.0, -8.0, 2.6), (6.2, 22.4, 2.4, 2.4), (-3.4, 25.6, -5.6, 3.0), (-4.6, 27.0, 1.0, 2.0), (2.0, 27.0, -2.2, 2.8),
                       (-9.9, 20.6, 0.0, 2.6), (9.4, 20.6, -3.0, 2.0), (-2.0, 21.0, 9.1, 3.0)):
        r.cube(h, (x, y, z), (w if abs(x) < 9 else 0.8, 1.2 if abs(x) < 9 and z > -9 else w * 0.6, w if abs(x) < 9 else w), "cap_spot")
    _pin(r, h, 6.5, 26.0, 3.5, 1.0, head="gold")
    _pin(r, h, -8, 23.2, 4, 2.2, head="patch_blue")
    for c in hb["cubes"][n0:]:                     # set the whole cap a little higher and further back, so the face shows
        c["origin"][1] = round(c["origin"][1] + 0.4, 3)
        c["origin"][2] = round(c["origin"][2] + 1.6, 3)
    # buds: little sporelings sprouting on the shoulders
    for x, s in ((5.2, 1), (-6.8, -1)):
        r.cube("body", (x, 14.2, -1), (1.6, 1.4, 1.6), "spore_skin")
        r.cube("body", (x - 0.8, 15.6, -1.8), (3.2, 1.2, 3.2), "cap_toxic")
        r.cube("body", (x + 0.2, 16.6, -0.8), (1.2, 0.6, 1.2), "toxic")
    # left arm: flesh with a bandage; right arm: a carved wooden doll arm with gold rings
    al = r.bone("arm_l", "body", (6, 13.5, 0), role="arm_l")
    r.cube(al, (5.2, 6.5, -1.6), (3.2, 7.6, 3.2), "spore_skin")
    r.cube(al, (5.0, 9, -1.8), (3.6, 2, 3.6), "cloth_grey")
    r.cube(al, (4.8, 5.0, -2.4), (4, 2, 4), "gill_w")
    for x in (4.9, 6.4, 7.9):
        r.cube(al, (x, 4.0, -2.6), (0.8, 1.2, 1.2), "tooth")
    ar = r.bone("arm_r", "body", (-6, 13.5, 0), role="arm_r")
    r.cube(ar, (-8.4, 6.5, -1.5), (3, 7.6, 3), "doll_wood")
    r.cube(ar, (-8.7, 12.0, -1.8), (3.6, 1, 3.6), "gold")
    r.cube(ar, (-8.7, 9.0, -1.8), (3.6, 1.4, 3.6), "cap_lacquer")
    r.cube(ar, (-8.8, 4.6, -2.2), (3.8, 2.4, 3.8), "doll_wood")            # round wooden fist
    r.cube(ar, (-8.4, 6.9, -1.9), (3, 0.5, 3.4), "gold")
    _pin(r, ar, -7, 12.4, -2.6, 1.6)
    # legs: one flesh, one a lacquered peg
    ll = r.bone("leg_l", "body", (2.6, 7, 0), role="leg_l")
    r.cube(ll, (0.8, 1, -1.8), (3.6, 6.5, 3.6), "spore_skin")
    r.cube(ll, (0.5, 0, -2.8), (4.2, 1.4, 4.6), "fungus")
    lr = r.bone("leg_r", "body", (-2.6, 7, 0), role="leg_r")
    r.cube(lr, (-4.2, 4, -1.6), (3.2, 3.5, 3.2), "spore_skin")
    r.cube(lr, (-3.6, 0, -1.0), (2, 4.5, 2), "doll_wood")                  # wooden peg leg
    r.cube(lr, (-3.9, 3.6, -1.3), (2.6, 0.8, 2.6), "gold")
    r.cube(lr, (-3.8, 1.6, -1.2), (2.4, 0.8, 2.4), "cap_lacquer")
    r.cube(lr, (-4.0, 0, -1.4), (2.8, 0.6, 2.8), "wood_dark")
    for i, (x, y, z) in enumerate(((11, 18, 2), (-11, 15, -2), (4, 26, 7))):
        o = r.bone(f"spore{i}", h, (0, 18, 0), role="orbit")
        r.cube(o, (x - 0.7, y, z - 0.7), (1.4, 1.4, 1.4), "toxic")
    return r


# ================================================================== Ash Titanid
def ash_titanid():
    """A hunched smith of ash and lava rebuilt as a doll: a red lacquer headscarf framing a painted doll mask
    with ember eyes, a furnace grate in its chest, black lacquer plates with gold trim, a riveted leather apron,
    chimneys smoking on its back, a forge hammer, a giant sewing pin through one pauldron."""
    r = Rig("ash_titanid")
    r.bone("body", None, (0, 13, 0), role="body")
    r.cube("body", (-7, 18, -5), (14, 7, 10), "ash_body")                 # chest
    r.cube("body", (-5.6, 12, -4.2), (11.2, 6.6, 8.4), "ash_body")         # narrower waist
    r.cube("body", (-7.5, 21, -6), (15, 6, 12), "ash_crust")              # hunched shoulders
    r.cube("body", (-4.6, 14.4, -5.6), (9.2, 7.4, 0.8), "lacquer_black")   # lacquer frame around the furnace
    r.cube("body", (-3.6, 15.2, -5.9), (7.2, 5.6, 0.5), "forge_glow")     # the furnace in its chest
    for x in (-2.6, -0.8, 1.0, 2.6):
        r.cube("body", (x - 0.25, 15.0, -6.2), (0.5, 6, 0.4), "iron")      # grate bars
    r.cube("body", (-4.8, 21.6, -6.3), (9.6, 0.6, 0.5), "gold")
    r.cube("body", (-4.8, 14.0, -6.0), (9.6, 0.6, 0.5), "gold")
    for x, y, w, hh in ((-6.4, 13, 0.5, 5), (5.6, 16, 0.5, 4), (5.6, 16, 1.6, 0.5)):
        r.cube("body", (x, y, -5.25), (w, hh, 0.3), "magma")              # cracks of lava
    r.cube("body", (7.05, 14, -2), (0.3, 6, 0.5), "magma")
    # leather apron with rivets
    r.cube("body", (-5, 9, -5.8), (10, 5.6, 0.6), "leather")
    for x in (-4.2, 3.4):
        r.cube("body", (x, 13.6, -6.1), (0.8, 0.8, 0.3), "gold")
    r.cube("body", (-5.2, 12.2, -5.4), (10.4, 1.2, 10.8), "lacquer_black")  # belt
    r.cube("body", (-1.2, 11.9, -5.8), (2.4, 1.8, 0.4), "gold")             # buckle
    # chimneys on its back
    for x in (-4, 3):
        r.cube("body", (x - 0.2, 24, 3), (2.4, 7, 2.4), "iron")
        r.cube("body", (x - 0.6, 30.6, 2.6), (3.2, 1, 3.2), "gold")
        r.cube("body", (x + 0.2, 31.4, 3.4), (1.6, 0.8, 1.6), "ember")
    # head, thrust forward: a lacquer headscarf around a painted doll mask
    h = r.bone("head", "body", (0, 25, -3), role="head")
    r.cube(h, (-4.2, 23.6, -9.4), (8.4, 7.6, 7.4), "hood_red")
    r.cube(h, (-4.4, 30.6, -8.8), (8.8, 0.8, 6.8), "gold")
    r.cube(h, (-1.2, 31.2, -6.4), (2.4, 1.6, 2.4), "hood_red")           # the scarf's knot
    r.cube(h, (-3.2, 24.6, -9.9), (6.4, 5.4, 0.8), "doll_face")          # the mask
    r.cube(h, (-3.6, 30.0, -10.0), (7.2, 0.6, 1), "gold")
    r.cube(h, (-3.6, 24.2, -10.0), (0.6, 6.2, 1), "gold")
    r.cube(h, (3.0, 24.2, -10.0), (0.6, 6.2, 1), "gold")
    r.cube(h, (-3.2, 28.6, -10.15), (6.4, 1.4, 0.4), "doll_hair")        # painted hair parting under the scarf
    r.cube(h, (-2.7, 27.0, -10.2), (2.2, 1.3, 0.4), "ink")               # ember eyes in painted lids
    r.cube(h, (-2.4, 27.2, -10.35), (1.6, 0.9, 0.3), "ember")
    r.cube(h, (0.5, 27.0, -10.2), (2.2, 1.3, 0.4), "ink")
    r.cube(h, (0.8, 27.2, -10.35), (1.6, 0.9, 0.3), "ember")
    r.cube(h, (-2.8, 25.8, -10.1), (1.4, 0.9, 0.3), "cheek")
    r.cube(h, (1.4, 25.8, -10.1), (1.4, 0.9, 0.3), "cheek")
    r.cube(h, (1.2, 26.2, -10.15), (0.4, 3.2, 0.3), "ash_body")          # a crack across the mask
    jaw = r.bone("jaw", h, (0, 25, -6), role="jaw")
    r.cube(jaw, (-2.6, 22.6, -10.2), (5.2, 2, 2.4), "ash_body")          # glowing maw, open
    r.cube(jaw, (-2.0, 24.0, -10.0), (4, 1, 1), "forge_glow")
    # shoulders: red lacquer pauldrons, a sewing pin through one
    for s in (1, -1):
        r.cube("body", (s * 7 - 4, 24.4, -4.5), (8, 4.2, 9), "lac_red")
        r.cube("body", (s * 7 - 1.2, 28.5, -1.4), (2.4, 0.5, 2.4), "gold")                 # painted flower on top
        r.cube("body", (s * 7 - 0.5, 28.8, -0.7), (1, 0.4, 1), "spark")
        r.cube("body", (s * 7 - 4.2, 24.2, -4.7), (8.4, 0.8, 9.4), "gold")
    _pin(r, "body", 8, 25, -1, 6, head="gold")
    # arms: massive forearms
    for side, s in (("l", 1), ("r", -1)):
        a = r.bone(f"arm_{side}", "body", (s * 9.5, 25, 0), role=f"arm_{side}")
        r.cube(a, (s * 9.5 - 2.5, 15.5, -2.5), (5, 9, 5), "ash_body")
        r.cube(a, (s * 9.5 - 3.2, 7.5, -3.2), (6.4, 8.6, 6.4), "ash_crust")    # forearm
        r.cube(a, (s * 9.5 - 3.5, 11, -3.5), (7, 3, 7), "lacquer_black")
        r.cube(a, (s * 9.5 - 3.6, 13.6, -3.6), (7.2, 0.6, 7.2), "gold")
        r.cube(a, (s * 9.5 - 3.4, 3.6, -3.6), (6.8, 4.4, 7), "ash_body")       # fist
        r.cube(a, (s * 9.5 - 3.5, 5.0, -3.8), (7, 0.6, 0.3), "magma")      # glowing knuckles
        r.cube(a, (s * 9.5 + s * 3.25 - 0.15, 8, -1), (0.3, 6, 0.5), "magma")        # lava seams up the forearm
        r.cube(a, (s * 9.5 - 0.5, 8, -3.35), (0.5, 3, 0.3), "magma")
        r.cube(a, (s * 9.5 - 1, 2.6, -1), (2, 1.2, 2), "forge_glow")              # molten drip under the fist
        _stitch_row(r, a, (s * 9.5 - 2, 19, -2.75), 1.2, 4, face_z=True)
    # forge hammer in the left fist (the one that leads Forge Hammer), tongs and a glowing ingot in the right
    hm = r.bone("hammer", "arm_l", (9.5, 5, 0))
    r.cube(hm, (8.6, 2.5, -10), (1.8, 1.8, 14), "wood_dark")              # haft held forward
    r.cube(hm, (6.2, 0, -15.5), (6.6, 7.2, 6), "iron")
    r.cube(hm, (6.0, 0.8, -15.7), (7, 1, 6.4), "gold")
    r.cube(hm, (6.0, 4.4, -15.7), (7, 1, 6.4), "gold")
    r.cube(hm, (6.8, 1.8, -15.9), (5.4, 2.4, 0.4), "forge_glow")         # white-hot face
    tg = r.bone("tongs", "arm_r", (-9.5, 5, 0))
    r.cube(tg, (-10.4, 1.2, -9), (0.6, 0.6, 6), "iron")
    r.cube(tg, (-9.0, 1.2, -9), (0.6, 0.6, 6), "iron")
    r.cube(tg, (-11.2, 0.4, -11.6), (3.2, 1.6, 2.8), "forge_glow")       # the ingot being forged
    # legs
    for side, s in (("l", 1), ("r", -1)):
        l = r.bone(f"leg_{side}", "body", (s * 3.8, 12, 0), role=f"leg_{side}")
        r.cube(l, (s * 3.8 - 2.8, 3, -2.8), (5.6, 9.6, 5.6), "ash_body")
        r.cube(l, (s * 3.8 - 3.1, 4, -3.2), (6.2, 4.6, 6), "lacquer_black")   # greave
        r.cube(l, (s * 3.8 - 3.2, 8.4, -3.3), (6.4, 0.6, 6.2), "gold")
        r.cube(l, (s * 3.8 - 3.4, 0, -4.8), (6.8, 3.2, 8), "ash_crust")        # heavy boot
        r.cube(l, (s * 3.8 - 3.0, 0.4, -5.0), (6, 0.6, 0.4), "magma")
        r.cube(l, (s * 3.8 + s * 2.85 - 0.15, 9, -1), (0.3, 3, 0.5), "magma")
    for i, (x, y, z) in enumerate(((10, 30, -4), (-11, 27, 3), (2, 34, 6))):
        o = r.bone(f"ember{i}", "body", (0, 26, 0), role="orbit")
        r.cube(o, (x - 0.5, y, z - 0.5), (1, 1, 1), "ember")
    return r


# ================================================================== Colossal Jailer
def colossal_jailer():
    """A jailer the size of a house, shaped like a nesting doll: a black lacquer body with gold trim panels,
    a red doll scarf around an iron visor with glowing slits over a painted smile, a key ring as large as a shield
    hanging from its left arm, an iron gavel in its right, a belt of chains and padlocks."""
    r = Rig("colossal_jailer")
    r.bone("body", None, (0, 12, 0), role="body")
    r.cube("body", (-8, 2, -7), (16, 9, 14), "robe_lacquer")              # the doll's wide base
    r.cube("body", (-7, 10, -6), (14, 11, 12), "robe_lacquer")
    r.cube("body", (-8.2, 2, -7.2), (16.4, 1.2, 14.4), "gold")            # hem trim
    r.cube("body", (-3.6, 3.2, -7.5), (7.2, 15, 0.6), "lacquer")          # painted front panel
    r.cube("body", (-3.9, 3.2, -7.6), (0.5, 15, 0.6), "gold")             # gold trim framing the panel
    r.cube("body", (3.4, 3.2, -7.6), (0.5, 15, 0.6), "gold")
    r.cube("body", (-7.2, 19.4, -6.2), (14.4, 0.8, 12.4), "gold")         # collar trim
    r.cube("body", (-1.6, 9.6, -7.9), (3.2, 3.2, 0.5), "gold")            # keyhole emblem
    r.cube("body", (-0.5, 7.4, -8.1), (1, 2.6, 0.4), "gold")
    r.cube("body", (-0.6, 10.4, -8.2), (1.2, 1.2, 0.3), "lacquer_black")
    for x, y in ((-2.6, 5), (1.6, 5), (-2.6, 14.6), (1.6, 14.6)):
        r.cube("body", (x, y, -7.8), (1, 1, 0.4), "gold")                 # painted flowers
    # belt of chain with padlocks
    r.cube("body", (-7.4, 11, -6.4), (14.8, 1.4, 12.8), "chain")
    for x, z, sx in ((-5.6, -7.2, 0), (4.0, -7.2, 0), (7.0, -1, 1), (-7.6, 2, 1)):
        size = (1.8, 2.2, 1) if not sx else (1, 2.2, 1.8)
        r.cube("body", (x, 8.6, z), size, "gold")
        r.cube("body", (x + (0.4 if not sx else 0.1), 10.6, z + (0.1 if not sx else 0.4)), (1 if not sx else 0.8, 1, 0.8 if not sx else 1), "iron")
    for i, x in enumerate((-6.5, 5.6)):                                    # hanging chain loops
        r.cube("body", (x, 5, -7.3), (0.8, 6, 0.6), "chain")
    # head: red scarf, iron visor, painted smile
    h = r.bone("head", "body", (0, 21, 0), role="head")
    r.cube(h, (-5.5, 20.5, -5.5), (11, 10, 11), "hood_red")
    r.cube(h, (-4, 30.4, -4), (8, 1.2, 8), "hood_red")
    r.cube(h, (-5.7, 20.5, -5.7), (11.4, 0.8, 11.4), "gold")
    r.cube(h, (-4, 21.4, -6.0), (8, 7.6, 1), "doll_face")
    r.cube(h, (-4.4, 21.0, -6.3), (8.8, 0.6, 1), "gold")                   # gold rim of the face opening
    r.cube(h, (-4.4, 28.8, -6.3), (8.8, 0.6, 1), "gold")
    r.cube(h, (-4.2, 25.2, -6.4), (8.4, 3.4, 0.8), "iron")                # visor over the eyes
    r.cube(h, (-3.2, 26.4, -6.6), (2.4, 0.7, 0.3), "ice_glow")
    r.cube(h, (0.8, 26.4, -6.6), (2.4, 0.7, 0.3), "ice_glow")
    for x in (-3.8, 3.4):
        r.cube(h, (x, 25.5, -6.7), (0.5, 0.5, 0.3), "gold")                # visor rivets
    r.cube(h, (-3.6, 22.8, -6.15), (1.6, 1, 0.3), "cheek")
    r.cube(h, (2.0, 22.8, -6.15), (1.6, 1, 0.3), "cheek")
    jaw = r.bone("jaw", h, (0, 22.4, -3), role="jaw")
    r.cube(jaw, (-1.8, 21.6, -6.25), (3.6, 0.6, 0.3), "maw")              # painted smile
    r.cube(jaw, (-2.4, 22.2, -6.25), (0.6, 0.6, 0.3), "maw")
    r.cube(jaw, (1.8, 22.2, -6.25), (0.6, 0.6, 0.3), "maw")
    _pin(r, h, 3, 31.4, 2, 2.2, head="gold")
    for sx in (-1, 1):                                                     # painted flowers on the scarf
        x = 5.5 if sx > 0 else -5.8
        r.cube(h, (x, 24, -1.5), (0.3, 3, 3), "gold")
        r.cube(h, (x + (0.05 if sx > 0 else -0.05), 24.8, -0.7), (0.3, 1.4, 1.4), "lac_red")
    r.cube(h, (-1.6, 19.2, 5.2), (3.2, 2.4, 1.4), "hood_red")             # the scarf knot at the back
    r.cube(h, (-2.4, 15.4, 5.6), (1.8, 4, 0.6), "hood_red")
    r.cube(h, (0.6, 16.2, 5.6), (1.8, 3.2, 0.6), "hood_red")
    # arms in wide sleeves
    for side, s in (("l", 1), ("r", -1)):
        a = r.bone(f"arm_{side}", "body", (s * 8.5, 19.5, 0), role=f"arm_{side}")
        r.cube(a, (s * 8.5 - 2.5, 12, -2.5), (5, 9, 5), "robe_lacquer")
        r.cube(a, (s * 8.5 - 3, 8, -3), (6, 5, 6), "robe_lacquer")        # wide cuff
        r.cube(a, (s * 8.5 - 3.2, 8, -3.2), (6.4, 0.8, 6.4), "gold")
        r.cube(a, (s * 8.5 - 2, 5, -2), (4, 3.4, 4), "iron")                # gauntlet
    # the key ring, big as a shield, on the left arm
    kr = r.bone("keyring", "arm_l", (12.5, 7, 0))
    r.cube(kr, (12, 0, -7), (1.2, 1.4, 14), "gold")
    r.cube(kr, (12, 12.6, -7), (1.2, 1.4, 14), "gold")
    r.cube(kr, (12, 0, -7), (1.2, 14, 1.4), "gold")
    r.cube(kr, (12, 0, 5.6), (1.2, 14, 1.4), "gold")
    r.cube(kr, (11.2, 6, -1), (2.8, 2, 2), "iron")                         # clasp on the gauntlet
    for i, z in enumerate((-4.5, -1.2, 2.2)):                              # giant keys hanging from the ring
        L = 7.5 - i * 1.2
        r.cube(kr, (12.85, 12.6 - 3.4, z - 1.4), (0.9, 3.4, 3.2), "pin_steel")  # bow
        r.cube(kr, (12.75, 12.6 - 2.6, z - 0.6), (1.1, 1.6, 1.6), "ink")
        r.cube(kr, (12.9, 9.2 - L, z - 0.4), (0.8, L, 0.8), "pin_steel")             # shaft
        r.cube(kr, (12.9, 9.2 - L, z + 0.4), (0.8, 1, 1.4), "pin_steel")             # bit
        r.cube(kr, (12.9, 9.2 - L + 1.6, z + 0.4), (0.8, 0.8, 1), "pin_steel")
    # the iron gavel in the right hand
    g = r.bone("gavel", "arm_r", (-8.5, 6, 0))
    r.cube(g, (-9.3, 5, -9), (1.6, 1.6, 11), "wood_dark")
    r.cube(g, (-12, 2, -14.5), (7, 7.5, 6), "iron")
    r.cube(g, (-12.3, 2, -14.8), (7.6, 1, 6.6), "gold")
    r.cube(g, (-12.3, 8.5, -14.8), (7.6, 1, 6.6), "gold")
    r.cube(g, (-9.6, 4.6, -15.0), (2.2, 2.2, 0.4), "lacquer")
    # iron boots peeking under the hem
    for side, s in (("l", 1), ("r", -1)):
        l = r.bone(f"leg_{side}", "body", (s * 3.6, 3, 0), role=f"leg_{side}")
        r.cube(l, (s * 3.6 - 2.4, 0, -4), (4.8, 3, 6), "iron")
        r.cube(l, (s * 3.6 - 2.4, 0, -4.4), (4.8, 1, 1), "gold")
    return r


# ================================================================== Titan Ray
def titan_ray():
    """An enormous manta of storm sewn from painted canvas like a kite: wooden battens, stitched seams,
    gold-trimmed leading edges, painted lacquer bands, storm clouds clinging underneath, lightning eyes,
    horn-like cephalic fins and a long tail ending in a tassel and a lightning barb."""
    r = Rig("titan_ray")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-6.5, 4, -11), (13, 4, 22), "canvas_storm")
    r.cube("body", (-4.6, 7.6, -9), (9.2, 1.6, 16), "lacquer_blue")       # painted ridge
    r.cube("body", (-1.2, 9.0, -7), (2.4, 0.6, 12), "gold")
    r.cube("body", (-5.4, 3, -10), (10.8, 1.2, 19), "storm_belly")
    for z in (-6, -3.6, -1.2):                                             # gill slits underneath
        r.cube("body", (-4, 2.9, z), (2.6, 0.3, 0.6), "ink")
        r.cube("body", (1.4, 2.9, z), (2.6, 0.3, 0.6), "ink")
    _stitch_row(r, "body", (-5.0, 8.3, -10.5), 2.2, 5, face_z=True)
    # head: mouth, eyes on the sides, cephalic fins
    h = r.bone("head", "body", (0, 6, -11), role="head")
    r.cube(h, (-5, 3.6, -15), (10, 4, 4.4), "canvas_storm")
    r.cube(h, (-3.6, 3.8, -15.4), (7.2, 1.4, 0.6), "maw")                  # wide mouth
    r.cube(h, (-5.3, 6, -14), (0.6, 1.4, 1.8), "lightning")                # eyes on the flanks
    r.cube(h, (4.7, 6, -14), (0.6, 1.4, 1.8), "lightning")
    r.cube(h, (-4.6, 7.4, -14.8), (9.2, 0.6, 3.6), "gold")
    for s in (1, -1):
        r.cube(h, (s * 4.5 - 1.2, 2.4, -20), (2.4, 2, 6.4), "lacquer_blue")   # cephalic fins curling forward
        r.cube(h, (s * 4.5 - 1.0, 2.2, -21.4), (2, 1.6, 1.6), "gold")
        r.cube(h, (s * 4.5 - 0.6, 3.8, -21), (1.2, 1.2, 1.2), "lacquer_blue")
    # wings: four panels each, swept back to a point; painted storm canvas on battens, gold leading edge,
    # matryoshka flowers painted on top, storm clouds clinging underneath
    for side, s in (("l", 1), ("r", -1)):
        par = "body"
        x0 = 6
        for i, (w, z0, d, th) in enumerate(((9, -10, 21, 2.0), (9, -6, 16, 1.6), (8, -1.5, 10.5, 1.2), (6, 3.5, 4.5, 0.9))):
            nm = r.bone(f"wing_{side}{i}", par, (s * x0, 6, 0), role=f"wing_{side}")
            xa = s * x0 if s > 0 else s * x0 - w
            r.cube(nm, (xa - (0.3 if s < 0 else 0), 6 - th / 2, z0), (w + 0.3, th, d), "canvas_storm")
            r.cube(nm, (xa, 6 - th / 2 - 0.1, z0 - 0.6), (w + 0.3, th + 0.2, 0.9), "gold")            # leading edge
            r.cube(nm, (xa, 6 - th / 2 - 0.15, z0 + d - 0.5), (w + 0.3, 0.4, 0.8), "canvas")          # canvas hem
            r.cube(nm, (xa + (w - 0.6 if s > 0 else 0), 6 + th / 2 - 0.2, z0), (0.6, 0.5, d), "wood_dark")  # batten
            if i < 3:
                r.cube(nm, (xa + 1, 6 - th / 2 - 1.4, z0 + d * 0.35), (w - 2, 1.4, d * 0.45), "cloud")
            if i == 0:
                r.cube(nm, (xa + 2.5, 6 + th / 2 - 0.1, z0 + 6), (4, 0.4, 4), "lac_red")                 # painted flower
                r.cube(nm, (xa + 3.7, 6 + th / 2 + 0.1, z0 + 7.2), (1.6, 0.4, 1.6), "gold")
                for k in range(4):
                    r.cube(nm, (xa + 1 + k * 2, 6 + th / 2 - 0.1, z0 + 14), (0.4, 0.3, 1.4), "thread")   # stitched seam
                r.cube(nm, (xa + 0.8, 6 + th / 2 - 0.15, z0 + 14.5), (w - 1.6, 0.3, 0.3), "maw")
            if i == 1:
                r.cube(nm, (xa + 2, 6 + th / 2 - 0.1, z0 + 5), (0.6, 0.3, 4), "lightning")                # painted lightning
                r.cube(nm, (xa + 2, 6 + th / 2 - 0.1, z0 + 8.6), (3, 0.3, 0.6), "lightning")
                r.cube(nm, (xa + 4.4, 6 + th / 2 - 0.1, z0 + 8.6), (0.6, 0.3, 4), "lightning")
            if i == 2:
                r.cube(nm, (xa + 2, 6 - 0.2, z0 + 3), (3.4, th / 2 + 0.4, 3.4), "patch_check")            # a patch
                r.cube(nm, (xa + 1.8, 6 + th / 2 + 0.1, z0 + 2.8), (0.3, 0.2, 3.8), "thread_red")
            par = nm
            x0 += w
    # tail
    par = "body"
    z = 10
    for i, (w, d) in enumerate(((3, 6), (2, 6), (1.4, 6))):
        t = r.bone(f"tail{i}", par, (0, 5.6, z), role="tail")
        r.cube(t, (-w / 2, 5.6 - w / 2, z - 0.5), (w, w, d + 0.5), "canvas" if i < 2 else "storm")
        r.cube(t, (-w / 2 - 0.1, 5.6 + w / 2 - 0.3, z + d / 2), (w + 0.2, 0.4, 0.8), "gold")
        par = t
        z += d
    r.cube(par, (-0.5, 5.6 - 2.6, z - 1), (1, 2.4, 1), "gold")              # tassel cord
    r.cube(par, (-1.2, 1.4, z - 1.6), (2.4, 2, 2.2), "thread_red")          # tassel
    r.cube(par, (-0.4, 5.2, z), (0.8, 0.8, 3), "lightning")                 # lightning barb
    r.cube(par, (-1.2, 5.2, z + 2.4), (2.4, 0.6, 0.6), "lightning")
    return r


# ================================================================== Colossus Prowler
def colossus_prowler():
    """A gigantic eyeless prowler: a smooth blind head with painted-shut doll eyes, vast fan ears that listen,
    a jaw that hangs open on a glowing soul throat, a hide painted with lacquer bands and gold rosettes,
    seams of thread across its back, pins still in it, gold-capped claws and a stitched tail."""
    r = Rig("colossus_prowler")
    r.bone("body", None, (0, 13, 0), role="body")
    r.cube("body", (-6, 8, -9), (12, 9, 19), "w10_prowler_hide")
    r.cube("body", (-6.6, 12, -10), (13.2, 7.4, 10), "w10_prowler_hide")       # shoulder hump
    r.cube("body", (-5, 7.4, -7), (10, 1.2, 15), "prowler_skin")           # belly
    # doll paint on the flanks: a big red-and-cream matryoshka flower, a red band, gold dots
    for s in (1, -1):
        x = 6.0 if s > 0 else -6.3                                         # flank face of the hind body
        xs = 6.6 if s > 0 else -6.9                                        # flank face of the shoulder hump
        r.cube("body", (xs, 12.6, -8.4), (0.3, 5.6, 6.4), "lac_red")       # flower on the shoulder
        r.cube("body", (xs + 0.1 * s, 13.8, -7.2), (0.3, 3.2, 4), "doll_face")
        r.cube("body", (xs + 0.2 * s, 14.6, -6.0), (0.3, 1.6, 1.6), "gold")
        r.cube("body", (x, 9.4, 1.5), (0.3, 7, 1.6), "lac_red")            # painted band
        r.cube("body", (x + 0.05 * s, 9.4, 3.1), (0.3, 7, 0.5), "gold")
        for z, y in ((5.5, 13), (7.5, 10.5), (8.5, 14)):
            r.cube("body", (x, y, z), (0.3, 1, 1), "gold")
    r.cube("body", (-3.5, 8.6, -10.3), (7, 7, 0.4), "doll_face")           # cream bib on the chest
    r.cube("body", (-1.5, 11, -10.5), (3, 3, 0.3), "lac_red")
    r.cube("body", (-0.6, 11.9, -10.6), (1.2, 1.2, 0.2), "gold")
    # spine: black lacquer plates with gold edge, a seam, pins
    for i, z in enumerate((-8.5, -4.5, -0.5, 3.5)):
        r.cube("body", (-2.2 + 0.2 * i, 19.2 if z < 0 else 16.8, z), (4.4 - 0.4 * i, 1.4, 3), "plate_black")
        r.cube("body", (-2.4 + 0.2 * i, (19.2 if z < 0 else 16.8) + 0.2, z - 0.2), (4.8 - 0.4 * i, 0.5, 0.4), "gold")
    for z in (0.5, 2.5, 4.5, 6.5, 8.5):
        r.cube("body", (-3.5, 16.85, z), (7, 0.3, 0.4), "thread")          # a long stitched seam across the back
    r.cube("body", (-3.4, 16.9, 0.2), (0.3, 0.2, 8.6), "maw")
    _pin(r, "body", 2.5, 17, 6, 3)
    _pin(r, "body", -3.5, 19.2, -6, 2.4, head="gold")
    # head: eyeless, painted shut
    h = r.bone("head", "body", (0, 15, -10), role="head")
    r.cube(h, (-5, 11.6, -19), (10, 8, 9.6), "prowler_skin")
    r.cube(h, (-4.2, 19.4, -18), (8.4, 1.2, 7), "w10_prowler_hide")
    r.cube(h, (-4, 16.4, -19.3), (3, 0.5, 0.4), "gold")                    # painted closed eyes, gold lashes
    r.cube(h, (1, 16.4, -19.3), (3, 0.5, 0.4), "gold")
    for x in (-3.6, -2.4, 1.4, 2.6):
        r.cube(h, (x, 15.6, -19.3), (0.3, 0.8, 0.3), "gold")
    r.cube(h, (-4.4, 14.4, -19.2), (1.8, 1, 0.3), "cheek")
    r.cube(h, (2.6, 14.4, -19.2), (1.8, 1, 0.3), "cheek")
    r.cube(h, (-1, 17.6, -19.3), (2, 1.8, 0.3), "lacquer")                 # a painted flower on the brow
    r.cube(h, (-0.4, 18.2, -19.4), (0.8, 0.6, 0.2), "gold")
    r.cube(h, (-3.6, 11.6, -21.4), (7.2, 4.2, 2.6), "prowler_skin")       # blunt muzzle
    r.cube(h, (-2.2, 14.4, -21.6), (1.2, 0.6, 0.4), "ink")                 # nostrils: it hunts by sound and smell
    r.cube(h, (1.0, 14.4, -21.6), (1.2, 0.6, 0.4), "ink")
    for x in (-3.4, -1.8, -0.4, 1.0, 2.6):
        r.cube(h, (x, 10.6, -21.2), (0.8, 1.6 if x in (-3.4, 2.6) else 1.1, 0.8), "tooth")   # upper fangs
    r.cube(h, (-3.8, 11.4, -18.6), (7.6, 0.6, 6), "maw")
    # fan ears that listen
    for s in (1, -1):
        e = r.bone(f"ear_{'l' if s > 0 else 'r'}", h, (s * 4.6, 18, -13))
        xa = s * 4.6 if s > 0 else s * 4.6 - 6
        r.cube(e, (xa, 17, -14.5), (6, 6, 0.6), "ear_membrane")
        r.cube(e, (xa + (5 if s > 0 else 0), 17, -14.6), (1, 7.4, 0.8), "w10_prowler_hide")
        r.cube(e, (xa, 17, -14.6), (6, 0.8, 0.8), "w10_prowler_hide")
        r.cube(e, (xa + (2.4 if s > 0 else 2.6), 17.6, -14.7), (1, 4.6, 0.3), "soul")
    jaw = r.bone("jaw", h, (0, 12, -11), role="jaw")
    r.cube(jaw, (-4.4, 8.0, -18.6), (8.8, 2.4, 8), "prowler_skin")         # lower jaw, hung open
    r.cube(jaw, (-3.4, 8.2, -21.0), (6.8, 2.0, 2.6), "prowler_skin")
    r.cube(jaw, (-3.6, 10.2, -18.0), (7.2, 0.6, 6.6), "soul")              # glowing throat
    for x in (-3.0, -1.2, 0.4, 2.2):
        r.cube(jaw, (x, 10.2, -20.9), (0.8, 1.4, 0.8), "tooth")
    # legs: front legs are arms (they maul), back legs drive the pounce
    for side, s in (("l", 1), ("r", -1)):
        a = r.bone(f"arm_{side}", "body", (s * 5, 13, -6), role=f"arm_{side}")
        r.cube(a, (s * 5 - 2.4, 4, -8.4), (4.8, 10, 4.8), "w10_prowler_hide")
        r.cube(a, (s * 5 - 2.6, 4.6, -8.6), (5.2, 1, 5.2), "gold")
        r.cube(a, (s * 5 - 2.8, 0, -9.6), (5.6, 4.4, 6), "prowler_skin")    # big paw
        for x in (-2.2, -0.5, 1.2):
            r.cube(a, (s * 5 + x, 0, -10.6), (1, 1.4, 1.2), "gold")        # gold-capped claws
        l = r.bone(f"leg_{side}", "body", (s * 4.4, 12, 6), role=f"leg_{side}")
        r.cube(l, (s * 4.4 - 2.4, 4, 3.6), (4.8, 9, 5.2), "w10_prowler_hide")
        r.cube(l, (s * 4.4 - 2.0, 0, 4.0), (4, 4.6, 4), "prowler_skin")
        r.cube(l, (s * 4.4 - 2.4, 0, 2.6), (4.8, 1.4, 2), "prowler_skin")
        for x in (-1.6, 0.6):
            r.cube(l, (s * 4.4 + x, 0, 1.8), (1, 1, 1), "gold")
    r.cube("arm_l", (6.3, 6, -7), (0.3, 5, 0.4), "thread")                 # a stitched foreleg
    for y in (6.5, 8, 9.5):
        r.cube("arm_l", (6.2, y, -7.4), (0.4, 0.3, 1.2), "thread")
    # tail: stitched together, ending in a tassel
    par = "body"
    z = 10
    for i, w in enumerate((3, 2.4, 1.8)):
        t = r.bone(f"tail{i}", par, (0, 15 - i, z), role="tail")
        r.cube(t, (-w / 2, 15 - i - w / 2, z - 0.5), (w, w, 6.5), "w10_prowler_hide")
        r.cube(t, (-w / 2 - 0.1, 15 - i - w / 2 - 0.1, z + 5.5), (w + 0.2, w + 0.2, 0.8), "gold" if i != 1 else "thread_red")
        par = t
        z += 6
    r.cube(par, (-0.8, 11.6, z - 1), (1.6, 1.4, 1.4), "gold")
    r.cube(par, (-1.4, 9.4, z - 1.2), (2.8, 2.4, 2.6), "thread_red")        # tassel
    return r
