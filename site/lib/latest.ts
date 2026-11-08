// Server side only: hands the latest version's data, its history and the changelog sections to lib/data.ts
// and lib/versions.ts, for the prerendered pages. Imported by lib/meta.ts, which every page uses.
import en from "@/data/en.json";
import fr from "@/data/fr.json";
import hist from "@/data/history.json";
import changelog from "@/data/changes.json";
import { provide } from "./data";
import { LATEST, provideChanges, provideHistory, type ChangeSection, type Hist } from "./versions";
import type { SiteData } from "./types";

provide("en", LATEST, en as unknown as SiteData);
provide("fr", LATEST, fr as unknown as SiteData);
provideHistory(hist as unknown as Record<string, Hist>);
provideChanges(changelog as unknown as Record<string, ChangeSection>);
