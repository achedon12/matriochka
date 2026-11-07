package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.Blocks2;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * The way into each world. World 1 opens with its Seed, planted on tilled World Soil (block/Blocks2.WorldSoil); every
 * other world has its own object (ids seed_2..seed_10, named in tools/content.py RITES) and its own rite: where the
 * object is set down and what it waits for. Set down, the object becomes a rite site (the Planted Seed block, flagged
 * "rite", drawn as that object), which hatches into the World Block like a Seed once its condition holds.
 * <ul>
 * <li>2 Ember Heart: lava within 3 blocks and 4 Ashrock around it;</li>
 * <li>3 Jailer's Key: against an iron door, with a redstone signal;</li>
 * <li>4 Storm Rod: on top of a lightning rod under the open sky, opened by a storm or a Storm Essence;</li>
 * <li>5 Black Lantern: complete darkness and 4 Spent Glow within 2 blocks;</li>
 * <li>6 Twin Mirrors: glass two blocks away on both sides, along one axis;</li>
 * <li>7 Abyssal Pearl: dropped into water 3 blocks deep;</li>
 * <li>8 Sapling of the Four Seasons: planted on grass or dirt, opens at dawn or dusk;</li>
 * <li>9 Seismic Stake: driven into stone or deepslate below y 40;</li>
 * <li>10 Traveller's Matryoshka: anywhere.</li>
 * </ul>
 */
public final class Rites {
	private Rites() {}

