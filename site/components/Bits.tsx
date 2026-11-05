import { asset, SHARED } from "@/lib/data";
import type { Ing, Recipe } from "@/lib/types";

/** A Lucide icon (ISC licence), inner markup exported by tools/site.py. */
export function Icon({ name, className = "ic" }: { name: string; className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"
      dangerouslySetInnerHTML={{ __html: SHARED.icons[name] ?? "" }} />
  );
}

/** A Minecraft texture shown pixel for pixel, set in a small gold-edged lacquer inlay. */
export function Inlay({ src, size = 32, alt = "", bare = false }: { src: string | null; size?: number; alt?: string; bare?: boolean }) {
  const img = src ? (
    <img className="px" src={asset(src)} width={size} height={size} alt={alt} loading="lazy" decoding="async" />
  ) : (
    <span className="px px-vanilla" style={{ width: size, height: size }} aria-hidden="true" />
  );
  return bare ? img : <span className="inlay">{img}</span>;
}

export function Ingredients({ inputs }: { inputs: Ing[] }) {
  return (
    <ul className="ings">
      {inputs.map((i) => (
        <li className="ing" key={i.id}>
          <Inlay src={i.tex} size={24} bare />
          <span className="num">{i.n}</span>
          <span className="ing-name">{i.name}</span>
        </li>
      ))}
    </ul>
  );
}

export function Recipes({ recipes }: { recipes: Recipe[] }) {
  return (
    <ul className="recs">
      {recipes.map((r) => (
        <li className="rec" key={r.out}>
          <p className="rec-out"><Inlay src={r.tex} size={32} /><span>{r.name}{r.count > 1 && <span className="num"> ×{r.count}</span>}</span></p>
          <Ingredients inputs={r.inputs} />
        </li>
      ))}
    </ul>
  );
}

export function Shot({ src, caption, className = "shot" }: { src: string | null; caption: string; className?: string }) {
  if (!src) return null;
  const gui = src.includes("gui_");
  return (
    <figure className={`${className}${gui ? " shot-gui" : ""}`}>
      <img src={asset(src)} alt={caption} loading="lazy" decoding="async" />
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
