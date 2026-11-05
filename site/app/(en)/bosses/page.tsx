import { BossesPage } from "@/components/pages/CreaturesPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("en", "bosses");

export default function Page() {
  return <BossesPage lang={"en"} />;
}
