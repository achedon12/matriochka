package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.net.Net;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;

/**
 * The Artisan's Scroll is a birch-paper roll on two wooden rods; the Journal is an open book in a lacquered cover with
 * ribbon bookmarks. Left page: the illustration of the current chapter. Right page: its content.
 */
public class JournalScreen extends Screen {
	private static final int BW = 340, BH = 214;
	private static final String[] TABS = {"objective", "quests", "karma", "worlds", "scroll"};
	private final boolean scroll;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private int tab, page, questWorld;

	public JournalScreen(boolean scroll) {
		super(Component.translatable(scroll ? "item.matriochka.artisan_scroll" : "item.matriochka.artisan_journal"));
		this.scroll = scroll;
	}

	/** Opens the journal on a given tab (used by the showcase). */
	public JournalScreen tab(int t) {
		this.tab = t;
		return this;
	}

	private int left() { return (width - BW) / 2; }
	private int top() { return (height - BH) / 2 + 6; }

	@Override
	protected void init() {
		rebuild();
	}

	private void rebuild() {
		buttons.clear();
		int l = left(), t = top();
		boolean pages = scroll || tab == 4;
		if (pages) {
			buttons.add(l + BW / 2 - 70, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.previous"), () -> page = Math.max(0, page - 1), () -> page > 0);
			buttons.add(l + BW / 2 + 30, t + BH - 30, 40, 16, Component.translatable("journal.matriochka.next"), () -> page = Math.min(4, page + 1), () -> page < 4);
		}
		if (!scroll && tab == 1) {
			buttons.add(l + BW / 2 + 18, t + BH - 30, 18, 16, Component.literal("<"), () -> { questWorld = Math.max(0, questWorld - 1); rebuild(); }, () -> questWorld > 0);
			buttons.add(l + BW - 40, t + BH - 30, 18, 16, Component.literal(">"), () -> { questWorld = Math.min(10, questWorld + 1); rebuild(); }, () -> questWorld < 10);
			int y = t + 30;
			for (Defs.QuestDef q : Content.QUESTS) {
				if (q.world() != questWorld) continue;
				if (q.objKind().equals("choice") && !done(q) && unlocked(q.world())) {
					buttons.add(l + BW - 98, y + 18, 36, 14, Component.translatable("journal.matriochka.help"), () -> send(q.id(), 1));
					buttons.add(l + BW - 60, y + 18, 36, 14, Component.translatable("journal.matriochka.betray"), () -> send(q.id(), -1));
				}
				y += 26;
			}
		}
	}

	private static boolean done(Defs.QuestDef q) {
		return MatrioClient.state.getBooleanOr("f_quest_" + q.id(), false);
	}

	private void send(String quest, int choice) {
		ClientPlayNetworking.send(new Net.ChoicePayload(quest, choice));
		onClose();
	}

	private static boolean unlocked(int world) {
		return world == 0 || (MatrioClient.state.getIntOr("done", 0) & (1 << (world - 1))) != 0;
	}

	private static int highest() {
		int done = MatrioClient.state.getIntOr("done", 0), best = -1;
		for (int i = 0; i <= 10; i++) if ((done & (1 << i)) != 0) best = i;
		return best;
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top();
		if (scroll) {
			// the roll: paper between two turned wooden rods
			Ui.paper(g, l + 30, t + 8, BW - 60, BH - 16);
			rod(g, l + 18, t, BW - 36);
			rod(g, l + 18, t + BH - 10, BW - 36);
			return;
		}
		// ribbons peek above the cover; the active one hangs lower
		for (int i = 0; i < TABS.length; i++) {
			int rx = l + 28 + i * 60;
			boolean on = tab == i;
			Ui.sprite(g, on ? "ribbon_on" : "ribbon", rx, t - (on ? 22 : 16), 54, 40);
			Component label = Component.translatable("journal.matriochka.tab." + TABS[i]);
			g.text(font, label, rx + 27 - font.width(label) / 2, t - (on ? 17 : 11), on ? 0xFF1E1410 : Ui.LIGHT, false);
		}
		Ui.frame(g, l, t, BW, BH);
		int pw = (BW - 30) / 2;
		Ui.paper(g, l + 11, t + 11, pw, BH - 22);
		Ui.paper(g, l + 19 + pw, t + 11, pw, BH - 22);
		// the spine: a gold seam between the pages
		g.fill(l + BW / 2 - 1, t + 11, l + BW / 2 + 1, t + BH - 11, 0xFF96682A);
	}

	private static void rod(GuiGraphicsExtractor g, int x, int y, int w) {
		g.fill(x, y, x + w, y + 10, 0xFF1E1410);
		g.fill(x + 1, y + 1, x + w - 1, y + 9, 0xFF784A28);
		g.fill(x + 1, y + 2, x + w - 1, y + 4, 0xFF9A6238);
		g.fill(x - 4, y - 1, x + 3, y + 11, 0xFFB3261E);
		g.fill(x + w - 3, y - 1, x + w + 4, y + 11, 0xFFB3261E);
		g.fill(x - 3, y + 4, x + 2, y + 6, 0xFFE8C060);
		g.fill(x + w - 2, y + 4, x + w + 3, y + 6, 0xFFE8C060);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		int l = left(), t = top();
		int pw = (BW - 30) / 2;
		int lx = l + 20, rx = l + 28 + pw, cw = pw - 18;
		if (scroll) {
			drawScrollPage(g, l + 46, t + 24, BW - 92);
		} else {
			// left page: the chapter's illustration
			drawDolls(g, lx + cw / 2, t + 150, tab == 4 ? page : Math.max(0, Math.min(4, highest() + 1)));
			Component chapter = Component.translatable("journal.matriochka.tab." + TABS[tab]);
			g.text(font, chapter, lx + cw / 2 - font.width(chapter) / 2, t + 22, Ui.INK, false);
			g.fill(lx + 10, t + 33, lx + cw - 10, t + 34, 0xFF96682A);
			switch (tab) {
				case 0 -> objective(g, rx, t + 24, cw);
				case 1 -> quests(g, rx, t + 24, cw);
				case 2 -> karma(g, rx, t + 24, cw);
				case 3 -> worlds(g, rx, t + 24, cw);
				default -> drawScrollPage(g, rx, t + 24, cw);
			}
		}
		buttons.draw(g, font, mx, my);
	}

	private void drawScrollPage(GuiGraphicsExtractor g, int x, int y, int w) {
		Component title = Component.translatable("scroll.matriochka.p" + page + ".title");
		g.text(font, title, x, y, 0xFF8A2018, false);
		g.fill(x, y + 11, x + font.width(title), y + 12, 0xFF96682A);
		g.textWithWordWrap(font, Component.translatable("scroll.matriochka.p" + page), x, y + 20, scroll ? w - 90 : w, Ui.INK, false);
		if (scroll) drawDolls(g, x + w - 40, y + 140, page);
		Component n = Component.literal((page + 1) + " / 5");
		g.text(font, n, x + w / 2 - font.width(n) / 2 - (scroll ? 0 : 0), top() + BH - 44, Ui.INK_SOFT, false);
	}

	private void objective(GuiGraphicsExtractor g, int x, int y, int w) {
		int h = highest();
		String key = h < 0 ? "journal.matriochka.objective.guardian" : h >= 10 ? "journal.matriochka.objective.end" : "journal.matriochka.objective.next";
		int yy = y + g.textWithWordWrap(font, Component.translatable(key, h + 1), x, y, w, Ui.INK, false) + 10;
		var s = MatrioClient.state;
		for (int i = 0; i < s.getIntOr("doll_max", 0); i++) Ui.sprite(g, i < s.getIntOr("doll_layers", 0) ? "doll_full" : "doll_empty", x + i * 12, yy, 9, 12);
		g.text(font, Component.translatable("journal.matriochka.doll_short"), x + 40, yy + 2, Ui.INK_SOFT, false);
		yy += 20;
		g.text(font, Component.translatable("journal.matriochka.group", s.getIntOr("members", 1)), x, yy, Ui.INK_SOFT, false);
		int pages = 0;
		for (int w2 = 1; w2 <= 10; w2++) pages += Integer.bitCount(s.getIntOr("pages_" + w2, 0));
		g.text(font, Component.translatable("journal.matriochka.pages", pages), x, yy + 12, Ui.INK_SOFT, false);
		String title = s.getStringOr("title", "");
		if (!title.isEmpty()) g.text(font, Component.translatable("title.matriochka." + title), x, yy + 24, 0xFF8A2018, false);
	}

	private void quests(GuiGraphicsExtractor g, int x, int y, int w) {
		Component place = questWorld == 0 ? Component.translatable("journal.matriochka.surface") : Component.translatable("hud.matriochka.world", questWorld);
		g.text(font, place, x + w / 2 - font.width(place) / 2 + 20, top() + BH - 26, Ui.INK, false);
		int yy = y + 6;
		for (Defs.QuestDef q : Content.QUESTS) {
			if (q.world() != questWorld) continue;
			boolean done = done(q), open = unlocked(q.world());
			int col = done ? Ui.GREEN : open ? Ui.INK : 0xFFA89878;
			g.fill(x, yy + 2, x + 4, yy + 6, done ? Ui.GREEN : open ? 0xFFB3261E : 0xFFA89878);
			g.text(font, Component.translatable("quest.matriochka." + q.id()), x + 8, yy, col, false);
			String kind = q.objKind().equals("deliver") ? "obtain" : q.objKind();
			int prog = Math.min(q.objCount(), MatrioClient.state.getIntOr("c_" + kind + ":" + q.objTarget(), 0));
			if (!q.objKind().equals("choice") && open && !done) {
				Component p = Component.literal(prog + "/" + q.objCount());
				g.text(font, p, x + w - font.width(p), yy, 0xFF8A2018, false);
			}
			Component sub = open ? Component.translatable("quest.matriochka." + q.id() + ".desc") : Component.translatable("journal.matriochka.locked");
			g.text(font, font.substrByWidth(sub, w - 8).getString(), x + 8, yy + 10, Ui.INK_SOFT, false);
			yy += 26;
		}
	}

	private void karma(GuiGraphicsExtractor g, int x, int y, int w) {
		int k = MatrioClient.state.getIntOr("karma", 0);
		g.text(font, Component.translatable("journal.matriochka.karma", k), x, y + 4, Ui.INK, false);
		Ui.gauge(g, x, y + 18, w, 8, (k + 100) / 200f, k >= 0 ? 0xFFE8C060 : 0xFF7A2A5A);
		g.fill(x + w / 2, y + 15, x + w / 2 + 1, y + 29, Ui.INK);
		g.text(font, Component.translatable("journal.matriochka.souls", MatrioClient.state.getIntOr("souls", 0)), x, y + 36, 0xFF8A2018, false);
		String tier = k >= 50 ? "light2" : k >= 25 ? "light1" : k <= -50 ? "dark2" : k <= -25 ? "dark1" : "neutral";
		g.textWithWordWrap(font, Component.translatable("journal.matriochka.karma." + tier), x, y + 52, w, Ui.INK_SOFT, false);
	}

	private void worlds(GuiGraphicsExtractor g, int x, int y, int w) {
		int done = MatrioClient.state.getIntOr("done", 0);
		for (int i = 0; i <= 10; i++) {
			boolean beaten = (done & (1 << i)) != 0, open = i == 0 || (done & (1 << (i - 1))) != 0;
			Component name = i == 0 ? Component.translatable("entity.matriochka.block_guardian") : Component.translatable("world.matriochka." + i);
			Ui.sprite(g, beaten ? "doll_full" : "doll_empty", x, y + i * 14, 7, 10);
			g.text(font, i == 0 ? name : Component.literal(i + "  ").append(name), x + 12, y + i * 14 + 1, beaten ? Ui.GREEN : open ? Ui.INK : 0xFFA89878, false);
		}
	}

	/** The nested dolls, one more for every page or world reached, drawn in lacquer and gold. */
	private static void drawDolls(GuiGraphicsExtractor g, int cx, int base, int n) {
		int count = Math.max(1, Math.min(5, n + 1));
		for (int i = 0; i < count; i++) {
			int s = 46 - i * 8;
			int ox = cx + (i - (count - 1) / 2) * 0;
			int col = i % 2 == 0 ? 0xFFB3261E : 0xFF1E1410;
			int by = base - i * 3;
			g.fill(ox - s / 2, by - s, ox + s / 2, by, col);
			g.fill(ox - s / 2 + 2, by - s - 2, ox + s / 2 - 2, by - s, col);
			g.fill(ox - s / 3, by - s - s / 2, ox + s / 3, by - s, col);
			g.fill(ox - s / 4, by - s - s / 2 + 3, ox + s / 4, by - s - 3, 0xFFF0D0B0);
			g.fill(ox - s / 4, by - s / 2 - 4, ox + s / 4, by - s / 4, 0xFFE8C060);
			g.outline(ox - s / 2 - 1, by - s - 1, s + 2, s + 2, 0xFF96682A);
		}
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (buttons.click(event.x(), event.y())) return true;
		if (!scroll) {
			int l = left(), t = top();
			for (int i = 0; i < TABS.length; i++) {
				int rx = l + 28 + i * 60;
				if (event.x() >= rx && event.x() < rx + 54 && event.y() >= t - 22 && event.y() < t) {
					tab = i;
					page = 0;
					rebuild();
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
