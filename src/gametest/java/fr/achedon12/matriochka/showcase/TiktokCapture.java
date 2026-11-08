package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.EndingScreen;
import fr.achedon12.matriochka.client.StallScreen;
import fr.achedon12.matriochka.client.Ui;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.replay.Trials;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.CycleStats;
import fr.achedon12.matriochka.world.Endings;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.CameraType;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Util;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

import static fr.achedon12.matriochka.showcase.Film.*;

/**
 * Vertical takes for short videos (-Dmatriochka.capture=tiktok, ./gradlew runClientGameTest -Ptiktok): the window is
 * 1080 x 1920 and every frame is one game tick, with the mod's interface clock (Ui.frameClock) stepped 50 ms per tick
 * so screen animations play at game speed whatever a screenshot costs. Takes (-Ptakes=..., all when empty):
 * p a first-person Seed planted, hatching into a World Block and entered; s the same seen from an orbiting camera;
 * m the market stall (the Peddler, then the black market), with the cursor's path written to tk_cursor.txt;
 * l three Doll of Life layers breaking under the Ash Titan; t the Gauntlet's countdown and first stage;
 * then for each world (-Pworlds=...): v an orbit of the arena with its boss and creatures, i the boss's introduction,
 * b its signature attacks, f a third-person fight with the HUD; g World 10 at doll height; d World 5 without night
 * vision; and last r the cycle recap opening. Frames: tk_<take>[_wNN]_0000.png.
 */
final class TiktokCapture {
	private TiktokCapture() {}

	private static String TAKES = "";

	private static boolean take(char c) {
		return TAKES.isEmpty() || TAKES.indexOf(c) >= 0;
	}

