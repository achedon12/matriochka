package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.gear.GearClasses;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Every crafted weapon, tool or armor piece receives a random equipment class; armor layers take the wear first. */
@Mixin(ItemStack.class)
public abstract class ItemStackMixin {
	@Inject(method = "onCraftedBy", at = @At("HEAD"))
	private void matriochka$rollClass(Player player, int craftCount, CallbackInfo ci) {
		if (!player.level().isClientSide()) {
			GearClasses.roll((ItemStack) (Object) this, player.getRandom());
			if (player instanceof net.minecraft.server.level.ServerPlayer sp) {
				fr.achedon12.matriochka.rules.PlayerState.of(sp).progress("craft", fr.achedon12.matriochka.content.ModContent.idOf(((ItemStack) (Object) this).getItem()), craftCount);
			}
		}
	}

	@Inject(method = "processDurabilityChange", at = @At("RETURN"), cancellable = true)
	private void matriochka$layers(int amount, net.minecraft.server.level.ServerLevel level, net.minecraft.server.level.ServerPlayer player, CallbackInfoReturnable<Integer> cir) {
		int wear = cir.getReturnValue();
		if (wear > 0 && fr.achedon12.matriochka.gear.ArmorLayers.absorb((ItemStack) (Object) this, wear, level, player)) cir.setReturnValue(0);
	}
}
