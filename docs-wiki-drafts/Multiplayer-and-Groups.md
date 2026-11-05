# Multiplayer and Groups (changes)

## Bosses

| Players | Boss health | Attack speed |
| --- | --- | --- |
| 1 | x1 | x1 |
| 2 | x1.6 | x1.05 |
| 4 | x2.8 | x1.15 |
| 8 | x5.2 | x1.35 |

Health is set when the boss wakes; the attack speed is recounted during the fight from the players within 48 blocks.

## Taking part in the last boss

World progression belongs to the group, but the **gear of the group's newest world** can only be crafted by players who took part in its last boss fight (being near the boss at any time during the fight counts, even if you fell before the end). Older gear stays open to everyone. A newcomer earns it at the next fight: lairs re-arm, offerings can be made again.

## Group commands

| Command | Who | Effect |
| --- | --- | --- |
| `/matriochka group info` | anyone | Members, leader, bosses beaten |
| `/matriochka group leader` | anyone | Who leads |
| `/matriochka group invite <player>` | leader | Invites a player |
| `/matriochka group join` | invited | Joins the inviting group |
| `/matriochka group leave` | anyone | Back to a group of one |
| `/matriochka group kick <player>` | leader | Sends a member out |
| `/matriochka group transfer <player>` | leader | Hands over the lead |
| `/matriochka group disband` | leader | Dissolves the group |

- When the leader leaves, the oldest member leads.
- A player who leaves or is kicked keeps their gear, quests and achievements, but loses the group's worlds and refuge: if they stand in one, they are sent out.
- A disbanded group's worlds are kept for 30 days, then an administrator may reset them (`/matriochka world list` shows which).
