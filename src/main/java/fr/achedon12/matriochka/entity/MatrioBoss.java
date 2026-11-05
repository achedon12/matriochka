package fr.achedon12.matriochka.entity;

import com.geckolib.animatable.GeoEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.animation.object.PlayState;
import com.geckolib.constant.DefaultAnimations;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Worlds;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

/**
 * Boss with readable attacks: every attack is announced (animation, sound and particles), executed, then followed by an
 * opening where the boss takes extra damage. Phases change at 66% and 33% of its health (50% for the Block Guardian,
 * every shell for the Unfinished).
 */
public class MatrioBoss extends Monster implements GeoEntity {
	private static final RawAnimation CHARGE = RawAnimation.begin().thenPlayAndHold("attack.charge");
	private static final RawAnimation SLAM = RawAnimation.begin().thenPlay("attack.slam");
	private static final RawAnimation CAST = RawAnimation.begin().thenPlay("attack.cast");
	private static final RawAnimation STRIKE = RawAnimation.begin().thenPlay("attack.strike");
	private static final RawAnimation PHASE = RawAnimation.begin().thenPlay("misc.phase");
	private static final RawAnimation REST = RawAnimation.begin().thenPlay("misc.rest");

	private enum State { CHASE, TELEGRAPH, OPENING, PHASE }

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
	public final Defs.BossDef def;
	private final ServerBossEvent bar;
	private State state = State.CHASE;
	private int stateTicks;
	private int attack;
	private int phase;
	private final long[] lastUse = new long[3];
	private Vec3 aim = Vec3.ZERO;
	private int nodes;

	public MatrioBoss(EntityType<? extends Monster> type, Level level, Defs.BossDef def) {
		super(type, level);
		this.def = def;
		this.xpReward = 200;
		this.bar = new ServerBossEvent(java.util.UUID.randomUUID(), Component.translatable("entity.matriochka." + def.id()), color(def.world()), BossEvent.BossBarOverlay.NOTCHED_10);
		setPersistenceRequired();
		if (def.flying() || def.aquatic()) setNoGravity(true);
	}

	private static BossEvent.BossBarColor color(int w) {
		return switch (w) {
			case 1 -> BossEvent.BossBarColor.GREEN;
			case 2 -> BossEvent.BossBarColor.RED;
			case 3, 5 -> BossEvent.BossBarColor.WHITE;
			case 4, 7 -> BossEvent.BossBarColor.BLUE;
			case 6 -> BossEvent.BossBarColor.PINK;
			case 8 -> BossEvent.BossBarColor.YELLOW;
			default -> BossEvent.BossBarColor.PURPLE;
		};
	}

	public static AttributeSupplier.Builder attributes(Defs.BossDef def) {
		return Monster.createMonsterAttributes()
			.add(Attributes.MAX_HEALTH, def.hp())
			.add(Attributes.ATTACK_DAMAGE, def.damage())
			.add(Attributes.MOVEMENT_SPEED, 0.24)
			.add(Attributes.FOLLOW_RANGE, 48)
			.add(Attributes.ARMOR, 8)
			.add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
			.add(Attributes.FLYING_SPEED, 0.4);
	}

