import { WorldPage } from "@/components/pages/WorldsPage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { VERSION_PARAMS } from "@/lib/versions";

export const dynamicParams = false;

export function generateStaticParams() {
  return VERSION_PARAMS.flatMap((ver) => getData("en", ver).worlds.map((w) => ({ ver, n: String(w.n) })));
}

export async function generateMetadata({ params }: { params: Promise<{ ver: string; n: string }> }) {
  const { ver, n } = await params;
  const w = getData("en", ver).worlds[Number(n)];
  return meta("en", `worlds/${n}/`, w.name, w.long, ver);
}

export default async function Page({ params }: { params: Promise<{ ver: string; n: string }> }) {
  const { ver, n } = await params;
  return <WorldPage lang={"en"} n={Number(n)} v={ver} />;
}
