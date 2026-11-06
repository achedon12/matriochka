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
 * vis_world_N (the light, fog and particles of every world, at noon and at night for World 8's seasons; World 5 around
 * a few lanterns, World 0 in its entry hall and vis_world_0_cavern from the cavern), vis_stations
 * (the thirteen stations side by side, lit and in the dark), vis_frames (an item frame wall of the hand-painted
 * items), vis_inventory (the same items in the inventory) and vis_particle_ID (every new particle in front of the
 * camera, half on black, half on white). -Pworlds=0,5,p retakes only those worlds (p: the particles).
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

	/** The worlds to retake (-Pworlds=0,5,p), empty for the whole run. */
	private static final String ONLY = System.getProperty("matriochka.worlds", "");

	private static boolean picked(String w) {
		return ONLY.isEmpty() || ("," + ONLY + ",").contains("," + w + ",");
	}

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
			if (!ONLY.isEmpty()) {
				// -Pworlds=0,5 retakes only those worlds (and the particles with p)
				if (picked("p")) particles(ctx, sp);
				return;
			}
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
			if (!picked(String.valueOf(w))) continue;
			s.runCommand("gamemode creative @a");
			s.runCommand("execute as @p run matriochka world enter " + w);
			ctx.setScreen(() -> null);
			ctx.waitTicks(120);
			sp.getConnection().waitForChunksRender();
			s.runCommand("gamemode spectator @a");
			if (w == 5) {
				// the Deep has no light of its own: show it the way a player sees it, around a few lanterns they set down
				lanterns(s);
				s.runCommand("execute as @p at @s run tp @s ~ ~3 ~ 35 24");
			} else {
				s.runCommand("execute as @p at @s run tp @s ~ ~6 ~ 35 12");
			}
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
		// World 0: inside the smallest doll, the way a player arrives (the entry hall, looking toward the chambers), then
		// a spectator glance over the raw cavern around it
		if (!picked("0")) return;
		s.runCommand("gamemode creative @a");
		s.runCommand("execute as @p run matriochka world zero");
		ctx.setScreen(() -> null);
		ctx.waitTicks(120);
		sp.getConnection().waitForChunksRender();
		s.runCommand("gamemode spectator @a");
		s.runCommand("execute as @p at @s run tp @s ~ ~2.2 ~-3.5 0 10");
		ctx.waitTicks(60);
		shot(ctx, "vis_world_0");
		s.runCommand("execute in matriochka:world_zero run tp @p 0 70 0 45 15");
		ctx.waitTicks(120);
		sp.getConnection().waitForChunksRender();
		shot(ctx, "vis_world_0_cavern");
		s.runCommand("execute in minecraft:overworld run tp @p 0 120 0");
		ctx.waitTicks(60);
	}

	/**
	 * Sets lanterns on the ground in front of the player (looking 35 degrees west of south), a few blocks apart, and
	 * one of the Deep's own Faint Glows: the lit patches World 5's atmosphere is about.
	 */
	private static void lanterns(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s) {
		s.runOnServer(server -> {
			var p = server.getPlayerList().getPlayers().get(0);
			var lvl = p.level();
			double yaw = Math.toRadians(35);
			double fx = -Math.sin(yaw), fz = Math.cos(yaw);
			int[][] spots = {{4, 0}, {7, -3}, {9, 3}, {13, -1}, {17, 4}, {21, -4}};
			for (int i = 0; i < spots.length; i++) {
				double ahead = spots[i][0], side = spots[i][1];
				int x = (int) Math.floor(p.getX() + fx * ahead - fz * side), z = (int) Math.floor(p.getZ() + fz * ahead + fx * side);
				for (int y = p.getBlockY() + 4; y > p.getBlockY() - 14; y--) {
					var at = new net.minecraft.core.BlockPos(x, y, z);
					if (lvl.getBlockState(at).isSolidRender() && lvl.getBlockState(at.above()).isAir()) {
						var light = i == 3 ? fr.achedon12.matriochka.content.ModContent.block("faint_glow").defaultBlockState()
							: net.minecraft.world.level.block.Blocks.LANTERN.defaultBlockState();
						lvl.setBlock(at.above(), light, 3);
						break;
					}
				}
			}
		});
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

	/**
	 * Every new particle, one shot each: a dense burst a couple of blocks in front of the camera, by day so the unlit
	 * ones are lit, in front of a wall split in two (black on the left for the bright and glowing ones, white on the
	 * right for the dark ones). The camera is a spectator, so it hangs where it is put. Each burst is shot after a few
	 * ticks, well inside the shortest life (the storm spark lives 5 to 11 ticks).
	 */
	private static void particles(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("time set 6000");
		s.runCommand("gamemode spectator @a");
		s.runCommand("fill -6 218 4 6 230 12 minecraft:air");
		s.runCommand("fill -6 218 5 -1 230 5 minecraft:black_concrete");
		s.runCommand("fill 0 218 5 6 230 5 minecraft:white_concrete");
		s.runCommand("tp @p 0.5 223.4 1.0 0 0");
		ctx.waitTicks(40);
		sp.getConnection().waitForChunksRender();
		for (var entry : Particles.STYLES.entrySet()) {
			var type = entry.getKey();
			int life = entry.getValue().lifeMin();
			String id = BuiltInRegistries.PARTICLE_TYPE.getKey(type).toString();
			s.runCommand("tp @p 0.5 223.4 1.0 0 0");
			// a few overlapping bursts so the shot catches several frames of the animation, the last one fresh
			int gap = Math.max(1, Math.min(4, life / 4));
			for (int k = 0; k < 4; k++) {
				s.runCommand("particle " + id + " 0.5 225.0 3.2 0.9 0.5 0.15 0.004 40 force");
				ctx.waitTicks(gap);
			}
			shot(ctx, "vis_particle_" + id.substring(id.indexOf(':') + 1));
			ctx.waitTicks(Math.min(80, entry.getValue().lifeMax() + 5));
		}
	}
}
