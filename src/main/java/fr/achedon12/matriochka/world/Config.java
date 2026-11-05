package fr.achedon12.matriochka.world;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/**
 * config/matriochka.json: progression gates, difficulty, creature multipliers, group size.
 * difficulty: "story" (creatures deal 70% damage, the inventory is kept on death), "normal", "nightmare" (130% damage,
 * Soul Cradles hold one charge), "hardcore" (as nightmare, the Doll of Life never saves you, death is permanent and a
 * broken World Block deletes its world for the group).
 */
public final class Config {
	public static class Values {
		public boolean progressionGates = true;
		public float mobHealthMultiplier = 1f;
		public float mobDamageMultiplier = 1f;
		public int maxGroupSize = 8;
		public String difficulty = "normal";
		/** World events (invasions, surges, travelling merchants): on or off, and how often (see worldEventChance). */
		public boolean worldEvents = true;
		/** Chance that an event starts around a player in a world, rolled once a minute. */
		public float worldEventChance = 0.06f;
		/** Minutes of quiet after an event before the next one can start in the same world. */
		public int worldEventCooldown = 10;
		/** Relative weights of the three events. */
		public int invasionWeight = 3, surgeWeight = 3, merchantWeight = 2;
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

	/** Story mode: nothing is lost on death. */
	public static boolean keepInventory() {
		return mode().equals("story");
	}

	public static boolean hardcore() {
		return "hardcore".equalsIgnoreCase(values.difficulty);
	}

	public static int maxGroupSize() {
		return Math.max(1, values.maxGroupSize);
	}

	/** Whether world events may happen at all (never in peaceful: see world/WorldEvents). */
	public static boolean worldEvents() {
		return values.worldEvents && values.worldEventChance > 0;
	}

	public static float worldEventChance() {
		return Math.max(0f, Math.min(1f, values.worldEventChance));
	}

	/** Ticks of quiet after an event. */
	public static int worldEventCooldown() {
		return Math.max(0, values.worldEventCooldown) * 1200;
	}

	public static Values get() {
		return values;
	}
}
