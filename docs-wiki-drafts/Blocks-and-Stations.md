# Blocks and stations

This page lists the structural blocks of the mod, the thirteen crafting stations with their conditions and recipes, and the terrain blocks of each world.

<!-- gui -->
## The stations in game

![Matrix Workbench](https://achedon12.github.io/matriochka/shots/gui_station_matrix_workbench.png)
![Spore Vat](https://achedon12.github.io/matriochka/shots/gui_station_spore_vat.png)
![Ash Foundry](https://achedon12.github.io/matriochka/shots/gui_station_ash_foundry.png)
![Jailer Table](https://achedon12.github.io/matriochka/shots/gui_station_jailer_table.png)
![Lightning Forge](https://achedon12.github.io/matriochka/shots/gui_station_lightning_forge.png)
![Dark Altar](https://achedon12.github.io/matriochka/shots/gui_station_dark_altar.png)
![Inverter](https://achedon12.github.io/matriochka/shots/gui_station_inverter.png)
![Abyssal Press](https://achedon12.github.io/matriochka/shots/gui_station_abyssal_press.png)
![Time Workshop](https://achedon12.github.io/matriochka/shots/gui_station_time_workshop.png)
![Terrain Anchor](https://achedon12.github.io/matriochka/shots/gui_station_terrain_anchor.png)
![Final Loom](https://achedon12.github.io/matriochka/shots/gui_station_final_loom.png)
![Soul Altar](https://achedon12.github.io/matriochka/shots/gui_station_soul_altar.png)
![Class Table](https://achedon12.github.io/matriochka/shots/gui_station_class_table.png)
<!-- /gui -->

## Structural blocks

| Block | What it does |
| --- | --- |
| World Soil 0 to 9 | The soil of each world. Tilled with a hoe, World Soil 0 accepts the World 1 Seed; Soils 1 to 9 are decorative. See [Core loop](Core-Loop#world-soil). |
| Planted Seed | The growing World 1 Seed, or a rite site drawn as the object set down for Worlds 2 to 10 (see [The way into each world](The-Way-Into-Each-World)). Not obtainable as an item. |
| World Block | Holds a world. Use it to enter. Only its group can break it; breaking it drops a Cracked Doll and leaves the world unstable for 20 minutes (half as many creatures again). A group has one World Block per world: a second Seed or rite of the same world waits until the first block is broken. Light level 9, immovable by pistons, huge blast resistance. A small turning island of its world floats above it, and it stays linked to its surroundings within 8 blocks (see [Effects between the scales](Effects-Between-the-Scales)). In the hardcore mode, breaking it deletes its world for the group. |
| Threshold | The exit platform inside each world. Use it to leave. Unbreakable, light level 12. |
| Soul Cradle | Respawn point inside a world, 3 charges. See [Doll of Life and death](Doll-of-Life-and-Death#soul-cradle). |
| Death Chest | Holds your items after a death inside a world. Unbreakable; using it gives everything back and removes it. |
| Nesting Chest | Three rows. Holds the two smaller nesting chests with their contents. See [Nesting systems](Nesting-Systems#nesting-chests). |
| Middle Nesting Chest | Two rows. Fits in a Nesting Chest, holds a Little one. |
| Little Nesting Chest | One row. Fits in the two larger nesting chests. |
| Lair Heart | Wakes the boss of its lair when someone comes close. See [Bosses](Bosses). |
| Guardian's Altar | Wakes the Block Guardian. Found in the Guardian's Sanctuary. Unbreakable. |
| Arena Altar | Wakes the world's boss. Found in the middle of each boss arena. Unbreakable. |
| Sealed Door | World 3 dungeon door. Unbreakable; opens with a Dungeon Key (always) or a Lockpick Kit (50%). |
| Painted Wood | Decoration. 8 Oak Planks and 1 Red Dye give 8. |
| Lacquer Block | Decoration. 4 Painted Wood and 1 Honeycomb give 4. |

## Stations

Each station is a sculpted 3D model that faces the player who places it, with moving parts, and each has a screen of its own (see [Station screens](#station-screens)). Every screen lists only the recipes you have unlocked, shows the station's condition (Ready / Not ready) and, in a bar, the recipe under the cursor. At every station but the Matrix Workbench you craft by clicking a recipe, and its ingredients are taken from your inventory; the Workbench is a 3 x 3 crafting table (see [Matrix Workbench](#matrix-workbench)). Creative players craft for free and ignore conditions. Every station works with a sound of its own (see [Sounds](Sounds)). With Just Enough Items installed, every station has a recipe page with the station as catalyst, and recipes that open with a boss say which one.

| Station | World | Mechanic | How to get it |
| --- | --- | --- | --- |
| Matrix Workbench | Surface | 3 x 3 crafting table for the way into each world; recipes unlock with cores. | Dropped by the Block Guardian |
| Class Table | Surface | Upgrades an item's class. | 1 Smithing Table (vanilla), 6 Iron Ingot (vanilla) (Block Guardian defeated) |
| Soul Altar | Surface | Purify or devour an item. | 4 Crying Obsidian (vanilla), 4 Gold Ingot (vanilla) (Block Guardian defeated) |
| Spore Vat | World 1 | Result depends on fermentation time. | 1 Cauldron (vanilla), 4 Iron Ingot (vanilla) (Block Guardian defeated) |
| Ash Foundry | World 2 | Keep the temperature in the green. | 1 Blast Furnace (vanilla), 4 Sporite, 2 Chitin (World 1 boss defeated) |
| Jailer's Table | World 3 | Reproduce the lock pattern. | 1 Smithing Table (vanilla), 4 Ash Ingot (World 2 boss defeated) |
| Lightning Forge | World 4 | Needs a lightning strike or storm essence. | 2 Lightning Rod (vanilla), 4 Ash Ingot, 4 Sealed Fragment (World 3 boss defeated) |
| Dark Altar | World 5 | Works only in complete darkness. | 4 Obsidian (vanilla), 4 Celestial Crystal, 2 Storm Essence (World 4 boss defeated) |
| Inverter | World 6 | Every gain comes with a flaw. | 2 Observer (vanilla), 6 Shadow Shard (World 5 boss defeated) |
| Abyssal Press | World 7 | Must be deep underwater. | 2 Piston (vanilla), 6 Unstable Alloy, 1 Inverted Crystal (World 6 boss defeated) |
| Time Workshop | World 8 | Accepts recipes at dawn and dusk. | 2 Clock (vanilla), 6 Abyssal Salt, 1 Pressure Pearl (World 7 boss defeated) |
| Terrain Anchor | World 9 | Stabilizes the ground (radius 16). | 1 Anvil (vanilla), 8 Temporal Sand, 1 Season Fragment (World 8 boss defeated) |
| Final Loom | World 10 | Weaves materials from every world. | 1 Loom (vanilla), 8 Terrain Fragment, 1 Terrain Heart (World 9 boss defeated) |

### Station screens

Every screen has its own layout and a live instrument in its niche.

| Station | Layout | Instrument |
| --- | --- | --- |
| Matrix Workbench | 3 x 3 grid, result slot and recipe drawers | - |
| Spore Vat | Jars on two shelves | A porthole into the vat |
| Ash Foundry | Crucibles | A thermometer |
| Jailer's Table | Key tags on chains | - |
| Lightning Forge | Plates in two arcs over an anvil | Charge cells |
| Dark Altar | Rune circles | An eye that opens in darkness |
| Inverter | Mirrored rows | - |
| Abyssal Press | A honeycomb of portholes | A depth gauge |
| Time Workshop | Medallions round a gear | A clock |
| Terrain Anchor | Strata | A seismograph |
| Final Loom | Banners | - |

### Automation

Every station with recipes (all but the Soul Altar and the Class Table, which work on your own souls and gear) can run by itself from hoppers, droppers or any mod that moves items through vanilla containers.

- **The kept recipe.** A station keeps one recipe: the last one you crafted there by hand, or the one you pick with the small gilded funnel that shows on a recipe under the cursor (lit when chosen; click it again to stop). Picking a recipe asks the same as crafting it: it must be unlocked, and the newest world's gear needs you to have taken part in its last boss.
- **In and out.** Ingredients go in from the top and the sides; each ingredient has its own two slots, so one never crowds out another, and anything the recipe does not use is refused. The result comes out from below. Below also gives back the ingredients of a recipe you no longer keep. A comparator reads how full the station is.
- **Crafting.** Once a second, when every ingredient is there, the output has room and the station's condition holds, it makes the recipe once, with the same yields and side effects as by hand.
- **Conditions.** They are those of crafting by hand: the Ash Foundry needs its heat in the green (and can still blow up when overheated), the Lightning Forge spends a charge per craft (lightning, or Storm Essence fed by a hopper into its fuel slot), the Dark Altar needs complete darkness, the Abyssal Press deep water, the Time Workshop dawn or dusk. The Spore Vat waits until its brew is ripe (one minute), then brews. The Jailer's Table makes one batch each time its lock pattern is entered.
- Breaking a station drops what its buffer holds. Automatic crafts do not count for quests.

### Matrix Workbench

The base crafting station. It makes the way into each world (the World 1 Seed and the nine rite objects), the other stations and the utility items.

It is a real 3 x 3 crafting table. Each recipe has a fixed pattern on the grid, built from its exact cost: each ingredient fills a symmetric group of cells, and the rarest one (a core, for example) takes the centre. The result shows in the result slot; take it, or shift-click it, like a crafted item. Its recipe drawers act as a recipe book: pressing one lays that recipe's pattern out on the grid from your inventory.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| World 1 Seed | 1 Guardian Core, 16 Iron Ingot (vanilla), 16 Oak Log (vanilla) | Block Guardian defeated |
| Ember Heart (World 2) | 1 Queen Core, 8 Sporite, 16 Spores | World 1 boss defeated |
| Jailer's Key (World 3) | 1 Titan Core, 8 Ash Ingot, 16 Blazing Rock | World 2 boss defeated |
| Storm Rod (World 4) | 1 Jailer Core, 8 Dungeon Key, 8 Sealed Fragment | World 3 boss defeated |
| Black Lantern (World 5) | 1 Storm King Core, 8 Storm Essence, 8 Celestial Crystal | World 4 boss defeated |
| Twin Mirrors (World 6) | 1 Light Eater Core, 8 Shadow Shard, 4 Diamond Fragment | World 5 boss defeated |
| Abyssal Pearl (World 7) | 1 Double Core, 8 Unstable Alloy, 4 Inverted Crystal | World 6 boss defeated |
| Sapling of the Four Seasons (World 8) | 1 Leviathan Core, 4 Pressure Pearl, 8 Abyssal Salt | World 7 boss defeated |
| Seismic Stake (World 9) | 1 Seasons Core, 8 Temporal Sand, 4 Season Fragment | World 8 boss defeated |
| Traveller's Matryoshka (World 10) | 1 Terrain Core, 1 Terrain Heart, 1 Key of the Last Doll | World 9 boss defeated |
| Soul Cradle | 4 Oak Planks (vanilla), 1 Wool Thread, 2 Roots | Always |
| Wool Thread x4 | 1 White Wool (vanilla) | Always |
| Return Thread x2 | 2 Wool Thread, 1 Ender Pearl (vanilla) | Always |
| Doll Mallet | 3 Painted Wood, 2 Stick (vanilla) | Block Guardian defeated |
| Chance Doll | 2 Oak Planks (vanilla), 1 Red Dye (vanilla), 2 Gold Ingot (vanilla) | Always |
| Artisan's Scroll | 3 Paper (vanilla) | Always |
| Class Table | 1 Smithing Table (vanilla), 6 Iron Ingot (vanilla) | Block Guardian defeated |
| Soul Altar | 4 Crying Obsidian (vanilla), 4 Gold Ingot (vanilla) | Block Guardian defeated |
| Nesting Chest | 2 Chest (vanilla), 2 Ash Ingot | World 2 boss defeated |
| Middle Nesting Chest | 1 Chest (vanilla), 1 Ash Ingot | World 2 boss defeated |
| Little Nesting Chest x2 | 1 Chest (vanilla), 2 Wool Thread | World 2 boss defeated |
| Refuge Doll | 8 Painted Wood, 4 Sealed Fragment, 2 Gold Ingot (vanilla) | World 3 boss defeated |
| Painted Wood x8 | 8 Oak Planks (vanilla), 1 Red Dye (vanilla) | Always |
| Lacquer Block x4 | 4 Painted Wood, 1 Honeycomb (vanilla) | Always |
| Spore Vat | 1 Cauldron (vanilla), 4 Iron Ingot (vanilla) | Block Guardian defeated |
| Ash Foundry | 1 Blast Furnace (vanilla), 4 Sporite, 2 Chitin | World 1 boss defeated |
| Jailer's Table | 1 Smithing Table (vanilla), 4 Ash Ingot | World 2 boss defeated |
| Lightning Forge | 2 Lightning Rod (vanilla), 4 Ash Ingot, 4 Sealed Fragment | World 3 boss defeated |
| Dark Altar | 4 Obsidian (vanilla), 4 Celestial Crystal, 2 Storm Essence | World 4 boss defeated |
| Inverter | 2 Observer (vanilla), 6 Shadow Shard | World 5 boss defeated |
| Abyssal Press | 2 Piston (vanilla), 6 Unstable Alloy, 1 Inverted Crystal | World 6 boss defeated |
| Time Workshop | 2 Clock (vanilla), 6 Abyssal Salt, 1 Pressure Pearl | World 7 boss defeated |
| Terrain Anchor | 1 Anvil (vanilla), 8 Temporal Sand, 1 Season Fragment | World 8 boss defeated |
| Final Loom | 1 Loom (vanilla), 8 Terrain Fragment, 1 Terrain Heart | World 9 boss defeated |
| World Soil 0 x4 | 4 Dirt (vanilla), 1 Bone Meal (vanilla) | Block Guardian defeated |
| World Soil 1 x4 | 4 Dirt (vanilla), 1 Spores | World 1 boss defeated |
| World Soil 2 x4 | 4 Dirt (vanilla), 1 Spores | World 2 boss defeated |
| World Soil 3 x4 | 4 Dirt (vanilla), 1 Spores | World 3 boss defeated |
| World Soil 4 x4 | 4 Dirt (vanilla), 1 Spores | World 4 boss defeated |
| World Soil 5 x4 | 4 Dirt (vanilla), 1 Spores | World 5 boss defeated |
| World Soil 6 x4 | 4 Dirt (vanilla), 1 Spores | World 6 boss defeated |
| World Soil 7 x4 | 4 Dirt (vanilla), 1 Spores | World 7 boss defeated |
| World Soil 8 x4 | 4 Dirt (vanilla), 1 Spores | World 8 boss defeated |
| World Soil 9 x4 | 4 Dirt (vanilla), 1 Spores | World 9 boss defeated |

### Class Table

Place a weapon, tool or armor piece in its slot, then **Upgrade class** (costs souls and Shell Shards), **Reroll** (costs a Chance Doll and souls) or **Add a layer** (lays a Lacquer Layer on an armor piece). An item without a class gets one for free on its first upgrade. Details: [Equipment classes](Equipment-Classes) and [Nesting systems](Nesting-Systems#layered-armor).

### Soul Altar

Place an item, then **Purify** (+karma) or **Devour** (-karma), or **Rebuild a layer** of your Doll of Life for 50 souls and 4 rare resources of the current world. The cost is shown under the button, red when you are short, and its tooltip lists the resources that count. Soul Shards and Soul Vessels are refused: use them instead. Details: [Souls and karma](Souls-and-Karma) and [Doll of Life and death](Doll-of-Life-and-Death).

### World stations

#### Spore Vat (World 1)

Always ready. The vat ferments one step per second, up to 600 (10 minutes), and every craft empties it. What a brew yields depends on how long it fermented: fresh (under 1 minute) gives the normal amount, ripe (1 to 5 minutes) half as much again, aged (5 minutes and more) twice as much. This counts for antidotes, dishes and other brews; gear is not brewed and always comes out one piece. The Filter Mask needs at least one minute of fermentation.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Antidote x2 | 4 Spores, 2 Glass Bottle (vanilla) | Always |
| Filter Mask | 2 Chitin, 8 Spores, 2 String (vanilla) | Always |
| Root Broth x2 | 3 Roots, 2 Bowl (vanilla) | Always |
| Sporite Sword | 8 Chitin, 1 Stick (vanilla) | Always |
| Chitin Helmet | 5 Chitin | Always |
| Chitin Chestplate | 8 Chitin | Always |
| Chitin Leggings | 7 Chitin | Always |
| Chitin Boots | 4 Chitin | Always |
| Sporite Sword | 8 Sporite, 1 Roots | Always |

#### Ash Foundry (World 2)

Needs 1 to 3 heat sources touching one of its six faces (lava, magma block, fire, soul fire or campfire). With 3 sources, each craft has a 1 in 4 chance to blow the foundry up (explosion power 2.5).

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Ash Ingot | 1 Giant Ore, 1 Blazing Rock | Always |
| Cooling Water x2 | 2 Ice (vanilla), 2 Glass Bottle (vanilla) | Always |
| Drill | 6 Ash Ingot, 4 Blazing Rock, 4 Redstone (vanilla) | Always |
| Ice Bread x2 | 2 Bread (vanilla), 1 Ice (vanilla) | Always |
| Ash Hammer | 8 Ash Ingot, 1 Stick (vanilla) | Always |
| Thermal Helmet | 5 Ash Ingot | Always |
| Thermal Chestplate | 8 Ash Ingot | Always |
| Thermal Leggings | 7 Ash Ingot | Always |
| Thermal Boots | 4 Ash Ingot | Always |

#### Jailer's Table (World 3)

A three-pin lock pattern (pins 0 to 3) is rolled for the table. Press the pins in the right order; a wrong pin resets the input. The pattern changes after every craft.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Labyrinth Map | 4 Paper (vanilla), 1 Sealed Fragment | Always |
| Lockpick Kit x2 | 4 Iron Nugget (vanilla), 1 Sealed Fragment | Always |
| Portable Trap x2 | 2 Iron Ingot (vanilla), 1 Sealed Fragment | Always |
| Dungeon Key | 3 Sealed Fragment, 4 Gold Nugget (vanilla) | Always |
| Cell Ration x2 | 1 Bread (vanilla), 1 Cooked Beef (vanilla) | Always |
| Jailer's Blade | 8 Sealed Fragment, 1 Stick (vanilla) | Always |
| Jailer Helmet | 5 Sealed Fragment | Always |
| Jailer Chestplate | 8 Sealed Fragment | Always |
| Jailer Leggings | 7 Sealed Fragment | Always |
| Jailer Boots | 4 Sealed Fragment | Always |
| Sealed Shackle | 6 Sealed Fragment, 1 Dungeon Key, 2 Iron Chain (vanilla) | Always |

#### Lightning Forge (World 4)

Stores charge, up to 8: +1 every 10 seconds during a thunderstorm when the sky is open above it, or +2 for each **Storm Essence** you hold against it. Each craft uses 1 charge; crafting with an empty forge burns a Storm Essence from your inventory automatically, so the forge shows as ready when you carry one. It also makes **Lacquer Layers** for layered armor (see [Nesting systems](Nesting-Systems#layered-armor)).

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Glider | 8 Ray Membrane, 4 Stick (vanilla), 2 Storm Essence | Always |
| Grappling Hook | 2 Celestial Crystal, 8 String (vanilla), 3 Iron Ingot (vanilla) | Always |
| Cloud Fruit x2 | 2 Apple (vanilla), 1 Storm Essence | Always |
| Lacquer Layer x2 | 1 Celestial Crystal, 1 Storm Essence, 2 Honeycomb (vanilla) | Always |
| Lightning Lance | 8 Celestial Crystal, 1 Stick (vanilla) | Always |
| Celestial Helmet | 5 Celestial Crystal | Always |
| Celestial Chestplate | 8 Celestial Crystal | Always |
| Celestial Leggings | 7 Celestial Crystal | Always |
| Celestial Boots | 4 Celestial Crystal | Always |
| Storm Censer | 4 Storm Essence, 2 Celestial Crystal, 2 Ray Membrane | Always |

#### Dark Altar (World 5)

Works only in complete darkness: the light level above the altar must be 0.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Solar Lantern | 4 Storm Essence, 1 Lantern (vanilla), 2 Gold Ingot (vanilla) | Always |
| Sonar | 4 Shadow Shard, 2 Amethyst Shard (vanilla) | Always |
| Silence Balm x3 | 1 Shadow Shard, 1 Honey Bottle (vanilla) | Always |
| Diamond (vanilla) | 4 Diamond Fragment | Always |
| Mute Mushroom x2 | 2 Brown Mushroom (vanilla), 1 Shadow Shard | Always |
| Shadow Blade | 8 Shadow Shard, 1 Stick (vanilla) | Always |
| Nocturnal Helmet | 5 Shadow Shard | Always |
| Nocturnal Chestplate | 8 Shadow Shard | Always |
| Nocturnal Leggings | 7 Shadow Shard | Always |
| Nocturnal Boots | 4 Shadow Shard | Always |

#### Inverter (World 6)

Every gain has a flaw: anything with durability comes out already 25% worn. The Inverter also swaps properties: place two pieces of the **same kind** (two armor pieces, two weapons or two tools) in the two sockets of its niche and press **Invert**. They trade their class, class level and enchantments; each loses a quarter of its durability and counts one more class change (Chance Doll rerolls cost more), and an enchantment the other piece cannot carry is lost.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Gravity Boots | 6 Unstable Alloy, 2 Inverted Crystal | Always |
| Stabilizer x3 | 1 Unstable Alloy, 2 Quartz (vanilla) | Always |
| Flipped Apple x2 | 2 Apple (vanilla), 1 Inverted Crystal | Always |
| Mirror Blade | 8 Unstable Alloy, 1 Stick (vanilla) | Always |
| Mirror Helmet | 5 Unstable Alloy | Always |
| Mirror Chestplate | 8 Unstable Alloy | Always |
| Mirror Leggings | 7 Unstable Alloy | Always |
| Mirror Boots | 4 Unstable Alloy | Always |

#### Abyssal Press (World 7)

Must be deep underwater: water directly above the press and 8 blocks above it. Its **Refill** button fills a snorkel helmet's tank to the brim (the one on your head, otherwise the emptiest one you carry).

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Oxygen Capsule x3 | 4 Kelp (vanilla), 1 Abyssal Salt | Always |
| Thruster | 2 Pressure Pearl, 4 Unstable Alloy | Always |
| Pressure Pearl | 6 Abyssal Salt, 2 Prismarine Crystals (vanilla) | Always |
| Apnea Kelp x3 | 3 Dried Kelp (vanilla), 1 Abyssal Salt | Always |
| Salt Snorkel Helmet | 5 Abyssal Salt, 2 Glass Pane (vanilla), 2 Kelp (vanilla) | Always |
| Nacre Snorkel Helmet | 5 Nacre, 2 Glass Pane (vanilla), 2 Kelp (vanilla) | Always |
| Cobalt Snorkel Helmet | 5 Abyssal Cobalt, 2 Glass Pane (vanilla), 2 Kelp (vanilla) | Always |
| Pearl Snorkel Helmet | 5 Pressure Pearl, 2 Glass Pane (vanilla), 2 Kelp (vanilla) | Always |
| Trench Trident | 8 Abyssal Salt, 1 Stick (vanilla) | Always |
| Diving Chestplate | 8 Abyssal Cobalt | Always |
| Diving Leggings | 7 Abyssal Cobalt | Always |
| Diving Boots | 4 Abyssal Cobalt | Always |

#### Time Workshop (World 8)

Accepts recipes only at dawn (time 22500 to 1500) or dusk (11500 to 13500) on the clock of the world it stands in. Inside World 8 that clock runs three times faster.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Hourglass | 6 Temporal Sand, 2 Glass (vanilla), 1 Season Fragment | Always |
| Season Preserve x3 | 1 Season Fragment, 3 Glass Bottle (vanilla) | Always |
| Season Jam x2 | 4 Sweet Berries (vanilla), 1 Temporal Sand | Always |
| Scythe of Seasons | 8 Temporal Sand, 1 Stick (vanilla) | Always |
| Seasonal Helmet | 5 Temporal Sand | Always |
| Seasonal Chestplate | 8 Temporal Sand | Always |
| Seasonal Leggings | 7 Temporal Sand | Always |
| Seasonal Boots | 4 Temporal Sand | Always |
| Wreath of Seasons | 2 Season Fragment, 6 Temporal Sand, 1 Season Preserve | Always |

#### Terrain Anchor (World 9)

No condition to craft. Once placed, no ground zone within 16 blocks of it ever moves (see [World 9](World-9#the-rule-tremor)), and it stops Foundation Eaters within 6 blocks.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Anchor x4 | 2 Terrain Fragment, 2 Iron Ingot (vanilla) | Always |
| Grip Boots | 6 Terrain Fragment, 1 Leather Boots (vanilla) | Always |
| Anchor Bread x2 | 2 Bread (vanilla), 1 Terrain Fragment | Always |
| Seismic Mace | 8 Terrain Fragment, 1 Stick (vanilla) | Always |
| Living Rock Helmet | 5 Terrain Fragment | Always |
| Living Rock Chestplate | 8 Terrain Fragment | Always |
| Living Rock Leggings | 7 Terrain Fragment | Always |
| Living Rock Boots | 4 Terrain Fragment | Always |

#### Final Loom (World 10)

No condition. It combines the final materials with gear from earlier worlds.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Artisan's Blade | 8 Artisan's Thread, 1 Artisan's Shard, 1 Sporite Sword | Always |
| Artisan Helmet | 5 Artisan's Thread, 1 Chitin Helmet | Always |
| Artisan Chestplate | 8 Artisan's Thread, 1 Celestial Chestplate | Always |
| Artisan Leggings | 7 Artisan's Thread, 1 Diving Leggings | Always |
| Artisan Boots | 4 Artisan's Thread, 1 Gravity Boots | Always |
| Unfinished Effigy | 6 Artisan's Thread, 1 Artisan's Shard, 4 Wool Thread | Always |
| Workshop Feast | 1 Root Broth, 1 Ice Bread, 1 Cloud Fruit, 1 Season Jam | Always |

## Terrain blocks

Ores need the correct tool. Stone, brick and station blocks are mined with a pickaxe, moss, sand and soils with a shovel, wood with an axe. Every world also generates its glowing block in small patches.

### World 1: Toxic Jungle

| Block | Type | Drops |
| --- | --- | --- |
| Spore Moss | Soft (shovel) | itself |
| Rootstone | Stone (pickaxe) | itself |
| Spore Bloom | Light level 13 | itself |
| Sporite Ore | Ore (pickaxe, correct tool needed) | Sporite |
### World 2: Giant Veins

| Block | Type | Drops |
| --- | --- | --- |
| Ashrock | Stone (pickaxe) | itself |
| Ember Stone | Light level 13 | itself |
| Giant Vein | Giant ore (pickaxe, correct tool needed) | Giant Ore |
| Blazing Rock Ore | Ore (pickaxe, correct tool needed) | Blazing Rock |
### World 3: Endless Dungeon

| Block | Type | Drops |
| --- | --- | --- |
| Dungeon Brick | Brick (pickaxe) | itself |
| Sealed Brick | Unbreakable | itself |
| Cold Lamp | Light level 13 | itself |
| Sealed Ore | Ore (pickaxe, correct tool needed) | Sealed Fragment |
### World 4: Storm Archipelago

| Block | Type | Drops |
| --- | --- | --- |
| Skygrass | Soft (shovel) | itself |
| Cloudstone | Stone (pickaxe) | itself |
| Storm Glass | Light level 13 | itself |
| Celestial Crystal Ore | Ore (pickaxe, correct tool needed) | Celestial Crystal |
### World 5: Lightless Deep

| Block | Type | Drops |
| --- | --- | --- |
| Umbral Stone | Stone (pickaxe) | itself |
| Umbral Moss | Soft (shovel) | itself |
| Faint Glow | Light level 13 | itself |
| Diamond Fragment Ore | Ore (pickaxe, correct tool needed) | Diamond Fragment |
| Spent Glow | What a glowing block you placed becomes once its light burns out | itself |
### World 6: Upside Realm

| Block | Type | Drops |
| --- | --- | --- |
| Inverted Stone | Stone (pickaxe) | itself |
| Mirror Glass | Glass, see-through | itself |
| Prism Moss | Soft (shovel) | itself |
| Unstable Alloy Ore | Ore (pickaxe, correct tool needed) | Unstable Alloy |
### World 7: Pressure Ocean

| Block | Type | Drops |
| --- | --- | --- |
| Abyssal Sand | Soft (shovel) | itself |
| Trench Rock | Stone (pickaxe) | itself |
| Pressure Coral | Light level 13 | itself |
| Abyssal Salt Ore | Ore (pickaxe, correct tool needed), y -50 to 200 | Abyssal Salt |
| Nacre Vein | Ore, in the reefs and the upper floor (y 110 to 220) | Nacre |
| Abyssal Cobalt Ore | Ore, deeper down (y -20 to 110) | Abyssal Cobalt |
| Pearl Bed | Ore, in the deep rock and sand (y -50 to 60), rare | Pressure Pearl |
| Air Vent | On the sea floor, light level 6; breathes out air that refills a snorkel helmet | itself |
### World 8: Hastened Seasons

| Block | Type | Drops |
| --- | --- | --- |
| Chrono Grass | Soft (shovel) | itself |
| Hourstone | Stone (pickaxe) | itself |
| Temporal Sand Block | Soft (shovel) | itself |
| Season Ore | Ore (pickaxe, correct tool needed) | Season Fragment |
### World 9: Restless Ground

| Block | Type | Drops |
| --- | --- | --- |
| Living Rock | Stone (pickaxe) | itself |
| Flesh Stone | Soft (shovel) | itself |
| Pulse Vein | Light level 13 | itself |
| Terrain Ore | Ore (pickaxe, correct tool needed) | Terrain Fragment |
### World 10: The Giant Workshop

| Block | Type | Drops |
| --- | --- | --- |
| Giant Plank | Wood (axe) | itself |
| Workshop Felt | Soft (shovel) | itself |
| Lacquer Glow | Light level 13 | itself |
| Thread Spool | Ore (pickaxe, correct tool needed) | Artisan's Thread |
