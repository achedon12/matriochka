import { ChangesPage } from "@/components/pages/ChangesPage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { LATEST } from "@/lib/versions";

const l = getData("en").copy.versions;
export const metadata = meta("en", "changes/", l.changesH.replace("{v}", LATEST), l.desc);

export default function Page() {
  return <ChangesPage lang={"en"} />;
}
