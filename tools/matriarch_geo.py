"""The Matriarch Armour worn: a GeckoLib armour model (Blockbench format), its texture and glowmask and its idle
animation, generated here like the cradle's (tools/cradle_geo.py, whose box-UV painter it shares).

The set is drawn as the most precious of the mod: a lacquered doll-head crown with a gold rim, a kokoshnik crest
painted with a small face on the brow and a row of pearls; pauldrons shaped like little nested doll halves; a
breastplate in khokhloma lacquer (red, black and gold, a touch of green) with a matryoshka in gold filigree and a gem
at its heart that is lit while the Nested Shell is ready (gem_lit, gem_dim: block/../client/MatriarchArmorRenderer);
layered skirt plates painted with folk flowers on the legs; boots with gold toe caps. Its idle animation runs a glint
along the gold and breathes the gem.

The bones follow GeckoLib's armour template (armorHead, armorBody, armorRightArm, armorLeftArm, armorRightLeg,
armorLeftLeg, armorRightBoot, armorLeftBoot), in the player model's coordinates: 16 units to a block, the feet at
y 0, the head from y 24 to 32, the front toward -Z.
"""
import json
import os

from craft import SKIN, INK, CHEEK, hramp, pnoise
from cradle_geo import Cube, Bone, Track, paint, LACQUER, LEAF, CREAM, FLOWER

ID = "matriarch"
BLACK = [(14, 8, 10), (28, 16, 18), (44, 26, 26), (62, 40, 36)]
GREEN = [(28, 70, 30), (58, 118, 48), (104, 160, 70)]
PEARL = [(196, 186, 176), (232, 226, 216), (252, 250, 244)]
# the armour's gold, deeper than the cradle's so it reads as metal under the world's light
GOLD_DEEP = [(120, 74, 16), (184, 128, 34), (222, 168, 52), (246, 206, 98)]
# the box UV's front region is the face turned to the viewer (see tools/cradle_geo.py)
FRONT = "south"


