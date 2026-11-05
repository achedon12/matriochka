"""Boss moves, part A: the Surface to the Lightless Deep (see tools/boss_moves.py for the kit and conventions).

Every boss function receives its kit, the three windup lengths and the three release budgets of its timing
tier, and returns its attack slugs and its clips. Times inside a clip are normalised (0 to 1); clip.sec(s)
converts seconds when a beat must last a fixed time whatever the tier.
"""
import math

from boss_moves import boss, BLEND, PHASE_SECONDS, DEATH_TICKS


def parts(kit, wind, rel, slot, strike):
    """The three clips of one attack slot: a held windup, a strike of `strike` seconds and a recover that fills
    what is left of the release budget once the controller's two blends are taken out."""
    w = kit.clip(wind[slot], "hold")
    s = kit.clip(strike)
    r = kit.clip(max(0.3, rel[slot] - strike - 2 * BLEND))
    return w, s, r


def finish(slug, w, s, r, clips, boss_id):
    s.start_from(w)
    r.start_from(s)
    r.settle()
    base = f"attack.{boss_id}.{slug}"
    clips[base + ".windup"] = w
    clips[base + ".strike"] = s
    clips[base + ".recover"] = r


def phase_clip(kit):
    return kit.clip(PHASE_SECONDS - BLEND)


def death_clip(kit):
    return kit.clip(DEATH_TICKS / 20 - BLEND, "hold")


def outward(kit, bone, dist, dy=0.0):
    """The position offset that pushes an orbiting part `dist` units away from the body's axis (and dy up)."""
    cs = [c for c in kit.bones[bone]["cubes"]]
    x = sum(c["origin"][0] + c["size"][0] / 2 for c in cs) / len(cs)
    z = sum(c["origin"][2] + c["size"][2] / 2 for c in cs) / len(cs)
    n = math.hypot(x, z) or 1
    return (x / n * dist, dy, z / n * dist)


