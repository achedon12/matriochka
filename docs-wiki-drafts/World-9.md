# World 9: Restless Ground

The terrain itself is hostile: it moves, it closes, and it carries away whatever is not anchored.

## Rule: the shifting zones

The ground is made of **zones of 16 x 16 blocks** (one chunk each). Every **60 seconds** it heaves.

- **3 seconds before**: *"The ground is about to move."*, the ground cracks and puffs dust around you, and the tremor gauge fills up.
- At the heave, up to **three zones** within two zones of you move, whole, from a few blocks under their lowest surface up to their highest block:
  - **rise** by 1 to 3 blocks;
  - **sink** by 1 to 3 blocks;
  - **slide** 1 or 2 blocks east, west, north or south (what slides out of one edge comes back on the other, so nothing is lost);
  - **close**: the chasms of the zone fill up with rock to its usual level.
- Zones that stand high tend to sink and low ones to rise, so the land shifts without drifting away.
- **Everything on a moving zone rides it**: you, the creatures, the items, and the blocks you placed. You are never crushed: anyone overlapping the ground after a move is lifted to the nearest free spot. Riders feel a short nausea: *"The ground carries you along."*
- When a build of yours rides the ground, you earn **My Base Walks**.

## What holds the ground

- **Terrain Anchor** (station): no zone within **16 blocks** of it ever moves. Build around one.
- **Anchor** (consumable): for **10 minutes**, the zone under you, and any zone within **4 blocks** of you, stays still.
- **Grip Boots**: while you wear them, the zone under you stays still.
- **Anchor Bread**: 5 minutes of steady footing, like an Anchor.
- Zones holding a chest, a station or any block entity, an unbreakable block, a boss, the Threshold or the boss stage never move. Very steep zones (more than 96 blocks of relief) stay put too.

When you are anchored at the heave: *"Your anchor holds the ground still."*

## Numbers

| | |
| --- | --- |
| 60 s | between two heaves |
| 3 s | of warning |
| 16 x 16 | blocks per zone |
| 3 | zones moved around each player per heave |
| 1 to 3 | blocks of rise or sink, 1 to 2 of slide |
| 16 | blocks of calm around a Terrain Anchor |
| 4 | blocks of calm around an anchored player |

## Site copy (for `tools/site.py`, RULE_LONG and RULE_NUMS)

EN: Every 60 seconds the ground heaves: around you, up to three 16 x 16 zones rise, sink, slide sideways or close their chasms, and everything on them rides along, you and your builds included. You get three seconds of warning and are never buried. Within 16 blocks of a Terrain Anchor nothing moves; an Anchor holds the ground within 4 blocks of you for ten minutes, and Grip Boots hold the zone under your feet.

FR : Toutes les 60 secondes, le sol se soulève : autour de toi, jusqu'à trois zones de 16 x 16 montent, s'enfoncent, glissent de côté ou referment leurs gouffres, et tout ce qui s'y trouve suit le mouvement, toi et tes constructions compris. Tu as trois secondes de préavis et tu n'es jamais enseveli. À moins de 16 blocs d'une Ancre de terrain, rien ne bouge ; une Ancre retient le sol à moins de 4 blocs de toi pendant dix minutes, et les Bottes d'accroche retiennent la zone sous tes pieds.

Numbers: `60 s` between two heaves / entre deux secousses; `16` blocks of calm around a Terrain Anchor / blocs de calme autour d'une Ancre de terrain; `16 x 16` blocks per moving zone / blocs par zone qui bouge.
