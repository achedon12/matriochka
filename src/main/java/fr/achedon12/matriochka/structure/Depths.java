package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.RailShape;

/** Underground, enclosed and organic archetypes. */
final class Depths {
	private Depths() {}

	// ---------------------------------------------------------------- vault
	static void vault(Kit k) {
		if (k.world == 10 && k.large()) { giantChest(k); return; }
		if (!k.small()) { treasury(k); return; }
		Palette p = k.p;
		k.site(k.R, 12);
		// surface kiosk
		k.room(-3, -3, 3, 3, 0, 4, 3, 0, p.base);
		int top = k.hip(-3, -3, 3, 3, 5, 1);
		k.set(0, top + 1, 0, p.cap);
		k.lanternOn(0, top + 2, 0);
		k.doorway(0, 1, -3, Direction.NORTH, 1, 3);
		k.banner(-1, 3, -4, Direction.NORTH, p.colA);
		k.banner(1, 3, -4, Direction.NORTH, p.colB);
		k.pot(-2, 1, -2);
		k.pot(2, 1, -2);
		k.candles(-2, 1, 2, 3);
		// antechamber and the vault behind its mural wall
		k.shell(-4, -7, -3, 4, -2, 2, p.alt);
		k.floor(-3, -2, 3, 1, -7, 1);
		k.shell(-3, -7, 2, 3, -2, 6, p.alt);
		k.floor(-2, 3, 2, 5, -7, 2);
		k.spiral(0, 0, -6, 0);
		k.set(0, 0, 0, p.pillar);
		// the mural: inlay pattern with the passage hidden in it, framed by candles and banners
		for (int x = -3; x <= 3; x++)
			for (int y = -6; y <= -3; y++) k.set(x, y, 2, ((x + y) & 1) == 0 ? p.inlay : p.inlay2);
		BlockState seal = switch (k.world) {
			case 1 -> Blocks.ROOTED_DIRT.defaultBlockState();
			case 2 -> Kit.facing(Blocks.BLAST_FURNACE.defaultBlockState(), Direction.NORTH);
			case 3 -> ModContent.block("sealed_door").defaultBlockState();
			case 5 -> ModContent.block("umbral_moss").defaultBlockState();
			case 7 -> Blocks.DEAD_BRAIN_CORAL_BLOCK.defaultBlockState();
			case 8 -> ModContent.block("temporal_sand_block").defaultBlockState();
			case 9 -> ModContent.block("flesh_stone").defaultBlockState();
			default -> p.cracked;
		};
		k.set(0, -6, 2, seal);
		k.set(0, -5, 2, seal);
		k.set(0, -4, 2, p.accent);
		k.set(0, -3, 2, p.cap);
		k.candles(-2, -6, 1, 2);
		k.candles(2, -6, 1, 2);
		k.banner(-2, -4, 1, Direction.NORTH, p.colA);
		k.banner(2, -4, 1, Direction.NORTH, p.colB);
		k.hang(-3, -3, -2, 0);
		k.hang(3, -3, -2, 0);
		k.crates(-3, -6, -2);
		k.mark("hidden", 3, -6, -2, Direction.WEST);
		// inside the vault: a pedestal, gold, light
		k.set(0, -6, 5, p.cap);
		k.mark("secret", 0, -5, 5, Direction.NORTH);
		k.set(-2, -6, 5, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(2, -6, 5, Blocks.GOLD_BLOCK.defaultBlockState());
		k.set(-2, -5, 5, p.light);
		k.set(2, -5, 5, p.light);
		k.candles(-1, -6, 4, 4);
		k.candles(1, -6, 4, 4);
		k.banner(0, -3, 5, Direction.NORTH, p.colA);
		k.mark("guard", 0, -6, 3, Direction.SOUTH);
		k.decay(-4, -7, -4, 4, 8, 6, 0.2);
	}

	/** Treasury: a pillared strongroom, gold heaped in barred bays, chests set in wall niches. */
	private static void treasury(Kit k) {
		Palette p = k.p;
		int hw = 8, hl = 9;
		k.site(k.R, 14);
		k.room(-hw, -hl, hw, hl, 0, 7, 4, 0, p.base);
		k.floor(-hw + 1, -hl + 1, hw - 1, hl - 1, 0, 1);
		if (k.world == 3) {
			for (int x = -1; x <= 1; x++) for (int y = 1; y <= 3; y++) k.set(x, y, -hl, ModContent.block("sealed_door").defaultBlockState());
		} else k.doorway(0, 1, -hl, Direction.NORTH, 3, 3);
		// vault door ring
		for (int a = -3; a <= 3; a++)
			for (int b = 0; b <= 5; b++) {
				double d = Math.sqrt(a * a + (b - 2) * (b - 2));
				if (d > 2.6 && d <= 3.6) k.set(a, b + 1, -hl - 1, Blocks.IRON_BLOCK.defaultBlockState());
			}
		for (int x : new int[] {-4, 4})
			for (int z = -6; z <= 6; z += 4) k.pillar(x, 1, z, 6, true);
		// gold heaps behind bars
		for (int s : new int[] {-1, 1})
			for (int z = -6; z <= 6; z += 6) {
				int x0 = s * 6;
				for (int a = -1; a <= 1; a++)
					for (int b = -1; b <= 1; b++) {
						int h = 1 + k.hi(x0 + a, 0, z + b, 501, 3) - (Math.abs(a) + Math.abs(b)) / 2;
						for (int y = 1; y <= h; y++) k.set(x0 + a, y, z + b, k.hc(x0 + a, y, z + b, 503, 0.5) ? Blocks.GOLD_BLOCK.defaultBlockState() : Blocks.RAW_GOLD_BLOCK.defaultBlockState());
						k.set(x0 + a, h + 1, z + b, Blocks.LIGHT_WEIGHTED_PRESSURE_PLATE.defaultBlockState());
					}
				for (int b = -2; b <= 2; b++) for (int y = 1; y <= 4; y++) k.set(x0 - s * 2, y, z + b, p.bars);
			}
		for (int z = -6; z <= 6; z += 6) k.chandelier(0, 6, z, 1);
		k.runner(-1, -hl + 1, 1, hl - 2, 1);
		k.set(0, 1, hl - 2, p.cap);
		k.set(0, 2, hl - 2, p.accent);
		// chest niches in the walls
		for (int z = -6; z <= 6; z += 4) {
			k.mark("hidden", -hw, 2, z + 1, Direction.EAST);
			k.set(-hw - 1, 2, z + 1, p.base);
			k.mark("hidden", hw, 2, z + 1, Direction.WEST);
			k.set(hw + 1, 2, z + 1, p.base);
		}
		k.mark("guard", 0, 1, hl - 1, Direction.NORTH);
		k.mark("secret", 0, 3, hl - 2, Direction.NORTH);
		k.decay(-k.R, 0, -k.R, k.R, 10, k.R, 0.15);
	}

	/** The giant chest: a chest the size of a hall, its lid ajar, a hoard inside. */
	private static void giantChest(Kit k) {
		Palette p = k.p;
		int hw = 12, hd = 8, h = 11;
		k.site(k.R, 22);
		BlockState wood = Blocks.SPRUCE_PLANKS.defaultBlockState(), frame = Kit.axis(Blocks.DARK_OAK_LOG.defaultBlockState(), Direction.Axis.Y);
		BlockState gold = Blocks.GOLD_BLOCK.defaultBlockState();
		for (int x = -hw; x <= hw; x++)
			for (int z = -hd; z <= hd; z++)
				for (int y = 0; y <= h; y++) {
					boolean edgeX = Math.abs(x) == hw, edgeZ = Math.abs(z) == hd;
					boolean shellB = edgeX || edgeZ || y == 0;
					if (!shellB) { k.air(x, y, z); continue; }
					BlockState s = (edgeX && edgeZ) || y == 0 && (edgeX || edgeZ) ? frame : (Math.abs(x) == 6 ? gold : wood);
					k.set(x, y, z, s);
				}
		// the lid, raised at the front
		for (int x = -hw - 1; x <= hw + 1; x++)
			for (int z = -hd - 1; z <= hd + 1; z++) {
				int ly = z < -2 ? h + 3 : h + 2;
				boolean rim = Math.abs(x) == hw + 1 || Math.abs(z) == hd + 1;
				k.set(x, ly, z, rim ? frame : wood);
				if (z >= -2) k.set(x, h + 1, z, rim ? frame : wood);
			}
		// lock plate and keyhole
		k.box(-2, h - 4, -hd - 1, 2, h, -hd - 1, gold);
		k.set(0, h - 2, -hd - 1, fr.achedon12.matriochka.mc.McBlocks.WOOL.black().defaultBlockState());
		k.set(0, h - 3, -hd - 1, fr.achedon12.matriochka.mc.McBlocks.WOOL.black().defaultBlockState());
		// crates stacked as steps up to the gap under the lid
		for (int i = 0; i < h; i++) {
			int z = -hd - 1 - (h - i) / 2;
			k.box(-8 + i % 2, i, z, -6, i, -hd - 1, i % 3 == 0 ? Blocks.BARREL.defaultBlockState() : p.plank);
		}
		k.air(-hw + 1, h + 1, -hd, hw - 1, h + 2, -hd);
		// the hoard
		for (int x = -hw + 1; x <= hw - 1; x++)
			for (int z = -hd + 1; z <= hd - 1; z++) {
				double d = Math.sqrt(x * x / 100.0 + z * z / 36.0);
				int hh = (int) Math.round((1.0 - d) * 5) + k.hi(x, 0, z, 511, 2) - 1;
				for (int y = 1; y <= hh; y++) k.set(x, y, z, k.hc(x, y, z, 513, 0.35) ? gold : Blocks.RAW_GOLD_BLOCK.defaultBlockState());
				if (hh >= 0 && k.hc(x, 0, z, 517, 0.2)) k.set(x, Math.max(1, hh + 1), z, Blocks.LIGHT_WEIGHTED_PRESSURE_PLATE.defaultBlockState());
			}
		for (int i = 0; i < 4; i++) {
			int x = -9 + i * 6;
			k.ring(x, 1, hd - 2, 2, gold);
		}
		for (int x = -hw + 2; x <= hw - 2; x += 5) k.hang(x, h, 0, 2);
		k.mark("hidden", -hw + 1, 1, hd - 1, Direction.EAST);
		k.mark("hidden", hw - 1, 1, -hd + 1, Direction.WEST);
		k.mark("hidden", 0, 7, 0, Direction.NORTH);
		k.mark("hidden", hw - 1, 1, hd - 1, Direction.WEST);
		k.mark("guard", 0, 6, 2, Direction.NORTH);
		k.decay(-k.R, 0, -k.R, k.R, 18, k.R, 0.05);
	}

	// ---------------------------------------------------------------- crypt
	static void crypt(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean echo = k.world == 5;
		k.site(R, 14);
		int e = R - 1;
		// fence of bars on a trim kerb with posts
		for (int i = -e; i <= e; i++)
			for (int[] c : new int[][] {{i, -e}, {i, e}, {-e, i}, {e, i}}) {
				k.set(c[0], 0, c[1], p.trim);
				boolean post = Math.floorMod(i, 4) == 0;
				k.set(c[0], 1, c[1], post ? p.wall : p.bars);
				k.set(c[0], 2, c[1], post ? p.cap : p.bars);
				if (post) k.lanternOn(c[0], 3, c[1]);
			}
		for (int x = -1; x <= 1; x++) { k.air(x, 1, -e); k.air(x, 2, -e); }
		for (int s : new int[] {-2, 2}) for (int y = 1; y <= 4; y++) k.set(s, y, -e, p.pillar);
		for (int x = -2; x <= 2; x++) k.set(x, 5, -e, p.trim);
		// graves
		for (int x = -e + 2; x <= e - 2; x += 3) {
			if (Math.abs(x) <= 2) continue;
			for (int z = -e + 2; z <= 0; z += 3) {
				k.set(x, 1, z, p.wall);
				k.set(x, 2, z, k.hc(x, 2, z, 521, 0.5) ? p.cap : Kit.slabOf(p.slab, false));
				k.set(x, 0, z + 1, echo ? Blocks.SCULK.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState());
				if (k.hc(x, 1, z, 523, 0.5)) k.candles(x, 1, z + 1, 1 + k.hi(x, 1, z, 525, 3));
				else if (k.hc(x, 1, z, 527, 0.3)) k.set(x, 1, z + 1, Blocks.SKELETON_SKULL.defaultBlockState());
				if (echo && k.hc(x, 1, z, 529, 0.25)) { k.set(x + 1, 0, z, Blocks.SOUL_SOIL.defaultBlockState()); k.set(x + 1, 1, z, Blocks.SOUL_FIRE.defaultBlockState()); }
			}
		}
		for (int z = -e + 1; z <= 0; z++) for (int x = -1; x <= 1; x++) k.set(x, 0, z, x == 0 ? p.inlay : p.floor);
		// mausoleum
		k.room(-4, 1, 4, 8, 0, 5, 4, 0, p.base);
		k.gable(-4, 1, 4, 8, 6, false, p.alt);
		k.doorway(0, 1, 1, Direction.NORTH, 1, 3);
		for (int s : new int[] {-2, 2}) { k.pillar(s, 1, 0, 5, false); }
		k.box(-3, 6, -1, 3, 6, 0, p.trim);
		k.banner(-1, 4, 0, Direction.NORTH, p.colA);
		k.banner(1, 4, 0, Direction.NORTH, p.colB);
		k.candles(-3, 1, 7, 4);
		k.set(-2, 1, 7, p.cap);
		k.set(-2, 2, 7, Blocks.SKELETON_SKULL.defaultBlockState());
		// the crypt hall with burial niches, and the stair down into it
		int cy = -7;
		k.shell(-3, cy, -9, 3, -2, 9, p.alt);
		k.floor(-2, -8, 2, 8, cy, 1);
		for (int i = 0; i <= 6; i++) {
			k.air(2, -i + 1, 7 - i, 2, -i + 3, 7 - i);
			k.stair(2, -i, 7 - i, Direction.SOUTH, false);
			if (-i > cy + 1) k.set(3, -i, 7 - i, p.alt);
		}
		for (int z = -7; z <= 7; z += 3) {
			for (int s : new int[] {-1, 1}) {
				int x = s * 3;
				if (z > 0 && s > 0) continue;
				k.air(x, cy + 1, z, x, cy + 2, z);
				k.set(x + s, cy + 1, z, p.alt);
				k.set(x + s, cy + 2, z, p.alt);
				k.slab(x, cy + 1, z, p.slab, false);
				k.set(x, cy + 2, z, k.hc(x, cy, z, 531, 0.5) ? Blocks.SKELETON_SKULL.defaultBlockState() : Blocks.BONE_BLOCK.defaultBlockState());
				k.set(x, cy + 3, z, Kit.stairOf(p.stair, s > 0 ? Direction.WEST : Direction.EAST, true));
			}
			k.stair(-2, -3, z, Direction.EAST, true);
			if (z < 0) k.stair(2, -3, z, Direction.WEST, true);
			k.hang(0, -3, z, 0);
		}
		// sarcophagi down the middle
		for (int z = -5; z <= 3; z += 4) {
			k.stair(0, cy + 1, z, Direction.SOUTH, false);
			k.slab(0, cy + 1, z + 1, p.slab, true);
			k.candles(0, cy + 2, z + 1, 2);
		}
		// ossuary at the far end, the altar and guarded hoard at the near end
		for (int x = -2; x <= 2; x++) for (int y = cy + 1; y <= cy + 3; y++) if (k.hc(x, y, 8, 533, 0.6)) k.set(x, y, 8, Blocks.BONE_BLOCK.defaultBlockState());
		k.box(-1, cy + 1, -8, 1, cy + 1, -8, p.trim);
		k.set(0, cy + 2, -8, echo ? Blocks.SCULK_SHRIEKER.defaultBlockState() : p.accent);
		k.mark("guard", -1, cy + 1, -7, Direction.SOUTH);
		k.mark("spawner", 1, cy + 1, -6, Direction.SOUTH);
		k.mark("spawner", -2, cy + 1, 0, Direction.SOUTH);
		k.mark("spawner", 1, cy + 1, 5, Direction.SOUTH);
		k.mark("hidden", -3, cy + 1, -4, Direction.EAST);
		k.mark("hidden", 3, cy + 1, -1, Direction.WEST);
		k.mark("hidden", -3, cy + 1, 5, Direction.EAST);
		k.mark("hidden", 3, 1, 7, Direction.WEST);
		k.mark("reading", -3, 1, 4, Direction.EAST);
		k.decay(-R, cy, -R, R, 10, R, 0.4);
	}

	// ---------------------------------------------------------------- cell
	static void cell(Kit k) {
		if (k.small()) { cage(k); return; }
		Palette p = k.p;
		int R = k.R;
		k.site(R, 18);
		int x0 = -13, x1 = 13, z0 = -7, z1 = 7;
		k.room(x0, z0, x1, z1, 0, 5, 4, 0, p.plank);
		k.room(x0, z0, x1, z1, 5, 5, 4, 1, null);
		k.box(x0 + 1, 10, z0 + 1, x1 - 1, 10, z1 - 1, p.alt);
		Parts.crenels(k, x0, z0, x1, z0, 11);
		Parts.crenels(k, x0, z1, x1, z1, 11);
		Parts.crenels(k, x0, z0, x0, z1, 11);
		Parts.crenels(k, x1, z0, x1, z1, 11);
		// open the corridor to full height, galleries along the upper cells
		k.air(x0 + 1, 1, -1, x1 - 1, 9, 1);
		for (int x = x0 + 1; x <= x1 - 1; x++) {
			k.slab(x, 5, -1, p.slab, true);
			k.slab(x, 5, 1, p.slab, true);
		}
		for (int i = 0; i < 5; i++) k.stair(x1 - 2 - i, 5 - i, 0, Direction.EAST, false);
		k.doorway(x0, 1, 0, Direction.WEST, 1, 3);
		// rows of cells on both sides, both floors
		int npcCell = 2 + k.variant % 3;
		for (int fl = 0; fl < 2; fl++) {
			int fy = fl * 5;
			for (int j = 0; j <= 6; j++) {
				int xw = x0 + 4 * j;
				for (int s : new int[] {-1, 1}) {
					int zf = s * 2, zb = s * (z1 - 1);
					for (int z = Math.min(zf, zb); z <= Math.max(zf, zb); z++) for (int y = fy + 1; y <= fy + 4; y++) k.set(xw, y, z, p.base);
					if (j == 6) continue;
					for (int x = xw + 1; x <= xw + 3; x++) for (int y = fy + 1; y <= fy + 4; y++) k.set(x, y, zf, y == fy + 4 ? p.trim : p.bars);
					int dx = xw + 2;
					boolean open = fl == 0 && s > 0 && j == npcCell;
					BlockState door = Kit.facing(Blocks.IRON_DOOR.defaultBlockState(), s > 0 ? Direction.NORTH : Direction.SOUTH).setValue(DoorBlock.OPEN, open);
					k.set(dx, fy + 1, zf, door.setValue(DoorBlock.HALF, DoubleBlockHalf.LOWER));
					k.set(dx, fy + 2, zf, door.setValue(DoorBlock.HALF, DoubleBlockHalf.UPPER));
					// cot, bucket, chain
					k.bed(xw + 1, fy + 1, zb, s > 0 ? Direction.NORTH : Direction.SOUTH, DyeColor.GRAY);
					k.set(xw + 3, fy + 1, zb, Blocks.CAULDRON.defaultBlockState());
					k.set(xw + 3, fy + 4, zb - s, Kit.axis(p.chain, Direction.Axis.Y));
					k.set(xw + 3, fy + 3, zb - s, Kit.axis(p.chain, Direction.Axis.Y));
					if (open) k.mark("npc", xw + 2, fy + 1, zb - s, Direction.NORTH);
					else if ((j + s + fl) % 3 == 0) k.mark("hidden", xw + 3, fy + 1, zf + s, s > 0 ? Direction.NORTH : Direction.SOUTH);
					if (k.hc(xw, fy, s, 541, 0.4)) k.set(xw + 1, fy + 3, zb, Blocks.COBWEB.defaultBlockState());
				}
			}
		}
		for (int x = x0 + 3; x <= x1 - 3; x += 6) { k.hang(x, 9, 0, 2); k.hang(x, 4, -1, 0); }
		// warden's office at the east end
		k.room(x1, -5, x1 + 4, 5, 0, 5, 0, 1, p.plank);
		k.doorway(x1, 1, 3, Direction.WEST, 1, 2);
		k.table(x1 + 2, 1, 0);
		k.chair(x1 + 3, 1, 0, Direction.WEST);
		k.set(x1 + 3, 1, -3, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.WEST));
		for (int z = -3; z <= 3; z += 2) k.set(x1 + 1, 3, z, Kit.facing(Blocks.TRIPWIRE_HOOK.defaultBlockState(), Direction.EAST));
		k.banner(x1 + 3, 3, 4, Direction.NORTH, p.colA);
		k.mark("hidden", x1 + 3, 1, -4, Direction.WEST);
		k.mark("guard", x1 + 3, 1, 3, Direction.WEST);
		// exercise yard with a watchtower
		for (int x = x0; x <= x1; x++) { k.set(x, 1, 16, p.base); k.set(x, 2, 16, p.base); k.set(x, 3, 16, p.wall); }
		for (int z = 8; z <= 16; z++) { k.set(x0, 1, z, p.base); k.set(x0, 2, z, p.base); k.set(x0, 3, z, p.wall); k.set(x1, 1, z, p.base); k.set(x1, 2, z, p.base); k.set(x1, 3, z, p.wall); }
		k.doorway(0, 1, z1, Direction.SOUTH, 1, 2);
		Parts.roundTower(k, x1 - 2, 13, 2, 0, 10, true);
		k.decay(-R, 0, -R, R, 14, R, 0.25);
	}

