"""The rule meters' status icons: one row of ten 9 x 9 icons above the hunger bar, drawn like the vanilla hearts,
shanks and air bubbles (client/MeterHud).

Each icon is one grid below: fill shades 1 (dark) to 4 (light) and h (highlight) are the contents, a and b the
parts that stay when the icon is empty (a brass rim, the caps of an hourglass). The black outline is traced
around the shape. Every meter gets, at its true 9 x 9 texel size like the vanilla icons:

    meter_<id>_container            outline and the dark empty inside, always drawn first
    meter_<id>_container_blinking   the same with a white outline, when the meter jumps
    meter_<id>_full, _half          the contents, drawn over the container (half: left half, or the bottom half
                                    for what fills like a liquid)
    meter_<id>_full_critical, ...   the contents in their danger colours, alternating with the normal ones
    meter_<id>_full_stripes, ...    with the Gauge patterns comfort option: stripes past half, crosshatching in
    meter_<id>_full_critical_cross  danger, so the level reads without the colours

    python3 tools/hud_icons.py --preview D   writes only these sprites, plus an 8x contact sheet into D
"""
import os
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "src/main/resources/assets/matriochka/textures/gui/sprites")

OUTLINE = (0, 0, 0)
EMPTY = (40, 40, 40)
EMPTY_LIT = (58, 58, 58)
BLINK = (255, 255, 255)

# shape, how the half fills ("left" like hearts, "bottom" like a liquid), shades 1 4 h, critical shades, rim a b
ICONS = {
    # World 1: a drop that fills with poison
    "toxin": dict(cut="bottom", grid=(
        ".........",
        "....4....",
        "....4....",
        "...443...",
        "..4h332..",
        "..4h332..",
        "..33322..",
        "...221...",
        ".........",
    ), fill=[(38, 86, 22), (62, 132, 30), (98, 182, 44), (146, 222, 74), (214, 255, 160)],
        crit=[(92, 96, 10), (150, 160, 16), (200, 214, 30), (232, 244, 84), (255, 255, 196)]),
    # World 2: a flame with a white-hot core
    "heat": dict(cut="left", grid=(
        ".........",
        "...3.....",
        "...43....",
        "..443.3..",
        "..44h43..",
        "..4hhh3..",
        "..4hhh2..",
        "...332...",
        ".........",
    ), fill=[(150, 34, 10), (214, 72, 18), (246, 132, 28), (255, 190, 54), (255, 240, 150)],
        crit=[(196, 70, 20), (246, 140, 40), (255, 204, 80), (255, 236, 150), (255, 255, 236)]),
    # World 3: an hourglass whose sand runs until the halls move
    "shift": dict(cut="bottom", grid=(
        ".........",
        "..aaaab..",
        "...h43...",
        "...432...",
        "....3....",
        "...432...",
        "...h43...",
        "..aaaab..",
        ".........",
    ), fill=[(130, 90, 30), (186, 134, 48), (222, 176, 76), (244, 210, 120), (255, 240, 190)],
        crit=[(30, 110, 140), (60, 160, 196), (110, 206, 236), (170, 234, 255), (236, 252, 255)],
        rim=[(150, 98, 52), (100, 62, 30)]),
    # World 4: a lightning bolt charging up to the next gust
    "storm": dict(cut="left", grid=(
        ".........",
        ".....h4..",
        "....h43..",
        "...h43...",
        "..hh4443.",
        "....443..",
        "...443...",
        "...42....",
        "...2.....",
    ), fill=[(52, 84, 150), (96, 146, 220), (160, 204, 255), (212, 236, 255), (255, 255, 255)],
        crit=[(150, 110, 10), (214, 166, 22), (250, 214, 50), (255, 238, 120), (255, 255, 214)]),
    # World 5: a bell, how far your steps carry in the dark
    "noise": dict(cut="left", grid=(
        ".........",
        "....4....",
        "...4h3...",
        "..4h332..",
        "..43332..",
        "..43322..",
        ".4433322.",
        "....1....",
        ".........",
    ), fill=[(96, 62, 12), (164, 112, 24), (214, 162, 40), (244, 206, 88), (255, 242, 176)],
        crit=[(120, 20, 14), (184, 40, 24), (226, 76, 40), (250, 130, 80), (255, 210, 170)]),
    # World 6: a feather, the time left before the columns turn over
    "flip": dict(cut="left", grid=(
        ".........",
        "......hh.",
        ".....h43.",
        "....h433.",
        "...h4332.",
        "...4332..",
        "..432....",
        ".1.......",
        ".........",
    ), fill=[(70, 40, 112), (112, 70, 172), (154, 112, 214), (196, 164, 242), (240, 226, 255)],
        crit=[(126, 26, 96), (186, 50, 146), (230, 96, 196), (250, 156, 228), (255, 224, 248)]),
    # World 7: a brass porthole full of air, your breath
    "oxygen": dict(cut="bottom", grid=(
        ".........",
        "...aaa...",
        "..a4h3a..",
        ".a4h332b.",
        ".a43332b.",
        ".a43322b.",
        "..b222b..",
        "...bbb...",
        ".........",
    ), fill=[(20, 72, 124), (32, 112, 172), (62, 162, 216), (122, 206, 240), (222, 246, 255)],
        crit=[(110, 18, 18), (170, 34, 30), (214, 64, 50), (240, 120, 100), (255, 206, 196)],
        rim=[(214, 164, 72), (140, 94, 34)]),
    # World 7 with a snorkel helmet: its air tank
    "tank": dict(cut="bottom", grid=(
        ".........",
        "....b....",
        "...aaa...",
        "..a4h2b..",
        "..a4h2b..",
        "..a432b..",
        "..a432b..",
        "...bbb...",
        ".........",
    ), fill=[(20, 72, 124), (32, 112, 172), (62, 162, 216), (122, 206, 240), (222, 246, 255)],
        crit=[(110, 18, 18), (170, 34, 30), (214, 64, 50), (240, 120, 100), (255, 206, 196)],
        rim=[(176, 184, 196), (104, 110, 122)]),
    # World 9: a cracked stone, the time left before the ground heaves
    "tremor": dict(cut="left", grid=(
        ".........",
        "..44443..",
        ".4h41433.",
        ".4h44132.",
        ".44h1332.",
        ".4413322.",
        ".3313222.",
        "..32222..",
        ".........",
    ), fill=[(22, 20, 22), (98, 96, 100), (132, 130, 134), (168, 166, 170), (210, 208, 212)],
        # in danger the crack glows, as if the ground were about to open
        crit=[(255, 160, 40), (110, 98, 92), (146, 130, 120), (184, 166, 152), (224, 208, 194)]),
    # World 0: an eye that will not look away
    "obsession": dict(cut="left", grid=(
        ".........",
        ".........",
        "..33333..",
        ".3h22243.",
        ".4421244.",
        ".3422243.",
        "..33333..",
        ".........",
        ".........",
    ), fill=[(16, 2, 4), (176, 26, 36), (92, 34, 42), (226, 214, 210), (255, 252, 248)],
        crit=[(40, 0, 0), (246, 44, 44), (150, 30, 36), (244, 176, 170), (255, 226, 220)]),
}

