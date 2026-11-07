package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Sounds;
import fr.achedon12.matriochka.mixin.client.BossHealthOverlayAccess;
import fr.achedon12.matriochka.mixin.client.MusicManagerAccess;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.sounds.Music;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;

/**
 * The adaptive music. The world themes come from the biomes (tools/sound.py) and the game plays them as usual while
 * exploring. On top of that, a small state machine follows what happens:
 * <ul>
 * <li>DANGER while creatures hunt the player (the server counts them, net/Cues), held a few seconds after;</li>
 * <li>BOSS while a Matriochka boss bar is shown, BOSS_FINAL below a third of its health;</li>
 * <li>a heartbeat layer that swells with low health or low breath, the theme ducking under it;</li>
 * <li>a short sting when a structure, a Journal page or a quest is done.</li>
 * </ul>
 * Changing state fades the playing theme out before the next one fades in: never two themes at once. Every part
 * plays in the music category (the game's music slider) and has its own slider in the comfort options.
 */
public final class MusicThemes {
	private MusicThemes() {}

	public enum State { NONE, EXPLORE, DANGER, BOSS, BOSS_FINAL }

	/** Replaces whatever plays, starts at once and starts again as soon as it ends. */
	private static Music now(SoundEvent e) {
		return new Music(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(e), 0, 0, true);
	}

	public static final Music BOSS = now(Sounds.MUSIC_BOSS);
	public static final Music BOSS_FINAL = now(Sounds.MUSIC_BOSS_FINAL);
	public static final Music ENDINGS = now(Sounds.MUSIC_ENDINGS);

	private static final long DANGER_HOLD_MS = 6000, STING_GAP_MS = 2500;
	private static final float FADE_OUT = 1 / 20f, FADE_IN = 1 / 30f, VANILLA_OUT = 1 / 16f;

	private static State state = State.EXPLORE;
	private static Track theme, heartbeat;
	private static float vanillaFade = 1;
	private static boolean played;
	private static long lastDangerAt = -1, lastStingAt = -1;
	// sting detection: counts taken from the synced player state
	private static CompoundTag seenTag;
	private static int seenQuests = -1, seenVisited = -1, seenPages = -1;
	/** Stings played since the game started (read by the check run). */
	public static int stings;

	/**
	 * The state for a situation. screenMusic: a screen plays its own (the endings' crawl); bossLowest: the lowest
	 * health fraction among the Matriochka boss bars shown, or more than 1.5 when none is; danger: creatures hunt
	 * the player now or did a moment ago.
	 */
	public static State choose(boolean screenMusic, float bossLowest, boolean danger) {
		if (screenMusic) return State.NONE;
		if (bossLowest <= 1.5f) return bossLowest <= 0.34f ? State.BOSS_FINAL : State.BOSS;
		return danger ? State.DANGER : State.EXPLORE;
	}

	public static State state() {
		return state;
	}

	/** The lowest health fraction among the mod's boss bars, 2 when none is shown (or in the End). */
	public static float bossLowest(Minecraft mc) {
		if (mc.player == null || mc.player.level().dimension() == Level.END) return 2f;
		float lowest = 2f;
		for (LerpingBossEvent e : ((BossHealthOverlayAccess) fr.achedon12.matriochka.client.mc.McClient.bossOverlay(mc)).matriochka$events().values()) {
			if (e.shouldPlayBossMusic() && isOurs(e)) lowest = Math.min(lowest, e.getProgress());
		}
		return lowest;
	}

	/** The world of the weakest Matriochka boss whose bar is shown, -1 when none is known. */
	static int bossWorld(Minecraft mc) {
		int world = -1;
		float lowest = 2f;
		for (LerpingBossEvent e : ((BossHealthOverlayAccess) fr.achedon12.matriochka.client.mc.McClient.bossOverlay(mc)).matriochka$events().values()) {
			if (!e.shouldPlayBossMusic() || !isOurs(e) || e.getProgress() >= lowest) continue;
			fr.achedon12.matriochka.content.Defs.BossDef d = BossBars.bossOf(e.getName());
			if (d != null) {
				world = d.world();
				lowest = e.getProgress();
			}
		}
		return world;
	}

