package fr.achedon12.matriochka.client;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Supplier;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;

/**
 * The comfort options, opened from the Journal: the same red lacquer book. Left page, the screen (shakes, flashes,
 * soft effects, cinematics, subtitles, particles, gauge patterns); right page, the HUD plaque and the music. A switch
 * is a gilt pip on a lacquer button; a slider is a vial filled with gold, with a doll for a knob. Hovering a line
 * shows what it does. Changes are saved at once (config/matriochka-client.json).
 */
public class ComfortScreen extends Screen {
	private static final int BW = 340, BH = 214, PW = 155, ROW = 19, TOP = 42, CTRL = 58;
	/** A slider's track, leaving the value its own room on the right. */
	private static final int TRACK = 34;
	private final Screen parent;
	private final Ui.Motion motion = new Ui.Motion(300, 160);
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final List<Row> left = new ArrayList<>(), right = new ArrayList<>();
	private Row dragging;

	private enum Kind { TOGGLE, SLIDER, CYCLE }

	private static final class Row {
		final String key;
		final Kind kind;
		final Supplier<Float> get;
		final Consumer<Float> set;
		final Supplier<Component> value;
		float shown = -1;

		Row(String key, Kind kind, Supplier<Float> get, Consumer<Float> set, Supplier<Component> value) {
			this.key = key;
			this.kind = kind;
			this.get = get;
			this.set = set;
			this.value = value;
		}
	}

	public ComfortScreen(Screen parent) {
		super(Component.translatable("comfort.matriochka.title"));
		this.parent = parent;
		Comfort.Values v = Comfort.get();
		left.add(slider("shake", () -> v.shake / 100f, f -> v.shake = Math.round(f * 100)));
		left.add(toggle("flashes", () -> v.flashes, b -> v.flashes = b));
		left.add(toggle("soft_effects", () -> v.softEffects, b -> v.softEffects = b));
		left.add(toggle("cinematics", () -> v.cinematics, b -> v.cinematics = b));
		left.add(toggle("subtitles", () -> v.subtitles, b -> v.subtitles = b));
		left.add(toggle("particles", () -> v.reducedParticles, b -> v.reducedParticles = b));
		left.add(toggle("patterns", () -> v.patterns, b -> v.patterns = b));
		right.add(new Row("hud_scale", Kind.SLIDER, () -> (v.hudScale - 0.5f) / 1.5f, f -> v.hudScale = Math.round((0.5f + f * 1.5f) * 4) / 4f,
			() -> Component.literal("x" + trim(v.hudScale))));
		right.add(new Row("world_label", Kind.CYCLE, () -> (float) labelIndex(), f -> v.worldLabel = LABELS[(labelIndex() + 1) % LABELS.length],
			() -> Component.translatable(v.worldLabel.equals("off") ? "comfort.matriochka.off" : "comfort.matriochka.corner." + v.worldLabel)));
		right.add(slider("music_explore", () -> v.musicExplore / 100f, f -> v.musicExplore = Math.round(f * 100)));
		right.add(slider("music_danger", () -> v.musicDanger / 100f, f -> v.musicDanger = Math.round(f * 100)));
		right.add(slider("music_boss", () -> v.musicBoss / 100f, f -> v.musicBoss = Math.round(f * 100)));
		right.add(slider("music_layers", () -> v.musicLayers / 100f, f -> v.musicLayers = Math.round(f * 100)));
		right.add(slider("music_stings", () -> v.musicStings / 100f, f -> v.musicStings = Math.round(f * 100)));
	}

	private static String trim(float f) {
		return f == Math.floor(f) ? Integer.toString((int) f) : Float.toString(f);
	}

	/** Where the world's name can stay on screen: nowhere, or a corner. */
	private static final String[] LABELS = {"off", "top_left", "top_right", "bottom_left", "bottom_right"};

	private static int labelIndex() {
		for (int i = 0; i < LABELS.length; i++) if (LABELS[i].equals(Comfort.get().worldLabel)) return i;
		return 0;
	}

	private static int cornerIndex() {
		for (int i = 0; i < Comfort.CORNERS.length; i++) if (Comfort.CORNERS[i].equals(Comfort.get().hudCorner)) return i;
		return 0;
	}

