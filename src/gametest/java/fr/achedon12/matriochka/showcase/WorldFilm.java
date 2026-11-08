package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.Reliquary;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.client.StationScreen;
import fr.achedon12.matriochka.client.Ui;
import fr.achedon12.matriochka.client.mc.McClient;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Atlas;
import fr.achedon12.matriochka.world.Rumors;
import fr.achedon12.matriochka.world.Worlds;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.client.CameraType;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.Util;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import static fr.achedon12.matriochka.showcase.Film.*;

/**
 * Landscape takes for the 45-second videos that show off each world (-Dmatriochka.capture=worldfilm,
 * ./gradlew runClientGameTest -Pworldfilm -Pworlds=N): 1920 x 1080, every frame one game tick, the interface clock
 * stepped with it (see Film). Takes for each world (-Ptakes=..., all when empty):
 * h first person through the world with the HUD, its rule's meter rising; x the world's weapon in hand against
 * three of its creatures, seen from behind; a a slow orbit round the player in the world's armour; c its station
 * set down, opened, the cursor over its recipes and one pulled; w its wonder from the air, then its reliquary opened
 * with the right cross key; n one of its people telling the wonder's rumour; j the Journal on the world's card, then
 * its map; and the boss takes v orbit, i introduction, b signature attacks, f third-person fight. The Surface
 * (World 0) gets h, c, n, j and the boss takes, then p the Seed's ritual in first person, s the same from a circling
 * camera and u an aerial pass over its own places. Frames: wf_<take>_wNN_0000.png; the cursor's path in
 * wf_cursor.txt. A take that fails is logged and skipped.
 */
final class WorldFilm {
	private WorldFilm() {}

	private static String TAKES = "";

	private static boolean take(char c) {
		return TAKES.isEmpty() || TAKES.indexOf(c) >= 0;
	}

	private static String tag(int w) {
		return String.format(Locale.ROOT, "w%02d", w);
	}

