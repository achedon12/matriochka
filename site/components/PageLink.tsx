// next/link for the latest pages, a plain link for an older version's (/v/<version>/): those pages load whole,
// so their navigation payloads are not published (scripts/trim-versions.mjs), which keeps the site small
// however many versions it shows.
import Link from "next/link";
import type { ComponentProps } from "react";
import { BASE } from "@/lib/config";

export default function PageLink({ href, ...rest }: ComponentProps<typeof Link>) {
  if (typeof href === "string" && /^\/(fr\/)?v\//.test(href)) {
    const { prefetch: _p, replace: _r, scroll: _s, ...a } = rest; // eslint-disable-line @typescript-eslint/no-unused-vars
    return <a href={BASE + href} {...a} />;
  }
  return <Link href={href} {...rest} />;
}
