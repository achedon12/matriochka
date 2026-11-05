package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.net.Net;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;

/**
 * The Artisan's Scroll is a parchment roll on two turned rods that unrolls when it opens; the Journal is an open
 * book in a red lacquer cover with satin ribbon bookmarks. Left page: the chapter's painted nesting dolls. Right
 * page: its content. Switching tab pulls the ribbon down and turns the page.
 */
public class JournalScreen extends Screen {
	private static final int BW = 340, BH = 214, PW = 155;
	private static final int TURN_MS = 420, UNROLL_MS = 560, ROLLUP_MS = 220;
	private static final String[] TABS = {"objective", "quests", "karma", "worlds", "scroll", "pages"};
	private static final int PAGES_TAB = 5;
	private static final int[] NEST_W = {42, 34, 28, 22, 16}, NEST_H = {64, 52, 42, 33, 25};
	private final boolean scroll;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(320, 170);
	private final float[] hang = new float[TABS.length];
	private int tab, page, questWorld;
	// the Pages tab: the selected Journal page (world 1..10, index 0..4)
	private int pageWorld = 1, pageIndex = 0;
	private boolean cycleConfirm;
	// page turn: the previous left page stays visible until the turning sheet covers it
	private long turnAt = -1, pageAt = -1;
	private int turnDir = 1, prevTab, prevPage;
	private long last = Ui.now();

	public JournalScreen(boolean scroll) {
		super(Component.translatable(scroll ? "item.matriochka.artisan_scroll" : "item.matriochka.artisan_journal"));
		this.scroll = scroll;
		for (int i = 0; i < hang.length; i++) hang[i] = 6;
		int[] first = JournalPages.first();
		if (first != null) {
			pageWorld = first[0];
			pageIndex = first[1];
		}
	}

	/** Left edge of a ribbon bookmark above the cover. */
	private int ribbonX(int i) {
		return left() + 7 + i * 55;
	}

	/** Opens the journal on a given tab (used by the showcase). */
	public JournalScreen tab(int t) {
		this.tab = t;
		this.prevTab = t;
		return this;
	}

	private int left() { return (width - BW) / 2; }
	private int top() { return Math.max(0, Math.min((height - BH) / 2 + 12, height - BH - 1)); }

	@Override
	protected void init() {
		if (!motion.closing() && Ui.now() - motion.openedAt() < 100) {
			if (scroll) Ui.sound(SoundEvents.BOOK_PAGE_TURN, 0.7f, 1f);
			else Ui.pageTurn();
		}
		rebuild();
	}

