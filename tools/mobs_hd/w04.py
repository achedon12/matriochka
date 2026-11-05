"""World 4, Storm Archipelago: floating islands, wind and lightning."""
from common import Rig, mat

# ---------------------------------------------------------------- palette
mat("ray_back", "3a5a92", "5a7ab0", "cloud")
mat("ray_belly", "d8e4f0", "ffffff", "cloud")
mat("ray_edge", "8ab0d8", "c8e0f8", "cloud")
mat("wind_line", "9ae8ff", "c8f4ff", "glow", True)
mat("ray_eye", "6ae0ff", "a8f0ff", "glow", True)
mat("ray_mouth", "142034", "1e2e48", "skin")

mat("tb_feather", "23304f", "34466e", "fur")
mat("tb_dark", "141a2c", "2a3450", "fur")
mat("tb_chest", "c8d0e0", "ffffff", "fur")
mat("tb_beak", "d89a2a", "f0c060", "skin")
mat("tb_talon", "2a2a30", "4a4a54", "skin")
mat("bolt", "ffe14a", "fff08a", "glow", True)
mat("tb_eye", "ffe040", "fff090", "glow", True)

mat("ward_stone", "5f6670", "8a929c", "blocks")
mat("ward_dark", "3e434c", "5a606a", "blocks")
mat("grass_top", "4f9a35", "8ad050", "leaf")
mat("island_dirt", "6a4a2e", "8a6a44", "blocks")
mat("sky_crystal", "5ad8ff", "c8f8ff", "crystal", True)
mat("ward_eye", "7af0ff", "c8faff", "glow", True)
mat("waterfall", "5ab8f0", "a8e0ff", "glow", True)
mat("root", "5a3a22", "7a5232", "bark")
mat("leaf_sky", "4aa040", "8ad060", "leaf")

mat("thundercloud", "8a94a8", "c8d0dc", "cloud")
mat("cloud_belly", "4a5266", "6a7488", "cloud")
mat("mine_iron", "3a3e48", "6a707c", "metal")
mat("mine_crack", "ffe14a", "fff6b0", "vein", True)
mat("mine_eye", "ff6a2a", "ffa060", "glow", True)

mat("coat_storm", "2f4058", "4f6a8a", "cloth")
mat("harp_skin", "c08a62", "d8a47a", "skin")
mat("beard", "8a5a30", "a8743c", "fur")
mat("cap_leather", "5a3a22", "7a5232", "cloth")
mat("goggle", "7ae0ff", "b8f0ff", "glow", True)
mat("rope", "b0905a", "d0b07a", "bark")
mat("harp_steel", "8a96a4", "d0d8e0", "metal")
mat("trouser", "4a3a2e", "6a5444", "cloth")
mat("shirt", "d8d0c0", "f0e8d8", "cloth")


