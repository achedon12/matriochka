package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Blocks;

/**
 * The bosses coming out of their shells: ./gradlew runClientGameTest -Pawaken. On a quartz stage in the sky, summons
 * each boss in front of the player and photographs its awakening (misc.<boss>.awaken) folded, swelling and roaring.
 * Shots: awaken_<boss>_<0|1|2|bar|cracked|fold|sealed>.png. -Pbosses=a,b limits the run.
 */
final class AwakenTest {
	private AwakenTest() {}

	static final List<String> BOSSES = List.of("block_guardian", "spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater",
		"your_double", "pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished");

	static void run(ClientGameTestContext ctx) {
		String only = System.getProperty("matriochka.bosses", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			sp.getConnection().waitForChunksRender();
			for (String c : List.of("gamerule advance_time false", "time set 6000", "gamerule spawn_monsters false", "gamemode creative @a",
				"gamerule show_death_messages false")) s.runCommand(c);
			ctx.setScreen(() -> null);
			int y = s.computeOnServer(srv -> srv.overworld().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, 0, 0)) + 30;
			s.runOnServer(srv -> {
				var l = srv.overworld();
				for (int x = -14; x <= 14; x++)
					for (int z = -22; z <= 6; z++) {
						l.setBlock(new BlockPos(x, y - 1, z), Blocks.SMOOTH_QUARTZ.defaultBlockState(), 3);
						for (int h = 0; h < 14; h++) l.setBlock(new BlockPos(x, y + h, z), Blocks.AIR.defaultBlockState(), 3);
					}
			});
			ctx.waitTicks(40);
			for (String id : BOSSES) {
				if (!only.isEmpty() && !only.contains(id)) continue;
				// facing north, the boss wakes six blocks ahead
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a 0.5 %d 2.5 180 5", y));
				ctx.waitTicks(10);
				s.runCommand("execute as @p at @s run matriochka boss " + id);
				ctx.waitTicks(6);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_0").withSize(1600, 900).disableCounterPrefix());
				ctx.waitTicks(16);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_1").withSize(1600, 900).disableCounterPrefix());
				ctx.waitTicks(14);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_2").withSize(1600, 900).disableCounterPrefix());
				// once the introduction is over: the boss's own bar at the top of the screen, hit once to show its trail
				ctx.waitTicks(50);
				s.runCommand("damage @e[type=matriochka:" + id + ",limit=1] 60 minecraft:player_attack by @p");
				ctx.waitTicks(4);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_bar").withSize(1600, 900).disableCounterPrefix());
				// broken through its phases: the cracks of its later shells
				for (float at : new float[]{0.5f, 0.2f}) {
					s.runOnServer(srv -> {
						var l = srv.overworld();
						for (var b : l.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioBoss.class, new net.minecraft.world.phys.AABB(new BlockPos(0, y, 0)).inflate(48)))
							b.setHealth(b.getMaxHealth() * at + 2);
					});
					s.runCommand("damage @e[type=matriochka:" + id + ",limit=1] 2 minecraft:player_attack by @p");
					ctx.waitTicks(50);
				}
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_cracked").withSize(1600, 900).disableCounterPrefix());
				// its defeat: it folds back into its doll, its name is sealed on a card, its relics fall
				s.runCommand("kill @e[type=matriochka:" + id + "]");
				ctx.waitTicks(20);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_fold").withSize(1600, 900).disableCounterPrefix());
				ctx.waitTicks(30);
				ctx.takeScreenshot(TestScreenshotOptions.of("awaken_" + id + "_sealed").withSize(1600, 900).disableCounterPrefix());
				ctx.waitTicks(30);
				s.runCommand("kill @e[type=item]");
			}
			Matriochka.LOG.info("[awaken] ok");
		}
	}
}
