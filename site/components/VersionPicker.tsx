"use client";
// The version picker of the header: the mod's versions as a drawer of lacquered slots, each with the Minecraft
// versions it runs on. Each one opens the same page in that version (or its section when the page is not in
// it); the choice is kept in the browser, so the latest pages take a returning reader back to it.
import Link from "./PageLink";
import { useEffect, useId, useRef, useState } from "react";
import { Icon } from "./Bits";

import { VERSION_KEY } from "@/lib/config";

export interface PickerVersion { v: string; mc: string[]; date: string | null; latest: boolean; href: string }

function remember(v: string, latest: boolean) {
  try {
    window.localStorage.setItem(VERSION_KEY, latest ? "latest" : v);
  } catch {
    // private windows and blocked storage: the address still carries the version
  }
}

/** "See the latest", under the header of an older version's pages: forgets the older version picked. */
export function LatestLink({ href, children }: { href: string; children: React.ReactNode }) {
  return <Link href={href} onClick={() => remember("", true)}>{children}</Link>;
}

export default function VersionPicker({ current, versions, labels, changes }: {
  current: string; versions: PickerVersion[]; changes: { href: string; label: string };
  labels: { label: string; pick: string; latest: string; mc: string };
}) {
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null);
  const btn = useRef<HTMLButtonElement>(null);
  const id = useId();
  useEffect(() => {
    if (!open) return;
    const away = (e: PointerEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") { setOpen(false); btn.current?.focus(); } };
    document.addEventListener("pointerdown", away);
    document.addEventListener("keydown", key);
    return () => { document.removeEventListener("pointerdown", away); document.removeEventListener("keydown", key); };
  }, [open]);
  const cur = versions.find((x) => x.v === current);
  return (
    <div ref={box} className="vp relative">
      <button ref={btn} type="button" aria-expanded={open} aria-controls={id} onClick={() => setOpen(!open)}
        title={labels.pick} className="vp-btn">
        <span className="sr-only">{labels.label}</span>
        <Icon name="history" className="ic size-[18px]" />
        <span className="font-pixel text-[21px] leading-none">{current}</span>
        <Icon name="chevron-down" className={`ic size-4 transition-transform duration-150 motion-reduce:transition-none ${open ? "rotate-180" : ""}`} />
      </button>
      <div id={id} hidden={!open} className="vp-pop">
        <p className="vp-h">{labels.label}{cur && cur.mc.length > 0 && <span>{labels.mc} {cur.mc.join(", ")}</span>}</p>
        <ul className="vp-list">
          {versions.map((x) => {
            const here = x.v === current;
            return (
              <li key={x.v}>
                <Link href={x.href} aria-current={here ? "page" : undefined} className="vp-row"
                  onClick={() => { remember(x.v, x.latest); setOpen(false); }}>
                  <span className="vp-v">{x.v}</span>
                  <span className="vp-mc">
                    {x.mc.map((m) => <span key={m} className="vp-chip">{m}</span>)}
                  </span>
                  <span className="vp-meta">{x.latest ? <strong>{labels.latest}</strong> : x.date}</span>
                </Link>
              </li>
            );
          })}
        </ul>
        <Link href={changes.href} className="vp-changes" onClick={() => setOpen(false)}><Icon name="book-open" className="ic size-4" />{changes.label}</Link>
      </div>
    </div>
  );
}
