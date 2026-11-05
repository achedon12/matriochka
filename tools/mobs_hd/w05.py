"""World 5, Lightless Deep: total darkness, things that hunt by sound and eat light.

Everything here is near-black, so each creature is read through value contrast (a paler belly or mask against
the dark hide) and a few emissive accents: sonar teal for the sound hunters, amber for swallowed light,
violet for the brood. Structural parts are axis-aligned (stepped), so the model looks the same in game
as in the preview; rotated cubes are only used where the sign of the tilt does not matter.
"""
from common import Rig, mat

# --- shared deep materials
mat("deep_claw", "c8ccd6", "ffffff", "skin")
mat("sonar", "2ee0cc", "c8fff4", "glow", True)
mat("sonar_dim", "0e3a3e", "2ee0cc", "spots")          # freckles of sculk that catch a few pixels of glow

# --- Blind Prowler
mat("prowler_hide", "1b1d28", "343c56", "fur")
mat("prowler_belly", "3a3c4e", "5a5e78", "skin")
mat("prowler_plate", "2c3246", "6a7a9c", "chitin")
mat("prowler_ear", "3a2c46", "8a6aa0", "membrane")
mat("prowler_visor", "626882", "9aa0b8", "skin")
mat("prowler_gum", "3a0e1e", "a03a5a", "flesh")


def _claws(r, bone, x, z, n, length, y=0.0, mat_="deep_claw", w=0.5):
    """A row of n claws pointing forward (-Z) from a paw front at depth z, centred on x."""
    for i in range(n):
        cx = x + (i - (n - 1) / 2) * (w + 0.35)
        r.cube(bone, (cx - w / 2, y, z - length), (w, 0.6, length + 0.3), mat_)


