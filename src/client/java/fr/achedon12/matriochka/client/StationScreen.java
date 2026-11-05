package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.net.StationMenu;
import java.util.List;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * A station is a lacquered cabinet painted for its world: recipes are drawers that slide in when it opens and pull
 * out under the cursor, each with a gilded groove that fills as you gather its ingredients. The machine's state is
 * a glass doll in the niche on the right, its liquid rising with the station's condition.
 */
public class StationScreen extends AbstractContainerScreen<StationMenu> {
	private static final String[] PINS = {"I", "II", "III", "IV"};
	private static final int ROWS = 5, ROW_H = 22, CAB_X = 12, CAB_Y = 22;
	private final List<Recipes.Recipe> recipes;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(300, 160);
	private final int world;
	private int scroll;
	private float scrollShown, fillShown, flash;
	private final float[] pull, progress;
	private final long[] pressed;
	private boolean wasReady;
	private long readyAt = -1, last = Ui.now();

	public StationScreen(StationMenu menu, Inventory inv, Component title) {
		super(menu, inv, title, StationMenu.PANEL_W, StationMenu.PANEL_H);
		this.recipes = Recipes.of(menu.data.station());
		this.world = Ui.stationWorld(menu.data.station());
		this.inventoryLabelY = 128;
		this.inventoryLabelX = 48;
		this.pull = new float[recipes.size()];
		this.progress = new float[recipes.size()];
		this.pressed = new long[recipes.size()];
		java.util.Arrays.fill(pressed, -1);
	}

	private void click(int id) {
		minecraft.gameMode.handleInventoryButtonClick(menu.containerId, id);
	}

	private boolean hasSlot() {
		return menu.data.station().equals("soul_altar") || menu.data.station().equals("class_table");
	}

	private boolean jailer() {
		return menu.data.station().equals("jailer_table");
	}

