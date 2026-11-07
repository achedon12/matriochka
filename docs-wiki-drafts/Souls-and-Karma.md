# Souls and karma

Souls are the mod's currency: they pay for class upgrades, rerolls, doll layers and cradle charges. Karma is a value from -100 to +100 that changes how the peoples of the worlds and the Surface villagers treat you, which quests open, the variant of the worlds you open and your ending. Both are stored on the player and survive death.

## Soul values

| Rarity | Souls |
| --- | --- |
| Common | 1 |
| Rare | 10 |
| Epic | 30 |
| Legendary | 100 |

Vanilla items use their own rarity: epic 30, rare 10, uncommon 3, common 1.

## Earning souls

| Source | Souls |
| --- | --- |
| Boss kill (every player within 64 blocks) | 100 |
| Reaper gear | 5% more per piece (more with the level) on every kill, and a chance of a soul from creatures worth none |
| Elite creature kill | 5 |
| Structure chests: Soul Shard (5) and Soul Vessel (20), used from the inventory | about 10 per chest, about 100 per world |
| Progress achievement | 5 |
| Exploration achievement | 10 |
| Quest rewards | 10 to 100 |
| Soul Altar | the item's soul value x its stack size |

Your souls are shown on the HUD and with `/matriochka karma show`.

## The Soul Altar

Place an item on the altar and make a final choice. The item is consumed either way and you receive its souls.

- **Purify:** you gain karma.
- **Devour:** you lose karma.

Karma per use = max(0, souls / 10 - repeats / 4), where `repeats` counts how many times you have already used that same item type on the altar. An item worth 10 souls or more always gives at least 1 karma for its first four uses. Cores and Hidden Dolls are refused. Purifying raises karma and devouring lowers it, as do the karma quests.

The altar also has a third button: **Rebuild a layer**, which buys back one Doll of Life layer for 50 souls and 4 rare resources of the current world (see [Doll of Life and death](Doll-of-Life-and-Death#rebuilding-a-layer-at-the-soul-altar)).

## Karma quests

Each world has one karma quest. In the Journal's quest tab it shows **Help** and **Betray** buttons: Help adds the quest's karma (+5 or +10), Betray removes it. Both paths give the quest's soul reward. See [Quests](Quests).

## Karma tiers

| Karma | Attitude | Prices | What opens |
| --- | --- | --- | --- |
| +50 and more | Very welcoming (villagers glow green) | -10% | Mutual-help quests |
| +25 to +49 | Friendly | -10% | |
| -24 to +24 | Neutral | normal | |
| -25 to -49 | Wary (villagers smoke) | +10% | Black markets |
| -50 and less | Hostile in places: one villager in three turns you away ("They turn away from you. Your karma precedes you.") | +10% | Pact quests |

Prices change by at least one item both for the peoples of the worlds, the Doll Peddler and the **Surface villagers** (on top of their own reputation).

## Killing an innocent

Killing a villager or one of the peoples of the worlds costs 5 karma (less once it becomes a habit).

## Black markets

From karma -25, every people keeps other goods under the counter: diamond fragments before their time, boss offerings, materials of the next world. The Doll Peddler sells Diamond Fragments and Shell Shards. Each black-market offer can be bought three times.

## Karma Paths quests

A chapter after the ten worlds in the Journal's quest tab. Mutual-help quests open at karma +50, pact quests at -50.

| Path | Quest | Objective | Reward |
| --- | --- | --- | --- |
| Help (+50) | A Light for Others | Free 100 souls at the Soul Altar | Chance Doll |
| Help (+50) | Many Hands | Trade 10 times with the peoples of the worlds (not the Doll Peddler) | 40 souls |
| Help (+50) | A Warm Hearth | Bring 16 Wool Threads to any people of the worlds | Soul Cradle |
| Pact (-50) | Hunger | Absorb 100 souls at the Soul Altar | 60 souls |
| Pact (-50) | The Price of Silence | Buy 3 goods on a black market | 2 Shell Shards |
| Pact (-50) | No Witnesses | Silence 3 innocents, on the Surface or in the worlds | 2 Diamond Fragments |

Completing a help quest adds 3 karma, a pact quest takes 3.

## Karma at the extremes

- **World variants:** a Seed planted or a rite performed at karma +100 hatches into a Hallowed world, at -100 into a Cursed one. See [World variants and mutations](World-Variants-and-Mutations).
- **Endings:** beating the Unfinished with a karma of 0 or more seals it away; with a negative karma you absorb it, and your karma falls to -100 for good. See [Endings and the New Cycle](Endings-and-New-Cycle).
- Karma is kept through a New Cycle.

## Design notes

The design document balances about 300 souls per world (100 from the boss, 100 from structure chests, 50 from elites, 50 from the altar), which would let a player finish one level 5 set around World 8.

## Souls in structure chests

The chests of the worlds' structures keep souls for the 100 the design budgets per world (about ten chests of ten souls):

| Chest | Souls it holds |
| --- | --- |
| Common | 1 Soul Shard, a second one 34% (World 1) to 48% (World 10) of the time |
| Rare | 2 Soul Shards, a third one 42% to 60% of the time |
| Vault (secret and large combat structures) | 1 Soul Vessel, plus a Soul Shard 34% to 70% of the time |

A Soul Shard holds 5 souls and a Soul Vessel 20. Use one to free its souls; sneak to free the whole stack. These souls are neutral, like those of bosses and elites: they do not move your karma, and the Soul Altar refuses them. Surface chests hold none. Chests already generated before this version keep their old loot.
