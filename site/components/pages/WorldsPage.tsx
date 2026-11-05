import Link from "next/link";
import { creature, getData, href } from "@/lib/data";
import type { Boss, CodexEntry, Lang, Mob, World } from "@/lib/types";
import { Ingredients, Inlay, Recipes, Shot } from "../Bits";
import WorldBestiary, { type BestiaryEntry } from "../WorldBestiary";
import { viewerLabels } from "./CreaturesPages";
import { DollRow, DollWindow } from "../Dolls";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";

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
      <PageHead title={c.h} lead={c.lead} img={c.headImg}>
        <nav className="doll-index" aria-label={c.h}>
          <DollRow worlds={d.worlds} lang={lang} title={c.h} animated={false} className="dolls dolls-index" />
        </nav>
      </PageHead>
      <div className="worlds-seq">
        {d.worlds.map((w, i) => {
          const prev = i ? d.worlds[i - 1].bg : w.bg;
          return (
            <section key={w.n} id={`world-${w.n}`} className={`world${i % 2 ? " world-flip" : ""}`}
              style={{ "--wb": w.bg, "--wp": prev, "--wl": w.light } as React.CSSProperties} aria-labelledby={`wh-${w.n}`}>
              <Vine className="vine-sep" />
              <div className="wrap world-grid">
                <figure className="world-window">
                  <DollWindow world={w} alt={windowAlt(w, lang, c.noShot, c.inGame)} id={`w${w.n}`} />
                  {!w.tall && <figcaption>{c.noShot}</figcaption>}
                </figure>
                <div className="world-copy">
                  <h2 id={`wh-${w.n}`}><span className="w-n">{w.n}</span>{w.name}</h2>
                  <WorldSummary w={w} lang={lang} />
                  {w.n === 0 && w.surface && (
                    <div className="w-block">
                      <h3>{ui.madeAt}</h3>
                      <Recipes recipes={w.surface} />
                    </div>
                  )}
                  {w.n > 0 && <p><Link className="quiet" href={href(lang, `worlds/${w.n}/`)}>{ui.moreAbout}</Link></p>}
                </div>
              </div>
            </section>
          );
        })}
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
