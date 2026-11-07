# Compatibility

Matriochka needs only Fabric API and GeckoLib. Every integration below is optional: the mod is compiled against nothing but Mod Menu's API (and JEI's), and loads the same without any of them.

Checked on Modrinth for Minecraft 26.3 on Fabric (November 2026):

| Mod | Available for 26.3 Fabric | Status with Matriochka |
| --- | --- | --- |
| Sodium | yes (0.9.3 beta) | No conflict expected, see below |
| Iris | yes (1.11.7) | No conflict expected, see below |
| Xaero's Minimap / World Map | yes (26.6.2 / 1.47.2) | Adapted: no cave view or radar in World 5 |
| JourneyMap | yes (6.0.10) | Works as a plain map; no integration |
| VoxelMap Updated | yes (1.16.13) | Works as a plain map; no integration |
| Traveler's Backpack | yes (11.4.3) | No way around the progression found, see below |
| Sophisticated Backpacks | no (NeoForge only) | — |
| Mod Menu | yes (21.0.0) | Integrated: info screen, comfort options and links |
| Just Enough Items | yes | Integrated since 0.3.0: station recipe pages |

## Sodium and Iris

Matriochka does not touch chunk rendering, so Sodium's renderer has nothing to conflict with: its blocks are plain block models (no custom render types, no block-model mixins). What it draws itself goes through vanilla's render types:

- **Creatures and bosses** are GeckoLib entity renderers; the bosses' and creatures' glowing parts use GeckoLib's own glow layer. GeckoLib supports Sodium and Iris.
- **The World Block's miniature world** (a block entity renderer) submits small cubes through vanilla's `entitySolid`, `entityTranslucent` and `entityTranslucentEmissive` render types, which Iris maps to its entity programs. The little sun is drawn full-bright, so it still glows under shaders.
- **The HUD, the Journal and the station screens** are drawn through the GUI only.
- The client mixins stay out of world rendering: one draws the Matriochka bosses' own bars in place of vanilla's (other mods' and vanilla's bars keep their look), the others set the music, the camera's field of view and shake, the trader screen and the particle budget.

To try them in a dev client: `./gradlew runClient -Pcompat` adds Sodium, Iris and Mod Menu (versions in `gradle.properties`). Worth a look under a shader pack: the World Block's island and sun, the boss glow layers, and World 5 (darkness) and World 7 (underwater fog).

## Map mods

- **Names:** every world has a translated dimension name (`dimension.matriochka.world_1` = "World 1 — Toxic Jungle", and so on, in all five languages), which map mods that show translated dimension names use. Mod worlds are separate dimensions, so maps and waypoints of each world stay apart. Groups get parcels 13,000 blocks apart, so no group's map shows another's.
- **World 5, the Lightless Deep:** the whole world is about darkness, and a minimap's cave view and entity radar would show what the dark hides. When a client runs Xaero's Minimap or World Map, it tells the server on join; entering World 5 then sends Xaero's documented fair-play code in a short chat line ("In the Lightless Deep, your map sees no further than you do."), which turns off cave mode and the radar, and leaving World 5 sends its reset code ("Your map can see in the dark again."). Players without Xaero never get these lines.
  - The reset code clears every Xaero flag set by chat codes, so a server that sends its own fair-play code on login loses it after a trip to World 5. Servers that rely on that should use Xaero's server-side settings instead (they are not affected).
- Waypoints are left alone everywhere: worlds 3, 6 and 9 move under your feet but a waypoint is only a hint, and World 3's halls move anyway.
- JourneyMap and VoxelMap have no server-side switch that works without them on the server; they are left as plain maps.

## Backpacks

Traveler's Backpack was checked against every progression gate. None of them looks at what you carry, so a backpack cannot get around them:

- **Seeds and rite objects:** planting a Seed or setting down a rite object checks on the server that your group beat the previous boss, so one (or a core) brought in a backpack, or given by a friend, does not open a world early.
- **Bosses and altars:** altars only work in their own world, and an offering in a backpack still has to be held.
- **Enchanting, the Nether and the End** are gated by your group's progression, not by items.
- **Diamonds** do not exist before World 5: they are removed from the Surface's ores and from vanilla chests, wherever they would be stored.
- **The Refuge Doll** stays shut near an awake boss whatever you carry; a backpack is only storage, it does not teleport.
- **The New Cycle** takes back the old cycle's cores, Seeds and rite objects, World Soils, offerings and keys from your inventory only; one kept in a backpack (or a shulker box) cannot be used anyway, because the new cycle's worlds check the new cycle's progress.
- **Death in a world** puts your inventory, backpack items included, in the death chest. A backpack worn on the back follows Traveler's Backpack's own death rules.

## Mod Menu

Matriochka's entry shows its translated summary and description, links to the wiki, the Discord and the issue tracker, and its configure button opens a small info screen (version, what the mod is, where the server rules live, links to the wiki and the website) with a **Comfort** button that opens the comfort options, the same screen as the Journal's (see [Accessibility](Accessibility)).
