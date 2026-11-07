package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.mixin.client.BossHealthOverlayAccess;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.BossHealthOverlay;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;

/**
 * The bosses' own health bars, in place of vanilla's: every boss has a bar of its own design (sprites by
 * tools/bossbars.py), its housing drawn for what it is and the world it rules, its head set in a socket of its own
 * shape, its name on its own plate, and a gauge of its own matter, animated here:
 * <ul>
 * <li>Block Guardian: mossy stone blocks filling one by one; Spore Queen: a bubbling toxic sludge;</li>
 * <li>Ash Titan: molten metal flowing under a bright crust; Grand Jailer: blue soul fire licking behind bars;</li>
 * <li>Storm King: lightning arcing along an electric charge; Light Eater: a violet dark that swallows motes;</li>
 * <li>Your Double: a mirrored gauge that empties from both ends at once; Pressure Leviathan: deep water;</li>
 * <li>Seasons Master: the four seasons along its quarters; Terrain Heart: a heartbeat running through red veins;</li>
 * <li>The Unfinished: red lacquer and gold over pencil hatching, ten shells.</li>
 * </ul>
 * The damage just taken lingers as a pale trail, the head flinches and flashes when hit, and the boss's phases
 * are marked on the gauge. Other mods' and vanilla's bars keep their look and are stacked under these; the bars
 * keep clear of the first-steps card and the world plaque.
 */
public final class BossBars {
	private BossBars() {}

	/** The bar's size, and its two windows: the head's socket and the gauge (tools/bossbars.py). */
	private static final int W = 240, H = 40, STEP = H + 3;
	/** The gauge's window, and the centres of the two sculpted ends. */
	private static final int TX = 24, TY = 17, TW = 192, TH = 10, LEFT = 12, RIGHT = 228;
	private static final Map<UUID, Float> TRAIL = new HashMap<>();
	private static final Map<UUID, Long> HIT = new HashMap<>();
	private static long last = Ui.now();

	/** The Matriochka boss a bar belongs to, read from its name (entity.matriochka.<id>), or null. */
	static Defs.BossDef bossOf(Component name) {
		if (name == null) return null;
		if (name.getContents() instanceof TranslatableContents tc) {
			String key = tc.getKey();
			if (key.startsWith("entity.matriochka.")) {
				String id = key.substring("entity.matriochka.".length());
				for (Defs.BossDef b : Content.BOSSES) if (b.id().equals(id)) return b;
			}
			for (Object a : tc.getArgs()) if (a instanceof Component c) {
				Defs.BossDef b = bossOf(c);
				if (b != null) return b;
			}
		}
		for (Component s : name.getSiblings()) {
			Defs.BossDef b = bossOf(s);
			if (b != null) return b;
		}
		return null;
	}

	/** Draws every bar when one of them is a Matriochka boss's; false leaves the drawing to vanilla. */
	public static boolean draw(BossHealthOverlay overlay, GuiGraphicsExtractor g) {
		Map<UUID, LerpingBossEvent> events = ((BossHealthOverlayAccess) overlay).matriochka$events();
		if (events.isEmpty()) return false;
		boolean ours = false;
		for (LerpingBossEvent e : events.values()) ours |= bossOf(e.getName()) != null;
		if (!ours) return false;
		Font font = Minecraft.getInstance().font;
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		int cx = g.guiWidth() / 2, y = 4;
		// keep clear of what stands in the top corners: slide the bars aside, or under it on a narrow screen
		int left = 0, right = g.guiWidth(), below = 0;
		for (int[] r : obstacles(g)) {
			if (r[1] > y + H) continue;
			if (r[2] <= cx) left = Math.max(left, r[2] + 4);
			else if (r[0] >= cx) right = Math.min(right, r[0] - 4);
			below = Math.max(below, r[3] + 4);
		}
		if (right - left >= W) cx = Math.max(left + W / 2, Math.min(cx, right - W / 2));
		else y = below;
		for (LerpingBossEvent e : events.values()) {
			Defs.BossDef d = bossOf(e.getName());
			if (d != null) {
				bar(g, font, e, d, cx - W / 2, y, dt, now);
				y += STEP;
			} else {
				g.centeredText(font, e.getName(), cx, y, 0xFFFFFFFF);
				((BossHealthOverlayAccess) overlay).matriochka$extractBar(g, cx - 91, y + 9, e);
				y += 19;
			}
			if (y >= g.guiHeight() / 3) break;
		}
		TRAIL.keySet().retainAll(events.keySet());
		HIT.keySet().retainAll(events.keySet());
		return true;
	}

