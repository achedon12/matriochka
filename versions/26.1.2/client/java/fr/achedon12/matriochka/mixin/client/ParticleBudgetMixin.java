package fr.achedon12.matriochka.mixin.client;

import com.llamalad7.mixinextras.injector.v2.WrapWithCondition;
import fr.achedon12.matriochka.client.Comfort;
import fr.achedon12.matriochka.client.MusicThemes;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.core.particles.ParticleOptions;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;

/**
 * Comfort option "reduced particles": two particles out of three sent by the server are skipped inside the worlds
 * and during boss fights. 26.2 adds them one by one inside handleParticleEvent.
 */
@Mixin(ClientPacketListener.class)
public abstract class ParticleBudgetMixin {
	@Unique
	private int matriochka$count;

	@WrapWithCondition(method = "handleParticleEvent", at = @At(value = "INVOKE",
		target = "Lnet/minecraft/client/multiplayer/ClientLevel;addParticle(Lnet/minecraft/core/particles/ParticleOptions;ZZDDDDDD)V"), require = 0)
	private boolean matriochka$reduce(ClientLevel level, ParticleOptions o, boolean force, boolean always, double x, double y, double z, double xa, double ya, double za) {
		if (!Comfort.get().reducedParticles) return true;
		Minecraft mc = Minecraft.getInstance();
		boolean ours = level.dimension().identifier().getNamespace().equals("matriochka") || MusicThemes.bossFight(mc);
		return !ours || matriochka$count++ % 3 == 0;
	}
}
