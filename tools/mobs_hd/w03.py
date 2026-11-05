"""World 3, Endless Dungeon: prisons, locks, chains and keys."""
from common import Rig, mat

# ---------------------------------------------------------------- palette
mat("jail_coat", "2c333d", "4a5462", "cloth")         # slate warder's greatcoat
mat("jail_hood", "5a2a22", "8a4232", "cloth")         # rust-red hood and mantle
mat("jail_skin", "b89a7a", "d0b494", "skin")          # sallow, sunless skin
mat("jail_nose", "b8705a", "d08a70", "skin")
mat("stubble", "6a5848", "8a7460", "fur")
mat("key_brass", "b08a30", "f0d070", "metal")
mat("lantern_fire", "ffb040", "ffd070", "glow", True)
mat("old_iron", "3e4046", "6a6e78", "metal")
mat("chain_dark", "4a4e56", "8a8f98", "chain")

mat("sent_iron", "4a4e56", "7a808c", "metal")
mat("sent_plate", "5e636c", "9aa0aa", "metal")
mat("sent_eye", "ff3a1a", "ff7a3a", "glow", True)
mat("sent_iris", "ffb02a", "ffd060", "glow", True)
mat("sent_slit", "120c0a", "2a1a14", "skin")

mat("lock_brass", "9a7228", "e0b850", "metal")
mat("lock_steel", "8a9098", "d0d6de", "metal")
mat("lock_throat", "c02a1a", "ff6a2a", "magma", True)
mat("lock_eye", "ffc830", "ffe070", "glow", True)
mat("wax", "a01e1e", "e04a3a", "skin")
mat("parchment", "d8c89a", "f0e4c0", "cloth")

mat("rat_fur", "4e4038", "7a6656", "fur")
mat("rat_belly", "8a786a", "a89480", "fur")
mat("rat_tooth", "d8b040", "f0d880", "skin")
mat("rat_nose", "d0707a", "f0a0a8", "skin")
mat("rat_eye", "ff2a1a", "ff5a3a", "glow", True)
mat("scar", "8a3a3a", "b05a5a", "skin")

mat("exe_hood", "141216", "2e2a34", "cloth")
mat("exe_pants", "2a2428", "403840", "cloth")
mat("exe_skin", "a88a78", "c8a690", "flesh")
mat("exe_apron", "4a2e1a", "6a4428", "cloth")
mat("exe_blade", "50555e", "8a909a", "metal")
mat("exe_edge", "b8c0c8", "f0f4f8", "metal")
mat("bandage", "c8bca0", "e0d6bc", "cloth")
mat("exe_eye", "ff2a1a", "ff6a3a", "glow", True)


# ---------------------------------------------------------------- helpers
def chain(r, bone, x, ytop, z, n, m="chain_dark", link=1.7):
    """A hanging chain of n alternating links, from ytop down; returns the bottom y."""
    y = ytop
    for i in range(n):
        if i % 2 == 0:
            r.cube(bone, (x - 0.3, y - link, z - 0.7), (0.6, link + 0.2, 1.4), m)
        else:
            r.cube(bone, (x - 0.7, y - link, z - 0.3), (1.4, link + 0.2, 0.6), m)
        y -= link - 0.2
    return y


def key(r, bone, x, ytop, z, m="key_brass", length=3.2, ang=0):
    """A hanging key facing front: bow, shaft and a toothed bit."""
    kw = dict(rot=(0, 0, ang), pivot=(x, ytop, z)) if ang else {}
    r.cube(bone, (x - 0.9, ytop - 1.6, z - 0.25), (1.8, 1.6, 0.5), m, **kw)
    r.cube(bone, (x - 0.3, ytop - 1.6 - length, z - 0.2), (0.6, length, 0.4), m, **kw)
    r.cube(bone, (x + 0.3, ytop - 1.4 - length, z - 0.2), (0.9, 1.0, 0.4), m, **kw)


def shackle(r, bone, x, y, z, m="old_iron", s=2.4):
    """An open iron cuff: a square ring lying flat."""
    r.cube(bone, (x - s / 2, y, z - s / 2), (s, 0.8, 0.5), m)
    r.cube(bone, (x - s / 2, y, z + s / 2 - 0.5), (s, 0.8, 0.5), m)
    r.cube(bone, (x - s / 2, y, z - s / 2), (0.5, 0.8, s), m)
    r.cube(bone, (x + s / 2 - 0.5, y, z - s / 2), (0.5, 0.8, s), m)


