package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.Worlds;
import it.unimi.dsi.fastutil.HashCommon;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.WeakHashMap;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * World 6: the realm is cut into 32 x 32 columns, and every 90 seconds about a third of them turn upside down. Inside
 * a flipped column gravity really points up (the gravity attribute goes negative): players, creatures and dropped items
 * fall toward the sky and stand on ceilings, up to 16 blocks above the column's ground, where the pull fades and they
 * hang. Purple sparks trace the borders between flipped and normal columns. Gravity Boots, a Stabilizer or a Flipped
 * Apple keep your own gravity normal. When a column turns back, whoever was falling upward drifts down slowly.
 */
public final class GravityZones {
	private GravityZones() {}

	public static final int ZONE = 32;
	public static final long PERIOD = 20 * 90;
	public static final long WARN = 20 * 5;
	/** How far above the ground of a flipped column its pull reaches. */
	public static final int CAP = 16;
	/** Share of the columns flipped at any time, in percent. */
	private static final int SHARE = 35;
	/** No flip within this many blocks of the Threshold, so nobody arrives falling into the sky. */
	private static final int CALM = 48;

	private static final Identifier ID = Matriochka.id("flipped_gravity");
	/** Total gravity times (1 - 2): the normal pull, reversed. */
	private static final AttributeModifier FLIP = new AttributeModifier(ID, -2.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);

	private static final class State {
		long epoch = -1;
		int airTicks;
		boolean told;
	}

	private static final Map<UUID, State> STATES = new HashMap<>();
	private static final Set<LivingEntity> FLIPPED_MOBS = Collections.newSetFromMap(new WeakHashMap<>());

	public static long epoch(long t) {
		return t / PERIOD;
	}

	/** Whether the column (zx, zz) is upside down during this epoch. */
	public static boolean flippedZone(ServerLevel level, int zx, int zz, long epoch) {
		int x0 = zx * ZONE, z0 = zz * ZONE;
		BlockPos c = Worlds.parcelCenter(Worlds.parcelOf(new BlockPos(x0, 0, z0)));
		if (x0 + ZONE > c.getX() - CALM && x0 < c.getX() + CALM && z0 + ZONE > c.getZ() - CALM && z0 < c.getZ() + CALM) return false;
		for (int z : new int[]{z0, z0 + ZONE / 2, z0 + ZONE - 1}) if (MatrioBoss.inArena(level, new BlockPos(x0, 64, z))) return false;
		long h = HashCommon.mix(Mth.getSeed(zx, (int) epoch, zz) ^ level.getSeed() ^ 0x6A09E667F3BCC909L);
		return Math.floorMod(h, 100) < SHARE;
	}

	public static boolean flippedColumn(ServerLevel level, double x, double z, long epoch) {
		return flippedZone(level, Math.floorDiv(Mth.floor(x), ZONE), Math.floorDiv(Mth.floor(z), ZONE), epoch);
	}

