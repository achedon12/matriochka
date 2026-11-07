package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import net.minecraft.advancements.AdvancementType;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.toasts.Toast;
import net.minecraft.client.gui.components.toasts.ToastManager;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;

/**
 * A Matriochka advancement, announced on the mod's own card: the lacquer frame of its screens, the rule icon of the
 * world it belongs to (a doll for the Surface's), what kind of feat it is in gold, and its title. A challenge gets a
 * red plate, a gilt rim that catches the light, and the challenge fanfare.
 */
public final class MatrioToast implements Toast {
	private static final long SHOWN_MS = 5000;
	private final int world;
	private final DisplayInfo display;
	private Visibility wanted = Visibility.SHOW;

	public MatrioToast(String path, DisplayInfo display) {
		this.display = display;
		int w = 0;
		if (path.startsWith("world_")) {
			try {
				w = Integer.parseInt(path.substring(6, path.indexOf('/') > 0 ? path.indexOf('/') : path.length()));
			} catch (NumberFormatException ignored) {
				w = 0;
			}
		}
		this.world = w >= 1 && w <= Content.WORLDS.size() ? w : 0;
	}

	@Override
	public Visibility getWantedVisibility() {
		return wanted;
	}

	@Override
	public void update(ToastManager manager, long visibleMs) {
		wanted = visibleMs >= SHOWN_MS * manager.getNotificationDisplayTimeMultiplier() ? Visibility.HIDE : Visibility.SHOW;
	}

	@Override
	public SoundEvent getSoundEvent() {
		return fr.achedon12.matriochka.client.mc.McClient.type(display) == AdvancementType.CHALLENGE ? SoundEvents.UI_TOAST_CHALLENGE_COMPLETE : null;
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, Font font, long visibleMs) {
		boolean challenge = fr.achedon12.matriochka.client.mc.McClient.type(display) == AdvancementType.CHALLENGE;
		int w = width(), h = height();
		Ui.sprite(g, "frame", 0, 0, w, h);
		// the world's plate behind the icon
		Ui.sprite(g, "plate_" + world, 5, 6, 22, 20);
		if (world > 0) Ui.sprite(g, "rule_" + Content.WORLDS.get(world - 1).rule(), 8, 8, 16, 16);
		else Ui.sprite(g, "doll_small_full", 10, 7, 12, 18);
		Component kind = fr.achedon12.matriochka.client.mc.McClient.type(display).getDisplayName();
		g.text(font, kind, 32, 7, challenge ? 0xFFFF8C6E : Ui.GOLD, false);
		String title = font.plainSubstrByWidth(fr.achedon12.matriochka.client.mc.McClient.title(display).getString(), w - 40);
		g.text(font, Component.literal(title), 32, 18, 0xFFF4E8D0, false);
		if (challenge) {
			// a glint running round the gilt rim
			int per = 2 * (w + h), at = (int) (visibleMs / 6 % per);
			int gx = at < w ? at : at < w + h ? w - 2 : at < 2 * w + h ? w - (at - w - h) : 1;
			int gy = at < w ? 1 : at < w + h ? at - w : at < 2 * w + h ? h - 2 : h - (at - 2 * w - h);
			g.fill(gx, gy, gx + 2, gy + 1, 0xFFFFF4C0);
			g.fill(gx, gy, gx + 1, gy + 2, 0xFFFFF4C0);
		}
	}
}
