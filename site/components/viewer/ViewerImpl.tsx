"use client";
// The WebGL part of the creature viewer. Loaded on demand (next/dynamic, no server rendering), one per
// visible viewer; it stops drawing when its canvas leaves the screen and frees the GPU when unmounted.
import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { asset } from "@/lib/data";
import { buildRig, parseAnimations, pose, type AnimFile, type Clip, type GeoFile } from "./geo";

export interface ViewerImplProps {
  id: string;
  play: { key: string; n: number };
  rotate: boolean;
  still: boolean;
  onEnd: () => void;
  onReady: () => void;
  onError: () => void;
}

function shadowTexture() {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grd = g.createRadialGradient(64, 64, 4, 64, 64, 62);
  grd.addColorStop(0, "rgba(10,6,4,0.75)");
  grd.addColorStop(1, "rgba(10,6,4,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

export default function ViewerImpl({ id, play, rotate, still, onEnd, onReady, onError }: ViewerImplProps) {
  const host = useRef<HTMLDivElement>(null);
  const state = useRef<{ clips?: Map<string, Clip>; current?: string; start: number; rotate: boolean; still: boolean; onEnd: () => void; held: boolean }>({
    start: 0, rotate, still, onEnd, held: false,
  });

  state.current.rotate = rotate;
  state.current.onEnd = onEnd;

  useEffect(() => {
    state.current.current = play.key;
    state.current.start = performance.now();
    state.current.held = false;
    state.current.still = still && play.n === 0;
  }, [play, still]);

  useEffect(() => {
    const el = host.current;
    if (!el) return;
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
    } catch {
      onError();
      return;
    }
    let disposed = false;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    el.appendChild(renderer.domElement);
    renderer.domElement.setAttribute("aria-hidden", "true");

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(30, 1, 0.05, 200);
    // lacquer light: warm gold from above, red bounce from below, a cool rim from behind
    scene.add(new THREE.HemisphereLight(0xffe2a8, 0x5a1410, 1.25));
    const key = new THREE.DirectionalLight(0xfff0d0, 2.1);
    key.position.set(3, 6, 5);
    scene.add(key);
    const rim = new THREE.DirectionalLight(0xf0c960, 1.1);
    rim.position.set(-4, 3, -5);
    scene.add(rim);
    const fill = new THREE.DirectionalLight(0xc8342a, 0.6);
    fill.position.set(-5, -1, 3);
    scene.add(fill);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = false;
    controls.autoRotateSpeed = 1.1;

    const shadowTex = shadowTexture();
    let rig: ReturnType<typeof buildRig> | undefined;
    let texture: THREE.Texture | undefined;
    const holder = new THREE.Group();
    holder.rotation.y = Math.PI; // the front of a Bedrock model looks north; turn it toward the camera
    scene.add(holder);

    const resize = () => {
      const w = el.clientWidth || 1;
      const h = el.clientHeight || 1;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    };
    const ro = new ResizeObserver(resize);
    ro.observe(el);
    resize();

    let visible = true;
    const io = new IntersectionObserver((es) => {
      visible = es.some((e) => e.isIntersecting);
      if (visible) loop();
    });
    io.observe(el);

    let raf = 0;
    const draw = () => {
      raf = 0;
      if (disposed || !visible || document.hidden) return;
      const s = state.current;
      controls.autoRotate = s.rotate;
      controls.update();
      if (rig && s.clips) {
        const clip = s.clips.get(s.current ?? "") ?? s.clips.get("misc.idle");
        let t = s.still ? 0 : (performance.now() - s.start) / 1000;
        if (clip) {
          if (clip.loop === true) t = t % clip.length;
          else if (t >= clip.length) {
            t = clip.length;
            if (clip.loop !== "hold_on_last_frame" && !s.held) {
              s.held = true;
              s.onEnd();
            }
          }
        }
        pose(rig, clip, t);
      }
      renderer.render(scene, camera);
      raf = requestAnimationFrame(draw);
    };
    const loop = () => {
      if (!raf) raf = requestAnimationFrame(draw);
    };
    const onVis = () => loop();
    document.addEventListener("visibilitychange", onVis);

    (async () => {
      try {
        const [geo, anim] = await Promise.all([
          fetch(asset(`models/${id}.geo.json`)).then((r) => r.json() as Promise<GeoFile>),
          fetch(asset(`animations/${id}.animation.json`)).then((r) => (r.ok ? (r.json() as Promise<AnimFile>) : { animations: {} })),
        ]);
        texture = await new THREE.TextureLoader().loadAsync(asset(`entities/${id}.png`));
        if (disposed) return;
        texture.magFilter = THREE.NearestFilter;
        texture.minFilter = THREE.NearestFilter;
        texture.generateMipmaps = false;
        texture.colorSpace = THREE.SRGBColorSpace;
        let glow: THREE.Texture | undefined;
        try {
          glow = await new THREE.TextureLoader().loadAsync(asset(`entities/${id}_glowmask.png`));
          glow.magFilter = THREE.NearestFilter;
          glow.minFilter = THREE.NearestFilter;
          glow.generateMipmaps = false;
          glow.colorSpace = THREE.SRGBColorSpace;
        } catch {
          glow = undefined;
        }
        rig = buildRig(geo, texture, glow);
        state.current.clips = parseAnimations(anim);
        const s = 1 / 16;
        rig.root.scale.setScalar(s);
        holder.add(rig.root);
        const h = rig.height * s;
        const w = rig.width * s;
        const shadow = new THREE.Mesh(new THREE.CircleGeometry(Math.max(w, h * 0.5) * 0.62, 40),
          new THREE.MeshBasicMaterial({ map: shadowTex, transparent: true, depthWrite: false }));
        shadow.rotation.x = -Math.PI / 2;
        shadow.position.y = 0.002;
        scene.add(shadow);
        const size = Math.max(h, w * 0.9);
        const dist = (size / 2 / Math.tan((camera.fov * Math.PI) / 360)) * 1.72;
        controls.target.set(0, h * 0.48, 0);
        camera.position.set(dist * 0.42, h * 0.62 + dist * 0.12, dist);
        controls.minDistance = dist * 0.45;
        controls.maxDistance = dist * 2.2;
        controls.update();
        onReady();
        loop();
      } catch {
        if (!disposed) onError();
      }
    })();

    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      io.disconnect();
      ro.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      controls.dispose();
      scene.traverse((o) => {
        const m = o as THREE.Mesh;
        if (m.geometry) m.geometry.dispose();
        const mat = m.material as THREE.Material | undefined;
        if (mat) mat.dispose();
      });
      texture?.dispose();
      shadowTex.dispose();
      renderer.dispose();
      renderer.forceContextLoss();
      renderer.domElement.remove();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  return <div ref={host} className="viewer-gl" />;
}
