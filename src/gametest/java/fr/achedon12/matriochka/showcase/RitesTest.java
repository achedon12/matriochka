package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.MatrioData;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The way into Worlds 2 to 10: ./gradlew runClientGameTest -Prites. For each world it builds the smallest scene its
 * rite asks for (lava and Ashrock, an iron door on redstone, a lightning rod, a dark room of Spent Glow, two glass
 * blocks, a deep pool, grass at dawn, stone under y 40, open ground), sets the object down through the player's own
 * right click, checks the rite waits while its condition is missing where it can be, then that it hatches into its
 * world's World Block. Shots: rites_<world>.png. Fails the run on the first failed check.
 */
final class RitesTest {
	private RitesTest() {}

	private static final List<String> REPORT = new ArrayList<>();

	private static void check(boolean ok, String what) {
		REPORT.add((ok ? "ok   " : "FAIL ") + what);
		Matriochka.LOG.info("[rites] {}{}", ok ? "ok   " : "FAIL ", what);
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	/** Builds the scene of a rite round its spot and returns the block to click (its top face, or the pool floor). */
	static BlockPos scene(ServerLevel l, int world, BlockPos spot) {
		BlockPos below = spot.below();
		// a clean stone pad with air above
		for (int x = -4; x <= 4; x++)
			for (int z = -4; z <= 4; z++) {
				l.setBlock(below.offset(x, 0, z), Blocks.STONE.defaultBlockState(), 3);
				for (int y = 0; y < 6; y++) l.setBlock(spot.offset(x, y, z), Blocks.AIR.defaultBlockState(), 3);
			}
		switch (world) {
			case 2 -> {
				l.setBlock(spot.offset(2, -1, 0), Blocks.LAVA.defaultBlockState(), 3);
				for (BlockPos p : List.of(spot.offset(-1, 0, -1), spot.offset(1, 0, -1), spot.offset(-1, 0, 1), spot.offset(1, 0, 1)))
					l.setBlock(p, ModContent.block("ashrock").defaultBlockState(), 3);
			}
			case 3 -> {
				l.setBlock(below, Blocks.REDSTONE_BLOCK.defaultBlockState(), 3);
				l.setBlock(spot.east(), Blocks.IRON_DOOR.defaultBlockState(), 3);
				l.setBlock(spot.east().above(), Blocks.IRON_DOOR.defaultBlockState().setValue(DoorBlock.HALF, net.minecraft.world.level.block.state.properties.DoubleBlockHalf.UPPER), 3);
			}
			case 4 -> {
				l.setBlock(spot, net.minecraft.core.registries.BuiltInRegistries.BLOCK.getValue(net.minecraft.resources.Identifier.withDefaultNamespace("lightning_rod")).defaultBlockState(), 3);
				return spot;
			}
			case 5 -> {
				// a sealed stone room, Spent Glow on the floor round the spot
				for (int x = -3; x <= 3; x++)
					for (int z = -3; z <= 3; z++)
						for (int y = -1; y <= 3; y++)
							if (Math.abs(x) == 3 || Math.abs(z) == 3 || y == -1 || y == 3) l.setBlock(spot.offset(x, y, z), Blocks.STONE.defaultBlockState(), 3);
				for (BlockPos p : List.of(spot.offset(-2, -1, 0), spot.offset(2, -1, 0), spot.offset(0, -1, -2), spot.offset(0, -1, 2)))
					l.setBlock(p, ModContent.block("spent_glow").defaultBlockState(), 3);
			}
			case 6 -> {
				l.setBlock(spot.offset(-2, 0, 0), Blocks.GLASS.defaultBlockState(), 3);
				l.setBlock(spot.offset(2, 0, 0), Blocks.GLASS.defaultBlockState(), 3);
			}
			case 7 -> {
				// a basin three blocks deep; the pearl is dropped on its floor
				for (int x = -2; x <= 2; x++)
					for (int z = -2; z <= 2; z++)
						for (int y = -1; y <= 3; y++) {
							boolean wall = Math.abs(x) == 2 || Math.abs(z) == 2 || y == -1;
							l.setBlock(spot.offset(x, y, z), wall ? Blocks.STONE.defaultBlockState() : y < 3 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState(), 3);
						}
			}
			case 8 -> l.setBlock(below, Blocks.GRASS_BLOCK.defaultBlockState(), 3);
			default -> {}
		}
		return below;
	}

	static void run(ClientGameTestContext ctx) {
		REPORT.clear();
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			McTest.waitForChunks(sp);
			for (String c : List.of("gamerule advance_weather false", "weather clear", "gamerule spawn_monsters false", "gamerule advance_time false",
				"time set 23000", "gamemode creative @a")) s.runCommand(c);
			ctx.setScreen(() -> null);
			// the group has beaten every boss, so every rite is unlocked
			s.runOnServer(srv -> {
				MatrioData md = MatrioData.get(srv);
				String g = md.groupOf(player(srv).getUUID());
				for (int w = 0; w <= 10; w++) md.markDefeated(g, w);
			});
			int surface = s.computeOnServer(srv -> srv.overworld().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, 0, 0)) + 30;
			for (int world = 2; world <= 10; world++) {
				final int w = world;
				// the stake goes below y 40, the lantern in a sealed room; the others on a pad in the air
				BlockPos spot = new BlockPos((world - 2) * 14, w == 9 ? 30 : w == 5 ? 20 : surface, 40);
				String placed = s.computeOnServer(srv -> {
					ServerLevel l = srv.overworld();
					BlockPos click = scene(l, w, spot);
					ServerPlayer p = player(srv);
					p.teleportTo(spot.getX() + 0.5, spot.getY() + 1, spot.getZ() - 3.5);
					p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("seed_" + w)));
					Vec3 hit = Vec3.atCenterOf(click).add(0, 0.5, 0);
					p.gameMode.useItemOn(p, l, p.getMainHandItem(), InteractionHand.MAIN_HAND, new BlockHitResult(hit, Direction.UP, click, false));
					BlockPos at = w == 4 ? spot.above() : spot;
					return l.getBlockState(at).is(ModContent.block("planted_seed")) ? "" : "no rite site at " + at.toShortString() + " (" + l.getBlockState(at) + ")";
				});
				check(placed.isEmpty(), "the World " + w + " object is set down " + placed);
				if (!placed.isEmpty()) continue;
				BlockPos at = w == 4 ? spot.above() : spot;
				if (w == 4) {
					// no storm: it waits, until a Storm Essence is fed to it
					ctx.waitTicks(240);
					boolean waiting = s.computeOnServer(srv -> srv.overworld().getBlockState(at).is(ModContent.block("planted_seed")));
					check(waiting, "the Storm Rod waits without a storm");
					s.runOnServer(srv -> {
						ServerPlayer p = player(srv);
						p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("storm_essence")));
						p.gameMode.useItemOn(p, srv.overworld(), p.getMainHandItem(), InteractionHand.MAIN_HAND,
							new BlockHitResult(Vec3.atCenterOf(at), Direction.NORTH, at, false));
					});
				}
				ctx.waitTicks(60);
				s.runCommand(String.format(java.util.Locale.ROOT, "tp @a %.2f %.2f %.2f 0 25", at.getX() + 0.5, at.getY() + 1.6, at.getZ() - 2.6));
				ctx.waitTicks(20);
				ctx.runOnClient(mc -> { if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
				ctx.takeScreenshot(TestScreenshotOptions.of("rites_" + w).withSize(1600, 900).disableCounterPrefix());
				ctx.runOnClient(mc -> { if (fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
				ctx.waitTicks(200);
				String opened = s.computeOnServer(srv -> {
					var st = srv.overworld().getBlockState(at);
					if (!st.is(ModContent.block("world_block"))) return "found " + st;
					return srv.overworld().getBlockEntity(at) instanceof DataBlockEntity be && be.data().getIntOr("world", 0) == w ? "" : "a World Block of the wrong world";
				});
				check(opened.isEmpty(), "the World " + w + " rite opens its World Block " + opened);
			}
		}
		long failed = REPORT.stream().filter(r -> r.startsWith("FAIL")).count();
		Matriochka.LOG.info("[rites] {} checks, {} failed", REPORT.size(), failed);
		if (failed > 0) throw new AssertionError(failed + " rite checks failed:\n" + String.join("\n", REPORT));
	}
}
