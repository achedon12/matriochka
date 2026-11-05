package fr.achedon12.matriochka.entity;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * A creature's moveset on top of its basic strike and signature mechanic. A move is picked among those in range,
 * never the same one twice in a row; it plays its wind-up animation, lands on its hit tick, then goes on cooldown.
 * Timings mirror tools/moves.py, which places the animation hit frames on the same ticks.
 */
public final class MobMoves {
	/** hit tick, total ticks, cooldown ticks, min range, max range. */
	record Move(int hit, int end, int cooldown, double min, double max) {}

	static final Map<String, Move> MOVES = Map.of(
		"combo", new Move(6, 18, 70, 0, 3),
		"lunge", new Move(9, 24, 90, 3, 9),
		"sweep", new Move(9, 16, 80, 0, 3.2),
		"slam", new Move(14, 22, 110, 0, 4),
		"spit", new Move(12, 18, 80, 3.5, 16),
		"roar", new Move(12, 24, 220, 0, 10),
		"blink", new Move(8, 14, 130, 3, 14),
		"spin", new Move(4, 20, 100, 0, 2.6),
		"grab", new Move(8, 16, 120, 0, 2.4)
	);

	private static final boolean DEBUG = Boolean.getBoolean("matriochka.debugMoves");
	private final MatrioMob mob;
	private final int[] cooldowns;
	private String current;
	private String last;
	private int t;
	private int global = 40;
	private boolean landed;

	MobMoves(MatrioMob mob) {
		this.mob = mob;
		this.cooldowns = new int[8];
	}

	public boolean busy() {
		return current != null;
	}

	private List<String> list() {
		return mob.def().moves();
	}

	void tick(ServerLevel level, LivingEntity target) {
		List<String> moves = list();
		if (moves.isEmpty()) return;
		for (int i = 0; i < cooldowns.length; i++) if (cooldowns[i] > 0) cooldowns[i]--;
		if (current != null) {
			run(level, target);
			return;
		}
		if (global > 0) {
			global--;
			return;
		}
		if (target == null || !target.isAlive() || mob.getRandom().nextFloat() > 0.18f) return;
		double d = Math.sqrt(mob.distanceToSqr(target));
		List<Integer> ready = new ArrayList<>();
		for (int i = 0; i < moves.size() && i < cooldowns.length; i++) {
			Move m = MOVES.get(moves.get(i));
			if (m == null || cooldowns[i] > 0 || moves.get(i).equals(last) && moves.size() > 1) continue;
			if (d < m.min() || d > m.max()) continue;
			if (!moves.get(i).equals("roar") && !mob.hasLineOfSight(target)) continue;
			ready.add(i);
		}
		if (ready.isEmpty()) return;
		int pick = ready.get(mob.getRandom().nextInt(ready.size()));
		start(level, moves.get(pick), pick);
	}

	private void start(ServerLevel level, String name, int idx) {
		Move m = MOVES.get(name);
		float speed = Defs.speedMultiplier(mob.def().world());
		cooldowns[idx] = (int) (m.cooldown() / speed);
		global = (int) (24 / speed);
		current = name;
		last = name;
		t = 0;
		landed = false;
		mob.triggerAnim("attack", name);
		if (DEBUG) org.slf4j.LoggerFactory.getLogger("matriochka").info("[moves] {} starts {}", mob.def().id(), name);
		if (!name.equals("lunge")) mob.getNavigation().stop();
		SoundEvent cue = switch (name) {
			case "roar" -> SoundEvents.RAVAGER_ROAR;
			case "slam" -> SoundEvents.IRON_GOLEM_ATTACK;
			case "spit" -> SoundEvents.LLAMA_SPIT;
			case "blink" -> SoundEvents.ENDERMAN_TELEPORT;
			case "grab" -> SoundEvents.EVOKER_PREPARE_ATTACK;
			default -> SoundEvents.PLAYER_ATTACK_SWEEP;
		};
		level.playSound(null, mob.blockPosition(), cue, SoundSource.HOSTILE, name.equals("roar") ? 1.2f : 0.7f, 0.8f + mob.getRandom().nextFloat() * 0.4f);
	}

