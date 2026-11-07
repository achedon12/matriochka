package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.structure.Rewards;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

/**
 * The Journal's world cards: every item of a world and how it is had, read from the mod's own tables so the card
 * can never disagree with the game. An item can be crafted (at which station), dropped (by which creature or boss),
 * mined (from which ore) or found (in which chests of the world's structures); several ways are listed in that order.
 */
public final class WorldCards {
	private WorldCards() {}

	/** One item and its ways, the first one short for the card's line, all of them for its tooltip. */
	public record Entry(Defs.ItemDef item, List<Component> ways) {}

	private static final Map<Integer, List<Entry>> CACHE = new LinkedHashMap<>();

	public static List<Entry> of(int world) {
		return CACHE.computeIfAbsent(world, WorldCards::build);
	}

	private static Component name(String id) {
		return new net.minecraft.world.item.ItemStack(fr.achedon12.matriochka.block.Stations.resolve(id)).getHoverName();
	}

	private static List<Entry> build(int world) {
		// station recipes, by what they make
		Map<String, List<String>> crafted = new LinkedHashMap<>();
		for (Defs.BlockDef b : Content.BLOCKS) {
			if (!b.kind().equals("station")) continue;
			for (Recipes.Recipe r : Recipes.of(b.id())) crafted.computeIfAbsent(r.output(), k -> new ArrayList<>()).add(b.id());
		}
		List<Entry> out = new ArrayList<>();
		for (Defs.ItemDef it : Content.ITEMS) {
			if (it.world() != world) continue;
			List<Component> ways = new ArrayList<>();
			for (String st : crafted.getOrDefault(it.id(), List.of()).stream().distinct().toList())
				ways.add(Component.translatable("journal.matriochka.card.craft", name(st)));
			for (Defs.MobDef m : Content.MOBS) {
				if (it.id().equals(m.drop())) ways.add(Component.translatable("journal.matriochka.card.drop", Component.translatable("entity.matriochka." + m.id())));
				else if (it.id().equals(m.rareDrop())) ways.add(Component.translatable("journal.matriochka.card.rare_drop", Component.translatable("entity.matriochka." + m.id())));
			}
			for (Defs.BossDef b : Content.BOSSES)
				if (it.id().equals(b.core())) ways.add(Component.translatable("journal.matriochka.card.boss", Component.translatable("entity.matriochka." + b.id())));
			for (Defs.BlockDef b : Content.BLOCKS)
				if (it.id().equals(b.drop()) && !it.id().equals(b.id())) ways.add(Component.translatable("journal.matriochka.card.ore", name(b.id())));
			String chest = Rewards.chestTier(it);
			if (chest != null) ways.add(Component.translatable("journal.matriochka.card.chest." + chest));
			if (ways.isEmpty()) ways.add(Component.translatable("journal.matriochka.card.other"));
			out.add(new Entry(it, ways));
		}
		return out;
	}

	/** Every way of an entry, one per line, for its tooltip. */
	public static Component tooltip(Entry e) {
		MutableComponent c = Component.empty().append(name(e.item().id()).copy().withStyle(net.minecraft.ChatFormatting.GOLD));
		for (Component w : e.ways()) c.append("\n").append(w);
		return c;
	}
}
