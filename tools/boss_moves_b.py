"""Boss moves, part B: the Upside Realm to the Giant Workshop, and World 0 (see tools/boss_moves.py)."""
import math  # noqa: F401

from boss_moves import boss  # noqa: F401
from boss_moves_a import parts, finish, phase_clip, death_clip, outward  # noqa: F401


def biped(fl, fr, ll=0, lr=0):
    return [("leg_l0", "leg_l1", fl, ll), ("leg_r0", "leg_r1", fr, lr)]


# =============================================================== World 6: Your Double
@boss("your_double", world=6)
def your_double(k, wind, rel):
    C = {}
    B = "your_double"
    copies = ["copy0", "copy1", "copy2", "copy3", "shards"]

    # ---- Copied Strike: your own sword swing, mirrored: blade up past the shoulder, then a fast chop across
    w, s, r = parts(k, wind, rel, 0, 0.2)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(4, -3), 1.2, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (1, -4, -18, 0, "cout"))
    w.rot("arm_r0", (0, 0, 0, 0), (1, -150, 0, -24, "cout"))
    w.rot("arm_r1", (0, 0, 0, 0), (1, -30, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (1, -24, 0, 14))
    w.rot("head", (0, 0, 0, 0), (1, 6, 16, 0))
    k.stance(s, 0.45, biped(6, -4), 2.0, z=-2, body="body", ease="expo")
    k.stance(s, 1, biped(6, -4), 1.8, z=-2, body="body")
    s.rot("body", (0.45, 12, 22, 0, "expo"), (1, 10, 18, 0))
    s.rot("arm_r0", (0.45, -40, 30, 30, "expo"), (1, -30, 34, 34))
    s.rot("arm_r1", (0.45, -6, 0, 0, "expo"))
    s.rot("arm_l0", (0.45, 16, 0, 10, "expo"))
    s.rot("head", (0.45, 4, -12, 0, "expo"))
    s.scl("heart", (0, 1), (0.45, 1.4, "expo"), (1, 1.1))
    finish("copied_strike", w, s, r, C, B)

    # ---- Copied Weapon: its open hand reaches for yours as if reading it, snatches it closed, and the glass
    # copy of your blade lunges straight at you
    w, s, r = parts(k, wind, rel, 1, 0.3)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(3, -3), 1.0, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (1, 8, 16, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -88, 0, -8, "cout"), (1, -92, 0, -10))
    w.rot("arm_l1", (0, 0, 0, 0), (0.6, -4, 0, 0))
    w.tremble("arm_l0", "rotation", 0.6, 1.0, 2.5, 6, (0, 1, 1))
    w.rot("arm_r0", (0, 0, 0, 0), (1, 34, 0, -10, "cout"))
    w.rot("head", (0, 0, 0, 0), (0.6, 8, 0, 16, "sine"), (1, 8, 0, 18))
    for i, b in enumerate(copies):
        w.scl(b, (0, 1), (0.5 + 0.1 * i, 1.25, "back"), (1, 1.3))
    w.scl("heart", (0, 1), (1, 1.25))
    k.stance(s, 0.45, biped(8, -5), 2.5, z=-5, body="body", ease="expo")
    k.stance(s, 1, biped(8, -5), 2.3, z=-5, body="body")
    s.rot("body", (0.45, 12, -24, 0, "expo"), (1, 10, -20, 0))
    s.rot("arm_l0", (0.3, -40, 0, -30, "cout"), (1, -36, 0, -26))
    s.rot("arm_l1", (0.3, -100, 0, 0, "cout"), (1, -96, 0, 0))
    s.rot("arm_r0", (0.45, -46, 0, 6, "expo"), (1, -44, 0, 6))
    s.rot("arm_r1", (0.45, 44, 0, 0, "expo"), (1, 40, 0, 0))
    s.rot("head", (0.45, 6, -10, 0, "expo"))
    for b in copies:
        s.scl(b, (0.45, 0.8, "expo"), (1, 1))
    finish("copied_weapon", w, s, r, C, B)

    # ---- Gravity Flip: it floats up, palms raised, starts to tip backwards, and turns head over heels
    w, s, r = parts(k, wind, rel, 2, 0.4)
    legs = ["leg_l0", "leg_r0"]
    for b in ["body"] + legs:
        w.pos(b, (0, 0, 0, 0), (0.2, 0, -1.5, 0, "sine"), (0.65, 0, 9, 0, "cout"), (1, 0, 10, 0))
        w.rot(b, (0, 0, 0, 0), (0.65, 0, 0, 0), (1, -26, 0, 0, "sine"))
    w.rots(["leg_l1", "leg_r1"], (0, 0, 0, 0), (0.2, 20, 0, 0), (0.65, 30, 0, 0), (1, 32, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -30, 0, 66, "cout"), (1, -40, 0, 70))
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, -30, 0, -66, "cout"), (1, -40, 0, -70))
    w.rot("head", (0, 0, 0, 0), (0.6, -20, 0, 0), (1, -26, 0, 0))
    for i, b in enumerate(copies):
        w.rot(b, (0, 0, 0, 0), (1, 0, 360 if i % 2 == 0 else -360, 0, "cin"))
        w.pos(b, (0, 0, 0, 0), (1, 0, 8 + 2 * i, 0, "cout"))
    w.rot("frame", (0, 0, 0, 0), (1, 0, 0, 10, "sine"))
    w.scl("heart", (0, 1), (1, 1.4))
    for b in ["body"] + legs:
        s.rot(b, (0.6, 180, 0, 0, "back"), (1, 180, 0, 0))
        s.pos(b, (0.6, 0, 18, 0, "back"), (1, 0, 18, 0))
    s.rot("arm_l0", (0.6, -170, 0, 30, "back"))
    s.rot("arm_r0", (0.6, -170, 0, -30, "back"))
    s.scl("heart", (0.6, 1.7, "back"), (1, 1.5))
    for i, b in enumerate(copies):
        s.rot(b, (1, 0, 540 if i % 2 == 0 else -540, 0, "lin"))
    # recover: it completes the turn and lands on its feet
    for b in ["body"] + legs:
        r.rot(b, (0.7, 360, 0, 0, "cio"), (1, 360, 0, 0))
        r.pos(b, (0.7, 0, 2, 0, "cin"), (1, 0, 0, 0, "bounce"))
    for i, b in enumerate(copies):
        r.rot(b, (1, 0, 720 if i % 2 == 0 else -720, 0, "cout"))
    finish("gravity_flip", w, s, r, C, B)

    # ---- Phase: it adopts your style; a full turn on the spot with its arms open, then a mocking salute
    p = phase_clip(k)
    p.rot("body", (0, 0, 0, 0), (0.15, 0, -20, 0, "sine"), (0.6, 0, 360, 0, "cio"), (1, 0, 360, 0))
    for b in ("leg_l0", "leg_r0"):
        p.rot(b, (0, 0, 0, 0), (0.6, 0, 0, 0), (1, 0, 0, 0))
    p.rot("arm_l0", (0, 0, 0, 0), (0.3, -20, 0, 70, "cout"), (0.6, -20, 0, 70), (0.75, 0, 0, 10, "sine"), (1, 0, 0, 0))
    p.rot("arm_r0", (0, 0, 0, 0), (0.3, -20, 0, -70, "cout"), (0.6, -20, 0, -70), (0.72, -150, 0, 6, "back"), (0.9, -150, 0, 6), (1, 0, 0, 0, "sine"))
    p.rot("arm_r1", (0, 0, 0, 0), (0.72, -50, 0, 0, "back"), (0.9, -50, 0, 0), (1, 0, 0, 0))
    p.rot("head", (0, 0, 0, 0), (0.6, 0, 0, 0), (0.75, 10, 0, 22, "back"), (0.9, 10, 0, 22), (1, 0, 0, 0))
    p.scl("heart", (0, 1), (0.6, 1.2), (0.75, 1.6, "back"), (1, 1))
    for i, b in enumerate(copies):
        p.rot(b, (0, 0, 0, 0), (1, 0, -360 if i % 2 == 0 else 360, 0, "cio"))
    C[f"misc.{B}.phase"] = p

    # ---- Death: it kneels, then shatters: head, arms, sword and the copies drift apart and wink out
    d = death_clip(k)
    k.stance(d, 0, biped(0, 0), 0, body="body")
    k.stance(d, 0.3, biped(4, -2), 7.0, body="body", ease="bounce")
    k.stance(d, 1, biped(4, -2), 7.0, body="body")
    d.rot("body", (0, 0, 0, 0), (0.3, 20, 0, 0, "bounce"), (1, 24, 0, 0))
    for b, off in (("head", (0, 8, -2)), ("arm_l0", (6, -2, -2)), ("arm_r0", (-6, -3, -1)), ("sword", (-3, -6, -6)), ("frame", (0, -4, 6))):
        d.pos(b, (0, 0, 0, 0), (0.45, 0, 0, 0), (1, off[0], off[1], off[2], "cout"))
        d.scl(b, (0, 1), (0.45, 1), (1, 0.05, "cin"))
    d.rot("head", (0, 0, 0, 0), (0.3, 24, 0, 0), (1, 40, 30, 20, "cout"))
    d.rot("arm_l0", (0, 0, 0, 0), (0.3, -20, 0, 10), (1, -40, 0, 70, "cout"))
    d.rot("arm_r0", (0, 0, 0, 0), (0.3, -20, 0, -10), (1, -40, 0, -70, "cout"))
    for i, b in enumerate(copies):
        ox, oy, oz = outward(k, b, 10, -4)
        d.pos(b, (0, 0, 0, 0), (1, ox, oy, oz, "cout"))
        d.scl(b, (0, 1), (0.4, 1.3), (1, 0.05, "cin"))
    d.scl("heart", (0, 1), (0.3, 1.8, "back"), (0.6, 0.6), (1, 0.05))
    d.scl("body", (0, 1), (0.6, 1), (1, 0.6, 0.6, 0.6, "cin"))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["copied_strike", "copied_weapon", "gravity_flip"], "clips": C}


