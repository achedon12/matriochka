package fr.achedon12.matriochka.compat.modmenu;

import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;
import fr.achedon12.matriochka.client.InfoScreen;

/**
 * Mod Menu support: the "configure" button of Matriochka opens its info screen. Mod Menu loads this class through the
 * "modmenu" entrypoint, so without Mod Menu it is never touched and the mod does not need it.
 */
public class MatrioModMenu implements ModMenuApi {
	@Override
	public ConfigScreenFactory<?> getModConfigScreenFactory() {
		return InfoScreen::new;
	}
}
