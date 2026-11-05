package fr.achedon12.matriochka.entity;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Runs a creature's signature attacks (tools/attacks.py). Each attack is one of a few deliveries (a blow, a leap,
 * a ring, a bolt...) with its own numbers, afflictions, particles and sound. An attack is picked among those in
 * range, never the same twice in a row; it plays its wind-up, lands on its hit tick, then goes on cooldown.
 */
public final class MobMoves {
	private static final boolean DEBUG = Boolean.getBoolean("matriochka.debugMoves");
	private static final Map<String, List<MobEffectInstance>> FX_CACHE = new HashMap<>();
	private final MatrioMob mob;
	private final int[] cooldowns = new int[8];
	private Defs.AttackDef current;
	private Defs.AttackDef last;
	private int t;
	private int global = 40;
	private boolean landed;
	private Vec3 mark;
	private Vec3 dashDir;

	MobMoves(MatrioMob mob) {
		this.mob = mob;
	}

	public boolean busy() {
		return current != null;
	}

	void tick(ServerLevel level, LivingEntity target) {
		List<Defs.AttackDef> list = mob.def().attacks();
		if (list.isEmpty()) return;
		for (int i = 0; i < cooldowns.length; i++) if (cooldowns[i] > 0) cooldowns[i]--;
		if (current != null) {
			run(level, target);
			return;
		}
		if (global > 0) {
			global--;
			return;
		}
		if (target == null || !target.isAlive() || mob.getRandom().nextFloat() > 0.3f) return;
		double d = Math.sqrt(mob.distanceToSqr(target));
		List<Integer> ready = new ArrayList<>();
		for (int i = 0; i < list.size() && i < cooldowns.length; i++) {
			Defs.AttackDef a = list.get(i);
			if (cooldowns[i] > 0 || a == last && list.size() > 1) continue;
			if (d < a.min() || d > a.max()) continue;
			if (!a.kind().equals("roar") && !a.kind().equals("ward") && !a.kind().equals("summon") && !mob.hasLineOfSight(target)) continue;
			if (a.kind().equals("ward") && mob.getHealth() > mob.getMaxHealth() * 0.85f && a.heal() > 0) continue;
			if (a.kind().equals("summon") && level.getEntitiesOfClass(MatrioMob.class, mob.getBoundingBox().inflate(16)).size() > 6) continue;
			ready.add(i);
		}
		if (ready.isEmpty()) return;
		int pick = ready.get(mob.getRandom().nextInt(ready.size()));
		start(level, list.get(pick), pick, target);
	}

	private void start(ServerLevel level, Defs.AttackDef a, int idx, LivingEntity target) {
		float speed = Defs.speedMultiplier(mob.def().world());
		cooldowns[idx] = (int) (a.cooldown() / speed);
		global = (int) (16 / speed);
		current = a;
		last = a;
		t = 0;
		landed = false;
		mark = target.position();
		dashDir = null;
		mob.triggerAnim("attack", a.id());
		if (!a.kind().equals("leap")) mob.getNavigation().stop();
		if (DEBUG) org.slf4j.LoggerFactory.getLogger("matriochka").info("[moves] {} starts {}", mob.def().id(), a.id());
	}

