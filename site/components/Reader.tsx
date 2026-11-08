"use client";
// The pages of an older version of the mod, all from one prerendered page: /v/?v=0.6.0&p=creatures/sporeling/
// reads the version and the page from its address, fetches that version's data (site/public/versions,
// written by tools/site_versions.py) and draws the page with the same components as the latest pages.
import { useEffect, useState } from "react";
import { asset, getData, href, provide } from "@/lib/data";
import type { Lang, SiteData } from "@/lib/types";
import { info, LATEST, pageIn, provideChanges, provideHistory, type ChangeSection, type Hist } from "@/lib/versions";
import HomePage from "./pages/HomePage";
import WorldsPage, { WorldPage } from "./pages/WorldsPage";
import { BestiaryPage, BossesPage, CreaturePage } from "./pages/CreaturesPages";
import { ItemsPage } from "./pages/ItemsPage";
import { SystemsPage } from "./pages/TextPages";
import { ChangesPage } from "./pages/ChangesPage";
import { PageHead, Shell } from "./Shell";
import Link from "./PageLink";

/** A JSON file of site/public; gzip files are unpacked here (the host may or may not have done it). */
async function load<T>(path: string): Promise<T> {
  const r = await fetch(asset(path));
  if (!r.ok) throw new Error(`${path}: ${r.status}`);
  let bytes = new Uint8Array(await r.arrayBuffer());
  if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
    const s = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    bytes = new Uint8Array(await new Response(s).arrayBuffer());
  }
  return JSON.parse(new TextDecoder().decode(bytes)) as T;
}

export interface ReaderLabels { loading: string; unknown: string; failed: string; notIn: string; notInP: string; seeLatest: string }

type State = { kind: "loading" } | { kind: "error"; text: string } | { kind: "ready"; v: string; p: string };

/** The page drawn for one path; a path with no page in this version says so and leads to the latest. */
function Page({ lang, v, p }: { lang: Lang; v: string; p: string }) {
  if (!pageIn(p, v)) {
    const l = getData(lang, v).copy.versions;
    return (
      <Shell lang={lang} path={p} v={v}>
        <PageHead title={l.notIn.replace("{v}", v)} lead={l.notInP.replace("{v}", v)}>
          <p className="mt-6"><Link className="btn" href={href(lang, p)}>{l.seeLatest}</Link></p>
        </PageHead>
      </Shell>
    );
  }
  let m = p.match(/^creatures\/([\w-]+)\/$/);
  if (m) return <CreaturePage lang={lang} id={m[1]} v={v} />;
  m = p.match(/^worlds\/(\d+)\/$/);
  if (m) return <WorldPage lang={lang} n={Number(m[1])} v={v} />;
  switch (p) {
    case "worlds/": return <WorldsPage lang={lang} v={v} />;
    case "bestiary/": return <BestiaryPage lang={lang} v={v} />;
    case "bosses/": return <BossesPage lang={lang} v={v} />;
    case "items/": return <ItemsPage lang={lang} v={v} />;
    case "systems/": return <SystemsPage lang={lang} v={v} />;
    case "changes/": return <ChangesPage lang={lang} v={v} />;
    default: return <HomePage lang={lang} v={v} />;
  }
}

/** The title of the tab, as the prerendered pages have it. */
function title(lang: Lang, v: string, p: string): string {
  const d = getData(lang, v);
  const c = p.match(/^creatures\/([\w-]+)\/$/);
  const w = p.match(/^worlds\/(\d+)\/$/);
  const name = c ? [...d.mobs, ...d.bosses].find((x) => x.id === c[1])?.name
    : w ? d.worlds.find((x) => x.n === Number(w[1]))?.name
    : p === "changes/" ? d.copy.versions.changesH.replace("{v}", v)
    : p ? d.copy.nav[p.replace("/", "")] : null;
  return name ? `${name} | Matriochka ${v}` : `Matriochka ${v}`;
}

export default function Reader({ lang, labels }: { lang: Lang; labels: ReaderLabels }) {
  const [st, setSt] = useState<State>({ kind: "loading" });
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const v = q.get("v") ?? "";
    const p = (q.get("p") ?? "").replace(/^\/+/, "");
    if (v === LATEST) {
      window.location.replace(asset(href(lang, p).slice(1)) + window.location.hash);
      return;
    }
    if (!info(v)) {
      setSt({ kind: "error", text: labels.unknown });
      return;
    }
    let live = true;
    Promise.all([
      load<SiteData>(`versions/${v}/${lang}.json.gz`),
      load<Record<string, Hist>>("versions/history.json.gz"),
      p === "changes/" ? load<Record<string, ChangeSection>>("versions/changes.json.gz") : Promise.resolve(null),
    ]).then(([d, h, c]) => {
      if (!live) return;
      provide(lang, v, d);
      provideHistory(h);
      if (c) provideChanges(c);
      document.title = title(lang, v, p);
      setSt({ kind: "ready", v, p });
    }).catch(() => live && setSt({ kind: "error", text: labels.failed }));
    return () => { live = false; };
  }, [lang, labels]);

  if (st.kind === "ready") return <Page lang={lang} v={st.v} p={st.p} />;
  return (
    <main id="main" className="grid min-h-svh place-items-center p-6">
      <div className="grid justify-items-center gap-5 text-center" role="status" aria-live="polite">
        <span className={`grid size-[86px] place-items-center rounded-full bg-ink shadow-[0_0_0_2px_#d9a441,0_0_0_6px_#17100d,0_0_0_7px_rgba(240,201,96,.35)] ${st.kind === "loading" ? "motion-safe:animate-pulse" : ""}`}>
          <img src={asset("logo-128.webp")} width="72" height="72" alt="" />
        </span>
        <p className="m-0 max-w-[40ch] text-lg text-paper">{st.kind === "loading" ? labels.loading : st.text}</p>
        {st.kind === "error" && <p className="m-0"><a className="quiet" href={asset(href(lang).slice(1))}>{labels.seeLatest}</a></p>}
      </div>
    </main>
  );
}
