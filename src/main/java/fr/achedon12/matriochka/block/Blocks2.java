package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jspecify.annotations.Nullable;

/** The world-structure blocks: World Soil, Planted Seed, World Block, Threshold. */
public final class Blocks2 {
	private Blocks2() {}

	// ---------------------------------------------------------------- World Soil
	public static class WorldSoil extends Block {
		public static final BooleanProperty TILLED = BooleanProperty.create("tilled");
		public final int index;

		public WorldSoil(int index, BlockBehaviour.Properties p) {
			super(p);
			this.index = index;
			registerDefaultState(stateDefinition.any().setValue(TILLED, false));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(TILLED);
		}

		@Override
		protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
			if (stack.is(net.minecraft.tags.ItemTags.HOES) && !state.getValue(TILLED)) {
				level.setBlock(pos, state.setValue(TILLED, true), 3);
				level.playSound(player, pos, SoundEvents.HOE_TILL.value(), SoundSource.BLOCKS, 1f, 1f);
				return InteractionResult.SUCCESS;
			}
			String id = ModContent.idOf(stack.getItem());
			if (id.startsWith("seed_") && state.getValue(TILLED) && level.getBlockState(pos.above()).isAir()) {
				int world = Integer.parseInt(id.substring(5));
				if (world != index + 1) {
					if (!level.isClientSide()) player.sendSystemMessage(Component.translatable("message.matriochka.wrong_soil", world - 1));
					return InteractionResult.FAIL;
				}
				if (player instanceof ServerPlayer sp) {
					MatrioData data = MatrioData.get(sp.level().getServer());
					if (!data.defeated(sp, world - 1)) {
						sp.sendSystemMessage(Component.translatable("message.matriochka.not_unlocked", world - 1));
						return InteractionResult.FAIL;
					}
					level.setBlock(pos.above(), ModContent.block("planted_seed").defaultBlockState(), 3);
					if (level.getBlockEntity(pos.above()) instanceof DataBlockEntity be) {
						be.data().putInt("world", world);
						be.data().putString("owner", sp.getUUID().toString());
						be.changed();
					}
					stack.consume(1, sp);
					sp.sendSystemMessage(Component.translatable("message.matriochka.seed_planted." + world));
				}
				return InteractionResult.SUCCESS;
			}
			return InteractionResult.TRY_WITH_EMPTY_HAND;
		}

		@Override
		protected boolean isRandomlyTicking(BlockState state) {
			return state.getValue(TILLED);
		}

