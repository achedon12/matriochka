package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.Cinematics;
import net.minecraft.client.Camera;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The slow push-in of a boss introduction and the punch of a phase break narrow the field of view a little. */
@Mixin(Camera.class)
public abstract class CameraFovMixin {
	@Inject(method = "calculateFov", at = @At("RETURN"), cancellable = true)
	private void matriochka$push(float partialTicks, CallbackInfoReturnable<Float> cir) {
		float k = Cinematics.fovScale();
		if (k != 1f) cir.setReturnValue(cir.getReturnValue() * k);
	}
}
