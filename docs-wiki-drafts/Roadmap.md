# Roadmap and known limitations

Matriochka is an alpha. The whole story can be played from the Surface to the third ending: the ten worlds with their moving rules, World 0, the three endings and the New Cycle. This page lists what is in the game now, and honestly what is still missing or simpler than the design.

## In the game now

**Story and endgame**

- [World 0](World-0), opened by the ten [hidden dolls](Hidden-Dolls) nested in order, with its Obsession rule and the Artisan's Shadow.
- The three [endings](Endings-and-New-Cycle) (Sealed, Absorbed, Set Down the Tools), each with a crawl on the Scroll, the credits and an advancement, and the New Cycle with stronger worlds.
- The fifty Journal pages, in English and French, with the coded pages in the Artisan's cipher (see [The Artisan's Journal](Artisans-Journal)).
- [World variants](World-Variants-and-Mutations) chosen while a Seed or rite site hatches, the karma variants at +100 and -100, and boss mutations from World 6.

**Worlds**

- World 3 halls really move, World 5 lights burn out, World 6 gravity changes by zone, World 9 ground zones rise, sink, slide and close.
- World 7 is entirely under water, with snorkel helmets, a diving chamber and sea wildlife.
- World 10 at doll scale, with the giant props and the Maquette of your base on the Titanic Workbench.
- The miniature of its world over every World Block, and the [effects between the scales](Effects-Between-the-Scales) in both directions.

**Systems**

- The [Refuge Doll](Refuge-Doll), [nesting chests and layered armor](Nesting-Systems).
- [Station automation](Blocks-and-Stations#automation): hoppers feed a kept recipe, the result comes out below, comparators read the station, and every station keeps its condition.
- [Shaking the World Block on purpose](Effects-Between-the-Scales#shaking-the-block-on-purpose) from outside, to help (stun the creatures, open the boss) or hinder (quake, falling blocks) the group inside.
- The Doll of Life layer at the Soul Altar costs 50 souls and 4 rare resources of the current world; structure chests keep Soul Shards and Soul Vessels, about 100 souls per world (see [Souls and karma](Souls-and-Karma#souls-in-structure-chests)).
- Every [quest](Quests) checks what its description says: deliveries to the peoples, places reached, stations used, kills under a condition.
- The Unfinished fights on the shortest timing tier, on every shell.
- The Drill's 3 x 3 mining and fuel, Storm Essence for the Lightning Forge, the Spore Vat's fermentation yields, the Inverter's property swap.
- Karma on the Surface, black markets and the Karma Paths quests (see [Souls and karma](Souls-and-Karma)).
- Reaper soul gain, Prowler dodge, Shell Shards for class upgrades (see [Equipment classes](Equipment-Classes)).
- Boss attack speed that grows with the players, the "take part in the last boss" rule, group leader commands (see [Multiplayer and groups](Multiplayer-and-Groups)).
- Administrator commands to list, repair, move and reset worlds and to reset bosses (see [Commands](Commands)).
- The story and hardcore difficulty modes (see [Configuration](Configuration)).
- Villager diamond trades held back until World 5.
- The mod's own [sounds and music](Sounds), synthesized from seeded recipes.
- Recipe pages in Just Enough Items (optional). EMI has no build for Minecraft 26.3, so there is no EMI support.

## Art

- Every creature and boss has its own model, built part by part in `tools/mobs_hd` and `tools/bosses_hd.py`, with its own animations and one animation per attack. The GeckoLib files in `src/main/resources/assets/matriochka/geckolib` open directly in Blockbench.
- Block and item textures and the interface sprites are painted by code (`tools/paint.py`, `tools/gui.py`). None of it is hand-drawn yet.

## Still missing

- **Accessibility and comfort options.** The config has no switch for screen effects (shakes, nausea, Darkness pulses), no karma or soul options and no limit on active groups or parcels, all of which the design lists.
- **Cinematics and screen effects.** Beyond the endings' crawl and credits there are no cutscenes, camera shakes or slow motion.
- **Adaptive music.** Each world has its theme and bosses have a fight theme that turns fiercer below a third of their health, but the music does not otherwise follow what happens.
- **A modpack version**, which the design plans for after the standalone mod.

## Known issues

No known bug is open. Report anything odd on the [issue tracker](https://github.com/achedon12/matriochka/issues).

## Release plan (from the design)

1. Private alpha on worlds 1 to 3.
2. Closed beta up to World 10.
3. Public 1.0 with the ten worlds, published on Modrinth and CurseForge for Fabric, tested on Lunar Client, with a trailer, this wiki and a Discord.

The design's priorities: P0 proves the concept on World 1, P1 builds the reusable systems (attack system, stations, gates, classes, karma), P2 finishes the game (World 0, endings, variants, mutations, layered armor, nesting chests, miniature preview, New Cycle, difficulty modes, accessibility, music). P0 and P1 are done; of P2, accessibility and cinematics remain. Modrinth and CurseForge listings are still in review.
