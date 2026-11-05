"""World 7, Pressure Ocean: deep sea, crushing pressure, bioluminescence."""
from common import Rig, mat

mat("w7_hunter_hide", "172a36", "3e6878", "scales")
mat("w7_hunter_plate", "3a3c44", "8a9098", "chitin")
mat("w7_hunter_belly", "56767a", "a8c4c0", "skin")
mat("w7_hunter_fin", "12303e", "3ab0c0", "membrane")
mat("w7_needle", "d8e4ea", "ffffff", "crystal")
mat("w7_deep_maw", "4a0816", "b0304a", "flesh")
mat("w7_barnacle", "8a8478", "c8c0b0", "blocks")
mat("w7_photophore", "3af0ff", "e0ffff", "glow", True)
mat("w7_esca", "baffe0", "ffffff", "glow", True)

mat("w7_school_back", "1a2a44", "3a5a80", "scales")
mat("w7_school_silver", "c4ced8", "ffffff", "metal")
mat("w7_school_belly", "e4ecf2", "ffffff", "skin")
mat("w7_blade", "c8d4de", "ffffff", "crystal")
mat("w7_blade_edge", "8ad8ff", "ffffff", "glow", True)

mat("w7_jelly_bell", "2a46c8", "3a64e0", "glow", True)
mat("w7_jelly_dome", "3a6ae8", "5a90f4", "glow", True)
mat("w7_jelly_rim", "5a1aa8", "9a3ae0", "glow", True)
mat("w7_jelly_gonad", "ff6ac8", "ffd0f0", "glow", True)
mat("w7_jelly_core", "0c1230", "4a5ab0", "crystal")
mat("w7_jelly_band", "3ae8ff", "7af4ff", "glow", True)
mat("w7_tentacle", "6a3ac8", "b08aff", "glow", True)
mat("w7_tentacle_tip", "ff5ac0", "ffc0ec", "glow", True)

mat("w7_bell_bronze", "b07a34", "f0c868", "metal")
mat("w7_bell_dark", "6a4220", "a87038", "metal")
mat("w7_verdigris", "3a7a66", "7ac0a0", "flesh")
mat("w7_porthole", "ffc040", "ffa020", "glow", True)
mat("w7_crab_shell", "8a2218", "d8583a", "chitin")
mat("w7_crab_pale", "e8b090", "fff0e0", "skin")
mat("w7_seaweed", "2a5a2a", "5a9a3a", "leaf")

mat("w7_eel_armor", "16161e", "4a4a5a", "chitin")
mat("w7_eel_hide", "22303a", "3a5262", "scales")
mat("w7_eel_belly", "6a7a6a", "a8b09a", "skin")
mat("w7_eel_volt", "d8ff3a", "f4ff8a", "glow", True)
mat("w7_eel_fin", "1a2a30", "8af0ff", "membrane")


