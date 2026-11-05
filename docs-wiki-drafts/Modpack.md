# Matriochka Pack

Matriochka stays a standalone mod. The **Matriochka Pack** is a Modrinth modpack (`.mrpack`) built around it, for players who want everything set up in one click. It comes in two flavors:

| Pack | Difficulty | File |
| --- | --- | --- |
| Matriochka Pack | `normal` | `matriochka-pack-<version>+<minecraft>.mrpack` |
| Matriochka Pack (Hard) | `nightmare`: creatures hit 30% harder, Soul Cradles hold one charge | `matriochka-pack-<version>-hard+<minecraft>.mrpack` |

Both are attached to every [GitHub release](https://github.com/achedon12/matriochka/releases) from 0.4 on. Open one with the Modrinth App, Prism Launcher or any launcher that imports `.mrpack` files.

## What is inside

| Mod | Side | Why |
| --- | --- | --- |
| Matriochka | both | the mod (downloaded from the GitHub release) |
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
| Mod Menu (+ Placeholder API) | client | mod list and config screens |
| Iris | client, optional | shaders |

Versions: Fabric API, GeckoLib and JEI are the ones the mod is built against (`gradle.properties`); the others are the newest release for the Minecraft version on Modrinth (a beta only when a mod has no release for it), with their required dependencies. Left out on purpose: **LambDynamicLights** (a held torch would light the Lightless Deep and defeat World 5's rule), C2ME and ScalableLux (alpha builds only), ModernFix and MemoryLeakFix (no build for 26.3).

Overrides: `config/matriochka.json` with the mod's defaults (difficulty `normal`, or `nightmare` in the hard pack) and an `options.txt` with render distance 10 and simulation distance 8.

## Building it

```sh
./gradlew build
python3 tools/modpack.py            # build/modpack/matriochka-pack-<version>+<mc>.mrpack
python3 tools/modpack.py --hard     # the hard pack
python3 tools/modpack.py --jar path/to/matriochka.jar --mod-url https://...   # another jar or download link
```

The script reads `gradle.properties`, asks the Modrinth API for each mod's file, hashes and download link, hashes the mod jar itself, writes `modrinth.index.json` and zips it with `tools/modpack/overrides`. The mod's link is Modrinth's copy when Modrinth serves that exact jar, otherwise the GitHub release asset. If the API cannot be reached it stops with an error (exit code 2) instead of writing an incomplete pack. Standard library only.

The release workflow builds both packs after the jar is published and attaches them to the GitHub release (`gh release upload --clobber`). The step does not stop the release when it fails.

## Publishing it on Modrinth or CurseForge

The pack is not uploaded to Modrinth or CurseForge automatically: a modpack needs a project of its own, which only the owner can create.

1. **Modrinth:** create a project of type *Modpack* (name "Matriochka Pack", license MIT, client required, server optional), then upload the `.mrpack` from the release as a version (game version 26.3, loader Fabric). Every file of the pack points to Modrinth, GitHub or the Matriochka release, which Modrinth accepts. To automate it, add a `MODRINTH_PACK_PROJECT_ID` variable and a step in `release.yml` like the Modrinth one, with `"loaders": ["fabric"]` and the `.mrpack` as the file, passing the values through `env:`.
2. **CurseForge:** CurseForge modpacks use their own format (`manifest.json` with CurseForge file ids), not `.mrpack`; it would need a second exporter, or exporting the pack from the CurseForge app after importing it.
