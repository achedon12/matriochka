package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * World 7, the Pressure Ocean: the sea fills the world from its floor up to {@link #SEA_LEVEL} (the generator writes
 * the same value, see OCEAN_SEA in tools/gen.py). The player arrives in a diving chamber on the sea floor: a glass
 * dome full of air with a door that holds the water back.
 */
public final class Ocean {
	public static final int WORLD = 7;
	public static final int SEA_LEVEL = 240;
	/** The Threshold sits on the sea floor, within these heights (a chamber over a trench stands on legs). */
	public static final int THRESHOLD_MIN = 124, THRESHOLD_MAX = 200;
	/** The Leviathan's temple is sunk this far below the level of the Threshold, in a trench cut for it. */
	public static final int LAIR_SINK = 10;
	/** Radius of the diving chamber's dome. */
	public static final int CHAMBER = 6;
	/** Depth below which the pressure hurts without protection, and what each piece of protection gives back. */
	public static final int PRESSURE_Y = 110, PER_DIVING_PIECE = 22;

	private Ocean() {}

	/** Height of the sea floor (first block that is not solid) at a column. */
	public static int floor(ServerLevel level, int x, int z) {
		return level.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z);
	}

	/** Where the Threshold goes for a parcel centre: on the sea floor, kept out of the trenches and off the reefs. */
	public static int thresholdY(ServerLevel level, BlockPos center) {
		return Math.max(THRESHOLD_MIN, Math.min(THRESHOLD_MAX, floor(level, center.getX(), center.getZ())));
	}

	/**
	 * The diving chamber around the Threshold at {@code base} (the Threshold block itself; the player stands on top):
	 * a glass dome full of air ribbed with prismarine, a floor of lacquer and painted wood, lanterns, a door that keeps
	 * the sea out, a stocked chest and an air vent just outside to show where helmets refill.
	 */
	public static void buildChamber(ServerLevel level, BlockPos base) {
		BlockState glass = Blocks.GLASS.defaultBlockState();
		BlockState rib = Blocks.DARK_PRISMARINE.defaultBlockState();
		BlockState trim = Blocks.PRISMARINE_BRICKS.defaultBlockState();
		BlockState rock = ModContent.block("trench_rock").defaultBlockState();
		BlockState lacquer = ModContent.block("lacquer_block").defaultBlockState();
		BlockState wood = ModContent.block("painted_wood").defaultBlockState();
		BlockState air = Blocks.AIR.defaultBlockState();
		int r = CHAMBER;
		for (int dx = -r - 1; dx <= r + 1; dx++) {
			for (int dz = -r - 1; dz <= r + 1; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz);
				if (d > r + 0.5) continue;
				// footing down to the sea floor, so the chamber never floats over a dip
				for (int dy = -2; dy > -40; dy--) {
					BlockPos q = base.offset(dx, dy, dz);
					BlockState s = level.getBlockState(q);
					if (!s.isAir() && s.getFluidState().isEmpty() && dy < -2) break;
					level.setBlock(q, d > r - 0.5 ? trim : rock, 2);
				}
				level.setBlock(base.offset(dx, -1, dz), d > r - 0.5 ? trim : (d > r - 1.5 ? wood : lacquer), 2);
				for (int h = 0; h <= r + 1; h++) {
					double dd = Math.sqrt(dx * dx + dz * dz + h * h);
					BlockPos q = base.offset(dx, h, dz);
					if (dd > r + 0.5) continue;
					if (dd > r - 0.6) level.setBlock(q, (dx == 0 || dz == 0 || h == 0) ? rib : glass, 2);
					else level.setBlock(q, air, 2);
				}
			}
		}
		level.setBlock(base.above(r), Blocks.SEA_LANTERN.defaultBlockState(), 2);
		for (int[] o : new int[][]{{3, 3}, {-3, 3}, {3, -3}, {-3, -3}}) {
			level.setBlock(base.offset(o[0], 0, o[1]), Blocks.LANTERN.defaultBlockState(), 2);
		}
		// the door toward the boss (south, +Z): doors hold water back, so the sea stays outside when it opens
		BlockPos door = base.offset(0, 0, r);
		level.setBlock(door.below(), trim, 2);
		BlockState lower = Blocks.DARK_OAK_DOOR.defaultBlockState().setValue(DoorBlock.FACING, Direction.NORTH).setValue(DoorBlock.HALF, DoubleBlockHalf.LOWER);
		level.setBlock(door, lower, 2);
		level.setBlock(door.above(), lower.setValue(DoorBlock.HALF, DoubleBlockHalf.UPPER), 2);
		level.setBlock(door.above(2), rib, 2);
		level.setBlock(door.offset(-1, 2, 0), Blocks.SEA_LANTERN.defaultBlockState(), 2);
		level.setBlock(door.offset(1, 2, 0), Blocks.SEA_LANTERN.defaultBlockState(), 2);
		// a chest of supplies for the first dive
		BlockPos chest = base.offset(-3, 0, 0);
		level.setBlock(chest, Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, Direction.EAST), 2);
		if (level.getBlockEntity(chest) instanceof ChestBlockEntity c) {
			c.setItem(0, new ItemStack(ModContent.item("oxygen_capsule"), 4));
			c.setItem(1, new ItemStack(ModContent.item("apnea_kelp"), 3));
			c.setItem(2, new ItemStack(net.minecraft.world.item.Items.IRON_PICKAXE));
		}
		level.setBlock(base.offset(3, 0, 0), Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, false), 2);
		// an air vent on the sea floor a few strides out of the door
		BlockPos vent = base.offset(2, 0, r + 4);
		int fy = floor(level, vent.getX(), vent.getZ());
		BlockPos v = new BlockPos(vent.getX(), Math.min(fy, base.getY()), vent.getZ());
		level.setBlock(v.below(), rock, 2);
		level.setBlock(v, ModContent.block("air_vent").defaultBlockState(), 2);
	}
}
