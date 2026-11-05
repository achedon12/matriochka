package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.net.Cues;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Comfort option "soft effects": a player who chose it never gets Nausea or Darkness, whatever gives them (world rules,
 * creature and boss attacks); the client draws a gentle tint for as long as the effect would have lasted.
 */
@Mixin(LivingEntity.class)
public abstract class SoftEffectsMixin {
	@Inject(method = "addEffect(Lnet/minecraft/world/effect/MobEffectInstance;Lnet/minecraft/world/entity/Entity;)Z", at = @At("HEAD"), cancellable = true)
	private void matriochka$softEffects(MobEffectInstance effect, Entity source, CallbackInfoReturnable<Boolean> cir) {
		if (!((Object) this instanceof ServerPlayer player) || !Cues.soft(player)) return;
		boolean nausea = effect.is(MobEffects.NAUSEA), darkness = effect.is(MobEffects.DARKNESS);
		if (!nausea && !darkness) return;
		Cues.tint(player, nausea ? "nausea" : "darkness", effect.getDuration());
		cir.setReturnValue(false);
	}
}
