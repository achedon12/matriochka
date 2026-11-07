package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.TitleDolls;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.TitleScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** A row of nesting dolls and the mod's version in a corner of the title screen (TitleDolls). */
@Mixin(TitleScreen.class)
public abstract class TitleScreenMixin {
	@Inject(method = "extractRenderState", at = @At("TAIL"))
	private void matriochka$dolls(GuiGraphicsExtractor g, int mouseX, int mouseY, float partial, CallbackInfo ci) {
		TitleDolls.draw(g);
	}
}