def blind_prowler():
    """An eyeless panther: a smooth plated brow where the eyes should be, huge bat ears ribbed with sonar,
    a glowing sonar crest down the skull and spine, whiskers, long white claws and a rattle on the tail."""
    r = Rig("blind_prowler")
    r.bone("body", None, (0, 12, 0), role="body")
    r.cube("body", (-4, 8.5, -7.5), (8, 7, 7.5), "prowler_hide")           # deep chest
    r.cube("body", (-3.5, 9, -0.5), (7, 6, 7.5), "prowler_hide")           # lean hindquarters
    r.cube("body", (-4.5, 12.5, -7), (9, 3, 5), "prowler_hide")            # shoulder blades
    r.cube("body", (-3, 8, -6.5), (6, 1.2, 12), "prowler_belly")           # pale belly
    for s in (1, -1):                                                      # ribs showing through the hide
        for i, z in enumerate((-5.6, -4.0, -2.4)):
            r.cube("body", (s * 4.02 - 0.12, 9.6 + i * 0.2, z), (0.24, 4.2 - i * 0.5, 0.6), "prowler_plate")
    r.cube("body", (3.7, 10.2, 1.0), (0.4, 2.0, 3.0), "sonar_dim")         # sculk creeping over one flank
    r.cube("body", (3.75, 11.6, 3.2), (0.4, 1.6, 1.6), "sonar_dim")
    r.cube("body", (3.8, 10.6, 1.6), (0.3, 0.6, 0.6), "sonar")
    r.cube("body", (-3.9, 11.5, 2.5), (0.4, 1.2, 1.5), "sonar_dim")
    for i in range(6):                                                     # sonar fins down the spine
        z, h = -6.2 + i * 2.3, 2.0 - i * 0.25
        r.cube("body", (-0.5, 15.2, z), (1, h, 1.4), "prowler_plate")
        r.cube("body", (-0.25, 15.2 + h, z + 0.2), (0.5, 0.35, 1), "sonar")
    # head
    r.bone("head", "body", (0, 14, -7), role="head")
    r.cube("head", (-2, 11.8, -9.5), (4, 4.2, 3.5), "prowler_hide")        # neck
    r.cube("head", (-3, 12.2, -13.2), (6, 4.6, 5), "prowler_hide")         # skull
    r.cube("head", (-2.1, 12.2, -16.2), (4.2, 2.4, 3.2), "prowler_hide")   # muzzle
    r.cube("head", (-0.8, 13.9, -16.3), (1.6, 0.8, 0.4), "prowler_plate")  # nose pad
    r.cube("head", (-1.6, 14.9, -15.4), (3.2, 0.6, 2.4), "prowler_plate")  # bridge of the nose
    r.cube("head", (-3.2, 14.6, -13.7), (6.4, 1.8, 4.6), "prowler_visor")  # smooth blind visor where eyes should be
    for s in (1, -1):
        r.cube("head", (s * 1.6 - 0.15, 14.8, -13.85), (0.3, 1.4, 0.2), "prowler_plate")  # scar seams on the visor
        r.cube("head", (s * 0.55 - 0.25, 13.6, -16.32), (0.5, 0.35, 0.15), "pupil")          # flared nostrils
        r.cube("head", ((2.1 if s > 0 else -4.9), 13.5, -15.6), (2.8, 0.15, 0.15), "deep_claw")   # whiskers
        r.cube("head", ((2.1 if s > 0 else -4.6), 13.0, -15.2), (2.5, 0.15, 0.15), "deep_claw")
        r.cube("head", (s * 3.02 - 0.12, 12.8, -12.6), (0.24, 2.2, 0.4), "sonar_dim")       # cheek pits
    for i, (z, h) in enumerate(((-15.2, 0.5), (-13.4, 0.9), (-11.8, 1.4), (-10.2, 1.1))):   # sonar crest on the skull
        y = 15.5 if i == 0 else 16.4
        r.cube("head", (-0.35, y, z), (0.7, h, 1.1), "prowler_plate")
        r.cube("head", (-0.2, y + h, z + 0.15), (0.4, 0.3, 0.8), "sonar")
    for k, x in enumerate((-1.8, -1.0, 0.6, 1.4)):                         # upper teeth, fangs at the corners
        fang = k in (0, 3)
        r.cube("head", (x, 11.2 if fang else 11.7, -16.1), (0.4, 1.0 if fang else 0.5, 0.4), "tooth")
    for s, side in ((1, "l"), (-1, "r")):                                  # the huge ears, swept out like dishes
        e = r.bone(f"ear_{side}", "head", (s * 2.5, 16, -10))
        def ear(x0, y0, w, h):
            xa = s * x0 - (0 if s > 0 else w)
            r.cube(e, (xa, y0, -10.2), (w, h, 0.5), "prowler_plate")
            r.cube(e, (xa + 0.3, y0 + (0.0 if y0 > 16 else 0.3), -10.45), (w - 0.6, h - (0.0 if y0 > 16 else 0.3), 0.25), "prowler_ear")
        ear(2.2, 15.8, 3.4, 2.6)
        ear(2.9, 18.4, 3.4, 2.2)
        ear(3.8, 20.6, 2.4, 1.2)
        r.cube(e, (s * 5.4 - (0 if s > 0 else 0.8), 21.8, -10.2), (0.8, 0.8, 0.5), "prowler_plate")   # ear tip
        for j, y in enumerate((16.6, 18.3, 20.0)):                         # sonar ribs inside the ear
            w = 2.2 - j * 0.3
            r.cube(e, (s * (2.8 + j * 0.5) - (0 if s > 0 else w), y, -10.55), (w, 0.3, 0.15), "sonar")
    j = r.bone("jaw", "head", (0, 12.4, -12), role="jaw")
    r.cube(j, (-1.9, 10.9, -16), (3.8, 1.4, 4.5), "prowler_hide")
    r.cube(j, (-1.5, 12.1, -15.8), (3.0, 0.3, 3.8), "prowler_gum")
    for x in (-1.4, -0.4, 0.4, 1.0):
        r.cube(j, (x, 12.2, -15.9), (0.4, 0.6 if x in (-0.4, 0.4) else 0.8, 0.4), "tooth")
    r.cube(j, (-0.2, 10.0, -15.4), (0.4, 0.9, 0.4), "sonar")               # a drip of glowing saliva               # a drip of glowing saliva
    # front legs (they swipe: arm roles)
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 3, 12, -5.5), role=f"arm_{side}")
        r.cube(a, (s * 3 - 1.6, 9.5, -7.2), (3.2, 4, 3.4), "prowler_plate")    # shoulder plate
        r.cube(a, (s * 3 - 1.3, 5, -6.8), (2.6, 6, 2.8), "prowler_hide")
        r.cube(a, (s * 3 - 1.1, 1, -6.5), (2.2, 4.5, 2.2), "prowler_hide")
        r.cube(a, (s * 3 - 1.5, 0, -8), (3, 1.4, 3.6), "prowler_hide")         # paw
        _claws(r, a, s * 3, -8, 3, 3.2)
        r.cube(a, (s * 3 - 0.25, 2.6, -4.6), (0.5, 0.5, 1.4), "deep_claw")     # dewclaw
    # hind legs, digitigrade
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 3, 11, 4), role=f"leg_{side}")
        r.cube(l, (s * 3 - 1.6, 6, 2), (3.2, 6, 4.5), "prowler_hide")          # thigh
        r.cube(l, (s * 3 - 1.1, 1, 4.6), (2.2, 6, 2), "prowler_hide")          # hock
        r.cube(l, (s * 3 - 1.4, 0, 2.6), (2.8, 1.3, 3.6), "prowler_hide")
        _claws(r, l, s * 3, 2.6, 3, 1.2, w=0.45)
    # tail with a sonar rattle
    t = r.bone("tail", "body", (0, 13.5, 6.5), role="tail")
    r.cube(t, (-1, 12.5, 6.5), (2, 2, 5), "prowler_hide")
    t2 = r.bone("tail2", t, (0, 13.5, 11), role="tail")
    r.cube(t2, (-0.8, 12.7, 11), (1.6, 1.6, 5), "prowler_hide")
    for k in range(3):
        r.cube(t2, (-1.1, 12.4, 15.2 + k * 1.1), (2.2, 2.2, 0.6), "prowler_plate")
        r.cube(t2, (-0.6, 12.9, 15.0 + k * 1.1), (1.2, 1.2, 1.0), "sonar")
    return r


# --- Glow Devourer
mat("devourer_skin", "1c1628", "3e2e58", "membrane")
mat("devourer_foot", "100c18", "2a2038", "skin")
mat("devourer_thin", "c8862e", "ffe08a", "vein")      # stretched skin with swallowed light glowing through
mat("devourer_lip", "3a1a2e", "7a3a5a", "flesh")
mat("gut_glow", "ffb83a", "ffd870", "glow", True)
mat("torch_wood", "6a4a2a", "8a6438", "bark")
mat("charred", "1a1614", "3a3230", "metal")


