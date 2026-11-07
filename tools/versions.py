"""The data that differs between the Minecraft versions the mod is built for.

For every version other than the default (26.3), gen.py writes the world generation in that version's formats, from
that version's vanilla templates (tools/vanilla_<mc>/), into a scratch folder; every file that differs from the
default's (src/main/resources) is kept in versions/<mc>/main/resources, which Gradle lays over src/main/resources
when building with -Pmc=<mc>.

  python3 tools/versions.py          after tools/gen.py
"""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSIONS = ["26.2", "26.1.2"]


SILK = {"condition": "minecraft:match_tool",
        "predicate": {"predicates": {"minecraft:enchantments": [{"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}


def older_conditions(o, parent=None):
    """Advancements and loot tables in 26.2's form: an entity predicate is a list of conditions keyed "condition"
    (26.3: one object keyed "type"), and the named condition minecraft:tool/can_silk_touch is spelled out."""
    if isinstance(o, list):
        return [older_conditions(x, parent) for x in o]
    if not isinstance(o, dict):
        return o
    c = {k: older_conditions(v, k) for k, v in o.items()}
    if c.get("condition") == "minecraft:tool/can_silk_touch":
        c.pop("condition")
        c["conditions"] = c.get("conditions", []) + [SILK]
    if parent in ("entity", "player", "killing_blow") and isinstance(c.get("type"), str):
        cond = dict(c)
        cond["condition"] = cond.pop("type")
        return [cond]
    return c


def convert_tree(main_res, out, folder):
    """Writes the 26.2 form of every file of data/matriochka/<folder> that differs from 26.3's."""
    import json
    kept = 0
    base = os.path.join(main_res, "data/matriochka", folder)
    for dp, _, files in os.walk(base):
        for f in files:
            if not f.endswith(".json"):
                continue
            src = os.path.join(dp, f)
            obj = json.load(open(src, encoding="utf-8"))
            new = older_conditions(obj)
            if new == obj:
                continue
            dst = os.path.join(out, os.path.relpath(src, main_res))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "w", encoding="utf-8") as fh:
                json.dump(new, fh, indent=2, ensure_ascii=False)
            kept += 1
    return kept


def main():
    main_res = os.path.join(ROOT, "src/main/resources")
    for mc in VERSIONS:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, MATRIO_MC=mc, MATRIO_RES=tmp)
            subprocess.run([sys.executable, os.path.join(ROOT, "tools/gen.py")], env=env, check=True, stdout=subprocess.DEVNULL)
            out = os.path.join(ROOT, "versions", mc, "main/resources")
            shutil.rmtree(os.path.join(out, "data"), ignore_errors=True)
            kept = 0
            for dp, _, files in os.walk(os.path.join(tmp, "data")):
                for f in files:
                    src = os.path.join(dp, f)
                    rel = os.path.relpath(src, tmp)
                    ref = os.path.join(main_res, rel)
                    if os.path.exists(ref) and filecmp.cmp(src, ref, shallow=False):
                        continue
                    dst = os.path.join(out, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(src, dst)
                    kept += 1
            for folder in ("advancement", "loot_table"):
                kept += convert_tree(main_res, out, folder)
            print(mc, kept, "files differ")


if __name__ == "__main__":
    main()
