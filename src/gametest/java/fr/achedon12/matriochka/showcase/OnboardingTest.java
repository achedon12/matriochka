package fr.achedon12.matriochka.showcase;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.InfoScreen;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.net.Net;
import fr.achedon12.matriochka.net.StationMenu;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Tutorial;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.input.MouseButtonInfo;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Walks the first-steps guide with real actions and real ticks: the Scroll's Next button, a trip to the Guardian's
 * Sanctuary, the altar, the Guardian's defeat and its drops, placing the Workbench, crafting the Seed through the
 * station menu, a hoe on World Soil, the Seed planted by water, its hatching and the World Block. Shots of the card
 * at a few steps (onboarding_*.png), then a check of every lang file against English and of the fallback to English.
 * Run with ./gradlew runClientGameTest -Ponboarding. Fails the run on the first broken check.
 */
final class OnboardingTest {
	private OnboardingTest() {}

	private static final List<String> REPORT = new ArrayList<>();
	/** The test pad by the sanctuary: floor centre, set once the Guardian is down. */
	private static BlockPos pad;

	static void run(ClientGameTestContext ctx) {
		REPORT.clear();
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("time set 6000");
			server.runCommand("gamemode survival @a");
			server.runCommand("effect give @a resistance infinite 4 true");
			server.runCommand("effect give @a saturation infinite 0 true");
			ctx.waitTicks(40);
			// the Scroll opened by itself at the first join: close it without reading
			ctx.setScreen(() -> null);
			ctx.waitTicks(30);
			check(step(server) == 0, "a new player starts the guide at step 0 (" + step(server) + ")");
			shot(ctx, "onboarding_0_read");

			// 1. read: the Scroll's Next button, clicked for real, turns to the objective page
			ctx.setScreen(() -> new JournalScreen(true));
			ctx.waitTicks(30);
			ctx.runOnClient(mc -> {
				var screen = mc.gui.screen();
				int bw = 340, bh = 214;
				int l = (screen.width - bw) / 2, t = Math.max(0, Math.min((screen.height - bh) / 2 + 12, screen.height - bh - 1));
				screen.mouseClicked(new MouseButtonEvent(l + bw / 2 + 30 + 20, t + bh - 30 + 8, new MouseButtonInfo(0, 0)), false);
			});
			ctx.waitTicks(50);
			ctx.setScreen(() -> null);
			ctx.waitTicks(30);
			check(step(server) >= 1, "turning the Scroll to its objective page completes step 1 (" + step(server) + ")");
			boolean located = server.computeOnServer(s -> PlayerState.of(player(s)).tag().contains("tut_sx"));
			check(located, "the Guardian's Sanctuary was located for the compass");
			shot(ctx, "onboarding_1_sanctuary");

			// the card can be hidden and shown again, and the choice is kept server side
			ctx.runOnClient(mc -> ClientPlayNetworking.send(new Net.TutorialPayload("hide")));
			ctx.waitTicks(10);
			check(server.computeOnServer(s -> PlayerState.of(player(s)).has("tut_hide")), "the card can be hidden");
			ctx.runOnClient(mc -> ClientPlayNetworking.send(new Net.TutorialPayload("show")));
			ctx.waitTicks(10);
			check(server.computeOnServer(s -> !PlayerState.of(player(s)).has("tut_hide")), "the card can be shown again");
			if (!located) return;

			// 2. sanctuary: walk in (a teleport next to its altar)
			BlockPos altar = server.computeOnServer(OnboardingTest::goToSanctuary);
			check(altar != null, "the sanctuary's altar is there (" + altar + ")");
			if (altar == null) return;
			ctx.waitTicks(60);
			check(step(server) >= 2, "reaching the sanctuary completes step 2 (" + step(server) + ")");

			// 3. wake: use the altar with an empty hand
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				emptyHand(p);
				use(p, altar, Direction.UP);
			});
			ctx.waitTicks(60);
			check(step(server) >= 3, "waking the Guardian completes step 3 (" + step(server) + ")");
			shot(ctx, "onboarding_3_defeat");

			// 4. defeat: the Guardian falls; walk over its drops
			BlockPos drop = server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				ServerLevel level = (ServerLevel) p.level();
				var bosses = level.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(64));
				if (bosses.isEmpty()) return null;
				MatrioBoss boss = bosses.get(0);
				BlockPos at = boss.blockPosition();
				boss.die(level.damageSources().playerAttack(p));
				boss.discard();
				return at;
			});
			check(drop != null, "the Guardian woke at the altar");
			if (drop == null) return;
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				ServerLevel level = (ServerLevel) p.level();
				// gather what it dropped: stand on each item in turn
				for (ItemEntity e : level.getEntitiesOfClass(ItemEntity.class, new net.minecraft.world.phys.AABB(drop).inflate(12))) e.setPos(p.getX(), p.getY(), p.getZ());
			});
			ctx.waitTicks(60);
			check(step(server) >= 4, "defeating the Guardian completes step 4 (" + step(server) + ")");
			List<String> picked = server.computeOnServer(s -> {
				List<String> out = new ArrayList<>();
				ServerPlayer p = player(s);
				for (String id : new String[]{"matrix_workbench", "guardian_core", "world_soil_0"}) {
					if (count(p, ModContent.item(id)) == 0) {
						out.add(id);
						p.getInventory().add(new ItemStack(ModContent.item(id), id.equals("world_soil_0") ? 4 : 1));
					}
				}
				pad = buildPad(p, altar);
				return out;
			});
			check(picked.isEmpty(), "the Guardian's workbench, core and soil were picked up (missing: " + picked + ")");

			// 5. workbench: place it on the floor
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				hold(p, ModContent.item("matrix_workbench"));
				use(p, pad.offset(2, -1, 0), Direction.UP);
			});
			ctx.waitTicks(40);
			check(step(server) >= 5, "placing the Matrix Workbench completes step 5 (" + step(server) + ")");
			shot(ctx, "onboarding_5_seed");

			// 6. seed: open the workbench and press the World 1 Seed's button, as the station screen does
			String crafted = server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				p.getInventory().add(new ItemStack(Items.IRON_INGOT, 16));
				p.getInventory().add(new ItemStack(Items.OAK_LOG, 16));
				emptyHand(p);
				use(p, pad.offset(2, 0, 0), Direction.UP);
				if (!(p.containerMenu instanceof StationMenu menu)) return "the workbench menu did not open";
				int index = -1;
				var list = Recipes.of("matrix_workbench");
				for (int i = 0; i < list.size(); i++) if (list.get(i).output().equals("seed_1")) index = i;
				// the drawer lays the Seed's pattern on the grid, then the result is taken like a crafted item
				menu.clickMenuButton(p, index);
				menu.quickMoveStack(p, menu.resultSlot);
				p.closeContainer();
				return count(p, ModContent.item("seed_1")) > 0 ? "" : "no Seed after the craft";
			});
			check(crafted.isEmpty(), "the World 1 Seed is crafted at the workbench " + crafted);
			ctx.waitTicks(40);
			check(step(server) >= 6, "crafting the Seed completes step 6 (" + step(server) + ")");

			// 7. till: place World Soil, then a hoe on it
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				hold(p, ModContent.item("world_soil_0"));
				use(p, pad.offset(-2, -2, 0), Direction.UP);
				p.getInventory().add(new ItemStack(Items.IRON_HOE));
				hold(p, Items.IRON_HOE);
				use(p, pad.offset(-2, -1, 0), Direction.UP);
			});
			ctx.waitTicks(40);
			check(step(server) >= 7, "tilling World Soil completes step 7 (" + step(server) + ")");

			// 8. plant: the Seed on the tilled soil, with water two blocks away
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				hold(p, ModContent.item("seed_1"));
				use(p, pad.offset(-2, -1, 0), Direction.UP);
			});
			ctx.waitTicks(30);
			check(step(server) >= 8, "planting the Seed completes step 8 (" + step(server) + ")");
			shot(ctx, "onboarding_8_hatch");

			// 9. hatch: real ticks until the World Block forms
			for (int i = 0; i < 20 && step(server) < 9; i++) ctx.waitTicks(20);
			check(step(server) >= 9, "the Seed hatching completes step 9 (" + step(server) + ")");
			shot(ctx, "onboarding_9_enter");

			// 10. enter: use the World Block
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				emptyHand(p);
				use(p, pad.offset(-2, 0, 0), Direction.NORTH);
			});
			ctx.waitTicks(40);
			check(step(server) >= Tutorial.DONE, "entering World 1 ends the guide (" + step(server) + ")");
			shot(ctx, "onboarding_10_done");

			ctx.setScreen(() -> new InfoScreen(null));
			ctx.waitTicks(20);
			shot(ctx, "onboarding_info");
			ctx.setScreen(() -> null);

			langs(ctx);
		} catch (Throwable t) {
			REPORT.add("FAIL exception " + t);
			Matriochka.LOG.error("[onboarding]", t);
		} finally {
			for (String line : REPORT) Matriochka.LOG.info("[onboarding] {}", line);
		}
		long failed = REPORT.stream().filter(l -> l.startsWith("FAIL")).count();
		if (failed > 0) throw new AssertionError(failed + " onboarding check(s) failed: " + REPORT);
	}

	// ---------------------------------------------------------------- lang files
	private static final Pattern PH = Pattern.compile("%(?:\\d+\\$)?[sd]");
	private static final String[] LANGS = {"fr_fr", "es_es", "de_de", "pt_br"};

	private static Map<String, String> lang(Minecraft mc, String code) throws Exception {
		var res = mc.getResourceManager().getResource(Matriochka.id("lang/" + code + ".json"));
		if (res.isEmpty()) return null;
		try (var in = new InputStreamReader(res.get().open(), StandardCharsets.UTF_8)) {
			JsonObject o = JsonParser.parseReader(in).getAsJsonObject();
			Map<String, String> m = new java.util.LinkedHashMap<>();
			for (var e : o.entrySet()) m.put(e.getKey(), e.getValue().getAsString());
			return m;
		}
	}

	private static int placeholders(String s) {
		Matcher m = PH.matcher(s.replace("%%", ""));
		int n = 0;
		while (m.find()) n++;
		return n;
	}

	/** Every lang file: its keys exist in English, its placeholders match; a missing key reads as English in game. */
	private static void langs(ClientGameTestContext ctx) {
		String sample = ctx.computeOnClient(mc -> {
			try {
				Map<String, String> en = lang(mc, "en_us");
				check(en != null && !en.isEmpty(), "en_us.json is there (" + (en == null ? 0 : en.size()) + " keys)");
				if (en == null) return "";
				String missingKey = "";
				for (String code : LANGS) {
					Map<String, String> tr = lang(mc, code);
					check(tr != null, code + ".json is there");
					if (tr == null) continue;
					int unknown = 0, broken = 0, missing = 0;
					for (var e : tr.entrySet()) {
						if (!en.containsKey(e.getKey())) unknown++;
						else if (placeholders(e.getValue()) != placeholders(en.get(e.getKey()))) broken++;
					}
					for (String k : en.keySet()) if (!tr.containsKey(k)) {
						missing++;
						if (code.equals("es_es") && missingKey.isEmpty()) missingKey = k;
					}
					check(unknown == 0 && broken == 0, code + ": " + tr.size() + "/" + en.size() + " keys, " + missing + " fall back to English, " + unknown + " unknown, " + broken + " with other placeholders");
				}
				return missingKey;
			} catch (Exception e) {
				check(false, "reading the lang files: " + e);
				return "";
			}
		});
		// switch the game to Spanish: a translated key reads in Spanish, a missing one in English
		ctx.runOnClient(mc -> {
			mc.options.languageCode = "es_es";
			mc.getLanguageManager().setSelected("es_es");
			mc.reloadResourcePacks();
		});
		ctx.waitTicks(200);
		ctx.runOnClient(mc -> {
			try {
				Map<String, String> en = lang(mc, "en_us"), es = lang(mc, "es_es");
				var language = net.minecraft.locale.Language.getInstance();
				String key = "tutorial.matriochka.read";
				if (es != null && es.containsKey(key)) check(language.getOrDefault(key).equals(es.get(key)), "in Spanish, " + key + " reads \"" + language.getOrDefault(key) + "\"");
				if (!sample.isEmpty()) check(language.getOrDefault(sample).equals(en.get(sample)), "in Spanish, the untranslated " + sample + " falls back to English");
				else check(true, "es_es has every key: nothing to fall back on");
			} catch (Exception e) {
				check(false, "checking the fallback: " + e);
			}
		});
		ctx.setScreen(() -> null);
		shot(ctx, "onboarding_es");
		ctx.runOnClient(mc -> {
			mc.options.languageCode = "en_us";
			mc.getLanguageManager().setSelected("en_us");
			mc.reloadResourcePacks();
		});
		ctx.waitTicks(200);
	}

	// ---------------------------------------------------------------- helpers
	private static void check(boolean ok, String what) {
		REPORT.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.waitTicks(20);
		ctx.takeScreenshot(TestScreenshotOptions.of(name).withSize(1920, 1080).disableCounterPrefix());
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	private static int step(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext server) {
		return server.computeOnServer(s -> Tutorial.step(PlayerState.of(player(s))));
	}

	private static int count(ServerPlayer p, Item item) {
		return fr.achedon12.matriochka.block.Stations.count(p.getInventory(), item);
	}

	/** Takes an item in hand as a player would: selects its hotbar slot, or swaps it into the selected one. */
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

	/** Selects an empty hotbar slot. */
	private static void emptyHand(ServerPlayer p) {
		var inv = p.getInventory();
		for (int i = 8; i >= 0; i--) {
			if (inv.getItem(i).isEmpty()) {
				inv.setSelectedSlot(i);
				return;
			}
		}
	}

	/** A right click on a block face, through the same path as a real client click. */
	private static void use(ServerPlayer p, BlockPos pos, Direction face) {
		Vec3 hit = Vec3.atCenterOf(pos).add(face.getStepX() * 0.5, face.getStepY() * 0.5, face.getStepZ() * 0.5);
		p.gameMode.useItemOn(p, p.level(), p.getItemInHand(InteractionHand.MAIN_HAND), InteractionHand.MAIN_HAND, new BlockHitResult(hit, face, pos, false));
	}

	/** Loads the sanctuary the compass points at, finds its altar and stands the player beside it. */
	private static BlockPos goToSanctuary(MinecraftServer s) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		var tag = PlayerState.of(p).tag();
		int sx = tag.getIntOr("tut_sx", 0), sz = tag.getIntOr("tut_sz", 0);
		for (int cx = -4; cx <= 4; cx++) for (int cz = -4; cz <= 4; cz++) level.getChunk((sx >> 4) + cx, (sz >> 4) + cz);
		BlockPos altar = null;
		for (int dx = -64; dx <= 64 && altar == null; dx++) {
			for (int dz = -64; dz <= 64 && altar == null; dz++) {
				int x = sx + dx, z = sz + dz, top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
				for (int y = top + 4; y >= top - 40 && altar == null; y--) {
					BlockPos q = new BlockPos(x, y, z);
					if (level.getBlockState(q).is(ModContent.block("sanctuary_altar"))) altar = q;
				}
			}
		}
		if (altar == null) return null;
		BlockPos stand = altar.offset(0, 0, 3);
		while (!level.getBlockState(stand).isAir() && stand.getY() < altar.getY() + 6) stand = stand.above();
		p.teleportTo(level, stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5, Set.of(), 180f, 30f, false);
		return altar;
	}

	/**
	 * A flat stone pad around the player (who stands on its centre), clear of the sanctuary, with water two blocks
	 * from where the soil goes. Returns the centre at the player's feet.
	 */
	private static BlockPos buildPad(ServerPlayer p, BlockPos altar) {
		ServerLevel level = (ServerLevel) p.level();
		// south of the altar at its height, not where the fight left the player: after the fight the player stood
		// below sea level (y 56), and the water around flowed into the open pad, over the soil, so the Seed could not go in
		BlockPos c = altar.offset(0, 0, 24);
		for (int dx = -6; dx <= 6; dx++) {
			for (int dz = -6; dz <= 6; dz++) {
				boolean rim = Math.abs(dx) == 6 || Math.abs(dz) == 6;
				level.setBlock(c.offset(dx, -2, dz), Blocks.STONE.defaultBlockState(), 3);
				level.setBlock(c.offset(dx, -1, dz), Blocks.STONE.defaultBlockState(), 3);
				// a low stone rim keeps the water and sand around out of the pad
				for (int dy = 0; dy <= 4; dy++) level.setBlock(c.offset(dx, dy, dz), (rim ? Blocks.STONE : Blocks.AIR).defaultBlockState(), 3);
			}
		}
		// the soil goes on the floor at (-2, -1, 0): its block replaces nothing, so dig its place out first
		level.setBlock(c.offset(-2, -1, 0), Blocks.AIR.defaultBlockState(), 3);
		level.setBlock(c.offset(-4, -1, 0), Blocks.WATER.defaultBlockState(), 3);
		p.teleportTo(level, c.getX() + 0.5, c.getY(), c.getZ() + 0.5, Set.of(), -90f, 40f, false);
		return c;
	}
}
