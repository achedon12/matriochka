package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.Ui;
import fr.achedon12.matriochka.content.BossAnims;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.util.ArrayList;
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
 * What the frame-accurate captures (TiktokCapture, WorldFilm) share: the frozen server stepped one tick per frame
 * with the interface clock, the frames, the camera, the cursor's glide, the Seed's ritual (p first person, s an
 * orbit), the worlds' arenas and the boss takes (v orbit, i introduction, b signature attacks, f third-person fight). One capture runs per game, so the frame
 * size and the name prefix are set once by {@link #begin}.
 */
final class Film {
	private Film() {}

	static int W = 1080, H = 1920;
	private static String PREFIX = "tk";
	static TestServerContext SERVER;
	/** The cursor's path, one line a frame, for drawing it over the frames afterwards (screenshots have no cursor). */
	static final StringBuilder CURSOR = new StringBuilder();
	static double[] cur = {540, 1500};
	/** Keeps the action bar empty in every frame (WorldFilm: the rules' warnings would sit over the hotbar). */
	static boolean quietOverlay;

	static void begin(String prefix, int w, int h) {
		PREFIX = prefix;
		W = w;
		H = h;
		CURSOR.setLength(0);
		cur = new double[]{w / 2.0, h * 0.78};
	}

	// ---------------------------------------------------------------- clock and frames
	/** Waits game ticks and moves the interface clock by as much. */
	static void step(ClientGameTestContext ctx, int ticks) {
		// the server is frozen (/tick freeze) once the world is up: it moves exactly as many ticks as the client, so a
		// frame is one tick of game time however long its screenshot takes
		if (SERVER != null) SERVER.runCommand("tick step " + ticks);
		for (int i = 0; i < ticks; i++) {
			ctx.waitTick();
			Ui.frameClock += 50;
		}
		// no toast in a promo frame (advancements, recipes, tutorials): they show test state
		ctx.runOnClient(mc -> {
			fr.achedon12.matriochka.client.mc.McClient.clearToasts(mc);
			if (quietOverlay) fr.achedon12.matriochka.client.mc.McClient.clearOverlay(mc);
		});
	}

	static void frame(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(W, H).disableCounterPrefix());
	}

	static String f(String take, int i) {
		return String.format(Locale.ROOT, "%s_%s_%04d", PREFIX, take, i);
	}

	/** One frame a tick, frames frames, numbered from i; returns the next number. */
	static int roll(ClientGameTestContext ctx, String take, int i, int frames) {
		for (int k = 0; k < frames; k++) {
			step(ctx, 1);
			frame(ctx, f(take, i++));
		}
		return i;
	}

	static void hud(ClientGameTestContext ctx, boolean on) {
		ctx.runOnClient(mc -> { if (fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc) == on) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
	}

	static void camera(ClientGameTestContext ctx, CameraType type) {
		ctx.runOnClient(mc -> mc.options.setCameraType(type));
	}

	static void chunks(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		try {
			McTest.waitForChunks(sp);
		} catch (AssertionError e) {
			step(ctx, 40);
		}
	}

	static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	static void hudScale(ClientGameTestContext ctx, float scale) {
		ctx.runOnClient(mc -> {
			Comfort.get().hudScale = scale;
			Comfort.get().hudCorner = "top_left";
			Comfort.changed();
		});
	}

	/** Places the camera (a spectator or a flying creative player) at eye position eye, looking at a point. */
	static void look(MinecraftServer server, Vec3 eye, Vec3 at) {
		ServerPlayer p = player(server);
		Vec3 to = at.subtract(eye);
		float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
		float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
		p.teleportTo((ServerLevel) p.level(), eye.x, eye.y - p.getEyeHeight(), eye.z, Set.of(), yaw, pitch, false);
	}

	static void fly(TestServerContext s) {
		s.runOnServer(server -> {
			for (var p : server.getPlayerList().getPlayers()) {
				p.getAbilities().mayfly = true;
				p.getAbilities().flying = true;
				p.onUpdateAbilities();
			}
		});
	}

	static void hold(ServerPlayer p, Item item) {
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

	static void use(ServerPlayer p, BlockPos pos, Direction face) {
		Vec3 hit = Vec3.atCenterOf(pos).add(face.getStepX() * 0.5, face.getStepY() * 0.5, face.getStepZ() * 0.5);
		p.gameMode.useItemOn(p, p.level(), p.getItemInHand(InteractionHand.MAIN_HAND), InteractionHand.MAIN_HAND, new BlockHitResult(hit, face, pos, false));
	}

	static void clearBad(MinecraftServer s) {
		var p = player(s);
		for (var eff : List.of(MobEffects.DARKNESS, MobEffects.BLINDNESS, MobEffects.NAUSEA, MobEffects.LEVITATION)) p.removeEffect(eff);
		p.setHealth(p.getMaxHealth());
	}

	// ---------------------------------------------------------------- the cursor
	/** Moves the cursor from where it is to a point of the interface (GUI coordinates), easing, one frame a tick. */
	static int glide(ClientGameTestContext ctx, String take, int i, int[] to, int frames) {
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

	/** Frames with the cursor still, its place logged. */
	static int still(ClientGameTestContext ctx, String take, int i, int frames) {
		for (int k = 0; k < frames; k++) {
			step(ctx, 1);
			String n = f(take, i++);
			CURSOR.append(n).append(' ').append((int) cur[0]).append(' ').append((int) cur[1]).append('\n');
			frame(ctx, n);
		}
		return i;
	}

	static int clickAt(ClientGameTestContext ctx, String take, int i) {
		ctx.getInput().pressMouse(com.mojang.blaze3d.platform.InputConstants.MOUSE_BUTTON_LEFT);
		CURSOR.append("click ").append(f(take, i)).append('\n');
		return i;
	}

	// ---------------------------------------------------------------- the Seed
	/** A small garden on the Surface: grass, the World Soil in the middle, water two blocks away, a few flowers. */
	static BlockPos garden(ClientGameTestContext ctx, TestSingleplayerContext sp) {
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
	static void soil(TestServerContext s, BlockPos c) {
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

	static void plant(TestServerContext s, BlockPos c) {
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			hold(p, ModContent.item("seed_1"));
			use(p, c.below(), Direction.UP);
		});
	}

	static boolean hatched(TestServerContext s, BlockPos c) {
		return s.computeOnServer(srv -> player(srv).level().getBlockState(c).is(ModContent.block("world_block")));
	}

	/** P: first person, the Seed in hand, planted, its ritual, the World Block, then a right click and World 1. */
	static void seedPov(ClientGameTestContext ctx, TestSingleplayerContext sp, BlockPos c, String take) {
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
			frame(ctx, f(take, i++));
		}
		// a real right click on the soil, through the client, so the hand moves; the server's use if it missed
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(true));
		step(ctx, 1);
		frame(ctx, f(take, i++));
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
		step(ctx, 2);
		if (!s.computeOnServer(srv -> player(srv).level().getBlockState(c).is(ModContent.block("planted_seed")))) {
			Matriochka.LOG.warn("[film] the click missed the soil, planting from the server");
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
			frame(ctx, f(take, i++));
		}
		// empty hand, right click: into the world
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().clearContent();
			p.getInventory().setSelectedSlot(0);
		});
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.setXRot(32f); });
		step(ctx, 1);
		frame(ctx, f(take, i++));
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(true));
		step(ctx, 1);
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
		for (int k = 0; k < 170; k++) {
			if (k == 6 && s.computeOnServer(srv -> player(srv).level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD))) {
				Matriochka.LOG.warn("[film] the click missed the World Block, entering from the server");
				s.runOnServer(srv -> use(player(srv), c, Direction.NORTH));
			}
			// once inside, the head comes up to the jungle
			if (k > 8) {
				float pt = Math.max(-4f, 32f - (k - 8) * 0.9f);
				ctx.runOnClient(mc -> { if (mc.player != null && !mc.player.level().dimension().equals(net.minecraft.world.level.Level.OVERWORLD)) mc.player.setXRot(pt); });
			}
			step(ctx, 1);
			frame(ctx, f(take, i++));
		}
		hud(ctx, false);
		s.runCommand("execute as @p run matriochka world leave");
		step(ctx, 60);
		chunks(ctx, sp);
	}

	/** S: the same ritual from a camera circling the Seed close to the ground. */
	static void seedOrbit(ClientGameTestContext ctx, TestSingleplayerContext sp, BlockPos c, String take) {
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
			frame(ctx, f(take, k));
		}
		s.runCommand("gamemode survival @a");
		s.runOnServer(srv -> ((ServerLevel) player(srv).level()).setBlock(c, Blocks.AIR.defaultBlockState(), 3));
	}

	// ---------------------------------------------------------------- the worlds
	static void enter(ClientGameTestContext ctx, TestSingleplayerContext sp, int w) {
		var s = sp.getServer();
		s.runCommand("gamemode creative @a");
		s.runCommand("execute as @p run matriochka world enter " + w);
		ctx.setScreen(() -> null);
		step(ctx, 100);
		chunks(ctx, sp);
	}

	static void leave(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		camera(ctx, CameraType.FIRST_PERSON);
		s.runCommand("kill @e[type=!player]");
		s.runCommand("gamemode creative @a");
		s.runCommand("effect clear @a");
		s.runCommand("execute as @p run matriochka world leave");
		step(ctx, 40);
	}

	/** The arena of world w, built near where the player stands; returns its centre (the lair's heart for a lair). */
	static BlockPos arena(TestServerContext s, int world) {
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

	static void buffs(TestServerContext s, int w, boolean nightVision) {
		if (nightVision) s.runCommand("effect give @a night_vision infinite 0 true");
		s.runCommand("effect give @a resistance infinite 4 true");
		s.runCommand("effect give @a regeneration infinite 4 true");
		s.runCommand("effect give @a saturation infinite 4 true");
		if (w == 7) s.runCommand("effect give @a conduit_power infinite 0 true");
	}

	static MatrioBoss boss(MinecraftServer srv, String id) {
		ServerLevel lvl = (ServerLevel) player(srv).level();
		for (var e : lvl.getEntitiesOfClass(MatrioBoss.class, player(srv).getBoundingBox().inflate(120))) {
			if (net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getPath().equals(id)) return e;
		}
		return null;
	}

	static final String[] BOSSES = {"block_guardian", "spore_queen", "ash_titan", "grand_jailer", "storm_king", "light_eater", "your_double",
		"pressure_leviathan", "seasons_master", "terrain_heart_boss", "the_unfinished"};
	/** The attacks filmed for each world's boss (indices in BossAnims.SLUGS). */
	static final int[][] MOVES = {{2, 1}, {1}, {0, 2}, {1}, {1, 2}, {0, 1}, {2}, {1, 0}, {2}, {0}, {2, 0}};

	/** Up to three of world w's creatures that show well on screen: no elites, statues, mimics or hidden roots. */
	static List<Defs.MobDef> creatures(int w) {
		List<Defs.MobDef> out = new ArrayList<>();
		for (Defs.MobDef m : Content.MOBS) {
			if (m.world() != w || out.size() >= 3 || m.elite() || m.behavior().equals("statue") || m.behavior().equals("mimic") || m.behavior().equals("ambush_root")) continue;
			out.add(m);
		}
		return out;
	}

	private static String tag(int w) {
		return String.format(Locale.ROOT, "w%02d", w);
	}

	/**
	 * I: the boss wakes in front of the player, with its introduction (title card, bars, camera) when intro is set;
	 * without, it is summoned out of frame. Either way it is left calm in the middle of the arena.
	 */
	static void bossIntro(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, BlockPos a, boolean intro) {
		var s = sp.getServer();
		String id = BOSSES[w];
		boolean lair = w > 0 && ModContent.bossForWorld(w).lair();
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
		s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 12, Set.of(), 0f, -4f, false));
		step(ctx, lair ? 75 : 15);
		chunks(ctx, sp);
		camera(ctx, CameraType.FIRST_PERSON);
		boolean exists = s.computeOnServer(srv -> boss(srv, id) != null);
		if (intro && !exists) {
			hud(ctx, true);
			s.runOnServer(srv -> MatrioBoss.summon((ServerLevel) player(srv).level(), id, a, player(srv), true));
			for (int k = 0; k < 96; k++) {
				step(ctx, 1);
				frame(ctx, f("i_" + tag(w), k));
			}
			hud(ctx, false);
		} else if (!exists) {
			s.runOnServer(srv -> MatrioBoss.summon((ServerLevel) player(srv).level(), id, a, player(srv), false));
			step(ctx, 40);
		}
		s.runOnServer(srv -> { MatrioBoss b = boss(srv, id); if (b != null) b.calm(100000); });
	}

	/**
	 * V: an orbit of the arena, the boss held still in the middle and three of the world's creatures around (summoned
	 * at the player, so in the player's world: the server's own commands run on the Surface).
	 */
	static void orbit(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, BlockPos a) {
		var s = sp.getServer();
		String id = BOSSES[w];
		s.runCommand("gamemode spectator @a");
		int n = 0;
		for (Defs.MobDef m : creatures(w)) {
			s.runCommand("execute as @a at @s run summon matriochka:" + m.id() + " " + (a.getX() + n * 4 - 4) + " " + a.getY() + " " + (a.getZ() - 5 + n));
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
			frame(ctx, f("v_" + tag(w), k));
		}
		s.runCommand("kill @e[type=!player,type=!marker,type=!matriochka:" + id + "]");
	}

	/** B: the signature attacks, the boss alone against an invisible target, seen from low in front. */
	static void attacks(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, BlockPos a) {
		var s = sp.getServer();
		String id = BOSSES[w];
		s.runCommand("gamemode creative @a");
		fly(s);
		int[] picks = MOVES[w];
		List<String> slugs = BossAnims.SLUGS.get(id);
		for (int pick : picks) {
			String tagm = tag(w) + "_" + (slugs == null ? Integer.toString(pick) : slugs.get(pick));
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

	/** F: third person, the HUD on, against three of the world's creatures (the boss sent away first). */
	static void fight(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, BlockPos a) {
		var s = sp.getServer();
		s.runCommand("kill @e[type=matriochka:" + BOSSES[w] + "]");
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runCommand("item replace entity @p weapon.mainhand with minecraft:netherite_sword");
		s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), a.getX() + 0.5, a.getY(), a.getZ() + 0.5 - 12, Set.of(), 0f, 0f, false));
		step(ctx, 10);
		int n = 0;
		for (Defs.MobDef m : creatures(w)) {
			s.runCommand("execute as @a at @s run summon matriochka:" + m.id() + " " + (a.getX() + n * 5 - 5) + " " + a.getY() + " " + (a.getZ() + 2 + n));
			n++;
		}
		hudScale(ctx, 1.5f);
		hud(ctx, true);
		camera(ctx, CameraType.THIRD_PERSON_BACK);
		step(ctx, 4);
		for (int k = 0; k < 150; k++) {
			int ff = k;
			ctx.runOnClient(mc -> EpicPlay.play(mc, null, ff, false));
			if (k % 6 == 0) s.runOnServer(Film::clearBad);
			step(ctx, 1);
			frame(ctx, f("f_" + tag(w), k));
		}
		ctx.runOnClient(EpicPlay::release);
		hud(ctx, false);
		hudScale(ctx, 1f);
	}

	static IronGolem decoy(ServerLevel lvl, double x, double y, double z) {
		var box = new net.minecraft.world.phys.AABB(x - 40, y - 20, z - 40, x + 40, y + 40, z + 40);
		var found = lvl.getEntitiesOfClass(IronGolem.class, box, e -> e.isAlive() && e.entityTags().contains("tk_decoy"));
		IronGolem d;
		if (!found.isEmpty()) d = found.getFirst();
		else {
			d = fr.achedon12.matriochka.mc.McEntities.IRON_GOLEM.create(lvl, EntitySpawnReason.COMMAND);
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
			if (dist < reach && p.getAttackStrengthScale(0f) > 0.92f && mc.gameMode != null) attack(mc, best);
		}

		/** A real left click through the client (the arm swings, the hit lands as a player's), the game mode's attack if that fails. */
		static void attack(Minecraft mc, Entity target) {
			try {
				var m = Minecraft.class.getDeclaredMethod("startAttack");
				m.setAccessible(true);
				m.invoke(mc);
			} catch (ReflectiveOperationException e) {
				mc.gameMode.attack(mc.player, target);
			}
		}
	}
}
