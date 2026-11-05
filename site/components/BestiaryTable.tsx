"use client";
// The bestiary as a field guide: one dense table, filterable by world, and a single specimen stage that
// shows the selected creature's animated model (one canvas for the whole page).
import Link from "next/link";
import { useMemo, useRef, useState } from "react";
import { asset } from "@/lib/data";
import type { Lang, Mob } from "@/lib/types";
import ModelViewer, { type ViewerLabels } from "./viewer/ModelViewer";

export default function BestiaryTable({ lang, mobs, worlds, ui, viewer }: {
  lang: Lang; mobs: Mob[]; worlds: { n: number; name: string; rule: string | null; light: string }[];
  ui: Record<string, string>; viewer: ViewerLabels;
}) {
  const [world, setWorld] = useState<number | null>(null);
  const [sel, setSel] = useState(mobs[0].id);
  const shown = useMemo(() => worlds.filter((w) => world === null || w.n === world), [world, worlds]);
  const cur = mobs.find((m) => m.id === sel) ?? mobs[0];
  const prefix = lang === "fr" ? "/fr" : "";
  const specimen = useRef<HTMLElement>(null);
  const show = (id: string) => {
    setSel(id);
    // on narrow screens the stage sits above the table: bring it into view
    if (window.matchMedia("(max-width: 1023px)").matches) specimen.current?.scrollIntoView({ block: "start" });
  };
  return (
    <div className="bestiary">
      <div className="filters" role="group" aria-label={ui.filter}>
        <button type="button" className="chip-btn" aria-pressed={world === null} onClick={() => setWorld(null)}>{ui.all}</button>
        {worlds.map((w) => (
          <button key={w.n} type="button" className="chip-btn chip-world" aria-pressed={world === w.n} title={w.name}
            style={{ "--c": w.light } as React.CSSProperties} onClick={() => { setWorld(w.n); setSel(mobs.find((m) => m.world === w.n)!.id); }}>
            <span className="num">{w.n}</span><span className="sr-only"> {w.name}</span>
          </button>
        ))}
      </div>
      <div className="bestiary-grid">
        <div className="tbl tbl-guide">
          <table>
            <thead>
              <tr>
                <th scope="col">{ui.creature}</th>
                <th scope="col" className="c-num">{ui.health}</th>
                <th scope="col" className="c-num">{ui.damage}</th>
                <th scope="col">{ui.traits}</th>
                <th scope="col">{ui.drops}</th>
              </tr>
            </thead>
            {shown.map((w) => (
              <tbody key={w.n} id={`world-${w.n}`}>
                <tr className="tg">
                  <th scope="rowgroup" colSpan={5}>
                    <span className="num">{w.n}</span> {w.name} <span className="tg-rule" style={{ "--c": w.light } as React.CSSProperties}>{w.rule}</span>
                  </th>
                </tr>
                {mobs.filter((m) => m.world === w.n).map((m) => (
                  <tr key={m.id} id={`mob-${m.id}`} className={m.id === sel ? "is-sel" : undefined}>
                    <th scope="row" data-label={ui.creature}>
                      <span className="mob-name">
                        <Link href={`${prefix}/creatures/${m.id}/`}>{m.name}</Link>
                        <button type="button" className="view-btn" aria-pressed={m.id === sel} onClick={() => show(m.id)}>{viewer.view3d}<span className="sr-only">: {m.name}</span></button>
                      </span>
                      <span className="mob-desc">{m.desc}</span>
                    </th>
                    <td className="c-num num" data-label={ui.health}>{m.hp}</td>
                    <td className="c-num num" data-label={ui.damage}>{m.dmg}</td>
                    <td data-label={ui.traits}>{m.tags.join(", ")}</td>
                    <td data-label={ui.drops}>
                      <ul className="drops">
                        {m.drops.filter((dr) => !dr.bonus).map((dr) => (
                          <li key={dr.id}>
                            {dr.tex && <img className="px" src={asset(dr.tex)} width="20" height="20" alt="" loading="lazy" />}
                            {dr.name} <span className="num">{dr.chance}</span>
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            ))}
          </table>
        </div>
        <aside className="specimen" aria-label={ui.specimen} ref={specimen}>
          <div className="specimen-in">
            <h2 className="h-plate">{cur.name}</h2>
            <p className="small">{ui.world} {cur.world}, {cur.worldName}</p>
            <ModelViewer key={cur.id} id={cur.id} name={cur.name} anims={cur.anims} labels={viewer} tex={cur.tex} auto />
            <p className="specimen-stats">
              <span><span className="num">{cur.hp}</span> {ui.health.toLowerCase()}</span>
              <span><span className="num">{cur.dmg}</span> {ui.damage.toLowerCase()}</span>
            </p>
            <p><Link className="quiet" href={`${prefix}/creatures/${cur.id}/`}>{ui.open}</Link></p>
          </div>
        </aside>
      </div>
    </div>
  );
}
