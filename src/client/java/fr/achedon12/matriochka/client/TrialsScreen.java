package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.replay.ReplayNet;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;

/**
 * The Trials, in the Journal's red lacquer book: the left page lists the eleven trials with a pip for each one won
 * and the best time; the right page tells the chosen trial, its par, your best and your group's, and the server's
 * board, with the button that begins it. A second leaf lists the titles you own and lets you wear one.
 */
public class TrialsScreen extends Screen {
	private static final int BW = 340, BH = 214, PW = 155, ROW = 12, LIST_Y = 42;
	private final Screen parent;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(320, 170);
	private int selected;
	private boolean titles;
	private long pageAt = -1;

	public TrialsScreen(Screen parent) {
		super(Component.translatable("trials.matriochka.title"));
		this.parent = parent;
	}

	private int left() { return (width - BW) / 2; }
	private int top() { return Math.max(0, Math.min((height - BH) / 2 + 12, height - BH - 1)); }

	private static boolean unlocked() {
		var s = MatrioClient.state;
		return s.getBooleanOr("f_end_seal", false) || s.getBooleanOr("f_end_absorb", false) || s.getBooleanOr("f_end_tools", false);
	}

	private static boolean inTrial() {
		return MatrioClient.state.getCompoundOrEmpty("trial").contains("key");
	}

	private ReplayContent.TrialDef trial() {
		return ReplayContent.TRIALS.get(Math.max(0, Math.min(ReplayContent.TRIALS.size() - 1, selected)));
	}

	@Override
	protected void init() {
		if (Ui.now() - motion.openedAt() < 100) Ui.pageTurn();
		ClientPlayNetworking.send(new ReplayNet.TrialAction("board", ""));
		rebuild();
	}

	/** The board arrived or changed: redraw with it. */
	public void refresh() {
		rebuild();
	}

	private void rebuild() {
		buttons.clear();
		int l = left(), t = top();
		int rx = l + 28 + PW;
		buttons.add(l + 20 + (PW - 18) / 2 - 38, t + BH - 30, 76, 16,
			Component.translatable(titles ? "trials.matriochka.back" : "trials.matriochka.titles"), () -> {
				titles = !titles;
				pageAt = Ui.now();
				Ui.pageTurn();
				rebuild();
			});
		if (titles) {
			int y = t + 40;
			for (String id : ownedTitles()) {
				String wear = id;
				buttons.add(rx + 137 - 40, y - 2, 40, 12, Component.translatable("trials.matriochka.wear"), () -> send("title", wear),
					() -> !MatrioClient.state.getStringOr("title", "").equals(wear));
				y += 14;
				if (y > t + BH - 50) break;
			}
			return;
		}
		if (inTrial()) {
			buttons.add(rx + 137 - 76, t + BH - 30, 76, 16, Component.translatable("trials.matriochka.leave"), () -> {
				send("leave", "");
				onClose();
			});
		} else {
			buttons.add(rx + 137 - 76, t + BH - 30, 76, 16, Component.translatable("trials.matriochka.begin"), () -> {
				send("start", trial().key());
				onClose();
			}, TrialsScreen::unlocked);
		}
	}

	private void send(String action, String arg) {
		ClientPlayNetworking.send(new ReplayNet.TrialAction(action, arg));
	}

	/** The titles this player owns: from the trials and from the quests that give one. */
	static List<String> ownedTitles() {
		var s = MatrioClient.state;
		List<String> out = new ArrayList<>();
		for (ReplayContent.TrialDef d : ReplayContent.TRIALS) if (s.getBooleanOr("f_title_" + d.title(), false)) out.add(d.title());
		if (s.getBooleanOr("f_title_" + ReplayContent.SWIFT_TITLE, false)) out.add(ReplayContent.SWIFT_TITLE);
		for (Defs.QuestDef q : Content.QUESTS) {
			if (q.rewardKind().equals("title") && s.getBooleanOr("f_quest_" + q.id(), false) && !out.contains(q.rewardTarget())) out.add(q.rewardTarget());
		}
		return out;
	}