	public static boolean bossFight(Minecraft mc) {
		return bossLowest(mc) <= 1.5f;
	}

	/** True while the adaptive music holds the music channel: the game must not start a world theme. */
	public static boolean holding() {
		return state != State.EXPLORE && state != State.NONE || theme != null;
	}

	/** The share of the world theme's volume: the comfort slider, and the quick fade out when another theme takes over. */
	public static float exploreGain() {
		return Comfort.get().musicExplore / 100f * vanillaFade;
	}

	// ---------------------------------------------------------------- the tick
	public static void tick(Minecraft mc) {
		if (mc.player == null) {
			stopAll(mc);
			seenTag = null;
			seenQuests = seenVisited = seenPages = -1;
			return;
		}
		long now = Ui.now();
		if (Cinematics.danger() > 0) lastDangerAt = now;
		boolean screenMusic = fr.achedon12.matriochka.client.mc.McClient.screen(mc) != null && fr.achedon12.matriochka.client.mc.McClient.screen(mc).getBackgroundMusic() != null;
		state = choose(screenMusic, bossLowest(mc), lastDangerAt >= 0 && now - lastDangerAt < DANGER_HOLD_MS);
		stings(mc, now);
		layers(mc);
		if (state == State.NONE) {
			if (theme != null) mc.getSoundManager().stop(theme);
			theme = null;
			restoreVanilla(mc);
			return;
		}
		MusicManagerAccess mm = (MusicManagerAccess) mc.getMusicManager();
		if (state == State.EXPLORE) {
			if (theme != null) {
				theme.target = 0;
				if (theme.isStopped() || !mc.getSoundManager().isActive(theme)) {
					theme = null;
					// the world theme comes back after a breath instead of the usual minutes of silence
					if (played) mm.matriochka$setDelay(Math.min(mm.matriochka$delay(), 100));
					played = false;
				}
			}
			restoreVanilla(mc);
			return;
		}
		// another theme takes over: first the game's own track fades out quickly
		SoundInstance current = mm.matriochka$current();
		if (current != null && !(current instanceof Track)) {
			vanillaFade = Math.max(0, vanillaFade - VANILLA_OUT);
			float g = mc.getMusicVolume();
			mm.matriochka$setGain(g);
			mc.getSoundManager().updateCategoryVolume(SoundSource.MUSIC, g);
			if (vanillaFade <= 0) {
				mc.getMusicManager().stopPlaying();
				restoreVanilla(mc);
			}
			return;
		}
		if (theme != null && theme.state != state) {
			theme.target = 0;
			if (!theme.isStopped() && mc.getSoundManager().isActive(theme)) return;
			theme = null;
		}
		if (theme == null) {
			mc.getSoundManager().updateCategoryVolume(SoundSource.MUSIC, 1f);
			theme = new Track(switch (state) {
				case DANGER -> Sounds.MUSIC_DANGER;
				case BOSS_FINAL -> Sounds.MUSIC_BOSS_FINAL;
				default -> Sounds.bossMusic(bossWorld(mc));
			}, state, true);
			mc.getSoundManager().play(theme);
			played = true;
		}
		theme.target = 1;
	}

	private static void restoreVanilla(Minecraft mc) {
		if (vanillaFade >= 1) return;
		vanillaFade = 1;
		((MusicManagerAccess) mc.getMusicManager()).matriochka$setGain(1f);
		mc.getSoundManager().updateCategoryVolume(SoundSource.MUSIC, 1f);
	}

	private static void stopAll(Minecraft mc) {
		if (theme != null) mc.getSoundManager().stop(theme);
		if (heartbeat != null) mc.getSoundManager().stop(heartbeat);
		theme = heartbeat = null;
		state = State.EXPLORE;
		lastDangerAt = -1;
		played = false;
		vanillaFade = 1;
	}

