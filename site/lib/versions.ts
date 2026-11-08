// The versions of the mod the site shows, from site/data/versions.json (tools/site_versions.py): the latest
// is the current tree, prerendered at the plain addresses; the older ones are drawn by the reader page
// (/v/?v=<version>&p=<page>) from the data it fetches. Safe for client components: the history and the
// changelog sections are handed in (lib/latest.ts on the server, the reader in the browser).
import index from "@/data/versions.json";

export interface VersionInfo {
  v: string; mc: string[]; date: string | null; released: boolean; latest: boolean;
  /** what has a page of its own in that version */
  creatures: string[]; bosses: string[]; worlds: number[];
}
export interface Skipped { v: string; mc: string[]; date: string | null; reason: "static" | "failed"; note: string }
export interface Hist { since: string | null; changes: { v: string; f: string[] }[] }
/** A run of a changelog line: plain text, code, bold, a link out [a, text, url] or a page of the site [r, text, path]. */
export type Seg = ["t" | "c" | "b", string] | ["a" | "r", string, string];
export type ChangeBlock = ["h", string] | ["p", Seg[]] | ["ul", [Seg[], Seg[][]][]];
export interface ChangeSection { title: string; lead: Seg[][]; blocks: ChangeBlock[] }
/** What a badge says about one thing in the version shown. */
export type Mark = { kind: "new" | "changed"; v: string } | null;

const INDEX = index as unknown as { latest: string; versions: VersionInfo[]; skipped: Skipped[] };

export const LATEST = INDEX.latest;
export const VERSIONS: VersionInfo[] = INDEX.versions;
export const SKIPPED: Skipped[] = INDEX.skipped;
export const OLDER: string[] = VERSIONS.filter((x) => !x.latest).map((x) => x.v);

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

/** The version a page shows: the one it was given, or the latest. */
export function shown(v?: string | null): string {
  return v ?? LATEST;
}

/** Whether a page (a path without language or version, e.g. "creatures/sporeling/") exists in a version. */
export function pageIn(path: string, v?: string | null): boolean {
  const p = path.split("#")[0];
  const x = info(shown(v));
  if (!x) return false;
  let m = p.match(/^creatures\/([\w-]+)\/$/);
  if (m) return x.creatures.includes(m[1]) || x.bosses.includes(m[1]);
  m = p.match(/^worlds\/(\d+)\/$/);
  if (m) return x.worlds.includes(Number(m[1]));
  return ["", "worlds/", "bestiary/", "bosses/", "items/", "systems/", "changes/"].includes(p);
}

/** Whether a creature id is a boss (in any version). */
export function isBoss(id: string): boolean {
  return VERSIONS.some((x) => x.bosses.includes(id));
}

let HISTORY: Record<string, Hist> = {};
let CHANGES: Record<string, ChangeSection> = {};

export function provideHistory(h: Record<string, Hist>) {
  HISTORY = h;
}

export function provideChanges(c: Record<string, ChangeSection>) {
  CHANGES = c;
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
