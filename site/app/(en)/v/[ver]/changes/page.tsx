import { ChangesPage } from "@/components/pages/ChangesPage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { VERSION_PARAMS } from "@/lib/versions";

export const dynamicParams = false;

export function generateStaticParams() {
  return VERSION_PARAMS.map((ver) => ({ ver }));
}

export async function generateMetadata({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  const l = getData("en", ver).copy.versions;
  return meta("en", "changes/", l.changesH.replace("{v}", ver), l.desc, ver);
}

export default async function Page({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  return <ChangesPage lang={"en"} v={ver} />;
}
