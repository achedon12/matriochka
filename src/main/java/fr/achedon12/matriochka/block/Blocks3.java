package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.Lairs;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Rituals;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
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
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jspecify.annotations.Nullable;

/** Cradle, death chest, nesting chest, boss altars, lair hearts and sealed doors. */
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
				be.data().putInt("charges", fr.achedon12.matriochka.world.Config.cradleCharges());
				be.changed();
				var t = PlayerState.of(sp).tag();
				net.minecraft.nbt.CompoundTag c = new net.minecraft.nbt.CompoundTag();
				c.putInt("x", pos.getX());
				c.putInt("y", pos.getY());
				c.putInt("z", pos.getZ());
				t.put("cradle_" + world, c);
				sp.sendSystemMessage(Component.translatable("message.matriochka.cradle_set", fr.achedon12.matriochka.world.Config.cradleCharges()));
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

		@Override
		protected float getDestroyProgress(BlockState state, Player player, net.minecraft.world.level.BlockGetter level, BlockPos pos) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be
				&& !fr.achedon12.matriochka.world.MatrioData.get(sp.level().getServer()).sameGroup(be.data().getStringOr("owner", ""), sp)) {
				return 0f;
			}
			return super.getDestroyProgress(state, player, level, pos);
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

	// ---------------------------------------------------------------- Nesting chest: three rows, two rows or one row; holds the smaller ones
	public static class NestingChest extends Block implements EntityBlock {
		private final int rows;
		private final net.minecraft.world.phys.shapes.VoxelShape shape;

		public NestingChest(BlockBehaviour.Properties p, int rows) {
			super(p);
			this.rows = rows;
			int inset = (3 - rows) * 2;
			this.shape = Block.box(inset, 0, inset, 16 - inset, 16 - inset * 2, 16 - inset);
		}

		public int rows() {
			return rows;
		}

		@Override
		protected net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext ctx) {
			return shape;
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				if (sp.isSecondaryUseActive()) NestingChests.cycleRule(sp, be);
				else NestingChests.open(sp, (ServerLevel) level, be, rows);
			}
			return InteractionResult.SUCCESS;
		}

		@Override
		public void setPlacedBy(Level level, BlockPos pos, BlockState state, net.minecraft.world.entity.@Nullable LivingEntity by, ItemStack stack) {
			if (!level.isClientSide() && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				NestingChests.fromItem(stack, be.data(), level.registryAccess(), rows);
				be.changed();
			}
		}

		/** The chest drops as one item holding its contents and its sorting rule, like a doll closing on the smaller ones. */
		@Override
		protected java.util.List<ItemStack> getDrops(BlockState state, net.minecraft.world.level.storage.loot.LootParams.Builder params) {
			BlockEntity be = params.getOptionalParameter(net.minecraft.world.level.storage.loot.parameters.LootContextParams.BLOCK_ENTITY);
			if (be instanceof DataBlockEntity d) {
				NestingChests.forget(d);
				return java.util.List.of(NestingChests.toItem(this, d.data(), params.getLevel().registryAccess()));
			}
			return super.getDrops(state, params);
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			// creative breaking drops nothing: keep the contents anyway
			if (!level.isClientSide() && player.isCreative() && level.getBlockEntity(pos) instanceof DataBlockEntity be && be.data().contains("items")
				&& !be.data().getListOrEmpty("items").isEmpty()) {
				NestingChests.forget(be);
				Block.popResource(level, pos, NestingChests.toItem(this, be.data(), level.registryAccess()));
			}
			return super.playerWillDestroy(level, pos, state, player);
		}
	}

	// ---------------------------------------------------------------- Boss altars
	/**
	 * The Guardian's altar (Surface) wakes it directly. The arena altar of a world wakes its altar boss: holding that world's
	 * offering consumes it and starts a short ritual ({@link Rituals}); without it, the altar names the offering it wants.
	 * Lair bosses have no altar; an arena altar left from an older parcel still wakes them directly.
	 */
	public static class BossAltar extends Block {
		public BossAltar(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (!(player instanceof ServerPlayer sp)) return InteractionResult.SUCCESS;
			ServerLevel sl = (ServerLevel) level;
			int world = Worlds.number(level);
			Defs.BossDef boss = world == 0 ? ModContent.bossForWorld(0) : ModContent.bossForWorld(world);
			if (!sl.getEntitiesOfClass(MatrioBoss.class, sp.getBoundingBox().inflate(48)).isEmpty()) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.boss_already"));
				return InteractionResult.SUCCESS;
			}
			MatrioData data = MatrioData.get(sl.getServer());
			String group = data.groupOf(sp.getUUID());
			if (world == 0) {
				if (data.defeated(group, 0) && !sp.isCreative() && !sp.isShiftKeyDown()) {
					sp.sendSystemMessage(Component.translatable("message.matriochka.guardian_done"));
					return InteractionResult.SUCCESS;
				}
				MatrioBoss.summon(sl, boss.id(), pos.above(2), sp);
				sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, 1, 0, 0, 0, 0);
				return InteractionResult.SUCCESS;
			}
			if (boss.lair() || boss.offering().isEmpty()) {
				MatrioBoss.summon(sl, boss.id(), pos.above(2), sp);
				sl.sendParticles(ParticleTypes.EXPLOSION_EMITTER, pos.getX() + 0.5, pos.getY() + 1, pos.getZ() + 0.5, 1, 0, 0, 0, 0);
				return InteractionResult.SUCCESS;
			}
			if (Rituals.busy(sl, pos)) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.offering.busy"));
				return InteractionResult.SUCCESS;
			}
			Component offering = Component.translatable("item.matriochka." + boss.offering());
			ItemStack held = null;
			for (InteractionHand hand : InteractionHand.values()) {
				ItemStack s = sp.getItemInHand(hand);
				if (!s.isEmpty() && ModContent.idOf(s.getItem()).equals(boss.offering())) {
					held = s;
					break;
				}
			}
			if (held == null) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.offering.needed",
					Component.translatable("entity.matriochka." + boss.id()), offering).withStyle(net.minecraft.ChatFormatting.GRAY));
				level.playSound(null, pos, SoundEvents.RESPAWN_ANCHOR_DEPLETE.value(), SoundSource.BLOCKS, 0.6f, 1.4f);
				return InteractionResult.SUCCESS;
			}
			held.consume(1, sp);
			sp.sendSystemMessage(Component.translatable("message.matriochka.offering.accepted", offering).withStyle(net.minecraft.ChatFormatting.GOLD));
			Rituals.start(sl, pos, boss, sp);
			return InteractionResult.SUCCESS;
		}
	}

	// ---------------------------------------------------------------- Lair heart: wakes the lair boss when a player comes close
	public static class LairHeart extends Block implements EntityBlock {
		public LairHeart(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
			return level.isClientSide() ? null : (l, p, s, be) -> Lairs.tick((ServerLevel) l, p, (DataBlockEntity) be);
		}
	}

	// ---------------------------------------------------------------- Sealed door: opened once by a dungeon key, or by a lockpick (1 in 2)
	public static class SealedDoor extends Block {
		public SealedDoor(BlockBehaviour.Properties p) {
			super(p);
		}

		/** While a redstone signal reaches the World Block outside, sealed doors open by hand (see ScaleLinks). */
		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (level instanceof ServerLevel sl && fr.achedon12.matriochka.world.ScaleLinks.activeAt(sl, pos, "unlocked")) {
				for (BlockPos p : BlockPos.betweenClosed(pos.offset(-2, -3, -2), pos.offset(2, 3, 2))) {
					if (level.getBlockState(p).is(this)) level.setBlock(p, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
				}
				level.playSound(null, pos, SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 1f, 0.7f);
				return InteractionResult.SUCCESS;
			}
			return super.useWithoutItem(state, level, pos, player, hit);
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
