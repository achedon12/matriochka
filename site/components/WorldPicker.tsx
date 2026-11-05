"use client";
// The ten worlds as a row of dolls: pick one and its world opens in the frame above.
// Arrow keys move along the row, Home and End jump to the ends.
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { asset } from "@/lib/data";
import { btn } from "./ui";

export interface PickerWorld {
  n: number; name: string; short: string; long: string; img: string | null; tex: string;
  doll: { body: string; scarf: string; orn: string }; light: string; href: string; label: string;
  bg: string; boss: string; mobs: string[];
}

export default function WorldPicker({ worlds, open, listLabel, pauseLabel, playLabel }: {
  worlds: PickerWorld[]; open: string; listLabel: string; pauseLabel: string; playLabel: string;
}) {
  const [cur, setCur] = useState(1);
  // the dolls open one after another until the visitor picks one or pauses
  const [auto, setAuto] = useState(true);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) setAuto(false);
  }, []);
  useEffect(() => {
    if (!auto) return;
    const t = window.setTimeout(() => setCur((c) => (c + 1) % worlds.length), 7000);
    return () => window.clearTimeout(t);
  }, [auto, cur, worlds.length]);
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const w = worlds[cur];
  const go = (i: number) => {
    setAuto(false);
    const j = (i + worlds.length) % worlds.length;
    setCur(j);
    tabs.current[j]?.focus();
  };
  return (
    <div>
      <div role="tabpanel" id="wp-panel" aria-labelledby={`wp-tab-${w.n}`}
        className="relative min-h-[520px] overflow-hidden border-2 border-gold bg-black shadow-frame md:aspect-[21/9] md:min-h-[420px]">
        {/* the world itself: its photo when there is one, its own colours otherwise */}
        {w.img ? (
          <img key={w.img} className="kenburns absolute inset-0 size-full object-cover motion-safe:animate-[wp-in_.5s_ease-out]" src={asset(w.img)} alt="" width={1920} height={820} />
        ) : (
          <span key={`g${w.n}`} className="absolute inset-0 motion-safe:animate-[wp-in_.5s_ease-out]"
            style={{ background: `radial-gradient(ellipse at 72% 40%, ${w.light}66 0%, ${w.bg} 48%, #0e0806 100%)` }}>
            <svg className="absolute top-[6%] right-[6%] h-[88%] w-auto opacity-25" viewBox="0 0 100 170" aria-hidden="true">
              <use href="#doll" width="100" height="170" style={{ "--db": w.doll.body, "--ds": w.doll.scarf, "--do": w.doll.orn } as React.CSSProperties} />
            </svg>
          </span>
        )}
        {/* who lives there: the boss standing behind its five creatures */}
        <div key={`c${w.n}`} className="pointer-events-none absolute right-0 bottom-0 z-[5] hidden h-full w-[52%] md:block" aria-hidden="true">
          <img className="bob absolute right-[8%] bottom-[16%] h-[78%] w-auto drop-shadow-[0_24px_30px_rgba(0,0,0,.75)] motion-safe:animate-[wp-in_.6s_ease-out]"
            src={asset(`portraits/${w.boss}.png`)} alt="" width={512} height={512} />
          <div className="absolute right-[4%] bottom-[3%] flex items-end gap-1">
            {w.mobs.map((m, k) => (
              <img key={m} className="h-[clamp(60px,9vw,120px)] w-auto drop-shadow-[0_10px_12px_rgba(0,0,0,.7)] motion-safe:animate-[wp-in_.5s_ease-out_both]"
                style={{ animationDelay: `${0.08 * k + 0.15}s` }} src={asset(`portraits/${m}.png`)} alt="" width={256} height={256} />
            ))}
          </div>
        </div>
        <span className="absolute inset-0 bg-[linear-gradient(0deg,rgba(10,6,5,.95)_0%,rgba(10,6,5,.6)_55%,rgba(10,6,5,.1)_100%)] md:bg-[linear-gradient(90deg,rgba(10,6,5,.92)_0%,rgba(10,6,5,.6)_38%,transparent_62%)]" />
        <div className="absolute right-5 bottom-[clamp(20px,4vw,48px)] left-[clamp(20px,4vw,56px)] z-10 md:right-auto md:max-w-[min(520px,80%)]">
          <p className="m-0 mb-1 font-pixel text-[26px]" style={{ color: w.light }}>{w.label}</p>
          <h3 className="m-0 mb-2.5 font-display text-[clamp(36px,4.6vw,64px)] leading-[0.95] font-normal text-paper [text-shadow:0_4px_0_rgba(0,0,0,.7)]">{w.name}</h3>
          <p className="m-0 mb-2 font-body text-lg leading-snug font-bold text-gold-b">{w.short}</p>
          <p className="m-0 mb-4.5 line-clamp-3 text-base leading-normal text-paper">{w.long}</p>
          <Link className={btn} href={w.href}>{open} {w.name}</Link>
        </div>
        <button type="button" onClick={() => setAuto((a) => !a)} aria-pressed={!auto}
          className="absolute top-3 right-3 z-20 grid size-11 cursor-pointer place-items-center rounded-full border-2 border-gold bg-ink/70 text-gold-b hover:bg-ink">
          <span className="sr-only">{auto ? pauseLabel : playLabel}</span>
          <svg viewBox="0 0 24 24" className="size-5" fill="currentColor" aria-hidden="true">{auto ? <path d="M7 5h4v14H7zM13 5h4v14h-4z" /> : <path d="M8 5l11 7-11 7z" />}</svg>
        </button>
        {auto && <span key={`p${cur}`} className="wp-progress absolute right-0 bottom-0 left-0 z-20 h-1 bg-gold-b" style={{ "--t": "7s" } as React.CSSProperties} />}
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
              aria-selected={on} aria-controls="wp-panel" tabIndex={on ? 0 : -1} onClick={() => { setAuto(false); setCur(i); }}
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
