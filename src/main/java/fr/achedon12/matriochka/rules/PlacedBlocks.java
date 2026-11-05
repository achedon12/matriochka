package fr.achedon12.matriochka.rules;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.world.Worlds;
import it.unimi.dsi.fastutil.longs.Long2LongMap;
import it.unimi.dsi.fastutil.longs.Long2LongOpenHashMap;
import java.util.Arrays;
import java.util.function.LongUnaryOperator;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import org.jspecify.annotations.Nullable;

/**
 * Remembers, per chunk, which blocks players placed and when. The moving worlds read it: World 3 never shifts a hall
 * holding a player's block, World 5 burns out the lights players bring, World 9 carries builds along with the ground
 * (and knows when it did). Only worlds 3, 5, 9 and 10 keep records. Entries are pruned lazily when the block is gone.
 */
public final class PlacedBlocks {
	private PlacedBlocks() {}

	/** Placement time of a light that is the moving glow of a lit Solar Lantern, not a block a player placed. */
	public static final long LANTERN = -1L;

	/** The records of one chunk: every placed block, and the light emitters among them (or lantern glows). */
	public static final class Marks {
		final Long2LongOpenHashMap placed = new Long2LongOpenHashMap();
		final Long2LongOpenHashMap lights = new Long2LongOpenHashMap();

		static Marks of(long[] placed, long[] lights) {
			Marks m = new Marks();
			for (int i = 0; i + 1 < placed.length; i += 2) m.placed.put(placed[i], placed[i + 1]);
			for (int i = 0; i + 1 < lights.length; i += 2) m.lights.put(lights[i], lights[i + 1]);
			return m;
		}

		private static long[] flat(Long2LongOpenHashMap map) {
			long[] out = new long[map.size() * 2];
			int i = 0;
			for (Long2LongMap.Entry e : map.long2LongEntrySet()) {
				out[i++] = e.getLongKey();
				out[i++] = e.getLongValue();
			}
			return out;
		}

		public boolean isEmpty() {
			return placed.isEmpty() && lights.isEmpty();
		}

		public Long2LongOpenHashMap placed() {
			return placed;
		}

		public Long2LongOpenHashMap lights() {
			return lights;
		}
	}

	private static final Codec<long[]> LONGS = Codec.LONG_STREAM.xmap(java.util.stream.LongStream::toArray, Arrays::stream);
	private static final Codec<Marks> CODEC = RecordCodecBuilder.create(i -> i.group(
		LONGS.optionalFieldOf("placed", new long[0]).forGetter(m -> Marks.flat(m.placed)),
		LONGS.optionalFieldOf("lights", new long[0]).forGetter(m -> Marks.flat(m.lights))
	).apply(i, Marks::of));

	public static final AttachmentType<Marks> TYPE = AttachmentRegistry.<Marks>builder()
		.persistent(CODEC)
		.initializer(Marks::new)
		.buildAndRegister(Matriochka.id("placed_blocks"));

	public static void init() {}

	/** Worlds whose rules care about player blocks: the halls (3), the dark (5), the ground (9) and the synthesis (10). */
	public static boolean tracked(ServerLevel level) {
		int w = Worlds.number(level);
		return w == 3 || w == 5 || w == 9 || w == 10;
	}

	/** Called after a player placed a block (from the block item mixin). */
	public static void onPlaced(ServerLevel level, BlockPos pos) {
		if (!tracked(level)) return;
		LevelChunk chunk = level.getChunkSource().getChunkNow(SectionPos.blockToSectionCoord(pos.getX()), SectionPos.blockToSectionCoord(pos.getZ()));
		if (chunk == null) return;
		Marks m = chunk.getAttachedOrCreate(TYPE);
		long now = level.getGameTime();
		BlockState state = level.getBlockState(pos);
		m.placed.put(pos.asLong(), now);
		if (Burnout.burns(state)) m.lights.put(pos.asLong(), now);
		// the other half of a two-block item (doors, tall plants) belongs to the player too
		BlockPos up = pos.above();
		if (level.getBlockState(up).is(state.getBlock())) m.placed.put(up.asLong(), now);
		chunk.markUnsaved();
	}

