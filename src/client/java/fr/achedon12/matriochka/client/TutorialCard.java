package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.net.Net;
import fr.achedon12.matriochka.world.Tutorial;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

/**
 * The first-steps card: a small lacquer plaque next to the HUD plaque (under it, or over it in a bottom corner) with the step's item in a gilt slot, its name,
 * a one-line hint, a compass needle toward the Guardian's Sanctuary while it is being searched for, and ten pips for
 * the ten steps. It slides in again with a glint each time a step is done, and says farewell for a few seconds after
 * the last one. Hidden or shown again from the Scroll and the Journal (the choice is kept per player, server side).
 */
public class TutorialCard implements HudElement {
	private static final int W = 152;
	private static final long FAREWELL_MS = 9000;
	private int lastStep = -1;
	private long changedAt = Ui.now(), doneAt = -1;

	/** Whether the card is hidden by the player's choice. */
	static boolean hidden() {
		return MatrioClient.state.getBooleanOr("f_tut_hide", false);
	}

	static int step() {
		return Math.max(0, Math.min(Tutorial.DONE, MatrioClient.state.getIntOr("tut_step", 0)));
	}

	/** The Scroll and Journal button: hide the card, or bring it back. */
	static void toggle() {
		ClientPlayNetworking.send(new Net.TutorialPayload(hidden() ? "show" : "hide"));
	}

	/** Tells the server the Scroll was read up to its objective page (the first step). */
	static void scrollRead() {
		if (step() == 0) ClientPlayNetworking.send(new Net.TutorialPayload("read"));
	}

