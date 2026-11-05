package fr.achedon12.matriochka.structure;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/**
 * The lacquered stage of the Trials, inside the Refuge doll: a round arena painted in the materials of the world being
 * fought, ringed by a wall of pillars, braziers and banners, with a raised dais where the boss wakes and a gilt gate on
 * the players' side. An invisible dome keeps everyone in. Rebuilt for every world of the Gauntlet.
 */
public final class TrialStage {
	/** Radius of the fighting floor. */
	public static final int R = 18;
	/** Height of the invisible dome above the floor. */
	public static final int DOME = 26;

	private TrialStage() {}

	public static BoundingBox box(BlockPos c) {
		return new BoundingBox(c.getX() - R - 4, c.getY() - 4, c.getZ() - R - 4, c.getX() + R + 4, c.getY() + DOME + 2, c.getZ() + R + 4);
	}

	/** Where the players stand when a stage opens: before the gate, facing the dais. */
	public static BlockPos entry(BlockPos c) {
		return c.offset(0, 1, -R + 3);
	}

	/** Where the boss wakes and the waves come from. */
	public static BlockPos dais(BlockPos c) {
		return c.offset(0, 3, 6);
	}

	/** Paints the stage for a world (0 for the Surface) around the centre c (c is the floor level). */
	public static void build(ServerLevel level, BlockPos c, int world) {
		BoundingBox box = box(c);
		Kit k = new Kit(level, box, box, c, 0x7A1A15L + world * 977L, world, R, 10, "trial_stage", "decor", "large", "trial");
		Palette p = k.p;
		BlockState barrier = Blocks.BARRIER.defaultBlockState();
		// wipe the previous stage: true air everywhere, the floor and its foundation again
		k.dry(-R - 3, -3, -R - 3, R + 3, DOME + 1, R + 3);
		k.cyl(0, 0, R + 2.5, -3, -2, p.found);
		k.disc(0, -1, 0, R + 2.5, p.base);
		k.roundFloor(0, 0, 0, R + 0.5);
		// the inside of the ring: open air, or the sea in the Pressure Ocean (water for the Leviathan to swim in)
		for (int y = 1; y <= 7; y++) k.disc(0, y, 0, R, p.fill);
		// ring wall: courses of the world's stone, a trim band and a crenellated cap
		for (int x = -R - 2; x <= R + 2; x++)
			for (int z = -R - 2; z <= R + 2; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d <= R + 0.5 || d > R + 2.5) continue;
				for (int y = 1; y <= 7; y++) k.set(x, y, z, y == 1 ? p.trim : y == 4 ? p.alt : p.base);
				k.set(x, 8, z, (x + z) % 2 == 0 ? p.cap : p.slab);
			}
		// twelve pillars standing out of the wall, a lantern on each, banners and braziers between them
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6;
			int px = (int) Math.round(Math.cos(a) * (R - 0.5)), pz = (int) Math.round(Math.sin(a) * (R - 0.5));
			k.pillar(px, 1, pz, 8, false);
			k.lanternOn(px, 9, pz);
			double b = a + Math.PI / 12;
			int bx = (int) Math.round(Math.cos(b) * (R - 0.2)), bz = (int) Math.round(Math.sin(b) * (R - 0.2));
			Direction in = Kit.inward(bx, bz);
			if (i % 2 == 0) k.banner(bx, 5, bz, in, i % 4 == 0 ? p.colA : p.colB);
			else k.brazier(bx, 1, bz);
		}
		// the dais: two stepped rings of slabs and an inlaid rosette where the boss wakes
		k.disc(0, 1, 6, 4.2, p.trim);
		k.ring(0, 1, 6, 4.5, Kit.slabOf(p.slab, false));
		k.disc(0, 2, 6, 2.4, p.inlay);
		k.set(0, 2, 6, p.inlay2);
		for (Direction d : Direction.Plane.HORIZONTAL) k.set(d.getStepX() * 3, 2, 6 + d.getStepZ() * 3, Kit.slabOf(p.slab, false));
		// the players' gate: a gilt arch in the wall behind them, shut
		for (int x = -2; x <= 2; x++) {
			for (int y = 1; y <= 4; y++) k.set(x, y, -R - 1, Math.abs(x) == 2 || y == 4 ? p.cap : Blocks.GOLD_BLOCK.defaultBlockState());
			k.set(x, 5, -R - 1, p.trim);
		}
		k.lanternOn(-3, 1, -R + 1);
		k.lanternOn(3, 1, -R + 1);
		k.runner(-1, -R + 1, 1, -R + 6, 1);
		// lights over the floor so the fight is readable even in the darkest worlds
		for (int i = 0; i < 4; i++) {
			double a = Math.PI / 4 + i * Math.PI / 2;
			k.lampPost((int) Math.round(Math.cos(a) * 11), 1, (int) Math.round(Math.sin(a) * 11), 3);
		}
		// the invisible dome
		for (int x = -R - 1; x <= R + 1; x++)
			for (int z = -R - 1; z <= R + 1; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > R + 1.5) continue;
				if (d > R + 0.5) for (int y = 9; y <= DOME; y++) k.set(x, y, z, barrier);
				k.set(x, DOME + 1, z, barrier);
			}
		k.finish();
	}

	/** Clears everything the stage holds (after the last stage). */
	public static void clear(ServerLevel level, BlockPos c) {
		BoundingBox box = box(c);
		Kit k = new Kit(level, box, box, c, 1L, 0, R, 10, "trial_stage", "decor", "large", "trial");
		k.dry(-R - 3, -3, -R - 3, R + 3, DOME + 1, R + 3);
	}
}