def glow_devourer():
    """A crawling blob that is mostly mouth: its belly skin is stretched so thin the stolen light shows through,
    with the silhouettes of a swallowed lantern and torch inside. Snuffed torches stick out of its back,
    small gold eyes sit over a maw of needle teeth, and two sucker tendrils reach for your light."""
    r = Rig("glow_devourer")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-6, 4.5, -5.5), (12, 6, 11.5), "devourer_skin")        # upper mass (lip, back)
    r.cube("body", (-6.4, 1, -1), (12.8, 4.5, 7.4), "devourer_skin")       # sagging rear belly
    r.cube("body", (-6.8, 2.5, -3.5), (13.6, 6, 8.5), "devourer_skin")     # bulging flanks
    r.cube("body", (-5, 10.5, -4.5), (10, 1.5, 9.5), "devourer_skin")      # dome
    r.cube("body", (-3.5, 12, -3), (7, 0.8, 6.5), "devourer_skin")
    r.cube("body", (-4.5, 3, 5.8), (9, 6, 1), "devourer_skin")             # rear bulge
    r.cube("body", (-7.2, 0, -2), (14.4, 1.2, 9.4), "devourer_foot")       # flattened crawling skirt
    for (x, z) in ((-7.4, 0.5), (6.6, 3.5), (-1, 7.2)):                    # skirt lobes
        r.cube("body", (x, 0, z), (0.8, 0.8, 2), "devourer_foot")
    # windows of thin skin, swallowed light glowing through
    r.cube("body", (6.65, 3.2, -2.5), (0.3, 4.8, 6), "devourer_thin")      # right flank
    r.cube("body", (-6.95, 3.5, -1), (0.3, 4, 4.2), "devourer_thin")       # left flank, smaller
    r.cube("body", (-3.2, 4, 6.65), (6.4, 4.4, 0.3), "devourer_thin")      # rump
    r.cube("body", (-2.2, 12.65, -1.8), (4.4, 0.3, 3.6), "devourer_thin")  # crown of the dome
    # silhouettes of what it ate, pressed against the thin skin
    r.cube("body", (6.9, 3.8, -0.4), (0.2, 3, 2.4), "charred")             # a lantern inside the right flank
    r.cube("body", (6.9, 6.8, 0.2), (0.2, 0.6, 1.2), "charred")
    r.cube("body", (6.95, 4.4, 0.2), (0.2, 1.8, 1.2), "gut_glow")
    r.cube("body", (6.9, 4.0, 3.0), (0.2, 1.2, 1.2), "charred")            # a half-digested torch head
    r.cube("body", (-1.6, 4.3, 6.9), (0.6, 3.6, 0.2), "charred")           # a torch stick inside the rump
    r.cube("body", (-1.8, 7.6, 6.95), (1, 0.8, 0.2), "gut_glow")
    r.cube("body", (0.9, 4.6, 6.9), (1.5, 1.5, 0.2), "charred")            # a glowstone, half dissolved
    r.cube("body", (-6.95, 4.4, 0.4), (0.2, 1.6, 1.6), "charred")
    for (x, y, z) in ((3.6, 10, 5.5), (-4.6, 8.4, 4.6), (5.6, 8.6, -4.6)):   # light blisters pushing out
        r.cube("body", (x, y, z), (1.2, 1.2, 1.2), "gut_glow")
    # snuffed torches stuck in its back
    for (x, z, h) in ((2.5, 1.5, 3.2), (-3, 0, 2.4)):
        r.cube("body", (x, 12.0, z), (0.7, h, 0.7), "torch_wood")
        r.cube("body", (x - 0.05, 12.0 + h, z - 0.05), (0.8, 0.6, 0.8), "charred")
    r.cube("body", (-3.2, 15.2, -0.2), (0.3, 0.6, 0.3), "smoke")           # last curl of soot
    # eyes over the maw: two main, three small, a little asymmetric
    for (x, y, sz) in ((-4.0, 8.6, 1.8), (2.0, 8.8, 1.8), (-1.0, 10.0, 0.8), (0.4, 10.3, 0.6), (4.6, 7.6, 0.7)):
        r.cube("body", (x - 0.3, y - 0.3, -5.62), (sz + 0.6, sz + 0.6, 0.2), "pupil")    # sunken socket
        r.cube("body", (x, y, -5.75), (sz, sz, 0.3), "eye_gold")
        r.cube("body", (x + sz / 2 - 0.15, y + 0.1, -5.85), (0.3, sz - 0.2, 0.2), "pupil")   # slit pupil
    r.cube("body", (-4.5, 10.6, -5.9), (2.8, 0.5, 0.5), "devourer_lip")    # heavy lids
    r.cube("body", (1.5, 10.8, -5.9), (2.8, 0.5, 0.5), "devourer_lip")
    # upper lip and needle teeth
    r.cube("body", (-6.2, 4.2, -6), (12.4, 1.3, 1), "devourer_lip")
    for k in range(10):
        x = -5.3 + k * 1.15
        r.cube("body", (x, 3.0 if k % 3 else 2.4, -5.8), (0.5, 1.4 if k % 3 else 2.0, 0.5), "tooth")
    r.cube("body", (-5, 2, -0.8), (10, 2.6, 0.3), "gut_glow")              # the throat, lit by stolen light
    r.cube("body", (-5.2, 1.4, -5.2), (10.4, 0.5, 4.4), "maw")             # dark mouth floor
    j = r.bone("jaw", "body", (0, 3, -0.5), role="jaw")
    r.cube(j, (-6, 0.2, -6.5), (12, 2.2, 6), "devourer_skin")
    r.cube(j, (-6.2, 1.8, -6.8), (12.4, 0.9, 1), "devourer_lip")
    for k in range(9):
        r.cube(j, (-4.8 + k * 1.15, 2.4, -6.5), (0.45, 0.9 if k % 2 else 1.3, 0.45), "tooth")
    r.cube(j, (-1.5, 2.1, -5), (3, 0.5, 4.5), "devourer_lip")              # tongue
    r.cube(j, (-2.3, -0.0, -6.6), (0.4, 0.8, 0.4), "ink")                  # ink drips off the chin
    r.cube(j, (1.6, 0.0, -6.4), (0.4, 0.5, 0.4), "ink")
    # sucker tendrils that reach for your light
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 6.6, 7, -4), role=f"arm_{side}")
        o = 0 if s > 0 else -1
        r.cube(a, (s * 6.4 + o * 2, 4, -5), (2, 3.6, 2), "devourer_skin")
        r.cube(a, (s * 6.8 + o * 1.6, 1.6, -5.4), (1.6, 2.8, 1.6), "devourer_skin")
        r.cube(a, (s * 6.8 + o * 1.6, 0.4, -7.2), (1.6, 1.4, 3.2), "devourer_skin")     # tip curling forward
        r.cube(a, (s * 7.0 + o * 1.2, 0.3, -7.6), (1.2, 0.3, 2.4), "gut_glow")          # glowing suckers underneath
        r.cube(a, (s * 7.0 + o * 1.2, 1.8, -7.5), (1.2, 0.3, 0.3), "devourer_lip")
        for k in range(3):                                                               # suckers along the inside
            r.cube(a, (s * 6.75 + o * 0.3, 2.2 + k * 1.3, -5.5 if k == 0 else -5.3), (0.3, 0.6, 0.6), "gut_glow")
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 3.5, 2, 2.5), role=f"leg_{side}")
        r.cube(l, (s * 3.5 - 2, 0, 0.5), (4, 1.8, 4.5), "devourer_foot")
    return r


