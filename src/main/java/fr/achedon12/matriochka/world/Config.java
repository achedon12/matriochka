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
 * karma: false freezes every karma change (the Journal still shows the value). soulGainMultiplier scales every soul gain.
 * maxActiveGroups and maxParcels (0 = no limit) cap how many groups may hold worlds and how many parcels may be handed
 * out on the server: a Seed whose group would go over a limit waits, unhatched, until room is made.
 */
public final class Config {
	public static class Values {
		public boolean progressionGates = true;
		public float mobHealthMultiplier = 1f;
		public float mobDamageMultiplier = 1f;
		public int maxGroupSize = 8;
		public String difficulty = "normal";
		public boolean karma = true;
		public float soulGainMultiplier = 1f;
		public int maxActiveGroups = 0;
		public int maxParcels = 0;
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

	public static final java.util.List<String> DIFFICULTIES = java.util.List.of("story", "normal", "nightmare", "hardcore");

	public static String difficulty() {
		return mode();
	}

	/** Sets the difficulty for the whole server and writes it to config/matriochka.json (/matriochka difficulty). */
	public static boolean setDifficulty(String mode) {
		String m = mode.toLowerCase(java.util.Locale.ROOT);
		if (!DIFFICULTIES.contains(m)) return false;
		values.difficulty = m;
		try {
			Path p = FabricLoader.getInstance().getConfigDir().resolve("matriochka.json");
			Files.writeString(p, new GsonBuilder().setPrettyPrinting().create().toJson(values));
		} catch (Exception e) {
			Matriochka.LOG.warn("Could not write config/matriochka.json", e);
		}
		return true;
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

	/** False when the server turned karma off: no action moves it. */
	public static boolean karma() {
		return values.karma;
	}

	/** Souls actually gained for a gain of n (never negative, at least 1 for a positive gain unless the multiplier is 0). */
	public static int souls(int n) {
		if (n <= 0) return n;
		float m = Math.max(0f, values.soulGainMultiplier);
		if (m == 0f) return 0;
		return Math.max(1, Math.round(n * m));
	}

	/** Largest number of groups holding at least one world at once, or 0 for no limit. */
	public static int maxActiveGroups() {
		return Math.max(0, values.maxActiveGroups);
	}

	/** Largest number of parcels handed out on the server, or 0 for no limit. */
	public static int maxParcels() {
		return Math.max(0, values.maxParcels);
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
