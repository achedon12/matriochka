package fr.achedon12.matriochka.compat.rei;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import me.shedaniel.math.Point;
import me.shedaniel.math.Rectangle;
import me.shedaniel.rei.api.client.gui.Renderer;
import me.shedaniel.rei.api.client.gui.widgets.Widget;
import me.shedaniel.rei.api.client.gui.widgets.Widgets;
import me.shedaniel.rei.api.client.plugins.REIClientPlugin;
import me.shedaniel.rei.api.client.registry.category.CategoryRegistry;
import me.shedaniel.rei.api.client.registry.display.DisplayCategory;
import me.shedaniel.rei.api.client.registry.display.DisplayRegistry;
import me.shedaniel.rei.api.common.category.CategoryIdentifier;
import me.shedaniel.rei.api.common.display.DisplaySerializer;
import me.shedaniel.rei.api.common.display.basic.BasicDisplay;
import me.shedaniel.rei.api.common.entry.EntryIngredient;
import me.shedaniel.rei.api.common.util.EntryIngredients;
import me.shedaniel.rei.api.common.util.EntryStacks;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;

/**
 * Roughly Enough Items support: one recipe page per Matriochka station, as the JEI plugin has (compat/jei), with the
 * station as its workstation. REI loads this class through the "rei_client" entrypoint, so without REI it is never
 * touched and the mod does not need it.
 */
public class MatrioReiPlugin implements REIClientPlugin {
	private static final int PER_ROW = 5, SLOT = 18;

	/** Stations that have recipes. */
	private static List<String> stations() {
		List<String> out = new ArrayList<>();
		for (Defs.BlockDef b : Content.BLOCKS) if (b.kind().equals("station") && !Recipes.of(b.id()).isEmpty()) out.add(b.id());
		return out;
	}

	private static CategoryIdentifier<StationDisplay> id(String station) {
		return CategoryIdentifier.of(Matriochka.MOD_ID, station);
	}

	@Override
	public void registerCategories(CategoryRegistry registry) {
		for (String station : stations()) {
			registry.add(new StationCategory(station));
			registry.addWorkstations(id(station), EntryStacks.of(ModContent.item(station)));
		}
	}

	@Override
	public void registerDisplays(DisplayRegistry registry) {
		for (String station : stations()) {
			List<Recipes.Recipe> all = Recipes.of(station);
			for (int i = 0; i < all.size(); i++) registry.add(new StationDisplay(station, all.get(i), i));
		}
	}

	/** One recipe of a station. */
	public static final class StationDisplay extends BasicDisplay {
		final String station;
		final Recipes.Recipe recipe;

		StationDisplay(String station, Recipes.Recipe recipe, int index) {
			super(inputs(recipe), List.of(EntryIngredients.of(new ItemStack(Stations.resolve(recipe.output()), recipe.count()))),
				Optional.of(Matriochka.id(station + "/" + index + "_" + recipe.output())));
			this.station = station;
			this.recipe = recipe;
		}

		private static List<EntryIngredient> inputs(Recipes.Recipe r) {
			List<EntryIngredient> out = new ArrayList<>();
			for (Recipes.Ing ing : r.inputs()) out.add(EntryIngredients.of(new ItemStack(Stations.resolve(ing.id()), ing.count())));
			return out;
		}

		@Override
		public CategoryIdentifier<?> getCategoryIdentifier() {
			return id(station);
		}

		@Override
		public DisplaySerializer<? extends me.shedaniel.rei.api.common.display.Display> getSerializer() {
			// built on the client from the mod's own tables: never sent over the network
			return null;
		}
	}

	/** The recipes of one station: the ingredients in rows of five, an arrow and the result, the boss it waits on. */
	static final class StationCategory implements DisplayCategory<StationDisplay> {
		private final String station;
		private final int rows;

		StationCategory(String station) {
			this.station = station;
			int most = 1;
			for (Recipes.Recipe r : Recipes.of(station)) most = Math.max(most, r.inputs().size());
			this.rows = (most + PER_ROW - 1) / PER_ROW;
		}

		@Override
		public CategoryIdentifier<? extends StationDisplay> getCategoryIdentifier() {
			return id(station);
		}

		@Override
		public Component getTitle() {
			return Component.translatable("block." + Matriochka.MOD_ID + "." + station);
		}

		@Override
		public Renderer getIcon() {
			return EntryStacks.of(ModContent.item(station));
		}

		@Override
		public int getDisplayHeight() {
			return rows * SLOT + 22;
		}

		@Override
		public int getDisplayWidth(StationDisplay display) {
			return PER_ROW * SLOT + 70;
		}

		@Override
		public List<Widget> setupDisplay(StationDisplay display, Rectangle bounds) {
			List<Widget> w = new ArrayList<>();
			w.add(Widgets.createRecipeBase(bounds));
			int x0 = bounds.x + 6, y0 = bounds.y + 6;
			List<EntryIngredient> in = display.getInputEntries();
			for (int i = 0; i < in.size(); i++) {
				w.add(Widgets.createSlot(new Point(x0 + (i % PER_ROW) * SLOT, y0 + (i / PER_ROW) * SLOT)).entries(in.get(i)).markInput());
			}
			int ax = x0 + PER_ROW * SLOT + 6;
			w.add(Widgets.createArrow(new Point(ax, y0)));
			w.add(Widgets.createResultSlotBackground(new Point(ax + 34, y0)));
			w.add(Widgets.createSlot(new Point(ax + 34, y0)).entries(display.getOutputEntries().getFirst()).disableBackground().markOutput());
			if (display.recipe.requiresDefeated() >= 0) {
				for (Defs.BossDef b : Content.BOSSES) {
					if (b.world() == display.recipe.requiresDefeated()) {
						w.add(Widgets.createLabel(new Point(x0, bounds.getMaxY() - 12),
							Component.translatable("jei.matriochka.requires", Component.translatable("entity." + Matriochka.MOD_ID + "." + b.id())))
							.leftAligned().noShadow().color(0xFF7A5A3A, 0xFFC8A070));
						break;
					}
				}
			}
			return w;
		}

		@Override
		public Identifier getIdentifier() {
			return id(station).getIdentifier();
		}
	}
}
