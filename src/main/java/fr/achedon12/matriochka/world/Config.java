package fr.achedon12.matriochka.world;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/** config/matriochka.json: progression gates, difficulty multipliers, group size. */
public final class Config {
	public static class Values {
		public boolean progressionGates = true;
		public float mobHealthMultiplier = 1f;
		public float mobDamageMultiplier = 1f;
		public int maxGroupSize = 8;
		public boolean screenShake = true;
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

	public static Values get() {
		return values;
	}
}
