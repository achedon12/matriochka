"""The bosses' health bars: one design per boss, drawn for what it is and the world it rules.

Every bar shares one layout so client/BossBars.java can draw any of them (logical px, the sprites are S times
larger):
  - bossbar_frame_<id>  240 x 40: the boss's own housing: a band round the gauge window (TRACK), two sculpted ends
    that carry its emblem, and a drop shadow so it stands off any sky. It is drawn over the gauge, so its rims and
    the shadow it casts into the window sit on top of the gauge's matter.
  - bossbar_plate_<id>  nine-slice 48 x 16: what its name is written on, over the top of the band.
The gauge's matter (molten metal, soul fire, sea water...) and the life round the bar (embers, spores, bubbles)
are animated by BossBars.java.

  block_guardian      mossy stone blocks, crenellated; runed stone pillars with floating cubes at the ends
  spore_queen         ribbed chitin; clusters of spotted mushrooms and a glowing toxin pod at the ends
  ash_titan           riveted black iron with glowing seams; furnaces at the ends, a smoking stack on the right
  grand_jailer        dark iron studded with rivets, prison bars across the gauge; padlocks and hanging chains
  storm_king          a copper conduit in storm clouds; lightning-rod spires with charged orbs, bolts
  light_eater         no metal at all: smoke and tendrils; a violet eye with a slit pupil at each end
  your_double         a mirror lozenge, mint above and pink below; mirror crystals at the ends, shards
  pressure_leviathan  a brass diving pipe with flanges and barnacles; a porthole and a pressure dial
  seasons_master      clockwork brass and dark wood; a great gear and a clock face, the seasons' signs
  terrain_heart_boss  layered rock with a jagged edge and red veins; a heart crystal in a geode, crystal spires
  the_unfinished      a doll half painted: lacquer and gold at the left end, bare pencilled wood at the right
"""
import math

LW, LH = 240, 40
TRACK_X, TRACK_Y, TRACK_W, TRACK_H = 24, 17, 192, 10
BAND_Y0, BAND_Y1 = 12, 32
LEFT_X, RIGHT_X = 12, 228          # the centres of the two ends


def build(ns):
    mine = globals()
    mine.update({k: v for k, v in ns.items() if not k.startswith("__") and k not in mine})
    from content import BOSSES
    for b in BOSSES:
        FRAMES[b["id"]]()
        PLATES[b["id"]]()
        cap(b["id"])


# ------------------------------------------------------------------ geometry and finishing
def L(v):
    return v * S


def new():
    return Cv(L(LW), L(LH))


def in_track(x, y, pad=0):
    return L(TRACK_X) - pad <= x < L(TRACK_X + TRACK_W) + pad and L(TRACK_Y) - pad <= y < L(TRACK_Y + TRACK_H) + pad


def in_band(x, y, y0=BAND_Y0, y1=BAND_Y1, x0=8, x1=232):
    return L(x0) <= x < L(x1) and L(y0) <= y < L(y1)


def paint(cv, inside, color, outline=..., bbox=None):
    if outline is ...:
        outline = OUTLINE
    return shape(cv, inside, bbox or (0, 0, cv.w, cv.h), color, outline)


def noise_mat(cols, seed, sx=6.0, sy=6.0, light=0.5, k=0.45, grad=0.35):
    """A noisy material lit from above across the band."""
    def color(x, y):
        t = light + (fbm(x / sx, y / sy, seed, 3) - 0.5) * k - ((y / S - BAND_Y0) / (BAND_Y1 - BAND_Y0) - 0.5) * grad
        return ramp(cols, clamp(t))
    return color


