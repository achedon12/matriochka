package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.net.Cues;
import fr.achedon12.matriochka.world.Worlds;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.locale.Language;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * Client-side cinematics and screen effects, all driven by the server's cues (net/Cues) and all bounded by the
 * comfort options: a boss introduction (letterbox bars, a framed title card, a slow push-in of the camera that turns
 * toward the boss), the title card of a world entered for the first time, a freeze-frame flash when a boss breaks
 * into its next phase, telegraph subtitles, camera shakes, and the soft tint that stands in for Nausea and Darkness.
 * Nothing here changes the game: only what is drawn and where the camera looks during an introduction.
 */
public final class Cinematics implements HudElement {
	private static final int INTRO_MS = 3800, CARD_MS = 4800, PHASE_MS = 900;

	// boss introduction
	private static long introAt = -1;
	private static String introBoss = "";
	private static int introEntity = -1;
	/** Introductions played since the game started (read by the check run). */
	public static int intros;
	// world title card: waits for the loading screen to go
	private static int pendingWorld = -1, cardWorld = -1;
	private static long cardAt = -1;
	public static int worldCards;
	// phase break
	private static long phaseAt = -1;
	private static int phaseNumber;
	// telegraph subtitle
	private static Component teleText;
	private static boolean teleSignature;
	private static long teleAt = -1, teleUntil = -1;
	// tint standing in for Nausea / Darkness
	private static String tintKind = "";
	private static long tintUntil = -1;
	// camera shake: strength decays to zero at shakeUntil; tremor is a gentle continuous one (World Blocks nearby)
	private static float shakeStrength, tremor;
	private static long shakeAt = -1, shakeUntil = -1, tremorAt = -1;
	/** Creatures hunting the player right now (server count, for the music). */
	private static int danger;

	public static void init() {
		ClientPlayNetworking.registerGlobalReceiver(Cues.CuePayload.TYPE, (p, ctx) -> cue(p));
	}

	public static void cue(Cues.CuePayload p) {
		// the numbers come from the server: keep them finite and in range before anything draws with them
		if (!Float.isFinite(p.strength()) || p.ticks() < 0 || p.ticks() > 20 * 60) return;
		switch (p.kind()) {
			case "intro" -> startIntro(p.text(), p.entity());
			case "phase" -> startPhase((int) p.strength());
			case "telegraph" -> startTelegraph(p.text(), (int) p.strength(), p.ticks());
			case "shake" -> shake(p.strength(), p.ticks());
			case "tint" -> {
				tintKind = p.text();
				tintUntil = Math.max(tintUntil, Ui.now() + p.ticks() * 50L);
			}
			case "danger" -> danger = (int) p.strength();
			case "world" -> {
				// never trust the number: a bad one would index past the world table
				int w = (int) p.strength();
				if (validWorld(w)) pendingWorld = w;
			}
			default -> {}
		}
	}

	/** World 0 (Worlds.ZERO) or one of the worlds of the content table. */
	private static boolean validWorld(int w) {
		return w == Worlds.ZERO || (w >= 1 && w <= Content.WORLDS.size());
	}

	// ---------------------------------------------------------------- starting effects
	public static void startIntro(String boss, int entity) {
		intros++;
		introBoss = boss;
		introEntity = entity;
		if (!Comfort.cinematics()) return;
		introAt = Ui.now();
		Ui.sound(net.minecraft.sounds.SoundEvents.BELL_RESONATE, 0.6f, 0.5f);
	}

	public static void startWorldCard(int world) {
		pendingWorld = -1;
		if (!validWorld(world)) return;
		worldCards++;
		if (!Comfort.cinematics()) return;
		cardWorld = world;
		cardAt = Ui.now();
	}

	public static void startPhase(int phase) {
		phaseNumber = Math.max(0, Math.min(9, phase));
		phaseAt = Ui.now();
		shake(0.6f, 10);
	}

	public static void startTelegraph(String boss, int attack, int ticks) {
		teleText = Component.translatable("boss.matriochka." + boss + ".attack" + attack);
		teleSignature = attack == 2;
		teleAt = Ui.now();
		teleUntil = teleAt + Math.max(400, ticks * 50L);
	}

