import { CreaturePage } from "@/components/pages/CreaturesPages";
import { allCreatureIds, creature, getData } from "@/lib/data";
import { meta } from "@/lib/meta";

export const dynamicParams = false;

export function generateStaticParams() {
  return allCreatureIds().map((id) => ({ id }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const c = creature("fr", id)!;
  const ui = getData("fr").copy.ui;
  return meta("fr", `creatures/${id}/`, `${c.name}, ${ui.sheet.toLowerCase()}`, c.kind === "mob" ? c.desc : c.phases);
}

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <CreaturePage lang={"fr"} id={id} />;
}
