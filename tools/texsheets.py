#!/usr/bin/env python3
"""Preview sheets of the hand-crafted textures, upscaled, with a vanilla item for scale when the Minecraft client jar
is in the Gradle cache. Written to docs-wiki-drafts/textures/ for the wiki and for reviewing the art.

    python3 tools/texsheets.py
"""
import glob
import io
import os
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import craft  # noqa: E402
import particles  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs-wiki-drafts/textures")


def vanilla(names, res):
    """Vanilla item textures from the client jar, if it can be found, upscaled to res."""
    jars = sorted(glob.glob(os.path.expanduser("~/.gradle/caches/fabric-loom/minecraftMaven/net/minecraft/minecraft-clientonly-*/26.3/*.jar")))
    jars += sorted(glob.glob(os.path.join(ROOT, "..", "*", ".gradle/loom-cache/minecraftMaven/net/minecraft/minecraft-clientOnly-*/26.3/*-26.3.jar")))
    jars += sorted(glob.glob(os.path.join(ROOT, ".gradle/loom-cache/minecraftMaven/net/minecraft/minecraft-clientOnly-*/26.3/*-26.3.jar")))
    out = []
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as z:
                for n in names:
                    data = z.read(f"assets/minecraft/textures/item/{n}.png")
                    out.append(Image.open(io.BytesIO(data)).convert("RGBA").crop((0, 0, 16, 16)).resize((res, res), Image.NEAREST))
            return out
        except (KeyError, zipfile.BadZipFile, OSError):
            out = []
    return out


GEAR = (("sporite_sword", 1), ("ash_hammer", 2), ("jailer_blade", 3), ("lightning_lance", 4), ("shadow_blade", 5),
        ("mirror_blade", 6), ("trench_trident", 7), ("season_scythe", 8), ("seismic_mace", 9), ("artisan_blade", 10))


def sheets(res):
    return {
        "dolls": (craft.prev_dolls(res), 8, ["totem_of_undying"]),
        "cores": ([craft.it_core(res, w) for w in range(0, 11)], 11, ["heart_of_the_sea"]),
        "seeds": ([craft.it_seed(res, w) for w in range(1, 11)], 10, ["wheat_seeds"]),
        "writings_offerings": ([craft.it_scroll(res), craft.it_scroll(res, True), craft.it_journal(res), craft.it_page(res),
                                craft.it_shackle(res), craft.it_censer(res), craft.it_wreath(res), craft.it_effigy(res)], 8, ["writable_book"]),
        "snorkels": ([craft.it_snorkel(res, k) for k in craft.SNORKEL_STYLE], 4, ["turtle_helmet"]),
        "armor": ([craft.it_armor(res, s, p) for s in craft.ARMOR_STYLE for p in ("helmet", "chestplate", "leggings", "boots")], 8, ["iron_chestplate"]),
        "weapons": ([craft.it_weapon(res, i, w) for i, w in GEAR], 10, ["diamond_sword"]),
        "soils": ([craft.bl_soil(res, w) for w in range(10)] + [craft.bl_soil(res, w, True) for w in range(10)], 10, []),
        "blocks": ([craft.bl_world_block(res), craft.bl_threshold(res)], 2, []),
        "stations": ([craft.bl_station(res, s, f) for s in craft.STATION_WORLD for f in ("side", "top", "bottom")], 6, []),
    }


def main():
    os.makedirs(OUT, exist_ok=True)
    for res, scale in ((16, 8), (32, 4)):
        for name, (sprites, cols, ref) in sheets(res).items():
            craft.sheet(sprites, scale=scale, cols=cols + (1 if ref else 0), extra=vanilla(ref, res)).save(os.path.join(OUT, f"{name}_{res}.png"))
    craft.sheet(particles.preview(8), scale=12, cols=12).save(os.path.join(OUT, "particles_8.png"))
    craft.sheet(particles.preview(16), scale=6, cols=12).save(os.path.join(OUT, "particles_16.png"))
    print(f"sheets in {OUT}")


if __name__ == "__main__":
    main()
