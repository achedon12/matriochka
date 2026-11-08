package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.ModContent;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/**
 * The souls and the Doll of Life, kept out of the corners that other mods and clients use for their own HUD.
 *
 * The souls are a thin blue bar laid along the top edge of the vanilla experience bar, as wide as it, under the
 * hearts and the hunger (drawn before them, so their rows and every mod that leans on their places stay where they
 * are). It fills toward the next hundred souls; their count shows in blue over it when it changes, beside the
 * experience level, never on it, and fades after three seconds. The bar is there inside the worlds, or while holding
 * something that holds souls; it hides with the status bars (F1, creative, spectator). The Doll of Life's layers are
 * three small dolls at the bar's left end.
 */
public class Hud implements HudElement {
	/** The experience bar's width, and how long the count shows after it changed. */
	private static final int BAR_W = 182, SHOW_MS = 3000;
	private static int lastSouls = -1;
	private static long changedAt = -10000;
	/** Two elements share this class: the bar (drawn before the hearts) and the count (drawn after them, on top). */
	private final boolean count;

	public Hud(boolean count) {
		this.count = count;
	}
	/** Kept for the cards that used to sit beside the corner plaque (none is drawn now). */
	static int plaqueX = 6, plaqueRight, plaqueTop, plaqueBottom;

	/** Whether the souls are shown now: inside the worlds, or while holding a soul shard or vessel. */
	public static boolean soulsShown(Minecraft mc) {
		Player p = mc.player;
		if (p == null || mc.gameMode == null || !mc.gameMode.canHurtPlayer()) return false;
		if (MatrioClient.state.getIntOr("here", 0) > 0) return true;
		return holdsSouls(p.getMainHandItem()) || holdsSouls(p.getOffhandItem());
	}

	private static boolean holdsSouls(ItemStack s) {
		var def = ModContent.def(ModContent.idOf(s.getItem()));
		return def != null && "soul".equals(def.kind());
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		plaqueBottom = 0;
		var s = MatrioClient.state;
		int souls = s.getIntOr("souls", 0);
		long now = Ui.now();
		if (count) {
			if (lastSouls >= 0 && souls != lastSouls) changedAt = now;
			lastSouls = souls;
		}
		if (!soulsShown(mc)) return;
		if (count) {
			count(g, mc, souls, now);
			return;
		}
		int x = g.guiWidth() / 2 - BAR_W / 2, y = g.guiHeight() - 32;
		// the bar: a lacquer line under a gold edge, filled with blue toward the next hundred souls
		g.fill(x, y, x + BAR_W, y + 3, 0xFF2A1408);
		g.fill(x, y, x + BAR_W, y + 1, 0xFF96682A);
		int fill = Math.round((BAR_W - 2) * ((souls % 100) / 100f));
		if (fill > 0) {
			g.fill(x + 1, y + 1, x + 1 + fill, y + 3, 0xFF3A7AD8);
			g.fill(x + 1, y + 1, x + 1 + fill, y + 2, 0xFF8AC4FF);
			// a glint running along the blue
			int gx = x + 1 + (int) ((now / 12) % Math.max(1, fill + 40)) - 20;
			if (gx > x && gx < x + fill) g.fill(gx, y + 1, gx + 2, y + 2, 0xFFE8F6FF);
		}
		// the Doll of Life: three small dolls at the bar's left end, full or empty
		int max = Math.min(3, s.getIntOr("doll_max", 0)), layers = s.getIntOr("doll_layers", 0);
		for (int i = 0; i < max; i++) {
			int dw = 6 - i, dh = 9 - i;
			Ui.sprite(g, "life_" + i + (i < layers ? "_full" : "_empty"), x - 4 - (i + 1) * 7, y + 3 - dh, dw, dh);
		}
	}

	private static void count(GuiGraphicsExtractor g, Minecraft mc, int souls, long now) {
		// the count, in blue, when it changes: beside the experience level, never over it
		float shown = 1f - Ui.clamp01((now - changedAt - (SHOW_MS - 600)) / 600f);
		if (now - changedAt >= SHOW_MS || shown <= 0) return;
		String text = Integer.toString(souls);
		float scale = Math.max(0.75f, Math.min(1.5f, Comfort.get().hudScale));
		int level = mc.player.experienceLevel;
		int xpw = level > 0 ? mc.font.width(Integer.toString(level)) : 0;
		int tw = Math.round(mc.font.width(text) * scale);
		// the experience level sits in the middle; the count goes just left of it (in the middle when there is none)
		int tx = level > 0 ? g.guiWidth() / 2 - xpw / 2 - 3 - tw : g.guiWidth() / 2 - tw / 2;
		int ty = g.guiHeight() - 35 - Math.round(8 * (scale - 1));
		g.pose().pushMatrix();
		g.pose().translate(tx, ty);
		g.pose().scale(scale, scale);
		int a = Math.round(255 * shown) << 24;
		for (int[] o : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) g.text(mc.font, text, o[0], o[1], a | 0x0A1430, false);
		g.text(mc.font, text, 0, 0, a | 0x9ED6FF, false);
		g.pose().popMatrix();
	}
}
