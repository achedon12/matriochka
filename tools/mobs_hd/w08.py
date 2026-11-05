"""World 8, Hastened Seasons: time runs fast, seasons, clocks and hourglasses."""
import math

from common import Rig, mat

mat("w8_fur_spring", "b8956a", "e4cca0", "fur")
mat("w8_fur_summer", "3e7c2a", "74b844", "fur")
mat("w8_fur_autumn", "b4501c", "ec9a3a", "fur")
mat("w8_fur_winter", "dfe8f2", "ffffff", "fur")
mat("w8_snow", "eef4fa", "ffffff", "cloud")
mat("w8_frost", "9ad4f0", "e0f8ff", "crystal")
mat("w8_antler", "7a5a3a", "a8845a", "bark")
mat("w8_hoof", "2a1e18", "4a3a2e", "skin")
mat("w8_blossom", "f08ab8", "ffd0e4", "leaf")
mat("w8_leaf_summer", "4a9a2a", "8ad04a", "leaf")
mat("w8_leaf_red", "c83a1e", "f08a2a", "leaf")
mat("w8_sun_gold", "ffb020", "ffd850", "glow", True)

mat("w8_elder_robe", "5a466e", "7a6890", "cloth")
mat("w8_elder_robe_dark", "2a2034", "3e3250", "cloth")
mat("w8_elder_trim", "8a6a2a", "ffe08a", "rune")
mat("w8_elder_skin", "c8b49a", "e4d4bc", "skin")
mat("w8_beard", "e8e4dc", "ffffff", "fur")
mat("w8_sand_glow", "f4b850", "ffd890", "glow", True)
mat("w8_elder_eye", "ffa820", "ffd050", "glow", True)
mat("w8_sand_dark", "c8a060", "e0c080", "blocks")
mat("w8_hour_glass", "b8e0ec", "e8ffff", "glow", True)

mat("w8_dusk_day", "e87a2a", "ffc050", "cloth")
mat("w8_dusk_day_deep", "b83a3a", "e86a3a", "cloth")
mat("w8_dusk_night", "1e1e4a", "34346e", "cloth")
mat("w8_dusk_night_deep", "0e0e26", "22224a", "cloth")
mat("w8_dusk_stars", "1a1a44", "5a64b4", "spots")
mat("w8_dusk_violet", "6a2a6a", "a8487a", "cloth")
mat("w8_dusk_mask_day", "f0c890", "fff0c8", "skin")
mat("w8_dusk_mask_night", "a8b4d8", "d8e0f4", "skin")
mat("w8_moon_glow", "c8dcff", "ffffff", "glow", True)
mat("w8_dusk_claw", "1a1418", "3a3038", "skin")

mat("w8_tin_red", "c0342a", "6a1410", "lacquer")
mat("w8_tin_blue", "2e52a8", "16285a", "lacquer")
mat("w8_dial", "f4e8c8", "fff8e8", "skin")
mat("w8_dial_glow", "fff0c0", "fffae8", "glow", True)
mat("w8_hand_black", "1a1410", "2a2018", "metal")
mat("w8_glove", "f4f0e8", "ffffff", "skin")
mat("w8_gear_glow", "ffb43a", "ffe08a", "glow", True)

mat("w8_tower_stone", "8a8478", "b0aa9c", "blocks")
mat("w8_tower_dark", "5a564e", "7a766c", "blocks")
mat("w8_slate", "3a3e4a", "5a6070", "chitin")
mat("w8_bronze_bell", "b07a2a", "f0c060", "metal")
mat("w8_ivy", "3a6a2a", "6aa040", "leaf")
mat("w8_keeper_eye", "ffd040", "ffb020", "glow", True)


def _octo(r, bone, y, h, w, cut, m):
    """A rounded (octagonal) slab: two crossed cubes."""
    r.cube(bone, (-w / 2, y, -(w - cut) / 2), (w, h, w - cut), m)
    r.cube(bone, (-(w - cut) / 2, y, -w / 2), (w - cut, h, w), m)


def _dial_ticks(r, bone, cx, cy, z, rad, size=0.6, m="w8_hand_black", big=1.0):
    """Twelve hour marks around a clock face (front, facing -Z)."""
    for i in range(12):
        a = math.radians(i * 30)
        s = size * (big if i % 3 == 0 else 1)
        x, y = cx + math.sin(a) * rad, cy + math.cos(a) * rad
        r.cube(bone, (x - s / 2, y - s / 2, z), (s, s, 0.3), m)


def _hand(r, bone, cx, cy, z, length, width, angle, m="w8_hand_black", t=0.3):
    """A clock hand from the centre, `angle` in degrees clockwise from twelve."""
    r.cube(bone, (cx - width / 2, cy, z), (width, length, t), m, rot=(0, 0, -angle), pivot=(cx, cy, z))


