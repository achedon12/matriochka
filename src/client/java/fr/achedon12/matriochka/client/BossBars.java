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
 * The bosses' own health bars, in place of vanilla's: a reliquary per boss (sprites by tools/gui_stations.py).
 * <ul>
 * <li>a carved gold cameo with the boss's portrait on its world's enamel, which flinches and flashes when hit;</li>
 * <li>its name on a red satin ribbon with folded tails, its title under the tube;</li>
 * <li>a glass tube in a gold sleeve engraved with its world's motif, filled with the world's colour: a lit surface,
 *     a meniscus that ripples at the end of the health, bubbles and motes of the world rising in it;</li>
 * <li>gold collars between the boss's shells (its phases); a spent shell shows cracked, empty glass;</li>
 * <li>the damage just taken stays as pale foam that melts away; low on health the liquid pulses;</li>
 * <li>a painted doll of the world's colours on the tube's end.</li>
 * </ul>
 * Other mods' and vanilla's bars keep their look and are stacked under these; the bars keep clear of the
 * first-steps card and the world plaque.
 */
public final class BossBars {
	private BossBars() {}

	/** The reliquary's size, and where the tube's inside sits in it. */
	private static final int W = 250, H = 54;
	private static final int SLEEVE_X = 34, SLEEVE_Y = 16, TUBE_X = SLEEVE_X + 10, TUBE_Y = SLEEVE_Y + 7, TUBE_W = 180, TUBE_H = 10;
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
		int cx = g.guiWidth() / 2, y = 3;
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
				reliquary(g, font, e, d, cx - W / 2, y, dt, now);
				y += H + 4;
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

	private static void reliquary(GuiGraphicsExtractor g, Font font, LerpingBossEvent e, Defs.BossDef d, int x, int y, float dt, long now) {
		float p = Ui.clamp01(e.getProgress());
		float t = TRAIL.getOrDefault(e.getId(), p);
		// a hit: the health dropped since the last frame
		if (p < lastP(e) - 0.002f) HIT.put(e.getId(), now);
		// the foam of the damage just taken waits a moment, then melts down to the health
		t = p > t ? p : Math.max(p, t - dt * 0.2f);
		TRAIL.put(e.getId(), t);
		LAST_P.put(e.getId(), p);
		long hitAt = HIT.getOrDefault(e.getId(), -1L);
		float hit = hitAt < 0 ? 0 : 1 - Ui.since(hitAt, 380);
		if (hit <= 0) HIT.remove(e.getId());
		int world = d.world();
		int color = 0xFF000000 | Ui.worldColor(world);

		// the sleeve and its tube
		int sx = x + SLEEVE_X, sy = y + SLEEVE_Y;
		Ui.sprite(g, "bossbar_sleeve_" + d.id(), sx, sy, 200, 24);
		int x0 = x + TUBE_X, y0 = y + TUBE_Y;
		int fill = Math.round(TUBE_W * p), foam = Math.round(TUBE_W * t);
		if (foam > fill) g.fill(x0 + fill, y0, x0 + foam, y0 + TUBE_H, Ui.alpha(0xFFFFF4E0, 0.7f));
		if (fill > 0) liquid(g, x0, y0, fill, color, world, d.id().hashCode(), now, p);
		// the spent shells: cracked, empty glass between the thresholds the health has passed
		float[] th = d.phases();
		for (int i = 0; i < th.length; i++) {
			float hi = i == 0 ? 1f : th[i - 1];
			if (p < th[i]) {
				int a = x0 + Math.round(TUBE_W * th[i]), b = x0 + Math.round(TUBE_W * hi);
				for (int cx = Math.max(a, x0 + foam); cx < b; cx += 32) Ui.spritePart(g, "bossbar_crack", 64, 20, 0, 0, cx, y0, Math.min(32, b - cx), TUBE_H, 0xFFFFFFFF);
			}
		}
		Ui.sprite(g, "bossbar_glass", x0 + 4, y0, TUBE_W - 8, TUBE_H);
		for (float threshold : th) {
			int rx = x0 + Math.round(TUBE_W * threshold);
			Ui.sprite(g, "bossbar_collar", rx - 3, sy + 4, 6, 16, p < threshold ? 0xFFA08060 : 0xFFFFFFFF);
		}
		// the doll on the tube's end
		Ui.sprite(g, "bossbar_doll_" + world, sx + 198, sy - 2, 16, 26);

		// the cameo: it flinches and flashes when the boss is hit
		int shake = hit > 0 ? Math.round((float) Math.sin(now / 18.0) * 2 * hit) : 0;
		Ui.sprite(g, "bossbar_cameo_" + d.id(), x + shake, y + 6, 44, 44);
		if (hit > 0) Ui.sprite(g, "glow", x + 4 + shake, y + 10, 36, 36, Ui.white(0.5f * hit));

		// the name on its ribbon, the title under the tube
		Component name = e.getName();
		int nw = font.width(name) + 18, nx = x0 + TUBE_W / 2 - nw / 2, ny = y + 1;
		Ui.sprite(g, "bossbar_tail", nx - 9, ny + 1, 12, 14);
		Ui.sprite(g, "bossbar_tail_r", nx + nw - 3, ny + 1, 12, 14);
		Ui.sprite(g, "bossbar_ribbon", nx, ny, nw, 14);
		Ui.embossed(g, font, name, nx + 9, ny + 3, Ui.GOLD);
		// the title under the tube, on a soft dark band so it reads over any sky
		Component title = Component.translatable("cine.matriochka.boss." + d.id());
		int tw = font.width(title), tx = x0 + TUBE_W / 2 - tw / 2, ty = sy + 26;
		for (int k = 0; k < 6; k++) g.fill(tx - 10 + k * 2, ty - 1, tx + tw + 10 - k * 2, ty + 9, Ui.alpha(0xFF140B08, 0.1f));
		g.text(font, title, tx, ty, 0xFFE8CFA6, true);
	}

