"""World 2, Giant Veins: a hot underground of lava veins, ore and old mines."""
from common import Rig, mat

# shared glows of the world
mat("w2_ember_eye", "ff4a12", "ff8a30", "glow", True)
mat("w2_lamp", "ffd860", "ffe890", "glow", True)
mat("w2_hot", "ff6a14", "ffb040", "magma", True)
mat("w2_crack", "ff7a1c", "ffb040", "glow", True)
mat("w2_core", "ffb020", "ffd050", "glow", True)
mat("w2_vein", "ff5a14", "ffa040", "vein", True)

# ash miner
mat("w2_soot", "2e2a28", "46403c", "skin")
mat("w2_soot_hi", "6a6058", "8a7e72", "skin")
mat("w2_shirt", "5a4632", "7a6044", "cloth")
mat("w2_pants", "2c3040", "485068", "cloth")
mat("w2_patch", "6a5a3a", "8a7a52", "cloth")
mat("w2_boot", "1e1814", "3a2e24", "cloth")
mat("w2_helmet", "9a7428", "d8b050", "metal")
mat("w2_wood", "6a4a2a", "8a6438", "bark")
mat("w2_pick", "6a6e78", "a8aeb8", "metal")
mat("w2_ore", "e86a1a", "ffa040", "glow", True)
mat("w2_basket", "5a3e22", "7a5a32", "bark")

# living vein
mat("w2_basalt", "2a2630", "48424e", "blocks")
mat("w2_basalt2", "3a302e", "584a46", "blocks")
mat("w2_gold", "d8a030", "f8e080", "crystal")
mat("w2_copper", "c8683a", "f0a878", "crystal")
mat("w2_crust", "4a1e14", "7a3420", "flesh")

# rock salamander
mat("w2_sal", "2a1a16", "4e2c20", "scales")
mat("w2_sal_ember", "2e1a14", "e85a1a", "spots")
mat("w2_sal_belly", "c8501e", "f09040", "scales")
mat("w2_sal_plate", "4e4646", "6e6666", "blocks")
mat("w2_sal_eye", "ffc820", "ffe060", "glow", True)
mat("w2_claw", "141018", "2a2230", "skin")
mat("w2_tongue", "e83a4a", "ff8090", "skin")

# dead smith
mat("w2_char", "241a16", "3e2c24", "skin")
mat("w2_char_hi", "4a362c", "644a3a", "skin")
mat("w2_apron", "5a3820", "7a5030", "cloth")
mat("w2_burn", "120c08", "1e1410", "skin")
mat("w2_beard", "4a4644", "6e6a66", "fur")
mat("w2_strap", "3a2414", "5a3a22", "cloth")
mat("w2_brass", "a07a30", "e0c060", "metal")
mat("w2_lens", "6a9aa8", "b0e0f0", "crystal")
mat("w2_iron", "4a4c54", "7a7e88", "metal")

# slag golem
mat("w2_slag", "26221f", "4a423c", "blocks")
mat("w2_slag2", "4a413b", "6a5e54", "blocks")
mat("w2_glass", "1c1622", "5a4a6a", "crystal")
mat("w2_molten", "ff6010", "ffa830", "magma", True)
mat("w2_steam", "a8a29c", "d8d4d0", "cloud")
mat("w2_rust", "6a3a22", "a8602e", "metal")


def _eye(r, bone, x, y, z, w, h, glow, pupil=None):
    """A glowing eye in a dark socket on a face whose front is at depth z; pupil 'dot', 'slit' or None."""
    r.cube(bone, (x - w / 2 - 0.3, y - h / 2 - 0.3, z - 0.2), (w + 0.6, h + 0.6, 0.4), "pupil")
    r.cube(bone, (x - w / 2, y - h / 2, z - 0.35), (w, h, 0.4), glow)
    if pupil == "slit":
        r.cube(bone, (x - 0.15, y - h / 2, z - 0.45), (0.3, h, 0.2), "pupil")
    elif pupil == "dot":
        r.cube(bone, (x - w * 0.15, y - h * 0.2, z - 0.45), (w * 0.35, h * 0.45, 0.2), "pupil")


