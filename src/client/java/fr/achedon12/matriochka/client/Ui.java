package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BooleanSupplier;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.Holder;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Util;

/**
 * Matryoshka folk-art kit. Every sprite is painted by tools/gui.py at twice its GUI size: lacquer over wood, gold
 * leaf, khokhloma vines, parchment, satin ribbons, dolls and lanterns. This class holds the drawing helpers, the
 * easing used by every transition, the UI sounds and the lacquer buttons.
 */
public final class Ui {
	public static final int INK = 0xFF3A2416, INK_SOFT = 0xFF6E4E36, GOLD = 0xFFEFCB72, GOLD_DARK = 0xFF96682A,
		PAPER_TEXT = 0xFF3A2416, LIGHT = 0xFFF6E8CC, RED = 0xFFB3261E, RED_INK = 0xFF9A2418, GREEN = 0xFF3F6E2C,
		MUTED = 0xFFC8B494, SHADOW = 0xFF140A06, OK = 0xFFA8E07A, WARN = 0xFFF08A6A;

	private Ui() {}

	// ------------------------------------------------------------------ time and easing
	public static long now() {
		return Util.getMillis();
	}

	public static float clamp01(float v) {
		return v < 0 ? 0 : v > 1 ? 1 : v;
	}

	/** Fraction of a span of ms elapsed since start, clamped to [0, 1]. */
	public static float since(long start, float ms) {
		return clamp01((now() - start) / ms);
	}

	public static float easeOut(float t) {
		t = clamp01(t);
		float u = 1 - t;
		return 1 - u * u * u;
	}

	public static float easeIn(float t) {
		t = clamp01(t);
		return t * t * t;
	}

	public static float easeInOut(float t) {
		t = clamp01(t);
		return t < 0.5f ? 4 * t * t * t : 1 - (float) Math.pow(-2 * t + 2, 3) / 2;
	}

	/** Ease out with a small overshoot, for things that settle into place. */
	public static float easeBack(float t) {
		t = clamp01(t);
		float c1 = 1.4f, c3 = c1 + 1;
		float u = t - 1;
		return 1 + c3 * u * u * u + c1 * u * u;
	}

	/** Frame-rate independent approach of a value toward its target (rate: fraction per second). */
	public static float approach(float value, float target, float rate, float dtSeconds) {
		return target + (value - target) * (float) Math.exp(-rate * dtSeconds);
	}

	public static int alpha(int argb, float a) {
		int al = Math.round(((argb >>> 24) & 0xFF) * clamp01(a));
		return (al << 24) | (argb & 0xFFFFFF);
	}

	public static int white(float a) {
		return alpha(0xFFFFFFFF, a);
	}

