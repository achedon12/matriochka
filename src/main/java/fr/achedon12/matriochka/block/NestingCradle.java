package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Particles;
import fr.achedon12.matriochka.content.Sounds;
import fr.achedon12.matriochka.world.WorldOres;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.item.ItemEntity;
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
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jspecify.annotations.Nullable;

/**
 * The Nesting Cradle, a great carved matryoshka opened at its waist: it takes the ten worlds' ores, one of each, and
 * nests them.
 *
 * It is drawn by an animated GeckoLib model (tools/cradle_geo.py, block/CradleBlockEntity): a ring of beads with a
 * socket per world turns round its waist, and every ore set lights its world's socket; an empty hand takes the last
 * one back. When the tenth is set the ritual runs by itself, eight seconds keyed on the model (tools/content.py
 * CRADLE_TIMELINE): the ring spins up and draws in, the upper half is thrown open and a nest of ten smaller dolls rises
 * out of it and fans out; one by one they close over the next with a clack; the last sinks into the bowl, the doll
 * slams shut, jumps, shakes and glows, then opens a last time on the Matriochkite Ingot, which rises, spins and pops
 * out to the player.
 *
 * The server runs it: the state (the ores set, the tick the ritual began) lives in the block entity's data, survives
 * the chunk unloading and is sent to the clients, which play the animation from that tick; the server lays the
 * particles, the light and the sounds on the same timeline, so every player near sees and hears it. A cradle broken
 * before the flash gives its ores back.
 */
public class NestingCradle extends Block implements EntityBlock {
	public static final EnumProperty<Direction> FACING = BlockStateProperties.HORIZONTAL_FACING;
	private static final VoxelShape SHAPE = Block.box(1.5, 0, 1.5, 14.5, 16, 14.5);

	/** Ticks an ore takes to rise into its socket, and the wait between the tenth and the ritual. */
	public static final int RISE = 16, START_DELAY = 18;
	/** The ritual's timeline (tools/content.py CRADLE_TIMELINE): the flash when the doll slams, the end when the ingot pops. */
	public static final int FLASH = Content.CRADLE_SLAM, DURATION = Content.CRADLE_END;
	/** Heights on the model, in blocks above the cradle's floor (tools/cradle_geo.py): its waist and ring, the nest risen, the ingot. */
	private static final double WAIST = 1.0, RING = 0.94, RING_IN = 0.72, NEST = 2.2, INGOT = 1.95;

	public NestingCradle(BlockBehaviour.Properties p) {
		super(p);
		registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
	}

