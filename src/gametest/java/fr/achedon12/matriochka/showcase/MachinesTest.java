package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.net.StationMenu;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The thirteen stations: ./gradlew runClientGameTest -Pmachines. Builds a row of them on a quartz floor, photographs
 * each sculpted model from the front-left, the whole row, then opens every station through a real right click and
 * photographs its screen. Shots: machines_*.png. Fails the run when a screen does not open.
 */
final class MachinesTest {
	private MachinesTest() {}

	static final List<String> STATIONS = List.of("matrix_workbench", "class_table", "soul_altar", "spore_vat", "ash_foundry", "jailer_table",
		"lightning_forge", "dark_altar", "inverter", "abyssal_press", "time_workshop", "terrain_anchor", "final_loom");

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.runOnClient(mc -> { if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
		ctx.waitTicks(2);
		ctx.takeScreenshot(TestScreenshotOptions.of("machines_" + name).withSize(1600, 900).disableCounterPrefix());
		ctx.runOnClient(mc -> { if (fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
	}

	static void run(ClientGameTestContext ctx) {
		String only = System.getProperty("matriochka.only", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			McTest.waitForChunks(sp);
			for (String c : List.of("gamerule advance_time false", "gamerule advance_weather false", "weather clear", "gamerule spawn_monsters false",
				"time set 1000", "gamemode creative @a")) s.runCommand(c);
			ctx.setScreen(() -> null);
			int y = s.computeOnServer(srv -> srv.overworld().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, 0, 0)) + 20;
			s.runOnServer(srv -> {
				var lvl = srv.overworld();
				for (int x = -4; x < STATIONS.size() * 3 + 4; x++)
					for (int z = -6; z < 5; z++) {
						lvl.setBlock(new BlockPos(x, y - 1, z), Blocks.SMOOTH_QUARTZ.defaultBlockState(), 3);
						for (int h = 0; h < 6; h++) lvl.setBlock(new BlockPos(x, y + h, z), Blocks.AIR.defaultBlockState(), 3);
					}
				for (int i = 0; i < STATIONS.size(); i++)
					lvl.setBlock(new BlockPos(i * 3, y, 0), ModContent.block(STATIONS.get(i)).defaultBlockState(), 3);
			});
			ctx.waitTicks(60);
			McTest.waitForChunks(sp);
			for (int i = 0; i < STATIONS.size(); i++) {
				String id = STATIONS.get(i);
				if (!only.isEmpty() && !only.contains(id)) continue;
				// three quarters from the front-left, a little above
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f -35 28", i * 3 + 0.5 - 1.0, y + 0.55, -1.15));
				ctx.waitTicks(25);
				shot(ctx, id);
			}
			if (only.isEmpty()) {
				// the overviews hover beside the floor: a spectator does not fall
				s.runCommand("gamemode spectator @a");
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f 0 24", STATIONS.size() * 1.5 - 1.0, y + 4.5, -13.0));
				ctx.waitTicks(30);
				shot(ctx, "row");
				// the same row at night: the lit parts of every station glow
				s.runCommand("time set 18000");
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f 0 30", STATIONS.size() * 1.5 - 1.0, y + 3.2, -7.5));
				ctx.waitTicks(40);
				shot(ctx, "night");
				s.runCommand("time set 1000");
				s.runCommand("gamemode creative @a");
				ctx.waitTicks(10);
			}
			for (int i = 0; i < STATIONS.size(); i++) {
				String id = STATIONS.get(i);
				if (!only.isEmpty() && !only.contains(id)) continue;
				BlockPos pos = new BlockPos(i * 3, y, 0);
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f 0 30", i * 3 + 0.5, (double) y, -1.5));
				ctx.waitTicks(5);
				s.runOnServer(srv -> {
					ServerPlayer p = player(srv);
					Vec3 hit = Vec3.atCenterOf(pos).add(0, 0, -0.5);
					p.gameMode.useItemOn(p, p.level(), p.getItemInHand(InteractionHand.MAIN_HAND), InteractionHand.MAIN_HAND, new BlockHitResult(hit, Direction.NORTH, pos, false));
				});
				ctx.waitTicks(30);
				boolean open = s.computeOnServer(srv -> player(srv).containerMenu instanceof StationMenu);
				if (!open) throw new AssertionError("the " + id + " screen did not open");
				if (id.equals("matrix_workbench")) {
					// the World 1 Seed's drawer lays its pattern on the grid; the result must show
					String err = s.computeOnServer(srv -> {
						ServerPlayer p = player(srv);
						StationMenu m = (StationMenu) p.containerMenu;
						var list = fr.achedon12.matriochka.content.Recipes.of("matrix_workbench");
						int idx = -1;
						for (int k = 0; k < list.size(); k++) if (list.get(k).output().equals("seed_1")) idx = k;
						m.clickMenuButton(p, idx);
						return m.slots.get(m.resultSlot).getItem().is(ModContent.item("seed_1")) ? "" : "no Seed in the result slot";
					});
					if (!err.isEmpty()) throw new AssertionError(err);
				}
				ctx.waitTicks(20);
				ctx.getInput().setCursorPos(0, 0);
				shot(ctx, "screen_" + id);
				ctx.setScreen(() -> null);
				ctx.waitTicks(5);
			}
			Matriochka.LOG.info("[machines] ok");
		}
	}
}
