"""The Matriarch Armour worn: a GeckoLib armour model (Blockbench format), its texture and glowmask and its idle
animation, generated here like the cradle's (tools/cradle_geo.py, whose box-UV painter it shares).

Few pieces, each a clear shape, and the detail in the painting: a smooth lacquered doll-head helmet with a gold rim,
the player's face left open under it, and a small crest on the brow painted with a doll's face and a row of pearls;
two rounded pauldrons like halves of little dolls over sleeves that cover the whole arm; a breastplate of khokhloma
lacquer (red, black and gold, a touch of green) painted with one gold filigree matryoshka round a gem, lit while the
Nested Shell is ready (gem_lit, gem_dim: client/MatriarchArmorRenderer); two broad skirt plates painted with folk
flowers on each leg; boots with gold toe caps. Every cube is inflated off the player's skin so nothing fights it. Its
idle animation runs a glint along the crest and breathes the gem.

The bones follow GeckoLib's armour template (armorHead, armorBody, armorRightArm, armorLeftArm, armorRightLeg,
armorLeftLeg, armorRightBoot, armorLeftBoot), in the player model's coordinates: 16 units to a block, the feet at
y 0, the head from y 24 to 32, the front toward -Z.
"""
import os

from craft import SKIN, INK, CHEEK, hramp, pnoise
from cradle_geo import Cube, Bone, Track, paint, LACQUER, LEAF, CREAM, FLOWER

ID = "matriarch"
BLACK = [(14, 8, 10), (28, 16, 18), (44, 26, 26), (62, 40, 36)]
GREEN = [(28, 70, 30), (58, 118, 48), (104, 160, 70)]
PEARL = [(196, 186, 176), (232, 226, 216), (252, 250, 244)]
# the armour's gold, deeper than the cradle's so it reads as metal under the world's light
GOLD = [(110, 66, 14), (176, 120, 32), (218, 164, 50), (244, 204, 96), (255, 236, 168)]
RED = [(66, 8, 14), (118, 18, 24), (168, 30, 32), (204, 46, 42), (230, 86, 66)]
# the box UV's front region is the face turned to the viewer (see tools/cradle_geo.py), its back region the other
FRONT, BACK = "south", "north"
CLEAR = (0, 0, 0, 0)


