import type { Ing } from "@/lib/types";
import { Ingredients, Inlay } from "./Bits";

export interface Meet {
  mode: "altar" | "lair"; modeLabel: string; place: string; steps: string[];
  offering?: { id: string; tex: string | null; name: string; station: string | null; inputs: Ing[] };
  heartTex?: string; heartName?: string;
}

/** How a boss is met: at an altar with its offering, or in its lair. Steps in order, the offering's recipe in icons. */
export default function MeetBoss({ meet, title, offeringLabel, compact = false }: { meet: Meet; title: string; offeringLabel: string; compact?: boolean }) {
  return (
    <div className={`border-2 border-gold bg-ink/80 ${compact ? "p-4" : "p-5 md:p-6"}`}>
      <div className="mb-3 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h3 className="m-0 font-display text-2xl font-normal text-gold-b">{title}</h3>
        <span className={`rounded-[2px] px-2 py-0.5 text-[13px] font-bold ${meet.mode === "lair" ? "bg-berry text-paper" : "bg-gold-b text-ink"}`}>{meet.modeLabel}</span>
        <span className="text-[15px] text-paper-dim">{meet.place}</span>
      </div>
      <ol className="m-0 mb-1 grid list-none gap-2 p-0">
        {meet.steps.map((s, i) => (
          <li key={i} className="grid grid-cols-[28px_minmax(0,1fr)] items-baseline gap-2 text-[15px] leading-snug text-paper">
            <span className="font-pixel text-xl text-gold-b">{i + 1}</span><span>{s}</span>
          </li>
        ))}
      </ol>
      {meet.offering && (
        <div className="mt-4 border-t border-rule pt-3">
          <p className="m-0 mb-2 flex items-center gap-2 text-[15px] text-paper"><Inlay src={meet.offering.tex} size={32} />
            <span><strong>{meet.offering.name}</strong> <span className="text-paper-dim">({offeringLabel}{meet.offering.station ? `, ${meet.offering.station}` : ""})</span></span></p>
          <Ingredients inputs={meet.offering.inputs} />
        </div>
      )}
      {meet.heartTex && (
        <p className="m-0 mt-4 flex items-center gap-2 border-t border-rule pt-3 text-[15px] text-paper"><Inlay src={meet.heartTex} size={32} /><strong>{meet.heartName}</strong></p>
      )}
    </div>
  );
}