	// ------------------------------------------------------------------ sounds
	public static void sound(SoundEvent e, float pitch, float volume) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(e, pitch, volume));
	}

	public static void sound(Holder<SoundEvent> e, float pitch) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(e, pitch));
	}

	public static void click() {
		sound(SoundEvents.UI_BUTTON_CLICK, 1.1f);
	}

	public static void pageTurn() {
		sound(SoundEvents.BOOK_PAGE_TURN, 0.9f + (float) Math.random() * 0.2f, 1f);
	}

	// ------------------------------------------------------------------ sprites
	public static void sprite(GuiGraphicsExtractor g, String name, int x, int y, int w, int h) {
		g.blitSprite(RenderPipelines.GUI_TEXTURED, Matriochka.id(name), x, y, w, h);
	}

	public static void sprite(GuiGraphicsExtractor g, String name, int x, int y, int w, int h, int color) {
		g.blitSprite(RenderPipelines.GUI_TEXTURED, Matriochka.id(name), x, y, w, h, color);
	}

	/** Draws the part [u, u+w) x [v, v+h) of a stretched sprite of logical size texW x texH. */
	public static void spritePart(GuiGraphicsExtractor g, String name, int texW, int texH, int u, int v, int x, int y, int w, int h, int color) {
		if (w <= 0 || h <= 0) return;
		g.blitSprite(RenderPipelines.GUI_TEXTURED, Matriochka.id(name), texW, texH, u, v, x, y, w, h, color);
	}

	public static void frame(GuiGraphicsExtractor g, int x, int y, int w, int h) {
		sprite(g, "frame", x, y, w, h);
	}

	public static void paper(GuiGraphicsExtractor g, int x, int y, int w, int h) {
		sprite(g, "paper", x, y, w, h);
	}

	/** Text with a one-pixel dark drop, for gold or light lettering on lacquer. */
	public static void embossed(GuiGraphicsExtractor g, Font font, Component text, int x, int y, int color) {
		g.text(font, text, x + 1, y + 1, alpha(SHADOW, ((color >>> 24) & 0xFF) / 255f * 0.9f), false);
		g.text(font, text, x, y, color, false);
	}

	/** A title in the lacquer band, centred, scaled 1.25x with a gold drop. */
	public static void title(GuiGraphicsExtractor g, Font font, Component text, int cx, int y) {
		g.pose().pushMatrix();
		g.pose().translate(cx, y);
		g.pose().scale(1.25f, 1.25f);
		int w = font.width(text);
		g.text(font, text, -w / 2 + 1, 1, SHADOW, false);
		g.text(font, text, -w / 2, 0, GOLD, false);
		g.pose().popMatrix();
	}

	/**
	 * A gilded title cartouche in a world's enamel, sized to the text, with a sheen that crosses it every few
	 * seconds. Returns the plate's width.
	 */
	public static int plate(GuiGraphicsExtractor g, Font font, Component text, int cx, int y, int world, long phase) {
		int w = font.width(text) + 34;
		int x = cx - w / 2;
		sprite(g, "plate_" + Math.max(0, Math.min(10, world)), x, y, w, 16);
		sheen(g, x + 6, y + 3, w - 12, 10, 4200, phase, 0.8f);
		embossed(g, font, text, cx - font.width(text) / 2, y + 4, GOLD);
		return w;
	}

	/** A soft band of light sweeping across a rectangle once per period, clipped to it. */
	public static void sheen(GuiGraphicsExtractor g, int x, int y, int w, int h, int period, long phase, float strength) {
		long t = Math.floorMod(now() + phase, period);
		float p = t / 900f;
		if (p > 1) return;
		int sw = 20 + h;
		int sx = x - sw + Math.round(easeInOut(p) * (w + sw));
		g.enableScissor(x, y, x + w, y + h);
		sprite(g, "sheen", sx, y - 1, sw, h + 2, white(strength * (float) Math.sin(Math.PI * p)));
		g.disableScissor();
	}

	/** A four-pointed glint that swells and fades; t in [0, 1]. */
	public static void glint(GuiGraphicsExtractor g, float cx, float cy, float t, float size) {
		if (t <= 0 || t >= 1) return;
		float s = size * (float) Math.sin(Math.PI * t);
		if (s < 1) return;
		g.pose().pushMatrix();
		g.pose().translate(cx, cy);
		g.pose().rotate((float) (t * Math.PI * 0.5));
		g.pose().scale(s / 9f, s / 9f);
		sprite(g, "glint", -5, -5, 9, 9, white(0.95f));
		g.pose().popMatrix();
	}

	/**
	 * A glint that wanders between the given points, one every period ms: gentle idle life for gold rims.
	 */
	public static void wanderingGlint(GuiGraphicsExtractor g, int[][] points, int period, long seed) {
		long t = now() + seed;
		int idx = (int) Math.floorMod((t / period) * 7 + seed, (long) points.length);
		float p = Math.floorMod(t, period) / (float) period;
		glint(g, points[idx][0], points[idx][1], p * 1.6f, 9);
	}

	/**
	 * A glass vial lying on its side: dark glass, a tinted liquid that fills from the left with a bright meniscus,
	 * glass highlights on top, and a flash after the value changes.
	 */
	public static void vial(GuiGraphicsExtractor g, int x, int y, int w, int h, float frac, int color, float flash) {
		sprite(g, "vial_back", x, y, w, h);
		int ix = x + 5, iw = w - 10, iy = y + 2, ih = h - 4;
		int fw = Math.round(iw * clamp01(frac));
		if (fw > 0) {
			spritePart(g, "vial_liquid", iw, ih, 0, 0, ix, iy, fw, ih, color);
			float wob = (float) Math.sin(now() / 260.0) * 0.5f + 0.5f;
			g.fill(ix + fw - 1, iy, ix + fw, iy + ih, white(0.45f + 0.3f * wob));
			if (flash > 0) g.fill(ix, iy, ix + fw, iy + ih, white(0.55f * flash));
		}
		for (int k = 1; k < 4; k++) g.fill(ix + iw * k / 4, iy + ih - 2, ix + iw * k / 4 + 1, iy + ih, alpha(0xFFE8C060, 0.7f));
		sprite(g, "vial_front", x, y, w, h);
	}

	/** Kept for callers that want a plain groove gauge: draws a vial. */
	public static void gauge(GuiGraphicsExtractor g, int x, int y, int w, int h, float frac, int color) {
		vial(g, x, y - 1, w, Math.max(9, h + 2), frac, color, 0);
	}

	/** The station's world, or 0 for the surface stations. */
	public static int stationWorld(String station) {
		return switch (station) {
			case "spore_vat" -> 1; case "ash_foundry" -> 2; case "jailer_table" -> 3; case "lightning_forge" -> 4;
			case "dark_altar" -> 5; case "inverter" -> 6; case "abyssal_press" -> 7; case "time_workshop" -> 8;
			case "terrain_anchor" -> 9; case "final_loom" -> 10;
			default -> 0;
		};
	}

	public static int worldColor(int world) {
		return switch (world) {
			case 1 -> 0xFF96D63C; case 2 -> 0xFFFF8C28; case 3 -> 0xFF7FD3FF; case 4 -> 0xFFFFE14A; case 5 -> 0xFF6A8AFF;
			case 6 -> 0xFFC84AD8; case 7 -> 0xFF3CC8D2; case 8 -> 0xFFE88C32; case 9 -> 0xFFE8A070; case 10 -> 0xFFE8C070;
			default -> 0xFFDE3422;
		};
	}

	// ------------------------------------------------------------------ open / close motion
	/** The open and close transition shared by every screen: the panel rises and settles, then sinks away. */
	public static final class Motion {
		private final long opened = now();
		private final int openMs, closeMs;
		private long closing = -1;
		private Runnable done;

		public Motion(int openMs, int closeMs) {
			this.openMs = openMs;
			this.closeMs = closeMs;
		}

		public float open() {
			return since(opened, openMs);
		}

		public boolean closing() {
			return closing >= 0;
		}

		public long openedAt() {
			return opened;
		}

		public long closedAt() {
			return closing;
		}

		/** Starts closing; done runs from tick() once the panel has gone. */
		public void close(Runnable done) {
			if (closing < 0) {
				closing = now();
				this.done = done;
			}
		}

		public void tick() {
			if (closing >= 0 && done != null && now() - closing >= closeMs) {
				Runnable r = done;
				done = null;
				r.run();
			}
		}

		/** 0 when hidden, 1 when fully shown. */
		public float shown() {
			float v = easeBack(open());
			if (closing >= 0) v *= 1 - easeIn(since(closing, closeMs));
			return v;
		}

		public void push(GuiGraphicsExtractor g, float cx, float cy) {
			float v = shown();
			float s = 0.86f + 0.14f * v;
			g.pose().pushMatrix();
			g.pose().translate(cx, cy + (1 - Math.min(1, v)) * 14);
			g.pose().scale(s, s);
			g.pose().translate(-cx, -cy);
		}

		public void pop(GuiGraphicsExtractor g) {
			g.pose().popMatrix();
		}
	}

	// ------------------------------------------------------------------ buttons
	/** Self-drawn lacquer buttons with hover, pressed and disabled states, so the whole interface shares one material. */
	public static final class Buttons {
		private static final class B {
			final int x, y, w, h;
			final Component label;
			final Runnable action;
			final BooleanSupplier enabled;
			float hover;
			long pressed = -1;

			B(int x, int y, int w, int h, Component label, Runnable action, BooleanSupplier enabled) {
				this.x = x;
				this.y = y;
				this.w = w;
				this.h = h;
				this.label = label;
				this.action = action;
				this.enabled = enabled;
			}
		}

		private final List<B> list = new ArrayList<>();
		private long last = now();

		public void clear() {
			list.clear();
		}

		public void add(int x, int y, int w, int h, Component label, Runnable action) {
			list.add(new B(x, y, w, h, label, action, () -> true));
		}

		public void add(int x, int y, int w, int h, Component label, Runnable action, BooleanSupplier enabled) {
			list.add(new B(x, y, w, h, label, action, enabled));
		}

		public void draw(GuiGraphicsExtractor g, Font font, int mx, int my) {
			long t = now();
			float dt = Math.min(0.1f, (t - last) / 1000f);
			last = t;
			for (B b : list) {
				boolean on = b.enabled.getAsBoolean();
				boolean over = on && mx >= b.x && mx < b.x + b.w && my >= b.y && my < b.y + b.h;
				b.hover = approach(b.hover, over ? 1 : 0, 18, dt);
				boolean down = b.pressed >= 0 && t - b.pressed < 140;
				String sprite = !on ? "btn_off" : down ? "btn_pressed" : "btn";
				sprite(g, sprite, b.x, b.y, b.w, b.h);
				if (on && !down && b.hover > 0.01f) sprite(g, "btn_hover", b.x, b.y, b.w, b.h, white(b.hover));
				if (on && b.hover > 0.5f && !down) sheen(g, b.x + 3, b.y + 2, b.w - 6, b.h - 4, 1600, b.x * 31L, 0.5f);
				int tw = font.width(b.label);
				int ty = b.y + (b.h - 8) / 2 + (down ? 1 : 0);
				int col = on ? (b.hover > 0.5f ? 0xFFFFF4D8 : LIGHT) : 0xFF8A7A70;
				if (tw > b.w - 6) {
					// a longer label (other languages) shrinks to fit its button
					float sc = (b.w - 6f) / tw;
					g.pose().pushMatrix();
					g.pose().translate(b.x + b.w / 2f, ty + 4);
					g.pose().scale(sc, sc);
					embossed(g, font, b.label, -tw / 2, -4, col);
					g.pose().popMatrix();
				} else embossed(g, font, b.label, b.x + (b.w - tw) / 2, ty, col);
			}
		}

		public boolean click(double mx, double my) {
			for (B b : list) {
				if (b.enabled.getAsBoolean() && mx >= b.x && mx < b.x + b.w && my >= b.y && my < b.y + b.h) {
					b.pressed = now();
					Ui.click();
					b.action.run();
					return true;
				}
			}
			return false;
		}
	}
}