	public static void init() {
		UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
			ItemStack stack = player.getItemInHand(hand);
			int world = worldOf(stack);
			if (world < 2) return InteractionResult.PASS;
			if (!(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl)) return InteractionResult.SUCCESS;
			return use(sp, sl, hit, stack, world);
		});
	}

	/** The world a rite object opens, or 0 (World 1's Seed counts as 1 and keeps its soil). */
	public static int worldOf(ItemStack stack) {
		String id = ModContent.idOf(stack.getItem());
		if (!id.startsWith("seed_")) return 0;
		try {
			return Integer.parseInt(id.substring(5));
		} catch (NumberFormatException e) {
			return 0;
		}
	}

	private static InteractionResult use(ServerPlayer sp, ServerLevel level, BlockHitResult hit, ItemStack stack, int world) {
		MatrioData data = MatrioData.get(level.getServer());
		if (!data.defeated(sp, world - 1)) {
			sp.sendSystemMessage(Component.translatable("message.matriochka.not_unlocked", world - 1));
			return InteractionResult.FAIL;
		}
		BlockPos clicked = hit.getBlockPos();
		BlockPos at = clicked.relative(hit.getDirection());
		// a rite site is placed like a block: spawn protection, adventure mode and claims apply
		if (!sp.mayBuild() || !level.mayInteract(sp, at) || !sp.mayUseItemAt(at, hit.getDirection(), stack)) return InteractionResult.FAIL;
		// the pearl sinks: clicked on the sea floor or a block beside water, it goes into the water there
		boolean water = level.getFluidState(at).is(FluidTags.WATER) && level.getFluidState(at).isSource();
		if (!(level.getBlockState(at).isAir() || (world == 7 && water))) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.rite.no_room"));
			return InteractionResult.FAIL;
		}
		String place = placement(level, at, world);
		if (place != null) {
			sp.sendOverlayMessage(Component.translatable(place));
			return InteractionResult.FAIL;
		}
		BlockState site = ModContent.block("planted_seed").defaultBlockState().setValue(Blocks2.PlantedSeed.WORLD, world);
		level.setBlock(at, site, 3);
		if (level.getBlockEntity(at) instanceof DataBlockEntity be) {
			be.data().putInt("world", world);
			be.data().putBoolean("rite", true);
			be.data().putString("owner", sp.getUUID().toString());
			be.data().putInt("karma", PlayerState.of(sp).karma());
			be.changed();
		}
		stack.consume(1, sp);
		// the Journal's collection remembers the rites this player has performed
		PlayerState ps = PlayerState.of(sp);
		if (!ps.has("rite_" + world)) {
			ps.set("rite_" + world, true);
			ps.sync();
		}
		level.playSound(null, at, fr.achedon12.matriochka.content.Sounds.SEED_PULSE, SoundSource.BLOCKS, 0.8f, 0.7f);
		sp.sendSystemMessage(Component.translatable("item.matriochka.seed_" + world + ".desc"));
		return InteractionResult.SUCCESS;
	}

	/** What the spot itself must be, checked when the object is set down: null when it fits, else a message key. */
	private static String placement(ServerLevel level, BlockPos at, int world) {
		BlockState below = level.getBlockState(at.below());
		return switch (world) {
			case 4 -> below.getBlock() instanceof net.minecraft.world.level.block.LightningRodBlock ? null : "message.matriochka.rite.place.4";
			case 7 -> level.getFluidState(at).is(FluidTags.WATER) ? null : "message.matriochka.rite.place.7";
			case 8 -> soil(below) ? null : "message.matriochka.rite.place.8";
			case 9 -> (below.is(BlockTags.BASE_STONE_OVERWORLD) || below.is(Blocks.DEEPSLATE) || below.is(Blocks.STONE)) && at.getY() <= 40 ? null : "message.matriochka.rite.place.9";
			default -> null;
		};
	}

	/** Grass or dirt the sapling takes root in. */
	private static boolean soil(BlockState s) {
		return s.is(BlockTags.DIRT) || s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.DIRT) || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.PODZOL)
			|| s.is(Blocks.MYCELIUM) || s.is(Blocks.ROOTED_DIRT) || s.is(Blocks.MOSS_BLOCK);
	}

	/** Whether a rite site still stands where it should (else it pops back into its object). */
	public static boolean stillFits(ServerLevel level, BlockPos pos, int world) {
		return switch (world) {
			case 4 -> level.getBlockState(pos.below()).getBlock() instanceof net.minecraft.world.level.block.LightningRodBlock;
			case 8 -> soil(level.getBlockState(pos.below()));
			case 9 -> !level.getBlockState(pos.below()).isAir();
			default -> true;
		};
	}

	/** The condition a rite waits for before it opens its world. */
	public static boolean ready(ServerLevel level, BlockPos pos, int world, DataBlockEntity be) {
		return switch (world) {
			case 2 -> near(level, pos, 3, s -> s.getFluidState().is(FluidTags.LAVA)) && count(level, pos, 3, s -> s.is(ModContent.block("ashrock"))) >= 4;
			case 3 -> (level.hasNeighborSignal(pos) || level.hasNeighborSignal(pos.below()))
				&& near(level, pos, 1, s -> s.is(Blocks.IRON_DOOR));
			case 4 -> level.canSeeSky(pos.above()) && (level.isThundering() || be.data().getBooleanOr("charged", false));
			case 5 -> level.getMaxLocalRawBrightness(pos) == 0 && count(level, pos, 2, s -> s.is(ModContent.block("spent_glow"))) >= 4;
			case 6 -> mirrored(level, pos, Direction.EAST) || mirrored(level, pos, Direction.SOUTH);
			case 7 -> deepWater(level, pos);
			case 8 -> { long t = level.getOverworldClockTime() % 24000; yield t > 22500 || t < 1500 || (t > 11500 && t < 13500); }
			case 9 -> pos.getY() <= 40;
			default -> true;
		};
	}

	/** Glass two blocks away on both sides along one axis. */
	private static boolean mirrored(ServerLevel level, BlockPos pos, Direction d) {
		return glass(level.getBlockState(pos.relative(d, 2))) && glass(level.getBlockState(pos.relative(d.getOpposite(), 2)));
	}

	private static boolean glass(BlockState s) {
		return s.is(Blocks.GLASS) || s.is(Blocks.TINTED_GLASS) || s.is(Blocks.GLASS_PANE) || s.is(net.minecraft.tags.BlockTags.IMPERMEABLE);
	}

	/** Water above and around for at least 3 blocks of depth. */
	private static boolean deepWater(ServerLevel level, BlockPos pos) {
		int depth = 0;
		for (int dy = 0; dy < 6; dy++) if (level.getFluidState(pos.above(dy)).is(FluidTags.WATER)) depth++;
		// the site replaced the water it sank into: count the column above and the water beside it
		boolean beside = false;
		for (Direction d : Direction.Plane.HORIZONTAL) beside |= level.getFluidState(pos.relative(d)).is(FluidTags.WATER);
		return beside && depth + 1 >= 3;
	}

	private static boolean near(ServerLevel level, BlockPos pos, int r, java.util.function.Predicate<BlockState> test) {
		return count(level, pos, r, test) > 0;
	}

	private static int count(ServerLevel level, BlockPos pos, int r, java.util.function.Predicate<BlockState> test) {
		int n = 0;
		for (BlockPos p : BlockPos.betweenClosed(pos.offset(-r, -1, -r), pos.offset(r, 1, r))) if (test.test(level.getBlockState(p))) n++;
		return n;
	}
}
