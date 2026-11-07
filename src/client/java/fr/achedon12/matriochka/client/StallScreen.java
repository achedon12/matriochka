package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.net.Net;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundSelectTradePacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;

/**
 * The trades of the mod's peoples, at a painted market stall: a striped awning in the world's colour over a
 * lacquered cabinet. On the left, the trader's ledger lists every offer on parchment (what it costs, what it gives,
 * how many are left, the karma's discount or markup), the black market's goods "under the counter" in their own
 * plum section. On the right, the trader's plaque (world medallion, world, kind of trader, karma), the counter
 * with the selected trade's slots, and the player's inventory in the lower tray.
 * <p>
 * Only the screen is the mod's: the menu is vanilla's MerchantMenu, its slots sit where vanilla puts them (the panel
 * is laid out around them), and choosing a row sends the vanilla trade-select packet.
 */
public class StallScreen extends AbstractContainerScreen<MerchantMenu> {
	/** The panel, and where the menu's own coordinates start inside it (the vanilla slots land on the counter and the tray). */
	public static final int MW = 316, MH = 206, OX = 36, OY = 34;
	/** The ledger: page left/right, first row, row height, rows shown. */
	private static final int LX = 18, LR = 129, HEAD_Y = 28, ROW_Y = 42, ROW_H = 20, ROWS = 7;
	private static final int THUMB_X = 131;
	private static final String[] EMBLEMS = {"stillness", "toxin", "heat", "locks", "wind", "darkness", "gravity", "pressure", "time", "ground", "synthesis"};
	private static final int PLUM = 0xFF5A2466, PLUM_LIGHT = 0xFFD8A8E8;

	private static Net.MerchantInfoPayload pending;
	private static long pendingAt;

	private final Net.MerchantInfoPayload info;
	private final Ui.Motion motion = new Ui.Motion(300, 160);
	private final long opened = Ui.now();
	private int px, py, shopItem, scroll;
	private float scrollShown;
	private boolean dragging;
	private long last = Ui.now(), pickedAt = -1;
	private float[] hover = new float[0];

	/** One line of the ledger: an offer, or the heading of the black market's section. */
	private record Row(int offer, boolean header) {}

	public StallScreen(MerchantMenu menu, Inventory inv, Component title, Net.MerchantInfoPayload info) {
		super(menu, inv, title, MW, MH);
		this.info = info;
	}

	/** The server is about to open the trades of one of the mod's peoples. */
	public static void receive(Net.MerchantInfoPayload p) {
		pending = p;
		pendingAt = Ui.now();
	}

	/** Called for every merchant menu the server opens: true when the stall was opened in place of the vanilla screen. */
	public static boolean open(Minecraft mc, int containerId, Component title) {
		Net.MerchantInfoPayload info = pending;
		pending = null;
		if (info == null || mc.player == null || Ui.now() - pendingAt > 5000) return false;
		MerchantMenu menu = MenuType.MERCHANT.create(containerId, mc.player.getInventory());
		StallScreen screen = new StallScreen(menu, mc.player.getInventory(), title, info);
		mc.player.containerMenu = menu;
		fr.achedon12.matriochka.client.mc.McClient.setScreen(mc, screen);
		return true;
	}

	public Net.MerchantInfoPayload info() {
		return info;
	}

	public int selected() {
		return shopItem;
	}

	public int scrolled() {
		return scroll;
	}

	/** The centre of an offer's line in the ledger, on screen, or null when it is scrolled out (used by the showcase). */
	public int[] rowCenter(int offer) {
		List<Row> rows = rows();
		for (int i = 0; i < rows.size(); i++) {
			if (rows.get(i).header() || rows.get(i).offer() != offer) continue;
			if (i < scroll || i >= scroll + ROWS) return null;
			return new int[]{px + (LX + LR) / 2, py + ROW_Y + (i - scroll) * ROW_H + ROW_H / 2};
		}
		return null;
	}

	/** The centre of a menu slot on screen (used by the showcase). */
	public int[] slotCenter(int index) {
		Slot s = menu.getSlot(index);
		return new int[]{leftPos + s.x + 8, topPos + s.y + 8};
	}

