import { getData } from "@/lib/data";
import type { Lang } from "@/lib/types";
import ItemsCatalog from "../ItemsCatalog";
import { PageHead, Shell } from "../Shell";

export function ItemsPage({ lang }: { lang: Lang }) {
  const d = getData(lang);
  const c = d.copy.items;
  const worlds = d.catalog.map((k) => {
    const w = d.worlds.find((x) => x.n === k.n)!;
    return { ...k, doll: w.doll, light: w.light };
  });
  return (
    <Shell lang={lang} path="items/" section="items">
      <PageHead title={c.h} lead={c.lead} />
      <div className="mx-auto w-full max-w-[1320px] px-4 pb-20 md:px-8">
        <ItemsCatalog worlds={worlds} c={c} />
      </div>
    </Shell>
  );
}
