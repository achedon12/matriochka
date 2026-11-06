"""Matriochka's own particles: the table, their pixel art and the generated registration.

Each particle has a few 8 x 8 frames painted with the craft painter (16 x 16 in the HD pack) and a behaviour read by
the client particle (client/MatrioParticle.java): gravity (negative rises), friction, lifetime, size, whether it
glows (full brightness), spin, sideways sway and opacity. Attacks name them as "matriochka:<id>" (tools/attacks.py),
biomes use them as ambient particles (gen.py, ATMOSPHERE) and the bosses spray them in their attacks (MatrioBoss).
"""
import json
import math
import os

from craft import GOLD, IRON, PAPER, RED, Spr, hramp, hx, n_flat, n_sphere

# id: (frames, gravity, friction, life min, life max, size, glow, spin, sway, alpha, description)
PARTICLES = {
    "spore": (3, -0.004, 0.96, 70, 110, 0.10, False, 0.0, 0.012, 0.9, "World 1: a drifting puff of toxic spores"),
    "ember": (2, 0.006, 0.97, 40, 80, 0.07, True, 0.0, 0.006, 1.0, "World 2: an ember falling from the heat"),
    "cold_dust": (2, 0.003, 0.97, 90, 150, 0.06, False, 0.0, 0.004, 0.75, "World 3: cold dust settling in the halls"),
    "chain_glint": (3, 0.0, 0.9, 10, 18, 0.12, True, 0.0, 0.0, 1.0, "World 3: the glint of a chain or a key"),
    "storm_spark": (2, 0.0, 0.82, 5, 11, 0.12, True, 0.4, 0.0, 1.0, "World 4: a lightning spark"),
    "shadow_wisp": (3, -0.008, 0.94, 40, 70, 0.16, False, 0.05, 0.01, 0.8, "World 5: a wisp of shadow"),
    "deep_mote": (2, -0.001, 0.98, 100, 160, 0.06, True, 0.0, 0.006, 0.85, "World 5: a rare mote of light in the deep"),
    "mirror_shard": (3, -0.006, 0.97, 50, 90, 0.09, True, 0.12, 0.004, 1.0, "World 6: a mirror shard falling upward"),
    "bubble": (2, -0.03, 0.9, 40, 80, 0.08, False, 0.0, 0.01, 0.9, "World 7: a pressure bubble"),
    "petal": (2, 0.005, 0.96, 80, 130, 0.08, False, 0.15, 0.03, 1.0, "World 8, spring: a blossom petal"),
    "pollen": (2, -0.001, 0.97, 80, 130, 0.05, True, 0.0, 0.01, 0.9, "World 8, summer: pollen in the warm air"),
    "autumn_leaf": (2, 0.007, 0.96, 80, 130, 0.09, False, 0.18, 0.035, 1.0, "World 8, autumn: a falling leaf"),
    "snowflake": (2, 0.006, 0.97, 90, 140, 0.07, False, 0.06, 0.02, 1.0, "World 8, winter: a snowflake"),
    "grit": (2, 0.05, 0.98, 20, 40, 0.06, False, 0.3, 0.0, 1.0, "World 9: grit knocked off the moving rock"),
    "rust_mote": (2, 0.0015, 0.98, 100, 160, 0.06, False, 0.0, 0.008, 0.7, "World 9: rust-red dust hanging in the air"),
    "thread_scrap": (3, 0.004, 0.96, 60, 110, 0.09, False, 0.2, 0.03, 1.0, "World 10: a scrap of thread or cloth"),
    "fluff": (2, -0.0015, 0.985, 140, 220, 0.08, False, 0.03, 0.012, 0.95, "World 10: floating wool fluff in the workshop light"),
    "gold_mote": (2, -0.001, 0.97, 60, 100, 0.06, True, 0.0, 0.008, 1.0, "World 0 and the Surface: gold leaf dust"),
}


def _soft(s, cx, cy, r, ramp, a_out=150):
    core = s.disc(cx, cy, r)
    s.shade(core, ramp, n_sphere(cx - r * 0.3, cy - r * 0.3, r * 1.2), rim=False, lo=1, hi=len(ramp) - 1)
    halo = s.disc(cx, cy, r + 1.6) - core
    s.fill(halo, ramp[1], a=a_out)


