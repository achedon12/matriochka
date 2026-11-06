#!/usr/bin/env python3
"""Balance check: the numbers of tools/content.py and tools/attacks.py against the design's targets.

Usage (from the repository root):
    python3 tools/balance.py                         # summary and outliers on stdout
    python3 tools/balance.py --baseline v0.3.0 --label 0.3.0 --write docs-wiki-drafts/Balance.md
                                                     # the report, before (that git ref) and after (the working tree)

For every world it computes, from the content table and the rules the Java code applies (mirrored below, see the
`# mirrors` comments):
  - the player of that world: health, armor, toughness and damage with the world's gear and a Berserker weapon at the
    class level allowed on arrival (design/conception.md, "Équilibrage du joueur" and "Limites selon la progression");
  - every creature: its health and damage against the reference creature (20 health, 5 damage, x1.35 and x1.20 per
    world), the hits each side needs to kill the other and the seconds it takes;
  - the boss: health and strong hit against the reference boss (500 health, 12 damage), the hits of a strong blow a
    player survives, and the length of the fight for 1, 2 and 4 players, simulated tick by tick with the boss's
    attack cycle (cooldowns, telegraphs, openings x1.5, x0.75 otherwise, phase changes);
  - the soul budget (design/regles.txt: 100 boss + 100 chests + 50 elites + 50 altar = 300 per world) against what
    the class upgrades of that world cost;
  - an estimate of the combat time of the world (creatures the quests and the gear ask for, then the boss).
Then it flags the outliers. Standard library only.
"""
import argparse
import math
import os
import subprocess
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- design targets
REF_MOB_HP, REF_MOB_DMG = 20.0, 5.0
REF_BOSS_HP, REF_BOSS_DMG = 500.0, 12.0
# design/conception.md, "Équilibrage du joueur": hits to kill a reference creature, its hits before death, strong
# boss hits before death, at worlds 1, 5 and 10 (interpolated in between)
TARGET_HITS_TO_KILL = {1: 2.9, 5: 3.5, 10: 5.0}
TARGET_MOB_HITS_TO_DIE = {1: 8.9, 5: 7.9, 10: 8.5}
TARGET_BOSS_HITS_TO_DIE = {1: 2.9, 5: 2.2, 10: 3.3}
# design/conception.md, "Bonus de classe max" per world (class cap on arrival)
CLASS_BONUS = {1: 0, 2: 0, 3: 0.10, 4: 0.10, 5: 0.20, 6: 0.20, 7: 0.35, 8: 0.35, 9: 0.50, 10: 0.50}
# design/regles.txt, "Sources d'âme"
SOUL_TARGET = 300
SOUL_PLAN = dict(boss=100, chests=10 * 10, elites=10 * 5, altar=5 * 10)
REF_FINAL_HP = 1000.0  # the Unfinished: 1000 x 1.35^9 = 14894 over ten shells
# Tolerances: how far a creature may stray from the reference before it is flagged
HP_BAND = {False: (0.6, 2.2), True: (1.5, 3.2)}      # (regular, elite) x reference health
# x reference damage, by tier: the tiers ask for forgiving learning worlds and danger growing through patterns
DMG_BAND = {
    "learning": {False: (0.55, 1.2), True: (1.0, 1.4)},
    "mastery": {False: (0.55, 1.4), True: (1.1, 1.5)},
    "expertise": {False: (0.55, 1.5), True: (1.2, 1.6)},
    "final": {False: (0.55, 1.5), True: (1.2, 1.6)},
}
MIN_HITS_TO_DIE = {False: 4.0, True: 3.0}            # basic hits a geared player survives
MAX_BURST = 2.6                                      # strongest move (mult x hits) in reference hits
TOLERANCE = 0.25                                     # +-25% around the player-side targets

# ---------------------------------------------------------------- rules mirrored from the Java code
BOSS_ARMOR = 8                    # mirrors MatrioBoss.attributes
MOB_ARMOR = {False: 2, True: 6}   # mirrors MatrioMob.attributes
BONUS = [0, 0, 0.10, 0.20, 0.35, 0.50]  # mirrors GearClasses.BONUS
UPGRADE_COST = [0, 0, 10, 30, 90, 270]  # mirrors GearClasses.UPGRADE_COST
SHARD_COST = [0, 0, 1, 1, 2, 2]         # mirrors GearClasses.SHARD_COST
SHARDS_PER_BOSS = None                  # mirrors MatrioBoss.SHELL_SHARDS (read from the code)
ELITE_SOULS = 5                         # mirrors MatrioMob.die
PLAYER_ATTACK_SPEED = 4 - 2.4           # mirrors ModContent.makeItem: p.sword(..., -2.4f)
UPTIME = 0.6                            # share of the chase a solo player spends hitting (the rest dodging)
# talents (tools/content.py TALENTS, applied by replay/Talents.java)
LOW_HEALTH_SHARE = 0.25                 # share of the blows struck below half health (Berserker rage)
SNEAK_SHARE = 0.5                       # share of a Prowler's blows struck sneaking
DODGE_CAP, LASTSTAND_CAP = 0.3, 0.6     # mirrors Talents: dodge chance and the share of a blow healed back below 30%
TALENT_FIGHT_CUT = 0.25                 # talents may shorten a boss fight by this much at most (the design's tolerance)


def class_level(world):
    """Mirrors GearClasses.maxLevel, for the progression on arrival (the previous world's boss beaten)."""
    beaten = world - 1
    return 5 if beaten >= 8 else 4 if beaten >= 6 else 3 if beaten >= 4 else 2 if beaten >= 2 else 1


