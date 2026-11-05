# Translations

Matriochka is played in five languages. Every game string is translated: item, block and creature names, the interface, quests, achievements, the Scroll and the fifty Journal pages, endings, credits and sound subtitles.

| Language | Minecraft code | Source |
| --- | --- | --- |
| English | `en_us` | `tools/content.py`, `tools/ui_lang.py` |
| French | `fr_fr` | `tools/content.py`, `tools/ui_lang.py` |
| Spanish (Spain) | `es_es` | `tools/i18n/es_es.json` |
| German | `de_de` | `tools/i18n/de_de.json` |
| Portuguese (Brazil) | `pt_br` | `tools/i18n/pt_br.json` |

Select the language in Minecraft's own Language screen. Any string a language does not have yet shows in English: Minecraft always loads English under the selected language.

## How it is built

English and French sit side by side in the content tables (`content.py`) and the interface table (`ui_lang.py`). Every other language is a plain JSON table in `tools/i18n/<code>.json`, mapping a lang key to its translation. `python3 tools/gen.py` writes `src/main/resources/assets/matriochka/lang/<code>.json` from it and checks each entry against English:

- a key that no longer exists in English is left out (renamed or removed content never ships a dead string);
- a translation whose placeholders (`%s`, `%d`, `%1$s`) differ in number from the English one is left out and reported, so a broken format can never break a tooltip; it falls back to English;
- a missing key is left out and falls back to English.

The line `translations: es_es=1702/1702 de_de=... pt_br=...` at the end of `gen.py` shows the coverage.

## Adding or fixing a translation

1. Run `python3 tools/translations.py` to see the coverage of every language, or `python3 tools/translations.py es_es` to get the missing (and dropped) keys of one language as JSON, with their English and French text.
2. Add the keys to `tools/i18n/<code>.json` (sorted keys, UTF-8).
3. Run `python3 tools/ui_lang.py` (only if you changed interface strings) then `python3 tools/gen.py`, and check the report.

Keep the placeholders, the `\n` line breaks and the `§` codes as they are. The Scroll, the Journal pages and the endings are letters from the Artisan: they use the familiar form (`tú`, `du`, `você`), like the French `tu`. Keep item and creature names identical everywhere they are mentioned.

## A new language

Add its Minecraft code to `LANGS` in `tools/translations.py`, create `tools/i18n/<code>.json`, and regenerate. Open an issue first so we can help with the names.

## Glossary

| English | Español | Deutsch | Português (BR) |
| --- | --- | --- | --- |
| Artisan's Scroll | Pergamino del Artesano | Schriftrolle des Handwerkers | Pergaminho do Artesão |
| Artisan's Journal | Diario del Artesano | Tagebuch des Handwerkers | Diário do Artesão |
| World Block | Bloque-mundo | Weltblock | Bloco-mundo |
| World Soil 0 | Suelo-mundo 0 | Welterde 0 | Terra de mundo 0 |
| World 1 Seed | Semilla del Mundo 1 | Samen von Welt 1 | Semente do mundo 1 |
| Matrix Workbench | Mesa matriz | Matrix-Werkbank | Bancada matricial |
| Refuge Doll | Muñeca refugio | Zufluchtspuppe | Boneca-refúgio |
| Soul Cradle | Cuna de almas | Seelenwiege | Berço de almas |
| Block Guardian | Guardián del Bloque | Blockwächter | Guardião do Bloco |
| Guardian Sanctuary | Santuario del Guardián | Heiligtum des Wächters | Santuário do Guardião |
| The Unfinished | La Inacabada | Das Unvollendete | A Inacabada |
| Guide | Guía | Hilfe | Guia |

The Artisan is *el Artesano*, *der Handwerker* and *o Artesão*.