	/** Low health or breath: the heartbeat swells, the theme ducks under it. */
	private static void layers(Minecraft mc) {
		var p = mc.player;
		float sev = 0;
		if (!p.isCreative() && !p.isSpectator() && p.isAlive()) {
			sev = Math.max(sev, Ui.clamp01((0.35f - p.getHealth() / p.getMaxHealth()) / 0.25f));
			sev = Math.max(sev, Ui.clamp01((0.3f - p.getAirSupply() / (float) p.getMaxAirSupply()) / 0.25f));
			if (MatrioClient.state.contains("g_oxygen") && MatrioClient.state.getIntOr("here", 0) == 7) {
				sev = Math.max(sev, Ui.clamp01((25f - MatrioClient.state.getFloatOr("g_oxygen", 100f)) / 20f));
			}
		}
		if (theme != null) theme.duck = 1 - 0.35f * sev;
		if (sev > 0 && state != State.NONE && (heartbeat == null || heartbeat.isStopped())) {
			heartbeat = new Track(Sounds.MUSIC_LAYER_HEARTBEAT, null, true);
			mc.getSoundManager().play(heartbeat);
		}
		if (heartbeat != null) {
			heartbeat.target = state == State.NONE ? 0 : sev > 0 ? 0.45f + 0.55f * sev : 0;
			if (heartbeat.isStopped()) heartbeat = null;
		}
	}

	/** A sting when the synced state shows a new structure visited, a new Journal page or a quest done. */
	private static void stings(Minecraft mc, long now) {
		CompoundTag t = MatrioClient.state;
		if (t == seenTag) return;
		seenTag = t;
		int quests = 0, visited = 0, pages = 0;
		for (String k : t.keySet()) {
			if (k.startsWith("f_quest_") && t.getBooleanOr(k, false)) quests++;
			else if (k.startsWith("f_visited_") && t.getBooleanOr(k, false)) visited++;
			else if (k.startsWith("pages_")) pages += Integer.bitCount(t.getIntOr(k, 0));
		}
		boolean first = seenQuests < 0;
		SoundEvent sting = null;
		if (!first && quests > seenQuests) sting = Sounds.MUSIC_STING_QUEST;
		else if (!first && (visited > seenVisited || pages > seenPages)) sting = Sounds.MUSIC_STING_DISCOVERY;
		seenQuests = quests;
		seenVisited = visited;
		seenPages = pages;
		if (sting != null) sting(mc, sting, now);
	}

	public static void sting(Minecraft mc, SoundEvent e, long now) {
		if (lastStingAt >= 0 && now - lastStingAt < STING_GAP_MS) return;
		lastStingAt = now;
		stings++;
		float v = Comfort.get().musicStings / 100f;
		if (v <= 0) return;
		mc.getSoundManager().play(new SimpleSoundInstance(e.location(), SoundSource.MUSIC, v, 1f, SoundInstance.createUnseededRandom(), false, 0,
			SoundInstance.Attenuation.NONE, 0, 0, 0, true));
	}

	/** Only the mod's bosses: their bar is named after the entity. */
	private static boolean isOurs(LerpingBossEvent e) {
		return e.getName().getContents() instanceof TranslatableContents t && t.getKey().startsWith("entity." + Matriochka.MOD_ID + ".");
	}

	/** A theme or a layer whose volume eases toward a target every tick; it stops itself once faded out. */
	private static final class Track extends AbstractTickableSoundInstance {
		final State state;
		float fade, target = 1, duck = 1;

		Track(SoundEvent e, State state, boolean loop) {
			super(e, SoundSource.MUSIC, SoundInstance.createUnseededRandom());
			this.state = state;
			this.looping = loop;
			this.attenuation = SoundInstance.Attenuation.NONE;
			this.relative = true;
			this.volume = 0.001f;
		}

		@Override
		public boolean canStartSilent() {
			return true;
		}

		@Override
		public void tick() {
			fade = target > fade ? Math.min(target, fade + FADE_IN) : Math.max(target, fade - FADE_OUT);
			var c = Comfort.get();
			int pct = state == null ? c.musicLayers : state == State.DANGER ? c.musicDanger : c.musicBoss;
			volume = Math.max(0.0001f, fade * duck * pct / 100f);
			if (target <= 0 && fade <= 0) stop();
		}
	}
}
