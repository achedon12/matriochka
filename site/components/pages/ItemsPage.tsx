import { getData } from "@/lib/data";
import type { CodexEntry, Lang } from "@/lib/types";
import { history, mark } from "@/lib/versions";
import ItemsCatalog from "../ItemsCatalog";
import { PageHead, Shell } from "../Shell";

export function ItemsPage({ lang, v }: { lang: Lang; v?: string }) {
  const d = getData(lang, v);
  const c = d.copy.items;
  // each entry carries its badge and its history in the version shown
  const dated = (e: CodexEntry) => ({ ...e, mark: mark(`item:${e.id}`, v), hist: history(`item:${e.id}`, v) });
  const worlds = d.catalog.map((k) => {
    const w = d.worlds.find((x) => x.n === k.n)!;
    return { ...k, items: k.items.map(dated), blocks: k.blocks.map(dated), doll: w.doll, light: w.light };
  });
  return (
    <Shell lang={lang} path="items/" section="items" v={v}>
      <PageHead title={c.h} lead={c.lead} />
      <div className="mx-auto w-full max-w-[1320px] px-4 pb-20 md:px-8">
        <ItemsCatalog worlds={worlds} c={c} vl={d.copy.versions} />
      </div>
    </Shell>
  );
}
