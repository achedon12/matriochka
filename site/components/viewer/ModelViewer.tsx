"use client";
// The creature viewer as the pages use it: a framed stage with the creature's texture as a static fallback,
// the real animated model once the stage scrolls into view (or on "View in 3D"), and one button per animation.
import dynamic from "next/dynamic";
import { useCallback, useEffect, useRef, useState } from "react";
import { asset } from "@/lib/data";
import type { Anim } from "@/lib/types";

const ViewerImpl = dynamic(() => import("./ViewerImpl"), { ssr: false });

export interface ViewerLabels { view3d: string; loading3d: string; no3d: string; dragHint: string; animations: string; autoRotate: string }

export default function ModelViewer({ id, name, anims, labels, tex, auto = true, release = false, className = "" }: {
  id: string; name: string; anims: Anim[]; labels: ViewerLabels; tex: string | null;
  /** start when scrolled into view (otherwise only on click) */ auto?: boolean;
  /** free the canvas again when it is far off screen (pages that hold many viewers) */ release?: boolean;
  className?: string;
}) {
  const stage = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const [play, setPlay] = useState({ key: "misc.idle", n: 0 });
  const [rotate, setRotate] = useState(true);
  const [still, setStill] = useState(false);

  useEffect(() => {
    const rm = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (rm.matches) {
      setRotate(false);
      setStill(true);
    }
  }, []);

  useEffect(() => {
    const el = stage.current;
    if (!el || (!auto && !release)) return;
    const io = new IntersectionObserver(
      (es) => {
        const on = es.some((e) => e.isIntersecting);
        if (on && auto) setMounted(true);
        if (!on && release) {
          setMounted(false);
          setReady(false);
        }
      },
      { rootMargin: release ? "600px 0px" : "200px 0px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [auto, release]);

  const onEnd = useCallback(() => setPlay((p) => ({ key: "misc.idle", n: p.n + 1 })), []);
  const onReady = useCallback(() => setReady(true), []);
  const onError = useCallback(() => setFailed(true), []);

  const choose = (key: string) => {
    setMounted(true);
    setStill(false);
    setPlay((p) => ({ key, n: p.n + 1 }));
  };

  return (
    <div className={`viewer ${className}`}>
      <div className={`stage${ready ? " is-ready" : ""}${failed ? " is-failed" : ""}`} ref={stage}>
        {(!ready || failed) && (
          <div className="stage-fallback">
            <img className="stage-portrait" src={asset(`portraits/${id}.png`)} alt="" width="512" height="512" loading="lazy" />
            {failed ? <p>{labels.no3d}</p> : mounted ? <p className="stage-wait">{labels.loading3d}</p> : (
              <button type="button" className="btn btn-small" onClick={() => setMounted(true)}>{labels.view3d}</button>
            )}
          </div>
        )}
        {mounted && !failed && (
          <ViewerImpl id={id} play={play} rotate={rotate} still={still} onEnd={onEnd} onReady={onReady} onError={onError} />
        )}
        <span className="sr-only">{name}</span>
      </div>
      <div className="viewer-bar">
        <div className="anim-btns" role="group" aria-label={labels.animations}>
          {anims.map((a) => (
            <button key={a.key} type="button" className="chip-btn" aria-pressed={play.key === a.key && mounted && !still}
              onClick={() => choose(a.key)}>{a.label}</button>
          ))}
        </div>
        <label className="rot-toggle">
          <input type="checkbox" checked={rotate} onChange={(e) => setRotate(e.target.checked)} />
          <span>{labels.autoRotate}</span>
        </label>
      </div>
      <p className="viewer-hint">{labels.dragHint}</p>
    </div>
  );
}
