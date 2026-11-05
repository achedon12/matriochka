"use client";
// The ten worlds as a lacquered stage: the boss in a beam of its world's light, its creatures at the front,
// the world's name set huge behind them. Below, the dolls on their shelf: the chosen one lifts its lid.
// The stage turns to the next world every 7 seconds until the visitor picks one or pauses.
// Arrow keys move along the shelf, Home and End jump to the ends.
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { asset } from "@/lib/data";
import { btn } from "./ui";

export interface PickerWorld {
  n: number; name: string; short: string; long: string; img: string | null; tex: string;
  doll: { body: string; scarf: string; orn: string }; light: string; href: string; label: string;
  bg: string; boss: string; mobs: string[];
}

const CORNERS = ["top-0 left-0", "top-0 right-0 -scale-x-100", "bottom-0 left-0 -scale-y-100", "right-0 bottom-0 -scale-100"];

export default function WorldPicker({ worlds, open, listLabel, pauseLabel, playLabel }: {
  worlds: PickerWorld[]; open: string; listLabel: string; pauseLabel: string; playLabel: string;
}) {
  const [cur, setCur] = useState(1);
  const [auto, setAuto] = useState(true);
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) setAuto(false);
  }, []);
  useEffect(() => {
    if (!auto) return;
    const t = window.setTimeout(() => setCur((c) => (c + 1) % worlds.length), 7000);
    return () => window.clearTimeout(t);
  }, [auto, cur, worlds.length]);
  const w = worlds[cur];
  const go = (i: number) => {
    setAuto(false);
    const j = (i + worlds.length) % worlds.length;
    setCur(j);
    tabs.current[j]?.focus();
  };
  const dollStyle = (x: PickerWorld) => ({ "--db": x.doll.body, "--ds": x.doll.scarf, "--do": x.doll.orn } as React.CSSProperties);

  return (
    <div>
      <div role="tabpanel" id="wp-panel" aria-labelledby={`wp-tab-${w.n}`}
        className="relative isolate min-h-[600px] overflow-hidden border-2 border-gold bg-black shadow-frame md:aspect-[21/9] md:min-h-[480px]">
        {/* ground: the world's photo, or its own colours */}
        {w.img ? (
          <img key={w.img} className="kenburns absolute inset-0 -z-30 size-full object-cover opacity-70 motion-safe:animate-[wp-in_.6s_ease-out]" src={asset(w.img)} alt="" width={1920} height={820} />
        ) : (
          <span key={`g${w.n}`} className="absolute inset-0 -z-30" style={{ background: `radial-gradient(ellipse at 70% 30%, ${w.light}55 0%, ${w.bg} 50%, #0a0605 100%)` }} />
        )}
        <span className="absolute inset-0 -z-20 bg-[linear-gradient(0deg,rgba(10,6,5,.96)_0%,rgba(10,6,5,.55)_50%,rgba(10,6,5,.2)_100%)] md:bg-[linear-gradient(90deg,rgba(10,6,5,.95)_0%,rgba(10,6,5,.7)_34%,rgba(10,6,5,.15)_70%)]" />

        {/* type moment: the world's name, huge and hollow, behind the stage */}
        <p key={`t${w.n}`} aria-hidden="true"
          className="pointer-events-none absolute -right-4 bottom-[18%] -z-10 m-0 font-display text-[clamp(90px,15vw,240px)] leading-[0.8] font-normal whitespace-nowrap text-transparent uppercase opacity-60 motion-safe:animate-[wp-in_.8s_ease-out] [-webkit-text-stroke:1.5px_#d9a441]">
          {w.name}
        </p>

        {/* the stage: a beam of light, a gilded plinth, the boss, its creatures in front */}
        <div key={`s${w.n}`} className="pointer-events-none absolute right-0 bottom-0 -z-10 hidden h-full w-[56%] md:block" aria-hidden="true">
          <span className="absolute top-0 right-[16%] h-[92%] w-[46%] opacity-70 [clip-path:polygon(38%_0,62%_0,100%_100%,0_100%)]"
            style={{ background: `linear-gradient(180deg, ${w.light}00 0%, ${w.light}55 60%, ${w.light}22 100%)` }} />
          <span className="absolute right-[12%] bottom-[9%] h-[14%] w-[54%] rounded-[50%] border-2 border-gold-b/70 bg-[radial-gradient(ellipse,rgba(240,201,96,.35),rgba(10,6,5,.9)_70%)] shadow-[0_0_40px_rgba(240,201,96,.35)]" />
          <img className="bob absolute right-[20%] bottom-[14%] h-[76%] w-auto drop-shadow-[0_28px_30px_rgba(0,0,0,.8)] motion-safe:animate-[rise_.7s_cubic-bezier(.2,.8,.2,1)_both]"
            src={asset(`portraits/${w.boss}.png`)} alt="" width={512} height={512} />
          <div className="absolute right-[6%] bottom-[2%] flex items-end gap-0.5">
            {w.mobs.map((m, k) => (
              <img key={m} className="h-[clamp(56px,8.4vw,118px)] w-auto drop-shadow-[0_10px_10px_rgba(0,0,0,.75)] motion-safe:animate-[rise_.55s_cubic-bezier(.2,.8,.2,1)_both]"
                style={{ animationDelay: `${0.25 + 0.07 * k}s` }} src={asset(`portraits/${m}.png`)} alt="" width={256} height={256} />
            ))}
          </div>
        </div>

        {/* khokhloma blooms in the four corners of the lacquered frame */}
        {CORNERS.map((c) => (
          <svg key={c} className={`pointer-events-none absolute z-10 size-[clamp(44px,5vw,72px)] ${c}`} viewBox="-34 -34 68 68" aria-hidden="true">
            <use href="#bloom" />
          </svg>
        ))}

        {/* the words */}
        <div className="absolute right-5 bottom-[clamp(24px,4vw,52px)] left-[clamp(22px,4vw,60px)] z-10 md:right-auto md:max-w-[min(500px,46%)]">
          <p key={`n${w.n}`} className="m-0 font-pixel text-[clamp(64px,7vw,104px)] leading-[0.8] motion-safe:animate-[wp-in_.5s_ease-out]" style={{ color: w.light }}>
            {String(w.n).padStart(2, "0")}
          </p>
          <p className="m-0 mb-1 text-[13px] tracking-[0.18em] text-paper-dim">{w.label}</p>
          <h3 className="m-0 mb-3 font-display text-[clamp(36px,4.4vw,60px)] leading-[0.95] font-normal text-paper [text-shadow:0_4px_0_rgba(0,0,0,.7)]">{w.name}</h3>
          <p className="m-0 mb-2 font-body text-lg leading-snug font-bold text-gold-b">{w.short}</p>
          <p className="m-0 mb-5 line-clamp-3 text-base leading-normal text-paper">{w.long}</p>
          <Link className={btn} href={w.href}>{open} {w.name}</Link>
        </div>

        <button type="button" onClick={() => setAuto((a) => !a)} aria-pressed={!auto}
          className="absolute top-4 right-4 z-20 grid size-11 cursor-pointer place-items-center rounded-full border-2 border-gold bg-ink/70 text-gold-b hover:bg-ink">
          <span className="sr-only">{auto ? pauseLabel : playLabel}</span>
          <svg viewBox="0 0 24 24" className="size-5" fill="currentColor" aria-hidden="true">{auto ? <path d="M7 5h4v14H7zM13 5h4v14h-4z" /> : <path d="M8 5l11 7-11 7z" />}</svg>
        </button>
        {auto && <span key={`p${cur}`} className="wp-progress absolute right-0 bottom-0 left-0 z-20 h-1 bg-gold-b" style={{ "--t": "7s" } as React.CSSProperties} />}
      </div>

      {/* the shelf of dolls: the chosen one opens */}
      <div role="tablist" aria-label={listLabel}
        className="relative flex items-end gap-[clamp(4px,1.3vw,18px)] overflow-x-auto px-2 pt-10 md:justify-center md:overflow-visible"
        onKeyDown={(e) => {
          const k = { ArrowRight: cur + 1, ArrowLeft: cur - 1, Home: 0, End: worlds.length - 1 }[e.key];
          if (k !== undefined) { e.preventDefault(); go(k); }
        }}>
        {worlds.map((x, i) => {
          const on = i === cur;
          return (
            <button key={x.n} ref={(el) => { tabs.current[i] = el; }} id={`wp-tab-${x.n}`} role="tab" type="button"
              aria-selected={on} aria-controls="wp-panel" tabIndex={on ? 0 : -1} onClick={() => { setAuto(false); setCur(i); }}
              className={`group relative grid min-w-11 cursor-pointer justify-items-center gap-1.5 border-0 bg-transparent px-0 pb-3 ${on ? "text-gold-b" : "text-paper-dim hover:text-paper"}`}>
              <svg viewBox="-4 -30 108 204" aria-hidden="true" style={{ width: `calc(clamp(42px, 6.4vw, 86px) * ${1 - i * 0.045})` }}
                className={`h-auto overflow-visible drop-shadow-[0_5px_0_rgba(0,0,0,.45)] transition-transform duration-300 motion-reduce:transition-none ${on ? "-translate-y-1" : "group-hover:-translate-y-1"}`}>
                {on && <ellipse cx="50" cy="168" rx="56" ry="9" fill="rgba(240,201,96,.35)" />}
                <g className="transition-transform duration-500 motion-reduce:transition-none" style={{ transformOrigin: "50px 98px", transform: on ? "translateY(-26px) rotate(-6deg)" : "none" }}>
                  <use href="#doll" width="100" height="170" clipPath="url(#doll-top)" style={dollStyle(x)} />
                </g>
                {on && <ellipse cx="50" cy="99" rx="40" ry="5" fill="#0a0605" />}
                <use href="#doll" width="100" height="170" clipPath="url(#doll-bottom)" style={dollStyle(x)} />
              </svg>
              <span className="font-pixel text-xl leading-none">{x.n}</span>
              <span className="sr-only">{x.label}, {x.name}</span>
            </button>
          );
        })}
        {/* the lacquered shelf they stand on */}
        <span className="pointer-events-none absolute right-0 bottom-0 left-0 h-[10px] border-y-2 border-gold bg-lacquer bg-[radial-gradient(circle,#f0c960_1.2px,transparent_1.6px)] bg-[length:14px_10px]" />
      </div>
    </div>
  );
}