def build():
    bones = []

    def B(name, parent, pivot):
        b = Bone(name, parent, pivot)
        bones.append(b)
        return b

    def c(bone, o, s, mat, faces=None, glow=False, inflate=0.0, rot=None, pivot=None):
        bone.cubes.append(Cube(o, s, mat, faces, glow=glow, rot=rot, pivot=pivot, inflate=inflate))

    def mirror(o, s):
        return [-o[0] - s[0], o[1], o[2]]

    # ---- the crown: a lacquered doll's head over the helmet, its gold rim, the crest with the painted face
    head = B("armorHead", None, [0, 24, 0])
    # the face stays open: lacquered cheek panels and a nape plate below the crown
    for x in (-4.7, 4.1):
        c(head, [x, 24.0, -4.6], [0.6, 6.0, 9.2], "khokhloma")
    c(head, [-4.7, 24.0, 4.0], [9.4, 6.0, 0.7], "khokhloma")
    c(head, [-4.9, 29.6, -4.9], [9.8, 0.9, 9.8], "gold")
    c(head, [-4.6, 30.5, -4.6], [9.2, 2.2, 9.2], "lacquer")
    c(head, [-3.8, 32.7, -3.8], [7.6, 1.1, 7.6], "lacquer")
    c(head, [-2.8, 33.8, -2.8], [5.6, 0.8, 5.6], "gold")
    c(head, [-1.4, 34.6, -1.4], [2.8, 0.9, 2.8], "lacquer")
    c(head, [-0.7, 35.5, -0.7], [1.4, 0.9, 1.4], "gold", glow=True)
    # the kokoshnik crest standing over the brow, its painted face, its gold edge and pearls
    c(head, [-4.2, 30.2, -5.6], [8.4, 5.4, 0.8], "lacquer", {FRONT: "crest", "north": "crest"})
    c(head, [-4.5, 29.8, -5.8], [9.0, 0.6, 1.2], "gold")
    c(head, [-4.5, 35.6, -5.8], [9.0, 0.6, 1.2], "gold")
    for x in (-4.6, 3.8):
        c(head, [x, 29.8, -5.8], [0.8, 6.4, 1.2], "gold")
    for i in range(5):
        c(head, [-3.6 + i * 1.6, 36.2, -5.4], [0.8, 0.8, 0.8], "pearl", glow=True)
    # gold cheek guards
    for x in (-5.1, 4.5):
        c(head, [x, 24.6, -3.6], [0.6, 4.4, 4.6], "gold")
    glint_h = B("glint_head", "armorHead", [0, 33, -5.8])
    c(glint_h, [-4.4, 32.6, -6.0], [0.6, 0.6, 0.3], "spark", glow=True)

    # ---- the breastplate: khokhloma lacquer, a gold collar and belt, the filigree matryoshka and its gem
    body = B("armorBody", None, [0, 24, 0])
    c(body, [-4.6, 12.2, -2.6], [9.2, 11.6, 5.2], "khokhloma", {FRONT: "emblem_plate"})
    c(body, [-4.9, 22.6, -2.9], [9.8, 1.4, 5.8], "gold")
    c(body, [-4.9, 12.0, -2.9], [9.8, 1.2, 5.8], "gold")
    c(body, [-1.0, 13.2, -2.9], [2.0, 9.4, 0.3], "gold")
    # the filigree doll on the chest: body, head, apron, face (in front of the plate)
    # the filigree doll: a gold body and head in relief, a small painted face, the gem at its heart
    c(body, [-2.4, 14.2, -3.2], [4.8, 4.6, 0.6], "filigree")
    c(body, [-1.6, 18.8, -3.2], [3.2, 2.8, 0.6], "filigree")
    c(body, [-0.9, 19.3, -3.4], [1.8, 1.7, 0.2], "cream")
    gem_dim = B("gem_dim", "armorBody", [0, 16.5, -3.7])
    c(gem_dim, [-1.1, 15.4, -4.0], [2.2, 2.2, 0.8], "gem_dim")
    gem_lit = B("gem_lit", "armorBody", [0, 16.5, -3.7])
    c(gem_lit, [-1.1, 15.4, -4.0], [2.2, 2.2, 0.8], "gem", glow=True)
    c(gem_lit, [-1.5, 15.0, -3.6], [3.0, 3.0, 0.3], "gem_halo", glow=True)
    # a gold doll down the back
    c(body, [-1.8, 14.6, 2.6], [3.6, 3.6, 0.4], "filigree")
    c(body, [-1.2, 18.2, 2.6], [2.4, 2.2, 0.4], "filigree")
    glint_b = B("glint_body", "armorBody", [0, 22, -3])
    c(glint_b, [-4.6, 22.8, -3.1], [0.6, 0.8, 0.3], "spark", glow=True)

    # ---- the arms: pauldrons like little nested doll halves, a vambrace, a gilded cuff
    for side, name in ((-1, "armorRightArm"), (1, "armorLeftArm")):
        arm = B(name, None, [5 * side, 22, 0])

        def a(o, s, mat, **kw):
            c(arm, o if side < 0 else mirror(o, s), s, mat, **kw)
        a([-8.8, 20.4, -3.0], [5.8, 0.7, 6.0], "gold")
        a([-8.6, 21.1, -2.8], [5.4, 2.4, 5.6], "lacquer")
        a([-8.0, 23.5, -2.2], [4.2, 1.2, 4.4], "lacquer")
        a([-7.2, 24.7, -1.2], [2.6, 0.8, 2.4], "gold")
        a([-8.5, 18.6, -2.7], [5.0, 1.8, 5.4], "khokhloma_black")
        a([-8.7, 18.3, -2.9], [5.4, 0.5, 5.8], "gold")
        a([-8.3, 16.3, -2.3], [4.6, 2.1, 4.6], "lacquer")
        a([-8.4, 12.4, -2.4], [4.8, 4.0, 4.8], "khokhloma")
        a([-8.6, 12.0, -2.6], [5.2, 0.9, 5.2], "gold")
        a([-8.6, 15.9, -2.6], [5.2, 0.6, 5.2], "gold")

    # ---- the legs: layered skirt plates painted with folk flowers, gold edges, knee cups
    for side, name in ((-1, "armorRightLeg"), (1, "armorLeftLeg")):
        leg = B(name, None, [1.9 * side, 12, 0])

        def l(o, s, mat, **kw):
            c(leg, o if side < 0 else mirror(o, s), s, mat, **kw)
        l([-4.5, 8.6, -2.6], [4.7, 3.4, 5.2], "khokhloma")
        l([-4.7, 8.3, -2.8], [5.1, 0.5, 5.6], "gold")
        l([-4.7, 5.4, -2.8], [5.1, 3.0, 5.6], "khokhloma_black")
        l([-4.9, 5.1, -3.0], [5.5, 0.5, 6.0], "gold")
        l([-3.6, 3.6, -3.2], [2.8, 1.8, 0.6], "gold")
        l([-3.0, 4.0, -3.4], [1.6, 1.0, 0.3], "gem_dim")

    # ---- the boots: lacquer with gold toe caps and cuffs
    for side, name in ((-1, "armorRightBoot"), (1, "armorLeftBoot")):
        boot = B(name, None, [1.9 * side, 12, 0])

        def b(o, s, mat, **kw):
            c(boot, o if side < 0 else mirror(o, s), s, mat, **kw)
        b([-4.4, 0.0, -2.6], [4.6, 3.4, 5.2], "khokhloma")
        b([-4.5, 0.0, -3.5], [4.8, 1.6, 1.2], "gold")
        b([-4.6, 3.2, -2.8], [5.0, 0.8, 5.6], "gold")
        b([-4.5, 0.0, 2.6], [4.8, 1.2, 0.6], "gold")
    return bones


def _hash(x, y, s):
    return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) & 0xffff


