# Visuals

Matriochka paints all of its art in code, so it stays consistent and can be regenerated at any size. This page covers the hand-painted textures, the light and fog of every world, the particles, the optional HD pack and shader packs.

## Hand-painted textures

The items and blocks you look at most are drawn by `tools/craft.py` in the vanilla style: a dark outline taken from the colour it closes, three or four tones lit from the top left, shadows that lean toward violet-blue and highlights that lean toward warm yellow, and a few highlights where the form faces the light.

Each world has its palette, and its objects share it: a lacquer body, a painted second colour, a light colour and a small glyph.

| World | Palette | Glyph |
| --- | --- | --- |
| Surface | Red lacquer, gold leaf | A bouquet of berries |
| 1 | Jungle green, toxic violet, acid green | A toadstool |
| 2 | Charcoal, molten orange | A flame |
| 3 | Slate, steel, cold blue | A keyhole plate |
| 4 | Sky blue, cloud white, storm yellow | A lightning bolt |
| 5 | Midnight, black, deep blue | An open eye |
| 6 | Magenta, teal, pearl white | Two mirrored triangles |
| 7 | Deep sea, turquoise, foam | Bubbles over a wave |
| 8 | Ochre, burnt orange, frost | A leaf |
| 9 | Rust, clay, ember | A heart of stone |
| 10 | Workshop red, thread blue, gold | A thread spool |
| 0 | Dark red lacquer, gold, ivory | The Artisan's star |

What is hand-painted:

- **The dolls**: the ten hidden dolls (each in its world's lacquer and glyph, and taller the further out it sits in the nest), the Nested Dolls (an opened doll with the next one inside), the Whole Matryoshka, the Life, Chance, Cracked and Refuge Dolls.
- **The eleven cores**: a lacquered shell in the world's colour, caged in gold, its heart glowing through a window.
- **The ways into the worlds**: the World 1 Seed, a lacquered kernel with the world's painted bands, set in a gold cup, sprouting; and the nine rite objects in their worlds' palettes (an ember heart, the Jailer's key, a storm rod, a black lantern, twin mirrors, an abyssal pearl, a sapling of the four seasons, a seismic stake and a traveller's matryoshka). A rite site set down in the world is drawn as its object.
- **The gear**: every armor piece of the ten sets, with its own detail (chitin plates, glowing thermal seams, jailer rivets, a celestial star, nocturnal glints, a mirror band, diving portholes, season leaves, living rock cracks, artisan gold), and the ten world weapons.
- **The four snorkel helmets**: salt, nacre, cobalt and pearl.
- **Writings and offerings**: the Artisan's Scroll, the Blank Scroll, the Journal, the Journal Page, the Sealed Shackle, the Storm Censer, the Wreath of Seasons and the Unfinished Effigy.
- **Blocks**: the ten World Soils and their tilled tops, the World Block and the Threshold.
- **The thirteen stations** are sculpted 3D models with fitted shapes, not cubes: they face the player who places them and have moving parts (the matrix over the workbench, the rank medal, the soul wisps, the vat's bubbles, the jailer's key, the forge's arc, the dark crystal, the inverter's ring, the press ram, the pendulum and clock hands, the anchor's stones, the loom shuttle). The HD pack gives them 32 x 32 materials.

Preview sheets, upscaled with a vanilla item for scale, are in [`docs-wiki-drafts/textures/`](textures/): `python3 tools/texsheets.py` rebuilds them.

## Glowing faces

The lit parts of the stations (the vat's brew, the foundry's fire, the forge's bolt, the dark altar's eye, the press's gauge, the anchor's cracks, the jailer's keyhole, the soul altar's flame) and the Threshold's doorway sit on an emissive overlay, the way vanilla draws the firefly bush and the eyeblossom: they stay bright in the dark.

## Light, fog and particles of each world

Every world sets its own fog, sky, clouds, light tint and floating particles (`tools/atmosphere.py`):

| World | Atmosphere |
| --- | --- |
| 1 | Spore haze: green-gold fog closing in at 90 blocks, filtered green sunlight, spores drifting everywhere |
| 2 | Heat: orange haze, hot light, embers and ash falling |
| 3 | Cold stone: blue-grey fog, white-blue lamplight, cold dust settling, the odd glint of a chain |
| 4 | Storm sky: slate sky, low dark clouds, grey-blue light, sparks crackling in the air |
| 5 | Near black: the fog swallows everything past 18 blocks, lights look cold, rare motes and shadow wisps |
| 6 | Inverted pastel: a mint sky over pink fog, lilac clouds, mirror shards falling upward |
| 7 | Deep blue water fog closing in at 40 blocks, bubbles rising everywhere |
| 8 | The light changes with the season every two minutes: pink with petals in spring, golden with pollen in summer, amber with falling leaves in autumn, blue with snow in winter |
| 9 | Rust haze: red-brown dust in the air, grit falling off the moving ground |
| 10 | Warm workshop light, honey haze, wool fluff and thread scraps floating down |
| 0 | Lantern light on red lacquer, gold dust in the air |

## Skies

The open worlds have skies of their own, as their own day and moon timelines (`tools/atmosphere.py`, `SKY`): a moon that stays dark behind the spores (World 1), a full moon and no stars through the storm (World 4), an upside-down sky where the sun and moon trade places and the stars come out by day (World 6), a bright starry sky over the sea (World 7), no stars under the Workshop's ceiling (World 10).

## Particles

Eighteen particles of the mod's own, painted like the textures: spores, embers, cold dust, chain glints, lightning sparks, shadow wisps, deep motes, mirror shards, bubbles, petals, pollen, autumn leaves, snowflakes, grit, rust motes, thread scraps, fluff and gold dust. The glowing ones are drawn at full brightness.

They float in the worlds, mark where a boss attack will land, burst when it lands (World 8's follow the season), and many creature attacks use them (the Sporeling's nip, the Dead Smith's sparks, the Jailer's shackle, the Storm Bird's static, the Broken Mirror's splinters, the Walking Column's rubble...).

## Matriochka HD

An optional resource pack with the same hand-painted textures at twice the size: 32 x 32 items and blocks, 16 x 16 particles. Download `matriochka-hd-<version>.zip` from the release, put it in `resourcepacks` and enable it above the mod. To build it yourself: `python3 tools/hdpack.py` writes `build/matriochka-hd-<version>.zip`.

## Shader packs

Iris exists for 26.3 (Iris 1.11.7 for Fabric 26.3, which needs Sodium). Matriochka adds no shader code of its own and uses only vanilla mechanisms for light, so it works with shader packs:

- the glowing station faces and the Threshold use vanilla emissive model elements (`light_emission`), which Iris and shader packs read as block light;
- glowing particles use the full-brightness light value, as the vanilla end rod and glow particles do;
- the glow of the creatures and bosses goes through GeckoLib's glow layer (how it looks depends on GeckoLib's own Iris support);
- fog, sky and light come from the world's environment attributes, which shader packs may replace with their own sky and fog.

Shader packs that tag emissive blocks by name (`block.properties`) do not know the mod's blocks, so those blocks glow by their light level and emissive faces only. This has not been tested in game with every shader pack.

## Checking it in game

`./gradlew runClientGameTest -Pvisuals` enters every world and photographs its atmosphere (and World 8 in each season), places the stations by day and by night, hangs the painted items on an item frame wall and in the inventory, and sprays every new particle. The shots land in `run/screenshots` as `vis_*.png`.
