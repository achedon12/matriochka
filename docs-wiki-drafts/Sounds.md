# Sounds and Music

Every sound of Matriochka is its own: nothing is recorded, everything is synthesized from seeded recipes by `tools/sound.py` (the table), `tools/sfx.py` (the recipes), `tools/music.py` (the composer) and `tools/synth.py` (the instruments), then written as mono 44.1 kHz Ogg Vorbis by `python3 tools/gen.py`. The same recipe always gives the same file.

The palette follows the nesting doll: lacquered linden wood that twists, pops and clicks, a music box, plucked strings (balalaika, domra tremolo, gusli), a wooden flute, a bayan, church bells and a frame drum. The music is written on Slavic folk modes.

Subtitles exist in English and French for every sound that is not music or an ambient loop.

## Music

Each world plays its own theme every 3 to 10 minutes. The lullaby of World 0 is the motif the giant world, the boss and the endings come back to.

| Track | Where | What you hear |
| --- | --- | --- |
| World 0 | World 0 and the Refuge Doll | The lullaby: a music box waltz in A major over soft plucked chords. |
| World 1 | Toxic Jungle | A swung wooden flute in D Dorian, a music box answering, plucked bass, a drone. |
| World 2 | Giant ores and heat | A fast 2/4 dance in E Phrygian dominant: domra tremolo, oom-pah bass, frame drum. |
| World 3 | Dungeons without sky | Slow bells in A harmonic minor over a bayan pad, in a long stone echo. |
| World 4 | Floating islands and storms | An airy flute waltz in G Mixolydian with a music box countermelody. |
| World 5 | Total darkness | A slow, sparse music box in C minor, alone in a huge reverb. |
| World 6 | Unstable gravity | A music box played backwards (notes swell in) in F Lydian, with a forward echo. |
| World 7 | Pressure ocean | Deep bells and a pad in D minor, muffled as if heard under water. |
| World 8 | Accelerated time | A clockwork music box at 120 bpm over ticking, climbing a fourth every time round (the cycles). |
| World 9 | Hostile terrain | Low plucked strings in C# Phrygian over a heartbeat in the ground. |
| World 10 | The giant world | The lullaby again, in D harmonic minor: domra tremolo, music box, pad and a march drum. |
| Boss | While a Matriochka boss bar is shown | The lullaby turned into a 138 bpm fight: tremolo strings, driving drum, music box. |
| Boss, last phase | Once the boss is below a third of its health | Faster (152 bpm), in Phrygian dominant, with bells. |
| Endings | The Scroll's crawl and credits | The lullaby slowed to a 66 bpm waltz in F major, music box and flute. |

## Adaptive music

The music follows what happens (client/MusicThemes):

| State | When | What plays |
| --- | --- | --- |
| Exploring | Nothing hunts you | The world's theme, as above. |
| Danger | Creatures have you as their target within 24 blocks (held 6 seconds after) | The lullaby at 104 bpm in A Phrygian, tremolo strings over a march drum and a drone, muffled. |
| Boss | A Matriochka boss bar is shown | The boss theme, fiercer below a third of its health. |

Changing state fades the playing theme out (one second) before the next fades in (one and a half): two themes never play together. When the danger or the fight is over, the world theme comes back after a few seconds instead of the usual minutes of silence.

On top of that:

- **Heartbeat.** Below a third of your health, or short of breath (your air, or World 7's oxygen), a slow heartbeat over a muffled drone swells and the theme ducks under it.
- **Stings.** A music box run up the lullaby's scale when you find a structure or a Journal page; a plucked cadence and a chord when a quest is done.

Each part has its own volume in the [comfort options](Accessibility). The danger theme, the heartbeat and the stings are rendered like the rest; their recipes live in `tools/cues.py`.

## Ambience

Each world has a seamless 24-second loop and one-shot sounds that play at random.

| World | Loop | One-shots |
| --- | --- | --- |
| 0 | none | Painted wood creaking. |
| 1 | The jungle breathing: leaves and air swelling, insects pulsing. | Insect buzz, spore puffs. |
| 2 | A low heat rumble with sparse embers. | Distant hammer strikes, crackling embers. |
| 3 | A dark stone drone and a cold draft. | Rattling chains, a door slamming far away. |
| 4 | Wind in three bands with a whistle that follows the gusts. | Whistling gusts, distant thunder. |
| 5 | Near silence: a very low breath of air. | Something breathing close, footsteps nearby. |
| 6 | A warbling, bending hum. | A chime played backwards. |
| 7 | Deep pressure rumble and muffled water. | Water drips, pressure groans of a hull. |
| 8 | Three clocks ticking at their own pace. | A clock striking, a cuckoo. |
| 9 | Ground rumble and a slow heartbeat. | The ground beating, rock grinding. |
| 10 | Wind, rumble and far ticking at once. | One-shots borrowed from worlds 1, 4, 7, 8 and 9. |

## Nesting dolls and World Blocks

| Sound | When | What you hear |
| --- | --- | --- |
| Doll opens | Station screens, nesting chests, the Refuge Doll, World 0's door | Two lacquered halves twisting, then a hollow pop. |
| Doll closes | Station screens, nesting a hidden doll, placing a cracked doll, recharging the Doll of Life | A twist, then the rims clacking shut. |
| Doll clicks | Sorting a nesting chest | A single wooden click. |
| Doll rattles | A hidden doll that does not fit, rerolling a class with a Chance Doll | A doll shaken: quick wooden clicks. |
| Doll of Life breaks | It saves you from death | The shell cracks and a bell and a music box arpeggio bloom. |
| World Block opens | Entering a world | The doll opens, a whoosh falls and a music box runs down two octaves. |
| World Block forms | A Seed becomes a World Block | A rising music box arpeggio, a bell and the doll closing. |
| World Block cracks | Breaking a World Block | Wood and lacquer splitting with a low knock. |
| Seed hums | A planted Seed growing | One music box note that rises in pitch as the Seed grows. |

## Stations

| Station | What you hear |
| --- | --- |
| Matrix Workbench | Three wooden knocks and a gilded music box arpeggio. |
| Class Table | A whetstone, an anvil ring and a two-note chime. |
| Soul Altar | Purify: a pure chord swelling and a bell. Devour: a low growl and a swell sucked backwards. |
| Spore Vat | Bubbling and the lid popping. |
| Ash Foundry | The furnace roaring, crackles and molten metal hissing. |
| Jailer's Table | Each correct pin clicks a little higher; the lock gives with three tumblers and a bolt. |
| Lightning Forge | Sparks, an electric zap and an anvil ring. |
| Dark Altar | A low hum, whispers and a dark bell. |
| Inverter | Two tones gliding through each other and trading places. |
| Abyssal Press | A hydraulic hiss, a deep thud and bubbles. |
| Time Workshop | Ticks that speed up, then a chime. |
| Terrain Anchor | A deep stone thud and a hum that settles. |
| Final Loom | Shuttle clacks and a gusli run up the whole scale. |

## Bosses and world rules

| Sound | What you hear |
| --- | --- |
| Boss awakens | A low drone swells, a bell tolls and the doll shell creaks open. |
| Boss prepares an attack | Each world's own warning: its lead instrument climbs a tense figure over the world's texture (wooden knocks, spores, anvils, chains, wind, an inhale, a reversed note, drips, fast ticks, a heartbeat, clashing bells). |
| Boss shell cracks | A new phase: a crack, a boom and a falling minor figure on bells. |
| Boss defeated | The lullaby's cadence on music box and gusli under a bell. |
| Gust of wind | World 4's gusts that push you. |
| Gravity wavers | World 6, before the zones flip: a bending pad and a reversed music box note. |
| Ground heaves / rumbles | World 9 zones moving, and the warning before. |

Creature attacks keep their vanilla sounds, which fit them; an attack in `tools/attacks.py` can now name one of the mod's sounds with its namespace (`matriochka:doll.rattle`).

## Changing a sound

Edit its recipe in `tools/sfx.py` or its theme in `tools/sound.py`, then run `python3 tools/gen.py`. Rendering needs numpy and ffmpeg with libvorbis; `tools/sounds.lock.json` remembers a hash of every recipe, so only the sounds whose recipe changed are rendered again (a change to the synthesizer itself renders everything, about two minutes), and gen.py runs without numpy or ffmpeg when nothing changed.