# =============================================================== World 7: Pressure Leviathan
@boss("pressure_leviathan", world=7)
def pressure_leviathan(k, wind, rel):
    C = {}
    B = "pressure_leviathan"
    seg = [f"seg{i}" for i in range(6)] + ["fluke"]
    lure = ["lure0", "lure1", "lure2"]

    def fins(c, u, y, z, ease="sine"):
        for b in ("fin_l0", "fin_l3"):
            c.rot(b, (u, 0, y, z, ease))
        for b in ("fin_r0", "fin_r3"):
            c.rot(b, (u, 0, -y, -z, ease))

    # ---- Tail Lash: it coils the tail round to one side, then whips it across in a wave that runs to the fluke
    w, s, r = parts(k, wind, rel, 0, 0.24)
    w.follow(seg, [(0, 0, 0, 0), (1, 0, 14, 0, "cout")], lag=0.02, gain=1.05)
    w.rot("body", (0, 0, 0, 0), (1, 0, 12, 0, "cout"))
    w.rot("head", (0, 0, 0, 0), (1, 0, -14, 0, "cout"))
    s.follow(seg, [(0.4, 0, -22, 0, "expo"), (1, 0, -10, 0)], lag=0.025, gain=1.12)
    s.rot("body", (0.4, 0, -16, 0, "expo"), (1, 0, -10, 0))
    s.rot("head", (0.4, 0, 12, 0, "expo"), (1, 0, 6, 0))
    s.rot("jaw", (0, 0, 0, 0), (0.4, 16, 0, 0, "expo"), (1, 6, 0, 0))
    fins(s, 0, 0, 0)
    fins(s, 0.4, 20, 10, "expo")
    r.follow(seg, [(0.35, 0, 8, 0, "sine"), (0.7, 0, -4, 0, "sine")], lag=0.03)
    finish("tail_lash", w, s, r, C, B)

    # ---- Charge: it draws back into an S, jaw ajar, fins folded, then rams a block forward
    w, s, r = parts(k, wind, rel, 1, 0.3)
    w.pos("body", (0, 0, 0, 0), (1, 0, 0, 7, "cout"))
    w.rot("body", (0, 0, 0, 0), (1, 8, 0, 0, "cout"))
    for i, b in enumerate(seg):
        w.rot(b, (0, 0, 0, 0), (0.7, 0, (22 if i % 2 == 0 else -26) * (1 + 0.1 * i), 0, "cout"), (1, 0, (24 if i % 2 == 0 else -28) * (1 + 0.1 * i), 0))
    w.rot("head", (0, 0, 0, 0), (1, 10, 0, 0, "cout"))
    w.rot("jaw", (0, 0, 0, 0), (1, 16, 0, 0))
    fins(w, 0, 0, 0)
    fins(w, 1, 40, -6, "cout")
    w.follow(lure, [(0, 0, 0, 0), (1, 20, 0, 0)], lag=0.04)
    s.pos("body", (0.5, 0, 0, -20, "expo"), (1, 0, 0, -18))
    s.rot("body", (0.5, -4, 0, 0, "expo"))
    s.follow(seg, [(0.5, 0, 0, 0, "expo"), (1, 0, 4, 0)], lag=0.025)
    s.rot("jaw", (0.5, 38, 0, 0, "expo"), (1, 30, 0, 0))
    s.rot("head", (0.5, -6, 0, 0, "expo"))
    fins(s, 0.5, 60, -10, "expo")
    s.follow(lure, [(0.5, -40, 0, 0, "expo"), (1, -30, 0, 0)], lag=0.03)
    # recover: it glides back, the jaw closing, and shakes its huge head
    r.pos("body", (0.6, 0, 0, -4, "sine"))
    r.rot("head", (0.3, 0, 12, 0, "sine"), (0.45, 0, -12, 0, "sine"), (0.6, 0, 8, 0, "sine"))
    r.follow(seg, [(0.3, 0, -10, 0, "sine"), (0.55, 0, 10, 0, "sine"), (0.8, 0, -6, 0, "sine")], lag=0.04)
    finish("charge", w, s, r, C, B)

    # ---- Abyssal Pull: it raises its head and opens its maw impossibly wide, the lure dangling bright, then
    # inhales the sea in a bulge that runs down its whole body
    w, s, r = parts(k, wind, rel, 2, 0.34)
    w.rot("body", (0, 0, 0, 0), (0.5, -18, 0, 0, "cout"), (1, -20, 0, 0))
    w.follow(seg, [(0, 0, 0, 0), (0.5, 6, 0, 0, "sine"), (1, 8, 0, 0)], lag=0.04)
    for i, b in enumerate(seg[1:]):
        w.tremble(b, "rotation", 0.4, 1.0, 5 + i, 4, (0, 1, 0))
    w.rot("jaw", (0, 0, 0, 0), (0.6, 50, 0, 0, "cout"), (1, 58, 0, 0))
    w.tremble("jaw", "rotation", 0.65, 1.0, 3, 6)
    w.rot("head", (0, 0, 0, 0), (1, -8, 0, 0))
    w.follow(lure, [(0, 0, 0, 0), (0.5, 40, 0, 0), (0.75, 20, 0, 0), (1, 44, 0, 0)], lag=0.05)
    w.scl("lure2", (0, 1), (0.5, 1.4), (0.75, 1.2), (1, 1.6))
    fins(w, 0, 0, 0)
    fins(w, 1, -10, 34, "cout")
    s.rot("body", (0.3, 6, 0, 0, "expo"), (1, 4, 0, 0))
    s.pos("body", (0.3, 0, 0, -5, "expo"), (1, 0, 0, -3))
    s.rot("jaw", (0.2, 64, 0, 0), (0.8, 4, 0, 0, "cin"), (1, 6, 0, 0))
    for i, b in enumerate(seg[:6]):
        u = 0.15 + 0.12 * i
        s.scl(b, (0, 1), (u, 1.28, 1.28, 1, "sine"), (min(1, u + 0.2), 1, 1, 1, "sine"))
    s.follow(lure, [(0.3, -50, 0, 0, "expo"), (1, -20, 0, 0)], lag=0.03)
    fins(s, 0.3, 40, -10, "expo")
    finish("abyssal_pull", w, s, r, C, B)

    # ---- Phase: the depth worsens; it thrashes and barrel-rolls, the roll running down to its tail
    p = phase_clip(k)
    p.rot("body", (0, 0, 0, 0), (0.15, 0, 16, -20, "sine"), (0.75, 0, -10, 360, "cio"), (1, 0, 0, 360, "sine"))
    p.follow(seg, [(0, 0, 0, 0), (0.15, 0, -18, 10), (0.45, 0, 20, -30), (0.75, 0, -14, -10), (1, 0, 0, 0)], lag=0.05)
    p.rot("jaw", (0, 0, 0, 0), (0.2, 40, 0, 0), (0.5, 10, 0, 0), (0.8, 44, 0, 0), (1, 0, 0, 0))
    p.follow(lure, [(0, 0, 0, 0), (0.4, 50, 0, 0), (0.8, -40, 0, 0), (1, 0, 0, 0)], lag=0.04)
    fins(p, 0, 0, 0)
    fins(p, 0.4, 30, 40)
    fins(p, 0.8, -20, -20)
    fins(p, 1, 0, 0)
    C[f"misc.{B}.phase"] = p

    # ---- Death: it goes limp, rolls belly up and sinks, the jaw slack and the tail drooping
    d = death_clip(k)
    d.rot("body", (0, 0, 0, 0), (0.2, -12, 10, 0, "cout"), (1, 6, 0, 180, "cio"))
    d.pos("body", (0, 0, 0, 0), (0.2, 0, 2, 0), (1, 0, -6, 0, "cin"))
    d.follow(seg, [(0, 0, 0, 0), (0.2, 0, 20, 0), (0.5, 0, -14, 0), (1, -8, 6, 0, "sine")], lag=0.05)
    d.rot("jaw", (0, 0, 0, 0), (0.2, 50, 0, 0), (1, 30, 0, 0))
    d.follow(lure, [(0, 0, 0, 0), (1, 60, 0, 0, "bounce")], lag=0.05)
    d.scl("lure2", (0, 1), (1, 0.4))
    fins(d, 0, 0, 0)
    fins(d, 1, 30, -20)
    C[f"misc.{B}.death"] = d
    return {"slugs": ["tail_lash", "charge", "abyssal_pull"], "clips": C}


