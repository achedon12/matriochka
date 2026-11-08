package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.rules.Snorkel;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudStatusBarHeightRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;

/**
 * The world's rule as a vanilla status row: ten 9 x 9 icons on the right, right above the hunger bar, filling in
 * halves like the shanks (5% a half icon). It is a Fabric status bar placed after the air bubbles, so it stacks
 * above them under water and above the mount's hearts, and other mods' bars stack around it. Like the vanilla rows,
 * the containers flash white when the meter jumps, the icons tremble like the shanks of a starving player when it
 * climbs fast, and near the threshold they shake like low hearts and pulse in their danger colours. Hidden with
 * the rest of the status bars (F1, creative, spectator). Icons: tools/hud_icons.py.
 */
public class MeterHud implements HudElement {
	public static final Identifier ID = Matriochka.id("rule_meter");
	private static final MeterHud INSTANCE = new MeterHud();

	/** A meter: its icon, its value (0 to 100), whether more is worse, and where stripes and danger start. */
	public record Meter(String icon, float value, boolean rising, boolean countdown, float warn, float danger) {
		boolean dangerous() {
			return rising ? value >= danger : value <= danger;
		}

		boolean warned() {
			return rising ? value > warn : value <= warn;
		}
	}

	private final Random random = new Random();
	private final float[] last = {-1, -1}, rate = {0, 0};
	private final long[] changedAt = {0, 0}, blinkUntil = {0, 0};
	private final int[] lastHalves = {-1, -1};
	private String lastIcons = "";

	public static void register() {
		HudElementRegistry.attachElementAfter(VanillaHudElements.AIR_BAR, ID, Hud.lifted(INSTANCE));
		HudStatusBarHeightRegistry.addRight(ID, p -> rows(p).size() * 10);
	}

	/** The rows to draw for this player, bottom first (none on the Surface, in creative or spectator). */
	public static List<Meter> rows(Player player) {
		List<Meter> out = new ArrayList<>(2);
		Minecraft mc = Minecraft.getInstance();
		if (player == null || mc.gameMode == null || !mc.gameMode.canHurtPlayer()) return out;
		var s = MatrioClient.state;
		int here = s.getIntOr("here", 0);
		if (here <= 0) return out;
		int rule = here == Worlds.ZERO ? 0 : here == 10 ? s.getIntOr("zone", 0) : here;
		if (here == 10 && rule == 0) return out;
		if (here != Worlds.ZERO && here != 10 && here > Content.WORLDS.size()) return out;
		switch (rule) {
			case 0 -> out.add(new Meter("obsession", g("obsession", 0), true, false, 50, 75));
			case 1 -> out.add(new Meter("toxin", g("toxin", 0), true, false, 50, 75));
			case 2 -> out.add(new Meter("heat", g("heat", 0), true, false, 50, 75));
			case 3 -> out.add(new Meter("shift", g("shift", 0), true, true, 50, 90));
			case 4 -> out.add(new Meter("storm", g("storm", 0), true, true, 50, 90));
			case 5 -> out.add(new Meter("noise", g("noise", 0), true, false, 35, 50));
			case 6 -> out.add(new Meter("flip", g("flip", 0), true, true, 50, 90));
			case 7 -> {
				var helmet = player.getItemBySlot(EquipmentSlot.HEAD);
				float breath = g("oxygen", 100);
				if (Snorkel.is(helmet)) {
					// the helmet's tank feeds you; your own breath shows above it only once it starts to run out
					out.add(new Meter("tank", Snorkel.fraction(helmet) * 100f, false, false, 50, 25));
					if (breath < 99.5f) out.add(new Meter("oxygen", breath, false, false, 50, 25));
				} else {
					out.add(new Meter("oxygen", breath, false, false, 50, 25));
				}
			}
			case 8 -> {
				int season = Math.floorMod(s.getIntOr("season", 0), 4);
				String name = new String[]{"spring", "summer", "autumn", "winter"}[season];
				// the leaf pulses only when a harsh season comes next (summer's hunger, winter's slowness)
				boolean harsh = season == 0 || season == 2;
				out.add(new Meter("season_" + name, g("season_turn", 0), true, true, 101, harsh ? 90 : 101));
			}
			case 9 -> out.add(new Meter("tremor", g("tremor", 0), true, true, 50, 90));
			default -> {}
		}
		return out;
	}

