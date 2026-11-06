# World 7: Pressure Ocean

Pressure Ocean is world 7 of 10, in the expertise tier. Its rule is **Oxygen**. You open it with the World 7 Seed, made from the core of the World 6 boss (Your Double).

The whole world is sea. There is no dry land: you live, fight and mine under water, and the only way to breathe for long is a **snorkel helmet**.

## At a glance

| | |
| --- | --- |
| Tier | Expertise |
| Rule | Oxygen |
| Station | Abyssal Press |
| Boss | Pressure Leviathan (3027 health, 35.8 damage) |
| Core | Leviathan Core |
| People | Diver |
| Seed | 1 Double Core, 8 Unstable Alloy, 4 Inverted Crystal |

## Opening the world

- **Seed recipe** (Matrix Workbench, after the World 6 boss (Your Double) is defeated): 1 Double Core, 8 Unstable Alloy, 4 Inverted Crystal.
- **Soil:** tilled World Soil 6.
- **Hatching condition:** Water within 4 blocks horizontally and 1 block vertically, as for World 1.
- **Arrival:** a **diving chamber** on the sea floor at the centre of your group's parcel: a glass dome full of air around the Threshold, with lanterns, a chest of supplies (4 Oxygen Capsules, 3 Apnea Kelp, an iron pickaxe) and a door facing south. Doors hold water back, so the chamber stays dry when you open it. An Air Vent bubbles on the floor a few strides outside. The boss lair is 160 blocks south (positive Z); glowing coral posts on the sea floor lead the way.

## Terrain

The sea fills the world from its floor up to **y 240**; above that there are only 16 blocks of air under the sky. The sea floor rolls around y 140, with hills, reef crowns rising toward y 200 and rare **trenches** that drop below y 20. Caves run under the floor; some of them hold dry **air pockets**. Kelp forests, seagrass, coral reefs, sea pickles and spires of glowing Pressure Coral light the deep.

| Block | Type | Drops |
| --- | --- | --- |
| Abyssal Sand | Soft (shovel) | itself |
| Trench Rock | Stone (pickaxe) | itself |
| Pressure Coral | Light level 13 | itself |
| Abyssal Salt Ore | Ore, everywhere from y -50 to y 200 | Abyssal Salt |
| Nacre Vein | Ore, in the reefs and the upper floor (y 110 to 220) | Nacre |
| Abyssal Cobalt Ore | Ore, deeper down (y -20 to 110) | Abyssal Cobalt |
| Pearl Bed | Ore, in the deep rock and sand (y -50 to 60), rare | Pressure Pearl |
| Air Vent | On the sea floor, light level 6 | itself |

## The rule: Oxygen

The mod keeps the vanilla air bar full and uses its own gauge instead: your **breath**, 0 to 100.

- **Under water without air:** -3 breath per second (about 33 seconds). At 0 you take 2 drowning damage per second.
- **With a snorkel helmet:** you breathe from its **tank**. It costs 1 second of tank per second, and it tops your breath back up (+6 per second, at 0.25 second of tank per point). Apnea Kelp halves the cost for 5 minutes, and the Survivor class reduces it.
- **In air** (an air pocket, a grotto, a habitat, the diving chamber, the surface): +10 breath per second, and the helmet's tank refills by 20 seconds per second.
- **In a bubble column or over an Air Vent** (up to 6 blocks above it): +5 breath per second and +12 seconds of tank per second, even under water.
- **Oxygen Capsule:** fills half of a worn helmet's tank, or gives +60 breath without a helmet.
- **Abyssal Press:** its **Refill** button fills a helmet to the brim (the one on your head, otherwise the emptiest one you carry), as long as the press stands deep under water.
- Blade Schools (-3 per second), Pressure Jellies (-2 per second) and the Leviathan's attacks (-5 or -15) take breath; the helmet pays them back from its tank.
- **Pressure:** under water below y 110 you take 1.5 damage per second. Each Diving piece lowers that limit by 22 blocks and the helmet's tier by 0 to 18 more: with the three Diving pieces and a Pearl Snorkel Helmet the limit is y 26.