	/** Hanging cage: a domed cage of bars hung on a chain from a floating rock. */
	private static void cage(Kit k) {
		Palette p = k.p;
		k.site(k.R, 30);
		k.ellipsoid(0, 24, 0, 5, 3, 5, p.found, 0);
		k.ellipsoid(0, 26, 0, 4, 1, 4, p.soil, 0);
		for (int y = 14; y <= 21; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		int fy = 5, rad = 4;
		k.disc(0, fy, 0, rad, p.trim);
		k.disc(0, fy, 0, rad - 1, p.floor);
		for (int y = fy + 1; y <= fy + 6; y++) k.ring(0, y, 0, rad, y == fy + 3 ? p.alt : p.bars);
		k.ring(0, fy + 7, 0, rad - 1, p.bars);
		k.ring(0, fy + 8, 0, rad - 2, p.bars);
		k.disc(0, fy + 8, 0, 1, p.trim);
		k.set(0, fy + 8, 0, p.cap);
		k.hang(0, fy + 7, 0, 1);
		for (int y = fy - 3; y < fy; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		k.set(0, fy - 4, 0, p.accent);
		// way in: a ladder column and a gap in the bars
		for (int y = 1; y <= fy; y++) { k.set(0, y, -rad - 1, p.base); k.set(0, y, -rad - 2, Kit.ladderFacing(Direction.NORTH)); }
		k.air(0, fy + 1, -rad);
		k.air(0, fy + 2, -rad);
		k.set(1, fy + 1, 1, Blocks.BONE_BLOCK.defaultBlockState());
		k.set(-1, fy + 1, 2, Blocks.SKELETON_SKULL.defaultBlockState());
		k.mark("guard", 0, fy + 1, 2, Direction.NORTH);
		k.mark("spawner", -2, fy + 1, 0, Direction.NORTH);
		k.mark("spawner", 2, fy + 1, -1, Direction.NORTH);
		k.mark("hidden", 0, 25, 0, Direction.NORTH);
		k.decay(-k.R, fy, -k.R, k.R, fy + 9, k.R, 0.2);
	}

	// ---------------------------------------------------------------- maze
	static void maze(Kit k) {
		Palette p = k.p;
		int n = (2 * (k.R - 1)) / 3;
		int w = 3 * n + 1, x0 = -w / 2, z0 = -w / 2;
		k.site(k.R, 10);
		// solid block of walls, then carve cells
		for (int x = 0; x < w; x++)
			for (int z = 0; z < w; z++) {
				k.set(x0 + x, 0, z0 + z, p.floor);
				for (int y = 1; y <= 4; y++) k.set(x0 + x, y, z0 + z, y == 4 ? p.trim : y == 1 ? p.alt : p.base);
				k.set(x0 + x, 5, z0 + z, p.base);
			}
		boolean[][] seen = new boolean[n][n];
		ArrayDeque<int[]> stack = new ArrayDeque<>();
		List<int[]> ends = new ArrayList<>();
		int mid = n / 2;
		stack.push(new int[] {mid, 0});
		seen[mid][0] = true;
		carveCell(k, x0, z0, mid, 0);
		int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
		while (!stack.isEmpty()) {
			int[] c = stack.peek();
			List<int[]> opts = new ArrayList<>();
			for (int[] d : dirs) {
				int nx = c[0] + d[0], nz = c[1] + d[1];
				if (nx >= 0 && nz >= 0 && nx < n && nz < n && !seen[nx][nz]) opts.add(new int[] {nx, nz, d[0], d[1]});
			}
			if (opts.isEmpty()) {
				stack.pop();
				continue;
			}
			int[] o = opts.get(k.r.nextInt(opts.size()));
			seen[o[0]][o[1]] = true;
			carveCell(k, x0, z0, o[0], o[1]);
			int wx = x0 + 3 * c[0] + 1 + (o[2] > 0 ? 2 : o[2] < 0 ? -1 : 0);
			int wz = z0 + 3 * c[1] + 1 + (o[3] > 0 ? 2 : o[3] < 0 ? -1 : 0);
			for (int a = 0; a < 2; a++) {
				int ax = o[2] != 0 ? wx : wx + a, az = o[3] != 0 ? wz : wz + a;
				k.air(ax, 1, az, ax, 3, az);
			}
			stack.push(new int[] {o[0], o[1]});
			int deg = 0;
			for (int[] d : dirs) {
				int nx = o[0] + d[0], nz = o[1] + d[1];
				if (nx >= 0 && nz >= 0 && nx < n && nz < n && !seen[nx][nz]) deg++;
			}
			if (deg == 0) ends.add(new int[] {o[0], o[1]});
		}
		// entrance and the central chamber
		int ex = x0 + 3 * mid + 1;
		k.air(ex, 1, z0, ex + 1, 3, z0);
		k.banner(ex - 1, 3, z0 - 1, Direction.NORTH, p.colA);
		k.banner(ex + 2, 3, z0 - 1, Direction.NORTH, p.colB);
		int cx = x0 + 3 * (mid - 1) + 1, cz = z0 + 3 * (mid - 1) + 1;
		k.air(cx, 1, cz, cx + 4, 3, cz + 4);
		k.floor(cx, cz, cx + 4, cz + 4, 0, 2);
		k.set(cx + 2, 1, cz + 2, p.cap);
		k.set(cx + 2, 2, cz + 2, p.accent);
		k.mark("guard", cx + 2, 1, cz + 3, Direction.NORTH);
		k.mark("spawner", cx, 1, cz, Direction.NORTH);
		k.mark("spawner", cx + 4, 1, cz + 4, Direction.NORTH);
		k.mark("spawner", cx + 4, 1, cz, Direction.NORTH);
		k.glowTrap(cx + 2, 5, cz + 2, true);
		for (int i = 0; i < ends.size() && i < 6; i++) {
			int[] e = ends.get(i);
			k.mark("hidden", x0 + 3 * e[0] + 1, 1, z0 + 3 * e[1] + 1, Direction.NORTH);
		}
		// lights, cobwebs, barred windows, pit traps
		for (int x = 0; x < w; x++)
			for (int z = 0; z < w; z++) {
				int lx = x0 + x, lz = z0 + z;
				boolean wall = (x % 3 == 0) || (z % 3 == 0);
				if (!wall && x % 6 == 1 && z % 6 == 1) k.glowTrap(lx, 5, lz, true);
				if (wall && k.hc(lx, 2, lz, 551, 0.04)) k.set(lx, 2, lz, p.bars);
				if (wall && k.hc(lx, 3, lz, 553, 0.03)) k.set(lx, 3, lz, p.light);
				if (!wall && k.hc(lx, 1, lz, 555, 0.04)) k.set(lx, 3, lz, Blocks.COBWEB.defaultBlockState());
				if (!wall && k.large() && k.hc(lx, 0, lz, 557, 0.015) && Math.abs(lx - ex) > 3) {
					for (int y = -3; y <= 0; y++) k.air(lx, y, lz);
					k.set(lx, -4, lz, Blocks.COBWEB.defaultBlockState());
				}
			}
		k.decay(x0, 1, z0, x0 + w, 5, z0 + w, 0.15);
	}

	private static void carveCell(Kit k, int x0, int z0, int cx, int cz) {
		int x = x0 + 3 * cx + 1, z = z0 + 3 * cz + 1;
		k.air(x, 1, z, x + 1, 3, z + 1);
		k.set(x, 0, z, k.p.floor);
		k.set(x + 1, 0, z + 1, k.p.inlay);
	}

	// ---------------------------------------------------------------- mine
	static void mine(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean deep = k.large();
		k.site(R, 16);
		// shaft
		int bottom = deep ? -13 : -11;
		for (int y = bottom; y <= 0; y++)
			for (int x = -2; x <= 2; x++)
				for (int z = -2; z <= 2; z++) {
					boolean edge = Math.abs(x) == 2 || Math.abs(z) == 2;
					if (edge) k.set(x, y, z, (y % 3 == 0) ? Kit.axis(p.log, Math.abs(x) == 2 ? Direction.Axis.Z : Direction.Axis.X) : p.plank);
					else k.air(x, y, z);
				}
		for (int y = bottom + 1; y <= 0; y++) k.set(0, y, 1, Kit.ladderFacing(Direction.NORTH));
		// headframe with pulley wheel
		for (int[] c : new int[][] {{-2, -2}, {2, -2}, {-2, 2}, {2, 2}}) for (int y = 1; y <= 9; y++) k.set(c[0], y, c[1], p.log);
		for (int y = 3; y <= 9; y += 3) {
			for (int i = -1; i <= 1; i++) { k.set(i, y, -2, Kit.axis(p.log, Direction.Axis.X)); k.set(i, y, 2, Kit.axis(p.log, Direction.Axis.X)); }
		}
		k.box(-2, 10, -2, 2, 10, 2, p.plank);
		k.air(-1, 10, -1, 1, 10, 1);
		for (int a = 0; a < 16; a++) {
			double t = a * Math.PI / 8;
			k.set((int) Math.round(Math.cos(t) * 2), 13 + (int) Math.round(Math.sin(t) * 2), 0, p.fence);
		}
		k.set(0, 13, 0, Kit.axis(p.log, Direction.Axis.Z));
		for (int y = 11; y <= 12; y++) { k.set(-2, y, 0, p.log); k.set(2, y, 0, p.log); }
		for (int y = bottom + 3; y <= 12; y++) k.set(0, y, -1, Kit.axis(p.chain, Direction.Axis.Y));
		k.set(0, bottom + 2, -1, p.lantern);
		// deck around the shaft and a tool shed
		for (int x = -4; x <= 4; x++) for (int z = -4; z <= 4; z++) if (Math.max(Math.abs(x), Math.abs(z)) > 2) k.set(x, 0, z, p.plank);
		for (int i = -4; i <= 4; i++) { k.set(i, 1, -4, (i & 1) == 0 ? p.fence : p.fill); k.set(i, 1, 4, p.fence); }
		k.air(-1, 1, -4, 1, 1, -4);
		k.crates(3, 1, 3);
		k.set(-3, 1, 3, Kit.facing(Blocks.GRINDSTONE.defaultBlockState(), Direction.EAST));
		// galleries
		BlockState ore = ModContent.block(k.world == 2 ? "blazing_rock_ore" : k.world == 5 ? "diamond_fragment_ore" : "sporite_ore").defaultBlockState();
		BlockState big = ModContent.block(k.world == 2 ? "giant_ore_block" : k.world == 5 ? "faint_glow" : "rootstone").defaultBlockState();
		int[] levels = deep ? new int[] {-5, -9, -13} : new int[] {-5, -11};
		int li = 0;
		for (int ly : levels) {
			for (int i = 0; i < 4; i++) {
				Direction d = Direction.from2DDataValue(i);
				if ((i + li) % 4 == 3) continue;
				Direction s = d.getClockWise();
				int len = R - 2;
				for (int t = 2; t <= len; t++) {
					for (int o = -1; o <= 1; o++) {
						int x = d.getStepX() * t + s.getStepX() * o, z = d.getStepZ() * t + s.getStepZ() * o;
						k.set(x, ly, z, p.found);
						for (int y = ly + 1; y <= ly + 3; y++) k.air(x, y, z);
						k.set(x, ly + 4, z, p.found);
						for (int y = ly + 1; y <= ly + 3; y++) {
							int wx = x + s.getStepX() * (o == 0 ? 0 : o), wz = z + s.getStepZ() * (o == 0 ? 0 : o);
							if (o != 0 && k.hc(wx + s.getStepX() * o, y, wz + s.getStepZ() * o, 561, 0.12))
								k.set(x + s.getStepX() * o, y, z + s.getStepZ() * o, k.hc(x, y, z, 563, 0.3) ? big : ore);
						}
					}
					int cx = d.getStepX() * t, cz = d.getStepZ() * t;
					k.set(cx, ly + 1, cz, Blocks.RAIL.defaultBlockState().setValue(BlockStateProperties.RAIL_SHAPE, d.getAxis() == Direction.Axis.X ? RailShape.EAST_WEST : RailShape.NORTH_SOUTH));
					if (t % 3 == 0) {
						for (int y = ly + 1; y <= ly + 3; y++) {
							k.set(cx + s.getStepX(), y, cz + s.getStepZ(), p.fence);
							k.set(cx - s.getStepX(), y, cz - s.getStepZ(), p.fence);
						}
						for (int o = -1; o <= 1; o++) k.set(cx + s.getStepX() * o, ly + 3, cz + s.getStepZ() * o, Kit.axis(p.log, s.getAxis()));
						k.set(cx, ly + 4, cz, p.light);
					}
				}
				// end of the gallery: a storage nook, or a collapse
				int ex = d.getStepX() * (len + 1), ez = d.getStepZ() * (len + 1);
				if ((i + li) % 2 == 0) {
					k.mark("hidden", ex - d.getStepX(), ly + 1, ez - d.getStepZ(), d.getOpposite());
					k.crates(ex - d.getStepX() + s.getStepX(), ly + 1, ez - d.getStepZ() + s.getStepZ());
				} else {
					for (int t = len - 3; t <= len; t++)
						for (int o = -1; o <= 1; o++)
							for (int y = ly + 1; y <= ly + 3; y++) {
								int x = d.getStepX() * t + s.getStepX() * o, z = d.getStepZ() * t + s.getStepZ() * o;
								if (y - ly <= (t - len + 4) + (o == 0 ? 0 : 1)) k.set(x, y, z, k.hc(x, y, z, 565, 0.5) ? Blocks.GRAVEL.defaultBlockState() : p.found);
							}
					k.mark("hidden", d.getStepX() * (len - 4), ly + 1, d.getStepZ() * (len - 4), s);
				}
			}
			li++;
		}
		k.mark("guard", 1, bottom + 1, -1, Direction.NORTH);
		k.mark("reading", -1, bottom + 1, -1, Direction.SOUTH);
		k.decay(-R, bottom, -R, R, 14, R, 0.3);
	}

	// ---------------------------------------------------------------- forge
	static void forge(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean giant = k.world == 10;
		int hw = R - 4, hl = R - 3, wh = k.large() ? 10 : 8;
		k.site(R, 32);
		k.room(-hw, -hl, hw, hl, 0, wh, 4, 3, null);
		k.gable(-hw, -hl, hw, hl, wh, true, p.alt);
		k.doorway(0, 1, -hl, Direction.NORTH, 3, 4);
		k.floor(-hw + 1, -hl + 1, hw - 1, hl - 1, 0, 3);
		// the furnace core: stepped stack with a glowing mouth, and its chimney
		int fz = hl - 5, fr = k.large() ? 4 : 3;
		for (int y = 1; y <= wh - 1; y++) {
			int r2 = Math.max(1, fr - (y - 1) / 3);
			for (int x = -r2; x <= r2; x++)
				for (int z = -r2; z <= r2; z++) k.set(x, y, fz + z, (Math.abs(x) == r2 || Math.abs(z) == r2) ? (y % 3 == 0 ? p.trim : p.alt) : p.accent);
		}
		k.air(-1, 1, fz - fr, 1, 3, fz - 1);
		k.set(0, 1, fz - 1, Blocks.LAVA.defaultBlockState());
		k.set(-1, 1, fz - fr, Kit.facing(Blocks.BLAST_FURNACE.defaultBlockState(), Direction.NORTH));
		k.set(1, 1, fz - fr, Kit.facing(Blocks.BLAST_FURNACE.defaultBlockState(), Direction.NORTH));
		k.stair(0, 3, fz - fr, Direction.SOUTH, true);
		int chimneyTop = Math.min(38, wh + 18);
		for (int y = wh; y <= chimneyTop; y++)
			for (int x = -1; x <= 1; x++)
				for (int z = fz - 1; z <= fz + 1; z++) {
					boolean in = x == 0 && z == fz;
					k.set(x, y, z, in ? p.fill : (y % 5 == 0 ? p.trim : p.alt));
				}
		k.set(0, chimneyTop, fz, Blocks.CAMPFIRE.defaultBlockState());
		k.set(0, chimneyTop - 1, fz, Blocks.HAY_BLOCK.defaultBlockState());
		// lava channel to a row of moulds, a quench pool
		for (int z = fz - fr - 1; z >= fz - fr - 6; z--) {
			k.set(0, -1, z, p.base);
			k.set(0, 0, z, Blocks.LAVA.defaultBlockState());
			k.set(0, 1, z, p.bars);
		}
		for (int x = -2; x <= 2; x += 4) k.set(x, 1, fz - fr - 6, Blocks.LAVA_CAULDRON.defaultBlockState());
		for (int x = 4; x <= 6; x++) for (int z = -3; z <= -1; z++) {
			boolean rim = x == 4 || x == 6 || z == -3 || z == -1;
			if (rim) k.stair(x, 1, z, Kit.inward(x - 5, z + 2).getOpposite(), false); else k.set(x, 0, z, Blocks.WATER.defaultBlockState());
		}
		k.set(5, 1, -2, p.fill);
		k.set(5, 0, -2, Blocks.WATER.defaultBlockState());
		// workstations along the walls
		for (int z = -hl + 3; z <= hl - 4; z += 4) {
			k.set(-hw + 2, 1, z, Blocks.ANVIL.defaultBlockState());
			k.set(-hw + 1, 1, z + 1, Blocks.SMITHING_TABLE.defaultBlockState());
			k.set(-hw + 1, 1, z - 1, Kit.facing(Blocks.GRINDSTONE.defaultBlockState(), Direction.EAST));
			k.set(hw - 1, 1, z, Blocks.COAL_BLOCK.defaultBlockState());
			if (k.hc(hw, 1, z, 571, 0.6)) k.set(hw - 1, 2, z, Blocks.COAL_BLOCK.defaultBlockState());
			k.barrel(hw - 1, 1, z + 1, Direction.UP);
			int ry = wh + Math.min(z + hl + 1, hl + 1 - z) - 1;
			k.hang(-hw + 3, ry, z, ry - wh + 2);
		}
		int hookTop = wh + Math.min(-3 + hl + 1, hl + 4) - 1;
		for (int x = -hw + 3; x <= hw - 3; x += 5) {
			for (int y = wh - 4; y <= hookTop; y++) k.set(x, y, -3, Kit.axis(p.chain, Direction.Axis.Y));
			k.set(x, wh - 5, -3, p.lantern.hasProperty(BlockStateProperties.HANGING) ? p.lantern.setValue(BlockStateProperties.HANGING, true) : p.lantern);
		}
		if (giant) {
			// a giant anvil in the middle of the hall
			BlockState iron = Blocks.IRON_BLOCK.defaultBlockState();
			k.box(-3, 1, -4, 3, 1, -1, iron);
			k.box(-1, 2, -3, 1, 3, -2, iron);
			k.box(-4, 4, -4, 4, 5, -1, iron);
			k.box(5, 5, -3, 6, 5, -2, iron);
			k.set(7, 5, -3, iron);
			for (int i = 0; i < 7; i++) k.set(-5 + i, 6 + i / 3, -6, Kit.axis(p.log, Direction.Axis.X));
			k.box(1, 6, -7, 3, 9, -5, iron);
		}
		// combat: the forge vault in the corner; story: the smith's quarters
		int vx = hw - 5, vz = -hl + 1;
		k.room(vx, vz, hw, vz + 5, 0, 4, 0, 0, p.plank);
		k.doorway(vx, 1, vz + 3, Direction.WEST, 1, 2);
		k.set(vx, 1, vz + 3, p.bars);
		k.set(vx, 2, vz + 3, p.bars);
		k.air(vx, 1, vz + 2);
		k.air(vx, 2, vz + 2);
		k.mark("guard", hw - 2, 1, vz + 4, Direction.WEST);
		k.mark("spawner", 3, 1, 3, Direction.NORTH);
		k.mark("spawner", -4, 1, -4, Direction.NORTH);
		k.mark("spawner", 3, 1, -hl + 3, Direction.NORTH);
		k.bed(-hw + 1, 1, hl - 2, Direction.EAST, p.colA);
		k.shelves(-hw + 1, hl - 4, -hw + 1, hl - 3, 1, 2);
		k.mark("reading", -hw + 1, 1, hl - 6, Direction.EAST);
		k.mark("hidden", hw - 1, 1, hl - 1, Direction.WEST);
		k.mark("hidden", -hw + 1, 1, -hl + 1, Direction.EAST);
		k.mark("hidden", hw - 2, 1, vz + 1, Direction.WEST);
		k.decay(-R, 1, -R, R, 30, R, k.role.equals("story") ? 0.45 : 0.15);
	}

	// ---------------------------------------------------------------- well
	static void well(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean light = k.world == 5;
		BlockState pool = k.world == 2 ? Blocks.LAVA.defaultBlockState() : Blocks.WATER.defaultBlockState();
		if (k.flip) {
			k.flipY = 24;
			k.site(R, k.flipY - 4);
			k.ellipsoid(0, -7, 0, R - 2, 8, R - 2, p.found, 0);
			k.ellipsoid(0, -1, 0, R - 1, 1, R - 1, p.base, 0);
		} else k.site(R, 14);
		k.roundFloor(0, 0, 0, R - 1);
		for (int i = 0; i < 4; i++) {
			double a = i * Math.PI / 2 + Math.PI / 4;
			Parts.stoneLantern(k, (int) Math.round(Math.cos(a) * (R - 3)), 1, (int) Math.round(Math.sin(a) * (R - 3)));
		}
		// well head and pavilion
		k.ring(0, 1, 0, 3, p.base);
		k.ring(0, 2, 0, 3, p.trim);
		for (int[] c : new int[][] {{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) k.pillar(c[0], 1, c[1], 5, false);
		k.box(-4, 6, -4, 4, 6, 4, p.trim);
		k.air(-3, 6, -3, 3, 6, 3);
		int top = k.hip(-4, -4, 4, 4, 7, 0);
		k.lanternOn(0, top + 1, 0);
		for (int x = -3; x <= 3; x++) k.set(x, 5, 0, Kit.axis(p.log, Direction.Axis.X));
		// shaft
		int bot = -8;
		for (int y = bot; y <= 0; y++) {
			k.ring(0, y, 0, 3, y % 4 == 0 ? p.trim : p.alt);
			k.disc(0, y, 0, 2, p.fill);
		}
		for (int y = bot + 1; y <= 4; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		for (int y = bot; y <= 2; y++) k.set(0, y, -2, Kit.ladderFacing(Direction.SOUTH));
		if (light) for (int y = bot; y <= 0; y += 2) for (int i = 0; i < 4; i++) {
			Direction d = Direction.from2DDataValue(i);
			k.set(d.getStepX() * 3, y, d.getStepZ() * 3, p.light);
		}
		// niches in the shaft wall
		k.mark("hidden", 2, -3, 0, Direction.WEST);
		k.set(3, -3, 0, p.alt);
		k.mark("hidden", -2, -6, 0, Direction.EAST);
		k.set(-3, -6, 0, p.alt);
		// the chamber at the bottom
		int cy = -13;
		for (int x = -7; x <= 7; x++)
			for (int z = -7; z <= 7; z++)
				for (int h = 0; h <= 6; h++) {
					double d = Math.sqrt(x * x + z * z + h * h * 1.5);
					if (d > 7.5) continue;
					if (d > 6.5 || h == 0) k.set(x, cy + h, z, h == 0 ? p.floor : (light && k.hc(x, h, z, 581, 0.2) ? p.light : p.alt));
					else k.air(x, cy + h, z);
				}
		k.disc(0, cy + 6, 0, 2, p.fill);
		for (int x = -3; x <= 3; x++)
			for (int z = -3; z <= 3; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > 3.5) continue;
				if (d > 2.5) k.stair(x, cy + 1, z, Kit.inward(x, z).getOpposite(), false);
				else {
					k.set(x, cy, z, light ? b(Blocks.SEA_LANTERN) : p.trim);
					k.set(x, cy + 1, z, pool);
					if (k.flip) k.set(x, cy + 2, z, Blocks.GLASS.defaultBlockState());
				}
			}
		k.set(0, cy + 1, 0, p.cap);
		k.set(0, cy + 2, 0, k.flip ? Blocks.GLASS.defaultBlockState() : p.accent);
		k.ladder(0, cy + 2, cy + 5, -2, Direction.SOUTH);
		k.set(0, cy + 2, -3, p.alt);
		for (int i = 0; i < 6; i++) {
			double a = i * Math.PI / 3;
			k.set((int) Math.round(Math.cos(a) * 5), cy + 1, (int) Math.round(Math.sin(a) * 5), p.pillar);
			k.set((int) Math.round(Math.cos(a) * 5), cy + 2, (int) Math.round(Math.sin(a) * 5), p.light);
		}
		k.mark("guard", 5, cy + 1, 0, Direction.WEST);
		k.mark("spawner", -4, cy + 1, 3, Direction.NORTH);
		k.mark("spawner", -4, cy + 1, -3, Direction.NORTH);
		k.mark("spawner", 3, cy + 1, -4, Direction.NORTH);
		k.mark("hidden", 4, cy + 1, 4, Direction.WEST);
		k.mark("hidden", -5, cy + 1, 0, Direction.EAST);
		if (k.flip) {
			boolean f = k.flip;
			int t = k.flipY - 1;
			k.flip = false;
			for (int y = 1; y <= t; y++) { k.set(0, y, -3, p.base); k.set(0, y, -2, Kit.ladderFacing(Direction.SOUTH)); }
			k.flip = f;
		}
		k.decay(-R, cy, -R, R, 12, R, k.combat() ? 0.3 : 0.15);
	}

	private static BlockState b(net.minecraft.world.level.block.Block block) {
		return block.defaultBlockState();
	}

	// ---------------------------------------------------------------- chasm
	static void chasm(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean living = k.world == 9;
		k.site(R, 12);
		// the rift: jagged walls, depth down to the bottom of the piece
		for (int x = -R; x <= R; x++) {
			int w = 3 + k.hi(x / 3, 0, 0, 601, 3) + (int) Math.round(2 * Math.cos(x * Math.PI / (2 * R)));
			if (Math.abs(x) > R - 2) w = Math.max(1, w - 3);
			for (int z = -w - 2; z <= w + 2; z++)
				for (int y = -13; y <= 0; y++) {
					int ww = w - (y < -9 ? 1 : 0) + k.hi(x, y / 2, z, 603, 2) - 1;
					if (Math.abs(z) <= ww) k.air(x, y, z);
					else if (Math.abs(z) <= ww + 1) k.set(x, y, z, living && k.hc(x, y, z, 605, 0.2) ? p.light : living ? p.cap : (k.hc(x, y, z, 607, 0.1) ? p.mossy : p.base));
				}
			k.set(x, -13, 0, p.found);
			if (living && Math.abs(x) % 3 == 0) {
				k.set(x, 0, -w - 1, Blocks.POINTED_DRIPSTONE.defaultBlockState().setValue(BlockStateProperties.VERTICAL_DIRECTION, Direction.DOWN));
				k.set(x, 1, w + 1, Blocks.POINTED_DRIPSTONE.defaultBlockState());
			}
		}
		// stone arch bridge across the middle
		int bw = 9;
		for (int z = -bw; z <= bw; z++)
			for (int x = -1; x <= 1; x++) {
				k.set(x, 0, z, x == 0 ? p.inlay : p.floor);
				k.set(x, -1, z, p.trim);
			}
		for (int z = -bw; z <= bw; z++) { k.set(-2, 1, z, p.wall); k.set(2, 1, z, p.wall); k.set(-2, 0, z, p.trim); k.set(2, 0, z, p.trim); }
		for (int x = -2; x <= 2; x++) k.arch(-bw, bw, -10, x, false, 1);
		for (int z = -bw; z <= bw; z += 4) { k.lampPost(-2, 1, z, 2); k.hang(0, -2, z, 4); }
		// ledges with scaffolding and ladders
		int[][] ledges = {{-9, -4}, {8, -8}, {-4, -10}, {11, -3}};
		for (int i = 0; i < ledges.length; i++) {
			int lx = ledges[i][0], ly = ledges[i][1];
			int side = (i & 1) == 0 ? -1 : 1;
			int w = 3 + k.hi(lx / 3, 0, 0, 601, 3) + (int) Math.round(2 * Math.cos(lx * Math.PI / (2 * R)));
			int inner = Math.max(1, w - 2);
			for (int dx = -2; dx <= 2; dx++)
				for (int dz = 0; dz <= 3; dz++) {
					int z = side * (inner + dz);
					k.set(lx + dx, ly, z, p.plank);
					if (dz == 0) k.set(lx + dx, ly + 1, z, p.fence);
				}
			for (int y = ly + 1; y <= 0; y++) k.set(lx + 2, y, side * (inner + 2), Blocks.SCAFFOLDING.defaultBlockState());
			k.lanternOn(lx - 2, ly + 1, side * (inner + 1));
			k.mark("hidden", lx, ly + 1, side * (inner + 2), side < 0 ? Direction.SOUTH : Direction.NORTH);
			k.mark("spawner", lx - 1, ly + 1, side * (inner + 2), Direction.NORTH);
			if (k.p.underwater) {
				k.room(lx - 2, side < 0 ? -9 : 5, lx + 2, side < 0 ? -5 : 9, ly, 3, 0, 1, p.plank);
			}
		}
		// grotto at the bottom with the guarded hoard
		k.ellipsoid(R - 4, -10, 0, 3, 2, 3, p.fill, 0);
		k.box(R - 7, -13, -3, R - 1, -13, 3, p.floor);
		k.set(R - 4, -12, 0, p.cap);
		k.set(R - 4, -11, 0, p.light);
		k.mark("guard", R - 3, -12, 1, Direction.WEST);
		for (int x = -R + 2; x <= R - 2; x += 2) if (k.hc(x, -12, 0, 611, 0.5)) k.set(x, -12, k.hi(x, 0, 0, 613, 3) - 1, k.p.underwater ? Blocks.KELP_PLANT.defaultBlockState() : p.plants[k.hi(x, 1, 0, 615, p.plants.length)]);
		k.decay(-R, -13, -R, R, 4, R, 0.3);
	}

	// ---------------------------------------------------------------- nest
	static void nest(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean cavern = k.world == 2;
		boolean feathers = k.world == 4;
		boolean mimic = k.world == 9;
		if (feathers) { k.siteClear(R, 16); k.island(0, 0, 0, R, 8); } else k.site(R, cavern ? 16 : 10);
		int r0 = R - 2;
		BlockState lining = switch (k.world) {
			case 1 -> b(Blocks.MOSS_BLOCK);
			case 2 -> b(Blocks.MAGMA_BLOCK);
			case 4 -> b(Blocks.HAY_BLOCK);
			case 5 -> b(Blocks.SCULK);
			case 9 -> b(Blocks.ROOTED_DIRT);
			default -> p.soil;
		};
		if (cavern) {
			for (int x = -R; x <= R; x++)
				for (int z = -R; z <= R; z++)
					for (int h = 0; h <= R; h++) {
						double d = Math.sqrt(x * x + z * z + h * h * 1.6);
						if (d > R + 0.5) continue;
						if (d > R - 1.0 + k.hi(x, h, z, 621, 2) * 0.5) k.set(x, h, z, k.hc(x, h, z, 623, 0.1) ? p.light : p.base);
						else k.air(x, h, z);
					}
			k.air(-2, 1, -R, 2, 4, -R + 3);
			for (int i = 0; i < 10; i++) {
				int x = k.hi(i, 1, 0, 625, 2 * r0) - r0, z = k.hi(i, 2, 0, 627, 2 * r0) - r0;
				int ceil = (int) Math.sqrt(Math.max(0, (R - 1.5) * (R - 1.5) - x * x - z * z) / 1.6);
				if (ceil > 2) k.set(x, ceil, z, Blocks.POINTED_DRIPSTONE.defaultBlockState().setValue(BlockStateProperties.VERTICAL_DIRECTION, Direction.DOWN));
			}
		}
		// crater rim and the lined bowl
		for (int x = -R; x <= R; x++)
			for (int z = -R; z <= R; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > r0 + 1.5) continue;
				if (d > r0 - 0.5) {
					int h = 1 + k.hi((int) (Math.atan2(z, x) * 4), 0, 0, 631, 3);
					for (int y = 0; y <= h; y++) k.set(x, y, z, feathers ? Kit.axis(p.log, Math.abs(x) > Math.abs(z) ? Direction.Axis.Z : Direction.Axis.X) : (y == h ? p.mossy : p.base));
					if (feathers && k.hc(x, h, z, 633, 0.5)) k.set(x, h + 1, z, p.fence);
				} else {
					k.set(x, -1, z, lining);
					k.air(x, 0, z);
					if (k.hc(x, 0, z, 635, feathers ? 0.25 : 0.08)) k.set(x, 0, z, feathers ? b(fr.achedon12.matriochka.mc.McBlocks.WOOL.white()) : b(Blocks.BONE_BLOCK));
				}
			}
		// eggs
		for (int i = 0; i < 5; i++) {
			double a = i * 1.26;
			int ex = (int) Math.round(Math.cos(a) * 2), ez = (int) Math.round(Math.sin(a) * 2);
			k.set(ex, 0, ez, p.accent);
			k.set(ex, 1, ez, i % 2 == 0 ? p.light : p.accent);
		}
		k.set(0, 0, 0, p.light);
		// ribs arching over the nest
		BlockState rib = k.world == 5 || k.world == 2 ? b(Blocks.BONE_BLOCK) : p.wall;
		if (!cavern) for (int i = 0; i < 3; i++) {
			double a = i * Math.PI / 3;
			for (int t = 0; t <= 20; t++) {
				double th = t * Math.PI / 20;
				int rr = (int) Math.round(Math.cos(th) * (r0 - 1));
				int y = (int) Math.round(Math.sin(th) * (r0 - 2)) + 1;
				k.set((int) Math.round(Math.cos(a) * rr), y, (int) Math.round(Math.sin(a) * rr), rib);
			}
		}
		// burrows under the rim, each ending in a den
		for (int i = 0; i < 3; i++) {
			double a = Math.PI / 6 + i * 2 * Math.PI / 3;
			int dx = (int) Math.round(Math.cos(a) * (r0 - 1)), dz = (int) Math.round(Math.sin(a) * (r0 - 1));
			for (int t = 0; t <= 4; t++) {
				int x = (int) Math.round(Math.cos(a) * (r0 - 3 + t)), z = (int) Math.round(Math.sin(a) * (r0 - 3 + t));
				k.air(x, -2, z, x, -1, z);
				k.set(x, -3, z, lining);
			}
			int ex = (int) Math.round(Math.cos(a) * (r0 + 1)), ez = (int) Math.round(Math.sin(a) * (r0 + 1));
			k.air(ex - 1, -3, ez - 1, ex + 1, -1, ez + 1);
			k.box(ex - 1, -4, ez - 1, ex + 1, -4, ez + 1, lining);
			k.mark("hidden", ex, -3, ez, Kit.inward(dx, dz));
			k.mark("spawner", (int) Math.round(Math.cos(a) * (r0 - 3)), 0, (int) Math.round(Math.sin(a) * (r0 - 3)), Direction.NORTH);
		}
		if (mimic) {
			// a ring of decoy chests: only the marked ones hold anything
			for (int i = 0; i < 10; i++) {
				double a = i * Math.PI / 5;
				int x = (int) Math.round(Math.cos(a) * (r0 - 2)), z = (int) Math.round(Math.sin(a) * (r0 - 2));
				if (i % 3 == 0) k.mark("hidden", x, 0, z, Kit.inward(x, z));
				else k.set(x, 0, z, Kit.facing(i % 2 == 0 ? b(Blocks.TRAPPED_CHEST) : b(Blocks.BARREL), Kit.inward(x, z)));
			}
		}
		if (k.world == 5) for (int i = 0; i < 12; i++) {
			int x = k.hi(i, 3, 0, 641, 2 * r0) - r0, z = k.hi(i, 4, 0, 643, 2 * r0) - r0;
			k.set(x, 1 + k.hi(i, 5, 0, 645, 3), z, b(Blocks.COBWEB));
		}
		k.mark("guard", 1, 0, -1, Direction.SOUTH);
		k.decay(-R, -4, -R, R, R, R, 0.2);
	}

	// ---------------------------------------------------------------- hive
	static void hive(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 18);
		BlockState comb = b(Blocks.HONEYCOMB_BLOCK);
		// lobes: a great central dome and three smaller ones
		int[][] lobes = {{0, 0, 8, 11}, {-6, 5, 4, 6}, {6, 4, 4, 7}, {0, -7, 3, 5}};
		for (int[] l : lobes)
			for (int x = -l[2] - 1; x <= l[2] + 1; x++)
				for (int z = -l[2] - 1; z <= l[2] + 1; z++)
					for (int h = 0; h <= l[3]; h++) {
						double d = Math.sqrt((x * x + z * z) / (double) (l[2] * l[2]) + (h * h) / (double) (l[3] * l[3]));
						if (d > 1.0) continue;
						int wx = l[0] + x, wz = l[1] + z;
						if (d > 0.82) {
							BlockState s = k.hc(wx, h, wz, 651, 0.12) ? p.light : k.hc(wx, h, wz, 653, 0.3) ? p.inlay : k.hc(wx, h, wz, 655, 0.3) ? comb : p.base;
							k.set(wx, h, wz, s);
						} else k.air(wx, h, wz);
					}
		k.roundFloor(0, 0, 0, 7);
		// entrances
		k.air(-1, 1, -10, 1, 3, -7);
		k.air(8, 1, -1, 10, 3, 1);
		// comb terraces inside the great dome
		for (int y = 4; y <= 8; y += 4) {
			double rr = 8 * Math.sqrt(1 - (y * y) / 121.0) - 1;
			for (int x = -8; x <= 8; x++)
				for (int z = -8; z <= 8; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > rr || d < rr - 2) continue;
					k.set(x, y, z, ((x + 2 * z) % 3 == 0) ? comb : p.inlay);
				}
		}
		for (int y = 1; y <= 4; y++) { k.set(6, y, 0, p.base); k.set(5, y, 0, Kit.ladderFacing(Direction.WEST)); }
		// spore blossoms and drips hanging inside
		for (int i = 0; i < 8; i++) {
			int x = k.hi(i, 0, 0, 657, 11) - 5, z = k.hi(i, 1, 0, 659, 11) - 5;
			int ceil = (int) (11 * Math.sqrt(Math.max(0, 1 - (x * x + z * z) / 64.0))) - 1;
			if (ceil > 2) k.set(x, ceil, z, k.world == 1 ? b(Blocks.SPORE_BLOSSOM) : p.light);
		}
		// queen chamber
		k.ellipsoid(0, 2, 3, 4, 3, 4, comb, 1);
		k.air(-1, 1, -1, 1, 2, 0);
		k.box(-1, 0, 1, 1, 0, 3, p.inlay2);
		k.set(0, 1, 3, p.accent);
		k.set(0, 2, 3, p.light);
		k.mark("guard", 0, 1, 2, Direction.NORTH);
		k.mark("spawner", -6, 1, 5, Direction.NORTH);
		k.mark("spawner", 6, 1, 4, Direction.NORTH);
		k.mark("spawner", -4, 5, 0, Direction.NORTH);
		k.mark("hidden", 0, 1, -7, Direction.SOUTH);
		k.mark("hidden", 6, 5, 3, Direction.WEST);
		k.decay(-R, 0, -R, R, 12, R, 0.35);
	}

	// ---------------------------------------------------------------- cocoon
	static void cocoon(Kit k) {
		switch (k.id) {
			case "unstable_core" -> core(k);
			case "air_grotto" -> grotto(k);
			case "collapsed_doll" -> collapsedDoll(k);
			default -> silk(k);
		}
	}

	/** Giant cocoon hung from an arch of logs, chambers of silk inside, egg sacs around. */
	private static void silk(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 20);
		for (int t = 0; t <= 30; t++) {
			double th = t * Math.PI / 30;
			int x = (int) Math.round(Math.cos(th) * (R - 2)), y = (int) Math.round(Math.sin(th) * 17);
			k.set(x, y, 0, p.log);
			k.set(x, y, 1, p.log);
		}
		BlockState wool = b(fr.achedon12.matriochka.mc.McBlocks.WOOL.white());
		for (int x = -5; x <= 5; x++)
			for (int y = -8; y <= 8; y++)
				for (int z = -5; z <= 5; z++) {
					double d = Math.sqrt(x * x / 20.0 + y * y / 64.0 + z * z / 20.0);
					if (d > 1.0) continue;
					int wy = 9 + y;
					if (d > 0.78) k.set(x, wy, z, k.hc(x, wy, z, 661, 0.2) ? b(Blocks.COBWEB) : k.hc(x, wy, z, 663, 0.25) ? p.mossy : wool);
					else k.air(x, wy, z);
				}
		for (int y = 15; y <= 16; y++) k.set(0, y, 0, wool);
		k.disc(0, 4, 0, 3, wool);
		k.disc(0, 9, 0, 3, wool);
		k.air(0, 9, 0);
		k.air(0, 4, 0);
		for (int y = 1; y <= 12; y++) k.set(0, y, -1, Kit.ladderFacing(Direction.SOUTH));
		k.set(0, 0, -1, p.found);
		k.air(-1, 1, -3, 1, 3, -2);
		for (int y = 1; y <= 3; y++) k.set(0, y, -2, b(Blocks.COBWEB));
		k.air(0, 1, -2, 0, 2, -2);
		k.set(1, 10, 2, p.light);
		k.set(-2, 5, 1, p.light);
		// silk threads to the ground
		for (int i = 0; i < 6; i++) {
			double a = i * Math.PI / 3;
			for (int t = 0; t < 6; t++) {
				int x = (int) Math.round(Math.cos(a) * (4 + t)), z = (int) Math.round(Math.sin(a) * (4 + t));
				k.set(x, 6 - t, z, b(Blocks.COBWEB));
			}
		}
		// egg sacs
		for (int i = 0; i < 4; i++) {
			double a = Math.PI / 4 + i * Math.PI / 2;
			int x = (int) Math.round(Math.cos(a) * 8), z = (int) Math.round(Math.sin(a) * 8);
			k.ellipsoid(x, 1, z, 1.6, 1.4, 1.6, wool, 0);
			k.mark("hidden", x, 1, z, Kit.inward(x, z));
		}
		k.mark("hidden", 2, 10, 0, Direction.WEST);
		k.mark("hidden", -2, 5, -1, Direction.EAST);
		k.mark("guard", 1, 5, 1, Direction.NORTH);
		k.decay(-R, 0, -R, R, 18, R, 0.35);
	}

