// A small loader for the mod's GeckoLib (Bedrock 1.12.0) entity models and animations.
//
// Bedrock files use a space mirrored on X compared to three.js. Like Blockbench and GeckoLib, every pivot,
// cube origin and position keyframe has its X negated, and rotations become (-x, -y, z) in degrees, applied
// in Z, Y, X order. Sizes are in pixels (1/16 of a block). Faces use box UV: the top and bottom on the first
// row, then east, north, west and south side by side on the second; the north face is the front.
import * as THREE from "three";

type V3 = [number, number, number];
interface GeoCube { origin: V3; size: V3; uv: [number, number]; inflate?: number; rotation?: V3; pivot?: V3 }
interface GeoBone { name: string; parent?: string; pivot: V3; rotation?: V3; cubes?: GeoCube[] }
export interface GeoFile {
  "minecraft:geometry": { description: { texture_width: number; texture_height: number }; bones: GeoBone[] }[];
}

type Value = number | string;
type Channel = V3 | Record<string, Value[] | { post?: Value[]; pre?: Value[] }>;
interface AnimDef { loop?: boolean | "hold_on_last_frame"; animation_length?: number; bones: Record<string, Partial<Record<"rotation" | "position" | "scale", Channel>>> }
export interface AnimFile { animations: Record<string, AnimDef> }

const D2R = Math.PI / 180;

export interface Rig {
  root: THREE.Group;
  bones: Map<string, { obj: THREE.Object3D; pos: THREE.Vector3; rot: THREE.Euler }>;
  height: number;
  width: number;
}

function faceGeometry(from: V3, to: V3, uv: [number, number], size: V3, tw: number, th: number) {
  const [x0, y0, z0] = from;
  const [x1, y1, z1] = to;
  const [w, h, d] = size.map((v) => Math.max(1, Math.ceil(v - 1e-6)));
  const [u, v] = uv;
  // corners of each face as seen from outside: top-left, top-right, bottom-left, bottom-right
  const faces: { c: V3[]; r: [number, number, number, number]; flip?: boolean }[] = [
    { c: [[x1, y1, z0], [x0, y1, z0], [x1, y0, z0], [x0, y0, z0]], r: [u + d, v + d, w, h] }, // north (front)
    { c: [[x1, y1, z1], [x1, y1, z0], [x1, y0, z1], [x1, y0, z0]], r: [u, v + d, d, h] }, // east
    { c: [[x0, y1, z1], [x1, y1, z1], [x0, y0, z1], [x1, y0, z1]], r: [u + 2 * d + w, v + d, w, h] }, // south
    { c: [[x0, y1, z0], [x0, y1, z1], [x0, y0, z0], [x0, y0, z1]], r: [u + d + w, v + d, d, h] }, // west
    { c: [[x1, y1, z1], [x0, y1, z1], [x1, y1, z0], [x0, y1, z0]], r: [u + d, v, w, d] }, // up
    { c: [[x1, y0, z0], [x0, y0, z0], [x1, y0, z1], [x0, y0, z1]], r: [u + d + w, v, w, d], flip: true }, // down
  ];
  const pos: number[] = [];
  const uvs: number[] = [];
  const nrm: number[] = [];
  const idx: number[] = [];
  faces.forEach((f, i) => {
    const [ru, rv, rw, rh] = f.r;
    const ua = ru / tw, ub = (ru + rw) / tw;
    let va = 1 - rv / th, vb = 1 - (rv + rh) / th;
    if (f.flip) [va, vb] = [vb, va];
    const quad = [[ua, va], [ub, va], [ua, vb], [ub, vb]];
    const a = new THREE.Vector3(...f.c[0]), b = new THREE.Vector3(...f.c[1]), c = new THREE.Vector3(...f.c[2]);
    const n = new THREE.Vector3().subVectors(c, a).cross(new THREE.Vector3().subVectors(b, a)).normalize();
    f.c.forEach((p, k) => {
      pos.push(...p);
      uvs.push(...quad[k]);
      nrm.push(n.x, n.y, n.z);
    });
    const o = i * 4;
    idx.push(o, o + 2, o + 1, o + 1, o + 2, o + 3);
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nrm, 3));
  g.setIndex(idx);
  return g;
}

const mx = (p: V3): V3 => [-p[0], p[1], p[2]];
const rotOf = (r?: V3) => new THREE.Euler(-(r?.[0] ?? 0) * D2R, -(r?.[1] ?? 0) * D2R, (r?.[2] ?? 0) * D2R, "ZYX");

