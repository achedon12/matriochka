package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.item.MatriarchArmor;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.ChatFormatting;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/**
 * What the client shows of the Matriarch Armour: its tooltip (the set as a checklist, worn pieces lit, owned ones
 * pale; the Nested Shell in two short lines and its state, ready or mending with the time left) and a small doll beside
 * the hearts while the whole set is worn, full when the shell is ready, filling back up while it mends. It hides with
 * the status bars (F1, creative, spectator) and follows the HUD scale of the comfort settings.
 */
public final class MatriarchTip implements HudElement {
	private static final String[] PIECES = {"helmet", "chestplate", "leggings", "boots"};
	private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
	/** The doll icon beside the hearts, in GUI pixels. */
	public static final int ICON_W = 9, ICON_H = 11;

	private MatriarchTip() {}

	public static void init() {
		MatriarchArmor.TIP = MatriarchTip::append;
		MatriarchArmor.PROVIDER = new com.geckolib.animatable.client.GeoRenderProvider() {
			private MatriarchArmorRenderer<?> renderer;

			@Override
			public com.geckolib.renderer.GeoArmorRenderer<?, ?> getGeoArmorRenderer(ItemStack stack, EquipmentSlot slot) {
				if (renderer == null) renderer = new MatriarchArmorRenderer<>();
				return renderer;
			}
		};
		HudElementRegistry.attachElementAfter(VanillaHudElements.HEALTH_BAR, Matriochka.id("nested_shell"), new MatriarchTip());
	}

	/** Seconds before the player's own Nested Shell is whole again (0: ready). */
	public static long secondsLeft() {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) return 0;
		long cracked = MatrioClient.state.getLongOr("matriarch_cracked", -Content.MATRIARCH_SAVE_COOLDOWN);
		long left = cracked + Content.MATRIARCH_SAVE_COOLDOWN - mc.level.getGameTime();
		return left <= 0 ? 0 : (left + 19) / 20;
	}

	/** How many of the four pieces the player wears. */
	public static int worn(Player p) {
		int n = 0;
		for (int i = 0; i < 4; i++) if (p.getItemBySlot(SLOTS[i]).is(ModContent.item("matriarch_" + PIECES[i]))) n++;
		return n;
	}

	public static String time(long seconds) {
		return seconds >= 60 ? (seconds / 60) + " min " + (seconds % 60) + " s" : seconds + " s";
	}

	private static void append(ItemStack stack, Consumer<Component> out) {
		Player p = Minecraft.getInstance().player;
		out.accept(Component.translatable("tooltip.matriochka.matriarch.bonus1").withStyle(ChatFormatting.GOLD));
		out.accept(Component.translatable("tooltip.matriochka.matriarch.bonus2").withStyle(ChatFormatting.GOLD));
		int worn = p == null ? 0 : worn(p);
		out.accept(Component.translatable("tooltip.matriochka.matriarch.set", worn).withStyle(ChatFormatting.GRAY));
		for (int i = 0; i < 4; i++) {
			var item = ModContent.item("matriarch_" + PIECES[i]);
			boolean on = p != null && p.getItemBySlot(SLOTS[i]).is(item);
			boolean owned = on || p != null && p.getInventory().contains(new ItemStack(item));
			Component name = new ItemStack(item).getHoverName();
			out.accept(Component.literal(on ? "  ◆ " : owned ? "  ◇ " : "  · ").append(name)
				.withStyle(on ? ChatFormatting.YELLOW : owned ? ChatFormatting.GRAY : ChatFormatting.DARK_GRAY));
		}
		long left = secondsLeft();
		if (worn < 4) out.accept(Component.translatable("tooltip.matriochka.matriarch.idle").withStyle(ChatFormatting.DARK_GRAY));
		else if (left <= 0) out.accept(Component.translatable("tooltip.matriochka.matriarch.ready").withStyle(ChatFormatting.GREEN));
		else out.accept(Component.translatable("tooltip.matriochka.matriarch.mending", time(left)).withStyle(ChatFormatting.RED));
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
		Minecraft mc = Minecraft.getInstance();
		Player p = mc.player;
		if (p == null || mc.gameMode == null || !mc.gameMode.canHurtPlayer() || worn(p) < 4) return;
		float scale = Math.max(0.75f, Math.min(1.5f, Comfort.get().hudScale));
		int w = Math.round(ICON_W * scale), h = Math.round(ICON_H * scale);
		// left of the hearts, its foot on their row
		int x = g.guiWidth() / 2 - 91 - w - 3, y = g.guiHeight() - 39 + 9 - h;
		long left = secondsLeft();
		float fill = left <= 0 ? 1f : 1f - left / (Content.MATRIARCH_SAVE_COOLDOWN / 20f);
		Ui.sprite(g, "matriarch_shell_empty", x, y, w, h);
		int full = Math.round(ICON_H * fill);
		if (full > 0) Ui.spritePart(g, "matriarch_shell_full", ICON_W, ICON_H, 0, ICON_H - full, x, y + h - Math.round(full * scale), w, Math.round(full * scale), 0xFFFFFFFF);
		// ready: a slow glint over the doll; mending: the time left, with the gauge patterns option
		if (left <= 0 && (Ui.now() / 120) % 25 < 2) Ui.sprite(g, "matriarch_shell_glint", x, y, w, h);
		if (left > 0 && Comfort.get().patterns) g.text(mc.font, String.valueOf(left), x - mc.font.width(String.valueOf(left)) - 1, y + h - 8, 0xFFE8C050, true);
	}
}