	private void run(ServerLevel level, LivingEntity target) {
		Defs.AttackDef a = current;
		t++;
		if (target != null && !a.kind().equals("dash")) mob.getLookControl().setLookAt(target, 30, 30);
		if (!a.kind().equals("leap") && !a.kind().equals("blink") && !a.kind().equals("dash")) mob.getNavigation().stop();
		if (t == Math.max(1, a.hit() - 6)) sound(level, a, 0.8f);
		if (target != null && target.isAlive()) {
			switch (a.kind()) {
				case "melee" -> {
					if (t >= a.hit() && (t - a.hit()) % a.interval() == 0 && (t - a.hit()) / a.interval() < a.hits()
						&& mob.distanceToSqr(target) < (a.radius() + 0.6) * (a.radius() + 0.6)) {
						hurt(level, target, a);
						puff(level, target.position().add(0, 1, 0), a, 6, 0.3);
					}
				}
				case "leap" -> {
					if (t == a.hit()) {
						Vec3 to = target.position().subtract(mob.position());
						Vec3 h = new Vec3(to.x, 0, to.z).normalize().scale(Math.min(1.3, 0.35 + to.horizontalDistance() * 0.12));
						double up = mob.isNoGravity() || mob.isInWater() ? Mth.clamp(to.y * 0.15, -0.6, 0.6) : a.lift();
						mob.setDeltaMovement(h.x, up, h.z);
						mob.needsSync = true;
						puff(level, mob.position(), a, 10, 0.4);
					}
					if (t > a.hit() && !landed && mob.getBoundingBox().inflate(0.6).intersects(target.getBoundingBox())) {
						landed = true;
						hurt(level, target, a);
					}
				}
				case "dash" -> {
					if (t == a.hit()) dashDir = target.position().subtract(mob.position()).multiply(1, 0, 1).normalize();
					if (dashDir != null && t >= a.hit() && t < a.hit() + 8) {
						mob.setDeltaMovement(dashDir.x * 0.9, mob.getDeltaMovement().y, dashDir.z * 0.9);
						mob.needsSync = true;
						puff(level, mob.position(), a, 2, 0.3);
						if (!landed && mob.getBoundingBox().inflate(0.4).intersects(target.getBoundingBox())) {
							landed = true;
							hurt(level, target, a);
							Vec3 side = new Vec3(-dashDir.z, 0, dashDir.x).scale(a.knock());
							target.push(side.x + dashDir.x * 0.5, 0.3, side.z + dashDir.z * 0.5);
							target.needsSync = true;
						}
					}
				}
				case "ring" -> {
					if (t == a.hit()) {
						for (LivingEntity e : around(level, mob.position(), a.radius())) {
							hurt(level, e, a);
							if (a.lift() != 0) { e.push(0, a.lift(), 0); e.needsSync = true; }
						}
						circle(level, mob.position(), a.radius(), a, 28);
						if (a.mult() >= 0.9f) level.sendParticles(ParticleTypes.EXPLOSION, mob.getX(), mob.getY() + 0.3, mob.getZ(), 1, 0, 0, 0, 0);
					}
				}
				case "quake" -> {
					int i = t - a.hit();
					if (i >= 0 && i % a.interval() == 0 && i / a.interval() < a.hits()) {
						double r = a.radius() * (i / a.interval() + 1) / a.hits();
						circle(level, mob.position(), r, a, 36);
						for (LivingEntity e : around(level, mob.position(), r)) {
							double dist = e.position().distanceTo(mob.position());
							if (dist > r - 1.6 && e.onGround()) {
								hurt(level, e, a);
								e.push(0, 0.35, 0);
								e.needsSync = true;
							}
						}
					}
				}
				case "cone" -> {
					if (t == a.hit()) {
						Vec3 look = mob.getLookAngle().multiply(1, 0, 1).normalize();
						for (LivingEntity e : around(level, mob.position(), a.radius())) {
							Vec3 to = e.position().subtract(mob.position()).multiply(1, 0, 1).normalize();
							if (to.dot(look) > 0.35) {
								hurt(level, e, a);
								e.push(to.x * a.knock(), 0.25 + a.lift(), to.z * a.knock());
								e.needsSync = true;
							}
						}
						for (int k = 1; k <= 4; k++) {
							Vec3 p = mob.position().add(look.scale(a.radius() * k / 4)).add(0, 1, 0);
							level.sendParticles(particle(a), p.x, p.y, p.z, 4, k * 0.25, 0.3, k * 0.25, 0.02);
						}
					}
				}
				case "bolt" -> {
					int i = t - a.hit();
					if (i >= 0 && i % a.interval() == 0 && i / a.interval() < a.hits()) {
						Vec3 from = mob.getEyePosition();
						Vec3 to = target.getEyePosition().add((mob.getRandom().nextDouble() - 0.5) * 0.4 * (a.hits() - 1), 0, (mob.getRandom().nextDouble() - 0.5) * 0.4 * (a.hits() - 1));
						line(level, from, to, a);
						if (i > 0) sound(level, a, 0.5f);
						if (mob.hasLineOfSight(target) && from.distanceTo(to) <= a.radius()) hurt(level, target, a);
					}
				}
				case "beam" -> {
					int i = t - a.hit();
					if (i >= 0 && i / a.interval() < a.hits()) {
						Vec3 from = mob.getEyePosition();
						Vec3 to = target.getEyePosition();
						if (i % 2 == 0) line(level, from, to, a);
						if (i % a.interval() == 0 && mob.hasLineOfSight(target) && from.distanceTo(to) <= a.radius()) hurt(level, target, a);
					}
				}
				case "pull" -> {
					if (t == a.hit() && mob.hasLineOfSight(target)) {
						line(level, mob.getEyePosition(), target.getEyePosition(), a);
						Vec3 pull = mob.position().subtract(target.position()).normalize().scale(a.knock()).add(0, 0.3, 0);
						target.setDeltaMovement(pull);
						target.needsSync = true;
					}
					if (t == a.hit() + 6 && mob.distanceToSqr(target) < 9) hurt(level, target, a);
				}
				case "grab" -> {
					if (t == a.hit() && mob.distanceToSqr(target) < (a.radius() + 0.8) * (a.radius() + 0.8)) {
						hurt(level, target, a);
						target.addEffect(new MobEffectInstance(effect("slowness"), a.hold(), 9));
						target.addEffect(new MobEffectInstance(effect("jump_boost"), a.hold(), 250));
						target.setDeltaMovement(Vec3.ZERO);
						target.needsSync = true;
						if (a.heal() > 0) mob.heal(mob.getMaxHealth() * a.heal());
						puff(level, target.position().add(0, 1, 0), a, 12, 0.4);
					}
				}
				case "blink" -> {
					if (t == a.hit() - 1) puff(level, mob.position(), a, 24, 0.5);
					if (t == a.hit()) {
						Vec3 back = target.getLookAngle().multiply(1, 0, 1).normalize().scale(-1.8);
						Vec3 dest = target.position().add(back);
						if (level.noCollision(mob, mob.getBoundingBox().move(dest.subtract(mob.position())))) {
							mob.teleportTo(dest.x, dest.y, dest.z);
							mob.lookAt(target, 180, 180);
						}
						puff(level, mob.position(), a, 24, 0.5);
					}
					if (t == a.hit() + 2 && mob.distanceToSqr(target) < 9) hurt(level, target, a);
				}
				case "spin" -> {
					int i = t - a.hit();
					if (i >= 0 && i % a.interval() == 0 && i / a.interval() < a.hits()) {
						for (LivingEntity e : around(level, mob.position(), a.radius())) hurt(level, e, a);
						circle(level, mob.position().add(0, 0.8, 0), a.radius(), a, 16);
					}
				}
				case "rain" -> {
					if (t < a.hit() && t % 3 == 0) circle(level, mark, a.radius(), a, 20);
					if (t == a.hit()) {
						for (LivingEntity e : around(level, mark, a.radius())) {
							hurt(level, e, a);
							if (a.lift() != 0) { e.push(0, a.lift(), 0); e.needsSync = true; }
						}
						level.sendParticles(particle(a), mark.x, mark.y + 3, mark.z, 40, a.radius() * 0.4, 1.5, a.radius() * 0.4, 0.05);
						level.sendParticles(ParticleTypes.EXPLOSION, mark.x, mark.y + 0.2, mark.z, 1, 0, 0, 0, 0);
						sound(level, a, 1f);
					}
				}
				case "trail" -> {
					if (t == a.hit()) {
						AreaEffectCloud cloud = new AreaEffectCloud(level, mob.getX(), mob.getY(), mob.getZ());
						cloud.setRadius(a.radius());
						cloud.setDuration(a.duration());
						cloud.setRadiusPerTick(-a.radius() / a.duration() * 0.5f);
						cloud.setCustomParticle(particle(a));
						for (MobEffectInstance e : effects(a.effects())) cloud.addEffect(e);
						if (a.fire() > 0 || !a.gauges().isEmpty()) cloud.addEffect(new MobEffectInstance(effect("slowness"), 20, 0));
						cloud.setOwner(mob);
						level.addFreshEntity(cloud);
						for (LivingEntity e : around(level, mob.position(), a.radius())) afflict(level, e, a);
					}
				}
				case "roar" -> {
					if (t == a.hit()) {
						for (LivingEntity e : around(level, mob.position(), a.radius())) afflict(level, e, a);
						circle(level, mob.position().add(0, 1, 0), a.radius() * 0.6, a, 32);
						sound(level, a, 1.3f);
					}
				}
				case "summon" -> {
					if (t == a.hit()) {
						var type = ModContent.entity(a.summon());
						for (int i = 0; i < a.count(); i++) {
							Entity e = type.create(level, EntitySpawnReason.MOB_SUMMONED);
							if (e instanceof MatrioMob m) {
								m.addTag("matrio_child");
								m.setPos(mob.getX() + mob.getRandom().nextGaussian(), mob.getY(), mob.getZ() + mob.getRandom().nextGaussian());
								m.setTarget(target);
								level.addFreshEntity(m);
								puff(level, m.position(), a, 16, 0.4);
							}
						}
					}
				}
				case "ward" -> {
					if (t == a.hit()) {
						for (MobEffectInstance e : effects(a.self())) mob.addEffect(e);
						if (a.heal() > 0) mob.heal(mob.getMaxHealth() * a.heal());
						puff(level, mob.position().add(0, mob.getBbHeight() * 0.5, 0), a, 20, 0.6);
					}
				}
				default -> {}
			}
		}
		if (t >= a.end()) current = null;
	}

