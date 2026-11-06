package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.Cinematics;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.ComfortScreen;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.client.MusicThemes;
import fr.achedon12.matriochka.client.MusicThemes.State;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;

/**
 * Checks the comfort options, the cinematics and the adaptive music: ./gradlew runClientGameTest -Pcomfort.
 * The options file round trip, the server skipping Nausea and Darkness for a player who opted out (and only for
 * them), a boss introduction and a world title card being triggered, and the music state machine. Screenshots:
 * comfort_options, comfort_boss_intro, comfort_subtitle, comfort_world_card, comfort_hud. Fails the run on the
 * first broken check, after the screenshots.
 */
final class ComfortTest {
	private ComfortTest() {}

	private static void shot(ClientGameTestContext ctx, String name, boolean hud) {
		if (!hud) ctx.runOnClient(mc -> { if (!mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
		if (!hud) ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	static void run(ClientGameTestContext ctx) {
		List<String> out = new ArrayList<>();
		// ---------------------------------------------------------------- the options file
		Path dir = ctx.computeOnClient(mc -> mc.gameDirectory.toPath().resolve("config"));
		Path trip = dir.resolve("matriochka-client-check.json");
		Comfort.Values v = new Comfort.Values();
		v.shake = 35;
		v.flashes = false;
		v.softEffects = true;
		v.hudScale = 1.5f;
		v.hudCorner = "bottom_right";
		v.musicDanger = 40;
		Comfort.write(trip, v);
		Comfort.Values back = Comfort.read(trip);
		check(out, back.shake == 35 && !back.flashes && back.softEffects && back.hudScale == 1.5f && back.hudCorner.equals("bottom_right") && back.musicDanger == 40,
			"the options file keeps what was written");
		try {
			Files.writeString(trip, "{\"shake\": 250, \"hudScale\": 9, \"hudCorner\": \"middle\"}");
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		Comfort.Values bad = Comfort.read(trip);
		check(out, bad.shake == 100 && bad.hudScale == 2f && bad.hudCorner.equals("top_left") && bad.cinematics, "out-of-range options are brought back in range");
		Comfort.useFile(dir.resolve("matriochka-client.json"));

		// ---------------------------------------------------------------- the music state machine
		check(out, MusicThemes.choose(false, 2f, false) == State.EXPLORE, "exploring plays the world theme");
		check(out, MusicThemes.choose(false, 2f, true) == State.DANGER, "hunted, the danger theme");
		check(out, MusicThemes.choose(false, 0.8f, true) == State.BOSS, "a boss fight wins over danger");
		check(out, MusicThemes.choose(false, 0.2f, false) == State.BOSS_FINAL, "below a third, the fiercer boss theme");
		check(out, MusicThemes.choose(true, 0.5f, true) == State.NONE, "a screen's own music wins over everything");

		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("time set 6000");
			server.runCommand("difficulty normal");
			server.runCommand("gamemode survival @a");
			server.runCommand("effect give @a resistance infinite 4 true");
			server.runCommand("effect give @a regeneration infinite 4 true");
			server.runCommand("execute as @p run matriochka progression set 10");
			ctx.setScreen(() -> null);
			ctx.waitTicks(40);

			// ------------------------------------------------------------ soft effects, synced to the server
			ctx.runOnClient(mc -> {
				Comfort.get().softEffects = true;
				Comfort.changed();
			});
			ctx.waitTicks(10);
			boolean[] soft = server.computeOnServer(s -> {
				ServerPlayer p = s.getPlayerList().getPlayers().get(0);
				p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 100, 0));
				p.addEffect(new MobEffectInstance(MobEffects.DARKNESS, 100, 0));
				return new boolean[]{p.hasEffect(MobEffects.NAUSEA), p.hasEffect(MobEffects.DARKNESS)};
			});
			check(out, !soft[0] && !soft[1], "an opted-out player gets neither Nausea nor Darkness");
			ctx.waitTicks(5);
			check(out, ctx.computeOnClient(mc -> Cinematics.tinted()), "the client draws the soft tint instead");
			ctx.runOnClient(mc -> {
				Comfort.get().softEffects = false;
				Comfort.changed();
			});
			ctx.waitTicks(10);
			boolean hard = server.computeOnServer(s -> {
				ServerPlayer p = s.getPlayerList().getPlayers().get(0);
				p.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 40, 0));
				boolean has = p.hasEffect(MobEffects.NAUSEA);
				p.removeEffect(MobEffects.NAUSEA);
				return has;
			});
			check(out, hard, "without the option, Nausea applies as before");

			// ------------------------------------------------------------ the options screen
			ctx.setScreen(() -> new ComfortScreen(new JournalScreen(false)));
			ctx.waitTicks(12);
			shot(ctx, "comfort_options", false);
			ctx.setScreen(() -> null);
			ctx.waitTicks(5);

			// ------------------------------------------------------------ danger
			// the spawn point is spread at random over a hilly spot: on a slope ~4 ~ ~4 can be inside the hill, where the
			// zombie never sees the player; a small open pad at the player's feet keeps it in the open, in sight
			server.runOnServer(s -> {
				ServerPlayer p = s.getPlayerList().getPlayers().get(0);
				var level = p.level();
				var feet = p.blockPosition();
				for (int dx = -6; dx <= 6; dx++) {
					for (int dz = -6; dz <= 6; dz++) {
						level.setBlockAndUpdate(feet.offset(dx, -1, dz), net.minecraft.world.level.block.Blocks.STONE.defaultBlockState());
						for (int dy = 0; dy <= 3; dy++) level.setBlockAndUpdate(feet.offset(dx, dy, dz), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
					}
				}
			});
			server.runCommand("execute as @p at @s run summon minecraft:zombie ~4 ~ ~4");
			ctx.waitTicks(60);
			int danger = ctx.computeOnClient(mc -> Cinematics.danger());
			State hunted = ctx.computeOnClient(mc -> MusicThemes.state());
			check(out, danger > 0 && hunted == State.DANGER, "a zombie on your heels starts the danger theme (" + danger + ", " + hunted + ")");
			server.runCommand("kill @e[type=minecraft:zombie]");
			ctx.waitTicks(20);

			// ------------------------------------------------------------ boss introduction
			int before = ctx.computeOnClient(mc -> Cinematics.intros);
			server.runCommand("execute as @p at @s run matriochka boss block_guardian");
			ctx.waitTicks(28);
			int after = ctx.computeOnClient(mc -> Cinematics.intros);
			boolean playing = ctx.computeOnClient(mc -> Cinematics.introPlaying());
			String who = ctx.computeOnClient(mc -> Cinematics.lastIntroBoss());
			check(out, after == before + 1 && playing && who.equals("block_guardian"), "waking a boss plays its introduction (" + who + ")");
			shot(ctx, "comfort_boss_intro", true);
			ctx.waitTicks(60);
			State boss = ctx.computeOnClient(mc -> MusicThemes.state());
			check(out, boss == State.BOSS || boss == State.BOSS_FINAL, "the boss theme plays during the fight (" + boss + ")");
			ctx.runOnClient(mc -> Cinematics.startTelegraph("block_guardian", 2, 80));
			ctx.waitTicks(6);
			shot(ctx, "comfort_subtitle", true);
			server.runCommand("kill @e[type=matriochka:block_guardian]");
			ctx.waitTicks(200);
			State calm = ctx.computeOnClient(mc -> MusicThemes.state());
			check(out, calm == State.EXPLORE, "the music goes back to exploring after the fight (" + calm + ")");

			// ------------------------------------------------------------ world title card
			int cards = ctx.computeOnClient(mc -> Cinematics.worldCards);
			server.runCommand("execute as @p run matriochka world enter 1");
			ctx.setScreen(() -> null);
			for (int i = 0; i < 200 && !ctx.computeOnClient(mc -> Cinematics.cardPlaying()); i++) ctx.waitTick();
			check(out, ctx.computeOnClient(mc -> Cinematics.worldCards) == cards + 1, "entering World 1 the first time shows its title card");
			ctx.waitTicks(30);
			shot(ctx, "comfort_world_card", true);
			ctx.waitTicks(120);
			// the HUD plaque bigger, in the top right corner, with its gauge patterned
			ctx.runOnClient(mc -> {
				Comfort.get().hudScale = 1.5f;
				Comfort.get().hudCorner = "top_right";
				Comfort.get().patterns = true;
				Comfort.changed();
			});
			server.runOnServer(s -> {
				var ps = fr.achedon12.matriochka.rules.PlayerState.of(s.getPlayerList().getPlayers().get(0));
				ps.setGauge("toxin", 85);
				ps.sync();
			});
			ctx.waitTicks(40);
			shot(ctx, "comfort_hud", true);
			int cardsAgain = ctx.computeOnClient(mc -> Cinematics.worldCards);
			server.runCommand("execute as @p run matriochka world leave");
			ctx.waitTicks(40);
			server.runCommand("execute as @p run matriochka world enter 1");
			ctx.waitTicks(80);
			check(out, ctx.computeOnClient(mc -> Cinematics.worldCards) == cardsAgain, "the card does not play again on the next visit");
			ctx.runOnClient(mc -> {
				Comfort.get().hudScale = 1f;
				Comfort.get().hudCorner = "top_left";
				Comfort.get().patterns = false;
				Comfort.changed();
			});
		}
		for (String line : out) Matriochka.LOG.info("[comfort] {}", line);
		long failed = out.stream().filter(l -> l.startsWith("FAIL")).count();
		if (failed > 0) throw new AssertionError(failed + " comfort check(s) failed: " + out);
	}
}
