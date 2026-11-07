package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.net.StationMenu;
import java.util.List;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * A station is a lacquered cabinet painted for its world: recipes are drawers that slide in when it opens and pull
 * out under the cursor, each with a gilded groove that fills as you gather its ingredients. The machine's state is
 * a glass doll in the niche on the right, its liquid rising with the station's condition.
 */
public class StationScreen extends AbstractContainerScreen<StationMenu> {
	private static final String[] PINS = {"I", "II", "III", "IV"};
	private static final int ROWS = 5, ROW_H = 22, CAB_X = 12, CAB_Y = 22;
	private final List<Recipes.Recipe> recipes;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(300, 160);
	private final int world;
	private int scroll;
	private float scrollShown, fillShown, flash;
	private final float[] pull, progress;
	private final long[] pressed;
	private boolean wasReady;
	private long readyAt = -1, last = Ui.now();

	public StationScreen(StationMenu menu, Inventory inv, Component title) {
		super(menu, inv, title, StationMenu.PANEL_W, StationMenu.PANEL_H);
		this.recipes = Recipes.of(menu.data.station());
		this.world = Ui.stationWorld(menu.data.station());
		this.inventoryLabelY = 128;
		this.inventoryLabelX = 48;
		this.pull = new float[recipes.size()];
		this.progress = new float[recipes.size()];
		this.pressed = new long[recipes.size()];
		java.util.Arrays.fill(pressed, -1);
	}

	private void click(int id) {
		minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
	}

	private boolean hasSlot() {
		return menu.data.station().equals("soul_altar") || menu.data.station().equals("class_table");
	}

	private boolean jailer() {
		return menu.data.station().equals("jailer_table");
	}

