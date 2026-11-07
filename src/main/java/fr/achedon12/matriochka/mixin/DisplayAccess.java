package fr.achedon12.matriochka.mixin;

import com.mojang.math.Transformation;
import net.minecraft.world.entity.Display;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Billboarding and placement of a display entity from code. */
@Mixin(Display.class)
public interface DisplayAccess {
	@Invoker("setBillboardConstraints")
	void matriochka$setBillboard(Display.BillboardConstraints b);

	@Invoker("setTransformation")
	void matriochka$setTransformation(Transformation t);

	@Invoker("setPosRotInterpolationDuration")
	void matriochka$setPosRotInterpolation(int ticks);
}
