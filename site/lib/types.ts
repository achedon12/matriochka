// Shapes of site/data/{en,fr,shared}.json, written by tools/site.py.

export type Lang = "en" | "fr";

export interface Ing { id: string; tex: string | null; n: number; name: string }
export interface Recipe { out: string; tex: string | null; name: string; count: number; inputs: Ing[] }
export interface DollColours { body: string; scarf: string; orn: string }
export interface Item { id: string; tex: string | null; name: string; effect: string }
export interface Anim { key: string; label: string }
export interface Ach { world: number; cat: string; hidden: boolean; name: string; desc: string }
export interface Quest { world: number; name: string; desc: string; count: number }
export interface Drop { id: string; tex: string | null; name: string; chance?: string; note: string; bonus?: string }

export interface World {
  n: number; name: string; short: string; long: string; nums: { v: string; l: string }[];
  doll: DollColours; light: string; bg: string; block: string; tall: string | null; wide: string | null; banner?: string | null;
  boss: { id: string; name: string; hp: string; core: string; coreTex: string | null; coreName: string };
  mobs: { id: string; name: string; elite: boolean; tex: string | null }[];
  rule: string | null; tier: string; bossNote: string;
  seed: { id: string; tex: string | null; name: string; soil: string; cond: string; inputs: Ing[] } | null;
  station: { id: string; tex: string | null; name: string; note: string; make: Ing[]; recipes: Recipe[] } | null;
  surface?: Recipe[];
  items: Item[];
  armor: { pieces: { tex: string | null; name: string }[]; text: string } | null;
  structures: { role: string; names: string[] }[];
  gallery?: { src: string; caption: string }[];
  codex: Codex;
}

export interface CodexEntry {
  id: string; tex: string | null; name: string; kind: string; rarity?: string; effect: string;
  station: string | null; inputs: Ing[]; count: number; drops: string[]; yields?: string | null;
}
export interface Codex {
  items: CodexEntry[]; blocks: CodexEntry[]; quests: { name: string; desc: string }[];
  ach: { cat: string; hidden: boolean; name: string; desc: string }[];
}

interface CreatureBase {
  id: string; name: string; en: string; fr: string; world: number; worldName: string; light: string; bg: string;
  doll: DollColours; hp: string; dmg: string; tex: string | null; anims: Anim[]; quests: Quest[]; ach: Ach[];
  prev: string | null; next: string | null; prevName: string | null; nextName: string | null;
}

export interface Mob extends CreatureBase {
  kind: "mob"; desc: string; tags: string[]; elite: boolean; hpRaw: number; dmgRaw: number;
  speedMult: string; attackEvery: string | null; attackTicks: number | null; moveSpeed: string;
  behaviour: string; facts: string[]; moves: { key: string; name: string; desc: string; cooldown: string }[]; drops: Drop[]; dropTex: string | null;
  spawn: { weight: number; share: string; min: number; max: number } | null;
}

export interface Boss extends CreatureBase {
  meet: import("../components/MeetBoss").Meet;
  kind: "boss"; phases: string; atks: { label: string; name: string }[]; timings: { label: string; v: string }[];
  cooldown: string[]; mp: { p: number; mult: string; hp: string }[]; drops: Drop[]; souls: string;
  unlocks: string[]; special: string[]; story: string; shot: string | null; block: string; coreTex: string | null;
}

export type Creature = Mob | Boss;

/* eslint-disable @typescript-eslint/no-explicit-any */
export interface SiteData {
  lang: Lang;
  copy: {
    ui: Record<string, string>;
    nav: Record<string, string>;
    home: any; worlds: any; bestiary: any; bosses: any; systems: any; download: any;
  };
  worlds: World[];
  mobs: Mob[];
  bosses: Boss[];
}

export interface Shared {
  version: string; repo: string; releases: string; wiki: string; site: string;
  icons: Record<string, string>; hasTrailer: boolean; hasReel: boolean;
}
