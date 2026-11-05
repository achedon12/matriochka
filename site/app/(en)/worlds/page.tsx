import WorldsPage from "@/components/pages/WorldsPage";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("en", "worlds");

export default function Page() {
  return <WorldsPage lang={"en"} />;
}
