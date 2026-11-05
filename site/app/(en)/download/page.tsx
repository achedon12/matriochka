import { DownloadPage } from "@/components/pages/TextPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("en", "download");

export default function Page() {
  return <DownloadPage lang={"en"} />;
}