def finish(cv, name, window_rim=None, rim_light=True, after=None):
    """Cuts the gauge window, shades its inside, lights the housing's top edges and casts the drop shadow."""
    from PIL import Image as _I
    tx0, ty0, tx1, ty1 = L(TRACK_X), L(TRACK_Y), L(TRACK_X + TRACK_W), L(TRACK_Y + TRACK_H)
    if window_rim:
        cols = window_rim
        for y in range(ty0 - L(2), ty1 + L(2)):
            for x in range(tx0 - L(2), tx1 + L(2)):
                if in_track(x, y):
                    continue
                up = y < (ty0 + ty1) // 2
                d = min(abs(y - ty0), abs(y - ty1), abs(x - tx0), abs(x - tx1)) / L(2)
                light = (0.8 if up else 0.35) - d * 0.2 + (fbm(x / 6, y / 4, 7, 2) - 0.5) * 0.1
                cv.put(x, y, ramp(cols, clamp(light)))
        for x in range(tx0 - L(2) - 1, tx1 + L(2) + 1):
            cv.put(x, ty0 - L(2) - 1, OUTLINE)
            cv.put(x, ty1 + L(2), OUTLINE)
        for y in range(ty0 - L(2) - 1, ty1 + L(2) + 1):
            cv.put(tx0 - L(2) - 1, y, OUTLINE)
            cv.put(tx1 + L(2), y, OUTLINE)
    for y in range(ty0, ty1):
        for x in range(tx0, tx1):
            cv.p[x, y] = (0, 0, 0, 0)
    if rim_light:
        # a thin light along every upper edge of the housing
        src = cv.im.copy().load()
        for y in range(1, cv.h):
            for x in range(cv.w):
                if src[x, y][3] > 200 and src[x, y - 1][3] < 60 and not in_track(x, y - 1):
                    r, g, b, _ = src[x, y]
                    cv.p[x, y] = (min(255, r + 55), min(255, g + 55), min(255, b + 55), 255)
    # the shadow the rim casts into the window
    for x in range(tx0, tx1):
        for k in range(4):
            cv.put(x, ty0 + k, (0, 0, 0), 0.45 * (1 - k / 4))
        cv.put(x, ty1 - 1, (0, 0, 0), 0.3)
    for y in range(ty0, ty1):
        for k in range(3):
            cv.put(tx0 + k, y, (0, 0, 0), 0.35 * (1 - k / 3))
            cv.put(tx1 - 1 - k, y, (0, 0, 0), 0.2 * (1 - k / 3))
    if after:
        after(cv)
    # what stands inside the window (bars) is kept; the rest of it stays clear
    keep = {(x // S, y // S) for y in range(ty0, ty1) for x in range(tx0, tx1) if cv.p[x, y][3] >= 200}
    blocky(cv)
    # the window stays clear, with a hard one-texel shade along its top and left
    for y in range(ty0, ty1):
        for x in range(tx0, tx1):
            if (x // S, y // S) not in keep:
                cv.p[x, y] = (0, 0, 0, 0)
    for x in range(tx0, tx1):
        for k in range(S):
            if (x // S, (ty0 + k) // S) not in keep:
                cv.p[x, ty0 + k] = (0, 0, 0, 110)
    for y in range(ty0 + S, ty1):
        for k in range(S):
            if ((tx0 + k) // S, y // S) not in keep:
                cv.p[tx0 + k, y] = (0, 0, 0, 80)
    save(name, cv)


def blocky(cv, colors=44, shadow=True):
    """Makes a sprite read as Minecraft pixel art: one texel per logical pixel (box-averaged down from the S x
    canvas), a short palette with no dithering, hard alpha, a dark outline on the outside edge and a hard one-texel
    shadow under it; then scaled back up by S without smoothing so it keeps its logical size."""
    from PIL import Image as _I
    im = cv.im
    w, h = im.width // S, im.height // S
    small = im.resize((w, h), _I.BOX)
    a = small.getchannel("A").point(lambda v: 255 if v >= 110 else 0)
    rgb = _I.new("RGB", (w, h), (0, 0, 0))
    rgb.paste(small.convert("RGB"), mask=a)
    q = rgb.quantize(colors=colors, method=_I.Quantize.MEDIANCUT, dither=_I.Dither.NONE).convert("RGB")
    out = q.convert("RGBA")
    out.putalpha(a)
    px, ap = out.load(), a.load()
    edge = []
    for y in range(h):
        for x in range(w):
            if ap[x, y] == 0:
                continue
            if any(not (0 <= x + dx < w and 0 <= y + dy < h) or ap[x + dx, y + dy] == 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                edge.append((x, y))
    for x, y in edge:
        r, g, b, _ = px[x, y]
        px[x, y] = (min(r, OUTLINE[0] + r // 5), min(g, OUTLINE[1] + g // 5), min(b, OUTLINE[2] + b // 5), 255)
    if shadow:
        base = out.copy()
        sh = _I.new("RGBA", (w, h), (0, 0, 0, 0))
        sp = sh.load()
        bp = base.load()
        for y in range(h):
            for x in range(w):
                if bp[x, y][3] and x + 1 < w and y + 1 < h and bp[x + 1, y + 1][3] == 0:
                    sp[x + 1, y + 1] = (12, 8, 8, 150)
        sh.alpha_composite(base)
        out = sh
    cv.im = out.resize((w * S, h * S), _I.NEAREST)
    cv.p = cv.im.load()
    return cv


def glow_line(cv, pts, col, r=1.2, a=0.9):
    stroke(cv, pts, r * 2.4, r * 2.4, col, a * 0.22)
    stroke(cv, pts, r, r * 0.8, col, a)


def mirrored(fn):
    """Draws an end emblem at both ends: fn(cv, cx, side) with side -1 at the left, +1 at the right."""
    def both(cv):
        fn(cv, L(LEFT_X), -1)
        fn(cv, L(RIGHT_X), 1)
    return both


def ellipse_in(cx, cy, rx, ry):
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def lit(cols, cx, cy, r, base=0.55):
    """A colour function for a rounded form lit from the top left."""
    return lambda x, y: ramp(cols, clamp(base + 0.45 - ((x - cx) + (y - cy) * 1.2) / (2.2 * r) - math.hypot(x - cx, y - cy) / r * 0.25))


# ------------------------------------------------------------------ materials
MOSS = [(20, 36, 14), (38, 66, 22), (62, 100, 34), (98, 140, 50), (146, 184, 78)]
CHITIN = [(14, 20, 10), (30, 40, 18), (50, 64, 28), (78, 92, 40), (116, 130, 60), (160, 170, 90)]
CAP = [(60, 10, 40), (110, 24, 70), (160, 50, 110), (206, 96, 150), (240, 160, 196)]
TOXIN = (170, 240, 70)
SOOT = [(10, 8, 8), (22, 18, 18), (38, 32, 30), (58, 50, 46), (88, 78, 70), (130, 118, 106)]
HOT = [(90, 14, 4), (190, 60, 10), (250, 140, 30), (255, 220, 120), (255, 250, 220)]
GAOL = [(10, 12, 16), (22, 26, 34), (40, 46, 58), (66, 74, 90), (104, 114, 132), (156, 166, 184)]
SOULC = (110, 190, 255)
SLATE = [(16, 20, 34), (30, 38, 60), (50, 62, 94), (78, 94, 132), (120, 138, 176), (180, 196, 224)]
SILVER = [(60, 64, 76), (110, 116, 130), (160, 166, 180), (200, 206, 218), (232, 236, 244), (255, 255, 255)]
MINT = [(40, 110, 104), (90, 180, 168), (150, 226, 212), (204, 248, 238)]
PINK = [(120, 50, 110), (196, 104, 180), (236, 164, 222), (252, 214, 244)]
VERD = [(14, 40, 40), (26, 74, 70), (44, 110, 100), (80, 150, 130), (140, 196, 170)]
ROCK = [(30, 14, 10), (60, 30, 22), (96, 52, 36), (134, 80, 56), (176, 116, 84), (214, 160, 120)]
CRYST = [(60, 20, 40), (140, 40, 60), (220, 80, 80), (255, 160, 130), (255, 230, 210)]
RAWWOOD = [(120, 86, 52), (168, 128, 84), (204, 166, 116), (228, 198, 152), (244, 226, 190)]
VOID = [(4, 2, 10), (14, 8, 30), (30, 18, 60), (60, 40, 110)]
VIOLET = (150, 110, 255)
PENCIL = (78, 68, 60)


# ------------------------------------------------------------------ Block Guardian
def block_guardian():
    cv = new()
    grid = 8
    heights = [0, 3, 1, 2, 0, 3, 1, 0, 2, 3, 0, 1, 3, 1, 0, 2, 1, 3, 0, 2, 1, 0, 3, 1, 2, 0, 1, 3]

    def stone(x, y, seed=5):
        u, v = x / S, y / S
        bx, by = int(u // grid), int(v // grid)
        lx, ly = u % grid, v % grid
        tone = 0.42 + _h(bx, by, seed) * 0.22 + (fbm(x / 3, y / 3, 9, 2) - 0.5) * 0.25
        if lx < 1 or ly < 1:
            tone += 0.2
        elif lx > grid - 1.1 or ly > grid - 1.1:
            tone -= 0.25
        c = ramp(STONE, clamp(tone))
        if ly < 2.5 + 2.5 * fbm(u / 2, bx, 3, 2) and fbm(u / 4, v / 4, 11, 2) > 0.42:
            c = ramp(MOSS, clamp(0.55 + (fbm(x / 2, y / 2, 4, 2) - 0.5) * 0.8 - ly / 6))
        if abs(fbm(x / 7, y / 7, 13, 3) - 0.5) < 0.012:
            c = scale_c(c, 0.55)
        return c

    def inside(x, y):
        u, v = x / S, y / S
        if not 6 <= u < 234:
            return False
        col = int((u - 6) // grid)
        return 10 - heights[col % len(heights)] * 0.7 <= v < 34 + (heights[(col + 7) % len(heights)] % 2)

    paint(cv, inside, stone)

    @mirrored
    def pillar(cv, cx, side):
        x0, x1 = cx - L(10), cx + L(10)
        paint(cv, lambda x, y: x0 <= x < x1 and L(3) <= y < L(37), lambda x, y: stone(x + L(3), y, 7))
        for y0, y1 in ((L(1), L(4)), (L(36), L(39))):
            paint(cv, lambda x, y, y0=y0, y1=y1: x0 - L(1.5) <= x < x1 + L(1.5) and y0 <= y < y1,
                  lambda x, y, y0=y0: ramp(STONE, 0.78 - (y - y0) / L(3) * 0.45), OUTLINE, (x0 - L(3), y0 - 2, x1 + L(3), y1 + 2))
        # a carved rune glowing like the guardian's eyes
        rx, ry = cx, L(20)
        cv.glow(rx, ry, L(7), (90, 230, 240), 0.3)
        for d in (L(5), L(4.4)):
            for a in range(0, 360, 6):
                r = math.radians(a)
                cv.put(rx + math.cos(r) * d, ry + math.sin(r) * d, OUTLINE if d > L(4.6) else STONE[1])
        glow_line(cv, [(rx - L(2.4), ry - L(2.2)), (rx, ry + L(2.4)), (rx + L(2.4), ry - L(2.2))], (90, 230, 240), 0.9)
        glow_line(cv, [(rx, ry - L(3)), (rx, ry - L(0.6))], (90, 230, 240), 0.8)
        # moss hanging off the capital
        for k in range(6):
            mx = x0 + L(2 + k * 3.2)
            ln = L(1 + _h(k, side + 2, 15) * 3.5)
            stroke(cv, [(mx, L(4)), (mx, L(4) + ln)], L(0.6), L(0.4), MOSS[2 + k % 2])
        # a floating cube over the pillar, like the ones that orbit the guardian
        fx, fy, fs = cx + side * L(4), L(-1.2), L(2.4)
        paint(cv, lambda x, y: abs(x - fx) < fs and abs(y - fy) < fs and y >= 0,
              lambda x, y: ramp(STONE, 0.8 - (y - fy + fs) / (2 * fs) * 0.5), OUTLINE, (fx - fs - 2, 0, fx + fs + 2, fy + fs + 2))

    pillar(cv)
    for x in range(L(16), L(224)):
        for y in range(cv.h):
            if cv.alpha(x, y) > 200:
                if _h(x, 3, 17) > 0.45:
                    cv.put(x, y - 1, MOSS[3])
                if _h(x, 5, 17) > 0.8:
                    cv.put(x, y - 2, MOSS[4])
                break
    for u in range(44, 200, 26):
        cx, cy = L(u), L(30)
        glow_line(cv, [(cx - L(1.5), cy - L(1)), (cx, cy + L(0.6)), (cx + L(1.5), cy - L(1))], (90, 230, 240), 0.5, 0.8)
    finish(cv, "bossbar_frame_block_guardian", STONE)


# ------------------------------------------------------------------ Spore Queen
def mushroom(cv, cx, by, r, h, lean, seed):
    stem_top = (cx + lean * L(2), by - h)
    tube(cv, [(cx, by), stem_top], max(1.2, r * 0.22), max(1.0, r * 0.16), [(140, 130, 100), (200, 190, 150), (236, 228, 196)])
    sx, sy = stem_top

    def capin(x, y):
        return ((x - sx) / r) ** 2 + ((y - sy) / (r * 0.6)) ** 2 <= 1 and y <= sy + r * 0.18

    def capcol(x, y):
        t = 0.75 - (y - sy) / r * 0.9 - (x - sx) / r * 0.25
        c = ramp(CAP, clamp(t))
        if fbm(x / 2.6, y / 2.6, seed, 2) > 0.74:
            c = (252, 238, 210)
        return c

    paint(cv, capin, capcol, OUTLINE, (sx - r - 2, sy - r - 2, sx + r + 2, sy + r * 0.4))
    for k in range(-3, 4):
        cv.put(sx + k * r / 4, sy + r * 0.2, (90, 40, 60))


def spore_queen():
    cv = new()

    def inside(x, y):
        u, v = x / S, y / S
        if not 8 <= u < 232:
            return False
        wob = 1.6 * math.sin(u / 6) + 1.0 * math.sin(u / 2.7 + 1)
        return 12 + wob * 0.4 <= v < 33 - wob * 0.35

    def color(x, y):
        u, v = x / S, y / S
        rib = (u / 5 + math.sin(v / 2.5) * 0.4) % 1
        t = 0.32 + 0.4 * rib ** 1.5 + (fbm(x / 4, y / 4, 21, 3) - 0.5) * 0.25 - (v - 22) / 30
        c = ramp(CHITIN, clamp(t))
        if abs(fbm(x / 9, y / 5, 27, 3) - 0.5) < 0.01:
            c = mix(c, TOXIN, 0.8)
        return c

    paint(cv, inside, color)

    @mirrored
    def cluster(cv, cx, side):
        paint(cv, ellipse_in(cx, L(22), L(10), L(13)), lit(CHITIN, cx, L(22), L(12), 0.4))
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.55
            stroke(cv, [(cx + math.cos(a) * L(4), L(22) + math.sin(a) * L(5)), (cx + math.cos(a) * L(9), L(22) + math.sin(a) * L(12))], 0.9, 0.6, CHITIN[0])
        cv.glow(cx, L(24), L(10), TOXIN, 0.35)
        paint(cv, ellipse_in(cx, L(24), L(4.5), L(5.5)), lambda x, y: mix(TOXIN, (40, 90, 10), clamp(math.hypot(x - cx + L(1), y - L(22)) / L(6))), (30, 60, 10))
        cv.put(cx - L(1.5), L(21.5), (250, 255, 220))
        mushroom(cv, cx - side * L(3), L(12), L(6.5), L(6), side * 0.6, 31)
        mushroom(cv, cx + side * L(5), L(13), L(4), L(4), side * 1.2, 33)
        mushroom(cv, cx - side * L(8), L(15), L(3), L(3), -side * 0.4, 35)
        for k, dx in enumerate((-5, 0, 5)):
            x = cx + L(dx)
            ln = L(2 + _h(k, side + 2, 37) * 3)
            stroke(cv, [(x, L(33)), (x + L(0.6), L(33) + ln)], L(0.9), L(0.4), CHITIN[2])
            cv.disc(x + L(0.6), L(33) + ln + 1, L(0.8), TOXIN)

    cluster(cv)
    for u, r in ((52, 2.6), (86, 1.8), (150, 2.4), (188, 1.6)):
        mushroom(cv, L(u), L(13), L(r), L(r * 0.9), 0.3, 41 + u)
    for u in (64, 110, 132, 170, 206):
        ln = L(2 + _h(u, 1, 3) * 4)
        stroke(cv, [(L(u), L(32)), (L(u) + 1, L(32) + ln)], L(0.8), L(0.3), CHITIN[2])
        cv.disc(L(u) + 1, L(32) + ln + 1, L(0.7), TOXIN)
    finish(cv, "bossbar_frame_spore_queen", CHITIN)


# ------------------------------------------------------------------ Ash Titan
def ash_titan():
    cv = new()

    def iron(x, y):
        u, v = x / S, y / S
        plate = int((u - 8) // 28)
        t = 0.36 + _h(plate, 0, 7) * 0.1 + (fbm(x / 5, y / 5, 31, 3) - 0.5) * 0.22 - (v - 22) / 34
        if (u - 8) % 28 < 1.2:
            t -= 0.25
        c = ramp(SOOT, clamp(t))
        heat = fbm(x / 14, y / 6, 33, 2)
        if abs(heat - 0.55) < 0.011:
            c = ramp(HOT, 0.75 - abs(heat - 0.55) * 30)
        elif abs(heat - 0.55) < 0.03:
            c = mix(c, HOT[1], 0.5)
        return c

    paint(cv, lambda x, y: in_band(x, y, 11, 33), iron)
    for u in range(16, 226, 14):
        rivet(cv, L(u), L(13.5), L(1.0), SOOT)
        rivet(cv, L(u), L(30.5), L(1.0), SOOT)

    @mirrored
    def furnace(cv, cx, side):
        x0, x1 = cx - L(11), cx + L(11)
        paint(cv, lambda x, y: x0 <= x < x1 and L(4) <= y < L(37), iron)
        for y0, y1 in ((L(3), L(7)), (L(35), L(39))):
            paint(cv, lambda x, y, y0=y0, y1=y1: x0 - L(1) <= x < x1 + L(1) and y0 <= y < y1,
                  lambda x, y, y0=y0: ramp(SOOT, 0.8 - (y - y0) / L(4) * 0.5), OUTLINE, (x0 - L(2), y0 - 2, x1 + L(2), y1 + 2))
            for k in (-7, 0, 7):
                rivet(cv, cx + L(k), (y0 + y1) / 2, L(0.9), SOOT)
        mx, my = cx, L(23)

        def mouth(x, y):
            dx, dy = (x - mx) / L(6.5), (y - my) / L(8)
            return math.hypot(dx, dy) < 1 if dy < 0 else abs(dx) < 1 and dy < 1

        cv.glow(mx, my + L(2), L(13), HOT[2], 0.35)
        paint(cv, mouth, lambda x, y: ramp(HOT, clamp(1.0 - (y - (my - L(8))) / L(17) * 0.9 - abs(x - mx) / L(14))), OUTLINE)
        for k in range(-2, 3):
            cv.rect(mx + L(k * 2.6) - 1, my - L(2), mx + L(k * 2.6) + 2, my + L(8), SOOT[2])
        cv.rect(mx - L(6.5), my + L(3), mx + L(6.5), my + L(4), SOOT[2])

    furnace(cv)
    sx = L(RIGHT_X - 4)
    paint(cv, lambda x, y: sx - L(4) <= x < sx + L(4) and 0 <= y < L(4), lambda x, y: ramp(SOOT, 0.3 + 0.5 * math.sin(math.pi * (x - sx + L(4)) / L(8))), OUTLINE)
    cv.rect(sx - L(3), 0, sx + L(3), L(0.8), HOT[3])
    for u in (60, 172):
        for j in range(5):
            cv.rect(L(u + j * 4), L(28), L(u + j * 4 + 2.2), L(31), HOT[1])
            cv.rect(L(u + j * 4), L(28), L(u + j * 4 + 2.2), L(29), HOT[3])
    def after(cv):
        for x in range(L(TRACK_X), L(TRACK_X + TRACK_W)):
            cv.put(x, L(TRACK_Y) - 1, HOT[1], 0.7)

    finish(cv, "bossbar_frame_ash_titan", SOOT, after=after)


# ------------------------------------------------------------------ Grand Jailer
def padlock(cv, cx, cy, s):
    for a in range(180, 361, 3):
        r = math.radians(a)
        for w in (0, 1, 2):
            cv.disc(cx + math.cos(r) * (s * 0.62 - w), cy - s * 0.2 + math.sin(r) * (s * 0.8 - w), L(0.7), GAOL[3 + (w == 1)])
    paint(cv, lambda x, y: abs(x - cx) <= s and cy - s * 0.25 <= y < cy + s * 1.0,
          lambda x, y: ramp(GOLD[1:], clamp(0.9 - (y - cy + s * 0.25) / (s * 1.25) * 0.55 - (x - cx) / (s * 2) * 0.4)), OUTLINE,
          (cx - s - 2, cy - s * 0.3, cx + s + 2, cy + s * 1.05))
    for x in range(int(cx - s + 2), int(cx + s - 1)):
        cv.put(x, cy - s * 0.25 + 3, GOLD[5])
        cv.put(x, cy + s * 0.95 - 2, GOLD[1])
    cv.disc(cx, cy + s * 0.25, s * 0.2, OUTLINE)
    paint(cv, lambda x, y: abs(x - cx) <= s * 0.09 + (y - cy - s * 0.25) * 0.12 and cy + s * 0.25 <= y < cy + s * 0.7, lambda x, y: OUTLINE, None)
    rivet(cv, cx - s * 0.7, cy + s * 0.05, L(0.7), GOLD)
    rivet(cv, cx + s * 0.7, cy + s * 0.05, L(0.7), GOLD)


def grand_jailer():
    cv = new()
    paint(cv, lambda x, y: in_band(x, y, 11, 33), noise_mat(GAOL, 51, 4, 9, 0.42, 0.35, 0.5))
    for u in range(12, 228, 6):
        cv.put(L(u), L(13), GAOL[5])
        cv.put(L(u) + 1, L(13) + 1, GAOL[0])
        cv.put(L(u), L(30.5), GAOL[5])
        cv.put(L(u) + 1, L(30.5) + 1, GAOL[0])
    for a, b in ((28, 82), (92, 148), (158, 212)):
        for i in range(26):
            t = i / 25
            x = L(a + (b - a) * t)
            y = L(33 + 4.5 * math.sin(math.pi * t))
            if i % 2 == 0:
                for ang in range(0, 360, 20):
                    r = math.radians(ang)
                    cv.put(x + math.cos(r) * L(1.2), y + math.sin(r) * L(0.8), GAOL[3 if ang < 180 else 5])
                cv.put(x, y, GAOL[0])
            else:
                cv.rect(x - L(0.8), y - 1, x + L(0.8), y + 1, GAOL[5])
    key_shape(cv, L(120), L(34), 0.8 * S / 2, [(30, 24, 14)] + GOLD[1:])

    @mirrored
    def lock_end(cv, cx, side):
        paint(cv, lambda x, y: abs(x - cx) < L(9) and L(8) <= y < L(36), noise_mat(GAOL, 53 + side, 3, 6, 0.5, 0.3, 0.6))
        for y in (L(10), L(33.5)):
            for x in range(int(cx - L(9)), int(cx + L(9)), L(3)):
                rivet(cv, x + L(1.5), y, L(0.8), GAOL)
        cv.glow(cx, L(22), L(10), SOULC, 0.25)
        padlock(cv, cx, L(18), L(7.5))

    lock_end(cv)
    def after(cv):
        for u in range(TRACK_X + 12, TRACK_X + TRACK_W - 4, 16):
            x = L(u)
            for y in range(L(TRACK_Y) - L(2), L(TRACK_Y + TRACK_H) + L(2)):
                for d in range(-2, 3):
                    cv.put(x + d, y, ramp(GAOL, 0.78 - abs(d) * 0.18 - d * 0.05))
                cv.put(x - 3, y, OUTLINE)
                cv.put(x + 3, y, OUTLINE)
            rivet(cv, x, L(TRACK_Y) - L(1.3), L(0.9), GAOL)
            rivet(cv, x, L(TRACK_Y + TRACK_H) + L(1.3), L(0.9), GAOL)

    finish(cv, "bossbar_frame_grand_jailer", GAOL, after=after)


# ------------------------------------------------------------------ Storm King
def storm_king():
    cv = new()
    paint(cv, lambda x, y: in_band(x, y, 13, 31, 14, 226),
          lambda x, y: ramp(COPPER, clamp(0.9 - abs(y - L(22)) / L(9) * 0.9 + (fbm(x / 9, y / 3, 61, 2) - 0.5) * 0.2)))
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.alpha(x, y) > 200 and fbm(x / 4, y / 4, 63, 3) > 0.7:
                cv.tint(x, y, VERD[3], 0.6)
    for u in range(40, 210, 24):
        cv.rect(L(u), L(12), L(u + 3), L(32), COPPER[4])
        for y in range(L(12), L(32)):
            cv.put(L(u), y, COPPER[5])
            cv.put(L(u + 3) - 1, y, COPPER[1])
    for i, u in enumerate(range(22, 222, 11)):
        r = L(3.4 + 1.6 * _h(i, 1, 65))
        cloud_curl(cv, L(u), L(12) - r * 0.2, r, SLATE[1:])
        cloud_curl(cv, L(u + 5), L(32) + r * 0.15, r * 0.8, SLATE[:5])

    @mirrored
    def spire(cv, cx, side):
        for dx, dy, r in ((-5, 30, 5), (4, 31, 5.5), (0, 26, 6), (-7, 22, 4), (7, 23, 4)):
            cloud_curl(cv, cx + L(dx), L(dy), L(r), SLATE[1:])
        tube(cv, [(cx, L(30)), (cx, L(7))], L(1.6), L(1.0), COPPER[1:])
        for y in (L(12), L(17), L(22)):
            cv.rect(cx - L(2.6), y, cx + L(2.6), y + L(1.2), COPPER[4])
            cv.put(cx - L(2.6), y, COPPER[5])
        cv.glow(cx, L(5), L(9), (255, 225, 74), 0.4)
        paint(cv, ellipse_in(cx, L(5), L(3.6), L(3.6)), lambda x, y: mix((255, 255, 230), (255, 200, 40), clamp(math.hypot(x - cx + L(1), y - L(4)) / L(4))), (110, 70, 10))
        bolt(cv, [(cx + side * L(4), L(5)), (cx + side * L(8), L(9)), (cx + side * L(6), L(11)), (cx + side * L(10), L(16))])

    spire(cv)
    finish(cv, "bossbar_frame_storm_king", COPPER)


# ------------------------------------------------------------------ Light Eater
def light_eater():
    cv = new()
    for y in range(cv.h):
        for x in range(cv.w):
            u, v = x / S, y / S
            n = fbm(x / 10, y / 7, 71, 4)
            d = max(0, abs(v - 22) - 7.5) / 6 if 6 <= u < 234 else 9
            for ex in (LEFT_X, RIGHT_X):
                d = min(d, max(0, math.hypot((u - ex) / 1.2, v - 22) - 9) / 5)
            d -= (n - 0.5) * 1.6
            if d < 1:
                a = clamp(1 - d) ** 1.5
                cv.put(x, y, ramp(VOID, clamp(0.35 + (n - 0.5) * 1.2)), a * 0.96)
    for u, up in ((36, 1), (62, -1), (96, 1), (128, -1), (160, 1), (190, -1), (210, 1)):
        y0 = L(14) if up > 0 else L(30)
        pts = bez((L(u), y0), (L(u + 4), y0 - up * L(7)), (L(u + 11), y0 - up * L(9)), (L(u + 8), y0 - up * L(4)))
        stroke(cv, pts, L(2.2), L(0.3), VIOLET, 0.3)
        stroke(cv, pts, L(1.6), L(0.2), VOID[0])

    @mirrored
    def eye(cv, cx, side):
        cy = L(22)

        def almond(x, y):
            dx, dy = (x - cx) / L(9), (y - cy) / L(9)
            return abs(dx) < 1 and abs(dy) < 0.62 * (1 - dx * dx)

        cv.glow(cx, cy, L(14), VIOLET, 0.4)
        paint(cv, almond, lambda x, y: mix((40, 20, 90), (200, 170, 255), clamp(1 - math.hypot(x - cx, y - cy) / L(9))), (20, 8, 40))
        ix = cx - side * L(1.5)
        paint(cv, ellipse_in(ix, cy, L(4), L(4.4)), lambda x, y: ramp([(60, 20, 120), (150, 90, 255), (230, 200, 255)], clamp(1 - math.hypot(x - ix, y - cy) / L(4.4) + (y < cy) * 0.15)), (30, 10, 60))
        paint(cv, lambda x, y: abs(x - ix) < L(0.9) * (1 - abs(y - cy) / L(4)) and abs(y - cy) < L(4), lambda x, y: (2, 0, 8), None)
        cv.put(ix - L(1.6), cy - L(1.6), (255, 255, 255))
        for k in range(-2, 3):
            stroke(cv, [(cx + L(k * 3), cy - L(5.5 - abs(k) * 0.8)), (cx + L(k * 4), cy - L(9 - abs(k)))], L(0.7), L(0.2), VOID[0])

    eye(cv)
    for i in range(16):
        x, y = L(20 + _h(i, 2, 73) * 200), L(6 + _h(i, 4, 73) * 30)
        if not in_track(x, y, L(3)):
            cv.put(x, y, (230, 220, 255), 0.8)
            cv.glow(x, y, L(2), VIOLET, 0.3)
    def after(cv):
        for x in range(L(TRACK_X), L(TRACK_X + TRACK_W)):
            cv.put(x, L(TRACK_Y) - 1, VIOLET, 0.6)
            cv.put(x, L(TRACK_Y + TRACK_H), VIOLET, 0.4)

    finish(cv, "bossbar_frame_light_eater", None, rim_light=False, after=after)


# ------------------------------------------------------------------ Your Double
def your_double():
    cv = new()
    mid = L(22)

    def inside(x, y):
        u, v = x / S, y / S
        if not 4 <= u < 236:
            return False
        tip = min(u - 4, 236 - u)
        return abs(v - 22) < min(10, 2 + tip * 0.8)

    def color(x, y):
        u, v = x / S, y / S
        top = y < mid
        d = abs(y - mid) / L(10)
        t = 0.3 + d * 0.6 + 0.2 * math.sin((u + v * (1 if top else -1)) / 8)
        return ramp(MINT if top else PINK, clamp(t))

    paint(cv, inside, color, (60, 40, 80))
    src = cv.im.copy().load()
    for y in range(cv.h):
        for x in range(cv.w):
            if src[x, y][3] > 200 and any(src[min(cv.w - 1, max(0, x + dx)), min(cv.h - 1, max(0, y + dy))][3] < 100 for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0))):
                cv.put(x, y, SILVER[4 if y < mid else 1])
    for x in range(L(6), L(234)):
        if cv.alpha(x, mid) > 200:
            cv.put(x, mid, (255, 255, 255))

    @mirrored
    def crystal(cv, cx, side):
        cv.glow(cx, mid, L(14), (240, 220, 250), 0.35)

        def gem(x, y):
            return abs(x - cx) / L(7) + abs(y - mid) / L(17) < 1

        def facet(x, y):
            top = y < mid
            left = (x < cx) == (side < 0)
            return ramp(MINT if top else PINK, 0.85 if left == top else 0.45 if left else 0.25)

        paint(cv, gem, facet, (60, 40, 80))
        stroke(cv, [(cx, mid - L(16)), (cx, mid + L(16))], 0.5, 0.5, (255, 255, 255), 0.7)
        stroke(cv, [(cx - L(6.5), mid), (cx + L(6.5), mid)], 0.5, 0.5, (255, 255, 255), 0.9)
        star(cv, cx - L(2), mid - L(8), L(2.4), (255, 255, 255))

    crystal(cv)
    for i in range(14):
        u = 24 + i * 14.5
        for sd in (-1, 1):
            cx, cy = L(u + 4 * _h(i, 2, 81)), mid + sd * L(13 + 4 * _h(i, sd + 3, 81))
            r = L(1.1 + _h(i, 5, 81) * 1.1)
            paint(cv, lambda x, y, cx=cx, cy=cy, r=r: abs(x - cx) + abs(y - cy) * 1.4 < r,
                  lambda x, y, sd=sd: SILVER[4] if (x + y) % 3 else (MINT if sd < 0 else PINK)[2], (60, 40, 80),
                  (cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2))
    def after(cv):
        for x in range(L(TRACK_X), L(TRACK_X + TRACK_W)):
            cv.put(x, L(TRACK_Y) - 1, SILVER[4])
            cv.put(x, L(TRACK_Y + TRACK_H), SILVER[4])

    finish(cv, "bossbar_frame_your_double", None, rim_light=False, after=after)


# ------------------------------------------------------------------ Pressure Leviathan
def pressure_leviathan():
    cv = new()

    def pipe(x, y):
        return ramp(BRASS, clamp(0.92 * math.cos(clamp((y - L(20)) / L(14), -1, 1) * 1.45) ** 0.7 - 0.05 + (fbm(x / 8, y / 3, 91, 2) - 0.5) * 0.15))

    paint(cv, lambda x, y: in_band(x, y, 12, 32, 10, 230), pipe)
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.alpha(x, y) > 200 and fbm(x / 5, y / 5, 93, 3) > 0.67:
                cv.tint(x, y, VERD[2], 0.65)
    for u in range(36, 210, 28):
        paint(cv, lambda x, y, u=u: L(u) <= x < L(u + 5) and L(10) <= y < L(34),
              lambda x, y, u=u: ramp(BRASS, clamp(0.85 - (x - L(u)) / L(5) * 0.55 - (y - L(10)) / L(24) * 0.35)), OUTLINE,
              (L(u) - 1, L(10) - 1, L(u + 5) + 1, L(34) + 1))
        for vy in (11.8, 32.2):
            rivet(cv, L(u + 2.5), L(vy), L(1.0), BRASS)
    for u in (60, 112, 150, 190):
        for j in range(3):
            cv.disc(L(u + j * 2.6), L(32.5), L(0.9 + 0.3 * j), (220, 214, 196))
            cv.put(L(u + j * 2.6), L(32.5), (110, 100, 90))
    # the porthole at the left
    cx, cy = L(LEFT_X), L(21)
    paint(cv, ellipse_in(cx, cy, L(12), L(12)), lit(BRASS, cx, cy, L(12), 0.5))
    paint(cv, ellipse_in(cx, cy, L(8.5), L(8.5)), lambda x, y: mix((40, 150, 190), (2, 20, 40), clamp(math.hypot(x - cx, y - cy - L(3)) / L(9))), OUTLINE)
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        rivet(cv, cx + math.cos(a) * L(10.3), cy + math.sin(a) * L(10.3), L(1.1), BRASS)
    for k in range(3):
        stroke(cv, [(cx - L(5) + k * L(1.6), cy - L(1) - k * L(1.6)), (cx - L(2) + k * L(1.6), cy - L(4) - k * L(1.6))], 0.5, 0.5, (230, 250, 255), 0.6)
    # the pressure dial at the right, its needle deep in the red
    dx, dy = L(RIGHT_X), L(21)
    paint(cv, ellipse_in(dx, dy, L(11), L(11)), lit(BRASS, dx, dy, L(11), 0.5))
    paint(cv, ellipse_in(dx, dy, L(8.5), L(8.5)), lambda x, y: (240, 234, 216) if math.hypot(x - dx, y - dy) < L(7.5) else (60, 40, 20), OUTLINE)
    for i in range(11):
        a = math.radians(135 + i * 27)
        r0 = L(6.2 if i % 2 else 5.4)
        stroke(cv, [(dx + math.cos(a) * r0, dy + math.sin(a) * r0), (dx + math.cos(a) * L(7.2), dy + math.sin(a) * L(7.2))], 0.5, 0.5, (40, 30, 20) if i < 8 else (200, 30, 20))
    for a in range(135 + 8 * 27, 406, 3):
        r = math.radians(a)
        cv.put(dx + math.cos(r) * L(6.8), dy + math.sin(r) * L(6.8), (220, 40, 30))
    na = math.radians(392)
    stroke(cv, [(dx - math.cos(na) * L(1.5), dy - math.sin(na) * L(1.5)), (dx + math.cos(na) * L(6), dy + math.sin(na) * L(6))], 0.9, 0.4, (180, 20, 20))
    rivet(cv, dx, dy, L(1.2), BRASS)
    for i in range(6):
        a = i * math.pi / 3
        rivet(cv, dx + math.cos(a) * L(9.8), dy + math.sin(a) * L(9.8), L(0.8), BRASS)
    finish(cv, "bossbar_frame_pressure_leviathan", BRASS)


# ------------------------------------------------------------------ Seasons Master
def gear(cv, cx, cy, R, n, cols=None):
    cols = cols or BRASS

    def gin(x, y):
        a = math.atan2(y - cy, x - cx)
        rr = R * (1 if math.cos(a * n) > 0.2 else 0.8)
        d = math.hypot(x - cx, y - cy)
        if d >= rr or d < R * 0.22:
            return False
        return not (R * 0.35 < d < R * 0.66 and math.cos(a * 4) < 0.3)

    paint(cv, gin, lambda x, y: ramp(cols, clamp(0.85 - (x - cx + y - cy) / (2.4 * R))), OUTLINE, (cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2))


def seasons_master():
    cv = new()
    for u, v, r, n in ((52, 8, 6, 9), (118, 36, 5.5, 8), (176, 7, 5, 8), (200, 37, 4, 7)):
        gear(cv, L(u), L(v), L(r), n)

    def case(x, y):
        if abs(y - L(22)) > L(7):
            return ramp(BRASS, clamp(0.8 - abs(y - L(22)) / L(10) * 0.6 + (fbm(x / 12, y / 2, 101, 2) - 0.5) * 0.12))
        return ramp(WOOD, 0.3 + fbm(x / 20, y / 1.5, 103, 2) * 0.3)

    paint(cv, lambda x, y: in_band(x, y, 12, 32, 12, 228), case)
    for u in range(20, 224, 8):
        for y in (L(13.5), L(30.5)):
            for k in range(6):
                a = k * math.pi / 5
                cv.put(L(u) + math.cos(a) * L(2), y + math.sin(a) * L(0.8) * (1 if y > L(20) else -1), BRASS[1])
    q = TRACK_W / 4
    for i in range(4):
        cx, cy = L(TRACK_X + q * i + q / 2), L(35)
        paint(cv, ellipse_in(cx, cy, L(4.2), L(4.2)), lambda x, y: (236, 228, 206), BRASS[0])
        for a in range(0, 360, 6):
            r = math.radians(a)
            cv.put(cx + math.cos(r) * L(4.2), cy + math.sin(r) * L(4.2), BRASS[3])
        if i == 0:
            for j in range(5):
                a = j * math.pi * 2 / 5 - math.pi / 2
                cv.disc(cx + math.cos(a) * L(1.5), cy + math.sin(a) * L(1.5), L(1.1), (244, 160, 200))
            cv.disc(cx, cy, L(0.8), (250, 220, 100))
        elif i == 1:
            cv.disc(cx, cy, L(1.8), (255, 200, 60))
            for j in range(8):
                a = j * math.pi / 4
                stroke(cv, [(cx + math.cos(a) * L(2.4), cy + math.sin(a) * L(2.4)), (cx + math.cos(a) * L(3.3), cy + math.sin(a) * L(3.3))], 0.6, 0.4, (240, 170, 40))
        elif i == 2:
            leaf(cv, (cx - L(2.4), cy + L(2)), (cx + L(2.6), cy - L(2.4)), L(1.5), [(120, 40, 10), (200, 90, 20), (240, 150, 50), (255, 200, 110)], OUTLINE)
        else:
            snowflake(cv, cx, cy, L(2.8), (90, 140, 210))
    for i in range(1, 4):
        x = L(TRACK_X + q * i)
        cv.rect(x - 2, L(12), x + 2, L(32), GOLD[4])
    gear(cv, L(LEFT_X), L(21), L(13), 12)
    rivet(cv, L(LEFT_X), L(21), L(2.2), GOLD)
    cx, cy = L(RIGHT_X), L(21)
    paint(cv, ellipse_in(cx, cy, L(12.5), L(12.5)), lit(BRASS, cx, cy, L(12), 0.5))
    paint(cv, ellipse_in(cx, cy, L(9.5), L(9.5)), lambda x, y: mix((250, 246, 232), (214, 200, 170), clamp(math.hypot(x - cx + L(2), y - cy + L(2)) / L(12))), OUTLINE)
    for i in range(12):
        a = i * math.pi / 6
        r0 = L(7.0 if i % 3 else 6.0)
        stroke(cv, [(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * L(8.6), cy + math.sin(a) * L(8.6))], 0.9 if i % 3 == 0 else 0.5, 0.5, OUTLINE)
    rivet(cv, cx, cy, L(1.1), GOLD)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        rivet(cv, cx + math.cos(a) * L(11), cy + math.sin(a) * L(11), L(0.9), BRASS)
    finish(cv, "bossbar_frame_seasons_master", BRASS)


# ------------------------------------------------------------------ Terrain Heart
def terrain_heart_boss():
    cv = new()

    def inside(x, y):
        u, v = x / S, y / S
        if not 4 <= u < 236:
            return False
        e = min(u - 4, 236 - u)
        top = 11 - 3 * fbm(u / 6, 0, 111, 3) - (2 if _h(int(u // 9), 0, 113) > 0.7 else 0) + max(0, 6 - e) * 0.6
        bot = 33 + 3 * fbm(u / 6, 9, 111, 3) - max(0, 6 - e) * 0.6
        return top <= v < bot

    def color(x, y):
        u, v = x / S, y / S
        strata = v + 2.5 * math.sin(u / 17) + 1.5 * fbm(u / 8, v / 3, 115, 2)
        t = 0.25 + 0.3 * ((strata / 4) % 1) + (fbm(x / 3, y / 3, 117, 2) - 0.5) * 0.3 - (v - 22) / 40
        return ramp(ROCK, clamp(t))

    paint(cv, inside, color)
    for i in range(6):
        y = L(12 + i * 4)
        pts = [(L(8), y)]
        x = L(8)
        while x < L(232):
            x += L(4 + 5 * _h(int(x), i, 119))
            y = clamp(y + L((_h(int(x), i, 121) - 0.5) * 5), L(11), L(33))
            pts.append((x, y))
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if not (in_track(ax, ay, L(3)) or in_track(bx, by, L(3))):
                glow_line(cv, [(ax, ay), (bx, by)], (230, 50, 40), 0.55, 0.75)

    def crystals(cx, cy, up, specs):
        for dx, h, w in specs:
            x0 = cx + L(dx)
            paint(cv, lambda x, y, x0=x0, h=h, w=w: abs(x - x0) <= L(w) * (1 - abs(y - cy) / L(h)) and ((cy - L(h) <= y <= cy) if up else (cy <= y <= cy + L(h))),
                  lambda x, y, x0=x0, w=w: ramp(CRYST, clamp(0.85 - (x - x0) / L(w * 2) - 0.1)), OUTLINE, (x0 - L(w) - 2, cy - L(h) - 2, x0 + L(w) + 2, cy + L(h) + 2))

    for u, up in ((70, 1), (128, 0), (176, 1)):
        crystals(L(u), L(12) if up else L(32), up, ((-1.8, 4, 1.1), (0, 6.5, 1.4), (2, 3.5, 1)))
    cx, cy = L(LEFT_X), L(21)
    paint(cv, ellipse_in(cx, cy, L(12), L(14)), lit(ROCK, cx, cy, L(13), 0.4))
    paint(cv, ellipse_in(cx, cy, L(8.5), L(10.5)), lambda x, y: ramp(CRYST, clamp(0.3 + _h(int(x / 4), int(y / 4), 127) * 0.4)), OUTLINE)

    def heart(x, y):
        dx, dy = (x - cx) / L(5.6), (y - cy - L(1)) / L(5.6)
        return (dx * dx + dy * dy - 1) ** 3 - dx * dx * (-dy) ** 3 < 0

    cv.glow(cx, cy, L(14), (255, 60, 40), 0.35)
    paint(cv, heart, lambda x, y: mix((255, 200, 180), (150, 10, 20), clamp(math.hypot(x - cx + L(2), y - cy + L(2)) / L(7))), (60, 4, 10))
    rx = L(RIGHT_X)
    paint(cv, ellipse_in(rx, L(24), L(11), L(11)), lit(ROCK, rx, L(24), L(11), 0.4))
    crystals(rx, L(22), 1, ((-5, 10, 2.2), (0, 18, 2.8), (5, 12, 2.2), (-8, 6, 1.4), (8, 7, 1.5)))
    finish(cv, "bossbar_frame_terrain_heart_boss", ROCK)


# ------------------------------------------------------------------ The Unfinished
def half_doll(cv, cx, cy, painted, side):
    """A matryoshka standing at an end of the bar: painted in lacquer and gold, or still a pencil sketch on wood."""
    hx, hy, hr = cx, cy - L(8), L(6)
    bx, by, brx, bry = cx, cy + L(5), L(9), L(12)

    def body(x, y):
        return ((x - hx) / hr) ** 2 + ((y - hy) / (hr * 1.05)) ** 2 <= 1 or ((x - bx) / brx) ** 2 + ((y - by) / bry) ** 2 <= 1 and y < cy + L(15)

    if painted:
        paint(cv, body, lambda x, y: ramp(RED[1:], clamp(0.85 - (x - cx + y - cy) / L(30) - abs(x - cx) / L(20))))
        paint(cv, ellipse_in(hx, hy + L(0.5), L(3.8), L(4)), lambda x, y: mix(SKIN, (220, 170, 140), clamp((x - hx + y - hy) / L(10) + 0.3)), (120, 60, 40))
        cv.put(hx - L(1.3), hy, OUTLINE)
        cv.put(hx + L(1.3), hy, OUTLINE)
        cv.disc(hx - L(2), hy + L(1.8), L(0.7), (230, 110, 100))
        cv.disc(hx + L(2), hy + L(1.8), L(0.7), (230, 110, 100))
        cv.put(hx, hy + L(2.4), (180, 40, 40))
        paint(cv, ellipse_in(bx, by + L(1), L(5.5), L(7)), lambda x, y: (252, 236, 206), GOLD[1])
        rosette(cv, bx, by, L(2.6))
        for a in (-0.9, 0.9, math.pi - 0.9, math.pi + 0.9):
            leaf(cv, (bx, by), (bx + math.cos(a) * L(4.5), by + math.sin(a) * L(5)), L(1.0), GOLD[2:6], OUTLINE)
        for x in range(int(cx - L(9)), int(cx + L(9))):
            if cv.alpha(x, int(cy - L(2))) > 200:
                cv.put(x, cy - L(2), GOLD[4])
    else:
        paint(cv, body, lambda x, y: ramp(RAWWOOD, clamp(0.75 - (x - cx + y - cy) / L(34))), (120, 90, 60))
        for a in range(0, 360, 4):
            r = math.radians(a)
            cv.put(hx + math.cos(r) * L(3.8), hy + L(0.5) + math.sin(r) * L(4), PENCIL, 0.8)
            cv.put(bx + math.cos(r) * L(5.5), by + L(1) + math.sin(r) * L(7), PENCIL, 0.7)
        cv.put(hx - L(1.3), hy, PENCIL)
        cv.put(hx + L(1.3), hy, PENCIL)
        for k in range(8):
            a = k * math.pi / 4
            stroke(cv, [(bx, by), (bx + math.cos(a) * L(3), by + math.sin(a) * L(3))], 0.4, 0.4, PENCIL, 0.7)
        for x in range(int(cx - L(9)), int(cx + L(9)), 3):
            cv.put(x, cy - L(2), PENCIL, 0.8)
        for k in range(6):
            x = cx + side * L(4 + k)
            stroke(cv, [(x, cy + L(2)), (x - L(2), cy + L(8))], 0.35, 0.35, PENCIL, 0.5)


def the_unfinished():
    cv = new()

    def done(x, y):
        return clamp((190 - x / S) / 60 + (fbm(x / 9, y / 9, 131, 3) - 0.5) * 0.6)

    def color(x, y):
        f = done(x, y)
        lac = ramp(RED[1:], clamp(0.55 - (y - L(22)) / L(22) + (fbm(x / 20, y / 2, 133, 2) - 0.5) * 0.15))
        raw = ramp(RAWWOOD, clamp(0.5 + (fbm(x / 30, y / 1.2, 135, 2) - 0.5) * 0.6))
        return mix(raw, lac, smooth(clamp((f - 0.4) / 0.2)))

    paint(cv, lambda x, y: in_band(x, y, 12, 32, 14, 226), color)
    for x in range(L(14), L(226)):
        for y in (L(13.5), L(30.5)):
            if done(x, y) > 0.5:
                cv.put(x, y, GOLD[4])
            elif x % 3:
                cv.put(x, y, PENCIL, 0.7)
    for i, u in enumerate(range(30, 214, 14)):
        cx, cy = L(u), L(14.8) if i % 2 else L(29.2)
        if done(cx, cy) > 0.55:
            leaf(cv, (cx - L(3.5), cy), (cx + L(3.5), cy), L(1.1), GOLD[2:6], OUTLINE)
            berry(cv, cx + L(4.5), cy, L(1.0))
        else:
            for t in range(13):
                cv.put(cx - L(3.5) + t * L(7) / 12, cy + math.sin(t / 12 * math.pi) * L(1.1), PENCIL, 0.8)
            for t in range(12):
                cv.put(cx + L(4.5) + math.cos(t / 2) * L(1), cy + math.sin(t / 2) * L(1), PENCIL, 0.7)
    half_doll(cv, L(LEFT_X), L(22), True, -1)
    half_doll(cv, L(RIGHT_X), L(22), False, 1)
    tube(cv, [(L(186), L(9)), (L(214), L(4))], L(1.1), L(0.8), WOOD[1:])
    cv.rect(L(184), L(8), L(188), L(10.4), SILVER[2])
    for t in range(9):
        cv.disc(L(184) - t * 2, L(9.3) + t * 0.3, L(1.3) * (1 - t / 11), RED[3] if t > 2 else (210, 196, 176))
    spindle(cv, L(40), L(7), L(9))
    finish(cv, "bossbar_frame_the_unfinished", [scale_c(c, 0.85) for c in GOLD[1:]])


FRAMES = {
    "block_guardian": block_guardian, "spore_queen": spore_queen, "ash_titan": ash_titan,
    "grand_jailer": grand_jailer, "storm_king": storm_king, "light_eater": light_eater,
    "your_double": your_double, "pressure_leviathan": pressure_leviathan, "seasons_master": seasons_master,
    "terrain_heart_boss": terrain_heart_boss, "the_unfinished": the_unfinished,
}


# ------------------------------------------------------------------ the name plates
def plate_simple(bid, cols, seed, trim=None, notch=False):
    cv = Cv(L(48), L(16))

    def inside(x, y):
        if notch and (x < L(3) or x >= cv.w - L(3)):
            return abs(y - cv.h / 2) < (min(x, cv.w - x) / L(3)) * cv.h / 2
        return 1 <= x < cv.w - 1 and 1 <= y < cv.h - 1

    shape(cv, inside, (0, 0, cv.w, cv.h), noise_mat(cols, seed, 5, 3, 0.45, 0.3, 0.0), OUTLINE)
    for y in range(cv.h):
        for x in range(cv.w):
            cv.mul(x, y, 1.15 - y / cv.h * 0.35)
    if trim:
        for x in range(L(3), cv.w - L(3)):
            if (x // 3) % 2 == 0:
                cv.put(x, L(2), trim)
                cv.put(x, cv.h - L(2) - 1, trim)
    for x in range(2, cv.w - 2):
        cv.put(x, 2, (255, 255, 255), 0.2)
    blocky(cv, 16, False)
    save("bossbar_plate_" + bid, cv, border={"left": 5, "top": 5, "right": 5, "bottom": 5})


def plate_smoke():
    cv = Cv(L(48), L(16))
    # a slab of the dark, ragged at its ends, a violet seam along it
    def inside(x, y):
        e = min(x, cv.w - x)
        return 1 <= y < cv.h - 1 and e > L(2) * (1 - abs(y - cv.h / 2) / (cv.h / 2)) + _h(int(y), 0, 177) * L(1.5)
    shape(cv, inside, (0, 0, cv.w, cv.h), lambda x, y: ramp(VOID, clamp(0.5 + (fbm(x / 4, y / 3, 179, 2) - 0.5) * 0.8)), (2, 0, 6))
    for x in range(L(3), cv.w - L(3)):
        if x % 4:
            cv.put(x, cv.h - L(2) - 1, VIOLET)
        cv.put(x, L(2), (60, 40, 110))
    blocky(cv, 10, False)
    save("bossbar_plate_light_eater", cv, border={"left": 6, "top": 5, "right": 6, "bottom": 5})


def plate_mirror():
    cv = Cv(L(48), L(16))
    mid = cv.h / 2
    shape(cv, lambda x, y: 1 <= y < cv.h - 1 and abs(y - mid) < min(mid, 2 + min(x, cv.w - x) * 0.9), (0, 0, cv.w, cv.h),
          lambda x, y: scale_c(ramp(MINT if y < mid else PINK, clamp(0.3 + abs(y - mid) / mid * 0.4)), 0.42), (230, 236, 244))
    for x in range(cv.w):
        cv.put(x, int(mid), SILVER[5], 0.5)
    blocky(cv, 12, False)
    save("bossbar_plate_your_double", cv, border={"left": 6, "top": 5, "right": 6, "bottom": 5})


def plate_paper():
    cv = Cv(L(48), L(16))
    paper(cv, 1, 1, cv.w - 1, cv.h - 1, 141)
    cv.disc(L(3), cv.h / 2, L(1.3), RED[3])
    cv.put(L(3) - 1, cv.h / 2 - 1, (255, 200, 190))
    blocky(cv, 12, False)
    save("bossbar_plate_the_unfinished", cv, border={"left": 6, "top": 5, "right": 5, "bottom": 5})


PLATES = {
    "block_guardian": lambda: plate_simple("block_guardian", STONE, 151, trim=MOSS[3]),
    "spore_queen": lambda: plate_simple("spore_queen", CHITIN, 153, trim=TOXIN, notch=True),
    "ash_titan": lambda: plate_simple("ash_titan", SOOT, 155, trim=HOT[2]),
    "grand_jailer": lambda: plate_simple("grand_jailer", GAOL, 157, trim=GAOL[5]),
    "storm_king": lambda: plate_simple("storm_king", SLATE, 159, trim=(255, 225, 74), notch=True),
    "light_eater": plate_smoke,
    "your_double": plate_mirror,
    "pressure_leviathan": lambda: plate_simple("pressure_leviathan", BRASS, 161, trim=VERD[3]),
    "seasons_master": lambda: plate_simple("seasons_master", BRASS, 163, trim=WOOD[2]),
    "terrain_heart_boss": lambda: plate_simple("terrain_heart_boss", ROCK, 165, trim=(230, 50, 40), notch=True),
    "the_unfinished": plate_paper,
}


# ------------------------------------------------------------------ the ornaments on each side of the name
def cap(bid):
    """bossbar_cap_<id> (12 x 16), set at the left of the name plate; bossbar_cap_<id>_r, its mirror, at the right."""
    cv = Cv(L(12), L(16))
    cx, cy = L(6), L(8)
    if bid == "block_guardian":
        paint(cv, lambda x, y: abs(x - cx) < L(4.2) and abs(y - cy) < L(4.2), lambda x, y: ramp(STONE, 0.8 - (y - cy + L(4)) / L(8) * 0.5 - (x - cx) / L(16)))
        cv.rect(cx - L(4.2) + 1, cy - L(4.2) + 1, cx + L(4.2) - 1, cy - L(2.8), MOSS[3])
        cv.glow(cx, cy + L(0.5), L(3.5), (90, 230, 240), 0.5)
        cv.disc(cx, cy + L(0.5), L(1), (160, 250, 255))
    elif bid == "spore_queen":
        mushroom(cv, cx, L(14), L(5), L(6), 0.3, 171)
    elif bid == "ash_titan":
        def hexn(x, y):
            a = math.atan2(y - cy, x - cx)
            return math.hypot(x - cx, y - cy) < L(4.6) * (0.92 + 0.08 * math.cos(6 * a))
        paint(cv, hexn, lit(SOOT, cx, cy, L(4.6), 0.4))
        cv.glow(cx, cy, L(4), HOT[2], 0.6)
        cv.disc(cx, cy, L(1.6), HOT[3])
    elif bid == "grand_jailer":
        key_shape(cv, cx, L(2), 1.0 * S / 2 * 1.4, [(30, 24, 14)] + GOLD[1:])
    elif bid == "storm_king":
        cv.glow(cx, cy, L(6), (255, 225, 74), 0.35)
        bolt(cv, [(cx + L(2), L(1)), (cx - L(2), L(8)), (cx + L(1.5), L(8.5)), (cx - L(2.5), L(15))])
    elif bid == "light_eater":
        cv.glow(cx, cy, L(6), VIOLET, 0.5)
        paint(cv, lambda x, y: abs(x - cx) < L(5) and abs(y - cy) < L(2.6) * (1 - ((x - cx) / L(5)) ** 2), lambda x, y: (200, 170, 255), (20, 8, 40))
        paint(cv, lambda x, y: abs(x - cx) < L(0.6) and abs(y - cy) < L(2.2), lambda x, y: (2, 0, 8), None)
    elif bid == "your_double":
        def gem(x, y):
            return abs(x - cx) / L(3.6) + abs(y - cy) / L(6.5) < 1
        paint(cv, gem, lambda x, y: ramp(MINT if y < cy else PINK, 0.8 if x < cx else 0.35), (60, 40, 80))
        star(cv, cx - L(1), cy - L(2.5), L(1.6), (255, 255, 255))
    elif bid == "pressure_leviathan":
        for a in range(0, 360, 5):
            r = math.radians(a)
            cv.disc(cx + math.cos(r) * L(4), cy + math.sin(r) * L(4), L(0.8), BRASS[3 if a > 180 else 2])
        for k in range(4):
            a = k * math.pi / 4
            stroke(cv, [(cx - math.cos(a) * L(4), cy - math.sin(a) * L(4)), (cx + math.cos(a) * L(4), cy + math.sin(a) * L(4))], 0.7, 0.7, BRASS[2])
        rivet(cv, cx, cy, L(1.4), [(140, 20, 10), (180, 30, 20), (220, 60, 40), (240, 110, 80), (255, 180, 150), (255, 230, 220)])
    elif bid == "seasons_master":
        gear(cv, cx, cy, L(5), 8)
        rivet(cv, cx, cy, L(1), GOLD)
    elif bid == "terrain_heart_boss":
        for dx, h, w in ((-2.2, 6, 1.4), (0, 9, 1.8), (2.4, 5, 1.3)):
            x0 = cx + L(dx)
            paint(cv, lambda x, y, x0=x0, h=h, w=w: abs(x - x0) <= L(w) * (L(14) - y) / L(h) and L(14) - L(h) <= y <= L(14),
                  lambda x, y, x0=x0, w=w: ramp(CRYST, clamp(0.85 - (x - x0) / L(w * 2) - 0.1)), OUTLINE)
    else:
        spindle(cv, cx, cy, L(12))
    blocky(cv, 12)
    save("bossbar_cap_" + bid, cv)
    m = Cv(cv.w, cv.h)
    m.im = cv.im.transpose(0)
    m.p = m.im.load()
    save("bossbar_cap_" + bid + "_r", m)
