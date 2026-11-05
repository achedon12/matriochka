package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * World 3: every five minutes the halls rearrange. Around each player the dungeon is cut into 8 x 8 hall sections
 * (16 blocks tall, around the player's height); a handful of them, 16 to 40 blocks away, swap places or turn on
 * themselves, so passages open and close. Ten seconds before, dust falls from the sections about to move.
 * <p>
 * A section never moves when it holds a player (or sits next to one), a boss, a block entity (chests, stations, the
 * Jailer's Table), an unbreakable block (sealed bricks and doors, altars, the Threshold), a fluid, a block a player
 * placed, or any part of a structure: rooms, locks and their keys stay where they are, only the halls between them
 * move. Creatures inside a moving section travel with it. Work is spread over the ticks, two moves per tick.
 */
public final class DungeonShift {
	private DungeonShift() {}

	public static final long PERIOD = 20 * 300;
	public static final long WARN = 20 * 10;
	public static final int SIZE = 8;
	public static final int HEIGHT = 16;
	/** How many sections below the player's feet a section starts. */
	private static final int BELOW = 5;
	/** Ring of sections around the player that may move (in sections, Chebyshev distance). */
	private static final int RING_MIN = 2, RING_MAX = 5;
	private static final int SWAPS = 4, TURNS = 2;
	private static final int MOVES_PER_TICK = 2;
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE | Block.UPDATE_SUPPRESS_DROPS;

	/** One move: section a swaps with section b (or turns in place when b is null), each turned by its rotation. */
	public record Move(BlockPos a, BlockPos b, Rotation rot) {
		public boolean isTurn() {
			return b == null;
		}
	}

	private static final Map<ResourceKey<Level>, List<Move>> PLANNED = new HashMap<>();
	private static final Map<ResourceKey<Level>, ArrayDeque<Move>> QUEUE = new HashMap<>();
	/** Game time of the last planning in each level, so a shift only plans on its own when the warning was missed. */
	private static final Map<ResourceKey<Level>, Long> PLANNED_AT = new HashMap<>();

	public static BoundingBox box(BlockPos origin) {
		return new BoundingBox(origin.getX(), origin.getY(), origin.getZ(), origin.getX() + SIZE - 1, origin.getY() + HEIGHT - 1, origin.getZ() + SIZE - 1);
	}

	// ---------------------------------------------------------------- planning

	/** Picks the sections that will move around this player (ten seconds before the shift). */
	public static List<Move> plan(ServerLevel level, ServerPlayer p) {
		List<Move> planned = PLANNED.computeIfAbsent(level.dimension(), k -> new ArrayList<>());
		Set<Long> used = new HashSet<>();
		for (Move m : planned) {
			used.add(column(m.a));
			if (m.b != null) used.add(column(m.b));
		}
		RandomSource rnd = level.getRandom();
		int sx = Math.floorDiv(p.getBlockX(), SIZE), sz = Math.floorDiv(p.getBlockZ(), SIZE);
		int y0 = Math.max(level.getMinY() + 1, Math.min(level.getMaxY() - HEIGHT, p.getBlockY() - BELOW));
		List<BlockPos> pool = new ArrayList<>();
		for (int dx = -RING_MAX; dx <= RING_MAX; dx++) {
			for (int dz = -RING_MAX; dz <= RING_MAX; dz++) {
				if (Math.max(Math.abs(dx), Math.abs(dz)) < RING_MIN) continue;
				BlockPos o = new BlockPos((sx + dx) * SIZE, y0, (sz + dz) * SIZE);
				if (used.contains(column(o))) continue;
				pool.add(o);
			}
		}
		net.minecraft.util.Util.shuffle(pool, rnd);
		List<BlockPos> ok = new ArrayList<>();
		for (BlockPos o : pool) {
			if (ok.size() >= SWAPS * 2 + TURNS) break;
			if (movable(level, o, true)) ok.add(o);
		}
		List<Move> mine = new ArrayList<>();
		int i = 0;
		for (; i + 1 < ok.size() && mine.size() < SWAPS; i += 2) {
			mine.add(new Move(ok.get(i), ok.get(i + 1), Rotation.values()[rnd.nextInt(4)]));
		}
		for (; i < ok.size() && mine.size() < SWAPS + TURNS; i++) {
			mine.add(new Move(ok.get(i), null, rnd.nextBoolean() ? Rotation.CLOCKWISE_90 : Rotation.COUNTERCLOCKWISE_90));
		}
		planned.addAll(mine);
		PLANNED_AT.put(level.dimension(), level.getGameTime());
		return mine;
	}

	private static long column(BlockPos o) {
		return BlockPos.asLong(o.getX(), 0, o.getZ());
	}

	/** Whether a section may move right now. The first check (at planning) also wants a hall: some air, some wall. */
	public static boolean movable(ServerLevel level, BlockPos o, boolean wantHall) {
		BoundingBox box = box(o);
		if (box.minY() <= level.getMinY() || box.maxY() >= level.getMaxY()) return false;
		LevelChunk chunk = level.getChunkSource().getChunkNow(SectionPos.blockToSectionCoord(o.getX()), SectionPos.blockToSectionCoord(o.getZ()));
		if (chunk == null) return false;
		BlockPos c = Worlds.parcelCenter(Worlds.parcelOf(o));
		if (Math.abs(o.getX() - c.getX()) < 32 && Math.abs(o.getZ() - c.getZ()) < 32) return false;
		if (MatrioBoss.inArena(level, o) || MatrioBoss.inArena(level, o.offset(0, 0, SIZE - 1))) return false;
		AABB area = AABB.of(box);
		for (Player pl : level.players()) if (area.inflate(6).contains(pl.position())) return false;
		if (!level.getEntitiesOfClass(MatrioBoss.class, area.inflate(4)).isEmpty()) return false;
		for (BlockPos be : chunk.getBlockEntitiesPos()) if (box.isInside(be)) return false;
		int air = 0, total = SIZE * SIZE * HEIGHT;
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		for (int x = 0; x < SIZE; x++) {
			for (int z = 0; z < SIZE; z++) {
				for (int y = 0; y < HEIGHT; y++) {
					q.set(o.getX() + x, o.getY() + y, o.getZ() + z);
					BlockState s = chunk.getBlockState(q);
					if (s.isAir()) {
						air++;
						continue;
					}
					if (!s.getFluidState().isEmpty() || s.getDestroySpeed(level, q) < 0 || s.is(ModContent.block("sealed_door"))) return false;
				}
			}
		}
		if (wantHall && (air < total / 8 || air > total * 7 / 8)) return false;
		if (inStructure(level, box)) return false;
		return !PlacedBlocks.anyIn(level, box);
	}

	private static boolean inStructure(ServerLevel level, BoundingBox box) {
		var refs = level.structureManager().getAllStructuresAt(new BlockPos(box.minX(), box.minY(), box.minZ()));
		boolean[] hit = {false};
		for (var e : refs.entrySet()) {
			level.structureManager().fillStartsForStructure(e.getKey(), e.getValue(), start -> {
				if (start.getBoundingBox().intersects(box)) hit[0] = true;
			});
			if (hit[0]) return true;
		}
		return false;
	}

	// ---------------------------------------------------------------- warning and shift

	/** During the warning: dust falls from the planned sections and the walls grind. */
	public static void rumble(ServerLevel level, ServerPlayer p) {
		List<Move> planned = PLANNED.get(level.dimension());
		if (planned == null) return;
		var dust = new BlockParticleOption(ParticleTypes.FALLING_DUST, ModContent.block("dungeon_brick").defaultBlockState());
		for (Move m : planned) {
			for (BlockPos o : m.b == null ? new BlockPos[]{m.a} : new BlockPos[]{m.a, m.b}) {
				if (o.distSqr(p.blockPosition()) > 48 * 48) continue;
				level.sendParticles(p, dust, false, false, o.getX() + SIZE / 2.0, o.getY() + HEIGHT - 1, o.getZ() + SIZE / 2.0, 12, SIZE / 3.0, 0.5, SIZE / 3.0, 0);
			}
		}
		level.playSound(null, p.blockPosition(), SoundEvents.GRINDSTONE_USE, SoundSource.AMBIENT, 0.5f, 0.4f);
	}

	/** The shift itself: queues the planned moves (planning now if the warning was missed, after a restart). */
	public static void shift(ServerLevel level, ServerPlayer p) {
		List<Move> planned = PLANNED.computeIfAbsent(level.dimension(), k -> new ArrayList<>());
		if (planned.isEmpty() && level.getGameTime() - PLANNED_AT.getOrDefault(level.dimension(), Long.MIN_VALUE / 2) > WARN * 2) plan(level, p);
		if (planned.isEmpty()) return;
		QUEUE.computeIfAbsent(level.dimension(), k -> new ArrayDeque<>()).addAll(planned);
		planned.clear();
	}

	/** Plans and performs a full shift around this player at once (tests, admin). Returns the moves made. */
	public static List<Move> shiftNow(ServerLevel level, ServerPlayer p) {
		List<Move> moves = plan(level, p);
		List<Move> done = new ArrayList<>();
		for (Move m : moves) if (perform(level, m)) done.add(m);
		PLANNED.getOrDefault(level.dimension(), new ArrayList<>()).removeAll(moves);
		settle(level, done);
		return done;
	}

	/** Every tick: performs a few queued moves. */
	public static void tick(MinecraftServer server) {
		for (var e : QUEUE.entrySet()) {
			ArrayDeque<Move> q = e.getValue();
			if (q.isEmpty()) continue;
			ServerLevel level = server.getLevel(e.getKey());
			if (level == null) {
				q.clear();
				continue;
			}
			List<Move> done = new ArrayList<>();
			for (int i = 0; i < MOVES_PER_TICK && !q.isEmpty(); i++) {
				Move m = q.poll();
				if (perform(level, m)) done.add(m);
			}
			settle(level, done);
		}
	}

	/** Moves one pair (or turns one section) if both are still free to move. */
	public static boolean perform(ServerLevel level, Move m) {
		if (!movable(level, m.a, false) || (m.b != null && !movable(level, m.b, false))) return false;
		BlockState[] a = read(level, m.a);
		List<Entity> ea = riders(level, m.a);
		if (m.b == null) {
			write(level, m.a, a, m.rot);
			carry(ea, m.a, m.a, m.rot);
		} else {
			BlockState[] b = read(level, m.b);
			List<Entity> eb = riders(level, m.b);
			write(level, m.b, a, m.rot);
			write(level, m.a, b, m.rot);
			carry(ea, m.a, m.b, m.rot);
			carry(eb, m.b, m.a, m.rot);
		}
		return true;
	}

	private static int idx(int x, int y, int z) {
		return (y * SIZE + z) * SIZE + x;
	}

	private static BlockState[] read(ServerLevel level, BlockPos o) {
		BlockState[] out = new BlockState[SIZE * SIZE * HEIGHT];
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		for (int y = 0; y < HEIGHT; y++)
			for (int z = 0; z < SIZE; z++)
				for (int x = 0; x < SIZE; x++) out[idx(x, y, z)] = level.getBlockState(q.set(o.getX() + x, o.getY() + y, o.getZ() + z));
		return out;
	}

	/** Local (x, z) of a section turned by the rotation about its center. */
	private static int[] turn(int x, int z, Rotation r) {
		int n = SIZE - 1;
		return switch (r) {
			case CLOCKWISE_90 -> new int[]{n - z, x};
			case CLOCKWISE_180 -> new int[]{n - x, n - z};
			case COUNTERCLOCKWISE_90 -> new int[]{z, n - x};
			default -> new int[]{x, z};
		};
	}

	private static void write(ServerLevel level, BlockPos o, BlockState[] src, Rotation r) {
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		for (int y = 0; y < HEIGHT; y++) {
			for (int z = 0; z < SIZE; z++) {
				for (int x = 0; x < SIZE; x++) {
					int[] d = turn(x, z, r);
					BlockState s = src[idx(x, y, z)].rotate(r);
					q.set(o.getX() + d[0], o.getY() + y, o.getZ() + d[1]);
					if (level.getBlockState(q) != s) level.setBlock(q, s, FLAGS);
				}
			}
		}
	}

	private static List<Entity> riders(ServerLevel level, BlockPos o) {
		return level.getEntities((Entity) null, AABB.of(box(o)), e -> !(e instanceof Player) && !e.isPassenger());
	}

	private static void carry(List<Entity> riders, BlockPos from, BlockPos to, Rotation r) {
		for (Entity e : riders) {
			double lx = e.getX() - from.getX(), lz = e.getZ() - from.getZ();
			double nx, nz;
			switch (r) {
				case CLOCKWISE_90 -> { nx = SIZE - lz; nz = lx; }
				case CLOCKWISE_180 -> { nx = SIZE - lx; nz = SIZE - lz; }
				case COUNTERCLOCKWISE_90 -> { nx = lz; nz = SIZE - lx; }
				default -> { nx = lx; nz = lz; }
			}
			e.teleportTo(to.getX() + nx, e.getY() - from.getY() + to.getY(), to.getZ() + nz);
			e.setYRot(e.getYRot() + 90f * r.ordinal());
		}
	}

	/** After moves: nobody stays stuck in a wall, and everyone near hears the halls settle. */
	private static void settle(ServerLevel level, List<Move> done) {
		if (done.isEmpty()) return;
		for (ServerPlayer p : level.players()) {
			boolean near = false;
			for (Move m : done) {
				if (m.a.distSqr(p.blockPosition()) < 64 * 64) near = true;
			}
			if (!near) continue;
			if (!level.noCollision(p)) {
				BlockPos safe = Travel.findSafe(level, p.blockPosition());
				p.teleportTo(safe.getX() + 0.5, safe.getY(), safe.getZ() + 0.5);
			}
			p.sendOverlayMessage(Component.translatable("message.matriochka.rule.halls_moved").withStyle(ChatFormatting.AQUA));
			level.playSound(null, p.blockPosition(), SoundEvents.PISTON_EXTEND, SoundSource.AMBIENT, 0.8f, 0.5f);
		}
		for (Move m : done) {
			Vec3 c = Vec3.atCenterOf(m.a.offset(SIZE / 2, HEIGHT / 2, SIZE / 2));
			level.sendParticles(ParticleTypes.POOF, c.x, c.y, c.z, 10, SIZE / 3.0, HEIGHT / 3.0, SIZE / 3.0, 0.02);
		}
	}

	public static void clearAll() {
		PLANNED.clear();
		QUEUE.clear();
		PLANNED_AT.clear();
	}
}
