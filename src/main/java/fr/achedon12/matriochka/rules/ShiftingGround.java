package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
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
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.AABB;

/**
 * World 9: every minute the ground heaves. Around each player up to three 16 x 16 zones (whole chunk columns, from a
 * few blocks under their lowest surface up to their highest block) rise or sink by one to three blocks, slide one or
 * two blocks sideways (what slides out of one edge comes back on the other), or close their chasms. Zones that stand
 * high tend to sink and low ones to rise, so the land shifts without drifting away.
 * <p>
 * Everything on a moving zone rides it: players, creatures, items, and the blocks players placed (which earns My Base
 * Walks). Nobody is ever left inside the ground: anyone colliding after a move is lifted to the nearest free spot. A
 * zone stays still when it holds a block entity (chests, stations), an unbreakable block, a boss, the Threshold or
 * the boss stage, when it lies within 16 blocks of a Terrain Anchor, or within 4 blocks of a player who used an Anchor
 * or wears Grip Boots. One zone moves per tick.
 */
public final class ShiftingGround {
	private ShiftingGround() {}

	public static final long PERIOD = 20 * 60;
	public static final long WARN = 20 * 3;
	private static final int ZONES_PER_PLAYER = 3;
	private static final int RADIUS = 2;
	/** Zones whose relief is taller than this are cliffs and stay put. */
	private static final int MAX_SPAN = 96;
	private static final int DEPTH = 6;
	private static final int FLAGS = Block.UPDATE_CLIENTS | Block.UPDATE_KNOWN_SHAPE | Block.UPDATE_SUPPRESS_DROPS;

	public enum Kind { RISE, SINK, SLIDE_X, SLIDE_Z, CLOSE }

	public record Shift(int cx, int cz, Kind kind, int amount) {}

	private static final Map<ResourceKey<Level>, ArrayDeque<Shift>> QUEUE = new HashMap<>();

	// ---------------------------------------------------------------- anchors

	/** Whether the zone is held still by a Terrain Anchor (radius 16) or an anchored player (radius 4). */
	public static boolean anchored(ServerLevel level, int cx, int cz) {
		int x0 = cx * 16, z0 = cz * 16;
		long now = level.getGameTime();
		for (ServerPlayer p : level.players()) {
			if (!(PlayerState.of(p).flagActive("anchor", now) || WorldRules.wearing(p, "grip_boots"))) continue;
			if (p.getX() > x0 - 4 && p.getX() < x0 + 20 && p.getZ() > z0 - 4 && p.getZ() < z0 + 20) return true;
		}
		BlockState anchor = ModContent.block("terrain_anchor").defaultBlockState();
		for (int dx = -1; dx <= 1; dx++) {
			for (int dz = -1; dz <= 1; dz++) {
				LevelChunk c = level.getChunkSource().getChunkNow(cx + dx, cz + dz);
				if (c == null) continue;
				for (BlockPos be : c.getBlockEntitiesPos()) {
					if (!c.getBlockState(be).is(anchor.getBlock())) continue;
					int ddx = Math.max(0, Math.max(x0 - be.getX(), be.getX() - (x0 + 15)));
					int ddz = Math.max(0, Math.max(z0 - be.getZ(), be.getZ() - (z0 + 15)));
					if (ddx * ddx + ddz * ddz <= 16 * 16) return true;
				}
			}
		}
		return false;
	}

	// ---------------------------------------------------------------- the zone and its span

	/** [bottom, top] of the moving slab, or null when the zone cannot move. */
	private static int[] span(ServerLevel level, LevelChunk c) {
		int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
		for (int x = 0; x < 16; x++) {
			for (int z = 0; z < 16; z++) {
				int h = c.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
				lo = Math.min(lo, h);
				hi = Math.max(hi, h);
			}
		}
		int bottom = Math.max(level.getMinY() + 4, lo - DEPTH), top = hi;
		if (top < bottom || top - bottom > MAX_SPAN || top + 4 >= level.getMaxY()) return null;
		return new int[]{bottom, top};
	}

	/** Whether the zone may move at all (ignoring anchors). */
	public static boolean movable(ServerLevel level, int cx, int cz) {
		LevelChunk c = level.getChunkSource().getChunkNow(cx, cz);
		if (c == null) return false;
		int[] s = span(level, c);
		if (s == null) return false;
		int x0 = cx * 16, z0 = cz * 16;
		BlockPos center = Worlds.parcelCenter(Worlds.parcelOf(new BlockPos(x0, 0, z0)));
		if (Math.abs(x0 + 8 - center.getX()) < 40 && Math.abs(z0 + 8 - center.getZ()) < 40) return false;
		for (int z : new int[]{z0, z0 + 15}) if (MatrioBoss.inArena(level, new BlockPos(x0, 64, z))) return false;
		for (BlockPos be : c.getBlockEntitiesPos()) if (be.getY() >= s[0] - 4 && be.getY() <= s[1] + 4) return false;
		AABB area = new AABB(x0, s[0] - 4, z0, x0 + 16, s[1] + 6, z0 + 16);
		if (!level.getEntitiesOfClass(MatrioBoss.class, area).isEmpty()) return false;
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		for (int x = 0; x < 16; x++) {
			for (int z = 0; z < 16; z++) {
				for (int y = s[0] - 3; y <= s[1]; y++) {
					BlockState st = c.getBlockState(q.set(x0 + x, y, z0 + z));
					if (!st.isAir() && st.getDestroySpeed(level, q) < 0) return false;
				}
			}
		}
		return true;
	}

