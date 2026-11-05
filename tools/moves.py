"""Creature movesets.

Every creature keeps its basic strike and its signature mechanic, and also gets three moves (four for elites)
drawn from the library below. Each move has a wind-up you can read, a hit frame, and a cooldown, so a fight
against the same creature never plays out the same way twice. Timings are in ticks and must match
MobMoves.java; the animation hit frame is placed on the same tick.
"""
import zlib

# id: (EN name, FR name, EN description, FR description, wind-up/hit tick, total ticks, cooldown ticks)
MOVES = {
    "combo": ("Flurry", "Rafale",
              "Three quick hits in a row at close range, 60% damage each.",
              "Trois coups rapides d'affilée au corps à corps, 60 % des dégâts chacun.", 6, 18, 70),
    "lunge": ("Lunge", "Bond",
              "Crouches, then leaps at you from 3 to 9 blocks away: 120% damage on contact.",
              "S'accroupit puis bondit sur toi de 3 à 9 blocs : 120 % des dégâts au contact.", 9, 24, 90),
    "sweep": ("Sweep", "Balayage",
              "A wide swing that hits everything in front of it within 3 blocks and throws it back.",
              "Un large revers qui touche tout ce qui est devant lui à 3 blocs et le repousse.", 9, 16, 80),
    "slam": ("Ground slam", "Frappe au sol",
             "Rears up, then strikes the ground: 110% damage to everything within 3.5 blocks, thrown upward.",
             "Se dresse puis frappe le sol : 110 % des dégâts à tout ce qui est à 3,5 blocs, projeté en l'air.", 14, 22, 110),
    "spit": ("Bolt", "Trait",
             "Fires a bolt in a straight line up to 16 blocks: 80% damage and the world's affliction. Breaking line of sight dodges it.",
             "Lance un trait en ligne droite jusqu'à 16 blocs : 80 % des dégâts et le mal du monde. Couper la ligne de vue l'esquive.", 12, 18, 80),
    "roar": ("Roar", "Cri",
             "Lets out a cry: players within 8 blocks suffer the world's affliction, nearby creatures speed up and hit harder for 5 seconds.",
             "Pousse un cri : les joueurs à 8 blocs subissent le mal du monde, les créatures proches accélèrent et frappent plus fort pendant 5 secondes.", 12, 24, 220),
    "blink": ("Blink", "Éclipse",
              "Vanishes in a puff and reappears behind you, then strikes at once.",
              "Disparaît dans un nuage et réapparaît derrière toi, puis frappe aussitôt.", 8, 14, 130),
    "spin": ("Whirl", "Tourbillon",
             "Spins for a second, hitting everything within 2 blocks four times at 40% damage.",
             "Tourne sur lui-même une seconde et touche quatre fois tout ce qui est à 2 blocs, à 40 % des dégâts.", 4, 20, 100),
    "grab": ("Grab", "Étreinte",
             "Seizes you at arm's reach: you are held in place for 2 seconds and take 50% damage.",
             "T'attrape à portée de bras : tu es immobilisé 2 secondes et tu subis 50 % des dégâts.", 8, 16, 120),
}

ARCHETYPE = {
    "humanoid": ["combo", "sweep", "slam", "lunge", "roar", "spit"],
    "beast": ["lunge", "combo", "sweep", "roar", "blink", "spin"],
    "shapeless": ["spit", "slam", "spin", "blink", "roar"],
    "flyer": ["lunge", "spit", "sweep", "spin"],
    "swimmer": ["lunge", "spin", "grab", "combo"],
    "burrower": ["blink", "lunge", "slam", "grab"],
}

BODY_ARCHETYPE = {
    "biped": "humanoid", "biped_short": "humanoid", "robed": "humanoid", "brute": "humanoid", "golem": "humanoid",
    "tall": "humanoid", "column": "humanoid", "hand": "burrower",
    "quad": "beast", "lizard": "beast", "rat": "beast", "crawler": "beast", "spider": "beast", "beetle": "beast",
    "crab": "beast", "imp": "beast",
    "blob": "shapeless", "jelly": "shapeless", "orb": "shapeless", "plant": "shapeless", "block": "shapeless",
    "chest": "shapeless", "floating_head": "shapeless", "wisp": "shapeless",
    "ray": "flyer", "bird": "flyer", "fish": "swimmer", "fish_small": "swimmer", "eel": "swimmer", "worm": "burrower",
}

