package fr.achedon12.matriochka.gear;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.equipment.Equippable;

/**
 * Equipment classes. Every weapon, tool or armor piece gets a random class when crafted; the Class Table raises its
 * level (1..5) and a Chance Doll rerolls it. Bonuses are written into the stack's attribute modifiers, server side.
 */
public final class GearClasses {
	public record Gear(String cls, int level, int changes) {
		public static final Codec<Gear> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.STRING.fieldOf("class").forGetter(Gear::cls),
			Codec.INT.fieldOf("level").forGetter(Gear::level),
			Codec.INT.fieldOf("changes").forGetter(Gear::changes)).apply(i, Gear::new));
		public static final StreamCodec<RegistryFriendlyByteBuf, Gear> STREAM = StreamCodec.composite(
			ByteBufCodecs.STRING_UTF8, Gear::cls, ByteBufCodecs.VAR_INT, Gear::level, ByteBufCodecs.VAR_INT, Gear::changes, Gear::new);
	}

	public static final DataComponentType<Gear> GEAR = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, Matriochka.id("gear"),
		DataComponentType.<Gear>builder().persistent(Gear.CODEC).networkSynchronized(Gear.STREAM).build());

	public static final String[] ARMOR = {"guardian", "berserker", "prowler", "reaper", "survivor"};
	public static final String[] WEAPON = {"berserker", "prowler", "reaper", "survivor"};
	public static final String[] TOOL = {"prospector"};
	public static final float[] BONUS = {0f, 0f, 0.10f, 0.20f, 0.35f, 0.50f};
	public static final int[] UPGRADE_COST = {0, 0, 10, 30, 90, 270};
	private static final Identifier MOD_ID = Matriochka.id("class_bonus");

	private GearClasses() {}

	public static void init() {}

	public enum Kind { ARMOR, WEAPON, TOOL, NONE }

	public static Kind kind(ItemStack stack) {
		if (stack.isEmpty() || stack.getMaxStackSize() > 1) return Kind.NONE;
		Equippable eq = stack.get(DataComponents.EQUIPPABLE);
		if (eq != null && eq.slot().isArmor()) return Kind.ARMOR;
		if (stack.has(DataComponents.WEAPON) || stack.is(net.minecraft.tags.ItemTags.SWORDS) || stack.is(net.minecraft.tags.ItemTags.AXES)) return Kind.WEAPON;
		if (stack.has(DataComponents.TOOL)) return Kind.TOOL;
		return Kind.NONE;
	}

	public static String[] pool(Kind k) {
		return switch (k) {
			case ARMOR -> ARMOR;
			case WEAPON -> WEAPON;
			case TOOL -> TOOL;
			default -> new String[0];
		};
	}

	/** Assigns a random class to a freshly crafted item, if it has none. */
	public static void roll(ItemStack stack, RandomSource random) {
		Kind k = kind(stack);
		if (k == Kind.NONE || stack.has(GEAR)) return;
		String[] p = pool(k);
		apply(stack, new Gear(p[random.nextInt(p.length)], 1, 0));
	}

	/** Rerolls to a different class (keeps level); returns the soul cost that was charged, -1 if impossible. */
	public static int reroll(ItemStack stack, RandomSource random) {
		Gear g = stack.get(GEAR);
		Kind k = kind(stack);
		if (g == null || k == Kind.NONE) return -1;
		String[] p = pool(k);
		if (p.length < 2) return -1;
		String next;
		do {
			next = p[random.nextInt(p.length)];
		} while (next.equals(g.cls()));
		apply(stack, new Gear(next, g.level(), g.changes() + 1));
		return 20 << g.changes();
	}

	public static int rerollCost(ItemStack stack) {
		Gear g = stack.get(GEAR);
		return g == null ? 20 : 20 << g.changes();
	}

	public static void apply(ItemStack stack, Gear gear) {
		stack.set(GEAR, gear);
		ItemAttributeModifiers base = stack.getItem().components().getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
		Equippable eq = stack.get(DataComponents.EQUIPPABLE);
		EquipmentSlotGroup group = eq != null ? EquipmentSlotGroup.bySlot(eq.slot()) : EquipmentSlotGroup.MAINHAND;
		float mult = 1f + BONUS[Math.max(1, Math.min(5, gear.level()))];
		List<Bonus> bonuses = bonuses(gear.cls(), kind(stack), mult, base);
		ItemAttributeModifiers mods = base;
		int i = 0;
		for (Bonus b : bonuses) {
			mods = mods.withModifierAdded(b.attr, new AttributeModifier(MOD_ID.withSuffix("_" + i++), b.amount, b.op), group);
		}
		stack.set(DataComponents.ATTRIBUTE_MODIFIERS, mods);
	}

	private record Bonus(Holder<Attribute> attr, double amount, AttributeModifier.Operation op) {}

	private static double baseValue(ItemAttributeModifiers base, Holder<Attribute> attr) {
		double v = 0;
		for (ItemAttributeModifiers.Entry e : base.modifiers()) {
			if (e.attribute().equals(attr) && e.modifier().operation() == AttributeModifier.Operation.ADD_VALUE) v += e.modifier().amount();
		}
		return v;
	}

	private static List<Bonus> bonuses(String cls, Kind kind, float mult, ItemAttributeModifiers base) {
		List<Bonus> out = new ArrayList<>();
		var add = AttributeModifier.Operation.ADD_VALUE;
		var pct = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;
		switch (cls) {
			case "guardian" -> {
				out.add(new Bonus(Attributes.ARMOR, Math.max(1, baseValue(base, Attributes.ARMOR) * 0.15) * mult, add));
				out.add(new Bonus(Attributes.KNOCKBACK_RESISTANCE, 0.04 * mult, add));
			}
			case "berserker" -> {
				if (kind == Kind.WEAPON) {
					out.add(new Bonus(Attributes.ATTACK_DAMAGE, Math.max(1, baseValue(base, Attributes.ATTACK_DAMAGE) * 0.08) * mult, add));
					out.add(new Bonus(Attributes.ATTACK_SPEED, 0.08 * mult, add));
				} else {
					out.add(new Bonus(Attributes.ATTACK_DAMAGE, 0.03 * mult, pct));
				}
			}
			case "prowler" -> out.add(new Bonus(Attributes.MOVEMENT_SPEED, 0.03 * mult, pct));
			case "reaper" -> out.add(new Bonus(Attributes.LUCK, 0.5 * mult, add));
			case "survivor" -> out.add(new Bonus(Attributes.MAX_HEALTH, 1.0 * mult, add));
			case "prospector" -> {
				out.add(new Bonus(Attributes.MINING_EFFICIENCY, 3.0 * mult, add));
				out.add(new Bonus(Attributes.LUCK, 0.5 * mult, add));
			}
			default -> {}
		}
		return out;
	}

	/** Life steal fraction for reaper gear worn/held by a player (sum over equipment). */
	public static float lifeSteal(net.minecraft.world.entity.LivingEntity e) {
		float s = 0;
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			Gear g = e.getItemBySlot(slot).get(GEAR);
			if (g != null && g.cls().equals("reaper")) s += 0.03f * (1 + BONUS[g.level()]);
		}
		return s;
	}

	/** Gauge reduction from survivor gear (0..0.6). */
	public static float survivorResistance(net.minecraft.world.entity.LivingEntity e) {
		float s = 0;
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			Gear g = e.getItemBySlot(slot).get(GEAR);
			if (g != null && g.cls().equals("survivor")) s += 0.06f * (1 + BONUS[g.level()]);
		}
		return Math.min(0.6f, s);
	}

	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		Gear g = stack.get(GEAR);
		if (g == null) return;
		out.accept(Component.translatable("tooltip.matriochka.class", Component.translatable("class.matriochka." + g.cls()), g.level())
			.withStyle(ChatFormatting.GOLD));
		out.accept(Component.translatable("class.matriochka." + g.cls() + ".desc").withStyle(ChatFormatting.DARK_AQUA));
	}

	/** Max class level allowed by the group's progression. */
	public static int maxLevel(int highestDefeatedWorld) {
		if (highestDefeatedWorld >= 8) return 5;
		if (highestDefeatedWorld >= 6) return 4;
		if (highestDefeatedWorld >= 4) return 3;
		if (highestDefeatedWorld >= 2) return 2;
		return 1;
	}
}