	private static Row slider(String key, Supplier<Float> get, Consumer<Float> set) {
		return new Row(key, Kind.SLIDER, get, f -> set.accept(Ui.clamp01(f)), () -> Component.literal(Math.round(get.get() * 100) + "%"));
	}

	private static Row toggle(String key, Supplier<Boolean> get, Consumer<Boolean> set) {
		return new Row(key, Kind.TOGGLE, () -> get.get() ? 1f : 0f, f -> set.accept(f > 0.5f),
			() -> Component.translatable(get.get() ? "comfort.matriochka.on" : "comfort.matriochka.off"));
	}

	private int left() { return (width - BW) / 2; }
	private int top() { return Math.max(0, Math.min((height - BH) / 2 + 12, height - BH - 1)); }

	@Override
	protected void init() {
		if (Ui.now() - motion.openedAt() < 100) Ui.pageTurn();
		buttons.clear();
		int l = left(), t = top();
		buttons.add(l + 24, t + BH - 30, 64, 16, Component.translatable("comfort.matriochka.defaults"), () -> {
			Comfort.Values d = new Comfort.Values(), v = Comfort.get();
			v.shake = d.shake;
			v.flashes = d.flashes;
			v.softEffects = d.softEffects;
			v.cinematics = d.cinematics;
			v.subtitles = d.subtitles;
			v.reducedParticles = d.reducedParticles;
			v.patterns = d.patterns;
			v.hudScale = d.hudScale;
			v.hudCorner = d.hudCorner;
			v.worldLabel = d.worldLabel;
			v.musicExplore = d.musicExplore;
			v.musicDanger = d.musicDanger;
			v.musicBoss = d.musicBoss;
			v.musicLayers = d.musicLayers;
			v.musicStings = d.musicStings;
			Comfort.changed();
		});
		buttons.add(l + BW - 88, t + BH - 30, 64, 16, Component.translatable("journal.matriochka.previous"), this::onClose);
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Comfort.changed();
		Ui.pageTurn();
		motion.close(() -> fr.achedon12.matriochka.client.mc.McClient.setScreen(minecraft, parent));
	}

	@Override
	public void tick() {
		super.tick();
		motion.tick();
	}

	// ---------------------------------------------------------------- layout
	private int pageX(boolean rightPage) {
		return rightPage ? left() + 28 + PW : left() + 20;
	}

	private int rowY(int i) {
		return top() + TOP + i * ROW;
	}

	private int ctrlX(boolean rightPage) {
		return pageX(rightPage) + PW - 18 - CTRL;
	}

	/** The row under a point and its page, or null. */
	private Object[] rowAt(double mx, double my) {
		for (int p = 0; p < 2; p++) {
			List<Row> rows = p == 0 ? left : right;
			int x = pageX(p == 1);
			for (int i = 0; i < rows.size(); i++) {
				int y = rowY(i);
				if (mx >= x - 3 && mx < x + PW - 16 && my >= y - 3 && my < y + ROW - 4) return new Object[]{rows.get(i), p == 1};
			}
		}
		return null;
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
		motion.push(g, l + BW / 2f, t + BH / 2f);
		page(g, false, left, Component.translatable("comfort.matriochka.page.screen"), mx, my);
		page(g, true, right, Component.translatable("comfort.matriochka.page.hud"), mx, my);
		buttons.draw(g, font, mx, my);
		motion.pop(g);
		Object[] at = rowAt(mx, my);
		if (at != null && dragging == null) {
			Row r = (Row) at[0];
			g.setTooltipForNextFrame(font, font.split(Component.translatable("comfort.matriochka." + r.key + ".desc"), 190), mx, my);
		}
	}

