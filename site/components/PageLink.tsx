// next/link for the prerendered pages, a plain link for the reader page of the older versions (/v/?v=...):
// the reader reads its version and page from the address once, when it loads, so it is always loaded whole.
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
