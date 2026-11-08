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
 * for good, once per relic, and a gift of its world: the rules of Worlds 1, 2, 5 and 7 weigh a quarter less (toxin,
 * heat, noise, breath; World 10 has them all), the others a lasting attribute. All ten add armour. The relics live in
 * the player's state ("relic_n") and are laid on as attribute modifiers, refreshed while the player plays so they
 * survive deaths and reconnections.
 */
public final class Relics {
	private Relics() {}

	private static final net.minecraft.resources.Identifier MOD = Matriochka.id("relics");

	private record Gift(net.minecraft.core.Holder<net.minecraft.world.entity.ai.attributes.Attribute> attr, double amount, AttributeModifier.Operation op) {}

	/** The attribute each relic gives besides its heart; the relics of the rules' worlds ease the rule instead (ease). */
	private static final java.util.Map<Integer, Gift> GIFTS = java.util.Map.of(
		3, new Gift(Attributes.LUCK, 1.0, AttributeModifier.Operation.ADD_VALUE),
		4, new Gift(Attributes.ATTACK_SPEED, 0.1, AttributeModifier.Operation.ADD_MULTIPLIED_BASE),
		6, new Gift(Attributes.SAFE_FALL_DISTANCE, 4.0, AttributeModifier.Operation.ADD_VALUE),
		8, new Gift(Attributes.MOVEMENT_SPEED, 0.05, AttributeModifier.Operation.ADD_MULTIPLIED_BASE),
		9, new Gift(Attributes.KNOCKBACK_RESISTANCE, 0.2, AttributeModifier.Operation.ADD_VALUE),
		10, new Gift(Attributes.BLOCK_BREAK_SPEED, 0.15, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
	private static final double ALL_ARMOR = 4.0;

	/** What a rule's gauge gain is multiplied by: three quarters with the relic of World w. */
	public static float ease(PlayerState ps, int w) {
		return ps.has("relic_" + w) ? 0.75f : 1f;
	}

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
		gifts(sp);
		var attr = sp.getAttribute(Attributes.MAX_HEALTH);
		if (attr == null) return;
		double want = 2.0 * count(PlayerState.of(sp));
		var cur = attr.getModifier(MOD);
		if (cur != null && cur.amount() == want) return;
		attr.removeModifier(MOD);
		if (want > 0) attr.addPermanentModifier(new AttributeModifier(MOD, want, AttributeModifier.Operation.ADD_VALUE));
	}

	/** Lays each relic's own gift and the armour of all ten, removing what is no longer owed. */
	private static void gifts(ServerPlayer sp) {
		PlayerState ps = PlayerState.of(sp);
		for (var e : GIFTS.entrySet()) {
			var attr = sp.getAttribute(e.getValue().attr());
			if (attr == null) continue;
			var id = Matriochka.id("relic_" + e.getKey());
			boolean owed = ps.has("relic_" + e.getKey());
			if (owed == (attr.getModifier(id) != null)) continue;
			attr.removeModifier(id);
			if (owed) attr.addPermanentModifier(new AttributeModifier(id, e.getValue().amount(), e.getValue().op()));
		}
		var armor = sp.getAttribute(Attributes.ARMOR);
		if (armor != null) {
			var id = Matriochka.id("relics_all");
			boolean owed = count(ps) == 10;
			if (owed != (armor.getModifier(id) != null)) {
				armor.removeModifier(id);
				if (owed) armor.addPermanentModifier(new AttributeModifier(id, ALL_ARMOR, AttributeModifier.Operation.ADD_VALUE));
			}
		}
	}
}
