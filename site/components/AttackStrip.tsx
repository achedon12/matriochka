"use client";
// The attacks of one boss on its poster: for each, the in-game wind-up and strike, swapped on hover and focus,
// and played once when the strip first scrolls into view. Each card opens the 3D viewer on that attack.
import { useEffect, useRef, useState } from "react";
import { asset } from "@/lib/data";
import type { BossMove } from "@/lib/types";
import { Icon } from "./Bits";

export interface StripLabels { windup: string; strike: string; warning: string; see3d: string }

function Card({ m, n, href, l, auto }: { m: BossMove; n: number; href: string; l: StripLabels; auto: boolean }) {
  const [hot, setHot] = useState(false);
  const strike = hot || auto;
  const pic = m.windup && m.strike;
  return (
    <li className="min-w-0">
      <a href={`${href}#anim-${m.slug}`} onMouseEnter={() => setHot(true)} onMouseLeave={() => setHot(false)} onFocus={() => setHot(true)} onBlur={() => setHot(false)}
        className="group grid h-full grid-cols-[minmax(0,128px)_minmax(0,1fr)] items-start gap-3 rounded-[3px] text-paper no-underline min-[640px]:grid-cols-1 min-[640px]:gap-2.5 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-gold-b">
        <span className="relative block aspect-[4/3] overflow-hidden rounded-[2px] border-2 border-gold bg-ink shadow-[0_0_0_3px_#17100d,0_0_0_4px_rgba(240,201,96,.34),0_10px_18px_rgba(0,0,0,.45)] transition-colors group-hover:border-gold-b">
          {pic ? (
            <>
              <img className="absolute inset-0 size-full object-cover" src={asset(m.windup!)} alt="" width={360} height={270} loading="lazy" decoding="async" />
              <img className={`absolute inset-0 size-full object-cover transition-opacity duration-200 ${strike ? "opacity-100" : "opacity-0"}`} src={asset(m.strike!)} alt="" width={360} height={270} loading="lazy" decoding="async" />
              <span className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_top,rgba(23,16,13,.62),rgba(23,16,13,0)_58%)] shadow-[inset_0_0_26px_rgba(23,16,13,.75)]" />
              <span className="absolute bottom-1.5 left-1.5 flex items-center gap-1.5 rounded-[2px] border border-rule bg-ink/85 px-1.5 pt-px pb-0.5 font-pixel text-[15px] leading-none text-gold-b" aria-hidden="true">
                <span className={`size-1.5 rounded-full ${strike ? "bg-gold/35" : "bg-gold-b"}`} />
                <span className={`size-1.5 rounded-full ${strike ? "bg-gold-b" : "bg-gold/35"}`} />
                {strike ? l.strike : l.windup}
              </span>
            </>
          ) : (
            <span className="absolute inset-0 grid place-items-center font-pixel text-5xl text-gold/50">{n}</span>
          )}
        </span>
        <span className="grid gap-1">
          <span className="flex items-baseline gap-2">
            <span className="font-pixel text-xl leading-none text-gold-b">{n}</span>
            <strong className="font-display text-[19px] leading-tight font-normal text-paper group-hover:text-gold-b">{m.name}</strong>
          </span>
          <small className="text-sm leading-snug text-paper-dim">{m.label} · <span className="whitespace-nowrap">{m.warn} {l.warning}</span></small>
          <span className="mt-0.5 inline-flex items-center gap-1.5 text-sm font-bold text-gold-b underline decoration-1 underline-offset-[3px] [&_svg]:size-4">
            <Icon name="rotate-3d" />{l.see3d}
          </span>
        </span>
      </a>
    </li>
  );
}

export default function AttackStrip({ moves, href, labels }: { moves: BossMove[]; href: string; labels: StripLabels }) {
  const ref = useRef<HTMLOListElement>(null);
  const [auto, setAuto] = useState(-1); // index of the card showing its strike on its own
  useEffect(() => {
    const el = ref.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timers: number[] = [];
    const io = new IntersectionObserver((es) => {
      if (!es.some((e) => e.isIntersecting)) return;
      io.disconnect();
      moves.forEach((_, k) => {
        timers.push(window.setTimeout(() => setAuto(k), 500 + k * 900));
      });
      timers.push(window.setTimeout(() => setAuto(-1), 500 + moves.length * 900));
    }, { threshold: 0.6 });
    io.observe(el);
    return () => { io.disconnect(); timers.forEach(clearTimeout); };
  }, [moves]);
  return (
    <ol ref={ref} className="m-0 grid list-none gap-4 p-0 min-[640px]:grid-cols-3 min-[640px]:gap-5">
      {moves.map((m, k) => <Card key={m.slug} m={m} n={k + 1} href={href} l={labels} auto={auto === k} />)}
    </ol>
  );
}
