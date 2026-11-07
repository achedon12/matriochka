package fr.achedon12.matriochka.client;

import net.minecraft.client.gui.GuiGraphicsExtractor;

/**
 * The live instrument in each station's niche, over its painted face (gauge_<station>): the foundry's thermometer
 * needle, the forge's capacitor cells, the dark altar's eye, the workshop's clock hand, the anchor's seismograph...
 * Every station reads its own state differently, so each has its own instrument instead of one shared vessel.
 * <p>
 * The face is 48 x 56 at (x, y). `fill` is the station's condition 0..1 (as the old vessel showed it), `ready`
 * whether it works right now, `value` the raw reading where it has one.
 */
final class StationInstruments {
	private StationInstruments() {}

	static final int W = 48, H = 56;

	static boolean has(String station) {
		return switch (station) {
			case "soul_altar", "class_table", "inverter" -> false;
			default -> true;
		};
	}

	static void draw(GuiGraphicsExtractor g, String station, int world, int x, int y, float fill, boolean ready, int value, float craftable, long dayTime) {
		Ui.sprite(g, "gauge_" + station, x, y, W, H);
		long t = Ui.now();
		int glow = Ui.worldColor(world);
		switch (station) {
			case "matrix_workbench" -> {
				// one socket lights for each recipe the player can make right now (of nine)
				int lit = Math.round(craftable * 9);
				for (int k = 0; k < 9; k++) {
					int cx = x + 9 + (k % 3) * 15, cy = y + 13 + (k / 3) * 15;
					boolean on = k < lit;
					float pulse = on ? 0.7f + 0.3f * (float) Math.sin(t / 400.0 + k) : 0.15f;
					g.fill(cx - 2, cy - 2, cx + 3, cy + 3, Ui.alpha(0xFFF4D27A, pulse));
				}
			}
			case "spore_vat" -> {
				// the brew level in the porthole, its colour deepening from fresh to aged
				int stage = value >= 300 ? 2 : value >= 60 ? 1 : 0;
				int px = x + 26, py = y + 26, r = 14;
				float lvl = 0.35f + 0.6f * Math.min(1f, value / 300f);
				int col = stage == 2 ? 0xFF8AD020 : stage == 1 ? 0xFFB4E04A : 0xFFD8F098;
				int top = py + r - Math.round(2 * r * lvl);
				for (int yy = top; yy <= py + r; yy++) {
					int half = (int) Math.sqrt(Math.max(0, r * r - (yy - py) * (yy - py)));
					g.fill(px - half, yy, px + half, yy + 1, Ui.alpha(col, 0.85f));
				}
				for (int b = 0; b < 3; b++) {
					float p = Math.floorMod(t + b * 700L, 2100L) / 2100f;
					int by = Math.round(py + r - 2 - p * (py + r - top));
					if (by > top) g.fill(px - 6 + b * 6, by, px - 4 + b * 6, by + 2, Ui.white(0.7f * (1 - p)));
				}
				// the mark the brew has reached
				int[] marks = {y + 40, y + 28, y + 16};
				g.fill(x + 1, marks[stage], x + 7, marks[stage] + 2, 0xFFFFFFFF);
			}
			case "ash_foundry" -> {
				// the needle over the dial: heat sources 0..6, the green band 1..3
				float heat = Math.min(6, value) / 6f;
				double a = Math.PI + heat * Math.PI + Math.sin(t / 160.0) * 0.03;
				needle(g, x + 24, y + 28, a, 17, ready ? 0xFFF4F0E0 : 0xFFF08060);
				g.fill(x + 22, y + 26, x + 27, y + 31, 0xFF3A3A44);
				int bars = Math.min(6, value);
				for (int k = 0; k < 6; k++) g.fill(x + 9 + k * 5, y + 41, x + 12 + k * 5, y + 48, k < bars ? (k >= 3 ? 0xFFE04020 : 0xFF60C040) : 0x40FFFFFF);
			}
			case "jailer_table" -> {
				// the three tumblers: each one set lights its window
				for (int k = 0; k < 3; k++) {
					boolean ok = k < value;
					g.fill(x + 7 + k * 13, y + 34, x + 15 + k * 13, y + 43, ok ? 0xFF80D060 : 0x30FFFFFF);
				}
				if (ready) Ui.glint(g, x + 24, y + 18, Math.floorMod(t, 1800L) / 800f, 6);
			}
			case "lightning_forge" -> {
				// eight cells fill with the stored charge, the top one flickers
				for (int k = 0; k < 8; k++) {
					int cx = x + 4 + (k % 4) * 10 + 1, cy = y + 12 + (k / 4) * 21 + 1;
					boolean on = k < value;
					float f = on ? (k == value - 1 ? 0.6f + 0.4f * (float) Math.abs(Math.sin(t / 90.0)) : 1f) : 0f;
					if (on) g.fill(cx, cy, cx + 7, cy + 16, Ui.alpha(0xFFFFE14A, f));
					else g.fill(cx, cy + 14, cx + 7, cy + 16, 0x60406080);
				}
			}
			case "dark_altar" -> {
				// an eye in the roundel: shut while any light reaches the altar, open in full darkness
				int cx = x + 24, cy = y + 26;
				float open = ready ? 0.8f + 0.2f * (float) Math.sin(t / 700.0) : 0.08f;
				for (int k = -13; k <= 13; k++) {
					int h = Math.round(7 * open * (1 - (k / 13.5f) * (k / 13.5f)));
					if (h > 0) g.fill(cx + k, cy - h, cx + k + 1, cy + h, 0xFFE8E0FF);
					else g.fill(cx + k, cy, cx + k + 1, cy + 1, 0xFF8070C0);
				}
				if (ready) {
					int look = Math.round((float) Math.sin(t / 1300.0) * 4);
					g.fill(cx - 3 + look, cy - 3, cx + 4 + look, cy + 4, Ui.alpha(glow, 1f));
					g.fill(cx - 1 + look, cy - 1, cx + 2 + look, cy + 2, 0xFF000000);
				}
			}
			case "abyssal_press" -> {
				// the dial reads the depth, the column fills with water once deep enough
				double a = Math.PI * 0.75 + (ready ? 0.85 + 0.03 * Math.sin(t / 300.0) : 0.12) * Math.PI * 1.5;
				needle(g, x + 24, y + 17, a, 10, 0xFFC02020);
				int ch = ready ? 18 : 4;
				g.fill(x + 17, y + 52 - ch, x + 31, y + 52, 0xFF3AB8D0);
				if (ready) for (int b = 0; b < 2; b++) {
					float p = Math.floorMod(t + b * 900L, 1800L) / 1800f;
					g.fill(x + 21 + b * 4, y + 50 - Math.round(p * 15), x + 23 + b * 4, y + 52 - Math.round(p * 15), Ui.white(0.6f * (1 - p)));
				}
			}
			case "time_workshop" -> {
				// one hand turns once a day; the workshop works while it points into a gold window
				double a = -Math.PI / 2 + ((dayTime + 6000) % 24000) / 24000.0 * Math.PI * 2;
				needle(g, x + 24, y + 28, a, 16, ready ? 0xFFE09030 : 0xFF2A1A10);
				g.fill(x + 22, y + 26, x + 27, y + 31, 0xFFC09040);
			}
			case "terrain_anchor" -> {
				// the seismograph pen: a calm line while the anchor holds, tremors otherwise
				int x0 = x + 5, x1 = x + 43, mid = y + 28;
				int prev = mid;
				for (int px = x0; px < x1; px++) {
					double k = (px - x0 + t / 40.0) / 3.0;
					double amp = ready ? 1.0 : 7.0;
					int yy = mid + (int) Math.round(Math.sin(k) * amp * 0.6 + Math.sin(k * 2.7 + 1) * amp * 0.4);
					g.fill(px, Math.min(prev, yy), px + 1, Math.max(prev, yy) + 1, 0xFF8A2A1A);
					prev = yy;
				}
			}
			case "final_loom" -> {
				// the shuttle runs across the ten threads; threads light as you gather the recipe's materials
				int lit = Math.round(craftable * 10);
				for (int k = 0; k < 10; k++) {
					int tx = x + 6 + (k * 7) / 2;
					if (k < lit) g.fill(tx, y + 6, tx + 2, y + 50, Ui.white(0.35f + 0.15f * (float) Math.sin(t / 500.0 + k)));
				}
				float s = (float) Math.sin(t / 600.0);
				int sx = x + 20 + Math.round(s * 15);
				g.fill(sx, y + 25, sx + 10, y + 30, 0xFF5A3018);
				g.fill(sx + 2, y + 26, sx + 8, y + 29, 0xFFE0B060);
			}
			default -> {}
		}
	}

	/** A needle from (cx, cy) at angle a (radians, screen space), drawn pixel by pixel. */
	private static void needle(GuiGraphicsExtractor g, int cx, int cy, double a, int len, int color) {
		for (int i = 0; i <= len; i++) {
			int px = cx + (int) Math.round(Math.cos(a) * i), py = cy + (int) Math.round(Math.sin(a) * i);
			g.fill(px, py, px + 1 + (i < len / 2 ? 1 : 0), py + 1 + (i < len / 2 ? 1 : 0), color);
		}
	}
}
