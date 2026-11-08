#!/usr/bin/env python3
"""Exports the site data of every released version of the mod, so the website can show each one.

Usage: python3 tools/site_versions.py [--force] [--only 0.6.0]
       (run by `npm run build` in site/, through scripts/build-data.mjs, after tools/site.py)

For every release tag (vX.Y.Z), the tag's own tree is extracted into a temporary folder (text files only: no
sounds), and that tag's own tools/site.py builds its data there, with its asset step replaced by a listing of the
pictures already in site/public: the pictures are shared with the current site, and a picture that no longer
exists is left out (the page shows an empty slot). The result is stored in site/data/versions/<version>/, once:
a version already there is not built again (--force rebuilds them). A tag whose site.py fails is recorded with
a note and left out of the site; the build goes on.

Then, every run, from those versions and the current tree (site/data/{en,fr}.json, the version in
gradle.properties), it writes:
  site/data/versions.json   the versions (newest first), the Minecraft versions each runs on, what has a page in each
  site/data/history.json    when every item, block, creature, world and place appeared and changed
  site/data/changes.json    each version's section of CHANGELOG.md, with links to what it names
  site/public/versions/<version>/{en,fr}.json.gz, history.json.gz, changes.json.gz
                            what the reader page of the older versions (/v/?v=<version>) fetches: gzip, about
                            75 KB a language, unpacked in the browser
"""
import gzip
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import webp  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "site", "data")
PUBLIC = os.path.join(ROOT, "site", "public")
OUT = os.path.join(DATA, "versions")  # the store of built versions (not in git)
PUBLISHED = os.path.join(PUBLIC, "versions")  # what the reader page fetches (not in git)
# bump when the stored files change shape, so every version is built again
SCHEMA = 2
# what a tag's site.py reads; the sounds are left out, they are most of the weight and never read
PATHS = ["tools", "src/main", "gradle.properties", "versions"]


def vkey(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if check and r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors="replace").strip())
    return r.stdout


def current_version():
    for line in open(os.path.join(ROOT, "gradle.properties"), encoding="utf-8"):
        if line.startswith("mod_version="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("site_versions.py: no mod_version in gradle.properties")


def tags():
    try:
        out = git("tag", "-l", "v*").decode().split()
    except (RuntimeError, OSError):
        return []
    return sorted((t for t in out if re.fullmatch(r"v\d+\.\d+\.\d+", t)), key=vkey)


def mc_versions(tree):
    """Minecraft versions a tree builds for: its versions/<mc>/ folders, or gradle.properties' minecraft_version."""
    d = os.path.join(tree, "versions")
    if os.path.isdir(d):
        found = [f for f in os.listdir(d) if re.fullmatch(r"\d+(\.\d+)+", f) and os.path.isdir(os.path.join(d, f))]
        if found:
            return sorted(found, key=vkey)
    for line in open(os.path.join(tree, "gradle.properties"), encoding="utf-8"):
        if line.startswith("minecraft_version="):
            return [line.split("=", 1)[1].strip()]
    return []


def tag_date(tag):
    try:
        return git("log", "-1", "--format=%as", tag).decode().strip()
    except RuntimeError:
        return None


# ---------------------------------------------------------------- one tag's data, in a child process
def run_tree(tree):
    """Runs the site.py of an extracted tree, without its asset step: the picture sets that step fills are read
    from the current site/public instead (the names are the same: one file per item, block or entity id)."""
    tools = os.path.join(tree, "tools")
    sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("matriochka_site", os.path.join(tools, "site.py"))
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)

    def names(sub, suffix):
        # the site's pictures may be WebP now: an older site.py still builds ".png" paths, set right in publish()
        d = os.path.join(PUBLIC, sub)
        sufs = (suffix, ".webp") if suffix in (".png", ".jpg") else (suffix,)
        return {f.rsplit(".", 1)[0] for f in os.listdir(d) if f.endswith(sufs)} if os.path.isdir(d) else set()

    def listed_assets():
        for attr, sub, suffix in (("ITEM_TEX", "items", ".png"), ("ENTITY_TEX", "entities", ".png"),
                                  ("BLOCK_TEX", "blocks", ".png"), ("STATION_IMG", "stations", ".png"),
                                  ("CUBE_TEX", "cubes", ".png"), ("MOVES", "shots/moves", ".webp")):
            if isinstance(getattr(S, attr, None), set):
                getattr(S, attr).update(names(sub, suffix))
        if isinstance(getattr(S, "VANILLA_TEX", None), set):
            S.VANILLA_TEX.update("minecraft:" + n for n in names("vanilla", ".png"))
        if isinstance(getattr(S, "SHOTS", None), dict):
            d = os.path.join(PUBLIC, "shots")
            for f in os.listdir(d) if os.path.isdir(d) else []:
                if os.path.isfile(os.path.join(d, f)):
                    S.SHOTS[f.rsplit(".", 1)[0]] = f

    S.copy_assets = listed_assets
    if hasattr(S, "check_boss_anims"):
        S.check_boss_anims = lambda: None
    S.main()


