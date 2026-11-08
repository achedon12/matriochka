package fr.achedon12.matriochka.client.mc;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.advancements.AdvancementType;
import net.minecraft.advancements.DisplayInfo;
import net.minecraft.network.chat.Component;

/** The client calls that differ between Minecraft versions (versions/<mc>/): this is 26.2's. */
public final class McClient {
	private McClient() {}

	public static void rotate(PoseStack pose, Axis axis, float degrees) {
		pose.mulPose(axis.rotationDegrees(degrees));
	}

	public static AdvancementType type(DisplayInfo d) {
		return d.getType();
	}

	public static Component title(DisplayInfo d) {
		return d.getTitle();
	}

	/** The screen shown (26.1: Minecraft.screen; 26.2: Minecraft.gui.screen()). */
	public static net.minecraft.client.gui.screens.@org.jspecify.annotations.Nullable Screen screen(net.minecraft.client.Minecraft mc) {
		return mc.gui.screen();
	}

	public static void setScreen(net.minecraft.client.Minecraft mc, net.minecraft.client.gui.screens.@org.jspecify.annotations.Nullable Screen s) {
		mc.gui.setScreen(s);
	}

	/** Whether the HUD is hidden (F1). */
	public static boolean hudHidden(net.minecraft.client.Minecraft mc) {
		return mc.gui.hud.isHidden();
	}

	public static void toggleHud(net.minecraft.client.Minecraft mc) {
		mc.gui.hud.toggle();
	}

	public static net.minecraft.client.gui.components.BossHealthOverlay bossOverlay(net.minecraft.client.Minecraft mc) {
		return mc.gui.hud.getBossOverlay();
	}

	/** The packed light at a block, for rendering. */
	public static int lightAt(net.minecraft.world.level.Level level, net.minecraft.core.BlockPos pos) {
		return net.minecraft.util.LightCoordsUtil.getLightCoords(level, pos);
	}

	public static final int FULL_LIGHT = net.minecraft.util.LightCoordsUtil.FULL_BRIGHT;

	public static void clearToasts(net.minecraft.client.Minecraft mc) {
		mc.gui.toastManager().clear();
	}

	public static void clearChat(net.minecraft.client.Minecraft mc) {
		mc.gui.hud.getChat().clearMessages(true);
	}
}