def ash_miner():
    """A soot-black undead miner, hunched under a basket of glowing ore: a brass helmet with a carbide headlamp,
    ember eyes in a gaunt skull, suspenders over a torn shirt that shows the ribs, a lantern at the belt and a pick."""
    r = Rig("ash_miner")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 1.8, 8, 0), role=f"leg_{side}")
        r.cube(leg, (s * 1.8 - 1.3, 2, -1.3), (2.6, 6.5, 2.6), "w2_pants")
        r.cube(leg, (s * 1.8 - 1.5, 0, -2.2), (3, 2.4, 3.6), "w2_boot")
        r.cube(leg, (s * 1.8 - 1.4, 0, -2.5), (2.8, 1.2, 0.6), "w2_pick")     # steel toe cap
        r.cube(leg, (s * 1.8 - 1.6, 2.2, -1.6), (3.2, 0.7, 3.2), "w2_strap")  # boot top
    r.cube("leg_l", (1.1, 4.4, -1.45), (1.6, 1.8, 0.3), "w2_patch")             # a patched knee
    r.bone("body", None, (0, 8, 0), role="body")
    r.cube("body", (-3.6, 7.2, -2.2), (7.2, 1.8, 4.4), "w2_strap")              # belt
    r.cube("body", (-0.7, 7.4, -2.5), (1.4, 1.3, 0.4), "w2_brass")             # buckle
    r.cube("body", (-3.3, 8.8, -1.9), (6.6, 3.6, 3.8), "w2_shirt")
    r.cube("body", (-3.7, 12, -2.7), (7.4, 3.6, 4.6), "w2_shirt")              # hunched shoulders
    r.cube("body", (-1.9, 9.4, -2.05), (2.8, 2.6, 0.3), "w2_soot")              # torn shirt...
    for y in (9.8, 10.8):
        r.cube("body", (-1.6, y, -2.15), (2.2, 0.4, 0.3), "bone")             # ...showing the ribs
    for x in (-2.6, 1.8):
        r.cube("body", (x, 8.8, -2.3), (0.8, 6.8, 0.3), "w2_strap")             # suspenders
        r.cube("body", (x + 0.15, 8.9, -2.45), (0.5, 0.5, 0.2), "w2_brass")
    r.cube("body", (-3, 14.4, -3.2), (6, 1.2, 5.2), "cloth_red")                # sooty neckerchief
    r.cube("body", (-0.6, 13.2, -3.25), (1.6, 1.4, 0.4), "cloth_red")
    # basket of ore on the back
    r.cube("body", (-3, 9, 2.1), (6, 6, 3), "w2_basket")
    r.cube("body", (-3.2, 14.6, 1.9), (6.4, 0.6, 3.4), "w2_wood")
    r.cube("body", (-2.2, 14.8, 2.6), (1.8, 1.6, 1.8), "w2_ore")
    r.cube("body", (-0.2, 14.8, 2.4), (2, 1.3, 2), "w2_basalt2")
    r.cube("body", (1.3, 15, 3.1), (1.3, 1.4, 1.3), "w2_ore")
    for x in (-2.6, 1.8):
        r.cube("body", (x, 14.2, -2.9), (0.8, 0.6, 5), "w2_strap")             # shoulder straps
    # lantern hanging at the belt
    r.cube("body", (3.7, 7.4, -0.6), (0.4, 0.9, 0.4), "w2_iron")
    r.cube("body", (3.1, 6.8, -1.1), (1.6, 0.5, 1.6), "w2_iron")
    r.cube("body", (3.3, 5, -0.9), (1.2, 1.8, 1.2), "w2_lamp")
    r.cube("body", (3.1, 4.6, -1.1), (1.6, 0.5, 1.6), "w2_iron")
    # head
    r.bone("head", "body", (0, 15.4, -0.8), role="head")
    r.cube("head", (-2.8, 16.2, -3.6), (5.6, 3.6, 5), "w2_soot")
    r.cube("head", (-2.9, 16.4, -3.75), (1.1, 0.8, 0.3), "w2_soot_hi")           # cheekbones
    r.cube("head", (1.8, 16.4, -3.75), (1.1, 0.8, 0.3), "w2_soot_hi")
    _eye(r, "head", -1.2, 17.9, -3.6, 1.2, 0.9, "w2_ember_eye")
    _eye(r, "head", 1.2, 17.9, -3.6, 1, 0.8, "w2_ember_eye")
    r.cube("head", (-0.4, 16.9, -3.9), (0.8, 0.6, 0.3), "pupil")               # nose hole
    r.cube("head", (-1.6, 16.1, -3.95), (3.2, 0.5, 0.3), "pupil")              # mouth
    for x in (-1.4, -0.5, 0.8):
        r.cube("head", (x, 15.9, -4.0), (0.5, 0.6, 0.3), "tooth")
    r.cube("head", (-2.9, 17, 1.2), (5.8, 2.4, 0.5), "fur_grey")                 # stringy hair at the back
    r.cube("head", (-3.2, 19.4, -3.8), (6.4, 1.8, 5.6), "w2_helmet")             # helmet
    r.cube("head", (-3.6, 19.2, -4.5), (7.2, 0.6, 6.6), "w2_helmet")             # brim
    r.cube("head", (-0.5, 21.1, -3.2), (1, 0.5, 4.6), "w2_brass")               # ridge
    r.cube("head", (1.6, 20.2, -3.95), (0.8, 0.8, 0.3), "w2_soot")              # dent
    r.cube("head", (-1, 19.6, -5), (2, 1.8, 1), "w2_brass")                     # carbide lamp
    r.cube("head", (-0.7, 19.9, -5.2), (1.4, 1.2, 0.3), "w2_lamp")
    jaw = r.bone("jawbone", "head", (0, 16, -1.5))
    r.cube(jaw, (-2.4, 14.7, -3.8), (4.8, 1.5, 3.8), "w2_soot_hi")              # bony jaw
    for x in (-1.2, 0.2, 1.1):
        r.cube(jaw, (x, 16, -3.95), (0.5, 0.5, 0.3), "tooth")
    # arms
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 4.2, 14.6, -0.8), role=f"arm_{side}")
        x = s * 4.6
        r.cube(arm, (x - 1.2, 11.4, -2), (2.4, 4, 2.4), "w2_shirt")              # rolled sleeve
        r.cube(arm, (x - 1.3, 11.2, -2.1), (2.6, 0.8, 2.6), "w2_patch")
        r.cube(arm, (x - 0.9, 8.4, -1.7), (1.8, 3.4, 1.8), "w2_soot")             # bony forearm
        r.cube(arm, (x - 1.05, 9.2, -1.85), (2.1, 0.8, 2.1), "cloth_grey")       # wrist wrap
        r.cube(arm, (x - 1.2, 7.2, -2), (2.4, 1.6, 2.4), "w2_soot_hi")           # hand
    for dx in (-0.8, 0.5):                                                      # bony claws, free hand
        r.cube("arm_l", (4.6 + dx - 0.2, 6.4, -1.9), (0.5, 1, 0.5), "bone")
    # the pick
    r.cube("arm_r", (-5.2, 7.6, -10.2), (1.2, 1.2, 8.6), "w2_wood")
    r.cube("arm_r", (-5.3, 7.5, -3.6), (1.4, 1.4, 1.2), "w2_strap")             # grip wrap
    r.cube("arm_r", (-5.4, 6.8, -11.6), (1.6, 2.8, 1.6), "w2_pick")
    r.cube("arm_r", (-5.3, 9.6, -11.3), (1.4, 2.2, 1.2), "w2_pick")
    r.cube("arm_r", (-5.2, 11.6, -10.6), (1.2, 1, 1.1), "w2_pick")
    r.cube("arm_r", (-5.3, 4.6, -11.3), (1.4, 2.2, 1.2), "w2_pick")
    r.cube("arm_r", (-5.2, 3.8, -10.6), (1.2, 0.9, 1.1), "w2_pick")
    return r