# ---------------------------------------------------------------- old data in the current shape
# keys whose value is a file of site/public; an old one the current site no longer has is dropped
PICTURE_KEYS = {"tex", "img", "shot", "coreTex", "stationTex", "dropTex", "tall", "wide", "banner", "hud", "src", "headImg", "heroImg"}


def _pictures(x):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in PICTURE_KEYS and isinstance(v, str) and re.search(r"\.(png|jpe?g|webp)$", v):
                w = webp.paths(v, PUBLIC)
                x[k] = w if os.path.exists(os.path.join(PUBLIC, w)) else None
            else:
                _pictures(v)
    elif isinstance(x, list):
        for v in x:
            _pictures(v)


def normalize(d, lang):
    """An older version's data in the shape the current pages read. Only structure is filled in here: the words
    an older version lacks (labels of newer pages) are taken from the current data when the site loads it."""
    _pictures(d)
    stations = {}
    for w in d["worlds"]:
        for e in w["codex"]["items"] + w["codex"]["blocks"]:
            if e.get("kind") == "station":
                stations[e["name"]] = (e["id"], e.get("tex"))
    for w in d["worlds"]:
        for e in w["codex"]["items"] + w["codex"]["blocks"]:
            if "stationId" not in e:
                sid, stex = stations.get(e.get("station"), (None, None))
                e["stationId"], e["stationTex"] = sid, stex
            e.setdefault("drops", [])
            e.setdefault("inputs", [])
            e.setdefault("count", 1)
    if "catalog" not in d:
        d["catalog"] = [dict(n=w["n"], name=w["name"], items=w["codex"]["items"], blocks=w["codex"]["blocks"]) for w in d["worlds"]]
    for b in d["bosses"]:
        b.setdefault("moves", [])
        b.setdefault("passive", [])
    return d