# ---------------------------------------------------------------- creatures
def wind_ray():
    """A manta made of storm and cloud: a dark blue back streaked with glowing wind lines, a white cloud
    belly with gill slits, curling cephalic horns, cyan eyes, wingtips fraying into cloud puffs and a long
    whip tail ending in a lightning barb."""
    r = Rig("wind_ray")
    Y = 8
    body = r.bone("body", None, (0, Y, 0), role="body")
    r.cube(body, (-3.5, Y - 1.5, -5), (7, 3, 10), "ray_back")
    r.cube(body, (-3.0, Y - 2.1, -4.5), (6, 0.6, 9), "ray_belly")
    r.cube(body, (-1.2, Y + 1.5, -3.5), (2.4, 0.8, 7), "ray_back")              # dorsal ridge
    r.cube(body, (-0.3, Y + 2.3, -2.0), (0.6, 0.3, 4.5), "wind_line")
    for s in (1, -1):
        for i in range(2):                                                       # gill slits under the belly
            r.cube(body, (s * 1.6 - 0.6, Y - 2.25, -2.6 + i * 1.2), (1.2, 0.2, 0.3), "ray_mouth")
        r.cube(body, (s * 1.8 - 0.6, Y - 1.4, 4.4), (1.2, 0.8, 2.2), "ray_edge")  # pelvic fins
    head = r.bone("head", body, (0, Y, -5), role="head")
    r.cube(head, (-3.0, Y - 1.4, -8), (6, 2.6, 3.4), "ray_back")
    r.cube(head, (-2.6, Y - 1.9, -7.8), (5.2, 0.6, 3.0), "ray_belly")
    r.cube(head, (-2.4, Y - 1.5, -8.2), (4.8, 0.8, 0.4), "ray_mouth")           # wide filter mouth
    r.cube(head, (-2.0, Y - 1.3, -8.3), (4.0, 0.3, 0.3), "ray_edge")
    for s in (1, -1):
        r.cube(head, (s * 3.0 - 0.3, Y - 0.2, -7.0), (0.6, 1.0, 1.4), "ray_eye")   # eyes on the flanks of the head
        r.cube(head, (s * 3.0 - 0.35, Y + 0.0, -6.6), (0.7, 0.5, 0.5), "pupil")
        r.cube(head, (s * 3.2 - 0.6, Y - 0.6, -10.6), (1.2, 1.4, 2.8), "ray_back")  # cephalic horns, forward
        r.cube(head, (s * 2.7 - 0.6, Y - 0.2, -11.8), (1.2, 1.2, 1.4), "ray_edge")  # curling inward
        r.cube(head, (s * 3.2 - 0.25, Y + 0.8, -10.2), (0.5, 0.15, 2.2), "wind_line")
    for side, s in (("l", 1), ("r", -1)):
        w = r.bone(f"wing_{side}", body, (s * 3.4, Y, -0.5), role=f"wing_{side}")

        def X(x0, ww):
            return x0 if s > 0 else -x0 - ww
        # swept triangle: each panel narrower, thinner and further back than the last
        for x0, ww, z0, d, h in ((3.0, 3.6, -4.6, 9.4, 1.8), (6.6, 2.6, -3.2, 7.4, 1.4),
                                 (9.2, 2.0, -1.6, 5.4, 1.0), (11.2, 1.6, 0.2, 3.4, 0.7)):
            r.cube(w, (X(x0, ww), Y - h / 2, z0), (ww, h, d), "ray_back")
            r.cube(w, (X(x0, ww) + 0.1, Y - h / 2 - 0.3, z0 + 0.3), (ww - 0.2, 0.3, d - 0.6), "ray_belly")
            r.cube(w, (X(x0, ww), Y - h / 2 + 0.1, z0 - 0.5), (ww, h - 0.2, 0.5), "ray_edge")   # pale leading edge
        r.cube(w, (X(12.8, 1.4), Y - 0.3, 2.0), (1.4, 0.6, 2.2), "ray_edge")          # swept tip
        for x0, z0, sz in ((4.0, 4.6, 1.8), (7.2, 4.0, 1.6), (10.0, 3.6, 1.4), (13.0, 4.0, 1.2)):  # trailing edge frays into cloud
            r.cube(w, (X(x0, sz), Y - 0.7, z0), (sz, 1.2, sz), "cloud")
        r.cube(w, (X(4.0, 6.0), Y + 0.95, -1.6), (6.0, 0.2, 0.5), "wind_line")        # wind streaks
        r.cube(w, (X(7.0, 4.2), Y + 0.72, 0.8), (4.2, 0.2, 0.4), "wind_line")
    prev, z = body, 5.0
    for i, (wd, ln) in enumerate(((1.2, 3.0), (0.8, 2.6), (0.5, 2.4))):
        t = r.bone(f"tail{i}", prev, (0, Y, z), role="tail")
        r.cube(t, (-wd / 2, Y - wd / 2, z - 0.2), (wd, wd, ln + 0.4), "ray_back" if i < 2 else "ray_edge")
        prev, z = t, z + ln
    r.cube(prev, (-0.7, Y - 0.25, z - 0.4), (1.4, 0.5, 1.2), "bolt")             # lightning barb
    r.cube(prev, (-0.25, Y - 0.25, z + 0.6), (0.5, 0.5, 1.0), "bolt")
    for i, (x, y, z) in enumerate(((7, Y + 3, -4), (-6, Y - 2.5, 4))):           # gust wisps riding with it
        o = r.bone(f"gust{i}", body, (0, Y, 0), role="orbit")
        r.cube(o, (x - 1.2, y - 0.2, z - 0.2), (2.4, 0.3, 0.4), "wind_line")
    return r


