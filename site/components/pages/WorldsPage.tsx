import Link from "next/link";
import { asset, creature, getData, href } from "@/lib/data";
import type { Boss, CodexEntry, Lang, Mob, World } from "@/lib/types";
import { Ingredients, Inlay, Recipes, Shot } from "../Bits";
import WorldBestiary, { type BestiaryEntry } from "../WorldBestiary";
import { viewerLabels } from "./CreaturesPages";
import { DollRow, DollWindow } from "../Dolls";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";
import { btn, btnGhost, wrap } from "../ui";
import DepthRail from "../DepthRail";
import { StageCast, StageCorners, StageGround, StageTitle } from "../WorldStage";
import MeetBoss from "../MeetBoss";

function windowAlt(w: World, lang: Lang, noShot: string, inGame: string) {
  if (!w.tall) return noShot;
  return w.n === 0 ? `${w.name}, ${inGame}` : `${lang === "fr" ? "Monde" : "World"} ${w.n}, ${w.name}, ${inGame}`;
}

/** The rule figures, seed, boss and creatures of a world: shared by the Worlds page and a world's own page. */
export function WorldSummary({ w, lang }: { w: World; lang: Lang }) {
  const { copy } = getData(lang);
  const ui = copy.ui;
  return (
    <>
      <p className="w-meta">{w.rule ? <>{ui.rule}: <strong>{w.rule}</strong>. {ui.stage}: {w.tier}.</> : w.tier}</p>
      <p className="w-long">{w.long}</p>
      {w.nums.length > 0 && (
        <ul className="nums">
          {w.nums.map((x) => <li key={x.l}><span className="nv">{x.v}</span><span className="nl">{x.l}</span></li>)}
        </ul>
      )}
      {w.seed && (
        <div className="w-block">
          <h3><Inlay src={w.seed.tex} size={32} />{w.seed.name}</h3>
          <p className="small">{w.seed.soil} {w.seed.cond}</p>
          <Ingredients inputs={w.seed.inputs} />
        </div>
      )}
      <div className="w-block">
        <h3>{ui.boss}</h3>
        <p>
          <Link className="boss-link" href={href(lang, `creatures/${w.boss.id}/`)}>
            <Inlay src={w.boss.coreTex} size={32} /><span><strong>{w.boss.name}</strong> <span className="num">{w.boss.hp}</span> {ui.health.toLowerCase()}</span>
          </Link>
        </p>
        <p className="small">{w.bossNote}</p>
      </div>
      {w.mobs.length > 0 && (
        <div className="w-block">
          <h3>{ui.creatures}</h3>
          <ul className="inline-list">
            {w.mobs.map((m) => (
              <li key={m.id}><Link href={href(lang, `creatures/${m.id}/`)}>{m.name}</Link>{m.elite && <em> ({lang === "fr" ? "élite" : "elite"})</em>}</li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

export default function WorldsPage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const c = d.copy.worlds;
  const ui = d.copy.ui;
  return (
    <Shell lang={lang} path="worlds/" section="worlds">
      <PageHead title={c.h} lead={c.lead} img={c.headImg} />
      <div className={`${wrap} grid gap-8 py-10 lg:grid-cols-[200px_minmax(0,1fr)]`}>
        <DepthRail worlds={d.worlds} label={c.h} />
        <div className="grid gap-[clamp(28px,4vw,56px)]">
          {d.worlds.map((w) => {
            const sw = { n: w.n, name: w.name, img: w.banner ?? w.wide ?? null, light: w.light, bg: w.bg, boss: w.boss.id, mobs: w.mobs.map((m) => m.id) };
            return (
              <section key={w.n} id={`world-${w.n}`} data-world={w.n} aria-labelledby={`wh-${w.n}`}
                className="relative isolate min-h-[560px] scroll-mt-28 overflow-hidden border-2 border-gold bg-black shadow-frame md:min-h-[620px]">
                <StageGround w={sw} />
                <span className="absolute inset-0 -z-20 bg-[linear-gradient(0deg,rgba(10,6,5,.96)_0%,rgba(10,6,5,.6)_55%,rgba(10,6,5,.25)_100%)] md:bg-[linear-gradient(90deg,rgba(10,6,5,.95)_0%,rgba(10,6,5,.72)_38%,rgba(10,6,5,.1)_72%)]" />
                <StageTitle w={sw} className="top-[6%] text-[clamp(80px,12vw,200px)]" />
                <StageCast w={sw} className="hidden w-[46%] md:block" />
                {/* one gold rule per level of nesting: the deeper the world, the more frames around it */}
                {Array.from({ length: w.n }, (_, k) => (
                  <span key={k} aria-hidden="true" className="pointer-events-none absolute z-0 border border-gold/45" style={{ inset: `${10 + k * 7}px` }} />
                ))}
                <StageCorners />
                <div className="relative z-10 flex h-full min-h-[inherit] flex-col justify-end p-[clamp(22px,4vw,56px)] md:max-w-[50%]">
                  <p className="m-0 font-pixel text-[clamp(72px,8vw,120px)] leading-[0.8]" style={{ color: w.light }}>{String(w.n).padStart(2, "0")}</p>
                  <p className="m-0 mb-1 text-[13px] tracking-[0.18em] text-paper-dim">{w.n === 0 ? ui.surface ?? "" : `${ui.world} ${w.n}`}{w.rule ? `, ${w.tier}` : ""}</p>
                  <h2 id={`wh-${w.n}`} className="m-0 mb-3 font-display text-[clamp(38px,4.6vw,64px)] leading-[0.95] font-normal text-paper [text-shadow:0_4px_0_rgba(0,0,0,.7)]">{w.name}</h2>
                  {w.rule && <p className="m-0 mb-3 self-start rounded-[2px] bg-gold-b px-2.5 py-1 text-sm font-bold text-ink">{ui.rule}: {w.rule}</p>}
                  <p className="m-0 mb-4 font-body text-lg leading-snug font-bold text-gold-b">{w.short}</p>
                  {w.nums.length > 0 && (
                    <ul className="m-0 mb-6 flex list-none flex-wrap gap-x-7 gap-y-3 p-0">
                      {w.nums.map((x) => (
                        <li key={x.l} className="max-w-[190px] border-t-2 border-gold pt-1.5"><span className="block font-pixel text-[30px] leading-none text-paper">{x.v}</span><span className="text-[13px] leading-snug text-paper-dim">{x.l}</span></li>
                      ))}
                    </ul>
                  )}
                  <p className="m-0 flex flex-wrap gap-3">
                    <Link className={btn} href={href(lang, `worlds/${w.n}/`)}>{w.n === 0 ? ui.moreAbout : `${ui.explore} ${w.name}`}</Link>
                    <Link className={btnGhost} href={href(lang, `creatures/${w.boss.id}/`)}>{w.boss.name}</Link>
                  </p>
                </div>
              </section>
            );
          })}
        </div>
      </div>
    </Shell>
  );
}

function CodexCard({ e, c }: { e: CodexEntry; c: Record<string, string> }) {
  return (
    <li className="cx-card">
      <div className="cx-head">
        <Inlay src={e.tex} size={32} />
        <div><h4>{e.name}{e.count > 1 && <span className="num"> ×{e.count}</span>}</h4>{e.rarity && <span className={`cx-rar cx-${e.rarity.toLowerCase()}`}>{e.rarity}</span>}</div>
      </div>
      {e.effect && <p className="cx-eff">{e.effect}</p>}
      {e.station && e.inputs.length > 0 && (
        <div className="cx-how"><p className="small">{c.cMade} <strong>{e.station}</strong></p><Ingredients inputs={e.inputs} /></div>
      )}
      {e.drops.length > 0 && <p className="small cx-how">{c.cFound} {e.drops.join(", ")}</p>}
      {e.yields && <p className="small cx-how">{c.cGives} <strong>{e.yields}</strong></p>}
    </li>
  );
}

const ROLE_TONE: Record<string, string> = { combat: "bg-berry text-paper", exploration: "bg-gold-b text-ink", story: "bg-paper text-ink", utility: "bg-[#4a7a3a] text-paper", secret: "bg-ink text-gold-b ring-1 ring-gold" };

function Sites({ w, lang }: { w: World; lang: Lang }) {
  const c = getData(lang).copy.worlds;
  if (!w.sites?.length) return null;
  return (
    <section className={`${wrap} py-12`} aria-labelledby="sites-h">
      <h2 id="sites-h" className="reveal m-0 mb-3 font-display text-[clamp(34px,4.6vw,60px)] leading-none font-normal text-gold-b">{c.sitesH}</h2>
      <p className="m-0 mb-8 max-w-[62ch] text-paper-dim">{c.sitesP}</p>
      <ul className="m-0 grid list-none grid-cols-[repeat(auto-fill,minmax(min(100%,300px),1fr))] gap-4 p-0">
        {w.sites.map((st) => (
          <li key={st.id} className="reveal flex flex-col overflow-hidden border border-rule bg-ink/70">
            <div className="relative aspect-[16/9] bg-black">
              {st.img ? <img className="size-full object-cover" src={asset(st.img)} alt="" loading="lazy" width={800} height={450} />
                : <span className="absolute inset-0 bg-[length:48px] opacity-40 [image-rendering:pixelated]" style={{ backgroundImage: `url(${asset(w.block)})` }} />}
              <span className={`absolute top-2 left-2 rounded-[2px] px-2 py-0.5 text-[12px] font-bold ${ROLE_TONE[st.roleKey] ?? ""}`}>{st.role}</span>
            </div>
            <div className="grid gap-2 p-4">
              <h3 className="m-0 font-display text-[22px] leading-tight font-normal text-gold-b">{st.name}</h3>
              <p className="m-0 text-[13px] text-paper-dim">{st.size}{st.rarity ? `, ${st.rarity.toLowerCase()}` : ""}</p>
              <p className="m-0 text-[15px] leading-snug text-paper">{st.desc}</p>
              <p className="m-0 border-t border-dotted border-rule pt-2 text-[14px] leading-snug text-paper-dim">{st.inside}</p>
            </div>
          </li>
        ))}
      </ul>
      {w.loot && (
        <>
          <h3 className="mt-12 mb-4 border-b-2 border-gold pb-2 font-display text-[28px] font-normal text-gold-b">{c.lootH}</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {w.loot.map((t) => (
              <div key={t.tier} className="border-2 border-gold bg-ink/80 p-4">
                <h4 className="m-0 font-display text-xl font-normal text-paper">{t.tier}</h4>
                <p className="m-0 mb-3 text-[13px] text-paper-dim">{t.note}</p>
                <ul className="m-0 flex list-none flex-wrap gap-1.5 p-0">
                  {t.items.map((it) => (
                    <li key={it.id} className="flex items-center gap-1.5 rounded-[2px] bg-black/30 py-1 pr-2 pl-1 text-[13px] text-paper"><Inlay src={it.tex} size={20} />{it.name}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function Codex({ w, lang }: { w: World; lang: Lang }) {
  const c = getData(lang).copy.worlds;
  const x = w.codex;
  return (
    <section className="wrap codex" aria-labelledby="cx-h">
      <h2 id="cx-h">{c.codexH}</h2>
      <p className="world-life-p">{c.codexP}</p>
      {x.items.length > 0 && (<><h3 className="h-plate">{c.cItems}</h3><ul className="cx-grid">{x.items.map((e) => <CodexCard key={e.id} e={e} c={c} />)}</ul></>)}
      {x.blocks.length > 0 && (<><h3 className="h-plate">{c.cBlocks}</h3><ul className="cx-grid">{x.blocks.map((e) => <CodexCard key={e.id} e={e} c={c} />)}</ul></>)}
      <div className="cx-cols">
        {x.quests.length > 0 && (
          <div><h3 className="h-plate">{c.cQuests}</h3><ul className="cx-list">{x.quests.map((q) => <li key={q.name}><strong>{q.name}</strong><span>{q.desc}</span></li>)}</ul></div>
        )}
        {x.ach.length > 0 && (
          <div><h3 className="h-plate">{c.cAch}</h3><ul className="cx-list">{x.ach.map((a) => (
            <li key={a.name}><strong>{a.name}</strong><span>{a.desc}</span><small className="cx-cat">{a.cat}{a.hidden ? `, ${c.cHidden.toLowerCase()}` : ""}</small></li>
          ))}</ul></div>
        )}
      </div>
    </section>
  );
}

function bestiary(lang: Lang, w: World): BestiaryEntry[] {
  const ui = getData(lang).copy.ui;
  const out: BestiaryEntry[] = [];
  for (const m of w.mobs) {
    const c = creature(lang, m.id) as Mob | undefined;
    if (!c) continue;
    out.push({ id: c.id, name: c.name, tex: c.tex, anims: c.anims, badge: c.elite ? (lang === "fr" ? "élite" : "elite") : null, line: c.desc,
      moves: c.moves.map((x) => ({ name: x.name, desc: x.desc })), href: href(lang, `creatures/${c.id}/`),
      stats: [{ l: ui.health, v: c.hp }, { l: ui.damage, v: c.dmg }] });
  }
  const b = creature(lang, w.boss.id) as Boss | undefined;
  if (b) out.push({ id: b.id, name: b.name, tex: b.tex, anims: b.anims, badge: ui.boss, line: w.bossNote,
    moves: b.atks.map((x) => ({ name: x.name, desc: x.label })), href: href(lang, `creatures/${b.id}/`),
    stats: [{ l: ui.health, v: b.hp }, { l: ui.damage, v: b.dmg }] });
  return out;
}

export function WorldPage({ lang, n }: { lang: Lang; n: number }) {
  const d = getData(lang);
  const c = d.copy.worlds;
  const ui = d.copy.ui;
  const w = d.worlds[n];
  const prev = n > 0 ? d.worlds[n - 1] : null;
  const next = n < 10 ? d.worlds[n + 1] : null;
  const label = (x: World) => `${ui.world} ${x.n}, ${x.name}`;
  return (
    <Shell lang={lang} path={`worlds/${n}/`} section="worlds">
      <div className="world world-single" style={{ "--wb": w.bg, "--wp": w.bg, "--wl": w.light } as React.CSSProperties}>
        <div className="wrap world-grid">
          <figure className="world-window">
            <DollWindow world={w} alt={windowAlt(w, lang, c.noShot, c.inGame)} id={`w${w.n}`} />
            {!w.tall && <figcaption>{c.noShot}</figcaption>}
          </figure>
          <div className="world-copy">
            <p className="crumbs"><Link href={href(lang, "worlds/")}>{ui.backWorlds}</Link></p>
            <h1><span className="w-n">{w.n}</span>{w.name}</h1>
            <WorldSummary w={w} lang={lang} />
          </div>
        </div>
        {w.gallery && w.gallery.length > 0 && (
          <div className="wrap world-reel">
            {w.gallery.map((g) => <Shot key={g.src} src={g.src} caption={g.caption} className="shot shot-framed" />)}
          </div>
        )}
        <Vine className="vine-sep" />
        <section className="wrap world-life" aria-labelledby="wl-h">
          <h2 id="wl-h">{c.lifeH}</h2>
          <p className="world-life-p">{c.lifeP}</p>
          <WorldBestiary entries={bestiary(lang, w)} labels={viewerLabels(ui)} sheet={ui.openSheet} movesH={ui.moves} />
        </section>
        {(() => { const b = creature(lang, w.boss.id) as Boss | undefined; return b ? (
          <section className={`${wrap} pb-10`}><MeetBoss meet={b.meet} title={`${ui.howMeet}: ${b.name}`} offeringLabel={ui.offering} /></section>
        ) : null; })()}
        <Vine className="vine-sep" />
        <Sites w={w} lang={lang} />
        <Vine className="vine-sep" />
        <Codex w={w} lang={lang} />
        <Vine className="vine-sep" />
        <div className="wrap">
          {w.station && (
            <Lacquer className="world-more">
              <section className="col">
                <h2 className="h-plate"><Inlay src={w.station.tex} />{w.station.name}</h2>
                <p>{w.station.note}</p>
                {w.station.make.length > 0 && <div className="st-make"><p className="small">{ui.builtFrom}</p><Ingredients inputs={w.station.make} /></div>}
                <Recipes recipes={w.station.recipes} />
              </section>
              <section className="col">
                <h2 className="h-plate">{ui.carry}</h2>
                <ul className="items">
                  {w.items.map((it) => (
                    <li key={it.id}><Inlay src={it.tex} /><span><strong>{it.name}</strong>{it.effect && <small>{it.effect}</small>}</span></li>
                  ))}
                </ul>
                {w.armor && (
                  <div className="armor">
                    <p className="armor-pieces">{w.armor.pieces.map((p) => <Inlay key={p.name} src={p.tex} alt={p.name} />)}</p>
                    <p><strong>{ui.armour}</strong> {w.armor.text}</p>
                  </div>
                )}
              </section>
              <section className="col">
                <h2 className="h-plate">{ui.structures}</h2>
                {w.structures.map((s) => (
                  <div className="srole" key={s.role}><h3>{s.role}</h3><p>{s.names.join(", ")}</p></div>
                ))}
              </section>
            </Lacquer>
          )}
          <nav className="pager" aria-label={ui.worldsLink}>
            {prev ? <Link className="pager-prev" href={href(lang, `worlds/${prev.n}/`)}><small>{ui.prev}</small>{label(prev)}</Link> : <span />}
            {next ? <Link className="pager-next" href={href(lang, `worlds/${next.n}/`)}><small>{ui.next}</small>{label(next)}</Link> : <span />}
          </nav>
        </div>
      </div>
    </Shell>
  );
}
