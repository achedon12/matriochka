package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.ChatFormatting;
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
			if (id.equals("seed_1") && state.getValue(TILLED) && level.getBlockState(pos.above()).isAir()) {
				int world = 1;
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
						be.data().putInt("karma", PlayerState.of(sp).karma());
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
		/** The world this Seed or rite opens; it picks the model (the Seed for World 1, the rite object after). */
		public static final net.minecraft.world.level.block.state.properties.IntegerProperty WORLD =
			net.minecraft.world.level.block.state.properties.IntegerProperty.create("world", 1, 10);

		public PlantedSeed(BlockBehaviour.Properties p) {
			super(p);
			registerDefaultState(stateDefinition.any().setValue(WORLD, 1));
		}

		@Override
		protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
			b.add(WORLD);
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

		/** Feeding a hatching Seed leans its world calm or wild (see Variants). */
		@Override
		protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
			if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				// only the planter's group may lean its Seed
				if (!MatrioData.get(sl.getServer()).sameGroup(be.data().getStringOr("owner", ""), sp)) {
					sp.sendOverlayMessage(Component.translatable("message.matriochka.not_yours"));
					return InteractionResult.FAIL;
				}
				// a Storm Essence opens the Storm Rod without waiting for a storm
				if (be.data().getIntOr("world", 1) == 4 && be.data().getBooleanOr("rite", false) && stack.is(ModContent.item("storm_essence"))
					&& !be.data().getBooleanOr("charged", false)) {
					be.data().putBoolean("charged", true);
					be.setChanged();
					stack.consume(1, sp);
					sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 30, 0.3, 0.4, 0.3, 0.3);
					return InteractionResult.SUCCESS;
				}
				if (fr.achedon12.matriochka.world.Variants.feed(sl, pos, be.data(), stack, sp)) {
					be.setChanged();
					return InteractionResult.SUCCESS;
				}
				return InteractionResult.TRY_WITH_EMPTY_HAND;
			}
			return InteractionResult.SUCCESS;
		}

		/** A seed needs its world's condition (water, heat, redstone...) nearby, then hatches after a short ritual. */
		static void tickSeed(ServerLevel level, BlockPos pos, DataBlockEntity be) {
			int world = be.data().getIntOr("world", 1);
			boolean rite = be.data().getBooleanOr("rite", false);
			BlockState soil = level.getBlockState(pos.below());
			// a Seed lives on its tilled soil; a rite site on the spot its rite asks for (world/Rites.java)
			boolean standing = rite ? fr.achedon12.matriochka.world.Rites.stillFits(level, pos, world)
				: soil.getBlock() instanceof WorldSoil && soil.getValue(WorldSoil.TILLED);
			if (!standing) {
				level.removeBlock(pos, false);
				Block.popResource(level, pos, new ItemStack(ModContent.item("seed_" + world)));
				return;
			}
			boolean met = rite ? fr.achedon12.matriochka.world.Rites.ready(level, pos, world, be) : conditionMet(level, pos, world);
			if (!met) {
				if (level.getGameTime() % 40 == 0) level.sendParticles(ParticleTypes.SMOKE, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 3, 0.2, 0.2, 0.2, 0.01);
				// the planter reads what the rite still waits for
				if (rite && level.getGameTime() % 100 == 0) {
					String owner = be.data().getStringOr("owner", "");
					var op = owner.isEmpty() ? null : level.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(owner));
					if (op != null && op.blockPosition().closerThan(pos, 24)) op.sendOverlayMessage(Component.translatable("message.matriochka.rite.wait." + world));
				}
				return;
			}
			int t = be.data().getIntOr("t", 0) + 1;
			be.data().putInt("t", t);
			if (t % 10 == 0) {
				level.sendParticles(ParticleTypes.ENCHANT, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 12, 0.4, 0.4, 0.4, 0.3);
				level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.SEED_PULSE, SoundSource.BLOCKS, 0.5f, 0.6f + t / 250f);
				// a rite under way sounds like its world: embers, a turning key, a storm, a breath, glass, water, leaves, rock
				if (rite && t % 30 == 0) level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.rite(world), SoundSource.BLOCKS, 0.9f, 0.85f + t / 600f);
			}
			if (t >= 200) {
				String seedOwner = be.data().getStringOr("owner", "");
				MatrioData md = MatrioData.get(level.getServer());
				String seedGroup = seedOwner.isEmpty() ? "" : md.groupOf(java.util.UUID.fromString(seedOwner));
				if (!seedGroup.isEmpty() && md.hasWorldBlock(level.getServer(), seedGroup, world)) {
					// one World Block per world and group: the Seed waits until the old one is broken
					be.data().putInt("t", 199);
					be.setChanged();
					if (level.getGameTime() % 100 == 0) {
						var op = level.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(seedOwner));
						if (op != null) op.sendOverlayMessage(Component.translatable("message.matriochka.world_exists", world));
					}
					return;
				}
				if (!seedGroup.isEmpty() && !md.mayOpen(seedGroup)) {
					// the server's limit on active groups or parcels is reached: the Seed waits for room
					be.data().putInt("t", 199);
					be.setChanged();
					if (level.getGameTime() % 100 == 0) {
						var op = level.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(seedOwner));
						if (op != null) op.sendOverlayMessage(Component.translatable("message.matriochka.server_full"));
					}
					return;
				}
				if (!rite) level.setBlock(pos.below(), soil.setValue(WorldSoil.TILLED, false), 3);
				level.setBlock(pos, ModContent.block("world_block").defaultBlockState(), 3);
				if (level.getBlockEntity(pos) instanceof DataBlockEntity wb) {
					wb.data().putInt("world", world);
					wb.data().putString("owner", seedOwner);
					if (!seedGroup.isEmpty()) wb.data().putInt("cycle", fr.achedon12.matriochka.world.Cycles.of(md, seedGroup));
					// the variant is chosen now, from what the Seed was fed, its surroundings and the planter's karma
					wb.data().putString("variant", fr.achedon12.matriochka.world.Variants.hatch(level, pos, be.data(), seedGroup, world, seedOwner));
					wb.changed();
					if (!seedGroup.isEmpty()) md.setWorldBlock(seedGroup, world, level, pos);
					// the last Seed opens the Giant Workshop: the base around it is captured for the scale model
					if (world == 10 && !seedGroup.isEmpty()) fr.achedon12.matriochka.world.BaseModel.capture(level, pos, md, seedGroup);
				}
				level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 60, 0.5, 0.5, 0.5, 0.4);
				level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.WORLD_BLOCK_FORM, SoundSource.BLOCKS, 1.5f, 1f);
				if (rite) level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.riteOpen(world), SoundSource.BLOCKS, 1.6f, 1f);
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

		/** Striking the block with a Doll Mallet shakes the world inside to hinder those in it. */
		@Override
		protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
			if (stack.is(ModContent.item("doll_mallet"))) {
				if (player instanceof ServerPlayer sp && level instanceof ServerLevel sl) shakeBy(sp, sl, pos, true);
				return InteractionResult.SUCCESS;
			}
			return InteractionResult.TRY_WITH_EMPTY_HAND;
		}

		static void shakeBy(ServerPlayer sp, ServerLevel level, BlockPos pos, boolean hinder) {
			var result = fr.achedon12.matriochka.world.ScaleLinks.shake(sp, level, pos, hinder);
			ChatFormatting color = switch (result) {
				case HELPED -> ChatFormatting.AQUA;
				case HINDERED -> ChatFormatting.RED;
				default -> ChatFormatting.GRAY;
			};
			sp.sendOverlayMessage(Component.translatable("message.matriochka.shake." + result.name().toLowerCase(java.util.Locale.ROOT)).withStyle(color));
		}

		@Override
		protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
			// sneaking with empty hands: shake the world inside to help those in it, rather than entering
			if (player instanceof ServerPlayer sp && sp.isSecondaryUseActive() && level instanceof ServerLevel sl) {
				shakeBy(sp, sl, pos, false);
				return InteractionResult.SUCCESS;
			}
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = be.data().getIntOr("world", 1);
				MatrioData data = MatrioData.get(sp.level().getServer());
				String owner = be.data().getStringOr("owner", "");
				if (!owner.isEmpty() && !data.groupOf(java.util.UUID.fromString(owner)).equals(data.groupOf(sp.getUUID())) && !sp.isCreative()) {
					sp.sendSystemMessage(Component.translatable("message.matriochka.not_your_world"));
					return InteractionResult.FAIL;
				}
				String group = owner.isEmpty() ? data.groupOf(sp.getUUID()) : data.groupOf(java.util.UUID.fromString(owner));
				if (be.data().getIntOr("cycle", 0) < fr.achedon12.matriochka.world.Cycles.of(data, group)) {
					// a World Block of an older cycle: its prison was closed again by the New Cycle
					data.clearWorldBlock(group, world, pos);
					level.destroyBlock(pos, false);
					sp.sendSystemMessage(Component.translatable("message.matriochka.cycle.old_block"));
					return InteractionResult.SUCCESS;
				}
				Travel.enter(sp, world, pos);
				Achievements.grantId(sp, "world_" + world + "/a0");
			}
			return InteractionResult.SUCCESS;
		}

		@Override
		protected float getDestroyProgress(BlockState state, Player player, net.minecraft.world.level.BlockGetter level, BlockPos pos) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be
				&& !MatrioData.get(sp.level().getServer()).sameGroup(be.data().getStringOr("owner", ""), sp)) {
				if (sp.level().getGameTime() % 20 == 0) sp.sendOverlayMessage(Component.translatable("message.matriochka.not_yours"));
				return 0f;
			}
			return super.getDestroyProgress(state, player, level, pos);
		}

		@Override
		public BlockState playerWillDestroy(Level level, BlockPos pos, BlockState state, Player player) {
			if (level instanceof ServerLevel sl && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				int world = be.data().getIntOr("world", 1);
				// expel everybody of the owner's group who is inside, without harm
				MatrioData data = MatrioData.get(sl.getServer());
				String owner = be.data().getStringOr("owner", "");
				String group = owner.isEmpty() ? data.groupOf(player.getUUID()) : data.groupOf(java.util.UUID.fromString(owner));
				data.clearWorldBlock(group, world, pos);
				for (ServerPlayer p : sl.getServer().getPlayerList().getPlayers()) {
					if (Worlds.number(p.level()) == world && data.groupOf(p.getUUID()).equals(group)) Travel.leave(p);
				}
				if (fr.achedon12.matriochka.world.Config.hardcore()) {
					// hardcore: the world goes with its block, for good
					fr.achedon12.matriochka.world.WorldAdmin.reset(sl.getServer(), group, world);
					for (ServerPlayer p : sl.getServer().getPlayerList().getPlayers()) {
						if (data.groupOf(p.getUUID()).equals(group)) p.sendSystemMessage(Component.translatable("message.matriochka.world_deleted", world));
					}
					level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.WORLD_BLOCK_CRACK, SoundSource.BLOCKS, 1.2f, 0.7f);
					return super.playerWillDestroy(level, pos, state, player);
				}
				ItemStack doll = new ItemStack(ModContent.item("cracked_doll"));
				net.minecraft.nbt.CompoundTag t = new net.minecraft.nbt.CompoundTag();
				t.putInt("world", world);
				t.putString("owner", be.data().getStringOr("owner", ""));
				t.putInt("cycle", be.data().getIntOr("cycle", 0));
				doll.set(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.of(t));
				Block.popResource(level, pos, doll);
				data.worldEntry(group, world).putLong("unstable_until", sl.getGameTime() + 20 * 60 * 20);
				data.changed();
				level.playSound(null, pos, fr.achedon12.matriochka.content.Sounds.WORLD_BLOCK_CRACK, SoundSource.BLOCKS, 1.2f, 1f);
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
			if (player instanceof ServerPlayer sp) {
				if (fr.achedon12.matriochka.world.Refuge.inRefuge(level)) fr.achedon12.matriochka.world.Refuge.leave(sp);
				else Travel.leave(sp);
			}
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
		int world = t.getIntOr("world", 1);
		String owner = t.getStringOr("owner", player.getUUID().toString());
		MatrioData md = MatrioData.get(level.getServer());
		String group = md.groupOf(java.util.UUID.fromString(owner.isEmpty() ? player.getUUID().toString() : owner));
		int cycle = fr.achedon12.matriochka.world.Cycles.of(md, group);
		if (t.getIntOr("cycle", 0) < cycle) {
			stack.consume(1, player);
			player.sendSystemMessage(Component.translatable("message.matriochka.cycle.old_block"));
			return false;
		}
		if (md.hasWorldBlock(level.getServer(), group, world)) {
			player.sendOverlayMessage(Component.translatable("message.matriochka.world_exists", world));
			return false;
		}
		level.setBlock(at, ModContent.block("world_block").defaultBlockState(), 3);
		if (level.getBlockEntity(at) instanceof DataBlockEntity be) {
			be.data().putInt("world", world);
			be.data().putString("owner", owner);
			be.data().putInt("cycle", cycle);
			be.data().putString("variant", fr.achedon12.matriochka.world.Variants.of(md, group, world));
			be.changed();
		}
		md.setWorldBlock(group, world, level, at);
		stack.consume(1, player);
		level.playSound(null, at, fr.achedon12.matriochka.content.Sounds.DOLL_CLOSE, SoundSource.BLOCKS, 1f, 0.8f);
		PlayerState.of(player).sync();
		return true;
	}
}
