"""Procedural GeckoLib (Blockbench-format) models, animations and box-UV textures.

Every body plan is a list of bones. Each bone has a role used by the animation
builder (leg_l, leg_r, arm_l, arm_r, head, body, tail, wing_l, wing_r, seg, orbit,
jaw, extra). The output files open in Blockbench as regular GeckoLib entity models.
"""
import json
import math
from PIL import Image
from paint import hx, shade, mix, rng


class B:
    def __init__(self, name, role, pivot, cubes, parent="root", rot=None):
        self.name, self.role, self.pivot, self.cubes, self.parent, self.rot = name, role, pivot, cubes, parent, rot


def C(o, s, col="p", inflate=0, rot=None, pivot=None):
    return dict(o=o, s=s, col=col, inflate=inflate, rot=rot, pivot=pivot)


def legs4(y, w, h, d, sx, fz, bz, col="d"):
    return [B("leg_fl", "leg_l", [sx, y + h, fz], [C([sx - w / 2, y, fz - d / 2], [w, h, d], col)]),
            B("leg_fr", "leg_r", [-sx, y + h, fz], [C([-sx - w / 2, y, fz - d / 2], [w, h, d], col)]),
            B("leg_bl", "leg_r", [sx, y + h, bz], [C([sx - w / 2, y, bz - d / 2], [w, h, d], col)]),
            B("leg_br", "leg_l", [-sx, y + h, bz], [C([-sx - w / 2, y, bz - d / 2], [w, h, d], col)])]