	private static final Map<UUID, Float> LAST_P = new HashMap<>();

	private static float lastP(LerpingBossEvent e) {
		return LAST_P.getOrDefault(e.getId(), e.getProgress());
	}

	/**
	 * The liquid in the tube: the world's colour lit on top and shaded under, a rippling meniscus at its end, a slow
	 * glow running through it, and bubbles and motes of the world rising (embers, sparks, spores, specks of dark).
	 */
	private static void liquid(GuiGraphicsExtractor g, int x0, int y0, int fill, int color, int world, long seed, long now, float p) {
		g.fill(x0, y0, x0 + fill, y0 + TUBE_H, color);
		g.fill(x0, y0, x0 + fill, y0 + 2, Ui.alpha(0xFFFFFFFF, 0.38f));
		g.fill(x0, y0 + TUBE_H - 3, x0 + fill, y0 + TUBE_H, Ui.alpha(0xFF000000, 0.32f));
		// the meniscus: a lighter rim that ripples up and down the end of the liquid
		for (int yy = 0; yy < TUBE_H; yy++) {
			int off = Math.round((float) Math.sin(now / 140.0 + yy * 0.9) * 1.2f);
			int ex = x0 + fill + off;
			if (ex > x0 + 1) g.fill(ex - 2, y0 + yy, ex, y0 + yy + 1, Ui.alpha(0xFFFFFFFF, 0.45f));
		}
		Ui.sheen(g, x0, y0, fill, TUBE_H, 3600, seed, 0.6f);
		// what rises in it, by world
		int mote = switch (world) {
			case 1 -> 0xFFC8F06A;
			case 2 -> 0xFFFFC060;
			case 4 -> 0xFFFFFFFF;
			case 5 -> 0xFF0A0A18;
			case 7 -> 0xFFD8F8FF;
			default -> 0xFFFFF0D0;
		};
		for (int i = 0; i < 9; i++) {
			long period = 1600 + (i * 371L) % 900;
			float ph = Math.floorMod(now + i * 577L + seed, period) / (float) period;
			int bx = x0 + 3 + (int) ((i * 0.618f % 1f) * (TUBE_W - 6));
			if (bx >= x0 + fill - 2) continue;
			int by = y0 + TUBE_H - 2 - Math.round(ph * (TUBE_H - 3));
			float a = (1 - ph) * 0.8f;
			if (world == 4 && (now / 70 + i) % 5 != 0) continue;
			g.fill(bx, by, bx + 1, by + 1, Ui.alpha(mote, a));
		}
		// low on health, the liquid pulses
		if (p < 0.25f) g.fill(x0, y0, x0 + fill, y0 + TUBE_H, Ui.alpha(0xFFFFFFFF, 0.16f * (0.5f + 0.5f * (float) Math.sin(now / 150.0))));
	}
}
