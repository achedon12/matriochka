package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.item.ReplayGear;
import fr.achedon12.matriochka.replay.ReplayNet;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.nbt.CompoundTag;

/** Client side of the replay content: the Trials board and screen, the trial clock, the thrown gear. */
public final class ReplayClient {
	/** The last Trials board the server sent (see replay/Trials#board). */
	public static CompoundTag board = new CompoundTag();

	private ReplayClient() {}

	public static void init() {
		HudElementRegistry.addLast(Matriochka.id("trial_clock"), new ReplayHud());
		EntityRendererRegistry.register(ReplayGear.THROWN, ThrownItemRenderer::new);
		ClientPlayNetworking.registerGlobalReceiver(ReplayNet.TrialBoard.TYPE, (p, ctx) -> {
			board = p.board();
			Minecraft mc = Minecraft.getInstance();
			if (mc.gui.screen() instanceof TrialsScreen ts) ts.refresh();
			else if (p.open()) mc.setScreenAndShow(new TrialsScreen(null));
		});
	}
}
