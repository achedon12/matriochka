import { SystemsPage } from "@/components/pages/TextPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("fr", "systems");

export default function Page() {
  return <SystemsPage lang={"fr"} />;
}
