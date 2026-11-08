#!/usr/bin/env python3
"""Generates Matriochka assets, data and Java definitions from content.py.

Usage: python3 tools/gen.py  (from the repository root)
Vanilla worldgen templates are read from $MC_DATA (extracted 26.3 data folder).
"""
import copy
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa
from paint import paint_item, paint_armor_item, paint_armor_layer, paint_block, paint_station_top, hx, paint_snorkel_item, paint_snorkel_layer
import atmosphere
import held3d
import blocks_art
import craft
import particles
import models
import stations3d
import patterns
import bosses_hd
import attacks
import sound
import translations
import gen_replay
import ores_art
import cradle_geo
import matriarch_geo
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobs_hd"))
import registry as mobs_registry  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# the Minecraft version the data is written for: 26.3 by default; MATRIO_MC=26.2 (tools/versions.py) writes the world
# generation in 26.2's formats, from 26.2's vanilla templates, into MATRIO_RES
TARGET = os.environ.get("MATRIO_MC", "26.3")
RES = os.environ.get("MATRIO_RES", os.path.join(ROOT, "src/main/resources"))
A = os.path.join(RES, "assets/matriochka")
D = os.path.join(RES, "data/matriochka")
JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Content.java")
SOUNDS_JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Sounds.java")
PARTICLES_JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Particles.java")
MC = os.environ.get("MC_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "vanilla" if TARGET == "26.3" else "vanilla_" + TARGET))
NS = "matriochka"

EN, FR = {}, {}
# every boss the mod registers: the ten worlds and the Surface, plus the hidden encounter of World 0
ALL_BOSSES = BOSSES + [WORLD_ZERO_BOSS]


def w(path, obj):
    if TARGET != "26.3" and not isinstance(obj, str):
        obj = older_format(path, obj)
        # 26.2 keeps the configured features under their older folder name
        path = path.replace(os.sep + "worldgen" + os.sep + "feature" + os.sep, os.sep + "worldgen" + os.sep + "configured_feature" + os.sep)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------ older formats (TARGET 26.2)
def to262_density(o):
    """A density function written in 26.3's form, rewritten in 26.2's: argument/argument1/argument2 instead of
    input/left/right, y_clamped_gradient for gradient, cache_once for cache, shifted_noise for a shifted noise, sub
    and lerp spelled out with add and mul, and no beardifier (26.2 adds it on its own)."""
    if isinstance(o, list):
        return [to262_density(x) for x in o]
    if not isinstance(o, dict) or not isinstance(o.get("type"), str):
        return {k: to262_density(v) for k, v in o.items()} if isinstance(o, dict) else o
    t = o["type"].removeprefix("minecraft:")
    c = {k: to262_density(v) for k, v in o.items()}
    neg = lambda x: {"type": "minecraft:mul", "argument1": -1.0, "argument2": x}
    if t in ("add", "mul", "min", "max"):
        a, b = c.get("left", c.get("argument1")), c.get("right", c.get("argument2"))
        if t == "add" and isinstance(b, dict) and b.get("type") == "minecraft:beardifier":
            return a
        if t == "add" and isinstance(a, dict) and a.get("type") == "minecraft:beardifier":
            return b
        return {"type": "minecraft:" + t, "argument1": a, "argument2": b}
    if t == "beardifier":
        return 0.0
    if t == "sub":
        return {"type": "minecraft:add", "argument1": c["left"], "argument2": neg(c["right"])}
    if t == "lerp":
        first, second, alpha = c["first"], c["second"], c["alpha"]
        return {"type": "minecraft:add", "argument1": first,
                "argument2": {"type": "minecraft:mul", "argument1": alpha, "argument2": {"type": "minecraft:add", "argument1": second, "argument2": neg(first)}}}
    if t == "gradient":
        return {"type": "minecraft:y_clamped_gradient", "from_y": int(c["from_coordinate"]), "to_y": int(c["to_coordinate"]),
                "from_value": c["from_value"], "to_value": c["to_value"]}
    if t == "cache":
        return {"type": "minecraft:cache_once", "argument": c.get("input", c.get("argument"))}
    if t in ("abs", "square", "cube", "half_negative", "quarter_negative", "squeeze", "blend_density", "interpolated", "invert",
             "cache_2d", "cache_once", "flat_cache", "cache_all_in_cell"):
        return {"type": "minecraft:" + t, "argument": c.get("input", c.get("argument"))}
    if t == "noise" and "shift_x" in c:
        return {"type": "minecraft:shifted_noise", "noise": c["noise"], "shift_x": c["shift_x"], "shift_y": 0.0, "shift_z": c["shift_z"],
                "xz_scale": c["xz_scale"], "y_scale": c["y_scale"]}
    return c


def older_format(path, obj):
    """What a file written in 26.3's format becomes for TARGET (26.2)."""
    p = path.replace(os.sep, "/")
    if "/worldgen/noise/" in p and "base_octave" in obj:
        # 26.2: the first octave and one amplitude per octave
        mods = obj.get("amplitude_modifiers", [1.0] * obj["octave_count"])
        return {"firstOctave": obj["base_octave"], "amplitudes": [obj.get("base_amplitude", 1.0) * m for m in mods][:obj["octave_count"]]}
    if "/worldgen/biome/" in p:
        obj = copy.deepcopy(obj)
        ns = obj.get("attributes", {}).pop("minecraft:gameplay/natural_mob_spawns", None)
        arg = (ns or {}).get("argument", ns or {})
        cats = {k: [] for k in ("monster", "creature", "ambient", "axolotls", "underground_water_creature", "water_creature", "water_ambient", "misc")}
        for cat, entries in arg.get("spawns_by_category", {}).items():
            for e in entries:
                cnt = e.get("count", 1)
                lo, hi = (cnt["min_inclusive"], cnt["max_inclusive"]) if isinstance(cnt, dict) else (cnt, cnt)
                cats.setdefault(cat, []).append({"type": e["type"], "weight": e.get("weight", 1), "minCount": lo, "maxCount": hi})
        obj["spawners"] = cats
        obj["spawn_costs"] = arg.get("spawn_costs", {})
        return obj
    if "/worldgen/noise_settings/" in p:
        obj = to262_density(obj)
        # 26.2: the default block and fluid are block states
        for k in ("default_block", "default_fluid"):
            v = obj.get(k)
            if isinstance(v, str):
                obj[k] = {"Name": v, "Properties": {"level": "0"}} if v in ("minecraft:water", "minecraft:lava") else {"Name": v}
        return obj
    if "/worldgen/density_function/" in p:
        return to262_density(obj)
    if "/worldgen/feature/" in p:
        # 26.2: the feature's settings under "config", blocks as states, providers spelled out
        def state(o):
            if isinstance(o, list):
                return [state(x) for x in o]
            if isinstance(o, dict):
                if set(o) == {"id"} and isinstance(o["id"], str):
                    return {"type": "minecraft:simple_state_provider", "state": {"Name": o["id"]}}
                return {k: ({"Name": v} if k == "state" and isinstance(v, str) else state(v)) for k, v in o.items()}
            return o
        return {"type": obj["type"], "config": state({k: v for k, v in obj.items() if k != "type"})}
    return obj


def mk(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def pal(world):
    if world == 0:
        return ("c8342a", "e8c050", "f0d0b0", "3a1a10")
    return WORLDS[world - 1]["pal"]


def lang(key, en, fr):
    EN[key] = en
    FR[key] = fr


# ------------------------------------------------------------------ items
ARMOR_PIECES = [("helmet", "Helmet", "Casque"), ("chestplate", "Chestplate", "Plastron"),
                ("leggings", "Leggings", "Jambières"), ("boots", "Boots", "Bottes")]
SNORKEL_PAL = {s[0]: s[-1] for s in SNORKELS}
ALL_ITEMS = []  # (id, world, kind, rarity, extra dict)


def expand_items():
    seen = set()
    for it in ITEMS:
        if it["kind"] == "armorset":
            for pid, pen, pfr in ARMOR_PIECES:
                if pid not in it.get("pieces", [p[0] for p in ARMOR_PIECES]):
                    continue
                iid = f"{it['id']}_{pid}"
                ALL_ITEMS.append(dict(id=iid, world=it["world"], kind="armor", rarity=it["rarity"], piece=pid, set=it["id"],
                                      en=f"{it['set_en']} {pen}", fr=f"{pfr} {it['set_fr']}", shape="armor",
                                      effect_en=it.get("effect_en", ""), effect_fr=it.get("effect_fr", "")))
            continue
        if it["id"] in seen:
            continue
        seen.add(it["id"])
        ALL_ITEMS.append(dict(it))


def gen_items():
    tex = mk(os.path.join(A, "textures/item/x"))
    for it in ALL_ITEMS:
        iid = it["id"]
        lang(f"item.{NS}.{iid}", it["en"], it["fr"])
        if it.get("effect_en"):
            lang(f"item.{NS}.{iid}.desc", it["effect_en"], it["effect_fr"])
        p = it.get("pal") or pal(it["world"])
        tpath = os.path.join(A, f"textures/item/{iid}.png")
        # the replay gear paints itself and writes its own models (tools/gen_replay.py)
        if gen_replay.item_assets(it, p, tpath, w, A):
            continue
        hand = craft.crafted_item(it)
        if hand is not None:
            hand.image().save(tpath)
        elif it["kind"] == "armor":
            paint_armor_item(it["piece"], p, iid, tpath)
        elif it["kind"] == "snorkel":
            paint_snorkel_item(SNORKEL_PAL[iid], iid, tpath)
        else:
            paint_item(it["shape"], p, iid, tpath, it["rarity"])
        parent = "minecraft:item/handheld" if it["kind"] in ("weapon", "drill", "tool") or it["shape"] in ("pick", "hook") else "minecraft:item/generated"
        w(os.path.join(A, f"models/item/{iid}.json"), {"parent": parent, "textures": {"layer0": f"{NS}:item/{iid}"}})
        w(os.path.join(A, f"items/{iid}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:item/{iid}"}})
    # armor equipment layers
    for it in ITEMS:
        if it["kind"] == "armorset":
            sid = it["id"]
            p = pal(it["world"])
            if sid == "matriarch":
                # the Matriarch's red lacquer and gold leaf (tools/ores_art.py)
                ores_art.paint_matriarch_layer(mk(os.path.join(A, f"textures/entity/equipment/humanoid/{sid}.png")))
                ores_art.paint_matriarch_layer(mk(os.path.join(A, f"textures/entity/equipment/humanoid_leggings/{sid}.png")), legs=True)
                w(os.path.join(D, f"tags/item/repairs/{sid}.json"), {"values": [f"{NS}:matriochkite_ingot"]})
            else:
                paint_armor_layer(p, sid, mk(os.path.join(A, f"textures/entity/equipment/humanoid/{sid}.png")))
                paint_armor_layer(p, sid + "l", mk(os.path.join(A, f"textures/entity/equipment/humanoid_leggings/{sid}.png")), legs=True)
            w(os.path.join(A, f"equipment/{sid}.json"), {"layers": {"humanoid": [{"texture": f"{NS}:{sid}"}],
                                                                   "humanoid_leggings": [{"texture": f"{NS}:{sid}"}]}})
    for eq, wd in (("filter_mask", 1), ("gravity_boots", 6), ("grip_boots", 9)):
        paint_armor_layer(pal(wd), eq, mk(os.path.join(A, f"textures/entity/equipment/humanoid/{eq}.png")))
        w(os.path.join(A, f"equipment/{eq}.json"), {"layers": {"humanoid": [{"texture": f"{NS}:{eq}"}]}})
    for s in SNORKELS:
        sid, ore, palette = s[0], s[3], s[-1]
        paint_snorkel_layer(palette, sid, mk(os.path.join(A, f"textures/entity/equipment/humanoid/{sid}.png")))
        w(os.path.join(A, f"equipment/{sid}.json"), {"layers": {"humanoid": [{"texture": f"{NS}:{sid}"}]}})
        # a cracked helmet is mended at the anvil with its own ore
        w(os.path.join(D, f"tags/item/repairs/{sid}.json"), {"values": [f"{NS}:{ore}"]})


# ------------------------------------------------------------------ blocks
def emissive_cube(tex, glow):
    """A full cube (up/down/side textures) with an emissive overlay on the faces that have a glow texture: the overlay
    is a second, coplanar element with light_emission 15, as vanilla does for the firefly bush and the eyeblossom, so
    the lit parts stay bright in the dark and with shader packs that respect vanilla block light."""
    faces = {"north": "side", "south": "side", "east": "side", "west": "side", "up": "up", "down": "down"}
    textures = {"particle": tex["side"]}
    for key in ("up", "down", "side"):
        textures[key] = tex[key]
        if glow.get(key):
            textures[key + "_glow"] = glow[key]
    base = {"from": [0, 0, 0], "to": [16, 16, 16],
            "faces": {f: {"uv": [0, 0, 16, 16], "texture": "#" + k, "cullface": f} for f, k in faces.items()}}
    elements = [base]
    lit = {f: {"uv": [0, 0, 16, 16], "texture": "#" + k + "_glow", "cullface": f} for f, k in faces.items() if glow.get(k)}
    if lit:
        elements.append({"from": [0, 0, 0], "to": [16, 16, 16], "light_emission": 15, "faces": lit})
    return {"parent": "minecraft:block/block", "textures": textures, "elements": elements}


def gen_station_materials():
    """The painted materials the sculpted station models share (block/station/*)."""
    d = mk(os.path.join(A, "textures/block/station/x.png"))
    for name, spr in stations3d.materials(16).items():
        spr.image().save(os.path.join(os.path.dirname(d), name + ".png"))


def gen_blocks():
    gen_station_materials()
    patterns.build()
    for b in BLOCKS:
        bid = b["id"]
        lang(f"block.{NS}.{bid}", b["en"], b["fr"])
        if b.get("note_en"):
            lang(f"block.{NS}.{bid}.desc", b["note_en"], b["note_fr"])
        p = ORE_PAL.get(b["id"]) or pal(b["world"])
        tpath = mk(os.path.join(A, f"textures/block/{bid}.png"))
        if b["kind"] in ("nesting_cradle", "time_sprout"):
            # sculpted and staged blocks: their textures, models and blockstates come from tools/ores_art.py
            if b["kind"] == "nesting_cradle":
                w(os.path.join(A, f"items/{bid}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:block/{bid}"}})
                w(os.path.join(D, f"loot_table/blocks/{bid}.json"), {"type": "minecraft:block", "pools": [
                    {"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}"}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
            else:
                ripe = {"condition": "minecraft:block_state_property", "block": f"{NS}:{bid}", "properties": {"age": "3"}}
                w(os.path.join(D, f"loot_table/blocks/{bid}.json"), {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
                    {"type": "minecraft:alternatives", "children": [
                        {"type": "minecraft:item", "name": f"{NS}:chrono_shard", "conditions": [ripe]},
                        {"type": "minecraft:item", "name": f"{NS}:time_seed"}]}]}]})
            continue
        # World Soil is painted as a block of the new terrain set (tools/blocks_art.py), its tilled face too
        hand = None if bid.startswith("world_soil_") else craft.crafted_block(bid)
        glows = {}
        if hand is not None:
            for suffix, spr in hand.items():
                spr.image().save(os.path.join(A, f"textures/block/{bid}{suffix}.png"))
                if spr.glow:
                    spr.glow_image().save(os.path.join(A, f"textures/block/{bid}{suffix}_glow.png"))
                    glows[suffix] = f"{NS}:block/{bid}{suffix}_glow"
        elif not blocks_art.paint(b["style"], p, bid, tpath):
            paint_block(b["style"], p, bid, tpath)
        if b["kind"] == "station":
            if hand is None:
                paint_station_top(p, bid + "t", os.path.join(A, f"textures/block/{bid}_top.png"))
            # a sculpted model per station (tools/stations3d.py); its painted faces become the front plaque and inlay
            model = stations3d.model(bid)
        elif b["kind"] == "soil":
            if hand is None:
                if not blocks_art.paint("soil", p, bid, os.path.join(A, f"textures/block/{bid}_tilled.png"), tilled=True):
                    paint_block("soil", p, bid + "f", os.path.join(A, f"textures/block/{bid}_tilled.png"))
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{bid}"}}
            w(os.path.join(A, f"models/block/{bid}_tilled.json"),
              {"parent": "minecraft:block/template_cube_bottom_top_indented", "textures": {"bottom": f"{NS}:block/{bid}", "side": f"{NS}:block/{bid}", "top": f"{NS}:block/{bid}_tilled"}})
        elif glows:
            model = emissive_cube({"up": f"{NS}:block/{bid}", "down": f"{NS}:block/{bid}", "side": f"{NS}:block/{bid}"},
                                  {"up": glows.get(""), "down": glows.get(""), "side": glows.get("")})
        elif b["kind"] == "planted_seed":
            model = {"parent": "minecraft:block/cross", "textures": {"cross": f"{NS}:block/planted_seed_cross"}}
            paint_item("seed", p, "seed_block", os.path.join(A, "textures/block/planted_seed_cross.png"))
            # a rite site shows its object (tools/rites_art.py): one cross model per world after the first
            import rites_art
            for rw, art in rites_art.RITE_ART.items():
                art(16).image().save(os.path.join(A, f"textures/block/rite_{rw}.png"))
                w(os.path.join(A, f"models/block/planted_seed_{rw}.json"),
                  {"parent": "minecraft:block/cross", "textures": {"cross": f"{NS}:block/rite_{rw}"}})
        elif b.get("inset"):
            # the smaller nesting chests: a smaller box standing on the floor
            a = b["inset"]
            box = {"from": [a, 0, a], "to": [16 - a, 16 - 2 * a, 16 - a],
                   "faces": {f: {"texture": "#all", "uv": [a, a if f in ("up", "down") else 2 * a, 16 - a, 16 - a if f in ("up", "down") else 16],
                                 **({"cullface": "down"} if f == "down" else {})}
                             for f in ("north", "south", "east", "west", "up", "down")}}
            model = {"parent": "minecraft:block/block", "textures": {"particle": f"{NS}:block/{bid}", "all": f"{NS}:block/{bid}"}, "elements": [box]}
        elif b["style"] == "glass":
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": {"sprite": f"{NS}:block/{bid}", "force_translucent": True}}}
        else:
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{bid}"}}
        w(os.path.join(A, f"models/block/{bid}.json"), model)
        if b["kind"] == "soil":
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {"tilled=false": {"model": f"{NS}:block/{bid}"},
                                                                        "tilled=true": {"model": f"{NS}:block/{bid}_tilled"}}})
        elif b["kind"] == "station":
            w(os.path.join(A, f"blockstates/{bid}.json"), stations3d.blockstate(bid))
        elif b["kind"] == "planted_seed":
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {
                f"world={rw}": {"model": f"{NS}:block/{bid}" + ("" if rw == 1 else f"_{rw}")} for rw in range(1, 11)}})
        else:
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {"": {"model": f"{NS}:block/{bid}"}}})
        if b["kind"] != "planted_seed":
            w(os.path.join(A, f"items/{bid}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:block/{bid}"}})
        # loot
        drop = ORE_DROPS.get(bid)
        if b["kind"] in ("world_block", "planted_seed", "death_chest", "boss_altar", "sealed_door", "threshold", "lair_heart"):
            continue
        # a world ore's drops are ruled in world/WorldOres.java, unless it drops like any ore
        if b["kind"] == "world_ore" and not drop:
            continue
        if drop:
            pool = {"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
                {"type": "minecraft:item", "name": f"{NS}:{bid}", "condition": "minecraft:tool/can_silk_touch"},
                {"type": "minecraft:item", "name": f"{NS}:{drop}", "functions": [
                    {"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune", "formula": "minecraft:ore_drops"},
                    {"function": "minecraft:explosion_decay"}]}]}]}
        else:
            pool = {"rolls": 1, "entries": [{"type": "minecraft:item", "name": f"{NS}:{bid}"}], "conditions": [{"condition": "minecraft:survives_explosion"}]}
        w(os.path.join(D, f"loot_table/blocks/{bid}.json"), {"type": "minecraft:block", "pools": [pool]})
    # tags
    pick = [f"{NS}:{b['id']}" for b in BLOCKS if b["kind"] in ("terrain", "station", "deco", "sealed_door", "vent", "world_ore", "matriochkite_block") and b["style"] not in ("moss", "sand", "wood")]
    shovel = [f"{NS}:{b['id']}" for b in BLOCKS if b["kind"] == "soil" or b["style"] in ("moss", "sand")]
    axe = [f"{NS}:{b['id']}" for b in BLOCKS if b["style"] == "wood"] + [f"{NS}:soul_cradle", f"{NS}:nesting_chest", f"{NS}:nesting_cradle"]
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/pickaxe.json"), {"values": pick})
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/shovel.json"), {"values": shovel})
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/axe.json"), {"values": axe})
    # the Matriochkite at the crafting table: nine nuggets an ingot, nine ingots a block, and back
    for big, n, small, _ in MATRIOCHKITE_CRAFTS:
        w(os.path.join(D, f"recipe/{big}.json"), {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["###", "###", "###"],
                                                  "key": {"#": f"{NS}:{small}"}, "result": {"id": f"{NS}:{big}", "count": 1}})
        w(os.path.join(D, f"recipe/{small}_from_{big}.json"), {"type": "minecraft:crafting_shapeless", "category": "misc",
                                                               "ingredients": [f"{NS}:{big}"], "result": {"id": f"{NS}:{small}", "count": n}})
    w(os.path.join(RES, "data/minecraft/tags/block/beacon_base_blocks.json"), {"replace": False, "values": [f"{NS}:matriochkite_block"]})
    w(os.path.join(D, "tags/block/world_soil.json"), {"values": [f"{NS}:world_soil_{i}" for i in range(10)]})
    w(os.path.join(D, "tags/block/stone_like.json"), {"values": [f"{NS}:{b['id']}" for b in BLOCKS if b["kind"] == "terrain" and b["style"] == "stone"]})


