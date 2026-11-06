package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.net.Net;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;

/**
 * Per-player persistent state (karma, souls, gauges, quests, pages, dolls), stored as a compound tag attachment
 * that survives death. Gauges are 0..100 floats.
 */
public final class PlayerState {
	public static final AttachmentType<CompoundTag> TYPE = AttachmentRegistry.<CompoundTag>builder()
		.persistent(CompoundTag.CODEC)
		.copyOnDeath()
		.initializer(CompoundTag::new)
		.buildAndRegister(Matriochka.id("player_state"));

	private final ServerPlayer player;
	private final CompoundTag tag;

	private PlayerState(ServerPlayer player) {
		this.player = player;
		this.tag = player.getAttachedOrCreate(TYPE);
	}

	public static PlayerState of(ServerPlayer player) {
		return new PlayerState(player);
	}

	public static void init() {}

	public CompoundTag tag() {
		return tag;
	}

	private void save() {
		player.setAttached(TYPE, tag);
	}

	// ------------------------------------------------------------- karma and souls
	public int karma() {
		return tag.getIntOr("karma", 0);
	}

	public void addKarma(int delta) {
		// the Absorb ending: whoever took the creature's hunger can no longer climb back
		if (delta > 0 && has("end_absorb")) return;
		if (!fr.achedon12.matriochka.world.Config.karma()) return;
		tag.putInt("karma", Math.max(-100, Math.min(100, karma() + delta)));
		save();
		sync();
	}

	public int souls() {
		return tag.getIntOr("souls", 0);
	}

	public boolean spendSouls(int n) {
		if (souls() < n) return false;
		tag.putInt("souls", souls() - n);
		save();
		sync();
		return true;
	}

	/** A soul gain from play: scaled by the server's soulGainMultiplier. */
	public void addSouls(int n) {
		int gain = fr.achedon12.matriochka.world.Config.souls(n);
		if (gain > 0) fr.achedon12.matriochka.world.CycleStats.add(player, "souls", gain);
		setSouls(souls() + gain);
	}

	/** Sets the souls as given, unscaled (administrator command). */
	public void setSouls(int n) {
		tag.putInt("souls", Math.max(0, n));
		save();
		sync();
	}

	// ------------------------------------------------------------- gauges
	public float gauge(String name) {
		return tag.getFloatOr("g_" + name, name.equals("oxygen") ? 100f : 0f);
	}

	public void setGauge(String name, float value) {
		tag.putFloat("g_" + name, Math.max(0, Math.min(100, value)));
		save();
	}

	public void addGauge(String name, float delta) {
		setGauge(name, gauge(name) + delta);
	}

	public long flagTime(String name) {
		return tag.getLongOr("t_" + name, 0L);
	}

	public void setFlagTime(String name, long until) {
		tag.putLong("t_" + name, until);
		save();
	}

	public boolean flagActive(String name, long now) {
		return flagTime(name) > now;
	}

	// ------------------------------------------------------------- doll of life
	public int dollLayers() {
		return tag.getIntOr("doll_layers", 0);
	}

	public int dollMax() {
		return tag.getIntOr("doll_max", 0);
	}

	public void setDoll(int layers, int max) {
		int now = Math.max(0, Math.min(max, layers));
		// a layer put back (Soul Altar, a fallen boss) counts in the cycle's recap
		if (now > dollLayers()) fr.achedon12.matriochka.world.CycleStats.add(player, "rebuilt", now - dollLayers());
		tag.putInt("doll_layers", now);
		tag.putInt("doll_max", max);
		save();
		sync();
	}

	// ------------------------------------------------------------- generic flags & counters
	public boolean has(String key) {
		return tag.getBooleanOr("f_" + key, false);
	}

	public void set(String key, boolean v) {
		tag.putBoolean("f_" + key, v);
		save();
	}

	public int counter(String key) {
		return tag.getIntOr("c_" + key, 0);
	}

	public void addCounter(String key, int d) {
		tag.putInt("c_" + key, counter(key) + d);
		save();
	}

	/** Quest progress hook: kind (kill/craft/obtain/use/deliver...), target id, amount. */
	public void progress(String kind, String target, int amount) {
		addCounter(kind + ":" + target, amount);
		fr.achedon12.matriochka.world.Quests.onProgress(player, kind, target);
	}

	public int pages(int world) {
		return Integer.bitCount(tag.getIntOr("pages_" + world, 0));
	}

	public boolean addPage(int world, int index) {
		int bits = tag.getIntOr("pages_" + world, 0);
		if ((bits & (1 << index)) != 0) return false;
		tag.putInt("pages_" + world, bits | (1 << index));
		fr.achedon12.matriochka.world.CycleStats.add(player, "pages", 1);
		save();
		return true;
	}

	public void sync() {
		Net.syncState(player, this);
	}
}
