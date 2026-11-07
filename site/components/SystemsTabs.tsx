"use client";
// The systems as tiles; one panel open at a time, so the page stays short. The open panel follows the URL hash.
import { useEffect, useState } from "react";
import { asset } from "@/lib/data";
import type { Ing } from "@/lib/types";
import { Icon, Ingredients, Inlay } from "./Bits";
import { Craft } from "./Craft";

/* eslint-disable @typescript-eslint/no-explicit-any */
type S = Record<string, any>;

function Feature({ f }: { f: { tex: string | null; h: string; p: string; inputs?: Ing[]; station?: { tex: string | null; name: string } | null; count?: number; grid?: (Ing | null)[] | null } }) {
  return (
    <div className="border border-rule bg-ink/60 p-4">
      <h4 className="m-0 mb-1.5 flex items-center gap-2 font-body text-lg font-bold text-paper"><Inlay src={f.tex} size={32} />{f.h}</h4>
      <p className="m-0 mb-2 text-[15px] leading-snug text-paper-dim">{f.p}</p>
      {f.inputs && f.inputs.length > 0 && (f.station
        ? <Craft inputs={f.inputs} grid={f.grid} out={{ tex: f.tex, name: f.h, count: f.count ?? 1 }} station={f.station} />
        : <Ingredients inputs={f.inputs} />)}
    </div>
  );
}

const panel = "grid gap-6";

function Photo({ src, caption, pixel = false }: { src: string | null; caption: string; pixel?: boolean }) {
  if (!src) return null;
  return (
    <figure className="m-0">
      <div className="border-2 border-gold bg-black shadow-frame">
        <img className={`block h-auto w-full ${pixel ? "[image-rendering:pixelated]" : ""}`} src={asset(src)} alt={caption} loading="lazy" decoding="async" />
      </div>
      <figcaption className="mt-1.5 text-[13px] text-paper-dim">{caption}</figcaption>
    </figure>
  );
}

function Bullets({ items }: { items: string[] }) {
  return (
    <ul className="m-0 grid list-none content-start gap-2 p-0">
      {items.map((x) => <li key={x} className="border-l-4 border-gold bg-ink/50 px-3 py-2 text-[15px] leading-snug text-paper">{x}</li>)}
    </ul>
  );
}
const h3 = "m-0 mb-3 font-display text-[26px] font-normal text-gold-b";

function Survival({ s }: { s: S }) {
  return (
    <div className={`${panel} md:grid-cols-[2fr_3fr]`}>
      <div className="border-2 border-gold bg-ink/80 p-5">
        <div className="mb-3 flex items-end justify-center gap-3">
          {[1, 0.82, 0.66].map((k, i) => (
            <svg key={i} viewBox="0 0 100 170" className="h-auto" style={{ width: 70 * k }} aria-hidden="true">
              <use href="#doll" width="100" height="170" style={{ "--db": "#8e2a21", "--ds": "#d9a441", "--do": "#f3e2c2" } as React.CSSProperties} />
            </svg>
          ))}
        </div>
        <h3 className="m-0 mb-1 flex items-center gap-2 font-display text-2xl font-normal text-gold-b"><Inlay src={s.lifeDoll.tex} size={32} />{s.lifeDoll.h}</h3>
        <p className="m-0 text-[15px] leading-snug text-paper">{s.lifeDoll.p}</p>
      </div>
      <div>
        <h3 className={h3}>{s.deathH}</h3>
        <ol className="m-0 mb-5 grid list-none gap-2 p-0">
          {s.death.map((x: string, i: number) => (
            <li key={x} className="grid grid-cols-[36px_minmax(0,1fr)] items-baseline gap-2 text-[15px] leading-snug text-paper">
              <span className="grid size-8 place-items-center rounded-full border-2 border-gold font-pixel text-lg text-gold-b">{i + 1}</span><span>{x}</span>
            </li>
          ))}
        </ol>
        <div className="grid gap-3 sm:grid-cols-2">{s.features.map((f: any) => <Feature key={f.h} f={f} />)}</div>
      </div>
    </div>
  );
}

