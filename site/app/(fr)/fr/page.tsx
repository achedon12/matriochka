import HomePage from "@/components/pages/HomePage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";

export const metadata = meta("fr", "", null, getData("fr").copy.home.desc);

export default function Page() {
  return <HomePage lang={"fr"} />;
}