	/** Rectangles drawn in the top of the screen this frame that the bars must not cover. */
	private static java.util.List<int[]> obstacles(GuiGraphicsExtractor g) {
		java.util.List<int[]> out = new java.util.ArrayList<>();
		if (Ui.now() - TutorialCard.drawnAt < 250) out.add(TutorialCard.drawn);
		if (Hud.plaqueBottom > 0 && Hud.plaqueTop < g.guiHeight() / 2) out.add(new int[]{Hud.plaqueX, Hud.plaqueTop, Hud.plaqueRight, Hud.plaqueBottom});
		return out;
	}

	private static void bar(GuiGraphicsExtractor g, Font font, LerpingBossEvent e, Defs.BossDef d, int x, int y, float dt, long now) {
		float p = Ui.clamp01(e.getProgress());
		float t = TRAIL.getOrDefault(e.getId(), p);
		// a hit: the health dropped since the last frame
		if (p < lastP(e) - 0.002f) HIT.put(e.getId(), now);
		// the trail of the damage just taken waits a moment, then melts down to the health
		t = p > t ? p : Math.max(p, t - dt * 0.2f);
		TRAIL.put(e.getId(), t);
		LAST_P.put(e.getId(), p);
		long hitAt = HIT.getOrDefault(e.getId(), -1L);
		float hit = hitAt < 0 ? 0 : 1 - Ui.since(hitAt, 380);
		if (hit <= 0) HIT.remove(e.getId());
		String id = d.id();
		Style st = style(id);

		// the gauge: its empty ground, the trail, then the boss's own matter
		int x0 = x + TX, y0 = y + TY;
		empty(g, st, x0, y0, now);
		boolean mirror = st == Style.MIRROR;
		int fill = Math.round(TW * p), trail = Math.round(TW * t);
		if (mirror) {
			int mid = x0 + TW / 2;
			if (trail > fill) g.fill(mid - trail / 2, y0, mid + trail / 2, y0 + TH, Ui.alpha(0xFFFFF4F8, 0.75f));
		} else if (trail > fill) g.fill(x0 + fill, y0, x0 + trail, y0 + TH, Ui.alpha(0xFFFFF4E0, 0.7f));
		if (fill > 0) matter(g, st, x0, y0, fill, now, p, id.hashCode());
		// low on health, the matter pulses
		if (p < 0.25f && fill > 0) {
			int a = mirror ? x0 + TW / 2 - fill / 2 : x0, b = mirror ? a + fill : x0 + fill;
			g.fill(a, y0, b, y0 + TH, Ui.alpha(0xFFFFFFFF, 0.14f * (0.5f + 0.5f * (float) Math.sin(now / 150.0))));
		}
		// the boss's shells: a notch at every phase, dimmed once passed
		for (float th : d.phases()) {
			int rx = mirror ? x0 + TW / 2 + Math.round(TW * th / 2) : x0 + Math.round(TW * th);
			notch(g, rx, y0, p < th, st.accent);
			if (mirror) notch(g, x0 + TW / 2 - Math.round(TW * th / 2), y0, p < th, st.accent);
		}

		// the life round the bar, behind the housing
		ambient(g, st, x, y, now, false);
		// the housing over it all, its ends alive
		Ui.sprite(g, "bossbar_frame_" + id, x, y, W, H);
		emblems(g, st, x, y, now, hit, p);
		ambient(g, st, x, y, now, true);

		// the name on its plate, over the top of the housing, an ornament of the boss on each side
		Component name = e.getName();
		int nw = font.width(name) + 22, nx = x0 + TW / 2 - nw / 2, ny = y + 2;
		Ui.sprite(g, "bossbar_plate_" + id, nx, ny, nw, 16);
		Ui.sprite(g, "bossbar_cap_" + id, nx - 10, ny, 12, 16);
		Ui.sprite(g, "bossbar_cap_" + id + "_r", nx + nw - 2, ny, 12, 16);
		boolean light = st == Style.SEASONS || st == Style.LACQUER;
		g.text(font, name, nx + 12, ny + 5, light ? Ui.alpha(0xFFFFFFFF, 0.35f) : Ui.alpha(0xFF000000, 0.55f), false);
		g.text(font, name, nx + 11, ny + 4, st.name, false);
		if (hit > 0) g.fill(nx + 2, ny + 2, nx + nw - 2, ny + 14, Ui.alpha(0xFFFFFFFF, 0.18f * hit));
	}

	private static final Map<UUID, Float> LAST_P = new HashMap<>();

	private static float lastP(LerpingBossEvent e) {
		return LAST_P.getOrDefault(e.getId(), e.getProgress());
	}