# ---------------------------------------------------------------- creatures
def jailer_mob():
    """A hunched prison warder: rust hood over a sour, squinting face, slate greatcoat, a big jangling
    ring of keys on the hip, an iron-capped baton in one fist and a lit lantern swinging from the other."""
    r = Rig("jailer_mob")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 2, 9, 0), role=f"leg_{side}")
        r.cube(leg, (s * 2 - 1.4, 2, -1.4), (2.8, 7.5, 2.8), "jail_coat")
        r.cube(leg, (s * 2 - 1.7, 0, -2.4), (3.4, 2.6, 3.8), "leather")
        r.cube(leg, (s * 2 - 1.8, 2.2, -1.8), (3.6, 0.8, 3.6), "old_iron")       # boot band
    body = r.bone("body", None, (0, 10, 0), role="body")
    r.cube(body, (-4.6, 4.5, -3), (9.2, 6.5, 6), "jail_coat")                     # coat skirt
    r.cube(body, (-4.6, 3.4, -3), (2.0, 1.1, 6), "jail_coat")                     # ragged hem
    r.cube(body, (1.4, 3.8, -3), (2.4, 0.7, 6), "jail_coat")
    r.cube(body, (-5, 10.5, -3.4), (10, 7.5, 7), "jail_coat")                    # chest
    r.cube(body, (-4.6, 15, -1), (9.2, 4.5, 5.5), "jail_coat")                   # the hunch
    r.cube(body, (-5.6, 16.6, -4), (11.2, 2.6, 8.4), "jail_hood")                # mantle over the shoulders
    r.cube(body, (-4, 13.6, 3.6), (8, 3.4, 1.4), "jail_hood")                    # mantle back drop
    r.cube(body, (-5.2, 9.8, -3.7), (10.4, 1.6, 7.4), "leather")                 # belt
    r.cube(body, (-1.1, 9.6, -4.1), (2.2, 2, 0.5), "key_brass")                  # buckle
    r.cube(body, (1.6, 14.4, -3.8), (1.6, 1.8, 0.5), "key_brass")                # warder's badge
    r.cube(body, (2.0, 14.8, -4.0), (0.8, 1.0, 0.3), "rat_eye")                  # its enamel stone
    r.cube(body, (-0.4, 12.4, -3.7), (0.8, 3.2, 0.4), "old_iron")                # button placket
    # big ring of keys hanging at the front of the right hip
    ring = r.bone("key_ring", body, (-3.6, 10, -3.9), role="tail")
    r.cube(ring, (-5.4, 8.8, -4.3), (3.6, 0.6, 0.5), "key_brass")
    r.cube(ring, (-5.4, 5.8, -4.3), (3.6, 0.6, 0.5), "key_brass")
    r.cube(ring, (-5.4, 5.8, -4.3), (0.6, 3.6, 0.5), "key_brass")
    r.cube(ring, (-2.4, 5.8, -4.3), (0.6, 3.6, 0.5), "key_brass")
    key(r, ring, -5.0, 6.2, -4.7, "key_brass", 3.0, ang=-16)
    key(r, ring, -3.6, 6.0, -4.9, "old_iron", 3.8, ang=4)
    key(r, ring, -2.2, 6.2, -4.6, "key_brass", 2.6, ang=22)
    # head, pushed forward by the hunch
    head = r.bone("head", body, (0, 19, -2.5), role="head")
    r.cube(head, (-2.8, 18.6, -7.6), (5.6, 5.4, 5.6), "jail_skin")
    r.cube(head, (-3.1, 22.0, -8.0), (6.2, 1.0, 1.2), "stubble")                 # one long frown of a brow
    r.cube(head, (-2.4, 20.6, -7.8), (1.8, 1.2, 0.3), "eye_white")
    r.cube(head, (-1.6, 20.6, -7.95), (0.8, 1.0, 0.3), "pupil")
    r.cube(head, (0.7, 20.8, -7.8), (1.7, 0.7, 0.3), "eye_white")               # the squinting eye
    r.cube(head, (1.0, 20.8, -7.95), (0.7, 0.6, 0.3), "pupil")
    r.cube(head, (-0.8, 19.3, -8.8), (1.6, 2.4, 1.3), "jail_nose")              # bulbous nose
    r.cube(head, (-1.8, 18.9, -7.75), (3.6, 0.5, 0.3), "maw")                    # sour mouth line
    r.cube(head, (1.6, 21.6, -7.9), (0.3, 1.6, 0.2), "scar")                     # old scar over the squint
    jaw = r.bone("jaw", head, (0, 19.2, -4), role="jaw")
    r.cube(jaw, (-2.6, 17.2, -7.7), (5.2, 2.0, 4.8), "stubble")
    r.cube(jaw, (-1.4, 18.8, -7.9), (0.7, 0.8, 0.3), "rat_tooth")                # one crooked tooth
    # hood: thin cheeks so the face reads, rounded crown, a drooping point
    r.cube(head, (-3.7, 23.6, -8.2), (7.4, 1.6, 7.8), "jail_hood")
    r.cube(head, (-3.0, 25.0, -7.2), (6.0, 1.0, 6.0), "jail_hood")
    r.cube(head, (2.9, 17.6, -8.2), (0.9, 6.4, 7.8), "jail_hood")
    r.cube(head, (-3.8, 17.6, -8.2), (0.9, 6.4, 7.8), "jail_hood")
    r.cube(head, (-3.7, 17.6, -1.2), (7.4, 6.8, 1.6), "jail_hood")
    r.cube(head, (-1.4, 23.6, -0.4), (2.8, 2.2, 3.4), "jail_hood", rot=(-35, 0, 0), pivot=(0, 24.5, -0.5))
    # arms
    for side, s in (("l", 1), ("r", -1)):
        cx = s * 5.6
        arm = r.bone(f"arm_{side}", body, (cx, 18, -1.6), role=f"arm_{side}")
        r.cube(arm, (cx - 1.7, 16.2, -3.4), (3.4, 2.8, 3.6), "old_iron")          # pauldron
        r.cube(arm, (cx - 1.4, 11.6, -3.0), (2.8, 5.4, 2.8), "jail_coat")
        r.cube(arm, (cx - 1.6, 10.6, -3.2), (3.2, 1.6, 3.2), "jail_hood")         # cuff
        r.cube(arm, (cx - 1.2, 8.8, -2.8), (2.4, 2.2, 2.4), "leather")            # glove
    bat = r.bone("baton", "arm_r", (-5.6, 9.8, -1.6), rot=(12, 0, 0))
    r.cube(bat, (-6.3, 9.1, -10.5), (1.4, 1.4, 11), "wood_dark")
    r.cube(bat, (-6.5, 8.9, -10.9), (1.8, 1.8, 1.6), "old_iron")                  # iron cap
    r.cube(bat, (-6.6, 9.6, -7.6), (2.0, 0.5, 0.5), "old_iron")                   # stud band
    lan = r.bone("lantern", "arm_l", (5.6, 8.8, -1.6))
    r.cube(lan, (5.3, 7.4, -1.9), (0.6, 1.6, 0.6), "old_iron")                    # bail
    r.cube(lan, (4.3, 6.6, -2.9), (2.6, 0.9, 2.6), "old_iron")                    # cap
    r.cube(lan, (4.6, 3.8, -2.6), (2.0, 2.8, 2.0), "lantern_fire")                # flame
    r.cube(lan, (4.3, 3.8, -2.9), (0.5, 2.8, 0.5), "old_iron")                    # frame posts
    r.cube(lan, (6.4, 3.8, -2.9), (0.5, 2.8, 0.5), "old_iron")
    r.cube(lan, (4.3, 3.2, -2.9), (2.6, 0.7, 2.6), "old_iron")                    # base
    return r


