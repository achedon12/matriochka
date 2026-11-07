package fr.achedon12.matriochka.replay;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.WorldRules;
import fr.achedon12.matriochka.world.Config;
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
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.Difficulty;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Random events inside the worlds, around the players who are there (never in peaceful, never near a boss, see
 * world/Config for how often):
 * <ul>
 * <li>an invasion: a warning, then three waves of the world's creatures, the last led by an elite warlord; a reward
 * chest stands where the last one fell;</li>
 * <li>a surge: the world's rule bites twice as hard for two minutes ({@link #surge}), with its own cues;</li>
 * <li>a travelling merchant: one of the world's people with special trades, who moves on after five minutes.</li>
 * </ul>
 * One event at a time per world and parcel, then a quiet spell. A boss bar tells what is happening and how far along.
 */
public final class WorldEvents {
	public static final String INVASION = "invasion", SURGE = "surge", MERCHANT = "merchant";
	public static final String TAG = "matriochka_event", MERCHANT_TAG = "matriochka_merchant";
	private static final int RANGE = 64;

	static final class Event {
		final String kind;
		final int world, parcel;
		final ServerLevel level;
		BlockPos anchor;
		final ServerBossEvent bar;
		final Set<UUID> foes = new LinkedHashSet<>();
		int ticks, wave, waveSize, length;
		boolean live, over;
		UUID merchant;
		BlockPos chest;

		Event(String kind, ServerLevel level, BlockPos anchor) {
			this.kind = kind;
			this.level = level;
			this.anchor = anchor;
			this.world = Worlds.number(level);
			this.parcel = Worlds.parcelOf(anchor);
			BossEvent.BossBarColor color = switch (kind) {
				case INVASION -> BossEvent.BossBarColor.RED;
				case SURGE -> BossEvent.BossBarColor.PURPLE;
				default -> BossEvent.BossBarColor.YELLOW;
			};
			this.bar = new ServerBossEvent(UUID.randomUUID(), title(this), color, BossEvent.BossBarOverlay.PROGRESS);
		}

		String key() {
			return WorldEvents.key(world, parcel);
		}
	}

	private static final Map<String, Event> ACTIVE = new HashMap<>();
	private static final Map<String, Long> QUIET = new HashMap<>();

	private WorldEvents() {}

	private static String key(int world, int parcel) {
		return world + ":" + parcel;
	}

	private static Component title(Event e) {
		return switch (e.kind) {
			case INVASION -> e.live
				? Component.translatable("event.matriochka.invasion.wave", Component.translatable("world.matriochka." + e.world), e.wave, ReplayContent.INVASION_WAVES)
				: Component.translatable("event.matriochka.invasion.coming", Component.translatable("world.matriochka." + e.world));
			case SURGE -> Component.translatable(e.live ? "event.matriochka.surge.live" : "event.matriochka.surge.coming", Component.translatable("event.matriochka.surge." + e.world));
			default -> Component.translatable("event.matriochka.merchant." + e.world);
		};
	}

	// ---------------------------------------------------------------- the dice
	static void tick(MinecraftServer server) {
		long t = server.getTickCount();
		for (Event e : new ArrayList<>(ACTIVE.values())) {
			try {
				step(server, e);
			} catch (RuntimeException ex) {
				fr.achedon12.matriochka.Matriochka.LOG.error("World event {} failed", e.kind, ex);
				end(e);
			}
		}
		if (t % 1200 == 600) roll(server, t);
	}

