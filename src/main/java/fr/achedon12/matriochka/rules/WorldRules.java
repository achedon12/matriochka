package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.structure.StructureTracker;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Worlds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.item.FallingBlockEntity;
import net.minecraft.world.item.ItemStack;
import fr.achedon12.matriochka.world.Ocean;
import fr.achedon12.matriochka.world.ScaleLinks;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/** The unique rule of each world, evaluated once per second per player. */
public final class WorldRules {
	private WorldRules() {}

	public static void serverTick(MinecraftServer server) {
		long t = server.overworld().getGameTime();
		// World 8: hastened time (day and night in 8 minutes) on its own clock
		ServerLevel w8 = server.getLevel(Worlds.key(8));
		if (w8 != null) HastenedClock.tick(w8);
		MovingWorlds.tick(server, t);
		if (t % 20 != 0) return;
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (p.isSpectator()) continue;
			int world = Worlds.number(p.level());
			PlayerState ps = PlayerState.of(p);
			// the Journal's map: the ground walked through and the structures found, every three seconds
			if (t % 60 == 0) fr.achedon12.matriochka.world.Atlas.sample(p);
			if (world > 0) {
				border(p);
				int rule = world == 10 ? synthesisZone(p) : world;
				// the client draws the meter of the rule you live under: in World 10, your zone's
				if (world == 10) ps.tag().putInt("zone", rule);
				else ps.tag().remove("zone");
				apply(p, ps, rule, t);
				if (t % 100 == 0) {
					StructureTracker.tick(p);
					fr.achedon12.matriochka.world.BaseModel.tick(p);
				}
				if (p.isFallFlying() && (world == 4 || world == 6 || world == 9) && !MatrioData.get(server).defeated(p, 8)) p.stopFallFlying();
			} else {
				for (String g : new String[]{"toxin", "heat", "noise"}) if (ps.gauge(g) > 0) ps.setGauge(g, ps.gauge(g) - 5);
				if (ps.gauge("oxygen") < 100) ps.setGauge("oxygen", 100);
			}
			ps.sync();
		}
	}

	/** The rule a player lives under: their world's, or in World 10 the one of their zone (0 on the Surface). */
	public static int rule(ServerPlayer p) {
		int world = Worlds.number(p.level());
		return world == 10 ? synthesisZone(p) : world;
	}

	/** World 10: nine zones, each replaying the rule of worlds 1 to 9. */
	public static int synthesisZone(ServerPlayer p) {
		int zx = Math.floorMod(p.getBlockX() >> 8, 3), zz = Math.floorMod(p.getBlockZ() >> 8, 3);
		return 1 + zx + zz * 3;
	}

	private static void border(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		BlockPos c = Worlds.parcelCenter(data.parcel(data.groupOf(p.getUUID()), Worlds.number(p.level())));
		double half = Worlds.PARCEL_SIZE / 2.0;
		double dx = p.getX() - c.getX(), dz = p.getZ() - c.getZ();
		if (Math.abs(dx) > half || Math.abs(dz) > half) {
			Vec3 back = new Vec3(-Math.signum(dx) * (Math.abs(dx) > half ? 1 : 0), 0.3, -Math.signum(dz) * (Math.abs(dz) > half ? 1 : 0));
			p.setDeltaMovement(back);
			p.needsSync = true;
			p.sendOverlayMessage(Component.translatable("message.matriochka.border").withStyle(ChatFormatting.RED));
		}
	}

	static boolean wearing(ServerPlayer p, String id) {
		// a set may not have every piece (the Diving set has no helmet: the head slot is the snorkel's)
		var item = ModContent.itemOrNull(id);
		if (item == null) return false;
		for (EquipmentSlot s : EquipmentSlot.values()) if (p.getItemBySlot(s).is(item)) return true;
		return false;
	}

	private static int setCount(ServerPlayer p, String set) {
		int n = 0;
		for (String piece : new String[]{"helmet", "chestplate", "leggings", "boots"}) {
			if (wearing(p, set + "_" + piece)) n++;
		}
		return n;
	}

	private static void apply(ServerPlayer p, PlayerState ps, int rule, long t) {
		ServerLevel level = (ServerLevel) p.level();
		float resist = 1f - GearClasses.survivorResistance(p);
		// the world's variant makes its rule gentler or harsher
		float strength = fr.achedon12.matriochka.world.Variants.of(p).rule() * fr.achedon12.matriochka.replay.WorldEvents.surge(p);
		switch (rule) {
			case 1 -> {
				float gain = p.isInWaterOrRain() ? -2f : 1f;
				if (gain > 0 && wearing(p, "filter_mask")) gain *= 0.5f;
				if (gain > 0 && ps.flagActive("root_broth", t)) gain *= 0.5f;
				// water around the World Block soaks the jungle
				if (gain > 0 && ScaleLinks.active(p, "damp")) gain *= 0.5f;
				if (gain > 0) gain *= strength;
				ps.addGauge("toxin", gain * resist);
				float v = ps.gauge("toxin");
				if (v >= 50) p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40, 0, true, false));
				if (v >= 75) p.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 40, 0, true, false));
				if (v >= 100) p.hurtServer(level, level.damageSources().magic(), 1f);
				if (level.getRandom().nextInt(3) == 0) level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, p.getX(), p.getY() + 2, p.getZ(), 6, 3, 1, 3, 0);
			}
			case 2 -> {
				float gain = -2f;
				if (!p.isInWater()) {
					gain = p.getY() < 40 ? 0.5f : 0f;
					for (BlockPos q : BlockPos.betweenClosed(p.blockPosition().offset(-3, -2, -3), p.blockPosition().offset(3, 2, 3))) {
						if (level.getFluidState(q).is(net.minecraft.tags.FluidTags.LAVA)) { gain = 1f; break; }
					}
					if (gain <= 0 && p.getY() >= 40) gain = -1f;
				}
				if (gain > 0) gain *= 1f - 0.125f * setCount(p, "thermal");
				if (gain > 0 && ps.flagActive("ice_bread", t)) gain *= 0.5f;
				// ice around the World Block cools the veins
				if (gain > 0 && ScaleLinks.active(p, "cool")) gain *= 0.5f;
				if (gain > 0) gain *= strength;
				ps.addGauge("heat", gain * resist);
				float v = ps.gauge("heat");
				if (v >= 50) p.addEffect(new MobEffectInstance(MobEffects.HUNGER, 40, 1, true, false));
				if (v >= 75) p.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 40, 0, true, false));
				if (v >= 100) p.hurtServer(level, level.damageSources().onFire(), 1f);
			}
			case 3 -> {
				// the halls only physically move in World 3 itself; the synthesis zone keeps the warning
				long phase = t % DungeonShift.PERIOD;
				// the hourglass meter: how far along the halls are toward their next move
				ps.setGauge("shift", phase * 100f / DungeonShift.PERIOD);
				boolean halls = Worlds.number(level) == 3;
				if (phase == DungeonShift.PERIOD - DungeonShift.WARN) {
					p.sendOverlayMessage(Component.translatable("message.matriochka.rule.halls").withStyle(ChatFormatting.AQUA));
					if (halls) DungeonShift.plan(level, p);
				}
				if (halls && phase > DungeonShift.PERIOD - DungeonShift.WARN) DungeonShift.rumble(level, p);
				if (halls && phase == 0) DungeonShift.shift(level, p);
			}
			case 4 -> {
				long phase = t % 600;
				// the storm meter charges up to the next gust
				ps.setGauge("storm", phase / 6f);
				boolean exposed = level.canSeeSky(p.blockPosition().above());
				if (phase == 560) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.gust").withStyle(ChatFormatting.AQUA));
				if (phase == 0 && exposed && !p.isShiftKeyDown()) {
					double a = (t / 600 * 1.7) % (Math.PI * 2);
					double s = (0.6 + level.getRandom().nextDouble() * 0.8) * strength;
					// a storm over the World Block strengthens the gusts inside
					if (ScaleLinks.active(p, "storm")) s *= 1.5;
					p.push(Math.cos(a) * s, 0.25, Math.sin(a) * s);
					p.needsSync = true;
					level.sendParticles(ParticleTypes.GUST, p.getX(), p.getY() + 1, p.getZ(), 4, 1, 0.5, 1, 0);
					level.playSound(null, p.blockPosition(), fr.achedon12.matriochka.content.Sounds.WORLD_GUST, SoundSource.WEATHER, 1f, 0.9f + level.getRandom().nextFloat() * 0.2f);
				}
				if (exposed && t % 900 == 840) {
					BlockPos at = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, p.blockPosition().offset(level.getRandom().nextInt(9) - 4, 0, level.getRandom().nextInt(9) - 4));
					ps.tag().putLong("bolt", at.asLong());
					level.sendParticles(ParticleTypes.ELECTRIC_SPARK, at.getX() + 0.5, at.getY() + 0.2, at.getZ() + 0.5, 40, 0.6, 0.1, 0.6, 0.05);
					p.sendOverlayMessage(Component.translatable("message.matriochka.rule.lightning").withStyle(ChatFormatting.YELLOW));
				}
				if (t % 900 == 0 && ps.tag().contains("bolt")) {
					LightningBolt bolt = fr.achedon12.matriochka.mc.McEntities.LIGHTNING_BOLT.create(level, EntitySpawnReason.TRIGGERED);
					if (bolt != null) {
						bolt.setPos(Vec3.atBottomCenterOf(BlockPos.of(ps.tag().getLongOr("bolt", 0))));
						level.addFreshEntity(bolt);
					}
					ps.tag().remove("bolt");
				}
			}
			case 5 -> {
				float gain = p.isSprinting() ? 4f : (p.isShiftKeyDown() ? -3f : (p.getDeltaMovement().horizontalDistanceSqr() > 0.001 ? 0.6f : -1.5f));
				if (ps.flagActive("mute", t)) gain = Math.min(gain, 0);
				if (gain > 0) gain *= strength;
				ps.addGauge("noise", gain * resist);
				if (ps.gauge("noise") >= 50) {
					for (MatrioMob m : level.getEntitiesOfClass(MatrioMob.class, p.getBoundingBox().inflate(28))) if (m.getTarget() == null) m.setTarget(p);
				}
				Burnout.scan(level, p, level.getGameTime());
				// the dark itself presses on whoever stands in it
				boolean dark = level.getBrightness(net.minecraft.world.level.LightLayer.BLOCK, p.blockPosition()) < 4;
				if (dark && !ps.flagActive("lantern", t) && !p.hasEffect(MobEffects.NIGHT_VISION) && t % 200 == 0) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, true, false));
			}
			case 6 -> {
				// gravity columns, their warning and their sparks run every tick in GravityZones; the feather meter
				// shows how far along the columns are toward turning over
				ps.setGauge("flip", (t % GravityZones.PERIOD) * 100f / GravityZones.PERIOD);
			}
			case 7 -> {
				// Oxygen: the gauge is your breath. Under water it runs out in about half a minute, unless a snorkel
				// helmet feeds you from its tank; the helmet refills in air, in bubble columns and over air vents.
				ItemStack helmet = Snorkel.worn(p);
				float mult = (ps.flagActive("apnea", t) ? 0.5f : 1f) * resist * strength;
				if (p.isUnderWater()) {
					if (Snorkel.atAirSource(level, p)) {
						if (!helmet.isEmpty()) Snorkel.refill(helmet, Snorkel.VENT_RATE);
						ps.addGauge("oxygen", 5);
						level.sendParticles(ParticleTypes.BUBBLE, p.getX(), p.getY() + 1, p.getZ(), 6, 0.3, 0.6, 0.3, 0.05);
					}
					if (Snorkel.breathe(p, ps, helmet, mult, t)) {
						Achievements.grant(p, "snorkel");
					} else {
						ps.addGauge("oxygen", -Snorkel.HOLD_DRAIN * mult);
					}
					p.setAirSupply(p.getMaxAirSupply());
					if (ps.gauge("oxygen") <= 0) p.hurtServer(level, level.damageSources().drown(), 2f);
					// pressure: each diving piece and the helmet's tier let you go deeper
					int limit = Ocean.PRESSURE_Y - Ocean.PER_DIVING_PIECE * setCount(p, "diving") - Snorkel.depthBonus(helmet);
					// dry ground around the World Block eases the pressure
					if (ScaleLinks.active(p, "dry")) limit -= 16;
					if (p.getY() < limit) {
						p.hurtServer(level, level.damageSources().cramming(), 1.5f);
						p.sendOverlayMessage(Component.translatable("message.matriochka.rule.pressure").withStyle(ChatFormatting.DARK_AQUA));
					}
					if (p.getY() < 30) Achievements.grant(p, "deep_dive");
				} else {
					// a breath of real air: an air pocket, a grotto, a habitat, the chamber or the surface
					ps.addGauge("oxygen", 10);
					if (!helmet.isEmpty()) Snorkel.refill(helmet, Snorkel.AIR_RATE);
				}
			}
			case 8 -> {
				int season = HastenedClock.season(level);
				ps.tag().putInt("season", season);
				int seen = ps.tag().getIntOr("seasons_seen", 0) | (1 << season);
				ps.tag().putInt("seasons_seen", seen);
				if (seen == 15) Achievements.grant(p, "four_seasons");
				if (!ps.flagActive("preserve", t)) {
					switch (season) {
						case 1 -> p.addEffect(new MobEffectInstance(MobEffects.HUNGER, 40, 0, true, false));
						case 3 -> p.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40, 0, true, false));
						default -> {}
					}
				}
				ps.setGauge("season", season * 33.3f);
				// the leaf meter: how far the current season has turned (a season lasts 2400 ticks)
				ps.setGauge("season_turn", (level.getGameTime() % 2400) / 24f);
			}
			case 9 -> {
				long phase = t % ShiftingGround.PERIOD;
				if (phase == ShiftingGround.PERIOD - ShiftingGround.WARN) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.tremor").withStyle(ChatFormatting.GOLD));
				if (phase >= ShiftingGround.PERIOD - ShiftingGround.WARN) ShiftingGround.rumble(level, p);
				ps.setGauge("tremor", phase / (ShiftingGround.PERIOD / 100f));
				if (phase == 0) {
					if (anchored(level, p, ps, t)) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.ground_held").withStyle(ChatFormatting.GOLD));
					ShiftingGround.heave(level, p);
				}
			}
			default -> {}
		}
	}

	/** Whether the ground under this player is held still right now (anchor, grip boots or a Terrain Anchor nearby). */
	public static boolean anchoredNow(ServerLevel level, ServerPlayer p) {
		return anchored(level, p, PlayerState.of(p), level.getGameTime());
	}

	private static boolean anchored(ServerLevel level, ServerPlayer p, PlayerState ps, long t) {
		if (ps.flagActive("anchor", t) || wearing(p, "grip_boots")) return true;
		// Terrain Anchors around the World Block hold the ground
		if (ScaleLinks.active(p, "calm")) return true;
		for (BlockPos q : BlockPos.betweenClosed(p.blockPosition().offset(-16, -6, -16), p.blockPosition().offset(16, 6, 16))) {
			if (level.getBlockState(q).is(ModContent.block("terrain_anchor"))) return true;
		}
		return false;
	}

	static boolean unused() {
		return Blocks.AIR == null;
	}
}
