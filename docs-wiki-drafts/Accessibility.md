# Accessibility and Comfort

Every screen effect of Matriochka can be softened or turned off. Open the **Artisan's Journal** and press **Comfort** at the foot of the left page, or, with Mod Menu, use Matriochka's configure button and press **Comfort** (it works from the title screen too). The options are saved at once, per player, in `config/matriochka-client.json`; hover a line to read what it does.

## Screen

| Option | Default | What it changes |
| --- | --- | --- |
| Screen shake | 100% | How much heavy boss blows, phase breaks, World 9 quakes, a moved World Block and a trembling World Block nearby shake the camera. 0% turns every shake off. |
| Flashes | On | The white flash of a boss phase break and the red glow at the screen's edge before a signature attack. Off, a soft darkening of the edges stands in for both. |
| Soft effects | Off | You never get Nausea or Darkness, whatever gives them (World 5's pulses, World 9's moving ground, creature and boss attacks, vanilla sources too). A gentle tint shows how long they would have lasted: a slow green and violet haze for Nausea, a steady dimming without pulses for Darkness. The option is sent to the server when you join and when you change it. Blindness and the other effects are unchanged. |
| Cinematics | On | Boss introductions, the title card of a world entered for the first time, and the phase freeze-frame. |
| Attack subtitles | On | While a boss winds up an attack, its name in large letters on a lacquer cartouche, red for a signature attack, with a gilt line that shrinks until it lands. |
| Fewer particles | Off | Two particles out of three sent by the server are skipped inside the worlds and during boss fights. The game's own Particles setting still applies on top. |
| Gauge patterns | Off | The icons of the world's rule meter (the row above the hunger bar) also carry a pattern: diagonal stripes past half, crosshatching in danger, so the level reads without the colours. In danger the icons also shake, whatever the option. |

## HUD and music

| Option | Default | What it changes |
| --- | --- | --- |
| Plaque size | x1 | The HUD plaque (world and rule, Doll of Life, souls) from x0.5 to x2, in steps of a quarter. The rule meter above the hunger bar follows the game's GUI scale, like the vanilla rows. |
| Plaque corner | Top left | Top left, top right, bottom left (above the chat) or bottom right. |
| World themes | 100% | The world themes while exploring. |
| Danger | 100% | The tense theme that takes over while creatures hunt you. |
| Boss fights | 100% | The boss themes. |
| Heartbeat | 100% | The heartbeat that rises with low health or low breath. |
| Stings | 100% | The short phrases for a place found, a Journal page or a quest done. |

Every music volume is a share of the game's own Music slider.

## Cinematics

- **Boss introduction.** When a boss wakes, bars slide in at the top and bottom, the camera turns toward the boss and pushes in slowly, and a framed title card names it: the world's enamel plate, the boss's name in gold and its title beneath. About four seconds; the fight does not wait for it.
- **World title card.** The first time you enter each world: its rule medallion turns in above a card with the world's name and a line about its law.
- **Phase break.** When a boss breaks into its next shell: a freeze-frame flash, a short punch of the camera and the shell's number.
- **Endings.** The Scroll's crawl is framed by letterbox bars and darkened edges.

Turning Cinematics off keeps the subtitles, the shakes (as set) and the flashes (as set).

## The file

```json
{
  "shake": 100,
  "flashes": true,
  "softEffects": false,
  "cinematics": true,
  "subtitles": true,
  "reducedParticles": false,
  "patterns": false,
  "hudScale": 1.0,
  "hudCorner": "top_left",
  "musicExplore": 100,
  "musicDanger": 100,
  "musicBoss": 100,
  "musicLayers": 100,
  "musicStings": 100
}
```

Values out of range are brought back in range when the file is read.
