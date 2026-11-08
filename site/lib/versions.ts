// The versions of the mod the site shows, written by tools/site_versions.py into site/data/versions/:
// index.json (the versions, newest first), history.json (when each thing appeared and changed),
// changes.json (each version's changelog section) and <version>/{en,fr}.json (an older version's data).
// Read at build time only: the pages are static.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import shared from "@/data/shared.json";
import type { Lang, SiteData } from "./types";

export interface VersionInfo { v: string; mc: string[]; date: string | null; released: boolean; latest: boolean }
export interface Skipped { v: string; mc: string[]; date: string | null; reason: "static" | "failed"; note: string }
export interface Hist { since: string | null; changes: { v: string; f: string[] }[] }
/** A run of a changelog line: plain text, code, bold, a link out [a, text, url] or a page of the site [r, text, path]. */
export type Seg = ["t" | "c" | "b", string] | ["a" | "r", string, string];
export type ChangeBlock = ["h", string] | ["p", Seg[]] | ["ul", [Seg[], Seg[][]][]];
export interface ChangeSection { title: string; lead: Seg[][]; blocks: ChangeBlock[] }
/** What a badge says about one thing in the version shown. */
export type Mark = { kind: "new" | "changed"; v: string } | null;

const DIR = join(process.cwd(), "data", "versions");

function read<T>(name: string, fallback: T): T {
  const p = join(DIR, name);
  if (!existsSync(p)) return fallback;
  try {
    return JSON.parse(readFileSync(p, "utf-8")) as T;
  } catch {
    return fallback;
  }
}

// without tools/site_versions.py (no git tags, a bare copy of site/), the site shows the current version only
const INDEX = read<{ latest: string; versions: VersionInfo[]; skipped: Skipped[] }>("index.json", {
  latest: (shared as { version: string }).version,
  versions: [{ v: (shared as { version: string }).version, mc: [], date: null, released: false, latest: true }],
  skipped: [],
});
const HISTORY = read<Record<string, Hist>>("history.json", {});
const CHANGES = read<Record<string, ChangeSection>>("changes.json", {});

export const LATEST = INDEX.latest;
export const VERSIONS: VersionInfo[] = INDEX.versions;
export const SKIPPED: Skipped[] = INDEX.skipped;
/** The older versions, each with its own pages under /v/<version>/. */
export const OLDER: string[] = VERSIONS.filter((x) => !x.latest).map((x) => x.v);
/** The versions the /v/[ver]/ routes are built for. A static export needs at least one: without older versions
 * the latest is built there too (nothing links to it). */
export const VERSION_PARAMS: string[] = OLDER.length ? OLDER : [LATEST];

export function vkey(v: string): number[] {
  return v.split(".").map(Number);
}

export function vcmp(a: string, b: string): number {
  const x = vkey(a), y = vkey(b);
  for (let i = 0; i < Math.max(x.length, y.length); i++) if ((x[i] ?? 0) !== (y[i] ?? 0)) return (x[i] ?? 0) - (y[i] ?? 0);
  return 0;
}

export function info(v: string): VersionInfo | undefined {
  return VERSIONS.find((x) => x.v === v);
}

/** The version a page shows: the one in its address, or the latest. */
export function shown(v?: string | null): string {
  return v ?? LATEST;
}

const loaded = new Map<string, SiteData>();

/** An older version's data as tools/site_versions.py stored it (null when it is not there). */
export function olderData(lang: Lang, v: string): SiteData | null {
  const key = `${v}/${lang}`;
  if (!loaded.has(key)) {
    const d = read<SiteData | null>(`${v}/${lang}.json`, null);
    if (!d) return null;
    loaded.set(key, d);
  }
  return loaded.get(key)!;
}

/** The history of one thing ("item:<id>", "mob:<id>", "world:<n>", "site:<id>") up to the version shown. */
export function history(key: string, v?: string | null): Hist | null {
  const h = HISTORY[key];
  if (!h) return null;
  const s = shown(v);
  if (h.since && vcmp(h.since, s) > 0) return null;
  const changes = h.changes.filter((c) => vcmp(c.v, s) <= 0);
  return h.since || changes.length ? { since: h.since, changes } : null;
}

/** New in the version shown, or changed in it. */
export function mark(key: string, v?: string | null): Mark {
  const h = HISTORY[key];
  const s = shown(v);
  if (!h) return null;
  if (h.since === s) return { kind: "new", v: s };
  if (h.changes.some((c) => c.v === s)) return { kind: "changed", v: s };
  return null;
}

export function changes(v: string): ChangeSection | null {
  return CHANGES[v] ?? null;
}