	private void rebuild() {
		buttons.clear();
		int l = left(), t = top();
		boolean pages = scroll || tab == 4;
		if (pages) {
			buttons.add(l + BW / 2 - 70, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.previous"), () -> turnPage(-1), () -> page > 0);
			buttons.add(l + BW / 2 + 30, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.next"), () -> turnPage(1), () -> page < 4);
		}
		if (!scroll) {
			// the comfort options, at the foot of the left page on every tab
			buttons.add(l + 24, t + BH - 30, 64, 16, Component.translatable("comfort.matriochka.open"),
				() -> minecraft.gui.setScreen(new ComfortScreen(this)));
		}
		if (!scroll && tab == PAGES_TAB) {
			buttons.add(l + BW / 2 + 18, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.previous"), () -> stepPage(-1),
				() -> JournalPages.step(pageWorld, pageIndex, -1) != null);
			buttons.add(l + BW - 62, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.next"), () -> stepPage(1),
				() -> JournalPages.step(pageWorld, pageIndex, 1) != null);
		}
		if (!scroll && tab == 0 && JournalPages.endingsSeen() > 0) {
			Component label = Component.translatable(cycleConfirm ? "journal.matriochka.new_cycle.confirm" : "journal.matriochka.new_cycle");
			buttons.add(l + BW - 98, t + BH - 30, 76, 16, label, () -> {
				if (!cycleConfirm) {
					cycleConfirm = true;
					rebuild();
					return;
				}
				ClientPlayNetworking.send(new Net.CyclePayload(true));
				onClose();
			});
		}
		if (!scroll && tab == 1) {
			buttons.add(l + BW / 2 + 18, t + BH - 30, 18, 16, Component.literal("<"), () -> { questWorld = Math.max(0, questWorld - 1); pageAt = Ui.now(); turnDir = -1; rebuild(); }, () -> questWorld > 0);
			buttons.add(l + BW - 40, t + BH - 30, 18, 16, Component.literal(">"), () -> { questWorld = Math.min(KARMA_CHAPTER, questWorld + 1); pageAt = Ui.now(); turnDir = 1; rebuild(); }, () -> questWorld < KARMA_CHAPTER);
			int y = t + 30;
			for (Defs.QuestDef q : Content.QUESTS) {
				if (q.world() != questWorld) continue;
				if (q.objKind().equals("choice") && !done(q) && open(q)) {
					buttons.add(l + BW - 98, y + 18, 36, 14, Component.translatable("journal.matriochka.help"), () -> send(q.id(), 1));
					buttons.add(l + BW - 60, y + 18, 36, 14, Component.translatable("journal.matriochka.betray"), () -> send(q.id(), -1));
				}
				y += 26;
			}
		}
	}

	private void turnPage(int dir) {
		int next = Math.max(0, Math.min(4, page + dir));
		if (next == page) return;
		prevTab = tab;
		prevPage = page;
		page = next;
		turnDir = dir;
		if (scroll) pageAt = Ui.now();
		else turnAt = Ui.now();
		Ui.pageTurn();
	}

	/** Moves to the previous or next page found, sliding the right page in. */
	private void stepPage(int dir) {
		int[] next = JournalPages.step(pageWorld, pageIndex, dir);
		if (next == null) return;
		selectPage(next[0], next[1], dir);
	}

	private void selectPage(int world, int index, int dir) {
		if (world == pageWorld && index == pageIndex) return;
		pageWorld = world;
		pageIndex = index;
		pageAt = Ui.now();
		turnDir = dir;
		Ui.pageTurn();
	}

	/** Turns to a tab as a click on its ribbon would (used by the showcase). */
	public void turnTo(int i) {
		switchTab(i);
	}

	private void switchTab(int i) {
		if (i == tab) return;
		prevTab = tab;
		prevPage = page;
		turnDir = i > tab ? 1 : -1;
		tab = i;
		page = 0;
		cycleConfirm = false;
		turnAt = Ui.now();
		Ui.pageTurn();
		rebuild();
	}

	private static boolean done(Defs.QuestDef q) {
		return MatrioClient.state.getBooleanOr("f_quest_" + q.id(), false);
	}

	private void send(String quest, int choice) {
		ClientPlayNetworking.send(new Net.ChoicePayload(quest, choice));
		onClose();
	}

	/** The karma-path chapter comes after the ten worlds. */
	private static final int KARMA_CHAPTER = 11;

	/** A quest is open once its world is; a karma-path quest once the karma reaches its path. */
	private static boolean open(Defs.QuestDef q) {
		if (q.world() == KARMA_CHAPTER) {
			int k = MatrioClient.state.getIntOr("karma", 0);
			return q.type().equals("help") ? k >= 50 : q.type().equals("pact") ? k <= -50 : true;
		}
		return unlocked(q.world());
	}

	private static Component lockedText(Defs.QuestDef q) {
		if (q.world() == KARMA_CHAPTER) return Component.translatable("journal.matriochka.locked_" + q.type());
		return Component.translatable("journal.matriochka.locked");
	}

	private static boolean unlocked(int world) {
		return world == 0 || (MatrioClient.state.getIntOr("done", 0) & (1 << (world - 1))) != 0;
	}

	private static int highest() {
		int done = MatrioClient.state.getIntOr("done", 0), best = -1;
		for (int i = 0; i <= 10; i++) if ((done & (1 << i)) != 0) best = i;
		return best;
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(scroll ? SoundEvents.BOOK_PAGE_TURN : SoundEvents.BOOK_PUT, scroll ? 0.6f : 1.1f, 0.8f);
		motion.close(super::onClose);
	}

	@Override
	public void tick() {
		super.tick();
		motion.tick();
	}

	/** 0..1, how far the scroll is unrolled. */
	private float unroll() {
		float v = Ui.easeOut(Ui.since(motion.openedAt() + 60, UNROLL_MS));
		if (motion.closing()) v *= 1 - Ui.easeIn(Ui.since(motion.closedAt(), ROLLUP_MS));
		return v;
	}

	private int rodY() {
		int t = top();
		return Math.round(t + 4 + (BH - 15) * unroll());
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top();
		if (scroll) {
			int by = rodY();
			g.enableScissor(l, t + 4, l + BW, by + 7);
			Ui.sprite(g, "scroll_paper", l + 30, t + 8, 280, 198);
			g.disableScissor();
			// the shadow the lower rod casts on the paper it is still rolling out
			g.fillGradient(l + 30, by - 6, l + 310, by + 4, 0x00000000, 0x55301808);
			Ui.sprite(g, "scroll_rod", l + 12, t - 3, 316, 14);
			Ui.sprite(g, "scroll_rod", l + 12, by, 316, 14);
			Ui.wanderingGlint(g, new int[][]{{l + 18, t + 4}, {l + 322, t + 4}, {l + 18, by + 7}, {l + 322, by + 7}}, 1900, 3);
			return;
		}
		motion.push(g, l + BW / 2f, t + BH / 2f);
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		// ribbons peek above the cover; the active one is pulled lower and glows, hovered ones lift a little
		for (int i = 0; i < TABS.length; i++) {
			int rx = ribbonX(i);
			boolean on = tab == i;
			boolean over = !on && mx >= rx && mx < rx + 54 && my >= t - 18 && my < t;
			hang[i] = Ui.approach(hang[i], on ? 23 : over ? 18 : 15, on ? 9 : 14, dt);
			int top = t - Math.round(hang[i]);
			Ui.sprite(g, on ? "ribbon_" + i + "_on" : "ribbon_" + i, rx, top, 54, 48);
			Component label = Component.translatable("journal.matriochka.tab." + TABS[i]);
			int col = i == 2 ? 0xFF2A1408 : on ? 0xFFFFF4D8 : Ui.LIGHT;
			int lx = rx + 27 - font.width(label) / 2;
			if (i == 2) g.text(font, label, lx, top + 5, col, false);
			else Ui.embossed(g, font, label, lx, top + 5, col);
		}
		Ui.sprite(g, "book", l, t, BW, BH);
		Ui.wanderingGlint(g, new int[][]{{l + 4, t + 4}, {l + BW - 4, t + 4}, {l + 4, t + BH - 4}, {l + BW - 4, t + BH - 4}, {l + BW / 2, t + 6}, {l + BW / 2, t + BH - 6}}, 1700, 11);
		motion.pop(g);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		int l = left(), t = top();
		int lx = l + 20, rx = l + 28 + PW, cw = PW - 18;
		if (scroll) {
			int by = rodY();
			g.enableScissor(l, t + 8, l + BW, by + 3);
			float p = pageAt < 0 ? 1 : Ui.easeOut(Ui.since(pageAt, 300));
			int off = Math.round((1 - p) * 18 * turnDir);
			drawScrollPage(g, l + 46 + off, t + 24, BW - 92, p);
			buttons.draw(g, font, mx, my);
			g.disableScissor();
			return;
		}
		motion.push(g, l + BW / 2f, t + BH / 2f);
		float turn = turnAt < 0 ? 1 : Ui.since(turnAt, TURN_MS);
		// left page: the chapter's illustration. Turning forward, the old one stays until the sheet lands on it;
		// turning back, the lifted sheet uncovers the new one.
		boolean old = turn < 1 && turnDir > 0;
		leftPage(g, lx, t, cw, old ? prevTab : tab, old ? prevPage : page);
		// right page: the content, sliding in a little after a world change in the quest list
		float slide = pageAt < 0 ? 1 : Ui.easeOut(Ui.since(pageAt, 260));
		g.pose().pushMatrix();
		g.pose().translate((1 - slide) * 10 * turnDir, 0);
		switch (tab) {
			case 0 -> objective(g, rx, t + 24, cw);
			case 1 -> quests(g, rx, t + 24, cw, mx, my);
			case 2 -> karma(g, rx, t + 24, cw);
			case 3 -> worlds(g, rx, t + 24, cw, mx, my);
			case PAGES_TAB -> journalPage(g, rx, t + 24, cw);
			default -> drawScrollPage(g, rx, t + 24, cw, 1);
		}
		if (tab == PAGES_TAB && turn >= 1) pageIndexHover(g, lx, t, cw, mx, my);
		g.pose().popMatrix();
		buttons.draw(g, font, mx, my);
		if (turn < 1) drawTurningSheet(g, l, t, turn);
		motion.pop(g);
	}

	/** The sheet in mid-turn: it lifts off one page, narrows to the spine, then falls open on the other. */
	private void drawTurningSheet(GuiGraphicsExtractor g, int l, int t, float turn) {
		int spineL = l + 166, spineR = l + 174, y0 = t + 11, h = 192;
		boolean firstHalf = turn < 0.5f;
		float q = firstHalf ? Ui.easeIn(turn * 2) : Ui.easeOut((turn - 0.5f) * 2);
		boolean rightSide = (turnDir > 0) == firstHalf;
		int w = Math.max(1, Math.round(PW * (firstHalf ? 1 - q : q)));
		int x = rightSide ? spineR : spineL - w;
		// the shadow the lifted sheet casts beside its free edge
		int shadowW = Math.round(14 * (firstHalf ? q : 1 - q)) + 2;
		int sx = rightSide ? x + w : x - shadowW;
		for (int i = 0; i < shadowW; i++) {
			float f = rightSide ? 1 - i / (float) shadowW : i / (float) shadowW;
			g.fill(sx + i, y0, sx + i + 1, y0 + h, Ui.alpha(0xFF2A1408, 0.32f * f));
		}
		// a sheet landing on the right page is blank: it fades into the page it becomes
		float fade = rightSide && !firstHalf && turn > 0.8f ? 1 - (turn - 0.8f) / 0.2f : 1;
		Ui.sprite(g, "page_sheet", x, y0, w, h, Ui.white(fade));
		// a sheet lying over the left page carries a left page: the new one as it lands, the old one as it lifts
		if (!rightSide) {
			g.enableScissor(x, y0, x + w, y0 + h);
			if (firstHalf) leftPage(g, l + 20, t, PW - 18, prevTab, prevPage);
			else leftPage(g, l + 20, t, PW - 18, tab, page);
			g.disableScissor();
		}
	}

	private void leftPage(GuiGraphicsExtractor g, int lx, int t, int cw, int forTab, int forPage) {
		Component chapter = Component.translatable("journal.matriochka.tab." + TABS[forTab]);
		g.text(font, chapter, lx + cw / 2 - font.width(chapter) / 2, t + 22, Ui.RED_INK, false);
		Ui.sprite(g, "divider", lx + cw / 2 - 60, t + 31, 120, 10);
		if (forTab == PAGES_TAB) {
			pageIndex(g, lx, t, cw);
			return;
		}
		drawDolls(g, lx + cw / 2, t + 176, forTab == 4 ? forPage : Math.max(0, Math.min(4, highest() + 1)), cw - 4);
	}

	// ---------------------------------------------------------------- the Pages tab
	private static final int INDEX_Y = 42, INDEX_ROW = 13, PIP_X = 82, PIP_STEP = 10;

	/** Left page of the Pages tab: one row per world, five pips for its five pages (gilded when read, red when found). */
	private void pageIndex(GuiGraphicsExtractor g, int lx, int t, int cw) {
		for (int w = 1; w <= 10; w++) {
			int ry = t + INDEX_Y + (w - 1) * INDEX_ROW;
			int found = JournalPages.found(w);
			Component name = Component.translatable("hud.matriochka.world", w);
			g.text(font, name, lx + 2, ry, found == 0 ? 0xFF9A8A6E : Ui.INK, false);
			g.fill(lx + PIP_X - 6, ry + 2, lx + PIP_X - 3, ry + 5, found > 0 ? Ui.worldColor(w) : 0x60605048);
			for (int i = 0; i < 5; i++) {
				int px = lx + PIP_X + i * PIP_STEP;
				boolean have = (found & (1 << i)) != 0;
				boolean sel = w == pageWorld && i == pageIndex;
				if (sel) {
					g.fill(px - 2, ry - 2, px + 9, ry + 9, 0x2E8A2018);
					g.fill(px - 2, ry + 9, px + 9, ry + 10, 0xFFB0782A);
				}
				String pip = !have ? "pip_locked" : JournalPages.readable(w, i) ? "pip_done" : "pip_open";
				Ui.sprite(g, pip, px, ry, 7, 7);
			}
		}
		Component total = Component.translatable("journal.matriochka.pages", JournalPages.total());
		g.text(font, total, lx + cw / 2 - font.width(total) / 2, t + INDEX_Y + 10 * INDEX_ROW + 6, Ui.INK_SOFT, false);
	}

	/** Hover outline and tooltip over the index pips. */
	private void pageIndexHover(GuiGraphicsExtractor g, int lx, int t, int cw, int mx, int my) {
		int[] at = pipAt(lx, t, mx, my);
		if (at == null) return;
		int px = lx + PIP_X + at[1] * PIP_STEP, ry = t + INDEX_Y + (at[0] - 1) * INDEX_ROW;
		g.fill(px - 1, ry - 1, px + 8, ry, 0xFFB0782A);
		boolean have = (JournalPages.found(at[0]) & (1 << at[1])) != 0;
		Component tip = have ? Component.translatable("journal.matriochka.page." + at[0] + "." + at[1] + ".title")
			: Component.translatable("journal.matriochka.pages.label", at[0], at[1] + 1);
		g.setTooltipForNextFrame(font, font.split(tip, 160), mx, my);
	}

	/** The (world, index) of the pip under the mouse, or null. */
	private int[] pipAt(int lx, int t, double mx, double my) {
		for (int w = 1; w <= 10; w++) {
			int ry = t + INDEX_Y + (w - 1) * INDEX_ROW;
			if (my < ry - 2 || my >= ry + 10) continue;
			for (int i = 0; i < 5; i++) {
				int px = lx + PIP_X + i * PIP_STEP;
				if (mx >= px - 2 && mx < px + 9) return new int[]{w, i};
			}
		}
		return null;
	}

	/** Right page of the Pages tab: the selected page, enciphered while it cannot be read yet. */
	private void journalPage(GuiGraphicsExtractor g, int x, int y, int w) {
		if (JournalPages.total() == 0) {
			g.textWithWordWrap(font, Component.translatable("journal.matriochka.pages.none"), x, y + 4, w, Ui.INK_SOFT, false);
			return;
		}
		Component label = Component.translatable("journal.matriochka.pages.label", pageWorld, pageIndex + 1);
		g.text(font, label, x, y, Ui.INK_SOFT, false);
		g.fill(x + w - 4, y + 2, x + w, y + 6, Ui.worldColor(pageWorld));
		boolean have = (JournalPages.found(pageWorld) & (1 << pageIndex)) != 0;
		if (!have) {
			g.textWithWordWrap(font, Component.translatable("journal.matriochka.pages.missing", pageWorld), x, y + 16, w, 0xFF9A8A6E, false);
			return;
		}
		String base = "journal.matriochka.page." + pageWorld + "." + pageIndex;
		int yy = y + 13 + g.textWithWordWrap(font, Component.translatable(base + ".title"), x, y + 13, w, Ui.RED_INK, false);
		g.fill(x, yy + 1, x + Math.min(w, 60), yy + 2, 0xFFB0782A);
		yy += 7;
		boolean coded = JournalPages.coded(pageIndex);
		boolean readable = JournalPages.readable(pageWorld, pageIndex);
		Component body = Component.translatable(base);
		if (coded && !readable) body = Component.literal(JournalPages.cipher(body.getString(), pageWorld));
		int bodyH = g.textWithWordWrap(font, body, x, yy, w, readable ? Ui.INK : 0xFF5A3A5A, false);
		if (coded) {
			Component note = Component.translatable(readable ? "journal.matriochka.pages.decoded" : "journal.matriochka.pages.coded");
			g.textWithWordWrap(font, note, x, yy + bodyH + 6, w, readable ? Ui.GREEN : Ui.RED_INK, false);
		}
	}

	private void drawScrollPage(GuiGraphicsExtractor g, int x, int y, int w, float alpha) {
		int ink = Ui.alpha(Ui.INK, Math.max(0.05f, alpha));
		Component title = Component.translatable("scroll.matriochka.p" + page + ".title");
		g.text(font, title, x, y, Ui.alpha(Ui.RED_INK, Math.max(0.05f, alpha)), false);
		g.fill(x, y + 11, x + font.width(title), y + 12, Ui.alpha(0xFFB0782A, alpha));
		g.textWithWordWrap(font, Component.translatable("scroll.matriochka.p" + page), x, y + 20, scroll ? w - 90 : w, ink, false);
		if (scroll) drawDolls(g, x + w - 40, y + 140, page, 84);
		Component n = Component.literal((page + 1) + " / 5");
		g.text(font, n, x + w / 2 - font.width(n) / 2, top() + BH - 44, Ui.alpha(Ui.INK_SOFT, Math.max(0.05f, alpha)), false);
	}

	private void objective(GuiGraphicsExtractor g, int x, int y, int w) {
		int h = highest();
		String key = h < 0 ? "journal.matriochka.objective.guardian" : h >= 10 ? "journal.matriochka.objective.end" : "journal.matriochka.objective.next";
		if (h >= 10 && JournalPages.carries("whole_matryoshka") && !MatrioClient.state.getBooleanOr("f_end_tools", false)) key = "journal.matriochka.objective.zero";
		int yy = y + g.textWithWordWrap(font, Component.translatable(key, h + 1), x, y, w, Ui.INK, false) + 10;
		var s = MatrioClient.state;
		int max = s.getIntOr("doll_max", 0), layers = s.getIntOr("doll_layers", 0);
		int dx = x;
		for (int i = 0; i < max; i++) {
			int dw = new int[]{12, 10, 8}[Math.min(2, i)], dh = new int[]{17, 14, 11}[Math.min(2, i)];
			Ui.sprite(g, "life_" + Math.min(2, i) + (i < layers ? "_full" : "_empty"), dx, yy + 17 - dh, dw, dh);
			dx += dw + 1;
		}
		g.text(font, Component.translatable("journal.matriochka.doll_short"), x + Math.max(40, dx - x + 6), yy + 6, Ui.INK_SOFT, false);
		yy += 24;
		g.text(font, Component.translatable("journal.matriochka.group", s.getIntOr("members", 1)), x, yy, Ui.INK_SOFT, false);
		int pages = 0;
		for (int w2 = 1; w2 <= 10; w2++) pages += Integer.bitCount(s.getIntOr("pages_" + w2, 0));
		g.text(font, Component.translatable("journal.matriochka.pages", pages), x, yy + 12, Ui.INK_SOFT, false);
		String title = s.getStringOr("title", "");
		if (!title.isEmpty()) g.text(font, Component.translatable("title.matriochka." + title), x, yy + 24, Ui.RED_INK, false);
		yy += 36;
		int cycle = s.getIntOr("cycle", 0);
		if (cycle > 0 || JournalPages.endingsSeen() > 0) {
			g.text(font, Component.translatable("journal.matriochka.cycle", cycle + 1), x, yy, Ui.RED_INK, false);
			yy += 12;
		}
		Component endings = JournalPages.endingNames();
		if (endings != null) g.textWithWordWrap(font, Component.translatable("journal.matriochka.endings", endings), x, yy, w, Ui.INK_SOFT, false);
	}

	private void quests(GuiGraphicsExtractor g, int x, int y, int w, int mx, int my) {
		Component place = questWorld == 0 ? Component.translatable("journal.matriochka.surface")
			: questWorld == KARMA_CHAPTER ? Component.translatable("journal.matriochka.karma_paths") : Component.translatable("hud.matriochka.world", questWorld);
		g.text(font, place, x + 70 - font.width(place) / 2, top() + BH - 26, Ui.INK, false);
		int yy = y + 6;
		// full descriptions when they fit on the page, one line each otherwise (the full text shows on hover)
		int need = 0;
		for (Defs.QuestDef q : Content.QUESTS) {
			if (q.world() != questWorld) continue;
			Component d = open(q) ? Component.translatable("quest.matriochka." + q.id() + ".desc") : lockedText(q);
			need += 18 + Math.max(1, font.split(d, w - 9).size()) * 9;
		}
		boolean wrap = need <= top() + BH - 34 - yy;
		for (Defs.QuestDef q : Content.QUESTS) {
			if (q.world() != questWorld) continue;
			boolean done = done(q), open = open(q);
			Component sub = open ? Component.translatable("quest.matriochka." + q.id() + ".desc") : lockedText(q);
			int lines = wrap ? Math.max(1, font.split(sub, w - 9).size()) : 1;
			int rowH = 12 + lines * 9;
			if (mx >= x - 3 && mx < x + w + 2 && my >= yy - 2 && my < yy + rowH) {
				g.fill(x - 3, yy - 2, x + w + 2, yy + rowH, 0x1E8A2018);
				g.fill(x - 3, yy - 2, x - 2, yy + rowH, 0xFFB0782A);
			}
			int col = done ? Ui.GREEN : open ? Ui.INK : 0xFF9A8A6E;
			Ui.sprite(g, done ? "pip_done" : open ? "pip_open" : "pip_locked", x - 1, yy, 7, 7);
			String kind = q.objKind().equals("deliver") ? "obtain" : q.objKind();
			int prog = Math.min(q.objCount(), MatrioClient.state.getIntOr("c_" + kind + ":" + q.objTarget(), 0));
			Component p = Component.literal(prog + "/" + q.objCount());
			boolean showProg = !q.objKind().equals("choice") && open && !done;
			int titleW = w - 9 - (showProg ? font.width(p) + 4 : 0);
			Component name = Component.translatable("quest.matriochka." + q.id());
			g.text(font, font.width(name) > titleW ? font.substrByWidth(name, titleW - font.width("...")).getString() + "..." : name.getString(), x + 9, yy, col, false);
			if (showProg) g.text(font, p, x + w - font.width(p), yy, Ui.RED_INK, false);
			if (wrap) g.textWithWordWrap(font, sub, x + 9, yy + 10, w - 9, Ui.INK_SOFT, false);
			else {
				boolean cut = font.width(sub) > w - 9;
				g.text(font, cut ? font.substrByWidth(sub, w - 9 - font.width("...")).getString() + "..." : sub.getString(), x + 9, yy + 10, Ui.INK_SOFT, false);
				if (cut && mx >= x - 3 && mx < x + w + 2 && my >= yy - 2 && my < yy + rowH) g.setTooltipForNextFrame(font, font.split(sub, 200), mx, my);
			}
			yy += rowH + 6;
		}
	}

	private void karma(GuiGraphicsExtractor g, int x, int y, int w) {
		var s = MatrioClient.state;
		int k = s.getIntOr("karma", 0);
		g.text(font, Component.translatable("journal.matriochka.karma", k), x, y + 4, Ui.INK, false);
		Ui.vial(g, x, y + 16, w, 11, (k + 100) / 200f, k >= 0 ? 0xFFE8C060 : 0xFF8A3A9A, 0);
		g.fill(x + w / 2, y + 13, x + w / 2 + 1, y + 30, Ui.INK);
		Ui.sprite(g, "lantern", x, y + 34, 9, 13);
		lanternFlame(g, x, y + 34, 1f);
		g.text(font, Component.translatable("journal.matriochka.souls", s.getIntOr("souls", 0)), x + 13, y + 37, Ui.RED_INK, false);
		String tier = k >= 50 ? "light2" : k >= 25 ? "light1" : k <= -50 ? "dark2" : k <= -25 ? "dark1" : "neutral";
		g.textWithWordWrap(font, Component.translatable("journal.matriochka.karma." + tier), x, y + 54, w, Ui.INK_SOFT, false);
	}

	/** The flickering flame of a soul lantern at (x, y), with its halo. */
	static void lanternFlame(GuiGraphicsExtractor g, int x, int y, float strength) {
		long t = Ui.now();
		double n = Math.sin(t / 97.0) * 0.5 + Math.sin(t / 41.0 + 1.3) * 0.3 + Math.sin(t / 13.0) * 0.2;
		int frame = (int) Math.floorMod(t / 90, 3L);
		Ui.sprite(g, "glow", x - 8, y - 6, 24, 24, Ui.alpha(0xFFFFFFFF, Math.min(1f, (0.42f + 0.12f * (float) n) * strength)));
		Ui.sprite(g, "lantern_flame_" + frame, x, y, 9, 13, Ui.white(0.85f + 0.15f * (float) n));
	}

	private void worlds(GuiGraphicsExtractor g, int x, int y, int w, int mx, int my) {
		int done = MatrioClient.state.getIntOr("done", 0);
		for (int i = 0; i <= 10; i++) {
			boolean beaten = (done & (1 << i)) != 0, open = i == 0 || (done & (1 << (i - 1))) != 0;
			int ry = y + i * 14;
			if (mx >= x - 3 && mx < x + w + 2 && my >= ry - 2 && my < ry + 12) {
				g.fill(x - 3, ry - 2, x + w + 2, ry + 12, 0x1E8A2018);
				g.fill(x - 3, ry - 2, x - 2, ry + 12, 0xFFB0782A);
			}
			Component name = i == 0 ? Component.translatable("entity.matriochka.block_guardian") : Component.translatable("world.matriochka." + i);
			Ui.sprite(g, beaten ? "doll_small_full" : "doll_small_empty", x, ry - 1, 8, 11);
			if (i > 0) g.fill(x + w - 4, ry + 2, x + w, ry + 6, open ? Ui.worldColor(i) : 0x60605048);
			g.text(font, i == 0 ? name : Component.literal(i + "  ").append(name), x + 12, ry + 1, beaten ? Ui.GREEN : open ? Ui.INK : 0xFF9A8A6E, false);
			String variant = i == 0 ? "" : MatrioClient.state.getCompoundOrEmpty("variants").getStringOr(Integer.toString(i), "");
			if (!variant.isEmpty()) {
				// a little wax seal before the colour chip: green for the gentler variants, red lacquer for the harsher
				boolean kind = variant.equals("calm") || variant.equals("blessed");
				int sx = x + w - 11, sy = ry + 1;
				g.fill(sx, sy + 1, sx + 5, sy + 6, kind ? 0xFF3F6E2C : Ui.RED_INK);
				g.fill(sx + 1, sy, sx + 4, sy + 7, kind ? 0xFF3F6E2C : Ui.RED_INK);
				g.fill(sx + 1, sy + 2, sx + 2, sy + 3, Ui.GOLD);
				if (mx >= x - 3 && mx < x + w + 2 && my >= ry - 2 && my < ry + 12) {
					Component tip = Component.translatable("journal.matriochka.variant", Component.translatable(variantKey(variant, i)))
						.append("\n").append(Component.translatable("variant.matriochka." + variant + ".desc"));
					g.setTooltipForNextFrame(font, font.split(tip, 170), mx, my);
				}
			}
		}
	}

	/** The name of a variant in a world: calm and wild have their own name in every world (as in world/Variants). */
	private static String variantKey(String variant, int world) {
		if (variant.equals("calm") || variant.equals("wild")) return "variant.matriochka." + world + "." + variant;
		return "variant.matriochka." + variant;
	}

	/** The nested dolls, one more for every page or world reached, standing in a row that fits maxW. */
	private static void drawDolls(GuiGraphicsExtractor g, int cx, int base, int n, int maxW) {
		int count = Math.max(1, Math.min(5, n + 1));
		int total = 0;
		for (int i = 0; i < count; i++) total += NEST_W[i];
		int gap = count > 1 ? Math.min(3, (maxW - total) / (count - 1)) : 0;
		int x = cx - (total + gap * (count - 1)) / 2;
		long t = Ui.now();
		// a soft shadow they stand on
		for (int k = 0; k < 4; k++) g.fill(cx - (total / 2 + 6 - k * 4), base - 1 + k / 2, cx + (total / 2 + 6 - k * 4), base + 1 + k / 2, 0x16301808);
		for (int i = 0; i < count; i++) {
			int w = NEST_W[i], h = NEST_H[i];
			float bob = (float) Math.sin(t / 700.0 + i * 0.9) * 0.6f;
			g.pose().pushMatrix();
			g.pose().translate(0, bob);
			Ui.sprite(g, "nest_" + i, x, base - h, w, h);
			g.pose().popMatrix();
			float gl = Math.floorMod(t + i * 900L, 4500L) / 700f;
			Ui.glint(g, x + w * 0.3f, base - h * 0.62f, gl, 7);
			x += w + gap;
		}
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		if (!scroll && tab == PAGES_TAB) {
			int[] at = pipAt(left() + 20, top(), event.x(), event.y());
			if (at != null) {
				selectPage(at[0], at[1], at[0] * 5 + at[1] > pageWorld * 5 + pageIndex ? 1 : -1);
				return true;
			}
		}
		if (!scroll) {
			int l = left(), t = top();
			for (int i = 0; i < TABS.length; i++) {
				int rx = ribbonX(i);
				if (event.x() >= rx && event.x() < rx + 54 && event.y() >= t - Math.max(15, hang[i]) && event.y() < t) {
					switchTab(i);
					return true;
				}
			}
		}
		return super.mouseClicked(event, doubleClick);
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}
}