	/** Unstable core: a floating crystal sphere inside gyroscope rings, reached by a stair and a bridge. */
	private static void core(Kit k) {
		Palette p = k.p;
		int R = k.R, cy = 13;
		k.site(R, 30);
		k.roundFloor(0, 0, 0, R - 2);
		for (int i = 0; i < 4; i++) {
			double a = i * Math.PI / 2 + Math.PI / 4;
			int x = (int) Math.round(Math.cos(a) * 11), z = (int) Math.round(Math.sin(a) * 11);
			for (int y = 1; y <= 9; y++) k.set(x, y, z, y == 9 ? p.cap : p.pillar);
			k.set(x, 10, z, p.accent);
			k.set(x, 11, z, Blocks.END_ROD.defaultBlockState());
		}
		// the sphere
		for (int x = -6; x <= 6; x++)
			for (int y = -6; y <= 6; y++)
				for (int z = -6; z <= 6; z++) {
					double d = Math.sqrt(x * x + y * y + z * z);
					if (d > 6.3) continue;
					if (d > 5.3) k.set(x, cy + y, z, k.hc(x, y, z, 671, 0.4) ? p.glass : k.hc(x, y, z, 673, 0.5) ? b(Blocks.AMETHYST_BLOCK) : p.alt);
					else k.air(x, cy + y, z);
				}
		k.disc(0, cy - 4, 0, 3, p.trim);
		k.box(-1, cy - 3, -1, 1, cy - 3, 1, p.cap);
		k.set(0, cy, 0, p.light);
		for (Direction d : Direction.Plane.HORIZONTAL) k.set(d.getStepX(), cy, d.getStepZ(), b(Blocks.AMETHYST_CLUSTER).setValue(BlockStateProperties.FACING, d));
		// gyroscope rings
		for (int a = 0; a < 64; a++) {
			double t = a * Math.PI / 32;
			int u = (int) Math.round(Math.cos(t) * 9), v = (int) Math.round(Math.sin(t) * 9);
			k.set(u, cy + v, 0, p.alt);
			int u2 = (int) Math.round(Math.cos(t) * 8), v2 = (int) Math.round(Math.sin(t) * 8);
			k.set(0, cy + v2, u2, p.trim);
			int u3 = (int) Math.round(Math.cos(t) * 10), v3 = (int) Math.round(Math.sin(t) * 10);
			k.set(u3, cy + (int) Math.round(v3 * 0.35), (int) Math.round(v3 * 0.9), p.cap);
		}
		// stair column and bridge into the sphere
		int sx = -13;
		k.spiral(sx, 0, 1, cy - 4);
		for (int y = 1; y <= cy - 4; y++) {
			k.ring(sx, y, 0, 2, (y % 4 == 0) ? p.trim : p.bars);
		}
		for (int x = sx; x <= -5; x++) { k.set(x, cy - 4, 0, p.floor); k.set(x, cy - 3, 1, p.fence); k.set(x, cy - 3, -1, p.fence); }
		k.air(-6, cy - 3, 0, -5, cy - 2, 0);
		k.mark("guard", 2, cy - 3, 0, Direction.WEST);
		k.mark("spawner", -2, cy - 3, 2, Direction.NORTH);
		k.mark("spawner", 0, cy - 3, -3, Direction.NORTH);
		k.mark("spawner", 3, cy - 3, 2, Direction.NORTH);
		k.mark("hidden", 11, 1, 11, Direction.NORTH);
		k.decay(-R, 0, -R, R, 24, R, 0.1);
	}

