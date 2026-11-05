import HomePage from "@/components/pages/HomePage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";

export const metadata = meta("en", "", null, getData("en").copy.home.desc);

export default function Page() {
  return <HomePage lang={"en"} />;
}
