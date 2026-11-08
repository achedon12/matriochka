# Changelog

## 0.9.0 (beta)

Every world has an ore of its own, each one had its own way; set together in the Nesting Cradle, the ten are nested by a nest of ten dolls into the Matriochkite Ingot, the metal of the Matriarch Armour. Matriochka leaves alpha for beta.

### The ten world ores

- World 1, the Spore Crystal: it grows on the Spore Blooms that stand near water. Break a bloom with water within 4 blocks, about one in seven gives one.
- World 2, the Living Ember: mined from a Living Ember Vein deep in the Giant Veins, it only stays alight in a burning hand. With your Heat under 70 it goes out with a hiss and leaves ash.
- World 3, the Golden Ward: never mined, it lies only in the vault chests of the Endless Dungeon.
- World 4, the Fulgurite: the lightning of the Storm Archipelago fuses the cloudstone (under its grass too) or the sand it strikes into a Fulgurite Crust. Mine the crust.
- World 5, the Silent Stone: its veins shatter at the slightest sound. Mine them with your Noise at 0, sneaking.
- World 6, the Inverted Ore: its Hanging Veins grow on the underside of the Upside Realm's rock, under its overhangs and vaults. Mined, it falls upwards for a few seconds: catch it before it is gone.
- World 7, the Brine Crystal: any creature of the Pressure Ocean may leave one, about one in twenty-five.
- World 8, the Chrono Shard: the Time Seed lies in the chests of the Hastened Seasons. Planted on grass or dirt in World 8, it ripens in two minutes, far faster than any crop, into the shard.
- World 9, the Heartstone: the Heart of the Terrain leaves two or three when it falls.
- World 10, the Artisan's Thread, mined from the Thread Spools as before.
- Each ore's tooltip and its world's card in the Journal say how it is had.

### The Nesting Cradle

- A great carved matryoshka of red lacquer and gold, some two blocks tall, made at the Final Loom: an animated model, its upper half breathing ajar on a hinge, a glow inside the bowl, a ring of gold beads with a socket for each world turning round its waist. Set one ore of each world in it: the ore rises into its world's socket, which lights in that world's colour, and sings its note of the lullaby. An empty hand takes the last one back.
- The tenth starts the ritual, eight seconds keyed on the model: the ring spins up and draws in while light runs from every ore to the middle; the upper half is thrown open and a nest of ten smaller dolls, painted in the hidden dolls' worlds, rises out of it, fans out and spins; one by one they close over the next, the smallest first, each with a wooden clack; the last sinks into the bowl, the doll slams shut, jumps, shakes and glows in a golden flash, a pillar of light and a shockwave, the lullaby's chord; then it opens a last time on the Matriochkite Ingot, which rises, spins and pops out to the player.
- It is all run by the server and played from its start tick by every client near. A cradle broken before the flash gives its ores back.

### Matriochkite

- The Matriochkite Ingot, and a Matriochkite Nugget and a Block of Matriochkite at the crafting table (nine of one make the next, and back). The block is red lacquer framed in gold, painted with a rosette of the ten worlds round a gold doll, its gold glowing; it can stand under a beacon.

### The Matriarch Armour

- Helmet, chestplate, leggings and boots of Matriochkite Ingots (2, 3, 2 and 1), laid over the Artisan's own pieces at the Final Loom.
- Worn, it is a model of its own: a lacquered doll's-head crown with a gold rim, a kokoshnik crest with a small painted face and a row of pearls; pauldrons like little nested doll halves; a khokhloma breastplate (red, black and gold, a touch of green) with a matryoshka in gold filigree and a gem at its heart; layered skirt plates painted with folk flowers; boots with gold toe caps. A glint runs along its gold, and the gem is lit while the Nested Shell is ready.
- Just above the Artisan's set: 32 armour (Minecraft counts at most 30), 18 toughness, a little more knockback resistance, and one more heart per piece.
- The whole set's Nested Shell: every world's gauge builds half as fast (Toxin, Heat, Noise and the loss of breath), and once every five minutes a blow that would kill leaves you at three hearts instead, before the Doll of Life, which is then not spent. The screen flares gold and the outer doll's cracks run across it for a second.
- Its tooltip lists the set as a checklist (the pieces worn lit), says the bonus in two lines and the shell's state, ready or mending with the time left; a small doll beside the hearts, while the whole set is worn, is full when the shell is ready and fills back up as it mends.
- The Journal's card of World 10 opens on the chain: the ten ores, the Nesting Cradle, the ingot, the armour; every link's tooltip says it too.

### Sounds

- Ten music box notes of the lullaby, one per world's ore, the chord of the ten dolls, the clack of a golden shell and the crack of the Matriarch's outer doll.

### Interface

- Long item descriptions are laid on several lines in their tooltips.

### Fixes

- On Minecraft 26.3 the talents' extra blows were lost to the cooldown between two hits: they land again.

### Beta

- Releases on Modrinth and CurseForge, the mod and its packs, are published as beta.

### Checks

- `./gradlew runClientGameTest -Pnesting` (also run by `-Ppolish`) checks in game how each ore is had, runs the cradle's ritual from the ten ores to the ingot, crafts the Matriochkite, and wears the Matriarch Armour: its stats, its halved gauges, the Nested Shell's one save before the Doll of Life and its count on the HUD.

## 0.8.0 (alpha)

The wonders can be found and are worth finding: the worlds' people point at them, every relic gives its world's gift, a group shares the reliquary, and the Journal draws a map of every world.

### Wonders and relics

- The people of every world speak of its wonder: one greeting in two, while its relic is still to be found, they say in which direction it stands and how far. The Journal's world card keeps what they said.
- Every relic gives, besides its heart, a gift of its world: the relics of Worlds 1, 2, 5 and 7 make Toxin, Heat, Noise and the loss of breath a quarter slower (World 10 has all four rules); the others give luck in chests, faster attacks, safe falls, speed, less knockback or faster mining. The ten together add 4 armour.
- A reliquary opened by one member of a group gives its relic to every member standing within 24 blocks, straight into their inventory.
- The Last Candle is rebuilt as a great wax candle in a ring of open arches, and the Sleeping Giant as a giant lying on its back, face to the sky, moss grown over it.

### Journal

- A map of every world, from the world's card: the ground walked through inked in the world's colour, the places found drawn by role (people, combat, exploration, story, secret, wonder), the player as a small doll, and a legend of what has been found.

### Music and sounds

- Each of the twenty lesser biomes has its own variation of its world's theme, in the same mode, with its own tempo and lead instrument.
- New sounds for the reliquary opening and refusing a key, for a relic taken in, and a quiet air near a wonder.

