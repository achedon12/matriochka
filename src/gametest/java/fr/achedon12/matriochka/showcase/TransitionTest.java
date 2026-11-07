package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Worlds;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The dive into a World Block and the climb back out: ./gradlew runClientGameTest -Ptransition. Uses a World Block
 * and then the Threshold through the player's own right click, photographs the doll-shaped iris while it closes and
 * while it opens on the other side, and checks the player really arrived. Shots: transition_*.png.
 */
final class TransitionTest {
	private TransitionTest() {}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of("transition_" + name).withSize(1600, 900).disableCounterPrefix());
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			McTest.waitForChunks(sp);
			for (String c : List.of("gamerule advance_time false", "time set 6000", "gamerule spawn_monsters false", "gamemode creative @a")) s.runCommand(c);
			ctx.setScreen(() -> null);
			BlockPos block = s.computeOnServer(srv -> {
				ServerPlayer p = srv.getPlayerList().getPlayers().get(0);
				var lvl = srv.overworld();
				MatrioData.get(srv).markDefeated(MatrioData.get(srv).groupOf(p.getUUID()), 0);
				BlockPos at = p.blockPosition().offset(0, 0, 2);
				lvl.setBlock(at, ModContent.block("world_block").defaultBlockState(), 3);
				if (lvl.getBlockEntity(at) instanceof DataBlockEntity be) {
					be.data().putInt("world", 1);
					be.data().putString("owner", p.getUUID().toString());
					be.changed();
				}
				return at;
			});
			ctx.waitTicks(20);
			s.runOnServer(srv -> {
				ServerPlayer p = srv.getPlayerList().getPlayers().get(0);
				p.gameMode.useItemOn(p, srv.overworld(), p.getMainHandItem(), InteractionHand.MAIN_HAND,
					new BlockHitResult(Vec3.atCenterOf(block), Direction.NORTH, block, false));
			});
			ctx.waitTicks(11);
			shot(ctx, "dive_closing");
			ctx.waitTicks(2);
			shot(ctx, "dive_closing2");
			ctx.waitTicks(4);
			shot(ctx, "dive_closed");
			ctx.waitTicks(40);
			McTest.waitForChunks(sp);
			ctx.waitTicks(4);
			shot(ctx, "arrive_opening");
			ctx.waitTicks(12);
			shot(ctx, "arrive_open");
			int world = s.computeOnServer(srv -> Worlds.number(srv.getPlayerList().getPlayers().get(0).level()));
			if (world != 1) throw new AssertionError("the dive did not lead into World 1 (in world " + world + ")");
			// and back out through the Threshold under the player's feet
			s.runOnServer(srv -> {
				ServerPlayer p = srv.getPlayerList().getPlayers().get(0);
				BlockPos seuil = p.blockPosition().below();
				p.gameMode.useItemOn(p, p.level(), p.getMainHandItem(), InteractionHand.MAIN_HAND,
					new BlockHitResult(Vec3.atCenterOf(seuil).add(0, 0.5, 0), Direction.UP, seuil, false));
			});
			ctx.waitTicks(8);
			shot(ctx, "climb_closing");
			ctx.waitTicks(50);
			McTest.waitForChunks(sp);
			ctx.waitTicks(6);
			shot(ctx, "climb_opening");
			int back = s.computeOnServer(srv -> Worlds.number(srv.getPlayerList().getPlayers().get(0).level()));
			if (back != 0) throw new AssertionError("the Threshold did not lead back to the Surface (in world " + back + ")");
			Matriochka.LOG.info("[transition] ok");
		}
	}
}