def _rows(s, rows, cols):
    """An 8 x 8 pixel motif (2 units per pixel), so it stays crisp at 8 and doubles cleanly at 16."""
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch in cols:
                s.dot(i * 2, j * 2, cols[ch], size=2)


def paint(pid, frame, res=8):
    """Frame `frame` of particle `pid`, `res` pixels wide (8 for the mod, 16 for the HD pack)."""
    s = Spr(res)
    f = frame
    if pid == "spore":
        _soft(s, 8, 8, 2.2 + f * 1.4, hramp("b7e04a", n=5), 120 - f * 30)
        s.dot(6.0, 6.0, hramp("7c4a9c")[3])
    elif pid == "ember":
        g = hramp("ff9a3a", n=5, dl=0.09)
        _soft(s, 8, 8, 2.6 - f * 0.8, g, 160)
        s.dot(7.0, 7.0, (255, 240, 200))
    elif pid == "cold_dust":
        # big enough to read as a mote (two pixels across at 8 x 8), not a stray pixel
        _soft(s, 8, 8, 3.0 - f * 0.8, hramp("aab8c8", n=5), 110)
    elif pid == "chain_glint":
        rows = ([".......", "...#...", "..#o#..", "...#..."], ["...#...", "...#...", ".##o##.", "...#...", "...#..."],
                ["........", "...#....", "..#o#...", "...#...."])[f]
        _rows(s, rows if f != 1 else rows, {"#": hramp("7fd3ff")[3], "o": (235, 245, 255)})
    elif pid == "storm_spark":
        pts = [(3, 1), (9, 6), (6, 8), (13, 14)] if f == 0 else [(12, 1), (6, 7), (10, 9), (3, 15)]
        s.fill(s.path(pts, 1.3), hramp("ffe14a")[3])
        s.fill(s.path(pts, 0.6), (255, 255, 230))
    elif pid == "shadow_wisp":
        d = hramp("2a2244", n=5, dl=0.08)
        for i, (x, y, r) in enumerate(((6, 10, 4.0), (10, 6, 3.0), (8, 3, 2.0))):
            if i <= 2 - f or i == 0:
                s.fill(s.disc(x + f, y, r - f * 0.6), d[2 - min(i, 2)], a=200 - f * 50)
    elif pid == "deep_mote":
        _soft(s, 8, 8, 2.8 - f * 0.7, hramp("6a8aff", n=5), 110)
    elif pid == "mirror_shard":
        tris = ([(3, 13), (13, 9), (7, 2)], [(4, 4), (13, 6), (6, 14)], [(2, 8), (12, 3), (11, 14)])[f]
        m = s.poly(tris)
        s.shade(m, hramp("e8c8f4"), n_flat(-0.3, -0.4), rim=hramp("4ac8c0")[1], lo=2, hi=5)
        s.outline()
    elif pid == "bubble":
        # radii picked to land on whole pixels at 8 x 8 (a 4.6 ring broke up into four corner dots)
        r, w = ((6.0, 1.8), (3.4, 1.4))[f]
        s.fill(s.ring(8, 8, r - w, r), hramp("9af0ff")[4], a=230)
        s.fill(s.disc(8, 8, r - w), hramp("9af0ff")[2], a=60)
        s.dot(5.6, 5.4, (255, 255, 255))
    elif pid == "petal":
        m = s.ell(8, 8, 4.6, 2.8) if f == 0 else s.ell(8, 8, 2.8, 4.4)
        s.shade(m, hramp("f0b4c8", sat=0.12), n_sphere(7, 7, 5), lo=2, hi=5)
        s.outline()
    elif pid == "pollen":
        _soft(s, 8, 8, 2.6 - f * 0.6, hramp("ffe070", n=5), 100)
    elif pid == "autumn_leaf":
        m = s.poly([(2, 12), (6, 4), (13, 2), (12, 9), (5, 13)]) if f == 0 else s.poly([(3, 3), (11, 4), (14, 12), (6, 13), (2, 8)])
        s.shade(m, hramp("d8602a"), n_flat(-0.3, -0.3), lo=2, hi=4)
        s.fill(s.path([(3, 12), (11, 4)] if f == 0 else [(3, 4), (12, 12)], 0.5), hramp("d8602a")[1])
        s.outline()
    elif pid == "snowflake":
        rows = (["..#.#...", "...#....", "#.###.#.", ".##o##..", "#.###.#.", "...#....", "..#.#..."],
                ["........", "...#....", "..###...", ".##o##..", "..###...", "...#....", "........"])[f]
        _rows(s, rows, {"#": (236, 246, 255), "o": (190, 214, 240)})
    elif pid == "grit":
        m = s.poly([(4, 6), (9, 3), (12, 8), (8, 12)]) if f == 0 else s.poly([(5, 4), (12, 5), (10, 11), (4, 10)])
        s.shade(m, hramp("7a5040"), n_flat(-0.3, -0.3), lo=2, hi=4)
        s.outline()
    elif pid == "rust_mote":
        _soft(s, 8, 8, 3.0 - f * 0.8, hramp("b85a3e", n=5), 120)
    elif pid == "thread_scrap":
        col = (RED, hramp("3a6ab8"), GOLD)[f]
        m = s.path([(2, 11), (6, 6), (10, 9), (14, 4)], 1.1)
        s.shade(m, col, n_flat(-0.3, -0.3), lo=2, hi=4)
        s.outline()
    elif pid == "fluff":
        p = PAPER
        for (x, y, r) in ((7, 8, 3.2), (10, 7, 2.4), (8, 5, 2.2)) if f == 0 else ((8, 8, 3.0), (5, 7, 2.2), (10, 10, 2.0)):
            s.fill(s.disc(x, y, r), p[5], a=220)
        s.fill(s.disc(7, 7, 1.4), (255, 255, 255))
    elif pid == "gold_mote":
        _soft(s, 8, 8, 1.8 + f * 0.4, GOLD, 120)
        s.dot(7.0, 7.0, GOLD[5])
    return s


