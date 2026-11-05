package fr.achedon12.matriochka.compat;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.world.Worlds;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.fabricmc.fabric.api.entity.event.v1.ServerEntityLevelChangeEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

/**
 * Map mods. World 5's rule is darkness: a minimap's cave mode and entity radar would show what the dark hides. For
 * players whose client runs Xaero's Minimap or World Map (the client says so when it joins), entering World 5 sends
 * Xaero's documented "fair-play" system-message code, which turns off its cave mode and radar, and leaving sends its
 * reset code. Nothing here needs Xaero: without it, no client ever reports it and nothing is sent.
 */
public final class MapCompat {
	/** Xaero's codes, from its mod page ("Server-side features"): fair-play, and the reset of every flag. */
	private static final String FAIR = "§f§a§i§r§x§a§e§r§o", RESET = "§r§e§s§e§t§x§a§e§r§o";
	/** The world whose rule hides what a map would show. */
	private static final int DARK = 5;
	private static final Set<UUID> XAERO = ConcurrentHashMap.newKeySet();

	/** Sent once by the client when it joins: which map mods it runs. */
	public record MapsPayload(boolean xaero) implements CustomPacketPayload {
		public static final Type<MapsPayload> TYPE = new Type<>(Matriochka.id("maps"));
		public static final StreamCodec<RegistryFriendlyByteBuf, MapsPayload> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, MapsPayload::xaero, MapsPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	private MapCompat() {}

	public static void init() {
		PayloadTypeRegistry.serverboundPlay().register(MapsPayload.TYPE, MapsPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(MapsPayload.TYPE, (payload, ctx) -> {
			if (!payload.xaero()) return;
			XAERO.add(ctx.player().getUUID());
			if (Worlds.number(ctx.player().level()) == DARK) darken(ctx.player());
		});
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> XAERO.remove(handler.getPlayer().getUUID()));
		ServerEntityLevelChangeEvents.AFTER_PLAYER_CHANGE_LEVEL.register((player, from, to) -> {
			if (!XAERO.contains(player.getUUID())) return;
			if (Worlds.number(to) == DARK) darken(player);
			else if (Worlds.number(from) == DARK) player.sendSystemMessage(Component.translatable("message.matriochka.maps.clear").withStyle(ChatFormatting.GRAY).append(Component.literal(RESET)));
		});
	}

	private static void darken(ServerPlayer player) {
		player.sendSystemMessage(Component.translatable("message.matriochka.maps.dark").withStyle(ChatFormatting.GRAY).append(Component.literal(FAIR)));
	}
}
