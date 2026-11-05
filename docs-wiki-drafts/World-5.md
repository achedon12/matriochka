# World 5: Lightless Deep

No light, and a noise gauge. Every light you bring here dies.

## Rule: the lights burn out

Any light **you place** in World 5 lasts **one minute**.

- For its **last 5 seconds** it smokes and gutters: that is your warning.
- Then it dies:
  - **torches** (normal, soul, copper) crumble into a **stick**;
  - **campfires and candles** are snuffed. Relight them and the minute starts again;
  - **glowing blocks** (glowstone, sea lanterns, shroomlights, froglights, jack o'lanterns, the glowing blocks of other worlds) turn into **Spent Glow**;
  - **anything else that shines** (lanterns, end rods, sea pickles...) falls back as an item.
- The first time it happens, the chat reminds you: *"A light you brought gutters out. Here only the Solar Lantern and the Deep's own glow last."*

What lasts:

- **The Deep's own light**: Faint Glow and every World 5 block never burn out, even when you place them yourself. Mine Faint Glow and carry it.
- **The Solar Lantern**: lit, it gives 20 minutes of light that moves with you (a light level 14 glow at your eyes) and keeps the darkness from your sight.
- Lights the world built itself (in structures) are not yours and keep burning.
- Redstone (torches, lamps, ores, anything powered) and block entities such as furnaces are not touched.

## The dark and the noise

- When you stand in the dark (block light under 4) without a lit Solar Lantern or night vision, Darkness washes over your sight every ten seconds.
- The noise gauge is unchanged: sprinting adds 4 per second, walking 0.6; standing still removes 1.5, sneaking 3. Above 50, every creature within 28 blocks comes for you. Silence Balm wipes it, the Mute Mushroom slows it.

## Numbers

| | |
| --- | --- |
| 60 s | how long a brought light lasts |
| 5 s | of smoke before it dies |
| 20 min | of moving light from a Solar Lantern |
| 4 | block light under which the darkness presses on you |
| 50 | noise, and everything comes for you |

## Site copy (for `tools/site.py`, RULE_LONG and RULE_NUMS)

EN: No light, and a noise gauge. Every light you place burns out after a minute: torches crumble to sticks, campfires and candles are snuffed, glowing blocks turn to Spent Glow. Only the Deep's own Faint Glow lasts, and a lit Solar Lantern carries twenty minutes of light with you. Sprinting adds 4 noise per second, walking 0.6; standing still removes 1.5, sneaking 3. Above 50, every creature within 28 blocks comes for you. Silence Balm wipes your noise.

FR : Aucune lumière, et une jauge de bruit. Chaque lumière que tu poses s'éteint au bout d'une minute : les torches tombent en bâtons, les feux de camp et les bougies s'étouffent, les blocs lumineux deviennent de la Lueur éteinte. Seule la Lueur faible des profondeurs dure, et une Lanterne solaire allumée emporte vingt minutes de lumière avec toi. Courir ajoute 4 de bruit par seconde, marcher 0,6 ; rester immobile retire 1,5, s'accroupir 3. Au-dessus de 50, toutes les créatures à moins de 28 blocs viennent te chercher. Le Baume de silence efface ton bruit.

Numbers: `60 s` before a brought light burns out / avant qu'une lumière apportée s'éteigne; `50` noise, and everything comes for you / de bruit, et tout vient te chercher; `20 min` of light carried by the Solar Lantern / de lumière portée par la Lanterne solaire.
