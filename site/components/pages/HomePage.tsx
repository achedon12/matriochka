import Link from "next/link";
import { asset, creature, getData, href, SHARED } from "@/lib/data";
import type { Lang, Mob } from "@/lib/types";
import { Icon, Inlay } from "../Bits";
import { DOLL, Vine } from "../Ornament";
import { Shell } from "../Shell";
import WorldBestiary, { type BestiaryEntry } from "../WorldBestiary";
import WorldPicker, { type PickerWorld } from "../WorldPicker";
import { viewerLabels } from "./CreaturesPages";

function picks(lang: Lang, ids: string[]): BestiaryEntry[] {
  const ui = getData(lang).copy.ui;
  return ids.map((id) => creature(lang, id) as Mob | undefined).filter((c): c is Mob => !!c).map((c) => ({
    id: c.id, name: c.name, tex: c.tex, anims: c.anims, badge: c.worldName, line: c.desc,
    moves: c.moves.map((x) => ({ name: x.name, desc: x.desc })), href: href(lang, `creatures/${c.id}/`),
    stats: [{ l: ui.health, v: c.hp }, { l: ui.damage, v: c.dmg }],
  }));
}

/** The loop of the mod drawn as a ring of steps, a pulse running from one to the next. */
function Loop({ steps, title }: { steps: { tex: string; h: string; p: string }[]; title: string }) {
  const n = steps.length;
  const R = 200;
  const pts = steps.map((_, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [260 + R * Math.cos(a), 260 + R * Math.sin(a)];
  });
  return (
    <div className="loop">
      <svg className="loop-ring" viewBox="0 0 520 520" role="img" aria-label={title}>
        <circle className="loop-track" cx="260" cy="260" r={R} />
        <circle className="loop-pulse" cx="260" cy="260" r={R} pathLength="100" />
        <g transform="translate(222 196) scale(0.76)"><use href="#doll" width="100" height="170" className="loop-doll" /></g>
        {pts.map(([x, y], i) => (
          <g key={i}>
            <circle className="loop-node" cx={x} cy={y} r="30" />
            <text className="loop-n" x={x} y={y + 9} textAnchor="middle">{i + 1}</text>
          </g>
        ))}
      </svg>
      <ol className="loop-steps">
        {steps.map((s, i) => (
          <li key={i}>
            <span className="loop-k num" aria-hidden="true">{i + 1}</span>
            <div><h3><Inlay src={s.tex} />{s.h}</h3><p>{s.p}</p></div>
          </li>
        ))}
      </ol>
    </div>
  );
}

