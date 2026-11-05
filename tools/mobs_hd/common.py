"""Shared kit for the hand-made creature models (tools/mobs_hd/w*.py).

A creature module defines one function per creature id: `def sporeling(): r = Rig("sporeling"); ...; return r`.
Use the Rig DSL from bosses_hd (bone, cube, limb) and these roles so the animations find the right bones:
  body (one, the root of the trunk), head, jaw, arm_l, arm_r, leg_l, leg_r, tail, seg, wing_l, wing_r, orbit.
Bones without a role are fine for details; they follow their parent. Front of the model is -Z, up is +Y,
1 block = 16 units, the feet stand on y = 0.

Materials: everything in bosses_hd.MAT, plus EXTRA below, plus any a module adds with `mat(name, base, accent, pattern, emissive)`.
Patterns: blocks rune lacquer metal skin chitin membrane spots magma chain cloth glow cloud fur flesh crystal scales bark leaf vein.
Emissive materials (and the rune/spots/magma/vein patterns) light up through the glow mask: use them for eyes, cores and runes.
"""
import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import bosses_hd  # noqa: E402
from bosses_hd import Rig, MAT  # noqa: E402,F401

EXTRA = {
    "eye_white": ("f4f0e6", "ffffff", "skin", False),
    "eye_red": ("ff3a2a", "ffd0a0", "glow", True),
    "eye_green": ("9aff4a", "eaffc0", "glow", True),
    "eye_gold": ("ffd040", "fff4c0", "glow", True),
    "eye_blue": ("6ad0ff", "e0f8ff", "glow", True),
    "eye_violet": ("c07aff", "f0e0ff", "glow", True),
    "pupil": ("101010", "202020", "skin", False),
    "tooth": ("e8e0c8", "fffaf0", "skin", False),
    "bone": ("d8cfb4", "efe8d4", "skin", False),
    "moss": ("4a7a2a", "8ab84a", "leaf", False),
    "petal": ("c83a6a", "f08ab0", "leaf", False),
    "petal_inner": ("f0d040", "fff0a0", "spots", False),
    "stem": ("3a6a22", "5a8a32", "bark", False),
    "fungus": ("a8603a", "e8c090", "spots", False),
    "beetle_shell": ("2a4a1a", "7ab03a", "chitin", False),
    "rust": ("7a4a2a", "b8703a", "metal", False),
    "leather": ("5a3a24", "7a5234", "cloth", False),
    "cloth_red": ("8a2a22", "c84a3a", "cloth", False),
    "cloth_blue": ("2a3a6a", "4a6aa8", "cloth", False),
    "cloth_grey": ("4a4a52", "6a6a74", "cloth", False),
    "feather": ("3a5a8a", "a8c8f0", "fur", False),
    "feather_white": ("d8e0ea", "ffffff", "fur", False),
    "fur_brown": ("5a4030", "8a6a4a", "fur", False),
    "fur_grey": ("5a5a60", "8a8a90", "fur", False),
    "fur_black": ("1a1a22", "34344a", "fur", False),
    "rat_skin": ("c88a8a", "e8b0a8", "skin", False),
    "slime": ("6ab04a", "b0f080", "membrane", False),
    "jelly": ("6ab0d0", "c0f0ff", "membrane", True),
    "glass": ("a8d8e8", "f0ffff", "crystal", False),
    "obsidian": ("1a1428", "4a3a6a", "crystal", False),
    "sand": ("d8c08a", "f0e0b0", "blocks", False),
    "brass": ("b08a3a", "e8c86a", "metal", False),
    "clock_face": ("efe6cc", "3a2a1a", "rune", False),
    "wood_dark": ("4a2e1a", "6a4428", "bark", False),
    "wood_light": ("a87a4a", "d0a070", "bark", False),
    "dirt": ("6a4a2e", "8a6a44", "blocks", False),
    "coral": ("e06a5a", "ffb0a0", "spots", False),
    "pearl": ("f0f0ff", "ffffff", "glow", True),
    "ink": ("0a0a14", "1a1a2e", "flesh", False),
    "ember": ("ff8a2a", "ffe080", "magma", True),
    "spark": ("ffe14a", "ffffff", "glow", True),
    "soul": ("4ad8e8", "d0ffff", "glow", True),
    "toxic": ("b7e04a", "f4ff9a", "glow", True),
}
MAT.update(EXTRA)


def mat(name, base, accent, pattern="skin", emissive=False):
    MAT[name] = (base, accent, pattern, emissive)
    return name


def finish(rig, seed=0):
    """Writes the model, texture, glow mask and animations (idle, walk, strike, then the creature's own attacks)."""
    import models
    import moves
    roles = {}
    for r, names in rig.roles.items():
        base = r.rstrip("0123456789") if r[-1:].isdigit() and r.rstrip("0123456789") in (
            "arm_l", "arm_r", "leg_l", "leg_r") else r
        roles.setdefault(base, []).extend(names)
    bones = [SimpleNamespace(name=n, role=r) for r, ns in roles.items() for n in ns]
    an = models.animations(bones, False)["animations"]
    an.update(moves.attack_anims(roles, rig.name))
    _, h = bosses_hd.write(rig, an, seed)
    # hitboxes are square: size them on the body's width and depth around the centre, not on tails and weapons
    xs = sorted(abs(v) for b in rig.bones if b["name"] in roles.get("body", []) or b.get("parent") is None
                for c in b["cubes"] for v in (c["origin"][0], c["origin"][0] + c["size"][0]))
    zs = sorted(abs(v) for b in rig.bones if b["name"] in roles.get("body", [])
                for c in b["cubes"] for v in (c["origin"][2], c["origin"][2] + c["size"][2]))
    w = max(xs[-1] if xs else 4, (zs[len(zs) // 2] if zs else 4)) * 2 / 16
    return min(w, 1.8), h
