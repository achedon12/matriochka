package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

/**
 * The sealed reliquary at the heart of a world's wonder. Only the cross key found in another world's wonder opens it:
 * the key of World n opens the reliquary of World opens(n). Opened, it gives the world's relic, once per player.
 * Its world is stored in its block data by the wonder that set it down (structure/Rewards).
 */
public class Reliquary extends Block implements EntityBlock {
	public Reliquary(BlockBehaviour.Properties p) {
		super(p);
	}

	/** The world whose reliquary the cross key of World n opens. */
	public static int opens(int n) {
		return (n + 3) % 10 + 1;
	}

	/** The world whose cross key opens the reliquary of World w. */
	public static int keyFor(int w) {
		for (int n = 1; n <= 10; n++) if (opens(n) == w) return n;
		return 1;
	}

	@Override
	public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new DataBlockEntity(ModContent.BE_DATA, pos, state);
	}

	@Override
	protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
		if (!(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl) || !(level.getBlockEntity(pos) instanceof DataBlockEntity be))
			return InteractionResult.SUCCESS;
		int world = be.data().getIntOr("world", 0);
		if (world <= 0) return InteractionResult.SUCCESS;
		String opened = "opened_" + sp.getUUID();
		if (be.data().getBooleanOr(opened, false)) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.reliquary.empty"));
			return InteractionResult.SUCCESS;
		}
		int need = keyFor(world);
		if (!stack.is(ModContent.item("cross_key_" + need))) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.reliquary.needs", need).withStyle(ChatFormatting.GOLD));
			sl.playSound(null, pos, SoundEvents.CHEST_LOCKED, SoundSource.BLOCKS, 1f, 0.8f);
			return InteractionResult.SUCCESS;
		}
		if (!sp.isCreative()) stack.shrink(1);
		be.data().putBoolean(opened, true);
		be.changed();
		Block.popResource(sl, pos.above(), new ItemStack(ModContent.item("relic_" + world)));
		sl.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 60, 0.4, 0.6, 0.4, 0.3);
		sl.playSound(null, pos, SoundEvents.VAULT_OPEN_SHUTTER, SoundSource.BLOCKS, 1.4f, 0.9f);
		sl.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.2f, 1.2f);
		sp.sendSystemMessage(Component.translatable("message.matriochka.reliquary.opened", Component.translatable("item.matriochka.relic_" + world)).withStyle(ChatFormatting.GOLD));
		return InteractionResult.SUCCESS;
	}
}
