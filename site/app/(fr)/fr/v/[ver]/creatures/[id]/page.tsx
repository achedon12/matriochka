import { CreaturePage } from "@/components/pages/CreaturesPages";
import { allCreatureIds, creature, getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { VERSION_PARAMS } from "@/lib/versions";

export const dynamicParams = false;

export function generateStaticParams() {
  return VERSION_PARAMS.flatMap((ver) => allCreatureIds(ver).map((id) => ({ ver, id })));
}

export async function generateMetadata({ params }: { params: Promise<{ ver: string; id: string }> }) {
  const { ver, id } = await params;
  const c = creature("fr", id, ver)!;
  const ui = getData("fr", ver).copy.ui;
  return meta("fr", `creatures/${id}/`, `${c.name}, ${ui.sheet.toLowerCase()}`, c.kind === "mob" ? c.desc : c.phases, ver);
}

export default async function Page({ params }: { params: Promise<{ ver: string; id: string }> }) {
  const { ver, id } = await params;
  return <CreaturePage lang={"fr"} id={id} v={ver} />;
}