# =============================================================== World 8: Master of Seasons
@boss("seasons_master", world=8)
def seasons_master(k, wind, rel):
    C = {}
    B = "seasons_master"
    cape = ["cape0", "cape1", "cape2"]

    # ---- Seasonal Strike: the staff is drawn across the body, then swept out in a wide arc
    w, s, r = parts(k, wind, rel, 0, 0.24)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(3, -3), 1.5, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (1, 0, -26, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (1, -62, 0, -40, "cout"))
    w.rot("arm_l1", (0, 0, 0, 0), (1, -20, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (1, 20, 0, -20))
    w.rot("head", (0, 0, 0, 0), (1, 6, 20, 0))
    w.follow(cape, [(0, 0, 0, 0), (1, 6, 0, 8)], lag=0.03)
    k.stance(s, 0.45, biped(5, -4), 2.5, z=-2, body="body", ease="expo")
    k.stance(s, 1, biped(5, -4), 2.3, z=-2, body="body")
    s.rot("body", (0.45, 8, 30, 0, "expo"), (1, 6, 26, 0))
    s.rot("arm_l0", (0.45, -78, 0, 56, "expo"), (1, -70, 0, 60))
    s.rot("arm_l1", (0.45, -4, 0, 0))
    s.rot("head", (0.45, 6, -18, 0, "expo"))
    s.rot("year", (0, 0, 0, 0), (1, 0, 90, 0, "cout"))
    s.follow(cape, [(0.45, -10, 0, -14, "expo"), (1, -6, 0, -8)], lag=0.03)
    r.rot("year", (1, 0, 90, 0, "sine"))
    finish("seasonal_strike", w, s, r, C, B)

    # ---- Seasonal Ground: the staff lifts high, the year-ring tilts, and it is driven into the earth
    w, s, r = parts(k, wind, rel, 1, 0.3)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(2, -2), 0.8, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (1, -10, 0, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.7, -146, 0, 6, "cout"), (1, -152, 0, 8))
    w.rot("arm_l1", (0, 0, 0, 0), (0.7, -16, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (0.7, -120, 0, 26, "cout"), (1, -124, 0, 30))
    w.rot("arm_r1", (0, 0, 0, 0), (0.7, -30, 0, 0))
    w.rot("head", (0, 0, 0, 0), (1, -22, 0, 0, "cout"))
    w.rot("year", (0, 0, 0, 0), (1, 22, 40, 0, "cout"))
    w.scl("clock", (0, 1), (1, 1.4, "back"))
    w.follow(cape, [(0, 0, 0, 0), (1, 12, 0, 0)], lag=0.04)
    k.stance(s, 0.4, biped(5, -3), 5.0, z=-1, body="body", ease="cin")
    k.stance(s, 1, biped(5, -3), 4.6, z=-1, body="body")
    s.rot("body", (0.4, 26, 0, 0, "cin"), (1, 22, 0, 0))
    s.rot("arm_l0", (0.4, -50, 0, 4, "cin"), (1, -46, 0, 4))
    s.rot("arm_l1", (0.4, -6, 0, 0))
    s.rot("arm_r0", (0.4, -46, 0, -4, "cin"), (1, -40, 0, -4))
    s.rot("arm_r1", (0.4, -10, 0, 0))
    s.rot("head", (0.4, 18, 0, 0, "cin"))
    s.rot("year", (0.4, -10, 80, 0, "cin"), (1, 0, 90, 0))
    s.scl("clock", (0.4, 0.8, "cin"), (1, 1.1))
    s.follow(cape, [(0.4, -14, 0, 0, "cin"), (1, -4, 0, 0)], lag=0.03)
    # recover: kneeling by its staff, head bowed, the clock ticking
    for i, u in enumerate((0.15, 0.3, 0.45, 0.6)):
        r.scl("clock", (u, 1.15 if i % 2 == 0 else 0.95, "step"))
    r.rot("head", (0.25, 28, 0, 0, "sine"), (0.65, 26, 0, 0))
    r.rot("year", (1, 0, 360, 0, "sine"))
    r.rot("halo", (0, 0, 0, 0), (1, 0, 0, 90, "sine"))
    finish("seasonal_ground", w, s, r, C, B)

    # ---- Season Shift: the right arm sweeps round the dial like a clock hand while the year spins, then both
    # hands drive down and out as the season turns
    w, s, r = parts(k, wind, rel, 2, 0.32)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(2, -2), 1.0, body="body")
    w.rot("arm_r0", (0, 0, 0, 0), (0.1, 10, 0, -10, "sine"), (0.35, -90, 0, -14, "lin"), (0.6, -180, 0, -14, "lin"), (0.85, -270, 0, -14, "lin"), (1, -330, 0, -12, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.3, -150, 0, 10, "cout"), (1, -154, 0, 12))
    w.rot("body", (0, 0, 0, 0), (0.3, -8, 0, 0), (1, -12, 0, 0))
    w.rot("head", (0, 0, 0, 0), (0.3, -18, 0, 0), (1, -24, 0, 0))
    w.rot("year", (0, 0, 0, 0), (1, 0, 540, 0, "cin"))
    w.rot("halo", (0, 0, 0, 0), (1, 0, 0, -360, "cin"))
    w.rot("cogs", (0, 0, 0, 0), (1, 0, 720, 0, "lin"))
    w.scl("clock", (0, 1), (0.25, 1.2), (0.5, 1), (0.75, 1.25), (1, 1.4))
    w.follow(cape, [(0, 0, 0, 0), (0.5, 14, 0, 6), (1, 18, 0, -6)], lag=0.05)
    k.stance(s, 0.4, biped(4, -4), 4.0, body="body", ease="cin")
    k.stance(s, 1, biped(4, -4), 3.6, body="body")
    s.rot("arm_r0", (0.4, -400, 0, -44, "cin"), (1, -396, 0, -40))
    s.rot("arm_l0", (0.4, -40, 0, 44, "cin"), (1, -36, 0, 40))
    s.rot("body", (0.4, 16, 0, 0, "cin"), (1, 14, 0, 0))
    s.rot("head", (0.4, 14, 0, 0, "cin"))
    s.rot("year", (0.4, 0, 600, 0, "cin"), (1, 0, 720, 0, "cout"))
    s.rot("halo", (1, 0, 0, -360, "cout"))
    s.rot("cogs", (1, 0, 900, 0, "cout"))
    s.scl("clock", (0.4, 0.7, "cin"), (1, 1.3, "back"))
    s.follow(cape, [(0.4, -20, 0, 0, "cin"), (1, -10, 0, 0)], lag=0.03)
    r.rot("arm_r0", (1, -360, 0, 0, "sine"))
    r.rot("year", (1, 0, 720, 0, "sine"))
    r.rot("halo", (1, 0, 0, -360, "sine"))
    r.rot("cogs", (1, 0, 1080, 0, "sine"))
    finish("season_shift", w, s, r, C, B)

    # ---- Phase: the seasons overlap; arms wide, it shakes its antlers on four beats, ring and halo whirling
    p = phase_clip(k)
    p.rot("arm_l0", (0, 0, 0, 0), (0.2, -30, 0, 70, "cout"), (0.85, -30, 0, 74), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.2, -30, 0, -70, "cout"), (0.85, -30, 0, -74), (1, 0, 0, 0, "sine"))
    p.rot("body", (0, 0, 0, 0), (0.2, -12, 0, 0, "cout"), (0.85, -12, 0, 0), (1, 0, 0, 0, "sine"))
    p.rot("head", (0, 0, 0, 0), (0.25, -10, 0, 16, "sine"), (0.4, -10, 0, -16, "sine"), (0.55, -10, 0, 16, "sine"), (0.7, -10, 0, -16, "sine"), (0.85, -10, 0, 0, "sine"), (1, 0, 0, 0))
    p.scl("clock", (0, 1), (0.25, 1.4, "step"), (0.4, 1.1, "step"), (0.55, 1.45, "step"), (0.7, 1.15, "step"), (0.85, 1.5, "step"), (1, 1, "sine"))
    p.rot("year", (0, 0, 0, 0), (1, 0, 1080, 0, "cio"))
    p.rot("halo", (0, 0, 0, 0), (1, 0, 0, 720, "cio"))
    p.follow(cape, [(0, 0, 0, 0), (0.3, 30, 0, 10), (0.6, 20, 0, -10), (0.85, 30, 0, 6), (1, 0, 0, 0)], lag=0.05)
    C[f"misc.{B}.phase"] = p

    # ---- Death: it withers like an old tree: knees bend, it bows, and topples slowly to one side
    d = death_clip(k)
    k.stance(d, 0, biped(0, 0), 0, body=None)
    k.stance(d, 0.45, biped(3, -1), 7.0, ease="sine")
    k.stance(d, 1, biped(3, -1), 8.0)
    d.pos("body", (0, 0, 0, 0), (0.45, 0, -7, 0, "sine"), (1, -6, -14, 0, "cin"))
    d.rot("body", (0, 0, 0, 0), (0.45, 26, 0, 0, "sine"), (1, 30, 0, -72, "cin"))
    d.rot("head", (0, 0, 0, 0), (0.45, 30, 0, 0), (1, 30, 0, -10))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.45, -24, 0, 0), (1, -30, 0, 0))
    d.rot("arm_l1", (0, 0, 0, 0), (0.6, 30, 0, 0), (1, 40, 0, 0))
    d.rot("year", (0, 0, 0, 0), (0.6, 0, 120, 0, "cout"), (1, 30, 140, 0, "bounce"))
    d.pos("year", (0, 0, 0, 0), (1, 0, -30, 0, "bounce"))
    d.scl("clock", (0, 1), (1, 0.6))
    d.follow(cape, [(0, 0, 0, 0), (1, 20, 0, 0)], lag=0.05)
    C[f"misc.{B}.death"] = d
    return {"slugs": ["seasonal_strike", "seasonal_ground", "season_shift"], "clips": C}


