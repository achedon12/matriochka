# Matriochka Pack

Matriochka stays a standalone mod. The **Matriochka Pack** is a modpack built around it, for players who want everything set up in one click, in Modrinth's format (`.mrpack`) and in CurseForge's (`.zip` with a `manifest.json`). It comes in two flavors:

| Pack | Difficulty | Modrinth file | CurseForge file |
| --- | --- | --- | --- |
| Matriochka Pack | `normal` | `matriochka-pack-<version>+<minecraft>.mrpack` | `matriochka-pack-<version>+<minecraft>-curseforge.zip` |
| Matriochka Pack (Hard) | `nightmare`: creatures hit 30% harder, Soul Cradles hold one charge | `matriochka-pack-<version>-hard+<minecraft>.mrpack` | `matriochka-pack-<version>-hard+<minecraft>-curseforge.zip` |

All four are attached to every [GitHub release](https://github.com/achedon12/matriochka/releases) (the `.mrpack` files from 0.4 on, the CurseForge files once the modpack workflow has run for the release). Open a `.mrpack` with the Modrinth App, Prism Launcher or any launcher that imports them; import the `.zip` in the CurseForge app or Prism. Once the pack's own projects exist, both are also published there (see [Publishing](#publishing-it-on-modrinth-and-curseforge)).

## What is inside

| Mod | Side | Why |
| --- | --- | --- |
| Matriochka | both | the mod (from the GitHub release; in the CurseForge pack, its CurseForge file) |
| Fabric API | both | required |
| GeckoLib | both | required: models and animations |
| Just Enough Items (+ Mezz Config) | client, optional | recipe pages for every station |
| Sodium | client | rendering, much higher frame rate |
| Lithium | both | game logic, physics and chunk ticking |
| FerriteCore | both | memory use |
| Entity Culling | client | skips hidden creatures and block entities |
| ImmediatelyFast | client | faster HUD, text and map rendering |
| Dynamic FPS | client | lower frame rate in the background |
| Krypton | both | network stack |
| Mod Menu (+ Placeholder API) | client | mod list and config screens (not in the CurseForge pack, see below) |
| Iris | client, optional | shaders |

Versions: Fabric API, GeckoLib and JEI are the ones the mod is built against (`gradle.properties`); the others are the newest release for the Minecraft version on Modrinth (a beta only when a mod has no release for it), with their required dependencies. Left out on purpose: **LambDynamicLights** (a held torch would light the Lightless Deep and defeat World 5's rule), C2ME and ScalableLux (alpha builds only), ModernFix and MemoryLeakFix (no build for 26.3).

**The CurseForge pack** holds the same files, matched by their bytes (see [Building it](#building-it)). What has no identical, approved CurseForge file for 26.3 Fabric is left out, with the mods that need it, because CurseForge packs only accept CurseForge files. For 0.4.0 (November 2026):

- **Mod Menu and Placeholder API** are left out: Placeholder API 3.2.0 has no 26.3 file on CurseForge (its newest there is for 26.2), and Mod Menu needs it. Matriochka's comfort options stay in the Journal.
- **JEI and MezzConfig** were still in CurseForge's review queue (files 9453340 and 9453306); the script takes them as soon as they are approved, so a build made after that has them.
- Everything else is there, with optional mods (JEI, MezzConfig, Iris) marked `"required": false`.
- Entity Culling forbids third-party downloads on CurseForge, so Prism asks for that one file by hand when importing the CurseForge pack; the CurseForge app is not affected.

Overrides: `config/matriochka.json` with the mod's defaults (difficulty `normal`, or `nightmare` in the hard pack) and an `options.txt` with render distance 10 and simulation distance 8.

## Building it

```sh
./gradlew build
python3 tools/modpack.py            # build/modpack/matriochka-pack-<version>+<mc>.mrpack
python3 tools/modpack.py --hard     # the hard pack
python3 tools/modpack.py --jar path/to/matriochka.jar --mod-url https://...   # another jar or download link
python3 tools/modpack.py --curseforge [--hard] [--cf-mod-file <id>]          # the CurseForge pack
python3 tools/modpack.py --properties other/gradle.properties                # versions from another gradle.properties
```

The script reads `gradle.properties`, asks the Modrinth API for each mod's file, hashes and download link, hashes the mod jar itself, writes `modrinth.index.json` and zips it with `tools/modpack/overrides`. The mod's link is Modrinth's copy when Modrinth serves that exact jar, otherwise the GitHub release asset. If the API cannot be reached it stops with an error (exit code 2) instead of writing an incomplete pack. Standard library only.

**The CurseForge pack** starts from the same resolved list. Every jar of the Modrinth pack is downloaded (its sha1 checked), its CurseForge fingerprint (MurmurHash2 of the jar without whitespace bytes) is computed, and CurseForge's fingerprint lookup names the file with those exact bytes. Nothing from the lookup is trusted as is: each file must belong to the project listed for that mod in `CF_PROJECTS` (a fixed slug to project id table, checked by hand), carry the same sha1, be approved and tagged with the game version and Fabric, and the official CDN (`edge.forgecdn.net/files/<id>/...`) must serve exactly those bytes for its id. A mod with no such file is left out (with what needs it); a file that fails a check stops the script without writing a pack. The mod itself is the file given with `--cf-mod-file` (the release workflow passes the id its CurseForge upload returned) or the one with its fingerprint, verified the same way. `modlist.html` lists the mods with HTML-escaped names and links only to curseforge.com pages.

The lookup uses the official API (`api.curseforge.com`) with the key in `CURSEFORGE_API_KEY`. In CI the key is required and the CurseForge step fails without it (only that step: the release goes on). On your own machine, without a key, the script reads through the keyless read-only mirror `api.curse.tools` and prints a warning; the checks above still apply, the CDN check in particular.

## Publishing it on Modrinth and CurseForge

The release workflow (`release.yml`) builds the four pack files after the jar is published, attaches them to the GitHub release (`gh release upload --clobber`), then uploads them with `tools/modpack_publish.sh` to the pack's own projects. None of these steps can stop the mod's release: each is `continue-on-error`, and an upload that is not configured is skipped with a warning. The hard pack is uploaded first and the normal pack second, so the normal one is the newest version, the one launchers install by default.

- **Modrinth:** two versions per release, `<version>-hard` ("Matriochka Pack 0.4.0 (Hard)") then `<version>` ("Matriochka Pack 0.4.0"), game version from `gradle.properties`, loader `fabric`, type alpha, changelog from the `## <version>` section of `CHANGELOG.md`. Two versions rather than one version with the hard pack as an extra file, because the Modrinth App and Prism only install a version's primary file: an extra `.mrpack` could be downloaded but not installed from the launcher. A version number that is already on the project is skipped, so a re-run uploads only what is missing.
- **CurseForge:** two files the same way, tagged with the Minecraft version (the loader comes from `manifest.json`), release type alpha, the same changelog in Markdown.

The pack's Modrinth file list points at Modrinth's copy of every mod and at the GitHub release for Matriochka itself (Modrinth only accepts `cdn.modrinth.com`, `github.com`, `raw.githubusercontent.com` and `gitlab.com` downloads in a pack); the script switches to Modrinth's copy of the mod once the Matriochka Modrinth project is public.

### What the owner does once

1. **Modrinth:** create a project of type *Modpack*: name "Matriochka Pack", slug `matriochka-pack`, summary from `branding/modpack/summary.txt`, description from `branding/modpack/description.md`, icon `branding/modpack/icon.png`, categories *Adventure*, *Challenging*, *Quests* (and *Optimization*, *Lightweight* as additional ones), client side required, server side optional, license MIT, links (source, issues, wiki, Discord) and gallery from `branding/modpack/listing.json`. Then add the repository variable `MODRINTH_PACK_PROJECT_ID` (*Settings → Secrets and variables → Actions → Variables*) with the project id. The existing `MODRINTH_TOKEN` secret is reused; it needs the *Create versions* scope, and *Read versions* so the workflow can see the versions of a project that is not public yet.
2. **CurseForge:** create a project of type *Modpacks*: name "Matriochka Pack", summary from `branding/modpack/curseforge/summary.txt`, description from `branding/modpack/curseforge/description.md` (Markdown editor), avatar `branding/modpack/icon.png`, main category *Adventure and RPG*, additional *Quests*, *Exploration*, *Small / Light*, license MIT, links from `branding/modpack/curseforge/listing.json`. Then add the variable `CURSEFORGE_PACK_PROJECT_ID` (the project id shown on its overview page) and the secret `CURSEFORGE_API_KEY`: a key from [console.curseforge.com](https://console.curseforge.com) (*API keys*), which the export needs to look up files in CI. The existing `CURSEFORGE_TOKEN` secret (upload token) is reused.
3. **Publish 0.4.0**, which came out before the projects existed: *Actions → modpack → Run workflow* with tag `v0.4.0` (target `both`, `modrinth` or `curseforge`; the CurseForge file id of the mod, 9468136 for 0.4.0, can be given or left empty). The workflow downloads the released jar, builds the four files with the tag's `gradle.properties`, attaches them to the release and uploads them. From the next release on, `release.yml` does it on its own.

CurseForge only accepts a pack once every file in it is approved, Matriochka's own file included: if the pack is uploaded while the mod's file is still in review, CurseForge may reject or hold it, and running the modpack workflow again later fixes it. CurseForge's rules also say packs are made with the CurseForge app; the manifest written here has the app's format (`minecraftModpack`, version 1, `fabric-<loader>` as the primary loader, project and file ids), but if moderation asks, import the `.zip` in the CurseForge app and export it from there.

### By hand

`tools/modpack_publish.sh modrinth` or `curseforge` reads `TOKEN`, `PROJECT`, `VERSION`, `MC`, `NOTES` (default `notes.md`) and `PACK_DIR` (default `build/modpack`). `DRY_RUN=1` prints each request instead of uploading (it still reads the project's existing versions), which is how the workflow logic was checked against a fake project id.
