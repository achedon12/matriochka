package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.StallScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.MenuType;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Opens the Matriochka stall in place of the villager screen when the merchant menu belongs to one of the mod's
 * peoples (the server announced it just before, see Net.MerchantInfoPayload). The menu itself, its slots and its
 * packets stay vanilla; every other merchant keeps the vanilla screen.
 */
@Mixin(MenuScreens.class)
public abstract class MerchantScreenMixin {
	@Inject(method = "create", at = @At("HEAD"), cancellable = true)
	private static void matriochka$stall(MenuType<?> type, Minecraft minecraft, int containerId, Component title, CallbackInfo ci) {
		if (type == MenuType.MERCHANT && StallScreen.open(minecraft, containerId, title)) ci.cancel();
	}
}