### Checks

- The game tests check that every world raises its wonder inside the group's parcel and that a relic eases its world's rule.
- The CI's game runs on Minecraft 26.3 start at last: it gets a software Vulkan device beside Mesa's OpenGL.

## 0.7.0 (alpha)

Every world hides a wonder with a sealed reliquary that only a key from another world opens, the Journal gives every world a card of its items, the Surface has more to find before the first boss, and every block, item, tool and armour piece is repainted.

### Wonders and the keys between the worlds

- One wonder per world, rarer than any structure and seen from afar: the Mother Tree, the Molten Heart, the Hall of Keys, the Eye of the Storm, the Last Candle, the Upside Spire, the Sunken Bell, the Stopped Clock, the Sleeping Giant and the Artisan's Desk.
- At its heart a sealed reliquary, and beside it a vault chest with the world's cross key. A cross key never opens its own world's reliquary: the key of World n opens the reliquary of World (n + 3) mod 10 + 1, so the worlds have to be travelled back and forth. The wrong key leaves it shut and says which key it waits for.
- Opened, a reliquary gives its world's relic, once per player. Each relic used adds one heart of health for good, ten relics ten hearts.

### Journal

- Every world has a card: its items and how each one is made (at which station), dropped (by which creature or boss), mined or found (in which chests). Open it by clicking the world on the Worlds page.

### Surface

- The Artisan's old cabin, with notes of his in the chests; the Peddler's stall; a giant doll fallen from somewhere higher. They are found above ground, before the first boss.

### Textures

- Every block, item, tool and armour piece is repainted in Minecraft's own manner: hard tones, clustered materials, lit edges and a shape of its own for every material.

### Checks

- The CI's first steps and whole-game runs are bounded in time, and their logs are kept even when they fail.

## 0.6.0 (alpha)

The mod now runs on Minecraft 26.1.2, 26.2 and 26.3, every world has two lesser biomes, every boss fights to its own theme, and the dolls have a body when they are held.

### Minecraft versions

