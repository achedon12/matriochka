# Trials

Once you have seen an ending (Sealed, Absorbed or Set Down the Tools), the **Trials** open: boss rushes fought on a lacquered stage inside the Refuge doll, against the clock. They are for replaying the bosses at their hardest and racing other groups; they give nothing of the story (no core, no progression, no Doll of Life layer).

## Opening the Trials

- **From the Journal**: a **Trials** button appears at the foot of the Objective page, next to **Comfort**, once you have seen an ending.
- **From a Trial Altar**: a block carved at the Matrix Workbench once your group has beaten the Unfinished (4 Lacquer Blocks, 1 Gold Block, 2 Shell Shards). Use it to open the Trials book.
- **By command**: `/matriochka trials start <trial>`.

The Trials book lists the eleven trials on its left page, each with a pip (gilded once you have won it) and your best time. The right page tells the chosen trial, its par time, your best, your group's best and the server's board, with the **Begin** button. Its **Titles** leaf lists the titles you own and lets you wear one.

## The trials

| Trial | What you fight | Par |
| --- | --- | --- |
| Trial: Spore Queen ... Trial: The Unfinished (one per world) | two waves of the world's creatures (4 + one per player), the second led by its elites, then the world's boss | 2:45 for World 1, 15 s more per world, 8:00 for World 10 |
| The Gauntlet | the eleven bosses in a row, from the Block Guardian to the Unfinished, each on a stage painted in its world's materials | 30:00 |

- Trial bosses have **60% more health and 35% more damage** (the Gauntlet's 20% and 15%), on top of the difficulty and the New Cycle, and always wake with a mutation: Radiant for the Guardian and the Storm King, Hollow for the Spore Queen and the Light Eater, Searing for the Ash Titan and the Master of Seasons, Echoing for the Grand Jailer, Your Double and the Heart of the Terrain, Frenzied for the Leviathan and the Unfinished.
- Trial bosses wake without their introduction (bars, title card, the camera turning to them): the clock is already running. Their attack subtitles and phase freeze-frames still follow your comfort options.
- The Leviathan's stage is flooded; the trial lends you Water Breathing while you fight there.
- The trial is fought by you and the members of your group standing within 24 blocks of you when it begins. No trial starts in peaceful difficulty, or near an awake boss.

## The clock

A five-second countdown, then the clock runs on game ticks from the first wave to the last blow, pauses included. The HUD shows a lacquered plaque at the top of the screen (beside or under the HUD plaque when the comfort options put that one in a top corner) with the trial's name, the time (green under par, orange past it), the stage and your best time.

Falling in a trial does not kill you: the doll carries you out, at full health, back where you stood (your Doll of Life is not spent). Leaving the stage, logging out or the **Leave** button also takes you out. When no one is left, the trial ends.

## Records and rewards

- **Your best time** per trial, **your group's best time** per trial, and a **server-wide board** of the ten best groups per trial (one line per group, with the names of who fought). The board is in the Trials book and in chat with `/matriochka trials top <trial>`.
- Every win pays souls: 25 per world number (the Gauntlet, 300).
- **The first win** of a trial gives its **Trophy Doll** (use it to set it on your shoulder, as a parrot would; use it again to take it down) (a painted doll of the boss on a gilded plinth; the Gauntlet's has eleven in one) and its title:

| Trial | Title |
| --- | --- |
| World 1 | Hive Breaker |
| World 2 | Ember Walker |
| World 3 | Gaol Breaker |
| World 4 | Storm Rider |
| World 5 | Lightbringer |
| World 6 | Mirror Breaker |
| World 7 | Abyss Diver |
| World 8 | Timekeeper |
| World 9 | Groundshaker |
| World 10 | Unmaker |
| The Gauntlet | Gauntlet Champion |
| Any trial under its par | Swift Hand |

Titles are cosmetic: the one you wear is shown in the Journal. Quest titles can be worn from the same list.

## Commands

- `/matriochka trials start <trial>`: `w1` to `w10` or `gauntlet`.
- `/matriochka trials leave`
- `/matriochka trials top <trial>`

## Stored data

The stages stand at z 40,000 in the `matriochka:refuge` dimension, one every 256 blocks along x (64 at once). Records: `trial_best_<trial>` (ticks) and the `trial_done_<trial>` and `title_<id>` flags in the player state; `trial_best` in the group's data; `trials` in the server data (`matriochka:state`).
