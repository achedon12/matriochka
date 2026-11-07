package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.Cinematics;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.LevelLoadingScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** While a dive is loading its world, the loading screen stays dark under the doll's outline (Cinematics). */
@Mixin(LevelLoadingScreen.class)
public abstract class LevelLoadingScreenMixin {
	@Inject(method = "extractRenderState", at = @At("TAIL"))
	private void matriochka$veil(GuiGraphicsExtractor g, int mouseX, int mouseY, float partial, CallbackInfo ci) {
		Cinematics.loadingVeil(g, g.guiWidth(), g.guiHeight());
	}
}
