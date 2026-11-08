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
		return mc.screen;
	}

	public static void setScreen(net.minecraft.client.Minecraft mc, net.minecraft.client.gui.screens.@org.jspecify.annotations.Nullable Screen s) {
		mc.setScreen(s);
	}

	/** Whether the HUD is hidden (F1). */
	public static boolean hudHidden(net.minecraft.client.Minecraft mc) {
		return mc.options.hideGui;
	}

	public static void toggleHud(net.minecraft.client.Minecraft mc) {
		mc.options.hideGui = !mc.options.hideGui;
	}

	public static net.minecraft.client.gui.components.BossHealthOverlay bossOverlay(net.minecraft.client.Minecraft mc) {
		return mc.gui.getBossOverlay();
	}

	/** The packed light at a block, for rendering. */
	public static int lightAt(net.minecraft.world.level.Level level, net.minecraft.core.BlockPos pos) {
		return net.minecraft.client.renderer.LevelRenderer.getLightCoords(level, pos);
	}

	public static final int FULL_LIGHT = 0xF000F0;

	public static void clearToasts(net.minecraft.client.Minecraft mc) {
		mc.getToastManager().clear();
	}

	public static void clearChat(net.minecraft.client.Minecraft mc) {
		mc.gui.getChat().clearMessages(true);
	}
}
