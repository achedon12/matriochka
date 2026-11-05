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


# =============================================================== World 1: Spore Queen
@boss("spore_queen", world=1)
def spore_queen(k, wind, rel):
    C = {}
    B = "spore_queen"
    shins = [(f"shin_{s}{i}", 1 if s == "l" else -1) for s in "lr" for i in range(3)]
    wings_l, wings_r = ["wing_l0", "wing_l1"], ["wing_r0", "wing_r1"]
    abd = ["abdomen0", "abdomen1", "abdomen2"]
    ant = ["antenna_l", "antenna_r"]

    def drop(c, u, d, ease="sine", z=0.0):
        """Lowers (or raises) the body while the stilt legs splay to keep their feet on the ground."""
        a = math.degrees(math.acos(max(-1, min(1, 1 - max(0.0, d) / 21))))
        for sh, sg in shins:
            c.rot(sh, (u, 0, 0, sg * a, ease))
        c.pos("body", (u, 0, -d, z, ease))

    def wings(c, u, y, z, ease="sine", lower=0.7):
        for i, b in enumerate(wings_l):
            c.rot(b, (u, 0, y * (1 if i == 0 else lower), z * (1 if i == 0 else lower), ease))
        for i, b in enumerate(wings_r):
            c.rot(b, (u, 0, -y * (1 if i == 0 else lower), -z * (1 if i == 0 else lower), ease))

    # ---- Root Snare: she rears up on her stilts, scythes high, and drives both into the ground before her
    w, s, r = parts(k, wind, rel, 0, 0.24)
    drop(w, 0, 0)
    drop(w, 1, -2.5, "cout")
    w.rot("body", (0, 0, 0, 0), (0.7, -20, 0, 0, "cout"), (1, -22, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.7, -62, 0, 10, "cout"), (1, -66, 0, 12))
    w.rot("arm_r0", (0, 0, 0, 0), (0.7, -62, 0, -10, "cout"), (1, -66, 0, -12))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.7, -40, 0, 0, "cout"), (1, -44, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.7, 12, 0, 0), (1, 14, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (1, 18, 0, 0, "cout"))
    wings(w, 0, 0, 0)
    wings(w, 1, -14, 10, "cout")
    w.follow(ant, [(0, 0, 0, 0), (0.6, 18, 0, 0), (1, 22, 0, 0)], lag=0.04)
    w.follow(abd, [(0, 0, 0, 0), (1, -8, 0, 0, "sine")], lag=0.05)
    drop(s, 0.45, 3.0, "expo", z=-2)
    drop(s, 1, 2.6, "out", z=-2)
    s.rot("body", (0.45, 18, 0, 0, "expo"), (1, 15, 0, 0))
    s.rot("arm_l0", (0.45, 28, 0, 4, "expo"), (1, 24, 0, 4))
    s.rot("arm_r0", (0.45, 28, 0, -4, "expo"), (1, 24, 0, -4))
    s.rots(["arm_l1", "arm_r1"], (0.45, 26, 0, 0, "expo"), (1, 22, 0, 0))
    s.rot("head", (0.45, 16, 0, 0, "expo"), (1, 12, 0, 0))
    s.rot("jaw", (0.45, 34, 0, 0, "expo"), (1, 10, 0, 0))
    wings(s, 0.45, 18, -6, "expo")
    s.follow(abd, [(0.45, 14, 0, 0, "expo"), (1, 6, 0, 0)], lag=0.03)
    r.rots(["arm_l1", "arm_r1"], (0.25, 40, 0, 0, "inback"))  # pulls the scythes back out
    finish("root_snare", w, s, r, C, B)

    # ---- Toxic Cloud: the egg sac swells and pumps over her back, then bursts its spores as the wings beat
    w, s, r = parts(k, wind, rel, 1, 0.36)
    drop(w, 0, 0)
    drop(w, 0.4, 2.0)
    drop(w, 1, 2.4)
    w.rot("body", (0, 0, 0, 0), (0.4, 8, 0, 0), (1, 10, 0, 0))
    w.follow(abd, [(0, 0, 0, 0), (0.45, 18, 0, 0, "sine"), (1, 26, 0, 0, "sine")], lag=0.08, gain=1.15)
    w.scl("abdomen1", (0, 1), (0.2, 1.08, "sine"), (0.35, 1.0, "sine"), (0.55, 1.16, "sine"), (0.7, 1.06, "sine"), (0.88, 1.24, "sine"), (1, 1.2))
    w.scl("abdomen2", (0, 1), (0.6, 1.1), (1, 1.18))
    wings(w, 0, 0, 0)
    wings(w, 0.5, 40, 0)
    wings(w, 1, 46, 4)
    w.rot("head", (0, 0, 0, 0), (0.5, 16, 0, 0), (1, 18, 0, 0))
    w.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (1, 20, 0, 0, "sine"))
    w.follow(ant, [(0, 0, 0, 0), (1, -20, 0, 0, "sine")], lag=0.05)
    drop(s, 0.35, 0.5, "expo", z=2)
    drop(s, 1, 1.2)
    s.rot("body", (0.35, -10, 0, 0, "expo"), (1, -4, 0, 0))
    s.follow(abd, [(0.3, 46, 0, 0, "expo"), (1, 30, 0, 0)], lag=0.03)
    s.scl("abdomen1", (0.35, 0.82, 1.2, 0.82, "expo"), (1, 0.95, 1, 0.95))
    s.scl("abdomen2", (0.35, 0.8, "expo"), (1, 0.95))
    wings(s, 0.3, -36, 26, "expo")
    wings(s, 1, -20, 18)
    s.rot("head", (0.35, -14, 0, 0, "expo"), (1, -8, 0, 0))
    s.rot("jaw", (0.35, 26, 0, 0, "expo"), (1, 18, 0, 0))
    # recover: she fans the cloud with slow beats while the emptied sac sags
    for i, u in enumerate((0.12, 0.26, 0.4, 0.54, 0.68)):
        wings(r, u, 30 if i % 2 == 0 else -22, 14 if i % 2 == 0 else 4, "sine")
    wings(r, 0.85, 0, 0)
    r.follow(abd, [(0.3, -12, 0, 0, "sine"), (0.75, -10, 0, 0)], lag=0.08)
    drop(r, 0.35, 3.0)
    drop(r, 0.8, 2.6)
    r.rot("head", (0.3, 20, 0, 0), (0.75, 18, 0, 0))
    finish("toxic_cloud", w, s, r, C, B)

    # ---- Call of Sporelings: rearing, wings spread and quivering, she calls with her head thrown back
    # while the sac pulses ever harder, then she slams it down to drop her brood
    w, s, r = parts(k, wind, rel, 2, 0.4)
    drop(w, 0, 0)
    drop(w, 0.3, -3.0, "cout")
    drop(w, 1, -3.4)
    w.rot("body", (0, 0, 0, 0), (0.3, -26, 0, 0, "cout"), (1, -30, 0, 0))
    wings(w, 0, 0, 0)
    wings(w, 0.3, -30, 34, "back")
    wings(w, 1, -32, 38)
    for b in wings_l + wings_r:
        w.tremble(b, "rotation", 0.32, 1.0, 5, 14, (0, 1, 0))
    w.rot("head", (0, 0, 0, 0), (0.35, -28, 0, 0, "cout"), (1, -32, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.35, 36, 0, 0, "back"), (1, 40, 0, 0))
    w.tremble("jaw", "rotation", 0.4, 1.0, 8, 10)
    w.rot("arm_l0", (0, 0, 0, 0), (0.35, -50, 0, 34, "cout"), (1, -54, 0, 38))
    w.rot("arm_r0", (0, 0, 0, 0), (0.35, -50, 0, -34, "cout"), (1, -54, 0, -38))
    w.follow(ant, [(0, 0, 0, 0), (0.35, -30, 0, 0), (1, -34, 0, 0)], lag=0.04)
    for b in ant:
        w.tremble(b, "rotation", 0.4, 1.0, 7, 12, (1, 0, 1))
    w.follow(abd, [(0, 0, 0, 0), (0.35, 22, 0, 0, "cout"), (1, 28, 0, 0)], lag=0.08)
    beats = [(0.4, 1.12), (0.5, 1.0), (0.62, 1.18), (0.72, 1.02), (0.84, 1.26), (0.92, 1.06), (1, 1.32)]
    w.scl("abdomen1", (0, 1), *[(u, v, "sine") for u, v in beats])
    w.scl("abdomen2", (0, 1), *[(u, 1 + (v - 1) * 0.8, "sine") for u, v in beats])
    drop(s, 0.35, 3.5, "cin")
    drop(s, 1, 3.0, "out")
    s.rot("body", (0.35, 14, 0, 0, "cin"), (1, 10, 0, 0))
    s.follow(abd, [(0.3, -34, 0, 0, "cin"), (1, -26, 0, 0, "out")], lag=0.03)
    s.scl("abdomen1", (0.35, 1.25, 0.78, 1.25, "cin"), (1, 1, 1, 1, "back"))
    s.scl("abdomen2", (0.35, 1.2, 0.8, 1.2, "cin"), (1, 1, 1, 1, "back"))
    wings(s, 0.3, 40, 6, "expo")
    wings(s, 1, 24, 6)
    s.rot("head", (0.35, 18, 0, 0, "cin"), (1, 10, 0, 0))
    s.rot("jaw", (0.35, 4, 0, 0, "expo"), (1, 10, 0, 0))
    s.rots(["arm_l0", "arm_r0"], (0.35, 10, 0, 0, "cin"), (1, 6, 0, 0))
    finish("call_of_sporelings", w, s, r, C, B)

    # ---- Phase: she folds her wings around her body into a cocoon and shivers inside it
    p = phase_clip(k)
    drop(p, 0, 0)
    drop(p, 0.3, 5.0, "cio")
    drop(p, 0.85, 5.0)
    drop(p, 1, 0)
    p.rot("body", (0, 0, 0, 0), (0.3, 12, 0, 0, "cio"), (0.85, 12, 0, 0), (1, 0, 0, 0, "sine"))
    for i, b in enumerate(wings_l):
        p.rot(b, (0, 0, 0, 0), (0.32 + 0.05 * i, 0, -78, -10, "cio"), (0.85, 0, -80, -10), (1, 0, 0, 0, "back"))
    for i, b in enumerate(wings_r):
        p.rot(b, (0, 0, 0, 0), (0.32 + 0.05 * i, 0, 78, 10, "cio"), (0.85, 0, 80, 10), (1, 0, 0, 0, "back"))
    for b in wings_l + wings_r + ["body"]:
        p.tremble(b, "rotation", 0.42, 0.85, 3, 10, (0, 0, 1))
    p.rot("head", (0, 0, 0, 0), (0.3, 30, 0, 0, "cio"), (0.85, 30, 0, 0), (1, 0, 0, 0))
    p.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.3, 30, 0, 0), (0.85, 30, 0, 0), (1, 0, 0, 0))
    p.follow(abd, [(0, 0, 0, 0), (0.3, -18, 0, 0, "cio"), (0.85, -18, 0, 0), (1, 0, 0, 0)], lag=0.06)
    p.scl("abdomen1", (0, 1), (0.3, 1.1), (0.5, 1.2), (0.7, 1.1), (0.85, 1.22), (1, 1, "back"))
    C[f"misc.{B}.phase"] = p

    # ---- Death: the stilts give way and splay, she drops on her belly, the wings droop to the ground
    d = death_clip(k)
    drop(d, 0, 0)
    drop(d, 0.2, -1.5, "cout")
    for sh, sg in shins:
        d.rot(sh, (0.55, 0, 0, sg * 80, "bounce"), (1, 0, 0, sg * 80))
    d.pos("body", (0.55, 0, -10, 0, "bounce"), (1, 0, -10, 0))
    d.rot("body", (0, 0, 0, 0), (0.2, -16, 0, 0, "cout"), (0.55, 6, 0, 10, "bounce"), (1, 6, 0, 10))
    d.rot("head", (0, 0, 0, 0), (0.2, -30, 0, 0), (0.6, 36, 0, 18, "bounce"), (1, 36, 0, 18))
    d.rot("jaw", (0, 0, 0, 0), (0.6, 24, 0, 0), (1, 24, 0, 0))
    for i, b in enumerate(wings_l):
        d.rot(b, (0, 0, 0, 0), (0.2, 0, -20, 30), (0.65 + 0.06 * i, 0, 30, -50, "bounce"), (1, 0, 30, -50))
    for i, b in enumerate(wings_r):
        d.rot(b, (0, 0, 0, 0), (0.2, 0, 20, -30), (0.65 + 0.06 * i, 0, -30, 50, "bounce"), (1, 0, -30, 50))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.2, -40, 0, 0), (0.6, 30, 0, 0, "bounce"), (1, 30, 0, 0))
    d.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.6, 40, 0, 0), (1, 40, 0, 0))
    d.follow(abd, [(0, 0, 0, 0), (0.2, 10, 0, 0), (0.6, -14, 0, 0, "bounce"), (1, -14, 0, 0)], lag=0.06)
    d.follow(ant, [(0, 0, 0, 0), (0.6, 50, 0, 0, "bounce"), (1, 50, 0, 0)], lag=0.05)
    C[f"misc.{B}.death"] = d
    return {"slugs": ["root_snare", "toxic_cloud", "call_of_sporelings"], "clips": C}