function Souls({ s }: { s: S }) {
  const pos = (v: string) => (Number(v.replace("−", "-")) + 100) / 2;
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.soulsLead}</p>
      <ul className="m-0 flex list-none flex-wrap gap-3 p-0">
        {s.rarity.map((r: any) => (
          <li key={r.k} className="min-w-[120px] border-2 border-gold bg-ink/80 px-4 py-3 text-center">
            <span className="block font-pixel text-3xl leading-none text-gold-b">{r.v}</span><span className="text-[13px] text-paper-dim">{r.k}</span>
          </li>
        ))}
      </ul>
      <p className="m-0 text-[14px] text-paper-dim">{s.karmaNote}</p>
      <div>
        <h3 className={h3}>{s.karmaH}</h3>
        {/* the karma line, from devourer to saint */}
        <div className="relative mx-2 mt-10 mb-4 h-3 rounded-full bg-[linear-gradient(90deg,#3a0a14,#5a5a62_50%,#d9a441)]">
          {s.karma.map((k: any) => (
            <span key={k.v} className="absolute -top-8 -translate-x-1/2 font-pixel text-xl text-paper" style={{ left: `${pos(k.v)}%` }}>{k.v}</span>
          ))}
          {s.karma.map((k: any) => (
            <span key={`d${k.v}`} className="absolute top-1/2 size-4 -translate-1/2 rounded-full border-2 border-ink bg-gold-b" style={{ left: `${pos(k.v)}%` }} />
          ))}
        </div>
        <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2 lg:grid-cols-5">
          {[...s.karma].sort((a: any, b: any) => pos(a.v) - pos(b.v)).map((k: any) => (
            <li key={k.v} className="border border-rule bg-ink/60 p-3 text-[14px] leading-snug text-paper"><strong className="mb-1 block font-pixel text-xl text-gold-b">{k.v}</strong>{k.p}</li>
          ))}
        </ul>
        <p className="mt-3 text-[14px] text-paper-dim">{s.karmaEnd}</p>
      </div>
    </div>
  );
}

