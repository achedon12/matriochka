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

/**
 * One block class for the 13 stations; the station id drives recipes, conditions and the screen. Stations with recipes
 * also take hoppers and comparators (see {@link StationAutomation}).
 */
public class StationBlock extends Block implements EntityBlock, net.minecraft.world.WorldlyContainerHolder {
	public final String station;

	public static final net.minecraft.world.level.block.state.properties.EnumProperty<net.minecraft.core.Direction> FACING =
		net.minecraft.world.level.block.state.properties.BlockStateProperties.HORIZONTAL_FACING;

	/** Outer bounds of each sculpted model facing north, in 16ths (tools/stations3d.py bounds()). */
	private static final java.util.Map<String, int[]> BOUNDS = java.util.Map.ofEntries(
		java.util.Map.entry("matrix_workbench", new int[]{0, 0, 0, 16, 14, 16}),
		java.util.Map.entry("class_table", new int[]{1, 0, 1, 15, 14, 15}),
		java.util.Map.entry("soul_altar", new int[]{0, 0, 0, 16, 13, 16}),
		java.util.Map.entry("spore_vat", new int[]{1, 0, 0, 15, 15, 15}),
		java.util.Map.entry("ash_foundry", new int[]{0, 0, 0, 16, 16, 16}),
		java.util.Map.entry("jailer_table", new int[]{0, 0, 0, 16, 16, 16}),
		java.util.Map.entry("lightning_forge", new int[]{0, 0, 1, 16, 16, 15}),
		java.util.Map.entry("dark_altar", new int[]{0, 0, 2, 16, 16, 16}),
		java.util.Map.entry("inverter", new int[]{1, 0, 1, 15, 16, 15}),
		java.util.Map.entry("abyssal_press", new int[]{0, 0, 0, 16, 16, 16}),
		java.util.Map.entry("time_workshop", new int[]{1, 0, 3, 15, 16, 13}),
		java.util.Map.entry("terrain_anchor", new int[]{0, 0, 0, 16, 16, 16}),
		java.util.Map.entry("final_loom", new int[]{0, 0, 2, 16, 16, 14}));
	private final java.util.Map<net.minecraft.core.Direction, net.minecraft.world.phys.shapes.VoxelShape> shapes = new java.util.EnumMap<>(net.minecraft.core.Direction.class);

	public StationBlock(String station, BlockBehaviour.Properties p) {
		super(p);
		this.station = station;
		registerDefaultState(stateDefinition.any().setValue(FACING, net.minecraft.core.Direction.NORTH));
		int[] b = BOUNDS.getOrDefault(station, new int[]{0, 0, 0, 16, 16, 16});
		for (net.minecraft.core.Direction d : net.minecraft.core.Direction.Plane.HORIZONTAL) {
			// turn the north-facing bounds round the block centre, as the blockstate turns the model
			double x0 = b[0], z0 = b[2], x1 = b[3], z1 = b[5];
			double[] r = switch (d) {
				case EAST -> new double[]{16 - z1, x0, 16 - z0, x1};
				case SOUTH -> new double[]{16 - x1, 16 - z1, 16 - x0, 16 - z0};
				case WEST -> new double[]{z0, 16 - x1, z1, 16 - x0};
				default -> new double[]{x0, z0, x1, z1};
			};
			shapes.put(d, Block.box(r[0], b[1], r[1], r[2], b[4], r[3]));
		}
	}

	@Override
	protected void createBlockStateDefinition(net.minecraft.world.level.block.state.StateDefinition.Builder<Block, BlockState> b) {
		b.add(FACING);
	}

	@Override
	public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext ctx) {
		// the station faces the one who sets it down
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	protected BlockState rotate(BlockState state, net.minecraft.world.level.block.Rotation rot) {
		return state.setValue(FACING, rot.rotate(state.getValue(FACING)));
	}

	@Override
	protected BlockState mirror(BlockState state, net.minecraft.world.level.block.Mirror mirror) {
		return state.rotate(mirror.getRotation(state.getValue(FACING)));
	}

	@Override
	protected net.minecraft.world.phys.shapes.VoxelShape getShape(BlockState state, net.minecraft.world.level.BlockGetter level, BlockPos pos, net.minecraft.world.phys.shapes.CollisionContext ctx) {
		return shapes.get(state.getValue(FACING));
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

	/** Hoppers and droppers see the station's buffer; the Soul Altar and the Class Table have none. */
	@Override
	public net.minecraft.world.@Nullable WorldlyContainer getContainer(BlockState state, net.minecraft.world.level.LevelAccessor level, BlockPos pos) {
		if (!StationAutomation.automatable(station) || !(level.getBlockEntity(pos) instanceof DataBlockEntity be)) return null;
		return new StationInventory(be, station);
	}

	@Override
	protected boolean hasAnalogOutputSignal(BlockState state) {
		return StationAutomation.automatable(station);
	}

	/** A comparator reads how full the buffer is, output included. */
	@Override
	protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos, net.minecraft.core.Direction direction) {
		if (!(level.getBlockEntity(pos) instanceof DataBlockEntity be) || !be.hasItems()) return 0;
		return AbstractContainerMenu.getRedstoneSignalFromContainer(new StationInventory(be, station));
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

	/** Storm Essence held against the Lightning Forge charges it, as a lightning strike would. */
	@Override
	protected InteractionResult useItemOn(net.minecraft.world.item.ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, net.minecraft.world.InteractionHand hand, BlockHitResult hit) {
		if (station.equals("lightning_forge") && stack.is(ModContent.item("storm_essence"))) {
			if (player instanceof ServerPlayer sp && level.getBlockEntity(pos) instanceof DataBlockEntity be) {
				if (Stations.feedEssence(sp, (ServerLevel) level, pos, be)) {
					sp.sendOverlayMessage(Component.translatable("message.matriochka.station.forge_fed", be.data().getIntOr("charge", 0)));
				}
			}
			return InteractionResult.SUCCESS;
		}
		return InteractionResult.TRY_WITH_EMPTY_HAND;
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
