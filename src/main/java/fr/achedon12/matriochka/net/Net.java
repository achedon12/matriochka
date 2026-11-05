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

	private Net() {}

	public static void init() {
		PayloadTypeRegistry.clientboundPlay().register(StatePayload.TYPE, StatePayload.CODEC);
		PayloadTypeRegistry.clientboundPlay().register(OpenJournalPayload.TYPE, OpenJournalPayload.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(ChoicePayload.TYPE, ChoicePayload.CODEC);
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
		ServerPlayNetworking.send(player, new StatePayload(t));
	}

	public static void openJournal(ServerPlayer player, boolean scroll) {
		PlayerState ps = PlayerState.of(player);
		syncState(player, ps);
		ServerPlayNetworking.send(player, new OpenJournalPayload(scroll));
		if (scroll) {
			if (ps.counter("read:artisan_scroll") < 5) ps.progress("read", "artisan_scroll", 5);
		}
	}

	static FriendlyByteBuf unused() {
		return null;
	}
}
