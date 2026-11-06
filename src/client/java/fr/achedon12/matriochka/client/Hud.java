package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;

/**
 * A small lacquered plaque in the corner: the world's rule as a gilt medallion (the season dial in World 8) with
 * its name, the Doll of Life as three nested dolls, and the souls beside a flickering lantern. The rule's meter is
 * not here but a vanilla status row above the hunger bar (MeterHud). Every value eases toward its new state; a doll
 * shakes and empties when a layer is lost, the lantern flares when souls come in.
 */
public class Hud implements HudElement {
	private static final int[] LIFE_W = {12, 10, 8}, LIFE_H = {17, 14, 11};
	private float soulsShown = -1, lanternFlare, seasonAngle;
	private int lastHere = -1, lastLayers = -1, lastSouls = -1;
	private long shownAt = Ui.now(), layerChangeAt = -1, lastFrame = Ui.now();
	private int changedLayer = -1;
	private boolean layerLost;
	/** Where the plaque ended up this frame, on screen after the comfort scale and corner (bottom 0 when hidden), for
	 * the cards drawn next to it. */
	static int plaqueX = 6, plaqueRight, plaqueTop, plaqueBottom;

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		var s = MatrioClient.state;
		int here = s.getIntOr("here", 0);
		int layers = s.getIntOr("doll_layers", 0), max = Math.min(3, s.getIntOr("doll_max", 0));
		plaqueBottom = 0;
		if (here == 0 && max == 0) {
			lastHere = -1;
			return;
		}
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - lastFrame) / 1000f);
		lastFrame = now;
		if (here != lastHere) {
			shownAt = now;
			lastHere = here;
		}
		if (lastLayers >= 0 && layers != lastLayers) {
			layerChangeAt = now;
			layerLost = layers < lastLayers;
			changedLayer = layerLost ? layers : layers - 1;
		}
		lastLayers = layers;
		int souls = s.getIntOr("souls", 0);
		if (soulsShown < 0) soulsShown = souls;
		if (lastSouls >= 0 && souls > lastSouls) lanternFlare = 1;
		lastSouls = souls;
		soulsShown = Math.abs(souls - soulsShown) < 0.5f ? souls : Ui.approach(soulsShown, souls, 5, dt);
		lanternFlare = Ui.approach(lanternFlare, 0, 2.2f, dt);

		var font = mc.font;
		int w = 132, h = here > 0 ? 50 : 26;
		float slide = Ui.easeBack(Ui.since(shownAt, 450));
		// comfort options: the plaque's scale and corner; it slides in from its own side
		var comfort = Comfort.get();
		float scale = comfort.hudScale;
		boolean right = comfort.hudCorner.endsWith("right"), bottom = comfort.hudCorner.startsWith("bottom");
		float ax = right ? g.guiWidth() - 6 - w * scale : 6, ay = bottom ? g.guiHeight() - 6 - h * scale - (right ? 0 : 40) : 6;
		g.pose().pushMatrix();
		g.pose().translate(ax, ay);
		g.pose().scale(scale, scale);
		int x = Math.round((right ? 1 : -1) * (1 - slide) * (w + 10)), y = 0;
		Ui.sprite(g, "hud_plaque", x, y, w, h);
		plaqueX = Math.round(ax);
		plaqueRight = Math.round(ax + w * scale);
		plaqueTop = Math.round(ay);
		plaqueBottom = Math.round(ay + h * scale);
		int rowY = y + 5;
		if (here > 0) {
			// World 0 (internal number 11) has its own rule, Obsession
			boolean zero = here == fr.achedon12.matriochka.world.Worlds.ZERO;
			String rule = zero ? "stillness" : Content.WORLDS.get(here - 1).rule();
			int mxp = x + 5, myp = y + 4;
			// the medallion turns in when the world changes; wind keeps swaying, gravity keeps bobbing
			float spin = (1 - Ui.easeOut(Ui.since(shownAt + 150, 600))) * (float) Math.PI;
			float idle = switch (rule) {
				case "wind" -> (float) Math.sin(now / 600.0) * 0.18f;
				case "ground" -> s.getFloatOr("g_tremor", 0) > 80 ? (float) Math.sin(now / 30.0) * 0.06f : 0;
				default -> 0;
			};
			float bob = rule.equals("gravity") ? (float) Math.sin(now / 500.0) * 1.2f : 0;
			g.pose().pushMatrix();
			g.pose().translate(mxp + 11, myp + 11 + bob);
			g.pose().rotate(spin + idle);
			Ui.sprite(g, "rule_" + rule, -11, -11, 22, 22);
			if (rule.equals("time")) {
				float target = (float) (s.getFloatOr("g_season", 0) / 100f * Math.PI * 1.5);
				seasonAngle = Ui.approach(seasonAngle, target, 3, dt);
				g.pose().rotate(seasonAngle + (float) Math.PI / 4);
				Ui.sprite(g, "dial_needle", -1, -8, 2, 10);
			}
			g.pose().popMatrix();
			Ui.wanderingGlint(g, new int[][]{{mxp + 4, myp + 4}, {mxp + 18, myp + 18}, {x + w - 4, y + 4}}, 2300, 5);

			int tx = x + 31;
			Ui.embossed(g, font, Component.translatable("hud.matriochka.world", zero ? 0 : here), tx, y + 6, Ui.GOLD);
			// the rule's name under the world's; its meter is a status row above the hunger bar (MeterHud)
			Ui.embossed(g, font, Component.translatable("rule.matriochka." + rule), tx, y + 18, Ui.MUTED);
			// a thin gilt rule between the rule row and the doll row
			g.fill(x + 6, y + 31, x + w - 6, y + 32, 0xFFB0782A);
			g.fill(x + 6, y + 32, x + w - 6, y + 33, 0xFF2A1408);
			rowY = y + 33;
		}
		// the Doll of Life: largest outer doll first, each a layer
		int dx = x + 7;
		for (int i = 0; i < max; i++) {
			int dw = LIFE_W[i], dh = LIFE_H[i];
			int base = rowY + 14;
			boolean full = i < layers;
			float ch = i == changedLayer && layerChangeAt >= 0 ? Ui.since(layerChangeAt, 900) : 1;
			g.pose().pushMatrix();
			if (ch < 1) {
				if (layerLost) {
					g.pose().translate((float) Math.sin(ch * 40) * 2 * (1 - ch), 0);
				} else {
					float sc = 1 + 0.5f * (1 - Ui.easeBack(ch));
					g.pose().translate(dx + dw / 2f, base - dh / 2f);
					g.pose().scale(sc, sc);
					g.pose().translate(-(dx + dw / 2f), -(base - dh / 2f));
				}
			}
			Ui.sprite(g, "life_" + i + (full ? "_full" : "_empty"), dx, base - dh, dw, dh);
			if (ch < 1 && layerLost) Ui.sprite(g, "life_" + i + "_full", dx, base - dh, dw, dh, Ui.white(1 - Ui.easeOut(ch)));
			g.pose().popMatrix();
			if (ch < 1) Ui.glint(g, dx + dw / 2f, base - dh * 0.6f, ch, 12);
			dx += dw + 2;
		}
		// souls: a lantern whose flame flickers, flaring when souls come in
		int lx = max > 0 ? dx + 6 : x + 7;
		Ui.sprite(g, "lantern", lx, rowY + 1, 9, 13);
		JournalScreen.lanternFlame(g, lx, rowY + 1, 1f + lanternFlare * 1.2f);
		Component sc = Component.translatable("hud.matriochka.souls", Math.round(soulsShown));
		Ui.embossed(g, font, sc, lx + 13, rowY + 4, lanternFlare > 0.05f ? 0xFFFFE8A0 : Ui.LIGHT);
		g.pose().popMatrix();
	}
}