	private static Item icon(String id) {
		return switch (id) {
			case "read" -> ModContent.item("artisan_scroll");
			case "sanctuary" -> Items.COMPASS;
			case "wake" -> ModContent.item("sanctuary_altar");
			case "defeat" -> ModContent.item("guardian_core");
			case "workbench" -> ModContent.item("matrix_workbench");
			case "seed", "plant" -> ModContent.item("seed_1");
			case "till" -> ModContent.item("world_soil_0");
			default -> ModContent.item("world_block");
		};
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.gui.hud.isHidden() || MatrioClient.state.isEmpty()) return;
		// no card before the server's first check of this player (see Tutorial.tick)
		if (!MatrioClient.state.contains("tut_step")) {
			lastStep = -1;
			return;
		}
		int step = step();
		long now = Ui.now();
		if (step != lastStep) {
			// a step done in this session: slide in again; the last one gets a farewell card
			if (lastStep >= 0 && step > lastStep) {
				changedAt = now;
				Ui.sound(SoundEvents.BOOK_PAGE_TURN, 1.3f, 0.8f);
				if (step >= Tutorial.DONE) {
					doneAt = now;
					Ui.sound(SoundEvents.PLAYER_LEVELUP, 1.6f, 0.35f);
				}
			}
			lastStep = step;
		}
		if (hidden()) return;
		boolean done = step >= Tutorial.DONE;
		if (done && (doneAt < 0 || now - doneAt > FAREWELL_MS)) return;
		draw(g, mc, step, done, now);
	}

	private void draw(GuiGraphicsExtractor g, Minecraft mc, int step, boolean done, long now) {
		var font = mc.font;
		String id = done ? "enter" : Tutorial.STEPS[step];
		Component title = Component.translatable(done ? "tutorial.matriochka.done" : "tutorial.matriochka." + id);
		Component hint = Component.translatable(done ? "tutorial.matriochka.done.hint" : "tutorial.matriochka." + id + ".hint");
		int textX = 30, textW = W - textX - 7;
		var lines = font.split(hint, textW);
		boolean compass = !done && id.equals("sanctuary");
		int h = 7 + 10 + 11 + lines.size() * 9 + (compass ? 15 : 0) + 11;
		float in = Ui.easeBack(Ui.since(changedAt, 480));
		// the farewell card sinks away at the end
		float out = done ? Ui.easeIn(Ui.since(doneAt + FAREWELL_MS - 500, 500)) : 0;
		// next to the HUD plaque, wherever the comfort options put it: under it at the top, over it at the bottom, and
		// aligned on its side (the card slides in from that side)
		var comfort = Comfort.get();
		boolean right = comfort.hudCorner.endsWith("right"), bottom = comfort.hudCorner.startsWith("bottom");
		boolean plaque = Hud.plaqueBottom > 0;
		int baseX = right ? (plaque ? Hud.plaqueRight : g.guiWidth() - 6) - W : plaque ? Hud.plaqueX : 6;
		int y = bottom ? (plaque ? Hud.plaqueTop - 4 : g.guiHeight() - 6 - (right ? 0 : 40)) - h : plaque ? Hud.plaqueBottom + 4 : 6;
		int x = Math.round(baseX + (right ? 1 : -1) * ((1 - in) + out) * (W + 10));
		Ui.sprite(g, "hud_plaque", x, y, W, h);
		// a gilt slot with the step's item; it bobs a little while the step waits
		int sx = x + 7, sy = y + 8;
		Ui.sprite(g, "slot", sx, sy, 18, 18);
		float bob = (float) Math.sin(now / 520.0) * 0.8f;
		g.pose().pushMatrix();
		g.pose().translate(0, bob);
		g.item(new ItemStack(icon(id)), sx + 1, sy + 1);
		g.pose().popMatrix();
		Ui.glint(g, sx + 14, sy + 4, Ui.since(changedAt + 200, 700), 11);
		Ui.wanderingGlint(g, new int[][]{{x + 4, y + 4}, {x + W - 4, y + 4}, {x + W - 4, y + h - 4}}, 2600, 17);

		int tx = x + textX, ty = y + 6;
		Component header = Component.translatable("tutorial.matriochka.header", Math.min(step + 1, Tutorial.DONE), Tutorial.DONE);
		g.text(font, header, tx, ty, Ui.MUTED, false);
		ty += 10;
		Ui.embossed(g, font, fit(font, title, textW), tx, ty, Ui.GOLD);
		ty += 11;
		for (FormattedCharSequence line : lines) {
			g.text(font, line, tx, ty, Ui.LIGHT, false);
			ty += 9;
		}
		if (compass) {
			compassRow(g, mc, tx, ty + 2, now);
			ty += 15;
		}
		// the ten steps as pips: done in gold, the current one glowing in the Surface's red
		int px = tx, py = y + h - 8;
		for (int i = 0; i < Tutorial.DONE; i++) {
			int col = i < step ? Ui.GOLD : i == step ? Ui.alpha(0xFFDE3422, 0.65f + 0.35f * (float) Math.sin(now / 240.0)) : 0xFF3A1A10;
			g.fill(px, py, px + 9, py + 3, 0xFF140A06);
			g.fill(px + 1, py, px + 8, py + 2, col);
			px += 11;
		}
	}

	/** The needle toward the sanctuary the server found, turning with the player's view, and its distance. */
	private static void compassRow(GuiGraphicsExtractor g, Minecraft mc, int x, int y, long now) {
		var s = MatrioClient.state;
		var font = mc.font;
		if (mc.player.level().dimension() != Level.OVERWORLD) {
			g.text(font, Component.translatable("tutorial.matriochka.surface"), x, y + 2, Ui.MUTED, false);
			return;
		}
		if (!s.contains("tut_sx")) {
			if (s.getBooleanOr("f_tut_lost", false)) g.text(font, fit(font, Component.translatable("tutorial.matriochka.lost"), W - 37), x, y + 2, Ui.MUTED, false);
			return;
		}
		double dx = s.getIntOr("tut_sx", 0) + 0.5 - mc.player.getX(), dz = s.getIntOr("tut_sz", 0) + 0.5 - mc.player.getZ();
		// Minecraft yaw: 0 faces south (+z), 90 faces west (-x); the needle points up for straight ahead
		double bearing = Math.toDegrees(Math.atan2(-dx, dz));
		float rel = (float) Math.toRadians(net.minecraft.util.Mth.wrapDegrees(bearing - mc.player.getYRot()));
		int cx = x + 5, cy = y + 5;
		g.fill(cx - 5, cy - 5, cx + 6, cy + 6, 0xFF2A1408);
		g.fill(cx - 4, cy - 4, cx + 5, cy + 5, 0xFF4A2414);
		g.pose().pushMatrix();
		g.pose().translate(cx + 0.5f, cy + 0.5f);
		g.pose().rotate(rel + (float) Math.sin(now / 300.0) * 0.03f);
		Ui.sprite(g, "dial_needle", -1, -6, 2, 10);
		g.pose().popMatrix();
		int dist = (int) Math.round(Math.sqrt(dx * dx + dz * dz));
		Ui.embossed(g, font, Component.translatable("tutorial.matriochka.distance", dist), x + 15, y + 2, Math.abs(rel) < 0.35f ? Ui.OK : Ui.LIGHT);
	}

	private static Component fit(net.minecraft.client.gui.Font font, Component text, int w) {
		if (font.width(text) <= w) return text;
		return Component.literal(font.substrByWidth(text, w - font.width("...")).getString() + "...");
	}
}
