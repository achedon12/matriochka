# Administration and Configuration (changes)

## Administrator commands (permission level 2)

| Command | Effect |
| --- | --- |
| `/matriochka world list` | Every group: leader, members, state (active, disbanded, disbanded over 30 days), and each world it opened: World Block position, parcel, boss beaten or not |
| `/matriochka world repair <player> <world>` | Rebuilds the Threshold platform and the boss stage of that player's group's world |
| `/matriochka world move <player> <world>` | Moves the group's World Block to where the command runs; players inside will come out there |
| `/matriochka world reset <player> <world>` | Deletes the world for that group: players inside are sent out, the World Block disappears, the world gets a fresh parcel and its boss counts as not beaten |
| `/matriochka boss reset <player> <world>` | Forgets that the group beat that boss, removes awake bosses in its parcel and re-arms the lair heart |
| `/matriochka progression show <player>` | Highest boss beaten by the player's group |

The earlier commands (`progression set`, `world enter`/`leave`, `boss <id>`, `lair rearm`/`tp`, `karma`, `station`, `debug`) are unchanged.

## config/matriochka.json: difficulty

| Mode | Creature damage | Death | Other |
| --- | --- | --- | --- |
| `story` | x0.7 | The inventory and experience are kept | |
| `normal` | x1 | Death chest in the worlds | |
| `nightmare` | x1.3 | Death chest | Soul Cradles hold one charge |
| `hardcore` | x1.3 | Permanent: you come back as a spectator; the Doll of Life never saves you | A broken World Block deletes its world for the group |

## config/matriochka.json: karma, souls and limits

| Key | Default | Effect |
| --- | --- | --- |
| `karma` | `true` | `false` freezes karma: no action, quest or command moves it. The Journal still shows the value it had. |
| `soulGainMultiplier` | `1.0` | Scales every soul gained in play (creatures, bosses, quests, the Soul Altar). A positive gain gives at least 1 soul unless the multiplier is `0`, which turns soul gains off. `/matriochka karma soul` gives the exact amount. |
| `maxActiveGroups` | `0` | How many groups may hold worlds at once (groups with members and a parcel). `0` = no limit. |
| `maxParcels` | `0` | How many parcels the server hands out in all, every cycle and reset included. `0` = no limit. |

World events have their own keys (`worldEvents`, `worldEventChance`, `worldEventCooldown` and the event weights): see [World events](World-Events).

A group that already holds a parcel is never stopped. When a new group would go over a limit, its Seed or rite site stays unhatched and tells whoever set it down every few seconds that the server is full; it hatches on its own once room is made (a group disbanded, a limit raised).

Comfort options (screen shake, flashes, soft effects, subtitles, HUD, music volumes) are per player, on the client: see [Accessibility](Accessibility).