# =============================================================== World 2: Ash Titan
@boss("ash_titan", world=2)
def ash_titan(k, wind, rel):
    C = {}
    B = "ash_titan"
    legs = lambda fl, fr, ll=0, lr=0: [("leg_l0", "leg_l1", fl, ll), ("leg_r0", "leg_r1", fr, lr)]

    # ---- Hammer Blow: the beam hammer swings up over the right shoulder and chops down diagonally
    w, s, r = parts(k, wind, rel, 0, 0.26)
    k.stance(w, 0, legs(0, 0), 0, body="body")
    k.stance(w, 1, legs(6, -3), 2.0, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (0.7, -8, -22, 4, "cout"), (1, -10, -26, 4))
    w.rot("arm_r0", (0, 0, 0, 0), (0.7, -150, 0, -22, "cout"), (1, -158, 0, -24))
    w.rot("arm_r1", (0, 0, 0, 0), (0.7, -40, 0, 0), (1, -46, 0, 0))
    w.rot("hammer", (0, 0, 0, 0), (0.7, 34, 0, 0, "cout"), (1, 40, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.7, -36, 0, 10), (1, -40, 0, 12))
    w.rot("arm_l1", (0, 0, 0, 0), (1, -30, 0, 0))
    w.rot("head", (0, 0, 0, 0), (1, 6, 20, 0))
    w.scl("heart", (0, 1), (1, 1.15))
    k.stance(s, 0.45, legs(8, -4), 5.0, z=-3, body="body", ease="expo")
    k.stance(s, 1, legs(8, -4), 4.5, z=-3, body="body")
    s.rot("body", (0.45, 22, 18, -4, "expo"), (1, 20, 14, -2))
    s.rot("arm_r0", (0.45, -38, 0, 6, "expo"), (1, -30, 0, 4))
    s.rot("arm_r1", (0.45, -8, 0, 0, "expo"), (1, -6, 0, 0))
    s.rot("hammer", (0.45, -26, 0, 0, "expo"), (1, -18, 0, 0))
    s.rot("arm_l0", (0.45, 10, 0, 20, "expo"), (1, 6, 0, 16))
    s.rot("head", (0.45, 10, -10, 0, "expo"), (1, 8, -8, 0))
    s.rot("jaw", (0, 0, 0, 0), (0.45, 22, 0, 0, "expo"), (1, 10, 0, 0))
    s.scl("heart", (0.45, 1.3, "expo"), (1, 1.1))
    finish("hammer_blow", w, s, r, C, B)

    # ---- Ash Spray: the left hand digs into the furnace in its chest, then flings the burning ash ahead
    w, s, r = parts(k, wind, rel, 1, 0.34)
    k.stance(w, 0, legs(0, 0), 0, body="body")
    k.stance(w, 1, legs(-2, 4), 2.5, body="body")
    w.rot("body", (0, 0, 0, 0), (0.5, -10, 18, 0, "sine"), (1, -14, 24, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.45, -64, 0, -34, "cout"), (1, -70, 0, -40))
    w.rot("arm_l1", (0, 0, 0, 0), (0.45, -80, 0, 0, "cout"), (1, -86, 0, 0))
    w.tremble("arm_l1", "rotation", 0.55, 1.0, 4, 7)
    w.rot("arm_r0", (0, 0, 0, 0), (1, 14, 0, -16, "sine"))
    w.rot("head", (0, 0, 0, 0), (0.6, -22, -10, 0, "sine"), (1, -26, -12, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.6, 24, 0, 0), (1, 30, 0, 0))
    w.scl("heart", (0, 1), (0.3, 1.15), (0.45, 1.0), (0.65, 1.25), (0.8, 1.1), (1, 1.4))
    k.stance(s, 0.4, legs(4, -2), 3.0, z=-2, body="body", ease="expo")
    k.stance(s, 1, legs(4, -2), 3.0, z=-2, body="body")
    s.rot("body", (0.4, 14, -26, 0, "expo"), (1, 12, -22, 0))
    s.rot("arm_l0", (0.4, -104, 0, 42, "expo"), (1, -96, 0, 50))
    s.rot("arm_l1", (0.4, -6, 0, 0, "expo"), (1, -4, 0, 0))
    s.rot("arm_r0", (0.4, 20, 0, -20, "expo"), (1, 16, 0, -18))
    s.rot("head", (0.4, 16, 8, 0, "expo"), (1, 12, 8, 0))
    s.rot("jaw", (0.4, 42, 0, 0, "expo"), (1, 36, 0, 0))
    s.scl("heart", (0.4, 0.85, "expo"), (1, 1.0))
    # recover: it coughs ash, the jaw working, the arm hanging spent
    for i, u in enumerate((0.1, 0.2, 0.3, 0.42, 0.52)):
        r.rot("head", (u, 22 if i % 2 == 0 else 4, 0, 0, "sine"))
        r.rot("jaw", (u, 34 if i % 2 == 0 else 8, 0, 0, "sine"))
        r.rot("body", (u, 18 if i % 2 == 0 else 10, -6, 0, "sine"))
    r.rot("arm_l0", (0.25, 12, 0, 14, "sine"), (0.7, 10, 0, 12))
    r.rot("arm_l1", (0.25, -10, 0, 0))
    r.scl("heart", (0.3, 0.8, "sine"), (0.7, 0.9))
    finish("ash_spray", w, s, r, C, B)

    # ---- Rising Lava: both hands lift the hammer high, the forge in its chest beats harder, and it drives
    # the anvil head into the ground
    w, s, r = parts(k, wind, rel, 2, 0.42)
    k.stance(w, 0, legs(0, 0), 0, body="body")
    k.stance(w, 0.25, legs(3, -3), 4.5, body="body", ease="sine")
    k.stance(w, 0.7, legs(4, -4), 0.8, body="body", ease="cout")
    k.stance(w, 1, legs(4, -4), 1.0, body="body")
    w.rot("body", (0, 0, 0, 0), (0.25, 14, 0, 0, "sine"), (0.7, -16, 0, 0, "cout"), (1, -20, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (0.25, -30, 0, 0, "sine"), (0.7, -166, 0, -12, "cout"), (1, -172, 0, -14))
    w.rot("arm_l0", (0, 0, 0, 0), (0.25, -40, 0, -20, "sine"), (0.7, -166, 0, 14, "cout"), (1, -172, 0, 16))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.7, -26, 0, 0), (1, -30, 0, 0))
    w.rot("hammer", (0, 0, 0, 0), (0.7, 52, 0, 0, "cout"), (1, 60, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.25, 10, 0, 0), (0.7, -26, 0, 0, "cout"), (1, -30, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.7, 18, 0, 0), (1, 40, 0, 0, "cout"))
    w.scl("heart", (0, 1), (0.3, 1.15, "sine"), (0.4, 1.0), (0.55, 1.25, "sine"), (0.65, 1.05), (0.8, 1.38, "sine"), (0.88, 1.1), (1, 1.5, "sine"))
    w.tremble("body", "rotation", 0.75, 1.0, 1.4, 6, (0, 1, 1))
    k.stance(s, 0.38, legs(5, -5), 8.0, z=-2, body="body", ease="cin")
    k.stance(s, 1, legs(5, -5), 7.0, z=-2, body="body", ease="out")
    s.rot("body", (0.38, 38, 0, 0, "cin"), (1, 34, 0, 0))
    s.scl("body", (0, 1), (0.38, 1.04, 0.95, 1.04, "cin"), (1, 1, 1, 1, "out"))
    s.rot("arm_r0", (0.38, -46, 0, 8, "cin"), (1, -44, 0, 6))
    s.rot("arm_l0", (0.38, -50, 0, -10, "cin"), (1, -48, 0, -8))
    s.rots(["arm_l1", "arm_r1"], (0.38, -10, 0, 0), (1, -12, 0, 0))
    s.rot("hammer", (0.38, -20, 0, 0, "cin"), (1, -16, 0, 0))
    s.rot("head", (0.38, 6, 0, 0, "cin"), (1, -6, 0, 0))
    s.rot("jaw", (0.38, 48, 0, 0, "cin"), (1, 40, 0, 0))
    s.scl("heart", (0.38, 0.8, "cin"), (0.6, 1.4, "back"), (1, 1.2))
    k.stance(r, 0.4, legs(5, -5), 6.0, z=-2, body="body", ease="sine")
    r.rot("hammer", (0.35, 10, 0, 0, "inback"))  # wrenches it out of the ground
    r.rot("body", (0.4, 24, 0, 0, "sine"))
    finish("rising_lava", w, s, r, C, B)

    # ---- Phase: the armour melts open; it throws its arms back and roars, the heart blazing
    p = phase_clip(k)
    k.stance(p, 0, legs(0, 0), 0, body="body")
    k.stance(p, 0.2, legs(-3, -6), 2.0, body="body", ease="cout")
    k.stance(p, 0.45, legs(6, -6), 3.0, body="body", ease="sine")
    k.stance(p, 0.85, legs(6, -6), 3.0, body="body")
    k.stance(p, 1, legs(0, 0), 0, body="body", ease="sine")
    p.rot("body", (0, 0, 0, 0), (0.2, 10, 0, 0, "cout"), (0.45, -22, 0, 0, "back"), (0.85, -24, 0, 0), (1, 0, 0, 0, "sine"))
    p.rot("arm_l0", (0, 0, 0, 0), (0.2, -50, 0, -20), (0.45, 24, 0, 62, "back"), (0.85, 26, 0, 66), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.2, -50, 0, 20), (0.45, 24, 0, -62, "back"), (0.85, 26, 0, -66), (1, 0, 0, 0, "sine"))
    p.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.2, -60, 0, 0), (0.45, -30, 0, 0), (0.85, -34, 0, 0), (1, 0, 0, 0))
    p.rot("head", (0, 0, 0, 0), (0.2, 20, 0, 0), (0.45, -34, 0, 0, "back"), (0.85, -36, 0, 0), (1, 0, 0, 0))
    p.rot("jaw", (0, 0, 0, 0), (0.3, 0, 0, 0), (0.45, 52, 0, 0, "back"), (0.85, 50, 0, 0), (1, 0, 0, 0))
    p.tremble("jaw", "rotation", 0.5, 0.85, 6, 8)
    p.scl("heart", (0, 1), (0.2, 0.8), (0.45, 1.7, "back"), (0.55, 1.45), (0.65, 1.75), (0.75, 1.5), (0.85, 1.7), (1, 1, "sine"))
    C[f"misc.{B}.phase"] = p

    # ---- Death: it lets the hammer fall, drops to its knees and topples backwards, the forge going out
    d = death_clip(k)
    k.stance(d, 0, legs(0, 0), 0, body=None)
    k.stance(d, 0.25, legs(3, -2), 3.0, ease="sine")
    k.stance(d, 0.5, legs(6, 2), 11.0, ease="bounce")
    k.stance(d, 1, legs(6, 2), 11.5)
    d.pos("body", (0, 0, 0, 0), (0.25, 0, -3, 0), (0.5, 0, -11, 0, "bounce"), (0.85, 0, -15, 8, "bounce"), (1, 0, -15, 8))
    d.rot("body", (0, 0, 0, 0), (0.25, 14, 0, 0), (0.5, 6, 0, 0, "bounce"), (0.85, -72, 0, -6, "bounce"), (1, -72, 0, -6))
    d.rot("arm_r1", (0, 0, 0, 0), (0.2, 20, 0, 0))
    d.rot("hammer", (0, 0, 0, 0), (0.2, 40, 0, 0, "cin"), (0.35, 80, 0, 30, "bounce"), (1, 80, 0, 30))
    d.pos("hammer", (0, 0, 0, 0), (0.35, 0, -6, 0, "bounce"), (1, 0, -6, 0))
    d.rot("arm_l0", (0, 0, 0, 0), (0.5, 10, 0, 20), (0.85, -150, 0, 40, "bounce"), (1, -150, 0, 40))
    d.rot("arm_r0", (0, 0, 0, 0), (0.5, 10, 0, -20), (0.85, -150, 0, -40, "bounce"), (1, -150, 0, -40))
    d.rot("head", (0, 0, 0, 0), (0.5, 20, 0, 0), (0.9, -20, 20, 0, "bounce"), (1, -20, 20, 0))
    d.rot("jaw", (0, 0, 0, 0), (0.5, 30, 0, 0), (1, 34, 0, 0))
    d.scl("heart", (0, 1), (0.15, 1.3), (0.3, 1.0), (0.45, 1.15), (0.7, 0.8), (1, 0.45))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["hammer_blow", "ash_spray", "rising_lava"], "clips": C}


