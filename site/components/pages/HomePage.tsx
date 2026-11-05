import Link from "next/link";
import { asset, creature, getData, href, SHARED } from "@/lib/data";
import type { Lang, Mob } from "@/lib/types";
import { Icon, Inlay } from "../Bits";
import { DOLL, Vine } from "../Ornament";
import { Shell } from "../Shell";
import { btn, btnDark, btnGhost, frame, h2, lead, quiet, section, sectionDark, wrap } from "../ui";
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
    <div className="grid items-center gap-[clamp(24px,5vw,72px)] min-[900px]:grid-cols-[5fr_6fr]">
      <svg className="mx-auto h-auto w-full max-w-[360px] min-[900px]:max-w-[520px]" viewBox="0 0 520 520" role="img" aria-label={title}>
        <circle cx="260" cy="260" r={R} fill="none" stroke="rgba(240,201,96,0.34)" strokeWidth="3" />
        <circle className="loop-pulse" cx="260" cy="260" r={R} pathLength="100" fill="none" stroke="#f0c960" strokeWidth="4" strokeLinecap="round" />
        <g transform="translate(222 196) scale(0.76)">
          <use href="#doll" width="100" height="170" style={{ "--db": "#8e2a21", "--ds": "#d9a441", "--do": "#f3e2c2" } as React.CSSProperties} />
        </g>
        {pts.map(([x, y], i) => (
          <g key={i}>
            <circle cx={x} cy={y} r="30" fill="#17100d" stroke="#d9a441" strokeWidth="3" />
            <text className="font-pixel" x={x} y={y + 9} textAnchor="middle" fontSize="28" fill="#f0c960">{i + 1}</text>
          </g>
        ))}
      </svg>
      <ol className="m-0 grid list-none gap-4 p-0">
        {steps.map((s, i) => (
          <li key={i} className="grid grid-cols-[44px_minmax(0,1fr)] items-start gap-3.5">
            <span className="grid size-10 place-items-center rounded-full border-2 border-gold font-pixel text-2xl text-gold-b" aria-hidden="true">{i + 1}</span>
            <div>
              <h3 className="m-0 mb-1 flex items-center font-body text-xl font-bold text-paper"><Inlay src={s.tex} />{s.h}</h3>
              <p className="m-0 text-base text-paper-dim">{s.p}</p>
            </div>
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
      {/* hero: the game named, over its own world */}
      <section className="relative isolate grid h-[720px] min-h-[560px] items-end overflow-hidden bg-black max-md:h-auto md:min-h-[min(calc(100svh-150px),880px)]" aria-labelledby="hero-h">
        {SHARED.hasReel ? (
          <video className="absolute inset-0 -z-20 size-full object-cover motion-reduce:hidden" autoPlay muted loop playsInline preload="auto" poster={asset("reel.jpg")} aria-hidden="true">
            <source src={asset("reel.mp4")} type="video/mp4" />
          </video>
        ) : (
          h.heroImg && <img className="kenburns absolute inset-0 -z-20 size-full object-cover" src={asset(h.heroImg)} alt="" width={1920} height={1080} fetchPriority="high" />
        )}
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(90deg,rgba(14,8,6,.86)_0%,rgba(14,8,6,.55)_38%,transparent_70%),linear-gradient(0deg,rgba(14,8,6,.9)_0%,transparent_45%)]" />
        <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden" aria-hidden="true">
          {Array.from({ length: 22 }, (_, i) => (
            <span key={i} className="mote absolute bottom-0 block rounded-full bg-gold-b shadow-[0_0_8px_#f0c960]"
              style={{ left: `${(i * 37) % 100}%`, width: 2 + (i % 3), height: 2 + (i % 3), "--t": `${8 + (i % 5) * 2.3}s`, "--d": `${-(i * 1.7) % 12}s`, "--dx": `${((i * 53) % 80) - 40}px` } as React.CSSProperties} />
          ))}
        </div>
        <svg className="pointer-events-none absolute -bottom-[6%] right-[max(16px,calc(50vw-620px))] -z-10 h-[112%] w-auto opacity-55 max-md:hidden" viewBox="0 0 100 170" aria-hidden="true">
          <path d={DOLL} fill="none" stroke="#d9a441" strokeWidth="0.7" />
        </svg>
        <div className={`${wrap} pb-[clamp(36px,7vh,80px)]`}>
          <h1 id="hero-h" className="m-0 mb-4 font-display text-[clamp(64px,11vw,176px)] leading-[0.86] font-normal text-gold-b [text-shadow:0_6px_0_#17100d]">Matriochka</h1>
          <p className="m-0 mb-2.5 max-w-[30ch] font-body text-[clamp(21px,2vw,28px)] leading-snug text-paper [text-shadow:0_2px_8px_rgba(0,0,0,.6)]">{h.heroGenre}</p>
          <p className="m-0 mb-6 text-[17px] text-paper-dim"><span className="font-pixel text-xl text-gold-b">{SHARED.version}</span> {h.heroStatus}</p>
          <p className="m-0 flex flex-wrap gap-3 max-md:[&>*]:w-full max-md:[&>*]:justify-center">
            <Link className={btn} href={href(lang, "download/")}><Icon name="download" />{h.download}</Link>
            {SHARED.hasTrailer && <a className={btnGhost} href="#trailer"><Icon name="play" />{h.reelWatch}</a>}
          </p>
        </div>
      </section>

      {/* the ten worlds: pick a doll, its world opens */}
      <section className={section} aria-labelledby="worlds-h">
        <div className={wrap}>
          <h2 id="worlds-h" className={h2}>{h.stripH}</h2>
          <p className={lead}>{h.stripP}</p>
          <WorldPicker worlds={pw} open={h.openWorld} listLabel={h.stripH} pauseLabel={ui.pause} playLabel={ui.play} />
        </div>
      </section>


      {/* fifty creatures, drifting past: hover to stop, click to open one */}
      <section className="marquee-wrap overflow-hidden border-y-2 border-gold bg-ink py-6" aria-label={h.lifeH}>
        {[d.mobs.slice(0, 25), d.mobs.slice(25)].map((row, r) => (
          <div key={r} className="flex w-max">
            <ul className={`marquee m-0 flex list-none gap-3 p-0 pr-3 ${r ? "marquee-rev" : ""}`} style={{ "--t": `${70 + r * 12}s` } as React.CSSProperties}>
              {[...row, ...row].map((m, i) => (
                <li key={`${m.id}-${i}`} aria-hidden={i >= row.length}>
                  <Link href={href(lang, `creatures/${m.id}/`)} tabIndex={i >= row.length ? -1 : undefined}
                    className="group grid w-36 justify-items-center gap-1 rounded-[3px] border border-rule p-2 text-center text-paper no-underline transition-colors hover:border-gold-b hover:text-gold-b"
                    style={{ background: `radial-gradient(circle at 50% 40%, ${m.light}33, ${m.bg} 70%)` }}>
                    <img className="h-24 w-auto transition-transform duration-200 group-hover:scale-110" src={asset(`portraits/${m.id}.png`)} alt="" width={128} height={128} loading="lazy" />
                    <span className="text-[13px] leading-tight">{m.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      {SHARED.hasTrailer && (
        <section className={sectionDark} id="trailer" aria-labelledby="trailer-h">
          <div className={wrap}>
            <h2 id="trailer-h" className={h2}>{h.trailerH}</h2>
            <div className={frame}>
              <video className="block aspect-video h-auto w-full bg-black" controls preload="none" playsInline poster={asset("trailer.jpg")} width={1920} height={1080}>
                <source src={asset("trailer.mp4")} type="video/mp4" />
                <a href={asset("trailer.mp4")}>{h.trailerFallback}</a>
              </video>
            </div>
          </div>
        </section>
      )}

      {/* what you do: four verbs, each with its capture */}
      <section className={section} aria-labelledby="verbs-h">
        <div className={wrap}>
          <h2 id="verbs-h" className={`reveal ${h2}`}>{h.verbsH}</h2>
          <p className={lead}>{h.verbsP}</p>
          <ul className="m-0 grid list-none gap-5 p-0 sm:grid-cols-2 lg:grid-cols-4">
            {h.verbs.map((v: { verb: string; p: string; img: string | null; href: string }) => (
              <li key={v.verb} className="reveal">
                <Link className="group grid gap-2 text-paper no-underline transition-transform duration-200 hover:-translate-y-0.5 hover:text-paper" href={href(lang, v.href)}>
                  <span className="block aspect-[4/3] overflow-hidden border-2 border-gold bg-ink">
                    {v.img && <img className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.03]" src={asset(v.img)} alt="" loading="lazy" decoding="async" width={960} height={720} />}
                  </span>
                  <span className="mt-1.5 font-display text-[clamp(24px,2.2vw,30px)] leading-none text-gold-b">{v.verb}</span>
                  <span className="text-base leading-normal text-paper-dim">{v.p}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className={section} aria-labelledby="loop-h">
        <div className={wrap}>
          <h2 id="loop-h" className={`reveal ${h2}`}>{h.loopH}</h2>
          <p className={lead}>{h.loopP}</p>
          <Loop steps={h.loop} title={h.loopH} />
        </div>
      </section>

      {/* bosses: each one standing in front of its own arena */}
      <section className={sectionDark} aria-labelledby="bosses-h">
        <div className={wrap}>
          <h2 id="bosses-h" className={`reveal ${h2}`}>{h.bossesH}</h2>
          <p className={lead}>{h.bossesP}</p>
          <ol className="m-0 grid list-none grid-cols-[repeat(auto-fill,minmax(min(100%,230px),1fr))] gap-3.5 p-0">
            {d.bosses.map((b) => (
              <li key={b.id} className="reveal">
                <Link href={href(lang, `creatures/${b.id}/`)}
                  className="group relative block aspect-[4/3] overflow-hidden border border-rule bg-black no-underline transition-colors hover:border-gold-b"
                  style={{ background: `radial-gradient(circle at 60% 40%, ${b.light}55 0%, ${b.bg} 55%, #0e0806 100%)` }}>
                  {b.shot && <img className="absolute inset-0 size-full object-cover opacity-45 saturate-[.8]" src={asset(b.shot)} alt="" loading="lazy" decoding="async" width={960} height={720} />}
                  <img className="bob absolute right-0 bottom-8 z-10 h-auto w-[64%] origin-bottom-right drop-shadow-[0_12px_18px_rgba(0,0,0,.7)] transition-transform duration-300 group-hover:scale-105"
                    src={asset(`portraits/${b.id}.png`)} alt="" loading="lazy" decoding="async" width={512} height={512} />
                  <span className="absolute inset-0 z-10 bg-[linear-gradient(180deg,transparent_45%,rgba(0,0,0,.88))]" />
                  <span className="absolute right-3.5 bottom-11 left-3.5 z-20 text-[13px] text-gold-b">{b.worldName}</span>
                  <span className="absolute right-3.5 bottom-3 left-3.5 z-20 font-display text-2xl leading-none text-paper">{b.name}</span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className={section} aria-labelledby="life-h">
        <div className={wrap}>
          <h2 id="life-h" className={`reveal ${h2}`}>{h.lifeH}</h2>
          <p className={lead}>{h.lifeP}</p>
          <WorldBestiary entries={picks(lang, h.lifePicks)} labels={viewerLabels(ui)} sheet={ui.openSheet} movesH={ui.moves} />
          <p className="mt-6"><Link className={quiet} href={href(lang, "bestiary/")}>{h.allCreatures}</Link></p>
        </div>
      </section>

      <Vine className="vine-sep" />
      <section className={section} aria-labelledby="sys-h">
        <div className={`${wrap} grid items-center gap-[clamp(28px,5vw,72px)] min-[900px]:grid-cols-[6fr_5fr]`}>
          <div>
            <h2 id="sys-h" className={`reveal ${h2}`}>{h.sysH}</h2>
            <p className={lead}>{h.sysP}</p>
            <ul className="m-0 mb-5 grid list-none gap-4.5 p-0">
              {h.systems.map((s: { tex: string; h: string; p: string }) => (
                <li key={s.h} className="grid grid-cols-[auto_minmax(0,1fr)] items-start gap-3.5">
                  <Inlay src={s.tex} size={32} />
                  <div><h3 className="m-0 mb-1 font-body text-xl font-bold text-paper">{s.h}</h3><p className="m-0 text-base text-paper-dim">{s.p}</p></div>
                </li>
              ))}
            </ul>
            <p><Link className={quiet} href={href(lang, "systems/")}>{h.sysLink}</Link></p>
          </div>
          {h.sysImg && <div className={frame}><img className="block h-auto w-full [image-rendering:pixelated]" src={asset(h.sysImg)} alt="" loading="lazy" decoding="async" width={960} height={720} /></div>}
        </div>
      </section>

      {/* where to get it, and the questions people ask first */}
      <section className={sectionDark} aria-labelledby="get-h">
        <div className={`${wrap} grid items-start gap-[clamp(28px,5vw,72px)] min-[900px]:grid-cols-2`}>
          <div>
            <h2 id="get-h" className={`reveal ${h2}`}>{h.getH}</h2>
            <p className={lead}>{h.getP}</p>
            <ul className="m-0 grid list-none gap-3 p-0">
              {h.platforms.map((p: { name: string; note: string; href: string | null; icon: string }) => {
                const inner = (
                  <>
                    <Icon name={p.icon} className="size-7 text-gold-b" />
                    <span><strong className="block font-display text-[22px] leading-tight font-normal text-gold-b">{p.name}</strong><small className="text-[15px] text-paper-dim">{p.note}</small></span>
                  </>
                );
                return (
                  <li key={p.name}>
                    {p.href ? (
                      <a className="flex items-center gap-4 border-2 border-gold bg-white/[.02] px-5 py-4.5 text-paper no-underline transition-[transform,background-color] duration-150 hover:-translate-y-0.5 hover:bg-gold-b/10 hover:text-paper" href={p.href}>{inner}</a>
                    ) : (
                      <span className="flex items-center gap-4 border-2 border-dashed border-gold px-5 py-4.5 opacity-70">{inner}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
          <div>
            <h3 className="m-0 mb-3 border-b-2 border-gold pb-2 font-display text-[28px] font-normal text-gold-b">{h.faqH}</h3>
            {h.faq.map((f: { q: string; a: string }) => (
              <details key={f.q} className="group border-b border-rule">
                <summary className="relative cursor-pointer list-none py-3.5 pr-8 font-body text-lg leading-snug font-bold text-paper hover:text-gold-b [&::-webkit-details-marker]:hidden">
                  {f.q}
                  <span className="absolute top-2.5 right-1 font-pixel text-[26px] text-gold-b group-open:hidden" aria-hidden="true">+</span>
                  <span className="absolute top-2.5 right-1 hidden font-pixel text-[26px] text-gold-b group-open:inline" aria-hidden="true">&minus;</span>
                </summary>
                <p className="m-0 mb-4 text-base text-paper-dim">{f.a}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="gold-band">
        <Vine kind="gold" />
        <div className="wrap gold-in">
          <h2>{h.ctaH}</h2>
          <p>{h.ctaP}</p>
          <p><Link className={btnDark} href={href(lang, "download/")}><Icon name="download" />{h.download}</Link></p>
        </div>
      </section>
    </Shell>
  );
}
