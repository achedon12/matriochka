# Image slots for the store descriptions

The store texts (`curseforge_mod.md`, `modrinth_mod.md`) use bare placeholders as image URLs: `![...](POSTER)`.
Upload each file to the store's image gallery (CurseForge: Images tab; Modrinth: Gallery), copy its URL and replace
the placeholder. CurseForge only takes full URLs in the description; Modrinth gallery URLs work the same way.
Convert `.webp` to `.png` or `.jpg` before uploading to CurseForge, to be safe.

Status: OK = current for 0.9.0. OLD = shows the pre-0.9.0 interface (plaque, Comfort button). TODO = capture needed.

| Slot | Suggested local file | Size | Status / note |
| --- | --- | --- | --- |
| POSTER | `media/poster/out/matriochka_poster_3840x2160.jpg` | 3840x2160 | TODO: not generated yet (`media/poster/compose.py`). Fallback: `site/public/shots/hero_banner.webp` (1920x823) |
| BANNER | `media/poster/out/matriochka_banner_1920x480.jpg` | 1920x480 | TODO: not generated yet. Not used in the description body; it is the page header. Fallback: `site/public/shots/hero_banner.webp` |
| WORLD_01 | `site/public/shots/w01_view.webp` | 960x720 | OK. Jungle with the Gatherer village |
| WORLD_02 | `branding/modpack/gallery/04-giant-veins.jpg` | 1920x1080 | OK. Better than `w02_view.webp` (flat lava floor) |
| WORLD_03 | `site/public/shots/w03_view.webp` | 960x720 | OK. Lit hall with ice blocks |
| WORLD_04 | `site/public/shots/w04_view.webp` | 960x720 | OK. Floating islands |
| WORLD_05 | `branding/modpack/gallery/03-light-eater.jpg` | 1920x1080 | OK. The Light Eater; `w05_view.webp` is only blue fog, `wiki/images/visuals/world_5.jpg` is near black |
| WORLD_06 | `site/public/shots/w06_view.webp` | 960x720 | OK |
| WORLD_07 | `site/public/shots/w07_view.webp` | 960x720 | OK. Alternative: `media/gallery/wonder_sunken_bell.jpg` (1600x900) |
| WORLD_08 | `site/public/shots/w08_view.webp` | 960x720 | OK. Alternative: `wiki/images/visuals/world_8_season_1.jpg` to `_3.jpg` |
| WORLD_09 | `site/public/shots/w09_view.webp` | 960x720 | OK |
| WORLD_10 | `site/public/shots/w10_view.webp` | 960x720 | OK. Alternative: `branding/modpack/gallery/02-workshop-creatures.jpg` |
| BOSS | `branding/modpack/gallery/01-the-unfinished.jpg` | 1920x1080 | OK. Alternatives: `wiki/images/boss-moves/*_windup.jpg` (a tell before the strike) |
| JOURNAL | `media/gallery/journal_card.jpg` | 1600x900 | OK. World 1's card, recaptured for 0.9.0 (no Comfort button). Also `wiki/images/screens/journal-map.jpg` |
| WONDER | `media/gallery/wonder_mother_tree.jpg` | 1600x900 | OK. Others: `wonder_molten_heart.jpg`, `wonder_hall_of_keys.jpg`, `wiki/images/wonders/*.jpg` |
| CRADLE | `wiki/images/matriarch/ritual_nest.webp` | 1280x720 | OK. Others: `cradle.webp`, `ritual_flash.webp`, `ritual_ingot.webp` |
| ARMOUR | `wiki/images/matriarch/armour_front.webp` | 1280x720 | OK. Others: `armour_back.webp`, `nested_shell.webp`, `armour_tooltip.webp` |
| COMFORT | `wiki/images/comfort/options_screen.webp` | 1280x720 | OK. The 0.9.0 screen opened from Options > Matriochka... Also `wiki/images/comfort/options.jpg` (960x540), `site/public/shots/sys_comfort.webp` (the book alone) and `options_menu.webp` (the Options screen with its Matriochka... button) |

Extra gallery images worth uploading (store galleries, not the description body):

- `site/public/shots/sys_cradle_ritual.webp`, `sys_matriarch_armour.webp`, `sys_souls_bar.webp`, `sys_options.webp`, `sys_options_comfort.webp` (960x540): the 0.9.0 features in one size.

- `wiki/images/matriarch/souls_bar.webp` and `world_title.webp`: the 0.9.0 HUD (souls bar, world title on entry). `branding/modpack/gallery/05-hud.jpg` now shows the same HUD.
- `wiki/images/matriarch/ores.webp`, `matriochkite_block.webp`.
- `wiki/images/boss-moves/<boss>_<attack>_windup.jpg` and `_strike.jpg`: the readable attacks, in pairs.

All the captures that showed the plaque or the Journal's Comfort button were redone for 0.9.0: `wiki/images/comfort/*.jpg`, `wiki/images/screens/journal-*.jpg`, `wiki/images/matriarch/journal_chain.webp`, `site/public/shots/gui_hud_w*.webp`, `gui_journal_*`, `sys_comfort.webp`, `sys_world_card.webp`, `sys_boss_intro.webp`, and the pack's `05-hud.jpg` and `06-journal.jpg`.

## GitHub README

`github_readme_top.md` uses repository paths: `branding/logo-256.png` (the new logo, same file as the mod icon),
`site/public/shots/w0N_view.webp` (tracked), and `branding/poster.jpg`, which does not exist yet: copy the poster
there at 1920 wide (`media/` and `media/poster/out/` are not tracked). `wiki/` is not part of the repository, so the
0.9.0 shots are linked through `https://raw.githubusercontent.com/wiki/achedon12/matriochka/images/...`.

## Store avatars

- Mod: `branding/icon-square-1024.png` (or `branding/logo-512.png` on a transparent background).
- Pack: `branding/modpack/icon.png` (512, the doll in a ring of the ten worlds' gems, from `tools/logo_v2.py`).
- Discord server: `branding/discord-avatar-256.png`.
