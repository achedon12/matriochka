package fr.achedon12.matriochka.client;

import java.util.List;
import net.fabricmc.fabric.api.client.screen.v1.ScreenEvents;
import net.fabricmc.fabric.api.client.screen.v1.Screens;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.options.OptionsScreen;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;

/**
 * A "Matriochka..." button on the game's Options screen, opening the comfort settings (ComfortScreen), whose Back
 * comes back to the Options. It shares the footer with Done: Done keeps the left half of its place and the button
 * takes the right half, so it covers neither vanilla's buttons nor those other mods add. When another mod has
 * already changed the footer, it goes to the top left corner instead, if that is free, and otherwise is left out
 * (Mod Menu's configure button opens the same screen).
 */
public final class OptionsButton {
	private static final int W = 98, H = 20;
	/** The last button placed, for the check run. */
	public static Button last;

	private OptionsButton() {}

	public static void init() {
		ScreenEvents.AFTER_INIT.register((mc, screen, w, h) -> {
			if (screen instanceof OptionsScreen) add(screen);
		});
	}

	private static void add(Screen screen) {
		List<AbstractWidget> widgets = Screens.getWidgets(screen);
		Button button = Button.builder(Component.translatable("options.matriochka.button"),
			b -> fr.achedon12.matriochka.client.mc.McClient.setScreen(net.minecraft.client.Minecraft.getInstance(), new ComfortScreen(screen))).size(W, H).build();
		AbstractWidget done = null;
		for (AbstractWidget wdg : widgets)
			if (wdg instanceof Button && wdg.getMessage().getString().equals(CommonComponents.GUI_DONE.getString())) done = wdg;
		if (done != null && done.getWidth() >= 2 * W + 4) {
			int x = done.getX() + done.getWidth() - W, y = done.getY();
			if (free(widgets, done, x, y)) {
				done.setWidth(done.getWidth() - W - 4);
				place(screen, button, x, y);
				return;
			}
		}
		if (free(widgets, null, 4, 4)) place(screen, button, 4, 4);
	}

	private static void place(Screen screen, Button button, int x, int y) {
		button.setX(x);
		button.setY(y);
		Screens.getWidgets(screen).add(button);
		last = button;
	}

	/** Whether nothing but {@code except} lies where the button would go. */
	private static boolean free(List<AbstractWidget> widgets, AbstractWidget except, int x, int y) {
		for (AbstractWidget wdg : widgets) {
			if (wdg == except || !wdg.visible) continue;
			if (x < wdg.getX() + wdg.getWidth() && x + W > wdg.getX() && y < wdg.getY() + wdg.getHeight() && y + H > wdg.getY()) return false;
		}
		return true;
	}
}
