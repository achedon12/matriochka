package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.Snorkel;
import fr.achedon12.matriochka.rules.WorldRules;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;

/**
 * The rule meter as a vanilla status row: ./gradlew runClientGameTest -Phud. In every world, the meter at 0, 35%,
 * 55% (a half icon) and 90% (danger) at GUI scales 2 and 3; World 7 under water with the air bubbles, with and
 * without a snorkel; full armor and absorption hearts; riding a horse; the colour-blind patterns; hidden in
 * creative and with F1; the plaque with the first-steps card and with a trial running. Screenshots hud_*. The game
 * is frozen (tick freeze) between two rule updates so the values set stay put.
 */
final class HudTest {
	private HudTest() {}

	private static final List<String> OUT = new ArrayList<>();

	private static void check(boolean ok, String what) {
		OUT.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
	}

	private static void scale(ClientGameTestContext ctx, int s) {
		ctx.runOnClient(mc -> {
			mc.options.guiScale().set(s);
			mc.resizeGui();
		});
		ctx.waitTicks(2);
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	/** Freezes the game between two once-a-second rule updates, so the meter keeps the value set. */
	private static void freeze(ClientGameTestContext ctx, TestServerContext server) {
		server.runCommand("tick unfreeze");
		for (int i = 0; i < 40 && server.computeOnServer(s -> s.overworld().getGameTime() % 20 != 10); i++) ctx.waitTick();
		server.runCommand("tick freeze");
		ctx.waitTicks(2);
	}

	/** Sets a gauge and waits for the row to settle (past the white flash of a jump). */
	private static void set(ClientGameTestContext ctx, TestServerContext server, String gauge, float v) {
		set(ctx, server, gauge, v, 25);
	}

	private static void set(ClientGameTestContext ctx, TestServerContext server, String gauge, float v, int wait) {
		server.runOnServer(s -> {
			PlayerState ps = PlayerState.of(player(s));
			ps.setGauge(gauge, v);
			ps.sync();
		});
		ctx.waitTicks(wait);
	}

	/** The meter's gauge in the world the player is in (in World 10, the zone's). */
	private static String gauge(MinecraftServer s, int world) {
		int rule = world == Worlds.ZERO ? 0 : world == 10 ? WorldRules.synthesisZone(player(s)) : world;
		return switch (rule) {
			case 0 -> "obsession"; case 1 -> "toxin"; case 2 -> "heat"; case 3 -> "shift"; case 4 -> "storm"; case 5 -> "noise";
			case 6 -> "flip"; case 7 -> "oxygen"; case 8 -> "season_turn"; default -> "tremor";
		};
	}

	/** A small pool of still water around the player, deep enough for the eyes. */
	private static void submerge(TestServerContext server) {
		server.runOnServer(s -> {
			ServerPlayer p = player(s);
			var level = p.level();
			BlockPos f = p.blockPosition();
			for (BlockPos q : BlockPos.betweenClosed(f.offset(-2, -1, -2), f.offset(2, 3, 2))) {
				boolean wall = Math.abs(q.getX() - f.getX()) == 2 || Math.abs(q.getZ() - f.getZ()) == 2 || q.getY() == f.getY() - 1;
				level.setBlockAndUpdate(q, wall ? Blocks.GLASS.defaultBlockState() : Blocks.WATER.defaultBlockState());
			}
			p.teleportTo(f.getX() + 0.5, f.getY(), f.getZ() + 0.5);
		});
	}

	private static boolean shown(ClientGameTestContext ctx) {
		return ctx.computeOnClient(mc -> !fr.achedon12.matriochka.client.MeterHud.rows(mc.player).isEmpty());
	}

	static void run(ClientGameTestContext ctx) {
		ctx.getInput().resizeWindow(1920, 1080);
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			McTest.waitForChunks(sp);
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("time set 6000");
			server.runCommand("gamemode survival @a");
			server.runCommand("effect give @a resistance infinite 4 true");
			ctx.runOnClient(mc -> {
				Comfort.get().cinematics = false;
				Comfort.changed();
			});
			ctx.setScreen(() -> null);
			ctx.waitTicks(40);
			scale(ctx, 3);
			// the plaque on the Surface (three Doll of Life layers), with the first-steps card under it and no meter
			server.runOnServer(s -> {
				PlayerState ps = PlayerState.of(player(s));
				ps.tag().putInt("doll_max", 3);
				ps.tag().putInt("doll_layers", 3);
				// past the Scroll: the card shows from the second step (find the sanctuary)
				ps.set("tut_read", true);
				ps.tag().putInt("tut_step", 1);
				ps.sync();
			});
			ctx.runOnClient(mc -> net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.send(new fr.achedon12.matriochka.net.Net.TutorialPayload("show")));
			ctx.waitTicks(80);
			String card = ctx.computeOnClient(mc -> "step " + fr.achedon12.matriochka.client.MatrioClient.state.getIntOr("tut_step", -1)
				+ ", hidden " + fr.achedon12.matriochka.client.MatrioClient.state.getBooleanOr("f_tut_hide", false));
			check(card.startsWith("step 0") || card.startsWith("step 1"), "the first-steps card is on (" + card + ")");
			shot(ctx, "hud_surface_card_s3");
			check(!shown(ctx), "no meter on the Surface");
			server.runCommand("execute as @p run matriochka progression set 10");
			ctx.waitTicks(20);

			int[] worlds = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, Worlds.ZERO};
			for (int w : worlds) {
				server.runCommand("tick unfreeze");
				if (w == Worlds.ZERO) server.runCommand("execute as @p run matriochka world zero");
				else server.runCommand("execute as @p run matriochka world enter " + w);
				ctx.setScreen(() -> null);
				ctx.waitTicks(100);
				McTest.waitForChunks(sp);
				int here = server.computeOnServer(s -> Worlds.number(player(s).level()));
				check(here == w, "the player is in world " + w + " (" + here + ")");
				freeze(ctx, server);
				String gauge = server.computeOnServer(s -> gauge(s, w));
				if (w == 8) server.runOnServer(s -> PlayerState.of(player(s)).tag().putInt("season", 0));
				boolean breath = gauge.equals("oxygen");
				float[] levels = breath ? new float[]{100, 65, 45, 10} : new float[]{0, 35, 55, 90};
				for (int k = 0; k < levels.length; k++) {
					set(ctx, server, gauge, levels[k]);
					String tag = "hud_w" + (w == Worlds.ZERO ? 0 : w) + "_" + new String[]{"0", "35", "55", "90"}[k];
					for (int s : new int[]{2, 3}) {
						scale(ctx, s);
						shot(ctx, tag + "_s" + s);
					}
				}
				check(shown(ctx), "world " + w + " shows its meter (" + gauge + ")");
				if (w == 1) extrasWorld1(ctx, server);
				if (w == 7) extrasWorld7(ctx, server);
			}
			server.runCommand("tick unfreeze");
			trial(ctx, server);
		}
		scale(ctx, 0);
		for (String line : OUT) Matriochka.LOG.info("[hud] {}", line);
		long failed = OUT.stream().filter(l -> l.startsWith("FAIL")).count();
		if (failed > 0) throw new AssertionError(failed + " hud check(s) failed: " + OUT);
	}

	private static void extrasWorld1(ClientGameTestContext ctx, TestServerContext server) {
		scale(ctx, 3);
		// full netherite and two rows of absorption hearts: the left side grows, the row stays on the right
		server.runOnServer(s -> {
			ServerPlayer p = player(s);
			p.setItemSlot(EquipmentSlot.HEAD, new ItemStack(Items.NETHERITE_HELMET));
			p.setItemSlot(EquipmentSlot.CHEST, new ItemStack(Items.NETHERITE_CHESTPLATE));
			p.setItemSlot(EquipmentSlot.LEGS, new ItemStack(Items.NETHERITE_LEGGINGS));
			p.setItemSlot(EquipmentSlot.FEET, new ItemStack(Items.NETHERITE_BOOTS));
		});
		server.runCommand("effect give @p absorption 600 3 true");
		set(ctx, server, "toxin", 55);
		shot(ctx, "hud_w1_armor_absorption_s3");
		scale(ctx, 2);
		shot(ctx, "hud_w1_armor_absorption_s2");
		scale(ctx, 3);
		// the colour-blind patterns: stripes past half, crosshatching in danger
		ctx.runOnClient(mc -> {
			Comfort.get().patterns = true;
			Comfort.changed();
		});
		shot(ctx, "hud_w1_patterns_55_s3");
		set(ctx, server, "toxin", 90);
		shot(ctx, "hud_w1_patterns_90_s3");
		ctx.runOnClient(mc -> {
			Comfort.get().patterns = false;
			Comfort.changed();
		});
		// a jump: the containers flash white like hearts taking a hit
		set(ctx, server, "toxin", 40);
		set(ctx, server, "toxin", 60, 1);
		shot(ctx, "hud_w1_jump_s3");
		// riding a horse: its hearts replace the hunger bar, the row sits above them
		server.runCommand("tick unfreeze");
		server.runCommand("execute at @p run summon minecraft:horse ~ ~ ~ {Tame:1b,NoAI:1b,Health:30f,Attributes:[{id:\"minecraft:max_health\",base:30d}]}");
		ctx.waitTicks(5);
		server.runCommand("ride @p mount @e[type=minecraft:horse,limit=1,sort=nearest]");
		ctx.waitTicks(10);
		freeze(ctx, server);
		set(ctx, server, "toxin", 35);
		shot(ctx, "hud_w1_horse_s3");
		server.runCommand("tick unfreeze");
		server.runCommand("ride @p dismount");
		server.runCommand("kill @e[type=minecraft:horse]");
		ctx.waitTicks(5);
		// hidden with F1, in creative and in spectator
		ctx.runOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc));
		shot(ctx, "hud_w1_f1_s3");
		ctx.runOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc));
		server.runCommand("gamemode creative @a");
		ctx.waitTicks(5);
		check(!shown(ctx), "no meter in creative");
		shot(ctx, "hud_w1_creative_s3");
		server.runCommand("gamemode spectator @a");
		ctx.waitTicks(5);
		check(!shown(ctx), "no meter in spectator");
		server.runCommand("gamemode survival @a");
		server.runOnServer(s -> {
			ServerPlayer p = player(s);
			for (EquipmentSlot e : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) p.setItemSlot(e, ItemStack.EMPTY);
		});
		server.runCommand("effect clear @p absorption");
		ctx.waitTicks(5);
		freeze(ctx, server);
	}

	private static void extrasWorld7(ClientGameTestContext ctx, TestServerContext server) {
		server.runCommand("tick unfreeze");
		submerge(server);
		ctx.waitTicks(10);
		freeze(ctx, server);
		// under water: the vanilla bubbles above the hunger bar, the breath row above them
		check(ctx.computeOnClient(mc -> mc.player.isEyeInFluid(net.minecraft.tags.FluidTags.WATER)), "the player's eyes are under water");
		set(ctx, server, "oxygen", 45);
		for (int s : new int[]{2, 3}) {
			scale(ctx, s);
			shot(ctx, "hud_w7_underwater_s" + s);
		}
		// a snorkel helmet: its tank on the lower row, the breath above once it runs low
		server.runOnServer(s -> {
			ItemStack h = new ItemStack(ModContent.item("salt_snorkel"));
			Snorkel.setTank(h, 60f);
			player(s).setItemSlot(EquipmentSlot.HEAD, h);
		});
		set(ctx, server, "oxygen", 100);
		shot(ctx, "hud_w7_snorkel_s3");
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.MeterHud.rows(mc.player).size()) == 1, "a full breath under the helmet shows the tank alone");
		set(ctx, server, "oxygen", 30);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.MeterHud.rows(mc.player).size()) == 2, "a short breath shows above the tank");
		for (int s : new int[]{2, 3}) {
			scale(ctx, s);
			shot(ctx, "hud_w7_snorkel_low_s" + s);
		}
		server.runOnServer(s -> player(s).setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY));
	}

	private static void trial(ClientGameTestContext ctx, TestServerContext server) {
		server.runCommand("execute as @p run matriochka world leave");
		ctx.waitTicks(40);
		String err = server.computeOnServer(s -> {
			ServerPlayer p = player(s);
			PlayerState.of(p).set("end_seal", true);
			return fr.achedon12.matriochka.replay.Trials.start(p, "w1");
		});
		check(err == null, "a trial begins (" + err + ")");
		ctx.waitTicks(140);
		scale(ctx, 3);
		shot(ctx, "hud_trial_s3");
		scale(ctx, 2);
		shot(ctx, "hud_trial_s2");
	}
}
