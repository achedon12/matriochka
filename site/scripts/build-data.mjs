// Prebuild step: runs tools/site.py, which reads the mod's sources (content table, lang files, recipes,
// biome spawn tables, GeckoLib models and animations, branding, screenshots) and writes site/data/*.json
// plus the files the pages show into site/public.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..", "..");
const script = join(root, "tools", "site.py");
const python = process.env.PYTHON || "python3";

const r = spawnSync(python, [script], { stdio: "inherit", cwd: root });
if (r.status !== 0) {
  if (existsSync(join(here, "..", "data", "en.json"))) {
    console.warn("tools/site.py failed; building with the data already in site/data");
  } else {
    process.exit(r.status ?? 1);
  }
}
