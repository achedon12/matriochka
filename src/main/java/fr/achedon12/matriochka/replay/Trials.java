package fr.achedon12.matriochka.replay;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.structure.TrialStage;
import fr.achedon12.matriochka.world.Endings;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Refuge;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The Trials, open to whoever has seen an ending. A trial is fought by the player and the members of their group
 * standing near them, on a stage built inside the Refuge doll (dimension matriochka:refuge, far from the rooms): a
 * world trial is two waves of the world's creatures then its boss, the Gauntlet the eleven bosses in a row. Trial
 * bosses are stronger and always mutated, and grant nothing of the story (no core, no progression). The clock runs
 * from the end of the countdown to the last kill. Falling in a trial does not kill: you are carried out of it.
 * Records: per player (PlayerState "trial_best_<key>"), per group and on a server-wide board (MatrioData "trials").
 */
public final class Trials {
	public static final String TAG = "matriochka_trial";
	/** The stages stand on this line of the Refuge dimension, one slot every SPACING blocks along x. */
	public static final int STAGE_Z = 40000, SPACING = 256, SLOTS = 64;
	private static final int COUNTDOWN = 100, BETWEEN = 60, CELEBRATE = 100, BOARD_SIZE = 10;
	private static final Map<Integer, Run> RUNS = new HashMap<>();

	enum Phase { COUNTDOWN, FIGHT, BETWEEN, DONE }

	/** One step of a trial: a wave of creatures ("wave"), a wave led by elites ("elites") or a boss ("boss"). */
	record Stage(String kind, int world) {}

	static final class Run {
		final int slot;
		final ReplayContent.TrialDef def;
		final String group;
		final List<UUID> players = new ArrayList<>();
		final Set<String> names = new LinkedHashSet<>();
		final Set<UUID> foes = new LinkedHashSet<>();
		final List<Stage> stages = new ArrayList<>();
		int stage, ticks, builtWorld = -1;
		Phase phase = Phase.COUNTDOWN;
		long start, elapsed;

		Run(int slot, ReplayContent.TrialDef def, String group) {
			this.slot = slot;
			this.def = def;
			this.group = group;
			if (def.world() == 0) {
				for (int w = 0; w <= 10; w++) stages.add(new Stage("boss", w));
			} else {
				stages.add(new Stage("wave", def.world()));
				stages.add(new Stage("elites", def.world()));
				stages.add(new Stage("boss", def.world()));
			}
		}

		BlockPos center() {
			return new BlockPos(slot * SPACING, Refuge.FLOOR_Y, STAGE_Z);
		}

		boolean gauntlet() {
			return def.world() == 0;
		}
	}

	private Trials() {}

	public static ReplayContent.TrialDef def(String key) {
		for (ReplayContent.TrialDef d : ReplayContent.TRIALS) if (d.key().equals(key)) return d;
		return null;
	}

	/** Whether the Trials are open to this player: once they have seen an ending. */
	public static boolean unlocked(ServerPlayer p) {
		return Endings.any(PlayerState.of(p));
	}

	public static boolean inTrial(ServerPlayer p) {
		return runOf(p.getUUID()) != null;
	}

	private static Run runOf(UUID id) {
		for (Run r : RUNS.values()) if (r.players.contains(id)) return r;
		return null;
	}

	/** Actions sent by the Trials screen. */
	static void action(ServerPlayer p, String action, String arg) {
		switch (action) {
			case "board" -> ReplayNet.sendBoard(p, false);
			case "start" -> {
				String err = start(p, arg);
				if (err != null) p.sendSystemMessage(Component.translatable(err).withStyle(ChatFormatting.RED));
			}
			case "title" -> wearTitle(p, arg);
			case "leave" -> leave(p);
			default -> {}
		}
	}

