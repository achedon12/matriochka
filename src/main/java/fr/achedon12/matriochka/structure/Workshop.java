package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.BaseModel;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * World 10 at doll scale. The Giant Workshop is the Artisan's workshop seen by a doll: its felt floor is strewn with
 * spools, nails, pins, buttons, thimbles, scissors, pencils and wood offcuts many times the player's height, and the
 * Titanic Workbench stands over everything with the Maquette of the player's base on its top.
 * <p>
 * The props are scenery (role "decor": no chest, no page). Each is a handful of solid shapes (rods, discs, rings),
 * so replaying the build for every chunk stays cheap.
 */
final class Workshop {
	private Workshop() {}

	private static final DyeColor[] THREAD = {DyeColor.RED, DyeColor.BLUE, DyeColor.YELLOW, DyeColor.GREEN, DyeColor.PURPLE, DyeColor.ORANGE, DyeColor.CYAN, DyeColor.WHITE};
	private static final BlockState IRON = Blocks.IRON_BLOCK.defaultBlockState();
	private static final BlockState STEEL = Blocks.POLISHED_ANDESITE.defaultBlockState();
	private static final BlockState GOLD = Blocks.GOLD_BLOCK.defaultBlockState();

	static BlockState wool(DyeColor c) {
		return Blocks.WOOL.pick(c).defaultBlockState();
	}

	static BlockState concrete(DyeColor c) {
		return Blocks.CONCRETE.pick(c).defaultBlockState();
	}

	static void prop(Kit k) {
		switch (k.archetype) {
			case "prop_spool" -> spool(k);
			case "prop_nail" -> nail(k);
			case "prop_pin" -> pin(k);
			case "prop_button" -> button(k);
			case "prop_thimble" -> thimble(k);
			case "prop_scissors" -> scissors(k);
			case "prop_pencil" -> pencil(k);
			default -> offcuts(k);
		}
	}

	// ---------------------------------------------------------------- shapes
	/** A round rod of radius r from one point to another (local coordinates, chunk-safe). */
	static void rod(Kit k, double x0, double y0, double z0, double x1, double y1, double z1, double r, BlockState s) {
		double dx = x1 - x0, dy = y1 - y0, dz = z1 - z0, len2 = Math.max(1e-6, dx * dx + dy * dy + dz * dz);
		int ax = (int) Math.floor(Math.min(x0, x1) - r), bx = (int) Math.ceil(Math.max(x0, x1) + r);
		int ay = (int) Math.floor(Math.min(y0, y1) - r), by = (int) Math.ceil(Math.max(y0, y1) + r);
		int az = (int) Math.floor(Math.min(z0, z1) - r), bz = (int) Math.ceil(Math.max(z0, z1) + r);
		for (int x = ax; x <= bx; x++)
			for (int y = ay; y <= by; y++)
				for (int z = az; z <= bz; z++) {
					double t = Math.max(0, Math.min(1, ((x - x0) * dx + (y - y0) * dy + (z - z0) * dz) / len2));
					double ex = x - (x0 + dx * t), ey = y - (y0 + dy * t), ez = z - (z0 + dz * t);
					if (ex * ex + ey * ey + ez * ez <= r * r) k.set(x, y, z, s);
				}
	}

	/** A disc of radius r and thickness th lying across an axis: X, Y or Z, centred on (cx, cy, cz). */
	static void plate(Kit k, char axis, double cx, double cy, double cz, double r, int th, BlockState s, double hole) {
		int ir = (int) Math.ceil(r);
		for (int a = -ir; a <= ir; a++)
			for (int b = -ir; b <= ir; b++) {
				double d = Math.sqrt(a * a + b * b);
				if (d > r || d < hole) continue;
				for (int t = 0; t < th; t++) {
					switch (axis) {
						case 'x' -> k.set((int) cx + t, (int) cy + a, (int) cz + b, s);
						case 'z' -> k.set((int) cx + a, (int) cy + b, (int) cz + t, s);
						default -> k.set((int) cx + a, (int) cy + t, (int) cz + b, s);
					}
				}
			}
	}

