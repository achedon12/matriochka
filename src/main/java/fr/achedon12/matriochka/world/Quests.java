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

/** Optional quest book: 70 quests, tracked through PlayerState counters (see QuestHooks for what each kind watches). */
public final class Quests {
	private Quests() {}

	public static boolean done(PlayerState ps, Defs.QuestDef q) {
		return ps.has("quest_" + q.id());
	}

	public static int progress(PlayerState ps, Defs.QuestDef q) {
		return Math.min(q.objCount(), ps.counter(q.objKind() + ":" + q.objTarget()));
	}

	/** Chapter of the karma-path quests (mutual help and pacts), after the ten worlds. */
	public static final int KARMA_CHAPTER = 11;

	/** Whether a karma-path quest is open at this karma: help from +50, pacts from -50. Other quests always are. */
	public static boolean karmaOpen(Defs.QuestDef q, int karma) {
		return switch (q.type()) {
			case "help" -> karma >= Karma.TIER2;
			case "pact" -> karma <= -Karma.TIER2;
			default -> true;
		};
	}

	/** A quest is available once its world has been opened (or always on the surface); karma paths need their karma. */
	public static boolean available(ServerPlayer p, Defs.QuestDef q) {
		if (q.world() == KARMA_CHAPTER) return karmaOpen(q, PlayerState.of(p).karma());
		if (q.world() == 0) return true;
		return MatrioData.get(p.level().getServer()).defeated(p, q.world() - 1);
	}

	public static void onProgress(ServerPlayer player, String kind, String target) {
		PlayerState ps = PlayerState.of(player);
		for (Defs.QuestDef q : Content.QUESTS) {
			if (done(ps, q) || q.objKind().equals("choice")) continue;
			if (!q.objKind().equals(kind)) continue;
			if (!q.objTarget().equals(target)) {
				// a "+" target needs every part once: its counter is the number of parts done
				if (!q.objTarget().contains("+") || !java.util.List.of(q.objTarget().split("\\+")).contains(target)) continue;
				int n = 0;
				for (String part : q.objTarget().split("\\+")) if (ps.counter(kind + ":" + part) > 0) n++;
				String key = kind + ":" + q.objTarget();
				ps.addCounter(key, n - ps.counter(key));
			}
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
		if (q.type().equals("help")) ps.addKarma(3);
		if (q.type().equals("pact")) ps.addKarma(-3);
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
