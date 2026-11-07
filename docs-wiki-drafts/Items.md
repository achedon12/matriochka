# Items

Every Matriochka item, grouped by world, with its rarity, soul value and what it does in the code. Rarity sets the soul value used by the Soul Altar (see [Souls and karma](Souls-and-Karma)).

| Rarity | Souls | Tooltip color |
| --- | --- | --- |
| Common | 1 | white |
| Rare | 10 | aqua |
| Epic | 30 | light purple |
| Legendary | 100 | gold |

## Gear by world

Weapons are sword-type items; armor comes in sets of four. Toughness is spread evenly over the four pieces, and the bonus health is split 15% helmet, 40% chestplate, 30% leggings, 15% boots (rounded).

| World | Weapon damage | Armor per piece (H / C / L / B) | Armor total | Toughness total | Bonus health | Tool tier |
| --- | --- | --- | --- | --- | --- | --- |
| World 1 | 7 | 3 / 6 / 4 / 3 | 16 | 1 | 0 | iron |
| World 2 | 9 | 3 / 6 / 5 / 3 | 17 | 2 | 0 | iron |
| World 3 | 11 | 3 / 7 / 5 / 3 | 18 | 3 | 2 | iron |
| World 4 | 13 | 3 / 7 / 6 / 3 | 19 | 4 | 4 | iron |
| World 5 | 16 | 4 / 8 / 5 / 3 | 20 | 6 | 6 | netherite |
| World 6 | 19 | 4 / 8 / 6 / 4 | 22 | 8 | 8 | netherite |
| World 7 | 23 | 4 / 9 / 7 / 4 | 24 | 10 | 12 | netherite |
| World 8 | 28 | 5 / 10 / 7 / 4 | 26 | 12 | 16 | netherite |
| World 9 | 33 | 5 / 11 / 8 / 4 | 28 | 14 | 20 | netherite |
| World 10 | 40 | 5 / 11 / 9 / 5 | 30 | 16 | 24 | netherite |

Weapons need 8 of the world's base resource and a stick; a full armor set needs 24 (5 + 8 + 7 + 4). World 7 is the exception: the Diving suit has no helmet (the head slot belongs to the snorkel helmets) and is made of Abyssal Cobalt. The Spore Vat has a second sword recipe that uses 8 Sporite and 1 Roots.

## Cores