	// ---------------------------------------------------------------- the props
	/** A wooden spool wound with thread, standing or on its side, a loose end trailing on the felt. */
	static void spool(Kit k) {
		BlockState wood = k.coin(0.5) ? Blocks.SPRUCE_PLANKS.defaultBlockState() : Blocks.BIRCH_PLANKS.defaultBlockState();
		DyeColor c = k.pick(THREAD);
		BlockState thread = wool(c), band = wool(k.pick(THREAD));
		boolean standing = k.coin(0.6);
		k.site(9, 16);
		if (standing) {
			plate(k, 'y', 0, 1, 0, 7.5, 2, wood, 1.5);
			plate(k, 'y', 0, 12, 0, 7.5, 2, wood, 1.5);
			for (int y = 3; y <= 11; y++) plate(k, 'y', 0, y, 0, 5.5, 1, y == 6 || y == 7 ? band : thread, 1.5);
			// the loose end: down the side and across the floor
			for (int y = 1; y <= 8; y++) k.set(6, y, 0, thread);
			for (int i = 0; i < 12; i++) k.set(6 + i, 1, (int) Math.round(Math.sin(i * 0.6) * 2), thread);
		} else {
			plate(k, 'x', -7, 8, 0, 7.5, 2, wood, 1.5);
			plate(k, 'x', 6, 8, 0, 7.5, 2, wood, 1.5);
			for (int x = -5; x <= 5; x++) plate(k, 'x', x, 8, 0, 5.5, 1, x == 0 ? band : thread, 1.5);
			for (int i = 0; i < 14; i++) k.set((int) Math.round(Math.sin(i * 0.5) * 2), 1, 6 + i, thread);
		}
	}

	/** A nail driven into the floor at a slant, or one lying on its side. */
	static void nail(Kit k) {
		k.site(8, 30);
		if (k.coin(0.65)) {
			int h = k.ri(18, 28), tx = k.ri(-4, 4), tz = k.ri(-4, 4);
			rod(k, 0, -3, 0, tx, h, tz, 1.3, IRON);
			plate(k, 'y', tx, h + 1, tz, 4.2, 1, IRON, 0);
			// a ring of splinters where it bit into the floor
			for (int i = 0; i < 6; i++) {
				int x = (int) Math.round(Math.cos(i * 1.05) * 3), z = (int) Math.round(Math.sin(i * 1.05) * 3);
				k.set(x, 1, z, Kit.slabOf(Blocks.SPRUCE_SLAB.defaultBlockState(), false));
			}
		} else {
			rod(k, -14, 2, 0, 9, 2, 0, 1.3, IRON);
			plate(k, 'x', 10, 4, 0, 4.2, 1, IRON, 0);
		}
		// a little rust
		for (int x = -14; x <= 12; x++) for (int y = 0; y <= 28; y++) for (int z = -5; z <= 5; z++) {
			if (k.hc(x, y, z, 801, 0.04) && Blocks.IRON_BLOCK.defaultBlockState().equals(k.get(x, y, z))) k.set(x, y, z, Blocks.RAW_IRON_BLOCK.defaultBlockState());
		}
	}

	/** A dressmaker's pin with a round coloured head, stuck in at a slant. */
	static void pin(Kit k) {
		k.site(6, 26);
		int h = k.ri(16, 22), tx = k.ri(-6, 6), tz = k.ri(-6, 6);
		rod(k, 0, -2, 0, tx, h, tz, 0.6, STEEL);
		k.ellipsoid(tx, h + 2, tz, 3.2, 3.2, 3.2, concrete(k.pick(THREAD)), 0);
	}