def sentinel():
    """A floating iron great-helm that keeps watch: one huge burning eye in the T of its visor, a hinged
    breathing grille that drops open to fire, rivets, dents and rust, a mail aventail, chains it hurls
    from above, a padlock weight and an alarm bell at the nape."""
    r = Rig("sentinel")
    body = r.bone("body", None, (0, 15, 0), role="body")
    r.cube(body, (-5, 10, -4), (10, 10.5, 8), "sent_iron")                       # octagonal bucket
    r.cube(body, (-4, 10, -5), (8, 10.5, 10), "sent_iron")
    r.cube(body, (-5.4, 19.8, -5.4), (10.8, 1.4, 10.8), "sent_plate")            # crown band
    r.cube(body, (-4.0, 21.2, -4.0), (8.0, 1.2, 8.0), "sent_iron")               # flat top
    r.cube(body, (-1.0, 22.4, -1.0), (2.0, 1.0, 2.0), "old_iron")                # bolt on top
    for s in (1, -1):                                                            # swept iron horns
        r.cube(body, (s * 5.2 - 1.0, 18.0, -1.2), (2.0, 2.4, 2.4), "sent_plate")
        r.cube(body, (s * 6.0 - 0.7, 19.6, -0.9), (1.4, 3.0, 1.8), "sent_iron", rot=(0, 0, -s * 25), pivot=(s * 6, 19.6, 0))
        r.cube(body, (s * 7.4 - 0.45, 22.0, -0.6), (0.9, 2.2, 1.2), "key_brass", rot=(0, 0, -s * 40), pivot=(s * 7.4, 22, 0))
    for x in (-4.4, -2.4, 1.6, 3.6):                                             # crown rivets
        r.cube(body, (x, 20.2, -5.7), (0.8, 0.8, 0.4), "key_brass")
    r.cube(body, (5.2, 20.2, -3.6), (0.4, 0.8, 7.2), "key_brass")
    r.cube(body, (-5.6, 20.2, -3.6), (0.4, 0.8, 7.2), "key_brass")
    # visor: brow plate, dark slit, and the vertical breath slit of the T
    r.cube(body, (-4.4, 16.8, -5.7), (8.8, 3.2, 0.9), "sent_plate")
    r.cube(body, (-4.6, 16.4, -5.9), (9.2, 0.6, 0.6), "old_iron")
    r.cube(body, (-4.0, 14.2, -5.25), (8.0, 2.4, 0.4), "sent_slit")
    r.cube(body, (2.4, 18.0, -5.85), (1.2, 0.9, 0.3), "rust")                    # dent
    r.cube(body, (4.85, 12.0, -2.0), (0.3, 3.0, 2.4), "rust")
    r.cube(body, (-5.15, 13.0, 1.0), (0.3, 0.4, 3.0), "sent_slit")               # crack
    for s in (1, -1):                                                            # cheek bosses
        r.cube(body, (s * 5.0 - 0.6, 12.5, -3.0), (1.2, 4, 4), "sent_plate")
        r.cube(body, (s * 5.5 - 0.4, 13.9, -1.6), (0.8, 1.2, 1.2), "key_brass")
    r.cube(body, (4.4, 7.8, -3.6), (0.6, 2.6, 7.4), "chain")                     # mail aventail
    r.cube(body, (-5.0, 7.8, -3.6), (0.6, 2.6, 7.4), "chain")
    r.cube(body, (-4.0, 7.8, 4.4), (8.0, 2.6, 0.6), "chain")
    # the one eye, bulging through the slit
    head = r.bone("head", body, (0, 15.4, -4.6), role="head")
    r.cube(head, (-2.0, 13.6, -5.6), (4.0, 3.6, 0.6), "sent_eye")
    r.cube(head, (-1.1, 14.3, -5.8), (2.2, 2.2, 0.3), "sent_iris")
    r.cube(head, (-0.35, 14.1, -5.95), (0.7, 2.6, 0.3), "pupil")                 # slit pupil
    r.cube(head, (-3.8, 14.8, -5.35), (1.6, 0.8, 0.2), "sent_eye")              # glow leaking along the slit
    r.cube(head, (2.2, 14.8, -5.35), (1.6, 0.8, 0.2), "sent_eye")
    # hinged grille: drops open to fire
    jaw = r.bone("jaw", body, (0, 13.6, -5.4), role="jaw")
    r.cube(jaw, (-4.4, 10.0, -5.9), (8.8, 3.6, 0.9), "sent_plate")
    r.cube(jaw, (-0.4, 10.4, -6.0), (0.8, 3.0, 0.3), "sent_slit")                # breath slit
    for x in (-3.2, -1.8, 1.0, 2.4):
        r.cube(jaw, (x, 11.6, -6.0), (0.8, 0.8, 0.3), "sent_slit")
    r.cube(jaw, (-4.6, 9.6, -6.1), (9.2, 0.6, 1.2), "old_iron")                  # lower rim
    r.cube(body, (-3.6, 10.6, -5.05), (7.2, 2.8, 0.2), "lantern_fire")          # forge glow behind it
    # chains it throws, hanging from the cheek bosses and swinging out
    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", body, (s * 5.6, 12.6, -1.0), rot=(0, 0, s * 14), role=f"arm_{side}")
        y = chain(r, arm, s * 5.6, 12.6, -1.0, 4 if s > 0 else 5)
        r.cube(arm, (s * 5.6 - 0.3, y - 2.4, -1.3), (0.6, 2.6, 0.6), "old_iron")   # hook shank
        r.cube(arm, (s * 5.6 - 0.3, y - 2.6, -2.6), (0.6, 0.6, 1.9), "old_iron")   # hook curve
        r.cube(arm, (s * 5.6 - 0.3, y - 2.0, -2.6), (0.6, 0.9, 0.5), "lock_steel")  # barb
    # rear chain ending in a padlock weight
    tail = r.bone("tail", body, (0, 10.2, 2.5), role="tail")
    y = chain(r, tail, 0, 10.4, 2.5, 3)
    r.cube(tail, (-0.8, y - 1.4, 2.2), (1.6, 1.6, 0.5), "lock_steel")            # padlock shackle
    r.cube(tail, (-1.4, y - 4.0, 1.7), (2.8, 2.6, 1.6), "lock_brass")
    r.cube(tail, (-0.3, y - 3.4, 1.55), (0.6, 1.2, 0.2), "sent_slit")
    bell = r.bone("bell", body, (0, 12, 5))
    r.cube(bell, (-1.0, 9.6, 4.6), (2.0, 1.8, 1.4), "key_brass")
    r.cube(bell, (-1.3, 9.2, 4.3), (2.6, 0.6, 2.0), "key_brass")
    for i, (x, y, z) in enumerate(((8, 18, 0), (-7.5, 13, 2))):                 # watching sparks
        o = r.bone(f"mote{i}", body, (0, 15, 0), role="orbit")
        r.cube(o, (x - 0.6, y - 0.6, z - 0.6), (1.2, 1.2, 1.2), "sent_eye")
    return r


