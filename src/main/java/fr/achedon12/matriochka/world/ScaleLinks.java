package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.AbstractCandleBlock;
import net.minecraft.world.level.block.BaseFireBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.BonemealableBlock;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.FarmlandBlock;
import net.minecraft.world.level.block.LightningRodBlock;
import net.minecraft.world.level.block.entity.AbstractFurnaceBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Effects between the scales: a World Block is not a mere portal, it stays linked with what surrounds it.
 * <p>
 * Inside to outside, within 8 blocks of the block: World 1 breathes spores and makes plants grow, World 2 heats up
 * (furnaces burn faster, flammable things may catch fire), World 3 creaks and slams the doors around, World 4 blows
 * gusts and charges lightning rods, World 5 drinks the light of candles and campfires, World 6 lifts the items on the
 * ground, World 7 leaks (wet farmland, fires put out), World 8 hastens crops and spoils food left lying, World 9
 * shakes and cracks the stone. A boss fight inside makes the block tremble and crack, whatever the world.
 * <p>
 * Outside to inside, stored in the group's world entry as "fx_*" end times (overworld game time) and read by the
 * rules: water around World 1 halves the toxin ("damp"), ice around World 2 halves the heat ("cool"), a redstone
 * signal on World 3 lets sealed doors open by hand ("unlocked"), a storm over World 4 strengthens its gusts
 * ("storm"), lights around World 5 lengthen the lantern ("lit"), dry ground around World 7 eases the pressure
 * ("dry"), Terrain Anchors around World 9 hold its ground ("calm"). Moving the block shakes the world inside it
 * ("quake"). A player of the group outside can also shake the block on purpose, to help or to hinder those inside
 * (see {@link #shake}).
 * <p>
 * Effects only run while the block's chunk is loaded; the rules read the stored state, so a world keeps its last
 * effects without loading the block.
 */
public final class ScaleLinks {
	private ScaleLinks() {}

	public static final int RADIUS = 8;
	public static final long FIVE_MINUTES = 20 * 60 * 5;
	/** Last game time a boss of (world, parcel) was fighting. */
	private static final Map<Long, Long> FIGHTS = new HashMap<>();

	// ---------------------------------------------------------------- reading the state
	public static boolean active(MatrioData data, String group, int world, String fx, long now) {
		return data.worldEntry(group, world).getLongOr("fx_" + fx, 0L) > now;
	}

	/** Whether an outside effect is in force in the world a player stands in (their group's). */
	public static boolean active(ServerPlayer p, String fx) {
		int w = Worlds.number(p.level());
		if (w <= 0 || w > 10) return false;
		MatrioData data = MatrioData.get(p.level().getServer());
		return active(data, data.groupOf(p.getUUID()), w, fx, p.level().getServer().overworld().getGameTime());
	}

	/** Whether an outside effect is in force at a place of a world (its parcel's group). */
	public static boolean activeAt(ServerLevel level, BlockPos pos, String fx) {
		String g = Variants.groupAt(level, pos);
		return g != null && active(MatrioData.get(level.getServer()), g, Worlds.number(level), fx, level.getServer().overworld().getGameTime());
	}

	/** Starts an effect; returns true when it was not running yet (so the players inside are told once). */
	public static boolean start(MatrioData data, String group, int world, String fx, long now, long length) {
		CompoundTag e = data.worldEntry(group, world);
		boolean fresh = e.getLongOr("fx_" + fx, 0L) <= now;
		if (fresh || !fx.equals("lit")) e.putLong("fx_" + fx, Math.max(e.getLongOr("fx_" + fx, 0L), now + length));
		data.changed();
		return fresh;
	}

	/** Called by a boss while it fights: its World Block will tremble on the Surface. */
	public static void bossFighting(ServerLevel level, BlockPos at) {
		int w = Worlds.number(level);
		if (w <= 0 || w > 10) return;
		FIGHTS.put(((long) w << 32) | (Worlds.parcelOf(at) & 0xFFFFFFFFL), level.getGameTime());
	}

	/** A World Block was set down somewhere else than before: the world inside quakes. */
	public static void moved(MinecraftServer server, String group, int world) {
		MatrioData data = MatrioData.get(server);
		start(data, group, world, "quake", server.overworld().getGameTime(), 200);
		for (ServerPlayer p : inside(server, data, group, world)) p.sendSystemMessage(Component.translatable("message.matriochka.link.quake").withStyle(ChatFormatting.GOLD));
	}

	// ---------------------------------------------------------------- shaking the block on purpose
	/** Ticks between two shakes of the same world, whoever shakes it. */
	public static final long SHAKE_COOLDOWN = 20 * 30;
	/** How long a helping shake leaves the creatures stunned and a boss open, and how long a hindering one quakes. */
	public static final int SHAKE_STUN = 60, SHAKE_QUAKE = 100;

	/** Outcome of a shake, for the shaker's message (and the checks). */
	public enum Shake { HELPED, HINDERED, NOT_YOURS, COOLDOWN, EMPTY }

	/**
	 * A player outside shakes a World Block on purpose (sneak and use it with empty hands to help, strike it with a Doll
	 * Mallet to hinder). Only the owning group may; one shake per world every 30 seconds.
	 * <p>
	 * Helping: around everyone of the group inside, creatures are thrown off their feet and stunned for 3 seconds and a
	 * boss staggers, its guard open as after an attack. Hindering: the world quakes for 5 seconds (the players inside are
	 * shaken about, as when the block is moved) and blocks over their heads come loose and fall.
	 */
	public static Shake shake(ServerPlayer by, ServerLevel level, BlockPos pos, boolean hinder) {
		if (!(level.getBlockEntity(pos) instanceof DataBlockEntity be)) return Shake.EMPTY;
		MinecraftServer server = level.getServer();
		MatrioData data = MatrioData.get(server);
		String owner = be.data().getStringOr("owner", "");
		if (!data.sameGroup(owner, by)) return Shake.NOT_YOURS;
		int w = be.data().getIntOr("world", 1);
		String group = owner.isEmpty() ? data.groupOf(by.getUUID()) : data.groupOf(java.util.UUID.fromString(owner));
		long now = server.overworld().getGameTime();
		CompoundTag e = data.worldEntry(group, w);
		if (e.getLongOr("shake_ready", 0L) > now) return Shake.COOLDOWN;
		// the block itself rattles on the Surface
		be.data().putLong("quake", level.getGameTime() + 30);
		be.changed();
		double cx = pos.getX() + 0.5, cy = pos.getY() + 0.5, cz = pos.getZ() + 0.5;
		level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ModContent.block("world_block").defaultBlockState()), cx, cy + 0.5, cz, 20, 0.4, 0.4, 0.4, 0.1);
		level.playSound(null, pos, hinder ? SoundEvents.ANVIL_LAND : SoundEvents.WOOD_HIT, SoundSource.BLOCKS, hinder ? 0.7f : 1.2f, hinder ? 0.6f : 0.8f);
		List<ServerPlayer> in = inside(server, data, group, w);
		if (in.isEmpty()) return Shake.EMPTY;
		e.putLong("shake_ready", now + SHAKE_COOLDOWN);
		data.changed();
		if (hinder) {
			start(data, group, w, "quake", now, SHAKE_QUAKE);
			for (ServerPlayer p : in) {
				loosen((ServerLevel) p.level(), p.blockPosition(), p.getRandom());
				p.sendSystemMessage(Component.translatable("message.matriochka.shake.hinder", by.getDisplayName()).withStyle(ChatFormatting.RED));
			}
			return Shake.HINDERED;
		}
		for (ServerPlayer p : in) {
			ServerLevel inner = (ServerLevel) p.level();
			stun(inner, p);
			for (fr.achedon12.matriochka.entity.MatrioBoss boss : inner.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioBoss.class, p.getBoundingBox().inflate(48))) {
				if (boss.stagger(SHAKE_STUN)) inner.sendParticles(ParticleTypes.CRIT, boss.getX(), boss.getY() + boss.getBbHeight(), boss.getZ(), 30, 0.8, 0.4, 0.8, 0.2);
			}
			inner.playSound(null, p.blockPosition(), SoundEvents.DEEPSLATE_BREAK, SoundSource.AMBIENT, 1f, 0.5f);
			p.sendSystemMessage(Component.translatable("message.matriochka.shake.help", by.getDisplayName()).withStyle(ChatFormatting.AQUA));
		}
		return Shake.HELPED;
	}

	/** The creatures around a player lose their footing: thrown away from them and stunned. */
	private static void stun(ServerLevel level, ServerPlayer p) {
		for (net.minecraft.world.entity.Mob m : level.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, p.getBoundingBox().inflate(24),
			m -> m instanceof net.minecraft.world.entity.monster.Enemy && !(m instanceof fr.achedon12.matriochka.entity.MatrioBoss))) {
			Vec3 away = m.position().subtract(p.position()).multiply(1, 0, 1);
			away = away.lengthSqr() < 1.0E-4 ? new Vec3(0, 0, 1) : away.normalize();
			m.push(away.x * 0.6, 0.45, away.z * 0.6);
			m.needsSync = true;
			m.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOWNESS, SHAKE_STUN, 4));
			m.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.WEAKNESS, SHAKE_STUN, 1));
			m.getNavigation().stop();
			level.sendParticles(ParticleTypes.CRIT, m.getX(), m.getY() + m.getBbHeight() + 0.2, m.getZ(), 6, 0.3, 0.1, 0.3, 0.05);
		}
	}

	/** Up to six blocks over a player's head come loose and fall: plain, breakable blocks only, never the world's locks. */
	static int loosen(ServerLevel level, BlockPos at, RandomSource r) {
		int fell = 0;
		for (int tries = 0; tries < 40 && fell < 6; tries++) {
			BlockPos q = at.offset(r.nextInt(9) - 4, 3 + r.nextInt(6), r.nextInt(9) - 4);
			BlockState s = level.getBlockState(q);
			float hard = s.getDestroySpeed(level, q);
			if (s.isAir() || s.hasBlockEntity() || hard < 0 || hard > 3f || !s.isCollisionShapeFullBlock(level, q)) continue;
			if (BuiltInRegistries.BLOCK.getKey(s.getBlock()).getNamespace().equals("matriochka") && !s.is(BlockTags.MINEABLE_WITH_PICKAXE) && !s.is(BlockTags.MINEABLE_WITH_SHOVEL)) continue;
			if (!level.getBlockState(q.below()).isAir()) continue;
			net.minecraft.world.entity.item.FallingBlockEntity.fall(level, q, s);
			fell++;
		}
		return fell;
	}

	private static List<ServerPlayer> inside(MinecraftServer server, MatrioData data, String group, int world) {
		List<ServerPlayer> out = new ArrayList<>();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (Worlds.number(p.level()) == world && data.groupOf(p.getUUID()).equals(group)) out.add(p);
		}
		return out;
	}

	private static void tell(List<ServerPlayer> players, String key) {
		for (ServerPlayer p : players) p.sendSystemMessage(Component.translatable("message.matriochka.link." + key).withStyle(ChatFormatting.AQUA));
	}

	// ---------------------------------------------------------------- the tick
	public static void tick(MinecraftServer server) {
		long now = server.overworld().getGameTime();
		if (now % 10 == 0) quakes(server, now);
		if (now % 40 != 0) return;
		MatrioData data = MatrioData.get(server);
		for (String group : data.groups()) {
			for (int w = 1; w <= 10; w++) {
				CompoundTag e = data.worldEntry(group, w);
				String dim = e.getStringOr("block_dim", "");
				if (dim.isEmpty()) continue;
				ServerLevel level = server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(dim)));
				BlockPos pos = BlockPos.of(e.getLongOr("block_pos", 0L));
				if (level == null || !level.isLoaded(pos) || !level.getBlockState(pos).is(ModContent.block("world_block"))) continue;
				try {
					link(level, pos, data, group, w, now);
				} catch (RuntimeException ex) {
					fr.achedon12.matriochka.Matriochka.LOG.warn("World Block link {} {} failed", group, w, ex);
				}
			}
		}
	}

	/** One pass of the links of a World Block: what leaks out, what the surroundings send in. */
	public static void link(ServerLevel level, BlockPos b, MatrioData data, String group, int w, long now) {
		RandomSource r = level.getRandom();
		List<ServerPlayer> in = inside(level.getServer(), data, group, w);
		double cx = b.getX() + 0.5, cy = b.getY() + 0.5, cz = b.getZ() + 0.5;
		switch (w) {
			case 1 -> {
				level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, cx, cy + 1, cz, 8, 3, 1, 3, 0);
				grow(level, b, r, 3);
				if (count(level, b, 3, s -> s.getFluidState().is(FluidTags.WATER)) >= 3 && start(data, group, w, "damp", now, FIVE_MINUTES)) tell(in, "damp");
			}
			case 2 -> {
				level.sendParticles(ParticleTypes.LARGE_SMOKE, cx, cy + 0.8, cz, 2, 0.3, 0.1, 0.3, 0.01);
				level.sendParticles(ParticleTypes.LAVA, cx, cy + 0.6, cz, 1, 0.2, 0.1, 0.2, 0);
				furnaces(level, b, 10);
				if (r.nextInt(40) == 0) ignite(level, b, r);
				if (count(level, b, 3, s -> s.is(Blocks.ICE) || s.is(Blocks.PACKED_ICE) || s.is(Blocks.BLUE_ICE) || s.is(Blocks.SNOW_BLOCK)) >= 2
					&& start(data, group, w, "cool", now, FIVE_MINUTES)) tell(in, "cool");
			}
			case 3 -> {
				if (r.nextInt(6) == 0) {
					level.playSound(null, b, SoundEvents.WOODEN_DOOR_CLOSE, SoundSource.BLOCKS, 0.8f, 0.5f);
					for (BlockPos q : BlockPos.betweenClosed(b.offset(-RADIUS, -2, -RADIUS), b.offset(RADIUS, 2, RADIUS))) {
						BlockState s = level.getBlockState(q);
						if (s.getBlock() instanceof DoorBlock door && s.is(BlockTags.WOODEN_DOORS) && door.isOpen(s)
							&& s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF) == net.minecraft.world.level.block.state.properties.DoubleBlockHalf.LOWER) {
							door.setOpen(null, level, s, q.immutable(), false);
						}
					}
				}
				if (level.hasNeighborSignal(b) && start(data, group, w, "unlocked", now, 20 * 60)) tell(in, "unlocked");
			}
			case 4 -> {
				if (r.nextInt(3) == 0) {
					double a = r.nextDouble() * Math.PI * 2;
					for (LivingEntity le : level.getEntitiesOfClass(LivingEntity.class, new AABB(b).inflate(RADIUS), le -> !le.isSpectator() && !le.isShiftKeyDown())) {
						le.push(Math.cos(a) * 0.5, 0.15, Math.sin(a) * 0.5);
						le.needsSync = true;
					}
					level.sendParticles(ParticleTypes.GUST, cx, cy + 1, cz, 3, 2, 0.5, 2, 0);
					level.playSound(null, b, SoundEvents.BREEZE_WIND_CHARGE_BURST.value(), SoundSource.WEATHER, 0.5f, 0.8f);
				}
				if (r.nextInt(6) == 0) {
					for (BlockPos q : BlockPos.betweenClosed(b.offset(-RADIUS, -3, -RADIUS), b.offset(RADIUS, 6, RADIUS))) {
						BlockState s = level.getBlockState(q);
						if (s.getBlock() instanceof LightningRodBlock rod && !s.getValue(LightningRodBlock.POWERED)) {
							rod.onLightningStrike(s, level, q.immutable());
							break;
						}
					}
				}
				if ((level.isRainingAt(b.above()) || level.isThundering()) && start(data, group, w, "storm", now, 200)) tell(in, "storm");
			}
			case 5 -> {
				if (r.nextInt(4) == 0) {
					for (BlockPos q : BlockPos.betweenClosed(b.offset(-RADIUS, -2, -RADIUS), b.offset(RADIUS, 3, RADIUS))) {
						BlockState s = level.getBlockState(q);
						if ((s.getBlock() instanceof AbstractCandleBlock || s.getBlock() instanceof CampfireBlock) && s.hasProperty(BlockStateProperties.LIT) && s.getValue(BlockStateProperties.LIT)) {
							level.setBlock(q, s.setValue(BlockStateProperties.LIT, false), Block.UPDATE_ALL);
							level.sendParticles(ParticleTypes.SMOKE, q.getX() + 0.5, q.getY() + 0.6, q.getZ() + 0.5, 6, 0.1, 0.1, 0.1, 0.01);
							break;
						}
					}
				}
				level.sendParticles(ParticleTypes.SCULK_SOUL, cx, cy + 1, cz, 2, 2, 1, 2, 0.01);
				if (count(level, b, 5, s -> s.getLightEmission() >= 10) >= 4 && start(data, group, w, "lit", now, FIVE_MINUTES)) {
					for (ServerPlayer p : in) {
						PlayerState ps = PlayerState.of(p);
						if (ps.flagActive("lantern", level.getGameTime())) ps.setFlagTime("lantern", ps.flagTime("lantern") + FIVE_MINUTES);
					}
					tell(in, "lit");
				}
			}
			case 6 -> {
				for (ItemEntity it : level.getEntitiesOfClass(ItemEntity.class, new AABB(b).inflate(RADIUS))) {
					Vec3 v = it.getDeltaMovement();
					it.setDeltaMovement(v.x * 0.5, Math.max(v.y, 0.18), v.z * 0.5);
					it.needsSync = true;
				}
				level.sendParticles(ParticleTypes.REVERSE_PORTAL, cx, cy + 1, cz, 4, 1.5, 0.5, 1.5, 0.02);
			}
			case 7 -> {
				level.sendParticles(ParticleTypes.DRIPPING_WATER, cx, cy - 0.3, cz, 6, 0.5, 0.1, 0.5, 0);
				level.sendParticles(ParticleTypes.BUBBLE_POP, cx, cy + 0.6, cz, 4, 0.4, 0.2, 0.4, 0.02);
				for (BlockPos q : BlockPos.betweenClosed(b.offset(-RADIUS, -2, -RADIUS), b.offset(RADIUS, 2, RADIUS))) {
					BlockState s = level.getBlockState(q);
					if (s.getBlock() instanceof FarmlandBlock && s.getValue(BlockStateProperties.MOISTURE) < 7) level.setBlock(q, s.setValue(BlockStateProperties.MOISTURE, 7), Block.UPDATE_CLIENTS);
					else if (s.getBlock() instanceof BaseFireBlock) level.removeBlock(q, false);
				}
				if (count(level, b, 6, s -> s.getFluidState().is(FluidTags.WATER)) == 0 && start(data, group, w, "dry", now, FIVE_MINUTES)) tell(in, "dry");
			}
			case 8 -> {
				grow(level, b, r, 6);
				for (ItemEntity it : level.getEntitiesOfClass(ItemEntity.class, new AABB(b).inflate(RADIUS))) {
					ItemStack s = it.getItem();
					if (s.has(DataComponents.FOOD) && !s.is(Items.ROTTEN_FLESH) && r.nextInt(8) == 0) it.setItem(new ItemStack(Items.ROTTEN_FLESH, s.getCount()));
				}
			}
			case 9 -> {
				level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.DIRT.defaultBlockState()), cx, cy - 0.4, cz, 10, 2.5, 0.1, 2.5, 0.05);
				if (r.nextInt(4) == 0) {
					for (LivingEntity le : level.getEntitiesOfClass(LivingEntity.class, new AABB(b).inflate(RADIUS), le -> le.onGround() && !le.isSpectator())) {
						le.push((r.nextDouble() - 0.5) * 0.2, 0.12, (r.nextDouble() - 0.5) * 0.2);
						le.needsSync = true;
					}
					level.playSound(null, b, SoundEvents.ROOTED_DIRT_BREAK, SoundSource.BLOCKS, 0.7f, 0.5f);
				}
				if (r.nextInt(6) == 0) crack(level, b, r);
				if (count(level, b, RADIUS, s -> s.is(ModContent.block("terrain_anchor"))) > 0 && start(data, group, w, "calm", now, FIVE_MINUTES)) tell(in, "calm");
			}
			default -> {
				// World 10: none, the player is outside, in the giant world
			}
		}
		// a boss fight inside: the block trembles and cracks on the Surface
		Long fight = FIGHTS.get(((long) w << 32) | (data.parcel(group, w) & 0xFFFFFFFFL));
		ServerLevel inner = level.getServer().getLevel(Worlds.key(w));
		if (fight != null && inner != null && inner.getGameTime() - fight < 60) {
			level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ModContent.block("world_block").defaultBlockState()), cx, cy + 0.5, cz, 14, 0.4, 0.4, 0.4, 0.1);
			level.playSound(null, b, SoundEvents.DEEPSLATE_BREAK, SoundSource.BLOCKS, 0.8f, 0.6f);
			if (level.getBlockEntity(b) instanceof DataBlockEntity be) {
				be.data().putLong("quake", level.getGameTime() + 60);
				be.changed();
			}
			if (data.worldEntry(group, w).getLongOr("boss_told", 0L) < now) {
				data.worldEntry(group, w).putLong("boss_told", now + 20 * 60);
				for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(b).inflate(24))) p.sendOverlayMessage(Component.translatable("message.matriochka.link.boss").withStyle(ChatFormatting.GOLD));
			}
		}
	}

	/** While a world quakes, everyone of its group inside is shaken. */
	private static void quakes(MinecraftServer server, long now) {
		MatrioData data = MatrioData.get(server);
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			int w = Worlds.number(p.level());
			if (w <= 0 || w > 10 || p.isSpectator()) continue;
			if (!active(data, data.groupOf(p.getUUID()), w, "quake", now)) continue;
			ServerLevel level = (ServerLevel) p.level();
			RandomSource r = level.getRandom();
			if (p.onGround()) {
				p.push((r.nextDouble() - 0.5) * 0.35, 0.18, (r.nextDouble() - 0.5) * 0.35);
				p.needsSync = true;
			}
			BlockState under = level.getBlockState(p.blockPosition().below());
			if (!under.isAir()) level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, under), p.getX(), p.getY(), p.getZ(), 20, 3, 0.1, 3, 0.1);
			level.sendParticles(ParticleTypes.ASH, p.getX(), p.getY() + 4, p.getZ(), 30, 4, 1, 4, 0);
			if (now % 20 == 0) level.playSound(null, p.blockPosition(), SoundEvents.DEEPSLATE_BREAK, SoundSource.AMBIENT, 1.2f, 0.4f);
		}
	}

	// ---------------------------------------------------------------- helpers
	private static int count(ServerLevel level, BlockPos b, int r, java.util.function.Predicate<BlockState> test) {
		int n = 0;
		for (BlockPos q : BlockPos.betweenClosed(b.offset(-r, -2, -r), b.offset(r, 2, r))) if (test.test(level.getBlockState(q))) n++;
		return n;
	}

	/** A few random ticks to the plants around: crops, saplings, grass. */
	private static void grow(ServerLevel level, BlockPos b, RandomSource r, int tries) {
		for (int i = 0; i < tries; i++) {
			BlockPos q = b.offset(r.nextInt(RADIUS * 2 + 1) - RADIUS, r.nextInt(5) - 2, r.nextInt(RADIUS * 2 + 1) - RADIUS);
			BlockState s = level.getBlockState(q);
			if (s.getBlock() instanceof BonemealableBlock && s.isRandomlyTicking()) {
				s.randomTick(level, q, r);
				level.sendParticles(ParticleTypes.HAPPY_VILLAGER, q.getX() + 0.5, q.getY() + 0.5, q.getZ() + 0.5, 2, 0.2, 0.2, 0.2, 0);
			}
		}
	}

	/** Extra ticks for the furnaces, smokers and blast furnaces around the block. */
	private static void furnaces(ServerLevel level, BlockPos b, int extra) {
		for (int cx = (b.getX() - RADIUS) >> 4; cx <= (b.getX() + RADIUS) >> 4; cx++)
			for (int cz = (b.getZ() - RADIUS) >> 4; cz <= (b.getZ() + RADIUS) >> 4; cz++) {
				if (!level.hasChunk(cx, cz)) continue;
				for (var be : List.copyOf(level.getChunk(cx, cz).getBlockEntities().values())) {
					if (be instanceof AbstractFurnaceBlockEntity f && be.getBlockPos().closerThan(b, RADIUS + 0.5)) {
						for (int i = 0; i < extra; i++) AbstractFurnaceBlockEntity.serverTick(level, f.getBlockPos(), f.getBlockState(), f);
					}
				}
			}
	}

	/** A spark: one flammable spot near the block catches fire. */
	private static void ignite(ServerLevel level, BlockPos b, RandomSource r) {
		BlockPos q = b.offset(r.nextInt(11) - 5, r.nextInt(3) - 1, r.nextInt(11) - 5);
		if (!level.getBlockState(q).isAir()) return;
		for (Direction d : Direction.values()) {
			if (level.getBlockState(q.relative(d)).ignitedByLava() && BaseFireBlock.canBePlacedAt(level, q, Direction.UP)) {
				level.setBlock(q, BaseFireBlock.getState(level, q), Block.UPDATE_ALL);
				return;
			}
		}
	}

	/** One stone block near the block cracks. */
	private static void crack(ServerLevel level, BlockPos b, RandomSource r) {
		BlockPos q = b.offset(r.nextInt(13) - 6, r.nextInt(3) - 2, r.nextInt(13) - 6);
		BlockState s = level.getBlockState(q);
		BlockState to = s.is(Blocks.STONE) ? Blocks.COBBLESTONE.defaultBlockState()
			: s.is(Blocks.STONE_BRICKS) ? Blocks.CRACKED_STONE_BRICKS.defaultBlockState()
			: s.is(Blocks.DEEPSLATE_BRICKS) ? Blocks.CRACKED_DEEPSLATE_BRICKS.defaultBlockState()
			: s.is(Blocks.GRASS_BLOCK) ? Blocks.COARSE_DIRT.defaultBlockState() : null;
		if (to == null) return;
		level.setBlock(q, to, Block.UPDATE_ALL);
		level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, s), q.getX() + 0.5, q.getY() + 1, q.getZ() + 0.5, 12, 0.3, 0.1, 0.3, 0.05);
	}
}
