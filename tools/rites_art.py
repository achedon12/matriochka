"""The objects that open Worlds 2 to 10 (their ids stay seed_2..seed_10; World 1 keeps its Seed).

Each one is drawn in the hand-crafted style of craft.py, in its world's palette: an ember heart, the Jailer's key,
a storm rod, a black lantern, twin mirrors, an abyssal pearl, a sapling of the four seasons, a seismic stake and a
traveller's matryoshka.
"""
import math

from craft import Spr, GOLD, IRON, WOOD, RED, hramp, style, n_sphere, n_flat, n_bevel, n_cyl


def ember_heart(res):
    st = style(2)
    s = Spr(res)
    heart = s.mask(lambda x, y: ((x - 6.0) ** 2 + (y - 6.4) ** 2 <= 9.2) or ((x - 10.0) ** 2 + (y - 6.4) ** 2 <= 9.2)
                   or (y >= 6.4 and abs(x - 8.0) <= (14.2 - y) * 0.86))
    s.shade(heart, hramp("8a2a10"), n_sphere(7.0, 6.6, 6.4, 6.8), spec=0.05)
    cracks = s.path([(8.0, 4.4), (7.2, 7.0), (8.6, 9.0), (7.8, 11.6)], 0.42) | s.path([(5.2, 6.6), (7.0, 7.4)], 0.35) | s.path([(10.8, 6.0), (8.8, 8.2)], 0.35)
    s.fill(cracks & heart, lambda p: st["glow"][5] if (p[1] / s.k) < 9 else st["glow"][4], glow=True)
    s.dot(5.6, 5.0, (255, 230, 190))
    s.outline()
    return s


def jailer_key(res):
    s = Spr(res)
    bow = s.ring(5.0, 5.0, 2.0, 3.4)
    shaft = s.path([(7.4, 7.4), (13.0, 13.0)], 0.75)
    bits = s.path([(11.0, 13.0), (12.4, 11.6)], 0.55) | s.path([(12.6, 14.6), (14.0, 13.2)], 0.55)
    s.shade(bow | shaft | bits, IRON, n_flat(-0.4, -0.4), lo=1, hi=4)
    s.fill(s.ring(5.0, 5.0, 2.6, 3.0), GOLD[3])
    s.dot(5.0, 5.0, style(3)["glow"][4], glow=True)
    s.outline()
    return s


def storm_rod(res):
    st = style(4)
    s = Spr(res)
    rod = s.rect(7.2, 3.0, 8.8, 15.0)
    s.shade(rod, hramp("b8693a"), n_cyl(8.0, 0.9), lo=1, hi=4)
    for y in (6.0, 9.0, 12.0):
        s.shade(s.rect(6.2, y, 9.8, y + 0.9), GOLD, n_flat(0, -0.3), lo=2, hi=4)
    orb = s.disc(8.0, 3.2, 2.2)
    s.shade(orb, st["glow"], n_sphere(7.4, 2.6, 2.4), rim=False, lo=2, hi=5, glow=True)
    bolt = s.poly([(11.6, 1.0), (10.2, 3.6), (11.4, 3.6), (10.4, 6.4), (13.0, 3.0), (11.8, 3.0), (12.8, 1.0)])
    s.fill(bolt, st["glow"][5], glow=True)
    s.outline()
    return s


def black_lantern(res):
    s = Spr(res)
    frame = s.rect(4.6, 5.0, 11.4, 14.0)
    s.shade(frame, [(10, 8, 16), (20, 16, 30), (34, 28, 50), (54, 46, 76), (86, 76, 120)], n_bevel(s, frame, 1.0), lo=0, hi=3)
    glass = s.rect(5.8, 6.4, 10.2, 12.6)
    s.fill(glass, (6, 6, 12))
    flame = s.ell(8.0, 10.2, 1.3, 2.0)
    s.fill(flame, style(5)["glow"][3], glow=True)
    s.fill(s.rect(6.6, 2.6, 9.4, 5.0), IRON[2])
    s.fill(s.ring(8.0, 2.2, 0.9, 1.6), IRON[3])
    s.outline()
    return s


