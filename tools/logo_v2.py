"""Matriochka icons and logo, rendered as voxel pixel art.

Same family as the key-art wordmark (media/poster/logo.py): red lacquer, gold rim, deep plum outline, palettes
stepped with an ordered dither like hand-placed pixels, art drawn at 256 px and scaled up x4 with no smoothing.

The renderer is a small orthographic voxel ray caster in numpy:
  - every voxel has a material (a palette ramp, dark to light) and a tone (its base index in the ramp);
  - each pixel casts a ray (3D DDA) into the grid; the face it hits gives the normal (smoothed for rounded shapes);
  - shading = key light from the top left, cast shadows (a second ray toward the light), ambient occlusion,
    gold and lacquer specular, a lacquer gloss band;
  - in screen space: a light rim on the far silhouette edge, dark lines where the depth jumps, a plum outline,
    a stepped (dithered) glow around emissive voxels;
  - faces are painted as decals projected from the camera, so they stay straight on the curved heads.
The 48, 32 and 16 px icons are drawn pixel by pixel (Px, small_B, small_C), not downscaled.

Designs
  B  the world block: a grass block lacquered like a doll, broken open at the front corner; the next doll stands in
     the lit heart, the light spills onto the grass and the edges, the ten worlds are ten gems in the gold edges.
     The mod's icon and logo (branding/logo-*.png, icon-*.png, icon-square-1024.png on a lacquer plate,
     src/main/resources/assets/matriochka/icon.png).
  C  the guardian: the doll as a mascot on a black-lacquer medallion whose gold rim holds the ten worlds as gems.
     The pack's icon (branding/modpack/icon*.png) and the Discord avatar (branding/discord-avatar-256.png).
  A  the opening: the doll opened at the waist, a tiny lit world inside. branding/illustration-opening.png.

  python3 tools/logo_v2.py [--sheet dir]           # writes every file above (and a contact sheet in dir)
  python3 tools/logo_v2.py --concepts dir [A B C]  # the exploration sheets (concept_X.png, sizes, grid mock)
Then python3 tools/site.py (its branding step) makes the site's favicons, logo-*.webp and og.png from branding/.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ART = 256          # art resolution, scaled x4 to 1024
UP = 4

# ---------------------------------------------------------------- palettes (dark -> light), shared with the poster
RED = [(38, 6, 12), (70, 10, 16), (102, 14, 20), (150, 24, 28), (194, 38, 36), (226, 78, 60), (248, 146, 116)]
GOLD = [(70, 40, 12), (112, 74, 20), (160, 112, 34), (204, 154, 50), (238, 194, 82), (252, 224, 140), (255, 246, 206)]
CREAM = [(120, 84, 62), (170, 128, 96), (214, 178, 138), (238, 216, 180), (250, 238, 214), (255, 250, 238)]
BLACK = [(10, 6, 8), (20, 12, 14), (32, 20, 22), (48, 30, 30), (70, 46, 42)]
WOOD = [(60, 36, 22), (92, 62, 38), (122, 86, 54), (150, 108, 64), (180, 130, 76), (212, 162, 98), (238, 198, 134), (252, 226, 176)]
GRASS = [(18, 40, 16), (30, 62, 22), (48, 94, 30), (74, 128, 40), (106, 160, 52), (148, 196, 74), (196, 228, 120)]
DIRT = [(40, 24, 16), (66, 42, 26), (96, 64, 40), (126, 88, 56), (156, 114, 76)]
LEAF = [(12, 34, 18), (22, 56, 26), (34, 84, 34), (52, 116, 44), (80, 150, 58), (122, 188, 84)]
BARK = [(36, 22, 14), (60, 40, 24), (88, 60, 36), (116, 82, 50)]
WATER = [(10, 30, 70), (20, 60, 120), (34, 100, 170), (60, 150, 214), (120, 200, 240), (200, 240, 255), (255, 255, 255)]
STONE = [(40, 38, 44), (66, 64, 72), (96, 94, 102), (128, 126, 134), (164, 162, 170)]
PINK = [(140, 40, 40), (190, 70, 64), (222, 104, 92), (240, 140, 124)]
PLUM = (38, 10, 22)
PLUM_IN = (72, 20, 34)

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.47


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gem_ramp(pal):
    """A 7-step ramp round a world's most vivid colour (its signature): near black, dark, the colour, near white."""
    import colorsys
    cols = [hexc(h) for h in pal]

    def vivid(c):
        h, s_, v = colorsys.rgb_to_hsv(*(x / 255 for x in c))
        return s_ * (0.4 + v)
    sig = max(cols, key=vivid)
    dark = cols[3]
    return [mix(sig, (8, 4, 8), 0.85), mix(sig, (8, 4, 8), 0.62), mix(sig, (8, 4, 8), 0.35), sig,
            mix(sig, (255, 255, 255), 0.30), mix(sig, (255, 255, 255), 0.6), mix(sig, (255, 255, 255), 0.88)]


def hash3(x, y, z, s=0):
    h = (np.asarray(x, np.int64) * 374761393 + np.asarray(y, np.int64) * 668265263 + np.asarray(z, np.int64) * 1442695041
         + s * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 0xFFFFFFFF


# ---------------------------------------------------------------- materials
class Mats:
    """Material table: name -> id; each has a ramp and flags."""

    def __init__(self):
        self.list = [None]
        self.ids = {}

    def add(self, name, ramp, emissive=False, gold=False, gloss=False, noshadow=False, glow=None, ao=1.0):
        self.ids[name] = len(self.list)
        self.list.append(dict(name=name, ramp=ramp, emissive=emissive, gold=gold, gloss=gloss, noshadow=noshadow,
                              glow=glow, ao=ao))
        return self.ids[name]

    def __getitem__(self, k):
        return self.ids[k]


def base_mats():
    M = Mats()
    M.add("red", RED, gloss=True)
    M.add("gold", GOLD, gold=True)
    M.add("cream", CREAM)
    M.add("black", BLACK, gloss=True)
    M.add("wood", WOOD)
    M.add("grass", GRASS)
    M.add("dirt", DIRT)
    M.add("leaf", LEAF)
    M.add("bark", BARK)
    M.add("water", WATER)
    M.add("stone", STONE)
    M.add("pink", PINK)
    M.add("hair", BLACK, gloss=True)
    return M


class Grid:
    def __init__(self, shape):
        self.mat = np.zeros(shape, np.uint8)
        self.tone = np.zeros(shape, np.float32)
        self.lit = np.zeros(shape, bool)      # lit by the world's own light: cast shadows only dim it a little
        self.smooth = np.zeros(shape, np.float32)  # 0 shade by the voxel face, 1 by the smoothed surface normal
        self.shape = shape
        X, Y, Z = np.meshgrid(*[np.arange(n) + 0.5 for n in shape], indexing="ij")
        self.X, self.Y, self.Z = X, Y, Z

    def put(self, mask, mat, tone):
        self.mat[mask] = mat
        self.tone[mask] = tone if np.isscalar(tone) else np.asarray(tone)[mask] if np.shape(tone) == self.shape else tone


# ---------------------------------------------------------------- camera and ray casting
class Camera:
    def __init__(self, yaw, pitch):
        a, p = math.radians(yaw), math.radians(pitch)
        self.eye = np.array([math.cos(p) * math.cos(a), math.cos(p) * math.sin(a), math.sin(p)])
        self.f = -self.eye
        r = np.cross(self.f, [0, 0, 1.0])
        self.right = r / np.linalg.norm(r)
        self.up = np.cross(self.right, self.f)

    def light(self, side=-0.62, height=0.95, front=0.45):
        L = side * self.right + height * np.array([0, 0, 1.0]) + front * self.eye
        return L / np.linalg.norm(L)


def trace(occ, o, d, first_only=True, max_steps=None):
    """Orthographic 3D DDA. occ: bool grid; o: (N,3) origins; d: (3,) direction.
    Returns hit (N,), voxel (N,3), axis (N,), t (N,)."""
    N = o.shape[0]
    dims = np.array(occ.shape)
    d = np.where(np.abs(d) < 1e-9, 1e-9, d)
    inv = 1.0 / d
    t0 = (0 - o) * inv
    t1 = (dims - o) * inv
    tlo, thi = np.minimum(t0, t1), np.maximum(t0, t1)
    tmin, tmax = tlo.max(1), thi.min(1)
    tent = np.maximum(tmin, 0)
    valid = tmax > tent
    entry_axis = tlo.argmax(1)
    p = o + (tent + 1e-5)[:, None] * d
    idx = np.clip(np.floor(p).astype(np.int64), 0, dims - 1)
    step = np.sign(d).astype(np.int64)
    bound = idx + (step > 0)
    tMax = (bound - o) * inv
    tDelta = np.abs(inv)
    hit = np.zeros(N, bool)
    vox = np.zeros((N, 3), np.int64)
    axis = np.zeros(N, np.int64)
    thit = np.zeros(N)
    act = np.nonzero(valid)[0]
    I, TM, AX, TC = idx[act], tMax[act], entry_axis[act], tent[act]
    steps = max_steps or int(dims.sum()) + 4
    for _ in range(steps):
        if act.size == 0:
            break
        occd = occ[I[:, 0], I[:, 1], I[:, 2]]
        if occd.any():
            h = act[occd]
            hit[h] = True
            vox[h] = I[occd]
            axis[h] = AX[occd]
            thit[h] = TC[occd]
            keep = ~occd
            act, I, TM, AX, TC = act[keep], I[keep], TM[keep], AX[keep], TC[keep]
        a = TM.argmin(1)
        r = np.arange(act.size)
        TC = TM[r, a].copy()
        I[r, a] += step[a]
        TM[r, a] += tDelta[a]
        AX = a
        inb = ((I >= 0) & (I < dims)).all(1)
        if not inb.all():
            act, I, TM, AX, TC = act[inb], I[inb], TM[inb], AX[inb], TC[inb]
    return hit, vox, axis, thit


def box_blur3(a, r, passes=2):
    """Separable box blur of a 3D array (edge-padded), `passes` times."""
    out = a.astype(np.float32)
    for _ in range(passes):
        for ax in range(3):
            p = np.pad(out, [(r + 1, r) if i == ax else (0, 0) for i in range(3)], mode="edge")
            c = np.cumsum(p, axis=ax)
            n = out.shape[ax]
            hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=ax)
            lo = np.take(c, np.arange(0, n), axis=ax)
            out = (hi - lo) / (2 * r + 1)
    return out