# ---------------------------------------------------------------- building the missing versions
def build_tag(tag, dest):
    tmp = tempfile.mkdtemp(prefix="matriochka-" + tag + "-")
    try:
        tar = os.path.join(tmp, "tree.tar")
        present = [p for p in PATHS if git("ls-tree", "--name-only", tag, "--", p).strip()]
        with open(tar, "wb") as f:
            f.write(git("archive", "--format=tar", tag, "--", *present, ":(exclude)*.ogg"))
        tree = os.path.join(tmp, "tree")
        os.makedirs(tree)
        subprocess.run(["tar", "-xf", tar, "-C", tree], check=True)
        os.remove(tar)
        meta = dict(version=tag[1:], tag=tag, date=tag_date(tag), mc=mc_versions(tree), schema=SCHEMA)
        os.makedirs(dest, exist_ok=True)
        if not git("ls-tree", "--name-only", tag, "--", "site/package.json").strip():
            # before the Next.js site, site.py wrote static HTML pages: there is no data to read from them
            meta.update(ok=False, reason="static", note="its site.py writes static HTML pages, not the data of this site", ids=lang_ids(tree))
            json.dump(meta, open(os.path.join(dest, "meta.json"), "w", encoding="utf-8"), indent=1)
            return meta
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--run-tree", tree], cwd=tree,
                           capture_output=True, text=True)
        out = os.path.join(tree, "site", "data")
        files = {n: os.path.join(out, n + ".json") for n in ("en", "fr", "shared")}
        os.makedirs(dest, exist_ok=True)
        if r.returncode != 0 or not all(os.path.exists(p) for p in files.values()):
            tail = (r.stderr or r.stdout).strip().splitlines()[-3:]
            meta.update(ok=False, reason="failed", note="site.py of this tag failed: " + " / ".join(x.strip() for x in tail), ids=lang_ids(tree))
            for n in ("en", "fr", "shared"):
                if os.path.exists(os.path.join(dest, n + ".json")):
                    os.remove(os.path.join(dest, n + ".json"))
        else:
            for lang in ("en", "fr"):
                d = json.load(open(files[lang], encoding="utf-8"))
                json.dump(normalize(d, lang), open(os.path.join(dest, lang + ".json"), "w", encoding="utf-8"),
                          ensure_ascii=False, separators=(",", ":"))
            shutil.copy2(files["shared"], os.path.join(dest, "shared.json"))
            meta.update(ok=True)
        json.dump(meta, open(os.path.join(dest, "meta.json"), "w", encoding="utf-8"), indent=1)
        return meta
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def lang_ids(tree):
    """What a tree's English lang file names: its items, blocks, creatures and structures, as history keys."""
    p = os.path.join(tree, "src/main/resources/assets/matriochka/lang/en_us.json")
    if not os.path.exists(p):
        return []
    kinds = {"item": "item", "block": "item", "entity": "mob", "structure": "site"}
    out = set()
    for k in json.load(open(p, encoding="utf-8")):
        m = re.fullmatch(r"(item|block|entity|structure)\.matriochka\.(\w+)", k)
        if m:
            out.add(kinds[m.group(1)] + ":" + m.group(2))
    return sorted(out)


def stored(dest, ok=False):
    p = os.path.join(dest, "meta.json")
    if not os.path.exists(p):
        return None
    meta = json.load(open(p, encoding="utf-8"))
    if meta.get("schema") != SCHEMA or (ok and not meta.get("ok")):
        return None
    return meta


# ---------------------------------------------------------------- what appeared and changed, version by version
def _norm(s):
    """A value as compared between versions: the spaces and separators an older formatter used do not count."""
    if isinstance(s, str):
        return re.sub(r"[\s  ,]+", "", s).lower()
    if isinstance(s, (list, tuple)):
        return tuple(_norm(x) for x in s)
    return s