	// ---------------------------------------------------------------- run
	static void run(ClientGameTestContext ctx) {
		TAKES = System.getProperty("matriochka.takes", "");
		Film.begin("wf", 1920, 1080);
		quietOverlay = true;
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
				o.fov().set(70);
				o.guiScale().set(3);
				// the chat stays hidden: command feedback, game mode changes and the test player's name never show
				o.chatVisibility().set(net.minecraft.world.entity.player.ChatVisiblity.HIDDEN);
				McClient.clearChat(mc);
				mc.resizeGui();
			});
			int[] win = ctx.computeOnClient(mc -> new int[]{mc.getWindow().getWidth(), mc.getWindow().getHeight(), mc.getWindow().getGuiScaledWidth()});
			Matriochka.LOG.info("[worldfilm] window {}x{}, gui width {}", win[0], win[1], win[2]);
			hud(ctx, false);
			for (String c : List.of("gamerule advance_time false", "gamerule advance_weather false", "weather clear", "gamerule spawn_monsters false",
				"gamerule announce_advancements false", "gamerule show_death_messages false", "gamerule send_command_feedback false",
				"gamerule log_admin_commands false", "gamerule fire_spread_radius_around_player 0", "time set 6000", "difficulty normal",
				"gamemode survival @a", "execute as @p run matriochka progression set 10")) s.runCommand(c);
			s.runOnServer(srv -> {
				PlayerState ps = PlayerState.of(player(srv));
				ps.addSouls(1200);
				ps.sync();
				// no invasion, surge or merchant breaks into a take
				fr.achedon12.matriochka.world.Config.get().worldEvents = false;
			});
			step(ctx, 40);
			s.runCommand("tick freeze");
			SERVER = s;
			String only = System.getProperty("matriochka.worlds", "");
			for (int w = 0; w <= 10; w++) {
				if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
				long t0 = System.nanoTime();
				try {
					world(ctx, sp, w);
				} catch (Throwable e) {
					Matriochka.LOG.warn("[worldfilm] world {} stopped: {}", w, e.toString());
				}
				Matriochka.LOG.info("[worldfilm] world {} done in {} s", w, (System.nanoTime() - t0) / 1_000_000_000L);
			}
			try {
				Files.writeString(Path.of("screenshots", "wf_cursor.txt"), CURSOR.toString());
			} catch (IOException e) {
				Matriochka.LOG.warn("[worldfilm] cursor log: {}", e.toString());
			}
			SERVER = null;
			s.runCommand("tick unfreeze");
			s.runOnServer(srv -> fr.achedon12.matriochka.world.Config.get().worldEvents = true);
		}
		quietOverlay = false;
		Ui.frameClock = -1;
	}

	// ---------------------------------------------------------------- a world
	/** What a world shows: its weapon, its armour, its station, one of its people and its wonder (any may be missing). */
	private record Kit(Item weapon, List<Item> armour, String station, String npc, String wonder) {}

	private static Kit kit(int w) {
		Item weapon = null;
		List<Item> armour = new ArrayList<>();
		for (Defs.ItemDef d : Content.ITEMS) {
			if (d.world() != w) continue;
			// the world's newest weapon (its replay gear) when it has one, else its sword
			if (d.kind().equals("weapon")) weapon = ModContent.item(d.id());
			if (d.kind().equals("armor")) armour.add(ModContent.item(d.id()));
		}
		// the Diving set has no helmet: the head is the snorkel's
		if (w == 7) armour.add(ModContent.item("pearl_snorkel"));
		String station = null;
		for (Defs.BlockDef b : Content.BLOCKS) if (b.world() == w && b.kind().equals("station") && station == null) station = b.id();
		String npc = null;
		for (Defs.NpcDef n : Content.PEOPLES) if (n.world() == w && npc == null) npc = n.id();
		Defs.StructureDef wonder = w > 0 ? Rumors.wonderOf(w) : null;
		return new Kit(weapon, armour, station, npc, wonder == null ? null : wonder.id());
	}

	private static BlockPos home;
	private static float homeYaw;
	/** How far the ground runs open ahead of home. */
	private static int open;
	/** World 7: the takes are set in open water, out of the stations' glass domes. */
	private static boolean swim;

	private static void world(ClientGameTestContext ctx, TestSingleplayerContext sp, int w) {
		var s = sp.getServer();
		if (w > 0) enter(ctx, sp, w);
		s.runCommand("gamemode survival @a");
		s.runCommand("effect clear @a");
		buffs(s, w, true);
		Kit kit = kit(w);
		home = s.computeOnServer(srv -> player(srv).blockPosition());
		swim = w == 7;
		float[] way = s.computeOnServer(srv -> openYaw((ServerLevel) player(srv).level(), w, home, player(srv).getYRot()));
		// in a maze (World 3's halls, World 5's caves) the arrival may face a wall: look round for a longer way
		if (way[1] < 12) {
			float[] first = way;
			Object[] found = s.computeOnServer(srv -> {
				ServerLevel lvl = (ServerLevel) player(srv).level();
				BlockPos at = home;
				float[] best = first;
				for (int dx = -40; dx <= 40; dx += 4) {
					for (int dz = -40; dz <= 40; dz += 4) {
						BlockPos c = home.offset(dx, 0, dz);
						BlockPos feet = new BlockPos(c.getX(), ground(lvl, w, c.getX() + 0.5, c.getZ() + 0.5, home.getY()), c.getZ());
						if (!room(lvl, feet) || Worlds.ceiling(w) && !covered(lvl, feet)) continue;
						float[] o = openYaw(lvl, w, feet, best[0]);
						if (o[1] > best[1]) {
							best = o;
							at = feet;
						}
					}
				}
				return new Object[]{at, best};
			});
			home = (BlockPos) found[0];
			way = (float[]) found[1];
			s.runOnServer(srv -> player(srv).teleportTo((ServerLevel) player(srv).level(), home.getX() + 0.5, home.getY(), home.getZ() + 0.5, Set.of(), 0f, 0f, false));
			step(ctx, 10);
			chunks(ctx, sp);
		}
		homeYaw = way[0];
		open = (int) way[1];
		// a few steps off the block the world is entered by, onto the open ground
		home = s.computeOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			for (int d = Math.min(3, open / 3); d >= 1; d--) {
				Vec3 v = ahead(d, 0, 0);
				BlockPos feet = BlockPos.containing(v.x, ground(lvl, w, v.x, v.z, home.getY()), v.z);
				if (room(lvl, feet)) return feet;
			}
			return home;
		});
		open -= Math.min(3, open / 3);
		Matriochka.LOG.info("[worldfilm] world {} from {} facing {} ({} blocks open): {}", w, home, homeYaw, open, kit);
		// the dark halls and caves get invisible light round home, so the takes read
		if (w == 3 || w == 5) s.runOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			for (int dx = -18; dx <= 18; dx += 6) for (int dz = -18; dz <= 18; dz += 6) for (int dy = 1; dy <= 3; dy++) {
				BlockPos b = home.offset(dx, dy, dz);
				if (lvl.getBlockState(b).isAir()) {
					lvl.setBlock(b, Blocks.LIGHT.defaultBlockState(), 2);
					break;
				}
			}
		});
		attempt(ctx, sp, 'h', w, () -> explore(ctx, sp, w, kit));
		attempt(ctx, sp, 'x', w, () -> strike(ctx, sp, w, kit));
		attempt(ctx, sp, 'a', w, () -> armour(ctx, sp, w, kit));
		attempt(ctx, sp, 'c', w, () -> station(ctx, sp, w, kit));
		attempt(ctx, sp, 'n', w, () -> person(ctx, sp, w, kit));
		attempt(ctx, sp, 'j', w, () -> journal(ctx, sp, w, kit));
		attempt(ctx, sp, 'w', w, () -> wonder(ctx, sp, w, kit));
		if (take('i') || take('v') || take('b') || take('f')) {
			BlockPos[] a = new BlockPos[1];
			// the arena and its boss (woken with its introduction when i is filmed, out of frame for v and b alone)
			attempt(ctx, sp, 'i', w, take('i') || take('v') || take('b') || take('f'), () -> {
				atHome(ctx, sp, 0f);
				a[0] = arena(s, w);
				if (take('i') || take('v') || take('b')) bossIntro(ctx, sp, w, a[0], take('i'));
			});
			if (a[0] != null) {
				attempt(ctx, sp, 'v', w, () -> orbit(ctx, sp, w, a[0]));
				attempt(ctx, sp, 'b', w, () -> attacks(ctx, sp, w, a[0]));
				if (w > 0) attempt(ctx, sp, 'f', w, () -> {
					// the boss leaves without dying: the Unfinished's death would end the cycle on screen
					s.runOnServer(srv -> { var b = boss(srv, BOSSES[w]); if (b != null) b.discard(); });
					fight(ctx, sp, w, a[0]);
				});
			}
		}
		if (w == 0) {
			attempt(ctx, sp, 'p', w, () -> seed(ctx, sp, true));
			attempt(ctx, sp, 's', w, () -> seed(ctx, sp, false));
			attempt(ctx, sp, 'u', w, () -> places(ctx, sp));
		}
		if (w > 0) leave(ctx, sp);
		else {
			camera(ctx, CameraType.FIRST_PERSON);
			s.runCommand("kill @e[type=!player]");
			s.runCommand("effect clear @a");
		}
	}

	/** Runs one take when it is asked for; a failure is logged, the stage put back and the next take goes on. */
	private static void attempt(ClientGameTestContext ctx, TestSingleplayerContext sp, char take, int w, Runnable body) {
		attempt(ctx, sp, take, w, take(take), body);
	}

	private static void attempt(ClientGameTestContext ctx, TestSingleplayerContext sp, char take, int w, boolean run, Runnable body) {
		if (!run) return;
		long t0 = System.nanoTime();
		try {
			body.run();
		} catch (Skip e) {
			Matriochka.LOG.warn("[worldfilm] world {} take {} skipped: {}", w, take, e.getMessage());
		} catch (Throwable e) {
			Matriochka.LOG.warn("[worldfilm] world {} take {} failed: {}", w, take, e.toString(), e);
		}
		reset(ctx, sp);
		Matriochka.LOG.info("[worldfilm] world {} take {}: {} s", w, take, (System.nanoTime() - t0) / 1_000_000_000L);
	}

	/** A take that cannot be filmed in this world. */
	private static final class Skip extends RuntimeException {
		Skip(String why) {
			super(why);
		}
	}

	private static void reset(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		ctx.runOnClient(mc -> {
			EpicPlay.release(mc);
			mc.options.keyUse.setDown(false);
			mc.options.keyAttack.setDown(false);
			if (mc.player != null && mc.getCameraEntity() != mc.player) mc.setCameraEntity(mc.player);
			if (mc.player != null && McClient.screen(mc) != null) mc.player.closeContainer();
		});
		ctx.setScreen(() -> null);
		camera(ctx, CameraType.FIRST_PERSON);
		hud(ctx, false);
		hudScale(ctx, 1f);
		s.runCommand("gamemode survival @a");
		step(ctx, 2);
	}

	/** Back where the world was entered, facing the way the player came in, nothing else around, empty-handed. */
	private static void atHome(ClientGameTestContext ctx, TestSingleplayerContext sp, float pitch) {
		var s = sp.getServer();
		s.runCommand("kill @e[type=!player]");
		s.runCommand("gamemode survival @a");
		s.runCommand("clear @a");
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.teleportTo((ServerLevel) p.level(), home.getX() + 0.5, home.getY(), home.getZ() + 0.5, Set.of(), homeYaw, pitch, false);
			p.setDeltaMovement(Vec3.ZERO);
			p.getInventory().setSelectedSlot(0);
		});
		step(ctx, 4);
	}

	private static void dress(ServerPlayer p, Kit kit) {
		for (Item it : kit.armour()) {
			ItemStack st = new ItemStack(it);
			EquipmentSlot slot = it == ModContent.item("pearl_snorkel") ? EquipmentSlot.HEAD : slotOf(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(it).getPath());
			if (slot != null) p.setItemSlot(slot, st);
		}
		if (kit.weapon() != null) {
			p.getInventory().setItem(0, new ItemStack(kit.weapon()));
			p.getInventory().setSelectedSlot(0);
		}
	}

	private static EquipmentSlot slotOf(String id) {
		if (id.endsWith("_helmet")) return EquipmentSlot.HEAD;
		if (id.endsWith("_chestplate")) return EquipmentSlot.CHEST;
		if (id.endsWith("_leggings")) return EquipmentSlot.LEGS;
		if (id.endsWith("_boots")) return EquipmentSlot.FEET;
		return null;
	}

	/** A point dist blocks ahead of home along the way the player faces, at the given height offset. */
	private static Vec3 ahead(double dist, double side, double up) {
		double yaw = Math.toRadians(homeYaw);
		double fx = -Math.sin(yaw), fz = Math.cos(yaw);
		return new Vec3(home.getX() + 0.5 + fx * dist - fz * side, home.getY() + up, home.getZ() + 0.5 + fz * dist + fx * side);
	}

	/**
	 * The way from home with the most open ground ahead (sixteen headings, up to 24 blocks walked, no step higher
	 * than one block, no wall, no deep water), so the takes that look ahead do not look into a hill; the arrival heading
	 * when it is as good. Returns the heading and how many blocks it runs.
	 */
	private static float[] openYaw(ServerLevel lvl, int w, BlockPos from, float arrival) {
		float best = arrival;
		int bestRun = -1;
		for (int k = 0; k <= 16; k++) {
			float yaw = k == 0 ? arrival : (k - 1) * 22.5f;
			double fx = -Math.sin(Math.toRadians(yaw)), fz = Math.cos(Math.toRadians(yaw));
			int y = from.getY(), run = 0;
			for (int d = 1; d <= 24; d++) {
				double x = from.getX() + 0.5 + fx * d, z = from.getZ() + 0.5 + fz * d;
				int g = ground(lvl, w, x, z, y);
				BlockPos feet = BlockPos.containing(x, g, z);
				if (Math.abs(g - y) > 1 || !room(lvl, feet) || !swim && !lvl.getFluidState(feet.above()).isEmpty() || Worlds.ceiling(w) && !covered(lvl, feet)) break;
				y = g;
				run = d;
			}
			if (run > bestRun) {
				bestRun = run;
				best = yaw;
			}
		}
		return new float[]{best, bestRun};
	}

	/** The ground under x, z near height y: the highest place a player can stand, from three blocks above to six below, else y. */
	private static int ground(ServerLevel lvl, int w, double x, double z, int y) {
		if (swim && room(lvl, BlockPos.containing(x, y, z))) return y;
		BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos(Mth.floor(x), y + 3, Mth.floor(z));
		for (int k = 0; k < 10; k++, m.move(Direction.DOWN)) if (room(lvl, m)) return m.getY();
		return y;
	}

	// ---------------------------------------------------------------- h: exploring
	/** H: first person, the HUD on, walking and turning; the world's meter climbs (World 7: the breath runs out). */
	private static void explore(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		var s = sp.getServer();
		atHome(ctx, sp, 4f);
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			dress(p, kit);
			// the hotbar carries the world: its weapon, its station, its resources
			int slot = 1;
			if (kit.station() != null) p.getInventory().setItem(slot++, new ItemStack(ModContent.block(kit.station()).asItem()));
			for (Defs.ItemDef d : Content.ITEMS) {
				if (slot > 5 || d.world() != w || !List.of("resource", "gem", "ingot", "dust", "consumable").contains(d.kind())) continue;
				p.getInventory().setItem(slot++, new ItemStack(ModContent.item(d.id()), 8 + slot * 3));
			}
		});
		String gauge = switch (w) {
			case 1 -> "toxin";
			case 2 -> "heat";
			case 5 -> "noise";
			case 7 -> "oxygen";
			default -> null;
		};
		float from = w == 7 ? 100 : w == 5 ? 4 : 12, to = w == 7 ? 52 : w == 5 ? 46 : 58;
		camera(ctx, CameraType.FIRST_PERSON);
		hudScale(ctx, 1f);
		hud(ctx, true);
		step(ctx, 16);
		// over the sky islands of World 4 the walk stays short, so it does not end in the void
		// the walk follows the way found open from home (no wall, no drop), the ground's height smoothed under it
		double len = Math.max(0, Math.min(16, open - 3.5));
		double[] heights = s.computeOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			double[] hs = new double[(int) Math.ceil(len) + 2];
			int y = home.getY();
			for (int d = 0; d < hs.length; d++) {
				Vec3 v = ahead(d, 0, 0);
				y = ground(lvl, w, v.x, v.z, y);
				hs[d] = y;
			}
			return hs;
		});
		double[] eased = {home.getY()};
		for (int k = 0; k < 100; k++) {
			int kk = k;
			if (gauge != null) {
				float v = from + (to - from) * Math.min(1f, k / 90f);
				s.runOnServer(srv -> {
					PlayerState ps = PlayerState.of(player(srv));
					ps.setGauge(gauge, v);
					ps.sync();
				});
			}
			// a walking pace that sets off and slows at the end, the head turning a little from side to side
			double t = Math.max(0, (k - 6) / 93.0);
			double d = len * (t * t * (3 - 2 * t) * 0.5 + t * 0.5);
			int di = (int) Math.floor(d);
			double target = heights[Math.min(heights.length - 1, di)] + (heights[Math.min(heights.length - 1, di + 1)] - heights[Math.min(heights.length - 1, di)]) * (d - di);
			eased[0] += (target - eased[0]) * 0.35;
			double y = eased[0];
			float yaw = homeYaw + 9f * (float) Math.sin(kk / 100.0 * Math.PI * 0.9);
			float pitch = 4f - 6f * kk / 100f;
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				Vec3 v = ahead(d, 0, 0);
				p.teleportTo((ServerLevel) p.level(), v.x, y, v.z, Set.of(), yaw, pitch, false);
				p.setDeltaMovement(Vec3.ZERO);
			});
			if (k % 10 == 0) s.runOnServer(Film::clearBad);
			step(ctx, 1);
			frame(ctx, f("h_" + tag(w), k));
		}
		ctx.runOnClient(EpicPlay::release);
		hud(ctx, false);
	}

	// ---------------------------------------------------------------- x: the weapon
	/** X: from behind the player, the world's weapon against three of its creatures, weakened so each falls in a blow or two. */
	private static void strike(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		if (kit.weapon() == null) throw new Skip("no weapon");
		List<Defs.MobDef> mobs = creatures(w);
		if (mobs.isEmpty()) throw new Skip("no creature");
		var s = sp.getServer();
		atHome(ctx, sp, 10f);
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel lvl = (ServerLevel) p.level();
			dress(p, kit);
			double dmg = Math.max(4, p.getAttributeValue(Attributes.ATTACK_DAMAGE));
			double[][] at = {{4.2, -2.2}, {5.4, 0.4}, {4.6, 2.6}};
			// the giants of World 10 stand farther off, and the camera with them
			double big = 1;
			for (Defs.MobDef m : mobs) big = Math.max(big, m.scale() / 1.3);
			// the giants get a level stage of the world's ground ahead of the player, out of the water and the dips
			if (big > 1.5) {
				BlockState floor = lvl.getBlockState(home.below());
				for (int dx = -16; dx <= 16; dx++) for (int dz = -16; dz <= 16; dz++) {
					if (dx * dx + dz * dz > 256) continue;
					BlockPos c = home.offset(dx, 0, dz);
					for (int dy = 0; dy <= 14; dy++) lvl.setBlock(c.above(dy), Blocks.AIR.defaultBlockState(), 2 | 16);
					for (int dy = 1; dy <= 4; dy++) lvl.setBlock(c.below(dy), floor, 2 | 16);
				}
			}
			for (int i = 0; i < mobs.size(); i++) {
				Vec3 v = ahead(at[i][0] * (1 + (big - 1) * 0.6), at[i][1] * (1 + (big - 1) * 0.6), 0);
				Entity e = ModContent.entity(mobs.get(i).id()).create(lvl, EntitySpawnReason.COMMAND);
				if (!(e instanceof Mob m)) continue;
				m.snapTo(v.x, ground(lvl, w, v.x, v.z, home.getY()), v.z, homeYaw + 180f, 0f);
				m.setYHeadRot(homeYaw + 180f);
				m.setPersistenceRequired();
				lvl.addFreshEntity(m);
				m.setHealth((float) Math.min(m.getMaxHealth(), dmg * 1.5));
				// they stay where they stand, turning to the player, and do not run off the shot
				m.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, -1, 3, false, false));
				// the giants stand still: walking up to the player they would wall off the camera
				if (big > 1.5) m.setNoAi(true);
			}
			// the camera stands farther back than the game's four blocks, so the player and the creatures share the frame
			var dist = p.getAttribute(Attributes.CAMERA_DISTANCE);
			if (dist != null) dist.setBaseValue(6.5 * (1 + (big - 1) * 0.4));
			// the dark worlds get a little light round the fight (invisible light blocks), so the player reads
			if (w == 3 || w == 5) {
				for (int dx = -6; dx <= 6; dx += 4) for (int dz = -2; dz <= 8; dz += 5) {
					Vec3 v = ahead(dz, dx, 2);
					BlockPos b = BlockPos.containing(v);
					if (lvl.getBlockState(b).isAir()) lvl.setBlock(b, Blocks.LIGHT.defaultBlockState(), 3);
				}
			}
		});
		camera(ctx, CameraType.THIRD_PERSON_BACK);
		step(ctx, 6);
		for (int k = 0; k < 140; k++) {
			int ff = k;
			if (k >= 8) ctx.runOnClient(mc -> EpicPlay.play(mc, null, ff, false));
			if (k % 6 == 0) s.runOnServer(Film::clearBad);
			step(ctx, 1);
			frame(ctx, f("x_" + tag(w), k));
		}
		ctx.runOnClient(EpicPlay::release);
		s.runOnServer(srv -> {
			var dist = player(srv).getAttribute(Attributes.CAMERA_DISTANCE);
			if (dist != null) dist.setBaseValue(4.0);
		});
	}

	// ---------------------------------------------------------------- a: the armour
	/**
	 * A: a stand-in for the player (a mannequin, the player's own model, which the client does not draw while it is
	 * the camera) in the world's armour with its weapon, the camera circling it slowly.
	 */
	private static void armour(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		if (kit.armour().isEmpty()) throw new Skip("no armour");
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		StringBuilder eq = new StringBuilder();
		for (Item it : kit.armour()) {
			String id = net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(it).toString();
			EquipmentSlot slot = it == ModContent.item("pearl_snorkel") ? EquipmentSlot.HEAD : slotOf(id);
			if (slot == null) continue;
			eq.append(eq.isEmpty() ? "" : ",").append(slot.getName()).append(":{id:\"").append(id).append("\",count:1}");
		}
		if (kit.weapon() != null) eq.append(eq.isEmpty() ? "" : ",").append("mainhand:{id:\"").append(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(kit.weapon())).append("\",count:1}");
		Vec3 feet = s.computeOnServer(srv -> player(srv).position());
		s.runCommand(String.format(Locale.ROOT, "execute in %s run summon minecraft:mannequin %.2f %.2f %.2f {Rotation:[%.1ff,0f],hide_description:1b,immovable:1b,Tags:[\"wf_stand\"],equipment:{%s}}",
			s.computeOnServer(srv -> player(srv).level().dimension().identifier().toString()), feet.x, feet.y, feet.z, homeYaw, eq));
		boolean there = s.computeOnServer(srv -> !player(srv).level().getEntitiesOfClass(LivingEntity.class, player(srv).getBoundingBox().inflate(3), e -> e.entityTags().contains("wf_stand")).isEmpty());
		if (!there) throw new Skip("no mannequin");
		// the arc (of four, round the player) with the most room, and in a narrow hall a tighter circle, so the camera
		// stays inside the walls
		double[] arc = s.computeOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			double[] best = {40, 0};
			for (double start : new double[]{40, 130, 220, 310}) {
				double r = 3.1;
				for (int k = 0; k <= 100; k += 5) {
					double ang = Math.toRadians(homeYaw + start - k * 0.95);
					Vec3 dir = new Vec3(-Math.sin(ang), 0.5 / 3.1, Math.cos(ang));
					for (double d = 0.4; d < r + 0.4; d += 0.1) {
						BlockPos b = BlockPos.containing(feet.add(0, 1.05, 0).add(dir.scale(d)));
						if (!lvl.getBlockState(b).getCollisionShape(lvl, b).isEmpty()) {
							r = Math.max(1.5, d - 0.4);
							break;
						}
					}
				}
				if (r > best[1] + 0.05) best = new double[]{start, r};
			}
			return best;
		});
		double from = arc[0], radius = arc[1];
		s.runCommand("gamemode spectator @a");
		camera(ctx, CameraType.FIRST_PERSON);
		for (int k = -10; k < 100; k++) {
			int kk = Math.max(0, k);
			s.runOnServer(srv -> {
				// a quarter turn round the player, slowly, a little above the shoulders
				double ang = Math.toRadians(homeYaw + from - kk * 0.95);
				double r = radius - kk * 0.004;
				look(srv, new Vec3(feet.x - Math.sin(ang) * r, feet.y + 1.05 + r * 0.5 / 3.1, feet.z + Math.cos(ang) * r), feet.add(0, 1.05, 0));
			});
			step(ctx, 1);
			if (k >= 0) frame(ctx, f("a_" + tag(w), k));
		}
		s.runCommand("kill @e[tag=wf_stand]");
	}

	// ---------------------------------------------------------------- c: the station
	/** C: the station set down before the player, opened with a right click, the cursor over three recipes, one pulled. */
	private static void station(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		if (kit.station() == null) throw new Skip("no station");
		var s = sp.getServer();
		atHome(ctx, sp, 30f);
		List<Recipes.Recipe> recipes = Recipes.of(kit.station());
		BlockPos pos = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel lvl = (ServerLevel) p.level();
			Direction face = Direction.fromYRot(homeYaw);
			BlockPos two = home.relative(face, 2);
			BlockPos at = new BlockPos(two.getX(), ground(lvl, w, two.getX() + 0.5, two.getZ() + 0.5, home.getY()), two.getZ());
			for (int dy = 0; dy <= 2; dy++) lvl.setBlock(at.above(dy), Blocks.AIR.defaultBlockState(), 3);
			if (lvl.getBlockState(at.below()).isAir() || !lvl.getFluidState(at.below()).isEmpty()) lvl.setBlock(at.below(), Blocks.SMOOTH_STONE.defaultBlockState(), 3);
			BlockState st = ModContent.block(kit.station()).defaultBlockState();
			if (st.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) st = st.setValue(BlockStateProperties.HORIZONTAL_FACING, face.getOpposite());
			lvl.setBlock(at, st, 3);
			// what the first recipe needs, so its drawer can be pulled
			if (!recipes.isEmpty()) for (Recipes.Ing ing : recipes.getFirst().inputs()) {
				Item it = Stations.resolve(ing.id());
				if (it != null) p.getInventory().add(new ItemStack(it, Math.min(64, ing.count())));
			}
			look(srv, p.getEyePosition(), Vec3.atCenterOf(at));
			return at;
		});
		camera(ctx, CameraType.FIRST_PERSON);
		step(ctx, 4);
		int i = 0;
		cur = new double[]{W * 0.68, H * 0.62};
		ctx.getInput().setCursorPos(cur[0], cur[1]);
		i = still(ctx, "c_" + tag(w), i, 12);
		// a real right click on the station, the server's use when the click misses
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(true));
		i = still(ctx, "c_" + tag(w), i, 1);
		ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
		i = still(ctx, "c_" + tag(w), i, 2);
		if (!open(ctx)) {
			Matriochka.LOG.warn("[worldfilm] the click missed the station, opening it from the server");
			s.runOnServer(srv -> use(player(srv), pos, Direction.fromYRot(homeYaw).getOpposite()));
			i = still(ctx, "c_" + tag(w), i, 2);
		}
		if (!open(ctx)) {
			s.runCommand("execute as @p at @s run matriochka station " + kit.station());
			i = still(ctx, "c_" + tag(w), i, 2);
		}
		if (!open(ctx)) throw new Skip("the station did not open");
		// the drawers (or the station's pieces) come in
		i = still(ctx, "c_" + tag(w), i, 20);
		int n = ctx.computeOnClient(mc -> ((StationScreen) McClient.screen(mc)).recipeCount());
		int[] picks = n >= 3 ? new int[]{1, 2, n > 3 ? 3 : 0} : n == 2 ? new int[]{1, 0} : new int[]{0};
		for (int pick : picks) {
			int[] to = ctx.computeOnClient(mc -> McClient.screen(mc) instanceof StationScreen st ? st.recipeCenter(pick) : null);
			if (to == null) continue;
			i = glide(ctx, "c_" + tag(w), i, to, 12);
			i = still(ctx, "c_" + tag(w), i, 14);
		}
		int[] first = ctx.computeOnClient(mc -> McClient.screen(mc) instanceof StationScreen st ? st.recipeCenter(0) : null);
		if (first != null) {
			i = glide(ctx, "c_" + tag(w), i, first, 10);
			i = still(ctx, "c_" + tag(w), i, 6);
			i = clickAt(ctx, "c_" + tag(w), i);
			i = still(ctx, "c_" + tag(w), i, 22);
		}
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		step(ctx, 6);
		s.runOnServer(srv -> ((ServerLevel) player(srv).level()).setBlock(pos, Blocks.AIR.defaultBlockState(), 3));
	}

	private static boolean open(ClientGameTestContext ctx) {
		return ctx.computeOnClient(mc -> McClient.screen(mc) instanceof StationScreen);
	}

	// ---------------------------------------------------------------- n: a person
	/** N: one of the world's people, the player walking up to it; at greeting distance it tells the wonder's rumour. */
	private static void person(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		if (kit.npc() == null) throw new Skip("no people");
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		double start = Math.max(5.2, Math.min(7.5, open - 0.5));
		Vec3 spot = ahead(start, 0, 0);
		int npcId = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel lvl = (ServerLevel) p.level();
			Entity e = ModContent.entity(kit.npc()).create(lvl, EntitySpawnReason.COMMAND);
			if (!(e instanceof MatrioNpc npc)) return -1;
			npc.snapTo(spot.x, ground(lvl, w, spot.x, spot.z, home.getY()), spot.z, homeYaw + 180f, 0f);
			npc.setYHeadRot(homeYaw + 180f);
			npc.setYBodyRot(homeYaw + 180f);
			npc.setNoAi(true);
			lvl.addFreshEntity(npc);
			return npc.getId();
		});
		if (npcId < 0) throw new Skip("the person did not come");
		camera(ctx, CameraType.FIRST_PERSON);
		step(ctx, 6);
		boolean said = false;
		for (int k = 0; k < 90; k++) {
			// eased from start blocks away to 3; the line comes as the player reaches the greeting distance
			double t = Math.min(1.0, k / 46.0);
			t = t * t * (3 - 2 * t);
			double d = start - (start - 3.0) * t;
			boolean say = !said && d <= 4.7;
			said |= say;
			double dd = d;
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				ServerLevel lvl = (ServerLevel) p.level();
				if (!(lvl.getEntity(npcId) instanceof MatrioNpc npc)) return;
				Vec3 head = npc.position().add(0, npc.getBbHeight() * 0.92, 0);
				Vec3 from = ahead(start - dd, 0, 0);
				double y = ground(lvl, w, from.x, from.z, home.getY()) + p.getEyeHeight();
				look(srv, new Vec3(from.x, y, from.z), head.add(0, 0.45, 0));
				if (say) {
					Component line = rumour(lvl, p, npc, w);
					if (line != null) npc.say(line, 200);
				}
			});
			step(ctx, 1);
			frame(ctx, f("n_" + tag(w), k));
		}
	}

	/** The rumour of World w's wonder as its people tell it (the Surface's Peddler: its greeting). */
	private static Component rumour(ServerLevel lvl, ServerPlayer p, MatrioNpc npc, int w) {
		if (w == 0) return Component.translatable("npc.matriochka." + npc.def.id() + ".0");
		Component told = null;
		try {
			told = Rumors.tell(lvl, p, npc.blockPosition(), w);
		} catch (RuntimeException e) {
			Matriochka.LOG.warn("[worldfilm] rumour of world {}: {}", w, e.toString());
		}
		if (told != null) return told;
		return Component.translatable("npc.matriochka.rumor." + w, Component.translatable("rumor.matriochka.dir.north"), Component.translatable("rumor.matriochka.dist.near"));
	}

	// ---------------------------------------------------------------- j: the Journal
	/** J: the Journal open on the world's card, the cursor over one item for its tooltip, then the card turned to the map. */
	private static void journal(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		// the map inked by hand round the player: a winding walk and a few of the world's places
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			java.util.Random r = new java.util.Random(7 + w);
			int bx = p.getBlockX(), bz = p.getBlockZ();
			int x = 0, z = 0;
			for (int k = 0; k < 420; k++) {
				Atlas.mark(p, w, bx + x * 64, bz + z * 64);
				if (r.nextInt(3) == 0) Atlas.mark(p, w, bx + (x + 1) * 64, bz + z * 64);
				if (r.nextInt(3) == 0) Atlas.mark(p, w, bx + x * 64, bz + (z + 1) * 64);
				switch (r.nextInt(5)) {
					case 0 -> x++;
					case 1 -> x--;
					case 2 -> z++;
					case 3 -> z--;
					default -> x += Integer.signum(-x);
				}
				x = Math.max(-14, Math.min(14, x));
				z = Math.max(-14, Math.min(14, z));
			}
			int[][] at = {{-200, -180}, {260, 40}, {-60, 300}, {120, -260}, {-320, 120}, {40, -60}};
			int n = 0;
			for (Defs.StructureDef d : Content.STRUCTURES) {
				if (d.world() != w || n >= at.length) continue;
				if (d.role().equals("wonder")) Atlas.markFound(p, w, d.id(), bx + 40, bz - 60);
				else if (n < at.length - 1) Atlas.markFound(p, w, d.id(), bx + at[n][0], bz + at[n][1]);
				n++;
			}
			PlayerState.of(p).sync();
		});
		step(ctx, 4);
		cur = new double[]{W * 0.82, H * 0.74};
		ctx.getInput().setCursorPos(cur[0], cur[1]);
		ctx.setScreen(() -> {
			JournalScreen j = new JournalScreen(false).tab(3);
			j.openCard(w);
			return j;
		});
		int i = 0;
		String t = "j_" + tag(w);
		i = still(ctx, t, i, 12);
		if (!ctx.computeOnClient(mc -> McClient.screen(mc) instanceof JournalScreen)) throw new Skip("the Journal did not open");
		int[] row = ctx.computeOnClient(mc -> ((JournalScreen) McClient.screen(mc)).cardRowCenter(1));
		i = glide(ctx, t, i, row, 12);
		i = still(ctx, t, i, 24);
		int[] btn = ctx.computeOnClient(mc -> ((JournalScreen) McClient.screen(mc)).mapButtonCenter());
		i = glide(ctx, t, i, btn, 10);
		i = still(ctx, t, i, 2);
		i = clickAt(ctx, t, i);
		i = still(ctx, t, i, 6);
		// the cursor leaves the page so the map shows whole
		i = glide(ctx, t, i, new int[]{(int) (W * 0.88 / 3), (int) (H * 0.9 / 3)}, 10);
		i = still(ctx, t, i, 100 - i);
		ctx.setScreen(() -> null);
	}

	// ---------------------------------------------------------------- the Surface: the Seed and its places
	/**
	 * P (first person) or S (a camera circling low): the Seed of World 1 planted in tilled World Soil, its ritual, the
	 * World Block it hatches into; in P the player then steps inside (as TiktokCapture's takes, in landscape).
	 */
	private static void seed(ClientGameTestContext ctx, TestSingleplayerContext sp, boolean pov) {
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		s.runCommand("execute as @p run matriochka progression set 1");
		BlockPos garden = garden(ctx, sp);
		try {
			if (pov) seedPov(ctx, sp, garden, "p_w00");
			else seedOrbit(ctx, sp, garden, "s_w00");
		} finally {
			s.runCommand("execute as @p run matriochka progression set 10");
			s.runCommand("gamemode survival @a");
			step(ctx, 10);
		}
	}

	/**
	 * U: the Surface's own places set down side by side with the server's command (the Artisan's old cabin, the
	 * Peddler's stall, the fallen giant doll), and a slow aerial pass along the row, about fifty frames over each.
	 */
	private static void places(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		s.runCommand("gamemode spectator @a");
		String[] ids = {"artisan_cabin", "peddler_stall", "fallen_doll"};
		// off to the side of home, away from the arena and the garden
		int bx = home.getX() + 140, bz = home.getZ() - 120;
		int[] tops = new int[ids.length];
		for (int i = 0; i < ids.length; i++) {
			int x = bx + i * 60, k = i;
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				p.teleportTo(srv.overworld(), x + 0.5, 150, bz - 30.5, Set.of(), 0f, 40f, false);
			});
			step(ctx, 30);
			chunks(ctx, sp);
			s.runCommand("execute in minecraft:overworld positioned " + x + " 0 " + bz + " run place structure matriochka:" + ids[i] + " ~ ~ ~");
			tops[i] = s.computeOnServer(srv -> srv.overworld().getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, bz));
			Matriochka.LOG.info("[worldfilm] {} placed at {} {} {}", ids[k], x, tops[k], bz);
		}
		s.runOnServer(srv -> player(srv).teleportTo(srv.overworld(), bx - 24.5, tops[0] + 18, bz - 26.5, Set.of(), 0f, 30f, false));
		step(ctx, 30);
		chunks(ctx, sp);
		// the camera tracks along the row, high and three-quarters, its height easing between the places'
		double[] eye = {tops[0] + 17};
		for (int k = 0; k < 160; k++) {
			double x = bx - 22 + k * (120 + 44) / 160.0;
			int near = Math.max(0, Math.min(ids.length - 1, (int) Math.round((x - bx) / 60.0)));
			eye[0] += (tops[near] + 17 - eye[0]) * 0.05;
			double ex = x, ey = eye[0];
			s.runOnServer(srv -> look(srv, new Vec3(ex, ey, bz - 26), new Vec3(ex + 7, ey - 15, bz)));
			step(ctx, 1);
			frame(ctx, f("u_w00", k));
		}
	}

	// ---------------------------------------------------------------- w: the wonder
	/** W: the wonder set down near the player, seen from the air, then its reliquary opened with the right cross key. */
	private static void wonder(ClientGameTestContext ctx, TestSingleplayerContext sp, int w, Kit kit) {
		if (kit.wonder() == null) throw new Skip("no wonder");
		var s = sp.getServer();
		atHome(ctx, sp, 0f);
		s.runCommand("gamemode spectator @a");
		boolean ceiling = Worlds.ceiling(w);
		// away from the arena (60 blocks ahead on z), 52 blocks from home: on the flattest and lowest of five spots,
		// so a hill does not swallow it (caves, the sky islands and the sea keep the first)
		int[] spot = s.computeOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			int[][] tries = {{0, -52}, {52, 0}, {-52, 0}, {37, -37}, {-37, -37}};
			if (ceiling || w == 2 || w == 4 || w == 7) return new int[]{home.getX(), home.getZ() - 52};
			int[] best = null;
			double bestScore = Double.MAX_VALUE;
			for (int[] t : tries) {
				int cx = home.getX() + t[0], cz = home.getZ() + t[1];
				double sum = 0, sq = 0;
				int n = 0;
				for (int dx = -24; dx <= 24; dx += 6) for (int dz = -24; dz <= 24; dz += 6) {
					int h = lvl.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, cx + dx, cz + dz);
					sum += h;
					sq += (double) h * h;
					n++;
				}
				double mean = sum / n, rough = Math.sqrt(Math.max(0, sq / n - mean * mean));
				double score = rough * 3 + (mean - home.getY()) * 0.5;
				if (score < bestScore) {
					bestScore = score;
					best = new int[]{cx, cz};
				}
			}
			return best;
		});
		int px = spot[0], pz = spot[1];
		// in the open (not over the sky islands), the hills round the site are cut down to the ground's middle height, their tops grassed over
		// with the site's own surface, so the wonder stands against open ground and sky
		if (!ceiling && w != 2 && w != 4 && w != 7) s.runOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			int sum = 0, n = 0;
			for (int dx = -30; dx <= 30; dx += 5) for (int dz = -30; dz <= 30; dz += 5) {
				sum += lvl.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, px + dx, pz + dz);
				n++;
			}
			int base = sum / n;
			int low = Integer.MAX_VALUE;
			BlockPos lowAt = new BlockPos(px, base, pz);
			for (int dx = -30; dx <= 30; dx += 5) for (int dz = -30; dz <= 30; dz += 5) {
				int h = lvl.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, px + dx, pz + dz);
				if (h < low) {
					low = h;
					lowAt = new BlockPos(px + dx, h - 1, pz + dz);
				}
			}
			// the world's own ground cover (its "top" block), else what the lowest ground round the site is made of
			BlockState top = lvl.getBlockState(lowAt);
			for (Defs.WorldDef d : Content.WORLDS) {
				if (d.n() != w) continue;
				try {
					top = ModContent.block(d.top()).defaultBlockState();
				} catch (IllegalArgumentException e) {
					Matriochka.LOG.warn("[worldfilm] no ground block {}", d.top());
				}
			}
			if (top.isAir() || !lvl.getFluidState(lowAt).isEmpty()) top = Blocks.GRASS_BLOCK.defaultBlockState();
			for (int dx = -44; dx <= 44; dx++) for (int dz = -44; dz <= 44; dz++) {
				if (dx * dx + dz * dz > 44 * 44) continue;
				int h = lvl.getHeight(Heightmap.Types.WORLD_SURFACE, px + dx, pz + dz);
				if (h <= base + 1) continue;
				for (int y = base + 1; y <= h; y++) lvl.setBlock(new BlockPos(px + dx, y, pz + dz), Blocks.AIR.defaultBlockState(), 2 | 16);
				lvl.setBlock(new BlockPos(px + dx, base, pz + dz), top, 2 | 16);
			}
		});
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.teleportTo((ServerLevel) p.level(), px + 0.5, home.getY() + (ceiling ? 2 : 30), pz - 30.5, Set.of(), 0f, 30f, false);
		});
		step(ctx, 40);
		chunks(ctx, sp);
		int[] rel = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel lvl = (ServerLevel) p.level();
			// as ShowcaseTest.structures: the server's own command, at the surface (in caves, a height of their own)
			int y = ceiling ? 30 + Math.floorMod((px >> 4) * 31 + (pz >> 4) * 17, 40) : w == 2 ? 64 : lvl.getHeight(Heightmap.Types.WORLD_SURFACE, px, pz);
			var src = srv.createCommandSourceStack().withLevel(lvl).withPosition(new Vec3(px, y, pz)).withSuppressedOutput();
			try {
				int r = srv.getCommands().getDispatcher().execute("place structure matriochka:" + kit.wonder() + " " + px + " " + y + " " + pz, src);
				Matriochka.LOG.info("[worldfilm] {} placed ({}) at {} {} {}", kit.wonder(), r, px, y, pz);
			} catch (Exception e) {
				Matriochka.LOG.warn("[worldfilm] {} not placed: {}", kit.wonder(), e.getMessage());
				return null;
			}
			var block = ModContent.block("reliquary");
			for (BlockPos bp : BlockPos.betweenClosed(px - 40, lvl.getMinY(), pz - 40, px + 40, lvl.getMaxY(), pz + 40)) {
				if (!lvl.getBlockState(bp).is(block)) continue;
				if (lvl.getBlockEntity(bp) instanceof DataBlockEntity be && be.data().getIntOr("world", 0) <= 0) {
					be.data().putInt("world", w);
					be.changed();
				}
				return new int[]{bp.getX(), bp.getY(), bp.getZ(), y};
			}
			return new int[]{px, y, pz, y, 0};
		});
		if (rel == null) throw new Skip("the wonder was not placed");
		boolean found = rel.length == 4;
		if (!found) Matriochka.LOG.warn("[worldfilm] no reliquary found in {}", kit.wonder());
		BlockPos relic = new BlockPos(rel[0], rel[1], rel[2]);
		// the orbit turns round the middle of the wonder, between where it was set down and its reliquary
		// (a wonder that finds its own floor, under the sea or in a cave, is centred on its reliquary's height)
		Vec3 mid = new Vec3((px + rel[0]) / 2.0 + 0.5, (rel.length == 4 ? rel[1] + 3.0 : rel[3] + 2.0), (pz + rel[2]) / 2.0 + 0.5);
		step(ctx, 20);
		chunks(ctx, sp);
		String t = "w_" + tag(w);
		// the orbit that sees the wonder best: of a few circles (low and close under World 2's rock roof and in
		// caves, wider and higher in the open), the one whose camera stays out of the rock with the clearest view
		double[] orbit = s.computeOnServer(srv -> {
			ServerLevel lvl = (ServerLevel) player(srv).level();
			// under the sea the water's fog hides what is far: the camera comes in just outside the wonder's walls
			double reach = 0;
			if (w == 7) for (int a = 0; a < 8; a++) {
				double ang = a * Math.PI / 4;
				int water = 0;
				for (double d = 1; d < 40 && water < 3; d += 1) {
					BlockPos b = BlockPos.containing(mid.add(Math.sin(ang) * d, 0, Math.cos(ang) * d));
					if (lvl.getBlockState(b).getCollisionShape(lvl, b).isEmpty()) water++;
					else {
						water = 0;
						reach = Math.max(reach, d);
					}
				}
			}
			double out = Math.max(20, Math.min(24, reach + 8));
			double[][] tries = w == 7 ? new double[][]{{out, out * 0.45}, {out, out * 0.6}, {out, out * 0.35}}
				: ceiling ? new double[][]{{15, 5}, {12, 4}, {10, 3}, {18, 7}, {8, 3}, {9, 6}, {7, 2}}
				: w == 2 ? new double[][]{{24, 9}, {18, 6}, {30, 12}, {14, 5}}
				: new double[][]{{34, 22}, {44, 30}, {54, 40}, {30, 36}, {42, 50}, {24, 16}};
			double[] best = tries[0];
			int bestHits = Integer.MAX_VALUE;
			for (double[] c : tries) {
				int hits = 0;
				for (int k = 0; k < 110; k += 5) {
					double ang = Math.toRadians(200 + k * 0.62);
					Vec3 eye = mid.add(Math.sin(ang) * c[0], c[1], Math.cos(ang) * c[0]);
					BlockPos e = BlockPos.containing(eye);
					if (!lvl.getBlockState(e).getCollisionShape(lvl, e).isEmpty()) hits += 20;
					Vec3 to = mid.subtract(eye);
					double len = to.length();
					for (double d = 0; d < len - 6; d += 0.5) {
						BlockPos b = BlockPos.containing(eye.add(to.scale(d / len)));
						if (!lvl.getBlockState(b).getCollisionShape(lvl, b).isEmpty()) hits++;
					}
				}
				if (hits < bestHits) {
					bestHits = hits;
					best = c;
				}
			}
			Matriochka.LOG.info("[worldfilm] wonder orbit radius {} height {} ({} blocks in the way)", best[0], best[1], bestHits);
			return best;
		});
		int i = 0;
		for (int k = 0; k < 110; k++) {
			int kk = k;
			s.runOnServer(srv -> {
				double ang = Math.toRadians(200 + kk * 0.62);
				double r = orbit[0] * (1 - kk * 0.0009);
				double up = orbit[1] * (1 - kk * 0.0018);
				look(srv, mid.add(Math.sin(ang) * r, up, Math.cos(ang) * r), mid.add(0, ceiling ? 0.5 : w == 7 ? 4 : 1.5, 0));
			});
			step(ctx, 1);
			frame(ctx, f(t, i++));
		}
		if (!found) throw new Skip("no reliquary, the orbit alone");
		// first person: a few steps up to the reliquary, the right cross key in hand
		Vec3 stand = s.computeOnServer(srv -> standBy((ServerLevel) player(srv).level(), relic));
		if (stand == null) throw new Skip("no room to stand by the reliquary");
		int key = Reliquary.keyFor(w);
		s.runCommand("gamemode survival @a");
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().clearContent();
			// the sea's pressure spares a diver in the world's suit
			if (w == 7) dress(p, kit);
			p.getInventory().setItem(0, new ItemStack(ModContent.item("cross_key_" + key)));
			p.getInventory().setSelectedSlot(0);
			look(srv, stand.add(0, p.getEyeHeight(), 0), Vec3.atCenterOf(relic));
		});
		camera(ctx, CameraType.FIRST_PERSON);
		hud(ctx, true);
		step(ctx, 3);
		// aimed a little over the reliquary's middle, where the relic springs out
		Vec3 target = Vec3.atCenterOf(relic).add(0, 0.45, 0);
		boolean clicked = false, opened = false;
		int openedAt = -1;
		for (int k = 0; k < 70; k++) {
			int kk = k;
			boolean near = ctx.computeOnClient(mc -> {
				var p = mc.player;
				if (p == null) return true;
				Vec3 to = target.subtract(p.getEyePosition());
				float yaw = (float) Math.toDegrees(Math.atan2(-to.x, to.z));
				float pitch = (float) -Math.toDegrees(Math.atan2(to.y, Math.sqrt(to.x * to.x + to.z * to.z)));
				p.setYRot(p.getYRot() + Mth.clamp(Mth.wrapDegrees(yaw - p.getYRot()), -6f, 6f));
				p.setYHeadRot(p.getYRot());
				p.setXRot(p.getXRot() + Mth.clamp(pitch - p.getXRot(), -4f, 4f));
				double flat = Math.sqrt(to.x * to.x + to.z * to.z);
				boolean close = flat < 3.0 || kk > 26;
				mc.options.keyUp.setDown(!close);
				mc.options.keyJump.setDown(!close && p.horizontalCollision);
				return close;
			});
			if (near && !clicked && k >= 6) {
				clicked = true;
				ctx.runOnClient(mc -> {
					EpicPlay.release(mc);
					mc.options.keyUse.setDown(true);
				});
			} else ctx.runOnClient(mc -> mc.options.keyUse.setDown(false));
			step(ctx, 1);
			frame(ctx, f(t, i++));
			if (clicked && !opened) {
				opened = s.computeOnServer(srv -> isOpen(srv, relic));
				if (opened) openedAt = k;
				else if (openedAt < 0 && k > 0) {
					Matriochka.LOG.warn("[worldfilm] the click missed the reliquary, opening it from the server");
					s.runOnServer(srv -> {
						use(player(srv), relic, Direction.UP);
					});
					opened = s.computeOnServer(srv -> isOpen(srv, relic));
					openedAt = k;
				}
				// the relic stays where it lands for the camera, nobody picks it up
				if (opened) s.runOnServer(srv -> {
					ServerLevel lvl = (ServerLevel) player(srv).level();
					for (ItemEntity it : lvl.getEntitiesOfClass(ItemEntity.class, new AABB(relic).inflate(3))) it.setPickUpDelay(400);
				});
			}
		}
		if (!opened) Matriochka.LOG.warn("[worldfilm] the reliquary of world {} stayed shut", w);
		ctx.runOnClient(EpicPlay::release);
		hud(ctx, false);
		// the relic goes back so the rumour can be told again on a later run of the same world
		s.runOnServer(srv -> {
			PlayerState ps = PlayerState.of(player(srv));
			ps.set("relic_" + w, false);
			ps.sync();
		});
	}

	private static boolean isOpen(MinecraftServer srv, BlockPos relic) {
		ServerPlayer p = player(srv);
		return p.level().getBlockEntity(relic) instanceof DataBlockEntity be && be.data().getBooleanOr("opened_" + p.getUUID(), false);
	}

	/** A place to stand four to six blocks from the reliquary, on the ground, with room for a player. */
	private static Vec3 standBy(ServerLevel lvl, BlockPos relic) {
		for (double d = 4.5; d <= 6.5; d += 1.0) {
			for (int a = 0; a < 16; a++) {
				double ang = a * Math.PI / 8;
				int x = Mth.floor(relic.getX() + 0.5 + Math.sin(ang) * d), z = Mth.floor(relic.getZ() + 0.5 + Math.cos(ang) * d);
				for (int dy = 0; dy >= -2; dy--) {
					BlockPos feet = new BlockPos(x, relic.getY() + dy, z);
					if (room(lvl, feet) && clear(lvl, feet, relic)) return Vec3.atBottomCenterOf(feet);
				}
				BlockPos up = new BlockPos(x, relic.getY() + 1, z);
				if (room(lvl, up) && clear(lvl, up, relic)) return Vec3.atBottomCenterOf(up);
			}
		}
		return null;
	}

	/** Under a roof: the halls of World 3 and the caves of World 5, not their tops open to the void. */
	private static boolean covered(ServerLevel lvl, BlockPos feet) {
		for (int dy = 2; dy <= 10; dy++) {
			BlockPos b = feet.above(dy);
			if (!lvl.getBlockState(b).getCollisionShape(lvl, b).isEmpty()) return true;
		}
		return false;
	}

	private static boolean room(ServerLevel lvl, BlockPos feet) {
		// under World 7's sea a player floats: open water is room enough
		if (swim && lvl.getBlockState(feet).getCollisionShape(lvl, feet).isEmpty() && !lvl.getFluidState(feet).isEmpty() && !lvl.getFluidState(feet.above()).isEmpty()) return true;
		return lvl.getBlockState(feet).getCollisionShape(lvl, feet).isEmpty() && lvl.getBlockState(feet.above()).getCollisionShape(lvl, feet.above()).isEmpty()
			&& !lvl.getBlockState(feet.below()).getCollisionShape(lvl, feet.below()).isEmpty();
	}

	/** Nothing solid on the straight walk from feet to the reliquary, at knee and head height. */
	private static boolean clear(ServerLevel lvl, BlockPos feet, BlockPos relic) {
		Vec3 a = Vec3.atBottomCenterOf(feet), b = Vec3.atBottomCenterOf(relic);
		int steps = (int) Math.ceil(a.distanceTo(b) * 2);
		for (int k = 1; k < steps - 1; k++) {
			Vec3 v = a.lerp(b, k / (double) steps);
			BlockPos at = BlockPos.containing(v.x, a.y + 0.5, v.z);
			BlockPos head = at.above();
			if (!lvl.getBlockState(at).getCollisionShape(lvl, at).isEmpty() && k < steps - 3) return false;
			if (!lvl.getBlockState(head).getCollisionShape(lvl, head).isEmpty()) return false;
		}
		return true;
	}
}
