package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FallingBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/**
 * The Maquette: in the Giant Workshop the player's own base sits as a scale model on the Titanic Workbench.
 * <p>
 * When the World 10 Seed hatches, the 64 x 32 x 64 blocks around it (8 below, 24 above) are sampled at a quarter
 * scale: every 4 x 4 x 4 cube becomes one block, the most common solid block in it (or nothing when it is mostly
 * empty). The 16 x 8 x 16 result is kept in the group's World 10 entry ("model": a palette and 2048 cells). The first
 * time someone of the group comes near the Titanic Workbench, the model is built with real blocks on the plinth at
 * the centre of its top. Blocks that cannot stand alone on a table (water, falling sand, chests...) are swapped for
 * look-alikes; the group's World Block itself shows as a gold block.
 */
public final class BaseModel {
	private BaseModel() {}

	public static final int SX = 16, SY = 8, SZ = 16, SCALE = 4;
	/** Height of the workbench top's surface above the structure origin (see structure/Workshop.workbench). */
	public static final int TOP = 16;
	public static final String STRUCTURE = "titanic_workbench";

	// ---------------------------------------------------------------- capture
	/** Samples the base around a position into the group's World 10 entry. Loads the chunks it needs. */
	public static void capture(ServerLevel level, BlockPos center, MatrioData data, String group) {
		data.worldEntry(group, 10).put("model", sample(level, center));
		data.worldEntry(group, 10).remove("model_at");
		data.changed();
	}

	public static CompoundTag sample(ServerLevel level, BlockPos center) {
		Map<String, Integer> index = new HashMap<>();
		ListTag palette = new ListTag();
		int[] cells = new int[SX * SY * SZ];
		int x0 = center.getX() - SX * SCALE / 2, y0 = center.getY() - 8, z0 = center.getZ() - SZ * SCALE / 2;
		BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
		Map<Block, Integer> count = new HashMap<>();
		for (int cx = 0; cx < SX; cx++)
			for (int cz = 0; cz < SZ; cz++) {
				level.getChunk((x0 + cx * SCALE) >> 4, (z0 + cz * SCALE) >> 4);
				for (int cy = 0; cy < SY; cy++) {
					count.clear();
					int solid = 0;
					for (int dx = 0; dx < SCALE; dx++)
						for (int dy = 0; dy < SCALE; dy++)
							for (int dz = 0; dz < SCALE; dz++) {
								q.set(x0 + cx * SCALE + dx, y0 + cy * SCALE + dy, z0 + cz * SCALE + dz);
								BlockState s = level.getBlockState(q);
								Block b = shown(s);
								if (b == null) continue;
								solid++;
								count.merge(b, 1, Integer::sum);
							}
					// a quarter full is enough to keep the walls and roofs of a base
					if (solid < 16) continue;
					Block best = null;
					int most = 0;
					for (var e : count.entrySet()) if (e.getValue() > most || (e.getValue() == most && best != null && key(e.getKey()).compareTo(key(best)) < 0)) {
						best = e.getKey();
						most = e.getValue();
					}
					String id = key(best);
					Integer i = index.get(id);
					if (i == null) {
						i = palette.size();
						index.put(id, i);
						palette.add(StringTag.valueOf(id));
					}
					cells[(cx * SZ + cz) * SY + cy] = i + 1;
				}
			}
		CompoundTag t = new CompoundTag();
		t.put("palette", palette);
		t.putIntArray("cells", cells);
		t.putString("from", level.dimension().identifier() + " " + center.toShortString());
		return t;
	}

	private static String key(Block b) {
		return BuiltInRegistries.BLOCK.getKey(b).toString();
	}

	/** The block a sampled state shows as on the model, or null when it counts as empty. */
	private static Block shown(BlockState s) {
		if (s.isAir()) return null;
		if (s.is(ModContent.block("world_block"))) return Blocks.GOLD_BLOCK;
		if (!s.getFluidState().isEmpty() && s.getFluidState().isSource()) {
			return s.getFluidState().is(net.minecraft.tags.FluidTags.LAVA) ? Blocks.STAINED_GLASS.orange() : Blocks.STAINED_GLASS.lightBlue();
		}
		if (s.getBlock() instanceof FallingBlock) {
			if (s.is(Blocks.GRAVEL)) return Blocks.COBBLESTONE;
			if (s.is(Blocks.RED_SAND)) return Blocks.RED_SANDSTONE;
			return Blocks.SANDSTONE;
		}
		if (s.hasBlockEntity()) return Blocks.SPRUCE_PLANKS;
		// plants, torches, rails, carpets... are too small to show at a quarter scale
		if (!s.isSolid() && !s.is(net.minecraft.tags.BlockTags.LEAVES) && !s.is(Blocks.GLASS)) return null;
		return s.getBlock();
	}