def textures(pid):
    return [f"{pid}_{i}" for i in range(PARTICLES[pid][0])]


def gen(assets, java_path, res=8):
    """Writes the frames, the particle definitions and the generated Java registration."""
    os.makedirs(os.path.join(assets, "textures/particle"), exist_ok=True)
    os.makedirs(os.path.join(assets, "particles"), exist_ok=True)
    for pid, row in PARTICLES.items():
        for i in range(row[0]):
            paint(pid, i, res).image().save(os.path.join(assets, f"textures/particle/{pid}_{i}.png"))
        with open(os.path.join(assets, f"particles/{pid}.json"), "w", encoding="utf-8") as fh:
            json.dump({"textures": [f"matriochka:{t}" for t in textures(pid)]}, fh, indent=2)
    if java_path is None:
        return
    L = ["package fr.achedon12.matriochka.content;", "",
         "import fr.achedon12.matriochka.Matriochka;",
         "import java.util.LinkedHashMap;",
         "import java.util.Map;",
         "import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;",
         "import net.minecraft.core.Registry;",
         "import net.minecraft.core.particles.SimpleParticleType;",
         "import net.minecraft.core.registries.BuiltInRegistries;", "",
         "/** GENERATED by tools/gen.py from tools/particles.py. Do not edit by hand. */",
         "public final class Particles {",
         "\tprivate Particles() {}", "",
         "\t/** How a particle moves and shows: read by the client particle. */",
         "\tpublic record Style(int frames, float gravity, float friction, int lifeMin, int lifeMax, float size, boolean glow, float spin, float sway, float alpha) {}", "",
         "\tpublic static final Map<SimpleParticleType, Style> STYLES = new LinkedHashMap<>();", ""]
    for pid, (fr, g, fric, l0, l1, size, glow, spin, sway, alpha, desc) in PARTICLES.items():
        L.append(f"\t/** {desc}. */")
        L.append(f"\tpublic static final SimpleParticleType {pid.upper()} = register(\"{pid}\", new Style({fr}, {g}f, {fric}f, {l0}, {l1}, {size}f, {str(glow).lower()}, {spin}f, {sway}f, {alpha}f));")
    L += ["", "\tprivate static SimpleParticleType register(String id, Style style) {",
          "\t\tSimpleParticleType type = Registry.register(BuiltInRegistries.PARTICLE_TYPE, Matriochka.id(id), FabricParticleTypes.simple(false));",
          "\t\tSTYLES.put(type, style);",
          "\t\treturn type;",
          "\t}", "",
          "\tpublic static void init() {",
          "\t\t// the fields above register the particle types when the class loads",
          "\t}",
          "}"]
    with open(java_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def preview(res=8):
    out = []
    for pid, row in PARTICLES.items():
        for i in range(row[0]):
            out.append(paint(pid, i, res))
    return out