# --- Echo
mat("echo_mist", "6c8ca2", "d0f0ff", "cloud")
mat("echo_deep", "121a26", "2a3a52", "cloud")
mat("echo_face", "b8d4e2", "e8f8ff", "cloud")
mat("echo_glow", "6ad8f8", "b0f0ff", "glow", True)


def _arc_ring(r, bone, cy, radius, mat_, th=0.4, seg=8, gap=0.62):
    """A broken octagonal ring (arcs with gaps) around the bone's vertical axis: a sound wave."""
    w = 2 * radius * 0.414 * gap
    for k in range(seg):
        r.cube(bone, (-w / 2, cy - th / 2, -radius - th / 2), (w, th, th), mat_,
               rot=[0, k * 360 / seg, 0], pivot=(0, cy, 0))


def echo():
    """A hollow weeping ghost: a hood over a black face with downturned glowing eyes and long tear trails, hands
    raised to its cheeks, a mouth open on a borrowed cry, a hole right through its chest where a little sound
    heart floats, a body that frays into a wisp, and broken rings of sound around it."""
    r = Rig("echo")
    r.bone("body", None, (0, 14, 0), role="body")
    r.cube("body", (-4.2, 15, -2.2), (8.4, 3.5, 4.4), "echo_mist")         # hunched shoulders
    r.cube("body", (-3.2, 18.5, -1.8), (6.4, 1, 3.6), "echo_mist")
    r.cube("body", (-4, 9, -2), (1.6, 6, 4), "echo_mist")                  # hollow chest: left wall
    r.cube("body", (2.4, 9, -2), (1.6, 6, 4), "echo_mist")                 # right wall
    r.cube("body", (-4, 7.8, -2), (8, 1.4, 4), "echo_mist")                # bottom of the hole
    r.cube("body", (-2.4, 9.2, -1.6), (0.3, 5.8, 3.2), "echo_glow")        # glowing inner lining of the hole
    r.cube("body", (2.1, 9.2, -1.6), (0.3, 5.8, 3.2), "echo_glow")
    r.cube("body", (-2.4, 9.15, -1.6), (4.8, 0.3, 3.2), "echo_glow")
    for (x, y, w, hh) in ((-2.4, 13.6, 0.7, 1.4), (1.7, 9.2, 0.7, 1.2), (-0.8, 14.4, 1.6, 0.6), (-2.4, 9.2, 0.6, 0.6)):
        r.cube("body", (x, y, -2.1), (w, hh, 0.6), "echo_mist")            # ragged edges of the hole
    h = r.bone("heart", "body", (0, 12, 0), role="orbit")                  # the sound heart floating inside
    r.cube(h, (-0.8, 11.2, -0.8), (1.6, 1.6, 1.6), "echo_glow", rot=[45, 0, 45], pivot=(0, 12, 0))
    r.cube(h, (-0.4, 11.6, -0.4), (0.8, 0.8, 0.8), "pearl")
    # fraying wisp body
    t = r.bone("wisp", "body", (0, 8, 0), role="tail")
    r.cube(t, (-3.4, 4.5, -1.8), (6.8, 4, 3.6), "echo_mist")
    t2 = r.bone("wisp2", t, (0.4, 5, 0.3), role="tail")
    r.cube(t2, (-1.8, 2.2, -1.0), (4.6, 3.2, 2.6), "echo_mist")
    t3 = r.bone("wisp3", t2, (1.2, 2.5, 0.8), role="tail")
    r.cube(t3, (-0.4, 0.8, -0.2), (2.6, 2.2, 1.8), "echo_mist")
    r.cube(t3, (1.4, 0.2, 0.4), (1.6, 1.2, 1.2), "echo_mist")              # the wisp curls away
    r.cube(t3, (2.6, 0, 0.6), (0.8, 0.8, 0.8), "echo_glow")
    for (x, y, h_) in ((-3.6, 2.2, 2.6), (2.9, 1.2, 3.6), (-1.0, 0.8, 1.4)):    # trailing strands
        r.cube(t, (x, y, -0.6), (0.6, h_, 0.6), "echo_mist")
    # head, crying
    r.bone("head", "body", (0, 19, 0), role="head")
    r.cube("head", (-3.2, 19, -3), (6.4, 5.8, 5.8), "echo_mist")           # hood
    r.cube("head", (-2.4, 24.8, -2.4), (4.8, 0.8, 4.4), "echo_mist")
    r.cube("head", (-1.2, 23.6, 2.6), (2.4, 2, 1.4), "echo_mist")          # hood tip falling back
    r.cube("head", (-1.2, 25.6, -1.4), (2.4, 0.5, 2.4), "echo_mist")
    r.cube("head", (-2.7, 19.2, -3.15), (5.4, 5.2, 0.2), "echo_deep")      # shadow inside the hood
    r.cube("head", (-2.1, 19.4, -3.3), (4.2, 4.5, 0.2), "echo_face")       # pale, sunken face
    r.cube("head", (-1.5, 19.0, -3.25), (3.0, 0.5, 0.2), "echo_face")      # long chin
    for s in (1, -1):
        r.cube("head", (s * 1.25 - 0.5, 22.0, -3.42), (1.0, 1.1, 0.15), "echo_deep")      # hollow eye, outer half lower
        r.cube("head", (s * 0.55 - 0.4, 22.5, -3.42), (0.8, 1.0, 0.15), "echo_deep")      # inner half raised: grief
        r.cube("head", (s * 1.0 - 0.15, 22.4, -3.5), (0.3, 0.3, 0.1), "echo_glow")         # a pinpoint of light inside
        r.cube("head", (s * 1.0 - 0.5, 23.6, -3.42), (1.0, 0.3, 0.15), "echo_mist")        # brow, tilted up inside
        r.cube("head", (s * 0.4 - 0.2 + (0.2 if s > 0 else -0.2), 23.75, -3.42), (0.4, 0.3, 0.15), "echo_mist")
        r.cube("head", (s * 1.4 - 0.2, 19.6, -3.45), (0.4, 2.4, 0.15), "soul")             # tear trails
        r.cube("head", (s * 1.4 - 0.2, 18.4 - (0.5 if s > 0 else 0), -3.3), (0.4, 0.5, 0.4), "soul")   # falling tears
    r.cube("head", (-1.55, 17.3, -3.1), (0.35, 0.35, 0.35), "soul")
    r.cube("head", (-0.6, 19.6, -3.75), (1.2, 1.9, 0.45), "echo_deep")      # the open, wailing mouth
    r.cube("head", (-0.3, 19.9, -3.85), (0.6, 0.9, 0.1), "echo_glow")        # the borrowed cry glowing inside
    j = r.bone("jaw", "head", (0, 20.4, -3), role="jaw")
    r.cube(j, (-0.9, 18.9, -3.4), (1.8, 0.6, 0.3), "echo_face")            # chin drops when it cries
    # arms raised, hands pressed to the sides of the hood
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 4.2, 17.5, 0), role=f"arm_{side}")
        r.cube(a, (s * 4.6 - 0.8, 13.6, -1.2), (1.6, 4.4, 1.6), "echo_mist")      # upper arm
        r.cube(a, (s * 4.4 - 0.75, 13.4, -4.2), (1.5, 1.4, 3.4), "echo_mist")     # forearm forward
        r.cube(a, (s * 4.0 - 0.7, 14.3, -4.4), (1.4, 5.4, 1.2), "echo_mist")      # forearm rising
        r.cube(a, (s * 3.7 - 0.75, 19.4, -4.0), (1.5, 2.2, 1.0), "echo_mist")     # palm on the cheek
        for k in range(3):                                                         # thin fingers up the temple
            r.cube(a, (s * (3.3 + k * 0.45) - 0.15, 21.5, -3.9 + k * 0.5), (0.3, 1.9 - k * 0.3, 0.3), "echo_mist")
        r.cube(a, (s * 4.4 - 0.4, 13.2, -4.4), (0.8, 0.3, 0.8), "echo_glow")      # glowing elbow joint
        r.cube(a, (s * 4.6 - 0.3, 10.6, -3.8), (0.6, 2.8, 0.5), "echo_mist")      # sleeve rags trailing down
        r.cube(a, (s * 4.3 - 0.25, 11.4, -2.6), (0.5, 2.0, 0.5), "echo_mist")
    # rings of sound
    for i, (cy, rad) in enumerate(((11, 6.5), (16, 8), (5, 5))):
        o = r.bone(f"ring{i}", "body", (0, cy, 0), role="orbit")
        _arc_ring(r, o, cy, rad, "echo_glow", th=0.35, gap=0.55 + 0.1 * i)
    return r


