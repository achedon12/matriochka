package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;

/**
 * Records frame sequences for the trailer (run with -Dmatriochka.capture=trailer): a flyover of every world,
 * its creatures in the arena, and a live boss fight. Frames land in screenshots/ as seq_wNN_X_0000.png.
 */
public class TrailerCapture implements FabricClientGameTest {
	private static final String[] BOSSES = {"block_guardian", "spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater", "your_double",
		"pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished"};

	private static void frame(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
	}

	@Override
	public void runTest(ClientGameTestContext ctx) {
		if (!"trailer".equals(System.getProperty("matriochka.capture"))) return;
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			sp.getConnection().waitForChunksRender();
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("time set 6000");
			s.runCommand("effect give @a night_vision infinite 0 true");
			s.runCommand("effect give @a resistance infinite 255 true");
			s.runCommand("effect give @a regeneration infinite 255 true");
			s.runCommand("effect give @a saturation infinite 255 true");
			s.runCommand("execute as @p run matriochka progression set 10");
			for (int w = 0; w <= 10; w++) {
				String tag = String.format("w%02d", w);
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world enter " + w);
					ctx.setScreen(() -> null);
					ctx.waitTicks(100);
					sp.getConnection().waitForChunksRender();
				}
				s.runCommand("gamemode spectator @a");
				// A: flyover, rising and turning slowly
				s.runCommand("execute as @p at @s run tp @s ~ ~6 ~ 200 18");
				ctx.waitTicks(30);
				sp.getConnection().waitForChunksRender();
				for (int f = 0; f < 70; f++) {
					s.runCommand("execute as @p at @s run tp @s ^ ^0.06 ^0.45 ~0.35 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_a_%04d", tag, f));
				}
				// B: creatures of the world, the camera circling them
				s.runCommand("gamemode creative @a");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~" + 40);
				ctx.waitTicks(40);
				sp.getConnection().waitForChunksRender();
				int k = 0;
				for (Defs.MobDef m : Content.MOBS) {
					if (m.world() != w) continue;
					s.runCommand("execute as @p at @s run summon matriochka:" + m.id() + " ^" + (k * 2 - 4) + " ^ ^7 {NoAI:1b,PersistenceRequired:1b}");
					k++;
				}
				if (w == 0) s.runCommand("execute as @p at @s run summon matriochka:doll_peddler ^ ^ ^6 {NoAI:1b}");
				s.runCommand("gamemode spectator @a");
				for (int f = 0; f < 60; f++) {
					s.runCommand("execute as @p at @s run tp @s ^0.32 ^ ^0.08 ~-1.6 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_b_%04d", tag, f));
				}
				s.runCommand("kill @e[type=!player]");
				// C: the boss, awake, fighting the player
				s.runCommand("gamemode adventure @a");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~" + (w == 0 ? 30 : 100));
				ctx.waitTicks(40);
				sp.getConnection().waitForChunksRender();
				s.runCommand("execute as @p at @s run summon matriochka:" + BOSSES[w] + " ^ ^ ^9");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=matriochka:" + BOSSES[w] + ",limit=1] eyes");
				for (int f = 0; f < 110; f++) {
					if (f % 10 == 0) s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=matriochka:" + BOSSES[w] + ",limit=1] eyes");
					ctx.waitTicks(2);
					frame(ctx, String.format("seq_%s_c_%04d", tag, f));
				}
				s.runCommand("kill @e[type=!player]");
				s.runCommand("gamemode creative @a");
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world leave");
					ctx.waitTicks(40);
				}
			}
		}
	}
}
