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
		/** Levels outside 1..5 and absurd change counts (a hand-made item component) are brought back in range. */
		public Gear {
			level = clampLevel(level);
			changes = Math.max(0, Math.min(MAX_CHANGES, changes));
		}

		public static final Codec<Gear> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.STRING.fieldOf("class").forGetter(Gear::cls),
			Codec.intRange(1, 5).fieldOf("level").forGetter(Gear::level),
			Codec.intRange(0, MAX_CHANGES).fieldOf("changes").forGetter(Gear::changes)).apply(i, Gear::new));
		public static final StreamCodec<RegistryFriendlyByteBuf, Gear> STREAM = StreamCodec.composite(
			ByteBufCodecs.STRING_UTF8, Gear::cls, ByteBufCodecs.VAR_INT, Gear::level, ByteBufCodecs.VAR_INT, Gear::changes, Gear::new);
	}

	public static final DataComponentType<Gear> GEAR = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, Matriochka.id("gear"),
		DataComponentType.<Gear>builder().persistent(Gear.CODEC).networkSynchronized(Gear.STREAM).build());

	public static final int MAX_LEVEL = 5;
	/** The reroll cost doubles with each change: past this it would overflow. */
	public static final int MAX_CHANGES = 20;

	public static int clampLevel(int level) {
		return Math.max(1, Math.min(MAX_LEVEL, level));
	}

	/** Class bonus for a level, safe for any level value. */
	public static float bonus(int level) {
		return BONUS[clampLevel(level)];
	}

	public static final String[] ARMOR = {"guardian", "berserker", "prowler", "reaper", "survivor"};
	public static final String[] WEAPON = {"berserker", "prowler", "reaper", "survivor"};
	public static final String[] TOOL = {"prospector"};
	public static final float[] BONUS = {0f, 0f, 0.10f, 0.20f, 0.35f, 0.50f};
	public static final int[] UPGRADE_COST = {0, 0, 10, 30, 90, 270};
	/** Shell Shards (boss material) needed for each target level, on top of the souls. */
	public static final int[] SHARD_COST = {0, 0, 1, 1, 2, 2};
	private static final Identifier MOD_ID = Matriochka.id("class_bonus");
	private static final Identifier LAYER_ID = Matriochka.id("armor_layers");

	private GearClasses() {}

	public static void init() {
		ArmorLayers.init();
		// Prowler gear: a chance to slip out of the way of a blow
		net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) ->
			!(entity instanceof net.minecraft.server.level.ServerPlayer p && dodges(p, source)));
	}

	/** Whether this blow misses a player in Prowler gear (rolls the chance and plays the feedback). */
	public static boolean dodges(net.minecraft.server.level.ServerPlayer p, net.minecraft.world.damagesource.DamageSource source) {
		if (source.getEntity() == null || source.getEntity() == p) return false;
		if (source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return false;
		float chance = dodgeChance(p);
		if (chance <= 0 || p.getRandom().nextFloat() >= chance) return false;
		dodged(p);
		return true;
	}

	/** Dodge feedback: a puff of air, a swish and a word over the hotbar. */
	private static void dodged(net.minecraft.server.level.ServerPlayer p) {
		if (p.level() instanceof net.minecraft.server.level.ServerLevel l) {
			l.sendParticles(net.minecraft.core.particles.ParticleTypes.CLOUD, p.getX(), p.getY() + 0.8, p.getZ(), 8, 0.3, 0.4, 0.3, 0.02);
			l.playSound(null, p.blockPosition(), net.minecraft.sounds.SoundEvents.PLAYER_ATTACK_SWEEP, net.minecraft.sounds.SoundSource.PLAYERS, 0.6f, 1.8f);
		}
		p.sendOverlayMessage(Component.translatable("message.matriochka.dodge").withStyle(ChatFormatting.AQUA));
	}

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
		return 20 << Math.min(MAX_CHANGES, g.changes());
	}

	public static int rerollCost(ItemStack stack) {
		Gear g = stack.get(GEAR);
		return g == null ? 20 : 20 << Math.min(MAX_CHANGES, g.changes());
	}

	public static void apply(ItemStack stack, Gear gear) {
		stack.set(GEAR, gear);
		refresh(stack);
	}

	/** Rebuilds the stack's attribute modifiers from its item, its class and its armor layers. */
	public static void refresh(ItemStack stack) {
		ItemAttributeModifiers base = stack.getItem().components().getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
		Equippable eq = stack.get(DataComponents.EQUIPPABLE);
		EquipmentSlotGroup group = eq != null ? EquipmentSlotGroup.bySlot(eq.slot()) : EquipmentSlotGroup.MAINHAND;
		ItemAttributeModifiers mods = base;
		Gear gear = stack.get(GEAR);
		if (gear != null) {
			float mult = 1f + bonus(gear.level());
			int i = 0;
			for (Bonus b : bonuses(gear.cls(), kind(stack), mult, base)) {
				mods = mods.withModifierAdded(b.attr, new AttributeModifier(MOD_ID.withSuffix("_" + i++), b.amount, b.op), group);
			}
		}
		int layers = ArmorLayers.count(stack);
		if (layers > 0) mods = mods.withModifierAdded(Attributes.ARMOR, new AttributeModifier(LAYER_ID, layers, AttributeModifier.Operation.ADD_VALUE), group);
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
			if (g != null && g.cls().equals("reaper")) s += 0.03f * (1 + bonus(g.level()));
		}
		return s;
	}

	/** Extra share of souls a player harvests from creatures and bosses, from Reaper gear (0..1). */
	public static float soulGain(net.minecraft.world.entity.LivingEntity e) {
		float s = 0;
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			Gear g = e.getItemBySlot(slot).get(GEAR);
			if (g != null && g.cls().equals("reaper")) s += 0.05f * (1 + bonus(g.level()));
		}
		return Math.min(1f, s + fr.achedon12.matriochka.replay.Talents.sum(e, "souls"));
	}

	/**
	 * Souls a Reaper earns for a kill worth base souls: the bonus share is added, its fraction paid by chance, so even a
	 * creature worth nothing may yield a soul.
	 */
	public static int reapSouls(net.minecraft.world.entity.LivingEntity e, int base, RandomSource random) {
		float gain = soulGain(e);
		if (gain <= 0) return base;
		float extra = Math.max(base, 1) * gain;
		int whole = (int) extra;
		return base + whole + (random.nextFloat() < extra - whole ? 1 : 0);
	}

	/** Chance to dodge an attack, from Prowler gear (0..0.3). */
	public static float dodgeChance(net.minecraft.world.entity.LivingEntity e) {
		float s = 0;
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			Gear g = e.getItemBySlot(slot).get(GEAR);
			if (g != null && g.cls().equals("prowler")) s += 0.025f * (1 + bonus(g.level()));
		}
		return Math.min(0.3f, s);
	}

	/** Gauge reduction from survivor gear (0..0.6). */
	public static float survivorResistance(net.minecraft.world.entity.LivingEntity e) {
		float s = 0;
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			Gear g = e.getItemBySlot(slot).get(GEAR);
			if (g != null && g.cls().equals("survivor")) s += 0.06f * (1 + bonus(g.level()));
		}
		// Survivor talents add their share on top of the gear's, up to 85% in all
		return Math.min(0.6f, s) + Math.min(0.25f, fr.achedon12.matriochka.replay.Talents.sum(e, "resist"));
	}

	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		ArmorLayers.appendTooltip(stack, out);
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