# ------------------------------------------------------------------ Seasonal Creature
def seasonal_creature():
    """A stag whose body runs through the year from nose to tail: spring blossoms on its antlers and fawn head,
    a lush summer chest, an autumn flank shedding red leaves, a snowed-in winter rump with icicles."""
    r = Rig("seasonal_creature")
    r.bone("body", None, (0, 13, 0), role="body")
    r.cube("body", (-3.6, 9.6, -8.4), (7.2, 6.8, 5.4), "w8_fur_summer")             # summer chest
    r.cube("body", (-3.4, 9.4, -3.2), (6.8, 6.4, 5.6), "w8_fur_autumn")             # autumn flank
    r.cube("body", (-3.6, 9.6, 2.2), (7.2, 6.6, 5.8), "w8_fur_winter")              # winter rump
    r.cube("body", (-3.8, 15.8, 1.8), (7.6, 1.4, 6.4), "w8_snow")                   # snow cap on the rump
    r.cube("body", (-2.6, 17.0, 3.0), (5.0, 0.8, 4.0), "w8_snow")
    r.cube("body", (-3.9, 13.4, 2.0), (0.6, 2.8, 3.0), "w8_snow")
    r.cube("body", (3.3, 14.2, 4.6), (0.6, 2.0, 2.6), "w8_snow")
    r.cube("body", (-3.0, 16.2, -7.8), (6.0, 1.0, 4.4), "w8_leaf_summer")           # leafy ridge
    r.cube("body", (-1.6, 16.8, -6.8), (3.2, 0.8, 2.4), "w8_leaf_summer")
    r.cube("body", (-3.0, 15.6, -2.6), (6.0, 1.0, 4.6), "w8_leaf_red")              # autumn leaves on the back
    r.cube("body", (2.6, 13.2, -2.2), (1.2, 1.6, 1.6), "leaf_autumn")
    r.cube("body", (-3.8, 12.0, -1.0), (1.0, 1.8, 2.0), "leaf_autumn")
    r.cube("body", (-3.9, 11.6, -7.0), (0.6, 2.0, 2.2), "moss")                  # moss on the summer chest
    r.cube("body", (-1.2, 13.6, -8.8), (2.4, 2.4, 0.6), "petal_inner")           # sunflower on the chest
    r.cube("body", (-1.6, 13.2, -8.6), (3.2, 3.2, 0.3), "w8_sun_gold")
    for x, z in ((-2.6, 2.6), (-0.6, 4.2), (1.6, 3.0), (2.4, 6.2), (-2.2, 6.6), (0.4, 7.4)):   # icicles under the rump
        r.cube("body", (x, 8.2, z), (0.5, 1.6, 0.5), "w8_frost")
    r.cube("body", (-2.6, 8.8, -7.4), (5.2, 1.0, 4.0), "w8_fur_spring")             # pale belly
    r.cube("body", (-2.4, 8.8, -3.0), (4.8, 1.0, 5.0), "w8_fur_spring")

    neck = r.bone("neck", "body", (0, 14.5, -7))
    r.cube(neck, (-1.9, 12.8, -12.2), (3.8, 7.4, 4.4), "w8_fur_spring", rot=(-28, 0, 0), pivot=(0, 14.5, -8.5))
    r.cube(neck, (-2.1, 12.2, -10.8), (4.2, 3.0, 2.8), "w8_fur_winter", rot=(-28, 0, 0), pivot=(0, 14.5, -8.5))  # pale throat ruff
    r.cube(neck, (-0.9, 18.0, -10.8), (1.8, 0.8, 2.6), "w8_blossom", rot=(-28, 0, 0), pivot=(0, 14.5, -8.5))   # blossom mane

    head = r.bone("head", neck, (0, 18.5, -12), role="head")
    r.cube(head, (-2.3, 17.0, -15.2), (4.6, 3.8, 4.6), "w8_fur_spring")
    r.cube(head, (-1.6, 16.6, -18.4), (3.2, 2.8, 3.6), "w8_fur_spring")             # muzzle
    r.cube(head, (-1.2, 16.4, -18.6), (2.4, 1.0, 3.0), "w8_fur_winter")             # pale chin
    r.cube(head, (-0.9, 18.2, -18.8), (1.8, 1.0, 0.6), "pupil")                  # nose
    for s in (1, -1):
        r.cube(head, (s * 2.3 - 0.4, 18.4, -14.6), (0.8, 1.2, 1.4), "eye_gold")
        r.cube(head, (s * 2.4 - 0.25, 18.6, -14.8), (0.5, 0.8, 0.6), "pupil")
        r.cube(head, (s * 2.2 - (0 if s > 0 else 2.6), 19.4, -12.4), (2.6, 1.0, 1.4), "w8_fur_spring",
               rot=(0, 0, s * 20), pivot=(s * 2.2, 19.9, -11.7))                 # ears
        r.cube(head, (s * 2.4 - (0 if s > 0 else 1.6), 19.6, -12.5), (1.6, 0.6, 0.6), "petal",
               rot=(0, 0, s * 20), pivot=(s * 2.2, 19.9, -11.7))
        # antlers: a branching spring bough
        ax = s * 1.3
        r.cube(head, (ax - 0.4, 20.6, -13.4), (0.8, 3.4, 0.8), "w8_antler", rot=(0, 0, s * -18), pivot=(ax, 20.6, -13))
        r.cube(head, (ax + s * 1.0 - 0.35, 23.4, -13.4), (0.7, 2.8, 0.7), "w8_antler", rot=(0, 0, s * 8), pivot=(ax + s * 1.0, 23.4, -13))
        r.cube(head, (ax + s * 1.1 - (0 if s > 0 else 2.4), 22.6, -13.3), (2.4, 0.6, 0.6), "w8_antler")
        r.cube(head, (ax + s * 0.8 - 0.3, 22.0, -14.8), (0.6, 0.6, 1.8), "w8_antler")
        r.cube(head, (ax + s * 3.3 - 0.8, 22.2, -13.8), (1.6, 1.4, 1.6), "w8_blossom")
        r.cube(head, (ax + s * 1.5 - 0.9, 25.8, -13.9), (1.8, 1.4, 1.8), "w8_blossom")
        r.cube(head, (ax + s * 1.5 - 0.4, 26.4, -14.0), (0.8, 0.6, 0.4), "petal_inner")
        r.cube(head, (ax + s * 0.8 - 0.7, 21.6, -16.2), (1.4, 1.2, 1.4), "w8_blossom")
        r.cube(head, (ax - 0.5, 21.4, -13.0), (1.0, 0.8, 1.0), "leaf_spring")
    r.cube(head, (-1.0, 20.6, -15.6), (2.0, 0.6, 2.0), "petal_inner")             # flower crown on the brow

    for side, s in (("l", 1), ("r", -1)):
        fl = r.bone(f"arm_{side}", "body", (s * 2.2, 11, -6), role=f"arm_{side}")  # front legs: summer
        r.cube(fl, (s * 2.2 - 1.2, 5.2, -7.2), (2.4, 6.4, 2.4), "w8_fur_summer")
        r.cube(fl, (s * 2.2 - 0.8, 0.8, -6.8), (1.6, 5.0, 1.6), "w8_fur_spring")
        r.cube(fl, (s * 2.2 - 1.0, 4.8, -7.0), (2.0, 1.2, 2.0), "moss")           # knee
        r.cube(fl, (s * 2.2 - 1.0, 0, -7.2), (2.0, 1.2, 2.2), "w8_hoof")
        r.cube(fl, (s * 2.2 - 0.5 + s * 0.8, 6.6, -7.5), (1.0, 1.0, 0.6), "w8_blossom" if s > 0 else "petal_inner")
        bl = r.bone(f"leg_{side}", "body", (s * 2.3, 11, 5), role=f"leg_{side}")   # hind legs: winter
        r.cube(bl, (s * 2.3 - 1.4, 6.0, 3.6), (2.8, 5.8, 3.2), "w8_fur_winter")
        r.cube(bl, (s * 2.3 - 0.8, 0.8, 5.4), (1.6, 5.6, 1.6), "w8_fur_winter")
        r.cube(bl, (s * 2.3 - 1.0, 5.4, 5.0), (2.0, 1.4, 2.2), "w8_frost")           # frosted hock
        r.cube(bl, (s * 2.3 - 1.0, 0, 5.2), (2.0, 1.2, 2.2), "w8_hoof")
        r.cube(bl, (s * 2.3 - 0.2, 4.0, 6.9), (0.4, 1.4, 0.4), "w8_frost")           # icicle

    tail = r.bone("tail", "body", (0, 15, 8), role="tail")
    r.cube(tail, (-1.2, 13.4, 7.6), (2.4, 2.8, 2.0), "w8_fur_winter")
    r.cube(tail, (-1.3, 15.6, 7.4), (2.6, 0.8, 2.2), "w8_snow")
    r.cube(tail, (-0.25, 12.0, 9.0), (0.5, 1.6, 0.5), "w8_frost")

    for i, (x, y, z, m) in enumerate(((7, 18, -3, "w8_leaf_red"), (-7, 14, 3, "petal"), (1, 23, 7, "w8_frost"), (-5, 20, -8, "w8_leaf_summer"))):
        o = r.bone(f"season{i}", "body", (0, 13, 0), role="orbit")
        r.cube(o, (x - 0.6, y, z - 0.6), (1.2, 0.4, 1.2), m, rot=(0, 0, 25), pivot=(x, y, z))
    return r