	public static void shake(float strength, int ticks) {
		long now = Ui.now();
		float left = currentShake(now);
		if (strength >= left) {
			shakeStrength = Math.max(0, Math.min(1.5f, strength));
			shakeAt = now;
			shakeUntil = now + Math.max(100, ticks * 50L);
		}
	}

	/** A shaking World Block nearby: called by its renderer each frame with 0..1 by distance. */
	public static void tremor(float strength) {
		long now = Ui.now();
		if (now - tremorAt > 100) tremor = 0;
		tremor = Math.max(tremor, strength);
		tremorAt = now;
	}

	// ---------------------------------------------------------------- queries
	public static boolean introPlaying() {
		return introAt >= 0 && Ui.now() - introAt < INTRO_MS;
	}

	public static boolean cardPlaying() {
		return cardAt >= 0 && Ui.now() - cardAt < CARD_MS;
	}

	public static String lastIntroBoss() {
		return introBoss;
	}

	public static int danger() {
		return danger;
	}

	public static boolean tinted() {
		return Ui.now() < tintUntil;
	}

	public static String tintKind() {
		return tinted() ? tintKind : "";
	}

	/** Forgets everything on leaving a world (the check run uses it between cases). */
	public static void reset() {
		introAt = cardAt = phaseAt = teleAt = teleUntil = tintUntil = shakeUntil = -1;
		pendingWorld = cardWorld = -1;
		danger = 0;
	}

	private static float currentShake(long now) {
		if (now >= shakeUntil || shakeUntil <= shakeAt) return 0;
		float t = (now - shakeAt) / (float) (shakeUntil - shakeAt);
		return shakeStrength * (1 - t) * (1 - t);
	}

	/** Camera shake, in degrees: {yaw, pitch, roll}, scaled by the comfort slider. Called while the view is set up. */
	public static float[] shakeAngles() {
		float k = Comfort.shake();
		if (k <= 0) return null;
		long now = Ui.now();
		float s = currentShake(now);
		if (now - tremorAt < 150) s = Math.max(s, tremor * 0.25f);
		if (s <= 0.001f) return null;
		double t = now / 1000.0;
		float a = s * k * 1.8f;
		return new float[]{
			(float) (Math.sin(t * 37.0) * 0.6 + Math.sin(t * 23.0 + 1.7) * 0.4) * a,
			(float) (Math.sin(t * 41.0 + 0.6) * 0.6 + Math.sin(t * 29.0 + 2.3) * 0.4) * a,
			(float) (Math.sin(t * 19.0 + 0.9)) * a * 0.5f};
	}

	/** FOV multiplier: the slow push-in of an introduction and the punch of a phase break. */
	public static float fovScale() {
		float f = 1;
		long now = Ui.now();
		if (introPlaying()) {
			float t = (now - introAt) / (float) INTRO_MS;
			f *= 1 - 0.12f * (float) Math.sin(Math.PI * Math.min(1, t * 1.15f));
		}
		if (phaseAt >= 0 && now - phaseAt < PHASE_MS && Comfort.cinematics()) {
			float t = (now - phaseAt) / (float) PHASE_MS;
			f *= 1 - 0.07f * (1 - Ui.easeOut(t)) * Math.min(1, t * 8);
		}
		return f;
	}