# ------------------------------------------------------------------ entities
ENTITY_DIMS = {}


def gen_entities():
    for m in MOBS:
        m["moves"] = [a["slug"] for a in attacks.full(m["id"])]
        mid = m["id"]
        lang(f"entity.{NS}.{mid}", m["en"], m["fr"])
        lang(f"entity.{NS}.{mid}.desc", m["desc_en"], m["desc_fr"])
        p = pal(m["world"])
        hd = mobs_registry.build(mid)
        if hd:
            ENTITY_DIMS[mid] = (max(0.4, min(hd[0], 2.5)), max(0.4, hd[1]))
            continue
        wd, ht = models.build(m["body"], p, mid, mk(os.path.join(A, f"geckolib/models/entity/{mid}.geo.json")),
                              mk(os.path.join(A, f"geckolib/animations/entity/{mid}.animation.json")),
                              mk(os.path.join(A, f"textures/entity/{mid}.png")), mid, moves=mid)
        ENTITY_DIMS[mid] = (max(0.4, min(wd, 2.5)), max(0.4, ht))
        from PIL import Image as _I
        _t = _I.open(os.path.join(A, f"textures/entity/{mid}.png"))
        _I.new("RGBA", _t.size).save(os.path.join(A, f"textures/entity/{mid}_glowmask.png"))
    HD_BOSSES = bosses_hd.build_all()
    for b in ALL_BOSSES:
        bid = b["id"]
        lang(f"entity.{NS}.{bid}", b["en"], b["fr"])
        for i, (en, fr) in enumerate(b["atk"]):
            lang(f"boss.{NS}.{bid}.attack{i}", en, fr)
        if b.get("wake"):
            lang(f"message.{NS}.lair.wake.{bid}", *b["wake"])
        wd, ht = HD_BOSSES[bid]
        ENTITY_DIMS[bid] = (max(0.6, min(wd, 2.2)), max(0.8, ht))
    for c in CRITTERS:
        cid = c["id"]
        lang(f"entity.{NS}.{cid}", c["en"], c["fr"])
        lang(f"entity.{NS}.{cid}.desc", c["desc_en"], c["desc_fr"])
        wd, ht = mobs_registry.build(cid)
        ENTITY_DIMS[cid] = (max(0.4, min(wd, 1.2)), max(0.3, ht))
        pools = [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": c["drop"]}]}] if c.get("drop") else []
        w(os.path.join(D, f"loot_table/entities/{cid}.json"), {"type": "minecraft:entity", "pools": pools})
    for (pid, en, fr, wd) in PEOPLES:
        lang(f"entity.{NS}.{pid}", en, fr)
        p = pal(wd) if wd else ("6a4a8a", "e8c050", "f0d0b0", "2a1a3a")
        models.build("robed" if wd not in (6, 7) else "biped", p, pid, mk(os.path.join(A, f"geckolib/models/entity/{pid}.geo.json")),
                     mk(os.path.join(A, f"geckolib/animations/entity/{pid}.animation.json")),
                     mk(os.path.join(A, f"textures/entity/{pid}.png")), pid)
        ENTITY_DIMS[pid] = (0.6, 1.9)


# ------------------------------------------------------------------ worldgen
def jl(path):
    return json.load(open(os.path.join(MC, path)))


SURF = {1: ("spore_moss", "rootstone", "rootstone"), 2: ("ashrock", "ashrock", "ember_stone"), 3: ("dungeon_brick", "dungeon_brick", "dungeon_brick"),
        4: ("skygrass", "cloudstone", "cloudstone"), 5: ("umbral_moss", "umbral_stone", "umbral_stone"), 6: ("prism_moss", "inverted_stone", "inverted_stone"),
        7: ("abyssal_sand", "trench_rock", "trench_rock"), 8: ("chrono_grass", "hourstone", "hourstone"), 9: ("flesh_stone", "living_rock", "living_rock"),
        10: ("workshop_felt", "giant_plank", "giant_plank")}
# Each world's two lesser biomes beside its own: (suffix, English, French, surface block, grass and foliage, fog).
# The world's biome keeps the middle of the climate; the lesser ones take its wet and its warm edges
# (biome_source below), with their own floor, colours and name. Spawns, features and structures are the world's.
SUB_BIOMES = {
    1: [("bloom_hollow", "Bloom Hollow", "Creux des floraisons", "minecraft:moss_block", "5f8a2a", "4f6a32"),
        ("rot_marsh", "Rot Marsh", "Marais pourri", "minecraft:mud", "3a4a22", "3e4a30")],
    2: [("ember_fields", "Ember Fields", "Champs de braises", "matriochka:ember_stone", "6a2a14", "6a2a10"),
        ("ash_drifts", "Ash Drifts", "Congères de cendre", "minecraft:smooth_basalt", "4a3a34", "4a3430")],
    3: [("mossy_cells", "Mossy Cells", "Cellules moussues", "minecraft:mossy_stone_bricks", "5a6a4a", "2a332a"),
        ("crumbling_wing", "Crumbling Wing", "Aile effondrée", "minecraft:cracked_stone_bricks", "5a5a62", "33302a")],
    4: [("hail_meadows", "Hail Meadows", "Prés de grêle", "minecraft:calcite", "c8d8e8", "c8d8f0"),
        ("thunder_heights", "Thunder Heights", "Hauteurs du tonnerre", "matriochka:cloudstone", "8aa0c0", "9ab0d0")],
    5: [("hushed_hollow", "Hushed Hollow", "Creux du silence", "minecraft:sculk", "10202a", "020208"),
        ("bare_dark", "Bare Dark", "Noir nu", "matriochka:umbral_stone", "15151f", "050508")],
    6: [("crystal_fields", "Crystal Fields", "Champs de cristal", "minecraft:amethyst_block", "b84ad8", "c0a0e8"),
        ("mirror_flats", "Mirror Flats", "Plaines miroirs", "minecraft:smooth_quartz", "e0e0f0", "e0d0f0")],
    7: [("coral_shelf", "Coral Shelf", "Plateau de corail", "minecraft:sand", "1a8a8a", "0a3a5a"),
        ("black_trench", "Black Trench", "Fosse noire", "matriochka:trench_rock", "0a2a3a", "051a2a")],
    8: [("hourglass_dunes", "Hourglass Dunes", "Dunes du sablier", "matriochka:temporal_sand_block", "d8b860", "e0d0a0"),
        ("rust_grove", "Rust Grove", "Bosquet de rouille", "minecraft:podzol", "c86a2a", "d8b080")],
    9: [("flesh_mire", "Flesh Mire", "Bourbier de chair", "minecraft:mud", "8a3a2a", "8a4a3a"),
        ("bare_rock", "Bare Rock", "Roc nu", "matriochka:living_rock", "6a4a3a", "7a5a4a")],
    10: [("plank_floor", "Plank Floor", "Plancher", "matriochka:giant_plank", "c8a060", "d0b080"),
         ("lacquer_tray", "Lacquer Tray", "Plateau laqué", "matriochka:lacquer_block", "b0402a", "d0a080")],
}


def with_sub_surfaces(ns, n):
    """The world's noise settings with the floor of each lesser biome, right after the bedrock: its surface block on
    the top layer (26.3: material_rule, block ids as strings; 26.2: surface_rule, block states)."""
    key = "material_rule" if "material_rule" in ns else "surface_rule"
    rule = ns[key]
    if not (isinstance(rule, dict) and isinstance(rule.get("sequence"), list)):
        return ns
    state = (lambda b: b) if key == "material_rule" else (lambda b: {"Name": b})
    floor = {"type": "minecraft:stone_depth", "add_surface_depth": False, "offset": 0, "secondary_depth_range": 0, "surface_type": "floor"}
    rules = [{"type": "minecraft:condition", "if_true": {"type": "minecraft:biome", "biome_is": [f"{NS}:world_{n}_{sub[0]}"]},
              "then_run": {"type": "minecraft:condition", "if_true": floor, "then_run": {"type": "minecraft:block", "result_state": state(sub[3])}}}
             for sub in SUB_BIOMES.get(n, [])]
    rule = dict(rule)
    rule["sequence"] = rule["sequence"][:1] + rules + rule["sequence"][1:]
    ns[key] = rule
    return ns


def biome_source(n):
    """The world's own biome in the middle of the climate, its two lesser biomes on the wet and the warm side."""
    def point(biome, t, h):
        return {"biome": biome, "parameters": {"temperature": t, "humidity": h, "continentalness": 0.0, "erosion": 0.0,
                                               "weirdness": 0.0, "depth": 0.0, "offset": 0.0}}
    subs = SUB_BIOMES.get(n, [])
    if not subs:
        return {"type": "minecraft:fixed", "biome": f"{NS}:world_{n}"}
    pts = [point(f"{NS}:world_{n}", -0.15, -0.15)]
    for (sub, *_), (t, h) in zip(subs, ((-0.1, 0.5), (0.5, -0.1))):
        pts.append(point(f"{NS}:world_{n}_{sub}", t, h))
    return {"type": "minecraft:multi_noise", "biomes": pts}


TEMPLATE = {"overworld": "overworld", "caves": "caves", "ceiling": "nether", "floating": "floating_islands", "amplified": "amplified",
            "ocean": "overworld", "giant": "large_biomes"}

VANILLA_FEATURES = {
    1: ["minecraft:trees_jungle", "minecraft:bamboo_vegetation", "minecraft:patch_grass_jungle", "minecraft:vines", "minecraft:patch_melon"],
    4: ["minecraft:trees_meadow", "minecraft:patch_grass_plain", "minecraft:flower_meadow"],
    6: ["minecraft:trees_cherry", "minecraft:patch_grass_plain"],
    8: ["minecraft:trees_birch_and_oak_leaf_litter", "minecraft:flower_forest_flowers", "minecraft:patch_grass_forest", "minecraft:patch_pumpkin"],
    9: ["minecraft:patch_dead_bush_badlands"],
    10: ["minecraft:trees_plains", "minecraft:patch_grass_plain"],
}


# ------------------------------------------------------------------ World 7: the ocean
# The whole world is sea: water from the sea floor up to OCEAN_SEA (y 240), 16 blocks of air above it and no dry
# land. The sea floor rolls around y 140, raised into reefs and cut by trenches that drop below y 20; caves and air
# grottoes (from the aquifers) run under it. The same numbers live in world/Ocean.java.
OCEAN_SEA = 240
OCEAN_MIN_Y, OCEAN_HEIGHT = -64, 320
OCEAN_FLOOR = 140


def _df(t, **kw):
    d = {"type": f"minecraft:{t}"}
    d.update(kw)
    return d


def _add(a, b):
    return _df("add", left=a, right=b)


def _mul(a, b):
    return _df("mul", left=a, right=b)


def _noise2d(name, xz):
    return _df("noise", noise=f"{NS}:{name}", shift_x="minecraft:shift_x", shift_z="minecraft:shift_z", xz_scale=xz, y_scale=0.0)


def ocean_settings(ns, n):
    """Rewrites the overworld noise settings into the ocean: a custom terrain density, the vanilla cave system carved
    under it, a sea level near the top of the world and a sea-floor surface rule."""
    sand, rock = f"{NS}:abyssal_sand", f"{NS}:trench_rock"
    base = f"{NS}:world_{n}"
    # noises: broad hills, reef crowns, trench lines and the mask that keeps trenches rare
    for name, octave, count, amp in (("hills", -9, 4, 1.0), ("reef", -6, 3, 1.0), ("trench", -8, 3, 1.0), ("trench_mask", -9, 2, 1.0)):
        w(os.path.join(D, f"worldgen/noise/w{n}_{name}.json"), {"base_amplitude": amp, "base_octave": octave, "octave_count": count})
    # offset: where the floor sits, in depth units (1.0 = 128 blocks); 0.34375 puts it at y 140
    floor = (OCEAN_FLOOR - OCEAN_MIN_Y) / 128.0 - 1.25
    hills = _mul(0.22, _noise2d(f"w{n}_hills", 1.0))
    reef = _mul(0.30, _df("clamp", input=_mul(4.0, _add(_noise2d(f"w{n}_reef", 1.0), -0.55)), min=0.0, max=1.0))
    line = _df("square", input=_df("clamp", input=_add(1.0, _mul(-6.0, _df("abs", input=_noise2d(f"w{n}_trench", 0.6)))), min=0.0, max=1.0))
    mask = _df("clamp", input=_add(_mul(2.5, _noise2d(f"w{n}_trench_mask", 1.0)), 0.4), min=0.0, max=1.0)
    trench = _mul(-0.9, _mul(line, mask))
    w(os.path.join(D, f"worldgen/density_function/world_{n}/offset.json"), _df("cache", input=_add(floor, _add(hills, _add(reef, trench)))))
    grad = _df("gradient", axis="y", from_coordinate=OCEAN_MIN_Y, from_value=1.25, to_coordinate=OCEAN_MIN_Y + OCEAN_HEIGHT, to_value=-1.25)
    w(os.path.join(D, f"worldgen/density_function/world_{n}/depth.json"), _add(grad, f"{base}/offset"))
    # terrain: steep below the floor, soft above it (overhangs and arches), roughened by the vanilla 3D noise
    terrain = _df("cache", input=_add(_mul(_df("quarter_negative", input=_mul(f"{base}/depth", 3.0)), 4.0),
                                      _mul(0.4, "minecraft:overworld/base_3d_noise")))
    w(os.path.join(D, f"worldgen/density_function/world_{n}/terrain.json"), terrain)
    T = f"{base}/terrain"
    # the vanilla cave system (cheese, spaghetti, noodles, pillars, entrances) carved under that terrain
    caves = _df("range_choice", input=T, min_inclusive=-1000000.0, max_exclusive=1.5625,
                when_in_range=_df("min", left=T, right=_mul("minecraft:overworld/caves/entrances", 5.0)),
                when_out_of_range=_df("max", left=_df("min", left=_df("min", left=_add(
                    _mul(_df("square", input=_df("noise", noise="minecraft:cave_layer", xz_scale=1.0, y_scale=8.0)), 4.0),
                    _add(_df("clamp", input=_add(_df("noise", noise="minecraft:cave_cheese", xz_scale=1.0, y_scale=0.6666666666666666), 0.27), min=-1.0, max=1.0),
                         _df("clamp", input=_add(_mul(T, -0.64), 1.5), min=0.0, max=0.5))),
                    right="minecraft:overworld/caves/entrances"),
                    right=_add("minecraft:overworld/caves/spaghetti_2d", "minecraft:overworld/caves/spaghetti_roughness_function")),
                    right=_df("range_choice", input="minecraft:overworld/caves/pillars", min_inclusive=-1000000.0, max_exclusive=0.03,
                              when_in_range=-1000000.0, when_out_of_range="minecraft:overworld/caves/pillars")))
    top = OCEAN_MIN_Y + OCEAN_HEIGHT
    shaped = _df("lerp", alpha=_df("gradient", axis="y", from_coordinate=OCEAN_MIN_Y, from_value=0.0, to_coordinate=OCEAN_MIN_Y + 24, to_value=1.0),
                 first=0.1171875,
                 second=_df("lerp", alpha=_df("gradient", axis="y", from_coordinate=top - 16, from_value=1.0, to_coordinate=top, to_value=0.0),
                            first=-0.078125, second=caves))
    final = _add(_df("min", left=_df("squeeze", input=_df("interpolated", cell_size_xz=4, cell_size_y=8,
                                                          input=_mul(_df("blend_density", input=shaped), 0.64))),
                     right="minecraft:overworld/caves/noodle"), _df("beardifier"))
    w(os.path.join(D, f"worldgen/density_function/world_{n}/final_density.json"), final)
    surface = _df("find_top_surface", cell_height=8, lower_bound=OCEAN_MIN_Y, upper_bound=float(OCEAN_SEA - 8),
                  density=_add(_mul(_df("quarter_negative", input=_mul(f"{base}/depth", 3.0)), 4.0), -0.390625))
    w(os.path.join(D, f"worldgen/density_function/world_{n}/preliminary_surface_level.json"), surface)
    r = ns["noise_router"]
    r["depth"] = f"{base}/depth"
    r["final_density"] = f"{base}/final_density"
    if TARGET != "26.3":
        return ocean_settings_262(ns, n, sand, rock, base)
    r["chunk_surface_level"] = _df("interpolated", cell_size_xz=16, cell_size_y=1, input=f"{base}/preliminary_surface_level")
    aq = ns["aquifers"]
    aq["surface_level"] = f"{base}/preliminary_surface_level"
    aq["exclusion"] = _df("min", left=_df("sub", left=-0.225, right="minecraft:overworld/erosion"),
                          right=_df("max", left=_df("sub", left=f"{base}/depth", right=0.9), right=0.0))
    ns["debug_functions"] = [{"function": f"{base}/final_density", "label": "N"}, {"function": f"{base}/depth", "label": "D"},
                             {"function": f"{base}/preliminary_surface_level", "label": "PS"}]
    ns["noise"] = {"height": OCEAN_HEIGHT, "min_y": OCEAN_MIN_Y}
    ns["sea_level"] = OCEAN_SEA
    ns["default_block"] = rock
    ns["default_fluid"] = "minecraft:water"
    # sea floor: sand on gentle ground, bare rock on slopes and in patches, sand a few blocks deep
    block = lambda b: _df("block", result_state=b)
    cond = lambda c, then: _df("condition", if_true=c, then_run=then)
    ns["material_rule"] = _df("sequence", sequence=[
        "minecraft:bedrock_floor",
        cond(_df("above_preliminary_surface"), _df("sequence", sequence=[
            cond("minecraft:on_floor", _df("sequence", sequence=[
                cond(_df("steep"), block(rock)),
                cond(_df("noise_threshold", noise="minecraft:surface", min_threshold=0.45, max_threshold=10.0), block(rock)),
                block(sand)])),
            cond("minecraft:under_floor", _df("sequence", sequence=[
                cond(_df("steep"), block(rock)),
                block(sand)])),
        ])),
    ])
    return ns


def ocean_settings_262(ns, n, sand, rock, base):
    """The ocean's noise settings in 26.2's form: the surface level in the router, aquifers on, and the sea floor's
    surface rule written with 26.2's stone depth conditions and block states."""
    r = ns["noise_router"]
    r["preliminary_surface_level"] = f"{base}/preliminary_surface_level"
    ns["noise"] = dict(ns["noise"], height=OCEAN_HEIGHT, min_y=OCEAN_MIN_Y)
    ns["sea_level"] = OCEAN_SEA
    ns["default_block"] = {"Name": rock}
    ns["default_fluid"] = {"Name": "minecraft:water", "Properties": {"level": "0"}}
    bedrock = ns["surface_rule"]["sequence"][0]
    block = lambda b: {"type": "minecraft:block", "result_state": {"Name": b}}
    cond = lambda c, then: {"type": "minecraft:condition", "if_true": c, "then_run": then}
    depth = lambda add: {"type": "minecraft:stone_depth", "offset": 0, "surface_type": "floor", "add_surface_depth": add, "secondary_depth_range": 0}
    steep = {"type": "minecraft:steep"}
    ns["surface_rule"] = {"type": "minecraft:sequence", "sequence": [
        bedrock,
        cond({"type": "minecraft:above_preliminary_surface"}, {"type": "minecraft:sequence", "sequence": [
            cond(depth(False), {"type": "minecraft:sequence", "sequence": [
                cond(steep, block(rock)),
                cond({"type": "minecraft:noise_threshold", "noise": "minecraft:surface", "min_threshold": 0.45, "max_threshold": 10.0}, block(rock)),
                block(sand)]}),
            cond(depth(True), {"type": "minecraft:sequence", "sequence": [cond(steep, block(rock)), block(sand)]}),
        ]}),
    ]}
    return ns


def ocean_features(n, feats):
    """Life on the sea floor of World 7: kelp forests, seagrass, coral reefs, glowing coral spires, sea pickles,
    air vents and glowing patches in the rock."""
    floor = [{"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"},
             {"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:water"}},
             {"type": "minecraft:biome"}]
    # pressure coral spires: glowing columns rising from the floor
    w(os.path.join(D, "worldgen/feature/pressure_coral_spire.json"), {
        "type": "minecraft:block_column", "allowed_placement": {"type": "minecraft:matching_blocks", "blocks": "minecraft:water"},
        "direction": "up", "prioritize_tip": False,
        "layers": [{"height": {"type": "minecraft:biased_to_bottom", "min_inclusive": 1, "max_inclusive": 5}, "provider": {"id": f"{NS}:pressure_coral"}}]})
    w(os.path.join(D, "worldgen/placed_feature/pressure_coral_spire.json"), {
        "feature": f"{NS}:pressure_coral_spire", "placement": [{"type": "minecraft:count", "count": 3}, {"type": "minecraft:in_square"}] + floor})
    # air vents: rare cracks breathing air, where a snorkel helmet refills
    w(os.path.join(D, "worldgen/feature/air_vent.json"), {"type": "minecraft:simple_block", "to_place": {"id": f"{NS}:air_vent"}})
    w(os.path.join(D, "worldgen/placed_feature/air_vent.json"), {
        "feature": f"{NS}:air_vent", "placement": [{"type": "minecraft:rarity_filter", "chance": 3}, {"type": "minecraft:in_square"}] + floor})
    # the floor glows in places: pressure coral set into the sand
    w(os.path.join(D, "worldgen/feature/pressure_coral_bed.json"), {
        "type": "minecraft:ore", "discard_chance_on_air_exposure": 0.0, "size": 5,
        "targets": [{"state": f"{NS}:pressure_coral", "target": {"predicate_type": "minecraft:block_match", "block": f"{NS}:abyssal_sand"}}]})
    w(os.path.join(D, "worldgen/placed_feature/pressure_coral_bed.json"), {
        "feature": f"{NS}:pressure_coral_bed", "placement": [{"type": "minecraft:count", "count": 2}, {"type": "minecraft:in_square"},
                                                             {"type": "minecraft:heightmap", "heightmap": "OCEAN_FLOOR"},
                                                             {"type": "minecraft:biome"}]})
    feats[7].append(f"{NS}:pressure_coral_bed")
    feats[9] = ["minecraft:warm_ocean_vegetation", "minecraft:seagrass_deep_warm", "minecraft:kelp_warm", "minecraft:kelp_cold",
                "minecraft:sea_pickle", f"{NS}:pressure_coral_spire", f"{NS}:air_vent"]
    return feats


