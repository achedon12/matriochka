# World 6: Upside Realm

Up, down and falls are no longer reliable.

## Rule: the flipped columns

The realm is cut into columns of **32 x 32 blocks**. At any time about **a third** of them are **flipped**, and every **90 seconds** the pattern changes.

- **Inside a flipped column gravity points up.** You, the creatures and the items on the ground fall toward the sky.
- Under an overhang, in a cave or below a bridge, you land on the **ceiling** and walk on it. Jumping pushes you away from it, downward.
- In the open, the pull reaches **16 blocks above the column's ground**. Past that height it fades and you hang there, bobbing, until you leave the column or it turns back.
- **Purple sparks** draw curtains along the borders between flipped and normal columns around you; inside a flipped column, white motes drift upward.
- **5 seconds before** the pattern changes: *"Gravity is about to flip."*
- When the column you were falling up in turns back, you drift down slowly for 12 seconds. Walk off a ceiling into a normal column, though, and you simply fall.
- The 48 blocks around the Threshold and the boss stage are never flipped.

## Protection

- **Gravity Boots**: your gravity never flips.
- **Stabilizer**: 30 seconds of normal gravity.
- **Flipped Apple**: 30 seconds of normal gravity.

## Achievements

- **Ceiling Walk**: be caught by a flipped column.
- **Vertigo** (hidden): fall upward for 10 seconds without touching anything.

## Numbers

| | |
| --- | --- |
| 32 x 32 | blocks per gravity column |
| about 1 in 3 | columns flipped at a time |
| 90 s | between two changes of the pattern |
| 5 s | of warning |
| 16 | blocks above the ground: how high a flipped column pulls |
| 12 s | of slow fall when your column turns back |

## Site copy (for `tools/site.py`, RULE_LONG and RULE_NUMS)

EN: The realm is cut into 32 x 32 columns, and about a third of them are upside down. Inside one, gravity points up: you, the creatures and the items fall toward the sky and walk on ceilings, up to 16 blocks above the ground. Purple sparks trace the borders. Every 90 seconds the pattern changes, five seconds after a warning; if your column turns back you drift down slowly. Gravity Boots ignore the flips entirely; a Stabilizer or a Flipped Apple keeps you steady for 30 seconds.

FR : Le royaume est découpé en colonnes de 32 x 32, et environ un tiers d'entre elles sont à l'envers. À l'intérieur, la gravité pointe vers le haut : toi, les créatures et les objets tombez vers le ciel et marchez au plafond, jusqu'à 16 blocs au-dessus du sol. Des étincelles violettes dessinent les frontières. Toutes les 90 secondes, la carte change, cinq secondes après un avertissement ; si ta colonne se retourne, tu redescends lentement. Les Bottes de gravité ignorent les inversions ; un Stabilisateur ou une Pomme retournée te gardent stable 30 secondes.

Numbers: `90 s` between two changes of the gravity columns / entre deux changements des colonnes de gravité; `32` blocks per column / blocs par colonne; `16` blocks: how high a flipped column pulls / blocs : la hauteur où tire une colonne inversée.
