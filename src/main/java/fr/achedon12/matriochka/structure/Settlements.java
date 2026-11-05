package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.RailShape;

/** Ensembles: village, camp, market, city, fort, arena, garden, ruin, bridge, rail, stair. */
final class Settlements {
	private Settlements() {}

	private static Direction toward(int x, int z) {
		if (Math.abs(x) >= Math.abs(z)) return x > 0 ? Direction.WEST : Direction.EAST;
		return z > 0 ? Direction.NORTH : Direction.SOUTH;
	}

	/** Paved path one block wide from (x0,z0) to (x1,z1), L-shaped. */
	static void path(Kit k, int x0, int z0, int x1, int z1, int y) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++) k.set(x, y, z0, k.hc(x, y, z0, 401, 0.25) ? k.p.inlay : k.p.floor);
		for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) k.set(x1, y, z, k.hc(x1, y, z, 401, 0.25) ? k.p.inlay : k.p.floor);
	}

	/** Fenced garden plot with crops or the world's plants. */
	static void plot(Kit k, int x0, int z0, int x1, int z1, int y) {
		for (int x = x0; x <= x1; x++)
			for (int z = z0; z <= z1; z++) {
				boolean edge = x == x0 || x == x1 || z == z0 || z == z1;
				if (edge) {
					k.set(x, y, z, k.p.trim);
					k.set(x, y + 1, z, k.p.fence);
				} else if (z == (z0 + z1) / 2 && !k.p.underwater && k.world != 6) {
					k.set(x, y, z, Blocks.WATER.defaultBlockState());
				} else {
					k.set(x, y, z, k.world == 1 || k.world == 8 || k.world == 0 ? Blocks.FARMLAND.defaultBlockState() : k.p.soil);
					BlockState crop = k.world == 1 ? Blocks.CARROTS.defaultBlockState() : k.world == 8 ? Blocks.WHEAT.defaultBlockState().setValue(BlockStateProperties.AGE_7, 5)
						: null;
					if (crop != null) k.set(x, y + 1, z, crop); else k.plant(x, y + 1, z);
				}
			}
		k.set(x0, y + 1, z0, k.p.wall);
		k.lanternOn(x0, y + 2, z0);
	}

	// ---------------------------------------------------------------- village
	static void village(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean floating = k.world == 4;
		boolean silent = k.world == 5;
		boolean mirror = k.world == 6;
		boolean buried = k.id.equals("buried_village");
		if (buried) k.sink = 4;
		int base = mirror ? 8 : 0;
		if (floating) {
			k.siteClear(R, 20);
			k.island(0, 0, 0, 5, 7);
		} else k.site(R, 20 + base);
		if (mirror) {
			// the refuge stands on a platform; every house has its reflection hanging beneath
			for (int x = -R; x <= R; x++)
				for (int z = -R; z <= R; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > R - 0.5) continue;
					k.set(x, base, z, d > R - 1.5 ? p.trim : ((int) d % 3 == 0 ? p.inlay : p.floor));
				}
			for (int i = 0; i < 6; i++) {
				double a = i * Math.PI / 3;
				int px = (int) Math.round(Math.cos(a) * (R - 2)), pz = (int) Math.round(Math.sin(a) * (R - 2));
				for (int y = 1; y < base; y++) k.set(px, y, pz, p.pillar);
			}
			for (int y = 1; y <= base; y++) {
				k.stair(-1, y, -R + base - y + 1, Direction.SOUTH, false);
				k.stair(0, y, -R + base - y + 1, Direction.SOUTH, false);
				for (int yy = 1; yy < y; yy++) { k.set(-1, yy, -R + base - y + 1, p.base); k.set(0, yy, -R + base - y + 1, p.base); }
			}
		}
		// plaza
		int pr = k.large() ? 5 : 3;
		k.roundFloor(0, base, 0, pr);
		if (silent) {
			k.set(0, base + 1, 0, Blocks.SCULK_SHRIEKER.defaultBlockState());
			k.ring(0, base, 0, 2, Blocks.SCULK.defaultBlockState());
		} else if (mirror) {
			Parts.statue(k, 0, base + 1, 0, Direction.NORTH);
		} else Parts.fountain(k, 0, base + 1, 0, k.large() ? 3 : 2);
		// houses in a ring, doors facing the plaza
		int n = k.large() ? 6 : 4;
		double hr = k.large() ? 11.5 : 7;
		int chief = -1;
		for (int i = 0; i < n; i++) {
			double a = i * 2 * Math.PI / n + (k.variant % 7) * 0.1;
			int hx = (int) Math.round(Math.cos(a) * hr), hz = (int) Math.round(Math.sin(a) * hr);
			Direction door = toward(hx, hz);
			boolean alongX = door.getAxis() == Direction.Axis.Z;
			int w = 3 + (i % 2), dpt = 2 + ((i + k.variant) % 2);
			if (i == 0) { w = 4; dpt = 3; chief = i; }
			int x0 = alongX ? hx - w : hx - dpt, x1 = alongX ? hx + w : hx + dpt;
			int z0 = alongX ? hz - dpt : hz - w, z1 = alongX ? hz + dpt : hz + w;
			int lim = R - 1;
			if (x0 < -lim) { x1 += -lim - x0; x0 = -lim; }
			if (x1 > lim) { x0 -= x1 - lim; x1 = lim; }
			if (z0 < -lim) { z1 += -lim - z0; z0 = -lim; }
			if (z1 > lim) { z0 -= z1 - lim; z1 = lim; }
			if (floating) {
				k.island((x0 + x1) / 2, base, (z0 + z1) / 2, Math.max(x1 - x0, z1 - z0) / 2.0 + 1.5, 6);
				ropeBridge(k, (x0 + x1) / 2, (z0 + z1) / 2, base);
			}
			int floors = (i == 0 || k.large() && i % 3 == 1) ? 2 : 1;
			Parts.house(k, x0, z0, x1, z1, base, floors, door, (i + k.variant) % 3);
			if (silent) {
				int ex = door == Direction.WEST ? x0 : door == Direction.EAST ? x1 : (x0 + x1) / 2;
				int ez = door == Direction.NORTH ? z0 : door == Direction.SOUTH ? z1 : (z0 + z1) / 2;
				k.air(ex, base + 1, ez);
				k.air(ex, base + 2, ez);
				for (int x = x0 + 1; x < x1; x++) for (int z = z0 + 1; z < z1; z++) if (k.hc(x, base, z, 411, 0.5)) k.carpet(x, base + 1, z, p.colB);
			}
			if (mirror) {
				boolean f = k.flip;
				int fy = k.flipY;
				k.flip = true;
				k.flipY = base * 2;
				Parts.house(k, x0, z0, x1, z1, base, floors, door, (i + k.variant + 1) % 3);
				k.flip = f;
				k.flipY = fy;
			}
			if (!floating) path(k, 0, 0, (x0 + x1) / 2, (z0 + z1) / 2, base);
			if (i == chief) {
				int cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
				Direction back = door.getOpposite();
				int rx = cx + back.getStepX() * ((alongX ? dpt : dpt) - 1), rz = cz + back.getStepZ() * ((alongX ? dpt : dpt) - 1);
				k.mark("reading", rx, base + 1, rz, door);
			}
			// garden plot behind every other house
			if (!floating && !mirror && i % 2 == 1) {
				Direction back = door.getOpposite();
				int gx = (x0 + x1) / 2 + back.getStepX() * (dpt + 3), gz = (z0 + z1) / 2 + back.getStepZ() * (dpt + 3);
				if (Math.abs(gx) <= R - 3 && Math.abs(gz) <= R - 3) plot(k, gx - 2, gz - 1, gx + 2, gz + 1, base);
			}
		}
		// lamp posts and benches around the plaza
		for (int i = 0; i < 4; i++) {
			double a = i * Math.PI / 2 + Math.PI / 4;
			int lx = (int) Math.round(Math.cos(a) * (pr + 1)), lz = (int) Math.round(Math.sin(a) * (pr + 1));
			if (silent) k.set(lx, base + 1, lz, Blocks.SOUL_LANTERN.defaultBlockState()); else k.lampPost(lx, base + 1, lz, 2);
		}
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			Direction s = d.getClockWise();
			int bx = d.getStepX() * pr + s.getStepX() * 2, bz = d.getStepZ() * pr + s.getStepZ() * 2;
			k.chair(bx, base + 1, bz, d.getOpposite());
		}
		k.mark("npc", 2, base + 1, 1, Direction.NORTH);
		k.mark("guard", -1, base + 1, 2, Direction.NORTH);
		if (!silent && !k.p.underwater) Parts.belfry(k, pr + 1, base + 1, -pr - 1, true);
		k.decay(-R, base, -R, R, base + 18, R, buried ? 0.5 : silent ? 0.3 : 0.08);
	}

	/** Plank and fence rope bridge from the plaza edge to an island. */
	private static void ropeBridge(Kit k, int tx, int tz, int y) {
		int steps = Math.max(Math.abs(tx), Math.abs(tz));
		for (int s = 3; s <= steps; s++) {
			double t = s / (double) steps;
			int x = (int) Math.round(tx * t), z = (int) Math.round(tz * t);
			k.slab(x, y, z, k.p.woodSlab, true);
			if (s % 2 == 0) {
				Direction side = Math.abs(tx) > Math.abs(tz) ? Direction.SOUTH : Direction.EAST;
				k.set(x + side.getStepX(), y + 1, z + side.getStepZ(), k.p.fence);
				k.set(x - side.getStepX(), y + 1, z - side.getStepZ(), k.p.fence);
			}
		}
	}

	// ---------------------------------------------------------------- camp
	static void camp(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 14);
		// fire ring with log benches
		k.set(0, 0, 0, p.trim);
		k.set(0, 1, 0, Blocks.CAMPFIRE.defaultBlockState());
		for (int x = -1; x <= 1; x++) for (int z = -1; z <= 1; z++) if (x != 0 || z != 0) k.slab(x, 1, z, p.slab, false);
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			Direction s = d.getClockWise();
			for (int o = -1; o <= 1; o++) k.set(d.getStepX() * 3 + s.getStepX() * o, 1, d.getStepZ() * 3 + s.getStepZ() * o, Kit.axis(p.log, s.getAxis()));
		}
		// tents
		int tents = k.small() ? 2 : 4;
		double tr = k.small() ? 4 : 7;
		for (int i = 0; i < tents; i++) {
			double a = Math.PI / 4 + i * 2 * Math.PI / tents;
			int tx = (int) Math.round(Math.cos(a) * tr), tz = (int) Math.round(Math.sin(a) * tr);
			Parts.tent(k, tx, 0, tz, toward(tx, tz), i % 2 == 0 ? p.colA : p.colB);
		}
		// cooking corner and supplies
		int cx = k.small() ? -4 : -8;
		k.set(cx, 1, 0, Kit.facing(Blocks.SMOKER.defaultBlockState(), Direction.EAST));
		k.set(cx, 1, 1, Blocks.CAULDRON.defaultBlockState());
		k.barrel(cx, 1, -1, Direction.UP);
		k.set(cx, 2, -1, p.lantern);
		k.crates(-cx - 1, 1, 0);
		k.mark("hidden", -cx, 1, -1, Direction.WEST);
		if (!k.small()) {
			// lookout post
			int lx = -1, lz = -10;
			for (int[] c : new int[][] {{0, 0}, {2, 0}, {0, 2}, {2, 2}}) for (int y = 1; y <= 5; y++) k.set(lx + c[0], y, lz + c[1], p.fence);
			k.box(lx, 6, lz, lx + 2, 6, lz + 2, p.plank);
			for (int y = 1; y <= 6; y++) k.set(lx + 1, y, lz - 1, Kit.ladderFacing(Direction.NORTH));
			k.set(lx + 1, 6, lz - 1, Kit.ladderFacing(Direction.NORTH));
			k.lanternOn(lx, 7, lz);
			k.mark("hidden", lx + 2, 7, lz + 2, Direction.NORTH);
		}
		if (k.world == 2) {
			// miners: a timbered mine mouth and a pile of giant ore
			for (int y = 1; y <= 3; y++) { k.set(-2, y, R - 2, p.log); k.set(2, y, R - 2, p.log); }
			for (int x = -2; x <= 2; x++) k.set(x, 4, R - 2, Kit.axis(p.log, Direction.Axis.X));
			k.air(-1, 0, R - 2, 1, 3, R);
			for (int z = R - 2; z <= R; z++) k.set(0, 0, z, Blocks.RAIL.defaultBlockState());
			k.set(3, 1, 4, ModContent.block("giant_ore_block").defaultBlockState());
			k.set(4, 1, 4, ModContent.block("blazing_rock_ore").defaultBlockState());
			k.set(3, 2, 4, Blocks.ANVIL.defaultBlockState());
			k.hang(-2, 3, R - 3, 0);
		}
		if (k.world == 8) {
			k.set(2, 1, -3, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.SOUTH));
			k.set(-2, 1, 3, Blocks.HAY_BLOCK.defaultBlockState());
		}
		k.mark("npc", 1, 1, 2, Direction.NORTH);
		k.mark("guard", 0, 1, -2, Direction.NORTH);
		k.decay(-R, 1, -R, R, 10, R, k.world == 8 ? 0.4 : 0.1);
	}

	// ---------------------------------------------------------------- market
	static void market(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 20);
		for (int x = -R + 1; x <= R - 1; x++)
			for (int z = -R + 1; z <= R - 1; z++) k.set(x, 0, z, (Math.abs(x) <= 1) ? p.inlay : ((x + z) % 5 == 0 ? p.inlay2 : p.floor));
		// two rows of stalls along the avenue
		int salt = 0;
		for (int z = -R + 4; z <= 2; z += 6) {
			Parts.stall(k, -5, 0, z, Direction.EAST, salt++);
			Parts.stall(k, 5, 0, z, Direction.WEST, salt++);
			// lantern strings between the rows
			for (int x = -3; x <= 3; x++) k.set(x, 6, z, Kit.axis(p.chain, Direction.Axis.X));
			k.hang(0, 5, z, 0);
		}
		// covered market hall at the south end
		int hz0 = 6, hz1 = R - 2;
		for (int x = -9; x <= 9; x += 3) {
			k.pillar(x, 1, hz0, 6, false);
			k.pillar(x, 1, hz1, 6, false);
		}
		for (int z = hz0; z <= hz1; z += 3) { k.pillar(-9, 1, z, 6, false); k.pillar(9, 1, z, 6, false); }
		k.box(-10, 7, hz0 - 1, 10, 7, hz1 + 1, p.trim);
		k.gable(-9, hz0, 9, hz1, 8, true, p.alt);
		k.floor(-8, hz0 + 1, 8, hz1 - 1, 0, 1);
		k.banquet(0, 1, (hz0 + hz1) / 2, 10, true);
		for (int x = -6; x <= 6; x += 6) k.chandelier(x, 7, (hz0 + hz1) / 2, 1);
		k.crates(-8, 1, hz1 - 1);
		k.crates(7, 1, hz1 - 1);
		// clock pole in the middle of the avenue
		BlockState cu = Blocks.CUT_COPPER.waxed().exposed().defaultBlockState();
		for (int y = 1; y <= 7; y++) k.set(0, y, -2, y == 1 ? p.trim : Blocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState().setValue(BlockStateProperties.FACING, Direction.UP));
		k.box(-1, 8, -3, 1, 8, -1, cu);
		k.set(0, 8, -2, Blocks.COPPER_BULB.waxed().exposed().defaultBlockState().setValue(BlockStateProperties.LIT, true));
		k.set(0, 9, -2, Blocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState());
		// entrance arch
		for (int s : new int[] {-3, 3}) for (int y = 1; y <= 5; y++) k.set(s, y, -R + 1, p.pillar);
		k.arch(-3, 3, 4, -R + 1, true, 1);
		k.banner(-3, 3, -R, Direction.NORTH, p.colA);
		k.banner(3, 3, -R, Direction.NORTH, p.colB);
		k.mark("npc", 1, 1, hz0 + 2, Direction.NORTH);
		k.mark("hidden", -8, 1, hz0 + 1, Direction.EAST);
		k.mark("hidden", 8, 1, hz1 - 2, Direction.WEST);
		k.mark("guard", 0, 1, hz1 - 1, Direction.NORTH);
		k.decay(-R, 1, -R, R, 16, R, 0.08);
	}

	// ---------------------------------------------------------------- city
	static void city(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean giant = k.world == 10;
		boolean sunk = k.world == 7;
		int hw = R - 2;
		if (k.flip) {
			k.flipY = 30;
			k.site(R, k.flipY - 2);
			Towers.anchorRock(k, R - 4);
			k.box(-hw, 0, -hw, hw, 0, hw, p.found);
		} else k.site(R, 30);
		// paving, avenues
		for (int x = -hw; x <= hw; x++)
			for (int z = -hw; z <= hw; z++) k.set(x, 0, z, Math.abs(x) <= 1 || Math.abs(z) <= 1 ? p.inlay : ((x * 7 + z * 3) % 11 == 0 ? p.inlay2 : p.floor));
		// city wall with corner towers and two gates
		int wh = giant ? 10 : 6;
		for (int i = -hw; i <= hw; i++) {
			for (int[] c : new int[][] {{i, -hw}, {i, hw}, {-hw, i}, {hw, i}}) {
				for (int y = 1; y <= wh; y++) k.set(c[0], y, c[1], y == 1 ? p.trim : y == wh ? p.alt : p.base);
				if ((i & 1) == 0) k.set(c[0], wh + 1, c[1], p.wall);
			}
		}
		for (int s : new int[] {-1, 1}) {
			k.air(-1, 1, s * hw, 1, giant ? 7 : 4, s * hw);
			k.set(-2, giant ? 8 : 5, s * hw, p.trim);
		}
		for (int[] c : new int[][] {{-hw, -hw}, {hw, -hw}, {-hw, hw}, {hw, hw}}) {
			Parts.roundTower(k, c[0], c[1], 2, 0, wh + 4, true);
			k.air(c[0] - 2 * Integer.signum(c[0]), 1, c[1] - Integer.signum(c[1]), c[0] - 2 * Integer.signum(c[0]), 2, c[1] - Integer.signum(c[1]));
		}
		// quarters: houses, a keep, a tower
		int[][] lots = {{-11, -11}, {5, -11}, {-11, 5}, {5, 5}};
		for (int i = 0; i < 4; i++) {
			int lx = lots[i][0], lz = lots[i][1];
			int sz = giant ? 5 : 2;
			if (i == 3) {
				// keep with the guarded room
				k.room(lx, lz, lx + 6, lz + 6, 0, giant ? 10 : 6, 3, 2, p.plank);
				k.room(lx, lz, lx + 6, lz + 6, giant ? 10 : 6, 5, 3, 2, null);
				int ky = giant ? 10 : 6;
				k.hip(lx, lz, lx + 6, lz + 6, ky + 6, 1);
				k.doorway(lx + 3, 1, lz, Direction.NORTH, 1, 3);
				for (int y = 1; y <= ky; y++) k.set(lx + 5, y, lz + 5, Kit.ladderFacing(Direction.WEST));
				k.mark("guard", lx + 3, ky + 1, lz + 5, Direction.NORTH);
				k.mark("spawner", lx + 1, ky + 1, lz + 1, Direction.NORTH);
				k.mark("spawner", lx + 5, ky + 1, lz + 1, Direction.NORTH);
				k.mark("spawner", lx + 1, ky + 1, lz + 5, Direction.NORTH);
				k.banquet(lx + 3, 1, lz + 3, 4, true);
				k.mark("npc", lx + 2, 1, lz + 1, Direction.NORTH);
				continue;
			}
			if (i == 1) {
				Parts.roundTower(k, lx + 3, lz + 3, 3, 0, giant ? 18 : 14, true);
				k.doorway(lx + 3, 1, lz, Direction.NORTH, 1, 3);
				k.mark("hidden", lx + 3, 6, lz + 4, Direction.NORTH);
				continue;
			}
			Parts.house(k, lx, lz, lx + 5 + (giant ? 0 : 0), lz + 4 + sz, 0, giant ? 1 : 2, i == 0 ? Direction.EAST : Direction.NORTH, (i + k.variant) % 3);
			if (sunk) k.dome(lx + 3, 9, lz + 3 + sz / 2, 3, p.roof);
		}
		// plaza monument
		if (giant) {
			// a giant chair and table stand on the plaza
			for (int[] c : new int[][] {{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) for (int y = 1; y <= 5; y++) k.set(c[0], y, c[1], p.log);
			k.box(-4, 6, -4, 4, 6, 4, p.alt);
			for (int[] c : new int[][] {{-3, 6}, {3, 6}, {-3, 10}, {3, 10}}) for (int y = 1; y <= 3; y++) k.set(c[0], y, c[1], p.log);
			k.box(-3, 4, 6, 3, 4, 10, p.alt);
			k.box(-3, 5, 10, 3, 11, 10, p.trim);
		} else if (k.p.underwater) {
			Parts.statue(k, 0, 1, 0, Direction.NORTH);
		} else Parts.fountain(k, 0, 1, 0, 2);
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			for (int s = 4; s < hw; s += 5) k.lampPost(d.getStepX() * s + d.getClockWise().getStepX() * 2, 1, d.getStepZ() * s + d.getClockWise().getStepZ() * 2, giant ? 5 : 2);
		}
		k.mark("hidden", -hw + 1, 1, 0, Direction.EAST);
		k.mark("hidden", hw - 1, 1, -3, Direction.WEST);
		if (k.flip) {
			boolean f = k.flip;
			int top = k.flipY - 4;
			k.flip = false;
			for (int y = 1; y <= top; y++) { k.set(0, y, -hw - 1, p.base); k.set(0, y, -hw - 2, Kit.ladderFacing(Direction.NORTH)); }
			k.flip = f;
		}
		k.decay(-R, 0, -R, R, 30, R, sunk ? 0.4 : k.combat() ? 0.2 : 0.06);
	}

	// ---------------------------------------------------------------- fort
	static void fort(Kit k) {
		Palette p = k.p;
		int R = k.R, hw = R - 3, wh = 7;
		k.site(R, 26);
		k.floor(-hw, -hw, hw, hw, 0, 3);
		// curtain walls, two thick with a walkway and crenels
		for (int i = -hw; i <= hw; i++)
			for (int[] c : new int[][] {{i, -hw}, {i, hw}, {-hw, i}, {hw, i}}) {
				for (int y = 1; y <= wh; y++) k.set(c[0], y, c[1], y == 1 ? p.trim : y == wh ? p.alt : p.base);
				k.set(c[0], wh + 1, c[1], (i & 1) == 0 ? p.alt : p.wall);
				if (i % 5 == 0) k.set(c[0], 4, c[1], p.bars);
			}
		for (int i = -hw + 1; i <= hw - 1; i++)
			for (int[] c : new int[][] {{i, -hw + 1}, {i, hw - 1}, {-hw + 1, i}, {hw - 1, i}}) {
				k.set(c[0], wh, c[1], p.plank);
				if (i % 6 == 0) k.stair(c[0], wh - 1, c[1], Kit.inward(c[0], c[1]).getOpposite(), true);
			}
		for (int y = 1; y <= wh; y++) k.set(hw - 1, y, 0, Kit.ladderFacing(Direction.WEST));
		// corner towers
		for (int[] c : new int[][] {{-hw, -hw}, {hw, -hw}, {-hw, hw}, {hw, hw}}) {
			Parts.roundTower(k, c[0], c[1], 3, 0, wh + 5, true);
			int sx = Integer.signum(c[0]), sz = Integer.signum(c[1]);
			k.air(c[0] - 2 * sx, 1, c[1] - 2 * sz, c[0] - 2 * sx, 2, c[1] - 2 * sz);
			k.air(c[0] - 2 * sx, wh + 1, c[1] - 2 * sz, c[0] - 2 * sx, wh + 2, c[1] - 2 * sz);
		}
		// gatehouse with portcullis
		k.room(-4, -hw - 1, 4, -hw + 3, 0, wh + 3, 4, 1, p.plank);
		k.hip(-4, -hw - 1, 4, -hw + 3, wh + 4, 1);
		k.air(-1, 1, -hw - 1, 1, 4, -hw + 3);
		for (int x = -1; x <= 1; x++) for (int y = 1; y <= 4; y++) k.set(x, y, -hw + 1, y >= 3 ? p.bars : p.fill);
		for (int x = -1; x <= 1; x++) k.set(x, 5, -hw + 1, p.trim);
		k.banner(-3, wh, -hw - 2, Direction.NORTH, p.colA);
		k.banner(3, wh, -hw - 2, Direction.NORTH, p.colB);
		// the keep
		int kx0 = -5, kz0 = 1, kx1 = 5, kz1 = 11;
		k.room(kx0, kz0, kx1, kz1, 0, 5, 4, 2, p.plank);
		k.room(kx0, kz0, kx1, kz1, 5, 5, 4, 2, p.plank);
		k.room(kx0, kz0, kx1, kz1, 10, 5, 4, 2, null);
		k.hip(kx0, kz0, kx1, kz1, 16, 1);
		k.box(kx0 + 1, 15, kz0 + 1, kx1 - 1, 15, kz1 - 1, p.plank);
		k.doorway(0, 1, kz0, Direction.NORTH, 3, 3);
		for (int y = 1; y <= 15; y++) k.set(kx1 - 1, y, kz1 - 1, Kit.ladderFacing(Direction.WEST));
		k.banquet(0, 1, 6, 6, false);
		k.stair(0, 1, kz1 - 1, p.woodStair, Direction.SOUTH, false);
		k.banner(-2, 4, kz1 - 1, Direction.NORTH, p.colA);
		k.banner(2, 4, kz1 - 1, Direction.NORTH, p.colB);
		for (int z = kz0 + 2; z <= kz1 - 2; z += 3) { k.bed(kx0 + 1, 6, z, Direction.EAST, p.colA); k.bed(kx1 - 2, 6, z, Direction.WEST, p.colB); }
		k.set(-3, 11, kz1 - 1, Blocks.ANVIL.defaultBlockState());
		k.set(-1, 11, kz1 - 1, Kit.facing(Blocks.GRINDSTONE.defaultBlockState(), Direction.NORTH));
		k.set(1, 11, kz1 - 1, Blocks.SMITHING_TABLE.defaultBlockState());
		k.chandelier(0, 4, 4, 0);
		k.hang(0, 9, 6, 1);
		k.hang(0, 14, 4, 1);
		k.mark("guard", 0, 11, kz1 - 2, Direction.NORTH);
		k.mark("spawner", -3, 11, kz0 + 1, Direction.NORTH);
		k.mark("spawner", 3, 11, kz0 + 1, Direction.NORTH);
		k.mark("spawner", 3, 11, kz1 - 2, Direction.NORTH);
		k.mark("npc", 2, 1, 3, Direction.NORTH);
		k.mark("hidden", kx0 + 1, 6, kz1 - 1, Direction.EAST);
		k.mark("hidden", -hw + 1, 1, hw - 1, Direction.EAST);
		k.mark("hidden", hw - 3, wh + 1, -hw + 1, Direction.SOUTH);
		// courtyard: well, training dummies, stable
		Parts.fountain(k, -9, 1, -5, 1);
		for (int x = 6; x <= 10; x += 2) {
			k.set(x, 1, -6, p.fence);
			k.set(x, 2, -6, Blocks.HAY_BLOCK.defaultBlockState());
			k.set(x, 3, -6, Blocks.CARVED_PUMPKIN.defaultBlockState());
		}
		for (int z = 2; z <= 8; z++) { k.set(-hw + 4, 1, z, p.fence); }
		k.set(-hw + 2, 1, 5, Blocks.HAY_BLOCK.defaultBlockState());
		k.set(-hw + 2, 1, 3, Blocks.HAY_BLOCK.defaultBlockState());
		if (k.id.equals("anchored_fort")) {
			k.set(0, 1, 9, ModContent.block("terrain_anchor").defaultBlockState());
			// great chains anchoring the walls into the ground
			for (int[] c : new int[][] {{-hw, -hw}, {hw, -hw}, {-hw, hw}, {hw, hw}})
				for (int t = 0; t < 6; t++) k.set(c[0] + Integer.signum(c[0]) * (t / 2 + 3), wh + 2 - t * 2, c[1], Kit.axis(p.chain, Direction.Axis.Y));
		} else {
			// the mobile fortress rides on treads and wheels
			for (int z = -hw; z <= hw; z++) for (int s : new int[] {-hw - 1, hw + 1}) k.set(s, 0, z, Blocks.RAIL.defaultBlockState()
				.setValue(BlockStateProperties.RAIL_SHAPE, RailShape.NORTH_SOUTH));
			for (int z : new int[] {-8, 0, 8})
				for (int a = -3; a <= 3; a++)
					for (int b = -3; b <= 3; b++) if (a * a + b * b <= 10) for (int s : new int[] {-hw - 1, hw + 1}) k.set(s, 2 + b, z + a, a * a + b * b <= 2 ? p.cap : Kit.axis(p.log, Direction.Axis.X));
		}
		k.decay(-R, 1, -R, R, 26, R, k.combat() ? 0.2 : 0.08);
	}

	// ---------------------------------------------------------------- arena
	static void arena(Kit k) {
		if (k.id.equals("mirror_hall")) { mirrorHall(k); return; }
		if (k.id.equals("titanic_workbench")) { workbench(k); return; }
		Palette p = k.p;
		int R = k.R;
		boolean court = k.id.equals("jailer_court");
		boolean rough = k.world == 9;
		k.site(R, 14);
		int pit = R - 5;
		// sunken pit
		for (int x = -R; x <= R; x++)
			for (int z = -R; z <= R; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > R + 0.5) continue;
				if (d <= pit + 0.5) {
					k.set(x, -2, z, ((int) d) % 3 == 0 ? p.inlay : p.floor);
					k.air(x, -1, z);
					k.air(x, 0, z);
					if (rough && k.hc(x, 0, z, 421, 0.05) && d < pit - 1) for (int y = -1; y <= 1 + k.hi(x, 0, z, 422, 4); y++) k.set(x, y, z, p.base);
				} else if (d <= pit + 1.5) {
					for (int y = -2; y <= 1; y++) k.set(x, y, z, y == 1 ? p.trim : p.alt);
				} else if (d <= R - 1.5) {
					int tier = (int) (d - pit - 1.5);
					for (int y = 0; y <= tier + 1; y++) k.set(x, y, z, p.base);
					if (Math.abs((d - pit - 1.5) - tier - 0.5) < 0.5) k.stair(x, tier + 2, z, Kit.inward(x, z).getOpposite(), false);
				} else {
					for (int y = 0; y <= 8; y++) k.set(x, y, z, y == 0 ? p.trim : y == 8 ? p.alt : p.base);
					k.set(x, 9, z, ((x + z) & 1) == 0 ? p.wall : p.alt);
				}
			}
		// arches in the outer wall
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6 + Math.PI / 12;
			int x = (int) Math.round(Math.cos(a) * (R - 0.5)), z = (int) Math.round(Math.sin(a) * (R - 0.5));
			for (int y = 5; y <= 6; y++) k.set(x, y, z, p.pane);
		}
		// four gates with portcullis
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			Direction s = d.getClockWise();
			for (int dist = pit; dist <= R; dist++)
				for (int o = -1; o <= 1; o++) {
					int x = d.getStepX() * dist + s.getStepX() * o, z = d.getStepZ() * dist + s.getStepZ() * o;
					k.set(x, -2, z, p.floor);
					k.air(x, -1, z);
					k.air(x, 0, z);
					k.air(x, 1, z);
					k.set(x, 2, z, p.trim);
					if (dist == pit + 1) k.set(x, 1, z, p.bars);
				}
			for (int o : new int[] {-2, 2}) {
				int x = d.getStepX() * R + s.getStepX() * o, z = d.getStepZ() * R + s.getStepZ() * o;
				for (int y = 1; y <= 10; y++) k.set(x, y, z, p.pillar);
				k.set(x, 11, z, p.cap);
				k.banner(x + d.getStepX(), 8, z + d.getStepZ(), d, o < 0 ? p.colA : p.colB);
			}
		}
		// champion's box on the south side
		int bz = pit + 3;
		k.box(-2, 3, bz, 2, 3, bz + 1, p.trim);
		k.stair(0, 4, bz + 1, p.woodStair, Direction.SOUTH, false);
		for (int s : new int[] {-2, 2}) for (int y = 4; y <= 6; y++) k.set(s, y, bz + 1, p.pillar);
		k.box(-2, 7, bz, 2, 7, bz + 1, p.roof);
		k.standingBanner(-1, 4, bz, p.colA);
		k.standingBanner(1, 4, bz, p.colB);
		// central podium and cages
		k.box(-1, -1, -1, 1, -1, 1, p.trim);
		k.set(0, 0, 0, p.cap);
		k.set(0, 1, 0, p.accent);
		if (court) {
			for (int[] c : new int[][] {{-4, -4}, {4, -4}, {-4, 4}, {4, 4}}) {
				for (int y = -1; y <= 1; y++)
					for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (Math.abs(a) == 1 || Math.abs(b) == 1) k.set(c[0] + a, y, c[1] + b, p.bars);
				k.box(c[0] - 1, 2, c[1] - 1, c[0] + 1, 2, c[1] + 1, p.slab);
				k.hang(c[0], 1, c[1], 0);
			}
			k.box(-3, 3, bz - 1, 3, 3, bz - 1, p.alt);
			k.set(0, 4, bz - 1, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.NORTH));
		}
		// pens under the east seating: the guarded loot room
		int ex = pit + 2;
		k.shell(ex, -3, -3, ex + 4, 1, 3, p.alt);
		k.floor(ex + 1, -2, ex + 3, 2, -3, 1);
		k.air(ex, -2, -1, ex, -1, 1);
		k.set(ex, -2, 0, p.bars);
		k.set(ex, -1, 0, p.bars);
		k.hang(ex + 2, 0, 0, 0);
		k.mark("guard", ex + 3, -2, 0, Direction.WEST);
		k.mark("spawner", ex + 1, -2, -2, Direction.WEST);
		k.mark("spawner", ex + 1, -2, 2, Direction.WEST);
		k.mark("spawner", -pit + 2, -1, -pit + 4, Direction.NORTH);
		k.mark("hidden", -ex - 3, 1, 3, Direction.EAST);
		k.mark("hidden", 3, 4, bz, Direction.NORTH);
		k.decay(-R, -2, -R, R, 12, R, rough ? 0.45 : 0.2);
	}

	/** Hall of mirrors: walls and pillars of mirror glass, a checkered floor, a dais in the centre. */
	private static void mirrorHall(Kit k) {
		Palette p = k.p;
		int R = k.R, hw = R - 2;
		k.site(R, 16);
		k.room(-hw, -hw, hw, hw, 0, 9, 3, 6, p.alt);
		k.floor(-hw + 1, -hw + 1, hw - 1, hw - 1, 0, 0);
		for (int x = -hw + 1; x <= hw - 1; x++)
			for (int z = -hw + 1; z <= hw - 1; z++) if (((x + z) & 1) == 0) k.set(x, 0, z, p.glass);
		for (int x = -hw + 3; x <= hw - 3; x += 4)
			for (int z = -hw + 3; z <= hw - 3; z += 4) {
				if (Math.abs(x) <= 1 && Math.abs(z) <= 1) continue;
				for (int y = 1; y <= 8; y++) k.set(x, y, z, y == 1 || y == 8 ? p.trim : p.glass);
			}
		k.box(-1, 1, -1, 1, 1, 1, p.trim);
		k.set(0, 2, 0, p.light);
		for (int x = -hw + 1; x <= hw - 1; x += 5) k.chandelier(x, 8, 0, 1);
		k.hip(-hw, -hw, hw, hw, 10, 1);
		k.doorway(0, 1, -hw, Direction.NORTH, 3, 4);
		k.mark("guard", 0, 2, 1, Direction.NORTH);
		k.mark("spawner", -hw + 2, 1, -hw + 2, Direction.NORTH);
		k.mark("spawner", hw - 2, 1, hw - 2, Direction.NORTH);
		k.mark("spawner", -hw + 2, 1, hw - 2, Direction.NORTH);
		k.mark("hidden", hw - 1, 1, -hw + 1, Direction.WEST);
		k.decay(-R, 1, -R, R, 18, R, 0.15);
	}

	/** Titanic workbench: a crafting table the size of a house, giant tools on top, chests in its drawers. */
	private static void workbench(Kit k) {
		Palette p = k.p;
		int R = k.R, hw = 10, ty = 9;
		k.site(R, 26);
		for (int[] c : new int[][] {{-hw, -hw}, {hw - 2, -hw}, {-hw, hw - 2}, {hw - 2, hw - 2}})
			for (int y = 1; y < ty; y++) k.box(c[0], y, c[1], c[0] + 2, y, c[1] + 2, p.log);
		k.box(-hw - 1, ty, -hw - 1, hw + 1, ty + 1, hw + 1, p.alt);
		for (int x = -hw - 1; x <= hw + 1; x++)
			for (int z = -hw - 1; z <= hw + 1; z++) {
				boolean grid = Math.floorMod(x + hw + 1, 7) == 0 || Math.floorMod(z + hw + 1, 7) == 0;
				if (grid) k.set(x, ty + 1, z, p.trim);
			}
		// drawer under the top with chests
		k.shell(-6, ty - 3, -hw, 6, ty - 1, -hw + 4, p.plank);
		k.air(-5, ty - 2, -hw, 5, ty - 2, -hw);
		k.set(0, ty - 2, -hw - 1, Blocks.GOLD_BLOCK.defaultBlockState());
		k.mark("hidden", -3, ty - 2, -hw + 2, Direction.NORTH);
		k.mark("hidden", 3, ty - 2, -hw + 2, Direction.NORTH);
		// a giant ladder up one leg
		for (int y = 1; y <= ty + 1; y++) k.set(-hw + 1, y, -hw - 1, Kit.ladderFacing(Direction.NORTH));
		// tools on the top: hammer, saw, ruler, spool
		for (int x = -7; x <= -1; x++) k.set(x, ty + 2, -5, Kit.axis(p.log, Direction.Axis.X));
		k.box(-1, ty + 2, -7, 1, ty + 4, -3, Blocks.IRON_BLOCK.defaultBlockState());
		for (int z = 0; z <= 8; z++) { k.set(5, ty + 2, z, Blocks.IRON_BLOCK.defaultBlockState()); k.set(6, ty + 2, z, (z & 1) == 0 ? Blocks.IRON_BARS.defaultBlockState() : p.fill); }
		k.box(4, ty + 2, -2, 7, ty + 3, -1, p.plank);
		for (int x = -8; x <= 8; x++) k.set(x, ty + 2, 8, (x & 1) == 0 ? Blocks.GOLD_BLOCK.defaultBlockState() : p.trim);
		for (int y = ty + 2; y <= ty + 6; y++)
			for (int a = -2; a <= 2; a++) for (int b = -2; b <= 2; b++) {
				double d = Math.sqrt(a * a + b * b);
				if (d > 2.5) continue;
				boolean end = y == ty + 2 || y == ty + 6;
				k.set(-5 + a, y, 3 + b, end ? Blocks.SPRUCE_PLANKS.defaultBlockState() : d <= 1.2 ? ModContent.block("artisan_thread_ore").defaultBlockState() : Blocks.WOOL.blue().defaultBlockState());
			}
		k.mark("hidden", -5, ty + 7, 3, Direction.NORTH);
		k.mark("hidden", 0, 1, 0, Direction.NORTH);
		k.mark("guard", 0, ty + 2, 0, Direction.NORTH);
		// felt scraps and pins on the floor
		for (int i = 0; i < 6; i++) {
			int x = (int) Math.round(Math.cos(i) * 13), z = (int) Math.round(Math.sin(i) * 13);
			k.box(x - 1, 1, z - 1, x + 1, 1, z + 1, p.inlay);
			k.set(x, 2, z, Blocks.END_ROD.defaultBlockState());
		}
		Halls.doll(k, 12, -12, 3, k.variant);
		k.decay(-R, 1, -R, R, 20, R, 0.08);
	}

	// ---------------------------------------------------------------- garden
	static void garden(Kit k) {
		if (k.small()) { secretGarden(k); return; }
		Palette p = k.p;
		int R = k.R;
		boolean crystal = k.id.equals("crystal_works");
		boolean seasons = k.id.equals("season_greenhouse");
		k.site(R, 18);
		int hw = R - 3, hl = R - 2;
		// plinth walls and glazed bays between ribs
		for (int x = -hw; x <= hw; x++)
			for (int z = -hl; z <= hl; z++) {
				boolean edge = Math.abs(x) == hw || Math.abs(z) == hl;
				k.set(x, 0, z, p.floor);
				if (!edge) continue;
				boolean rib = Math.floorMod(Math.abs(x) == hw ? z : x, 3) == 0;
				for (int y = 1; y <= 6; y++) k.set(x, y, z, y <= 2 ? (y == 1 ? p.trim : p.base) : rib ? p.pillar : (crystal ? p.glass : p.pane));
				k.set(x, 7, z, p.trim);
			}
		k.air(-hw + 1, 1, -hl + 1, hw - 1, 14, hl - 1);
		// stepped glass roof with ribs
		for (int i = 0; i <= hw; i++) {
			int y = 7 + i;
			for (int z = -hl; z <= hl; z++) {
				boolean rib = Math.floorMod(z, 3) == 0;
				for (int s : new int[] {-1, 1}) k.set(s * (hw - i), y, z, rib ? p.trim : p.glass);
			}
			if (hw - i <= 1) {
				for (int z = -hl; z <= hl; z++) for (int x = -1; x <= 1; x++) k.set(x, y, z, Math.floorMod(z, 3) == 0 ? p.trim : p.glass);
				break;
			}
		}
		for (int x = -hw; x <= hw; x++) for (int y = 8; y <= 7 + hw; y++) {
			int lim = hw - (y - 7);
			if (Math.abs(x) < lim) { k.set(x, y, -hl, p.glass); k.set(x, y, hl, p.glass); }
		}
		k.doorway(0, 1, -hl, Direction.NORTH, 3, 4);
		// central path and fountain
		for (int z = -hl + 1; z <= hl - 1; z++) for (int x = -1; x <= 1; x++) k.set(x, 0, z, x == 0 ? p.inlay2 : p.inlay);
		if (!crystal) Parts.fountain(k, 0, 1, 0, 2);
		// beds or kilns along both sides
		for (int z = -hl + 2; z <= hl - 3; z += 5) {
			if (Math.abs(z) <= 2) continue;
			for (int s : new int[] {-1, 1}) {
				int x0 = s < 0 ? -hw + 2 : 3, x1 = s < 0 ? -3 : hw - 2;
				if (crystal) {
					k.set(x0, 1, z, Kit.facing(Blocks.BLAST_FURNACE.defaultBlockState(), s < 0 ? Direction.EAST : Direction.WEST));
					k.set(x0, 2, z, Blocks.CAMPFIRE.defaultBlockState());
					k.set(x0 + 1, 1, z, Blocks.LAVA_CAULDRON.defaultBlockState());
					for (int x = x0 + 2; x <= x1; x++) {
						k.set(x, 1, z, p.glass);
						if (k.hc(x, 1, z, 431, 0.5)) k.set(x, 2, z, Blocks.AMETHYST_CLUSTER.defaultBlockState());
					}
					k.set(x1, 1, z + 1, Blocks.AMETHYST_BLOCK.defaultBlockState());
					k.set(x1, 2, z + 1, Blocks.AMETHYST_CLUSTER.defaultBlockState());
				} else {
					int quarter = (s < 0 ? 0 : 1) + (z < 0 ? 0 : 2);
					bed(k, x0, z - 1, x1, z + 1, seasons ? quarter : -1);
				}
			}
		}
		// potting benches and hanging lights
		for (int z = -hl + 1; z <= hl - 1; z += 6) {
			k.set(hw - 1, 1, z, p.plank);
			k.pot(hw - 1, 2, z);
			k.hang(-hw + 3, 9, z, 2);
			k.hang(hw - 3, 9, z, 2);
		}
		k.set(-hw + 1, 1, hl - 1, Blocks.CAULDRON.defaultBlockState());
		k.set(-hw + 1, 1, hl - 2, Blocks.COMPOSTER.defaultBlockState());
		k.workbench(hw - 2, 1, hl - 1, Direction.NORTH);
		if (seasons) {
			for (int y = 1; y <= 5; y++) k.set(0, y, hl - 2, y == 5 ? Blocks.COPPER_BULB.waxed().exposed().defaultBlockState().setValue(BlockStateProperties.LIT, true) : Blocks.CUT_COPPER.waxed().exposed().defaultBlockState());
		}
		k.mark("hidden", -hw + 1, 1, -hl + 1, Direction.EAST);
		k.mark("hidden", hw - 1, 1, hl - 3, Direction.WEST);
		k.mark("hidden", -1, 1, hl - 1, Direction.NORTH);
		k.mark("hidden", -hw + 1, 1, 0, Direction.EAST);
		k.mark("guard", 1, 1, hl - 1, Direction.NORTH);
		k.decay(-R, 0, -R, R, 18, R, k.id.contains("abandoned") ? 0.5 : 0.15);
	}

	/** Raised planter: trim border, soil, plants; seasons 0-3 pick spring, summer, autumn, winter. */
	private static void bed(Kit k, int x0, int z0, int x1, int z1, int season) {
		Palette p = k.p;
		for (int x = x0; x <= x1; x++)
			for (int z = z0; z <= z1; z++) {
				boolean edge = x == x0 || x == x1 || z == z0 || z == z1;
				if (edge) { k.set(x, 1, z, p.trim); continue; }
				k.set(x, 1, z, season == 3 ? Blocks.SNOW_BLOCK.defaultBlockState() : p.soil);
				BlockState plant = switch (season) {
					case 0 -> k.hc(x, 2, z, 441, 0.3) ? Blocks.CHERRY_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true) : Blocks.PINK_PETALS.defaultBlockState();
					case 1 -> k.hc(x, 2, z, 441, 0.5) ? Blocks.POPPY.defaultBlockState() : Blocks.DANDELION.defaultBlockState();
					case 2 -> k.hc(x, 2, z, 441, 0.3) ? Blocks.PUMPKIN.defaultBlockState() : Blocks.LEAF_LITTER.defaultBlockState();
					case 3 -> k.hc(x, 2, z, 441, 0.3) ? Blocks.SPRUCE_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true) : Blocks.SNOW.defaultBlockState();
					default -> p.plants[k.hi(x, 2, z, 443, p.plants.length)];
				};
				k.set(x, 2, z, plant);
			}
	}

	/** Small secret garden on its own island: gazebo, flower beds, and a hidden cellar under the moss tile. */
	private static void secretGarden(Kit k) {
		Palette p = k.p;
		int R = k.R;
		int y0 = k.world == 6 ? 10 : 0;
		if (k.world == 4 || k.world == 6) {
			k.siteClear(R, 20 + y0);
			k.island(0, y0, 0, R, 9);
		} else k.site(R, 16);
		for (int x = -R; x <= R; x++)
			for (int z = -R; z <= R; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > R - 0.5) continue;
				if (d > 3.5 && k.hc(x, y0, z, 451, 0.45)) k.plant(x, y0 + 1, z);
			}
		k.roundFloor(0, y0, 0, 3);
		for (int[] c : new int[][] {{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) k.pillar(c[0], y0 + 1, c[1], 4, false);
		k.box(-3, y0 + 5, -3, 3, y0 + 5, 3, p.trim);
		int top = k.hip(-3, -3, 3, 3, y0 + 6, 0);
		k.lanternOn(0, top + 1, 0);
		k.hang(0, y0 + 4, 0, 0);
		k.chair(-1, y0 + 1, 1, Direction.EAST);
		k.chair(1, y0 + 1, 1, Direction.WEST);
		k.table(0, y0 + 1, 1);
		// clouds of wool or blossom drifting around
		for (int i = 0; i < 5; i++) {
			double a = i * 1.3;
			int cx = (int) Math.round(Math.cos(a) * (R - 1)), cz = (int) Math.round(Math.sin(a) * (R - 1));
			k.ellipsoid(cx, y0 + 7 + i % 3, cz, 1.6, 0.8, 1.2, k.world == 6 ? p.leaves : Blocks.WOOL.white().defaultBlockState(), 0);
		}
		// the puzzle: one moss tile in the gazebo floor sits over a ladder to the hidden cellar
		int cy = y0 - 6;
		k.shell(-2, cy, -2, 2, cy + 4, 2, p.alt);
		k.floor(-1, -1, 1, 1, cy, 1);
		k.set(0, y0, -1, p.mossy);
		for (int y = cy + 1; y < y0; y++) k.set(0, y, -1, Kit.ladderFacing(Direction.SOUTH));
		k.set(0, y0 - 1, -2, p.base);
		k.set(-1, cy + 1, 1, p.light);
		k.set(1, cy + 1, 1, p.light);
		k.set(0, cy + 1, 1, p.cap);
		k.mark("secret", 0, cy + 2, 1, Direction.NORTH);
		k.mark("hidden", 2, y0 + 1, -1, Direction.WEST);
		if (k.world == 6) {
			for (int i = 0; i < 4; i++) {
				double a = i * Math.PI / 2 + 0.4;
				int x = (int) Math.round(Math.cos(a) * (R - 2)), z = (int) Math.round(Math.sin(a) * (R - 2));
				for (int y = 1; y < y0 - 4; y++) k.set(x, y, z, Kit.axis(p.chain, Direction.Axis.Y));
			}
			for (int y = 1; y < y0 - 2; y++) k.set(R - 2, y, 0, Blocks.VINE.defaultBlockState().setValue(net.minecraft.world.level.block.VineBlock.UP, true));
			for (int y = 1; y <= y0; y++) { k.set(0, y, -R, p.base); k.set(0, y, -R - 1, Kit.ladderFacing(Direction.NORTH)); }
		}
		k.decay(-R, y0, -R, R, y0 + 10, R, 0.1);
	}

	// ---------------------------------------------------------------- ruin
	static void ruin(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean hanging = k.world == 4;
		boolean aging = k.world == 8;
		if (hanging) {
			k.siteClear(R, 16);
			k.island(0, 0, 0, R, 10);
			for (int i = 0; i < 3; i++) {
				double a = i * 2.1 + 0.5;
				int x = (int) Math.round(Math.cos(a) * (R - 2)), z = (int) Math.round(Math.sin(a) * (R - 2));
				k.island(x, -13, z, 2, 2);
				for (int y = -10; y < -3; y++) k.set(x, y, z, Kit.axis(p.chain, Direction.Axis.Y));
			}
		} else k.site(R, 14);
		int hw = R - 2, hl = R - 3;
		k.floor(-hw, -hl, hw, hl, 0, 1);
		// outer walls at hash heights with gaps
		for (int x = -hw; x <= hw; x++)
			for (int z = -hl; z <= hl; z++) {
				boolean edge = Math.abs(x) == hw || Math.abs(z) == hl;
				boolean part = (x == 0 && Math.abs(z) < hl) || (z == 0 && Math.abs(x) < hw && Math.abs(x) > 3);
				if (!edge && !part) continue;
				int h = 1 + k.hi(x / 3, 0, z / 3, 461, 6);
				if (aging && x < 0) h = 6;
				if (k.hc(x / 2, 1, z / 2, 463, 0.15)) h = 0;
				if (x == 0 && Math.abs(z) <= 1) h = 0;
				for (int y = 1; y <= h; y++) k.set(x, y, z, y == 1 ? p.trim : (y == 4 && Math.floorMod(x + z, 3) == 0) ? p.pane : p.base);
				if (h >= 6) k.set(x, 7, z, p.alt);
			}
		// colonnade, some columns broken
		for (int x = -hw + 3; x <= hw - 3; x += 4) {
			int h = 3 + k.hi(x, 0, 0, 467, 6);
			if (aging && x < 0) h = 8;
			k.pillar(x, 1, -hl + 3, h, false);
			if (h < 8) k.set(x, h, -hl + 3, p.pillar);
		}
		// fallen column lying in the grass
		for (int i = 0; i < 5; i++) k.set(-hw + 4 + i, 1, hl - 3, Kit.axis(p.pillar, Direction.Axis.X));
		k.set(-hw + 9, 1, hl - 3, p.cap);
		// an arch still standing
		for (int y = 1; y <= 4; y++) { k.set(-3, y, 0, p.pillar); k.set(3, y, 0, p.pillar); }
		k.arch(-3, 3, 5, 0, true, 1);
		k.air(-2, 1, 0, 2, 4, 0);
		// vaulted cellar under the centre, reached by a broken stair
		int cy = -5;
		k.shell(-5, cy, -4, 5, -1, 4, p.alt);
		k.floor(-4, -3, 4, 3, cy, 2);
		for (int i = 0; i < 4; i++) {
			k.stair(4 - i, -1 - i, -3, Direction.WEST, false);
			k.air(4 - i, -i, -3, 4 - i, 1 - i, -3);
		}
		k.air(4, 0, -3);
		k.air(4, 0, -2);
		for (int x = -4; x <= 4; x += 4) k.set(x, -2, 0, p.light);
		for (int x = -3; x <= 3; x += 3) { k.stair(x, -2, -3, Direction.NORTH, true); k.stair(x, -2, 3, Direction.SOUTH, true); }
		k.hang(0, -2, 0, 0);
		k.mark("guard", -3, cy + 1, 0, Direction.EAST);
		k.mark("spawner", 0, cy + 1, 2, Direction.NORTH);
		k.mark("spawner", 0, cy + 1, -2, Direction.NORTH);
		k.mark("hidden", -4, cy + 1, 3, Direction.EAST);
		k.mark("hidden", hw - 1, 1, hl - 1, Direction.WEST);
		k.mark("hidden", -hw + 1, 1, -hl + 1, Direction.EAST);
		k.mark("hidden", 2, cy + 1, 3, Direction.NORTH);
		k.rubble(-hw, -hl, hw, hl, 1, 0.08);
		if (k.world == 7) {
			for (int x = -hw; x <= hw; x++)
				for (int z = -hl; z <= hl; z++) if (k.hc(x, 0, z, 471, 0.12)) k.set(x, 1 + k.hi(x, 0, z, 472, 3), z, k.p.leaves);
		}
		if (aging) {
			k.decay(0, 0, -R, R, 12, R, 0.85);
			k.decay(-R, 0, -R, -1, 12, R, 0.05);
		} else k.decay(-R, -5, -R, R, 12, R, 0.6);
	}

	// ---------------------------------------------------------------- bridge
	static void bridge(Kit k) {
		Palette p = k.p;
		int R = k.R, L = R - 2, dy = 6;
		k.siteClear(R, 24);
		for (int s : new int[] {-1, 1}) k.island(s * (L - 1), dy, 0, 4, 9);
		// piers with hanging rock pendants
		for (int px : new int[] {-8, 0, 8}) {
			for (int y = -6; y < dy; y++) k.box(px - 1, y, -2, px + 1, y, 2, y > dy - 3 ? p.trim : p.base);
			k.ellipsoid(px, -8, 0, 2, 3, 3, p.found, 0);
		}
		for (int i = 0; i < 4; i++) {
			int a0 = -L + 1 + i * 8, a1 = a0 + 6;
			if (a0 < -L + 1) continue;
			for (int z = -2; z <= 2; z++) k.arch(a0 + (i == 0 ? 0 : 0), Math.min(a1, L), dy - 4, z, true, 1);
		}
		k.air(2, dy - 3, -3, 5, dy + 2, 3);
		// deck with parapets and lamps, broken in the middle
		for (int x = -L; x <= L; x++) {
			boolean gap = x >= 2 && x <= 5;
			for (int z = -2; z <= 2; z++) {
				if (gap) continue;
				k.set(x, dy, z, z == 0 ? p.inlay : p.floor);
			}
			if (gap) continue;
			k.set(x, dy + 1, -3, p.wall);
			k.set(x, dy + 1, 3, p.wall);
			k.set(x, dy, -3, p.trim);
			k.set(x, dy, 3, p.trim);
			if (Math.floorMod(x, 4) == 0) { k.lampPost(x, dy + 1, -3, 2); k.lampPost(x, dy + 1, 3, 2); }
		}
		for (int x = 1; x <= 6; x++) for (int z = -3; z <= 3; z++) if (k.hc(x, dy, z, 481, 0.4) && (x == 1 || x == 6)) k.air(x, dy, z);
		// rubble from the break on the pier below
		for (int z = -1; z <= 1; z++) k.slab(4, dy - 6, z, false);
		// gate towers at both ends
		for (int s : new int[] {-1, 1}) {
			int tx = s * (L - 2);
			k.room(tx - 2, -3, tx + 2, 3, dy, 8, 0, 2, p.plank);
			k.air(tx - 2, dy + 1, -1, tx + 2, dy + 3, 1);
			k.hip(tx - 2, -3, tx + 2, 3, dy + 9, 1);
			k.mark("hidden", tx, dy + 1, 2, Direction.NORTH);
			k.mark("hidden", tx, dy + 9, 0, Direction.NORTH);
			for (int y = dy + 1; y <= dy + 8; y++) k.set(tx + 1, y, -2, Kit.ladderFacing(Direction.SOUTH));
			k.banner(tx + s * 3, dy + 6, 0, s > 0 ? Direction.EAST : Direction.WEST, s > 0 ? p.colA : p.colB);
		}
		// pier room under the deck
		k.shell(-10, dy - 4, -2, -6, dy - 1, 2, p.alt);
		k.set(-8, dy - 2, 0, p.light);
		k.mark("hidden", -8, dy - 3, 0, Direction.NORTH);
		k.air(-8, dy, 1);
		k.set(-8, dy - 1, 1, Kit.ladderFacing(Direction.NORTH));
		// overturned cart on the deck
		k.box(-4, dy + 1, -1, -3, dy + 1, 1, p.plank);
		k.mark("hidden", -2, dy + 1, 0, Direction.WEST);
		k.mark("guard", -12, dy + 1, 0, Direction.EAST);
		k.decay(-R, -10, -R, R, dy + 14, R, 0.25);
	}

	// ---------------------------------------------------------------- rail
	static void rail(Kit k) {
		Palette p = k.p;
		int R = k.R, dy = 7;
		k.site(R, 16);
		// trestles
		for (int x = -R + 1; x <= R - 1; x++) {
			boolean broken = x > R - 5;
			if (!broken) {
				k.set(x, dy, -1, p.plank);
				k.set(x, dy, 0, p.plank);
				k.set(x, dy, 1, p.plank);
				k.set(x, dy + 1, 0, Blocks.RAIL.defaultBlockState().setValue(BlockStateProperties.RAIL_SHAPE, RailShape.EAST_WEST));
				k.set(x, dy + 1, -1, (x & 3) == 0 ? p.fence : p.fill);
				k.set(x, dy + 1, 1, (x & 3) == 0 ? p.fence : p.fill);
			}
			if (Math.floorMod(x, 4) == 0 && !broken) {
				for (int y = 1; y < dy; y++) { k.set(x, y, -2, p.log); k.set(x, y, 2, p.log); }
				for (int y = 1; y < dy; y += 2) k.set(x, y, 0, Kit.axis(p.log, Direction.Axis.Z));
				k.stair(x, dy - 1, -1, Direction.NORTH, true);
				k.stair(x, dy - 1, 1, Direction.SOUTH, true);
			}
		}
		// the broken end dangles
		for (int i = 0; i < 4; i++) k.set(R - 4 + i, dy - i, 0, Blocks.RAIL.defaultBlockState().setValue(BlockStateProperties.RAIL_SHAPE, RailShape.EAST_WEST));
		for (int i = 0; i < 4; i++) k.set(R - 4 + i, dy - i - 1, 0, p.plank);
		// station platform
		int pz0 = 2, pz1 = 6;
		k.box(-5, dy, pz0, 5, dy, pz1, p.floor);
		for (int x = -5; x <= 5; x += 5) for (int y = dy + 1; y <= dy + 4; y++) k.set(x, y, pz1, p.pillar);
		for (int x = -5; x <= 5; x += 5) for (int y = 1; y < dy; y++) k.set(x, y, pz1, p.pillar);
		for (int x = -5; x <= 5; x += 5) for (int y = 1; y < dy; y++) k.set(x, y, pz0, p.log);
		k.gable(-5, pz0, 5, pz1, dy + 5, true, p.plank);
		k.chair(-3, dy + 1, pz1 - 1, Direction.NORTH);
		k.chair(-2, dy + 1, pz1 - 1, Direction.NORTH);
		k.chair(2, dy + 1, pz1 - 1, Direction.NORTH);
		k.chair(3, dy + 1, pz1 - 1, Direction.NORTH);
		k.hang(0, dy + 4, 4, 1);
		k.crates(4, dy + 1, pz0 + 1);
		k.mark("hidden", -4, dy + 1, pz0 + 1, Direction.EAST);
		k.mark("hidden", 0, dy + 1, pz1 - 1, Direction.NORTH);
		k.mark("guard", 1, dy + 1, pz0 + 1, Direction.NORTH);
		// stair up from the ground
		for (int i = 0; i < dy; i++) {
			k.stair(-6 - i, dy - i, 4, Direction.EAST, false);
			for (int y = 1; y < dy - i; y++) k.set(-6 - i, y, 4, p.base);
		}
		// signal post and a cart loaded with ore under the trestle
		k.set(-8, dy + 1, -1, p.wall);
		k.set(-8, dy + 2, -1, p.wall);
		k.set(-8, dy + 3, -1, p.light);
		k.barrel(3, 1, -4, Direction.UP);
		k.set(4, 1, -4, ModContent.block("giant_ore_block").defaultBlockState());
		k.mark("hidden", 2, 1, -4, Direction.EAST);
		k.mark("hidden", -R + 2, 1, -3, Direction.EAST);
		for (int x = -R + 3; x <= R - 3; x += 6) for (int y = dy + 1; y <= dy + 12; y++) { k.set(x, y, -2, Kit.axis(p.chain, Direction.Axis.Y)); k.set(x, y, 2, Kit.axis(p.chain, Direction.Axis.Y)); }
		k.decay(-R, 1, -R, R, dy + 8, R, 0.3);
	}

	// ---------------------------------------------------------------- stair
	static void stair(Kit k) {
		Palette p = k.p;
		int R = k.R, a = 6;
		k.site(R, 26);
		k.roundFloor(0, 0, 0, R - 1);
		// four flights around a square, each rising four blocks to a pillared landing
		int[][] corners = {{-a, -a}, {a, -a}, {a, a}, {-a, a}};
		Direction[] run = {Direction.EAST, Direction.SOUTH, Direction.WEST, Direction.NORTH};
		for (int f = 0; f < 4; f++) {
			int y0 = f * 4;
			int cx = corners[f][0], cz = corners[f][1];
			Direction d = run[f];
			boolean upside = f == 3;
			if (upside) { k.flip = true; k.flipY = 2 * y0 + 4; }
			for (int i = 1; i < 2 * a; i++) {
				int x = cx + d.getStepX() * i, z = cz + d.getStepZ() * i;
				int y = y0 + (i * 4) / (2 * a) + 1;
				if (i % 3 == 0) k.stair(x, y, z, d, false); else k.slab(x, y, z, p.slab, (i % 3) == 2);
				Direction side = d.getClockWise();
				k.set(x + side.getStepX(), y, z + side.getStepZ(), p.trim);
				k.set(x + side.getStepX(), y + 1, z + side.getStepZ(), p.wall);
			}
			if (upside) k.flip = false;
			int nx = corners[(f + 1) % 4][0], nz = corners[(f + 1) % 4][1];
			int ly = y0 + 4;
			k.box(nx - 1, ly, nz - 1, nx + 1, ly, nz + 1, p.trim);
			for (int y = 1; y < ly; y++) k.set(nx, y, nz, p.pillar);
			k.set(nx, ly + 1, nz, p.cap);
			k.lanternOn(nx, ly + 2, nz);
			if (f < 3) k.mark("hidden", nx + 1, ly + 1, nz + 1, Direction.NORTH);
		}
		k.box(-a - 1, 0, -a - 1, -a + 1, 0, -a + 1, p.trim);
		// floating fragments of stair, some of them hanging the wrong way
		for (int i = 0; i < 6; i++) {
			double ang = i * 1.05;
			int x = (int) Math.round(Math.cos(ang) * (R - 2)), z = (int) Math.round(Math.sin(ang) * (R - 2));
			int y = 6 + (i * 5) % 14;
			boolean up = (i & 1) == 0;
			Direction d = Direction.from2DDataValue(i % 4);
			for (int s = 0; s < 3; s++) k.stair(x + d.getStepX() * s, y + s, z + d.getStepZ() * s, d, !up);
			k.set(x, y - 1, z, up ? p.accent : p.cap);
		}
		// reading pavilion in the middle
		for (int[] c : new int[][] {{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) k.pillar(c[0], 1, c[1], 4, false);
		k.box(-3, 5, -3, 3, 5, 3, p.trim);
		k.hip(-3, -3, 3, 3, 6, 0);
		k.floor(-2, -2, 2, 2, 0, 1);
		k.mark("reading", 0, 1, 2, Direction.NORTH);
		k.mark("guard", 0, 1, -1, Direction.NORTH);
		k.hang(0, 4, 0, 0);
		k.decay(-R, 1, -R, R, 24, R, 0.12);
	}
}