def living_vein():
    """A walking pillar of basalt boulders held together by molten ore: magma oozes from every seam, raised veins
    branch up its front into a white-hot cleft, a fissure for a face, ore crystals erupting from its crown, and
    arms that are dripping strands of magma ending in shards."""
    r = Rig("living_vein")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 2.8, 7, 0), role=f"leg_{side}")
        r.cube(leg, (s * 2.8 - 2.6, 0, -3), (5.2, 7.5, 5.6), "w2_basalt2")
        r.cube(leg, (s * 2.8 - 2.2, 0, -3.8), (4.4, 2.2, 1.2), "w2_basalt")       # toe ledge
        r.cube(leg, (s * 2.8 - 2.8, 3.4, -3.2), (5.6, 0.6, 6), "w2_vein")        # molten ring at the knee
        r.cube(leg, (s * 2.8 - 1, 0.4, -4.05), (0.8, 3.2, 0.4), "w2_vein")
    r.bone("body", None, (0, 7, 0), role="body")
    for x, y, z, w, h, d, m, rot in ((-4.8, 6.5, -3.8, 9.6, 5.5, 7.6, "w2_basalt", 0),
                                     (-5.4, 12.6, -4.2, 10.2, 6, 8.2, "w2_basalt2", -5),
                                     (-4.4, 19.2, -4, 9.4, 5.2, 8, "w2_basalt", 8)):
        r.cube("body", (x, y, z), (w, h, d), m, rot=[0, rot, 0] if rot else None, pivot=(0, y, 0))
    for y, w, d in ((11.9, 9, 7), (18.5, 9, 7.4)):
        r.cube("body", (-w / 2, y, -d / 2), (w, 0.8, d), "w2_vein")              # magma oozing between the boulders
    r.cube("body", (-1.8, 14, -4.6), (3.2, 7, 0.6), "w2_crust")                  # cleft in the chest
    r.cube("body", (-1.3, 14.4, -4.9), (1.8, 2.4, 0.6), "w2_core")              # white-hot core, a jagged cleft
    r.cube("body", (-0.7, 16.6, -4.9), (2, 2.6, 0.6), "w2_core")
    r.cube("body", (-1.1, 19, -4.9), (1.4, 1.6, 0.6), "w2_core")
    # raised veins branching up the front and back into the core
    for x, y, w, h in ((-3.6, 7.4, 1, 4.6), (-3.6, 11.6, 2.6, 1), (2.4, 6.6, 1, 6), (1, 12.2, 2.4, 1),
                       (-4.4, 15, 1, 3.6), (-4.4, 15, 3, 0.9), (3.3, 13.4, 0.9, 5)):
        r.cube("body", (x, y, -4.55 if y > 12 else -4.15), (w, h, 1), "w2_vein")
    for x, y, w, h in ((-0.5, 7, 1, 12), (-3, 10, 2.5, 0.9), (0.5, 15, 3, 0.9), (2.6, 15, 0.9, 3.6)):
        r.cube("body", (x, y, 3.55 if y < 12 else 3.65), (w, h, 1), "w2_vein")
    r.cube("body", (4.75, 8, -1.4), (0.8, 4, 1), "w2_vein")                       # side branches
    r.cube("body", (-5.75, 13.4, 0.4), (0.8, 4.4, 1), "w2_vein")
    r.cube("body", (1.6, 5.6, -2.4), (0.6, 1.4, 0.6), "w2_vein")                  # drip at the hips
    r.cube("body", (-1.5, 17, 4), (2.2, 2.4, 1.4), "w2_copper")                  # ore shards on the back
    r.cube("body", (2.2, 9, 3.6), (1.4, 1.6, 1.2), "w2_gold")
    r.cube("body", (-6.4, 7.4, -1.6), (2.2, 3, 3.4), "w2_basalt2")               # loose boulders stuck to it
    r.cube("body", (4.4, 15.4, -3.4), (2, 2.6, 2.8), "w2_basalt")
    r.cube("body", (4.2, 15.2, -3.6), (0.6, 3, 0.6), "w2_vein")
    for x, y, z in ((-4.1, 11.2, -4.75), (1.9, 11.9, -4.75), (-0.9, 14.5, 3.95)):
        r.cube("body", (x, y, z), (1.6, 1.6, 0.7), "w2_core")                   # glowing knots where veins meet
    r.cube("body", (-7.4, 9.4, -1.4), (2, 3.8, 2), "w2_gold", rot=[0, 45, 0], pivot=(-6.4, 11, -0.4))   # ore bursting out
    r.cube("body", (-6.8, 12.6, 0.6), (1.4, 2.4, 1.4), "w2_copper", rot=[0, 20, 0], pivot=(-6.1, 13.5, 1.3))
    # the top of the column: a fissure for a face and an ore crown
    r.bone("head", "body", (0, 24, 0), role="head")
    r.cube("head", (-4, 24, -3.6), (8.2, 5, 7.2), "w2_basalt2", rot=[0, -8, 0], pivot=(0, 24, 0))
    r.cube("head", (-3.2, 28.6, -2.8), (6.4, 2.2, 5.8), "w2_basalt")
    r.cube("head", (-4.4, 27.6, -4.3), (8.6, 1.2, 1.6), "w2_basalt")             # brow ledge
    r.cube("head", (-3.4, 26.2, -3.95), (6.8, 0.6, 0.5), "w2_vein")              # the fissure
    _eye(r, "head", -1.7, 26.5, -3.6, 1.5, 1, "w2_core")
    _eye(r, "head", 1.7, 26.5, -3.6, 1.5, 1, "w2_core")
    r.cube("head", (-0.4, 24, -4.05), (0.8, 2.2, 0.5), "w2_vein")                 # glowing seam for a mouth
    r.cube("head", (-1.2, 24.2, -4.1), (2.4, 0.6, 0.5), "w2_vein")
    r.cube("head", (-1, 30.4, -1.2), (2, 3.2, 2), "w2_gold", rot=[0, 45, 0], pivot=(0, 31.5, -0.2))
    r.cube("head", (1.6, 30.4, 0.4), (1.4, 2.2, 1.4), "w2_copper", rot=[0, 20, 0], pivot=(2.3, 31, 1.1))
    r.cube("head", (-2.8, 30.4, 0.6), (1.2, 1.7, 1.2), "w2_gold")
    r.cube("head", (2.8, 28, -2.4), (1.2, 2.4, 1.2), "w2_gold", rot=[0, 30, 0], pivot=(3.4, 29, -1.8))
    # arms: dripping strands of magma
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 5.4, 22, 0), role=f"arm_{side}")
        x = s * 6.6
        big = 4.6 if s < 0 else 4
        r.cube(arm, (x - big / 2, 19.6 if s > 0 else 20.4, -big / 2), (big, big, big), "w2_basalt")    # shoulder boulder
        r.cube(arm, (x - 0.8, 10, -0.8), (1.6, 10, 1.6), "w2_vein")                 # molten strand
        r.cube(arm, (x - 1.3, 16, -1.3), (2.6, 1.6, 2.6), "w2_basalt2")            # rock beads on it
        r.cube(arm, (x - 1.1, 12.4, -1.1), (2.2, 1.4, 2.2), "w2_basalt")
        r.cube(arm, (x - 1.1, 7, -1.1), (2.2, 3.4, 2.2), "w2_gold" if s > 0 else "w2_copper")   # shard tip
        r.cube(arm, (x - 0.6, 5.4, -0.6), (1.2, 1.8, 1.2), "w2_gold" if s > 0 else "w2_copper")
        r.cube(arm, (x + s * 0.6 - 0.3, 17.6, -0.3), (0.6, 1.4, 0.6), "w2_vein")  # drip
    r.cube("arm_l", (7.4, 11, 0.6), (0.6, 8, 0.6), "w2_vein")                     # left arm splits in two strands
    return r


