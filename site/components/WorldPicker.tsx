"use client";
// The ten worlds as a row of dolls: pick one and its world opens in the frame above.
// Arrow keys move along the row, Home and End jump to the ends.
import Link from "next/link";
import { useRef, useState } from "react";
import { asset } from "@/lib/data";
import { btn } from "./ui";

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
    <div>
      <div role="tabpanel" id="wp-panel" aria-labelledby={`wp-tab-${w.n}`}
        className="relative min-h-[520px] overflow-hidden border-2 border-gold bg-black shadow-frame md:aspect-[21/9] md:min-h-[420px]">
        {w.img ? (
          <img key={w.img} className="absolute inset-0 size-full object-cover motion-safe:animate-[wp-in_.5s_ease-out]" src={asset(w.img)} alt="" width={1920} height={820} />
        ) : (
          <span className="absolute inset-0 bg-[length:64px] opacity-50 [image-rendering:pixelated]" style={{ backgroundImage: `url(${asset(w.tex)})` }} />
        )}
        <span className="absolute inset-0 bg-[linear-gradient(0deg,rgba(10,6,5,.95)_0%,rgba(10,6,5,.6)_55%,rgba(10,6,5,.1)_100%)] md:bg-[linear-gradient(90deg,rgba(10,6,5,.9)_0%,rgba(10,6,5,.55)_40%,transparent_75%)]" />
        <div className="absolute right-5 bottom-[clamp(20px,4vw,48px)] left-[clamp(20px,4vw,56px)] z-10 md:right-auto md:max-w-[min(520px,80%)]">
          <p className="m-0 mb-1 font-pixel text-[26px]" style={{ color: w.light }}>{w.label}</p>
          <h3 className="m-0 mb-2.5 font-display text-[clamp(36px,4.6vw,64px)] leading-[0.95] font-normal text-paper [text-shadow:0_4px_0_rgba(0,0,0,.7)]">{w.name}</h3>
          <p className="m-0 mb-2 font-body text-lg leading-snug font-bold text-gold-b">{w.short}</p>
          <p className="m-0 mb-4.5 line-clamp-3 text-base leading-normal text-paper">{w.long}</p>
          <Link className={btn} href={w.href}>{open} {w.name}</Link>
        </div>
      </div>
      <div role="tablist" aria-label={listLabel}
        className="flex items-end gap-[clamp(4px,1.2vw,16px)] overflow-x-auto border-b-[3px] border-gold px-1 pt-6 md:justify-center md:overflow-visible"
        onKeyDown={(e) => {
          const k = { ArrowRight: cur + 1, ArrowLeft: cur - 1, Home: 0, End: worlds.length - 1 }[e.key];
          if (k !== undefined) { e.preventDefault(); go(k); }
        }}>
        {worlds.map((x, i) => {
          const on = i === cur;
          return (
            <button key={x.n} ref={(el) => { tabs.current[i] = el; }} id={`wp-tab-${x.n}`} role="tab" type="button"
              aria-selected={on} aria-controls="wp-panel" tabIndex={on ? 0 : -1} onClick={() => setCur(i)}
              className={`group relative grid min-w-11 cursor-pointer justify-items-center gap-1 border-0 bg-transparent px-0 pb-2 ${on ? "text-gold-b" : "text-paper-dim"}`}>
              <svg viewBox="0 0 100 170" aria-hidden="true" style={{ width: `calc(clamp(40px, 6.4vw, 84px) * ${1 - i * 0.045})` }}
                className={`h-auto drop-shadow-[0_4px_0_rgba(0,0,0,.45)] transition-transform duration-200 motion-reduce:transition-none ${on ? "-translate-y-2.5" : "group-hover:-translate-y-1"}`}>
                <use href="#doll" width="100" height="170" style={{ "--db": x.doll.body, "--ds": x.doll.scarf, "--do": x.doll.orn } as React.CSSProperties} />
              </svg>
              <span className="font-pixel text-xl">{x.n}</span>
              <span className="sr-only">{x.label}, {x.name}</span>
              {on && <span className="absolute right-[15%] -bottom-[3px] left-[15%] h-[3px] bg-gold-b" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