# World 8: a leaf in the colours of the season, filling as the season turns
LEAF = (
    ".........",
    "....4....",
    "...4h3...",
    "..4h132..",
    "..4h132..",
    "..44132..",
    "...313...",
    "....1....",
    "....1....",
)
for season, fill, crit in (
        ("spring", [(40, 96, 30), (70, 150, 44), (112, 196, 70), (170, 230, 120), (236, 255, 214)], None),
        ("summer", [(30, 74, 20), (52, 116, 30), (86, 160, 40), (150, 206, 60), (226, 246, 150)], None),
        ("autumn", [(120, 36, 12), (180, 66, 20), (226, 110, 30), (246, 170, 60), (255, 226, 150)], None),
        ("winter", [(70, 100, 140), (120, 160, 200), (180, 214, 240), (222, 240, 255), (255, 255, 255)], None)):
    ICONS["season_" + season] = dict(cut="left", grid=LEAF, fill=fill,
                                     crit=[tuple(min(255, int(c * 1.18 + 18)) for c in s) for s in fill])

SHADE = {"1": 0, "2": 1, "3": 2, "4": 3, "h": 4}


def _cells(grid):
    return {(x, y): ch for y, row in enumerate(grid) for x, ch in enumerate(row) if ch != "."}


def _outline(cells):
    ring = set()
    for (x, y) in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells and 0 <= q[0] < 9 and 0 <= q[1] < 9:
                ring.add(q)
    return ring


