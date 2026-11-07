import { ItemsPage } from "@/components/pages/ItemsPage";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("en", "items");

export default function Page() {
  return <ItemsPage lang={"en"} />;
}
