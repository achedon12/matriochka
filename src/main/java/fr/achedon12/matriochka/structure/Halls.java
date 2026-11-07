package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Monumental archetypes: temple, cathedral, throne, library, lab, shrine and the Guardian's sanctuary. */
final class Halls {
	private Halls() {}

	// ---------------------------------------------------------------- temple
	static void temple(Kit k) {
		switch (k.world) {
			case 1, 7 -> ziggurat(k);
			case 2 -> carved(k);
			case 10 -> workshop(k);
			default -> classical(k);
		}
	}

	/** Stepped pyramid with a grand stair, a terrace shrine on top and a pillared hall inside the base. */
	private static void ziggurat(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 30);
		int tiers = 4;
		for (int t = 0; t < tiers; t++) {
			int hw = R - 2 - 3 * t, y0 = 3 * t + 1;
			for (int x = -hw; x <= hw; x++)
				for (int z = -hw; z <= hw; z++) {
					boolean edge = Math.max(Math.abs(x), Math.abs(z)) == hw;
					for (int y = y0; y < y0 + 3; y++) {
						BlockState s = p.base;
						if (edge) s = y == y0 ? p.trim : y == y0 + 2 ? p.alt : ((x + z) % 4 == 0 ? p.accent : p.base);
						k.set(x, y, z, s);
					}
					if (!edge && Math.max(Math.abs(x), Math.abs(z)) > hw - 3) k.set(x, y0 + 2, z, ((x * 3 + z) & 3) == 0 ? p.inlay : p.floor);
				}
			for (int[] c : new int[][] {{hw - 1, hw - 1}, {-hw + 1, hw - 1}, {hw - 1, -hw + 1}, {-hw + 1, -hw + 1}}) k.brazier(c[0], y0 + 3, c[1]);
			for (int x = -hw; x <= hw; x++) {
				k.stair(x, y0 + 2, -hw - 1, Direction.SOUTH, true);
				k.stair(x, y0 + 2, hw + 1, Direction.NORTH, true);
			}
			for (int z = -hw + 1; z < hw; z++) {
				k.stair(-hw - 1, y0 + 2, z, Direction.EAST, true);
				k.stair(hw + 1, y0 + 2, z, Direction.WEST, true);
			}
		}
		int top = 3 * tiers;
		// grand stair on the north face
		for (int y = 1; y <= top; y++) {
			int z = -(R - 1) + y - 1;
			for (int x = -2; x <= 2; x++) {
				k.stair(x, y, z, Direction.SOUTH, false);
				for (int yy = 1; yy < y; yy++) k.set(x, yy, z, p.base);
				for (int yy = y + 1; yy <= y + 3; yy++) k.air(x, yy, z);
			}
			for (int s : new int[] {-3, 3}) {
				for (int yy = 1; yy <= y; yy++) k.set(s, yy, z, p.alt);
				k.set(s, y + 1, z, p.wall);
				if (y % 4 == 0) k.lanternOn(s, y + 2, z);
			}
		}
		// summit shrine
		k.room(-4, -4, 4, 4, top, 6, 4, 0, p.base);
		k.doorway(0, top + 1, -4, Direction.NORTH, 3, 4);
		k.hip(-4, -4, 4, 4, top + 7, 1);
		k.box(-1, top + 1, 1, 1, top + 1, 3, p.trim);
		k.set(0, top + 2, 2, p.cap);
		k.set(0, top + 3, 2, p.accent);
		k.candles(-1, top + 2, 2, 4);
		k.candles(1, top + 2, 2, 3);
		k.banner(-2, top + 4, 3, Direction.NORTH, p.colA);
		k.banner(2, top + 4, 3, Direction.NORTH, p.colB);
		k.hang(0, top + 5, -1, 1);
		k.mark("hidden", -3, top + 1, 3, Direction.EAST);
		// inner hall
		int hw = 10;
		k.room(-hw, -hw, hw, hw, 0, 7, 4, 0, p.base);
		for (int s : new int[] {-1, 1}) {
			int ex = s * hw;
			for (int x = ex; Math.abs(x) <= R - 2; x += s) {
				k.air(x, 1, -1, x, 4, 1);
				k.set(x, 0, 0, p.inlay);
				k.set(x, 0, -1, p.floor);
				k.set(x, 0, 1, p.floor);
				k.set(x, 5, 0, p.trim);
			}
			k.doorway(s * (R - 2), 1, 0, s > 0 ? Direction.EAST : Direction.WEST, 3, 4);
		}
		for (int x : new int[] {-5, 5})
			for (int z = -6; z <= 6; z += 4) k.pillar(x, 1, z, 6, true);
		k.runner(-1, -8, 1, 5, 1);
		k.box(-2, 1, 6, 2, 1, 8, p.trim);
		for (int x = -2; x <= 2; x++) k.stair(x, 1, 5, Direction.SOUTH, false);
		k.set(0, 2, 7, p.cap);
		k.set(0, 3, 7, p.accent);
		k.candles(-2, 2, 7, 4);
		k.candles(2, 2, 7, 4);
		for (int z = -6; z <= 6; z += 6) k.chandelier(0, 6, z, 1);
		k.mark("reading", 0, 1, -hw + 1, Direction.SOUTH);
		k.mark("hidden", hw - 1, 1, hw - 1, Direction.WEST);
		k.mark("hidden", -hw + 1, 1, hw - 1, Direction.EAST);
		k.mark("hidden", hw - 1, 1, -hw + 1, Direction.WEST);
		k.mark("secret", 0, 1, 8, Direction.NORTH);
		k.mark("guard", 0, 1, 4, Direction.NORTH);
		k.decay(-R, 1, -R, R, top + 14, R, k.world == 1 ? 0.55 : 0.35);
	}

	/** Columned temple on a podium, a cella inside the peristyle and a great gable roof with pediments. */
	private static void classical(Kit k) {
		Palette p = k.p;
		int R = k.R, e = R - 3;
		k.site(R, 34);
		for (int y = 1; y <= 3; y++)
			for (int x = -e - 1; x <= e + 1; x++)
				for (int z = -e - 1; z <= e + 1; z++) {
					boolean edge = Math.max(Math.abs(x), Math.abs(z)) == e + 1;
					k.set(x, y, z, edge ? p.trim : p.base);
				}
		k.floor(-e, -e, e, e, 3, 2);
		for (int s = 0; s < 3; s++)
			for (int x = -9; x <= 9; x++) {
				k.stair(x, s + 1, -e - 2 - (2 - s), Direction.SOUTH, false);
				for (int y = 1; y <= s; y++) k.set(x, y, -e - 2 - (2 - s), p.base);
			}
		int ph = 10;
		for (int x = -e + 1; x <= e - 1; x += 4) {
			k.pillar(x, 4, -e + 1, ph, true);
			k.pillar(x, 4, e - 1, ph, true);
		}
		for (int z = -e + 5; z <= e - 5; z += 4) {
			k.pillar(-e + 1, 4, z, ph, true);
			k.pillar(e - 1, 4, z, ph, true);
		}
		int ay = 4 + ph;
		for (int x = -e; x <= e; x++)
			for (int z = -e; z <= e; z++) {
				int d = Math.max(Math.abs(x), Math.abs(z));
				if (d >= e - 2) {
					k.set(x, ay, z, p.trim);
					k.set(x, ay + 1, z, d == e && (x + z) % 4 == 0 ? p.accent : p.alt);
				}
			}
		k.room(-8, -9, 8, 9, 3, 11, 4, 4, p.plank);
		k.doorway(0, 4, -9, Direction.NORTH, 3, 6);
		k.box(-7, ay + 1, -8, 7, ay + 1, 8, p.plank);
		int ridge = k.gable(-e, -e, e, e, ay + 2, false, p.alt);
		k.set(0, ridge, -e - 1, p.cap);
		k.set(0, ridge + 1, -e - 1, k.world == 4 ? fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().exposed().defaultBlockState() : p.accent);
		k.set(0, ridge, e + 1, p.cap);
		for (int z = -6; z <= 6; z += 3) {
			k.pillar(-4, 4, z, 10, false);
			k.pillar(4, 4, z, 10, false);
		}
		k.runner(-1, -8, 1, 4, 4);
		Parts.statue(k, 0, 4, 6, Direction.NORTH);
		k.brazier(-3, 4, 7);
		k.brazier(3, 4, 7);
		for (int z = -5; z <= 5; z += 5) k.chandelier(0, 13, z, 2);
		for (int z = -6; z <= 6; z += 4) {
			k.banner(-7, 9, z, Direction.EAST, p.colA);
			k.banner(7, 9, z, Direction.WEST, p.colB);
		}
		k.mark("reading", -7, 4, 0, Direction.EAST);
		k.mark("hidden", 7, 4, -8, Direction.WEST);
		k.mark("hidden", 7, 4, 8, Direction.WEST);
		k.mark("hidden", -7, 4, 8, Direction.EAST);
		k.mark("guard", 0, 4, -4, Direction.SOUTH);
		k.decay(-R, 1, -R, R, ridge, R, 0.2);
	}

	/** Sanctuary cut into a rock mound: a columned facade, a carved nave with lava channels and ore veins. */
	private static void carved(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 26);
		k.ellipsoid(0, 0, 2, R - 1, 17, R - 3, p.base, 0);
		k.ellipsoid(0, 1, 3, 9, 11, 12, p.fill, 0);
		k.box(-10, -10, -10, 10, -1, 16, p.base);
		k.air(-7, 1, -R, 7, 15, -11);
		k.air(-1, 1, -10, 1, 6, -9);
		k.floor(-8, -11, 8, 14, 0, 1);
		// ore veins in the carved walls
		for (int x = -10; x <= 10; x++)
			for (int y = 1; y <= 12; y++)
				for (int z = -9; z <= 16; z++) {
					double d = Math.sqrt(x * x / 81.0 + (y - 1) * (y - 1) / 121.0 + (z - 3) * (z - 3) / 144.0);
					if (d < 1.0 || d > 1.15) continue;
					if (k.hc(x, y, z, 211, 0.06)) k.set(x, y, z, ModContent.block("giant_ore_block").defaultBlockState());
					else if (k.hc(x, y, z, 212, 0.05)) k.set(x, y, z, ModContent.block("blazing_rock_ore").defaultBlockState());
					else if (k.hc(x, y, z, 213, 0.04)) k.set(x, y, z, p.light);
				}
		// facade
		for (int x = -7; x <= 7; x++)
			for (int y = 1; y <= 15; y++) k.set(x, y, -11, y == 1 ? p.trim : y >= 13 ? p.alt : p.base);
		for (int x : new int[] {-6, -3, 3, 6}) {
			k.pillar(x, 1, -12, 12, true);
		}
		for (int x = -8; x <= 8; x++) {
			k.set(x, 13, -12, p.trim);
			k.stair(x, 14, -13, Direction.SOUTH, true);
		}
		for (int i = 0; i <= 7; i++)
			for (int x = -7 + i; x <= 7 - i; x++) {
				boolean edge = x == -7 + i || x == 7 - i;
				k.set(x, 14 + i, -12, edge ? Kit.stairOf(p.stair, x < 0 ? Direction.EAST : Direction.WEST, false) : p.alt);
			}
		k.set(0, 17, -12, p.accent);
		k.doorway(0, 1, -11, Direction.NORTH, 3, 6);
		// lava channels under grates
		for (int z = -8; z <= 12; z++)
			for (int x : new int[] {-4, 4}) {
				k.set(x, -1, z, p.base);
				k.set(x, 0, z, Blocks.LAVA.defaultBlockState());
				k.set(x, 1, z, p.bars);
			}
		for (int z = -6; z <= 10; z += 4) {
			k.pillar(-7, 1, z, 9, true);
			k.pillar(7, 1, z, 9, true);
		}
		// forge altar
		k.box(-3, 1, 11, 3, 1, 13, p.trim);
		for (int x = -3; x <= 3; x++) k.stair(x, 1, 10, Direction.SOUTH, false);
		k.set(-1, 2, 12, Blocks.ANVIL.defaultBlockState());
		k.set(1, 2, 12, Blocks.LAVA_CAULDRON.defaultBlockState());
		k.set(0, 2, 13, p.accent);
		k.set(0, 3, 13, p.cap);
		k.set(0, 4, 13, p.light);
		for (int z = -6; z <= 10; z += 4) k.hang(0, 10, z, 3);
		// reading chamber off the east wall
		k.air(9, 1, 0, 13, 5, 6);
		k.floor(9, 0, 13, 6, 0, 0);
		k.box(14, 0, -1, 14, 6, 7, p.alt);
		k.box(9, 6, -1, 13, 6, 7, p.alt);
		k.mark("reading", 13, 1, 3, Direction.WEST);
		k.hang(11, 5, 3, 0);
		k.mark("hidden", -8, 1, 12, Direction.EAST);
		k.mark("hidden", 8, 1, -8, Direction.WEST);
		k.mark("hidden", -8, 1, -8, Direction.EAST);
		k.mark("guard", 0, 1, 8, Direction.NORTH);
		k.decay(-R, 1, -R, R, 22, R, 0.2);
	}

	/** The Artisan's giant workshop: a lacquered hall with a giant workbench, spools, scissors and dolls. */
	private static void workshop(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 30);
		int ex = R - 3, ez = R - 5;
		k.room(-ex, -ez, ex, ez, 0, 12, 5, 5, null);
		k.gable(-ex, -ez, ex, ez, 12, true, p.alt);
		k.doorway(0, 1, -ez, Direction.NORTH, 5, 8);
		// giant workbench
		for (int[] c : new int[][] {{-6, -3}, {5, -3}, {-6, 2}, {5, 2}})
			for (int y = 1; y <= 5; y++) k.box(c[0], y, c[1], c[0] + 1, y, c[1] + 1, p.log);
		k.box(-7, 6, -4, 7, 6, 4, p.alt);
		for (int x = -7; x <= 7; x++) { k.set(x, 6, -4, p.trim); k.set(x, 6, 4, p.trim); }
		// spool lying on the bench
		for (int x = -5; x <= -1; x++)
			for (int a = -2; a <= 2; a++)
				for (int b = -2; b <= 2; b++) {
					double d = Math.sqrt(a * a + b * b);
					if (d > 2.5) continue;
					boolean end = x == -5 || x == -1;
					if (end) k.set(x, 9 + b, a, Blocks.SPRUCE_PLANKS.defaultBlockState());
					else if (d <= 1.5) k.set(x, 9 + b, a, ModContent.block("artisan_thread_ore").defaultBlockState());
					else k.set(x, 9 + b, a, fr.achedon12.matriochka.mc.McBlocks.WOOL.red().defaultBlockState());
				}
		// open scissors
		for (int i = 0; i <= 5; i++) {
			k.set(1 + i, 7, -2 + i / 2, Blocks.IRON_BLOCK.defaultBlockState());
			k.set(1 + i, 7, 2 - i / 2, Blocks.IRON_BLOCK.defaultBlockState());
		}
		k.ring(1, 7, -3, 1, Blocks.GOLD_BLOCK.defaultBlockState());
		k.ring(1, 7, 3, 1, Blocks.GOLD_BLOCK.defaultBlockState());
		// thimble
		k.tube(5, -1, 1.5, 7, 9, Blocks.IRON_BLOCK.defaultBlockState());
		k.disc(5, 10, -1, 1.5, Blocks.IRON_BLOCK.defaultBlockState());
		// row of nesting dolls along the walls
		for (int i = 0; i < 4; i++) {
			int z = -ez + 3 + i * 5;
			doll(k, -ex + 3, z, 4 - i / 2, i);
			doll(k, ex - 3, z, 4 - i / 2, i + 1);
		}
		k.runner(-1, -ez + 1, 1, -5, 1);
		for (int x = -10; x <= 10; x += 10) k.chandelier(x, 11, 0, 2);
		k.box(-ex + 1, 1, ez - 1, -ex + 4, 1, ez - 1, p.alt);
		k.mark("reading", 0, 1, ez - 1, Direction.NORTH);
		k.mark("hidden", -1, 1, 0, Direction.NORTH);
		k.mark("hidden", ex - 1, 1, ez - 1, Direction.WEST);
		k.mark("hidden", -ex + 1, 1, -ez + 1, Direction.EAST);
		k.mark("guard", 0, 7, 0, Direction.NORTH);
		k.shelves(ex - 1, -ez + 2, ex - 1, -ez + 6, 1, 4);
		k.workbench(ex - 2, 1, 0, Direction.WEST);
		k.decay(-R, 1, -R, R, 30, R, 0.1);
	}

	/** A painted nesting doll: an egg of lacquer with painted bands and a face. */
	static void doll(Kit k, int cx, int cz, int size, int salt) {
		DyeColor[] cols = {DyeColor.RED, DyeColor.YELLOW, DyeColor.BLUE, DyeColor.GREEN, DyeColor.ORANGE};
		BlockState band = fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(cols[Math.floorMod(salt, cols.length)]).defaultBlockState();
		double rx = size * 0.6 + 0.5, ry = size + 0.5;
		k.ellipsoid(cx, size + 1, cz, rx, ry, rx, k.p.trim, 0);
		for (int a = -size; a <= size; a++)
			for (int b = -size; b <= size; b++) {
				double d = Math.sqrt(a * a / (rx * rx) + b * b / (rx * rx));
				if (d <= 1.0) k.set(cx + a, size + 1, cz + b, band);
			}
		int hy = size + 1 + (int) (ry * 0.55);
		k.set(cx, hy, cz - (int) Math.round(rx), fr.achedon12.matriochka.mc.McBlocks.WOOL.white().defaultBlockState());
		k.set(cx, hy + 1, cz - (int) Math.round(rx), Blocks.GOLD_BLOCK.defaultBlockState());
	}

	// ---------------------------------------------------------------- cathedral
	static void cathedral(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 36);
		int nw = 5, z0 = -14, z1 = 11;
		// aisles
		k.room(-nw - 4, z0, nw + 4, z1, 0, 8, 4, 4, p.plank);
		// nave walls rising above the aisles, clerestory windows
		for (int z = z0; z <= z1; z++)
			for (int s : new int[] {-nw, nw})
				for (int y = 1; y <= 16; y++) {
					boolean win = y >= 11 && y <= 14 && Math.floorMod(z - z0, 4) == 2;
					k.set(s, y, z, win ? p.pane : y == 9 || y == 16 ? p.trim : p.base);
				}
		k.air(-nw + 1, 1, z0 + 1, nw - 1, 16, z1 - 1);
		k.air(-nw - 3, 1, z0 + 1, -nw - 1, 7, z1 - 1);
		k.air(nw + 1, 1, z0 + 1, nw + 3, 7, z1 - 1);
		// arcades between nave and aisles
		for (int z = z0 + 2; z < z1; z += 4) {
			for (int s : new int[] {-nw, nw}) {
				k.air(s, 1, z - 1, s, 5, z + 1);
				k.stair(s, 5, z - 1, Direction.NORTH, true);
				k.stair(s, 5, z + 1, Direction.SOUTH, true);
			}
		}
		// transept
		k.room(-R + 3, -2, R - 3, 4, 0, 12, 4, 6, null);
		k.air(-nw - 4, 1, -2, nw + 4, 7, 4);
		k.air(-R + 4, 1, -1, R - 4, 11, 3);
		k.gable(-R + 3, -2, R - 3, 4, 12, true, p.alt);
		k.air(-nw + 1, 1, z0 + 1, nw - 1, 16, z1 - 1);
		// nave roof, steep
		k.gable(-nw, z0, nw, z1, 17, false, p.alt);
		// apse with a half dome
		for (int x = -5; x <= 5; x++)
			for (int z = 0; z <= 5; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > 5.5) continue;
				int zz = z1 + z;
				for (int y = 0; y <= 12; y++) {
					if (y == 0) k.set(x, y, zz, p.floor);
					else if (d > 4.5) k.set(x, y, zz, y >= 6 && y <= 10 && Math.abs(x) % 3 == 1 ? p.pane : p.base);
					else k.air(x, y, zz);
				}
				for (int h = 0; h <= 6; h++) {
					double dd = Math.sqrt(x * x + z * z + h * h);
					if (dd > 5.5) continue;
					if (dd > 4.5) k.set(x, 13 + h, zz, h == 0 ? p.trim : p.roof);
					else k.air(x, 13 + h, zz);
				}
			}
		k.air(-4, 1, z1, 4, 16, z1);
		// buttresses and flying buttresses
		for (int z = z0 + 2; z < z1; z += 4)
			for (int s : new int[] {-1, 1}) {
				int bx = s * (nw + 5);
				for (int y = 1; y <= 9; y++) k.set(bx, y, z, p.alt);
				k.stair(bx, 10, z, s > 0 ? Direction.WEST : Direction.EAST, false);
				for (int i = 1; i <= 4; i++) k.stair(bx - s * i, 9 + i, z, s > 0 ? Direction.EAST : Direction.WEST, true);
				k.set(bx, 11, z, p.cap);
			}
		// twin towers on the facade
		for (int s : new int[] {-1, 1}) {
			int tx = s * (nw + 3);
			k.room(tx - 2, z0 - 3, tx + 2, z0 + 1, 0, 22, 0, 3, p.plank);
			for (int y = 1; y <= 22; y++) k.set(tx - 1, y, z0 - 2, Kit.ladderFacing(Direction.EAST));
			k.air(tx - 1, 22, z0 - 2, tx - 1, 22, z0 - 2);
			int tip = k.hip(tx - 2, z0 - 3, tx + 2, z0 + 1, 23, 0);
			for (int y = tip; y < tip + 4; y++) k.set(tx, y, z0 - 1, p.wall);
			k.set(tx, tip + 4, z0 - 1, k.world == 5 ? Blocks.SOUL_LANTERN.defaultBlockState() : p.lantern);
		}
		// facade: rose window and great door
		for (int x = -nw; x <= nw; x++)
			for (int y = 1; y <= 16; y++) k.set(x, y, z0, y == 1 ? p.trim : p.base);
		for (int a = -3; a <= 3; a++)
			for (int b = -3; b <= 3; b++) {
				double d = Math.sqrt(a * a + b * b);
				if (d > 3.5) continue;
				k.set(a, 12 + b, z0, d > 2.5 ? p.trim : (a == 0 || b == 0 || Math.abs(a) == Math.abs(b)) ? p.bars : p.pane);
			}
		k.set(0, 12, z0, p.accent);
		k.doorway(0, 1, z0, Direction.NORTH, 3, 6);
		for (int y = 1; y <= 4; y++) { k.set(-3, y, z0 - 1, p.pillar); k.set(3, y, z0 - 1, p.pillar); }
		k.arch(-3, 3, 5, z0 - 1, true, 1);
		k.air(-2, 1, z0 - 1, 2, 4, z0 - 1);
		// interior: floor, pews, altar, light
		k.floor(-nw + 1, z0 + 1, nw - 1, z1 - 1, 0, 1);
		k.runner(0, z0 + 1, 0, z1 - 2, 1);
		for (int z = z0 + 3; z <= -3; z += 2)
			for (int x = 1; x <= 3; x++) {
				k.chair(x, 1, z, Direction.SOUTH);
				k.chair(-x, 1, z, Direction.SOUTH);
			}
		k.box(-3, 1, z1, 3, 1, z1 + 3, p.trim);
		for (int x = -3; x <= 3; x++) k.stair(x, 1, z1 - 1, Direction.SOUTH, false);
		k.box(-1, 2, z1 + 2, 1, 2, z1 + 2, p.cap);
		k.candles(-1, 3, z1 + 2, 4);
		k.candles(1, 3, z1 + 2, 4);
		k.set(0, 3, z1 + 2, p.accent);
		for (int y = 1; y <= 8; y++) k.set(0, y, z1 + 4, y == 6 ? p.light : y < 4 ? p.trim : p.pillar);
		k.set(-1, 6, z1 + 4, p.wall);
		k.set(1, 6, z1 + 4, p.wall);
		for (int z = z0 + 3; z < z1 - 2; z += 5) k.chandelier(0, 22, z, 7);
		for (int z = z0 + 4; z < z1; z += 4) {
			k.banner(-nw + 1, 8, z, Direction.EAST, p.colA);
			k.banner(nw - 1, 8, z, Direction.WEST, p.colB);
		}
		// crypt under the apse: the guarded loot room
		int cy = -6;
		k.shell(-5, cy, z1 - 4, 5, cy + 5, z1 + 4, p.alt);
		k.floor(-4, z1 - 3, 4, z1 + 3, cy, 2);
		for (int y = cy + 1; y <= 0; y++) k.set(4, y, z1 - 3, Kit.ladderFacing(Direction.WEST));
		k.set(4, 1, z1 - 3, p.fill);
		k.set(4, 0, z1 - 3, Kit.ladderFacing(Direction.WEST));
		for (int x = -4; x <= 4; x += 4) {
			k.set(x, cy + 1, z1 + 3, p.cap);
			k.set(x, cy + 2, z1 + 3, Blocks.SKELETON_SKULL.defaultBlockState());
		}
		k.hang(0, cy + 4, z1, 1);
		k.mark("guard", 0, cy + 1, z1 + 2, Direction.NORTH);
		k.mark("spawner", -3, cy + 1, z1 - 2, Direction.NORTH);
		k.mark("spawner", 3, cy + 1, z1 + 1, Direction.NORTH);
		k.mark("spawner", -3, cy + 1, z1 + 2, Direction.NORTH);
		k.mark("hidden", -nw - 3, 1, z1 - 1, Direction.EAST);
		k.mark("hidden", nw + 3, 1, z0 + 2, Direction.WEST);
		k.mark("reading", -R + 4, 1, 1, Direction.EAST);
		k.decay(-R, 1, -R, R, 30, R, 0.3);
	}

	// ---------------------------------------------------------------- throne
	static void throne(Kit k) {
		Palette p = k.p;
		int hw = 7, z0 = -10, z1 = 10;
		k.site(k.R, 24);
		k.room(-hw, z0, hw, z1, 0, 10, 4, 4, null);
		k.hip(-hw, z0, hw, z1, 11, 1);
		k.box(-hw + 1, 10, z0 + 1, hw - 1, 10, z1 - 1, p.fill);
		k.doorway(0, 1, z0, Direction.NORTH, 3, 5);
		for (int x = -3; x <= 3; x++) k.stair(x, 0, z0 - 1, Direction.SOUTH, false);
		for (int s : new int[] {-1, 1}) { k.standingBanner(s * 3, 1, z0 - 2, s < 0 ? p.colA : p.colB); k.brazier(s * 4, 0, z0 - 2); }
		k.floor(-hw + 1, z0 + 1, hw - 1, z1 - 1, 0, 1);
		for (int z = z0 + 3; z <= z1 - 5; z += 4) {
			k.pillar(-4, 1, z, 9, true);
			k.pillar(4, 1, z, 9, true);
			k.banner(-4, 7, z - 1, Direction.NORTH, p.colA);
			k.banner(4, 7, z - 1, Direction.NORTH, p.colB);
		}
		k.runner(-1, z0 + 1, 1, 4, 1);
		// dais of three steps
		for (int s = 0; s < 3; s++) {
			int zz = 5 + s;
			for (int x = -4 + s; x <= 4 - s; x++) {
				for (int y = 1; y <= s; y++) k.set(x, y, zz, p.trim);
				k.stair(x, s + 1, zz, Direction.SOUTH, false);
			}
		}
		k.box(-3, 1, 8, 3, 3, 9, p.trim);
		// the throne
		int ty = 4;
		k.stair(0, ty, 8, p.woodStair, Direction.SOUTH, false);
		k.set(-1, ty, 8, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(1, ty, 8, Blocks.GOLD_BLOCK.defaultBlockState());
		k.stair(-1, ty + 1, 8, Direction.EAST, true);
		k.stair(1, ty + 1, 8, Direction.WEST, true);
		for (int y = ty; y <= ty + 5; y++) k.set(0, y, 9, y == ty + 5 ? Blocks.GOLD_BLOCK.defaultBlockState() : p.trim);
		for (int y = ty + 1; y <= ty + 3; y++) { k.set(-1, y, 9, p.alt); k.set(1, y, 9, p.alt); }
		k.set(-1, ty + 4, 9, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(1, ty + 4, 9, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(0, ty + 6, 9, p.accent);
		k.brazier(-3, 4, 8);
		k.brazier(3, 4, 8);
		for (int z = z0 + 4; z <= z1 - 4; z += 6) k.chandelier(0, 9, z, 2);
		for (int z = z0 + 2; z <= z1 - 2; z += 4) {
			k.banner(-hw + 1, 6, z, Direction.EAST, p.colA);
			k.banner(hw - 1, 6, z, Direction.WEST, p.colB);
		}
		// hidden passage: the carpet in front of the throne hides a hatch into the treasure room under the dais
		k.shell(-3, -6, 5, 3, -1, 10, p.alt);
		k.floor(-2, 6, 2, 9, -6, 1);
		for (int y = -5; y <= 3; y++) k.set(0, y, 7, Kit.ladderFacing(Direction.NORTH));
		k.set(0, 4, 7, p.fill);
		k.carpet(0, 4, 7, p.colA);
		k.set(0, 3, 8, p.trim);
		k.set(-2, -5, 9, p.light);
		k.set(2, -5, 9, p.light);
		k.set(0, -5, 9, p.cap);
		k.candles(-2, -4, 9, 4);
		k.candles(2, -4, 9, 4);
		k.mark("secret", 0, -4, 9, Direction.NORTH);
		k.mark("hidden", -hw + 1, 1, z1 - 1, Direction.EAST);
		k.mark("hidden", hw - 1, 1, z0 + 1, Direction.WEST);
		k.mark("guard", 0, 1, 3, Direction.NORTH);
		k.mark("reading", -hw + 1, 1, 0, Direction.EAST);
		k.decay(-k.R, 1, -k.R, k.R, 22, k.R, 0.12);
	}

	// ---------------------------------------------------------------- library
	static void library(Kit k) {
		Palette p = k.p;
		boolean big = k.large();
		boolean giant = k.world == 10;
		boolean fresco = k.id.contains("fresco");
		int hw = big ? 12 : 7, hl = k.R - 2;
		int wh = big ? 12 : 10, mez = 5;
		k.site(k.R, wh + 14);
		k.room(-hw, -hl, hw, hl, 0, wh, 4, 0, null);
		k.gable(-hw, -hl, hw, hl, wh, false, p.alt);
		// clerestory windows
		for (int z = -hl + 2; z <= hl - 2; z += 4)
			for (int y = mez + 2; y <= wh - 2; y++) { k.set(-hw, y, z, p.pane); k.set(hw, y, z, p.pane); }
		for (int a = -2; a <= 2; a++)
			for (int y = mez + 1; y <= wh - 1; y++) k.set(a, y, hl, Math.abs(a) == 2 ? p.pillar : p.pane);
		// entrance porch
		if (k.world == 3) {
			k.air(-1, 1, -hl, 1, 3, -hl);
			for (int x = -1; x <= 1; x++) for (int y = 1; y <= 3; y++) k.set(x, y, -hl, ModContent.block("sealed_door").defaultBlockState());
			k.set(-2, 4, -hl - 1, p.lantern);
		} else k.doorway(0, 1, -hl, Direction.NORTH, 3, 4);
		k.pillar(-3, 1, -hl - 2, 6, false);
		k.pillar(3, 1, -hl - 2, 6, false);
		k.box(-4, 7, -hl - 3, 4, 7, -hl - 1, p.trim);
		for (int x = -4; x <= 4; x++) k.stair(x, 8, -hl - 3, Direction.SOUTH, false);
		k.box(-3, 8, -hl - 2, 3, 8, -hl - 1, p.roof);
		// walls of books on two levels, a mezzanine with a railing
		for (int z = -hl + 1; z <= hl - 1; z++) {
			for (int s : new int[] {-1, 1}) {
				int x = s * (hw - 1);
				boolean gap = Math.floorMod(z + hl, 4) == 0;
				if (fresco) fresco(k, x, z, 1, mez - 1, s);
				else if (giant) giantBooks(k, x, z, 1, mez - 1);
				else if (!gap) k.shelves(x, z, x, z, 1, mez - 1);
				k.set(x, mez, z, p.plank);
				k.set(x - s, mez, z, p.plank);
				k.set(x - 2 * s, mez + 1, z, p.fence);
				if (fresco) fresco(k, x, z, mez + 1, wh - mez - 2, s);
				else if (giant) giantBooks(k, x, z, mez + 1, wh - mez - 2);
				else if (!gap) k.shelves(x, z, x, z, mez + 1, 3);
				k.set(x - s, mez, z, Kit.slabOf(p.woodSlab, true));
			}
		}
		// stairs to the mezzanine
		for (int i = 0; i < mez; i++) {
			k.stair(hw - 3, i + 1, -hl + 2 + i, Direction.SOUTH, false);
			k.air(hw - 3, mez + 1, -hl + 2 + i);
		}
		// reading tables down the nave
		k.floor(-hw + 1, -hl + 1, hw - 1, hl - 1, 0, 2);
		for (int z = -hl + 4; z <= hl - 5; z += 5) {
			k.banquet(0, 1, z, Math.min(2 * hw - 8, 6), true);
			k.set(-hw + 3, 1, z, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.EAST));
			k.chandelier(0, wh - 1, z, 2);
		}
		if (giant) {
			// a giant open book lies on the floor at the far end
			for (int x = -5; x <= 5; x++)
				for (int z = hl - 7; z <= hl - 3; z++) {
					int yy = 1 + Math.abs(x) / 3;
					k.set(x, yy, z, x == 0 ? p.trim : fr.achedon12.matriochka.mc.McBlocks.WOOL.white().defaultBlockState());
				}
			for (int y = 1; y <= 7; y++) k.tube(hw - 4, hl - 4, 1, y, y, fr.achedon12.matriochka.mc.McBlocks.WOOL.white().defaultBlockState());
			k.set(hw - 4, 8, hl - 4, p.light);
		}
		k.mark("reading", 0, 1, hl - 1, Direction.NORTH);
		// chests hidden behind a bookshelf: set into the outer wall
		k.mark("hidden", -hw, 2, -hl + 3, Direction.EAST);
		k.set(-hw + 1, 2, -hl + 3, Blocks.BOOKSHELF.defaultBlockState());
		k.set(-hw - 1, 2, -hl + 3, p.base);
		k.set(hw + 1, 2, hl - 3, p.base);
		k.mark("hidden", hw, 2, hl - 3, Direction.WEST);
		k.set(hw - 1, 2, hl - 3, Blocks.BOOKSHELF.defaultBlockState());
		k.mark("hidden", -hw + 2, mez + 1, hl - 2, Direction.EAST);
		k.mark("hidden", hw - 2, mez + 1, -hl + 2 + mez + 1, Direction.WEST);
		k.mark("guard", 0, 1, 0, Direction.NORTH);
		k.decay(-k.R, 1, -k.R, k.R, wh + 12, k.R, k.world == 3 ? 0.35 : 0.15);
	}

	/** Fresco panel: framed mosaic of the world colours, drawn as a column of the wall. */
	private static void fresco(Kit k, int x, int z, int y0, int h, int s) {
		BlockState a = fr.achedon12.matriochka.mc.McBlocks.CONCRETE.pick(k.p.colA).defaultBlockState(), b = fr.achedon12.matriochka.mc.McBlocks.CONCRETE.pick(k.p.colB).defaultBlockState();
		BlockState w = fr.achedon12.matriochka.mc.McBlocks.CONCRETE.white().defaultBlockState(), g = fr.achedon12.matriochka.mc.McBlocks.CONCRETE.yellow().defaultBlockState();
		for (int y = y0; y < y0 + h; y++) {
			int u = Math.floorMod(z, 8), v = y - y0;
			BlockState c;
			if (u == 0 || v == 0 || v == h - 1) c = k.p.trim;
			else {
				int f = (u * 7 + v * 3 + (z / 8) * 5) % 9;
				c = f < 3 ? a : f < 5 ? b : f < 7 ? w : f == 7 ? g : k.p.light;
			}
			k.set(x, y, z, c);
			k.set(x + s, y, z, k.p.base);
		}
	}

	/** Shelf of giant books: tall wool spines on plank shelves. */
	private static void giantBooks(Kit k, int x, int z, int y0, int h) {
		DyeColor[] cols = {DyeColor.RED, DyeColor.BLUE, DyeColor.GREEN, DyeColor.BROWN, DyeColor.PURPLE, DyeColor.ORANGE};
		DyeColor c = cols[k.hi(x, y0, z, 223, cols.length)];
		int bh = h - k.hi(x, y0, z, 227, 2);
		for (int y = y0; y < y0 + h; y++) k.set(x, y, z, y < y0 + bh ? fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(c).defaultBlockState() : k.p.fill);
		if (bh > 2) k.set(x, y0 + bh / 2, z, Blocks.GOLD_BLOCK.defaultBlockState());
	}

	// ---------------------------------------------------------------- lab
	static void lab(Kit k) {
		if (k.p.underwater) station(k); else gravityLab(k);
	}

	/** Underwater research station: glass domes joined by tubes, dry inside, entered by a moon pool. */
	private static void station(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 22);
		BlockState glass = Blocks.GLASS.defaultBlockState();
		// legs and deck
		int dy = 3;
		for (int[] c : new int[][] {{-6, -6}, {6, -6}, {-6, 6}, {6, 6}, {-14, 0}, {14, 0}})
			for (int y = 0; y < dy; y++) k.set(c[0], y, c[1], p.pillar);
		hab(k, 0, dy, 0, 8, glass);
		hab(k, -13, dy, 0, 4, glass);
		hab(k, 13, dy, 0, 4, glass);
		// tubes
		for (int s : new int[] {-1, 1})
			for (int x = s * 8; Math.abs(x) <= 10; x += s) {
				k.box(x, dy, -2, x, dy + 4, 2, p.trim);
				for (int z = -1; z <= 1; z++) for (int y = dy + 1; y <= dy + 3; y++) k.set(x, y, z, Blocks.AIR.defaultBlockState());
				k.set(x, dy + 2, -2, glass);
				k.set(x, dy + 2, 2, glass);
				k.set(x, dy + 4, 0, p.light);
			}
		// moon pool in the west module: open water under an air pocket
		k.box(-14, dy, -1, -12, dy, 1, p.fill);
		k.box(-14, dy - 1, -1, -12, dy - 1, 1, p.fill);
		for (int x = -15; x <= -11; x++) for (int z = -2; z <= 2; z++) if (Math.abs(x + 13) == 2 || Math.abs(z) == 2) k.set(x, dy, z, p.trim);
		// main hall
		k.roundFloor(0, dy, 0, 7);
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			int x = d.getStepX() * 5, z = d.getStepZ() * 5;
			if (d.getAxis() == Direction.Axis.X) continue;
			k.set(x - 1, dy + 1, z, Kit.facing(Blocks.LECTERN.defaultBlockState(), d.getOpposite()));
			k.set(x, dy + 1, z, Blocks.BREWING_STAND.defaultBlockState());
			k.set(x + 1, dy + 1, z, Blocks.CAULDRON.defaultBlockState());
		}
		// specimen tanks: glass columns of water with glowing coral
		for (int[] c : new int[][] {{-4, -3}, {4, -3}, {-4, 3}, {4, 3}}) {
			k.set(c[0], dy + 1, c[1], p.trim);
			for (int y = dy + 2; y <= dy + 4; y++) k.set(c[0], y, c[1], y == dy + 3 ? p.accent : glass);
			k.set(c[0], dy + 5, c[1], p.trim);
		}
		k.set(0, dy + 1, 0, ModContent.block("abyssal_press").defaultBlockState());
		k.bed(12, dy + 1, -2, Direction.SOUTH, p.colA);
		k.bed(14, dy + 1, -2, Direction.SOUTH, p.colB);
		k.crates(12, dy + 1, 2);
		k.mark("npc", 2, dy + 1, 1, Direction.NORTH);
		k.mark("hidden", -6, dy + 1, 0, Direction.EAST);
		k.mark("hidden", 14, dy + 1, 1, Direction.WEST);
		k.mark("hidden", -12, dy + 1, -2, Direction.SOUTH);
		k.mark("reading", 0, dy + 1, 6, Direction.NORTH);
		k.mark("guard", 0, dy + 1, -6, Direction.SOUTH);
		// beacon buoy line up the water column
		for (int y = dy + 10; y <= 36; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		k.set(0, 37, 0, p.light);
		k.decay(-R, 0, -R, R, 16, R, 0.15);
	}

	/** Glass dome habitat on a ring footing, dry inside. */
	private static void hab(Kit k, int cx, int y, int cz, int rad, BlockState glass) {
		Palette p = k.p;
		k.disc(cx, y, cz, rad, p.floor);
		k.ring(cx, y, cz, rad, p.trim);
		int ir = rad + 1;
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++)
				for (int h = 1; h <= ir; h++) {
					double d = Math.sqrt(x * x + z * z + h * h);
					if (d > rad + 0.5) continue;
					if (d > rad - 0.6) k.set(cx + x, y + h, cz + z, h <= 1 || (x == 0 || z == 0) ? p.trim : glass);
					else k.set(cx + x, y + h, cz + z, Blocks.AIR.defaultBlockState());
				}
		k.set(cx, y + rad, cz, p.light);
	}

	/** Gravity laboratory: a two-storey lab whose upper floor is furnished on the ceiling, with floating specimens. */
	private static void gravityLab(Kit k) {
		Palette p = k.p;
		int R = k.R;
		int hw = R - 3, hd = R - 4;
		k.site(R, 26);
		k.room(-hw, -hd, hw, hd, 0, 5, 4, 2, p.alt);
		k.room(-hw, -hd, hw, hd, 6, 6, 4, 3, null);
		int roofTop = k.hip(-hw, -hd, hw, hd, 13, 1);
		k.set(0, roofTop + 1, 0, p.glass);
		k.set(0, roofTop + 2, 0, p.light);
		k.set(0, roofTop + 3, 0, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().unaffected().defaultBlockState());
		k.box(-hw + 1, 12, -hd + 1, hw - 1, 12, hd - 1, p.alt);
		k.doorway(0, 1, -hd, Direction.NORTH, 3, 3);
		for (int y = 1; y <= 6; y++) k.set(hw - 1, y, hd - 1, Kit.ladderFacing(Direction.WEST));
		// ground floor: benches of brewing and cauldrons
		for (int x = -hw + 2; x <= hw - 3; x += 3) {
			k.set(x, 1, -hd + 1, Blocks.BREWING_STAND.defaultBlockState());
			k.set(x + 1, 1, -hd + 1, Blocks.CAULDRON.defaultBlockState());
			k.set(x, 1, hd - 1, p.plank);
			k.slab(x, 2, hd - 1, p.woodSlab, false);
		}
		k.set(0, 1, 0, ModContent.block("inverter").defaultBlockState());
		for (int[] c : new int[][] {{-4, 0}, {4, 0}}) {
			k.set(c[0], 1, c[1], p.trim);
			for (int y = 2; y <= 4; y++) k.set(c[0], y, c[1], y == 3 ? p.accent : p.glass);
		}
		// upper floor: everything hangs from the ceiling, as if gravity had turned
		boolean f = k.flip;
		k.flip = true;
		k.flipY = 12;
		k.table(-3, 1, 0);
		k.chair(-2, 1, 0, Direction.WEST);
		k.chair(-4, 1, 0, Direction.EAST);
		k.bed(3, 1, -1, Direction.SOUTH, p.colA);
		k.shelves(-hw + 1, -2, -hw + 1, 2, 1, 2);
		k.set(2, 1, 3, Blocks.BREWING_STAND.defaultBlockState());
		k.lanternOn(0, 1, 0);
		k.mark("reading", hw - 1, 1, 0, Direction.WEST);
		k.flip = f;
		// floating specimens held by chains
		for (int[] c : new int[][] {{-5, -2}, {5, 2}, {0, -3}}) {
			k.set(c[0], 11, c[1], Kit.axis(p.chain, Direction.Axis.Y));
			k.set(c[0], 10, c[1], p.cap);
		}
		k.mark("hidden", -hw + 1, 1, hd - 1, Direction.EAST);
		k.mark("hidden", hw - 1, 7, -hd + 1, Direction.WEST);
		k.mark("hidden", -hw + 1, 1, -hd + 2, Direction.EAST);
		k.mark("guard", 0, 7, -2, Direction.NORTH);
		k.mark("npc", 1, 1, 2, Direction.NORTH);
		k.decay(-R, 1, -R, R, 20, R, 0.15);
	}

	// ---------------------------------------------------------------- shrine
	static void shrine(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean frozen = k.id.equals("frozen_garden");
		boolean gate = k.id.equals("block_gate");
		boolean keys = k.id.equals("key_hall");
		boolean blind = k.id.equals("blind_sanctuary");
		k.site(R, 22);
		// ring path and garden
		for (int x = -R; x <= R; x++)
			for (int z = -R; z <= R; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > R) continue;
				if (d > R - 3 && d <= R - 1) k.set(x, 0, z, ((int) (Math.atan2(z, x) * 6)) % 2 == 0 ? p.inlay : p.floor);
				else if (d > 7 && d <= R - 3) {
					k.set(x, 0, z, frozen ? Blocks.SNOW_BLOCK.defaultBlockState() : p.soil);
					if (k.hc(x, 0, z, 301, 0.3)) {
						if (frozen) k.set(x, 1, z, k.hc(x, 1, z, 302, 0.5) ? Blocks.SNOW.defaultBlockState() : Blocks.SPRUCE_LEAVES.defaultBlockState()
							.setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT, true));
						else k.plant(x, 1, z);
					}
				} else if (d <= 7) k.set(x, 0, z, p.floor);
			}
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4 + Math.PI / 8;
			Parts.stoneLantern(k, (int) Math.round(Math.cos(a) * (R - 2)), 1, (int) Math.round(Math.sin(a) * (R - 2)));
		}
		// axial path and the gate
		for (int z = -R; z <= -6; z++) for (int x = -1; x <= 1; x++) k.set(x, 0, z, x == 0 ? p.inlay2 : p.inlay);
		int gz = -R + 2;
		int gh = gate ? 10 : 6;
		for (int s : new int[] {-3, 3}) {
			k.set(s, 1, gz, p.trim);
			for (int y = 2; y < gh; y++) k.set(s, y, gz, gate ? p.trim : p.pillar);
		}
		for (int x = -5; x <= 5; x++) {
			k.set(x, gh, gz, gate ? Blocks.GOLD_BLOCK.defaultBlockState() : p.trim);
			k.stair(x, gh + 1, gz, Math.abs(x) == 5 ? (x < 0 ? Direction.EAST : Direction.WEST) : Direction.SOUTH, Math.abs(x) == 5);
		}
		k.slab(-4, gh + 1, gz, p.roofSlab, false);
		k.slab(4, gh + 1, gz, p.roofSlab, false);
		for (int x = -2; x <= 2; x++) k.set(x, gh - 2, gz, p.trim);
		if (gate) {
			for (int x = -2; x <= 2; x++) for (int y = 2; y < gh - 2; y++) if (k.hc(x, y, gz, 303, 0.15)) k.set(x, y, gz, p.accent);
			k.set(0, gh - 1, gz, p.accent);
		}
		// stepped platform
		for (int s = 0; s < 3; s++) {
			int r2 = 6 - s;
			for (int x = -r2; x <= r2; x++)
				for (int z = -r2; z <= r2; z++) {
					int d = Math.max(Math.abs(x), Math.abs(z));
					if (d == r2) k.stair(x, s + 1, z, Kit.inward(x, z), false);
					else k.set(x, s + 1, z, s == 2 ? p.floor : p.trim);
				}
		}
		k.floor(-3, -3, 3, 3, 3, 1);
		// pavilion: six-post or four-post with a hipped roof
		int py = 4, ph = keys ? 6 : 5;
		for (int[] c : new int[][] {{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) k.pillar(c[0], py, c[1], ph, false);
		if (keys) {
			// the key hall is walled, chains and hooks like a wall of keys
			for (int x = -3; x <= 3; x++)
				for (int y = py; y < py + ph; y++) {
					if (Math.abs(x) < 3) { k.set(x, y, 3, p.base); k.set(-3, y, x, p.base); k.set(3, y, x, p.base); }
				}
			for (int x = -2; x <= 2; x += 4) for (int y = py + 1; y < py + ph - 1; y++) {
				k.set(x, y, 2, Kit.facing(Blocks.TRIPWIRE_HOOK.defaultBlockState(), Direction.NORTH));
				k.set(-2, y, x, Kit.facing(Blocks.TRIPWIRE_HOOK.defaultBlockState(), Direction.EAST));
			}
		}
		k.box(-4, py + ph, -4, 4, py + ph, 4, p.trim);
		int top = k.hip(-4, -4, 4, 4, py + ph + 1, 1);
		k.set(0, top + 1, 0, p.cap);
		k.lanternOn(0, top + 2, 0);
		for (int[] c : new int[][] {{-4, -4}, {4, -4}, {-4, 4}, {4, 4}}) k.hang(c[0], py + ph - 1, c[1], 1);
		// altar
		k.set(0, py, -1, p.trim);
		k.set(0, py + 1, -1, blind ? Blocks.SCULK_SHRIEKER.defaultBlockState() : p.cap);
		k.set(0, py + 2, -1, k.world == 9 ? p.light : p.accent);
		k.candles(-1, py, -1, 4);
		k.candles(1, py, -1, 4);
		k.pot(-2, py, -2);
		k.pot(2, py, -2);
		k.stair(0, py, -3, p.woodStair, Direction.SOUTH, false);
		if (k.world == 9) {
			// the beating vein: pulsing ribs arching over the shrine
			for (int i = 0; i < 6; i++) {
				double a = i * Math.PI / 3;
				for (int t = 0; t <= 8; t++) {
					double rr = 9 - t * 0.6;
					k.set((int) Math.round(Math.cos(a) * rr), 1 + (int) Math.round(Math.sin(t * Math.PI / 16) * 12), (int) Math.round(Math.sin(a) * rr), t % 3 == 0 ? p.light : p.cap);
				}
			}
		}
		// the reading corner fills the back of the pavilion; chests lie under the altar and the steps
		k.mark("reading", 0, py, 2, Direction.NORTH);
		k.mark("hidden", -2, py, 2, Direction.EAST);
		k.mark("hidden", -5, 1, 5, Direction.NORTH);
		k.mark("hidden", 5, 1, -5, Direction.SOUTH);
		k.mark("hidden", 0, py - 1, -1, Direction.NORTH);
		k.mark("guard", 0, py, 2, Direction.NORTH);
		k.decay(-R, 1, -R, R, 18, R, frozen ? 0.05 : 0.2);
	}

	// ---------------------------------------------------------------- the Guardian's sanctuary (Surface)
	static void sanctuary(Kit k) {
		Palette p = k.p;
		BlockState lac = ModContent.block("lacquer_block").defaultBlockState(), paint = ModContent.block("painted_wood").defaultBlockState();
		BlockState deep = Blocks.POLISHED_DEEPSLATE.defaultBlockState(), chis = Blocks.CHISELED_STONE_BRICKS.defaultBlockState();
		BlockState gold = Blocks.GOLD_BLOCK.defaultBlockState();
		int R = 11;
		k.site(R, 22);
		// three-tier round platform
		for (int t = 0; t < 3; t++) {
			double rad = R - t;
			for (int x = -R; x <= R; x++)
				for (int z = -R; z <= R; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > rad + 0.5) continue;
					if (d > rad - 0.5) k.stair(x, t, z, Kit.inward(x, z), false);
					else k.set(x, t, z, t == 2 ? deep : Blocks.STONE_BRICKS.defaultBlockState());
				}
		}
		int fy = 2;
		// floor rosette: rings of lacquer and painted wood around the altar, gold spokes
		for (int x = -7; x <= 7; x++)
			for (int z = -7; z <= 7; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > 6.5) continue;
				int ring = (int) Math.round(d);
				BlockState s = ring <= 2 ? paint : ring == 4 ? lac : ring == 6 ? Blocks.DEEPSLATE_TILES.defaultBlockState() : deep;
				if (ring >= 3 && (x == 0 || z == 0)) s = gold;
				k.set(x, fy, z, s);
			}
		// eight great pillars with arches between them and braziers on top
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			int px = (int) Math.round(Math.cos(a) * 8), pz = (int) Math.round(Math.sin(a) * 8);
			k.set(px, fy + 1, pz, chis);
			for (int dd = 0; dd < 4; dd++) {
				Direction d = Direction.from2DDataValue(dd);
				k.stair(px + d.getStepX(), fy + 1, pz + d.getStepZ(), d.getOpposite(), false);
			}
			for (int y = fy + 2; y <= fy + 8; y++) k.set(px, y, pz, y == fy + 5 ? lac : Blocks.QUARTZ_PILLAR.defaultBlockState());
			k.set(px, fy + 9, pz, chis);
			for (int dd = 0; dd < 4; dd++) {
				Direction d = Direction.from2DDataValue(dd);
				k.stair(px + d.getStepX(), fy + 9, pz + d.getStepZ(), d.getOpposite(), true);
			}
			k.set(px, fy + 10, pz, lac);
			k.set(px, fy + 11, pz, Blocks.CAMPFIRE.defaultBlockState());
			k.banner(px - Integer.signum(px), fy + 7, pz - Integer.signum(pz), Kit.inward(px, pz), i % 2 == 0 ? DyeColor.RED : DyeColor.YELLOW);
		}
		// ring beam joining the pillar heads, open to the sky over the altar
		for (int x = -9; x <= 9; x++)
			for (int z = -9; z <= 9; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > 7.5 && d <= 8.5) k.set(x, fy + 10, z, ((x + z) & 1) == 0 ? lac : paint);
				if (d > 8.5 && d <= 9.5) k.stair(x, fy + 10, z, Kit.inward(x, z), true);
			}
		// chains with lanterns hanging from the ring towards the altar
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4 + Math.PI / 8;
			k.hang((int) Math.round(Math.cos(a) * 7), fy + 9, (int) Math.round(Math.sin(a) * 7), 3);
		}
		// four axial stairways and gate posts
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			Direction side = d.getClockWise();
			for (int s = -1; s <= 1; s++) {
				for (int t = 0; t < 3; t++) {
					int dist = R - t;
					k.stair(d.getStepX() * dist + side.getStepX() * s, t, d.getStepZ() * dist + side.getStepZ() * s, d.getOpposite(), false);
				}
			}
			for (int s : new int[] {-2, 2}) {
				int gx = d.getStepX() * (R - 1) + side.getStepX() * s, gz = d.getStepZ() * (R - 1) + side.getStepZ() * s;
				k.set(gx, 1, gz, chis);
				k.set(gx, 2, gz, Blocks.STONE_BRICK_WALL.defaultBlockState());
				k.set(gx, 3, gz, lac);
				k.set(gx, 4, gz, Blocks.LANTERN.defaultBlockState());
			}
		}
		// the altar dais: painted wood disc, gold ring, candles; the altar stays at the very centre
		k.disc(0, fy, 0, 2, paint);
		k.ring(0, fy, 0, 3, gold);
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			k.candles((int) Math.round(Math.cos(a) * 3), fy + 1, (int) Math.round(Math.sin(a) * 3), 1 + i % 4);
		}
		for (int x = -2; x <= 2; x++)
			for (int z = -2; z <= 2; z++) for (int y = fy + 1; y <= 18; y++) if (x * x + z * z <= 4 && (x != 0 || z != 0 || y > fy + 1)) k.air(x, y, z);
		k.set(0, fy + 1, 0, ModContent.block("sanctuary_altar").defaultBlockState());
		k.decay(-R, 1, -R, R, 16, R, 0.08);
	}
}
