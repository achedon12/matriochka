package fr.achedon12.matriochka.block;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Recipes;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * The Matrix Workbench's crafting patterns: each of its recipes laid out on a 3 x 3 grid (tools/patterns.py writes
 * data/matriochka/workbench_patterns.json; the site draws the same grids). A cell asks for an item and a count; the
 * cells add up to the recipe's own cost, which is checked when the patterns load.
 */
public final class WorkbenchPatterns {
	private WorkbenchPatterns() {}

	public record Cell(String id, int count) {}

	private static final Map<String, Cell[]> BY_OUTPUT = new HashMap<>();

	static {
		try (InputStream in = WorkbenchPatterns.class.getResourceAsStream("/data/matriochka/workbench_patterns.json")) {
			if (in != null) {
				JsonObject root = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				for (Map.Entry<String, JsonElement> e : root.entrySet()) {
					JsonArray a = e.getValue().getAsJsonArray();
					Cell[] cells = new Cell[9];
					for (int i = 0; i < 9 && i < a.size(); i++) {
						if (a.get(i).isJsonNull()) continue;
						JsonArray c = a.get(i).getAsJsonArray();
						cells[i] = new Cell(c.get(0).getAsString(), c.get(1).getAsInt());
					}
					BY_OUTPUT.put(e.getKey(), cells);
				}
			}
		} catch (Exception ex) {
			Matriochka.LOG.error("[matriochka] could not read the workbench patterns", ex);
		}
		// every grid must cost exactly what its recipe costs
		for (Recipes.Recipe r : Recipes.of("matrix_workbench")) {
			Cell[] p = BY_OUTPUT.get(r.output());
			if (p == null) {
				Matriochka.LOG.warn("[matriochka] no workbench pattern for {}", r.output());
				continue;
			}
			Map<String, Integer> need = new HashMap<>();
			for (Recipes.Ing ing : r.inputs()) need.merge(ing.id(), ing.count(), Integer::sum);
			for (Cell c : p) if (c != null) need.merge(c.id(), -c.count(), Integer::sum);
			if (need.values().stream().anyMatch(v -> v != 0)) Matriochka.LOG.warn("[matriochka] the workbench pattern of {} does not match its recipe", r.output());
		}
	}

	/** The nine cells of a recipe's grid (null cells stay empty), or null when the recipe has none. */
	public static Cell[] of(String output) {
		return BY_OUTPUT.get(output);
	}

	/** Whether a cell holds what the pattern asks: the same item, at least the count; an empty cell must stay empty. */
	private static boolean fits(Cell want, ItemStack have) {
		if (want == null) return have.isEmpty();
		Item item = Stations.resolve(want.id());
		return !have.isEmpty() && have.is(item) && have.getCount() >= want.count();
	}

	/** The workbench recipe the nine stacks spell out, or null. */
	public static Recipes.Recipe match(List<ItemStack> grid) {
		for (Recipes.Recipe r : Recipes.of("matrix_workbench")) {
			Cell[] p = of(r.output());
			if (p == null) continue;
			boolean ok = true;
			for (int i = 0; i < 9 && ok; i++) ok = fits(p[i], grid.get(i));
			if (ok) return r;
		}
		return null;
	}
}