def inline_material_rule(rule):
    """A 26.3 material rule with every reference to another rule (minecraft:overworld, minecraft:bedrock_floor...)
    replaced by its content from the vanilla templates, so the block swaps below reach the surface blocks too.
    Material conditions (minecraft:on_floor...) stay references: they name no block."""
    if isinstance(rule, str):
        path = os.path.join(MC, "worldgen/material_rule", rule.split(":", 1)[1] + ".json")
        if not os.path.exists(path):
            return rule
        return inline_material_rule(json.load(open(path)))
    if isinstance(rule, dict):
        out = dict(rule)
        if "then_run" in out:
            out["then_run"] = inline_material_rule(out["then_run"])
        if isinstance(out.get("sequence"), list):
            out["sequence"] = [inline_material_rule(x) for x in out["sequence"]]
        return out
    return rule


def template_noise_settings(name):
    """A vanilla noise settings template as text, its material rule inlined (26.3; 26.2 writes it inline already)."""
    txt = open(os.path.join(MC, f"worldgen/noise_settings/{name}.json")).read()
    ns = json.loads(txt)
    if "material_rule" in ns:
        ns["material_rule"] = inline_material_rule(ns["material_rule"])
        txt = json.dumps(ns, indent=2)
    return txt


def swap_block(txt, old, new):
    """Swaps a block id in a template, never a noise of the same name (26.2 has minecraft:netherrack, minecraft:gravel noises)."""
    return re.sub(r'(?<!"noise": )(?<!"noise":)"' + re.escape(old) + '"', f'"{new}"', txt)


