import { WorldPage } from "@/components/pages/WorldsPage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";

export const dynamicParams = false;

export function generateStaticParams() {
  return Array.from({ length: 11 }, (_, i) => ({ n: String(i) }));
}

export async function generateMetadata({ params }: { params: Promise<{ n: string }> }) {
  const { n } = await params;
  const w = getData("en").worlds[Number(n)];
  return meta("en", `worlds/${n}/`, w.name, w.long);
}

export default async function Page({ params }: { params: Promise<{ n: string }> }) {
  const { n } = await params;
  return <WorldPage lang={"en"} n={Number(n)} />;
}