	// ---------------------------------------------------------------- the boss's matter
	/** The gauge's matter of each boss, its empty ground, its accent and the colours of its name and title. */
	enum Style {
		BLOCKS(0xFF14180F, 0xFF8FE3A0, 0xFFE8F0D8, 0xFFB8D8A8),
		SLUDGE(0xFF0E160A, 0xFFC8F06A, 0xFFE6F8B0, 0xFFC8E090),
		MOLTEN(0xFF120806, 0xFFFFC060, 0xFFFFD8A0, 0xFFF0B080),
		SOUL(0xFF080C16, 0xFF9AD8FF, 0xFFD8E4F4, 0xFFA8C0E0),
		STORM(0xFF0A1020, 0xFFFFE14A, 0xFFFFF0B0, 0xFFC8D4F0),
		VOID(0xFF040208, 0xFFB49AFF, 0xFFD8CCFF, 0xFFA898D8),
		MIRROR(0xFF1A1424, 0xFFFFFFFF, 0xFFFFF4FC, 0xFFF4D8F0),
		WATER(0xFF02101C, 0xFFD8F8FF, 0xFFF4E8C0, 0xFFA8DCEC),
		SEASONS(0xFF1C140A, 0xFFFFF4D8, 0xFF3A2410, 0xFFF0DCA8),
		PULSE(0xFF100404, 0xFFFF8070, 0xFFF8D0B8, 0xFFE8A090),
		LACQUER(0xFFE6D6B6, 0xFFE8BC62, 0xFF3A2A20, 0xFFF0D8A8);

		final int empty, accent, name, title;

		Style(int empty, int accent, int name, int title) {
			this.empty = empty;
			this.accent = accent;
			this.name = name;
			this.title = title;
		}
	}

	static Style style(String id) {
		return switch (id) {
			case "block_guardian" -> Style.BLOCKS;
			case "spore_queen" -> Style.SLUDGE;
			case "ash_titan" -> Style.MOLTEN;
			case "grand_jailer" -> Style.SOUL;
			case "storm_king" -> Style.STORM;
			case "light_eater" -> Style.VOID;
			case "your_double" -> Style.MIRROR;
			case "pressure_leviathan" -> Style.WATER;
			case "seasons_master" -> Style.SEASONS;
			case "terrain_heart_boss" -> Style.PULSE;
			default -> Style.LACQUER;
		};
	}

	private static int mix(int a, int b, float t) {
		t = Ui.clamp01(t);
		int ar = a >> 16 & 255, ag = a >> 8 & 255, ab = a & 255, br = b >> 16 & 255, bg = b >> 8 & 255, bb = b & 255;
		return 0xFF000000 | Math.round(ar + (br - ar) * t) << 16 | Math.round(ag + (bg - ag) * t) << 8 | Math.round(ab + (bb - ab) * t);
	}

	private static float hash(int i, int seed) {
		int n = i * 374761393 + seed * 668265263;
		n = (n ^ (n >>> 13)) * 1274126177;
		return ((n ^ (n >>> 16)) & 0xFFFFFF) / (float) 0xFFFFFF;
	}

	/** A notch on the gauge at one of the boss's phases. */
	private static void notch(GuiGraphicsExtractor g, int rx, int y0, boolean passed, int accent) {
		g.fill(rx - 1, y0, rx + 2, y0 + TH, Ui.alpha(0xFF000000, 0.55f));
		g.fill(rx, y0, rx + 1, y0 + TH, passed ? Ui.alpha(accent, 0.35f) : accent);
	}

	/** The empty part of the gauge: a dark ground, the bare wood and its pencil hatching for the Unfinished. */
	private static void empty(GuiGraphicsExtractor g, Style st, int x0, int y0, long now) {
		g.fill(x0, y0, x0 + TW, y0 + TH, st.empty);
		switch (st) {
			case LACQUER -> {
				for (int i = -TH; i < TW; i += 4)
					for (int k = 0; k < TH; k++) {
						int x = x0 + i + k;
						if (x >= x0 && x < x0 + TW) g.fill(x, y0 + TH - 1 - k, x + 1, y0 + TH - k, 0x30403020);
					}
			}
			case VOID -> {
				// motes of light drifting toward the dark, swallowed as they reach it
				for (int i = 0; i < 7; i++) {
					float ph = Math.floorMod(now + i * 911L, 2600) / 2600f;
					int mx = x0 + TW - 2 - Math.round(ph * TW * (0.4f + hash(i, 3) * 0.5f));
					int my = y0 + 2 + Math.round(hash(i, 5) * (TH - 4));
					g.fill(mx, my, mx + 1, my + 1, Ui.alpha(0xFFD8CCFF, 0.7f * (1 - ph)));
				}
			}
			default -> g.fill(x0, y0, x0 + TW, y0 + 1, Ui.alpha(0xFFFFFFFF, 0.05f));
		}
	}