def telegraph(world):  # mirrors Defs.telegraphTicks
    return 30 if world <= 3 else 20 if world <= 6 else 15 if world <= 9 else 12


def opening(world):  # mirrors Defs.openingTicks
    return 60 if world <= 3 else 50 if world <= 6 else 40 if world <= 9 else 30


def after_armor(dmg, armor, tough):
    """Minecraft's armor formula (CombatRules.getDamageAfterAbsorb)."""
    f = 2 + tough / 4
    g = max(armor * 0.2, min(armor - dmg / f, 20))
    return dmg * (1 - g / 25)


def interp(table, w):
    keys = sorted(table)
    if w <= keys[0]:
        return table[keys[0]]
    for a, b in zip(keys, keys[1:]):
        if a <= w <= b:
            return table[a] + (table[b] - table[a]) * (w - a) / (b - a)
    return table[keys[-1]]


# ---------------------------------------------------------------- loading
def load_modules(ref=None):
    """content and attacks, from the working tree or from a git ref."""
    if ref is None:
        sys.path.insert(0, TOOLS)
        import content
        import attacks
        java = ""
        for f in ("gear/GearClasses.java", "entity/MatrioBoss.java"):
            java += open(os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka", f), encoding="utf-8").read()
        return content, attacks, java

    def show(path):
        return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout

    c = types.ModuleType("content_" + ref)
    exec(compile(show("tools/content.py"), "content.py@" + ref, "exec"), c.__dict__)
    a = types.ModuleType("attacks_" + ref)
    # attacks.describe imports content lazily; the balance never calls it
    exec(compile(show("tools/attacks.py"), "attacks.py@" + ref, "exec"), a.__dict__)
    return c, a, show("src/main/java/fr/achedon12/matriochka/gear/GearClasses.java") + show("src/main/java/fr/achedon12/matriochka/entity/MatrioBoss.java")


def shards_per_boss(java):
    import re
    m = re.search(r"SHELL_SHARDS = (\d+)", java) or re.search(r'item\("shell_shard"\), (\d+)\)', java)
    return int(m.group(1)) if m else 2


# ---------------------------------------------------------------- the player
def player(content, java, world, gear_world=None):
    """Health, armor, toughness, hit damage and swing time of a geared player in a world."""
    gw = world if gear_world is None else gear_world
    if gw <= 0:  # the Surface: iron
        dmg, armor, tough, hp_bonus = 6, 15, 0, 0
        level = 1
    else:
        dmg, armor, tough, hp_bonus = content.GEAR[gw]
        level = class_level(world)
        if gw == 7:
            # mirrors ModContent.material: the Diving suit has no helmet, a snorkel helmet takes the head
            helmet = round(armor * 0.18)
            tank = {s[0]: s for s in content.SNORKELS}["cobalt_snorkel"]
            armor = armor - helmet + tank[7]
            tough = tough * 3 / 4 + tank[8]
            hp_bonus = hp_bonus - round(hp_bonus * 0.15)
        else:
            # mirrors ModContent.makeItem: the bonus health is spread over the pieces and rounded
            hp_bonus = sum(round(hp_bonus * s) for s in (0.4, 0.3, 0.15, 0.15))
    m = 1 + BONUS[level]
    base = dmg - 1  # the weapon's attack damage modifier (the player's own 1 point is added after)
    # mirrors GearClasses.bonuses, Berserker weapon
    if "0.08 + (mult - 1)" in java:
        extra = max(1, base * (0.08 + (m - 1)))
    else:
        extra = max(1, base * 0.08) * m
    speed = PLAYER_ATTACK_SPEED + 0.08 * m
    return dict(hp=20 + hp_bonus, armor=armor, tough=tough, dmg=dmg + extra, raw=dmg, swing=20 / speed, level=level)


# ---------------------------------------------------------------- creatures
def mob_rows(content, attacks, java):
    rows = []
    for m in content.MOBS:
        w = m["world"]
        p = player(content, java, w)
        early = player(content, java, w, w - 1)
        ref_hp, ref_dmg = REF_MOB_HP * 1.35 ** (w - 1), REF_MOB_DMG * 1.20 ** (w - 1)
        armor = MOB_ARMOR[m["elite"]]
        hit = after_armor(p["dmg"], armor, 0)
        hits_to_kill = m["hp"] / hit
        taken = after_armor(m["dmg"], p["armor"], p["tough"])
        interval = max(6, int(20 / (1 + 0.06 * (w - 1))))  # mirrors MatrioMob's melee interval
        hits_to_die = p["hp"] / taken
        moves = attacks.full(m["id"])
        burst = max((a.get("m", 0) or 0) * a.get("n", 1) for a in moves)
        move_dps = sum((a.get("m", 0) or 0) * a.get("n", 1) * taken / a["cd"] for a in moves if a.get("m"))
        dps = taken * 20 / interval * 0.5 + move_dps  # melee half the time, the moves on their cooldowns
        rows.append(dict(
            id=m["id"], world=w, elite=m["elite"], hp=m["hp"], dmg=m["dmg"],
            hp_ratio=m["hp"] / ref_hp, dmg_ratio=m["dmg"] / ref_dmg,
            hits_to_kill=hits_to_kill, kill_s=math.ceil(hits_to_kill) * p["swing"] / 20,
            hits_to_kill_early=m["hp"] / after_armor(early["dmg"], armor, 0),
            hits_to_die=hits_to_die, die_s=p["hp"] / dps, burst=burst,
            burst_share=burst * taken / p["hp"]))
    return rows


def ref_mob(content, java, w):
    p = player(content, java, w)
    hp, dmg = REF_MOB_HP * 1.35 ** (w - 1), REF_MOB_DMG * 1.20 ** (w - 1)
    return dict(hits_to_kill=hp / p["dmg"], hits_to_die=p["hp"] / after_armor(dmg, p["armor"], p["tough"]))


# ---------------------------------------------------------------- bosses
def fight(boss, p, players, extra_hp=0.0):
    """Ticks to bring the boss down: its attack cycle (mirrors MatrioBoss.aiStep/chooseAttack) against the players' blows."""
    w = boss["world"]
    hp = boss["hp"] * (1 + 0.6 * (players - 1)) + extra_hp
    total, pace = hp, 1 + 0.05 * (players - 1)
    phases = list(boss["phases"])
    phase, state, st, attack = 0, "chase", 0, 0
    last = [-10 ** 6] * 3
    hit = after_armor(p["dmg"], BOSS_ARMOR, 0)
    swing = p["swing"]
    next_swing = [i * swing / players for i in range(players)]
    t = 0
    rng = 12345
    while hp > 0 and t < 20 * 60 * 40:
        t += 1
        st += 1
        if state == "chase":
            speed_up = phase * 20
            sig = t - last[2] > (400 - speed_up) / pace
            med = t - last[1] > (160 - speed_up / 2) / pace
            light = t - last[0] > (80 - speed_up / 4) / pace
            rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
            choice = -1
            if sig and (phase > 0 or rng % 3 == 0):
                choice = 2
            elif light:
                choice = 0
            elif med:
                choice = 1
            if choice >= 0 and st >= 10:
                attack, state, st = choice, "telegraph", 0
        elif state == "telegraph":
            tele = telegraph(w) * (2 if attack == 2 else 1)
            if attack == 0:
                tele = max(6, tele // 2)
            if st >= tele:
                last[attack] = t
                state, st = ("chase" if attack == 0 else "opening"), 0
        elif state == "opening":
            if st >= opening(w) * (1 if attack == 2 else 2) // 2:
                state, st = "chase", 0
        elif state == "phase":
            if st >= 40:
                state, st = "chase", 0
        # the players' blows: every one in the opening, a share of them otherwise; none while it changes phase
        for i in range(players):
            if t >= next_swing[i]:
                next_swing[i] += swing
                if state == "phase":
                    continue
                mult = 1.5 if state == "opening" else 0.75
                taken = hit * mult
                # talents: a second blow of a share of what this one dealt, through the boss's multiplier and armor again
                extra = p.get("extra", 0) + p.get("boss", 0) + (p.get("execute", 0) if hp - taken < total * 0.25 else 0)
                if extra > 0:
                    taken += after_armor(taken * extra * mult, BOSS_ARMOR, 0)
                hp -= taken * (1 if state == "opening" else UPTIME)
        if phase < len(phases) and hp / total <= phases[phase]:
            phase += 1
            state, st = "phase", 0
    return t


def boss_rows(content, java):
    rows = []
    for b in content.BOSSES:
        w = b["world"]
        p = player(content, java, w)
        ref_hp = (REF_FINAL_HP if w == 10 else REF_BOSS_HP) * 1.35 ** (w - 1) if w > 0 else b["hp"]
        ref_dmg = REF_BOSS_DMG * 1.20 ** (w - 1) if w > 0 else b["dmg"]
        strong = after_armor(b["dmg"], p["armor"], p["tough"])
        extra = 0.0
        if b["id"] == "spore_queen":
            # its second phase hides behind three Chitin Guards (the nodes) to kill first
            guard = next(m for m in content.MOBS if m["id"] == "chitin_guard")
            extra = 3 * guard["hp"]
        t = {n: fight(b, p, n, extra) / 20 / 60 for n in (1, 2, 4)}
        rows.append(dict(id=b["id"], world=w, hp=b["hp"], dmg=b["dmg"], hp_ratio=b["hp"] / ref_hp, dmg_ratio=b["dmg"] / ref_dmg,
                         hits_to_kill=b["hp"] / after_armor(p["dmg"], BOSS_ARMOR, 0), strong_hits=p["hp"] / strong,
                         t1=t[1], t2=t[2], t4=t[4]))
    return rows


# ---------------------------------------------------------------- souls and time
def souls(content, java, w):
    """Souls and Shell Shards a player has on reaching world w against what its Berserker weapon (and a full set)
    costs to bring from level 1 to the class cap of that world. Gear is new in every world, so it starts at level 1."""
    def income(n):
        quests = sum(q[8][2] for q in content.QUESTS if q[1] == n and q[8][0] == "souls")
        if n == 0:  # the Surface: the Guardian and its quest, no elites nor chests
            return dict(boss=100, quests=quests, elites=0, altar=0, chests=0)
        return dict(boss=100, quests=quests, elites=SOUL_PLAN["elites"], altar=SOUL_PLAN["altar"], chests=SOUL_PLAN["chests"])
    per = shards_per_boss(java)
    level = class_level(w)
    weapon = sum(UPGRADE_COST[2:level + 1])
    shards = sum(SHARD_COST[2:level + 1])
    need_shards = sum(sum(SHARD_COST[2:class_level(n) + 1]) for n in range(1, w + 1))
    need_souls = sum(sum(UPGRADE_COST[2:class_level(n) + 1]) for n in range(1, w + 1))
    have_souls = sum(sum(income(n).values()) for n in range(0, w))
    mine = income(w)
    return dict(income=mine, total=sum(mine.values()), quests=mine["quests"], level=level, weapon=weapon, set=5 * weapon,
                shards=shards, need_shards=need_shards, have_shards=per * w, need_souls=need_souls, have_souls=have_souls)


def combat_minutes(content, mobs, boss, w):
    """Creatures the world's quests ask to kill and the gear's resource farmed from drops (design: 60% common,
    15% rare), each at the time it takes to kill plus 10 s to reach it, then the boss."""
    by_id = {m["id"]: m for m in mobs}
    kills = 0.0
    seconds = 0.0
    for q in content.QUESTS:
        if q[1] == w and q[3][0] == "kill" and q[3][1] in by_id:
            m = by_id[q[3][1]]
            seconds += q[3][2] * (m["kill_s"] + 10)
            kills += q[3][2]
    world_mobs = [m for m in mobs if m["world"] == w and not m["elite"]]
    if world_mobs:
        avg = sum(m["kill_s"] for m in world_mobs) / len(world_mobs)
        # weapon 8 + set 24 pieces of the gear resource, about half from drops at 15% (rare) per kill
        farm = 16 / 0.15
        seconds += farm * (avg + 10)
        kills += farm
    return dict(kills=kills, minutes=seconds / 60 + boss["t1"])



# ---------------------------------------------------------------- talents
def talents_at(content, cls, world):
    """The summed effects of every talent of a class open on arrival in a world (mirrors Talents.compute and the gates
    of TALENT_TIERS: the highest boss beaten is the previous world's), with what they cost."""
    sums, souls, shards = {}, 0, 0
    for _bid, _en, _fr, talents in getattr(content, "TALENTS", {}).get(cls, []):
        for tier, t in enumerate(talents):
            cost, sh, gate = content.TALENT_TIERS[tier]
            if gate > world - 1:
                break
            sums[t[3]] = sums.get(t[3], 0) + t[4]
            souls += cost
            shards += sh
    return sums, souls, shards


def with_talents(p, sums):
    """The design player with a class's talents: attribute talents change the stats (mirrors Talents.ATTRS), the others
    become extra blows (mirrors Talents.strike) and a share of the damage taken back."""
    q = dict(p)
    q["dmg"] = p["dmg"] * (1 + sums.get("damage", 0))
    q["swing"] = p["swing"] / (1 + sums.get("attack_speed", 0))
    q["hp"] = p["hp"] + sums.get("max_health", 0)
    q["absorb"] = sums.get("absorb", 0)
    q["armor"] = p["armor"] + sums.get("armor", 0)
    q["tough"] = p["tough"] + sums.get("toughness", 0)
    q["dodge"] = min(DODGE_CAP, sums.get("dodge", 0))
    q["laststand"] = min(LASTSTAND_CAP, sums.get("laststand", 0))
    # extra damage on top of a blow, as a share of what the blow dealt
    q["extra"] = sums.get("rage", 0) * LOW_HEALTH_SHARE + sums.get("sneak", 0) * SNEAK_SHARE
    q["crit"], q["execute"], q["boss"] = sums.get("crit", 0), sums.get("execute", 0), sums.get("boss", 0)
    return q


def blows(hp, p, armor, boss=False):
    """Blows to bring down hp: the first one carries the crit talents, those that leave it under a quarter the execute
    ones; each extra is a second blow through the armor again (mirrors Talents.strike)."""
    left, n, first = hp, 0, True
    while n < 10000:
        taken = after_armor(p["dmg"], armor, 0)
        extra = p.get("extra", 0) + (p.get("boss", 0) if boss else 0) + (p.get("crit", 0) if first else 0)
        if left - taken < hp * 0.25:
            extra += p.get("execute", 0)
        dealt = taken + (after_armor(taken * extra, armor, 0) if extra > 0 else 0)
        if dealt >= left:
            return n + left / dealt
        left, n, first = left - dealt, n + 1, False
    return n


def survives(p, taken):
    """Blows of a given damage a player takes before death: absorption first, then the health, less what the last
    stand heals back under 30%, more with the dodge chance."""
    hp = p["hp"] + p.get("absorb", 0)
    high = (hp - 0.3 * p["hp"]) / taken
    low = 0.3 * p["hp"] / (taken * (1 - p.get("laststand", 0)))
    return (high + low) / (1 - p.get("dodge", 0))


def talent_rows(content, java, bosses):
    """Per class and world: the reference creature and boss measures with the class's open talents."""
    rows = []
    by_world = {b["world"]: b for b in bosses}
    for cls in getattr(content, "TALENTS", {}):
        for w in range(1, 11):
            sums, souls, shards = talents_at(content, cls, w)
            base = player(content, java, w)
            p = with_talents(base, sums)
            ref_hp, ref_dmg = REF_MOB_HP * 1.35 ** (w - 1), REF_MOB_DMG * 1.20 ** (w - 1)
            b = next(x for x in content.BOSSES if x["world"] == w)
            extra = 3 * next(m for m in content.MOBS if m["id"] == "chitin_guard")["hp"] if b["id"] == "spore_queen" else 0.0
            t1 = fight(b, p, 1, extra) / 20 / 60
            # the nominal class bonus against a boss: the weapon's level, its damage talents and its boss talents
            nominal = 0.08 + BONUS[base["level"]]
            rows.append(dict(cls=cls, world=w, sums=sums, souls=souls, shards=shards,
                             hits_to_kill=blows(ref_hp, p, 0), hits_to_die=survives(p, after_armor(ref_dmg, p["armor"], p["tough"])),
                             strong_hits=survives(p, after_armor(b["dmg"], p["armor"], p["tough"])),
                             t1=t1, base_t1=by_world[w]["t1"], cut=1 - t1 / by_world[w]["t1"],
                             boss_bonus=(1 + nominal) * (1 + sums.get("damage", 0)) * (1 + sums.get("boss", 0)) - 1,
                             speed=sums.get("attack_speed", 0)))
    return rows

# ---------------------------------------------------------------- report
def analyse(ref=None):
    content, attacks, java = load_modules(ref)
    mobs = mob_rows(content, attacks, java)
    bosses = boss_rows(content, java)
    worlds = []
    for w in range(0, 11):
        p = player(content, java, w)
        b = next(x for x in bosses if x["world"] == w)
        tier = next((x["tier"] for x in content.WORLDS if x["n"] == w), "learning")
        worlds.append(dict(world=w, tier=tier, player=p, ref=ref_mob(content, java, w) if w else None, boss=b,
                           souls=souls(content, java, w), combat=combat_minutes(content, mobs, b, w) if w else None))
    for w in worlds[1:]:
        # the Reaper's soul talents: their share of the souls of the kills (the boss and the elites)
        share = talents_at(content, "reaper", w["world"])[0].get("souls", 0)
        w["souls"]["reaper"] = round(share * (SOUL_PLAN["boss"] + SOUL_PLAN["elites"]))
        w["souls"]["tree"] = talents_at(content, "berserker", w["world"])[1:]
    return dict(mobs=mobs, bosses=bosses, worlds=worlds, talents=talent_rows(content, java, bosses))


def flags(a):
    out = []
    for w in a["worlds"]:
        n = w["world"]
        if n == 0:
            continue
        r = w["ref"]
        for key, target, label in (("hits_to_kill", TARGET_HITS_TO_KILL, "hits to kill the reference creature"),
                                   ("hits_to_die", TARGET_MOB_HITS_TO_DIE, "reference creature hits before death")):
            t = interp(target, n)
            if abs(r[key] / t - 1) > TOLERANCE:
                out.append(f"World {n}: {label} {r[key]:.1f}, design {t:.1f}")
        b = w["boss"]
        t = interp(TARGET_BOSS_HITS_TO_DIE, n)
        if abs(b["strong_hits"] / t - 1) > TOLERANCE:
            out.append(f"World {n}: strong boss hits before death {b['strong_hits']:.1f}, design {t:.1f}")
        if abs(b["hp_ratio"] - 1) > 0.02 or abs(b["dmg_ratio"] - 1) > 0.02:
            out.append(f"World {n}: {b['id']} off the reference boss (health x{b['hp_ratio']:.2f}, damage x{b['dmg_ratio']:.2f})")
    tiers = {w["world"]: w["tier"] for w in a["worlds"]}
    for m in a["mobs"]:
        e = m["elite"]
        lo, hi = HP_BAND[e]
        if not lo <= m["hp_ratio"] <= hi:
            out.append(f"World {m['world']}: {m['id']} health x{m['hp_ratio']:.2f} of the reference creature (band {lo}-{hi})")
        lo, hi = DMG_BAND[tiers[m["world"]]][e]
        if not lo - 0.005 <= m["dmg_ratio"] <= hi + 0.005:
            out.append(f"World {m['world']}: {m['id']} damage x{m['dmg_ratio']:.2f} of the reference creature ({tiers[m['world']]} band {lo}-{hi})")
        if m["hits_to_die"] < MIN_HITS_TO_DIE[e]:
            out.append(f"World {m['world']}: {m['id']} kills a geared player in {m['hits_to_die']:.1f} basic hits (minimum {MIN_HITS_TO_DIE[e]:.0f})")
        if m["burst"] > MAX_BURST:
            out.append(f"World {m['world']}: {m['id']} has a move worth {m['burst']:.2f} hits (maximum {MAX_BURST})")
    for w in a["worlds"][1:]:
        s = w["souls"]
        if s["total"] < SOUL_TARGET * 0.9:
            out.append(f"World {w['world']}: {s['total']} souls, design about {SOUL_TARGET}")
        if s["need_shards"] > s["have_shards"]:
            out.append(f"World {w['world']}: a Berserker weapon at the cap in every world needs {s['need_shards']} Shell Shards so far, "
                       f"the bosses gave {s['have_shards']}")
        if s["need_souls"] > s["have_souls"]:
            out.append(f"World {w['world']}: the weapons so far need {s['need_souls']} souls, {s['have_souls']} earned")
    # talents: on top of the design player, a class's open talents may move each measure by the tolerance at most, and
    # the hits to kill the reference creature (the design's own Berserker measure) stay in its band
    for r in a.get("talents", []):
        n, cls = r["world"], r["cls"].capitalize()
        ref = next(w for w in a["worlds"] if w["world"] == n)
        for key, now, was, label in (("kill", r["hits_to_kill"], ref["ref"]["hits_to_kill"], "hits to kill the reference creature"),
                                     ("die", r["hits_to_die"], ref["ref"]["hits_to_die"], "reference creature hits before death"),
                                     ("strong", r["strong_hits"], ref["boss"]["strong_hits"], "strong boss hits before death")):
            if abs(now / was - 1) > TOLERANCE:
                out.append(f"World {n}: {cls} talents move the {label} from {was:.1f} to {now:.1f} ({now / was - 1:+.0%}, at most {TOLERANCE:.0%})")
        t = interp(TARGET_HITS_TO_KILL, n)
        if abs(r["hits_to_kill"] / t - 1) > TOLERANCE:
            out.append(f"World {n}: {cls} talents: hits to kill the reference creature {r['hits_to_kill']:.1f}, design {t:.1f}")
        if r["cut"] > TALENT_FIGHT_CUT:
            out.append(f"World {n}: {cls} talents cut the solo {ref['boss']['id']} fight by {r['cut']:.0%} (at most {TALENT_FIGHT_CUT:.0%})")
    return out


SNORKEL_NOTE = ("Snorkel tanks (World 7): {tanks}. The Pressure Leviathan fight lasts about {fight:.0f} s solo, inside the "
                "smallest tank; the tanks are left as they are.")


def snorkels(a):
    content, _, _ = load_modules()
    lev = next(b for b in a["bosses"] if b["id"] == "pressure_leviathan")
    return dict(tanks=", ".join(f"{s[1]} {s[5]} s" for s in content.SNORKELS), fight=lev["t1"] * 60)


CHANGES = [
    "The talents are now part of the check: for every class and world, the talents open on arrival (the gates of "
    "TALENT_TIERS), applied as Talents.java applies them, on top of the design player.",
    "Berserker: the boss talents Giantkiller and Shell Splitter 6% + 12% -> 3% + 5%, Heavy Hand and Cleaver 3% + 5% -> "
    "3% + 4% damage, Bloodied and Red Mist 15% + 25% -> 10% + 12% below half health, Opener 20% -> 10%, Finisher "
    "20% -> 10%, Quick Arm and Flurry 5% + 10% -> 3% + 4% attack speed. With the weapon's +58% at level 5, the whole "
    "tree cut the solo boss fights of Worlds 9 and 10 by 40% and brought the reference creature of World 9 to 3.2 hits "
    "(design 4.7); now 23% to 24% and 3.5 hits.",
    "Guardian: the bulwark gives health and toughness instead of armor (Stout +1 armor -> +1 max health, Plated +2 armor "
    "-> +0.5 toughness, Unbroken +2 -> +0.5 toughness, Last Wall 25% -> 10%), Broad Back and Hearty +2 and +4 -> +1 and "
    "+1 max health, Lacquer Skin 4 -> 2 absorption. Near the armor formula's cap every armor point takes about a fifth "
    "of the damage away: the tree made a World 9 player survive 5.3 strong boss blows instead of 3 (+74%), now +24%.",
    "Survivor: Thick Skin and Iron Heart +2 and +4 -> +1 and +2 max health, Stubborn and Never Down 15% + 30% -> 10% + "
    "15% (+43% strong boss hits in World 9, now +18%).",
    "Prowler: First Cut 15% -> 10%, Stalker and Assassin 20% + 40% -> 10% + 20% while sneaking (the reference creature "
    "of World 9 fell in 3.2 hits, now 3.6).",
    "Reaper and Prospector talents move none of these measures; the Reaper's +28% souls from kills is shown in the "
    "soul table.",
]

OPEN = [
    "Talents cost Shell Shards (1 and 2 for the last two of a branch, 9 for a whole tree) from the same bosses that pay "
    "for the weapons' class levels: bringing every world's weapon to the cap leaves 4 shards by World 10, so a whole tree "
    "means leaving some weapons below the cap. A choice for the player, left as it is.",
    "Talents of two classes add up when gear of both is worn (a Berserker weapon and Prowler boots): the check takes "
    "one class at a time.",
    "Boss fights are short: with the reference boss health (500 x 1.35^(n-1)) and the design's gear, a solo fight lasts "
    "1 to 2 minutes up to World 9 and about 3.5 minutes for the Unfinished. The design gives no length; the expertise "
    "tier asks for long fights. Longer fights would need more boss health than the formula, or a smaller damage "
    "multiplier outside the openings (x0.75, MatrioBoss.hurtServer). Left to playtests.",
    "World gauges (toxin, heat, oxygen, noise...) gain and drain at rates written in the Java rules, not in content.py; "
    "they are not part of this pass.",
    "The class column of the wiki's Difficulty formulas page is one world early (+10% in World 2): the cap is reached "
    "after the boss of the previous world, so level 2 applies from World 3, as in the design.",
]


def table(rows, head):
    lines = ["| " + " | ".join(head) + " |", "| " + " | ".join("---" for _ in head) + " |"]
    lines += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(lines)


def ba(before, after, fmt="{:.1f}"):
    """'x' when unchanged, 'x -> y' otherwise."""
    a = fmt.format(after)
    if before is None:
        return a
    b = fmt.format(before)
    return a if a == b else f"{b} -> {a}"


def markdown(before, after, ref, git_ref=None):
    L = ["# Balance", "",
         f"Generated by `python3 tools/balance.py --baseline {git_ref or ref} --label {ref} --write docs-wiki-drafts/Balance.md`. "
         f"Each value reads \"{ref} -> now\" when the balance pass changed it.", "",
         "The script reads the creatures, bosses and gear of `tools/content.py` and the moves of `tools/attacks.py`, applies the "
         "rules the code applies (armor formula, class bonus, creature and boss armor, the boss attack cycle with its "
         "openings) and compares the result with the targets of the design: the reference creature (20 health, 5 damage) and "
         "boss (500 health, 12 damage for a strong hit) scaled by x1.35 health and x1.20 damage per world, the hits of "
         "\"Équilibrage du joueur\" and the soul budget of 300 per world.", "",
         "## Assumptions", "",
         "- The player wears the full set of the world and a Berserker weapon of that world at the class level allowed on "
         "arrival (level 2 from World 3, 3 from World 5, 4 from World 7, 5 from World 9), and swings at full charge "
         f"({PLAYER_ATTACK_SPEED:.1f} attacks per second plus the Berserker speed).",
         "- World 7 replaces the helmet by a Cobalt Snorkel Helmet. The Surface player has iron gear.",
         f"- In a boss fight a player hits every swing during the openings (x1.5 damage) and {UPTIME:.0%} of the swings "
         "otherwise (x0.75), none during the phase changes. Boss armor 8, creature armor 2 (elites 6).",
         "- Creature combat time: kills the quests ask for, plus about 107 kills for the gear's resource (16 drops at 15%), "
         "10 seconds each to reach the creature, then the solo boss fight. Exploration, crafting and travel are not counted: "
         "the design's 60 to 80 hours for a first game are mostly those.",
         "- Souls: the plan of `design/regles.txt` (boss 100, chests 10 x 10, elites 10 x 5, altar 5 x 10) with the real "
         "quest rewards. Structure chests give souls since 0.4.0 (Soul Shards and Soul Vessels, about 100 per world, "
         "Rewards.java); they are counted as planned.", ""]
    bw = {w["world"]: w for w in before["worlds"]} if before else {}
    bb = {b["id"]: b for b in before["bosses"]} if before else {}
    bm = {m["id"]: m for m in before["mobs"]} if before else {}

    def g(d, *keys):
        for k in keys:
            if d is None:
                return None
            d = d.get(k) if isinstance(d, dict) else None
        return d

    L += ["## Player and reference creature", "",
          "Design targets in brackets (\"Équilibrage du joueur\": 2.9 / 3.5 / 5 hits to kill, 8.9 / 7.9 / 8.5 hits to die, "
          "2.9 / 2.2 / 3.3 strong boss hits to die at worlds 1 / 5 / 10, interpolated).", ""]
    rows = []
    for w in after["worlds"]:
        n = w["world"]
        if n == 0:
            continue
        p, r, b = w["player"], w["ref"], w["boss"]
        o = bw.get(n)
        rows.append([n, f"{p['hp']:.0f}", f"{p['armor']:.0f} / {p['tough']:.1f}", f"{p['raw']:.0f}",
                     ba(g(o, "player", "dmg"), p["dmg"]), p["level"],
                     ba(g(o, "ref", "hits_to_kill"), r["hits_to_kill"]) + f" ({interp(TARGET_HITS_TO_KILL, n):.1f})",
                     ba(g(o, "ref", "hits_to_die"), r["hits_to_die"]) + f" ({interp(TARGET_MOB_HITS_TO_DIE, n):.1f})",
                     ba(g(o, "boss", "strong_hits"), b["strong_hits"]) + f" ({interp(TARGET_BOSS_HITS_TO_DIE, n):.1f})"])
    L += [table(rows, ["World", "Health", "Armor / toughness", "Weapon", "Hit (Berserker)", "Class level",
                       "Hits to kill", "Hits to die", "Strong boss hits to die"]), ""]

    L += ["## Bosses", "", "Fight length in minutes for 1, 2 and 4 players (health x1 / x1.6 / x2.8, attack pace x1 / x1.05 / x1.15).", ""]
    rows = []
    for b in after["bosses"]:
        o = bb.get(b["id"])
        rows.append([b["world"], b["id"], ba(g(o, "hp"), b["hp"], "{:.0f}"), ba(g(o, "dmg"), b["dmg"]),
                     f"x{b['hp_ratio']:.2f} / x{b['dmg_ratio']:.2f}", ba(g(o, "hits_to_kill"), b["hits_to_kill"], "{:.0f}"),
                     ba(g(o, "strong_hits"), b["strong_hits"]),
                     ba(g(o, "t1"), b["t1"]), ba(g(o, "t2"), b["t2"]), ba(g(o, "t4"), b["t4"])])
    L += [table(rows, ["World", "Boss", "Health", "Strong hit", "vs reference", "Player hits", "Strong hits to die",
                       "1 player", "2 players", "4 players"]), ""]

    L += ["## Creatures by world", "",
          "Health and damage as baked in `content.py` (x reference creature of the world), hits and seconds each way "
          "(the seconds to die count the basic melee half the time and every move on its cooldown), the strongest move "
          "in basic hits and, for the early column, the hits with the previous world's gear.", ""]
    for n in range(1, 11):
        rows = []
        for m in (x for x in after["mobs"] if x["world"] == n):
            o = bm.get(m["id"])
            rows.append([m["id"] + (" (elite)" if m["elite"] else ""), ba(g(o, "hp"), m["hp"], "{:g}"), ba(g(o, "dmg"), m["dmg"], "{:g}"),
                         f"x{m['hp_ratio']:.2f} / x{m['dmg_ratio']:.2f}",
                         ba(g(o, "hits_to_kill"), m["hits_to_kill"]), ba(g(o, "hits_to_kill_early"), m["hits_to_kill_early"]),
                         ba(g(o, "kill_s"), m["kill_s"]), ba(g(o, "hits_to_die"), m["hits_to_die"]), ba(g(o, "die_s"), m["die_s"]),
                         ba(g(o, "burst"), m["burst"], "{:.2f}")])
        L += [f"### World {n}", "", table(rows, ["Creature", "Health", "Damage", "vs reference", "Hits to kill", "Early",
                                                  "Seconds to kill", "Hits to die", "Seconds to die", "Strongest move"]), ""]

    L += ["## Talents", "",
          "Each class's talents open on arrival in a world (tier gates: the Guardian, then the bosses of Worlds 2, 5 and 8), "
          "bought and active on top of the design player. Attribute talents change the stats; the others are second blows "
          f"of a share of the damage dealt, through the armor again (Talents.strike): the crit talents on a foe's first blow, "
          f"the execute ones under a quarter of its health, rage on {LOW_HEALTH_SHARE:.0%} of the blows (below half health), "
          f"sneak on {SNEAK_SHARE:.0%} of a Prowler's blows. Last stand heals back its share of a blow under 30% health "
          f"(at most {LASTSTAND_CAP:.0%}), dodge is capped at {DODGE_CAP:.0%}. The check: each measure within "
          f"{TOLERANCE:.0%} of the design player without talents, a solo boss fight shortened by {TALENT_FIGHT_CUT:.0%} at "
          "most, and the reference creature's hits to kill in the design's band. \"Boss bonus\" is what the tooltips add up "
          "against a boss: the weapon's class level (Berserker), then the damage and boss talents.", ""]
    bt = {(r["cls"], r["world"]): r for r in before.get("talents", [])} if before else {}
    for cls in dict.fromkeys(r["cls"] for r in after.get("talents", [])):
        rows = []
        for r in (x for x in after["talents"] if x["cls"] == cls):
            o = bt.get((cls, r["world"]))
            w = next(x for x in after["worlds"] if x["world"] == r["world"])
            rows.append([r["world"], f"{r['souls']} / {r['shards']}",
                         ba(g(o, "hits_to_kill"), r["hits_to_kill"]) + f" ({w['ref']['hits_to_kill']:.1f})",
                         ba(g(o, "hits_to_die"), r["hits_to_die"]) + f" ({w['ref']['hits_to_die']:.1f})",
                         ba(g(o, "strong_hits"), r["strong_hits"]) + f" ({w['boss']['strong_hits']:.1f})",
                         ba(g(o, "t1"), r["t1"]) + f" ({w['boss']['t1']:.1f})",
                         ba(g(o, "cut"), r["cut"], "{:.0%}"), ba(g(o, "boss_bonus"), r["boss_bonus"], "{:+.0%}")])
        L += [f"### {cls.capitalize()}", "", table(rows, ["World", "Open talents cost (souls / shards)", "Hits to kill (without)",
                                                          "Hits to die (without)", "Strong boss hits (without)",
                                                          "Solo boss fight, min (without)", "Fight cut", "Boss bonus"]), ""]

    L += ["## Souls, Shell Shards and time", "",
          "Gear is new in every world, so its class starts again at level 1. The class cap of the world, what a Berserker "
          "weapon costs from level 1 to that cap (a full set with armor is five times as much), the souls and Shell Shards "
          "a player has on arrival against what the weapons of all the worlds so far needed, and the creature combat "
          "minutes of the world (see the assumptions).", ""]
    rows = []
    for w in after["worlds"][1:]:
        s = w["souls"]
        o = bw.get(w["world"])
        rows.append([w["world"], s["quests"], s["total"], s["level"], f"{s['weapon']} / {s['shards']}", s["set"],
                     f"{s['have_souls']} / {s['need_souls']}", ba(g(o, "souls", "have_shards"), s["have_shards"], "{:.0f}") + f" / {s['need_shards']}",
                     "{} / {}".format(*s["tree"]), ba(g(o, "souls", "reaper"), s["reaper"], "+{:.0f}"),
                     ba(g(o, "combat", "minutes"), w["combat"]["minutes"], "{:.0f}")])
    L += [table(rows, ["World", "Quest souls", "World income", "Class cap", "Weapon to cap (souls / shards)", "Set to cap (souls)",
                       "Souls on arrival / needed so far", "Shards on arrival / needed so far", "One class's open talents (souls / shards)",
                       "Reaper soul talents", "Combat minutes"]), ""]
    if SNORKEL_NOTE:
        L += [SNORKEL_NOTE.format(**snorkels(after)), ""]

    fb, fa = flags(before) if before else [], flags(after)
    L += ["## Outliers", "", f"Flagged at {ref}:", ""] + [f"- {f}" for f in fb] + ["", "Still flagged now:", ""]
    L += [f"- {f}" for f in fa] if fa else ["- none"]
    L += ["", "## What the pass changed", ""] + [f"- {c}" for c in CHANGES]
    L += ["", "## Open points", ""] + [f"- {c}" for c in OPEN]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Matriochka balance check.")
    ap.add_argument("--baseline", help="git ref to compare with (before/after)")
    ap.add_argument("--label", help="name of the baseline in the report (default: the ref)")
    ap.add_argument("--write", help="write the markdown report there")
    args = ap.parse_args()
    after = analyse()
    before = analyse(args.baseline) if args.baseline else None
    if args.write:
        with open(os.path.join(ROOT, args.write), "w", encoding="utf-8") as f:
            f.write(markdown(before, after, args.label or args.baseline or "HEAD", args.baseline or "HEAD"))
        print("wrote " + args.write)
    print("world  hp  armor  hit   ref-kill ref-die  boss-die  boss 1p/2p/4p (min)  souls  combat")
    for w in after["worlds"]:
        p, b, s = w["player"], w["boss"], w["souls"]
        r = w["ref"] or dict(hits_to_kill=0, hits_to_die=0)
        c = w["combat"]["minutes"] if w["combat"] else 0
        print(f"{w['world']:>5} {p['hp']:>3.0f} {p['armor']:>4.0f}/{p['tough']:<4.1f} {p['dmg']:>5.1f} {r['hits_to_kill']:>8.1f} {r['hits_to_die']:>7.1f} "
              f"{b['strong_hits']:>9.1f}  {b['t1']:>5.1f} {b['t2']:>5.1f} {b['t4']:>5.1f}  {s['total']:>11} {c:>6.0f}")
    print("\ntalents  world  hits to kill  hits to die  strong hits  solo fight cut  boss bonus")
    for r in after["talents"]:
        if r["world"] in (5, 9, 10):
            print(f"{r['cls']:<11} {r['world']:>3} {r['hits_to_kill']:>12.1f} {r['hits_to_die']:>12.1f} {r['strong_hits']:>12.1f} "
                  f"{r['cut']:>14.0%} {r['boss_bonus']:>+11.0%}")
    fl = flags(after)
    print(f"\n{len(fl)} outlier(s)")
    for f in fl:
        print("  " + f)


if __name__ == "__main__":
    main()
