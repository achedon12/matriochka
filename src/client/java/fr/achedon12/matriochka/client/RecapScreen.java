package fr.achedon12.matriochka.client;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.KeyEvent;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * The recap of a cycle, shown after an ending's crawl and reopened from the Journal. The great doll opens in two
 * halves: the head rises, the base sinks, and the parchment they held unrolls between them with the cycle's
 * numbers (the ending, the time, the bosses' cores in their sockets, deaths, layers, souls, dolls, pages, quests,
 * karma, class and the best Trial). F1 or the left button hides the buttons for a clean picture to share.
 */
public class RecapScreen extends Screen {
	/** The board, and how far the doll's halves stand out above and below it. */
	public static final int RW = 312, RH = 180, ABOVE = 24, BELOW = 20;
	private static final int DOLL_W = 56, HALF_H = 45, CLOSED_MS = 420, OPEN_MS = 800;
	private static final String[] CORES = {"guardian_core", "queen_core", "titan_core", "jailer_core", "storm_king_core", "light_eater_core",
		"double_core", "leviathan_core", "seasons_core", "terrain_core", "unfinished_core"};
	private final @Nullable Screen parent;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final long opened = Ui.now();
	private boolean clean;
	private long closing = -1;

	public RecapScreen(@Nullable Screen parent) {
		super(Component.translatable("recap.matriochka.title"));
		this.parent = parent;
	}

	public static boolean available() {
		return MatrioClient.state.get("last_cycle") instanceof CompoundTag c && !c.getStringOr("ending", "").isEmpty();
	}

	private static CompoundTag data() {
		return MatrioClient.state.getCompoundOrEmpty("last_cycle");
	}

	private String ending() {
		String e = data().getStringOr("ending", "seal");
		return e.equals("absorb") || e.equals("tools") ? e : "seal";
	}

	public boolean clean() {
		return clean;
	}

	/** Shows or hides the buttons (F1), for a screenshot. */
	public void toggleClean() {
		clean = !clean;
		Ui.sound(SoundEvents.BOOK_PAGE_TURN, 1.3f, 0.5f);
		rebuild();
	}

	private int left() { return (width - RW) / 2; }
	private int top() { return Math.max(ABOVE, (height - (RH + ABOVE + BELOW)) / 2 + ABOVE); }

