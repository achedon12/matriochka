package fr.achedon12.matriochka.mixin;

import net.minecraft.world.entity.Display;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Sets the item an item display shows, from code: the trophy doll on a player's shoulder (world/Shoulder). */
@Mixin(Display.ItemDisplay.class)
public interface ItemDisplayAccess {
	@Invoker("setItemStack")
	void matriochka$setItem(ItemStack stack);
}
