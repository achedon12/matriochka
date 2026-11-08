# Contributing to Matriochka

Thanks for wanting to help. Bug reports, balance feedback, translations, art and code are all welcome.

## Before you start

- Check the [issues](https://github.com/achedon12/matriochka/issues) to see if someone already reported or claimed it.
- For anything bigger than a fix (a new mob, a new mechanic, a rework), open an issue first so we can agree on the design before you spend time on it.
- Questions and ideas are also welcome on the [Discord server](https://github.com/achedon12/matriochka#community).

## Setup

You need **JDK 25** and **Python 3.11+** with Pillow (`pip install pillow`). Node 20+ is only needed for the website.

```sh
git clone https://github.com/achedon12/matriochka.git
cd matriochka
./gradlew build          # compiles and packages the mod into build/libs
./gradlew runClient      # starts a dev client with the mod loaded
```

If Gradle does not find your JDK, set `org.gradle.java.home` in your user-level `~/.gradle/gradle.properties`, not in the project file.

## How the content is built

Almost everything in the mod comes from one table: **`tools/content.py`**. Worlds, items, blocks, mobs, bosses, structures, quests and achievements are declared there, and

```sh
python3 tools/gen.py
```

generates the textures, GeckoLib models and animations, lang files, worldgen and loot data, and `content/Content.java`. Never edit generated files by hand: change the table or the generator, then regenerate. Generation is deterministic, so a regenerated tree with no table change produces no diff.

## Minecraft versions

The mod is built for several Minecraft versions from the same sources: 26.3 by default, 26.2 with `-Pmc=26.2` (`./gradlew build -Pmc=26.2`, `./gradlew runClientGameTest -Pmc=26.2 -Ponboarding`). Each version has a folder in `versions/<mc>/`:

- `gradle.properties`: its Minecraft, Fabric API, GeckoLib, JEI and Mod Menu versions;
- `main/java`, `client/java`: the few calls that differ between versions (`mc/Mc.java`, `client/mc/McClient.java`, and the mixins whose target changed), with the same class names in every version;
- `main/resources`: the data that differs, laid over `src/main/resources`. It is generated: after `tools/gen.py`, run `python3 tools/versions.py`, which writes the world generation in each older version's formats (from `tools/vanilla_<mc>/`) and keeps only the files that differ.

A version other than 26.3 builds into `build/mc-<mc>/`. CI builds every version, and a release publishes one jar per version.

| Tool | What it produces |
| --- | --- |
| `tools/content.py` | the data table everything reads |
| `tools/gen.py` | all generated assets, data and Java |
| `tools/paint.py` | item, block and armor pixel art |
| `tools/craft.py` | the hand-painted dolls, cores, Seeds, gear, writings, offerings, soils and stations, at any size |
| `tools/particles.py`, `tools/atmosphere.py` | the mod's particles, and each world's light, fog and floating particles |
| `tools/hdpack.py`, `tools/texsheets.py` | the optional Matriochka HD resource pack, and preview sheets of the textures |
| `tools/models.py` | creature rigs and animations |
| `tools/bosses_hd.py` | the eleven hand-rigged bosses |
| `tools/gui.py` | GUI art painted at twice its size: lacquer, gold leaf, khokhloma, parchment, dolls |
| `tools/ui_lang.py` | hand-written UI strings (EN and FR) |
| `tools/translations.py`, `tools/i18n/` | the other languages, checked against English |
| `tools/sound.py` | the sound table: ids, subtitles, biome music and ambience |
| `tools/sfx.py`, `tools/music.py`, `tools/synth.py` | sound recipes, the folk composer and the synthesizer |
| `tools/site.py` | data and images for the website in `site/` |
| `tools/modpack.py`, `tools/modpack_publish.sh` | the Matriochka Pack for Modrinth and CurseForge and its upload (see the wiki's Modpack page) |
| `tools/logo_v2.py` | the icons and logo, voxel pixel art: the mod's icon (`branding/logo-*.png`, `icon.png`, hand-tuned 16/32/48 px), the pack and Discord icon, the illustration |

Hand-written Java lives in `src/main/java` (game logic) and `src/client/java` (screens, HUD, renderers).

## Translations

Lang files are generated. English and French live in `tools/content.py` (content names and descriptions) and `tools/ui_lang.py` (interface text, run it before `gen.py`). Spanish, German and Brazilian Portuguese live in `tools/i18n/<code>.json`, one table per language checked against English by `gen.py`; `python3 tools/translations.py <code>` lists what is missing. A missing key falls back to English. For a new language, open an issue and we will set it up together.

## Pull requests

1. Fork, then branch from `main` (`fix/toxin-gauge`, `feat/new-mob`...).
2. Keep each PR focused on one change. Small commits with clear messages in the imperative ("Fix toxin gauge reset on death").
3. Run `python3 tools/gen.py`, `python3 tools/versions.py` and `./gradlew build` before pushing. CI runs the same checks.
4. For visual changes (models, textures, GUI), add a screenshot or a short clip to the PR.
5. Fill in the PR template; link the issue it closes.

## Code style

- Java: tabs, Mojang mappings names, no wildcard imports. Keep game rules in `rules/` and world logic in `world/`.
- Python: standard library plus Pillow only, four-space indent. The sound tools also need numpy and ffmpeg (libvorbis), but only to render a sound whose recipe changed: `tools/sounds.lock.json` keeps a hash of each recipe, so `gen.py` runs with Pillow alone otherwise.
- The `.editorconfig` covers whitespace for every file type.

## Licensing of contributions

By contributing you agree that your work is released under the project's [MIT License](LICENSE).