def storm_bird():
    """A thunderbird: midnight-blue plumage with a pale chest marked by a lightning zigzag, a hooked gold
    beak, burning yellow eyes under a heavy brow, a crackling crest, wings striped with lightning and
    tipped with sparks, a fanned tail, black talons and static motes circling it."""
    r = Rig("storm_bird")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 1.3, 6, 0.5), role=f"leg_{side}")
        r.cube(leg, (s * 1.3 - 0.9, 3.4, -0.5), (1.8, 2.8, 2.0), "tb_feather")    # feathered thigh
        r.cube(leg, (s * 1.3 - 0.4, 0.6, 0.1), (0.8, 3.2, 0.8), "tb_beak")
        r.cube(leg, (s * 1.3 - 0.9, 0, -1.6), (0.5, 0.6, 2.0), "tb_beak")          # toes
        r.cube(leg, (s * 1.3 + 0.4, 0, -1.6), (0.5, 0.6, 2.0), "tb_beak")
        r.cube(leg, (s * 1.3 - 0.9, 0, -2.0), (0.5, 0.6, 0.5), "tb_talon")         # talons
        r.cube(leg, (s * 1.3 + 0.4, 0, -2.0), (0.5, 0.6, 0.5), "tb_talon")
        r.cube(leg, (s * 1.3 - 0.25, 0, 0.8), (0.5, 0.6, 1.2), "tb_beak")          # back toe
    body = r.bone("body", None, (0, 8, 0), role="body")
    r.cube(body, (-2.6, 5.6, -3.2), (5.2, 4.6, 7.4), "tb_feather")
    r.cube(body, (-2.1, 5.2, -3.8), (4.2, 4.4, 2.2), "tb_chest")
    r.cube(body, (-0.9, 8.0, -4.0), (1.2, 0.6, 0.3), "bolt")                     # zigzag on the chest
    r.cube(body, (-0.3, 7.2, -4.0), (1.2, 0.8, 0.3), "bolt")
    r.cube(body, (-0.8, 6.2, -4.0), (1.0, 1.0, 0.3), "bolt")
    r.cube(body, (-2.2, 9.6, -2.4), (4.4, 1.2, 5.4), "tb_dark")                  # mantle feathers
    head = r.bone("head", body, (0, 10, -2.6), role="head")
    r.cube(head, (-2.0, 9.4, -6.4), (4.0, 3.6, 4.2), "tb_feather")
    r.cube(head, (-2.3, 11.8, -6.7), (4.6, 0.9, 2.2), "tb_dark")                 # scowling brow
    for s in (1, -1):
        r.cube(head, (s * 1.3 - 0.6, 10.7, -6.6), (1.2, 1.0, 0.3), "tb_eye")
        r.cube(head, (s * 1.3 - 0.2 - s * 0.15, 10.8, -6.7), (0.4, 0.8, 0.2), "pupil")
    r.cube(head, (-0.8, 9.6, -8.6), (1.6, 1.8, 2.3), "tb_beak")                  # hooked beak
    r.cube(head, (-0.5, 8.8, -8.9), (1.0, 1.4, 0.7), "tb_beak")
    r.cube(head, (-0.55, 10.8, -8.0), (0.3, 0.3, 0.3), "tb_talon")               # nostril
    jaw = r.bone("jaw", head, (0, 9.8, -6.4), role="jaw")
    r.cube(jaw, (-0.7, 9.0, -8.2), (1.4, 0.7, 1.9), "tb_beak")
    for i, (x, h, ang) in enumerate(((-1.1, 2.4, 30), (0, 3.2, 22), (1.1, 2.4, 30))):   # crackling crest
        r.cube(head, (x - 0.35, 12.6, -4.6), (0.7, h, 0.9), "tb_dark", rot=(ang, 0, 0), pivot=(x, 12.6, -4.2))
        r.cube(head, (x - 0.3, 12.6 + h, -4.6), (0.6, 0.8, 0.8), "bolt", rot=(ang, 0, 0), pivot=(x, 12.6, -4.2))
    for side, s in (("l", 1), ("r", -1)):
        w = r.bone(f"wing_{side}", body, (s * 2.4, 9.4, -1.0), role=f"wing_{side}")
        def X(x0, ww):
            return x0 if s > 0 else -x0 - ww
        r.cube(w, (X(2.2, 4.2), 8.7, -2.6), (4.2, 1.3, 5.4), "tb_feather")       # coverts
        r.cube(w, (X(6.2, 3.6), 8.9, -2.2), (3.6, 0.9, 5.8), "tb_feather")
        r.cube(w, (X(2.2, 7.6), 8.4, -2.4), (7.6, 0.3, 5.0), "tb_chest")         # pale underwing
        for i, (x0, ln) in enumerate(((9.6, 5.6), (10.6, 5.0), (11.4, 4.2))):    # primaries splaying back
            r.cube(w, (X(x0 - 0.2 * i, 1.2), 9.0, -1.6 + i * 1.4), (1.2, 0.6, ln), "tb_dark")
            r.cube(w, (X(x0 - 0.2 * i, 1.2), 9.0, -1.6 + i * 1.4 + ln), (1.2, 0.6, 0.6), "bolt")
        r.cube(w, (X(2.8, 2.4), 10.0, -0.6), (2.4, 0.3, 0.6), "bolt")             # lightning stripe
        r.cube(w, (X(4.9, 0.6), 10.0, -0.6), (0.6, 0.3, 2.2), "bolt")
        r.cube(w, (X(5.2, 3.0), 9.85, 1.0), (3.0, 0.3, 0.6), "bolt")
    tail = r.bone("tail", body, (0, 7.6, 4.0), role="tail")
    r.cube(tail, (-1.8, 7.0, 3.6), (3.6, 0.9, 2.4), "tb_feather")
    for x, ang in ((-1.6, -22), (-0.45, 0), (0.7, 22)):
        r.cube(tail, (x, 7.1, 5.4), (0.9, 0.6, 4.4), "tb_dark", rot=(0, ang, 0), pivot=(x + 0.45, 7.4, 5.4))
        r.cube(tail, (x, 7.1, 9.6), (0.9, 0.6, 0.7), "bolt", rot=(0, ang, 0), pivot=(x + 0.45, 7.4, 5.4))
    for i, (x, y, z) in enumerate(((5, 13, -3), (-6, 6, 2), (2, 4, 6))):         # static motes
        o = r.bone(f"static{i}", body, (0, 8, 0), role="orbit")
        r.cube(o, (x - 0.4, y - 0.4, z - 0.4), (0.8, 0.8, 0.8), "bolt")
    return r


