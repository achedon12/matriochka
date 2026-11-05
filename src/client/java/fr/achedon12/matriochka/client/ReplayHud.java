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
	private long lastElapsed = -1, receivedAt, shownAt = -1, stageAt = -1;
	private int lastStage = -1;

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		var t = MatrioClient.state.getCompoundOrEmpty("trial");
		if (!t.contains("key")) {
			shownAt = -1;
			lastElapsed = -1;
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
		int x = (g.guiWidth() - w) / 2, top = 4;
		// clear of the HUD plaque when the comfort options put it in a top corner (and scaled it up): beside it if
		// there is room, under it otherwise
		if (Hud.plaqueBottom > 0 && Hud.plaqueTop < top + h && Hud.plaqueX < x + w && Hud.plaqueRight > x) {
			boolean right = Hud.plaqueX > g.guiWidth() / 2;
			int beside = right ? Hud.plaqueX - 6 - w : Hud.plaqueRight + 6;
			if (beside >= 4 && beside + w <= g.guiWidth() - 4) x = beside;
			else top = Hud.plaqueBottom + 4;
		}
		int y = Math.round(top - (1 - slide) * (h + 8 + top));
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
	}

	static String clock(long ticks) {
		long cs = Math.max(0, ticks) * 5;
		return String.format(java.util.Locale.ROOT, "%d:%02d.%02d", cs / 6000, (cs / 100) % 60, cs % 100);
	}
}