	// ---------------------------------------------------------------- run
	static void run(ClientGameTestContext ctx) {
		TAKES = System.getProperty("matriochka.takes", "");
		Film.begin("tk", 1080, 1920);
		Ui.frameClock = Util.getMillis();
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(W, H);
			step(ctx, 5);
			chunks(ctx, sp);
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> {
				var o = mc.options;
				o.renderDistance().set(14);
				o.simulationDistance().set(10);
				o.biomeBlendRadius().set(7);
				o.entityDistanceScaling().set(2.0);
				o.bobView().set(false);
				o.cloudRange().set(128);
				o.framerateLimit().set(260);
				o.fov().set(75);
				o.guiScale().set(3);
				// the chat stays hidden: command feedback, game mode changes and the test player's name never show
				o.chatVisibility().set(net.minecraft.world.entity.player.ChatVisiblity.HIDDEN);
				fr.achedon12.matriochka.client.mc.McClient.clearChat(mc);
				mc.resizeGui();
			});
			int[] win = ctx.computeOnClient(mc -> new int[]{mc.getWindow().getWidth(), mc.getWindow().getHeight(), mc.getWindow().getGuiScaledWidth()});
			Matriochka.LOG.info("[tiktok] window {}x{}, gui width {}", win[0], win[1], win[2]);
			hud(ctx, false);
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule advance_weather false");
			s.runCommand("weather clear");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("gamerule show_death_messages false");
			s.runCommand("gamerule send_command_feedback false");
			s.runCommand("gamerule log_admin_commands false");
			s.runCommand("gamerule fire_spread_radius_around_player 0");
			s.runCommand("time set 11200");
			s.runCommand("difficulty normal");
			s.runCommand("gamemode survival @a");
			s.runCommand("execute as @p run matriochka progression set 1");
			step(ctx, 40);
			s.runCommand("tick freeze");
			SERVER = s;
			BlockPos garden = null;
			if (take('p') || take('s')) garden = garden(ctx, sp);
			if (take('p')) seedPov(ctx, sp, garden, "p");
			if (take('s')) seedOrbit(ctx, sp, garden, "s");
			s.runCommand("execute as @p run matriochka progression set 10");
			s.runOnServer(srv -> {
				PlayerState ps = PlayerState.of(player(srv));
				ps.set("end_seal", true);
				ps.addSouls(3000);
				ps.sync();
			});
			s.runCommand("time set 6000");
			step(ctx, 20);
			if (take('m')) stall(ctx, sp);
			if (take('l')) layers(ctx, sp);
			if (take('t')) trial(ctx, sp);
			worlds(ctx, sp);
			if (take('r')) recap(ctx, sp);
			try {
				Files.writeString(Path.of("screenshots", "tk_cursor.txt"), CURSOR.toString());
			} catch (IOException e) {
				Matriochka.LOG.warn("[tiktok] cursor log: {}", e.toString());
			}
			SERVER = null;
			s.runCommand("tick unfreeze");
		}
		Ui.frameClock = -1;
	}

	// ---------------------------------------------------------------- the stall
	private static int npcId = -1;

	private static void summonNpc(MinecraftServer srv, String id) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		for (Entity e : level.getEntities((Entity) null, p.getBoundingBox().inflate(24), e -> e instanceof MatrioNpc)) e.discard();
		Entity e = ModContent.entity(id).create(level, EntitySpawnReason.COMMAND);
		if (!(e instanceof MatrioNpc npc)) return;
		npc.snapTo(p.getX(), p.getY(), p.getZ() + 2.6, 180f, 0f);
		npc.setYHeadRot(180f);
		npc.setNoAi(true);
		level.addFreshEntity(npc);
		npcId = npc.getId();
	}

	private static void karma(MinecraftServer srv, int k) {
		PlayerState ps = PlayerState.of(player(srv));
		ps.tag().putInt("karma", k);
		ps.sync();
	}


	private static void stall(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @p");
		s.runCommand("give @p minecraft:emerald 64");
		s.runCommand("give @p minecraft:gold_ingot 12");
		s.runCommand("execute as @p at @s run tp @s ~ ~ ~ 0 8");
		s.runOnServer(srv -> {
			summonNpc(srv, "doll_peddler");
			karma(srv, 40);
		});
		camera(ctx, CameraType.FIRST_PERSON);
		step(ctx, 20);
		chunks(ctx, sp);
		int i = 0;
		cur = new double[]{W * 0.62, H * 0.62};
		ctx.getInput().setCursorPos(cur[0], cur[1]);
		i = still(ctx, "m", i, 12);
		s.runOnServer(srv -> ((MatrioNpc) player(srv).level().getEntity(npcId)).mobInteract(player(srv), InteractionHand.MAIN_HAND));
		i = still(ctx, "m", i, 30);
		if (!ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen)) {
			Matriochka.LOG.warn("[tiktok] the stall did not open");
			return;
		}
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(1)), 14);
		i = still(ctx, "m", i, 16);
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(0)), 10);
		i = still(ctx, "m", i, 6);
		i = clickAt(ctx, "m", i);
		i = still(ctx, "m", i, 18);
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).slotCenter(2)), 12);
		i = still(ctx, "m", i, 6);
		ctx.getInput().holdKey(com.mojang.blaze3d.platform.InputConstants.KEY_LSHIFT);
		i = clickAt(ctx, "m", i);
		ctx.getInput().releaseKey(com.mojang.blaze3d.platform.InputConstants.KEY_LSHIFT);
		i = still(ctx, "m", i, 26);
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		step(ctx, 8);
		// the black market: karma -40 at a world's people
		s.runOnServer(srv -> {
			summonNpc(srv, "prisoner");
			karma(srv, -40);
		});
		s.runCommand("give @p matriochka:sealed_fragment 20");
		step(ctx, 6);
		i = still(ctx, "m", i, 6);
		s.runOnServer(srv -> ((MatrioNpc) player(srv).level().getEntity(npcId)).mobInteract(player(srv), InteractionHand.MAIN_HAND));
		i = still(ctx, "m", i, 28);
		if (ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen)) {
			int n = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu().getOffers().size());
			i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(n - 1)), 16);
			i = still(ctx, "m", i, 30);
		}
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		step(ctx, 8);
		s.runOnServer(srv -> {
			karma(srv, 0);
			for (Entity e : player(srv).level().getEntities((Entity) null, player(srv).getBoundingBox().inflate(24), e -> e instanceof MatrioNpc)) e.discard();
		});
		s.runCommand("clear @p");
	}



	/** L: World 2, the Ash Titan's hammer; three times a blow that should kill breaks a layer of the Doll of Life. */
	private static void layers(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		enter(ctx, sp, 2);
		buffs(s, 2, true);
		BlockPos a = arena(s, 2);
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
		s.runOnServer(srv -> {
			PlayerState ps = PlayerState.of(player(srv));
			ps.setDoll(3, 3);
			ps.sync();
			player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 10, Set.of(), 180f, -12f, false);
		});
		step(ctx, 20);
		s.runOnServer(srv -> {
			MatrioBoss b = MatrioBoss.summon((ServerLevel) player(srv).level(), "ash_titan", a, player(srv), false);
			if (b != null) {
				b.snapTo(a.getX() + 0.5, a.getY(), a.getZ() + 0.5, 180f, 0f);
				b.calm(100000);
			}
		});
		step(ctx, 50);
		hudScale(ctx, 2f);
		hud(ctx, true);
		camera(ctx, CameraType.THIRD_PERSON_FRONT);
		int i = 0;
		i = roll(ctx, "l", i, 12);
		for (int hit = 0; hit < 3; hit++) {
			s.runOnServer(srv -> {
				MatrioBoss b = boss(srv, "ash_titan");
				if (b != null) b.rehearse(0, player(srv));
			});
			// through the telegraph, then the blow lands
			for (int k = 0; k < 90 && s.computeOnServer(srv -> { MatrioBoss b = boss(srv, "ash_titan"); return b != null && b.telegraphing(); }); k++) {
				step(ctx, 1);
				frame(ctx, f("l", i++));
			}
			i = roll(ctx, "l", i, 5);
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				PlayerState.of(p).tag().putLong("last_revive", -100000);
				p.removeEffect(MobEffects.RESISTANCE);
				p.hurtServer((ServerLevel) p.level(), p.damageSources().generic(), 1000f);
				p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, -1, 4, false, false));
				MatrioBoss b = boss(srv, "ash_titan");
				if (b != null) b.calm(100000);
			});
			i = roll(ctx, "l", i, 40);
		}
		hud(ctx, false);
		hudScale(ctx, 1f);
		s.runOnServer(srv -> {
			PlayerState ps = PlayerState.of(player(srv));
			ps.setDoll(3, 3);
			ps.sync();
		});
		leave(ctx, sp);
	}

	// ---------------------------------------------------------------- the Gauntlet
	private static void trial(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runCommand("effect give @a resistance infinite 4 true");
		s.runCommand("effect give @a regeneration infinite 4 true");
		s.runOnServer(srv -> player(srv).getInventory().setItem(0, new ItemStack(ModContent.item("magma_flail"))));
		s.runOnServer(srv -> player(srv).getInventory().setSelectedSlot(0));
		hudScale(ctx, 1.5f);
		s.runOnServer(srv -> Trials.start(player(srv), "gauntlet"));
		ctx.setScreen(() -> null);
		hud(ctx, true);
		camera(ctx, CameraType.THIRD_PERSON_BACK);
		int i = 0;
		for (int k = 0; k < 300; k++) {
			int ff = k;
			if (k > 110) ctx.runOnClient(mc -> EpicPlay.play(mc, null, ff, true));
			if (k % 6 == 0) s.runOnServer(Film::clearBad);
			step(ctx, 1);
			frame(ctx, f("t", i++));
		}
		ctx.runOnClient(EpicPlay::release);
		hud(ctx, false);
		hudScale(ctx, 1f);
		camera(ctx, CameraType.FIRST_PERSON);
		s.runOnServer(srv -> Trials.leave(player(srv)));
		step(ctx, 60);
		chunks(ctx, sp);
	}

	// ---------------------------------------------------------------- the worlds
	private static void worlds(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		boolean any = false;
		for (char c : "vibfgd".toCharArray()) any |= take(c);
		if (!any) return;
		var s = sp.getServer();
		String only = System.getProperty("matriochka.worlds", "");
		for (int w = 0; w <= 10; w++) {
			if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
			if (w > 0) enter(ctx, sp, w);
			s.runCommand("gamemode creative @a");
			s.runCommand("effect clear @a");
			buffs(s, w, w != 5);
			BlockPos a = arena(s, w);
			// -Pfull=...: the worlds that also get the boss's introduction and attacks (all when empty)
			String fullList = System.getProperty("matriochka.full", "");
			boolean full = fullList.isEmpty() || ("," + fullList + ",").contains("," + w + ",");

			if (take('g') && w == 10) giant(ctx, sp);
			if (take('d') && w == 5) dark(ctx, sp, a);
			if (w == 5) buffs(s, 5, true);

			if (take('i') || take('b') || take('v')) bossIntro(ctx, sp, w, a, take('i') && full);
			if (take('v')) orbit(ctx, sp, w, a);
			if (take('b') && full) attacks(ctx, sp, w, a);
			if (take('f') && w > 0) fight(ctx, sp, w, a);
			if (w > 0) leave(ctx, sp);
			else {
				camera(ctx, CameraType.FIRST_PERSON);
				s.runCommand("kill @e[type=!player]");
				s.runCommand("effect clear @a");
			}
		}
	}

	/** G: World 10 from a doll's height: the camera skims the workshop floor and tilts up at the giant tools. */
	private static void giant(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("gamemode spectator @a");
		camera(ctx, CameraType.FIRST_PERSON);
		Vec3 start = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel lvl = (ServerLevel) p.level();
			BlockPos at = p.blockPosition();
			int top = lvl.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.getX(), at.getZ());
			return new Vec3(at.getX() + 0.5, top + 0.35, at.getZ() + 0.5);
		});
		for (int pass = 0; pass < 2; pass++) {
			float yaw0 = pass == 0 ? 200f : 20f;
			for (int k = 0; k < 120; k++) {
				int kk = k;
				s.runOnServer(srv -> {
					double yaw = Math.toRadians(yaw0 + kk * 0.25);
					Vec3 eye = start.add(-Math.sin(yaw) * kk * 0.045, kk * 0.004, Math.cos(yaw) * kk * 0.045);
					float pitch = -4f - kk * 0.16f;
					ServerPlayer p = player(srv);
					p.teleportTo((ServerLevel) p.level(), eye.x, eye.y - p.getEyeHeight(), eye.z, Set.of(), (float) (yaw0 + kk * 0.25), pitch, false);
				});
				step(ctx, 1);
				frame(ctx, f("g" + pass, k));
			}
		}
	}

	/** D: World 5 as it is, no night vision, first person with the HUD; the Light Eater comes out of the dark. */
	private static void dark(ClientGameTestContext ctx, TestSingleplayerContext sp, BlockPos a) {
		var s = sp.getServer();
		s.runCommand("effect clear @a night_vision");
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runCommand("item replace entity @p weapon.mainhand with minecraft:torch");
		s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 16, Set.of(), 0f, 2f, false));
		step(ctx, 20);
		chunks(ctx, sp);
		hudScale(ctx, 1.5f);
		hud(ctx, true);
		camera(ctx, CameraType.FIRST_PERSON);
		int i = 0;
		for (int k = 0; k < 200; k++) {
			if (k == 50) s.runOnServer(srv -> MatrioBoss.summon((ServerLevel) player(srv).level(), "light_eater", a, player(srv), false));
			if (k == 1) ctx.runOnClient(mc -> mc.options.keyUp.setDown(true));
			if (k == 70) ctx.runOnClient(mc -> mc.options.keyUp.setDown(false));
			if (k % 6 == 0) s.runOnServer(Film::clearBad);
			step(ctx, 1);
			frame(ctx, f("d", i++));
		}
		ctx.runOnClient(EpicPlay::release);
		hud(ctx, false);
		hudScale(ctx, 1f);
		s.runCommand("kill @e[type=matriochka:light_eater]");
		s.runCommand("gamemode creative @a");
	}

	// ---------------------------------------------------------------- the recap
	private static void recap(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			PlayerState ps = PlayerState.of(p);
			CycleStats.reset(ps);
			ps.tag().remove(CycleStats.LAST);
			CycleStats.add(p, "deaths", 7);
			CycleStats.add(p, "lost", 5);
			CycleStats.add(p, "rebuilt", 4);
			CycleStats.add(p, "souls", 4180);
			CycleStats.add(p, "pages", 41);
			CycleStats.add(p, "hidden", 10);
			CycleStats.add(p, "ticks", 20 * 60 * 60 * 14 + 20 * 60 * 23);
			CycleStats.add(p, "worlds", 0x7FE);
			CycleStats.add(p, "bosses", 0x7FF);
			ps.tag().putInt("karma", 46);
			ps.sync();
		});
		s.runCommand("execute as @p at @s run tp @s ~ ~ ~ 0 -10");
		step(ctx, 20);
		s.runOnServer(srv -> Endings.play(player(srv), Endings.SEAL));
		step(ctx, 20);
		if (ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof EndingScreen)) ctx.runOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc).onClose());
		for (int k = 0; k < 100; k++) {
			step(ctx, 1);
			frame(ctx, f("r", k));
		}
		ctx.setScreen(() -> null);
	}

}
