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

	private static void third(ClientGameTestContext ctx, boolean on) {
		ctx.runOnClient(mc -> mc.options.setCameraType(on ? net.minecraft.client.CameraType.THIRD_PERSON_BACK : net.minecraft.client.CameraType.FIRST_PERSON));
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
			s.runCommand("difficulty normal");
			for (int w = 0; w <= 10; w++) {
				String tag = String.format("w%02d", w);
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world enter " + w);
					ctx.setScreen(() -> null);
					ctx.waitTicks(100);
					sp.getConnection().waitForChunksRender();
				}
				third(ctx, false);
				s.runCommand("gamemode spectator @a");
				// A: high aerial glide, looking down over the world
				s.runCommand("execute as @p at @s run tp @s ~ ~22 ~ 200 28");
				ctx.waitTicks(40);
				sp.getConnection().waitForChunksRender();
				for (int f = 0; f < 120; f++) {
					s.runCommand("execute as @p at @s run tp @s ^ ^-0.04 ^0.55 ~0.25 ~-0.06");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_a_%04d", tag, f));
				}
				// D: low dolly close to the ground
				s.runCommand("execute as @p at @s run tp @s ~ ~-18 ~ ~140 6");
				ctx.waitTicks(30);
				sp.getConnection().waitForChunksRender();
				for (int f = 0; f < 72; f++) {
					s.runCommand("execute as @p at @s run tp @s ^-0.05 ^0.03 ^0.3 ~-0.4 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_d_%04d", tag, f));
				}
				// B: the world's creatures, still, the camera circling them
				s.runCommand("gamemode creative @a");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~" + 40 + " 12");
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
				for (int f = 0; f < 72; f++) {
					s.runCommand("execute as @p at @s run tp @s ^0.32 ^ ^0.08 ~-1.6 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_b_%04d", tag, f));
				}
				s.runCommand("kill @e[type=!player]");
				// F: two creatures attacking the player, seen over the shoulder
				if (w > 0) {
					s.runCommand("gamemode adventure @a");
					s.runCommand("execute as @p at @s run tp @s ~ ~ ~" + 70 + " 8");
					ctx.waitTicks(30);
					sp.getConnection().waitForChunksRender();
					int n = 0;
					for (Defs.MobDef m : Content.MOBS) {
						if (m.world() != w || n >= 2 || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
						s.runCommand("execute as @p at @s run summon matriochka:" + m.id() + " ^" + (n * 4 - 2) + " ^1 ^7");
						n++;
					}
					third(ctx, true);
					for (int f = 0; f < 120; f++) {
						if (f % 15 == 0) s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=!player,limit=1,sort=nearest] feet");
						ctx.waitTicks(2);
						frame(ctx, String.format("seq_%s_f_%04d", tag, f));
					}
					third(ctx, false);
					s.runCommand("kill @e[type=!player]");
				}
				// C: the boss, awake, fighting the player
				s.runCommand("gamemode adventure @a");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~" + (w == 0 ? 30 : 100) + " 0");
				ctx.waitTicks(40);
				sp.getConnection().waitForChunksRender();
				s.runCommand("execute as @p at @s run summon matriochka:" + BOSSES[w] + " ^ ^ ^11");
				s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=matriochka:" + BOSSES[w] + ",limit=1] eyes");
				third(ctx, true);
				for (int f = 0; f < 150; f++) {
					if (f % 10 == 0) s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=matriochka:" + BOSSES[w] + ",limit=1] eyes");
					ctx.waitTicks(2);
					frame(ctx, String.format("seq_%s_c_%04d", tag, f));
				}
				third(ctx, false);
				s.runCommand("kill @e[type=!player]");
				s.runCommand("gamemode creative @a");
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world leave");
					ctx.waitTicks(40);
				}
			}
			// G: the interfaces, with the HUD back on
			ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
			s.runCommand("execute as @p run matriochka karma soul @p 420");
			ctx.waitTicks(20);
			ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(true));
			ctx.waitTicks(10);
			frame(ctx, "seq_gui_scroll");
			for (int t = 0; t < 4; t++) {
				int tab = t;
				ctx.setScreen(() -> new fr.achedon12.matriochka.client.JournalScreen(false).tab(tab));
				ctx.waitTicks(10);
				frame(ctx, "seq_gui_journal_" + t);
			}
			ctx.setScreen(() -> null);
			for (String st : new String[]{"matrix_workbench", "spore_vat", "jailer_table", "soul_altar", "class_table"}) {
				s.runCommand("execute as @p at @s run matriochka station " + st);
				ctx.waitTicks(15);
				frame(ctx, "seq_gui_station_" + st);
				ctx.setScreen(() -> null);
				ctx.waitTicks(5);
			}
		}
	}
}
