package fr.achedon12.matriochka.replay;

import fr.achedon12.matriochka.Matriochka;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

/** Payloads of the Trials screen and the talent cabinet. */
public final class ReplayNet {
	/** Client to server: a Trials action ("board", "start", "title", "leave") and its argument. */
	public record TrialAction(String action, String arg) implements CustomPacketPayload {
		public static final Type<TrialAction> TYPE = new Type<>(Matriochka.id("trial_action"));
		public static final StreamCodec<RegistryFriendlyByteBuf, TrialAction> CODEC = StreamCodec.composite(
			ByteBufCodecs.STRING_UTF8, TrialAction::action, ByteBufCodecs.STRING_UTF8, TrialAction::arg, TrialAction::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** Server to client: the leaderboards and the group's best times; open asks the client to show the Trials screen. */
	public record TrialBoard(CompoundTag board, boolean open) implements CustomPacketPayload {
		public static final Type<TrialBoard> TYPE = new Type<>(Matriochka.id("trial_board"));
		public static final StreamCodec<RegistryFriendlyByteBuf, TrialBoard> CODEC = StreamCodec.composite(
			ByteBufCodecs.COMPOUND_TAG, TrialBoard::board, ByteBufCodecs.BOOL, TrialBoard::open, TrialBoard::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** Client to server: learn a talent at the Class Table ("reset" unlearns them all). */
	public record LearnTalent(String id) implements CustomPacketPayload {
		public static final Type<LearnTalent> TYPE = new Type<>(Matriochka.id("learn_talent"));
		public static final StreamCodec<RegistryFriendlyByteBuf, LearnTalent> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, LearnTalent::id, LearnTalent::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	private ReplayNet() {}

	static void init() {
		PayloadTypeRegistry.serverboundPlay().register(TrialAction.TYPE, TrialAction.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(LearnTalent.TYPE, LearnTalent.CODEC);
		PayloadTypeRegistry.clientboundPlay().register(TrialBoard.TYPE, TrialBoard.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(TrialAction.TYPE, (payload, ctx) -> Trials.action(ctx.player(), payload.action(), payload.arg()));
		ServerPlayNetworking.registerGlobalReceiver(LearnTalent.TYPE, (payload, ctx) -> {
			String err = payload.id().equals("reset") ? Talents.reset(ctx.player()) : Talents.learn(ctx.player(), payload.id());
			if (err != null) ctx.player().sendOverlayMessage(net.minecraft.network.chat.Component.translatable(err).withStyle(net.minecraft.ChatFormatting.RED));
		});
	}

	public static void sendBoard(ServerPlayer player, boolean open) {
		if (player.connection == null) return;
		ServerPlayNetworking.send(player, new TrialBoard(Trials.board(player), open));
	}
}
