package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.world.Worlds;
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
			String only = System.getProperty("matriochka.worlds", "");
			String takes = System.getProperty("matriochka.takes", "adbfcg");
			for (int w = 0; w <= 10; w++) {
				if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
				String tag = String.format("w%02d", w);
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world enter " + w);
					ctx.setScreen(() -> null);
					ctx.waitTicks(100);
					sp.getConnection().waitForChunksRender();
				}
				s.runCommand("kill @e[type=marker]");
				s.runCommand("execute as @p at @s run summon marker ~ ~ ~ {Tags:[\"home\"]}");
				boolean under = w == 3 || w == 5;
				final int world = w;
				// the mod's own boss arena, built 26 blocks ahead: lit, open and the same stage in every world
				net.minecraft.core.BlockPos arena = sp.getServer().computeOnServer(server -> {
					var p = server.getPlayerList().getPlayers().get(0);
					var c = p.blockPosition().offset(0, 0, 26);
					fr.achedon12.matriochka.world.Arenas.buildArena((net.minecraft.server.level.ServerLevel) p.level(), world, c);
					return c;
				});
				// the Endless Dungeon rearranges its halls: rebuild the stage before each take there
				Runnable rebuild = () -> {
					if (world != 3) return;
					sp.getServer().runOnServer(server -> fr.achedon12.matriochka.world.Arenas.buildArena(
						(net.minecraft.server.level.ServerLevel) server.getPlayerList().getPlayers().get(0).level(), world, arena));
				};
				if (w == 7) s.runCommand("effect give @a conduit_power infinite 0 true");
				if (w == 2) {
					// the Giant Veins sit on lava: keep it from flowing onto the stage
					for (int qx = -1; qx <= 0; qx++) for (int qz = -1; qz <= 0; qz++) {
						int x0 = arena.getX() + qx * 30, z0 = arena.getZ() + qz * 30;
						s.runCommand("execute at @p run fill " + x0 + " " + (arena.getY() - 3) + " " + z0 + " " + (x0 + 29) + " " + (arena.getY() + 14) + " " + (z0 + 29) + " minecraft:basalt replace minecraft:lava");
					}
				}
				s.runCommand("kill @e[type=marker,tag=arena]");
				s.runCommand("execute at @p run summon marker " + arena.getX() + " " + arena.getY() + " " + arena.getZ() + " {Tags:[\"arena\"]}");
				s.runCommand("gamemode spectator @a");
				if (takes.contains("a")) {
				// A: the world from the air (underground worlds: a slow drift through the halls by the arena)
				if (under) {
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~-9 ~4 ~-9 -45 14");
				} else {
					s.runCommand("execute at @e[tag=home,limit=1] run tp @p ~ ~" + (w == 2 ? 8 : 24) + " ~ 200 " + (w == 2 ? 14 : 28));
				}
				ctx.waitTicks(50);
				sp.getConnection().waitForChunksRender();
				for (int f = 0; f < 120; f++) {
					s.runCommand(under ? "execute as @p at @s run tp @s ^0.05 ^0.01 ^0.1 ~0.5 ~"
						: "execute as @p at @s run tp @s ^ ^-0.04 ^0.55 ~0.25 ~-0.06");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_a_%04d", tag, f));
				}
				// the arena, 160 blocks from the Threshold: lit, open, the same place for every world
				}
				if (takes.contains("d")) {
				// D: low sweep across the arena floor and its pillars
				s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~-11 ~2.2 ~-11 -45 8");
				ctx.waitTicks(50);
				sp.getConnection().waitForChunksRender();
				for (int f = 0; f < 72; f++) {
					s.runCommand("execute as @p at @s run tp @s ^0.06 ^0.02 ^0.26 ~-0.35 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_d_%04d", tag, f));
				}
				}
				rebuild.run();
				if (takes.contains("b")) {
				// B: the world's creatures, still, the camera circling them
				int k = 0;
				for (Defs.MobDef m : Content.MOBS) {
					if (m.world() != w) continue;
					s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:" + m.id() + " ~" + (k * 3 - 6) + " ~ ~4 {NoAI:1b,PersistenceRequired:1b,Rotation:[180f,0f]}");
					k++;
				}
				if (w == 0) s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:doll_peddler ~ ~ ~4 {NoAI:1b,Rotation:[180f,0f]}");
				s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~-9 ~2.4 ~-4 -40 14");
				ctx.waitTicks(30);
				for (int f = 0; f < 72; f++) {
					s.runCommand("execute as @p at @s run tp @s ^0.3 ^ ^0.06 ~-1.1 ~");
					ctx.waitTick();
					frame(ctx, String.format("seq_%s_b_%04d", tag, f));
				}
				s.runCommand("kill @e[type=!player,type=!marker]");
				}
				rebuild.run();
				if (takes.contains("f")) {
				// F: two creatures come for the player, seen through the player's eyes
				if (w > 0) {
					s.runCommand("gamemode adventure @a");
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-10 0 6");
					ctx.waitTicks(20);
					int n = 0;
					for (Defs.MobDef m : Content.MOBS) {
						if (m.world() != w || n >= 2 || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
						s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:" + m.id() + " ~" + (n * 4 - 2) + " ~ ~-2");
						n++;
					}
					for (int f = 0; f < 120; f++) {
						if (f % 10 == 0) s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=!player,type=!marker,limit=1,sort=nearest] eyes");
						if (f % 4 == 0) { s.runCommand("effect clear @a minecraft:darkness"); s.runCommand("effect clear @a minecraft:blindness"); s.runCommand("effect clear @a minecraft:nausea"); }
						ctx.waitTicks(2);
						frame(ctx, String.format("seq_%s_f_%04d", tag, f));
					}
					s.runCommand("kill @e[type=!player,type=!marker]");
				}
				}
				rebuild.run();
				if (takes.contains("c")) {
				// C: the boss, awake, fighting the player
				s.runCommand("gamemode adventure @a");
				s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-12 0 0");
				ctx.waitTicks(20);
				s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:" + BOSSES[w] + " ~ ~ ~");
				for (int f = 0; f < 150; f++) {
					if (f % 8 == 0) s.runCommand("execute as @p at @s run tp @s ~ ~ ~ facing entity @e[type=matriochka:" + BOSSES[w] + ",limit=1] eyes");
					if (f % 4 == 0) { s.runCommand("effect clear @a minecraft:darkness"); s.runCommand("effect clear @a minecraft:blindness"); s.runCommand("effect clear @a minecraft:nausea"); }
					ctx.waitTicks(2);
					frame(ctx, String.format("seq_%s_c_%04d", tag, f));
				}
				s.runCommand("kill @e[type=!player]");
				}
				s.runCommand("gamemode creative @a");
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world leave");
					ctx.waitTicks(40);
				}
			}
			if (!takes.contains("g")) return;
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
