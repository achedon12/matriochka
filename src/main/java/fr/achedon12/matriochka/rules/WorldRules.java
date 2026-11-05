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
		if (t % 20 != 0) return;
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (p.isSpectator()) continue;
			int world = Worlds.number(p.level());
			PlayerState ps = PlayerState.of(p);
			if (world > 0) {
				border(p);
				int rule = world == 10 ? synthesisZone(p) : world;
				apply(p, ps, rule, t);
				if (t % 100 == 0) StructureTracker.tick(p);
				if (p.isFallFlying() && (world == 4 || world == 6 || world == 9) && !MatrioData.get(server).defeated(p, 8)) p.stopFallFlying();
			} else {
				for (String g : new String[]{"toxin", "heat", "noise"}) if (ps.gauge(g) > 0) ps.setGauge(g, ps.gauge(g) - 5);
				if (ps.gauge("oxygen") < 100) ps.setGauge("oxygen", 100);
			}
			ps.sync();
		}
	}

	/** World 10: nine zones, each replaying the rule of worlds 1 to 9. */
	public static int synthesisZone(ServerPlayer p) {
		int zx = Math.floorMod(p.getBlockX() >> 8, 3), zz = Math.floorMod(p.getBlockZ() >> 8, 3);
		return 1 + zx + zz * 3;
	}

	private static void border(ServerPlayer p) {
		BlockPos c = Worlds.parcelCenter(MatrioData.get(p.level().getServer()).parcel(MatrioData.get(p.level().getServer()).groupOf(p.getUUID())));
		double half = Worlds.PARCEL_SIZE / 2.0;
		double dx = p.getX() - c.getX(), dz = p.getZ() - c.getZ();
		if (Math.abs(dx) > half || Math.abs(dz) > half) {
			Vec3 back = new Vec3(-Math.signum(dx) * (Math.abs(dx) > half ? 1 : 0), 0.3, -Math.signum(dz) * (Math.abs(dz) > half ? 1 : 0));
			p.setDeltaMovement(back);
			p.needsSync = true;
			p.sendOverlayMessage(Component.translatable("message.matriochka.border").withStyle(ChatFormatting.RED));
		}
	}

	private static boolean wearing(ServerPlayer p, String id) {
		for (EquipmentSlot s : EquipmentSlot.values()) if (p.getItemBySlot(s).is(ModContent.item(id))) return true;
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
		switch (rule) {
			case 1 -> {
				float gain = p.isInWaterOrRain() ? -2f : 1f;
				if (gain > 0 && wearing(p, "filter_mask")) gain *= 0.5f;
				if (gain > 0 && ps.flagActive("root_broth", t)) gain *= 0.5f;
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
				ps.addGauge("heat", gain * resist);
				float v = ps.gauge("heat");
				if (v >= 50) p.addEffect(new MobEffectInstance(MobEffects.HUNGER, 40, 1, true, false));
				if (v >= 75) p.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 40, 0, true, false));
				if (v >= 100) p.hurtServer(level, level.damageSources().onFire(), 1f);
			}
			case 3 -> {
				if (t % (20 * 300) == 20 * 290) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.halls").withStyle(ChatFormatting.AQUA));
			}
			case 4 -> {
				long phase = t % 600;
				boolean exposed = level.canSeeSky(p.blockPosition().above());
				if (phase == 560) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.gust").withStyle(ChatFormatting.AQUA));
				if (phase == 0 && exposed && !p.isShiftKeyDown()) {
					double a = (t / 600 * 1.7) % (Math.PI * 2);
					double s = 0.6 + level.getRandom().nextDouble() * 0.8;
					p.push(Math.cos(a) * s, 0.25, Math.sin(a) * s);
					p.needsSync = true;
					level.sendParticles(ParticleTypes.GUST, p.getX(), p.getY() + 1, p.getZ(), 4, 1, 0.5, 1, 0);
					level.playSound(null, p.blockPosition(), SoundEvents.BREEZE_WIND_CHARGE_BURST.value(), SoundSource.WEATHER, 0.8f, 0.6f);
				}
				if (exposed && t % 900 == 840) {
					BlockPos at = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, p.blockPosition().offset(level.getRandom().nextInt(9) - 4, 0, level.getRandom().nextInt(9) - 4));
					ps.tag().putLong("bolt", at.asLong());
					level.sendParticles(ParticleTypes.ELECTRIC_SPARK, at.getX() + 0.5, at.getY() + 0.2, at.getZ() + 0.5, 40, 0.6, 0.1, 0.6, 0.05);
					p.sendOverlayMessage(Component.translatable("message.matriochka.rule.lightning").withStyle(ChatFormatting.YELLOW));
				}
				if (t % 900 == 0 && ps.tag().contains("bolt")) {
					LightningBolt bolt = net.minecraft.world.entity.EntityTypes.LIGHTNING_BOLT.create(level, EntitySpawnReason.TRIGGERED);
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
				ps.addGauge("noise", gain * resist);
				if (ps.gauge("noise") >= 50) {
					for (MatrioMob m : level.getEntitiesOfClass(MatrioMob.class, p.getBoundingBox().inflate(28))) if (m.getTarget() == null) m.setTarget(p);
				}
				if (!ps.flagActive("lantern", t) && !p.hasEffect(MobEffects.NIGHT_VISION) && t % 200 == 0) p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 60, 0, true, false));
			}
			case 6 -> {
				long phase = t % 1800;
				if (phase == 1700) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.gravity").withStyle(ChatFormatting.LIGHT_PURPLE));
				if (phase == 0) {
					boolean safe = wearing(p, "gravity_boots") || ps.flagActive("stable", t) || ps.flagActive("flipped_apple", t);
					if (!safe) {
						p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 20 * 6, 1, true, false));
						p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 20 * 12, 0, true, false));
						Achievements.grant(p, "flipped");
						Achievements.grant(p, "fall_up");
					}
				}
			}
			case 7 -> {
				boolean under = p.isUnderWater();
				int suit = setCount(p, "diving");
				if (under) {
					float drain = suit >= 4 ? 100f / 300f : 2f;
					if (ps.flagActive("apnea", t)) drain *= 0.5f;
					ps.addGauge("oxygen", -drain);
					p.setAirSupply(p.getMaxAirSupply());
					if (ps.gauge("oxygen") <= 0) p.hurtServer(level, level.damageSources().drown(), 2f);
					int limit = suit >= 4 ? 40 : 110;
					if (p.getY() < limit) {
						p.hurtServer(level, level.damageSources().cramming(), 1.5f);
						p.sendOverlayMessage(Component.translatable("message.matriochka.rule.pressure").withStyle(ChatFormatting.DARK_AQUA));
					}
					if (p.getY() < 30) Achievements.grant(p, "deep_dive");
				} else {
					ps.addGauge("oxygen", 10);
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
			}
			case 9 -> {
				long phase = t % 1200;
				if (phase == 1140) p.sendOverlayMessage(Component.translatable("message.matriochka.rule.tremor").withStyle(ChatFormatting.GOLD));
				ps.setGauge("tremor", phase / 12f);
				if (phase == 0 && !anchored(level, p, ps, t)) {
					p.push(level.getRandom().nextGaussian() * 0.5, 0.4, level.getRandom().nextGaussian() * 0.5);
					p.needsSync = true;
					p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 100, 0, true, false));
					level.playSound(null, p.blockPosition(), SoundEvents.WARDEN_EMERGE, SoundSource.AMBIENT, 1f, 0.6f);
					for (int i = 0; i < 4; i++) {
						BlockPos q = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition().offset(level.getRandom().nextInt(13) - 6, 0, level.getRandom().nextInt(13) - 6)).below();
						var st = level.getBlockState(q);
						if (!st.isAir() && st.getDestroySpeed(level, q) >= 0 && st.getDestroySpeed(level, q) < 4 && !(st.getBlock() instanceof net.minecraft.world.level.block.EntityBlock)) {
							FallingBlockEntity.fall(level, q, st);
							Achievements.grant(p, "base_moved");
						}
					}
				}
			}
			default -> {}
		}
	}

	private static boolean anchored(ServerLevel level, ServerPlayer p, PlayerState ps, long t) {
		if (ps.flagActive("anchor", t) || wearing(p, "grip_boots")) return true;
		for (BlockPos q : BlockPos.betweenClosed(p.blockPosition().offset(-16, -6, -16), p.blockPosition().offset(16, 6, 16))) {
			if (level.getBlockState(q).is(ModContent.block("terrain_anchor"))) return true;
		}
		return false;
	}

	static boolean unused() {
		return Blocks.AIR == null;
	}
}