def island_warden():
    """A stone golem bearing a chunk of floating island on its back: grass, a windswept little tree, a
    glowing sky crystal and a thread of waterfall, roots dangling beneath; a crystal heart and crystal-vein
    cracks in its chest, glowing eyes under a heavy brow, chains lashing the island to its shoulders and
    a rusty anchor chained to its right fist."""
    r = Rig("island_warden")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 3.8, 10, 0), role=f"leg_{side}")
        r.cube(leg, (s * 3.8 - 2.5, 1.5, -2.5), (5, 9.5, 5), "ward_stone")
        r.cube(leg, (s * 3.8 - 3.0, 0, -3.6), (6, 2.2, 6.6), "ward_dark")         # foot slab
        r.cube(leg, (s * 3.8 - 2.7, 5.4, -2.8), (5.4, 1.8, 1.0), "ward_dark")     # knee plate
        r.cube(leg, (s * 3.8 - 1.8, 2.2, -3.7), (2.4, 0.8, 1.0), "moss")
    body = r.bone("body", None, (0, 10, 0), role="body")
    r.cube(body, (-6, 9, -3.5), (12, 4, 7), "ward_dark")                         # pelvis
    r.cube(body, (-8, 12, -4.5), (16, 10, 9), "ward_stone")                      # torso
    r.cube(body, (-6.5, 15, -5.0), (13, 5.5, 1.0), "ward_stone")                 # chest slab
    r.cube(body, (-1.6, 16.0, -5.5), (3.2, 3.4, 0.8), "sky_crystal")             # crystal heart
    r.cube(body, (-0.8, 19.4, -5.3), (0.5, 2.2, 0.4), "sky_crystal")             # crystal veins in the cracks
    r.cube(body, (1.6, 14.4, -5.3), (2.6, 0.4, 0.4), "sky_crystal")
    r.cube(body, (-4.4, 13.8, -5.3), (0.4, 2.4, 0.4), "sky_crystal")
    for s in (1, -1):
        r.cube(body, (s * 6.5 - 3.0, 19.0, -4.0), (6.0, 4.2, 8.0), "ward_stone")   # shoulder boulders
        r.cube(body, (s * 6.5 - 2.6, 23.0, -3.4), (5.2, 0.9, 5.0), "grass_top")    # moss caps
        r.cube(body, (s * 4.0 - 0.6, 12.6, -5.2), (1.2, 10.0, 0.5), "chain")        # chains lashing the island
        r.cube(body, (s * 4.0 - 0.6, 21.8, -5.2), (1.2, 0.6, 8.0), "chain")
    r.cube(body, (5.2, 23.9, -1.0), (0.6, 1.2, 0.6), "leaf_spring")               # grass tufts
    r.cube(body, (-6.4, 23.9, 0.2), (0.6, 0.9, 0.6), "leaf_spring")
    r.cube(body, (-7.2, 23.9, -2.0), (0.8, 0.8, 0.8), "petal")                    # one flower
    head = r.bone("head", body, (0, 20, -4), role="head")
    r.cube(head, (-3, 17.6, -8.5), (6, 5.4, 5), "ward_stone")
    r.cube(head, (-3.6, 21.8, -9.1), (7.2, 1.6, 2.4), "ward_dark")               # heavy brow
    r.cube(head, (-2.4, 19.8, -8.8), (1.8, 1.0, 0.4), "ward_eye")
    r.cube(head, (0.6, 19.8, -8.8), (1.8, 1.0, 0.4), "ward_eye")
    r.cube(head, (-0.6, 18.4, -9.1), (1.2, 1.8, 0.8), "ward_stone")              # stub nose
    r.cube(head, (1.8, 22.6, -7.0), (1.2, 0.9, 1.2), "moss")
    jaw = r.bone("jaw", head, (0, 18.6, -5.5), role="jaw")
    r.cube(jaw, (-2.8, 16.6, -8.9), (5.6, 1.8, 4.4), "ward_dark")
    for x in (-2.0, 1.0):
        r.cube(jaw, (x, 18.2, -9.0), (1.0, 0.8, 0.5), "stone")                    # blunt stone teeth
    for side, s in (("l", 1), ("r", -1)):
        cx = s * 9.2
        arm = r.bone(f"arm_{side}", body, (cx, 20.5, 0), role=f"arm_{side}")
        r.cube(arm, (cx - 2.2, 11, -2.2), (4.4, 8, 4.4), "ward_stone")
        r.cube(arm, (cx - 2.8, 4.6, -2.8), (5.6, 7, 5.6), "ward_stone")           # forearm
        r.cube(arm, (cx - 3.1, 1.2, -3.3), (6.2, 4.2, 6.6), "ward_dark")          # fist
        r.cube(arm, (cx - 2.6, 2.6, -3.6), (5.2, 0.9, 0.5), "ward_stone")         # knuckles
    r.cube("arm_l", (6.6, 11.4, -2.5), (5.0, 0.8, 5.0), "grass_top")             # moss on the left forearm
    r.cube("arm_l", (10.4, 12.2, -1.0), (0.6, 0.8, 0.6), "leaf_spring")
    r.cube("arm_r", (-12.2, 7.2, -3.0), (6.0, 1.2, 6.0), "rust")                 # iron band round the right wrist
    anc = r.bone("anchor", "arm_r", (-12.0, 7.8, 0))
    r.cube(anc, (-12.6, 5.4, -0.4), (0.8, 2.4, 0.8), "chain")
    r.cube(anc, (-12.8, 4.6, -1.0), (1.2, 1.0, 2.0), "rust")                     # anchor ring
    r.cube(anc, (-12.6, 0.4, -0.5), (0.8, 4.4, 1.0), "rust")                     # shank
    r.cube(anc, (-12.7, 3.6, -2.0), (1.0, 0.7, 4.0), "rust")                     # stock
    r.cube(anc, (-12.7, 0.2, -2.8), (1.0, 0.8, 5.6), "rust")                     # crown and arms
    r.cube(anc, (-12.7, 0.6, -3.2), (1.0, 1.6, 0.8), "rust")                     # flukes
    r.cube(anc, (-12.7, 0.6, 2.4), (1.0, 1.6, 0.8), "rust")
    isl = r.bone("island", body, (0, 22, 6))
    r.cube(isl, (-6, 21.5, 3.0), (12, 3.5, 8.0), "island_dirt")
    r.cube(isl, (-6.3, 25.0, 2.7), (12.6, 1.0, 8.6), "grass_top")
    r.cube(isl, (-4.6, 18.5, 4.0), (9.2, 3.2, 6.0), "island_dirt")
    r.cube(isl, (-3.0, 15.6, 5.0), (6.0, 3.0, 4.0), "ward_dark")
    r.cube(isl, (-1.4, 13.6, 5.8), (2.8, 2.2, 2.4), "ward_dark")
    r.cube(isl, (3.0, 14.0, 7.2), (0.4, 4.6, 0.4), "root")                       # dangling roots
    r.cube(isl, (-3.6, 16.2, 8.4), (0.4, 3.2, 0.4), "root")
    r.cube(isl, (-1.6, 15.2, 10.95), (2.0, 9.8, 0.3), "waterfall")               # thread of waterfall
    r.cube(isl, (-1.8, 25.4, 9.0), (2.4, 0.4, 2.0), "waterfall")                 # its little pool
    r.cube(isl, (2.0, 26.0, 6.0), (1.4, 4.2, 1.4), "root")                       # tree trunk
    r.cube(isl, (2.2, 28.0, 6.4), (2.6, 0.6, 0.6), "root")                       # wind-bent branch
    r.cube(isl, (0.2, 29.4, 4.4), (5.6, 2.8, 5.0), "leaf_sky")
    r.cube(isl, (1.2, 32.0, 5.0), (3.4, 1.4, 3.4), "leaf_sky")
    r.cube(isl, (-4.6, 26.0, 4.2), (1.8, 4.0, 1.8), "sky_crystal", rot=(0, 0, 12), pivot=(-3.7, 26, 5.1))
    r.cube(isl, (-3.2, 26.0, 6.4), (1.0, 2.4, 1.0), "sky_crystal", rot=(0, 0, -15), pivot=(-2.7, 26, 6.9))
    r.cube(isl, (-1.0, 26.0, 3.4), (1.6, 1.0, 1.4), "stone")                     # pebbles
    return r


