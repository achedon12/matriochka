import Reader from "@/components/Reader";
import { getData } from "@/lib/data";
import { meta } from "@/lib/meta";

// every page of every older version, drawn in the browser from that version's data (/v/?v=0.6.0&p=items/)
const l = getData("fr").copy.versions;
export const metadata = { ...meta("fr", "v/", null, l.desc), robots: { index: false } };

export default function Page() {
  return <Reader lang={"fr"} labels={{ loading: l.loading, unknown: l.unknown, failed: l.failed, notIn: l.notIn, notInP: l.notInP, seeLatest: l.seeLatest }} />;
}
