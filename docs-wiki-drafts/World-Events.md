# World events

While you are in a world, now and then something happens around you. Once a minute, for every world and parcel with players in it, the dice may start an event around one of them: an **invasion**, a **surge** of the world's rule or a **travelling merchant**. A boss bar names what is going on and how far along it is. One event at a time per world and parcel, then a quiet spell.

Events never happen in peaceful difficulty, around creative or spectator players, near an awake boss or inside a boss stage. Leaving the area ends the event.

## Invasion

A horn and a warning: "The creatures of the world gather. They are coming for you." Ten seconds later, **three waves** of the world's creatures come at you from 10 to 18 blocks away (3 creatures, 2 more per player around, one more per wave). The last wave is led by a **warlord**: one of the world's elites, glowing, with three times its health and half again its damage.

Beat the last wave within four minutes and a **reward chest** stands where you are, with the world's materials, emeralds, bottles of experience, often a Shell Shard and sometimes the world's new gear; every player around also gets 10 souls per world number. Too slow, and the invaders withdraw into the world.

## Surge

A warning names the surge and what it does; ten seconds later, for **two minutes**, the world's rule bites **twice as hard** (the toxin, heat, noise and oxygen gauges change twice as fast) and the surge adds its own effect. The air fills with the world's particles. Weather it and you get 15 souls.

| World | Surge | On top of the stronger rule |
| --- | --- | --- |
| 1 | Spore Bloom | Clouds of poison drift around you |
| 2 | Magma Surge | Now and then the ground spits flame and sets you alight |
| 3 | Lockdown | Mining Fatigue, and every five seconds the locks grind and slow you |
| 4 | Tempest | A gust every five seconds in the open, lightning all around |
| 5 | Blackout | Darkness pulses every three seconds unless a Solar Lantern burns |
| 6 | Gravity Storm | You are thrown up at random, then caught by slow falling (a Stabilizer protects you) |
| 7 | Crushing Current | A deep current drags you while you swim |
| 8 | Season Rush | Hunger, slowness and weakness come and go (a Season Preserve protects you) |
| 9 | Great Quake | Tremors stagger you every three seconds unless the ground is anchored |
| 10 | Unravelling | The surge of the zone's world |

## Travelling merchant

One of the world's people, named and glowing as it arrives, turns up near you with **special trades**, and moves on after five minutes.

| World | Merchant | Sells |
| --- | --- | --- |
| 1 | Wandering Gatherer | Spore Bow, Shell Shard, Chance Doll |
| 2 | Wandering Free Miner | Magma Flail, Shell Shard, Drill |
| 3 | Escaped Prisoner | Key Chain Whip, Shell Shard, Sealed Shackle |
| 4 | Drifting Lighthouse Keeper | Storm Javelin, Lacquer Layers, Storm Censer |
| 5 | Silent Pedlar | Lantern Shield, Shell Shard, Solar Lantern |
| 6 | Stray Reflection | Shell Shard, Mutated Scale, Gravity Boots |
| 7 | Drifting Diver | Tide Harpoon, Shell Shard, Nacre Snorkel Helmet |
| 8 | Passing Ephemeral | Hourglass, Shell Shard, Wreath of Seasons |
| 9 | Uprooted Anchored | Quake Pick, Shell Shard, Grip Boots |
| 10 | Wandering Apprentice | Shell Shards, Artisan's Shard, Mutated Scale |

Each trade can be made twice. Prices are paid in the world's own materials (and emeralds for the Chance Doll).

## Configuration

In `config/matriochka.json`:

| Key | Default | Meaning |
| --- | --- | --- |
| `worldEvents` | `true` | Turns world events on or off |
| `worldEventChance` | `0.06` | Chance, rolled once a minute per world and parcel with players, that an event starts |
| `worldEventCooldown` | `10` | Minutes of quiet after an event in the same world and parcel |
| `invasionWeight`, `surgeWeight`, `merchantWeight` | `3`, `3`, `2` | How often each event is picked |

Operators can start one where they stand: `/matriochka event <invasion|surge|merchant>`.
