# World 3: Endless Dungeon

No surface and no sky, only dungeon. Sealed doors give way to Dungeon Keys, made at the Jailer's Table once you have reproduced the lock pattern. And the halls move.

## Rule: the moving halls

Every **5 minutes** the dungeon rearranges itself around every player.

- **10 seconds before**, the message *"The halls are about to move..."* appears, the walls grind, and dust falls from the parts of the dungeon that are about to move. Watch the dust: it shows you exactly which halls will change.
- The dungeon is cut into **hall sections** of 8 x 8 blocks, 16 blocks tall (from 5 blocks under your feet to 10 above your head).
- When the shift comes, up to **four pairs** of sections swap places, each pair turned a quarter, a half or three quarters on the way, and up to **two more** sections turn on themselves. They are picked **16 to 40 blocks** from you.
- Passages that led somewhere now end in a wall; walls that blocked you now open on a new hall. Creatures standing in a moving section travel with it.
- The message *"The halls have moved around you."* confirms the shift.

## What never moves

The halls move, the rooms do not. A section stays where it is when it holds, or sits next to:

- **a player** (no section within 6 blocks of anyone moves, and the ring around you starts two sections away, so the ground under your feet and the hall you stand in are never touched);
- **a block entity**: chests, barrels, stations, the **Jailer's Table**, Soul Cradles, death chests;
- **an unbreakable block**: Sealed Bricks, **Sealed Doors**, altars, the Threshold;
- **a fluid**;
- **a block you placed**: your torches, walls, bridges and builds keep the halls around them still;
- **any part of a structure**: arenas, courts, cells, vaults, mazes and their locks stay whole, so a key always finds its door;
- **a boss**, the boss stage and the area around the Threshold.

If anything ever ends up overlapping you after a shift, you are moved to the nearest free spot.

## Tips

- Build to keep a route: a single block you placed in a hall pins that hall in place.
- Light your way with your own torches: they also mark the halls as yours.
- A Labyrinth Map still finds the structures: they never move.

## Numbers

| | |
| --- | --- |
| 5 min | between two rearrangements |
| 10 s | of warning, with falling dust on the moving halls |
| 8 x 8 x 16 | blocks per hall section |
| 16 to 40 | blocks from you: where the halls move |
| 4 + 2 | swaps and turns per player per shift |

## Site copy (for `tools/site.py`, RULE_LONG and RULE_NUMS)

EN: There is no surface and no sky, only dungeon. Sealed doors give way to Dungeon Keys, made at the Jailer's Table once you have reproduced the lock pattern. Every five minutes the halls rearrange themselves: 8 x 8 sections 16 to 40 blocks from you swap places or turn, and dust falls on them ten seconds before. Rooms, locks, chests and anything you built never move. Light is scarce, so bring your own.

FR : Ici, ni surface ni ciel : rien que le donjon. Les portes scellées cèdent aux Clés de donjon, fabriquées à la Table du Geôlier une fois le motif de la serrure reproduit. Toutes les cinq minutes, les salles se réorganisent : des sections de 8 x 8 situées entre 16 et 40 blocs de toi échangent leur place ou pivotent, et de la poussière tombe sur elles dix secondes avant. Les salles fermées, les serrures, les coffres et tout ce que tu as construit ne bougent jamais. La lumière est rare : apporte la tienne.

Numbers: `5 min` between two rearrangements of the halls / entre deux réorganisations des salles; `10 s` of warning, dust on the moving halls / de préavis, la poussière sur les salles qui bougent; `16-40` blocks from you: where the halls move / blocs de toi : là où les salles bougent.
