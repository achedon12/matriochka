package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.net.Net;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/**
 * The Journal's map: per player and per world (the Surface 0 and Worlds 1 to 10), the ground walked through and the
 * structures found. Kept in its own attachment beside the player state so the state synced every second stays
 * small; the client asks for one world's map at a time ({@link Net.MapRequestPayload}) and gets it in one payload.
 * <p>
 * The ground is coarse: cells of 4 x 4 chunks (64 x 64 blocks), sampled every three seconds, every cell within
 * {@link #REACH} blocks of the player. A world's tag holds an origin cell (ox, oz, the first cell walked) and the
 * cells as one int each, (dx &lt;&lt; 16) | (dz &amp; 0xFFFF) relative to it, in the order they were walked, at most
 * {@link #MAX_CELLS} (the oldest go first: a parcel is 47 x 47 cells, so a world's parcel always fits). Structures are
 * a list of {id, x, z} (the centre of the structure), at most {@link #MAX_FOUND} per world.
 * <pre>
 * atlas: { w0: {ox, oz, cells: int[], found: [{id, x, z}, ...]}, w1: {...}, ... w10: {...} }
 * </pre>
 */
public final class Atlas {
	public static final AttachmentType<CompoundTag> TYPE = AttachmentRegistry.<CompoundTag>builder()
		.persistent(CompoundTag.CODEC)
		.copyOnDeath()
		.initializer(CompoundTag::new)
		.buildAndRegister(Matriochka.id("atlas"));

	/** A cell is 4 x 4 chunks: block >> 6. */
	public static final int CELL_SHIFT = 6;
	public static final int MAX_CELLS = 2304, MAX_FOUND = 64;
	/** How far from the player the ground counts as seen, in blocks. */
	private static final int REACH = 40;
	/** The Surface's own place, which lives outside the STRUCTURES table. */
	private static final String SANCTUARY = "guardian_sanctuary";

	private static final java.util.Map<String, Long> LAST = new java.util.concurrent.ConcurrentHashMap<>();

	private Atlas() {}

	public static void init() {}

	/** The world a level is mapped as: 0 for the overworld, 1 to 10 for the worlds, -1 for anywhere else. */
	public static int mapped(Level level) {
		if (level.dimension() == Level.OVERWORLD) return 0;
		int w = Worlds.number(level);
		return w >= 1 && w <= 10 ? w : -1;
	}

	private static CompoundTag root(ServerPlayer p) {
		return p.getAttachedOrCreate(TYPE);
	}

	private static CompoundTag world(CompoundTag root, int world) {
		return root.getCompoundOrEmpty("w" + world);
	}

	/** Every few seconds (rules/WorldRules): inks the cells round the player and notes the structure they stand in. */
	public static void sample(ServerPlayer p) {
		int world = mapped(p.level());
		if (world < 0) return;
		BlockPos pos = p.blockPosition();
		CompoundTag root = root(p);
		CompoundTag w = world(root, world).copy();
		boolean changed = false;
		for (int cx = (pos.getX() - REACH) >> CELL_SHIFT; cx <= (pos.getX() + REACH) >> CELL_SHIFT; cx++)
			for (int cz = (pos.getZ() - REACH) >> CELL_SHIFT; cz <= (pos.getZ() + REACH) >> CELL_SHIFT; cz++)
				changed |= addCell(w, cx, cz);
		changed |= detect(p, (ServerLevel) p.level(), world, w);
		if (!changed) return;
		root.put("w" + world, w);
		p.setAttached(TYPE, root);
	}

