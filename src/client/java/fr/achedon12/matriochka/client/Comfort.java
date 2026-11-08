package fr.achedon12.matriochka.client;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.net.Cues;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;

/**
 * Accessibility and comfort options, kept per player in config/matriochka-client.json and edited from the Journal
 * (ComfortScreen). Only "softEffects" concerns the server: it is sent on joining and whenever it changes, so the
 * server skips Nausea and Darkness for this player and sends a gentle tint instead.
 */
public final class Comfort {
	public static final String[] CORNERS = {"top_left", "top_right", "bottom_left", "bottom_right"};

	public static class Values {
		/** Camera shake strength, 0 to 100 (percent). */
		public int shake = 100;
		/** White flashes on phase breaks and red edge flashes before signature attacks. */
		public boolean flashes = true;
		/** No Nausea or Darkness: a soft tint instead. */
		public boolean softEffects = false;
		/** Boss introductions, world title cards and the phase freeze-frame. */
		public boolean cinematics = true;
		/** Large subtitles naming a boss attack while it winds up. */
		public boolean subtitles = true;
		/** Drops two thirds of the particles the server sends inside the worlds and during boss fights. */
		public boolean reducedParticles = false;
		/** Gauges carry stripes and crosshatching besides their colour. */
		public boolean patterns = false;
		/** HUD plaque scale, 0.5 to 2. */
		public float hudScale = 1f;
		/** HUD plaque corner: top_left, top_right, bottom_left, bottom_right. */
		public String hudCorner = "top_left";
		/** A small permanent label of the world you are in: off, or one of the corners (client/WorldTitle). */
		public String worldLabel = "off";
		/** Whether the Matriochka line has been put on the F3 screen once (it can be turned off there afterwards). */
		public boolean debugLineSet = false;
		/** Music volume per situation, 0 to 100 (percent of the game's music slider). */
		public int musicExplore = 100, musicDanger = 100, musicBoss = 100, musicLayers = 100, musicStings = 100;
	}

	private static Values values = new Values();
	private static Path file = FabricLoader.getInstance().getConfigDir().resolve("matriochka-client.json");
	private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

	private Comfort() {}

	public static Values get() {
		return values;
	}

	/** Reads the options (defaults when the file is missing or broken) and writes them back normalized. */
	public static void load() {
		values = read(file);
		write(file, values);
	}

	public static void init() {
		load();
		ClientPlayConnectionEvents.JOIN.register((handler, sender, mc) -> sync());
	}

	/** Saves and tells the server what it needs to know. */
	public static void changed() {
		normalize(values);
		write(file, values);
		sync();
	}

	public static void sync() {
		if (ClientPlayNetworking.canSend(Cues.ComfortPayload.TYPE)) ClientPlayNetworking.send(new Cues.ComfortPayload(values.softEffects));
	}

	public static Values read(Path p) {
		Values v = null;
		try {
			if (Files.exists(p)) v = GSON.fromJson(Files.readString(p), Values.class);
		} catch (Exception e) {
			Matriochka.LOG.warn("Could not read {}, using defaults", p.getFileName(), e);
		}
		if (v == null) v = new Values();
		normalize(v);
		return v;
	}

	public static void write(Path p, Values v) {
		try {
			Files.createDirectories(p.getParent());
			Files.writeString(p, GSON.toJson(v));
		} catch (Exception e) {
			Matriochka.LOG.warn("Could not write {}", p.getFileName(), e);
		}
	}

	private static void normalize(Values v) {
		v.shake = clamp(v.shake);
		v.musicExplore = clamp(v.musicExplore);
		v.musicDanger = clamp(v.musicDanger);
		v.musicBoss = clamp(v.musicBoss);
		v.musicLayers = clamp(v.musicLayers);
		v.musicStings = clamp(v.musicStings);
		v.hudScale = Math.round(Math.max(0.5f, Math.min(2f, Float.isFinite(v.hudScale) ? v.hudScale : 1f)) * 4) / 4f;
		boolean known = false;
		for (String c : CORNERS) known |= c.equals(v.hudCorner);
		if (!known) v.hudCorner = "top_left";
		boolean label = "off".equals(v.worldLabel);
		for (String c : CORNERS) label |= c.equals(v.worldLabel);
		if (!label) v.worldLabel = "off";
	}

	private static int clamp(int pct) {
		return Math.max(0, Math.min(100, pct));
	}

	// ---------------------------------------------------------------- shortcuts for the renderers
	public static float shake() {
		return values.shake / 100f;
	}

	public static boolean flashes() {
		return values.flashes;
	}

	public static boolean cinematics() {
		return values.cinematics;
	}

	/** For the check run: points the options at another file. */
	public static void useFile(Path p) {
		file = p;
	}

	public static Path file() {
		return file;
	}
}
