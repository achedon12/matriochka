package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;

/**
 * Smoke test and showcase: loads every world, wakes every boss and captures screenshots
 * (used for the trailer, the wiki and the website). Run with ./gradlew runClientGameTest.
 */
public class ShowcaseTest implements FabricClientGameTest {
	private static void shot(ClientGameTestContext ctx, String name) {
		// no advancement toasts or chat lines over the interface: screens are shot with the HUD layer hidden,
		// HUD shots wait for the toasts and the chat to fade
		boolean hud = name.startsWith("gui_hud");
		if (hud) ctx.waitTicks(220);
		else ctx.runOnClient(mc -> { if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
		if (!hud) ctx.runOnClient(mc -> { if (fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
	}

	/** Places every structure of every world and photographs it from above, three quarters. Shots: struct_<id>.png */
	private static void structures(ClientGameTestContext ctx) {
		String only = System.getProperty("matriochka.worlds", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			McTest.waitForChunks(sp);
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> { if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("time set 6000");
			s.runCommand("effect give @a night_vision infinite 0 true");
			s.runCommand("effect give @a conduit_power infinite 0 true");
			s.runCommand("execute as @p run matriochka progression set 10");
			for (int w = 1; w <= 10; w++) {
				if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
				s.runCommand("execute as @p run matriochka world enter " + w);
				ctx.setScreen(() -> null);
				ctx.waitTicks(100);
				s.runCommand("gamemode spectator @a");
				s.runCommand("kill @e[type=marker]");
				s.runCommand("execute as @p at @s run summon marker ~ ~ ~ {Tags:[\"st\"]}");
				int k = 0;
				final int world = w;
				String role = System.getProperty("matriochka.role", "");
				for (Defs.StructureDef d : Content.STRUCTURES) {
					if (d.world() != w) continue;
					if (!role.isEmpty() && !d.role().equals(role)) continue;
					final int dx = (k % 5) * 110 - 220, dz = 260 + (k / 5) * 140;
					k++;
					final int back = d.size().equals("large") ? 46 : d.size().equals("small") ? 22 : 32;
					// fly there first so the chunks load, then place it through the server's own command and aim the camera at it
					s.runCommand("execute at @e[tag=st,limit=1] run tp @p ~" + dx + " ~30 ~" + (dz - back));
					ctx.waitTicks(40);
					McTest.waitForChunks(sp);
					int[] cam = sp.getServer().computeOnServer(server -> {
						var p = server.getPlayerList().getPlayers().get(0);
						var lvl = (net.minecraft.server.level.ServerLevel) p.level();
						int x = p.getBlockX(), z = p.getBlockZ() + back;
						boolean ceiling = fr.achedon12.matriochka.world.Worlds.ceiling(world);
						// World 2's heightmap stops on its rock roof, out of the world: the structure finds its cave floor itself
						int y = ceiling ? 30 + Math.floorMod((x >> 4) * 31 + (z >> 4) * 17, 40) : world == 2 ? 64 : lvl.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.WORLD_SURFACE, x, z);
						var src = server.createCommandSourceStack().withLevel(lvl).withPosition(new net.minecraft.world.phys.Vec3(x, y, z)).withSuppressedOutput();
						try {
							int r = server.getCommands().getDispatcher().execute("place structure matriochka:" + d.id() + " " + x + " " + y + " " + z, src);
							org.slf4j.LoggerFactory.getLogger("matriochka").info("[shoot] {} placed ({})", d.id(), r);
						} catch (Exception e) {
							org.slf4j.LoggerFactory.getLogger("matriochka").info("[shoot] {} failed: {}", d.id(), e.getMessage());
						}
						int top = ceiling ? y : lvl.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
						if (d.role().equals("wonder")) {
							// a wonder may sit in a cave, under the sea or in the dark: aim at its reliquary, wherever it is
							var rel = fr.achedon12.matriochka.content.ModContent.block("reliquary");
							for (var bp : net.minecraft.core.BlockPos.betweenClosed(x - 40, lvl.getMinY(), z - 40, x + 40, lvl.getMaxY(), z + 40))
								if (lvl.getBlockState(bp).is(rel)) return new int[]{bp.getX(), bp.getY(), bp.getZ()};
						}
						return new int[]{x, top, z};
					});
					// World 5's fog is short: come in closer there
					final int cb = world == 5 ? back * 11 / 20 : d.role().equals("wonder") ? back * 3 / 4 : back;
					s.runCommand("execute as @p at @s run tp @s " + (cam[0] + cb / 2) + " " + (cam[1] + cb * 4 / 10) + " " + (cam[2] - cb * 9 / 10) + " facing " + cam[0] + " " + (cam[1] + 3) + " " + cam[2]);
					ctx.waitTicks(60);
					McTest.waitForChunks(sp);
					ctx.waitTicks(10);
					ctx.takeScreenshot(TestScreenshotOptions.of("struct_" + d.id()).withSize(1600, 900).disableCounterPrefix());
				}
				s.runCommand("gamemode creative @a");
				s.runCommand("execute as @p run matriochka world leave");
				ctx.waitTicks(40);
			}
		}
	}

	/** Moves the cursor to a point given in GUI coordinates. */
	private static void cursor(ClientGameTestContext ctx, double gx, double gy) {
		double scale = ctx.computeOnClient(mc -> mc.getWindow().getGuiScale());
		ctx.getInput().setCursorPos(gx * scale, gy * scale);
	}

	/**
	 * Every interface, at rest and in motion: the scroll unrolling, each Journal tab, a page mid-turn, every
	 * station (one caught while its drawers slide in, one with a drawer pulled out) and the HUD in a few worlds.
	 * Run with ./gradlew runClientGameTest -Pgui. Shots: gui_*.png
	 */
	private static void gui(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			McTest.waitForChunks(sp);
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("time set 6000");
			server.runCommand("gamemode creative @a");
			server.runCommand("effect give @a night_vision infinite 0 true");
			server.runCommand("execute as @p run matriochka progression set 3");
			server.runCommand("execute as @p run matriochka karma soul @p 420");
			server.runOnServer(srv -> fr.achedon12.matriochka.rules.PlayerState.of(srv.getPlayerList().getPlayers().get(0)).setDoll(2, 3));
			server.runCommand("give @p minecraft:iron_ingot 16");
			server.runCommand("give @p minecraft:oak_log 16");
			ctx.waitTicks(30);
			cursor(ctx, 2, 2);
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(true));
			ctx.waitTicks(4);
			shot(ctx, "gui_scroll_opening");
			ctx.waitTicks(16);
			shot(ctx, "gui_scroll");
			for (int t = 0; t < 5; t++) {
				int tab = t;
				ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(tab));
				ctx.waitTicks(12);
				shot(ctx, "gui_journal_" + t);
			}
			// the Pages tab, with a handful of pages found (one of them still coded), and an ending's crawl
			server.runOnServer(srv -> {
				var ps = fr.achedon12.matriochka.rules.PlayerState.of(srv.getPlayerList().getPlayers().get(0));
				ps.tag().putInt("pages_1", 0b11111);
				ps.tag().putInt("pages_4", 0b01011);
				ps.tag().putInt("pages_9", 0b10000);
				ps.sync();
			});
			ctx.waitTicks(5);
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(5));
			ctx.waitTicks(12);
			shot(ctx, "gui_journal_5");
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.EndingScreen("tools"));
			ctx.waitTicks(100);
			shot(ctx, "gui_ending");
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(0));
			ctx.waitTicks(12);
			ctx.runOnClient(mc -> ((fr.achedon12.matriochka.client.JournalScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).turnTo(2));
			ctx.waitTicks(3);
			shot(ctx, "gui_journal_turn");
			ctx.setScreen(() -> null);
			ctx.waitTicks(5);
			boolean firstStation = true;
			for (String st : new String[]{"matrix_workbench", "class_table", "soul_altar", "spore_vat", "ash_foundry", "jailer_table", "lightning_forge",
				"dark_altar", "inverter", "abyssal_press", "time_workshop", "terrain_anchor", "final_loom"}) {
				server.runCommand("execute as @p at @s run matriochka station " + st);
				if (firstStation) {
					ctx.waitTicks(4);
					shot(ctx, "gui_station_opening");
					firstStation = false;
				}
				ctx.waitTicks(16);
				shot(ctx, "gui_station_" + st);
				if (st.equals("matrix_workbench")) {
					int[] pos = ctx.computeOnClient(mc -> new int[]{fr.achedon12.matriochka.client.mc.McClient.screen(mc).width / 2 - 70, fr.achedon12.matriochka.client.mc.McClient.screen(mc).height / 2 - 111 + 22 + 10});
					cursor(ctx, pos[0], pos[1]);
					ctx.waitTicks(8);
					shot(ctx, "gui_station_hover");
					cursor(ctx, 2, 2);
				}
				ctx.setScreen(() -> null);
				ctx.waitTicks(5);
			}
			for (int w : new int[]{2, 7, 8, 4}) {
				server.runCommand("execute as @p run matriochka world enter " + w);
				ctx.setScreen(() -> null);
				ctx.waitTicks(100);
				shot(ctx, "gui_hud_w" + w);
				server.runCommand("execute as @p run matriochka world leave");
				ctx.waitTicks(40);
			}
		}
	}