export default function HomePage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const h = d.copy.home;
  const ui = d.copy.ui;
  const pw: PickerWorld[] = d.worlds.map((w) => ({
    n: w.n, name: w.name, short: w.short, long: w.long, img: w.banner ?? w.wide ?? w.tall, tex: w.block, doll: w.doll, light: w.light,
    href: href(lang, `worlds/${w.n}/`), label: w.n === 0 ? h.surfaceLabel : `${ui.world} ${w.n}`,
  }));
  return (
    <Shell lang={lang} path="">
      <section className="hero2" aria-labelledby="hero-h">
        {SHARED.hasReel ? (
          <video className="hero2-v" autoPlay muted loop playsInline preload="auto" poster={asset("reel.jpg")} aria-hidden="true">
            <source src={asset("reel.mp4")} type="video/mp4" />
          </video>
        ) : (
          h.heroImg && <img className="hero2-v" src={asset(h.heroImg)} alt="" width={1920} height={1080} fetchPriority="high" />
        )}
        <div className="hero2-in wrap">
          <h1 id="hero-h" className="hero2-title">Matriochka</h1>
          <p className="hero2-genre">{h.heroGenre}</p>
          <p className="hero2-status"><span className="num">{SHARED.version}</span> {h.heroStatus}</p>
          <p className="hero2-cta">
            <Link className="btn" href={href(lang, "download/")}><Icon name="download" />{h.download}</Link>
            {SHARED.hasTrailer && <a className="btn btn-ghost" href="#trailer"><Icon name="play" />{h.reelWatch}</a>}
          </p>
        </div>
        <svg className="hero2-doll" viewBox="0 0 100 170" aria-hidden="true"><path d={DOLL} /></svg>
      </section>

      <section className="sec sec-worlds" aria-labelledby="worlds-h">
        <div className="wrap">
          <h2 id="worlds-h">{h.stripH}</h2>
          <p className="sec-p">{h.stripP}</p>
          <WorldPicker worlds={pw} open={h.openWorld} listLabel={h.stripH} />
        </div>
      </section>

      {SHARED.hasTrailer && (
        <section className="sec sec-dark" id="trailer" aria-labelledby="trailer-h">
          <div className="wrap">
            <h2 id="trailer-h">{h.trailerH}</h2>
            <div className="frame">
              <video className="trailer-v" controls preload="none" playsInline poster={asset("trailer.jpg")} width={1920} height={1080}>
                <source src={asset("trailer.mp4")} type="video/mp4" />
                <a href={asset("trailer.mp4")}>{h.trailerFallback}</a>
              </video>
            </div>
          </div>
        </section>
      )}

      <section className="sec" aria-labelledby="verbs-h">
        <div className="wrap">
          <h2 id="verbs-h">{h.verbsH}</h2>
          <p className="sec-p">{h.verbsP}</p>
          <ul className="verbs">
            {h.verbs.map((v: { verb: string; p: string; img: string | null; href: string }) => (
              <li key={v.verb}>
                <Link className="verb" href={href(lang, v.href)}>
                  <span className="verb-img">{v.img && <img src={asset(v.img)} alt="" loading="lazy" decoding="async" width={960} height={540} />}</span>
                  <span className="verb-v">{v.verb}</span>
                  <span className="verb-p">{v.p}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className="sec" aria-labelledby="loop-h">
        <div className="wrap">
          <h2 id="loop-h">{h.loopH}</h2>
          <p className="sec-p">{h.loopP}</p>
          <Loop steps={h.loop} title={h.loopH} />
        </div>
      </section>

      <section className="sec sec-dark" aria-labelledby="bosses-h">
        <div className="wrap">
          <h2 id="bosses-h">{h.bossesH}</h2>
          <p className="sec-p">{h.bossesP}</p>
          <ol className="boss-row">
            {d.bosses.map((b) => (
              <li key={b.id}>
                <Link href={href(lang, `creatures/${b.id}/`)} className="boss-card">
                  {b.shot ? <img src={asset(b.shot)} alt="" loading="lazy" decoding="async" width={960} height={720} /> : <span className="boss-blank" style={{ backgroundImage: `url(${asset(b.block)})` }} />}
                  <img className="boss-portrait" src={asset(`portraits/${b.id}.png`)} alt="" loading="lazy" decoding="async" width={512} height={512} />
                  <span className="boss-w">{b.worldName}</span>
                  <span className="boss-name">{b.name}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="sec" aria-labelledby="life-h">
        <div className="wrap">
          <h2 id="life-h">{h.lifeH}</h2>
          <p className="sec-p">{h.lifeP}</p>
          <WorldBestiary entries={picks(lang, h.lifePicks)} labels={viewerLabels(ui)} sheet={ui.openSheet} movesH={ui.moves} />
          <p className="sec-more"><Link className="quiet" href={href(lang, "bestiary/")}>{h.allCreatures}</Link></p>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className="sec" aria-labelledby="sys-h">
        <div className="wrap sys2">
          <div>
            <h2 id="sys-h">{h.sysH}</h2>
            <p className="sec-p">{h.sysP}</p>
            <ul className="sys2-list">
              {h.systems.map((s: { tex: string; h: string; p: string }) => (
                <li key={s.h}><Inlay src={s.tex} size={32} /><div><h3>{s.h}</h3><p>{s.p}</p></div></li>
              ))}
            </ul>
            <p><Link className="quiet" href={href(lang, "systems/")}>{h.sysLink}</Link></p>
          </div>
          {h.sysImg && <div className="frame sys2-img"><img src={asset(h.sysImg)} alt="" loading="lazy" decoding="async" width={960} height={720} /></div>}
        </div>
      </section>

      <section className="sec sec-dark" aria-labelledby="get-h">
        <div className="wrap get">
          <div>
            <h2 id="get-h">{h.getH}</h2>
            <p className="sec-p">{h.getP}</p>
            <ul className="get-list">
              {h.platforms.map((p: { name: string; note: string; href: string | null; icon: string }) => (
                <li key={p.name}>
                  {p.href ? (
                    <a className="get-card" href={p.href}><Icon name={p.icon} /><span><strong>{p.name}</strong><small>{p.note}</small></span></a>
                  ) : (
                    <span className="get-card get-soon"><Icon name={p.icon} /><span><strong>{p.name}</strong><small>{p.note}</small></span></span>
                  )}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="h-plate">{h.faqH}</h3>
            <div className="faq">
              {h.faq.map((f: { q: string; a: string }) => (
                <details key={f.q}><summary>{f.q}</summary><p>{f.a}</p></details>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="gold-band">
        <Vine kind="gold" />
        <div className="wrap gold-in">
          <h2>{h.ctaH}</h2>
          <p>{h.ctaP}</p>
          <p><Link className="btn btn-dark" href={href(lang, "download/")}><Icon name="download" />{h.download}</Link></p>
        </div>
      </section>
    </Shell>
  );
}