def gen_worldgen():
    for wd in WORLDS:
        n = wd["n"]
        key = f"world_{n}"
        top, stone, deep = [f"{NS}:{x}" for x in SURF[n]]
        lang(f"world.{NS}.{n}", wd["en"], wd["fr"])
        lang(f"dimension.{NS}.{key}", f"World {n} — {wd['en']}", f"Monde {n} — {wd['fr']}")
        # noise settings from template, with block substitutions
        tpl = TEMPLATE[wd["gen"]]
        txt = template_noise_settings(tpl)
        for old, new in (("minecraft:grass_block", top), ("minecraft:deepslate", deep), ("minecraft:stone", stone),
                         ("minecraft:netherrack", stone), ("minecraft:soul_sand", top), ("minecraft:soul_soil", top),
                         ("minecraft:end_stone", stone), ("minecraft:podzol", top), ("minecraft:mycelium", top)):
            txt = swap_block(txt, old, new)
        ns = json.loads(txt)
        ns["disable_mob_generation"] = False
        if wd["gen"] == "ocean":
            ns = ocean_settings(ns, n)
        if wd["gen"] == "ceiling":
            ns["default_fluid"] = "minecraft:water" if n == 3 else "minecraft:air"
            ns["sea_level"] = 0
            if n == 5:
                ns["default_fluid"] = "minecraft:air"
        if n == 2:
            ns["default_fluid"] = "minecraft:lava"
            ns["sea_level"] = -40
        # the lesser biomes need a climate: a world whose template has none takes the overworld's
        router = ns["noise_router"]
        ow = json.loads(open(os.path.join(MC, "worldgen/noise_settings/overworld.json")).read())["noise_router"]
        for k in ("temperature", "vegetation"):
            if isinstance(router.get(k), (int, float)):
                router[k] = ow[k]
        ns = with_sub_surfaces(ns, n)
        w(os.path.join(D, f"worldgen/noise_settings/{key}.json"), ns)

        # dimension type
        if wd["ceiling"]:
            dt = jl("dimension_type/the_nether.json")
            dt["attributes"].pop("minecraft:gameplay/piglins_zombify", None)
            dt["attributes"].pop("minecraft:gameplay/fast_lava", None)
            dt["attributes"].pop("minecraft:gameplay/water_evaporates", None)
            dt["attributes"].pop("minecraft:visual/default_dripstone_particle", None)
            dt["attributes"].pop("minecraft:gameplay/snow_golem_melts", None)
            dt["coordinate_scale"] = 1.0
            dt["ambient_light"] = 0.0 if n == 5 else 0.05
            dt["attributes"]["minecraft:visual/fog_end_distance"] = 24.0 if n == 5 else 72.0
            dt["attributes"]["minecraft:visual/fog_start_distance"] = 2.0 if n == 5 else 8.0
            dt["attributes"]["minecraft:visual/ambient_light_color"] = "#000000" if n == 5 else "#1a1d26"
            dt["attributes"]["minecraft:visual/fog_color"] = "#" + wd["fog"]
            dt["attributes"]["minecraft:visual/sky_light_color"] = "#" + wd["sky"]
            dt["attributes"]["minecraft:gameplay/respawn_anchor_works"] = False
            dt["infiniburn"] = "#minecraft:infiniburn_overworld"
            dt["timelines"] = "#minecraft:in_overworld"
            dt.pop("has_fixed_time", None)
            dt["default_clock"] = "minecraft:overworld"
        else:
            dt = jl("dimension_type/overworld.json")
            dt["attributes"]["minecraft:visual/fog_color"] = "#" + wd["fog"]
            dt["attributes"]["minecraft:visual/sky_color"] = "#" + wd["sky"]
            if n == 7:
                dt["attributes"]["minecraft:visual/water_fog_end_distance"] = 48.0
            if wd["gen"] == "floating":
                dt["min_y"], dt["height"], dt["logical_height"] = 0, 256, 256
            if wd["gen"] == "caves":
                dt["min_y"], dt["height"], dt["logical_height"] = -64, 192, 192
                dt["has_skylight"] = True
        noise = ns["noise"]
        dt["min_y"], dt["height"] = noise["min_y"], noise["height"]
        dt["logical_height"] = noise["height"]
        dt["attributes"]["minecraft:gameplay/bed_rule"] = {"can_set_spawn": "never", "can_sleep": "never", "explodes": False,
                                                           "error_message": {"translate": f"message.{NS}.no_beds"}}
        dt["attributes"].pop("minecraft:gameplay/straw_bed_rule", None)
        dt["attributes"]["minecraft:gameplay/nether_portal_spawns_piglin"] = False
        if n == 8:
            dt["default_clock"] = f"{NS}:hastened"
            dt["timelines"] = f"#{NS}:in_hastened"
            w(os.path.join(D, "world_clock/hastened.json"), {})
            day = jl("timeline/day.json")
            day["clock"] = f"{NS}:hastened"
            w(os.path.join(D, "timeline/hastened_day.json"), day)
            moon = jl("timeline/moon.json")
            if "clock" in moon:
                moon["clock"] = f"{NS}:hastened"
            w(os.path.join(D, "timeline/hastened_moon.json"), moon)
            # the seasons tint the light and change the floating particles (tools/atmosphere.py)
            w(os.path.join(D, "world_clock/seasons.json"), {})
            w(os.path.join(D, "timeline/seasons.json"), atmosphere.season_timeline())
            w(os.path.join(D, "tags/timeline/in_hastened.json"), {"values": ["#minecraft:universal", f"{NS}:hastened_day", f"{NS}:hastened_moon", f"{NS}:seasons"]})
        if n in atmosphere.SKY and n != 8:
            # the world's own sky (tools/atmosphere.py): its day and moon timelines in place of vanilla's
            day, moon = atmosphere.sky_timelines(n, jl("timeline/day.json"), jl("timeline/moon.json"))
            w(os.path.join(D, f"timeline/sky_{n}_day.json"), day)
            w(os.path.join(D, f"timeline/sky_{n}_moon.json"), moon)
            w(os.path.join(D, f"tags/timeline/in_world_{n}.json"), {"values": ["#minecraft:universal", f"{NS}:sky_{n}_day", f"{NS}:sky_{n}_moon", "minecraft:early_game"]})
            dt["timelines"] = f"#{NS}:in_world_{n}"
        w(os.path.join(D, f"dimension_type/{key}.json"), dt)

        # biome
        bio = jl("worldgen/biome/plains.json")
        bio["attributes"] = {"minecraft:visual/sky_color": "#" + wd["sky"], "minecraft:visual/fog_color": "#" + wd["fog"],
                             "minecraft:visual/water_fog_color": "#" + wd["water"]}
        spawns = {"monster": [], "ambient": [], "creature": [], "water_creature": [], "underground_water_creature": [], "water_ambient": [], "axolotls": [], "misc": []}
        for m in MOBS:
            if m["world"] != n:
                continue
            cat = "water_creature" if m["aquatic"] else "monster"
            if m["aquatic"]:
                cat = "monster"
            weight = 10 if m["elite"] else (60 if m["behavior"].startswith("swarm") else 40)
            count = {"type": "minecraft:uniform", "min_inclusive": 1, "max_inclusive": 1 if m["elite"] else 3} if not m["behavior"].startswith("swarm") else {"type": "minecraft:uniform", "min_inclusive": 2, "max_inclusive": 4}
            spawns[cat].append({"type": f"{NS}:{m['id']}", "count": count, "weight": weight})
        for (pid, en, fr, pw) in PEOPLES:
            if pw == n:
                spawns["creature"].append({"type": f"{NS}:{pid}", "count": 1, "weight": 2})
        for c in CRITTERS:
            if c["world"] == n:
                hi = 5 if c["behavior"] == "shoal" else 3
                spawns["water_ambient"].append({"type": f"{NS}:{c['id']}", "count": {"type": "minecraft:uniform", "min_inclusive": 1, "max_inclusive": hi},
                                                "weight": 30 if c["behavior"] == "shoal" else 20})
        bio["attributes"]["minecraft:gameplay/natural_mob_spawns"] = {"argument": {"spawn_costs": {}, "spawns_by_category": {k: v for k, v in spawns.items() if v}}} if False else None
        bio["attributes"].pop("minecraft:gameplay/natural_mob_spawns")
        pl = {"argument": {"spawn_costs": {}, "spawns_by_category": {}}, "modifier": "overlay"}
        pl = copy.deepcopy(pl)
        if isinstance(pl, dict) and "argument" in pl:
            pl["argument"]["spawns_by_category"] = {k: v for k, v in spawns.items() if v}
            pl["argument"]["spawn_costs"] = {}
        else:
            pl = {"spawns_by_category": {k: v for k, v in spawns.items() if v}}
        bio["attributes"]["minecraft:gameplay/natural_mob_spawns"] = pl
        bio["effects"] = {"water_color": "#" + wd["water"], "grass_color": "#" + wd["pal"][0], "foliage_color": "#" + wd["pal"][0]}
        feats = [[] for _ in range(11)]
        ores = []
        for (bid, en, fr, style) in TERRAIN[n]:
            if style.startswith("ore"):
                ores.append(bid)
        # the world ores that lie in the rock like any other (tools/content.py WORLD_ORES)
        ores += [b["id"] for b in BLOCKS if b["kind"] == "world_ore" and b["world"] == n and b["id"] in ORE_GEN]
        for bid in ores:
            big = bid == "giant_ore_block"
            if bid in ORE_GEN:
                size, count, lo, hi, extra = ORE_GEN[bid]
                rng = {"type": "minecraft:uniform", "min_inclusive": {"absolute": lo}, "max_inclusive": {"absolute": hi}}
            else:
                size, count, extra = 24 if big else 9, 6 if big else 14, ()
                rng = {"type": "minecraft:uniform", "min_inclusive": {"above_bottom": 4}, "max_inclusive": {"below_top": 20}}
            hosts = [stone, deep] + [f"{NS}:{x}" for x in extra]
            w(os.path.join(D, f"worldgen/feature/{bid}.json"), {
                "type": "minecraft:ore", "discard_chance_on_air_exposure": 0.0, "size": size,
                "targets": [{"state": f"{NS}:{bid}", "target": {"predicate_type": "minecraft:block_match", "block": h}} for h in hosts]})
            w(os.path.join(D, f"worldgen/placed_feature/{bid}.json"), {
                "feature": f"{NS}:{bid}", "placement": [{"type": "minecraft:count", "count": count}, {"type": "minecraft:in_square"},
                                                        {"type": "minecraft:height_range", "height": rng},
                                                        {"type": "minecraft:biome"}]})
            feats[6].append(f"{NS}:{bid}")
        if n == 6:
            # World 6's Hanging Veins: from the air, look up for the underside of the rock and turn it to ore
            hg = HANGING_GEN
            w(os.path.join(D, "worldgen/feature/hanging_ore.json"), {"type": "minecraft:simple_block", "to_place": {"id": f"{NS}:hanging_ore"}})
            w(os.path.join(D, "worldgen/placed_feature/hanging_ore.json"), {
                "feature": f"{NS}:hanging_ore", "placement": [
                    {"type": "minecraft:count", "count": hg["count"]}, {"type": "minecraft:in_square"},
                    {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": hg["lo"]}, "max_inclusive": {"absolute": hg["hi"]}}},
                    {"type": "minecraft:environment_scan", "direction_of_search": "up", "max_steps": hg["scan"],
                     "allowed_search_condition": {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                     "target_condition": {"type": "minecraft:matching_blocks", "blocks": stone}},
                    {"type": "minecraft:biome"}]})
            feats[6].append(f"{NS}:hanging_ore")
        glow = ([b for (b, e, f, s) in TERRAIN[n] if s in ("glow", "glass")] or [TERRAIN[n][2][0]])[0]
        w(os.path.join(D, f"worldgen/feature/{glow}_patch.json"), {
            "type": "minecraft:ore", "discard_chance_on_air_exposure": 0.0, "size": 6,
            "targets": [{"state": f"{NS}:{glow}", "target": {"predicate_type": "minecraft:block_match", "block": stone}}]})
        w(os.path.join(D, f"worldgen/placed_feature/{glow}_patch.json"), {
            "feature": f"{NS}:{glow}_patch", "placement": [{"type": "minecraft:count", "count": 8}, {"type": "minecraft:in_square"},
                                                         {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"above_bottom": 4}, "max_inclusive": {"below_top": 4}}},
                                                         {"type": "minecraft:biome"}]})
        feats[6].append(f"{NS}:{glow}_patch")
        feats[9] = list(VANILLA_FEATURES.get(n, []))
        if wd["gen"] == "ocean":
            feats = ocean_features(n, feats)
        bio["features"] = feats
        bio["carvers"] = ["minecraft:cave", "minecraft:canyon"] if not wd["ceiling"] else ["minecraft:nether_cave"]
        bio["has_precipitation"] = n in (1, 4, 8)
        bio["temperature"] = {1: 0.95, 2: 2.0, 4: 0.5, 7: 0.5}.get(n, 0.8)
        bio["downfall"] = 0.9 if n in (1, 4) else 0.3
        bio["attributes"].update(sound.biome_audio(n))
        bio["attributes"].update(atmosphere.biome(n))
        w(os.path.join(D, f"worldgen/biome/{key}.json"), bio)
        lang(f"biome.{NS}.{key}", f"World {n}", f"Monde {n}")
        in_world = [f"{NS}:{key}"]
        for (sub, en, fr, top, grass, fog) in SUB_BIOMES.get(n, []):
            sb = copy.deepcopy(bio)
            sb["effects"]["grass_color"] = "#" + grass
            sb["effects"]["foliage_color"] = "#" + grass
            sb["attributes"]["minecraft:visual/fog_color"] = "#" + fog
            # its own variation of the world's theme
            sb["attributes"]["minecraft:audio/background_music"] = sound.biome_audio(n, sub)["minecraft:audio/background_music"]
            w(os.path.join(D, f"worldgen/biome/{key}_{sub}.json"), sb)
            lang(f"biome.{NS}.{key}_{sub}", f"{en} (World {n})", f"{fr} (Monde {n})")
            in_world.append(f"{NS}:{key}_{sub}")
        w(os.path.join(D, f"tags/worldgen/biome/in_{key}.json"), {"values": in_world})

        # dimension
        w(os.path.join(D, f"dimension/{key}.json"), {"type": f"{NS}:{key}", "generator": {
            "type": "minecraft:noise", "biome_source": biome_source(n), "settings": f"{NS}:{key}"}})

        # structures
        for i, (sid, en, fr, role, size, rarity, arch) in enumerate(STRUCTURES[n]):
            lang(f"structure.{NS}.{sid}", en, fr)
            w(os.path.join(D, f"worldgen/structure/{sid}.json"), {
                "type": f"{NS}:procedural", "biomes": f"#{NS}:in_{key}", "spawn_overrides": {}, "step": "surface_structures",
                "terrain_adaptation": "beard_thin" if not wd["ceiling"] else "none",
                "world": n, "archetype": arch, "role": role, "size": size, "structure_id": sid})
            spacing = {"common": 18, "rare": 34, "unique": 64, "wonder": 80}[rarity] + (8 if size == "large" else 0)
            w(os.path.join(D, f"worldgen/structure_set/{sid}.json"), {
                "placement": {"type": "minecraft:random_spread", "salt": 731000 + n * 100 + i, "separation": max(4, spacing // 3), "spacing": spacing},
                "structures": [{"structure": f"{NS}:{sid}", "weight": 1}]})
        # World 10 at doll scale: the giant sewing and carpentry things on the workshop floor (scenery only)
        if n == 10:
            for i, (sid, en, fr, arch, spacing, sep) in enumerate(WORKSHOP_PROPS):
                lang(f"structure.{NS}.{sid}", en, fr)
                w(os.path.join(D, f"worldgen/structure/{sid}.json"), {
                    "type": f"{NS}:procedural", "biomes": f"#{NS}:in_{key}", "spawn_overrides": {}, "step": "surface_structures",
                    "terrain_adaptation": "beard_thin", "world": n, "archetype": arch, "role": "decor", "size": "large", "structure_id": sid})
                w(os.path.join(D, f"worldgen/structure_set/{sid}.json"), {
                    "placement": {"type": "minecraft:random_spread", "salt": 741000 + i, "separation": sep, "spacing": spacing},
                    "structures": [{"structure": f"{NS}:{sid}", "weight": 1}]})
    # refuge dimension (pocket doll): flat void
    w(os.path.join(D, "dimension/refuge.json"), {"type": f"{NS}:refuge", "generator": {"type": "minecraft:flat", "settings": {
        "biome": f"{NS}:refuge", "layers": [], "lakes": False, "features": False, "structure_overrides": []}}})
    dt = jl("dimension_type/overworld.json")
    dt["attributes"]["minecraft:gameplay/bed_rule"] = {"can_set_spawn": "never", "can_sleep": "never", "explodes": False}
    dt["attributes"].pop("minecraft:gameplay/straw_bed_rule", None)
    dt["attributes"]["minecraft:visual/sky_color"] = "#c8342a"
    dt["attributes"]["minecraft:visual/fog_color"] = "#e8c050"
    dt["min_y"], dt["height"], dt["logical_height"] = 0, 256, 256
    w(os.path.join(D, "dimension_type/refuge.json"), dt)
    rb = jl("worldgen/biome/plains.json")
    rb["features"] = [[] for _ in range(11)]
    rb["carvers"] = []
    rb["attributes"] = {"minecraft:visual/sky_color": "#c8342a"}
    rb["attributes"]["minecraft:audio/background_music"] = sound.biome_audio(0)["minecraft:audio/background_music"]
    pl = copy.deepcopy({"argument": {"spawn_costs": {}, "spawns_by_category": {}}, "modifier": "overlay"})
    if isinstance(pl, dict) and "argument" in pl:
        pl["argument"]["spawns_by_category"] = {}
    rb["attributes"]["minecraft:gameplay/natural_mob_spawns"] = pl
    w(os.path.join(D, "worldgen/biome/refuge.json"), rb)
    lang(f"biome.{NS}.refuge", "Refuge Doll", "Poupée-refuge")
    # guardian sanctuary on the surface (overworld)
    lang(f"structure.{NS}.guardian_sanctuary", "Guardian Sanctuary", "Sanctuaire du Gardien")
    w(os.path.join(D, "worldgen/structure/guardian_sanctuary.json"), {
        "type": f"{NS}:procedural", "biomes": "#minecraft:is_overworld", "spawn_overrides": {}, "step": "surface_structures",
        "terrain_adaptation": "beard_thin", "world": 0, "archetype": "sanctuary", "role": "story", "size": "medium", "structure_id": "guardian_sanctuary"})
    w(os.path.join(D, "worldgen/structure_set/guardian_sanctuary.json"), {
        "placement": {"type": "minecraft:random_spread", "salt": 7310001, "spacing": 24, "separation": 10},
        "structures": [{"structure": f"{NS}:guardian_sanctuary", "weight": 1}]})
    # the Surface's own places before the first boss: the Artisan's workshop, the Peddler's stall, a fallen doll
    for i, (sid, en, fr, role, size, arch, spacing, sep) in enumerate(SURFACE_PLACES):
        lang(f"structure.{NS}.{sid}", en, fr)
        w(os.path.join(D, f"worldgen/structure/{sid}.json"), {
            "type": f"{NS}:procedural", "biomes": "#minecraft:has_structure/pillager_outpost", "spawn_overrides": {}, "step": "surface_structures",
            "terrain_adaptation": "beard_thin", "world": 0, "archetype": arch, "role": role, "size": size, "structure_id": sid})
        w(os.path.join(D, f"worldgen/structure_set/{sid}.json"), {
            "placement": {"type": "minecraft:random_spread", "salt": 7320001 + i, "spacing": spacing, "separation": sep},
            "structures": [{"structure": f"{NS}:{sid}", "weight": 1}]})
    for k2, (en, fr) in SURFACE_NOTES.items():
        lang(k2, en, fr)


SURFACE_PLACES = [
    ("artisan_cabin", "Artisan's Old Cabin", "Vieille cabane de l'Artisan", "story", "medium", "artisan_cabin", 28, 10),
    ("peddler_stall", "Peddler's Stall", "Étal du Colporteur", "utility", "small", "peddler_stall", 32, 12),
    ("fallen_doll", "Fallen Doll", "Poupée tombée", "exploration", "large", "fallen_doll", 40, 16),
]
SURFACE_NOTES = {
    "item.matriochka.artisan_note": ("Artisan's Note", "Note de l'Artisan"),
    "item.matriochka.artisan_note.0": ("\"I set the Guardian to sleep in a ring of eight pillars, a few hundred steps from here. Wake it only when you mean to go down.\"",
                                       "« J'ai couché le Gardien dans un cercle de huit piliers, à quelques centaines de pas d'ici. Ne le réveille que si tu comptes descendre. »"),
    "item.matriochka.artisan_note.1": ("\"Every doll holds a world, and every world holds the next. I carved ten. The eleventh I never finished.\"",
                                       "« Chaque poupée contient un monde, et chaque monde le suivant. J'en ai sculpté dix. La onzième, je ne l'ai jamais finie. »"),
    "item.matriochka.artisan_note.2": ("\"Soil from the Guardian, a seed from its core, water close by. That is how the first one opens.\"",
                                       "« De la terre du Gardien, une graine de son noyau, de l'eau tout près. C'est ainsi que s'ouvre la première. »"),
}


# ------------------------------------------------------------------ World 0
def gen_world_zero():
    """The smallest doll: a sealed hollow of painted wood and lacquer (the Nether noise turned inside a doll),
    no sky, warm lantern light, no natural spawns. Its rooms are built by the mod on first entry (WorldZero.java)."""
    wd = WORLD_ZERO
    key = wd["key"]
    lang(f"world.{NS}.{wd['n']}", wd["en"], wd["fr"])
    lang(f"dimension.{NS}.{key}", f"World 0 — {wd['en']}", f"Monde 0 — {wd['fr']}")
    lang(f"biome.{NS}.{key}", "World 0", "Monde 0")
    top, stone, deep = f"{NS}:workshop_felt", f"{NS}:painted_wood", f"{NS}:lacquer_block"
    txt = template_noise_settings("nether")
    for old, new in (("minecraft:netherrack", stone), ("minecraft:soul_sand", top), ("minecraft:soul_soil", top),
                     ("minecraft:gravel", top), ("minecraft:basalt", deep), ("minecraft:blackstone", deep),
                     ("minecraft:crimson_nylium", top), ("minecraft:warped_nylium", top),
                     ("minecraft:warped_wart_block", deep), ("minecraft:nether_wart_block", deep), ("minecraft:lava", "minecraft:air")):
        txt = swap_block(txt, old, new)
    ns = json.loads(txt)
    ns["default_fluid"] = "minecraft:air"
    ns["sea_level"] = 0
    ns["disable_mob_generation"] = True
    w(os.path.join(D, f"worldgen/noise_settings/{key}.json"), ns)
    dt = jl("dimension_type/the_nether.json")
    for k in ("minecraft:gameplay/piglins_zombify", "minecraft:gameplay/fast_lava", "minecraft:gameplay/water_evaporates",
              "minecraft:visual/default_dripstone_particle", "minecraft:gameplay/snow_golem_melts", "minecraft:gameplay/straw_bed_rule"):
        dt["attributes"].pop(k, None)
    dt["coordinate_scale"] = 1.0
    # no sky inside the smallest doll: the lacquer itself must carry some light, or the whole world sinks into its red
    # haze (the biome's atmosphere, tools/atmosphere.py, sets the fog and the warm ambient tint over this)
    dt["ambient_light"] = 0.3
    dt["attributes"]["minecraft:visual/fog_end_distance"] = 112.0
    dt["attributes"]["minecraft:visual/fog_start_distance"] = 12.0
    dt["attributes"]["minecraft:visual/ambient_light_color"] = "#b8805a"
    dt["attributes"]["minecraft:visual/fog_color"] = "#" + wd["fog"]
    dt["attributes"]["minecraft:visual/sky_light_color"] = "#" + wd["sky"]
    dt["attributes"]["minecraft:gameplay/respawn_anchor_works"] = False
    dt["attributes"]["minecraft:gameplay/nether_portal_spawns_piglin"] = False
    dt["attributes"]["minecraft:gameplay/bed_rule"] = {"can_set_spawn": "never", "can_sleep": "never", "explodes": False,
                                                       "error_message": {"translate": f"message.{NS}.no_beds"}}
    dt["infiniburn"] = "#minecraft:infiniburn_overworld"
    dt["timelines"] = "#minecraft:in_overworld"
    dt.pop("has_fixed_time", None)
    dt["default_clock"] = "minecraft:overworld"
    noise = ns["noise"]
    dt["min_y"], dt["height"], dt["logical_height"] = noise["min_y"], noise["height"], noise["height"]
    w(os.path.join(D, f"dimension_type/{key}.json"), dt)
    bio = jl("worldgen/biome/plains.json")
    pl = copy.deepcopy(bio["attributes"].get("minecraft:gameplay/natural_mob_spawns", {"argument": {"spawn_costs": {}, "spawns_by_category": {}}, "modifier": "overlay"}))
    if isinstance(pl, dict) and "argument" in pl:
        pl["argument"]["spawns_by_category"] = {}
        pl["argument"]["spawn_costs"] = {}
    else:
        pl = {"spawns_by_category": {}}
    bio["attributes"] = {"minecraft:visual/sky_color": "#" + wd["sky"], "minecraft:visual/fog_color": "#" + wd["fog"],
                         "minecraft:visual/water_fog_color": "#" + wd["water"], "minecraft:gameplay/natural_mob_spawns": pl}
    bio["effects"] = {"water_color": "#" + wd["water"], "grass_color": "#" + wd["pal"][0], "foliage_color": "#" + wd["pal"][0]}
    bio["features"] = [[] for _ in range(11)]
    bio["carvers"] = ["minecraft:nether_cave"]
    bio["has_precipitation"] = False
    bio["temperature"] = 0.8
    bio["downfall"] = 0.0
    bio["attributes"].update(sound.biome_audio(0))
    bio["attributes"].update(atmosphere.biome(wd["n"]))
    w(os.path.join(D, f"worldgen/biome/{key}.json"), bio)
    w(os.path.join(D, f"dimension/{key}.json"), {"type": f"{NS}:{key}", "generator": {
        "type": "minecraft:noise", "biome_source": {"type": "minecraft:fixed", "biome": f"{NS}:{key}"}, "settings": f"{NS}:{key}"}})


# ------------------------------------------------------------------ story texts
def gen_lang_story():
    for wn, pages in JOURNAL.items():
        for i, (te, be, tf, bf) in enumerate(pages):
            lang(f"journal.{NS}.page.{wn}.{i}.title", te, tf)
            lang(f"journal.{NS}.page.{wn}.{i}", be, bf)
    for wn, (en, fr) in DOLL_LINES.items():
        lang(f"message.{NS}.doll_line.{wn}", en, fr)
    for kind, e in ENDINGS.items():
        lang(f"ending.{NS}.{kind}", e["en"], e["fr"])
        for i, (en, fr) in enumerate(e["lines"]):
            lang(f"ending.{NS}.{kind}.{i}", en, fr)
        lang(f"ending.{NS}.{kind}.lasting", *e["lasting"])
    for i, (en, fr) in enumerate(CREDITS):
        lang(f"ending.{NS}.credits.{i}", en, fr)
    for k, (en, fr) in STORY_UI.items():
        lang(k, en, fr)


# ------------------------------------------------------------------ advancements
def gen_endings_tab():
    """The Endings tab: its root appears once the Unfinished has fallen; the entries are granted by the mod."""
    w(os.path.join(D, "advancement/endings/root.json"), {
        "display": {"icon": {"id": f"{NS}:whole_matryoshka"}, "title": {"translate": f"advancement.{NS}.endings.title"},
                    "description": {"translate": f"advancement.{NS}.endings.desc"}, "background": f"{NS}:block/lacquer_glow",
                    "show_toast": False, "announce_to_chat": False},
        "criteria": {"done": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": {"type": "minecraft:entity_properties",
                     "entity": "this", "predicate": {"minecraft:entity_type": f"{NS}:the_unfinished"}}}}}})
    lang(f"advancement.{NS}.endings.title", "The Last Doll", "La dernière poupée")
    lang(f"advancement.{NS}.endings.desc", "Every ending of the cycle.", "Toutes les fins du cycle.")
    for (aid, icon, te, tf, de, df) in ENDING_ADVANCEMENTS:
        w(os.path.join(D, f"advancement/endings/{aid}.json"), {
            "parent": f"{NS}:endings/root",
            "display": {"icon": {"id": f"{NS}:{icon}"}, "title": {"translate": f"advancement.{NS}.endings.{aid}.title"},
                        "description": {"translate": f"advancement.{NS}.endings.{aid}.desc"}, "frame": "challenge", "hidden": aid == "world_zero"},
            "criteria": {"done": {"trigger": "minecraft:impossible"}},
            "rewards": {"function": f"{NS}:reward/hidden"}})
        lang(f"advancement.{NS}.endings.{aid}.title", te, tf)
        lang(f"advancement.{NS}.endings.{aid}.desc", de, df)