	@Override
	protected void init() {
		super.init();
		if (Ui.now() - motion.openedAt() < 100) Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, 1f, 0.6f);
		buttons.clear();
		int l = leftPos, t = topPos;
		switch (menu.data.station()) {
			case "soul_altar" -> {
				buttons.add(l + 150, t + 30, 92, 18, Component.translatable("station.matriochka.purify"), () -> click(200));
				buttons.add(l + 150, t + 52, 92, 18, Component.translatable("station.matriochka.devour"), () -> click(201));
				buttons.add(l + 150, t + 74, 92, 18, Component.translatable("station.matriochka.recharge"), () -> click(202));
			}
			case "class_table" -> {
				buttons.add(l + 150, t + 38, 92, 18, Component.translatable("station.matriochka.upgrade"), () -> click(210));
				buttons.add(l + 150, t + 60, 92, 18, Component.translatable("station.matriochka.reroll"), () -> click(211));
				buttons.add(l + 150, t + 82, 92, 18, Component.translatable("station.matriochka.layer"), () -> click(212));
				// the talent trees open in their own cabinet
				buttons.add(l + 150, t + 117, 92, 16, Component.translatable("talents.matriochka.open"), () -> {
					minecraft.player.closeContainer();
					fr.achedon12.matriochka.client.mc.McClient.setScreen(minecraft, new TalentScreen());
				});
			}
			case "abyssal_press" -> buttons.add(l + 199, t + 113, 46, 16, Component.translatable("station.matriochka.refill"), () -> click(220));
			case "inverter" -> buttons.add(l + 199, t + 52, 46, 16, Component.translatable("station.matriochka.invert"), () -> click(220));
			case "jailer_table" -> {
				for (int i = 0; i < 4; i++) {
					int pin = i;
					buttons.add(l + 199 + (i % 2) * 24, t + 92 + (i / 2) * 20, 22, 18, Component.literal(PINS[i]), () -> click(100 + pin));
				}
			}
			default -> {}
		}
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_CLOSE, 1.05f, 0.55f);
		motion.close(super::onClose);
	}

	@Override
	protected void containerTick() {
		super.containerTick();
		motion.tick();
	}

	private int[] have(Recipes.Recipe r) {
		int need = 0, got = 0;
		for (Recipes.Ing ing : r.inputs()) {
			need += ing.count();
			got += Math.min(ing.count(), Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())));
		}
		return new int[]{got, need};
	}

	private float condition(boolean ready) {
		return switch (menu.data.station()) {
			case "ash_foundry" -> Math.min(1f, menu.sync.get(1) / 3f);
			case "lightning_forge" -> menu.sync.get(1) / 8f;
			case "spore_vat" -> menu.sync.get(6) / 300f;
			case "jailer_table" -> menu.sync.get(5) / 3f;
			default -> ready ? 1f : 0f;
		};
	}

	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		int l = leftPos, t = topPos;
		motion.push(g, l + imageWidth / 2f, t + imageHeight / 2f);
		Ui.sprite(g, "station_" + menu.data.station(), l, t, imageWidth, imageHeight);
		Ui.plate(g, font, title, l + imageWidth / 2, t + 1, world, l * 7L);
		for (Slot s : menu.slots) Ui.sprite(g, "slot", l + s.x - 1, t + s.y - 1, 18, 18);
		Ui.wanderingGlint(g, new int[][]{{l + 3, t + 3}, {l + imageWidth - 4, t + 3}, {l + 3, t + imageHeight - 4}, {l + imageWidth - 4, t + imageHeight - 4},
			{l + 20, t + imageHeight - 3}, {l + 236, t + imageHeight - 3}, {l + 22, t + 141}, {l + 234, t + 141}}, 1500, world * 97L);
		boolean ready = menu.sync.get(0) == 1;
		if (hasSlot()) {
			altar(g, l, t, mx, my);
		} else {
			if (StationLayouts.has(menu.data.station())) pieces(g, l, t, mx, my, dt);
			else drawers(g, l, t, mx, my, dt);
			niche(g, l, t, ready, dt, mx, my);
		}
		motion.pop(g);
	}

	private void altar(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		Ui.paper(g, l + 12, t + 22, 128, 100);
		// the help fits the parchment: beside the socket the lines stay short, under it they run the full width;
		// whatever does not fit is in the tooltip
		Component help = Component.translatable("station.matriochka." + menu.data.station() + ".help");
		var narrow = font.split(help, 96);
		int shown = 0, y = t + 28;
		for (; shown < narrow.size() && y < t + 90; shown++, y += 9) g.text(font, narrow.get(shown), l + 18, y, Ui.INK, false);
		boolean cut = false;
		if (shown < narrow.size()) {
			StringBuilder rest = new StringBuilder();
			for (int i = shown; i < narrow.size(); i++) {
				StringBuilder line = new StringBuilder();
				narrow.get(i).accept((idx, style, cp) -> { line.appendCodePoint(cp); return true; });
				rest.append(line).append(' ');
			}
			var wide = font.split(Component.literal(rest.toString().trim()), 118);
			for (int i = 0; i < wide.size(); i++, y += 9) {
				if (y + 9 > t + 120) { cut = true; break; }
				g.text(font, wide.get(i), l + 18, y, Ui.INK, false);
			}
		}
		if (cut && mx >= l + 12 && mx < l + 140 && my >= t + 22 && my < t + 122) g.setTooltipForNextFrame(font, help, mx, my);
		Ui.sprite(g, "slot", l + 119, t + 69, 18, 18);
		// a soft halo pulses round the item socket
		float pulse = 0.25f + 0.2f * (float) Math.sin(Ui.now() / 420.0);
		Ui.sprite(g, "glow", l + 116, t + 66, 24, 24, Ui.white(pulse));
		// the souls the altar and the class table work with
		int souls = MatrioClient.state.getIntOr("souls", 0);
		int soulsY = menu.data.station().equals("soul_altar") ? t + 113 : t + 103;
		Ui.sprite(g, "lantern", l + 160, soulsY - 3, 9, 13);
		JournalScreen.lanternFlame(g, l + 160, soulsY - 3, 1f);
		Ui.embossed(g, font, Component.translatable("hud.matriochka.souls", souls), l + 174, soulsY, Ui.GOLD);
		if (menu.data.station().equals("soul_altar")) rechargeCost(g, l + 150, t + 94, souls, mx, my);
	}

	/** Under the Doll of Life button: what a layer costs, souls and the rare resources of the current world, red when short. */
	private void rechargeCost(GuiGraphicsExtractor g, int x, int y, int souls, int mx, int my) {
		int w = Stations.rechargeWorld(MatrioClient.state.getIntOr("here", 0), MatrioClient.state.getIntOr("done", 0));
		List<net.minecraft.world.item.Item> rares = Stations.rareResources(w);
		int have = Stations.countRares(minecraft.player.getInventory(), w);
		Component sc = Component.literal(String.valueOf(Stations.RECHARGE_SOULS));
		Ui.embossed(g, font, sc, x + 2, y + 4, souls >= Stations.RECHARGE_SOULS ? Ui.GOLD : Ui.WARN);
		int ix = x + 4 + font.width(sc);
		Component plus = Component.literal("+ " + Stations.RECHARGE_RARES);
		Ui.embossed(g, font, plus, ix, y + 4, have >= Stations.RECHARGE_RARES ? Ui.LIGHT : Ui.WARN);
		ix += font.width(plus) + 2;
		// the rare resources take turns in one socket when there are more than fit
		int shown = Math.min(rares.size(), 3);
		int first = rares.size() > 3 ? (int) ((Ui.now() / 1200) % rares.size()) : 0;
		for (int i = 0; i < shown; i++) g.item(new ItemStack(rares.get((first + i) % rares.size())), ix + i * 15, y);
		if (mx >= x && mx < x + 92 && my >= y - 20 && my < y + 16) {
			List<Component> tip = new java.util.ArrayList<>();
			tip.add(Component.translatable("station.matriochka.recharge.tip", Stations.RECHARGE_SOULS, Stations.RECHARGE_RARES, Component.translatable("world.matriochka." + w)));
			for (net.minecraft.world.item.Item it : rares) tip.add(Component.literal("  ").append(new ItemStack(it).getHoverName()).withStyle(net.minecraft.ChatFormatting.GRAY));
			tip.add(Component.translatable("station.matriochka.recharge.have", have, souls).withStyle(have >= Stations.RECHARGE_RARES && souls >= Stations.RECHARGE_SOULS ? net.minecraft.ChatFormatting.GREEN : net.minecraft.ChatFormatting.RED));
			g.setComponentTooltipForNextFrame(font, tip, mx, my);
		}
	}

	/** Index of the recipe piece under the cursor, or -1. */
	private int pieceAt(double mx, double my) {
		String st = menu.data.station();
		int[] sz = StationLayouts.size(st);
		for (int i = 0; i < recipes.size(); i++) {
			int[] p = StationLayouts.at(st, i, recipes.size());
			int x = leftPos + p[0], y = topPos + p[1];
			if (mx >= x && mx < x + sz[0] && my >= y && my < y + sz[1]) return i;
		}
		return -1;
	}

	/** The automation funnel of a piece: in its top-right corner. */
	private int[] piecePin(int i) {
		String st = menu.data.station();
		int[] sz = StationLayouts.size(st);
		int[] p = StationLayouts.at(st, i, recipes.size());
		int px = sz[0] >= 56 ? p[0] + sz[0] - PIN_W - 2 : p[0] + sz[0] - PIN_W + 2;
		return new int[]{leftPos + px, topPos + p[1] - (sz[0] >= 56 ? -4 : 3)};
	}

	private boolean overPiecePin(double mx, double my, int i) {
		int[] q = piecePin(i);
		return mx >= q[0] - 1 && mx < q[0] + PIN_W + 1 && my >= q[1] - 1 && my < q[1] + PIN_H + 1;
	}

	private int hoverPiece = -1;
	private float barShown;

	/**
	 * The station's own layout: its backdrop, then every recipe as a piece of the station (jar, crucible, key tag,
	 * plate, rune, porthole, medallion, stratum, banner) that lights when the player carries everything, rises under
	 * the cursor and sinks when clicked; the bar under them shows the recipe of the piece under the cursor.
	 */
	private void pieces(GuiGraphicsExtractor g, int l, int t, int mx, int my, float dt) {
		String st = menu.data.station();
		Ui.sprite(g, "decor_" + st, l + StationLayouts.DECOR_X, t + StationLayouts.DECOR_Y, StationLayouts.DECOR_W, StationLayouts.DECOR_H);
		int[] sz = StationLayouts.size(st);
		int[] io = StationLayouts.itemAt(st);
		int hover = motion.closing() ? -1 : pieceAt(mx, my);
		if (hover >= 0) hoverPiece = hover;
		else if (hoverPiece < 0 || hoverPiece >= recipes.size()) hoverPiece = Math.max(0, menu.sync.get(7) - 1);
		for (int i = 0; i < recipes.size(); i++) {
			Recipes.Recipe r = recipes.get(i);
			int[] p = StationLayouts.at(st, i, recipes.size());
			int[] hv = have(r);
			boolean can = hv[0] >= hv[1];
			pull[i] = Ui.approach(pull[i], i == hover ? 1 : 0, 14, dt);
			// the pieces come in one after the other when the cabinet opens
			float in = Ui.easeOut(Ui.since(motion.openedAt() + 60L + i * 55L, 280));
			float press = pressed[i] < 0 ? 0 : 1 - Ui.since(pressed[i], 200);
			int x = l + p[0], y = t + p[1] + Math.round((1 - in) * 10 - pull[i] * 2 + press * 2);
			float a = in;
			if (a < 0.02f) continue;
			if (can) Ui.sprite(g, "glow", x - 6, y - 6, sz[0] + 12, sz[1] + 12, Ui.white((0.18f + 0.1f * (float) Math.sin(Ui.now() / 600.0 + i)) * a));
			Ui.sprite(g, "tile_" + st + (can ? "_ready" : ""), x, y, sz[0], sz[1], Ui.white(a));
			if (pull[i] > 0.02f) g.outline(x - 1, y - 1, sz[0] + 2, sz[1] + 2, Ui.alpha(0xFFF4D27A, pull[i] * a));
			ItemStack out = new ItemStack(Stations.resolve(r.output()), r.count());
			g.item(out, x + io[0], y + io[1]);
			g.itemDecorations(font, out, x + io[0], y + io[1]);
			if (sz[0] >= 56) {
				// the long pieces (mirrored rows, strata) show the ingredients that fit beside the result
				int ix = x + io[0] + 22;
				for (Recipes.Ing ing : r.inputs()) {
					if (ix + 16 > x + sz[0] - 2) break;
					ItemStack s = new ItemStack(Stations.resolve(ing.id()), ing.count());
					g.item(s, ix, y + io[1]);
					g.itemDecorations(font, s, ix, y + io[1]);
					if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) g.fill(ix, y + io[1] + 15, ix + 16, y + io[1] + 16, 0xFFD8402A);
					ix += 18;
				}
			}
			int[] q = piecePin(i);
			if (i == hover || i == menu.sync.get(7) - 1) funnel(g, q[0], q[1] + Math.round((1 - in) * 10), i == menu.sync.get(7) - 1, i == hover && overPiecePin(mx, my, i), i);
		}
		bar(g, l, t, dt);
		pinTooltipPieces(g, mx, my);
	}

	/** The bar under the pieces: the recipe under the cursor (or the one the funnel keeps making), in the row material. */
	private void bar(GuiGraphicsExtractor g, int l, int t, float dt) {
		if (recipes.isEmpty()) return;
		int i = Math.min(hoverPiece, recipes.size() - 1);
		Recipes.Recipe r = recipes.get(i);
		int[] hv = have(r);
		boolean can = hv[0] >= hv[1];
		barShown = Ui.approach(barShown, hv[1] == 0 ? 1 : hv[0] / (float) hv[1], 8, dt);
		int x = l + StationLayouts.BAR_X, y = t + StationLayouts.BAR_Y;
		float in = Ui.easeOut(Ui.since(motion.openedAt() + 200L, 300));
		Ui.sprite(g, rowSprite(can), x, y, 174, 21, Ui.white(in));
		ItemStack out = new ItemStack(Stations.resolve(r.output()), r.count());
		g.item(out, x + 9, y + 2);
		g.itemDecorations(font, out, x + 9, y + 2);
		int ix = x + 40;
		for (Recipes.Ing ing : r.inputs()) {
			ItemStack s = new ItemStack(Stations.resolve(ing.id()), ing.count());
			g.item(s, ix, y + 2);
			g.itemDecorations(font, s, ix, y + 2);
			if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) {
				g.fill(ix, y + 2, ix + 16, y + 18, 0x9C140A08);
				g.fill(ix, y + 17, ix + 16, y + 18, 0xFFD8402A);
			}
			ix += 21;
		}
		// the recipe's name, right of its ingredients, while there is room for it
		Component name = out.getHoverName();
		int room = x + 158 - ix;
		if (room > 30) {
			var line = font.split(name, room).getFirst();
			g.text(font, line, ix + 2, y + 6, Ui.LIGHT, true);
		}
		int fw = Math.round(124 * Ui.clamp01(barShown));
		Ui.spritePart(g, "drawer_fill", 124, 2, 0, 0, x + 38, y + 18, fw, 1, 0xFFFFFFFF);
		if (can) Ui.sheen(g, x + 38, y + 16, 124, 4, 2600, 77L, 0.9f);
	}

	private void pinTooltipPieces(GuiGraphicsExtractor g, int mx, int my) {
		int i = pieceAt(mx, my);
		if (i < 0 || motion.closing() || !overPiecePin(mx, my, i)) return;
		boolean on = i == menu.sync.get(7) - 1;
		List<Component> tip = new java.util.ArrayList<>();
		tip.add(Component.translatable(on ? "station.matriochka.auto.on" : "station.matriochka.auto.pick").withStyle(net.minecraft.ChatFormatting.GOLD));
		tip.add(Component.translatable("station.matriochka.auto.how").withStyle(net.minecraft.ChatFormatting.GRAY));
		String cond = "station.matriochka.auto.cond." + menu.data.station();
		if (net.minecraft.locale.Language.getInstance().has(cond)) tip.add(Component.translatable(cond).withStyle(net.minecraft.ChatFormatting.DARK_AQUA));
		g.setComponentTooltipForNextFrame(font, tip, mx, my);
	}

	private void drawers(GuiGraphicsExtractor g, int l, int t, int mx, int my, float dt) {
		scrollShown = Ui.approach(scrollShown, scroll, 16, dt);
		int x0 = l + CAB_X, y0 = t + CAB_Y;
		g.enableScissor(l + 10, t + 20, l + 188, t + 133);
		int first = Math.max(0, (int) Math.floor(scrollShown));
		for (int i = first; i < recipes.size() && i < first + ROWS + 1; i++) {
			Recipes.Recipe r = recipes.get(i);
			int y = y0 + Math.round((i - scrollShown) * ROW_H);
			boolean hover = !motion.closing() && mx >= x0 && mx < x0 + 174 && my >= Math.max(y, t + 20) && my < Math.min(y + 21, t + 133);
			int[] hv = have(r);
			boolean can = hv[0] >= hv[1];
			pull[i] = Ui.approach(pull[i], hover ? 1 : 0, 14, dt);
			progress[i] = Ui.approach(progress[i], hv[1] == 0 ? 1 : hv[0] / (float) hv[1], 6, dt);
			// slides in from the left when the cabinet opens, one drawer after the other
			int row = i - scroll;
			float in = Ui.easeOut(Ui.since(motion.openedAt() + 40L + Math.max(0, row) * 45L, 260));
			int slideIn = Math.round((1 - in) * -190);
			float press = pressed[i] < 0 ? 0 : 1 - Ui.since(pressed[i], 180);
			int dx = slideIn + Math.round(pull[i] * 4 - press * 3);
			if (dx > 0) Ui.sprite(g, "drawer_side", x0, y + 1, dx + 2, 19);
			int x = x0 + dx;
			// the drawer lifts: a shadow under it while pulled out
			if (pull[i] > 0.02f) g.fill(x + 2, y + 21, x + 176, y + 22, Ui.alpha(0xFF000000, 0.45f * pull[i]));
			// each station's rows are made of its own material (row_<station>); the workbench keeps its wooden drawers
			Ui.sprite(g, rowSprite(can), x, y, 174, 21);
			if (pull[i] > 0.02f) {
				g.fill(x + 1, y + 1, x + 173, y + 20, Ui.alpha(0xFFFFE6B0, 0.10f * pull[i]));
				g.outline(x, y, 174, 21, Ui.alpha(0xFFF4D27A, pull[i]));
			}
			g.item(new ItemStack(Stations.resolve(r.output()), r.count()), x + 9, y + 2);
			g.itemDecorations(font, new ItemStack(Stations.resolve(r.output()), r.count()), x + 9, y + 2);
			int ix = x + 40;
			for (Recipes.Ing ing : r.inputs()) {
				ItemStack s = new ItemStack(Stations.resolve(ing.id()), ing.count());
				g.item(s, ix, y + 2);
				g.itemDecorations(font, s, ix, y + 2);
				if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) {
					g.fill(ix, y + 2, ix + 16, y + 18, 0x9C140A08);
					g.fill(ix, y + 17, ix + 16, y + 18, 0xFFD8402A);
				}
				ix += 21;
			}
			// the gilded groove fills with what you already carry; full, it shines
			int fw = Math.round(124 * Ui.clamp01(progress[i]));
			Ui.spritePart(g, "drawer_fill", 124, 2, 0, 0, x + 38, y + 18, fw, 1, 0xFFFFFFFF);
			if (can) Ui.sheen(g, x + 38, y + 16, 124, 4, 2600, i * 431L, 0.9f);
			if (can && hover) Ui.sheen(g, x + 3, y + 3, 30, 15, 1400, i * 211L, 0.6f);
			funnel(g, x + PIN_X, y + PIN_Y, i == menu.sync.get(7) - 1, overPin(mx, my, x, y) && hover, i);
		}
		g.disableScissor();
		pinTooltip(g, l, t, mx, my);
		if (recipes.size() > ROWS) {
			int track = 108, th = Math.max(12, track * ROWS / recipes.size());
			int ty = t + 22 + Math.round((track - th) * scrollShown / Math.max(1, recipes.size() - ROWS));
			Ui.sprite(g, "thumb", l + 189, ty, 4, th);
		}
	}

	private String rowSprite(boolean ready) {
		String st = menu.data.station();
		if (st.equals("matrix_workbench")) return ready ? "drawer_ready" : "drawer";
		return "row_" + st + (ready ? "_ready" : "");
	}

	/** Share of this station's recipes the player can make right now, 0..1. */
	private float craftable() {
		if (recipes.isEmpty()) return 0;
		int n = 0;
		for (Recipes.Recipe r : recipes) {
			int[] hv = have(r);
			if (hv[0] >= hv[1]) n++;
		}
		return n / (float) recipes.size();
	}

	/** Where the automation funnel sits on a drawer, and its size. */
	private static final int PIN_X = 161, PIN_Y = 4, PIN_W = 11, PIN_H = 12;

	private boolean overPin(int mx, int my, int x, int y) {
		return mx >= x + PIN_X - 1 && mx < x + PIN_X + PIN_W + 1 && my >= y + PIN_Y - 1 && my < y + PIN_Y + PIN_H + 1;
	}

	/**
	 * The little gilded funnel on a drawer: lit, the station keeps making that recipe from its hoppers. Painted with the
	 * cabinet's gold leaf, a glow behind it when chosen.
	 */
	private void funnel(GuiGraphicsExtractor g, int x, int y, boolean on, boolean hover, int i) {
		if (on) Ui.sprite(g, "glow", x - 6, y - 5, PIN_W + 12, PIN_H + 10, Ui.white(0.45f + 0.15f * (float) Math.sin(Ui.now() / 450.0 + i)));
		int gold = on ? 0xFFF4D27A : hover ? 0xFFD8A850 : 0xC896682A;
		int dark = on ? 0xFF8A5A1A : 0xC85A3A16;
		// rim, bowl narrowing in four steps, spout
		g.fill(x, y, x + PIN_W, y + 2, gold);
		g.fill(x, y + 2, x + PIN_W, y + 3, dark);
		for (int k = 0; k < 4; k++) g.fill(x + 1 + k, y + 3 + k, x + PIN_W - 1 - k, y + 4 + k, k % 2 == 0 ? gold : Ui.alpha(gold, 0.85f));
		g.fill(x + 4, y + 7, x + PIN_W - 4, y + PIN_H, gold);
		g.fill(x + 5, y + 8, x + PIN_W - 5, y + PIN_H, dark);
		if (on) Ui.glint(g, x + 3, y + 1, Math.floorMod(Ui.now() + i * 300L, 2400L) / 1000f, 5);
	}

	/** The recipe row under the cursor whose funnel is hovered, or -1. */
	private int pinAt(double mx, double my) {
		int l = leftPos, t = topPos;
		if (mx < l + CAB_X || mx >= l + CAB_X + 174 || my < t + CAB_Y || my >= t + CAB_Y + ROW_H * ROWS) return -1;
		int idx = scroll + (int) ((my - t - CAB_Y) / ROW_H);
		if (idx >= recipes.size()) return -1;
		int x = l + CAB_X + Math.round(pull[idx] * 4), y = t + CAB_Y + (idx - scroll) * ROW_H;
		return overPin((int) mx, (int) my, x, y) ? idx : -1;
	}

	private void pinTooltip(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		int idx = pinAt(mx, my);
		if (idx < 0 || motion.closing()) return;
		boolean on = idx == menu.sync.get(7) - 1;
		List<Component> tip = new java.util.ArrayList<>();
		tip.add(Component.translatable(on ? "station.matriochka.auto.on" : "station.matriochka.auto.pick").withStyle(net.minecraft.ChatFormatting.GOLD));
		tip.add(Component.translatable("station.matriochka.auto.how").withStyle(net.minecraft.ChatFormatting.GRAY));
		String cond = "station.matriochka.auto.cond." + menu.data.station();
		if (net.minecraft.locale.Language.getInstance().has(cond)) tip.add(Component.translatable(cond).withStyle(net.minecraft.ChatFormatting.DARK_AQUA));
		g.setComponentTooltipForNextFrame(font, tip, mx, my);
	}

	/** The Inverter's niche: two sockets facing each other, the swap mark between them, the warning below. */
	private void inverterNiche(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		int ax = l + StationMenu.INVERTER_A_X, bx = l + StationMenu.INVERTER_B_X, y = t + StationMenu.INVERTER_Y;
		float pulse = 0.2f + 0.15f * (float) Math.sin(Ui.now() / 380.0);
		Ui.sprite(g, "glow", ax - 4, y - 4, 24, 24, Ui.white(pulse));
		Ui.sprite(g, "glow", bx - 4, y - 4, 24, 24, Ui.white(0.35f - pulse));
		Component swap = Component.literal("<>");
		Ui.embossed(g, font, swap, (ax + 16 + bx) / 2 - font.width(swap) / 2, y + 4, Ui.GOLD);
		Component desc = Component.translatable("station.matriochka.inverter.help");
		var lines = font.split(desc, 50);
		for (int i = 0; i < Math.min(6, lines.size()); i++) g.text(font, lines.get(i), l + 198, t + 74 + i * 9, Ui.MUTED, false);
		if (lines.size() > 6 && mx >= l + 195 && mx < l + 248 && my >= t + 70 && my < t + 133) g.setTooltipForNextFrame(font, desc, mx, my);
	}

	/**
	 * The workbench's niche is its crafting grid: a lacquered plate under the nine slots, a gilded arrow down to the
	 * result, which glows while the grid spells a recipe. The drawers fill the grid; the result is taken by hand.
	 */
	private void gridNiche(GuiGraphicsExtractor g, int l, int t) {
		int gx = l + StationMenu.GRID_X - 2, gy = t + StationMenu.GRID_Y - 2;
		g.fill(gx - 1, gy - 1, gx + 57, gy + 57, 0xFF2A0E0A);
		g.outline(gx - 2, gy - 2, 60, 60, 0xFFC8963C);
		boolean has = menu.slots.get(menu.resultSlot).hasItem();
		int ax = l + StationMenu.RESULT_X + 8, ay = t + StationMenu.GRID_Y + 56;
		int gold = has ? 0xFFF4D27A : 0x80C8963C;
		g.fill(ax - 1, ay, ax + 1, ay + 6, gold);
		for (int k = 0; k < 4; k++) g.fill(ax - 4 + k, ay + 6 + k, ax + 4 - k, ay + 7 + k, gold);
		int rx = l + StationMenu.RESULT_X, ry = t + StationMenu.RESULT_Y;
		if (has) Ui.sprite(g, "glow", rx - 8, ry - 8, 32, 32, Ui.white(0.45f + 0.2f * (float) Math.sin(Ui.now() / 420.0)));
		g.outline(rx - 2, ry - 2, 20, 20, has ? 0xFFF4D27A : 0xFF96682A);
		Component hint = Component.translatable(has ? "station.matriochka.grid.take" : "station.matriochka.grid.fill");
		var lines = font.split(hint, 52);
		for (int i = 0; i < Math.min(2, lines.size()); i++) g.text(font, lines.get(i), l + 222 - font.width(lines.get(i)) / 2, t + 112 + i * 9, has ? Ui.OK : Ui.MUTED, false);
	}

	private void niche(GuiGraphicsExtractor g, int l, int t, boolean ready, float dt, int mx, int my) {
		if (menu.workbench()) {
			gridNiche(g, l, t);
			return;
		}
		if (menu.data.station().equals("inverter")) {
			inverterNiche(g, l, t, mx, my);
			return;
		}
		if (ready && !wasReady) {
			readyAt = Ui.now();
			if (Ui.now() - motion.openedAt() > 400) Ui.sound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.6f, 0.6f);
		}
		wasReady = ready;
		float target = Ui.clamp01(condition(ready));
		if (Math.abs(target - fillShown) > 0.02f && target > fillShown) flash = 1;
		fillShown = Ui.approach(fillShown, target * Ui.easeOut(Ui.since(motion.openedAt() + 150, 500)), 4, dt);
		flash = Ui.approach(flash, 0, 3, dt);
		int vx = l + 202, vy = t + 23, vw = 40, vh = 56;
		if (StationInstruments.has(menu.data.station())) {
			// each station has its own instrument; the raw reading is the one the station syncs
			String st = menu.data.station();
			int value = switch (st) {
				case "spore_vat" -> menu.sync.get(6);
				case "jailer_table" -> menu.sync.get(5);
				default -> menu.sync.get(1);
			};
			long day = minecraft.level == null ? 0 : minecraft.level.getDefaultClockTime();
			StationInstruments.draw(g, st, world, l + 198, vy, fillShown, ready, value, craftable(), day);
			if (ready) {
				float since = readyAt < 0 ? 1 : Ui.since(readyAt, 900);
				if (since < 1) Ui.sprite(g, "glow", l + 210, vy + 16, 24, 24, Ui.alpha(0xFFFFFFFF, (1 - since) * 0.6f));
			}
		} else {
		Ui.sprite(g, "vessel_back", vx, vy, vw, vh);
		// liquid: the body of the doll spans rows 8..48 of the sprite; the surface wobbles a little
		int top = vy + 8, bottom = vy + 48;
		int level = bottom - Math.round((bottom - top) * fillShown);
		int liquid = Ui.worldColor(world);
		if (fillShown > 0.01f) {
			int wob = Math.round((float) Math.sin(Ui.now() / 300.0) * 0.7f);
			int lv = Math.min(bottom, level + wob);
			Ui.spritePart(g, "vessel_liquid", vw, vh, 0, lv - vy, vx, lv, vw, bottom - lv, liquid);
			g.fill(vx + 6, lv, vx + vw - 6, lv + 1, Ui.white(0.25f));
			long tt = Ui.now();
			for (int b = 0; b < 3; b++) {
				float p = Math.floorMod(tt + b * 777L, 2300L) / 2300f;
				int by = Math.round(bottom - 2 - p * (bottom - lv - 2));
				int bx = vx + 14 + b * 5 + Math.round((float) Math.sin(p * 9 + b) * 1.5f);
				if (by > lv + 1) Ui.sprite(g, "bubble", bx, by, 3, 3, Ui.white(0.7f * (1 - p)));
			}
			if (flash > 0.01f) Ui.spritePart(g, "vessel_liquid", vw, vh, 0, lv - vy, vx, lv, vw, bottom - lv, Ui.white(0.5f * flash));
		}
		Ui.sprite(g, "vessel_front", vx, vy, vw, vh);
		if (ready) {
			float since = readyAt < 0 ? 1 : Ui.since(readyAt, 900);
			Ui.sprite(g, "glow", vx + 8, vy + 10, 24, 24, Ui.alpha(0xFFFFFFFF, 0.25f + 0.2f * (float) Math.sin(Ui.now() / 500.0) + (1 - since) * 0.5f));
			Ui.glint(g, vx + 13, vy + 18, Math.floorMod(Ui.now(), 2200L) / 900f, 8);
		}
		}
		int sx = l + 198;
		if (!jailer()) {
			int ferment = menu.sync.get(6);
			Component st = menu.data.station().equals("spore_vat")
				? Component.translatable("station.matriochka.ferment." + (ferment >= 300 ? "aged" : ferment >= 60 ? "ripe" : "fresh"))
				: Component.translatable(ready ? "station.matriochka.ready" : "station.matriochka.not_ready");
			Ui.embossed(g, font, st, l + 222 - font.width(st) / 2, t + 82, ready ? Ui.OK : Ui.WARN);
			Component desc = Component.translatable("block.matriochka." + menu.data.station() + ".desc");
			var lines = font.split(desc, 50);
			// the press keeps room under its text for the button that refills snorkel helmets
			int shown = menu.data.station().equals("abyssal_press") ? 2 : 4;
			for (int i = 0; i < Math.min(shown, lines.size()); i++) g.text(font, lines.get(i), sx, t + 94 + i * 9, Ui.MUTED, false);
			if (lines.size() > shown && mx >= l + 195 && mx < l + 248 && my >= t + 20 && my < (shown == 2 ? t + 112 : t + 133)) g.setTooltipForNextFrame(font, desc, mx, my);
		} else {
			for (int i = 0; i < 3; i++) {
				boolean ok = i < menu.sync.get(5);
				Component pin = Component.literal(PINS[menu.sync.get(2 + i)]);
				int px = l + 204 + i * 14;
				g.fill(px - 2, t + 80, px + 11, t + 90, ok ? 0x6040A030 : 0x60200808);
				g.outline(px - 2, t + 80, 13, 10, ok ? 0xFFA8E07A : 0xFF96682A);
				Ui.embossed(g, font, pin, px + 5 - font.width(pin) / 2, t + 81, ok ? Ui.OK : Ui.WARN);
			}
		}
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		motion.push(g, leftPos + imageWidth / 2f, topPos + imageHeight / 2f);
		super.extractRenderState(g, mx, my, a);
		buttons.draw(g, font, mx, my);
		motion.pop(g);
	}

	@Override
	protected void extractLabels(GuiGraphicsExtractor g, int mx, int my) {
		// the title sits on the plate drawn with the background
	}

	@Override
	public boolean mouseScrolled(double x, double y, double sx, double sy) {
		if (StationLayouts.has(menu.data.station())) return true;
		scroll = Math.max(0, Math.min(Math.max(0, recipes.size() - ROWS), scroll - (int) Math.signum(sy)));
		return true;
	}

	@Override
	public boolean keyPressed(KeyEvent event) {
		if (motion.closing()) return true;
		return super.keyPressed(event);
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		if (!hasSlot() && StationLayouts.has(menu.data.station())) {
			int i = pieceAt(event.x(), event.y());
			if (i >= 0) {
				if (overPiecePin(event.x(), event.y(), i)) {
					Ui.sound(SoundEvents.CHAIN_PLACE, 1.4f, 0.5f);
					click(i == menu.sync.get(7) - 1 ? 299 : 300 + i);
				} else {
					pressed[i] = Ui.now();
					Ui.sound(SoundEvents.WOODEN_BUTTON_CLICK_ON, 1.0f, 0.6f);
					click(i);
				}
				return true;
			}
		} else if (!hasSlot()) {
			int pin = pinAt(event.x(), event.y());
			if (pin >= 0) {
				Ui.sound(SoundEvents.CHAIN_PLACE, 1.4f, 0.5f);
				click(pin == menu.sync.get(7) - 1 ? 299 : 300 + pin);
				return true;
			}
			int l = leftPos, t = topPos;
			double mx = event.x(), my = event.y();
			if (mx >= l + CAB_X && mx < l + CAB_X + 174 && my >= t + CAB_Y && my < t + CAB_Y + ROW_H * ROWS) {
				int idx = scroll + (int) ((my - t - CAB_Y) / ROW_H);
				if (idx < recipes.size()) {
					pressed[idx] = Ui.now();
					Ui.sound(SoundEvents.WOODEN_BUTTON_CLICK_ON, 1.0f, 0.6f);
					click(idx);
					return true;
				}
			}
		}
		return super.mouseClicked(event, doubleClick);
	}
}
