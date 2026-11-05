package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Builds the boss arena of a parcel: a round painted floor, a ring of pillars and the arena altar. */
public final class Arenas {
	public static final int RADIUS = 18;

	private Arenas() {}

	public static void build(ServerLevel level, int world, BlockPos center) {
		BlockState floor = floorFor(world);
		BlockState ring = ModContent.block("lacquer_block").defaultBlockState();
		BlockState pillar = ModContent.block("painted_wood").defaultBlockState();
		int height = Worlds.ceiling(world) ? 14 : 18;
		for (int dx = -RADIUS - 1; dx <= RADIUS + 1; dx++) {
			for (int dz = -RADIUS - 1; dz <= RADIUS + 1; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz);
				if (d > RADIUS + 1) continue;
				for (int dy = -3; dy <= -1; dy++) level.setBlock(center.offset(dx, dy, dz), dy == -1 ? (d > RADIUS - 1 ? ring : floor) : floor, 2);
				for (int dy = 0; dy < height; dy++) {
					BlockPos p = center.offset(dx, dy, dz);
					if (!level.getBlockState(p).isAir() && !(world == 7 && level.getBlockState(p).is(Blocks.WATER))) {
						level.setBlock(p, world == 7 && p.getY() < 150 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState(), 2);
					}
				}
				if (Worlds.ceiling(world)) level.setBlock(center.offset(dx, height, dz), floor, 2);
			}
		}
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			BlockPos p = center.offset((int) Math.round(Math.cos(a) * (RADIUS - 2)), 0, (int) Math.round(Math.sin(a) * (RADIUS - 2)));
			for (int dy = 0; dy < 5; dy++) level.setBlock(p.above(dy), pillar, 2);
			level.setBlock(p.above(5), Blocks.LANTERN.defaultBlockState(), 2);
		}
		level.setBlock(center, ModContent.block("arena_altar").defaultBlockState(), 3);
		// a path of lanterns from the threshold
		for (int z = 8; z < Worlds.ARENA_OFFSET - RADIUS; z += 12) {
			BlockPos p = center.offset(0, 0, -Worlds.ARENA_OFFSET + z);
			int y = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.getX(), p.getZ());
			if (!Worlds.ceiling(world) && world != 7 && world != 4) {
				level.setBlock(new BlockPos(p.getX(), y, p.getZ()), pillar, 2);
				level.setBlock(new BlockPos(p.getX(), y + 1, p.getZ()), Blocks.LANTERN.defaultBlockState(), 2);
			}
		}
	}

	public static BlockState floorFor(int world) {
		String id = switch (world) {
			case 1 -> "rootstone";
			case 2 -> "ashrock";
			case 3 -> "dungeon_brick";
			case 4 -> "cloudstone";
			case 5 -> "umbral_stone";
			case 6 -> "inverted_stone";
			case 7 -> "trench_rock";
			case 8 -> "hourstone";
			case 9 -> "living_rock";
			case 10 -> "giant_plank";
			default -> "painted_wood";
		};
		return ModContent.block(id).defaultBlockState();
	}
}
