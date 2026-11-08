// A world on stage: its photo or its colours, its name set huge and hollow, a beam of its light on a gilded plinth,
// the boss standing in it and its creatures in front. Used by the home page picker and the worlds page.
import { asset } from "@/lib/asset";

export interface StageWorld { n: number; name: string; img: string | null; light: string; bg: string; boss: string; mobs: string[] }

export function StageGround({ w }: { w: StageWorld }) {
  return w.img ? (
    <img key={w.img} className="kenburns absolute inset-0 -z-30 size-full object-cover opacity-70 motion-safe:animate-[wp-in_.6s_ease-out]" src={asset(w.img)} alt="" width={1920} height={820} loading="lazy" />
  ) : (
    <span key={`g${w.n}`} className="absolute inset-0 -z-30" style={{ background: `radial-gradient(ellipse at 70% 30%, ${w.light}55 0%, ${w.bg} 50%, #0a0605 100%)` }} />
  );
}

export function StageTitle({ w, className = "" }: { w: StageWorld; className?: string }) {
  return (
    <p key={`t${w.n}`} aria-hidden="true"
      className={`pointer-events-none absolute -right-4 -z-10 m-0 font-display leading-[0.8] font-normal whitespace-nowrap text-transparent uppercase opacity-60 motion-safe:animate-[wp-in_.8s_ease-out] [-webkit-text-stroke:1.5px_#d9a441] ${className}`}>
      {w.name}
    </p>
  );
}

export function StageCast({ w, className = "" }: { w: StageWorld; className?: string }) {
  return (
    <div key={`s${w.n}`} className={`pointer-events-none absolute right-0 bottom-0 -z-10 h-full ${className}`} aria-hidden="true">
      <span className="absolute top-0 right-[16%] h-[92%] w-[46%] opacity-70 [clip-path:polygon(38%_0,62%_0,100%_100%,0_100%)]"
        style={{ background: `linear-gradient(180deg, ${w.light}00 0%, ${w.light}55 60%, ${w.light}22 100%)` }} />
      <span className="absolute right-[12%] bottom-[9%] h-[14%] w-[54%] rounded-[50%] border-2 border-gold-b/70 bg-[radial-gradient(ellipse,rgba(240,201,96,.35),rgba(10,6,5,.9)_70%)] shadow-[0_0_40px_rgba(240,201,96,.35)]" />
      <img className="bob absolute bottom-[15%] left-[61%] h-[70%] w-[70%] -translate-x-1/2 object-contain object-bottom drop-shadow-[0_28px_30px_rgba(0,0,0,.8)] motion-safe:animate-[rise_.7s_cubic-bezier(.2,.8,.2,1)_both]"
        src={asset(`portraits/${w.boss}.webp`)} alt="" width={512} height={512} loading="lazy" />
      <div className="absolute bottom-[2%] left-[61%] flex -translate-x-1/2 items-end gap-0.5">
        {w.mobs.map((m, k) => (
          <img key={m} className="h-[clamp(56px,8.4vw,118px)] w-auto drop-shadow-[0_10px_10px_rgba(0,0,0,.75)] motion-safe:animate-[rise_.55s_cubic-bezier(.2,.8,.2,1)_both]"
            style={{ animationDelay: `${0.25 + 0.07 * k}s` }} src={asset(`portraits/${m}.webp`)} alt="" width={256} height={256} loading="lazy" />
        ))}
      </div>
    </div>
  );
}

const CORNERS = ["top-0 left-0", "top-0 right-0 -scale-x-100", "bottom-0 left-0 -scale-y-100", "right-0 bottom-0 -scale-100"];

export function StageCorners() {
  return (
    <>
      {CORNERS.map((c) => (
        <svg key={c} className={`pointer-events-none absolute z-10 size-[clamp(44px,5vw,72px)] ${c}`} viewBox="-34 -34 68 68" aria-hidden="true">
          <use href="#bloom" />
        </svg>
      ))}
    </>
  );
}
