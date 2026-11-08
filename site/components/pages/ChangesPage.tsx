import Link from "../PageLink";
import { Fragment } from "react";
import { getData, href } from "@/lib/data";
import type { Lang } from "@/lib/types";
import { changes, info, shown, SKIPPED, VERSIONS, type Seg } from "@/lib/versions";
import { Icon } from "../Bits";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";

/** One line of the changelog; a name of the site links to its page in the version shown. */
function Line({ segs, lang, v }: { segs: Seg[]; lang: Lang; v?: string }) {
  return (
    <>
      {segs.map((s, i) => {
        if (s[0] === "c") return <code key={i}>{s[1]}</code>;
        if (s[0] === "b") return <strong key={i}>{s[1]}</strong>;
        if (s[0] === "a") return <a key={i} href={s[2]}>{s[1]}</a>;
        if (s[0] === "r") return <Link key={i} className="ch-ref" href={href(lang, s[2], v)}>{s[1]}</Link>;
        return <Fragment key={i}>{s[1]}</Fragment>;
      })}
    </>
  );
}

export function ChangesPage({ lang, v }: { lang: Lang; v?: string }) {
  const d = getData(lang, v);
  const l = d.copy.versions;
  const ver = shown(v);
  const me = info(ver);
  const sec = changes(ver);
  return (
    <Shell lang={lang} path="changes/" v={v}>
      <PageHead title={l.changesH.replace("{v}", ver)} lead={l.changesLead}>
        <ul className="ch-facts">
          {me && me.mc.length > 0 && <li><Icon name="cpu" />{l.supports.replace("{mc}", me.mc.join(", "))}</li>}
          <li><Icon name="clock" />{me?.date ? l.released.replace("{d}", me.date) : l.unreleased}</li>
        </ul>
      </PageHead>
      <Vine className="vine-sep" />
      <div className="wrap longform">
        <Lacquer className="ch">
          {l.inEnglish && <p className="small" lang={lang}>{l.inEnglish}</p>}
          {!sec && <p>{l.noSection}</p>}
          {sec && (
            <div lang="en">
              {sec.lead.map((segs, i) => <p key={i} className="ch-lead"><Line segs={segs} lang={lang} v={v} /></p>)}
              {sec.blocks.map((b, i) => {
                if (b[0] === "h") return <h2 key={i} className="h-plate">{b[1]}</h2>;
                if (b[0] === "p") return <p key={i}><Line segs={b[1]} lang={lang} v={v} /></p>;
                return (
                  <ul key={i} className="ch-list">
                    {b[1].map(([segs, sub], j) => (
                      <li key={j}>
                        <Line segs={segs} lang={lang} v={v} />
                        {sub.length > 0 && <ul>{sub.map((x, k) => <li key={k}><Line segs={x} lang={lang} v={v} /></li>)}</ul>}
                      </li>
                    ))}
                  </ul>
                );
              })}
            </div>
          )}
        </Lacquer>
        <section aria-labelledby="ch-all">
          <h2 id="ch-all" className="h-plate">{l.allH}</h2>
          <ul className="ch-all">
            {VERSIONS.map((x) => (
              <li key={x.v}>
                <Link href={href(lang, "changes/", x.v)} aria-current={x.v === ver ? "page" : undefined}>
                  <span className="vp-v">{x.v}</span>
                  <span className="vp-mc">{x.mc.map((m) => <span key={m} className="vp-chip">{m}</span>)}</span>
                  <span className="vp-meta">{x.latest ? <strong>{l.latest}</strong> : x.date}</span>
                </Link>
              </li>
            ))}
            {SKIPPED.map((x) => (
              <li key={x.v} className="ch-off">
                <span className="vp-v">{x.v}</span>
                <span className="vp-mc">{x.mc.map((m) => <span key={m} className="vp-chip">{m}</span>)}</span>
                <span className="vp-meta">{l.notHere[x.reason] ?? l.notHere.failed}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </Shell>
  );
}
