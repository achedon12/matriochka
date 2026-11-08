package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import org.jspecify.annotations.Nullable;

/**
 * The worlds' people know where their world's wonder stands, roughly: a direction and how far. Told once, the rumour
 * is kept in the player's state ("rumor_<w>_x/z") so the Journal's world card can point at it (client/WorldCards).
 * The search is the one /locate does, a few placement regions around the person, so it stays cheap.
 */
public final class Rumors {
	private Rumors() {}

	private static final int SEARCH_REGIONS = 3;

	/** The wonder of World w, or null. */
	public static Defs.@Nullable StructureDef wonderOf(int w) {
		for (Defs.StructureDef d : Content.STRUCTURES) if (d.world() == w && d.role().equals("wonder")) return d;
		return null;
	}

	/** Where the nearest wonder of the level stands, seen from pos, or null when none is near enough to be known. */
	public static @Nullable BlockPos locate(ServerLevel level, BlockPos pos, int w) {
		Defs.StructureDef d = wonderOf(w);
		if (d == null) return null;
		var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(d.id())));
		if (holder.isEmpty()) return null;
		var found = level.getChunkSource().getGenerator().findNearestMapStructure(level, HolderSet.direct(holder.get()), pos, SEARCH_REGIONS, false);
		return found == null ? null : found.getFirst();
	}

	/** One of the eight directions, as a lang key suffix. */
	static String direction(double dx, double dz) {
		double a = Math.toDegrees(Math.atan2(dx, -dz));
		String[] dirs = {"north", "north_east", "east", "south_east", "south", "south_west", "west", "north_west"};
		return dirs[(int) Math.floorMod(Math.round(a / 45.0), 8)];
	}

	/** "near" (under 300 blocks), "far" (under 900), "very_far". */
	static String distance(double d) {
		return d < 300 ? "near" : d < 900 ? "far" : "very_far";
	}

	/**
	 * The rumour a person of World w tells the player standing at from, or null when the wonder is out of reach or
	 * its relic already taken. Kept in the player's state.
	 */
	public static @Nullable Component tell(ServerLevel level, ServerPlayer p, BlockPos from, int w) {
		PlayerState ps = PlayerState.of(p);
		if (ps.has("relic_" + w)) return null;
		BlockPos at = locate(level, from, w);
		if (at == null) return null;
		ps.tag().putInt("rumor_" + w + "_x", at.getX());
		ps.tag().putInt("rumor_" + w + "_z", at.getZ());
		ps.set("rumor_" + w, true);
		double dx = at.getX() - from.getX(), dz = at.getZ() - from.getZ();
		return Component.translatable("npc.matriochka.rumor." + w,
			Component.translatable("rumor.matriochka.dir." + direction(dx, dz)),
			Component.translatable("rumor.matriochka.dist." + distance(Math.sqrt(dx * dx + dz * dz))));
	}
}
