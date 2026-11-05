package fr.achedon12.matriochka.entity;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.HastenedClock;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.WorldRules;
import fr.achedon12.matriochka.world.Achievements;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;

/**
 * What each player did during one boss fight, for the "beat the boss without..." achievements.
 * A fight starts when a player first comes within reach of the boss and ends with its death.
 */
public final class BossFeats {
	private static final Set<String> GEAR = Set.of("weapon", "armor", "boots", "mask", "glider", "hook", "lantern", "sonar", "drill",
		"thruster", "anchor", "hourglass", "tool");
	private static Map<String, Integer> gearWorld;

	private final Map<UUID, Set<String>> flags = new HashMap<>();
	private final Map<UUID, Integer> seasons = new HashMap<>();
	private final Map<UUID, Integer> gear = new HashMap<>();
	private final Map<UUID, List<String>> loadouts = new HashMap<>();

	/** Every ten ticks: watch the players around the boss. */
	void watch(MatrioBoss boss, ServerLevel level) {
		String id = boss.def.id();
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, boss.getBoundingBox().inflate(48))) {
			if (p.isSpectator()) continue;
			Set<String> f = flags.computeIfAbsent(p.getUUID(), k -> new HashSet<>());
			switch (id) {
				case "spore_queen" -> { if (p.getItemBySlot(EquipmentSlot.HEAD).is(ModContent.item("filter_mask"))) f.add("mask"); }
				case "ash_titan" -> { if (p.isInLava()) f.add("lava"); }
				case "light_eater" -> { if (holdsLight(p)) f.add("light"); }
				case "your_double" -> {
					List<String> l = loadouts.computeIfAbsent(p.getUUID(), k -> new ArrayList<>());
					while (l.size() <= boss.phase()) l.add(null);
					String sig = loadout(p);
					// the gear that counts for a phase is the one worn at its end
					l.set(boss.phase(), sig);
				}
				case "terrain_heart_boss" -> { if (WorldRules.anchoredNow(level, p)) f.add("anchor"); }
				case "the_unfinished" -> gear.merge(p.getUUID(), gearBits(p), (a, b) -> a | b);
				default -> {}
			}
		}
	}

	/** A player hit the boss. */
	void hit(MatrioBoss boss, ServerLevel level, ServerPlayer p) {
		if (boss.def.id().equals("seasons_master")) seasons.merge(p.getUUID(), 1 << HastenedClock.season(level), (a, b) -> a | b);
		if (boss.def.id().equals("the_unfinished")) gear.merge(p.getUUID(), gearBits(p), (a, b) -> a | b);
	}

	/** Something happened to a player near the boss: struck by lightning, died. */
	void mark(ServerPlayer p, String flag) {
		flags.computeIfAbsent(p.getUUID(), k -> new HashSet<>()).add(flag);
	}

	/** The boss died: grant what each player earned. */
	void award(MatrioBoss boss, ServerLevel level, List<ServerPlayer> players) {
		String id = boss.def.id();
		for (ServerPlayer p : players) {
			Set<String> f = flags.getOrDefault(p.getUUID(), Set.of());
			switch (id) {
				case "spore_queen" -> { if (!f.contains("mask")) Achievements.grant(p, "queen_no_mask"); }
				case "ash_titan" -> { if (!f.contains("lava")) Achievements.grant(p, "titan_no_lava"); }
				case "storm_king" -> { if (!f.contains("bolt")) Achievements.grant(p, "king_no_bolt"); }
				case "light_eater" -> { if (!f.contains("light")) Achievements.grant(p, "eater_no_light"); }
				case "your_double" -> {
					List<String> l = loadouts.getOrDefault(p.getUUID(), List.of());
					Set<String> seen = new HashSet<>();
					boolean distinct = l.size() >= 2;
					for (String s : l) if (s == null || !seen.add(s)) distinct = false;
					if (distinct) Achievements.grant(p, "double_swap");
				}
				case "pressure_leviathan" -> { if (fr.achedon12.matriochka.rules.Snorkel.airPercent(p) < 5f) Achievements.grant(p, "levi_low_o2"); }
				case "seasons_master" -> { if (seasons.getOrDefault(p.getUUID(), 0) == 0b1111) Achievements.grant(p, "master_four"); }
				case "terrain_heart_boss" -> { if (!f.contains("anchor")) Achievements.grant(p, "heart_no_anchor"); }
				case "the_unfinished" -> {
					if (!f.contains("died")) Achievements.grant(p, "ten_shells");
					if (gear.getOrDefault(p.getUUID(), 0) == 0b11111111110) Achievements.grant(p, "all_gear");
					// "Set Down the Tools" (third_end) is no longer earned here: it is the third ending, in World 0
				}
				default -> {}
			}
		}
	}

	private static boolean holdsLight(ServerPlayer p) {
		for (ItemStack s : List.of(p.getMainHandItem(), p.getOffhandItem())) {
			if (s.is(ModContent.item("solar_lantern"))) return true;
			if (s.getItem() instanceof BlockItem bi && bi.getBlock().defaultBlockState().getLightEmission() > 0) return true;
		}
		return false;
	}

	private static String loadout(ServerPlayer p) {
		StringBuilder b = new StringBuilder();
		for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.MAINHAND, EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
			b.append(BuiltInRegistries.ITEM.getKey(p.getItemBySlot(s).getItem())).append(';');
		}
		return b.toString();
	}

	/** Bit n is set when the player holds or wears gear from world n. */
	private static int gearBits(ServerPlayer p) {
		if (gearWorld == null) {
			Map<String, Integer> m = new HashMap<>();
			for (Defs.ItemDef d : Content.ITEMS) if (GEAR.contains(d.kind()) && d.world() > 0) m.put(d.id(), d.world());
			gearWorld = m;
		}
		int bits = 0;
		for (EquipmentSlot s : EquipmentSlot.values()) {
			var key = BuiltInRegistries.ITEM.getKey(p.getItemBySlot(s).getItem());
			if (!key.getNamespace().equals("matriochka")) continue;
			Integer w = gearWorld.get(key.getPath());
			if (w != null) bits |= 1 << w;
		}
		return bits;
	}

	/** Mark a player for the fight of every boss near them. */
	public static void markNear(ServerPlayer p, String flag) {
		if (!(p.level() instanceof ServerLevel level)) return;
		for (MatrioBoss b : level.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(64))) b.feats().mark(p, flag);
	}
}
