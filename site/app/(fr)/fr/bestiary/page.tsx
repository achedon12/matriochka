import { BestiaryPage } from "@/components/pages/CreaturesPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("fr", "bestiary");

export default function Page() {
  return <BestiaryPage lang={"fr"} />;
}
