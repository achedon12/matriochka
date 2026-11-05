package fr.achedon12.matriochka.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import fr.achedon12.matriochka.client.Cinematics;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Camera shakes ride on the hurt tilt, so they move the world and the held item together. */
@Mixin(GameRenderer.class)
public abstract class CameraShakeMixin {
	@Inject(method = "bobHurt", at = @At("RETURN"))
	private void matriochka$shake(CameraRenderState cameraState, PoseStack poseStack, CallbackInfo ci) {
		float[] a = Cinematics.shakeAngles();
		if (a == null) return;
		poseStack.rotateDegrees(Axis.YP, a[0]);
		poseStack.rotateDegrees(Axis.XP, a[1]);
		poseStack.rotateDegrees(Axis.ZP, a[2]);
	}
}