def fit(grid, cam, W, H, box):
    """World units per pixel and screen origin so the occupied voxels fill box=(x0,y0,x1,y1) in pixels."""
    pts = np.argwhere(grid.mat > 0).astype(float)
    corners = np.array([[i, j, k] for i in (0, 1) for j in (0, 1) for k in (0, 1)], float)
    # project voxel corners (subsampled for speed)
    pts = pts[:: max(1, len(pts) // 60000)]
    P = (pts[:, None, :] + corners[None]).reshape(-1, 3)
    sx, sy = P @ cam.right, P @ cam.up
    x0, x1, y0, y1 = sx.min(), sx.max(), sy.min(), sy.max()
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = max((x1 - x0) / bw, (y1 - y0) / bh)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return s, cx, cy, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def render(grid, M, cam, W, H, box, opts=None):
    """Ray-cast the grid. Returns dict of per-pixel buffers (hit, mat, tone-shade, depth, normal axis/sign...)."""
    opts = opts or {}
    s, cx, cy, (bx, by) = fit(grid, cam, W, H, box)
    if "scale" in opts:
        s = opts["scale"]
    jj, ii = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    u = (jj - bx) * s + cx
    v = -(ii - by) * s + cy
    far = float(sum(grid.shape)) * 2
    centre = np.array(grid.shape) / 2.0
    # remove the centre's own projection so the ray origin is placed in front of the grid
    cpar = centre - (centre @ cam.right) * cam.right - (centre @ cam.up) * cam.up
    O = (u.reshape(-1, 1) * cam.right + v.reshape(-1, 1) * cam.up + cpar - far * cam.f)
    occ = grid.mat > 0
    hit, vox, axis, t = trace(occ, O, cam.f)
    N = W * H
    out = dict(W=W, H=H, s=s)
    out["hit"] = hit.reshape(H, W)
    out["depth"] = np.where(hit, t, np.inf).reshape(H, W)
    mat = np.zeros(N, np.uint8)
    mat[hit] = grid.mat[vox[hit, 0], vox[hit, 1], vox[hit, 2]]
    tone = np.zeros(N, np.float32)
    tone[hit] = grid.tone[vox[hit, 0], vox[hit, 1], vox[hit, 2]]
    step = np.sign(cam.f)
    nrm = np.zeros((N, 3))
    hi = np.nonzero(hit)[0]
    nrm[hi, axis[hi]] = -step[axis[hi]]
    P = O + t[:, None] * cam.f
    # ambient occlusion: per-vertex from the 8 cells around the cell in front of the face, bilinear across the face
    occp = np.pad(occ, 1)
    ao = np.ones(N)
    if hi.size:
        a = axis[hi]
        n = nrm[hi].astype(np.int64)
        c = vox[hi] + n + 1
        a1, a2 = (a + 1) % 3, (a + 2) % 3
        e1 = np.zeros((hi.size, 3), np.int64)
        e2 = np.zeros((hi.size, 3), np.int64)
        r = np.arange(hi.size)
        e1[r, a1] = 1
        e2[r, a2] = 1
        fu = np.clip(P[hi, a1] - vox[hi, a1], 0, 1)
        fv = np.clip(P[hi, a2] - vox[hi, a2], 0, 1)

        def oc(q):
            q = np.clip(q, 0, np.array(occp.shape) - 1)
            return occp[q[:, 0], q[:, 1], q[:, 2]].astype(float)

        s1m, s1p, s2m, s2p = oc(c - e1), oc(c + e1), oc(c - e2), oc(c + e2)
        cmm, cmp_, cpm, cpp = oc(c - e1 - e2), oc(c - e1 + e2), oc(c + e1 - e2), oc(c + e1 + e2)

        def vert(sa, sb, cc):
            return np.where((sa > 0) & (sb > 0), 0.0, 3.0 - sa - sb - cc) / 3.0

        v00, v01, v10, v11 = vert(s1m, s2m, cmm), vert(s1m, s2p, cmp_), vert(s1p, s2m, cpm), vert(s1p, s2p, cpp)
        ao[hi] = (v00 * (1 - fu) * (1 - fv) + v01 * (1 - fu) * fv + v10 * fu * (1 - fv) + v11 * fu * fv)
    # smoothed normals (for rounded shapes) and a broad cavity occlusion, from the blurred occupancy
    D = box_blur3(occ, 2)
    if hi.size:
        gx, gy, gz = np.gradient(D)
        vv = vox[hi]
        sn = -np.stack([gx[vv[:, 0], vv[:, 1], vv[:, 2]], gy[vv[:, 0], vv[:, 1], vv[:, 2]], gz[vv[:, 0], vv[:, 1], vv[:, 2]]], 1)
        sn /= np.linalg.norm(sn, axis=1, keepdims=True) + 1e-6
        sm = grid.smooth[vv[:, 0], vv[:, 1], vv[:, 2]][:, None]
        nn = nrm[hi] * (1 - sm) + sn * sm
        nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-6
        fo = nrm[hi] * (1 - sm) + sn * sm
        front = np.clip(np.round(vv + 0.5 + fo * 2.2 - 0.5).astype(np.int64), 0, np.array(occ.shape) - 1)
        dens = D[front[:, 0], front[:, 1], front[:, 2]]
        cav = np.ones(N)
        cav[hi] = np.clip(1.25 - 1.6 * dens, 0, 1)
        ao[hi] = ao[hi] * (1 - 0.92 * sm[:, 0]) + 0.92 * sm[:, 0] * 1.0
        ao = ao * cav
        snrm = nrm.copy()
        snrm[hi] = nn
    else:
        snrm = nrm
    # shadows
    L = opts.get("light", cam.light())
    shadow = np.zeros(N)
    if hi.size and opts.get("shadows", True):
        cast = occ.copy()
        for m in M.list[1:]:
            if m["emissive"] or m.get("nocast"):
                cast[grid.mat == M[m["name"]]] = False
        smh = grid.smooth[vox[hi, 0], vox[hi, 1], vox[hi, 2]][:, None]
        So = P[hi] + nrm[hi] * 0.02 + L * 0.02 + snrm[hi] * 1.8 * smh + L * 1.2 * smh
        sh, _, _, _ = trace(cast, So, L)
        shadow[hi] = sh
    lit = np.zeros(N, bool)
    lit[hit] = grid.lit[vox[hit, 0], vox[hit, 1], vox[hit, 2]]
    out.update(lit=lit.reshape(H, W), mat=mat.reshape(H, W), tone=tone.reshape(H, W), nrm=snrm.reshape(H, W, 3), ao=ao.reshape(H, W),
               shadow=shadow.reshape(H, W), L=L, P=P.reshape(H, W, 3), vox=vox.reshape(H, W, 3),
               axis=axis.reshape(H, W))
    return out


def shade(buf, M, cam, opts=None):
    """Turn the buffers into an RGBA pixel-art image (art resolution)."""
    opts = opts or {}
    H, W = buf["H"], buf["W"]
    hit, mat, tone, nrm, ao, shadow, depth = (buf[k] for k in ("hit", "mat", "tone", "nrm", "ao", "shadow", "depth"))
    L = buf["L"]
    yy, xx = np.mgrid[0:H, 0:W]
    ndl = np.clip((nrm * L).sum(-1), -0.2, 1)
    k = opts.get("contrast", 1.0)
    sh = (-1.5 + 2.9 * ndl) * k
    ao_k = np.zeros((H, W))
    emis = np.zeros((H, W), bool)
    gold = np.zeros((H, W), bool)
    gloss = np.zeros((H, W), bool)
    nosh = np.zeros((H, W), bool)
    for i, m in enumerate(M.list):
        if m is None:
            continue
        sel = mat == i
        ao_k[sel] = m["ao"]
        emis |= sel & m["emissive"]
        gold |= sel & m["gold"]
        gloss |= sel & m["gloss"]
        nosh |= sel & m["noshadow"]
    nosh |= buf["lit"]
    sh = sh - 1.7 * (1 - ao) * ao_k
    sh = sh - np.where(nosh, 0.35, 1.25) * shadow
    # gold: a hot specular on faces turned to the light, sparkles on lit gold
    hv = L + cam.eye
    hv = hv / np.linalg.norm(hv)
    spec = np.clip((nrm * hv).sum(-1), 0, 1) ** 6
    sh = np.where(gold, sh + 1.6 * spec + 0.3, sh)
    # lacquer: a tight specular highlight on the smoothed surface
    lspec = np.clip((nrm * hv).sum(-1), 0, 1) ** 28
    sh = np.where(gloss, sh + opts.get("lacquer_spec", 2.6) * lspec, sh)
    # lacquer gloss: a diagonal band across the image, on faces turned to the light
    band = opts.get("gloss_band", None)
    if band is not None:
        bx, bw = band
        g = np.abs((xx + yy * 0.55) - bx) < bw
        sh = np.where(gloss & g & (ndl > 0.35) & (shadow < 0.5), sh + 1.0, sh)
    sh = np.where(emis, opts.get("emis_tone", 0.0) + 0.6 * (ndl - 0.5), sh)
    # depth edges: the far side of a jump gets a dark line, the near side a light lip when lit
    dthr = opts.get("edge", 3.0)
    dpad = np.pad(depth, 1, constant_values=np.inf)
    near = np.zeros((H, W), bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nb = dpad[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        near |= hit & (nb < depth - dthr)
    sh = np.where(near & ~emis, sh - 1.6, sh)
    # rim light on the silhouette edge away from the key light (right and bottom)
    bg_r = np.pad(~hit, ((0, 0), (0, 1)), constant_values=True)[:, 1:]
    bg_d = np.pad(~hit, ((0, 1), (0, 0)), constant_values=True)[1:, :]
    rim = hit & (bg_r | bg_d) & ~emis
    sh = np.where(rim, sh + opts.get("rim", 1.3), sh)
    # sparkles on gold
    spark = gold & (hash3(xx, yy, 7) < 0.025) & (ndl > 0.4) & (shadow < 0.5)
    idx = tone + sh + BAYER[yy % 4, xx % 4] * opts.get("dither", 0.45)
    img = np.zeros((H, W, 4), np.uint8)
    for i, m in enumerate(M.list):
        if m is None:
            continue
        sel = hit & (mat == i)
        if not sel.any():
            continue
        r = np.array(m["ramp"], np.uint8)
        j = np.clip(np.floor(idx[sel] + 0.5), 0, len(r) - 1).astype(int)
        img[sel, :3] = r[j]
        if m["gold"]:
            sp = spark[sel]
            img[np.nonzero(sel)[0][sp], np.nonzero(sel)[1][sp], :3] = r[-1]
    img[hit, 3] = 255
    return img, emis


def glow_layer(emis_rgb, emis_mask, radius, strength, H, W):
    """A stepped (dithered) glow around emissive pixels, as RGBA."""
    rgb = np.zeros((H, W, 3), np.float32)
    rgb[emis_mask] = emis_rgb[emis_mask]
    im = Image.fromarray(rgb.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    a = Image.fromarray((emis_mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    c = np.array(im, np.float32)
    al = np.array(a, np.float32) / 255 * strength
    c = c / np.maximum(al[..., None] / strength, 1e-3)
    yy, xx = np.mgrid[0:H, 0:W]
    al = np.floor(np.clip(al + BAYER[yy % 4, xx % 4] * 0.18, 0, 1) * 4) / 4
    out = np.zeros((H, W, 4), np.float32)
    out[..., :3] = np.clip(c, 0, 255)
    out[..., 3] = al
    return out


def over(dst, src):
    """Alpha composite float RGBA (alpha 0..1) src over dst, both float."""
    a = src[..., 3:4]
    out = dst.copy()
    out[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    out[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    return out


def to_f(img):
    f = img.astype(np.float32)
    f[..., 3] /= 255
    return f


def to_u8(f):
    o = f.copy()
    o[..., 3] *= 255
    return np.clip(np.round(o), 0, 255).astype(np.uint8)


def outline(img, color=PLUM, width=1, mask=None):
    """Add a pixel outline around the opaque area (4-neighbour, then 8 for width 2)."""
    a = img[..., 3] > 127 if mask is None else mask
    H, W = a.shape
    grown = a.copy()
    cur = a.copy()
    for w in range(width):
        p = np.pad(cur, 1)
        nb = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
        if w > 0:
            nb |= p[:-2, :-2] | p[2:, 2:] | p[:-2, 2:] | p[2:, :-2]
        cur = cur | nb
    ring = cur & ~a
    out = img.copy()
    out[ring, :3] = color
    out[ring, 3] = 255
    return out


# ---------------------------------------------------------------- shapes
def doll_profile(h):
    """Radius of a matryoshka at height fraction h (0 base, 1 top), radius 1 at the widest."""
    pts = [(0.0, 0.70), (0.03, 0.84), (0.12, 0.96), (0.24, 1.0), (0.36, 0.97), (0.48, 0.86), (0.56, 0.72),
           (0.61, 0.62), (0.65, 0.60), (0.70, 0.62), (0.78, 0.62), (0.86, 0.57), (0.92, 0.47), (0.96, 0.35),
           (0.985, 0.22), (1.0, 0.0)]
    xs, ys = zip(*pts)
    return np.interp(h, xs, ys)


def screen_coords(G, cam):
    """Screen coordinates of every voxel centre, so faces can be painted as decals projected from the camera."""
    su = G.X * cam.right[0] + G.Y * cam.right[1] + G.Z * cam.right[2]
    sv = G.X * cam.up[0] + G.Y * cam.up[1] + G.Z * cam.up[2]
    return su, sv, max(0.5, float(cam.up[2]))


def paint_doll(G, M, inside, lx, ly, lz, H, R, front=(0, 1, 0), detail=1.0, belly="block", dots=True, scr=None, face_k=1.0):
    """Paint a doll on the voxels `inside` (bool) given local coords (lx lateral right, ly toward front, lz up from
    base) scaled by H (height) and R (max radius). Face toward +ly."""
    h = lz / H
    # head geometry
    hc = 0.80 * H        # head centre height
    put = G.put
    put(inside, M["red"], 3.4)
    # scarf darker toward the back
    back = inside & (ly < -0.2 * R)
    G.tone[back] -= 0.4
    # face oval, planar on the front (wider than tall, like the poster doll)
    fw, fh, fcz = 0.42 * R * face_k, 0.135 * H * face_k, hc - 0.02 * H
    if scr is not None:
        # project the face from the camera: find the face centre on screen, use screen offsets as face coordinates
        su, sv, k = scr
        ref = inside & (ly > 0) & (np.abs(lx) < 1.2) & (np.abs(lz - fcz) < 1.2)
        if ref.any():
            ref &= ly > ly[ref].max() - 1.5     # the front surface only, not the whole column through the head
            # the frontmost of those voxels
            u0, v0 = su[ref].mean(), sv[ref].mean()
            lx = np.where(ly > 0, su - u0, lx)
            lz = np.where(ly > 0, (sv - v0) / k + fcz, lz)
    fx, fz = lx / fw, (lz - fcz) / fh
    e = fx ** 2 + fz ** 2
    face = inside & (ly > 0) & (e < 1)
    rim = inside & (ly > 0) & (e < 1.30) & ~face
    put(rim, M["gold"], 3.4)
    put(inside & (ly > 0) & (e >= 1.30) & (e < 1.55), M["red"], 2.2)
    put(face, M["cream"], 3.8)
    G.tone[face & (fx > 0.55)] -= 0.5
    if fw < 6.5:
        hair = face & (fz > 0.28 - 0.25 * np.abs(fx) ** 2)
    else:
        hair = face & (fz > 0.30 - 0.38 * np.abs(fx) ** 2.2)
    put(hair, M["hair"], 1.4)
    put(hair & (fz > 0.55) & (np.abs(fx) < 0.5), M["hair"], 2.4)
    # eyes, cheeks, mouth
    small = fw < 6.5
    ew = 0.9 if small else max(0.85, 0.11 * fw * detail)
    ez = fcz - (0.30 if small else 0.14) * fh
    for sx in (-1, 1):
        ecx = sx * 0.40 * fw
        eye = face & (np.abs(lx - ecx) < ew + 0.05) & (np.abs(lz - ez) < ew * 1.35 + 0.05)
        put(eye, M["black"], 0.2)
        if detail >= 0.9 and fw >= 6.5:
            put(eye & (np.abs(lx - (ecx - sx * ew * 0.45)) < 0.55) & (np.abs(lz - (ez + ew * 0.75)) < 0.55), M["cream"], 5.0)
        ck = face & ((lx - sx * 0.62 * fw) ** 2 / (0.18 * fw) ** 2 + (lz - (fcz - (0.60 if small else 0.50) * fh)) ** 2 / (0.13 * fh + 0.4) ** 2 < 1)
        put(ck & ~eye, M["pink"], 2.4)
    mouth = face & (np.abs(lx) < 0.12 * fw + 0.1) & (np.abs(lz - (fcz - (0.76 if small else 0.66) * fh)) < 0.09 * fh + 0.1)
    put(mouth, M["red"], 3.0)
    # body apron: an oval on the belly
    if belly:
        bz = 0.33 * H
        bx_, bz_ = lx / (0.62 * R), (lz - bz) / (0.27 * H)
        e = bx_ ** 2 + bz_ ** 2
        front_b = inside & (ly > 0.1 * R)
        ap = front_b & (e < 1)
        put(front_b & (e >= 1) & (e < 1.22), M["gold"], 3.0)
        if belly == "black":
            put(ap, M["black"], 2.2)
        elif belly == "cream":
            put(ap, M["cream"], 3.4)
        elif belly == "block":
            put(ap, M["black"], 2.0)
        # gold leaf dots round the apron
        for k in range(12 if dots else 0):
            a = math.radians(k * 30 + 15)
            px, pz = math.cos(a) * 0.62 * R * 1.42, bz + math.sin(a) * 0.27 * H * 1.36
            dd = front_b & (np.abs(lx - px) + np.abs(lz - pz) < 1.3)
            put(dd & (h < 0.6), M["gold"], 4.0)
    return face


def paint_flower(G, M, mask, u, v, r, petals=6, center="red", leaves=True):
    """A khokhloma flower (gold petals, red heart, curling gold leaves), planar coords u (right) v (up), size r."""
    rr = np.hypot(u, v)
    ang = np.arctan2(v, u)
    pet = mask & (rr < r) & (rr > 0.32 * r) & (np.cos(ang * petals) > -0.05 + 0.9 * (rr / r - 0.32))
    G.put(pet, M["gold"], 3.7)
    G.put(pet & (rr < 0.62 * r) & (np.cos(ang * petals) > 0.6), M["gold"], 4.8)
    G.put(mask & (rr <= 0.36 * r), M[center], 4.4 if center == "red" else 3.6)
    G.put(mask & (rr <= 0.14 * r + 0.5), M["gold"], 5.0)
    if leaves:
        for sx in (-1, 1):
            lu, lv = u - sx * 1.25 * r, v + 0.55 * r
            le = (lu / (0.55 * r)) ** 2 + ((lv - 0.25 * lu * sx) / (0.24 * r)) ** 2 < 1
            G.put(mask & le, M["gold"], 3.2)
            G.put(mask & le & (np.abs(lv - 0.25 * lu * sx) < 0.5), M["gold"], 2.2)
            b = np.hypot(u - sx * 1.05 * r, v - 0.75 * r) < 0.22 * r + 0.4
            G.put(mask & b, M["red"], 5.0)


def save(img, path):
    Image.fromarray(img).save(path)


# ---------------------------------------------------------------- concept B: the world block
def concept_B(art=ART, pad_frac=0.05, plate="outline"):
    M = base_mats()
    M.add("light", GOLD, emissive=True)
    M.add("rawwood", WOOD)
    S = 44
    G = Grid((S, S, S + 16))
    X, Y, Z = G.X, G.Y, G.Z
    c = S / 2
    cheb = np.maximum(np.maximum(np.abs(X - c), np.abs(Y - c)), np.abs(Z - c))
    S2, S3 = 32, 26
    xi, yi, zi = (np.floor(X).astype(int), np.floor(Y).astype(int), np.floor(Z).astype(int))

    def jag(a, b, seed, amp=3, cell=2):
        return np.floor(hash3(a // cell, b // cell, seed) * (amp + 1))

    # the break: the corner toward the camera (+x +y +z), ragged on the lacquer, clean through the inner shell
    d = 6.0
    skin = cheb >= S / 2 - 2
    cut = ((X > c - d + np.where(skin, jag(yi, zi, 1, 2), 0)) & (Y > c - d + np.where(skin, jag(xi, zi, 2, 2), 0))
           & (Z > c - d + np.where(skin, jag(xi, yi, 3, 2), 0)))
    shell1 = (cheb < S / 2) & (cheb >= S2 / 2) & ~cut
    shell2 = (cheb < S2 / 2) & (cheb >= S3 / 2) & ~cut
    # shell 1: raw wood, red lacquer skin outside, grass on top with drips
    G.put(shell1, M["rawwood"], 4.4)
    G.tone[shell1] += (hash3(xi, yi // 3, zi // 2, 11)[shell1] - 0.5) * 0.8
    skin1 = shell1 & (cheb >= S / 2 - 1)
    G.put(skin1, M["red"], 3.4)
    drip = np.floor(hash3(np.minimum(xi, yi), np.maximum(xi, yi), 9) * 5)
    grass = shell1 & (Z >= S - 3 - np.where(cheb >= S / 2 - 1, drip, 0)) & ((Z >= S - 1) | (cheb >= S / 2 - 1))
    G.put(grass, M["grass"], 4.0)
    G.tone[grass] += (hash3(xi, yi, zi, 12)[grass] - 0.5) * 1.6
    # gold edges round the lacquer
    ex = (np.abs(X - c) >= S / 2 - 1)
    ey = (np.abs(Y - c) >= S / 2 - 1)
    ez = (Z < 1.0)
    edges = skin1 & ~grass & ((ex & ey) | (ex & ez) | (ey & ez))
    G.put(edges, M["gold"], 3.4)
    near_cut = np.zeros_like(cut)
    for ax in range(3):
        for sh_ in (-1, 1):
            near_cut |= np.roll(cut, sh_, ax)
    lip = skin1 & near_cut & ~grass
    # khokhloma rosette on the two front faces, under the break
    for face_axis in (0, 1):
        A = Y if face_axis == 0 else X
        on = skin1 & ((X >= S - 1) if face_axis == 0 else (Y >= S - 1))
        u, v = A - (c + S / 4 - 2), Z - (c - S / 4 - 0.5)
        r = np.hypot(u, v)
        ang = np.arctan2(v, u)
        petal = (r < 5.8) & (r > 1.6) & (np.cos(ang * 6) > 0.1 + (r - 2) / 8)
        G.put(on & petal, M["gold"], 3.6)
        G.put(on & (r < 1.8), M["gold"], 4.6)
        # the far half of the face: a gold vine with leaves
        u2 = A - (c - S / 4)
        vine = on & (np.abs(Z - (c + 2 + 3.5 * np.sin(u2 / 3.2))) < 0.7) & (A < c - 8) & (Z < S - 6)
        G.put(vine, M["gold"], 3.2)
        leaf = on & (A < c - 8) & (Z < S - 6) & (np.abs(np.mod(u2, 6.4) - 3.2) < 1.2) & (np.abs(Z - (c + 2 + 3.5 * np.sin(u2 / 3.2)) - 2.0 * np.sign(np.sin(u2 / 6.4 * math.pi))) < 1.2)
        G.put(leaf, M["gold"], 4.2)
    G.put(lip, M["gold"], 4.2)
    # the ten worlds: one small gem per world set in the gold edges and corners (a U from the left edge to the right)
    gem_ids = [M.add(f"gem{i + 1}", rmp, gloss=True) for i, rmp in enumerate(world_gems())]
    E = S - 0.5
    spots = [(E, 0.5, 31), (E, 0.5, 16), (E, 13, 0.5), (E, 27, 0.5), (E, E, 0.5), (E, E, 12),
             (27, E, 0.5), (13, E, 0.5), (0.5, E, 16), (0.5, E, 31)]
    for i, (gx, gy, gz) in enumerate(spots):
        dd = np.maximum(np.maximum(np.abs(X - gx), np.abs(Y - gy)), np.abs(Z - gz))
        bez = skin1 & (dd < 3.1) & ~grass
        G.put(bez, M["gold"], 4.4)
        gem = (cheb < S / 2) & (cheb >= S / 2 - 1.01) & (dd < 2.1)
        gem &= ~cut
        G.put(gem, gem_ids[i], 4.0)
        G.tone[gem] += np.clip((Z - gz) * 0.35, -0.8, 0.8)[gem] + 1.3 * (Y >= S - 1)[gem] * (X < S - 1)[gem]
        G.lit[gem] = True
    # shell 2: black lacquer skin outside, wood, its inside lit (the light of the world block)
    G.put(shell2, M["rawwood"], 3.4)
    G.tone[shell2] += (hash3(xi // 2, yi, zi // 3, 13)[shell2] - 0.5) * 0.8
    G.put(shell2 & (cheb >= S2 / 2 - 1), M["black"], 2.6)
    G.put(shell2 & (cheb >= S2 / 2 - 1) & ((xi + yi + zi) % 3 == 0) & (hash3(xi, yi, zi, 5) < 0.4), M["gold"], 3.6)
    G.put(shell2 & (cheb < S3 / 2 + 1), M["light"], 4.8)
    # warm light spilling out of the breach: surfaces near the cut are brightened (the grass and lacquer turn gold)
    warm = box_blur3(cut & (cheb < S / 2), 4)
    spill = (G.mat > 0) & ~cut & np.isin(G.mat, [M["grass"], M["red"], M["gold"], M["rawwood"], M["black"]])
    G.tone[spill] += np.clip(warm[spill] * 6.0 - 0.3, 0, 2.4)
    # where the light is strongest the grass and the lacquer take its colour
    M.add("grasslit", [mix(g, (255, 214, 110), t) for g, t in zip(GRASS, (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7))])
    M.add("redlit", [mix(r_, (255, 190, 90), t) for r_, t in zip(RED, (0.05, 0.1, 0.18, 0.26, 0.34, 0.45, 0.6))])
    hot = spill & (warm > 0.12)
    G.mat[hot & (G.mat == M["grass"])] = M["grasslit"]
    G.mat[hot & (G.mat == M["red"])] = M["redlit"]
    G.lit[spill & (warm > 0.15)] = True
    # the next doll, standing in the lit heart of the block and coming out through the break
    yaw = 40
    fa = math.radians(yaw)
    fwd = (math.cos(fa), math.sin(fa))
    rgt = (-math.sin(fa), math.cos(fa))
    dH, dR = DOLL_B
    px, py, base = c + 4.0, c + 4.0, c - S3 / 2
    qx, qy, qz = X - px, Y - py, Z - base
    doll, _, _ = doll_solid(G, qx, qy, qz, dH, dR, 0, dH)
    G.mat[doll] = 0
    G.smooth[doll] = 1.0
    camB = Camera(yaw, 30)
    dlx, dly = qx * rgt[0] + qy * rgt[1], qx * fwd[0] + qy * fwd[1]
    paint_doll(G, M, doll, dlx, dly, qz, dH, dR, belly=None, dots=False, detail=1.0, scr=screen_coords(G, camB))
    paint_flower(G, M, doll & (dly > 0), dlx, qz - 0.40 * dH, 5.5, leaves=False)
    G.lit[doll] = True
    cam = Camera(yaw, 30)
    pad = art * pad_frac
    buf = render(G, M, cam, art, art, (pad, pad, art - pad, art - pad))
    img, emis = shade(buf, M, cam, dict(gloss_band=(art * 0.42, art * 0.03), emis_tone=0.6, contrast=0.85))
    return img, emis, dict(plate=plate, finish=dict(glow=(7, 0.9), glow_col=(255, 210, 110), glow_over=0.35))


DOLL_B = (45.0, 14.8)


# ---------------------------------------------------------------- plates and finishing
def dramp(pal, v, yy, xx, dither=0.6):
    i = np.clip(np.floor(v + BAYER[yy % 4, xx % 4] * dither + 0.5), 0, len(pal) - 1).astype(int)
    return np.array(pal, np.uint8)[i]


def rrect_sdf(W, H, m, r):
    yy, xx = np.mgrid[0:H, 0:W] + 0.5
    qx = np.abs(xx - W / 2) - (W / 2 - m - r)
    qy = np.abs(yy - H / 2) - (H / 2 - m - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def lacquer_plate(W, H, base=None, m=3, r=34):
    """Rounded square of deep red-black lacquer, gold rim, a khokhloma vine border with berries."""
    base = base or [(14, 4, 8), (24, 6, 12), (38, 8, 14), (56, 10, 18), (80, 14, 22)]
    yy, xx = np.mgrid[0:H, 0:W]
    d = rrect_sdf(W, H, m, r)
    inside = d < 0
    img = np.zeros((H, W, 4), np.uint8)
    # lacquer: lighter toward the upper middle (lamp reflected in the varnish), dark at the edges
    cx, cy = W * 0.5, H * 0.42
    rr = np.hypot((xx - cx) / W, (yy - cy) / H)
    v = 3.2 - rr * 5.0 + np.clip(-d / 30, 0, 1) * 0.6
    img[..., :3] = dramp(base, v, yy, xx, 0.8)
    img[..., 3] = np.where(inside, 255, 0)
    # rims: outer plum line, gold band, thin black, then the field
    img[(d >= -1.5) & inside, :3] = PLUM
    g = (d < -1.5) & (d >= -4.5)
    gv = 3.7 + 2.6 * (0.5 - (xx + yy) / (W + H)) - 0.8 * (d < -3.5)
    img[g, :3] = dramp(GOLD, gv, yy, xx)[g]
    img[(d < -4.5) & (d >= -5.5), :3] = BLACK[0]
    # inner gold hairline with dots, and a khokhloma flower in each corner
    hl = (d < -8.0) & (d >= -9.0)
    img[hl, :3] = dramp(GOLD, 2.6 + 1.0 * (yy < H / 2), yy, xx)[hl]
    t = (np.arctan2(yy + 0.5 - H / 2, xx + 0.5 - W / 2) / (2 * math.pi) * 64) % 1.0
    dots = (np.abs(d + 12.0) < 1.1) & ((t < 0.12) | (t > 0.88))
    img[dots, :3] = GOLD[4]
    for cx_, cy_, rot in ((22, 22, 0), (W - 23, 22, 1), (22, H - 23, 3), (W - 23, H - 23, 2)):
        u, v = xx + 0.5 - cx_, yy + 0.5 - cy_
        rr = np.hypot(u, v)
        an = np.arctan2(v, u)
        pet = (rr < 8.5) & (rr > 3.0) & (np.cos(an * 5 + rot) > -0.1 + 0.9 * (rr - 3) / 5.5)
        img[pet, :3] = dramp(GOLD, 3.4 + 1.2 * (v < 0), yy, xx)[pet]
        img[rr < 3.2, :3] = RED[4]
        img[rr < 1.6, :3] = GOLD[5]
        img[(rr >= 8.5) & (rr < 9.6) & inside & (d < -9), :3] = BLACK[0]
        # berries along the diagonal toward the centre
        for k, (du, dv) in enumerate(((11, 4), (4, 11))):
            sx = 1 if cx_ < W / 2 else -1
            sy = 1 if cy_ < H / 2 else -1
            bb = np.hypot(u - sx * du, v - sy * dv) < 2.0
            img[bb, :3] = RED[4]
            img[np.hypot(u - sx * du + 0.6, v - sy * dv + 0.6) < 0.8, :3] = RED[6]
    return img, d


def finish(img, emis, plate, W=ART, H=ART, glow=(10, 0.9), glow_col=None, glow_over=0.0):
    """Compose plate, glow, subject and outline into an RGBA art-resolution image."""
    out = np.zeros((H, W, 4), np.float32)
    pd = None
    if plate == "lacquer":
        p, pd = lacquer_plate(W, H)
        out = to_f(p)
    sub = to_f(img)
    em_rgb = img[..., :3].astype(np.float32)
    if glow_col is not None:
        em_rgb[:] = glow_col
    if emis.any() and glow:
        gl = glow_layer(em_rgb, emis, glow[0], glow[1], H, W)
        if pd is not None:
            gl[..., 3] *= (pd < -6)
        out = over(out, gl)
    # subject with its plum outline
    a = img[..., 3] > 127
    ol = outline(img, PLUM, 1)
    out = over(out, to_f(ol))
    if glow_over and emis.any():
        # the light also falls on the subject: a stepped warm wash, only where the subject is not itself emissive
        gl = glow_layer(em_rgb, emis, glow[0] * 1.6, glow_over, H, W)
        gl[..., 3] *= (img[..., 3] > 0) & ~emis
        add = gl[..., :3] * gl[..., 3:4] * 0.55
        out[..., :3] = np.clip(out[..., :3] + add, 0, 255)
    return to_u8(out)


def downs_px(art, n, contrast=1.12):
    """Pixel downscale for the small sizes: per block, the block's own pixel closest to the block's mean colour
    (so every output pixel is a real palette colour, no blur); alpha by coverage; a touch more contrast."""
    H = art.shape[0]
    k = H // n
    f = art.astype(np.float32)
    blk = f.reshape(n, k, n, k, 4).transpose(0, 2, 1, 3, 4).reshape(n, n, k * k, 4)
    a = blk[..., 3] / 255
    cov = a.mean(-1)
    w = a / np.maximum(a.sum(-1, keepdims=True), 1e-6)
    mean = (blk[..., :3] * w[..., None]).sum(-2)
    lum = mean.mean(-1, keepdims=True)
    mean = np.clip(lum + (mean - lum) * contrast, 0, 255)
    d = ((blk[..., :3] - mean[..., None, :]) ** 2).sum(-1) + (a < 0.5) * 1e9
    pick = d.argmin(-1)
    rgb = np.take_along_axis(blk[..., :3], pick[..., None, None], axis=2)[..., 0, :]
    out = np.zeros((n, n, 4), np.uint8)
    out[..., :3] = rgb
    out[..., 3] = np.where(cov >= 0.45, 255, 0)
    return out


def downs_q(img1024, n, colors=40):
    """Small sizes: box downscale, a light unsharp mask, then snapped to its own 40-colour palette with no dither
    (flat pixel clusters instead of blur); alpha cut at 45 % coverage so the edge stays a clean pixel outline."""
    box = downs(img1024, n)
    im = Image.fromarray(box)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(1.0, 80, 0))
    q = rgb.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    return np.dstack([np.asarray(q), np.where(box[..., 3] > 115, 255, 0)]).astype(np.uint8)


def downs(img1024, n):
    """Box-filter downscale of the 1024 image (premultiplied) then a light snap of alpha."""
    im = Image.fromarray(img1024)
    f = np.asarray(im, np.float32) / 255
    pm = f.copy()
    pm[..., :3] *= pm[..., 3:4]
    k = img1024.shape[0] // n
    pm = pm.reshape(n, k, n, k, 4).mean((1, 3))
    a = pm[..., 3:4]
    rgb = np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0)
    o = np.concatenate([rgb, a], -1)
    return np.clip(o * 255 + 0.5, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- concept A: the opening
def doll_solid(G, qx, qy, qz, H, R, z0, z1, wall=None):
    """Voxels of a doll (solid of revolution) between heights z0 and z1 in local coords; hollow if wall."""
    rad = np.hypot(qx, qy)
    rr = R * doll_profile(np.clip(qz / H, 0, 1))
    m = (qz >= z0) & (qz < z1) & (rad < rr) & (qz >= 0) & (qz < H)
    if wall:
        m &= (rad >= rr - wall) | (qz < 1.5)
    return m, rad, rr


def concept_A(art=ART):
    M = base_mats()
    M.add("flower_r", RED)
    M.add("flower_y", GOLD)
    H, R = 76.0, 25.0
    NX = NY = 64
    NZ = 112
    G = Grid((NX, NY, NZ))
    X, Y, Z = G.X, G.Y, G.Z
    yaw = 45
    a = math.radians(yaw)
    fwd = np.array([math.cos(a), math.sin(a)])
    rgt = np.array([-math.sin(a), math.cos(a)])
    ox, oy = NX / 2, NY / 2
    zc = 0.42 * H
    # ---- bottom half, hollow, at the origin
    qx, qy, qz = X - ox, Y - oy, Z - 1.0
    lx = qx * rgt[0] + qy * rgt[1]
    ly = qx * fwd[0] + qy * fwd[1]
    bot, rad, rr = doll_solid(G, qx, qy, qz, H, R, 0, zc, wall=2.6)
    G.smooth[bot] = 1.0
    sel = bot
    tmp = Grid(G.shape)
    tmp.mat, tmp.tone = G.mat, G.tone
    G.mat[bot] = M["red"]
    G.tone[bot] = 3.4
    # paint the bottom (copy paint into only bot voxels)
    m0, t0 = G.mat.copy(), G.tone.copy()
    paint_doll(G, M, bot, lx, ly, qz, H, R, belly=None)
    paint_flower(G, M, bot & (ly > 0), lx - 6.0, qz - 0.20 * H, 7.0)
    # gold rim at the cut, and the raw wood of the cut ring on top
    G.put(bot & (qz >= zc - 2.0) & (rad >= rr - 1.0), M["gold"], 3.8)
    G.put(bot & (qz >= zc - 1.0) & (rad < rr - 1.0), M["wood"], 5.0)
    G.put(bot & (qz < 1.0) & (rad >= rr - 1.2), M["gold"], 3.0)
    # ---- the world inside
    rin = rr - 2.6
    hill = (3.0 * np.exp(-((lx + 8) ** 2 + (ly + 10) ** 2) / 60) + 1.2 * np.sin(lx / 4.0) * np.cos(ly / 5.0))
    surf = zc - 1.5 + np.floor(hill)
    inside = (rad < rin) & (qz >= 1.5) & (qz < surf + 1)
    G.put(inside, M["dirt"], 2.6)
    G.tone[inside] += (hash3(np.floor(X), np.floor(Y), np.floor(Z), 21)[inside] - 0.5) * 1.2
    top = inside & (qz >= surf)
    G.put(top, M["grass"], 4.0)
    G.tone[top] += (hash3(np.floor(X), np.floor(Y), 0, 22)[top] - 0.5) * 1.4
    G.lit[inside] = True
    # pool and waterfall over the rim, front-left
    pool = (rad < rin) & (np.hypot(lx + 7, ly - 11) < 6.0) & (qz >= surf - 1) & (qz < surf + 1)
    G.mat[pool & (qz >= surf)] = 0
    G.put(pool & (qz < surf), M["water"], 3.6)
    # the fall: a sheet of water down the outside of the doll from the pool's lip
    fall = (np.abs(lx + 7) < 2.6) & (ly > 0) & (rad >= rr - 0.2) & (rad < rr + 1.6) & (qz < zc + 0.5) & (qz >= 0)
    G.put(fall, M["water"], 4.0)
    G.tone[fall] += np.where(hash3(np.floor(X), np.floor(Y), np.floor(Z) // 3, 23)[fall] < 0.3, 1.5, 0)
    lip = (np.abs(lx + 7) < 2.6) & (ly > 0) & (rad >= rin - 0.5) & (rad < rr + 1.6) & (qz >= zc - 1) & (qz < zc + 0.5)
    G.put(lip, M["water"], 4.6)
    foam = (np.abs(lx + 7) < 3.6) & (ly > 0) & (rad >= rr - 0.2) & (rad < rr + 2.6) & (qz < 2.2)
    G.put(foam, M["water"], 5.5)
    G.lit[fall | lip | pool | foam] = True
    # trees: trunk and a blocky crown
    def tree(tx, ty, h, cr, seed):
        px = ox + tx * rgt[0] + ty * fwd[0]
        py = oy + tx * rgt[1] + ty * fwd[1]
        base = zc - 1.5 + math.floor(3.0 * math.exp(-((tx + 8) ** 2 + (ty + 10) ** 2) / 60) + 1.2 * math.sin(tx / 4) * math.cos(ty / 5)) + 1
        trunk = (np.abs(X - px) < 1.0) & (np.abs(Y - py) < 1.0) & (qz >= base - 1) & (qz < base + h)
        G.put(trunk, M["bark"], 2.4)
        cz = base + h + 1
        crown = ((np.abs(X - px) ** 2.5 + np.abs(Y - py) ** 2.5) ** 0.4 < cr) & (np.abs(qz - cz) < cr * 0.7)
        crown |= ((np.abs(X - px) ** 2.5 + np.abs(Y - py) ** 2.5) ** 0.4 < cr * 0.6) & (qz - cz >= 0) & (qz - cz < cr * 1.1)
        crown &= hash3(np.floor(X), np.floor(Y), np.floor(Z), seed) < 0.95
        G.put(crown, M["leaf"], 3.4)
        G.tone[crown] += (hash3(np.floor(X), np.floor(Y), np.floor(Z), seed + 1)[crown] - 0.5) * 1.6
        G.lit[trunk | crown] = True
    tree(-9, -9, 5, 4.0, 31)
    tree(9, -4, 4, 3.5, 33)
    # flowers
    fl = top & (hash3(np.floor(X), np.floor(Y), 1, 40) < 0.018) & ~pool
    above = np.roll(fl, 1, axis=2) & (G.mat == 0)
    G.put(above, M["flower_r"], 4.5)
    # ---- the next doll, peeking out at the front right
    sH, sR = H * 0.42, R * 0.42
    sx_, sy_ = 7.5, 6.0
    px = ox + sx_ * rgt[0] + sy_ * fwd[0]
    py = oy + sx_ * rgt[1] + sy_ * fwd[1]
    sb = zc - 2.0 - sH * 0.45
    q2x, q2y, q2z = X - px, Y - py, Z - 1 - sb
    small, _, _ = doll_solid(G, q2x, q2y, q2z, sH, sR, 0, sH)
    small &= (q2z > sH * 0.40)
    G.mat[small] = 0
    G.smooth[small] = 1.0
    camA = Camera(yaw, 28)
    scrA = screen_coords(G, camA)
    paint_doll(G, M, small, q2x * rgt[0] + q2y * rgt[1], q2x * fwd[0] + q2y * fwd[1], q2z, sH, sR, belly=None, detail=0.6,
               scr=scrA)
    G.lit[small] = True
    # ---- top half, lifted and tipped back
    lift, tilt, back = 0.22 * H, math.radians(14), 8.0
    # inverse transform: p -> q (rotate about the lateral axis through the rim's back edge)
    piv = np.array([ox - fwd[0] * R * 0.6, oy - fwd[1] * R * 0.6, 1.0 + zc])
    px_, py_, pz_ = X - piv[0] + fwd[0] * back, Y - piv[1] + fwd[1] * back, Z - piv[2] - lift
    f_ = px_ * fwd[0] + py_ * fwd[1]
    r_ = px_ * rgt[0] + py_ * rgt[1]
    ct, st = math.cos(tilt), math.sin(tilt)
    f2 = f_ * ct + pz_ * st
    z2 = -f_ * st + pz_ * ct
    # back to doll-local
    f2 = f2 - R * 0.6
    z2 = z2 + zc
    tq_x = f2 * fwd[0] + r_ * rgt[0]
    tq_y = f2 * fwd[1] + r_ * rgt[1]
    topm, trad, trr = doll_solid(G, tq_x, tq_y, z2, H, R, zc, H, wall=2.6)
    G.mat[topm] = M["red"]
    G.tone[topm] = 3.4
    G.smooth[topm] = 1.0
    paint_doll(G, M, topm, r_, f2, z2, H, R, belly=None, scr=scrA)
    # gold leaves on the shoulders
    for k in range(9):
        aa = math.radians(-60 + k * 15)
        pu, pz = math.sin(aa) * R * 0.95, 0.52 * H + 2.0 * math.cos(aa * 2)
        G.put(topm & (f2 > 0) & (np.abs(r_ - pu) + np.abs(z2 - pz) < 1.4), M["gold"], 4.0)
    G.put(topm & (z2 < zc + 2.0) & (trad >= trr - 1.0), M["gold"], 3.8)
    G.put(topm & (z2 < zc + 1.0) & (trad < trr - 1.0), M["wood"], 3.0)
    cam = Camera(yaw, 28)
    pad = art * 0.05
    buf = render(G, M, cam, art, art, (pad + 8, pad, art - pad - 8, art - pad))
    img, emis = shade(buf, M, cam, dict(gloss_band=(art * 0.40, art * 0.025), edge=7.0))
    world = np.isin(buf["mat"], [M["grass"], M["water"], M["leaf"]]) & buf["hit"]
    return img, world, dict(plate="lacquer", finish=dict(glow=(12, 0.85), glow_col=(255, 214, 120)))


# ---------------------------------------------------------------- concept C: the guardian
def world_gems():
    from content import WORLDS
    return [gem_ramp(w["pal"]) for w in WORLDS]


def concept_C(art=ART):
    M = base_mats()
    gems = []
    for i, rmp in enumerate(world_gems()):
        gems.append(M.add(f"gem{i + 1}", rmp, gloss=True))
    NX, NY, NZ = 104, 86, 112
    G = Grid((NX, NY, NZ))
    X, Y, Z = G.X, G.Y, G.Z
    cx, cz = NX / 2, 52.0
    Rd = 47.0
    # ---- the medallion: black lacquer field, raised gold rim, ten gems
    u, v = X - cx, Z - cz
    rr = np.hypot(u, v)
    an = np.degrees(np.arctan2(v, u))
    disk = (rr < Rd) & (Y >= 6) & (Y < 13)
    rimz = (rr >= Rd - 7) & (rr < Rd) & (Y >= 6) & (Y < 15)
    G.put(disk, M["black"], 2.4)
    G.put(rimz, M["gold"], 3.6)
    G.put(rimz & (rr >= Rd - 1.2), M["gold"], 2.6)
    G.put(rimz & (rr < Rd - 6), M["gold"], 2.4)
    # the field: plain black lacquer, a gold hairline, red berries in pairs of gold leaves
    fld = disk & (Y >= 12) & (rr < Rd - 7)
    G.put(fld & (np.abs(rr - (Rd - 9.2)) < 0.7), M["gold"], 3.2)
    for k in range(16):
        a = math.radians(k * 22.5 + 11.25)
        px, pz = cx + math.cos(a) * (Rd - 13), cz + math.sin(a) * (Rd - 13)
        G.put(fld & (np.hypot(X - px, Z - pz) < 1.6), M["red"], 4.4)
    # ten gems set in the rim, round the lower 300 degrees (the head breaks the top)
    for i in range(10):
        a = math.radians(-90 + (i - 4.5) * 31.0)
        a = math.radians(90 + 30 + i * (300 / 9.0))
        gx, gz = cx + math.cos(a) * (Rd - 3.5), cz + math.sin(a) * (Rd - 3.5)
        bez = (np.hypot(X - gx, Z - gz) < 5.2) & (Y >= 6) & (Y < 16)
        G.put(bez, M["gold"], 4.4)
        G.put(bez & (np.hypot(X - gx, Z - gz) >= 4.4), M["gold"], 2.6)
        gem = (np.maximum(np.abs(X - gx), np.abs(Z - gz)) < 3.4) & (Y >= 6) & (Y < 18)
        G.put(gem, gems[i], 3.8)
        G.tone[gem] += np.clip(((gx - X) + (Z - gz)) * 0.22, -1.2, 1.2)[gem]
        G.put(gem & (np.abs(X - (gx - 1.5)) < 0.6) & (np.abs(Z - (gz + 1.5)) < 0.6), gems[i], 6.0)
        G.lit[gem] = True
    G.lit[disk | rimz] = False
    # ---- the doll in front
    H, R = 80.0, 26.0
    dcx, dcy, base = cx, 15 + R * 0.62, 26.0
    qx, qy, qz = X - dcx, Y - dcy, Z - base
    doll, rad, rrd = doll_solid(G, qx, qy, qz, H, R, 0, H)
    G.mat[doll] = M["red"]
    G.smooth[doll] = 1.0
    lx, ly = qx, qy
    paint_doll(G, M, doll, lx, ly, qz, H, R, belly="black", dots=False, scr=screen_coords(G, Camera(84, 12)), face_k=1.16)
    # a world block set in the belly: grass top, lacquer sides, gold edges
    bs = 12
    bxc, byc, bzc = dcx, dcy + R * 0.86, base + 0.33 * H
    blk = (np.abs(X - bxc) < bs / 2) & (np.abs(Y - byc) < bs / 2) & (np.abs(Z - bzc) < bs / 2)
    G.put(blk, M["dirt"], 3.0)
    G.put(blk & (Z >= bzc + bs / 2 - 2.5), M["grass"], 4.2)
    G.tone[blk] += (hash3(np.floor(X), np.floor(Y), np.floor(Z), 51)[blk] - 0.5) * 1.4
    edge = blk & (((np.abs(X - bxc) >= bs / 2 - 1).astype(int) + (np.abs(Y - byc) >= bs / 2 - 1) + (np.abs(Z - bzc) >= bs / 2 - 1)) >= 2)
    G.put(edge & (Z < bzc + bs / 2 - 2.5), M["gold"], 3.8)
    G.smooth[blk] = 0
    G.lit[blk] = True
    cam = Camera(84, 12)
    pad = art * 0.04
    buf = render(G, M, cam, art, art, (pad, pad, art - pad, art - pad))
    img, emis = shade(buf, M, cam, dict(gloss_band=(art * 0.36, art * 0.025), edge=6.0))
    gm = np.isin(buf["mat"], gems) & buf["hit"]
    return img, gm, dict(plate=None, finish=dict(glow=(4, 0.7)))


# ---------------------------------------------------------------- hand-tuned small sizes
class Px:
    """A tiny pixel canvas for the hand-tuned 32 and 16 px icons: shapes are tested at pixel centres, shaded with
    the same ramps (lit from the top left), then outlined in plum."""

    def __init__(self, n):
        self.n = n
        self.img = np.zeros((n, n, 4), np.uint8)
        self.yy, self.xx = np.mgrid[0:n, 0:n] + 0.5

    def put(self, mask, col):
        self.img[mask, :3] = col
        self.img[mask, 3] = 255

    def ramp(self, mask, pal, v):
        v = np.broadcast_to(v, mask.shape)
        i = np.clip(np.round(v), 0, len(pal) - 1).astype(int)
        self.img[mask, :3] = np.array(pal, np.uint8)[i[mask]]
        self.img[mask, 3] = 255

    def poly(self, pts):
        """Inside test for a convex polygon given clockwise in screen coords."""
        m = np.ones((self.n, self.n), bool)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            m &= (x1 - x0) * (self.yy - y0) - (y1 - y0) * (self.xx - x0) >= -1e-6
        return m

    def ell(self, cx, cy, rx, ry):
        return ((self.xx - cx) / rx) ** 2 + ((self.yy - cy) / ry) ** 2 <= 1.0

    def px(self, x, y, col):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.img[y, x, :3] = col
            self.img[y, x, 3] = 255

    def stamp(self, x0, y0, rows, pal):
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != ".":
                    self.px(x0 + i, y0 + j, pal[ch])

    def outline(self, col=PLUM):
        a = self.img[..., 3] > 0
        p = np.pad(a, 1)
        ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~a
        self.put(ring, col)


FACE_PAL = {"g": GOLD[4], "G": GOLD[2], "h": BLACK[1], "c": CREAM[4], "C": CREAM[3], "k": BLACK[0], "p": PINK[2],
            "m": RED[3], "r": RED[4], "R": RED[3], "d": RED[2], "w": CREAM[5]}


def small_B(n):
    """The world block drawn pixel by pixel at 32 or 16: the iso grass block, the lit breach, the doll's face."""
    P = Px(n)
    k = n / 32.0
    cx = n / 2
    top, mid, fy, bot = 0.6 * k, 8.4 * k, 16.0 * k, 31.4 * k
    side = bot - fy
    T, L, Rr, F = (cx, top), (0.4 * k, mid), (n - 0.4 * k, mid), (cx, fy)
    Lb, Rb, Fb = (0.4 * k, mid + side), (n - 0.4 * k, mid + side), (cx, bot)
    topm = P.poly([T, Rr, F, L])
    left = P.poly([L, F, Fb, Lb]) & ~topm
    right = P.poly([F, Rr, Rb, Fb]) & ~topm & ~left
    xx, yy = P.xx, P.yy
    h = hash3(np.floor(xx).astype(int), np.floor(yy).astype(int), 0, 77)
    # faces
    P.ramp(topm, GRASS, 4.2 + (h - 0.5) * 1.6 - (yy - top) / (fy - top) * 0.4)
    P.ramp(left, RED, 3.6 - (yy - fy) / side * 0.6 + (h > 0.85) * 0.6)
    P.ramp(right, RED, 2.3 - (yy - fy) / side * 0.4)
    # grass lip down the sides with drips
    lipy = np.where(xx < cx, mid + (xx - 0.4 * k) / 2.0, mid + (n - 0.4 * k - xx) / 2.0)
    drip = np.floor(h * 3) * k
    lip = (left | right) & (yy < lipy + (2.2 + drip) * k)
    P.ramp(lip & left, GRASS, 3.4)
    P.ramp(lip & right, GRASS, 2.4)
    # gold edges: bottom edges and the front corner
    be = (left | right) & (yy > np.where(xx < cx, fy + (xx - 0.4 * k) / 2.0 + side - 1.2 * k, fy + (n - 0.4 * k - xx) / 2.0 + side - 1.2 * k) + 0.0)
    be = (left | right) & ~P.poly([(L[0], L[1] - 1), (F[0], F[1] - 1), (Fb[0], Fb[1] - 1.25 * k), (Lb[0], Lb[1] - 1.25 * k)]) & left | \
         (right & ~P.poly([(F[0], F[1] - 1), (Rr[0], Rr[1] - 1), (Rb[0], Rb[1] - 1.25 * k), (Fb[0], Fb[1] - 1.25 * k)]))
    P.ramp(be & left, GOLD, 4)
    P.ramp(be & right, GOLD, 3)
    fe = (left | right) & (np.abs(xx - cx) < 0.6) & (yy > fy)
    P.ramp(fe, GOLD, 4)
    # the breach: a ragged hexagon round the front corner, lit inside
    br = P.poly([(cx, fy - 7.6 * k), (cx + 9.2 * k, fy - 3.0 * k), (cx + 9.2 * k, fy + 6.0 * k), (cx, fy + 10.6 * k),
                 (cx - 9.2 * k, fy + 6.0 * k), (cx - 9.2 * k, fy - 3.0 * k)])
    rag = hash3(np.floor(xx).astype(int), np.floor(yy).astype(int), 1, 5) < 0.35
    edge = br & ~P.poly([(cx, fy - 6.4 * k), (cx + 8.0 * k, fy - 2.4 * k), (cx + 8.0 * k, fy + 5.4 * k), (cx, fy + 9.4 * k),
                         (cx - 8.0 * k, fy + 5.4 * k), (cx - 8.0 * k, fy - 2.4 * k)])
    inner = br & ~edge
    P.ramp(inner, GOLD, 5.2 - np.hypot(xx - cx, yy - fy) / (8 * k) * 1.6)
    P.ramp(edge & ~(rag & (n >= 32)), CREAM if n >= 32 else GOLD, 4)
    # warm spill: grass and lacquer round the breach take the light
    near = (np.hypot((xx - cx) / 1.0, (yy - fy + 1 * k) * 1.25) < 13.0 * k) & ~br
    P.ramp(near & topm, [mix(g, (255, 214, 110), 0.45) for g in GRASS], 4.6)
    P.ramp(near & left & ~be & ~lip, [mix(r_, (255, 180, 90), 0.25) for r_ in RED], 4.4)
    P.ramp(near & right & ~be & ~lip, [mix(r_, (255, 180, 90), 0.2) for r_ in RED], 3.2)
    # the doll: head and body, red lacquer, a highlight top left
    hx, hy = cx, fy - 2.4 * k
    hr = 5.6 * k if n >= 32 else 4.3
    head = P.ell(hx, hy, hr, hr)
    body = P.ell(cx, fy + 5.6 * k, 7.4 * k, 6.4 * k) & (yy < fy + 9.6 * k)
    dm = head | body
    P.put(dm, PLUM)
    dl = (head & P.ell(hx, hy, hr - 0.9, hr - 0.9)) | (body & P.ell(cx, fy + 5.6 * k, 7.4 * k - 0.9, 6.4 * k - 0.9))
    P.ramp(dl, RED, 4.0 - ((xx - cx) * 0.6 + (yy - hy) * 0.3) / (6 * k) + (h > 0.9) * 0.3)
    # gems: ten single pixels in the gold edges, a U from the left edge to the right one
    gems = [gem_ramp(w) for w in [x["pal"] for x in __import__("content").WORLDS]]
    if n >= 32:
        spots = [(1, 13), (1, 19), (5, 26), (10, 28), (16, 31), (16, 25), (22, 28), (27, 26), (30, 19), (30, 13)]
        face = [".ggggggg.",
                "ghhhhhhhg",
                "ghcchcchg",
                "gckccckcg",
                "gpcccccpg",
                ".gccmccg.",
                "..ggggg.."]
        P.stamp(int(cx) - 4, int(hy) - 3, face, FACE_PAL)
        # flower on the belly
        P.stamp(int(cx) - 2, int(fy + 4.0 * k), [".g.g.", "..r..", ".g.g."], {"g": GOLD[5], "r": GOLD[3]})
    else:
        spots = [(0, 7), (0, 10), (3, 13), (6, 14), (8, 15), (8, 12), (10, 14), (13, 13), (15, 10), (15, 7)]
        P.stamp(int(cx) - 3, int(hy) - 2, ["hhhhhh", "ckcckc", "pccccp"], FACE_PAL)
    P.outline()
    for i, (x, y) in enumerate(spots):
        if P.img[y, x, 3]:
            P.px(x, y, gems[i][4])
    return P.img


def small_C(n):
    """The guardian drawn pixel by pixel at 32 or 16: gold ring with the ten gems, black field, the doll."""
    P = Px(n)
    k = n / 32.0
    cx, cy = n / 2, n / 2 + 0.8 * k
    xx, yy = P.xx, P.yy
    rr = np.hypot(xx - cx, yy - cy)
    disk = rr <= 15.2 * k
    ring = disk & (rr > 12.6 * k)
    P.ramp(disk, BLACK, 2.0 - (yy - cy) / (15 * k) * 0.8)
    P.ramp(ring, GOLD, 4.2 - ((xx - cx) + (yy - cy)) / (15 * k) * 1.4)
    P.ramp(disk & (rr > 12.6 * k) & (rr <= 13.4 * k), GOLD, 2)
    # the doll
    hx, hy = cx, cy - 6.6 * k
    hr = 6.0 * k if n >= 32 else 4.3
    head = P.ell(hx, hy, hr, hr)
    body = P.ell(cx, cy + 3.6 * k, 9.2 * k, 9.6 * k) & (yy < cy + 12.4 * k)
    dm = head | body
    P.put(dm, PLUM)
    dl = (head & P.ell(hx, hy, hr - 0.9, hr - 0.9)) | (body & P.ell(cx, cy + 3.6 * k, 9.2 * k - 0.9, 9.6 * k - 0.9))
    P.ramp(dl, RED, 4.2 - ((xx - cx) * 0.7 + (yy - hy) * 0.25) / (7 * k))
    belly = P.ell(cx, cy + 4.6 * k, 5.4 * k, 6.0 * k) & dl
    P.put(belly, GOLD[3])
    P.ramp(belly & P.ell(cx, cy + 4.6 * k, 5.4 * k - 1, 6.0 * k - 1), BLACK, 2)
    gems = [gem_ramp(w) for w in [x["pal"] for x in __import__("content").WORLDS]]
    if n >= 32:
        P.stamp(int(cx) - 4, int(hy) - 3, [".ggggggg.",
                                          "ghhhhhhhg",
                                          "ghcchcchg",
                                          "gckccckcg",
                                          "gpcccccpg",
                                          ".gccmccg.",
                                          "..ggggg.."], FACE_PAL)
        P.stamp(int(cx) - 2, int(cy + 3.6 * k), ["gggg", "gGGg", "dddd", "dddd"],
                {"g": GRASS[5], "G": GRASS[4], "d": DIRT[3]})
        # the gems round the ring, the head breaks the top
        for i in range(10):
            a = math.radians(90 + 30 + i * (300 / 9.0))
            x = cx - math.cos(a) * 13.9 * k
            y = cy - math.sin(a) * 13.9 * k
            P.stamp(int(x) - 1, int(y) - 1, ["ab", "bc"], {"a": gems[i][5], "b": gems[i][3], "c": gems[i][2]})
    else:
        P.stamp(int(cx) - 3, int(hy) - 2, ["hhhhhh", "ckcckc", "pccccp"], FACE_PAL)
        P.stamp(int(cx) - 1, int(cy + 2.6 * k), ["gg", "dd"], {"g": GRASS[5], "d": DIRT[3]})
        for i in range(10):
            a = math.radians(90 + 30 + i * (300 / 9.0))
            P.px(int(cx - math.cos(a) * 14.0 * k), int(cy - math.sin(a) * 14.0 * k), gems[i][4])
    P.outline()
    return P.img


# ---------------------------------------------------------------- output
CONCEPTS = {
    "A": ("L'ouverture", "the doll opened at the waist, a tiny lit world inside, the next doll peeking out", concept_A),
    "B": ("Le bloc-monde", "a grass block lacquered like a doll, broken open on the lit heart where the next doll stands", concept_B),
    "C": ("La gardienne", "the doll as a mascot on a black-lacquer medallion set with the ten worlds as gems", concept_C),
}
SIZES = (256, 64, 32, 16)


def build(key):
    img, emis, o = CONCEPTS[key][2]()
    art = finish(img, emis, o["plate"], **o.get("finish", {}))
    big = np.asarray(Image.fromarray(art).resize((ART * UP, ART * UP), Image.NEAREST))
    return big, art


def search_grid(icons, bg, card, text, ph, names=("Concept A", "Concept B", "Concept C")):
    """A mock store search grid: 4 x 3 cards of 64 px icons, ours among neutral placeholders."""
    from PIL import ImageDraw
    cols, rows, cw, chh, gap = 4, 3, 300, 96, 14
    W, H = cols * cw + (cols + 1) * gap, rows * chh + (rows + 1) * gap + 40
    im = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((gap, 10, W - gap, 34), 6, fill=card)
    d.text((gap + 12, 16), "matriochka", fill=text)
    slots = {1: 0, 6: 1, 8: 2}
    k = 0
    for r in range(rows):
        for c in range(cols):
            x, y = gap + c * (cw + gap), 40 + gap + r * (chh + gap)
            d.rounded_rectangle((x, y, x + cw, y + chh), 8, fill=card)
            ix, iy = x + 16, y + 16
            if k in slots:
                icon = Image.fromarray(icons[slots[k]])
                im.alpha_composite(icon, (ix, iy))
                name = names[slots[k]]
            else:
                d.rounded_rectangle((ix, iy, ix + 64, iy + 64), 10, fill=ph)
                name = "Some Other Mod"
            d.text((ix + 80, iy + 8), name, fill=text)
            d.rounded_rectangle((ix + 80, iy + 30, ix + 80 + 150, iy + 36), 3, fill=ph)
            d.rounded_rectangle((ix + 80, iy + 44, ix + 80 + 110, iy + 50), 3, fill=ph)
            k += 1
    return im


ROOT = os.path.abspath(os.path.join(HERE, ".."))
BRANDING = os.path.join(ROOT, "branding")


def nearest(art, n):
    return np.asarray(Image.fromarray(art).resize((n, n), Image.NEAREST))


def release(sheet_dir=None):
    """Writes the official files: the mod's icon and logo (B), the square icon (B on a lacquer plate), the pack and
    Discord icon (C), the illustration (A), and the hand-tuned 48/32/16 px icons the favicons are made of."""
    def save(arr, *path):
        full = os.path.join(ROOT, *path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        Image.fromarray(arr).save(full, optimize=True)
        return arr

    def art_of(fn, **kw):
        img, emis, o = fn(**kw)
        return finish(img, emis, o["plate"], **o.get("finish", {}))

    out = {}
    # B: the mod's icon and logo
    b = art_of(concept_B)
    b1024 = nearest(b, 1024)
    save(b1024, "branding", "logo-1024.png")
    save(nearest(b, 512), "branding", "logo-512.png")
    save(b, "branding", "logo-256.png")
    save(downs(b1024, 128), "branding", "logo-128.png")
    save(b, "src", "main", "resources", "assets", "matriochka", "icon.png")
    for n in (48, 32, 16):
        out[("B", n)] = save(small_B(n), "branding", f"icon-{n}.png")
    out[("B", 1024)], out[("B", 64)] = b1024, downs(b1024, 64)
    # B on a rounded lacquer plate, for the places that need a full square (apple-touch, social cards)
    sq = art_of(concept_B, pad_frac=0.15, plate="lacquer")
    save(nearest(sq, 1024), "branding", "icon-square-1024.png")
    # C: the pack's icon and the Discord avatar
    cc = art_of(concept_C)
    c1024 = nearest(cc, 1024)
    save(nearest(cc, 512), "branding", "modpack", "icon.png")
    save(cc, "branding", "discord-avatar-256.png")
    for n in (32, 16):
        out[("C", n)] = save(small_C(n), "branding", "modpack", f"icon-{n}.png")
    out[("C", 1024)], out[("C", 64)] = c1024, downs(c1024, 64)
    # A: the illustration
    a = art_of(concept_A)
    save(nearest(a, 1024), "branding", "illustration-opening.png")
    if sheet_dir:
        final_sheet(out, sheet_dir)
    print("branding written")


def final_sheet(out, d):
    """Overview of the final icons at 1024/64/32/16 on dark and light, and the store grid mock."""
    from PIL import ImageDraw
    os.makedirs(d, exist_ok=True)
    W, H = 1500, 1000
    im = Image.new("RGBA", (W, H), (28, 24, 26, 255))
    dr = ImageDraw.Draw(im)
    for i, (k, name) in enumerate((("B", "mod icon (B)"), ("C", "pack and Discord icon (C)"))):
        x = 30 + i * 740
        im.alpha_composite(Image.fromarray(out[(k, 1024)]).resize((440, 440), Image.LANCZOS), (x, 40))
        dr.text((x, 18), name, fill=(240, 220, 170))
        for j, bg in enumerate(((22, 24, 29, 255), (240, 241, 244, 255))):
            y = 500 + j * 230
            dr.rectangle((x, y, x + 700, y + 215), fill=bg)
            xx = x + 14
            for n in (64, 32, 16):
                ic = Image.fromarray(out[(k, n)])
                im.alpha_composite(ic, (xx, y + 14))
                xx += n + 18
            for n in (32, 16):
                ic = Image.fromarray(out[(k, n)]).resize((192, 192), Image.NEAREST)
                im.alpha_composite(ic, (xx, y + 12))
                xx += 210
    im.save(os.path.join(d, "final_overview.png"))
    icons = [out[("B", 64)], out[("C", 64)], out[("B", 64)]]
    dark = search_grid(icons, (22, 24, 29, 255), (34, 37, 44, 255), (220, 222, 228), (58, 62, 72, 255), names=("Matriochka", "Matriochka Pack", "Matriochka"))
    light = search_grid(icons, (242, 243, 246, 255), (255, 255, 255, 255), (40, 42, 48), (214, 217, 224, 255), names=("Matriochka", "Matriochka Pack", "Matriochka"))
    g = Image.new("RGBA", (dark.width, dark.height * 2), (0, 0, 0, 255))
    g.paste(dark, (0, 0))
    g.paste(light, (0, dark.height))
    g.save(os.path.join(d, "final_grid_mock.png"))


def main():
    args = sys.argv[1:]
    if "--concepts" in args:
        args.remove("--concepts")
        return concepts(args)
    sheet = None
    if "--sheet" in args:
        sheet = args[args.index("--sheet") + 1]
    release(sheet)


def concepts(args):
    keys = [a for a in args if a in CONCEPTS] or list(CONCEPTS)
    outs = [a for a in args if a not in CONCEPTS]
    out = outs[0] if outs else os.path.join(HERE, "..", "build", "logo_v2")
    os.makedirs(out, exist_ok=True)
    smalls = {}
    for k in keys:
        big, art = build(k)
        Image.fromarray(big).save(os.path.join(out, f"concept_{k}.png"))
        smalls[k] = {}
        for n in SIZES:
            sm = art if n == ART else downs(big, n) if n >= 64 else downs_q(big, n)
            smalls[k][n] = sm
            Image.fromarray(sm).save(os.path.join(out, f"concept_{k}_{n}.png"))
        smalls[k][1024] = big
        print("concept", k, "done")
    if len(keys) == 3:
        icons = [smalls[k][64] for k in "ABC"]
        dark = search_grid(icons, (22, 24, 29, 255), (34, 37, 44, 255), (220, 222, 228), (58, 62, 72, 255))
        light = search_grid(icons, (242, 243, 246, 255), (255, 255, 255, 255), (40, 42, 48), (214, 217, 224, 255))
        g = Image.new("RGBA", (dark.width, dark.height * 2), (0, 0, 0, 255))
        g.paste(dark, (0, 0))
        g.paste(light, (0, dark.height))
        g.save(os.path.join(out, "grid_mock.png"))
        overview(smalls, g, out)


def overview(smalls, grid, out):
    from PIL import ImageDraw
    W = 3 * 560 + 4 * 30
    H = 870 + int(grid.height // 2 * (W // 2 - 45) / grid.width) + 30
    im = Image.new("RGBA", (W, H), (28, 24, 26, 255))
    d = ImageDraw.Draw(im)
    for i, k in enumerate("ABC"):
        x = 30 + i * 590
        big = Image.fromarray(smalls[k][1024]).resize((560, 560), Image.LANCZOS)
        im.alpha_composite(big, (x, 30))
        title, desc = CONCEPTS[k][0], CONCEPTS[k][1]
        d.text((x, 596), f"{k}  {title}", fill=(240, 220, 170))
        # small sizes on dark and light, 1x and the 32/16 magnified x4 with no smoothing
        for j, bg in enumerate(((22, 24, 29, 255), (240, 241, 244, 255))):
            y = 620 + j * 115
            d.rectangle((x, y, x + 560, y + 105), fill=bg)
            xx = x + 12
            for n in (64, 32, 16):
                ic = Image.fromarray(smalls[k][n])
                im.alpha_composite(ic, (xx, y + (105 - n) // 2))
                xx += n + 14
            for n in (32, 16):
                ic = Image.fromarray(smalls[k][n]).resize((n * (96 // n), n * (96 // n)), Image.NEAREST)
                im.alpha_composite(ic, (xx, y + 4))
                xx += 96 + 14
    gh = grid.height // 2
    im.alpha_composite(grid.crop((0, 0, grid.width, gh)).resize((W // 2 - 45, int(gh * (W // 2 - 45) / grid.width))), (30, 870))
    im.alpha_composite(grid.crop((0, gh, grid.width, 2 * gh)).resize((W // 2 - 45, int(gh * (W // 2 - 45) / grid.width))), (W // 2 + 15, 870))
    im.save(os.path.join(out, "overview.png"))


if __name__ == "__main__":
    main()
