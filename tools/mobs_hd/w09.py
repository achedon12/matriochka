"""World 9, Restless Ground: the earth itself is alive, blocks crawl, chests bite.

Note on hinges: GeckoLib inverts X rotations relative to the raw json math (as Blockbench does), so in game a
negative X keyframe lifts the front of a part hinged at its back and swings a hanging limb forward. Jaws here are
therefore upper parts (lids, upper skulls) or mouths that rest open and snap shut, and the Earth Hand is built
"pre-spun" (bone yawed 180 degrees) so that the same keyframes curl its fingers into the palm, toward the player.
"""
from common import Rig, mat

# ------------------------------------------------------------------ materials
mat("cb_dirt", "6a4a2e", "8f6c46", "blocks")
mat("cb_dirt_dark", "4a3220", "6a4a2e", "blocks")
mat("cb_grass", "4f8f33", "86c454", "leaf")
mat("cb_grass_dark", "3a6a26", "5a8f3a", "leaf")
mat("cb_amber", "ffb43a", "fff0b0", "glow", True)
mat("tongue", "c8485a", "f08a9a", "flesh")
mat("gum", "7a1c2a", "b8405a", "flesh")
mat("chest_wood", "a06a32", "c88e4c", "bark")
mat("chest_dark", "5e3a1c", "7c5230", "bark")
mat("chest_band", "3e3a3a", "8a8a90", "metal")
mat("gem_green", "2ad890", "c0ffe8", "crystal", True)
mat("worm_flesh", "8a5244", "b47a62", "flesh")
mat("worm_belly", "c8907a", "e8b8a0", "skin")
mat("brick", "9a4634", "c89a80", "blocks")
mat("drill", "5c5c66", "c0c4cc", "metal")
mat("gravel", "7a7470", "a8a09a", "spots")
mat("hand_earth", "6e4a30", "94704c", "blocks")
mat("hand_stone", "706a64", "9c968e", "blocks")
mat("nail", "2a2430", "6a5a8a", "crystal")
mat("col_marble", "b8ae98", "d6ceb8", "skin")
mat("col_shade", "7e7664", "a49c88", "blocks")
mat("col_groove", "5a5244", "6a6252", "skin")
mat("col_frieze", "9a917c", "c8bea6", "lacquer")
mat("bronze", "8a5a2a", "d09a4a", "metal")


def _teeth(r, bone, xs, y, z, down, mat_="tooth", d=0.8):
    """A row of teeth along x; down=True hangs them from y, else they stand up from y."""
    for i, x in enumerate(xs):
        h = (1.5 if i % 2 == 0 else 1.0)
        r.cube(bone, (x, y - h if down else y, z), (0.9, h, d), mat_)