	@Override
	public void runTest(ClientGameTestContext ctx) {
		Watchdog.start();
		if ("gui".equals(System.getProperty("matriochka.capture"))) {
			gui(ctx);
			return;
		}
		if ("trailer".equals(System.getProperty("matriochka.capture"))) {
			new TrailerCapture().runTest(ctx);
			return;
		}
		if ("structures".equals(System.getProperty("matriochka.capture"))) {
			structures(ctx);
			return;
		}
		if ("tiktok".equals(System.getProperty("matriochka.capture"))) {
			TiktokCapture.run(ctx);
			return;
		}
		if ("worldfilm".equals(System.getProperty("matriochka.capture"))) {
			WorldFilm.run(ctx);
			return;
		}
		if ("epic".equals(System.getProperty("matriochka.capture"))) {
			EpicCapture.run(ctx);
			return;
		}
		if ("automation".equals(System.getProperty("matriochka.capture"))) {
			AutomationTest.run(ctx);
			return;
		}
		if ("fixes".equals(System.getProperty("matriochka.capture"))) {
			FixesTest.run(ctx);
			return;
		}
		if ("rules".equals(System.getProperty("matriochka.capture"))) {
			RulesTest.run(ctx);
			return;
		}
		if ("ocean".equals(System.getProperty("matriochka.capture"))) {
			OceanTest.run(ctx);
			return;
		}
		if ("story".equals(System.getProperty("matriochka.capture"))) {
			StoryTest.run(ctx);
			return;
		}
		if ("systems".equals(System.getProperty("matriochka.capture"))) {
			SystemsTest.run(ctx);
			return;
		}
		if ("scale".equals(System.getProperty("matriochka.capture"))) {
			ScaleTest.run(ctx);
			return;
		}
		if ("visuals".equals(System.getProperty("matriochka.capture"))) {
			VisualsTest.run(ctx);
			return;
		}
		if ("hud".equals(System.getProperty("matriochka.capture"))) {
			HudTest.run(ctx);
			return;
		}
		if ("comfort".equals(System.getProperty("matriochka.capture"))) {
			ComfortTest.run(ctx);
			return;
		}
		if ("playthrough".equals(System.getProperty("matriochka.capture"))) {
			PlaythroughTest.run(ctx);
			return;
		}
		if ("onboarding".equals(System.getProperty("matriochka.capture"))) {
			OnboardingTest.run(ctx);
			return;
		}
		if ("replay".equals(System.getProperty("matriochka.capture"))) {
			ReplayTest.run(ctx);
			return;
		}
		if ("replayshots".equals(System.getProperty("matriochka.capture"))) {
			ReplayShots.run(ctx);
			return;
		}
		if ("screens".equals(System.getProperty("matriochka.capture"))) {
			ScreensTest.run(ctx);
			return;
		}
		if ("awaken".equals(System.getProperty("matriochka.capture"))) {
			AwakenTest.run(ctx);
			return;
		}
		if ("polish".equals(System.getProperty("matriochka.capture"))) {
			PolishTest.run(ctx);
			return;
		}
		if ("transition".equals(System.getProperty("matriochka.capture"))) {
			TransitionTest.run(ctx);
			return;
		}
		if ("rites".equals(System.getProperty("matriochka.capture"))) {
			RitesTest.run(ctx);
			return;
		}
		if ("machines".equals(System.getProperty("matriochka.capture"))) {
			MachinesTest.run(ctx);
			return;
		}
		if ("moves".equals(System.getProperty("matriochka.capture"))) {
			MovesTest.run(ctx);
			return;
		}
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			McTest.waitForChunks(sp);
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("time set 6000");
			server.runCommand("gamemode creative @a");
			server.runCommand("effect give @a night_vision infinite 0 true");
			ctx.waitTicks(40);
			ctx.setScreen(() -> null);
			ctx.waitTicks(10);
			shot(ctx, "00_surface");
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(true));
			ctx.waitTicks(10);
			shot(ctx, "gui_scroll");
			server.runCommand("execute as @p run matriochka progression set 3");
			server.runCommand("execute as @p run matriochka karma soul @p 420");
			ctx.waitTicks(30);
			for (int t = 0; t < 4; t++) {
				int tab = t;
				ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(tab));
				ctx.waitTicks(10);
				shot(ctx, "gui_journal_" + t);
			}
			ctx.setScreen(() -> null);
			for (String st : new String[]{"matrix_workbench", "spore_vat", "jailer_table", "soul_altar", "class_table"}) {
				server.runCommand("execute as @p at @s run matriochka station " + st);
				ctx.waitTicks(15);
				shot(ctx, "gui_station_" + st);
				ctx.setScreen(() -> null);
				ctx.waitTicks(5);
			}
			String[] bosses = {"spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater", "your_double", "pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished"};
			for (int w = 1; w <= 10; w++) {
				server.runCommand("execute as @p run matriochka world enter " + w);
				ctx.setScreen(() -> null);
				ctx.waitTicks(120);
				McTest.waitForChunks(sp);
				server.runCommand("execute as @p at @s run tp @s ~ ~1 ~ 180 15");
				ctx.waitTicks(60);
				shot(ctx, String.format("w%02d_threshold", w));
				server.runCommand("execute as @p at @s run tp @s ~ ~ ~ 0 5");
				ctx.waitTicks(20);
				shot(ctx, String.format("w%02d_view", w));
				server.runCommand("execute as @p at @s run tp @s ~ ~ ~" + 150 + " 0 10");
				ctx.waitTicks(80);
				McTest.waitForChunks(sp);
				server.runCommand("execute as @p at @s run summon matriochka:" + bosses[w - 1] + " ~ ~ ~-10 {NoAI:1b}");
				server.runCommand("execute as @p at @s run tp @s ~ ~3 ~ 180 12");
				ctx.waitTicks(40);
				shot(ctx, String.format("w%02d_boss", w));
				server.runCommand("kill @e[type=!player]");
				server.runCommand("execute as @p run matriochka world leave");
				ctx.waitTicks(40);
			}
		}
	}
}
