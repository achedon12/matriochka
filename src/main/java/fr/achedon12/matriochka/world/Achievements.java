package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.advancements.AdvancementProgress;
import net.minecraft.server.level.ServerPlayer;

/** Grants the code-driven achievements (the ones with an "impossible" criterion in the data pack). */
public final class Achievements {
	private Achievements() {}

	public static void grant(ServerPlayer player, String customKey) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) {
			if (a.trigger().equals("custom") && a.arg().equals(customKey)) grantId(player, a.id());
		}
	}

	public static void grantPages(ServerPlayer player, int world) {
		grantByTrigger(player, "pages", world);
	}

	public static void grantStructures(ServerPlayer player, int world) {
		grantByTrigger(player, "structures", world);
	}

	private static void grantByTrigger(ServerPlayer player, String trigger, int world) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) {
			if (a.trigger().equals(trigger) && a.arg().equals(Integer.toString(world))) grantId(player, a.id());
		}
	}

	public static void grantStructure(ServerPlayer player, String structureId) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) {
			if (a.trigger().equals("structure") && a.arg().equals(structureId)) grantId(player, a.id());
		}
	}

	public static void grantId(ServerPlayer player, String id) {
		AdvancementHolder holder = player.level().getServer().getAdvancements().get(Matriochka.id(id));
		if (holder == null) return;
		AdvancementProgress progress = player.getAdvancements().getOrStartProgress(holder);
		for (String c : progress.getRemainingCriteria()) player.getAdvancements().award(holder, c);
	}
}