	/** Air grotto: a dry dome on the sea floor, entered from below through a flooded tunnel. */
	private static void grotto(Kit k) {
		Palette p = k.p;
		int R = k.R, rad = 8;
		k.site(R, 14);
		for (int x = -rad - 1; x <= rad + 1; x++)
			for (int z = -rad - 1; z <= rad + 1; z++)
				for (int h = 0; h <= rad; h++) {
					double d = Math.sqrt(x * x + z * z + h * h);
					if (d > rad + 0.5) continue;
					if (d > rad - 0.6) k.set(x, h, z, h == 0 ? p.trim : k.hc(x, h, z, 681, 0.45) ? b(Blocks.GLASS) : k.hc(x, h, z, 683, 0.4) ? p.alt : p.base);
					else if (h == 0) k.set(x, h, z, k.hc(x, 0, z, 685, 0.3) ? p.inlay : p.soil);
					else k.set(x, h, z, b(Blocks.AIR));
				}
		// flooded entrance tunnel from outside to a pool in the floor
		for (int x = 3; x <= R; x++) for (int z = -1; z <= 1; z++) { k.set(x, -2, z, p.found); k.set(x, -1, z, p.fill); k.set(x, 0, z, x < rad ? p.base : p.fill); }
		k.set(3, 0, 0, p.fill);
		k.set(3, 0, -1, p.fill);
		k.box(4, -1, -1, 4, -1, 1, p.fill);
		// furniture of a refuge
		k.bed(-4, 1, -2, Direction.NORTH, p.colA);
		k.bed(-2, 1, -2, Direction.NORTH, p.colB);
		k.table(-3, 1, 3);
		k.chair(-4, 1, 3, Direction.EAST);
		k.chair(-2, 1, 3, Direction.WEST);
		k.set(0, 1, 5, p.light);
		k.set(-5, 1, 1, p.light);
		k.hang(0, rad - 1, 0, 2);
		for (int x = -rad - 3; x <= rad + 3; x++)
			for (int z = -rad - 3; z <= rad + 3; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d < rad + 1.5 || d > R) continue;
				if (k.hc(x, 1, z, 687, 0.25)) for (int y = 1; y <= 1 + k.hi(x, 1, z, 689, 6); y++) k.set(x, y, z, b(Blocks.KELP_PLANT));
				else if (k.hc(x, 1, z, 691, 0.1)) k.plant(x, 1, z);
			}
		k.mark("hidden", 5, 1, 2, Direction.WEST);
		k.mark("hidden", -6, 1, -1, Direction.EAST);
		k.mark("hidden", 0, 1, -6, Direction.SOUTH);
		k.mark("hidden", 2, 1, 5, Direction.NORTH);
		k.mark("guard", -1, 1, 0, Direction.NORTH);
		k.decay(-R, 0, -R, R, rad + 1, R, 0.1);
	}

	/** Collapsed doll: a giant nesting doll lying split open, a smaller doll in its belly. */
	private static void collapsedDoll(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 18);
		DyeColor[] bands = {DyeColor.RED, DyeColor.YELLOW, DyeColor.GREEN, DyeColor.BLUE};
		for (int x = -15; x <= 15; x++)
			for (int y = -7; y <= 7; y++)
				for (int z = -7; z <= 7; z++) {
					double d = Math.sqrt(x * x / 225.0 + y * y / 49.0 + z * z / 49.0);
					if (d > 1.0) continue;
					int wy = 7 + y;
					if (Math.abs(x) <= 1) continue;
					if (d > 0.86) {
						BlockState s = p.trim;
						int bnd = Math.floorMod(x + 15, 8);
						if (bnd == 3 || bnd == 4) s = b(fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(bands[Math.floorMod((x + 15) / 8, 4)]));
						if (x > 11 && z < -2) s = b(fr.achedon12.matriochka.mc.McBlocks.WOOL.white());
						k.set(x, wy, z, s);
					} else k.air(x, wy, z);
				}
		// face at the head end
		k.set(13, 9, -5, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.black()));
		k.set(13, 6, -5, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.black()));
		k.set(12, 5, -6, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.pink()));
		k.set(12, 10, -6, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.pink()));
		k.set(14, 7, -4, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.red()));
		// the halves drift apart: a crack opens, the inner doll shows
		k.air(-2, 1, -7, 2, 13, 7);
		k.floor(-6, -3, 6, 3, 0, 1);
		Halls.doll(k, 0, 0, 3, 5);
		k.air(-1, 1, 0, 1, 3, 0);
		for (int x = -12; x <= 12; x += 6) if (Math.abs(x) > 2) k.hang(x, 12, 0, 3);
		k.mark("guard", -8, 1, 0, Direction.EAST);
		k.mark("spawner", 8, 1, 2, Direction.NORTH);
		k.mark("spawner", 8, 1, -2, Direction.NORTH);
		k.mark("spawner", -10, 1, 3, Direction.NORTH);
		k.mark("hidden", 0, 1, 1, Direction.NORTH);
		k.decay(-R, 0, -R, R, 16, R, 0.12);
	}

	// ---------------------------------------------------------------- wreck
	static void wreck(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean air = k.world == 4;
		k.shear = 0.08;
		if (air) { k.siteClear(R, 32); k.island(0, -1, 0, R - 3, 7); } else { k.sink = 1; k.site(R, 20); }
		BlockState plank = p.plank, keel = Kit.axis(p.log, Direction.Axis.X);
		int L = R - 1, deck = 5;
		for (int x = -L; x <= L; x++) {
			double t = (double) x / L;
			double half = 4.2 * Math.sqrt(Math.max(0, 1 - (t > 0 ? t * t * t * t : t * t * t * t * 0.2)));
			if (t < -0.9) half = Math.min(half, 3);
			int w = (int) Math.round(half);
			if (w < 1) { k.set(x, deck, 0, keel); continue; }
			for (int y = 0; y <= deck; y++) {
				int ww = Math.max(1, w - (y == 0 ? 2 : y == 1 ? 1 : 0));
				for (int z = -ww; z <= ww; z++) {
					boolean hull = Math.abs(z) == ww || y == 0;
					if (y == deck) k.set(x, y, z, Math.abs(z) == ww ? p.log : plank);
					else if (hull) k.set(x, y, z, y == 0 ? keel : (y == 2 ? p.log : plank));
					else k.air(x, y, z);
				}
				if (y == deck) { k.set(x, y + 1, -ww, p.fence); k.set(x, y + 1, ww, p.fence); }
			}
		}
		// hole torn in the hull
		for (int x = 2; x <= 5; x++) for (int y = 1; y <= 3; y++) if (k.hc(x, y, 4, 701, 0.75)) k.air(x, y, 4);
		k.set(L, deck + 1, 0, p.accent);
		k.set(L + 1, deck, 0, keel);
		// sterncastle and the captain's cabin
		int sx0 = -L + 1, sx1 = -L + 6;
		for (int x = sx0; x <= sx1; x++)
			for (int z = -3; z <= 3; z++) {
				boolean edge = x == sx0 || x == sx1 || Math.abs(z) == 3;
				for (int y = deck + 1; y <= deck + 3; y++) {
					if (edge) k.set(x, y, z, (y == deck + 2 && !(x == sx0 || x == sx1) && Math.abs(z) == 3 && (x & 1) == 0) ? p.pane : (x == sx0 || x == sx1) && Math.abs(z) == 3 ? p.log : plank);
					else k.air(x, y, z);
				}
				k.set(x, deck + 4, z, plank);
				if (edge) k.set(x, deck + 5, z, p.fence);
			}
		k.air(sx1, deck + 1, 0, sx1, deck + 2, 0);
		k.door(sx1, deck + 1, 0, Direction.EAST);
		k.bed(sx0 + 1, deck + 1, -2, Direction.EAST, p.colA);
		k.table(sx0 + 3, deck + 1, 1);
		k.chair(sx0 + 3, deck + 1, 2, Direction.NORTH);
		k.set(sx0 + 1, deck + 1, 2, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.EAST));
		k.hang(sx0 + 3, deck + 3, 0, 0);
		k.mark("hidden", sx0 + 1, deck + 1, 0, Direction.EAST);
		k.mark("guard", sx0 + 4, deck + 1, -2, Direction.NORTH);
		// hold
		k.crates(-2, 1, -2);
		k.crates(3, 1, 1);
		k.mark("hidden", 0, 1, 2, Direction.NORTH);
		k.mark("hidden", 6, 1, -1, Direction.WEST);
		k.mark("spawner", -4, 1, 0, Direction.NORTH);
		k.mark("spawner", 1, 1, -2, Direction.NORTH);
		k.air(-1, deck, -1, 0, deck, 0);
		k.ladder(-1, 1, deck, 1, Direction.NORTH);
		// masts, yards and torn sails
		for (int mx : new int[] {-2, 5}) {
			int mh = mx < 0 ? 17 : 15;
			for (int y = 1; y <= mh; y++) k.set(mx, y, 0, p.log);
			for (int yy : new int[] {mh - 6, mh - 2}) {
				for (int z = -4; z <= 4; z++) k.set(mx, yy, z, Kit.axis(p.log, Direction.Axis.Z));
			}
			for (int y = mh - 5; y <= mh - 3; y++)
				for (int z = -3; z <= 3; z++) if (!k.hc(mx, y, z, 703, 0.2)) k.set(mx + 1, y, z, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.pick((z & 1) == 0 ? p.colA : DyeColor.WHITE)));
			k.lanternOn(mx, mh + 1, 0);
		}
		if (air) {
			// the airship's balloon, its ropes slack
			k.ellipsoid(1, 26, 0, R - 4, 4, 5, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.white()), 0);
			for (int x = -R + 5; x <= R - 5; x += 3) k.set(x, 23, 0, b(fr.achedon12.matriochka.mc.McBlocks.WOOL.pick(p.colB)));
			for (int[] c : new int[][] {{-8, -3}, {8, -3}, {-8, 3}, {8, 3}}) for (int y = deck + 2; y <= 22; y++) k.set(c[0], y, c[1], p.fence);
			for (int z = -2; z <= 2; z++) k.set(-L - 1, deck + 2, z, p.fence);
		} else {
			for (int x = -L; x <= L; x++) for (int z = -5; z <= 5; z++) if (k.hc(x, 0, z, 705, 0.15) && k.emptyAt(x, 1, z)) k.plant(x, 1, z);
		}
		k.decay(-R, 0, -R, R, 22, R, air ? 0.3 : 0.5);
	}

	// ---------------------------------------------------------------- diving bell
	static void bell(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 34);
		BlockState cu = b(fr.achedon12.matriochka.mc.McBlocks.COPPER_BLOCK.waxed().weathered()), cut = b(fr.achedon12.matriochka.mc.McBlocks.CUT_COPPER.waxed().oxidized());
		int[] radii = {4, 4, 4, 4, 3, 3, 2, 1};
		for (int[] c : new int[][] {{-3, -3}, {3, -3}, {-3, 3}, {3, 3}}) k.set(c[0], 0, c[1], p.pillar);
		for (int i = 0; i < radii.length; i++) {
			int y = 1 + i, r2 = radii[i];
			for (int x = -r2 - 1; x <= r2 + 1; x++)
				for (int z = -r2 - 1; z <= r2 + 1; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > r2 + 0.5) continue;
					boolean wall = d > r2 - 0.5 || i == radii.length - 1;
					if (wall) k.set(x, y, z, (i == 2 && (x == 0 || z == 0)) ? b(Blocks.GLASS) : i % 3 == 0 ? cut : cu);
					else k.set(x, y, z, b(Blocks.AIR));
				}
		}
		// floor with a hatch of open water
		k.disc(0, 1, 0, 3, p.plank);
		k.set(0, 1, 0, Blocks.WATER.defaultBlockState());
		k.set(1, 1, 0, Blocks.WATER.defaultBlockState());
		for (int x = 0; x <= 1; x++) k.air(x, 0, 0);
		k.chair(-2, 2, -1, Direction.EAST);
		k.chair(-2, 2, 1, Direction.EAST);
		k.set(2, 2, 2, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.WEST));
		k.set(0, 6, 0, p.light);
		k.mark("hidden", 2, 2, -2, Direction.WEST);
		k.mark("hidden", -1, 2, 2, Direction.NORTH);
		// chain to a buoy far above, crates and an anchor on the sea floor
		for (int y = 9; y <= 36; y++) k.set(0, y, 0, Kit.axis(p.chain, Direction.Axis.Y));
		k.set(0, 37, 0, p.light);
		k.slab(0, 38, 0, p.slab, false);
		k.crates(-5, 1, 3);
		k.crates(4, 1, -5);
		k.mark("hidden", 5, 1, 4, Direction.WEST);
		k.mark("hidden", -5, 1, -4, Direction.EAST);
		BlockState iron = b(Blocks.IRON_BLOCK);
		k.set(5, 1, 0, iron);
		k.set(5, 2, 0, iron);
		k.set(4, 1, 0, iron);
		k.set(6, 1, 0, iron);
		for (int x = 2; x <= 4; x++) k.set(x, 3, 0, Kit.axis(p.chain, Direction.Axis.X));
		k.mark("guard", -1, 2, -2, Direction.SOUTH);
		k.decay(-R, 0, -R, R, 10, R, 0.25);
	}
}
