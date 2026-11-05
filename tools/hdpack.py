#!/usr/bin/env python3
"""Builds the optional "Matriochka HD" resource pack: the same hand-crafted textures (tools/craft.py and
tools/particles.py) painted at twice the size, 32 x 32 for items and blocks and 16 x 16 for particles.

    python3 tools/hdpack.py [output.zip]     default: build/matriochka-hd-<mod_version>.zip

The zip is deterministic (sorted entries, fixed timestamps), so rebuilding it gives the same bytes.
"""
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import craft  # noqa: E402
import gen  # noqa: E402
import particles  # noqa: E402
from content import BLOCKS  # noqa: E402

ROOT = gen.ROOT
PACK_FORMAT = 97  # resource pack format of Minecraft 26.3 (version.json, pack_version.resource_major)
TEX = "assets/matriochka/textures/"


def version():
    for line in open(os.path.join(ROOT, "gradle.properties"), encoding="utf-8"):
        if line.startswith("mod_version="):
            return line.split("=", 1)[1].strip()
    return "dev"


def png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=False)
    return buf.getvalue()


def files():
    """{path in the zip: bytes} of the whole pack."""
    out = {}
    if not gen.ALL_ITEMS:
        gen.expand_items()
    for it in gen.ALL_ITEMS:
        spr = craft.crafted_item(it, 32)
        if spr is not None:
            out[TEX + f"item/{it['id']}.png"] = png(spr.image())
    for b in BLOCKS:
        faces = craft.crafted_block(b["id"], 32)
        for suffix, spr in (faces or {}).items():
            out[TEX + f"block/{b['id']}{suffix}.png"] = png(spr.image())
            if spr.glow:
                out[TEX + f"block/{b['id']}{suffix}_glow.png"] = png(spr.glow_image())
    for pid, row in particles.PARTICLES.items():
        for i in range(row[0]):
            out[TEX + f"particle/{pid}_{i}.png"] = png(particles.paint(pid, i, 16).image())
    out["pack.png"] = png(craft.it_whole_matryoshka(64).image())
    meta = {"pack": {"description": "Matriochka HD: the hand-painted dolls, cores, Seeds, gear and stations at 32 x 32",
                     "min_format": PACK_FORMAT, "max_format": PACK_FORMAT}}
    out["pack.mcmeta"] = (json.dumps(meta, indent=2) + "\n").encode()
    lic = os.path.join(ROOT, "LICENSE")
    if os.path.exists(lic):
        out["LICENSE"] = open(lic, "rb").read()
    return out


def build(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = files()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(data):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data[name])
    return len(data)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", f"matriochka-hd-{version()}.zip")
    n = build(target)
    print(f"{target}: {n} files")
