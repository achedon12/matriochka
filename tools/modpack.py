#!/usr/bin/env python3
"""Builds the Matriochka Pack around the mod: a Modrinth modpack (.mrpack) or a CurseForge modpack (.zip).

Usage (from the repository root, after ./gradlew build):
    python3 tools/modpack.py                       # the jar in build/libs, the normal pack
    python3 tools/modpack.py --hard                # the hard pack (nightmare difficulty)
    python3 tools/modpack.py --jar path/to/matriochka.jar --mod-url https://.../matriochka.jar
    python3 tools/modpack.py --curseforge [--hard] [--cf-mod-file 9468136]   # the CurseForge pack

The pack holds the mod, its dependencies (Fabric API, GeckoLib), Just Enough Items as an optional client mod and
the client performance mods that exist for this Minecraft version on Modrinth, plus the files of
tools/modpack/overrides and a config/matriochka.json with the pack's settings. Versions pinned in
gradle.properties (Fabric API, GeckoLib, JEI) are used as is; the others take the newest release for the game
version (a beta only when the mod has no release for it). Required dependencies of every mod are added too.

Downloads and hashes come from the Modrinth API. When the API cannot be reached the script stops with an error
instead of writing an incomplete pack. Standard library only.

The CurseForge pack holds the same files: each jar of the Modrinth pack is downloaded, its CurseForge fingerprint
(MurmurHash2 of the jar without whitespace bytes) is looked up, and the CurseForge file with exactly those bytes goes
into manifest.json. A mod with no such approved file for this game version and Fabric is left out, with every mod
that needs it: CurseForge does not accept jars from elsewhere in a modpack. The lookup uses the official CurseForge
API when CURSEFORGE_API_KEY is set (a key from console.curseforge.com), else the public read-only mirror
api.curse.tools, which answers the same requests without a key.
"""
import argparse
import hashlib
import html
import io
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OVERRIDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modpack", "overrides")
API = "https://api.modrinth.com/v2"
USER_AGENT = "achedon12/matriochka modpack builder (github.com/achedon12/matriochka)"
REPO = "achedon12/matriochka"
# Modrinth only accepts these hosts in a pack's download list
ALLOWED_HOSTS = ("cdn.modrinth.com", "github.com", "raw.githubusercontent.com", "gitlab.com")

REQ, OPT, NO = "required", "optional", "unsupported"

# (Modrinth slug, gradle.properties key pinning its version or None, client, server, why)
PACK = [
    ("fabric-api", "fabric_api_version", REQ, REQ, "required by Matriochka"),
    ("geckolib", "geckolib_version", REQ, REQ, "required by Matriochka (models and animations)"),
    ("jei", "jei_version", OPT, NO, "recipe pages for every station (optional)"),
    ("sodium", None, REQ, NO, "rendering engine: much higher frame rate"),
    ("lithium", None, REQ, REQ, "game logic, physics and chunk ticking"),
    ("ferrite-core", None, REQ, REQ, "memory use"),
    ("entityculling", None, REQ, NO, "skips hidden creatures and block entities"),
    ("immediatelyfast", None, REQ, NO, "faster HUD, text and map rendering"),
    ("dynamic-fps", None, REQ, NO, "lowers the frame rate when the game is in the background"),
    ("krypton", None, REQ, REQ, "network stack"),
    ("modmenu", None, REQ, NO, "mod list and config screens"),
    ("iris", None, OPT, NO, "shaders (optional)"),
]
# Left out on purpose:
#   lambdynamiclights: a held torch would light the Lightless Deep (World 5) and defeat its rule
#   c2me-fabric, scalablelux: alpha builds only for 26.3
#   modernfix, memoryleakfix, noisium: no build for 26.3
EXCLUDED = {"lambdynamiclights", "c2me-fabric", "scalablelux"}

