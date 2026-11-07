"""Per-station GUI skins for Matriochka: each station's recipe rows are made of its own material, and its niche
holds its own instrument (painted here, animated by StationScreen).

The rows keep the drawer's zones: result cartouche 3..33, ingredients from 38, a progress groove at y 18 and the
automation funnel at 161. Called from gui.build() with gui's namespace, so it paints with the same tools and its
sprites are saved (and kept) like the others.
"""
import math


def build(ns):
    mine = globals()
    mine.update({k: v for k, v in ns.items() if not k.startswith("__") and k not in mine})
    station_rows()
    station_gauges()
    tile_sprites()
    decor_sprites()
    boss_bars()


IRONS = [(22, 24, 30), (44, 48, 58), (72, 78, 90), (108, 114, 128), (150, 156, 170), (196, 202, 214)]
COPPER = [(60, 26, 14), (110, 52, 26), (160, 86, 44), (200, 122, 66), (230, 166, 104), (250, 210, 160)]
OBSID = [(6, 4, 12), (14, 10, 26), (24, 16, 42), (38, 26, 64), (60, 42, 96), (100, 80, 150)]
STONE = [(40, 34, 32), (66, 58, 54), (96, 86, 80), (128, 118, 108), (162, 152, 140), (200, 190, 176)]
BRASS = [(64, 44, 14), (120, 88, 30), (170, 130, 52), (206, 168, 84), (232, 204, 128), (250, 234, 180)]
MOSSWOOD = [(30, 34, 16), (52, 60, 26), (78, 88, 40), (104, 116, 56), (136, 150, 78), (176, 190, 110)]

# per station: row material ramp (None: painted specially), grain (lacquered wood), the knob and the edge detail
ROW_SKIN = {
    "spore_vat": dict(mat=MOSSWOOD, grain=True, knob="bubble", edge="hoop"),
    "ash_foundry": dict(mat=IRONS, grain=False, knob="ember", edge="rivet"),
    "jailer_table": dict(mat=IRONS, grain=False, knob="keyhole", edge="bars"),
    "lightning_forge": dict(mat=COPPER, grain=False, knob="spark", edge="coil"),
    "dark_altar": dict(mat=OBSID, grain=False, knob="eye", edge="rune"),
    "inverter": dict(mat=None, grain=False, knob="swap", edge="mirror"),
    "abyssal_press": dict(mat=IRONS, grain=False, knob="porthole", edge="rivet"),
    "time_workshop": dict(mat=BRASS, grain=False, knob="gear", edge="ticks"),
    "terrain_anchor": dict(mat=STONE, grain=False, knob="stone", edge="strata"),
    "final_loom": dict(mat=None, grain=False, knob="spool", edge="weave"),
}


def world_of(sid):
    return [st[3] for st in STATIONS if st[0] == sid][0]


def _metal(cv, x0, y0, x1, y1, cols, seed, brushed=True):
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            n = fbm((x - x0) / (40 if brushed else 10), (y - y0) / (3 if brushed else 10), seed, 3)
            t = 0.35 + (n - 0.5) * 0.45 + 0.25 * (1 - (y - y0) / max(1, y1 - y0))
            cv.put(x, y, ramp(cols, clamp(t)))


