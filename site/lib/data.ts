import en from "@/data/en.json";
import fr from "@/data/fr.json";
import { LATEST, olderData } from "./versions";
import type { Creature, Lang, SiteData } from "./types";

export { asset, SHARED } from "./asset";

const DATA: Record<Lang, SiteData> = { en: en as unknown as SiteData, fr: fr as unknown as SiteData };
const MERGED = new Map<string, SiteData>();

/** An older version's data, with the labels it lacks (pages added since, the version picker) taken from the
 * latest: its own words win wherever it has them. */
function older(lang: Lang, v: string): SiteData {
  const key = `${v}/${lang}`;
  if (!MERGED.has(key)) {
    const d = olderData(lang, v);
    if (!d) throw new Error(`site/data/versions/${v}/${lang}.json is missing: run tools/site_versions.py`);
    /* eslint-disable @typescript-eslint/no-explicit-any */
    const c = d.copy as any, k = DATA[lang].copy as any;
    MERGED.set(key, { ...d, copy: { ...k, ...c, ui: { ...k.ui, ...c.ui }, nav: { ...k.nav, ...c.nav }, items: { ...k.items, ...c.items }, versions: k.versions } });
  }
  return MERGED.get(key)!;
}

/** The data of a language, in a version (the latest when none is given). */
export function getData(lang: Lang, v?: string | null): SiteData {
  return !v || v === LATEST ? DATA[lang] : older(lang, v);
}

/** A page path in a language and a version, as given to next/link (which adds the base path). The latest
 * version keeps the plain addresses; an older one lives under /v/<version>/. */
export function href(lang: Lang, path = "", v?: string | null): string {
  const p = path.replace(/^\//, "");
  return (lang === "fr" ? "/fr/" : "/") + (v && v !== LATEST ? `v/${v}/` : "") + p;
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

/** Whether a page (a path without language or version) exists in a version. */
export function pageIn(path: string, v?: string | null): boolean {
  const p = path.split("#")[0];
  const d = getData("en", v);
  let m = p.match(/^creatures\/([\w-]+)\/$/);
  if (m) return !!creature("en", m[1], v);
  m = p.match(/^worlds\/(\d+)\/$/);
  if (m) return d.worlds.some((w) => w.n === Number(m![1]));
  return ["", "worlds/", "bestiary/", "bosses/", "items/", "systems/", "changes/"].includes(p);
}