def rock_salamander():
    """A lava lizard: charred scales under rocky back plates with embers glowing between them, a crest of spikes,
    slit-pupilled gold eyes, a flickering tongue, splayed clawed legs and a tail that ends in a live ember."""
    r = Rig("rock_salamander")
    r.bone("body", None, (0, 4, 0), role="body")
    r.cube("body", (-3, 2, -5.4), (6, 3.6, 11.4), "w2_sal_ember")
    r.cube("body", (-2.6, 1.6, -5), (5.2, 0.6, 10.6), "w2_sal_belly")           # belly
    for i, z in enumerate((-4.8, -2, 0.8, 3.6)):                               # rocky back plates
        w = 5.4 - (i % 2) * 0.6
        r.cube("body", (-w / 2, 5.4, z), (w, 1.1, 2.5), "w2_sal_plate")
        r.cube("body", (-2.1, 5.3, z + 2.45), (4.2, 0.8, 0.35), "w2_hot")       # embers between them
        r.cube("body", (-0.5, 6.4, z + 0.6), (1, 1.4 + (i % 2) * 0.6, 1.1), "w2_sal_plate")   # crest spike
    for x, y, z in ((3.05, 3.4, -3), (3.05, 2.6, 1.4), (-3.35, 3.2, -1), (-3.35, 2.8, 3.2)):
        r.cube("body", (x, y, z), (0.3, 0.8, 1.4), "w2_hot")                    # ember scales on the flanks
    # head: the lower jaw carries the head role, the upper skull gapes open as the jaw
    r.bone("head", "body", (0, 3.4, -5.2), role="head")
    r.cube("head", (-2.4, 1.2, -12.2), (4.8, 1.4, 6.6), "w2_sal_belly")
    r.cube("head", (-2.5, 1.4, -7), (5, 2.2, 2.4), "w2_sal")
    r.cube("head", (-1.7, 2.5, -12), (3.4, 0.3, 3.4), "maw")
    for x in (-1.6, 1.2):
        r.cube("head", (x, 2.5, -12.1), (0.4, 0.6, 0.4), "tooth")
    r.cube("head", (-0.3, 2.3, -14.2), (0.6, 0.35, 2.6), "w2_tongue")          # tongue flicking out
    r.cube("head", (-0.7, 2.3, -14.8), (0.5, 0.35, 0.8), "w2_tongue")
    r.cube("head", (0.2, 2.3, -14.8), (0.5, 0.35, 0.8), "w2_tongue")
    jaw = r.bone("jaw", "head", (0, 3, -6.5), role="jaw")
    r.cube(jaw, (-2.5, 2.7, -10), (5, 2.9, 5.2), "w2_sal")
    r.cube(jaw, (-2, 2.7, -12.4), (4, 1.9, 2.6), "w2_sal")                      # snout
    for s_ in (1, -1):
        r.cube(jaw, (s_ * 1.8 - 0.9, 5.2, -9.8), (1.8, 0.8, 3.4), "w2_sal_plate")   # brow plates
        r.cube(jaw, (s_ * 2.3 - 0.75, 4.4, -9.6), (1.5, 1.2, 1.4), "w2_sal_eye")    # bulging eyes
        r.cube(jaw, (s_ * 2.3 - 0.15, 4.4, -9.75), (0.3, 1.2, 0.2), "pupil")        # slit pupils
        r.cube(jaw, (s_ * 1 - 0.3, 3.9, -12.55), (0.6, 0.4, 0.2), "w2_hot")          # smouldering nostrils
        r.cube(jaw, (s_ * 2.6 - 0.2, 3.8, -6.8), (0.4, 1, 1.6), "w2_sal_plate")      # cheek frills
    for x in (-1.5, -0.4, 0.8):
        r.cube(jaw, (x, 2.2, -12.2), (0.4, 0.6, 0.4), "tooth")
    # splayed legs; front legs carry the arm roles so the walk is a diagonal trot
    for (nm, role, s, z) in (("leg_fl", "arm_l", 1, -3), ("leg_fr", "arm_r", -1, -3),
                             ("leg_bl", "leg_l", 1, 3.4), ("leg_br", "leg_r", -1, 3.4)):
        leg = r.bone(nm, "body" if role.startswith("arm") else None, (s * 2.8, 3.6, z), role=role)
        x0 = 2.6 if s > 0 else -5.4
        r.cube(leg, (x0, 2.6, z - 0.9), (2.8, 1.7, 1.8), "w2_sal")
        x1 = 4.4 if s > 0 else -6
        r.cube(leg, (x1, 0.5, z - 0.8), (1.6, 3, 1.6), "w2_sal")
        r.cube(leg, (x1 - 0.3, 0, z - 1.6), (2.2, 0.6, 2.4), "w2_sal")
        for dx in (0, 1.4):
            r.cube(leg, (x1 - 0.1 + dx, 0, z - 2.2), (0.4, 0.5, 0.7), "w2_claw")
        r.cube(leg, (x0 + 0.6, 4.2, z - 0.5), (1.4, 0.4, 1), "w2_sal_plate")
    # tail
    t0 = r.bone("tail0", "body", (0, 3.8, 5.6), role="tail")
    r.cube(t0, (-2.2, 2.2, 5.4), (4.4, 2.8, 4.6), "w2_sal_ember")
    r.cube(t0, (-1.8, 5, 5.8), (3.6, 0.8, 3.4), "w2_sal_plate")
    r.cube(t0, (-0.4, 5.6, 6.6), (0.8, 1, 0.9), "w2_sal_plate")
    t1 = r.bone("tail1", t0, (0, 3.5, 9.6), role="tail")
    r.cube(t1, (-1.6, 2, 9.4), (3.2, 2.2, 4.6), "w2_sal_ember")
    r.cube(t1, (-1.2, 4.2, 9.8), (2.4, 0.6, 3.4), "w2_sal_plate")
    r.cube(t1, (-1.3, 4.0, 9.2), (2.6, 0.5, 0.4), "w2_hot")
    t2 = r.bone("tail2", t1, (0, 3, 13.6), role="tail")
    r.cube(t2, (-1, 1.8, 13.4), (2, 1.6, 4.4), "w2_sal")
    r.cube(t2, (-1.1, 3.3, 13.2), (2.2, 0.4, 0.4), "w2_hot")
    r.cube(t2, (-0.7, 1.8, 17.6), (1.4, 1.4, 1.8), "w2_hot")                  # the ember at the tip
    r.cube(t2, (-0.4, 3.1, 17.9), (0.8, 0.8, 1), "w2_core")
    return r


