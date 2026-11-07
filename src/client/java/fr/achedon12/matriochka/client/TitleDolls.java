package fr.achedon12.matriochka.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;

/**
 * On the title screen, above the version line in the bottom left corner: the five painted nesting dolls of the
 * Journal standing in a row, rocking gently one after the other, and "Matriochka" with the mod's version beside
 * them. Nothing else of the title screen changes.
 */
public final class TitleDolls {
	private TitleDolls() {}

	private static final int[] W = {14, 12, 10, 8, 6}, H = {21, 18, 15, 12, 9};
	private static String version;

	public static void draw(GuiGraphicsExtractor g) {
		var font = Minecraft.getInstance().font;
		if (version == null) version = net.fabricmc.loader.api.FabricLoader.getInstance().getModContainer("matriochka")
			.map(c -> c.getMetadata().getVersion().getFriendlyString()).orElse("");
		int base = g.guiHeight() - 14, x = 4;
		long t = Ui.now();
		for (int i = 0; i < 5; i++) {
			// a slow rock that runs down the row, the smaller dolls following the larger
			double ph = (t / 900.0 - i * 0.35) % (Math.PI * 2);
			float rock = (float) Math.max(0, Math.sin(ph)) * 0.12f;
			g.pose().pushMatrix();
			g.pose().translate(x + W[i] / 2f, base);
			g.pose().rotate(rock * (i % 2 == 0 ? 1 : -1));
			Ui.sprite(g, "nest_" + i, -W[i] / 2, -H[i], W[i], H[i]);
			g.pose().popMatrix();
			x += W[i] + 1;
		}
		Component name = Component.literal("Matriochka " + version);
		g.text(font, name, x + 4, base - 8, 0xFFEFCB72, true);
	}
}