	/** Adds a cell to a world's tag; false when it was already there or lies too far from the origin to pack. */
	private static boolean addCell(CompoundTag w, int cx, int cz) {
		if (!w.contains("ox")) {
			w.putInt("ox", cx);
			w.putInt("oz", cz);
		}
		int dx = cx - w.getIntOr("ox", 0), dz = cz - w.getIntOr("oz", 0);
		if (dx < Short.MIN_VALUE || dx > Short.MAX_VALUE || dz < Short.MIN_VALUE || dz > Short.MAX_VALUE) return false;
		int packed = dx << 16 | dz & 0xFFFF;
		int[] cells = w.getIntArray("cells").orElse(new int[0]);
		for (int c : cells) if (c == packed) return false;
		int keep = Math.min(cells.length, MAX_CELLS - 1);
		int[] out = new int[keep + 1];
		System.arraycopy(cells, cells.length - keep, out, 0, keep);
		out[keep] = packed;
		w.putIntArray("cells", out);
		return true;
	}

	/** Notes the mod's structures the player stands in (the Surface: the Guardian's Sanctuary). */
	private static boolean detect(ServerPlayer p, ServerLevel level, int world, CompoundTag w) {
		var reg = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
		boolean changed = false;
		if (world == 0) return note(level, reg, p.blockPosition(), SANCTUARY, w);
		for (Defs.StructureDef s : Content.STRUCTURES) if (s.world() == world) changed |= note(level, reg, p.blockPosition(), s.id(), w);
		return changed;
	}

	private static boolean note(ServerLevel level, net.minecraft.core.Registry<net.minecraft.world.level.levelgen.structure.Structure> reg, BlockPos pos, String id, CompoundTag w) {
		var holder = reg.get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(id)));
		if (holder.isEmpty()) return false;
		StructureStart start = level.structureManager().getStructureAt(pos, holder.get().value());
		if (!start.isValid()) return false;
		BlockPos c = start.getBoundingBox().getCenter();
		return found(w, id, c.getX(), c.getZ());
	}

	/** Adds a structure to a world's tag, once per place (two of a kind closer than 32 blocks are the same one). */
	private static boolean found(CompoundTag w, String id, int x, int z) {
		ListTag list = w.getListOrEmpty("found");
		for (Tag t : list) {
			if (!(t instanceof CompoundTag c)) continue;
			if (c.getStringOr("id", "").equals(id) && Math.abs(c.getIntOr("x", 0) - x) < 32 && Math.abs(c.getIntOr("z", 0) - z) < 32) return false;
		}
		if (list.size() >= MAX_FOUND) return false;
		CompoundTag c = new CompoundTag();
		c.putString("id", id);
		c.putInt("x", x);
		c.putInt("z", z);
		list.add(c);
		w.put("found", list);
		return true;
	}

	/** Marks ground and a structure by hand (the showcase, and an administrator's tools). */
	public static void mark(ServerPlayer p, int world, int blockX, int blockZ) {
		CompoundTag root = root(p);
		CompoundTag w = world(root, world).copy();
		if (addCell(w, blockX >> CELL_SHIFT, blockZ >> CELL_SHIFT)) {
			root.put("w" + world, w);
			p.setAttached(TYPE, root);
		}
	}

	public static void markFound(ServerPlayer p, int world, String id, int x, int z) {
		CompoundTag root = root(p);
		CompoundTag w = world(root, world).copy();
		if (found(w, id, x, z)) {
			root.put("w" + world, w);
			p.setAttached(TYPE, root);
		}
	}

	/** A new cycle gives the group fresh parcels: the worlds' maps are blank again, the Surface's stays. */
	public static void newCycle(ServerPlayer p) {
		CompoundTag root = root(p).copy();
		for (int w = 1; w <= Worlds.ZERO; w++) root.remove("w" + w);
		p.setAttached(TYPE, root);
	}

	/** Answers the Journal: one world's map, nothing else. */
	public static void send(ServerPlayer p, int world) {
		if (world < 0 || world > 10 || p.connection == null || !ServerPlayNetworking.canSend(p, Net.MapPayload.TYPE)) return;
		// at most one answer a second per player and world, whatever a client asks
		long now = p.level().getGameTime();
		Long last = LAST.put(p.getUUID().toString() + world, now);
		if (last != null && now - last >= 0 && now - last < 20) return;
		CompoundTag t = world(root(p), world).copy();
		t.putInt("world", world);
		ServerPlayNetworking.send(p, new Net.MapPayload(t));
	}
}
