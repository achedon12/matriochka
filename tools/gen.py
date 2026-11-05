#!/usr/bin/env python3
"""Generates Matriochka assets, data and Java definitions from content.py.

Usage: python3 tools/gen.py  (from the repository root)
Vanilla worldgen templates are read from $MC_DATA (extracted 26.3 data folder).
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import *  # noqa
from paint import paint_item, paint_armor_item, paint_armor_layer, paint_block, paint_station_top, hx
import models
import bosses_hd
import attacks
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobs_hd"))
import registry as mobs_registry  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES = os.path.join(ROOT, "src/main/resources")
A = os.path.join(RES, "assets/matriochka")
D = os.path.join(RES, "data/matriochka")
JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content/Content.java")
MC = os.environ.get("MC_DATA", os.path.join(os.path.dirname(os.path.abspath(__file__)), "vanilla"))
NS = "matriochka"

EN, FR = {}, {}
# every boss the mod registers: the ten worlds and the Surface, plus the hidden encounter of World 0
ALL_BOSSES = BOSSES + [WORLD_ZERO_BOSS]


def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(obj, str):
            f.write(obj)
        else:
            json.dump(obj, f, indent=2, ensure_ascii=False)


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
ALL_ITEMS = []  # (id, world, kind, rarity, extra dict)


def expand_items():
    seen = set()
    for it in ITEMS:
        if it["kind"] == "armorset":
            for pid, pen, pfr in ARMOR_PIECES:
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
        p = pal(it["world"])
        tpath = os.path.join(A, f"textures/item/{iid}.png")
        if it["kind"] == "armor":
            paint_armor_item(it["piece"], p, iid, tpath)
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
            paint_armor_layer(p, sid, mk(os.path.join(A, f"textures/entity/equipment/humanoid/{sid}.png")))
            paint_armor_layer(p, sid + "l", mk(os.path.join(A, f"textures/entity/equipment/humanoid_leggings/{sid}.png")), legs=True)
            w(os.path.join(A, f"equipment/{sid}.json"), {"layers": {"humanoid": [{"texture": f"{NS}:{sid}"}],
                                                                   "humanoid_leggings": [{"texture": f"{NS}:{sid}"}]}})
    for eq, wd in (("filter_mask", 1), ("gravity_boots", 6), ("grip_boots", 9)):
        paint_armor_layer(pal(wd), eq, mk(os.path.join(A, f"textures/entity/equipment/humanoid/{eq}.png")))
        w(os.path.join(A, f"equipment/{eq}.json"), {"layers": {"humanoid": [{"texture": f"{NS}:{eq}"}]}})


# ------------------------------------------------------------------ blocks
def gen_blocks():
    for b in BLOCKS:
        bid = b["id"]
        lang(f"block.{NS}.{bid}", b["en"], b["fr"])
        if b.get("note_en"):
            lang(f"block.{NS}.{bid}.desc", b["note_en"], b["note_fr"])
        p = pal(b["world"])
        tpath = mk(os.path.join(A, f"textures/block/{bid}.png"))
        paint_block(b["style"], p, bid, tpath)
        if b["kind"] == "station":
            paint_station_top(p, bid + "t", os.path.join(A, f"textures/block/{bid}_top.png"))
            model = {"parent": "minecraft:block/cube_bottom_top",
                     "textures": {"top": f"{NS}:block/{bid}_top", "bottom": f"{NS}:block/painted_wood", "side": f"{NS}:block/{bid}"}}
        elif b["kind"] == "soil":
            paint_block("soil", p, bid + "f", os.path.join(A, f"textures/block/{bid}_tilled.png"))
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{bid}"}}
            w(os.path.join(A, f"models/block/{bid}_tilled.json"),
              {"parent": "minecraft:block/template_cube_bottom_top_indented", "textures": {"bottom": f"{NS}:block/{bid}", "side": f"{NS}:block/{bid}", "top": f"{NS}:block/{bid}_tilled"}})
        elif b["kind"] == "planted_seed":
            model = {"parent": "minecraft:block/cross", "textures": {"cross": f"{NS}:block/planted_seed_cross"}}
            paint_item("seed", p, "seed_block", os.path.join(A, "textures/block/planted_seed_cross.png"))
        elif b["style"] == "glass":
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": {"sprite": f"{NS}:block/{bid}", "force_translucent": True}}}
        else:
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": f"{NS}:block/{bid}"}}
        w(os.path.join(A, f"models/block/{bid}.json"), model)
        if b["kind"] == "soil":
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {"tilled=false": {"model": f"{NS}:block/{bid}"},
                                                                        "tilled=true": {"model": f"{NS}:block/{bid}_tilled"}}})
        elif b["kind"] == "station":
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {"": {"model": f"{NS}:block/{bid}"}}})
        else:
            w(os.path.join(A, f"blockstates/{bid}.json"), {"variants": {"": {"model": f"{NS}:block/{bid}"}}})
        if b["kind"] != "planted_seed":
            w(os.path.join(A, f"items/{bid}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:block/{bid}"}})
        # loot
        drop = ORE_DROPS.get(bid)
        if b["kind"] in ("world_block", "planted_seed", "death_chest", "boss_altar", "sealed_door", "threshold", "lair_heart"):
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
    pick = [f"{NS}:{b['id']}" for b in BLOCKS if b["kind"] in ("terrain", "station", "deco", "sealed_door") and b["style"] not in ("moss", "sand", "wood")]
    shovel = [f"{NS}:{b['id']}" for b in BLOCKS if b["kind"] == "soil" or b["style"] in ("moss", "sand")]
    axe = [f"{NS}:{b['id']}" for b in BLOCKS if b["style"] == "wood"] + [f"{NS}:soul_cradle", f"{NS}:nesting_chest"]
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/pickaxe.json"), {"values": pick})
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/shovel.json"), {"values": shovel})
    w(os.path.join(RES, "data/minecraft/tags/block/mineable/axe.json"), {"values": axe})
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
TEMPLATE = {"overworld": "overworld", "caves": "caves", "ceiling": "nether", "floating": "floating_islands", "amplified": "amplified",
            "ocean": "overworld", "giant": "large_biomes"}

VANILLA_FEATURES = {
    1: ["minecraft:trees_jungle", "minecraft:bamboo_vegetation", "minecraft:patch_grass_jungle", "minecraft:vines", "minecraft:patch_melon"],
    4: ["minecraft:trees_meadow", "minecraft:patch_grass_plain", "minecraft:flower_meadow"],
    6: ["minecraft:trees_cherry", "minecraft:patch_grass_plain"],
    7: ["minecraft:seagrass_deep", "minecraft:kelp_cold", "minecraft:sea_pickle"],
    8: ["minecraft:trees_birch_and_oak_leaf_litter", "minecraft:flower_forest_flowers", "minecraft:patch_grass_forest", "minecraft:patch_pumpkin"],
    9: ["minecraft:patch_dead_bush_badlands"],
    10: ["minecraft:trees_plains", "minecraft:patch_grass_plain"],
}


def gen_worldgen():
    for wd in WORLDS:
        n = wd["n"]
        key = f"world_{n}"
        top, stone, deep = [f"{NS}:{x}" for x in SURF[n]]
        lang(f"world.{NS}.{n}", wd["en"], wd["fr"])
        lang(f"dimension.{NS}.{key}", f"World {n} — {wd['en']}", f"Monde {n} — {wd['fr']}")
        # noise settings from template, with block substitutions
        tpl = TEMPLATE[wd["gen"]]
        txt = open(os.path.join(MC, f"worldgen/noise_settings/{tpl}.json")).read()
        for old, new in (("minecraft:grass_block", top), ("minecraft:deepslate", deep), ("minecraft:stone", stone),
                         ("minecraft:netherrack", stone), ("minecraft:soul_sand", top), ("minecraft:soul_soil", top),
                         ("minecraft:end_stone", stone), ("minecraft:podzol", top), ("minecraft:mycelium", top)):
            txt = txt.replace(f'"{old}"', f'"{new}"')
        ns = json.loads(txt)
        ns["disable_mob_generation"] = False
        if wd["gen"] == "ocean":
            ns["sea_level"] = 150
            txt2 = json.dumps(ns).replace('"minecraft:sand"', f'"{NS}:abyssal_sand"').replace('"minecraft:gravel"', f'"{NS}:abyssal_sand"')
            ns = json.loads(txt2)
        if wd["gen"] == "ceiling":
            ns["default_fluid"] = "minecraft:water" if n == 3 else "minecraft:air"
            ns["sea_level"] = 0
            if n == 5:
                ns["default_fluid"] = "minecraft:air"
        if n == 2:
            ns["default_fluid"] = "minecraft:lava"
            ns["sea_level"] = -40
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
            w(os.path.join(D, "tags/timeline/in_hastened.json"), {"values": ["#minecraft:universal", f"{NS}:hastened_day", f"{NS}:hastened_moon"]})
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
        bio["attributes"]["minecraft:gameplay/natural_mob_spawns"] = {"argument": {"spawn_costs": {}, "spawns_by_category": {k: v for k, v in spawns.items() if v}}} if False else None
        bio["attributes"].pop("minecraft:gameplay/natural_mob_spawns")
        pl = jl("worldgen/biome/plains.json")["attributes"]["minecraft:gameplay/natural_mob_spawns"]
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
        for bid in ores:
            big = bid == "giant_ore_block"
            w(os.path.join(D, f"worldgen/feature/{bid}.json"), {
                "type": "minecraft:ore", "discard_chance_on_air_exposure": 0.0, "size": 24 if big else 9,
                "targets": [{"state": f"{NS}:{bid}", "target": {"predicate_type": "minecraft:block_match", "block": stone}},
                            {"state": f"{NS}:{bid}", "target": {"predicate_type": "minecraft:block_match", "block": deep}}]})
            w(os.path.join(D, f"worldgen/placed_feature/{bid}.json"), {
                "feature": f"{NS}:{bid}", "placement": [{"type": "minecraft:count", "count": 6 if big else 14}, {"type": "minecraft:in_square"},
                                                        {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"above_bottom": 4}, "max_inclusive": {"below_top": 20}}},
                                                        {"type": "minecraft:biome"}]})
            feats[6].append(f"{NS}:{bid}")
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
        bio["features"] = feats
        bio["carvers"] = ["minecraft:cave", "minecraft:canyon"] if not wd["ceiling"] else ["minecraft:nether_cave"]
        bio["has_precipitation"] = n in (1, 4, 8)
        bio["temperature"] = {1: 0.95, 2: 2.0, 4: 0.5, 7: 0.5}.get(n, 0.8)
        bio["downfall"] = 0.9 if n in (1, 4) else 0.3
        w(os.path.join(D, f"worldgen/biome/{key}.json"), bio)
        lang(f"biome.{NS}.{key}", f"World {n}", f"Monde {n}")

        # dimension
        w(os.path.join(D, f"dimension/{key}.json"), {"type": f"{NS}:{key}", "generator": {
            "type": "minecraft:noise", "biome_source": {"type": "minecraft:fixed", "biome": f"{NS}:{key}"}, "settings": f"{NS}:{key}"}})

        # structures
        for i, (sid, en, fr, role, size, rarity, arch) in enumerate(STRUCTURES[n]):
            lang(f"structure.{NS}.{sid}", en, fr)
            w(os.path.join(D, f"worldgen/structure/{sid}.json"), {
                "type": f"{NS}:procedural", "biomes": f"{NS}:{key}", "spawn_overrides": {}, "step": "surface_structures",
                "terrain_adaptation": "beard_thin" if not wd["ceiling"] else "none",
                "world": n, "archetype": arch, "role": role, "size": size, "structure_id": sid})
            spacing = {"common": 18, "rare": 34, "unique": 64}[rarity] + (8 if size == "large" else 0)
            w(os.path.join(D, f"worldgen/structure_set/{sid}.json"), {
                "placement": {"type": "minecraft:random_spread", "salt": 731000 + n * 100 + i, "separation": max(4, spacing // 3), "spacing": spacing},
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
    pl = copy.deepcopy(jl("worldgen/biome/plains.json")["attributes"]["minecraft:gameplay/natural_mob_spawns"])
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
    txt = open(os.path.join(MC, "worldgen/noise_settings/nether.json")).read()
    for old, new in (("minecraft:netherrack", stone), ("minecraft:soul_sand", top), ("minecraft:soul_soil", top),
                     ("minecraft:gravel", top), ("minecraft:basalt", deep), ("minecraft:blackstone", deep),
                     ("minecraft:crimson_nylium", top), ("minecraft:warped_nylium", top),
                     ("minecraft:warped_wart_block", deep), ("minecraft:nether_wart_block", deep), ("minecraft:lava", "minecraft:air")):
        txt = txt.replace(f'"{old}"', f'"{new}"')
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
    dt["ambient_light"] = 0.12
    dt["attributes"]["minecraft:visual/fog_end_distance"] = 56.0
    dt["attributes"]["minecraft:visual/fog_start_distance"] = 6.0
    dt["attributes"]["minecraft:visual/ambient_light_color"] = "#3a1a10"
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
    pl = copy.deepcopy(bio["attributes"]["minecraft:gameplay/natural_mob_spawns"])
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
    L.append("\tpublic static final List<Defs.WorldDef> WORLDS = List.of(")
    L.append(",\n".join(f"\t\tnew Defs.WorldDef({wd['n']}, {jstr(wd['rule'])}, {jstr(wd['tier'])}, 0x{wd['pal'][0]}, 0x{wd['pal'][2]}, {str(wd['ceiling']).lower()})" for wd in WORLDS))
    L.append("\t);")
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
    expand_items()
    gen_items()
    gen_blocks()
    gen_entities()
    gen_worldgen()
    gen_world_zero()
    gen_advancements()
    gen_endings_tab()
    gen_lang_misc()
    gen_lang_story()
    gen_java()
    # merge hand-written lang (ui strings)
    for code, table in (("en_us", EN), ("fr_fr", FR)):
        extra = os.path.join(ROOT, f"tools/lang/{code}.json")
        if os.path.exists(extra):
            table.update(json.load(open(extra, encoding="utf-8")))
        w(os.path.join(A, f"lang/{code}.json"), dict(sorted(table.items())))
    print(f"items={len(ALL_ITEMS)} blocks={len(BLOCKS)} mobs={len(MOBS)} bosses={len(BOSSES)} "
          f"structures={sum(len(v) for v in STRUCTURES.values())} quests={len(QUESTS)} achievements={sum(len(v) for v in ACH.values())} lang={len(EN)}")


if __name__ == "__main__":
    main()