# ================================================================== Crawling Block
def crawling_block():
    """A grass-topped dirt block that walks on four stone stumps; its top half splits along a jagged crack
    into a toothed mouth, two amber eyes peek through the cracks, roots feel the ground in front."""
    r = Rig("crawling_block")
    r.bone("body", None, (0, 4, 0), role="body")
    r.cube("body", (-7, 3, -7), (14, 6.5, 6), "cb_dirt")                  # lower lip of the block (front)
    r.cube("body", (-7, 3, -1), (14, 7.5, 8), "cb_dirt")                  # the back stays shut: a plain block
    r.cube("body", (-6.4, 9, -6.4), (12.8, 2, 6), "gum")                  # the throat seen through the crack
    _teeth(r, "body", (-5.6, -3.4, -1.0, 1.4, 3.8), 9.5, -6.9, down=False)
    r.cube("body", (5.4, 9.5, -6.9), (1, 1.8, 0.8), "tooth")              # a crooked fang at the corner
    # embedded stones and ore specks on the lower half
    r.cube("body", (-7.3, 4, -3), (0.6, 2.5, 3), "stone")
    r.cube("body", (3, 3.6, -7.3), (2.6, 2, 0.6), "stone")
    r.cube("body", (6.7, 5.5, 2), (0.6, 2, 2.5), "stone")
    r.cube("body", (-4.5, 6.5, -7.2), (1, 1, 0.4), "gold")
    r.cube("body", (6.8, 7.2, -4.5), (0.4, 1, 1), "ink")
    r.cube("body", (-2, 3.2, 6.8), (3, 1.6, 0.5), "stone")
    # a living vein cracks the flank
    r.cube("body", (7.02, 3.5, -1), (0.2, 4, 0.5), "vein")
    r.cube("body", (7.02, 6.5, -1), (0.2, 0.5, 3), "vein")
    r.cube("body", (7.02, 4.5, 1.6), (0.2, 2.5, 0.5), "vein")
    r.cube("body", (-1.2, 3.4, -7.15), (0.4, 3, 0.3), "ink")              # crack running down from the mouth
    r.cube("body", (-0.8, 3.4, -7.15), (1.6, 0.4, 0.3), "ink")
    # the top half is the jaw, hinged at the back
    jaw = r.bone("jaw", "body", (0, 10.5, 7), role="jaw")
    r.cube(jaw, (-7, 11, -7), (14, 3.6, 14), "cb_dirt")
    r.cube(jaw, (-7.3, 14.3, -7.3), (14.6, 1.2, 14.6), "cb_grass")       # grass top
    for x, h in ((-6.8, 1.4), (-1.2, 0.9), (5.2, 1.6)):
        r.cube(jaw, (x, 14.3 - h, -7.35), (1.6, h, 0.4), "cb_grass")      # grass dripping over the edges
    for x, h in ((-4.6, 1.6), (2.6, 1.0)):
        r.cube(jaw, (x, 14.3 - h, 6.95), (1.8, h, 0.4), "cb_grass")
    for z, h in ((-4.5, 1.5), (2.2, 1.9)):
        r.cube(jaw, (-7.35, 14.3 - h, z), (0.4, h, 1.6), "cb_grass")
        r.cube(jaw, (6.95, 14.3 - h, z + 1.2), (0.4, h, 1.6), "cb_grass")
    _teeth(r, jaw, (-4.6, -2.2, 0.2, 2.6, 4.8), 11.2, -6.95, down=True)
    r.cube(jaw, (-6.6, 9.6, -6.95), (1.1, 1.6, 0.8), "tooth")             # corner fang
    # eyes peeking from cracks: one wide, one squinting under a heavy brow
    r.cube(jaw, (0.9, 11.4, -7.25), (3.6, 2.6, 0.4), "ink")
    r.cube(jaw, (1.3, 11.8, -7.4), (2.8, 1.8, 0.4), "cb_amber")
    r.cube(jaw, (2.4, 11.8, -7.5), (0.7, 1.8, 0.3), "pupil")
    r.cube(jaw, (-5.0, 11.6, -7.25), (3.2, 2.0, 0.4), "ink")
    r.cube(jaw, (-4.6, 11.9, -7.4), (2.4, 1.1, 0.4), "cb_amber")
    r.cube(jaw, (-3.7, 11.9, -7.5), (0.6, 1.1, 0.3), "pupil")
    r.cube(jaw, (-5.6, 13.0, -7.8), (4.0, 1.0, 1.1), "stone")             # heavy brow stone over the squint
    r.cube(jaw, (3.6, 13.2, -7.2), (0.4, 1.1, 0.3), "ink")                # cracks running up from the eyes
    r.cube(jaw, (3.9, 12.9, -7.2), (1.4, 0.4, 0.3), "ink")
    r.cube(jaw, (-6.2, 11.4, -7.2), (0.4, 2.2, 0.3), "ink")
    r.cube(jaw, (-7.2, 12, 1), (0.4, 2.4, 2), "stone")
    # life on top: a flower, a tuft, a pebble, a red mushroom
    r.cube(jaw, (3.5, 15.5, 2.5), (0.4, 2.4, 0.4), "stem")
    r.cube(jaw, (2.9, 17.6, 1.9), (1.6, 0.6, 1.6), "petal")
    r.cube(jaw, (3.4, 18.1, 2.4), (0.6, 0.4, 0.6), "petal_inner")
    for x, h in ((-5, 1.6), (-4.4, 2.3), (-3.8, 1.3)):
        r.cube(jaw, (x, 15.5, -4.5), (0.4, h, 0.4), "cb_grass_dark")
    r.cube(jaw, (-1, 15.5, 3.5), (2.2, 0.9, 1.8), "stone")
    r.cube(jaw, (5, 15.5, -5), (0.6, 1.2, 0.6), "bone")
    r.cube(jaw, (4.4, 16.6, -5.6), (1.8, 0.8, 1.8), "cloth_red")
    # four stubby stone legs with root toes
    for i, (x, z) in enumerate(((4.4, -4.4), (-4.4, -4.4), (4.4, 4.4), (-4.4, 4.4))):
        side = "l" if x > 0 else "r"
        leg = r.bone(f"leg_{side}{i // 2}", "body", (x, 4.5, z), role=f"leg_{side}")
        r.cube(leg, (x - 1.6, 0.8, z - 1.6), (3.2, 4, 3.2), "stone_dark")
        r.cube(leg, (x - 1.9, 0, z - 2.2), (3.8, 1.2, 3.8), "stone")
        r.cube(leg, (x - 0.4, 0, z - 3.2), (0.8, 0.6, 1.2), "bark")       # root toes
        r.cube(leg, (x + (1.8 if x > 0 else -2.8), 0, z - 0.4), (1, 0.6, 0.8), "bark")
    # roots dangling at the front corners, they feel for prey and drag it under
    for side, s in (("l", 1), ("r", -1)):
        a = r.bone(f"arm_{side}", "body", (s * 5.8, 4, -6.4), role=f"arm_{side}")
        r.cube(a, (s * 5.8 - 0.7, 1.4, -7.1), (1.4, 3, 1.4), "bark")
        r.cube(a, (s * 5.8 - 0.5, 0.2, -7.8), (1, 1.6, 1.2), "bark")
        r.cube(a, (s * 5.8 - 0.3, 0.1, -8.6), (0.6, 0.6, 1), "wood_light")
    for x in (-3, 1.5, 4.5):                                               # hair roots under the belly
        r.cube("body", (x, 1.6, -7.05), (0.4, 1.6, 0.4), "bark")
    return r


