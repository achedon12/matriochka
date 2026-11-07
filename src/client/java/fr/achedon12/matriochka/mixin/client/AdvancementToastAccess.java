package fr.achedon12.matriochka.mixin.client;

import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.client.gui.components.toasts.AdvancementToast;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Which advancement a vanilla advancement toast announces. */
@Mixin(AdvancementToast.class)
public interface AdvancementToastAccess {
	@Accessor("advancement")
	AdvancementHolder matriochka$advancement();
}