# Moves that would contradict the signature mechanic.
EXCLUDE = {
    "statue": {"blink", "lunge"}, "puller": {"lunge", "blink"}, "flee_cloud": {"lunge", "combo"},
    "exploder": {"spin", "slam", "combo"}, "grabber": {"grab"}, "chain_ranged": {"spit"}, "mimic": {"roar"},
    "charger": {"lunge"}, "charger_cage": {"lunge"}, "area_slam": {"slam"},
}
# Moves that fit a signature mechanic so well they are always included.
FAVOUR = {"sound_hunter": "roar", "lurer": "blink", "caller": "roar", "diver": "lunge", "harpoon": "spit",
          "shielded": "sweep", "digger": "slam", "swarm": "combo", "swarm_toxin": "combo", "light_eater": "spit",
          "copycat": "combo", "wall_crawler": "lunge", "reflect": "spin", "melee_reach": "sweep"}


def assign(m):
    if m.get("moves"):
        return list(m["moves"])
    pool = [x for x in ARCHETYPE[BODY_ARCHETYPE.get(m["body"], "beast")] if x not in EXCLUDE.get(m["behavior"], set())]
    n = 4 if m["elite"] else 3
    out = []
    fav = FAVOUR.get(m["behavior"])
    if fav and fav not in EXCLUDE.get(m["behavior"], set()):
        out.append(fav)
    rest = sorted((x for x in pool if x not in out), key=lambda x: zlib.crc32(f"{m['id']}:{x}".encode()))
    out += rest[: n - len(out)]
    return out


# ------------------------------------------------------------------ animations
def _k(d):
    return {f"{t:.2f}": {"post": v, "lerp_mode": "catmullrom"} for t, v in d}