	// ---------------------------------------------------------------- heave

	/** The heave around one player: picks up to three free zones and queues their shifts. Returns them. */
	public static List<Shift> heave(ServerLevel level, ServerPlayer p) {
		ArrayDeque<Shift> q = QUEUE.computeIfAbsent(level.dimension(), k -> new ArrayDeque<>());
		Set<Long> busy = new HashSet<>();
		for (Shift s : q) busy.add(ChunkPos.pack(s.cx, s.cz));
		RandomSource rnd = level.getRandom();
		int pcx = SectionPos.blockToSectionCoord(p.getBlockX()), pcz = SectionPos.blockToSectionCoord(p.getBlockZ());
		List<int[]> pool = new ArrayList<>();
		for (int dx = -RADIUS; dx <= RADIUS; dx++) for (int dz = -RADIUS; dz <= RADIUS; dz++) pool.add(new int[]{pcx + dx, pcz + dz});
		net.minecraft.util.Util.shuffle(pool, rnd);
		List<Shift> picked = new ArrayList<>();
		for (int[] z : pool) {
			if (picked.size() >= ZONES_PER_PLAYER) break;
			if (busy.contains(ChunkPos.pack(z[0], z[1])) || anchored(level, z[0], z[1]) || !movable(level, z[0], z[1])) continue;
			Shift s = choose(level, z[0], z[1], rnd);
			if (s == null) continue;
			picked.add(s);
		}
		q.addAll(picked);
		return picked;
	}