# =============================================================== World 3: Grand Jailer
@boss("grand_jailer", world=3)
def grand_jailer(k, wind, rel):
    C = {}
    B = "grand_jailer"
    chain = [f"chain{i}" for i in range(6)]
    back = [f"backchain_l{i}" for i in range(5)]
    robe = ["robe0", "robe1"]
    keys = [f"orbit{i}" for i in range(4)]

    # ---- Chain Pull: the chain in its left hand swings back, lashes out ahead, and is hauled in
    w, s, r = parts(k, wind, rel, 0, 0.26)
    w.rot("body", (0, 0, 0, 0), (1, -4, 22, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.7, 46, 0, 22, "cout"), (1, 52, 0, 24))
    w.rot("arm_l1", (0, 0, 0, 0), (1, -24, 0, 0))
    w.follow(chain, [(0, 0, 0, 0), (0.6, -30, 0, 8), (1, -36, 0, 10)], lag=0.04, gain=1.1)
    w.rot("head", (0, 0, 0, 0), (1, 10, -18, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (1, -18, 0, -6))
    w.follow(robe, [(0, 0, 0, 0), (1, 6, 0, -4)], lag=0.06)
    s.rot("body", (0.4, 12, -22, 0, "expo"), (1, -8, 6, 0, "inback"))
    s.rot("arm_l0", (0.4, -112, 0, 6, "expo"), (1, -40, 0, 16, "inback"))
    s.rot("arm_l1", (0.4, -4, 0, 0, "expo"), (1, -60, 0, 0))
    s.follow(chain, [(0.3, 40, 0, 0, "expo"), (0.65, -30, 0, 0), (1, 30, 0, 0)], lag=0.03, gain=1.15)
    s.rot("head", (0.4, 16, 0, 0, "expo"), (1, 0, 8, 0))
    s.follow(robe, [(0.4, -10, 0, 4, "expo"), (1, 6, 0, -2)], lag=0.04)
    r.follow(chain, [(0.2, -24, 0, 0, "sine"), (0.45, 14, 0, 0, "sine"), (0.7, -6, 0, 0, "sine")], lag=0.04)
    finish("chain_pull", w, s, r, C, B)

    # ---- Floor Cage: the key-staff rises high, the keys whirl, and its butt is struck on the floor
    w, s, r = parts(k, wind, rel, 1, 0.32)
    w.pos("body", (0, 0, 0, 0), (0.6, 0, 3, 0, "cout"), (1, 0, 3.5, 0))
    w.rot("body", (0, 0, 0, 0), (0.6, -8, 0, 0, "cout"), (1, -10, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, -128, 0, -10, "cout"), (1, -134, 0, -12))
    w.rot("arm_r1", (0, 0, 0, 0), (0.6, -20, 0, 0), (1, -24, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -40, 0, 30, "cout"), (1, -44, 0, 34))
    w.rot("head", (0, 0, 0, 0), (0.6, -16, 0, 0, "cout"), (1, -18, 0, 0))
    for i, b in enumerate(keys):
        w.rot(b, (0, 0, 0, 0), (1, 0, 540 if i % 2 == 0 else -540, 0, "cin"))
        w.scl(b, (0, 1), (1, 1.35, "cout"))
    w.follow(robe, [(0, 0, 0, 0), (0.6, -10, 0, 0, "sine"), (0.8, 6, 0, 0, "sine"), (1, -8, 0, 0)], lag=0.08)
    w.follow(chain, [(0, 0, 0, 0), (0.5, 14, 0, 0), (1, -10, 0, 0)], lag=0.05)
    w.scl("soul", (0, 1), (1, 1.3))
    s.pos("body", (0.4, 0, -1.5, -1, "cin"), (1, 0, -1, -1))
    s.rot("body", (0.4, 16, 0, 0, "cin"), (1, 12, 0, 0))
    s.rot("arm_r0", (0.4, -36, 0, -4, "cin"), (1, -34, 0, -4))
    s.rot("arm_r1", (0.4, -4, 0, 0, "cin"))
    s.rot("arm_l0", (0.4, 8, 0, 20, "cin"), (1, 4, 0, 16))
    s.rot("head", (0.4, 14, 0, 0, "cin"), (1, 10, 0, 0))
    for i, b in enumerate(keys):
        s.rot(b, (1, 0, 720 if i % 2 == 0 else -720, 0, "cout"))
        s.scl(b, (0.4, 0.7, "cin"), (1, 0.9))
    s.follow(robe, [(0.4, 14, 0, 0, "cin"), (1, -6, 0, 0)], lag=0.04)
    s.scl("soul", (0.4, 0.8, "cin"), (1, 1.1))
    # recover: it leans on the planted staff, head bowed, chains and lantern swinging
    r.rot("body", (0.2, 18, 0, 0, "sine"), (0.7, 16, 0, 0))
    r.rot("head", (0.2, 26, 0, 0, "sine"), (0.7, 24, 0, 0))
    r.follow(["lantern"], [(0.15, 18, 0, 0, "sine"), (0.35, -14, 0, 0, "sine"), (0.55, 8, 0, 0, "sine")], lag=0.02)
    r.follow(chain, [(0.15, 20, 0, 0, "sine"), (0.4, -14, 0, 0, "sine"), (0.65, 6, 0, 0, "sine")], lag=0.05)
    for b in keys:
        r.rot(b, (1, 0, 720 if b in ("orbit0", "orbit2") else -720, 0, "sine"))
    finish("floor_cage", w, s, r, C, B)

    # ---- Moving Walls: arms spread like opening doors, robe billowing, keys flung wide; then the arms swing
    # shut before it like two walls closing
    w, s, r = parts(k, wind, rel, 2, 0.4)
    w.pos("body", (0, 0, 0, 0), (0.4, 0, 4, 0, "sine"), (1, 0, 5, 0))
    w.rot("body", (0, 0, 0, 0), (0.4, -12, 0, 0, "sine"), (0.6, -12, 10, 0, "sine"), (0.8, -12, -10, 0, "sine"), (1, -14, 0, 0, "sine"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.4, -30, 0, 78, "cout"), (1, -34, 0, 84))
    w.rot("arm_r0", (0, 0, 0, 0), (0.4, -30, 0, -78, "cout"), (1, -34, 0, -84))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.4, -16, 0, 0), (1, -18, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.4, -22, 0, 0, "sine"), (1, -26, 0, 0))
    for i, b in enumerate(keys):
        ox, oy, oz = outward(k, b, 10, 6)
        w.pos(b, (0, 0, 0, 0), (0.45 + 0.05 * i, ox, oy, oz, "back"), (1, ox, oy + 1, oz))
        w.scl(b, (0, 1), (0.5, 1.5, "back"), (1, 1.6))
    for i, u in enumerate((0.2, 0.35, 0.5, 0.65, 0.8, 0.95)):
        w.follow(robe, [(u, -14 if i % 2 == 0 else 8, 0, 6 if i % 2 == 0 else -6, "sine")], lag=0.08)
    w.scl("soul", (0, 1), (0.5, 1.3), (0.7, 1.15), (1, 1.45))
    w.tremble("arm_l0", "rotation", 0.7, 1.0, 3, 6, (0, 0, 1))
    w.tremble("arm_r0", "rotation", 0.7, 1.0, 3, 6, (0, 0, 1))
    s.pos("body", (0.4, 0, 0, -2, "cin"), (1, 0, 0.5, -2))
    s.rot("body", (0.4, 18, 0, 0, "cin"), (1, 14, 0, 0))
    s.rot("arm_l0", (0.4, -74, 0, -24, "cin"), (1, -70, 0, -20))
    s.rot("arm_r0", (0.4, -74, 0, 24, "cin"), (1, -70, 0, 20))
    s.rots(["arm_l1", "arm_r1"], (0.4, -6, 0, 0))
    s.rot("head", (0.4, 16, 0, 0, "cin"), (1, 12, 0, 0))
    for b in keys:
        s.pos(b, (0.4, 0, 0, 0, "cin"))
        s.scl(b, (0.4, 0.5, "cin"), (1, 0.8, "back"))
    s.follow(robe, [(0.4, 18, 0, 0, "cin"), (1, -8, 0, 0)], lag=0.04)
    s.scl("soul", (0.4, 0.7, "cin"), (1, 1.0))
    finish("moving_walls", w, s, r, C, B)

    # ---- Phase: the arena becomes a cell; it thrusts the key-staff forward and turns it like a key in a lock
    p = phase_clip(k)
    p.rot("body", (0, 0, 0, 0), (0.25, 10, 0, 0, "cout"), (0.6, 14, -20, 0, "sine"), (0.85, 14, -20, 0), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.25, -92, 0, 0, "cout"), (0.6, -92, 0, 90, "cio"), (0.85, -92, 0, 92), (1, 0, 0, 0, "sine"))
    p.rot("arm_r1", (0, 0, 0, 0), (0.25, -4, 0, 0))
    p.rot("arm_l0", (0, 0, 0, 0), (0.3, -70, 0, -10, "cout"), (0.85, -70, 0, -10), (1, 0, 0, 0, "sine"))
    p.rot("head", (0, 0, 0, 0), (0.25, 8, 0, 0), (0.6, 10, 0, 16, "sine"), (0.85, 10, 0, 16), (1, 0, 0, 0))
    for i, b in enumerate(keys):
        p.rot(b, (0, 0, 0, 0), (0.6, 0, 0, 0), (0.85, 0, 360 if i % 2 == 0 else -360, 0, "cio"), (1, 0, 360 if i % 2 == 0 else -360, 0))
    p.scl("soul", (0, 1), (0.6, 1.0), (0.7, 1.5, "back"), (0.85, 1.3), (1, 1, "sine"))
    p.tremble("arm_l1", "rotation", 0.3, 0.85, 5, 10)
    p.follow(chain, [(0, 0, 0, 0), (0.4, 16, 0, 10), (0.6, -16, 0, -10), (0.8, 10, 0, 6), (1, 0, 0, 0)], lag=0.04)
    p.follow(back, [(0, 0, 0, 0), (0.62, 0, 0, 0), (0.7, 20, 0, 10), (0.85, -10, 0, -6), (1, 0, 0, 0)], lag=0.03)
    C[f"misc.{B}.phase"] = p

    # ---- Death: the robe empties and settles, the staff topples, and the prisoner's soul rises free
    d = death_clip(k)
    d.pos("body", (0, 0, 0, 0), (0.3, 0, 1.5, 0, "cout"), (0.75, 0, -9, 0, "cin"), (1, 0, -10, 0, "bounce"))
    d.rot("body", (0, 0, 0, 0), (0.3, -10, 0, 0, "cout"), (0.75, 34, 0, 8, "cin"), (1, 40, 0, 8, "bounce"))
    d.scl("robe1", (0, 1), (0.75, 1.15, 0.55, 1.15, "cin"), (1, 1.2, 0.45, 1.2))
    d.rot("head", (0, 0, 0, 0), (0.3, -24, 0, 0), (0.8, 40, 0, 10, "bounce"), (1, 40, 0, 10))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.3, -30, 0, 0), (0.8, 20, 0, 0, "bounce"), (1, 20, 0, 0))
    d.rot("keystaff", (0, 0, 0, 0), (0.3, 0, 0, 0), (0.7, 70, 0, -30, "bounce"), (1, 70, 0, -30))
    d.pos("soul", (0, 0, 0, 0), (0.4, 0, 2, 0), (1, 0, 22, -2, "cout"))
    d.scl("soul", (0, 1), (0.5, 1.6, "back"), (1, 0.01, "cin"))
    for i, b in enumerate(keys):
        ox, oy, oz = outward(k, b, 4, -26)
        d.pos(b, (0, 0, 0, 0), (0.4 + 0.08 * i, ox, oy, oz, "bounce"), (1, ox, oy, oz))
    d.rot("lantern", (0, 0, 0, 0), (0.6, 60, 0, 20, "bounce"), (1, 60, 0, 20))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["chain_pull", "floor_cage", "moving_walls"], "clips": C}


