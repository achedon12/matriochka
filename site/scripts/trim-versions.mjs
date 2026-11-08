// Postbuild step: the pages of the older versions (out/v/ and out/fr/v/) are reached by plain links
// (components/PageLink.tsx) and load whole, so the navigation payloads Next.js writes beside each of them
// (*.txt) are never read. Leaving them out halves the weight every version adds to the site.
import { existsSync, readdirSync, rmSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const out = join(dirname(fileURLToPath(import.meta.url)), "..", "out");
let n = 0;
let bytes = 0;

function trim(dir) {
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    const s = statSync(p);
    if (s.isDirectory()) trim(p);
    else if (f.endsWith(".txt")) {
      bytes += s.size;
      n += 1;
      rmSync(p);
    }
  }
}

for (const d of [join(out, "v"), join(out, "fr", "v")]) if (existsSync(d)) trim(d);
console.log(`trim-versions: ${n} navigation payloads of older versions left out (${(bytes / 1e6).toFixed(0)} MB)`);