	private static void roll(MinecraftServer server, long t) {
		strays(server);
		if (!Config.worldEvents()) return;
		Map<String, List<ServerPlayer>> byParcel = new HashMap<>();
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			int w = Worlds.number(p.level());
			if (w <= 0 || w > 10 || p.isSpectator() || p.isCreative() || !p.isAlive()) continue;
			if (p.level().getDifficulty() == Difficulty.PEACEFUL) continue;
			byParcel.computeIfAbsent(key(w, Worlds.parcelOf(p.blockPosition())), k -> new ArrayList<>()).add(p);
		}
		for (Map.Entry<String, List<ServerPlayer>> en : byParcel.entrySet()) {
			if (ACTIVE.containsKey(en.getKey()) || QUIET.getOrDefault(en.getKey(), 0L) > t) continue;
			List<ServerPlayer> ps = en.getValue();
			ServerPlayer focus = ps.get(server.overworld().getRandom().nextInt(ps.size()));
			if (!calm(focus) || server.overworld().getRandom().nextFloat() >= Config.worldEventChance()) continue;
			var v = Config.get();
			int total = Math.max(0, v.invasionWeight) + Math.max(0, v.surgeWeight) + Math.max(0, v.merchantWeight);
			if (total <= 0) continue;
			int pick = server.overworld().getRandom().nextInt(total);
			String kind = pick < Math.max(0, v.invasionWeight) ? INVASION : pick < Math.max(0, v.invasionWeight) + Math.max(0, v.surgeWeight) ? SURGE : MERCHANT;
			start(focus, kind);
		}
	}

	/** Merchants whose event is gone (the server stopped while they were there) move on. */
	private static void strays(MinecraftServer server) {
		Set<UUID> kept = new java.util.HashSet<>();
		for (Event e : ACTIVE.values()) if (e.merchant != null) kept.add(e.merchant);
		for (int w = 1; w <= 10; w++) {
			ServerLevel level = server.getLevel(Worlds.key(w));
			if (level == null || level.players().isEmpty()) continue;
			for (Entity e : level.getAllEntities()) {
				if (e instanceof MatrioNpc && e.entityTags().contains(MERCHANT_TAG) && !kept.contains(e.getUUID())) e.discard();
			}
		}
	}

	/** Nothing else is going on around this player: no boss awake, not in a boss stage. */
	private static boolean calm(ServerPlayer p) {
		if (!(p.level() instanceof ServerLevel level)) return false;
		if (MatrioBoss.inArena(level, p.blockPosition())) return false;
		return level.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(96), MatrioBoss::isAlive).isEmpty();
	}

	/** Starts an event around a player (the dice, the command and the checks). Returns false when one is already on. */
	public static boolean start(ServerPlayer focus, String kind) {
		if (!(focus.level() instanceof ServerLevel level)) return false;
		int w = Worlds.number(level);
		if (w <= 0 || w > 10) return false;
		Event e = new Event(kind, level, focus.blockPosition());
		if (ACTIVE.containsKey(e.key())) return false;
		ACTIVE.put(e.key(), e);
		switch (kind) {
			case INVASION -> {
				e.length = ReplayContent.INVASION_WARNING * 20;
				announce(e, Component.translatable("message.matriochka.event.invasion", Component.translatable("world.matriochka." + w)).withStyle(ChatFormatting.RED));
				sound(e, SoundEvents.RAID_HORN.value(), 1.2f, 0.8f);
			}
			case SURGE -> {
				e.length = ReplayContent.SURGE_WARNING * 20;
				announce(e, Component.translatable("message.matriochka.event.surge", Component.translatable("event.matriochka.surge." + w),
					Component.translatable("event.matriochka.surge." + w + ".desc")).withStyle(ChatFormatting.LIGHT_PURPLE));
				sound(e, SoundEvents.BEACON_POWER_SELECT, 1.5f, 0.5f);
			}
			default -> {
				if (!merchant(e, focus)) {
					ACTIVE.remove(e.key());
					return false;
				}
				e.live = true;
				e.length = ReplayContent.MERCHANT_STAY;
				announce(e, Component.translatable("message.matriochka.event.merchant", Component.translatable("event.matriochka.merchant." + w)).withStyle(ChatFormatting.YELLOW));
				sound(e, SoundEvents.WANDERING_TRADER_AMBIENT, 1f, 0.9f);
			}
		}
		e.bar.setName(title(e));
		return true;
	}

	private static List<ServerPlayer> near(Event e) {
		return e.level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(e.anchor).inflate(RANGE), p -> !p.isSpectator());
	}

	private static void announce(Event e, Component msg) {
		for (ServerPlayer p : near(e)) p.sendSystemMessage(msg);
	}

	private static void sound(Event e, net.minecraft.sounds.SoundEvent s, float vol, float pitch) {
		for (ServerPlayer p : near(e)) e.level.playSound(null, p.blockPosition(), s, SoundSource.AMBIENT, vol, pitch);
	}

	// ---------------------------------------------------------------- running
	private static void step(MinecraftServer server, Event e) {
		e.ticks++;
		List<ServerPlayer> near = near(e);
		if (e.ticks % 20 == 1) {
			for (ServerPlayer p : near) e.bar.addPlayer(p);
			for (ServerPlayer p : new ArrayList<>(e.bar.getPlayers())) if (!near.contains(p)) e.bar.removePlayer(p);
		}
		// everyone went away: the event fades
		if (near.isEmpty() && e.ticks > 40) {
			end(e);
			return;
		}
		switch (e.kind) {
			case INVASION -> invasion(e, near);
			case SURGE -> surgeStep(e, near);
			default -> merchantStep(e);
		}
	}

	private static void end(Event e) {
		ACTIVE.remove(e.key());
		e.bar.removeAllPlayers();
		e.over = true;
		QUIET.put(e.key(), (long) e.level.getServer().getTickCount() + Config.worldEventCooldown());
	}

	// ---------------------------------------------------------------- invasion
	private static void invasion(Event e, List<ServerPlayer> near) {
		if (!e.live) {
			e.bar.setProgress(1f - Math.min(1f, e.ticks / (float) e.length));
			if (e.ticks % 20 == 0) for (ServerPlayer p : near) e.level.sendParticles(ParticleTypes.ANGRY_VILLAGER, p.getX(), p.getY() + 2.2, p.getZ(), 1, 0.3, 0.1, 0.3, 0);
			if (e.ticks >= e.length) {
				e.live = true;
				e.ticks = 0;
				e.length = ReplayContent.INVASION_TIME * 20;
				wave(e, near);
			}
			return;
		}
		if (e.ticks % 10 != 0) return;
		e.foes.removeIf(id -> {
			Entity f = e.level.getEntity(id);
			return f == null || !f.isAlive();
		});
		e.bar.setProgress(e.waveSize == 0 ? 0 : e.foes.size() / (float) e.waveSize);
		if (e.ticks >= e.length) {
			announce(e, Component.translatable("message.matriochka.event.invasion.withdraw").withStyle(ChatFormatting.GRAY));
			for (UUID id : e.foes) {
				Entity f = e.level.getEntity(id);
				if (f != null) f.discard();
			}
			end(e);
			return;
		}
		if (!e.foes.isEmpty()) return;
		if (e.wave < ReplayContent.INVASION_WAVES) {
			wave(e, near);
			return;
		}
		e.chest = rewardChest(e, near);
		remember(e);
		announce(e, Component.translatable("message.matriochka.event.invasion.won", e.chest.getX(), e.chest.getY(), e.chest.getZ()).withStyle(ChatFormatting.GOLD));
		sound(e, SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, 1f, 1f);
		for (ServerPlayer p : near) PlayerState.of(p).addSouls(10 * e.world);
		end(e);
	}

	private static void wave(Event e, List<ServerPlayer> near) {
		e.wave++;
		boolean last = e.wave >= ReplayContent.INVASION_WAVES;
		int n = ReplayContent.INVASION_BASE + ReplayContent.INVASION_PER_PLAYER * near.size() + e.wave - 1;
		var pool = Content.MOBS.stream().filter(m -> m.world() == e.world && !m.elite() && m.aquatic() == (e.world == 7)).toList();
		var elites = Content.MOBS.stream().filter(m -> m.world() == e.world && m.elite()).toList();
		if (pool.isEmpty()) pool = Content.MOBS.stream().filter(m -> m.world() == e.world).toList();
		ServerPlayer focus = near.isEmpty() ? null : near.get(e.level.getRandom().nextInt(near.size()));
		if (focus != null) e.anchor = focus.blockPosition();
		for (int i = 0; i < n; i++) spawn(e, pool.get(e.level.getRandom().nextInt(pool.size())), focus, false);
		if (last) spawn(e, elites.isEmpty() ? pool.getLast() : elites.get(e.level.getRandom().nextInt(elites.size())), focus, true);
		e.waveSize = e.foes.size();
		e.bar.setName(title(e));
		e.bar.setProgress(1f);
		Component msg = Component.translatable(last ? "message.matriochka.event.invasion.warlord" : "message.matriochka.event.invasion.next", e.wave, ReplayContent.INVASION_WAVES);
		for (ServerPlayer p : near) p.sendOverlayMessage(msg.copy().withStyle(last ? ChatFormatting.GOLD : ChatFormatting.RED));
		sound(e, SoundEvents.RAID_HORN.value(), 0.8f, last ? 0.6f : 1f);
	}

	private static void spawn(Event e, Defs.MobDef def, ServerPlayer target, boolean warlord) {
		BlockPos at = spot(e.level, target != null ? target.blockPosition() : e.anchor, 10, 18, e.world == 7);
		if (at == null) return;
		Entity ent = ModContent.entity(def.id()).create(e.level, EntitySpawnReason.EVENT);
		if (!(ent instanceof MatrioMob mob)) return;
		mob.setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
		mob.setPersistenceRequired();
		mob.addTag(TAG);
		if (target != null) mob.setTarget(target);
		if (warlord) {
			mob.getAttribute(Attributes.MAX_HEALTH).setBaseValue(mob.getAttributeBaseValue(Attributes.MAX_HEALTH) * ReplayContent.WARLORD_HEALTH);
			mob.setHealth(mob.getMaxHealth());
			mob.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(mob.getAttributeBaseValue(Attributes.ATTACK_DAMAGE) * ReplayContent.WARLORD_DAMAGE);
			mob.setCustomName(Component.translatable("event.matriochka.warlord", Component.translatable("entity.matriochka." + def.id())).withStyle(ChatFormatting.GOLD));
			mob.setCustomNameVisible(true);
			mob.addEffect(new MobEffectInstance(MobEffects.GLOWING, 20 * 600, 0, false, false));
			mob.addTag(TAG + "_warlord");
		}
		e.level.addFreshEntity(mob);
		e.level.sendParticles(warlord ? ParticleTypes.SOUL_FIRE_FLAME : ParticleTypes.POOF, mob.getX(), mob.getY() + 0.6, mob.getZ(), 14, 0.4, 0.5, 0.4, 0.02);
		e.foes.add(mob.getUUID());
	}

	/** A free spot some distance from a place: standing room on solid ground (or open water in the Ocean). */
	static BlockPos spot(ServerLevel level, BlockPos around, int min, int max, boolean water) {
		for (int tries = 0; tries < 24; tries++) {
			double a = level.getRandom().nextDouble() * Math.PI * 2, r = min + level.getRandom().nextInt(Math.max(1, max - min));
			BlockPos at = BlockPos.containing(around.getX() + Math.cos(a) * r, around.getY(), around.getZ() + Math.sin(a) * r);
			for (int dy = 5; dy >= -8; dy--) {
				BlockPos q = at.above(dy);
				if (water) {
					if (level.getFluidState(q).isSource() && level.getFluidState(q.above()).isSource()) return q;
				} else if (level.getBlockState(q.below()).isSolid() && level.getBlockState(q).isAir() && level.getBlockState(q.above()).isAir()) {
					return q;
				}
			}
		}
		return null;
	}

	/** The spoils of a beaten invasion, in a chest on the ground near where the warlord fell. */
	private static BlockPos rewardChest(Event e, List<ServerPlayer> near) {
		BlockPos base = near.isEmpty() ? e.anchor : near.getFirst().blockPosition();
		BlockPos at = null;
		for (int r = 2; r <= 6 && at == null; r++) {
			for (int dx = -r; dx <= r && at == null; dx++)
				for (int dz = -r; dz <= r && at == null; dz++)
					for (int dy = 2; dy >= -3 && at == null; dy--) {
						BlockPos q = base.offset(dx, dy, dz);
						boolean free = e.world == 7 ? level(e).getFluidState(q).isSource() || level(e).getBlockState(q).isAir() : level(e).getBlockState(q).isAir();
						if (free && level(e).getBlockState(q.below()).isSolid()) at = q;
					}
		}
		if (at == null) at = base.above();
		e.level.setBlock(at, Blocks.CHEST.defaultBlockState(), 3);
		if (e.level.getBlockEntity(at) instanceof ChestBlockEntity chest) fill(chest, e.world, e.level.getRandom());
		e.level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 40, 0.5, 0.8, 0.5, 0.3);
		return at;
	}

	private static ServerLevel level(Event e) {
		return e.level;
	}

	/** The invasion's spoils: the world's materials, a chance of a Shell Shard and of the world's new gear. */
	static void fill(ChestBlockEntity chest, int world, net.minecraft.util.RandomSource r) {
		var common = Content.ITEMS.stream().filter(i -> i.world() == world && (i.kind().equals("resource") || i.kind().equals("consumable") || i.kind().equals("food"))).toList();
		var rare = Content.ITEMS.stream().filter(i -> i.world() == world && (i.kind().equals("gem") || i.kind().equals("ingot") || i.kind().equals("dust"))).toList();
		int slot = 0;
		for (int i = 0; i < 4 && !common.isEmpty(); i++) chest.setItem(slot++ * 2, new ItemStack(ModContent.item(common.get(r.nextInt(common.size())).id()), 3 + r.nextInt(8)));
		for (int i = 0; i < 2 && !rare.isEmpty(); i++) chest.setItem(slot++ * 2, new ItemStack(ModContent.item(rare.get(r.nextInt(rare.size())).id()), 1 + r.nextInt(3)));
		chest.setItem(slot++ * 2, new ItemStack(Items.EMERALD, 2 + r.nextInt(4 + world)));
		chest.setItem(slot++ * 2, new ItemStack(Items.EXPERIENCE_BOTTLE, 2 + r.nextInt(5)));
		if (r.nextFloat() < 0.35f) chest.setItem(slot++ * 2, new ItemStack(ModContent.item("shell_shard")));
		var gear = Content.ITEMS.stream().filter(i -> i.world() == world && ReplayContent.GEAR.contains(i.id())).toList();
		if (!gear.isEmpty() && r.nextFloat() < 0.15f) chest.setItem(13, new ItemStack(ModContent.item(gear.get(r.nextInt(gear.size())).id())));
	}

	// ---------------------------------------------------------------- surge
	/** The rule strength multiplier of a player's surroundings: SURGE_STRENGTH during a surge, 1 otherwise. */
	public static float surge(ServerPlayer p) {
		if (ACTIVE.isEmpty()) return 1f;
		int w = Worlds.number(p.level());
		Event e = ACTIVE.get(key(w, Worlds.parcelOf(p.blockPosition())));
		return e != null && e.kind.equals(SURGE) && e.live ? ReplayContent.SURGE_STRENGTH : 1f;
	}

	private static void surgeStep(Event e, List<ServerPlayer> near) {
		if (!e.live) {
			e.bar.setProgress(Math.min(1f, e.ticks / (float) e.length));
			if (e.ticks % 10 == 0) for (ServerPlayer p : near) cue(e.level, p, e.world, 4);
			if (e.ticks >= e.length) {
				e.live = true;
				e.ticks = 0;
				e.length = ReplayContent.SURGE_DURATION * 20;
				e.bar.setName(title(e));
				sound(e, SoundEvents.LIGHTNING_BOLT_THUNDER, 0.8f, 0.6f);
			}
			return;
		}
		e.bar.setProgress(1f - Math.min(1f, e.ticks / (float) e.length));
		if (e.ticks % 20 == 0) {
			for (ServerPlayer p : near) {
				int rule = e.world == 10 ? WorldRules.synthesisZone(p) : e.world;
				cue(e.level, p, rule, 14);
				bite(e.level, p, rule, e.ticks);
			}
		}
		if (e.ticks >= e.length) {
			announce(e, Component.translatable("message.matriochka.event.surge.over", Component.translatable("event.matriochka.surge." + e.world), ReplayContent.SURGE_SOULS).withStyle(ChatFormatting.GOLD));
			for (ServerPlayer p : near) PlayerState.of(p).addSouls(ReplayContent.SURGE_SOULS);
			end(e);
		}
	}

	/**
	 * The look of a surge around a player: its world's own particles (those of the world's atmosphere, ten times as
	 * thick), with a vanilla accent for the rule's danger.
	 */
	private static void cue(ServerLevel level, ServerPlayer p, int rule, int n) {
		ParticleOptions own = switch (rule) {
			case 1 -> fr.achedon12.matriochka.content.Particles.SPORE;
			case 2 -> fr.achedon12.matriochka.content.Particles.EMBER;
			case 3 -> fr.achedon12.matriochka.content.Particles.COLD_DUST;
			case 4 -> fr.achedon12.matriochka.content.Particles.STORM_SPARK;
			case 5 -> fr.achedon12.matriochka.content.Particles.SHADOW_WISP;
			case 6 -> fr.achedon12.matriochka.content.Particles.MIRROR_SHARD;
			case 7 -> fr.achedon12.matriochka.content.Particles.BUBBLE;
			case 8 -> fr.achedon12.matriochka.content.Particles.PETAL;
			case 9 -> fr.achedon12.matriochka.content.Particles.GRIT;
			default -> fr.achedon12.matriochka.content.Particles.THREAD_SCRAP;
		};
		ParticleOptions accent = switch (rule) {
			case 1 -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case 2 -> ParticleTypes.LAVA;
			case 4 -> ParticleTypes.ELECTRIC_SPARK;
			case 6 -> ParticleTypes.REVERSE_PORTAL;
			case 7 -> ParticleTypes.BUBBLE_COLUMN_UP;
			case 9 -> fr.achedon12.matriochka.content.Particles.RUST_MOTE;
			default -> null;
		};
		level.sendParticles(own, p.getX(), p.getY() + 1.5, p.getZ(), n * 2, 5, 2.5, 5, 0.01);
		if (accent != null) level.sendParticles(accent, p.getX(), p.getY() + 1.5, p.getZ(), Math.max(1, n / 4), 4, 2, 4, 0.02);
	}

	/** What a surge does to a player on top of its stronger rule, every second. */
	private static void bite(ServerLevel level, ServerPlayer p, int rule, int ticks) {
		PlayerState ps = PlayerState.of(p);
		long now = level.getGameTime();
		var r = level.getRandom();
		switch (rule) {
			case 1 -> {
				if (r.nextFloat() < 0.25f) {
					Vec3 at = p.position().add(r.nextGaussian() * 4, 0, r.nextGaussian() * 4);
					AreaEffectCloud c = new AreaEffectCloud(level, at.x, at.y, at.z);
					c.setRadius(2.5f);
					c.setDuration(100);
					c.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0));
					level.addFreshEntity(c);
				}
			}
			case 2 -> {
				if (!p.isInWater() && r.nextFloat() < 0.15f) {
					p.igniteForSeconds(2);
					level.sendParticles(ParticleTypes.FLAME, p.getX(), p.getY() + 0.2, p.getZ(), 20, 0.6, 0.1, 0.6, 0.05);
				}
			}
			case 3 -> {
				p.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 40, 0, true, false));
				if (ticks % 100 == 0) {
					p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40, 1, true, false));
					level.playSound(null, p.blockPosition(), SoundEvents.IRON_DOOR_CLOSE, SoundSource.AMBIENT, 1f, 0.5f);
				}
			}
			case 4 -> {
				if (ticks % 100 == 0 && !p.isShiftKeyDown() && level.canSeeSky(p.blockPosition().above())) {
					double a = r.nextDouble() * Math.PI * 2;
					p.push(Math.cos(a) * 0.9, 0.3, Math.sin(a) * 0.9);
					p.needsSync = true;
					level.sendParticles(ParticleTypes.GUST, p.getX(), p.getY() + 1, p.getZ(), 4, 1, 0.5, 1, 0);
					level.playSound(null, p.blockPosition(), fr.achedon12.matriochka.content.Sounds.WORLD_GUST, SoundSource.WEATHER, 1f, 0.8f);
				}
				if (r.nextFloat() < 0.15f) {
					LightningBolt bolt = fr.achedon12.matriochka.mc.McEntities.LIGHTNING_BOLT.create(level, EntitySpawnReason.TRIGGERED);
					if (bolt != null) {
						bolt.setVisualOnly(true);
						bolt.setPos(p.getX() + r.nextGaussian() * 8, p.getY(), p.getZ() + r.nextGaussian() * 8);
						level.addFreshEntity(bolt);
					}
				}
			}
			case 5 -> {
				if (ticks % 60 == 0 && !ps.flagActive("lantern", now)) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 80, 0, true, false));
			}
			case 6 -> {
				if (r.nextFloat() < 0.2f && !ps.flagActive("stable", now)) {
					p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 20, 1, true, false));
					p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 100, 0, true, false));
				}
			}
			case 7 -> {
				if (p.isInWater()) {
					double a = (now / 1200.0) % (Math.PI * 2);
					p.push(Math.cos(a) * 0.12, -0.02, Math.sin(a) * 0.12);
					p.needsSync = true;
				}
			}
			case 8 -> {
				if (!ps.flagActive("preserve", now)) {
					var eff = switch ((ticks / 20) % 3) {
						case 0 -> MobEffects.HUNGER;
						case 1 -> MobEffects.SLOWNESS;
						default -> MobEffects.WEAKNESS;
					};
					p.addEffect(new MobEffectInstance(eff, 30, 0, true, false));
				}
			}
			case 9 -> {
				if (ticks % 60 == 0 && !WorldRules.anchoredNow(level, p)) {
					p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 30, 1, true, false));
					p.push(r.nextGaussian() * 0.15, 0.25, r.nextGaussian() * 0.15);
					p.needsSync = true;
					level.playSound(null, p.blockPosition(), SoundEvents.WARDEN_HEARTBEAT, SoundSource.AMBIENT, 1.5f, 0.5f);
				}
			}
			default -> {}
		}
	}

	// ---------------------------------------------------------------- merchant
	private static boolean merchant(Event e, ServerPlayer focus) {
		Defs.NpcDef people = null;
		for (Defs.NpcDef d : Content.PEOPLES) if (d.world() == e.world) people = d;
		if (people == null) return false;
		BlockPos at = spot(e.level, focus.blockPosition(), 5, 10, e.world == 7);
		if (at == null) return false;
		Entity ent = ModContent.entity(people.id()).create(e.level, EntitySpawnReason.EVENT);
		if (!(ent instanceof MatrioNpc npc)) return false;
		npc.setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
		npc.addTag(MERCHANT_TAG);
		npc.setCustomName(Component.translatable("event.matriochka.merchant." + e.world).withStyle(ChatFormatting.GOLD));
		npc.setCustomNameVisible(true);
		npc.setPersistenceRequired();
		npc.addEffect(new MobEffectInstance(MobEffects.GLOWING, 100, 0, false, false));
		var offers = npc.getOffers();
		offers.clear();
		for (ReplayContent.Trade t : ReplayContent.MERCHANT_TRADES.get(e.world)) {
			var cost = fr.achedon12.matriochka.block.Stations.resolve(t.cost());
			var res = fr.achedon12.matriochka.block.Stations.resolve(t.result());
			offers.add(new MerchantOffer(new ItemCost(cost, t.costCount()), new ItemStack(res, t.resultCount()), 2, 5, 0.05f));
		}
		e.level.addFreshEntity(npc);
		e.level.sendParticles(ParticleTypes.HAPPY_VILLAGER, npc.getX(), npc.getY() + 1, npc.getZ(), 20, 0.5, 0.8, 0.5, 0);
		e.merchant = npc.getUUID();
		e.anchor = at;
		return true;
	}

	/** The ticks before a travelling merchant moves on, or -1 when the entity is not one. */
	public static int merchantTicksLeft(Entity npc) {
		for (Event e : ACTIVE.values()) if (npc.getUUID().equals(e.merchant)) return Math.max(0, e.length - e.ticks);
		return -1;
	}

	private static void merchantStep(Event e) {
		Entity npc = e.merchant == null ? null : e.level.getEntity(e.merchant);
		e.bar.setProgress(1f - Math.min(1f, e.ticks / (float) e.length));
		if (npc == null || !npc.isAlive()) {
			end(e);
			return;
		}
		if (e.ticks >= e.length) {
			e.level.sendParticles(ParticleTypes.POOF, npc.getX(), npc.getY() + 1, npc.getZ(), 30, 0.4, 0.8, 0.4, 0.02);
			announce(e, Component.translatable("message.matriochka.event.merchant.gone", Component.translatable("event.matriochka.merchant." + e.world)).withStyle(ChatFormatting.GRAY));
			npc.discard();
			end(e);
		}
	}

	// ---------------------------------------------------------------- server stop, test hooks
	static void stopAll() {
		for (Event e : ACTIVE.values()) e.bar.removeAllPlayers();
		ACTIVE.clear();
		QUIET.clear();
	}

	/** The event going on around a player, as its kind ("" for none). */
	public static String current(ServerPlayer p) {
		Event e = ACTIVE.get(key(Worlds.number(p.level()), Worlds.parcelOf(p.blockPosition())));
		return e == null ? "" : e.kind + (e.live ? "" : ":warning");
	}

	/** Test hook: the foes of the invasion around a player. */
	public static List<Entity> foes(ServerPlayer p) {
		List<Entity> out = new ArrayList<>();
		Event e = ACTIVE.get(key(Worlds.number(p.level()), Worlds.parcelOf(p.blockPosition())));
		if (e == null) return out;
		for (UUID id : e.foes) {
			Entity f = e.level.getEntity(id);
			if (f != null) out.add(f);
		}
		return out;
	}

	/** Test hook: brings the current phase of the event around a player to its last second. */
	public static void hurry(ServerPlayer p) {
		Event e = ACTIVE.get(key(Worlds.number(p.level()), Worlds.parcelOf(p.blockPosition())));
		if (e != null) e.ticks = Math.max(e.ticks, e.length - 20);
	}

	/** Test hook: the last reward chest placed by an invasion around this world and parcel, if any. */
	private static final Map<String, BlockPos> LAST_CHEST = new HashMap<>();

	public static BlockPos lastChest(ServerPlayer p) {
		return LAST_CHEST.get(key(Worlds.number(p.level()), Worlds.parcelOf(p.blockPosition())));
	}

	static void remember(Event e) {
		if (e.chest != null) LAST_CHEST.put(e.key(), e.chest);
	}
}