# ------------------------------------------------------------------ Hourglass Elder
def hourglass_elder():
    """A hunched elder in a dusk-violet robe stitched with glowing numerals, an hourglass set into its chest with
    sand falling, a deep hood with golden eyes, bushy brows and a drooping moustache, a sundial staff in one hand
    and sand slipping through the fingers of the other."""
    r = Rig("hourglass_elder")
    r.bone("body", None, (0, 14, 0), role="body")
    r.cube("body", (-6.2, 0, -5.2), (12.4, 5.2, 10.4), "w8_elder_robe")             # robe skirt
    r.cube("body", (-6.4, 0, -5.4), (12.8, 1.2, 10.8), "w8_elder_trim")             # numeral hem
    r.cube("body", (-6.3, 1.2, -5.3), (12.6, 1.0, 10.6), "w8_sand_dark")            # sand-stained hem
    r.cube("body", (-5.4, 5.2, -4.6), (10.8, 6.4, 9.2), "w8_elder_robe")
    r.cube("body", (-4.8, 11.6, -3.8), (9.6, 8.0, 7.6), "w8_elder_robe")            # torso
    r.cube("body", (-5.0, 10.8, -4.0), (10.0, 0.8, 8.0), "w8_elder_trim")           # sash
    r.cube("body", (-0.5, 1.2, -5.5), (1.0, 4.0, 0.3), "w8_elder_trim")             # front opening of the robe
    r.cube("body", (-0.5, 5.2, -4.9), (1.0, 5.6, 0.3), "w8_elder_trim")
    r.cube("body", (2.4, 8.6, -4.9), (0.9, 2.2, 0.5), "brass")                   # hourglass charm on the sash
    r.cube("body", (2.6, 9.2, -5.0), (0.5, 1.0, 0.3), "w8_sand_glow")
    r.cube("body", (-5.6, 19.0, -4.4), (11.2, 2.8, 8.8), "w8_elder_robe_dark")      # mantle
    r.cube("body", (-5.7, 18.7, -4.5), (11.4, 0.6, 9.0), "w8_elder_trim")
    r.cube("body", (-3.8, 19.6, 2.4), (7.6, 4.0, 2.8), "w8_elder_robe_dark")        # the hunch
    for x, z, h in ((-5.8, -5.6, 2.2), (2.4, -5.6, 2.6), (-4.4, 4.8, 2.0), (1.6, 5.0, 2.4)):
        r.cube("body", (x, 0, z), (1.6, h * 0.4, 0.6), "w8_elder_robe_dark")        # tattered folds
    for x, z, w in ((-7.4, -2.0, 2.4), (6.0, 1.4, 2.0), (-3.4, -7.0, 3.0)):
        r.cube("body", (x, 0, z), (w, 0.5, w * 0.8), "sand")                     # sand pooling at the hem
    # the hourglass in the chest
    r.cube("body", (-3.2, 12.0, -4.1), (6.4, 7.0, 0.4), "ink")                   # dark recess
    r.cube("body", (-3.0, 18.6, -5.6), (6.0, 1.0, 2.2), "brass")                 # top plate
    r.cube("body", (-3.0, 11.8, -5.6), (6.0, 1.0, 2.2), "brass")                 # bottom plate
    for s in (1, -1):
        r.cube("body", (s * 2.5 - 0.35, 12.8, -5.4), (0.7, 5.8, 0.7), "brass")   # pillars
        r.cube("body", (s * 2.5 - 0.45, 15.3, -5.5), (0.9, 0.8, 0.9), "gold")
        r.cube("body", (s * 2.7 - 0.4, 18.0, -5.8), (0.8, 0.6, 0.8), "gold")     # finials
    r.cube("body", (-2.0, 16.0, -5.2), (4.0, 2.6, 1.6), "w8_hour_glass")            # upper bulb
    r.cube("body", (-1.2, 15.4, -5.0), (2.4, 0.7, 1.2), "w8_hour_glass")
    r.cube("body", (-1.7, 16.6, -5.35), (3.4, 1.2, 0.3), "w8_sand_glow")            # sand left in it
    r.cube("body", (-0.4, 14.8, -4.9), (0.8, 0.7, 0.9), "w8_hour_glass")            # neck
    r.cube("body", (-1.2, 14.2, -5.0), (2.4, 0.7, 1.2), "w8_hour_glass")
    r.cube("body", (-2.0, 12.8, -5.2), (4.0, 1.6, 1.6), "w8_hour_glass")            # lower bulb
    r.cube("body", (-1.8, 12.8, -5.35), (3.6, 1.0, 0.3), "w8_sand_glow")            # sand heap
    r.cube("body", (-0.9, 13.8, -5.35), (1.8, 0.5, 0.3), "w8_sand_glow")
    r.cube("body", (-0.15, 14.2, -5.45), (0.3, 2.4, 0.3), "w8_sand_glow")           # falling stream
    # embroidered clock on the back
    r.cube("body", (-3.0, 12.2, 3.7), (6.0, 6.0, 0.4), "w8_elder_trim")
    r.cube("body", (-2.4, 12.8, 3.9), (4.8, 4.8, 0.4), "w8_dial")
    _hand(r, "body", 0, 15.2, 4.2, 2.0, 0.5, 180 + 300)
    _hand(r, "body", 0, 15.2, 4.2, 1.4, 0.6, 180 + 60)

    head = r.bone("head", "body", (0, 21.5, -1), role="head")
    r.cube(head, (-3.6, 20.8, -5.2), (7.2, 6.8, 7.0), "w8_elder_robe")              # hood
    r.cube(head, (-3.0, 27.6, -4.4), (6.0, 1.2, 5.6), "w8_elder_robe")
    r.cube(head, (-1.6, 28.8, -2.6), (3.2, 1.4, 3.6), "w8_elder_robe_dark")          # hood peak, folded back
    r.cube(head, (-0.6, 29.0, 1.0), (1.2, 1.2, 2.2), "w8_elder_robe_dark")
    r.cube(head, (-3.9, 26.2, -6.8), (7.8, 1.4, 1.8), "w8_elder_robe")               # hood brim, deep
    r.cube(head, (-3.9, 21.0, -6.8), (1.2, 5.4, 1.8), "w8_elder_robe")
    r.cube(head, (2.7, 21.0, -6.8), (1.2, 5.4, 1.8), "w8_elder_robe")
    r.cube(head, (-4.0, 26.9, -6.9), (8.0, 0.4, 0.5), "w8_elder_trim")
    r.cube(head, (-2.7, 21.0, -5.5), (5.4, 5.4, 0.3), "ink")                     # shadow inside the hood
    r.cube(head, (-2.3, 21.4, -5.8), (4.6, 4.6, 0.4), "w8_elder_skin")              # the old face
    r.cube(head, (-2.5, 25.0, -6.3), (2.1, 0.9, 0.6), "w8_beard")                   # bushy brows
    r.cube(head, (0.4, 25.0, -6.3), (2.1, 0.9, 0.6), "w8_beard")
    r.cube(head, (-1.9, 23.9, -6.0), (1.3, 0.9, 0.3), "w8_elder_eye")
    r.cube(head, (0.6, 23.9, -6.0), (1.3, 0.9, 0.3), "w8_elder_eye")
    r.cube(head, (-0.5, 22.6, -6.7), (1.0, 2.0, 1.0), "w8_elder_skin")              # long hooked nose
    r.cube(head, (-0.4, 22.2, -7.0), (0.8, 0.6, 0.5), "w8_elder_skin")
    r.cube(head, (-2.0, 21.8, -6.4), (4.0, 0.8, 0.6), "w8_beard")                   # moustache
    for s in (1, -1):
        r.cube(head, (s * 1.9 - 0.35, 20.4, -6.4), (0.7, 1.6, 0.6), "w8_beard")     # drooping ends
    r.cube(head, (-1.8, 19.4, -6.2), (3.6, 2.4, 0.9), "w8_beard")                   # short beard over the glass
    r.cube(head, (-0.9, 18.6, -6.1), (1.8, 0.9, 0.8), "w8_beard")
    r.cube(head, (-0.4, 18.2, -6.0), (0.8, 0.6, 0.6), "gold")                    # beard ring
    r.cube(head, (-0.4, 27.8, -7.0), (0.8, 1.2, 0.4), "gold")                    # hourglass brooch on the hood
    r.cube(head, (-0.6, 28.9, -7.05), (1.2, 0.3, 0.5), "gold")
    r.cube(head, (-0.6, 27.6, -7.05), (1.2, 0.3, 0.5), "gold")

    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 5.0, 20.0, -0.6), role=f"arm_{side}")
        r.cube(arm, (s * 5.4 - 1.4, 14.6, -2.0), (2.8, 6.4, 2.8), "w8_elder_robe")    # sleeve
        r.cube(arm, (s * 5.4 - 1.9, 11.6, -2.6), (3.8, 3.4, 3.8), "w8_elder_robe")    # wide cuff
        r.cube(arm, (s * 5.4 - 2.0, 11.4, -2.7), (4.0, 0.8, 4.0), "w8_elder_trim")
        r.cube(arm, (s * 5.4 - 0.9, 9.8, -2.2), (1.8, 2.0, 1.8), "w8_elder_skin")     # bony hand
        for k in range(3):
            r.cube(arm, (s * 5.4 - 0.8 + k * 0.6, 8.8, -2.6), (0.4, 1.2, 0.4), "w8_elder_skin")  # long fingers
    staff = r.bone("staff", "arm_r", (-5.4, 10.5, -2.8))
    r.cube(staff, (-5.8, 0.4, -3.4), (0.8, 24.4, 0.8), "wood_dark")
    r.cube(staff, (-6.0, 9.6, -3.6), (1.2, 0.6, 1.2), "brass")
    r.cube(staff, (-6.0, 11.6, -3.6), (1.2, 0.6, 1.2), "brass")
    r.cube(staff, (-7.3, 24.6, -4.9), (3.8, 0.8, 3.8), "brass")                   # sundial top
    r.cube(staff, (-6.9, 25.4, -4.5), (3.0, 0.3, 3.0), "w8_dial")
    r.cube(staff, (-5.6, 25.6, -4.2), (0.4, 1.8, 0.4), "w8_hand_black")             # gnomon
    r.cube(staff, (-5.8, 23.6, -3.4), (0.8, 1.0, 0.8), "w8_sun_gold")
    r.cube("arm_l", (4.8, 7.8, -2.0), (1.2, 1.0, 1.2), "w8_sand_glow")              # sand running out of the hand
    r.cube("arm_l", (5.2, 5.2, -1.6), (0.4, 2.6, 0.4), "w8_sand_glow")
    for i, (x, y, z) in enumerate(((8, 24, 2), (-8, 18, -2), (2, 30, 5))):
        o = r.bone(f"sand{i}", "body", (0, 20, 0), role="orbit")
        r.cube(o, (x - 0.4, y, z - 0.4), (0.8, 0.8, 0.8), "w8_sand_glow")
    return r


