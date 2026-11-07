package fr.achedon12.matriochka.client;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.Recipes;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

/**
 * The Journal's progressive hints: the longer a player plays without getting past the same objective, the more its
 * page says. A first hint after 15 minutes of play on that objective (what the next world's object waits for), a
 * second after 35 (what it is made of, or where the Sanctuary can be found). The time counts only while playing, and
 * starts again with every new objective; it is kept in config/matriochka-hints.json.
 */
public final class Hints {
	private Hints() {}

	static final int FIRST = 15 * 60 * 20, SECOND = 35 * 60 * 20;
	private static final Path FILE = FabricLoader.getInstance().getConfigDir().resolve("matriochka-hints.json");
	private static int stage = Integer.MIN_VALUE, ticks;
	private static boolean loaded;

	/** Client tick: counts the play time spent on the current objective. */
	public static void tick(Minecraft mc) {
		if (mc.player == null || mc.level == null || mc.isPaused()) return;
		if (!loaded) load();
		int now = JournalScreen.stage();
		if (now != stage) {
			stage = now;
			ticks = 0;
			save();
		}
		ticks++;
		if (ticks % 1200 == 0) save();
	}

	/** How many hints the objective page shows now: 0, 1 or 2. */
	static int level() {
		return ticks >= SECOND ? 2 : ticks >= FIRST ? 1 : 0;
	}

	/** The hints for an objective (stage: the highest boss beaten, -1 for none), as many as level() allows. */
	static java.util.List<Component> lines(int h) {
		java.util.List<Component> out = new java.util.ArrayList<>();
		int lvl = level();
		if (lvl == 0 || h >= 10) return out;
		if (h < 0) {
			out.add(Component.translatable("journal.matriochka.hint.guardian.1"));
			if (lvl > 1) out.add(Component.translatable("journal.matriochka.hint.guardian.2"));
			return out;
		}
		int next = h + 1;
		out.add(Component.translatable("journal.matriochka.hint.rite", next, Component.translatable("item.matriochka.seed_" + next + ".desc")));
		if (lvl > 1) {
			Component recipe = recipe("seed_" + next);
			if (recipe != null) out.add(Component.translatable("journal.matriochka.hint.recipe", next, recipe));
		}
		return out;
	}

	/** "1 Queen Core, 16 Iron Ingot..." for what the Matrix Workbench makes into this item. */
	private static Component recipe(String output) {
		for (Recipes.Recipe r : Recipes.of("matrix_workbench")) {
			if (!r.output().equals(output)) continue;
			MutableComponent c = Component.empty();
			for (int i = 0; i < r.inputs().size(); i++) {
				Recipes.Ing ing = r.inputs().get(i);
				if (i > 0) c.append(", ");
				c.append(ing.count() + " ").append(new net.minecraft.world.item.ItemStack(fr.achedon12.matriochka.block.Stations.resolve(ing.id())).getHoverName());
			}
			return c;
		}
		return null;
	}

	private static void load() {
		loaded = true;
		try {
			if (!Files.exists(FILE)) return;
			JsonObject o = JsonParser.parseString(Files.readString(FILE)).getAsJsonObject();
			stage = o.get("stage").getAsInt();
			ticks = o.get("ticks").getAsInt();
		} catch (Exception e) {
			stage = Integer.MIN_VALUE;
			ticks = 0;
		}
	}

	private static void save() {
		try {
			JsonObject o = new JsonObject();
			o.addProperty("stage", stage);
			o.addProperty("ticks", ticks);
			Files.writeString(FILE, o.toString());
		} catch (Exception ignored) {
			// hints are a comfort: without the file they count again from zero
		}
	}

	/** Test hook: the play time spent on the current objective, in ticks. */
	public static void setTicks(int t) {
		ticks = t;
	}
}