def _knob(cv, kind, x, y, st, ready):
    g = st["liquid"]
    if kind == "bubble":
        cv.disc(x, y, 5.2, OUTLINE)
        cv.disc(x, y, 4.2, scale_c(g, 0.6 if not ready else 1.0))
        cv.disc(x - 1.2, y - 1.2, 1.6, mix(g, (255, 255, 255), 0.6))
    elif kind == "ember":
        rivet(cv, x, y, 4.6, IRONS[1:])
        cv.disc(x, y, 2.4, (255, 140, 40) if ready else (120, 40, 20))
    elif kind == "keyhole":
        rivet(cv, x, y, 4.6, GOLD[1:])
        cv.disc(x, y - 1, 1.4, OUTLINE)
        cv.rect(x - 0.8, y - 1, x + 1, y + 3, OUTLINE)
    elif kind == "spark":
        cv.disc(x, y, 4.6, scale_c(COPPER[2], 0.7))
        bolt(cv, [(x + 1, y - 5), (x - 2, y), (x + 1, y), (x - 1, y + 5)])
    elif kind == "eye":
        for k in range(-5, 6):
            h = 2.6 * (1 - (k / 5.5) ** 2)
            for dy in range(int(-h), int(h) + 1):
                cv.put(x + k, y + dy, (200, 190, 240) if ready else OBSID[4])
        cv.disc(x, y, 1.6, OUTLINE)
    elif kind == "swap":
        cv.disc(x, y, 4.8, (200, 74, 216))
        for yy in range(int(y - 5), int(y + 6)):
            for xx in range(int(x), int(x + 6)):
                if (xx + .5 - x) ** 2 + (yy + .5 - y) ** 2 <= 4.8 ** 2:
                    cv.put(xx, yy, (60, 200, 190))
        cv.disc(x, y - 2.4, 1.2, (60, 200, 190))
        cv.disc(x, y + 2.4, 1.2, (200, 74, 216))
    elif kind == "porthole":
        cv.disc(x, y, 5.4, IRONS[1])
        cv.disc(x, y, 4.2, IRONS[4])
        cv.disc(x, y, 3.2, (20, 90, 110) if not ready else (90, 220, 230))
        cv.disc(x - 1, y - 1, 1.0, (220, 250, 255), 0.7)
    elif kind == "gear":
        for k in range(8):
            a = k * math.pi / 4
            cv.disc(x + math.cos(a) * 4.2, y + math.sin(a) * 4.2, 1.4, BRASS[3])
        cv.disc(x, y, 4.0, BRASS[2])
        cv.disc(x, y, 1.6, BRASS[0])
    elif kind == "stone":
        rock(cv, x, y, 4.6, 7)
    elif kind == "spool":
        spindle(cv, x, y, 10, thread=(214, 66, 44))