	// ---------------------------------------------------------------- helpers
	private List<LivingEntity> around(ServerLevel level, Vec3 at, double r) {
		return level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(r, 2, r),
			e -> e != mob && !(e instanceof MatrioMob) && !(e instanceof MatrioBoss) && e.isAlive() && e.position().distanceTo(at) <= r + 0.5
				&& !(e instanceof ServerPlayer p && (p.isCreative() || p.isSpectator())));
	}

	private void hurt(ServerLevel level, LivingEntity e, Defs.AttackDef a) {
		if (a.mult() > 0) e.hurtServer(level, mob.damageSources().mobAttack(mob), (float) mob.getAttributeValue(Attributes.ATTACK_DAMAGE) * a.mult());
		afflict(level, e, a);
	}

	private void afflict(ServerLevel level, LivingEntity e, Defs.AttackDef a) {
		for (MobEffectInstance fx : effects(a.effects())) e.addEffect(new MobEffectInstance(fx));
		if (a.fire() > 0) e.igniteForSeconds(a.fire());
		if (!a.gauges().isEmpty() && e instanceof ServerPlayer sp) {
			PlayerState ps = PlayerState.of(sp);
			for (String g : a.gauges().split(",")) {
				String[] kv = g.split(":");
				ps.addGauge(kv[0], Integer.parseInt(kv[1]));
			}
			ps.sync();
		}
	}

	private static List<MobEffectInstance> effects(String spec) {
		if (spec.isEmpty()) return List.of();
		return FX_CACHE.computeIfAbsent(spec, s -> {
			List<MobEffectInstance> out = new ArrayList<>();
			for (String part : s.split(",")) {
				String[] p = part.split(":");
				Holder<MobEffect> h = effect(p[0]);
				if (h != null) out.add(new MobEffectInstance(h, Integer.parseInt(p[1]), Integer.parseInt(p[2])));
			}
			return out;
		});
	}

	private static Holder<MobEffect> effect(String id) {
		return BuiltInRegistries.MOB_EFFECT.get(Identifier.withDefaultNamespace(id)).map(r -> (Holder<MobEffect>) r).orElse(null);
	}

	private static ParticleOptions particle(Defs.AttackDef a) {
		var type = BuiltInRegistries.PARTICLE_TYPE.getValue(Identifier.withDefaultNamespace(a.particle()));
		return type instanceof SimpleParticleType s ? s : ParticleTypes.CRIT;
	}

	private void sound(ServerLevel level, Defs.AttackDef a, float volume) {
		SoundEvent s = BuiltInRegistries.SOUND_EVENT.getValue(Identifier.withDefaultNamespace(a.sound()));
		if (s == null) s = SoundEvents.PLAYER_ATTACK_SWEEP;
		level.playSound(null, mob.blockPosition(), s, SoundSource.HOSTILE, volume, 0.85f + mob.getRandom().nextFloat() * 0.3f);
	}

	private void puff(ServerLevel level, Vec3 at, Defs.AttackDef a, int n, double spread) {
		level.sendParticles(particle(a), at.x, at.y + 0.5, at.z, n, spread, 0.4, spread, 0.02);
	}

	private void line(ServerLevel level, Vec3 from, Vec3 to, Defs.AttackDef a) {
		ParticleOptions p = particle(a);
		int steps = (int) (from.distanceTo(to) * 2.5);
		for (int i = 0; i <= steps; i++) {
			Vec3 q = from.lerp(to, i / (double) Math.max(1, steps));
			level.sendParticles(p, q.x, q.y, q.z, 1, 0.03, 0.03, 0.03, 0);
		}
	}

	private void circle(ServerLevel level, Vec3 at, double r, Defs.AttackDef a, int n) {
		ParticleOptions p = particle(a);
		for (int i = 0; i < n; i++) {
			double ang = i * Math.PI * 2 / n;
			level.sendParticles(p, at.x + Math.cos(ang) * r, at.y + 0.15, at.z + Math.sin(ang) * r, 1, 0.05, 0.05, 0.05, 0);
		}
	}
}