# ================================================================== Mimic
def mimic():
    """A banded treasure chest on scuttling claw legs: the lid is a jaw lined with fangs, the keyhole is a
    glowing eye, a long tongue lolls over the rim, coins and a gem spill out, a torn red cape is caught in the teeth."""
    r = Rig("mimic")
    r.bone("body", None, (0, 5, 0), role="body")
    r.cube("body", (-7, 3, -5.5), (14, 6.5, 11), "chest_wood")
    r.cube("body", (-6.5, 8.5, -5), (13, 2, 10), "gum")                    # inside of the mouth
    for x in (-7.25, 6.25):                                                 # iron corner bands
        r.cube("body", (x, 3, -5.75), (1, 6.5, 1), "chest_band")
        r.cube("body", (x, 3, 4.75), (1, 6.5, 1), "chest_band")
    r.cube("body", (-7.2, 3, -5.7), (14.4, 0.8, 11.4), "chest_dark")       # dark plinth
    r.cube("body", (-7.1, 8.8, -5.62), (14.2, 0.7, 11.24), "chest_dark")   # rim
    for x in (-4.4, -1.6, 1.4, 4.2):
        r.cube("body", (x, 3.8, -5.65), (0.3, 5, 0.2), "chest_dark")       # plank seams
    _teeth(r, "body", (-6.0, -4.2, -2.2, 1.4, 3.4, 5.2), 9.5, -5.4, down=False)
    r.cube("body", (-6.3, 9.2, -0.2), (0.8, 1.2, 0.8), "tooth")
    r.cube("body", (5.5, 9.2, 1.6), (0.8, 1.2, 0.8), "tooth")
    # a forgotten arrow in its flank, a coin stuck on a tooth
    r.cube("body", (7, 6, 1), (3.4, 0.4, 0.4), "wood_light")
    r.cube("body", (10, 5.7, 0.7), (0.6, 1, 1), "feather_white")
    r.cube("body", (-3.9, 10.2, -5.6), (1.2, 1.2, 0.3), "gold")
    # lid = upper jaw, hinged at the back
    jaw = r.bone("jaw", "body", (0, 10, 5.5), role="jaw")
    r.cube(jaw, (-7, 10.6, -5.5), (14, 3.4, 11), "chest_wood")
    r.cube(jaw, (-6.6, 13.8, -5.1), (13.2, 1.4, 10.2), "chest_wood")       # rounded top
    r.cube(jaw, (-7.1, 10.5, -5.62), (14.2, 0.7, 11.24), "chest_dark")
    for x in (-4.5, 3.5):
        r.cube(jaw, (x, 10.6, -5.8), (1, 4.8, 11.6), "gold")               # gilded straps over the lid
    r.cube(jaw, (-6.8, 14.9, -0.6), (13.6, 0.5, 1.2), "chest_dark")
    r.cube(jaw, (-1.5, 9.2, -6.2), (3, 3.8, 0.8), "gold")                  # latch
    r.cube(jaw, (-1.0, 10.1, -6.4), (2, 1.8, 0.3), "eye_red")              # the keyhole is an eye
    r.cube(jaw, (-0.25, 10.1, -6.5), (0.5, 1.8, 0.2), "pupil")
    r.cube(jaw, (-1.5, 12.8, -6.3), (3, 0.5, 0.4), "chest_dark")           # eyelid ridge
    for x in (-5.4, 2.4):                                                   # little sleepy eyes in the dark seam
        r.cube(jaw, (x, 10.7, -5.7), (1.6, 0.6, 0.3), "eye_gold")
    _teeth(r, jaw, (-5.2, -3.2, 2.2, 4.4), 10.6, -5.4, down=True)
    r.cube(jaw, (-6.7, 8.6, -5.4), (1, 2, 0.9), "tooth")                   # long corner fangs
    r.cube(jaw, (5.7, 8.6, -5.4), (1, 2, 0.9), "tooth")
    r.cube(jaw, (5.8, 7.8, -5.5), (1.4, 2.6, 0.3), "cloth_red")            # torn cape caught in the fang
    r.cube(jaw, (6.4, 6.6, -5.5), (0.8, 1.4, 0.3), "cloth_red")
    # the tongue lolls over the front and lashes out
    t = r.bone("arm_r", "body", (0, 9.2, -3), role="arm_r")
    r.cube(t, (-1.6, 8.8, -7.0), (3.2, 1, 4.5), "tongue")
    r.cube(t, (-1.4, 5.0, -7.4), (2.8, 4.4, 0.9), "tongue")
    r.cube(t, (-1.1, 3.6, -7.5), (2.2, 1.6, 0.9), "tongue")
    r.cube(t, (-0.15, 3.8, -7.6), (0.3, 5.4, 0.2), "gum")                  # groove down the middle
    r.cube(t, (0.9, 2.6, -7.45), (0.5, 1.2, 0.5), "slime")                 # drool
    r.cube(t, (-1.3, 6.6, -7.8), (1.3, 1.3, 0.3), "gold")                  # a coin stuck to it
    # coins and loot spilling on the ground
    for x, z, y in ((-4.5, -8, 0), (-3.2, -9.5, 0), (2.8, -8.6, 0), (3.6, -7.4, 0.3), (-5.6, -6.8, 0.3)):
        r.cube("body", (x, y, z), (1.4, 0.4, 1.4), "gold")
    r.cube("body", (1.4, 0, -9.8), (1.2, 1.2, 1.2), "gem_green")
    r.cube("body", (-2.2, 0, -7.6), (2.4, 0.8, 1.2), "gold")               # an ingot
    # scuttling claw legs
    for i, (x, z) in enumerate(((5, -3.6), (-5, -3.6), (5, 3.4), (-5, 3.4))):
        side = "l" if x > 0 else "r"
        leg = r.bone(f"leg_{side}{i // 2}", "body", (x, 3.6, z), role=f"leg_{side}")
        o = 1.2 if x > 0 else -1.2
        r.cube(leg, (x - 0.8, 1.6, z - 0.8), (1.6, 2.6, 1.6), "chest_dark")
        r.cube(leg, (x - 0.8 + o, 0.6, z - 0.9), (1.6, 1.4, 1.8), "gum")
        r.cube(leg, (x - 0.5 + o, 0, z - 1.8), (1, 0.7, 2.4), "tooth")     # claws
        r.cube(leg, (x - 0.5 + o * 1.8, 0, z - 0.5), (1, 0.7, 1), "tooth")
    return r


