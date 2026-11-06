package fr.achedon12.matriochka.client;

import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;

/**
 * The trial clock: a lacquered plaque at the top of the screen while a trial runs, with the trial's name on a gilt
 * line, the running time in large figures (green while under par, warm once past it), the stage and the best time to
 * beat. The clock ticks smoothly between the server's updates and glints when a stage falls.
 */
public class ReplayHud implements HudElement {
	/** Bottom of the plaque on the last frame (0 while no trial runs), so the subtitles keep clear of it. */
	static int bottom;
	private long lastElapsed = -1, receivedAt, shownAt = -1, stageAt = -1, countAt = -1, goAt = -1;
	private int lastStage = -1, lastLeft = -1;
	private String lastPhase = "";

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		var t = MatrioClient.state.getCompoundOrEmpty("trial");
		if (!t.contains("key")) {
			shownAt = -1;
			lastElapsed = -1;
			bottom = 0;
			lastPhase = "";
			return;
		}
		long now = Ui.now();
		if (shownAt < 0) shownAt = now;
		String phase = t.getStringOr("phase", "countdown");
		long elapsed = t.getLongOr("elapsed", 0L);
		if (elapsed != lastElapsed) {
			lastElapsed = elapsed;
			receivedAt = now;
		}
		boolean running = phase.equals("fight") || phase.equals("between");
		long shown = elapsed + (running ? Math.min(30, (now - receivedAt) / 50) : 0);
		int stage = t.getIntOr("stage", 1), stages = t.getIntOr("stages", 1);
		if (lastStage >= 0 && stage != lastStage) stageAt = now;
		lastStage = stage;
		int par = t.getIntOr("par", 0), best = t.getIntOr("best", 0);