# =============================================================== World 9: Heart of the Terrain
@boss("terrain_heart_boss", world=9)
def terrain_heart_boss(k, wind, rel):
    C = {}
    B = "terrain_heart_boss"
    chunks = [f"chunk{i}" for i in range(4)]

    # ---- Ground Wave: one boulder fist rises high and pounds the ground in front
    w, s, r = parts(k, wind, rel, 0, 0.22)
    w.rot("arm_r0", (0, 0, 0, 0), (1, -112, 0, -14, "cout"))
    w.rot("arm_r1", (0, 0, 0, 0), (1, -56, 0, 0, "cout"))
    w.rot("body", (0, 0, 0, 0), (1, -8, -10, 0, "cout"))
    w.scl("heart", (0, 1), (1, 0.9))
    s.rot("arm_r0", (0.45, -36, 0, 4, "expo"), (1, -32, 0, 4))
    s.rot("arm_r1", (0.45, -4, 0, 0, "expo"))
    s.rot("body", (0.45, 14, 6, 0, "expo"), (1, 10, 4, 0))
    s.pos("body", (0, 0, 0, 0), (0.45, 0, -2.5, -1, "expo"), (1, 0, -2, -1))
    s.scl("heart", (0.45, 1.25, "expo"), (1, 1.05))
    for i, b in enumerate(chunks):
        s.pos(b, (0, 0, 0, 0), (0.5 + 0.05 * i, 0, 4, 0, "out"), (1, 0, 0, 0, "bounce"))
    finish("ground_wave", w, s, r, C, B)

    # ---- Living Wall: both arms dig into the ground under it while the heart swells, then rip upward and
    # forward, raising the earth before it
    w, s, r = parts(k, wind, rel, 1, 0.3)
    w.pos("body", (0, 0, 0, 0), (1, 0, -4, 0, "cout"))
    w.rot("body", (0, 0, 0, 0), (1, 12, 0, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (1, 20, 0, 24, "cout"))
    w.rot("arm_r0", (0, 0, 0, 0), (1, 20, 0, -24, "cout"))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (1, 30, 0, 0, "cout"))
    w.scl("heart", (0, 1), (0.5, 1.15), (0.7, 1.05), (1, 1.28))
    w.rot("jaw", (0, 0, 0, 0), (1, 16, 0, 0))
    for i, b in enumerate(chunks):
        w.pos(b, (0, 0, 0, 0), (1, 0, -6, 0, "sine"))
    s.pos("body", (0.45, 0, 4, 0, "expo"), (1, 0, 3, 0))
    s.rot("body", (0.45, -14, 0, 0, "expo"), (1, -10, 0, 0))
    s.rots(["arm_l0", "arm_r0"], (0.45, -150, 0, 0, "expo"), (1, -140, 0, 0))
    s.rot("arm_l0", (0.45, -150, 0, -14, "expo"))
    s.rot("arm_r0", (0.45, -150, 0, 14, "expo"))
    s.rots(["arm_l1", "arm_r1"], (0.45, -20, 0, 0, "expo"))
    s.scl("heart", (0.45, 1.45, "expo"), (1, 1.2))
    s.rot("jaw", (0.45, 30, 0, 0, "expo"))
    for i, b in enumerate(chunks):
        s.pos(b, (0.5 + 0.06 * i, 0, 16, 0, "back"), (1, 0, 14, 0))
    # recover: the arms come down heavily, the heart stumbling through uneven beats
    r.rots(["arm_l0", "arm_r0"], (0.3, -10, 0, 0, "bounce"))
    r.scl("heart", (0.15, 1.1, "sine"), (0.25, 0.92), (0.38, 1.18), (0.5, 0.95), (0.6, 1.12), (0.75, 1.0))
    r.pos("body", (0.3, 0, -1, 0, "bounce"))
    for b in chunks:
        r.pos(b, (0.4, 0, 0, 0, "bounce"))
    finish("living_wall", w, s, r, C, B)

    # ---- Chasm: three heavy beats, each harder, arms spread gripping the ground; then both fists are raised
    # and brought down together to split the floor
    w, s, r = parts(k, wind, rel, 2, 0.32)
    beats = [(0.15, 1.15), (0.25, 1.0), (0.4, 1.25), (0.5, 1.02), (0.65, 1.35), (0.72, 1.1)]
    w.scl("heart", (0, 1), *[(u, v, "sine") for u, v in beats], (1, 1.3))
    w.pos("body", (0, 0, 0, 0), *[(u, 0, (v - 1) * 10, 0, "sine") for u, v in beats], (1, 0, 3, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.5, 0, 0, 40, "sine"), (0.72, 0, 0, 42), (1, -168, 0, 14, "cout"))
    w.rot("arm_r0", (0, 0, 0, 0), (0.5, 0, 0, -40, "sine"), (0.72, 0, 0, -42), (1, -168, 0, -14, "cout"))
    w.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.72, 10, 0, 0), (1, -24, 0, 0, "cout"))
    w.rot("body", (0, 0, 0, 0), (0.72, 0, 0, 0), (1, -16, 0, 0, "cout"))
    w.rot("jaw", (0, 0, 0, 0), (0.7, 20, 0, 0), (1, 34, 0, 0))
    for i, b in enumerate(chunks):
        w.scl(b, (0, 1), (0.7, 0.8, "sine"), (1, 0.75))
        w.pos(b, (0, 0, 0, 0), (1, 0, 8, 0, "sine"))
    s.rot("arm_l0", (0.4, -40, 0, -6, "cin"), (1, -36, 0, -6))
    s.rot("arm_r0", (0.4, -40, 0, 6, "cin"), (1, -36, 0, 6))
    s.rots(["arm_l1", "arm_r1"], (0.4, -6, 0, 0, "cin"))
    s.rot("body", (0.4, 26, 0, 0, "cin"), (1, 22, 0, 0))
    s.pos("body", (0.4, 0, -5, -2, "cin"), (1, 0, -4, -2))
    s.scl("body", (0, 1), (0.4, 1.06, 0.92, 1.06, "cin"), (1, 1, 1, 1, "back"))
    s.scl("heart", (0.4, 0.8, "cin"), (0.7, 1.35, "back"), (1, 1.15))
    s.rot("jaw", (0.4, 40, 0, 0, "cin"), (1, 26, 0, 0))
    for b in chunks:
        s.pos(b, (0.4, 0, -14, 0, "cin"), (1, 0, -10, 0))
        s.scl(b, (0.4, 1, "cin"))
    finish("chasm", w, s, r, C, B)

    # ---- Phase: it beats its own heart with its fists, left, right, left, right, and roars
    p = phase_clip(k)
    for i, u in enumerate((0.12, 0.24, 0.36, 0.48, 0.6, 0.72)):
        left = i % 2 == 0
        p.rot("arm_l0", (u, -84 if left else -20, 0, -36 if left else 10, "cout"))
        p.rot("arm_r0", (u, -20 if left else -84, 0, -10 if left else 36, "cout"))
        p.scl("heart", (u, 1.3 if i % 2 == 0 else 1.2, "expo"), (u + 0.06, 1.0, "sine"))
    for b in ("arm_l0", "arm_r0", "head", "jaw", "body"):
        p.rot(b, (0, 0, 0, 0))
    p.scl("heart", (0, 1))
    p.rots(["arm_l1", "arm_r1"], (0, 0, 0, 0), (0.12, -60, 0, 0), (0.72, -60, 0, 0), (1, 0, 0, 0))
    p.rot("arm_l0", (0.85, -40, 0, 50, "back"), (1, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0.85, -40, 0, -50, "back"), (1, 0, 0, 0, "sine"))
    p.rot("body", (0.72, -6, 0, 0), (0.85, -18, 0, 0, "back"), (1, 0, 0, 0))
    p.rot("head", (0.72, 0, 0, 0), (0.85, -20, 0, 0, "back"), (1, 0, 0, 0))
    p.rot("jaw", (0.72, 10, 0, 0), (0.85, 40, 0, 0, "back"), (1, 0, 0, 0))
    C[f"misc.{B}.phase"] = p

    # ---- Death: the beats slow and fade, the heart deflates, the arms slump and the earth falls out of the air
    d = death_clip(k)
    d.scl("heart", (0, 1), (0.1, 1.25, "sine"), (0.22, 1.0), (0.36, 1.15, "sine"), (0.5, 1.0), (0.66, 1.06, "sine"), (0.8, 1.0), (1, 1.06, 0.82, 1.06, "sine"))
    d.pos("body", (0, 0, 0, 0), (0.6, 0, -1, 0), (1, 0, -7, 0, "bounce"))
    d.rot("body", (0, 0, 0, 0), (0.6, 4, 0, 0), (1, 16, 0, 6, "bounce"))
    d.rot("arm_l0", (0, 0, 0, 0), (0.6, 0, 0, 10), (1, 10, 0, 46, "bounce"))
    d.rot("arm_r0", (0, 0, 0, 0), (0.6, 0, 0, -10), (1, 10, 0, -46, "bounce"))
    d.rot("head", (0, 0, 0, 0), (1, 20, 0, 6))
    d.rot("jaw", (0, 0, 0, 0), (0.6, 10, 0, 0), (1, 34, 0, 0, "bounce"))
    for i, b in enumerate(chunks):
        ox, oy, oz = outward(k, b, 3, -18 - 10 * (i % 2))
        d.pos(b, (0, 0, 0, 0), (0.5 + 0.1 * i, ox, oy, oz, "bounce"), (1, ox, oy, oz))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["ground_wave", "living_wall", "chasm"], "clips": C}


