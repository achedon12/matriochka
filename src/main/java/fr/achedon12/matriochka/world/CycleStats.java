package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.HashMap;
import java.util.Map;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;

/**
 * What a player does during one cycle, for the recap shown after an ending. The counters live in the player's state
 * ("cycle_stats", synced with it, saved, cleared when the player catches up with a New Cycle); reaching an ending
 * copies them, with what the group achieved, into "last_cycle", which stays until the next ending.
 * <ul>
 * <li>ticks: time played in the cycle (counted while online);</li>
 * <li>deaths, lost, rebuilt: real deaths, Doll of Life layers broken and layers put back;</li>
 * <li>souls, pages, quests, dolls: souls gathered, Journal pages and quests found and done in the cycle, hidden dolls
 * carried at once;</li>
 * <li>worlds, bosses: bitmasks of the worlds entered and the bosses beaten by the player (world 0 is the Guardian);</li>
 * <li>trial_&lt;key&gt;: the best time of each Trial run in the cycle, in ticks.</li>
 * </ul>
 */
public final class CycleStats {
	public static final String KEY = "cycle_stats", LAST = "last_cycle";
	private static final int TICK_STEP = 20;

	private CycleStats() {}

	public static void init() {
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (server.overworld().getGameTime() % TICK_STEP != 0) return;
			for (ServerPlayer p : server.getPlayerList().getPlayers()) add(p, "ticks", TICK_STEP);
		});
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (entity instanceof ServerPlayer p) add(p, "deaths", 1);
		});
	}

	/** The player's counters for the current cycle, created on first use. */
	public static CompoundTag of(PlayerState ps) {
		CompoundTag t = ps.tag();
		if (!(t.get(KEY) instanceof CompoundTag c)) {
			CompoundTag fresh = new CompoundTag();
			t.put(KEY, fresh);
			return fresh;
		}
		return c;
	}

	public static void add(ServerPlayer p, String stat, int n) {
		if (n == 0) return;
		CompoundTag c = of(PlayerState.of(p));
		c.putInt(stat, c.getIntOr(stat, 0) + n);
	}

	public static void bit(ServerPlayer p, String stat, int bit) {
		if (bit < 0 || bit > 30) return;
		CompoundTag c = of(PlayerState.of(p));
		c.putInt(stat, c.getIntOr(stat, 0) | (1 << bit));
	}

	public static void max(ServerPlayer p, String stat, int value) {
		CompoundTag c = of(PlayerState.of(p));
		if (value > c.getIntOr(stat, 0)) c.putInt(stat, value);
	}

	/** Keeps the fastest time of a Trial run in this cycle. */
	public static void trial(ServerPlayer p, String key, int ticks) {
		CompoundTag c = of(PlayerState.of(p));
		String k = "trial_" + key;
		int had = c.getIntOr(k, 0);
		if (had == 0 || ticks < had) c.putInt(k, ticks);
	}

	/** A New Cycle begins for this player: the counters start again, the last recap stays. */
	public static void reset(PlayerState ps) {
		ps.tag().remove(KEY);
	}

	/**
	 * An ending is reached: writes the recap of the cycle (the counters, the karma reached, the group's progression,
	 * the class worn and the best Trial times) into "last_cycle".
	 */
	public static void snapshot(ServerPlayer p, String ending, boolean first) {
		PlayerState ps = PlayerState.of(p);
		CompoundTag c = of(ps);
		CompoundTag r = c.copy();
		MatrioData data = MatrioData.get(p.level().getServer());
		String group = data.groupOf(p.getUUID());
		r.putString("ending", ending);
		r.putBoolean("first", first);
		r.putInt("cycle", Cycles.of(data, group));
		r.putInt("karma", ps.karma());
		r.putInt("souls_held", ps.souls());
		r.putInt("members", data.members(group).size());
		int done = data.group(group).getIntOr("done", 0);
		r.putInt("group_bosses", done);
		// the worlds opened: entered by the player, a World Block the group placed, or a world whose boss fell
		int opened = c.getIntOr("worlds", 0);
		CompoundTag worlds = data.group(group).getCompoundOrEmpty("worlds");
		for (int w = 1; w <= 10; w++) if (worlds.getCompoundOrEmpty(Integer.toString(w)).contains("block_pos")) opened |= 1 << w;
		for (int w = 1; w <= 10; w++) if ((done & (1 << w)) != 0) opened |= 1 << w;
		r.putInt("worlds", opened);
		int pagesTotal = 0;
		for (int w = 1; w <= 10; w++) pagesTotal += ps.pages(w);
		r.putInt("pages_total", pagesTotal);
		int questsTotal = 0;
		for (var q : fr.achedon12.matriochka.content.Content.QUESTS) if (ps.has("quest_" + q.id())) questsTotal++;
		r.putInt("quests_total", questsTotal);
		r.putInt("quests_all", fr.achedon12.matriochka.content.Content.QUESTS.size());
		gear(p, r);
		ListTag trials = new ListTag();
		for (ReplayContent.TrialDef d : ReplayContent.TRIALS) {
			int t = c.getIntOr("trial_" + d.key(), 0);
			if (t <= 0) continue;
			CompoundTag e = new CompoundTag();
			e.putString("key", d.key());
			e.putInt("ticks", t);
			trials.add(e);
		}
		r.put("trials", trials);
		r.putString("name", p.getGameProfile().name());
		ps.tag().put(LAST, r);
	}

	/** The class most of the worn and held gear belongs to, and the highest class level among those pieces. */
	private static void gear(ServerPlayer p, CompoundTag r) {
		Map<String, Integer> count = new HashMap<>(), level = new HashMap<>();
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			ItemStack s = p.getItemBySlot(slot);
			GearClasses.Gear g = s.get(GearClasses.GEAR);
			if (g == null) continue;
			count.merge(g.cls(), 1, Integer::sum);
			level.merge(g.cls(), g.level(), Math::max);
		}
		String best = "";
		for (var e : count.entrySet()) {
			if (best.isEmpty() || e.getValue() > count.get(best) || (e.getValue().equals(count.get(best)) && level.get(e.getKey()) > level.get(best))) best = e.getKey();
		}
		r.putString("cls", best);
		r.putInt("gear", best.isEmpty() ? 0 : level.get(best));
		r.putInt("pieces", best.isEmpty() ? 0 : count.get(best));
	}
}