def build():
    bones = []

    def B(name, parent, pivot):
        b = Bone(name, parent, pivot)
        bones.append(b)
        return b

    def c(bone, o, s, mat, inflate=0.0, glow=False):
        bone.cubes.append(Cube(o, s, mat, glow=glow, inflate=inflate))

    def mirror(o, s):
        return [-o[0] - s[0], o[1], o[2]]

    # ---- the helmet: a lacquered doll's head, its gold rim at the brow, its crest with the painted doll face
    head = B("armorHead", None, [0, 24, 0])
    c(head, [-4, 24, -4], [8, 8, 8], "helmet", inflate=0.6)
    c(head, [-3.4, 32.6, -3.4], [6.8, 1.6, 6.8], "dome")
    c(head, [-1.3, 34.2, -1.3], [2.6, 1.3, 2.6], "knob", glow=True)
    c(head, [-3.2, 29.6, -5.5], [6.4, 5.8, 0.7], "crest")
    glint = B("glint_head", "armorHead", [0, 32, -5.6])
    c(glint, [-3.2, 34.4, -5.7], [0.7, 0.7, 0.2], "spark", glow=True)

    # ---- the breastplate, painted with the filigree matryoshka, and its gem
    body = B("armorBody", None, [0, 24, 0])
    c(body, [-4, 12, -2], [8, 12, 4], "chest", inflate=0.9)
    gem_dim = B("gem_dim", "armorBody", [0, 17.5, -3.2])
    c(gem_dim, [-1.0, 16.5, -3.6], [2.0, 2.0, 0.7], "gem_dim")
    gem_lit = B("gem_lit", "armorBody", [0, 17.5, -3.2])
    c(gem_lit, [-1.0, 16.5, -3.6], [2.0, 2.0, 0.7], "gem", glow=True)

    # ---- the arms: a sleeve over the whole arm, a rounded half-doll pauldron
    for side, name in ((-1, "armorRightArm"), (1, "armorLeftArm")):
        arm = B(name, None, [5 * side, 22, 0])

        def a(o, s, mat, **kw):
            c(arm, o if side < 0 else mirror(o, s), s, mat, **kw)
        a([-8, 12, -2], [4, 12, 4], "sleeve", inflate=0.7)
        a([-9.1, 20.4, -3.1], [6.2, 2.8, 6.2], "pauldron")
        a([-8.3, 23.2, -2.3], [4.6, 1.4, 4.6], "pauldron_top")

    # ---- the legs: a lacquered legging, two broad painted skirt plates
    for side, name in ((-1, "armorRightLeg"), (1, "armorLeftLeg")):
        leg = B(name, None, [1.9 * side, 12, 0])

        def l(o, s, mat, **kw):
            c(leg, o if side < 0 else mirror(o, s), s, mat, **kw)
        l([-4, 4, -2], [4, 8, 4], "legging", inflate=0.5)
        l([-4.7, 8.2, -2.7], [5.4, 3.9, 5.4], "skirt")
        l([-4.9, 4.8, -2.9], [5.8, 3.4, 5.8], "skirt_black")

    # ---- the boots, with gold toe caps
    for side, name in ((-1, "armorRightBoot"), (1, "armorLeftBoot")):
        boot = B(name, None, [1.9 * side, 12, 0])

        def b(o, s, mat, **kw):
            c(boot, o if side < 0 else mirror(o, s), s, mat, **kw)
        b([-4, 0, -2], [4, 4.2, 4], "boot", inflate=0.7)
        b([-4.5, -0.6, -3.5], [5.0, 1.8, 1.4], "toe")
    return bones


# =================================================================== the painting
def _hash(x, y, s):
    return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) & 0xffff


def _lacquer(g, ramp=RED):
    return ramp[3] if g > 0.5 else ramp[2]


