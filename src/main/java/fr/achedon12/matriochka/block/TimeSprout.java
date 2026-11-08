package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * A Time Seed planted in World 8 (world/WorldOres.plant): it grows in the hastened time of the Seasons far faster
 * than any crop, a stage every half minute (tools/content.py ORE_RULES sprout_stage_ticks), on its own clock rather
 * than at random, and ripens in two minutes into a Chrono Shard (its loot table: the shard when ripe, the seed back
 * before).
 */
public class TimeSprout extends Block {
	public static final IntegerProperty AGE = IntegerProperty.create("age", 0, 3);
	public static final int RIPE = 3;
	private static final VoxelShape[] SHAPES = {Block.box(5, 0, 5, 11, 5, 11), Block.box(4, 0, 4, 12, 8, 12),
		Block.box(4, 0, 4, 12, 11, 12), Block.box(4, 0, 4, 12, 14, 12)};

	public TimeSprout(BlockBehaviour.Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(AGE, 0));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(AGE);
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return SHAPES[state.getValue(AGE)];
	}

	/** On grass or dirt, as a crop would stand (the seed is only planted there, see world/WorldOres.plant). */
	public static boolean soil(BlockState below) {
		return below.is(net.minecraft.tags.BlockTags.DIRT) || below.is(net.minecraft.world.level.block.Blocks.FARMLAND) || below.is(ModContent.block("chrono_grass"));
	}

	@Override
	protected boolean canSurvive(BlockState state, net.minecraft.world.level.LevelReader level, BlockPos pos) {
		return soil(level.getBlockState(pos.below()));
	}

	@Override
	protected void onPlace(BlockState state, Level level, BlockPos pos, BlockState old, boolean moved) {
		super.onPlace(state, level, pos, old, moved);
		if (!level.isClientSide() && !old.is(this) && state.getValue(AGE) < RIPE) level.scheduleTick(pos, this, Content.ORE_SPROUT_STAGE_TICKS);
	}

	/** One stage more; the ripe one rings like a clock. */
	@Override
	protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
		int age = state.getValue(AGE);
		if (age >= RIPE) return;
		level.setBlock(pos, state.setValue(AGE, age + 1), 2);
		level.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.4, pos.getZ() + 0.5, 6, 0.25, 0.25, 0.25, 0);
		if (age + 1 == RIPE) {
			level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1f, 1.5f);
			level.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 8, 0.2, 0.3, 0.2, 0.02);
		} else {
			level.scheduleTick(pos, this, Content.ORE_SPROUT_STAGE_TICKS);
		}
	}
}
