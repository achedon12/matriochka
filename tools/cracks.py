"""The cracks a boss shows as it breaks into its later phases (client/MatrioClient's phase layer).

For every boss, two overlays of its own texture, drawn as glowing (emissive) texels over its model:
  textures/entity/<boss>_cracks_1.png  a few cracks, after its first phase change
  textures/entity/<boss>_cracks_2.png  many, wider, after its second (and the Unfinished's later shells)
and textures/entity/boss_cracks_none.png, an empty texture for a boss still whole. Cracks only run over the
texture's painted texels, one texel wide, in the colour of the boss's world, with a darker edge on the wider ones.

  python3 tools/cracks.py
"""
import os
import random

from PIL import Image

import content as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "src/main/resources/assets/matriochka/textures/entity")


def world_light(w):
    if w == 0:
        return (110, 236, 246)
    pal = C.WORLDS[w - 1]["pal"]
    h = pal[2].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def overlay(base, n, length, wide, color, seed):
    rnd = random.Random(seed)
    w, h = base.size
    src = base.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = out.load()
    painted = [(x, y) for y in range(h) for x in range(w) if src[x, y][3] > 0]
    if not painted:
        return out
    dark = tuple(int(c * 0.45) for c in color)
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    for _ in range(n):
        stack = [(rnd.choice(painted), rnd.choice(dirs), length)]
        while stack:
            (x, y), (dx, dy), left = stack.pop()
            for _ in range(left):
                if not (0 <= x < w and 0 <= y < h) or src[x, y][3] == 0:
                    break
                px[x, y] = color + (255,)
                if wide:
                    for ox, oy in ((1, 0), (0, 1)):
                        qx, qy = x + ox, y + oy
                        if 0 <= qx < w and 0 <= qy < h and src[qx, qy][3] and px[qx, qy][3] == 0:
                            px[qx, qy] = dark + (255,)
                # a crack wanders, and now and then splits
                if rnd.random() < 0.22:
                    dx, dy = rnd.choice([d for d in dirs if d[0] * dx + d[1] * dy >= 0])
                if rnd.random() < 0.05 and left > 6:
                    stack.append(((x, y), rnd.choice(dirs), left // 2))
                x, y = x + dx, y + dy
                left -= 1
    return out


def main():
    Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(os.path.join(TEX, "boss_cracks_none.png"))
    for b in C.BOSSES:
        path = os.path.join(TEX, b["id"] + ".png")
        base = Image.open(path).convert("RGBA")
        scale = max(1, base.size[0] // 64)
        color = world_light(b["world"])
        seed = sum(map(ord, b["id"]))
        overlay(base, 3 * scale, 9 * scale, False, color, seed).save(os.path.join(TEX, b["id"] + "_cracks_1.png"), optimize=True)
        overlay(base, 7 * scale, 12 * scale, True, color, seed + 1).save(os.path.join(TEX, b["id"] + "_cracks_2.png"), optimize=True)
    print(len(C.BOSSES), "bosses cracked")


if __name__ == "__main__":
    main()