def _flowers(xx, yy, fw, fh, seed, base, berry, leaf_col, stem_col):
    """Khokhloma painted on a face: stems curling across it, a flower of red petals round a gold heart every few
    texels, little leaves; the field otherwise its lacquer."""
    if fw < 3 or fh < 3:
        return base
    # one flower per cell of 5 x 4, offset from row to row
    cx = (xx + (yy // 4) * 2) % 5
    cy = yy % 4
    h = _hash((xx + (yy // 4) * 2) // 5, yy // 4, seed)
    if h % 3 != 2:
        if (cx, cy) == (2, 1):
            return GOLD[4]
        if (cx, cy) in ((1, 1), (3, 1), (2, 0), (2, 2)):
            return berry
        if (cx, cy) in ((1, 2), (3, 0)) and h % 2:
            return leaf_col
    if cy == 3 and (xx + yy) % 3 == 0:
        return stem_col
    return base


def texel(mat, face, xx, yy, fw, fh, cube, seed):
    """One texel of the armour, and whether it glows (a colour of four values is left clear)."""
    g = pnoise(xx + seed * 5.1, yy + seed * 2.7, 4, 600 + seed % 89)
    side = face in ("north", "south", "east", "west")
    # ---- the helmet: red lacquer, a gold rim at the brow, the face left open under it
    if mat == "helmet":
        if face == FRONT:
            if yy <= 1:
                return _lacquer(g), False
            if yy == 2:
                return (GOLD[4] if xx % 2 else GOLD[3]), xx % 3 == 0
            if 1 <= xx <= fw - 2:
                return CLEAR, False
            return GOLD[2], False
        if face == "down":
            return CLEAR, False
        if face == "up":
            return _lacquer(g, [RED[1], RED[2], RED[3], RED[4], RED[4]]), False
        # sides and back: lacquer, the gold rim, a flower at the nape
        if yy == 2:
            return GOLD[3], False
        if yy == fh - 1:
            return GOLD[1], False
        if face == BACK and 3 <= yy <= 6:
            return _flowers(xx, yy, fw, fh, seed, _lacquer(g), FLOWER[2], GREEN[1], BLACK[1]), False
        return _lacquer(g), False
    if mat == "dome":
        return ((GOLD[3] if yy == fh - 1 else _lacquer(g)) if side else RED[3] if face == "up" else RED[1]), False
    if mat == "knob":
        return (GOLD[4] if face == "up" else GOLD[3]), True
    # ---- the crest: a gold frame, a row of pearls along its top, a little doll's face in red scarf
    if mat == "crest":
        if face != FRONT and face != BACK:
            return GOLD[2], False
        if face == BACK:
            return _lacquer(g), False
        if yy == 0:
            return (PEARL[2] if xx % 2 == 0 else GOLD[3]), xx % 2 == 0
        if xx in (0, fw - 1) or yy == fh - 1:
            return GOLD[3], False
        cx, cy = (fw - 1) / 2, fh * 0.55
        d = ((xx - cx) / (fw * 0.3)) ** 2 + ((yy - cy) / (fh * 0.34)) ** 2
        if d <= 1:
            if yy < cy - 0.5:
                return (92, 50, 30), False
            if yy == int(cy) and abs(xx - cx) > 0.6:
                return INK, False
            if yy == int(cy) + 1 and abs(xx - cx) > 1.0:
                return CHEEK, False
            return SKIN[3], False
        return RED[3], False
    if mat == "spark":
        return (255, 252, 230), True
    # ---- the breastplate: khokhloma round a gold filigree matryoshka, the gem at its heart
    if mat == "chest":
        if face == "up" or face == "down":
            return GOLD[2] if face == "up" else RED[1], False
        if yy == 0 or yy == 1:
            return (GOLD[4] if yy == 0 else GOLD[2]), yy == 0
        if yy == fh - 2:
            return GOLD[3], False
        if yy == fh - 1:
            return GOLD[1], False
        if face in (FRONT, BACK):
            # the matryoshka in gold wire: a round head over a rounder body
            cx = (fw - 1) / 2
            hd = ((xx - cx) / 1.6) ** 2 + ((yy - 3.6) / 1.4) ** 2
            bd = ((xx - cx) / 2.8) ** 2 + ((yy - 7.2) / 2.9) ** 2
            on_head, on_body = abs(hd - 1) < 0.45, abs(bd - 1) < 0.32
            if on_head or on_body:
                return (GOLD[4] if xx <= cx else GOLD[3]), True
            if hd < 1:
                return (CREAM[3] if face == FRONT else GOLD[2]), False
            if bd < 1:
                # the doll's body inside the gold wire: a cream apron with a red rose under the gem
                ad = ((xx - cx) / 1.8) ** 2 + ((yy - 7.6) / 2.0) ** 2
                if ad < 1:
                    return (FLOWER[1] if ad < 0.35 else CREAM[3]), False
                return RED[3], False
        return _flowers(xx, yy, fw, fh, seed, _lacquer(g), FLOWER[2] if g > 0.5 else GOLD[3], GREEN[1], BLACK[1]), False
    # ---- the sleeves and pauldrons
    if mat == "sleeve":
        if not side:
            return RED[1], False
        if yy >= fh - 2:
            return (GOLD[3] if yy == fh - 2 else GOLD[1]), False
        if yy in (5, 6):
            return (GOLD[2] if yy == 5 else BLACK[2]), False
        return _flowers(xx, yy, fw, fh, seed, _lacquer(g), GOLD[3], GREEN[1], BLACK[1]), False
    if mat in ("pauldron", "pauldron_top"):
        if face == "up":
            return (RED[4] if mat == "pauldron_top" else RED[3]), False
        if face == "down":
            return GOLD[1], False
        if yy == fh - 1:
            return GOLD[3], True
        if mat == "pauldron_top":
            return (GOLD[4] if yy == 0 else _lacquer(g)), False
        return _flowers(xx, yy, fw, fh, seed, _lacquer(g), GOLD[4], GREEN[1], BLACK[1]), False
    # ---- the legs: lacquer under two skirt plates painted with flowers
    if mat == "legging":
        if not side:
            return RED[1], False
        return (BLACK[2] if g > 0.5 else BLACK[1]), False
    if mat in ("skirt", "skirt_black"):
        black = mat == "skirt_black"
        base = (BLACK[2] if g > 0.5 else BLACK[1]) if black else _lacquer(g)
        if face == "up":
            return (GOLD[3] if not black else GOLD[2]), False
        if face == "down":
            return BLACK[0], False
        if yy == 0:
            return GOLD[4], False
        if yy == fh - 1:
            return GOLD[2], True
        return _flowers(xx, yy, fw, fh, seed, base, FLOWER[2] if black else GOLD[3], GREEN[1], GOLD[1] if black else BLACK[1]), False
    # ---- the boots
    if mat == "boot":
        if not side:
            return RED[1] if face == "up" else BLACK[0], False
        if yy == 0:
            return GOLD[4], False
        if yy == 1:
            return GOLD[2], False
        return _lacquer(g), False
    if mat == "toe":
        return (GOLD[4] if face == "up" else GOLD[3] if g > 0.4 else GOLD[2]), face == "up"
    if mat == "gem":
        ramp = hramp("e8203a", dl=0.09)
        edge = xx in (0, fw - 1) or yy in (0, fh - 1)
        return (GOLD[4] if edge else ramp[5] if (xx + yy) % 2 == 0 else ramp[4]), True
    if mat == "gem_dim":
        edge = xx in (0, fw - 1) or yy in (0, fh - 1)
        return (GOLD[2] if edge else (70, 18, 30) if (xx + yy) % 2 else (96, 30, 44)), False
    return (255, 0, 255), False


def idle():
    """A glint running along the crest, the gem breathing."""
    t = Track(3.0, True)
    t.keys("glint_head", "position", [(0, [0, 0, 0]), (0.7, [5.7, 0, 0], "easeInOutSine"), (3.0, [5.7, 0, 0])])
    t.keys("glint_head", "scale", [(0, [0, 0, 0], "step"), (0.05, [1, 1, 1], "step"), (0.7, [1, 1, 1]), (0.75, [0, 0, 0], "step"), (3.0, [0, 0, 0], "step")])
    t.keys("gem_lit", "scale", [(0, [1, 1, 1]), (1.5, [1.18, 1.18, 1], "easeInOutSine"), (3.0, [1, 1, 1], "easeInOutSine")])
    return t


def gen(write, assets):
    bones = build()
    img, glow, tw = paint(bones, texel, start=64)
    tex = os.path.join(assets, "textures/item/armor")
    os.makedirs(tex, exist_ok=True)
    img.save(os.path.join(tex, f"{ID}.png"))
    glow.save(os.path.join(tex, f"{ID}_glowmask.png"))
    from cradle_geo import geo_json
    geo = geo_json(bones, tw)
    geo["minecraft:geometry"][0]["description"].update({"identifier": f"geometry.{ID}", "visible_bounds_width": 3, "visible_bounds_height": 3,
                                                        "visible_bounds_offset": [0, 1.5, 0]})
    for d in ("models", "animations"):
        os.makedirs(os.path.join(assets, f"geckolib/{d}/item/armor"), exist_ok=True)
    write(os.path.join(assets, f"geckolib/models/item/armor/{ID}.geo.json"), geo)
    write(os.path.join(assets, f"geckolib/animations/item/armor/{ID}.animation.json"), {"format_version": "1.8.0", "animations": {"idle": idle().json()}})
    return len(bones)


if __name__ == "__main__":
    import sys
    from PIL import Image
    img, glow, tw = paint(build(), texel, start=64)
    img.resize((tw * 6, tw * 6), Image.NEAREST).save(sys.argv[1] if len(sys.argv) > 1 else "matriarch_tex.png")
