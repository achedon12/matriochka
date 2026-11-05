# Changelog

## Unreleased

- World 3: the halls really move. Every five minutes, 8 x 8 hall sections 16 to 40 blocks from each player swap places or turn, opening and closing passages; dust falls on them during the ten-second warning. Rooms, structures, locks, chests, stations, sealed doors and anything a player built never move, and no section next to a player does.
- World 5: the lights you bring burn out. A placed torch, lantern, candle, campfire or glowing block lasts one minute and smokes for its last five seconds: torches crumble to a stick, campfires and candles are snuffed (relight them), glowing blocks become the new Spent Glow, the rest falls back as an item. The Deep's own blocks keep glowing, and a lit Solar Lantern now carries a real light with you. The Darkness pulse only hits players standing in the dark.
- World 6: gravity changes by zone. The realm is cut into 32 x 32 columns and about a third of them are upside down, the pattern changing every 90 seconds: inside one, players, creatures and dropped items fall upward and stand on ceilings, up to 16 blocks above the ground. Purple sparks trace the borders. Gravity Boots, the Stabilizer and the Flipped Apple still protect you; Ceiling Walk and Vertigo come from the real thing.
- World 9: whole 16 x 16 zones move. Every minute up to three zones around each player rise, sink, slide or close their chasms, carrying players, creatures and builds along (My Base Walks) without ever burying anyone. Terrain Anchors (16 blocks), Anchors and Anchor Bread (4 blocks around you) and Grip Boots hold the ground still; zones with chests, stations or unbreakable blocks never move.
- Blocks placed by players are now remembered in worlds 3, 5, 9 and 10, so the moving worlds can protect, burn or carry them.
- New in-game check of these four mechanics: `./gradlew runClientGameTest -Prules`.
- World 7, the Pressure Ocean, is now entirely under water: the sea fills it from the floor up to y 240, with no dry land. The sea floor rolls around y 140, with reef crowns, rare trenches below y 20, caves and air pockets underneath, kelp forests, coral reefs and spires of glowing Pressure Coral.
- You arrive in a diving chamber on the sea floor: an air-filled glass dome around the Threshold, with a door that holds the water back, a chest of supplies and an Air Vent outside.
- Snorkel helmets: the only way to breathe for long under water. One per ore of the world (Abyssal Salt, and the new Nacre Vein, Abyssal Cobalt Ore and Pearl Bed), crafted at the Abyssal Press. They breathe for you from a tank that drains under water and refills in air pockets, in bubble columns, over Air Vents, with an Oxygen Capsule or with the press's new Refill button. They are fragile: hits wear them fast. Higher tiers hold more air, wear less and let you dive deeper.
- Without a helmet your breath lasts about half a minute under water. The HUD shows the helmet's tank in the oxygen vial and your breath as a thin line under it; the helmet's tooltip shows the air left.
- The Diving suit keeps its chestplate, leggings and boots (now made of Abyssal Cobalt): each piece lets you dive 22 blocks deeper. The helmet slot is the snorkel's.
- Every World 7 creature swims, never drowns and spawns in open water; the Bell Crab is now a sea creature too. Lantern Shoals and Glow Jellies, harmless wildlife, light the deep.
- World 7 structures stand on the sea floor instead of floating at the surface, and their dry refuges no longer spring leaks. The Pressure Leviathan sleeps in a temple at the bottom of a trench cut for it, reached by glowing coral posts.
- Divers live under water and sell a first helmet. Common World 7 chests sometimes hold a worn one.
- "Pressurized" now asks you to breathe through a snorkel helmet; "Last Breath" counts the helmet's tank.
- The Artisan's Journal is written: fifty pages in English and French, five per world (a site note, the portrait of the apprentice who became the boss, an observation, a coded page and a letter to the traveller), telling the story world by world. A new Pages tab of the Journal lists the pages found and reads them; the coded page of each world stays in the Artisan's cipher until you carry that world's core or your group beats its boss.
- The ten hidden dolls nest: hold the smallest in your main hand and the next one in the other hand, then use it. A doll that does not belong rattles and is refused. The order is hinted by the notches under each doll, the coded pages, the Carver's Note left beside every hidden doll and what each world's people say when you show them their doll. The ten closed together make the Whole Matryoshka.
- World 0, the smallest doll, opens with the Whole Matryoshka once the Unfinished has fallen: a sealed place of painted wood with three chambers of elite guards from every prison and the Artisan's own room. Its rule, Obsession, feeds on every tool you hold and every blow you strike; only empty hands calm it. Its encounter cannot be won by fighting.
- Three endings. After the Unfinished, your karma decides: Sealed (two more hearts) or Absorbed (stronger strikes, but your karma can never rise again). World 0 holds the third, Set Down the Tools, and the Blank Scroll. Each ending plays a crawl on the Scroll, then the credits, and has its advancement in a new Endings tab. The hidden achievement Set Down the Tools now belongs to the third ending.
- New Cycle: after an ending, the Journal can begin the next cycle. Your group starts over from the Guardian in fresh worlds where creatures and bosses have 50% more health and 25% more damage per cycle. You keep your souls, karma, pages, quests, endings and gear; the cores, Seeds, World Soils, offerings and keys of the old cycle are taken back, and its World Blocks crumble.
- New commands for operators: `/matriochka world zero`, `/matriochka ending <seal|absorb|tools>`, `/matriochka cycle show|begin`.
- An in-game check of all this: `./gradlew runClientGameTest -Pstory`.
- The Refuge Doll: every player who fights the Grand Jailer gets a pocket base for the group, a lacquered room that grows after worlds 5, 7 and 9 and stays shut while a boss is awake nearby.
- Layered armor: Lacquer Layers from the Lightning Forge are laid on armor at the Class Table; when the outer layer breaks the next takes over. The class decides how many a piece holds.
- Nesting chests come in three sizes; each holds the smaller ones with their contents, keeps everything when broken, and sorts items into the smaller chests by type.
- The Drill mines 3x3 squares and burns Blazing Rock.
- The Lightning Forge takes Storm Essence as a charge, Spore Vat brews give more when ripe or aged, and the Inverter swaps the class, level and enchantments of two pieces at a cost.
- Karma reaches the Surface: villager prices, refusals and reactions follow it, and killing an innocent costs karma. Black markets open from karma -25, and a Karma Paths chapter adds three mutual-help and three pact quests.
- Reaper gear harvests extra souls, Prowler gear dodges blows, and class upgrades also need Shell Shards, left by every boss.
- Bosses attack faster with more players, and the newest world's gear asks to have taken part in its last boss fight.
- Group leaders can kick, hand over the lead and disband; administrators can list, repair, move and reset worlds and reset bosses.
- Villager trades involving diamonds wait until World 5.
- Difficulty modes: story keeps the inventory on death; hardcore makes death permanent and a broken World Block deletes its world.
- Gear class levels read from item components are bounded.

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
