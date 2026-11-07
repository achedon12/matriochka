package fr.achedon12.matriochka.structure;

import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.BellBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BellAttachType;

/** Composite pieces shared by several archetypes: houses, round towers, fountains, statues, tents, stalls. */
final class Parts {
	private Parts() {}

	/**
	 * A furnished house over x0..x1 / z0..z1 from floor y0: plinth, quoins, framed storeys of four rows, windows with
	 * sills, a door with a step and a lantern, a gable roof along the long side and a chimney. style 0 masonry, 1 timber
	 * frame, 2 masonry ground floor and timber upper floors. Marks a hidden chest upstairs and one under the stair.
	 */
	static void house(Kit k, int x0, int z0, int x1, int z1, int y0, int floors, Direction door, int style) {
		Palette p = k.p;
		int top = y0 + floors * 4;
		k.air(x0 + 1, y0 + 1, z0 + 1, x1 - 1, top + 6, z1 - 1);
		k.box(x0, y0 - 1, z0, x1, y0 - 1, z1, p.found);
		for (int f = 0; f < floors; f++) {
			int fy = y0 + f * 4;
			boolean timber = style == 1 || (style == 2 && f > 0);
			k.floor(x0, z0, x1, z1, fy, f == 0 ? k.variant % 4 : 3);
			if (f > 0) k.box(x0 + 1, fy, z0 + 1, x1 - 1, fy, z1 - 1, p.plank);
			for (int x = x0; x <= x1; x++)
				for (int z = z0; z <= z1; z++) {
					boolean edgeX = x == x0 || x == x1, edgeZ = z == z0 || z == z1;
					if (!edgeX && !edgeZ) continue;
					boolean corner = edgeX && edgeZ;
					for (int ky = 0; ky < 4; ky++) {
						int y = fy + ky;
						BlockState s;
						if (corner) s = timber ? p.log : (ky == 0 ? p.trim : p.pillar);
						else if (ky == 0) s = timber && f > 0 ? Kit.axis(p.log, edgeX ? Direction.Axis.Z : Direction.Axis.X) : p.trim;
						else if (timber) s = ((edgeX ? z : x) % 3 == 0) ? p.log : p.plank;
						else s = ky == 3 ? p.alt : p.base;
						boolean win = (ky == 1 || ky == 2) && !corner && ((edgeX ? z - z0 : x - x0) % 3 == 2) && (edgeX ? z < z1 - 1 : x < x1 - 1);
						if (win) s = p.pane;
						k.set(x, y, z, s);
					}
					if (!corner && ((edgeX ? z - z0 : x - x0) % 3 == 2) && (edgeX ? z < z1 - 1 : x < x1 - 1)) {
						Direction out = edgeX ? (x == x0 ? Direction.WEST : Direction.EAST) : (z == z0 ? Direction.NORTH : Direction.SOUTH);
						k.stair(x + out.getStepX(), fy, z + out.getStepZ(), p.woodStair, out.getOpposite(), true);
					}
				}
		}
		// door on the given side, centred
		int dx = (x0 + x1) / 2, dz = (z0 + z1) / 2;
		int ex = door == Direction.WEST ? x0 : door == Direction.EAST ? x1 : dx;
		int ez = door == Direction.NORTH ? z0 : door == Direction.SOUTH ? z1 : dz;
		k.door(ex, y0 + 1, ez, door);
		k.set(ex, y0 + 3, ez, p.trim);
		k.stair(ex + door.getStepX(), y0, ez + door.getStepZ(), door.getOpposite(), false);
		Direction side = door.getClockWise();
		k.set(ex + door.getStepX() + side.getStepX(), y0 + 3, ez + door.getStepZ() + side.getStepZ(), p.lantern);
		// roof
		boolean alongX = (x1 - x0) >= (z1 - z0);
		k.gable(x0, z0, x1, z1, top, alongX, style == 0 ? p.base : p.plank);
		// chimney at the back corner
		int cx = door == Direction.WEST ? x1 - 1 : x0 + 1, cz = door == Direction.NORTH ? z1 - 1 : z0 + 1;
		int ridge = top + Math.min(x1 - x0, z1 - z0) / 2 + 2;
		for (int y = y0 + 1; y <= ridge; y++) k.set(cx, y, cz, y <= y0 + 1 ? p.trim : p.alt);
		k.set(cx, y0 + 1, cz, k.p.underwater ? p.light : Blocks.FURNACE.defaultBlockState());
		if (!p.underwater) k.set(cx, ridge + 1, cz, Blocks.CAMPFIRE.defaultBlockState());
		// ground floor furniture
		int ix0 = x0 + 1, ix1 = x1 - 1, iz0 = z0 + 1, iz1 = z1 - 1;
		int tx = (ix0 + ix1) / 2, tz = (iz0 + iz1) / 2;
		if (ix1 - ix0 >= 3 && iz1 - iz0 >= 3) {
			k.table(tx, y0 + 1, tz);
			k.chair(tx + 1, y0 + 1, tz, Direction.WEST);
			k.chair(tx - 1, y0 + 1, tz, Direction.EAST);
			k.carpet(tx, y0 + 1, tz + 1, p.colA);
			k.carpet(tx, y0 + 1, tz - 1, p.colA);
		}
		int bx = door == Direction.EAST ? ix0 : ix1, bz = door == Direction.SOUTH ? iz0 : iz1;
		k.barrel(bx, y0 + 1, bz, Direction.UP);
		k.set(bx, y0 + 2, bz, p.lantern);
		k.hang(tx, y0 + 3, tz, 0);
		// ladder to the upper floors in the corner opposite the chimney
		int lx = door == Direction.WEST ? x0 + 1 : x1 - 1, lz = door == Direction.NORTH ? z1 - 1 : z0 + 1;
		k.box(x0 + 1, top, z0 + 1, x1 - 1, top, z1 - 1, p.plank);
		Direction lf = lx == x1 - 1 ? Direction.WEST : Direction.EAST;
		for (int y = y0 + 1; y <= top; y++) k.set(lx, y, lz, Kit.ladderFacing(lf));
		for (int f = 1; f < floors; f++) {
			int fy = y0 + f * 4;
			k.bed(ix0 + (door == Direction.EAST ? 1 : 0), fy + 1, tz, Direction.NORTH, f % 2 == 0 ? p.colA : p.colB);
			k.shelves(ix1, iz0, ix1, iz0 + 1, fy + 1, 2);
			k.candles(ix1, fy + 3, iz0, 2);
			k.mark("hidden", ix1 - 1, fy + 1, iz1, Direction.NORTH);
			k.set(tx, fy + 3, tz, p.light);
		}
		// attic storage
		k.mark("hidden", tx, top + 1, tz, Direction.SOUTH);
		k.crates(ix0, top + 1, tz);
		k.mark("hidden", lx == ix0 ? ix0 + 1 : ix1 - 1, y0 + 1, lz, Direction.SOUTH);
	}

