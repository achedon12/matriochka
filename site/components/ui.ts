// Shared Tailwind class sets: one button pair, one frame, one heading scale for the whole site.
export const btn =
  "inline-flex min-h-11 items-center gap-2.5 rounded-[3px] bg-gold-b px-5 py-3 font-body text-lg font-bold leading-none text-ink " +
  "shadow-[inset_0_0_0_2px_#17100d,0_3px_0_#17100d] transition-[transform,background-color] duration-150 " +
  "hover:-translate-y-px hover:bg-[#ffdd80] hover:text-ink active:translate-y-px [&_svg]:size-5";

export const btnGhost =
  "inline-flex min-h-11 items-center gap-2.5 rounded-[3px] bg-ink/55 px-5 py-3 font-body text-lg font-bold leading-none text-paper " +
  "shadow-[inset_0_0_0_2px_#f3e2c2] transition-[transform,background-color,color] duration-150 " +
  "hover:-translate-y-px hover:bg-ink/80 hover:text-gold-b active:translate-y-px [&_svg]:size-5";

export const btnDark =
  "inline-flex min-h-11 items-center gap-2.5 rounded-[3px] bg-ink px-5 py-3 font-body text-lg font-bold leading-none text-gold-b " +
  "shadow-[inset_0_0_0_2px_#f0c960,0_3px_0_rgba(23,16,13,0.6)] transition-transform duration-150 hover:-translate-y-px hover:text-gold-b active:translate-y-px [&_svg]:size-5";

export const h2 = "m-0 mb-3.5 text-balance font-display text-[clamp(38px,5.4vw,72px)] leading-[0.98] font-normal text-gold-b";
export const lead = "m-0 mb-[clamp(28px,4vw,44px)] max-w-[60ch] text-[19px] leading-relaxed text-paper-dim";
export const section = "py-[clamp(60px,8vw,112px)]";
export const sectionDark = "bg-ink border-y-2 border-gold py-[clamp(60px,8vw,112px)]";
export const wrap = "mx-auto w-full max-w-[1240px] px-4 md:px-8";
export const frame = "relative border-2 border-gold bg-black shadow-frame";
export const quiet = "text-gold-b underline decoration-1 underline-offset-[3px] hover:text-[#ffe08a]";
