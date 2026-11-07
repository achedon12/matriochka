"""Hand-made animations for every attack of every boss (GeckoLib / Blockbench format).

The bosses of tools/bosses_hd.py share eight generic animations (idle, walk, charge, slam, cast, strike, phase,
rest). This module gives each named attack of each boss its own three-part move, keyed by hand on the real
bones of its rig:

  attack.<boss>.<slug>.windup   the telegraph: the boss shows what is coming, then holds the pose
  attack.<boss>.<slug>.strike   the release itself
  attack.<boss>.<slug>.recover  the way back to rest, sized to fill the boss's opening (the vulnerable window)

plus misc.<boss>.phase (the phase change), misc.<boss>.death (the fall) and misc.<boss>.awaken (out of its shell). The moves live in
tools/boss_moves_a.py and tools/boss_moves_b.py; this file holds the kit they are written with, the timing
read from Defs.java and the generated BossAnims.java that MatrioBoss uses to trigger them.

Conventions (GeckoLib, in the model's own coordinates, front is -Z, up is +Y, 16 units to a block):
  rotation X  a hanging limb swings forward with a negative angle (-90 points it ahead, -170 overhead);
              a bone that stands up from its pivot (a torso, a head) leans forward with a positive angle;
              a lower jaw opens with a positive angle.
  rotation Z  a hanging limb on the +X side swings out with a positive angle, on the -X side with a negative one.
  rotation Y  a positive angle turns the front toward +X.
  position    in model units, added to the bone; -Z is a step forward.
Keyframed rotations add to the static rotation of the bone. A keyframe's easing shapes the motion that ends on it.

Timing: the state machine of MatrioBoss holds a telegraph of Defs.telegraphTicks(world) (half of it, at least six
ticks, for the light attack; twice for the signature), then executes the attack and opens an opening of
Defs.openingTicks(world) after the medium attack (half of it after the signature; the light attack has none).
The action controller blends three ticks into every animation it starts, and once more between the strike and
the recover it chains after it, so each cut here is that much shorter than its window.
"""
import json
import math
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFS = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Defs.java")
JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/BossAnims.java")

BLEND = 3 / 20          # the action controller's transition, in seconds
LIGHT_RELEASE = 0.95    # strike + recover of the light attack (no opening follows it)
PHASE_SECONDS = 2.0     # the PHASE state of MatrioBoss lasts 40 ticks
DEATH_TICKS = 40        # MatrioBoss keeps a fallen boss this long before removing it

EASE = {
    "sine": "easeInOutSine", "in": "easeInQuad", "out": "easeOutQuad", "io": "easeInOutQuad",
    "cin": "easeInCubic", "cout": "easeOutCubic", "cio": "easeInOutCubic", "qin": "easeInQuart", "qout": "easeOutQuart",
    "expo": "easeOutExpo", "xin": "easeInExpo", "back": "easeOutBack", "inback": "easeInBack", "ioback": "easeInOutBack",
    "elastic": "easeOutElastic", "bounce": "easeOutBounce", "circ": "easeOutCirc", "cirin": "easeInCirc",
    "lin": "linear", "step": "step", None: "catmullrom",
}


# ---------------------------------------------------------------- timing, read from Defs.java
def _tier_table(fn):
    """[(max_world, ticks), ...] parsed from a `public static int fn(int world)` of if/return lines."""
    src = open(DEFS, encoding="utf-8").read()
    m = re.search(r"static int " + fn + r"\(int world\)\s*\{(.*?)\n\t\}", src, re.S)
    rows = [(int(a), int(b)) for a, b in re.findall(r"if \(world <= (\d+)\) return (\d+);", m.group(1))]
    last = int(re.findall(r"\n\s*return (\d+);", m.group(1))[-1])
    return rows, last


def _lookup(table, world):
    rows, last = table
    for top, v in rows:
        if world <= top:
            return v
    return last


TELE = _tier_table("telegraphTicks")
OPEN = _tier_table("openingTicks")


def telegraph_ticks(world):
    return _lookup(TELE, world)


def opening_ticks(world):
    return _lookup(OPEN, world)