def gen_advancements():
    # root tab per world
    roots = {}
    icon_for = {0: "artisan_scroll"}
    for wd in WORLDS:
        icon_for[wd["n"]] = f"seed_{wd['n']}"
    surface_root = {"display": {"icon": {"id": f"{NS}:artisan_scroll"}, "title": {"translate": f"advancement.{NS}.root.title"},
                                "description": {"translate": f"advancement.{NS}.root.desc"}, "background": f"{NS}:block/lacquer_block",
                                "show_toast": False, "announce_to_chat": False},
                    "criteria": {"tick": {"trigger": "minecraft:tick"}}}
    lang(f"advancement.{NS}.root.title", "Matriochka", "Matriochka")
    lang(f"advancement.{NS}.root.desc", "Every block can hold a world.", "Chaque bloc peut contenir un monde.")
    w(os.path.join(D, "advancement/root.json"), surface_root)
    for n, lst in ACH.items():
        wd = WORLDS[n - 1]
        rid = f"world_{n}/root"
        terr = SURF[n][0]
        w(os.path.join(D, f"advancement/{rid}.json"), {
            "display": {"icon": {"id": f"{NS}:seed_{n}"}, "title": {"translate": f"advancement.{NS}.w{n}.title"},
                        "description": {"translate": f"advancement.{NS}.w{n}.desc"}, "background": f"{NS}:block/{terr}",
                        "show_toast": False, "announce_to_chat": False},
            "criteria": {"seed": {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": f"{NS}:seed_{n}"}]}},
                         "enter": {"trigger": "minecraft:changed_dimension", "conditions": {"to": f"{NS}:world_{n}"}}},
            "requirements": [["seed", "enter"]]})
        lang(f"advancement.{NS}.w{n}.title", f"World {n}: {wd['en']}", f"Monde {n} : {wd['fr']}")
        lang(f"advancement.{NS}.w{n}.desc", "Craft or find this world's Seed.", "Fabriquer ou trouver la Graine de ce monde.")
        prev = rid
        for i, (typ, en, fr, den, dfr, trig) in enumerate(lst):
            aid = f"world_{n}/a{i}"
            kind, arg = trig
            if kind == "enter":
                crit = {"trigger": "minecraft:changed_dimension", "conditions": {"to": f"{NS}:world_{arg}"}}
            elif kind == "item":
                crit = {"trigger": "minecraft:inventory_changed", "conditions": {"items": [{"items": f"{NS}:{arg}"}]}}
            elif kind == "kill":
                crit = {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"minecraft:entity_type": f"{NS}:{arg}"}}}}
            else:
                crit = {"trigger": "minecraft:impossible"}
            icon = {"progress": f"{NS}:seed_{n}", "explore": "minecraft:compass", "combat": "minecraft:iron_sword", "hidden": f"{NS}:hidden_doll_{n}"}[typ]
            if kind == "item":
                icon = f"{NS}:{arg}"
            frame = {"progress": "task", "explore": "goal", "combat": "challenge", "hidden": "challenge"}[typ]
            w(os.path.join(D, f"advancement/{aid}.json"), {
                "parent": f"{NS}:{prev if typ != 'hidden' else rid}",
                "display": {"icon": {"id": icon}, "title": {"translate": f"advancement.{NS}.w{n}.a{i}.title"},
                            "description": {"translate": f"advancement.{NS}.w{n}.a{i}.desc"}, "frame": frame, "hidden": typ == "hidden"},
                "criteria": {"done": crit},
                "rewards": {"function": f"{NS}:reward/{typ}"}})
            lang(f"advancement.{NS}.w{n}.a{i}.title", en, fr)
            lang(f"advancement.{NS}.w{n}.a{i}.desc", den, dfr)
            if typ == "progress":
                prev = aid
    for typ, souls in (("progress", 5), ("explore", 10), ("combat", 0), ("hidden", 0)):
        w(os.path.join(D, f"function/reward/{typ}.mcfunction"), f"matriochka karma soul @s {souls}\n" if souls else "# titles and cosmetics are granted by the mod\n")


