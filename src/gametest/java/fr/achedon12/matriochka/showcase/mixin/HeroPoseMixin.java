package fr.achedon12.matriochka.showcase.mixin;

import fr.achedon12.matriochka.showcase.PosterPose;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Key-art capture only (-Pposter): once the vanilla animation of a humanoid model is set up, the poster's hero (a
 * mannequin) gets the action pose of PosterPose instead. Off unless PosterPose.active is set; the armour layers
 * (vanilla and GeckoLib, which copies these parts) follow the same parts.
 */
@Mixin(HumanoidModel.class)
abstract class HeroPoseMixin {
	@Inject(method = "setupAnim(Lnet/minecraft/client/renderer/entity/state/HumanoidRenderState;)V", at = @At("TAIL"))
	private void matriochka$heroPose(HumanoidRenderState state, CallbackInfo ci) {
		if (PosterPose.active) PosterPose.apply((HumanoidModel<?>) (Object) this, state);
	}
}
