package fr.achedon12.matriochka.client;

import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.world.entity.player.Player;

/**
 * The souls and the Doll of Life, kept out of the corners that other mods and clients use for their own HUD.
 *
 * The souls are a bar of their own, as wide as the experience bar and stacked above it with a gap: the experience
 * bar and its green level stay where vanilla puts them, then comes the souls bar, filled with blue toward the next
 * hundred souls, with its blue count centred on it the way the level sits on the experience bar, high enough never
 * to touch the green number. To make room, the status rows (hearts, armour, hunger, air, mount health, the world's
 * rule gauges and the shell's doll) are raised by {@link #lift()} while the bar shows, by translating their whole
 * HUD layers, so what other mods draw inside those layers moves with them. The bar is always there, like the experience
 * bar, so the rows never jump; it hides with the status bars (F1, creative, spectator) or from the comfort settings. The Doll of
 * Life's layers are three small dolls at the bar's left end, outside it.
 */
public class Hud implements HudElement {
	/** The experience bar's width, the souls bar's height, and its top above the bottom of the screen. */
	private static final int BAR_W = 182, BAR_H = 5, BAR_UP = 42;
	/** Kept for the cards that used to sit beside the corner plaque (none is drawn now). */
	static int plaqueX = 6, plaqueRight, plaqueTop, plaqueBottom;

	/** Whether the souls bar shows now: always, like the experience bar (not in creative, spectator or with F1), unless turned off. */
	public static boolean soulsShown(Minecraft mc) {
		Player p = mc.player;
		return p != null && mc.gameMode != null && mc.gameMode.canHurtPlayer() && !fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc) && Comfort.get().soulsBar;
	}

	private static float countScale() {
		return Math.max(0.75f, Math.min(1.5f, Comfort.get().hudScale));
	}

	/**
	 * How far the status rows go up while the souls bar shows: above the bar, and above its count when a bigger HUD
	 * makes the count wider than the gap between the hearts and the hunger.
	 */
	public static int lift() {
		Minecraft mc = Minecraft.getInstance();
		if (!soulsShown(mc)) return 0;
		float sc = countScale();
		return sc > 1f ? (int) Math.ceil(12 + 8 * sc) : BAR_UP - 29;
	}

	/** A HUD layer drawn raised by {@link #lift()}. */
	public static HudElement lifted(HudElement layer) {
		return (g, delta) -> {
			int up = lift();
			if (up == 0) {
				layer.extractRenderState(g, delta);
				return;
			}
			g.pose().pushMatrix();
			g.pose().translate(0, -up);
			try {
				layer.extractRenderState(g, delta);
			} finally {
				g.pose().popMatrix();
			}
		};
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		plaqueBottom = 0;
		if (!soulsShown(mc)) return;
		var s = MatrioClient.state;
		int souls = s.getIntOr("souls", 0);
		long now = Ui.now();
		int x = g.guiWidth() / 2 - BAR_W / 2, y = g.guiHeight() - BAR_UP;
		// the frame: a gilt edge around a lacquer groove, notched in tenths like the experience bar
		g.fill(x, y, x + BAR_W, y + BAR_H, 0xFF6A4614);
		g.fill(x, y, x + BAR_W, y + 1, 0xFFC8963C);
		g.fill(x + 1, y + 1, x + BAR_W - 1, y + BAR_H - 1, 0xFF1E0E06);
		int inner = BAR_W - 2;
		int fill = Math.round(inner * ((souls % 100) / 100f));
		if (fill > 0) {
			g.fill(x + 1, y + 1, x + 1 + fill, y + BAR_H - 1, 0xFF2E66C8);
			g.fill(x + 1, y + 1, x + 1 + fill, y + 2, 0xFF8AC4FF);
			// a glint running along the blue
			int gx = x + 1 + (int) ((now / 12) % Math.max(1, fill + 40)) - 20;
			if (gx > x && gx < x + fill) g.fill(gx, y + 1, gx + 2, y + BAR_H - 1, 0x90E8F6FF);
		}
		for (int i = 1; i < 10; i++) g.fill(x + 1 + inner * i / 10, y + 1, x + 2 + inner * i / 10, y + BAR_H - 1, 0x60000000);
		// the Doll of Life: three small dolls at the bar's left end, outside it, full or empty
		int max = Math.min(3, s.getIntOr("doll_max", 0)), layers = s.getIntOr("doll_layers", 0);
		for (int i = 0; i < max; i++) {
			int dw = 6 - i, dh = 9 - i;
			Ui.sprite(g, "life_" + i + (i < layers ? "_full" : "_empty"), x - 4 - (i + 1) * 7, y + BAR_H + 1 - dh, dw, dh);
		}
		// the count, centred on the bar as the level is on the experience bar, outlined the same way
		String text = Integer.toString(souls);
		float sc = countScale();
		int tw = mc.font.width(text);
		g.pose().pushMatrix();
		g.pose().translate(g.guiWidth() / 2f, y + 2);
		g.pose().scale(sc, sc);
		int tx = -tw / 2, ty = -8;
		for (int[] o : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) g.text(mc.font, text, tx + o[0], ty + o[1], 0xFF000000, false);
		g.text(mc.font, text, tx, ty, 0xFF7EC8FF, false);
		g.pose().popMatrix();
	}
}
