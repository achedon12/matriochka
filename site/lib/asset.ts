// What client components may import: no page data here, only the shared settings and the asset paths.
import shared from "@/data/shared.json";
import { BASE } from "./config";
import type { Shared } from "./types";

export const SHARED = shared as Shared;

/** A file in site/public, with the base path the site is served from. */
export function asset(p: string): string {
  return `${BASE}/${p}`;
}
