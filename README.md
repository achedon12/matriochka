<p align="center"><img src="src/main/resources/assets/matriochka/icon.png" width="96" alt="Matriochka icon"></p>

<h1 align="center">Matriochka</h1>

<p align="center">Every block can hold a world.</p>

<p align="center">
  <a href="https://achedon12.github.io/matriochka/">Website</a> ·
  <a href="https://github.com/achedon12/matriochka/wiki">Wiki</a> ·
  <a href="https://github.com/achedon12/matriochka/releases">Download</a>
</p>

Matriochka is a progression mod for Minecraft Java 26.3 (Fabric). Ten worlds are nested inside blocks, one inside the other, like the dolls it is named after. You craft a Seed, plant it on tilled World Soil, and the block that hatches holds a whole world with its own rule, creatures, machine and boss. Beat the boss, take its core, and the next Seed becomes possible.

## What is inside

| | |
| --- | --- |
| 10 worlds | Toxic jungle, giant veins, endless dungeon, storm archipelago, lightless deep, upside realm, pressure ocean, hastened seasons, restless ground, the giant workshop |
| 10 rules | Toxin, heat, locks, wind and lightning, noise, gravity flips, oxygen and pressure, accelerated seasons, moving ground, and a synthesis of all nine |
| 61 creatures | 50 mobs with their own mechanics (ambushes, mimics, sound hunters, nesting mobs that split on death) and 11 bosses |
| Readable bosses | Every attack is announced, executed, then leaves an opening. Phases at 66% and 33% of health. Health scales with the number of players |
| 13 stations | Each with one mechanic: fermentation, temperature, lock patterns, lightning, darkness, depth, time of day |
| Equipment classes | Gear gets a random class when crafted: Guardian, Berserker, Prowler, Reaper, Survivor or Prospector, upgradable to level 5 |
| Souls and karma | Every item holds a soul. Purify it or devour it at the Soul Altar. Karma changes prices, quests and people |
| Doll of Life | Each layer saves you from one death. Soul Cradles let you respawn inside a world, death chests keep your items |
| 100 structures | 10 types per world, generated procedurally, with journal pages and one hidden doll per world |
| 64 quests, 100 achievements | Optional quest book in the Artisan's Journal and one advancement tab per world |

<!-- gui -->
<p align="center"><img src="https://achedon12.github.io/matriochka/shots/gui_journal_1.png" alt="The Journal, quests tab" width="49%"> <img src="https://achedon12.github.io/matriochka/shots/gui_station_spore_vat.png" alt="The Spore Vat, World 1 station" width="49%"><br><img src="https://achedon12.github.io/matriochka/shots/gui_scroll.png" alt="The Artisan's Scroll" width="49%"> <img src="https://achedon12.github.io/matriochka/shots/gui_station_lightning_forge.png" alt="The Lightning Forge, World 4 station" width="49%"></p>
<!-- /gui -->

## Requirements

- Minecraft Java Edition 26.3
- Fabric Loader 0.20.0 or newer
- [Fabric API](https://modrinth.com/mod/fabric-api)
- [GeckoLib](https://modrinth.com/mod/geckolib) 5.5.7 or newer
- Java 25

The mod must be installed on the server and on every client. It works in singleplayer, on servers and on Lunar Client (Fabric profile).

## Getting started

1. You wake up with the Artisan's Scroll. Read it.
2. Find the Guardian's Sanctuary, a ring of stone pillars around an altar, a few hundred blocks from spawn.
3. Use the altar and defeat the Block Guardian. It drops its core, the Matrix Workbench and World Soil.
4. Craft the World 1 Seed, till the World Soil with a hoe, plant the Seed next to water and wait for it to hatch.
5. Use the World Block to enter. The Threshold or a Return Thread brings you back.

The full guide lives in the [wiki](https://github.com/achedon12/matriochka/wiki).

## Commands

| Command | Effect |
| --- | --- |
| `/matriochka group info / invite / join / leave` | Manage your group (up to 8 players share their worlds) |
| `/matriochka karma show` | Show your karma and souls |
| `/matriochka progression set <world>` | Operators: set the group's progression |
| `/matriochka world enter <n>` / `leave` | Operators: travel between worlds |
| `/matriochka boss <id>` | Operators: summon a boss for testing |
| `/matriochka debug` | Operators: current world, parcel, gauges |

## Building from source

```sh
python3 tools/gen.py        # regenerate textures, models, lang files and data from tools/content.py
./gradlew build             # build the mod jar into build/libs
./gradlew runClient         # start a development client
./gradlew runClientGameTest # load every world, wake every boss and save screenshots
```

All content (worlds, items, mobs, bosses, structures, quests, achievements) is described once in `tools/content.py`. The generator writes the textures, the GeckoLib models and animations (they open in Blockbench), the English and French translations, the dimensions, biomes and structures, and the generated Java definitions.

## Project layout

```
tools/            content table, texture painter, model generator, GUI sprites
src/main/java     server and common logic (worlds, rules, bosses, stations, karma, classes)
src/client/java   renderers, HUD, Journal and station screens
src/gametest/java showcase test that visits every world
design/           original design notes
site/             website (Next.js, GitHub Pages)
```

## Status

Matriochka is in alpha. All ten worlds, their rules, mobs, bosses, stations and progression are playable. Every creature and boss has its own hand-built GeckoLib model, animations and attacks. See the [roadmap](https://github.com/achedon12/matriochka/wiki/Roadmap) for what comes next.

## Contributing

Matriochka is open source and contributions are welcome: bug reports, balance feedback, translations, models and code. Start with [CONTRIBUTING.md](CONTRIBUTING.md), which explains how the content table and the generators fit together. Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md); security issues go through the [security policy](SECURITY.md).

## License

Code and assets are released under the [MIT License](LICENSE).

Made by [achedon12](https://github.com/achedon12).
