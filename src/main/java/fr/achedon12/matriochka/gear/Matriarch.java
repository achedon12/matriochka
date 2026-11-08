package fr.achedon12.matriochka.gear;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Sounds;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;

/**
 * The Matriarch Armour's set bonus, the Nested Shell (tools/content.py MATRIARCH): worn whole, every world's gauge
 * builds half as fast (toxin, heat, noise and the loss of breath, multiplied in where the relics ease them, see
 * rules/WorldRules), and once every five minutes a blow that would kill the wearer leaves them at three hearts instead:
 * the outer doll cracks. It is asked before the Doll of Life (world/Events), which is then not spent.
 */
public final class Matriarch {
	private Matriarch() {}

	private static final EquipmentSlot[] SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
	private static final String[] PIECES = {"helmet", "chestplate", "leggings", "boots"};

	/** Whether the player wears the four pieces. */
	public static boolean full(ServerPlayer p) {
		for (int i = 0; i < SLOTS.length; i++) if (!p.getItemBySlot(SLOTS[i]).is(ModContent.item("matriarch_" + PIECES[i]))) return false;
		return true;
	}

	/** What a rule's gauge gain is multiplied by: a half with the whole set on, one otherwise. */
	public static float ease(ServerPlayer p) {
		return full(p) ? Content.MATRIARCH_GAUGE : 1f;
	}

	/** Game time until which the outer doll mends after it cracked (0: whole). */
	public static long mendingUntil(ServerPlayer p) {
		return PlayerState.of(p).tag().getLongOr("matriarch_cracked", -Content.MATRIARCH_SAVE_COOLDOWN) + Content.MATRIARCH_SAVE_COOLDOWN;
	}

	/**
	 * A blow that would kill a wearer of the whole set: once every five minutes, the outer doll takes it and leaves them
	 * at three hearts. Returns true when it did (the death is cancelled). The void and /kill go through.
	 */
	public static boolean save(ServerPlayer p, DamageSource source) {
		if (!full(p) || source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return false;
		ServerLevel level = (ServerLevel) p.level();
		long now = level.getGameTime();
		if (now < mendingUntil(p)) return false;
		PlayerState ps = PlayerState.of(p);
		ps.tag().putLong("matriarch_cracked", now);
		ps.save();
		ps.sync();
		// on the wearer's screen: a gold vignette and the outer doll's cracks, for a second
		fr.achedon12.matriochka.net.Cues.tint(p, "matriarch", 24);
		p.setHealth(Math.min(p.getMaxHealth(), Content.MATRIARCH_SAVE_HEALTH));
		p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 40, 2));
		// gold dust and a few sparks burst from the outer doll, round the body and below the eyes
		double x = p.getX(), y = p.getY() + 0.7, z = p.getZ();
		for (int k = 0; k < 24; k++) {
			double ang = k * Math.PI * 2 / 24;
			level.sendParticles(fr.achedon12.matriochka.content.Particles.GOLD_MOTE, x + Math.cos(ang) * 0.9, y + (k % 3) * 0.3, z + Math.sin(ang) * 0.9, 1, 0, 0, 0, 0);
		}
		level.sendParticles(ParticleTypes.END_ROD, x, y, z, 10, 0.6, 0.3, 0.6, 0.06);
		level.playSound(null, p.blockPosition(), Sounds.MATRIARCH_CRACK, SoundSource.PLAYERS, 1.4f, 1f);
		p.sendOverlayMessage(Component.translatable("message.matriochka.matriarch.cracked").withStyle(ChatFormatting.GOLD));
		return true;
	}
}