def wobble(c, bone, u0, u1, amp, n=4, axis=(1, 0, 1)):
    """A matryoshka's rocking on its round base: a swing that halves each time, ending still."""
    for i in range(n):
        u = u0 + (u1 - u0) * (i + 1) / (n + 1)
        a = amp * (0.5 ** i) * (1 if i % 2 == 0 else -1)
        c.rot(bone, (u, a * axis[0], 0, a * axis[2] * 0.6, "sine"))
    c.rot(bone, (u1, 0, 0, 0, "sine"))


# =============================================================== World 10: The Unfinished
# its three attacks borrow the world of its current shell, and so the timing of that world: one cut per tier
@boss("the_unfinished", world=10, tiers=list(range(1, 10)))
def the_unfinished(k, wind, rel):
    C = {}
    B = "the_unfinished"
    dolls = ["doll0", "doll1", "doll2"]

    # ---- Shell Stroke: the doll rocks back on its base, brush raised high, and paints a slash across the air
    w, s, r = parts(k, wind, rel, 0, 0.24)
    w.rot("body", (0, 0, 0, 0), (1, -9, 0, 6, "cout"))
    w.rot("arm_r0", (0, 0, 0, 0), (1, -142, 0, -40, "cout"))
    w.rot("arm_r1", (0, 0, 0, 0), (1, -34, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (1, -30, 0, 20))
    w.rot("head", (0, 0, 0, 0), (1, -8, 14, 0))
    w.rot("brush", (0, 0, 0, 0), (1, 30, 0, 0))
    s.rot("body", (0.45, 12, 0, -6, "expo"), (1, 10, 0, -5))
    s.rot("arm_r0", (0.45, -44, 0, 32, "expo"), (1, -36, 0, 36))
    s.rot("arm_r1", (0.45, -8, 0, 0, "expo"))
    s.rot("brush", (0.45, -30, 0, 0, "expo"), (1, -16, 0, 0))
    s.rot("head", (0.45, 6, -8, 0, "expo"))
    s.scl("core", (0, 1), (0.45, 1.5, "expo"), (1, 1.2))
    wobble(r, "body", 0.0, 1.0, 8, 3)
    finish("shell_stroke", w, s, r, C, B)

    # ---- Shell Lift: the top half lifts off and turns, the inner doll rises with its core blazing, arms up;
    # then the lid slams back down and the whole doll rocks
    w, s, r = parts(k, wind, rel, 1, 0.3)
    w.pos("shell_top", (0, 0, 0, 0), (0.6, 0, 11, 0, "back"), (1, 0, 12, 0))
    w.rot("shell_top", (0, 0, 0, 0), (0.6, 0, 40, 0, "cout"), (1, 0, 46, 0))
    w.pos("inner", (0, 0, 0, 0), (0.7, 0, 5, 0, "back"), (1, 0, 5.5, 0))
    w.scl("core", (0, 1), (0.5, 1.4), (0.7, 1.2), (1, 1.7))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -70, 0, 34, "cout"), (1, -76, 0, 38))
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, -70, 0, -34, "cout"), (1, -76, 0, -38))
    w.tremble("body", "rotation", 0.3, 1.0, 2.5, 6, (0, 0, 1))
    for i, b in enumerate(dolls):
        w.pos(b, (0, 0, 0, 0), (1, 0, 6 + 2 * i, 0, "sine"))
    s.pos("shell_top", (0.4, 0, 0, 0, "cin"))
    s.rot("shell_top", (0.4, 0, 0, 0, "cin"))
    s.pos("inner", (0.35, 0, 0, 0, "cin"))
    s.scl("body", (0, 1), (0.4, 1.08, 0.88, 1.08, "cin"), (1, 1, 1, 1, "back"))
    s.rots(["arm_l0", "arm_r0"], (0.4, 10, 0, 0, "cin"))
    s.scl("core", (0.4, 0.8, "cin"), (1, 1.1))
    for b in dolls:
        s.pos(b, (0.5, 0, -2, 0, "cin"), (1, 0, 0, 0))
    wobble(r, "body", 0.0, 0.9, 12, 4)
    r.scl("core", (0.5, 0.8, "sine"))
    finish("shell_lift", w, s, r, C, B)

    # ---- Shell Burst: it spins on its base faster and faster, the lid rising, arms flung out; then halts and
    # the lid bursts up off the inner doll before crashing back
    w, s, r = parts(k, wind, rel, 2, 0.4)
    w.rot("body", (0, 0, 0, 0), (0.15, 0, -20, 0, "sine"), (1, 0, 720, 0, "cin"))
    w.pos("shell_top", (0, 0, 0, 0), (1, 0, 7, 0, "cin"))
    w.pos("inner", (0, 0, 0, 0), (1, 0, 3, 0, "cin"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.5, 0, 0, 80, "cout"), (1, 0, 0, 86))
    w.rot("arm_r0", (0, 0, 0, 0), (0.5, 0, 0, -80, "cout"), (1, 0, 0, -86))
    for b in dolls:
        ox, oy, oz = outward(k, b, 8, 4)
        w.pos(b, (0, 0, 0, 0), (1, ox, oy, oz, "cin"))
    w.scl("core", (0, 1), (1, 1.6))
    s.rot("body", (0.3, 0, 760, 0, "out"), (1, 0, 720, 0, "back"))
    s.pos("shell_top", (0.35, 0, 20, 0, "expo"), (0.75, 0, 0, 0, "cin"), (1, 0, 0, 0))
    s.rot("shell_top", (0.35, -24, 0, 12, "expo"), (0.75, 0, 0, 0, "cin"))
    s.scl("shell_bottom", (0, 1), (0.75, 1, "lin"), (0.85, 1.1, 0.85, 1.1, "cin"), (1, 1, 1, 1, "back"))
    s.rot("arm_l0", (0.35, -120, 0, 40, "expo"), (1, -10, 0, 20))
    s.rot("arm_r0", (0.35, -120, 0, -40, "expo"), (1, -10, 0, -20))
    s.scl("core", (0.35, 2.0, "expo"), (1, 1.2))
    r.rot("body", (1, 0, 720, 0, "sine"))
    r.scl("shell_bottom", (0.3, 1, "sine"))
    finish("shell_burst", w, s, r, C, B)

    # ---- Phase: a shell breaks and a new face is painted: the lid rises, spins a full turn and settles
    p = phase_clip(k)
    p.pos("shell_top", (0, 0, 0, 0), (0.3, 0, 18, 0, "back"), (0.75, 0, 18, 0), (0.92, 0, 0, 0, "bounce"), (1, 0, 0, 0))
    p.rot("shell_top", (0, 0, 0, 0), (0.3, 0, 0, 0), (0.75, 0, 360, 0, "cio"), (1, 0, 360, 0))
    p.scl("core", (0, 1), (0.3, 1.8, "back"), (0.5, 1.4), (0.7, 2.0), (0.9, 1.0), (1, 1))
    p.rot("arm_l0", (0, 0, 0, 0), (0.3, -150, 0, 30, "back"), (0.75, -150, 0, 30), (0.92, 0, 0, 0, "sine"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.3, -150, 0, -30, "back"), (0.75, -150, 0, -30), (0.92, 0, 0, 0, "sine"))
    p.pos("inner", (0, 0, 0, 0), (0.3, 0, 4, 0, "back"), (0.85, 0, 4, 0), (0.92, 0, 0, 0))
    p.rot("body", (0, 0, 0, 0), (0.88, 0, 0, 0))
    wobble(p, "body", 0.9, 1.0, 6, 2)
    C[f"misc.{B}.phase"] = p

    # ---- Death: a tiny final form; the two halves of the last shell fall away and only a small doll is left
    d = death_clip(k)
    d.pos("shell_top", (0, 0, 0, 0), (0.3, 4, 20, 2, "cout"), (0.75, 26, -12, 6, "bounce"), (1, 26, -12, 6))
    d.rot("shell_top", (0, 0, 0, 0), (0.3, 0, 30, -30, "cout"), (0.75, 0, 40, -90, "bounce"), (1, 0, 40, -90))
    d.pos("shell_bottom", (0, 0, 0, 0), (0.45, 0, 0, 0), (0.8, -10, 0, 2, "bounce"), (1, -10, 0, 2))
    d.rot("shell_bottom", (0, 0, 0, 0), (0.45, 0, 0, 0), (0.8, 0, 0, 34, "bounce"), (1, 0, 0, 34))
    d.scl("inner", (0, 1), (0.3, 1.0), (0.7, 0.28, "cio"), (1, 0.25))
    d.rot("inner", (0, 0, 0, 0), (0.7, 0, 0, 0), (0.85, 0, 0, 10, "sine"), (1, 0, 0, 0, "sine"))
    d.scl("core", (0, 1), (0.3, 2.0), (1, 1.4))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.3, -40, 0, 0), (1, 0, 0, 0, "sine"))
    for i, b in enumerate(dolls):
        ox, oy, oz = outward(k, b, 4, -(22 + 7 * i))
        d.pos(b, (0, 0, 0, 0), (0.4 + 0.1 * i, ox, oy + (8 if i == 1 else 0), oz, "bounce"), (1, ox, oy + (8 if i == 1 else 0), oz))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["shell_stroke", "shell_lift", "shell_burst"], "clips": C}