def texel(mat, face, xx, yy, fw, fh, cube, seed):
    """One texel of the armour's materials, and whether it glows."""
    g = pnoise(xx + seed * 5.1, yy + seed * 2.7, 4, 600 + seed % 89)
    if mat in ("khokhloma", "khokhloma_black"):
        # khokhloma: red (or black) lacquer with black (or gold) stems curling over it, berries of two by two texels
        # ringed in gold, a few green leaves; a gold line at the top of every band
        base = LACQUER if mat == "khokhloma" else BLACK
        c = base[3] if g > 0.45 else base[2]
        if face == "down":
            return base[1], False
        if face == "up":
            return base[2], False
        if yy == 0:
            return GOLD_DEEP[2], False
        if yy == fh - 1:
            return GOLD_DEEP[0], False
        bx, by = xx // 3, yy // 3
        h = _hash(bx, by, seed)
        lx, ly = xx % 3, yy % 3
        if h % 5 == 0 and lx < 2 and ly < 2:
            # a berry: red (gold on black) with a lit corner
            berry = FLOWER[2] if mat == "khokhloma_black" else GOLD_DEEP[2]
            return (GOLD_DEEP[3] if (lx, ly) == (0, 0) else berry), False
        if h % 7 == 1 and lx == 2 and ly == 1:
            return GREEN[1], False
        if (xx + yy * 2 + seed) % 7 == 0 and fh > 3:
            return (BLACK[1] if mat == "khokhloma" else GOLD_DEEP[1]), False
        return c, False
    if mat == "lacquer":
        c = LACQUER[3] if g > 0.45 else LACQUER[2]
        if face == "up":
            c = LACQUER[4]
        if face in ("north", "south", "east", "west") and yy == fh - 1:
            c = LEAF[2]
        return c, False
    if mat == "gold":
        # burnished gold leaf: deep tones, lit on top, a rare bright glint
        c = GOLD_DEEP[2] if g > 0.5 else GOLD_DEEP[1]
        if face == "up":
            c = GOLD_DEEP[3]
        if face == "down":
            c = GOLD_DEEP[0]
        glint = _hash(xx, yy, seed) % 19 == 0
        if glint:
            c = LEAF[5]
        return c, glint
    if mat == "filigree":
        # gold wire: a lit rim, an openwork lattice of gold over the dark lacquer behind it
        edge = xx in (0, fw - 1) or yy in (0, fh - 1)
        if edge:
            return GOLD_DEEP[3], True
        return ((GOLD_DEEP[2], True) if (xx + yy) % 2 == 0 or xx == fw // 2 else (LACQUER[1], False))
    if mat == "cream":
        if fh >= 2 and fw >= 2 and yy == fh // 2 and xx in (fw // 3, fw - 1 - fw // 3):
            return INK, False
        return CREAM[3], False
    if mat == "crest":
        # the kokoshnik's front: red lacquer, a gold arch, a small painted face at the brow
        cx, cy = (fw - 1) / 2, fh * 0.55
        dx, dy = (xx - cx) / max(1, fw * 0.22), (yy - cy) / max(1, fh * 0.34)
        if dx * dx + dy * dy <= 1:
            if yy < cy - fh * 0.14:
                return (92, 50, 30), False
            if yy == int(round(cy)) and abs(abs(xx - cx) - fw * 0.1) < 0.6:
                return INK, False
            if yy == int(round(cy)) + 1 and abs(abs(xx - cx) - fw * 0.16) < 0.6:
                return CHEEK, False
            return SKIN[3], False
        if dx * dx + dy * dy <= 1.6:
            return LEAF[4], False
        return (LACQUER[3] if g > 0.45 else LACQUER[2]), False
    if mat == "emblem_plate":
        return texel("khokhloma", face, xx, yy, fw, fh, cube, seed)
    if mat == "pearl":
        return (PEARL[2] if face == "up" else PEARL[1]), True
    if mat == "gem":
        ramp = hramp("e8203a", dl=0.09)
        return (ramp[5] if (xx + yy) % 2 == 0 else ramp[4]), True
    if mat == "gem_halo":
        return GOLD_DEEP[3], True
    if mat == "gem_dim":
        edge = xx in (0, fw - 1) or yy in (0, fh - 1)
        return ((LEAF[2] if edge else (70, 18, 30) if (xx + yy) % 2 else (96, 30, 44))), False
    if mat == "spark":
        return (255, 252, 230), True
    if mat == "none":
        return LACQUER[2], False
    return (255, 0, 255), False


def idle():
    """A glint running along the gold, the gem breathing."""
    t = Track(3.0, True)
    for bone in ("glint_head", "glint_body"):
        t.keys(bone, "position", [(0, [0, 0, 0]), (0.8, [8.6, 0, 0], "easeInOutSine"), (3.0, [8.6, 0, 0])])
        t.keys(bone, "scale", [(0, [0, 0, 0], "step"), (0.05, [1, 1, 1], "step"), (0.8, [1, 1, 1]), (0.85, [0, 0, 0], "step"), (3.0, [0, 0, 0], "step")])
    t.keys("gem_lit", "scale", [(0, [1, 1, 1]), (1.5, [1.25, 1.25, 1], "easeInOutSine"), (3.0, [1, 1, 1], "easeInOutSine")])
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
