"""Pixel icons for the item tooltips' strip (client/ItemTip.java), drawn texel by texel on a 9 x 9 grid.

  tip_gem_<rarity>  a cut gem in the rarity's colour (common, rare, epic, legendary)
  tip_soul          a soul wisp
The world chip uses the world's rule icon (rule_<rule>), drawn for the HUD.
"""

GEM = [
    "..XXXXX..",
    ".XaabbbX.",
    "XaabbbccX",
    "XbbbccccX",
    ".XbccccX.",
    "..XcccX..",
    "...XcX...",
    "....X....",
    ".........",
]
SOUL = [
    "....X....",
    "...XaX...",
    "..XabX...",
    "..XabbX..",
    ".XabbbcX.",
    ".XbbbccX.",
    ".XbXcXcX.",
    "..X.X.X..",
    ".........",
]
RARITY = {
    "common": ((250, 250, 250), (200, 200, 206), (140, 140, 150)),
    "rare": ((210, 250, 255), (90, 210, 240), (30, 120, 170)),
    "epic": ((250, 210, 255), (210, 110, 240), (120, 40, 160)),
    "legendary": ((255, 246, 190), (250, 196, 60), (170, 100, 20)),
}
SOUL_C = ((236, 250, 255), (150, 220, 240), (70, 140, 180))
EDGE = (20, 11, 8)


def _draw(grid, cols):
    cv = Cv(9 * S, 9 * S)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            c = EDGE if ch == "X" else cols["abc".index(ch)] if ch in "abc" else None
            if c:
                cv.rect(x * S, y * S, (x + 1) * S, (y + 1) * S, c)
    return cv


def build(ns):
    globals().update({k: v for k, v in ns.items() if not k.startswith("__") and k not in globals()})
    for r, cols in RARITY.items():
        save("tip_gem_" + r, _draw(GEM, cols))
    save("tip_soul", _draw(SOUL, SOUL_C))