def twin_mirrors(res):
    st = style(6)
    s = Spr(res)
    for cx, col in ((5.2, st["body"]), (10.8, st["second"])):
        m = s.ell(cx, 7.6, 3.0, 5.0)
        s.shade(m, GOLD, n_sphere(cx - 0.5, 7.0, 3.2, 5.2), lo=1, hi=4)
        glass = s.ell(cx, 7.6, 2.1, 4.0)
        s.shade(glass, col, n_sphere(cx - 0.8, 6.4, 2.4, 4.0), rim=False, lo=2, hi=5, glow=True)
        s.fill(s.path([(cx - 0.9, 5.0), (cx - 1.3, 7.4)], 0.3), (255, 255, 255))
        s.fill(s.rect(cx - 0.6, 12.4, cx + 0.6, 14.4), GOLD[2])
    s.outline()
    return s


def abyssal_pearl(res):
    st = style(7)
    s = Spr(res)
    shell = s.mask(lambda x, y: y >= 9.0 and ((x - 8) / 7.0) ** 2 + ((y - 9.0) / 5.0) ** 2 <= 1)
    s.shade(shell, hramp("1a6a7a"), n_sphere(7.0, 9.0, 7.2, 5.0), lo=1, hi=4)
    for k in range(5):
        x = 3.4 + k * 2.3
        s.fill(s.path([(8.0, 13.8), (x, 9.4)], 0.25) & shell, hramp("0a3a4a")[1])
    pearl = s.disc(8.0, 7.4, 3.2)
    s.shade(pearl, st["glow"], n_sphere(7.0, 6.4, 3.4), rim=False, lo=2, hi=5, spec=0.2, glow=True)
    s.outline()
    return s


def season_sapling(res):
    s = Spr(res)
    s.shade(s.mask(lambda x, y: y >= 12.6 and abs(x - 8.0) <= 3.8 - (y - 12.6) * 0.4), WOOD, n_flat(0, -0.4), lo=1, hi=3)
    s.shade(s.path([(8.0, 12.8), (8.0, 6.0)], 0.6), WOOD, n_cyl(8.0, 0.6), lo=1, hi=3)
    leaves = [((4.6, 5.6), "6aa040"), ((11.4, 5.6), "e0a020"), ((5.6, 9.2), "d85a2a"), ((10.4, 9.2), "dceaf0"), ((8.0, 3.4), "8ac050")]
    for (x, y), c in leaves:
        lf = s.ell(x, y, 2.2, 1.5)
        s.shade(lf, hramp(c, n=5), n_flat(-0.3, -0.5), lo=1, hi=3)
    s.dot(8.0, 3.0, style(8)["glow"][4], glow=True)
    s.outline()
    return s


def seismic_stake(res):
    st = style(9)
    s = Spr(res)
    spike = s.poly([(6.4, 4.0), (9.6, 4.0), (9.0, 12.0), (8.0, 15.2), (7.0, 12.0)])
    s.shade(spike, st["metal"], n_bevel(s, spike, 1.0), lo=1, hi=4)
    head = s.rect(4.8, 1.6, 11.2, 4.2)
    s.shade(head, IRON, n_bevel(s, head, 0.8), lo=1, hi=4)
    runes = s.path([(8.0, 5.4), (8.0, 7.0)], 0.3) | s.path([(7.4, 8.4), (8.6, 9.6)], 0.3) | s.path([(8.4, 10.6), (7.6, 11.6)], 0.3)
    s.fill(runes & spike, st["glow"][4], glow=True)
    s.outline()
    return s


def traveller_doll(res):
    st = style(10)
    s = Spr(res)
    head = s.disc(8.0, 4.6, 3.0)
    body = s.ell(8.0, 10.6, 4.6, 4.6)
    doll = head | body
    s.shade(doll, RED, n_sphere(7.0, 7.4, 5.0, 7.4), spec=0.06)
    face = s.disc(8.0, 4.8, 1.9)
    s.fill(face, (246, 214, 186))
    s.dot(7.3, 4.6, (40, 22, 18))
    s.dot(8.7, 4.6, (40, 22, 18))
    s.fill(s.mask(lambda x, y: abs(y - 8.2) < 0.45) & body, GOLD[4])
    # the seam where it opens, and the travelling-cloak band in the world's second colour
    s.fill(s.mask(lambda x, y: abs(y - 11.4) < 0.5) & body, st["second"][3])
    s.dot(8.0, 12.8, GOLD[5])
    s.outline()
    return s


RITE_ART = {2: ember_heart, 3: jailer_key, 4: storm_rod, 5: black_lantern, 6: twin_mirrors, 7: abyssal_pearl,
            8: season_sapling, 9: seismic_stake, 10: traveller_doll}