def dead_smith():
    """A charred smith that still works the forge: glowing cracks across a burnt body, a leather apron scorched with
    holes, a smouldering ash beard, goggles pushed up on the brow, a sledge hammer with a red-hot face in one hand
    and tongs gripping a glowing ingot in the other."""
    r = Rig("dead_smith")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 2.6, 12, 0), role=f"leg_{side}")
        r.cube(leg, (s * 2.6 - 2.1, 2.4, -2.1), (4.2, 10.2, 4.2), "w2_pants")
        r.cube(leg, (s * 2.6 - 2.4, 0, -3), (4.8, 3, 5.4), "w2_boot")
        r.cube(leg, (s * 2.6 - 2.6, 2.6, -2.6), (5.2, 1, 5.2), "w2_strap")
        r.cube(leg, (s * 2.6 - 2.3, 0.3, -3.3), (4.6, 1.2, 0.5), "w2_iron")     # iron-shod toes
    r.bone("body", None, (0, 12, 0), role="body")
    r.cube("body", (-5, 11.4, -3.2), (10, 1.8, 6.4), "w2_strap")                 # belt
    r.cube("body", (-1, 11.6, -3.5), (2, 1.4, 0.4), "w2_brass")
    r.cube("body", (-5.5, 13, -3.4), (11, 8, 6.8), "w2_char")                    # barrel chest
    r.cube("body", (-6, 20.6, -3.2), (12, 4.6, 6.4), "w2_char")                  # shoulders
    r.cube("body", (-4.5, 18.8, 2.4), (9, 5.6, 1.6), "w2_char_hi")               # hunched back
    for x, y, z, w, h, d in ((-4.4, 21.6, -3.45, 0.5, 3, 0.3), (3.6, 22, -3.45, 0.4, 2.6, 0.3),
                             (-2, 19, 4.05, 0.5, 5, 0.3), (-2, 21.6, 4.05, 3.6, 0.5, 0.3),
                             (1.2, 15, 3.45, 0.5, 4, 0.3), (5.55, 15, -1, 0.3, 4.6, 0.5)):
        r.cube("body", (x, y, z), (w, h, d), "w2_crack")                          # glowing cracks
    # apron
    r.cube("body", (-4.6, 5.6, -3.9), (9.2, 15.6, 0.6), "w2_apron")
    for x, w, h in ((-4.6, 2.4, 1.2), (-1.6, 1.6, 0.8), (0.6, 2.2, 1.4), (3.2, 1.4, 0.7)):
        r.cube("body", (x, 4.6 + (1.4 - h), -3.9), (w, h, 0.6), "w2_apron")     # ragged hem
    for x in (-4.4, 3.4):
        r.cube("body", (x, 21, -3.6), (1, 4.2, 0.5), "w2_strap")                 # bib straps
        r.cube("body", (x + 0.2, 20.2, -4.05), (0.6, 0.6, 0.3), "w2_brass")      # rivets
    r.cube("body", (-3, 9, -4.05), (1.6, 1.2, 0.3), "w2_burn")                   # burn holes
    r.cube("body", (-2.8, 9.2, -4.15), (1.2, 0.3, 0.2), "w2_crack")
    r.cube("body", (2, 7, -4.05), (1.2, 0.9, 0.3), "w2_burn")
    r.cube("body", (1, 13.6, -4.3), (2.8, 2.4, 0.5), "w2_strap")                 # pocket
    r.cube("body", (1.5, 15.6, -4.3), (0.6, 1.8, 0.5), "w2_wood")                # chisel in the pocket
    r.cube("body", (2.6, 15.8, -4.3), (0.5, 1.2, 0.5), "w2_iron")
    # head
    r.bone("head", "body", (0, 25, -0.6), role="head")
    r.cube("head", (-3.4, 24.6, -4), (6.8, 6, 6.4), "w2_char")
    r.cube("head", (-3.7, 28.3, -4.4), (7.4, 1, 1.2), "w2_char_hi")             # brow
    _eye(r, "head", -1.5, 27.4, -4, 1.4, 0.8, "w2_ember_eye")
    _eye(r, "head", 1.5, 27.4, -4, 1.4, 0.8, "w2_ember_eye")
    r.cube("head", (-0.5, 26, -4.5), (1, 1.4, 0.6), "w2_char_hi")               # broken nose
    r.cube("head", (-3.6, 29.4, -4.2), (7.2, 0.8, 6.8), "w2_strap")             # goggle strap
    for x in (-2.7, 0.5):
        r.cube("head", (x, 29.1, -4.7), (2.2, 1.6, 0.7), "w2_brass")             # goggles pushed up
        r.cube("head", (x + 0.4, 29.4, -4.85), (1.4, 1, 0.3), "w2_lens")
    r.cube("head", (0.4, 30.6, -3), (0.4, 0.3, 4), "w2_crack")                   # crack across the scalp
    r.cube("head", (-3.1, 22.4, -4.6), (6.2, 3.8, 1.6), "w2_beard")             # ash beard
    r.cube("head", (-2.2, 21.2, -4.4), (4.4, 1.4, 1.2), "w2_beard")
    r.cube("head", (-0.9, 20.2, -4.2), (1.8, 1.2, 0.9), "w2_beard")
    r.cube("head", (-1.8, 24.2, -4.75), (3.6, 0.5, 0.3), "w2_burn")             # mouth in the beard
    r.cube("head", (1.6, 22.6, -4.75), (0.6, 0.6, 0.3), "w2_hot")               # embers smouldering in it
    r.cube("head", (-2.4, 21.6, -4.55), (0.5, 0.5, 0.3), "w2_hot")
    # arms
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 6.6, 23, -0.4), role=f"arm_{side}")
        x = s * 7.8
        r.cube(arm, (x - 1.6, 15.6, -1.8), (3.2, 7.6, 3.2), "w2_char")
        r.cube(arm, (x - 1.7, 11, -2), (3.4, 5.2, 3.4), "w2_char")
        r.cube(arm, (x - 1.9, 12.2, -2.2), (3.8, 2.8, 3.8), "w2_strap")          # bracer
        r.cube(arm, (x - 1.75, 9.4, -2.2), (3.5, 2, 3.4), "w2_char_hi")          # fist
        r.cube(arm, (x + s * 1.65 - 0.15, 17, -0.6), (0.3, 4, 0.5), "w2_crack")
    r.cube("arm_r", (-10, 20.6, -2.6), (4.4, 3.6, 4.6), "w2_iron")                # shoulder guard
    r.cube("arm_r", (-10.2, 21.4, -2.8), (4.8, 0.6, 5), "w2_brass")
    # the sledge hammer, red-hot
    r.cube("arm_r", (-8.5, 9.8, -12), (1.4, 1.4, 10.2), "w2_wood")
    r.cube("arm_r", (-10, 7.6, -15), (4.4, 5.8, 3.4), "w2_iron")
    r.cube("arm_r", (-10.1, 7.2, -15.1), (4.6, 1.8, 3.6), "w2_hot")              # glowing striking face
    r.cube("arm_r", (-10.1, 11.6, -15.1), (4.6, 0.6, 3.6), "w2_brass")
    # tongs and the ingot
    for dx in (-0.8, 0.4):
        r.cube("arm_l", (7.8 + dx, 10.2, -11.6), (0.5, 0.5, 9.4), "w2_iron")
    r.cube("arm_l", (7.3, 10, -5.2), (1.6, 0.9, 0.9), "w2_brass")                # hinge rivet
    r.cube("arm_l", (6.6, 9.6, -14), (2.6, 1.3, 2.8), "w2_hot")                  # glowing ingot
    return r


