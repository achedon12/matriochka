import en from "@/data/en.json";
import fr from "@/data/fr.json";
import shared from "@/data/shared.json";
import { BASE } from "./config";
import type { Creature, Lang, Shared, SiteData } from "./types";

const DATA: Record<Lang, SiteData> = { en: en as unknown as SiteData, fr: fr as unknown as SiteData };

export const SHARED = shared as Shared;

export function getData(lang: Lang): SiteData {
  return DATA[lang];
}

/** A file in site/public, with the base path the site is served from. */
export function asset(p: string): string {
  return `${BASE}/${p}`;
}

/** A page path in a language, as given to next/link (which adds the base path). */
export function href(lang: Lang, path = ""): string {
  const p = path.replace(/^\//, "");
  return (lang === "fr" ? "/fr/" : "/") + p;
}

/** The same page in the other language. */
export function otherLang(lang: Lang): Lang {
  return lang === "en" ? "fr" : "en";
}

export function creature(lang: Lang, id: string): Creature | undefined {
  const d = getData(lang);
  return d.mobs.find((m) => m.id === id) ?? d.bosses.find((b) => b.id === id);
}

export function allCreatureIds(): string[] {
  const d = getData("en");
  return [...d.mobs.map((m) => m.id), ...d.bosses.map((b) => b.id)];
}
