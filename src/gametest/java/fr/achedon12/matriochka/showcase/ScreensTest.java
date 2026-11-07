package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.EndingScreen;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.client.MatrioClient;
import fr.achedon12.matriochka.client.RecapScreen;
import fr.achedon12.matriochka.client.StallScreen;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.replay.WorldEvents;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.CycleStats;
import fr.achedon12.matriochka.world.Cycles;
import fr.achedon12.matriochka.world.Endings;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;

/**
 * The market stall and the end-of-cycle recap: ./gradlew runClientGameTest -Pscreens. Opens the stall for the Doll
 * Peddler, a world's people with many offers, the black market and a travelling merchant, trades through it (a
 * click, then a shift-click), checks the stock and the karma's price; then plays real deaths, a boss kill and a
 * page found, reaches each ending and checks the recap's numbers, reopens it from the Journal, and photographs both
 * screens at GUI scales 2, 3 and 4, in a narrow window, in English, German and French. Shots: screens_*.png. Fails
 * the run on the first failed check.
 */
final class ScreensTest {
	private ScreensTest() {}

	private static final List<String> REPORT = new ArrayList<>();
	private static int npcId = -1;

	private static void check(boolean ok, String what) {
		REPORT.add((ok ? "ok   " : "FAIL ") + what);
		Matriochka.LOG.info("[screens] {}{}", ok ? "ok   " : "FAIL ", what);
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	private static int window = 1920, windowH = 1080;

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.runOnClient(mc -> { if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
		ctx.waitTick();
		ctx.takeScreenshot(TestScreenshotOptions.of("screens_" + name).withSize(window, windowH).disableCounterPrefix());
		ctx.runOnClient(mc -> { if (fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc); });
	}

	private static void cursor(ClientGameTestContext ctx, double gx, double gy) {
		double scale = ctx.computeOnClient(mc -> mc.getWindow().getGuiScale());
		ctx.getInput().setCursorPos(gx * scale, gy * scale);
	}

	private static void click(ClientGameTestContext ctx, int[] at) {
		cursor(ctx, at[0], at[1]);
		ctx.waitTicks(2);
		ctx.getInput().pressMouse(com.mojang.blaze3d.platform.InputConstants.MOUSE_BUTTON_LEFT);
		ctx.waitTicks(4);
	}

	private static void scale(ClientGameTestContext ctx, int s) {
		ctx.runOnClient(mc -> {
			mc.options.guiScale().set(s);
			mc.resizeGui();
		});
		ctx.waitTicks(3);
	}

	private static void resize(ClientGameTestContext ctx, int w, int h) {
		window = w;
		windowH = h;
		ctx.getInput().resizeWindow(w, h);
		ctx.waitTicks(5);
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

	static void run(ClientGameTestContext ctx) {
		REPORT.clear();
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			resize(ctx, 1920, 1080);
			McTest.waitForChunks(sp);
			s.runCommand("gamerule advance_time false");
			s.runCommand("gamerule advance_weather false");
			s.runCommand("weather clear");
			s.runCommand("gamerule spawn_monsters false");
			s.runCommand("gamerule announce_advancements false");
			s.runCommand("gamerule show_death_messages false");
			s.runCommand("time set 6000");
			s.runCommand("difficulty normal");
			s.runCommand("gamemode survival @a");
			ctx.setScreen(() -> null);
			ctx.waitTicks(40);
			scale(ctx, 3);
			stall(ctx, sp);
			recap(ctx, sp);
			language(ctx, "en_us");
			scale(ctx, 0);
		}
		long failed = REPORT.stream().filter(l -> l.startsWith("FAIL")).count();
		for (String line : REPORT) Matriochka.LOG.info("[screens] {}", line);
		if (failed > 0) throw new AssertionError(failed + " screen check(s) failed: " + REPORT);
	}

	// ---------------------------------------------------------------- the stall
	/** Summons one of the peoples three blocks ahead of the player, facing it, standing still. */
	private static void summon(MinecraftServer srv, String id) {
		ServerPlayer p = player(srv);
		ServerLevel level = (ServerLevel) p.level();
		for (Entity e : level.getEntities((Entity) null, p.getBoundingBox().inflate(24), e -> e instanceof MatrioNpc)) e.discard();
		Entity e = ModContent.entity(id).create(level, EntitySpawnReason.COMMAND);
		if (!(e instanceof MatrioNpc npc)) return;
		npc.setPos(p.getX() + 3, p.getY(), p.getZ());
		npc.setNoAi(true);
		level.addFreshEntity(npc);
		npcId = npc.getId();
	}

	private static MatrioNpc npc(MinecraftServer srv) {
		return (MatrioNpc) player(srv).level().getEntity(npcId);
	}

	private static void karma(MinecraftServer srv, int k) {
		PlayerState ps = PlayerState.of(player(srv));
		ps.tag().putInt("karma", k);
		ps.sync();
	}

	/** Opens the trades the way a right click does, on the server; the client opens whatever screen it opens. */
	private static void openTrades(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		sp.getServer().runOnServer(srv -> npc(srv).mobInteract(player(srv), InteractionHand.MAIN_HAND));
		ctx.waitTicks(14);
	}

	private static void closeTrades(ClientGameTestContext ctx) {
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.closeContainer(); });
		ctx.waitTicks(8);
	}

