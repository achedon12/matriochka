package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

/**
 * Records the takes of the action trailer (-Dmatriochka.capture=epic). For every world:
 * A a fast flyover; T a third-person fight against the world's creatures, the player driven like a real player
 * (keys held, aim turned, swings timed on the attack cooldown); K the same against the boss, strafing;
 * O a slow orbit around the boss while iron golems fight it; R the player in the foreground, seen from the front,
 * with the boss coming up behind. Frames: seq_wNN_X_0000.png at 2560 x 1440.
 */
public class EpicCapture {
	private static final String[] BOSSES = {"block_guardian", "spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater", "your_double",
		"pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished"};

	private EpicCapture() {}

	private static void frame(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(2560, 1440).disableCounterPrefix());
	}

	private static void chunks(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		try {
			McTest.waitForChunks(sp);
		} catch (AssertionError e) {
			ctx.waitTicks(40);
		}
	}

	private static void camera(ClientGameTestContext ctx, CameraType type) {
		ctx.runOnClient(mc -> mc.options.setCameraType(type));
	}

	private static void release(Minecraft mc) {
		var o = mc.options;
		for (var k : new net.minecraft.client.KeyMapping[]{o.keyUp, o.keyDown, o.keyLeft, o.keyRight, o.keySprint, o.keyJump}) k.setDown(false);
	}

	/**
	 * One frame of play, client side: turn toward the nearest target (bosses first when boss is set), run at it,
	 * swing when in reach and the attack is charged, jump when it is above or something blocks the way.
	 */
	private static void play(Minecraft mc, String boss, int f, boolean strafe) {
		var p = mc.player;
		if (p == null || mc.level == null) return;
		Entity best = null;
		double bd = 1e9;
		for (Entity e : mc.level.entitiesForRendering()) {
			if (e == p || !(e instanceof LivingEntity le) || !le.isAlive() || e instanceof Player) continue;
			String id = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getPath();
			if (boss != null && !id.equals(boss)) continue;
			if (boss == null && !net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace().equals("matriochka")) continue;
			double d = e.distanceToSqr(p);
			if (d < bd) { bd = d; best = e; }
		}
		var o = mc.options;
		if (best == null) { release(mc); return; }
		Vec3 to = best.getBoundingBox().getCenter().subtract(p.getEyePosition());
		float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
		float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
		float ny = p.getYRot() + Mth.clamp(Mth.wrapDegrees(yaw - p.getYRot()), -9f, 9f);
		float np = p.getXRot() + Mth.clamp(pitch - p.getXRot(), -5f, 5f);
		p.setYRot(ny);
		p.setYHeadRot(ny);
		p.setXRot(Mth.clamp(np, -40f, 50f));
		double dist = Math.sqrt(bd);
		double reach = boss != null ? 4.5 + best.getBbWidth() / 2 : 3.0;
		o.keyUp.setDown(dist > reach - 0.6);
		o.keySprint.setDown(dist > reach + 2);
		boolean side = strafe && dist < reach + 4;
		o.keyLeft.setDown(side && (f / 36) % 2 == 0);
		o.keyRight.setDown(side && (f / 36) % 2 == 1);
		o.keyDown.setDown(boss != null && dist < reach - 1.5);
		o.keyJump.setDown(p.horizontalCollision || to.y > 1.2 || (dist < reach + 1 && f % 23 == 0));
		if (dist < reach && p.getAttackStrengthScale(0f) > 0.92f && mc.gameMode != null) {
			// the game's own attack: aims through the crosshair, swings the arm, sends the hit
			try {
				var m = Minecraft.class.getDeclaredMethod("startAttack");
				m.setAccessible(true);
				m.invoke(mc);
			} catch (ReflectiveOperationException e) {
				mc.gameMode.attack(p, best);
			}
		}
	}

	private static void clearBadEffects(net.minecraft.server.MinecraftServer s) {
		var p = s.getPlayerList().getPlayers().get(0);
		for (var eff : new net.minecraft.core.Holder[]{net.minecraft.world.effect.MobEffects.DARKNESS, net.minecraft.world.effect.MobEffects.BLINDNESS,
			net.minecraft.world.effect.MobEffects.NAUSEA, net.minecraft.world.effect.MobEffects.LEVITATION}) {
			@SuppressWarnings("unchecked") var h = (net.minecraft.core.Holder<net.minecraft.world.effect.MobEffect>) eff;
			p.removeEffect(h);
		}
		p.setHealth(p.getMaxHealth());
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			chunks(ctx, sp);
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> {
				if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc);
				var o = mc.options;
				o.renderDistance().set(14);
				o.simulationDistance().set(10);
				o.biomeBlendRadius().set(7);
				o.entityDistanceScaling().set(2.0);
				o.bobView().set(false);
				o.cloudRange().set(128);
				o.framerateLimit().set(260);
				o.fov().set(80);
			});
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("time set 6000");
			s.runCommand("difficulty normal");
			s.runCommand("execute as @p run matriochka progression set 10");
			String only = System.getProperty("matriochka.worlds", "");
			String takes = System.getProperty("matriochka.takes", "atkor");
			for (int w = 0; w <= 10; w++) {
				if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
				final int world = w;
				String tag = String.format("w%02d", w);
				s.runCommand("gamemode creative @a");
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world enter " + w);
					ctx.setScreen(() -> null);
					ctx.waitTicks(100);
					chunks(ctx, sp);
				}
				s.runCommand("effect give @a night_vision infinite 0 true");
				s.runCommand("effect give @a resistance infinite 4 true");
				s.runCommand("effect give @a regeneration infinite 4 true");
				s.runCommand("effect give @a saturation infinite 4 true");
				if (w == 7) s.runCommand("effect give @a conduit_power infinite 0 true");
				s.runCommand("kill @e[type=marker]");
				s.runCommand("execute as @p at @s run summon marker ~ ~ ~ {Tags:[\"home\"]}");
				boolean under = w == 3 || w == 5;
				net.minecraft.core.BlockPos arena = s.computeOnServer(server -> {
					var p = server.getPlayerList().getPlayers().get(0);
					var c = p.blockPosition().offset(0, 0, 60);
					var level = (net.minecraft.server.level.ServerLevel) p.level();
					if (world == 0 || world == 3) {
						fr.achedon12.matriochka.world.Arenas.buildArena(level, world, c);
						return c;
					}
					fr.achedon12.matriochka.world.Arenas.build(level, world, c);
					return ModContent.bossForWorld(world).lair() ? fr.achedon12.matriochka.world.Lairs.heart(world, c) : c;
				});
				if (w == 2) {
					for (int qx = -1; qx <= 0; qx++) for (int qz = -1; qz <= 0; qz++) {
						int x0 = arena.getX() + qx * 30, z0 = arena.getZ() + qz * 30;
						s.runCommand("execute at @p run fill " + x0 + " " + (arena.getY() - 3) + " " + z0 + " " + (x0 + 29) + " " + (arena.getY() + 14) + " " + (z0 + 29) + " minecraft:basalt replace minecraft:lava");
					}
				}
				s.runCommand("execute at @p run summon marker " + arena.getX() + " " + arena.getY() + " " + arena.getZ() + " {Tags:[\"arena\"]}");
				Runnable rebuild = () -> {
					if (world != 3) return;
					s.runOnServer(server -> fr.achedon12.matriochka.world.Arenas.buildArena(
						(net.minecraft.server.level.ServerLevel) server.getPlayerList().getPlayers().get(0).level(), world, arena));
				};

				if (takes.contains("a")) {
					// A: a fast flyover, low over the ground (underground worlds: a dash through the hall)
					s.runCommand("gamemode spectator @a");
					camera(ctx, CameraType.FIRST_PERSON);
					if (under) s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~-14 ~5 ~-14 -45 16");
					else s.runCommand("execute at @e[tag=home,limit=1] run tp @p ~ ~" + (w == 2 ? 7 : 14) + " ~ 200 18");
					ctx.waitTicks(40);
					chunks(ctx, sp);
					for (int f = 0; f < 96; f++) {
						s.runCommand(under ? "execute as @p at @s run tp @s ^0.08 ^0.01 ^0.22 ~0.7 ~"
							: "execute as @p at @s run tp @s ^ ^-0.03 ^0.95 ~0.35 ~-0.05");
						ctx.waitTick();
						frame(ctx, String.format("seq_%s_a_%04d", tag, f));
					}
				}

				rebuild.run();
				if (takes.contains("t") && w > 0) {
					// T: third person, sword drawn, against three of the world's creatures
					s.runCommand("gamemode survival @a");
					s.runCommand("clear @a");
					s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-14 0 0");
					ctx.waitTicks(10);
					int n = 0;
					for (Defs.MobDef m : Content.MOBS) {
						if (m.world() != w || n >= 3 || m.elite() || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
						s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:" + m.id() + " ~" + (n * 5 - 5) + " ~ ~" + (2 + n));
						n++;
					}
					camera(ctx, CameraType.THIRD_PERSON_BACK);
					ctx.waitTicks(4);
					for (int f = 0; f < 140; f++) {
						int ff = f;
						ctx.runOnClient(mc -> play(mc, null, ff, false));
						if (f % 6 == 0) s.runOnServer(EpicCapture::clearBadEffects);
						ctx.waitTicks(2);
						frame(ctx, String.format("seq_%s_t_%04d", tag, f));
					}
					ctx.runOnClient(EpicCapture::release);
					s.runCommand("kill @e[type=!player,type=!marker]");
				}

				rebuild.run();
				boolean lairBoss = w > 0 && ModContent.bossForWorld(w).lair();
				Runnable wake = () -> {
					if (lairBoss) {
						s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-8 0 0");
						ctx.waitTicks(75);
						s.runCommand("execute at @e[tag=arena,limit=1] unless entity @e[type=matriochka:" + BOSSES[world] + "] run summon matriochka:" + BOSSES[world] + " ~ ~2 ~");
					} else {
						s.runCommand("execute at @e[tag=arena,limit=1] run summon matriochka:" + BOSSES[world] + " ~ ~ ~");
					}
				};
				if (takes.contains("k")) {
					// K: third person duel with the boss, circling it
					s.runCommand("gamemode survival @a");
					s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-13 0 0");
					ctx.waitTicks(10);
					wake.run();
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-12 0 0");
					camera(ctx, CameraType.THIRD_PERSON_BACK);
					for (int f = 0; f < 170; f++) {
						int ff = f;
						ctx.runOnClient(mc -> play(mc, BOSSES[world], ff, true));
						if (f % 6 == 0) s.runOnServer(EpicCapture::clearBadEffects);
						ctx.waitTicks(2);
						frame(ctx, String.format("seq_%s_k_%04d", tag, f));
					}
					ctx.runOnClient(EpicCapture::release);
				}

				if (takes.contains("o")) {
					// O: the boss against two iron golems, the camera orbiting the fight
					s.runCommand("gamemode spectator @a");
					camera(ctx, CameraType.FIRST_PERSON);
					s.runCommand("execute unless entity @e[type=matriochka:" + BOSSES[world] + "] at @e[tag=arena,limit=1] run summon matriochka:" + BOSSES[world] + " ~ ~ ~");
					s.runCommand("execute at @e[type=matriochka:" + BOSSES[world] + ",limit=1] run summon iron_golem ~4 ~ ~-3");
					s.runCommand("execute at @e[type=matriochka:" + BOSSES[world] + ",limit=1] run summon iron_golem ~-4 ~ ~3");
					ctx.waitTicks(10);
					for (int f = 0; f < 120; f++) {
						int ff = f;
						s.runOnServer(server -> {
							var p = server.getPlayerList().getPlayers().get(0);
							var lvl = (net.minecraft.server.level.ServerLevel) p.level();
							var bosses = lvl.getEntitiesOfClass(fr.achedon12.matriochka.entity.MatrioBoss.class, p.getBoundingBox().inflate(80));
							Vec3 c = bosses.isEmpty() ? Vec3.atCenterOf(arena) : bosses.get(0).getBoundingBox().getCenter();
							double r = 10 + (bosses.isEmpty() ? 0 : bosses.get(0).getBbWidth());
							double a = Math.toRadians(200 + ff * 1.1);
							Vec3 eye = c.add(Math.sin(a) * r, 2.5 + Math.sin(ff / 30.0) * 1.2, Math.cos(a) * r);
							Vec3 to = c.subtract(eye);
							float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
							float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
							p.teleportTo(lvl, eye.x, eye.y - p.getEyeHeight(), eye.z, java.util.Set.of(), yaw, pitch, false);
						});
						ctx.waitTick();
						frame(ctx, String.format("seq_%s_o_%04d", tag, f));
					}
					s.runCommand("kill @e[type=iron_golem]");
				}

				if (takes.contains("r")) {
					// R: the player in the foreground, facing the camera, the boss coming up behind
					s.runCommand("gamemode survival @a");
					s.runCommand("execute unless entity @e[type=matriochka:" + BOSSES[world] + "] at @e[tag=arena,limit=1] run summon matriochka:" + BOSSES[world] + " ~ ~ ~");
					s.runCommand("execute at @e[tag=arena,limit=1] run tp @p ~ ~ ~-11 180 -8");
					camera(ctx, CameraType.THIRD_PERSON_FRONT);
					ctx.waitTicks(6);
					for (int f = 0; f < 72; f++) {
						if (f % 6 == 0) s.runOnServer(EpicCapture::clearBadEffects);
						ctx.waitTicks(2);
						frame(ctx, String.format("seq_%s_r_%04d", tag, f));
					}
				}
				camera(ctx, CameraType.FIRST_PERSON);
				s.runCommand("kill @e[type=!player]");
				s.runCommand("gamemode creative @a");
				if (w > 0) {
					s.runCommand("execute as @p run matriochka world leave");
					ctx.waitTicks(40);
				}
			}
		}
	}
}
