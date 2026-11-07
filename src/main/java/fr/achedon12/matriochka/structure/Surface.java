package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The Surface's own places, before the first boss: they tell, without a word of the Scroll, that a doll-maker lived
 * here and that something waits in a ring of pillars. Built in untransformed coordinates like every archetype.
 * <ul>
 * <li>artisan_cabin: the Artisan's ruined cabin, a bench of half-carved dolls, notes and a reading corner;</li>
 * <li>peddler_stall: the Doll Peddler under his striped awning, barrels and crates of painted dolls;</li>
 * <li>fallen_doll: a giant matryoshka split open and half sunk in the ground, chests inside its halves.</li>
 * </ul>
 */
final class Surface {
	private Surface() {}

	private static BlockState lacquer() {
		return ModContent.block("lacquer_block").defaultBlockState();
	}

	private static BlockState painted() {
		return ModContent.block("painted_wood").defaultBlockState();
	}

	/** The Artisan's workshop: a timber cabin with a fallen roof, the bench, a doll carved halfway on each stool. */
	static void workshop(Kit k) {
		BlockState log = Blocks.SPRUCE_LOG.defaultBlockState(), plank = Blocks.SPRUCE_PLANKS.defaultBlockState();
		k.site(7, 9);
		// floor and walls: 9 x 7, logs at the corners
		for (int x = -4; x <= 4; x++)
			for (int z = -3; z <= 3; z++) k.set(x, 0, z, (x + z & 1) == 0 ? plank : Blocks.STRIPPED_SPRUCE_LOG.defaultBlockState());
		for (int y = 1; y <= 4; y++)
			for (int x = -4; x <= 4; x++)
				for (int z = -3; z <= 3; z++) {
					boolean edge = Math.abs(x) == 4 || Math.abs(z) == 3;
					if (!edge) continue;
					boolean corner = Math.abs(x) == 4 && Math.abs(z) == 3;
					k.set(x, y, z, corner ? log : y == 2 && (x == -2 || x == 2) ? Blocks.GLASS_PANE.defaultBlockState() : plank);
				}
		// the door gap and its step
		k.air(0, 1, 3);
		k.air(0, 2, 3);
		k.stair(0, 0, 4, Direction.NORTH, false);
		// half of the roof still stands; the other half lies in the room
		for (int x = -5; x <= 5; x++)
			for (int s = 0; s <= 3; s++) {
				if (x > 1 && s < 3) continue;
				k.stair(x, 5 + s, -4 + s, Direction.SOUTH, false);
				k.stair(x, 5 + s, 4 - s, Direction.NORTH, false);
			}
		for (int x = 2; x <= 4; x++) k.set(x, 1, -1 + (x & 1), Blocks.SPRUCE_SLAB.defaultBlockState());
		// the carving bench along the back wall, dolls in the making on it
		for (int x = -3; x <= 1; x++) k.set(x, 1, -2, Blocks.SPRUCE_PLANKS.defaultBlockState());
		k.set(-3, 2, -2, painted());
		k.set(-2, 2, -2, lacquer());
		k.set(-1, 2, -2, Blocks.CARVED_PUMPKIN.defaultBlockState().rotate(net.minecraft.world.level.block.Rotation.CLOCKWISE_180));
		k.set(0, 2, -2, Blocks.STONECUTTER.defaultBlockState());
		k.set(1, 2, -2, Blocks.CANDLE.defaultBlockState().setValue(net.minecraft.world.level.block.CandleBlock.LIT, false));
		// unfinished dolls standing about: a lacquered body under a painted head
		int[][] dolls = {{-3, 1}, {3, 2}};
		for (int[] d : dolls) {
			k.set(d[0], 1, d[1], lacquer());
			k.set(d[0], 2, d[1], painted());
		}
		k.set(-3, 1, 2, Blocks.BARREL.defaultBlockState());
		k.set(3, 1, -2, Blocks.CRAFTING_TABLE.defaultBlockState());
		k.hang(-1, 4, 0, 1);
		// the Artisan's notes: a reading corner against the west wall, a chest of his things under the bench
		k.mark("reading", -3, 1, 0, Direction.EAST);
		k.mark("hidden", 1, 1, -1, Direction.SOUTH);
		k.mark("hidden", 3, 1, 1, Direction.WEST);
		k.decay(-4, 1, -3, 4, 8, 3, 0.12);
	}