# --- Eyeless Watcher
mat("watcher_robe", "26222f", "4a4458", "cloth")
mat("watcher_inner", "08080c", "1a1a24", "cloth")
mat("watcher_mask", "e4ded2", "ffffff", "skin")
mat("watcher_mask_sh", "a8a094", "c8c0b4", "skin")
mat("watcher_skin", "7c7688", "a8a2b6", "skin")
mat("watcher_finger", "a8a2b4", "d0cadc", "skin")
mat("w5_wax", "e6dac0", "fff4dc", "skin")
mat("smoke", "3e3e46", "7a7a86", "cloud")


def eyeless_watcher():
    """A tall robed figure in a hood with a smooth porcelain face and no eyes at all, only a crack leaking pale
    light and a stitched mouth that opens on more of it. A crown of snuffed candles drips wax, one still smoking.
    Its sleeves end in grey hands whose fingers hang far too long, and bare grey toes peek under a torn hem."""
    r = Rig("eyeless_watcher")
    r.bone("body", None, (0, 14, 0), role="body")
    r.cube("body", (-3.6, 13.5, -2.4), (7.2, 9, 4.8), "watcher_robe")      # narrow chest
    r.cube("body", (-5, 20.5, -3), (10, 3, 6), "watcher_robe")             # mantle
    r.cube("body", (-4.4, 19.2, -3.2), (8.8, 1.3, 1), "watcher_robe")      # mantle drape in front
    r.cube("body", (-0.6, 13.5, -2.6), (1.2, 7, 0.3), "watcher_inner")     # open seam down the front
    for y in (15, 17, 19):                                                 # iron clasps across the seam
        r.cube("body", (-0.9, y, -2.8), (1.8, 0.5, 0.4), "iron")
    for x, h in ((-3.5, 3), (-1, 4.5), (2.5, 3.5)):                        # mantle tatters on the back
        r.cube("body", (x, 20.5 - h, 2.6), (1.2, h, 0.4), "watcher_robe")
    # robe skirt halves carry the walk
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 2, 14, 0), role=f"leg_{side}")
        x0 = 0 if s > 0 else -4.6
        r.cube(l, (x0 + (0.4 if s > 0 else 0), 6, -2.6), (4.2, 8, 5.2), "watcher_robe")
        r.cube(l, (x0 - (0.5 if s < 0 else 0), 1.5, -3.1), (5.1, 4.6, 6.2), "watcher_robe")   # hem flares out
        r.cube(l, (x0 - (0.5 if s < 0 else 0) + (4.6 if s > 0 else 0), 1.5, -3.1), (0.5, 4.6, 0.4), "watcher_inner")
        for k, (dx, h) in enumerate(((0.3, 1.5), (1.6, 0.8), (3.0, 1.3), (3.9, 0.6))):   # torn hem, uneven
            xx = x0 + (dx if s > 0 else 4.6 - dx - 0.8)
            r.cube(l, (xx, 1.5 - h, -2.6 + (k % 2) * 4.6), (0.8, h, 0.6), "watcher_robe")
        for k in range(3):                                                 # long grey toes
            r.cube(l, (s * (0.9 + k * 0.6) - 0.2, 0, -3.8 + k * 0.2), (0.4, 0.5, 1.4 - k * 0.2), "watcher_skin")
    # head
    r.bone("head", "body", (0, 23.5, -0.5), rot=[0, 0, 12], role="head")   # head cocked to one side, listening
    r.cube("head", (-0.9, 22.8, -1.4), (1.8, 2.2, 1.8), "watcher_skin")    # thin neck
    r.cube("head", (-2.5, 24.6, -3.6), (5, 6, 4.4), "watcher_mask")        # long smooth face
    r.cube("head", (-1.8, 23.8, -3.4), (3.6, 1, 3.6), "watcher_mask")      # narrow chin
    r.cube("head", (-2.4, 28.4, -3.75), (4.8, 0.6, 0.3), "watcher_mask_sh")    # brow ridge over nothing
    for s in (1, -1):
        r.cube("head", (s * 1.4 - 0.6, 27.0, -3.7), (1.2, 1.2, 0.15), "watcher_mask_sh")   # shallow sockets, empty
    r.cube("head", (-0.35, 26.4, -3.95), (0.7, 2.0, 0.4), "watcher_mask")  # nose ridge
    r.cube("head", (0.8, 28.6, -3.82), (0.3, 1.8, 0.15), "soul")           # the crack, leaking light
    r.cube("head", (0.5, 27.6, -3.82), (0.3, 1.1, 0.15), "soul")
    r.cube("head", (0.8, 26.9, -3.82), (0.3, 0.8, 0.15), "soul")
    r.cube("head", (1.1, 29.2, -3.82), (0.8, 0.25, 0.15), "soul")
    r.cube("head", (-1.2, 24.5, -3.45), (2.4, 1.1, 0.2), "soul")           # light behind the mouth
    j = r.bone("jaw", "head", (0, 25.6, -3.2), role="jaw")
    r.cube(j, (-1.5, 24.4, -3.75), (3, 1.2, 0.3), "watcher_mask_sh")
    for x in (-1.1, -0.4, 0.3, 1.0):                                       # stitches across the mouth
        r.cube(j, (x - 0.07, 24.6, -3.85), (0.15, 1.0, 0.12), "pupil")
    r.cube("head", (-3.3, 24, -2.8), (6.6, 7.2, 6.2), "watcher_robe")      # hood
    r.cube("head", (-2.6, 31.2, -2.2), (5.2, 0.8, 5), "watcher_robe")
    r.cube("head", (-3.3, 30.4, -4.2), (6.6, 0.8, 1.4), "watcher_robe")    # brim hanging over the brow
    r.cube("head", (-2.8, 23.5, 3.4), (5.6, 5.5, 1.2), "watcher_robe")     # hood falling down the back
    r.cube("head", (-3.5, 24, -3.1), (0.8, 7.2, 0.5), "watcher_inner")     # hood rim shadow
    r.cube("head", (2.7, 24, -3.1), (0.8, 7.2, 0.5), "watcher_inner")
    # crown of snuffed candles on the hood
    for k, (x, z, h) in enumerate(((-2.2, -1.2, 1.6), (-0.9, -1.8, 2.4), (0.6, -1.6, 1.2), (2.0, -0.9, 2.0), (0.2, 1.0, 1.4))):
        r.cube("head", (x - 0.4, 32, z), (0.8, h, 0.8), "w5_wax")
        r.cube("head", (x - 0.1, 32 + h, z + 0.3), (0.2, 0.4, 0.2), "pupil")      # black wick
        r.cube("head", (x - 0.5, 31.4 - k * 0.2, z - 0.1), (0.3, 1 + k * 0.2, 0.3), "w5_wax")   # wax running down
    r.cube("head", (-0.95, 35.3, -1.6), (0.5, 0.8, 0.5), "smoke")          # the last thread of smoke
    r.cube("head", (-0.7, 36.4, -1.4), (0.4, 0.6, 0.4), "smoke")
    # arms: sleeves, wrists, too-long fingers
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 4.6, 22, 0), role=f"arm_{side}")
        ax = s * 5.4
        r.cube(a, (ax - 1.2, 13, -1.2), (2.4, 10, 2.4), "watcher_robe")
        r.cube(a, (ax - 1.7, 11.4, -1.7), (3.4, 2.2, 3.4), "watcher_robe")            # flared cuff
        r.cube(a, (ax - 1.2, 11.2, -1.2), (2.4, 0.3, 2.4), "watcher_inner")
        r.cube(a, (ax - 1.75, 10.6, -1.0), (0.5, 1, 0.5), "watcher_robe")             # frayed cuff threads
        r.cube(a, (ax - 0.5, 9.4, -0.5), (1.0, 2.2, 1.0), "watcher_skin")             # thin wrist
        r.cube(a, (ax - 1.0, 7.4, -0.9), (2.0, 2.2, 1.6), "watcher_skin")             # palm
        for k in range(4):
            fx = ax - 1.1 + k * 0.62
            ln = (5.0, 6.4, 6.0, 4.4)[k if s > 0 else 3 - k]
            r.cube(a, (fx, 7.6 - ln, -0.55), (0.42, ln, 0.42), "watcher_finger")
            r.cube(a, (fx - 0.06, 7.6 - ln * 0.45, -0.6), (0.54, 0.45, 0.54), "watcher_skin")   # knuckle
            r.cube(a, (fx - 0.06, 7.6 - ln * 0.8, -0.6), (0.54, 0.4, 0.54), "watcher_skin")
            r.cube(a, (fx, 7.6 - ln - 0.6, -0.55), (0.42, 0.6, 0.42), "pupil")                 # black nail
        r.cube(a, (ax - (1.3 if s > 0 else -0.9), 6.0, -1.0), (0.4, 3, 0.4), "watcher_finger")   # thumb
    return r


