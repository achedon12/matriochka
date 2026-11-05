package fr.achedon12.matriochka.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * A crack in the World 7 sea floor that breathes out air: a column of bubbles rises from it, and a snorkel helmet
 * swimming in that column refills (see {@link fr.achedon12.matriochka.rules.Snorkel#atAirSource}).
 */
public class AirVent extends Block {
	public AirVent(Properties properties) {
		super(properties);
	}

	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		if (!level.getFluidState(pos.above()).isEmpty()) {
			for (int i = 0; i < 3; i++) {
				level.addParticle(ParticleTypes.BUBBLE_COLUMN_UP, pos.getX() + 0.3 + random.nextDouble() * 0.4, pos.getY() + 1.05,
					pos.getZ() + 0.3 + random.nextDouble() * 0.4, 0, 0.04, 0);
			}
			if (random.nextInt(6) == 0) level.addParticle(ParticleTypes.BUBBLE_POP, pos.getX() + 0.5, pos.getY() + 1.2, pos.getZ() + 0.5, 0, 0.02, 0);
		}
	}
}
