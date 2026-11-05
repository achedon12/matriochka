package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.Recipes;
import net.minecraft.core.Direction;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.WorldlyContainer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * The automatable side of a station, as hoppers, droppers and comparators see it. Slots 0 to 7 hold the ingredients of
 * the selected recipe, two slots per ingredient in recipe order (so one ingredient can never crowd out another);
 * slot 8 holds Storm Essence for the Lightning Forge's charge; slot 9 is the output. Ingredients go in from the top
 * and the sides, the output comes out from below. Below also gives back what no longer fits the selected recipe (an
 * input left over after the recipe changed). The stacks live in the station's block entity.
 */
public final class StationInventory implements WorldlyContainer {
	public static final int SIZE = 10, FUEL = 8, OUTPUT = 9;
	private static final int[] INPUTS = {0, 1, 2, 3, 4, 5, 6, 7, 8};
	private static final int[] ALL = {9, 0, 1, 2, 3, 4, 5, 6, 7, 8};

	private final DataBlockEntity be;
	private final String station;

	public StationInventory(DataBlockEntity be, String station) {
		this.be = be;
		this.station = station;
	}

	private Recipes.@Nullable Recipe recipe() {
		return StationAutomation.selected(be, station);
	}

	/** The ingredient a slot is kept for under the selected recipe, or null (fuel slot, output, unused). */
	public static Recipes.@Nullable Ing ingredientOf(Recipes.@Nullable Recipe r, int slot) {
		if (r == null || slot >= FUEL) return null;
		int i = slot / 2;
		return i < r.inputs().size() ? r.inputs().get(i) : null;
	}

	/** Whether a stack belongs in a slot under the selected recipe. */
	public boolean fits(int slot, ItemStack stack) {
		if (slot == FUEL) return station.equals("lightning_forge") && stack.is(fr.achedon12.matriochka.content.ModContent.item("storm_essence"));
		Recipes.Ing ing = ingredientOf(recipe(), slot);
		return ing != null && stack.is(Stations.resolve(ing.id()));
	}

	@Override
	public int[] getSlotsForFace(Direction direction) {
		return direction == Direction.DOWN ? ALL : INPUTS;
	}

	@Override
	public boolean canPlaceItemThroughFace(int slot, ItemStack stack, @Nullable Direction direction) {
		return direction != Direction.DOWN && slot < OUTPUT && canPlaceItem(slot, stack);
	}

	@Override
	public boolean canTakeItemThroughFace(int slot, ItemStack stack, Direction direction) {
		if (direction != Direction.DOWN) return false;
		return slot == OUTPUT || !fits(slot, stack);
	}

	@Override
	public boolean canPlaceItem(int slot, ItemStack stack) {
		return slot < OUTPUT && fits(slot, stack);
	}

	@Override
	public int getContainerSize() {
		return SIZE;
	}

	@Override
	public boolean isEmpty() {
		return !be.hasItems();
	}

	@Override
	public ItemStack getItem(int slot) {
		return be.items().get(slot);
	}

	@Override
	public ItemStack removeItem(int slot, int count) {
		ItemStack out = ContainerHelper.removeItem(be.items(), slot, count);
		if (!out.isEmpty()) setChanged();
		return out;
	}

	@Override
	public ItemStack removeItemNoUpdate(int slot) {
		return ContainerHelper.takeItem(be.items(), slot);
	}

	@Override
	public void setItem(int slot, ItemStack stack) {
		be.items().set(slot, stack);
		stack.limitSize(getMaxStackSize(stack));
		setChanged();
	}

	@Override
	public void setChanged() {
		be.setChanged();
	}

	@Override
	public boolean stillValid(Player player) {
		return false;
	}

	@Override
	public void clearContent() {
		be.items().clear();
		setChanged();
	}
}
