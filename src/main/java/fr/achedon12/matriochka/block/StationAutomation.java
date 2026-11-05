package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * Station automation, the late game of every machine (the design keeps the first crafts by hand). A station remembers
 * one recipe: the last one crafted by hand there, or the one picked with the small funnel on its drawer. Hoppers feed
 * its ingredients from the top and the sides (see {@link StationInventory}); every second, when they are all there,
 * the output slot has room and the station's own condition holds, it makes the recipe and a hopper below takes it out.
 * <p>
 * The conditions are those of crafting by hand: heat around the foundry, a charge in the forge (fed by lightning or by
 * Storm Essence in its fuel slot), complete darkness at the Dark Altar, deep water over the Abyssal Press, dawn or dusk
 * at the Time Workshop. The Jailer's Table only works once its lock pattern was entered, so it makes one batch per
 * pattern; the Spore Vat waits until its brew is ripe, then brews. The Soul Altar and the Class Table act on a player's
 * souls and gear, so they have no automation.
 */
public final class StationAutomation {
	/** Ticks between two automatic crafts of a station. */
	public static final int PERIOD = 20;

	private StationAutomation() {}

	/** Whether a station can be automated at all: it has recipes. */
	public static boolean automatable(String station) {
		return !Recipes.of(station).isEmpty();
	}

	/** The recipe a station keeps making, or null. Stored as its index and output, so a reordered list finds it back. */
	public static Recipes.@Nullable Recipe selected(DataBlockEntity be, String station) {
		String out = be.data().getStringOr("auto", "");
		if (out.isEmpty()) return null;
		List<Recipes.Recipe> list = Recipes.of(station);
		int i = be.data().getIntOr("auto_i", -1);
		if (i >= 0 && i < list.size() && list.get(i).output().equals(out)) return list.get(i);
		for (Recipes.Recipe r : list) if (r.output().equals(out)) return r;
		return null;
	}

	/** Index of the selected recipe in the station's list, or -1. */
	public static int selectedIndex(DataBlockEntity be, String station) {
		Recipes.Recipe r = selected(be, station);
		return r == null ? -1 : Recipes.of(station).indexOf(r);
	}

	/** Makes recipe #index the one the station keeps making, for this player (who must be allowed to craft it). */
	public static String select(DataBlockEntity be, String station, int index, ServerPlayer player) {
		List<Recipes.Recipe> list = Recipes.of(station);
		if (index < 0 || index >= list.size()) return "message.matriochka.station.unknown";
		Recipes.Recipe r = list.get(index);
		if (!Stations.canSeeRecipe(player, r)) return "message.matriochka.station.locked";
		if (!Stations.tookPart(player, r)) return "message.matriochka.station.take_part";
		be.data().putString("auto", r.output());
		be.data().putInt("auto_i", index);
		be.data().putString("auto_owner", player.getUUID().toString());
		be.setChanged();
		return null;
	}

	public static void clear(DataBlockEntity be) {
		be.data().remove("auto");
		be.data().remove("auto_i");
		be.setChanged();
	}

	/** Items of one kind in the input slots (the fuel slot included), whatever slot they sit in. */
	private static int buffered(DataBlockEntity be, Item item) {
		int n = 0;
		for (int i = 0; i < StationInventory.OUTPUT; i++) if (be.items().get(i).is(item)) n += be.items().get(i).getCount();
		return n;
	}

	private static void takeBuffered(DataBlockEntity be, Item item, int n) {
		for (int i = 0; i < StationInventory.OUTPUT && n > 0; i++) {
			ItemStack s = be.items().get(i);
			if (s.is(item)) {
				int k = Math.min(n, s.getCount());
				s.shrink(k);
				n -= k;
			}
		}
	}

	/** Whether the output slot can take this stack whole. */
	private static boolean room(DataBlockEntity be, ItemStack out) {
		ItemStack o = be.items().get(StationInventory.OUTPUT);
		if (o.isEmpty()) return true;
		return ItemStack.isSameItemSameComponents(o, out) && o.getCount() + out.getCount() <= o.getMaxStackSize();
	}

	/** Whether the selected recipe's ingredients are all in the buffer. */
	public static boolean stocked(DataBlockEntity be, Recipes.Recipe r) {
		for (Recipes.Ing ing : r.inputs()) if (buffered(be, Stations.resolve(ing.id())) < ing.count()) return false;
		return true;
	}

	/**
	 * Whether the station's own condition lets it work by itself right now. The forge burns a buffered Storm Essence
	 * (one the recipe does not need) when it has no charge left.
	 */
	public static boolean ready(ServerLevel level, BlockPos pos, String station, DataBlockEntity be, Recipes.Recipe r) {
		if (station.equals("lightning_forge") && be.data().getIntOr("charge", 0) <= 0) {
			Item essence = ModContent.item("storm_essence");
			int need = 0;
			for (Recipes.Ing ing : r.inputs()) if (Stations.resolve(ing.id()) == essence) need += ing.count();
			if (buffered(be, essence) > need) {
				ItemStack fuel = be.items().get(StationInventory.FUEL);
				if (fuel.is(essence)) fuel.shrink(1);
				else takeBuffered(be, essence, 1);
				be.data().putInt("charge", Math.min(8, Stations.ESSENCE_CHARGE));
				level.sendParticles(ParticleTypes.ELECTRIC_SPARK, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5, 12, 0.3, 0.2, 0.3, 0.2);
			}
		}
		if (station.equals("spore_vat") && Stations.fermentStage(be.data().getIntOr("ferment", 0)) < 1) return false;
		return Stations.condition(level, pos, station, be) == 1;
	}

	/** One pass of a station: craft the selected recipe once when everything is there. Returns true when it crafted. */
	public static boolean tick(ServerLevel level, BlockPos pos, String station, DataBlockEntity be) {
		if (!automatable(station) || !be.hasItems()) return false;
		Recipes.Recipe r = selected(be, station);
		if (r == null || !stocked(be, r)) return false;
		// the output is rolled once the conditions hold; its stack size is known before
		ItemStack probe = new ItemStack(Stations.resolve(r.output()), station.equals("spore_vat") ? Stations.vatYield(r, Stations.fermentStage(be.data().getIntOr("ferment", 0))) : r.count());
		if (!room(be, probe)) return false;
		if (!ready(level, pos, station, be, r)) {
			be.setChanged();
			return false;
		}
		ItemStack out = Stations.output(level, station, r, be);
		if (!room(be, out)) return false;
		for (Recipes.Ing ing : r.inputs()) takeBuffered(be, Stations.resolve(ing.id()), ing.count());
		ItemStack o = be.items().get(StationInventory.OUTPUT);
		if (o.isEmpty()) be.items().set(StationInventory.OUTPUT, out);
		else o.grow(out.getCount());
		be.data().putInt("auto_made", be.data().getIntOr("auto_made", 0) + 1);
		Stations.afterCraft(level, pos, station, be);
		return true;
	}
}