# --- Shadow Mother
mat("mother_fur", "211a2e", "433860", "fur")
mat("mother_hide", "201a2e", "40365c", "skin")
mat("mother_plate", "2c233c", "6a5a8e", "chitin")
mat("brood_sac", "8a3ab4", "e0b8ff", "vein")
mat("brood_eye", "b860ff", "dca0ff", "glow", True)
mat("young_fur", "4a4262", "6e6290", "fur")


def _pup(r, parent, x, y, z, flip=1):
    """One of the young clinging to her back: a tiny eyeless prowler pup with violet glints and gripping paws."""
    r.cube(parent, (x - 1.6, y, z - 2.2), (3.2, 2.2, 4.4), "young_fur")
    r.cube(parent, (x - 1.3, y + 0.3, z - 4.4), (2.6, 2.3, 2.4), "young_fur")      # head
    r.cube(parent, (x - 1.4, y + 2.5, z - 3.8), (0.8, 1.3, 0.4), "young_fur")      # oversized ears
    r.cube(parent, (x + 0.6, y + 2.5, z - 3.8), (0.8, 1.3, 0.4), "young_fur")
    r.cube(parent, (x - 1.0, y + 1.3, z - 4.6), (0.7, 0.6, 0.3), "brood_eye")
    r.cube(parent, (x + 0.3, y + 1.3, z - 4.6), (0.7, 0.6, 0.3), "brood_eye")
    r.cube(parent, (x - 0.4, y + 0.5, z - 4.65), (0.8, 0.4, 0.3), "maw")          # tiny mouth
    for s in (1, -1):                                                           # paws gripping the fur
        r.cube(parent, (x + s * 1.5 - 0.4, y - 0.7, z - 1.8), (0.8, 1, 3.6), "young_fur")
    r.cube(parent, (x - 0.3 + flip * 0.6, y + 0.6, z + 2), (0.6, 0.6, 2), "young_fur")  # tail


