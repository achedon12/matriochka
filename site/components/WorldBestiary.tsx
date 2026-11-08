"use client";
// A world's creatures and its boss on one stage: pick one, watch it move and attack, read what its attacks do.
import Link from "./PageLink";
import { useState } from "react";
import type { Anim } from "@/lib/types";
import ModelViewer, { type ViewerLabels } from "./viewer/ModelViewer";

export interface BestiaryEntry {
  id: string; name: string; tex: string | null; anims: Anim[]; badge: string | null; line: string;
  moves: { name: string; desc: string }[]; href: string; stats: { l: string; v: string }[];
}

export default function WorldBestiary({ entries, labels, sheet, movesH }: {
  entries: BestiaryEntry[]; labels: ViewerLabels; sheet: string; movesH: string;
}) {
  const [cur, setCur] = useState(0);
  const e = entries[cur];
  return (
    <div className="wb">
      <div className="wb-tabs" role="tablist" aria-label={movesH}>
        {entries.map((x, i) => (
          <button key={x.id} role="tab" type="button" aria-selected={i === cur} className={`wb-tab${x.badge ? " wb-tab-badge" : ""}`} onClick={() => setCur(i)}>
            <span>{x.name}</span>{x.badge && <small>{x.badge}</small>}
          </button>
        ))}
      </div>
      <div className="wb-stage" role="tabpanel">
        <ModelViewer key={e.id} id={e.id} name={e.name} anims={e.anims} labels={labels} tex={e.tex} auto className="viewer-sheet wb-viewer" />
        <div className="wb-info">
          <h3>{e.name}</h3>
          <p className="wb-line">{e.line}</p>
          <dl className="wb-stats">{e.stats.map((s) => <div key={s.l}><dt>{s.l}</dt><dd className="num">{s.v}</dd></div>)}</dl>
          {e.moves.length > 0 && (
            <>
              <h4>{movesH}</h4>
              <dl className="wb-moves">{e.moves.map((m) => <div key={m.name}><dt>{m.name}</dt><dd>{m.desc}</dd></div>)}</dl>
            </>
          )}
          <p><Link className="quiet" href={e.href}>{sheet}</Link></p>
        </div>
      </div>
    </div>
  );
}