	/** Round tower: plinth ring, body with arrow slits, floors with ladders, a corbelled parapet and an optional cone. */
	static int roundTower(Kit k, int cx, int cz, int rad, int y0, int h, boolean cone) {
		Palette p = k.p;
		k.disc(cx, y0, cz, rad, p.trim);
		k.tube(cx, cz, rad, y0 + 1, y0 + h, p.base);
		k.ring(cx, y0 + 1, cz, rad, p.trim);
		for (int y = y0 + 4; y < y0 + h; y += 4) k.ring(cx, y, cz, rad, p.alt);
		for (int y = y0 + 5; y < y0 + h; y += 5) k.disc(cx, y, cz, rad - 1, p.plank);
		for (int y = y0 + 1; y <= y0 + h; y++) k.set(cx, y, cz + rad - 1, Kit.ladderFacing(Direction.NORTH));
		for (int y = y0 + 3; y < y0 + h - 1; y += 5) {
			k.set(cx + rad, y, cz, p.bars);
			k.set(cx - rad, y, cz, p.bars);
			k.set(cx, y, cz - rad, p.bars);
		}
		int top = y0 + h;
		k.disc(cx, top, cz, rad, p.trim);
		k.set(cx, top, cz + rad - 1, Kit.ladderFacing(Direction.NORTH));
		int ir = rad + 2;
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				if (!k.onRing(x, z, rad + 1)) continue;
				k.stair(cx + x, top, cz + z, Kit.inward(x, z), true);
				k.set(cx + x, top + 1, cz + z, ((x + z) & 1) == 0 ? p.wall : p.alt);
			}
		if (cone) return k.cone(cx, top + 2, cz, rad + 1, 1.4);
		k.lampPost(cx, top + 1, cz, 1);
		return top + 3;
	}

	/** Basin fountain: stair rim, liquid, a central column with the world light on top. */
	static void fountain(Kit k, int cx, int y, int cz, int rad) {
		Palette p = k.p;
		BlockState liquid = k.world == 2 ? Blocks.LAVA.defaultBlockState() : Blocks.WATER.defaultBlockState();
		int ir = rad + 1;
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad + 0.5) continue;
				k.set(cx + x, y - 1, cz + z, p.trim);
				if (d > rad - 0.5) k.stair(cx + x, y, cz + z, Kit.inward(x, z).getOpposite(), false);
				else k.set(cx + x, y, cz + z, p.underwater ? p.inlay : liquid);
			}
		for (int k2 = 0; k2 < 3; k2++) k.set(cx, y + k2, cz, k2 == 2 ? p.cap : p.pillar);
		k.set(cx, y + 3, cz, p.underwater ? p.light : p.accent);
		if (!p.underwater && k.world != 2) k.set(cx, y + 4, cz, Blocks.WATER.defaultBlockState());
		for (Direction d : Direction.Plane.HORIZONTAL) k.stair(cx + d.getStepX(), y + 2, cz + d.getStepZ(), d.getOpposite(), true);
	}

	/** Statue on a stepped plinth: legs, body, arms and head of the world's blocks, a light held up. */
	static void statue(Kit k, int cx, int y, int cz, Direction face) {
		Palette p = k.p;
		k.box(cx - 1, y, cz - 1, cx + 1, y, cz + 1, p.trim);
		for (Direction d : Direction.Plane.HORIZONTAL) {
			for (int s = -1; s <= 1; s++) {
				Direction side = d.getClockWise();
				k.stair(cx + d.getStepX() * 2 + side.getStepX() * s, y, cz + d.getStepZ() * 2 + side.getStepZ() * s, d.getOpposite(), false);
			}
		}
		k.set(cx, y + 1, cz, p.cap);
		Direction side = face.getClockWise();
		k.set(cx + side.getStepX(), y + 2, cz + side.getStepZ(), p.wall);
		k.set(cx - side.getStepX(), y + 2, cz - side.getStepZ(), p.wall);
		k.set(cx, y + 3, cz, p.alt);
		k.set(cx, y + 4, cz, p.alt);
		k.set(cx, y + 2, cz, p.alt);
		k.set(cx + side.getStepX(), y + 4, cz + side.getStepZ(), p.wall);
		k.set(cx + side.getStepX(), y + 5, cz + side.getStepZ(), p.light);
		k.set(cx - side.getStepX(), y + 4, cz - side.getStepZ(), Kit.stairOf(p.stair, side, true));
		k.set(cx, y + 5, cz, k.world == 10 ? Blocks.CARVED_PUMPKIN.defaultBlockState() : p.cap);
		k.stair(cx, y + 6, cz, face.getOpposite(), false);
	}

	/** A-frame tent of wool in the world colours, with a bedroll and a lantern. */
	static void tent(Kit k, int cx, int y, int cz, Direction open, DyeColor c) {
		Direction side = open.getClockWise();
		BlockState wool = fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(c).defaultBlockState();
		for (int l = -2; l <= 2; l++) {
			int bx = cx + open.getStepX() * l, bz = cz + open.getStepZ() * l;
			for (int s = -2; s <= 2; s++) {
				int h = 2 - Math.abs(s);
				int x = bx + side.getStepX() * s, z = bz + side.getStepZ() * s;
				k.set(x, y + h + 1, z, Math.abs(s) == 2 ? Kit.slabOf(k.p.woodSlab, false) : wool);
				for (int yy = y + 1; yy <= y + h; yy++) {
					if (l == -2 || Math.abs(s) == 2) k.set(x, yy, z, l == -2 ? wool : k.p.fill);
					else k.air(x, yy, z);
				}
			}
		}
		k.set(cx + open.getStepX() * 2 + side.getStepX() * 2, y + 1, cz + open.getStepZ() * 2 + side.getStepZ() * 2, k.p.fence);
		k.set(cx + open.getStepX() * 2 - side.getStepX() * 2, y + 1, cz + open.getStepZ() * 2 - side.getStepZ() * 2, k.p.fence);
		k.bed(cx - open.getStepX(), y + 1, cz - open.getStepZ() + 0, open, c);
		k.set(cx + side.getStepX(), y + 1, cz + side.getStepZ(), k.p.lantern);
		k.mark("hidden", cx - side.getStepX(), y + 1, cz - side.getStepZ(), open);
	}

	/** Market stall: counter of barrels and slabs, striped awning on posts, goods on display. */
	static void stall(Kit k, int cx, int y, int cz, Direction front, int salt) {
		Palette p = k.p;
		Direction side = front.getClockWise();
		for (int s = -2; s <= 2; s++) {
			int x = cx + side.getStepX() * s, z = cz + side.getStepZ() * s;
			k.set(x, y + 1, z, Math.abs(s) == 2 ? p.log : (s == 0 ? Blocks.BARREL.defaultBlockState() : p.plank));
			if (Math.abs(s) < 2) k.slab(x, y + 2, z, p.woodSlab, false);
			for (int d = 0; d <= 3; d++) {
				int ax = x - front.getStepX() * d, az = z - front.getStepZ() * d;
				DyeColor c = (s & 1) == 0 ? p.colA : DyeColor.WHITE;
				k.set(ax, y + 4 + (d == 0 || d == 3 ? 0 : 1), az, fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(c).defaultBlockState());
			}
			if (Math.abs(s) == 2) {
				for (int yy = y + 1; yy <= y + 3; yy++) {
					k.set(x, yy, z, p.fence);
					k.set(x - front.getStepX() * 3, yy, z - front.getStepZ() * 3, p.fence);
				}
			}
		}
		BlockState[] goods = {Blocks.DECORATED_POT.defaultBlockState(), Blocks.PUMPKIN.defaultBlockState(), Blocks.HAY_BLOCK.defaultBlockState(),
			Blocks.MELON.defaultBlockState(), Blocks.FLOWER_POT.defaultBlockState(), p.accent};
		k.set(cx + side.getStepX(), y + 3, cz + side.getStepZ(), goods[Math.floorMod(salt, goods.length)]);
		k.set(cx - side.getStepX(), y + 3, cz - side.getStepZ(), goods[Math.floorMod(salt + 2, goods.length)]);
		k.hang(cx, y + 4, cz - front.getStepZ(), 0);
		k.mark("hidden", cx - front.getStepX() * 2, y + 1, cz - front.getStepZ() * 2, front);
	}

	/** Stone lantern: plinth, post, lantern under a slab cap. */
	static void stoneLantern(Kit k, int x, int y, int z) {
		k.set(x, y, z, k.p.trim);
		k.set(x, y + 1, z, k.p.wall);
		k.lanternOn(x, y + 2, z);
		k.slab(x, y + 3, z, k.p.slab, false);
	}

	/** Crenellated parapet along a wall top. */
	static void crenels(Kit k, int x0, int z0, int x1, int z1, int y) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++)
			for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) {
				k.set(x, y, z, ((x + z) & 1) == 0 ? k.p.alt : k.p.wall);
			}
	}

	/** Bell under a little gable on two posts. */
	static void belfry(Kit k, int x, int y, int z, boolean alongX) {
		Direction a = alongX ? Direction.EAST : Direction.SOUTH;
		for (int s : new int[] {-1, 1}) {
			for (int yy = y; yy < y + 3; yy++) k.set(x + a.getStepX() * s, yy, z + a.getStepZ() * s, k.p.pillar);
		}
		k.set(x, y + 3, z, k.p.trim);
		k.set(x + a.getStepX(), y + 3, z + a.getStepZ(), k.p.trim);
		k.set(x - a.getStepX(), y + 3, z - a.getStepZ(), k.p.trim);
		if (!k.p.underwater) k.set(x, y + 2, z, Kit.facing(Blocks.BELL.defaultBlockState(), alongX ? Direction.NORTH : Direction.EAST)
			.setValue(BellBlock.ATTACHMENT, BellAttachType.CEILING));
		k.slab(x, y + 4, z, k.p.roofSlab, false);
	}
}