	/** Client tick: the camera turns toward the waking boss during the first part of its introduction. */
	public static void tick(Minecraft mc) {
		if (mc.player == null || mc.level == null) return;
		if (pendingWorld > 0 && mc.gui.screen() == null) startWorldCard(pendingWorld);
		if (!introPlaying() || Ui.now() - introAt > 1800) return;
		Entity boss = mc.level.getEntity(introEntity);
		if (boss == null || boss.distanceTo(mc.player) > 64) return;
		Vec3 eye = mc.player.getEyePosition();
		Vec3 at = boss.position().add(0, boss.getBbHeight() * 0.6, 0).subtract(eye);
		float yaw = (float) (Mth.atan2(at.z, at.x) * Mth.RAD_TO_DEG) - 90f;
		float pitch = (float) -(Mth.atan2(at.y, Math.sqrt(at.x * at.x + at.z * at.z)) * Mth.RAD_TO_DEG);
		mc.player.setYRot(mc.player.getYRot() + Mth.wrapDegrees(yaw - mc.player.getYRot()) * 0.12f);
		mc.player.setXRot(Mth.clamp(mc.player.getXRot() + (pitch - mc.player.getXRot()) * 0.12f, -90, 90));
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null) return;
		Font font = mc.font;
		int w = g.guiWidth(), h = g.guiHeight();
		long now = Ui.now();
		if (tinted()) tint(g, w, h, now);
		if (teleUntil > now && Comfort.flashes() && teleSignature) edgeGlow(g, w, h, 0xFFD8402A, 0.35f * (float) Math.sin(Math.PI * Ui.clamp01((now - teleAt) / (float) (teleUntil - teleAt))));
		if (phaseAt >= 0 && now - phaseAt < PHASE_MS) phaseBreak(g, font, w, h, now);
		if (introPlaying()) intro(g, font, w, h, now);
		else if (cardPlaying()) worldCard(g, font, w, h, now);
		if (teleUntil > now && Comfort.get().subtitles && !introPlaying()) subtitle(g, font, w, h, now);
	}

	/** Bars that slide in from the top and bottom, with a thin gold rule on their inner edge. */
	static void letterbox(GuiGraphicsExtractor g, int w, int h, float shown) {
		int bar = Math.round(h * 0.11f * shown);
		if (bar <= 0) return;
		g.fill(0, 0, w, bar, 0xFF0A0604);
		g.fill(0, h - bar, w, h, 0xFF0A0604);
		g.fill(0, bar, w, bar + 1, Ui.alpha(0xFFB0782A, shown));
		g.fill(0, h - bar - 1, w, h - bar, Ui.alpha(0xFFB0782A, shown));
	}

	private static void intro(GuiGraphicsExtractor g, Font font, int w, int h, long now) {
		float t = (now - introAt) / (float) INTRO_MS;
		float in = Ui.easeOut(t / 0.12f), out = 1 - Ui.easeIn((t - 0.82f) / 0.18f);
		letterbox(g, w, h, Math.min(in, out));
		float card = Math.min(Ui.easeBack((t - 0.14f) / 0.16f), out);
		if (card <= 0.02f) return;
		int world = bossWorld(introBoss);
		Component name = Component.translatable("entity.matriochka." + introBoss);
		String titleKey = "cine.matriochka.boss." + introBoss;
		Component title = Language.getInstance().has(titleKey) ? Component.translatable(titleKey) : null;
		titleCard(g, font, w / 2, Math.round(h * 0.64f), name, title, world, card, introAt + 500);
	}

	private static void worldCard(GuiGraphicsExtractor g, Font font, int w, int h, long now) {
		float t = (now - cardAt) / (float) CARD_MS;
		float a = Math.min(Ui.easeBack(t / 0.12f), 1 - Ui.easeIn((t - 0.8f) / 0.2f));
		if (a <= 0.02f) return;
		if (!validWorld(cardWorld)) {
			cardAt = -1;
			return;
		}
		boolean zero = cardWorld == Worlds.ZERO;
		Component name = Component.translatable("world.matriochka." + cardWorld);
		Component rule = Component.translatable("cine.matriochka.world." + cardWorld);
		int cy = Math.round(h * 0.28f);
		titleCard(g, font, w / 2, cy, name, rule, zero ? 0 : cardWorld, a, cardAt + 300);
		// the world's rule medallion turns in above the card
		String emblem = zero ? "stillness" : Content.WORLDS.get(cardWorld - 1).rule();
		g.pose().pushMatrix();
		g.pose().translate(w / 2f, cy - 30);
		g.pose().rotate((1 - Ui.easeOut(t / 0.25f)) * (float) Math.PI);
		g.pose().scale(a, a);
		Ui.sprite(g, "rule_" + emblem, -11, -11, 22, 22, Ui.white(a));
		g.pose().popMatrix();
	}

	/**
	 * The framed title card: a lacquer frame sized to the text, the world's enamel plate on its top edge, the name
	 * in large gold letters, a gilt vine, and the line beneath. a in [0, 1+] drives its scale and fade.
	 */
	private static void titleCard(GuiGraphicsExtractor g, Font font, int cx, int cy, Component name, Component line, int world, float a, long sheenPhase) {
		float alpha = Ui.clamp01(a);
		int nameW = font.width(name) * 2;
		java.util.List<net.minecraft.util.FormattedCharSequence> lines = line == null ? java.util.List.of() : font.split(line, 260);
		int lineW = 0;
		for (var l : lines) lineW = Math.max(lineW, font.width(l));
		int cw = Math.max(nameW, lineW) + 48, ch = 44 + lines.size() * 10;
		g.pose().pushMatrix();
		g.pose().translate(cx, cy);
		float s = 0.9f + 0.1f * a;
		g.pose().scale(s, s);
		int x = -cw / 2, y = -ch / 2;
		Ui.sprite(g, "frame", x, y, cw, ch, Ui.white(alpha));
		Ui.sheen(g, x + 8, y + 6, cw - 16, ch - 12, 5200, sheenPhase, 0.5f * alpha);
		Component plate = world == 0 ? Component.translatable("journal.matriochka.surface") : Component.translatable("hud.matriochka.world", world);
		int pw = font.width(plate) + 34;
		Ui.sprite(g, "plate_" + Math.max(0, Math.min(10, world)), -pw / 2, y - 8, pw, 16, Ui.white(alpha));
		if (alpha > 0.1f) Ui.embossed(g, font, plate, -font.width(plate) / 2, y - 4, Ui.alpha(Ui.GOLD, alpha));
		if (alpha > 0.1f) {
			g.pose().pushMatrix();
			g.pose().scale(2, 2);
			int tx = -font.width(name) / 2, ty = (y + 13) / 2;
			g.text(font, name, tx + 1, ty + 1, Ui.alpha(Ui.SHADOW, alpha), false);
			g.text(font, name, tx, ty, Ui.alpha(Ui.GOLD, alpha), false);
			g.pose().popMatrix();
			int vine = Math.round(Math.min(cw - 30, 160) * Ui.easeOut(a));
			Ui.sprite(g, "divider", -vine / 2, y + 31, vine, 8, Ui.white(alpha));
			int ly = y + 41;
			for (var l : lines) {
				g.text(font, l, -font.width(l) / 2 + 1, ly + 1, Ui.alpha(Ui.SHADOW, alpha * 0.9f), false);
				g.text(font, l, -font.width(l) / 2, ly, Ui.alpha(Ui.LIGHT, alpha), false);
				ly += 10;
			}
		}
		g.pose().popMatrix();
		if (alpha > 0.3f) Ui.wanderingGlint(g, new int[][]{{cx + x + 4, cy + y + 4}, {cx - x - 4, cy + y + 4}, {cx + x + 4, cy - y - 4}, {cx - x - 4, cy - y - 4}}, 1400, 7);
	}

	/** The phase break: a freeze-frame flash (or a dark pulse without flashes) and the shell's number. */
	private static void phaseBreak(GuiGraphicsExtractor g, Font font, int w, int h, long now) {
		float t = (now - phaseAt) / (float) PHASE_MS;
		float f = 1 - Ui.easeOut(t);
		if (Comfort.flashes()) g.fill(0, 0, w, h, Ui.alpha(0xFFFFF4DE, 0.55f * f));
		else edgeGlow(g, w, h, 0xFF140A06, 0.6f * f);
		if (!Comfort.cinematics()) return;
		letterbox(g, w, h, 0.6f * Math.min(1, t * 6) * (1 - Ui.easeIn((t - 0.6f) / 0.4f)));
		Component n = Component.literal("I".repeat(Math.min(3, phaseNumber + 1)));
		float a = Ui.clamp01(1 - Ui.easeIn((t - 0.5f) / 0.5f));
		if (a < 0.05f) return;
		g.pose().pushMatrix();
		g.pose().translate(w / 2f, h * 0.36f);
		float s = 3.2f - 0.8f * Ui.easeOut(t * 2);
		g.pose().scale(s, s);
		g.text(font, n, -font.width(n) / 2 + 1, -3, Ui.alpha(Ui.SHADOW, a), false);
		g.text(font, n, -font.width(n) / 2, -4, Ui.alpha(Ui.RED, a), false);
		g.pose().popMatrix();
	}

	/** The attack a boss winds up, in big letters on a lacquer cartouche, with the time left as a shrinking gilt line. */
	private static void subtitle(GuiGraphicsExtractor g, Font font, int w, int h, long now) {
		float in = Ui.easeBack((now - teleAt) / 180f);
		float left = 1 - Ui.clamp01((now - teleAt) / (float) (teleUntil - teleAt));
		int tw = font.width(teleText) * 2 + 36, th = 32;
		int x = w / 2 - tw / 2, y = Math.round(h * 0.2f);
		g.pose().pushMatrix();
		g.pose().translate(w / 2f, y + th / 2f);
		g.pose().scale(0.85f + 0.15f * in, 0.85f + 0.15f * in);
		g.pose().translate(-w / 2f, -(y + th / 2f));
		Ui.sprite(g, "hud_plaque", x, y, tw, th);
		g.pose().pushMatrix();
		g.pose().scale(2, 2);
		int tx = (w / 2 - font.width(teleText)) / 2, ty = (y + 7) / 2;
		g.text(font, teleText, tx + 1, ty + 1, Ui.SHADOW, false);
		g.text(font, teleText, tx, ty, teleSignature ? 0xFFFF7A5A : Ui.GOLD, false);
		g.pose().popMatrix();
		int lw = Math.round((tw - 24) * left);
		g.fill(w / 2 - lw / 2, y + th - 6, w / 2 + lw / 2, y + th - 5, teleSignature ? 0xFFD8402A : 0xFFE8C060);
		g.pose().popMatrix();
	}

	/** A soft frame of colour around the screen, fading toward the middle. */
	static void edgeGlow(GuiGraphicsExtractor g, int w, int h, int color, float strength) {
		if (strength <= 0.01f) return;
		int band = Math.max(12, Math.min(w, h) / 5), steps = 12;
		for (int i = 0; i < steps; i++) {
			float k = (1 - i / (float) steps);
			int c = Ui.alpha(color, strength * k * k / 1.6f);
			int o = i * band / steps, o2 = (i + 1) * band / steps;
			g.fill(0, o, w, o2, c);
			g.fill(0, h - o2, w, h - o, c);
			g.fill(o, o2, o2, h - o2, c);
			g.fill(w - o2, o2, w - o, h - o2, c);
		}
	}

	/** Stands in for Nausea (a slow green-violet haze at the edges) and Darkness (a steady dimming, no pulses). */
	private static void tint(GuiGraphicsExtractor g, int w, int h, long now) {
		float fade = Ui.clamp01((tintUntil - now) / 600f);
		if (tintKind.equals("darkness")) {
			g.fill(0, 0, w, h, Ui.alpha(0xFF05050A, 0.28f * fade));
			edgeGlow(g, w, h, 0xFF05050A, 0.9f * fade);
		} else {
			float breathe = 0.5f + 0.5f * (float) Math.sin(now / 1400.0);
			edgeGlow(g, w, h, 0xFF6A8A3A, (0.35f + 0.15f * breathe) * fade);
			edgeGlow(g, w, h, 0xFF8A4A9A, (0.2f + 0.1f * (1 - breathe)) * fade);
		}
	}

	private static int bossWorld(String id) {
		for (var b : Content.BOSSES) if (b.id().equals(id)) return b.world() == Worlds.ZERO ? 0 : b.world();
		return 0;
	}
}
