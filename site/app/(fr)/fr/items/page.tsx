import { ItemsPage } from "@/components/pages/ItemsPage";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("fr", "items");

export default function Page() {
  return <ItemsPage lang={"fr"} />;
}
