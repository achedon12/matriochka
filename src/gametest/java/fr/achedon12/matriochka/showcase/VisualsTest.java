package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.Particles;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.registries.BuiltInRegistries;

/**
 * The visual overhaul, photographed: ./gradlew runClientGameTest -Pvisuals. Shots (in run/screenshots):
 * vis_world_N (the light, fog and particles of every world, at noon and at night for World 8's seasons), vis_stations
 * (the thirteen stations side by side, lit and in the dark), vis_frames (an item frame wall of the hand-painted
 * items), vis_inventory (the same items in the inventory) and vis_particle_ID (every new particle in front of the
 * camera).
 */
final class VisualsTest {
	private VisualsTest() {}

	private static final String[] FRAMED = {
		"hidden_doll_1", "hidden_doll_2", "hidden_doll_3", "hidden_doll_4", "hidden_doll_5", "hidden_doll_6", "hidden_doll_7",
		"hidden_doll_8", "hidden_doll_9", "hidden_doll_10", "nested_dolls", "whole_matryoshka", "life_doll", "chance_doll",
		"cracked_doll", "refuge_doll", "guardian_core", "queen_core", "titan_core", "jailer_core", "storm_king_core", "light_eater_core",
		"double_core", "leviathan_core", "seasons_core", "terrain_core", "unfinished_core", "seed_1", "seed_2", "seed_3", "seed_4",
		"seed_5", "seed_6", "seed_7", "seed_8", "seed_9", "seed_10", "artisan_scroll", "artisan_journal", "journal_page", "blank_scroll",
		"sealed_shackle", "storm_censer", "wreath_of_seasons", "unfinished_effigy", "salt_snorkel", "nacre_snorkel", "cobalt_snorkel",
		"pearl_snorkel", "sporite_sword", "ash_hammer", "jailer_blade", "lightning_lance", "shadow_blade", "mirror_blade",
		"trench_trident", "season_scythe", "seismic_mace", "artisan_blade", "chitin_chestplate", "thermal_chestplate",
		"jailer_chestplate", "celestial_chestplate", "nocturnal_chestplate", "mirror_chestplate", "diving_chestplate",
		"seasonal_chestplate", "living_rock_chestplate", "artisan_chestplate"};

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
		ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			sp.getConnection().waitForChunksRender();
			ctx.setScreen(() -> null);
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("time set 6000");
			s.runCommand("execute as @p run matriochka progression set 10");
			worlds(ctx, sp);
			s.runCommand("gamemode creative @a");
			s.runCommand("time set 6000");
			s.runCommand("effect clear @a");
			stations(ctx, sp);
			frames(ctx, sp);
			inventory(ctx, sp);
			particles(ctx, sp);
		}
	}

	/** Every world's atmosphere: looking out over the land at noon, and World 8 in each of its seasons. */
	private static void worlds(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		for (int w = 1; w <= 10; w++) {
			s.runCommand("gamemode creative @a");
			s.runCommand("execute as @p run matriochka world enter " + w);
			ctx.setScreen(() -> null);
			ctx.waitTicks(120);
			sp.getConnection().waitForChunksRender();
			s.runCommand("gamemode spectator @a");
			s.runCommand("execute as @p at @s run tp @s ~ ~6 ~ 35 12");
			ctx.waitTicks(80);
			shot(ctx, "vis_world_" + w);
			if (w == 8) {
				// one shot per season: the season follows the game time (two minutes each), so wait them out
				for (int season = 1; season < 4; season++) {
					ctx.waitTicks(2400);
					shot(ctx, "vis_world_8_season_" + season);
				}
			}
			s.runCommand("gamemode creative @a");
			s.runCommand("execute as @p run matriochka world leave");
			ctx.waitTicks(40);
		}
		// World 0: a spectator glance inside the smallest doll
		s.runCommand("gamemode spectator @a");
		s.runCommand("execute in matriochka:world_zero run tp @p 0 70 0 45 15");
		ctx.waitTicks(120);
		sp.getConnection().waitForChunksRender();
		shot(ctx, "vis_world_0");
		s.runCommand("execute in minecraft:overworld run tp @p 0 120 0");
		ctx.waitTicks(60);
	}

	/** The thirteen stations in a row on a lacquer floor, by day and in the dark (the emissive faces stay lit). */
	private static void stations(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("execute in minecraft:overworld run tp @p 0 200 0");
		ctx.waitTicks(40);
		s.runCommand("fill -10 199 -4 10 199 6 matriochka:lacquer_block");
		s.runCommand("fill -10 200 -4 10 206 6 minecraft:air");
		int i = 0;
		for (Defs.BlockDef b : Content.BLOCKS) {
			if (!b.kind().equals("station")) continue;
			int x = -9 + (i % 7) * 3, z = 2 + (i / 7) * 3;
			s.runCommand("setblock " + x + " 200 " + z + " matriochka:" + b.id());
			i++;
		}
		s.runCommand("setblock -3 200 -2 matriochka:world_block");
		s.runCommand("setblock 0 200 -2 matriochka:threshold");
		s.runCommand("setblock 3 200 -2 matriochka:world_soil_3");
		s.runCommand("tp @p 0 205 -9 0 30");
		ctx.waitTicks(60);
		sp.getConnection().waitForChunksRender();
		shot(ctx, "vis_stations");
		s.runCommand("time set 18000");
		ctx.waitTicks(40);
		shot(ctx, "vis_stations_night");
		s.runCommand("time set 6000");
	}

	/** A wall of item frames holding the hand-painted items. */
	private static void frames(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		int cols = 14;
		s.runCommand("fill -8 210 20 8 217 20 minecraft:dark_oak_planks");
		s.runCommand("fill -8 210 19 8 217 10 minecraft:air");
		for (int n = 0; n < FRAMED.length; n++) {
			int x = 6 - (n % cols), y = 216 - n / cols;
			s.runCommand("summon item_frame " + x + " " + y + " 19 {Facing:2b,Fixed:1b,Item:{id:\"matriochka:" + FRAMED[n] + "\",count:1}}");
		}
		s.runCommand("tp @p 0 213.5 12 180 0");
		ctx.waitTicks(60);
		sp.getConnection().waitForChunksRender();
		shot(ctx, "vis_frames");
	}

	/** The same items in the player's inventory. */
	private static void inventory(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		for (int n = 0; n < Math.min(36, FRAMED.length); n++) s.runCommand("give @p matriochka:" + FRAMED[n]);
		ctx.waitTicks(10);
		ctx.setScreen(() -> new net.minecraft.client.gui.screens.inventory.InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
		ctx.waitTicks(10);
		ctx.takeScreenshot(TestScreenshotOptions.of("vis_inventory").withSize(1920, 1080).disableCounterPrefix());
		ctx.setScreen(() -> null);
		s.runCommand("clear @a");
		for (int n = 36; n < FRAMED.length; n++) s.runCommand("give @p matriochka:" + FRAMED[n]);
		ctx.waitTicks(10);
		ctx.setScreen(() -> new net.minecraft.client.gui.screens.inventory.InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
		ctx.waitTicks(10);
		ctx.takeScreenshot(TestScreenshotOptions.of("vis_inventory_2").withSize(1920, 1080).disableCounterPrefix());
		ctx.setScreen(() -> null);
		s.runCommand("gamemode creative @a");
	}

	/** Every new particle, sprayed in front of the camera against a dark wall, by night so the glowing ones show. */
	private static void particles(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("time set 18000");
		s.runCommand("fill -6 220 8 6 230 8 minecraft:black_concrete");
		s.runCommand("tp @p 0 224 0 0 0");
		ctx.waitTicks(40);
		for (var type : Particles.STYLES.keySet()) {
			String id = BuiltInRegistries.PARTICLE_TYPE.getKey(type).toString();
			for (int k = 0; k < 6; k++) {
				s.runCommand("particle " + id + " 0 225 4 1.2 1.2 0.3 0.02 30 force");
				ctx.waitTicks(4);
			}
			shot(ctx, "vis_particle_" + id.substring(id.indexOf(':') + 1));
			ctx.waitTicks(60);
		}
		s.runCommand("time set 6000");
	}
}
