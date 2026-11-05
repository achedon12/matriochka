package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * The boss stage of a parcel, built once when the parcel is created. Altar bosses get a decorated round arena around the
 * arena altar; lair bosses get their own lair instead ({@link Lairs}).
 */
public final class Arenas {
	public static final int RADIUS = 18;
	/** Radius of the ring of light inlaid in the arena floor (the offering ritual draws over it). */
	public static final int RING = 13;

	private Arenas() {}

	/** Builds the stage of a world's boss around {@code center} (the arena centre, 160 blocks south of the Threshold). */
	public static void build(ServerLevel level, int world, BlockPos center) {
		boolean lair = world > 0 && ModContent.bossForWorld(world).lair();
		if (lair) Lairs.build(level, world, center);
		else buildArena(level, world, center);
		path(level, world, center, lair ? Lairs.GATE + 8 : RADIUS + 3);
	}

	/** The round arena of an altar boss: inlaid floor, colonnade, braziers, an entrance arch and the altar on its dais. */
	public static void buildArena(ServerLevel level, int world, BlockPos center) {
		BlockState floor = floorFor(world);
		BlockState trim = trimFor(world);
		BlockState accent = accentFor(world);
		BlockState ring = ModContent.block("lacquer_block").defaultBlockState();
		BlockState lacquer = ring;
		boolean ceiling = Worlds.ceiling(world);
		int height = ceiling ? 14 : 18;
		for (int dx = -RADIUS - 1; dx <= RADIUS + 1; dx++) {
			for (int dz = -RADIUS - 1; dz <= RADIUS + 1; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz);
				if (d > RADIUS + 1) continue;
				double a = Math.atan2(dz, dx);
				BlockState top;
				if (d > RADIUS - 1) top = ring;
				else if (Math.abs(d - RING) < 0.55) top = accent;
				else if (Math.abs(d - RING - 1.5) < 0.5 || Math.abs(d - RING + 1.5) < 0.5) top = trim;
				else if (d <= 3.6) top = lacquer;
				else if (d >= 4.5 && d <= RING - 2 && spoke(a, d)) top = trim;
				else if (d > RING + 2 && ((Math.floorDiv(dx, 2) + Math.floorDiv(dz, 2)) & 1) == 0) top = trim;
				else top = floor;
				for (int dy = -3; dy <= -1; dy++) level.setBlock(center.offset(dx, dy, dz), dy == -1 ? top : floor, 2);
				for (int dy = 0; dy < height; dy++) {
					BlockPos p = center.offset(dx, dy, dz);
					if (!level.getBlockState(p).isAir() && !(world == 7 && level.getBlockState(p).is(Blocks.WATER))) {
						level.setBlock(p, world == 7 && p.getY() < 150 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState(), 2);
					}
				}
				if (ceiling) level.setBlock(center.offset(dx, height, dz), Math.floorMod(dx, 6) == 0 && Math.floorMod(dz, 6) == 0 ? accent : floor, 2);
				// a low balustrade with merlons around the rim, open toward the Threshold
				if (d > RADIUS - 0.5 && !(dz < 0 && Math.abs(dx) <= 2)) {
					level.setBlock(center.offset(dx, 0, dz), trim, 2);
					if (Math.floorMod(dx + dz, 3) == 0) level.setBlock(center.offset(dx, 1, dz), trim, 2);
				}
			}
		}
		// the dais and the altar
		for (int dx = -3; dx <= 3; dx++)
			for (int dz = -3; dz <= 3; dz++) if (dx * dx + dz * dz <= 6) level.setBlock(center.offset(dx, 0, dz), trim, 2);
		for (int[] o : new int[][]{{2, 2}, {-2, 2}, {2, -2}, {-2, -2}}) level.setBlock(center.offset(o[0], 1, o[1]), accent, 2);
		level.setBlock(center.above(), ModContent.block("arena_altar").defaultBlockState(), 3);
		// colonnade: twelve pillars, the one facing the Threshold replaced by the arch
		BlockState lantern = (world == 3 || world == 5 ? Blocks.SOUL_LANTERN : Blocks.LANTERN).defaultBlockState();
		for (int i = 0; i < 12; i++) {
			if (i == 9) continue;
			double a = i * Math.PI / 6;
			BlockPos p = center.offset((int) Math.round(Math.cos(a) * (RADIUS - 2)), 0, (int) Math.round(Math.sin(a) * (RADIUS - 2)));
			int top = ceiling ? height - 1 : 7;
			level.setBlock(p, lacquer, 2);
			for (int dy = 1; dy <= top; dy++) level.setBlock(p.above(dy), dy == 6 ? accent : trim, 2);
			if (!ceiling) level.setBlock(p.above(top + 1), lantern, 2);
			else level.setBlock(p.offset(-(int) Math.round(Math.cos(a)), top, -(int) Math.round(Math.sin(a))), lantern.setValue(LanternBlock.HANGING, true), 2);
		}
		// braziers on the diagonals
		BlockState fire = (world == 3 || world == 5 ? Blocks.SOUL_CAMPFIRE : Blocks.CAMPFIRE).defaultBlockState();
		for (int[] o : new int[][]{{7, 7}, {-7, 7}, {7, -7}, {-7, -7}}) {
			level.setBlock(center.offset(o[0], 0, o[1]), trim, 2);
			level.setBlock(center.offset(o[0], 1, o[1]), world == 7 ? accent : fire, 2);
		}
		// the entrance arch, facing the Threshold
		int az = -RADIUS - 1;
		for (int dy = 0; dy <= 8; dy++) {
			level.setBlock(center.offset(-3, dy, az), dy == 8 ? accent : trim, 2);
			level.setBlock(center.offset(3, dy, az), dy == 8 ? accent : trim, 2);
		}
		for (int dx = -3; dx <= 3; dx++) level.setBlock(center.offset(dx, 9, az), dx == 0 ? accent : lacquer, 2);
		for (int dx : new int[]{-2, 2}) level.setBlock(center.offset(dx, 8, az), lantern.setValue(LanternBlock.HANGING, true), 2);
	}

	private static boolean spoke(double a, double d) {
		for (int k = 0; k < 8; k++) if (Math.abs(Math.sin(a - k * Math.PI / 4)) * d < 0.6 && Math.cos(a - k * Math.PI / 4) > 0) return true;
		return false;
	}

	/** A trail from the Threshold to the stage: lantern posts on open ground, a gallery in the Lightless Deep, sunken lights at sea. */
	private static void path(ServerLevel level, int world, BlockPos center, int stop) {
		BlockState pillar = ModContent.block("painted_wood").defaultBlockState();
		if (world == 5) {
			// a gallery dug from the Threshold to the lair's forecourt; no light in the Lightless Deep
			BlockState stone = ModContent.block("umbral_stone").defaultBlockState();
			for (int z = 4 - Worlds.ARENA_OFFSET; z <= -stop; z++) {
				for (int dx = -2; dx <= 2; dx++) {
					for (int dy = 0; dy <= 4; dy++) {
						BlockPos p = center.offset(dx, dy, z);
						boolean shell = Math.abs(dx) == 2 && dy == 4;
						if (shell) continue;
						if (!level.getBlockState(p).isAir()) level.setBlock(p, Blocks.AIR.defaultBlockState(), 2);
					}
					BlockPos f = center.offset(dx, -1, z);
					if (level.getBlockState(f).isAir()) level.setBlock(f, stone, 2);
				}
			}
			return;
		}
		for (int z = 8; z < Worlds.ARENA_OFFSET - stop; z += 12) {
			BlockPos p = center.offset(0, 0, -Worlds.ARENA_OFFSET + z);
			if (world == 7) {
				// lights just under the surface, leading to the beacon pillars of the sunken temple
				level.setBlock(new BlockPos(p.getX(), 148, p.getZ()), Blocks.SEA_LANTERN.defaultBlockState(), 2);
				continue;
			}
			int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.getX(), p.getZ());
			if (!Worlds.ceiling(world) && world != 4) {
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

	/** The world's light-giving block (the inlaid ring, pillar capitals, lair lights). */
	public static BlockState accentFor(int world) {
		String id = switch (world) {
			case 1 -> "spore_bloom"; case 2 -> "ember_stone"; case 3 -> "cold_lamp"; case 4 -> "storm_glass"; case 5 -> "faint_glow";
			case 6 -> "prism_moss"; case 7 -> "pressure_coral"; case 8 -> "temporal_sand_block"; case 9 -> "pulse_vein"; case 10 -> "lacquer_glow";
			default -> "lacquer_block";
		};
		return ModContent.block(id).defaultBlockState();
	}

	/** A dressed stone that reads against the world's floor: pillars, inlays, the balustrade. */
	public static BlockState trimFor(int world) {
		return switch (world) {
			case 1 -> Blocks.MOSSY_STONE_BRICKS.defaultBlockState();
			case 2 -> Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
			case 3 -> ModContent.block("sealed_brick").defaultBlockState();
			case 4 -> Blocks.QUARTZ_BRICKS.defaultBlockState();
			case 5 -> Blocks.POLISHED_DEEPSLATE.defaultBlockState();
			case 6 -> Blocks.PURPUR_BLOCK.defaultBlockState();
			case 7 -> Blocks.PRISMARINE_BRICKS.defaultBlockState();
			case 8 -> Blocks.TUFF_BRICKS.defaultBlockState();
			case 9 -> ModContent.block("flesh_stone").defaultBlockState();
			case 10 -> ModContent.block("painted_wood").defaultBlockState();
			default -> Blocks.CHISELED_STONE_BRICKS.defaultBlockState();
		};
	}
}
