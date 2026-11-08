// What changed between the versions, as the pages show it: a badge on what is new or changed in the version
// shown, and the short history of one thing. No data import here: the client catalogue uses them too.
import type { Hist, Mark } from "@/lib/versions";

/* eslint-disable @typescript-eslint/no-explicit-any */
export type VersionLabels = Record<string, any>;

export function badgeText(m: NonNullable<Mark>, l: VersionLabels): string {
  return (m.kind === "new" ? l.new : l.changed).replace("{v}", m.v);
}

/** "New in 0.7.0" or "Changed in 0.7.0"; nothing when neither. */
export function VBadge({ m, l, className = "" }: { m: Mark | undefined; l: VersionLabels; className?: string }) {
  if (!m) return null;
  return <span className={`vb vb-${m.kind} ${className}`}>{badgeText(m, l)}</span>;
}

/** Since which version a thing is in the mod and what changed, version by version. */
export function HistoryList({ h, l, className = "" }: { h: Hist | null | undefined; l: VersionLabels; className?: string }) {
  if (!h || (!h.since && !h.changes.length)) return null;
  const facet = (f: string) => l.f?.[f] ?? f;
  return (
    <ul className={`vh ${className}`}>
      <li>{h.since ? l.since.replace("{v}", h.since) : l.sinceFirst}</li>
      {[...h.changes].reverse().map((c) => (
        <li key={c.v}>{l.changedIn.replace("{v}", c.v).replace("{f}", c.f.map(facet).join(", "))}</li>
      ))}
    </ul>
  );
}