	@Override
	protected void init() {
		if (Ui.now() - opened < 100) {
			Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, 0.85f, 0.8f);
			Ui.sound(SoundEvents.AMETHYST_BLOCK_RESONATE, 0.7f, 0.5f);
		}
		rebuild();
	}

	private void rebuild() {
		buttons.clear();
		if (clean) return;
		int l = left(), t = top();
		buttons.add(l + 12, t + RH + 3, 84, 16, Component.translatable("recap.matriochka.clean"), this::toggleClean);
		buttons.add(l + RW - 96, t + RH + 3, 84, 16, Component.translatable(parent != null ? "recap.matriochka.back" : "recap.matriochka.continue"), this::onClose);
	}

	@Override
	public void onClose() {
		if (closing >= 0) return;
		closing = Ui.now();
		Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_CLOSE, 0.9f, 0.6f);
	}

	@Override
	public void tick() {
		super.tick();
		if (closing >= 0 && Ui.now() - closing > 260) {
			closing = -1;
			minecraft.gui.setScreen(parent);
		}
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public net.minecraft.sounds.Music getBackgroundMusic() {
		return parent == null ? MusicThemes.ENDINGS : null;
	}

	/** 0 while the doll stands closed, 1 once its halves are apart. */
	private float open() {
		float v = Ui.easeInOut(Ui.since(opened + CLOSED_MS, OPEN_MS));
		if (closing >= 0) v *= 1 - Ui.easeIn(Ui.since(closing, 240));
		return v;
	}

	/** How far the content has appeared, for a row that comes in after delay ms. */
	private float shown(int delay) {
		if (closing >= 0) return 1 - Ui.since(closing, 160);
		return Ui.easeOut(Ui.since(opened + CLOSED_MS + OPEN_MS - 200 + delay, 380));
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top(), cx = l + RW / 2;
		float o = open();
		// the board unrolls between the halves: its visible band grows from the joint outwards
		int mid = t + RH / 2;
		int halfShown = Math.round(RH / 2f * o);
		if (halfShown > 0) {
			g.enableScissor(l - 2, mid - halfShown, l + RW + 2, mid + halfShown);
			Ui.sprite(g, "recap_panel", l, t, RW, RH);
			g.disableScissor();
		}
		// the halves: joined at the middle while closed, then at the board's top and bottom edges
		String kind = ending();
		float appear = Ui.easeBack(Ui.since(opened, 360));
		if (closing >= 0) appear *= 1 - Ui.easeIn(Ui.since(closing, 260));
		int cutClosed = mid - 2, cutOpen = t + 20;
		int topCut = Math.round(cutClosed + (cutOpen - cutClosed) * o);
		int rimClosed = mid - 2, rimOpen = t + RH - 21;
		int botRim = Math.round(rimClosed + (rimOpen - rimClosed) * o);
		g.pose().pushMatrix();
		g.pose().translate(cx, mid);
		float s = 0.7f + 0.3f * appear;
		g.pose().scale(s, s);
		g.pose().translate(-cx, -mid);
		int alphaCol = Ui.white(Ui.clamp01(appear * 1.4f));
		// a soft shadow under the base
		g.fill(cx - 22, botRim + HALF_H - 5, cx + 22, botRim + HALF_H - 3, Ui.alpha(0xFF000000, 0.35f * appear));
		Ui.sprite(g, "recap_" + kind + "_bottom", cx - DOLL_W / 2, botRim - 5, DOLL_W, HALF_H, alphaCol);
		Ui.sprite(g, "recap_" + kind + "_top", cx - DOLL_W / 2, topCut - 44, DOLL_W, HALF_H, alphaCol);
		g.pose().popMatrix();
		// a glint runs round the gilt once the board is open
		if (o >= 1) Ui.wanderingGlint(g, new int[][]{{l + 3, t + 3}, {l + RW - 4, t + 3}, {l + 3, t + RH - 4}, {l + RW - 4, t + RH - 4}, {cx - 18, t + 4}, {cx + 20, t + 7}}, 1900, 29);
		// the moment the halves part, a burst of light from the joint
		float burst = Ui.since(opened + CLOSED_MS - 60, 700);
		if (burst > 0 && burst < 1 && closing < 0) {
			Ui.sprite(g, "glow", cx - 60, mid - 30, 120, 60, Ui.white(0.8f * (float) Math.sin(Math.PI * burst)));
			Ui.glint(g, cx - 14, mid - 2, burst, 18);
			Ui.glint(g, cx + 16, mid + 1, Ui.clamp01(burst * 1.2f - 0.1f), 12);
		}
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		int l = left(), t = top();
		if (open() > 0.98f || closing >= 0) content(g, l, t, mx, my);
		if (clean) signature(g, l, t);
		else if (open() >= 1 && closing < 0) buttons.draw(g, font, mx, my);
	}

	/** In the clean view, the mod's name and the player's under the board, where the buttons were. */
	private void signature(GuiGraphicsExtractor g, int l, int t) {
		float a = shown(0);
		Ui.sprite(g, "doll_small_full", l + 14, t + RH + 5, 8, 11, Ui.white(a));
		Ui.embossed(g, font, Component.literal("Matriochka"), l + 26, t + RH + 7, Ui.alpha(Ui.GOLD, a));
		Component who = Component.literal(data().getStringOr("name", minecraft.player != null ? minecraft.player.getGameProfile().name() : ""));
		Ui.embossed(g, font, who, l + RW - 14 - font.width(who), t + RH + 7, Ui.alpha(Ui.MUTED, a));
	}

	private void content(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		CompoundTag d = data();
		String kind = ending();
		int cx = l + RW / 2;
		// the ending, and the cycle with its time
		float a0 = shown(0);
		g.pose().pushMatrix();
		g.pose().translate(cx, t + 25);
		Component name = Component.translatable("ending.matriochka." + kind);
		float sc = Math.min(1.25f, 230f / Math.max(1, font.width(name)));
		g.pose().scale(sc, sc);
		g.text(font, name, -font.width(name) / 2, 0, Ui.alpha(Ui.RED_INK, a0), false);
		g.pose().popMatrix();
		int cycle = d.getIntOr("cycle", 0) + 1;
		Component sub = d.getIntOr("members", 1) > 1 ? Component.translatable("recap.matriochka.sub_group", cycle, d.getIntOr("members", 1))
			: Component.translatable("recap.matriochka.sub", cycle);
		Ui.fitted(g, font, sub, cx, t + 37, 250, Ui.alpha(Ui.INK_SOFT, a0), false);
		// the line of the ending
		float a1 = shown(120);
		Component line = Component.translatable("recap.matriochka.line." + kind).withStyle(ChatFormatting.ITALIC);
		// two lines at most: a longer language writes smaller rather than run into the cores
		float ls = 1f;
		List<net.minecraft.util.FormattedCharSequence> lines = font.split(line, 262);
		for (float tryS : new float[]{1f, 0.875f, 0.75f}) {
			ls = tryS;
			lines = font.split(line, Math.round(262 / tryS));
			if (lines.size() <= 2 || lines.size() * 9 * tryS <= 21) break;
		}
		g.pose().pushMatrix();
		g.pose().translate(cx, t + 48);
		g.pose().scale(ls, ls);
		for (int i = 0; i < lines.size(); i++) g.text(font, lines.get(i), -font.width(lines.get(i)) / 2, i * 9, Ui.alpha(Ui.INK, a1), false);
		g.pose().popMatrix();
		bosses(g, cx, t + 70, d, mx, my);
		stats(g, l, t + 94, d);
	}

	/** The eleven bosses' cores in gilt sockets, lit for those beaten during the cycle (by the player or the group). */
	private void bosses(GuiGraphicsExtractor g, int cx, int y, CompoundTag d, int mx, int my) {
		int beaten = d.getIntOr("bosses", 0) | d.getIntOr("group_bosses", 0);
		int step = 22, x0 = cx - (11 * step - 4) / 2;
		String hover = null;
		for (int w = 0; w <= 10; w++) {
			int x = x0 + w * step;
			float a = shown(260 + w * 70);
			if (a <= 0) continue;
			boolean on = (beaten & (1 << w)) != 0;
			if (on) Ui.sprite(g, "glow", x - 4, y - 4, 26, 26, Ui.white(0.45f * a));
			Ui.sprite(g, "slot", x, y, 18, 18, Ui.white(a));
			g.pose().pushMatrix();
			float pop = Ui.easeBack(a);
			g.pose().translate(x + 9, y + 9);
			g.pose().scale(pop, pop);
			g.fakeItem(new ItemStack(fr.achedon12.matriochka.content.ModContent.item(CORES[w])), -8, -8);
			g.pose().popMatrix();
			if (!on) g.fill(x + 1, y + 1, x + 17, y + 17, Ui.alpha(0xD0180C08, a));
			else {
				float gl = Ui.since(opened + CLOSED_MS + OPEN_MS + 200 + w * 70L, 600);
				if (gl > 0 && gl < 1) Ui.glint(g, x + 5, y + 4, gl, 10);
			}
			g.fill(x + 6, y + 19, x + 12, y + 20, Ui.alpha(on ? Ui.worldColor(w) : 0x60605048, a));
			if (mx >= x && mx < x + 18 && my >= y && my < y + 18) {
				hover = (on ? "+" : "-") + w;
				g.outline(x - 1, y - 1, 20, 20, 0xFFF4D27A);
			}
		}
		if (hover != null && !clean) {
			int w = Integer.parseInt(hover.substring(1));
			List<Component> tip = new ArrayList<>();
			tip.add(Component.translatable("entity.matriochka." + fr.achedon12.matriochka.entity.MatrioBoss.byWorld(w).id()).withStyle(ChatFormatting.GOLD));
			tip.add((w == 0 ? Component.translatable("journal.matriochka.surface") : Component.translatable("hud.matriochka.world", w)).withStyle(ChatFormatting.GRAY));
			tip.add(Component.translatable(hover.startsWith("+") ? "recap.matriochka.boss.beaten" : "recap.matriochka.boss.standing")
				.withStyle(hover.startsWith("+") ? ChatFormatting.GREEN : ChatFormatting.DARK_GRAY));
			g.setComponentTooltipForNextFrame(font, tip, mx, my);
		}
	}

	private record Stat(Component label, Component value, int color) {}

	/** Two ledger columns of label, dotted leader and value, each line arriving after the one above it. */
	private void stats(GuiGraphicsExtractor g, int l, int y, CompoundTag d) {
		List<Stat> left = new ArrayList<>(), right = new ArrayList<>();
		int worlds = Integer.bitCount(d.getIntOr("worlds", 0) & 0x7FE);
		int bosses = Integer.bitCount((d.getIntOr("bosses", 0) | d.getIntOr("group_bosses", 0)) & 0x7FF);
		left.add(stat("worlds", Component.literal(worlds + " / 10"), Ui.INK));
		left.add(stat("bosses", Component.literal(bosses + " / 11"), Ui.INK));
		left.add(stat("deaths", Component.literal(Integer.toString(d.getIntOr("deaths", 0))), d.getIntOr("deaths", 0) == 0 ? Ui.GREEN : Ui.INK));
		left.add(stat("layers", Component.literal(d.getIntOr("lost", 0) + " / " + d.getIntOr("rebuilt", 0)), Ui.INK));
		left.add(stat("souls", Component.literal(String.format(java.util.Locale.ROOT, "%,d", d.getIntOr("souls", 0)).replace(',', ' ')), Ui.RED_INK));
		left.add(stat("time", Component.literal(time(d.getIntOr("ticks", 0))), Ui.INK));
		right.add(stat("dolls", Component.literal(Math.min(10, d.getIntOr("dolls", 0)) + " / 10"), Ui.INK));
		right.add(stat("pages", Component.translatable("recap.matriochka.of_total", d.getIntOr("pages", 0), d.getIntOr("pages_total", 0), 50), Ui.INK));
		right.add(stat("quests", Component.translatable("recap.matriochka.of_total", d.getIntOr("quests", 0), d.getIntOr("quests_total", 0), d.getIntOr("quests_all", 70)), Ui.INK));
		int k = d.getIntOr("karma", 0);
		String tier = k >= 50 ? "light2" : k >= 25 ? "light1" : k <= -50 ? "dark2" : k <= -25 ? "dark1" : "neutral";
		right.add(stat("karma", Component.translatable("recap.matriochka.karma_value", (k > 0 ? "+" : "") + k, Component.translatable("recap.matriochka.karma." + tier)),
			k >= 25 ? Ui.GREEN : k <= -25 ? 0xFF6A2A7A : Ui.INK));
		String cls = d.getStringOr("cls", "");
		right.add(stat("class", cls.isEmpty() ? Component.translatable("recap.matriochka.no_class")
			: Component.translatable("recap.matriochka.class_value", Component.translatable("class.matriochka." + cls), d.getIntOr("gear", 1)), Ui.INK));
		right.add(stat("trial", trial(d), Ui.INK));
		int colW = 128, gap = 12, x0 = l + RW / 2 - colW - gap / 2, x1 = l + RW / 2 + gap / 2;
		for (int i = 0; i < left.size(); i++) row(g, left.get(i), x0, y + i * 10, colW, shown(500 + i * 90));
		for (int i = 0; i < right.size(); i++) row(g, right.get(i), x1, y + i * 10, colW, shown(545 + i * 90));
		// a gold thread between the columns
		float a = shown(500);
		for (int yy = y; yy < y + 58; yy += 3) g.fill(l + RW / 2, yy, l + RW / 2 + 1, yy + 1, Ui.alpha(0xFFB0782A, 0.7f * a));
	}

	private static Stat stat(String key, Component value, int color) {
		return new Stat(Component.translatable("recap.matriochka.stat." + key), value, color);
	}

	private void row(GuiGraphicsExtractor g, Stat s, int x, int y, int w, float a) {
		if (a <= 0) return;
		int dx = Math.round((1 - a) * 6);
		int vw = font.width(s.value());
		int room = w - vw - 6;
		int lw = font.width(s.label());
		float sc = lw > room ? Math.max(0.6f, room / (float) lw) : 1f;
		g.pose().pushMatrix();
		g.pose().translate(x + dx, y + 4);
		g.pose().scale(sc, sc);
		g.text(font, s.label(), 0, -4, Ui.alpha(Ui.INK_SOFT, a), false);
		g.pose().popMatrix();
		int lend = x + dx + Math.round(lw * sc) + 3;
		for (int xx = lend; xx < x + w - vw - 3; xx += 2) g.fill(xx, y + 7, xx + 1, y + 8, Ui.alpha(0x806E4E36, a));
		g.text(font, s.value(), x + w - vw, y, Ui.alpha(s.color(), a), false);
	}

	/** The best Trial run of the cycle, or a dash. */
	private static Component trial(CompoundTag d) {
		int best = 0, rank = -1;
		String key = "";
		for (Tag tag : d.getListOrEmpty("trials")) {
			if (!(tag instanceof CompoundTag e)) continue;
			int ticks = e.getIntOr("ticks", 0);
			// the Gauntlet weighs most, then the later worlds
			String k = e.getStringOr("key", "");
			int r = k.equals("gauntlet") ? 100 : parse(k.substring(Math.min(1, k.length())));
			if (ticks > 0 && r > rank) {
				best = ticks;
				key = k;
				rank = r;
			}
		}
		if (key.isEmpty()) return Component.translatable("recap.matriochka.none");
		Component name = key.equals("gauntlet") ? Component.translatable("trials.matriochka.gauntlet") : Component.translatable("hud.matriochka.world", key.substring(1));
		return Component.translatable("recap.matriochka.trial_value", name, clock(best));
	}

	private static int parse(String s) {
		try {
			return Integer.parseInt(s);
		} catch (NumberFormatException e) {
			return 0;
		}
	}

	private static String clock(int ticks) {
		int s = ticks / 20;
		return String.format(java.util.Locale.ROOT, "%d:%02d.%d", s / 60, s % 60, (ticks % 20) / 2);
	}

	/** Play time as hours and minutes ("3 h 07"), or minutes and seconds under an hour. */
	private static String time(int ticks) {
		int s = ticks / 20, h = s / 3600, m = (s / 60) % 60;
		return h > 0 ? String.format(java.util.Locale.ROOT, "%d h %02d", h, m) : String.format(java.util.Locale.ROOT, "%d min %02d", m, s % 60);
	}

	// ---------------------------------------------------------------- input
	@Override
	public boolean keyPressed(KeyEvent event) {
		// F1, as the game hides its own HUD
		if (event.key() == com.mojang.blaze3d.platform.InputConstants.KEY_F1) {
			toggleClean();
			return true;
		}
		return super.keyPressed(event);
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (closing >= 0) return true;
		if (clean) {
			toggleClean();
			return true;
		}
		if (open() >= 1 && buttons.click(event.x(), event.y())) return true;
		return super.mouseClicked(event, doubleClick);
	}
}