		var font = mc.font;
		int w = 168, h = 42;
		float slide = Ui.easeBack(Ui.since(shownAt, 450));
		// the comfort option's HUD size scales the clock with the plaque; the layout below is in scaled units
		float sc = Comfort.get().hudScale;
		int gw = Math.round(g.guiWidth() / sc);
		int x = (gw - w) / 2, top = 4;
		// clear of the HUD plaque when the comfort options put it in a top corner (and scaled it up): beside it if
		// there is room, under it otherwise
		int px = Math.round(Hud.plaqueX / sc), pr = Math.round(Hud.plaqueRight / sc), pt = Math.round(Hud.plaqueTop / sc), pb = Math.round(Hud.plaqueBottom / sc);
		if (Hud.plaqueBottom > 0 && pt < top + h && px < x + w && pr > x) {
			boolean right = px > gw / 2;
			int beside = right ? px - 6 - w : pr + 6;
			if (beside >= 4 && beside + w <= gw - 4) x = beside;
			else top = pb + 4;
		}
		// under the boss bars (12 pixels down, then 19 a bar), never over them
		int bars = ((fr.achedon12.matriochka.mixin.client.BossHealthOverlayAccess) mc.gui.hud.getBossOverlay()).matriochka$events().size();
		if (bars > 0) top = Math.max(top, Math.round((19 * Math.min(bars, 4) + 2) / sc));
		int y = Math.round(top - (1 - slide) * (h + 8 + top));
		bottom = Math.round((y + h) * sc);
		g.pose().pushMatrix();
		g.pose().scale(sc, sc);
		Ui.sprite(g, "hud_plaque", x, y, w, h);
		Component name = Component.translatable("trial.matriochka." + t.getStringOr("key", ""));
		Ui.embossed(g, font, name, x + w / 2 - font.width(name) / 2, y + 5, Ui.GOLD);
		g.fill(x + 8, y + 15, x + w - 8, y + 16, 0xFFB0782A);
		g.fill(x + 8, y + 16, x + w - 8, y + 17, 0xFF2A1408);
		// the time, twice the size, coloured against the par
		boolean underPar = par <= 0 || shown <= par * 20L;
		int col = phase.equals("countdown") ? Ui.MUTED : phase.equals("done") ? Ui.OK : underPar ? 0xFFC8F0A0 : Ui.WARN;
		Component time = Component.literal(clock(shown));
		g.pose().pushMatrix();
		g.pose().translate(x + 10, y + 20);
		g.pose().scale(1.6f, 1.6f);
		Ui.embossed(g, font, time, 0, 0, col);
		g.pose().popMatrix();
		Component st = Component.translatable("hud.matriochka.trial.stage", stage, stages);
		Ui.embossed(g, font, st, x + w - 8 - font.width(st), y + 20, Ui.LIGHT);
		Component b = best > 0 ? Component.translatable("hud.matriochka.trial.best", clock(best)) : Component.translatable("hud.matriochka.trial.par", clock(par * 20L));
		g.text(font, b, x + w - 8 - font.width(b), y + 30, Ui.MUTED, false);
		if (stageAt >= 0 && Ui.since(stageAt, 900) < 1) Ui.glint(g, x + w - 20, y + 24, Ui.since(stageAt, 900), 14);
		Ui.wanderingGlint(g, new int[][]{{x + 4, y + 4}, {x + w - 4, y + 4}, {x + w / 2, y + h - 4}}, 2600, 17);
		g.pose().popMatrix();
		countdown(g, font, t.getIntOr("left", 0), phase, now);
	}

	/**
	 * The countdown, large in the middle of the screen: each second's figure lands in gold with a ring that widens and
	 * fades, then a gilt burst as the fight opens.
	 */
	private void countdown(GuiGraphicsExtractor g, net.minecraft.client.gui.Font font, int left, String phase, long now) {
		if (phase.equals("countdown") && left != lastLeft) countAt = now;
		if (lastPhase.equals("countdown") && !phase.equals("countdown")) goAt = now;
		lastLeft = phase.equals("countdown") ? left : -1;
		lastPhase = phase;
		float cx = g.guiWidth() / 2f, cy = g.guiHeight() * 0.36f;
		if (phase.equals("countdown") && left > 0) {
			float k = Ui.since(countAt, 900);
			// lands from a little bigger, then settles; fades in its last moments
			float sc = 7f - 2f * Ui.easeOut(Math.min(1, k * 2.4f));
			float a = k > 0.8f ? 1 - (k - 0.8f) / 0.2f : 1;
			Component n = Component.literal(Integer.toString(left));
			g.pose().pushMatrix();
			g.pose().translate(cx, cy);
			g.pose().scale(sc, sc);
			int tw = font.width(n);
			// a dark rim all round, then the gilt figure with a lighter top edge
			int rim = Ui.alpha(Ui.SHADOW, a * 0.9f);
			for (int[] o : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}}) g.text(font, n, -tw / 2 + o[0], -4 + o[1], rim, false);
			g.text(font, n, -tw / 2, -4, Ui.alpha(left == 1 ? Ui.WARN : Ui.GOLD, Math.max(0.05f, a)), false);
			g.pose().popMatrix();
			// a gleam on the figure's shoulder as it lands
			Ui.glint(g, cx + font.width(n) * sc * 0.45f, cy - 3.5f * sc, Math.min(1, k * 1.8f), 16);
		} else if (goAt >= 0 && Ui.since(goAt, 700) < 1) {
			float k = Ui.since(goAt, 700);
			Ui.glint(g, cx, cy, k, 30 + 60 * k);
			Ui.glint(g, cx - 40 * k, cy + 6, Math.min(1, k * 1.3f), 18);
			Ui.glint(g, cx + 40 * k, cy - 6, Math.min(1, k * 1.3f), 18);
		}
	}

	static String clock(long ticks) {
		long cs = Math.max(0, ticks) * 5;
		return String.format(java.util.Locale.ROOT, "%d:%02d.%02d", cs / 6000, (cs / 100) % 60, cs % 100);
	}
}