def living_lock():
    """A huge brass padlock waddling on iron stubs: a keyhole that is a mouth lined with tumbler teeth and
    a red glowing throat, a snapping shackle, glaring eyes under angry steel brows, a key jammed in its
    flank, a chain down its side, a wax seal and a paper tag on a string."""
    r = Rig("living_lock")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 3.6, 3, 0), role=f"leg_{side}")
        r.cube(leg, (s * 3.6 - 1.3, 0.6, -1.4), (2.6, 3.0, 2.8), "old_iron")
        r.cube(leg, (s * 3.6 - 1.6, 0, -2.6), (3.2, 1.0, 3.6), "old_iron")
        for dx in (-1.2, 0.0, 1.2):                                                # toe claws
            r.cube(leg, (s * 3.6 + dx - 0.3, 0, -3.1), (0.6, 0.6, 0.6), "lock_steel")
    body = r.bone("body", None, (0, 3, 0), role="body")
    r.cube(body, (-6, 2.6, -3.5), (12, 9.6, 7), "lock_brass")                   # case
    r.cube(body, (-5.4, 2.0, -3.0), (10.8, 1.0, 6.0), "lock_brass")              # rounded bottom
    r.cube(body, (-6.3, 10.9, -3.8), (12.6, 1.5, 7.6), "old_iron")               # top band
    r.cube(body, (-6.3, 3.0, -3.8), (12.6, 1.1, 7.6), "old_iron")                # bottom band
    for x in (-5.6, 4.8):                                                        # band rivets
        for y in (3.15, 11.2):
            r.cube(body, (x, y, -4.0), (0.8, 0.8, 0.3), "lock_steel")
    for s in (1, -1):                                                            # glaring eyes
        r.cube(body, (s * 3.8 - 1.0, 8.2, -3.7), (2.0, 1.8, 0.3), "maw")
        r.cube(body, (s * 3.8 - 0.8, 8.3, -3.85), (1.6, 1.3, 0.3), "lock_eye")
        r.cube(body, (s * 3.8 - 0.3 - s * 0.25, 8.3, -3.95), (0.6, 1.3, 0.2), "pupil")
        r.cube(body, (s * 3.8 - 1.5, 9.5, -4.0), (3.0, 0.7, 0.5), "lock_steel", rot=(0, 0, -s * 16), pivot=(s * 3.8, 9.8, -4))
    # keyhole: escutcheon plate, round throat, tumbler teeth
    r.cube(body, (-2.6, 6.2, -3.85), (5.2, 4.4, 0.4), "lock_steel")
    r.cube(body, (-1.7, 6.4, -4.0), (3.4, 3.6, 0.2), "maw")
    r.cube(body, (-0.9, 7.0, -4.05), (1.8, 2.2, 0.2), "lock_throat")
    for x in (-1.5, -0.3, 0.9):
        r.cube(body, (x, 6.0, -4.15), (0.6, 1.0, 0.3), "tooth")
    r.cube(body, (-2.0, 3.4, -3.65), (4.0, 3.0, 0.2), "lock_throat")             # throat glow behind the jaw
    jaw = r.bone("jaw", body, (0, 6.3, -4.0), role="jaw")
    r.cube(jaw, (-2.6, 3.2, -4.25), (5.2, 3.1, 0.5), "lock_steel")
    r.cube(jaw, (-0.8, 3.6, -4.4), (1.6, 2.7, 0.2), "maw")                       # the keyhole slot
    for x in (-1.9, 1.3):
        r.cube(jaw, (x, 5.6, -4.45), (0.6, 0.9, 0.3), "tooth")
    # the shackle: snaps and clamps (lead arm)
    sh = r.bone("shackle", body, (0, 12.2, 0), role="arm_r")
    r.cube(sh, (3.0, 11.8, -1.0), (2.0, 5.4, 2.0), "lock_steel")
    r.cube(sh, (-5.0, 11.8, -1.0), (2.0, 5.4, 2.0), "lock_steel")
    r.cube(sh, (-4.2, 17.0, -1.0), (8.4, 2.0, 2.0), "lock_steel")
    r.cube(sh, (-4.6, 16.4, -1.0), (1.4, 1.4, 2.0), "lock_steel")               # rounded shoulders
    r.cube(sh, (3.2, 16.4, -1.0), (1.4, 1.4, 2.0), "lock_steel")
    r.cube(sh, (-4.6, 13.2, -1.3), (1.2, 0.6, 0.4), "maw")                       # locking notch
    r.cube(sh, (-1.0, 18.8, -0.4), (2.0, 0.3, 0.8), "rust")
    tag = r.bone("tag", sh, (4.0, 16.5, -1.1), role="tail")
    r.cube(tag, (4.9, 13.8, -1.2), (0.3, 3.0, 0.3), "parchment")
    r.cube(tag, (4.6, 11.6, -1.4), (2.4, 2.4, 0.3), "parchment")
    r.cube(tag, (5.2, 12.3, -1.55), (1.2, 1.0, 0.2), "wax")
    kb = r.bone("flank_key", body, (-6, 7, 0))                                    # key jammed in the flank
    r.cube(kb, (-6.6, 6.0, -1.2), (0.6, 2.0, 2.4), "lock_steel")
    r.cube(kb, (-8.2, 6.6, -0.4), (2.0, 0.8, 0.8), "key_brass")
    r.cube(kb, (-10.4, 5.6, -0.4), (2.6, 0.6, 0.8), "key_brass")
    r.cube(kb, (-10.4, 8.2, -0.4), (2.6, 0.6, 0.8), "key_brass")
    r.cube(kb, (-10.4, 5.6, -0.4), (0.6, 3.2, 0.8), "key_brass")
    r.cube(kb, (-8.4, 5.6, -0.4), (0.6, 3.2, 0.8), "key_brass")
    r.cube(body, (5.85, 2.4, -0.7), (0.7, 9.0, 1.4), "chain")                    # chain down the left flank
    r.cube(body, (5.6, 1.4, -1.0), (1.2, 1.2, 2.0), "old_iron")
    r.cube(body, (2.8, 3.7, -3.9), (2.2, 2.2, 0.4), "wax")                       # wax seal
    r.cube(body, (3.4, 4.3, -4.05), (1.0, 1.0, 0.2), "cloth_red")
    r.cube(body, (-5.2, 5.0, -3.6), (2.0, 0.3, 0.2), "rust", rot=(0, 0, 30), pivot=(-4.2, 5.2, -3.6))
    r.cube(body, (-4.8, 4.4, -3.6), (1.6, 0.3, 0.2), "rust", rot=(0, 0, 30), pivot=(-4.0, 4.6, -3.6))
    return r