export function buildRig(file: GeoFile, texture: THREE.Texture): Rig {
  const geo = file["minecraft:geometry"][0];
  const { texture_width: tw, texture_height: th } = geo.description;
  const material = new THREE.MeshStandardMaterial({ map: texture, transparent: true, alphaTest: 0.1, roughness: 0.62, metalness: 0.04, side: THREE.DoubleSide });
  const root = new THREE.Group();
  const bones: Rig["bones"] = new Map();
  const pivots = new Map<string, V3>();
  const box = new THREE.Box3();
  for (const b of geo.bones) pivots.set(b.name, mx(b.pivot ?? [0, 0, 0]));
  for (const b of geo.bones) {
    const p = pivots.get(b.name)!;
    const pp: V3 = b.parent ? pivots.get(b.parent) ?? [0, 0, 0] : [0, 0, 0];
    const obj = new THREE.Group();
    obj.name = b.name;
    obj.position.set(p[0] - pp[0], p[1] - pp[1], p[2] - pp[2]);
    obj.rotation.copy(rotOf(b.rotation));
    for (const c of b.cubes ?? []) {
      const inf = c.inflate ?? 0;
      const from: V3 = [-(c.origin[0] + c.size[0]) - inf, c.origin[1] - inf, c.origin[2] - inf];
      const to: V3 = [from[0] + c.size[0] + 2 * inf, from[1] + c.size[1] + 2 * inf, from[2] + c.size[2] + 2 * inf];
      const cp = c.pivot ? mx(c.pivot) : p;
      const holder = new THREE.Group();
      holder.position.set(cp[0] - p[0], cp[1] - p[1], cp[2] - p[2]);
      if (c.rotation) holder.rotation.copy(rotOf(c.rotation));
      const rel = (q: V3): V3 => [q[0] - cp[0], q[1] - cp[1], q[2] - cp[2]];
      const mesh = new THREE.Mesh(faceGeometry(rel(from), rel(to), c.uv, c.size, tw, th), material);
      holder.add(mesh);
      obj.add(holder);
      box.expandByPoint(new THREE.Vector3(...from)).expandByPoint(new THREE.Vector3(...to));
    }
    bones.set(b.name, { obj, pos: obj.position.clone(), rot: obj.rotation.clone() });
  }
  for (const b of geo.bones) {
    const node = bones.get(b.name)!.obj;
    const parent = b.parent ? bones.get(b.parent)?.obj : undefined;
    (parent ?? root).add(node);
  }
  const size = box.getSize(new THREE.Vector3());
  return { root, bones, height: Math.max(size.y, 4), width: Math.max(size.x, size.z, 4) };
}

// ---------------------------------------------------------------- Molang, the subset the mod uses
type Fn = (t: number) => number;
const SIN = (d: number) => Math.sin(d * D2R);
const COS = (d: number) => Math.cos(d * D2R);

function compile(v: Value): Fn {
  if (typeof v === "number") return () => v;
  const src = v.trim();
  if (src === "") return () => 0;
  const js = src
    .replace(/\bmath\.sin\s*\(/g, "S(")
    .replace(/\bmath\.cos\s*\(/g, "C(")
    .replace(/\bmath\.(abs|max|min|floor|ceil|round|sqrt)\s*\(/g, "Math.$1(")
    .replace(/\bmath\.pi\b/g, "Math.PI")
    .replace(/\b(query|q)\.anim_time\b/g, "t");
  // Only numbers, arithmetic and the identifiers above may remain: anything else is refused, not run.
  const rest = js.replace(/Math\.(abs|max|min|floor|ceil|round|sqrt|PI)\b|\b[SCt]\b/g, "");
  if (!/^[0-9.\s+\-*/(),]*$/.test(rest)) return () => 0;
  try {
    const f = new Function("t", "S", "C", `"use strict"; return (${js});`) as (t: number, s: typeof SIN, c: typeof COS) => number;
    return (t) => {
      const r = f(t, SIN, COS);
      return Number.isFinite(r) ? r : 0;
    };
  } catch {
    return () => 0;
  }
}

type Sampler = (t: number) => V3;

function sampler(ch: Channel): Sampler {
  if (Array.isArray(ch)) {
    const f = ch.map(compile);
    return (t) => [f[0](t), f[1](t), f[2](t)];
  }
  const keys = Object.entries(ch)
    .map(([k, v]) => {
      const arr = Array.isArray(v) ? v : (v.post ?? v.pre ?? [0, 0, 0]);
      return { t: parseFloat(k), f: arr.map(compile) };
    })
    .sort((a, b) => a.t - b.t);
  return (t) => {
    if (t <= keys[0].t) return keys[0].f.map((f) => f(t)) as V3;
    const last = keys[keys.length - 1];
    if (t >= last.t) return last.f.map((f) => f(t)) as V3;
    let i = 0;
    while (i < keys.length - 2 && keys[i + 1].t <= t) i++;
    const a = keys[i], b = keys[i + 1];
    const k = (t - a.t) / (b.t - a.t || 1);
    return [0, 1, 2].map((j) => a.f[j](t) + (b.f[j](t) - a.f[j](t)) * k) as V3;
  };
}

export interface Clip {
  name: string;
  length: number;
  loop: boolean | "hold_on_last_frame";
  tracks: { bone: string; rotation?: Sampler; position?: Sampler; scale?: Sampler }[];
}

export function parseAnimations(file: AnimFile): Map<string, Clip> {
  const out = new Map<string, Clip>();
  for (const [name, a] of Object.entries(file.animations)) {
    out.set(name, {
      name,
      length: a.animation_length ?? 1,
      loop: a.loop ?? false,
      tracks: Object.entries(a.bones).map(([bone, ch]) => ({
        bone,
        rotation: ch.rotation ? sampler(ch.rotation) : undefined,
        position: ch.position ? sampler(ch.position) : undefined,
        scale: ch.scale ? sampler(ch.scale) : undefined,
      })),
    });
  }
  return out;
}

/** Puts every bone back in its rest pose, then applies a clip at time t (seconds). */
export function pose(rig: Rig, clip: Clip | undefined, t: number) {
  for (const b of rig.bones.values()) {
    b.obj.position.copy(b.pos);
    b.obj.rotation.copy(b.rot);
    b.obj.scale.set(1, 1, 1);
  }
  if (!clip) return;
  for (const tr of clip.tracks) {
    const b = rig.bones.get(tr.bone);
    if (!b) continue;
    if (tr.rotation) {
      const [x, y, z] = tr.rotation(t);
      b.obj.rotation.set(b.rot.x - x * D2R, b.rot.y - y * D2R, b.rot.z + z * D2R, "ZYX");
    }
    if (tr.position) {
      const [x, y, z] = tr.position(t);
      b.obj.position.set(b.pos.x - x, b.pos.y + y, b.pos.z + z);
    }
    if (tr.scale) {
      const [x, y, z] = tr.scale(t);
      b.obj.scale.set(x, y, z);
    }
  }
}