# =============================================================== World 4: Storm King
@boss("storm_king", world=4)
def storm_king(k, wind, rel):
    C = {}
    B = "storm_king"
    funnel = [f"funnel{i}" for i in range(4)]
    cape = ["cape0", "cape1"]
    clouds = [f"cloudlet{i}" for i in range(3)]

    def wings(c, u, y, z, ease="sine"):
        c.rot("wing_l", (u, 0, y, z, ease))
        c.rot("wing_r", (u, 0, -y, -z, ease))

    # ---- Gust: wings drawn back and high, then clapped forward in one beat that throws the air ahead
    w, s, r = parts(k, wind, rel, 0, 0.22)
    wings(w, 0, 0, 0)
    wings(w, 1, 46, 24, "cout")
    w.rot("body", (0, 0, 0, 0), (1, -14, 0, 0, "cout"))
    w.pos("body", (0, 0, 0, 0), (1, 0, 2, 2, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (1, 30, 0, 30, "cout"))
    w.rot("head", (0, 0, 0, 0), (1, -10, 0, 0))
    w.follow(cape, [(0, 0, 0, 0), (1, 14, 0, 0)], lag=0.04)
    w.follow(funnel, [(0, 0, 0, 0), (1, -12, 0, 0)], lag=0.04)
    wings(s, 0.45, -60, 4, "expo")
    wings(s, 1, -44, 2)
    s.rot("body", (0.45, 16, 0, 0, "expo"), (1, 12, 0, 0))
    s.pos("body", (0.45, 0, -1, -3, "expo"), (1, 0, -1, -2))
    s.rot("arm_l0", (0.45, -90, 0, 0, "expo"), (1, -84, 0, 4))
    s.rot("arm_l1", (0.45, -10, 0, 0))
    s.rot("head", (0.45, 8, 0, 0, "expo"))
    s.follow(cape, [(0.45, -20, 0, 0, "expo"), (1, -10, 0, 0)], lag=0.03)
    s.follow(funnel, [(0.45, 22, 0, 0, "expo"), (1, 12, 0, 0)], lag=0.03)
    s.scl("orb", (0.45, 1.5, "expo"), (1, 1.2))
    finish("gust", w, s, r, C, B)

    # ---- Called Lightning: the trident is raised to the sky, crackling, then pointed down at the target
    w, s, r = parts(k, wind, rel, 1, 0.3)
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, -170, 0, -10, "cout"), (1, -176, 0, -12))
    w.rot("arm_r1", (0, 0, 0, 0), (0.6, -10, 0, 0))
    w.tremble("arm_r0", "rotation", 0.6, 1.0, 3, 8, (1, 0, 1))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -20, 0, 52, "cout"), (1, -24, 0, 56))
    w.rot("head", (0, 0, 0, 0), (0.6, -26, 0, 0, "cout"), (1, -30, 0, 0))
    w.rot("body", (0, 0, 0, 0), (0.6, -8, 0, 0), (1, -10, 0, 0))
    w.pos("body", (0, 0, 0, 0), (1, 0, 3, 0, "sine"))
    wings(w, 0, 0, 0)
    wings(w, 0.6, -10, 30, "cout")
    wings(w, 1, -12, 34)
    w.follow(funnel, [(0, 0, 0, 0), (1, 0, 220, 0, "cin")], lag=0.05, gain=1.2)
    w.scl("orb", (0, 1), (1, 1.35))
    w.rot("jaw", (0, 0, 0, 0), (1, 10, 0, 0))
    s.rot("arm_r0", (0.45, -66, 0, 0, "expo"), (1, -72, 0, -2))
    s.rot("arm_r1", (0.45, -2, 0, 0))
    s.rot("body", (0.45, 20, 0, 0, "expo"), (1, 16, 0, 0))
    s.rot("head", (0.45, 12, 0, 0, "expo"), (1, 8, 0, 0))
    s.pos("body", (0.45, 0, 1, -2, "expo"))
    wings(s, 0.45, 30, 10, "expo")
    s.follow(funnel, [(1, 0, 300, 0, "out")], lag=0.03)
    s.follow(cape, [(0.45, -16, 0, 0, "expo"), (1, -8, 0, 0)], lag=0.03)
    s.rot("jaw", (0.45, 18, 0, 0, "expo"))
    # recover: it hovers with the trident lowered, wings beating slowly
    for i, u in enumerate((0.2, 0.4, 0.6, 0.8)):
        wings(r, u, 20 if i % 2 == 0 else -10, 14 if i % 2 == 0 else -4, "sine")
        r.pos("body", (u, 0, 2 if i % 2 == 0 else -1, 0, "sine"))
    r.rot("arm_r0", (0.3, -30, 0, -6, "sine"), (0.7, -24, 0, -6))
    r.follow(funnel, [(1, 0, 360, 0, "sine")], lag=0.04)
    finish("called_lightning", w, s, r, C, B)

    # ---- Shattered Islet: it rises high, wings spread, both fists joined over its crown with the orb blazing,
    # then dives and hammers the islet apart
    w, s, r = parts(k, wind, rel, 2, 0.36)
    w.pos("body", (0, 0, 0, 0), (0.25, 0, -2, 0, "sine"), (0.7, 0, 11, 0, "cout"), (1, 0, 12, 0))
    w.rot("body", (0, 0, 0, 0), (0.25, 8, 0, 0), (0.7, -14, 0, 0, "cout"), (1, -16, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.25, 20, 0, 10), (0.7, -168, 0, 14, "cout"), (1, -172, 0, 16))
    w.rot("arm_r0", (0, 0, 0, 0), (0.25, 20, 0, -10), (0.7, -168, 0, -14, "cout"), (1, -172, 0, -16))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.7, -20, 0, 0), (1, -24, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.7, -24, 0, 0, "cout"), (1, -28, 0, 0))
    wings(w, 0, 0, 0)
    wings(w, 0.25, 30, -10)
    wings(w, 0.7, -20, 40, "back")
    wings(w, 1, -22, 44)
    w.scl("orb", (0, 1), (0.5, 1.3), (0.75, 1.6, "back"), (1, 1.75))
    w.follow(funnel, [(0, 0, 0, 0), (1, 0, 540, 0, "cin")], lag=0.05)
    w.scl("funnel0", (0, 1), (1, 0.9, 1.25, 0.9, "sine"))  # the children stretch with it
    w.follow(cape, [(0, 0, 0, 0), (0.5, 20, 0, 0, "sine"), (0.75, 6, 0, 0, "sine"), (1, 22, 0, 0)], lag=0.06)
    w.tremble("body", "rotation", 0.7, 1.0, 2, 8, (0, 0, 1))
    for i, b in enumerate(clouds):
        w.pos(b, (0, 0, 0, 0), (1, 0, -4 - i, 0, "sine"))
    s.pos("body", (0.4, 0, -3, -4, "cin"), (1, 0, -2, -4))
    s.rot("body", (0.4, 34, 0, 0, "cin"), (1, 28, 0, 0))
    s.rots(["arm_l0", "arm_r0"], (0.4, -44, 0, 0, "cin"), (1, -40, 0, 0))
    s.rot("arm_l0", (0.4, -44, 0, -8, "cin"))
    s.rot("arm_r0", (0.4, -44, 0, 8, "cin"))
    s.rot("head", (0.4, 12, 0, 0, "cin"))
    wings(s, 0.4, 70, -10, "cin")
    wings(s, 1, 60, -6)
    s.scl("orb", (0.4, 0.8, "cin"), (1, 1.1))
    s.follow(funnel, [(1, 0, 720, 0, "out")], lag=0.03)
    s.scl("funnel0", (0.4, 1.2, 0.8, 1.2, "cin"), (1, 1, 1, 1))
    s.follow(cape, [(0.4, -30, 0, 0, "cin"), (1, -20, 0, 0)], lag=0.03)
    r.follow(funnel, [(1, 0, 720, 0, "sine")], lag=0.02)
    finish("shattered_islet", w, s, r, C, B)

    # ---- Phase: a whirlwind; it spins twice on its funnel with arms flung wide and roars from its beard
    p = phase_clip(k)
    p.rot("body", (0, 0, 0, 0), (0.15, 6, -20, 0, "sine"), (0.75, -8, 720, 0, "cio"), (1, 0, 720, 0, "sine"))
    p.pos("body", (0, 0, 0, 0), (0.4, 0, 6, 0, "sine"), (0.8, 0, 6, 0), (1, 0, 0, 0, "sine"))
    p.rot("arm_l0", (0, 0, 0, 0), (0.3, -10, 0, 86, "cout"), (0.75, -10, 0, 88), (0.88, -150, 0, 20, "back"), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.3, -10, 0, -86, "cout"), (0.75, -10, 0, -88), (0.88, -150, 0, -20, "back"), (1, 0, 0, 0, "sine"))
    wings(p, 0, 0, 0)
    wings(p, 0.3, -24, 44, "cout")
    wings(p, 0.88, -30, 50)
    wings(p, 1, 0, 0)
    p.rot("head", (0, 0, 0, 0), (0.75, 0, 0, 0), (0.88, -34, 0, 0, "back"), (1, 0, 0, 0))
    p.rot("jaw", (0, 0, 0, 0), (0.75, 0, 0, 0), (0.88, 26, 0, 0, "back"), (1, 0, 0, 0))
    p.follow(funnel, [(0, 0, 0, 0), (0.75, 0, -300, 0, "cio"), (1, 0, -360, 0, "sine")], lag=0.04)
    p.follow(cape, [(0, 0, 0, 0), (0.3, 40, 0, 10), (0.75, 40, 0, -10), (1, 0, 0, 0)], lag=0.05)
    p.scl("orb", (0, 1), (0.88, 1.8, "back"), (1, 1))
    C[f"misc.{B}.phase"] = p

    # ---- Death: the storm leaves it; wings fold, the funnel unravels and it spirals down
    d = death_clip(k)
    d.rot("body", (0, 0, 0, 0), (0.2, -16, 0, 0, "cout"), (1, 50, -400, 30, "cin"))
    d.pos("body", (0, 0, 0, 0), (0.2, 0, 3, 0, "cout"), (1, 0, -20, 0, "cin"))
    wings(d, 0, 0, 0)
    wings(d, 0.2, -20, 40)
    wings(d, 1, 70, -40, "cin")
    d.rot("head", (0, 0, 0, 0), (0.2, -30, 0, 0), (1, 30, 0, 20))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.2, -60, 0, 0), (1, -150, 0, 0, "cin"))
    d.scl("funnel0", (0, 1), (0.4, 1.2), (1, 0.05, "cin"))
    for i, b in enumerate(clouds):
        ox, oy, oz = outward(k, b, 14, 4)
        d.pos(b, (0, 0, 0, 0), (1, ox, oy, oz, "cout"))
        d.scl(b, (0, 1), (1, 0.05, "cin"))
    d.scl("orb", (0, 1), (0.2, 1.6), (1, 0.2))
    d.follow(cape, [(0, 0, 0, 0), (0.5, -30, 0, 0), (1, -50, 0, 0)], lag=0.05)
    C[f"misc.{B}.death"] = d
    return {"slugs": ["gust", "called_lightning", "shattered_islet"], "clips": C}


