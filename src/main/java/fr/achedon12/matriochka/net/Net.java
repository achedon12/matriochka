package fr.achedon12.matriochka.net;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Quests;
import fr.achedon12.matriochka.world.Worlds;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;

/** Network payloads: player state sync (HUD + journal) and the journal's karma-quest choices. */
public final class Net {
	/** Snapshot of everything the client HUD and Journal need, as a compound tag. */
	public record StatePayload(CompoundTag tag) implements CustomPacketPayload {
		public static final Type<StatePayload> TYPE = new Type<>(Matriochka.id("state"));
		public static final StreamCodec<RegistryFriendlyByteBuf, StatePayload> CODEC = StreamCodec.composite(ByteBufCodecs.COMPOUND_TAG, StatePayload::tag, StatePayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	public record OpenJournalPayload(boolean scroll) implements CustomPacketPayload {
		public static final Type<OpenJournalPayload> TYPE = new Type<>(Matriochka.id("open_journal"));
		public static final StreamCodec<RegistryFriendlyByteBuf, OpenJournalPayload> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, OpenJournalPayload::scroll, OpenJournalPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	public record ChoicePayload(String quest, int choice) implements CustomPacketPayload {
		public static final Type<ChoicePayload> TYPE = new Type<>(Matriochka.id("choice"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ChoicePayload> CODEC = StreamCodec.composite(
			ByteBufCodecs.STRING_UTF8, ChoicePayload::quest, ByteBufCodecs.VAR_INT, ChoicePayload::choice, ChoicePayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** Plays an ending's crawl on the client: "seal", "absorb" or "tools". */
	public record EndingPayload(String kind) implements CustomPacketPayload {
		public static final Type<EndingPayload> TYPE = new Type<>(Matriochka.id("ending"));
		public static final StreamCodec<RegistryFriendlyByteBuf, EndingPayload> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, EndingPayload::kind, EndingPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** The Scroll page the player is reading, for the quest that asks to read all five. */
	public record ReadPayload(int page) implements CustomPacketPayload {
		public static final Type<ReadPayload> TYPE = new Type<>(Matriochka.id("read_page"));
		public static final StreamCodec<RegistryFriendlyByteBuf, ReadPayload> CODEC = StreamCodec.composite(ByteBufCodecs.VAR_INT, ReadPayload::page, ReadPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** The Journal's "New Cycle" button. */
	public record CyclePayload(boolean confirm) implements CustomPacketPayload {
		public static final Type<CyclePayload> TYPE = new Type<>(Matriochka.id("new_cycle"));
		public static final StreamCodec<RegistryFriendlyByteBuf, CyclePayload> CODEC = StreamCodec.composite(ByteBufCodecs.BOOL, CyclePayload::confirm, CyclePayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/** The first-steps guide: "read" (the Scroll reached its objective page), "hide" or "show" the card. */
	public record TutorialPayload(String action) implements CustomPacketPayload {
		public static final Type<TutorialPayload> TYPE = new Type<>(Matriochka.id("tutorial"));
		public static final StreamCodec<RegistryFriendlyByteBuf, TutorialPayload> CODEC = StreamCodec.composite(ByteBufCodecs.STRING_UTF8, TutorialPayload::action, TutorialPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	/**
	 * Sent just before one of the mod's peoples opens its trades, so the client shows the Matriochka stall instead of
	 * the villager screen: the trader's world, what kind of trader it is ("people", "peddler" or "travelling"), how many
	 * of the last offers are black-market goods, the karma the prices were set with, and for a travelling merchant
	 * the ticks before it moves on (-1 otherwise).
	 */
	public record MerchantInfoPayload(int entity, int world, String kind, int contraband, int karma, int ticksLeft) implements CustomPacketPayload {
		public static final Type<MerchantInfoPayload> TYPE = new Type<>(Matriochka.id("merchant_info"));
		public static final StreamCodec<RegistryFriendlyByteBuf, MerchantInfoPayload> CODEC = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, MerchantInfoPayload::entity, ByteBufCodecs.VAR_INT, MerchantInfoPayload::world, ByteBufCodecs.STRING_UTF8, MerchantInfoPayload::kind,
			ByteBufCodecs.VAR_INT, MerchantInfoPayload::contraband, ByteBufCodecs.INT, MerchantInfoPayload::karma, ByteBufCodecs.INT, MerchantInfoPayload::ticksLeft,
			MerchantInfoPayload::new);

		@Override
		public Type<? extends CustomPacketPayload> type() {
			return TYPE;
		}
	}

	private Net() {}

	public static void init() {
		PayloadTypeRegistry.clientboundPlay().register(StatePayload.TYPE, StatePayload.CODEC);
		PayloadTypeRegistry.clientboundPlay().register(OpenJournalPayload.TYPE, OpenJournalPayload.CODEC);
		PayloadTypeRegistry.clientboundPlay().register(EndingPayload.TYPE, EndingPayload.CODEC);
		PayloadTypeRegistry.clientboundPlay().register(MerchantInfoPayload.TYPE, MerchantInfoPayload.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(ChoicePayload.TYPE, ChoicePayload.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(CyclePayload.TYPE, CyclePayload.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(ReadPayload.TYPE, ReadPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(ReadPayload.TYPE, (payload, ctx) -> fr.achedon12.matriochka.world.QuestHooks.read(ctx.player(), payload.page()));
		PayloadTypeRegistry.serverboundPlay().register(TutorialPayload.TYPE, TutorialPayload.CODEC);
		ServerPlayNetworking.registerGlobalReceiver(TutorialPayload.TYPE, (payload, ctx) -> fr.achedon12.matriochka.world.Tutorial.action(ctx.player(), payload.action()));
		ServerPlayNetworking.registerGlobalReceiver(CyclePayload.TYPE, (payload, ctx) -> {
			if (payload.confirm()) fr.achedon12.matriochka.world.Cycles.begin(ctx.player());
		});
		ServerPlayNetworking.registerGlobalReceiver(ChoicePayload.TYPE, (payload, ctx) -> {
			ServerPlayer p = ctx.player();
			for (Defs.QuestDef q : Content.QUESTS) {
				if (q.id().equals(payload.quest()) && q.objKind().equals("choice") && Quests.available(p, q)) {
					Quests.complete(p, PlayerState.of(p), q, payload.choice() >= 0 ? 1 : -1);
				}
			}
			syncState(p, PlayerState.of(p));
		});
	}

	public static void syncState(ServerPlayer player, PlayerState ps) {
		if (player.connection == null) return;
		CompoundTag t = ps.tag().copy();
		t.remove("return");
		MatrioData data = MatrioData.get(player.level().getServer());
		String group = data.groupOf(player.getUUID());
		t.putInt("done", data.group(group).getIntOr("done", 0));
		t.putInt("members", data.members(group).size());
		t.putInt("here", Worlds.number(player.level()));
		t.putInt("cycle", fr.achedon12.matriochka.world.Cycles.of(data, group));
		t.put("variants", fr.achedon12.matriochka.world.Variants.summary(data, group));
		ServerPlayNetworking.send(player, new StatePayload(t));
	}

	public static void playEnding(ServerPlayer player, String kind) {
		if (player.connection == null) return;
		ServerPlayNetworking.send(player, new EndingPayload(kind));
	}

	/** Tells the client which of the mod's traders is about to open its trades; nothing for a client without the mod. */
	public static void merchantInfo(ServerPlayer player, MerchantInfoPayload info) {
		if (player.connection == null || !ServerPlayNetworking.canSend(player, MerchantInfoPayload.TYPE)) return;
		ServerPlayNetworking.send(player, info);
	}

	public static void openJournal(ServerPlayer player, boolean scroll) {
		PlayerState ps = PlayerState.of(player);
		syncState(player, ps);
		ServerPlayNetworking.send(player, new OpenJournalPayload(scroll));
	}

	static FriendlyByteBuf unused() {
		return null;
	}
}
