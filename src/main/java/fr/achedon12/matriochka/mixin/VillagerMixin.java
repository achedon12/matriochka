package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.world.Karma;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Surface villagers price their offers with the trading player's karma, on top of their own reputation. */
@Mixin(Villager.class)
public abstract class VillagerMixin {
	@Inject(method = "updateSpecialPrices", at = @At("TAIL"))
	private void matriochka$karmaPrices(Player player, CallbackInfo ci) {
		Karma.adjustPrices((Villager) (Object) this, player);
	}
}
