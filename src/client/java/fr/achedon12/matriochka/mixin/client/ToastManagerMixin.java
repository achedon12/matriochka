package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.MatrioToast;
import net.minecraft.client.gui.components.toasts.AdvancementToast;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** A Matriochka advancement is announced on the mod's own card (client/MatrioToast); every other toast is vanilla's. */
@Mixin(ToastManager.class)
public abstract class ToastManagerMixin {
	@Inject(method = "addToast", at = @At("HEAD"), cancellable = true)
	private void matriochka$ownToast(Toast toast, CallbackInfo ci) {
		if (!(toast instanceof AdvancementToast) || toast instanceof MatrioToast) return;
		var holder = ((AdvancementToastAccess) toast).matriochka$advancement();
		if (holder == null || !holder.id().getNamespace().equals(Matriochka.MOD_ID)) return;
		var display = holder.value().display();
		if (display.isEmpty()) return;
		ci.cancel();
		((ToastManager) (Object) this).addToast(new MatrioToast(holder.id().getPath(), display.get()));
	}
}