def _blank():
    return Image.new("RGBA", (9, 9), (0, 0, 0, 0))


def _put(im, x, y, c, a=255):
    im.putpixel((x, y), (c[0], c[1], c[2], a))


def _container(d, blink):
    cells = _cells(d["grid"])
    im = _blank()
    for (x, y) in _outline(cells):
        _put(im, x, y, BLINK if blink else OUTLINE)
    for (x, y), ch in cells.items():
        if ch in "ab":
            _put(im, x, y, d["rim"]["ab".index(ch)])
        else:
            # the empty inside keeps a faint trace of the highlight, like the vanilla empty air bubble
            _put(im, x, y, EMPTY_LIT if ch == "h" else EMPTY)
    return im


def _contents(d, colours, part, pattern):
    cells = _cells(d["grid"])
    fill = [(p, ch) for p, ch in cells.items() if ch in SHADE]
    if part == "half":
        if d["cut"] == "left":
            fill = [(p, ch) for p, ch in fill if p[0] <= 4]
        else:
            rows = sorted({p[1] for p, _ in fill})
            # the liquid's level: the lower half of the rows the contents span
            level = rows[len(rows) // 2]
            fill = [(p, ch) for p, ch in fill if p[1] >= level]
    im = _blank()
    for (x, y), ch in fill:
        c = colours[SHADE[ch]]
        if pattern and ch != "h":
            mark = (x + y) % 3 == 0 if pattern == "stripes" else ((x + y) % 2 == 0 and (x - y) % 4 == 0) or ((x + y) % 4 == 0 and (x - y) % 2 == 0)
            if mark:
                c = tuple(int(v * 0.42) for v in c)
        _put(im, x, y, c)
    return im


def sprites():
    """(name, image) of every meter sprite, in a fixed order."""
    out = []
    for mid, d in ICONS.items():
        out.append(("meter_%s_container" % mid, _container(d, False)))
        out.append(("meter_%s_container_blinking" % mid, _container(d, True)))
        for part in ("full", "half"):
            out.append(("meter_%s_%s" % (mid, part), _contents(d, d["fill"], part, None)))
            out.append(("meter_%s_%s_critical" % (mid, part), _contents(d, d["crit"], part, None)))
            out.append(("meter_%s_%s_stripes" % (mid, part), _contents(d, d["fill"], part, "stripes")))
            out.append(("meter_%s_%s_critical_cross" % (mid, part), _contents(d, d["crit"], part, "cross")))
    return out


class _Sprite:
    def __init__(self, im):
        self.im, self.w, self.h = im, im.width, im.height


def build(save):
    """Writes every meter sprite through tools/gui.py's save (which keeps them when it prunes old sprites)."""
    for name, im in sprites():
        save(name, _Sprite(im))


def preview(directory):
    """An 8x contact sheet: per meter, a row of ten as the HUD shows them at 0, 35, 55 and 90 percent, plus each sprite."""
    os.makedirs(directory, exist_ok=True)
    z = 8
    names = list(ICONS)
    sheet = Image.new("RGBA", ((10 * 8 + 1) * 4 * z + 3 * 20 * z // 4, len(names) * 12 * z + 8), (110, 130, 160, 255))
    for r, mid in enumerate(names):
        d = ICONS[mid]
        for k, pct in enumerate((0, 35, 55, 90)):
            row = Image.new("RGBA", (10 * 8 + 1, 9), (0, 0, 0, 0))
            halves = round(pct / 5)
            for i in range(10):
                x = (10 - 1 - i) * 8
                row.alpha_composite(_container(d, False), (x, 0))
                colours = d["crit"] if pct >= 90 else d["fill"]
                if i * 2 + 1 < halves:
                    row.alpha_composite(_contents(d, colours, "full", None), (x, 0))
                elif i * 2 + 1 == halves:
                    row.alpha_composite(_contents(d, colours, "half", None), (x, 0))
            big = row.resize((row.width * z, row.height * z), Image.NEAREST)
            sheet.alpha_composite(big, (k * (10 * 8 + 6) * z, r * 12 * z + 8))
    sheet.save(os.path.join(directory, "meters.png"))


if __name__ == "__main__":
    if "--preview" in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        for name, im in sprites():
            im.save(os.path.join(OUT, name + ".png"))
        preview(sys.argv[sys.argv.index("--preview") + 1])