	/**
	 * A light on an emblem, the way Minecraft lights things: no blur, a few hard pixels that come and go. The
	 * stronger it is, the more of them shine (a centre, then a cross, then its diagonals, then the outer ring).
	 */
	private static void glow(GuiGraphicsExtractor g, int cx, int cy, int r, int color, float a) {
		if (a < 0.3f) return;
		int c = color | 0xFF000000;
		g.fill(cx, cy, cx + 1, cy + 1, c);
		if (a > 0.5f) {
			g.fill(cx - 1, cy, cx + 2, cy + 1, c);
			g.fill(cx, cy - 1, cx + 1, cy + 2, c);
		}
		if (a > 0.75f) for (int[] d : new int[][]{{-1, -1}, {1, -1}, {-1, 1}, {1, 1}}) g.fill(cx + d[0], cy + d[1], cx + d[0] + 1, cy + d[1] + 1, Ui.alpha(c, 0.7f));
		if (a > 0.9f) {
			int k = Math.max(2, r / 4);
			for (int[] d : new int[][]{{-k, 0}, {k, 0}, {0, -k}, {0, k}}) g.fill(cx + d[0], cy + d[1], cx + d[0] + 1, cy + d[1] + 1, Ui.alpha(c, 0.6f));
		}
	}

	/** The ends of the bar come alive: what burns, beats, looks, turns or charges there. */
	private static void emblems(GuiGraphicsExtractor g, Style st, int x, int y, long now, float hit, float p) {
		int lx = x + LEFT, rx = x + RIGHT, cy = y + 21;
		float slow = 0.5f + 0.5f * (float) Math.sin(now / 600.0), fast = 0.5f + 0.5f * (float) Math.sin(now / 90.0);
		switch (st) {
			case BLOCKS -> {
				// the runes breathe
				glow(g, lx, y + 20, 8, 0xFF5AE6F0, 0.6f + 0.4f * slow);
				glow(g, rx, y + 20, 8, 0xFF5AE6F0, 0.6f + 0.4f * (1 - slow));
			}
			case SLUDGE -> {
				glow(g, lx, y + 24, 7, 0xFFAAF046, 0.5f + 0.5f * slow);
				glow(g, rx, y + 24, 7, 0xFFAAF046, 0.5f + 0.5f * slow);
			}
			case MOLTEN -> {
				// the furnace mouths flicker
				float f = 0.55f + 0.25f * fast + 0.2f * (float) Math.sin(now / 37.0);
				glow(g, lx, y + 24, 9, 0xFFFF8C1E, f);
				glow(g, rx, y + 24, 9, 0xFFFF8C1E, f);
			}
			case SOUL -> {
				glow(g, lx, y + 23, 9, 0xFF6EBEFF, 0.4f + 0.3f * slow);
				glow(g, rx, y + 23, 9, 0xFF6EBEFF, 0.4f + 0.3f * slow);
			}
			case STORM -> {
				// the orbs crackle, a flash now and then
				boolean flash = (now / 70) % 23 == 0;
				glow(g, lx, y + 5, 7, 0xFFFFE14A, flash ? 1 : 0.4f + 0.3f * fast);
				glow(g, rx, y + 5, 7, 0xFFFFE14A, (now / 70) % 29 == 0 ? 1 : 0.4f + 0.3f * fast);
			}
			case VOID -> {
				// the eyes glow, wider when it is hurt
				float a = 0.45f + 0.35f * slow + 0.4f * hit;
				glow(g, lx, cy, 10, 0xFF966EFF, a);
				glow(g, rx, cy, 10, 0xFF966EFF, a);
				if ((now / 100) % 50 == 0) {
					g.fill(lx - 8, cy - 4, lx + 8, cy + 4, 0xFF0A0418);
					g.fill(rx - 8, cy - 4, rx + 8, cy + 4, 0xFF0A0418);
				}
			}
			case MIRROR -> {
				glow(g, lx, cy, 9, 0xFFFFF0FF, 0.35f + 0.35f * slow);
				glow(g, rx, cy, 9, 0xFFFFF0FF, 0.35f + 0.35f * (1 - slow));
			}
			case WATER -> {
				// bubbles rising behind the porthole's glass; the needle trembling in the red
				for (int i = 0; i < 4; i++) {
					float ph = Math.floorMod(now + i * 700L, 2400) / 2400f;
					int bx = lx - 4 + i * 3, by = y + 28 - Math.round(ph * 14);
					g.fill(bx, by, bx + 1, by + 1, Ui.alpha(0xFFE8FCFF, 0.8f * (1 - ph)));
				}
				int tremble = Math.round((float) Math.sin(now / 45.0) * (1.2f - p));
				g.fill(rx + 1 + tremble, cy - 4, rx + 2 + tremble, cy - 1, 0xFFB41414);
			}
			case SEASONS -> {
				// the clock's hands go round, the great gear's spokes turn
				double a = now / 1000.0 * Math.PI / 2, b = now / 12000.0 * Math.PI * 2;
				hand(g, rx, cy, a, 7, 0xFF2A1E12);
				hand(g, rx, cy, b, 5, 0xFF2A1E12);
				double c = now / 2000.0;
				for (int k = 0; k < 3; k++) hand(g, lx, cy, c + k * Math.PI * 2 / 3, 6, 0xFFE8CC80);
			}
			case PULSE -> {
				// the heart crystal beats with the gauge
				float beat = Math.floorMod(now, 1100) / 1100f;
				float pulse = (float) Math.max(Math.exp(-Math.pow(beat * 12, 2)), 0.7 * Math.exp(-Math.pow((beat - 0.18) * 12, 2)));
				glow(g, lx, cy + 1, 11, 0xFFFF3C28, 0.35f + 0.65f * pulse);
			}
			case LACQUER -> glow(g, lx, cy + 4, 7, 0xFFFFD890, 0.25f + 0.2f * slow);
		}
	}

