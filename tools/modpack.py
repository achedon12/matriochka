#!/usr/bin/env python3
"""Builds the Matriochka Pack, a Modrinth modpack (.mrpack) around the mod.

Usage (from the repository root, after ./gradlew build):
    python3 tools/modpack.py                       # the jar in build/libs, the normal pack
    python3 tools/modpack.py --hard                # the hard pack (nightmare difficulty)
    python3 tools/modpack.py --jar path/to/matriochka.jar --mod-url https://.../matriochka.jar

The pack holds the mod, its dependencies (Fabric API, GeckoLib), Just Enough Items as an optional client mod and
the client performance mods that exist for this Minecraft version on Modrinth, plus the files of
tools/modpack/overrides and a config/matriochka.json with the pack's settings. Versions pinned in
gradle.properties (Fabric API, GeckoLib, JEI) are used as is; the others take the newest release for the game
version (a beta only when the mod has no release for it). Required dependencies of every mod are added too.

Downloads and hashes come from the Modrinth API. When the API cannot be reached the script stops with an error
instead of writing an incomplete pack. Standard library only.
"""
import argparse
import hashlib
import io
import json
import os
import sys
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
SUMMARY = "Matriochka with its dependencies, recipe pages and client performance mods, ready to play."


class ApiError(Exception):
    pass


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


def properties():
    props = {}
    with open(os.path.join(ROOT, "gradle.properties"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                props[k.strip()] = v.strip()
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
    """Every mod of PACK that exists for this game version, with its required dependencies."""
    query = {"game_versions": json.dumps([mc]), "loaders": json.dumps(["fabric"])}
    chosen, seen, report = [], set(), []
    todo = [(slug, props.get(key) if key else None, c, s, why) for slug, key, c, s, why in PACK]
    while todo:
        slug, pin, client, server, why = todo.pop(0)
        project = api(f"/project/{slug}")
        if project is None:
            if pin:
                die(f"{slug} is not on Modrinth, but gradle.properties pins it")
            report.append(f"  skip {slug}: not on Modrinth")
            continue
        if project["id"] in seen:
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
        chosen.append(entry("mods/" + f["filename"], f["hashes"]["sha1"], f["hashes"]["sha512"], f["size"], f["url"], client, server))
        report.append(f"  {slug} {v['version_number']} ({v['version_type']}): {why}")
        for d in v.get("dependencies", []):
            if d.get("dependency_type") != "required" or not d.get("project_id") or d["project_id"] in seen:
                continue
            dep = api(f"/project/{d['project_id']}")
            if dep is None or dep["slug"] in EXCLUDED:
                die(f"{slug} needs {d['project_id']}, which cannot be added")
            # a dependency is needed on the sides its parent runs on, as far as it supports them
            dc = client if side(dep.get("client_side")) != NO else NO
            ds = server if side(dep.get("server_side")) != NO else NO
            todo.append((dep["slug"], d.get("version_id"), dc, ds, f"needed by {slug}"))
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


def build(args):
    props = properties()
    version, mc, loader = props["mod_version"], props["minecraft_version"], props["loader_version"]
    jar = args.jar or find_jar()
    if not os.path.isfile(jar):
        die(f"{jar} does not exist")
    try:
        mod, url = mod_entry(jar, args.mod_url, version)
        files, report = resolve(mc, props)
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
        "files": [mod] + files,
        "dependencies": {"minecraft": mc, "fabric-loader": loader},
    }
    os.makedirs(args.out, exist_ok=True)
    out = os.path.join(args.out, f"matriochka-pack-{pack_version}+{mc}.mrpack")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        zip_add(z, "modrinth.index.json", json.dumps(index, indent=2, ensure_ascii=False) + "\n")
        for base, dirs, names in os.walk(OVERRIDES):
            dirs.sort()
            for n in sorted(names):
                src = os.path.join(base, n)
                rel = os.path.relpath(src, OVERRIDES).replace(os.sep, "/")
                with open(src, "rb") as f:
                    zip_add(z, "overrides/" + rel, f.read())
        zip_add(z, "overrides/config/matriochka.json", json.dumps(config(args.hard), indent=2) + "\n")
    with open(out, "wb") as f:
        f.write(buf.getvalue())
    print(f"{name} {pack_version} for Minecraft {mc}, Fabric Loader {loader}")
    print(f"  matriochka {version}: {url}")
    print("\n".join(report))
    print(f"wrote {os.path.relpath(out, ROOT)} ({len(index['files'])} mods)")
    return out


def main():
    p = argparse.ArgumentParser(description="Build the Matriochka Pack (.mrpack).")
    p.add_argument("--jar", help="the mod jar (default: the one in build/libs)")
    p.add_argument("--mod-url", help="download URL of that jar (default: Modrinth if it serves it, else the GitHub release)")
    p.add_argument("--out", default=os.path.join(ROOT, "build", "modpack"), help="output folder (default: build/modpack)")
    p.add_argument("--hard", action="store_true", help="the hard pack: nightmare difficulty")
    build(p.parse_args())


if __name__ == "__main__":
    main()
