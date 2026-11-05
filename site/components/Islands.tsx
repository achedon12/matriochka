"use client";
// Small client-side enhancements. Every page reads and works without them.
import { useEffect, useRef, useState } from "react";

/** Under the hero dolls: names the doll under the pointer or keyboard focus. */
export function DollCaption({ text }: { text: string }) {
  const [label, setLabel] = useState(text);
  const ref = useRef<HTMLParagraphElement>(null);
  useEffect(() => {
    const row = ref.current?.parentElement?.querySelector(".dolls");
    if (!row) return;
    const on = (e: Event) => {
      const a = (e.target as Element).closest?.(".hd");
      setLabel(a ? (a.getAttribute("data-name") ?? text) : text);
    };
    const off = () => setLabel(text);
    row.addEventListener("pointerover", on);
    row.addEventListener("focusin", on);
    row.addEventListener("pointerleave", off);
    row.addEventListener("focusout", off);
    return () => {
      row.removeEventListener("pointerover", on);
      row.removeEventListener("focusin", on);
      row.removeEventListener("pointerleave", off);
      row.removeEventListener("focusout", off);
    };
  }, [text]);
  return <p className="doll-caption" ref={ref} aria-live="polite">{label}</p>;
}

/** Marks the page once it has scrolled past the header, so the sticky header can fold to its compact form. */
export function StickyHeader() {
  useEffect(() => {
    const root = document.documentElement;
    const on = () => root.classList.toggle("is-scrolled", window.scrollY > 90);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);
  return null;
}
