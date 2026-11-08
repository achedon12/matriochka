package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.world.Worlds;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.debug.DebugScreenEntries;
import net.minecraft.client.gui.components.debug.DebugScreenEntryStatus;
import net.minecraft.network.chat.Component;

/**
 * Where you are, now that no plaque sits in a corner: the world's name as a great title in the middle of the screen
 * with its rule under it each time you enter a world (fading in and out over three and a half seconds, with a soft
 * chime; the first entry's framed card of client/Cinematics plays instead), a "Matriochka: World N - name" line on
 * the F3 screen, and, if the comfort settings ask for it, a small permanent label in a corner.
 */
public final class WorldTitle implements HudElement {
	private static final int MS = 3500;
	public static final net.minecraft.resources.Identifier DEBUG_ID = Matriochka.id("world");
	private int lastHere = -1;
	private long shownAt = -10000;
	private int shownWorld;
	/** Titles shown since the game started (read by the check runs). */
	public static int titles;

	private WorldTitle() {}

	public static void init() {
		HudElementRegistry.addLast(Matriochka.id("world_title"), new WorldTitle());
		DebugScreenEntries.register(DEBUG_ID, (displayer, level, clientChunk, serverChunk) -> {
			String line = debugLine();
			if (!line.isEmpty()) displayer.addLine(line);
		});
	}

	/** The world's line on the F3 screen (empty on the Surface). */
	public static String debugLine() {
		int here = MatrioClient.state.getIntOr("here", 0);
		if (here <= 0) return "";
		return Component.translatable("debug.matriochka.world", here == Worlds.ZERO ? 0 : here, name(here)).getString();
	}

	private static Component name(int here) {
		return Component.translatable("world.matriochka." + (here == Worlds.ZERO ? Worlds.ZERO : here));
	}

	private static Component rule(int here) {
		String r = here == Worlds.ZERO ? "stillness" : Content.WORLDS.get(here - 1).rule();
		return Component.translatable("hud.matriochka.world_rule", Component.translatable("rule.matriochka." + r));
	}

	private static boolean known(int here) {
		return here == Worlds.ZERO || (here >= 1 && here <= Content.WORLDS.size());
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		Comfort.Values comfort = Comfort.get();
		if (!comfort.debugLineSet) {
			// the line shows with the F3 screen from the first time on; F3 + F6 can turn it off after that
			if (mc.debugEntries.getStatus(DEBUG_ID) == DebugScreenEntryStatus.NEVER) mc.debugEntries.setStatus(DEBUG_ID, DebugScreenEntryStatus.IN_OVERLAY);
			comfort.debugLineSet = true;
			Comfort.changed();
		}
		int here = MatrioClient.state.getIntOr("here", 0);
		long now = Ui.now();
		if (here != lastHere) {
			if (here > 0 && known(here) && lastHere != -1) {
				shownAt = now;
				shownWorld = here;
				titles++;
				Ui.sound(net.minecraft.sounds.SoundEvents.AMETHYST_BLOCK_RESONATE, 1.2f, 0.45f);
			}
			lastHere = here;
		}
		int w = g.guiWidth(), h = g.guiHeight();
		// the great title, unless the first entry's framed card is playing
		float t = (now - shownAt) / (float) MS;
		if (t >= 0 && t < 1 && !Cinematics.cardPlaying() && shownWorld == here) {
			float a = t < 0.15f ? t / 0.15f : t > 0.7f ? (1 - t) / 0.3f : 1f;
			Component name = name(here), sub = rule(here);
			float big = 3f;
			g.pose().pushMatrix();
			g.pose().translate(w / 2f, h * 0.3f);
			g.pose().scale(big, big);
			int tw = mc.font.width(name);
			int col = Ui.alpha(Ui.GOLD, a), dark = Ui.alpha(0xFF1A0A06, a * 0.85f);
			for (int[] o : new int[][]{{1, 1}, {1, 0}, {0, 1}}) g.text(mc.font, name, -tw / 2 + o[0], o[1], dark, false);
			g.text(mc.font, name, -tw / 2, 0, col, false);
			g.pose().popMatrix();
			g.pose().pushMatrix();
			g.pose().translate(w / 2f, h * 0.3f + 30);
			g.pose().scale(1.4f, 1.4f);
			int sw = mc.font.width(sub);
			g.text(mc.font, sub, -sw / 2 + 1, 1, Ui.alpha(0xFF1A0A06, a * 0.8f), false);
			g.text(mc.font, sub, -sw / 2, 0, Ui.alpha(Ui.LIGHT, a), false);
			g.pose().popMatrix();
			// a thin gilt rule between them, drawn in from the middle
			int half = Math.round(Math.min(1f, t / 0.25f) * 70);
			g.fill(w / 2 - half, Math.round(h * 0.3f) + 26, w / 2 + half, Math.round(h * 0.3f) + 27, Ui.alpha(0xFFB0782A, a));
		}
		// the permanent label, if asked for
		if (!comfort.worldLabel.equals("off") && here > 0 && known(here)) {
			Component label = Component.translatable("hud.matriochka.world_label", here == Worlds.ZERO ? 0 : here, name(here));
			int lw = mc.font.width(label) + 8, lh = 13;
			boolean right = comfort.worldLabel.endsWith("right"), bottom = comfort.worldLabel.startsWith("bottom");
			int x = right ? w - lw - 4 : 4, y = bottom ? h - lh - 4 : 4;
			if (bottom) y -= right ? 0 : 0;
			g.fill(x, y, x + lw, y + lh, 0xC0140A06);
			g.fill(x, y + lh - 1, x + lw, y + lh, 0xFFB0782A);
			g.text(mc.font, label, x + 4, y + 3, Ui.GOLD, false);
		}
	}
}
