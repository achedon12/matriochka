package fr.achedon12.matriochka.mixin;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Display;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Sets up a text display from code: the speech bubbles of the worlds' people (entity/MatrioNpc). */
@Mixin(Display.TextDisplay.class)
public interface TextDisplayAccess {
	@Invoker("setText")
	void matriochka$setText(Component text);

	@Invoker("setBackgroundColor")
	void matriochka$setBackgroundColor(int argb);

	@Invoker("setLineWidth")
	void matriochka$setLineWidth(int width);
}
