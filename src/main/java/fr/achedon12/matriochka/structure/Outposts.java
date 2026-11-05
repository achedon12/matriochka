package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.Direction;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The structures added for replay value, one more per world (tools/content.py REPLAY_STRUCTURES):
 * <ul>
 * <li>bastion: a walled courtyard with corner towers, a gatehouse and a keep (the Gaolers' Gatehouse, the Drowned
 * Bastion);</li>
 * <li>circle: a ring of standing stones and lintels around a sunken altar (the Ember, Hushed and Restless Circles);</li>
 * <li>outpost: a lookout hut on stilts over a supply yard (the Sky, Hanging and Thimble Outposts);</li>
 * <li>caravan: covered wagons drawn up around a fire, a stall and a hitching rail (the Gatherers' and Ephemeral
 * Caravans).</li>
 * </ul>
 * Local coordinates as everywhere: floor at y 0, entrance toward -z.
 */
final class Outposts {
	private Outposts() {}

	static void build(Kit k) {
		switch (k.archetype) {
			case "bastion" -> bastion(k);
			case "circle" -> circle(k);
			case "outpost" -> outpost(k);
			default -> caravan(k);
		}
	}

	// ---------------------------------------------------------------- bastion
	static void bastion(Kit k) {
		Palette p = k.p;
		int R = k.R;
		int S = R - 3;
		k.site(R, 16);
		k.floor(-S + 1, -S + 1, S - 1, S - 1, 0, 1);
		// curtain walls, a walk behind the crenels, buttresses every few blocks
		for (int x = -S; x <= S; x++)
			for (int z = -S; z <= S; z++) {
				boolean edge = Math.abs(x) == S || Math.abs(z) == S;
				if (!edge) continue;
				for (int y = 1; y <= 6; y++) k.set(x, y, z, y == 1 ? p.trim : y == 5 ? p.alt : p.base);
				k.set(x, 7, z, ((x + z) & 1) == 0 ? p.cap : p.wall);
				if ((x + z) % 4 == 0 && (Math.abs(x) < S || Math.abs(z) < S)) {
					Direction out = Math.abs(x) == S ? (x > 0 ? Direction.EAST : Direction.WEST) : (z > 0 ? Direction.SOUTH : Direction.NORTH);
					k.stair(x + out.getStepX(), 1, z + out.getStepZ(), out.getOpposite(), false);
				}
			}
		for (int x = -S + 1; x <= S - 1; x++) {
			k.slab(x, 5, -S + 1, p.slab, true);
			k.slab(x, 5, S - 1, p.slab, true);
		}
		// four round corner towers, the back two with a cone roof
		int[][] corners = {{-S, -S}, {S, -S}, {-S, S}, {S, S}};
		for (int i = 0; i < 4; i++) {
			int cx = corners[i][0], cz = corners[i][1];
			Parts.roundTower(k, cx, cz, 3, 0, 9, cz > 0 && k.world != 7);
			k.mark("spawner", cx, 1, cz, Direction.NORTH);
			k.mark("hidden", cx + (cx > 0 ? -1 : 1), 6, cz, Direction.NORTH);
		}
		// the gatehouse: two thick piers, an arch, a raised portcullis and banners
		for (int s : new int[]{-3, 3}) {
			k.box(s - 1, 1, -S - 1, s + 1, 8, -S + 1, p.base);
			k.set(s, 9, -S, p.cap);
			k.banner(s, 6, -S - 2, Direction.NORTH, p.colA);
		}
		k.air(-2, 1, -S - 1, 2, 4, -S + 1);
		k.arch(-2, 2, 5, -S, true, 1);
		for (int x = -2; x <= 2; x++) k.set(x, 4, -S, p.bars);
		k.set(-2, 5, -S, p.chain);
		k.set(2, 5, -S, p.chain);
		k.runner(-1, -S + 2, 1, -2, 1);
		// the keep at the back: a hall with a banquet table and chandeliers under a hip roof
		int kz0 = S - 9, kz1 = S - 1;
		k.room(-6, kz0, 6, kz1, 0, 6, 3, 2, p.plank);
		k.hip(-6, kz0, 6, kz1, 6, 1);
		k.doorway(0, 1, kz0, Direction.NORTH, 3, 3);
		k.banquet(0, 1, (kz0 + kz1) / 2 + 1, 6, true);
		k.chandelier(-3, 5, (kz0 + kz1) / 2, 1);
		k.chandelier(3, 5, (kz0 + kz1) / 2, 1);
		k.banner(-5, 4, kz1 - 1, Direction.SOUTH, p.colB);
		k.banner(5, 4, kz1 - 1, Direction.SOUTH, p.colB);
		k.mark("guard", 0, 1, kz1 - 1, Direction.NORTH);
		k.mark("hidden", -5, 1, kz0 + 1, Direction.EAST);
		// the courtyard: a well, lamp posts, a smithy corner and supplies
		Parts.fountain(k, 0, 1, -2, 2);
		for (int[] l : new int[][]{{-S + 3, -S + 4}, {S - 3, -S + 4}, {-S + 3, 0}, {S - 3, 0}}) k.lampPost(l[0], 1, l[1], 2);
		k.crates(-S + 2, 1, -2);
		k.crates(S - 3, 1, 2);
		k.barrel(S - 2, 1, -5, Direction.UP);
		k.set(-S + 2, 1, 3, Blocks.ANVIL.defaultBlockState());
		k.set(-S + 2, 1, 4, Kit.facing(Blocks.BLAST_FURNACE.defaultBlockState(), Direction.EAST));
		k.mark("hidden", S - 2, 1, -6, Direction.WEST);
		if (k.world == 3) {
			// the gaolers keep a cell by the gate, its keys on a hook
			k.box(S - 5, 1, -S + 1, S - 1, 4, -S + 4, p.bars);
			k.air(S - 4, 1, -S + 2, S - 2, 3, -S + 3);
			k.set(S - 3, 1, -S + 3, Kit.facing(Blocks.CHEST.defaultBlockState(), Direction.NORTH));
			k.hang(S - 3, 4, -S + 2, 1);
			k.set(-S + 4, 1, -S + 2, ModContent.block("sealed_door").defaultBlockState());
		}
		k.decay(-R, 1, -R, R, 12, R, k.world == 7 ? 0.45 : 0.15);
	}