	/** Spawns a boss, scaling health with the number of players near it. */
	public static MatrioBoss summon(ServerLevel level, String id, BlockPos at, ServerPlayer by) {
		Entity e = ModContent.entity(id).create(level, EntitySpawnReason.EVENT);
		if (!(e instanceof MatrioBoss boss)) return null;
		int players = Math.max(1, level.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(at).inflate(48)).size());
		float hp = boss.def.hp() * Defs.bossHealthPlayers(players);
		boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(hp);
		boss.setHealth(hp);
		boss.setPos(Vec3.atBottomCenterOf(at));
		boss.setTarget(by);
		level.addFreshEntity(boss);
		level.playSound(null, at, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 0.8f, 0.8f + boss.def.world() * 0.03f);
		boss.triggerAnim("action", "phase");
		return boss;
	}

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 24f));
		targetSelector.addGoal(1, new HurtByTargetGoal(this));
		targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	@Override
	public void startSeenByPlayer(ServerPlayer player) {
		super.startSeenByPlayer(player);
		bar.addPlayer(player);
	}

	@Override
	public void stopSeenByPlayer(ServerPlayer player) {
		super.stopSeenByPlayer(player);
		bar.removePlayer(player);
	}

	private int world() {
		if (def.world() == 10) return Math.max(1, Math.min(9, phase + 1));
		return def.world();
	}

	// ---------------------------------------------------------------- the attack state machine
	@Override
	protected void customServerAiStep(ServerLevel level) {
		super.customServerAiStep(level);
		bar.setProgress(getHealth() / getMaxHealth());
		LivingEntity target = getTarget();
		stateTicks++;
		if (nodes > 0) {
			long alive = level.getEntitiesOfClass(MatrioMob.class, getBoundingBox().inflate(32), m -> m.entityTags().contains("boss_node")).size();
			if (alive == 0) {
				nodes = 0;
				level.playSound(null, blockPosition(), SoundEvents.TURTLE_EGG_CRACK, SoundSource.HOSTILE, 2f, 0.5f);
			}
		}
		if (target == null || !target.isAlive()) {
			state = State.CHASE;
			return;
		}
		double d = distanceTo(target);
		switch (state) {
			case CHASE -> {
				if (def.flying() || def.aquatic()) {
					Vec3 goal = target.position().add(0, def.flying() ? 5 : 1, 0);
					setDeltaMovement(getDeltaMovement().scale(0.85).add(goal.subtract(position()).normalize().scale(0.08)));
					lookAt(target, 20, 20);
				} else if (d > 3.5) {
					getNavigation().moveTo(target, 1.0 + 0.05 * phase);
				} else {
					getNavigation().stop();
				}
				int pick = chooseAttack(level, d);
				if (pick >= 0 && stateTicks > 10) {
					attack = pick;
					aim = target.position();
					state = State.TELEGRAPH;
					stateTicks = 0;
					getNavigation().stop();
					triggerAnim("action", attack == 0 ? "strike" : "charge");
					level.playSound(null, blockPosition(), telegraphSound(), SoundSource.HOSTILE, 1.4f, 0.7f + 0.1f * attack);
					announce(level);
				}
			}
			case TELEGRAPH -> {
				int tele = Defs.telegraphTicks(world()) * (attack == 2 ? 2 : 1);
				if (attack == 0) tele = Math.max(6, tele / 2);
				telegraphParticles(level);
				if (stateTicks >= tele) {
					execute(level, target);
					lastUse[attack] = level.getGameTime();
					state = attack == 0 ? State.CHASE : State.OPENING;
					if (state == State.OPENING) triggerAnim("action", "rest");
					stateTicks = 0;
				}
			}
			case OPENING -> {
				if (stateTicks >= Defs.openingTicks(world()) * (attack == 2 ? 1 : 2) / 2) {
					state = State.CHASE;
					stateTicks = 0;
				}
			}
			case PHASE -> {
				if (stateTicks >= 40) {
					state = State.CHASE;
					stateTicks = 0;
				}
			}
		}
	}

	private int chooseAttack(ServerLevel level, double distance) {
		long now = level.getGameTime();
		int speedUp = phase * 20;
		boolean sig = now - lastUse[2] > 400 - speedUp;
		boolean med = now - lastUse[1] > 160 - speedUp / 2;
		boolean light = now - lastUse[0] > 80 - speedUp / 4;
		if (sig && (phase > 0 || random.nextInt(3) == 0)) return 2;
		if (med && distance > 4) return 1;
		if (light && distance <= 5) return 0;
		if (med) return 1;
		return -1;
	}

	private net.minecraft.sounds.SoundEvent telegraphSound() {
		return switch (world()) {
			case 1 -> SoundEvents.SNIFFER_SCENTING;
			case 2 -> SoundEvents.BLAZE_SHOOT;
			case 3 -> SoundEvents.CHAIN_PLACE;
			case 4 -> SoundEvents.TRIDENT_THUNDER.value();
			case 5 -> SoundEvents.WARDEN_ANGRY;
			case 6 -> SoundEvents.ILLUSIONER_PREPARE_MIRROR;
			case 7 -> SoundEvents.ELDER_GUARDIAN_CURSE;
			case 8 -> SoundEvents.BELL_RESONATE;
			case 9 -> SoundEvents.RAVAGER_ROAR;
			default -> SoundEvents.IRON_GOLEM_ATTACK;
		};
	}

	private void announce(ServerLevel level) {
		Component name = Component.translatable("boss.matriochka." + def.id() + ".attack" + attack).withStyle(attack == 2 ? ChatFormatting.RED : ChatFormatting.GOLD);
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(40))) p.sendOverlayMessage(name);
	}

	private void telegraphParticles(ServerLevel level) {
		if (attack == 0) return;
		double r = attack == 2 ? 5 : 3;
		for (int i = 0; i < 12; i++) {
			double a = random.nextDouble() * Math.PI * 2;
			level.sendParticles(attack == 2 ? ParticleTypes.FLAME : ParticleTypes.CRIT, aim.x + Math.cos(a) * r, aim.y + 0.1, aim.z + Math.sin(a) * r, 1, 0, 0.02, 0, 0);
		}
	}

	private float dmg(float f) {
		return (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * f;
	}

	private List<LivingEntity> victims(ServerLevel level, Vec3 c, double r) {
		return level.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(c, c).inflate(r, 3, r),
			e -> e != this && !(e instanceof MatrioMob) && !(e instanceof MatrioBoss) && e.position().distanceTo(c) <= r + 0.5);
	}

	/** Executes the current attack, keyed by the (shell) world. */
	private void execute(ServerLevel level, LivingEntity target) {
		triggerAnim("action", attack == 1 ? "cast" : "slam");
		int w = def.world() == 0 ? 0 : world();
		if (attack == 0) {
			for (LivingEntity e : victims(level, position().add(getLookAngle().scale(2)), 3.2)) e.hurtServer(level, damageSources().mobAttack(this), dmg(0.6f));
			level.playSound(null, blockPosition(), SoundEvents.PLAYER_ATTACK_STRONG, SoundSource.HOSTILE, 1.2f, 0.6f);
			return;
		}
		boolean sig = attack == 2;
		switch (w) {
			case 0 -> {
				if (sig) throwBlocks(level, target);
				else shockwave(level, 7, dmg(0.7f));
			}
			case 1 -> {
				if (sig) summon(level, "sporeling", 4 + phase * 2);
				else cloud(level, aim, MobEffects.POISON, 4f);
			}
			case 2 -> {
				if (sig) ringOfFire(level, 6 + phase * 2);
				else zone(level, aim, 3.5, dmg(0.8f), ParticleTypes.LAVA);
			}
			case 3 -> {
				if (sig) cageAll(level);
				else pull(level, target, 1.6);
			}
			case 4 -> {
				if (sig) for (int i = 0; i < 4 + phase; i++) lightning(level, aim.add(random.nextGaussian() * 4, 0, random.nextGaussian() * 4));
				else push(level, 2.5);
			}
			case 5 -> {
				if (sig) dash(level, target, 2.2);
				else darkness(level);
			}
			case 6 -> {
				if (sig) for (LivingEntity e : victims(level, position(), 16)) e.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 40, 2));
				else copyWeapon(level, target);
			}
			case 7 -> {
				if (sig) pull(level, target, 2.0);
				else dash(level, target, 1.8);
				for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(20))) PlayerState.of(p).addGauge("oxygen", sig ? -15 : -5);
			}
			case 8 -> {
				var eff = switch ((int) ((level.getGameTime() / 200 + phase) % 4)) {
					case 0 -> MobEffects.POISON;
					case 1 -> MobEffects.SLOWNESS;
					case 2 -> MobEffects.WEAKNESS;
					default -> MobEffects.WITHER;
				};
				if (sig) {
					cloud(level, position(), eff, 7f);
					shockwave(level, 8, dmg(0.6f));
				} else {
					zone(level, aim, 4, dmg(0.7f), ParticleTypes.CHERRY_LEAVES);
				}
			}
			case 9 -> {
				if (sig) chasm(level, aim);
				else groundWave(level, target);
			}
			default -> shockwave(level, 6, dmg(0.6f));
		}
	}

	private void shockwave(ServerLevel level, double r, float dmg) {
		level.sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + 0.2, getZ(), 10, r / 2, 0.1, r / 2, 0);
		for (LivingEntity e : victims(level, position(), r)) {
			if (e.onGround()) {
				e.hurtServer(level, damageSources().mobAttack(this), dmg);
				e.push(0, 0.7, 0);
				e.needsSync = true;
			}
		}
		level.playSound(null, blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1f, 0.6f);
	}

	private void zone(ServerLevel level, Vec3 c, double r, float dmg, net.minecraft.core.particles.ParticleOptions p) {
		level.sendParticles(p, c.x, c.y + 0.3, c.z, 40, r / 2, 0.3, r / 2, 0.05);
		for (LivingEntity e : victims(level, c, r)) e.hurtServer(level, damageSources().mobAttack(this), dmg);
		level.playSound(null, BlockPos.containing(c), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 0.8f, 1f);
	}

	private void throwBlocks(ServerLevel level, LivingEntity target) {
		for (int i = 0; i < 3 + phase; i++) {
			Vec3 at = target.position().add(random.nextGaussian() * 2, 0, random.nextGaussian() * 2);
			net.minecraft.world.entity.item.FallingBlockEntity fb = net.minecraft.world.entity.item.FallingBlockEntity.fall(level,
				BlockPos.containing(at.x, at.y + 10, at.z), Blocks.COBBLESTONE.defaultBlockState());
			fb.setHurtsEntities(2f, 20);
			fb.dropItem = false;
		}
	}

	private void cloud(ServerLevel level, Vec3 at, net.minecraft.core.Holder<net.minecraft.world.effect.MobEffect> eff, float r) {
		AreaEffectCloud c = new AreaEffectCloud(level, at.x, at.y, at.z);
		c.setRadius(r);
		c.setDuration(120);
		c.addEffect(new MobEffectInstance(eff, 80, 1));
		c.setOwner(this);
		level.addFreshEntity(c);
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(at, at).inflate(r))) {
			if (world() == 1) PlayerState.of(p).addGauge("toxin", 15);
		}
	}

	private void summon(ServerLevel level, String mob, int n) {
		for (int i = 0; i < n; i++) {
			Entity e = ModContent.entity(mob).create(level, EntitySpawnReason.MOB_SUMMONED);
			if (e instanceof MatrioMob m) {
				m.setPos(getX() + random.nextGaussian() * 4, getY(), getZ() + random.nextGaussian() * 4);
				m.setTarget(getTarget());
				m.addTag("matrio_child");
				level.addFreshEntity(m);
			}
		}
	}

	private void ringOfFire(ServerLevel level, int r) {
		for (int i = 0; i < 48; i++) {
			double a = i * Math.PI * 2 / 48;
			BlockPos p = BlockPos.containing(getX() + Math.cos(a) * r, getY(), getZ() + Math.sin(a) * r);
			if (level.getBlockState(p).isAir() && !level.getBlockState(p.below()).isAir()) level.setBlock(p, Blocks.FIRE.defaultBlockState(), 3);
		}
		shockwave(level, r, dmg(0.5f));
	}

	private void cageAll(ServerLevel level) {
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(16))) {
			BlockPos at = p.blockPosition();
			for (int dx = -1; dx <= 1; dx++)
				for (int dz = -1; dz <= 1; dz++)
					for (int dy = 0; dy <= 2; dy++)
						if ((Math.abs(dx) == 1 || Math.abs(dz) == 1) && level.getBlockState(at.offset(dx, dy, dz)).isAir())
							level.setBlock(at.offset(dx, dy, dz), Blocks.IRON_BARS.defaultBlockState(), 3);
		}
		level.playSound(null, blockPosition(), SoundEvents.IRON_DOOR_CLOSE, SoundSource.HOSTILE, 1.5f, 0.4f);
	}

	private void pull(ServerLevel level, LivingEntity target, double s) {
		for (LivingEntity e : victims(level, position(), 18)) {
			e.setDeltaMovement(position().subtract(e.position()).normalize().scale(s).add(0, 0.3, 0));
			e.needsSync = true;
		}
		level.playSound(null, blockPosition(), SoundEvents.CHAIN_BREAK, SoundSource.HOSTILE, 1.5f, 0.5f);
	}

	private void push(ServerLevel level, double s) {
		for (LivingEntity e : victims(level, position(), 14)) {
			Vec3 v = e.position().subtract(position()).normalize().scale(s);
			e.setDeltaMovement(v.x, 0.5, v.z);
			e.needsSync = true;
		}
		level.sendParticles(ParticleTypes.GUST, getX(), getY() + 1, getZ(), 12, 3, 1, 3, 0);
	}

	private void lightning(ServerLevel level, Vec3 at) {
		LightningBolt bolt = net.minecraft.world.entity.EntityTypes.LIGHTNING_BOLT.create(level, EntitySpawnReason.TRIGGERED);
		if (bolt != null) {
			bolt.setPos(at);
			level.addFreshEntity(bolt);
		}
	}

	private void dash(ServerLevel level, LivingEntity target, double s) {
		Vec3 v = target.position().subtract(position()).normalize().scale(s);
		setDeltaMovement(v.x, 0.2, v.z);
		needsSync = true;
		for (LivingEntity e : victims(level, target.position(), 2.5)) e.hurtServer(level, damageSources().mobAttack(this), dmg(0.9f));
	}

	private void darkness(ServerLevel level) {
		for (LivingEntity e : victims(level, position(), 24)) e.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 160, 0));
		for (BlockPos p : BlockPos.betweenClosed(blockPosition().offset(-10, -3, -10), blockPosition().offset(10, 6, 10))) {
			var st = level.getBlockState(p);
			if (st.is(Blocks.TORCH) || st.is(Blocks.WALL_TORCH) || st.is(Blocks.LANTERN)) level.destroyBlock(p, true);
		}
	}

	private void copyWeapon(ServerLevel level, LivingEntity target) {
		ItemStack held = target.getMainHandItem().copy();
		setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND, held);
		zone(level, target.position(), 3, dmg(0.7f), ParticleTypes.REVERSE_PORTAL);
	}

	private void groundWave(ServerLevel level, LivingEntity target) {
		Vec3 dir = target.position().subtract(position()).normalize();
		for (int i = 1; i < 14; i++) {
			Vec3 p = position().add(dir.scale(i));
			level.sendParticles(ParticleTypes.EXPLOSION, p.x, p.y, p.z, 1, 0, 0, 0, 0);
			for (LivingEntity e : victims(level, p, 1.5)) {
				e.hurtServer(level, damageSources().mobAttack(this), dmg(0.6f));
				e.push(0, 0.8, 0);
			}
		}
	}

	private void chasm(ServerLevel level, Vec3 at) {
		for (LivingEntity e : victims(level, at, 4)) {
			e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 4));
			e.hurtServer(level, damageSources().mobAttack(this), dmg(1f));
		}
		level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, at.x, at.y, at.z, 30, 2, 0.2, 2, 0.02);
	}

	// ---------------------------------------------------------------- damage, phases, death
	@Override
	public boolean hurtServer(ServerLevel level, DamageSource source, float amount) {
		if (state == State.PHASE || nodes > 0) {
			level.playSound(null, blockPosition(), SoundEvents.SHIELD_BLOCK.value(), SoundSource.HOSTILE, 1f, 0.6f);
			return false;
		}
		float mult = state == State.OPENING ? 1.5f : 0.75f;
		if (def.id().equals("ash_titan") && phase >= 2) mult += 0.3f;
		boolean r = super.hurtServer(level, source, amount * mult);
		checkPhase(level);
		return r;
	}

	private void checkPhase(ServerLevel level) {
		float f = getHealth() / getMaxHealth();
		float[] ph = def.phases();
		if (phase < ph.length && f <= ph[phase] && isAlive()) {
			phase++;
			state = State.PHASE;
			stateTicks = 0;
			triggerAnim("action", "phase");
			level.playSound(null, blockPosition(), SoundEvents.ENDER_DRAGON_GROWL, SoundSource.HOSTILE, 1.5f, 0.8f + phase * 0.05f);
			bar.setName(Component.translatable("entity.matriochka." + def.id()).append(" — " + "I".repeat(Math.min(phase + 1, 3))));
			getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(getAttributeBaseValue(Attributes.MOVEMENT_SPEED) * 1.1);
			if (def.id().equals("spore_queen") && phase == 2) {
				summon(level, "chitin_guard", 3);
				for (MatrioMob m : level.getEntitiesOfClass(MatrioMob.class, getBoundingBox().inflate(8))) m.addTag("boss_node");
				nodes = 3;
			}
			if (def.id().equals("block_guardian")) heal(getMaxHealth() * 0.1f);
			if (def.id().equals("the_unfinished")) {
				Component shell = Component.translatable("message.matriochka.shell", phase + 1, Component.translatable("world.matriochka." + Math.min(9, phase + 1)));
				for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48))) p.sendSystemMessage(shell);
			}
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48))) {
				p.sendOverlayMessage(Component.translatable("boss.matriochka." + def.id() + ".attack3").withStyle(ChatFormatting.DARK_RED));
			}
		}
	}

	@Override
	public void die(DamageSource source) {
		super.die(source);
		bar.removeAllPlayers();
		if (!(level() instanceof ServerLevel level)) return;
		MatrioData data = MatrioData.get(level.getServer());
		int w = def.world();
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(64))) {
			String group = data.groupOf(p.getUUID());
			data.markDefeated(group, w);
			PlayerState ps = PlayerState.of(p);
			ps.addSouls(100);
			ps.progress("kill", def.id(), 1);
			// doll of life: one layer after worlds 1, 5 and 8; every boss refills one layer
			int max = ps.dollMax();
			if (w == 1 || w == 5 || w == 8) max = Math.min(3, max + 1);
			ps.setDoll(ps.dollLayers() + 1, max);
			ps.set("boss_" + w, true);
			p.sendSystemMessage(Component.translatable("message.matriochka.boss_down." + w).withStyle(ChatFormatting.GOLD));
			if (w == 0) {
				for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
					if (p.getInventory().getItem(i).is(ModContent.item("artisan_scroll"))) p.getInventory().setItem(i, new ItemStack(ModContent.item("artisan_journal")));
				}
			}
			ps.sync();
		}
		spawnAtLocation(level, new ItemStack(ModContent.item(def.core())));
		if (w == 0) {
			spawnAtLocation(level, new ItemStack(ModContent.item("matrix_workbench")));
			spawnAtLocation(level, new ItemStack(ModContent.item("world_soil_0"), 4));
		} else if (w < 10) {
			spawnAtLocation(level, new ItemStack(ModContent.item("world_soil_" + w), 4));
			if (w == 9) spawnAtLocation(level, new ItemStack(ModContent.item("last_doll_key")));
		}
		level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, getX(), getY() + 2, getZ(), 120, 1.5, 2, 1.5, 0.5);
		level.playSound(null, blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.HOSTILE, 1.5f, 1f);
		data.changed();
	}

	@Override
	public boolean removeWhenFarAway(double d) {
		return false;
	}

	@Override
	public boolean fireImmune() {
		return true;
	}

	@Override
	public boolean causeFallDamage(double fallDistance, float multiplier, DamageSource source) {
		return false;
	}

	public int phase() {
		return phase;
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(DefaultAnimations.genericWalkIdleController());
		controllers.add(new AnimationController<MatrioBoss>("action", 3, test -> PlayState.STOP)
			.triggerableAnim("charge", CHARGE).triggerableAnim("slam", SLAM).triggerableAnim("cast", CAST)
			.triggerableAnim("strike", STRIKE).triggerableAnim("phase", PHASE).triggerableAnim("rest", REST));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}

	public static Defs.BossDef byWorld(int w) {
		for (Defs.BossDef b : Content.BOSSES) if (b.world() == w) return b;
		return Content.BOSSES.getFirst();
	}

	public static boolean inArena(Level level, BlockPos p) {
		return Worlds.isModWorld(level) && Math.abs(p.getZ() - Worlds.ARENA_OFFSET) < 24;
	}
}