	/** The Doll Peddler's stall: a striped awning on four posts, barrels and crates, painted dolls on the counter. */
	static void stall(Kit k) {
		k.site(5, 6);
		BlockState post = Blocks.DARK_OAK_FENCE.defaultBlockState();
		for (int x = -3; x <= 3; x++)
			for (int z = -2; z <= 2; z++) k.set(x, 0, z, Blocks.COARSE_DIRT.defaultBlockState());
		for (int[] c : new int[][]{{-3, -2}, {3, -2}, {-3, 2}, {3, 2}})
			for (int y = 1; y <= 3; y++) k.set(c[0], y, c[1], post);
		// the awning, red and gold stripes
		for (int x = -3; x <= 3; x++)
			for (int z = -2; z <= 2; z++) k.set(x, 4, z, ((x + 3) & 1) == 0 ? fr.achedon12.matriochka.mc.McBlocks.WOOL.red().defaultBlockState() : fr.achedon12.matriochka.mc.McBlocks.WOOL.yellow().defaultBlockState());
		// the counter with dolls in a row, small to large
		for (int x = -2; x <= 2; x++) k.set(x, 1, -1, Blocks.SPRUCE_PLANKS.defaultBlockState());
		k.set(-2, 2, -1, Blocks.CANDLE.defaultBlockState());
		k.set(-1, 2, -1, painted());
		k.set(0, 2, -1, lacquer());
		k.set(1, 2, -1, painted());
		k.set(2, 2, -1, Blocks.LANTERN.defaultBlockState());
		k.set(-3, 1, 0, Blocks.BARREL.defaultBlockState());
		k.set(3, 1, 0, Blocks.BARREL.defaultBlockState());
		k.set(3, 1, 1, Blocks.CHEST.defaultBlockState());
		k.banner(0, 3, -2, Direction.SOUTH, DyeColor.RED);
		// the Peddler himself behind the counter, a chest of his stock beside him
		k.mark("npc", 0, 1, -2, Direction.SOUTH);
		k.mark("hidden", -2, 1, -2, Direction.SOUTH);
	}

	/** A giant matryoshka split open at the waist, its top half fallen beside it, chests inside both halves. */
	static void fallenDoll(Kit k) {
		k.site(9, 12);
		BlockState lac = lacquer(), paint = painted(), gold = Blocks.GOLD_BLOCK.defaultBlockState();
		// the lower half, standing and sunk two blocks: a hollow lacquered bowl, gold band at the rim
		for (int y = -2; y <= 4; y++) {
			double rad = 5.2 - Math.max(0, -y) * 0.4;
			for (int x = -6; x <= 6; x++)
				for (int z = -6; z <= 6; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > rad + 0.5) continue;
					boolean shell = d > rad - 1.0 || y == -2;
					if (shell) k.set(x, y, z, y == 4 ? gold : (Math.abs(x) + y) % 5 == 0 ? paint : lac);
					else if (y > -2) k.air(x, y, z);
				}
		}
		// a crack down its side
		for (int y = 0; y <= 4; y++) k.air(5, y, (y & 1));
		// the upper half lying on its side to the east, its painted face looking at the sky
		for (int x = 8; x <= 14; x++)
			for (int y = 0; y <= 7; y++)
				for (int z = -4; z <= 4; z++) {
					double d = Math.sqrt(Math.pow(y - 3.5, 2) + z * z);
					double rad = 4.2 - Math.max(0, x - 11) * 0.6;
					if (d > rad + 0.5) continue;
					boolean shell = d > rad - 1.0 || x == 8;
					if (!shell) {
						k.air(x, y, z);
						continue;
					}
					boolean face = y >= 6 && Math.abs(z) <= 2 && x >= 10 && x <= 12;
					k.set(x, y, z, face ? fr.achedon12.matriochka.mc.McBlocks.DYED_TERRACOTTA.white().defaultBlockState() : x == 8 ? gold : lac);
				}
		k.air(8, 1, 0, 8, 4, 0);
		// grass and moss creeping in: it fell a long time ago
		k.decay(-6, -1, -6, 14, 8, 6, 0.06);
		// chests inside both halves
		k.mark("hidden", 0, -1, 0, Direction.SOUTH);
		k.mark("hidden", -2, -1, 2, Direction.NORTH);
		k.mark("hidden", 11, 1, 0, Direction.WEST);
	}
}