# ------------------------------------------------------------------ misc lang
def gen_lang_misc():
    for k, v in RULES.items():
        lang(f"rule.{NS}.{k}", v["en"], v["fr"])
    for (cid, en, fr, applies, den, dfr) in CLASSES:
        lang(f"class.{NS}.{cid}", en, fr)
        lang(f"class.{NS}.{cid}.desc", den, dfr)
    for q in QUESTS:
        qid, wd, t, obj, en, fr, den, dfr, rew = q
        lang(f"quest.{NS}.{qid}", en, fr)
        lang(f"quest.{NS}.{qid}.desc", den, dfr)
    for (pid, en, fr, wd) in PEOPLES:
        pass
    for r, (en, fr) in {"none": ("Soulless", "Sans âme"), "common": ("Common", "Commun"), "rare": ("Rare", "Rare"),
                        "epic": ("Epic", "Épique"), "legendary": ("Legendary", "Légendaire")}.items():
        lang(f"rarity.{NS}.{r}", en, fr)
    for (vid, rule, danger, loot, spawn, en, fr, den, dfr) in VARIANT_KINDS:
        lang(f"variant.{NS}.{vid}", en, fr)
        lang(f"variant.{NS}.{vid}.desc", den, dfr)
    for n, ((cen, cfr), (wen, wfr)) in VARIANT_NAMES.items():
        lang(f"variant.{NS}.{n}.calm", cen, cfr)
        lang(f"variant.{NS}.{n}.wild", wen, wfr)
    for (mid, en, fr, den, dfr) in MUTATIONS:
        lang(f"mutation.{NS}.{mid}", en, fr)
        lang(f"mutation.{NS}.{mid}.desc", den, dfr)
    lang(f"itemGroup.{NS}.main", "Matriochka", "Matriochka")
    lang(f"itemGroup.{NS}.worlds", "Matriochka — Worlds", "Matriochka — Mondes")


