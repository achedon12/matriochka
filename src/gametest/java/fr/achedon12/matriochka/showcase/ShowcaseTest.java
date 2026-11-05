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
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
	}

	/** Places every structure of every world and photographs it from above, three quarters. Shots: struct_<id>.png */
	private static void structures(ClientGameTestContext ctx) {
		String only = System.getProperty("matriochka.worlds", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			sp.getConnection().waitForChunksRender();
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
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
				for (Defs.StructureDef d : Content.STRUCTURES) {
					if (d.world() != w) continue;
					int x = (k % 5) * 110 - 220, z = 260 + (k / 5) * 140;
					k++;
					s.runCommand("execute at @e[tag=st,limit=1] run place structure matriochka:" + d.id() + " ~" + x + " ~ ~" + z);
					int back = d.size().equals("large") ? 46 : d.size().equals("small") ? 22 : 32;
					s.runCommand("execute at @e[tag=st,limit=1] positioned ~" + x + " ~ ~" + z + " run tp @p ~" + (back * 6 / 10) + " ~" + (back * 6 / 10) + " ~-" + back + " facing ~ ~2 ~");
					ctx.waitTicks(60);
					sp.getConnection().waitForChunksRender();
					ctx.waitTicks(10);
					ctx.takeScreenshot(TestScreenshotOptions.of("struct_" + d.id()).withSize(1600, 900).disableCounterPrefix());
				}
				s.runCommand("gamemode creative @a");
				s.runCommand("execute as @p run matriochka world leave");
				ctx.waitTicks(40);
			}
		}
	}

	/** Lets a few creatures fight a protected survival player and logs every move they start. */
	private static void moves(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("time set 6000");
			server.runCommand("difficulty normal");
			server.runCommand("execute as @p at @s run spreadplayers ~ ~ 0 1 false @s");
			server.runCommand("gamemode survival @a");
			server.runCommand("effect give @a resistance infinite 4 true");
			server.runCommand("effect give @a regeneration infinite 4 true");
			server.runCommand("effect give @a saturation infinite 4 true");
			ctx.setScreen(() -> null);
			ctx.waitTicks(40);
			String[] mobs = {"executioner", "blind_prowler", "dead_smith", "sentinel", "storm_bird", "bell_crab"};
			for (int i = 0; i < mobs.length; i++) {
				server.runCommand("execute as @p at @s run summon matriochka:" + mobs[i] + " ~" + (i % 3 * 3 - 3) + " ~2 ~" + (6 + i / 3 * 3));
			}
			server.runCommand("execute as @p at @s run tp @s ~ ~ ~ 0 20");
			for (int i = 0; i < 12; i++) {
				ctx.waitTicks(50);
				shot(ctx, String.format("moves_%02d", i));
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
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
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
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(0));
			ctx.waitTicks(12);
			ctx.runOnClient(mc -> ((fr.achedon12.matriochka.client.JournalScreen) mc.gui.screen()).turnTo(2));
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
					int[] pos = ctx.computeOnClient(mc -> new int[]{mc.gui.screen().width / 2 - 70, mc.gui.screen().height / 2 - 111 + 22 + 10});
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
		if ("moves".equals(System.getProperty("matriochka.capture"))) {
			moves(ctx);
			return;
		}
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
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
				sp.getConnection().waitForChunksRender();
				server.runCommand("execute as @p at @s run tp @s ~ ~1 ~ 180 15");
				ctx.waitTicks(60);
				shot(ctx, String.format("w%02d_threshold", w));
				server.runCommand("execute as @p at @s run tp @s ~ ~ ~ 0 5");
				ctx.waitTicks(20);
				shot(ctx, String.format("w%02d_view", w));
				server.runCommand("execute as @p at @s run tp @s ~ ~ ~" + 150 + " 0 10");
				ctx.waitTicks(80);
				sp.getConnection().waitForChunksRender();
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
