import { SystemsPage } from "@/components/pages/TextPages";
import { metaFor } from "@/lib/meta";
import { VERSION_PARAMS } from "@/lib/versions";

export const dynamicParams = false;

export function generateStaticParams() {
  return VERSION_PARAMS.map((ver) => ({ ver }));
}

export async function generateMetadata({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  return metaFor("en", "systems", ver);
}

export default async function Page({ params }: { params: Promise<{ ver: string }> }) {
  const { ver } = await params;
  return <SystemsPage lang={"en"} v={ver} />;
}