	@Override
	public void tick() {
		super.tick();
		motion.tick();
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(SoundEvents.BOOK_PUT, 1.1f, 0.8f);
		motion.close(() -> minecraft.gui.setScreen(parent instanceof JournalScreen ? parent : null));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top();
		motion.push(g, l + BW / 2f, t + BH / 2f);
		Ui.sprite(g, "book", l, t, BW, BH);
		Ui.wanderingGlint(g, new int[][]{{l + 4, t + 4}, {l + BW - 4, t + 4}, {l + 4, t + BH - 4}, {l + BW - 4, t + BH - 4}}, 1700, 23);
		motion.pop(g);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		int l = left(), t = top();
		int lx = l + 20, rx = l + 28 + PW, cw = PW - 18;
		motion.push(g, l + BW / 2f, t + BH / 2f);
		list(g, lx, t, cw, mx, my);
		float slide = pageAt < 0 ? 1 : Ui.easeOut(Ui.since(pageAt, 260));
		g.pose().pushMatrix();
		g.pose().translate((1 - slide) * 10, 0);
		if (titles) titlesPage(g, rx, t + 24, cw);
		else detail(g, rx, t + 24, cw);
		g.pose().popMatrix();
		buttons.draw(g, font, mx, my);
		motion.pop(g);
	}

	private Component shortName(ReplayContent.TrialDef d) {
		return d.world() == 0 ? Component.translatable("trials.matriochka.gauntlet") : Component.translatable("hud.matriochka.world", d.world());
	}

	private static CompoundTag boardOf(String key) {
		return ReplayClient.board.getCompoundOrEmpty(key);
	}

	/** Left page: the eleven trials, a pip for each won, their best times. */
	private void list(GuiGraphicsExtractor g, int lx, int t, int cw, int mx, int my) {
		Component chapter = Component.translatable("trials.matriochka.title");
		g.text(font, chapter, lx + cw / 2 - font.width(chapter) / 2, t + 22, Ui.RED_INK, false);
		Ui.sprite(g, "divider", lx + cw / 2 - 60, t + 31, 120, 10);
		boolean open = unlocked();
		for (int i = 0; i < ReplayContent.TRIALS.size(); i++) {
			ReplayContent.TrialDef d = ReplayContent.TRIALS.get(i);
			int ry = t + LIST_Y + i * ROW;
			boolean over = mx >= lx - 3 && mx < lx + cw + 2 && my >= ry - 2 && my < ry + ROW - 2;
			if (i == selected || over) {
				g.fill(lx - 3, ry - 2, lx + cw + 2, ry + ROW - 2, i == selected ? 0x2E8A2018 : 0x1E8A2018);
				g.fill(lx - 3, ry - 2, lx - 2, ry + ROW - 2, 0xFFB0782A);
			}
			boolean won = MatrioClient.state.getBooleanOr("f_trial_done_" + d.key(), false);
			Ui.sprite(g, won ? "pip_done" : open ? "pip_open" : "pip_locked", lx, ry, 7, 7);
			if (d.world() > 0) g.fill(lx + 10, ry + 2, lx + 13, ry + 5, Ui.worldColor(d.world()));
			g.text(font, shortName(d), lx + 16, ry, open ? Ui.INK : 0xFF9A8A6E, false);
			int best = boardOf(d.key()).getIntOr("mine", 0);
			Component time = Component.literal(best > 0 ? ReplayHud.clock(best) : "-");
			g.text(font, time, lx + cw - font.width(time), ry, best > 0 ? Ui.RED_INK : 0xFF9A8A6E, false);
		}
	}