	// ---------------------------------------------------------------- starting
	/** Starts a trial for the player and the group members around them; returns an error key or null. */
	public static String start(ServerPlayer p, String key) {
		ReplayContent.TrialDef def = def(key);
		if (def == null) return "message.matriochka.trial.unknown";
		if (!unlocked(p)) return "message.matriochka.trial.locked";
		if (inTrial(p)) return "message.matriochka.trial.already";
		MinecraftServer server = p.level().getServer();
		ServerLevel stage = server.getLevel(Worlds.REFUGE);
		if (stage == null) return "message.matriochka.no_dimension";
		if (stage.getDifficulty() == Difficulty.PEACEFUL) return "message.matriochka.trial.peaceful";
		if (Refuge.bossNearby(p)) return "message.matriochka.refuge.boss";
		int slot = -1;
		for (int i = 0; i < SLOTS && slot < 0; i++) if (!RUNS.containsKey(i)) slot = i;
		if (slot < 0) return "message.matriochka.trial.busy";
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		Run run = new Run(slot, def, group);
		List<ServerPlayer> joining = new ArrayList<>();
		joining.add(p);
		for (UUID id : data.members(group)) {
			ServerPlayer m = server.getPlayerList().getPlayer(id);
			if (m == null || m == p || m.isSpectator() || !m.isAlive() || m.level() != p.level() || m.distanceTo(p) > 24 || inTrial(m)) continue;
			joining.add(m);
		}
		RUNS.put(slot, run);
		BlockPos c = run.center();
		forceChunks(stage, c, true);
		build(stage, run, run.stages.getFirst().world());
		BlockPos entry = TrialStage.entry(c);
		int i = 0;
		for (ServerPlayer m : joining) {
			PlayerState ps = PlayerState.of(m);
			CompoundTag ret = new CompoundTag();
			ret.putString("dim", m.level().dimension().identifier().toString());
			ret.putDouble("x", m.getX());
			ret.putDouble("y", m.getY());
			ret.putDouble("z", m.getZ());
			ret.putFloat("yaw", m.getYRot());
			ps.tag().put("trial_return", ret);
			run.players.add(m.getUUID());
			run.names.add(m.getGameProfile().name());
			Vec3 at = Vec3.atBottomCenterOf(entry.offset((i % 3 - 1) * 2, 0, -(i / 3)));
			m.teleport(new TeleportTransition(stage, at, Vec3.ZERO, 0f, 0f, Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
			m.setHealth(m.getMaxHealth());
			m.clearFire();
			i++;
		}
		for (ServerPlayer m : players(server, run)) {
			m.sendSystemMessage(Component.translatable("message.matriochka.trial.begin", Component.translatable("trial.matriochka." + def.key()), run.stages.size()).withStyle(ChatFormatting.GOLD));
		}
		hud(server, run);
		return null;
	}

	private static void forceChunks(ServerLevel level, BlockPos c, boolean on) {
		BoundingBox b = TrialStage.box(c);
		for (int cx = b.minX() >> 4; cx <= b.maxX() >> 4; cx++)
			for (int cz = b.minZ() >> 4; cz <= b.maxZ() >> 4; cz++) level.setChunkForced(cx, cz, on);
	}

	private static void build(ServerLevel level, Run run, int world) {
		if (run.builtWorld == world) return;
		clearFoes(level, run, true);
		TrialStage.build(level, run.center(), world);
		// wiping the previous stage pops its carpets, banners and lanterns: they are not loot
		for (Entity e : level.getEntitiesOfClass(ItemEntity.class, AABB.of(TrialStage.box(run.center())).inflate(4))) e.discard();
		run.builtWorld = world;
	}

	private static List<ServerPlayer> players(MinecraftServer server, Run run) {
		List<ServerPlayer> out = new ArrayList<>();
		for (UUID id : run.players) {
			ServerPlayer m = server.getPlayerList().getPlayer(id);
			if (m != null) out.add(m);
		}
		return out;
	}

	// ---------------------------------------------------------------- the clock
	static void tick(MinecraftServer server) {
		if (RUNS.isEmpty()) return;
		ServerLevel level = server.getLevel(Worlds.REFUGE);
		if (level == null) return;
		for (Run run : new ArrayList<>(RUNS.values())) {
			try {
				step(server, level, run);
			} catch (RuntimeException e) {
				fr.achedon12.matriochka.Matriochka.LOG.error("Trial {} failed", run.def.key(), e);
				close(server, level, run);
			}
		}
	}

	private static void step(MinecraftServer server, ServerLevel level, Run run) {
		run.ticks++;
		BlockPos c = run.center();
		// whoever left the stage (another dimension, logged out, carried out) is out of the trial
		run.players.removeIf(id -> {
			ServerPlayer m = server.getPlayerList().getPlayer(id);
			return m == null || m.level() != level || m.position().distanceTo(Vec3.atCenterOf(c)) > TrialStage.R + 12;
		});
		if (run.players.isEmpty() && run.phase != Phase.DONE) {
			close(server, level, run);
			return;
		}
		if (run.phase != Phase.COUNTDOWN && run.phase != Phase.DONE) run.elapsed = server.getTickCount() - run.start;
		Stage stage = run.stages.get(Math.min(run.stage, run.stages.size() - 1));
		if (run.ticks % 20 == 0) {
			for (ServerPlayer m : players(server, run)) {
				// the Leviathan's stage is flooded: the trial lends you gills
				if (stage.world() == 7) m.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 60, 0, true, false));
			}
			hud(server, run);
		}
		switch (run.phase) {
			case COUNTDOWN -> {
				if (run.ticks % 20 == 0 && run.ticks < COUNTDOWN) {
					int left = (COUNTDOWN - run.ticks) / 20;
					// the clock plaque draws the count large in the middle of the screen (ReplayHud): sent right away
					for (ServerPlayer m : players(server, run)) {
						level.playSound(null, m.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.PLAYERS, 1f, 0.8f + 0.1f * (5 - left));
						PlayerState.of(m).sync();
					}
				}
				if (run.ticks >= COUNTDOWN) {
					run.start = server.getTickCount();
					run.phase = Phase.FIGHT;
					run.ticks = 0;
					spawn(server, level, run);
				}
			}
			case FIGHT -> {
				if (run.ticks % 10 != 0 || alive(level, run) > 0) return;
				run.stage++;
				run.ticks = 0;
				clearFoes(level, run, false);
				if (run.stage >= run.stages.size()) {
					finish(server, level, run);
					return;
				}
				run.phase = Phase.BETWEEN;
				for (ServerPlayer m : players(server, run)) {
					m.sendOverlayMessage(Component.translatable("message.matriochka.trial.cleared", run.stage, run.stages.size()).withStyle(ChatFormatting.GREEN));
					level.playSound(null, m.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.8f, 1.2f);
				}
			}
			case BETWEEN -> {
				if (run.ticks < BETWEEN) return;
				Stage next = run.stages.get(run.stage);
				if (next.world() != run.builtWorld) {
					build(level, run, next.world());
					BlockPos entry = TrialStage.entry(c);
					for (ServerPlayer m : players(server, run)) m.teleportTo(level, entry.getX() + 0.5, entry.getY(), entry.getZ() + 0.5, Set.of(), 0f, 0f, true);
				}
				run.phase = Phase.FIGHT;
				run.ticks = 0;
				spawn(server, level, run);
			}
			case DONE -> {
				if (run.ticks >= CELEBRATE) close(server, level, run);
			}
		}
	}

