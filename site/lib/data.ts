// The data of the pages, by language and version. Safe for client components: nothing is imported here.
// The latest version's data is handed in on the server by lib/latest.ts (prerendered pages); an older
// version's by the reader page once it has fetched it (components/Reader.tsx).
import { LATEST, pageIn } from "./versions";
import type { Creature, Lang, SiteData } from "./types";

export { asset, SHARED } from "./asset";
export { pageIn };

const DATA = new Map<string, SiteData>();

export function provide(lang: Lang, v: string, d: SiteData) {
  // the catalogue is every world's items and blocks in world order; an older version's file leaves it out
  if (!d.catalog) d.catalog = d.worlds.map((w) => ({ n: w.n, name: w.name, items: w.codex.items, blocks: w.codex.blocks }));
  DATA.set(`${v}/${lang}`, d);
}

/** The data of a language, in a version (the latest when none is given). */
export function getData(lang: Lang, v?: string | null): SiteData {
  const d = DATA.get(`${v ?? LATEST}/${lang}`);
  if (!d) throw new Error(`no data for ${v ?? LATEST}/${lang}`);
  return d;
}

/** A page path in a language and a version, as given to next/link (which adds the base path). The latest
 * version keeps the plain addresses; an older one is drawn by the reader page: /v/?v=<version>&p=<path>. */
export function href(lang: Lang, path = "", v?: string | null): string {
  const p = path.replace(/^\//, "");
  const root = lang === "fr" ? "/fr/" : "/";
  if (!v || v === LATEST) return root + p;
  const [page, hash] = p.split("#");
  return `${root}v/?v=${v}${page ? `&p=${page}` : ""}${hash !== undefined ? `#${hash}` : ""}`;
}

/** The same page in the other language. */
export function otherLang(lang: Lang): Lang {
  return lang === "en" ? "fr" : "en";
}

export function creature(lang: Lang, id: string, v?: string | null): Creature | undefined {
  const d = getData(lang, v);
  return d.mobs.find((m) => m.id === id) ?? d.bosses.find((b) => b.id === id);
}

export function allCreatureIds(v?: string | null): string[] {
  const d = getData("en", v);
  return [...d.mobs.map((m) => m.id), ...d.bosses.map((b) => b.id)];
}
