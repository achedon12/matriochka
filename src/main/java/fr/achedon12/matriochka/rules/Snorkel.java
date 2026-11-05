package fr.achedon12.matriochka.rules;

import com.mojang.serialization.Codec;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;

/**
 * Snorkel helmets, the only way to breathe for long in the Pressure Ocean. Each one is head armor with a tank of air
 * (in seconds, stored on the stack): under water you breathe from it, and it tops your lungs up as it empties. It
 * refills in air (an air pocket, a grotto, a habitat, the surface), in bubble columns, over an air vent, at the Abyssal
 * Press or with an Oxygen Capsule. It breaks easily: every hit wears it on top of the usual armor wear, and the depths
 * grind it down while you use it. Higher tiers hold more air, wear less and let you dive deeper.
 */
public final class Snorkel {
	/** Seconds of air left in the tank. Absent means full (a fresh helmet). */
	public static final DataComponentType<Float> OXYGEN = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, Matriochka.id("oxygen"),
		DataComponentType.<Float>builder().persistent(Codec.FLOAT).networkSynchronized(ByteBufCodecs.FLOAT).build());
	/** Tank seconds won back per second in open air, and over a vent or in a bubble column. */
	public static final float AIR_RATE = 20f, VENT_RATE = 12f;
	/** Tank seconds spent per second of breathing, and per point of breath topped up. */
	public static final float BREATH_COST = 1f, TOP_UP_COST = 0.25f;
	/** Breath lost per second under water without air, out of 100 (about 33 seconds). */
	public static final float HOLD_DRAIN = 3f;
	/** Every this many ticks of use under water, the depths take one point of durability. */
	public static final int GRIND_TICKS = 20 * 30;

	private static final Map<String, Defs.SnorkelDef> DEFS = new HashMap<>();

	private Snorkel() {}

	public static void init() {
		for (Defs.SnorkelDef d : Content.SNORKELS) DEFS.put(d.id(), d);
		ServerLivingEntityEvents.AFTER_DAMAGE.register(Snorkel::afterDamage);
	}

	public static Defs.SnorkelDef def(String id) {
		return DEFS.get(id);
	}

	public static Defs.SnorkelDef def(ItemStack stack) {
		if (stack == null || stack.isEmpty()) return null;
		return DEFS.get(ModContent.idOf(stack.getItem()));
	}

	public static boolean is(ItemStack stack) {
		return def(stack) != null;
	}

	/** The snorkel helmet on a player's head, or an empty stack. */
	public static ItemStack worn(Player p) {
		ItemStack head = p.getItemBySlot(EquipmentSlot.HEAD);
		return is(head) ? head : ItemStack.EMPTY;
	}

	public static int capacity(ItemStack stack) {
		Defs.SnorkelDef d = def(stack);
		return d == null ? 0 : d.tank();
	}

	public static float tank(ItemStack stack) {
		Defs.SnorkelDef d = def(stack);
		if (d == null) return 0;
		Float v = stack.get(OXYGEN);
		return v == null ? d.tank() : v;
	}

	public static void setTank(ItemStack stack, float seconds) {
		if (!is(stack)) return;
		stack.set(OXYGEN, Math.max(0f, Math.min(capacity(stack), seconds)));
	}

	public static float fraction(ItemStack stack) {
		int cap = capacity(stack);
		return cap <= 0 ? 0 : tank(stack) / cap;
	}

	/** Adds air to the tank; returns how much went in. */
	public static float refill(ItemStack stack, float seconds) {
		float before = tank(stack);
		setTank(stack, before + seconds);
		return tank(stack) - before;
	}

	/** How full the player's air is, in percent: the helmet's tank while it holds air, otherwise the lungs. */
	public static float airPercent(ServerPlayer p) {
		ItemStack h = worn(p);
		if (!h.isEmpty() && tank(h) > 0) return fraction(h) * 100f;
		return PlayerState.of(p).gauge("oxygen");
	}

	/** Blocks of extra depth the helmet allows before the pressure hurts. */
	public static int depthBonus(ItemStack stack) {
		Defs.SnorkelDef d = def(stack);
		return d == null ? 0 : d.depth();
	}

	/** True when the player swims in a bubble column or right over an air vent. */
	public static boolean atAirSource(ServerLevel level, ServerPlayer p) {
		BlockPos at = p.blockPosition();
		if (level.getBlockState(at).is(Blocks.BUBBLE_COLUMN) || level.getBlockState(at.above()).is(Blocks.BUBBLE_COLUMN)) return true;
		var vent = ModContent.block("air_vent");
		for (BlockPos q : BlockPos.betweenClosed(at.offset(-1, -6, -1), at.offset(1, 0, 1))) {
			if (level.getBlockState(q).is(vent)) return true;
		}
		return false;
	}

	/**
	 * One second of breathing under water from the helmet. Returns true when the helmet gave air. {@code mult} scales the
	 * cost (Apnea Kelp, the Survivor class).
	 */
	public static boolean breathe(ServerPlayer p, PlayerState ps, ItemStack helmet, float mult, long t) {
		if (helmet.isEmpty() || tank(helmet) <= 0) return false;
		float topUp = Math.min(6f, 100f - ps.gauge("oxygen"));
		float before = fraction(helmet);
		setTank(helmet, tank(helmet) - mult * (BREATH_COST + topUp * TOP_UP_COST));
		ps.addGauge("oxygen", topUp);
		if (t % GRIND_TICKS == 0) helmet.hurtAndBreak(1, p, EquipmentSlot.HEAD);
		float after = fraction(helmet);
		if (before > 0.2f && after <= 0.2f) p.sendOverlayMessage(Component.translatable("message.matriochka.snorkel.low").withStyle(ChatFormatting.GOLD));
		if (after <= 0) p.sendOverlayMessage(Component.translatable("message.matriochka.snorkel.empty").withStyle(ChatFormatting.RED));
		return true;
	}

	/** Hits wear a snorkel helmet much faster than ordinary armor; a hard knock also spills some air. */
	private static void afterDamage(LivingEntity entity, DamageSource source, float base, float taken, boolean blocked) {
		if (!(entity instanceof ServerPlayer p) || taken <= 0 || blocked) return;
		ItemStack h = worn(p);
		Defs.SnorkelDef d = def(h);
		if (d == null) return;
		float wear = taken * d.wear();
		int extra = (int) wear + (p.getRandom().nextFloat() < wear - (int) wear ? 1 : 0);
		if (taken >= 4) setTank(h, tank(h) - taken * (1f - 0.2f * d.tier()));
		if (extra > 0) {
			boolean warned = h.getMaxDamage() - h.getDamageValue() > h.getMaxDamage() / 5;
			h.hurtAndBreak(extra, p, EquipmentSlot.HEAD);
			if (warned && !h.isEmpty() && h.getMaxDamage() - h.getDamageValue() <= h.getMaxDamage() / 5) {
				p.sendOverlayMessage(Component.translatable("message.matriochka.snorkel.cracked").withStyle(ChatFormatting.RED));
			}
		}
	}

	/** Tooltip lines of a snorkel helmet: the air in its tank and its tier. */
	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		Defs.SnorkelDef d = def(stack);
		if (d == null) return;
		int left = Math.round(tank(stack));
		out.accept(Component.translatable("tooltip.matriochka.tank", left / 60, String.format("%02d", left % 60), d.tank() / 60, Math.round(fraction(stack) * 100))
			.withStyle(fraction(stack) < 0.25f ? ChatFormatting.RED : ChatFormatting.AQUA));
		out.accept(Component.translatable("tooltip.matriochka.snorkel_tier", d.tier(), d.depth()).withStyle(ChatFormatting.DARK_AQUA));
	}
}
