"""Hand-drawn pixel art for the replay gear and the trophy dolls.

Every sprite is a 16 x 16 grid typed by hand: one character per pixel, "." for transparent, every other letter a
colour of the sprite's palette. The bow also has its three drawing frames, made from the idle limb with the string
pulled back and an arrow nocked.
"""
from PIL import Image


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _save(grid, colors, path):
    assert len(grid) == 16 and all(len(r) == 16 for r in grid), path
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != ".":
                c = colors[ch]
                img.putpixel((x, y), (c[0], c[1], c[2], 255))
    img.save(path)


# ------------------------------------------------------------------ the spore bow (World 1)
BOW = [
    "................",
    "...........oSSo.",
    "........oowwsSSo",
    "......oowwWWWso.",
    ".....owwWoo..t..",
    "....owWo....t...",
    "...owWo....t....",
    "...ocCo...t.....",
    "..ocCo...t......",
    "..ocCo..t.......",
    "..owWo.t........",
    ".owWo.t.........",
    ".owWot..........",
    ".sSwo...........",
    ".sSSo...........",
    "..oo............",
]
BOW_COLORS = {"o": hx("2a1a0e"), "w": hx("6a4424"), "W": hx("9a6a3a"), "s": hx("6b3f8a"), "S": hx("a878c8"),
              "c": hx("3f6b2a"), "C": hx("6a9a3a"), "t": hx("b7e04a"), "a": hx("8a6a4a"), "h": hx("c8a0e8"), "f": hx("e8f0d8")}
# where the string is drawn back to in each frame, and how long the nocked arrow is
BOW_PULL = [((10, 9), 7), ((11, 10), 8), ((12, 11), 9)]


def _line(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]


def _bow_frame(apex, length):
    g = [list(r.replace("t", ".")) for r in BOW]
    for (x, y) in _line(13, 4, apex[0], apex[1]) + _line(apex[0], apex[1], 5, 12):
        if g[y][x] == ".":
            g[y][x] = "t"
    # the arrow lies along the diagonal toward the top left: fletching at the string, a spore pod for a head
    ax, ay = apex
    for i in range(1, length):
        x, y = ax - i, ay - i
        if 0 <= x < 16 and 0 <= y < 16:
            g[y][x] = "f" if i <= 2 else "a"
    hx_, hy = ax - length, ay - length
    for (x, y, c) in ((hx_, hy, "s"), (hx_ - 1, hy, "h"), (hx_, hy - 1, "h"), (hx_ - 1, hy - 1, "S")):
        if 0 <= x < 16 and 0 <= y < 16:
            g[y][x] = c
    return ["".join(r) for r in g]


# ------------------------------------------------------------------ the magma flail (World 2)
FLAIL = [
    "...........i....",
    ".........ioRoi..",
    "........oRRMRRo.",
    ".......ioRMYMRoi",
    "........oRMMRRo.",
    ".........oRMRo..",
    "..........ioi...",
    "..........k.....",
    ".........K......",
    "........k.......",
    ".......K........",
    "......GG........",
    ".....oWG........",
    "....owWo........",
    "...owWo.........",
    "...ooo..........",
]
FLAIL_COLORS = {"o": hx("1a100c"), "R": hx("4a3530"), "M": hx("e0661c"), "Y": hx("ffd070"), "i": hx("c8ccd4"),
                "k": hx("5a5a62"), "K": hx("a0a4ac"), "G": hx("e8c050"), "W": hx("9a6a3a"), "w": hx("5a3a22")}

# ------------------------------------------------------------------ the key chain whip (World 3)
WHIP = [
    "............ggg.",
    "......kKk..gc.g.",
    ".....K...K.g..g.",
    "....k.....Kkgg..",
    "....K.......gG..",
    ".....k......gG..",
    "......K.....g...",
    ".......k....gg..",
    ".......K....g...",
    "......k.....gg..",
    ".....oo.........",
    "....oLLo........",
    "...oLlo.........",
    "..oLlo..........",
    ".oGlo...........",
    ".oo.............",
]
WHIP_COLORS = {"k": hx("5a5a62"), "K": hx("a8acb8"), "g": hx("c8a040"), "G": hx("f0d070"), "c": hx("7fd3ff"),
               "o": hx("1e1e24"), "L": hx("8a5a3a"), "l": hx("5a3a22")}

# ------------------------------------------------------------------ the storm javelin (World 4)
JAVELIN = [
    "............ooo.",
    "...........oCWCo",
    "..........oCcWCo",
    "...........GccCo",
    "..........G.oCo.",
    ".........bG.....",
    "........bBy.....",
    ".......bBy......",
    "......yBy.......",
    ".....bBy........",
    "....bBy.........",
    "...bB...........",
    "..bB............",
    ".GB.............",
    "GG..............",
    "................",
]
JAVELIN_COLORS = {"o": hx("2a3a5a"), "C": hx("7ab0ff"), "c": hx("d8e8f8"), "W": hx("ffffff"), "G": hx("e8c050"),
                  "b": hx("2a4a7a"), "B": hx("9ac0e8"), "y": hx("ffe14a")}

