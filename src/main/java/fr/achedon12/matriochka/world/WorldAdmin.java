package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

/** Group membership changes and the administrator's tools for worlds and bosses. */
public final class WorldAdmin {
	/** A disbanded group's worlds may be deleted by an administrator after this long. */
	public static final long KEEP_DISBANDED_MS = 30L * 24 * 3600 * 1000;

	private WorldAdmin() {}

	// ---------------------------------------------------------------- groups
	/** A player who left (or was sent out of) a group loses its worlds and its refuge: send them out if they stand there. */
	public static void expel(MinecraftServer server, UUID player, String oldGroup) {
		ServerPlayer p = server.getPlayerList().getPlayer(player);
		if (p == null) return;
		MatrioData data = MatrioData.get(server);
		int w = Worlds.number(p.level());
		if (w > 0 && Worlds.parcelOf(p.blockPosition()) == data.parcel(oldGroup, w)) Travel.leave(p);
		if (Refuge.inRefuge(p.level())) Refuge.expel(p, data.parcel(oldGroup));
		fr.achedon12.matriochka.rules.PlayerState.of(p).sync();
	}

	public static void kick(MinecraftServer server, UUID player) {
		MatrioData data = MatrioData.get(server);
		String g = data.groupOf(player);
		data.leave(player);
		expel(server, player, g);
	}

	public static List<UUID> disband(MinecraftServer server, String group) {
		MatrioData data = MatrioData.get(server);
		List<UUID> was = data.disband(group, System.currentTimeMillis());
		for (UUID u : was) expel(server, u, group);
		return was;
	}

	// ---------------------------------------------------------------- worlds
	private static ServerLevel blockLevel(MinecraftServer server, CompoundTag entry) {
		String dim = entry.getStringOr("block_dim", "");
		if (dim.isEmpty()) return null;
		return server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
	}

	private static String name(MinecraftServer server, String uuid) {
		try {
			var p = server.getPlayerList().getPlayer(UUID.fromString(uuid));
			if (p != null) return p.getGameProfile().name();
		} catch (IllegalArgumentException ignored) {
			// not a player id
		}
		return uuid.length() > 8 ? uuid.substring(0, 8) : uuid;
	}

	/** One line per group, then one per world it opened. */
	public static List<Component> list(MinecraftServer server) {
		MatrioData data = MatrioData.get(server);
		List<Component> out = new ArrayList<>();
		long now = System.currentTimeMillis();
		for (String g : data.groups()) {
			CompoundTag grp = data.group(g);
			CompoundTag worlds = grp.getCompoundOrEmpty("worlds");
			if (worlds.isEmpty() && data.members(g).size() <= 1 && !grp.contains("disbanded_at")) continue;
			String state = grp.contains("disbanded_at")
				? (now - grp.getLongOr("disbanded_at", now) >= KEEP_DISBANDED_MS ? "expired" : "disbanded") : "active";
			out.add(Component.translatable("command.matriochka.world.group", name(server, g), name(server, data.leader(g)), data.members(g).size(),
				Component.translatable("command.matriochka.world.state." + state), data.parcel(g)));
			for (String k : worlds.keySet()) {
				CompoundTag e = worlds.getCompoundOrEmpty(k);
				int w;
				try {
					w = Integer.parseInt(k);
				} catch (NumberFormatException ex) {
					continue;
				}
				String block = e.contains("block_pos") ? BlockPos.of(e.getLongOr("block_pos", 0L)).toShortString() + " " + e.getStringOr("block_dim", "") : "-";
				out.add(Component.translatable("command.matriochka.world.entry", w, block, data.parcel(g, w),
					Component.translatable(data.defeated(g, w) ? "command.matriochka.world.beaten" : "command.matriochka.world.not_beaten")));
			}
		}
		return out;
	}

	/** Rebuilds the Threshold platform and the boss stage of a world where they were recorded. */
	public static boolean repair(MinecraftServer server, String group, int world) {
		MatrioData data = MatrioData.get(server);
		CompoundTag e = data.worldEntry(group, world);
		ServerLevel level = server.getLevel(Worlds.key(world));
		if (level == null || !e.contains("seuil_y")) return false;
		BlockPos base = new BlockPos(e.getIntOr("seuil_x", 0), e.getIntOr("seuil_y", 64), e.getIntOr("seuil_z", 0));
		level.getChunk(base);
		Travel.buildPlatform(level, base, world);
		Arenas.build(level, world, base.offset(0, 0, Worlds.ARENA_OFFSET));
		e.remove("unstable_until");
		data.changed();
		return true;
	}