def slag_golem():
    """A hulking golem of cooling slag: dark glassy crust plates over a body still molten inside, so every seam
    glows; a molten heart in its belly, the head thrust low between huge shoulders, fists dripping slag,
    rebar and scrap stuck in it, and vents on its back that steam as it hardens."""
    r = Rig("slag_golem")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 3.8, 9, 1), role=f"leg_{side}")
        r.cube(leg, (s * 3.8 - 2.7, 2.6, -1.8), (5.4, 7, 5.6), "w2_slag")
        r.cube(leg, (s * 3.8 - 2.9, 5, -2), (5.8, 0.8, 6), "w2_molten")          # glowing ring
        r.cube(leg, (s * 3.8 - 3.2, 0, -3.4), (6.4, 3, 7.2), "w2_slag2")
        r.cube(leg, (s * 3.8 - 3, 0.6, -3.7), (6, 0.6, 0.4), "w2_crack")
    r.bone("body", None, (0, 10, 1), role="body")
    r.cube("body", (-5.4, 8.5, -3.6), (10.8, 6.2, 8.4), "w2_slag")             # belly
    r.cube("body", (-2.4, 9.6, -4.2), (4.8, 4.2, 0.8), "w2_glass")
    r.cube("body", (-1.8, 10.2, -4.5), (3.6, 3, 0.6), "w2_molten")              # the molten heart
    r.cube("body", (-0.8, 10.9, -4.7), (1.6, 1.6, 0.3), "w2_core")
    r.cube("body", (-6.2, 14, -4.8), (12.4, 8.8, 10.4), "w2_molten")            # chest, molten inside...
    for x, y, z, w, h, d in ((-6.8, 18.7, -5.4, 6.3, 4.3, 1.2), (1, 17.9, -5.4, 5.8, 5.1, 1.2),
                             (-6.8, 13.8, -5.4, 4.1, 3.8, 1.2), (-1.3, 13.8, -5.4, 8.1, 3, 1.2),
                             (5.7, 13.8, -4.6, 1.2, 9, 5.8), (5.7, 15.2, 1.8, 1.2, 7.6, 3.6),
                             (-6.9, 13.8, -4.6, 1.2, 5.6, 9.6), (-6.9, 20, -4.6, 1.2, 2.8, 4.4), (-6.9, 20, 0.4, 1.2, 2.8, 5),
                             (-6.8, 13.8, 5.0, 7.4, 9.2, 1.2), (1.2, 14.6, 5.0, 5.6, 8.4, 1.2)):
        r.cube("body", (x, y, z), (w, h, d), "w2_slag")                          # ...under crust plates
    r.cube("body", (-7.4, 22.2, -3.4), (14.8, 5, 9.4), "w2_slag2")             # hunched upper back
    r.cube("body", (-6, 27, -1), (12, 1.6, 6), "w2_slag")
    r.cube("body", (-6.8, 19, -5.9), (3.6, 2.6, 0.8), "w2_glass")               # glassy flakes
    r.cube("body", (2.4, 14.4, -5.9), (3, 2, 0.8), "w2_glass")
    # vents on the back, still steaming
    r.cube("body", (-4.4, 27.6, 2.4), (2.4, 2.6, 2.4), "w2_glass")
    r.cube("body", (-4, 30, 2.8), (1.6, 0.4, 1.6), "w2_molten")
    r.cube("body", (-4.8, 30.6, 2), (3.2, 1.6, 3.2), "w2_steam")
    r.cube("body", (-4.2, 32, 2.6), (2, 1, 2), "w2_steam")
    r.cube("body", (2.6, 27.6, 3.2), (1.8, 2, 1.8), "w2_glass")
    r.cube("body", (2.4, 29.8, 3), (2.2, 1.2, 2.2), "w2_steam")
    r.cube("body", (4.6, 26, -2), (0.8, 5.4, 0.8), "w2_rust")                   # rebar stuck in the shoulder
    r.cube("body", (3.6, 30.6, -2), (1.8, 0.8, 0.8), "w2_rust")
    # head thrust low between the shoulders
    r.bone("head", "body", (0, 20, -4.5), role="head")
    r.cube("head", (-3.6, 17.6, -10), (7.2, 5.4, 5.6), "w2_slag2")
    r.cube("head", (-4.2, 21.8, -10.8), (8.4, 1.6, 2.8), "w2_glass")            # heavy brow
    _eye(r, "head", -1.7, 20.6, -10, 1.6, 1, "w2_core")
    _eye(r, "head", 1.7, 20.6, -10, 1.6, 1, "w2_core")
    r.cube("head", (-2.6, 18.4, -10.2), (5.2, 0.8, 0.4), "w2_molten")           # molten mouth
    jaw = r.bone("chin", "head", (0, 18.4, -6))
    r.cube(jaw, (-3.2, 16.4, -10.4), (6.4, 2.2, 4.8), "w2_slag")
    r.cube(jaw, (-0.5, 15, -10), (1, 1.6, 1), "w2_molten")                       # slag drooling off the chin
    r.cube(jaw, (1.6, 15.6, -10.2), (0.6, 1, 0.6), "w2_molten")
    # arms: fists almost to the ground
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 9.4, 24, 0), role=f"arm_{side}")
        x = s * 10.6
        r.cube(arm, (x - 3.8, 20.4, -3.8), (7.6, 7, 7.6), "w2_slag")             # shoulder boulder
        r.cube(arm, (x - 4, 22.6, -4), (8, 0.8, 8), "w2_molten")                 # glowing seam
        r.cube(arm, (x - 2.6, 12, -2.6), (5.2, 9, 5.2), "w2_slag2")
        r.cube(arm, (x - 2.8, 14.6, -2.8), (5.6, 0.7, 5.6), "w2_molten")
        r.cube(arm, (x - 3, 6, -3.6), (6, 7, 6.4), "w2_slag")                    # forearm
        r.cube(arm, (x - 3.3, 9.6, -3.9), (6.6, 0.8, 7), "w2_molten")            # crack ring
        r.cube(arm, (x - 3.8, 0.6, -5.2), (7.6, 5.8, 8), "w2_slag2")             # huge fist
        r.cube(arm, (x - 3.6, 5.9, -5), (7.2, 0.6, 7.6), "w2_molten")            # wrist seam
        r.cube(arm, (x - 3.9, 1, -5.5), (7.8, 1, 0.4), "w2_crack")               # knuckle seam
        r.cube(arm, (x - 3.9, 3.4, -5.5), (2.2, 0.5, 0.4), "w2_crack")
        r.cube(arm, (x - 0.4, 0, -1), (0.8, 0.8, 0.8), "w2_molten")              # drip
        r.cube(arm, (x - 3.7, 7.5, -2.5), (0.9, 3, 5), "w2_glass")               # crust flake
        r.cube(arm, (x - 1, 26.6, -1.6), (2, 3.4, 2), "w2_glass", rot=[0, 45, 0], pivot=(x, 28, -0.6))   # slag spikes
        r.cube(arm, (x + s * 1.8 - 0.7, 26.6, 1), (1.4, 2.2, 1.4), "w2_glass", rot=[0, 30, 0], pivot=(x + s * 1.8, 27.5, 1.7))
    r.cube("arm_l", (11.6, 2.2, -5.6), (2.8, 3, 0.6), "w2_molten")               # a patch still molten
    r.cube("arm_r", (-12.8, 2.6, -5.9), (2.6, 2.6, 1.2), "w2_rust")               # scrap iron in the fist
    return r
