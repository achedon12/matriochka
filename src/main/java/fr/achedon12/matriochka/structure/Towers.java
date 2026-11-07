package fr.achedon12.matriochka.structure;

import net.minecraft.core.Direction;
import net.minecraft.world.level.block.BellBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BellAttachType;

/** Vertical archetypes: tower, lighthouse, clock. */
final class Towers {
	private Towers() {}

	// ---------------------------------------------------------------- tower
	static void tower(Kit k) {
		Palette p = k.p;
		int tr = k.small() ? 4 : k.large() ? 7 : 5;
		int h = Math.min(k.H, k.flip ? 20 : 26);
		boolean tree = k.id.equals("hollow_tree");
		boolean obs = k.id.contains("observatory");
		if (k.flip) k.flipY = Math.min(38, h + tr + 10);
		k.site(tr + 3, k.flip ? k.flipY - 4 : h + 12);
		if (k.flip) anchorRock(k, tr + 3);

		BlockState body = tree ? p.log : p.base;
		// plinth and stepped foot
		k.disc(0, 0, 0, tr + 1, p.trim);
		for (int x = -tr - 3; x <= tr + 3; x++)
			for (int z = -tr - 3; z <= tr + 3; z++)
				if (k.onRing(x, z, tr + 2)) k.stair(x, 0, z, Kit.inward(x, z), false);
		k.tube(0, 0, tr, 1, h, body);
		if (!tree) {
			for (int y = 6; y < h; y += 6) k.ring(0, y, 0, tr, p.alt);
			k.ring(0, 1, 0, tr, p.trim);
			// ribs at the eight points
			int[][] ribs = {{tr + 1, 0}, {-tr - 1, 0}, {0, tr + 1}, {0, -tr - 1}};
			for (int[] c : ribs) {
				if (c[1] == -tr - 1) continue;
				k.stair(c[0], 1, c[1], Kit.inward(c[0], c[1]), false);
				for (int y = 2; y < h - 1; y++) k.set(c[0], y, c[1], p.pillar);
				k.set(c[0], h - 1, c[1], p.cap);
			}
		} else {
			// roots spreading from the foot of the hollow tree
			for (int i = 0; i < 8; i++) {
				double a = i * Math.PI / 4 + 0.3;
				for (int s = 0; s < 4; s++) {
					int x = (int) Math.round(Math.cos(a) * (tr + s)), z = (int) Math.round(Math.sin(a) * (tr + s));
					k.set(x, 1 - s / 2, z, Kit.axis(p.log, Math.abs(Math.cos(a)) > 0.7 ? Direction.Axis.X : Direction.Axis.Z));
					k.set(x, -s / 2, z, p.soil);
				}
			}
		}
		// floors and the spiral
		int floors = 0;
		for (int y = 6; y < h - 5; y += 6) {
			k.roundFloor(0, y, 0, tr - 1);
			floors++;
		}
		k.roundFloor(0, 0, 0, tr - 1);
		// windows: tall panes at the cardinal points, slits between
		for (int y = 2; y < h - 2; y += 6) {
			for (int[] c : new int[][] {{tr, 0}, {-tr, 0}, {0, tr}}) {
				k.set(c[0], y + 1, c[1], tree ? p.fill : p.pane);
				k.set(c[0], y + 2, c[1], tree ? p.fill : p.pane);
				if (!tree) k.stair(c[0] + Integer.signum(c[0]), y, c[1] + Integer.signum(c[1]), Kit.inward(c[0], c[1]), true);
			}
			int d = (int) Math.round(tr * 0.7071);
			for (int[] c : new int[][] {{d, d}, {-d, d}, {d, -d}, {-d, -d}}) k.set(c[0], y + 2, c[1], tree ? p.fill : p.bars);
		}
		// entrance
		k.doorway(0, 1, -tr, Direction.NORTH, 1, 3);
		k.banner(-2, 3, -tr - 1, Direction.NORTH, p.colA);
		k.banner(2, 3, -tr - 1, Direction.NORTH, p.colB);
		k.runner(0, -tr + 1, 0, -2, 1);
		// rooms on each storey
		int ir = tr - 1;
		for (int f = 0; f <= floors; f++) {
			int fy = f * 6;
			int kind = (f + k.variant) % 4;
			if (f == 0) kind = 0;
			else if (f == 1 && k.role.equals("story")) kind = 1;
			k.hang(ir - 1, Math.min(fy + 5, h - 1), 0, 1);
			k.hang(-ir + 1, Math.min(fy + 5, h - 1), 0, 1);
			switch (kind) {
				case 0 -> {
					k.crates(ir - 1, fy + 1, -1);
					k.barrel(-ir + 1, fy + 1, 1, Direction.UP);
					k.mark("hidden", -ir + 1, fy + 1, -1, Direction.EAST);
					k.mark("hidden", 0, fy + 1, ir, Direction.NORTH);
				}
				case 1 -> {
					k.shelves(-ir + 1, ir - 1, -2, ir - 1, fy + 1, 3);
					k.shelves(2, ir - 1, ir - 1, ir - 1, fy + 1, 3);
					if (tr >= 5) k.mark("reading", 0, fy + 1, ir, Direction.NORTH);
					else k.mark("hidden", 0, fy + 1, ir, Direction.NORTH);
					k.candles(ir - 1, fy + 1, -1, 3);
				}
				case 2 -> {
					k.bed(ir - 1, fy + 1, 2, Direction.NORTH, p.colA);
					k.carpet(-ir + 1, fy + 1, 0, p.colB);
					k.carpet(-ir + 1, fy + 1, 1, p.colB);
					k.mark("hidden", -ir + 1, fy + 1, -1, Direction.EAST);
				}
				default -> {
					k.set(ir - 1, fy + 1, 1, Blocks.ANVIL.defaultBlockState());
					k.set(-ir + 1, fy + 1, 1, Kit.facing(Blocks.GRINDSTONE.defaultBlockState(), Direction.EAST));
					k.set(-ir + 1, fy + 1, -1, Blocks.SMITHING_TABLE.defaultBlockState());
					k.mark("hidden", 0, fy + 1, ir, Direction.NORTH);
				}
			}
		}
		// the guarded room is the highest storey
		int ty = floors * 6;
		k.mark("guard", 0, ty + 1, ir, Direction.NORTH);
		k.mark("spawner", ir - 1, ty + 1, -1, Direction.NORTH);
		k.mark("spawner", -ir + 1, ty + 1, -1, Direction.NORTH);
		k.mark("spawner", 0, ty + 1, -ir + 1, Direction.NORTH);

		// crown
		k.disc(0, h, 0, tr, p.trim);
		k.air(-1, h, -1, 1, h, 1);
		k.spiral(0, 0, 1, h);
		k.set(0, h, 0, p.pillar);
		for (int x = -tr - 2; x <= tr + 2; x++)
			for (int z = -tr - 2; z <= tr + 2; z++) {
				if (!k.onRing(x, z, tr + 1)) continue;
				k.stair(x, h, z, Kit.inward(x, z), true);
				if (!tree) k.set(x, h + 1, z, ((x + z) & 1) == 0 ? p.wall : p.alt);
			}
		topper(k, tr, h, tree, obs);
		if (k.id.equals("walking_tower")) legs(k, tr);
		if (k.flip) access(k, tr);
		k.decay(-tr - 3, 0, -tr - 3, tr + 3, h + 2, tr + 3, tree ? 0.5 : k.combat() ? 0.15 : 0.25);
	}

