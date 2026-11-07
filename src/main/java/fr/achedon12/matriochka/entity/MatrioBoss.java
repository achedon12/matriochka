package fr.achedon12.matriochka.entity;

import com.geckolib.animatable.GeoEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.animation.object.PlayState;
import com.geckolib.constant.DefaultAnimations;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.BossAnims;
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

	/** Shell Shards every fighter gets: enough to bring each world's weapon to the class cap (see tools/balance.py). */
	public static final int SHELL_SHARDS = 3;

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
	public final Defs.BossDef def;
	private final ServerBossEvent bar;
	private State state = State.CHASE;
	private int stateTicks;
	private int attack;
	private int phase;
	private final BossFeats feats = new BossFeats();
	private final long[] lastUse = new long[3];
	private Vec3 aim = Vec3.ZERO;
	private int nodes;
	private int calmUntil;
	/** Set when the boss is summoned: its awakening animation is sent on its third tick. */
	private boolean awakening;
	/** Attack pace from the number of players in the fight (see Defs.bossAttackSpeedPlayers). */
	private float pace = 1f;
	/** The mutation it woke with ("" for none), see {@link #mutationTick} and world/Variants. */
	private String mutation = "";
	private boolean frenzied;
	private int echoAt = -1;

	public MatrioBoss(EntityType<? extends Monster> type, Level level, Defs.BossDef def) {
		super(type, level);
		this.def = def;
		this.xpReward = 200;
		this.bar = new ServerBossEvent(java.util.UUID.randomUUID(), Component.translatable("entity.matriochka." + def.id()), color(def.world()), BossEvent.BossBarOverlay.NOTCHED_10);
		// the client plays the boss theme while this bar is shown (MusicMixin)
		this.bar.setPlayBossMusic(true);
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

	/** The burst a boss wakes in: a column of its world's particles round it, and a ring on the ground. */
	private static void awakenBurst(ServerLevel level, MatrioBoss boss) {
		var particle = switch (boss.def.world()) {
			case 1 -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case 2 -> ParticleTypes.LAVA;
			case 3 -> ParticleTypes.SOUL;
			case 4 -> ParticleTypes.ELECTRIC_SPARK;
			case 5 -> ParticleTypes.SCULK_SOUL;
			case 6 -> ParticleTypes.REVERSE_PORTAL;
			case 7 -> ParticleTypes.BUBBLE_COLUMN_UP;
			case 8 -> ParticleTypes.WAX_ON;
			case 9 -> ParticleTypes.ASH;
			case 10 -> ParticleTypes.TOTEM_OF_UNDYING;
			default -> ParticleTypes.ENCHANT;
		};
		double w = boss.getBbWidth(), h = boss.getBbHeight();
		level.sendParticles(particle, boss.getX(), boss.getY() + h * 0.5, boss.getZ(), 90, w * 0.6, h * 0.5, w * 0.6, 0.15);
		for (int i = 0; i < 32; i++) {
			double a = i * Math.PI * 2 / 32;
			level.sendParticles(ParticleTypes.POOF, boss.getX() + Math.cos(a) * (w + 1), boss.getY() + 0.1, boss.getZ() + Math.sin(a) * (w + 1), 1, 0, 0, 0, 0.02);
		}
	}

	/** A boss is heard before it is seen: a breath, a growl or a hum in its world's colour, every few seconds. */
	@Override
	protected net.minecraft.sounds.SoundEvent getAmbientSound() {
		return fr.achedon12.matriochka.content.Sounds.presence(def.world());
	}

	@Override
	public int getAmbientSoundInterval() {
		return 140;
	}

	@Override
	protected float getSoundVolume() {
		return 2.0f;
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
		return summon(level, id, at, by, true);
	}

	/**
	 * Spawns a boss; without its introduction (bars, title card, the camera turning to it) when {@code intro} is false,
	 * as in the Trials, where the clock is running.
	 */
	public static MatrioBoss summon(ServerLevel level, String id, BlockPos at, ServerPlayer by, boolean intro) {
		Entity e = ModContent.entity(id).create(level, EntitySpawnReason.EVENT);
		if (!(e instanceof MatrioBoss boss)) return null;
		int players = Math.max(1, level.getEntitiesOfClass(Player.class, new net.minecraft.world.phys.AABB(at).inflate(48)).size());
		int cycle = fr.achedon12.matriochka.world.Cycles.at(level, at);
		float hp = boss.def.hp() * Defs.bossHealthPlayers(players) * fr.achedon12.matriochka.world.Config.healthMult()
			* fr.achedon12.matriochka.world.Cycles.healthFactor(cycle);
		boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(hp);
		boss.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(boss.def.damage() * fr.achedon12.matriochka.world.Config.damageMult()
			* fr.achedon12.matriochka.world.Cycles.damageFactor(cycle));
		// the variant of the parcel: its danger, and from World 6 its mutation
		Defs.VariantDef variant = fr.achedon12.matriochka.world.Variants.at(level, at);
		hp *= variant.danger();
		boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(hp);
		boss.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(boss.getAttributeBaseValue(Attributes.ATTACK_DAMAGE) * variant.danger());
		boss.setHealth(hp);
		boss.pace = Defs.bossAttackSpeedPlayers(players);
		boss.mutate(fr.achedon12.matriochka.world.Variants.mutation(variant.id(), boss.def.world()));
		boss.setPos(Vec3.atBottomCenterOf(at));
		boss.setTarget(by);
		level.addFreshEntity(boss);
		level.playSound(null, at, fr.achedon12.matriochka.content.Sounds.BOSS_AWAKEN, SoundSource.HOSTILE, 2f, 1f);
		// it comes out of its shell (misc.<boss>.awaken) in a burst of its world's particles
		// triggered a couple of ticks later (see tick), once the clients track the new entity: an animation sent in
		// the tick it is added would be lost; it stands still while it comes out of its shell
		boss.awakening = true;
		boss.calm(56);
		awakenBurst(level, boss);
		if (intro) fr.achedon12.matriochka.net.Cues.bossIntro(level, boss, id);
		if (!boss.mutation.isEmpty()) {
			Component desc = Component.translatable("mutation.matriochka." + boss.mutation + ".desc");
			for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, boss.getBoundingBox().inflate(48))) {
				p.sendSystemMessage(Component.translatable("message.matriochka.mutation.woke", desc).withStyle(ChatFormatting.LIGHT_PURPLE));
			}
		}
		return boss;
	}

	// ---------------------------------------------------------------- mutations
	public String mutation() {
		return mutation;
	}

	/** Sets the mutation ("" removes it) and names it in the boss bar. */
	public void mutate(String m) {
		mutation = m == null ? "" : m;
		bar.setName(barName());
	}

	private Component barName() {
		Component name = Component.translatable("entity.matriochka." + def.id());
		if (phase > 0) name = name.copy().append(" — " + "I".repeat(Math.min(phase + 1, 3)));
		if (mutation.isEmpty()) return name;
		return Component.translatable("boss.matriochka.mutated", name, Component.translatable("mutation.matriochka." + mutation));
	}

	/** What a mutation adds every tick: a delayed echo, a light pulse, creatures out of its shell, a frenzy. */
	private void mutationTick(ServerLevel level, LivingEntity target) {
		boolean fighting = target != null && target.isAlive();
		switch (mutation) {
			case "echoing" -> {
				if (tickCount == echoAt) {
					level.sendParticles(ParticleTypes.SONIC_BOOM, getX(), getY() + 1, getZ(), 1, 0, 0, 0, 0);
					shockwave(level, 9, dmg(0.5f));
				}
			}
			case "radiant" -> {
				if (fighting && tickCount % 300 == 0) {
					level.sendParticles(ParticleTypes.END_ROD, getX(), getY() + getBbHeight() / 2, getZ(), 80, 2, 2, 2, 0.4);
					level.playSound(null, blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.HOSTILE, 1.5f, 1.6f);
					for (LivingEntity e : victims(level, position(), 12)) {
						e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 40, 0));
						e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 1));
						e.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0));
					}
				}
			}
			case "hollow" -> {
				if (fighting && tickCount % 400 == 200) {
					var pool = Content.MOBS.stream().filter(m -> m.world() == def.world() && !m.elite()).toList();
					if (!pool.isEmpty()) summon(level, pool.get(random.nextInt(pool.size())).id(), 2);
					level.playSound(null, blockPosition(), SoundEvents.TURTLE_EGG_HATCH, SoundSource.HOSTILE, 1.5f, 0.5f);
				}
			}
			case "frenzied" -> {
				if (!frenzied && getHealth() < getMaxHealth() * 0.5f && isAlive()) {
					frenzied = true;
					heal(getMaxHealth() * 0.05f);
					pace *= 1.3f;
					getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(getAttributeBaseValue(Attributes.MOVEMENT_SPEED) * 1.25);
					level.sendParticles(ParticleTypes.ANGRY_VILLAGER, getX(), getY() + getBbHeight(), getZ(), 12, 1, 0.5, 1, 0);
					level.playSound(null, blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 2f, 0.6f);
					triggerAnim("action", "phase");
				}
			}
			default -> {}
		}
	}

	/** What a mutation adds once an attack has landed. */
	private void mutationAfter(ServerLevel level, boolean signature) {
		switch (mutation) {
			case "searing" -> {
				for (LivingEntity e : victims(level, position(), 6)) e.igniteForSeconds(4);
				if (signature) ringOfFire(level, 5);
			}
			case "echoing" -> {
				if (signature) echoAt = tickCount + 30;
			}
			default -> {}
		}
	}

	@Override
	protected void addAdditionalSaveData(net.minecraft.world.level.storage.ValueOutput out) {
		super.addAdditionalSaveData(out);
		out.putString("mutation", mutation);
		out.putBoolean("frenzied", frenzied);
	}

	@Override
	protected void readAdditionalSaveData(net.minecraft.world.level.storage.ValueInput in) {
		super.readAdditionalSaveData(in);
		frenzied = in.getBooleanOr("frenzied", false);
		mutate(in.getStringOr("mutation", ""));
	}

	@Override
	protected void registerGoals() {
		// the Leviathan lives under water: it must not float up like a land boss caught in the sea
		Defs.BossDef d = def != null ? def : lookup(getType());
		if (d == null || !d.aquatic()) goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 24f));
		targetSelector.addGoal(1, new HurtByTargetGoal(this));
		targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, false));
	}

	/** The definition of a boss type (registerGoals runs in the super constructor, before {@link #def} is set). */
	private static Defs.BossDef lookup(EntityType<?> type) {
		String id = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(type).getPath();
		for (Defs.BossDef b : fr.achedon12.matriochka.content.Content.BOSSES) if (b.id().equals(id)) return b;
		return null;
	}

	/** The lightning a boss calls down (the Storm King, a borrowed World 4 law) strikes around it, never the boss itself. */
	@Override
	public void thunderHit(ServerLevel level, LightningBolt bolt) {
		if (!bolt.entityTags().contains(OWN_BOLT)) super.thunderHit(level, bolt);
	}

	/** The tag of the bolts a boss calls down itself (a player's lightning still strikes it). */
	private static final String OWN_BOLT = "matriochka_boss_bolt";

	/** The boss's own clouds (the Spore Queen's toxin, a borrowed World 1 law) settle around its target, not on itself. */
	@Override
	public boolean addEffect(MobEffectInstance effect, @org.jspecify.annotations.Nullable Entity source) {
		if (source instanceof AreaEffectCloud cloud && cloud.getOwner() == this) return false;
		return super.addEffect(effect, source);
	}

	@Override
	public boolean canBreatheUnderwater() {
		return (def != null && def.aquatic()) || super.canBreatheUnderwater();
	}

	@Override
	public boolean isPushedByFluid() {
		return (def == null || !def.aquatic()) && super.isPushedByFluid();
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
		// the Artisan's Shadow borrows the law of a prison, a new one every fifteen seconds
		if (def.world() == Worlds.ZERO) return 1 + (tickCount / 300) % 9;
		return def.world();
	}

	/**
	 * The world whose timing tier (telegraph and opening windows) the boss uses. Every shell of the Unfinished borrows
	 * the attacks of an older boss but keeps the final tier, the shortest: it is the last test of what was learned.
	 */
	public int timingWorld() {
		return def.world() == 10 ? 10 : world();
	}

	/** Telegraph length of the current attack, in ticks. */
	public int telegraphTicks() {
		int tele = Defs.telegraphTicks(timingWorld()) * (attack == 2 ? 2 : 1);
		return attack == 0 ? Math.max(6, tele / 2) : tele;
	}

	/** Whether the boss is announcing an attack right now, and which one (0 light, 1 medium, 2 signature). */
	public boolean telegraphing() {
		return state == State.TELEGRAPH;
	}

	public int attackIndex() {
		return attack;
	}

	/**
	 * The World Block was shaken from outside to help: the boss loses its footing, drops the attack it was announcing
	 * and stays open (taking the opening's extra damage) for a number of ticks. Not during a phase change.
	 */
	public boolean stagger(int ticks) {
		if (state == State.PHASE || !isAlive()) return false;
		attack = 1;
		state = State.OPENING;
		stateTicks = openingTicks() - ticks;
		getNavigation().stop();
		triggerAnim("action", "rest");
		return true;
	}

	public boolean opening() {
		return state == State.OPENING;
	}

	/** Opening after the current attack, in ticks. */
	public int openingTicks() {
		return Defs.openingTicks(timingWorld()) * (attack == 2 ? 1 : 2) / 2;
	}

	/**
	 * Starts one given attack (0 light, 1 medium, 2 signature) against a target right away, exactly as the fight would
	 * once it picked it: the telegraph, then the release and the opening. Used by the in-game checks (-Pmoves) to
	 * photograph every move of every boss.
	 */
	public void rehearse(int pick, LivingEntity target) {
		calmUntil = 0;
		setTarget(target);
		attack = Math.max(0, Math.min(2, pick));
		aim = target.position();
		state = State.TELEGRAPH;
		stateTicks = 0;
		getNavigation().stop();
		triggerAnim("action", ownMoves() ? move("windup") : attack == 0 ? "strike" : "charge");
	}

	/** Holds the boss still, without attacking, for a number of ticks (the Shadow before a kneeling player). */
	public void calm(int ticks) {
		calmUntil = Math.max(calmUntil, tickCount + ticks);
	}

	// ---------------------------------------------------------------- the attack state machine
	@Override
	protected void customServerAiStep(ServerLevel level) {
		// the parcel's arena burns round the fight
		if (tickCount % 10 == 0) {
			BlockPos arena = fr.achedon12.matriochka.world.Arenas.centerOf(this);
			if (arena != null) {
				fr.achedon12.matriochka.world.Arenas.ward(level, arena, def.world(), level.getGameTime());
				// nobody left in the arena (all fallen, or fled): the arch opens so they can come back, and closes
				// again behind the first one back in
				boolean inside = !level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(arena).inflate(fr.achedon12.matriochka.world.Arenas.RADIUS, 12, fr.achedon12.matriochka.world.Arenas.RADIUS),
					p -> !p.isSpectator() && p.isAlive()).isEmpty();
				int was = arenaEmpty;
				arenaEmpty = inside ? 0 : arenaEmpty + 1;
				if (arenaEmpty == 40) fr.achedon12.matriochka.world.Arenas.seal(level, arena, false);
				else if (inside && was >= 40) fr.achedon12.matriochka.world.Arenas.seal(level, arena, true);
			}
		}
		super.customServerAiStep(level);
		bar.setProgress(getHealth() / getMaxHealth());
		if (tickCount % 10 == 0) feats.watch(this, level);
		if (tickCount % 100 == 0) pace = Defs.bossAttackSpeedPlayers(fighters(level)) * (frenzied ? 1.3f : 1f);
		LivingEntity target = getTarget();
		if (!mutation.isEmpty()) mutationTick(level, target);
		// a fight inside shakes the World Block on the Surface
		if (target != null && tickCount % 20 == 0) fr.achedon12.matriochka.world.ScaleLinks.bossFighting(level, blockPosition());
		stateTicks++;
		if (awakening && tickCount >= 3) {
			awakening = false;
			triggerAnim("action", BossAnims.SLUGS.containsKey(def.id()) ? "awaken" : "phase");
		}
		if (tickCount < calmUntil) {
			getNavigation().stop();
			state = State.CHASE;
			stateTicks = 0;
			return;
		}
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
					triggerAnim("action", ownMoves() ? move("windup") : attack == 0 ? "strike" : "charge");
					level.playSound(null, blockPosition(), telegraphSound(), SoundSource.HOSTILE, 1.4f, 0.7f + 0.1f * attack);
					announce(level);
					fr.achedon12.matriochka.net.Cues.telegraph(level, this, def.id(), attack, telegraphTicks());
				}
			}
			case TELEGRAPH -> {
				int tele = telegraphTicks();
				telegraphParticles(level);
				if (stateTicks >= tele) {
					execute(level, target);
					if (!mutation.isEmpty()) mutationAfter(level, attack == 2);
					lastUse[attack] = level.getGameTime();
					state = attack == 0 ? State.CHASE : State.OPENING;
					// the boss's own release already chains its recover over the opening
					if (state == State.OPENING && !ownMoves()) triggerAnim("action", "rest");
					stateTicks = 0;
				}
			}
			case OPENING -> {
				if (stateTicks >= openingTicks()) {
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

	/** True when the boss has its own animation for every attack (tools/boss_moves.py), not only the generic set. */
	private boolean ownMoves() {
		return BossAnims.SLUGS.containsKey(def.id());
	}

	/**
	 * The trigger of the current attack's own animation: "windup" (held through the telegraph) or "release" (the
	 * strike, then the recover sized to the opening). A boss that borrows the timing of another world (the
	 * Shadow) has one cut per timing tier, picked from the world whose timing it uses right now (timingWorld).
	 */
	private String move(String part) {
		return part + attack + tierSuffix(def.id(), timingWorld());
	}

	private static String tierSuffix(String id, int world) {
		List<Integer> tiers = BossAnims.TIERS.get(id);
		if (tiers == null) return "";
		for (int w : tiers) {
			if (Defs.telegraphTicks(w) == Defs.telegraphTicks(world) && Defs.openingTicks(w) == Defs.openingTicks(world)) return ".w" + w;
		}
		return ".w" + tiers.getFirst();
	}

	/** Players taking part in the fight right now. */
	private int fighters(ServerLevel level) {
		return Math.max(1, level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(48), p -> !p.isSpectator() && p.isAlive()).size());
	}

	public float pace() {
		return pace;
	}

	private int chooseAttack(ServerLevel level, double distance) {
		long now = level.getGameTime();
		int speedUp = phase * 20;
		// more players, faster attacks: every cooldown shrinks with the pace
		boolean sig = now - lastUse[2] > (400 - speedUp) / pace;
		boolean med = now - lastUse[1] > (160 - speedUp / 2) / pace;
		boolean light = now - lastUse[0] > (80 - speedUp / 4) / pace;
		if (sig && (phase > 0 || random.nextInt(3) == 0)) return 2;
		if (med && distance > 4) return 1;
		if (light && distance <= 5) return 0;
		if (med) return 1;
		return -1;
	}

	/** The warning of the (shell) world's attacks: its own instrument and texture, generated by tools/sound.py. */
	private net.minecraft.sounds.SoundEvent telegraphSound() {
		return fr.achedon12.matriochka.content.Sounds.telegraph(def.world() == 0 ? 0 : world());
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
		BossFx.telegraph(level, def.world() == 0 ? 0 : world(), aim, r, attack == 2 ? 16 : 8);
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
		triggerAnim("action", ownMoves() ? move("release") : attack == 1 ? "cast" : "slam");
		int w = def.world() == 0 ? 0 : world();
		BossFx.attack(level, this, w, attack, aim);
		if (attack == 0) {
			for (LivingEntity e : victims(level, position().add(getLookAngle().scale(2)), 3.2)) e.hurtServer(level, damageSources().mobAttack(this), dmg(0.6f));
			level.playSound(null, blockPosition(), SoundEvents.PLAYER_ATTACK_STRONG, SoundSource.HOSTILE, 1.2f, 0.6f);
			return;
		}
		boolean sig = attack == 2;
		// heavy blows shake the camera of everyone near (client comfort settings decide how much)
		fr.achedon12.matriochka.net.Cues.impact(level, position(), sig ? 0.85f : 0.4f, sig ? 28 : 16, sig ? 14 : 8);
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
		// only the fighters: a spectator or a creative player watching the fight is not locked in
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(16), p -> !p.isSpectator() && !p.isCreative())) {
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
			bolt.addTag(OWN_BOLT);
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
		if (def.world() == Worlds.ZERO && getHealth() - amount * mult <= getMaxHealth() * 0.1f) {
			// the Artisan's Shadow cannot be finished: brought near death, it stitches itself back together
			setHealth(getMaxHealth());
			state = State.PHASE;
			stateTicks = 0;
			triggerAnim("action", "phase");
			fr.achedon12.matriochka.world.WorldZero.onStitch(level, this);
			return false;
		}
		boolean r = super.hurtServer(level, source, amount * mult);
		if (r && source.getEntity() instanceof ServerPlayer sp) feats.hit(this, level, sp);
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
			level.playSound(null, blockPosition(), fr.achedon12.matriochka.content.Sounds.BOSS_PHASE, SoundSource.HOSTILE, 2f, 1f - phase * 0.04f);
			bar.setName(barName());
			fr.achedon12.matriochka.net.Cues.phase(level, this, phase);
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
		if (ownMoves()) triggerAnim("action", "death");
		super.die(source);
		bar.removeAllPlayers();
		if (!(level() instanceof ServerLevel level)) return;
		fr.achedon12.matriochka.net.Cues.defeat(level, this, def.id());
		// a trial boss grants nothing of the story: the trial keeps its own score
		if (entityTags().contains(fr.achedon12.matriochka.replay.Trials.TAG)) {
			fr.achedon12.matriochka.replay.Trials.bossDown(this);
			return;
		}
		// the Shadow of World 0 grants nothing by dying (only by being set down, see WorldZero)
		if (def.world() == Worlds.ZERO) return;
		MatrioData data = MatrioData.get(level.getServer());
		int w = def.world();
		List<ServerPlayer> present = level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(64));
		feats.award(this, level, present);
		// everyone who fought it took part, even if they fell before the end: that is what the next world's gear asks for
		for (java.util.UUID id : feats.participants()) {
			ServerPlayer fighter = level.getServer().getPlayerList().getPlayer(id);
			if (fighter != null && !present.contains(fighter)) {
				PlayerState.of(fighter).set("boss_" + w, true);
				fr.achedon12.matriochka.world.CycleStats.bit(fighter, "bosses", w);
			}
		}
		for (ServerPlayer p : present) {
			String group = data.groupOf(p.getUUID());
			data.markDefeated(group, w);
			PlayerState ps = PlayerState.of(p);
			ps.addSouls(fr.achedon12.matriochka.gear.GearClasses.reapSouls(p, 100, p.getRandom()));
			ItemStack shards = new ItemStack(ModContent.item("shell_shard"), SHELL_SHARDS);
			if (!p.getInventory().add(shards)) spawnAtLocation(level, shards);
			ps.progress("kill", def.id(), 1);
			// doll of life: one layer after worlds 1, 5 and 8; every boss refills one layer
			int max = ps.dollMax();
			if (w == 1 || w == 5 || w == 8) max = Math.min(3, max + 1);
			ps.setDoll(ps.dollLayers() + 1, max);
			ps.set("boss_" + w, true);
			fr.achedon12.matriochka.world.CycleStats.bit(p, "bosses", w);
			if (w == 3 && !ps.has("refuge_doll_given")) {
				ps.set("refuge_doll_given", true);
				ItemStack refuge = new ItemStack(ModContent.item("refuge_doll"));
				if (!p.getInventory().add(refuge)) spawnAtLocation(level, refuge);
			}
			p.sendSystemMessage(Component.translatable("message.matriochka.boss_down." + w).withStyle(ChatFormatting.GOLD));
			if (w == 0) {
				for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
					if (p.getInventory().getItem(i).is(ModContent.item("artisan_scroll"))) p.getInventory().setItem(i, new ItemStack(ModContent.item("artisan_journal")));
				}
			}
			ps.sync();
			// the Unfinished has fallen: karma decides between sealing it and absorbing it
			if (w == 10) fr.achedon12.matriochka.world.Endings.afterUnfinished(p);
		}
		// its relics fall once it has folded back into its doll (tickDeath), where it fell
		relicsPending = true;
		relicsAt = position();
		fr.achedon12.matriochka.world.Lairs.onBossDeath(level, this);
		level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, getX(), getY() + 2, getZ(), 40, 1.5, 2, 1.5, 0.3);
		level.playSound(null, blockPosition(), fr.achedon12.matriochka.content.Sounds.BOSS_DEFEAT, SoundSource.HOSTILE, 2f, 1f);
		data.changed();
	}

	/** Half-seconds without a player in its arena (see customServerAiStep). */
	private int arenaEmpty;

	/** The relics of a story boss, held back until it has folded into its doll. */
	private boolean relicsPending;
	/** Where it fell: a flying boss drifts while it folds, its relics must not drift with it. */
	private Vec3 relicsAt;

	/**
	 * One relic, laid where the boss fell and still; over the void (a flying boss above a sky island's edge), at the
	 * feet of the nearest fighter instead.
	 */
	private void relic(ServerLevel level, ItemStack stack, List<ServerPlayer> present) {
		Vec3 at = relicsAt != null ? relicsAt : position();
		BlockPos below = BlockPos.containing(at);
		boolean ground = false;
		for (int k = 0; k < 40 && !ground; k++) ground = !level.getBlockState(below.below(k)).getCollisionShape(level, below.below(k)).isEmpty() || !level.getFluidState(below.below(k)).isEmpty();
		if (!ground && !present.isEmpty()) {
			Vec3 fell = at;
			ServerPlayer near = present.stream().min(java.util.Comparator.comparingDouble(pl -> pl.position().distanceToSqr(fell))).orElseThrow();
			at = near.position();
		}
		net.minecraft.world.entity.item.ItemEntity item = new net.minecraft.world.entity.item.ItemEntity(level, at.x, at.y + 0.5, at.z, stack);
		item.setDeltaMovement(Vec3.ZERO);
		item.setDefaultPickUpDelay();
		level.addFreshEntity(item);
	}

	/** The core, the mutated scales and the keys, dropped from a column of light where the doll closed. */
	private void dropRelics(ServerLevel level) {
		relicsPending = false;
		int w = def.world();
		List<ServerPlayer> present = level.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(64));
		relic(level, new ItemStack(ModContent.item(def.core())), present);
		// a mutated boss sheds a bonus
		if (!mutation.isEmpty()) {
			relic(level, new ItemStack(ModContent.item("mutated_scale"), 1 + random.nextInt(2)), present);
			relic(level, new ItemStack(ModContent.item("shell_shard"), 2), present);
			for (ServerPlayer p : present) p.sendSystemMessage(Component.translatable("message.matriochka.mutation.bonus").withStyle(ChatFormatting.LIGHT_PURPLE));
		}
		if (w == 0) {
			relic(level, new ItemStack(ModContent.item("matrix_workbench")), present);
			relic(level, new ItemStack(ModContent.item("world_soil_0"), 4), present);
		} else if (w == 9) {
			// only World 1 grows from soil now (world/Rites.java): the other bosses leave no World Soil
			relic(level, new ItemStack(ModContent.item("last_doll_key")), present);
		}
		double cy = getY() + getBbHeight() * 0.5;
		level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, getX(), cy, getZ(), 90, 0.6, 0.6, 0.6, 0.45);
		for (int k = 0; k < 24; k++) level.sendParticles(ParticleTypes.END_ROD, getX(), getY() + k * 0.35, getZ(), 2, 0.08, 0.1, 0.08, 0.01);
		level.playSound(null, blockPosition(), net.minecraft.sounds.SoundEvents.AMETHYST_CLUSTER_BREAK, SoundSource.HOSTILE, 2f, 0.6f);
		level.playSound(null, blockPosition(), net.minecraft.sounds.SoundEvents.BELL_RESONATE, SoundSource.HOSTILE, 1.2f, 1.2f);
	}

	/**
	 * The doll closing on a fallen boss while its death animation plays: two rings of gold, one rising from its feet
	 * and one coming down from above its head, tighten and meet at its waist, like the two halves of a matryoshka.
	 */
	private void foldIntoDoll(ServerLevel level, int last) {
		float t = Math.min(1f, deathTime / (float) last);
		double h = getBbHeight(), r = (getBbWidth() * 0.9 + 1.2) * (1 - 0.85 * t * t);
		double waist = getY() + h * 0.5, low = getY() + h * 0.5 * t, high = getY() + h * (1.25 - 0.75 * t);
		int n = 18;
		for (int k = 0; k < n; k++) {
			double a = (k + deathTime * 0.35) * Math.PI * 2 / n;
			double x = getX() + Math.cos(a) * r, z = getZ() + Math.sin(a) * r;
			level.sendParticles(fr.achedon12.matriochka.content.Particles.GOLD_MOTE, x, low, z, 1, 0, 0, 0, 0);
			level.sendParticles(fr.achedon12.matriochka.content.Particles.GOLD_MOTE, x, high, z, 1, 0, 0, 0, 0);
		}
		if (deathTime % 6 == 0) level.sendParticles(ParticleTypes.ENCHANT, getX(), waist, getZ(), 12, r * 0.5, h * 0.3, r * 0.5, 0.4);
	}

	/** Removed before its doll closed (unloaded, discarded): its relics are never lost, they fall where it was. */
	@Override
	public void remove(Entity.RemovalReason reason) {
		if (relicsPending && level() instanceof ServerLevel sl) dropRelics(sl);
		// the fight is over (fallen, or gone): the arena's arch opens again
		if (!reason.equals(Entity.RemovalReason.UNLOADED_TO_CHUNK) && !reason.equals(Entity.RemovalReason.UNLOADED_WITH_PLAYER)
			&& level() instanceof ServerLevel sl2) {
			BlockPos arena = fr.achedon12.matriochka.world.Arenas.centerOf(this);
			if (arena != null) fr.achedon12.matriochka.world.Arenas.seal(sl2, arena, false);
		}
		super.remove(reason);
	}

	/** A fallen boss stays until its death animation (misc.<boss>.death) has played out. */
	@Override
	protected void tickDeath() {
		deathTime++;
		int last = ownMoves() ? BossAnims.DEATH_TICKS : 20;
		if (level() instanceof ServerLevel sl && deathTime < last) foldIntoDoll(sl, last);
		if (deathTime >= last && !level().isClientSide() && !isRemoved()) {
			if (relicsPending && level() instanceof ServerLevel sl) dropRelics(sl);
			level().broadcastEntityEvent(this, (byte) 60);
			remove(Entity.RemovalReason.KILLED);
		}
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

	public BossFeats feats() {
		return feats;
	}

	public int phase() {
		return phase;
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(DefaultAnimations.genericWalkIdleController());
		AnimationController<MatrioBoss> action = new AnimationController<MatrioBoss>("action", 3, test -> PlayState.STOP)
			.triggerableAnim("charge", CHARGE).triggerableAnim("slam", SLAM).triggerableAnim("cast", CAST)
			.triggerableAnim("strike", STRIKE).triggerableAnim("phase", PHASE).triggerableAnim("rest", REST);
		// each boss's own attacks, phase change and fall, generated by tools/boss_moves.py
		Defs.BossDef d = def != null ? def : lookup(getType());
		List<String> slugs = d == null ? null : BossAnims.SLUGS.get(d.id());
		if (slugs != null) {
			List<Integer> tiers = BossAnims.TIERS.get(d.id());
			List<String> cuts = tiers == null ? List.of("") : tiers.stream().map(w -> ".w" + w).toList();
			for (int i = 0; i < slugs.size(); i++) {
				String base = "attack." + d.id() + "." + slugs.get(i) + ".";
				for (String cut : cuts) {
					action.triggerableAnim("windup" + i + cut, RawAnimation.begin().thenPlayAndHold(base + "windup" + cut));
					action.triggerableAnim("release" + i + cut, RawAnimation.begin().thenPlay(base + "strike" + cut).thenPlay(base + "recover" + cut));
				}
			}
			action.triggerableAnim("phase", RawAnimation.begin().thenPlay("misc." + d.id() + ".phase"));
			action.triggerableAnim("death", RawAnimation.begin().thenPlayAndHold("misc." + d.id() + ".death"));
			action.triggerableAnim("awaken", RawAnimation.begin().thenPlay("misc." + d.id() + ".awaken"));
		}
		controllers.add(action);
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}

	public static Defs.BossDef byWorld(int w) {
		for (Defs.BossDef b : Content.BOSSES) if (b.world() == w) return b;
		return Content.BOSSES.getFirst();
	}

	/** Inside the boss stage of a parcel: the arena, or the whole lair with its hall and alcove. */
	public static boolean inArena(Level level, BlockPos p) {
		if (!Worlds.isModWorld(level)) return false;
		int dz = p.getZ() - Worlds.ARENA_OFFSET;
		if (byWorld(Worlds.number(level)).lair()) return dz > -fr.achedon12.matriochka.world.Lairs.GATE - 8 && dz < fr.achedon12.matriochka.world.Lairs.R + 11;
		return Math.abs(dz) < 24;
	}

	/** Where a death chest goes for someone who died in the boss stage: just outside it, toward the Threshold. */
	public static int stageExitZ(Level level) {
		return Worlds.ARENA_OFFSET - (byWorld(Worlds.number(level)).lair() ? fr.achedon12.matriochka.world.Lairs.GATE + 4 : 22);
	}
}
