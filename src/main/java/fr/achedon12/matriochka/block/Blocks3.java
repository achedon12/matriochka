package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

/** Cradle, death chest, nesting chest, boss altars and sealed doors. */
public final class Blocks3 {
	private Blocks3() {}

	// ---------------------------------------------------------------- Soul Cradle
	public static class SoulCradle extends Block implements EntityBlock {
		public SoulCradle(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, net.minecraft.world.entity.@Nullable LivingEntity by, ItemStack stack) {
			if (by instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = Worlds.number(level);
				be.data().putString("owner", sp.getUUID().toString());
				be.data().putInt("charges", 3);
				be.changed();
				var t = PlayerState.of(sp).tag();
				net.minecraft.nbt.CompoundTag c = new net.minecraft.nbt.CompoundTag();
				c.putInt("x", pos.getX());
				c.putInt("y", pos.getY());
				c.putInt("z", pos.getZ());
				t.put("cradle_" + world, c);
				sp.sendSystemMessage(Component.translatable("message.matriochka.cradle_set", 3));
			}
		}

		@Override
		protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = Worlds.number(level);
				String id = ModContent.idOf(stack.getItem());
				boolean worldRes = world > 0 && ModContent.def(id) != null && ModContent.def(id).world() == world && !stack.isEmpty();
				if (worldRes && PlayerState.of(sp).spendSouls(5)) {
					stack.consume(1, sp);
					be.data().putInt("charges", be.data().getIntOr("charges", 0) + 1);
					be.changed();
				}
				sp.sendSystemMessage(Component.translatable("message.matriochka.cradle_charges", be.data().getIntOr("charges", 0)));
			}
			return InteractionResult.SUCCESS;
		}
	}

	// ---------------------------------------------------------------- Death Chest (keeps the inventory after the last doll layer)
	public static class DeathChest extends Block implements EntityBlock {
		public DeathChest(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				NonNullList<ItemStack> items = ContainerTags.load(be.data(), level.registryAccess(), 54);
				for (ItemStack s : items) {
					if (!s.isEmpty() && !sp.getInventory().add(s)) net.minecraft.world.level.block.Block.popResource(sp.level(), sp.blockPosition(), s);
				}
				level.removeBlock(pos, false);
				level.playSound(null, pos, SoundEvents.CHEST_OPEN, SoundSource.BLOCKS, 1f, 0.8f);
			}
			return InteractionResult.SUCCESS;
		}

		@Override
		protected float getDestroyProgress(BlockState state, Player player, net.minecraft.world.level.BlockGetter level, BlockPos pos) {
			return 0f;
		}
	}

	// ---------------------------------------------------------------- Nesting chest: holds a 27-slot inventory
	public static class NestingChest extends Block implements EntityBlock {
		public NestingChest(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				SimpleContainer c = new SimpleContainer(27) {
					@Override
					public void setChanged() {
						super.setChanged();
						NonNullList<ItemStack> l = NonNullList.withSize(27, ItemStack.EMPTY);
						for (int i = 0; i < 27; i++) l.set(i, getItem(i));
						ContainerTags.save(be.data(), level.registryAccess(), l);
						be.setChanged();
					}
				};
				NonNullList<ItemStack> items = ContainerTags.load(be.data(), level.registryAccess(), 27);
				for (int i = 0; i < 27; i++) c.setItem(i, items.get(i));
				sp.openMenu(new SimpleMenuProvider((id, inv, p) -> ChestMenu.threeRows(id, inv, c), Component.translatable("block.matriochka.nesting_chest")));
				level.playSound(null, pos, SoundEvents.CHEST_OPEN, SoundSource.BLOCKS, 0.8f, 1.3f);
			}
			return InteractionResult.SUCCESS;
		}

		@Override
		protected void affectNeighborsAfterRemoval(BlockState state, ServerLevel level, BlockPos pos, boolean moved) {
			super.affectNeighborsAfterRemoval(state, level, pos, moved);
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			if (level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				for (ItemStack s : ContainerTags.load(be.data(), level.registryAccess(), 27)) Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), s);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}
	}

	// ---------------------------------------------------------------- Boss altars
	public static class BossAltar extends Block {
		public BossAltar(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (!(player instanceof ServerPlayer sp)) return InteractionResult.SUCCESS;
			ServerLevel sl = (ServerLevel) level;
			int world = Worlds.number(level);
			String bossId = world == 0 ? "block_guardian" : ModContent.bossForWorld(world).id();
			if (!sl.getEntitiesOfClass(MatrioBoss.class, sp.getBoundingBox().inflate(48)).isEmpty()) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.boss_already"));
				return InteractionResult.SUCCESS;
			}
			MatrioData data = MatrioData.get(sl.getServer());
			String group = data.groupOf(sp.getUUID());
			if (world == 0 && data.defeated(group, 0) && !sp.isCreative() && !sp.isShiftKeyDown()) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.guardian_done"));
				return InteractionResult.SUCCESS;
			}
			MatrioBoss.summon(sl, bossId, pos.above(2), sp);
			sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, 1, 0, 0, 0, 0);
			return InteractionResult.SUCCESS;
		}
	}

	// ---------------------------------------------------------------- Sealed door: opened once by a dungeon key, or by a lockpick (1 in 2)
	public static class SealedDoor extends Block {
		public SealedDoor(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
			if (!(player instanceof ServerPlayer sp)) return InteractionResult.SUCCESS;
			String id = ModContent.idOf(stack.getItem());
			boolean open = false;
			if (id.equals("dungeon_key")) {
				open = true;
				stack.consume(1, sp);
				PlayerState.of(sp).progress("use", "dungeon_key", 1);
			} else if (id.equals("lockpick_kit")) {
				stack.consume(1, sp);
				open = level.getRandom().nextBoolean();
			}
			if (open) {
				for (BlockPos p : BlockPos.betweenClosed(pos.offset(-2, -3, -2), pos.offset(2, 3, 2))) {
					if (level.getBlockState(p).is(this)) level.setBlock(p, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
				}
				level.playSound(null, pos, SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 1f, 0.5f);
				Achievements.grant(sp, "door_opened");
			} else {
				level.playSound(null, pos, SoundEvents.CHAIN_HIT, SoundSource.BLOCKS, 1f, 0.6f);
			}
			return InteractionResult.SUCCESS;
		}
	}
}