	/** When no capture was made (a World 10 opened before the Maquette existed), the first World Block, the bed or the world spawn. */
	public static CompoundTag fallback(ServerPlayer p, MatrioData data, String group) {
		var server = p.level().getServer();
		for (int w = 1; w <= 10; w++) {
			CompoundTag e = data.worldEntry(group, w);
			String dim = e.getStringOr("block_dim", "");
			if (dim.isEmpty()) continue;
			ServerLevel level = server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
			if (level != null) return sample(level, BlockPos.of(e.getLongOr("block_pos", 0L)));
		}
		var respawn = p.getRespawnConfig();
		if (respawn != null) {
			ServerLevel level = server.getLevel(respawn.respawnData().dimension());
			if (level != null && !Worlds.isModWorld(level)) return sample(level, respawn.respawnData().pos());
		}
		ServerLevel over = server.overworld();
		return sample(over, over.getRespawnData().pos());
	}

	// ---------------------------------------------------------------- the Titanic Workbench
	/** Checks every few seconds whether a player of a group stands at the workbench whose model is not built yet. */
	public static void tick(ServerPlayer p) {
		if (Worlds.number(p.level()) != 10 || !(p.level() instanceof ServerLevel level)) return;
		var reg = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
		var holder = reg.get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(STRUCTURE)));
		if (holder.isEmpty()) return;
		StructureStart start = level.structureManager().getStructureAt(p.blockPosition(), holder.get().value());
		if (!start.isValid() || start.getPieces().isEmpty()) return;
		MatrioData data = MatrioData.get(level.getServer());
		String group = Variants.groupAt(level, p.blockPosition());
		if (group == null) group = data.groupOf(p.getUUID());
		BlockPos origin = origin(start.getPieces().getFirst().getBoundingBox());
		CompoundTag e = data.worldEntry(group, 10);
		if (e.getLongOr("model_at", Long.MIN_VALUE) == origin.asLong()) return;
		if (!e.contains("model")) e.put("model", fallback(p, data, group));
		if (build(level, origin, e.getCompoundOrEmpty("model")) > 0) {
			p.sendSystemMessage(Component.translatable("message.matriochka.maquette"));
		}
		e.putLong("model_at", origin.asLong());
		data.changed();
	}

	/** The structure origin from its piece box, as ProceduralPiece computes it. */
	public static BlockPos origin(BoundingBox box) {
		return new BlockPos(box.getCenter().getX(), box.minY() + 14, box.getCenter().getZ());
	}

	/** The lowest north-west corner of the model on the workbench top. */
	public static BlockPos corner(BlockPos origin) {
		return origin.offset(-SX / 2, TOP, -SZ / 2);
	}

	/** Builds a captured model on the workbench; returns how many blocks it placed. */
	public static int build(ServerLevel level, BlockPos origin, CompoundTag model) {
		ListTag palette = model.getListOrEmpty("palette");
		int[] cells = model.getIntArray("cells").orElse(new int[0]);
		if (cells.length != SX * SY * SZ) return 0;
		BlockState[] states = new BlockState[palette.size()];
		for (int i = 0; i < palette.size(); i++) {
			Tag t = palette.get(i);
			Block b = BuiltInRegistries.BLOCK.getValue(Identifier.parse(t.asString().orElse("minecraft:air")));
			states[i] = b.defaultBlockState();
		}
		BlockPos c = corner(origin);
		int placed = 0;
		for (int cx = 0; cx < SX; cx++)
			for (int cz = 0; cz < SZ; cz++)
				for (int cy = 0; cy < SY; cy++) {
					int v = cells[(cx * SZ + cz) * SY + cy];
					if (v <= 0 || v > states.length) continue;
					BlockPos at = c.offset(cx, cy, cz);
					if (!level.getBlockState(at).isAir()) continue;
					level.setBlock(at, states[v - 1], Block.UPDATE_CLIENTS);
					placed++;
				}
		level.sendParticles(ParticleTypes.END_ROD, c.getX() + SX / 2.0, c.getY() + 2, c.getZ() + SZ / 2.0, 60, SX / 3.0, 2, SZ / 3.0, 0.02);
		level.playSound(null, c.offset(SX / 2, 0, SZ / 2), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.5f, 0.6f);
		return placed;
	}
}
