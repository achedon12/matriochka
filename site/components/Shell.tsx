import Link from "next/link";
import type { ReactNode } from "react";
import { asset, getData, href, otherLang, SHARED } from "@/lib/data";
import type { Lang } from "@/lib/types";
import { Icon } from "./Bits";
import { Sprite, Vine } from "./Ornament";

const PAGES = ["worlds", "bestiary", "bosses", "systems", "download"] as const;

/** Header, ornament and footer around every page. `path` is the page path without language, e.g. "worlds/3/". */
export function Shell({ lang, path, section, children }: { lang: Lang; path: string; section?: string; children: ReactNode }) {
  const { copy } = getData(lang);
  const ui = copy.ui;
  const other = otherLang(lang);
  return (
    <>
      <Sprite />
      <a className="skip" href="#main">{ui.skip}</a>
      <header className="top">
        <div className="wrap top-in">
          <Link className="brand" href={href(lang)} aria-current={path === "" ? "page" : undefined}>
            <img src={asset("logo-128.png")} width="40" height="40" alt="" />
            <span>Matriochka</span>
          </Link>
          <nav className="nav" aria-label={ui.main}>
            <ul>
              {PAGES.map((p) => (
                <li key={p}>
                  <Link href={href(lang, `${p}/`)} aria-current={section === p ? (path === `${p}/` ? "page" : "true") : undefined}>
                    {copy.nav[p === "worlds" ? "worlds" : p]}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <div className="top-tools">
            <a className="lang" href={asset((other === "fr" ? "fr/" : "") + path)} hrefLang={other} lang={other}>{ui.other}</a>
            <a className="gh" href={SHARED.repo} aria-label={ui.github}><Icon name="github" /></a>
          </div>
        </div>
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

export function PageHead({ title, lead, children }: { title: string; lead: string; children?: ReactNode }) {
  return (
    <section className="phead">
      <div className="wrap">
        <h1>{title}</h1>
        <p className="lead">{lead}</p>
        {children}
      </div>
    </section>
  );
}
