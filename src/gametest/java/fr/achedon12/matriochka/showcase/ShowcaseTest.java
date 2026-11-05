package fr.achedon12.matriochka.showcase;

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

	@Override
	public void runTest(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().create()) {
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