def facets(d):
    """key -> {facet: value} for everything with a page or a card, from one version's English data. A facet
    missing from a version (an older site.py did not export it) is never counted as a change."""
    out = {}
    for w in d["catalog"]:
        for e in w["items"] + w["blocks"]:
            f = dict(effect=e.get("effect") or "", rarity=e.get("rarity") or "",
                     recipe=(e.get("stationId") or e.get("station"), sorted((i["id"], i["n"]) for i in e.get("inputs", [])), e.get("count", 1)),
                     source=(sorted(e.get("drops", [])), e.get("yields") or ""))
            if "stats" in e:
                f["stats"] = [(s["k"], s["v"]) for s in e["stats"]]
            out["item:" + e["id"]] = f
    for m in d["mobs"]:
        out["mob:" + m["id"]] = dict(health=m["hp"], damage=m["dmg"], speed=(m.get("speedMult"), m.get("moveSpeed")),
                                    moves=[(x["name"], x.get("cooldown")) for x in m.get("moves", [])],
                                    drops=[(x["id"], x.get("chance"), x.get("note")) for x in m.get("drops", [])],
                                    spawn=m.get("spawn") and (m["spawn"]["weight"], m["spawn"]["min"], m["spawn"]["max"]))
    for b in d["bosses"]:
        f = dict(health=b["hp"], damage=b["dmg"], phases=b.get("phases"), attacks=[a["name"] for a in b.get("atks", [])],
                 drops=[(x["id"], x.get("note")) for x in b.get("drops", [])])
        out["mob:" + b["id"]] = f
    for w in d["worlds"]:
        f = dict(rule=w.get("rule") or "", creatures=sorted(m["id"] for m in w.get("mobs", [])), boss=w["boss"]["id"])
        if "sites" in w:
            f["structures"] = sorted(s["id"] for s in w["sites"])
            for s in w["sites"]:
                out["site:" + s["id"]] = dict(desc=s.get("desc"), inside=s.get("inside"), size=s.get("size"), rarity=s.get("rarity"))
        out["world:" + str(w["n"])] = f
    return out


def history(series):
    """series: [(version, facets or None, ids or None)] oldest first; a version left out of the site may still
    give the ids its lang file names. key -> {since, changes: [{v, f: [facets]}]}. "since" is the first version
    known to have it, or None when that cannot be told (it was there in the first version with data, and no
    older version names that kind of thing)."""
    hist, prev, known = {}, None, set()
    for v, cur, ids in series:
        if cur is None:  # only the ids: they tell when things first appeared, not what changed
            for k in ids or ():
                hist.setdefault(k, dict(since=v, changes=[]))
            known |= {k.split(":")[0] for k in ids or ()}
            continue
        for k, f in cur.items():
            if k not in hist:
                first = prev is None and k.split(":")[0] not in known
                hist[k] = dict(since=None if first else v, changes=[])
            if prev is None or k not in prev:
                continue
            changed = [n for n, x in f.items() if n in prev[k] and _norm(x) != _norm(prev[k][n])]
            if changed:
                hist[k]["changes"].append(dict(v=v, f=changed))
        prev = cur
    return hist


# ---------------------------------------------------------------- CHANGELOG.md, one section per version
WIKI = "https://github.com/achedon12/matriochka/wiki/"
REPO = "https://github.com/achedon12/matriochka/blob/main/"


def targets(d):
    """English name -> path of its page in one version (paths without language or version prefix)."""
    t = {}
    for w in d["worlds"]:
        for s in w.get("sites", []):
            t.setdefault(s["name"], f"worlds/{w['n']}/#site-{s['id']}")
    for w in d["catalog"]:
        for e in w["items"] + w["blocks"]:
            t.setdefault(e["name"], f"items/#{e['id']}")
    for m in d["mobs"] + d["bosses"]:
        t[m["name"]] = f"creatures/{m['id']}/"
    for w in d["worlds"]:
        t[w["name"]] = f"worlds/{w['n']}/"
        if w["n"]:
            t[f"World {w['n']}"] = f"worlds/{w['n']}/"
    # "the Sleeping Giant" in a sentence names "The Sleeping Giant"
    for k, v in list(t.items()):
        if k.startswith("The "):
            t.setdefault(k[4:], v)
    return {k: v for k, v in t.items() if len(k) >= 4}


def inline(text, names, used):
    """Markdown of one line -> segments: [kind, text, href?] with kind t (text), c (code), b (bold), a (link out),
    r (a page of the site, its first mention in the block)."""
    segs = []
    for m in re.finditer(r"`([^`]+)`|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|([^`*\[]+|[`*\[])", text):
        if m.group(1):
            segs.append(["c", m.group(1)])
        elif m.group(2):
            segs.append(["b", m.group(2)])
        elif m.group(3):
            url = m.group(4)
            if url.startswith("docs-wiki-drafts/"):
                url = WIKI + url[len("docs-wiki-drafts/"):].removesuffix(".md")
            elif not re.match(r"https?://", url):
                url = REPO + url
            segs.append(["a", m.group(3), url])
        else:
            segs.extend(_refs(m.group(5), names, used))
    out = []
    for s in segs:  # glue runs of plain text back together
        if out and s[0] == "t" and out[-1][0] == "t":
            out[-1][1] += s[1]
        else:
            out.append(s)
    return out