PACK_NAME = "Matriochka Pack"
AUTHOR = "achedon12"
CF_PROJECT = 1785262  # Matriochka on CurseForge
CF_GAME = 432  # Minecraft
CF_API = "https://api.curseforge.com/v1"
CF_MIRROR = "https://api.curse.tools/v1"
# The CurseForge project of each mod of the pack (Modrinth slug -> project id), checked by hand once: a file the API
# names for a mod must belong to this project. A mod missing here is left out of the CurseForge pack with an error.
CF_PROJECTS = {
    "fabric-api": 306612,  # Fabric API
    "geckolib": 388172,  # GeckoLib
    "jei": 238222,  # Just Enough Items
    "mezzconfig": 1689768,  # MezzConfig
    "sodium": 394468,  # Sodium
    "lithium": 360438,  # Lithium
    "ferrite-core": 459857,  # FerriteCore (Fabric)
    "entityculling": 448233,  # Entity Culling (tr7zw)
    "immediatelyfast": 686911,  # ImmediatelyFast
    "dynamic-fps": 335493,  # Dynamic FPS
    "krypton": 428912,  # Krypton
    "modmenu": 308702,  # Mod Menu
    "placeholder-api": 1037459,  # Text Placeholder API
    "iris": 455508,  # Iris Shaders
}
SUMMARY = "Matriochka with its dependencies, recipe pages and client performance mods, ready to play."


class ApiError(Exception):
    def __init__(self, msg, code=None):
        super().__init__(msg)
        self.code = code


def die(msg, code=2):
    print("modpack: error: " + msg, file=sys.stderr)
    sys.exit(code)