Your breath is the row of brass portholes above the hunger bar (above the vanilla air bubbles when your head is under water, which the mod keeps full). With a snorkel helmet on, the row shows the helmet's tank instead, as small air tanks, and your own breath comes back above it as soon as it drops.

## Snorkel helmets

One helmet for each ore of the world, all crafted at the Abyssal Press from 5 of their ore, 2 Glass Panes and 2 Kelp. They come out with a full tank. They are **fragile**: on top of the usual armor wear, every hit takes extra durability (half a point per point of damage for the Salt helmet), a hard hit spills some air, and every 30 seconds of use under water costs one more point. Mend them at the anvil with their own ore.

| Helmet | Ore | Tank | Durability | Armor | Toughness | Extra wear per damage | Deeper |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Salt Snorkel Helmet | Abyssal Salt | 3 min | 44 | 2 | 0 | 0.5 | 0 |
| Nacre Snorkel Helmet | Nacre | 5 min | 66 | 3 | 1 | 0.35 | 6 |
| Cobalt Snorkel Helmet | Abyssal Cobalt | 8 min | 110 | 3 | 2 | 0.25 | 12 |
| Pearl Snorkel Helmet | Pressure Pearl | 12 min | 154 | 4 | 3 | 0.15 | 18 |

The tooltip shows the air left in the tank and the helmet's tier. The first common chests of the world sometimes hold a worn, half-full Salt Snorkel Helmet, and the Divers sell one for 8 Abyssal Salt.

## Creatures

Every creature of the world lives under water: they swim in three dimensions, never drown and spawn in open, dark water (regular ones in groups of 1 to 3, swarms in groups of 2 to 4, elites alone and rarer), and from spawners in combat structures. See the [Bestiary](Bestiary).

| Creature | Health | Damage | Traits | Behavior (as coded) | Drops |
| --- | --- | --- | --- | --- | --- |
| Abyssal Hunter | 157 | 20.9 | aquatic | Swims straight at you. | Abyssal Salt (60%) |
| Blade School | 73 | 11.9 | aquatic | Fast swimmer. Drains 3 breath per second when within 3 blocks. | Abyssal Salt (60%) |
| Pressure Jelly | 121 | 14.9 | aquatic | Within 7 blocks: Slowness II, Mining Fatigue II and -2 breath per second. | Pressure Pearl (60%) |
| Bell Crab | 242 | 17.9 | aquatic, nesting | Plain melee attacker. Nesting: on death splits into 2 smaller copies (60% size, 40% health, 30% faster) that drop nothing. | Pressure Pearl (60%) |
| Trench Eel | 182 | 23.9 | elite, aquatic | Every 3.5 s at close range: Slowness VII (2.5 s) and Wither I (2 s). | Pressure Pearl (100%, 1-2) |

### Wildlife

Harmless creatures fill the sea. They never attack.

| Creature | Health | Behavior | Drops |
| --- | --- | --- | --- |
| Lantern Shoal | 6 | A school of tiny glowing fish that darts away from swimmers. | Raw Cod |
| Glow Jelly | 8 | A small jellyfish that drifts slowly and lights the deep. | Glow Ink Sac |

## Items