# ================================================================== Foundation Eater
def foundation_eater():
    """A burrowing worm whose head is a drill crown: a ring of steel-tipped teeth around a glowing gullet,
    eaten bricks, cobble and planks stuck in its back plates, bristles along its flanks, crumbs orbiting its mouth."""
    r = Rig("foundation_eater")
    r.bone("body", None, (0, 4, -4), role="body")
    r.cube("body", (-3.8, 0.4, -5), (7.6, 7.2, 6.4), "worm_flesh")
    r.cube("body", (-3.2, 0, -4.6), (6.4, 1, 5.6), "worm_belly")
    r.cube("body", (-3.4, 7.2, -4.4), (6.8, 1, 5), "stone_dark")         # dorsal plate
    r.cube("body", (-1.8, 7.8, -3.6), (3, 1.2, 2.4), "brick")             # an eaten brick in its back
    r.cube("body", (-4.1, 2, -3.5), (0.4, 3.6, 0.4), "vein")
    r.cube("body", (3.7, 2, -3.5), (0.4, 3.6, 0.4), "vein")
    # head: drill crown with a ring mouth
    h = r.bone("head", "body", (0, 4.2, -5), role="head")
    r.cube(h, (-4.2, 0.2, -10.5), (8.4, 8, 6), "worm_flesh")
    r.cube(h, (-3.6, 0, -10), (7.2, 1, 5), "worm_belly")
    r.cube(h, (-4.6, 1.2, -11.2), (9.2, 6, 1.6), "drill")                 # the steel collar
    r.cube(h, (-3.6, 0.6, -11.2), (7.2, 7.4, 1.6), "drill")
    r.cube(h, (-2.6, 1.8, -11.6), (5.2, 4.8, 0.6), "maw")                 # the gullet
    r.cube(h, (-1.5, 2.8, -11.4), (3, 2.8, 0.4), "ember")                 # glowing throat
    r.cube(h, (-0.6, 3.6, -11.5), (1.2, 1.2, 0.3), "eye_gold")
    for x, y in ((-2.2, 5.6), (1.4, 5.6), (-2.2, 2.0), (1.4, 2.0)):
        r.cube(h, (x, y, -12.0), (0.8, 0.8, 0.8), "bone")                 # inner ring of teeth, deeper in
    for x, y, w, hh in ((-2.6, 6.2, 0.9, 1.1), (-0.5, 6.4, 1, 1.4), (1.6, 6.2, 0.9, 1.1),
                        (-2.6, 1.2, 0.9, 1.1), (-0.5, 0.9, 1, 1.4), (1.6, 1.2, 0.9, 1.1)):
        r.cube(h, (x, y - (0.6 if y > 4 else -0.2), -12.6), (w, hh * 0.7, 1.4), "tooth")   # teeth all round the ring
    for y in (2.4, 4.2):
        r.cube(h, (-3.4, y, -12.6), (1.2, 0.9, 1.4), "tooth")
        r.cube(h, (2.2, y, -12.6), (1.2, 0.9, 1.4), "tooth")
    for x, y in ((-4.4, 7.2), (3.4, 7.2), (-4.4, 0.6), (3.4, 0.6)):
        r.cube(h, (x, y, -12.8), (1, 1, 2), "iron")                       # drill bits at the four corners
    r.cube(h, (-4.6, 3.6, -9.5), (0.5, 0.5, 4.5), "vein")
    r.cube(h, (4.1, 3.6, -9.5), (0.5, 0.5, 4.5), "vein")
    r.cube(h, (-3.2, 8, -9.6), (2.4, 0.8, 2.4), "gravel")
    # upper mandible: a steel visor plate hinged at the back, it lifts to swallow
    jaw = r.bone("jaw", h, (0, 8, -6), role="jaw")
    r.cube(jaw, (-4, 7.6, -11.8), (8, 1.4, 6.4), "drill")
    r.cube(jaw, (-3, 8.8, -11.2), (6, 0.8, 4), "rust")
    for x in (-3.2, -1.4, 0.6, 2.4):
        r.cube(jaw, (x, 8.6, -12.6), (0.8, 0.8, 1.2), "tooth")
    # crumbs of eaten blocks circling the mouth
    for i, (x, y, z, m) in enumerate(((6, 6, -9, "cb_dirt"), (-6.5, 4.5, -11, "stone"), (1, 8.4, -13.5, "brick"))):
        o = r.bone(f"crumb{i}", h, (0, 4, -9), role="orbit")
        r.cube(o, (x - 0.7, y, z - 0.7), (1.4, 1.4, 1.4), m)
    # the body: segments trailing behind, each wearing a different eaten block
    par = "body"
    loot = ("cb_dirt", "stone", "wood_light", "gravel", None)
    z = 1.4
    for i, (w, hh, d) in enumerate(((7, 6.6, 5), (6.4, 6, 4.6), (5.6, 5.2, 4.2), (4.6, 4.2, 3.8), (3.4, 3.2, 3.4))):
        s = r.bone(f"seg{i}", par, (0, hh / 2 + 0.2, z - 0.4), role="seg")
        r.cube(s, (-w / 2, 0.2, z - 0.6), (w, hh, d + 0.6), "worm_flesh")
        r.cube(s, (-w / 2 + 0.5, 0, z), (w - 1, 0.8, d - 0.4), "worm_belly")
        r.cube(s, (-w / 2 - 0.2, hh * 0.35, z - 0.7), (w + 0.4, 0.6, 0.6), "vein")   # glowing seam ring
        r.cube(s, (-w / 2 + 0.3, hh - 0.2, z + 0.2), (w - 0.6, 0.9, d - 0.6), "stone_dark")
        if loot[i]:
            r.cube(s, (-w / 4 + (0.6 if i % 2 else -0.6), hh + 0.5, z + 0.8), (w / 2, 1.2, d / 2), loot[i])
        for sx in (-1, 1):                                                 # bristles
            r.cube(s, (sx * w / 2 - (0 if sx > 0 else 1.2), 0.6, z + d / 2 - 0.4), (1.2, 0.5, 0.6), "chitin_dark")
        par = s
        z += d
    tip = r.bone("tail", par, (0, 1.8, z - 0.4), role="tail")
    r.cube(tip, (-1.2, 0.6, z - 0.6), (2.4, 2.2, 3), "drill")
    r.cube(tip, (-0.6, 1.2, z + 2.2), (1.2, 1.1, 2), "iron")
    return r


