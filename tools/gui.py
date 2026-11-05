"""GUI sprites in the matryoshka folk-art style (nine-slice), drawn as pixel art."""
import json, os, random
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "src/main/resources/assets/matriochka/textures/gui/sprites")
os.makedirs(OUT, exist_ok=True)

RED = (179, 38, 30); RED_D = (122, 22, 18); RED_L = (214, 70, 52)
BLACK = (30, 20, 16); GOLD = (217, 164, 65); GOLD_L = (245, 214, 130); GOLD_D = (150, 104, 36)
BIRCH = (232, 210, 166); BIRCH_D = (205, 178, 128); INK = (58, 36, 22)
WOOD = (120, 74, 40); WOOD_D = (84, 50, 26); WOOD_L = (150, 98, 56); GREEN = (79, 122, 58)

def save(name, img, border, w=None, h=None):
    img.save(os.path.join(OUT, name + ".png"))
    json.dump({"gui": {"scaling": {"type": "nine_slice", "width": w or img.width, "height": h or img.height, "border": border}}},
              open(os.path.join(OUT, name + ".png.mcmeta"), "w"))

def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c + (255,))

def rect(img, x0, y0, x1, y1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            px(img, x, y, c)

def ring(img, i, c):
    w, h = img.size
    for x in range(i, w - i):
        px(img, x, i, c); px(img, x, h - 1 - i, c)
    for y in range(i, h - i):
        px(img, i, y, c); px(img, w - 1 - i, y, c)

def rosette(img, cx, cy):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        px(img, cx + dx, cy + dy, GOLD)
    px(img, cx, cy, GOLD_L)
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        px(img, cx + dx, cy + dy, GOLD_D)

# --- the nested frame: black, red lacquer band with gold beads, gold line, black, dark wood inside
def frame():
    S = 48
    img = Image.new("RGBA", (S, S))
    r = random.Random(1)
    for x in range(S):
        for y in range(S):
            g = 0.9 + 0.1 * ((x * 7 + y * 3) % 5) / 5
            px(img, x, y, tuple(int(c * g) for c in (38, 26, 20)))
    ring(img, 0, BLACK)
    for i in range(1, 6):
        ring(img, i, RED if i not in (1, 5) else RED_D)
    ring(img, 2, RED_L)
    for t in range(4, S - 4, 4):   # gold beads along the lacquer band
        for (x, y) in ((t, 3), (t, S - 4), (3, t), (S - 4, t)):
            px(img, x, y, GOLD)
    ring(img, 6, GOLD)
    ring(img, 7, GOLD_D)
    ring(img, 8, BLACK)
    for (cx, cy) in ((3, 3), (S - 4, 3), (3, S - 4), (S - 4, S - 4)):
        rosette(img, cx, cy)
    save("frame", img, 10)

def paper():
    S = 32
    img = Image.new("RGBA", (S, S))
    r = random.Random(2)
    for x in range(S):
        for y in range(S):
            f = 0.95 + r.random() * 0.06 - (0.05 if r.random() < 0.04 else 0)
            px(img, x, y, tuple(min(255, int(c * f)) for c in BIRCH))
    ring(img, 0, INK)
    ring(img, 1, BIRCH_D)
    save("paper", img, 3)

def drawer(name, face, knob):
    W, H = 32, 22
    img = Image.new("RGBA", (W, H))
    for x in range(W):
        for y in range(H):
            grain = 0.9 + 0.1 * ((x // 3 + y * 5) % 4) / 4
            px(img, x, y, tuple(int(c * grain) for c in face))
    ring(img, 0, BLACK)
    for x in range(1, W - 1):
        px(img, x, 1, tuple(min(255, c + 30) for c in face))
        px(img, x, H - 2, tuple(int(c * 0.7) for c in face))
    for y in range(3, H - 3):
        px(img, 2, y, knob)
    save(name, img, 4)

def button(name, base, edge):
    W, H = 24, 16
    img = Image.new("RGBA", (W, H))
    rect(img, 0, 0, W - 1, H - 1, base)
    ring(img, 0, BLACK)
    ring(img, 1, edge)
    for x in range(2, W - 2):
        px(img, x, 2, tuple(min(255, c + 40) for c in base))
        px(img, x, H - 3, tuple(int(c * 0.65) for c in base))
    save(name, img, 4)

def ribbon(name, base):
    W, H = 20, 40
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x in range(W):
        for y in range(H - 6):
            px(img, x, y, base)
    for y in range(H - 6, H):
        for x in range(W):
            if abs(x - W / 2 + 0.5) > (y - (H - 6)) * 1.6:
                px(img, x, y, base)
    for y in range(H):
        px(img, 1, y, GOLD) if img.getpixel((1, y))[3] else None
        px(img, W - 2, y, GOLD) if img.getpixel((W - 2, y))[3] else None
    save(name, img, 4)

def slot():
    img = Image.new("RGBA", (18, 18))
    rect(img, 0, 0, 17, 17, (52, 34, 24))
    ring(img, 0, GOLD_D)
    for x in range(1, 17):
        px(img, x, 1, BLACK)
        px(img, 1, x, BLACK)
    save("slot", img, 2)

def doll(name, body, face=(240, 208, 176)):
    img = Image.new("RGBA", (9, 12), (0, 0, 0, 0))
    shape = ["..XXXXX..", ".XXXXXXX.", ".XFFFFFX.", ".XFFFFFX.", "..XXXXX..", ".XXXXXXX.",
             "XXXGGGXXX", "XXGGGGGXX", "XXXGGGXXX", "XXXXXXXXX", ".XXXXXXX.", "..XXXXX.."]
    for y, row in enumerate(shape):
        for x, ch in enumerate(row):
            if ch == "X": px(img, x, y, body)
            elif ch == "F": px(img, x, y, face)
            elif ch == "G": px(img, x, y, GOLD if body != (70, 60, 56) else (90, 80, 76))
    px(img, 3, 3, BLACK); px(img, 5, 3, BLACK)
    img.save(os.path.join(OUT, name + ".png"))

frame(); paper(); slot()
drawer("drawer", WOOD, GOLD); drawer("drawer_hover", WOOD_L, GOLD_L); drawer("drawer_ready", (96, 108, 52), GOLD)
button("button", RED, GOLD_D); button("button_hover", RED_L, GOLD); button("button_off", (70, 52, 46), (90, 70, 60))
ribbon("ribbon", RED_D); ribbon("ribbon_on", GOLD_D)
doll("doll_full", RED); doll("doll_empty", (70, 60, 56), (110, 100, 96))
print("gui sprites ok")