- One jar for each of Minecraft 26.3, 26.2 and 26.1.2, built from the same code: what differs between the versions lives in `versions/<mc>/` (the dependencies, the few renamed calls, and the world generation in each version's own format, written by `tools/versions.py`).
- On 26.3, worlds 1 to 6 and 8 to 10 wore vanilla grass, dirt and netherrack on their surface instead of their own moss, ash, brick and felt: their surface rules are now written out with the mod's blocks, as on the older versions.

### Worlds

- Every world has two lesser biomes beside its own, each with its own floor, colours and name: the Bloom Hollow and the Rot Marsh in the Toxic Jungle, the Ember Fields and the Ash Drifts in the Giant Veins, the Mossy Cells and the Crumbling Wing in the Endless Dungeon, the Hail Meadows and the Thunder Heights in the Storm Archipelago, the Hushed Hollow and the Bare Dark in the Lightless Deep, the Crystal Fields and the Mirror Flats in the Upside Realm, the Coral Shelf and the Black Trench in the Pressure Ocean, the Hourglass Dunes and the Rust Grove in the Hastened Seasons, the Flesh Mire and the Bare Rock in the Restless Ground, the Plank Floor and the Lacquer Tray in the Giant Workshop. The world's creatures, people and structures live in all three.
- The Abyssal Pearl can no longer be washed away by the water it lies in.

### Bosses

- Every boss fights to its own theme: the lullaby at a fighting tempo, in its world's key and mode, led by its world's instrument. The last third of a fight keeps the shared final theme.
- In a New Cycle every boss wakes mutated, even before World 6, and the mutation changes from one cycle to the next.

### Items

- The dolls (trophies, hidden dolls, the Doll of Life, the Refuge, Chance and Cracked Dolls, the Nested Dolls) are turned in 3D wherever they are held, worn, framed, dropped or carried on a shoulder; the inventory keeps their sprite.

### Comfort and settings

- Gauge patterns also show a boss's health in figures on its bar.
- Mod Menu's configure button opens the comfort settings.
- `/matriochka difficulty` shows the difficulty, `/matriochka difficulty <story|normal|nightmare|hardcore>` (operators) changes it for the whole server and saves it.

### Compatibility

- Roughly Enough Items shows every station's recipes, as Just Enough Items does.
- Jade names the world inside a World Block, its variant and its cycle, and the world a planted Seed or a rite will open.

### Languages

- Italian, Russian, Polish and Simplified Chinese, beside English, French, Spanish, German and Brazilian Portuguese.

### Checks

- A test run ends at once, with the error, when the game breaks where the test cannot see it (a chunk that fails to generate, a data file that does not load), instead of waiting forever.
- `python3 tools/check_refs.py` checks, without starting the game, that every reference in the data of every Minecraft version points at something that exists.
- `tools/server_smoke.sh [mc]` starts the mod on a dedicated server and generates every world.
- The CI runs the dedicated server and the first steps for every Minecraft version, and the whole game on every push to main.

## 0.5.2 (alpha)

The fights close in and hit harder, the bosses break as they weaken, the worlds' people speak, and the interface wears the mod's colours from the title screen to the tooltips.

### Fights

- A lair's portcullis drops row by row over the chamber's doorway when its boss wakes, and an altar arena's arch is barred while its rim burns with the world's light. Both open when the boss falls, or after 20 seconds with nobody inside, and close again behind the first one back.
- A boss breaking into its later phases shows glowing cracks of its world's colour, more after the second.
- A heavy or critical blow jolts the attacker's camera a little (comfort slider); the worlds' weapons spray their world's matter where they land and ring with the world's sound on a heavy hit.
- A boss's relics fall where it fell and stay there, or at the nearest fighter's feet when it fell over the void.

### People and worlds

- The worlds' people greet a player who comes near in a speech bubble over their head, with a line that knows whether the boss of their world has fallen (the Peddler: how far down the group has gone).
- The open worlds have skies of their own: a dark moon behind the spores, a full moon in the storm, an upside-down sky with stars by day in World 6, a starry sky over the sea, no stars in the Workshop.
- A trophy doll won in the Trials rides on its owner's shoulder.

### Interface

- Matriochka items show their world, rarity and souls as pixel icons under their name.
- Matriochka advancements are announced on the mod's own lacquer card.
- The Journal's Worlds page shows the worlds nested as dolls and what has been gathered of each: pages, hidden doll, rite and boss.
- The title screen shows a row of nesting dolls and the mod's version; a dive's loading screen stays dark under the doll's outline.

### Checks

- `./gradlew runClientGameTest -Ppolish` photographs the title screen, a tooltip, a toast, a greeting, a trophy on a shoulder, the Journal's map and World 6's sky; the playthrough checks every stage closes and opens again.

## 0.5.1 (alpha)

Every boss now has a bar of its own and a proper end, and diving into a world is a moment of its own.

### Bosses

- Every boss bar is drawn for its boss and its world, in pixel art on Minecraft's grid: runed stone pillars for the Block Guardian, mushroom clusters for the Spore Queen, furnaces for the Ash Titan, padlocks and bars for the Grand Jailer, lightning rods in storm clouds for the Storm King, violet eyes in smoke for the Light Eater, mirror crystals for Your Double, a porthole and a pressure dial for the Pressure Leviathan, a gear and a clock for the Master of Seasons, a heart crystal for the Heart of the Terrain, and a doll painted at one end and sketched at the other for the Unfinished.
- Each gauge is the boss's own matter, animated: stone blocks, toxic sludge, molten metal, soul fire, a lightning arc, a dark that swallows light, a mirrored gauge emptying from both ends, deep water, the four seasons, a heartbeat, red lacquer. The damage just taken lingers as a pale trail, each phase is a notch, the name flashes on a hit, and the ends of the bar come alive.
- Every boss comes out of its shell when summoned: folded and small, it swells, rears up and roars, with a burst of its world's particles.
- A fallen boss folds back into its doll: two rings of gold close on it, its name is sealed on a card, and its relics fall from a column of light once the doll has closed. A boss unloaded before that still leaves its relics.

### Worlds

- Using a World Block closes the screen on a doll-shaped iris in the world's colour while the camera plunges, and the iris opens again on the other side; the Threshold runs it the other way. With cinematics off (comfort options), a plain fade.

### Stations

- The Matrix Workbench's grid taps when a piece is set on it, rattles when a drawer lays a pattern out and chimes when a recipe forms.

### Checks

- `./gradlew runClientGameTest -Ptransition` dives into World 1 and climbs back out; `-Pawaken` summons every boss and photographs its awakening, its bar and its defeat.

## 0.5.0 (alpha)

Every world now has its own way in, the stations are sculpted 3D pieces with screens of their own, and the Matrix Workbench is a real crafting table.

### The way into each world

- Only World 1 still grows from a Seed planted on tilled World Soil 0. Every other world opens with its own object and its own rite, made at the Matrix Workbench from the core of the boss before it:
  - World 2, Ember Heart: within 3 blocks of lava, with 4 Ashrock around it.
  - World 3, Jailer's Key: against an iron door, with a redstone signal.
  - World 4, Storm Rod: on top of a lightning rod under the open sky, opened by a storm or a Storm Essence.
  - World 5, Black Lantern: in complete darkness, with 4 Spent Glow within 2 blocks.
  - World 6, Twin Mirrors: between two glass blocks, two blocks away on either side.
  - World 7, Abyssal Pearl: dropped into water 3 blocks deep.
  - World 8, Sapling of the Four Seasons: planted on grass or dirt, opens at dawn or dusk.
  - World 9, Seismic Stake: driven into stone or deepslate below y 40.
  - World 10, Traveller's Matryoshka: anywhere.
- A rite site shows its object, puffs smoke while it waits and tells the player nearby what it still lacks. Feeding it still leans its world calm or wild. Each object keeps its item id (seed_2 to seed_10), so saves, recipes and quests carry over.
- The bosses of Worlds 1 to 9 no longer drop World Soil; the Guardian still leaves the four soils World 1 needs.

### Stations

- The thirteen stations are sculpted 3D models that face the player who places them, with fitted shapes and moving parts: the matrix over the workbench, the rank medal, the soul wisps, the vat's bubbles, the jailer's key, the forge's arc, the dark crystal, the inverter's ring, the press ram, the pendulum and clock hands, the anchor's stones, the loom shuttle. Their lit parts glow in the dark; the HD pack has 32 x 32 materials.
- Every station screen has its own layout and material: jars on two shelves (Spore Vat), crucibles (Ash Foundry), key tags on chains (Jailer's Table), plates in two arcs over an anvil (Lightning Forge), rune circles (Dark Altar), mirrored rows (Inverter), a honeycomb of portholes (Abyssal Press), medallions round a gear (Time Workshop), strata (Terrain Anchor), banners (Final Loom). A bar under the pieces shows the recipe under the cursor, and the niche holds a live instrument per station: thermometer, capacitor cells, an eye that opens in the dark, a depth gauge, a clock, a seismograph.
- The Matrix Workbench is a 3 x 3 crafting table: every recipe made there has a pattern built from its exact cost, the result is taken like a crafted item, and its drawers fill the grid from the inventory like a recipe book.

### Sound

- Every boss is heard before it is seen: a breath, a growl or a hum in its world's colour.
- Each rite sounds like its world while it works (embers, a turning key, a storm, a breath, glass, water, leaves, grinding rock, wooden doll halves) and opens its world with a swell in the world's own key.

### Site

- An Items page lists every item and block as an inventory, with nested dolls to pick a world, a search, and a sheet for each one: its recipe drawn slot by slot (the workbench's as a real 3 x 3 grid), the station that makes it, where it comes from, what it is used for and, for a station, everything it makes. Every ingredient and use opens its own sheet.
- Recipes across the site are drawn the same way, with the stations' 3D renders and vanilla ingredient icons.

### Checks

- `./gradlew runClientGameTest -Pmachines` photographs every station model, the row by day and night, and every station screen; `-Prites` performs the nine rites and checks each opens its world.

## 0.4.3 (alpha)

Each world's rule meter now reads like the vanilla HUD: a row of ten icons above the hunger bar.

### Interface

- Each world's rule meter is now a vanilla status row instead of a gauge bar in the plaque: ten 9 x 9 pixel-art icons right above the hunger bar, filling in halves like the shanks (5% a half icon). A drop that fills with poison (World 1), a flame (2), an hourglass toward the halls' next move (3), a lightning bolt charging up to the next gust (4), a bell for noise (5), a feather toward the columns' next turn (6), brass portholes of breath and, with a snorkel helmet, small air tanks (7), a leaf in the season's colours as the season turns (8), a cracked stone toward the next tremor (9), the zone's own meter in World 10 and an eye for Obsession (World 0). The containers flash white when the meter jumps, the icons tremble when it climbs fast, and near the threshold they shake like low hearts and pulse in their danger colours (steady with Flashes off).
- The row is a Fabric status bar: it stacks above the air bubbles under water and above a mount's hearts, other mods' bars stack around it, and it hides with the vanilla bars (F1, creative, spectator).
- The plaque keeps the world's medallion, its name and its rule, the Doll of Life and the souls; the Gauge patterns option now draws its stripes and crosshatching on the row's icons.

### Systems

- The server syncs the progress of the timed rules (the halls' move, the gusts, the gravity columns, the season and the zone a player stands in within World 10) so the client can draw their meters.

### Checks

- `./gradlew runClientGameTest -Phud` photographs the row in every world at 0, 35, 55 and 90% at GUI scales 2 and 3, under water with the air bubbles, with a snorkel's tank and breath, with full armor and absorption hearts, riding a horse, with the patterns, with F1 and in creative, the plaque with the first-steps card and a trial.

## 0.4.2 (alpha)

The mod's traders get a painted market stall, and every ending now closes on a recap of the cycle.

### Interface

- The mod's peoples trade at a painted market stall instead of the villager screen (the people of each world, the Doll Peddler, the travelling merchants and the black market): a ledger of every offer on parchment with its stock and the karma's discount or markup, a plum "under the counter" section for the black market's goods, sold-out lines stamped, the trader's plaque with its world's medallion, the kind of trader, a travelling merchant's time left and the karma, the counter with the selected trade and the inventory tray. The menu, its slots and its packets stay vanilla's: shift-click, the wheel, tooltips and the delivery quests work as before, and vanilla villagers keep their screen (see [Trading Stall and Cycle Recap](docs-wiki-drafts/Trading-Stall-and-Cycle-Recap.md)).
- The recap of a cycle after an ending's crawl: the great doll opens in two halves on the ending, the cycle, the eleven bosses' cores, worlds opened, deaths, Doll of Life layers lost and rebuilt, souls gathered, time played, hidden dolls, Journal pages and quests, karma, class and the best Trial. F1 hides the buttons for a picture to share; the Journal's Objective page reopens it (**Last cycle**).

### Systems

- The player's state counts each cycle (time played, deaths, layers lost and rebuilt, souls, pages, quests, hidden dolls, worlds entered, bosses beaten, Trial times), saved and synced with the rest, written into the recap at each ending and started again at each New Cycle.

### Website

- Each boss's 3D viewer plays its real attacks, named in English and French, as one move (wind-up, strike, recover), plus its phase change and fall; the bosses page shows every attack's wind-up and strike in game, with a link to the attack in 3D.
- The French site no longer shows English animation names, nor "Iron pickaxe".

### Checks

- `./gradlew runClientGameTest -Pscreens` opens the stall for the Peddler, a people with many wares (scrolled), the black market, a travelling merchant and a sold-out line, trades through it by click and shift-click and checks the stock and the karma's prices; then counts a real death, a boss kill and a page found, reaches the three endings in two cycles, checks the recap's numbers and the Journal's button, and photographs both screens at GUI scales 2, 3 and 4, in a 640x480 window, in English, German and French.
- Test runs and captures play no sound (OpenAL Soft's null output); `-Psound` for a capture that needs audio.

## 0.4.1 (alpha)

The kneel at the end calms the whole room, the Trials and talent screens and the new structures are fixed after a look at every one of them, talents are balanced against the design, and the Matriochka Pack has its own Modrinth project.

### Balance

- `tools/balance.py` now models the talents: for every class and world, the talents open on arrival, applied as the game applies them, on top of the design player. A class's whole tree may move the hits to kill a creature, the hits you survive and the length of a solo boss fight by a quarter at most (report: [Balance](docs-wiki-drafts/Balance.md)).
- Berserker talents lowered: Giantkiller and Shell Splitter 6% + 12% -> 3% + 5% against bosses, Cleaver 5% -> 4%, Bloodied and Red Mist 15% + 25% -> 10% + 12%, Opener and Finisher 20% -> 10%, Quick Arm and Flurry 5% + 10% -> 3% + 4% attack speed. With the weapon's +58% at level 5, the tree added up to +101% against a boss and cut the solo fights of Worlds 9 and 10 by 40%; now +83% and 24%.
- Guardian: the bulwark gives health and toughness instead of armor (Stout +1 max health, Plated and Unbroken +0.5 toughness, Last Wall 10%), Broad Back and Hearty +1 max health, Lacquer Skin 2 absorption. Near the armor cap every point counts so much that the tree made a World 9 player survive 5.3 strong boss blows instead of 3; now 3.8.
- Survivor: Thick Skin and Iron Heart +1 and +2 max health, Stubborn and Never Down 10% and 15%. Prowler: First Cut 10%, Stalker and Assassin 10% and 20% while sneaking.

### Fixes

- The ending's kneel calms the whole room: the creatures the Artisan's Shadow called in let go of the kneeling player, freeze in loose thread and unravel into thread and gold dust a second later, and the blows already thrown fade. They no longer knock the player off the carpet.
- The new structures of the Ember Veins (World 2) stand on a cave floor under the rock roof; they were placed on the roof, above the build limit, and never built.
- The caravans, circles, outposts and bastions no longer stand on a pillar of foundation in the middle of a lake or a sea.
- The Lantern Shield is held like a shield and raised across the body while it blocks (it was held like a flat item); its flare bursts in gold sparks in front of the bearer instead of white rods in the player's face.
- The trial clock sits under the boss bars instead of over them, scales with the HUD size comfort option, and the boss attack subtitles keep below it. The countdown is drawn large in the middle of the screen, a gilt figure each second.
- The Talent cabinet: the talent's name sits on the plaque between the sprigs, the description, cost and reason shrink together to fit the red panel in any language, branch and class names shrink instead of being cut, the tree is centred on its panel and the Forget button is a full lacquer button.
- The Trials book and the Journal no longer overlap wrapped text with what follows it; the Trials board's empty line wraps on the page.
- Rebuilding a Gauntlet stage no longer drops the previous stage's carpets and banners at the players' feet.
- Surges use their world's own particles (spores, embers, cold dust, storm sparks, shadow wisps, mirror shards, bubbles, petals, grit, thread), the warlord's name and its wave's warning are written in gold instead of an unreadable dark red, the harpoon draws its line to its catch, and the Quake Pick's tremor cracks the ground in rings of crumbs and grit.
- The harpoon line is only drawn while its thrower is in the same world and within 48 blocks.
- A first-steps guide that jumps to its end (progression given by command, a group ahead, an ending already seen) no longer shows its goodbye card, and the card never draws during a trial.

### Checks

- `./gradlew runClientGameTest -Preplayshots` photographs the Trials, their stages in ten worlds, the HUD clock, the Trials and Talent screens in English and German, the new gear in hand and in use, the world events and the ten new structures (`-Ptakes=gtues` for parts).
- The playthrough test keeps the Shadow's creatures in the room while kneeling and checks that they are stilled and that nothing knocks the player off the carpet.

### Matriochka Pack

- A CurseForge version of the pack: `tools/modpack.py --curseforge` writes the CurseForge modpack (`manifest.json`, `modlist.html`, the same configs), normal and hard, from the same files as the Modrinth pack, each matched to its CurseForge file by its bytes and checked against the CurseForge CDN. Mods with no such file are left out with what needs them: for 0.4.0, Mod Menu and its library Placeholder API (no 26.3 file on CurseForge), and JEI until its file is approved.
- The pack is published on its own Modrinth and CurseForge projects: the release workflow uploads the hard then the normal pack once the `MODRINTH_PACK_PROJECT_ID` and `CURSEFORGE_PACK_PROJECT_ID` variables are set (the CurseForge export needs a `CURSEFORGE_API_KEY` secret), without ever failing the mod's release, and a new `modpack` workflow does the same for a version already released.
- Listing material for both sites in `branding/modpack/`: an icon of its own (three dolls tied with a gold ribbon), descriptions, summaries, categories and a gallery.

## 0.4.0 (alpha)

Trials, world events and talents to replay the worlds, a unique animation for every boss attack, a new look for each world, the design's rules for automation, souls and quests, comfort options, cinematics and adaptive music, a guided start, and three new languages.

### Replay value

- Trials, open once you have seen an ending: a rush per world (two waves of its creatures, the second led by its elites, then its boss) and the Gauntlet of the eleven bosses, fought against the clock on a lacquered stage inside the Refuge doll, painted for each world. Trial bosses have more health and damage and always wake mutated, without their introduction cinematic, and grant nothing of the story. Open them from the Journal's Objective page, a new Trial Altar or `/matriochka trials start`. Falling carries you out instead of killing you.
- A trial clock on the HUD (green under par), best times per player and per group, and a server-wide board of the ten best groups per trial, in the new Trials book and with `/matriochka trials top`. The first win of each trial gives its Trophy Doll and a title; finishing under par gives Swift Hand. Titles can be worn from the Trials book, quest titles included.
- World events while you are in a world: invasions (three waves, the last led by a glowing warlord, a reward chest at the end), a surge of each world's rule (twice as strong for two minutes, with its own effect and particles: Spore Bloom, Magma Surge, Lockdown, Tempest, Blackout, Gravity Storm, Crushing Current, Season Rush, Great Quake, Unravelling) and a travelling merchant per world with special trades. A boss bar follows each event. Never in peaceful; frequency and weights in `config/matriochka.json` (`worldEvents`, `worldEventChance`, `worldEventCooldown`, the three weights). Operators can start one with `/matriochka event`.
- Talent trees at the Class Table: three branches of four talents per class, bought with souls and, for the last two of a branch, Shell Shards, opened by your group's progression. A class's talents act while you wear or hold its gear. A new cabinet screen with the six trees, tooltips for every talent and a Forget button that gives back half the souls.
- New gear with its own behaviour: the Spore Bow (World 1), Magma Flail (2), Key Chain Whip (3), Storm Javelin (4, thrown, calls lightning and comes back), Lantern Shield (5, a blocked blow blinds and throws back), Tide Harpoon (7, thrown, drags its catch back) and Quake Pick (9, mines three blocks, a tremor on the ground). Each is crafted at its world's station and has hand-drawn pixel art; the bow has its drawing frames.
- One more structure per world: the Gatherers' and Ephemeral Caravans, the Ember, Hushed and Restless Circles, the Gaolers' Gatehouse and the Drowned Bastion, the Sky, Hanging and Thimble Outposts, each decorated in its world's materials, with its loot.

### Bosses

- Every boss attack has its own hand-made animation: the boss shows what is coming during the warning (the Guardian heaves a torn block overhead, the Queen's egg sac swells, the Titan lifts its hammer, the Jailer spreads its arms like walls, the Light Eater sinks low to stalk...), strikes, then stays open and spent for exactly as long as it takes extra damage. Each boss also has its own phase change (the Guardian rebuilds itself, the Queen folds into her cocoon, the Jailer turns its key, the Unfinished paints a new face) and its own fall, which now plays out for two seconds instead of the vanilla tip-over.
- The Artisan's Shadow keeps its animations in step with the world whose timing it borrows; the Unfinished's are cut for the final, shortest tier it now fights on.
- The Unfinished now fights on the shortest timing tier on every shell, as the final fight of the design.
- Bosses no longer poison themselves in their own toxic cloud, nor get struck by the lightning they call down (a player's lightning still hits them). The Jailer's floor cage only closes on the fighters, not on spectators or creative players watching.

### Look and atmosphere

- New hand-painted textures for the items and blocks you see most, in the vanilla style (outlines, three to four tones lit from the top left, warm highlights and cool shadows): the ten hidden dolls, the Nested Dolls, the Whole Matryoshka and the other dolls, the eleven cores, the ten Seeds, every armor piece and world weapon, the four snorkel helmets, the Scroll, Journal and pages, the four boss offerings, the World Soils, the World Block, the Threshold and every face of the thirteen stations. Each world's objects share its palette and glyph.
- The lit parts of the stations and the Threshold's doorway glow in the dark (emissive faces, as vanilla does for the firefly bush).
- Every world has its own light and fog: spore haze in World 1, heat and falling embers in World 2, cold dust in World 3, a storm sky in World 4, near-black fog in World 5, an inverted pastel sky in World 6, deep blue water fog in World 7, light tinted by the season in World 8 (petals, pollen, leaves or snow), rust haze in World 9, warm workshop light with floating fluff in World 10, and lantern light with gold dust in World 0.
- World 0 reads as a warm red dusk, not a wall of fog: the lacquer carries its own light and the haze opens from 12 to 112 blocks. World 3's cold fog is darker than its stone, so its halls read at a corridor's length; World 5 stays black, but a lantern now reads across a cavern (its fog closes in from 4 to 30 blocks).
- Eighteen new particles (spores, embers, cold dust, chain glints, lightning sparks, shadow wisps, deep motes, mirror shards, bubbles, petals, pollen, leaves, snowflakes, grit, rust, thread scraps, fluff, gold dust). Boss attacks spray their world's particles where they land and around their warning ring, and many creature attacks use them.
- The bubble, cold dust, deep mote, pollen and rust particles are redrawn so they read at their size (the bubble's first frame had broken into four corner dots).
- Matriochka HD: an optional resource pack with the same textures at 32 x 32, attached to each release.
- Works with Iris shader packs through vanilla light only (emissive faces, full-bright particles); see the Visuals page of the wiki.

### Game rules from the design

- Station automation: every station with recipes now works with hoppers. A station keeps one recipe, the last one crafted there by hand or the one picked with the new gilded funnel on its drawer. Ingredients go in from the top and the sides (each ingredient has its own slots, anything else is refused), the result comes out from below, and a comparator reads how full the station is. Each station keeps its condition: heat for the Ash Foundry, a charge for the Lightning Forge (lightning, or Storm Essence fed into its fuel slot), darkness, deep water, dawn and dusk; the Spore Vat waits for a ripe brew and the Jailer's Table makes one batch per lock pattern entered. The Soul Altar and the Class Table stay manual. Breaking a station drops its buffer.
- Shake a World Block on purpose: a player of the owning group outside can sneak and use it with empty hands to help those inside (creatures stunned and thrown off their feet for 3 seconds, a boss staggered and open), or strike it with the new Doll Mallet to hinder them (the world quakes and loose blocks fall over their heads). One shake per world every 30 seconds; other groups cannot.
- Rebuilding a Doll of Life layer at the Soul Altar now also costs 4 rare resources of the current world, as the design asks. The cost is shown under the button, with a tooltip listing the resources that count.
- Structure chests now keep souls: Soul Shards (5 souls) and Soul Vessels (20), about 10 souls per chest and 100 per world, a little more in the deeper worlds. Use them to free their souls (sneak for the whole stack); they do not move karma. Chests generated before keep their loot.
- Every quest checks what its description says. Deliveries are handed to the world's people (Hard Harvest, The Miners' Pay, A Life in a Day by day, A Warm Hearth); places are reached (Read the Plan, Last Message, The Impossible Stair, The Wreck's Crew, The Ground Plan, The Surveyor, Looking Down); stations are used (The Vat with a ripe brew, Under Control, Catch the Lightning, Double Meaning, Compress, The Workshop); kills ask for their condition (No Filter, Bare Hands, The Night Light, Lost Reflection, All at Once); and Read Between the Lines, Fingers in the Doll, First Flight, Light the Lighthouse, Hear the Danger, The Signs, The Silent Station, Four Seasons, The Archives, The Drifting Fort, The Apprentices and Every Tool watch the real action. Several descriptions say more precisely what to do. Many Hands only counts the peoples of the worlds.

### Comfort, cinematics and music

- Comfort options, opened from the Journal (Comfort button) and saved in `config/matriochka-client.json`: screen shake strength, flashes, soft effects (no Nausea or Darkness, a gentle tint instead; the server skips the effects for that player), cinematics, large boss attack subtitles, fewer particles, colour-blind gauge patterns, HUD plaque size and corner, and a volume per kind of music.
- Boss introductions: letterbox bars, the camera turning toward the boss with a slow push-in, and a framed title card with the boss's name and title.
- A title card the first time you enter each world, with its rule medallion and a line about its law.
- Boss phase breaks freeze-frame with a flash and the shell's number; heavy boss blows, World 9's moving ground, a moved World Block's quake and a trembling World Block nearby shake the camera.
- The endings' crawl is framed by letterbox bars.
- Adaptive music: a danger theme while creatures hunt you, the boss themes during fights, a heartbeat at low health or breath, and stings for a structure, a Journal page or a quest; themes fade into one another and the world theme comes back soon after.

### First steps, languages and compatibility

- First steps: until you enter World 1, a small lacquered card under the HUD plaque shows the next of ten steps (read the Scroll, find the Guardian's Sanctuary, wake and defeat the Guardian, place the Matrix Workbench, craft the World 1 Seed, till World Soil, plant it by water, wait for it to hatch, enter), with the step's item, a short hint and a compass needle toward the nearest sanctuary with its distance. Every step is detected from what you really do, a later step done first skips ahead, and progress is kept per player. Hide it or bring it back with the Guide button on the Scroll and on the Journal's Objective page.
- Matriochka is translated into Spanish, German and Brazilian Portuguese: every name, the interface, quests, achievements, the Scroll, the fifty Journal pages, endings, credits and subtitles. A string missing from a language shows in English.
- Button and ribbon labels shrink to fit when a language makes them longer.
- Mod Menu (optional): Matriochka's entry has its summary, links to the wiki, the Discord and the issues, and a small info screen with a Comfort button that opens the comfort options.
- Xaero's Minimap and World Map: their cave view and entity radar are turned off in the Lightless Deep (World 5), where they would show what the darkness hides, and back on when you leave.
- Checked with Sodium, Iris, Xaero's maps, JourneyMap, VoxelMap and Traveler's Backpack for 26.3: no conflict found, and no backpack way around the progression (see the Compatibility page).

### Balance, servers and modpack

- Balance pass, checked by the new `tools/balance.py` against the design's targets (report: [Balance](docs-wiki-drafts/Balance.md)):
  - Berserker weapons add 8% of their damage plus the whole bonus of their level (up to +58% at level 5, was at most +12%), so the reference creature again takes about 5 hits in World 10, as the design plans.
  - Bosses leave 3 Shell Shards instead of 2: enough to bring each world's weapon to the class cap.
  - Dungeon Rat 18 -> 22 health; Executioner 11.5 -> 10.1 damage; Sky Harpooner 59 -> 111 health and 8.6 -> 10.4 damage (it was weaker than the Island Warden); Unstable Sphere 19.9 -> 17.4, Earth Hand 34.4 -> 30.1 and Titan Ray 41.3 -> 36.1 damage (regular creatures that hit like elites).
- Server options in `config/matriochka.json`: `karma` (on or off), `soulGainMultiplier`, `maxActiveGroups` and `maxParcels`.
- The Matriochka Pack: a Modrinth modpack (`.mrpack`) with the mod, Fabric API, GeckoLib, Just Enough Items (optional) and client performance mods (Sodium, Lithium, FerriteCore, Entity Culling, ImmediatelyFast, Dynamic FPS, Krypton, Mod Menu, Iris as an option), in a normal and a hard (nightmare) version. Built by `tools/modpack.py` and attached to every GitHub release. See [Modpack](docs-wiki-drafts/Modpack.md).

### Tools and checks

- `tools/anim_preview.py` renders contact sheets of the boss animations (`docs-wiki-drafts/boss-anims/`).
- New check run: `./gradlew runClientGameTest -Pautomation`.
- A playthrough test (`./gradlew runClientGameTest -Pplaythrough`) plays the whole game in real ticks, from the Guardian through the ten worlds to World 0 and the third ending, and checks every step.

### Fixes

- World 2's Threshold and the Ash Titan's lair were placed above the build limit, over the rock roof, so nothing was built and travellers landed on the roof: they now stand on a cave floor under the roof, with a lit gallery to the lair, and a Threshold saved too high is rebuilt.
- Nesting two dolls no longer loses both: the Nested Dolls stay in your hand.
- A blow the Lantern Shield blocks completely now makes it flare.

## 0.3.0 (alpha)

The story is complete: the Artisan's Journal, the hidden dolls, World 0, three endings and the New Cycle. World 7 is now entirely under water, worlds 3, 5, 6, 9 and 10 have their full mechanics, and the mod has its own music and sounds. Trailer: [matriochka-trailer.mp4](https://github.com/achedon12/matriochka/releases/download/v0.3.0/matriochka-trailer.mp4).

- Matriochka has its own sounds and music, synthesized from seeded recipes (no recordings): a theme per world on Slavic folk modes (music box, balalaika and domra, gusli, wooden flute, bayan, bells, frame drum), played every few minutes in that world; a boss theme during every boss fight, fiercer below a third of the boss's health; and an endings' theme over the Scroll. The lullaby of World 0 comes back in World 10, the boss fight and the endings.
- Each world has its own ambience: a seamless loop and random sounds (jungle breath and insects, embers and hammers, chains and far doors, wind and thunder, breaths and footsteps in the dark, backwards chimes, drips and pressure groans, ticking clocks and a cuckoo, the ground's heartbeat and grinding rock).
- New sounds for the nesting dolls (open, close, click, rattle), the Doll of Life breaking, World Blocks forming, cracking and opening, a growing Seed, each of the 13 stations at work, the Jailer's pins, boss awakening, attack warnings per world, phase changes and defeat, and the World 4 gusts, World 6 gravity shifts and World 9 quakes. All have English and French subtitles. Creature attacks keep their vanilla sounds.
- Just Enough Items support (optional): every station has a recipe page with the station as catalyst, and recipes that open with a boss say which one.

- World 3: the halls really move. Every five minutes, 8 x 8 hall sections 16 to 40 blocks from each player swap places or turn, opening and closing passages; dust falls on them during the ten-second warning. Rooms, structures, locks, chests, stations, sealed doors and anything a player built never move, and no section next to a player does.
- World 5: the lights you bring burn out. A placed torch, lantern, candle, campfire or glowing block lasts one minute and smokes for its last five seconds: torches crumble to a stick, campfires and candles are snuffed (relight them), glowing blocks become the new Spent Glow, the rest falls back as an item. The Deep's own blocks keep glowing, and a lit Solar Lantern now carries a real light with you. The Darkness pulse only hits players standing in the dark.
- World 6: gravity changes by zone. The realm is cut into 32 x 32 columns and about a third of them are upside down, the pattern changing every 90 seconds: inside one, players, creatures and dropped items fall upward and stand on ceilings, up to 16 blocks above the ground. Purple sparks trace the borders. Gravity Boots, the Stabilizer and the Flipped Apple still protect you; Ceiling Walk and Vertigo come from the real thing.
- World 9: whole 16 x 16 zones move. Every minute up to three zones around each player rise, sink, slide or close their chasms, carrying players, creatures and builds along (My Base Walks) without ever burying anyone. Terrain Anchors (16 blocks), Anchors and Anchor Bread (4 blocks around you) and Grip Boots hold the ground still; zones with chests, stations or unbreakable blocks never move.
- Blocks placed by players are now remembered in worlds 3, 5, 9 and 10, so the moving worlds can protect, burn or carry them.
- World 7, the Pressure Ocean, is now entirely under water: the sea fills it from the floor up to y 240, with no dry land. The sea floor rolls around y 140, with reef crowns, rare trenches below y 20, caves and air pockets underneath, kelp forests, coral reefs and spires of glowing Pressure Coral.
- You arrive in a diving chamber on the sea floor: an air-filled glass dome around the Threshold, with a door that holds the water back, a chest of supplies and an Air Vent outside.
- Snorkel helmets: the only way to breathe for long under water. One per ore of the world (Abyssal Salt, and the new Nacre Vein, Abyssal Cobalt Ore and Pearl Bed), crafted at the Abyssal Press. They breathe for you from a tank that drains under water and refills in air pockets, in bubble columns, over Air Vents, with an Oxygen Capsule or with the press's new Refill button. They are fragile: hits wear them fast. Higher tiers hold more air, wear less and let you dive deeper.
- Without a helmet your breath lasts about half a minute under water. The HUD shows the helmet's tank in the oxygen vial and your breath as a thin line under it; the helmet's tooltip shows the air left.
- The Diving suit keeps its chestplate, leggings and boots (now made of Abyssal Cobalt): each piece lets you dive 22 blocks deeper. The helmet slot is the snorkel's.
- Every World 7 creature swims, never drowns and spawns in open water; the Bell Crab is now a sea creature too. Lantern Shoals and Glow Jellies, harmless wildlife, light the deep.
- World 7 structures stand on the sea floor instead of floating at the surface, and their dry refuges no longer spring leaks. The Pressure Leviathan sleeps in a temple at the bottom of a trench cut for it, reached by glowing coral posts.
- Divers live under water and sell a first helmet. Common World 7 chests sometimes hold a worn one.
- "Pressurized" now asks you to breathe through a snorkel helmet; "Last Breath" counts the helmet's tank.
- The Artisan's Journal is written: fifty pages in English and French, five per world (a site note, the portrait of the apprentice who became the boss, an observation, a coded page and a letter to the traveller), telling the story world by world. A new Pages tab of the Journal lists the pages found and reads them; the coded page of each world stays in the Artisan's cipher until you carry that world's core or your group beats its boss.
- The ten hidden dolls nest: hold the smallest in your main hand and the next one in the other hand, then use it. A doll that does not belong rattles and is refused. The order is hinted by the notches under each doll, the coded pages, the Carver's Note left beside every hidden doll and what each world's people say when you show them their doll. The ten closed together make the Whole Matryoshka.
- World 0, the smallest doll, opens with the Whole Matryoshka once the Unfinished has fallen: a sealed place of painted wood with three chambers of elite guards from every prison and the Artisan's own room. Its rule, Obsession, feeds on every tool you hold and every blow you strike; only empty hands calm it. Its encounter cannot be won by fighting.
- Three endings. After the Unfinished, your karma decides: Sealed (two more hearts) or Absorbed (stronger strikes, but your karma can never rise again). World 0 holds the third, Set Down the Tools, and the Blank Scroll. Each ending plays a crawl on the Scroll, then the credits, and has its advancement in a new Endings tab. The hidden achievement Set Down the Tools now belongs to the third ending.
- New Cycle: after an ending, the Journal can begin the next cycle. Your group starts over from the Guardian in fresh worlds where creatures and bosses have 50% more health and 25% more damage per cycle. You keep your souls, karma, pages, quests, endings and gear; the cores, Seeds, World Soils, offerings and keys of the old cycle are taken back, and its World Blocks crumble.
- New commands for operators: `/matriochka world zero`, `/matriochka ending <seal|absorb|tools>`, `/matriochka cycle show|begin`.
- The Refuge Doll: every player who fights the Grand Jailer gets a pocket base for the group, a lacquered room that grows after worlds 5, 7 and 9 and stays shut while a boss is awake nearby.
- Layered armor: Lacquer Layers from the Lightning Forge are laid on armor at the Class Table; when the outer layer breaks the next takes over. The class decides how many a piece holds.
- Nesting chests come in three sizes; each holds the smaller ones with their contents, keeps everything when broken, and sorts items into the smaller chests by type.
- The Drill mines 3x3 squares and burns Blazing Rock.
- The Lightning Forge takes Storm Essence as a charge, Spore Vat brews give more when ripe or aged, and the Inverter swaps the class, level and enchantments of two pieces at a cost.
- Karma reaches the Surface: villager prices, refusals and reactions follow it, and killing an innocent costs karma. Black markets open from karma -25, and a Karma Paths chapter adds three mutual-help and three pact quests.
- Reaper gear harvests extra souls, Prowler gear dodges blows, and class upgrades also need Shell Shards, left by every boss.
- Bosses attack faster with more players, and the newest world's gear asks to have taken part in its last boss fight.
- Group leaders can kick, hand over the lead and disband; administrators can list, repair, move and reset worlds and reset bosses.
- Villager trades involving diamonds wait until World 5.
- Difficulty modes: story keeps the inventory on death; hardcore makes death permanent and a broken World Block deletes its world.
- World variants: a Seed now hatches into a variant of its world. Feeding the planted Seed (flowers, honey, berries, moss lean it calm; gunpowder, blaze powder, rotten flesh, bones, spider eyes, magma cream lean it wild) and the blocks within 3 of it decide; at karma +100 the world is Hallowed, at -100 Cursed. Calm worlds have fewer, weaker creatures and a gentler rule; wild and cursed ones more and stronger creatures, a harsher rule and richer drops. Each world names its calm and wild variants; the Journal's Worlds tab marks them with a seal and explains them on hover. Only the planter's group can feed its Seed.
- Boss mutations: from World 6, the boss of a wild, hallowed or cursed world wakes mutated (Searing, Frenzied, Echoing, Radiant or Hollow), named in its boss bar. A mutated boss drops a Mutated Scale and two more Shell Shards.
- Effects between the scales: a World Block now leaks its world within 8 blocks (spores and growth, heat for furnaces and sparks, slammed doors, gusts and charged lightning rods, snuffed candles, floating items, soaked farmland, hastened crops and spoiled food, cracking stone) and shakes while a boss fight rages inside. In return, water, ice, redstone, storms, lights, dry ground or Terrain Anchors around it soften or strengthen the rule inside, and moving a World Block makes its world quake.
- Every World Block shows a small turning island of its world above it, tinted by its variant.
- World 10 at doll scale: giant spools, nails, pins, buttons, thimbles, scissors, pencils and wood offcuts lie on the workshop floor, and the Titanic Workbench is now a towering bench whose top holds the Maquette: a quarter-scale model of your base, captured when the World 10 Seed hatches and built with real blocks on your first visit.

## 0.2.0 (alpha)

- Every creature now has its own signature attacks: 160 in all, three per creature and four per elite, none shared. Each has its own wind-up animation, numbers, afflictions, particles and sound, drawn from what the creature is.
- Two ways to meet a boss. The Grand Jailer, the Storm King, the Master of Seasons and the Unfinished are woken at the arena altar with an offering crafted at their world's station (Sealed Shackle, Storm Censer, Wreath of Seasons, Unfinished Effigy), through a three-second ritual; every fight costs one offering. The six other bosses sleep in their own lairs (a hive, a forge-hall, a lightless pit, a hall of mirrors, a sunken trench temple and a cavern of living rock), woken by the lair heart and guarding a treasure alcove that opens when they fall.
- The altar arena is rebuilt with an inlaid floor, a colonnade, braziers and an entrance arch.
- The eleven bosses are rebuilt as full rigs with joints, secondary motion and glowing eyes and cores.
- Texture generation is reproducible; the build no longer needs a local copy of Minecraft data.
- New releases are announced automatically in the Discord changelog channel.
- Every achievement can now be earned. The boss challenges ("beat the Queen without a mask", "the Titan without touching lava"...) are tracked over the whole fight; Forgotten Plate, A Crumb and Set Down the Tools have new conditions that exist in the game.
- Every world offers its five Journal pages: the exploration structures hold pages 1 to 3, the story structures pages 4 and 5.
- The ten world dishes now give their effects.
- The Grappling Hook pulls creatures toward you.
- The Doll Peddler wanders the Surface like a trader.
- Once unmasked, Mimics and Crawling Blocks chase you. The Dusk Shade only comes out at dusk.
- A broken world stays unstable for 20 minutes, with more creatures around.
- Only its group can break a World Block or a Soul Cradle; a group has one World Block per world; a cradle stays shut while a boss is awake near it.
- The config is applied: creature health and damage multipliers, group size, and four difficulty modes (story, normal, nightmare, hardcore).
- No more diamonds in vanilla loot chests.
- A day in World 8 lasts 8 minutes, as designed.

## 0.1.0 (alpha)

First public alpha for Minecraft 26.3 (Fabric).

- Ten nested worlds, each in its own dimension with its own terrain, biome, sky and rule.
- World Soil, Seeds with hatching conditions, World Blocks, Thresholds, Return Threads and Cracked Dolls.
- 50 creatures and 11 bosses with GeckoLib models and animations.
- Boss attack system with telegraphs, openings, phases and multiplayer scaling.
- 13 stations with their own mechanics and recipes.
- Equipment classes, Class Table and Chance Doll.
- Souls, karma, Soul Altar and karma-aware merchants for every world.
- Doll of Life, Soul Cradle and death chests.
- 100 procedural structures, journal pages and hidden dolls.
- 64 optional quests and 100 achievements.
- Progression gates for diamonds, enchanting, the Nether, the End, elytra and beds.
- English and French translations.
