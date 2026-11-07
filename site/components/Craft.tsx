import { asset } from "@/lib/data";
import type { Ing } from "@/lib/types";

/**
 * One inventory slot: the item's picture pixel for pixel, its count in the corner like in game, its name on hover.
 * With `onPick` it becomes a button that opens that item's sheet (the catalogue's ingredients and uses).
 */
export function Slot({ tex, name, n, big = false, onPick }: { tex: string | null; name: string; n?: number; big?: boolean; onPick?: () => void }) {
  const inner = (
    <>
      {tex ? <img className="px" src={asset(tex)} alt="" loading="lazy" decoding="async" /> : <span className="mc-slot-blank" aria-hidden="true">?</span>}
      {n !== undefined && n > 1 && <span className="mc-count" aria-hidden="true">{n}</span>}
      <span className="sr-only">{n && n > 1 ? `${name} ×${n}` : name}</span>
    </>
  );
  const cls = `mc-slot${big ? " mc-slot-big" : ""}${onPick ? " mc-slot-link" : ""}`;
  return onPick
    ? <button type="button" className={cls} title={name} onClick={onPick}>{inner}</button>
    : <span className={cls} title={name}>{inner}</span>;
}

/**
 * A recipe drawn as the station shows it: the ingredients in their slots, the station itself (its sculpted model)
 * over the arrow that leads to the result. Without a station the arrow stands alone.
 */
export function Craft({ inputs, out, station, label, pick, grid }: {
  inputs: Ing[]; out: { id?: string; tex: string | null; name: string; count: number }; station?: { id?: string; tex: string | null; name: string } | null;
  label?: string; pick?: (id: string) => (() => void) | undefined; grid?: (Ing | null)[] | null;
}) {
  const st = station?.id && pick ? pick(station.id) : undefined;
  return (
    <figure className="mc-craft" aria-label={label ?? out.name}>
      {grid
        // a workbench recipe: its pattern on the 3 x 3 grid, each cell where it goes in the game
        ? <ul className="mc-grid">{grid.map((c, k) => <li key={k}>{c ? <Slot tex={c.tex} name={c.name} n={c.n} onPick={pick?.(c.id)} /> : <span className="mc-slot" aria-hidden="true" />}</li>)}</ul>
        : <ul className="mc-ins">
            {inputs.map((i) => <li key={i.id}><Slot tex={i.tex} name={i.name} n={i.n} onPick={pick?.(i.id)} /></li>)}
          </ul>}
      <span className="mc-via">
        {station?.tex && (st
          ? <button type="button" className="mc-station-btn" onClick={st} title={station.name}><img className="mc-station" src={asset(station.tex)} alt="" loading="lazy" decoding="async" /></button>
          : <img className="mc-station" src={asset(station.tex)} alt="" loading="lazy" decoding="async" />)}
        <span className="mc-arrow" aria-hidden="true" />
        {station && <span className="mc-station-name">{station.name}</span>}
      </span>
      <Slot tex={out.tex} name={out.name} n={out.count} big onPick={out.id ? pick?.(out.id) : undefined} />
    </figure>
  );
}