# =============================================================== World 0: The Artisan's Shadow
# it borrows the law of a prison, a new one every fifteen seconds, and with it that world's timing
@boss("artisan_shadow", world=11, tiers=list(range(1, 10)))
def artisan_shadow(k, wind, rel):
    C = {}
    B = "artisan_shadow"
    halves = ["half0", "half1"]
    seams = [f"seam{i}" for i in range(6)]

    # ---- Unfinished Stroke: chisel set against the air, hammer high; one sculptor's blow drives it forward
    w, s, r = parts(k, wind, rel, 0, 0.22)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(3, -3), 1.5, body="body", ease="cout")
    w.rot("body", (0, 0, 0, 0), (1, 8, 10, 0, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (1, -72, 0, -10, "cout"))
    w.rot("arm_l1", (0, 0, 0, 0), (1, -30, 0, 0))
    w.rot("arm_r0", (0, 0, 0, 0), (1, -152, 0, -14, "cout"))
    w.rot("arm_r1", (0, 0, 0, 0), (1, -40, 0, 0))
    w.rot("head", (0, 0, 0, 0), (1, 18, 0, 0))
    k.stance(s, 0.45, biped(6, -4), 2.5, z=-3, body="body", ease="expo")
    k.stance(s, 1, biped(6, -4), 2.3, z=-3, body="body")
    s.rot("body", (0.45, 14, 0, 0, "expo"), (1, 12, 0, 0))
    s.rot("arm_l0", (0.45, -94, 0, -6, "expo"), (1, -90, 0, -6))
    s.rot("arm_l1", (0.45, -6, 0, 0))
    s.rot("arm_r0", (0.45, -78, 0, 22, "expo"), (1, -74, 0, 20))
    s.rot("arm_r1", (0.45, -24, 0, 0))
    for b in seams:
        s.scl(b, (0, 1), (0.45, 1.5, "expo"), (1, 1))
    finish("unfinished_stroke", w, s, r, C, B)

    # ---- Borrowed Law: the hammer rises like a gavel over an open palm, the doll halves gather above, and the
    # verdict falls on the palm
    w, s, r = parts(k, wind, rel, 1, 0.3)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 1, biped(1, -1), 0.5, body="body")
    w.rot("body", (0, 0, 0, 0), (1, -8, 0, 0, "cout"))
    w.rot("arm_r0", (0, 0, 0, 0), (0.6, -166, 0, -6, "cout"), (1, -170, 0, -8))
    w.rot("arm_r1", (0, 0, 0, 0), (1, -20, 0, 0))
    w.rot("arm_l0", (0, 0, 0, 0), (0.6, -78, 0, -14, "cout"), (1, -80, 0, -16))
    w.rot("head", (0, 0, 0, 0), (1, -16, 0, 0))
    for i, b in enumerate(halves):
        w.pos(b, (0, 0, 0, 0), (0.7, 0, 12 - 7 * i, 0, "back"), (1, 0, 13 - 7 * i, 0))
        w.scl(b, (0, 1), (1, 1.3, "back"))
    k.stance(s, 0.4, biped(2, -2), 3.0, body="body", ease="cin")
    k.stance(s, 1, biped(2, -2), 2.6, body="body")
    s.rot("body", (0.4, 18, 0, 0, "cin"), (1, 14, 0, 0))
    s.rot("arm_r0", (0.4, -72, 0, 18, "cin"), (1, -70, 0, 16))
    s.rot("arm_r1", (0.4, -24, 0, 0))
    s.rot("head", (0.4, 14, 0, 0, "cin"))
    for b in halves:
        s.pos(b, (0.4, 0, -4, 0, "cin"), (1, 0, 0, 0, "back"))
        s.scl(b, (0.4, 0.8, "cin"), (1, 1))
    finish("borrowed_law", w, s, r, C, B)

    # ---- Ten Prisons at Once: down on one knee, it taps the ground faster and faster as if nailing the
    # walls of ten cells at once, then one two-handed blow
    w, s, r = parts(k, wind, rel, 2, 0.36)
    k.stance(w, 0, biped(0, 0), 0, body="body")
    k.stance(w, 0.2, biped(6, -6, 0, 0), 6.5, body="body", ease="cout")
    k.stance(w, 1, biped(6, -6), 6.8, body="body")
    w.rot("body", (0, 0, 0, 0), (0.2, 22, 0, 0, "cout"), (1, 24, 0, 0))
    taps = [(0.3, -150), (0.4, -40), (0.5, -140), (0.58, -40), (0.66, -130), (0.72, -40), (0.78, -120), (0.83, -40), (0.88, -110), (0.92, -40)]
    w.rot("arm_r0", (0, 0, 0, 0), *[(u, a, 0, 0, "expo" if a == -40 else "sine") for u, a in taps], (1, -170, 0, -10, "cout"))
    w.rot("arm_l0", (0, 0, 0, 0), (0.2, -40, 0, 0), (0.92, -40, 0, 0), (1, -170, 0, 10, "cout"))
    for i, b in enumerate(seams):
        w.scl(b, (0, 1), (1, 0.6, "sine"))
    for i, b in enumerate(halves):
        w.rot(b, (0, 0, 0, 0), (1, 0, 540 if i == 0 else -540, 0, "cin"))
    k.stance(s, 0.4, biped(6, -6), 7.2, body="body", ease="cin")
    s.rot("body", (0.4, 40, 0, 0, "cin"), (1, 36, 0, 0))
    s.rot("arm_r0", (0.4, -40, 0, -4, "cin"), (1, -36, 0, -4))
    s.rot("arm_l0", (0.4, -40, 0, 4, "cin"), (1, -36, 0, 4))
    for b in seams:
        s.scl(b, (0.4, 1.6, "expo"), (1, 1.1))
    for i, b in enumerate(halves):
        s.rot(b, (1, 0, 720 if i == 0 else -720, 0, "cout"))
    for i, b in enumerate(halves):
        r.rot(b, (1, 0, 720 if i == 0 else -720, 0, "sine"))
    finish("ten_prisons", w, s, r, C, B)

    # ---- Phase: every seam gives way; head, arms and the doll halves burst apart, then stitch back together
    p = phase_clip(k)
    parts_off = (("head", (0, 7, 0)), ("arm_l0", (6, 1, 0)), ("arm_r0", (-6, 1, 0)), ("leg_l0", (2, -1, 0)), ("leg_r0", (-2, -1, 0)))
    for b, (x, y, z) in parts_off:
        p.pos(b, (0, 0, 0, 0), (0.3, x, y, z, "expo"), (0.6, x * 1.1, y * 1.1, z, "sine"), (0.85, 0, 0, 0, "back"), (1, 0, 0, 0))
    p.rot("head", (0, 0, 0, 0), (0.3, -20, 0, 14, "expo"), (0.6, -20, 0, -10), (0.85, 0, 0, 0, "back"))
    p.rot("arm_l0", (0, 0, 0, 0), (0.3, 0, 0, 50, "expo"), (0.85, 0, 0, 0, "back"))
    p.rot("arm_r0", (0, 0, 0, 0), (0.3, 0, 0, -50, "expo"), (0.85, 0, 0, 0, "back"))
    for b in halves + seams:
        ox, oy, oz = outward(k, b, 10, 2)
        p.pos(b, (0, 0, 0, 0), (0.3, ox, oy, oz, "expo"), (0.85, 0, 0, 0, "back"), (1, 0, 0, 0))
    for b in seams:
        p.scl(b, (0, 1), (0.3, 1.8, "expo"), (0.85, 1, "back"))
    C[f"misc.{B}.phase"] = p

    # ---- Death: it kneels, lays its hammer and chisel on the ground and bows its head
    d = death_clip(k)
    k.stance(d, 0, biped(0, 0), 0, body="body")
    k.stance(d, 0.4, biped(5, -7), 8.5, body="body", ease="sine")
    k.stance(d, 1, biped(5, -7), 8.8, body="body")
    d.rot("body", (0, 0, 0, 0), (0.4, 16, 0, 0, "sine"), (1, 40, 0, 0, "sine"))
    d.rots(["arm_l0", "arm_r0"], (0, 0, 0, 0), (0.4, -30, 0, 0), (0.75, -56, 0, 0, "sine"), (1, -20, 0, 0, "sine"))
    d.rot("hammer", (0, 0, 0, 0), (0.75, 0, 0, 0), (0.9, 80, 0, 0, "bounce"), (1, 80, 0, 0))
    d.rot("chisel", (0, 0, 0, 0), (0.75, 0, 0, 0), (0.9, 80, 0, 0, "bounce"), (1, 80, 0, 0))
    d.rot("head", (0, 0, 0, 0), (0.5, 10, 0, 0), (1, 44, 0, 0, "sine"))
    for b in halves + seams:
        ox, oy, oz = outward(k, b, 2, -18)
        d.pos(b, (0, 0, 0, 0), (0.6, ox, oy, oz, "bounce"), (1, ox, oy, oz))
    C[f"misc.{B}.death"] = d
    return {"slugs": ["unfinished_stroke", "borrowed_law", "ten_prisons"], "clips": C}
