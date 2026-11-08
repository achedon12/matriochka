import { ChangesPage } from "@/components/pages/ChangesPage";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";
import { LATEST } from "@/lib/versions";

const l = getData("fr").copy.versions;
export const metadata = meta("fr", "changes/", l.changesH.replace("{v}", LATEST), l.desc);

export default function Page() {
  return <ChangesPage lang={"fr"} />;
}
