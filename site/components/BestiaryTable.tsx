"use client";
// The bestiary as a field guide of portraits: filter by world, show elites only, or search by name.
// Every card opens the creature's technical sheet.
import Link from "next/link";
import { useMemo, useState } from "react";
import { asset } from "@/lib/data";
import type { Lang, Mob } from "@/lib/types";
import type { ViewerLabels } from "./viewer/ModelViewer";

export default function BestiaryTable({ lang, mobs, worlds, ui }: {
  lang: Lang; mobs: Mob[]; worlds: { n: number; name: string; rule: string | null; light: string }[];
  ui: Record<string, string>; viewer?: ViewerLabels;
}) {
  const [world, setWorld] = useState<number | null>(null);
  const [elite, setElite] = useState(false);
  const [q, setQ] = useState("");
  const prefix = lang === "fr" ? "/fr" : "";
  const shown = useMemo(() => {
    const s = q.trim().toLowerCase();
    return mobs.filter((m) => (world === null || m.world === world) && (!elite || m.elite)
      && (!s || m.name.toLowerCase().includes(s) || m.moves.some((x) => x.name.toLowerCase().includes(s))));
  }, [mobs, world, elite, q]);
  const groups = worlds.map((w) => ({ w, list: shown.filter((m) => m.world === w.n) })).filter((g) => g.list.length);
  return (
    <div className="bx">
      <div className="bx-bar">
        <div className="bx-worlds" role="group" aria-label={ui.filter}>
          <button type="button" className="chip-btn" aria-pressed={world === null} onClick={() => setWorld(null)}>{ui.all}</button>
          {worlds.map((w) => (
            <button key={w.n} type="button" className="chip-btn chip-world" aria-pressed={world === w.n}
              style={{ "--c": w.light } as React.CSSProperties} onClick={() => setWorld(world === w.n ? null : w.n)}>
              <span className="num">{w.n}</span> <span className="bx-wname">{w.name}</span>
            </button>
          ))}
        </div>
        <div className="bx-tools">
          <label className="bx-search">
            <span className="sr-only">{ui.search}</span>
            <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder={ui.searchPh} autoComplete="off" spellCheck={false} />
          </label>
          <label className="bx-check"><input type="checkbox" checked={elite} onChange={(e) => setElite(e.target.checked)} /> {ui.elitesOnly}</label>
        </div>
      </div>
      <p className="bx-count" aria-live="polite">{shown.length} / {mobs.length}</p>
      {groups.length === 0 && <p className="bx-empty">{ui.noMatch}</p>}
      {groups.map(({ w, list }) => (
        <section key={w.n} className="bx-group" aria-labelledby={`bx-w${w.n}`} style={{ "--wl": w.light } as React.CSSProperties}>
          <h2 id={`bx-w${w.n}`} className="bx-h"><span className="num">{w.n}</span>{w.name}{w.rule && <small>{w.rule}</small>}</h2>
          <ul className="bx-grid">
            {list.map((m) => (
              <li key={m.id} className="reveal">
                <Link className="bx-card" href={`${prefix}/creatures/${m.id}/`} style={{ "--cb": m.bg } as React.CSSProperties}>
                  <span className="bx-art"><img src={asset(`portraits/${m.id}.png`)} alt="" loading="lazy" decoding="async" width={512} height={512} /></span>
                  <span className="bx-name">{m.name}{m.elite && <em className="bx-elite">{ui.elite}</em>}</span>
                  <span className="bx-desc">{m.desc}</span>
                  <span className="bx-stats"><span><small>{ui.health}</small><b className="num">{m.hp}</b></span><span><small>{ui.damage}</small><b className="num">{m.dmg}</b></span></span>
                  <span className="bx-moves">{m.moves.map((x) => x.name).join(", ")}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
