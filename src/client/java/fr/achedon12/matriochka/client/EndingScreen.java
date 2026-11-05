package fr.achedon12.matriochka.client;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.locale.Language;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;

/**
 * The cinematic of an ending: the Artisan's Scroll unrolls, the ending's lines rise across the parchment like a
 * credits crawl, then its lasting consequence and the credits. The nested dolls stand at the foot of the page: they
 * close for Sealed, darken for Absorbed, and for Set Down the Tools they open one by one until the last Scroll is left
 * blank.
 */
public class EndingScreen extends Screen {
	private static final int BW = 340, BH = 214, UNROLL_MS = 900;
	private static final float SPEED = 13f; // pixels per second
	private final String kind;
	private final long opened = Ui.now();
	private final List<Line> lines = new ArrayList<>();
	private int contentH;

	private record Line(FormattedCharSequence text, int color, int y) {}

	public EndingScreen(String kind) {
		super(Component.translatable("ending.matriochka." + kind));
		this.kind = kind;
	}

	/** The endings' theme plays over the crawl and the credits, in place of any world's music. */
	@Override
	public net.minecraft.sounds.Music getBackgroundMusic() {
		return MusicThemes.ENDINGS;
	}

	private int left() { return (width - BW) / 2; }
	private int top() { return Math.max(0, (height - BH) / 2); }
	private int textW() { return BW - 120; }

	@Override
	protected void init() {
		if (Ui.now() - opened < 100) {
			Ui.sound(SoundEvents.BOOK_PAGE_TURN, 0.6f, 1f);
			Ui.sound(SoundEvents.AMETHYST_BLOCK_RESONATE, 0.5f, 0.8f);
		}
		lines.clear();
		int y = 0;
		Language lang = Language.getInstance();
		for (int i = 0; lang.has("ending.matriochka." + kind + "." + i); i++) {
			y = add(Component.translatable("ending.matriochka." + kind + "." + i), Ui.INK, y) + 10;
		}
		y += 8;
		y = add(Component.translatable("ending.matriochka." + kind + ".lasting"), Ui.RED_INK, y) + 28;
		for (int i = 0; lang.has("ending.matriochka.credits." + i); i++) {
			y = add(Component.translatable("ending.matriochka.credits." + i), i == 0 ? Ui.RED_INK : Ui.INK_SOFT, y) + (i == 0 ? 6 : 4);
		}
		contentH = y;
	}

	private int add(Component c, int color, int y) {
		for (FormattedCharSequence s : font.split(c, textW())) {
			lines.add(new Line(s, color, y));
			y += 10;
		}
		return y;
	}

	private float unroll() {
		return Ui.easeOut(Ui.since(opened + 100, UNROLL_MS));
	}

	private float seconds() {
		return Math.max(0, (Ui.now() - opened - UNROLL_MS - 600) / 1000f);
	}

	/** True once every line has risen out of the page. */
	private boolean over() {
		return seconds() * SPEED > contentH + windowH();
	}

	private int windowY() { return top() + 44; }
	private int windowH() { return 116; }

	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top();
		// the cinematic frame: the screen darkens at its edges, letterbox bars slide in and lift once the credits are over
		if (Comfort.cinematics()) {
			float bars = Ui.easeOut(Ui.since(opened, 1200));
			if (over()) bars *= 1 - Ui.easeIn(Math.min(1, (seconds() * SPEED - contentH - windowH()) / 40f));
			Cinematics.edgeGlow(g, width, height, 0xFF0A0604, 0.8f * bars);
			Cinematics.letterbox(g, width, height, bars * 0.8f);
		}
		int by = Math.round(t + 4 + (BH - 15) * unroll());
		g.enableScissor(l, t + 4, l + BW, by + 7);
		Ui.sprite(g, "scroll_paper", l + 30, t + 8, 280, 198);
		g.disableScissor();
		g.fillGradient(l + 30, by - 6, l + 310, by + 4, 0x00000000, 0x55301808);
		Ui.sprite(g, "scroll_rod", l + 12, t - 3, 316, 14);
		Ui.sprite(g, "scroll_rod", l + 12, by, 316, 14);
		Ui.wanderingGlint(g, new int[][]{{l + 18, t + 4}, {l + 322, t + 4}, {l + 18, by + 7}, {l + 322, by + 7}}, 1900, 3);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		if (unroll() < 0.98f) return;
		int l = left(), t = top(), cx = l + BW / 2;
		float in = Ui.easeOut(Ui.since(opened + UNROLL_MS, 500));
		boolean blank = kind.equals("tools") && over();
		// the title cartouche, gone from the last Scroll of the third ending, which is left blank
		if (!blank) {
			int world = switch (kind) { case "seal" -> 10; case "absorb" -> 5; default -> 0; };
			Ui.plate(g, font, getTitle(), cx, t + 20, world, opened);
		}
		// the crawl: lines rise from the bottom of the window and fade at both edges
		float scroll = seconds() * SPEED;
		int wy = windowY(), wh = windowH();
		g.enableScissor(l + 40, wy, l + BW - 40, wy + wh);
		for (Line line : lines) {
			float y = wy + wh - scroll + line.y();
			if (y < wy - 10 || y > wy + wh) continue;
			float edge = Math.min(Math.min(1, (y - wy) / 22f), Math.min(1, (wy + wh - y - 8) / 22f));
			int col = Ui.alpha(line.color(), Math.max(0, edge) * in);
			if (((col >>> 24) & 0xFF) < 8) continue;
			g.text(font, line.text(), cx - font.width(line.text()) / 2, Math.round(y), col, false);
		}
		g.disableScissor();
		// the dolls at the foot of the page
		dolls(g, cx, t + 186);
		if (over()) {
			Component close = Component.translatable("ending.matriochka.close");
			float pulse = 0.55f + 0.35f * (float) Math.sin(Ui.now() / 500.0);
			g.text(font, close, cx - font.width(close) / 2, t + BH - 4, Ui.alpha(Ui.LIGHT, pulse), false);
		}
	}

	private void dolls(GuiGraphicsExtractor g, int cx, int base) {
		int[] w = {28, 22, 17, 13, 10}, h = {42, 33, 26, 20, 15};
		float s = seconds();
		int shown = switch (kind) {
			// Sealed: the dolls close one inside the other until one remains
			case "seal" -> Math.max(1, 5 - (int) (s / 6));
			// Set Down the Tools: they open one by one, then none is left
			case "tools" -> over() ? 0 : Math.min(5, 1 + (int) (s / 5));
			default -> 5;
		};
		int total = 0;
		for (int i = 0; i < shown; i++) total += w[i] + 3;
		int x = cx - total / 2;
		for (int i = 0; i < shown; i++) {
			int tint = kind.equals("absorb") ? 0xFF8A5A7A : 0xFFFFFFFF;
			float bob = (float) Math.sin(Ui.now() / 700.0 + i * 0.9) * 0.6f;
			g.pose().pushMatrix();
			g.pose().translate(0, bob);
			Ui.sprite(g, "nest_" + i, x, base - h[i], w[i], h[i], tint);
			g.pose().popMatrix();
			Ui.glint(g, x + w[i] * 0.3f, base - h[i] * 0.62f, Math.floorMod(Ui.now() + i * 900L, 4500L) / 700f, 6);
			x += w[i] + 3;
		}
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}
}
