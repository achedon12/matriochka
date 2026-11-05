import Link from "next/link";
import type { ReactNode } from "react";
import { asset, getData, href, otherLang, SHARED } from "@/lib/data";
import type { Lang } from "@/lib/types";
import { Icon } from "./Bits";
import { Sprite, Vine } from "./Ornament";
import { StickyHeader } from "./Islands";

const LEFT = ["worlds", "bestiary"] as const;
const RIGHT = ["bosses", "systems"] as const;

/** Header, ornament and footer around every page. `path` is the page path without language, e.g. "worlds/3/". */
export function Shell({ lang, path, section, children }: { lang: Lang; path: string; section?: string; children: ReactNode }) {
  const { copy } = getData(lang);
  const ui = copy.ui;
  const other = otherLang(lang);
  const item = (p: (typeof LEFT)[number] | (typeof RIGHT)[number]) => (
    <li key={p}>
      <Link href={href(lang, `${p}/`)} aria-current={section === p ? (path === `${p}/` ? "page" : "true") : undefined}>
        <svg className="cur" viewBox="0 0 100 170" aria-hidden="true"><use href="#doll" /></svg>
        {copy.nav[p]}
      </Link>
    </li>
  );
  return (
    <>
      <Sprite />
      <a className="skip" href="#main">{ui.skip}</a>
      <StickyHeader />
      <header className="top">
        <div className="wrap top-in">
          <a className="lang" href={asset((other === "fr" ? "fr/" : "") + path)} hrefLang={other} lang={other}>{ui.other}</a>
          <nav className="nav" aria-label={ui.main}>
            <ul className="nav-l">{LEFT.map((p) => item(p))}</ul>
            <Link className="brand" href={href(lang)} aria-current={path === "" ? "page" : undefined}>
              <span className="medal"><img src={asset("logo-128.png")} width="72" height="72" alt="" /></span>
              <span className="word">Matriochka</span>
            </Link>
            <ul className="nav-r">{RIGHT.map((p) => item(p))}<li className="nav-dl"><Link href={href(lang, "download/")}>{copy.nav.download}</Link></li></ul>
          </nav>
          <a className="gh" href={SHARED.repo} aria-label={ui.github}><Icon name="github" /></a>
        </div>
        <Link className="ribbon" href={href(lang, "download/")} aria-current={section === "download" ? "page" : undefined}>
          <Icon name="download" />
          <span>{copy.nav.download}</span>
        </Link>
      </header>
      <Vine kind="black" className="vine-top" />
      <main id="main">{children}</main>
      <footer className="foot">
        <Vine kind="black" />
        <div className="wrap foot-in">
          <div className="foot-brand">
            <img src={asset("logo-128.png")} width="64" height="64" alt="" />
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
