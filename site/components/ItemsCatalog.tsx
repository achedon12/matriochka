"use client";
// The catalogue as the game's own inventory: the thirteen stations on a shelf, a row of nested dolls that opens one
// world, every item and block as a slot, and a lacquered sheet for the one picked: its recipe drawn slot by slot,
// where it comes from and what it makes. Every ingredient, station and use opens its own sheet, and the address
// follows the sheet (#id), so a link opens it.
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { asset } from "@/lib/asset";
import type { CodexEntry, DollColours } from "@/lib/types";
import { Craft, Slot } from "./Craft";
import { badgeText, HistoryList, VBadge, type VersionLabels } from "./Version";
import type { Hist, Mark } from "@/lib/versions";

/** An entry with its badge and history in the version shown. */
type Dated = CodexEntry & { mark?: Mark; hist?: Hist | null };
type World = { n: number; name: string; doll: DollColours; light: string; items: Dated[]; blocks: Dated[] };
type Entry = Dated & { world: number; block: boolean };

const RARE: Record<string, string> = { rare: "rare", epic: "epic", "épique": "epic", legendary: "legendary", "légendaire": "legendary" };
const rarity = (e: CodexEntry) => RARE[(e.rarity ?? "").toLowerCase()] ?? "common";

function Doll({ c, open, h }: { c: DollColours; open: boolean; h: number }) {
  const style = { "--db": c.body, "--ds": c.scarf, "--do": c.orn } as React.CSSProperties;
  return (
    <svg viewBox="-6 -40 112 216" style={{ height: h, width: "auto" }} aria-hidden="true" className="ic-doll">
      <g className="ic-lid" style={{ transform: open ? "translateY(-46px) rotate(-12deg)" : undefined }}>
        <use href="#doll" width="100" height="170" clipPath="url(#doll-top)" style={style} />
      </g>
      <use href="#doll" width="100" height="170" clipPath="url(#doll-bottom)" style={style} />
    </svg>
  );
}