	/** Whether gravity points up at this point: in a flipped column, below its cap. */
	public static boolean flippedAt(ServerLevel level, double x, double y, double z, long epoch) {
		if (!flippedColumn(level, x, z, epoch)) return false;
		int bx = Mth.floor(x), bz = Mth.floor(z);
		if (!level.isLoaded(new BlockPos(bx, 0, bz))) return false;
		return y < level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, bx, bz) + CAP;
	}

	public static boolean protectedFrom(ServerPlayer p, long t) {
		PlayerState ps = PlayerState.of(p);
		return WorldRules.wearing(p, "gravity_boots") || ps.flagActive("stable", t) || ps.flagActive("flipped_apple", t);
	}

	private static void setFlipped(LivingEntity e, boolean on) {
		AttributeInstance g = e.getAttribute(Attributes.GRAVITY);
		if (g == null) return;
		boolean has = g.hasModifier(ID);
		if (on && !has) g.addTransientModifier(FLIP);
		else if (!on && has) g.removeModifier(ID);
	}

	public static boolean isFlipped(LivingEntity e) {
		AttributeInstance g = e.getAttribute(Attributes.GRAVITY);
		return g != null && g.hasModifier(ID);
	}

	/** Every tick: players, creatures and items of the World 6 rule zones. */
	public static void tick(MinecraftServer server, java.util.function.Predicate<ServerPlayer> inRule) {
		long t = server.overworld().getGameTime();
		boolean mobs = t % 5 == 0, sparks = t % 10 == 0;
		Set<LivingEntity> seen = mobs ? Collections.newSetFromMap(new java.util.IdentityHashMap<>()) : null;
		Set<ItemEntity> pushed = Collections.newSetFromMap(new java.util.IdentityHashMap<>());
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			boolean here = !p.isSpectator() && inRule.test(p);
			if (!here) {
				if (isFlipped(p)) setFlipped(p, false);
				STATES.remove(p.getUUID());
				continue;
			}
			ServerLevel level = (ServerLevel) p.level();
			tickPlayer(level, p, t);
			if (t % PERIOD == PERIOD - WARN) {
				p.sendOverlayMessage(Component.translatable("message.matriochka.rule.gravity").withStyle(ChatFormatting.LIGHT_PURPLE));
				level.playSound(null, p.blockPosition(), fr.achedon12.matriochka.content.Sounds.WORLD_GRAVITY_SHIFT, SoundSource.AMBIENT, 0.8f, 1f);
			}
			items(level, p, t, pushed);
			if (mobs) {
				for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(48), e -> !(e instanceof Player) && !(e instanceof MatrioBoss))) {
					if (seen.add(e)) tickMob(level, e, t);
				}
			}
			if (sparks) sparks(level, p, t);
		}
		if (mobs) {
			// creatures flipped earlier that wandered away from every player: settle them again
			for (LivingEntity e : FLIPPED_MOBS.toArray(new LivingEntity[0])) {
				if (e.isRemoved() || !(e.level() instanceof ServerLevel l)) {
					FLIPPED_MOBS.remove(e);
					continue;
				}
				if (!seen.contains(e)) tickMob(l, e, t);
			}
		}
	}

	/** One player, one tick: flips their gravity on or off and counts their upward fall. */
	public static void tickPlayer(ServerLevel level, ServerPlayer p, long t) {
		long ep = epoch(t);
		State st = STATES.computeIfAbsent(p.getUUID(), k -> new State());
		boolean shielded = protectedFrom(p, t) || p.getAbilities().flying;
		boolean column = !shielded && flippedColumn(level, p.getX(), p.getZ(), ep);
		boolean inv = column && flippedAt(level, p.getX(), p.getY(), p.getZ(), ep);
		boolean was = isFlipped(p);
		if (inv && !was) {
			setFlipped(p, true);
			Achievements.grant(p, "flipped");
			if (!st.told) {
				st.told = true;
				p.sendOverlayMessage(Component.translatable("message.matriochka.rule.flipped").withStyle(ChatFormatting.LIGHT_PURPLE));
			}
		} else if (!inv && was) {
			setFlipped(p, false);
			// the column turned back (or a Stabilizer kicked in) under someone falling up: let them drift down
			if (st.epoch != ep || shielded) p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 20 * 12, 0, true, false));
		}
		if (inv) st.epoch = ep;
		if (inv && !p.onGround()) {
			// falling upward through open air: the server reads it as levitation, not as flying
			MobEffectInstance lev = p.getEffect(MobEffects.LEVITATION);
			if (lev == null || lev.getDuration() < 3) p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 8, 5, true, false, false));
		}
		if (column && !p.onGround()) {
			if (++st.airTicks >= 200) Achievements.grant(p, "fall_up");
		} else {
			st.airTicks = 0;
		}
	}

	/** One creature: falls up in a flipped column, settles once it is out. */
	public static void tickMob(ServerLevel level, LivingEntity e, long t) {
		boolean inv = !e.isNoGravity() && flippedAt(level, e.getX(), e.getY(), e.getZ(), epoch(t));
		boolean was = isFlipped(e);
		if (inv == was) return;
		setFlipped(e, inv);
		if (inv) FLIPPED_MOBS.add(e);
		else {
			FLIPPED_MOBS.remove(e);
			e.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 20 * 6, 0, true, false));
		}
	}

	/** Dropped items near a player float up too (their gravity is not an attribute, so they get pushed). */
	private static void items(ServerLevel level, ServerPlayer p, long t, Set<ItemEntity> pushed) {
		long ep = epoch(t);
		for (ItemEntity it : level.getEntitiesOfClass(ItemEntity.class, p.getBoundingBox().inflate(24), e -> !e.isNoGravity())) {
			if (!pushed.add(it) || !flippedAt(level, it.getX(), it.getY(), it.getZ(), ep)) continue;
			Vec3 m = it.getDeltaMovement();
			it.setDeltaMovement(m.x, Math.min(0.4, m.y + 0.08), m.z);
			it.needsSync = true;
		}
	}

	/** Sparks along the borders between flipped and normal columns, and motes rising inside the flipped ones. */
	private static void sparks(ServerLevel level, ServerPlayer p, long t) {
		long ep = epoch(t);
		int px = p.getBlockX(), pz = p.getBlockZ();
		double py = p.getY();
		int zx = Math.floorDiv(px, ZONE), zz = Math.floorDiv(pz, ZONE);
		var rnd = level.getRandom();
		for (int dx = -1; dx <= 1; dx++) {
			for (int dz = -1; dz <= 1; dz++) {
				int ax = zx + dx, az = zz + dz;
				boolean here = flippedZone(level, ax, az, ep);
				// east border of (ax, az) and south border of (ax, az)
				if (here != flippedZone(level, ax + 1, az, ep)) {
					int bx = (ax + 1) * ZONE;
					if (Math.abs(bx - px) <= 16) line(level, p, bx, az * ZONE, true, py, pz, rnd);
				}
				if (here != flippedZone(level, ax, az + 1, ep)) {
					int bz = (az + 1) * ZONE;
					if (Math.abs(bz - pz) <= 16) line(level, p, ax * ZONE, bz, false, py, px, rnd);
				}
				if (here && dx == 0 && dz == 0) {
					for (int i = 0; i < 4; i++) {
						level.sendParticles(p, ParticleTypes.END_ROD, false, false, px + rnd.nextGaussian() * 6, py + rnd.nextDouble() * 4 - 1, pz + rnd.nextGaussian() * 6, 0, 0, 1, 0, 0.08);
					}
				}
			}
		}
	}

	/** A dotted vertical curtain on one border segment, around the player's height and position along it. */
	private static void line(ServerLevel level, ServerPlayer p, int x, int z, boolean alongZ, double py, int near, net.minecraft.util.RandomSource rnd) {
		int from = (alongZ ? z : x), to = from + ZONE;
		int a = Math.max(from, near - 12), b = Math.min(to, near + 12);
		for (int s = a; s <= b; s += 2) {
			double y = py - 1 + rnd.nextDouble() * 5;
			double fx = alongZ ? x : s + 0.5, fz = alongZ ? s + 0.5 : z;
			level.sendParticles(p, ParticleTypes.REVERSE_PORTAL, false, false, fx, y, fz, 1, 0.05, 0.3, 0.05, 0.01);
		}
	}

	public static void clearAll() {
		STATES.clear();
		FLIPPED_MOBS.clear();
	}
}