# =============================================================== The Surface: Block Guardian
@boss("block_guardian", world=0)
def block_guardian(k, wind, rel):
    C = {}
    B = "block_guardian"
    legs = lambda fl, fr, ll=0, lr=0: [("leg_l0", "leg_l1", fl, ll), ("leg_r0", "leg_r1", fr, lr)]
    blocks = [f"block{i}" for i in range(4)]

    # ---- Punch: the right fist cocks back past the hip while the left guards, then drives straight ahead
    w, s, r = parts(k, wind, rel, 0, 0.22)
    w.rot("body", (0, 0, 0, 0), (0.55, -4, -24, 0, "cout"), (1, -6, -28, 0, "sine"))
    k.stance(w, 0, legs(0, 0), 0, body=None)
    k.stance(w, 0.6, legs(5, -4), 1.5, ease="cout")
    k.stance(w, 1, legs(5, -4), 2.0)
    w.pos("body", (0, 0, 0, 0), (0.6, 0, -1.5, 1.0, "cout"), (1, 0, -2, 1.2))
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, 48, 0, -14, "cout"), (1, 52, 0, -16, "sine"))
    w.rot("arm_r1", (0, 0, 0, 0), (0.6, -72, 0, 0, "cout"), (1, -78, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -48, 10, 8, "cout"), (1, -52, 12, 8))
    w.rot("arm_l1", (0, 0, 0, 0), (0.6, -45, 0, 0), (1, -50, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.6, 8, 22, 0, "cout"), (1, 10, 26, 0))
    w.scl("core", (0, 1), (1, 1.2, "sine"))
    s.rot("body", (0.45, 10, 26, 0, "expo"), (1, 8, 22, 0))
    k.stance(s, 0.45, legs(8, -6), 2.5, z=-3, ease="expo")
    k.stance(s, 1, legs(8, -6), 2.2, z=-3)
    s.pos("body", (0.45, 0, -2.5, -3.5, "expo"), (1, 0, -2.2, -3.2))
    s.rot("arm_r0", (0.45, -98, 0, -4, "expo"), (1, -90, 0, -6))
    s.rot("arm_r1", (0.45, -4, 0, 0, "expo"), (1, -8, 0, 0))
    s.rot("arm_l0", (0.45, 18, 0, 12, "expo"), (1, 14, 0, 10))
    s.rot("arm_l1", (0.45, -20, 0, 0), (1, -24, 0, 0))
    s.rot("head", (0.45, 4, -18, 0, "expo"), (1, 6, -16, 0))
    s.scl("core", (0.45, 1.3, "expo"), (1, 1.1))
    s.rot("jaw", (0, 0, 0, 0), (0.45, 18, 0, 0, "expo"), (1, 6, 0, 0))
    r.rot("arm_r0", (0.35, -60, 0, -6, "sine"))
    r.rot("body", (0.4, 4, 10, 0, "sine"))
    finish("punch", w, s, r, C, B)

    # ---- Shockwave: a double fist raised overhead with the torn blocks rising, then the ground is struck
    w, s, r = parts(k, wind, rel, 1, 0.34)
    k.stance(w, 0, legs(0, 0), 0, body=None)
    k.stance(w, 0.22, legs(1, -1), 3.5, body="body", ease="sine")
    k.stance(w, 0.62, legs(2, -2), 0.5, body="body", ease="sine")
    k.stance(w, 1, legs(2, -2), 0.8, body="body")
    w.rot("body", (0, 0, 0, 0), (0.22, 16, 0, 0, "sine"), (0.62, -14, 0, 0, "cout"), (1, -16, 0, 0))
    w.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.22, 34, 0, 0, "sine"))
    w.rot("arm_l0", (0.62, -166, 0, 14, "cout"), (1, -170, 0, 16))
    w.rot("arm_r0", (0.62, -166, 0, -14, "cout"), (1, -170, 0, -16))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.22, -10, 0, 0), (0.62, -24, 0, 0), (1, -26, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.22, 12, 0, 0), (0.62, -20, 0, 0, "cout"), (1, -22, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.55, 0, 0, 0), (0.7, 22, 0, 0, "back"), (1, 26, 0, 0))
    for i, b in enumerate(blocks):
        d = 0.08 * i
        w.pos(b, (0, 0, 0, 0), (0.25 + d, 0, -2, 0, "sine"), (0.7 + d * 0.5, 0, 10 + i, 0, "back"), (1, 0, 11 + i, 0))
    w.scl("core", (0, 1), (0.6, 1.2), (1, 1.35))
    w.tremble("body", "rotation", 0.7, 1.0, 1.6, 6, (0, 1, 1))
    w.tremble("arm_l0", "rotation", 0.7, 1.0, 2.5, 5, (1, 0, 0))
    w.tremble("arm_r0", "rotation", 0.7, 1.0, 2.5, 5, (1, 0, 0))
    k.stance(s, 0.38, legs(4, -4), 5.5, body="body", ease="cin")
    k.stance(s, 1, legs(4, -4), 4.6, body="body", ease="cout")
    s.rot("body", (0.38, 36, 0, 0, "cin"), (1, 30, 0, 0, "cout"))
    s.scl("body", (0, 1), (0.38, 1.05, 0.93, 1.05, "cin"), (1, 1, 1, 1, "cout"))
    s.rots(["arm_l0", "arm_r0"], (0.38, -60, 0, 0, "cin"), (1, -56, 0, 0))
    s.rot("arm_l0", (0.38, -60, 0, 6, "cin"))
    s.rot("arm_r0", (0.38, -60, 0, -6, "cin"))
    s.rots(["arm_l1", "arm_r1"], (0.38, -8, 0, 0, "cin"), (1, -12, 0, 0))
    s.rot("head", (0.38, 12, 0, 0, "cin"), (1, 6, 0, 0))
    s.rot("jaw", (0.38, 34, 0, 0, "cin"), (1, 14, 0, 0))
    for i, b in enumerate(blocks):
        s.pos(b, (0.3 + 0.05 * i, 0, -10, 0, "cin"), (1, 0, -6, 0, "cout"))
    s.scl("core", (0.38, 0.85, "cin"), (1, 1.1))
    # recover: kneeling over its fists, heaving, then it straightens
    for i, u in enumerate((0.15, 0.3, 0.45, 0.6)):
        k.stance(r, u, legs(4, -4), 4.8 + (0.8 if i % 2 else 0), body="body", ease="sine")
        r.rot("body", (u, 30 + (2 if i % 2 else -1), 0, 0, "sine"))
        r.scl("core", (u, 1.15 if i % 2 else 0.95, "sine"))
    k.stance(r, 0.95, legs(0, 0), 0, body="body", ease="sine")
    r.rot("head", (0.3, 22, 0, 0, "sine"), (0.65, 20, 0, 0), (0.9, 0, 0, 0, "sine"))
    r.rots(["arm_l0", "arm_r0"], (0.65, -50, 0, 0), (0.95, 0, 0, 0, "sine"))
    for i, b in enumerate(blocks):
        r.pos(b, (0.5, 0, -6, 0), (0.85 + 0.03 * i, 0, 1, 0, "back"))
    finish("shockwave", w, s, r, C, B)

    # ---- Torn Block: it stoops, tears the front block out of the ground, heaves it overhead and hurls it
    w, s, r = parts(k, wind, rel, 2, 0.4)
    blk = "block2"  # the front-right block
    k.stance(w, 0, legs(0, 0), 0, body=None)
    k.stance(w, 0.28, legs(3, -3), 6.5, body="body", ease="sine")
    k.stance(w, 0.42, legs(3, -3), 6.0, body="body")
    k.stance(w, 0.72, legs(1, -6), 1.0, body="body", ease="cout")
    k.stance(w, 1, legs(1, -6), 1.4, body="body")
    w.rot("body", (0, 0, 0, 0), (0.28, 38, -16, -6, "sine"), (0.42, 40, -18, -6), (0.72, -16, 0, 0, "cout"), (1, -20, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (0.28, -40, 0, -8, "sine"), (0.42, -36, 0, -6), (0.72, -168, 0, -16, "cout"), (1, -172, 0, -18))
    w.rot("arm_r1", (0, 0, 0, 0), (0.28, -10, 0, 0), (0.72, -18, 0, 0), (1, -20, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.28, -34, 0, 10, "sine"), (0.42, -30, 0, 8), (0.72, -168, 0, 16, "cout"), (1, -172, 0, 18))
    w.rot("arm_l1", (0, 0, 0, 0), (0.28, -30, 0, 0), (0.72, -18, 0, 0), (1, -20, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.28, 18, -10, 0, "sine"), (0.72, -24, 0, 0, "cout"), (1, -26, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.3, 10, 0, 0), (0.42, 26, 0, 0, "back"), (0.7, 8, 0, 0), (1, 14, 0, 0))
    w.rot(blk, (0, 0, 0, 0), (1, 0, 0, 0))
    w.pos(blk, (0, 0, 0, 0), (0.28, 2, -22, 4, "sine"), (0.42, 2, -21, 4), (0.74, 17, 38, 15, "cout"), (1, 17, 40, 15))
    w.scl(blk, (0, 1), (0.42, 1.1), (0.74, 1.35, "back"), (1, 1.4))
    w.tremble(blk, "position", 0.3, 0.42, 1.2, 5, (1, 1, 0))
    w.tremble("body", "rotation", 0.75, 1.0, 1.5, 6, (1, 0, 1))
    w.scl("core", (0, 1), (0.42, 1.3, "back"), (1, 1.4))
    for b, d in (("block0", 0), ("block1", 1), ("block3", 2)):
        w.pos(b, (0, 0, 0, 0), (0.5 + 0.06 * d, 0, 6, 0, "sine"), (1, 0, 7, 0))
    k.stance(s, 0.4, legs(9, -7), 3.5, z=-4, body="body", ease="expo")
    k.stance(s, 1, legs(9, -7), 4.0, z=-4, body="body")
    s.rot("body", (0.4, 28, 0, 0, "expo"), (1, 32, 0, 0))
    s.rots(["arm_l0", "arm_r0"], (0.4, -70, 0, 0, "expo"), (1, -40, 0, 0, "cout"))
    s.rots(["arm_l1", "arm_r1"], (0.4, -6, 0, 0), (1, -10, 0, 0))
    s.rot("head", (0.4, 4, 0, 0, "expo"), (1, 10, 0, 0))
    s.rot("jaw", (0.4, 30, 0, 0, "expo"), (1, 12, 0, 0))
    s.pos(blk, (0.3, 17, 44, -4, "in"), (1, 17, 52, -120, "out"))
    s.scl(blk, (0.6, 1.2), (1, 0.01, "cin"))
    s.scl("core", (0.4, 0.9, "expo"), (1, 1.1))
    r.pos(blk, (0.02, 0, 0, 0, "step"))
    r.scl(blk, (0.02, 0.01, "step"), (0.55, 0.01), (0.95, 1, "back"))
    k.stance(r, 0.55, legs(5, -4), 2.0, z=-2, body="body", ease="sine")
    r.rot("body", (0.5, 12, 0, 0, "sine"))
    r.rots(["arm_l0", "arm_r0"], (0.5, -20, 0, 0, "sine"))
    finish("torn_block", w, s, r, C, B)

    # ---- Phase: it falls apart into the arena and rebuilds itself, bigger, with a roar
    p = phase_clip(k)
    k.stance(p, 0, legs(0, 0), 0, body="body")
    k.stance(p, 0.28, legs(2, -2), 7.0, body="body", ease="cin")
    k.stance(p, 0.62, legs(2, -3), 0.5, body="body", ease="back")
    k.stance(p, 0.85, legs(2, -3), 0.8, body="body")
    k.stance(p, 1, legs(0, 0), 0, body="body", ease="sine")
    p.rot("body", (0, 0, 0, 0), (0.28, 26, 0, 8, "cin"), (0.62, -12, 0, 0, "back"), (0.85, -14, 0, 0), (1, 0, 0, 0, "sine"))
    p.scl("body", (0, 1), (0.28, 0.94, "cin"), (0.62, 1.08, "back"), (0.85, 1.08), (1, 1, "sine"))
    p.rot("arm_l0", (0, 0, 0, 0), (0.28, 12, 0, 18, "cin"), (0.62, -40, 0, 72, "back"), (0.85, -44, 0, 76), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.28, 12, 0, -18, "cin"), (0.62, -40, 0, -72, "back"), (0.85, -44, 0, -76), (1, 0, 0, 0, "sine"))
    p.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.28, 8, 0, 0), (0.62, -40, 0, 0), (0.85, -44, 0, 0), (1, 0, 0, 0))
    p.rot("head", (0, 0, 0, 0), (0.28, 34, 0, -10, "cin"), (0.62, -24, 0, 0, "back"), (0.85, -26, 0, 0), (1, 0, 0, 0))
    p.rot("jaw", (0, 0, 0, 0), (0.28, 20, 0, 0), (0.55, 4, 0, 0), (0.68, 36, 0, 0, "back"), (0.85, 34, 0, 0), (1, 0, 0, 0))
    p.scl("core", (0, 1), (0.28, 0.5, "cin"), (0.62, 1.6, "back"), (0.85, 1.5), (1, 1, "sine"))
    for i, b in enumerate(blocks):
        ox, oy, oz = outward(k, b, 16, -24 - 6 * (i % 2))
        p.pos(b, (0, 0, 0, 0), (0.26 + 0.02 * i, ox, oy, oz, "bounce"), (0.42 + 0.04 * i, ox, oy, oz), (0.7 + 0.03 * i, 0, 4, 0, "back"), (1, 0, 0, 0, "sine"))
    p.tremble("body", "rotation", 0.66, 0.85, 1.5, 5, (0, 1, 1))
    C[f"misc.{B}.phase"] = p

    # ---- Death: staggers, its knees give, and it crumbles face first; its blocks drop around it
    d = death_clip(k)
    k.stance(d, 0, legs(0, 0), 0, body=None)
    k.stance(d, 0.2, legs(-1, -6), 1.0, ease="cout")
    k.stance(d, 0.5, legs(4, -2), 9.0, ease="cin")
    k.stance(d, 1, legs(4, -2), 9.5)
    d.pos("body", (0, 0, 0, 0), (0.2, 0, -1, 2, "cout"), (0.5, 0, -9, 0, "cin"), (0.82, 0, -14, -6, "bounce"), (1, 0, -14, -6))
    d.rot("body", (0, 0, 0, 0), (0.2, -12, 0, -6, "cout"), (0.5, 24, 0, 4, "cin"), (0.82, 78, 0, 6, "bounce"), (1, 78, 0, 6))
    d.rot("head", (0, 0, 0, 0), (0.2, -20, 0, 8), (0.5, 20, 0, 0), (0.82, 10, 30, 0, "bounce"), (1, 10, 30, 0))
    d.rot("jaw", (0, 0, 0, 0), (0.5, 20, 0, 0), (1, 28, 0, 0))
    d.rot("arm_l0", (0, 0, 0, 0), (0.2, 10, 0, 40, "cout"), (0.5, -20, 0, 14), (0.82, -150, 0, 30, "bounce"), (1, -150, 0, 30))
    d.rot("arm_r0", (0, 0, 0, 0), (0.2, 10, 0, -40, "cout"), (0.5, -20, 0, -14), (0.82, -120, 0, -40, "bounce"), (1, -120, 0, -40))
    d.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.5, -10, 0, 0), (1, -20, 0, 0))
    d.scl("core", (0, 1), (0.2, 1.3), (0.82, 0.6), (1, 0.4))
    for i, b in enumerate(blocks):
        ox, oy, oz = outward(k, b, 4 + 3 * i, -30 - 8 * (i % 2))
        d.pos(b, (0, 0, 0, 0), (0.35 + 0.08 * i, ox, oy, oz, "bounce"), (1, ox, oy, oz))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["punch", "shockwave", "torn_block"], "clips": C}
