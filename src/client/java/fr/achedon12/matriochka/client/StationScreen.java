package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.net.StationMenu;
import java.util.List;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * A station is a painted cabinet: recipes are drawers (a drawer turns green when you carry every ingredient), the
 * machine's state is a small doll on the right whose body fills with the station's condition.
 */
public class StationScreen extends AbstractContainerScreen<StationMenu> {
	private static final String[] PINS = {"I", "II", "III", "IV"};
	private final List<Recipes.Recipe> recipes;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private int scroll;

	public StationScreen(StationMenu menu, Inventory inv, Component title) {
		super(menu, inv, title, StationMenu.PANEL_W, StationMenu.PANEL_H);
		this.recipes = Recipes.of(menu.data.station());
		this.inventoryLabelY = 128;
		this.inventoryLabelX = 48;
	}

	private void click(int id) {
		minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
	}

	private boolean hasSlot() {
		return menu.data.station().equals("soul_altar") || menu.data.station().equals("class_table");
	}

	@Override
	protected void init() {
		super.init();
		buttons.clear();
		int l = leftPos, t = topPos;
		switch (menu.data.station()) {
			case "soul_altar" -> {
				buttons.add(l + 150, t + 34, 92, 18, Component.translatable("station.matriochka.purify"), () -> click(200));
				buttons.add(l + 150, t + 56, 92, 18, Component.translatable("station.matriochka.devour"), () -> click(201));
				buttons.add(l + 150, t + 78, 92, 18, Component.translatable("station.matriochka.recharge"), () -> click(202));
			}
			case "class_table" -> {
				buttons.add(l + 150, t + 44, 92, 18, Component.translatable("station.matriochka.upgrade"), () -> click(210));
				buttons.add(l + 150, t + 66, 92, 18, Component.translatable("station.matriochka.reroll"), () -> click(211));
			}
			case "jailer_table" -> {
				for (int i = 0; i < 4; i++) {
					int pin = i;
					buttons.add(l + 196 + (i % 2) * 24, t + 52 + (i / 2) * 20, 22, 18, Component.literal(PINS[i]), () -> click(100 + pin));
				}
			}
			default -> {}
		}
	}

	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = leftPos, t = topPos;
		Ui.frame(g, l, t, imageWidth, imageHeight);
		for (Slot s : menu.slots) Ui.sprite(g, "slot", l + s.x - 1, t + s.y - 1, 18, 18);
		boolean ready = menu.sync.get(0) == 1;
		if (hasSlot()) {
			Ui.paper(g, l + 12, t + 22, 128, 100);
			g.textWithWordWrap(font, Component.translatable("station.matriochka." + menu.data.station() + ".help"), l + 18, t + 28, 116, Ui.INK, false);
			Ui.sprite(g, "slot", l + 119, t + 69, 18, 18);
			return;
		}
		int y = t + 22;
		int rows = 0;
		for (int i = scroll; i < recipes.size() && rows < 5; i++, rows++) {
			Recipes.Recipe r = recipes.get(i);
			boolean hover = mx >= l + 12 && mx < l + 186 && my >= y && my < y + 21;
			boolean can = true;
			for (Recipes.Ing ing : r.inputs()) if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) can = false;
			Ui.sprite(g, hover ? "drawer_hover" : can ? "drawer_ready" : "drawer", l + 12, y, 174, 21);
			g.item(new ItemStack(Stations.resolve(r.output()), r.count()), l + 16, y + 2);
			g.fill(l + 35, y + 4, l + 36, y + 17, 0xFF1E1410);
			int x = l + 40;
			for (Recipes.Ing ing : r.inputs()) {
				ItemStack s = new ItemStack(Stations.resolve(ing.id()), ing.count());
				g.item(s, x, y + 2);
				g.itemDecorations(font, s, x, y + 2);
				if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) g.fill(x, y + 2, x + 16, y + 18, 0xB01E1410);
				x += 21;
			}
			y += 22;
		}
		if (recipes.size() > 5) {
			int track = 108, th = Math.max(12, track * 5 / recipes.size());
			int ty = t + 22 + (track - th) * scroll / Math.max(1, recipes.size() - 5);
			g.fill(l + 189, t + 22, l + 192, t + 22 + track, 0xFF1E1410);
			g.fill(l + 189, ty, l + 192, ty + th, 0xFFE8C060);
		}
		// machine state: a painted doll whose body fills with the condition
		int sx = l + 198, sy = t + 24;
		Ui.paper(g, sx - 4, sy - 4, 52, 104);
		float fill = switch (menu.data.station()) {
			case "ash_foundry" -> Math.min(1f, menu.sync.get(1) / 3f);
			case "lightning_forge" -> menu.sync.get(1) / 8f;
			case "spore_vat" -> menu.sync.get(6) / 60f;
			case "jailer_table" -> menu.sync.get(5) / 3f;
			default -> ready ? 1f : 0f;
		};
		int body = ready ? 0xFFB3261E : 0xFF5A4A44;
		g.fill(sx + 8, sy + 2, sx + 36, sy + 16, body);
		g.fill(sx + 13, sy + 5, sx + 31, sy + 14, 0xFFF0D0B0);
		g.fill(sx + 4, sy + 16, sx + 40, sy + 50, body);
		int fh = Math.round(30 * Math.max(0, Math.min(1, fill)));
		g.fill(sx + 10, sy + 48 - fh, sx + 34, sy + 48, 0xFFE8C060);
		g.outline(sx + 3, sy + 1, 38, 50, 0xFF1E1410);
		if (!menu.data.station().equals("jailer_table")) {
			Component st = Component.translatable(ready ? "station.matriochka.ready" : "station.matriochka.not_ready");
			g.text(font, st, sx + 22 - font.width(st) / 2, sy + 56, ready ? Ui.GREEN : 0xFF8A2018, false);
			var lines = font.split(Component.translatable("block.matriochka." + menu.data.station() + ".desc"), 44);
			for (int i = 0; i < Math.min(3, lines.size()); i++) g.text(font, lines.get(i), sx, sy + 68 + i * 9, Ui.INK_SOFT, false);
		} else {
			for (int i = 0; i < 3; i++) {
				int col = i < menu.sync.get(5) ? Ui.GREEN : 0xFF8A2018;
				g.text(font, PINS[menu.sync.get(2 + i)], sx + 2 + i * 16, sy + 56, col, false);
			}
		}
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		buttons.draw(g, font, mx, my);
	}

	@Override
	protected void extractLabels(GuiGraphicsExtractor g, int mx, int my) {
		int w = font.width(title);
		g.text(font, title, imageWidth / 2 - w / 2 + 1, 4, 0xFF1E1410, false);
		g.text(font, title, imageWidth / 2 - w / 2, 3, Ui.GOLD, false);
	}

	@Override
	public boolean mouseScrolled(double x, double y, double sx, double sy) {
		scroll = Math.max(0, Math.min(Math.max(0, recipes.size() - 5), scroll - (int) Math.signum(sy)));
		return true;
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (buttons.click(event.x(), event.y())) return true;
		if (!hasSlot()) {
			int l = leftPos, t = topPos;
			double mx = event.x(), my = event.y();
			if (mx >= l + 12 && mx < l + 186 && my >= t + 22 && my < t + 22 + 22 * 5) {
				int idx = scroll + (int) ((my - t - 22) / 22);
				if (idx < recipes.size()) {
					click(idx);
					return true;
				}
			}
		}
		return super.mouseClicked(event, doubleClick);
	}
}
