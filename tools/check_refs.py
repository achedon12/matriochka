"""Checks, without starting the game, that every matriochka:<id> named in the data points at something that exists.

For each Minecraft version the mod is built for, the data the jar would hold is laid out (src/main/resources, then
versions/<mc>/main/resources over it) and every reference to the mod's own world generation, blocks, biomes,
structures, loot tables and advancements is resolved by what the key holding it expects:

  "noise": "matriochka:x"            worldgen/noise/x.json
  a density argument                 worldgen/density_function/x.json
  "feature": "matriochka:x"          worldgen/feature/x.json (26.2: worldgen/configured_feature)
  a biome's "features" lists         worldgen/placed_feature/x.json
  "biomes", "biome"                  worldgen/biome/x.json
  "Name", "block", "default_block"   assets/matriochka/blockstates/x.json
  "structure" (in a structure set)   worldgen/structure/x.json
  "parent" (in an advancement)       advancement/x.json

A noise named like a block (26.2 has minecraft:netherrack and minecraft:gravel noises) once made a block swap turn a
noise reference into a block id; this is the check that would have caught it.

  python3 tools/check_refs.py        exits 1 and lists every broken reference
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "matriochka"
DENSITY_KEYS = {"argument", "argument1", "argument2", "input", "left", "right", "function", "final_density", "depth",
                "surface_level", "preliminary_surface_level", "initial_density_without_jaggedness", "erosion",
                "continents", "ridges", "temperature", "vegetation", "barrier", "fluid_level_floodedness",
                "fluid_level_spread", "lava", "vein_toggle", "vein_ridged", "vein_gap", "when_in_range", "when_out_of_range",
                "shift_x", "shift_y", "shift_z", "offset", "factor", "jaggedness"}
BLOCK_KEYS = {"Name", "block", "default_block", "default_fluid"}


def versions():
    out = ["26.3"]
    vdir = os.path.join(ROOT, "versions")
    if os.path.isdir(vdir):
        out += sorted(v for v in os.listdir(vdir) if v != "26.3" and os.path.isdir(os.path.join(vdir, v)))
    return out


def tree(mc):
    """{relative path: absolute path} of the resources a jar for this version holds."""
    files = {}
    roots = [os.path.join(ROOT, "src/main/resources")]
    over = os.path.join(ROOT, "versions", mc, "main/resources")
    if os.path.isdir(over):
        roots.append(over)
    for r in roots:
        for d, _, fs in os.walk(r):
            for f in fs:
                p = os.path.join(d, f)
                files[os.path.relpath(p, r)] = p
    return files


def check(mc):
    files = tree(mc)
    feature_dir = "feature" if mc == "26.3" else "configured_feature"
    have = lambda rel: rel in files
    errs = []

    def resolve(kind, ident, where):
        if not isinstance(ident, str) or not ident.startswith(NS + ":"):
            return
        name = ident.split(":", 1)[1]
        wanted = {
            "noise": [f"data/{NS}/worldgen/noise/{name}.json"],
            "density": [f"data/{NS}/worldgen/density_function/{name}.json"],
            "feature": [f"data/{NS}/worldgen/{feature_dir}/{name}.json"],
            "placed": [f"data/{NS}/worldgen/placed_feature/{name}.json"],
            "biome": [f"data/{NS}/worldgen/biome/{name}.json"],
            "block": [f"assets/{NS}/blockstates/{name}.json"],
            "structure": [f"data/{NS}/worldgen/structure/{name}.json"],
            "advancement": [f"data/{NS}/advancement/{name}.json"],
        }[kind]
        if not any(have(w) for w in wanted):
            errs.append(f"{mc}: {where}: {kind} {ident} does not exist")

    def walk(o, where, parent=None, section=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    if k == "noise":
                        resolve("noise", v, where)
                    elif k in DENSITY_KEYS and section in ("noise_settings", "density_function"):
                        resolve("density", v, where)
                    elif k == "feature" and section == "placed_feature":
                        resolve("feature", v, where)
                    elif k in ("biome", "biomes") and section != "biome":
                        resolve("biome", v, where)
                    elif k in BLOCK_KEYS:
                        resolve("block", v, where)
                    elif k == "structure" and section == "structure_set":
                        resolve("structure", v, where)
                    elif k == "parent" and section == "advancement":
                        resolve("advancement", v, where)
                elif k == "features" and section == "biome" and isinstance(v, list):
                    for step in v:
                        for pf in step if isinstance(step, list) else [step]:
                            resolve("placed", pf, where)
                elif k in ("biomes",) and isinstance(v, list):
                    for b in v:
                        resolve("biome", b, where)
                else:
                    walk(v, where, k, section)
        elif isinstance(o, list):
            for x in o:
                walk(x, where, parent, section)

    for rel, path in sorted(files.items()):
        if not rel.endswith(".json") or not rel.startswith(f"data/{NS}/"):
            continue
        parts = rel.split("/")
        section = parts[3] if parts[2] == "worldgen" and len(parts) > 3 else parts[2]
        if mc != "26.3" and parts[2] == "worldgen" and section == "feature":
            continue  # 26.2 reads configured_feature; the 26.3 folder is left in the jar unread
        try:
            data = json.load(open(path))
        except ValueError as e:
            errs.append(f"{mc}: {rel}: not JSON ({e})")
            continue
        walk(data, rel, None, section)
    return errs


def main():
    errs = []
    for mc in versions():
        errs += check(mc)
    for e in errs:
        print(e)
    print(f"{len(errs)} broken reference(s) in {', '.join(versions())}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
