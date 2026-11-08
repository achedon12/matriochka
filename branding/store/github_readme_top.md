<!--
Replaces README.md from the first line down to (not including) "## Requirements".
Everything from "## Requirements" on stays as it is.

Proposed GitHub repo description (About):
  Fabric mod for Minecraft 26.1.2 to 26.3: ten worlds nested inside blocks, each with its own rule, creatures, station and boss.

Proposed topics:
  minecraft, minecraft-mod, fabric, fabricmc, fabric-mod, minecraft-fabric, geckolib, java, progression,
  dimensions, boss-fight, adventure, matryoshka

Images: branding/poster.jpg is the key art (copy media/poster/out/matriochka_poster_3840x2160.jpg there, scaled to
1920 wide, since media/ is not tracked). The world shots are already tracked in site/public/shots/. The 0.9.0 shots
come from the wiki repository (wiki/ is not part of this repository), through raw.githubusercontent.com/wiki/.
-->

<p align="center"><img src="branding/logo-256.png" width="128" alt="Matriochka logo"></p>

<h1 align="center">Matriochka</h1>

<p align="center"><b>Every block can hold a world.</b></p>

<p align="center">
  <a href="https://achedon12.github.io/matriochka/">Website</a> ·
  <a href="https://github.com/achedon12/matriochka/wiki">Wiki</a> ·
  <a href="https://github.com/achedon12/matriochka/releases">Download</a> ·
  <a href="https://discord.gg/SPVCf5hRuh">Discord</a>
</p>

<p align="center">
  <a href="https://www.curseforge.com/minecraft/mc-mods/matriochka"><img src="https://img.shields.io/curseforge/dt/1785262?label=CurseForge&logo=curseforge&color=a8231a" alt="CurseForge downloads"></a>
  <a href="https://modrinth.com/mod/matriochka"><img src="https://img.shields.io/modrinth/dt/matriochka?label=Modrinth&logo=modrinth&color=a8231a" alt="Modrinth downloads"></a>
  <a href="https://github.com/achedon12/matriochka/releases"><img src="https://img.shields.io/github/downloads/achedon12/matriochka/total?label=GitHub&logo=github&color=a8231a" alt="GitHub downloads"></a>
</p>

<p align="center"><img src="branding/poster.jpg" alt="Matriochka key art" width="100%"></p>

Matriochka is a progression mod for Minecraft Java 26.1.2, 26.2 and 26.3 on Fabric. Ten worlds are nested inside blocks, one inside the other, like the dolls it is named after.

You craft a Seed, plant it on tilled World Soil next to water, and the block that hatches holds a whole world: its own rule, creatures and people, its own crafting station, and a boss at the end. Beat the boss, take its core, and the way into the next world opens. Every world after the first opens with its own object and its own rite.

It starts in your normal world, with the Block Guardian a few hundred blocks from spawn, and it ends in World 0, the smallest doll, which only the ten hidden dolls open.

The mod is in beta (0.9.0): every world, boss and ending is playable, and it is being polished.

## The ten worlds

| World | Rule | What it does to you |
| --- | --- | --- |
| 1. Toxic Jungle | Toxin | Builds every second out of water or rain |
| 2. Giant Veins | Heat | Lava and depth cook you; water and thermal armour cool you |
| 3. Endless Dungeon | Locks | Sealed doors need keys, and the halls move every five minutes |
| 4. Storm Archipelago | Wind | Gusts every 30 seconds, announced lightning, no elytra |
| 5. Lightless Deep | Noise | Sprint and everything near hunts you; placed lights die in a minute |
| 6. Upside Realm | Gravity | A third of the land flips gravity, the pattern changes every 90 seconds |
| 7. Pressure Ocean | Oxygen | No dry land; breath, snorkel tanks and crushing depth |
| 8. Hastened Seasons | Season | Eight-minute days, two-minute seasons, hungry summers, slow winters |
| 9. Restless Ground | Tremor | Every minute, whole zones of ground rise, sink, slide or close |
| 10. The Giant Workshop | Synthesis | The nine rules before it, one per zone |