	private static void topper(Kit k, int tr, int h, boolean tree, boolean obs) {
		Palette p = k.p;
		int y = h + 2;
		if (tree) {
			k.ellipsoid(0, h + 4, 0, tr + 3, 4, tr + 3, p.leaves, 0);
			for (int i = 0; i < 6; i++) {
				double a = i * Math.PI / 3;
				k.set((int) (Math.cos(a) * (tr + 1)), h + 2, (int) (Math.sin(a) * (tr + 1)), p.light);
			}
			k.set(0, h + 1, 0, p.light);
			for (int i = 0; i < 10; i++) {
				int x = (int) Math.round(Math.cos(i * 0.63) * (tr + 2)), z = (int) Math.round(Math.sin(i * 0.63) * (tr + 2));
				for (int d = 1; d <= 3 + i % 3; d++) k.set(x, h + 2 - d, z, Blocks.VINE.defaultBlockState()
					.setValue(net.minecraft.world.level.block.VineBlock.UP, true));
			}
			return;
		}
		if (k.id.equals("giant_lightning_rod")) {
			BlockState cu = fr.achedon12.matriochka.mc.McBlocks.COPPER_BLOCK.waxed().exposed().defaultBlockState();
			for (int yy = y; yy < y + 6; yy++) {
				k.set(0, yy, 0, cu);
				if (yy < y + 3) for (Direction d : Direction.Plane.HORIZONTAL) k.set(d.getStepX(), yy, d.getStepZ(), fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().weathered().defaultBlockState());
			}
			for (int yy = y + 6; yy < y + 11; yy++) k.set(0, yy, 0, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().unaffected().defaultBlockState());
			for (int x = -tr - 1; x <= tr + 1; x += 2) k.set(x, h + 2, -tr - 1 + Math.abs(x) / 3, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState());
			for (int i = 0; i < 4; i++) {
				Direction d = Direction.from2DDataValue(i);
				for (int s = 1; s <= tr; s++) k.set(d.getStepX() * s, y + 5 - s / 2, d.getStepZ() * s, Kit.axis(p.chain, d.getAxis()));
			}
			k.set(0, y - 1, 0, p.light);
			return;
		}
		if (obs) {
			k.dome(0, h + 1, 0, tr, p.glass);
			k.ring(0, h + 1, 0, tr, p.trim);
			// telescope on its mount
			k.set(0, h + 1, 0, Blocks.LODESTONE.defaultBlockState());
			BlockState tube = fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().exposed().defaultBlockState();
			k.set(1, h + 2, 0, tube);
			k.set(2, h + 3, 0, tube);
			k.set(0, h + 2, 0, tube);
			k.stair(3, h + 4, 0, fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER_STAIRS.waxed().exposed().defaultBlockState(), Direction.WEST, false);
			k.set(-1, h + 1, 0, p.fence);
			k.set(-1, h + 2, 0, Kit.slabOf(p.woodSlab, false));
			if (k.world == 8) {
				// armillary of the solar observatory: two gold rings around a light
				for (int a = 0; a < 24; a++) {
					double t = a * Math.PI / 12;
					int rx = (int) Math.round(Math.cos(t) * 3), ry = (int) Math.round(Math.sin(t) * 3);
					k.set(rx, h + 5 + ry, -3, Blocks.GOLD_BLOCK.defaultBlockState());
				}
				k.set(0, h + 5, -3, Blocks.SHROOMLIGHT.defaultBlockState());
			}
			return;
		}
		if (k.id.equals("needle_tower")) {
			BlockState iron = Blocks.IRON_BLOCK.defaultBlockState();
			for (int yy = y; yy < y + 8; yy++) {
				k.set(0, yy, 0, iron);
				if (yy < y + 4) { k.set(1, yy, 0, iron); k.set(0, yy, 1, iron); k.set(1, yy, 1, iron); }
			}
			k.set(0, y + 6, 0, p.fill);
			k.set(0, y + 8, 0, Blocks.END_ROD.defaultBlockState());
			k.set(0, y + 9, 0, Blocks.END_ROD.defaultBlockState());
			// red thread wound around the tower and through the eye
			BlockState thread = fr.achedon12.matriochka.mc.McBlocks.WOOL.red().defaultBlockState();
			for (int yy = 2; yy < h; yy++) {
				double t = yy * 0.45;
				k.set((int) Math.round(Math.cos(t) * (tr + 1)), yy, (int) Math.round(Math.sin(t) * (tr + 1)), thread);
			}
			return;
		}
		if (k.world == 5) {
			int tip = k.cone(0, h + 2, 0, tr, 2.0);
			k.set(0, tip + 1, 0, Blocks.SOUL_CAMPFIRE.defaultBlockState());
			for (int x = -tr - 1; x <= tr + 1; x += tr + 1)
				for (int z = -tr - 1; z <= tr + 1; z += tr + 1) if (x != 0 || z != 0) k.brazier(x, h + 1, z);
			return;
		}
		int tip = k.cone(0, h + 2, 0, tr, Math.max(0.8, Math.min(1.6, (37.0 - h - 2) / (tr + 1))));
		k.set(0, tip + 1, 0, p.wall);
		k.lanternOn(0, tip + 2, 0);
	}