# ------------------------------------------------------------------ Abyssal Hunter
def abyssal_hunter():
    """A deep anglerfish: armoured skull, an underbite full of glass needles, a glowing lure dangling over the maw,
    milky eyes, photophores along the flanks and a tail that flicks like a whip."""
    r = Rig("abyssal_hunter")
    r.bone("body", None, (0, 7, 2), role="body")
    r.cube("body", (-4.5, 2.5, -2), (9, 9, 8), "w7_hunter_hide")
    r.cube("body", (-4, 2, -1.5), (8, 1.5, 7), "w7_hunter_belly")                 # pale belly
    for i, z in enumerate((0, 2.2, 4.4)):                                       # dorsal spines with a web
        r.cube("body", (-0.3, 11.5, z - 0.4), (0.6, 2.6 - i * 0.5, 0.8), "w7_needle")
    r.cube("body", (-0.15, 11.4, -0.2), (0.3, 1.6, 5.2), "w7_hunter_fin")
    for s in (1, -1):                                                           # photophores on the flanks
        for z, y in ((-0.5, 6), (2.0, 5.4), (0.8, 8.2)):
            r.cube("body", (s * 4.5 - (0.3 if s > 0 else 0.3), y, z), (0.6, 0.7, 0.7), "w7_photophore")
    r.cube("body", (3.6, 9.4, 1.2), (1.4, 1, 1.4), "w7_barnacle")                  # barnacles, one side only
    r.cube("body", (4.0, 8.4, 3.0), (1, 0.8, 1), "w7_barnacle")

    head = r.bone("head", "body", (0, 7, -1.5), role="head")
    r.cube(head, (-5, 4.5, -9), (10, 7.5, 7.6), "w7_hunter_hide")                   # skull
    r.cube(head, (-5.3, 10.6, -9.2), (10.6, 1.6, 5), "w7_hunter_plate")             # brow armour
    r.cube(head, (-4.4, 11.8, -7.8), (8.8, 1.2, 4.6), "w7_hunter_plate")
    r.cube(head, (-3.4, 12.6, -6.4), (6.8, 0.9, 3.4), "w7_hunter_plate")
    for s in (1, -1):
        r.cube(head, (s * 5.2 - 0.6, 6.2, -8.6), (1.2, 4.4, 6), "w7_hunter_plate")  # cheek plates
        r.cube(head, (s * 5.6 - 0.4, 9.6, -6.2), (0.8, 2.6, 0.8), "w7_needle")      # cheek spike
        r.cube(head, (s * 4.0 - 1.0, 9.8, -10.0), (2.0, 2.0, 1.6), "w7_hunter_plate")  # eye socket
        r.cube(head, (s * 4.0 - 0.8, 10.0, -10.3), (1.6, 1.6, 0.6), "w7_photophore")   # milky glowing eye
        r.cube(head, (s * 4.0 - 0.3, 10.4, -10.45), (0.6, 0.8, 0.3), "pupil")
    r.cube(head, (-4.6, 2.2, -8.8), (9.2, 2.4, 7), "w7_deep_maw")
    r.cube(head, (-5.2, 4.2, -9.6), (10.4, 0.9, 1.2), "w7_hunter_plate")              # upper lip                   # inside of the mouth
    for i, x in enumerate((-4.3, -3.0, -1.7, -0.4, 0.9, 2.2, 3.5)):             # upper needles, hanging
        h = 2.4 if i % 2 == 0 else 1.5
        r.cube(head, (x, 4.4 - h, -9.4), (0.5, h, 0.5), "w7_needle")
    for s in (1, -1):
        for z in (-7.4, -5.0):
            r.cube(head, (s * 4.4 - 0.25, 3.2, z), (0.5, 1.4, 0.5), "w7_needle")

    jaw = r.bone("jaw", head, (0, 4, -2.5), role="jaw")
    r.cube(jaw, (-5.6, 0.2, -10.4), (11.2, 2.2, 8.6), "w7_hunter_plate")            # underbite
    r.cube(jaw, (-5, -0.1, -9.6), (10, 0.8, 7), "w7_hunter_belly")
    r.cube(jaw, (-4.8, 2.2, -9.6), (9.6, 0.4, 6.4), "w7_deep_maw")                   # tongue floor
    for i, x in enumerate((-5.2, -3.8, -2.4, -1.0, 0.4, 1.8, 3.2, 4.6)):        # lower needles, pointing up
        h = 3.2 if i in (1, 6) else (2.2 if i % 2 == 0 else 2.7)
        r.cube(jaw, (x, 2.3, -10.2), (0.6, h, 0.6), "w7_needle")
    for s in (1, -1):
        r.cube(jaw, (s * 5.0 - 0.3, 2.3, -7.6), (0.6, 1.8, 0.6), "w7_needle")
    r.cube(jaw, (-0.5, -0.6, -9.4), (1.0, 1.0, 1.0), "w7_hunter_fin")               # chin barbel
    r.cube(jaw, (-0.4, -1.2, -9.3), (0.8, 0.7, 0.8), "w7_photophore")

    lure = r.bone("lure", head, (0, 12.8, -5.5), role="tail")                   # the illicium, sways
    r.cube(lure, (-0.4, 12.6, -5.9), (0.8, 2.6, 0.8), "w7_hunter_plate")
    r.cube(lure, (-0.35, 14.6, -8.6), (0.7, 0.7, 3.2), "w7_hunter_plate", rot=(-18, 0, 0), pivot=(0, 15, -5.5))
    r.cube(lure, (-0.35, 15.4, -14.6), (0.7, 0.7, 6.2), "w7_hunter_plate")
    r.cube(lure, (-0.3, 9.6, -14.6), (0.6, 6.0, 0.6), "w7_hunter_fin")
    r.cube(lure, (-1.3, 7.0, -15.6), (2.6, 2.6, 2.6), "w7_esca")                  # the esca
    r.cube(lure, (-0.6, 9.4, -14.9), (1.2, 0.5, 1.2), "w7_photophore")
    r.cube(lure, (-0.6, 6.5, -14.9), (1.2, 0.6, 1.2), "w7_photophore")
    for x, z in ((-1.0, -15.3), (0.6, -14.0)):
        r.cube(lure, (x, 5.2, z), (0.3, 1.5, 0.3), "w7_photophore")                # trailing filaments

    for side, s in (("l", 1), ("r", -1)):
        fin = r.bone(f"fin_{side}", "body", (s * 4.4, 5, 0.5), role=f"wing_{side}")
        r.cube(fin, (s * 4.2 - (0 if s > 0 else 4.2), 4.6, -0.5), (4.2, 0.5, 3.6), "w7_hunter_fin")
        for z in (-0.2, 2.0):
            r.cube(fin, (s * 4.2 - (0 if s > 0 else 4.2), 4.9, z), (4.4, 0.4, 0.4), "w7_hunter_plate")

    t0 = r.bone("tail0", "body", (0, 7, 5.6), role="seg")
    r.cube(t0, (-3.2, 3.6, 5.2), (6.4, 7, 4.8), "w7_hunter_hide")
    r.cube(t0, (-0.15, 10.4, 5.6), (0.3, 1.6, 3.6), "w7_hunter_fin")
    r.cube(t0, (-3.25, 6.2, 7.0), (6.5, 0.6, 0.8), "w7_photophore")                # lateral glow line
    t1 = r.bone("tail1", t0, (0, 7, 9.6), role="seg")
    r.cube(t1, (-2.2, 4.6, 9.2), (4.4, 5, 4.2), "w7_hunter_hide")
    r.cube(t1, (-0.15, 2.8, 9.8), (0.3, 1.8, 3), "w7_hunter_fin")
    fin = r.bone("tailfin", t1, (0, 7, 13), role="tail")
    r.cube(fin, (-0.3, 1.4, 12.8), (0.6, 11.2, 4.4), "w7_hunter_fin")
    r.cube(fin, (-0.45, 6.2, 12.6), (0.9, 1.6, 2), "w7_hunter_plate")
    for y in (3.0, 10.6):
        r.cube(fin, (-0.4, y, 13.2), (0.8, 0.4, 4.2), "w7_hunter_plate")           # fin rays
    r.cube(fin, (-0.35, 11.8, 16.6), (0.7, 0.8, 0.7), "w7_photophore")
    r.cube(fin, (-0.35, 1.4, 16.6), (0.7, 0.8, 0.7), "w7_photophore")
    return r