	private void run(ServerLevel level, LivingEntity target) {
		Move m = MOVES.get(current);
		t++;
		if (target != null) mob.getLookControl().setLookAt(target, 30, 30);
		if (!current.equals("lunge") && !current.equals("blink")) mob.getNavigation().stop();
		if (target != null && target.isAlive()) {
			switch (current) {
				case "combo" -> {
					if ((t == m.hit() || t == m.hit() + 4 || t == m.hit() + 8) && mob.distanceToSqr(target) < 10) hurt(level, target, 0.6f);
				}
				case "lunge" -> {
					if (t == m.hit()) {
						Vec3 to = target.position().subtract(mob.position());
						Vec3 h = new Vec3(to.x, 0, to.z).normalize().scale(Math.min(1.25, 0.35 + to.horizontalDistance() * 0.12));
						double up = mob.isNoGravity() ? Mth.clamp(to.y * 0.15, -0.6, 0.6) : 0.42;
						mob.setDeltaMovement(h.x, up, h.z);
						mob.needsSync = true;
						particles(level, ParticleTypes.CLOUD, 8, 0.4);
					}
					if (t > m.hit() && !landed && mob.getBoundingBox().inflate(0.6).intersects(target.getBoundingBox())) {
						landed = true;
						hurt(level, target, 1.2f);
					}
				}
				case "sweep" -> {
					if (t == m.hit()) {
						Vec3 look = mob.getLookAngle();
						for (LivingEntity e : around(level, 3.2)) {
							Vec3 to = e.position().subtract(mob.position()).normalize();
							if (to.dot(look) > 0.15) {
								hurt(level, e, 1f);
								e.push(to.x * 1.1, 0.35, to.z * 1.1);
								e.needsSync = true;
							}
						}
						particles(level, ParticleTypes.SWEEP_ATTACK, 3, 1.2);
					}
				}
				case "slam" -> {
					if (t == m.hit()) {
						for (LivingEntity e : around(level, 3.5)) {
							hurt(level, e, 1.1f);
							e.push(0, 0.65, 0);
							e.needsSync = true;
						}
						particles(level, ParticleTypes.EXPLOSION, 4, 1.8);
						level.playSound(null, mob.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 0.6f, 1.1f);
					}
				}
				case "spit" -> {
					if (t == m.hit()) {
						Vec3 from = mob.getEyePosition();
						Vec3 to = target.getEyePosition();
						ParticleOptions trail = trail();
						int steps = (int) (from.distanceTo(to) * 2);
						for (int i = 0; i <= steps; i++) {
							Vec3 p = from.lerp(to, i / (double) Math.max(1, steps));
							level.sendParticles(trail, p.x, p.y, p.z, 1, 0.02, 0.02, 0.02, 0);
						}
						if (mob.hasLineOfSight(target)) {
							hurt(level, target, 0.8f);
							affliction(level, target, mob.def().world());
						}
					}
				}
				case "roar" -> {
					if (t == m.hit()) {
						for (LivingEntity e : around(level, 8)) affliction(level, e, mob.def().world());
						for (MatrioMob ally : level.getEntitiesOfClass(MatrioMob.class, mob.getBoundingBox().inflate(12))) {
							ally.addEffect(new MobEffectInstance(MobEffects.SPEED, 100, 0));
							ally.addEffect(new MobEffectInstance(MobEffects.STRENGTH, 100, 0));
							if (ally.getTarget() == null) ally.setTarget(target);
						}
						particles(level, ParticleTypes.SONIC_BOOM, 1, 0);
					}
				}
				case "blink" -> {
					if (t == m.hit() - 1) particles(level, ParticleTypes.LARGE_SMOKE, 20, 0.5);
					if (t == m.hit()) {
						Vec3 back = target.getLookAngle().multiply(1, 0, 1).normalize().scale(-1.8);
						Vec3 dest = target.position().add(back);
						if (level.noCollision(mob, mob.getBoundingBox().move(dest.subtract(mob.position())))) {
							mob.teleportTo(dest.x, dest.y, dest.z);
							mob.lookAt(target, 180, 180);
						}
						particles(level, ParticleTypes.LARGE_SMOKE, 20, 0.5);
					}
					if (t == m.hit() + 2 && mob.distanceToSqr(target) < 9) hurt(level, target, 1f);
				}
				case "spin" -> {
					if (t >= m.hit() && (t - m.hit()) % 4 == 0 && t < m.end()) {
						for (LivingEntity e : around(level, 2.1)) hurt(level, e, 0.4f);
						particles(level, ParticleTypes.SWEEP_ATTACK, 2, 0.8);
					}
				}
				case "grab" -> {
					if (t == m.hit() && mob.distanceToSqr(target) < 6.5) {
						hurt(level, target, 0.5f);
						target.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40, 9));
						target.addEffect(new MobEffectInstance(MobEffects.JUMP_BOOST, 40, 250));
						target.setDeltaMovement(Vec3.ZERO);
						target.needsSync = true;
					}
				}
				default -> {}
			}
		}
		if (t >= m.end()) current = null;
	}

	private List<LivingEntity> around(ServerLevel level, double r) {
		return level.getEntitiesOfClass(LivingEntity.class, mob.getBoundingBox().inflate(r),
			e -> e != mob && !(e instanceof MatrioMob) && !(e instanceof MatrioBoss) && e.isAlive() && !(e instanceof ServerPlayer p && (p.isCreative() || p.isSpectator())));
	}

	private void hurt(ServerLevel level, LivingEntity e, float mult) {
		e.hurtServer(level, mob.damageSources().mobAttack(mob), (float) mob.getAttributeValue(Attributes.ATTACK_DAMAGE) * mult);
	}

	private void particles(ServerLevel level, ParticleOptions p, int n, double spread) {
		level.sendParticles(p, mob.getX(), mob.getY() + mob.getBbHeight() * 0.5, mob.getZ(), n, spread, 0.3, spread, 0.02);
	}

	private ParticleOptions trail() {
		return switch (mob.def().world()) {
			case 1 -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case 2 -> ParticleTypes.FLAME;
			case 3 -> ParticleTypes.CRIT;
			case 4 -> ParticleTypes.ELECTRIC_SPARK;
			case 5 -> ParticleTypes.SQUID_INK;
			case 6 -> ParticleTypes.REVERSE_PORTAL;
			case 7 -> ParticleTypes.BUBBLE_POP;
			case 8 -> ParticleTypes.END_ROD;
			case 9 -> ParticleTypes.CRIMSON_SPORE;
			default -> ParticleTypes.WAX_ON;
		};
	}

	/** Each world's own harm, applied by bolts and roars. */
	static void affliction(ServerLevel level, LivingEntity e, int world) {
		PlayerState ps = e instanceof ServerPlayer sp ? PlayerState.of(sp) : null;
		switch (world) {
			case 1 -> { if (ps != null) ps.addGauge("toxin", 6); else e.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0)); }
			case 2 -> { if (ps != null) ps.addGauge("heat", 6); e.igniteForSeconds(3); }
			case 3 -> e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 2));
			case 4 -> e.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 20, 1));
			case 5 -> e.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0));
			case 6 -> e.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 100, 0));
			case 7 -> { if (ps != null) ps.addGauge("oxygen", -4); else e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 1)); }
			case 8 -> e.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 80, 1));
			case 9 -> e.addEffect(new MobEffectInstance(MobEffects.HUNGER, 100, 1));
			case 10 -> e.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 1));
			default -> {}
		}
		if (ps != null) ps.sync();
	}
}
