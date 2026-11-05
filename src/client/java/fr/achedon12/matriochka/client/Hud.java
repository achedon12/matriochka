package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;

/** A small lacquered plaque: the world's rule gauge, the doll layers as little dolls, souls and karma. */
public class Hud implements HudElement {
	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		var s = MatrioClient.state;
		int here = s.getIntOr("here", 0);
		int layers = s.getIntOr("doll_layers", 0), max = s.getIntOr("doll_max", 0);
		if (here == 0 && max == 0) return;
		int x = 6, y = 6, w = 132, h = here > 0 ? 52 : 34;
		Ui.frame(g, x, y, w, h);
		int ix = x + 11, iy = y + 11;
		if (here > 0) {
			String rule = Content.WORLDS.get(here - 1).rule();
			String gauge = switch (rule) {
				case "toxin", "synthesis" -> "toxin"; case "heat" -> "heat"; case "darkness" -> "noise"; case "pressure" -> "oxygen";
				case "time" -> "season"; case "ground" -> "tremor"; default -> "";
			};
			g.text(mc.font, Component.translatable("hud.matriochka.world", here), ix, iy, Ui.GOLD, false);
			if (!gauge.isEmpty()) {
				float v = s.getFloatOr("g_" + gauge, gauge.equals("oxygen") ? 100f : 0f) / 100f;
				int col = gauge.equals("oxygen") ? 0xFF4AA8E0 : v > 0.75f ? 0xFFD8402A : v > 0.5f ? 0xFFE0902A : Ui.worldColor(here);
				Component label = Component.translatable("rule.matriochka." + rule);
				g.text(mc.font, label, ix, iy + 12, Ui.MUTED, false);
				Ui.gauge(g, ix + 46, iy + 12, w - 68, 7, v, col);
			}
			iy += 24;
		}
		for (int i = 0; i < Math.max(max, 0); i++) Ui.sprite(g, i < layers ? "doll_full" : "doll_empty", ix + i * 11, iy - 2, 9, 12);
		g.text(mc.font, Component.translatable("hud.matriochka.souls", s.getIntOr("souls", 0)), ix + (max > 0 ? max * 11 + 4 : 0), iy, Ui.LIGHT, false);
	}
}