# ------------------------------------------------------------------ Blade School
def _blade_fish(r, name, parent, c, role):
    """One silver fish, nose to -Z: dark back, mirror flanks, a knife dorsal fin, blade pectorals, forked tail."""
    x, y, z = c
    f = r.bone(name, parent, (x, y, z), role=role)
    r.cube(f, (x - 0.8, y - 0.9, z - 2.6), (1.6, 1.9, 4.6), "w7_school_silver")   # mirror flanks
    r.cube(f, (x - 0.85, y + 0.5, z - 2.4), (1.7, 0.6, 4.4), "w7_school_back")    # dark back
    r.cube(f, (x - 0.55, y - 0.6, z - 3.4), (1.1, 1.2, 0.9), "w7_school_silver")  # snout
    r.cube(f, (x - 0.3, y - 0.4, z - 4.1), (0.6, 0.45, 0.8), "w7_blade")          # needle jaw
    r.cube(f, (x - 0.85, y + 0.05, z - 3.0), (1.7, 0.7, 0.7), "eye_white")
    r.cube(f, (x - 0.9, y + 0.2, z - 2.9), (1.8, 0.4, 0.4), "pupil")
    r.cube(f, (x - 0.15, y + 0.9, z - 1.6), (0.3, 1.2, 2.0), "w7_blade_edge", rot=(28, 0, 0), pivot=(x, y + 1, z - 1.6))
    r.cube(f, (x - 2.4, y - 0.6, z - 1.8), (4.8, 0.2, 0.8), "w7_blade")           # blade pectorals, both sides
    r.cube(f, (x - 0.85, y - 0.15, z - 1.9), (1.7, 0.25, 3.2), "w7_blade_edge")   # glowing lateral line
    t = r.bone(name + "_tail", f, (x, y, z + 1.9), role="tail")
    r.cube(t, (x - 0.1, y - 0.1, z + 1.9), (0.2, 1.6, 1.5), "w7_blade", rot=(40, 0, 0), pivot=(x, y, z + 2.1))
    r.cube(t, (x - 0.1, y - 1.5, z + 1.9), (0.2, 1.6, 1.5), "w7_blade", rot=(-40, 0, 0), pivot=(x, y, z + 2.1))
    return f


