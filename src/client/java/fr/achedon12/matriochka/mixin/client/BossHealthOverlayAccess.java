package fr.achedon12.matriochka.mixin.client;

import java.util.Map;
import java.util.UUID;
import net.minecraft.client.gui.components.BossHealthOverlay;
import net.minecraft.client.gui.components.LerpingBossEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Reads the boss bars the client shows, to pick the boss theme. */
@Mixin(BossHealthOverlay.class)
public interface BossHealthOverlayAccess {
	@Accessor("events")
	Map<UUID, LerpingBossEvent> matriochka$events();
}
