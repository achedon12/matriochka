package fr.achedon12.matriochka.compat.jei;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.widgets.IRecipeExtrasBuilder;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.IFocusGroup;
import mezz.jei.api.recipe.category.AbstractRecipeCategory;
import mezz.jei.api.recipe.types.IRecipeType;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.ItemStack;

/**
 * The recipes of one station: the ingredients in a row (two rows past five), an arrow and the result. A recipe that
 * opens with a boss says which one under the row.
 */
public class StationCategory extends AbstractRecipeCategory<Recipes.Recipe> {
	private static final int PER_ROW = 5, SLOT = 18, ARROW_X = PER_ROW * SLOT + 6, OUT_X = ARROW_X + 30;
	private final String station;

	public StationCategory(IRecipeType<Recipes.Recipe> type, String station, IGuiHelper gui) {
		super(type, Component.translatable("block." + Matriochka.MOD_ID + "." + station), gui.createDrawableItemLike(ModContent.item(station)),
			OUT_X + 26, rows(station) * SLOT + 12);
		this.station = station;
	}

	private static int rows(String station) {
		int most = 1;
		for (Recipes.Recipe r : Recipes.of(station)) most = Math.max(most, r.inputs().size());
		return (most + PER_ROW - 1) / PER_ROW;
	}

	@Override
	public void setRecipe(IRecipeLayoutBuilder builder, Recipes.Recipe recipe, IFocusGroup focuses) {
		for (int i = 0; i < recipe.inputs().size(); i++) {
			Recipes.Ing ing = recipe.inputs().get(i);
			builder.addInputSlot(1 + (i % PER_ROW) * SLOT, 1 + (i / PER_ROW) * SLOT).setStandardSlotBackground()
				.add(new ItemStack(Stations.resolve(ing.id()), ing.count()));
		}
		builder.addOutputSlot(OUT_X + 5, 1).setOutputSlotBackground().add(new ItemStack(Stations.resolve(recipe.output()), recipe.count()));
	}

	@Override
	public void createRecipeExtras(IRecipeExtrasBuilder builder, Recipes.Recipe recipe, IFocusGroup focuses) {
		builder.addRecipeArrowWidget().setPosition(ARROW_X, 1);
		if (recipe.requiresDefeated() >= 0) {
			for (Defs.BossDef b : Content.BOSSES) {
				if (b.world() == recipe.requiresDefeated()) {
					builder.addText(Component.translatable("jei.matriochka.requires", Component.translatable("entity." + Matriochka.MOD_ID + "." + b.id())),
						getWidth(), 10).setPosition(0, getHeight() - 10).setColor(0xFF7A5A3A);
					break;
				}
			}
		}
	}

	@Override
	public Identifier getIdentifier(Recipes.Recipe recipe) {
		return Matriochka.id(station + "/" + Recipes.of(station).indexOf(recipe) + "_" + recipe.output().replace(':', '_'));
	}
}