| Core | From | Rarity | Use |
| --- | --- | --- | --- |
| Guardian Core | Surface | legendary | Opens the way into World 1 (World 1 Seed) |
| Queen Core | World 1 | legendary | Opens the way into World 2 (Ember Heart) |
| Titan Core | World 2 | legendary | Opens the way into World 3 (Jailer's Key) |
| Jailer Core | World 3 | legendary | Opens the way into World 4 (Storm Rod) |
| Storm King Core | World 4 | legendary | Opens the way into World 5 (Black Lantern) |
| Light Eater Core | World 5 | legendary | Opens the way into World 6 (Twin Mirrors) |
| Double Core | World 6 | legendary | Opens the way into World 7 (Abyssal Pearl) |
| Leviathan Core | World 7 | legendary | Opens the way into World 8 (Sapling of the Four Seasons) |
| Seasons Core | World 8 | legendary | Opens the way into World 9 (Seismic Stake) |
| Terrain Core | World 9 | legendary | Opens the way into World 10 (Traveller's Matryoshka) |
| Unfinished Core | World 10 | legendary | Trophy |

Cores glow, are fire resistant and stack to 1. The Soul Altar refuses them.

## The way into each world

| Object | Item id | Where it goes | What it waits for |
| --- | --- | --- | --- |
| World 1 Seed | `seed_1` | Planted on tilled World Soil 0 | Water (any water block) within 4 blocks horizontally and 1 block vertically of the seed. |
| Ember Heart (World 2) | `seed_2` | Set down within 3 blocks of lava | At least 4 Ashrock around it. |
| Jailer's Key (World 3) | `seed_3` | Set against an iron door | A redstone signal (a lever, a button). |
| Storm Rod (World 4) | `seed_4` | On top of a lightning rod, under the open sky | A storm, or a Storm Essence fed to it. |
| Black Lantern (World 5) | `seed_5` | Set down in complete darkness | At least 4 Spent Glow within 2 blocks. |
| Twin Mirrors (World 6) | `seed_6` | Between two glass blocks facing each other, two blocks away on either side | Nothing more. |
| Abyssal Pearl (World 7) | `seed_7` | Dropped into water | Water at least 3 blocks deep. |
| Sapling of the Four Seasons (World 8) | `seed_8` | Planted on grass or dirt | Dawn or dusk on the overworld clock: time 22500 to 1500, or 11500 to 13500. |
| Seismic Stake (World 9) | `seed_9` | Driven into stone or deepslate below y 40 | Nothing more. |
| Traveller's Matryoshka (World 10) | `seed_10` | Anywhere | Nothing: it is ready at once. |

All ten stack to 16 and are fire resistant. Recipes: [Core loop](Core-Loop#the-way-into-each-world). Rites, waiting and feeding: [The way into each world](The-Way-Into-Each-World).

## Hidden Dolls

There are ten Hidden Dolls, one in the vault chest of each world's secret structure, beside a Carver's Note. The tooltip of each tells how many notches are carved under its base. Nested together from the smallest to the largest, they become the Whole Matryoshka, the key to [World 0](World-0). See [Hidden Dolls](Hidden-Dolls).

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Hidden Doll 1 to 10 | secret | - | One per world. Hold the smallest in your main hand and the next in the other hand, then use it. The Soul Altar refuses them. |
| Nested Dolls | secret | - | The nest being built (2 / 10 to 9 / 10). Hold it in your main hand and the next hidden doll in the other, then use it. |
| The Whole Matryoshka | secret | legendary | The ten dolls closed together. Use it once your group has beaten the Unfinished to enter World 0. |
| Blank Scroll | secret | - | Given by the third ending, Set Down the Tools. Nothing is written on it. |

## Surface and common items

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Artisan's Scroll | guide | - | Explains the mod. Becomes the Journal. In code: Right-click opens the Scroll (5 pages). Given once on first join. Replaced by the Journal when the Block Guardian dies. |
| Artisan's Journal | guide | - | Story, objectives, quests and karma. In code: Right-click opens the Journal: objective, quests, karma, worlds, scroll and Journal pages. See [The Artisan's Journal](Artisans-Journal). |
| Life Doll | doll | legendary (100) | Breaks a layer instead of letting you die. In code: Creative tab icon only. Your doll layers are stored on the player, not in this item. |
| Return Thread | consumable | common (1) | Brings you back to the world block. In code: Right-click inside a world: teleports you to the world block you entered from. Consumed. |
| Chance Doll | consumable | rare (10) | Rerolls the class of an item. In code: Consumed by the Class Table to reroll a class. |
| Cracked Doll | doll | - | Holds the access to a broken world. In code: Right-click a block face to put the broken World Block back. Keeps its world and owner. |
| Journal Page | page | - | A lost page of the Artisan's Journal. In code: Pages found in structure chests are recorded in the Journal's Pages tab when they are in your inventory. Fifty pages, five per world. |
| Wool Thread | resource | common (1) | Used for cradles and threads. |
| Shell Shard | resource | epic (30) | Left by a fallen boss: 3 for every player in the fight, 2 more from a mutated boss. Every class upgrade needs some (see [Equipment classes](Equipment-Classes)). |
| Mutated Scale | gem | epic (30) | Shed by a mutated boss (1 or 2). Rich in soul. See [World variants and mutations](World-Variants-and-Mutations). |
| Doll Mallet | tool | rare | Made at the Matrix Workbench (3 Painted Wood, 2 sticks). Use it on a World Block of your group to shake the world inside and hinder those in it. See [Effects between the scales](Effects-Between-the-Scales#shaking-the-block-on-purpose). |
| Soul Shard | soul | common | Found in structure chests. Holds 5 souls: use it to free them (sneak: the whole stack). Neutral souls, refused by the Soul Altar. |
| Soul Vessel | soul | rare | Found in vault chests. Holds 20 souls, freed the same way. See [Souls and karma](Souls-and-Karma#souls-in-structure-chests). |

## World 1: Toxic Jungle

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Spores | resource | common (1) | Base of antidotes. |
| Roots | resource | common (1) | Living wood. |
| Sporite | gem | rare (10) | World 1 ore. |
| Chitin | resource | rare (10) | Armor of the world. |
| Antidote | consumable | common (1) | Reduces toxin by 50. In code: Right-click: toxin -50. |
| Filter Mask | mask | rare (10) | Halves toxin gain. In code: Head slot. Halves toxin gain. |
| Sporite Sword | weapon | rare (10) | Sword-type weapon, about 7 attack damage. Gets a random class when crafted. |
| Chitin Helmet | armor | rare (10) | 3 armor, 0.25 toughness |
| Chitin Chestplate | armor | rare (10) | 6 armor, 0.25 toughness |
| Chitin Leggings | armor | rare (10) | 4 armor, 0.25 toughness |
| Chitin Boots | armor | rare (10) | 3 armor, 0.25 toughness |
| Root Broth | food | common (1) | Slows toxin for 5 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
## World 2: Giant Veins

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Blazing Rock | resource | common (1) | Powerful fuel. |
| Giant Ore | resource | rare (10) | A whole vein in one block. |
| Ash Ingot | ingot | rare (10) | Base of World 2 gear. |
| Cooling Water | consumable | common (1) | Reduces heat by 50. In code: Right-click: heat -50. |
| Drill | drill | epic (30) | Mines 3x3, burns Blazing Rock. In code: mines a 3 x 3 square across the face you look at; one Blazing Rock (taken from your inventory when the tank is empty) feeds 8 squares. Without fuel, or when sneaking, it mines one block like a pickaxe. The tooltip shows the fuel left. |
| Ash Hammer | weapon | rare (10) | Sword-type weapon, about 9 attack damage. Gets a random class when crafted. |
| Thermal Helmet | armor | rare (10) | 3 armor, 0.5 toughness. Halves heat gain. (each piece -12.5% heat gain) |
| Thermal Chestplate | armor | rare (10) | 6 armor, 0.5 toughness. Halves heat gain. (each piece -12.5% heat gain) |
| Thermal Leggings | armor | rare (10) | 5 armor, 0.5 toughness. Halves heat gain. (each piece -12.5% heat gain) |
| Thermal Boots | armor | rare (10) | 3 armor, 0.5 toughness. Halves heat gain. (each piece -12.5% heat gain) |
| Ice Bread | food | common (1) | Slows heat for 5 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
## World 3: Endless Dungeon

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Dungeon Key | key | rare (10) | Opens a sealed door once. In code: Use on a Sealed Door: opens it and every sealed door block within 2 blocks. Consumed. |
| Sealed Fragment | resource | rare (10) | Traps and gear. |
| Labyrinth Map | tool | common (1) | Reveals nearby structures. In code: Right-click: names the nearest unvisited structure of the current world, its distance and direction (2 s cooldown). |
| Lockpick Kit | tool | common (1) | Opens an ordinary lock. In code: Use on a Sealed Door: 50% chance to open it. Consumed either way. |
| Portable Trap | consumable | common (1) | Immobilizes a mob. In code: Use on a mob: Slowness XI and Weakness III for 8 s. Consumed. |
| Jailer's Blade | weapon | rare (10) | Sword-type weapon, about 11 attack damage. Gets a random class when crafted. |
| Jailer Helmet | armor | rare (10) | 3 armor, 0.75 toughness |
| Jailer Chestplate | armor | rare (10) | 7 armor, 0.75 toughness, +1 max health |
| Jailer Leggings | armor | rare (10) | 5 armor, 0.75 toughness, +1 max health |
| Jailer Boots | armor | rare (10) | 3 armor, 0.75 toughness |
| Cell Ration | food | common (1) | Long-lasting saturation. Food: 6 hunger, 0.8 saturation, always edible. |
| Sealed Shackle | offering | epic (30) | Held at the arena altar, it wakes the Grand Jailer. |
| Refuge Doll | doll | legendary (100) | A pocket base for your group. Given to every player who fights the Grand Jailer; can be crafted again at the Matrix Workbench. See [Refuge Doll](Refuge-Doll). |
## World 4: Storm Archipelago

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Ray Membrane | resource | common (1) | Glider cloth. |
| Storm Essence | resource | rare (10) | Energy of the Lightning Forge. |
| Celestial Crystal | gem | rare (10) | Gear and the Black Lantern (World 5). |
| Glider | glider | epic (30) | Glide between islands. In code: Hold it while falling: you glide forward at a capped fall speed and take no fall damage. |
| Grappling Hook | hook | rare (10) | Pulls you toward a surface. In code: Right-click a block up to 32 blocks away to be pulled toward it. Resets fall distance. 1 s cooldown. |
| Lightning Lance | weapon | rare (10) | Sword-type weapon, about 13 attack damage. Gets a random class when crafted. |
| Celestial Helmet | armor | rare (10) | 3 armor, 1 toughness, +1 max health |
| Celestial Chestplate | armor | rare (10) | 7 armor, 1 toughness, +2 max health |
| Celestial Leggings | armor | rare (10) | 6 armor, 1 toughness, +1 max health |
| Celestial Boots | armor | rare (10) | 3 armor, 1 toughness, +1 max health |
| Cloud Fruit | food | common (1) | Slow falling for 3 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
| Lacquer Layer | layer | rare (10) | Laid on armor at the Class Table. When the outer layer breaks, the next takes over. See [Nesting systems](Nesting-Systems#layered-armor). |
| Storm Censer | offering | epic (30) | Held at the arena altar, it wakes the Storm King. |
## World 5: Lightless Deep

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Shadow Shard | resource | rare (10) | Base of World 5 gear. |
| Diamond Fragment | gem | epic (30) | 4 fragments make 1 diamond. In code: 4 fragments make 1 Diamond at the Dark Altar. |
| Solar Lantern | lantern | epic (30) | 20 minutes of light. In code: Right-click: 20 minutes of Night Vision, a light (level 14) that moves with you and protection from the World 5 darkness pulses. 60 s cooldown, not consumed. |
| Sonar | sonar | rare (10) | Reveals nearby creatures. In code: Right-click: every creature within 32 blocks glows for 8 s. 10 s cooldown. |
| Silence Balm | consumable | common (1) | Clears your noise. In code: Right-click: noise -100. |
| Shadow Blade | weapon | epic (30) | Sword-type weapon, about 16 attack damage. Gets a random class when crafted. |
| Nocturnal Helmet | armor | epic (30) | 4 armor, 1.5 toughness, +1 max health |
| Nocturnal Chestplate | armor | epic (30) | 8 armor, 1.5 toughness, +2 max health |
| Nocturnal Leggings | armor | epic (30) | 5 armor, 1.5 toughness, +2 max health |
| Nocturnal Boots | armor | epic (30) | 3 armor, 1.5 toughness, +1 max health |
| Mute Mushroom | food | common (1) | Noise reduced for 5 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
## World 6: Upside Realm

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Unstable Alloy | ingot | rare (10) | Base of World 6 gear. |
| Inverted Crystal | gem | epic (30) | Inverter and the Abyssal Pearl (World 7). |
| Gravity Boots | boots | epic (30) | Ignore gravity flips. In code: Feet slot. Your gravity never flips in a flipped column. |
| Stabilizer | consumable | common (1) | Cancels an inversion. In code: Right-click: 30 s of normal gravity, even in a flipped column. |
| Mirror Blade | weapon | epic (30) | Sword-type weapon, about 19 attack damage. Gets a random class when crafted. |
| Mirror Helmet | armor | epic (30) | 4 armor, 2 toughness, +1 max health |
| Mirror Chestplate | armor | epic (30) | 8 armor, 2 toughness, +3 max health |
| Mirror Leggings | armor | epic (30) | 6 armor, 2 toughness, +2 max health |
| Mirror Boots | armor | epic (30) | 4 armor, 2 toughness, +1 max health |
| Flipped Apple | food | common (1) | Stability for 30 seconds. Food: 6 hunger, 0.8 saturation, always edible. |
## World 7: Pressure Ocean

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Abyssal Salt | dust | rare (10) | Salt Snorkel Helmet and the Sapling of the Four Seasons (World 8). |
| Nacre | gem | rare (10) | Nacre Snorkel Helmet. |
| Abyssal Cobalt | ingot | rare (10) | Cobalt Snorkel Helmet and the Diving suit. |
| Pressure Pearl | gem | epic (30) | Pearl Snorkel Helmet and the Sapling of the Four Seasons (World 8). |
| Oxygen Capsule | consumable | common (1) | Right-click: fills half of a worn snorkel helmet's tank, or +60 breath. |
| Thruster | thruster | epic (30) | Right-click underwater: dash in the direction you look. 0.75 s cooldown. |
| Trench Trident | weapon | epic (30) | Sword-type weapon, about 23 attack damage. Gets a random class when crafted. |
| Salt, Nacre, Cobalt and Pearl Snorkel Helmets | snorkel | rare or epic | See [Snorkel helmets](World-7#snorkel-helmets). |
| Diving Chestplate | armor | epic (30) | 9 armor, 2.5 toughness, +5 max health. Each piece lets you dive 22 blocks deeper. |
| Diving Leggings | armor | epic (30) | 7 armor, 2.5 toughness, +4 max health. Each piece lets you dive 22 blocks deeper. |
| Diving Boots | armor | epic (30) | 4 armor, 2.5 toughness, +2 max health. Each piece lets you dive 22 blocks deeper. |
| Apnea Kelp | food | common (1) | Oxygen lasts twice as long for 5 minutes, and +30 breath. |

The Diving suit has no helmet any more: the snorkel helmet takes the head slot.

## World 8: Hastened Seasons

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Temporal Sand | dust | rare (10) | Base of World 8 gear. |
| Season Fragment | gem | epic (30) | The Seismic Stake (World 9). |
| Hourglass | hourglass | epic (30) | Slows the world cycle. In code: Right-click: pauses the World 8 fast clock for 90 s. 5 min cooldown. |
| Season Preserve | consumable | common (1) | Protects from the current season. In code: Right-click: immune to season effects for 2 minutes. |
| Scythe of Seasons | weapon | epic (30) | Sword-type weapon, about 28 attack damage. Gets a random class when crafted. |
| Seasonal Helmet | armor | epic (30) | 5 armor, 3 toughness, +2 max health |
| Seasonal Chestplate | armor | epic (30) | 10 armor, 3 toughness, +6 max health |
| Seasonal Leggings | armor | epic (30) | 7 armor, 3 toughness, +5 max health |
| Seasonal Boots | armor | epic (30) | 4 armor, 3 toughness, +2 max health |
| Season Jam | food | common (1) | Protection from the season for 3 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
| Wreath of Seasons | offering | epic (30) | Held at the arena altar, it wakes the Master of Seasons. |
## World 9: Restless Ground

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Terrain Fragment | resource | rare (10) | Base of World 9 gear. |
| Terrain Heart | resource | legendary (100) | The Traveller's Matryoshka (World 10). |
| Anchor | anchor | rare (10) | Calms the ground (radius 4). In code: Right-click: for 10 minutes the ground zone under you and any zone within 4 blocks of you stay still. Consumed. |
| Grip Boots | boots | epic (30) | No falls from moving ground. In code: Feet slot. The ground zone under you stays still while you wear them. |
| Seismic Mace | weapon | legendary (100) | Sword-type weapon, about 33 attack damage. Gets a random class when crafted. |
| Living Rock Helmet | armor | legendary (100) | 5 armor, 3.5 toughness, +3 max health |
| Living Rock Chestplate | armor | legendary (100) | 11 armor, 3.5 toughness, +8 max health |
| Living Rock Leggings | armor | legendary (100) | 8 armor, 3.5 toughness, +6 max health |
| Living Rock Boots | armor | legendary (100) | 4 armor, 3.5 toughness, +3 max health |
| Key of the Last Doll | key | - | The Traveller's Matryoshka (World 10). In code: Dropped by the Heart of the Terrain. Ingredient of the Traveller's Matryoshka. |
| Anchor Bread | food | common (1) | Steady footing for 5 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
## World 10: The Giant Workshop

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Artisan's Thread | thread | rare (10) | Base of the final gear. |
| Artisan's Shard | gem | legendary (100) | Upgrades the final gear. |
| Artisan's Blade | weapon | legendary (100) | Sword-type weapon, about 40 attack damage. Gets a random class when crafted. |
| Artisan Helmet | armor | legendary (100) | 5 armor, 4 toughness, +4 max health |
| Artisan Chestplate | armor | legendary (100) | 11 armor, 4 toughness, +10 max health |
| Artisan Leggings | armor | legendary (100) | 9 armor, 4 toughness, +7 max health |
| Artisan Boots | armor | legendary (100) | 5 armor, 4 toughness, +4 max health |
| Workshop Feast | food | common (1) | Every dish's effect for 2 minutes. Food: 6 hunger, 0.8 saturation, always edible. |
| Unfinished Effigy | offering | epic (30) | Held at the arena altar, it wakes the Unfinished. |