	@Override
	protected void init() {
		super.init();
		if (Ui.now() - motion.openedAt() < 100) Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, 1f, 0.6f);
		buttons.clear();
		int l = leftPos, t = topPos;
		switch (menu.data.station()) {
			case "soul_altar" -> {
				buttons.add(l + 150, t + 30, 92, 18, Component.translatable("station.matriochka.purify"), () -> click(200));
				buttons.add(l + 150, t + 52, 92, 18, Component.translatable("station.matriochka.devour"), () -> click(201));
				buttons.add(l + 150, t + 74, 92, 18, Component.translatable("station.matriochka.recharge"), () -> click(202));
			}
			case "class_table" -> {
				buttons.add(l + 150, t + 38, 92, 18, Component.translatable("station.matriochka.upgrade"), () -> click(210));
				buttons.add(l + 150, t + 60, 92, 18, Component.translatable("station.matriochka.reroll"), () -> click(211));
				buttons.add(l + 150, t + 82, 92, 18, Component.translatable("station.matriochka.layer"), () -> click(212));
				// the talent trees open in their own cabinet
				buttons.add(l + 150, t + 117, 92, 16, Component.translatable("talents.matriochka.open"), () -> {
					minecraft.player.closeContainer();
					minecraft.gui.setScreen(new TalentScreen());
				});
			}
			case "abyssal_press" -> buttons.add(l + 199, t + 113, 46, 16, Component.translatable("station.matriochka.refill"), () -> click(220));
			case "inverter" -> buttons.add(l + 199, t + 52, 46, 16, Component.translatable("station.matriochka.invert"), () -> click(220));
			case "jailer_table" -> {
				for (int i = 0; i < 4; i++) {
					int pin = i;
					buttons.add(l + 199 + (i % 2) * 24, t + 92 + (i / 2) * 20, 22, 18, Component.literal(PINS[i]), () -> click(100 + pin));
				}
			}
			default -> {}
		}
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_CLOSE, 1.05f, 0.55f);
		motion.close(super::onClose);
	}

	@Override
	protected void containerTick() {
		super.containerTick();
		motion.tick();
	}

	private int[] have(Recipes.Recipe r) {
		int need = 0, got = 0;
		for (Recipes.Ing ing : r.inputs()) {
			need += ing.count();
			got += Math.min(ing.count(), Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())));
		}
		return new int[]{got, need};
	}

	private float condition(boolean ready) {
		return switch (menu.data.station()) {
			case "ash_foundry" -> Math.min(1f, menu.sync.get(1) / 3f);
			case "lightning_forge" -> menu.sync.get(1) / 8f;
			case "spore_vat" -> menu.sync.get(6) / 300f;
			case "jailer_table" -> menu.sync.get(5) / 3f;
			default -> ready ? 1f : 0f;
		};
	}

	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		int l = leftPos, t = topPos;
		motion.push(g, l + imageWidth / 2f, t + imageHeight / 2f);
		Ui.sprite(g, "station_" + menu.data.station(), l, t, imageWidth, imageHeight);
		Ui.plate(g, font, title, l + imageWidth / 2, t + 1, world, l * 7L);
		for (Slot s : menu.slots) Ui.sprite(g, "slot", l + s.x - 1, t + s.y - 1, 18, 18);
		Ui.wanderingGlint(g, new int[][]{{l + 3, t + 3}, {l + imageWidth - 4, t + 3}, {l + 3, t + imageHeight - 4}, {l + imageWidth - 4, t + imageHeight - 4},
			{l + 20, t + imageHeight - 3}, {l + 236, t + imageHeight - 3}, {l + 22, t + 141}, {l + 234, t + 141}}, 1500, world * 97L);
		boolean ready = menu.sync.get(0) == 1;
		if (hasSlot()) {
			altar(g, l, t);
		} else {
			drawers(g, l, t, mx, my, dt);
			niche(g, l, t, ready, dt, mx, my);
		}
		motion.pop(g);
	}

	private void altar(GuiGraphicsExtractor g, int l, int t) {
		Ui.paper(g, l + 12, t + 22, 128, 100);
		g.textWithWordWrap(font, Component.translatable("station.matriochka." + menu.data.station() + ".help"), l + 18, t + 28, 96, Ui.INK, false);
		Ui.sprite(g, "slot", l + 119, t + 69, 18, 18);
		// a soft halo pulses round the item socket
		float pulse = 0.25f + 0.2f * (float) Math.sin(Ui.now() / 420.0);
		Ui.sprite(g, "glow", l + 116, t + 66, 24, 24, Ui.white(pulse));
		// the souls the altar and the class table work with
		int souls = MatrioClient.state.getIntOr("souls", 0);
		Ui.sprite(g, "lantern", l + 160, t + 100, 9, 13);
		JournalScreen.lanternFlame(g, l + 160, t + 100, 1f);
		Ui.embossed(g, font, Component.translatable("hud.matriochka.souls", souls), l + 174, t + 103, Ui.GOLD);
	}

	private void drawers(GuiGraphicsExtractor g, int l, int t, int mx, int my, float dt) {
		scrollShown = Ui.approach(scrollShown, scroll, 16, dt);
		int x0 = l + CAB_X, y0 = t + CAB_Y;
		g.enableScissor(l + 10, t + 20, l + 188, t + 133);
		int first = Math.max(0, (int) Math.floor(scrollShown));
		for (int i = first; i < recipes.size() && i < first + ROWS + 1; i++) {
			Recipes.Recipe r = recipes.get(i);
			int y = y0 + Math.round((i - scrollShown) * ROW_H);
			boolean hover = !motion.closing() && mx >= x0 && mx < x0 + 174 && my >= Math.max(y, t + 20) && my < Math.min(y + 21, t + 133);
			int[] hv = have(r);
			boolean can = hv[0] >= hv[1];
			pull[i] = Ui.approach(pull[i], hover ? 1 : 0, 14, dt);
			progress[i] = Ui.approach(progress[i], hv[1] == 0 ? 1 : hv[0] / (float) hv[1], 6, dt);
			// slides in from the left when the cabinet opens, one drawer after the other
			int row = i - scroll;
			float in = Ui.easeOut(Ui.since(motion.openedAt() + 40L + Math.max(0, row) * 45L, 260));
			int slideIn = Math.round((1 - in) * -190);
			float press = pressed[i] < 0 ? 0 : 1 - Ui.since(pressed[i], 180);
			int dx = slideIn + Math.round(pull[i] * 4 - press * 3);
			if (dx > 0) Ui.sprite(g, "drawer_side", x0, y + 1, dx + 2, 19);
			int x = x0 + dx;
			// the drawer lifts: a shadow under it while pulled out
			if (pull[i] > 0.02f) g.fill(x + 2, y + 21, x + 176, y + 22, Ui.alpha(0xFF000000, 0.45f * pull[i]));
			Ui.sprite(g, can ? "drawer_ready" : "drawer", x, y, 174, 21);
			if (pull[i] > 0.02f) {
				g.fill(x + 1, y + 1, x + 173, y + 20, Ui.alpha(0xFFFFE6B0, 0.10f * pull[i]));
				g.outline(x, y, 174, 21, Ui.alpha(0xFFF4D27A, pull[i]));
			}
			g.item(new ItemStack(Stations.resolve(r.output()), r.count()), x + 9, y + 2);
			g.itemDecorations(font, new ItemStack(Stations.resolve(r.output()), r.count()), x + 9, y + 2);
			int ix = x + 40;
			for (Recipes.Ing ing : r.inputs()) {
				ItemStack s = new ItemStack(Stations.resolve(ing.id()), ing.count());
				g.item(s, ix, y + 2);
				g.itemDecorations(font, s, ix, y + 2);
				if (Stations.count(minecraft.player.getInventory(), Stations.resolve(ing.id())) < ing.count()) {
					g.fill(ix, y + 2, ix + 16, y + 18, 0x9C140A08);
					g.fill(ix, y + 17, ix + 16, y + 18, 0xFFD8402A);
				}
				ix += 21;
			}
			// the gilded groove fills with what you already carry; full, it shines
			int fw = Math.round(124 * Ui.clamp01(progress[i]));
			Ui.spritePart(g, "drawer_fill", 124, 2, 0, 0, x + 38, y + 18, fw, 1, 0xFFFFFFFF);
			if (can) Ui.sheen(g, x + 38, y + 16, 124, 4, 2600, i * 431L, 0.9f);
			if (can && hover) Ui.sheen(g, x + 3, y + 3, 30, 15, 1400, i * 211L, 0.6f);
		}
		g.disableScissor();
		if (recipes.size() > ROWS) {
			int track = 108, th = Math.max(12, track * ROWS / recipes.size());
			int ty = t + 22 + Math.round((track - th) * scrollShown / Math.max(1, recipes.size() - ROWS));
			Ui.sprite(g, "thumb", l + 189, ty, 4, th);
		}
	}

	/** The Inverter's niche: two sockets facing each other, the swap mark between them, the warning below. */
	private void inverterNiche(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		int ax = l + StationMenu.INVERTER_A_X, bx = l + StationMenu.INVERTER_B_X, y = t + StationMenu.INVERTER_Y;
		float pulse = 0.2f + 0.15f * (float) Math.sin(Ui.now() / 380.0);
		Ui.sprite(g, "glow", ax - 4, y - 4, 24, 24, Ui.white(pulse));
		Ui.sprite(g, "glow", bx - 4, y - 4, 24, 24, Ui.white(0.35f - pulse));
		Component swap = Component.literal("<>");
		Ui.embossed(g, font, swap, (ax + 16 + bx) / 2 - font.width(swap) / 2, y + 4, Ui.GOLD);
		Component desc = Component.translatable("station.matriochka.inverter.help");
		var lines = font.split(desc, 50);
		for (int i = 0; i < Math.min(6, lines.size()); i++) g.text(font, lines.get(i), l + 198, t + 74 + i * 9, Ui.MUTED, false);
		if (lines.size() > 6 && mx >= l + 195 && mx < l + 248 && my >= t + 70 && my < t + 133) g.setTooltipForNextFrame(font, desc, mx, my);
	}

	private void niche(GuiGraphicsExtractor g, int l, int t, boolean ready, float dt, int mx, int my) {
		if (menu.data.station().equals("inverter")) {
			inverterNiche(g, l, t, mx, my);
			return;
		}
		if (ready && !wasReady) {
			readyAt = Ui.now();
			if (Ui.now() - motion.openedAt() > 400) Ui.sound(SoundEvents.AMETHYST_BLOCK_CHIME, 1.6f, 0.6f);
		}
		wasReady = ready;
		float target = Ui.clamp01(condition(ready));
		if (Math.abs(target - fillShown) > 0.02f && target > fillShown) flash = 1;
		fillShown = Ui.approach(fillShown, target * Ui.easeOut(Ui.since(motion.openedAt() + 150, 500)), 4, dt);
		flash = Ui.approach(flash, 0, 3, dt);
		int vx = l + 202, vy = t + 23, vw = 40, vh = 56;
		Ui.sprite(g, "vessel_back", vx, vy, vw, vh);
		// liquid: the body of the doll spans rows 8..48 of the sprite; the surface wobbles a little
		int top = vy + 8, bottom = vy + 48;
		int level = bottom - Math.round((bottom - top) * fillShown);
		int liquid = Ui.worldColor(world);
		if (fillShown > 0.01f) {
			int wob = Math.round((float) Math.sin(Ui.now() / 300.0) * 0.7f);
			int lv = Math.min(bottom, level + wob);
			Ui.spritePart(g, "vessel_liquid", vw, vh, 0, lv - vy, vx, lv, vw, bottom - lv, liquid);
			g.fill(vx + 6, lv, vx + vw - 6, lv + 1, Ui.white(0.25f));
			long tt = Ui.now();
			for (int b = 0; b < 3; b++) {
				float p = Math.floorMod(tt + b * 777L, 2300L) / 2300f;
				int by = Math.round(bottom - 2 - p * (bottom - lv - 2));
				int bx = vx + 14 + b * 5 + Math.round((float) Math.sin(p * 9 + b) * 1.5f);
				if (by > lv + 1) Ui.sprite(g, "bubble", bx, by, 3, 3, Ui.white(0.7f * (1 - p)));
			}
			if (flash > 0.01f) Ui.spritePart(g, "vessel_liquid", vw, vh, 0, lv - vy, vx, lv, vw, bottom - lv, Ui.white(0.5f * flash));
		}
		Ui.sprite(g, "vessel_front", vx, vy, vw, vh);
		if (ready) {
			float since = readyAt < 0 ? 1 : Ui.since(readyAt, 900);
			Ui.sprite(g, "glow", vx + 8, vy + 10, 24, 24, Ui.alpha(0xFFFFFFFF, 0.25f + 0.2f * (float) Math.sin(Ui.now() / 500.0) + (1 - since) * 0.5f));
			Ui.glint(g, vx + 13, vy + 18, Math.floorMod(Ui.now(), 2200L) / 900f, 8);
		}
		int sx = l + 198;
		if (!jailer()) {
			int ferment = menu.sync.get(6);
			Component st = menu.data.station().equals("spore_vat")
				? Component.translatable("station.matriochka.ferment." + (ferment >= 300 ? "aged" : ferment >= 60 ? "ripe" : "fresh"))
				: Component.translatable(ready ? "station.matriochka.ready" : "station.matriochka.not_ready");
			Ui.embossed(g, font, st, l + 222 - font.width(st) / 2, t + 82, ready ? Ui.OK : Ui.WARN);
			Component desc = Component.translatable("block.matriochka." + menu.data.station() + ".desc");
			var lines = font.split(desc, 50);
			// the press keeps room under its text for the button that refills snorkel helmets
			int shown = menu.data.station().equals("abyssal_press") ? 2 : 4;
			for (int i = 0; i < Math.min(shown, lines.size()); i++) g.text(font, lines.get(i), sx, t + 94 + i * 9, Ui.MUTED, false);
			if (lines.size() > shown && mx >= l + 195 && mx < l + 248 && my >= t + 20 && my < (shown == 2 ? t + 112 : t + 133)) g.setTooltipForNextFrame(font, desc, mx, my);
		} else {
			for (int i = 0; i < 3; i++) {
				boolean ok = i < menu.sync.get(5);
				Component pin = Component.literal(PINS[menu.sync.get(2 + i)]);
				int px = l + 204 + i * 14;
				g.fill(px - 2, t + 80, px + 11, t + 90, ok ? 0x6040A030 : 0x60200808);
				g.outline(px - 2, t + 80, 13, 10, ok ? 0xFFA8E07A : 0xFF96682A);
				Ui.embossed(g, font, pin, px + 5 - font.width(pin) / 2, t + 81, ok ? Ui.OK : Ui.WARN);
			}
		}
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		motion.push(g, leftPos + imageWidth / 2f, topPos + imageHeight / 2f);
		super.extractRenderState(g, mx, my, a);
		buttons.draw(g, font, mx, my);
		motion.pop(g);
	}

	@Override
	protected void extractLabels(GuiGraphicsExtractor g, int mx, int my) {
		// the title sits on the plate drawn with the background
	}

	@Override
	public boolean mouseScrolled(double x, double y, double sx, double sy) {
		scroll = Math.max(0, Math.min(Math.max(0, recipes.size() - ROWS), scroll - (int) Math.signum(sy)));
		return true;
	}

	@Override
	public boolean keyPressed(KeyEvent event) {
		if (motion.closing()) return true;
		return super.keyPressed(event);
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		if (!hasSlot()) {
			int l = leftPos, t = topPos;
			double mx = event.x(), my = event.y();
			if (mx >= l + CAB_X && mx < l + CAB_X + 174 && my >= t + CAB_Y && my < t + CAB_Y + ROW_H * ROWS) {
				int idx = scroll + (int) ((my - t - CAB_Y) / ROW_H);
				if (idx < recipes.size()) {
					pressed[idx] = Ui.now();
					Ui.sound(SoundEvents.WOODEN_BUTTON_CLICK_ON, 1.0f, 0.6f);
					click(idx);
					return true;
				}
			}
		}
		return super.mouseClicked(event, doubleClick);
	}
}