def _refs(text, names, used):
    if not names:
        return [["t", text]]
    rx = names["rx"]
    out, i = [], 0
    for m in rx.finditer(text):
        path = names["map"][m.group(0)]
        if path in used:
            continue
        used.add(path)
        out.append(["t", text[i:m.start()]])
        out.append(["r", m.group(0), path])
        i = m.end()
    out.append(["t", text[i:]])
    return [s for s in out if s[1]]


def changelog(path, data_of):
    """version -> {title, lead, blocks}; blocks are [h, segs] headings, [p, segs] paragraphs and [ul, [[segs, [sub segs]]]]."""
    if not os.path.exists(path):
        return {}
    out, cur = {}, None
    for raw in open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^## (\d+\.\d+\.\d+)\s*(.*)$", raw)
        if m:
            v = m.group(1)
            d = data_of(v)
            names = None
            if d is not None:
                mp = targets(d)
                rx = re.compile(r"(?<![\w'])(" + "|".join(re.escape(k) for k in sorted(mp, key=len, reverse=True)) + r")(?![\w])")
                names = dict(map=mp, rx=rx)
            cur = out[v] = dict(title=m.group(2).strip("() "), lead=[], blocks=[], names=names)
            continue
        if cur is None or not raw.strip():
            continue
        h = re.match(r"^###\s+(.*)$", raw)
        sub = re.match(r"^\s{2,}[-*]\s+(.*)$", raw)
        li = re.match(r"^[-*]\s+(.*)$", raw)
        used = set()
        if h:
            cur["blocks"].append(["h", h.group(1).strip()])
        elif sub and cur["blocks"] and cur["blocks"][-1][0] == "ul":
            cur["blocks"][-1][1][-1][1].append(inline(sub.group(1), cur["names"], used))
        elif li:
            if not cur["blocks"] or cur["blocks"][-1][0] != "ul":
                cur["blocks"].append(["ul", []])
            cur["blocks"][-1][1].append([inline(li.group(1), cur["names"], used), []])
        elif not cur["blocks"]:
            cur["lead"].append(inline(raw.strip(), cur["names"], used))
        else:
            cur["blocks"].append(["p", inline(raw.strip(), cur["names"], used)])
    for v in out.values():
        v.pop("names")
    return out


def main(argv):
    if "--run-tree" in argv:
        run_tree(argv[argv.index("--run-tree") + 1])
        return
    force = "--force" in argv
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    cur = current_version()
    os.makedirs(OUT, exist_ok=True)
    metas = []
    for tag in tags():
        v = tag[1:]
        if vkey(v) >= vkey(cur):  # the current tree is that version, or a newer one is tagged ahead of it
            continue
        dest = os.path.join(OUT, v)
        meta = None if force and (only in (None, v)) else stored(dest)
        if meta is None:
            print(f"site_versions.py: building {v} from {tag}", flush=True)
            meta = build_tag(tag, dest)
            if not meta["ok"]:
                print(f"site_versions.py: {v} left out, {meta['note']}", file=sys.stderr)
        metas.append(meta)
    write_indexes(cur, metas)
    print(f"site_versions.py: {sum(m['ok'] for m in metas)} older versions, {sum(not m['ok'] for m in metas)} left out")


def pages_of(d):
    """What has its own page in one version: the creatures (bosses apart) and the worlds."""
    return dict(creatures=[m["id"] for m in d["mobs"]], bosses=[b["id"] for b in d["bosses"]], worlds=[w["n"] for w in d["worlds"]])