# ------------------------------------------------------------------ java
def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def attack_java(a):
    fx = ",".join(f"{e}:{t}:{lv}" for e, t, lv in a["fx"])
    g = ",".join(f"{k}:{v}" for k, v in a["g"])
    sf = ",".join(f"{e}:{t}:{lv}" for e, t, lv in a["self"])
    f = lambda k, d=0: a.get(k, d)
    return (f"new Defs.AttackDef({jstr(a['slug'])}, {jstr(a['kind'])}, {f('m')}f, {f('r')}f, {f('n', 1)}, {f('iv', 4)}, {f('kb')}f, {f('up')}f, "
            f"{a['hit']}, {a['end']}, {int(a['cd'] * 20)}, {a['min']}f, {a['max']}f, {f('hold', 40)}, {f('dur', 100)}, {f('fire')}, {f('heal')}f, "
            f"{f('count', 1)}, {jstr(f('summon', ''))}, {jstr(fx)}, {jstr(g)}, {jstr(sf)}, {jstr(a['p'])}, {jstr(a['s'])})")


def gen_java():
    L = ["package fr.achedon12.matriochka.content;", "", "import java.util.List;", "",
         "/** GENERATED by tools/gen.py from tools/content.py. Do not edit by hand. */",
         "public final class Content {", "\tprivate Content() {}", ""]
    L.append("\t/** Worlds of the hidden dolls, from the smallest (innermost) to the largest: the order they nest in. */")
    L.append("\tpublic static final int[] NEST_ORDER = {" + ", ".join(str(n) for n in NEST_ORDER) + "};")
    L.append("\t/** Index of the coded page of every world in the Artisan's Journal. */")
    L.append(f"\tpublic static final int JOURNAL_CODED = {JOURNAL_CODED};")
    L.append("\tpublic static final List<Defs.WorldDef> WORLDS = List.of(")
    rows = []
    for wd in WORLDS:
        n = wd["n"]
        glow = ([b for (b, e, f, st) in TERRAIN[n] if st in ("glow", "glass")] or [TERRAIN[n][2][0]])[0]
        rows.append(f"\t\tnew Defs.WorldDef({n}, {jstr(wd['rule'])}, {jstr(wd['tier'])}, 0x{wd['pal'][0]}, 0x{wd['pal'][2]}, {str(wd['ceiling']).lower()}, "
                    f"0x{wd['sky']}, {jstr(SURF[n][0])}, {jstr(SURF[n][1])}, {jstr(glow)})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\t/** World variants, chosen while a Seed hatches (see tools/content.py VARIANT_KINDS). */")
    L.append("\tpublic static final List<Defs.VariantDef> VARIANTS = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.VariantDef({jstr(v[0])}, {v[1]}f, {v[2]}f, {v[3]}f, {v[4]}f)" for v in VARIANT_KINDS))
    L.append("\t);")
    for kind in ("calm", "wild"):
        L.append(f"\tpublic static final List<String> VARIANT_FEED_{kind.upper()} = List.of(" + ", ".join(jstr(x) for x in VARIANT_FEED[kind]) + ");")
        L.append(f"\tpublic static final List<String> VARIANT_GROUND_{kind.upper()} = List.of(" + ", ".join(jstr(x) for x in VARIANT_GROUND[kind]) + ");")
    L.append(f"\tpublic static final int VARIANT_LEAN = {VARIANT_LEAN};")
    L.append(f"\tpublic static final int MUTATION_FROM = {MUTATION_FROM};")
    L.append("\tpublic static final List<String> MUTATIONS = List.of(" + ", ".join(jstr(m[0]) for m in MUTATIONS) + ");")
    L.append("\t/** Mutation of a wild world's boss, by world number (empty: none). */")
    L.append("\tpublic static final String[] WILD_MUTATION = {" + ", ".join(jstr(WILD_MUTATION.get(i, "")) for i in range(12)) + "};")
    # the ten world ores, the Nesting Cradle and the Matriarch Armour (tools/content.py WORLD_ORES, ORE_RULES, MATRIARCH)
    L.append("\t/** The ore of each world, by world number (1 to 10): the ten the Nesting Cradle takes. */")
    L.append("\tpublic static final String[] WORLD_ORES = {\"\", " + ", ".join(jstr(WORLD_ORES[n]) for n in range(1, 11)) + "};")
    for k, v in ORE_RULES.items():
        name = "ORE_" + k.upper()
        if isinstance(v, tuple):
            L.append(f"\tpublic static final int[] {name} = {{{', '.join(str(x) for x in v)}}};")
        elif isinstance(v, float):
            L.append(f"\tpublic static final float {name} = {v}f;")
        else:
            L.append(f"\tpublic static final int {name} = {v};")
    mt = MATRIARCH
    L.append(f"\tpublic static final int MATRIARCH_ARMOR = {mt['armor']}, MATRIARCH_DURABILITY = {mt['durability']}, MATRIARCH_ENCHANT = {mt['enchant']}, MATRIARCH_SAVE_COOLDOWN = {mt['save_cooldown']};")
    L.append(f"\tpublic static final float MATRIARCH_TOUGHNESS = {mt['toughness']}f, MATRIARCH_KNOCKBACK = {mt['knockback']}f, MATRIARCH_EXTRA_HEALTH = {mt['extra_health']}f, "
             f"MATRIARCH_GAUGE = {mt['gauge']}f, MATRIARCH_SAVE_HEALTH = {mt['save_health']}f;")
    L.append("\t/** Matriochkite Ingots per Matriarch piece: helmet, chestplate, leggings, boots. */")
    L.append("\tpublic static final int[] MATRIARCH_INGOTS = {" + ", ".join(str(mt['ingots'][p]) for p in ("helmet", "chestplate", "leggings", "boots")) + "};")
    L.append("\t/** The cradle's ritual, in ticks from its start (tools/content.py CRADLE_TIMELINE, its animation in tools/cradle_geo.py). */")
    L.append("\tpublic static final int " + ", ".join(f"CRADLE_{k.upper()} = {v}" for k, v in CRADLE_TIMELINE.items()) + ";")
    L.append("\t/** The Nesting Cradle's recipe at its station: ids and counts, in turn. */")
    L.append(f"\tpublic static final String CRADLE_STATION = {jstr(CRADLE_RECIPE[0])};")
    L.append("\tpublic static final Object[] CRADLE_INPUTS = {" + ", ".join(f"{jstr(i)}, {n}" for i, n in CRADLE_RECIPE[1]) + "};")
    L.append("\tpublic static final List<Defs.ItemDef> ITEMS = List.of(")
    rows = []
    for it in ALL_ITEMS:
        rows.append(f"\t\tnew Defs.ItemDef({jstr(it['id'])}, {it['world']}, {jstr(it['kind'])}, {jstr(it['rarity'])}, {jstr(it.get('piece', ''))}, {jstr(it.get('set', ''))})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.BlockDef> BLOCKS = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.BlockDef({jstr(b['id'])}, {b['world']}, {jstr(b['kind'])}, {jstr(b['style'])}, {jstr(ORE_DROPS.get(b['id'], ''))})" for b in BLOCKS))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.MobDef> MOBS = List.of(")
    rows = []
    for m in MOBS:
        wd, ht = ENTITY_DIMS[m["id"]]
        mv = ", ".join(attack_java(a) for a in attacks.full(m["id"]))
        rows.append(f"\t\tnew Defs.MobDef({jstr(m['id'])}, {m['world']}, {m['hp']}f, {m['dmg']}f, {jstr(m['behavior'])}, {m['size']}f, {wd:.2f}f, {ht:.2f}f, "
                    f"{jstr(m['drop'])}, {jstr(m['rare_drop'] or '')}, {str(m['elite']).lower()}, {str(m['nesting']).lower()}, {str(m['flying']).lower()}, {str(m['aquatic']).lower()}, List.of({mv}))")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.BossDef> BOSSES = List.of(")
    rows = []
    for b in ALL_BOSSES:
        wd, ht = ENTITY_DIMS[b["id"]]
        ph = ", ".join(f"{p}f" for p in b["phases"])
        rows.append(f"\t\tnew Defs.BossDef({jstr(b['id'])}, {b['world']}, {b['hp']}f, {b['dmg']}f, {b['size']}f, {wd:.2f}f, {ht:.2f}f, {jstr(b['core'])}, new float[]{{{ph}}}, "
                    f"{str(b.get('flying', False)).lower()}, {str(b.get('aquatic', False)).lower()}, {jstr(b.get('meet', 'altar'))}, {jstr(b.get('offering', ''))})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.NpcDef> PEOPLES = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.NpcDef({jstr(p[0])}, {p[3]})" for p in PEOPLES))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.CritterDef> CRITTERS = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.CritterDef({jstr(c['id'])}, {c['world']}, {c['hp']}f, {jstr(c['behavior'])}, "
                        f"{ENTITY_DIMS[c['id']][0]:.2f}f, {ENTITY_DIMS[c['id']][1]:.2f}f)" for c in CRITTERS))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.SnorkelDef> SNORKELS = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.SnorkelDef({jstr(s[0])}, {jstr(s[3])}, {s[4]}, {s[5]}, {s[6]}, {s[7]}, {s[8]}f, {s[9]}f, {s[10]})" for s in SNORKELS))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.StructureDef> STRUCTURES = List.of(")
    rows = []
    for n, lst in STRUCTURES.items():
        for (sid, en, fr, role, size, rarity, arch) in lst:
            rows.append(f"\t\tnew Defs.StructureDef({jstr(sid)}, {n}, {jstr(role)}, {jstr(size)}, {jstr(rarity)}, {jstr(arch)})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.QuestDef> QUESTS = List.of(")
    rows = []
    for (qid, wd, t, obj, en, fr, den, dfr, rew) in QUESTS:
        rows.append(f"\t\tnew Defs.QuestDef({jstr(qid)}, {wd}, {jstr(t)}, {jstr(obj[0])}, {jstr(obj[1])}, {obj[2]}, {jstr(rew[0])}, {jstr(rew[1])}, {rew[2]})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("\tpublic static final List<Defs.AchDef> ACHIEVEMENTS = List.of(")
    rows = []
    for n, lst in ACH.items():
        for i, (typ, en, fr, den, dfr, trig) in enumerate(lst):
            rows.append(f"\t\tnew Defs.AchDef(\"world_{n}/a{i}\", {n}, {jstr(typ)}, {jstr(trig[0])}, {jstr(str(trig[1]))})")
    L.append(",\n".join(rows))
    L.append("\t);")
    L.append("}")
    os.makedirs(os.path.dirname(JAVA), exist_ok=True)
    open(JAVA, "w").write("\n".join(L) + "\n")


def main():
    if TARGET != "26.3":
        # only the world generation differs between versions (tools/versions.py keeps what differs)
        expand_items()
        gen_worldgen()
        gen_world_zero()
        print("worldgen for", TARGET, "in", RES)
        return
    expand_items()
    gen_items()
    print("held dolls in 3D:", held3d.gen(A, NS, [it["id"] if isinstance(it, dict) else it[0] for it in ALL_ITEMS], w))
    gen_blocks()
    ores_art.gen(w, A, lang, ORE_HOW)
    cradle_geo.gen(w, A)
    matriarch_geo.gen(w, A)
    gen_entities()
    gen_worldgen()
    gen_world_zero()
    gen_advancements()
    gen_endings_tab()
    gen_lang_misc()
    gen_lang_story()
    gen_java()
    particles.gen(A, PARTICLES_JAVA)
    gen_replay.gen(lang, w, ROOT)
    rendered = sound.gen(A, SOUNDS_JAVA, lang, w)
    # merge hand-written lang (ui strings)
    for code, table in (("en_us", EN), ("fr_fr", FR)):
        extra = os.path.join(ROOT, f"tools/lang/{code}.json")
        if os.path.exists(extra):
            table.update(json.load(open(extra, encoding="utf-8")))
        w(os.path.join(A, f"lang/{code}.json"), dict(sorted(table.items())))
    # every other language: tools/i18n/<code>.json, checked against English (missing keys fall back to English)
    print("translations:", translations.write(EN, A, w))
    print(f"items={len(ALL_ITEMS)} blocks={len(BLOCKS)} mobs={len(MOBS)} bosses={len(BOSSES)} "
          f"structures={sum(len(v) for v in STRUCTURES.values())} quests={len(QUESTS)} achievements={sum(len(v) for v in ACH.values())} lang={len(EN)} "
          f"sounds={len(sound.SOUNDS)} rendered={rendered}")


if __name__ == "__main__":
    main()
