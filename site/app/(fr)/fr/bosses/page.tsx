import { BossesPage } from "@/components/pages/CreaturesPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("fr", "bosses");

export default function Page() {
  return <BossesPage lang={"fr"} />;
}