	/** A sewing button lying flat: a rim, four holes and sometimes the thread still through them. */
	static void button(Kit k) {
		DyeColor c = k.pick(THREAD);
		BlockState body = concrete(c), rim = Blocks.DYED_TERRACOTTA.pick(c).defaultBlockState();
		double r = k.ri(6, 8) + 0.5;
		k.site((int) r + 1, 8);
		plate(k, 'y', 0, 1, 0, r, 2, body, 0);
		k.ring(0, 3, 0, r - 0.5, rim);
		for (int[] h : new int[][] {{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) for (int y = 1; y <= 2; y++) {
			k.air(h[0], y, h[1]);
			k.air(h[0] + 1, y, h[1]);
			k.air(h[0], y, h[1] + 1);
			k.air(h[0] + 1, y, h[1] + 1);
		}
		if (k.coin(0.5)) {
			BlockState thread = wool(k.pick(THREAD));
			rod(k, -1.5, 3, -1.5, 2.5, 3, 2.5, 0.5, thread);
			rod(k, 2.5, 3, -1.5, -1.5, 3, 2.5, 0.5, thread);
		}
	}

	/** A thimble standing open side down, dimpled all over, with a gap a doll can walk through. */
	static void thimble(Kit k) {
		k.site(8, 14);
		BlockState dimple = STEEL;
		for (int y = 1; y <= 10; y++) {
			double r = 6.5 - y * 0.12;
			int ir = (int) Math.ceil(r);
			for (int x = -ir; x <= ir; x++)
				for (int z = -ir; z <= ir; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > r) continue;
					if (d > r - 1.2) k.set(x, y, z, k.hc(x, y, z, 811, 0.3) && (y & 1) == 0 ? dimple : IRON);
					else k.air(x, y, z);
				}
		}
		k.dome(0, 11, 0, 5.8, IRON);
		// the dent a doll gets in by
		for (int y = 1; y <= 4; y++) for (int z = -1; z <= 1; z++) for (int x = 4; x <= 7; x++) k.air(x, y, z);
		k.set(0, 10, 0, ModContent.block("lacquer_glow").defaultBlockState());
	}

	/** Planks cut off the Artisan's work: boards lying across each other, felt scraps draped over them. */
	static void offcuts(Kit k) {
		k.site(12, 10);
		BlockState[] woods = {Blocks.OAK_PLANKS.defaultBlockState(), Blocks.SPRUCE_PLANKS.defaultBlockState(), Blocks.BIRCH_PLANKS.defaultBlockState(),
			ModContent.block("giant_plank").defaultBlockState()};
		int n = k.ri(3, 5);
		for (int i = 0; i < n; i++) {
			BlockState w = k.pick(woods);
			boolean alongX = k.coin(0.5);
			int len = k.ri(10, 18), wide = k.ri(3, 5), cx = k.ri(-6, 6), cz = k.ri(-6, 6), rise = k.coin(0.4) ? k.ri(2, 5) : 0, base = 1 + i / 2;
			for (int a = -len / 2; a <= len / 2; a++) {
				int y = base + (rise == 0 ? 0 : (int) Math.round((a + len / 2.0) / len * rise));
				for (int b = 0; b < wide; b++) for (int t = 0; t < 2; t++) {
					if (alongX) k.set(cx + a, y + t, cz + b, w);
					else k.set(cx + b, y + t, cz + a, w);
				}
			}
		}
		// felt scraps
		DyeColor[] felt = {DyeColor.RED, DyeColor.YELLOW, DyeColor.GREEN};
		for (int i = 0; i < 3; i++) {
			int cx = k.ri(-8, 8), cz = k.ri(-8, 8);
			BlockState scrap = Blocks.CARPET.pick(felt[i]).defaultBlockState();
			for (int x = cx - 2; x <= cx + 2; x++) for (int z = cz - 2; z <= cz + 2; z++) {
				for (int y = 12; y >= 1; y--) {
					if (k.solidAt(x, y - 1, z) && k.emptyAt(x, y, z)) {
						k.set(x, y, z, scrap);
						break;
					}
				}
			}
		}
	}

	/** A pair of scissors left open on the floor. */
	static void scissors(Kit k) {
		k.site(17, 6);
		rod(k, -2, 1.5, -1, 16, 1.5, 4, 1.1, IRON);
		rod(k, -2, 1.5, 1, 16, 1.5, -4, 1.1, IRON);
		plate(k, 'y', 0, 3, 0, 1.6, 1, GOLD, 0);
		BlockState grip = concrete(k.pick(THREAD));
		for (int s : new int[] {-1, 1}) {
			rod(k, -2, 1.5, s, -6, 1.5, s * 4, 1.0, IRON);
			for (int y = 1; y <= 2; y++) k.ring(-9, y, s * 5, 3.5, grip);
		}
	}

	/** A yellow pencil on its side, sharpened, an eraser at its end. */
	static void pencil(Kit k) {
		k.site(17, 8);
		BlockState body = concrete(DyeColor.YELLOW), lead = concrete(DyeColor.BLACK);
		rod(k, -9, 3, 0, 8, 3, 0, 2.6, body);
		rod(k, 9, 3, 0, 10, 3, 0, 2.6, IRON);
		rod(k, 11, 3, 0, 13, 3, 0, 2.6, concrete(DyeColor.PINK));
		for (int x = -16; x <= -10; x++) {
			double r = 2.6 * (x + 17) / 8.0;
			plate(k, 'x', x, 3, 0, r, 1, x <= -15 ? lead : Blocks.BIRCH_PLANKS.defaultBlockState(), 0);
		}
	}

	// ---------------------------------------------------------------- the Titanic Workbench
	/**
	 * A carpenter's bench as tall as a house: four great legs, a top 33 blocks wide, the Artisan's tools lying on it
	 * (a hammer, a saw, a rule, a spool, nails) around a framed board at its centre where the Maquette of the
	 * player's base is set (see world/BaseModel). Two hidden chests in its drawer, one on the spool, one under it.
	 */
	static void workbench(Kit k) {
		var p = k.p;
		int hw = 16, ty = BaseModel.TOP - 2;
		k.site(k.R, BaseModel.TOP + 14);
		// legs and stretchers
		for (int[] c : new int[][] {{-hw + 1, -hw + 1}, {hw - 3, -hw + 1}, {-hw + 1, hw - 3}, {hw - 3, hw - 3}})
			for (int y = 1; y < ty; y++) k.box(c[0], y, c[1], c[0] + 2, y, c[1] + 2, p.log);
		for (int s : new int[] {-1, 1}) {
			int e = s < 0 ? -hw + 2 : hw - 2;
			for (int a = -hw + 4; a <= hw - 4; a++) {
				k.set(a, 4, e, Kit.axis(p.log, Direction.Axis.X));
				k.set(e, 4, a, Kit.axis(p.log, Direction.Axis.Z));
			}
		}
		// the top, its planks running one way, a lacquer edge
		k.box(-hw, ty, -hw, hw, ty + 1, hw, p.alt);
		for (int x = -hw; x <= hw; x++) for (int z = -hw; z <= hw; z++) {
			boolean edge = Math.abs(x) == hw || Math.abs(z) == hw;
			if (edge) k.set(x, ty + 1, z, p.trim);
			else if (Math.floorMod(x, 5) == 0) k.set(x, ty + 1, z, Blocks.SPRUCE_PLANKS.defaultBlockState());
		}
		// the Maquette board: a birch baseboard in a gold frame at the centre (kept clear for the model)
		for (int x = -9; x <= 9; x++) for (int z = -9; z <= 9; z++) {
			boolean frame = Math.abs(x) == 9 || Math.abs(z) == 9;
			k.set(x, ty + 1, z, frame ? GOLD : Blocks.BIRCH_PLANKS.defaultBlockState());
			if (frame) k.set(x, ty + 2, z, Kit.slabOf(Blocks.SMOOTH_STONE_SLAB.defaultBlockState(), false));
		}
		int top = ty + 2;
		// a hammer
		for (int x = -14; x <= -3; x++) k.set(x, top, -13, Kit.axis(p.log, Direction.Axis.X));
		k.box(-2, top, -15, 1, top + 2, -11, IRON);
		// a saw along the east edge
		for (int z = -12; z <= 5; z++) {
			k.set(13, top, z, IRON);
			if ((z & 1) == 0) k.set(14, top, z, Blocks.IRON_BARS.defaultBlockState());
		}
		k.box(12, top, 6, 14, top + 1, 9, p.plank);
		// a folding rule along the south edge
		for (int x = -14; x <= 14; x++) k.set(x, top, 13, (x & 1) == 0 ? Blocks.CONCRETE.pick(DyeColor.YELLOW).defaultBlockState() : Blocks.CONCRETE.pick(DyeColor.BLACK).defaultBlockState());
		// a spool of the Artisan's own thread
		for (int y = top; y <= top + 4; y++)
			for (int a = -2; a <= 2; a++) for (int b = -2; b <= 2; b++) {
				double d = Math.sqrt(a * a + b * b);
				if (d > 2.5) continue;
				boolean end = y == top || y == top + 4;
				k.set(-13 + a, y, 6 + b, end ? Blocks.SPRUCE_PLANKS.defaultBlockState() : d <= 1.2 ? ModContent.block("artisan_thread_ore").defaultBlockState() : wool(DyeColor.BLUE));
			}
		// nails spilled near the hammer
		rod(k, 4, top, -13, 9, top, -12, 0.5, IRON);
		rod(k, 6, top, -10, 10, top, -14, 0.5, IRON);
		// drawer under the top
		k.shell(-6, ty - 3, -hw + 1, 6, ty - 1, -hw + 5, p.plank);
		k.air(-5, ty - 2, -hw + 1, 5, ty - 2, -hw + 1);
		k.set(0, ty - 2, -hw, GOLD);
		k.mark("hidden", -3, ty - 2, -hw + 3, Direction.NORTH);
		k.mark("hidden", 3, ty - 2, -hw + 3, Direction.NORTH);
		k.mark("hidden", -13, top + 5, 6, Direction.NORTH);
		k.mark("hidden", 0, 1, 0, Direction.NORTH);
		k.mark("guard", 0, 1, 3, Direction.NORTH);
		// a giant ladder up one leg
		for (int y = 1; y <= ty + 1; y++) k.set(-hw + 2, y, -hw, Kit.ladderFacing(Direction.NORTH));
		// felt scraps and pins on the floor
		for (int i = 0; i < 6; i++) {
			int x = (int) Math.round(Math.cos(i) * 12), z = (int) Math.round(Math.sin(i) * 12);
			k.box(x - 1, 1, z - 1, x + 1, 1, z + 1, p.inlay);
			k.set(x, 2, z, Blocks.END_ROD.defaultBlockState());
		}
		Halls.doll(k, 11, -11, 3, k.variant);
		k.decay(-k.R, 1, -k.R, k.R, ty - 1, k.R, 0.06);
	}
}