function Classes({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.classesLead}</p>
      <ul className="m-0 grid list-none gap-3 p-0 sm:grid-cols-2 lg:grid-cols-3">
        {s.classes.map((c: any) => (
          <li key={c.name} className="border-2 border-gold bg-ink/80 p-4">
            <h4 className="m-0 mb-1 font-display text-2xl font-normal text-gold-b">{c.name}</h4>
            <p className="m-0 mb-1 text-[15px] text-paper">{c.bonus}</p>
            <p className="m-0 text-[13px] text-paper-dim">{c.slot}</p>
          </li>
        ))}
      </ul>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h3 className={h3}>{s.upH}</h3>
          <ol className="m-0 flex list-none items-end gap-2 p-0">
            {s.up.map((u: any, i: number) => (
              <li key={u.lv} className="flex-1 text-center">
                <span className="mb-1 block font-pixel text-lg text-gold-b">{u.bonus}</span>
                <span className="block border-2 border-gold bg-[linear-gradient(0deg,#a33a2a,#d9a441)]" style={{ height: 24 + i * 22 }} />
                <span className="mt-1 block text-[13px] text-paper">{s.upCols[0]} {u.lv}</span>
                <span className="block text-[12px] text-paper-dim">{u.souls} {s.upCols[2].toLowerCase()}</span>
              </li>
            ))}
          </ol>
          <p className="mt-3 text-[14px] text-paper-dim">{s.upNote}</p>
        </div>
        <div>
          <h3 className={h3}>{s.capH}</h3>
          <ul className="m-0 grid list-none gap-2 p-0">
            {s.cap.map((c: any) => (
              <li key={c.k} className="flex items-center justify-between border-b border-rule py-2 text-[15px] text-paper"><span>{c.k}</span><span className="font-pixel text-2xl text-gold-b">{c.v}</span></li>
            ))}
          </ul>
          <div className="mt-4"><Feature f={s.chance} /></div>
        </div>
      </div>
      <div>
        <h3 className={h3}>{s.talentsH}</h3>
        <p className="m-0 mb-4 max-w-[70ch] text-paper">{s.talentsLead}</p>
        <div className="tbl mb-4"><table>
          <thead><tr>{s.talentCols.map((c: string) => <th scope="col" key={c}>{c}</th>)}</tr></thead>
          <tbody>{s.talentTiers.map((r: any) => <tr key={r.lv}><th scope="row">{r.lv}</th><td className="num">{r.souls}</td><td className="num">{r.shards}</td><td>{r.gate}</td></tr>)}</tbody>
        </table></div>
        <ul className="m-0 grid list-none gap-3 p-0 md:grid-cols-2 lg:grid-cols-3">
          {s.talentTree.map((c: any) => (
            <li key={c.cls} className="border-2 border-gold bg-ink/80 p-4">
              <h4 className="m-0 mb-2 font-display text-2xl font-normal text-gold-b">{c.cls}</h4>
              {c.branches.map((b: any) => (
                <div key={b.name} className="mb-2 last:mb-0">
                  <p className="m-0 font-body text-[15px] font-bold text-paper">{b.name}</p>
                  <ol className="m-0 list-none p-0">
                    {b.talents.map((x: any, i: number) => (
                      <li key={x.name} className="text-[13px] leading-snug text-paper-dim"><span className="font-pixel text-gold-b">{i + 1}</span> {x.name}: {x.eff}</li>
                    ))}
                  </ol>
                </div>
              ))}
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[14px] text-paper-dim">{s.talentNote}</p>
      </div>
    </div>
  );
}

function Workshop({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.gearLead}</p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{s.gear.map((f: any) => <Feature key={f.h} f={f} />)}</div>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h3 className={h3}>{s.autoH}</h3>
          <Bullets items={s.auto} />
        </div>
        <div className="grid content-start gap-4">
          <Photo src={s.autoShot.src} caption={s.autoShot.caption} />
          <Feature f={s.shake} />
        </div>
      </div>
    </div>
  );
}

function Trials({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.trialsLead}</p>
      <ul className="m-0 grid list-none gap-3 p-0 sm:grid-cols-2 lg:grid-cols-4">
        {s.trialFacts.map((f: any) => (
          <li key={f.k} className="border-2 border-gold bg-ink/80 px-4 py-3">
            <span className="block text-[13px] text-paper-dim">{f.k}</span>
            <span className="block font-pixel text-2xl leading-tight text-gold-b">{f.v}</span>
            <span className="block text-[13px] leading-snug text-paper">{f.d}</span>
          </li>
        ))}
      </ul>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="tbl"><table>
          <thead><tr>{s.trialCols.map((c: string) => <th scope="col" key={c}>{c}</th>)}</tr></thead>
          <tbody>{s.trialList.map((r: any) => <tr key={r.name}><th scope="row"><span className="inline-flex items-center gap-2"><Inlay src={r.tex} size={24} />{r.name}</span></th><td className="num">{r.par}</td></tr>)}</tbody>
        </table></div>
        <div>
          <h3 className={h3}>{s.boardH}</h3>
          <p className="m-0 text-[15px] text-paper">{s.board}</p>
        </div>
      </div>
      <div>
        <h3 className={h3}>{s.eventsH}</h3>
        <p className="m-0 mb-4 max-w-[70ch] text-paper">{s.eventsLead}</p>
        <ul className="m-0 mb-4 grid list-none gap-3 p-0 md:grid-cols-3">
          {s.events.map((e: any) => (
            <li key={e.h} className="border-2 border-gold bg-ink/80 p-4">
              <h4 className="m-0 mb-1 flex items-center gap-2 font-display text-2xl font-normal text-gold-b"><Icon name={e.icon} className="size-6" />{e.h}</h4>
              <p className="m-0 text-[15px] leading-snug text-paper">{e.p}</p>
            </li>
          ))}
        </ul>
        <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2">
          {s.surges.map((x: any) => (
            <li key={x.w} className="grid grid-cols-[36px_minmax(0,1fr)] items-baseline gap-2 border border-rule bg-ink/60 p-3">
              <span className="font-pixel text-xl text-gold-b">{x.w}</span>
              <span className="text-[14px] leading-snug text-paper"><strong className="text-paper">{x.name}</strong> <span className="text-paper-dim">{x.p}</span></span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[14px] text-paper-dim">{s.eventsNote}</p>
      </div>
    </div>
  );
}

function Comfort({ s }: { s: S }) {
  return (
    <div className={panel}>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <h3 className={h3}>{s.comfortH}</h3>
          <p className="m-0 mb-3 text-[15px] text-paper-dim">{s.comfortLead}</p>
          <Bullets items={s.comfort} />
        </div>
        <Photo src={s.comfortShot.src} caption={s.comfortShot.caption} pixel />
      </div>
      <div>
        <h3 className={h3}>{s.cineH}</h3>
        <div className="grid gap-6 md:grid-cols-2">
          <Bullets items={s.cine} />
          <div className="grid content-start gap-4">{s.cineShots.map((j: any) => <Photo key={j.src} src={j.src} caption={j.caption} />)}</div>
        </div>
      </div>
      <div>
        <h3 className={h3}>{s.atmosH}</h3>
        <p className="m-0 mb-4 max-w-[70ch] text-paper">{s.atmos}</p>
        <div className="grid gap-4 md:grid-cols-2">{s.atmosShots.map((j: any) => <Photo key={j.src} src={j.src} caption={j.caption} />)}</div>
      </div>
      <div>
        <h3 className={h3}>{s.langH}</h3>
        <p className="m-0 max-w-[70ch] text-paper">{s.lang}</p>
      </div>
    </div>
  );
}

function Nesting({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.nestingLead}</p>
      <ul className="m-0 grid list-none gap-3 p-0 sm:grid-cols-2 lg:grid-cols-3">
        {s.nest.map((n: any, i: number) => (
          <li key={n.a} className="relative overflow-hidden border-2 border-gold bg-ink/80 p-4 pl-16">
            <svg viewBox="0 0 100 170" className="absolute top-3 left-3 h-12 w-auto" aria-hidden="true">
              <use href="#doll" width="100" height="170" style={{ "--db": ["#8e2a21", "#3f6b2a", "#e0661c", "#5a5a62", "#3a7ac8", "#1f2a4a"][i % 6], "--ds": "#d9a441", "--do": "#f3e2c2" } as React.CSSProperties} />
            </svg>
            <h4 className="m-0 mb-1 font-body text-lg font-bold text-paper">{n.a}</h4>
            <p className="m-0 mb-1 text-[15px] text-paper-dim">{n.b}</p>
            <p className="m-0 text-[13px] text-gold-b">{n.c}</p>
          </li>
        ))}
      </ul>
      <div>
        <h3 className={h3}>{s.gatesH}</h3>
        <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2">
          {s.gates.map((g: string) => <li key={g} className="border-l-4 border-gold bg-ink/50 px-3 py-2 text-[15px] text-paper">{g}</li>)}
        </ul>
      </div>
    </div>
  );
}

function Groups({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.groupsLead}</p>
      <ul className="m-0 grid list-none gap-2 p-0 md:grid-cols-2">
        {s.cmds.map((c: any) => (
          <li key={c.c} className="border border-rule bg-black/40 p-3">
            <code className="block bg-transparent p-0 font-mono text-[15px] text-gold-b">{c.c}</code>
            <span className="text-[14px] text-paper-dim">{c.d}</span>
          </li>
        ))}
      </ul>
      <p className="m-0 text-[14px] text-paper-dim">{s.serverNote}</p>
    </div>
  );
}

function Journal({ s }: { s: S }) {
  return (
    <div className={panel}>
      <p className="m-0 max-w-[70ch] text-paper">{s.journalLead}</p>
      <div className="grid gap-4 md:grid-cols-2">
        {s.journalShots.map((j: any) => (
          <div key={j.src} className="border-2 border-gold bg-black shadow-frame"><img className="block h-auto w-full [image-rendering:pixelated]" src={asset(j.src)} alt={j.caption} loading="lazy" /></div>
        ))}
      </div>
      <Feature f={s.firstSteps} />
      <div>
        <h3 className={h3}>{s.titlesH}</h3>
        <ul className="m-0 flex list-none flex-wrap gap-2 p-0">
          {s.titles.map((x: string) => <li key={x} className="rounded-[2px] border border-gold px-3 py-1 text-[14px] text-paper">{x}</li>)}
        </ul>
        <p className="mt-3 text-[14px] text-paper-dim">{s.titlesNote}</p>
      </div>
    </div>
  );
}

const PANELS: Record<string, (p: { s: S }) => React.ReactElement> = { survival: Survival, souls: Souls, classes: Classes, workshop: Workshop, nesting: Nesting, groups: Groups, journal: Journal, trials: Trials, comfort: Comfort };

export default function SystemsTabs({ s }: { s: S }) {
  const ids: string[] = s.tiles.map((t: any) => t.id);
  const [cur, setCur] = useState(ids[0]);
  useEffect(() => {
    const fromHash = () => { const h = window.location.hash.slice(1); if (ids.includes(h)) setCur(h); };
    fromHash();
    window.addEventListener("hashchange", fromHash);
    return () => window.removeEventListener("hashchange", fromHash);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const pick = (id: string) => { setCur(id); history.replaceState(null, "", `#${id}`); };
  const names: Record<string, string> = Object.fromEntries(s.toc);
  const Panel = PANELS[cur];
  return (
    <div>
      <div role="tablist" aria-label={s.onPage} className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {s.tiles.map((t: any) => {
          const on = t.id === cur;
          return (
            <button key={t.id} id={`tab-${t.id}`} role="tab" type="button" aria-selected={on} aria-controls="sys-panel" onClick={() => pick(t.id)}
              className={`group grid cursor-pointer grid-cols-[48px_minmax(0,1fr)] items-start gap-3 border-2 p-4 text-left transition-[transform,background-color,border-color] duration-200 hover:-translate-y-0.5 ${on ? "border-gold-b bg-gold-b text-ink" : "border-gold bg-ink/80 text-paper hover:border-gold-b"}`}>
              <span className={`grid size-12 place-items-center rounded-full border-2 ${on ? "border-ink text-ink" : "border-gold text-gold-b"}`}><Icon name={t.icon} className="size-7" /></span>
              <span>
                <span className={`block font-display text-2xl leading-tight ${on ? "text-ink" : "text-gold-b"}`}>{names[t.id]}</span>
                <span className={`block text-[14px] leading-snug ${on ? "text-ink/80" : "text-paper-dim"}`}>{t.line}</span>
                <span className={`mt-1 block font-pixel text-xl ${on ? "text-berry" : "text-paper"}`}>{t.stat}</span>
              </span>
            </button>
          );
        })}
      </div>
      <section id="sys-panel" role="tabpanel" aria-labelledby={`tab-${cur}`} className="mt-6 border-2 border-gold bg-lacquer-deep/60 p-[clamp(18px,3vw,36px)] shadow-frame">
        <h2 id={cur} className="m-0 mb-5 font-display text-[clamp(34px,4vw,54px)] leading-none font-normal text-gold-b">{names[cur]}</h2>
        <div key={cur} className="motion-safe:animate-[wp-in_.35s_ease-out]"><Panel s={s} /></div>
      </section>
    </div>
  );
}
