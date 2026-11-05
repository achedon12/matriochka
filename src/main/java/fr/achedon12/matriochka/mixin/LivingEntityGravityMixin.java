package fr.achedon12.matriochka.mixin;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** World 6: jumping off a ceiling pushes you down, away from it. */
@Mixin(LivingEntity.class)
public abstract class LivingEntityGravityMixin {
	@Inject(method = "jumpFromGround", at = @At("TAIL"))
	private void matriochka$jumpAwayFromCeiling(CallbackInfo ci) {
		LivingEntity self = (LivingEntity) (Object) this;
		if (self.getGravity() >= 0) return;
		Vec3 m = self.getDeltaMovement();
		if (m.y > 0) self.setDeltaMovement(m.x, -m.y, m.z);
	}
}