def move_anims(roles, moves):
    """Keyframed animations for the given moves, using the rig's bone roles (see models.plan)."""
    body = (roles.get("body") or roles.get("head") or ["root"])[0]
    head = roles.get("head", [])
    arms_r, arms_l = roles.get("arm_r", []), roles.get("arm_l", [])
    arms = arms_r + arms_l
    legs = roles.get("leg_l", []) + roles.get("leg_r", [])
    jaws = roles.get("jaw", [])
    wings_l, wings_r = roles.get("wing_l", []), roles.get("wing_r", [])
    tails = roles.get("tail", []) + roles.get("seg", [])
    out = {}

    def sec(move, which):
        d = MOVES[move]
        return (d[4] if which == "hit" else d[5]) / 20

    for mv in moves:
        hit, end = sec(mv, "hit"), sec(mv, "end")
        B = {}
        if mv == "combo":
            strikes = [hit, hit + 0.2, hit + 0.4]
            for i, a in enumerate(arms or head or [body]):
                ks = [(0, [0, 0, 0])]
                for j, s in enumerate(strikes):
                    side = (j + i) % 2
                    ks += [(s - 0.1, [-80 if side == 0 else -20, 0, 0]), (s, [30 if side == 0 else -5, 0, 0])]
                ks.append((end, [0, 0, 0]))
                B[a] = {"rotation": _k(ks)}
            B[body] = {"rotation": _k([(0, [0, 0, 0]), (strikes[0], [6, 14, 0]), (strikes[1], [6, -14, 0]), (strikes[2], [8, 10, 0]), (end, [0, 0, 0])])}
            for j in jaws:
                B[j] = {"rotation": _k([(0, [0, 0, 0])] + [(s, [-35, 0, 0]) for s in strikes] + [(end, [0, 0, 0])])}
        elif mv == "lunge":
            B[body] = {"position": _k([(0, [0, 0, 0]), (hit - 0.15, [0, -2.5, 2]), (hit, [0, 1.5, -3]), (hit + 0.35, [0, 0.5, -1]), (end, [0, 0, 0])]),
                       "rotation": _k([(0, [0, 0, 0]), (hit - 0.15, [12, 0, 0]), (hit, [-18, 0, 0]), (hit + 0.35, [8, 0, 0]), (end, [0, 0, 0])])}
            for a in arms:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.15, [30, 0, 0]), (hit, [-120, 0, 0]), (hit + 0.4, [-40, 0, 0]), (end, [0, 0, 0])])}
            for l in legs:
                B[l] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.15, [-25, 0, 0]), (hit, [40, 0, 0]), (hit + 0.4, [0, 0, 0]), (end, [0, 0, 0])])}
            for j in jaws:
                B[j] = {"rotation": _k([(0, [0, 0, 0]), (hit, [-50, 0, 0]), (hit + 0.25, [0, 0, 0]), (end, [0, 0, 0])])}
        elif mv == "sweep":
            B[body] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.2, [0, 45, 0]), (hit, [6, -55, 0]), (hit + 0.15, [4, -40, 0]), (end, [0, 0, 0])])}
            for a in arms_r or arms or head:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.2, [-60, 40, 60]), (hit, [-70, -40, -10]), (end, [0, 0, 0])])}
            for t in tails:
                B[t] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.2, [0, -40, 0]), (hit, [0, 50, 0]), (end, [0, 0, 0])])}
        elif mv == "slam":
            B[body] = {"position": _k([(0, [0, 0, 0]), (hit - 0.3, [0, 3, 0]), (hit, [0, -2.5, 0]), (hit + 0.1, [0, -1.5, 0]), (end, [0, 0, 0])]),
                       "rotation": _k([(0, [0, 0, 0]), (hit - 0.3, [-16, 0, 0]), (hit, [18, 0, 0]), (end, [0, 0, 0])]),
                       "scale": _k([(0, [1, 1, 1]), (hit - 0.3, [0.95, 1.08, 0.95]), (hit, [1.1, 0.9, 1.1]), (hit + 0.15, [1, 1, 1]), (end, [1, 1, 1])])}
            for a in arms:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.3, [-165, 0, 0]), (hit, [25, 0, 0]), (end, [0, 0, 0])])}
        elif mv == "spit":
            B[body] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.25, [-10, 0, 0]), (hit, [14, 0, 0]), (end, [0, 0, 0])]),
                       "scale": _k([(0, [1, 1, 1]), (hit - 0.05, [1.08, 1.08, 1.08]), (hit + 0.05, [0.96, 0.96, 0.96]), (end, [1, 1, 1])])}
            for h in head:
                B[h] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.25, [-30, 0, 0]), (hit, [20, 0, 0]), (end, [0, 0, 0])])}
            for j in jaws:
                B[j] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.05, [-55, 0, 0]), (hit + 0.15, [-10, 0, 0]), (end, [0, 0, 0])])}
            for a in arms_r[:1]:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.25, [-150, 0, 20]), (hit, [-80, 0, 0]), (end, [0, 0, 0])])}
        elif mv == "roar":
            B[body] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.3, [10, 0, 0]), (hit, [-16, 0, 0]), (end - 0.3, [-14, 0, 0]), (end, [0, 0, 0])]),
                       "scale": _k([(0, [1, 1, 1]), (hit, [1.1, 1.1, 1.1]), (end - 0.3, [1.08, 1.08, 1.08]), (end, [1, 1, 1])])}
            for h in head:
                B[h] = {"rotation": _k([(0, [0, 0, 0]), (hit, [-40, 0, 0]), (hit + 0.2, [-38, 8, 0]), (hit + 0.4, [-38, -8, 0]), (end, [0, 0, 0])])}
            for j in jaws:
                B[j] = {"rotation": _k([(0, [0, 0, 0]), (hit, [-60, 0, 0]), (end - 0.2, [-55, 0, 0]), (end, [0, 0, 0])])}
            for a in arms_l:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit, [-40, 0, -50]), (end, [0, 0, 0])])}
            for a in arms_r:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit, [-40, 0, 50]), (end, [0, 0, 0])])}
            for w in wings_l:
                B[w] = {"rotation": _k([(0, [0, 0, 0]), (hit, [0, 0, 70]), (end, [0, 0, 0])])}
            for w in wings_r:
                B[w] = {"rotation": _k([(0, [0, 0, 0]), (hit, [0, 0, -70]), (end, [0, 0, 0])])}
        elif mv == "blink":
            B[body] = {"scale": _k([(0, [1, 1, 1]), (hit - 0.1, [0.6, 1.3, 0.6]), (hit, [0.05, 0.05, 0.05]), (hit + 0.05, [1.2, 0.8, 1.2]), (end, [1, 1, 1])])}
            for a in arms:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit + 0.05, [-100, 0, 0]), (hit + 0.2, [20, 0, 0]), (end, [0, 0, 0])])}
        elif mv == "spin":
            B[body] = {"rotation": {"0.00": {"post": [0, 0, 0], "lerp_mode": "linear"}, f"{hit:.2f}": {"post": [0, 0, 0], "lerp_mode": "linear"},
                                    f"{end - 0.1:.2f}": {"post": [0, 720, 0], "lerp_mode": "linear"}, f"{end:.2f}": {"post": [0, 720, 0], "lerp_mode": "linear"}}}
            for a in arms_l:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit, [0, 0, -80]), (end - 0.1, [0, 0, -80]), (end, [0, 0, 0])])}
            for a in arms_r:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit, [0, 0, 80]), (end - 0.1, [0, 0, 80]), (end, [0, 0, 0])])}
        elif mv == "grab":
            for a in arms or head or [body]:
                B[a] = {"rotation": _k([(0, [0, 0, 0]), (hit - 0.15, [-60, 0, 0]), (hit, [-95, 0, 0]), (hit + 0.1, [-75, 0, 0]), (end, [0, 0, 0])])}
            B.setdefault(body, {})["position"] = _k([(0, [0, 0, 0]), (hit, [0, 0, -2]), (end, [0, 0, 0])])
            for t in tails:
                B[t] = {"rotation": _k([(0, [0, 0, 0]), (hit, [0, 35, 0]), (hit + 0.2, [0, -20, 0]), (end, [0, 0, 0])])}
        out[f"attack.{mv}"] = {"loop": False, "animation_length": end, "bones": B}
    return out