# =============================================================== World 5: Light Eater
@boss("light_eater", world=5)
def light_eater(k, wind, rel):
    C = {}
    B = "light_eater"
    tail = [f"tail{i}" for i in range(5)]
    FL, FR, HL, HR = ("fleg_l0", "fleg_l1"), ("fleg_r0", "fleg_r1"), ("hleg_l0", "hleg_l1"), ("hleg_r0", "hleg_r1")

    def legs(c, u, front=0.0, hind=0.0, z=0.0, ease="sine", ff=0.0, hf=0.0, skip=()):
        """Front and hind hips lowered by front/hind, feet ff/hf ahead of their hips; the body follows."""
        for (th, sh), dr, f in ((FL, front, ff), (FR, front, ff), (HL, hind, hf), (HR, hind, hf)):
            if th in skip:
                continue
            k.stance(c, u, [(th, sh, f, 0)], dr, z=z, ease=ease)
        # the body pitches with the difference between front and hind (the hips are 15 units apart)
        c.pos("body", (u, 0, -(front + hind) / 2, z, ease))

    def feelers(c, u, y, z=0, ease="sine"):
        c.rot("feeler_l", (u, 0, y, z, ease))
        c.rot("feeler_r", (u, 0, -y, -z, ease))

    # ---- Claw in the Dark: a foreleg rises with the claws hooked, then rakes down and across
    w, s, r = parts(k, wind, rel, 0, 0.2)
    legs(w, 0)
    legs(w, 1, front=-1, hind=3, z=1.5, ease="cout", skip=("fleg_r0",))
    w.rot("body", (0, 0, 0, 0), (1, -12, 10, 0, "cout"))
    w.rot("fleg_r0", (0, 0, 0, 0), (1, -84, 0, -14, "cout"))
    w.rot("fleg_r1", (0, 0, 0, 0), (1, 64, 0, 0, "cout"))
    w.pos("fleg_r0", (0, 0, 0, 0), (1, 0, 2, 1.5, "cout"))
    w.rot("neck", (0, 0, 0, 0), (1, -10, -16, 0))
    w.rot("jaw", (0, 0, 0, 0), (1, 14, 0, 0))
    w.follow(tail, [(0, 0, 0, 0), (1, 14, 20, 0)], lag=0.03)
    legs(s, 0.45, front=2, hind=1, z=-3, ease="expo", skip=("fleg_r0",))
    s.rot("body", (0.45, 10, -12, 0, "expo"), (1, 8, -10, 0))
    s.rot("fleg_r0", (0.45, 14, 0, 26, "expo"), (1, 18, 0, 22))
    s.rot("fleg_r1", (0.45, -20, 0, 0, "expo"), (1, -10, 0, 0))
    s.pos("fleg_r0", (0.45, 0, -2, -3, "expo"))
    s.rot("neck", (0.45, 12, 14, 0, "expo"))
    s.rot("jaw", (0.45, 34, 0, 0, "expo"), (1, 16, 0, 0))
    s.follow(tail, [(0.45, -10, -24, 0, "expo")], lag=0.03)
    finish("claw_in_the_dark", w, s, r, C, B)

    # ---- Lights Out: it sits back, lifts its head and opens its maw wide, then gulps the light down
    w, s, r = parts(k, wind, rel, 1, 0.34)
    legs(w, 0)
    legs(w, 0.6, front=0, hind=5, hf=-2, ease="cout")
    legs(w, 1, front=0, hind=5.5, hf=-2)
    w.rot("body", (0, 0, 0, 0), (0.6, -18, 0, 0, "cout"), (1, -20, 0, 0))
    w.rot("neck", (0, 0, 0, 0), (0.6, -32, 0, 0, "cout"), (1, -36, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.6, -10, 0, 0), (1, -12, 0, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.5, 20, 0, 0), (1, 48, 0, 0, "cout"))
    feelers(w, 0, 0)
    feelers(w, 1, -40, 14, "cout")
    w.scl("gorged", (0, 1), (0.4, 1.12), (0.6, 1.0), (0.85, 1.2), (1, 1.1))
    w.follow(tail, [(0, 0, 0, 0), (1, 20, 0, 0)], lag=0.04)
    legs(s, 0.5, front=2, hind=3, z=-2, ease="expo")
    s.rot("body", (0.5, 6, 0, 0, "expo"), (1, 4, 0, 0))
    s.rot("neck", (0.5, 26, 0, 0, "expo"), (1, 20, 0, 0))
    s.rot("head", (0.5, 10, 0, 0, "expo"))
    s.rot("jaw", (0.25, 58, 0, 0, "cout"), (0.7, 0, 0, 0, "cin"), (1, 0, 0, 0))
    s.scl("gorged", (0.7, 1.0), (1, 1.4, "back"))
    s.scl("body", (0, 1), (0.7, 1, 1, 1), (1, 1.04, 1.06, 1.0, "back"))
    feelers(s, 0.5, 30, -6, "expo")
    # recover: the belly glows full; it chews slowly, head low, tail swaying
    for i, u in enumerate((0.1, 0.2, 0.3, 0.4, 0.5)):
        r.rot("jaw", (u, 12 if i % 2 == 0 else 0, 0, 0, "sine"))
    r.scl("gorged", (0.15, 1.35), (0.45, 1.25), (0.8, 1.05, "sine"))
    r.scl("body", (0.3, 1.04, 1.05, 1.0), (0.8, 1, 1, 1, "sine"))
    r.rot("neck", (0.3, 22, 0, 0), (0.7, 18, 0, 0))
    r.follow(tail, [(0.25, 0, 24, 0, "sine"), (0.5, 0, -24, 0, "sine"), (0.75, 0, 14, 0, "sine")], lag=0.05)
    finish("lights_out", w, s, r, C, B)

    # ---- Silent Charge: it sinks low and stalks, rump twitching, then pounces a full block forward
    w, s, r = parts(k, wind, rel, 2, 0.36)
    legs(w, 0)
    legs(w, 0.4, front=5, hind=6, hf=2, ease="sine")
    legs(w, 1, front=5.5, hind=7, hf=3)
    w.rot("body", (0, 0, 0, 0), (0.4, 6, 0, 0, "sine"), (0.6, 6, 4, 0, "sine"), (0.75, 6, -4, 0, "sine"), (0.9, 6, 4, 0, "sine"), (1, 8, 0, 0))
    w.rot("neck", (0, 0, 0, 0), (0.4, 14, 0, 0), (1, 16, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.4, -14, 0, 0), (1, -16, 0, 0))
    feelers(w, 0, 0)
    feelers(w, 0.4, 50, -6)
    w.follow(tail, [(0, 0, 0, 0), (0.4, -10, 0, 0), (0.6, -8, 12, 0), (0.8, -8, -12, 0), (1, -10, 0, 0)], lag=0.04)
    w.scl("gorged", (0, 1), (1, 0.85))
    for th, sh, ang, kn in ((FL, None, -76, 30), (FR, None, -70, 26), (HL, None, 52, 10), (HR, None, 56, 14)):
        s.rot(th[0], (0.45, ang, 0, 0, "expo"), (1, ang * 0.6, 0, 0))
        s.rot(th[1], (0.45, kn, 0, 0, "expo"), (1, kn * 0.6, 0, 0))
        s.pos(th[0], (0.45, 0, 4, -16, "expo"), (1, 0, 0, -16, "in"))
    s.pos("body", (0.45, 0, 4, -16, "expo"), (1, 0, 0, -16, "in"))
    s.rot("body", (0.45, -6, 0, 0, "expo"), (1, 4, 0, 0))
    s.rot("neck", (0.45, -6, 0, 0, "expo"))
    s.rot("jaw", (0.45, 44, 0, 0, "expo"), (1, 30, 0, 0))
    s.follow(tail, [(0.45, 12, 0, 0, "expo"), (1, 0, 0, 0)], lag=0.03)
    # recover: it skids, the hound catches up with its own lunge, shakes its head
    legs(r, 0.35, front=3, hind=2, z=-6, ease="out")
    legs(r, 0.9, ease="sine")
    r.rot("head", (0.45, 0, 0, 14, "sine"), (0.6, 0, 0, -14, "sine"), (0.75, 0, 0, 8, "sine"))
    finish("silent_charge", w, s, r, C, B)

    # ---- Phase: it sits and howls, head raised, feelers waving, the swallowed light flaring
    p = phase_clip(k)
    legs(p, 0)
    legs(p, 0.25, front=0, hind=6, hf=-2, ease="cout")
    legs(p, 0.85, front=0, hind=6, hf=-2)
    legs(p, 1, ease="sine")
    p.rot("body", (0, 0, 0, 0), (0.25, -24, 0, 0, "cout"), (0.85, -26, 0, 0), (1, 0, 0, 0, "sine"))
    p.rot("neck", (0, 0, 0, 0), (0.3, -46, 0, 0, "back"), (0.85, -50, 0, 0), (1, 0, 0, 0))
    p.rot("head", (0, 0, 0, 0), (0.3, -24, 0, 0, "back"), (0.85, -26, 0, 0), (1, 0, 0, 0))
    p.rot("jaw", (0, 0, 0, 0), (0.3, 44, 0, 0, "back"), (0.85, 40, 0, 0), (1, 0, 0, 0))
    p.tremble("jaw", "rotation", 0.35, 0.85, 4, 10)
    for i, u in enumerate((0.25, 0.4, 0.55, 0.7, 0.85)):
        feelers(p, u, -30 if i % 2 == 0 else 20, 20 if i % 2 == 0 else -10)
    feelers(p, 1, 0)
    p.scl("gorged", (0, 1), (0.35, 1.5, "back"), (0.5, 1.25), (0.65, 1.5), (0.85, 1.3), (1, 1))
    p.follow(tail, [(0, 0, 0, 0), (0.3, 30, 0, 0), (0.85, 30, 0, 0), (1, 0, 0, 0)], lag=0.04)
    C[f"misc.{B}.phase"] = p

    # ---- Death: the legs splay, it drops on its belly, the head hits the ground and the light leaks out
    d = death_clip(k)
    legs(d, 0)
    legs(d, 0.2, front=-1, hind=1, ease="cout")
    legs(d, 0.6, front=8.5, hind=8, ff=11, hf=-10, ease="bounce")
    legs(d, 1, front=8.8, hind=8.2, ff=11.5, hf=-10.5)
    d.rot("body", (0, 0, 0, 0), (0.2, -10, 0, 0), (0.6, 2, 0, 6, "bounce"), (1, 2, 0, 6))
    d.rot("neck", (0, 0, 0, 0), (0.2, -30, 0, 0), (0.75, 34, 0, 0, "bounce"), (1, 34, 0, 0))
    d.rot("head", (0, 0, 0, 0), (0.75, 10, 0, 16, "bounce"), (1, 10, 0, 16))
    d.rot("jaw", (0, 0, 0, 0), (0.2, 40, 0, 0), (0.75, 20, 0, 0), (1, 22, 0, 0))
    d.scl("gorged", (0, 1), (0.2, 1.4), (1, 0.5, "cin"))
    feelers(d, 0, 0)
    feelers(d, 1, 30, -30, "bounce")
    d.follow(tail, [(0, 0, 0, 0), (0.3, 20, 0, 0), (0.8, -12, 20, 0, "bounce"), (1, -12, 20, 0)], lag=0.04)
    C[f"misc.{B}.death"] = d
    return {"slugs": ["claw_in_the_dark", "lights_out", "silent_charge"], "clips": C}