# ================================================================== Earth Hand
def earth_hand():
    """A giant hand of packed earth and stone erupting from torn-up ground: knuckle plates, obsidian nails,
    glowing cracks, an eye open in the palm, moss and a sapling on its back, roots pulled up with it."""
    r = Rig("earth_hand")
    r.bone("body", None, (0, 3, 0), role="body")
    # torn-up ground ring
    for x, y, z, w, h, d, ry in ((-7.5, 0, -6, 4.5, 2.4, 4, 12), (2.5, 0, -7, 5, 1.6, 3.5, -18), (4.8, 0, -1, 3.5, 3.2, 5, 8),
                                 (-8, 0, 0.5, 3.8, 2.0, 5, -10), (-3, 0, 3.6, 6, 2.8, 3.4, 4)):
        r.cube("body", (x, y, z), (w, h, d), "cb_dirt", rot=[0, ry, 0], pivot=(x + w / 2, 0, z + d / 2))
        r.cube("body", (x + 0.3, y + h, z + 0.3), (w - 0.6, 0.5, d - 0.6), "cb_grass_dark", rot=[0, ry, 0], pivot=(x + w / 2, 0, z + d / 2))
    r.cube("body", (-4, 0, -4.5), (8, 0.6, 8), "maw")                    # the hole it tears open
    r.cube("body", (-6.5, 0, -8.5), (2, 1.2, 1.6), "stone")               # rubble
    r.cube("body", (7, 0, 3.5), (1.6, 1, 1.6), "gravel")
    r.cube("body", (-2, 0, -9.5), (1.2, 0.8, 1.2), "stone")
    # wrist and the bottom of the forearm, rooted in the ground
    r.cube("body", (-3.6, 0, -3), (7.2, 4.5, 6), "hand_earth")
    r.cube("body", (-1, 1, 2.8), (0.8, 3, 0.8), "bark")                   # roots dragged up with it
    r.cube("body", (2.4, 0.6, 2.6), (0.7, 2.6, 0.7), "bark")
    r.cube("body", (-3.7, 2, -1), (0.5, 0.5, 3), "vein")
    # the hand: built pre-spun (bone yawed 180) so the X keyframes fold it and its fingers toward the front
    P = (0, 0)

    def hc(bone, o, s, m):
        r.cube(bone, (2 * P[0] - o[0] - s[0], o[1], 2 * P[1] - o[2] - s[2]), s, m)

    def hb(name, parent, pv, role=None):
        return r.bone(name, parent, (2 * P[0] - pv[0], pv[1], 2 * P[1] - pv[2]), rot=[0, 180, 0] if parent == "body" else None, role=role)

    hand = hb("arm_r", "body", (0, 4, 0), role="arm_r")
    hc(hand, (-3.4, 3.5, -2.8), (6.8, 5, 5.6), "hand_earth")             # forearm
    hc(hand, (-3.8, 6.4, -3.2), (7.6, 1.4, 6.4), "hand_stone")            # a band of stone at the wrist
    hc(hand, (-4.6, 8, -2.6), (9.2, 6.6, 4.4), "hand_earth")              # palm
    hc(hand, (-4.3, 9, 1.6), (8.6, 4.8, 0.6), "hand_stone")               # back of the hand plate
    hc(hand, (-2.6, 10, 2.1), (3, 2.6, 0.6), "moss")
    hc(hand, (0.8, 13.6, 1.6), (0.4, 2.6, 0.4), "stem")                   # a sapling on the back of the hand
    hc(hand, (0.1, 15.9, 0.9), (1.8, 1.4, 1.8), "leaf_spring")
    hc(hand, (-3.6, 8.6, -2.75), (0.4, 4, 0.3), "vein")                   # glowing cracks in the palm
    hc(hand, (-3.6, 8.6, -2.75), (2.4, 0.4, 0.3), "vein")
    hc(hand, (2.4, 12.6, -2.75), (1.8, 0.4, 0.3), "vein")
    hc(hand, (-1.6, 9.6, -2.85), (3.2, 2.6, 0.4), "eye_white")           # the eye in the palm
    hc(hand, (-0.9, 10.0, -3.0), (1.8, 1.8, 0.3), "eye_gold")
    hc(hand, (-0.3, 10.3, -3.1), (0.6, 1.2, 0.2), "pupil")
    hc(hand, (-1.9, 12.2, -3.0), (3.8, 0.6, 0.5), "hand_stone")          # its lids of stone
    hc(hand, (-1.9, 9.1, -3.0), (3.8, 0.5, 0.5), "hand_stone")
    # thumb, jutting out sideways then up
    th = hb("thumb", hand, (4.4, 9.4, -0.6))
    hc(th, (4.2, 8.6, -2.2), (3.4, 2.8, 3.2), "hand_earth")
    hc(th, (6.4, 10.6, -2.0), (2.4, 4.0, 2.8), "hand_earth")
    hc(th, (6.6, 14.4, -1.6), (2.0, 1.2, 2.0), "nail")
    hc(th, (6.1, 11.2, 0.6), (3.0, 1.4, 0.6), "hand_stone")
    # four long fingers, spread, each a jaw bone so they curl together
    for i, (x, ln) in enumerate(((-4.6, 4.8), (-2.2, 6.2), (0.2, 6.6), (2.6, 5.6))):
        f = hb(f"finger{i}", hand, (x + 0.9, 14.2, -0.4), role="jaw")
        hc(f, (x, 13.8, -1.9), (1.9, ln * 0.5 + 0.6, 3.4), "hand_earth")
        hc(f, (x - 0.2, 13.8 + ln * 0.45, -1.6), (2.3, 1.4, 3.6), "hand_stone")   # knuckle
        hc(f, (x + 0.15, 14.6 + ln * 0.5, -1.7), (1.6, ln * 0.5, 2.9), "hand_earth")
        hc(f, (x + 0.2, 14.4 + ln, -1.9), (1.5, 1.2, 2.2), "nail")           # obsidian claw, hooked to the front
        hc(f, (x + 0.4, 14.0 + ln, -2.5), (1.1, 0.8, 0.8), "nail")
        if i == 1:
            hc(f, (x + 0.3, 14.4, -2.05), (0.4, 2.2, 0.3), "vein")
        if i == 3:
            hc(f, (x + 0.4, 14.2, 1.3), (1, 1, 0.6), "moss")
    # settle the hand a little lower into its wrist so the fingertips stay near the old height
    kids = {"arm_r", "thumb"} | {f"finger{i}" for i in range(4)}
    for b in r.bones:
        if b["name"] in kids:
            if b["name"] != "arm_r":
                b["pivot"][1] = round(b["pivot"][1] - 1.6, 3)
            for c in b["cubes"]:
                if c["origin"][1] >= 7.9:
                    c["origin"][1] = round(c["origin"][1] - 1.6, 3)
    return r