	/** Foes of the stage still standing. */
	private static int alive(ServerLevel level, Run run) {
		run.foes.removeIf(id -> {
			Entity e = level.getEntity(id);
			return e == null || !e.isAlive() || e.isRemoved();
		});
		return run.foes.size();
	}

	private static void spawn(MinecraftServer server, ServerLevel level, Run run) {
		Stage s = run.stages.get(run.stage);
		BlockPos c = run.center();
		BlockPos dais = TrialStage.dais(c);
		List<ServerPlayer> ps = players(server, run);
		ServerPlayer target = ps.isEmpty() ? null : ps.getFirst();
		Component name;
		if (s.kind().equals("boss")) {
			Defs.BossDef def = MatrioBoss.byWorld(s.world());
			// no introduction cinematic: the trial clock is running
			MatrioBoss boss = MatrioBoss.summon(level, def.id(), dais, target, false);
			if (boss == null) return;
			float h = run.gauntlet() ? ReplayContent.GAUNTLET_HEALTH : ReplayContent.TRIAL_HEALTH;
			float d = run.gauntlet() ? ReplayContent.GAUNTLET_DAMAGE : ReplayContent.TRIAL_DAMAGE;
			boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(boss.getAttributeBaseValue(Attributes.MAX_HEALTH) * h);
			boss.setHealth(boss.getMaxHealth());
			boss.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(boss.getAttributeBaseValue(Attributes.ATTACK_DAMAGE) * d);
			String mutation = ReplayContent.TRIAL_MUTATION[Math.max(0, Math.min(10, s.world()))];
			boss.mutate(mutation);
			tag(run, boss);
			name = Component.translatable("entity.matriochka." + def.id());
			Component desc = Component.translatable("mutation.matriochka." + mutation + ".desc");
			for (ServerPlayer m : ps) m.sendSystemMessage(Component.translatable("message.matriochka.mutation.woke", desc).withStyle(ChatFormatting.LIGHT_PURPLE));
		} else {
			boolean elites = s.kind().equals("elites");
			int n = ReplayContent.TRIAL_WAVE + ps.size();
			var pool = Content.MOBS.stream().filter(m -> m.world() == s.world() && !m.elite()).toList();
			var elitePool = Content.MOBS.stream().filter(m -> m.world() == s.world() && m.elite()).toList();
			List<Defs.MobDef> wave = new ArrayList<>();
			if (elites) {
				for (int i = 0; i < ReplayContent.TRIAL_ELITES + ps.size() / 2 && !elitePool.isEmpty(); i++) wave.add(elitePool.get(level.getRandom().nextInt(elitePool.size())));
				n = Math.max(2, n / 2);
			}
			for (int i = 0; i < n && !pool.isEmpty(); i++) wave.add(pool.get(level.getRandom().nextInt(pool.size())));
			for (int i = 0; i < wave.size(); i++) {
				Entity e = ModContent.entity(wave.get(i).id()).create(level, EntitySpawnReason.EVENT);
				if (e == null) continue;
				double a = i * Math.PI * 2 / wave.size();
				double r = 3 + (i % 3) * 2;
				e.setPos(dais.getX() + 0.5 + Math.cos(a) * r, dais.getY() - 1, dais.getZ() + 0.5 + Math.sin(a) * r);
				if (e instanceof MatrioMob mob) {
					mob.setPersistenceRequired();
					if (target != null) mob.setTarget(target);
				}
				tag(run, e);
				level.addFreshEntity(e);
				level.sendParticles(ParticleTypes.POOF, e.getX(), e.getY() + 0.5, e.getZ(), 10, 0.3, 0.4, 0.3, 0.02);
			}
			name = Component.translatable(elites ? "message.matriochka.trial.wave_elites" : "message.matriochka.trial.wave", Component.translatable("world.matriochka." + s.world()));
		}
		for (ServerPlayer m : ps) {
			m.sendOverlayMessage(Component.translatable("message.matriochka.trial.stage", run.stage + 1, run.stages.size(), name).withStyle(ChatFormatting.GOLD));
			level.playSound(null, m.blockPosition(), SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 0.6f, 1.2f);
		}
	}

