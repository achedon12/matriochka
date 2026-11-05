# Changelog

## Unreleased

- The Artisan's Journal is written: fifty pages in English and French, five per world (a site note, the portrait of the apprentice who became the boss, an observation, a coded page and a letter to the traveller), telling the story world by world. A new Pages tab of the Journal lists the pages found and reads them; the coded page of each world stays in the Artisan's cipher until you carry that world's core or your group beats its boss.
- The ten hidden dolls nest: hold the smallest in your main hand and the next one in the other hand, then use it. A doll that does not belong rattles and is refused. The order is hinted by the notches under each doll, the coded pages, the Carver's Note left beside every hidden doll and what each world's people say when you show them their doll. The ten closed together make the Whole Matryoshka.
- World 0, the smallest doll, opens with the Whole Matryoshka once the Unfinished has fallen: a sealed place of painted wood with three chambers of elite guards from every prison and the Artisan's own room. Its rule, Obsession, feeds on every tool you hold and every blow you strike; only empty hands calm it. Its encounter cannot be won by fighting.
- Three endings. After the Unfinished, your karma decides: Sealed (two more hearts) or Absorbed (stronger strikes, but your karma can never rise again). World 0 holds the third, Set Down the Tools, and the Blank Scroll. Each ending plays a crawl on the Scroll, then the credits, and has its advancement in a new Endings tab. The hidden achievement Set Down the Tools now belongs to the third ending.
- New Cycle: after an ending, the Journal can begin the next cycle. Your group starts over from the Guardian in fresh worlds where creatures and bosses have 50% more health and 25% more damage per cycle. You keep your souls, karma, pages, quests, endings and gear; the cores, Seeds, World Soils, offerings and keys of the old cycle are taken back, and its World Blocks crumble.
- New commands for operators: `/matriochka world zero`, `/matriochka ending <seal|absorb|tools>`, `/matriochka cycle show|begin`.
- An in-game check of all this: `./gradlew runClientGameTest -Pstory`.

## 0.2.0 (alpha)

- Every creature now has its own signature attacks: 160 in all, three per creature and four per elite, none shared. Each has its own wind-up animation, numbers, afflictions, particles and sound, drawn from what the creature is.
- Two ways to meet a boss. The Grand Jailer, the Storm King, the Master of Seasons and the Unfinished are woken at the arena altar with an offering crafted at their world's station (Sealed Shackle, Storm Censer, Wreath of Seasons, Unfinished Effigy), through a three-second ritual; every fight costs one offering. The six other bosses sleep in their own lairs (a hive, a forge-hall, a lightless pit, a hall of mirrors, a sunken trench temple and a cavern of living rock), woken by the lair heart and guarding a treasure alcove that opens when they fall.
- The altar arena is rebuilt with an inlaid floor, a colonnade, braziers and an entrance arch.
- The eleven bosses are rebuilt as full rigs with joints, secondary motion and glowing eyes and cores.
- Texture generation is reproducible; the build no longer needs a local copy of Minecraft data.
- New releases are announced automatically in the Discord changelog channel.
- Every achievement can now be earned. The boss challenges ("beat the Queen without a mask", "the Titan without touching lava"...) are tracked over the whole fight; Forgotten Plate, A Crumb and Set Down the Tools have new conditions that exist in the game.
- Every world offers its five Journal pages: the exploration structures hold pages 1 to 3, the story structures pages 4 and 5.
- The ten world dishes now give their effects.
- The Grappling Hook pulls creatures toward you.
- The Doll Peddler wanders the Surface like a trader.
- Once unmasked, Mimics and Crawling Blocks chase you. The Dusk Shade only comes out at dusk.
- A broken world stays unstable for 20 minutes, with more creatures around.
- Only its group can break a World Block or a Soul Cradle; a group has one World Block per world; a cradle stays shut while a boss is awake near it.
- The config is applied: creature health and damage multipliers, group size, and four difficulty modes (story, normal, nightmare, hardcore).
- No more diamonds in vanilla loot chests.
- A day in World 8 lasts 8 minutes, as designed.

## 0.1.0 (alpha)

First public alpha for Minecraft 26.3 (Fabric).

- Ten nested worlds, each in its own dimension with its own terrain, biome, sky and rule.
- World Soil, Seeds with hatching conditions, World Blocks, Thresholds, Return Threads and Cracked Dolls.
- 50 creatures and 11 bosses with GeckoLib models and animations.
- Boss attack system with telegraphs, openings, phases and multiplayer scaling.
- 13 stations with their own mechanics and recipes.
- Equipment classes, Class Table and Chance Doll.
- Souls, karma, Soul Altar and karma-aware merchants for every world.
- Doll of Life, Soul Cradle and death chests.
- 100 procedural structures, journal pages and hidden dolls.
- 64 optional quests and 100 achievements.
- Progression gates for diamonds, enchanting, the Nether, the End, elytra and beds.
- English and French translations.
