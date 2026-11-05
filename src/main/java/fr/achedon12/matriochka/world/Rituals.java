package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.Blocks3;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;

/**
 * The offering ritual of an arena altar: three seconds of rising light in the world's colour, a ring of light drawn on the
 * arena floor and a building chord, then the boss is summoned. Rituals live in memory only; one runs per altar.
 */
public final class Rituals {
	public static final int DURATION = 60;
	private static final int RING = Arenas.RING;

	private record Ritual(ServerLevel level, BlockPos altar, Defs.BossDef boss, UUID player, long start, int color, double floorY) {}

	private static final List<Ritual> ACTIVE = new ArrayList<>();

	private Rituals() {}

	public static boolean busy(ServerLevel level, BlockPos altar) {
		for (Ritual r : ACTIVE) if (r.level == level && r.altar.equals(altar)) return true;
		return false;
	}

	public static void start(ServerLevel level, BlockPos altar, Defs.BossDef boss, ServerPlayer by) {
		int world = Math.max(1, boss.world());
		int color = Content.WORLDS.get(world - 1).accent();
		// the decorated arena raises its altar on a dais; an older arena has it flush with the floor
		double floorY = level.getBlockState(altar.offset(RING, -1, 0)).isAir() ? altar.getY() - 1 : altar.getY();
		ACTIVE.add(new Ritual(level, altar.immutable(), boss, by.getUUID(), level.getGameTime(), color, floorY));
		level.playSound(null, altar, SoundEvents.BEACON_ACTIVATE, SoundSource.BLOCKS, 1.6f, 0.6f);
	}

	public static void clear() {
		ACTIVE.clear();
	}

	public static void tick(MinecraftServer server) {
		for (Iterator<Ritual> it = ACTIVE.iterator(); it.hasNext(); ) {
			Ritual r = it.next();
			ServerLevel level = r.level;
			if (level.getServer() != server || !(level.getBlockState(r.altar).getBlock() instanceof Blocks3.BossAltar)) {
				it.remove();
				continue;
			}
			long t = level.getGameTime() - r.start;
			if (t >= DURATION) {
				it.remove();
				finish(r);
				continue;
			}
			step(r, (int) t);
		}
	}

	private static void step(Ritual r, int t) {
		ServerLevel level = r.level;
		RandomSource rnd = level.getRandom();
		float f = t / (float) DURATION;
		double cx = r.altar.getX() + 0.5, cy = r.altar.getY() + 1.0, cz = r.altar.getZ() + 0.5;
		DustParticleOptions dust = new DustParticleOptions(r.color, 1.4f + f);
		// rising motes around the altar, climbing higher as the ritual builds
		for (int i = 0; i < 6; i++) {
			double a = rnd.nextDouble() * Math.PI * 2, d = rnd.nextDouble() * 2.6;
			level.sendParticles(dust, cx + Math.cos(a) * d, cy + rnd.nextDouble() * (1 + 6 * f), cz + Math.sin(a) * d, 1, 0, 0, 0, 0);
		}
		level.sendParticles(ParticleTypes.END_ROD, cx + rnd.nextGaussian() * 0.8, cy, cz + rnd.nextGaussian() * 0.8, 0, 0, 1, 0, 0.12 + 0.2 * f);
		// a twin helix of the world's colour
		for (int k = 0; k < 2; k++) {
			double a = t * 0.35 + k * Math.PI;
			level.sendParticles(dust, cx + Math.cos(a) * 1.4, cy + (t % 20) / 20.0 * 6, cz + Math.sin(a) * 1.4, 1, 0, 0, 0, 0);
		}
		// the ring of light, drawn around the arena floor as the ritual advances
		double sweep = Math.PI * 2 * f;
		int points = 72;
		for (int i = 0; i < points; i++) {
			double a = i * Math.PI * 2 / points;
			if (a > sweep) break;
			double x = cx + Math.cos(a - Math.PI / 2) * RING, z = cz + Math.sin(a - Math.PI / 2) * RING;
			if (i % 2 == t % 2) level.sendParticles(dust, x, r.floorY + 0.15, z, 1, 0.05, 0, 0.05, 0);
		}
		double fx = cx + Math.cos(sweep - Math.PI / 2) * RING, fz = cz + Math.sin(sweep - Math.PI / 2) * RING;
		level.sendParticles(ParticleTypes.END_ROD, fx, r.floorY + 0.2, fz, 2, 0.1, 0.1, 0.1, 0.01);
		// a chord that climbs to the summoning
		if (t % 10 == 0) level.playSound(null, r.altar, SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.BLOCKS, 1.2f, 0.5f + 1.5f * f);
		if (t % 10 == 5) level.playSound(null, r.altar, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.5f, 0.6f + f);
		if (t == 20 || t == 40) level.playSound(null, r.altar, SoundEvents.RESPAWN_ANCHOR_CHARGE, SoundSource.BLOCKS, 1.4f, 0.7f + f * 0.6f);
		if (t == 50) level.playSound(null, r.altar, SoundEvents.BELL_RESONATE, SoundSource.BLOCKS, 2f, 0.7f);
	}

	private static void finish(Ritual r) {
		ServerLevel level = r.level;
		double cx = r.altar.getX() + 0.5, cz = r.altar.getZ() + 0.5;
		DustParticleOptions dust = new DustParticleOptions(r.color, 2.5f);
		for (int i = 0; i < 120; i++) {
			double a = i * Math.PI * 2 / 120;
			level.sendParticles(dust, cx + Math.cos(a) * RING, r.floorY + 0.3, cz + Math.sin(a) * RING, 2, 0.1, 0.3, 0.1, 0);
			if (i % 4 == 0) level.sendParticles(ParticleTypes.END_ROD, cx + Math.cos(a) * RING, r.floorY + 0.3, cz + Math.sin(a) * RING, 0, 0, 1, 0, 0.3);
		}
		level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, cx, r.altar.getY() + 1, cz, 1, 0, 0, 0, 0);
		level.playSound(null, r.altar, SoundEvents.BEACON_POWER_SELECT, SoundSource.BLOCKS, 2f, 0.5f);
		if (!level.getEntitiesOfClass(MatrioBoss.class, new net.minecraft.world.phys.AABB(r.altar).inflate(48)).isEmpty()) return;
		ServerPlayer by = level.getServer().getPlayerList().getPlayer(r.player);
		if (by != null && by.level() != level) by = null;
		MatrioBoss.summon(level, r.boss.id(), r.altar.above(2), by);
	}
}