<p align="center">
  <img src="site/public/shots/w01_view.webp" alt="World 1, the Toxic Jungle" width="49%">
  <img src="site/public/shots/w04_view.webp" alt="World 4, the Storm Archipelago" width="49%"><br>
  <img src="site/public/shots/w06_view.webp" alt="World 6, the Upside Realm" width="49%">
  <img src="site/public/shots/w07_view.webp" alt="World 7, the Pressure Ocean" width="49%"><br>
  <img src="site/public/shots/w08_view.webp" alt="World 8, the Hastened Seasons" width="49%">
  <img src="site/public/shots/w10_view.webp" alt="World 10, the Giant Workshop" width="49%">
</p>

## What is inside

| | |
| --- | --- |
| 10 worlds and World 0 | Each with its own rule, creatures, people, station, structures, wonder and boss |
| 12 bosses | Every attack is announced, executed, then leaves an opening. Phases at 66% and 33% of health. Health scales with the players near the fight. Each has its own model, boss bar and music theme |
| 50 creatures | Ambushers, mimics, sound hunters, nesting mobs that split on death, each with its own GeckoLib model and moves |
| 13 stations | Each with one mechanic: fermentation, temperature, lock patterns, lightning, darkness, depth, time of day |
| The Artisan's Journal | Objective, 70 optional quests, karma, a card for every world's items and how to get them, a map inked as you walk, 50 pages of story |
| 10 wonders | One great place per world, with a reliquary that only another world's cross key opens. Each relic gives a heart for good and its world's gift |
| 10 world ores | One per world, each obtained its own way, nested in the Nesting Cradle into Matriochkite |
| Matriarch Armour | The finest set, whose Nested Shell halves every world's gauge and turns one deadly blow every five minutes |
| Equipment classes | Gear rolls Guardian, Berserker, Prowler, Reaper, Survivor or Prospector when crafted, up to level 5, with 72 talents |
| Souls and karma | Every item holds a soul; purify it or devour it. Karma changes prices, quests, people and your ending |
| Doll of Life | Each layer saves you from one death. Soul Cradles and death chests do the rest |
| 110 structures | Eleven per world, with Journal pages and a hidden doll in each world |
| Endings and replay | Three endings, a New Cycle with mutated bosses, and the Trials with a server leaderboard |
| 100 achievements | One advancement tab per world |
| Comfort | Options > Matriochka...: screen shake, flashes, soft effects, cinematics, subtitles, particles, gauge patterns, HUD and music volumes |
| Groups | Up to 8 players share worlds and bosses; each keeps their own souls, karma and quests |
| 9 languages | English, French, Spanish, German, Brazilian Portuguese, Italian, Russian, Polish, Simplified Chinese |

## New in 0.9.0: Nesting

Every world now has an ore of its own, each obtained its own way: grown on blooms by the water, mined with a burning hand or in total silence, fused by lightning, falling upwards, dropped by the creatures of the deep, ripened from a seed in two minutes. Set the ten in the Nesting Cradle and an eight-second ritual of ten nesting dolls turns them into a Matriochkite Ingot, the metal of the Matriarch Armour: 32 armour, 18 toughness, a heart per piece, and the Nested Shell. See the [wiki page](https://github.com/achedon12/matriochka/wiki/World-Ores-and-the-Matriarch) and the [changelog](CHANGELOG.md).

<p align="center">
  <img src="https://raw.githubusercontent.com/wiki/achedon12/matriochka/images/matriarch/ritual_nest.webp" alt="The Nesting Cradle's ritual" width="49%">
  <img src="https://raw.githubusercontent.com/wiki/achedon12/matriochka/images/matriarch/armour_front.webp" alt="The Matriarch Armour" width="49%">
</p>

<!-- gui -->
<p align="center"><img src="https://achedon12.github.io/matriochka/shots/gui_journal_1.png" alt="The Journal, quests tab" width="49%"> <img src="https://achedon12.github.io/matriochka/shots/gui_station_spore_vat.png" alt="The Spore Vat, World 1 station" width="49%"><br><img src="https://achedon12.github.io/matriochka/shots/gui_scroll.png" alt="The Artisan's Scroll" width="49%"> <img src="https://achedon12.github.io/matriochka/shots/gui_station_lightning_forge.png" alt="The Lightning Forge, World 4 station" width="49%"></p>
<!-- /gui -->

Want it set up in one click? The [Matriochka Pack](https://modrinth.com/modpack/matriochka-pack) (also on [CurseForge](https://www.curseforge.com/projects/1791269)) is the mod with its libraries, recipe pages and client performance mods, in a normal and a hard version.