	/** Feet of the walking tower: four buttress legs ending in toes. */
	private static void legs(Kit k, int tr) {
		Palette p = k.p;
		for (int i = 0; i < 4; i++) {
			double a = Math.PI / 4 + i * Math.PI / 2;
			for (int s = 0; s <= 4; s++) {
				int x = (int) Math.round(Math.cos(a) * (tr + s)), z = (int) Math.round(Math.sin(a) * (tr + s));
				int top = 9 - s * 2;
				for (int y = -1; y <= top; y++) k.set(x, y, z, s == 4 ? p.cap : p.base);
				k.stair(x, top + 1, z, Kit.inward(x, z), false);
			}
		}
	}

	/** Floating rock the inverted structures hang from (drawn in local space above the flipped floor). */
	static void anchorRock(Kit k, int rad) {
		Palette p = k.p;
		k.ellipsoid(0, -4, 0, rad + 1, 4, rad + 1, p.found, 0);
		k.ellipsoid(0, -6, 0, rad, 2, rad, p.soil, 0);
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			int x = (int) Math.round(Math.cos(a) * rad), z = (int) Math.round(Math.sin(a) * rad);
			k.set(x, -9, z, p.growth.isAir() ? p.cap : p.growth);
			k.set(x, -8, z, p.accent);
		}
	}

	/** Ladder column from the real ground to the lowest point of a flipped structure's door. */
	private static void access(Kit k, int tr) {
		boolean f = k.flip;
		int top = k.flipY - 4;
		k.flip = false;
		for (int y = 1; y <= top; y++) {
			k.set(0, y, -tr - 3, k.p.base);
			k.set(0, y, -tr - 4, Kit.ladderFacing(Direction.NORTH));
		}
		k.set(0, top, -tr - 2, k.p.trim);
		k.set(0, top, -tr - 1, k.p.trim);
		k.flip = f;
	}

	// ---------------------------------------------------------------- lighthouse
	static void lighthouse(Kit k) {
		Palette p = k.p;
		boolean sunk = k.world == 7;
		if (sunk) { k.sink = 2; k.shear = 0.06; }
		int tr = 5, h = Math.min(k.H, 24);
		k.site(k.R, h + 12);
		BlockState stripe = fr.achedon12.matriochka.mc.McBlocks.CONCRETE.pick(p.colB).defaultBlockState();
		k.disc(0, 0, 0, tr + 2, p.trim);
		for (int y = 1; y <= h; y++) {
			double rad = tr + 1 - 2.0 * y / h;
			BlockState s = ((y - 1) / 4) % 2 == 0 ? p.base : stripe;
			int ir = (int) Math.ceil(rad) + 1;
			for (int x = -ir; x <= ir; x++)
				for (int z = -ir; z <= ir; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > rad + 0.5) continue;
					if (d > rad - 0.5) k.set(x, y, z, s); else k.air(x, y, z);
				}
		}
		for (int y = 6; y < h; y += 6) k.roundFloor(0, y, 0, tr - 1 - (2.0 * y / h));
		for (int y = 3; y < h - 2; y += 6) {
			double rad = tr + 1 - 2.0 * y / h;
			int rr = (int) Math.round(rad);
			k.set(rr, y, 0, p.pane); k.set(rr, y + 1, 0, p.pane);
			k.set(-rr, y, 0, p.pane); k.set(-rr, y + 1, 0, p.pane);
			k.set(0, y, rr, p.pane); k.set(0, y + 1, rr, p.pane);
		}
		k.doorway(0, 1, -tr - 1, Direction.NORTH, 1, 3);
		// gallery and lantern room
		int gr = tr + 1;
		k.disc(0, h, 0, gr, p.trim);
		k.air(-1, h, -1, 1, h, 1);
		k.set(0, h, 0, p.pillar);
		k.spiral(0, 0, 1, h);
		for (int x = -gr - 2; x <= gr + 2; x++)
			for (int z = -gr - 2; z <= gr + 2; z++) {
				if (k.onRing(x, z, gr + 1)) {
					k.stair(x, h, z, Kit.inward(x, z), true);
					k.set(x, h + 1, z, p.bars);
				}
			}
		int lr = 3;
		for (int y = h + 1; y <= h + 4; y++)
			for (int x = -lr - 1; x <= lr + 1; x++)
				for (int z = -lr - 1; z <= lr + 1; z++) {
					if (!k.onRing(x, z, lr)) continue;
					boolean post = (x == 0 || z == 0);
					k.set(x, y, z, post ? p.pillar : p.pane);
				}
		k.air(0, h + 1, -lr, 0, h + 2, -lr);
		for (int y = h + 1; y <= h + 3; y++) k.set(0, y, 0, y == h + 2 ? p.accent : p.light);
		k.set(1, h + 2, 0, p.light); k.set(-1, h + 2, 0, p.light); k.set(0, h + 2, 1, p.light); k.set(0, h + 2, -1, p.light);
		k.disc(0, h + 5, 0, lr + 1, p.trim);
		int tip = k.cone(0, h + 6, 0, lr, 1.2);
		k.set(0, tip + 1, 0, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState());
		// keeper's cottage
		Parts.house(k, tr + 2, -3, Math.min(k.R - 1, tr + 7), 3, 0, 1, Direction.NORTH, 2);
		// rooms
		k.mark("hidden", 3, 1, 2, Direction.WEST);
		k.mark("hidden", -3, 7, 0, Direction.EAST);
		k.mark("hidden", 2, 13, -2, Direction.WEST);
		k.mark("reading", 0, 7, 3, Direction.NORTH);
		k.shelves(-3, 2, -2, 2, 7, 2);
		k.bed(3, 13, 0, Direction.SOUTH, p.colA);
		k.hang(2, 11, 0, 1);
		k.hang(-2, 17, 0, 1);
		k.crates(-3, 1, -1);
		k.set(-2, 1, 2, Blocks.CAULDRON.defaultBlockState());
		k.decay(-k.R, 0, -k.R, k.R, h + 8, k.R, sunk ? 0.5 : 0.15);
	}

	// ---------------------------------------------------------------- clock tower
	static void clock(Kit k) {
		Palette p = k.p;
		int hw = 5, h = Math.min(k.H, 24);
		k.site(k.R, h + 12);
		// courtyard with gear wheels set in the paving
		for (int x = -k.R + 1; x <= k.R - 1; x++)
			for (int z = -k.R + 1; z <= k.R - 1; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > k.R - 1) continue;
				k.set(x, 0, z, ((int) d) % 4 == 0 ? p.inlay : p.floor);
			}
		for (int[] g : new int[][] {{-11, -11}, {11, -11}, {-11, 11}, {11, 11}}) gear(k, g[0], 0, g[1], 3);
		// stepped plinth
		k.box(-hw - 2, 1, -hw - 2, hw + 2, 1, hw + 2, p.trim);
		for (int x = -hw - 3; x <= hw + 3; x++)
			for (int z = -hw - 3; z <= hw + 3; z++)
				if (Math.max(Math.abs(x), Math.abs(z)) == hw + 3) k.stair(x, 1, z, Kit.inward(x, z), false);
		// body with corner buttresses
		for (int y = 2; y <= h; y++)
			for (int x = -hw; x <= hw; x++)
				for (int z = -hw; z <= hw; z++) {
					boolean edge = Math.abs(x) == hw || Math.abs(z) == hw;
					if (!edge) { k.air(x, y, z); continue; }
					BlockState s = (y - 2) % 6 == 0 ? p.trim : (y % 6 == 5 ? p.alt : p.base);
					k.set(x, y, z, s);
				}
		for (int[] c : new int[][] {{hw, hw}, {-hw, hw}, {hw, -hw}, {-hw, -hw}})
			for (int y = 2; y <= h + 1; y++) {
				k.set(c[0] + Integer.signum(c[0]), y, c[1], p.pillar);
				k.set(c[0], y, c[1] + Integer.signum(c[1]), p.pillar);
			}
		// floors with a central well for the pendulum
		int floors = 0;
		for (int y = 8; y < h - 5; y += 6) {
			k.floor(-hw + 1, -hw + 1, hw - 1, hw - 1, y, 2);
			k.air(-1, y, -1, 1, y, 1);
			for (int x = -2; x <= 2; x++) { k.set(x, y + 1, -2, p.fence); k.set(x, y + 1, 2, p.fence); }
			for (int z = -1; z <= 1; z++) { k.set(-2, y + 1, z, p.fence); k.set(2, y + 1, z, p.fence); }
			floors++;
		}
		k.floor(-hw + 1, -hw + 1, hw - 1, hw - 1, 1, 1);
		// corner ladder
		for (int y = 2; y < h; y++) k.set(hw - 1, y, hw - 1, Kit.ladderFacing(Direction.WEST));
		// pendulum
		int pt = h;
		for (int y = 4; y <= pt; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		k.set(0, 3, 0, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(0, 2, 0, Blocks.HEAVY_WEIGHTED_PRESSURE_PLATE.defaultBlockState());
		// windows
		for (int y = 4; y < h - 8; y += 6)
			for (int s = -2; s <= 2; s += 4) {
				for (int yy = y; yy < y + 3; yy++) {
					k.set(s, yy, -hw, p.pane); k.set(s, yy, hw, p.pane); k.set(-hw, yy, s, p.pane); k.set(hw, yy, s, p.pane);
				}
			}
		k.doorway(0, 2, -hw, Direction.NORTH, 3, 4);
		// four clock faces
		int fy = h - 5;
		for (int i = 0; i < 4; i++) clockFace(k, Direction.from2DDataValue(i), hw, fy);
		// belfry and roof
		int by = h + 1;
		k.box(-hw - 1, by, -hw - 1, hw + 1, by, hw + 1, p.trim);
		for (int[] c : new int[][] {{hw, hw}, {-hw, hw}, {hw, -hw}, {-hw, -hw}, {0, hw}, {0, -hw}, {hw, 0}, {-hw, 0}})
			for (int y = by + 1; y <= by + 4; y++) k.set(c[0], y, c[1], p.pillar);
		for (int y = by + 1; y <= by + 3; y++) k.air(-hw + 1, y, -hw + 1, hw - 1, y, hw - 1);
		k.box(-hw, by + 5, -hw, hw, by + 5, hw, p.trim);
		k.set(0, by + 4, 0, p.plank);
		k.set(0, by + 3, 0, Kit.facing(Blocks.BELL.defaultBlockState(), Direction.NORTH).setValue(BellBlock.ATTACHMENT, BellAttachType.CEILING));
		int top = k.hip(-hw, -hw, hw, hw, by + 6, 1);
		k.set(0, top + 1, 0, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState());
		// clockwork chamber at the top floor
		int cy = 8 + (floors - 1) * 6;
		for (int z = -hw + 1; z <= hw - 1; z += hw * 2 - 2) for (int a = 0; a < 16; a++) {
			double t = a * Math.PI / 8;
			int gx = (int) Math.round(Math.cos(t) * 2.5), gy = (int) Math.round(Math.sin(t) * 2.5);
			k.set(gx, cy + 3 + gy, z, fr.achedon12.matriochka.mc.McBlocks.COPPER_GRATE.waxed().exposed().defaultBlockState());
		}
		k.set(-hw + 1, cy + 1, 0, p.accent);
		k.set(hw - 1, cy + 1, 0, p.accent);
		k.mark("guard", -3, cy + 1, hw - 1, Direction.NORTH);
		k.mark("spawner", 3, cy + 1, -3, Direction.NORTH);
		k.mark("spawner", -3, cy + 1, -3, Direction.NORTH);
		k.mark("spawner", 3, cy + 1, 3, Direction.NORTH);
		for (int f = 0; f < floors; f++) {
			int y = 8 + f * 6;
			k.mark("hidden", -hw + 1, y + 1, -hw + 1, Direction.SOUTH);
			k.crates(hw - 2, y + 1, -hw + 1);
			k.hang(-3, y + 5, 3, 1);
		}
		k.mark("hidden", -hw + 1, 2, hw - 1, Direction.EAST);
		k.mark("reading", 0, 2, hw - 1, Direction.NORTH);
		// sundial obelisks along the axes
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			int ox = d.getStepX() * (k.R - 4), oz = d.getStepZ() * (k.R - 4);
			if (d == Direction.NORTH) ox += 4;
			for (int y = 1; y <= 5; y++) k.set(ox, y, oz, y == 5 ? p.cap : p.pillar);
			k.set(ox, 6, oz, p.accent);
		}
		k.decay(-k.R, 0, -k.R, k.R, h + 10, k.R, 0.2);
	}

	private static void gear(Kit k, int cx, int y, int cz, int rad) {
		BlockState cu = fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().exposed().defaultBlockState();
		k.ring(cx, y, cz, rad, cu);
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			k.set(cx + (int) Math.round(Math.cos(a) * (rad + 1)), y, cz + (int) Math.round(Math.sin(a) * (rad + 1)), cu);
		}
		k.set(cx, y, cz, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(cx + 1, y, cz, cu); k.set(cx - 1, y, cz, cu); k.set(cx, y, cz + 1, cu); k.set(cx, y, cz - 1, cu);
	}

	/** A round clock face on one side of the tower: ring, dial, twelve markers and two hands. */
	private static void clockFace(Kit k, Direction side, int hw, int fy) {
		Palette p = k.p;
		Direction right = side.getClockWise();
		int ox = side.getStepX() * (hw + 1), oz = side.getStepZ() * (hw + 1);
		BlockState dial = Blocks.SMOOTH_QUARTZ.defaultBlockState();
		BlockState rim = fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().weathered().defaultBlockState();
		for (int a = -4; a <= 4; a++)
			for (int b = -4; b <= 4; b++) {
				double d = Math.sqrt(a * a + b * b);
				if (d > 4.5) continue;
				int x = ox + right.getStepX() * a, z = oz + right.getStepZ() * a;
				k.set(x, fy + b, z, d > 3.5 ? rim : dial);
			}
		for (int i = 0; i < 12; i++) {
			double t = i * Math.PI / 6;
			int a = (int) Math.round(Math.cos(t) * 3), b = (int) Math.round(Math.sin(t) * 3);
			k.set(ox + right.getStepX() * a, fy + b, oz + right.getStepZ() * a, i % 3 == 0 ? Blocks.GOLD_BLOCK.defaultBlockState() : p.accent);
		}
		BlockState hand = Blocks.POLISHED_BLACKSTONE.defaultBlockState();
		k.set(ox, fy + 1, oz, hand);
		k.set(ox, fy + 2, oz, hand);
		int hx = ox + right.getStepX(), hz = oz + right.getStepZ();
		k.set(hx, fy, hz, hand);
		k.set(hx + right.getStepX(), fy - 1, hz + right.getStepZ(), hand);
		k.set(ox, fy, oz, Blocks.GOLD_BLOCK.defaultBlockState());
	}
}