		@Override
		protected void randomTick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
			if (!level.getBlockState(pos.above()).isAir() && !level.getBlockState(pos.above()).is(ModContent.block("planted_seed"))) {
				level.setBlock(pos, state.setValue(TILLED, false), 3);
			}
		}

		@Override
		public void fallOn(Level level, BlockState state, BlockPos pos, net.minecraft.world.entity.Entity entity, double fall) {
			if (!level.isClientSide() && state.getValue(TILLED) && fall > 1.0 && level.getRandom().nextFloat() < fall - 0.5) {
				level.setBlock(pos, state.setValue(TILLED, false), 3);
			}
			super.fallOn(level, state, pos, entity, fall);
		}
	}

	// ---------------------------------------------------------------- Planted Seed (hatching)
	public static class PlantedSeed extends Block implements EntityBlock {
		private static final VoxelShape SHAPE = Block.box(4, 0, 4, 12, 10, 12);

		public PlantedSeed(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
			return SHAPE;
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
			return level.isClientSide() ? null : (l, p, s, be) -> tickSeed((ServerLevel) l, p, (DataBlockEntity) be);
		}

		/** A seed needs its world's condition (water, heat, redstone...) nearby, then hatches after a short ritual. */
		static void tickSeed(ServerLevel level, BlockPos pos, DataBlockEntity be) {
			int world = be.data().getIntOr("world", 1);
			BlockState soil = level.getBlockState(pos.below());
			if (!(soil.getBlock() instanceof WorldSoil) || !soil.getValue(WorldSoil.TILLED)) {
				level.removeBlock(pos, false);
				Block.popResource(level, pos, new ItemStack(ModContent.item("seed_" + world)));
				return;
			}
			if (!conditionMet(level, pos, world)) {
				if (level.getGameTime() % 40 == 0) level.sendParticles(ParticleTypes.SMOKE, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 3, 0.2, 0.2, 0.2, 0.01);
				return;
			}
			int t = be.data().getIntOr("t", 0) + 1;
			be.data().putInt("t", t);
			if (t % 10 == 0) {
				level.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 12, 0.4, 0.4, 0.4, 0.3);
				level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 0.6f, 0.5f + t / 200f);
			}
			if (t >= 200) {
				level.setBlock(pos.below(), soil.setValue(WorldSoil.TILLED, false), 3);
				level.setBlock(pos, ModContent.block("world_block").defaultBlockState(), 3);
				if (level.getBlockEntity(pos) instanceof DataBlockEntity wb) {
					wb.data().putInt("world", world);
					wb.data().putString("owner", be.data().getStringOr("owner", ""));
					wb.changed();
				}
				level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 60, 0.5, 0.5, 0.5, 0.4);
				level.playSound(null, pos, SoundEvents.CHEST_OPEN, SoundSource.BLOCKS, 1.2f, 0.5f);
				level.playSound(null, pos, SoundEvents.TOTEM_USE, SoundSource.BLOCKS, 0.5f, 1.5f);
			} else {
				be.setChanged();
			}
		}

		public static boolean conditionMet(ServerLevel level, BlockPos pos, int world) {
			return switch (world) {
				case 1, 7 -> near(level, pos, 4, s -> s.getFluidState().is(net.minecraft.tags.FluidTags.WATER));
				case 2 -> near(level, pos, 3, s -> s.getFluidState().is(net.minecraft.tags.FluidTags.LAVA) || s.is(net.minecraft.world.level.block.Blocks.MAGMA_BLOCK) || s.is(net.minecraft.world.level.block.Blocks.CAMPFIRE));
				case 3, 9 -> level.hasNeighborSignal(pos.below()) || level.hasNeighborSignal(pos);
				case 4 -> level.canSeeSky(pos.above());
				case 5 -> level.getMaxLocalRawBrightness(pos) <= 3;
				case 6 -> pos.getY() >= 100;
				case 8 -> { long day = level.getOverworldClockTime() % 24000; yield day > 22500 || day < 1500 || (day > 11500 && day < 13500); }
				default -> true;
			};
		}

		private static boolean near(ServerLevel level, BlockPos pos, int r, java.util.function.Predicate<BlockState> test) {
			for (BlockPos p : BlockPos.betweenClosed(pos.offset(-r, -1, -r), pos.offset(r, 1, r))) {
				if (test.test(level.getBlockState(p))) return true;
			}
			return false;
		}
	}

	// ---------------------------------------------------------------- World Block
	public static class WorldBlock extends Block implements EntityBlock {
		public WorldBlock(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
			return new DataBlockEntity(ModContent.BE_DATA, pos, state);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = be.data().getIntOr("world", 1);
				MatrioData data = MatrioData.get(sp.level().getServer());
				String owner = be.data().getStringOr("owner", "");
				if (!owner.isEmpty() && !data.groupOf(java.util.UUID.fromString(owner)).equals(data.groupOf(sp.getUUID())) && !sp.isCreative()) {
					sp.sendSystemMessage(Component.translatable("message.matriochka.not_your_world"));
					return InteractionResult.FAIL;
				}
				Travel.enter(sp, world, pos);
				Achievements.grantId(sp, "world_" + world + "/a0");
			}
			return InteractionResult.SUCCESS;
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			if (level instanceof ServerLevel sl && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = be.data().getIntOr("world", 1);
				// expel everybody of this group who is inside, without harm
				MatrioData data = MatrioData.get(sl.getServer());
				String group = data.groupOf(player.getUUID());
				for (ServerPlayer p : sl.getServer().getPlayerList().getPlayers()) {
					if (Worlds.number(p.level()) == world && data.groupOf(p.getUUID()).equals(group)) Travel.leave(p);
				}
				ItemStack doll = new ItemStack(ModContent.item("cracked_doll"));
				net.minecraft.nbt.CompoundTag t = new net.minecraft.nbt.CompoundTag();
				t.putInt("world", world);
				t.putString("owner", be.data().getStringOr("owner", ""));
				doll.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(t));
				Block.popResource(level, pos, doll);
				data.worldEntry(group, world).putLong("unstable_until", sl.getGameTime() + 20 * 60 * 20);
				data.changed();
				level.playSound(null, pos, SoundEvents.GLASS_BREAK, SoundSource.BLOCKS, 1f, 0.6f);
			}
			return super.playerWillDestroy(level, pos, state, player);
		}

		@Override
		public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
			if (random.nextInt(3) == 0) {
				level.addParticle(ParticleTypes.END_ROD, pos.getX() + random.nextDouble(), pos.getY() + 1.1, pos.getZ() + random.nextDouble(), 0, 0.02, 0);
			}
		}
	}

	// ---------------------------------------------------------------- Threshold
	public static class Threshold extends Block {
		public Threshold(BlockBehaviour.Properties p) {
			super(p);
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			if (player instanceof ServerPlayer sp) Travel.leave(sp);
			return InteractionResult.SUCCESS;
		}

		@Override
		public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
			level.addParticle(ParticleTypes.PORTAL, pos.getX() + random.nextDouble(), pos.getY() + 1.2, pos.getZ() + random.nextDouble(), 0, 0.1, 0);
		}
	}

	/** Cracked doll placement: restores a broken world block without needing soil. */
	public static boolean placeCrackedDoll(ServerPlayer player, ItemStack stack, BlockPos at) {
		var cd = stack.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
		if (cd == null) return false;
		var t = cd.copyTag();
		ServerLevel level = (ServerLevel) player.level();
		if (!level.getBlockState(at).isAir()) return false;
		level.setBlock(at, ModContent.block("world_block").defaultBlockState(), 3);
		if (level.getBlockEntity(at) instanceof DataBlockEntity be) {
			be.data().putInt("world", t.getIntOr("world", 1));
			be.data().putString("owner", t.getStringOr("owner", player.getUUID().toString()));
			be.changed();
		}
		stack.consume(1, player);
		level.playSound(null, at, SoundEvents.CHEST_CLOSE, SoundSource.BLOCKS, 1f, 0.6f);
		PlayerState.of(player).sync();
		return true;
	}
}
