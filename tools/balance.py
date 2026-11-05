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
                if state == "opening":
                    hp -= hit * 1.5
                else:
                    hp -= hit * 0.75 * UPTIME
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
    return dict(mobs=mobs, bosses=bosses, worlds=worlds)


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
    return out


SNORKEL_NOTE = ("Snorkel tanks (World 7): {tanks}. The Pressure Leviathan fight lasts about {fight:.0f} s solo, inside the "
                "smallest tank; the tanks are left as they are.")


def snorkels(a):
    content, _, _ = load_modules()
    lev = next(b for b in a["bosses"] if b["id"] == "pressure_leviathan")
    return dict(tanks=", ".join(f"{s[1]} {s[5]} s" for s in content.SNORKELS), fight=lev["t1"] * 60)


CHANGES = [
    "Berserker weapons now add 8% of their damage plus the whole bonus of their level (+10% at level 2 up to +50% at "
    "level 5), as the design's \"Bonus de classe max\" column reads. They added 8% x (1 + bonus), so 8% to 12%, and the "
    "reference creature took 6 hits in World 9 and 6.7 in World 10 instead of 4.7 and 5 (GearClasses.java).",
    "Bosses leave 3 Shell Shards instead of 2. With 2, bringing only the weapon of each world to the class cap needed "
    "20 shards by World 9 and 26 by World 10, more than the 18 and 20 the bosses give (MatrioBoss.SHELL_SHARDS).",
    "Dungeon Rat 18 -> 22 health: half the reference creature of World 3, barely more than a World 1 Sporeling.",
    "Executioner 11.5 -> 10.1 damage (x1.6 -> x1.4): the learning tier asks for forgiving deaths, and it hit as hard, "
    "relative to its world, as the expertise elites.",
    "Sky Harpooner 59 -> 111 health, 8.6 -> 10.4 damage: an elite that was weaker than the Island Warden of its own "
    "world, now in line with the other elites (x2.25 health, x1.2 damage).",
    "Unstable Sphere 19.9 -> 17.4, Earth Hand 34.4 -> 30.1, Titan Ray 41.3 -> 36.1 damage (x1.6 -> x1.4): regular "
    "creatures that hit as hard as the elites of their world.",
]

OPEN = [
    "Boss fights are short: with the reference boss health (500 x 1.35^(n-1)) and the design's gear, a solo fight lasts "
    "1 to 2 minutes up to World 9 and about 3.5 minutes for the Unfinished. The design gives no length; the expertise "
    "tier asks for long fights. Longer fights would need more boss health than the formula, or a smaller damage "
    "multiplier outside the openings (x0.75, MatrioBoss.hurtServer). Left to playtests.",
    "World gauges (toxin, heat, oxygen, noise...) gain and drain at rates written in the Java rules, not in content.py; "
    "they are not part of this pass.",
    "The soul plan counts 100 souls per world from structure chests, which 0.3.0 does not give. Without them a world "
    "brings 100 souls less; the quests (30 to 180 per world) cover most of it.",
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
         "quest rewards. Structure chests do not give souls in 0.3.0; they are counted as planned.", ""]
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
                     ba(g(o, "combat", "minutes"), w["combat"]["minutes"], "{:.0f}")])
    L += [table(rows, ["World", "Quest souls", "World income", "Class cap", "Weapon to cap (souls / shards)", "Set to cap (souls)",
                       "Souls on arrival / needed so far", "Shards on arrival / needed so far", "Combat minutes"]), ""]
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
    fl = flags(after)
    print(f"\n{len(fl)} outlier(s)")
    for f in fl:
        print("  " + f)


if __name__ == "__main__":
    main()