def publish(d, cur):
    """An older version's data as the reader page fetches it: the words it lacks (pages and labels added since)
    taken from the current data, its own words winning wherever it has them, and no catalogue (the reader
    rebuilds it from the worlds)."""
    c, k = d["copy"], cur["copy"]
    copy = {**k, **c, "ui": {**k["ui"], **c["ui"]}, "nav": {**k["nav"], **c["nav"]},
            "items": {**k["items"], **c.get("items", {})}, "versions": k["versions"]}
    out = {key: v for key, v in d.items() if key != "catalog"}
    out["copy"] = copy
    return webp.paths(out, PUBLIC)  # the pictures as the site now has them (WebP)


def write_gz(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # mtime 0: the same data gives the same file, run after run
    with open(path, "wb") as f:
        f.write(gzip.compress(raw, 9, mtime=0))


def write_indexes(cur, metas):
    """versions.json, history.json and changes.json (site/data, read by the latest pages), and what the reader
    page fetches (site/public/versions), from the stored versions and the current tree's data."""
    latest = {}
    for lang in ("en", "fr"):
        p = os.path.join(DATA, lang + ".json")
        if not os.path.exists(p):
            raise SystemExit("site_versions.py: run tools/site.py first (no site/data/%s.json)" % lang)
        latest[lang] = json.load(open(p, encoding="utf-8"))
    cur_tag = "v" + cur if "v" + cur in tags() else None
    entries = [dict(v=cur, mc=mc_versions(ROOT), date=tag_date(cur_tag) if cur_tag else None, released=bool(cur_tag),
                    latest=True, **pages_of(latest["en"]))]
    loaded = {cur: latest["en"]}

    def data_of(v, lang="en"):
        key = v if lang == "en" else v + "/" + lang
        if key not in loaded:
            p = os.path.join(OUT, v, lang + ".json")
            loaded[key] = json.load(open(p, encoding="utf-8")) if os.path.exists(p) and stored(os.path.join(OUT, v), ok=True) else None
        return loaded[key]

    published = set()
    for m in sorted(metas, key=lambda m: vkey(m["version"]), reverse=True):
        if m["ok"] and data_of(m["version"]) is not None:
            v = m["version"]
            entries.append(dict(v=v, mc=m["mc"], date=m["date"], released=True, latest=False, **pages_of(data_of(v))))
            for lang in ("en", "fr"):
                write_gz(os.path.join(PUBLISHED, v, lang + ".json.gz"), publish(data_of(v, lang), latest[lang]))
            published.add(v)
    # versions no longer shown (a tag moved, or the current tree reached it) leave the published files
    if os.path.isdir(PUBLISHED):
        for f in os.listdir(PUBLISHED):
            if os.path.isdir(os.path.join(PUBLISHED, f)) and f not in published:
                shutil.rmtree(os.path.join(PUBLISHED, f))
    index = dict(latest=cur, versions=entries,
                 skipped=[dict(v=m["version"], mc=m["mc"], date=m["date"], reason=m.get("reason", "failed"), note=m["note"]) for m in metas if not m["ok"]])

    series = []
    for m in sorted(metas, key=lambda m: vkey(m["version"])):
        d = data_of(m["version"]) if m["ok"] else None
        series.append((m["version"], facets(d) if d else None, None if d else m.get("ids")))
    series.append((cur, facets(latest["en"]), None))
    hist = {k: h for k, h in history(series).items() if h["since"] or h["changes"]}
    changes = changelog(os.path.join(ROOT, "CHANGELOG.md"), data_of)
    for name, obj in (("versions", index), ("history", hist), ("changes", changes)):
        with open(os.path.join(DATA, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    write_gz(os.path.join(PUBLISHED, "history.json.gz"), hist)
    write_gz(os.path.join(PUBLISHED, "changes.json.gz"), changes)



if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main(sys.argv[1:])
