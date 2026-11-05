package fr.achedon12.matriochka.world;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/**
 * config/matriochka.json: progression gates, difficulty, creature multipliers, group size.
 * difficulty: "story" (creatures deal 70% damage), "normal", "nightmare" (130% damage, Soul Cradles hold one charge),
 * "hardcore" (as nightmare, and the Doll of Life never saves you).
 */
public final class Config {
	public static class Values {
		public boolean progressionGates = true;
		public float mobHealthMultiplier = 1f;
		public float mobDamageMultiplier = 1f;
		public int maxGroupSize = 8;
		public String difficulty = "normal";
	}

	private static Values values = new Values();

	private Config() {}

	public static void load() {
		Path p = FabricLoader.getInstance().getConfigDir().resolve("matriochka.json");
		Gson gson = new GsonBuilder().setPrettyPrinting().create();
		try {
			if (Files.exists(p)) values = gson.fromJson(Files.readString(p), Values.class);
			Files.writeString(p, gson.toJson(values));
		} catch (Exception e) {
			Matriochka.LOG.warn("Could not read config/matriochka.json, using defaults", e);
		}
	}

	public static boolean gates() {
		return values.progressionGates;
	}

	private static String mode() {
		return values.difficulty == null ? "normal" : values.difficulty.toLowerCase(java.util.Locale.ROOT);
	}

	private static float difficultyScale() {
		return switch (mode()) {
			case "story" -> 0.7f;
			case "nightmare", "hardcore" -> 1.3f;
			default -> 1f;
		};
	}

	/** Charges a new Soul Cradle starts with. */
	public static int cradleCharges() {
		return mode().equals("nightmare") || mode().equals("hardcore") ? 1 : 3;
	}

	/** Health multiplier for every Matriochka creature and boss. */
	public static float healthMult() {
		return Math.max(0.1f, values.mobHealthMultiplier);
	}

	/** Damage multiplier for every Matriochka creature and boss. */
	public static float damageMult() {
		return Math.max(0.1f, values.mobDamageMultiplier) * difficultyScale();
	}

	public static boolean hardcore() {
		return "hardcore".equalsIgnoreCase(values.difficulty);
	}

	public static int maxGroupSize() {
		return Math.max(1, values.maxGroupSize);
	}

	public static Values get() {
		return values;
	}
}
