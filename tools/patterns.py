"""The Matrix Workbench's crafting patterns: every recipe made there laid out on its 3 x 3 grid.

The costs stay exactly those of content/Recipes.java and content/ReplayContent.java: each ingredient fills a
symmetric group of cells (the centre, the four edges, the four corners, a row, a column, the ring...) with the same
count in each cell, so the cells always add up to the recipe's count. The rarest ingredient (a core, a single piece)
takes the centre.

Written to data/matriochka/workbench_patterns.json, {output id: [9 cells, row by row, each [item id, count] or
null]}; the game (block/WorkbenchPatterns.java) and the site (tools/site.py) both read that file, so the grid in the
game and the one on the site are always the same.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JAVA = os.path.join(ROOT, "src/main/java/fr/achedon12/matriochka/content")
OUT = os.path.join(ROOT, "src/main/resources/data/matriochka/workbench_patterns.json")

CENTRE = (4,)
# groups of cells by size, the most pleasing first; each is symmetric about the vertical axis
GROUPS = {
    9: [(0, 1, 2, 3, 4, 5, 6, 7, 8)],
    8: [(0, 1, 2, 3, 5, 6, 7, 8)],
    6: [(0, 1, 2, 6, 7, 8), (0, 3, 6, 2, 5, 8)],
    5: [(1, 3, 4, 5, 7), (0, 2, 4, 6, 8)],
    4: [(0, 2, 6, 8), (1, 3, 5, 7)],
    3: [(3, 4, 5), (1, 4, 7), (6, 7, 8), (0, 1, 2)],
    2: [(3, 5), (1, 7), (0, 2), (6, 8)],
    1: [(4,), (1,), (7,), (3,), (5,)],
}


def workbench_recipes():
    """[(output, count, [(ingredient id, count)])] of every recipe made at the Matrix Workbench."""
    out = []
    src = open(os.path.join(JAVA, "Recipes.java")).read()
    for m in re.finditer(r'\br\(W,\s*"([a-z0-9_:]+)",\s*(\d+),\s*-?\d+,\s*([^;]*?)\);', src):
        args = re.findall(r'"([a-z0-9_:]+)",\s*(\d+)', m.group(3))
        out.append((m.group(1), int(m.group(2)), [(a, int(b)) for a, b in args]))
    # the ten World Soils come from a loop: four dirt and a bone meal (Surface) or spores
    for i in range(10):
        out.append((f"world_soil_{i}", 4, [("minecraft:dirt", 4), ("minecraft:bone_meal" if i == 0 else "spores", 1)]))
    rep = open(os.path.join(JAVA, "ReplayContent.java")).read()
    for m in re.finditer(r'new GearRecipe\("matrix_workbench",\s*"([a-z0-9_]+)",\s*-?\d+,\s*List\.of\(([^)]*)\),\s*List\.of\(([^)]*)\)\)', rep):
        ids = re.findall(r'"([a-z0-9_:]+)"', m.group(2))
        counts = [int(x) for x in re.findall(r"\d+", m.group(3))]
        out.append((m.group(1), 1, list(zip(ids, counts))))
    return out


def pattern(inputs):
    """Nine cells for a list of (ingredient, count): each ingredient on a symmetric group whose size divides its count."""
    cells = [None] * 9
    free = set(range(9))
    # the rarest first (fewest items), so a core or a single piece lands in the centre
    order = sorted(range(len(inputs)), key=lambda i: (inputs[i][1], i))
    for k, i in enumerate(order):
        iid, n = inputs[i]
        placed = False
        left = len(inputs) - k - 1  # ingredients still to place after this one: leave each at least one cell
        for size in (9, 8, 6, 5, 4, 3, 2, 1):
            if size > len(free) - left or n % size or n // size > 64:
                continue
            for g in GROUPS[size]:
                if all(c in free for c in g):
                    for c in g:
                        cells[c] = [iid, n // size]
                        free.discard(c)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            # no symmetric group divides the count: one cell holds it all
            c = min(free, key=lambda x: (x != 4, abs(x % 3 - 1) + abs(x // 3 - 1), x))
            cells[c] = [iid, n]
            free.discard(c)
    return cells


def build():
    pats = {}
    for out, _count, inputs in workbench_recipes():
        pats[out] = pattern(inputs)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(pats, f, indent=1, sort_keys=True)
        f.write("\n")
    return pats


if __name__ == "__main__":
    p = build()
    print(f"workbench patterns: {len(p)}")