def dungeon_rat():
    """A mangy dungeon rat: patchy fur with bald scarred flanks, a glowing red eye and a milky scarred one,
    yellow incisors, a torn ear, bristling spine, pink clawed paws, whiskers and a ringed tail curled at
    its side with the rusty cuff it slipped out of."""
    r = Rig("dungeon_rat")
    Z = 1.6   # whole rat shifted back so the nose and the tail stay inside a small footprint
    body = r.bone("body", None, (0, 4.5, Z), role="body")
    r.cube(body, (-2.4, 2.6, -3.6 + Z), (4.8, 3.8, 6.0), "rat_fur")
    r.cube(body, (-2.8, 2.4, 0.8 + Z), (5.6, 4.4, 4.2), "rat_fur")              # heavy haunches
    r.cube(body, (-2.0, 2.2, -3.0 + Z), (4.0, 0.5, 7.0), "rat_belly")
    for z, h in ((-2.4, 0.7), (-0.6, 1.0), (1.2, 0.8), (2.8, 0.6)):              # bristling spine
        r.cube(body, (-0.4, 6.4 if z < 0.8 else 6.8, z + Z), (0.8, h, 0.9), "fur_black")
    r.cube(body, (2.55, 3.6, -1.6 + Z), (0.4, 1.8, 2.6), "rat_skin")            # mange patch
    r.cube(body, (2.65, 4.0, -1.2 + Z), (0.4, 0.3, 1.8), "scar")
    r.cube(body, (-3.05, 3.8, 1.6 + Z), (0.4, 1.6, 2.0), "rat_skin")
    r.cube(body, (-3.15, 4.6, 1.8 + Z), (0.4, 0.3, 1.6), "scar")
    head = r.bone("head", body, (0, 5, -3.4 + Z), role="head")
    r.cube(head, (-2.0, 3.0, -7.0 + Z), (4.0, 3.4, 4.0), "rat_fur")
    r.cube(head, (-1.3, 3.0, -9.2 + Z), (2.6, 2.3, 2.4), "rat_fur")             # snout
    r.cube(head, (-0.6, 4.4, -9.6 + Z), (1.2, 0.9, 0.6), "rat_nose")
    r.cube(head, (1.7, 4.6, -6.6 + Z), (0.5, 0.9, 1.0), "rat_eye")              # beady glowing eye
    r.cube(head, (-2.2, 4.6, -6.6 + Z), (0.5, 0.9, 1.0), "eye_white")           # milky blind eye
    r.cube(head, (-2.3, 3.8, -6.2 + Z), (0.3, 2.4, 0.4), "scar", rot=(0, 0, 20), pivot=(-2.2, 5, -6 + Z))
    r.cube(head, (1.0, 6.2, -5.0 + Z), (2.0, 2.0, 0.5), "rat_skin")             # whole ear
    r.cube(head, (1.4, 6.5, -5.15 + Z), (1.2, 1.3, 0.2), "rat_nose")
    r.cube(head, (-2.6, 6.2, -5.0 + Z), (1.6, 1.2, 0.5), "rat_skin")            # torn ear
    r.cube(head, (-2.2, 6.2, -5.15 + Z), (0.8, 0.8, 0.2), "rat_nose")
    r.cube(head, (-0.6, 2.3, -9.1 + Z), (1.2, 0.9, 0.3), "rat_tooth")           # upper incisors
    for s in (1, -1):                                                            # whiskers
        for y, a in ((4.0, 12), (3.5, -10)):
            r.cube(head, (s * 1.3 - (2.6 if s < 0 else 0), y, -8.4 + Z), (2.6, 0.15, 0.15), "eye_white",
                   rot=(0, s * a, 0), pivot=(s * 1.3, y, -8.4 + Z))
    jaw = r.bone("jaw", head, (0, 3.2, -6.2 + Z), role="jaw")
    r.cube(jaw, (-1.1, 2.3, -8.6 + Z), (2.2, 0.9, 2.8), "rat_fur")
    r.cube(jaw, (-0.5, 2.9, -8.75 + Z), (1.0, 0.7, 0.3), "rat_tooth")
    for side, s in (("l", 1), ("r", -1)):
        for z, back in ((-2.6 + Z, False), (2.6 + Z, True)):
            leg = r.bone(f"leg_{side}_{'b' if back else 'f'}", None, (s * 1.8, 3.6, z), role=f"leg_{side}")
            if back:
                r.cube(leg, (s * 1.8 - 0.9, 1.0, z - 1.2), (1.8, 3.0, 2.4), "rat_fur")
                r.cube(leg, (s * 1.8 - 0.8, 0, z - 2.0), (1.6, 0.7, 2.8), "rat_skin")
            else:
                r.cube(leg, (s * 1.8 - 0.7, 0.4, z - 0.7), (1.4, 3.4, 1.4), "rat_fur")
                r.cube(leg, (s * 1.8 - 0.8, 0, z - 1.4), (1.6, 0.6, 2.0), "rat_skin")
            for dx in (-0.5, 0.2):                                                 # claws
                r.cube(leg, (s * 1.8 + dx, 0, z - (2.4 if back else 1.8)), (0.3, 0.3, 0.5), "tooth")
    # ringed tail: droops from the rump, runs back, then curls round to the side
    t0 = r.bone("tail0", body, (0, 3.9, 5.0 + Z), role="tail")
    r.cube(t0, (-0.5, 3.1, 5.0 + Z - 0.2), (1.0, 1.0, 3.4), "rat_skin", rot=(-12, 0, 0))
    r.cube(t0, (-0.55, 3.05, 6.6 + Z), (1.1, 1.1, 0.25), "rat_nose", rot=(-12, 0, 0), pivot=(0, 3.9, 5.0 + Z))
    zz = 8.0 + Z
    t1 = r.bone("tail1", t0, (0, 3.1, zz), role="tail")
    r.cube(t1, (-0.35, 2.75, zz - 0.4), (3.6, 0.7, 0.7), "rat_skin", rot=(0, 30, 0))
    r.cube(t1, (1.4, 2.7, zz - 0.45), (0.25, 0.8, 0.8), "rat_nose", rot=(0, 30, 0), pivot=(0, 3.1, zz))
    x2, z2 = 2.9, zz - 1.8
    t2 = r.bone("tail2", t1, (x2, 3.0, z2), role="tail")
    r.cube(t2, (x2 - 0.25, 2.75, z2 - 5.0), (0.5, 0.5, 5.2), "rat_skin", rot=(0, 12, 0))
    for k in (1.4, 3.0):
        r.cube(t2, (x2 - 0.3, 2.7, z2 - k), (0.6, 0.6, 0.2), "rat_nose", rot=(0, 12, 0), pivot=(x2, 3.0, z2))
    r.cube(t2, (x2 - 0.55, 2.45, z2 - 2.4), (1.1, 1.1, 0.5), "rust", rot=(0, 12, 0), pivot=(x2, 3.0, z2))
    return r