def cloud_mine():
    """A naval sea-mine swallowed by a thundercloud: a riveted iron shell cracked with lightning, horned
    detonators with sparking caps poking through the puffs, two slit eyes and a jagged lit grin, a dark
    rain-heavy underside and forked lightning dangling below."""
    r = Rig("cloud_mine")
    Y = 9.5
    body = r.bone("body", None, (0, Y, 0), role="body")
    r.cube(body, (-3.5, Y - 3, -3.5), (7, 6, 7), "mine_iron")                    # shell
    r.cube(body, (-3, Y - 3.5, -3), (6, 7, 6), "mine_iron")
    r.cube(body, (-3.9, Y - 0.5, -3.9), (7.8, 1.0, 7.8), "brass")                # riveted seam
    r.cube(body, (1.4, Y + 0.6, -3.65), (0.4, 2.0, 0.2), "mine_crack")           # lightning cracks
    r.cube(body, (1.6, Y + 2.4, -3.65), (1.2, 0.4, 0.2), "mine_crack")
    r.cube(body, (3.55, Y - 2.4, -1.0), (0.2, 1.8, 0.4), "mine_crack")
    # detonator horns: iron stalks with sparking caps
    horns = ((0, Y + 3.4, 0, (0, 1, 0)), (-2.4, Y + 2.6, -2.4, (0, 1, 0)), (3.9, Y + 0.6, 0.8, (1, 0, 0)),
             (-3.9, Y + 0.6, -0.8, (-1, 0, 0)), (0, Y + 0.4, 3.9, (0, 0, 1)), (2.4, Y + 2.6, -2.4, (0, 1, 0)))
    for x, y, z, (dx, dy, dz) in horns:
        L = 1.8
        sx, sy, sz = (L if dx else 1.0), (L if dy else 1.0), (L if dz else 1.0)
        ox = x - 0.5 if not dx else (x if dx > 0 else x - L)
        oy = y - 0.5 if not dy else (y if dy > 0 else y - L)
        oz = z - 0.5 if not dz else (z if dz > 0 else z - L)
        r.cube(body, (ox, oy, oz), (sx, sy, sz), "mine_iron")
        cx, cy, cz = x + dx * L, y + dy * L, z + dz * L
        r.cube(body, (cx - 0.6, cy - 0.6, cz - 0.6), (1.2, 1.2, 1.2), "bolt")
    # the thundercloud wrapped around it
    for (x, y, z, w, h, d) in ((-7.4, Y - 1.6, -2.6, 4.4, 4.0, 5.6), (3.4, Y - 1.2, -2.0, 4.6, 4.2, 5.4),
                               (-3.6, Y + 2.0, 0.4, 5.0, 3.0, 4.4), (-4.6, Y - 1.8, 2.6, 8.4, 4.4, 3.6),
                               (1.0, Y + 1.8, 1.2, 4.0, 2.6, 3.6), (-6.0, Y + 1.2, -1.6, 2.8, 2.2, 3.0)):
        r.cube(body, (x, y, z), (w, h, d), "thundercloud")
    for (x, y, z, w, h, d) in ((-6.6, Y + 2.0, -1.8, 3.4, 1.6, 3.6), (3.8, Y + 2.6, -1.4, 3.4, 1.4, 3.8),
                               (-3.0, Y + 4.6, 1.0, 3.6, 1.4, 3.2), (1.4, Y + 4.0, 1.8, 2.8, 1.2, 2.6)):
        r.cube(body, (x, y, z), (w, h, d), "cloud")                                # sunlit tops of the puffs
    r.cube(body, (-6.8, Y - 3.6, -3.4), (13.6, 2.0, 7.6), "cloud_belly")         # rain-dark underside
    r.cube(body, (-5.0, Y - 4.4, -2.2), (10.0, 1.0, 5.4), "cloud_belly")
    head = r.bone("head", body, (0, Y, -3.6), role="head")                       # its face on the shell
    r.cube(head, (-2.6, Y + 1.0, -3.8), (1.8, 0.7, 0.3), "mine_eye", rot=(0, 0, -15), pivot=(-1.7, Y + 1.3, -3.8))
    r.cube(head, (0.8, Y + 1.0, -3.8), (1.8, 0.7, 0.3), "mine_eye", rot=(0, 0, 15), pivot=(1.7, Y + 1.3, -3.8))
    r.cube(head, (-2.6, Y - 2.2, -3.75), (5.2, 0.6, 0.2), "mine_crack")          # jagged grin
    for x in (-1.8, -0.4, 1.0):
        r.cube(head, (x, Y - 1.8, -3.8), (0.6, 0.6, 0.2), "mine_crack")
    # forked lightning hanging below
    for i, (x, z) in enumerate(((-2.4, -0.6), (2.2, 1.0))):
        t = r.bone(f"bolt{i}", body, (x, Y - 4.4, z), role="tail")
        y = Y - 4.4
        for j, off in enumerate((0, 0.7, -0.2, 0.6)):
            h = 1.4
            r.cube(t, (x + off - 0.3, y - h, z - 0.3), (0.6, h + 0.2, 0.6), "bolt")
            y -= h
    for i, (x, y, z) in enumerate(((8, Y + 2, 0), (-8, Y - 1, 2), (0, Y + 5, 6))):
        o = r.bone(f"puff{i}", body, (0, Y, 0), role="orbit")
        r.cube(o, (x - 1.0, y - 0.7, z - 1.0), (2.0, 1.4, 2.0), "cloud" if i < 2 else "bolt")
    return r