# ------------------------------------------------------------------ Dusk Shade
def dusk_shade():
    """A floating twilight wraith split down the middle: its left half is a sunset running gold to crimson to violet,
    its right half a starry night. A sun eye and a crescent eye under a drooping hood, a halo that is half sun with
    rays and half crescent moon, long clawed sleeves and ragged strips trailing beneath it."""
    r = Rig("dusk_shade")
    r.bone("body", None, (0, 13, 0), role="body")
    tiers = [(16.0, 3.4, 7.6, 4.6, "w8_dusk_day", "w8_dusk_stars"),             # chest
             (12.2, 3.8, 8.4, 5.4, "w8_dusk_day_deep", "w8_dusk_night"),       # waist
             (8.2, 4.0, 9.6, 6.4, "w8_dusk_violet", "w8_dusk_stars"),          # flaring robe
             (5.6, 2.6, 10.4, 7.2, "w8_dusk_violet", "w8_dusk_night_deep")]
    for y, h, w, d, day, night in tiers:
        r.cube("body", (0, y, -d / 2 - 0.4), (w / 2, h, d), day)
        r.cube("body", (-w / 2, y, -d / 2 - 0.4), (w / 2, h, d), night)
    for x, y, z, m in ((-1.2, 13.4, -3.2, "w8_dusk_day_deep"), (-0.8, 9.6, -3.65, "w8_dusk_violet"),
                       (0.2, 17.0, -2.85, "w8_dusk_stars"), (0.4, 10.6, -3.25, "w8_dusk_night")):
        r.cube("body", (x, y, z), (1.0, 1.6, 0.5), m)                            # ragged boundary between halves
    r.cube("body", (0.4, 18.6, -3.2), (4.6, 1.8, 5.2), "w8_dusk_day")            # hunched shoulders
    r.cube("body", (-5.0, 18.6, -3.2), (4.6, 1.8, 5.2), "w8_dusk_night")
    r.cube("body", (3.2, 19.6, -1.8), (1.4, 1.6, 2.4), "w8_dusk_day_deep")       # shoulder rags
    r.cube("body", (-4.6, 19.6, -1.8), (1.4, 1.6, 2.4), "w8_dusk_night_deep")
    r.cube("body", (1.0, 13.6, -3.3), (2.2, 2.2, 0.4), "w8_sun_gold")            # sun sigil on the chest
    r.cube("body", (-3.0, 13.6, -3.3), (1.8, 2.2, 0.4), "w8_moon_glow")          # crescent sigil
    r.cube("body", (-2.4, 14.0, -3.45), (1.2, 1.6, 0.4), "w8_dusk_night_deep")
    for i in range(3):                                                           # ribs through the rags
        r.cube("body", (-2.2, 16.4 + i * 0.9, -3.0), (4.4, 0.4, 0.3), "bone")
    for x, y, z in ((-3.4, 17.2, -2.95), (-1.6, 11.4, -3.35), (-2.6, 7.0, -4.15)):
        r.cube("body", (x, y, z), (0.4, 0.4, 0.2), "pearl")                       # stars on the night half

    head = r.bone("head", "body", (0, 20, -1), role="head")
    r.cube(head, (0, 19.6, -4.6), (3.8, 5.6, 6.4), "w8_dusk_day")                 # hood, day side
    r.cube(head, (-3.8, 19.6, -4.6), (3.8, 5.6, 6.4), "w8_dusk_stars")
    r.cube(head, (0, 24.4, -6.0), (3.9, 1.4, 3.0), "w8_dusk_day_deep")            # brim drooping forward
    r.cube(head, (-3.9, 24.4, -6.0), (3.9, 1.4, 3.0), "w8_dusk_night")
    r.cube(head, (-2.4, 25.2, -3.6), (4.8, 1.2, 4.0), "w8_dusk_night_deep")
    r.cube(head, (-1.0, 26.2, -2.4), (2.0, 1.0, 2.6), "w8_dusk_night_deep")      # pointed tip
    r.cube(head, (-2.9, 19.8, -4.9), (5.8, 4.6, 0.4), "ink")                     # the dark inside of the hood
    r.cube(head, (0.5, 21.6, -5.2), (1.8, 1.2, 0.4), "w8_sun_gold")              # sun eye burning in the void
    r.cube(head, (1.1, 23.0, -5.1), (0.5, 0.5, 0.3), "w8_sun_gold")              # its little rays
    r.cube(head, (2.4, 22.0, -5.1), (0.5, 0.5, 0.3), "w8_sun_gold")
    r.cube(head, (1.1, 21.0, -5.1), (0.5, 0.4, 0.3), "w8_sun_gold")
    r.cube(head, (-2.3, 21.4, -5.2), (1.6, 1.8, 0.4), "w8_moon_glow")            # crescent moon eye
    r.cube(head, (-2.0, 21.8, -5.35), (1.1, 1.3, 0.4), "ink")                    # the bite that makes it a crescent
    for x in (-1.3, -0.5, 0.3, 1.1):
        r.cube(head, (x, 20.2, -5.15), (0.4, 0.6, 0.3), "bone")                  # a grin of teeth in the dark
    # the halo: half sun with rays (+X), half crescent moon (-X)
    cy, z = 22.4, 2.4
    for i, yy in enumerate((-3.6, -2.2, -0.8, 0.6, 2.0, 3.4)):
        w = math.sqrt(max(0.0, 4.4 ** 2 - (yy + 0.7) ** 2))
        r.cube(head, (0, cy + yy, z), (w, 1.4, 0.5), "w8_sun_gold")
    for a in (20, 55, 90, 125, 160):
        x, y = math.sin(math.radians(a)) * 5.6, math.cos(math.radians(a)) * 5.6
        r.cube(head, (x - 0.35, cy + y - 0.9, z + 0.05), (0.7, 1.8, 0.4), "w8_sun_gold",
               rot=(0, 0, -a), pivot=(x, cy + y, z))
    for a in range(204, 340, 26):
        rad = 4.4
        x, y = math.sin(math.radians(a)) * rad, math.cos(math.radians(a)) * rad
        sz = 1.5 - abs(a - 270) / 90 * 0.9
        r.cube(head, (x - sz / 2, cy + y - sz / 2, z), (sz, sz, 0.5), "w8_moon_glow")

    for side, s in (("l", 1), ("r", -1)):
        day = s > 0
        arm = r.bone(f"arm_{side}", "body", (s * 4.6, 19.4, -0.8), role=f"arm_{side}")
        r.cube(arm, (s * 5.0 - 1.1, 12.6, -1.9), (2.2, 7.2, 2.2), "w8_dusk_day" if day else "w8_dusk_stars")
        r.cube(arm, (s * 5.0 - 1.6, 10.4, -2.4), (3.2, 2.6, 3.2), "w8_dusk_day_deep" if day else "w8_dusk_night")  # ragged cuff
        r.cube(arm, (s * 5.0 - 1.6, 8.8, -2.2), (0.9, 1.8, 0.6), "w8_dusk_violet" if day else "w8_dusk_night_deep")
        r.cube(arm, (s * 5.0 + 0.6, 9.4, -0.2), (0.9, 1.2, 0.6), "w8_dusk_violet" if day else "w8_dusk_night_deep")
        r.cube(arm, (s * 5.0 - 0.8, 9.2, -1.6), (1.6, 1.6, 1.6), "w8_dusk_claw")
        for k in range(3):                                                       # long claws
            r.cube(arm, (s * 5.0 - 0.8 + k * 0.6, 6.4, -2.0 + k * 0.1), (0.4, 3.0, 0.4), "bone",
                   rot=(-15, 0, 0), pivot=(s * 5.0, 9.2, -1.6))

    strips = [(3.6, -3.6, "w8_dusk_violet", 3.4), (1.6, -3.8, "w8_dusk_day_deep", 4.2), (4.6, -0.6, "w8_dusk_violet", 2.6),
              (2.2, 3.0, "w8_dusk_day_deep", 4.4),
              (-1.6, -3.8, "w8_dusk_night", 3.6), (-3.8, -3.4, "w8_dusk_stars", 4.4), (-4.8, -0.2, "w8_dusk_night_deep", 3.0),
              (-2.4, 3.0, "w8_dusk_stars", 3.8)]
    for i, (x, z, m, ln) in enumerate(strips):                                   # tatters dragging below
        par = "body"
        y = 6.0
        for k in range(2):
            l = ln * (0.55 if k == 0 else 0.45)
            t = r.bone(f"rag{i}_{k}", par, (x, y, z), role="tail")
            w = 1.8 - k * 0.7
            r.cube(t, (x - w / 2, y - l, z - 0.45), (w, l + 0.4, 0.9), m)
            par, y = t, y - l

    for i, (x, y, z, m) in enumerate(((-7.5, 22, 2, "w8_moon_glow"), (7.5, 16, -2, "ember"), (-6.5, 9, -3, "pearl"))):
        o = r.bone(f"mote{i}", "body", (0, 13, 0), role="orbit")
        r.cube(o, (x - 0.4, y, z - 0.4), (0.8, 0.8, 0.8), m)
    return r