def blade_school():
    """Six razor fish packed into one tight school: a lead fish, a wedge behind it, two stragglers circling."""
    r = Rig("blade_school")
    lead = _blade_fish(r, "body", None, (0, 3.8, -4.5), "body")
    for i, c in enumerate(((-3.2, 2.4, -0.8), (3.0, 4.9, -0.4), (0.2, 4.4, 3.4))):
        _blade_fish(r, f"fish{i}", lead, c, "seg")
    for i, c in enumerate(((-5.6, 4.2, 4.4), (5.4, 2.6, 6.4))):
        o = r.bone(f"orbit{i}", lead, (0, 3.8, 0.5), role="orbit")
        _blade_fish(r, f"stray{i}", o, c, None)
    return r


# ------------------------------------------------------------------ Pressure Jelly
def _octo(r, bone, y, h, w, cut, m):
    """A rounded (octagonal) slab: two crossed cubes."""
    r.cube(bone, (-w / 2, y, -(w - cut) / 2), (w, h, w - cut), m)
    r.cube(bone, (-(w - cut) / 2, y, -w / 2), (w - cut, h, w), m)


def pressure_jelly():
    """A crushing jellyfish: a rounded luminous bell with four pink gonad rings and radial canals, a dense dark core
    clamped by bright pressure bands, two frilled oral arms that sting and a curtain of beaded glowing tentacles."""
    r = Rig("pressure_jelly")
    r.bone("body", None, (0, 16, 0), role="body")
    _octo(r, "body", 12.8, 2.4, 15.4, 4, "w7_jelly_rim")                            # bell margin
    _octo(r, "body", 15.2, 2.6, 14.6, 4, "w7_jelly_bell")
    _octo(r, "body", 17.8, 2.2, 13.2, 4, "w7_jelly_bell")
    _octo(r, "body", 20.0, 1.6, 11.0, 3.4, "w7_jelly_bell")
    _octo(r, "body", 21.6, 1.2, 8.6, 2.6, "w7_jelly_dome")
    _octo(r, "body", 22.8, 0.8, 5.6, 1.8, "w7_jelly_dome")
    for x, z, wx, wz in ((-8.2, -2.2, 0.8, 4.4), (7.4, -2.2, 0.8, 4.4), (-2.2, -8.2, 4.4, 0.8), (-2.2, 7.4, 4.4, 0.8),
                         (-6.6, -6.6, 2, 2), (4.6, -6.6, 2, 2), (-6.6, 4.6, 2, 2), (4.6, 4.6, 2, 2)):
        r.cube("body", (x, 11.8, z), (wx, 2.2, wz), "w7_jelly_rim")                  # scalloped lappets
    for x, z in ((-7.9, -5.3), (6.7, 4.1), (4.1, -7.9), (-5.3, 6.7)):
        r.cube("body", (x, 14.0, z), (1.2, 1.2, 1.2), "pearl")                    # photophores on the margin
    for s in (1, -1):                                                            # radial canals over the dome
        r.cube("body", (-0.4, 15.2, s * 7.3 - 0.25), (0.8, 4.8, 0.5), "w7_jelly_band")
        r.cube("body", (s * 7.3 - 0.25, 15.2, -0.4), (0.5, 4.8, 0.8), "w7_jelly_band")
    for x, z in ((-3.0, -3.0), (1.0, -3.0), (-3.0, 1.0), (1.0, 1.0)):           # four gonad rings on top
        r.cube("body", (x, 23.4, z), (2, 0.5, 2), "w7_jelly_gonad")
        r.cube("body", (x + 0.6, 23.5, z + 0.6), (0.8, 0.5, 0.8), "w7_jelly_dome")  # ring hole

    core = r.bone("core", "body", (0, 12, 0))                                    # the compressed core
    r.cube(core, (-3.4, 6.0, -3.4), (6.8, 5.4, 6.8), "w7_jelly_core")
    r.cube(core, (-2.2, 11.2, -2.2), (4.4, 2.0, 4.4), "w7_jelly_rim")               # manubrium, holds it up
    r.cube(core, (-3.9, 7.0, -3.9), (7.8, 0.8, 7.8), "w7_jelly_band")               # pressure bands
    r.cube(core, (-3.9, 9.4, -3.9), (7.8, 0.8, 7.8), "w7_jelly_band")
    r.cube(core, (-1.4, 5.8, -3.7), (0.6, 5.0, 0.4), "pearl")                    # bright cracks
    r.cube(core, (0.4, 7.8, -3.7), (1.6, 0.5, 0.4), "pearl")
    r.cube(core, (-2.4, 5.0, -2.4), (4.8, 1.2, 4.8), "w7_jelly_core")
    r.cube(core, (-1.1, 4.2, -1.1), (2.2, 0.9, 2.2), "w7_jelly_band")

    for side, s in (("l", 1), ("r", -1)):                                        # frilled oral arms
        arm = r.bone(f"arm_{side}", core, (s * 1.6, 5.0, -1.2), role=f"arm_{side}")
        r.cube(arm, (s * 1.6 - 0.9, 0.4, -2.1), (1.8, 5.0, 1.8), "w7_tentacle")
        for i, y in enumerate((3.6, 1.2)):
            r.cube(arm, (s * 1.6 - 1.6 + s * 0.3 * i, y, -2.8), (3.2, 1.0, 3.2), "w7_jelly_rim")  # frills
        r.cube(arm, (s * 1.6 - 0.6, -0.4, -1.8), (1.2, 1.2, 1.2), "w7_tentacle_tip")

    spots = [(-6, -5.2, 3), (5.4, -5.4, 3), (-6.2, 5, 3), (5.4, 5.4, 3), (0, -7, 2), (0, 6.6, 2), (-7.2, 0, 2), (7, 0, 2)]
    for i, (x, z, n) in enumerate(spots):                                        # tentacle curtain, beaded
        par = "body"
        y = 13.2
        for k in range(n):
            ln = 4.0 - k * 0.5 + (0.8 if i % 3 == 0 else 0)
            bend = (8 if (i + k) % 2 else -8, 0, 6 if (i + k) % 2 else -6)
            t = r.bone(f"ten{i}_{k}", par, (x, y, z), rot=bend if k else None, role="tail")
            w = 0.9 - k * 0.15
            r.cube(t, (x - w / 2, y - ln, z - w / 2), (w, ln + 0.4, w), "w7_tentacle")
            if k == 0:
                r.cube(t, (x - w / 2 - 0.25, y - 0.5, z - w / 2 - 0.25), (w + 0.5, 0.7, w + 0.5), "w7_tentacle_tip")
            if k == n - 1:
                r.cube(t, (x - 0.4, y - ln - 0.7, z - 0.4), (0.8, 0.8, 0.8), "w7_tentacle_tip")
            par, y = t, y - ln

    for i, (x, y, z) in enumerate(((9.5, 18, 0), (-9, 9, 3), (2, 25.2, 7.5))):    # pressure bubbles
        o = r.bone(f"bubble{i}", "body", (0, 16, 0), role="orbit")
        r.cube(o, (x - 0.6, y, z - 0.6), (1.2, 1.2, 1.2), "glass")
    return r


