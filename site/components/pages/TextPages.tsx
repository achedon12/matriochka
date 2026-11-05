/* eslint-disable @typescript-eslint/no-explicit-any */
import { getData, SHARED } from "@/lib/data";
import type { Lang } from "@/lib/types";
import { Icon, Ingredients, Inlay, Shot } from "../Bits";
import { Lacquer, Vine } from "../Ornament";
import { PageHead, Shell } from "../Shell";

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
      <PageHead title={s.h} lead={s.lead}>
        <nav className="subnav" aria-label={s.onPage}>
          <ul>{s.toc.map(([id, l]: [string, string]) => <li key={id}><a href={`#${id}`}>{l}</a></li>)}</ul>
        </nav>
      </PageHead>
      <Vine className="vine-sep" />
      <div className="wrap longform">
        <Lacquer>
          <section id="survival" className="sect">
            <h2>{s.survivalH}</h2>
            <div className="cols">
              <div>
                <Feature f={s.lifeDoll} />
                <h3>{s.deathH}</h3>
                <ol className="numbered">{s.death.map((x: string) => <li key={x}>{x}</li>)}</ol>
              </div>
              <div>{s.features.map((f: any) => <Feature key={f.h} f={f} />)}</div>
            </div>
          </section>
          <hr className="orn-rule" />
          <section id="souls" className="sect">
            <h2>{s.soulsH}</h2>
            <p className="sect-lead">{s.soulsLead}</p>
            <div className="cols">
              <div>
                <Table cols={s.rarCols} rows={s.rarity.map((r: any) => [r.k, r.v])} />
                <p className="small">{s.karmaNote}</p>
                <Shot src={s.altarShot.src} caption={s.altarShot.caption} />
              </div>
              <div>
                <h3>{s.karmaH}</h3>
                <ul className="karma">{s.karma.map((k: any) => <li key={k.v}><span className="num">{k.v}</span><p>{k.p}</p></li>)}</ul>
                <p className="small">{s.karmaEnd}</p>
              </div>
            </div>
          </section>
          <hr className="orn-rule" />
          <section id="classes" className="sect">
            <h2>{s.classesH}</h2>
            <p className="sect-lead">{s.classesLead}</p>
            <Table cols={s.clsCols} rows={s.classes.map((c: any) => [c.name, c.bonus, c.slot])} />
            <div className="cols">
              <div><h3>{s.upH}</h3><Table cols={s.upCols} rows={s.up.map((u: any) => [u.lv, u.bonus, u.souls])} /><p className="small">{s.upNote}</p></div>
              <div><h3>{s.capH}</h3><Table cols={s.capCols} rows={s.cap.map((c: any) => [c.k, c.v])} /></div>
            </div>
            <div className="cols">
              <Feature f={s.chance} />
              <Shot src={s.classShot.src} caption={s.classShot.caption} />
            </div>
          </section>
          <hr className="orn-rule" />
          <section id="nesting" className="sect">
            <h2>{s.nestingH}</h2>
            <p className="sect-lead">{s.nestingLead}</p>
            <Table cols={s.nestCols} rows={s.nest.map((n: any) => [n.a, n.b, n.c])} />
            <h3>{s.gatesH}</h3>
            <ul className="plain">{s.gates.map((g: string) => <li key={g}>{g}</li>)}</ul>
          </section>
          <hr className="orn-rule" />
          <section id="groups" className="sect">
            <h2>{s.groupsH}</h2>
            <p className="sect-lead">{s.groupsLead}</p>
            <div className="tbl"><table><tbody>{s.cmds.map((c: any) => <tr key={c.c}><th scope="row"><code>{c.c}</code></th><td>{c.d}</td></tr>)}</tbody></table></div>
            <p className="small">{s.serverNote}</p>
          </section>
          <hr className="orn-rule" />
          <section id="journal" className="sect">
            <h2>{s.journalH}</h2>
            <p className="sect-lead">{s.journalLead}</p>
            <div className="cols">{s.journalShots.map((j: any) => <Shot key={j.src} src={j.src} caption={j.caption} />)}</div>
            <h3>{s.titlesH}</h3>
            <ul className="titles">{s.titles.map((x: string) => <li key={x}>{x}</li>)}</ul>
          </section>
        </Lacquer>
      </div>
    </Shell>
  );
}

export function DownloadPage({ lang }: { lang: Lang }) {
  const s = getData(lang).copy.download;
  return (
    <Shell lang={lang} path="download/" section="download">
      <PageHead title={s.h} lead={s.lead} />
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
