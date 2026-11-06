/* eslint-disable @typescript-eslint/no-explicit-any */
import { getData, SHARED } from "@/lib/data";
import type { Lang } from "@/lib/types";
import { Icon, Ingredients, Inlay, Shot } from "../Bits";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";
import SystemsTabs from "../SystemsTabs";

const NUMERIC = /^[+−×-]?[\d.,\u202f\u00a0 ]+%?$/;

function Table({ cols, rows }: { cols?: string[]; rows: (string | number)[][] }) {
  return (
    <div className="tbl">
      <table>
        {cols && <thead><tr>{cols.map((c) => <th scope="col" key={c}>{c}</th>)}</tr></thead>}
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>{r.map((v, j) => (j === 0 ? <th scope="row" key={j}>{v}</th> : <td key={j} className={NUMERIC.test(String(v)) ? "num" : undefined}>{v}</td>))}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Feature({ f }: { f: { tex: string; h: string; p: string; inputs?: any[] } }) {
  return (
    <div className="feature">
      <Inlay src={f.tex} size={48} />
      <div>
        <h3>{f.h}</h3>
        <p>{f.p}</p>
        {f.inputs && f.inputs.length > 0 && <Ingredients inputs={f.inputs} />}
      </div>
    </div>
  );
}

export function SystemsPage({ lang }: { lang: Lang }) {
  const s = getData(lang).copy.systems;
  return (
    <Shell lang={lang} path="systems/" section="systems">
      <PageHead title={s.h} lead={s.lead} img={s.headImg} />
      <div className="mx-auto w-full max-w-[1240px] px-4 py-12 md:px-8">
        <SystemsTabs s={s} />
      </div>
    </Shell>
  );
}

export function DownloadPage({ lang }: { lang: Lang }) {
  const s = getData(lang).copy.download;
  return (
    <Shell lang={lang} path="download/" section="download">
      <PageHead title={s.h} lead={s.lead} img={s.headImg} />
      <Vine className="vine-sep" />
      <div className="wrap longform dl">
        <Lacquer>
          <h2>Matriochka {SHARED.version}</h2>
          <ul className="sources">
            {s.sources.map((src: any) => (
              <li key={src.name}>
                {src.href ? (
                  <a className="src src-on" href={src.href}><Icon name="github" /><span><strong>{src.name}</strong><small>{src.note}</small></span><Icon name="download" className="ic ic-end" /></a>
                ) : (
                  <span className="src src-off" aria-disabled="true"><Icon name="package" /><span><strong>{src.name}</strong><small>{src.note}</small></span></span>
                )}
              </li>
            ))}
          </ul>
          <div className="cols">
            <div>
              <h3>{s.reqH}</h3>
              <ul className="reqs">{s.reqs.map((r: any) => <li key={r.n}><span className="req-n">{r.n}</span><span className="num">{r.v}</span><small>{r.s}</small></li>)}</ul>
            </div>
            <div>
              <h3>{s.installH}</h3>
              <ol className="numbered">{s.steps.map((x: string) => <li key={x}>{x}</li>)}</ol>
            </div>
          </div>
          <hr className="orn-rule" />
          <div className="cols cols-3">
            <section><h3><Icon name="info" />{s.lunarH}</h3><p>{s.lunar}</p></section>
            <section><h3><Icon name="book-open" />{s.wikiH}</h3><p>{s.wiki}</p><p><a className="quiet" href={SHARED.wiki}>{s.wikiBtn}</a></p></section>
            <section><h3><Icon name="circle-alert" />{s.earlyH}</h3><p>{s.early}</p><p><a className="quiet" href={`${SHARED.repo}/issues`}>{getData(lang).copy.ui.bug}</a></p></section>
          </div>
          <hr className="orn-rule" />
          <div className="cols cols-3">
            <section><h3><Icon name="package" />{s.packH}</h3><p>{s.pack}</p></section>
            <section><h3><Icon name="check" />{s.compatH}</h3><p>{s.compat}</p></section>
            <section><h3><Icon name="languages" />{s.langsH}</h3><p>{s.langs}</p></section>
          </div>
          <hr className="orn-rule" />
          <section>
            <h2>{s.cfgH}</h2>
            <p className="small">{s.cfgNote}</p>
            <div className="tbl"><table>
              <thead><tr>{s.cfgCols.map((c: string) => <th scope="col" key={c}>{c}</th>)}</tr></thead>
              <tbody>{s.cfg.map((c: any) => <tr key={c.k}><th scope="row"><code>{c.k}</code></th><td><code>{c.v}</code></td><td>{c.d}</td></tr>)}</tbody>
            </table></div>
          </section>
        </Lacquer>
      </div>
    </Shell>
  );
}