# ------------------------------------------------------------------ Child of Minutes
def minute_child():
    """A clockwork toddler with a too-big red alarm clock for a head: cream dial with twelve marks and hands, wide
    child eyes, twin brass bells, a wind-up key turning on top, a tin body with a gear heart, a spinning top in hand."""
    r = Rig("minute_child")
    r.bone("body", None, (0, 6, 0), role="body")
    r.cube("body", (-2.6, 4.0, -1.8), (5.2, 5.0, 3.6), "w8_tin_blue")
    r.cube("body", (-2.8, 3.6, -2.0), (5.6, 1.2, 4.0), "w8_tin_red")                # belt
    r.cube("body", (-0.5, 3.7, -2.15), (1.0, 1.0, 0.3), "brass")                 # buckle
    r.cube("body", (-1.4, 5.6, -2.0), (2.8, 2.8, 0.4), "brass")                  # chest window
    r.cube("body", (-1.0, 6.0, -2.15), (2.0, 2.0, 0.3), "w8_gear_glow")             # gear heart
    for x, y in ((-0.3, 8.0), (-0.3, 5.6), (-1.4, 6.8), (0.8, 6.8)):
        r.cube("body", (x, y, -2.25), (0.6, 0.4, 0.3), "brass")                  # gear teeth
    r.cube("body", (-3.0, 8.6, -2.2), (6.0, 0.9, 4.4), "w8_glove")                  # ruffled collar
    r.cube("body", (-2.2, 4.4, 1.7), (4.4, 3.6, 0.4), "brass")                   # back plate
    r.cube("body", (-0.4, 5.6, 2.0), (0.8, 0.8, 1.8), "brass")                   # back key
    r.cube("body", (-1.6, 5.0, 3.6), (3.2, 2.0, 0.5), "brass")

    head = r.bone("head", "body", (0, 9.4, 0), role="head")
    r.cube(head, (-6.0, 10.6, -2.6), (12.0, 8.6, 5.0), "w8_tin_red")             # clock case (rounded)
    r.cube(head, (-4.8, 9.4, -2.6), (9.6, 11.0, 5.0), "w8_tin_red")
    r.cube(head, (-5.4, 9.9, -2.6), (10.8, 10.0, 5.0), "w8_tin_red")
    r.cube(head, (-4.6, 10.6, -2.85), (9.2, 8.6, 0.3), "brass")               # thin bezel
    r.cube(head, (-3.8, 9.8, -2.85), (7.6, 10.2, 0.3), "brass")
    r.cube(head, (-4.2, 11.0, -3.1), (8.4, 7.8, 0.4), "w8_dial_glow")            # the dial
    r.cube(head, (-3.4, 10.2, -3.0), (6.8, 9.4, 0.3), "w8_dial_glow")
    _dial_ticks(r, head, 0, 14.9, -3.35, 3.9, 0.55, big=1.5)
    for s in (1, -1):                                                            # big child eyes
        r.cube(head, (s * 1.8 - 1.0, 14.6, -3.5), (2.0, 2.2, 0.3), "eye_white")
        r.cube(head, (s * 1.8 - 0.6 + s * 0.2, 14.8, -3.65), (1.2, 1.5, 0.3), "pupil")
        r.cube(head, (s * 1.8 - 0.3 + s * 0.3, 15.8, -3.75), (0.4, 0.4, 0.2), "w8_glove")   # catchlight
        r.cube(head, (s * 2.6 - 0.4, 13.4, -3.45), (0.8, 0.5, 0.2), "petal")             # rosy cheeks
    _hand(r, head, 0, 13.8, -3.6, 3.6, 0.4, -50)                                 # hands at ten past ten
    _hand(r, head, 0, 13.8, -3.6, 3.0, 0.5, 52)
    r.cube(head, (-0.4, 13.4, -3.75), (0.8, 0.8, 0.3), "brass")                  # hand pivot
    r.cube(head, (-0.7, 11.6, -3.5), (1.4, 0.8, 0.3), "maw")                     # little open mouth
    r.cube(head, (-4.4, 10.0, 2.4), (8.8, 9.4, 0.4), "brass")                    # back cover
    for i, (x, y) in enumerate(((-2.0, 12.0), (1.2, 15.6), (-1.6, 16.6))):
        rad = (1.6, 1.2, 0.9)[i]
        r.cube(head, (x - rad, y - rad, 2.7), (rad * 2, rad * 2, 0.4), "w8_gear_glow" if i == 0 else "gold")  # gears
        r.cube(head, (x - 0.3, y - 0.3, 3.0), (0.6, 0.6, 0.3), "w8_hand_black")
    for s in (1, -1):                                                            # twin alarm bells
        bx = s * 3.6
        r.cube(head, (bx - 1.8, 19.6, -1.8), (3.6, 1.8, 3.6), "brass", rot=(0, 0, s * -22), pivot=(bx, 19.6, 0))
        r.cube(head, (bx - 1.3, 21.4, -1.3), (2.6, 0.8, 2.6), "brass", rot=(0, 0, s * -22), pivot=(bx, 19.6, 0))
        r.cube(head, (bx - 0.3, 19.0, -0.3), (0.6, 1.0, 0.6), "w8_hand_black")
        r.cube(head, (s * 4.4 - 0.6, 8.8, -1.0), (1.2, 1.0, 2.0), "brass")        # little feet of the clock
    key = r.bone("key", head, (0, 20.4, 0), role="orbit")                        # wind-up key, turning
    r.cube(key, (-0.3, 20.0, -0.3), (0.6, 1.4, 0.6), "brass")
    r.cube(key, (-1.6, 21.2, -0.25), (3.2, 1.6, 0.5), "brass")
    r.cube(key, (-1.0, 21.6, -0.3), (0.7, 0.8, 0.6), "w8_tin_red")
    r.cube(key, (0.3, 21.6, -0.3), (0.7, 0.8, 0.6), "w8_tin_red")

    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 2.8, 8.4, 0), role=f"arm_{side}")
        r.cube(arm, (s * 3.2 - 0.8, 5.0, -0.8), (1.6, 3.8, 1.6), "w8_tin_blue")
        r.cube(arm, (s * 3.2 - 0.9, 6.4, -0.9), (1.8, 0.4, 1.8), "brass")       # elbow ring
        r.cube(arm, (s * 3.2 - 1.0, 3.4, -1.0), (2.0, 1.8, 2.0), "w8_glove")       # mitten
        leg = r.bone(f"leg_{side}", None, (s * 1.3, 4.2, 0), role=f"leg_{side}")
        r.cube(leg, (s * 1.3 - 0.9, 1.2, -0.9), (1.8, 3.4, 1.8), "brass")
        r.cube(leg, (s * 1.3 - 1.0, 2.6, -1.0), (2.0, 0.5, 2.0), "w8_hand_black")   # knee joint
        r.cube(leg, (s * 1.3 - 1.1, 0, -1.6), (2.2, 1.3, 2.6), "w8_tin_red")       # boots
    top = r.bone("top", "arm_r", (-3.2, 3.4, -1))                                # a spinning top in hand
    r.cube(top, (-4.0, 1.4, -1.8), (1.6, 1.4, 1.6), "w8_tin_red")
    r.cube(top, (-4.2, 2.0, -2.0), (2.0, 0.5, 2.0), "petal_inner")
    r.cube(top, (-3.5, 0.6, -1.3), (0.6, 0.8, 0.6), "brass")
    r.cube(top, (-3.5, 2.6, -1.3), (0.6, 1.4, 0.6), "w8_hand_black")              # its handle, held in the mitten
    return r


