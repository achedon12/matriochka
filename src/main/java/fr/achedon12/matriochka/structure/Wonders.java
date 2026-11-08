package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The ten wonders, one per world and rarer than any structure: a place to be seen from afar, with the world's
 * reliquary at its heart (marked "secret", sealed for another world's cross key) and a vault chest (marked "guard")
 * holding this world's own key. Built in untransformed coordinates, within the large footprint (radius 18).
 */
final class Wonders {
	private Wonders() {}

	static void build(Kit k) {
		switch (k.world) {
			case 1 -> motherTree(k);
			case 2 -> moltenHeart(k);
			case 3 -> hallOfKeys(k);
			case 4 -> eyeOfTheStorm(k);
			case 5 -> lastCandle(k);
			case 6 -> upsideSpire(k);
			case 7 -> sunkenBell(k);
			case 8 -> stoppedClock(k);
			case 9 -> sleepingGiant(k);
			default -> artisansDesk(k);
		}
	}

	private static BlockState b(net.minecraft.world.level.block.Block block) {
		return block.defaultBlockState();
	}

	private static BlockState mod(String id) {
		return ModContent.block(id).defaultBlockState();
	}

	/** A round dais under the reliquary, gold ring, the vault chest beside it. */
	private static void heart(Kit k, int y, BlockState floor, BlockState ring) {
		k.disc(0, y, 0, 3.2, floor);
		k.ring(0, y, 0, 3, ring);
		for (int a = 0; a < 4; a++) {
			int x = new int[]{3, -3, 0, 0}[a], z = new int[]{0, 0, 3, -3}[a];
			k.candles(x, y + 1, z, 3);
		}
		k.mark("secret", 0, y + 1, 0, Direction.SOUTH);
		k.mark("guard", 2, y + 1, 1, Direction.WEST);
		k.mark("hidden", -2, y + 1, -1, Direction.EAST);
	}

	// ---------------------------------------------------------------- World 1: a giant tree with a hollow at its foot
	static void motherTree(Kit k) {
		Palette p = k.p;
		k.site(14, 36);
		BlockState bark = b(Blocks.JUNGLE_WOOD), wood = b(Blocks.STRIPPED_JUNGLE_WOOD), leaf = p.leaves != null ? p.leaves : b(Blocks.JUNGLE_LEAVES);
		// the trunk: a hollow cylinder that narrows, roots fanning out over the ground
		for (int y = 0; y <= 26; y++) {
			double rad = 6.5 - y * 0.13;
			k.tube(0, 0, rad, y, y, bark);
		}
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4;
			for (int d = 6; d <= 13; d++) {
				int x = (int) Math.round(Math.cos(a) * d), z = (int) Math.round(Math.sin(a) * d);
				int h = Math.max(0, 3 - (d - 6) / 2);
				for (int y = 0; y <= h; y++) k.set(x, y, z, bark);
			}
		}
		// the hollow inside, an arched way in on the south
		for (int y = 1; y <= 12; y++) k.cyl(0, 0, 6.5 - y * 0.13 - 1.6, y, y, b(Blocks.AIR));
		for (int y = 1; y <= 5; y++) for (int x = -1; x <= 1; x++) for (int z = 4; z <= 7; z++) k.air(x, y, z);
		k.disc(0, 0, 0, 4.9, wood);
		// the crown: layered discs of leaves with glowing spore blooms in them
		for (int y = 24; y <= 34; y++) {
			double rad = 13 - Math.abs(y - 28) * 1.6;
			for (int x = -14; x <= 14; x++)
				for (int z = -14; z <= 14; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d <= rad && k.hc(x, y, z, 11, 0.78)) k.set(x, y, z, k.hc(x, y, z, 12, 0.06) ? mod("spore_bloom") : leaf);
				}
		}
		for (int i = 0; i < 10; i++) k.hang(k.hi(i, 1, 1, 13, 20) - 10, 25, k.hi(i, 2, 2, 14, 20) - 10, 4);
		heart(k, 0, wood, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 2: a cavern of lava round a molten core
	static void moltenHeart(Kit k) {
		k.site(15, 24);
		BlockState rock = mod("ashrock"), ember = mod("ember_stone"), obs = b(Blocks.OBSIDIAN);
		// a crater: rings of ember stone stepping down to a lava moat
		for (int x = -15; x <= 15; x++)
			for (int z = -15; z <= 15; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > 15) continue;
				if (d > 11) k.set(x, 0, z, rock);
				else if (d > 8) { k.set(x, -1, z, b(Blocks.MAGMA_BLOCK)); k.set(x, 0, z, b(Blocks.LAVA)); }
				else k.set(x, 0, z, d > 6.5 ? ember : obs);
			}
		// four bridges of obsidian over the moat
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			for (int s = 7; s <= 12; s++) for (int w = -1; w <= 1; w++)
				k.set(d.getStepX() * s + d.getClockWise().getStepX() * w, 0, d.getStepZ() * s + d.getClockWise().getStepZ() * w, obs);
		}
		// the molten heart hanging above the dais in a cage of chains
		k.ellipsoid(0, 13, 0, 3, 3, 3, b(Blocks.MAGMA_BLOCK), 0);
		k.ellipsoid(0, 13, 0, 1.6, 1.6, 1.6, b(Blocks.SHROOMLIGHT), 0);
		for (int[] c : new int[][]{{3, 3}, {-3, 3}, {3, -3}, {-3, -3}}) for (int y = 9; y <= 17; y++) k.set(c[0], y, c[1], b(Blocks.IRON_CHAIN));
		// basalt spires around
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4 + 0.3;
			int x = (int) Math.round(Math.cos(a) * 13.5), z = (int) Math.round(Math.sin(a) * 13.5);
			for (int y = 1; y <= 6 + (i % 3) * 3; y++) k.set(x, y, z, y % 4 == 0 ? ember : b(Blocks.BASALT));
		}
		heart(k, 0, obs, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 3: a vaulted hall hung with a thousand keys
	static void hallOfKeys(Kit k) {
		Palette p = k.p;
		k.site(13, 18);
		BlockState brick = mod("dungeon_brick"), sealed = mod("sealed_brick");
		k.shell(-12, 0, -12, 12, 16, 12, brick);
		k.air(-11, 1, -11, 11, 15, 11);
		k.box(-12, 0, -12, 12, 0, 12, b(Blocks.POLISHED_DEEPSLATE));
		// pillars with cold lamps
		for (int x = -8; x <= 8; x += 8)
			for (int z = -8; z <= 8; z += 8) {
				if (x == 0 && z == 0) continue;
				for (int y = 1; y <= 15; y++) k.set(x, y, z, y % 5 == 0 ? mod("cold_lamp") : sealed);
			}
		// the keys: tripwire hooks and chains hanging from the vault, at every height
		for (int x = -10; x <= 10; x += 2)
			for (int z = -10; z <= 10; z += 2) {
				if (Math.abs(x) < 4 && Math.abs(z) < 4) continue;
				if (!k.hc(x, 0, z, 31, 0.55)) continue;
				int len = 2 + k.hi(x, 1, z, 32, 6);
				for (int y = 15; y > 15 - len; y--) k.set(x, y, z, b(Blocks.IRON_CHAIN));
				k.set(x, 15 - len, z, k.hc(x, 2, z, 33, 0.5) ? b(Blocks.TRIPWIRE_HOOK) : fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().unaffected().defaultBlockState());
			}
		// outside: buttresses, a stepped roof of sealed brick, a great gold key on every wall
		for (int i = -12; i <= 12; i += 6) if (i != 0)
			for (int[] f : new int[][]{{i, -13}, {i, 13}, {-13, i}, {13, i}})
				for (int y = 0; y <= 13 - Math.abs(i) / 6; y++) k.set(f[0], y, f[1], y % 4 == 3 ? mod("cold_lamp") : sealed);
		for (int r = 0; r <= 6; r++) k.ring(0, 17 + r, 0, 12 - r * 2, sealed);
		for (int r = 0; r <= 6; r++) k.box(-11 + r * 2, 16 + r, -11 + r * 2, 11 - r * 2, 16 + r, 11 - r * 2, r % 2 == 0 ? sealed : brick);
		for (int y = 24; y <= 27; y++) k.set(0, y, 0, y == 27 ? mod("cold_lamp") : b(Blocks.IRON_BARS));
		BlockState gold = b(Blocks.GOLD_BLOCK);
		for (int[] w : new int[][]{{0, -13, 1, 0}, {0, 13, 1, 0}, {-13, 0, 0, 1}, {13, 0, 0, 1}}) {
			// the bow: a ring, the shaft, two teeth
			for (int[] q : new int[][]{{-1, 12}, {0, 12}, {1, 12}, {-2, 11}, {2, 11}, {-2, 10}, {2, 10}, {-1, 9}, {1, 9}, {0, 9}, {0, 8}, {0, 7}, {0, 6}, {1, 6}, {1, 7}})
				k.set(w[0] + w[2] * q[0], q[1], w[1] + w[3] * q[0], gold);
		}
		// the way in, framed in gold
		for (int y = 1; y <= 4; y++) for (int x = -1; x <= 1; x++) k.air(x, y, 12);
		for (int y = 1; y <= 5; y++) { k.set(-2, y, 13, gold); k.set(2, y, 13, gold); }
		for (int x = -2; x <= 2; x++) k.set(x, 5, 13, gold);
		heart(k, 0, b(Blocks.CHISELED_DEEPSLATE), b(Blocks.GOLD_BLOCK));
		k.decay(-12, 1, -12, 12, 16, 12, 0.03);
	}

	// ---------------------------------------------------------------- World 4: a ring of floating pillars round a calm eye
	static void eyeOfTheStorm(Kit k) {
		k.site(16, 30);
		BlockState cloud = mod("cloudstone"), glass = mod("storm_glass");
		k.disc(0, 0, 0, 7.5, cloud);
		k.ring(0, 0, 0, 7, b(Blocks.GOLD_BLOCK));
		// twelve pillars standing on air in a ring, each crowned with a lightning rod
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6;
			int x = (int) Math.round(Math.cos(a) * 14), z = (int) Math.round(Math.sin(a) * 14);
			int y0 = 3 + (i % 3) * 2;
			for (int y = y0; y <= y0 + 9; y++) k.set(x, y, z, y == y0 + 4 ? glass : b(Blocks.QUARTZ_PILLAR));
			k.set(x, y0 + 10, z, fr.achedon12.matriochka.mc.McBlocks.LIGHTNING_ROD.waxed().unaffected().defaultBlockState());
			k.set(x, y0 - 1, z, cloud);
		}
		// a spiral of storm glass rising from the eye
		for (int t = 0; t < 70; t++) {
			double a = t * 0.35;
			int x = (int) Math.round(Math.cos(a) * 5), z = (int) Math.round(Math.sin(a) * 5);
			k.set(x, 2 + t / 3, z, glass);
		}
		heart(k, 0, cloud, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 5: a dark dome round one great candle
	static void lastCandle(Kit k) {
		k.site(13, 18);
		BlockState stone = mod("umbral_stone");
		k.ellipsoid(0, 0, 0, 12, 14, 12, stone, 1.2);
		k.box(-12, 0, -12, 12, 0, 12, mod("umbral_moss"));
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			for (int y = 1; y <= 7; y++)
				for (int w = -3; w <= 3; w++) {
					if (y > 5 && Math.abs(w) > 7 - y) continue;
					for (int s = 8; s <= 13; s++)
						k.air(d.getStepX() * s + d.getClockWise().getStepX() * w, y, d.getStepZ() * s + d.getClockWise().getStepZ() * w);
				}
		}
		k.cyl(0, 0, 3.5, 10, 15, b(Blocks.AIR));
		k.ring(0, 12, 0, 4, b(Blocks.GOLD_BLOCK));
		// outside, a ring of tall dead candles, their wicks cold
		for (int i = 0; i < 10; i++) {
			double a = i * Math.PI / 5 + 0.3;
			int x = (int) Math.round(Math.cos(a) * 16), z = (int) Math.round(Math.sin(a) * 16);
			int h = 3 + (i % 3) * 2;
			for (int y = 0; y <= h; y++) k.set(x, y, z, fr.achedon12.matriochka.mc.McBlocks.WOOL.white().defaultBlockState());
			k.set(x, h + 1, z, b(Blocks.CANDLE));
		}
		// the candle: a pillar of white wax with a single flame on top, wax pooled at its foot
		for (int y = 1; y <= 9; y++) k.set(0, y, -6, fr.achedon12.matriochka.mc.McBlocks.WOOL.white().defaultBlockState());
		k.set(0, 10, -6, b(Blocks.CANDLE).setValue(net.minecraft.world.level.block.CandleBlock.LIT, true));
		k.disc(0, 1, -6, 2.2, fr.achedon12.matriochka.mc.McBlocks.CARPET.white().defaultBlockState());
		// spent glow everywhere else: the Deep drank every other light
		for (int i = 0; i < 14; i++) k.set(k.hi(i, 0, 3, 41, 18) - 9, 1, k.hi(i, 0, 4, 42, 18) - 9, mod("spent_glow"));
		heart(k, 0, stone, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 6: a spire hanging point down from a floating rock
	static void upsideSpire(Kit k) {
		k.site(12, 34);
		BlockState inv = mod("inverted_stone"), glass = mod("mirror_glass");
		// the floating rock up high, the spire hanging from it, its tip just above the dais
		k.ellipsoid(0, 28, 0, 10, 4, 10, inv, 0);
		for (int y = 6; y <= 26; y++) {
			double rad = (y - 6) * 0.3;
			k.cyl(0, 0, rad, y, y, (y % 4 == 0) ? glass : inv);
		}
		// mirrored stairs spiralling up around it
		for (int t = 0; t < 64; t++) {
			double a = t * 0.3;
			int x = (int) Math.round(Math.cos(a) * 8), z = (int) Math.round(Math.sin(a) * 8);
			k.set(x, 1 + t / 3, z, t % 5 == 0 ? glass : mod("prism_moss"));
		}
		heart(k, 0, inv, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 7: a great bronze bell on the sea floor
	static void sunkenBell(Kit k) {
		k.site(13, 22);
		BlockState rock = mod("trench_rock"), copper = fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().weathered().defaultBlockState();
		k.disc(0, 0, 0, 12, mod("abyssal_sand"));
		// the bell: a hollow dome of weathered copper on four feet, its rim a band of gold
		for (int y = 3; y <= 16; y++) {
			double rad = y <= 5 ? 9 : 9 - (y - 5) * 0.55;
			k.tube(0, 0, rad, y, y, y == 3 || y == 4 ? b(Blocks.GOLD_BLOCK) : copper);
		}
		k.disc(0, 17, 0, 3.5, copper);
		for (int[] c : new int[][]{{7, 7}, {-7, 7}, {7, -7}, {-7, -7}}) for (int y = 0; y <= 3; y++) k.set(c[0], y, c[1], rock);
		// the clapper hanging inside
		for (int y = 9; y <= 16; y++) k.set(0, y, 0, b(Blocks.IRON_CHAIN));
		k.ellipsoid(0, 7, 0, 1.5, 1.5, 1.5, b(Blocks.PRISMARINE_BRICKS), 0);
		// coral growing on it
		for (int i = 0; i < 16; i++) k.set(k.hi(i, 0, 5, 51, 22) - 11, 1, k.hi(i, 0, 6, 52, 22) - 11, mod("pressure_coral"));
		heart(k, 0, rock, b(Blocks.GOLD_BLOCK));
		// the dais under the clapper is the heart: lift the clapper clear
		k.air(0, 1, 0, 0, 5, 0);
	}

	// ---------------------------------------------------------------- World 8: a clock tower whose hands have stopped
	static void stoppedClock(Kit k) {
		k.site(9, 34);
		BlockState stone = mod("hourstone"), sand = mod("temporal_sand_block");
		k.shell(-5, 0, -5, 5, 26, 5, stone);
		k.air(-4, 1, -4, 4, 25, 4);
		for (int y = 1; y <= 4; y++) for (int x = -1; x <= 1; x++) k.air(x, y, 5);
		// four clock faces, hands at the same stopped hour
		for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i), s = d.getClockWise();
			int fx = d.getStepX() * 5, fz = d.getStepZ() * 5;
			for (int u = -3; u <= 3; u++)
				for (int v = -3; v <= 3; v++) {
					if (u * u + v * v > 10) continue;
					k.set(fx + s.getStepX() * u, 20 + v, fz + s.getStepZ() * u, u * u + v * v > 6 ? b(Blocks.GOLD_BLOCK) : fr.achedon12.matriochka.mc.McBlocks.CONCRETE.white().defaultBlockState());
				}
			for (int t = 0; t <= 2; t++) k.set(fx + s.getStepX() * 0, 20 + t, fz + s.getStepZ() * 0, fr.achedon12.matriochka.mc.McBlocks.CONCRETE.black().defaultBlockState());
			for (int t = 0; t <= 1; t++) k.set(fx + s.getStepX() * t, 20, fz + s.getStepZ() * t, fr.achedon12.matriochka.mc.McBlocks.CONCRETE.black().defaultBlockState());
		}
		// a roof of stairs and a bell
		for (int y = 27; y <= 31; y++) k.box(-5 + (y - 27), y, -5 + (y - 27), 5 - (y - 27), y, 5 - (y - 27), k.p.roof != null ? k.p.roof : stone);
		k.set(0, 24, 0, b(Blocks.BELL));
		// time's sand drifting round its foot
		k.disc(0, 0, 0, 9, sand);
		heart(k, 0, stone, b(Blocks.GOLD_BLOCK));
	}

	// ---------------------------------------------------------------- World 9: a giant asleep under the ground, its face showing
	static void sleepingGiant(Kit k) {
		k.site(16, 18);
		BlockState rock = mod("living_rock"), flesh = mod("flesh_stone");
		// the body: a long mound, a head at the north end, a hand on the east
		k.ellipsoid(0, 0, 4, 9, 6, 14, rock, 0);
		k.ellipsoid(0, 3, -11, 6, 6, 5, rock, 0);
		k.ellipsoid(10, 1, 2, 3, 2, 5, flesh, 0);
		// the face: closed eyes of pulse vein, a mouth that breathes
		k.set(-2, 5, -16, mod("pulse_vein"));
		k.set(-3, 5, -16, mod("pulse_vein"));
		k.set(2, 5, -16, mod("pulse_vein"));
		k.set(3, 5, -16, mod("pulse_vein"));
		for (int x = -2; x <= 2; x++) k.set(x, 2, -16, fr.achedon12.matriochka.mc.McBlocks.CONCRETE.black().defaultBlockState());
		// the way into its chest, the heart inside
		k.ellipsoid(0, 3, 2, 4.5, 3, 4.5, b(Blocks.AIR), 0);
		for (int y = 1; y <= 3; y++) for (int x = -1; x <= 1; x++) for (int z = 6; z <= 18; z++) k.air(x, y, z);
		k.disc(0, 0, 2, 4.5, flesh);
		k.mark("secret", 0, 1, 2, Direction.SOUTH);
		k.mark("guard", 2, 1, 3, Direction.WEST);
		k.mark("hidden", -2, 1, 1, Direction.EAST);
		k.candles(3, 1, 2, 2);
		k.candles(-3, 1, 2, 2);
		k.decay(-16, 0, -16, 16, 12, 18, 0.05);
	}

	// ---------------------------------------------------------------- World 10: the Artisan's own desk at doll scale
	static void artisansDesk(Kit k) {
		k.site(17, 24);
		BlockState plank = mod("giant_plank"), lac = mod("lacquer_block"), paint = mod("painted_wood");
		// the desk top on four legs, high above the floor; a ladder of drawers up one leg
		k.box(-14, 14, -9, 14, 15, 9, plank);
		for (int[] c : new int[][]{{-13, -8}, {13, -8}, {-13, 8}, {13, 8}}) k.box(c[0] - 1, 0, c[1] - 1, c[0] + 1, 13, c[1] + 1, plank);
		for (int y = 1; y <= 13; y++) k.set(-11, y, -8, b(Blocks.LADDER).setValue(net.minecraft.world.level.block.LadderBlock.FACING, Direction.EAST));
		// on the desk: unfinished dolls in a row, small to large, and a pot of brushes
		int[] hs = {3, 4, 6, 8};
		for (int i = 0; i < hs.length; i++) {
			int x = -9 + i * 5;
			k.ellipsoid(x, 16 + hs[i] / 3, -4, hs[i] / 2.5, hs[i] / 3.0, hs[i] / 2.5, i % 2 == 0 ? lac : paint, 0);
			k.ellipsoid(x, 16 + hs[i] / 3 + hs[i] / 2, -4, hs[i] / 3.5, hs[i] / 3.5, hs[i] / 3.5, paint, 0);
		}
		k.cyl(10, 4, 1.6, 16, 19, b(Blocks.DECORATED_POT));
		for (int y = 20; y <= 24; y++) k.set(10, y, 4, b(Blocks.END_ROD));
		k.banner(0, 13, 9, Direction.SOUTH, DyeColor.RED);
		// the heart on the desk top, in front of the dolls
		heart(k, 15, paint, b(Blocks.GOLD_BLOCK));
	}
}