	@Override
	protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) {
		b.add(FACING);
	}

	@Override
	public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext ctx) {
		// the doll's face turns to the one who sets it down
		return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
	}

	@Override
	protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
		return SHAPE;
	}

	/** The animated model draws it (block/CradleBlockEntity); the block model only gives its particles. */
	@Override
	protected net.minecraft.world.level.block.RenderShape getRenderShape(BlockState state) {
		return net.minecraft.world.level.block.RenderShape.INVISIBLE;
	}

	@Override
	public @Nullable BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
		return new CradleBlockEntity(pos, state);
	}

	@Override
	public <T extends BlockEntity> @Nullable BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
		if (level.isClientSide()) return null;
		return (l, p, s, be) -> tick((ServerLevel) l, p, s, (DataBlockEntity) be);
	}

	// ---------------------------------------------------------------- the state, in the block entity's data
	public static int[] ores(DataBlockEntity be) {
		return be.data().getIntArray("ores").orElse(new int[0]);
	}

	/** Game time the ritual began at (0: not begun). */
	public static long start(DataBlockEntity be) {
		return be.data().getLongOr("start", 0L);
	}

	public static boolean running(DataBlockEntity be) {
		return start(be) > 0;
	}

	private static boolean has(int[] ores, int w) {
		for (int o : ores) if (o == w) return true;
		return false;
	}

	// ---------------------------------------------------------------- use
	@Override
	protected InteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
		int w = WorldOres.worldOf(stack);
		if (w == 0) return InteractionResult.TRY_WITH_EMPTY_HAND;
		if (!(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl) || !(level.getBlockEntity(pos) instanceof DataBlockEntity be))
			return InteractionResult.SUCCESS;
		insert(sl, pos, be, sp, stack);
		return InteractionResult.SUCCESS;
	}

	/** Sets an ore in the cradle; the tenth starts the ritual. Returns false when the cradle refused it. */
	public static boolean insert(ServerLevel level, BlockPos pos, DataBlockEntity be, ServerPlayer sp, ItemStack stack) {
		int w = WorldOres.worldOf(stack);
		if (w == 0) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.not_ore").withStyle(ChatFormatting.GOLD));
			return false;
		}
		if (running(be)) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.busy").withStyle(ChatFormatting.GOLD));
			return false;
		}
		int[] ores = ores(be);
		if (has(ores, w)) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.has", w).withStyle(ChatFormatting.GOLD));
			return false;
		}
		int[] next = java.util.Arrays.copyOf(ores, ores.length + 1);
		next[ores.length] = w;
		be.data().putIntArray("ores", next);
		be.data().putLong("set_" + w, level.getGameTime());
		Component name = stack.getHoverName();
		stack.consume(1, sp);
		level.playSound(null, pos, Sounds.cradleNote(w), SoundSource.BLOCKS, 1.2f, 1f);
		sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.set", name, next.length).withStyle(ChatFormatting.GOLD));
		if (next.length == 10) {
			be.data().putLong("start", level.getGameTime() + START_DELAY);
			be.data().putString("by", sp.getUUID().toString());
		}
		be.changed();
		return true;
	}

	@Override
	protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
		if (!player.getMainHandItem().isEmpty()) return InteractionResult.PASS;
		if (!(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl) || !(level.getBlockEntity(pos) instanceof DataBlockEntity be))
			return InteractionResult.SUCCESS;
		if (running(be)) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.busy").withStyle(ChatFormatting.GOLD));
			return InteractionResult.SUCCESS;
		}
		int[] ores = ores(be);
		if (ores.length == 0) return InteractionResult.PASS;
		int w = ores[ores.length - 1];
		be.data().putIntArray("ores", java.util.Arrays.copyOf(ores, ores.length - 1));
		be.data().remove("set_" + w);
		be.changed();
		ItemStack back = WorldOres.ore(w);
		Component name = back.getHoverName();
		if (!sp.getInventory().add(back)) sp.spawnAtLocation(sl, back);
		sl.playSound(null, pos, Sounds.CRADLE_CLACK, SoundSource.BLOCKS, 0.8f, 1.3f);
		sp.sendOverlayMessage(Component.translatable("message.matriochka.cradle.taken", name).withStyle(ChatFormatting.GOLD));
		return InteractionResult.SUCCESS;
	}

	/** The cradle is broken: before the flash its ores come back, after it the ingot; its picture goes. */
	public static void spill(ServerLevel level, BlockPos pos, DataBlockEntity be) {
		long start = start(be);
		long t = start > 0 ? level.getGameTime() - start : -1;
		if (t >= FLASH) {
			Block.popResource(level, pos, new ItemStack(ModContent.item("matriochkite_ingot")));
		} else {
			for (int w : ores(be)) Block.popResource(level, pos, WorldOres.ore(w));
		}
		be.data().remove("ores");
		be.data().remove("start");
	}

	/** Each world's own particle, from World 1 to World 10: spores, embers, glints, sparks, motes, shards, bubbles... */
	private static final net.minecraft.core.particles.SimpleParticleType[] WORLD_MOTES = {Particles.SPORE, Particles.EMBER, Particles.CHAIN_GLINT,
		Particles.STORM_SPARK, Particles.DEEP_MOTE, Particles.MIRROR_SHARD, Particles.BUBBLE, Particles.POLLEN, Particles.RUST_MOTE, Particles.THREAD_SCRAP};

	private static int colour(int w) {
		return Content.WORLDS.get(w - 1).accent();
	}

	private static double smooth(double f) {
		f = Math.max(0, Math.min(1, f));
		return f * f * (3 - 2 * f);
	}

	// ---------------------------------------------------------------- the light and the sounds on the ritual's timeline
	private static void tick(ServerLevel level, BlockPos pos, BlockState state, DataBlockEntity be) {
		int[] ores = ores(be);
		long start = start(be);
		if (ores.length == 0 && start == 0) return;
		long now = level.getGameTime();
		int t = start > 0 && now >= start ? (int) (now - start) : -1;
		if (t >= DURATION) {
			finish(level, pos, be);
			return;
		}
		Vec3 base = Vec3.atBottomCenterOf(pos);
		Vec3 waist = base.add(0, WAIST, 0);
		var rnd = level.getRandom();
		if (t < 0) {
			// the set ores breathe their worlds' light round the ring
			if (now % 3 == 0) {
				int w = ores[rnd.nextInt(ores.length)];
				double a = rnd.nextDouble() * Math.PI * 2;
				level.sendParticles(new DustParticleOptions(colour(w), 0.7f), waist.x + Math.sin(a) * RING, waist.y + 0.1, waist.z - Math.cos(a) * RING, 1, 0.02, 0.05, 0.02, 0);
			}
			if (now % 20 == 0) level.sendParticles(Particles.GOLD_MOTE, waist.x, waist.y + 0.2, waist.z, 3, 0.3, 0.1, 0.3, 0.01);
			return;
		}
		// ---- the ring spins up and draws in: the ten notes climb, a line of light runs from every world to the middle
		if (t < Content.CRADLE_TIGHTEN + 20) {
			if (t % 4 == 0 && t / 4 < ores.length) {
				int[] sorted = ores.clone();
				java.util.Arrays.sort(sorted);
				level.playSound(null, pos, Sounds.cradleNote(sorted[t / 4]), SoundSource.BLOCKS, 1.3f, 1f);
			}
			if (t == 0) level.playSound(null, pos, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 1f, 1.4f);
			double r = RING - (RING - RING_IN) * smooth(t / (double) Content.CRADLE_TIGHTEN);
			double ring = waist.y + 0.25 * smooth(t / (double) Content.CRADLE_TIGHTEN);
			if (t % 2 == 0) for (int w : ores) {
				double a = Math.PI * 2 * (w - 1) / 10 + t * 0.18;
				Vec3 at = new Vec3(waist.x + Math.sin(a) * r, ring, waist.z - Math.cos(a) * r);
				DustParticleOptions beam = new DustParticleOptions(colour(w), 0.5f);
				for (int k = 1; k <= 4; k++) {
					Vec3 q = at.lerp(waist.add(0, 0.25, 0), k / 5.0);
					level.sendParticles(beam, q.x, q.y, q.z, 1, 0, 0, 0, 0);
				}
			}
		}
		// ---- the doll opens: its glow spills out
		if (t == Content.CRADLE_OPEN) {
			level.playSound(null, pos, Sounds.DOLL_OPEN, SoundSource.BLOCKS, 1.4f, 0.7f);
			level.sendParticles(ParticleTypes.END_ROD, waist.x, waist.y, waist.z, 24, 0.25, 0.1, 0.25, 0.12);
		}
		// ---- the nest rises and spins: gold dust swirls round it
		if (t >= Content.CRADLE_RISE && t < Content.CRADLE_DESCEND && t % 2 == 0) {
			double a = t * 0.4, y = base.y + Math.min(NEST, WAIST + (NEST - WAIST) * smooth((t - Content.CRADLE_RISE) / 20.0));
			for (int k = 0; k < 3; k++) {
				double b = a + k * Math.PI * 2 / 3;
				level.sendParticles(Particles.GOLD_MOTE, base.x + Math.cos(b) * 1.1, y + 0.4, base.z + Math.sin(b) * 1.1, 1, 0, 0, 0, 0);
			}
			if (t == Content.CRADLE_RISE) level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.4f, 0.8f);
		}
		// ---- each doll closes over the next, the smallest first: a clack, a little ring of gold
		int c = t - Content.CRADLE_CLOSE;
		if (c >= 0 && c % Content.CRADLE_CLACK_EVERY == 0 && c / Content.CRADLE_CLACK_EVERY < 10) {
			int k = c / Content.CRADLE_CLACK_EVERY;
			level.playSound(null, pos, Sounds.CRADLE_CLACK, SoundSource.BLOCKS, 1.3f, 1.4f - k * 0.07f);
			double y = base.y + NEST + 0.35;
			for (int q = 0; q < 16; q++) {
				double a = q * Math.PI * 2 / 16;
				level.sendParticles(Particles.GOLD_MOTE, base.x + Math.cos(a) * (0.3 + k * 0.04), y, base.z + Math.sin(a) * (0.3 + k * 0.04), 1, 0, 0, 0, 0);
			}
		}
		if (t == Content.CRADLE_DESCEND) level.playSound(null, pos, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.4f, 1.3f);
		if (t > FLASH - 8 && t < FLASH && t % 2 == 0) level.sendParticles(Particles.GOLD_MOTE, waist.x, waist.y + 0.5, waist.z, 8, 0.4, 0.4, 0.4, 0.03);
		// ---- the doll slams shut and jumps: the flash, a pillar of light, the worlds flung out, a shockwave, the chord
		if (t == FLASH) {
			Vec3 c0 = waist.add(0, 0.4, 0);
			level.playSound(null, pos, Sounds.DOLL_CLOSE, SoundSource.BLOCKS, 1.6f, 0.6f);
			level.sendParticles(ColorParticleOption.create(ParticleTypes.FLASH, 0xFFFFD27A), c0.x, c0.y, c0.z, 1, 0, 0, 0, 0);
			level.sendParticles(ParticleTypes.END_ROD, c0.x, c0.y, c0.z, 90, 0.05, 0.05, 0.05, 0.42);
			level.sendParticles(Particles.GOLD_MOTE, c0.x, c0.y, c0.z, 140, 0.15, 0.15, 0.15, 0.45);
			for (int k = 0; k < 36; k++) level.sendParticles(ParticleTypes.END_ROD, c0.x, base.y + 0.3 + k * 0.16, c0.z, 1, 0.03, 0, 0.03, 0.005);
			for (var mote : WORLD_MOTES) level.sendParticles(mote, c0.x, c0.y, c0.z, 6, 0.2, 0.2, 0.2, 0.35);
			level.playSound(null, pos, Sounds.CRADLE_CHORD, SoundSource.BLOCKS, 1.6f, 1f);
			level.playSound(null, pos, SoundEvents.TOTEM_USE, SoundSource.BLOCKS, 0.5f, 1.5f);
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(pos).inflate(16)))
				fr.achedon12.matriochka.net.Cues.shake(p, 0.35f, 10);
		}
		if (t >= FLASH && t < FLASH + 14) {
			double r = 0.5 + (t - FLASH) * 0.38;
			int pts = 32 + (t - FLASH) * 3;
			DustParticleOptions gold = new DustParticleOptions(0xFFD27A, 0.9f);
			for (int q = 0; q < pts; q++) {
				double a = q * Math.PI * 2 / pts + (rnd.nextDouble() - 0.5) * 0.08;
				level.sendParticles(gold, base.x + Math.cos(a) * r, base.y + 0.25, base.z + Math.sin(a) * r, 1, 0, 0.02, 0, 0);
				if (q % 8 == 0 && t % 2 == 0) level.sendParticles(ParticleTypes.END_ROD, base.x + Math.cos(a) * r, base.y + 0.3, base.z + Math.sin(a) * r, 1, 0, 0, 0, 0.01);
			}
		}
		// ---- it opens a last time on the ingot, which rises and spins in a swirl of gold
		if (t == Content.CRADLE_REVEAL) {
			level.playSound(null, pos, Sounds.DOLL_OPEN, SoundSource.BLOCKS, 1.4f, 1.2f);
			level.sendParticles(ParticleTypes.END_ROD, waist.x, waist.y + 0.2, waist.z, 30, 0.1, 0.4, 0.1, 0.08);
		}
		if (t > Content.CRADLE_REVEAL && t % 2 == 0) {
			double a = t * 0.5, y = base.y + INGOT;
			level.sendParticles(Particles.GOLD_MOTE, base.x + Math.cos(a) * 0.5, y, base.z + Math.sin(a) * 0.5, 1, 0, 0, 0, 0);
			level.sendParticles(Particles.GOLD_MOTE, base.x - Math.cos(a) * 0.5, y, base.z - Math.sin(a) * 0.5, 1, 0, 0, 0, 0);
		}
	}

	/** The ritual is over: the ingot pops out toward the one who set the tenth ore, the cradle is empty again. */
	private static void finish(ServerLevel level, BlockPos pos, DataBlockEntity be) {
		Vec3 at = Vec3.atBottomCenterOf(pos).add(0, INGOT, 0);
		ServerPlayer by = null;
		try {
			by = level.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(be.data().getStringOr("by", "")));
		} catch (IllegalArgumentException ignored) {
			// no one recorded: it pops straight up
		}
		if (by != null && (by.level() != level || by.position().distanceTo(at) > 24)) by = null;
		ItemEntity item = new ItemEntity(level, at.x, at.y, at.z, new ItemStack(ModContent.item("matriochkite_ingot")));
		Vec3 v = by == null ? new Vec3(0, 0.3, 0) : by.position().add(0, 1, 0).subtract(at).normalize().scale(0.28).add(0, 0.22, 0);
		item.setDeltaMovement(v);
		item.setDefaultPickUpDelay();
		level.addFreshEntity(item);
		level.playSound(null, pos, Sounds.DOLL_OPEN, SoundSource.BLOCKS, 1.2f, 1.5f);
		level.sendParticles(ParticleTypes.END_ROD, at.x, at.y, at.z, 16, 0.1, 0.1, 0.1, 0.15);
		CompoundTag d = be.data();
		d.remove("ores");
		d.remove("start");
		d.remove("by");
		for (int w = 1; w <= 10; w++) d.remove("set_" + w);
		be.changed();
		if (by != null) by.sendSystemMessage(Component.translatable("message.matriochka.cradle.born").withStyle(ChatFormatting.GOLD));
	}
}
