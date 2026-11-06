package fr.achedon12.matriochka.showcase;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import fr.achedon12.matriochka.content.BossAnims;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.animal.golem.IronGolem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Every attack of every boss, photographed: ./gradlew runClientGameTest -Pmoves. Each boss stands alone on a flat
 * cleared floor at noon, facing an invisible target; the camera watches it from the side, far enough to frame its
 * whole body, and each of its three attacks is started on cue (MatrioBoss.rehearse) and caught twice: at the peak of
 * the windup and in the middle of the strike. Shots: moves_<boss>_<attack>_windup.png and ..._strike.png. The run
 * also checks that each boss plays its own animations (the action controller is running a move of that attack).
 */
final class MovesTest {
	private MovesTest() {}

	private static final Logger LOG = LoggerFactory.getLogger("matriochka");
	/** The floor every boss stands on. */
	private static final int FLOOR = 150;
	/** The controller blends this many ticks into every animation it starts (tools/boss_moves.py, BLEND). */
	private static final int BLEND = 3;

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.setScreen(() -> null);
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
	}

	/** Length in ticks of one animation of a boss, read from its generated animation file (0 when missing). */
	private static int length(String boss, String anim) {
		String path = "assets/matriochka/geckolib/animations/entity/" + boss + ".animation.json";
		try (InputStream in = MatrioBoss.class.getClassLoader().getResourceAsStream(path)) {
			if (in == null) return 0;
			JsonObject all = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonObject("animations");
			JsonObject a = all.getAsJsonObject(anim);
			return a == null ? 0 : Math.round(a.get("animation_length").getAsFloat() * 20);
		} catch (Exception e) {
			return 0;
		}
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			sp.getConnection().waitForChunksRender();
			ctx.setScreen(() -> null);
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule advance_weather false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule fire_spread_radius_around_player 0");
			s.runCommand("weather clear");
			s.runCommand("time set 6000");
			s.runCommand("difficulty normal");
			// a flying creative camera: no mob targets it and no blow hurts it, and unlike a spectator it does not see
			// the invisible target
			s.runCommand("gamemode creative @a");
			fly(s);
			ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
			int played = 0, missing = 0;
			int b = 0;
			for (Defs.BossDef def : Content.BOSSES) {
				List<String> slugs = BossAnims.SLUGS.get(def.id());
				if (slugs == null) continue;
				String only = System.getProperty("matriochka.bosses", "");
				if (!only.isEmpty() && !("," + only + ",").contains("," + def.id() + ",")) continue;
				final int cx = 400 + b * 160, cz = 400;
				b++;
				s.runCommand("tp @p " + cx + " " + (FLOOR + 12) + " " + (cz - 14));
				ctx.waitTicks(30);
				clear(s, cx, cz);
				ctx.waitTicks(10);
				sp.getConnection().waitForChunksRender();
				final String id = def.id();
				// the boss, facing south, and an invisible target in front of it
				double[] box = s.computeOnServer(server -> {
					ServerLevel lvl = server.overworld();
					var boss = (MatrioBoss) ModContent.entity(id).create(lvl, EntitySpawnReason.COMMAND);
					boss.snapTo(cx + 0.5, FLOOR + 1 + (def.flying() ? 1.5 : 0), cz + 0.5, 0, 0);
					boss.addTag("mv");
					boss.setPersistenceRequired();
					lvl.addFreshEntity(boss);
					decoy(lvl, cx, cz, def);
					boss.calm(100000);
					return new double[]{boss.getBbWidth(), boss.getBbHeight()};
				});
				// from the side (east of it), a little in front, the whole body in frame with room for the strike
				double h = box[1], w = box[0];
				double dist = Math.max(4.5, 1.25 * h + 0.9 * w) * (def.aquatic() ? 1.35 : 1);
				double by = FLOOR + 1 + (def.flying() ? 1.5 : 0);
				double eyeY = by + h * 0.6;
				String cam = String.format(java.util.Locale.ROOT, "tp @p %.2f %.2f %.2f facing %.2f %.2f %.2f", cx + 0.5 + dist, eyeY + h * 0.1 + 0.4,
					cz + 0.5 + dist * 0.35, cx + 0.5, eyeY, cz + 0.5 + target(def) * 0.3);
				s.runCommand(cam);
				fly(s);
				ctx.waitTicks(60); // the awakening settles
				for (int a = 0; a < slugs.size(); a++) {
					final int atk = a;
					String base = "attack." + id + "." + slugs.get(a) + ".";
					String cut = cut(id);
					int windup = length(id, base + "windup" + cut), strike = length(id, base + "strike" + cut);
					reset(s, cx, cz, def);
					s.runCommand(cam);
					ctx.waitTicks(15);
					int tele = s.computeOnServer(server -> {
						ServerLevel lvl = server.overworld();
						MatrioBoss boss = boss(lvl);
						LivingEntity decoy = decoy(lvl, cx, cz, def);
						boss.rehearse(atk, decoy);
						return boss.telegraphTicks();
					});
					// the windup holds its last pose through the telegraph: catch it once it has arrived there
					int peak = Math.max(2, Math.min(tele - 1, BLEND + windup + 1));
					ctx.waitTicks(peak);
					s.runCommand("effect clear @a");
					ctx.waitTick();
					boolean own = ctx.computeOnClient(mc -> playing(mc, base));
					if (own) played++;
					else missing++;
					LOG.info("[moves] {} {} windup: {} (telegraph {} ticks, windup {}, strike {})", id, slugs.get(a), own ? "playing" : "NOT PLAYING", tele, windup, strike);
					shot(ctx, "moves_" + id + "_" + slugs.get(a) + "_windup");
					// the release starts when the telegraph ends: wait for it, then catch the strike in its middle, where
					// the blow lands. The light attack has no opening: the boss is held still after it, or it would chain
					// its next windup over its strike.
					for (int t = 0; t < 80 && s.computeOnServer(server -> { MatrioBoss m = boss(server.overworld()); return m != null && m.telegraphing(); }); t++) ctx.waitTick();
					if (atk == 0) s.runOnServer(server -> { MatrioBoss m = boss(server.overworld()); if (m != null) m.calm(100000); });
					ctx.waitTicks(BLEND + Math.max(1, strike / 2));
					s.runCommand("effect clear @a");
					s.runCommand(cam);
					ctx.waitTick();
					String now = ctx.computeOnClient(mc -> current(mc));
					String srv = s.computeOnServer(server -> {
						MatrioBoss boss = boss(server.overworld());
						return boss == null ? "gone" : (boss.telegraphing() ? "telegraph" : boss.opening() ? "opening" : "chase") + " target=" + boss.getTarget();
					});
					LOG.info("[moves] {} {} strike shot: client plays {}, server {}", id, slugs.get(a), now, srv);
					shot(ctx, "moves_" + id + "_" + slugs.get(a) + "_strike");
					// let the recover and the opening play out before the next one
					ctx.waitTicks(70);
					s.runOnServer(server -> {
						MatrioBoss boss = boss(server.overworld());
						if (boss != null) boss.calm(100000);
					});
				}
				// removed, not killed: the fall of the Unfinished would play the Sealed ending over the next shots
				s.runOnServer(server -> {
					var all = new java.util.ArrayList<net.minecraft.world.entity.Entity>();
					for (var e : server.overworld().getAllEntities()) if (e != null && !(e instanceof net.minecraft.world.entity.player.Player)) all.add(e);
					all.forEach(net.minecraft.world.entity.Entity::discard);
				});
				ctx.waitTicks(10);
			}
			LOG.info("[moves] {} attacks played their own windup, {} did not", played, missing);
		}
	}

	/** Keeps the creative camera hanging in the air where it is put. */
	private static void fly(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s) {
		s.runOnServer(server -> {
			for (var p : server.getPlayerList().getPlayers()) {
				p.getAbilities().mayfly = true;
				p.getAbilities().flying = true;
				p.onUpdateAbilities();
			}
		});
	}

	/** How far in front of the boss its target stands: inside the reach of the light attack. */
	private static double target(Defs.BossDef def) {
		return Math.max(3.5, def.width() * 0.9 + 2);
	}

	/** The cut of a boss whose timing follows a borrowed world (the Shadow): the one of its first tier. */
	private static String cut(String id) {
		List<Integer> tiers = BossAnims.TIERS.get(id);
		return tiers == null ? "" : ".w" + tiers.getFirst();
	}

	private static MatrioBoss boss(ServerLevel lvl) {
		for (var e : lvl.getAllEntities()) if (e instanceof MatrioBoss m && m.entityTags().contains("mv")) return m;
		return null;
	}

	/** A flat floor of light stone with nothing above it. */
	private static void clear(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, int cx, int cz) {
		for (int y = FLOOR + 1; y < FLOOR + 31; y += 10) {
			s.runCommand("fill " + (cx - 22) + " " + y + " " + (cz - 22) + " " + (cx + 22) + " " + (y + 9) + " " + (cz + 22) + " minecraft:air");
		}
		s.runCommand("fill " + (cx - 22) + " " + FLOOR + " " + (cz - 22) + " " + (cx + 22) + " " + FLOOR + " " + (cz + 22) + " minecraft:smooth_stone");
		s.runCommand("fill " + (cx - 22) + " " + (FLOOR - 1) + " " + (cz - 22) + " " + (cx + 22) + " " + (FLOOR - 1) + " " + (cz + 22) + " minecraft:stone");
	}

	/** Between two attacks: the floor rebuilt, what the last one summoned gone, the boss and its target back in place. */
	private static void reset(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, int cx, int cz, Defs.BossDef def) {
		clear(s, cx, cz);
		s.runCommand("kill @e[type=!player,tag=!mv]");
		s.runOnServer(server -> {
			ServerLevel lvl = server.overworld();
			MatrioBoss boss = boss(lvl);
			if (boss == null) return;
			boss.getNavigation().stop();
			boss.setDeltaMovement(0, 0, 0);
			boss.snapTo(cx + 0.5, FLOOR + 1 + (def.flying() ? 1.5 : 0), cz + 0.5, 0, 0);
			boss.setYHeadRot(0);
			boss.setYBodyRot(0);
			IronGolem d = decoy(lvl, cx, cz, def);
			d.setDeltaMovement(0, 0, 0);
			d.snapTo(cx + 0.5, FLOOR + 1, cz + 0.5 + target(def), 180, 0);
			d.setHealth(d.getMaxHealth());
		});
	}

	/**
	 * The invisible target the boss attacks, standing in front of it (a new one if the last attack carried it off). A
	 * frozen iron golem that no blow can hurt (a villager would turn into a witch under the Storm King's lightning): an armor stand or an invulnerable entity is not an enemy a mob keeps as its
	 * target (LivingEntity.canBeSeenAsEnemy), so the boss would drop it before the release.
	 */
	private static IronGolem decoy(ServerLevel lvl, int cx, int cz, Defs.BossDef def) {
		var box = new net.minecraft.world.phys.AABB(cx - 40, FLOOR - 10, cz - 40, cx + 40, FLOOR + 40, cz + 40);
		var found = lvl.getEntitiesOfClass(IronGolem.class, box, e -> e.isAlive() && e.entityTags().contains("mv_decoy"));
		if (!found.isEmpty()) return found.getFirst();
		IronGolem decoy = net.minecraft.world.entity.EntityTypes.IRON_GOLEM.create(lvl, EntitySpawnReason.COMMAND);
		decoy.snapTo(cx + 0.5, FLOOR + 1, cz + 0.5 + target(def), 180, 0);
		decoy.setNoAi(true);
		decoy.setSilent(true);
		decoy.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, -1, 0, false, false));
		decoy.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, -1, 4, false, false));
		decoy.addTag("mv");
		decoy.addTag("mv_decoy");
		lvl.addFreshEntity(decoy);
		return decoy;
	}

	/** The animation the action controller of the boss in view is running, with its time. */
	private static String current(net.minecraft.client.Minecraft mc) {
		if (mc.level == null) return "-";
		for (var e : mc.level.entitiesForRendering()) {
			if (!(e instanceof MatrioBoss boss)) continue;
			var action = boss.getAnimatableInstanceCache().getManagerForId(boss.getId()).getAnimationControllers().get("action");
			if (action == null || action.getCurrentRawAnimation() == null) return "none";
			return action.getCurrentRawAnimation() + " @" + action.getCurrentAnimationTime();
		}
		return "-";
	}

	/** Whether the boss in view is playing one of the moves of this attack on its action controller. */
	private static boolean playing(net.minecraft.client.Minecraft mc, String base) {
		if (mc.level == null) return false;
		for (var e : mc.level.entitiesForRendering()) {
			if (!(e instanceof MatrioBoss boss)) continue;
			var controllers = boss.getAnimatableInstanceCache().getManagerForId(boss.getId()).getAnimationControllers();
			var action = controllers.get("action");
			if (action == null) continue;
			var current = action.getCurrentRawAnimation();
			if (current == null) return false;
			for (var stage : current.getAnimationStages()) if (stage.animationName().startsWith(base)) return true;
			return false;
		}
		return false;
	}
}