	/** One hand of a dial: a line of single pixels from the centre. */
	private static void hand(GuiGraphicsExtractor g, int cx, int cy, double a, int len, int color) {
		for (int k = 1; k <= len; k++) {
			int hx = cx + (int) Math.round(Math.sin(a) * k), hy = cy - (int) Math.round(Math.cos(a) * k);
			g.fill(hx, hy, hx + 1, hy + 1, color);
		}
	}

	/** The life round the bar: embers rising, spores drifting, bubbles, sparks, petals, motes, thread. */
	private static void ambient(GuiGraphicsExtractor g, Style st, int x, int y, long now, boolean front) {
		int n = 14;
		for (int i = front ? 0 : 1; i < n; i += 2) {
			long per = 2600 + (long) (hash(i, 29) * 2200);
			float ph = Math.floorMod(now + (long) (hash(i, 31) * per), per) / (float) per;
			int px = x + 6 + Math.round(hash(i, 37) * (W - 12));
			float a = (float) Math.sin(Math.PI * ph);
			int py;
			int color;
			int size = 1;
			switch (st) {
				case MOLTEN -> { py = y + 34 - Math.round(ph * 40); color = ph < 0.5f ? 0xFFFFD060 : 0xFFFF6A1A; px += Math.round((float) Math.sin(ph * 7 + i) * 2); }
				case SLUDGE -> { py = y + 30 - Math.round(ph * 34); color = 0xFFC8F06A; px += Math.round((float) Math.sin(ph * 5 + i) * 3); }
				case WATER -> { py = y + 34 - Math.round(ph * 38); color = 0xFFD8F8FF; size = i % 3 == 0 ? 2 : 1; }
				case STORM -> { if (hash((int) (now / 80) + i, 41) > 0.3f) continue; py = y + 4 + Math.round(hash(i, 43) * 32); color = 0xFFFFF4A0; a = 1; }
				case VOID -> { py = y + 6 + Math.round(hash(i, 47) * 28); px = x + W - 8 - Math.round(ph * (W - 16)); color = 0xFFD8CCFF; }
				case SEASONS -> {
					int season = (int) (now / 6000 % 4);
					py = y + 2 + Math.round(ph * 38); px += Math.round((float) Math.sin(ph * 6 + i) * 4);
					color = new int[]{0xFFF4A8C8, 0xFFFFE890, 0xFFE87A30, 0xFFFFFFFF}[season];
				}
				case BLOCKS -> { py = y + 32 - Math.round(ph * 36); color = 0xFF90E8F0; if (i % 3 != 0) continue; }
				case SOUL -> { py = y + 34 - Math.round(ph * 30); color = 0xFF8ACCFF; if (i % 2 != 0) continue; }
				case MIRROR -> { py = y + 20 + Math.round((ph - 0.5f) * 44 * (i % 2 == 0 ? 1 : -1)); color = 0xFFFFFFFF; }
				case PULSE -> { py = y + 34 + Math.round(ph * 6); color = 0xFFB07A5A; if (i % 2 != 0) continue; }
				default -> { py = y + 2 + Math.round(ph * 38); color = i % 2 == 0 ? 0xFFE8BC62 : 0xFFD43A26; if (i % 3 != 0) continue; }
			}
			if (px >= x + TX && px < x + TX + TW && py >= y + TY - 2 && py < y + TY + TH + 2) continue;
			g.fill(px, py, px + size, py + size, Ui.alpha(color, 0.85f * a));
		}
	}