export default function ItemsCatalog({ worlds, c, vl, missing }: {
  worlds: World[]; c: Record<string, string>; vl: VersionLabels;
  /** in an older version: what to say when the address names an item it does not have, and the latest items page */
  missing?: { text: string; latest: string };
}) {
  const all = useMemo<Entry[]>(() => worlds.flatMap((w) => [
    ...w.items.map((e) => ({ ...e, world: w.n, block: false })),
    ...w.blocks.map((e) => ({ ...e, world: w.n, block: true })),
  ]), [worlds]);
  const byId = useMemo(() => new Map(all.map((e) => [e.id, e])), [all]);
  const usedIn = useMemo(() => {
    const m = new Map<string, Entry[]>();
    for (const e of all) for (const i of e.inputs) m.set(i.id, [...(m.get(i.id) ?? []), e]);
    return m;
  }, [all]);
  const stations = useMemo(() => all.filter((e) => e.kind === "station"), [all]);

  const [q, setQ] = useState("");
  const [kind, setKind] = useState<"all" | "items" | "blocks">("all");
  const [world, setWorld] = useState<number | null>(null);
  const [sel, setSel] = useState<string>(stations[0]?.id ?? all[0]?.id);
  const sheet = useRef<HTMLElement>(null);
  const [lost, setLost] = useState<string | null>(null);

  // the sheet follows the address, so a shared link opens it
  useEffect(() => {
    const read = () => {
      const id = decodeURIComponent(location.hash.slice(1));
      if (byId.has(id)) setSel(id);
      setLost(id && !byId.has(id) ? id : null);
    };
    read();
    window.addEventListener("hashchange", read);
    return () => window.removeEventListener("hashchange", read);
  }, [byId]);

  const open = useCallback((id: string, scroll = true) => {
    if (!byId.has(id)) return;
    setSel(id);
    setLost(null);
    history.replaceState(null, "", `#${id}`);
    // on a narrow screen the sheet sits under the shelf: bring it into view
    if (scroll && sheet.current && window.matchMedia("(max-width: 979px)").matches) {
      const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      sheet.current.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" });
    }
  }, [byId]);
  const pick = useCallback((id: string) => (byId.has(id) ? () => open(id) : undefined), [byId, open]);

  const groups = useMemo(() => {
    const s = q.trim().toLowerCase();
    const hit = (e: Entry) => (kind === "all" || (kind === "blocks") === e.block) && (!s || e.name.toLowerCase().includes(s)
      || e.effect.toLowerCase().includes(s) || e.inputs.some((i) => i.name.toLowerCase().includes(s)) || (e.station ?? "").toLowerCase().includes(s));
    return worlds.filter((w) => world === null || w.n === world)
      .map((w) => ({ w, list: all.filter((e) => e.world === w.n && hit(e)) })).filter((g) => g.list.length);
  }, [worlds, all, q, kind, world]);
  const total = groups.reduce((a, g) => a + g.list.length, 0);
  const e = byId.get(sel);
  const ew = e ? worlds.find((w) => w.n === e.world) : undefined;
  const uses = e ? (usedIn.get(e.id) ?? []) : [];
  // a station's sheet lists everything it makes, each opening its own sheet
  const makes = e && e.kind === "station" ? all.filter((x) => x.stationId === e.id) : [];

  return (
    <div className="icat">
      <section className="ic-shelf" aria-labelledby="ic-st">
        <h2 id="ic-st" className="ic-h">{c.stationsH}</h2>
        <p className="ic-sub">{c.stationsP}</p>
        <ul className="ic-stations">
          {stations.map((s) => (
            <li key={s.id}>
              <button type="button" className="ic-station" aria-pressed={sel === s.id} onClick={() => open(s.id)}
                style={{ "--wl": worlds.find((w) => w.n === s.world)?.light } as React.CSSProperties}>
                {s.tex && <img src={asset(s.tex)} alt="" width={96} height={96} loading="lazy" decoding="async" />}
                <span className="ic-station-n">{s.name}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <div className="ic-dolls" role="group" aria-label={c.allWorlds}>
        {worlds.map((w, i) => (
          <button key={w.n} type="button" className="ic-dollbtn" aria-pressed={world === w.n} title={w.name}
            onClick={() => setWorld(world === w.n ? null : w.n)} style={{ "--wl": w.light } as React.CSSProperties}>
            <Doll c={w.doll} open={world === w.n} h={Math.round(104 * 0.93 ** i)} />
            <span className="ic-dolln">{w.n}</span>
            <span className="sr-only">{w.name}</span>
          </button>
        ))}
      </div>

      <p className="ic-dollname" aria-live="polite">{world === null ? c.allWorlds : (world === 0 ? worlds[0].name : `${c.world} ${world}, ${worlds.find((w) => w.n === world)?.name}`)}</p>

      <div className="ic-tools">
        <label className="ic-search">
          <span className="sr-only">{c.search}</span>
          <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" /><path d="m20 20-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          <input type="search" value={q} onChange={(ev) => setQ(ev.target.value)} placeholder={c.search} autoComplete="off" spellCheck={false} />
        </label>
        <div className="ic-seg" role="group" aria-label={c.all}>
          {(["all", "items", "blocks"] as const).map((k) => (
            <button key={k} type="button" aria-pressed={kind === k} onClick={() => setKind(k)}>
              {k === "all" ? c.all : k === "items" ? c.onlyItems : c.onlyBlocks}
            </button>
          ))}
        </div>
        <span className="ic-count" aria-live="polite">
          {c.count.replace("{n}", String(total))}
        </span>
      </div>

      <div className="ic-main">
        <div className="ic-inv">
          {groups.length === 0 && <p className="ic-empty">{c.none}</p>}
          {groups.map(({ w, list }) => (
            <section key={w.n} className="ic-world" aria-labelledby={`icw-${w.n}`} style={{ "--wl": w.light } as React.CSSProperties}>
              <h3 id={`icw-${w.n}`}><span className="ic-wn">{w.n}</span>{w.name}<span className="ic-wc">{list.length}</span></h3>
              <ul className="ic-grid">
                {list.map((x) => (
                  <li key={x.id}>
                    <button type="button" className={`ic-slot ic-${rarity(x)}`} aria-pressed={x.id === sel} onClick={() => open(x.id)}>
                      {x.tex ? <img className="px" src={asset(x.tex)} alt="" loading="lazy" decoding="async" /> : <span className="mc-slot-blank">?</span>}
                      <span className="ic-tip" aria-hidden="true">{x.name}</span>
                      <span className="sr-only">{x.name}{x.mark && `, ${badgeText(x.mark, vl)}`}</span>
                      {x.mark && <span className={`ic-pip ic-pip-${x.mark.kind}`} aria-hidden="true" />}
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        <aside className="ic-sheet" ref={sheet} aria-live="polite" style={{ "--wl": ew?.light } as React.CSSProperties}>
          {lost && missing ? (
            <article className="ic-card">
              <p className="ic-eff">{missing.text}</p>
              <p className="ic-src"><a href={`${missing.latest}#${lost}`}>{vl.seeLatest}</a></p>
            </article>
          ) : e && (
            <article key={e.id} className="ic-card">
              <div className="ic-plinth">
                <span className="ic-halo" aria-hidden="true" />
                {e.tex && <img className={e.kind === "station" ? "ic-model" : "px ic-big"} src={asset(e.tex)} alt="" />}
              </div>
              <h2 className="ic-name">{e.name}</h2>
              <p className="ic-meta">
                {e.rarity && <span className={`ic-r ic-r-${rarity(e)}`}>{e.rarity}</span>}
                <span>{e.block ? c.aBlock : c.anItem}</span>
                {ew && <button type="button" className="ic-wlink" onClick={() => setWorld(ew.n)}>{ew.n === 0 ? ew.name : `${c.world} ${ew.n}, ${ew.name}`}</button>}
                <VBadge m={e.mark} l={vl} />
              </p>
              {e.effect && <p className="ic-eff">{e.effect}</p>}
              {e.stats && e.stats.length > 0 && (
                <>
                  <h3 className="ic-sh">{c.statsH}</h3>
                  <dl className="ic-stats">
                    {e.stats.map((x, k) => <div key={k}><dt>{x.k}</dt><dd>{x.v}</dd></div>)}
                  </dl>
                  {(e.kind === "weapon" || e.kind === "armor") && <p className="ic-note">{c.statsNote}</p>}
                </>
              )}

              <h3 className="ic-sh">{c.recipeH}</h3>
              {e.inputs.length > 0
                ? <Craft inputs={e.inputs} out={{ tex: e.tex, name: e.name, count: e.count }} pick={pick} grid={e.grid}
                    station={e.station ? { id: e.stationId ?? undefined, tex: e.stationTex ?? null, name: e.station } : null} label={`${c.made} ${e.station ?? ""}`} />
                : <p className="ic-note">{e.drops.length || e.yields ? c.noCraft : c.noRecipe}</p>}
              {e.drops.length > 0 && <p className="ic-src">{c.found} <strong>{e.drops.join(", ")}</strong></p>}
              {e.yields && <p className="ic-src">{c.gives} <strong>{e.yields}</strong></p>}

              {makes.length > 0 && (
                <>
                  <h3 className="ic-sh">{c.makesH} <span className="ic-shn">{makes.length}</span></h3>
                  <ul className="ic-uses">
                    {makes.map((u) => <li key={u.id}><Slot tex={u.tex} name={u.name} n={u.count} onPick={() => open(u.id)} /></li>)}
                  </ul>
                </>
              )}
              {uses.length > 0 && (
                <>
                  <h3 className="ic-sh">{c.usesH}</h3>
                  <ul className="ic-uses">
                    {uses.map((u) => <li key={u.id}><Slot tex={u.tex} name={u.name} onPick={() => open(u.id)} /></li>)}
                  </ul>
                </>
              )}
              {e.hist && (
                <>
                  <h3 className="ic-sh">{vl.historyH}</h3>
                  <HistoryList h={e.hist} l={vl} />
                </>
              )}
            </article>
          )}
        </aside>
      </div>
    </div>
  );
}
