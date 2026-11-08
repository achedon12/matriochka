import Link from "./PageLink";
import type { CSSProperties, ReactNode } from "react";
import { asset, getData, href, otherLang, SHARED } from "@/lib/data";
import { BASE, VERSION_KEY } from "@/lib/config";
import { isBoss, LATEST, OLDER, pageIn, VERSIONS } from "@/lib/versions";
import type { Lang } from "@/lib/types";
import { Icon } from "./Bits";
import { Vine } from "./Ornament";
import Sprite from "./Sprite";
import { StickyHeader } from "./Islands";
import VersionPicker, { LatestLink, type PickerVersion } from "./VersionPicker";

/** Where the version picker leads from a page: the same page in that version, or its section when the page is
 * not in it (a creature added later), or the version's home. */
function target(path: string, v: string): string {
  if (pageIn(path, v) || (v === LATEST && path === "download/")) return path;
  const c = path.match(/^creatures\/([\w-]+)\//);
  if (c) return isBoss(c[1]) ? "bosses/" : "bestiary/";
  if (path.startsWith("worlds/")) return "worlds/";
  return "";
}

/** On the latest pages, before anything is drawn: a reader who picked an older version is taken back to it. */
function returnScript(lang: Lang, path: string): string {
  const to: Record<string, string> = {};
  for (const v of OLDER) to[v] = BASE + href(lang, target(path, v), v);
  return `try{var v=localStorage.getItem(${JSON.stringify(VERSION_KEY)}),t=${JSON.stringify(to)};if(v&&t[v])location.replace(t[v]+location.hash)}catch(e){}`;
}

/** Header, ornament and footer around every page. `path` is the page path without language or version, e.g.
 * "worlds/3/"; `v` is the version shown when it is not the latest. */
export function Shell({ lang, path, section, v, children }: { lang: Lang; path: string; section?: string; v?: string; children: ReactNode }) {
  const { copy } = getData(lang, v);
  const ui = copy.ui;
  const vl = copy.versions;
  const other = otherLang(lang);
  const shown = v ?? LATEST;
  const picker: PickerVersion[] = VERSIONS.map((x) => ({ v: x.v, mc: x.mc, date: x.date, latest: x.latest, href: href(lang, target(path, x.v), x.v) }));
  // the nav nests: four painted dolls, each a size smaller, in the colours of the worlds they lead to
  const NAV = [
    { p: "worlds", h: 34, c: ["#a8231a", "#d9a441", "#f3e2c2"] },
    { p: "bestiary", h: 31, c: ["#3f6b2f", "#c9d36a", "#f3e2c2"] },
    { p: "bosses", h: 28, c: ["#17100d", "#d9a441", "#a8231a"] },
    { p: "items", h: 26, c: ["#6a3a1c", "#e0b050", "#f3e2c2"] },
    { p: "systems", h: 24, c: ["#2f4f7a", "#9fc3e8", "#f3e2c2"] },
  ] as const;
  const doll = (c: readonly string[], h: number, open: boolean) => (
    <svg viewBox="-4 -30 108 204" aria-hidden="true" style={{ height: `calc(${h + 10}px * var(--navdoll, 1))`, width: "auto" }}
      className="overflow-visible drop-shadow-[0_3px_0_rgba(0,0,0,.45)]">
      <g className="transition-transform duration-300 motion-reduce:transition-none group-hover:-translate-y-[6px] group-hover:-rotate-3"
        style={{ transformOrigin: "50px 98px", transform: open ? "translateY(-24px) rotate(-7deg)" : undefined }}>
        <use href="#doll" width="100" height="170" clipPath="url(#doll-top)" style={{ "--db": c[0], "--ds": c[1], "--do": c[2] } as CSSProperties} />
      </g>
      {open && <ellipse cx="50" cy="99" rx="40" ry="5" fill="#0a0605" />}
      <use href="#doll" width="100" height="170" clipPath="url(#doll-bottom)" style={{ "--db": c[0], "--ds": c[1], "--do": c[2] } as CSSProperties} />
    </svg>
  );
  return (
    <>
      {!v && OLDER.length > 0 && path !== "download/" && <script dangerouslySetInnerHTML={{ __html: returnScript(lang, path) }} />}
      <Sprite />
      <a className="skip" href="#main">{ui.skip}</a>
      <StickyHeader />
      <header className="sticky top-0 z-30 border-b-2 border-gold bg-lacquer-deep bg-[radial-gradient(120%_160%_at_50%_-40%,#7a2a22_0%,#4a1714_55%,#2a0d0b_100%)] shadow-[0_6px_0_rgba(0,0,0,.35)]">
        {/* a thin gold bead along the top edge, the rim of a lacquered box */}
        <span aria-hidden="true" className="absolute inset-x-0 top-0 h-[5px] bg-[radial-gradient(circle,#f0c960_1.3px,transparent_1.7px)] bg-[length:12px_5px] opacity-80" />
        <div className="wrap flex items-end gap-x-5 gap-y-2 pt-3 pb-2 transition-[padding] duration-200 max-[1060px]:flex-wrap max-[1060px]:justify-between [.is-scrolled_&]:pt-1.5 [.is-scrolled_&]:pb-1">
          <Link href={href(lang, "", v)} aria-current={path === "" ? "page" : undefined}
            className="group flex shrink-0 items-center gap-3 self-center text-gold-b no-underline hover:text-[#ffdd80]">
            <span className="grid size-[58px] place-items-center rounded-full bg-ink shadow-[0_0_0_2px_#d9a441,0_0_0_5px_#17100d,0_0_0_6px_rgba(240,201,96,.35)] transition-[width,height] duration-200 [.is-scrolled_&]:size-[42px]">
              <img src={asset("logo-128.webp")} width="50" height="50" alt="" className="size-[84%]" />
            </span>
            <span className="font-display text-[clamp(20px,2.2vw,28px)] leading-none tracking-[0.06em] [text-shadow:0_2px_0_rgba(0,0,0,.6)] max-[420px]:hidden">Matriochka</span>
          </Link>
          <nav aria-label={ui.main} className="mx-auto max-[1060px]:order-3 max-[1060px]:w-full max-[480px]:[--navdoll:0.8]">
            <ul className="m-0 flex list-none items-end gap-[clamp(10px,2.4vw,30px)] p-0 max-[1060px]:justify-center max-[480px]:gap-1.5">
              {NAV.map(({ p, h, c }) => {
                const here = section === p;
                return (
                  <li key={p}>
                    <Link href={href(lang, `${p}/`, v)} aria-current={here ? (path === `${p}/` ? "page" : "true") : undefined}
                      className={`group flex items-end gap-2 rounded-sm px-1 pb-1 font-body text-[17px] font-bold no-underline max-[480px]:flex-col max-[480px]:items-center max-[480px]:gap-0.5 max-[480px]:text-[13px] ${here ? "text-gold-b" : "text-paper hover:text-gold-b"}`}>
                      {doll(c, h, here)}
                      <span className={`pb-[3px] ${here ? "border-b-2 border-gold-b" : "border-b-2 border-transparent group-hover:border-gold/60"}`}>{copy.nav[p]}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
          <div className="flex shrink-0 items-center gap-3 self-center">
            {VERSIONS.length > 1 && (
              <VersionPicker current={shown} versions={picker} labels={{ label: vl.label, pick: vl.pick, latest: vl.latest, mc: vl.mc }}
                changes={{ href: href(lang, "changes/", v), label: vl.changesNav.replace("{v}", shown) }} />
            )}
            <a href={asset(href(other, path, path === "download/" ? null : v).slice(1))} hrefLang={other} lang={other}
              className="rounded-sm border border-gold/50 px-2 py-1 text-[14px] text-paper-dim no-underline hover:border-gold-b hover:text-gold-b">{ui.other}</a>
            <a href={SHARED.repo} aria-label={ui.github} className="inline-flex text-paper-dim hover:text-gold-b"><Icon name="github" /></a>
            <Link href={href(lang, "download/")} aria-current={section === "download" ? "page" : undefined}
              className="inline-flex items-center gap-2 rounded-t-[14px] rounded-b-[4px] border-2 border-[#ffdd80] bg-[linear-gradient(180deg,#f0c960,#d9a441)] px-4 py-2 font-body text-[16px] font-bold text-ink no-underline shadow-[0_3px_0_#7a5212] transition-transform duration-150 hover:-translate-y-0.5 active:translate-y-px motion-reduce:transition-none">
              <Icon name="download" />
              <span>{copy.nav.download}</span>
            </Link>
          </div>
        </div>
      </header>
      {v && (
        <div className="vp-older">
          <p className="wrap">
            <span>{vl.older} <strong className="font-pixel text-[21px] font-normal leading-none text-gold-b">{v}</strong></span>
            <LatestLink href={href(lang, target(path, LATEST))}>{vl.toLatest} {LATEST}</LatestLink>
          </p>
        </div>
      )}
      <main id="main">{children}</main>
      <footer className="foot">
        <Vine kind="black" />
        <div className="wrap foot-in">
          <div className="foot-brand">
            <img src={asset("logo-128.webp")} width="64" height="64" alt="" />
            <div>
              <p className="foot-name">Matriochka</p>
              <p>{ui.footer}</p>
            </div>
          </div>
          <ul className="foot-links">
            <li><a href={SHARED.releases}><Icon name="download" />{ui.releases}</a></li>
            <li><a href={SHARED.wiki}><Icon name="book-open" />{ui.wiki}</a></li>
            <li><a href={SHARED.repo}><Icon name="github" />GitHub</a></li>
            <li><a href={`${SHARED.repo}/issues`}><Icon name="bug" />{ui.bug}</a></li>
          </ul>
          <p className="foot-note">{ui.notOfficial}</p>
        </div>
      </footer>
    </>
  );
}

export function PageHead({ title, lead, img, children }: { title: string; lead: string; img?: string | null; children?: ReactNode }) {
  return (
    <section className={`relative isolate overflow-hidden ${img ? "bg-black pt-[clamp(110px,15vw,210px)] pb-[clamp(36px,5vw,60px)]" : "pt-10 pb-9"}`}>
      {img && (
        <>
          <img className="kenburns absolute inset-0 -z-20 !h-full w-full object-cover" src={asset(img)} alt="" width={1920} height={823} fetchPriority="high" />
          <span className="absolute inset-0 -z-10 bg-[linear-gradient(0deg,rgba(14,8,6,.96)_0%,rgba(14,8,6,.6)_50%,rgba(14,8,6,.15)_100%)]" />
        </>
      )}
      <div className="mx-auto w-full max-w-[1240px] px-4 md:px-8">
        <h1 className="m-0 mb-4 font-display text-[clamp(46px,9vw,124px)] leading-[0.9] font-normal text-gold-b [text-shadow:0_5px_0_#17100d]">{title}</h1>
        <p className="m-0 max-w-[62ch] text-[clamp(18px,1.6vw,22px)] leading-relaxed text-paper [text-shadow:0_2px_8px_rgba(0,0,0,.6)]">{lead}</p>
        {children}
      </div>
    </section>
  );
}