# ------------------------------------------------------------------ Bell Crab
def bell_crab():
    """A crab living under a bronze diving bell: riveted bands, glowing portholes (a tiny crab peeks out of the front
    one), a valve wheel and shackle on top, verdigris, barnacles and seaweed, periscope eyes peeking from under the
    rim, a heavy crusher claw and a slimmer cutter, six spiky walking legs."""
    r = Rig("bell_crab")
    r.bone("body", None, (0, 7, 0), role="body")
    r.cube("body", (-4.8, 3.4, -5.4), (9.6, 3, 10), "w7_crab_shell")                # the crab under the bell
    _octo(r, "body", 5.0, 1.8, 14.6, 3.6, "w7_bell_dark")                           # heavy rim band
    _octo(r, "body", 6.8, 4.8, 13.4, 3.4, "w7_bell_bronze")
    _octo(r, "body", 9.2, 0.8, 14.0, 3.6, "w7_bell_dark")                            # riveted mid band
    _octo(r, "body", 11.6, 2.4, 11.6, 3.0, "w7_bell_bronze")
    r.cube("body", (-4.2, 14.0, -4.2), (8.4, 1.2, 8.4), "w7_bell_bronze")
    r.cube("body", (-1.6, 15.2, -1.6), (3.2, 1.0, 3.2), "w7_bell_dark")              # valve
    r.cube("body", (-0.5, 16.2, -1.8), (1, 1.6, 0.9), "iron")                     # shackle
    r.cube("body", (-0.5, 16.2, 0.9), (1, 1.6, 0.9), "iron")
    r.cube("body", (-0.5, 17.6, -1.8), (1, 0.7, 3.6), "iron")
    r.cube("body", (1.6, 15.6, -0.3), (1.6, 0.6, 0.6), "brass")                   # valve wheel
    r.cube("body", (3.0, 14.9, -1.1), (0.5, 2.0, 2.0), "brass")
    for x in (-4.6, -1.6, 1.6, 4.6):                                             # rivets on the mid band
        r.cube("body", (x - 0.25, 9.35, -7.2), (0.5, 0.5, 0.4), "brass")
    for z in (-4.0, 4.0):
        r.cube("body", (-7.2, 9.35, z - 0.25), (14.4, 0.5, 0.5), "brass")
    # front porthole with a baby crab looking out
    r.cube("body", (-2.4, 10.0, -6.4), (4.8, 4.2, 0.8), "brass")
    r.cube("body", (-1.8, 10.6, -6.6), (3.6, 3.0, 0.6), "w7_porthole")
    r.cube("body", (-1.3, 10.6, -6.8), (2.6, 1.1, 0.4), "w7_crab_shell")
    r.cube("body", (-1.0, 11.6, -6.9), (0.7, 0.7, 0.4), "pupil")
    r.cube("body", (0.3, 11.6, -6.9), (0.7, 0.7, 0.4), "pupil")
    for s in (1, -1):                                                            # side portholes
        r.cube("body", (s * 6.6 - 0.4, 6.9, -1.8), (0.8, 3.6, 3.6), "brass")
        r.cube("body", (s * 6.8 - 0.3, 7.4, -1.3), (0.6, 2.6, 2.6), "w7_porthole")
        r.cube("body", (s * 6.85 - 0.35, 8.5, -1.6), (0.7, 0.4, 3.2), "brass")    # cross bar
    r.cube("body", (-1.8, 6.9, 6.2), (3.6, 3.6, 0.8), "brass")                   # back porthole
    r.cube("body", (-1.3, 7.4, 6.5), (2.6, 2.6, 0.6), "w7_porthole")
    r.cube("body", (-6.9, 10.2, -3), (1.2, 2.6, 4.4), "w7_verdigris")               # verdigris and growth
    r.cube("body", (2.2, 12.0, 3.0), (3.2, 2.2, 2.8), "w7_verdigris")
    r.cube("body", (-4.4, 13.6, 0.6), (2.6, 0.8, 2.6), "w7_verdigris")
    r.cube("body", (4.0, 13.4, -3.6), (1.4, 1.2, 1.4), "w7_barnacle")
    r.cube("body", (-5.4, 11.8, 3.4), (1.2, 1.0, 1.2), "w7_barnacle")
    r.cube("body", (5.4, 2.6, 3.0), (0.6, 2.6, 0.6), "w7_seaweed")                  # seaweed dangling from the rim
    r.cube("body", (-6.0, 2.0, 4.4), (0.6, 3.2, 0.6), "w7_seaweed")
    # periscope eyes peeking over the front rim, mouthparts beneath
    for s in (1, -1):
        r.cube("body", (s * 3.0 - 0.45, 4.0, -7.9), (0.9, 4.2, 0.9), "w7_crab_shell")
        r.cube("body", (s * 3.0 - 0.75, 8.0, -8.2), (1.5, 1.5, 1.5), "eye_gold")
        r.cube("body", (s * 3.0 - 0.35, 8.4, -8.4), (0.7, 0.8, 0.3), "pupil")
    r.cube("body", (-1.6, 3.2, -5.9), (3.2, 1.2, 0.6), "w7_crab_pale")              # mouthparts

    for side, s in (("l", 1), ("r", -1)):
        big = s > 0                                                              # left claw is the crusher
        arm = r.bone(f"arm_{side}", "body", (s * 4.4, 5, -4.8), role=f"arm_{side}")
        r.cube(arm, (s * 4.4 - 1.0, 4.0, -8.6), (2.0, 2.0, 4.6), "w7_crab_shell")
        r.cube(arm, (s * 4.4 - 1.2, 4.6, -7.2), (2.4, 0.8, 0.8), "w7_crab_pale")
        r.cube(arm, (s * 4.4 - 0.3, 5.9, -6.8), (0.6, 0.7, 0.6), "w7_crab_pale")   # spine
        claw = r.bone(f"claw_{side}", arm, (s * 4.8, 5, -8.2))
        w, h = (4.4, 4.2) if big else (3.0, 3.0)
        cx = s * (4.8 + w / 2 - 1.2)
        r.cube(claw, (cx - w / 2, 3.0, -12.6), (w, h, 4.8), "w7_crab_shell")         # palm
        r.cube(claw, (cx - w / 2 - 0.2, 3.0 + h - 0.7, -12.0), (w + 0.4, 0.7, 3.6), "w7_crab_pale")
        for k in range(2 if big else 1):
            r.cube(claw, (cx - w / 2 + 0.4 + k * 1.2, 3.0 + h, -11.6 + k * 1.1), (0.6, 0.5, 0.6), "w7_crab_pale")  # knobs
        fh = h * 0.38
        r.cube(claw, (cx - w / 2 + 0.3, 3.0, -16.4), (w - 0.6, fh, 4.0), "w7_crab_shell")    # fixed finger
        r.cube(claw, (cx - w / 2 + 0.3, 3.0 + fh, -16.0), (w - 0.6, 0.5, 3.4), "tooth")    # crushing teeth
        r.cube(claw, (cx - w / 2 + 0.6, 2.9, -17.2), (w - 1.2, fh + 0.4, 1.0), "w7_crab_pale")  # tip
        dy = 3.0 + h - fh
        r.cube(claw, (cx - w / 2 + 0.3, dy, -16.2), (w - 0.6, fh, 3.8), "w7_crab_shell",
               rot=(-18, 0, 0), pivot=(cx, dy + fh / 2, -12.4))                    # dactyl, open
        r.cube(claw, (cx - w / 2 + 0.6, dy - 0.3, -17.0), (w - 1.2, fh + 0.2, 1.0), "w7_crab_pale",
               rot=(-18, 0, 0), pivot=(cx, dy + fh / 2, -12.4))
        for i, z in enumerate((-2.8, 0.2, 3.2)):
            leg = r.bone(f"leg_{side}{i}", None, (s * 5.4, 5.4, z), role=f"leg_{side}")
            ox = s * 5.4 - (0 if s > 0 else 5.0)
            r.cube(leg, (ox, 4.6, z - 0.7), (5.0, 1.5, 1.4), "w7_crab_shell", rot=(0, 0, s * 24), pivot=(s * 5.4, 5.4, z))
            kx, ky = s * 9.8, 7.4                                                # the knee, high like a real crab
            r.cube(leg, (kx - 0.9, ky - 0.9, z - 0.85), (1.8, 1.6, 1.7), "w7_crab_pale")
            r.cube(leg, (kx - 0.65, 0.6, z - 0.6), (1.3, ky - 0.2, 1.2), "w7_crab_shell", rot=(0, 0, s * 14), pivot=(kx, ky, z))
            r.cube(leg, (kx - 0.35 + s * 1.7, 0.0, z - 0.35), (0.7, 1.4, 0.7), "w7_crab_pale")      # pointed tip
    o = r.bone("bubbles", "body", (0, 16, 0), role="orbit")
    r.cube(o, (1.2, 18.4, -0.4), (0.9, 0.9, 0.9), "glass")
    r.cube(o, (-0.8, 19.6, 0.6), (0.6, 0.6, 0.6), "glass")
    return r