	/** The records of a loaded chunk, or null when it is not loaded or holds none. */
	public static @Nullable Marks marks(ServerLevel level, int cx, int cz) {
		LevelChunk chunk = level.getChunkSource().getChunkNow(cx, cz);
		if (chunk == null) return null;
		Marks m = chunk.getAttached(TYPE);
		return m == null || m.isEmpty() ? null : m;
	}

	public static void dirty(ServerLevel level, int cx, int cz) {
		LevelChunk chunk = level.getChunkSource().getChunkNow(cx, cz);
		if (chunk != null) chunk.markUnsaved();
	}

	/** Records a block as the glow of a lit Solar Lantern, so that it is cleaned up even after a restart. */
	public static void markLantern(ServerLevel level, BlockPos pos) {
		LevelChunk chunk = level.getChunkSource().getChunkNow(SectionPos.blockToSectionCoord(pos.getX()), SectionPos.blockToSectionCoord(pos.getZ()));
		if (chunk == null) return;
		chunk.getAttachedOrCreate(TYPE).lights.put(pos.asLong(), LANTERN);
		chunk.markUnsaved();
	}

	public static void forgetLight(ServerLevel level, BlockPos pos) {
		Marks m = marks(level, SectionPos.blockToSectionCoord(pos.getX()), SectionPos.blockToSectionCoord(pos.getZ()));
		if (m == null || !m.lights.containsKey(pos.asLong())) return;
		m.lights.remove(pos.asLong());
		dirty(level, SectionPos.blockToSectionCoord(pos.getX()), SectionPos.blockToSectionCoord(pos.getZ()));
	}

	/**
	 * Whether a player block (still standing) lies inside the box. Stale records of blocks since broken are dropped on
	 * the way.
	 */
	public static boolean anyIn(ServerLevel level, BoundingBox box) {
		boolean found = false;
		for (int cx = SectionPos.blockToSectionCoord(box.minX()); cx <= SectionPos.blockToSectionCoord(box.maxX()); cx++) {
			for (int cz = SectionPos.blockToSectionCoord(box.minZ()); cz <= SectionPos.blockToSectionCoord(box.maxZ()); cz++) {
				Marks m = marks(level, cx, cz);
				if (m == null) continue;
				var it = m.placed.long2LongEntrySet().iterator();
				boolean pruned = false;
				while (it.hasNext()) {
					long key = it.next().getLongKey();
					int x = BlockPos.getX(key), y = BlockPos.getY(key), z = BlockPos.getZ(key);
					if (!box.isInside(x, y, z)) continue;
					if (level.getBlockState(BlockPos.of(key)).isAir()) {
						it.remove();
						pruned = true;
						continue;
					}
					found = true;
				}
				if (pruned) dirty(level, cx, cz);
			}
		}
		return found;
	}

	/**
	 * Moves the records of one chunk whose blocks just moved: every record inside the box is remapped by the given
	 * position function (which must keep it in the same chunk). Returns how many player blocks moved.
	 */
	public static int remap(ServerLevel level, int cx, int cz, BoundingBox box, LongUnaryOperator move) {
		Marks m = marks(level, cx, cz);
		if (m == null) return 0;
		int moved = remap(m.placed, box, move);
		remap(m.lights, box, move);
		if (moved > 0) dirty(level, cx, cz);
		return moved;
	}

	private static int remap(Long2LongOpenHashMap map, BoundingBox box, LongUnaryOperator move) {
		Long2LongOpenHashMap out = new Long2LongOpenHashMap();
		var it = map.long2LongEntrySet().iterator();
		while (it.hasNext()) {
			var e = it.next();
			long key = e.getLongKey();
			if (!box.isInside(BlockPos.getX(key), BlockPos.getY(key), BlockPos.getZ(key))) continue;
			out.put(move.applyAsLong(key), e.getLongValue());
			it.remove();
		}
		map.putAll(out);
		return out.size();
	}
}