def sky_harpooner():
    """A sky-pirate whaler: weathered face with a bushy ginger beard and an eye patch, leather flight cap
    with brass goggles, red scarf streaming behind, long storm-blue coat with brass buttons and a
    bandolier of barbs, a rope coil on the back, a peg leg, and a brass harpoon gun with a winch reel and
    a lightning-charged barbed harpoon; a grappling hook swings from his other hand."""
    r = Rig("sky_harpooner")
    leg = r.bone("leg_l", None, (2, 12, 0), role="leg_l")                         # the peg leg
    r.cube(leg, (0.4, 7.6, -1.6), (3.2, 4.8, 3.2), "trouser")
    r.cube(leg, (0.6, 7.0, -1.4), (2.8, 1.0, 2.8), "leather")                      # strap
    r.cube(leg, (1.3, 0.6, -0.7), (1.4, 7.0, 1.4), "wood_light")
    r.cube(leg, (1.15, 3.6, -0.85), (1.7, 0.6, 1.7), "brass")
    r.cube(leg, (1.1, 0, -0.9), (1.8, 0.8, 1.8), "iron")
    leg = r.bone("leg_r", None, (-2, 12, 0), role="leg_r")
    r.cube(leg, (-3.6, 4.4, -1.6), (3.2, 8.0, 3.2), "trouser")
    r.cube(leg, (-3.9, 0, -2.6), (3.8, 5.4, 4.0), "leather")                       # tall boot
    r.cube(leg, (-4.0, 4.6, -2.7), (4.0, 1.2, 4.2), "leather")
    r.cube(leg, (-2.4, 3.0, -2.8), (0.8, 0.8, 0.3), "brass")
    body = r.bone("body", None, (0, 12, 0), role="body")
    r.cube(body, (-4.4, 8.0, -2.8), (8.8, 5.0, 5.6), "coat_storm")               # coat skirt front panels
    r.cube(body, (-4.6, 12.4, -3.0), (9.2, 9.8, 6.0), "coat_storm")              # torso
    r.cube(body, (-1.2, 14.4, -3.15), (2.4, 7.6, 0.3), "shirt")
    r.cube(body, (-2.4, 17.0, -3.25), (1.2, 5.0, 0.3), "cloth_red", rot=(0, 0, 12), pivot=(-1.8, 22, -3.2))   # lapels
    r.cube(body, (1.2, 17.0, -3.25), (1.2, 5.0, 0.3), "cloth_red", rot=(0, 0, -12), pivot=(1.8, 22, -3.2))
    for y in (14.6, 16.4):
        r.cube(body, (-2.4, y, -3.3), (0.7, 0.7, 0.3), "brass")
        r.cube(body, (1.7, y, -3.3), (0.7, 0.7, 0.3), "brass")
    r.cube(body, (-4.8, 12.0, -3.2), (9.6, 1.4, 6.4), "leather")                 # belt
    r.cube(body, (-0.9, 11.8, -3.5), (1.8, 1.8, 0.4), "brass")
    r.cube(body, (-4.2, 13.6, -3.4), (1.4, 9.6, 0.4), "leather", rot=(0, 0, -38), pivot=(0, 18, -3.4))   # bandolier
    for i in range(3):
        r.cube(body, (-2.6 + i * 1.5, 15.0 + i * 1.6, -3.7), (0.8, 1.2, 0.4), "harp_steel")
    r.cube(body, (3.4, 9.6, -2.2), (1.2, 3.2, 1.2), "brass")                     # spyglass on the belt
    # rope coil on the back
    for (x, y, w, h) in ((-3.0, 18.4, 6.0, 1.0), (-3.0, 13.4, 6.0, 1.0), (-3.0, 13.4, 1.0, 6.0), (2.0, 13.4, 1.0, 6.0)):
        r.cube(body, (x, y, 3.0), (w, h, 1.2), "rope")
    r.cube(body, (-5.0, 17.4, -3.4), (1.0, 5.0, 7.0), "rope", rot=(0, 0, -30), pivot=(-4.5, 20, 0))
    for side, s in (("tail_l", 1), ("tail_r", -1)):                              # coat tails
        t = r.bone(side, body, (s * 2.2, 12.4, 2.6), role="tail")
        r.cube(t, (s * 2.2 - 2.2, 3.2, 2.0), (4.4, 9.6, 1.0), "coat_storm")
        r.cube(t, (s * 2.2 - 2.2, 3.2, 2.15), (4.4, 1.2, 1.0), "cloth_red")
    head = r.bone("head", body, (0, 22, 0), role="head")
    r.cube(head, (-2.8, 22.0, -3.0), (5.6, 5.6, 5.6), "harp_skin")
    r.cube(head, (-3.0, 20.6, -3.5), (6.0, 2.8, 2.6), "beard")                  # bushy beard
    r.cube(head, (-2.2, 22.8, -3.6), (4.4, 0.8, 0.6), "beard")                  # moustache
    r.cube(head, (-0.6, 23.4, -3.8), (1.2, 1.6, 0.9), "harp_skin")              # nose
    r.cube(head, (0.8, 24.6, -3.2), (1.4, 1.0, 0.3), "eye_white")
    r.cube(head, (1.2, 24.6, -3.3), (0.7, 0.8, 0.2), "pupil")
    r.cube(head, (-2.4, 24.2, -3.25), (1.8, 1.6, 0.3), "fur_black")             # eye patch
    r.cube(head, (-3.0, 25.4, -3.2), (6.0, 0.4, 6.2), "fur_black", rot=(0, 0, -14), pivot=(0, 25.4, 0))  # its strap
    r.cube(head, (-3.2, 26.6, -3.4), (6.4, 2.2, 6.8), "cap_leather")            # flight cap
    r.cube(head, (-3.3, 23.4, -2.2), (0.6, 3.6, 3.2), "cap_leather")            # ear flaps
    r.cube(head, (2.7, 23.4, -2.2), (0.6, 3.6, 3.2), "cap_leather")
    r.cube(head, (-3.3, 26.5, -3.5), (6.6, 0.6, 0.4), "leather")                # goggle strap
    for x in (-2.4, 0.4):
        r.cube(head, (x, 26.9, -3.9), (2.0, 1.8, 0.8), "brass")                 # goggles pushed up
        r.cube(head, (x + 0.4, 27.3, -4.0), (1.2, 1.0, 0.2), "goggle")
    sc = r.bone("scarf", head, (1.0, 21.6, 2.6), role="tail")                    # scarf streaming back
    r.cube(head, (-3.0, 21.0, -3.2), (6.0, 1.6, 6.2), "cloth_red")
    r.cube(sc, (0.2, 17.4, 2.6), (2.0, 4.4, 0.6), "cloth_red", rot=(20, 0, 0), pivot=(1.0, 21.6, 2.6))
    r.cube(sc, (0.2, 17.4, 2.6), (2.0, 0.8, 0.6), "shirt", rot=(20, 0, 0), pivot=(1.0, 21.6, 2.6))
    for side, s in (("l", 1), ("r", -1)):
        cx = s * 5.6
        arm = r.bone(f"arm_{side}", body, (cx, 21, 0), role=f"arm_{side}")
        r.cube(arm, (cx - 1.6, 14.0, -1.6), (3.2, 8.0, 3.2), "coat_storm")
        r.cube(arm, (cx - 1.9, 13.0, -1.9), (3.8, 1.8, 3.8), "cloth_red")       # turned-back cuff
        r.cube(arm, (cx - 1.4, 10.8, -1.4), (2.8, 2.4, 2.8), "leather")         # glove
    r.cube("arm_r", (-7.8, 20.0, -2.0), (4.4, 1.4, 4.0), "brass")               # brass epaulette
    # harpoon gun, lowered toward the ground in front: modelled hanging straight down from the fist
    # (so its length doesn't widen the hitbox) and swung forward by the bone
    P = (-5.6, 12.0, 0)
    gun = r.bone("gun", "arm_r", P, rot=(55, 0, 0))

    def g(origin, size, m):
        (x, y, z), (w, h, d) = origin, size
        r.cube(gun, (x, P[1] + z - P[2], P[2] - (y + h - P[1])), (w, d, h), m)
    g((-6.4, 11.2, -0.6), (1.6, 1.8, 4.8), "wood_dark")                          # stock
    g((-6.2, 11.4, -10.0), (1.2, 1.3, 9.6), "brass")                             # barrel
    g((-6.5, 11.1, -10.6), (1.8, 1.9, 0.8), "iron")                              # muzzle
    g((-6.7, 9.4, -5.0), (2.2, 2.0, 2.2), "brass")                               # winch reel
    g((-6.6, 9.6, -4.8), (2.0, 1.6, 1.8), "rope")
    g((-4.4, 9.8, -4.2), (1.2, 0.4, 0.4), "iron")                                # crank
    g((-5.85, 11.8, -16.0), (0.5, 0.5, 6.0), "harp_steel")                       # harpoon shaft
    g((-6.3, 11.5, -18.0), (1.4, 1.1, 2.0), "harp_steel")                        # barbed head
    g((-7.0, 11.7, -16.8), (2.8, 0.5, 0.6), "harp_steel")                        # barbs
    g((-5.95, 11.75, -19.0), (0.7, 0.6, 1.0), "bolt")                            # charged tip
    # grappling hook swinging from the left hand
    hk = r.bone("grapple", "arm_l", (5.6, 11, 0))
    r.cube(hk, (5.35, 6.4, -0.25), (0.5, 4.8, 0.5), "rope")
    r.cube(hk, (5.1, 4.2, -0.4), (1.0, 2.4, 0.8), "iron")
    r.cube(hk, (4.0, 4.0, -0.3), (3.2, 0.6, 0.6), "iron")
    r.cube(hk, (4.0, 4.0, -0.3), (0.6, 1.4, 0.6), "iron")
    r.cube(hk, (6.6, 4.0, -0.3), (0.6, 1.4, 0.6), "iron")
    return r
