# Bosses

Every world ends with a boss, and the Surface has the Block Guardian. All eleven use the same readable attack system: each attack is announced, executed, then leaves an opening. This page describes that system as coded in `MatrioBoss.java`, then every boss.

## Overview

| Boss | Where | Health | Damage | Phase thresholds | Core |
| --- | --- | --- | --- | --- | --- |
| Block Guardian | Surface | 300 | 12 | 50% | Guardian Core |
| Spore Queen | World 1 | 500 | 12 | 66%, 33% | Queen Core |
| Ash Titan | World 2 | 675 | 14.4 | 66%, 33% | Titan Core |
| Grand Jailer | World 3 | 911 | 17.3 | 66%, 33% | Jailer Core |
| Storm King | World 4 | 1230 | 20.7 | 66%, 33% | Storm King Core |
| Light Eater | World 5 | 1661 | 24.9 | 66%, 33% | Light Eater Core |
| Your Double | World 6 | 2242 | 29.9 | 66%, 33% | Double Core |
| Pressure Leviathan | World 7 | 3027 | 35.8 | 66%, 33% | Leviathan Core |
| Master of Seasons | World 8 | 4086 | 43 | 66%, 33% | Seasons Core |
| Heart of the Terrain | World 9 | 5516 | 51.6 | 66%, 33% | Terrain Core |
| The Unfinished | World 10 | 14894 | 61.9 | 90% to 10%, every 10% | Unfinished Core |

Health and damage values already include the world multipliers (see [Difficulty formulas](Difficulty-Formulas)). Every boss also has 8 armor, full knockback resistance, a 48-block follow range, fire immunity and no fall damage.

Every boss is heard before it is seen: while it is near and idle, it has a presence sound of its own, a breath, a growl or a hum in its world's colour (see [Sounds](Sounds)).

## Summoning

The stage closes round the fight: in a lair, a portcullis drops over the chamber's doorway when the boss wakes; in an altar arena, the entrance arch is barred and the rim burns with the world's light. Both open again when the boss falls, or after 20 seconds with nobody inside (to let fallen players back in), and close again behind the first one back.

- Use the altar: the Guardian's Altar on the Surface, or the Arena Altar in the arena 160 blocks south of a world's Threshold. The boss appears 2 blocks above the altar and targets you.
- Only one boss can be awake within 48 blocks of you.
- Bosses can be summoned again after they are beaten. For the Block Guardian the altar prints a reminder but still wakes it.

## Attack structure

Each boss has three attacks, a light one, a medium one and a signature one, and cycles through three states.

1. **Chase.** The boss walks (or flies, or swims) toward its target and picks an attack when one is off cooldown, after at least half a second of chasing.
2. **Telegraph.** It stops, plays its charge or strike animation and a world-specific sound, and the attack name appears above your hotbar (gold for medium, red for the signature). For medium and signature attacks a ring of particles marks the area it aimed at (radius 3, or 5 for the signature, with flames).
3. **Execution.** The attack fires. The aim point is locked when the telegraph starts, so moving away during the telegraph is the main way to dodge.
4. **Opening.** After a medium or signature attack the boss rests. During this window it takes **150%** damage; the rest of the time it takes only **75%**. Light attacks have no opening.

### Choosing an attack

| Attack | Cooldown (ticks) | When it is picked |
| --- | --- | --- |
| Light | 80 - 5 x phase | Target within 5 blocks |
| Medium | 160 - 10 x phase | Preferred when the target is farther than 4 blocks |
| Signature | 400 - 20 x phase | When ready. Before the first phase change it passes a 1 in 3 roll each tick, so it still comes out within moments |

### Timing windows

The telegraph and opening lengths depend on the world tier.

| Worlds | Telegraph (medium) | Telegraph (signature) | Telegraph (light) | Opening after medium | Opening after signature |
| --- | --- | --- | --- | --- | --- |
| Surface, 1 to 3 | 30 ticks (1.5 s) | 60 ticks | 15 ticks | 60 ticks (3 s) | 30 ticks |
| 4 to 6 | 20 ticks (1 s) | 40 ticks | 10 ticks | 50 ticks | 25 ticks |
| 7 to 9 | 15 ticks | 30 ticks | 7 ticks | 40 ticks | 20 ticks |

