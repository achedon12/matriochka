package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.item.ItemTip;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.tooltip.ClientTooltipComponent;
import net.minecraft.network.chat.Component;

/**
 * The strip of pixel icons under a Matriochka item's name: the world's rule icon and "World N" in the world's colour,
 * a gem of the rarity's colour and its name, and a soul with the souls the item is worth (or holds).
 */
public record ItemTipClient(ItemTip tip) implements ClientTooltipComponent {
	private static final int ICON = 9, GAP = 8;

	private Component world() {
		return tip.world() > 0 && tip.world() <= Content.WORLDS.size() ? Component.translatable("tooltip.matriochka.world", tip.world()) : null;
	}

	private Component rarity() {
		return Component.translatable("rarity.matriochka." + tip.rarity());
	}

	private Component souls() {
		return tip.souls() > 0 || tip.holds() ? Component.literal((tip.holds() ? "" : "+") + tip.souls()) : null;
	}

	private static int rarityColor(String r) {
		return switch (r) {
			case "rare" -> 0xFF5AD2F0;
			case "epic" -> 0xFFD26EF0;
			case "legendary" -> 0xFFFAC43C;
			default -> 0xFFE0E0E6;
		};
	}

	@Override
	public int getHeight(Font font) {
		return ICON + 3;
	}

	@Override
	public int getWidth(Font font) {
		int w = 0;
		for (Component c : new Component[]{world(), rarity(), souls()}) if (c != null) w += (w > 0 ? GAP : 0) + ICON + 2 + font.width(c);
		return w;
	}

	@Override
	public void extractImage(Font font, int x, int y, int width, int height, GuiGraphicsExtractor g) {
		int cx = x;
		Component w = world();
		if (w != null) {
			Ui.sprite(g, "rule_" + Content.WORLDS.get(tip.world() - 1).rule(), cx, y, ICON, ICON);
			cx += ICON + 2;
			g.text(font, w, cx, y + 1, 0xFF000000 | Ui.worldColor(tip.world()), true);
			cx += font.width(w) + GAP;
		}
		Ui.sprite(g, "tip_gem_" + switch (tip.rarity()) {
			case "rare", "epic", "legendary" -> tip.rarity();
			default -> "common";
		}, cx, y, ICON, ICON);
		cx += ICON + 2;
		Component r = rarity();
		g.text(font, r, cx, y + 1, rarityColor(tip.rarity()), true);
		cx += font.width(r) + GAP;
		Component s = souls();
		if (s != null) {
			Ui.sprite(g, "tip_soul", cx, y, ICON, ICON);
			g.text(font, s, cx + ICON + 2, y + 1, 0xFF9ADCF0, true);
		}
	}
}
