package fr.achedon12.matriochka.content;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Station recipes. Ingredients are taken from the player's inventory; ids without namespace are Matriochka items. */
public final class Recipes {
	public record Ing(String id, int count) {}

	/** world > 0 means: the group must have defeated the boss of world (world - 1) to use it (Seeds). */
	public record Recipe(String station, String output, int count, List<Ing> inputs, int requiresDefeated) {}

	public static final Map<String, List<Recipe>> BY_STATION = new LinkedHashMap<>();

	private Recipes() {}

	private static void r(String station, String out, int count, int requires, Object... in) {
		List<Ing> ings = new ArrayList<>();
		for (int i = 0; i < in.length; i += 2) ings.add(new Ing((String) in[i], (Integer) in[i + 1]));
		BY_STATION.computeIfAbsent(station, k -> new ArrayList<>()).add(new Recipe(station, out, count, ings, requires));
	}

	private static void gear(String station, int world, String weapon, String set, String res) {
		r(station, weapon, 1, -1, res, 8, "minecraft:stick", 1);
		r(station, set + "_helmet", 1, -1, res, 5);
		r(station, set + "_chestplate", 1, -1, res, 8);
		r(station, set + "_leggings", 1, -1, res, 7);
		r(station, set + "_boots", 1, -1, res, 4);
	}

