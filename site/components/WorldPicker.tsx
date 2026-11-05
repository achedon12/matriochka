"use client";
// The ten worlds as a row of dolls: pick one and its world opens in the frame above.
// Arrow keys move along the row, Home and End jump to the ends.
import Link from "next/link";
import { useRef, useState } from "react";
import { asset } from "@/lib/data";

export interface PickerWorld {
  n: number; name: string; short: string; long: string; img: string | null; tex: string;
  doll: { body: string; scarf: string; orn: string }; light: string; href: string; label: string;
}

export default function WorldPicker({ worlds, open, listLabel }: { worlds: PickerWorld[]; open: string; listLabel: string }) {
  const [cur, setCur] = useState(1);
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const w = worlds[cur];
  const go = (i: number) => {
    const j = (i + worlds.length) % worlds.length;
    setCur(j);
    tabs.current[j]?.focus();
  };
  return (
    <div className="wp" style={{ "--wl": w.light } as React.CSSProperties}>
      <div className="wp-stage" role="tabpanel" id="wp-panel" aria-labelledby={`wp-tab-${w.n}`}>
        {w.img ? <img key={w.img} className="wp-img" src={asset(w.img)} alt="" width={1920} height={820} /> :
          <span className="wp-img wp-tile" style={{ backgroundImage: `url(${asset(w.tex)})` }} />}
        <div className="wp-copy">
          <p className="wp-n num">{w.label}</p>
          <h3>{w.name}</h3>
          <p className="wp-short">{w.short}</p>
          <p className="wp-long">{w.long}</p>
          <Link className="btn" href={w.href}>{open} {w.name}</Link>
        </div>
      </div>
      <div className="wp-row" role="tablist" aria-label={listLabel}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight") { e.preventDefault(); go(cur + 1); }
          if (e.key === "ArrowLeft") { e.preventDefault(); go(cur - 1); }
          if (e.key === "Home") { e.preventDefault(); go(0); }
          if (e.key === "End") { e.preventDefault(); go(worlds.length - 1); }
        }}>
        {worlds.map((x, i) => (
          <button key={x.n} ref={(el) => { tabs.current[i] = el; }} id={`wp-tab-${x.n}`} role="tab" type="button"
            aria-selected={i === cur} aria-controls="wp-panel" tabIndex={i === cur ? 0 : -1}
            className="wp-doll" onClick={() => setCur(i)} style={{ "--s": 1 - i * 0.045 } as React.CSSProperties}>
            <svg viewBox="0 0 100 170" aria-hidden="true">
              <use href="#doll" width="100" height="170" style={{ "--db": x.doll.body, "--ds": x.doll.scarf, "--do": x.doll.orn } as React.CSSProperties} />
            </svg>
            <span className="wp-num num">{x.n}</span>
            <span className="sr-only">{x.label}, {x.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