	private static void matter(GuiGraphicsExtractor g, Style st, int x0, int y0, int fill, long now, float p, int seed) {
		switch (st) {
			case BLOCKS -> {
				// stone blocks shot through with moss, filling one by one, a block now and then catching the light
				for (int bx = 0; bx < fill; bx += 9) {
					int w = Math.min(8, fill - bx), i = bx / 9;
					int base = mix(0xFF2E8A3A, 0xFF58C060, hash(i, 7));
					int x = x0 + bx;
					g.fill(x, y0, x + w, y0 + TH, base);
					g.fill(x, y0, x + w, y0 + 2, mix(base, 0xFFD8FFD0, 0.5f));
					g.fill(x, y0, x + 1, y0 + TH, mix(base, 0xFFFFFFFF, 0.25f));
					g.fill(x, y0 + TH - 2, x + w, y0 + TH, mix(base, 0xFF000000, 0.4f));
					if (w == 8) g.fill(x + 3, y0 + 5, x + 5, y0 + 7, mix(base, 0xFF000000, 0.3f));
					float glint = (float) Math.max(0, Math.sin(now / 700.0 + i * 1.7) - 0.92) / 0.08f;
					if (glint > 0) g.fill(x, y0, x + w, y0 + TH, Ui.alpha(0xFF90E8F0, 0.45f * glint));
				}
			}
			case SLUDGE -> {
				for (int i = 0; i < fill; i++) {
					float n = (float) (Math.sin((i + now / 90.0) * 0.21) * 0.5 + Math.sin(i * 0.53 - now / 260.0) * 0.5);
					int c = mix(0xFF4E8A18, 0xFF9AD83A, 0.5f + n * 0.4f);
					int surf = Math.round(1.5f + (float) Math.sin(i * 0.4 + now / 180.0) * 1.2f);
					g.fill(x0 + i, y0 + surf, x0 + i + 1, y0 + TH, c);
					g.fill(x0 + i, y0 + surf, x0 + i + 1, y0 + surf + 1, 0xFFE0FF90);
					g.fill(x0 + i, y0 + TH - 3, x0 + i + 1, y0 + TH, mix(c, 0xFF102008, 0.5f));
				}
				for (int i = 0; i < 10; i++) {
					long per = 1400 + (i * 331L) % 900;
					float ph = Math.floorMod(now + i * 577L + seed, per) / (float) per;
					int bx = x0 + 3 + Math.round(hash(i, 11) * (TW - 6));
					if (bx > x0 + fill - 3) continue;
					int by = y0 + TH - 3 - Math.round(ph * (TH - 4));
					int r = ph > 0.85f ? 2 : 1;
					g.fill(bx, by, bx + r + 1, by + r + 1, Ui.alpha(0xFFE8FFB0, 0.85f * (1 - ph * 0.6f)));
				}
			}
			case MOLTEN -> {
				for (int i = 0; i < fill; i++) {
					double u = i - now / 45.0;
					float n = (float) (Math.sin(u * 0.17) * 0.45 + Math.sin(u * 0.41 + 1.3) * 0.3 + Math.sin(u * 0.07) * 0.25);
					for (int k = 0; k < TH; k++) {
						float depth = k / (float) TH;
						int c = mix(mix(0xFFFF7A10, 0xFFFFD050, 0.5f + n * 0.5f), 0xFF8A1A04, depth * 0.9f - n * 0.15f);
						g.fill(x0 + i, y0 + k, x0 + i + 1, y0 + k + 1, c);
					}
				}
				g.fill(x0, y0, x0 + fill, y0 + 1, 0xFFFFF4C0);
				// the bright, crusting end
				g.fill(x0 + fill - 2, y0, x0 + fill, y0 + TH, 0xFFFFF0B0);
				for (int i = 0; i < 6; i++) {
					float ph = Math.floorMod(now + i * 613L, 1100) / 1100f;
					int ex = x0 + Math.round(hash(i, 13) * fill);
					g.fill(ex, y0 + TH - 2 - Math.round(ph * (TH - 3)), ex + 1, y0 + TH - 1 - Math.round(ph * (TH - 3)), Ui.alpha(0xFFFFFFE0, 1 - ph));
				}
			}
			case SOUL -> {
				g.fill(x0, y0, x0 + fill, y0 + TH, 0xFF123A78);
				for (int i = 0; i < fill; i++) {
					float f1 = (float) (0.5 + 0.5 * Math.sin(i * 0.7 + now / 110.0) * Math.sin(i * 0.23 - now / 190.0));
					int h = Math.round(TH * (0.35f + 0.6f * f1));
					g.fill(x0 + i, y0 + TH - h, x0 + i + 1, y0 + TH, 0xFF3C8CE8);
					int h2 = Math.round(h * 0.55f);
					g.fill(x0 + i, y0 + TH - h2, x0 + i + 1, y0 + TH, 0xFF9AD8FF);
					g.fill(x0 + i, y0 + TH - 2, x0 + i + 1, y0 + TH, 0xFFE8F8FF);
				}
			}
			case STORM -> {
				for (int k = 0; k < TH; k++) g.fill(x0, y0 + k, x0 + fill, y0 + k + 1, mix(0xFF4A78D8, 0xFF1A2E70, Math.abs(k - TH / 2f) / (TH / 2f)));
				// the arc: a jagged line redrawn ten times a second, with a softer twin
				long beat = now / 90;
				int py = y0 + TH / 2;
				for (int i = 0; i < fill; i += 5) {
					int ny = y0 + 2 + Math.round(hash((int) (i / 5 + beat * 31), 17) * (TH - 4));
					int seg = Math.min(5, fill - i);
					for (int k = 0; k < seg; k++) {
						int yy = Math.round(py + (ny - py) * (k + 1) / (float) seg);
						g.fill(x0 + i + k, yy - 1, x0 + i + k + 1, yy + 2, Ui.alpha(0xFFFFE14A, 0.3f));
						g.fill(x0 + i + k, yy, x0 + i + k + 1, yy + 1, 0xFFFFFFFF);
					}
					py = ny;
				}
				if ((now / 60) % 9 == 0) g.fill(x0, y0, x0 + fill, y0 + TH, Ui.alpha(0xFFFFFFFF, 0.3f));
			}
			case VOID -> {
				for (int k = 0; k < TH; k++) g.fill(x0, y0 + k, x0 + fill, y0 + k + 1, mix(0xFF5A3CB0, 0xFF140A30, Math.abs(k - TH / 2f) / (TH / 2f) * 0.8f + 0.2f));
				// it feeds: motes of light flow along it into its swallowing end
				for (int i = 0; i < 12; i++) {
					float ph = Math.floorMod(now + i * 433L, 1800) / 1800f;
					int mx = x0 + Math.round(ph * fill);
					int my = y0 + 2 + Math.round(hash(i, 19) * (TH - 4));
					g.fill(mx, my, mx + 1, my + 1, Ui.alpha(0xFFFFF4FF, 0.9f * (1 - ph)));
				}
				g.fill(x0 + fill - 2, y0, x0 + fill, y0 + TH, 0xFF0A0418);
				g.fill(x0 + fill - 3, y0, x0 + fill - 2, y0 + TH, 0xFFB49AFF);
			}
			case MIRROR -> {
				int mid = x0 + TW / 2, a = mid - fill / 2, b = mid + fill / 2;
				g.fill(a, y0, b, y0 + TH / 2, 0xFF9AE6D8);
				g.fill(a, y0 + TH / 2, b, y0 + TH, 0xFFECA4DE);
				g.fill(a, y0, b, y0 + 1, 0xFFE8FFFA);
				g.fill(a, y0 + TH - 1, b, y0 + TH, 0xFFFFE4F8);
				g.fill(a, y0 + TH / 2, b, y0 + TH / 2 + 1, 0xFFFFFFFF);
				// a reflection sliding across, the same on both sides
				int sweep = Math.round(Math.floorMod(now, 2600) / 2600f * (fill / 2f + 16)) - 8;
				for (int sd : new int[]{-1, 1})
					for (int k = 0; k < TH; k++) {
						int sx = mid + sd * (sweep + k / 2);
						if (sx > a && sx < b - 2) g.fill(sx, y0 + k, sx + 2, y0 + k + 1, Ui.alpha(0xFFFFFFFF, 0.55f));
					}
			}
			case WATER -> {
				for (int k = 0; k < TH; k++) g.fill(x0, y0 + k, x0 + fill, y0 + k + 1, mix(0xFF2E9AD8, 0xFF0A2A6A, k / (float) TH));
				for (int i = 0; i < fill; i++) {
					int wy = y0 + 1 + Math.round((float) Math.sin(i * 0.3 + now / 220.0));
					g.fill(x0 + i, y0, x0 + i + 1, wy, 0xFF0E3A70);
					g.fill(x0 + i, wy, x0 + i + 1, wy + 1, 0xFFC8F4FF);
					// caustics: light ripples on the deeper water
					float c = (float) (Math.sin(i * 0.5 + now / 300.0) + Math.sin(i * 0.23 - now / 410.0));
					if (c > 1.5f) g.fill(x0 + i, y0 + 5, x0 + i + 1, y0 + 6 + (i % 2), Ui.alpha(0xFF9AE0FF, 0.5f));
				}
				for (int i = 0; i < 9; i++) {
					long per = 1700 + (i * 271L) % 800;
					float ph = Math.floorMod(now + i * 389L, per) / (float) per;
					int bx = x0 + 2 + Math.round(hash(i, 23) * (TW - 4)) + Math.round((float) Math.sin(ph * 9) * 1.2f);
					if (bx > x0 + fill - 2) continue;
					int by = y0 + TH - 2 - Math.round(ph * (TH - 3));
					g.fill(bx, by, bx + 1, by + 1, Ui.alpha(0xFFE8FCFF, 0.85f));
				}
			}
			case SEASONS -> {
				// spring, summer, autumn and winter along the quarters, blending where they meet
				int[] season = {0xFFF4A8C8, 0xFFF8D060, 0xFFE87A30, 0xFFB8DCF8};
				for (int i = 0; i < fill; i++) {
					float q = i / (TW / 4f);
					int s0 = Math.min(3, (int) q);
					float f = q - s0;
					int c = f > 0.85f && s0 < 3 ? mix(season[s0], season[s0 + 1], (f - 0.85f) / 0.15f) : season[s0];
					g.fill(x0 + i, y0, x0 + i + 1, y0 + TH, c);
					g.fill(x0 + i, y0 + TH - 3, x0 + i + 1, y0 + TH, mix(c, 0xFF000000, 0.25f));
					g.fill(x0 + i, y0, x0 + i + 1, y0 + 2, mix(c, 0xFFFFFFFF, 0.35f));
				}
				// the hand of the year sweeping the gauge, and the end ticking like a clock
				int hand = x0 + Math.round(Math.floorMod(now, 4000) / 4000f * fill);
				g.fill(hand, y0, hand + 1, y0 + TH, Ui.alpha(0xFFFFFFFF, 0.5f));
				int tick = (int) (now / 500 % 2);
				g.fill(x0 + fill - 2, y0 + tick, x0 + fill, y0 + TH - 1 + tick, 0xFF3A2410);
			}
			case PULSE -> {
				// the beat: lub-dub every 1.1 seconds, running out from the heart along the gauge
				float beat = Math.floorMod(now, 1100) / 1100f;
				for (int i = 0; i < fill; i++) {
					float d = i / (float) TW;
					float w1 = (float) Math.exp(-Math.pow((beat - d * 0.5f) * 14, 2)), w2 = (float) Math.exp(-Math.pow((beat - 0.18f - d * 0.5f) * 14, 2));
					float glow = Math.max(w1, w2 * 0.7f);
					int c = mix(0xFF7A0E0A, 0xFFFF5038, 0.25f + glow * 0.75f);
					g.fill(x0 + i, y0, x0 + i + 1, y0 + TH, c);
					int vy = y0 + 4 + Math.round((float) (Math.sin(i * 0.19) * 2 + Math.sin(i * 0.47) * 1.2));
					g.fill(x0 + i, vy, x0 + i + 1, vy + 1, mix(c, 0xFFFFC0A0, 0.5f + glow * 0.5f));
					g.fill(x0 + i, y0 + TH - 2, x0 + i + 1, y0 + TH, mix(c, 0xFF000000, 0.45f));
				}
			}
			case LACQUER -> {
				for (int k = 0; k < TH; k++) g.fill(x0, y0 + k, x0 + fill, y0 + k + 1, mix(0xFFD43A26, 0xFF6A0E0A, k / (float) TH));
				g.fill(x0, y0, x0 + fill, y0 + 1, 0xFFFF9A78);
				// little gold berries and leaves painted along it
				for (int i = 4; i < fill - 3; i += 10) {
					int up = (i / 10) % 2 == 0 ? 3 : 7;
					g.fill(x0 + i, y0 + up, x0 + i + 2, y0 + up + 2, 0xFFE8BC62);
					g.fill(x0 + i + 2, y0 + up + 1, x0 + i + 5, y0 + up + 2, 0xFFB88830);
				}
				// the brush still at work on the end
				g.fill(x0 + fill - 1, y0, x0 + fill + 1, y0 + TH, 0xFF8A1A10);
			}
		}
	}
}