	@Override
	protected void init() {
		super.init();
		px = leftPos;
		py = Math.max(0, topPos);
		leftPos = px + OX;
		topPos = py + OY;
		if (Ui.now() - motion.openedAt() < 100) {
			Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, 1.15f, 0.5f);
			Ui.sound(SoundEvents.WOODEN_TRAPDOOR_OPEN, 1.3f, 0.35f);
		}
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(SoundEvents.WOODEN_TRAPDOOR_CLOSE, 1.3f, 0.35f);
		motion.close(super::onClose);
	}

	@Override
	protected void containerTick() {
		super.containerTick();
		motion.tick();
	}

	@Override
	protected boolean hasClickedOutside(double mx, double my, int xo, int yo) {
		return mx < px || my < py || mx >= px + MW || my >= py + MH;
	}

	// ---------------------------------------------------------------- offers and rows
	private MerchantOffers offers() {
		return menu.getOffers();
	}

	/** Index of the first black-market offer (they come last). */
	private int firstContraband() {
		return Math.max(0, offers().size() - Math.max(0, info.contraband()));
	}

	private boolean contraband(int offer) {
		return info.contraband() > 0 && offer >= firstContraband();
	}

	private List<Row> rows() {
		List<Row> out = new ArrayList<>();
		int n = offers().size(), first = firstContraband();
		for (int i = 0; i < n; i++) {
			if (i == first && info.contraband() > 0) out.add(new Row(-1, true));
			out.add(new Row(i, false));
		}
		return out;
	}

	private int maxScroll() {
		return Math.max(0, rows().size() - ROWS);
	}

	private int carried(ItemStack want) {
		if (want.isEmpty()) return 0;
		int n = 0;
		Inventory inv = minecraft.player.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (ItemStack.isSameItemSameComponents(s, want)) n += s.getCount();
		}
		// what already sits in the payment slots counts too
		for (int i = 0; i < 2; i++) {
			ItemStack s = menu.getSlot(i).getItem();
			if (ItemStack.isSameItemSameComponents(s, want)) n += s.getCount();
		}
		return n;
	}

	private boolean affordable(MerchantOffer o) {
		return carried(o.getCostA()) >= o.getCostA().getCount() && (o.getCostB().isEmpty() || carried(o.getCostB()) >= o.getCostB().getCount());
	}

	/** The karma's change to the first price: negative for a discount, positive for a markup. */
	private static int priceDiff(MerchantOffer o) {
		return o.getCostA().getCount() - o.getBaseCostA().getCount();
	}

	private void select(int offer) {
		if (offer < 0 || offer >= offers().size()) return;
		shopItem = offer;
		pickedAt = Ui.now();
		menu.setSelectionHint(offer);
		menu.tryMoveItems(offer);
		minecraft.getConnection().send(new ServerboundSelectTradePacket(offer));
	}

	/** Selects an offer as a click on its row would (used by the showcase). */
	public void pick(int offer) {
		select(offer);
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		int l = px, t = py, w = Math.max(0, Math.min(10, info.world()));
		motion.push(g, l + MW / 2f, t + MH / 2f);
		Ui.sprite(g, "stall_" + w, l, t, MW, MH);
		// the name plain on the plate (a travelling merchant's custom name comes styled)
		Ui.plate(g, font, Component.literal(title.getString()), l + MW / 2, t + 1, w, l * 7L);
		for (Slot s : menu.slots) Ui.sprite(g, "slot", leftPos + s.x - 1, topPos + s.y - 1, 18, 18);
		Ui.wanderingGlint(g, new int[][]{{l + 3, t + 3}, {l + MW - 4, t + 3}, {l + 3, t + MH - 4}, {l + MW - 4, t + MH - 4}, {l + 157, t + 63}, {l + 302, t + 63}}, 1600, w * 41L + 5);
		ledger(g, l, t, mx, my, dt);
		plaque(g, l, t);
		counter(g, l, t, dt);
		motion.pop(g);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		motion.push(g, px + MW / 2f, py + MH / 2f);
		super.extractRenderState(g, mx, my, a);
		motion.pop(g);
		if (!motion.closing()) tooltips(g, mx, my);
	}

	@Override
	protected void extractLabels(GuiGraphicsExtractor g, int mx, int my) {
		// the trader's name sits on the plate, the ledger and the plaque carry the rest
	}

	/** The ledger on the left: a heading, then one ruled line per offer, scrolled by whole lines. */
	private void ledger(GuiGraphicsExtractor g, int l, int t, int mx, int my, float dt) {
		MerchantOffers offers = offers();
		Component head = Component.translatable("stall.matriochka.wares");
		g.text(font, head, l + LX, t + HEAD_Y, Ui.RED_INK, false);
		Component count = Component.literal(Integer.toString(offers.size()));
		g.text(font, count, l + LR - font.width(count), t + HEAD_Y, Ui.INK_SOFT, false);
		// a red double rule under the heading, as in the Journal
		g.fill(l + LX - 1, t + HEAD_Y + 10, l + LR + 1, t + HEAD_Y + 11, 0xC0AA2818);
		g.fill(l + LX - 1, t + HEAD_Y + 12, l + LR + 1, t + HEAD_Y + 13, 0x90BE8C3C);
		List<Row> rows = rows();
		if (hover.length != rows.size()) hover = new float[rows.size()];
		scroll = Math.max(0, Math.min(maxScroll(), scroll));
		scrollShown = Ui.approach(scrollShown, scroll, 18, dt);
		if (offers.isEmpty()) {
			Ui.block(g, font, List.of(new Ui.Para(Component.translatable("stall.matriochka.empty"), Ui.INK_SOFT, 0)), l + LX, t + ROW_Y + 4, LR - LX, 60);
			return;
		}
		int top = t + ROW_Y, bottom = t + ROW_Y + ROWS * ROW_H;
		g.enableScissor(l + 10, top, l + 137, bottom);
		int first = Math.max(0, (int) Math.floor(scrollShown));
		for (int i = first; i < rows.size() && i < first + ROWS + 1; i++) {
			Row r = rows.get(i);
			int y = top + Math.round((i - scrollShown) * ROW_H);
			float in = Ui.easeOut(Ui.since(opened + 60L + Math.max(0, i - scroll) * 40L, 240));
			int dx = Math.round((1 - in) * -10);
			boolean over = !motion.closing() && !r.header() && mx >= l + LX - 3 && mx < l + LR + 2 && my >= Math.max(y, top) && my < Math.min(y + ROW_H, bottom);
			hover[i] = Ui.approach(hover[i], over ? 1 : 0, 16, dt);
			if (r.header()) underTheCounter(g, l + dx, y, in);
			else row(g, l + dx, y, r.offer(), hover[i], in);
		}
		g.disableScissor();
		// a soft fade where the lines leave the page
		g.fillGradient(l + 16, top, l + 132, top + 3, 0x40301808, 0x00301808);
		g.fillGradient(l + 16, bottom - 3, l + 132, bottom, 0x00301808, 0x40301808);
		if (rows.size() > ROWS) {
			int track = ROWS * ROW_H - 2, th = Math.max(14, track * ROWS / rows.size());
			int ty = top + 1 + Math.round((track - th) * scrollShown / Math.max(1, maxScroll()));
			g.fill(l + THUMB_X + 1, top + 1, l + THUMB_X + 3, top + track + 1, 0x30301808);
			Ui.sprite(g, "thumb", l + THUMB_X, ty, 4, th);
		}
	}

	/** The heading of the black market's goods: plum ink between two dotted rules, a wax seal at each end. */
	private void underTheCounter(GuiGraphicsExtractor g, int l, int y, float in) {
		g.fill(l + LX - 3, y + 1, l + LR + 2, y + ROW_H - 1, Ui.alpha(0x30401048, in));
		Component c = Component.translatable("stall.matriochka.under_counter");
		int cx = l + (LX + LR) / 2, tw = Math.min(font.width(c), LR - LX - 24);
		Ui.fitted(g, font, c, cx, y + 6, LR - LX - 24, Ui.alpha(PLUM, in), false);
		for (int x = l + LX + 8; x < cx - tw / 2 - 3; x += 3) g.fill(x, y + 10, x + 1, y + 11, Ui.alpha(PLUM, 0.7f * in));
		for (int x = cx + tw / 2 + 3; x < l + LR - 8; x += 3) g.fill(x, y + 10, x + 1, y + 11, Ui.alpha(PLUM, 0.7f * in));
		seal(g, l + LX + 1, y + 7, in);
		seal(g, l + LR - 6, y + 7, in);
	}

	/** A little wax seal in plum lacquer with a gold dot. */
	private static void seal(GuiGraphicsExtractor g, int x, int y, float a) {
		g.fill(x, y + 1, x + 6, y + 5, Ui.alpha(0xFF4A1856, a));
		g.fill(x + 1, y, x + 5, y + 6, Ui.alpha(0xFF4A1856, a));
		g.fill(x + 1, y + 1, x + 3, y + 2, Ui.alpha(0xFF9A5AAA, a));
		g.fill(x + 2, y + 2, x + 4, y + 4, Ui.alpha(Ui.GOLD, a));
	}

	/** One offer of the ledger: what it costs, an inked arrow, what it gives, the stock and the karma's tag. */
	private void row(GuiGraphicsExtractor g, int l, int y, int idx, float over, float in) {
		MerchantOffer o = offers().get(idx);
		boolean sel = idx == shopItem && pickedAt >= 0, out = o.isOutOfStock(), black = contraband(idx), can = affordable(o);
		int x0 = l + LX;
		if (black) {
			g.fill(x0 - 3, y + 1, l + LR + 2, y + ROW_H - 1, Ui.alpha(0x2A401048, in));
			g.fill(x0 - 3, y + 1, x0 - 2, y + ROW_H - 1, Ui.alpha(PLUM, in));
		}
		if (over > 0.01f) {
			g.fill(x0 - 3, y + 1, l + LR + 2, y + ROW_H - 1, Ui.alpha(black ? 0x30501060 : 0x1E8A2018, over));
			g.fill(x0 - 3, y + 1, x0 - 2, y + ROW_H - 1, Ui.alpha(0xFFB0782A, over));
		}
		if (sel) {
			g.fill(x0 - 3, y + 1, l + LR + 2, y + ROW_H - 1, Ui.alpha(0x2CC89A3A, in));
			g.outline(x0 - 3, y + 1, LR - LX + 5, ROW_H - 2, Ui.alpha(0xFFB0782A, in));
			float p = pickedAt < 0 ? 1 : Ui.since(pickedAt, 700);
			if (p < 1) Ui.glint(g, x0 - 3, y + 1, p, 9);
		}
		// the line ruled under each entry
		for (int x = x0 - 2; x < l + LR + 1; x += 2) g.fill(x, y + ROW_H - 1, x + 1, y + ROW_H, 0x3C6E4E36);
		int iy = y + 2;
		ItemStack a = o.getCostA(), b = o.getCostB(), res = o.getResult();
		int diff = priceDiff(o);
		g.fakeItem(a, x0, iy);
		String countA = (diff < 0 ? ChatFormatting.GREEN : diff > 0 ? ChatFormatting.RED : ChatFormatting.WHITE) + Integer.toString(a.getCount());
		g.itemDecorations(font, a, x0, iy, a.getCount() == 1 && diff == 0 ? null : countA);
		if (!can && carried(a) < a.getCount()) shortMark(g, x0, iy);
		if (!b.isEmpty()) {
			g.fakeItem(b, x0 + 19, iy);
			g.itemDecorations(font, b, x0 + 19, iy);
			if (!can && carried(b) < b.getCount()) shortMark(g, x0 + 19, iy);
		}
		arrow(g, x0 + 39, y + 7, out ? 0xFF9A2418 : black ? PLUM : Ui.INK_SOFT);
		g.fakeItem(res, x0 + 49, iy);
		g.itemDecorations(font, res, x0 + 49, iy);
		// the stock, and below it the karma's change to the price
		int right = l + LR - 2;
		if (!out) {
			Component stock = Component.literal((o.getMaxUses() - o.getUses()) + "/" + o.getMaxUses());
			g.text(font, stock, right - font.width(stock), y + 2, black ? PLUM : Ui.INK, false);
		}
		if (diff != 0) {
			Component tag = Component.literal((diff < 0 ? "-" : "+") + Math.abs(diff));
			int tx = right - font.width(tag) - 2;
			// a little price tag: pale wash, inked edge, the change in the karma's colour
			g.fill(tx - 2, y + 10, right + 1, y + 19, diff < 0 ? 0x38A8D878 : 0x38E8806A);
			g.outline(tx - 2, y + 10, right + 3 - tx, 9, diff < 0 ? 0x903F6E2C : 0x909A2418);
			g.text(font, tag, tx, y + 11, diff < 0 ? Ui.GREEN : Ui.RED_INK, false);
		}
		if (out) {
			g.fill(x0 - 2, y + 1, l + LR + 1, y + ROW_H - 1, 0x90E8D8B4);
			stamp(g, (x0 + l + LR) / 2 + 8, y + ROW_H / 2, Component.translatable("stall.matriochka.sold_out"));
		}
	}

	/** Red ink under a price the player cannot pay yet. */
	private static void shortMark(GuiGraphicsExtractor g, int x, int y) {
		g.fill(x, y, x + 16, y + 16, 0x50E8D8B4);
		g.fill(x + 1, y + 16, x + 15, y + 17, 0xFFC8402A);
	}

	/** An inked arrow: a shaft and a barbed head. */
	private static void arrow(GuiGraphicsExtractor g, int x, int y, int col) {
		g.fill(x, y + 2, x + 6, y + 3, col);
		g.fill(x + 4, y, x + 5, y + 5, col);
		g.fill(x + 5, y + 1, x + 6, y + 4, col);
		g.fill(x + 6, y + 2, x + 7, y + 3, col);
	}

	/** "Sold out", stamped across a line in red ink, a little askew. */
	private void stamp(GuiGraphicsExtractor g, int cx, int cy, Component text) {
		int tw = font.width(text);
		float sc = Math.min(1f, 76f / (tw + 8));
		g.pose().pushMatrix();
		g.pose().translate(cx, cy);
		g.pose().rotate(-0.12f);
		g.pose().scale(sc, sc);
		int w = tw + 8, h = 12;
		g.fill(-w / 2, -h / 2, w / 2, h / 2, 0x30C8402A);
		g.outline(-w / 2, -h / 2, w, h, 0xE09A2418);
		g.outline(-w / 2 + 1, -h / 2 + 1, w - 2, h - 2, 0x709A2418);
		g.text(font, text, -tw / 2, -4, 0xFF9A2418, false);
		g.pose().popMatrix();
	}

	/** The plaque: the world's medallion, the world, the kind of trader and the karma the prices answer to. */
	private void plaque(GuiGraphicsExtractor g, int l, int t) {
		int w = Math.max(0, Math.min(10, info.world()));
		boolean black = info.contraband() > 0;
		float pulse = 0.35f + 0.15f * (float) Math.sin(Ui.now() / 600.0);
		Ui.sprite(g, "glow", l + 142, t + 26, 28, 28, black ? Ui.alpha(0xFFB070D0, pulse) : Ui.white(pulse * 0.8f));
		Ui.sprite(g, "rule_" + EMBLEMS[w], l + 145, t + 29, 22, 22);
		Component world = w == 0 ? Component.translatable("journal.matriochka.surface") : Component.translatable("stall.matriochka.world", w, Component.translatable("world.matriochka." + w));
		int tx = l + 172, tw = 132;
		fittedLeft(g, world, tx, t + 29, tw, Ui.GOLD);
		fittedLeft(g, kindLine(), tx, t + 40, tw, black ? PLUM_LIGHT : Ui.MUTED);
		fittedLeft(g, karmaLine(), tx, t + 50, tw, info.karma() >= 25 ? Ui.OK : info.karma() <= -25 ? Ui.WARN : Ui.LIGHT);
	}

	private Component kindLine() {
		if (info.contraband() > 0) return Component.translatable("stall.matriochka.kind.black_market", info.contraband());
		return switch (info.kind()) {
			case "travelling" -> {
				int left = info.ticksLeft() < 0 ? -1 : Math.max(0, info.ticksLeft() / 20 - (int) ((Ui.now() - opened) / 1000));
				yield left < 0 ? Component.translatable("stall.matriochka.kind.travelling")
					: Component.translatable("stall.matriochka.kind.travelling_left", String.format("%d:%02d", left / 60, left % 60));
			}
			case "peddler" -> Component.translatable("stall.matriochka.kind.peddler");
			default -> Component.translatable("stall.matriochka.kind.people");
		};
	}

	private Component karmaLine() {
		int k = info.karma();
		String tier = k >= 25 ? "kind" : k <= -25 ? "dear" : "fair";
		return Component.translatable("stall.matriochka.karma." + tier, (k > 0 ? "+" : "") + k);
	}

	/** One line from x, shrunk (never below 60%) when wider than maxW. */
	private void fittedLeft(GuiGraphicsExtractor g, Component c, int x, int y, int maxW, int color) {
		int tw = font.width(c);
		float sc = tw > maxW ? Math.max(0.6f, maxW / (float) tw) : 1f;
		g.pose().pushMatrix();
		g.pose().translate(x, y + 4);
		g.pose().scale(sc, sc);
		Ui.embossed(g, font, c, 0, -4, color);
		g.pose().popMatrix();
	}

	/** The counter: the selected trade's price waiting faintly in empty slots, its state under the plank. */
	private void counter(GuiGraphicsExtractor g, int l, int t, float dt) {
		MerchantOffers offers = offers();
		if (offers.isEmpty() || shopItem >= offers.size()) return;
		MerchantOffer o = offers.get(shopItem);
		ItemStack[] want = {o.getCostA(), o.getCostB()};
		for (int i = 0; i < 2; i++) {
			Slot s = menu.getSlot(i);
			if (s.hasItem() || want[i].isEmpty()) continue;
			int sx = leftPos + s.x, sy = topPos + s.y;
			g.fakeItem(want[i], sx, sy);
			g.fill(sx, sy, sx + 16, sy + 16, 0xA8201208);
		}
		Slot result = menu.getSlot(2);
		if (!result.hasItem() && !o.isOutOfStock()) {
			int sx = leftPos + result.x, sy = topPos + result.y;
			g.fakeItem(o.getResult(), sx, sy);
			g.fill(sx, sy, sx + 16, sy + 16, 0xA8201208);
		}
		if (result.hasItem()) {
			float p = 0.3f + 0.2f * (float) Math.sin(Ui.now() / 380.0);
			Ui.sprite(g, "glow", leftPos + result.x - 6, topPos + result.y - 6, 28, 28, Ui.white(p));
		}
		int cx = l + 224, y = t + 99;
		Component line;
		int col;
		if (o.isOutOfStock()) {
			line = Component.translatable("stall.matriochka.sold_out.long");
			col = Ui.WARN;
			// the painted arrow is crossed out
			int ax = l + 228, ay = t + 79;
			for (int k = -4; k <= 4; k++) {
				g.fill(ax + k, ay + k, ax + k + 2, ay + k + 1, 0xFFC8402A);
				g.fill(ax + k, ay - k, ax + k + 2, ay - k + 1, 0xFFC8402A);
			}
		} else {
			line = Component.translatable("stall.matriochka.stock", o.getMaxUses() - o.getUses(), o.getMaxUses());
			col = contraband(shopItem) ? PLUM_LIGHT : Ui.LIGHT;
		}
		Ui.fitted(g, font, line, cx, y, 158, col, true);
	}

	/** Item tooltips over the ledger's icons, and a summary of the line elsewhere on it. */
	private void tooltips(GuiGraphicsExtractor g, int mx, int my) {
		if (!menu.getCarried().isEmpty()) return;
		int l = px, t = py, top = t + ROW_Y;
		if (mx < l + LX - 3 || mx >= l + LR + 2 || my < top || my >= top + ROWS * ROW_H) return;
		int i = scroll + (my - top) / ROW_H;
		List<Row> rows = rows();
		if (i >= rows.size() || rows.get(i).header()) return;
		int idx = rows.get(i).offer();
		MerchantOffer o = offers().get(idx);
		int x0 = l + LX, ry = top + (i - scroll) * ROW_H + 2;
		boolean onIcon = my >= ry && my < ry + 16;
		if (onIcon && mx >= x0 && mx < x0 + 16) {
			g.setTooltipForNextFrame(font, o.getCostA(), mx, my);
			return;
		}
		if (onIcon && !o.getCostB().isEmpty() && mx >= x0 + 19 && mx < x0 + 35) {
			g.setTooltipForNextFrame(font, o.getCostB(), mx, my);
			return;
		}
		if (onIcon && mx >= x0 + 49 && mx < x0 + 65) {
			g.setTooltipForNextFrame(font, o.getResult(), mx, my);
			return;
		}
		List<Component> tip = new ArrayList<>();
		tip.add(Component.translatable("stall.matriochka.tip.gives", o.getResult().getCount(), o.getResult().getHoverName()).withStyle(ChatFormatting.GOLD));
		Component price = Component.translatable("stall.matriochka.tip.price", o.getCostA().getCount(), o.getCostA().getHoverName());
		if (!o.getCostB().isEmpty()) price = Component.translatable("stall.matriochka.tip.price2", price, o.getCostB().getCount(), o.getCostB().getHoverName());
		tip.add(price.copy().withStyle(ChatFormatting.WHITE));
		int diff = priceDiff(o);
		if (diff != 0) tip.add(Component.translatable(diff < 0 ? "stall.matriochka.tip.discount" : "stall.matriochka.tip.markup", o.getBaseCostA().getCount()).withStyle(diff < 0 ? ChatFormatting.GREEN : ChatFormatting.RED));
		tip.add((o.isOutOfStock() ? Component.translatable("stall.matriochka.sold_out.long") : Component.translatable("stall.matriochka.stock", o.getMaxUses() - o.getUses(), o.getMaxUses()))
			.withStyle(o.isOutOfStock() ? ChatFormatting.RED : ChatFormatting.GRAY));
		if (!affordable(o)) tip.add(Component.translatable("stall.matriochka.tip.short", carried(o.getCostA()), o.getCostA().getCount()).withStyle(ChatFormatting.RED));
		if (contraband(idx)) tip.add(Component.translatable("stall.matriochka.tip.contraband").withStyle(ChatFormatting.DARK_PURPLE));
		g.setComponentTooltipForNextFrame(font, tip, mx, my);
	}

	// ---------------------------------------------------------------- input
	private int rowAt(double mx, double my) {
		int l = px, top = py + ROW_Y;
		if (mx < l + LX - 3 || mx >= l + LR + 2 || my < top || my >= top + ROWS * ROW_H) return -1;
		int i = scroll + (int) ((my - top) / ROW_H);
		List<Row> rows = rows();
		if (i >= rows.size() || rows.get(i).header()) return -1;
		return rows.get(i).offer();
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		double mx = event.x(), my = event.y();
		int top = py + ROW_Y;
		if (maxScroll() > 0 && mx >= px + THUMB_X - 1 && mx < px + THUMB_X + 5 && my >= top && my < top + ROWS * ROW_H) {
			dragging = true;
			dragTo(my);
			return true;
		}
		int idx = rowAt(mx, my);
		if (idx >= 0 && menu.getCarried().isEmpty() && event.button() == com.mojang.blaze3d.platform.InputConstants.MOUSE_BUTTON_LEFT) {
			Ui.sound(SoundEvents.BOOK_PAGE_TURN, 1.5f, 0.45f);
			Ui.sound(SoundEvents.WOODEN_BUTTON_CLICK_ON, 1.2f, 0.4f);
			select(idx);
			return true;
		}
		return super.mouseClicked(event, doubleClick);
	}

	private void dragTo(double my) {
		int top = py + ROW_Y, track = ROWS * ROW_H;
		float f = (float) ((my - top) / track);
		scroll = Math.max(0, Math.min(maxScroll(), Math.round(f * maxScroll())));
	}

	@Override
	public boolean mouseDragged(MouseButtonEvent event, double dx, double dy) {
		if (dragging) {
			dragTo(event.y());
			return true;
		}
		return super.mouseDragged(event, dx, dy);
	}

	@Override
	public boolean mouseReleased(MouseButtonEvent event) {
		dragging = false;
		return super.mouseReleased(event);
	}

	@Override
	public boolean mouseScrolled(double x, double y, double sx, double sy) {
		if (x >= px && x < px + 140 && y >= py && y < py + MH) {
			scroll = Math.max(0, Math.min(maxScroll(), scroll - (int) Math.signum(sy)));
			return true;
		}
		return super.mouseScrolled(x, y, sx, sy);
	}

	@Override
	public boolean keyPressed(KeyEvent event) {
		if (motion.closing()) return true;
		return super.keyPressed(event);
	}
}