def executioner():
    """The headsman: a hulking bare-chested brute in a black pointed hood with burning eye holes and a
    grimacing stubbled chin, stained leather apron, bandaged gut and scars, one spiked pauldron, a broad
    notched axe as tall as a man, and a manacle chain dragging from his other fist."""
    r = Rig("executioner")
    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 3, 11, 0), role=f"leg_{side}")
        r.cube(leg, (s * 3 - 2, 3.4, -2), (4, 8.2, 4), "exe_pants")
        r.cube(leg, (s * 3 - 2.4, 0, -2.8), (4.8, 4, 5), "leather")
        r.cube(leg, (s * 3 - 2.5, 0, -3.3), (5, 1.6, 1.2), "old_iron")            # toecap
    body = r.bone("body", None, (0, 12, 0), role="body")
    r.cube(body, (-6, 10.4, -3.6), (12, 3.2, 7.2), "leather")                    # belt
    r.cube(body, (-1.6, 10.2, -4.1), (3.2, 3.0, 0.6), "old_iron")                # buckle
    r.cube(body, (-6.4, 13.2, -4.0), (12.8, 9.0, 8.0), "exe_skin")               # torso
    r.cube(body, (-5.0, 12.8, -4.6), (10.0, 4.4, 1.0), "exe_skin")               # gut
    r.cube(body, (-5.2, 14.0, -4.75), (10.4, 1.6, 1.0), "bandage")               # bandage wrap
    r.cube(body, (-5.4, 18.2, -4.5), (10.8, 3.4, 0.8), "exe_skin")               # pecs
    r.cube(body, (-0.1, 18.2, -4.6), (0.2, 3.0, 0.2), "maw")
    r.cube(body, (1.6, 17.0, -4.75), (0.3, 3.6, 0.3), "scar", rot=(0, 0, 35), pivot=(1.6, 19, -4.7))
    r.cube(body, (-3.6, 15.8, -4.85), (2.6, 0.3, 0.3), "scar")
    r.cube(body, (-4.0, 21.4, -2.4), (8.0, 2.6, 5.2), "exe_skin")                # bull neck
    r.cube(body, (-6.6, 20.4, -4.6), (13.2, 2.8, 9.2), "exe_hood")               # hood mantle
    r.cube(body, (-5.6, 14.0, 3.8), (11.2, 7.0, 1.2), "exe_hood")
    r.cube(body, (-3.4, 17.6, -5.0), (6.8, 3.0, 0.6), "exe_hood")                # bib point
    r.cube(body, (-4.4, 3.6, -4.9), (8.8, 9.6, 0.6), "exe_apron")                # stained apron
    r.cube(body, (-1.2, 6.0, -5.05), (2.0, 1.8, 0.2), "maw")
    r.cube(body, (1.6, 8.6, -5.05), (1.2, 1.0, 0.2), "maw")
    r.cube(body, (-4.4, 3.4, -5.0), (8.8, 0.6, 0.7), "leather")
    r.cube(body, (5.2, 19.6, -3.4), (4.4, 3.4, 6.8), "old_iron")                 # spiked pauldron, left only
    for z in (-2.0, 1.2):
        r.cube(body, (6.8, 23.0, z), (0.9, 1.8, 0.9), "lock_steel")
    r.cube(body, (5.6, 19.0, -3.6), (3.6, 0.8, 7.2), "leather")
    head = r.bone("head", body, (0, 23, -1.2), role="head")
    r.cube(head, (-3.6, 22.6, -5.4), (7.2, 7.4, 7.0), "exe_hood")
    r.cube(head, (-2.6, 29.4, -4.0), (5.2, 1.8, 5.2), "exe_hood", rot=(-8, 0, 0), pivot=(0, 29.4, -1))
    r.cube(head, (-1.4, 30.8, -2.4), (2.8, 1.8, 2.8), "exe_hood", rot=(-16, 0, 0), pivot=(0, 30.8, -1))
    r.cube(head, (-0.15, 23.0, -5.55), (0.3, 7.0, 0.2), "cloth_grey")            # rough stitched seam
    r.cube(head, (-2.8, 25.8, -5.6), (2.2, 1.6, 0.3), "maw")                     # eye holes
    r.cube(head, (0.6, 25.6, -5.6), (2.4, 2.0, 0.3), "maw")
    r.cube(head, (-2.2, 26.2, -5.75), (1.0, 0.8, 0.2), "exe_eye")
    r.cube(head, (1.3, 26.2, -5.75), (1.0, 1.0, 0.2), "exe_eye")
    jaw = r.bone("jaw", head, (0, 23.4, -3.5), role="jaw")
    r.cube(jaw, (-2.2, 21.8, -6.0), (4.4, 2.0, 2.6), "stubble")                  # chin out of the mouth hole
    for x in (-1.4, -0.3, 0.8):
        r.cube(jaw, (x, 23.4, -6.15), (0.6, 0.6, 0.3), "tooth")
    for side, s in (("l", 1), ("r", -1)):
        cx = s * 8.2
        arm = r.bone(f"arm_{side}", body, (cx, 21.4, 0), role=f"arm_{side}")
        r.cube(arm, (cx - 2.2, 14.0, -2.2), (4.4, 8.6, 4.4), "exe_skin")
        r.cube(arm, (cx - 2.5, 9.0, -2.5), (5.0, 5.4, 5.0), "leather")            # bracer
        r.cube(arm, (cx - 0.5, 11.0, -2.85), (1.0, 1.0, 0.5), "old_iron")         # stud
        r.cube(arm, (cx - 2.2, 6.0, -2.3), (4.4, 3.4, 4.6), "exe_pants")          # glove
        r.cube(arm, (cx - 2.3, 6.8, -2.6), (4.6, 0.8, 0.5), "old_iron")           # knuckle bar
    r.cube("arm_r", (-10.45, 16.0, -0.8), (0.3, 3.0, 0.3), "scar")
    # the broad axe, upright in the right fist, blade turned out to the front quarter
    axe = r.bone("axe", "arm_r", (-8.2, 7.6, 0), rot=(0, 25, 0))
    r.cube(axe, (-8.9, 1.0, -0.7), (1.4, 26.0, 1.4), "wood_dark")
    r.cube(axe, (-9.2, 5.0, -1.0), (2.0, 5.0, 2.0), "leather")                   # grip wrap
    r.cube(axe, (-9.3, 0.4, -1.1), (2.2, 1.2, 2.2), "old_iron")                  # pommel
    r.cube(axe, (-9.5, 18.4, -1.3), (2.6, 7.6, 2.6), "old_iron")                 # socket
    r.cube(axe, (-9.7, 21.4, -0.5), (3.0, 0.8, 0.8), "lock_steel")               # rivet
    r.cube(axe, (-8.7, 17.6, -7.6), (1.0, 9.0, 6.4), "exe_blade")                # cheek of the blade
    r.cube(axe, (-8.7, 16.0, -9.0), (1.0, 12.0, 1.6), "exe_edge")                # bright edge
    r.cube(axe, (-8.7, 15.4, -7.6), (1.0, 2.4, 3.0), "exe_blade")                # bearded lower horn
    r.cube(axe, (-8.7, 26.4, -7.8), (1.0, 1.6, 3.2), "exe_blade")                # upper horn
    r.cube(axe, (-8.8, 21.0, -9.1), (1.2, 0.8, 0.6), "maw")                      # notch in the edge
    r.cube(axe, (-8.6, 21.6, -6.0), (1.2, 2.2, 2.2), "rust")
    r.cube(axe, (-8.7, 20.6, 1.2), (1.0, 2.0, 3.0), "old_iron")                  # back spike
    ch = r.bone("drag_chain", "arm_l", (8.2, 6.2, 0), role="tail")
    y = chain(r, ch, 8.2, 6.4, 0, 3)
    shackle(r, ch, 8.2, y - 0.8, 0, s=3.0)
    r.cube(ch, (7.4, y - 1.2, -1.6), (1.6, 1.0, 0.6), "lock_brass")              # its lock
    return r
