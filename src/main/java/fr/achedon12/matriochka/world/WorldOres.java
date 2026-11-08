package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * How each world's ore is had (tools/content.py WORLD_ORES, ORE_RULES): the Spore Crystal grows on the blooms that
 * stand near water, the Living Ember only stays alight in a hot hand, the Silent Stone shatters at any noise, the
 * Inverted Ore falls upwards, the lightning of World 4 fuses the ground into fulgurite, the creatures of World 7 carry
 * Brine Crystals. The Golden Ward and the Time Seed lie in chests (structure/Rewards), the Chrono Shard ripens from
 * the seed (block/TimeSprout), the Heartstones fall with the Heart of the Terrain (entity/MatrioBoss), and the
 * Artisan's Thread is mined like any ore.
 */
public final class WorldOres {
	private WorldOres() {}

	/** Inverted Ore rising after it was mined, and when it is gone if nobody caught it. */
	private record Rising(ItemEntity item, long until) {}

	private static final List<Rising> RISING = new ArrayList<>();
	public static final String RISING_TAG = "matriochka.rising";

	public static void init() {
		PlayerBlockBreakEvents.AFTER.register((level, player, pos, state, be) -> {
			if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) broken(sl, sp, pos, state);
		});
		// World 4: a bolt that strikes cloudstone or sand fuses it (the rule's own bolts, a storm's, a javelin's)
		ServerEntityEvents.ENTITY_LOAD.register((e, level) -> {
			if (e instanceof LightningBolt bolt && Worlds.number(level) == 4) fuse(level, bolt.position());
		});
		ServerTickEvents.END_SERVER_TICK.register(server -> rise());
		ServerLifecycleEvents.SERVER_STOPPED.register(server -> RISING.clear());
	}

	/** Whether the item is one of the ten world ores (the cradle's), and of which world (0: none). */
	public static int worldOf(ItemStack stack) {
		String id = ModContent.idOf(stack.getItem());
		for (int w = 1; w <= 10; w++) if (Content.WORLD_ORES[w].equals(id)) return w;
		return 0;
	}

	public static ItemStack ore(int world) {
		return new ItemStack(ModContent.item(Content.WORLD_ORES[world]));
	}

	// ---------------------------------------------------------------- mined
	private static void broken(ServerLevel level, ServerPlayer p, BlockPos pos, BlockState state) {
		if (p.isCreative()) return;
		Vec3 c = Vec3.atCenterOf(pos);
		if (state.is(ModContent.block("spore_bloom"))) {
			if (nearWater(level, pos) && p.getRandom().nextFloat() < Content.ORE_SPORE_CHANCE) {
				net.minecraft.world.level.block.Block.popResource(level, pos, new ItemStack(ModContent.item("spore_crystal")));
				level.sendParticles(ParticleTypes.HAPPY_VILLAGER, c.x, c.y, c.z, 10, 0.3, 0.3, 0.3, 0);
				level.playSound(null, pos, SoundEvents.AMETHYST_CLUSTER_BREAK, SoundSource.BLOCKS, 0.8f, 1.4f);
			}
			return;
		}
		if (!p.hasCorrectToolForDrops(state)) return;
		PlayerState ps = PlayerState.of(p);
		if (state.is(ModContent.block("living_ember_ore"))) {
			if (ps.gauge("heat") >= Content.ORE_EMBER_HEAT) {
				net.minecraft.world.level.block.Block.popResource(level, pos, new ItemStack(ModContent.item("living_ember")));
				level.sendParticles(ParticleTypes.FLAME, c.x, c.y, c.z, 14, 0.3, 0.3, 0.3, 0.03);
				level.playSound(null, pos, SoundEvents.FIRECHARGE_USE, SoundSource.BLOCKS, 0.7f, 1.3f);
			} else {
				// it goes out: a hiss, a puff of smoke, ash
				net.minecraft.world.level.block.Block.popResource(level, pos, new ItemStack(ModContent.item("ashrock")));
				level.sendParticles(ParticleTypes.LARGE_SMOKE, c.x, c.y, c.z, 12, 0.3, 0.3, 0.3, 0.02);
				level.sendParticles(ParticleTypes.WHITE_ASH, c.x, c.y, c.z, 30, 0.4, 0.4, 0.4, 0.02);
				level.playSound(null, pos, SoundEvents.FIRE_EXTINGUISH, SoundSource.BLOCKS, 1f, 0.8f);
				p.sendOverlayMessage(Component.translatable("message.matriochka.ember.out").withStyle(ChatFormatting.GRAY));
			}
			return;
		}
		if (state.is(ModContent.block("silent_stone_ore"))) {
			if (ps.gauge("noise") > 0f) {
				level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, state), c.x, c.y, c.z, 40, 0.3, 0.3, 0.3, 0.15);
				level.playSound(null, pos, SoundEvents.GLASS_BREAK, SoundSource.BLOCKS, 1f, 0.6f);
				p.sendOverlayMessage(Component.translatable("message.matriochka.silent.shattered").withStyle(ChatFormatting.BLUE));
			} else {
				net.minecraft.world.level.block.Block.popResource(level, pos, new ItemStack(ModContent.item("silent_stone")));
				level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 0.4f, 0.6f);
			}
			return;
		}
		if (state.is(ModContent.block("hanging_ore"))) {
			risingDrop(level, c, new ItemStack(ModContent.item("inverted_ore")));
			p.sendOverlayMessage(Component.translatable("message.matriochka.inverted.rises").withStyle(ChatFormatting.LIGHT_PURPLE));
		}
	}

	/** Water within the reach the Spore Crystal needs of the bloom. */
	public static boolean nearWater(ServerLevel level, BlockPos pos) {
		int r = Content.ORE_SPORE_WATER;
		for (BlockPos q : BlockPos.betweenClosed(pos.offset(-r, -r, -r), pos.offset(r, r, r))) {
			if (level.getFluidState(q).is(FluidTags.WATER)) return true;
		}
		return false;
	}

	// ---------------------------------------------------------------- the ore that falls upwards
	/** Drops a stack that falls upwards for a few seconds, then is gone if nobody caught it. */
	public static ItemEntity risingDrop(ServerLevel level, Vec3 at, ItemStack stack) {
		ItemEntity item = new ItemEntity(level, at.x, at.y, at.z, stack);
		item.setNoGravity(true);
		item.setDeltaMovement(0, 0.09, 0);
		item.setNoPickUpDelay();
		item.addTag(RISING_TAG);
		level.addFreshEntity(item);
		RISING.add(new Rising(item, level.getGameTime() + Content.ORE_INVERTED_RISE_TICKS));
		level.playSound(null, BlockPos.containing(at), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 0.8f, 1.6f);
		return item;
	}

	private static void rise() {
		for (Iterator<Rising> it = RISING.iterator(); it.hasNext(); ) {
			Rising r = it.next();
			ItemEntity e = r.item();
			if (e.isRemoved() || !(e.level() instanceof ServerLevel level)) {
				it.remove();
				continue;
			}
			// it keeps falling up at the same pace, a trail of its colour behind it
			e.setDeltaMovement(e.getDeltaMovement().x * 0.9, 0.09, e.getDeltaMovement().z * 0.9);
			if (level.getGameTime() % 3 == 0) level.sendParticles(new DustParticleOptions(0x4ad8c8, 0.9f), e.getX(), e.getY() + 0.1, e.getZ(), 1, 0.05, 0.05, 0.05, 0);
			if (level.getGameTime() >= r.until()) {
				level.sendParticles(ParticleTypes.REVERSE_PORTAL, e.getX(), e.getY() + 0.2, e.getZ(), 20, 0.2, 0.2, 0.2, 0.05);
				e.discard();
				it.remove();
			}
		}
	}

	// ---------------------------------------------------------------- World 4: fulgurite
	/** A bolt lands at `at`: the cloudstone (under its grass too) or the sand it strikes fuses into fulgurite. */
	public static boolean fuse(ServerLevel level, Vec3 at) {
		BlockPos hit = BlockPos.containing(at.x, at.y - 0.01, at.z);
		for (int k = 0; k < 2; k++) {
			BlockState s = level.getBlockState(hit);
			if (s.is(ModContent.block("skygrass")) || s.isAir()) {
				hit = hit.below();
				continue;
			}
			if (s.is(ModContent.block("cloudstone")) || s.is(Blocks.SAND) || s.is(Blocks.RED_SAND)) {
				level.setBlock(hit, ModContent.block("fulgurite_ore").defaultBlockState(), 3);
				Vec3 c = Vec3.atCenterOf(hit);
				level.sendParticles(ParticleTypes.ELECTRIC_SPARK, c.x, c.y + 0.6, c.z, 30, 0.4, 0.2, 0.4, 0.2);
				level.sendParticles(ParticleTypes.LARGE_SMOKE, c.x, c.y + 0.6, c.z, 6, 0.3, 0.2, 0.3, 0.01);
				return true;
			}
			return false;
		}
		return false;
	}

	// ---------------------------------------------------------------- World 7 and World 9
	/** Whether a creature of World 7, rolling `roll` (0 to 1), carries a Brine Crystal. */
	public static boolean brine(int world, float roll) {
		return world == 7 && roll < Content.ORE_BRINE_CHANCE;
	}

	/** How many Heartstones the Heart of the Terrain leaves: two or three. */
	public static int heartstones(RandomSource r) {
		return Content.ORE_HEARTSTONES[0] + r.nextInt(Content.ORE_HEARTSTONES[1] - Content.ORE_HEARTSTONES[0] + 1);
	}

	// ---------------------------------------------------------------- World 8: the Time Seed
	/** Plants a Time Seed on the grass or dirt at `soil`, in World 8 only. Returns true when it was planted. */
	public static boolean plant(ServerLevel level, ServerPlayer player, BlockPos soil, ItemStack stack) {
		if (Worlds.number(level) != 8) {
			player.sendOverlayMessage(Component.translatable("message.matriochka.time_seed.world").withStyle(ChatFormatting.GOLD));
			return false;
		}
		BlockState s = level.getBlockState(soil);
		boolean ground = fr.achedon12.matriochka.block.TimeSprout.soil(s);
		if (!ground || !level.getBlockState(soil.above()).isAir()) {
			player.sendOverlayMessage(Component.translatable("message.matriochka.time_seed.soil").withStyle(ChatFormatting.GOLD));
			return false;
		}
		level.setBlock(soil.above(), ModContent.block("time_sprout").defaultBlockState(), 3);
		level.playSound(null, soil.above(), SoundEvents.CROP_PLANTED, SoundSource.BLOCKS, 1f, 1f);
		if (!player.isCreative()) stack.shrink(1);
		return true;
	}
}