def _edge(cv, kind, W, H):
    if kind == "hoop":
        for x0 in (10 * S, 150 * S):
            _metal(cv, x0, 1, x0 + 5, H - 1, IRONS[1:], 3)
    elif kind == "rivet":
        for x in range(6, W - 6, 28):
            for y in (4, H - 5):
                rivet(cv, x, y, 1.6, IRONS[1:])
    elif kind == "bars":
        for x in range(36 * S, 160 * S, 18 * S):
            cv.rect(x, 2, x + 3, H - 2, IRONS[0])
            cv.rect(x + 1, 2, x + 2, H - 2, IRONS[4], 0.6)
    elif kind == "coil":
        for x in range(4, W - 4, 6):
            cv.rect(x, 2, x + 3, 4, COPPER[4])
            cv.rect(x, H - 4, x + 3, H - 2, COPPER[4])
    elif kind == "rune":
        g = (150, 110, 255)
        for i, x in enumerate(range(40 * S, 160 * S, 22 * S)):
            cv.rect(x, 4, x + 1, 9, g, 0.55)
            cv.rect(x - 2, 6 + (i % 2) * 2, x + 3, 7 + (i % 2) * 2, g, 0.55)
    elif kind == "ticks":
        for i, x in enumerate(range(4, W - 4, 5)):
            cv.rect(x, 2, x + 1, 5 if i % 6 else 7, BRASS[0])
    elif kind == "strata":
        for k, y in enumerate((7, 15, 29)):
            for x in range(W):
                yy = y + int(2 * math.sin(x / 23.0 + k))
                cv.put(x, yy, STONE[0], 0.6)
                cv.put(x, yy + 1, STONE[4], 0.35)
    elif kind == "mirror":
        for y in range(2, H - 2):
            cv.put(W // 2, y, (240, 230, 250), 0.7)


def station_rows():
    W, H = 174 * S, 21 * S
    for sid, skin in ROW_SKIN.items():
        st = world_style(world_of(sid))
        for ready in (False, True):
            cv = Cv(W, H)
            if sid == "inverter":
                for y in range(H):
                    for x in range(W):
                        n = fbm(x / 40, y / 6, 9, 3)
                        cv.put(x, y, scale_c(mix((120, 40, 150), (30, 130, 130), clamp(x / W * 1.6 - 0.3)), 0.55 + n * 0.35))
                cols = [(40, 14, 54), (80, 30, 100), (150, 70, 180), (190, 120, 220), (230, 200, 250)]
            elif sid == "final_loom":
                # undyed linen with the ten worlds' warp threads running through it
                bands = [world_style(k)["accent"] for k in range(1, 11)]
                for y in range(H):
                    for x in range(W):
                        n = fbm(x / 30, y / 4, 21, 2)
                        c = mix((150, 124, 92), (196, 170, 128), n)
                        if ((x // 3) + (y // 3)) % 2:
                            c = scale_c(c, 0.9)
                        if x % 34 in (0, 1, 2):
                            c = mix(c, bands[(x // 34) % 10], 0.75)
                        cv.put(x, y, c)
                cols = WOOD[1:]
            else:
                cols = skin["mat"]
                if skin["grain"]:
                    lacquer(cv, 0, 0, W, H, cols[1:], 71, 0.7, 0.06, wood=(40, 30, 14))
                else:
                    _metal(cv, 0, 0, W, H, cols, 61 + world_of(sid), brushed=sid not in ("terrain_anchor", "dark_altar"))
            if ready:
                for y in range(H):
                    for x in range(W):
                        cv.tint(x, y, st["liquid"], 0.18)
            _edge(cv, skin["edge"], W, H)
            for x in range(W):
                cv.put(x, 0, OUTLINE)
                cv.put(x, H - 1, OUTLINE)
                cv.put(x, 1, cols[-1], 0.7)
                cv.put(x, H - 2, scale_c(cols[0], 0.8))
            for y in range(H):
                cv.put(0, y, OUTLINE)
                cv.put(W - 1, y, OUTLINE)
            # the result cartouche: a recess framed in the station's metal
            x0, x1 = 3 * S, 33 * S
            frame = GOLD if sid in ("time_workshop", "final_loom", "jailer_table", "spore_vat") else \
                COPPER if sid == "lightning_forge" else OBSID if sid == "dark_altar" else IRONS
            for y in range(3, H - 3):
                for x in range(x0, x1):
                    d = min(x - x0, y - 3, x1 - 1 - x, H - 4 - y)
                    if d < 2:
                        cv.put(x, y, ramp(frame, 0.85 if (d == 0) != ((x - x0) > (y - 3)) else 0.3))
                    else:
                        cv.put(x, y, scale_c(st["enamel"], 0.7) if not ready else mix(st["enamel"], st["liquid"], 0.45))
            for x in range(38 * S, 162 * S):
                cv.put(x, 18 * S - 1, OUTLINE)
                cv.put(x, 18 * S, (14, 10, 8))
                cv.put(x, 18 * S + 1, (22, 16, 12))
            _knob(cv, skin["knob"], 168 * S, H / 2, st, ready)
            save("row_" + sid + ("_ready" if ready else ""), cv)


def _dial_face(cv, cx, cy, r, face, rim):
    cv.disc(cx, cy, r + 2, OUTLINE)
    for y in range(int(cy - r - 2), int(cy + r + 2)):
        for x in range(int(cx - r - 2), int(cx + r + 2)):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if r - 2 < d <= r + 1:
                cv.put(x, y, ramp(rim, clamp(0.3 + 0.6 * (1 - (y - cy + r) / (2 * r)))))
            elif d <= r - 2:
                cv.put(x, y, mix(face, (0, 0, 0), 0.25 * d / r))


def station_gauges():
    """The instrument in each station's niche, 48x56 logical."""
    W, H = 48 * S, 56 * S
    cx = W / 2
    for sid, _en, _fr, w, *_ in STATIONS:
        if sid in ("soul_altar", "class_table", "inverter"):
            continue
        st = world_style(w)
        cv = Cv(W, H)
        if sid == "matrix_workbench":
            # a lacquer plate holding a 3 x 3 matrix of core sockets
            lacquer(cv, 4, 6, W - 4, H - 6, RED[1:], 3, 0.4, 0.1)
            thin_gilt(cv, 4, 6, W - 4, H - 6)
            for i in range(3):
                for j in range(3):
                    x, y = 18 + i * 30, 26 + j * 30
                    cv.disc(x, y, 10, OUTLINE)
                    cv.disc(x, y, 8.5, GOLD[2])
                    cv.disc(x, y, 6.5, (30, 10, 8))
        elif sid == "spore_vat":
            # a riveted porthole into the vat, the marks for fresh, ripe and aged on its left
            _metal(cv, 2, 2, W - 2, H - 2, IRONS[1:], 5)
            cv.disc(cx + 4, 52, 38, OUTLINE)
            cv.disc(cx + 4, 52, 35, IRONS[3])
            cv.disc(cx + 4, 52, 30, (16, 24, 12))
            for k in range(10):
                a = k * math.pi / 5
                rivet(cv, cx + 4 + math.cos(a) * 33, 52 + math.sin(a) * 33, 1.8, IRONS[1:])
            for k, y in enumerate((80, 56, 32)):
                cv.rect(4, y, 12, y + 3, st["liquid"] if k else (200, 200, 200))
        elif sid == "ash_foundry":
            # a thermometer dial: cold blue, the green band, too hot red
            _dial_face(cv, cx, 56, 42, (30, 24, 22), IRONS)
            for k in range(81):
                a = math.pi + k * math.pi / 80
                t = k / 80
                col = (70, 110, 200) if t < 1 / 6 else (90, 200, 80) if t <= 3 / 6 else (220, 60, 30)
                for rr in range(31, 38):
                    cv.put(cx + math.cos(a) * rr, 56 + math.sin(a) * rr, col)
            cv.rect(14, 74, W - 14, 100, (24, 18, 16))
            thin_gilt(cv, 14, 74, W - 14, 100)
        elif sid == "jailer_table":
            # the lock face: a gold escutcheon, the keyhole, three tumbler windows
            shape(cv, lambda x, y: ((x - cx) / 44) ** 2 + ((y - 54) / 52) ** 2 <= 1, (0, 0, W, H),
                  lambda x, y: gold_tone(x, y, 0.75 - y / H * 0.4, 5, False), OUTLINE)
            cv.disc(cx, 30, 7, OUTLINE)
            cv.rect(cx - 4, 30, cx + 4, 50, OUTLINE)
            for k in range(3):
                cv.rect(12 + k * 26, 66, 32 + k * 26, 88, OUTLINE)
                cv.rect(14 + k * 26, 68, 30 + k * 26, 86, (40, 26, 14))
        elif sid == "lightning_forge":
            # a bank of eight capacitor cells under a copper bus bar
            _metal(cv, 2, 2, W - 2, H - 2, COPPER[:5], 7)
            cv.rect(6, 8, W - 6, 16, COPPER[4])
            for k in range(8):
                x = 7 + (k % 4) * 21
                y = 24 + (k // 4) * 42
                cv.rect(x, y, x + 18, y + 36, OUTLINE)
                cv.rect(x + 2, y + 2, x + 16, y + 34, (14, 20, 34))
                cv.rect(x + 6, y - 6, x + 12, y, COPPER[3])
        elif sid == "dark_altar":
            # an obsidian roundel ringed with runes; the eye inside opens in the dark
            _metal(cv, 2, 2, W - 2, H - 2, OBSID, 9, brushed=False)
            cv.disc(cx, 52, 38, OUTLINE)
            cv.disc(cx, 52, 35, OBSID[2])
            for k in range(12):
                a = k * math.pi / 6
                x, y = cx + math.cos(a) * 41, 52 + math.sin(a) * 41
                cv.rect(x - 1, y - 1, x + 2, y + 2, (120, 90, 220))
        elif sid == "abyssal_press":
            # a depth gauge: a dial over a glass water column
            _metal(cv, 2, 2, W - 2, H - 2, IRONS[1:], 11)
            _dial_face(cv, cx, 34, 26, (210, 220, 214), IRONS)
            for k in range(9):
                a = math.pi * 0.75 + k * math.pi * 1.5 / 8
                x, y = cx + math.cos(a) * 20, 34 + math.sin(a) * 20
                cv.rect(x - 1, y - 1, x + 1, y + 1, OUTLINE)
            cv.rect(32, 66, W - 32, 106, OUTLINE)
            cv.rect(34, 68, W - 34, 104, (14, 30, 40))
        elif sid == "time_workshop":
            # a clock face with the dawn and dusk windows marked gold
            _dial_face(cv, cx, 56, 44, PAPER[3], BRASS)
            for k in range(24):
                a = -math.pi / 2 + k * math.pi / 12
                lit = k in (23, 0, 1, 11, 12, 13)
                r0 = 30 if k % 6 else 25
                for rr in range(r0, 38):
                    cv.put(cx + math.cos(a) * rr, 56 + math.sin(a) * rr, (230, 150, 40) if lit else OUTLINE)
        elif sid == "terrain_anchor":
            # a seismograph: a paper strip in a stone frame
            _metal(cv, 2, 2, W - 2, H - 2, STONE, 13, brushed=False)
            paper(cv, 8, 14, W - 8, H - 14, 4)
            for y in range(24, H - 20, 12):
                cv.rect(10, y, W - 10, y + 1, PAPER[1])
        elif sid == "final_loom":
            # a warp of the ten worlds' threads on a wooden frame
            lacquer(cv, 2, 2, W - 2, H - 2, WOOD[1:], 15, 0.7, 0.05)
            cv.rect(10, 10, W - 10, H - 10, (30, 18, 10))
            for k in range(10):
                x = 13 + k * 7
                cv.rect(x, 12, x + 4, H - 12, world_style(k + 1)["accent"])
            cv.rect(6, 6, W - 6, 12, WOOD[3])
            cv.rect(6, H - 12, W - 6, H - 6, WOOD[3])
        save("gauge_" + sid, cv)


# =================================================================== the recipe pieces and the backdrops
# Every station but the workbench lays its recipes out its own way (StationScreen / StationLayouts): jars on a
# shelf, crucibles, keys on a ring, plates over an anvil, runes in a circle, portholes, clock medallions, strata,
# banners. tile_<sid>[_ready] is one recipe piece, decor_<sid> the 180 x 88 backdrop under them.
TILES = {
    "spore_vat": (26, 38), "ash_foundry": (30, 36), "jailer_table": (22, 38), "lightning_forge": (26, 26),
    "dark_altar": (22, 22), "inverter": (84, 20), "abyssal_press": (24, 24), "time_workshop": (24, 24),
    "terrain_anchor": (56, 26), "final_loom": (22, 58),
}


def _disc_plate(cv, cx, cy, r, rim, face, inner=None):
    cv.disc(cx, cy, r, OUTLINE)
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if d < r - 1:
                if d > r - 4:
                    cv.put(x, y, ramp(rim, clamp(0.75 - (y - cy) / r * 0.35 - (x - cx) / r * 0.15)))
                else:
                    cv.put(x, y, mix(face, (0, 0, 0), 0.35 * d / r) if inner is None else inner(x, y, d))


def tile_sprites():
    for sid, (lw, lh) in TILES.items():
        st = world_style(world_of(sid))
        liq = st["liquid"]
        for ready in (False, True):
            W, H = lw * S, lh * S
            cv = Cv(W, H)
            cx, cy = W / 2, H / 2
            if sid == "spore_vat":
                # a stoppered glass jar, the brew inside lit when the recipe is ready
                def inside(x, y):
                    return 4 <= x < W - 4 and 16 <= y < H - 3 and not ((x < 9 or x >= W - 9) and (y < 21 or y >= H - 8) and
                                                                     math.hypot(x - (9 if x < 9 else W - 9), y - (21 if y < 21 else H - 8)) > 5)
                shape(cv, inside, (0, 0, W, H), lambda x, y: mix((200, 230, 220), (90, 120, 110), clamp(abs(x - cx) / cx)) + (0.35,), OUTLINE)
                top = int(H * 0.45) if ready else int(H * 0.62)
                for y in range(top, H - 4):
                    for x in range(5, W - 5):
                        if inside(x, y):
                            cv.put(x, y, scale_c(liq, 0.95 if ready else 0.55), 0.85)
                cv.rect(12, 7, W - 12, 16, WOOD[2])
                cv.rect(10, 5, W - 10, 9, WOOD[4])
                for x in range(9, W - 9):
                    cv.put(x, 16, OUTLINE)
                cv.rect(8, 22, 10, H - 12, (255, 255, 255), 0.35)
            elif sid == "ash_foundry":
                # a crucible on its trivet, molten metal at the brim when ready
                shape(cv, lambda x, y: 8 <= y < H - 16 and abs(x - cx) < (W / 2 - 4) - (y - 8) * 0.18, (0, 0, W, H),
                      lambda x, y: ramp(IRONS, clamp(0.55 - (x - cx) / W * 0.6 - (y / H) * 0.2)), OUTLINE)
                cv.rect(10, 8, W - 10, 14, (255, 150, 40) if ready else (70, 30, 18))
                if ready:
                    cv.glow(cx, 10, 20, (255, 180, 60), 0.6)
                for x0 in (14, W - 18):
                    cv.rect(x0, H - 16, x0 + 4, H - 2, IRONS[1])
                cv.rect(8, H - 18, W - 8, H - 14, IRONS[2])
            elif sid == "jailer_table":
                # a key tag on its hook: iron plate, gold rim, the keyhole lit when ready
                cv.disc(cx, 6, 5, IRONS[3])
                cv.disc(cx, 6, 3, (0, 0, 0, 0)[:3])
                shape(cv, lambda x, y: 10 <= y < H - 2 and abs(x - cx) < W / 2 - 2 - max(0, (y - (H - 18))) * 0.6, (0, 0, W, H),
                      lambda x, y: gold_tone(x, y, 0.7 - y / H * 0.35, 3, False) if abs(x - cx) > W / 2 - 6 or y < 14 else ramp(IRONS, 0.5 - y / H * 0.3), OUTLINE)
                cv.disc(cx, H - 20, 4, (230, 190, 90) if ready else OUTLINE)
                cv.rect(cx - 1.5, H - 20, cx + 1.5, H - 12, (230, 190, 90) if ready else OUTLINE)
            elif sid in ("lightning_forge", "dark_altar", "abyssal_press", "time_workshop"):
                r = W / 2 - 1
                if sid == "lightning_forge":
                    _disc_plate(cv, cx, cy, r, COPPER, (20, 26, 44) if not ready else (40, 60, 110))
                    for k in range(6):
                        a = k * math.pi / 3
                        rivet(cv, cx + math.cos(a) * (r - 2.5), cy + math.sin(a) * (r - 2.5), 1.3, COPPER[1:])
                elif sid == "dark_altar":
                    _disc_plate(cv, cx, cy, r, OBSID, (16, 10, 30) if not ready else (60, 40, 120))
                    for k in range(8):
                        a = k * math.pi / 4
                        cv.rect(cx + math.cos(a) * (r - 2) - 1, cy + math.sin(a) * (r - 2) - 1, cx + math.cos(a) * (r - 2) + 1, cy + math.sin(a) * (r - 2) + 1,
                                (170, 140, 255) if ready else (80, 60, 140))
                elif sid == "abyssal_press":
                    _disc_plate(cv, cx, cy, r, IRONS, (10, 34, 46) if not ready else (30, 110, 130))
                    for k in range(8):
                        a = k * math.pi / 4 + math.pi / 8
                        rivet(cv, cx + math.cos(a) * (r - 2.5), cy + math.sin(a) * (r - 2.5), 1.2, IRONS[1:])
                    cv.disc(cx - r * 0.35, cy - r * 0.35, 3, (220, 250, 255), 0.35)
                else:
                    _disc_plate(cv, cx, cy, r, BRASS, (240, 226, 190) if not ready else (250, 236, 170))
                    for k in range(12):
                        a = k * math.pi / 6
                        cv.put(cx + math.cos(a) * (r - 5), cy + math.sin(a) * (r - 5), OUTLINE)
                if ready:
                    cv.glow(cx, cy, r, liq, 0.35)
            elif sid in ("inverter", "terrain_anchor"):
                if sid == "inverter":
                    for y in range(H):
                        for x in range(W):
                            left = x < W / 2
                            c = (120, 40, 150) if left else (30, 130, 130)
                            n = fbm(x / 30, y / 5, 31, 2)
                            cv.put(x, y, scale_c(c, (0.55 if not ready else 0.8) + n * 0.3))
                    for y in range(H):
                        cv.put(W // 2, y, (240, 230, 250))
                        cv.put(W // 2 + 1, y, (120, 110, 140))
                else:
                    for y in range(H):
                        for x in range(W):
                            n = fbm(x / 26, y / 6, 33, 3)
                            layer = int((y + 6 * math.sin(x / 40.0)) / 8) % 3
                            c = [STONE[2], STONE[3], (150, 104, 70)][layer]
                            cv.put(x, y, scale_c(c, 0.75 + n * 0.4 + (0.15 if ready else 0)))
                for x in range(W):
                    cv.put(x, 0, OUTLINE)
                    cv.put(x, H - 1, OUTLINE)
                for y in range(H):
                    cv.put(0, y, OUTLINE)
                    cv.put(W - 1, y, OUTLINE)
                if ready:
                    for x in range(1, W - 1):
                        cv.put(x, 1, liq, 0.8)
            elif sid == "final_loom":
                # a woven banner hanging from a rod, its point down; the weave glows gold when ready
                bands = [world_style(k)["accent"] for k in range(1, 11)]
                def cloth(x, y):
                    edge = x < 6 or x >= W - 6
                    if edge:
                        return gold_tone(x, y, 0.7, 5, False) if ready else (150, 40, 30)
                    base = (232, 214, 176) if ready else (198, 178, 140)
                    c = scale_c(base, 0.92 if (x // 2 + y // 2) % 2 else 1.0)
                    if 10 <= y < 16:
                        c = bands[(x // 4) % 10]
                    return c
                shape(cv, lambda x, y: 6 <= y < H - 2 and 2 <= x < W - 2 and y < H - 2 - abs(x - cx) * 0.6, (0, 0, W, H), cloth, OUTLINE)
                cv.rect(0, 2, W, 6, WOOD[3])
                cv.rect(0, 2, W, 3, WOOD[5])
                if ready:
                    for y in range(8, H - 12):
                        cv.put(4, y, GOLD[5])
                        cv.put(W - 5, y, GOLD[5])
            save("tile_" + sid + ("_ready" if ready else ""), cv)


def decor_sprites():
    W, H = 180 * S, 88 * S
    for sid in TILES:
        st = world_style(world_of(sid))
        cv = Cv(W, H)
        if sid == "spore_vat":
            lacquer(cv, 0, 0, W, H, MOSSWOOD[:5], 5, 0.6, 0.04, wood=(30, 34, 16))
            for sy in (42, 84):
                _metal(cv, 0, (sy - 2) * S, W, (sy + 3) * S, WOOD[:5], 7 + sy)
                for x in range(0, W, 3):
                    cv.put(x, (sy + 3) * S, OUTLINE)
            for x0 in (10, W - 16):
                cv.rect(x0, 78 * S, x0 + 6, H, WOOD[1])
        elif sid == "ash_foundry":
            for y in range(H):
                for x in range(W):
                    bx = (x + (12 if (y // 16) % 2 else 0)) % 24
                    brick = bx < 2 or y % 16 < 2
                    c = (26, 18, 16) if brick else mix((70, 34, 24), (110, 50, 30), fbm(x / 20, y / 12, 3, 2))
                    glow = clamp((y - H * 0.4) / (H * 0.6))
                    cv.put(x, y, mix(c, (255, 120, 40), 0.35 * glow * glow))
        elif sid == "jailer_table":
            _metal(cv, 0, 0, W, H, [scale_c(c, 0.6) for c in STONE], 9, brushed=False)
            for x in range(0, W, 40):
                cv.rect(x, 0, x + 3, H, IRONS[1])
            for cy in (6, 50):
                cy *= S
                cv.rect(8, cy - 2, W - 8, cy + 2, IRONS[3])
                for x in range(12, W - 12, 8):
                    cv.disc(x, cy, 3, IRONS[4])
                    cv.disc(x, cy, 1.5, IRONS[1])
        elif sid == "lightning_forge":
            for y in range(H):
                for x in range(W):
                    n = fbm(x / 50, y / 30, 11, 3)
                    cv.put(x, y, mix((14, 18, 34), (50, 62, 100), clamp(n * 1.2 - y / H * 0.3)))
            # the anvil at the foot of the arc
            ax, ay = W / 2, H - 6
            cv.rect(ax - 44, ay - 30, ax + 44, ay - 18, IRONS[3])
            cv.rect(ax - 44, ay - 30, ax + 44, ay - 27, IRONS[5])
            cv.rect(ax - 20, ay - 18, ax + 20, ay - 8, IRONS[2])
            cv.rect(ax - 32, ay - 8, ax + 32, ay, IRONS[1])
            shape(cv, lambda x, y: ay - 30 <= y < ay - 22 and ax + 44 <= x < ax + 64 - (y - (ay - 30)) * 2, (0, 0, W, H), lambda x, y: IRONS[3])
            for y in range(int(ay - 30), int(ay)):
                cv.put(ax - 44, y, OUTLINE)
        elif sid == "dark_altar":
            _metal(cv, 0, 0, W, H, OBSID, 13, brushed=False)
            cx, cy = W / 2, (69 - 22) * S
            for rr in (35 * S, 30 * S, 15 * S):
                for k in range(720):
                    a = k * math.pi / 360
                    cv.put(cx + math.cos(a) * rr, cy + math.sin(a) * rr, (130, 100, 230), 0.8)
            pts = [(cx + math.cos(-math.pi / 2 + k * 6 * math.pi / 7) * 30 * S, cy + math.sin(-math.pi / 2 + k * 6 * math.pi / 7) * 30 * S) for k in range(8)]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                for i in range(200):
                    t = i / 200
                    cv.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, (110, 80, 200), 0.6)
        elif sid == "inverter":
            for y in range(H):
                for x in range(W):
                    left = x < W / 2
                    n = fbm(x / 40, y / 30, 15, 3)
                    c = (50, 16, 66) if left else (10, 56, 58)
                    cv.put(x, y, scale_c(c, 0.7 + n * 0.5))
            for y in range(H):
                cv.put(W // 2, y, (240, 230, 250), 0.8)
        elif sid == "abyssal_press":
            _metal(cv, 0, 0, W, H, [(10, 30, 44), (20, 50, 70), (34, 76, 100), (60, 110, 130), (100, 150, 170)], 17)
            for x in range(0, W, 60):
                cv.rect(x, 0, x + 2, H, (6, 20, 30))
            for y in range(0, H, 58):
                cv.rect(0, y, W, y + 2, (6, 20, 30))
            for x in range(6, W, 20):
                for y in (5, H - 6):
                    rivet(cv, x, y, 1.4, IRONS[1:])
        elif sid == "time_workshop":
            lacquer(cv, 0, 0, W, H, [scale_c(c, 0.55) for c in BRASS[:5]], 19, 0.3, 0.05, wood=(40, 28, 10))
            cx, cy = W / 2, (66 - 22) * S
            # the gear the four medallions sit on
            for k in range(16):
                a = k * math.pi / 8 + math.pi / 16
                cv.disc(cx + math.cos(a) * 41 * S, cy + math.sin(a) * 41 * S, 3 * S, BRASS[2])
            for y in range(int(cy - 42 * S), int(cy + 42 * S)):
                for x in range(int(cx - 42 * S), int(cx + 42 * S)):
                    d = math.hypot(x - cx, y - cy)
                    if 26 * S < d < 39 * S:
                        cv.put(x, y, BRASS[2] if 28 * S < d < 37 * S else BRASS[1])
                    elif d <= 26 * S and 16 * S < d:
                        cv.put(x, y, BRASS[1])
            for k in range(6):
                a = k * math.pi / 3
                for r in range(0, 16 * S):
                    cv.put(cx + math.cos(a) * r, cy + math.sin(a) * r, BRASS[3])
            cv.disc(cx, cy, 6 * S, BRASS[3])
        elif sid == "terrain_anchor":
            for y in range(H):
                for x in range(W):
                    n = fbm(x / 40, y / 10, 23, 3)
                    layer = int((y + 10 * math.sin(x / 60.0)) / 22)
                    c = [(60, 48, 40), (84, 64, 50), (52, 40, 36), (96, 70, 50)][layer % 4]
                    cv.put(x, y, scale_c(c, 0.7 + n * 0.5))
        elif sid == "final_loom":
            lacquer(cv, 0, 0, W, H, [(30, 18, 10), (44, 28, 14), (60, 38, 20), (80, 52, 28), (100, 66, 36)], 27, 0.5, 0.03)
            for k in range(40):
                x = 6 + k * 9
                cv.rect(x, 14, x + 1, H, world_style(1 + k % 10)["accent"], 0.4)
            cv.rect(0, 6, W, 16, WOOD[3])
            cv.rect(0, 6, W, 8, WOOD[5])
            for x0 in (2, W - 10):
                cv.rect(x0, 0, x0 + 8, H, WOOD[2])
        inner_shadow(cv, 0, 0, W, H, 8, 0.6)
        save("decor_" + sid, cv)


# =================================================================== boss bars: the reliquary
# The bosses' bars are drawn by tools/bossbars.py, one design per boss.
def boss_bars():
    import bossbars
    bossbars.build(globals())
