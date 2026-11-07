package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.MusicThemes;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.Music;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Hands the music channel to the adaptive music (client/MusicThemes) while it plays a danger or boss theme, and
 * applies the comfort slider and the quick fade to the world themes the game plays itself.
 */
@Mixin(Minecraft.class)
public abstract class MusicMixin {
	@Inject(method = "getSituationalMusic", at = @At("RETURN"), cancellable = true)
	private void matriochka$adaptiveMusic(CallbackInfoReturnable<Music> cir) {
		Minecraft mc = (Minecraft) (Object) this;
		// a screen's own music (the endings' crawl) wins
		if (fr.achedon12.matriochka.client.mc.McClient.screen(mc) != null && fr.achedon12.matriochka.client.mc.McClient.screen(mc).getBackgroundMusic() != null) return;
		if (MusicThemes.holding()) cir.setReturnValue(null);
	}

	@Inject(method = "getMusicVolume", at = @At("RETURN"), cancellable = true)
	private void matriochka$exploreVolume(CallbackInfoReturnable<Float> cir) {
		Minecraft mc = (Minecraft) (Object) this;
		if (fr.achedon12.matriochka.client.mc.McClient.screen(mc) != null && fr.achedon12.matriochka.client.mc.McClient.screen(mc).getBackgroundMusic() != null) return;
		cir.setReturnValue(cir.getReturnValue() * MusicThemes.exploreGain());
	}
}
