package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.BossBars;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.BossHealthOverlay;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** While a Matriochka boss's bar is shown, the boss bars are drawn by client/BossBars instead of vanilla. */
@Mixin(BossHealthOverlay.class)
public class BossBarMixin {
	@Inject(method = "extractRenderState", at = @At("HEAD"), cancellable = true)
	private void matriochka$bars(GuiGraphicsExtractor g, CallbackInfo ci) {
		if (BossBars.draw((BossHealthOverlay) (Object) this, g)) ci.cancel();
	}
}
