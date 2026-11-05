package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.net.StationMenu;
import net.fabricmc.fabric.api.menu.v1.ExtendedMenuProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
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

/** One block class for the 13 stations; the station id drives recipes, conditions and the screen. */
public class StationBlock extends Block implements EntityBlock {
	public final String station;

	public StationBlock(String station, BlockBehaviour.Properties p) {
		super(p);
		this.station = station;
	}

	@Override
	public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new DataBlockEntity(ModContent.BE_DATA, pos, state);
	}

	@Override
	public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		if (level.isClientSide()) return null;
		return (l, p, s, be) -> Stations.tick((ServerLevel) l, p, station, (DataBlockEntity) be);
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (player instanceof ServerPlayer sp) {
			sp.openMenu(new ExtendedMenuProvider<StationMenu.Data>() {
				@Override
				public StationMenu.Data getScreenOpeningData(ServerPlayer p) {
					return new StationMenu.Data(pos, station);
				}

				@Override
				public Component getDisplayName() {
					return Component.translatable("block.matriochka." + station);
				}

				@Override
				public AbstractContainerMenu createMenu(int id, Inventory inv, Player p) {
					return new StationMenu(id, inv, new StationMenu.Data(pos, station));
				}
			});
		}
		return InteractionResult.SUCCESS;
	}

	@Override
	public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
		if (random.nextInt(4) != 0) return;
		var particle = switch (station) {
			case "spore_vat" -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case "ash_foundry" -> ParticleTypes.FLAME;
			case "lightning_forge" -> ParticleTypes.ELECTRIC_SPARK;
			case "dark_altar" -> ParticleTypes.SCULK_SOUL;
			case "inverter" -> ParticleTypes.REVERSE_PORTAL;
			case "abyssal_press" -> ParticleTypes.BUBBLE_COLUMN_UP;
			case "time_workshop" -> ParticleTypes.WAX_ON;
			case "terrain_anchor" -> ParticleTypes.ASH;
			case "soul_altar" -> ParticleTypes.SOUL;
			default -> ParticleTypes.ENCHANT;
		};
		level.addParticle(particle, pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.6, pos.getY() + 1.05, pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.6, 0, 0.03, 0);
	}
}