# ------------------------------------------------------------------ Hour Keeper
def hour_keeper():
    """A walking clock tower: stone body with a glowing clock face and roman marks, a pendulum swinging behind
    glass, a belfry head with burning eyes under its roof and a bronze bell for a heart, gear shoulders, a minute
    hand blade on one arm and a fist of cogs on the other, ivy creeping up the stone."""
    r = Rig("hour_keeper")
    r.bone("body", None, (0, 16, 0), role="body")
    r.cube("body", (-5.6, 10.0, -4.0), (11.2, 6.4, 8.0), "w8_tower_stone")          # lower tower
    r.cube("body", (-6.6, 16.0, -4.8), (13.2, 9.0, 9.6), "w8_tower_stone")          # clock storey
    r.cube("body", (-7.0, 15.4, -5.2), (14.0, 1.0, 10.4), "w8_tower_dark")          # cornices
    r.cube("body", (-7.0, 24.6, -5.2), (14.0, 1.0, 10.4), "w8_tower_dark")
    for s in (1, -1):
        r.cube("body", (s * 6.4 - 0.7, 16.4, -5.4), (1.4, 8.2, 1.4), "w8_tower_dark")   # corner buttresses
    # clock face
    r.cube("body", (-4.6, 16.4, -5.2), (9.2, 8.0, 0.4), "brass")
    r.cube("body", (-3.6, 15.9, -5.2), (7.2, 9.0, 0.4), "brass")
    r.cube("body", (-4.0, 17.0, -5.5), (8.0, 6.8, 0.4), "w8_dial_glow")
    r.cube("body", (-3.0, 16.5, -5.45), (6.0, 7.8, 0.3), "w8_dial_glow")
    _dial_ticks(r, "body", 0, 20.4, -5.75, 3.0, 0.5, big=1.6)
    _hand(r, "body", 0, 20.4, -5.85, 3.2, 0.5, 300)
    _hand(r, "body", 0, 20.4, -5.85, 2.2, 0.7, 90)
    r.cube("body", (-0.45, 19.95, -6.0), (0.9, 0.9, 0.3), "gold")
    # pendulum case
    r.cube("body", (-2.6, 10.6, -4.3), (5.2, 4.8, 0.4), "brass")
    r.cube("body", (-2.1, 11.0, -4.35), (4.2, 4.0, 0.2), "ink")
    pend = r.bone("pendulum", "body", (0, 15.2, -4.5), role="wing_l")
    r.cube(pend, (-0.15, 12.2, -4.6), (0.3, 3.0, 0.2), "gold")
    r.cube(pend, (-0.8, 11.2, -4.7), (1.6, 1.6, 0.3), "gold")
    r.cube(pend, (-0.4, 11.6, -4.8), (0.8, 0.8, 0.2), "w8_sun_gold")
    for s in (1, -1):                                                            # quoins on the lower tower
        r.cube("body", (s * 5.4 - 0.5, 11.6, -4.3), (1.0, 1.6, 1.6), "w8_tower_dark")
        r.cube("body", (s * 5.4 - 0.5, 13.4, 2.8), (1.0, 1.6, 1.6), "w8_tower_dark")
    r.cube("body", (-5.8, 9.6, -4.2), (11.6, 0.8, 8.4), "brass")                 # waist band
    # ivy and wear on the stone
    r.cube("body", (-6.9, 10.4, -1.0), (0.6, 6.0, 1.8), "w8_ivy")
    r.cube("body", (-7.2, 16.6, -2.2), (0.5, 4.0, 1.6), "w8_ivy")
    r.cube("body", (-7.25, 18.4, 0.4), (0.5, 2.6, 2.4), "w8_ivy")
    r.cube("body", (5.4, 10.4, 2.0), (0.6, 2.2, 1.4), "w8_ivy")
    r.cube("body", (-1.6, 16.0, 4.6), (3.2, 5.0, 0.6), "w8_tower_dark")             # arched window at the back
    r.cube("body", (-1.1, 16.4, 4.9), (2.2, 4.0, 0.4), "w8_gear_glow")
    r.cube("body", (-0.15, 16.4, 5.2), (0.3, 4.0, 0.2), "w8_hand_black")

    head = r.bone("head", "body", (0, 25.6, 0), role="head")
    r.cube(head, (-5.0, 25.6, -4.0), (10.0, 1.0, 8.0), "w8_tower_dark")             # belfry floor
    for x in (-4.8, 3.4):
        for z in (-3.8, 2.4):
            r.cube(head, (x, 26.6, z), (1.4, 4.6, 1.4), "w8_tower_stone")           # posts
    r.cube(head, (-5.2, 30.0, -4.6), (10.4, 1.4, 0.8), "w8_tower_dark")             # brow lintel
    r.cube(head, (-3.6, 30.3, -4.75), (2.2, 0.7, 0.3), "w8_keeper_eye")             # burning eyes
    r.cube(head, (1.4, 30.3, -4.75), (2.2, 0.7, 0.3), "w8_keeper_eye")
    r.cube(head, (-5.6, 31.2, -4.6), (11.2, 1.0, 9.2), "w8_slate")                  # roof
    r.cube(head, (-4.4, 32.2, -3.6), (8.8, 1.0, 7.2), "w8_slate")
    r.cube(head, (-3.0, 33.2, -2.4), (6.0, 1.0, 4.8), "w8_slate")
    r.cube(head, (-1.6, 34.2, -1.2), (3.2, 0.8, 2.4), "w8_slate")
    r.cube(head, (-0.3, 35.0, -0.3), (0.6, 1.6, 0.6), "gold")                    # finial
    r.cube(head, (-0.8, 35.6, -0.1), (1.6, 0.3, 0.2), "gold")
    r.cube(head, (-0.6, 30.6, -0.6), (1.2, 0.6, 1.2), "iron")                    # bell yoke
    bell = r.bone("bell", head, (0, 30.6, 0), role="tail")
    r.cube(bell, (-1.6, 28.4, -1.6), (3.2, 2.2, 3.2), "w8_bronze_bell")
    r.cube(bell, (-2.2, 26.8, -2.2), (4.4, 1.8, 4.4), "w8_bronze_bell")
    r.cube(bell, (-2.4, 26.7, -2.4), (4.8, 0.5, 4.8), "gold")                    # bell lip
    r.cube(bell, (-0.35, 26.0, -0.35), (0.7, 1.2, 0.7), "iron")                  # clapper

    for side, s in (("l", 1), ("r", -1)):
        arm = r.bone(f"arm_{side}", "body", (s * 7.4, 23.0, 0), role=f"arm_{side}")
        r.cube(arm, (s * 8.2 - 2.6, 21.4, -2.8), (5.2, 3.8, 5.6), "w8_tower_dark")   # shoulder block
        r.cube(arm, (s * 10.6 - 0.4, 20.6, -2.6), (0.8, 5.2, 5.2), "brass")       # shoulder gear
        r.cube(arm, (s * 10.6 - 0.4, 22.2, -3.2), (0.8, 2.0, 6.4), "brass")
        r.cube(arm, (s * 10.9 - 0.4, 22.4, -0.8), (0.8, 1.6, 1.6), "w8_gear_glow")
        r.cube(arm, (s * 8.2 - 1.9, 15.2, -1.9), (3.8, 6.8, 3.8), "w8_tower_stone")  # upper arm
        r.cube(arm, (s * 8.2 - 2.2, 13.6, -2.2), (4.4, 1.6, 4.4), "brass")        # elbow band
        r.cube(arm, (s * 8.2 - 2.1, 8.4, -2.1), (4.2, 5.6, 4.2), "w8_tower_stone")   # forearm
    # right: a minute-hand blade; left: a fist of cogs
    r.cube("arm_r", (-9.4, 6.4, -1.6), (2.4, 2.4, 3.0), "w8_tower_dark")         # fist gripping the hand
    r.cube("arm_r", (-8.75, 7.1, -13.0), (1.1, 1.0, 11.4), "w8_hand_black")      # minute-hand blade, a lance
    r.cube("arm_r", (-8.85, 7.0, -11.0), (1.3, 1.2, 0.6), "gold")
    r.cube("arm_r", (-9.4, 6.5, -6.4), (2.4, 2.2, 0.7), "gold")                  # ornate loop
    r.cube("arm_r", (-8.9, 7.0, -6.5), (1.4, 1.2, 0.9), "w8_hand_black")
    r.cube("arm_r", (-9.7, 6.3, -15.0), (3.0, 2.6, 2.0), "w8_hand_black")        # arrow head
    r.cube("arm_r", (-9.2, 6.8, -16.4), (2.0, 1.6, 1.4), "w8_hand_black")
    r.cube("arm_r", (-8.7, 7.2, -17.2), (1.0, 0.8, 0.8), "gold")
    r.cube("arm_r", (-9.0, 6.9, 1.4), (1.6, 1.4, 2.4), "gold")                   # counterweight
    r.cube("arm_l", (6.0, 6.2, -2.4), (4.4, 2.6, 4.8), "brass")                  # cog fist
    for z in (-2.8, -0.2, 2.2):
        r.cube("arm_l", (5.6, 6.6, z), (5.2, 1.6, 0.8), "gold")                  # cog teeth
    r.cube("arm_l", (5.8, 5.4, -1.2), (4.8, 0.8, 2.4), "gold")
    r.cube("arm_l", (10.3, 6.8, -0.6), (0.4, 1.2, 1.2), "w8_gear_glow")

    for side, s in (("l", 1), ("r", -1)):
        leg = r.bone(f"leg_{side}", None, (s * 3.0, 10.4, 0), role=f"leg_{side}")
        r.cube(leg, (s * 3.0 - 2.2, 1.6, -2.2), (4.4, 9.4, 4.4), "w8_tower_stone")
        r.cube(leg, (s * 3.0 - 2.4, 5.6, -2.4), (4.8, 1.0, 4.8), "brass")         # knee band
        r.cube(leg, (s * 3.0 - 2.8, 0, -3.2), (5.6, 1.8, 5.8), "w8_tower_dark")      # plinth foot
    for i, (x, y, z) in enumerate(((11, 30, 0), (-10, 27, 3), (0, 33, -9))):
        o = r.bone(f"cog{i}", "body", (0, 26, 0), role="orbit")
        r.cube(o, (x - 0.9, y - 0.9, z - 0.25), (1.8, 1.8, 0.5), "brass")
        r.cube(o, (x - 0.3, y - 1.3, z - 0.3), (0.6, 2.6, 0.6), "brass")
    return r