def windows(world):
    """Windup lengths and release budgets (seconds) of the three attack slots for a world's timing tier."""
    tele, opening = telegraph_ticks(world), opening_ticks(world)
    wind = [max(6, tele // 2) / 20, tele / 20, tele * 2 / 20]
    release = [LIGHT_RELEASE, opening / 20, (opening // 2) / 20]
    return [max(0.2, w - BLEND) for w in wind], release


# ---------------------------------------------------------------- clips
def _vec(v):
    if isinstance(v, (int, float)):
        return [v, v, v]
    return list(v)


class Clip:
    """One animation, keyed on a normalised time u in [0, 1] (u * length seconds)."""

    def __init__(self, kit, length, loop=False):
        self.kit = kit
        self.L = round(length, 3)
        self.loop = loop
        self.ch = {}  # (bone, channel) -> {u: (value, ease)}

    def sec(self, s):
        """Seconds to normalised time."""
        return s / self.L

    def _put(self, bone, chan, keys):
        if bone not in self.kit.bones:
            raise KeyError(f"{self.kit.name}: no bone {bone}")
        d = self.ch.setdefault((bone, chan), {})
        for k in keys:
            u = round(min(1.0, max(0.0, k[0])), 4)
            if chan == "scale" and len(k) in (2, 3) and not isinstance(k[1], (list, tuple)):
                val, ease = _vec(k[1]), (k[2] if len(k) > 2 else None)
            elif len(k) in (2, 3):
                val, ease = _vec(k[1]), (k[2] if len(k) > 2 else None)
            else:
                val, ease = [k[1], k[2], k[3]], (k[4] if len(k) > 4 else None)
            d[u] = ([round(float(x), 3) for x in val], ease)
        return self

    def rot(self, bone, *keys):
        """keys: (u, x, y, z[, ease])"""
        return self._put(bone, "rotation", keys)

    def pos(self, bone, *keys):
        return self._put(bone, "position", keys)

    def scl(self, bone, *keys):
        """keys: (u, s[, ease]) for a uniform scale or (u, x, y, z[, ease])"""
        return self._put(bone, "scale", keys)

    def rots(self, bones, *keys):
        for b in bones:
            self.rot(b, *keys)
        return self

    def value(self, bone, chan, u):
        """The keyed value of a channel at u (linear between keys), or its rest value."""
        d = self.ch.get((bone, chan))
        rest = [1, 1, 1] if chan == "scale" else [0, 0, 0]
        if not d:
            return rest
        ks = sorted(d.items())
        if u <= ks[0][0]:
            return list(ks[0][1][0])
        for (u0, (v0, _)), (u1, (v1, _)) in zip(ks, ks[1:]):
            if u <= u1:
                p = 0 if u1 == u0 else (u - u0) / (u1 - u0)
                return [a + (b - a) * p for a, b in zip(v0, v1)]
        return list(ks[-1][1][0])

    def end_pose(self):
        return {key: self.value(key[0], key[1], 1.0) for key in self.ch}

    # -------- composition helpers
    def start_from(self, other):
        """Begins every channel of `other` from where `other` ends (a strike from its windup, a recover from its
        strike); channels already keyed at u=0 keep their key."""
        for (bone, chan), v in other.end_pose().items():
            d = self.ch.setdefault((bone, chan), {})
            if 0.0 not in d:
                d[0.0] = ([round(x, 3) for x in v], None)
        return self

    def settle(self, ease="sine"):
        """Ends every channel at rest (u=1) unless it is keyed there already."""
        for (bone, chan), d in self.ch.items():
            if 1.0 not in d:
                d[1.0] = ([1, 1, 1] if chan == "scale" else [0, 0, 0], ease)
        return self

    def hold(self, u):
        """Every channel keeps its value from u to the end (a held pose)."""
        for (bone, chan), d in self.ch.items():
            if 1.0 not in d:
                d[1.0] = ([round(x, 3) for x in self.value(bone, chan, u)], "lin")
        return self

    def tremble(self, bone, chan, u0, u1, amp, n=6, axis=(1, 0, 0)):
        """Adds a shiver between u0 and u1 on top of what the channel already does there."""
        for i in range(1, n):
            u = u0 + (u1 - u0) * i / n
            base = self.value(bone, chan, u)
            s = amp * (1 if i % 2 else -1)
            self.ch.setdefault((bone, chan), {})[round(u, 4)] = ([round(b + s * a, 3) for b, a in zip(base, axis)], "sine")
        return self

    def follow(self, bones, keys, lag=0.06, gain=1.0, chan="rotation"):
        """Keys the same motion down a chain (a tail, a chain, a cape): each link lags `lag` seconds behind the one
        before it and moves `gain` times as far, so the motion travels down to the tip."""
        for i, b in enumerate(bones):
            shift, g = self.sec(lag * i), gain ** i
            ks = []
            for k in keys:
                u = k[0] + (shift if 0 < k[0] else 0)
                v = [x * g for x in (k[1:4] if len(k) >= 4 else _vec(k[1]))]
                e = k[4] if len(k) > 4 else None
                if u <= 1.0:
                    ks.append((u, v[0], v[1], v[2], e))
            self._put(b, chan, ks)
        return self

    def json(self):
        bones = {}
        for (bone, chan), d in sorted(self.ch.items()):
            out = {}
            for u, (v, ease) in sorted(d.items()):
                t = f"{u * self.L:.3f}"
                name = EASE.get(ease, ease)
                if name in ("catmullrom", "linear", "step"):
                    out[t] = {"post": v, "lerp_mode": name}
                else:
                    out[t] = {"post": v, "easing": name}
            bones.setdefault(bone, {})[chan] = out
        loop = {"hold": "hold_on_last_frame", "loop": True}.get(self.loop, False)
        return {"loop": loop, "animation_length": self.L, "bones": bones}


# ---------------------------------------------------------------- the kit: one rig, its timing, leg solvers
class Kit:
    def __init__(self, rig, world):
        self.rig = rig
        self.name = rig.name
        self.bones = {b["name"]: b for b in rig.bones}
        self.world = world

    def role(self, r):
        return list(self.rig.roles.get(r, []))

    def pivot(self, bone):
        return self.bones[bone]["pivot"]

    def has(self, bone):
        return bone in self.bones

    # -------- two-link legs that keep their feet on the ground
    def leg_ik(self, thigh, shin, drop=0.0, fwd=0.0, lift=0.0, ground=0.0):
        """Thigh and shin X rotations that put the foot of a hanging two-segment leg `fwd` units ahead of the hip
        (negative: behind) and `lift` above the ground while the hip is lowered by `drop`."""
        hy = self.pivot(thigh)[1]
        ky = self.pivot(shin)[1]
        l1, l2 = hy - ky, ky - ground
        h = (hy - ground) - drop - lift
        d = min(l1 + l2 - 1e-3, math.hypot(h, fwd))
        # angle of the hip-foot line from straight down, forward positive
        base = math.atan2(fwd, h)
        a1 = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
        t1 = base + a1                                   # knee ahead of the hip-foot line
        kx, ky2 = l1 * math.sin(t1), -l1 * math.cos(t1)
        t2 = math.atan2(fwd - kx, ky2 + h)               # absolute shin angle from straight down
        return -math.degrees(t1), -math.degrees(t2 - t1)

    def stance(self, clip, u, legs, drop=0.0, z=0.0, ease="sine", body=None, body_pos=None):
        """Keys the legs (and the body) at u: legs = [(thigh, shin, fwd, lift)], drop lowers the hips, z moves the
        hips forward (negative) or back. The body gets the same drop and z unless body_pos overrides it."""
        for thigh, shin, fwd, lift in legs:
            a, b = self.leg_ik(thigh, shin, drop, fwd, lift)
            clip.rot(thigh, (u, a, 0, 0, ease))
            clip.rot(shin, (u, b, 0, 0, ease))
            clip.pos(thigh, (u, 0, -drop, z, ease))
        for bd in ([body] if isinstance(body, str) else (body or [])):
            p = body_pos if body_pos is not None else (0, -drop, z)
            clip.pos(bd, (u, p[0], p[1], p[2], ease))
        return clip

    def clip(self, length, loop=False):
        return Clip(self, length, loop)


# ---------------------------------------------------------------- registry of the moves
MOVES = {}


def boss(boss_id, world, tiers=None):
    """Registers the moves of one boss: fn(kit, windups, releases) -> {"slugs": [3 slugs], "clips": {name: Clip}}.
    `tiers` lists the worlds whose timing the boss borrows (the Unfinished, the Shadow): one cut per tier."""
    def deco(fn):
        MOVES[boss_id] = (world, tiers, fn)
        return fn
    return deco


def _load():
    import boss_moves_a  # noqa: F401
    import boss_moves_b  # noqa: F401


def tiers_of(boss_id):
    world, tiers, _ = MOVES[boss_id]
    if not tiers:
        return [None]
    seen, out = set(), []
    for w in tiers:
        t = (telegraph_ticks(w), opening_ticks(w))
        if t not in seen:
            seen.add(t)
            out.append(w)
    return out


AWAKEN_SECONDS = 2.6


def awaken_clip(kit):
    """misc.<boss>.awaken: the boss comes out of its shell. Folded small and low, it swells past its size as it
    rises and rears back, throws its head up and roars with its arms and wings flung out, then settles into its
    stance. Built from the rig's own bones, so every boss wakes in its own shape; played as its introduction starts."""
    c = kit.clip(AWAKEN_SECONDS - BLEND)
    roots = [b["name"] for b in kit.rig.bones if not b.get("parent")]
    for r in roots:
        c.scl(r, (0, 0.35), (0.4, 1.1, "cout"), (0.58, 0.96, "sine"), (0.74, 1.0, "sine"))
        c.pos(r, (0, 0, -10, 0), (0.4, 0, 2.5, 0, "cout"), (0.6, 0, 0, 0, "sine"))
    body = kit.role("body") or roots
    for b in body[:1]:
        c.rot(b, (0, 38, 0, 0), (0.42, -14, 0, 0, "cout"), (0.7, -6, 0, 0, "sine"), (1, 0, 0, 0, "sine"))
    for h in kit.role("head"):
        c.rot(h, (0, 34, 0, 0), (0.45, 0, 0, 0, "sine"), (0.55, -30, 0, 0, "cout"), (0.84, -24, 0, 0, "sine"), (1, 0, 0, 0, "sine"))
        c.tremble(h, "rotation", 0.56, 0.82, 2.5, n=8, axis=(0, 1, 0))
    for j in kit.role("jaw"):
        c.rot(j, (0, 0, 0, 0), (0.5, 0, 0, 0), (0.58, 32, 0, 0, "cout"), (0.84, 26, 0, 0, "sine"), (1, 0, 0, 0, "sine"))
    for side, sign in (("arm_l", 1), ("arm_r", -1)):
        for a in kit.role(side):
            c.rot(a, (0, 20, 0, -sign * 10), (0.5, -24, 0, sign * 55, "cout"), (0.84, -18, 0, sign * 44, "sine"), (1, 0, 0, 0, "sine"))
    for side, sign in (("wing_l", 1), ("wing_r", -1)):
        for wg in kit.role(side):
            c.rot(wg, (0, 0, 0, -sign * 30), (0.45, 0, 0, sign * 62, "cout"), (0.6, 0, 0, -sign * 8, "sine"),
                  (0.76, 0, 0, sign * 50, "cout"), (1, 0, 0, 0, "sine"))
    for o in kit.role("orbit"):
        c.scl(o, (0, 0.0), (0.5, 0.0), (0.7, 1.15, "cout"), (0.85, 1.0, "sine"))
    for t in kit.role("tail"):
        c.rot(t, (0, 0, 0, 0), (0.5, 0, 28, 0, "cout"), (0.7, 0, -20, 0, "sine"), (1, 0, 0, 0, "sine"))
    return c


def build(rig):
    """The boss's own animations, ready to merge into its animation file ({} for a rig without moves)."""
    _load()
    if rig.name not in MOVES:
        return {}
    world, tiers, fn = MOVES[rig.name]
    out = {}
    slugs = None
    for w in tiers_of(rig.name):
        kit = Kit(rig, w if w is not None else world)
        wind, rel = windows(kit.world)
        res = fn(kit, wind, rel)
        slugs = res["slugs"]
        suffix = f".w{w}" if w is not None else ""
        for name, clip in res["clips"].items():
            if name.startswith("misc."):
                if w is None or w == tiers_of(rig.name)[0]:
                    out[name] = clip.json()
            else:
                out[name + suffix] = clip.json()
    MOVES_SLUGS[rig.name] = slugs
    out[f"misc.{rig.name}.awaken"] = awaken_clip(Kit(rig, world)).json()
    return out


MOVES_SLUGS = {}


def write_java():
    """content/BossAnims.java: the attack slugs of every boss and the telegraph tiers of the bosses that borrow
    their timing from other worlds, so MatrioBoss can name the animation of the attack it chose."""
    _load()
    ids = sorted(MOVES)
    L = ["package fr.achedon12.matriochka.content;", "",
         "import java.util.List;", "import java.util.Map;", "",
         "/** Generated by tools/boss_moves.py: the hand-made attack animations of the bosses. Do not edit. */",
         "public final class BossAnims {",
         "\tprivate BossAnims() {}", "",
         "\t/** How long a fallen boss stays before it is removed, so its death animation plays out. */",
         f"\tpublic static final int DEATH_TICKS = {DEATH_TICKS};", "",
         "\t/** The light, medium and signature attack of each boss, as named in its animation file:",
         "\t * attack.<boss>.<slug>.windup, .strike and .recover. */",
         "\tpublic static final Map<String, List<String>> SLUGS = Map.ofEntries("]
    rows = []
    for b in ids:
        s = MOVES_SLUGS.get(b)
        if s is None:
            raise RuntimeError(f"build the rig of {b} before writing BossAnims.java")
        rows.append(f"\t\tMap.entry(\"{b}\", List.of({', '.join(chr(34) + x + chr(34) for x in s)}))")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("")
    L.append("\t/** Bosses whose timing follows a borrowed world: one cut of each attack per timing tier, named with the")
    L.append("\t * suffix .w<world> of the first world of that tier (same Defs.telegraphTicks and Defs.openingTicks). */")
    L.append("\tpublic static final Map<String, List<Integer>> TIERS = Map.ofEntries(")
    rows = []
    for b in ids:
        if MOVES[b][1]:
            rows.append(f"\t\tMap.entry(\"{b}\", List.of({', '.join(str(w) for w in tiers_of(b))}))")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("}")
    os.makedirs(os.path.dirname(JAVA), exist_ok=True)
    open(JAVA, "w", encoding="utf-8").write("\n".join(L) + "\n")