# ------------------------------------------------------------------ Trench Eel
def trench_eel():
    """An armoured electric eel: a broad flat skull with a gaping jaw of hooked teeth and a charge glowing in the
    throat, voltaic rings and a lateral line down each flank, black armour plates with a spine ridge, a long
    ventral fin ribbon and a glowing paddle tail."""
    r = Rig("trench_eel")
    r.bone("body", None, (0, 4, -3), role="body")
    r.cube("body", (-2.6, 1.6, -7), (5.2, 5.0, 8.4), "w7_eel_hide")
    r.cube("body", (-2.8, 5.8, -6.6), (5.6, 1.2, 7.6), "w7_eel_armor")
    r.cube("body", (-2.3, 1.3, -6.6), (4.6, 1.0, 7.8), "w7_eel_belly")
    for s in (1, -1):
        r.cube("body", (s * 2.6 - 0.2, 3.8, -6.4), (0.4, 0.8, 7.4), "w7_eel_volt")
        r.cube("body", (s * 2.6 - 0.25, 2.2, -2.6), (0.5, 3.6, 0.8), "w7_eel_volt")     # voltaic ring
        r.cube("body", (s * 2.9 - (0 if s > 0 else 2.4), 2.4, -5.4), (2.4, 0.3, 2.2), "w7_eel_fin",
               rot=(0, 0, s * -20), pivot=(s * 2.6, 2.6, -4.4))                      # pectoral fins
    for z in (-5.6, -2.6, 0.2):
        r.cube("body", (-0.4, 7.0, z), (0.8, 1.1, 1.2), "w7_needle")

    head = r.bone("head", "body", (0, 4.2, -6.6), role="head")
    r.cube(head, (-3.0, 3.8, -14.6), (6.0, 2.8, 8.4), "w7_eel_hide")                # flat skull, upper jaw
    r.cube(head, (-3.2, 6.0, -13.8), (6.4, 1.1, 7.0), "w7_eel_armor")
    r.cube(head, (-2.4, 7.0, -12.4), (4.8, 0.6, 4.8), "w7_eel_armor")
    r.cube(head, (-2.6, 3.6, -15.2), (5.2, 2.2, 1.0), "w7_eel_armor")               # snout plate
    for s in (1, -1):
        r.cube(head, (s * 2.6 - 0.75, 5.3, -12.8), (1.5, 1.3, 1.5), "w7_eel_volt")  # eyes
        r.cube(head, (s * 2.6 - 0.35, 5.5, -13.1), (0.7, 0.8, 0.4), "pupil")
        r.cube(head, (s * 3.2 - 0.3, 6.2, -11.2), (0.6, 1.2, 3.6), "w7_needle", rot=(-22, 0, 0), pivot=(s * 3.2, 6.2, -11.2))
        r.cube(head, (s * 2.2 - 0.2, 1.4, -15.0), (0.4, 2.2, 0.4), "w7_eel_fin")     # barbels
        r.cube(head, (s * 2.2 - 0.25, 1.0, -15.05), (0.5, 0.5, 0.5), "w7_eel_volt")
    r.cube(head, (-2.7, 2.2, -14.4), (5.4, 1.8, 7.6), "w7_deep_maw")
    for x in (-2.5, -1.3, -0.1, 1.1, 2.0):
        r.cube(head, (x, 1.6, -14.9), (0.55, 2.0, 0.55), "tooth")
    for s in (1, -1):
        for z in (-12.8, -10.2):
            r.cube(head, (s * 2.5 - 0.3, 2.2, z), (0.6, 1.5, 0.6), "tooth")
    r.cube(head, (-1.0, 2.4, -11.6), (2.0, 1.0, 2.6), "w7_eel_volt")                 # charge in the throat

    jaw = r.bone("jaw", head, (0, 2.6, -7.4), role="jaw")
    r.cube(jaw, (-2.8, -0.2, -15.0), (5.6, 2.0, 8.0), "w7_eel_armor")               # lower jaw, hanging open
    r.cube(jaw, (-2.4, -0.4, -14.4), (4.8, 0.6, 7.0), "w7_eel_belly")
    r.cube(jaw, (-2.4, 1.6, -14.4), (4.8, 0.4, 6.6), "w7_deep_maw")
    for x in (-2.3, -1.1, 0.1, 1.3):
        r.cube(jaw, (x, 1.8, -14.8), (0.6, 1.8, 0.6), "tooth")
    for s in (1, -1):
        r.cube(jaw, (s * 2.3 - 0.3, 1.8, -12.6), (0.6, 1.3, 0.6), "tooth")

    par = "body"
    z = 1.0
    sizes = [4.8, 4.4, 4.0, 3.4, 2.8, 2.2]
    for i, w in enumerate(sizes):
        ln = 5.4
        role = "tail" if i == len(sizes) - 1 else "seg"
        bend = (0, (10, -12, -12, 8, 14, 8)[i], 0)                              # resting S-curve
        s_ = r.bone(f"seg{i}", par, (0, 4, z), rot=bend, role=role)
        y0 = 4 - w / 2 + 0.1
        r.cube(s_, (-w / 2, y0, z - 0.6), (w, w, ln + 0.6), "w7_eel_hide")
        r.cube(s_, (-w / 2 - 0.2, y0 + w - 0.5, z - 0.4), (w + 0.4, 0.9, ln * 0.6), "w7_eel_armor")    # overlapping plates
        if i < 3:
            r.cube(s_, (-w / 2 - 0.1, y0 + w - 0.5, z + ln * 0.55), (w + 0.2, 0.8, ln * 0.45), "w7_eel_armor")
        r.cube(s_, (-0.3, y0 + w + 0.3, z + 1.0), (0.6, 1.0 - i * 0.1, 1.0), "w7_needle")
        for s in (1, -1):                                                         # voltaic line and ring
            r.cube(s_, (s * w / 2 - 0.25, y0 + w * 0.5, z), (0.5, 0.6, ln), "w7_eel_volt")
            if i % 2 == 0:
                r.cube(s_, (s * w / 2 - 0.3, y0 + 0.4, z + ln * 0.55), (0.6, w - 0.9, 0.7), "w7_eel_volt")
        r.cube(s_, (-0.2, y0 - 1.5, z), (0.4, 1.6, ln), "w7_eel_fin")                # ventral fin ribbon
        if i == len(sizes) - 1:
            r.cube(s_, (-0.25, y0 - 1.6, z + ln - 0.4), (0.5, w + 3.0, 3.2), "w7_eel_fin")
            r.cube(s_, (-0.3, y0 - 1.8, z + ln + 2.2), (0.6, w + 3.4, 1.0), "w7_eel_volt")
        par, z = s_, z + ln
    return r
