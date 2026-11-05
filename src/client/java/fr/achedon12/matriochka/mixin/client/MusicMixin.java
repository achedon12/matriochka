package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.MusicThemes;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.Music;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Plays the boss theme during a Matriochka boss fight, the way the End plays its own during the dragon fight. */
@Mixin(Minecraft.class)
public abstract class MusicMixin {
	@Inject(method = "getSituationalMusic", at = @At("RETURN"), cancellable = true)
	private void matriochka$bossMusic(CallbackInfoReturnable<Music> cir) {
		Minecraft mc = (Minecraft) (Object) this;
		// a screen's own music (the endings' crawl) wins
		if (mc.gui.screen() != null && mc.gui.screen().getBackgroundMusic() != null) return;
		Music boss = MusicThemes.situational(mc);
		if (boss != null) cir.setReturnValue(boss);
	}
}
