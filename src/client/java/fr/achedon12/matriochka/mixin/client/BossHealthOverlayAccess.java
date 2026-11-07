package fr.achedon12.matriochka.mixin.client;

import java.util.Map;
import java.util.UUID;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.BossHealthOverlay;
import net.minecraft.client.gui.components.LerpingBossEvent;
import net.minecraft.world.BossEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Reads the boss bars the client shows (to pick the boss theme), and draws one the vanilla way (client/BossBars). */
@Mixin(BossHealthOverlay.class)
public interface BossHealthOverlayAccess {
	@Accessor("events")
	Map<UUID, LerpingBossEvent> matriochka$events();

	@Invoker("extractBar")
	void matriochka$extractBar(GuiGraphicsExtractor g, int x, int y, BossEvent event);
}
