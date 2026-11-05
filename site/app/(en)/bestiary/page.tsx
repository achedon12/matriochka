import { BestiaryPage } from "@/components/pages/CreaturesPages";
import { metaFor } from "@/lib/meta";

export const metadata = metaFor("en", "bestiary");

export default function Page() {
  return <BestiaryPage lang={"en"} />;
}
