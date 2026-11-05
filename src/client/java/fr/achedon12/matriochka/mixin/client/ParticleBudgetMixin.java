package fr.achedon12.matriochka.mixin.client;

import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.MusicThemes;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.network.protocol.game.ClientboundLevelParticlesPacket;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Comfort option "reduced particles": two particles out of three sent by the server are skipped inside the worlds
 * and during boss fights.
 */
@Mixin(ClientPacketListener.class)
public abstract class ParticleBudgetMixin {
	@Unique
	private int matriochka$count;

	@Inject(method = "tryAddParticle", at = @At("HEAD"), cancellable = true)
	private void matriochka$reduce(ClientboundLevelParticlesPacket packet, double x, double y, double z, double xa, double ya, double za,
								   CallbackInfoReturnable<Boolean> cir) {
		if (!Comfort.get().reducedParticles) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) return;
		boolean ours = mc.level.dimension().identifier().getNamespace().equals("matriochka") || MusicThemes.bossFight(mc);
		if (ours && matriochka$count++ % 3 != 0) cir.setReturnValue(true);
	}
}
