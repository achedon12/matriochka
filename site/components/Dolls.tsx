// The opened set of nesting dolls (hero, and the index of the Worlds page) and the doll-shaped window.
import { BASE } from "@/lib/config";
import { asset } from "@/lib/asset";
import type { Lang, World } from "@/lib/types";
import { BLACK, DOLL } from "./Ornament";

export function DollRow({ worlds, lang, title, animated = true, className = "dolls" }: {
  worlds: World[]; lang: Lang; title: string; animated?: boolean; className?: string;
}) {
  const H = 300;
  const r = 0.84;
  const hs = worlds.map((_, i) => H * r ** i);
  const ws = hs.map((h) => (h * 100) / 170);
  const xs: number[] = [];
  let x = 0;
  hs.forEach((h, i) => {
    xs.push(x);
    x += ws[i] + Math.max(6, h * 0.085);
  });
  const total = x;
  const base = 300;
  const top = animated ? -78 : -8;
  const bigC = xs[0] + ws[0] / 2;
  const prefix = lang === "fr" ? "/fr" : "";
  const order = worlds.map((_, i) => i).reverse();
  return (
    <svg className={`${className}${animated ? " is-animated" : ""}`} viewBox={`-10 ${top} ${Math.round(total + 16)} ${Math.round(base + 44 - top)}`}
      role="group" aria-label={title}>
      <path className="shelf" d={`M-6,${base + 1.5} H${Math.round(total + 2)}`} />
      <path className="shelf-dots" d={`M-6,${base + 9} H${Math.round(total + 2)}`} />
      {order.map((i) => {
        const w = worlds[i];
        const h = hs[i];
        const s = h / 170;
        const tr = `translate(${xs[i].toFixed(1)} ${(base - h).toFixed(1)}) scale(${s.toFixed(4)})`;
        const style = { "--db": w.doll.body, "--ds": w.doll.scarf, "--do": w.doll.orn } as React.CSSProperties;
        const label = i === 0 ? w.name : `${lang === "fr" ? "Monde" : "World"} ${i}, ${w.name}`;
        const dx = bigC - (xs[i] + ws[i] / 2);
        const art = i === 0 && animated ? (
          <>
            <g className="lid"><g transform={tr}><use href="#doll" width="100" height="170" clipPath="url(#doll-top)" style={style} /></g></g>
            <g transform={tr}>
              <ellipse cx="50" cy="99" rx="45" ry="5" fill={BLACK} />
              <use href="#doll" width="100" height="170" clipPath="url(#doll-bottom)" style={style} />
            </g>
          </>
        ) : (
          <g transform={tr}><use href="#doll" width="100" height="170" style={style} /></g>
        );
        return (
          <a key={i} className="hd" href={`${BASE}${prefix}/worlds/#world-${i}`} data-name={label} aria-label={label}
            style={{ "--i": i, "--dx": dx.toFixed(1) } as React.CSSProperties}>
            <g className="hd-move">
              <g className="hd-hover">
                {art}
                <rect className="hd-ring" x={(xs[i] - 5).toFixed(1)} y={(base - h - 6).toFixed(1)} width={(ws[i] + 10).toFixed(1)} height={(h + 12).toFixed(1)} rx="8" />
              </g>
            </g>
            <text className="hd-n" x={(xs[i] + ws[i] / 2).toFixed(1)} y={base + 32} textAnchor="middle">{i}</text>
          </a>
        );
      })}
    </svg>
  );
}

/** A screenshot seen through a doll-shaped window; the world's block stands in when there is no capture. */
export function DollWindow({ world, alt, id }: { world: World; alt: string; id: string }) {
  const pid = `tile-${id}`;
  return (
    <svg className="window" viewBox="-4 -4 108 178" role="img" aria-label={alt}>

      <path d={DOLL} fill={BLACK} transform="translate(0 3)" opacity=".5" />
      <g clipPath="url(#doll-clip)">
        {world.tall ? (
          <image href={asset(world.tall)} x="-10" y="0" width="120" height="180" preserveAspectRatio="xMidYMid slice" />
        ) : (
          <>
            <rect x="0" y="0" width="100" height="170" fill={world.bg} />
            <rect x="0" y="0" width="100" height="170" fill={world.light} opacity=".18" />
            <image href={asset(`portraits/${world.boss.id}.png`)} x="-6" y="30" width="112" height="112" preserveAspectRatio="xMidYMid meet" />
          </>
        )}
        <path d="M2,96 Q50,106 98,96" fill="none" stroke={BLACK} strokeOpacity=".55" strokeWidth="2.4" />
      </g>
      <path d={DOLL} fill="none" className="window-rim" />
      <path d="M2,96 Q50,106 98,96" fill="none" className="window-seam" />
    </svg>
  );
}