# ================================================================== Walking Column
def walking_column():
    """An ancient fluted column that tore itself out of a temple: two plinth legs, a carved face on its top drum
    with a gaping mouth, an Ionic capital with volutes still carrying a broken lintel, glowing fault lines,
    ivy climbing its back, stone arms with bronze rings, rubble orbiting it."""
    r = Rig("walking_column")
    r.bone("body", None, (0, 13, 0), role="body")
    r.cube("body", (-7.5, 11, -7.5), (15, 3.2, 15), "col_marble")         # the torus / hip plinth
    r.cube("body", (-7, 13.6, -7), (14, 1, 14), "col_shade")
    r.cube("body", (-6, 14, -6), (12, 22.4, 12), "col_marble")           # the shaft
    for x in (-4.2, -0.9, 2.4):                                            # fluting on all four faces
        r.cube("body", (x + 0.2, 14.6, -6.15), (0.8, 21, 0.3), "col_groove")
        r.cube("body", (x + 0.2, 14.6, 5.85), (0.8, 21, 0.3), "col_groove")
        r.cube("body", (-6.15, 14.6, x + 0.2), (0.3, 21, 0.8), "col_groove")
        r.cube("body", (5.85, 14.6, x + 0.2), (0.3, 21, 0.8), "col_groove")
    r.cube("body", (-6.2, 24, -6.2), (12.4, 2, 12.4), "col_frieze")       # carved frieze band
    # fault lines glowing with the living earth inside
    for x, y, w, h in ((1.4, 15, 0.5, 4), (1.4, 18.6, 2.2, 0.5), (3.2, 18.6, 0.5, 4.5), (3.2, 22.6, 2.8, 0.5),
                       (-3.6, 27, 0.5, 5), (-3.6, 27, 1.8, 0.5), (-2.2, 27, 0.5, 2.4)):
        r.cube("body", (x, y, -6.3), (w, h, 0.3), "vein")
    r.cube("body", (5.2, 29, -6.3), (1.2, 4, 3), "maw")                   # a broken-off corner
    r.cube("body", (5.4, 30, -5.8), (0.9, 2, 2), "magma")
    r.cube("body", (-6.25, 17, 3), (0.3, 6, 0.5), "vein")
    # ivy climbing the back
    for x, y, w, h in ((-5, 14, 1.4, 7), (-4.2, 20, 1.2, 5), (-3, 24, 1.6, 6), (-4.6, 16, 2.4, 1.6), (-2.6, 27, 2.6, 1.6)):
        r.cube("body", (x, y, 6.05), (w, h, 0.4), "moss")
    r.cube("body", (6.05, 30, 2), (0.4, 5, 1.2), "moss")
    # the head: the top drum with the face, and the capital
    h = r.bone("head", "body", (0, 36, 0), role="head")
    r.cube(h, (-6, 36, -6), (12, 7.4, 12), "col_marble")
    r.cube(h, (-6.1, 36, -6.1), (12.2, 0.6, 12.2), "col_shade")           # drum joint
    r.cube(h, (-5, 41.2, -6.9), (10, 1.4, 1.2), "col_shade")             # heavy brow ridge
    r.cube(h, (-5.4, 36.2, -6.3), (10.8, 5, 0.3), "col_groove")          # the carved face panel, in shadow
    for x in (-4.4, 1.2):
        r.cube(h, (x, 38.8, -6.5), (3.2, 2.4, 0.4), "ink")                # deep eye sockets
        r.cube(h, (x + 0.5, 39.2, -6.7), (2.2, 1.6, 0.3), "cb_amber")
        r.cube(h, (x + 1.3, 39.2, -6.8), (0.6, 1.6, 0.2), "pupil")
    r.cube(h, (-0.8, 37.4, -7.2), (1.6, 3.6, 1.0), "col_marble")          # nose
    r.cube(h, (-3, 36.3, -6.5), (6, 1.3, 0.4), "maw")                     # the gaping mouth
    for x in (-2.6, -1.0, 0.6, 2.0):
        r.cube(h, (x, 36.8, -6.7), (0.7, 0.8, 0.3), "col_marble")         # upper stone teeth
    r.cube(h, (4.0, 37.4, -6.3), (0.4, 3.4, 0.3), "ink")                  # crack through the cheek
    r.cube(h, (2.8, 40.6, -6.3), (0.4, 1.4, 0.3), "ink")
    jaw = r.bone("jaw", h, (0, 36.8, -3), role="jaw")
    r.cube(jaw, (-3, 34.8, -6.8), (6, 1.8, 1.6), "col_marble")            # chin slab, rests dropped open
    for x in (-2.2, -0.2, 1.6):
        r.cube(jaw, (x, 36.4, -6.5), (0.7, 0.7, 0.3), "col_marble")
    r.cube(h, (-7.2, 43.4, -7.2), (14.4, 2.2, 14.4), "col_marble")        # echinus
    for sx in (-1, 1):                                                     # Ionic volutes, front and back
        for zz in (-7.6, 6.6):
            r.cube(h, (sx * 7.6 - (2.2 if sx > 0 else -0.2) - (0 if sx > 0 else 2), 42.6, zz), (2.8, 2.8, 1), "col_marble")
            r.cube(h, (sx * 7.6 - (1.4 if sx > 0 else -0.6) - (0 if sx > 0 else 1.6), 43.3, zz - 0.15), (1.2, 1.2, 1.3), "col_groove")
    r.cube(h, (-8.4, 45.6, -8.4), (16.8, 2.2, 16.8), "col_marble")       # abacus
    r.cube(h, (-8.5, 45.6, -8.5), (16.8, 0.5, 16.8), "col_shade")
    r.cube(h, (-6, 47.8, -3.5), (13, 2.8, 6), "col_shade", rot=[0, -14, 0], pivot=(0, 47.8, 0))   # broken lintel
    r.cube(h, (-6.2, 50.4, -3.6), (5, 0.6, 3), "cb_grass", rot=[0, -14, 0], pivot=(0, 47.8, 0))
    for x, l in ((-8.6, 3.5), (-5, 2), (3, 4.5), (7.6, 2.5)):                # moss draping from the abacus
        r.cube(h, (x, 45.6 - l, -8.7), (1.2, l, 0.4), "moss")
    r.cube(h, (8.15, 41.5, 2), (0.4, 4, 1.4), "moss")
    # stone arms with bronze rings
    for side, s in (("l", 1), ("r", -1)):
        a = r.bone(f"arm_{side}", "body", (s * 7.4, 33.5, 0), role=f"arm_{side}")
        r.cube(a, (s * 7.4 - 2.2, 31.5, -2.2), (4.4, 4.4, 4.4), "col_shade")       # shoulder block
        r.cube(a, (s * 7.4 - 1.7, 24, -1.7), (3.4, 8, 3.4), "col_marble")
        r.cube(a, (s * 7.4 - 2.1, 24.6, -2.1), (4.2, 1.2, 4.2), "bronze")
        f = r.bone(f"forearm_{side}", a, (s * 7.4, 24.5, 0))
        r.cube(f, (s * 7.4 - 1.6, 17.5, -1.6), (3.2, 7.6, 3.2), "col_marble")
        r.cube(f, (s * 7.4 - 2.2, 14.2, -2.4), (4.4, 3.8, 4.4), "col_shade")       # blocky fist
        r.cube(f, (s * 7.4 - 2.2, 15.2, -2.6), (4.4, 0.4, 0.3), "col_groove")
        if s > 0:
            r.cube(f, (s * 7.4 + 1.5, 18, -1), (0.4, 4, 1.2), "moss")
        else:
            r.cube(f, (s * 7.4 - 1.9, 19.5, -1.75), (0.3, 3, 0.4), "vein")
    # plinth legs: two halves of the base
    for side, s in (("l", 1), ("r", -1)):
        l = r.bone(f"leg_{side}", "body", (s * 3.6, 12, 0), role=f"leg_{side}")
        r.cube(l, (s * 3.6 - 2.8, 2, -3.6), (5.6, 10.6, 7.2), "col_marble")
        r.cube(l, (s * 3.6 - 3.6, 0, -4.6), (7.2, 2.4, 9.2), "col_shade")  # square plinth foot
        r.cube(l, (s * 3.6 - 3.0, 7, -3.75), (6.0, 1, 0.3), "col_groove")
        r.cube(l, (s * 3.6 - (0.4 if s > 0 else -0.0) - 0.4, 0, -5.3), (1.2, 1.2, 0.8), "stone")
    r.cube("leg_l", (5.9, 3, -1), (0.3, 4, 0.4), "vein")
    r.cube("leg_r", (-4.0, 2.4, -3.95), (2.6, 2.2, 0.3), "maw")           # chipped shin
    # rubble torn from the ground, circling it
    for i, (x, y, z, sz, m) in enumerate(((12, 18, 2, 3.4, "col_shade"), (-12, 26, -4, 2.6, "stone"), (3, 9, 12, 3.0, "cb_dirt"))):
        o = r.bone(f"rubble{i}", "body", (0, 20, 0), role="orbit")
        r.cube(o, (x, y, z), (sz, sz * 0.8, sz), m)
        r.cube(o, (x, y + sz * 0.8, z), (sz, 0.4, sz), "cb_grass" if m == "cb_dirt" else "moss")
    return r
