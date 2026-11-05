package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Sounds;
import fr.achedon12.matriochka.mixin.client.BossHealthOverlayAccess;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.sounds.Music;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.level.Level;

/**
 * The music that is not tied to a biome: the boss theme while a Matriochka boss bar is shown (a fiercer one once the
 * boss is below a third of its health), and the endings' theme. World themes come from the biomes (tools/sound.py).
 */
public final class MusicThemes {
	private MusicThemes() {}

	/** Replaces whatever plays, starts at once and starts again as soon as it ends. */
	private static Music now(SoundEvent e) {
		return new Music(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(e), 0, 0, true);
	}

	public static final Music BOSS = now(Sounds.MUSIC_BOSS);
	public static final Music BOSS_FINAL = now(Sounds.MUSIC_BOSS_FINAL);
	public static final Music ENDINGS = now(Sounds.MUSIC_ENDINGS);

	/** The boss theme to play now, or null to let the game choose. */
	public static Music situational(Minecraft mc) {
		if (mc.player == null || mc.player.level().dimension() == Level.END) return null;
		float lowest = 2f;
		for (LerpingBossEvent e : ((BossHealthOverlayAccess) mc.gui.hud.getBossOverlay()).matriochka$events().values()) {
			if (e.shouldPlayBossMusic() && isOurs(e)) lowest = Math.min(lowest, e.getProgress());
		}
		if (lowest > 1.5f) return null;
		return lowest <= 0.34f ? BOSS_FINAL : BOSS;
	}

	private static boolean fighting;

	/** Client tick: when the fight ends (the boss falls or the player leaves), the boss theme stops with it. */
	public static void tick(Minecraft mc) {
		boolean now = situational(mc) != null;
		if (fighting && !now) {
			mc.getMusicManager().stopPlaying(BOSS);
			mc.getMusicManager().stopPlaying(BOSS_FINAL);
		}
		fighting = now;
	}

	/** Only the mod's bosses: their bar is named after the entity. */
	private static boolean isOurs(LerpingBossEvent e) {
		return e.getName().getContents() instanceof TranslatableContents t && t.getKey().startsWith("entity." + Matriochka.MOD_ID + ".");
	}
}