	private static void tag(Run run, Entity e) {
		// every foe glows, so a Mimic in disguise or a buried Root Creeper can always be found
		if (e instanceof net.minecraft.world.entity.LivingEntity le) le.addEffect(new MobEffectInstance(MobEffects.GLOWING, 20 * 1800, 0, false, false));
		e.addTag(TAG);
		e.addTag(TAG + "_" + run.slot);
		run.foes.add(e.getUUID());
	}

	/** Removes what is left of a stage: its foes and their minions, and once the trial is over, the loot on the floor. */
	private static void clearFoes(ServerLevel level, Run run, boolean everything) {
		AABB box = AABB.of(TrialStage.box(run.center())).inflate(8);
		for (Entity e : level.getEntitiesOfClass(Entity.class, box, e -> e instanceof MatrioMob || e instanceof MatrioBoss
			|| e.entityTags().contains(TAG) || (everything && (e instanceof ItemEntity || e instanceof ExperienceOrb)))) {
			if (!(e instanceof ServerPlayer)) e.discard();
		}
		if (everything) run.foes.clear();
	}

	/** A trial boss fell (called by MatrioBoss instead of the story's rewards). */
	public static void bossDown(MatrioBoss boss) {
		if (boss.level() instanceof ServerLevel level) {
			level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, boss.getX(), boss.getY() + 2, boss.getZ(), 80, 1.5, 2, 1.5, 0.5);
			level.playSound(null, boss.blockPosition(), fr.achedon12.matriochka.content.Sounds.BOSS_DEFEAT, SoundSource.HOSTILE, 2f, 1.1f);
		}
	}

	// ---------------------------------------------------------------- the end
	private static void finish(MinecraftServer server, ServerLevel level, Run run) {
		run.phase = Phase.DONE;
		run.ticks = 0;
		long ticks = run.elapsed;
		int rank = record(server, run, ticks);
		boolean swift = ticks <= run.def.par() * 20L;
		Component time = Component.literal(clock(ticks));
		for (ServerPlayer m : players(server, run)) {
			PlayerState ps = PlayerState.of(m);
			String best = "trial_best_" + run.def.key();
			boolean personal = ps.tag().getIntOr(best, 0) == 0 || ticks < ps.tag().getIntOr(best, 0);
			if (personal) ps.tag().putInt(best, (int) ticks);
			ps.addCounter("trial_clears_" + run.def.key(), 1);
			ps.addSouls(ReplayContent.TRIAL_SOULS * Math.max(1, run.gauntlet() ? 12 : run.def.world()));
			m.sendSystemMessage(Component.translatable("message.matriochka.trial.done", Component.translatable("trial.matriochka." + run.def.key()), time).withStyle(ChatFormatting.GOLD));
			if (personal) m.sendSystemMessage(Component.translatable("message.matriochka.trial.personal").withStyle(ChatFormatting.YELLOW));
			if (rank > 0) m.sendSystemMessage(Component.translatable("message.matriochka.trial.rank", rank).withStyle(ChatFormatting.YELLOW));
			if (!ps.has("trial_done_" + run.def.key())) {
				ps.set("trial_done_" + run.def.key(), true);
				String trophy = run.gauntlet() ? "trophy_doll_gauntlet" : "trophy_doll_" + run.def.world();
				ItemStack doll = new ItemStack(ModContent.item(trophy));
				if (!m.getInventory().add(doll)) m.spawnAtLocation(level, doll);
				grantTitle(m, run.def.title());
			}
			if (swift) grantTitle(m, ReplayContent.SWIFT_TITLE);
			level.sendParticles(ParticleTypes.FIREWORK, m.getX(), m.getY() + 2, m.getZ(), 40, 1, 1, 1, 0.2);
			level.playSound(null, m.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
			ps.sync();
		}
		hud(server, run);
	}

	/** Writes the time to the group's best and to the server board; returns the group's rank on the board (0 if off it). */
	static int record(MinecraftServer server, Run run, long ticks) {
		MatrioData data = MatrioData.get(server);
		String key = run.def.key();
		CompoundTag best = data.group(run.group).getCompoundOrEmpty("trial_best");
		if (best.getIntOr(key, 0) == 0 || ticks < best.getIntOr(key, 0)) {
			best.putInt(key, (int) ticks);
			best.putString(key + "_names", String.join(", ", run.names));
		}
		data.group(run.group).put("trial_best", best);
		CompoundTag trials = data.root().getCompoundOrEmpty("trials");
		ListTag top = trials.getListOrEmpty(key);
		List<CompoundTag> rows = new ArrayList<>();
		boolean placed = false;
		for (Tag t : top) {
			if (!(t instanceof CompoundTag row)) continue;
			if (row.getStringOr("group", "").equals(run.group)) {
				// one line per group: its best run
				if (ticks < row.getIntOr("ticks", Integer.MAX_VALUE)) continue;
				placed = true;
			}
			rows.add(row);
		}
		if (!placed) {
			CompoundTag row = new CompoundTag();
			row.putString("group", run.group);
			row.putString("names", String.join(", ", run.names));
			row.putInt("ticks", (int) ticks);
			row.putInt("players", run.names.size());
			row.putLong("day", server.overworld().getGameTime() / 24000L);
			rows.add(row);
		}
		rows.sort((a, b) -> Integer.compare(a.getIntOr("ticks", 0), b.getIntOr("ticks", 0)));
		ListTag out = new ListTag();
		int rank = 0;
		for (int i = 0; i < rows.size() && i < BOARD_SIZE; i++) {
			out.add(rows.get(i));
			if (rows.get(i).getStringOr("group", "").equals(run.group)) rank = i + 1;
		}
		trials.put(key, out);
		data.root().put("trials", trials);
		data.changed();
		return rank;
	}

	/** Back home: every player of the trial returns where they stood, the stage is emptied and released. */
	private static void close(MinecraftServer server, ServerLevel level, Run run) {
		RUNS.remove(run.slot);
		for (ServerPlayer m : players(server, run)) sendHome(m);
		clearFoes(level, run, true);
		forceChunks(level, run.center(), false);
	}

	/** Carries a player out of the Trials to where they stood before. */
	public static void sendHome(ServerPlayer m) {
		MinecraftServer server = m.level().getServer();
		PlayerState ps = PlayerState.of(m);
		CompoundTag ret = ps.tag().getCompoundOrEmpty("trial_return");
		ps.tag().remove("trial_return");
		ps.tag().remove("trial");
		ServerLevel target = null;
		Vec3 at = null;
		float yaw = m.getYRot();
		if (ret.contains("dim")) {
			target = server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(ret.getStringOr("dim", "minecraft:overworld"))));
			at = new Vec3(ret.getDoubleOr("x", 0), ret.getDoubleOr("y", 64), ret.getDoubleOr("z", 0));
			yaw = ret.getFloatOr("yaw", yaw);
		}
		if (target == null) {
			target = server.overworld();
			at = Vec3.atBottomCenterOf(Travel.findSafe(target, target.getRespawnData().pos()));
		}
		m.teleport(new TeleportTransition(target, at, Vec3.ZERO, yaw, m.getXRot(), Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		ps.sync();
	}

	/** Leaving on purpose (the screen's button or the command). */
	public static void leave(ServerPlayer p) {
		Run run = runOf(p.getUUID());
		if (run == null) return;
		run.players.remove(p.getUUID());
		sendHome(p);
		p.sendSystemMessage(Component.translatable("message.matriochka.trial.left").withStyle(ChatFormatting.GRAY));
	}

	/** A blow that would kill a player in a trial carries them out instead. Returns false when it did. */
	static boolean allowDeath(ServerPlayer p) {
		Run run = runOf(p.getUUID());
		if (run == null) return true;
		p.setHealth(p.getMaxHealth());
		p.clearFire();
		p.removeAllEffects();
		run.players.remove(p.getUUID());
		sendHome(p);
		p.sendSystemMessage(Component.translatable("message.matriochka.trial.fallen").withStyle(ChatFormatting.RED));
		return false;
	}

	/** Back from a trial that ended while the player was away (a server stop). */
	static void onJoin(ServerPlayer p) {
		if (PlayerState.of(p).tag().contains("trial_return") && !inTrial(p)) sendHome(p);
	}

	/**
	 * Every run ends with the server: its stage is emptied and its chunks released (the players are sent home when they
	 * next join, see {@link #onJoin}).
	 */
	static void stopAll(MinecraftServer server) {
		ServerLevel level = server.getLevel(Worlds.REFUGE);
		if (level != null) {
			for (Run run : RUNS.values()) {
				clearFoes(level, run, true);
				forceChunks(level, run.center(), false);
			}
		}
		RUNS.clear();
	}

	// ---------------------------------------------------------------- HUD, titles, board
	/** The trial's state as the HUD reads it from the synced player state. */
	private static void hud(MinecraftServer server, Run run) {
		for (ServerPlayer m : players(server, run)) {
			CompoundTag t = new CompoundTag();
			t.putString("key", run.def.key());
			t.putInt("stage", Math.min(run.stage + 1, run.stages.size()));
			t.putInt("stages", run.stages.size());
			t.putLong("elapsed", run.phase == Phase.COUNTDOWN ? 0 : run.elapsed);
			t.putString("phase", run.phase.name().toLowerCase(java.util.Locale.ROOT));
			if (run.phase == Phase.COUNTDOWN) t.putInt("left", Math.max(1, (COUNTDOWN - run.ticks + 19) / 20));
			t.putInt("par", run.def.par());
			t.putInt("best", PlayerState.of(m).tag().getIntOr("trial_best_" + run.def.key(), 0));
			PlayerState.of(m).tag().put("trial", t);
		}
	}

	public static String clock(long ticks) {
		long cs = ticks * 5;
		return String.format(java.util.Locale.ROOT, "%d:%02d.%02d", cs / 6000, (cs / 100) % 60, cs % 100);
	}

	public static void grantTitle(ServerPlayer p, String id) {
		PlayerState ps = PlayerState.of(p);
		if (ps.has("title_" + id)) return;
		ps.set("title_" + id, true);
		if (ps.tag().getStringOr("title", "").isEmpty()) ps.tag().putString("title", id);
		p.sendSystemMessage(Component.translatable("message.matriochka.trial.title", Component.translatable("title.matriochka." + id)).withStyle(ChatFormatting.LIGHT_PURPLE));
	}

	/** Titles a player owns: from the trials, and from the quests that reward one. */
	public static boolean owns(PlayerState ps, String id) {
		if (ps.has("title_" + id)) return true;
		for (Defs.QuestDef q : Content.QUESTS) if (q.rewardKind().equals("title") && q.rewardTarget().equals(id) && ps.has("quest_" + q.id())) return true;
		return false;
	}

	static void wearTitle(ServerPlayer p, String id) {
		PlayerState ps = PlayerState.of(p);
		if (!id.isEmpty() && !owns(ps, id)) return;
		ps.tag().putString("title", id);
		ps.sync();
	}

	/** What the Trials screen shows: every board, the group's and the player's best times. */
	static CompoundTag board(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		CompoundTag out = new CompoundTag();
		CompoundTag trials = data.root().getCompoundOrEmpty("trials");
		CompoundTag group = data.group(data.groupOf(p.getUUID())).getCompoundOrEmpty("trial_best");
		for (ReplayContent.TrialDef d : ReplayContent.TRIALS) {
			CompoundTag t = new CompoundTag();
			t.put("top", trials.getListOrEmpty(d.key()).copy());
			t.putInt("group", group.getIntOr(d.key(), 0));
			t.putInt("mine", PlayerState.of(p).tag().getIntOr("trial_best_" + d.key(), 0));
			out.put(d.key(), t);
		}
		out.putBoolean("unlocked", unlocked(p));
		return out;
	}

	/** The board of one trial, as chat lines (the command). */
	public static List<Component> top(MinecraftServer server, String key) {
		List<Component> out = new ArrayList<>();
		ListTag top = MatrioData.get(server).root().getCompoundOrEmpty("trials").getListOrEmpty(key);
		int i = 1;
		for (Tag t : top) {
			if (!(t instanceof CompoundTag row)) continue;
			out.add(Component.translatable("command.matriochka.trial.row", i++, clock(row.getIntOr("ticks", 0)), row.getStringOr("names", "?")));
		}
		return out;
	}

	static int running() {
		return RUNS.size();
	}

	/** Test hook: the foes of the player's current stage. */
	public static List<Entity> foes(ServerPlayer p) {
		Run run = runOf(p.getUUID());
		List<Entity> out = new ArrayList<>();
		if (run == null || !(p.level() instanceof ServerLevel level)) return out;
		for (UUID id : run.foes) {
			Entity e = level.getEntity(id);
			if (e != null) out.add(e);
		}
		return out;
	}
}