def shadow_mother():
    """A huge hunched maternal beast of shadow: a face crowded with a brood of violet eyes, swollen glowing egg
    sacs under the belly, three young clinging to her back, heavy forelimbs with long pale claws and a mane."""
    r = Rig("shadow_mother")
    r.bone("body", None, (0, 12, 0), role="body")
    r.cube("body", (-6, 7, -8), (12, 9, 14), "mother_fur")                 # trunk
    r.cube("body", (-6.6, 12.5, -8.5), (13.2, 5.5, 8.5), "mother_fur")     # hunched shoulders
    r.cube("body", (-5, 7.5, 5), (10, 7.5, 5), "mother_fur")               # haunches
    r.cube("body", (-4.5, 6.2, -6.5), (9, 1, 11), "mother_hide")           # bare belly
    for (x, z, sz) in ((-2.6, -4, 2.6), (1.0, -2.5, 2.2), (-1.0, 1.2, 2.4), (2.4, 2.0, 1.8)):   # egg sacs
        r.cube("body", (x, 6.2 - sz * 0.8, z), (sz, sz * 0.8 + 0.3, sz), "brood_sac")
    for i in range(5):                                                     # spine plates
        r.cube("body", (-1, 18 - i * 0.6, -7 + i * 3), (2, 1, 2.2), "mother_plate")
    for (x, y, z) in ((-6.9, 13, -8), (5.9, 12.6, -7.5), (-6.4, 9.5, -8.4), (5.4, 9.8, -8.3)):   # shaggy mane
        r.cube("body", (x, y, z), (1, 4, 2.5), "mother_fur")
    r.cube("body", (-4, 15.8, -9.2), (8, 2, 1.5), "mother_fur")
    for k, (x, h) in enumerate(((-6.2, 5), (-4.6, 6.5), (3.4, 6), (5.2, 4.5), (-2.8, 3.5), (1.6, 4))):   # long mane hanging over the chest
        r.cube("body", (x, 16 - h, -9.4 - (k % 2) * 0.3), (1.1, h, 0.8), "mother_fur")
    for (x, y, z, rev) in ((-0.2, 18.2, -5.5, 1), (2.8, 16.6, 0.5, -1), (-3.0, 15.6, 4.0, 1)):
        _pup(r, "body", x, y, z, rev)
    r.cube("body", (-0.4, 5.3, 6), (0.4, 1.5, 0.4), "ink")                 # shadow dripping off her
    r.cube("body", (3.6, 6.0, -5.5), (0.4, 1.0, 0.4), "ink")
    # head
    r.bone("head", "body", (0, 12, -8), role="head")
    r.cube("head", (-3.8, 8.4, -14), (7.6, 6.8, 6.5), "mother_hide")       # skull
    r.cube("head", (-2.6, 8.4, -17), (5.2, 3.2, 3.5), "mother_hide")       # muzzle
    r.cube("head", (-1.2, 11.2, -17.2), (2.4, 0.6, 1), "mother_plate")     # nose
    r.cube("head", (-4.2, 15.0, -14.6), (8.4, 1.4, 5.6), "mother_plate")   # brow plate
    for s in (1, -1):                                                      # back-swept bone spurs
        r.cube("head", (s * 3.2 - 0.5, 15.6, -11), (1, 1, 4), "deep_claw")
        r.cube("head", (s * 3.5 - 0.4, 16.0, -7.6), (0.8, 0.8, 1.6), "deep_claw")
        r.cube("head", (s * 3.85 - 0.2, 9.4, -13.6), (0.4, 0.5, 0.5), "brood_eye")   # eyes down the cheeks too
        r.cube("head", (s * 2.65 - 0.2, 10.6, -16.4), (0.4, 0.4, 0.4), "brood_eye")
    eyes = ((-2.8, 12.6, 1.5), (1.2, 12.7, 1.5), (-0.5, 14.0, 0.8), (2.9, 14.0, 0.6), (-3.6, 14.2, 0.5),
            (-1.0, 12.0, 0.5), (3.1, 12.0, 0.6), (0.4, 13.8, 0.5), (-3.6, 11.6, 0.6), (2.1, 14.4, 0.4))
    for (x, y, sz) in eyes:                                                # the brood of eyes
        r.cube("head", (x, y, -14.3), (sz, sz, 0.4), "brood_eye")
        if sz >= 0.7:
            p = sz * 0.45
            r.cube("head", (x + (sz - p) / 2, y + (sz - p) / 2, -14.45), (p, p, 0.2), "pupil")
    for (x, y, z) in ((-6.8, 15.2, -6), (6.7, 14.4, -3.5), (-6.8, 11.8, -1.5), (6.7, 10.6, 2), (-5.2, 12.3, 7.6)):
        r.cube("body", (x, y, z), (0.3, 0.5, 0.5), "brood_eye")           # eyes glinting in the fur
    for x in (-2.3, -1.2, -0.3, 0.6, 1.7):                                 # upper teeth, two long fangs
        fang = x in (-2.3, 1.7)
        r.cube("head", (x, 6.6 if fang else 7.8, -17.6), (0.6, 2.0 if fang else 0.7, 0.6), "tooth")
    r.cube("head", (-2.7, 8.2, -17.3), (5.4, 0.4, 0.4), "mother_plate")    # lip line
    r.cube("head", (-2.3, 8.2, -16.6), (4.6, 0.3, 3), "maw")
    j = r.bone("jaw", "head", (0, 8.4, -12), role="jaw")
    r.cube(j, (-2.4, 6.8, -17.2), (4.8, 1.6, 5), "mother_hide")
    for x in (-1.8, -0.6, 0.6, 1.4):
        r.cube(j, (x, 8.3, -17.0), (0.45, 0.7, 0.45), "tooth")
    r.cube(j, (-0.3, 5.9, -16.6), (0.5, 0.9, 0.5), "ink")
    # forelimbs (rend, three blows)
    for s, side in ((1, "l"), (-1, "r")):
        a = r.bone(f"arm_{side}", "body", (s * 5.5, 13, -5), role=f"arm_{side}")
        r.cube(a, (s * 5.5 - 2.2, 9, -7.4), (4.4, 6, 4.8), "mother_fur")
        r.cube(a, (s * 5.5 - 1.8, 4, -7), (3.6, 5.5, 3.8), "mother_fur")
        r.cube(a, (s * 5.5 - 2.3, 8, -7.8), (4.6, 2, 1), "mother_plate")      # elbow plate
        r.cube(a, (s * 5.5 - 1.5, 1, -6.6), (3, 3.5, 3), "mother_hide")
        r.cube(a, (s * 5.5 - 2, 0, -9), (4, 1.6, 4.4), "mother_hide")
        _claws(r, a, s * 5.5, -9, 4, 3.4, w=0.6)
    for s, side in ((1, "l"), (-1, "r")):
        l = r.bone(f"leg_{side}", None, (s * 4.5, 11, 6.5), role=f"leg_{side}")
        r.cube(l, (s * 4.5 - 2, 5, 4), (4, 7, 5.2), "mother_fur")
        r.cube(l, (s * 4.5 - 1.4, 1, 6.6), (2.8, 5, 2.5), "mother_hide")
        r.cube(l, (s * 4.5 - 1.8, 0, 4.4), (3.6, 1.4, 4.5), "mother_hide")
        _claws(r, l, s * 4.5, 4.4, 3, 1.4, w=0.5)
    t = r.bone("tail", "body", (0, 12.5, 9.5), role="tail")
    r.cube(t, (-1.5, 11, 9.5), (3, 3, 5), "mother_fur")
    t2 = r.bone("tail2", t, (0, 12.3, 14), role="tail")
    r.cube(t2, (-1.1, 11.2, 14), (2.2, 2.2, 5), "mother_fur")
    r.cube(t2, (-0.8, 10.6, 15.5), (1.6, 0.8, 1.6), "brood_sac")           # a last egg carried on the tail
    r.cube(t2, (-0.6, 11.5, 18.8), (1.2, 1.2, 1.4), "mother_plate")
    return r