	private static float g(String name, float fallback) {
		return Math.max(0, Math.min(100, MatrioClient.state.getFloatOr("g_" + name, fallback)));
	}

	/** Halves shown for a value, like the shanks: 20 halves, one per 5%. */
	static int halves(float value) {
		return Math.max(0, Math.min(20, Math.round(value / 5f)));
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		Player player = mc.player;
		List<Meter> rows = rows(player);
		String icons = String.join(",", rows.stream().map(Meter::icon).toList());
		if (!icons.equals(lastIcons)) {
			// a new world or zone: start from what it shows, without a jump
			lastIcons = icons;
			for (int k = 0; k < 2; k++) {
				last[k] = -1;
				rate[k] = 0;
				lastHalves[k] = -1;
				blinkUntil[k] = 0;
			}
		}
		if (rows.isEmpty()) return;
		long now = Ui.now();
		int tick = (int) (now / 50);
		int top = g.guiHeight() - HudStatusBarHeightRegistry.getHeight(ID);
		int xRight = g.guiWidth() / 2 + 91;
		for (int k = 0; k < rows.size(); k++) {
			Meter m = rows.get(k);
			int y = top + (rows.size() - 1 - k) * 10;
			draw(g, m, k, xRight, y, now, tick);
		}
	}

	private void draw(GuiGraphicsExtractor g, Meter m, int k, int xRight, int y, long now, int tick) {
		int halves = halves(m.value());
		// how fast the meter moves, from the server's once-a-second updates
		if (last[k] < 0) {
			last[k] = m.value();
			changedAt[k] = now;
		} else if (Math.abs(m.value() - last[k]) > 0.01f) {
			float secs = Math.max(0.5f, (now - changedAt[k]) / 1000f);
			rate[k] = (m.value() - last[k]) / secs;
			last[k] = m.value();
			changedAt[k] = now;
		} else if (now - changedAt[k] > 1600) {
			rate[k] = 0;
		}
		// the containers flash white when a half is lost (or gained, for breath) as the hearts do
		if (lastHalves[k] >= 0 && !m.countdown() && halves != lastHalves[k] && (halves > lastHalves[k]) == m.rising()) {
			blinkUntil[k] = now + 1000;
		}
		lastHalves[k] = halves;
		boolean blink = now < blinkUntil[k] && (now - blinkUntil[k] + 1000) / 150 % 2 == 0;
		boolean danger = m.dangerous();
		boolean fast = !m.countdown() && (m.rising() ? rate[k] : -rate[k]) >= (m.icon().equals("oxygen") || m.icon().equals("tank") ? 6f : 3.5f);
		// in danger the contents alternate with their danger colours, unless flashes are turned down
		boolean critical = danger && (!Comfort.flashes() || tick / 8 % 2 == 0);
		boolean patterns = Comfort.get().patterns;
		String fill = critical ? (patterns ? "_critical_cross" : "_critical") : patterns && danger ? "_critical_cross" : patterns && m.warned() ? "_stripes" : "";
		String base = "meter_" + m.icon();
		random.setSeed(tick * 312871L + k * 7919L);
		for (int i = 0; i < 10; i++) {
			int xo = xRight - i * 8 - 9, yo = y;
			if (danger) yo += random.nextInt(2);
			else if (fast && tick % (halves * 3 + 1) == 0) yo += random.nextInt(3) - 1;
			Ui.sprite(g, base + (blink ? "_container_blinking" : "_container"), xo, yo, 9, 9);
			if (i * 2 + 1 < halves) Ui.sprite(g, base + "_full" + fill, xo, yo, 9, 9);
			else if (i * 2 + 1 == halves) Ui.sprite(g, base + "_half" + fill, xo, yo, 9, 9);
		}
	}
}
