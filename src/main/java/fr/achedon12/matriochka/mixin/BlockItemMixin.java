package fr.achedon12.matriochka.mixin;

import fr.achedon12.matriochka.rules.PlacedBlocks;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Records the blocks players place, for the worlds whose rules move or burn them. */
@Mixin(BlockItem.class)
public abstract class BlockItemMixin {
	@Inject(method = "placeBlock", at = @At("RETURN"))
	private void matriochka$track(BlockPlaceContext context, BlockState state, CallbackInfoReturnable<Boolean> cir) {
		if (cir.getReturnValueZ() && context.getPlayer() != null && context.getLevel() instanceof ServerLevel level) {
			PlacedBlocks.onPlaced(level, context.getClickedPos());
		}
	}
}
