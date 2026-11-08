package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * The ten relics of the wonders (structure/Rewards, block/Reliquary): each one used gives one more heart of health
 * for good, once per relic. The bonus lives in the player's state ("relic_n") and is laid on the max health as one
 * attribute modifier, refreshed while the player plays so it survives deaths and reconnections.
 */
public final class Relics {
	private Relics() {}

	private static final net.minecraft.resources.Identifier MOD = Matriochka.id("relics");

	public static int count(PlayerState ps) {
		int n = 0;
		for (int w = 1; w <= 10; w++) if (ps.has("relic_" + w)) n++;
		return n;
	}

	/** Uses the relic of World w: true when it was consumed (a relic already taken in stays in the hand). */
	public static boolean use(ServerPlayer sp, int w) {
		PlayerState ps = PlayerState.of(sp);
		if (ps.has("relic_" + w)) {
			sp.sendOverlayMessage(Component.translatable("message.matriochka.relic.known"));
			return false;
		}
		ps.set("relic_" + w, true);
		ps.sync();
		apply(sp);
		sp.heal(2f);
		int n = count(ps);
		ServerLevel sl = (ServerLevel) sp.level();
		sl.sendParticles(ParticleTypes.HEART, sp.getX(), sp.getY() + 1.6, sp.getZ(), 8, 0.4, 0.3, 0.4, 0.05);
		sl.playSound(null, sp.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.8f, 1.4f);
		sp.sendSystemMessage(Component.translatable("message.matriochka.relic.taken", n).withStyle(ChatFormatting.GOLD));
		if (n == 10) sp.sendSystemMessage(Component.translatable("message.matriochka.relic.all").withStyle(ChatFormatting.LIGHT_PURPLE));
		return true;
	}

	/** Lays the relics' hearts on the player's max health (one heart each). */
	public static void apply(ServerPlayer sp) {
		var attr = sp.getAttribute(Attributes.MAX_HEALTH);
		if (attr == null) return;
		double want = 2.0 * count(PlayerState.of(sp));
		var cur = attr.getModifier(MOD);
		if (cur != null && cur.amount() == want) return;
		attr.removeModifier(MOD);
		if (want > 0) attr.addPermanentModifier(new AttributeModifier(MOD, want, AttributeModifier.Operation.ADD_VALUE));
	}
}
