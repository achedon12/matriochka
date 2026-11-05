package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.gear.GearClasses;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Every crafted weapon, tool or armor piece receives a random equipment class. */
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
}
