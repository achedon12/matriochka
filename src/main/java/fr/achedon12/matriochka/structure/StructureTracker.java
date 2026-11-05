package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/** Tracks which structure types a player visited (achievements "visit the 10 structure types") and powers the map. */
public final class StructureTracker {
	private StructureTracker() {}

	public static void tick(ServerPlayer player) {
		ServerLevel level = (ServerLevel) player.level();
		int world = Worlds.number(level);
		if (world == 0) return;
		PlayerState ps = PlayerState.of(player);
		BlockPos pos = player.blockPosition();
		var reg = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
		int visited = 0;
		for (Defs.StructureDef s : Content.STRUCTURES) {
			if (s.world() != world) continue;
			String key = "visited_" + s.id();
			if (!ps.has(key)) {
				var holder = reg.get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(s.id())));
				if (holder.isPresent()) {
					StructureStart start = level.structureManager().getStructureAt(pos, holder.get().value());
					if (start.isValid()) {
						ps.set(key, true);
						player.sendOverlayMessage(Component.translatable("structure.matriochka." + s.id()));
						Achievements.grantStructure(player, s.id());
					}
				}
			}
			if (ps.has(key)) visited++;
		}
		if (visited >= 10) Achievements.grantStructures(player, world);
	}

	/** Labyrinth map: names the nearest unvisited structure and its direction. */
	public static void describeNearby(ServerPlayer player) {
		ServerLevel level = (ServerLevel) player.level();
		int world = Worlds.number(level);
		var reg = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
		PlayerState ps = PlayerState.of(player);
		BlockPos best = null;
		String bestId = null;
		for (Defs.StructureDef s : Content.STRUCTURES) {
			if (s.world() != world || ps.has("visited_" + s.id())) continue;
			var holder = reg.get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(s.id())));
			if (holder.isEmpty()) continue;
			var set = net.minecraft.core.HolderSet.direct(holder.get());
			var found = level.getChunkSource().getGenerator().findNearestMapStructure(level, set, player.blockPosition(), 12, false);
			if (found != null && (best == null || found.getFirst().distSqr(player.blockPosition()) < best.distSqr(player.blockPosition()))) {
				best = found.getFirst();
				bestId = s.id();
			}
		}
		if (best == null) {
			player.sendSystemMessage(Component.translatable("message.matriochka.map.none"));
			return;
		}
		int dx = best.getX() - player.getBlockX(), dz = best.getZ() - player.getBlockZ();
		String dir = Math.abs(dx) > Math.abs(dz) ? (dx > 0 ? "east" : "west") : (dz > 0 ? "south" : "north");
		player.sendSystemMessage(Component.translatable("message.matriochka.map.found", Component.translatable("structure.matriochka." + bestId),
			(int) Math.sqrt((double) dx * dx + (double) dz * dz), Component.translatable("message.matriochka.dir." + dir)));
	}
}
