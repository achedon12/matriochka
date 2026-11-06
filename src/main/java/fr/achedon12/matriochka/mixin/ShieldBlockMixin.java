package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.item.ReplayGear;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A blow stopped by a held shield. A fully blocked blow leaves hurtServer early, before Fabric's AFTER_DAMAGE, so the
 * Lantern Shield's flare is fired from the blocking itself.
 */
@Mixin(LivingEntity.class)
public abstract class ShieldBlockMixin {
	@Inject(method = "applyItemBlocking", at = @At("RETURN"))
	private void matriochka$shieldBlocked(ServerLevel level, DamageSource source, float amount, CallbackInfoReturnable<Float> cir) {
		if (cir.getReturnValueF() > 0 && (Object) this instanceof ServerPlayer player) ReplayGear.blocked(level, player, source);
	}
}
