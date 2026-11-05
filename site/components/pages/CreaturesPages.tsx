import Link from "next/link";
import { asset, creature, getData, href } from "@/lib/data";
import type { Boss, Creature, Lang, Mob } from "@/lib/types";
import BestiaryTable from "../BestiaryTable";
import { Inlay } from "../Bits";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";
import { btn, wrap } from "../ui";
import MeetBoss from "../MeetBoss";
import ModelViewer, { type ViewerLabels } from "../viewer/ModelViewer";

export function viewerLabels(ui: Record<string, string>): ViewerLabels {
  return { view3d: ui.view3d, loading3d: ui.loading3d, no3d: ui.no3d, dragHint: ui.dragHint, animations: ui.animations, autoRotate: ui.autoRotate };
}

// ---------------------------------------------------------------- bestiary
export function BestiaryPage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const c = d.copy.bestiary;
  const ui = d.copy.ui;
  const worlds = d.worlds.slice(1).map((w) => ({ n: w.n, name: w.name, rule: w.rule, light: w.light }));
  return (
    <Shell lang={lang} path="bestiary/" section="bestiary">
      <PageHead title={c.h} lead={c.lead} img={c.headImg}><p className="lead-note">{c.nesting}</p></PageHead>
      <Vine className="vine-sep" />
      <div className="wrap">
        <BestiaryTable lang={lang} mobs={d.mobs} worlds={worlds} ui={ui} viewer={viewerLabels(ui)} />
      </div>
      <Vine className="vine-sep" />
      <section className="band" aria-labelledby="peoples-h">
        <div className="wrap split">
          <div className="split-h"><h2 id="peoples-h">{c.peoplesH}</h2><p>{c.peoplesP}</p></div>
          <ul className="peoples">
            {c.peoples.map((p: { id: string; name: string; world: number; worldName: string }) => (
              <li key={p.id}><strong>{p.name}</strong><span>{p.worldName}</span></li>
            ))}
          </ul>
        </div>
      </section>
    </Shell>
  );
}