def api(path, query=None):
    url = API + path + ("?" + urllib.parse.urlencode(query) if query else "")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise ApiError(f"{url} answered HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ApiError(f"cannot reach the Modrinth API ({url}): {getattr(e, 'reason', e)}")


def properties(path):
    """gradle.properties, with the pack's Minecraft version and its dependencies (versions/26.3/gradle.properties,
    the default version) when the file itself names none."""
    props = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                props[k.strip()] = v.strip()
    default = os.path.join(ROOT, "versions", "26.3", "gradle.properties")
    if "minecraft_version" not in props and os.path.exists(default) and os.path.abspath(path) == os.path.join(ROOT, "gradle.properties"):
        for k, v in properties(default).items():
            props.setdefault(k, v)
    return props


def pick(versions, pin):
    """The pinned version (by id or version number), else the newest release, else the newest beta."""
    if pin:
        for v in versions:
            if v["id"] == pin or v["version_number"] == pin:
                return v
        return None
    for kind in ("release", "beta"):
        found = [v for v in versions if v["version_type"] == kind]
        if found:
            return max(found, key=lambda v: v["date_published"])
    return None


def primary(version):
    files = version["files"]
    f = next((x for x in files if x.get("primary")), files[0] if files else None)
    if f is None:
        raise ApiError(f"version {version['id']} has no file")
    return f


def entry(path, sha1, sha512, size, url, client, server):
    host = urllib.parse.urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        die(f"{url}: Modrinth packs only accept downloads from {', '.join(ALLOWED_HOSTS)}")
    return {"path": path, "hashes": {"sha1": sha1, "sha512": sha512}, "env": {"client": client, "server": server},
            "downloads": [url], "fileSize": size}


def side(value):
    return {"required": REQ, "optional": OPT}.get(value, NO)


def resolve(mc, props):
    """Every mod of PACK that exists for this game version, with its required dependencies.
    Each is {slug, id, title, version, needed_by (slugs of the mods that require it), entry (its modrinth.index.json line)}."""
    query = {"game_versions": json.dumps([mc]), "loaders": json.dumps(["fabric"])}
    chosen, seen, report = [], set(), []
    todo = [(slug, props.get(key) if key else None, c, s, why, None) for slug, key, c, s, why in PACK]
    while todo:
        slug, pin, client, server, why, parent = todo.pop(0)
        project = api(f"/project/{slug}")
        if project is None:
            if pin:
                die(f"{slug} is not on Modrinth, but gradle.properties pins it")
            report.append(f"  skip {slug}: not on Modrinth")
            continue
        if project["id"] in seen:
            for c in chosen:
                if c["id"] == project["id"] and parent:
                    c["needed_by"].append(parent)
            continue
        versions = api(f"/project/{project['id']}/version", query) or []
        v = pick(versions, pin)
        if v is None:
            if pin:
                die(f"{slug} {pin} (pinned in gradle.properties) has no Fabric build for Minecraft {mc} on Modrinth")
            report.append(f"  skip {slug}: no Fabric build for {mc}")
            continue
        seen.add(project["id"])
        f = primary(v)
        chosen.append({"slug": project["slug"], "id": project["id"], "title": project["title"], "version": v["version_number"],
                       "needed_by": [parent] if parent else [],
                       "entry": entry("mods/" + f["filename"], f["hashes"]["sha1"], f["hashes"]["sha512"], f["size"], f["url"], client, server)})
        report.append(f"  {slug} {v['version_number']} ({v['version_type']}): {why}")
        for d in v.get("dependencies", []):
            if d.get("dependency_type") != "required" or not d.get("project_id"):
                continue
            if d["project_id"] in seen:
                for c in chosen:
                    if c["id"] == d["project_id"]:
                        c["needed_by"].append(project["slug"])
                continue
            dep = api(f"/project/{d['project_id']}")
            if dep is None or dep["slug"] in EXCLUDED:
                die(f"{slug} needs {d['project_id']}, which cannot be added")
            # a dependency is needed on the sides its parent runs on, as far as it supports them
            dc = client if side(dep.get("client_side")) != NO else NO
            ds = server if side(dep.get("server_side")) != NO else NO
            todo.append((dep["slug"], d.get("version_id"), dc, ds, f"needed by {slug}", project["slug"]))
    return chosen, report


def mod_entry(jar, url, version):
    data = open(jar, "rb").read()
    sha1, sha512 = hashlib.sha1(data).hexdigest(), hashlib.sha512(data).hexdigest()
    name = os.path.basename(jar)
    if not url:
        # the copy Modrinth serves, once the project is public; the GitHub release asset otherwise
        found = api(f"/version_file/{sha1}", {"algorithm": "sha1"})
        if found:
            url = primary(found)["url"]
        else:
            url = f"https://github.com/{REPO}/releases/download/v{version}/{urllib.parse.quote(name)}"
    return entry("mods/" + name, sha1, sha512, len(data), url, REQ, REQ), url


def find_jar():
    libs = os.path.join(ROOT, "build", "libs")
    jars = sorted(j for j in os.listdir(libs) if j.startswith("matriochka-") and j.endswith(".jar") and "-sources" not in j) if os.path.isdir(libs) else []
    if not jars:
        die("no mod jar in build/libs: run ./gradlew build first, or pass --jar")
    return os.path.join(libs, jars[-1])


def config(hard):
    """The pack's config/matriochka.json: the mod's defaults, nightmare difficulty for the hard pack."""
    return {
        "progressionGates": True,
        "mobHealthMultiplier": 1.0,
        "mobDamageMultiplier": 1.0,
        "maxGroupSize": 8,
        "difficulty": "nightmare" if hard else "normal",
    }


def zip_add(z, name, data):
    info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def write_zip(out, first, hard):
    """The pack file: its manifest files (name -> text) then the overrides, the same for both formats."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, text in first:
            zip_add(z, name, text)
        for base, dirs, names in os.walk(OVERRIDES):
            dirs.sort()
            for n in sorted(names):
                src = os.path.join(base, n)
                rel = os.path.relpath(src, OVERRIDES).replace(os.sep, "/")
                with open(src, "rb") as f:
                    zip_add(z, "overrides/" + rel, f.read())
        zip_add(z, "overrides/config/matriochka.json", json.dumps(config(hard), indent=2) + "\n")
    with open(out, "wb") as f:
        f.write(buf.getvalue())


# --- CurseForge ---------------------------------------------------------------------------------------------------

def cf_fingerprint(data):
    """CurseForge's file fingerprint: 32-bit MurmurHash2 (seed 1) of the file without tab, LF, CR and space bytes."""
    data = data.translate(None, b"\t\n\r ")
    m, n = 0x5BD1E995, len(data)
    h = (1 ^ n) & 0xFFFFFFFF
    end = n - n % 4
    for (k,) in struct.iter_unpack("<I", data[:end]):
        k = (k * m) & 0xFFFFFFFF
        k ^= k >> 24
        k = (k * m) & 0xFFFFFFFF
        h = ((h * m) & 0xFFFFFFFF) ^ k
    tail = data[end:]
    if tail:
        if len(tail) == 3:
            h ^= tail[2] << 16
        if len(tail) >= 2:
            h ^= tail[1] << 8
        h ^= tail[0]
        h = (h * m) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * m) & 0xFFFFFFFF
    return h ^ (h >> 15)