The Unfinished borrows the attacks of the world its current shell copies but always keeps the shortest tier, World 10 (12-tick telegraph, 30-tick opening), on every shell: the final fight tests everything at the fastest pace. A World Block shaken from outside to help makes a boss stagger and stay open for 3 seconds (see [Effects between the scales](Effects-Between-the-Scales#shaking-the-block-on-purpose)).

## Phases

- Most bosses change phase at **66%** and **33%** of their health. The Block Guardian has one change at **50%**. The Unfinished breaks a shell at every 10%.
- On a phase change the boss roars, becomes **invulnerable for 2 seconds**, gets 10% faster, adds a numeral to its boss bar and shows the name of its final-phase move. Its body cracks: glowing cracks of its world's colour after the first change, many more after the second.
- Cooldowns shrink with each phase (see the table above) and the signature attack is always used when ready after phase 1.
- Special phase effects: the Guardian heals 10% at 50%; the Spore Queen becomes invulnerable behind three Chitin Guard nodes at 33%; the Ash Titan takes 30% more damage from 33%.

## Rewards

When a boss dies, every player within 64 blocks:

- marks the boss as defeated for their group (this unlocks the way into the next world, recipes and gates);
- gets 100 souls and the kill for quests;
- gets one Doll of Life layer back, and one extra maximum layer after the bosses of worlds 1, 5 and 8 (see [Doll of Life and death](Doll-of-Life-and-Death));
- gets 3 Shell Shards, the material of class upgrades;
- reads the boss's revelation line in chat.

Once it has folded into its doll, the boss drops its core, which opens the way into the next world (the World 10 core is a trophy); the bosses of Worlds 1 to 9 drop no World Soil. The Block Guardian also drops a Matrix Workbench and 4 World Soil 0, the soil the World 1 Seed is planted on, and turns every Artisan's Scroll it finds in nearby inventories into the Journal. The World 9 boss also drops the Key of the Last Doll. Each boss gives 200 experience.

## The boss bar

Every boss has a bar of its own, drawn for what it is and the world it rules, in place of vanilla's:

| Boss | Its bar | Its gauge |
| --- | --- | --- |
| Block Guardian | mossy stone, runed pillars with floating cubes | stone blocks filling one by one |
| Spore Queen | ribbed chitin, mushroom clusters, a toxin pod | a bubbling toxic sludge |
| Ash Titan | riveted black iron, furnaces and a smoking stack | molten metal under a bright crust |
| Grand Jailer | dark iron, padlocks, chains, bars across the gauge | blue soul fire |
| Storm King | a copper conduit in storm clouds, lightning rods | a lightning arc |
| Light Eater | smoke and tendrils, a violet eye at each end | a dark that swallows motes of light |
| Your Double | a mirror, mint above and pink below | a mirrored gauge that empties from both ends |
| Pressure Leviathan | a brass diving pipe, a porthole and a pressure dial | deep water |
| Master of Seasons | clockwork brass, a gear and a clock | the four seasons along its quarters |
| Heart of the Terrain | layered rock with red veins, a heart crystal | a heartbeat running along it |
| The Unfinished | a doll painted at one end and sketched at the other | red lacquer over pencil hatching, ten shells |

The damage just taken lingers as a pale trail, each phase is a notch on the gauge, the name flashes when the boss is hit, and the ends of the bar come alive (the clock turns, the heart beats, the furnaces flicker).

## Defeat

A fallen boss folds back into its doll while its death animation plays: two rings of gold, one rising from its feet and one coming down from above its head, close on it. Its name is sealed on a card ("Sealed back in its doll"), and its relics fall from a column of light once the doll has closed, about two seconds after the last blow. A boss removed before that (its chunk unloaded) still leaves its relics where it stood.

## Multiplayer scaling

Health is multiplied by **1 + 0.6 x (players - 1)**, counting the players within 48 blocks of the altar when the boss is summoned.

| Players | Health multiplier | Spore Queen health |
| --- | --- | --- |
| 1 | x1.0 | 500 |
| 2 | x1.6 | 800 |
| 3 | x2.2 | 1100 |
| 4 | x2.8 | 1400 |
| 6 | x4.0 | 2000 |
| 8 | x5.2 | 2600 |

Attack speed is multiplied by **1 + 0.05 x (players - 1)** (x1.05 with 2 players, x1.15 with 4, x1.35 with 8). It is recounted every five seconds from the players within 48 blocks of the boss, so it follows the fight as players arrive or fall.

In a [New Cycle](Endings-and-New-Cycle#new-cycle) bosses also gain +50% health and +25% damage per cycle, and the [variant](World-Variants-and-Mutations) of their world scales their danger too.

## Bosses

### Block Guardian

Surface · 300 health · 12 damage · summoned at the Guardian's Altar in the Guardian's Sanctuary, on the Surface.

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Punch | Frontal strike: 60% damage within 3.2 blocks in front of it. |
| Medium: Shockwave | Ground shockwave, radius 7: 70% damage and a launch, but only to targets standing on the ground. Jump over it. |
| Signature: Torn Block | Throws 3 + phase cobblestone blocks that fall from 10 blocks above you and around you. |
| Final phase: Rebuilds itself from the arena | At 50% health it heals 10% of its maximum health. |
### Spore Queen

World 1 · 500 health · 12 damage · summoned at the Arena Altar of [World 1](World-1).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Root Snare | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Toxic Cloud | Poison cloud (radius 4, Poison II) at the spot it aimed at; +15 toxin to players inside. |
| Signature: Call of Sporelings | Summons 4 + 2 x phase Sporelings. |
| Final phase: Cocoon guarded by nodes | At 33% health it summons 3 Chitin Guards; they and every other creature within 8 blocks become cocoon nodes, and the Queen takes no damage until all of them are dead. |
### Ash Titan

World 2 · 675 health · 14.4 damage · summoned at the Arena Altar of [World 2](World-2).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Hammer Blow | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Ash Spray | Ash burst at the aimed spot: 80% damage within 3.5 blocks. |
| Signature: Rising Lava | Lights a ring of fire of radius 6 + 2 x phase around itself, with a shockwave (50% damage) inside the ring. |
| Final phase: Molten armor, exposed heart | From 33% health it takes 30% more damage (molten armor). |
### Grand Jailer

World 3 · 911 health · 17.3 damage · summoned at the Arena Altar of [World 3](World-3).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Chain Pull | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Floor Cage | Chain pull: drags everything within 18 blocks toward it. |
| Signature: Moving Walls | Cages every player within 16 blocks in iron bars. |
| Final phase: The arena becomes a cell | Phase change only (speed up, faster cooldowns). |
### Storm King

World 4 · 1230 health · 20.7 damage · summoned at the Arena Altar of [World 4](World-4). It flies and hovers 5 blocks above its target.

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Gust | Frontal strike: 60% damage within 3.2 blocks. Flies 5 blocks above its target. |
| Medium: Called Lightning | Gust: throws everything within 14 blocks away from it. |
| Signature: Shattered Islet | Calls 4 + phase lightning bolts around the aimed spot. |
| Final phase: Fight on drifting debris | Phase change only. |
### Light Eater

World 5 · 1661 health · 24.9 damage · summoned at the Arena Altar of [World 5](World-5).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Claw in the Dark | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Lights Out | Lights out: Darkness for 8 seconds within 24 blocks, and breaks torches and lanterns within 10 blocks. |
| Signature: Silent Charge | Silent charge: dashes at you, 90% damage within 2.5 blocks of you. |
| Final phase: Track it by sound only | Phase change only. |
### Your Double

World 6 · 2242 health · 29.9 damage · summoned at the Arena Altar of [World 6](World-6).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Copied Strike | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Copied Weapon | Copies the item in your main hand into its own hand, then hits the area around you (70% damage, radius 3). |
| Signature: Gravity Flip | Gravity flip: Levitation III for 2 seconds to everyone within 16 blocks. |
| Final phase: It adopts your play style | Phase change only. |
### Pressure Leviathan

World 7 · 3027 health · 35.8 damage · sleeps in its lair, the sunken trench temple of [World 7](World-7). It swims, never drowns and does not float up.

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Tail Lash | Frontal strike: 60% damage within 3.2 blocks. Swims freely. |
| Medium: Charge | Charge (90% damage on impact) and -5 oxygen to every player within 20 blocks. |
| Signature: Abyssal Pull | Abyssal pull toward it from 18 blocks and -15 oxygen to every player within 20 blocks. |
| Final phase: Depth and oxygen worsen | Phase change only. |
### Master of Seasons

World 8 · 4086 health · 43 damage · summoned at the Arena Altar of [World 8](World-8).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Seasonal Strike | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Seasonal Ground | Seasonal ground at the aimed spot: 70% damage within 4 blocks. |
| Signature: Season Shift | A season cloud of radius 7 (Poison, Slowness, Weakness or Wither, changing every 10 seconds) plus a ground shockwave of radius 8. |
| Final phase: Overlapping seasons | Phase change only. |
### Heart of the Terrain

World 9 · 5516 health · 51.6 damage · summoned at the Arena Altar of [World 9](World-9).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Ground Wave | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Living Wall | Ground wave: a 13-block line toward you, 60% damage and a launch. |
| Signature: Chasm | Chasm at the aimed spot: 100% damage and Slowness V for 3 seconds within 4 blocks. |
| Final phase: The floor vanishes in sections | Phase change only. |
### The Unfinished

World 10 · 14894 health · 61.9 damage · summoned at the Arena Altar of [World 10](World-10).

| Attack (name shown on screen) | What the code does |
| --- | --- |
| Light: Shell Attack | Frontal strike: 60% damage within 3.2 blocks. |
| Medium: Shell Attack | The medium attack of the world its current shell copies. |
| Signature: Shell Attack | The signature attack of the world its current shell copies. |
| Final phase: A tiny final form | Ten shells: at 90%, 80% ... 10% of its health a shell breaks and it switches to the attacks of the next world, from World 1 up to World 9, always on the shortest timings. |

## Mutations

From World 6 on, the boss of a wild, hallowed or cursed world wakes **mutated**. The mutation adds to its fight without replacing it, and its name follows the boss's in the boss bar.

| Mutation | Comes from | Effect |
| --- | --- | --- |
| Echoing | Wild World 6 and 9 | Every big attack is followed by a second shockwave a moment later |
| Frenzied | Wild World 7 and 10 | Below half health it heals a little, then moves and attacks faster |
| Searing | Wild World 8 | Its attacks set you on fire; a ring of flames follows every big attack |
| Radiant | Hallowed worlds | Every 15 seconds a pulse of light blinds, slows and outlines those around it |
| Hollow | Cursed worlds | Every 20 seconds two creatures of its world come out of its shell |

A mutated boss drops one or two Mutated Scales and two more Shell Shards. See [World variants and mutations](World-Variants-and-Mutations).

## The Artisan's Shadow (World 0)

9000 health, 55 damage. It waits in the Artisan's room in [World 0](World-0), borrows the law of a different prison every fifteen seconds and cannot be finished: brought near death, it stitches itself back together. Its attacks are Unfinished Stroke, Borrowed Law and Ten Prisons at Once. The way to end the encounter is on the World 0 page.

## How to meet each boss

Two ways: altar bosses are summoned at the arena altar with their offering, lair bosses sleep in their own lair and wake when you walk up to the lair heart. Arenas and lairs sit 160 blocks south of each world's Threshold.

### Block Guardian (altar boss, The Guardian's Sanctuary)

1. Follow your Scroll's sketch to the Guardian's Sanctuary on the Surface.
2. Use the sanctuary altar: the Block Guardian rises. No offering needed.
3. Sneak while using the altar to fight it again.

### Spore Queen (lair boss, The Hive)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### Ash Titan (lair boss, The Forge-Hall)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### Grand Jailer (altar boss, The arena altar)

1. Craft a Sealed Shackle at the Jailer's Table.
2. Walk 160 blocks south of the Threshold to the arena.
3. Hold the offering and use the altar on its dais: a three-second ritual summons the boss.
4. Every fight, the first and the next ones, costs one offering.

Offering: **Sealed Shackle**, made at the Jailer's Table from 6 Sealed Fragment, 1 Dungeon Key, 2 Iron Chain.

### Storm King (altar boss, The arena altar)

1. Craft a Storm Censer at the Lightning Forge.
2. Walk 160 blocks south of the Threshold to the arena.
3. Hold the offering and use the altar on its dais: a three-second ritual summons the boss.
4. Every fight, the first and the next ones, costs one offering.

Offering: **Storm Censer**, made at the Lightning Forge from 4 Storm Essence, 2 Celestial Crystal, 2 Ray Membrane.

### Light Eater (lair boss, The Lightless Pit)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### Your Double (lair boss, The Hall of Mirrors)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### Pressure Leviathan (lair boss, The Sunken Trench Temple)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### Master of Seasons (altar boss, The arena altar)

1. Craft a Wreath of Seasons at the Time Workshop.
2. Walk 160 blocks south of the Threshold to the arena.
3. Hold the offering and use the altar on its dais: a three-second ritual summons the boss.
4. Every fight, the first and the next ones, costs one offering.

Offering: **Wreath of Seasons**, made at the Time Workshop from 2 Season Fragment, 6 Temporal Sand, 1 Season Preserve.

### Heart of the Terrain (lair boss, The Living Cavern)

1. Walk 160 blocks south of the Threshold to its lair gate.
2. Come within 10 blocks of the lair heart at the centre of the chamber.
3. It wakes after a three-second tremor. Beat it and the treasure alcove opens: three chests of the world's best loot.
4. The heart wakes again ten minutes later, for a second fight.

### The Unfinished (altar boss, The arena altar)

1. Craft a Unfinished Effigy at the Final Loom.
2. Walk 160 blocks south of the Threshold to the arena.
3. Hold the offering and use the altar on its dais: a three-second ritual summons the boss.
4. Every fight, the first and the next ones, costs one offering.

Offering: **Unfinished Effigy**, made at the Final Loom from 6 Artisan's Thread, 1 Artisan's Shard, 4 Wool Thread.