def legs_n(n, y, w, h, d, sx, z0, z1, col="d"):
    out = []
    for i in range(n // 2):
        z = z0 + (z1 - z0) * (i / max(1, n // 2 - 1))
        for side, sgn in (("l", 1), ("r", -1)):
            role = "leg_l" if (i % 2 == 0) == (side == "l") else "leg_r"
            out.append(B(f"leg_{side}{i}", role, [sgn * sx, y + h, z],
                         [C([sgn * sx - (w if sgn < 0 else 0), y, z - d / 2], [w + 4, h, d], col, rot=[0, 0, sgn * 35],
                            pivot=[sgn * sx, y + h, z])]))
    return out


def biped(lh=12, bh=12, bw=8, bd=4, hs=8, aw=4, ah=12, lw=4, col_body="p", col_head="s", col_arm="p", col_leg="d"):
    y_body = lh
    y_head = lh + bh
    return [
        B("leg_l", "leg_l", [lw / 2, lh, 0], [C([0, 0, -lw / 2], [lw, lh, lw], col_leg)]),
        B("leg_r", "leg_r", [-lw / 2, lh, 0], [C([-lw, 0, -lw / 2], [lw, lh, lw], col_leg)]),
        B("body", "body", [0, y_body, 0], [C([-bw / 2, y_body, -bd / 2], [bw, bh, bd], col_body)]),
        B("head", "head", [0, y_head, 0], [C([-hs / 2, y_head, -hs / 2], [hs, hs, hs], col_head)], parent="body"),
        B("arm_l", "arm_l", [bw / 2 + aw / 2, y_head - 2, 0], [C([bw / 2, y_head - ah, -aw / 2], [aw, ah, aw], col_arm)], parent="body"),
        B("arm_r", "arm_r", [-bw / 2 - aw / 2, y_head - 2, 0], [C([-bw / 2 - aw, y_head - ah, -aw / 2], [aw, ah, aw], col_arm)], parent="body"),
    ]


def plan(body):
    if body == "biped":
        return biped()
    if body == "biped_short":
        bs = biped(lh=6, bh=8, bw=8, bd=5, hs=7, aw=3, ah=8, lw=3)
        bs.append(B("pick", "extra", [-6, 10, 0], [C([-7, 2, -1], [2, 10, 2], "d"), C([-10, 10, -1], [8, 2, 2], "a")], parent="arm_r"))
        return bs
    if body == "brute":
        bs = biped(lh=10, bh=12, bw=12, bd=7, hs=7, aw=5, ah=14, lw=5)
        bs.append(B("hood", "extra", [0, 22, 0], [C([-4, 22, -4], [8, 9, 8], "d", inflate=0.3)], parent="head"))
        bs.append(B("axe", "extra", [-8, 10, 0], [C([-9, 0, -1], [2, 16, 2], "d"), C([-13, 12, -1], [8, 6, 1], "a")], parent="arm_r"))
        return bs
    if body == "robed":
        return [
            B("body", "body", [0, 0, 0], [C([-5, 0, -4], [10, 18, 8], "p"), C([-4, 18, -3], [8, 4, 6], "s")]),
            B("head", "head", [0, 22, 0], [C([-4, 22, -4], [8, 8, 8], "s"), C([-4.5, 25, -4.5], [9, 6, 9], "d")], parent="body"),
            B("arm_l", "arm_l", [6, 20, 0], [C([5, 8, -1.5], [3, 13, 3], "p")], parent="body"),
            B("arm_r", "arm_r", [-6, 20, 0], [C([-8, 8, -1.5], [3, 13, 3], "p")], parent="body"),
            B("chain", "extra", [0, 12, 0], [C([-6, 12, -4.5], [12, 1, 1], "a"), C([-1, 2, -4.5], [2, 10, 1], "a")], parent="body"),
        ]
    if body == "imp":
        return [
            B("leg_l", "leg_l", [1.5, 4, 0], [C([0.5, 0, -1], [2, 4, 2], "d")]),
            B("leg_r", "leg_r", [-1.5, 4, 0], [C([-2.5, 0, -1], [2, 4, 2], "d")]),
            B("body", "body", [0, 4, 0], [C([-3, 4, -2], [6, 6, 4], "p")]),
            B("head", "head", [0, 10, 0], [C([-4, 10, -4], [8, 7, 8], "s"), C([-6, 17, -6], [12, 3, 12], "a"), C([-3, 20, -3], [6, 2, 6], "a")], parent="body"),
            B("arm_l", "arm_l", [4, 9, 0], [C([3, 3, -1], [2, 6, 2], "p")], parent="body"),
            B("arm_r", "arm_r", [-4, 9, 0], [C([-5, 3, -1], [2, 6, 2], "p")], parent="body"),
        ]
    if body == "crawler":
        bs = [B("body", "body", [0, 4, 0], [C([-6, 3, -8], [12, 5, 16], "p"), C([-5, 8, -6], [10, 2, 12], "a")]),
              B("head", "head", [0, 5, -8], [C([-4, 2, -14], [8, 5, 6], "s")], parent="body")]
        return bs + legs_n(6, 0, 2, 3, 2, 6, -6, 6)
    if body == "beetle":
        bs = [B("body", "body", [0, 6, 0], [C([-7, 4, -8], [14, 8, 18], "p"), C([-6, 12, -6], [12, 3, 14], "a")]),
              B("head", "head", [0, 7, -8], [C([-4, 4, -14], [8, 6, 6], "s"), C([-1, 9, -18], [2, 2, 6], "a")], parent="body"),
              B("shield", "extra", [0, 8, -9], [C([-6, 3, -11], [12, 9, 1], "a")], parent="body")]
        return bs + legs_n(6, 0, 2, 4, 2, 7, -6, 6)
    if body == "plant":
        return [
            B("body", "body", [0, 0, 0], [C([-2, 0, -2], [4, 14, 4], "p"), C([-7, 0, -1], [6, 1, 3], "d"), C([1, 0, -1], [6, 1, 3], "d")]),
            B("head", "head", [0, 14, 0], [C([-3, 14, -3], [6, 6, 6], "s"),
                                           C([-7, 15, -1], [4, 4, 2], "a"), C([3, 15, -1], [4, 4, 2], "a"),
                                           C([-1, 15, -7], [2, 4, 4], "a"), C([-1, 15, 3], [2, 4, 4], "a")], parent="body"),
            B("jaw", "jaw", [0, 15, -3], [C([-2, 14, -5], [4, 2, 3], "d")], parent="head"),
        ]
    if body == "blob":
        return [B("body", "body", [0, 0, 0], [C([-6, 0, -6], [12, 10, 12], "p"), C([-4, 10, -4], [8, 3, 8], "a")]),
                B("head", "head", [0, 6, -6], [C([-3, 5, -7], [6, 3, 1], "s")], parent="body")]
    if body == "golem":
        return [
            B("leg_l", "leg_l", [4, 10, 0], [C([1, 0, -3], [6, 10, 6], "d")]),
            B("leg_r", "leg_r", [-4, 10, 0], [C([-7, 0, -3], [6, 10, 6], "d")]),
            B("body", "body", [0, 10, 0], [C([-7, 10, -5], [14, 14, 10], "p"), C([-4, 14, -6], [8, 6, 1], "a")]),
            B("head", "head", [0, 24, 0], [C([-4, 24, -5], [8, 8, 8], "s")], parent="body"),
            B("arm_l", "arm_l", [9, 22, 0], [C([7, 4, -3], [6, 18, 6], "p")], parent="body"),
            B("arm_r", "arm_r", [-9, 22, 0], [C([-13, 4, -3], [6, 18, 6], "p")], parent="body"),
        ]
    if body == "lizard":
        return [B("body", "body", [0, 4, 0], [C([-3, 2, -8], [6, 5, 16], "p"), C([-1, 7, -6], [2, 2, 12], "a")]),
                B("head", "head", [0, 5, -8], [C([-3, 2, -15], [6, 4, 7], "s")], parent="body"),
                B("tail", "tail", [0, 4, 8], [C([-1.5, 2, 8], [3, 3, 12], "p")], parent="body")] + legs4(0, 2, 3, 2, 4, -5, 5)
    if body == "floating_head":
        return [B("body", "body", [0, 16, 0], [C([-5, 14, -5], [10, 10, 10], "p"), C([-3, 17, -5.5], [6, 2, 1], "a")]),
                B("head", "head", [0, 24, 0], [C([-6, 24, -6], [12, 2, 12], "s")], parent="body"),
                B("chain_l", "tail", [4, 14, 0], [C([3.5, 2, -0.5], [1, 12, 1], "a")], parent="body"),
                B("chain_r", "tail", [-4, 14, 0], [C([-4.5, 4, -0.5], [1, 10, 1], "a")], parent="body")]
    if body == "block":
        return [B("body", "body", [0, 0, 0], [C([-8, 0, -8], [16, 12, 16], "p")]),
                B("head", "jaw", [0, 12, 8], [C([-8, 12, -8], [16, 4, 16], "s")], parent="body")]
    if body == "chest":
        return [B("body", "body", [0, 0, 0], [C([-7, 0, -7], [14, 10, 14], "p"), C([-6, 9, -7.5], [12, 1, 1], "a")]),
                B("head", "jaw", [0, 10, 7], [C([-7, 10, -7], [14, 5, 14], "s"), C([-1, 8, -8], [2, 4, 1], "a")], parent="body")]
    if body == "rat":
        return [B("body", "body", [0, 3, 0], [C([-3, 2, -5], [6, 5, 10], "p")]),
                B("head", "head", [0, 4, -5], [C([-2, 2, -10], [4, 4, 5], "s"), C([-3, 6, -7], [2, 2, 1], "s"), C([1, 6, -7], [2, 2, 1], "s")], parent="body"),
                B("tail", "tail", [0, 4, 5], [C([-0.5, 3.5, 5], [1, 1, 9], "a")], parent="body")] + legs4(0, 2, 2, 2, 2, -3, 3)
    if body == "ray":
        return [B("body", "body", [0, 8, 0], [C([-6, 7, -8], [12, 3, 16], "p"), C([-2, 10, -4], [4, 1, 8], "a")]),
                B("wing_l", "wing_l", [6, 8, 0], [C([6, 8, -6], [14, 1, 12], "s")], parent="body"),
                B("wing_r", "wing_r", [-6, 8, 0], [C([-20, 8, -6], [14, 1, 12], "s")], parent="body"),
                B("tail", "tail", [0, 8, 8], [C([-0.5, 8, 8], [1, 1, 16], "d")], parent="body")]
    if body == "bird":
        return [B("body", "body", [0, 8, 0], [C([-3, 5, -5], [6, 6, 10], "p")]),
                B("head", "head", [0, 10, -5], [C([-2.5, 9, -10], [5, 5, 5], "s"), C([-1, 10, -13], [2, 2, 3], "a")], parent="body"),
                B("wing_l", "wing_l", [3, 10, 0], [C([3, 10, -4], [12, 1, 8], "s")], parent="body"),
                B("wing_r", "wing_r", [-3, 10, 0], [C([-15, 10, -4], [12, 1, 8], "s")], parent="body"),
                B("tail", "tail", [0, 8, 5], [C([-3, 8, 5], [6, 1, 6], "d")], parent="body")]
    if body == "orb":
        return [B("body", "body", [0, 12, 0], [C([-5, 7, -5], [10, 10, 10], "a"), C([-3, 9, -6], [6, 6, 12], "s"), C([-6, 9, -3], [12, 6, 6], "s")]),
                B("ring", "orbit", [0, 12, 0], [C([-8, 11.5, -8], [16, 1, 16], "p", inflate=-0.2)], parent="body")]
    if body == "quad":
        return [B("body", "body", [0, 12, 0], [C([-5, 10, -9], [10, 10, 18], "p"), C([-4, 20, -6], [8, 2, 12], "a")]),
                B("head", "head", [0, 16, -9], [C([-4, 11, -17], [8, 8, 8], "s"), C([-3, 9, -17.5], [6, 3, 1], "a")], parent="body"),
                B("tail", "tail", [0, 17, 9], [C([-1, 16, 9], [2, 2, 10], "d")], parent="body")] + legs4(0, 4, 10, 4, 3, -6, 6)
    if body == "wisp":
        return [B("body", "body", [0, 10, 0], [C([-4, 8, -3], [8, 10, 6], "p"), C([-2, 3, -2], [4, 5, 4], "d")]),
                B("head", "head", [0, 18, 0], [C([-3.5, 18, -3.5], [7, 7, 7], "s")], parent="body"),
                B("arm_l", "arm_l", [5, 17, 0], [C([4, 9, -1], [2, 8, 2], "p")], parent="body"),
                B("arm_r", "arm_r", [-5, 17, 0], [C([-6, 9, -1], [2, 8, 2], "p")], parent="body")]
    if body == "spider":
        bs = [B("body", "body", [0, 6, 0], [C([-5, 4, -6], [10, 6, 12], "p"), C([-6, 5, 6], [12, 8, 12], "a")]),
              B("head", "head", [0, 6, -6], [C([-4, 3, -12], [8, 6, 6], "s")], parent="body")]
        return bs + legs_n(8, 4, 12, 2, 2, 5, -5, 5)
    if body == "tall":
        return [
            B("leg_l", "leg_l", [2, 24, 0], [C([0.5, 0, -1.5], [3, 24, 3], "d")]),
            B("leg_r", "leg_r", [-2, 24, 0], [C([-3.5, 0, -1.5], [3, 24, 3], "d")]),
            B("body", "body", [0, 24, 0], [C([-4, 24, -3], [8, 8, 6], "p")]),
            B("head", "head", [0, 32, 0], [C([-3, 32, -3], [6, 6, 6], "s")], parent="body"),
            B("arm_l", "arm_l", [5.5, 31, 0], [C([4, 13, -1.5], [3, 18, 3], "p")], parent="body"),
            B("arm_r", "arm_r", [-5.5, 31, 0], [C([-7, 13, -1.5], [3, 18, 3], "p")], parent="body")]
    if body == "fish":
        return [B("body", "body", [0, 6, 0], [C([-4, 2, -8], [8, 8, 16], "p"), C([-0.5, 10, -4], [1, 4, 8], "a")]),
                B("head", "head", [0, 6, -8], [C([-3.5, 2.5, -13], [7, 7, 5], "s")], parent="body"),
                B("tail", "tail", [0, 6, 8], [C([-1, 1, 8], [2, 10, 6], "a")], parent="body")]
    if body == "fish_small":
        return [B("body", "body", [0, 3, 0], [C([-2, 1, -5], [4, 4, 10], "p")]),
                B("head", "head", [0, 3, -5], [C([-1.5, 1.5, -7], [3, 3, 2], "s")], parent="body"),
                B("tail", "tail", [0, 3, 5], [C([-0.5, 0, 5], [1, 6, 4], "a")], parent="body")]
    if body == "jelly":
        bs = [B("body", "body", [0, 16, 0], [C([-7, 14, -7], [14, 10, 14], "p"), C([-5, 12, -5], [10, 2, 10], "a")])]
        for i in range(8):
            ang = i * math.pi / 4
            x, z = 4.5 * math.cos(ang), 4.5 * math.sin(ang)
            bs.append(B(f"tent{i}", "tail", [x, 12, z], [C([x - 0.5, 0, z - 0.5], [1, 12, 1], "s")], parent="body"))
        return bs
    if body == "crab":
        bs = [B("body", "body", [0, 6, 0], [C([-7, 4, -6], [14, 6, 12], "p"), C([-5, 10, -5], [10, 8, 10], "a")]),
              B("arm_l", "arm_l", [7, 7, -6], [C([6, 4, -13], [6, 5, 7], "s")], parent="body"),
              B("arm_r", "arm_r", [-7, 7, -6], [C([-12, 4, -13], [6, 5, 7], "s")], parent="body")]
        return bs + legs_n(6, 0, 2, 5, 2, 7, -4, 4)
    if body in ("eel", "worm"):
        n, w = (6, 6) if body == "eel" else (5, 8)
        bs, parent = [], "root"
        for i in range(n):
            z = -i * 10 + 10
            role = "head" if i == 0 else "seg"
            bs.append(B(f"seg{i}", role, [0, w / 2, z], [C([-w / 2, 0, z - 10], [w, w, 10], "p" if i % 2 else "s")], parent=parent))
            parent = f"seg{i}"
        bs[0].cubes.append(C([-w / 2 - 0.5, -0.5, 9], [w + 1, w + 1, 3], "a"))
        bs[0].name = "head"
        for b in bs[1:2]:
            b.parent = "head"
        return bs
    if body == "hand":
        bs = [B("body", "body", [0, 0, 0], [C([-6, 0, -6], [12, 6, 12], "p"), C([-4, -6, -4], [8, 6, 8], "d")])]
        for i, x in enumerate((-5, -2.5, 0, 2.5)):
            bs.append(B(f"finger{i}", "arm_l" if i % 2 else "arm_r", [x, 6, -4], [C([x - 1, 6, -5], [2.5, 10, 2.5], "s")], parent="body"))
        bs.append(B("thumb", "arm_l", [6, 4, 0], [C([6, 4, -1], [2.5, 8, 2.5], "s")], parent="body"))
        return bs
    if body == "column":
        return [B("leg_l", "leg_l", [4, 6, 0], [C([2, 0, -3], [5, 6, 6], "d")]),
                B("leg_r", "leg_r", [-4, 6, 0], [C([-7, 0, -3], [5, 6, 6], "d")]),
                B("body", "body", [0, 6, 0], [C([-8, 6, -8], [16, 4, 16], "s"), C([-6, 10, -6], [12, 36, 12], "p"), C([-8, 46, -8], [16, 4, 16], "s")]),
                B("head", "head", [0, 30, -6], [C([-3, 28, -7], [6, 4, 1], "a")], parent="body")]
    # ---- bosses
    if body == "guardian":
        bs = biped(lh=16, bh=20, bw=20, bd=14, hs=10, aw=10, ah=26, lw=9)
        for i in range(4):
            ang = i * math.pi / 2
            x, z = 20 * math.cos(ang), 20 * math.sin(ang)
            bs.append(B(f"stone{i}", "orbit", [0, 30, 0], [C([x - 3, 26 + i * 3, z - 3], [6, 6, 6], "s")], parent="body"))
        return bs
    if body == "queen":
        bs = [B("body", "body", [0, 14, 0], [C([-6, 10, -6], [12, 12, 12], "p"), C([-8, 8, 6], [16, 14, 20], "a")]),
              B("head", "head", [0, 18, -6], [C([-5, 14, -15], [10, 10, 10], "s"),
                                              C([-5, 24, -11], [2, 5, 2], "a"), C([3, 24, -11], [2, 5, 2], "a"), C([-1, 24, -13], [2, 6, 2], "a")], parent="body"),
              B("wing_l", "wing_l", [5, 22, 2], [C([5, 22, -2], [18, 1, 14], "s")], parent="body"),
              B("wing_r", "wing_r", [-5, 22, 2], [C([-23, 22, -2], [18, 1, 14], "s")], parent="body"),
              B("arm_l", "arm_l", [6, 18, -6], [C([5, 8, -9], [3, 12, 3], "d")], parent="body"),
              B("arm_r", "arm_r", [-6, 18, -6], [C([-8, 8, -9], [3, 12, 3], "d")], parent="body")]
        return bs + legs_n(6, 0, 3, 10, 3, 6, -4, 4)
    if body == "titan":
        bs = biped(lh=16, bh=18, bw=16, bd=10, hs=10, aw=7, ah=22, lw=8)
        bs.append(B("hammer", "extra", [-11, 16, 0], [C([-12.5, -6, -1.5], [3, 24, 3], "d"), C([-18, -14, -6], [14, 10, 12], "a")], parent="arm_r"))
        bs.append(B("core", "extra", [0, 24, -5], [C([-3, 21, -6], [6, 6, 1], "a")], parent="body"))
        return bs
    if body == "jailer":
        bs = plan("robed")
        bs.append(B("ring", "orbit", [0, 14, 0], [C([-9, 13, -9], [18, 1, 1], "a"), C([-9, 13, 8], [18, 1, 1], "a"),
                                                  C([-9, 13, -9], [1, 1, 18], "a"), C([8, 13, -9], [1, 1, 18], "a")], parent="body"))
        bs.append(B("keyring", "extra", [7, 8, 0], [C([6, 3, -2], [4, 4, 1], "a")], parent="arm_l"))
        return bs
    if body == "storm_king":
        bs = biped()
        bs.append(B("wing_l", "wing_l", [3, 22, 2], [C([3, 6, 2], [18, 18, 1], "s")], parent="body"))
        bs.append(B("wing_r", "wing_r", [-3, 22, 2], [C([-21, 6, 2], [18, 18, 1], "s")], parent="body"))
        bs.append(B("crown", "extra", [0, 32, 0], [C([-4, 32, -4], [8, 3, 8], "a")], parent="head"))
        return bs
    if body == "light_eater":
        bs = plan("quad")
        bs[1].cubes = [C([-7, 9, -24], [14, 12, 16], "s")]
        bs.append(B("jaw", "jaw", [0, 10, -10], [C([-6, 6, -23], [12, 4, 14], "d")], parent="head"))
        bs.append(B("tendril_l", "wing_l", [5, 20, 0], [C([5, 20, -1], [10, 1, 2], "a")], parent="body"))
        bs.append(B("tendril_r", "wing_r", [-5, 20, 0], [C([-15, 20, -1], [10, 1, 2], "a")], parent="body"))
        return bs
    if body == "double":
        return biped()
    if body == "leviathan":
        bs, parent = [], "root"
        for i in range(8):
            z = -i * 16 + 16
            w = 14 - i
            bs.append(B("head" if i == 0 else f"seg{i}", "head" if i == 0 else "seg", [0, 8, z],
                        [C([-w / 2, 8 - w / 2, z - 16], [w, w, 16], "p" if i % 2 else "s")], parent=parent))
            parent = bs[-1].name
        bs.append(B("jaw", "jaw", [0, 4, 16], [C([-6, 0, 14], [12, 4, 10], "d")], parent="head"))
        bs.append(B("fin_l", "wing_l", [7, 8, 0], [C([7, 8, -6], [10, 1, 8], "a")], parent="head"))
        bs.append(B("fin_r", "wing_r", [-7, 8, 0], [C([-17, 8, -6], [10, 1, 8], "a")], parent="head"))
        return bs
    if body == "seasons":
        bs = biped(lh=14, bh=22, bw=14, bd=10, hs=10, aw=6, ah=22, lw=7, col_body="d", col_head="p")
        bs.append(B("antlers", "extra", [0, 46, 0], [C([-9, 46, -1], [4, 10, 2], "d"), C([5, 46, -1], [4, 10, 2], "d"), C([-12, 52, -1], [4, 2, 2], "d"), C([8, 52, -1], [4, 2, 2], "d")], parent="head"))
        for i, col in enumerate(("a", "s", "p", "eye")):
            ang = i * math.pi / 2
            bs.append(B(f"orb{i}", "orbit", [0, 30, 0], [C([22 * math.cos(ang) - 2.5, 30, 22 * math.sin(ang) - 2.5], [5, 5, 5], col)], parent="body"))
        return bs
    if body == "heart":
        bs = [B("body", "body", [0, 20, 0], [C([-12, 8, -12], [24, 24, 24], "p"), C([-8, 32, -4], [6, 8, 6], "s"), C([2, 32, -2], [6, 10, 6], "s")])]
        for i in range(6):
            ang = i * math.pi / 3
            bs.append(B(f"spike{i}", "orbit", [0, 20, 0], [C([16 * math.cos(ang) - 2, 16 + (i % 2) * 6, 16 * math.sin(ang) - 2], [4, 4, 4], "a")], parent="body"))
        return bs
    if body == "unfinished":
        return [B("body", "body", [0, 0, 0], [C([-10, 0, -10], [20, 22, 20], "lacquer"), C([-9, 4, -10.5], [18, 10, 1], "gold")]),
                B("head", "head", [0, 22, 0], [C([-7, 22, -7], [14, 14, 14], "lacquer"), C([-5, 24, -7.5], [10, 9, 1], "skin")], parent="body"),
                B("shell", "orbit", [0, 18, 0], [C([-12, 0, -12], [24, 4, 24], "gold", inflate=0.2), C([-12, 34, -12], [24, 2, 24], "gold", inflate=0.2)], parent="body")]
    return biped()


# ------------------------------------------------------------------ texture packing + painting
def box_uv_size(s):
    w, h, d = [max(1, int(math.ceil(v))) for v in s]
    return 2 * (d + w), d + h, (w, h, d)


def build(body, pal, seed, out_geo, out_anim, out_tex, ident, boss=False):
    bones = plan(body)
    # pack cubes
    cubes = [(b, c) for b in bones for c in b.cubes]
    tw = 64
    while True:
        x = y = rowh = 0
        placements = []
        ok = True
        for (b, c) in cubes:
            uw, uh, _ = box_uv_size(c["s"])
            if uw > tw:
                ok = False
                break
            if x + uw > tw:
                x, y, rowh = 0, y + rowh, 0
            placements.append((x, y))
            x += uw
            rowh = max(rowh, uh)
        th = y + rowh
        if ok and th <= tw:
            break
        tw *= 2
    th = tw
    for (b, c), (u, v) in zip(cubes, placements):
        c["uv"] = [u, v]

    cols = {"p": hx(pal[0]), "s": hx(pal[1]), "a": hx(pal[2]), "d": hx(pal[3]),
            "eye": (255, 240, 120), "lacquer": hx("c8342a"), "gold": hx("e8c050"), "skin": hx("f0d0b0")}
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    r = rng(seed)
    for (b, c) in cubes:
        u, v = c["uv"]
        _, _, (w, h, d) = box_uv_size(c["s"])
        base = cols.get(c["col"], cols["p"])
        faces = [(u + d, v, w, d, 1.15), (u + d + w, v, w, d, 0.7), (u, v + d, d, h, 0.85), (u + d, v + d, w, h, 1.0),
                 (u + d + w, v + d, d, h, 0.85), (u + d + w + d, v + d, w, h, 0.9)]
        for fi, (x0, y0, ww, hh, lf) in enumerate(faces):
            for xx in range(x0, x0 + ww):
                for yy in range(y0, y0 + hh):
                    if xx >= tw or yy >= th:
                        continue
                    f = lf * (0.86 + r.random() * 0.22)
                    rel = (yy - y0) / max(1, hh)
                    f *= 1.08 - rel * 0.18
                    col = shade(base, f)
                    edge = xx in (x0, x0 + ww - 1) or yy in (y0, y0 + hh - 1)
                    if edge and ww > 2 and hh > 2:
                        col = shade(col, 0.72)
                    elif (xx * 7 + yy * 3) % 11 == 0 and c["col"] in ("p", "s"):
                        col = mix(col, cols["a"], 0.35)
                    img.putpixel((xx, yy), col + (255,))
        # eyes on the north (front) face of the head
        if b.role == "head" and c is b.cubes[0] and w >= 4 and h >= 3:
            fx, fy = u + d, v + d
            ey = fy + max(1, h // 3)
            for ex in (fx + max(1, w // 4), fx + w - 1 - max(1, w // 4)):
                eye = (255, 230, 90) if not boss else (255, 90, 60)
                img.putpixel((ex, ey), eye + (255,))
                if w >= 8:
                    img.putpixel((ex, ey + 1), shade(eye, 0.6) + (255,))
            if h >= 6:
                for mx in range(fx + w // 3, fx + w - w // 3):
                    img.putpixel((mx, fy + h - max(2, h // 4)), (30, 15, 15, 255))
    img.save(out_tex)

    geo_bones = [{"name": "root", "pivot": [0, 0, 0]}]
    for b in bones:
        jb = {"name": b.name, "parent": b.parent, "pivot": b.pivot, "cubes": []}
        if b.rot:
            jb["rotation"] = b.rot
        for c in b.cubes:
            jc = {"origin": [round(v, 3) for v in c["o"]], "size": [round(v, 3) for v in c["s"]], "uv": c["uv"]}
            if c["inflate"]:
                jc["inflate"] = c["inflate"]
            if c["rot"]:
                jc["rotation"] = c["rot"]
                jc["pivot"] = c["pivot"]
            jb["cubes"].append(jc)
        geo_bones.append(jb)
    ys = [c["o"][1] + c["s"][1] for b in bones for c in b.cubes]
    height = max(ys) / 16
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{ident}", "texture_width": tw, "texture_height": th,
                        "visible_bounds_width": 6, "visible_bounds_height": max(3, height + 1), "visible_bounds_offset": [0, height / 2, 0]},
        "bones": geo_bones}]}
    json.dump(geo, open(out_geo, "w"), indent=1)
    json.dump(animations(bones, boss), open(out_anim, "w"), indent=1)
    xs = [abs(c["o"][0]) for b in bones for c in b.cubes] + [abs(c["o"][0] + c["s"][0]) for b in bones for c in b.cubes]
    zs = [abs(c["o"][2]) for b in bones for c in b.cubes] + [abs(c["o"][2] + c["s"][2]) for b in bones for c in b.cubes]
    width = min(max(max(xs), max(zs)) * 2 / 16, 3.0)
    return width, height


def anim(length, loop, bones):
    return {"loop": loop, "animation_length": length, "bones": bones}


def animations(bones, boss):
    roles = {}
    for b in bones:
        roles.setdefault(b.role, []).append(b.name)
    A = {}

    def rot(expr_x="0", expr_y="0", expr_z="0"):
        return {"rotation": [expr_x, expr_y, expr_z]}

    # idle
    idle = {}
    if "body" in roles:
        idle[roles["body"][0]] = {"position": [0, "math.sin(query.anim_time*180)*0.4", 0]}
    for h in roles.get("head", []):
        idle[h] = rot("math.sin(query.anim_time*90)*3", "math.sin(query.anim_time*60)*6")
    for w in roles.get("wing_l", []):
        idle[w] = rot("0", "0", "math.sin(query.anim_time*240)*18")
    for w in roles.get("wing_r", []):
        idle[w] = rot("0", "0", "-math.sin(query.anim_time*240)*18")
    for t in roles.get("tail", []):
        idle[t] = rot("math.sin(query.anim_time*120)*6", "math.sin(query.anim_time*90)*14")
    for i, s in enumerate(roles.get("seg", [])):
        idle[s] = rot("0", f"math.sin(query.anim_time*180+{i * 50})*10")
    for o in roles.get("orbit", []):
        idle[o] = rot("0", "query.anim_time*45")
    for j in roles.get("jaw", []):
        idle[j] = rot("math.max(0,math.sin(query.anim_time*120))*-12")
    A["misc.idle"] = anim(4.0, True, idle)

    walk = dict(idle)
    for l in roles.get("leg_l", []):
        walk[l] = rot("math.sin(query.anim_time*400)*32")
    for l in roles.get("leg_r", []):
        walk[l] = rot("-math.sin(query.anim_time*400)*32")
    for a in roles.get("arm_l", []):
        walk[a] = rot("-math.sin(query.anim_time*400)*24")
    for a in roles.get("arm_r", []):
        walk[a] = rot("math.sin(query.anim_time*400)*24")
    for w in roles.get("wing_l", []):
        walk[w] = rot("0", "0", "math.sin(query.anim_time*600)*32")
    for w in roles.get("wing_r", []):
        walk[w] = rot("0", "0", "-math.sin(query.anim_time*600)*32")
    for i, s in enumerate(roles.get("seg", [])):
        walk[s] = rot("0", f"math.sin(query.anim_time*360+{i * 50})*16")
    if "body" in roles:
        walk[roles["body"][0]] = {"position": [0, "math.abs(math.sin(query.anim_time*400))*0.8", 0]}
    A["move.walk"] = anim(1.8, True, walk)

    # attack: arms swing / lunge
    atk = {}
    arms = roles.get("arm_r", []) + roles.get("arm_l", [])
    if arms:
        for a in arms:
            atk[a] = {"rotation": {"0.0": [0, 0, 0], "0.15": [-110, 0, 0], "0.35": [20, 0, 0], "0.6": [0, 0, 0]}}
    else:
        tgt = (roles.get("head") or roles.get("body"))[0]
        atk[tgt] = {"rotation": {"0.0": [0, 0, 0], "0.15": [25, 0, 0], "0.35": [-15, 0, 0], "0.6": [0, 0, 0]},
                    "position": {"0.0": [0, 0, 0], "0.2": [0, 0, -3], "0.6": [0, 0, 0]}}
    for j in roles.get("jaw", []):
        atk[j] = {"rotation": {"0.0": [0, 0, 0], "0.1": [-35, 0, 0], "0.4": [0, 0, 0]}}
    A["attack.strike"] = anim(0.6, False, atk)

    if boss:
        tel = {}
        body = roles.get("body", ["root"])[0]
        tel[body] = {"position": {"0.0": [0, 0, 0], "0.5": [0, -2, 0], "1.0": [0, -2.5, 0]},
                     "rotation": {"0.0": [0, 0, 0], "0.25": [0, 4, 0], "0.5": [0, -4, 0], "0.75": [0, 4, 0], "1.0": [0, 0, 0]}}
        for a in arms:
            tel[a] = {"rotation": {"0.0": [0, 0, 0], "1.0": [-150, 0, 0]}}
        for h in roles.get("head", []):
            tel[h] = {"rotation": {"0.0": [0, 0, 0], "1.0": [-20, 0, 0]}}
        A["attack.charge"] = anim(1.0, "hold_on_last_frame", tel)
        slam = {}
        for a in arms:
            slam[a] = {"rotation": {"0.0": [-150, 0, 0], "0.15": [30, 0, 0], "0.6": [0, 0, 0]}}
        slam[body] = {"position": {"0.0": [0, -2.5, 0], "0.15": [0, 0, 0], "0.6": [0, 0, 0]}}
        A["attack.slam"] = anim(0.6, False, slam)
        cast = {}
        for a in roles.get("arm_l", []):
            cast[a] = {"rotation": {"0.0": [0, 0, 0], "0.3": [-160, 0, -20], "0.9": [-160, 0, -20], "1.2": [0, 0, 0]}}
        for a in roles.get("arm_r", []):
            cast[a] = {"rotation": {"0.0": [0, 0, 0], "0.3": [-160, 0, 20], "0.9": [-160, 0, 20], "1.2": [0, 0, 0]}}
        for o in roles.get("orbit", []):
            cast[o] = rot("0", "query.anim_time*360")
        cast[body] = {"position": {"0.0": [0, 0, 0], "0.6": [0, 2, 0], "1.2": [0, 0, 0]}}
        A["attack.cast"] = anim(1.2, False, cast)
        roar = {}
        for h in roles.get("head", []):
            roar[h] = {"rotation": {"0.0": [0, 0, 0], "0.4": [-35, 0, 0], "1.6": [-35, 0, 0], "2.0": [0, 0, 0]}}
        roar[body] = {"rotation": {"0.0": [0, 0, 0], "0.4": [-8, 0, 0], "1.6": [-8, 0, 0], "2.0": [0, 0, 0]},
                      "scale": {"0.0": [1, 1, 1], "0.4": [1.08, 1.08, 1.08], "1.6": [1.08, 1.08, 1.08], "2.0": [1, 1, 1]}}
        for j in roles.get("jaw", []):
            roar[j] = {"rotation": {"0.0": [0, 0, 0], "0.4": [-45, 0, 0], "1.6": [-45, 0, 0], "2.0": [0, 0, 0]}}
        A["misc.phase"] = anim(2.0, False, roar)
        vuln = {body: {"rotation": {"0.0": [0, 0, 0], "0.3": [14, 0, 6], "2.0": [14, 0, 6], "2.4": [0, 0, 0]},
                       "position": {"0.0": [0, 0, 0], "0.3": [0, -3, 0], "2.0": [0, -3, 0], "2.4": [0, 0, 0]}}}
        A["misc.rest"] = anim(2.4, False, vuln)
    return {"format_version": "1.8.0", "animations": A}
