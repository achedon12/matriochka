package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.TalentScreen;
import fr.achedon12.matriochka.client.TrialsScreen;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.replay.Trials;
import fr.achedon12.matriochka.replay.WorldEvents;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.structure.TrialStage;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Refuge;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.CameraType;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.zombie.Husk;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Photographs the replay content: ./gradlew runClientGameTest -Preplayshots. Shots rs_*.png: the new gear in hand and
 * in use (g), the Trials stage, clock and countdown (t), the Trials and Talent screens in English and German (u), the
 * world events (e) and the ten new structures in their worlds (s). -Ptakes=gu retakes only those parts.
 */
final class ReplayShots {
	private ReplayShots() {}

	private static final String TAKES = System.getProperty("matriochka.takes", "");
	private static final String[] GEAR = {"spore_bow", "magma_flail", "key_chain_whip", "storm_javelin", "lantern_shield", "tide_harpoon", "quake_pick"};

	private static boolean take(char c) {
		return TAKES.isEmpty() || TAKES.indexOf(c) >= 0;
	}

	private static void shot(ClientGameTestContext ctx, String name, boolean hud) {
		ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden() == hud) mc.gui.hud.toggle(); });
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
		ctx.runOnClient(mc -> { if (mc.gui.hud.isHidden()) mc.gui.hud.toggle(); });
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	private static void camera(ClientGameTestContext ctx, CameraType type) {
		ctx.runOnClient(mc -> mc.options.setCameraType(type));
	}

	private static void cursor(ClientGameTestContext ctx, double gx, double gy) {
		double scale = ctx.computeOnClient(mc -> mc.getWindow().getGuiScale());
		ctx.getInput().setCursorPos(gx * scale, gy * scale);
	}

	private static int[] gui(ClientGameTestContext ctx) {
		return ctx.computeOnClient(mc -> new int[]{mc.getWindow().getGuiScaledWidth(), mc.getWindow().getGuiScaledHeight()});
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			// the window at the shot's size: otherwise the interface is laid out for the small test window
			ctx.getInput().resizeWindow(1920, 1080);
			ctx.waitTicks(5);
			sp.getConnection().waitForChunksRender();
			ctx.setScreen(() -> null);
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule advance_weather false");
			s.runCommand("weather clear");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("gamerule show_death_messages false");
			s.runCommand("time set 6000");
			s.runCommand("difficulty normal");
			s.runCommand("gamemode survival @a");
			s.runCommand("effect give @a resistance infinite 4 true");
			s.runCommand("effect give @a regeneration infinite 4 true");
			s.runCommand("effect give @a saturation infinite 0 true");
			s.runCommand("execute as @p run matriochka progression set 10");
			s.runOnServer(srv -> {
				PlayerState ps = PlayerState.of(player(srv));
				ps.set("end_seal", true);
				ps.addSouls(3000);
				ps.sync();
			});
			ctx.waitTicks(40);
			if (take('g')) gear(ctx, sp);
			if (take('t')) trials(ctx, sp);
			if (take('u')) screens(ctx, sp);
			if (take('e')) events(ctx, sp);
			if (take('s')) structures(ctx, sp);
		}
	}

	// ---------------------------------------------------------------- gear
	private static final List<Entity> DUMMIES = new ArrayList<>();

	private static void clearing(MinecraftServer srv) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		BlockPos c = p.blockPosition();
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-14, 0, -14), c.offset(14, 8, 14))) level.setBlock(q, Blocks.AIR.defaultBlockState(), 2);
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-14, -1, -14), c.offset(14, -1, 14))) level.setBlock(q, Blocks.GRASS_BLOCK.defaultBlockState(), 2);
	}

	/** A still husk dz blocks north of the player, facing them. */
	private static void dummy(MinecraftServer srv, double dx, double dz, boolean ai) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		Husk z = net.minecraft.world.entity.EntityTypes.HUSK.create(level, EntitySpawnReason.COMMAND);
		z.setPos(p.getX() + dx, p.getY(), p.getZ() + dz);
		z.setNoAi(!ai);
		z.setYRot(180);
		z.setYHeadRot(180);
		z.setPersistenceRequired();
		z.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(200);
		z.setHealth(200);
		level.addFreshEntity(z);
		DUMMIES.add(z);
	}

	private static void clearDummies(MinecraftServer srv) {
		for (Entity e : DUMMIES) e.discard();
		DUMMIES.clear();
	}

	private static void hold(TestServerContext s, String id) {
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().setSelectedSlot(0);
			p.setItemInHand(InteractionHand.MAIN_HAND, id.isEmpty() ? ItemStack.EMPTY : new ItemStack(ModContent.item(id)));
		});
	}

	private static void face(TestServerContext s, double x, double y, double z, float yaw, float pitch) {
		s.runCommand(String.format(java.util.Locale.ROOT, "execute as @p at @s run tp @s %.2f %.2f %.2f %.1f %.1f", x, y, z, yaw, pitch));
	}

	private static void gear(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runOnServer(ReplayShots::clearing);
		double[] at = s.computeOnServer(srv -> new double[]{Math.floor(player(srv).getX()) + 0.5, player(srv).getY(), Math.floor(player(srv).getZ()) + 0.5});
		face(s, at[0], at[1], at[2], 180, 10);
		ctx.waitTicks(30);
		sp.getConnection().waitForChunksRender();
		// every item at rest, first person, with its icon in the hotbar
		for (String id : GEAR) {
			hold(s, id);
			ctx.waitTicks(40);
			shot(ctx, "rs_gear_" + id + "_hand", true);
		}
		// the icons, in the inventory, a tooltip open on the javelin
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().clearContent();
			for (int i = 0; i < GEAR.length; i++) p.getInventory().setItem(i, new ItemStack(ModContent.item(GEAR[i])));
			for (int i = 0; i < GEAR.length; i++) p.getInventory().setItem(9 + i, new ItemStack(ModContent.item(GEAR[i])));
		});
		ctx.waitTicks(10);
		ctx.setScreen(() -> new net.minecraft.client.gui.screens.inventory.InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
		ctx.waitTicks(10);
		int[] g = gui(ctx);
		// the hotbar row of the inventory: 176 x 166 panel, hotbar at y 142, slot 3 at x 8 + 3 * 18
		cursor(ctx, (g[0] - 176) / 2 + 8 + 3 * 18 + 8, (g[1] - 166) / 2 + 142 + 8);
		ctx.waitTicks(4);
		shot(ctx, "rs_gear_inventory", false);
		ctx.setScreen(() -> null);
		cursor(ctx, 2, 2);
		ctx.waitTicks(5);
		s.runOnServer(srv -> player(srv).getInventory().clearContent());

		// the Spore Bow drawn, then its arrow and spore cloud
		hold(s, "spore_bow");
		s.runOnServer(srv -> player(srv).getInventory().setItem(9, new ItemStack(Items.ARROW, 16)));
		face(s, at[0], at[1], at[2], 180, -2);
		ctx.waitTicks(10);
		ctx.getInput().holdKey(o -> o.keyUse);
		ctx.waitTicks(6);
		shot(ctx, "rs_gear_spore_bow_draw1", true);
		ctx.waitTicks(16);
		shot(ctx, "rs_gear_spore_bow_drawn", true);
		ctx.getInput().releaseKey(o -> o.keyUse);
		ctx.waitTicks(22);
		shot(ctx, "rs_gear_spore_bow_cloud", true);
		ctx.waitTicks(20);

		// the Magma Flail: three blows, the third bursts in a ring of flame
		s.runOnServer(srv -> dummy(srv, 0, -2.6, false));
		hold(s, "magma_flail");
		face(s, at[0], at[1], at[2], 180, 15);
		ctx.waitTicks(14);
		for (int i = 0; i < 3; i++) {
			ctx.getInput().pressKey(o -> o.keyAttack);
			ctx.waitTicks(3);
			if (i == 0) shot(ctx, "rs_gear_magma_flail_swing", true);
			if (i == 2) shot(ctx, "rs_gear_magma_flail_ring", true);
			ctx.waitTicks(i == 2 ? 2 : 20);
		}
		s.runOnServer(ReplayShots::clearDummies);
		ctx.waitTicks(20);
		camera(ctx, CameraType.THIRD_PERSON_FRONT);
		ctx.waitTicks(6);
		ctx.getInput().pressKey(o -> o.keyAttack);
		ctx.waitTicks(3);
		shot(ctx, "rs_gear_magma_flail_third", true);
		camera(ctx, CameraType.FIRST_PERSON);
		s.runOnServer(ReplayShots::clearDummies);
		ctx.waitTicks(20);

		// the Key Chain Whip lashing a husk 5 blocks away
		s.runOnServer(srv -> dummy(srv, 0, -5.5, false));
		hold(s, "key_chain_whip");
		face(s, at[0], at[1], at[2], 180, 10);
		ctx.waitTicks(16);
		ctx.getInput().pressKey(o -> o.keyAttack);
		ctx.waitTicks(2);
		shot(ctx, "rs_gear_key_chain_whip_lash", true);
		ctx.waitTicks(6);
		shot(ctx, "rs_gear_key_chain_whip_pull", true);
		s.runOnServer(ReplayShots::clearDummies);
		ctx.waitTicks(10);

		// the Storm Javelin: thrown, in flight, the lightning where it strikes
		s.runOnServer(srv -> dummy(srv, 0, -10, false));
		hold(s, "storm_javelin");
		face(s, at[0], at[1], at[2], 180, 2);
		ctx.waitTicks(16);
		ctx.getInput().pressKey(o -> o.keyUse);
		ctx.waitTicks(2);
		shot(ctx, "rs_gear_storm_javelin_flight", true);
		ctx.waitTicks(4);
		shot(ctx, "rs_gear_storm_javelin_strike", true);
		ctx.waitTicks(3);
		shot(ctx, "rs_gear_storm_javelin_lightning", true);
		ctx.waitTicks(20);
		shot(ctx, "rs_gear_storm_javelin_return", true);
		ctx.waitTicks(60);
		s.runOnServer(ReplayShots::clearDummies);
		s.runCommand("kill @e[type=minecraft:item]");
		s.runCommand("execute as @p at @s run fill ~-14 ~ ~-14 ~14 ~3 ~14 air replace fire");

		// the Lantern Shield raised, then a blow it stops, with its flare
		s.runOnServer(srv -> dummy(srv, 0, -1.8, false));
		hold(s, "lantern_shield");
		face(s, at[0], at[1], at[2], 180, 10);
		ctx.waitTicks(14);
		ctx.getInput().holdKey(o -> o.keyUse);
		ctx.waitTicks(12);
		shot(ctx, "rs_gear_lantern_shield_block", true);
		s.runOnServer(srv -> DUMMIES.getFirst().teleportTo(player(srv).getX() + 2.2, player(srv).getY(), player(srv).getZ() - 0.6));
		camera(ctx, CameraType.THIRD_PERSON_FRONT);
		ctx.waitTicks(4);
		shot(ctx, "rs_gear_lantern_shield_block_third", true);
		camera(ctx, CameraType.FIRST_PERSON);
		s.runOnServer(srv -> DUMMIES.getFirst().teleportTo(player(srv).getX(), player(srv).getY(), player(srv).getZ() - 1.8));
		ctx.waitTicks(4);
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			ServerLevel level = (ServerLevel) p.level();
			p.hurtServer(level, level.damageSources().mobAttack((LivingEntity) DUMMIES.getFirst()), 4f);
		});
		ctx.waitTicks(2);
		shot(ctx, "rs_gear_lantern_shield_flare", true);
		ctx.getInput().releaseKey(o -> o.keyUse);
		s.runOnServer(ReplayShots::clearDummies);
		ctx.waitTicks(10);

		// the Tide Harpoon dragging a husk back
		s.runOnServer(srv -> dummy(srv, 0, -9, true));
		hold(s, "tide_harpoon");
		face(s, at[0], at[1], at[2], 180, 4);
		ctx.waitTicks(16);
		ctx.getInput().pressKey(o -> o.keyUse);
		ctx.waitTicks(4);
		shot(ctx, "rs_gear_tide_harpoon_flight", true);
		ctx.waitTicks(5);
		shot(ctx, "rs_gear_tide_harpoon_hit", true);
		ctx.waitTicks(6);
		shot(ctx, "rs_gear_tide_harpoon_pull", true);
		ctx.waitTicks(50);
		s.runOnServer(ReplayShots::clearDummies);

		// the Quake Pick: used on the ground among three husks
		s.runOnServer(srv -> {
			dummy(srv, 2.5, -3, true);
			dummy(srv, -2.5, -3, true);
			dummy(srv, 0, -4.5, true);
		});
		hold(s, "quake_pick");
		face(s, at[0], at[1], at[2], 180, 55);
		ctx.waitTicks(16);
		ctx.getInput().pressKey(o -> o.keyUse);
		ctx.waitTicks(3);
		shot(ctx, "rs_gear_quake_pick_tremor", true);
		face(s, at[0], at[1], at[2], 180, 20);
		ctx.waitTicks(4);
		shot(ctx, "rs_gear_quake_pick_after", true);
		s.runOnServer(ReplayShots::clearDummies);
		hold(s, "");
		ctx.waitTicks(10);
	}

	// ---------------------------------------------------------------- trials
	private static void trials(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		hold(s, "");
		s.runOnServer(srv -> player(srv).getInventory().setItem(0, new ItemStack(ModContent.item("magma_flail"))));
		// World 1, fought to the end so the board and the titles have something to show
		s.runOnServer(srv -> Trials.start(player(srv), "w1"));
		ctx.setScreen(() -> null);
		ctx.waitTicks(30);
		shot(ctx, "rs_trial_countdown", true);
		ctx.waitTicks(20);
		shot(ctx, "rs_trial_countdown_2", true);
		ctx.waitTicks(80);
		shot(ctx, "rs_trial_w1_fight", true);
		camera(ctx, CameraType.THIRD_PERSON_BACK);
		ctx.waitTicks(2);
		shot(ctx, "rs_trial_w1_fight_third", true);
		camera(ctx, CameraType.FIRST_PERSON);
		// the HUD plaque moved to the top right and scaled up, then the top left at twice the size
		for (String corner : new String[]{"top_right", "top_left", "bottom_left"}) {
			ctx.runOnClient(mc -> {
				Comfort.get().hudScale = 2f;
				Comfort.get().hudCorner = corner;
				Comfort.changed();
			});
			ctx.waitTicks(10);
			shot(ctx, "rs_trial_hud_" + corner + "_x2", true);
		}
		ctx.runOnClient(mc -> {
			Comfort.get().hudScale = 1f;
			Comfort.get().hudCorner = "top_left";
			Comfort.changed();
		});
		for (int stage = 0; stage < 3; stage++) {
			s.runOnServer(ReplayShots::clearTrialStage);
			ctx.waitTicks(stage < 2 ? 20 : 10);
			if (stage == 0) shot(ctx, "rs_trial_between", true);
			ctx.waitTicks(stage < 2 ? 70 : 10);
			if (stage == 1) {
				ctx.waitTicks(30);
				shot(ctx, "rs_trial_w1_boss", true);
			}
		}
		ctx.waitTicks(10);
		shot(ctx, "rs_trial_done", true);
		ctx.waitTicks(140);

		// a player's view of the flooded World 7 stage and the Gauntlet's first stage
		for (String key : new String[]{"w7", "w4", "gauntlet"}) {
			s.runOnServer(srv -> Trials.start(player(srv), key));
			ctx.waitTicks(125);
			shot(ctx, "rs_trial_" + key + "_view", true);
			camera(ctx, CameraType.THIRD_PERSON_BACK);
			ctx.waitTicks(2);
			shot(ctx, "rs_trial_" + key + "_third", true);
			camera(ctx, CameraType.FIRST_PERSON);
			s.runOnServer(srv -> Trials.leave(player(srv)));
			ctx.waitTicks(60);
		}

		// wide views of the stage painted for several worlds, built away from the trials
		s.runCommand("gamemode spectator @a");
		s.runCommand("effect give @a night_vision infinite 0 true");
		int[] worlds = {0, 1, 2, 3, 5, 6, 7, 8, 9, 10};
		for (int i = 0; i < worlds.length; i++) {
			int w = worlds[i];
			int cx = (Trials.SLOTS + 2 + i) * Trials.SPACING, cy = Refuge.FLOOR_Y, cz = Trials.STAGE_Z;
			s.runCommand("execute in matriochka:refuge run tp @p " + cx + " " + (cy + 20) + " " + (cz - 34) + " facing " + cx + " " + cy + " " + (cz + 2));
			ctx.waitTicks(40);
			s.runOnServer(srv -> {
				ServerLevel level = srv.getLevel(Worlds.REFUGE);
				BlockPos c = new BlockPos(cx, cy, cz);
				var b = TrialStage.box(c);
				for (int x = b.minX() >> 4; x <= b.maxX() >> 4; x++)
					for (int z = b.minZ() >> 4; z <= b.maxZ() >> 4; z++) level.setChunkForced(x, z, true);
				TrialStage.build(level, c, w);
			});
			ctx.waitTicks(30);
			sp.getConnection().waitForChunksRender();
			ctx.waitTicks(10);
			shot(ctx, "rs_stage_w" + w + "_wide", false);
			s.runCommand("execute in matriochka:refuge run tp @p " + (cx + 9) + " " + (cy + 2.6) + " " + (cz - 13) + " facing " + cx + " " + (cy + 3) + " " + (cz + 6));
			ctx.waitTicks(20);
			sp.getConnection().waitForChunksRender();
			ctx.waitTicks(6);
			shot(ctx, "rs_stage_w" + w + "_floor", false);
		}
		s.runCommand("effect clear @a night_vision");
		s.runCommand("gamemode survival @a");
		s.runCommand("execute as @p run matriochka world leave");
		s.runCommand("effect give @a resistance infinite 4 true");
		s.runCommand("effect give @a regeneration infinite 4 true");
		ctx.waitTicks(60);
	}

	private static void clearTrialStage(MinecraftServer srv) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		for (Entity e : Trials.foes(p)) {
			if (e instanceof LivingEntity le) le.die(level.damageSources().playerAttack(p));
			e.discard();
		}
	}

	// ---------------------------------------------------------------- screens
	private static void screens(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			p.getInventory().clearContent();
			p.getInventory().add(new ItemStack(ModContent.item("shell_shard"), 7));
			ItemStack blade = new ItemStack(ModContent.item("season_scythe"));
			fr.achedon12.matriochka.gear.GearClasses.apply(blade, new fr.achedon12.matriochka.gear.GearClasses.Gear("berserker", 4, 0));
			p.setItemInHand(InteractionHand.MAIN_HAND, blade);
			PlayerState ps = PlayerState.of(p);
			// a few talents learnt, in two branches of the Berserker and one of the Guardian
			for (String id : new String[]{"berserker_heavy_hand", "berserker_bloodied", "berserker_cleaver", "berserker_quick_arm", "guardian_stout", "guardian_plated"}) ps.set("talent_" + id, true);
			// the group has beaten up to World 5: the last talent of each branch stays locked
			MatrioData data = MatrioData.get(srv);
			String group = data.groupOf(p.getUUID());
			data.group(group).putInt("done", (1 << 6) - 1);
			data.changed();
			ps.sync();
		});
		ctx.waitTicks(20);
		for (String lang : new String[]{"en_us", "de_de"}) {
			if (!lang.equals("en_us")) language(ctx, lang);
			String sfx = "_" + lang.substring(0, 2);
			// the Trials book: the list, a chosen trial with its board, the titles page
			cursor(ctx, 2, 2);
			ctx.setScreen(() -> new TrialsScreen(null));
			ctx.waitTicks(20);
			shot(ctx, "rs_ui_trials" + sfx, false);
			int[] g = gui(ctx);
			int l = (g[0] - 340) / 2, t = Math.max(0, Math.min((g[1] - 214) / 2 + 12, g[1] - 214 - 1));
			cursor(ctx, l + 60, t + 42 + 6 * 12 + 3);
			ctx.getInput().pressMouse(0);
			ctx.waitTicks(10);
			shot(ctx, "rs_ui_trials_w7" + sfx, false);
			cursor(ctx, l + 60, t + 42 + 10 * 12 + 3);
			ctx.getInput().pressMouse(0);
			ctx.waitTicks(10);
			shot(ctx, "rs_ui_trials_gauntlet" + sfx, false);
			cursor(ctx, l + 88, t + 214 - 22);
			ctx.getInput().pressMouse(0);
			ctx.waitTicks(10);
			shot(ctx, "rs_ui_trials_titles" + sfx, false);
			ctx.setScreen(() -> null);
			ctx.waitTicks(10);

			// the Talent cabinet: every class tab, a tooltip, a locked talent, the Forget button
			cursor(ctx, 2, 2);
			ctx.setScreen(TalentScreen::new);
			ctx.waitTicks(20);
			int tl = (g[0] - 256) / 2, tt = (g[1] - 222) / 2;
			for (int i = 0; i < ReplayContent.CLASSES.length; i++) {
				cursor(ctx, tl + 50 + (i % 3) * 52 + 25, tt + 142 + (i / 3) * 24 + 10);
				ctx.getInput().pressMouse(0);
				ctx.waitTicks(6);
				cursor(ctx, 2, 2);
				ctx.waitTicks(4);
				shot(ctx, "rs_ui_talents_" + ReplayContent.CLASSES[i] + sfx, false);
			}
			// back to the Berserker: a learnt talent, one to learn, a locked one, with their tooltips
			cursor(ctx, tl + 50 + 52 + 25, tt + 142 + 10);
			ctx.getInput().pressMouse(0);
			ctx.waitTicks(6);
			int[][] nodes = {{0, 1, 0}, {2, 1, 1}, {0, 3, 2}, {1, 2, 3}};
			String[] what = {"learnt", "ready", "locked", "next"};
			for (int k = 0; k < nodes.length; k++) {
				int nx = tl + 31 + nodes[k][0] * 43 + 8, ny = tt + 44 + nodes[k][1] * 19 + 8;
				cursor(ctx, nx, ny);
				if (k == 1) {
					ctx.getInput().pressMouse(0);
				}
				ctx.waitTicks(6);
				shot(ctx, "rs_ui_talents_tip_" + what[k] + sfx, false);
			}
			cursor(ctx, tl + 189, tt + 204);
			ctx.waitTicks(6);
			shot(ctx, "rs_ui_talents_forget" + sfx, false);
			ctx.setScreen(() -> null);
			ctx.waitTicks(10);
		}
		language(ctx, "en_us");
		cursor(ctx, 2, 2);
	}

	private static void language(ClientGameTestContext ctx, String code) {
		ctx.runOnClient(mc -> {
			mc.options.languageCode = code;
			mc.getLanguageManager().setSelected(code);
			mc.reloadResourcePacks();
		});
		ctx.waitTicks(200);
		ctx.setScreen(() -> null);
		ctx.waitTicks(10);
	}

	// ---------------------------------------------------------------- events
	private static void events(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		hold(s, "");
		for (int w : new int[]{1, 2}) {
			s.runCommand("execute as @p run matriochka world enter " + w);
			ctx.setScreen(() -> null);
			ctx.waitTicks(160);
			sp.getConnection().waitForChunksRender();
			// a little room around the player, on the land
			s.runOnServer(srv -> {
				ServerPlayer p = player(srv);
				ServerLevel level = (ServerLevel) p.level();
				BlockPos c = p.blockPosition();
				for (BlockPos q : BlockPos.betweenClosed(c.offset(-5, 0, -5), c.offset(5, 4, 5))) if (!level.getBlockState(q).isAir()) level.setBlock(q, Blocks.AIR.defaultBlockState(), 2);
			});
			if (w == 1) {
				s.runOnServer(srv -> WorldEvents.start(player(srv), WorldEvents.INVASION));
				ctx.waitTicks(40);
				shot(ctx, "rs_event_invasion_warning", true);
				s.runOnServer(srv -> WorldEvents.hurry(player(srv)));
				ctx.waitTicks(40);
				shot(ctx, "rs_event_invasion_wave1", true);
				for (int wave = 1; wave < ReplayContent.INVASION_WAVES; wave++) {
					s.runOnServer(ReplayShots::clearInvasion);
					ctx.waitTicks(30);
				}
				// the warlord's wave: look at the warlord
				s.runOnServer(srv -> {
					ServerPlayer p = player(srv);
					for (Entity e : WorldEvents.foes(p)) {
						if (!e.entityTags().contains(WorldEvents.TAG + "_warlord")) continue;
						if (e instanceof net.minecraft.world.entity.Mob m) m.setNoAi(true);
						Vec3 d = e.position().subtract(p.position()).normalize();
						e.teleportTo(p.getX() + d.x * 6, p.getY(), p.getZ() + d.z * 6);
						srv.getCommands().performPrefixedCommand(srv.createCommandSourceStack().withSuppressedOutput(),
							String.format(java.util.Locale.ROOT, "execute as %s at @s run tp @s ~ ~ ~ facing %.2f %.2f %.2f", p.getGameProfile().name(), e.getX(), e.getY() + 1.4, e.getZ()));
					}
				});
				ctx.waitTicks(20);
				shot(ctx, "rs_event_invasion_warlord", true);
				s.runOnServer(ReplayShots::clearInvasion);
				ctx.waitTicks(30);
				s.runOnServer(srv -> {
					ServerPlayer p = player(srv);
					BlockPos c = WorldEvents.lastChest(p);
					if (c != null) srv.getCommands().performPrefixedCommand(srv.createCommandSourceStack().withSuppressedOutput(),
						"execute as " + p.getGameProfile().name() + " at @s run tp @s ~ ~ ~ facing " + (c.getX() + 0.5) + " " + c.getY() + " " + (c.getZ() + 0.5));
				});
				ctx.waitTicks(6);
				shot(ctx, "rs_event_invasion_chest", true);
				// the travelling merchant, and its trades
				s.runOnServer(srv -> WorldEvents.start(player(srv), WorldEvents.MERCHANT));
				ctx.waitTicks(30);
				s.runOnServer(srv -> {
					ServerPlayer p = player(srv);
					var npcs = p.level().getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(24), n -> n.entityTags().contains(WorldEvents.MERCHANT_TAG));
					if (npcs.isEmpty()) return;
					MatrioNpc n = npcs.getFirst();
					n.setNoAi(true);
					Vec3 d = n.position().subtract(p.position()).normalize();
					n.teleportTo(p.getX() + d.x * 4, p.getY(), p.getZ() + d.z * 4);
					srv.getCommands().performPrefixedCommand(srv.createCommandSourceStack().withSuppressedOutput(),
						String.format(java.util.Locale.ROOT, "execute as %s at @s run tp @s ~ ~ ~ facing %.2f %.2f %.2f", p.getGameProfile().name(), n.getX(), n.getY() + 1.5, n.getZ()));
				});
				ctx.waitTicks(20);
				shot(ctx, "rs_event_merchant", true);
				s.runOnServer(srv -> {
					ServerPlayer p = player(srv);
					var npcs = p.level().getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(24), n -> n.entityTags().contains(WorldEvents.MERCHANT_TAG));
					if (!npcs.isEmpty()) npcs.getFirst().mobInteract(p, InteractionHand.MAIN_HAND);
				});
				ctx.waitTicks(20);
				shot(ctx, "rs_event_merchant_trades", false);
				ctx.setScreen(() -> null);
				s.runOnServer(srv -> WorldEvents.hurry(player(srv)));
				ctx.waitTicks(40);
			}
			// the surge of the world's rule
			s.runCommand("execute as @p at @s run tp @s ~ ~ ~ ~ 0");
			s.runOnServer(srv -> WorldEvents.start(player(srv), WorldEvents.SURGE));
			ctx.waitTicks(60);
			shot(ctx, "rs_event_surge_w" + w + "_warning", true);
			s.runOnServer(srv -> WorldEvents.hurry(player(srv)));
			ctx.waitTicks(80);
			shot(ctx, "rs_event_surge_w" + w, true);
			camera(ctx, CameraType.THIRD_PERSON_BACK);
			ctx.waitTicks(20);
			shot(ctx, "rs_event_surge_w" + w + "_third", true);
			camera(ctx, CameraType.FIRST_PERSON);
			s.runOnServer(srv -> WorldEvents.hurry(player(srv)));
			ctx.waitTicks(40);
			s.runCommand("execute as @p run matriochka world leave");
			ctx.waitTicks(60);
		}
	}

	private static void clearInvasion(MinecraftServer srv) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		for (Entity e : WorldEvents.foes(p)) {
			if (e instanceof LivingEntity le) le.die(level.damageSources().playerAttack(p));
			e.discard();
		}
	}

	// ---------------------------------------------------------------- structures
	private static void structures(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("effect give @a night_vision infinite 0 true");
		s.runCommand("effect give @a conduit_power infinite 0 true");
		String only = System.getProperty("matriochka.worlds", "");
		for (var d : Content.STRUCTURES) {
			if (!List.of("caravan", "circle", "outpost", "bastion").contains(d.archetype())) continue;
			int w = d.world();
			if (!only.isEmpty() && !("," + only + ",").contains("," + w + ",")) continue;
			s.runCommand("gamemode creative @a");
			s.runCommand("execute as @p run matriochka world enter " + w);
			ctx.setScreen(() -> null);
			ctx.waitTicks(120);
			s.runCommand("gamemode spectator @a");
			// a site 200 blocks south: fly there so its chunks load, then place it with the server's own command
			s.runCommand("execute as @p at @s run tp @s ~ ~30 ~200");
			ctx.waitTicks(60);
			sp.getConnection().waitForChunksRender();
			int[] site = null;
			// the land camps refuse a site under water: the next site back toward the spawn's land, flown to first so its chunks load
			for (int attempt = 0; attempt < 8 && site == null; attempt++) {
			if (attempt > 0) {
				s.runCommand("execute as @p at @s run tp @s ~" + (attempt % 2 == 0 ? 48 : -48) + " ~ ~-40");
				ctx.waitTicks(50);
				sp.getConnection().waitForChunksRender();
			}
			site = s.computeOnServer(srv -> {
				ServerPlayer p = player(srv);
				ServerLevel lvl = (ServerLevel) p.level();
				int x = (p.getBlockX() >> 4 << 4) + 8, z = ((p.getBlockZ() + 30) >> 4 << 4) + 8;
				// the command only takes the column: the structure finds its own height (World 2: a cave floor under the roof)
				int y = Worlds.ceiling(w) ? 30 + Math.floorMod((x >> 4) * 31 + (z >> 4) * 17, 40) : w == 2 ? 64 : lvl.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
				var src = srv.createCommandSourceStack().withLevel(lvl).withPosition(new Vec3(x, y, z)).withSuppressedOutput();
				try {
					srv.getCommands().getDispatcher().execute("place structure matriochka:" + d.id() + " " + x + " " + y + " " + z, src);
				} catch (Exception e) {
					Matriochka.LOG.warn("[replayshots] place {} at {} {} refused: {}", d.id(), x, z, e.getMessage());
					return null;
				}
				// its chest, the one nearest the centre
				BlockPos chest = null;
				for (int cx = (x - 24) >> 4; cx <= (x + 24) >> 4; cx++)
					for (int cz = (z - 24) >> 4; cz <= (z + 24) >> 4; cz++)
						for (var be : lvl.getChunk(cx, cz).getBlockEntities().values()) {
							if (!(be instanceof ChestBlockEntity)) continue;
							BlockPos q = be.getBlockPos();
							if (chest == null || q.distSqr(new BlockPos(x, q.getY(), z)) < chest.distSqr(new BlockPos(x, chest.getY(), z))) chest = q;
						}
				if (w == 2 && chest != null) y = chest.getY();
				int top = Worlds.ceiling(w) || w == 2 ? y : lvl.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
				int ground = w == 7 ? lvl.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z) : top;
				Matriochka.LOG.info("[replayshots] {} at {} {} {} (top {}), chest {}", d.id(), x, y, z, top, chest);
				return chest == null ? new int[]{x, y, z, top, ground, 0, 0, 0, 0} : new int[]{x, y, z, top, ground, 1, chest.getX(), chest.getY(), chest.getZ()};
			});
			}
			if (site == null) continue;
			// in the cave worlds the structure sits in a cavern carved around it: the camera stays inside it
			boolean cave = Worlds.ceiling(w) || w == 2;
			int back = cave ? 16 : d.size().equals("large") ? 46 : 32;
			int x = site[0], y = site[1], z = site[2], top = site[3];
			int lookY = Worlds.ceiling(w) || w == 2 ? y + 3 : Math.max(y, top - 4) + 3;
			// three quarters from above
			s.runCommand("execute as @p at @s run tp @s " + (x + back / 2) + " " + (lookY + back * 4 / 10) + " " + (z - back * 9 / 10) + " facing " + x + " " + lookY + " " + z);
			ctx.waitTicks(40);
			sp.getConnection().waitForChunksRender();
			ctx.waitTicks(10);
			shot(ctx, "rs_struct_" + d.id() + "_above", false);
			// at eye height, from where a traveller would come
			s.runCommand("execute as @p at @s run tp @s " + (x - back * 3 / 4) + " " + (y + 2) + " " + (z - back * 3 / 4) + " facing " + x + " " + (y + 2) + " " + z);
			ctx.waitTicks(30);
			sp.getConnection().waitForChunksRender();
			ctx.waitTicks(6);
			shot(ctx, "rs_struct_" + d.id() + "_ground", false);
			// inside, before its chest
			if (site[5] == 1) {
				int chx = site[6], chy = site[7], chz = site[8];
				double dx = x - chx, dz = z - chz, len = Math.max(1, Math.sqrt(dx * dx + dz * dz));
				double ex = chx + 0.5 + dx / len * 3, ez = chz + 0.5 + dz / len * 3;
				s.runCommand(String.format(java.util.Locale.ROOT, "execute as @p at @s run tp @s %.2f %.2f %.2f facing %.2f %.2f %.2f", ex, chy + 1.0, ez, chx + 0.5, chy + 0.3, chz + 0.5));
				ctx.waitTicks(30);
				sp.getConnection().waitForChunksRender();
				ctx.waitTicks(6);
				shot(ctx, "rs_struct_" + d.id() + "_chest", false);
			}
			s.runCommand("gamemode creative @a");
			s.runCommand("execute as @p run matriochka world leave");
			ctx.waitTicks(40);
		}
		s.runCommand("gamemode survival @a");
	}
}
