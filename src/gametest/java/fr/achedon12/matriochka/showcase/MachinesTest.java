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
		ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
		ctx.waitTicks(2);
		ctx.takeScreenshot(TestScreenshotOptions.of("machines_" + name).withSize(1600, 900).disableCounterPrefix());
		ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
	}

	static void run(ClientGameTestContext ctx) {
		String only = System.getProperty("matriochka.only", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			sp.getConnection().waitForChunksRender();
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
			sp.getConnection().waitForChunksRender();
			for (int i = 0; i < STATIONS.size(); i++) {
				String id = STATIONS.get(i);
				if (!only.isEmpty() && !only.contains(id)) continue;
				// three quarters from the front-left, a little above
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f -35 28", i * 3 + 0.5 - 1.0, y + 0.55, -1.15));
				ctx.waitTicks(25);
				shot(ctx, id);
			}
			if (only.isEmpty()) {
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f 0 24", STATIONS.size() * 1.5 - 1.0, y + 4.5, -13.0));
				ctx.waitTicks(30);
				shot(ctx, "row");
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