def cf_api(path, body=None):
    key = os.environ.get("CURSEFORGE_API_KEY", "").strip()
    url = (CF_API if key else CF_MIRROR) + path
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if key:
        headers["x-api-key"] = key
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["data"]
    except urllib.error.HTTPError as e:
        raise ApiError(f"{url} answered HTTP {e.code}", e.code)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as e:
        raise ApiError(f"cannot read the CurseForge API ({url}): {getattr(e, 'reason', e)}")


def download(url, sha1=None, tries=1):
    """The bytes at url; with sha1, they must match it."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            break
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt + 1 == tries:
                raise ApiError(f"cannot download {url}: {getattr(e, 'reason', e)}")
            time.sleep(30)
    if sha1 and hashlib.sha1(data).hexdigest() != sha1:
        raise ApiError(f"{url} does not match its sha1")
    return data


def cf_source():
    """The official API when CURSEFORGE_API_KEY is set. Without it: an error in CI, the keyless mirror locally."""
    if os.environ.get("CURSEFORGE_API_KEY", "").strip():
        return "the CurseForge API"
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        die("the CurseForge export needs the CURSEFORGE_API_KEY secret in CI (a key from console.curseforge.com);"
            " the api.curse.tools mirror is only used for local runs")
    print("modpack: warning: CURSEFORGE_API_KEY is not set, reading CurseForge through the api.curse.tools mirror;"
          " every file it names is checked against the CurseForge CDN", file=sys.stderr)
    return "the api.curse.tools mirror"


def cf_edge(file_id, name):
    """The official CurseForge CDN address of a file, built from its id: what it serves proves what the id is."""
    return f"https://edge.forgecdn.net/files/{file_id // 1000}/{file_id % 1000}/{urllib.parse.quote(name)}"


def cf_verify(f, project, sha1, fingerprint, mc, tries=1, check_versions=True):
    """Problems with CurseForge file f standing for the jar (sha1, fingerprint) of the given project, or []."""
    bad = []
    if f.get("modId") != project:
        bad.append(f"belongs to project {f.get('modId')}, expected {project}")
    if f.get("fileFingerprint") != fingerprint:
        bad.append("fingerprint differs")
    api_sha1 = next((h["value"] for h in f.get("hashes", []) if h.get("algo") == 1), None)
    if api_sha1 and api_sha1.lower() != sha1:
        bad.append(f"sha1 {api_sha1} differs from the pack's {sha1}")
    if check_versions and (mc not in f.get("gameVersions", []) or "Fabric" not in f.get("gameVersions", [])):
        bad.append(f"not tagged {mc} Fabric")
    if not bad:
        try:
            data = download(cf_edge(f["id"], f["fileName"]), tries=tries)
        except ApiError as e:
            return [str(e)]
        if hashlib.sha1(data).hexdigest() != sha1 or cf_fingerprint(data) != fingerprint:
            bad.append("the CurseForge CDN serves other bytes for this file id")
    return bad


def cf_files(mods, jar, mod_file, mc):
    """The CurseForge file of each mod (same bytes, approved, this game version, Fabric), what is left out, and the
    mismatches (files the API names that fail verification)."""
    prints, wanted = {}, {}
    for m in mods:
        e = m["entry"]
        fp = cf_fingerprint(download(e["downloads"][0], e["hashes"]["sha1"]))
        prints[fp] = m["slug"]
        wanted[m["slug"]] = (e["hashes"]["sha1"], fp)
    own_data = open(jar, "rb").read()
    own_sha1, own = hashlib.sha1(own_data).hexdigest(), cf_fingerprint(own_data)
    found = cf_api(f"/fingerprints/{CF_GAME}", {"fingerprints": list(prints) + [own]})
    by_print = {x["file"]["fileFingerprint"]: x["file"] for x in found.get("exactMatches", []) if isinstance(x.get("file"), dict)}
    picked, missing, wrong = {}, {}, {}
    # the mod itself: the id given (from the upload) or the file with its fingerprint, checked on the CDN either way
    f = by_print.get(own)
    if mod_file is not None and (f is None or f.get("id") != mod_file):
        # just uploaded: not in the fingerprint index yet, ask for the file itself
        for attempt in range(6):
            try:
                f = cf_api(f"/mods/{CF_PROJECT}/files/{mod_file}")
                break
            except ApiError as e:
                if attempt == 5 or e.code in (400, 401, 403):
                    die(f"cannot read the mod's CurseForge file {mod_file}: {e}")
                time.sleep(30)
    if f is None:
        die("the mod jar is not on CurseForge yet (no file with its fingerprint): upload it first or pass --cf-mod-file")
    bad = cf_verify(f, CF_PROJECT, own_sha1, own, mc, tries=6, check_versions=mod_file is None)
    if bad:
        die(f"CurseForge file {f['id']} is not the mod jar: {'; '.join(bad)}")
    mod_file = f["id"]
    if f.get("fileStatus", 4) != 4:
        print(f"modpack: warning: the mod's CurseForge file {mod_file} is not approved yet; CurseForge only accepts the pack"
              " once every file in it is approved", file=sys.stderr)
    for fp, slug in prints.items():
        f = by_print.get(fp)
        project = CF_PROJECTS.get(slug)
        if f is None:
            missing[slug] = "not on CurseForge with the same file"
        elif project is None:
            wrong[slug] = f"no CurseForge project is listed for it in CF_PROJECTS (the API names {f.get('modId')})"
        elif f.get("fileStatus") != 4 or not f.get("isAvailable", True):
            missing[slug] = f"its CurseForge file {f['id']} is not approved yet"
        else:
            bad = cf_verify(f, project, *wanted[slug], mc)
            if bad:
                wrong[slug] = f"CurseForge file {f.get('id')}: {'; '.join(bad)}"
            else:
                picked[slug] = f
    missing.update(wrong)
    # a mod whose required dependency is missing cannot load: leave it out too
    changed = True
    while changed:
        changed = False
        for m in mods:
            if m["slug"] in missing:
                continue
            needs = [x["slug"] for x in mods if m["slug"] in x["needed_by"] and x["slug"] in missing]
            if needs:
                missing[m["slug"]] = f"needs {', '.join(needs)}, which is not on CurseForge"
                picked.pop(m["slug"], None)
                changed = True
    return mod_file, picked, missing, wrong


def cf_link(url):
    """url when it is an http(s) page on curseforge.com, else None."""
    if not isinstance(url, str):
        return None
    u = urllib.parse.urlparse(url)
    host = (u.hostname or "").lower()
    if u.scheme in ("http", "https") and (host == "curseforge.com" or host.endswith(".curseforge.com")):
        return url
    return None


def modlist(projects):
    lines = ["<ul>"]
    for p in projects:
        name = html.escape(str(p.get("name", "")))
        author = html.escape(", ".join(str(a.get("name", "")) for a in p.get("authors", [])) or "unknown")
        link = cf_link((p.get("links") or {}).get("websiteUrl"))
        if link:
            lines.append(f'<li><a href="{html.escape(link, quote=True)}">{name} (by {author})</a></li>')
        else:
            lines.append(f"<li>{name} (by {author})</li>")
    lines.append("</ul>")
    return "\n".join(lines) + "\n"


def build_curseforge(args, props, mods):
    version, mc, loader = props["mod_version"], props["minecraft_version"], props["loader_version"]
    source = cf_source()
    mod_file, picked, missing, wrong = cf_files(mods, args.jar, args.cf_mod_file, mc)
    if wrong:
        for slug, why in wrong.items():
            print(f"modpack: error: {slug}: {why}", file=sys.stderr)
        die("some CurseForge files failed verification: no pack written")
    optional = {m["slug"] for m in mods if m["entry"]["env"]["client"] == OPT}
    files = [{"projectID": CF_PROJECT, "fileID": mod_file, "required": True}]
    for m in mods:
        f = picked.get(m["slug"])
        if f:
            files.append({"projectID": f["modId"], "fileID": f["id"], "required": m["slug"] not in optional})
    projects = {p["id"]: p for p in cf_api("/mods", {"modIds": [f["projectID"] for f in files]})}
    name = PACK_NAME + (" (Hard)" if args.hard else "")
    pack_version = version + ("-hard" if args.hard else "")
    manifest = {
        "minecraft": {"version": mc, "modLoaders": [{"id": f"fabric-{loader}", "primary": True}]},
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": name,
        "version": pack_version,
        "author": AUTHOR,
        "files": files,
        "overrides": "overrides",
    }
    os.makedirs(args.out, exist_ok=True)
    out = os.path.join(args.out, f"matriochka-pack-{pack_version}+{mc}-curseforge.zip")
    write_zip(out, [("manifest.json", json.dumps(manifest, indent=2) + "\n"),
                    ("modlist.html", modlist(projects[f["projectID"]] for f in files if f["projectID"] in projects))], args.hard)
    print(f"{name} {pack_version} (CurseForge) for Minecraft {mc}, Fabric Loader {loader}"
          f" (looked up through {source}, every file checked on the CurseForge CDN)")
    print(f"  matriochka {version}: project {CF_PROJECT}, file {mod_file}")
    for m in mods:
        f = picked.get(m["slug"])
        if f:
            print(f"  {m['slug']} {m['version']}: project {f['modId']}, file {f['id']}" + (" (optional)" if m["slug"] in optional else ""))
    for slug, why in missing.items():
        print(f"  left out {slug}: {why}")
    print(f"wrote {os.path.relpath(out, ROOT)} ({len(files)} mods)")
    return out


# --- Modrinth -----------------------------------------------------------------------------------------------------

def properties_for(path, mc):
    """The properties of the pack for Minecraft version mc: the given file, with versions/<mc>/gradle.properties over it."""
    props = properties(path)
    if mc:
        over = os.path.join(ROOT, "versions", mc, "gradle.properties")
        if not os.path.exists(over):
            die(f"no Minecraft version {mc} (versions/{mc}/gradle.properties)")
        props.update(properties(over))
    return props


def build(args):
    props = properties_for(args.properties, args.mc)
    version, mc, loader = props["mod_version"], props["minecraft_version"], props["loader_version"]
    args.jar = args.jar or find_jar()
    if not os.path.isfile(args.jar):
        die(f"{args.jar} does not exist")
    try:
        mod, url = mod_entry(args.jar, args.mod_url, version)
        mods, report = resolve(mc, props)
        if args.curseforge:
            return build_curseforge(args, props, mods)
    except ApiError as e:
        die(f"{e}. The pack needs the API for download links and hashes; try again once it answers.")
    name = PACK_NAME + (" (Hard)" if args.hard else "")
    pack_version = version + ("-hard" if args.hard else "")
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": pack_version,
        "name": name,
        "summary": SUMMARY + (" Nightmare difficulty: creatures hit 30% harder and Soul Cradles hold one charge." if args.hard else ""),
        "files": [mod] + [m["entry"] for m in mods],
        "dependencies": {"minecraft": mc, "fabric-loader": loader},
    }
    os.makedirs(args.out, exist_ok=True)
    out = os.path.join(args.out, f"matriochka-pack-{pack_version}+{mc}.mrpack")
    write_zip(out, [("modrinth.index.json", json.dumps(index, indent=2, ensure_ascii=False) + "\n")], args.hard)
    print(f"{name} {pack_version} for Minecraft {mc}, Fabric Loader {loader}")
    print(f"  matriochka {version}: {url}")
    print("\n".join(report))
    print(f"wrote {os.path.relpath(out, ROOT)} ({len(index['files'])} mods)")
    return out


def main():
    p = argparse.ArgumentParser(description="Build the Matriochka Pack (.mrpack, or the CurseForge .zip).")
    p.add_argument("--jar", help="the mod jar (default: the one in build/libs)")
    p.add_argument("--mod-url", help="download URL of that jar (default: Modrinth if it serves it, else the GitHub release)")
    p.add_argument("--out", default=os.path.join(ROOT, "build", "modpack"), help="output folder (default: build/modpack)")
    p.add_argument("--hard", action="store_true", help="the hard pack: nightmare difficulty")
    p.add_argument("--curseforge", action="store_true", help="write the CurseForge modpack (.zip with manifest.json) instead")
    p.add_argument("--cf-mod-file", type=int, help="CurseForge file id of the mod jar (default: looked up by fingerprint)")
    p.add_argument("--properties", default=os.path.join(ROOT, "gradle.properties"), help="gradle.properties to read (default: the repository's)")
    p.add_argument("--mc", help="the Minecraft version of the pack (26.3, 26.2, 26.1.2): its dependencies come from versions/<mc>/gradle.properties (default: 26.3)")
    build(p.parse_args())


if __name__ == "__main__":
    main()
