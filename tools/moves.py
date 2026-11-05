"""Animations for the signature attacks of tools/attacks.py.

Each attack gets its own animation: the delivery picks the gesture (a blow, a leap, a cry...), and the attack's
own numbers shape it: the hit frame sits on the attack's hit tick, multi-hit attacks strike that many times,
and a per-attack seed varies the amplitude, the leading limb and the follow-through, so no two creatures move
the same way.
"""
import random

import attacks as ATK


def _k(d):
    return {f"{t:.2f}": {"post": [round(v, 2) for v in val], "lerp_mode": "catmullrom"} for t, val in d}


def _lin(d):
    return {f"{t:.2f}": {"post": val, "lerp_mode": "linear"} for t, val in d}


def attack_anims(roles, mob_id):
    body = (roles.get("body") or roles.get("head") or ["root"])[0]
    head = roles.get("head", [])
    arms_r, arms_l = roles.get("arm_r", []), roles.get("arm_l", [])
    legs = roles.get("leg_l", []) + roles.get("leg_r", [])
    jaws = roles.get("jaw", [])
    wings_l, wings_r = roles.get("wing_l", []), roles.get("wing_r", [])
    tails = roles.get("tail", []) + roles.get("seg", [])
    out = {}
    for a in (ATK.full(mob_id) if mob_id in ATK.A else []):  # harmless wildlife has no attacks
        r = random.Random(ATK.anim_seed(a))
        amp = 0.8 + r.random() * 0.45
        lead, other = (arms_r, arms_l) if r.random() < 0.6 else (arms_l, arms_r)
        lead = lead or other or head or [body]
        tw = r.choice([-1, 1]) * (8 + r.random() * 14)
        hit, end = a["hit"] / 20, a["end"] / 20
        pre = max(0.05, hit - 0.12 - r.random() * 0.1)
        k = a["kind"]
        B = {}

        def add(bone, ch, keys, lerp=_k):
            B.setdefault(bone, {})[ch] = lerp(keys)

        if k == "melee":
            n = a["n"]
            step = a["iv"] / 20
            hits = [hit + i * step for i in range(n)]
            for i, bone in enumerate(lead + (other if n > 1 else [])):
                ks = [(0, [0, 0, 0]), (pre, [-95 * amp, tw, 0])]
                for j, s in enumerate(hits):
                    up = (j + i) % 2 == 0
                    ks += [(s, [35 * amp if up else -10, -tw, 0]), (min(end - 0.02, s + step * 0.6), [-70 * amp if j < n - 1 else 10, tw * 0.5, 0])]
                ks.append((end, [0, 0, 0]))
                ks = sorted(dict(ks).items())
                add(bone, "rotation", ks)
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [-6, tw * 0.8, 0]), (hits[-1], [10 * amp, -tw, 0]), (end, [0, 0, 0])])
            for j in jaws:
                add(j, "rotation", [(0, [0, 0, 0])] + [(s, [-45 * amp, 0, 0]) for s in hits] + [(end, [0, 0, 0])])
            if not (arms_r or arms_l):
                add(body, "position", [(0, [0, 0, 0]), (pre, [0, 0, 2]), (hits[0], [0, 0, -3 * amp]), (end, [0, 0, 0])])
        elif k in ("leap", "dash"):
            low = k == "dash"
            add(body, "position", [(0, [0, 0, 0]), (pre, [0, -2.5 * amp, 2]), (hit, [0, (0.5 if low else 2.5) * amp, -4]), (hit + 0.3, [0, 0.5, -1]), (end, [0, 0, 0])])
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [14 * amp, 0, 0]), (hit, [(-8 if low else -22) * amp, 0, tw * 0.3]), (hit + 0.35, [6, 0, 0]), (end, [0, 0, 0])])
            for bone in lead + other:
                add(bone, "rotation", [(0, [0, 0, 0]), (pre, [35, 0, 0]), (hit, [(-60 if low else -130) * amp, 0, 0]), (hit + 0.4, [-30, 0, 0]), (end, [0, 0, 0])])
            for l in legs:
                add(l, "rotation", [(0, [0, 0, 0]), (pre, [-30 * amp, 0, 0]), (hit, [45 * amp, 0, 0]), (hit + 0.4, [0, 0, 0]), (end, [0, 0, 0])])
            for j in jaws:
                add(j, "rotation", [(0, [0, 0, 0]), (hit, [-55 * amp, 0, 0]), (hit + 0.25, [0, 0, 0]), (end, [0, 0, 0])])
            for t in tails:
                add(t, "rotation", [(0, [0, 0, 0]), (hit, [25 * amp, 0, 0]), (end, [0, 0, 0])])
        elif k in ("ring", "quake"):
            n = a.get("n", 1) if k == "quake" else 1
            step = a.get("iv", 5) / 20
            hits = [hit + i * step for i in range(n)]
            ks_p = [(0, [0, 0, 0]), (pre, [0, 3 * amp, 0])]
            ks_s = [(0, [1, 1, 1]), (pre, [0.95, 1.08, 0.95])]
            for s in hits:
                ks_p += [(s, [0, -2.5 * amp, 0]), (min(end - 0.02, s + step * 0.5), [0, 1 * amp, 0])]
                ks_s += [(s, [1.1, 0.9, 1.1]), (min(end - 0.02, s + step * 0.5), [1, 1, 1])]
            ks_p.append((end, [0, 0, 0]))
            ks_s.append((end, [1, 1, 1]))
            add(body, "position", sorted(dict(ks_p).items()))
            add(body, "scale", sorted(dict(ks_s).items()))
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [-18 * amp, 0, 0]), (hits[0], [16 * amp, 0, 0]), (end, [0, 0, 0])])
            for bone in lead + other:
                add(bone, "rotation", [(0, [0, 0, 0]), (pre, [-165 * amp, 0, 0]), (hits[0], [25, 0, 0]), (end, [0, 0, 0])])
        elif k == "cone":
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [0, 50 * amp, 0]), (hit, [8, -60 * amp, 0]), (hit + 0.15, [4, -40 * amp, 0]), (end, [0, 0, 0])])
            for bone in lead:
                add(bone, "rotation", [(0, [0, 0, 0]), (pre, [-70 * amp, 50, 60]), (hit, [-75 * amp, -45, -10]), (end, [0, 0, 0])])
            for t in tails:
                add(t, "rotation", [(0, [0, 0, 0]), (pre, [0, -45 * amp, 0]), (hit, [0, 55 * amp, 0]), (end, [0, 0, 0])])
            for w in wings_l:
                add(w, "rotation", [(0, [0, 0, 0]), (pre, [0, 0, 60 * amp]), (hit, [0, 0, -40]), (end, [0, 0, 0])])
            for w in wings_r:
                add(w, "rotation", [(0, [0, 0, 0]), (pre, [0, 0, -60 * amp]), (hit, [0, 0, 40]), (end, [0, 0, 0])])
        elif k in ("bolt", "beam"):
            n = a["n"]
            step = a["iv"] / 20
            shots = [hit + i * step for i in range(n)] if k == "bolt" else [hit]
            hold = hit + (n - 1) * step if k == "beam" else shots[-1]
            ks_b = [(0, [1, 1, 1]), (pre, [1.08 * 1, 1.08, 1.08])]
            for s in shots:
                ks_b += [(s, [0.94, 0.94, 0.94]), (min(end - 0.02, s + step * 0.5), [1.03, 1.03, 1.03])]
            ks_b.append((end, [1, 1, 1]))
            add(body, "scale", sorted(dict(ks_b).items()))
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [-12 * amp, 0, 0]), (hit, [14 * amp, 0, 0]), (hold, [10 * amp, 0, 0]), (end, [0, 0, 0])])
            for h in head:
                add(h, "rotation", [(0, [0, 0, 0]), (pre, [-30 * amp, 0, 0]), (hit, [18 * amp, 0, 0]), (hold, [15 * amp, tw * 0.3, 0]), (end, [0, 0, 0])])
            for j in jaws:
                add(j, "rotation", [(0, [0, 0, 0]), (pre, [-10, 0, 0]), (hit, [-55 * amp, 0, 0]), (hold, [-45 * amp, 0, 0]), (end, [0, 0, 0])])
            for bone in lead[:1]:
                add(bone, "rotation", [(0, [0, 0, 0]), (pre, [-150 * amp, 0, 20]), (hit, [-85, 0, 0]), (hold, [-85, 0, 0]), (end, [0, 0, 0])])
        elif k in ("pull", "grab"):
            reach = -110 if k == "pull" else -95
            hold = hit + (a.get("hold", 20) / 20 if k == "grab" else 0.3)
            hold = min(hold, end - 0.05)
            for bone in lead + other:
                add(bone, "rotation", [(0, [0, 0, 0]), (pre, [-50 * amp, 0, 0]), (hit, [reach * amp, 0, 0]), (hold, [(reach + 30) * amp, 0, 0]), (end, [0, 0, 0])])
            add(body, "position", [(0, [0, 0, 0]), (hit, [0, 0, -3 * amp]), (hold, [0, 0, 1.5 if k == "pull" else -2]), (end, [0, 0, 0])])
            for j in jaws:
                add(j, "rotation", [(0, [0, 0, 0]), (hit, [-60 * amp, 0, 0]), (hold, [-20, 0, 0]), (end, [0, 0, 0])])
            for t in tails:
                add(t, "rotation", [(0, [0, 0, 0]), (hit, [0, 40 * amp, 0]), (hold, [0, -25, 0]), (end, [0, 0, 0])])
        elif k == "blink":
            add(body, "scale", [(0, [1, 1, 1]), (pre, [0.6, 1.35, 0.6]), (hit, [0.04, 0.04, 0.04]), (hit + 0.05, [1.25, 0.8, 1.25]), (end, [1, 1, 1])])
            for bone in lead:
                add(bone, "rotation", [(0, [0, 0, 0]), (hit + 0.05, [-110 * amp, tw, 0]), (hit + 0.2, [25, 0, 0]), (end, [0, 0, 0])])
        elif k == "spin":
            turns = 360 * max(1, round(a["n"] / 2))
            add(body, "rotation", [(0, [0, 0, 0]), (hit, [0, 0, 0]), (end - 0.1, [0, turns * (1 if tw > 0 else -1), 0]), (end, [0, turns * (1 if tw > 0 else -1), 0])], _lin)
            for bone in arms_l:
                add(bone, "rotation", [(0, [0, 0, 0]), (hit, [0, 0, -85 * amp]), (end - 0.1, [0, 0, -85 * amp]), (end, [0, 0, 0])])
            for bone in arms_r:
                add(bone, "rotation", [(0, [0, 0, 0]), (hit, [0, 0, 85 * amp]), (end - 0.1, [0, 0, 85 * amp]), (end, [0, 0, 0])])
        elif k == "rain":
            add(body, "position", [(0, [0, 0, 0]), (hit - 0.4, [0, 2 * amp, 0]), (hit, [0, -2, 0]), (end, [0, 0, 0])])
            for bone in lead + other:
                add(bone, "rotation", [(0, [0, 0, 0]), (0.25, [-170 * amp, 0, 0]), (hit - 0.1, [-175 * amp, 0, tw * 0.5]), (hit, [30, 0, 0]), (end, [0, 0, 0])])
            for h in head:
                add(h, "rotation", [(0, [0, 0, 0]), (0.25, [-35 * amp, 0, 0]), (hit, [25, 0, 0]), (end, [0, 0, 0])])
            for w in wings_l + wings_r:
                add(w, "rotation", [(0, [0, 0, 0]), (0.25, [0, 0, (70 if w in wings_l else -70) * amp]), (hit, [0, 0, 0]), (end, [0, 0, 0])])
        elif k == "trail":
            add(body, "position", [(0, [0, 0, 0]), (hit, [0, -1.5 * amp, 0]), (end, [0, 0, 0])])
            add(body, "rotation", [(0, [0, 0, 0]), (hit * 0.5, [0, 0, tw * 0.4]), (hit, [0, 0, -tw * 0.4]), (end, [0, 0, 0])])
            add(body, "scale", [(0, [1, 1, 1]), (hit, [1.12 * amp ** 0.3, 0.9, 1.12 * amp ** 0.3]), (end, [1, 1, 1])])
        elif k in ("roar", "summon", "ward"):
            swell = 1.12 if k != "ward" else 0.92
            add(body, "rotation", [(0, [0, 0, 0]), (pre, [12, 0, 0]), (hit, [(-18 if k != "ward" else 14) * amp, 0, 0]), (end - 0.2, [-12 if k != "ward" else 10, 0, 0]), (end, [0, 0, 0])])
            add(body, "scale", [(0, [1, 1, 1]), (hit, [swell, swell if k != "ward" else 1.05, swell]), (end - 0.2, [swell, swell, swell]), (end, [1, 1, 1])])
            for h in head:
                add(h, "rotation", [(0, [0, 0, 0]), (hit, [(-45 if k != "ward" else 20) * amp, 0, 0]), (hit + 0.2, [-40 * amp if k != "ward" else 20, tw * 0.6, 0]), (end, [0, 0, 0])])
            for j in jaws:
                add(j, "rotation", [(0, [0, 0, 0]), (hit, [-65 * amp, 0, 0]), (end - 0.2, [-55, 0, 0]), (end, [0, 0, 0])])
            for bone in arms_l:
                add(bone, "rotation", [(0, [0, 0, 0]), (hit, [(-40 if k != "ward" else -80) * amp, 0, -55 if k != "ward" else 30]), (end, [0, 0, 0])])
            for bone in arms_r:
                add(bone, "rotation", [(0, [0, 0, 0]), (hit, [(-40 if k != "ward" else -80) * amp, 0, 55 if k != "ward" else -30]), (end, [0, 0, 0])])
            for w in wings_l:
                add(w, "rotation", [(0, [0, 0, 0]), (hit, [0, 0, 75 * amp]), (end, [0, 0, 0])])
            for w in wings_r:
                add(w, "rotation", [(0, [0, 0, 0]), (hit, [0, 0, -75 * amp]), (end, [0, 0, 0])])
        out[f"attack.{a['slug']}"] = {"loop": False, "animation_length": round(end, 2), "bones": B}
    return out
