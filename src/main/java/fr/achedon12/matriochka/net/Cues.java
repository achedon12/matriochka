package fr.achedon12.matriochka.net;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Presentation cues the server sends to the client: boss introductions, phase breaks, telegraph subtitles, camera
 * shakes, world title cards, the soft tint that replaces Nausea and Darkness for players who asked for it, and how
 * many creatures hunt a player (for the adaptive music). None of them changes the game: the client draws them as its
 * comfort options allow (client/Cinematics, client/MusicThemes).
 */
public final class Cues {
	private Cues() {}

	/**
	 * kind: "intro" (entity, text = boss id), "phase" (entity, strength = phase number), "telegraph" (entity,
	 * strength = attack index, ticks = wind-up, text = boss id), "shake" (strength 0..1, ticks), "tint" (text =
	 * "nausea" or "darkness", ticks), "danger" (strength = creatures hunting the player), "world" (strength = world).
	 */
	public record CuePayload(String kind, int entity, float strength, int ticks, String text) implements CustomPacketPayload {
		public static final Type<CuePayload> TYPE = new Type<>(Matriochka.id("cue"));
		public static final StreamCodec<RegistryFriendlyByteBuf, CuePayload> CODEC = StreamCodec.composite(
			ByteBufCodecs.STRING_UTF8, CuePayload::kind, ByteBufCodecs.VAR_INT, CuePayload::entity, ByteBufCodecs.FLOAT, CuePayload::strength,
			ByteBufCodecs.VAR_INT, CuePayload::ticks, ByteBufCodecs.STRING_UTF8, CuePayload::text, CuePayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** The client's comfort choices the server must know: soft = no Nausea or Darkness, a tint instead. */
	public record ComfortPayload(boolean soft) implements CustomPacketPayload {
		public static final Type<ComfortPayload> TYPE = new Type<>(Matriochka.id("comfort"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ComfortPayload> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, ComfortPayload::soft, ComfortPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	private static final Set<UUID> SOFT = new HashSet<>();
	private static final Map<UUID, Integer> DANGER = new HashMap<>();

	public static void init() {
		PayloadTypeRegistry.clientboundPlay().register(CuePayload.TYPE, CuePayload.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(ComfortPayload.TYPE, ComfortPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(ComfortPayload.TYPE, (p, ctx) -> setSoft(ctx.player().getUUID(), p.soft()));
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> {
			SOFT.remove(handler.player.getUUID());
			DANGER.remove(handler.player.getUUID());
		});
		ServerTickEvents.END_SERVER_TICK.register(Cues::tick);
	}

	// ---------------------------------------------------------------- comfort
	public static void setSoft(UUID player, boolean soft) {
		if (soft) SOFT.add(player);
		else SOFT.remove(player);
	}

	/** True when this player asked for the soft overlay instead of Nausea and Darkness. */
	public static boolean soft(ServerPlayer player) {
		return SOFT.contains(player.getUUID());
	}

	/** Sends the gentle tint that stands in for a skipped effect. */
	public static void tint(ServerPlayer player, String kind, int ticks) {
		send(player, new CuePayload("tint", 0, 1f, ticks, kind));
	}

	// ---------------------------------------------------------------- cinematics
	/** A boss wakes: everyone near it gets its introduction. */
	public static void bossIntro(ServerLevel level, Entity boss, String id) {
		for (ServerPlayer p : near(level, boss.position(), 48)) send(p, new CuePayload("intro", boss.getId(), 1f, 70, id));
	}

	/** A boss breaks into its next phase. */
	public static void phase(ServerLevel level, Entity boss, int phase) {
		for (ServerPlayer p : near(level, boss.position(), 48)) send(p, new CuePayload("phase", boss.getId(), phase, 0, ""));
	}

	/** A boss winds up an attack: the subtitle names it for as long as the wind-up lasts. */
	public static void telegraph(ServerLevel level, Entity boss, String id, int attack, int ticks) {
		for (ServerPlayer p : near(level, boss.position(), 40)) send(p, new CuePayload("telegraph", boss.getId(), attack, ticks, id));
	}

	/** A heavy blow: players near it feel the ground, less the farther they stand. */
	public static void impact(ServerLevel level, Vec3 at, float strength, double radius, int ticks) {
		for (ServerPlayer p : near(level, at, radius)) {
			float fall = 1f - (float) Math.min(1, p.position().distanceTo(at) / radius);
			if (fall > 0.05f) shake(p, strength * (0.35f + 0.65f * fall), ticks);
		}
	}

	public static void shake(ServerPlayer player, float strength, int ticks) {
		send(player, new CuePayload("shake", 0, strength, ticks, ""));
	}

	/** A player arrives in a world: the title card plays the first time only. */
	public static void worldEntered(ServerPlayer player, int world) {
		PlayerState ps = PlayerState.of(player);
		String key = "card_" + world;
		if (ps.has(key)) return;
		ps.set(key, true);
		send(player, new CuePayload("world", 0, world, 0, ""));
	}

	// ---------------------------------------------------------------- danger
	/** Twice a second: how many creatures have this player as their target, within 24 blocks. Sent when it changes. */
	private static void tick(MinecraftServer server) {
		if (server.getTickCount() % 10 != 0) return;
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			int n = p.isSpectator() || p.isCreative() ? 0 : Math.min(9, p.level().getEntitiesOfClass(Mob.class, new AABB(p.blockPosition()).inflate(24),
				m -> m.isAlive() && m.getTarget() == p).size());
			Integer was = DANGER.put(p.getUUID(), n);
			if (was == null || was != n) send(p, new CuePayload("danger", 0, n, 0, ""));
		}
	}

	// ---------------------------------------------------------------- helpers
	private static java.util.List<ServerPlayer> near(ServerLevel level, Vec3 at, double r) {
		return level.getEntitiesOfClass(ServerPlayer.class, new AABB(at, at).inflate(r));
	}

	private static void send(ServerPlayer player, CuePayload cue) {
		if (player.connection != null && ServerPlayNetworking.canSend(player, CuePayload.TYPE)) ServerPlayNetworking.send(player, cue);
	}
}
