// Hand-drawn khokhloma ornament: gold stems that curl, red berries, black leaves. Everything is defined
// once per page as SVG symbols and patterns (Sprite), then reused as borders, frame corners and dolls.
import type { ReactNode } from "react";

export const RED = "#8E2A21";
export const RED_B = "#B0412E";
export const BLACK = "#17100D";
export const GOLD = "#D9A441";
export const GOLD_B = "#F0C960";
export const PAPER = "#F3E2C2";

/** The doll silhouette, 100 x 170: round head, narrow neck, full belly, flat base. */
export const DOLL =
  "M50,2 C70,2 82,18 82,38 C82,50 78,58 73,63 C91,73 98,96 98,122 C98,148 93,163 87,170 " +
  "L13,170 C7,163 2,148 2,122 C2,96 9,73 27,63 C22,58 18,50 18,38 C18,18 30,2 50,2 Z";

function leaf(x: number, y: number, rot: number, s: number, fill: string, vein: string) {
  return (
    `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})">` +
    `<path d="M0,0 C5,-7.5 15,-8.5 23,0 C15,6.5 5,6 0,0Z" fill="${fill}"/>` +
    `<path d="M2.5,0 C9,-1.2 15,-1.2 20,0" fill="none" stroke="${vein}" stroke-width="1" stroke-linecap="round"/></g>`
  );
}

function berries(x: number, y: number, s: number, fill: string, ring: string) {
  const out = [
    [0, 0],
    [6.4, -2.6],
    [5.2, 4.2],
  ]
    .map(
      ([dx, dy]) =>
        `<circle cx="${dx}" cy="${dy}" r="3.3" fill="${fill}" stroke="${ring}" stroke-width=".9"/>` +
        `<circle cx="${dx - 1.1}" cy="${dy - 1.1}" r=".9" fill="${GOLD_B}"/>`,
    )
    .join("");
  return `<g transform="translate(${x} ${y}) scale(${s})">${out}</g>`;
}

function vineHalf(stem: string, lf: string, vein: string, berry: string, ring: string) {
  return (
    `<path d="M40,12.8 C39,5 46,1.6 50.5,4.6 C54,7 51.5,11.4 48.4,9.6" fill="none" stroke="${stem}" stroke-width="1.5" stroke-linecap="round"/>` +
    `<path d="M30,14.6 C26,9.5 20.5,10 20,13.6 C19.6,16.4 23.4,17 24.4,15" fill="none" stroke="${stem}" stroke-width="1.2" stroke-linecap="round"/>` +
    berries(57, 8.5, 1, berry, ring) +
    leaf(43, 14.2, 38, 0.8, lf, vein) +
    leaf(35, 14, 148, 0.72, lf, vein) +
    `<path d="M66,16.5 c2,-3 5,-4 7.5,-3.6 M70,19.4 c2.6,-1.6 5,-1.8 7,-.8" fill="none" stroke="${stem}" stroke-width=".9" stroke-linecap="round"/>`
  );
}

function vinePattern(id: string, stem: string, lf: string, vein: string, berry: string, ring: string, bg?: string) {
  const half = vineHalf(stem, lf, vein, berry, ring);
  const back = bg ? `<rect width="160" height="48" fill="${bg}"/>` : "";
  return (
    `<pattern id="${id}" width="160" height="48" patternUnits="userSpaceOnUse">${back}` +
    `<path d="M-1,24.5 C27,9 53,9 80,24 S133,39 161,23.5" fill="none" stroke="${stem}" stroke-width="2.4"/>` +
    `<g>${half}</g><g transform="translate(80 48) scale(1 -1)">${half}</g></pattern>`
  );
}

function vinePatternV(id: string, src: string) {
  // the same running vine, turned upright for the sides of a frame
  return `<pattern id="${id}" width="48" height="160" patternUnits="userSpaceOnUse" patternTransform="rotate(90) translate(0 -48)"><rect width="160" height="48" fill="url(#${src})"/></pattern>`;
}

function bloom(stem: string, lf: string, vein: string, berry: string, ring: string) {
  const arms = [0, 90, 180, 270]
    .map(
      (rot) =>
        `<g transform="rotate(${rot})">` +
        `<path d="M0,-9 C-3,-20 6,-30 14,-26 C20,-23 17,-15 12,-17" fill="none" stroke="${stem}" stroke-width="2" stroke-linecap="round"/>` +
        leaf(5, -8, -62, 1.05, lf, vein) +
        leaf(-4, -9, -118, 0.8, lf, vein) +
        `</g>`,
    )
    .join("");
  return arms + berries(-3.4, -0.6, 1.25, berry, ring);
}

