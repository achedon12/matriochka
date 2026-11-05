package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.util.List;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.AbstractFurnaceBlock;
import net.minecraft.world.level.block.AnvilBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.SkullBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The lairs of the six lair bosses, built by code when a parcel is created, in place of the plain arena. Every lair shares
 * one plan, seen from its heart (the {@code lair_heart} block at the centre of the chamber floor): a gate and an entrance
 * hall toward the Threshold (north, -Z), a round domed chamber (radius {@link #R}; the fight space within 18 blocks of the
 * heart and 14 blocks above the floor is kept clear) and a treasure alcove behind a seal on the far side (+Z). Each world
 * dresses that plan its own way.
 *
 * <p>The heart wakes the boss when a player comes within {@link #WAKE_RADIUS} blocks; when the boss dies the seal breaks and
 * the alcove chests fill with the world's best loot; ten minutes later the heart re-arms and the seal closes again.
 */
public final class Lairs {
	public static final int R = 24;
	/** Distance from the heart to the outer gate, toward the Threshold. */
	public static final int GATE = 46;
	public static final int WAKE_RADIUS = 10;
	public static final int REARM_TICKS = 20 * 60 * 10;
	public static final int AWAKEN_TICKS = 60;
	/** Depth of the Light Eater's pit below the arena centre (the Leviathan's temple sinks {@link Ocean#LAIR_SINK}). */
	public static final int PIT_DEPTH = 8;
	private static final String TAG = "matriochka.lair:";

	private static final int ARMED = 0, WAKING = 1, AWAKE = 2, BEATEN = 3;

	private Lairs() {}

	/** Where the heart of a world's lair sits, for an arena centre. */
	public static BlockPos heart(int world, BlockPos center) {
		return switch (world) {
			case 5 -> center.below(PIT_DEPTH);
			case 7 -> center.below(Ocean.LAIR_SINK);
			default -> center;
		};
	}

	/** A spot in the forecourt, just outside the gate. */
	public static BlockPos forecourt(int world, BlockPos heart) {
		return heart.offset(0, theme(world).rise(), -GATE - 4);
	}

	// ================================================================ building
	/** The dressing of one lair: materials and the height of its dome. */
	private record Theme(BlockState floor, BlockState floor2, BlockState wall, BlockState wall2, BlockState roof, BlockState light,
						 BlockState base, int top, int rise) {}

	private static BlockState mb(String id) {
		return ModContent.block(id).defaultBlockState();
	}

	private static Theme theme(int world) {
		return switch (world) {
			case 1 -> new Theme(mb("spore_moss"), mb("rootstone"), Blocks.HONEYCOMB_BLOCK.defaultBlockState(), mb("rootstone"),
				Blocks.HONEYCOMB_BLOCK.defaultBlockState(), mb("spore_bloom"), mb("rootstone"), 22, 0);
			case 2 -> new Theme(Blocks.POLISHED_BLACKSTONE.defaultBlockState(), mb("ashrock"), mb("ashrock"), Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState(),
				mb("ashrock"), mb("ember_stone"), mb("ashrock"), 22, 0);
			case 5 -> new Theme(mb("umbral_moss"), mb("umbral_stone"), mb("umbral_stone"), Blocks.POLISHED_DEEPSLATE.defaultBlockState(),
				mb("umbral_stone"), Blocks.COBBLED_DEEPSLATE.defaultBlockState(), mb("umbral_stone"), 24, PIT_DEPTH);
			case 6 -> new Theme(mb("inverted_stone"), Blocks.PURPUR_BLOCK.defaultBlockState(), mb("inverted_stone"), Blocks.QUARTZ_BLOCK.defaultBlockState(),
				mb("inverted_stone"), Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState(), mb("inverted_stone"), 22, 0);
			case 7 -> new Theme(mb("abyssal_sand"), mb("trench_rock"), mb("trench_rock"), Blocks.PRISMARINE_BRICKS.defaultBlockState(),
				Blocks.DARK_PRISMARINE.defaultBlockState(), Blocks.SEA_LANTERN.defaultBlockState(), mb("trench_rock"), 22, 0);
			default -> new Theme(mb("living_rock"), mb("flesh_stone"), mb("living_rock"), mb("flesh_stone"),
				mb("living_rock"), mb("pulse_vein"), mb("living_rock"), 22, 0);
		};
	}

	/** Block writer relative to the heart, with the world's fluid (water in the Pressure Ocean, air elsewhere). */
	private static final class Draw {
		final ServerLevel level;
		final BlockPos o;
		final int world;
		final Theme th;
		final BlockState fluid;
		final RandomSource rnd;

		Draw(ServerLevel level, BlockPos heart, int world) {
			this.level = level;
			this.o = heart;
			this.world = world;
			this.th = theme(world);
			this.fluid = world == 7 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState();
			this.rnd = RandomSource.create(heart.asLong() * 31L + world);
		}

		void set(int x, int y, int z, BlockState s) {
			level.setBlock(o.offset(x, y, z), s, 2);
		}

		BlockState get(int x, int y, int z) {
			return level.getBlockState(o.offset(x, y, z));
		}

		void box(int x0, int y0, int z0, int x1, int y1, int z1, BlockState s) {
			for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++)
				for (int y = Math.min(y0, y1); y <= Math.max(y0, y1); y++)
					for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) set(x, y, z, s);
		}

		void clear(int x0, int y0, int z0, int x1, int y1, int z1) {
			box(x0, y0, z0, x1, y1, z1, fluid);
		}

		/** Fills down from y to the first solid block so nothing floats. */
		void foundation(int x, int y, int z) {
			for (int i = 0; i < 48; i++) {
				BlockState s = get(x, y - i, z);
				if (!s.isAir() && s.getFluidState().isEmpty()) return;
				set(x, y - i, z, th.base);
			}
		}

		float r() {
			return rnd.nextFloat();
		}
	}

	/** Dome height above the floor at a distance from the heart. */
	private static int ceilAt(Theme th, double d) {
		return th.top - (int) Math.round(6.0 * d * d / (R * R));
	}

	/** Floor height of the entrance hall at z (the Light Eater's hall descends into its pit). */
	private static int hallFloor(Theme th, int z) {
		if (th.rise == 0) return 0;
		double t = (-z - R) / (double) (GATE - 8 - R);
		return (int) Math.round(th.rise * Math.max(0, Math.min(1, t)));
	}

	public static void build(ServerLevel level, int world, BlockPos center) {
		BlockPos heart = heart(world, center);
		Draw d = new Draw(level, heart, world);
		if (world == Ocean.WORLD) cutTrench(d);
		shell(d);
		switch (world) {
			case 1 -> hive(d);
			case 2 -> forge(d);
			case 5 -> pit(d);
			case 6 -> mirrors(d);
			case 7 -> trench(d);
			default -> cavern(d);
		}
		seal(d);
		level.setBlock(heart, ModContent.block("lair_heart").defaultBlockState(), 3);
	}

	/** The shared plan: foundation, floor, round wall, dome, entrance hall, gate, forecourt and alcove. */
	private static void shell(Draw d) {
		Theme th = d.th;
		// chamber
		for (int x = -R - 1; x <= R + 1; x++) {
			for (int z = -R - 1; z <= R + 1; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist > R + 0.5) continue;
				int ceil = ceilAt(th, dist);
				d.foundation(x, -4, z);
				for (int y = -3; y <= -1; y++) d.set(x, y, z, y == -1 ? th.floor : th.floor2);
				if (dist >= R - 1.5) {
					for (int y = 0; y <= ceil + 1; y++) d.set(x, y, z, (y == 4 || y == 11) ? th.wall2 : th.wall);
				} else {
					d.clear(x, 0, z, x, ceil - 1, z);
					d.set(x, ceil, z, th.roof);
					d.set(x, ceil + 1, z, th.roof);
				}
			}
		}
		// entrance hall, from the gate to the chamber
		for (int z = -GATE; z <= -(R - 2); z++) {
			int fy = hallFloor(th, z);
			for (int x = -6; x <= 6; x++) {
				d.foundation(x, fy - 3, z);
				d.set(x, fy - 2, z, th.floor2);
				d.set(x, fy - 1, z, Math.abs(x) <= 1 ? th.wall2 : th.floor);
				if (Math.abs(x) >= 5) {
					for (int y = fy; y <= fy + 10; y++) d.set(x, y, z, th.wall);
				} else {
					d.clear(x, fy, z, x, fy + 8, z);
					d.set(x, fy + 9, z, th.roof);
					d.set(x, fy + 10, z, th.roof);
				}
			}
			if (Math.floorMod(z, 4) == 0) {
				for (int y = fy; y <= fy + 8; y++) {
					d.set(-5, y, z, th.wall2);
					d.set(5, y, z, th.wall2);
				}
			} else if (Math.floorMod(z, 4) == 2) {
				d.set(-5, fy + 5, z, th.light);
				d.set(5, fy + 5, z, th.light);
			}
		}
		// stairs of the descending hall are solid all the way down
		// forecourt in front of the gate
		int gy = hallFloor(th, -GATE);
		for (int z = -GATE - 8; z <= -GATE - 1; z++) {
			for (int x = -8; x <= 8; x++) {
				d.foundation(x, gy - 2, z);
				d.set(x, gy - 1, z, (Math.abs(x) + Math.abs(z)) % 3 == 0 ? th.floor2 : th.floor);
				d.clear(x, gy, z, x, gy + 11, z);
			}
		}
		// the gate: a thick frame with an arched opening
		for (int z = -GATE - 1; z <= -GATE; z++) {
			for (int x = -8; x <= 8; x++) {
				for (int y = gy; y <= gy + 13; y++) {
					boolean open = Math.abs(x) <= 3 && (y < gy + 7 || (y == gy + 7 && Math.abs(x) <= 2) || (y == gy + 8 && Math.abs(x) <= 1));
					if (open) d.set(x, y, z, d.fluid);
					else d.set(x, y, z, (Math.abs(x) == 4 || y == gy + 13 || (y == gy + 9 && Math.abs(x) <= 4)) ? th.wall2 : th.wall);
				}
			}
		}
		d.set(0, gy + 10, -GATE - 1, th.light);
		d.set(-6, gy + 6, -GATE - 1, th.light);
		d.set(6, gy + 6, -GATE - 1, th.light);
		// treasure alcove behind the chamber, opposite the gate
		for (int x = -6; x <= 6; x++) {
			for (int z = R + 1; z <= R + 10; z++) {
				d.foundation(x, -2, z);
				for (int y = -1; y <= 7; y++) {
					boolean shellBlock = Math.abs(x) == 6 || z == R + 10 || y == -1 || y == 7;
					d.set(x, y, z, shellBlock ? (y == -1 ? th.floor2 : th.wall) : d.fluid);
				}
			}
		}
		for (int[] c : new int[][]{{-5, R + 1}, {5, R + 1}, {-5, R + 9}, {5, R + 9}}) {
			for (int y = 0; y <= 6; y++) d.set(c[0], y, c[1], th.wall2);
			d.set(c[0], 6, c[1], th.light);
		}
		for (int x = -3; x <= 3; x++) {
			d.set(x, 0, R + 8, th.wall2);
			d.set(x, 6, R + 5, th.light.is(Blocks.COBBLED_DEEPSLATE) ? mb("faint_glow") : th.light);
		}
		// frame of the seal, one block proud of the chamber wall
		for (int y = 0; y <= 6; y++) {
			d.set(-4, y, R - 2, th.wall2);
			d.set(4, y, R - 2, th.wall2);
		}
		for (int x = -4; x <= 4; x++) d.set(x, 6, R - 2, x == 0 ? th.light : th.wall2);
	}

	/** Seal blocks closing the treasure alcove (inside the chamber wall, behind the frame). */
	private static void seal(Draw d) {
		BlockState seal = mb("sealed_brick");
		for (int x = -3; x <= 3; x++)
			for (int y = 0; y <= 5; y++)
				for (int z = R - 1; z <= R; z++) d.set(x, y, z, seal);
	}

	// ---------------------------------------------------------------- Spore Queen: the hive
	private static void hive(Draw d) {
		Theme th = d.th;
		BlockState comb = Blocks.HONEYCOMB_BLOCK.defaultBlockState();
		BlockState nest = Blocks.BEE_NEST.defaultBlockState();
		BlockState bloom = mb("spore_bloom");
		BlockState root = mb("rootstone");
		BlockState moss = mb("spore_moss");
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist > R + 0.5) continue;
				double a = Math.atan2(z, x);
				// floor: a honeycomb lattice of root ribs over spore moss, honey around the heart
				if (dist < R - 1.5) {
					boolean rib = Math.floorMod(x + 2 * z, 7) == 0 || Math.floorMod(x - 2 * z, 7) == 0;
					BlockState f = dist <= 4.5 ? comb : rib ? root : moss;
					if (Math.abs(dist - 3) < 0.5 || (!rib && d.r() < 0.02)) f = bloom;
					d.set(x, -1, z, f);
				}
				int ceil = ceilAt(th, dist);
				if (dist >= R - 1.5) {
					if (Math.abs(x) <= 4 && z < 0) continue;
					// ribbed comb wall, nests and glowing sacs set into it
					boolean rib = Math.abs(Math.sin(a * 12)) < 0.12;
					for (int y = 0; y <= ceil + 1; y++) {
						float n = d.r();
						BlockState s = rib ? root : n < 0.05 ? nest : n < 0.08 ? bloom : comb;
						d.set(x, y, z, s);
					}
				} else if (d.r() < 0.06) {
					d.set(x, ceil, z, bloom);
				}
			}
		}
		// glowing spore sacs hanging from the dome, never below the headroom
		for (int i = 0; i < 16; i++) {
			double a = d.r() * Math.PI * 2, dist = 3 + d.r() * 17;
			int x = (int) Math.round(Math.cos(a) * dist), z = (int) Math.round(Math.sin(a) * dist);
			int ceil = ceilAt(th, dist);
			int bottom = Math.max(15, ceil - 3 - (int) (d.r() * 3));
			for (int y = ceil - 1; y > bottom + 1; y--) d.set(x, y, z, root);
			for (int dx = -1; dx <= 1; dx++)
				for (int dy = -1; dy <= 1; dy++)
					for (int dz = -1; dz <= 1; dz++)
						if (Math.abs(dx) + Math.abs(dy) + Math.abs(dz) <= 2) d.set(x + dx, bottom + dy, z + dz, bloom);
			d.set(x, bottom, z, Blocks.VERDANT_FROGLIGHT.defaultBlockState());
		}
		// spore blossoms shedding over the fight
		for (int i = 0; i < 10; i++) {
			double a = i * Math.PI / 5 + 0.3, dist = 8 + (i % 3) * 4;
			int x = (int) Math.round(Math.cos(a) * dist), z = (int) Math.round(Math.sin(a) * dist);
			d.set(x, ceilAt(th, dist) - 1, z, Blocks.SPORE_BLOSSOM.defaultBlockState());
		}
		// cocoon pods along the wall
		BlockState silk = Blocks.MUSHROOM_STEM.defaultBlockState();
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6 + Math.PI / 12;
			if (Math.abs(Math.cos(a)) * 20.5 < 8) continue; // keep the hall and the seal free
			int cx = (int) Math.round(Math.cos(a) * 20.5), cz = (int) Math.round(Math.sin(a) * 20.5);
			int h = 3 + (i % 2);
			for (int dx = -2; dx <= 2; dx++)
				for (int dy = -h; dy <= h; dy++)
					for (int dz = -2; dz <= 2; dz++) {
						double e = dx * dx / 4.0 + dy * dy / (double) (h * h) + dz * dz / 4.0;
						if (e > 1.0) continue;
						if (Math.sqrt((cx + dx) * (cx + dx) + (cz + dz) * (cz + dz)) < 18.5) continue;
						d.set(cx + dx, h + dy, cz + dz, e > 0.55 ? silk : bloom);
					}
			d.set(cx, 2 * h + 1, cz, root);
			d.set(cx, 0, cz, Blocks.COBWEB.defaultBlockState());
		}
		// the hall: a root tunnel, the gate: a comb mouth studded with nests
		for (int z = -GATE + 1; z <= -R; z++) {
			if (Math.floorMod(z, 3) == 0) {
				d.set(-4, 8, z, Blocks.HANGING_ROOTS.defaultBlockState());
				d.set(4, 8, z, Blocks.HANGING_ROOTS.defaultBlockState());
			}
			if (Math.floorMod(z, 5) == 1) d.set(0, 9, z, bloom);
		}
		for (int x = -8; x <= 8; x++)
			for (int y = 0; y <= 13; y++) {
				double r = Math.sqrt(x * x + (y - 4.5) * (y - 4.5));
				if (r > 4.2 && r < 8.6 && d.get(x, y, -GATE - 1).isSolid()) d.set(x, y, -GATE - 1, (x + y) % 4 == 0 ? nest : (x * y) % 7 == 0 ? bloom : comb);
			}
		for (int x : new int[]{-7, 7}) {
			for (int y = 0; y <= 4; y++) d.set(x, y, -GATE - 5, comb);
			d.set(x, 5, -GATE - 5, bloom);
		}
		for (int x = -4; x <= 4; x++) d.set(x, -1, R + 5, comb);
	}

	// ---------------------------------------------------------------- Ash Titan: the forge-hall
	private static void forge(Draw d) {
		Theme th = d.th;
		BlockState lava = Blocks.LAVA.defaultBlockState();
		BlockState black = Blocks.POLISHED_BLACKSTONE.defaultBlockState();
		BlockState bricks = Blocks.POLISHED_BLACKSTONE_BRICKS.defaultBlockState();
		BlockState basalt = Blocks.SMOOTH_BASALT.defaultBlockState();
		BlockState gilded = Blocks.GILDED_BLACKSTONE.defaultBlockState();
		BlockState ember = mb("ember_stone");
		BlockState magma = Blocks.MAGMA_BLOCK.defaultBlockState();
		// tiled floor, cut by four lava channels running from the wall toward the heart
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist >= R - 1.5) continue;
				boolean channel = dist >= 6 && dist <= 21 && (x == z || x == z + 1 || x == -z || x == -z + 1);
				if (channel) {
					d.set(x, -2, z, black);
					d.set(x, -1, z, lava);
				} else {
					boolean tile = ((Math.floorDiv(x, 3) + Math.floorDiv(z, 3)) & 1) == 0;
					d.set(x, -1, z, dist <= 4.5 ? (Math.abs(dist - 3) < 0.5 ? ember : bricks) : tile ? black : basalt);
				}
			}
		}
		// banded walls with ember seams
		for (int i = 0; i < 48; i++) {
			double a = i * Math.PI / 24;
			int x = (int) Math.round(Math.cos(a) * (R - 1)), z = (int) Math.round(Math.sin(a) * (R - 1));
			if (Math.abs(x) <= 4 && z < 0) continue;
			d.set(x, 2, z, ember);
			d.set(x, 8, z, i % 2 == 0 ? magma : ember);
		}
		// eight forge pillars, anvils between them
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4 + Math.PI / 8;
			int x = (int) Math.round(Math.cos(a) * 20.5), z = (int) Math.round(Math.sin(a) * 20.5);
			int top = ceilAt(th, 20.5);
			d.box(x, 0, z, x + 1, top, z + 1, bricks);
			d.box(x, 0, z, x + 1, 0, z + 1, gilded);
			d.box(x, 6, z, x + 1, 6, z + 1, ember);
			double b = a + Math.PI / 8;
			int ax = (int) Math.round(Math.cos(b) * 20), az = (int) Math.round(Math.sin(b) * 20);
			if (Math.abs(ax) <= 4 && az < 0 || Math.abs(ax) <= 5 && az > 0) continue;
			Block anvil = i % 3 == 0 ? Blocks.ANVIL : i % 3 == 1 ? Blocks.CHIPPED_ANVIL : Blocks.DAMAGED_ANVIL;
			d.set(ax, 0, az, bricks);
			d.set(ax, 1, az, anvil.defaultBlockState().setValue(AnvilBlock.FACING, i % 2 == 0 ? Direction.NORTH : Direction.EAST));
		}
		// chains from the vault, each holding a lantern above the fight
		for (int i = 0; i < 18; i++) {
			double a = d.r() * Math.PI * 2, dist = 5 + d.r() * 13;
			int x = (int) Math.round(Math.cos(a) * dist), z = (int) Math.round(Math.sin(a) * dist);
			int ceil = ceilAt(th, dist);
			int low = 14 + (int) (d.r() * 3);
			for (int y = ceil - 1; y > low; y--) d.set(x, y, z, Blocks.IRON_CHAIN.defaultBlockState());
			d.set(x, low, z, Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, true));
		}
		// the great furnace, built into the east wall, its chimney through the vault
		for (int x = 19; x <= 28; x++)
			for (int z = -6; z <= 6; z++)
				for (int y = -1; y <= 14; y++) {
					boolean edge = x == 28 || Math.abs(z) == 6 || y == -1 || y == 14 || x == 19;
					d.set(x, y, z, edge ? (y == 7 || y == 14 ? gilded : bricks) : magma);
				}
		for (int z = -4; z <= 4; z++)
			for (int y = 0; y <= 6; y++) {
				boolean mouth = Math.abs(z) <= 3 && y <= 5 && !(y == 5 && Math.abs(z) == 3);
				if (!mouth) continue;
				d.set(19, y, z, Blocks.IRON_BARS.defaultBlockState());
				for (int x = 20; x <= 24; x++) d.set(x, y, z, y == 0 ? lava : Blocks.AIR.defaultBlockState());
				d.set(25, y, z, magma);
			}
		for (int z = -5; z <= 5; z++) {
			d.set(19, 8, z, Blocks.FURNACE.defaultBlockState().setValue(AbstractFurnaceBlock.FACING, Direction.WEST).setValue(AbstractFurnaceBlock.LIT, true));
			d.set(19, 10, z, Blocks.BLAST_FURNACE.defaultBlockState().setValue(AbstractFurnaceBlock.FACING, Direction.WEST).setValue(AbstractFurnaceBlock.LIT, true));
		}
		for (int y = 15; y <= th.top + 7; y++)
			for (int x = 22; x <= 25; x++)
				for (int z = -2; z <= 1; z++) {
					boolean inner = x >= 23 && x <= 24 && z >= -1 && z <= 0;
					d.set(x, y, z, inner ? Blocks.AIR.defaultBlockState() : bricks);
				}
		for (int x = 23; x <= 24; x++)
			for (int z = -1; z <= 0; z++) d.set(x, 14, z, Blocks.CAMPFIRE.defaultBlockState());
		// hall: lava behind iron grates, the gate guarded by two anvils and braziers
		for (int z = -GATE + 3; z <= -R - 2; z += 6) {
			for (int sx : new int[]{-1, 1}) {
				d.box(sx * 6, 0, z - 1, sx * 7, 4, z + 1, bricks);
				d.box(sx * 6, 1, z, sx * 6, 2, z, lava);
				d.set(sx * 5, 1, z, Blocks.IRON_BARS.defaultBlockState());
				d.set(sx * 5, 2, z, Blocks.IRON_BARS.defaultBlockState());
			}
		}
		for (int x = -2; x <= 2; x += 2)
			for (int y = 5; y <= 7; y++) d.set(x, y, -GATE, Blocks.IRON_CHAIN.defaultBlockState());
		for (int sx : new int[]{-1, 1}) {
			d.set(sx * 7, 0, -GATE - 4, bricks);
			d.set(sx * 7, 1, -GATE - 4, Blocks.ANVIL.defaultBlockState());
			d.set(sx * 5, 0, -GATE - 7, bricks);
			d.set(sx * 5, 1, -GATE - 7, Blocks.CAMPFIRE.defaultBlockState());
			for (int y = 0; y <= 13; y++) d.set(sx * 8, y, -GATE - 1, y % 4 == 0 ? gilded : bricks);
		}
		for (int x = -4; x <= 4; x++) d.set(x, -1, R + 5, gilded);
	}

	// ---------------------------------------------------------------- Light Eater: the lightless pit
	private static void pit(Draw d) {
		Theme th = d.th;
		BlockState bone = Blocks.BONE_BLOCK.defaultBlockState();
		BlockState web = Blocks.COBWEB.defaultBlockState();
		BlockState tiles = Blocks.CRACKED_DEEPSLATE_TILES.defaultBlockState();
		BlockState sculk = Blocks.SCULK.defaultBlockState();
		BlockState cobbled = Blocks.COBBLED_DEEPSLATE.defaultBlockState();
		BlockState campfire = Blocks.CAMPFIRE.defaultBlockState().setValue(CampfireBlock.LIT, false);
		// floor: moss, sculk creeping in, cracked tiles in rings
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist >= R - 1.5) {
					if (dist <= R + 0.5 && !(Math.abs(x) <= 4 && z < 0)) {
						int ceil = ceilAt(th, dist);
						for (int y = 0; y <= ceil; y++) {
							// claw marks raked across the wall
							boolean claw = Math.floorMod(x + z + y, 9) == 0 && y >= 2 && y <= 9;
							if (claw) d.set(x, y, z, cobbled);
						}
					}
					continue;
				}
				BlockState f = th.floor;
				if (Math.abs(dist - 6) < 0.5 || Math.abs(dist - 12) < 0.5) f = tiles;
				else if (d.r() < 0.07) f = sculk;
				if (dist <= 3.5) f = Blocks.POLISHED_DEEPSLATE.defaultBlockState();
				d.set(x, -1, z, f);
			}
		}
		// bone heaps along the wall, crowned with skulls and snuffed candles
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6 + 0.2;
			if (Math.abs(Math.cos(a)) * 20.5 < 8) continue;
			double dist = 20.5;
			int cx = (int) Math.round(Math.cos(a) * dist), cz = (int) Math.round(Math.sin(a) * dist);
			int hr = 2 + i % 2;
			for (int dx = -hr; dx <= hr; dx++)
				for (int dz = -hr; dz <= hr; dz++) {
					int px = cx + dx, pz = cz + dz;
					if (Math.sqrt(px * px + pz * pz) < 18.5) continue;
					int h = hr - (int) Math.round(Math.sqrt(dx * dx + dz * dz));
					for (int y = 0; y < h; y++) d.set(px, y, pz, bone);
					if (h > 0 && d.r() < 0.35) d.set(px, h, pz, Blocks.SKELETON_SKULL.defaultBlockState().setValue(SkullBlock.ROTATION, d.rnd.nextInt(16)));
					else if (h > 0 && d.r() < 0.3) d.set(px, h, pz, Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.CANDLES, 1 + d.rnd.nextInt(4)).setValue(CandleBlock.LIT, false));
					else if (h == 0 && d.r() < 0.3) d.set(px, 0, pz, web);
				}
		}
		// snuffed lanterns: empty cages on chains, above the fight
		for (int i = 0; i < 14; i++) {
			double a = d.r() * Math.PI * 2, dist = 4 + d.r() * 14;
			int x = (int) Math.round(Math.cos(a) * dist), z = (int) Math.round(Math.sin(a) * dist);
			int ceil = ceilAt(th, dist);
			int low = 15 + (int) (d.r() * 4);
			for (int y = ceil - 1; y > low; y--) d.set(x, y, z, Blocks.IRON_CHAIN.defaultBlockState());
			d.set(x, low, z, Blocks.IRON_BARS.defaultBlockState());
			d.set(x, low - 1, z, web);
		}
		// cold braziers between the heaps
		for (int i = 0; i < 8; i++) {
			double a = i * Math.PI / 4 + Math.PI / 8;
			int x = (int) Math.round(Math.cos(a) * 19.5), z = (int) Math.round(Math.sin(a) * 19.5);
			d.set(x, 0, z, Blocks.POLISHED_DEEPSLATE.defaultBlockState());
			d.set(x, 1, z, campfire);
		}
		// the hall descends in the dark; cobwebs in its corners, skulls over the gate
		for (int z = -GATE + 1; z <= -R; z++) {
			int fy = hallFloor(th, z);
			if (d.r() < 0.4) d.set(-4, fy + 8, z, web);
			if (d.r() < 0.4) d.set(4, fy + 8, z, web);
			if (Math.floorMod(z, 7) == 0) {
				d.set(-4, fy, z, bone);
				d.set(4, fy, z, Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT, false));
			}
		}
		int gy = hallFloor(th, -GATE);
		for (int x = -6; x <= 6; x += 2) d.set(x, gy + 14, -GATE - 1, Blocks.SKELETON_SKULL.defaultBlockState().setValue(SkullBlock.ROTATION, 8));
		for (int x = -3; x <= 3; x++) d.set(x, gy + 7 - (Math.abs(x) == 3 ? 1 : 0), -GATE - 1, bone);
		for (int sx : new int[]{-1, 1}) {
			d.set(sx * 6, gy, -GATE - 5, Blocks.POLISHED_DEEPSLATE.defaultBlockState());
			d.set(sx * 6, gy + 1, -GATE - 5, campfire);
			d.box(sx * 7, gy, -GATE - 8, sx * 8, gy + 1, -GATE - 7, bone);
		}
		for (int x = -4; x <= 4; x++) d.set(x, -1, R + 5, Blocks.POLISHED_DEEPSLATE.defaultBlockState());
	}

	// ---------------------------------------------------------------- Your Double: the hall of mirrors
	private static void mirrors(Draw d) {
		Theme th = d.th;
		BlockState glass = mb("mirror_glass");
		BlockState quartz = Blocks.QUARTZ_BLOCK.defaultBlockState();
		BlockState pillar = Blocks.QUARTZ_PILLAR.defaultBlockState();
		BlockState chisel = Blocks.CHISELED_QUARTZ_BLOCK.defaultBlockState();
		BlockState purpur = Blocks.PURPUR_BLOCK.defaultBlockState();
		BlockState frog = Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState();
		BlockState prism = mb("prism_moss");
		// checkered floor with a glowing glass ring; the vault repeats the checker, upside down
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist >= R - 1.5) continue;
				boolean check = ((Math.floorDiv(x, 2) + Math.floorDiv(z, 2)) & 1) == 0;
				BlockState f = check ? th.floor : purpur;
				if (Math.abs(dist - 7) < 0.6) {
					f = glass;
					d.set(x, -2, z, frog);
				} else if (Math.abs(dist - 14) < 0.5) f = prism;
				else if (dist <= 3.5) f = chisel;
				d.set(x, -1, z, f);
				d.set(x, ceilAt(th, dist), z, check ? th.roof : purpur);
			}
		}
		// twelve tall mirrors around the room; one in three is broken
		for (int i = 0; i < 12; i++) {
			if (i == 9 || i == 3) continue;
			double a = i * Math.PI / 6;
			double cx = Math.cos(a) * 21, cz = Math.sin(a) * 21;
			double tx = -Math.sin(a), tz = Math.cos(a);
			boolean broken = i % 3 == 1;
			for (double s = -3; s <= 3; s += 0.5) {
				int x = (int) Math.round(cx + tx * s), z = (int) Math.round(cz + tz * s);
				for (int y = 0; y <= 11; y++) {
					boolean frame = Math.abs(s) >= 3 || y == 0 || y == 11;
					BlockState st = frame ? (y == 11 && Math.abs(s) < 1 ? chisel : Math.abs(s) >= 3 ? pillar : quartz) : glass;
					if (broken) {
						// a jagged hole through the glass and a missing corner of the frame
						if (!frame && (y + Math.abs(s) * 1.7) % 5 < 2.2 && y > 3) st = Blocks.AIR.defaultBlockState();
						if (frame && y >= 8 && s >= 2) st = Blocks.AIR.defaultBlockState();
					}
					d.set(x, y, z, st);
				}
			}
			d.set((int) Math.round(Math.cos(a) * 22.5), 12, (int) Math.round(Math.sin(a) * 22.5), frog);
			if (broken) {
				// shards on the floor in front of it
				for (int k = 0; k < 5; k++) {
					int x = (int) Math.round(Math.cos(a) * (19 + d.r()) + tx * (d.r() * 6 - 3)), z = (int) Math.round(Math.sin(a) * (19 + d.r()) + tz * (d.r() * 6 - 3));
					if (Math.sqrt(x * x + z * z) >= 18.5) d.set(x, 0, z, k % 2 == 0 ? Blocks.AMETHYST_CLUSTER.defaultBlockState() : Blocks.GLASS_PANE.defaultBlockState());
				}
			}
		}
		// an inverted chandelier hanging from the apex
		for (int y = 15; y < th.top; y++) d.set(0, y, 0, pillar);
		for (int[] o : new int[][]{{2, 0}, {-2, 0}, {0, 2}, {0, -2}}) {
			d.set(o[0], 16, o[1], quartz);
			d.set(o[0], 15, o[1], frog);
		}
		d.set(0, 14 + 1, 0, frog);
		// the hall: mirrors between quartz pilasters; the gate: a great broken frame
		for (int z = -GATE + 1; z <= -R; z++) {
			if (Math.floorMod(z, 4) == 0) continue;
			for (int y = 1; y <= 6; y++) {
				d.set(-5, y, z, glass);
				d.set(5, y, z, glass);
			}
			if (Math.floorMod(z, 4) == 2) d.set(0, 9, z, frog);
		}
		for (int x = -8; x <= 8; x++)
			for (int y = 0; y <= 13; y++) {
				if (!d.get(x, y, -GATE - 1).isSolid()) continue;
				boolean frame = Math.abs(x) >= 7 || y >= 12 || Math.abs(x) == 4;
				BlockState st = frame ? (Math.abs(x) >= 7 ? pillar : quartz) : glass;
				if (!frame && x > 0 && y > 8) st = Blocks.AIR.defaultBlockState();
				if (x >= 6 && y >= 11) st = Blocks.AIR.defaultBlockState();
				d.set(x, y, -GATE - 1, st);
			}
		for (int sx : new int[]{-1, 1}) {
			d.set(sx * 6, 0, -GATE - 6, chisel);
			d.set(sx * 6, 1, -GATE - 6, Blocks.AMETHYST_CLUSTER.defaultBlockState());
		}
		for (int x = -4; x <= 4; x++) {
			d.set(x, -1, R + 5, chisel);
			for (int y = 0; y <= 6; y++) d.set(x, y, R + 10, Math.abs(x) <= 3 && y >= 1 && y <= 5 ? glass : quartz);
		}
	}

	// ---------------------------------------------------------------- Pressure Leviathan: the sunken trench temple
	private static void trench(Draw d) {
		Theme th = d.th;
		BlockState bricks = Blocks.PRISMARINE_BRICKS.defaultBlockState();
		BlockState dark = Blocks.DARK_PRISMARINE.defaultBlockState();
		BlockState prismarine = Blocks.PRISMARINE.defaultBlockState();
		BlockState lantern = Blocks.SEA_LANTERN.defaultBlockState();
		BlockState coral = mb("pressure_coral");
		BlockState rock = mb("trench_rock");
		BlockState water = Blocks.WATER.defaultBlockState();
		Block[] blocks = {Blocks.TUBE_CORAL_BLOCK, Blocks.BRAIN_CORAL_BLOCK, Blocks.BUBBLE_CORAL_BLOCK, Blocks.FIRE_CORAL_BLOCK, Blocks.HORN_CORAL_BLOCK};
		Block[] plants = {Blocks.TUBE_CORAL, Blocks.BRAIN_CORAL, Blocks.BUBBLE_CORAL, Blocks.FIRE_CORAL, Blocks.HORN_CORAL,
			Blocks.TUBE_CORAL_FAN, Blocks.BRAIN_CORAL_FAN, Blocks.FIRE_CORAL_FAN};
		// flagstones over the sand: a cross of paths and two rings; seagrass and coral toward the walls
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist >= R - 1.5) continue;
				BlockState f = th.floor;
				if (Math.abs(x) <= 1 || Math.abs(z) <= 1 || Math.abs(dist - 9) < 0.6 || Math.abs(dist - 16) < 0.6) f = rock;
				if (dist <= 4.5) f = Math.abs(dist - 3) < 0.5 ? lantern : dark;
				d.set(x, -1, z, f);
				if (dist >= 18.5 && f == th.floor) {
					float n = d.r();
					if (n < 0.25) d.set(x, 0, z, Blocks.SEAGRASS.defaultBlockState());
					else if (n < 0.33) d.set(x, 0, z, plants[d.rnd.nextInt(plants.length)].defaultBlockState());
				}
				// a broken vault: holes let the dim light of the surface fall in
				int ceil = ceilAt(th, dist);
				double hole = Math.sin(x * 0.45) * Math.cos(z * 0.38) + Math.sin((x + z) * 0.21);
				if (hole > 1.15 && dist > 6) {
					d.set(x, ceil, z, water);
					d.set(x, ceil + 1, z, water);
				}
			}
		}
		// twelve pressure-cracked pillars; the sea has broken some of them
		for (int i = 0; i < 12; i++) {
			double a = i * Math.PI / 6 + Math.PI / 12;
			int cx = (int) Math.round(Math.cos(a) * 20.5), cz = (int) Math.round(Math.sin(a) * 20.5);
			int top = ceilAt(th, 20.5);
			int h = i % 3 == 2 ? 5 + d.rnd.nextInt(6) : top;
			for (int dx = -1; dx <= 1; dx++)
				for (int dz = -1; dz <= 1; dz++) {
					if (Math.sqrt((cx + dx) * (cx + dx) + (cz + dz) * (cz + dz)) < 18.5) continue;
					for (int y = 0; y < h; y++) {
						boolean crack = Math.floorMod(y * 3 + dx * 5 + dz * 7 + i, 11) == 0;
						BlockState st = y == 0 ? dark : crack ? (d.r() < 0.5 ? coral : Blocks.DEAD_BRAIN_CORAL_BLOCK.defaultBlockState()) : (y % 6 == 3 ? prismarine : bricks);
						d.set(cx + dx, y, cz + dz, st);
					}
				}
			d.set(cx, 0, cz, dark);
			if (h < top) {
				// rubble of the fallen drum lies at its foot
				for (int k = 0; k < 6; k++) {
					int x = cx + d.rnd.nextInt(5) - 2, z = cz + d.rnd.nextInt(5) - 2;
					if (Math.sqrt(x * x + z * z) >= 18.5 && Math.sqrt(x * x + z * z) < R - 1.5) d.set(x, 0, z, k % 2 == 0 ? bricks : prismarine);
				}
			} else {
				d.set(cx, 8, cz, lantern);
			}
		}
		// coral reefs and kelp between the pillars
		for (int i = 0; i < 24; i++) {
			double a = i * Math.PI / 12;
			int x = (int) Math.round(Math.cos(a) * 21.5), z = (int) Math.round(Math.sin(a) * 21.5);
			if ((Math.abs(x) <= 4 && z < 0) || (Math.abs(x) <= 5 && z > 0)) continue;
			if (i % 2 == 0) {
				int h = 4 + d.rnd.nextInt(8);
				for (int y = 0; y < h; y++) d.set(x, y, z, Blocks.KELP_PLANT.defaultBlockState());
				d.set(x, h, z, Blocks.KELP.defaultBlockState());
			} else {
				Block cb = blocks[d.rnd.nextInt(blocks.length)];
				d.set(x, 0, z, cb.defaultBlockState());
				d.set(x, 1, z, plants[d.rnd.nextInt(plants.length)].defaultBlockState());
			}
		}
		// lanterns in the wall
		for (int i = 0; i < 24; i++) {
			double a = i * Math.PI / 12 + Math.PI / 24;
			int x = (int) Math.round(Math.cos(a) * (R - 1)), z = (int) Math.round(Math.sin(a) * (R - 1));
			if (Math.abs(x) <= 4) continue;
			d.set(x, 5, z, lantern);
			d.set(x, 12, z, coral);
		}
		// the hall is a sunken colonnade open to the sea above
		for (int z = -GATE + 1; z <= -R - 2; z++) {
			for (int x = -4; x <= 4; x++) {
				d.set(x, 9, z, water);
				d.set(x, 10, z, water);
			}
			if (Math.floorMod(z, 4) == 0) {
				for (int sx : new int[]{-1, 1}) {
					int h = Math.floorMod(z, 12) == 0 ? 6 : 11;
					for (int y = 0; y <= h; y++) d.set(sx * 4, y, z, y == h ? dark : bricks);
				}
			}
		}
		// the portico and two beacon pillars rising to the surface
		for (int x = -8; x <= 8; x++) d.set(x, 14, -GATE - 1, dark);
		for (int x = -6; x <= 6; x++) d.set(x, 15, -GATE - 1, Math.abs(x) <= 3 ? dark : water);
		d.set(0, 16, -GATE - 1, lantern);
		int surface = Ocean.SEA_LEVEL - 1 - d.o.getY();
		for (int sx : new int[]{-1, 1}) {
			d.foundation(sx * 10, -1, -GATE - 4);
			for (int y = 0; y <= surface; y++) d.set(sx * 10, y, -GATE - 4, y % 6 == 5 || y == surface ? lantern : (y % 2 == 0 ? bricks : prismarine));
		}
		for (int x = -4; x <= 4; x++) d.set(x, -1, R + 5, dark);
	}

	/**
	 * The Leviathan's temple lies at the bottom of a trench cut into the sea floor: every solid block over the lair's
	 * footprint, from the temple floor up to the sea floor, becomes sea. The uncut rock around it makes the trench walls.
	 */
	private static void cutTrench(Draw d) {
		int minZ = -GATE - 14, maxZ = R + 14, half = R + 8;
		for (int x = -half; x <= half; x++) {
			for (int z = minZ; z <= maxZ; z++) {
				int top = Ocean.floor(d.level, d.o.getX() + x, d.o.getZ() + z) - d.o.getY();
				for (int y = 0; y <= top; y++) {
					BlockState s = d.get(x, y, z);
					if (!s.getFluidState().isEmpty() && s.getBlock() == Blocks.WATER) continue;
					d.set(x, y, z, d.fluid);
				}
			}
		}
	}

	// ---------------------------------------------------------------- Heart of the Terrain: the cavern of living rock
	private static void cavern(Draw d) {
		Theme th = d.th;
		BlockState rock = mb("living_rock");
		BlockState flesh = mb("flesh_stone");
		BlockState vein = mb("pulse_vein");
		BlockState ore = mb("terrain_ore");
		// the wall swells inward in knots of rock and flesh (never into the fight space)
		for (int x = -R; x <= R; x++) {
			for (int z = -R; z <= R; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist >= R - 1.5 || dist < 18.5) continue;
				if (Math.abs(x) <= 4 && z < 0) continue;
				if (Math.abs(x) <= 5 && z > 0) continue;
				double a = Math.atan2(z, x);
				int ceil = ceilAt(th, dist);
				for (int y = 0; y < ceil; y++) {
					double bump = 2 + 2 * Math.sin(a * 5 + y * 0.4) * Math.cos(a * 3 - y * 0.25);
					if (dist > R - 1.5 - bump) d.set(x, y, z, d.r() < 0.25 ? flesh : d.r() < 0.03 ? ore : rock);
				}
			}
		}
		// veins: eight meandering channels on the floor, all running to the heart, and up the walls
		for (int k = 0; k < 8; k++) {
			double base = k * Math.PI / 4 + 0.2;
			for (double r = 2; r <= R - 1; r += 0.35) {
				double a = base + 0.22 * Math.sin(r * 0.45 + k);
				int x = (int) Math.round(Math.cos(a) * r), z = (int) Math.round(Math.sin(a) * r);
				d.set(x, -1, z, vein);
			}
			double wa = base + Math.PI / 8;
			for (int y = 0; y <= 18; y++) {
				double a = wa + 0.08 * Math.sin(y * 0.6);
				int x = (int) Math.round(Math.cos(a) * (R - 1)), z = (int) Math.round(Math.sin(a) * (R - 1));
				if (Math.abs(x) <= 5) continue;
				d.set(x, y, z, vein);
			}
		}
		for (int x = -4; x <= 4; x++)
			for (int z = -4; z <= 4; z++) {
				double dist = Math.sqrt(x * x + z * z);
				if (dist <= 4.5) d.set(x, -1, z, Math.abs(dist - 3) < 0.5 ? vein : flesh);
			}
		// stalactites (kept above the headroom) and stalagmites by the wall
		for (int i = 0; i < 22; i++) {
			double a = d.r() * Math.PI * 2, dist = d.r() * 21;
			int x = (int) Math.round(Math.cos(a) * dist), z = (int) Math.round(Math.sin(a) * dist);
			int ceil = ceilAt(th, dist);
			int len = 2 + d.rnd.nextInt(5);
			for (int j = 0; j < len && ceil - 1 - j >= 15; j++) {
				d.set(x, ceil - 1 - j, z, j == len - 1 ? flesh : rock);
				if (j < len / 2) {
					d.set(x + 1, ceil - 1 - j, z, rock);
					d.set(x, ceil - 1 - j, z + 1, rock);
				}
			}
		}
		for (int i = 0; i < 14; i++) {
			double a = i * Math.PI * 2 / 14 + 0.1;
			int x = (int) Math.round(Math.cos(a) * 19.5), z = (int) Math.round(Math.sin(a) * 19.5);
			if ((Math.abs(x) <= 4 && z < 0) || (Math.abs(x) <= 5 && z > 0)) continue;
			int h = 2 + d.rnd.nextInt(5);
			for (int y = 0; y < h; y++) d.set(x, y, z, y == h - 1 ? vein : rock);
		}
		// the hall is a rough throat; the gate a maw with fleshy teeth
		for (int z = -GATE + 1; z <= -R; z++) {
			for (int x = -4; x <= 4; x++) {
				double n = Math.sin(z * 0.5 + x) * Math.cos(z * 0.3);
				if (Math.abs(x) == 4 && n > 0.3) d.set(x, 0, z, rock);
				if (Math.abs(x) >= 3 && n > 0.5) d.set(x, 8, z, flesh);
			}
			if (Math.floorMod(z, 3) == 0) d.set(0, -1, z, vein);
		}
		for (int x = -3; x <= 3; x++) {
			int len = 1 + Math.floorMod(x * 7, 3);
			for (int j = 0; j < len; j++) d.set(x, 7 - j, -GATE - 1, flesh);
		}
		for (int x = -8; x <= 8; x++)
			for (int y = 0; y <= 13; y++) if (d.get(x, y, -GATE - 1).isSolid() && d.r() < 0.3) d.set(x, y, -GATE - 1, d.r() < 0.4 ? vein : flesh);
		for (int x = -4; x <= 4; x++) d.set(x, -1, R + 5, flesh);
	}

	// ================================================================ the heart
	private static int state(DataBlockEntity be) {
		return be.data().getIntOr("state", ARMED);
	}

	private static void setState(DataBlockEntity be, int s, long until) {
		be.data().putInt("state", s);
		be.data().putLong("until", until);
		be.setChanged();
	}

	/** Lair heart ticker: wake the boss, keep track of it, re-arm ten minutes after its death. */
	public static void tick(ServerLevel level, BlockPos pos, DataBlockEntity be) {
		long now = level.getGameTime();
		int world = Worlds.number(level);
		Defs.BossDef boss = ModContent.bossForWorld(world);
		int st = state(be);
		long until = be.data().getLongOr("until", 0L);
		if (st == WAKING) {
			awakening(level, pos, world, (int) (AWAKEN_TICKS - (until - now)));
			if (now >= until) summon(level, pos, boss, be);
			return;
		}
		if (Math.floorMod(now + pos.hashCode(), 10) != 0) return;
		List<ServerPlayer> close = level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(WAKE_RADIUS),
			p -> !p.isSpectator() && p.isAlive() && p.distanceToSqr(Vec3.atCenterOf(pos)) <= WAKE_RADIUS * WAKE_RADIUS);
		switch (st) {
			case ARMED -> {
				ambient(level, pos, world, now);
				if (close.isEmpty()) return;
				if (!level.getEntitiesOfClass(MatrioBoss.class, new AABB(pos).inflate(64)).isEmpty()) return;
				setState(be, WAKING, now + AWAKEN_TICKS);
				Component line = (boss.lair() ? Component.translatable("message.matriochka.lair.wake." + boss.id())
					: Component.translatable("message.matriochka.lair.wake", Component.translatable("entity.matriochka." + boss.id()))).withStyle(ChatFormatting.DARK_RED);
				for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(64))) p.sendSystemMessage(line);
				level.playSound(null, pos, SoundEvents.WARDEN_EMERGE, SoundSource.HOSTILE, 2f, 0.7f);
			}
			case AWAKE -> {
				String id = be.data().getStringOr("boss", "");
				boolean alive = false;
				try {
					var e = id.isEmpty() ? null : level.getEntity(UUID.fromString(id));
					alive = e instanceof MatrioBoss b && b.isAlive();
				} catch (IllegalArgumentException ignored) {
					// a damaged id counts as a lost boss
				}
				if (alive) {
					be.data().putInt("lost", 0);
					return;
				}
				// the boss left without dying (unloaded, removed): re-arm after 30 s without it
				int lost = be.data().getIntOr("lost", 0) + 1;
				be.data().putInt("lost", lost);
				be.setChanged();
				if (lost >= 60 && level.getEntitiesOfClass(MatrioBoss.class, new AABB(pos).inflate(96)).isEmpty()) setState(be, ARMED, 0);
			}
			case BEATEN -> {
				if (now >= until) {
					// never wall someone in: wait until the alcove is empty
					AABB alcove = new AABB(Vec3.atLowerCornerOf(pos.offset(-6, 0, R - 2)), Vec3.atLowerCornerOf(pos.offset(7, 9, R + 11)));
					if (!level.getEntitiesOfClass(ServerPlayer.class, alcove).isEmpty()) return;
					setState(be, ARMED, 0);
					reseal(level, pos, world);
					level.playSound(null, pos, SoundEvents.WARDEN_HEARTBEAT, SoundSource.HOSTILE, 2f, 0.6f);
					for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(48))) {
						p.sendOverlayMessage(Component.translatable("message.matriochka.lair.rearmed").withStyle(ChatFormatting.DARK_RED));
					}
				} else if (!close.isEmpty()) {
					long min = Math.max(1, (until - now + 1199) / 1200);
					for (ServerPlayer p : close) p.sendOverlayMessage(Component.translatable("message.matriochka.lair.quiet", min).withStyle(ChatFormatting.GRAY));
				}
			}
			default -> {}
		}
	}

	private static ParticleOptions worldParticle(int world) {
		return switch (world) {
			case 1 -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case 2 -> ParticleTypes.LAVA;
			case 5 -> ParticleTypes.SCULK_SOUL;
			case 6 -> ParticleTypes.REVERSE_PORTAL;
			case 7 -> ParticleTypes.BUBBLE_COLUMN_UP;
			default -> ParticleTypes.DUST_PLUME;
		};
	}

	/** The short awakening: the ground shakes, the world's particles rise and a growl builds. */
	private static void awakening(ServerLevel level, BlockPos pos, int world, int t) {
		RandomSource rnd = level.getRandom();
		double cx = pos.getX() + 0.5, cy = pos.getY() + 1, cz = pos.getZ() + 0.5;
		BlockState floor = level.getBlockState(pos.offset(3, -1, 0));
		if (floor.isAir() || !floor.getFluidState().isEmpty()) floor = Arenas.floorFor(world);
		for (int i = 0; i < 10; i++) {
			double a = rnd.nextDouble() * Math.PI * 2, r = 2 + rnd.nextDouble() * 16;
			level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, floor), cx + Math.cos(a) * r, cy - 0.9, cz + Math.sin(a) * r, 3, 0.3, 0.1, 0.3, 0.1);
		}
		level.sendParticles(worldParticle(world), cx, cy + 1, cz, 8, 1.5, 1.5, 1.5, 0.02);
		int color = Content.WORLDS.get(Math.max(1, world) - 1).accent();
		level.sendParticles(new DustParticleOptions(color, 2f), cx, cy + t / 10.0, cz, 6, 0.6, 0.4, 0.6, 0);
		if (t % 5 == 0) {
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(32))) {
				if (p.isSpectator() || !p.onGround()) continue;
				p.push((rnd.nextDouble() - 0.5) * 0.3, 0.12, (rnd.nextDouble() - 0.5) * 0.3);
			}
			level.playSound(null, pos, SoundEvents.DEEPSLATE_BREAK, SoundSource.BLOCKS, 1.5f, 0.5f + rnd.nextFloat() * 0.3f);
		}
		if (t % 20 == 0) level.playSound(null, pos, SoundEvents.WARDEN_HEARTBEAT, SoundSource.HOSTILE, 2f, 0.6f + t / 120f);
		if (t == 40) level.playSound(null, pos, SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 2f, 0.6f);
	}

	private static void summon(ServerLevel level, BlockPos pos, Defs.BossDef boss, DataBlockEntity be) {
		ServerPlayer target = null;
		double best = Double.MAX_VALUE;
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(48), p -> !p.isSpectator() && p.isAlive())) {
			double dd = p.distanceToSqr(Vec3.atCenterOf(pos));
			if (dd < best) {
				best = dd;
				target = p;
			}
		}
		BlockPos at = boss.aquatic() || boss.flying() ? pos.above(5) : pos.offset(0, 0, 6);
		MatrioBoss b = MatrioBoss.summon(level, boss.id(), at, target);
		level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 1, 0, 0, 0, 0);
		if (b == null) {
			setState(be, ARMED, 0);
			return;
		}
		b.addTag(TAG + pos.asLong());
		be.data().putString("boss", b.getUUID().toString());
		be.data().putInt("lost", 0);
		setState(be, AWAKE, 0);
	}

	/** Called when a boss dies: if it came from a lair heart, open the alcove and fill its chests. */
	public static void onBossDeath(ServerLevel level, MatrioBoss boss) {
		for (String tag : boss.entityTags()) {
			if (!tag.startsWith(TAG)) continue;
			BlockPos pos;
			try {
				pos = BlockPos.of(Long.parseLong(tag.substring(TAG.length())));
			} catch (NumberFormatException e) {
				return;
			}
			if (!(level.getBlockEntity(pos) instanceof DataBlockEntity be)) return;
			setState(be, BEATEN, level.getGameTime() + REARM_TICKS);
			int world = Worlds.number(level);
			openAlcove(level, pos, world);
			level.playSound(null, pos.offset(0, 2, R), SoundEvents.VAULT_OPEN_SHUTTER, SoundSource.BLOCKS, 2f, 0.6f);
			level.playSound(null, pos.offset(0, 2, R), SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 2f, 0.5f);
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(64))) {
				p.sendSystemMessage(Component.translatable("message.matriochka.lair.treasure").withStyle(ChatFormatting.GOLD));
			}
			return;
		}
	}

	/** Re-arms the heart of a lair now (testing command). */
	public static boolean rearm(ServerLevel level, BlockPos pos) {
		if (!(level.getBlockEntity(pos) instanceof DataBlockEntity be) || !level.getBlockState(pos).is(ModContent.block("lair_heart"))) return false;
		setState(be, ARMED, 0);
		reseal(level, pos, Worlds.number(level));
		return true;
	}

	private static void openAlcove(ServerLevel level, BlockPos heart, int world) {
		BlockState open = world == 7 ? Blocks.WATER.defaultBlockState() : Blocks.AIR.defaultBlockState();
		BlockState seal = mb("sealed_brick");
		for (int x = -3; x <= 3; x++)
			for (int y = 0; y <= 5; y++)
				for (int z = R - 1; z <= R; z++) {
					BlockPos p = heart.offset(x, y, z);
					if (level.getBlockState(p).is(seal.getBlock())) {
						level.setBlock(p, open, 3);
						if ((x + y) % 2 == 0) level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, seal), p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.1);
					}
				}
		fillTreasure(level, heart, world);
	}

	private static void reseal(ServerLevel level, BlockPos heart, int world) {
		BlockState seal = mb("sealed_brick");
		for (int x = -3; x <= 3; x++)
			for (int y = 0; y <= 5; y++)
				for (int z = R - 1; z <= R; z++) {
					BlockPos p = heart.offset(x, y, z);
					BlockState s = level.getBlockState(p);
					if (s.isAir() || !s.getFluidState().isEmpty()) level.setBlock(p, seal, 3);
				}
	}

	/** Three chests at the back of the alcove: the world's rarest materials, a piece of its gear, and riches. */
	private static void fillTreasure(ServerLevel level, BlockPos heart, int world) {
		RandomSource r = level.getRandom();
		List<Defs.ItemDef> mats = Content.ITEMS.stream().filter(i -> i.world() == world
			&& List.of("resource", "gem", "ingot", "dust").contains(i.kind()) && !i.rarity().equals("common")).toList();
		List<Defs.ItemDef> gear = Content.ITEMS.stream().filter(i -> i.world() == world && (i.kind().equals("weapon") || i.kind().equals("armor"))).toList();
		List<Defs.ItemDef> cons = Content.ITEMS.stream().filter(i -> i.world() == world && (i.kind().equals("consumable") || i.kind().equals("food"))).toList();
		for (int c = 0; c < 3; c++) {
			BlockPos p = heart.offset(-2 + c * 2, 1, R + 8);
			level.setBlock(p, Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, Direction.NORTH).setValue(ChestBlock.WATERLOGGED, world == 7), 3);
			if (!(level.getBlockEntity(p) instanceof ChestBlockEntity chest)) continue;
			switch (c) {
				case 0 -> {
					for (int i = 0; i < 5 && !mats.isEmpty(); i++) {
						Defs.ItemDef d = mats.get(r.nextInt(mats.size()));
						put(chest, r, new ItemStack(ModContent.item(d.id()), d.rarity().equals("rare") ? 3 + r.nextInt(5) : 1 + r.nextInt(3)));
					}
				}
				case 1 -> {
					if (!gear.isEmpty()) put(chest, r, new ItemStack(ModContent.item(gear.get(r.nextInt(gear.size())).id())));
					for (int i = 0; i < 3 && !cons.isEmpty(); i++) put(chest, r, new ItemStack(ModContent.item(cons.get(r.nextInt(cons.size())).id()), 2 + r.nextInt(3)));
					put(chest, r, new ItemStack(ModContent.item("return_thread"), 2));
					if (r.nextBoolean()) put(chest, r, new ItemStack(ModContent.item("chance_doll")));
				}
				default -> {
					put(chest, r, new ItemStack(Items.GOLD_INGOT, 4 + r.nextInt(7)));
					put(chest, r, new ItemStack(Items.EMERALD, 2 + r.nextInt(5)));
					put(chest, r, new ItemStack(Items.EXPERIENCE_BOTTLE, 4 + r.nextInt(5)));
					if (world >= 5) put(chest, r, new ItemStack(Items.DIAMOND, 1 + r.nextInt(3)));
					if (!mats.isEmpty()) put(chest, r, new ItemStack(ModContent.item(mats.get(r.nextInt(mats.size())).id()), 2 + r.nextInt(3)));
				}
			}
			chest.setChanged();
		}
	}

	private static void put(ChestBlockEntity chest, RandomSource r, ItemStack s) {
		for (int tries = 0; tries < 27; tries++) {
			int slot = r.nextInt(27);
			if (chest.getItem(slot).isEmpty()) {
				chest.setItem(slot, s);
				return;
			}
		}
	}

	/** Small signs of life around an armed heart, for whoever is near. */
	private static void ambient(ServerLevel level, BlockPos pos, int world, long now) {
		if (level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(40), p -> !p.isSpectator()).isEmpty()) return;
		double cx = pos.getX() + 0.5, cy = pos.getY() + 1, cz = pos.getZ() + 0.5;
		level.sendParticles(worldParticle(world), cx, cy, cz, 3, 0.4, 0.4, 0.4, 0.01);
		if (world == 9 && now % 40 < 10) {
			// the veins beat: a pulse runs outward along the floor
			level.playSound(null, pos, SoundEvents.WARDEN_HEARTBEAT, SoundSource.AMBIENT, 1.2f, 0.5f);
			DustParticleOptions dust = new DustParticleOptions(Content.WORLDS.get(8).accent(), 1.8f);
			for (int k = 0; k < 8; k++) {
				double base = k * Math.PI / 4 + 0.2;
				for (double r = 2; r <= R - 2; r += 1.5) {
					double a = base + 0.22 * Math.sin(r * 0.45 + k);
					level.sendParticles(dust, cx + Math.cos(a) * r, cy - 0.8, cz + Math.sin(a) * r, 1, 0, 0.05, 0, 0);
				}
			}
		}
	}
}
