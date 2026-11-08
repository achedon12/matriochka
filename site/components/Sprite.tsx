"use client";
// All symbols and patterns, once per page (kept out of layout so patterns render in every browser). A client
// component without props: the page's HTML has the markup, its navigation payload only a reference to it.
import { SPRITE } from "./Ornament";

export default function Sprite() {
  return (
    <svg className="sprite" aria-hidden="true" focusable="false" width="0" height="0">
      <defs dangerouslySetInnerHTML={{ __html: SPRITE }} />
    </svg>
  );
}