function flower() {
  const petals = [0, 1, 2, 3, 4]
    .map(
      (k) =>
        `<ellipse cx="0" cy="-7.4" rx="4.3" ry="6.6" transform="rotate(${k * 72})" fill="currentColor" stroke="${BLACK}" stroke-width=".7"/>`,
    )
    .join("");
  return (
    `<path d="M0,6 C-1,12 -2,16 -1,20" fill="none" stroke="${GOLD}" stroke-width="1.4"/>` +
    leaf(-1, 15, 158, 0.62, BLACK, GOLD) +
    leaf(-1, 15, 22, 0.62, BLACK, GOLD) +
    petals +
    `<circle r="3.6" fill="${GOLD_B}" stroke="${BLACK}" stroke-width=".8"/>`
  );
}

function dollSymbol() {
  return (
    `<path d="${DOLL}" fill="var(--db,${RED_B})"/>` +
    `<ellipse cx="50" cy="39.5" rx="24" ry="23" fill="var(--ds,${BLACK})"/>` +
    `<g fill="${GOLD_B}" opacity=".9"><circle cx="31" cy="24" r="1.3"/><circle cx="69" cy="24" r="1.3"/><circle cx="27" cy="44" r="1.3"/><circle cx="73" cy="44" r="1.3"/><circle cx="50" cy="13" r="1.3"/></g>` +
    `<ellipse cx="50" cy="41" rx="18" ry="17.5" fill="${PAPER}"/>` +
    `<path d="M32,39 C32,27 43,22.5 50,28 C57,22.5 68,27 68,39 C64,32 57,30 50,33 C43,30 36,32 32,39Z" fill="${BLACK}"/>` +
    `<ellipse cx="43.2" cy="42.4" rx="1.7" ry="2.3" fill="${BLACK}"/><ellipse cx="56.8" cy="42.4" rx="1.7" ry="2.3" fill="${BLACK}"/>` +
    `<circle cx="40.2" cy="49" r="3.4" fill="${RED_B}" opacity=".75"/><circle cx="59.8" cy="49" r="3.4" fill="${RED_B}" opacity=".75"/>` +
    `<path d="M47.2,52.6 Q50,51 52.8,52.6 Q50,56 47.2,52.6Z" fill="${RED}"/>` +
    `<path d="M38,58 C42,63 46,64 50,64 C54,64 58,63 62,58 L58,68 L50,64 L42,68Z" fill="var(--ds,${BLACK})"/>` +
    `<ellipse cx="50" cy="121" rx="33" ry="38" fill="${PAPER}" stroke="${GOLD}" stroke-width="1.8"/>` +
    `<g transform="translate(50 116) scale(1.25)" style="color:var(--do,${RED_B})">${flower()}</g>` +
    `<path d="M6,95 Q50,104 94,95" fill="none" stroke="${BLACK}" stroke-opacity=".45" stroke-width="1.1"/>` +
    `<path d="${DOLL}" fill="none" stroke="${GOLD_B}" stroke-width="2.4" vector-effect="non-scaling-stroke"/>`
  );
}

/** All symbols and patterns, drawn once per page by components/Sprite.tsx. */
export const SPRITE =
  vinePattern("vine-black", GOLD, GOLD, BLACK, RED_B, BLACK, BLACK) +
  vinePattern("vine-red", GOLD, BLACK, GOLD, RED_B, BLACK) +
  vinePattern("vine-gold", BLACK, RED, GOLD_B, RED_B, BLACK, GOLD) +
  vinePatternV("vine-red-v", "vine-red") +
  `<symbol id="bloom" viewBox="-34 -34 68 68">${bloom(GOLD, BLACK, GOLD, RED_B, BLACK)}</symbol>` +
  `<symbol id="bloom-dark" viewBox="-34 -34 68 68">${bloom(GOLD, GOLD, BLACK, RED_B, BLACK)}</symbol>` +
  `<symbol id="doll" viewBox="0 0 100 170">${dollSymbol()}</symbol>` +
  `<clipPath id="doll-clip"><path d="${DOLL}"/></clipPath>` +
  `<clipPath id="doll-top"><rect x="-10" y="-10" width="120" height="109"/></clipPath>` +
  `<clipPath id="doll-bottom"><rect x="-10" y="98" width="120" height="90"/></clipPath>`;


/** A horizontal border of running vine on a red, black or gold ground. */
export function Vine({ kind = "red", className = "" }: { kind?: "red" | "black" | "gold"; className?: string }) {
  return (
    <svg className={`vine vine-${kind} ${className}`} aria-hidden="true" focusable="false" width="100%" height="48">
      <rect width="100%" height="48" fill={`url(#vine-${kind})`} />
    </svg>
  );
}

export function Corners({ dark = false }: { dark?: boolean }) {
  return (
    <>
      {(["tl", "tr", "bl", "br"] as const).map((p) => (
        <svg key={p} className={`corner corner-${p}`} aria-hidden="true" focusable="false" viewBox="-34 -34 68 68">
          <use href={dark ? "#bloom-dark" : "#bloom"} />
        </svg>
      ))}
    </>
  );
}

/** Black lacquer inside a gold double rule, with a painted flower in each corner. */
export function Lacquer({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`lacquer ${className}`}>
      <Corners dark />
      <div className="lacquer-in">{children}</div>
    </div>
  );
}
