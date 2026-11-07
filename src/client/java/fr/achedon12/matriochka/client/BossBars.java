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
 * The bosses' own health bars, in place of vanilla's: each boss has its cartouche (bossbar_<boss>, painted by
 * tools/gui_stations.py) in its world's enamel, the world's number on the medallion, its name engraved above.
 * The health runs in the world's colour with a sheen; the damage just taken stays as a pale trail that melts away;
 * gold rivets mark the phase thresholds and crack once passed. Other mods' and vanilla's bars keep their look and
 * are stacked under these.
 */
public final class BossBars {
	private BossBars() {}

	private static final int W = 240, H = 28, IN_X = 34, IN_Y = 11, IN_W = 194, IN_H = 8;
	private static final Map<UUID, Float> TRAIL = new HashMap<>();
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
		// keep clear of what stands in the top corners (the first-steps card, the world plaque): slide the bars aside,
		// or under it when the screen is too narrow
		int left = 0, right = g.guiWidth(), below = 0;
		for (int[] r : obstacles(g)) {
			if (r[1] > 4 + H + 14) continue;
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
				y += H + 14;
			} else {
				// another mod's or vanilla's bar, as vanilla draws it
				g.centeredText(font, e.getName(), cx, y, 0xFFFFFFFF);
				((BossHealthOverlayAccess) overlay).matriochka$extractBar(g, cx - 91, y + 9, e);
				y += 19;
			}
			if (y >= g.guiHeight() / 3) break;
		}
		TRAIL.keySet().retainAll(events.keySet());
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
		// the damage just taken: a pale trail that waits a moment, then melts down to the health
		float t = TRAIL.getOrDefault(e.getId(), p);
		t = p > t ? p : Math.max(p, t - dt * 0.22f);
		TRAIL.put(e.getId(), t);
		int top = y + 10;
		Component name = e.getName();
		Ui.embossed(g, font, name, x + W / 2 - font.width(name) / 2 + 10, y, Ui.GOLD);
		Ui.sprite(g, "bossbar_" + d.id(), x, top, W, H);
		int color = 0xFF000000 | Ui.worldColor(d.world());
		int x0 = x + IN_X, y0 = top + IN_Y;
		int fill = Math.round(IN_W * p), trail = Math.round(IN_W * t);
		if (trail > fill) g.fill(x0 + fill, y0, x0 + trail, y0 + IN_H, Ui.alpha(0xFFFFF0D8, 0.75f));
		if (fill > 0) {
			// the health: the world's colour, lit on top and shaded under, with a slow sheen running along it
			g.fill(x0, y0, x0 + fill, y0 + IN_H, color);
			g.fill(x0, y0, x0 + fill, y0 + 2, Ui.alpha(0xFFFFFFFF, 0.35f));
			g.fill(x0, y0 + IN_H - 2, x0 + fill, y0 + IN_H, Ui.alpha(0xFF000000, 0.35f));
			Ui.sheen(g, x0, y0, fill, IN_H, 3200, d.id().hashCode(), 0.7f);
			// low on health, the bar pulses
			if (p < 0.25f) g.fill(x0, y0, x0 + fill, y0 + IN_H, Ui.alpha(0xFFFFFFFF, 0.18f * (0.5f + 0.5f * (float) Math.sin(now / 160.0))));
		}
		// the phase rivets: gold while ahead, cracked once the health has passed them
		for (float threshold : d.phases()) {
			int rx = x0 + Math.round(IN_W * threshold);
			boolean passed = p < threshold;
			g.fill(rx - 2, y0 - 2, rx + 2, y0 + IN_H + 2, 0xFF140B08);
			g.fill(rx - 1, y0 - 1, rx + 1, y0 + IN_H + 1, passed ? 0xFF5A3A1A : 0xFFF4D27A);
			if (passed) g.fill(rx, y0 + 2, rx + 1, y0 + IN_H - 2, 0xFF140B08);
		}
		// the world's number on the medallion
		Component n = Component.literal(d.world() == 0 ? "0" : String.valueOf(d.world()));
		Ui.embossed(g, font, n, x + 15 - font.width(n) / 2, top + H / 2 - 4, Ui.GOLD);
	}
}
