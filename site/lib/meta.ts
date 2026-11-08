import type { Metadata, Viewport } from "next";
import { BASE, SITE_ORIGIN } from "./config";
import "./latest";
import { getData, href } from "./data";
import type { Lang } from "./types";

export const viewport: Viewport = { themeColor: "#17100D", width: "device-width", initialScale: 1 };

/** Title, description, language alternates and the Open Graph card of a page. `v` is the version shown when it
 * is not the latest: its pages say so in their title. */
export function meta(lang: Lang, path: string, title: string | null, description: string, v?: string): Metadata {
  const site = v ? `Matriochka ${v}` : "Matriochka";
  const full = title ? `${title} | ${site}` : site;
  const en = `${BASE}${href("en", path, v)}`;
  const fr = `${BASE}${href("fr", path, v)}`;
  return {
    metadataBase: new URL(SITE_ORIGIN),
    title: full,
    description,
    authors: [{ name: "achedon12" }],
    alternates: { canonical: lang === "en" ? en : fr, languages: { en, fr } },
    openGraph: { title: full, description, type: "website", locale: lang === "en" ? "en_GB" : "fr_FR", images: [{ url: `${BASE}/og.png`, width: 1200, height: 630 }] },
    icons: {
      icon: [{ url: `${BASE}/favicon.ico`, sizes: "any" }, { url: `${BASE}/favicon-32.png`, type: "image/png", sizes: "32x32" }, { url: `${BASE}/favicon-192.png`, type: "image/png", sizes: "192x192" }],
      apple: `${BASE}/apple-touch-icon.png`,
    },
  };
}

export function metaFor(lang: Lang, page: "worlds" | "bestiary" | "bosses" | "items" | "systems" | "download", v?: string) {
  const c = getData(lang, v).copy;
  const t = page === "worlds" ? c.worlds.h : c[page].h;
  return meta(lang, `${page}/`, page === "worlds" ? c.nav.worlds : t, c[page].desc, v);
}