	// ---------------------------------------------------------------- circle
	static void circle(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 14);
		double ring = R - 3;
		// a paved ring and a rune-inlaid floor that sinks toward the altar
		k.roundFloor(0, 0, 0, ring + 1.5);
		int n = k.large() ? 14 : 10;
		for (int i = 0; i < n; i++) {
			double a = i * Math.PI * 2 / n;
			int x = (int) Math.round(Math.cos(a) * ring), z = (int) Math.round(Math.sin(a) * ring);
			// standing stones lean and vary in height, the Restless Ground's more than any
			int h = 4 + k.hi(x, 0, z, 41, 3);
			k.set(x, 1, z, p.trim);
			for (int y = 2; y <= h; y++) k.set(x, y, z, k.hc(x, y, z, 43, 0.2) ? p.cracked : p.pillar);
			k.set(x, h + 1, z, p.cap);
			// every other pair carries a lintel
			if (i % 2 == 0) {
				double b = (i + 1) * Math.PI * 2 / n;
				int x2 = (int) Math.round(Math.cos(b) * ring), z2 = (int) Math.round(Math.sin(b) * ring);
				int top = Math.max(h, 4 + k.hi(x2, 0, z2, 41, 3)) + 2;
				int steps = Math.max(Math.abs(x2 - x), Math.abs(z2 - z));
				for (int s = 0; s <= steps; s++) {
					int lx = x + Math.round((x2 - x) * s / (float) Math.max(1, steps)), lz = z + Math.round((z2 - z) * s / (float) Math.max(1, steps));
					k.set(lx, top, lz, p.base);
				}
			}
			// a brazier, a soul flame or candles at the foot of every stone
			double c = a + Math.PI / n;
			int bx = (int) Math.round(Math.cos(c) * (ring - 2)), bz = (int) Math.round(Math.sin(c) * (ring - 2));
			if (k.world == 5) k.candles(bx, 1, bz, 1 + k.hi(bx, 1, bz, 47, 3));
			else k.brazier(bx, 1, bz);
		}
		// the sunken altar: three steps down to a dais where the guarded chest waits, spawners under two stones
		for (int d = 1; d <= 3; d++) {
			double rr = 6 - d * 1.3;
			for (int x = -6; x <= 6; x++)
				for (int z = -6; z <= 6; z++) {
					double dist = Math.sqrt(x * x + z * z);
					if (dist > rr + 0.5) continue;
					k.air(x, 1 - d, z);
					k.set(x, -d, z, dist > rr - 0.5 ? p.trim : p.floor);
					if (dist > rr - 0.5 && dist <= rr + 0.5) k.stair(x, 1 - d, z, Kit.inward(x, z).getOpposite(), false);
				}
		}
		k.disc(0, -3, 0, 1.5, p.inlay);
		k.set(0, -3, 0, p.inlay2);
		k.set(-2, -2, 0, p.cap);
		k.set(2, -2, 0, p.cap);
		k.lanternOn(-2, -1, 0);
		k.lanternOn(2, -1, 0);
		k.mark("guard", 0, -2, 1, Direction.NORTH);
		k.mark("spawner", (int) Math.round(ring - 1), 1, 0, Direction.WEST);
		k.mark("spawner", -(int) Math.round(ring - 1), 1, 0, Direction.EAST);
		k.mark("hidden", 0, 1, (int) Math.round(ring) + 1, Direction.NORTH);
		k.mark("hidden", (int) Math.round(ring * 0.7), 1, -(int) Math.round(ring * 0.7), Direction.WEST);
		switch (k.world) {
			case 2 -> {
				// the embers: magma veins radiating from the pit, smouldering heaps of blazing rock
				for (int i = 0; i < 6; i++) {
					double a = i * Math.PI / 3;
					for (int r = 5; r < ring - 1; r++) k.set((int) Math.round(Math.cos(a) * r), 0, (int) Math.round(Math.sin(a) * r), p.accent);
				}
				k.set(3, 1, 5, ModContent.block("blazing_rock_ore").defaultBlockState());
				k.set(-4, 1, -5, ModContent.block("ember_stone").defaultBlockState());
			}
			case 5 -> {
				// the hush: sculk muffling the floor, soul lanterns hung low, no flame anywhere
				for (int x = -R + 2; x <= R - 2; x++)
					for (int z = -R + 2; z <= R - 2; z++) if (k.hc(x, 0, z, 53, 0.12) && x * x + z * z < ring * ring) k.set(x, 0, z, Blocks.SCULK.defaultBlockState());
				k.set(0, 1, (int) ring - 1, Blocks.SCULK_SENSOR.defaultBlockState());
			}
			case 9 -> {
				// the restless: a stone toppled across the ring, the floor split by a scar
				for (int x = -3; x <= 3; x++) k.set(x + 4, 1, 4 - x / 2, p.pillar);
				for (int z = -R + 3; z <= -5; z++) k.set(k.hi(0, 0, z, 59, 3) - 1, 0, z, p.fill);
			}
			default -> {}
		}
		k.decay(-R, 1, -R, R, 10, R, 0.12);
	}

	// ---------------------------------------------------------------- outpost
	static void outpost(Kit k) {
		Palette p = k.p;
		int R = k.R;
		boolean sky = k.world == 4 || k.world == 6;
		int deck = k.large() ? 9 : 6;
		if (sky) {
			k.siteClear(R, deck + 12);
			k.island(0, 0, 0, R - 1, k.large() ? 9 : 6);
		} else {
			k.site(R, deck + 12);
		}
		if (k.world == 10) {
			// the thimble: a dimpled steel cup turned upside down, the outpost built on top of it
			int tr = R - 4;
			for (int y = 0; y <= deck; y++) {
				double rr = tr - y * 0.15;
				for (int x = -tr; x <= tr; x++)
					for (int z = -tr; z <= tr; z++) {
						double d = Math.sqrt(x * x + z * z);
						if (d > rr + 0.5) continue;
						boolean shell = d > rr - 0.6 || y == deck;
						if (!shell) {
							k.air(x, y, z);
							continue;
						}
						boolean dimple = ((x + 2 * y) % 3 == 0) && ((z + y) % 3 == 0);
						k.set(x, y, z, dimple ? Blocks.IRON_BLOCK.defaultBlockState() : Blocks.CUT_COPPER.waxed().unaffected().defaultBlockState());
					}
			}
			k.doorway(0, 1, -tr, Direction.NORTH, 3, 3);
			k.mark("spawner", 3, 1, 2, Direction.NORTH);
			k.mark("spawner", -3, 1, 2, Direction.NORTH);
			k.mark("hidden", 0, 1, tr - 2, Direction.NORTH);
		} else {
			// four log legs braced with fences, a supply yard underneath
			for (int[] c : new int[][]{{-4, -4}, {4, -4}, {-4, 4}, {4, 4}}) {
				for (int y = 1; y < deck; y++) k.set(c[0], y, c[1], Kit.axis(p.log, Direction.Axis.Y));
				k.set(c[0], 0, c[1], p.trim);
				for (int y = 2; y < deck - 1; y += 3) {
					k.set(c[0] + (c[0] > 0 ? -1 : 1), y, c[1], p.fence);
					k.set(c[0], y, c[1] + (c[1] > 0 ? -1 : 1), p.fence);
				}
			}
			k.crates(-2, 1, -2);
			k.crates(1, 1, 2);
			k.barrel(2, 1, -2, Direction.UP);
			k.mark("spawner", 0, 1, 0, Direction.NORTH);
			k.mark("hidden", -2, 1, 2, Direction.EAST);
			for (int y = 1; y <= deck; y++) k.set(0, y, -5, Kit.ladderFacing(Direction.NORTH));
		}
		// the deck, its railing and the lookout hut
		k.box(-5, deck, -5, 5, deck, 5, p.plank);
		for (int x = -5; x <= 5; x++)
			for (int z = -5; z <= 5; z++) if ((Math.abs(x) == 5 || Math.abs(z) == 5) && !(x == 0 && z == -5)) k.set(x, deck + 1, z, p.fence);
		k.room(-3, -1, 3, 4, deck, 4, 3, 2, p.plank);
		k.gable(-3, -1, 3, 4, deck + 4, true, p.plank);
		k.doorway(0, deck + 1, -1, Direction.NORTH, 1, 2);
		k.set(-2, deck + 1, 3, Kit.facing(Blocks.LECTERN.defaultBlockState(), Direction.NORTH));
		k.bed(2, deck + 1, 2, Direction.SOUTH, p.colA);
		k.lanternOn(-2, deck + 1, 0);
		k.mark("guard", 0, deck + 1, 3, Direction.NORTH);
		k.mark("hidden", 2, deck + 1, 0, Direction.WEST);
		// the signal fire and its flags at the corners of the deck
		k.brazier(4, deck + 1, -4);
		k.standingBanner(-4, deck + 1, -4, p.colB);
		k.standingBanner(4, deck + 1, 4, p.colA);
		switch (k.world) {
			case 4 -> k.set(0, deck + 7, 1, Blocks.LIGHTNING_ROD.waxed().unaffected().defaultBlockState());
			case 6 -> {
				// chains dangle from the hanging deck, crystals caught in them
				for (int[] c : new int[][]{{-5, -3}, {5, 3}, {-3, 5}, {3, -5}}) {
					for (int y = deck - 1; y > deck - 5; y--) k.set(c[0], y, c[1], Kit.axis(p.chain, Direction.Axis.Y));
					k.set(c[0], deck - 5, c[1], Blocks.AMETHYST_CLUSTER.defaultBlockState());
				}
			}
			case 10 -> {
				// a giant pin stuck through the hut's roof, as if the thimble was set down in a sewing box
				for (int y = deck + 4; y <= deck + 12; y++) k.set(-4, y, 3, Blocks.IRON_BARS.defaultBlockState());
				k.set(-4, deck + 13, 3, Blocks.WOOL.pick(DyeColor.RED).defaultBlockState());
			}
			default -> {}
		}
		k.decay(-R, 1, -R, R, deck + 8, R, 0.1);
	}

	// ---------------------------------------------------------------- caravan
	static void caravan(Kit k) {
		Palette p = k.p;
		int R = k.R;
		k.site(R, 12);
		// a ring of trampled ground around the fire
		for (int x = -R + 2; x <= R - 2; x++)
			for (int z = -R + 2; z <= R - 2; z++) if (x * x + z * z < (R - 3) * (R - 3) && k.hc(x, 0, z, 71, 0.35)) k.set(x, 0, z, Blocks.COARSE_DIRT.defaultBlockState());
		k.set(0, 0, 0, p.trim);
		k.set(0, 1, 0, Blocks.CAMPFIRE.defaultBlockState());
		for (Direction d : Direction.Plane.HORIZONTAL) k.set(d.getStepX() * 3, 1, d.getStepZ() * 3, Kit.axis(p.log, d.getClockWise().getAxis()));
		k.set(1, 1, 1, Blocks.CAULDRON.defaultBlockState());
		// three covered wagons drawn up around it
		wagon(k, -6, 3, Direction.EAST, p.colA);
		wagon(k, 6, 3, Direction.WEST, p.colB);
		wagon(k, 0, 7, Direction.NORTH, DyeColor.WHITE);
		// a stall for the wares and a hitching rail with hay
		Parts.stall(k, -5, 0, -6, Direction.NORTH, k.variant);
		for (int x = 3; x <= 7; x++) k.set(x, 1, -6, p.fence);
		k.set(5, 1, -5, Blocks.HAY_BLOCK.defaultBlockState());
		k.set(6, 1, -5, Blocks.HAY_BLOCK.defaultBlockState());
		k.set(5, 2, -5, Blocks.HAY_BLOCK.defaultBlockState());
		k.set(7, 1, -5, Blocks.WATER_CAULDRON.defaultBlockState());
		for (int[] l : new int[][]{{-3, -3}, {3, -3}}) k.lampPost(l[0], 1, l[1], 2);
		k.mark("npc", 2, 1, -2, Direction.NORTH);
		k.mark("hidden", 0, 1, 9, Direction.NORTH);
		if (k.world == 1) {
			// the gatherers' haul: baskets of spores, moss on everything, spore blossoms hung under the covers
			k.set(-2, 1, -2, ModContent.block("spore_moss").defaultBlockState());
			k.set(3, 1, 2, Blocks.COMPOSTER.defaultBlockState());
			k.set(-6, 5, 3, ModContent.block("spore_bloom").defaultBlockState());
		} else if (k.world == 8) {
			// the ephemeral folk travel light: autumn leaves drift over half-packed crates, an hourglass on the counter
			for (int x = -R + 2; x <= R - 2; x++)
				for (int z = -R + 2; z <= R - 2; z++) if (k.hc(x, 1, z, 73, 0.08) && k.emptyAt(x, 1, z) && k.solidAt(x, 0, z)) k.set(x, 1, z, Blocks.LEAF_LITTER.defaultBlockState());
			k.crates(-2, 1, 4);
		}
		k.decay(-R, 1, -R, R, 8, R, k.world == 8 ? 0.3 : 0.08);
	}

	/** A covered wagon along an axis: plank bed on wheels, a wool cover on hoops, crates and a lantern inside. */
	private static void wagon(Kit k, int cx, int cz, Direction along, DyeColor cover) {
		Palette p = k.p;
		Direction side = along.getClockWise();
		BlockState wool = Blocks.WOOL.pick(cover).defaultBlockState();
		for (int l = -2; l <= 2; l++) {
			int x = cx + along.getStepX() * l, z = cz + along.getStepZ() * l;
			for (int s = -1; s <= 1; s++) {
				int wx = x + side.getStepX() * s, wz = z + side.getStepZ() * s;
				k.set(wx, 1, wz, Kit.slabOf(p.woodSlab, true));
				// hoops of the cover
				if (Math.abs(s) == 1) {
					k.set(wx, 2, wz, p.fence);
					k.set(wx, 3, wz, wool);
				} else {
					k.set(wx, 4, wz, wool);
				}
			}
			if (Math.abs(l) == 2) {
				// wheels at the corners: dark log ends
				for (int s : new int[]{-2, 2}) k.set(x + side.getStepX() * s, 1, z + side.getStepZ() * s, Kit.axis(p.log, side.getAxis()));
			}
		}
		// the shaft in front, a barrel and a lantern under the cover
		for (int l = 3; l <= 4; l++) k.set(cx + along.getStepX() * l, 1, cz + along.getStepZ() * l, p.fence);
		k.barrel(cx - along.getStepX(), 2, cz - along.getStepZ(), Direction.UP);
		k.set(cx + along.getStepX(), 2, cz + along.getStepZ(), p.lantern);
		k.mark("hidden", cx, 2, cz, along);
	}
}
