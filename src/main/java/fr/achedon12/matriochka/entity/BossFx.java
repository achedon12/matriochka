package fr.achedon12.matriochka.entity;

import fr.achedon12.matriochka.content.Particles;
import fr.achedon12.matriochka.rules.HastenedClock;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * The world's own particles sprayed by a boss's attacks (purely visual, no sound, no gameplay): spores in World 1,
 * falling embers in World 2, chain glints and dust in World 3, lightning sparks in World 4, shadow wisps in World 5,
 * mirror shards in World 6, bubbles in World 7, the season's petals, pollen, leaves or snow in World 8, grit in
 * World 9, thread scraps and fluff in World 10, gold dust on the Surface and in World 0.
 */
public final class BossFx {
	private BossFx() {}

	/** The particle of a (shell) world; World 8 follows its season. */
	public static SimpleParticleType of(ServerLevel level, int world) {
		return switch (world) {
			case 1 -> Particles.SPORE;
			case 2 -> Particles.EMBER;
			case 3 -> Particles.CHAIN_GLINT;
			case 4 -> Particles.STORM_SPARK;
			case 5 -> Particles.SHADOW_WISP;
			case 6 -> Particles.MIRROR_SHARD;
			case 7 -> Particles.BUBBLE;
			case 8 -> switch (HastenedClock.season(level)) {
				case 0 -> Particles.PETAL;
				case 1 -> Particles.POLLEN;
				case 2 -> Particles.AUTUMN_LEAF;
				default -> Particles.SNOWFLAKE;
			};
			case 9 -> Particles.GRIT;
			case 10 -> Particles.THREAD_SCRAP;
			default -> Particles.GOLD_MOTE;
		};
	}

	/** A second, softer particle that hangs around the first. */
	private static SimpleParticleType haze(int world) {
		return switch (world) {
			case 1 -> Particles.SPORE;
			case 2 -> Particles.EMBER;
			case 3 -> Particles.COLD_DUST;
			case 4 -> Particles.STORM_SPARK;
			case 5 -> Particles.DEEP_MOTE;
			case 6 -> Particles.MIRROR_SHARD;
			case 7 -> Particles.BUBBLE;
			case 9 -> Particles.RUST_MOTE;
			case 10 -> Particles.FLUFF;
			default -> Particles.GOLD_MOTE;
		};
	}

	/** The ring of the world's particles marking where an attack will land, during its warning. */
	public static void telegraph(ServerLevel level, int world, Vec3 at, double r, int n) {
		SimpleParticleType p = of(level, world);
		for (int i = 0; i < n; i++) {
			double a = i * Math.PI * 2 / n;
			level.sendParticles(p, at.x + Math.cos(a) * r, at.y + 0.2, at.z + Math.sin(a) * r, 1, 0.05, 0.05, 0.05, 0);
		}
	}

	/** What an attack sprays once it lands: attack 0 light, 1 medium, 2 signature. */
	public static void attack(ServerLevel level, Entity boss, int world, int attack, Vec3 aim) {
		SimpleParticleType p = of(level, world);
		SimpleParticleType h = haze(world);
		double mid = boss.getBbHeight() * 0.6;
		if (attack == 0) {
			Vec3 front = boss.position().add(boss.getLookAngle().scale(2));
			level.sendParticles(p, front.x, front.y + 1, front.z, 12, 0.8, 0.5, 0.8, 0.08);
			return;
		}
		boolean sig = attack == 2;
		int n = sig ? 90 : 40;
		double r = sig ? 5 : 3;
		switch (world) {
			// embers and grit come down from above the target, the others burst where the attack lands
			case 2, 9 -> {
				level.sendParticles(p, aim.x, aim.y + 5, aim.z, n, r * 0.5, 1.0, r * 0.5, 0.02);
				level.sendParticles(h, aim.x, aim.y + 0.4, aim.z, n / 2, r * 0.5, 0.3, r * 0.5, 0.02);
			}
			// the Jailer's glints close around every player it cages
			case 3 -> {
				for (ServerPlayer pl : level.getEntitiesOfClass(ServerPlayer.class, boss.getBoundingBox().inflate(16))) {
					level.sendParticles(p, pl.getX(), pl.getY() + 1, pl.getZ(), sig ? 24 : 10, 0.8, 1.0, 0.8, 0.0);
				}
				level.sendParticles(h, aim.x, aim.y + 1, aim.z, n, r * 0.5, 1.0, r * 0.5, 0.01);
			}
			// shadow wisps rise all around the boss, mirror shards fly out of it
			case 5, 6 -> {
				level.sendParticles(p, boss.getX(), boss.getY() + mid, boss.getZ(), n, r * 0.6, mid, r * 0.6, 0.06);
				level.sendParticles(h, aim.x, aim.y + 0.5, aim.z, n / 3, r * 0.4, 0.4, r * 0.4, 0.02);
			}
			// a column of bubbles out of the sea floor
			case 7 -> level.sendParticles(p, aim.x, aim.y + 1.5, aim.z, n, r * 0.35, 1.5, r * 0.35, 0.05);
			default -> {
				level.sendParticles(p, aim.x, aim.y + 0.6, aim.z, n, r * 0.5, 0.6, r * 0.5, 0.06);
				level.sendParticles(h, boss.getX(), boss.getY() + mid, boss.getZ(), n / 3, 1.0, mid, 1.0, 0.03);
			}
		}
	}
}
