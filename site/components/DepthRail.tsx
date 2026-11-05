"use client";
// The descent: one doll per world on a rail that stays beside the page and lights the world in view.
import { useEffect, useState } from "react";

export default function DepthRail({ worlds, label }: { worlds: { n: number; name: string; doll: { body: string; scarf: string; orn: string } }[]; label: string }) {
  const [cur, setCur] = useState(0);
  useEffect(() => {
    const io = new IntersectionObserver((es) => {
      for (const e of es) if (e.isIntersecting) setCur(Number((e.target as HTMLElement).dataset.world));
    }, { rootMargin: "-45% 0px -50% 0px" });
    document.querySelectorAll<HTMLElement>("[data-world]").forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);
  return (
    <nav aria-label={label} className="sticky top-28 hidden self-start lg:block">
      <ol className="m-0 grid list-none gap-1.5 p-0">
        {worlds.map((w) => {
          const on = w.n === cur;
          return (
            <li key={w.n}>
              <a href={`#world-${w.n}`} aria-current={on ? "true" : undefined}
                className={`group flex items-center gap-2.5 rounded-[3px] px-2 py-1 no-underline transition-colors ${on ? "bg-ink text-gold-b" : "text-paper-dim hover:text-paper"}`}>
                <svg viewBox="0 0 100 170" aria-hidden="true" className={`h-8 w-auto transition-transform duration-300 ${on ? "scale-125" : "group-hover:scale-110"}`}>
                  <use href="#doll" width="100" height="170" style={{ "--db": w.doll.body, "--ds": w.doll.scarf, "--do": w.doll.orn } as React.CSSProperties} />
                </svg>
                <span className="font-pixel text-lg leading-none">{w.n}</span>
                <span className="text-[13px] leading-tight">{w.name}</span>
              </a>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