| Item | Kind | Rarity (souls) | Effect |
| --- | --- | --- | --- |
| Abyssal Salt | dust | rare (10) | Salt Snorkel Helmet and World 8 Seed. |
| Nacre | gem | rare (10) | Nacre Snorkel Helmet. |
| Abyssal Cobalt | ingot | rare (10) | Cobalt Snorkel Helmet and the Diving suit. |
| Pressure Pearl | gem | epic (30) | Pearl Snorkel Helmet and World 8 Seed. |
| Oxygen Capsule | consumable | common (1) | Right-click: fills half of a worn snorkel helmet's tank, or +60 breath. |
| Thruster | thruster | epic (30) | Right-click underwater: dash in the direction you look. 0.75 s cooldown. |
| Trench Trident | weapon | epic (30) | Sword-type weapon, about 23 attack damage. Gets a random class when crafted. |
| Salt, Nacre, Cobalt and Pearl Snorkel Helmets | snorkel | rare or epic | See [Snorkel helmets](#snorkel-helmets). |
| Diving Chestplate | armor | epic (30) | 9 armor, 2.5 toughness, +5 max health. Each piece lets you dive 22 blocks deeper. |
| Diving Leggings | armor | epic (30) | 7 armor, 2.5 toughness, +4 max health. Each piece lets you dive 22 blocks deeper. |
| Diving Boots | armor | epic (30) | 4 armor, 2.5 toughness, +2 max health. Each piece lets you dive 22 blocks deeper. |
| Apnea Kelp | food | common (1) | Oxygen lasts twice as long for 5 minutes, and +30 breath. |

The Diving suit has no helmet any more: the snorkel helmet takes the head slot.

## Station: Abyssal Press

Must be deep underwater: water directly above the press and 8 blocks above it. Crafted at the Matrix Workbench from 2 Piston (vanilla), 6 Unstable Alloy, 1 Inverted Crystal (World 6 boss defeated). Its **Refill** button fills a snorkel helmet's tank.

| Output | Ingredients | Unlocked |
| --- | --- | --- |
| Oxygen Capsule x3 | 4 Kelp (vanilla), 1 Abyssal Salt | Always |
| Thruster | 2 Pressure Pearl, 4 Unstable Alloy | Always |
| Pressure Pearl | 6 Abyssal Salt, 2 Prismarine Crystals (vanilla) | Always |
| Apnea Kelp x3 | 3 Dried Kelp (vanilla), 1 Abyssal Salt | Always |
| Salt Snorkel Helmet | 5 Abyssal Salt, 2 Glass Pane, 2 Kelp (vanilla) | Always |
| Nacre Snorkel Helmet | 5 Nacre, 2 Glass Pane, 2 Kelp (vanilla) | Always |
| Cobalt Snorkel Helmet | 5 Abyssal Cobalt, 2 Glass Pane, 2 Kelp (vanilla) | Always |
| Pearl Snorkel Helmet | 5 Pressure Pearl, 2 Glass Pane, 2 Kelp (vanilla) | Always |
| Trench Trident | 8 Abyssal Salt, 1 Stick (vanilla) | Always |
| Diving Chestplate | 8 Abyssal Cobalt | Always |
| Diving Leggings | 7 Abyssal Cobalt | Always |
| Diving Boots | 4 Abyssal Cobalt | Always |

Every weapon, tool and armor piece crafted here gets a random class (see [Equipment classes](Equipment-Classes)).

## Boss: Pressure Leviathan

3027 health, 35.8 damage, phases at 66% and 33% of its health. It sleeps in a **sunken trench temple**: the temple is cut 10 blocks below the level of the diving chamber, at the bottom of a trench open to the sea, and two beacon pillars rise from its forecourt to the surface. Its heart wakes it when you swim within 10 blocks. It swims freely, never drowns and does not float up. When it falls the alcove behind the seal opens on three chests (the world's rarest materials, a piece of its gear or a snorkel helmet, and riches).

| Attack | What the code does |
| --- | --- |
| Light: Tail Lash | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Charge | Charge (90% damage on impact) and -5 breath to every player within 20 blocks. |
| Signature: Abyssal Pull | Abyssal pull toward it from 18 blocks and -15 breath to every player within 20 blocks. |
| Final phase: Depth and oxygen worsen | Phase change only. |

Its hits are hard on a snorkel helmet: a Salt helmet does not survive two of them. Bring a better tier, a spare, or capsules.

## Structures

Ten structure types generate in this world, all on the sea floor. Several of them hold dry refuges where your breath and your helmet refill: the Air Grotto (a glass dome with beds, entered through a flooded tunnel), the Diving Bell and the habitats of the Pressure Station.

| Structure | Role | Size | Rarity | Layout | Contents |
| --- | --- | --- | --- | --- | --- |
| Hunters' Trench | combat | large | common | chasm | a mob spawner and a loot chest |
| Dead Reef | combat | medium | common | ruin | a mob spawner and a loot chest |
| Sunken City | combat | large | rare | city | a mob spawner and a loot chest |
| Wreck | exploration | medium | common | wreck | two loot chests |
| Diving Bell | exploration | small | common | bell | an air pocket and two loot chests |
| Air Grotto | exploration | medium | common | cocoon | a dry refuge and two loot chests |
| Abyssal Temple | story | large | unique | temple | a chest with a Journal Page, and a painted frieze |
| Sunken Lighthouse | story | medium | unique | lighthouse | a chest with a Journal Page, and a painted frieze |
| Pressure Station | utility | large | rare | lab | dry habitats, an Abyssal Press and a Diver |
| Vault of the Deep | secret | small | unique | vault | a chest with a Journal Page and the world's Hidden Doll |

## People: Diver

Station chiefs and mechanics who keep the pressure station running. They live under water and walk the sea floor. Prices drop by 10% at karma +25 and rise by 10% at karma -25; at karma -50 or lower they refuse to trade one time in three (see [Souls and karma](Souls-and-Karma)).

| They want | They give |
| --- | --- |
| Abyssal Salt x3 | Oxygen Capsule x3 |
| Pressure Pearl x1 | Apnea Kelp x4 |
| Abyssal Salt x8 | Salt Snorkel Helmet x1 |

## Quests

| Quest | Type | Description | Objective as coded | Reward |
| --- | --- | --- | --- | --- |
| Under Pressure | Guide | Craft a Salt Snorkel Helmet at the Abyssal Press. | Craft Salt Snorkel Helmet | 8 Oxygen Capsule |
| Compress | Guide | Press something at the Abyssal Press. | Craft Pressure Pearl | 40 souls |
| The Silent Station | People | Repair 3 station cables. | Carry 6 Abyssal Salt | 1 Thruster |
| The Wreck's Crew | People | Recover 3 crew plates. | Kill 10 Blade School | 40 souls |
| The Signal | Karma | Rescue the castaways (+10) or divert their oxygen (-10). | Choose Help or Betray in the Journal | 60 souls |
| One Breath | Challenge | Defeat a Trench Eel. | Kill 1 Trench Eel | Title: Cold Blood |

## Achievements

| Achievement | Type | Description | How it unlocks in the code | Reward |
| --- | --- | --- | --- | --- |
| Great Depth | progress | Open World 7. | Enter World 7. | 5 souls |
| Pressurized | progress | Breathe through a snorkel helmet. | Breathe from a helmet's tank under water. | 5 souls |
| Silence of the Trenches | progress | Defeat the Leviathan. | Land the killing blow on Pressure Leviathan. | 5 souls |
| Extreme Dive | explore | Reach the deepest trench. | Swim below y 30 in World 7. | 10 souls |
| Open Sea | explore | Visit the 10 structure types. | Step inside all 10 structure types of this world. | 10 souls |
| Wet Paper | explore | Find the 5 Journal pages. | Collect the 5 Journal Pages of this world. | 10 souls |
| School Scattered | combat | Kill 5 Blade Schools. | Land the killing blow on Blade School. | - |
| Last Breath | combat | Beat the Leviathan with under 5% oxygen left in your helmet or your lungs. | When the Leviathan dies: the helmet's tank (or your breath without air in a helmet) is under 5%. | - |
| Forgotten Plate | hidden | Search a sunken wreck. | Step inside a Wreck. | - |
| Drowned Doll | hidden | Find the hidden doll of the world. | Have Hidden Doll 7 in your inventory. | - |

Previous: [World 6](World-6) · Next: [World 8](World-8)