	private void page(GuiGraphicsExtractor g, boolean rightPage, List<Row> rows, Component title, int mx, int my) {
		int x = pageX(rightPage), cw = PW - 18, t = top();
		g.text(font, title, x + cw / 2 - font.width(title) / 2, t + 22, Ui.RED_INK, false);
		Ui.sprite(g, "divider", x + cw / 2 - 60, t + 31, 120, 10);
		int cx = ctrlX(rightPage);
		for (int i = 0; i < rows.size(); i++) {
			Row r = rows.get(i);
			int y = rowY(i);
			boolean over = mx >= x - 3 && mx < x + cw + 2 && my >= y - 3 && my < y + ROW - 4;
			if (over) {
				g.fill(x - 3, y - 3, x + cw + 2, y + ROW - 4, 0x1E8A2018);
				g.fill(x - 3, y - 3, x - 2, y + ROW - 4, 0xFFB0782A);
			}
			Component label = Component.translatable("comfort.matriochka." + r.key);
			int lw = cx - x - 4;
			// a long label shrinks first (down to 75%), and is only cut when even that does not fit
			int fw = font.width(label);
			float ls = fw > lw ? Math.max(0.75f, lw / (float) fw) : 1f;
			String text = fw * ls > lw ? font.substrByWidth(label, Math.round(lw / ls) - font.width("...")).getString() + "..." : label.getString();
			g.pose().pushMatrix();
			g.pose().translate(x, y + 2 + (1 - ls) * 4);
			g.pose().scale(ls, ls);
			g.text(font, text, 0, 0, Ui.INK, false);
			g.pose().popMatrix();
			float v = r.get.get();
			if (r.shown < 0) r.shown = v;
			r.shown = Ui.approach(r.shown, v, 14, 0.016f);
			switch (r.kind) {
				case TOGGLE -> {
					boolean on = v > 0.5f;
					Ui.sprite(g, on ? "btn" : "btn_off", cx, y - 1, CTRL, 12);
					if (over) Ui.sprite(g, "btn_hover", cx, y - 1, CTRL, 12, Ui.white(0.6f));
					Ui.sprite(g, on ? "pip_done" : "pip_locked", cx + 4, y + 1, 7, 7);
					Component val = r.value.get();
					Ui.embossed(g, font, val, cx + 14 + (CTRL - 18 - font.width(val)) / 2, y + 1, on ? Ui.LIGHT : 0xFFB8A890);
				}
				case CYCLE -> {
					Ui.sprite(g, "btn", cx, y - 1, CTRL, 12);
					if (over) Ui.sprite(g, "btn_hover", cx, y - 1, CTRL, 12, Ui.white(0.6f));
					Component val = r.value.get();
					Ui.embossed(g, font, val, cx + (CTRL - font.width(val)) / 2, y + 1, Ui.LIGHT);
				}
				case SLIDER -> {
					Ui.vial(g, cx, y, TRACK, 9, r.shown, 0xFFE8C060, 0);
					int kx = cx + 5 + Math.round((TRACK - 10) * Ui.clamp01(r.shown));
					Ui.sprite(g, "doll_small_full", kx - 4, y - 2, 8, 11);
					// the value right of the track, clear of the knob (shrunk a little when "100%" is too wide)
					Component val = r.value.get();
					int room = CTRL - TRACK - 5, vw = font.width(val);
					float vs = vw > room ? Math.max(0.75f, room / (float) vw) : 1f;
					g.pose().pushMatrix();
					g.pose().translate(cx + CTRL - vw * vs, y + 1 + (1 - vs) * 4);
					g.pose().scale(vs, vs);
					g.text(font, val, 0, 0, Ui.INK_SOFT, false);
					g.pose().popMatrix();
				}
			}
		}
	}

	// ---------------------------------------------------------------- input
	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		Object[] at = rowAt(event.x(), event.y());
		if (at != null) {
			Row r = (Row) at[0];
			switch (r.kind) {
				case TOGGLE -> {
					r.set.accept(r.get.get() > 0.5f ? 0f : 1f);
					Ui.click();
					Comfort.changed();
				}
				case CYCLE -> {
					r.set.accept(0f);
					Ui.click();
					Comfort.changed();
				}
				case SLIDER -> {
					dragging = r;
					drag(r, (Boolean) at[1], event.x());
					Ui.click();
				}
			}
			return true;
		}
		return super.mouseClicked(event, doubleClick);
	}

	private void drag(Row r, boolean rightPage, double mx) {
		int cx = ctrlX(rightPage);
		r.set.accept(Ui.clamp01((float) (mx - cx - 5) / (TRACK - 10)));
	}

	@Override
	public boolean mouseDragged(MouseButtonEvent event, double dx, double dy) {
		if (dragging != null) {
			drag(dragging, right.contains(dragging), event.x());
			return true;
		}
		return super.mouseDragged(event, dx, dy);
	}

	@Override
	public boolean mouseReleased(MouseButtonEvent event) {
		if (dragging != null) {
			dragging = null;
			Comfort.changed();
			return true;
		}
		return super.mouseReleased(event);
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}
}