	/** Moves a group's World Block to a new place; players inside will come out there. */
	public static void move(MinecraftServer server, String group, int world, ServerLevel to, BlockPos pos) {
		MatrioData data = MatrioData.get(server);
		CompoundTag e = data.worldEntry(group, world);
		String owner = "";
		ServerLevel from = blockLevel(server, e);
		if (from != null) {
			BlockPos old = BlockPos.of(e.getLongOr("block_pos", 0L));
			if (from.getBlockEntity(old) instanceof DataBlockEntity be) owner = be.data().getStringOr("owner", "");
			if (from.getBlockState(old).is(ModContent.block("world_block"))) from.setBlock(old, Blocks.AIR.defaultBlockState(), 3);
		}
		if (owner.isEmpty()) {
			List<UUID> m = data.members(group);
			owner = m.isEmpty() ? group : m.getFirst().toString();
		}
		to.setBlock(pos, ModContent.block("world_block").defaultBlockState(), 3);
		if (to.getBlockEntity(pos) instanceof DataBlockEntity be) {
			be.data().putInt("world", world);
			be.data().putString("owner", owner);
			be.changed();
		}
		data.setWorldBlock(group, world, to, pos);
	}

	/**
	 * Resets (deletes) a group's world: everyone of the group inside is sent out, its World Block disappears, the world
	 * gets a fresh parcel and its boss counts as not beaten. Planting the Seed again opens a new world.
	 */
	public static void reset(MinecraftServer server, String group, int world) {
		MatrioData data = MatrioData.get(server);
		int oldParcel = data.parcel(group, world);
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (Worlds.number(p.level()) == world && Worlds.parcelOf(p.blockPosition()) == oldParcel) Travel.leave(p);
		}
		CompoundTag e = data.worldEntry(group, world);
		ServerLevel from = blockLevel(server, e);
		if (from != null) {
			BlockPos old = BlockPos.of(e.getLongOr("block_pos", 0L));
			if (from.isLoaded(old) && from.getBlockState(old).is(ModContent.block("world_block"))) from.setBlock(old, Blocks.AIR.defaultBlockState(), 3);
		}
		ServerLevel level = server.getLevel(Worlds.key(world));
		if (level != null) discardBosses(level, oldParcel);
		CompoundTag fresh = new CompoundTag();
		fresh.putInt("parcel", data.newParcel());
		data.group(group).getCompoundOrEmpty("worlds").put(Integer.toString(world), fresh);
		data.unmarkDefeated(group, world);
		data.changed();
	}

	/** Forgets that a group beat a world's boss and wakes the boss stage again (the lair heart re-arms). */
	public static boolean resetBoss(MinecraftServer server, String group, int world) {
		MatrioData data = MatrioData.get(server);
		data.unmarkDefeated(group, world);
		if (world == 0) return true;
		ServerLevel level = server.getLevel(Worlds.key(world));
		if (level == null) return false;
		discardBosses(level, data.parcel(group, world));
		CompoundTag e = data.worldEntry(group, world);
		if (ModContent.bossForWorld(world).lair() && e.contains("seuil_y")) {
			BlockPos seuil = new BlockPos(e.getIntOr("seuil_x", 0), e.getIntOr("seuil_y", 64), e.getIntOr("seuil_z", 0));
			BlockPos heart = Lairs.heart(world, seuil.offset(0, 0, Worlds.ARENA_OFFSET));
			level.getChunk(heart);
			Lairs.rearm(level, heart);
		}
		return true;
	}

	/** Removes the awake bosses of one parcel. */
	private static void discardBosses(ServerLevel level, int parcel) {
		BlockPos c = Worlds.parcelCenter(parcel);
		double half = Worlds.PARCEL_SIZE / 2.0;
		AABB box = new AABB(c.getX() - half, level.getMinY(), c.getZ() - half, c.getX() + half, level.getMaxY(), c.getZ() + half);
		for (MatrioBoss b : level.getEntitiesOfClass(MatrioBoss.class, box)) b.discard();
	}
}