	/** What a zone does: high zones sink, low ones rise, chasms close, the rest slide or wobble. */
	static Shift choose(ServerLevel level, int cx, int cz, RandomSource rnd) {
		LevelChunk c = level.getChunkSource().getChunkNow(cx, cz);
		if (c == null) return null;
		int[] hs = heights(c);
		int[] sorted = hs.clone();
		Arrays.sort(sorted);
		int median = sorted[128];
		int deep = 0;
		for (int h : hs) if (h < median - 4) deep++;
		if (deep >= 8 && rnd.nextInt(2) == 0) return new Shift(cx, cz, Kind.CLOSE, 0);
		double mean = Arrays.stream(hs).average().orElse(median), around = 0;
		int n = 0;
		for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) {
			LevelChunk o = level.getChunkSource().getChunkNow(cx + d[0], cz + d[1]);
			if (o == null) continue;
			around += o.getHeight(Heightmap.Types.WORLD_SURFACE, 8, 8);
			n++;
		}
		int amount = 1 + rnd.nextInt(3);
		if (n > 0) {
			double diff = mean - around / n;
			if (diff > 2 && rnd.nextInt(3) > 0) return new Shift(cx, cz, Kind.SINK, amount);
			if (diff < -2 && rnd.nextInt(3) > 0) return new Shift(cx, cz, Kind.RISE, amount);
		}
		return switch (rnd.nextInt(4)) {
			case 0 -> new Shift(cx, cz, Kind.RISE, amount);
			case 1 -> new Shift(cx, cz, Kind.SINK, amount);
			case 2 -> new Shift(cx, cz, Kind.SLIDE_X, rnd.nextBoolean() ? 1 + rnd.nextInt(2) : -1 - rnd.nextInt(2));
			default -> new Shift(cx, cz, Kind.SLIDE_Z, rnd.nextBoolean() ? 1 + rnd.nextInt(2) : -1 - rnd.nextInt(2));
		};
	}

	private static int[] heights(LevelChunk c) {
		int[] hs = new int[256];
		for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) hs[x * 16 + z] = c.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
		return hs;
	}

	/** Every tick: one queued zone moves. */
	public static void tick(MinecraftServer server) {
		for (var e : QUEUE.entrySet()) {
			ArrayDeque<Shift> q = e.getValue();
			if (q.isEmpty()) continue;
			ServerLevel level = server.getLevel(e.getKey());
			if (level == null) {
				q.clear();
				continue;
			}
			perform(level, q.poll());
		}
	}

	/** Moves one zone now, if it is still free and unanchored. Returns whether it moved. */
	public static boolean perform(ServerLevel level, Shift s) {
		if (anchored(level, s.cx, s.cz) || !movable(level, s.cx, s.cz)) return false;
		LevelChunk c = level.getChunkSource().getChunkNow(s.cx, s.cz);
		int[] sp = span(level, c);
		int bottom = sp[0], top = sp[1], x0 = s.cx * 16, z0 = s.cz * 16;
		Kind kind = s.kind;
		int d = s.amount;
		// sinking would bury the lowest layers: never when a player's block sits there
		if (kind == Kind.SINK && PlacedBlocks.anyIn(level, new BoundingBox(x0, bottom - d, z0, x0 + 15, bottom - 1, z0 + 15))) kind = Kind.RISE;
		if (kind == Kind.RISE && top + d + 4 >= level.getMaxY()) return false;
		if (kind == Kind.SINK && bottom - d <= level.getMinY() + 1) return false;
		int h = top - bottom + 1;
		BlockState[] src = new BlockState[256 * h];
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		for (int x = 0; x < 16; x++)
			for (int z = 0; z < 16; z++)
				for (int y = 0; y < h; y++) src[(x * 16 + z) * h + y] = c.getBlockState(q.set(x0 + x, bottom + y, z0 + z));
		List<Entity> riders = level.getEntities((Entity) null, new AABB(x0, bottom - 1, z0, x0 + 16, top + 4, z0 + 16), e -> !e.isPassenger());
		boolean placed = PlacedBlocks.anyIn(level, new BoundingBox(x0, bottom, z0, x0 + 15, top, z0 + 15));
		int[] lift = new int[256];
		switch (kind) {
			case RISE -> {
				for (int x = 0; x < 16; x++)
					for (int z = 0; z < 16; z++) {
						int col = (x * 16 + z) * h;
						for (int y = h - 1 + d; y >= 0; y--) {
							BlockState st = y - d >= 0 ? src[col + y - d] : src[col];
							set(level, q.set(x0 + x, bottom + y, z0 + z), st);
						}
					}
			}
			case SINK -> {
				for (int x = 0; x < 16; x++)
					for (int z = 0; z < 16; z++) {
						int col = (x * 16 + z) * h;
						for (int y = -d; y < h; y++) {
							BlockState st = y + d < h ? src[col + y + d] : Blocks.AIR.defaultBlockState();
							set(level, q.set(x0 + x, bottom + y, z0 + z), st);
						}
					}
			}
			case SLIDE_X, SLIDE_Z -> {
				boolean alongX = kind == Kind.SLIDE_X;
				for (int x = 0; x < 16; x++)
					for (int z = 0; z < 16; z++) {
						int sx = alongX ? Math.floorMod(x - d, 16) : x, sz = alongX ? z : Math.floorMod(z - d, 16);
						int col = (sx * 16 + sz) * h;
						for (int y = 0; y < h; y++) set(level, q.set(x0 + x, bottom + y, z0 + z), src[col + y]);
					}
			}
			case CLOSE -> {
				int[] hs = heights(c);
				int[] sorted = hs.clone();
				Arrays.sort(sorted);
				int median = sorted[128];
				int mx = 0, mz = 0;
				for (int i = 0; i < 256; i++) if (hs[i] == median) { mx = i / 16; mz = i % 16; break; }
				BlockState fill = c.getBlockState(q.set(x0 + mx, median, z0 + mz));
				if (fill.isAir() || !fill.isSolid()) fill = ModContent.block("living_rock").defaultBlockState();
				for (int x = 0; x < 16; x++)
					for (int z = 0; z < 16; z++) {
						int ch = hs[x * 16 + z];
						if (ch >= median - 4) continue;
						for (int y = ch + 1; y <= median - 1; y++) {
							q.set(x0 + x, y, z0 + z);
							if (level.getBlockState(q).canBeReplaced()) set(level, q, fill);
						}
						lift[x * 16 + z] = median;
					}
			}
		}
		final Kind k = kind;
		BoundingBox moved = new BoundingBox(x0, bottom, z0, x0 + 15, top, z0 + 15);
		int carried = switch (k) {
			case RISE -> PlacedBlocks.remap(level, s.cx, s.cz, moved, key -> BlockPos.offset(key, 0, d, 0));
			case SINK -> PlacedBlocks.remap(level, s.cx, s.cz, moved, key -> BlockPos.offset(key, 0, -d, 0));
			case SLIDE_X, SLIDE_Z -> PlacedBlocks.remap(level, s.cx, s.cz, moved, key -> {
				int x = BlockPos.getX(key), z = BlockPos.getZ(key);
				if (k == Kind.SLIDE_X) x = x0 + Math.floorMod(x - x0 + d, 16);
				else z = z0 + Math.floorMod(z - z0 + d, 16);
				return BlockPos.asLong(x, BlockPos.getY(key), z);
			});
			case CLOSE -> 0;
		};
		carry(level, riders, k, d, x0, z0, lift);
		after(level, s, x0, z0, bottom, top, placed && carried > 0, riders);
		return true;
	}

	private static void set(ServerLevel level, BlockPos pos, BlockState st) {
		if (level.getBlockState(pos) == st) return;
		level.setBlock(pos, st, FLAGS);
		if (!st.getFluidState().isEmpty()) level.scheduleTick(pos, st.getFluidState().getType(), 4);
	}

	private static void carry(ServerLevel level, List<Entity> riders, Kind k, int d, int x0, int z0, int[] lift) {
		for (Entity e : riders) {
			double x = e.getX(), y = e.getY(), z = e.getZ();
			switch (k) {
				case RISE -> y += d;
				case SINK -> y -= d;
				case SLIDE_X -> x = x0 + Math.floorMod((int) Math.floor(x - x0) + d, 16) + (x - Math.floor(x));
				case SLIDE_Z -> z = z0 + Math.floorMod((int) Math.floor(z - z0) + d, 16) + (z - Math.floor(z));
				case CLOSE -> {
					int i = Math.floorMod((int) Math.floor(x), 16) * 16 + Math.floorMod((int) Math.floor(z), 16);
					if (lift[i] > 0 && y < lift[i]) y = lift[i];
				}
			}
			e.teleportTo(x, y, z);
		}
	}

	/** Nobody stays in the ground; riders feel it; builds that moved earn My Base Walks. */
	private static void after(ServerLevel level, Shift s, int x0, int z0, int bottom, int top, boolean buildMoved, List<Entity> riders) {
		AABB zone = new AABB(x0 - 2, bottom - 4, z0 - 2, x0 + 18, top + 8, z0 + 18);
		for (ServerPlayer p : level.players()) {
			if (zone.contains(p.position()) && !level.noCollision(p)) {
				BlockPos safe = Travel.findSafe(level, p.blockPosition());
				for (int i = 0; i < 8 && !level.noCollision(p, p.getType().getDimensions().makeBoundingBox(safe.getX() + 0.5, safe.getY(), safe.getZ() + 0.5)); i++) safe = safe.above();
				p.teleportTo(safe.getX() + 0.5, safe.getY(), safe.getZ() + 0.5);
			}
			if (riders.contains(p)) {
				p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 60, 0, true, false));
				fr.achedon12.matriochka.net.Cues.shake(p, 0.7f, 24);
				p.sendOverlayMessage(Component.translatable("message.matriochka.rule.ground_moved").withStyle(ChatFormatting.GOLD));
			}
			if (buildMoved && p.distanceToSqr(x0 + 8, p.getY(), z0 + 8) < 64 * 64) Achievements.grant(p, "base_moved");
		}
		for (Entity e : riders) {
			if (e instanceof ServerPlayer || level.noCollision(e)) continue;
			BlockPos safe = Travel.findSafe(level, e.blockPosition());
			e.teleportTo(safe.getX() + 0.5, safe.getY(), safe.getZ() + 0.5);
		}
		var dust = new BlockParticleOption(ParticleTypes.BLOCK, ModContent.block("living_rock").defaultBlockState());
		var rnd = level.getRandom();
		for (int i = 0; i < 6; i++) {
			int x = x0 + rnd.nextInt(16), z = z0 + rnd.nextInt(16);
			int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
			level.sendParticles(dust, x + 0.5, y + 0.2, z + 0.5, 12, 0.6, 0.2, 0.6, 0.1);
		}
		level.playSound(null, new BlockPos(x0 + 8, top, z0 + 8), fr.achedon12.matriochka.content.Sounds.WORLD_QUAKE, SoundSource.AMBIENT, 1.5f, 1f);
	}

	/** During the warning: the ground around the player cracks and puffs dust. */
	public static void rumble(ServerLevel level, ServerPlayer p) {
		var dust = new BlockParticleOption(ParticleTypes.BLOCK, ModContent.block("living_rock").defaultBlockState());
		var rnd = level.getRandom();
		for (int i = 0; i < 5; i++) {
			int x = p.getBlockX() + rnd.nextInt(25) - 12, z = p.getBlockZ() + rnd.nextInt(25) - 12;
			if (!level.isLoaded(new BlockPos(x, 0, z))) continue;
			int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
			level.sendParticles(p, dust, false, false, x + 0.5, y + 0.1, z + 0.5, 10, 0.8, 0.1, 0.8, 0.05);
		}
		level.playSound(null, p.blockPosition(), fr.achedon12.matriochka.content.Sounds.WORLD_RUMBLE, SoundSource.AMBIENT, 0.8f, 0.9f + level.getRandom().nextFloat() * 0.2f);
	}

	public static void clearAll() {
		QUEUE.clear();
	}
}
