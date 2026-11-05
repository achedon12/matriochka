import Link from "next/link";
import { asset, creature, getData, href, SHARED } from "@/lib/data";
import type { Lang, Mob } from "@/lib/types";
import { Icon, Inlay, Shot } from "../Bits";
import { DollRow, DollWindow } from "../Dolls";
import WorldBestiary, { type BestiaryEntry } from "../WorldBestiary";
import { viewerLabels } from "./CreaturesPages";
import { DollCaption } from "../Islands";
import { Lacquer, Vine } from "../Ornament";
import { Shell } from "../Shell";

function picks(lang: Lang, ids: string[]): BestiaryEntry[] {
  const ui = getData(lang).copy.ui;
  return ids.map((id) => creature(lang, id) as Mob | undefined).filter((c): c is Mob => !!c).map((c) => ({
    id: c.id, name: c.name, tex: c.tex, anims: c.anims, badge: c.worldName, line: c.desc,
    moves: c.moves.map((x) => ({ name: x.name, desc: x.desc })), href: href(lang, `creatures/${c.id}/`),
    stats: [{ l: ui.health, v: c.hp }, { l: ui.damage, v: c.dmg }],
  }));
}

export default function HomePage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const h = d.copy.home;
  const ui = d.copy.ui;
  return (
    <Shell lang={lang} path="">
      {SHARED.hasReel && (
        <section className="reel" aria-label={h.tagline}>
          <video className="reel-v" autoPlay muted loop playsInline preload="auto" poster={asset("reel.jpg")} aria-hidden="true">
            <source src={asset("reel.mp4")} type="video/mp4" />
          </video>
          <div className="reel-in wrap">
            <p className="reel-kicker">{h.tagline}</p>
            <p className="cta">
              <Link className="btn" href={href(lang, "download/")}><Icon name="download" />{h.download}</Link>
              {SHARED.hasTrailer && <a className="btn btn-dark" href="#trailer-h">{h.reelWatch}</a>}
            </p>
          </div>
        </section>
      )}
      <section className="hero" aria-labelledby="hero-h">
        <svg className="hero-side hero-side-l" aria-hidden="true" focusable="false"><rect width="100%" height="100%" fill="url(#vine-red-v)" /></svg>
        <svg className="hero-side hero-side-r" aria-hidden="true" focusable="false"><rect width="100%" height="100%" fill="url(#vine-red-v)" /></svg>
        <div className="wrap hero-in">
          <h1 id="hero-h" className="hero-title">Matriochka</h1>
          <div className="hero-copy">
            <p className="tagline">{h.tagline}</p>
            <p className="hero-p">{h.intro}</p>
            <p className="cta">
              <Link className="btn" href={href(lang, "download/")}><Icon name="download" />{h.download}</Link>
              <Link className="quiet" href={href(lang, "worlds/")}>{ui.worldsLink}</Link>
            </p>
            <p className="facts">{h.facts}</p>
          </div>
          <div className="hero-dolls">
            <DollRow worlds={d.worlds} lang={lang} title={h.dollsTitle} />
            <DollCaption text={h.dollsCaption} />
          </div>
        </div>
      </section>

      {SHARED.hasTrailer && (
        <section className="trailer" aria-labelledby="trailer-h">
          <div className="wrap">
            <h2 id="trailer-h" className="h-quiet">{h.trailerH}</h2>
            <Lacquer className="lacquer-video">
              <video className="trailer-v" controls preload="none" playsInline poster={asset("trailer.jpg")} width={1280} height={720}>
                <source src={asset("trailer.mp4")} type="video/mp4" />
                <a href={asset("trailer.mp4")}>{h.trailerFallback}</a>
              </video>
            </Lacquer>
          </div>
        </section>
      )}

      <Vine className="vine-sep" />
      <section className="strip" aria-labelledby="strip-h">
        <div className="wrap">
          <h2 id="strip-h">{h.stripH}</h2>
          <p className="strip-p">{h.stripP}</p>
          <ol className="strip-row">
            {d.worlds.map((w) => (
              <li key={w.n} style={{ "--wl": w.light } as React.CSSProperties}>
                <Link href={href(lang, `worlds/${w.n}/`)} className="strip-card">
                  <DollWindow world={w} alt={w.name} id={`s${w.n}`} />
                  <span className="strip-n num">{w.n}</span>
                  <span className="strip-name">{w.name}</span>
                  <span className="strip-rule">{w.short}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="bossband" aria-labelledby="bosses-h">
        <div className="wrap">
          <h2 id="bosses-h">{h.bossesH}</h2>
          <p className="strip-p">{h.bossesP}</p>
          <ol className="boss-row">
            {d.bosses.map((b) => (
              <li key={b.id}>
                <Link href={href(lang, `creatures/${b.id}/`)} className="boss-card">
                  {b.shot ? <img src={asset(b.shot)} alt="" loading="lazy" decoding="async" /> : <span className="boss-blank" style={{ backgroundImage: `url(${asset(b.block)})` }} />}
                  <span className="boss-w">{b.worldName}</span>
                  <span className="boss-name">{b.name}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="band" aria-labelledby="life-h">
        <div className="wrap">
          <h2 id="life-h">{h.lifeH}</h2>
          <p className="strip-p">{h.lifeP}</p>
          <WorldBestiary entries={picks(lang, h.lifePicks)} labels={viewerLabels(ui)} sheet={ui.openSheet} movesH={ui.moves} />
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className="band">
        <div className="wrap split">
          <div className="split-h">
            <h2>{h.loopH}</h2>
            <p>{h.loopP}</p>
          </div>
          <ol className="steps">
            {h.loop.map((s: { tex: string; h: string; p: string }, i: number) => (
              <li className="step" key={i}>
                <span className="step-n" aria-hidden="true">{i + 1}</span>
                <div className="step-b">
                  <h3><Inlay src={s.tex} />{s.h}</h3>
                  <p>{s.p}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className="band">
        <div className="wrap split">
          <div className="split-h">
            <h2>{h.worldsH}</h2>
            <p>{h.worldsP}</p>
          </div>
          <ol className="ledger">
            {d.worlds.slice(1).map((w) => (
              <li key={w.n}>
                <Link className="ledger-row" href={href(lang, `worlds/${w.n}/`)}>
                  <Inlay src={`blocks/world_soil_${w.n - 1}.png`} />
                  <span className="lr-n">{w.n}</span>
                  <span className="lr-t"><span className="lr-name">{w.name}</span><span className="lr-line">{w.short}</span></span>
                  <span className="lr-rule" style={{ "--c": w.light } as React.CSSProperties}>{w.rule}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className="band">
        <div className="wrap split">
          <div className="split-h">
            <h2>{h.sysH}</h2>
            <p>{h.sysP}</p>
            <p><Link className="quiet" href={href(lang, "systems/")}>{h.sysLink}</Link></p>
          </div>
          <ul className="sys-list">
            {h.systems.map((s: { tex: string; h: string; p: string }) => (
              <li key={s.h}><h3><Inlay src={s.tex} />{s.h}</h3><p>{s.p}</p></li>
            ))}
          </ul>
        </div>
      </section>

      {h.gallery.length > 0 && (
        <>
          <Vine className="vine-sep" />
          <section className="band">
            <div className="wrap split">
              <div className="split-h"><h2>{h.galleryH}</h2><p>{h.galleryP}</p></div>
              <div className="gallery">
                {h.gallery.map((g: { src: string; caption: string }) => <Shot key={g.src} src={g.src} caption={g.caption} className="shot shot-framed" />)}
              </div>
            </div>
          </section>
        </>
      )}

      <section className="gold-band">
        <Vine kind="gold" />
        <div className="wrap gold-in">
          <h2>{h.ctaH}</h2>
          <p>{h.ctaP}</p>
          <p><Link className="btn btn-dark" href={href(lang, "download/")}><Icon name="download" />{h.ctaBtn}</Link></p>
        </div>
      </section>
    </Shell>
  );
}
