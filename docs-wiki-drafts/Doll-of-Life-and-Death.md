# Doll of Life and death

Dying in Matriochka is meant to teach, not to wipe hours of progress. Three systems soften it: the Doll of Life, the death chest and the Soul Cradle.

## Order of resolution

When you take a fatal hit:

1. If your Doll of Life has a layer and your last revival was at least 60 seconds ago, a layer breaks and you stay alive (never in the hardcore mode).
2. Otherwise you die. Inside a Matriochka world (and unless `keepInventory` is on), your inventory goes into a death chest. In the story mode nothing drops: your inventory and experience come back when you respawn. In the hardcore mode the death is final and you come back as a spectator (see [Configuration](Configuration#difficulty-modes)).
3. You respawn at your normal spawn point. If you died inside a world where you placed a Soul Cradle with charges left, you are moved to the cradle.

## Doll of Life

| Event | Effect |
| --- | --- |
| World 1 boss defeated | maximum layers 1 |
| World 5 boss defeated | maximum layers 2 |
| World 8 boss defeated | maximum layers 3 |
| Any boss defeated | +1 layer, up to your maximum |
| Soul Altar | +1 layer for 50 souls and 4 rare resources of the current world |

- Layers belong to each player, not to the group. You must be within 64 blocks of the boss when it dies to gain the maximum layer.
- A revival restores 50% of your health and gives Resistance V and Regeneration II for 5 seconds.
- Only one revival per 60 seconds, so two fatal hits in a row still kill you.
- The HUD shows your layers as small dolls next to your souls. The Journal shows "Doll of Life: x / y layers".
- The Life Doll item in the creative tab has no use; the doll is a player state.
- A [New Cycle](Endings-and-New-Cycle#new-cycle) takes the layers of the doll away: they grow back with the bosses of the new cycle.
- When the doll breaks you hear it: the shell cracks and a bell and a music box arpeggio bloom.

## Rebuilding a layer at the Soul Altar

The altar's **Rebuild a layer** button costs 50 souls and 4 rare resources of the current world, in any mix. The current world is the one you stand in; on the Surface it is the newest world your group has opened (the one after its highest boss beaten). The rare resources of a world are its rare resources, gems, ingots, dusts and threads:

| World | Rare resources |
| --- | --- |
| 1 | Sporite, Chitin |
| 2 | Giant Ore, Ash Ingot |
| 3 | Sealed Fragment |
| 4 | Storm Essence, Celestial Crystal |
| 5 | Shadow Shard |
| 6 | Unstable Alloy |
| 7 | Abyssal Salt, Nacre, Abyssal Cobalt |
| 8 | Temporal Sand |
| 9 | Terrain Fragment |
| 10 | Artisan's Thread |

The cost sits under the button, red when you are short; its tooltip lists the resources and what you carry. The most plentiful ones are taken first. Creative players rebuild for free.

## Death chest

- Only inside the ten worlds. On the Surface, normal vanilla death rules apply.
- It holds up to 54 stacks: your whole inventory except the Artisan's Scroll and Journal, which you keep.
- It appears where you died. If you died in a boss arena, it is moved to the arena's entrance side (22 blocks from the centre toward the Threshold) so you can reach it.
- Chat gives its coordinates. It cannot be broken; using it returns everything and removes the chest. It never despawns.

## Soul Cradle

- Recipe (Matrix Workbench): 4 Oak Planks, 1 Wool Thread, 2 Roots. The surface quest "Fingers in the Doll" also gives one.
- Place it inside a world: it starts with **3 charges** (1 in the Nightmare and Hardcore modes) and becomes your cradle for that world. Placing a new one in the same world replaces the old link (one active cradle per player per world).
- Use it while holding a resource of that world: +1 charge for 1 item and 5 souls.
- After a death in that world, you are moved to the cradle and it loses a charge. Chat tells you how many remain.
- Beds do not work inside the worlds; the cradle replaces them.

Only your group can break your cradle. While a boss is awake within 48 blocks of it, the cradle stays shut and you respawn at your usual spawn point.

## Breaking a World Block

Breaking a World Block is not a death: everyone of your group inside that world is sent out unharmed, and you get a Cracked Doll that puts the block back (see [Core loop](Core-Loop#world-block)).