	private static boolean stallOpen(ClientGameTestContext ctx) {
		return ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen);
	}

	private static int count(MinecraftServer srv, net.minecraft.world.item.Item item) {
		return fr.achedon12.matriochka.block.Stations.count(player(srv).getInventory(), item);
	}

	private static void stall(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runCommand("clear @p");
		s.runCommand("give @p minecraft:emerald 64");
		s.runCommand("give @p minecraft:gold_ingot 8");
		s.runCommand("execute as @p at @s run tp @s ~ ~ ~ 270 10");
		s.runOnServer(srv -> {
			summon(srv, "doll_peddler");
			karma(srv, 40);
		});
		ctx.waitTicks(10);
		// ---- the Peddler, karma 40: a discount on every price
		openTrades(ctx, sp);
		check(stallOpen(ctx), "the Doll Peddler opens the Matriochka stall, not the villager screen");
		String kind = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen st ? st.info().kind() : "");
		check(kind.equals("peddler"), "the stall knows it is the Peddler (" + kind + ")");
		ctx.waitTicks(20);
		cursor(ctx, 2, 2);
		shot(ctx, "stall_peddler");
		int price = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu().getOffers().get(0).getCostA().getCount());
		check(price == 5, "karma 40 takes the Chance Doll from 6 to 5 emeralds (" + price + ")");
		// the tooltip of a line
		int[] row1 = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(1));
		cursor(ctx, row1[0] + 30, row1[1]);
		ctx.waitTicks(6);
		shot(ctx, "stall_peddler_tooltip");
		// ---- a trade through the stall: pick the line, take the doll, drop it in the inventory
		int[] row0 = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(0));
		click(ctx, row0);
		int sel = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).selected());
		check(sel == 0, "clicking a line selects its trade (" + sel + ")");
		ctx.waitTicks(6);
		boolean filled = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu().getSlot(0).getItem().is(Items.EMERALD)
			&& ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu().getSlot(2).getItem().is(ModContent.item("chance_doll")));
		check(filled, "the selection moves the emeralds onto the counter and shows the Chance Doll");
		cursor(ctx, 2, 2);
		shot(ctx, "stall_peddler_selected");
		click(ctx, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).slotCenter(2)));
		int empty = ctx.computeOnClient(mc -> {
			var menu = ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu();
			for (int i = 3; i < menu.slots.size(); i++) if (!menu.getSlot(i).hasItem()) return i;
			return -1;
		});
		click(ctx, ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).slotCenter(empty)));
		ctx.waitTicks(6);
		// ---- shift-click: the Wool Thread (2 emeralds, 1 with the discount) as long as the stock lasts
		int[] row2 = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(2));
		click(ctx, row2);
		ctx.waitTicks(4);
		int[] result = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).slotCenter(2));
		cursor(ctx, result[0], result[1]);
		ctx.waitTicks(2);
		// the test input cannot hold a modifier through a click in this version: send the shift-click the screen sends
		ctx.runOnClient(mc -> {
			var menu = ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu();
			mc.gameMode.handleContainerInput(menu.containerId, 2, 0, net.minecraft.world.inventory.ContainerInput.QUICK_MOVE, mc.player);
		});
		ctx.waitTicks(10);
		cursor(ctx, 2, 2);
		shot(ctx, "stall_peddler_sold_out");
		closeTrades(ctx);
		int[] after = s.computeOnServer(srv -> new int[]{count(srv, Items.EMERALD), count(srv, ModContent.item("chance_doll")), count(srv, ModContent.item("wool_thread")),
			npc(srv).getOffers().get(0).getUses(), npc(srv).getOffers().get(2).getUses(), npc(srv).getOffers().get(2).isOutOfStock() ? 1 : 0});
		check(after[1] == 1, "the click trade gave one Chance Doll (" + after[1] + ")");
		check(after[3] == 1, "the Chance Doll's stock went down by one (" + after[3] + " used)");
		check(after[4] == 12 && after[5] == 1 && after[2] == 48, "the shift-click bought the Wool Thread until the stock ran out (" + after[4] + " used, " + after[2] + " threads)");
		check(after[0] == 64 - 5 - 12, "the emeralds paid are the karma's prices: 5, then 12 x 1 (" + after[0] + " left)");
		// ---- the same trader, reopened: the sold-out line
		openTrades(ctx, sp);
		ctx.waitTicks(16);
		int[] row2b = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(2));
		click(ctx, row2b);
		cursor(ctx, 2, 2);
		ctx.waitTicks(6);
		shot(ctx, "stall_out_of_stock");
		for (int g : new int[]{2, 4}) {
			scale(ctx, g);
			ctx.waitTicks(4);
			shot(ctx, "stall_scale" + g);
		}
		scale(ctx, 3);
		closeTrades(ctx);
		// ---- a world's people with many wares, scrolled
		s.runOnServer(srv -> {
			summon(srv, "gatherer");
			karma(srv, 0);
			MatrioNpc npc = npc(srv);
			var offers = npc.getOffers();
			net.minecraft.world.item.Item[] goods = {Items.BREAD, Items.APPLE, Items.TORCH, Items.ARROW, Items.STRING, Items.LEATHER, Items.PAPER, Items.BOOK, Items.LANTERN, Items.CANDLE, Items.HONEY_BOTTLE};
			for (int i = 0; i < goods.length; i++) offers.add(new MerchantOffer(new ItemCost(Items.EMERALD, 1 + i % 4), i % 3 == 0 ? java.util.Optional.of(new ItemCost(Items.GOLD_INGOT, 1)) : java.util.Optional.empty(), new ItemStack(goods[i], 1 + i % 5), i == 4 ? 4 : 0, 8, 1, 0.05f));
			offers.get(offers.size() - 2).setToOutOfStock();
		});
		ctx.waitTicks(5);
		openTrades(ctx, sp);
		check(stallOpen(ctx), "a world's people opens the stall too");
		ctx.waitTicks(16);
		shot(ctx, "stall_people_many");
		int[] mid = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).rowCenter(0));
		cursor(ctx, mid[0], mid[1] + 40);
		for (int i = 0; i < 12; i++) {
			ctx.getInput().scroll(-1);
			ctx.waitTicks(1);
		}
		ctx.waitTicks(12);
		int scrolled = ctx.computeOnClient(mc -> ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).scrolled());
		check(scrolled > 0, "the wheel scrolls the ledger (" + scrolled + " lines)");
		cursor(ctx, 2, 2);
		shot(ctx, "stall_people_scrolled");
		closeTrades(ctx);
		// ---- the black market: karma -40 at a world's people
		s.runOnServer(srv -> {
			summon(srv, "prisoner");
			karma(srv, -40);
		});
		s.runCommand("give @p matriochka:sealed_fragment 20");
		ctx.waitTicks(5);
		openTrades(ctx, sp);
		int under = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen st ? st.info().contraband() : -1);
		check(under > 0, "karma -40 opens the black market at the stall (" + under + " goods under the counter)");
		ctx.waitTicks(16);
		cursor(ctx, 2, 2);
		shot(ctx, "stall_black_market");
		int markup = ctx.computeOnClient(mc -> {
			var o = ((StallScreen) fr.achedon12.matriochka.client.mc.McClient.screen(mc)).getMenu().getOffers().get(0);
			return o.getCostA().getCount() - o.getBaseCostA().getCount();
		});
		check(markup > 0, "dark karma raises the prices (+" + markup + ")");
		closeTrades(ctx);
		// ---- narrow window, smallest GUI the game allows
		resize(ctx, 640, 480);
		scale(ctx, 0);
		openTrades(ctx, sp);
		ctx.waitTicks(16);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc).width >= StallScreen.MW && fr.achedon12.matriochka.client.mc.McClient.screen(mc).height >= StallScreen.MH), "the stall fits a 640x480 window");
		shot(ctx, "stall_narrow");
		closeTrades(ctx);
		resize(ctx, 1920, 1080);
		scale(ctx, 3);
		// ---- a travelling merchant, in World 1
		s.runCommand("execute as @p run matriochka progression set 1");
		s.runCommand("execute as @p run matriochka world enter 1");
		ctx.setScreen(() -> null);
		ctx.waitTicks(160);
		McTest.waitForChunks(sp);
		boolean started = s.computeOnServer(srv -> WorldEvents.start(player(srv), WorldEvents.MERCHANT));
		ctx.waitTicks(30);
		boolean found = s.computeOnServer(srv -> {
			ServerPlayer p = player(srv);
			for (Entity e : ((ServerLevel) p.level()).getEntities((Entity) null, p.getBoundingBox().inflate(40), e -> e instanceof MatrioNpc && e.entityTags().contains(WorldEvents.MERCHANT_TAG))) {
				npcId = e.getId();
				((MatrioNpc) e).setNoAi(true);
				e.teleportTo(p.getX() + 3, p.getY(), p.getZ());
				return true;
			}
			return false;
		});
		check(started && found, "a travelling merchant arrives in World 1");
		if (found) {
			s.runOnServer(srv -> karma(srv, 10));
			s.runCommand("execute as @p at @s run tp @s ~ ~ ~ 270 10");
			ctx.waitTicks(10);
			openTrades(ctx, sp);
			String k = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof StallScreen st ? st.info().kind() + ":" + st.info().ticksLeft() : "");
			check(k.startsWith("travelling:") && !k.endsWith(":-1"), "the stall shows a travelling merchant and its time left (" + k + ")");
			ctx.waitTicks(16);
			cursor(ctx, 2, 2);
			shot(ctx, "stall_travelling");
			closeTrades(ctx);
		}
		s.runCommand("execute as @p run matriochka world leave");
		ctx.waitTicks(60);
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			for (Entity e : ((ServerLevel) p.level()).getEntities((Entity) null, p.getBoundingBox().inflate(24), e -> e instanceof MatrioNpc)) e.discard();
		});
		// ---- a vanilla villager keeps the vanilla screen
		s.runCommand("execute as @p at @s run summon minecraft:villager ~3 ~ ~ {NoAI:1b,VillagerData:{profession:\"minecraft:librarian\",level:2,type:\"minecraft:plains\"}}");
		ctx.waitTicks(10);
		s.runOnServer(srv -> {
			ServerPlayer p = player(srv);
			for (Entity e : ((ServerLevel) p.level()).getEntities((Entity) null, p.getBoundingBox().inflate(8), e -> e instanceof net.minecraft.world.entity.npc.villager.Villager)) {
				((net.minecraft.world.entity.npc.villager.Villager) e).mobInteract(p, InteractionHand.MAIN_HAND);
				break;
			}
		});
		ctx.waitTicks(14);
		boolean vanilla = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof net.minecraft.client.gui.screens.inventory.MerchantScreen);
		check(vanilla, "a vanilla villager still opens the vanilla merchant screen");
		closeTrades(ctx);
		s.runCommand("kill @e[type=minecraft:villager]");
		s.runOnServer(srv -> karma(srv, 0));
	}

	// ---------------------------------------------------------------- the recap
	private static CompoundTag stats(MinecraftServer srv) {
		return CycleStats.of(PlayerState.of(player(srv))).copy();
	}

	private static void recap(ClientGameTestContext ctx, TestSingleplayerContext sp) {
		var s = sp.getServer();
		s.runOnServer(srv -> {
			PlayerState ps = PlayerState.of(player(srv));
			CycleStats.reset(ps);
			ps.tag().remove(CycleStats.LAST);
			ps.sync();
		});
		// ---- real actions: a death, a boss kill, a page found
		s.runCommand("gamemode survival @a");
		s.runCommand("kill @p");
		ctx.waitTicks(20);
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.respawn(); });
		ctx.waitTicks(40);
		ctx.setScreen(() -> null);
		s.runCommand("gamemode creative @a");
		s.runCommand("execute as @p at @s run summon matriochka:spore_queen ~4 ~ ~ {NoAI:1b}");
		ctx.waitTicks(10);
		s.runCommand("kill @e[type=matriochka:spore_queen]");
		ctx.waitTicks(60);
		s.runCommand("give @p matriochka:journal_page[minecraft:custom_data={world:2,index:3}]");
		ctx.waitTicks(130);
		CompoundTag st = s.computeOnServer(ScreensTest::stats);
		check(st.getIntOr("deaths", 0) == 1, "a death is counted (" + st.getIntOr("deaths", 0) + ")");
		check((st.getIntOr("bosses", 0) & (1 << 1)) != 0, "the Spore Queen's fall is counted (bosses " + Integer.toBinaryString(st.getIntOr("bosses", 0)) + ")");
		check(st.getIntOr("pages", 0) == 1, "the page found is counted (" + st.getIntOr("pages", 0) + ")");
		check(st.getIntOr("souls", 0) > 0, "the boss's souls are counted (" + st.getIntOr("souls", 0) + ")");
		check(st.getIntOr("rebuilt", 0) >= 1, "the boss's Doll of Life layer counts as rebuilt (" + st.getIntOr("rebuilt", 0) + ")");
		check(st.getIntOr("ticks", 0) > 100, "the play time runs (" + st.getIntOr("ticks", 0) + " ticks)");
		// ---- the Sealed ending: the crawl, then the recap
		s.runOnServer(srv -> karma(srv, 30));
		ctx.waitTicks(4);
		s.runOnServer(srv -> Endings.play(player(srv), Endings.SEAL));
		ctx.waitTicks(20);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof EndingScreen), "the ending's crawl plays");
		ctx.runOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc).onClose());
		ctx.waitTicks(1);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof RecapScreen), "leaving the crawl opens the recap");
		ctx.waitTicks(10);
		shot(ctx, "recap_opening");
		ctx.waitTicks(60);
		CompoundTag last = ctx.computeOnClient(mc -> MatrioClient.state.getCompoundOrEmpty("last_cycle").copy());
		check(last.getStringOr("ending", "").equals("seal") && last.getIntOr("deaths", 0) == 1 && (last.getIntOr("bosses", 0) & 2) != 0 && last.getIntOr("pages", 0) == 1
			&& last.getIntOr("karma", 0) == 30 && last.getIntOr("cycle", -1) == 0, "the recap reaches the client with the cycle's numbers: " + last);
		cursor(ctx, 2, 2);
		shot(ctx, "recap_seal_first");
		int[] core = ctx.computeOnClient(mc -> new int[]{fr.achedon12.matriochka.client.mc.McClient.screen(mc).width / 2 - (11 * 22 - 4) / 2 + 22 + 9,
			Math.max(RecapScreen.ABOVE, (fr.achedon12.matriochka.client.mc.McClient.screen(mc).height - (RecapScreen.RH + RecapScreen.ABOVE + RecapScreen.BELOW)) / 2 + RecapScreen.ABOVE) + 70 + 9});
		cursor(ctx, core[0], core[1]);
		ctx.waitTicks(6);
		shot(ctx, "recap_seal_boss_tooltip");
		cursor(ctx, 2, 2);
		ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_F1);
		ctx.waitTicks(4);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof RecapScreen r && r.clean()), "F1 hides the buttons for a clean picture");
		shot(ctx, "recap_seal_clean");
		ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_F1);
		ctx.waitTicks(4);
		for (int g : new int[]{2, 4}) {
			scale(ctx, g);
			ctx.waitTicks(4);
			shot(ctx, "recap_scale" + g);
		}
		scale(ctx, 3);
		ctx.setScreen(() -> null);
		ctx.waitTicks(10);
		// ---- reopened from the Journal's Objective page
		ctx.setScreen(() -> new JournalScreen(false).tab(0));
		ctx.waitTicks(14);
		shot(ctx, "journal_last_cycle");
		int[] button = ctx.computeOnClient(mc -> {
			int l = (fr.achedon12.matriochka.client.mc.McClient.screen(mc).width - 340) / 2, t = Math.max(0, Math.min((fr.achedon12.matriochka.client.mc.McClient.screen(mc).height - 214) / 2 + 12, fr.achedon12.matriochka.client.mc.McClient.screen(mc).height - 214 - 1));
			return new int[]{l + 20 + (155 - 18) / 2, t + 46 + 8};
		});
		click(ctx, button);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) instanceof RecapScreen), "the Journal's Last cycle button reopens the recap");
		ctx.waitTicks(10);
		ctx.getInput().pressKey(com.mojang.blaze3d.platform.InputConstants.KEY_ESCAPE);
		ctx.waitTicks(10);
		String back = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc) == null ? "none" : fr.achedon12.matriochka.client.mc.McClient.screen(mc).getClass().getSimpleName());
		check(back.equals("JournalScreen"), "closing a recap opened from the Journal goes back to it (" + back + ")");
		ctx.setScreen(() -> null);
		// ---- a New Cycle: the counters start again, the recap stays
		s.runCommand("execute as @p run matriochka progression set 10");
		ctx.waitTicks(5);
		s.runOnServer(srv -> Cycles.begin(player(srv)));
		ctx.waitTicks(20);
		CompoundTag fresh = s.computeOnServer(ScreensTest::stats);
		String lastEnd = s.computeOnServer(srv -> PlayerState.of(player(srv)).tag().getCompoundOrEmpty(CycleStats.LAST).getStringOr("ending", ""));
		check(fresh.getIntOr("deaths", 0) == 0 && fresh.getIntOr("pages", 0) == 0 && fresh.getIntOr("bosses", 0) == 0, "the New Cycle starts the counters again: " + fresh);
		check(lastEnd.equals("seal"), "the New Cycle keeps the last recap until the next ending");
		// ---- the second cycle, to the Absorbed ending: a death, then the ending
		s.runCommand("gamemode survival @a");
		s.runCommand("kill @p");
		ctx.waitTicks(20);
		ctx.runOnClient(mc -> { if (mc.player != null) mc.player.respawn(); });
		ctx.waitTicks(40);
		ctx.setScreen(() -> null);
		s.runCommand("gamemode creative @a");
		s.runOnServer(srv -> {
			karma(srv, -60);
			Endings.play(player(srv), Endings.ABSORB);
		});
		ctx.waitTicks(20);
		ctx.runOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc).onClose());
		ctx.waitTicks(70);
		CompoundTag second = ctx.computeOnClient(mc -> MatrioClient.state.getCompoundOrEmpty("last_cycle").copy());
		check(second.getStringOr("ending", "").equals("absorb") && second.getIntOr("cycle", 0) == 1 && second.getIntOr("deaths", 0) == 1 && second.getIntOr("karma", 0) == -60,
			"the second cycle's recap: Absorbed, cycle 2, one death, karma -60: " + second);
		cursor(ctx, 2, 2);
		shot(ctx, "recap_absorb_cycle2");
		// ---- a long later cycle, as a group, to Set Down the Tools (written in directly, for the picture)
		s.runOnServer(srv -> {
			PlayerState ps = PlayerState.of(player(srv));
			CompoundTag r = new CompoundTag();
			r.putString("ending", "tools");
			r.putInt("cycle", 3);
			r.putInt("ticks", 20 * (3 * 3600 + 7 * 60 + 41));
			r.putInt("deaths", 7);
			r.putInt("lost", 4);
			r.putInt("rebuilt", 9);
			r.putInt("souls", 12840);
			r.putInt("pages", 6);
			r.putInt("pages_total", 47);
			r.putInt("quests", 9);
			r.putInt("quests_total", 64);
			r.putInt("quests_all", 70);
			r.putInt("dolls", 10);
			r.putInt("worlds", 0x7FE);
			r.putInt("bosses", 0x7FF);
			r.putInt("group_bosses", 0x7FF);
			r.putInt("karma", 64);
			r.putInt("members", 3);
			r.putString("cls", "guardian");
			r.putInt("gear", 5);
			ListTag trials = new ListTag();
			CompoundTag t1 = new CompoundTag();
			t1.putString("key", "w7");
			t1.putInt("ticks", 20 * 201 + 7);
			trials.add(t1);
			r.put("trials", trials);
			r.putString("name", player(srv).getGameProfile().name());
			ps.tag().put(CycleStats.LAST, r);
			ps.sync();
		});
		ctx.waitTicks(5);
		cursor(ctx, 2, 2);
		ctx.setScreen(() -> new RecapScreen(null));
		ctx.waitTicks(80);
		shot(ctx, "recap_tools_cycle4");
		// ---- German and French: the stall's black market and the recap
		for (String code : new String[]{"de_de", "fr_fr"}) {
			language(ctx, code);
			String sfx = "_" + code.substring(0, 2);
			cursor(ctx, 2, 2);
			ctx.setScreen(() -> new RecapScreen(null));
			ctx.waitTicks(80);
			shot(ctx, "recap_tools" + sfx);
			ctx.setScreen(() -> null);
			s.runOnServer(srv -> {
				summon(srv, "prisoner");
				karma(srv, -40);
			});
			s.runCommand("execute as @p at @s run tp @s ~ ~ ~ 270 10");
			ctx.waitTicks(10);
			openTrades(ctx, sp);
			ctx.waitTicks(16);
			cursor(ctx, 2, 2);
			check(stallOpen(ctx), "the stall opens in " + code);
			shot(ctx, "stall_black_market" + sfx);
			closeTrades(ctx);
			s.runOnServer(srv -> {
				summon(srv, "doll_peddler");
				karma(srv, 40);
			});
			ctx.waitTicks(6);
			openTrades(ctx, sp);
			ctx.waitTicks(16);
			shot(ctx, "stall_peddler" + sfx);
			closeTrades(ctx);
		}
		// ---- the smallest GUI the game allows, in a narrow window (last: the cursor is not trusted after it)
		resize(ctx, 640, 480);
		scale(ctx, 0);
		ctx.setScreen(() -> new RecapScreen(null));
		ctx.waitTicks(70);
		check(ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.mc.McClient.screen(mc).height >= RecapScreen.RH + RecapScreen.ABOVE + RecapScreen.BELOW && fr.achedon12.matriochka.client.mc.McClient.screen(mc).width >= RecapScreen.RW), "the recap fits a 640x480 window");
		shot(ctx, "recap_narrow");
		resize(ctx, 1920, 1080);
		scale(ctx, 3);
	}
}