# ------------------------------------------------------------------ the lantern shield (World 5)
SHIELD = [
    "................",
    "..oooooooooooo..",
    "..oIiiiiiiiiIo..",
    "..oiDDDggDDDio..",
    "..oiDaggygaDio..",
    "..oiDgyYYygDio..",
    "..oiDgyYYygDio..",
    "..oiDaggygaDio..",
    "..oiDDDggDDDio..",
    "..oiDdDDDDdDio..",
    "...oiDDaaDDio...",
    "...oiDdDDdDio...",
    "....oiDDDDio....",
    ".....oiDDio.....",
    "......oiio......",
    ".......oo.......",
]
SHIELD_COLORS = {"o": hx("05050a"), "I": hx("c8ccd8"), "i": hx("6a6e7a"), "D": hx("1f2a4a"), "d": hx("15151f"),
                 "g": hx("c8a040"), "y": hx("ffe8a0"), "Y": hx("ffffff"), "a": hx("6a8aff")}

# ------------------------------------------------------------------ the tide harpoon (World 7)
HARPOON = [
    "..............oN",
    ".............oNn",
    "............oNno",
    ".......N...oNno.",
    ".......oN.oNno..",
    "........oNNno...",
    ".........oNo.N..",
    "........bcooNo..",
    ".......bc...o...",
    "......bc........",
    ".....bc..rrr....",
    "....bc..r...r...",
    "...bc...r...r...",
    "..bc.....rrr....",
    ".bc.............",
    "bc..............",
]
HARPOON_COLORS = {"o": hx("021018"), "N": hx("a8e0e0"), "n": hx("f4e4ee"), "b": hx("1a3a8a"), "c": hx("3a7ae0"),
                  "r": hx("d8c8a0")}

# ------------------------------------------------------------------ the quake pick (World 9)
PICK = [
    "................",
    "......ooooo.....",
    ".....oRRvRRooo..",
    "......ooRRRRvRo.",
    "..........oRRRo.",
    ".........oRvRRRo",
    "........owRo.oRo",
    ".......owwo..oRo",
    "......owwo...oRo",
    ".....owwo....ovo",
    "....owwo......o.",
    "...owwo.........",
    "..owwo..........",
    ".oGGo...........",
    ".oGo............",
    "..o.............",
]
PICK_COLORS = {"o": hx("2a140e"), "R": hx("8a4a3a"), "v": hx("ffb070"), "w": hx("6a4a3a"), "G": hx("e8c050")}

# ------------------------------------------------------------------ trophy dolls
# a gilded matryoshka of the boss's world on a wooden plinth with a gold plaque
TROPHY = [
    "................",
    "......oooo......",
    ".....oPPPPo.....",
    "....oPfffPPo....",
    "....oPfefPPo....",
    "....oPfffPPo....",
    ".....oAAAAo.....",
    "....oPPPPPPo....",
    "...oPPAggAPPo...",
    "...oPAgSSgAPo...",
    "...oPPAggAPPo...",
    "....oPPPPPPo....",
    "...oGGGGGGGGo...",
    "..owwwwGGwwwwo..",
    "..oWWWWWWWWWWo..",
    "...oooooooooo...",
]


def trophy_colors(pal):
    p, s, a, d = [hx(c) for c in pal]
    return {"o": mix(d, (0, 0, 0), 0.4), "P": p, "A": a, "g": hx("e8c050"), "S": s, "f": hx("f0d0b0"),
            "e": hx("2a1a10"), "G": hx("e8c050"), "w": hx("5a3a22"), "W": hx("8a5a3a")}


SPRITES = {
    "magma_flail": (FLAIL, FLAIL_COLORS), "key_chain_whip": (WHIP, WHIP_COLORS), "storm_javelin": (JAVELIN, JAVELIN_COLORS),
    "lantern_shield": (SHIELD, SHIELD_COLORS), "tide_harpoon": (HARPOON, HARPOON_COLORS), "quake_pick": (PICK, PICK_COLORS),
}
SHAPES = set(SPRITES) | {"spore_bow", "trophy"}


def paint(shape, pal, path):
    """Paints one replay sprite. The bow's drawing frames go next to it as <name>_pulling_<n>.png."""
    if shape == "spore_bow":
        _save(BOW, BOW_COLORS, path)
        for i, (apex, length) in enumerate(BOW_PULL):
            _save(_bow_frame(apex, length), BOW_COLORS, path[:-4] + f"_pulling_{i}.png")
    elif shape == "trophy":
        _save(TROPHY, trophy_colors(pal), path)
    else:
        grid, colors = SPRITES[shape]
        _save(grid, colors, path)