	/** Right page: the chosen trial, its times and the board. */
	private void detail(GuiGraphicsExtractor g, int x, int y, int w) {
		ReplayContent.TrialDef d = trial();
		int yy = y + Ui.wrap(g, font, Component.translatable("trial.matriochka." + d.key()), x, y, w, Ui.RED_INK);
		g.fill(x, yy + 1, x + Math.min(w, 60), yy + 2, 0xFFB0782A);
		yy += 6;
		if (!unlocked()) {
			Ui.wrap(g, font, Component.translatable("trials.matriochka.locked"), x, yy, w, Ui.INK_SOFT);
			return;
		}
		Component desc = d.world() == 0 ? Component.translatable("trials.matriochka.desc.gauntlet")
			: Component.translatable("trials.matriochka.desc.world", Component.translatable("world.matriochka." + d.world()));
		// the page ends above the Begin button; the description gives way first in a longer language
		int bottom = top() + BH - 34;
		yy += Ui.block(g, font, List.of(new Ui.Para(desc, Ui.INK_SOFT, 0)), x, yy, w, Math.max(18, bottom - yy - 70)) + 5;
		CompoundTag b = boardOf(d.key());
		yy = line(g, x, yy, w, "trials.matriochka.par", d.par() * 20);
		yy = line(g, x, yy, w, "trials.matriochka.mine", b.getIntOr("mine", 0));
		yy = line(g, x, yy, w, "trials.matriochka.group", b.getIntOr("group", 0));
		yy += 4;
		g.text(font, Component.translatable("trials.matriochka.board"), x, yy, Ui.RED_INK, false);
		yy += 11;
		int rank = 1;
		for (Tag tag : b.getListOrEmpty("top")) {
			if (!(tag instanceof CompoundTag row) || rank > 5 || yy + 9 > bottom) break;
			Component r = Component.literal(rank + ".  " + ReplayHud.clock(row.getIntOr("ticks", 0)));
			g.text(font, r, x, yy, rank == 1 ? Ui.RED_INK : Ui.INK, false);
			String names = row.getStringOr("names", "");
			int nx = x + 62, nw = w - 62;
			String cut = font.width(names) > nw ? font.plainSubstrByWidth(names, nw - font.width("...")) + "..." : names;
			g.text(font, Component.literal(cut), nx, yy, Ui.INK_SOFT, false);
			yy += 10;
			rank++;
		}
		if (rank == 1) Ui.wrap(g, font, Component.translatable("trials.matriochka.board.empty"), x, yy, w, 0xFF9A8A6E);
	}

	private int line(GuiGraphicsExtractor g, int x, int y, int w, String key, int ticks) {
		Component label = Component.translatable(key);
		g.text(font, label, x, y, Ui.INK, false);
		Component v = Component.literal(ticks > 0 ? ReplayHud.clock(ticks) : "-");
		g.text(font, v, x + w - font.width(v), y, ticks > 0 ? Ui.RED_INK : 0xFF9A8A6E, false);
		return y + 11;
	}

	/** Right page, second leaf: the titles owned, the one worn marked with a gilt seal. */
	private void titlesPage(GuiGraphicsExtractor g, int x, int y, int w) {
		g.text(font, Component.translatable("trials.matriochka.titles"), x, y, Ui.RED_INK, false);
		g.fill(x, y + 11, x + 60, y + 12, 0xFFB0782A);
		List<String> owned = ownedTitles();
		if (owned.isEmpty()) {
			Ui.wrap(g, font, Component.translatable("trials.matriochka.titles.none"), x, y + 18, w, Ui.INK_SOFT);
			return;
		}
		String worn = MatrioClient.state.getStringOr("title", "");
		int yy = y + 18;
		for (String id : owned) {
			boolean on = id.equals(worn);
			if (on) {
				g.fill(x - 1, yy + 1, x + 4, yy + 6, Ui.RED_INK);
				g.fill(x + 1, yy + 2, x + 2, yy + 3, Ui.GOLD);
			}
			g.text(font, Component.translatable("title.matriochka." + id), x + 8, yy, on ? Ui.RED_INK : Ui.INK, false);
			yy += 14;
			if (yy > top() + BH - 50) break;
		}
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		int lx = left() + 20, t = top(), cw = PW - 18;
		for (int i = 0; i < ReplayContent.TRIALS.size(); i++) {
			int ry = t + LIST_Y + i * ROW;
			if (event.x() >= lx - 3 && event.x() < lx + cw + 2 && event.y() >= ry - 2 && event.y() < ry + ROW - 2) {
				if (i != selected) {
					selected = i;
					titles = false;
					pageAt = Ui.now();
					Ui.pageTurn();
					rebuild();
				}
				return true;
			}
		}
		return super.mouseClicked(event, doubleClick);
	}
}
