package fr.achedon12.matriochka.compat.jei;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import mezz.jei.api.IModPlugin;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.types.IRecipeType;
import mezz.jei.api.registration.IRecipeCatalystRegistration;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import mezz.jei.api.registration.IRecipeRegistration;
import net.minecraft.resources.Identifier;

/**
 * Just Enough Items support: one recipe page per Matriochka station, with the station as its catalyst. JEI loads this
 * class through the "jei_mod_plugin" entrypoint, so without JEI it is never touched and the mod does not need it.
 */
public class MatrioJeiPlugin implements IModPlugin {
	/** Stations that have recipes, in the order of the design document, with their JEI recipe type. */
	private final Map<String, IRecipeType<Recipes.Recipe>> types = new java.util.LinkedHashMap<>();

	@Override
	public Identifier getPluginUid() {
		return Matriochka.id("jei");
	}

	private Map<String, IRecipeType<Recipes.Recipe>> types() {
		if (types.isEmpty()) {
			for (Defs.BlockDef b : Content.BLOCKS) {
				if (b.kind().equals("station") && !Recipes.of(b.id()).isEmpty()) {
					types.put(b.id(), IRecipeType.create(Matriochka.MOD_ID, b.id(), Recipes.Recipe.class));
				}
			}
		}
		return types;
	}

	@Override
	public void registerCategories(IRecipeCategoryRegistration registration) {
		IGuiHelper gui = registration.getJeiHelpers().getGuiHelper();
		List<StationCategory> categories = new ArrayList<>();
		types().forEach((station, type) -> categories.add(new StationCategory(type, station, gui)));
		registration.addRecipeCategories(categories.toArray(StationCategory[]::new));
	}

	@Override
	public void registerRecipes(IRecipeRegistration registration) {
		types().forEach((station, type) -> registration.addRecipes(type, Recipes.of(station)));
	}

	@Override
	public void registerRecipeCatalysts(IRecipeCatalystRegistration registration) {
		types().forEach((station, type) -> registration.addCraftingStation(type, ModContent.item(station)));
	}
}