	static {
		String W = "matrix_workbench";
		// Seeds: core of the previous boss + resources, as in the design document
		r(W, "seed_1", 1, 0, "guardian_core", 1, "minecraft:iron_ingot", 16, "minecraft:oak_log", 16);
		r(W, "seed_2", 1, 1, "queen_core", 1, "sporite", 8, "spores", 16);
		r(W, "seed_3", 1, 2, "titan_core", 1, "ash_ingot", 8, "blazing_rock", 16);
		r(W, "seed_4", 1, 3, "jailer_core", 1, "dungeon_key", 8, "sealed_fragment", 8);
		r(W, "seed_5", 1, 4, "storm_king_core", 1, "storm_essence", 8, "celestial_crystal", 8);
		r(W, "seed_6", 1, 5, "light_eater_core", 1, "shadow_shard", 8, "diamond_fragment", 4);
		r(W, "seed_7", 1, 6, "double_core", 1, "unstable_alloy", 8, "inverted_crystal", 4);
		r(W, "seed_8", 1, 7, "leviathan_core", 1, "pressure_pearl", 4, "abyssal_salt", 8);
		r(W, "seed_9", 1, 8, "seasons_core", 1, "temporal_sand", 8, "season_fragment", 4);
		r(W, "seed_10", 1, 9, "terrain_core", 1, "terrain_heart", 1, "last_doll_key", 1);
		r(W, "soul_cradle", 1, -1, "minecraft:oak_planks", 4, "wool_thread", 1, "roots", 2);
		r(W, "wool_thread", 4, -1, "minecraft:white_wool", 1);
		r(W, "return_thread", 2, -1, "wool_thread", 2, "minecraft:ender_pearl", 1);
		r(W, "chance_doll", 1, -1, "minecraft:oak_planks", 2, "minecraft:red_dye", 1, "minecraft:gold_ingot", 2);
		r(W, "artisan_scroll", 1, -1, "minecraft:paper", 3);
		r(W, "class_table", 1, 0, "minecraft:smithing_table", 1, "minecraft:iron_ingot", 6);
		r(W, "soul_altar", 1, 0, "minecraft:crying_obsidian", 4, "minecraft:gold_ingot", 4);
		r(W, "nesting_chest", 1, 2, "minecraft:chest", 2, "ash_ingot", 2);
		r(W, "nesting_chest_medium", 1, 2, "minecraft:chest", 1, "ash_ingot", 1);
		r(W, "nesting_chest_little", 2, 2, "minecraft:chest", 1, "wool_thread", 2);
		r(W, "refuge_doll", 1, 3, "painted_wood", 8, "sealed_fragment", 4, "minecraft:gold_ingot", 2);
		r(W, "painted_wood", 8, -1, "minecraft:oak_planks", 8, "minecraft:red_dye", 1);
		r(W, "lacquer_block", 4, -1, "painted_wood", 4, "minecraft:honeycomb", 1);
		r(W, "spore_vat", 1, 0, "minecraft:cauldron", 1, "minecraft:iron_ingot", 4);
		r(W, "ash_foundry", 1, 1, "minecraft:blast_furnace", 1, "sporite", 4, "chitin", 2);
		r(W, "jailer_table", 1, 2, "minecraft:smithing_table", 1, "ash_ingot", 4);
		r(W, "lightning_forge", 1, 3, "minecraft:lightning_rod", 2, "ash_ingot", 4, "sealed_fragment", 4);
		r(W, "dark_altar", 1, 4, "minecraft:obsidian", 4, "celestial_crystal", 4, "storm_essence", 2);
		r(W, "inverter", 1, 5, "minecraft:observer", 2, "shadow_shard", 6);
		r(W, "abyssal_press", 1, 6, "minecraft:piston", 2, "unstable_alloy", 6, "inverted_crystal", 1);
		r(W, "time_workshop", 1, 7, "minecraft:clock", 2, "abyssal_salt", 6, "pressure_pearl", 1);
		r(W, "terrain_anchor", 1, 8, "minecraft:anvil", 1, "temporal_sand", 8, "season_fragment", 1);
		r(W, "final_loom", 1, 9, "minecraft:loom", 1, "terrain_fragment", 8, "terrain_heart", 1);
		for (int i = 0; i < 10; i++) r(W, "world_soil_" + i, 4, i, "minecraft:dirt", 4, i == 0 ? "minecraft:bone_meal" : "spores", 1);

		// World 1
		r("spore_vat", "antidote", 2, -1, "spores", 4, "minecraft:glass_bottle", 2);
		r("spore_vat", "filter_mask", 1, -1, "chitin", 2, "spores", 8, "minecraft:string", 2);
		r("spore_vat", "root_broth", 2, -1, "roots", 3, "minecraft:bowl", 2);
		gear("spore_vat", 1, "sporite_sword", "chitin", "chitin");
		r("spore_vat", "sporite_sword", 1, -1, "sporite", 8, "roots", 1);
		// World 2
		r("ash_foundry", "ash_ingot", 1, -1, "giant_ore", 1, "blazing_rock", 1);
		r("ash_foundry", "cooling_water", 2, -1, "minecraft:ice", 2, "minecraft:glass_bottle", 2);
		r("ash_foundry", "drill", 1, -1, "ash_ingot", 6, "blazing_rock", 4, "minecraft:redstone", 4);
		r("ash_foundry", "ice_bread", 2, -1, "minecraft:bread", 2, "minecraft:ice", 1);
		gear("ash_foundry", 2, "ash_hammer", "thermal", "ash_ingot");
		// World 3
		r("jailer_table", "labyrinth_map", 1, -1, "minecraft:paper", 4, "sealed_fragment", 1);
		r("jailer_table", "lockpick_kit", 2, -1, "minecraft:iron_nugget", 4, "sealed_fragment", 1);
		r("jailer_table", "portable_trap", 2, -1, "minecraft:iron_ingot", 2, "sealed_fragment", 1);
		r("jailer_table", "dungeon_key", 1, -1, "sealed_fragment", 3, "minecraft:gold_nugget", 4);
		r("jailer_table", "cell_ration", 2, -1, "minecraft:bread", 1, "minecraft:cooked_beef", 1);
		gear("jailer_table", 3, "jailer_blade", "jailer", "sealed_fragment");
		r("jailer_table", "sealed_shackle", 1, -1, "sealed_fragment", 6, "dungeon_key", 1, "minecraft:iron_chain", 2);
		// World 4
		r("lightning_forge", "glider", 1, -1, "ray_membrane", 8, "minecraft:stick", 4, "storm_essence", 2);
		r("lightning_forge", "grappling_hook", 1, -1, "celestial_crystal", 2, "minecraft:string", 8, "minecraft:iron_ingot", 3);
		r("lightning_forge", "cloud_fruit", 2, -1, "minecraft:apple", 2, "storm_essence", 1);
		r("lightning_forge", "armor_layer", 2, -1, "celestial_crystal", 1, "storm_essence", 1, "minecraft:honeycomb", 2);
		gear("lightning_forge", 4, "lightning_lance", "celestial", "celestial_crystal");
		r("lightning_forge", "storm_censer", 1, -1, "storm_essence", 4, "celestial_crystal", 2, "ray_membrane", 2);
		// World 5
		r("dark_altar", "solar_lantern", 1, -1, "storm_essence", 4, "minecraft:lantern", 1, "minecraft:gold_ingot", 2);
		r("dark_altar", "sonar", 1, -1, "shadow_shard", 4, "minecraft:amethyst_shard", 2);
		r("dark_altar", "silence_balm", 3, -1, "shadow_shard", 1, "minecraft:honey_bottle", 1);
		r("dark_altar", "minecraft:diamond", 1, -1, "diamond_fragment", 4);
		r("dark_altar", "mute_mushroom", 2, -1, "minecraft:brown_mushroom", 2, "shadow_shard", 1);
		gear("dark_altar", 5, "shadow_blade", "nocturnal", "shadow_shard");
		// World 6
		r("inverter", "gravity_boots", 1, -1, "unstable_alloy", 6, "inverted_crystal", 2);
		r("inverter", "stabilizer", 3, -1, "unstable_alloy", 1, "minecraft:quartz", 2);
		r("inverter", "flipped_apple", 2, -1, "minecraft:apple", 2, "inverted_crystal", 1);
		gear("inverter", 6, "mirror_blade", "mirror", "unstable_alloy");
		// World 7
		r("abyssal_press", "oxygen_capsule", 3, -1, "minecraft:kelp", 4, "abyssal_salt", 1);
		r("abyssal_press", "thruster", 1, -1, "pressure_pearl", 2, "unstable_alloy", 4);
		r("abyssal_press", "pressure_pearl", 1, -1, "abyssal_salt", 6, "minecraft:prismarine_crystals", 2);
		r("abyssal_press", "apnea_kelp", 3, -1, "minecraft:dried_kelp", 3, "abyssal_salt", 1);
		gear("abyssal_press", 7, "trench_trident", "diving", "abyssal_salt");
		// World 8
		r("time_workshop", "hourglass", 1, -1, "temporal_sand", 6, "minecraft:glass", 2, "season_fragment", 1);
		r("time_workshop", "season_preserve", 3, -1, "season_fragment", 1, "minecraft:glass_bottle", 3);
		r("time_workshop", "season_jam", 2, -1, "minecraft:sweet_berries", 4, "temporal_sand", 1);
		gear("time_workshop", 8, "season_scythe", "seasonal", "temporal_sand");
		r("time_workshop", "wreath_of_seasons", 1, -1, "season_fragment", 2, "temporal_sand", 6, "season_preserve", 1);
		// World 9
		r("terrain_anchor", "anchor", 4, -1, "terrain_fragment", 2, "minecraft:iron_ingot", 2);
		r("terrain_anchor", "grip_boots", 1, -1, "terrain_fragment", 6, "minecraft:leather_boots", 1);
		r("terrain_anchor", "anchor_bread", 2, -1, "minecraft:bread", 2, "terrain_fragment", 1);
		gear("terrain_anchor", 9, "seismic_mace", "living_rock", "terrain_fragment");
		// World 10
		r("final_loom", "artisan_blade", 1, -1, "artisan_thread", 8, "artisan_shard", 1, "sporite_sword", 1);
		r("final_loom", "artisan_helmet", 1, -1, "artisan_thread", 5, "chitin_helmet", 1);
		r("final_loom", "artisan_chestplate", 1, -1, "artisan_thread", 8, "celestial_chestplate", 1);
		r("final_loom", "artisan_leggings", 1, -1, "artisan_thread", 7, "diving_leggings", 1);
		r("final_loom", "artisan_boots", 1, -1, "artisan_thread", 4, "gravity_boots", 1);
		r("final_loom", "unfinished_effigy", 1, -1, "artisan_thread", 6, "artisan_shard", 1, "wool_thread", 4);
		r("final_loom", "workshop_feast", 1, -1, "root_broth", 1, "ice_bread", 1, "cloud_fruit", 1, "season_jam", 1);
	}

	public static List<Recipe> of(String station) {
		return BY_STATION.getOrDefault(station, List.of());
	}
}
