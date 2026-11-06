**Matriochka, set up and ready to play.** This pack is the [Matriochka](https://github.com/achedon12/matriochka) mod for Minecraft 26.3 on Fabric, with its two required libraries, recipe pages and a set of client performance mods. Nothing else changes the game: no extra content, no tweaks to vanilla, only the mod and what makes it run well.

Matriochka is a progression mod. Ten worlds are nested inside blocks, one inside the other, like the dolls it is named after. You craft a Seed, plant it on tilled World Soil, and the block that hatches holds a whole world with its own rule, creatures, station and boss. Beat the boss, take its core, and the next Seed becomes possible.

![World 10, the Giant Workshop](https://achedon12.github.io/matriochka/shots/hero_banner.jpg)

## Two versions

| Version | Difficulty | Pick it if |
| --- | --- | --- |
| **Matriochka Pack** (version `0.4.0`) | `normal`: the mod's defaults | you want the game as designed |
| **Matriochka Pack (Hard)** (version `0.4.0-hard`) | `nightmare`: creatures and bosses hit 30% harder, Soul Cradles hold one charge instead of three | you have already finished a cycle, or play with a group that wants it tight |

Both have the same mods. The only difference is `config/matriochka.json`, which a server operator can change at any time (`difficulty`: `story`, `normal`, `nightmare` or `hardcore`, see [Configuration](https://github.com/achedon12/matriochka/wiki/Configuration)). The normal version is the newest upload of each release, so it is what launchers install by default; pick the `-hard` version from the version list.

## What is inside

| Mod | Side | Why it is here |
| --- | --- | --- |
| [Matriochka](https://github.com/achedon12/matriochka) | client and server | the mod itself |
| [Fabric API](https://modrinth.com/mod/fabric-api) | client and server | required by Matriochka |
| [GeckoLib](https://modrinth.com/mod/geckolib) | client and server | required: the models and animations of the 61 creatures and bosses |
| [Just Enough Items](https://modrinth.com/mod/jei) + [MezzConfig](https://modrinth.com/mod/mezzconfig) | client, optional | a recipe page for each of the thirteen stations (Matrix Workbench, Spore Vat, Ash Foundry...) |
| [Sodium](https://modrinth.com/mod/sodium) | client | a much higher frame rate, mostly in the dense worlds (the jungle of World 1, the halls of World 3) |
| [Lithium](https://modrinth.com/mod/lithium) | client and server | faster game logic: mob AI, physics, chunk ticking. Every world is a separate dimension, so this adds up |
| [FerriteCore](https://modrinth.com/mod/ferrite-core) | client and server | less memory, which matters with eleven extra dimensions loaded over a playthrough |
| [Entity Culling](https://modrinth.com/mod/entityculling) | client | skips creatures and block entities you cannot see |
| [ImmediatelyFast](https://modrinth.com/mod/immediatelyfast) | client | faster HUD, text and map rendering |
| [Dynamic FPS](https://modrinth.com/mod/dynamic-fps) | client | lowers the frame rate when the game is in the background or minimised |
| [Krypton](https://modrinth.com/mod/krypton) | client and server | a lighter network stack, for servers |
| [Mod Menu](https://modrinth.com/mod/modmenu) + [Placeholder API](https://modrinth.com/mod/placeholder-api) | client | the mod list; Matriochka's entry opens its info screen and its comfort options |
| [Iris](https://modrinth.com/mod/iris) | client, optional | shaders, if you want them. Off unless you load a shader pack |

Versions: Fabric API, GeckoLib and JEI are the exact versions Matriochka is built against. The others are the newest release for Minecraft 26.3 when the pack is built, with their required libraries. Every file is downloaded from Modrinth, except the Matriochka jar, which comes from its [GitHub release](https://github.com/achedon12/matriochka/releases) until the Modrinth project is public.

The pack also sets render distance 10 and simulation distance 8 in `options.txt`.

## Left out on purpose

- **LambDynamicLights.** A torch in your hand would light the Lightless Deep, and the whole point of World 5 is that it is dark: its rule is noise, its creatures hunt what they hear, and light is something you place. Dynamic lights would defeat that rule.
- **Minimaps** (Xaero's, JourneyMap, VoxelMap). A personal choice, and a map is not needed. They work with Matriochka if you add them; Xaero's cave view and radar are turned off inside World 5 for the same reason as above (see [Compatibility](https://github.com/achedon12/matriochka/wiki/Compatibility)).
- **C2ME and ScalableLux.** Only alpha builds exist for 26.3, and both rewrite chunk generation and lighting, which every Matriochka world uses.
- **ModernFix, MemoryLeakFix and Noisium.** No build for 26.3 yet.
- Content mods of any kind. The pack is Matriochka and nothing else, so a bug report is a Matriochka bug report.

## Install

**Modrinth App.** Click *Install* on this page, or search "Matriochka Pack" in the app. To play the hard version, open *Versions* and install `0.4.0-hard`.

**Prism Launcher.** *Add Instance* → *Modrinth* → search "Matriochka Pack", or *Import* the `.mrpack` file from the *Versions* tab. Prism asks about the optional mods (JEI, Iris): untick what you do not want.

**Other launchers.** Any launcher that imports `.mrpack` files works (ATLauncher, MultiMC forks). The `.mrpack` files are also attached to each [GitHub release](https://github.com/achedon12/matriochka/releases).

You need Java 25; the Modrinth App and Prism download it for you.

## Running a server

Matriochka has to be on the server and on every client. On a Fabric 26.3 server (Fabric Loader 0.20.0 or newer, Java 25), put these in `mods/`:

- **Required:** Matriochka, Fabric API, GeckoLib
- **Recommended:** Lithium, FerriteCore, Krypton (server side only, players do not need them to match)

Do not put Sodium, Iris, Entity Culling, ImmediatelyFast, Dynamic FPS, Mod Menu or JEI on the server: they are client mods. For the hard version, copy the pack's `config/matriochka.json` to the server's `config/` folder, or set `"difficulty": "nightmare"` there yourself. Server rules and commands are on the wiki: [Configuration](https://github.com/achedon12/matriochka/wiki/Configuration), [Commands](https://github.com/achedon12/matriochka/wiki/Commands), [Multiplayer and groups](https://github.com/achedon12/matriochka/wiki/Multiplayer-and-Groups).

## Links

- Website: <https://achedon12.github.io/matriochka/>
- Wiki: <https://github.com/achedon12/matriochka/wiki> (getting started, every world, boss and station)
- Source, issues and releases: <https://github.com/achedon12/matriochka>
- Discord: <https://discord.gg/SPVCf5hRuh>

Bugs in the pack (a mod that does not start, a conflict) and in the mod go to the same [issue tracker](https://github.com/achedon12/matriochka/issues). Matriochka and the pack are MIT licensed; each included mod keeps its own license.
