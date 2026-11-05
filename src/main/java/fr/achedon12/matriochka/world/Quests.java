package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;

/** Optional quest book: 64 quests, tracked through PlayerState counters. */
public final class Quests {
	private Quests() {}

	public static boolean done(PlayerState ps, Defs.QuestDef q) {
		return ps.has("quest_" + q.id());
	}

	public static int progress(PlayerState ps, Defs.QuestDef q) {
		String kind = q.objKind().equals("deliver") ? "obtain" : q.objKind();
		return Math.min(q.objCount(), ps.counter(kind + ":" + q.objTarget()));
	}

	/** A quest is available once its world has been opened (or always on the surface). */
	public static boolean available(ServerPlayer p, Defs.QuestDef q) {
		if (q.world() == 0) return true;
		return MatrioData.get(p.level().getServer()).defeated(p, q.world() - 1);
	}

	public static void onProgress(ServerPlayer player, String kind, String target) {
		PlayerState ps = PlayerState.of(player);
		for (Defs.QuestDef q : Content.QUESTS) {
			if (done(ps, q) || q.objKind().equals("choice")) continue;
			String qk = q.objKind().equals("deliver") ? "obtain" : q.objKind();
			if (!qk.equals(kind) || !q.objTarget().equals(target)) continue;
			if (!available(player, q)) continue;
			if (progress(ps, q) >= q.objCount()) complete(player, ps, q, 0);
		}
	}

	/** Completes a quest; for karma quests, choice is +1 (help) or -1 (betray). */
	public static void complete(ServerPlayer player, PlayerState ps, Defs.QuestDef q, int choice) {
		if (done(ps, q)) return;
		ps.set("quest_" + q.id(), true);
		if (q.objKind().equals("choice")) {
			ps.addKarma(choice >= 0 ? q.objCount() : -q.objCount());
			if (choice < 0) ps.addSouls(q.rewardCount());
		}
		switch (q.rewardKind()) {
			case "souls" -> { if (!q.objKind().equals("choice") || choice >= 0) ps.addSouls(q.rewardCount()); }
			case "item" -> {
				ItemStack stack = new ItemStack(ModContent.item(q.rewardTarget()), q.rewardCount());
				if (!player.getInventory().add(stack)) net.minecraft.world.level.block.Block.popResource(player.level(), player.blockPosition(), stack);
			}
			case "title" -> ps.tag().putString("title", q.rewardTarget());
			default -> {}
		}
		player.sendSystemMessage(Component.translatable("message.matriochka.quest_done", Component.translatable("quest.matriochka." + q.id()))
			.withStyle(ChatFormatting.GOLD));
		player.level().playSound(null, player.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.6f, 1.4f);
		ps.sync();
	}
}
