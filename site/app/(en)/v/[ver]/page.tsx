import HomePage from "@/components/pages/HomePage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { VERSION_PARAMS } from "@/lib/versions";

export const dynamicParams = false;

export function generateStaticParams() {
  return VERSION_PARAMS.map((ver) => ({ ver }));
}

export async function generateMetadata({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  return meta("en", "", null, getData("en", ver).copy.home.desc, ver);
}

export default async function Page({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  return <HomePage lang={"en"} v={ver} />;
}
