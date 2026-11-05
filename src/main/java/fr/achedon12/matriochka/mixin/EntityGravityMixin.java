package fr.achedon12.matriochka.mixin;

import com.llamalad7.mixinextras.sugar.Local;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * World 6: an entity whose gravity is negative falls upward, so the ceiling it bumps into is the ground it stands on.
 * Runs on both sides, so the client predicts the same footing as the server.
 */
@Mixin(Entity.class)
public abstract class EntityGravityMixin {
	@ModifyArg(method = "move", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/Entity;setOnGroundWithMovement(ZZLnet/minecraft/world/phys/Vec3;)V"), index = 0)
	private boolean matriochka$ceilingIsGround(boolean below, @Local(argsOnly = true) Vec3 delta) {
		Entity self = (Entity) (Object) this;
		return self.getGravity() < 0 ? self.verticalCollision && delta.y > 0 : below;
	}
}