// ---------------------------------------------------------------- bosses
export function BossesPage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const c = d.copy.bosses;
  const ui = d.copy.ui;
  const vl = viewerLabels(ui);
  return (
    <Shell lang={lang} path="bosses/" section="bosses">
      <PageHead title={c.h} lead={c.lead} img={c.headImg} />
      {/* the eleven, as a row of portraits that jump to each poster */}
      <nav className={`${wrap} pb-4`} aria-label={c.h}>
        <ol className="m-0 grid list-none grid-cols-[repeat(auto-fill,minmax(96px,1fr))] gap-2 p-0">
          {d.bosses.map((b) => (
            <li key={b.id}>
              <a href={`#boss-${b.id}`} className="group grid justify-items-center gap-1 rounded-[3px] border border-rule bg-ink/60 p-2 text-center text-paper no-underline transition-colors hover:border-gold-b hover:text-gold-b">
                <img className="h-20 w-auto drop-shadow-[0_6px_8px_rgba(0,0,0,.6)] transition-transform duration-200 group-hover:-translate-y-1" src={asset(`portraits/${b.id}.png`)} alt="" width={160} height={160} loading="lazy" />
                <span className="font-pixel text-base leading-none" style={{ color: b.light }}>{b.world}</span>
                <span className="text-[13px] leading-tight">{b.name}</span>
              </a>
            </li>
          ))}
        </ol>
      </nav>
      {d.bosses.map((b, i) => (
        <section key={b.id} id={`boss-${b.id}`} aria-labelledby={`bh-${b.id}`} className="relative isolate overflow-hidden border-t-2 border-gold bg-ink">
          {b.shot && <img className="absolute inset-0 -z-20 size-full object-cover opacity-35 saturate-[.8]" src={asset(b.shot)} alt="" loading="lazy" width={960} height={720} />}
          <span className="absolute inset-0 -z-10" style={{ background: `radial-gradient(ellipse at ${i % 2 ? "75%" : "25%"} 45%, ${b.light}44 0%, ${b.bg}dd 45%, #0e0806 100%)` }} />
          <div className={`${wrap} grid items-center gap-[clamp(20px,4vw,56px)] py-[clamp(48px,7vw,96px)] min-[960px]:grid-cols-2`}>
            <div className={`relative ${i % 2 ? "min-[960px]:order-2" : ""}`}>
              <img className="bob mx-auto block h-auto w-full max-w-[540px] drop-shadow-[0_30px_40px_rgba(0,0,0,.75)]" src={asset(`portraits/${b.id}.png`)} alt={b.name} width={512} height={512} loading="lazy" />
            </div>
            <div>
              <p className="m-0 mb-1 font-pixel text-2xl" style={{ color: b.light }}>{b.world ? `${ui.world} ${b.world}` : b.worldName}<span className="font-body text-base text-paper-dim"> {b.world ? b.worldName : ""}</span></p>
              <h2 id={`bh-${b.id}`} className="m-0 mb-4 font-display text-[clamp(40px,5vw,72px)] leading-[0.95] font-normal text-gold-b [text-shadow:0_5px_0_#17100d]">{b.name}</h2>
              <dl className="m-0 mb-6 grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
                {[[ui.solo, b.hp], [ui.heavy, b.dmg], [c.tierCols[1], b.timings[1].v], [c.tierCols[3], b.timings[3].v]].map(([l, v]) => (
                  <div key={l} className="border-t-2 border-gold pt-2"><dt className="text-[13px] text-paper-dim">{l}</dt><dd className="m-0 font-pixel text-[28px] leading-none text-paper">{v}</dd></div>
                ))}
              </dl>
              <ol className="m-0 mb-5 grid list-none gap-2 p-0">
                {b.atks.map((a, k) => (
                  <li key={a.label} className="grid grid-cols-[34px_minmax(0,1fr)] items-baseline gap-3 border-b border-rule py-2">
                    <span className="font-pixel text-xl text-gold-b">{k + 1}</span>
                    <span><strong className="block font-display text-xl font-normal text-paper">{a.name}</strong><small className="text-sm text-paper-dim">{a.label}</small></span>
                  </li>
                ))}
              </ol>
              <p className="m-0 mb-3 text-base text-paper"><strong className="text-gold-b">{ui.phases}.</strong> {b.phases}.</p>
              <p className="m-0 mb-5 flex items-center gap-2 text-base text-paper"><Inlay src={b.coreTex} /><span><strong>{b.drops[0].name}</strong> {c.rewardNote}</span></p>
              <div className="mb-5"><MeetBoss meet={b.meet} title={ui.howMeet} offeringLabel={ui.offering} compact /></div>
              <p className="m-0 flex flex-wrap gap-3">
                <Link className={btn} href={href(lang, `creatures/${b.id}/`)}>{ui.open}</Link>
              </p>
            </div>
          </div>
        </section>
      ))}
      {/* the rules every boss fight follows */}
      <section className={`${wrap} grid gap-10 py-[clamp(48px,7vw,96px)] min-[960px]:grid-cols-[3fr_2fr]`}>
        <div>
          <h2 className="h-plate">{ui.timings}</h2>
          <div className="tbl">
            <table className="stack">
              <thead><tr>{c.tierCols.map((x: string) => <th scope="col" key={x}>{x}</th>)}</tr></thead>
              <tbody>
                {c.tiers.map((r: { tier: string; warn: string; sig: string; opening: string }) => (
                  <tr key={r.tier}><th scope="row">{r.tier}</th><td className="num" data-label={c.tierCols[1]}>{r.warn}</td><td className="num" data-label={c.tierCols[2]}>{r.sig}</td><td className="num" data-label={c.tierCols[3]}>{r.opening}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="small">{c.tierNote}</p>
        </div>
        <div>
          <h2 className="h-plate">{ui.inGroup}</h2>
          <div className="tbl">
            <table>
              <thead><tr><th scope="col">{ui.players}</th><th scope="col">{ui.bossHealth}</th></tr></thead>
              <tbody>{c.mp.map((r: { p: number; mult: string }) => <tr key={r.p}><th scope="row" className="num">{r.p}</th><td className="num">{r.mult}</td></tr>)}</tbody>
            </table>
          </div>
          <p className="small">{c.mpNote}</p>
        </div>
      </section>
    </Shell>
  );
}

// ---------------------------------------------------------------- technical sheet
function Pager({ lang, c, ui }: { lang: Lang; c: Creature; ui: Record<string, string> }) {
  return (
    <nav className="pager" aria-label={ui.sheet}>
      {c.prev ? <Link className="pager-prev" href={href(lang, `creatures/${c.prev}/`)}><small>{ui.prev}</small>{c.prevName}</Link> : <span />}
      {c.next ? <Link className="pager-next" href={href(lang, `creatures/${c.next}/`)}><small>{ui.next}</small>{c.nextName}</Link> : <span />}
    </nav>
  );
}

function Related({ c, ui }: { c: Creature; ui: Record<string, string> }) {
  return (
    <div className="sheet-cols">
      <section>
        <h2 className="h-plate">{ui.quests}</h2>
        {c.quests.length ? (
          <ul className="rel">{c.quests.map((q) => <li key={q.name}><strong>{q.name}</strong><span>{q.desc}</span></li>)}</ul>
        ) : <p className="small">{ui.noQuests}</p>}
      </section>
      <section>
        <h2 className="h-plate">{ui.achievements}</h2>
        {c.ach.length ? (
          <ul className="rel">{c.ach.map((a) => <li key={a.name}><strong>{a.name}</strong><span>{a.desc}</span><em>{a.cat}</em></li>)}</ul>
        ) : <p className="small">{ui.noAch}</p>}
      </section>
    </div>
  );
}

function MobSheet({ lang, m }: { lang: Lang; m: Mob }) {
  const ui = getData(lang).copy.ui;
  return (
    <>
      <dl className="stats stats-wide">
        <div><dt>{ui.health}</dt><dd className="num">{m.hp}</dd></div>
        <div><dt>{ui.damage}</dt><dd className="num">{m.dmg}</dd></div>
        <div><dt>{ui.attackSpeed}</dt><dd><span className="num">{m.speedMult}</span><small>{m.attackEvery ? `${ui.attackEvery} ${m.attackEvery}` : ui.noMelee}</small></dd></div>
        <div><dt>{ui.moveSpeed}</dt><dd className="num">{m.moveSpeed}</dd></div>
      </dl>
      <h2 className="h-plate">{ui.behaviour}</h2>
      <p className="sheet-lead">{m.behaviour}</p>
      <ul className="facts">{m.facts.map((f) => <li key={f}>{f}</li>)}</ul>
      {m.moves.length > 0 && (
        <>
          <h2 className="h-plate">{ui.moves}</h2>
          <p className="small">{ui.movesLead}</p>
          <dl className="moves">
            {m.moves.map((mv) => (
              <div key={mv.key}>
                <dt>{mv.name}<span className="num">{ui.recharge} {mv.cooldown}</span></dt>
                <dd>{mv.desc}</dd>
              </div>
            ))}
          </dl>
        </>
      )}
      <div className="sheet-cols">
        <section>
          <h2 className="h-plate">{ui.drops}</h2>
          <table className="drop-table">
            <thead><tr><th scope="col">{ui.drops}</th><th scope="col">{ui.chance}</th><th scope="col">{ui.count}</th></tr></thead>
            <tbody>
              {m.drops.map((d) => (
                <tr key={d.id + (d.bonus ? "-bonus" : "")}><th scope="row"><Inlay src={d.tex} /><span>{d.name}{d.bonus && <small className="drop-note">{d.bonus}</small>}</span></th><td className="num">{d.chance}</td><td className="num">{d.note}</td></tr>
              ))}
            </tbody>
          </table>
        </section>
        <section>
          <h2 className="h-plate">{ui.spawns}</h2>
          {m.spawn ? (
            <ul className="spawn">
              <li><span className="num">{m.spawn.share}</span> {ui.spawnShare}</li>
              <li><span className="num">{m.spawn.weight}</span> {ui.spawnWeight}</li>
              <li><span className="num">{m.spawn.min === m.spawn.max ? m.spawn.min : `${m.spawn.min}–${m.spawn.max}`}</span> {ui.group}</li>
            </ul>
          ) : null}
          <p><Link href={href(lang, `worlds/${m.world}/`)}>{ui.world} {m.world}, {m.worldName}</Link></p>
        </section>
      </div>
    </>
  );
}

function BossSheet({ lang, b }: { lang: Lang; b: Boss }) {
  const d = getData(lang);
  const ui = d.copy.ui;
  return (
    <>
      <dl className="stats stats-wide">
        <div><dt>{ui.solo}</dt><dd className="num">{b.hp}</dd></div>
        <div><dt>{ui.heavy}</dt><dd className="num">{b.dmg}</dd></div>
        <div><dt>{ui.phases}</dt><dd><small>{b.phases}</small></dd></div>
      </dl>
      <div className="my-8"><MeetBoss meet={b.meet} title={ui.howMeet} offeringLabel={ui.offering} /></div>
      <div className="sheet-cols">
        <section>
          <h2 className="h-plate">{ui.attacks}</h2>
          <ol className="atks">{b.atks.map((a) => <li key={a.label}><span className="atk-l">{a.label}</span>{a.name}</li>)}</ol>
          {b.special.map((s) => <p key={s} className="small">{s}</p>)}
        </section>
        <section>
          <h2 className="h-plate">{ui.timings}</h2>
          <table className="drop-table">
            <tbody>{b.timings.map((t) => <tr key={t.label}><th scope="row">{t.label}</th><td className="num">{t.v}</td></tr>)}</tbody>
          </table>
          <ul className="facts">{b.cooldown.map((x) => <li key={x}>{x}</li>)}</ul>
        </section>
      </div>
      <div className="sheet-cols">
        <section>
          <h2 className="h-plate">{ui.inGroup}</h2>
          <table className="drop-table">
            <thead><tr><th scope="col">{ui.players}</th><th scope="col">{ui.multiplier}</th><th scope="col">{ui.bossHealth}</th></tr></thead>
            <tbody>{b.mp.map((r) => <tr key={r.p}><th scope="row" className="num">{r.p}</th><td className="num">{r.mult}</td><td className="num">{r.hp}</td></tr>)}</tbody>
          </table>
          <p className="small">{d.copy.bosses.mpNote}</p>
        </section>
        <section>
          <h2 className="h-plate">{ui.drops}</h2>
          <table className="drop-table">
            <thead><tr><th scope="col">{ui.drops}</th><th scope="col">{ui.count}</th></tr></thead>
            <tbody>{b.drops.map((x) => <tr key={x.id}><th scope="row"><Inlay src={x.tex} />{x.name}</th><td className="num">{x.note}</td></tr>)}</tbody>
          </table>
          <p className="small">{b.souls}. {ui.arena}</p>
        </section>
      </div>
      <h2 className="h-plate">{ui.unlocks}</h2>
      <ul className="facts">{b.unlocks.map((u) => <li key={u}>{u}</li>)}</ul>
      <details className="spoiler"><summary>{ui.reveal}</summary><p>{b.story}</p></details>
    </>
  );
}

export function CreaturePage({ lang, id }: { lang: Lang; id: string }) {
  const d = getData(lang);
  const ui = d.copy.ui;
  const c = creature(lang, id)!;
  const isBoss = c.kind === "boss";
  const back = isBoss ? href(lang, `bosses/#boss-${c.id}`) : href(lang, `bestiary/#mob-${c.id}`);
  const otherName = lang === "en" ? c.fr : c.en;
  const tags = c.kind === "mob" ? c.tags : [ui.boss];
  return (
    <Shell lang={lang} path={`creatures/${c.id}/`} section={isBoss ? "bosses" : "bestiary"}>
      <div className="sheet" style={{ "--wb": c.bg, "--wl": c.light } as React.CSSProperties}>
        <div className="wrap">
          <p className="crumbs"><Link href={back}>{isBoss ? ui.backBosses : ui.back}</Link></p>
        </div>
        <div className="wrap sheet-head">
          <div className="sheet-title">
            <p className="small">{ui.sheet}</p>
            <h1 style={{ "--longest": Math.max(...c.name.split(" ").map((w) => w.length)) } as React.CSSProperties}>{c.name}</h1>
            <p className="sheet-other" lang={lang === "en" ? "fr" : "en"}>{otherName}</p>
            <p className="sheet-meta">
              <Link href={href(lang, c.world ? `worlds/${c.world}/` : "worlds/#world-0")}>{c.world ? `${ui.world} ${c.world}, ${c.worldName}` : c.worldName}</Link>
              <span className="tags">{tags.map((t) => <span key={t} className="tag">{t}</span>)}</span>
            </p>
            {c.kind === "mob" && <p className="sheet-desc">{c.desc}</p>}
          </div>
          <ModelViewer id={c.id} name={c.name} anims={c.anims} labels={viewerLabels(ui)} tex={c.tex} auto className="viewer-sheet" />
        </div>
        <Vine className="vine-sep" />
        <div className="wrap">
          <Lacquer className="sheet-body">
            {c.kind === "mob" ? <MobSheet lang={lang} m={c} /> : <BossSheet lang={lang} b={c} />}
            <Related c={c} ui={ui} />
          </Lacquer>
          <Pager lang={lang} c={c} ui={ui} />
        </div>
      </div>
    </Shell>
  );
}
