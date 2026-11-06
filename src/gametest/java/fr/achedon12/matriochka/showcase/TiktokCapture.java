package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.EndingScreen;
import fr.achedon12.matriochka.client.StallScreen;
import fr.achedon12.matriochka.client.Ui;
import fr.achedon12.matriochka.content.BossAnims;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
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
import java.util.List;
import java.util.Locale;
import java.util.Set;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.Util;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.golem.IronGolem;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

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

	static final int W = 1080, H = 1920;
	private static String TAKES = "";
	private static final StringBuilder CURSOR = new StringBuilder();

	private static boolean take(char c) {
		return TAKES.isEmpty() || TAKES.indexOf(c) >= 0;
	}

	// ---------------------------------------------------------------- clock and frames
	/** Waits game ticks and moves the interface clock by as much. */
	private static void step(ClientGameTestContext ctx, int ticks) {
		// the server is frozen (/tick freeze) once the world is up: it moves exactly as many ticks as the client, so a
		// frame is one tick of game time however long its screenshot takes
		if (SERVER != null) SERVER.runCommand("tick step " + ticks);
		for (int i = 0; i < ticks; i++) {
			ctx.waitTick();
			Ui.frameClock += 50;
		}
	}

	private static TestServerContext SERVER;

	private static void frame(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(W, H).disableCounterPrefix());
	}

	private static String f(String take, int i) {
		return String.format(Locale.ROOT, "tk_%s_%04d", take, i);
	}

	private static void hud(ClientGameTestContext ctx, boolean on) {
		ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden() == on) mc.gui.hud.toggle(); });
	}

	private static void camera(ClientGameTestContext ctx, CameraType type) {
		ctx.runOnClient(mc -> mc.options.setCameraType(type));
	}

	private static void chunks(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		try {
			sp.getConnection().waitForChunksRender();
		} catch (AssertionError e) {
			step(ctx, 40);
		}
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	private static void hudScale(ClientGameTestContext ctx, float scale) {
		ctx.runOnClient(mc -> {
			Comfort.get().hudScale = scale;
			Comfort.get().hudCorner = "top_left";
			Comfort.changed();
		});
	}

	/** Places the camera (a spectator or a flying creative player) at eye position eye, looking at a point. */
	private static void look(MinecraftServer server, Vec3 eye, Vec3 at) {
		ServerPlayer p = player(server);
		Vec3 to = at.subtract(eye);
		float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
		float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
		p.teleportTo((ServerLevel) p.level(), eye.x, eye.y - p.getEyeHeight(), eye.z, Set.of(), yaw, pitch, false);
	}

	private static void fly(TestServerContext s) {
		s.runOnServer(server -> {
			for (var p : server.getPlayerList().getPlayers()) {
				p.getAbilities().mayfly = true;
				p.getAbilities().flying = true;
				p.onUpdateAbilities();
			}
		});
	}

	private static void hold(ServerPlayer p, Item item) {
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			if (!inv.getItem(i).is(item)) continue;
			if (i < 9) inv.setSelectedSlot(i);
			else {
				ItemStack held = inv.getItem(inv.getSelectedSlot());
				inv.setItem(inv.getSelectedSlot(), inv.getItem(i));
				inv.setItem(i, held);
			}
			return;
		}
	}

	private static void use(ServerPlayer p, BlockPos pos, Direction face) {
		Vec3 hit = Vec3.atCenterOf(pos).add(face.getStepX() * 0.5, face.getStepY() * 0.5, face.getStepZ() * 0.5);
		p.gameMode.useItemOn(p, p.level(), p.getItemInHand(InteractionHand.MAIN_HAND), InteractionHand.MAIN_HAND, new BlockHitResult(hit, face, pos, false));
	}

	private static void clearBad(MinecraftServer s) {
		var p = player(s);
		for (var eff : List.of(MobEffects.DARKNESS, MobEffects.BLINDNESS, MobEffects.NAUSEA, MobEffects.LEVITATION)) p.removeEffect(eff);
		p.setHealth(p.getMaxHealth());
	}

	// ---------------------------------------------------------------- run
	static void run(ClientGameTestContext ctx) {
		TAKES = System.getProperty("matriochka.takes", "");
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
			if (take('p')) seedPov(ctx, sp, garden);
			if (take('s')) seedOrbit(ctx, sp, garden);
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

	// ---------------------------------------------------------------- the Seed
	/** A small garden on the Surface: grass, the World Soil in the middle, water two blocks away, a few flowers. */
	private static BlockPos garden(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		BlockPos c = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel level = (ServerLevel) p.level();
			BlockPos at = p.blockPosition();
			for (int dx = -7; dx <= 7; dx++) {
				for (int dz = -7; dz <= 7; dz++) {
					double r = Math.sqrt(dx * dx + dz * dz);
					if (r > 7.4) continue;
					level.setBlock(at.offset(dx, -2, dz), Blocks.DIRT.defaultBlockState(), 3);
					level.setBlock(at.offset(dx, -1, dz), Blocks.GRASS_BLOCK.defaultBlockState(), 3);
					for (int dy = 0; dy <= 6; dy++) level.setBlock(at.offset(dx, dy, dz), Blocks.AIR.defaultBlockState(), 3);
				}
			}
			level.setBlock(at.offset(2, -1, 0), Blocks.WATER.defaultBlockState(), 3);
			level.setBlock(at.offset(2, -1, 1), Blocks.WATER.defaultBlockState(), 3);
			int[][] flowers = {{-2, 2}, {-3, -1}, {1, -3}, {3, 3}, {-1, 4}, {4, -2}, {-4, 3}, {0, -5}, {5, 1}};
			var kinds = List.of(Blocks.POPPY, Blocks.CORNFLOWER, Blocks.OXEYE_DAISY, Blocks.POPPY, Blocks.SHORT_GRASS, Blocks.DANDELION, Blocks.SHORT_GRASS, Blocks.POPPY, Blocks.FERN);
			for (int i = 0; i < flowers.length; i++) level.setBlock(at.offset(flowers[i][0], 0, flowers[i][1]), kinds.get(i).defaultBlockState(), 3);
			return at;
		});
		step(ctx, 20);
		chunks(ctx, sp);
		return c;
	}

	/** World Soil 0, tilled, at the garden's centre, and nothing left of an earlier World Block of World 1. */
	private static void soil(TestServerContext s, BlockPos c) {
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel level = (ServerLevel) p.level();
			level.setBlock(c, Blocks.AIR.defaultBlockState(), 3);
			level.setBlock(c.below(), ModContent.block("world_soil_0").defaultBlockState(), 3);
			p.getInventory().add(new ItemStack(Items.IRON_HOE));
			hold(p, Items.IRON_HOE);
			use(p, c.below(), Direction.UP);
			p.getInventory().clearContent();
			p.getInventory().add(new ItemStack(ModContent.item("seed_1")));
			hold(p, ModContent.item("seed_1"));
		});
	}

	private static void plant(TestServerContext s, BlockPos c) {
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			hold(p, ModContent.item("seed_1"));
			use(p, c.below(), Direction.UP);
		});
	}

	private static boolean hatched(TestServerContext s, BlockPos c) {
		return s.computeOnServer(srv -> player(srv).level().getBlockState(c).is(ModContent.block("world_block")));
	}

	/** P: first person, the Seed in hand, planted, its ritual, the World Block, then a right click and World 1. */
	private static void seedPov(ClientGameTestContext ctx, TestSingleplayerContext sp, BlockPos c) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		camera(ctx, CameraType.FIRST_PERSON);
		soil(s, c);
		s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), c.getX() + 0.5, c.getY(), c.getZ() - 1.6, Set.of(), 0f, 45f, false));
		step(ctx, 20);
		hud(ctx, true);
		int i = 0;
		for (int k = 0; k < 14; k++) {
			step(ctx, 1);
			frame(ctx, f("p", i++));
		}
		// a real right click on the soil, through the client, so the hand moves; the server's use if it missed
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(true));
		step(ctx, 1);
		frame(ctx, f("p", i++));
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
		step(ctx, 2);
		if (!s.computeOnServer(srv -> player(srv).level().getBlockState(c).is(ModContent.block("planted_seed")))) {
			Matriochka.LOG.warn("[tiktok] the click missed the soil, planting from the server");
			plant(s, c);
		}
		// the ritual: 200 ticks, then the burst; every tick until a little after
		int after = -1;
		for (int k = 0; k < 320 && (after < 0 || after < 50); k++) {
			step(ctx, 1);
			if (after < 0 && hatched(s, c)) after = 0;
			else if (after >= 0) after++;
			// the head comes up slowly over the last part, toward the little world above the block
			float pitch = after < 0 ? 45f - Math.max(0, k - 120) * 0.08f : Math.max(16f, 38f - after * 0.45f);
			ctx.runOnClient(mc -> { if (mc.player != null) mc.player.setXRot(pitch); });
			frame(ctx, f("p", i++));
		}
		// empty hand, right click: into the world
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().clearContent();
			p.getInventory().setSelectedSlot(0);
		});
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.setXRot(32f); });
		step(ctx, 1);
		frame(ctx, f("p", i++));
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(true));
		step(ctx, 1);
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
		for (int k = 0; k < 170; k++) {
			if (k == 6 && s.computeOnServer(srv -> player(srv).level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD))) {
				Matriochka.LOG.warn("[tiktok] the click missed the World Block, entering from the server");
				s.runOnServer(srv -> use(player(srv), c, Direction.NORTH));
			}
			// once inside, the head comes up to the jungle
			if (k > 8) {
				float pt = Math.max(-4f, 32f - (k - 8) * 0.9f);
				ctx.runOnClient(mc -> { if (mc.player != null && !mc.player.level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD)) mc.player.setXRot(pt); });
			}
			step(ctx, 1);
			frame(ctx, f("p", i++));
		}
		hud(ctx, false);
		s.runCommand("execute as @p run matriochka world leave");
		step(ctx, 60);
		chunks(ctx, sp);
	}

	/** S: the same ritual from a camera circling the Seed close to the ground. */
	private static void seedOrbit(ClientGameTestContext ctx, TestSingleplayerContext sp, BlockPos c) {
		var s = sp.getServer();
		s.runCommand("gamemode survival @a");
		soil(s, c);
		s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), c.getX() + 0.5, c.getY(), c.getZ() - 1.6, Set.of(), 0f, 58f, false));
		step(ctx, 5);
		plant(s, c);
		step(ctx, 2);
		s.runCommand("gamemode spectator @a");
		camera(ctx, CameraType.FIRST_PERSON);
		Vec3 mid = Vec3.atBottomCenterOf(c);
		int after = -1;
		for (int k = 0; k < 330 && (after < 0 || after < 80); k++) {
			final int kk = k;
			final int af = after;
			s.runOnServer(srv -> {
				double a = Math.toRadians(150 + kk * 0.55);
				double r = af < 0 ? 3.1 - kk * 0.003 : 2.5 + af * 0.02;
				double y = af < 0 ? 0.55 : 0.55 + af * 0.028;
				look(srv, mid.add(Math.sin(a) * r, y, Math.cos(a) * r), mid.add(0, af < 0 ? 0.25 : 0.25 + af * 0.012, 0));
			});
			step(ctx, 1);
			if (after < 0 && hatched(s, c)) after = 0;
			else if (after >= 0) after++;
			frame(ctx, f("s", k));
		}
		s.runCommand("gamemode survival @a");
		s.runOnServer(srv -> ((ServerLevel) player(srv).level()).setBlock(c, Blocks.AIR.defaultBlockState(), 3));
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

	private static double[] cur = {540, 1500};

	/** Moves the cursor from where it is to a point of the interface (GUI coordinates), easing, one frame a tick. */
	private static int glide(ClientGameTestContext ctx, String take, int i, int[] to, int frames) {
		double scale = ctx.computeOnClient(mc -> mc.getWindow().getGuiScale());
		double x0 = cur[0], y0 = cur[1], x1 = to[0] * scale, y1 = to[1] * scale;
		for (int k = 1; k <= frames; k++) {
			double t = (double) k / frames;
			t = t * t * (3 - 2 * t);
			cur = new double[]{x0 + (x1 - x0) * t, y0 + (y1 - y0) * t};
			ctx.getInput().setCursorPos(cur[0], cur[1]);
			step(ctx, 1);
			String n = f(take, i++);
			CURSOR.append(n).append(' ').append((int) cur[0]).append(' ').append((int) cur[1]).append('\n');
			frame(ctx, n);
		}
		return i;
	}

	private static int hold(ClientGameTestContext ctx, String take, int i, int frames) {
		for (int k = 0; k < frames; k++) {
			step(ctx, 1);
			String n = f(take, i++);
			CURSOR.append(n).append(' ').append((int) cur[0]).append(' ').append((int) cur[1]).append('\n');
			frame(ctx, n);
		}
		return i;
	}

	private static int clickAt(ClientGameTestContext ctx, String take, int i) {
		ctx.getInput().pressMouse(com.mojang.blaze3d.platform.InputConstants.MOUSE_BUTTON_LEFT);
		CURSOR.append("click ").append(f(take, i)).append('\n');
		return i;
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
		i = hold(ctx, "m", i, 12);
		s.runOnServer(srv -> ((MatrioNpc) player(srv).level().getEntity(npcId)).mobInteract(player(srv), InteractionHand.MAIN_HAND));
		i = hold(ctx, "m", i, 30);
		if (!ctx.computeOnClient(mc -> mc.gui.screen() instanceof StallScreen)) {
			Matriochka.LOG.warn("[tiktok] the stall did not open");
			return;
		}
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) mc.gui.screen()).rowCenter(1)), 14);
		i = hold(ctx, "m", i, 16);
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) mc.gui.screen()).rowCenter(0)), 10);
		i = hold(ctx, "m", i, 6);
		i = clickAt(ctx, "m", i);
		i = hold(ctx, "m", i, 18);
		i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) mc.gui.screen()).slotCenter(2)), 12);
		i = hold(ctx, "m", i, 6);
		ctx.getInput().holdKey(com.mojang.blaze3d.platform.InputConstants.KEY_LSHIFT);
		i = clickAt(ctx, "m", i);
		ctx.getInput().releaseKey(com.mojang.blaze3d.platform.InputConstants.KEY_LSHIFT);
		i = hold(ctx, "m", i, 26);
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		step(ctx, 8);
		// the black market: karma -40 at a world's people
		s.runOnServer(srv -> {
			summonNpc(srv, "prisoner");
			karma(srv, -40);
		});
		s.runCommand("give @p matriochka:sealed_fragment 20");
		step(ctx, 6);
		i = hold(ctx, "m", i, 6);
		s.runOnServer(srv -> ((MatrioNpc) player(srv).level().getEntity(npcId)).mobInteract(player(srv), InteractionHand.MAIN_HAND));
		i = hold(ctx, "m", i, 28);
		if (ctx.computeOnClient(mc -> mc.gui.screen() instanceof StallScreen)) {
			int n = ctx.computeOnClient(mc -> ((StallScreen) mc.gui.screen()).getMenu().getOffers().size());
			i = glide(ctx, "m", i, ctx.computeOnClient(mc -> ((StallScreen) mc.gui.screen()).rowCenter(n - 1)), 16);
			i = hold(ctx, "m", i, 30);
		}
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		step(ctx, 8);
		s.runOnServer(srv -> {
			karma(srv, 0);
			for (Entity e : player(srv).level().getEntities((Entity) null, player(srv).getBoundingBox().inflate(24), e -> e instanceof MatrioNpc)) e.discard();
		});
		s.runCommand("clear @p");
	}

	// ---------------------------------------------------------------- the Doll of Life
	private static void enter(ClientGameTestContext ctx, TestSingleplayerContext sp, int w) {
		var s = sp.getServer();
		s.runCommand("gamemode creative @a");
		s.runCommand("execute as @p run matriochka world enter " + w);
		ctx.setScreen(() -> null);
		step(ctx, 100);
		chunks(ctx, sp);
	}

	private static void leave(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		camera(ctx, CameraType.FIRST_PERSON);
		s.runCommand("kill @e[type=!player]");
		s.runCommand("gamemode creative @a");
		s.runCommand("effect clear @a");
		s.runCommand("execute as @p run matriochka world leave");
		step(ctx, 40);
	}

	/** The arena of world w, built near where the player stands; returns its centre (the lair's heart for a lair). */
	private static BlockPos arena(TestServerContext s, int world) {
		s.runCommand("kill @e[type=marker]");
		s.runCommand("execute as @p at @s run summon marker ~ ~ ~ {Tags:[\"home\"]}");
		BlockPos a = s.computeOnServer(server -> {
			var p = server.getPlayerList().getPlayers().get(0);
			var c = p.blockPosition().offset(0, 0, 60);
			var level = (ServerLevel) p.level();
			if (world == 0 || world == 3) {
				fr.achedon12.matriochka.world.Arenas.buildArena(level, world, c);
				return c;
			}
			fr.achedon12.matriochka.world.Arenas.build(level, world, c);
			return ModContent.bossForWorld(world).lair() ? fr.achedon12.matriochka.world.Lairs.heart(world, c) : c;
		});
		if (world == 2) {
			for (int qx = -1; qx <= 0; qx++) for (int qz = -1; qz <= 0; qz++) {
				int x0 = a.getX() + qx * 30, z0 = a.getZ() + qz * 30;
				s.runCommand("fill " + x0 + " " + (a.getY() - 3) + " " + z0 + " " + (x0 + 29) + " " + (a.getY() + 14) + " " + (z0 + 29) + " minecraft:basalt replace minecraft:lava");
			}
		}
		return a;
	}

	private static void buffs(TestServerContext s, int w, boolean nightVision) {
		if (nightVision) s.runCommand("effect give @a night_vision infinite 0 true");
		s.runCommand("effect give @a resistance infinite 4 true");
		s.runCommand("effect give @a regeneration infinite 4 true");
		s.runCommand("effect give @a saturation infinite 4 true");
		if (w == 7) s.runCommand("effect give @a conduit_power infinite 0 true");
	}

	private static MatrioBoss boss(MinecraftServer srv, String id) {
		ServerLevel lvl = (ServerLevel) player(srv).level();
		for (var e : lvl.getEntitiesOfClass(MatrioBoss.class, player(srv).getBoundingBox().inflate(120))) {
			if (net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getPath().equals(id)) return e;
		}
		return null;
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
		i = holdWorld(ctx, "l", i, 12);
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
			i = holdWorld(ctx, "l", i, 5);
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				PlayerState.of(p).tag().putLong("last_revive", -100000);
				p.removeEffect(MobEffects.RESISTANCE);
				p.hurtServer((ServerLevel) p.level(), p.damageSources().generic(), 1000f);
				p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, -1, 4, false, false));
				MatrioBoss b = boss(srv, "ash_titan");
				if (b != null) b.calm(100000);
			});
			i = holdWorld(ctx, "l", i, 40);
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

	private static int holdWorld(ClientGameTestContext ctx, String take, int i, int frames) {
		for (int k = 0; k < frames; k++) {
			step(ctx, 1);
			frame(ctx, f(take, i++));
		}
		return i;
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
			if (k % 6 == 0) s.runOnServer(TiktokCapture::clearBad);
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
	private static final String[] BOSSES = {"block_guardian", "spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater", "your_double",
		"pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished"};
	/** The attacks filmed for each world's boss (indices in BossAnims.SLUGS). */
	private static final int[][] MOVES = {{2, 1}, {1}, {0, 2}, {1}, {1, 2}, {0, 1}, {2}, {1, 0}, {2}, {0}, {2, 0}};

	private static void worlds(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		boolean any = false;
		for (char c : "vibfgd".toCharArray()) any |= take(c);
		if (!any) return;
		var s = sp.getServer();
		String only = System.getProperty("matriochka.worlds", "");
		for (int w = 0; w <= 10; w++) {
			if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
			final int world = w;
			String tag = String.format(Locale.ROOT, "w%02d", w);
			if (w > 0) enter(ctx, sp, w);
			s.runCommand("gamemode creative @a");
			s.runCommand("effect clear @a");
			buffs(s, w, w != 5);
			BlockPos a = arena(s, w);
			String id = BOSSES[w];
			boolean lair = w > 0 && ModContent.bossForWorld(w).lair();
			// -Pfull=...: the worlds that also get the boss's introduction and attacks (all when empty)
			String fullList = System.getProperty("matriochka.full", "");
			boolean full = fullList.isEmpty() || ("," + fullList + ",").contains("," + w + ",");

			if (take('g') && w == 10) giant(ctx, sp);
			if (take('d') && w == 5) dark(ctx, sp, a);
			if (w == 5) buffs(s, 5, true);

			// I: the boss wakes in front of the player, with its introduction (title card, bars, camera)
			if (take('i') || take('b') || take('v')) {
				s.runCommand("gamemode survival @a");
				s.runCommand("clear @a");
				s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
				s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 12, Set.of(), 0f, -4f, false));
				step(ctx, lair ? 75 : 15);
				chunks(ctx, sp);
				camera(ctx, CameraType.FIRST_PERSON);
				boolean exists = s.computeOnServer(srv -> boss(srv, id) != null);
				if (take('i') && full && !exists) {
					hud(ctx, true);
					s.runOnServer(srv -> MatrioBoss.summon((ServerLevel) player(srv).level(), id, a, player(srv), true));
					for (int k = 0; k < 96; k++) {
						step(ctx, 1);
						frame(ctx, f("i_" + tag, k));
					}
					hud(ctx, false);
				} else if (!exists) {
					s.runOnServer(srv -> MatrioBoss.summon((ServerLevel) player(srv).level(), id, a, player(srv), false));
					step(ctx, 40);
				}
				s.runOnServer(srv -> { MatrioBoss b = boss(srv, id); if (b != null) b.calm(100000); });
			}

			// V: an orbit of the arena, the boss held still in the middle and three of the world's creatures around
			if (take('v')) {
				s.runCommand("gamemode spectator @a");
				int n = 0;
				for (Defs.MobDef m : Content.MOBS) {
					if (m.world() != w || n >= 3 || m.elite() || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
					s.runCommand("summon matriochka:" + m.id() + " " + (a.getX() + n * 4 - 4) + " " + a.getY() + " " + (a.getZ() - 5 + n));
					n++;
				}
				step(ctx, 10);
				for (int k = 0; k < 110; k++) {
					int kk = k;
					s.runOnServer(srv -> {
						MatrioBoss b = boss(srv, id);
						Vec3 c = b == null ? Vec3.atCenterOf(a) : b.getBoundingBox().getCenter();
						double r = 9 + (b == null ? 0 : b.getBbWidth() * 1.2) + kk * 0.015;
						double ang = Math.toRadians(205 + kk * 0.5);
						Vec3 eye = c.add(Math.sin(ang) * r, 1.0 + kk * 0.03, Math.cos(ang) * r);
						look(srv, eye, c.add(0, 0.5, 0));
					});
					step(ctx, 1);
					frame(ctx, f("v_" + tag, k));
				}
				s.runCommand("kill @e[type=!player,type=!marker,type=!matriochka:" + id + "]");
			}

			// B: the signature attacks, the boss alone against an invisible target, seen from low in front
			if (take('b') && full) {
				s.runCommand("gamemode creative @a");
				fly(s);
				int[] picks = MOVES[w];
				List<String> slugs = BossAnims.SLUGS.get(id);
				for (int pick : picks) {
					String tagm = tag + "_" + (slugs == null ? Integer.toString(pick) : slugs.get(pick));
					double[] box = s.computeOnServer(srv -> {
						MatrioBoss b = boss(srv, id);
						if (b == null) return new double[]{1, 2};
						b.getNavigation().stop();
						b.setDeltaMovement(0, 0, 0);
						b.snapTo(a.getX() + 0.5, b.getY(), a.getZ() + 0.5, 0f, 0f);
						b.setYHeadRot(0);
						b.setYBodyRot(0);
						return new double[]{b.getBbWidth(), b.getBbHeight(), b.getY()};
					});
					if (box.length < 3) break;
					double bw = box[0], bh = box[1], by = box[2];
					double tgt = Math.max(3.5, bw * 0.9 + 2);
					s.runOnServer(srv -> decoy((ServerLevel) player(srv).level(), a.getX() + 0.5, by, a.getZ() + 0.5 + tgt));
					double dist = Math.max(5.5, Math.max(1.35 * bh, 1.6 * bw)) * (w == 7 ? 1.25 : 1);
					Vec3 center = new Vec3(a.getX() + 0.5, by + bh * 0.5, a.getZ() + 0.5);
					step(ctx, 15);
					s.runOnServer(srv -> {
						MatrioBoss b = boss(srv, id);
						LivingEntity d = decoy((ServerLevel) player(srv).level(), a.getX() + 0.5, by, a.getZ() + 0.5 + tgt);
						if (b != null) b.rehearse(pick, d);
					});
					int strike = 0;
					boolean released = false;
					for (int k = 0; k < 150; k++) {
						int kk = k;
						s.runOnServer(srv -> {
							double ang = Math.toRadians(38 - kk * 0.08);
							double r = dist * (1.12 - kk * 0.0012);
							Vec3 eye = center.add(Math.sin(ang) * r, -bh * 0.22, Math.cos(ang) * r);
							look(srv, eye, center.add(0, bh * 0.05, tgt * 0.25));
							for (var eff : List.of(MobEffects.DARKNESS, MobEffects.BLINDNESS, MobEffects.NAUSEA, MobEffects.LEVITATION)) player(srv).removeEffect(eff);
						});
						step(ctx, 1);
						frame(ctx, f("b_" + tagm, k));
						boolean tele = s.computeOnServer(srv -> { MatrioBoss b = boss(srv, id); return b != null && b.telegraphing(); });
						if (!tele) released = true;
						if (released && ++strike > 45) break;
					}
					s.runOnServer(srv -> { MatrioBoss b = boss(srv, id); if (b != null) b.calm(100000); });
					buffs(s, w, w != 5);
					step(ctx, 50);
					s.runCommand("kill @e[type=!player,type=!marker,type=!matriochka:" + id + "]");
				}
			}

			// F: third person, the HUD on, against three of the world's creatures
			if (take('f') && w > 0) {
				s.runCommand("kill @e[type=matriochka:" + id + "]");
				s.runCommand("gamemode survival @a");
				s.runCommand("clear @a");
				s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
				s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 12, Set.of(), 0f, 0f, false));
				step(ctx, 10);
				int n = 0;
				for (Defs.MobDef m : Content.MOBS) {
					if (m.world() != w || n >= 3 || m.elite() || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
					s.runCommand("summon matriochka:" + m.id() + " " + (a.getX() + n * 5 - 5) + " " + a.getY() + " " + (a.getZ() + 2 + n));
					n++;
				}
				hudScale(ctx, 1.5f);
				hud(ctx, true);
				camera(ctx, CameraType.THIRD_PERSON_BACK);
				step(ctx, 4);
				for (int k = 0; k < 150; k++) {
					int ff = k;
					ctx.runOnClient(mc -> EpicPlay.play(mc, null, ff, false));
					if (k % 6 == 0) s.runOnServer(TiktokCapture::clearBad);
					step(ctx, 1);
					frame(ctx, f("f_" + tag, k));
				}
				ctx.runOnClient(EpicPlay::release);
				hud(ctx, false);
				hudScale(ctx, 1f);
			}
			if (w > 0) leave(ctx, sp);
			else {
				camera(ctx, CameraType.FIRST_PERSON);
				s.runCommand("kill @e[type=!player]");
				s.runCommand("effect clear @a");
			}
		}
	}

	private static IronGolem decoy(ServerLevel lvl, double x, double y, double z) {
		var box = new net.minecraft.world.phys.AABB(x - 40, y - 20, z - 40, x + 40, y + 40, z + 40);
		var found = lvl.getEntitiesOfClass(IronGolem.class, box, e -> e.isAlive() && e.entityTags().contains("tk_decoy"));
		IronGolem d;
		if (!found.isEmpty()) d = found.getFirst();
		else {
			d = net.minecraft.world.entity.EntityTypes.IRON_GOLEM.create(lvl, EntitySpawnReason.COMMAND);
			d.setNoAi(true);
			d.setSilent(true);
			d.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, -1, 0, false, false));
			d.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, -1, 4, false, false));
			d.addTag("tk_decoy");
			lvl.addFreshEntity(d);
		}
		d.snapTo(x, y, z, 180, 0);
		d.setDeltaMovement(0, 0, 0);
		d.setHealth(d.getMaxHealth());
		return d;
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
			if (k % 6 == 0) s.runOnServer(TiktokCapture::clearBad);
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
		if (ctx.computeOnClient(mc -> mc.gui.screen() instanceof EndingScreen)) ctx.runOnClient(mc -> mc.gui.screen().onClose());
		for (int k = 0; k < 100; k++) {
			step(ctx, 1);
			frame(ctx, f("r", k));
		}
		ctx.setScreen(() -> null);
	}

	/** The trailer's driven player, shared. */
	static final class EpicPlay {
		private EpicPlay() {}

		static void release(Minecraft mc) {
			var o = mc.options;
			for (var k : new net.minecraft.client.KeyMapping[]{o.keyUp, o.keyDown, o.keyLeft, o.keyRight, o.keySprint, o.keyJump}) k.setDown(false);
		}

		static void play(Minecraft mc, String boss, int f, boolean strafe) {
			var p = mc.player;
			if (p == null || mc.level == null) return;
			Entity best = null;
			double bd = 1e9;
			for (Entity e : mc.level.entitiesForRendering()) {
				if (e == p || !(e instanceof LivingEntity le) || !le.isAlive() || e instanceof Player) continue;
				var key = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
				if (boss != null && !key.getPath().equals(boss)) continue;
				if (boss == null && !key.getNamespace().equals("matriochka")) continue;
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
			double reach = best instanceof MatrioBoss ? 4.5 + best.getBbWidth() / 2 : 3.0;
			o.keyUp.setDown(dist > reach - 0.6);
			o.keySprint.setDown(dist > reach + 2);
			boolean side = strafe && dist < reach + 4;
			o.keyLeft.setDown(side && (f / 36) % 2 == 0);
			o.keyRight.setDown(side && (f / 36) % 2 == 1);
			o.keyJump.setDown(p.horizontalCollision || to.y > 1.2);
			if (dist < reach && p.getAttackStrengthScale(0f) > 0.92f && mc.gameMode != null) {
				try {
					var m = Minecraft.class.getDeclaredMethod("startAttack");
					m.setAccessible(true);
					m.invoke(mc);
				} catch (ReflectiveOperationException e) {
					mc.gameMode.attack(p, best);
				}
			}
		}
	}
}
