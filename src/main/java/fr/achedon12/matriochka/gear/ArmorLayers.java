package fr.achedon12.matriochka.gear;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import org.jspecify.annotations.Nullable;

/**
 * Layered armor: a piece of armor can carry lacquer layers laid on at the Class Table. The outer layer takes the wear
 * the armor would take; when it breaks the next one takes over, and the armor itself only wears once the last layer
 * is gone. Each intact layer adds one point of armor. The class decides how many layers a piece holds: one, plus one
 * at class level 3 and 5, plus one for Guardian gear, whose layers are also half as sturdy again.
 */
public final class ArmorLayers {
	public record Layers(int count, int wear) {
		/** A hand-made component cannot ask for more layers than a piece can ever hold, nor negative wear. */
		public Layers {
			count = Math.max(0, Math.min(MAX_LAYERS, count));
			wear = Math.max(0, wear);
		}

		public static final Codec<Layers> CODEC = RecordCodecBuilder.create(i -> i.group(
			Codec.INT.fieldOf("count").forGetter(Layers::count),
			Codec.INT.fieldOf("wear").forGetter(Layers::wear)).apply(i, Layers::new));
		public static final StreamCodec<RegistryFriendlyByteBuf, Layers> STREAM = StreamCodec.composite(
			ByteBufCodecs.VAR_INT, Layers::count, ByteBufCodecs.VAR_INT, Layers::wear, Layers::new);
	}

	public static final DataComponentType<Layers> LAYERS = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, Matriochka.id("layers"),
		DataComponentType.<Layers>builder().persistent(Layers.CODEC).networkSynchronized(Layers.STREAM).build());

	/** One, plus class levels 3 and 5, plus the Guardian class. */
	public static final int MAX_LAYERS = 4;

	private ArmorLayers() {}

	public static void init() {}

	public static int count(ItemStack stack) {
		Layers l = stack.get(LAYERS);
		return l == null ? 0 : l.count();
	}

	/** How many layers this piece can hold, from its class and class level. */
	public static int max(ItemStack stack) {
		GearClasses.Gear g = stack.get(GearClasses.GEAR);
		int level = g == null ? 1 : g.level();
		int m = 1 + (level >= 3 ? 1 : 0) + (level >= 5 ? 1 : 0);
		if (g != null && g.cls().equals("guardian")) m++;
		return m;
	}

	/** Wear one layer can take before it breaks. */
	public static int capacity(ItemStack stack) {
		int c = Math.max(40, stack.getMaxDamage() / 3);
		GearClasses.Gear g = stack.get(GearClasses.GEAR);
		if (g != null && g.cls().equals("guardian")) c = c * 3 / 2;
		return c;
	}

	/** Lays one more layer under the outer one. Returns a message key on failure, null on success. */
	public static String add(ItemStack stack) {
		if (GearClasses.kind(stack) != GearClasses.Kind.ARMOR) return "message.matriochka.layer.not_armor";
		Layers l = stack.getOrDefault(LAYERS, new Layers(0, 0));
		if (l.count() >= max(stack)) return "message.matriochka.layer.full";
		stack.set(LAYERS, new Layers(l.count() + 1, l.wear()));
		GearClasses.refresh(stack);
		return null;
	}

	/**
	 * Called for every durability loss of an item: the outer layer takes it instead of the armor. Returns true when the
	 * layers absorbed it.
	 */
	public static boolean absorb(ItemStack stack, int amount, @Nullable ServerLevel level, @Nullable ServerPlayer player) {
		Layers l = stack.get(LAYERS);
		if (l == null || l.count() <= 0 || amount <= 0) return false;
		int cap = capacity(stack);
		int wear = l.wear() + amount, count = l.count();
		boolean broke = false;
		while (wear >= cap && count > 0) {
			wear -= cap;
			count--;
			broke = true;
		}
		if (count == 0) wear = 0;
		stack.set(LAYERS, new Layers(count, wear));
		if (broke) {
			GearClasses.refresh(stack);
			if (player != null) {
				player.level().playSound(null, player.blockPosition(), SoundEvents.SHIELD_BREAK.value(), SoundSource.PLAYERS, 0.8f, 1.3f);
				player.sendOverlayMessage(Component.translatable(count > 0 ? "message.matriochka.layer.broke" : "message.matriochka.layer.last", count)
					.withStyle(ChatFormatting.GOLD));
			}
		}
		return true;
	}

	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		Layers l = stack.get(LAYERS);
		if (l == null || l.count() <= 0) return;
		int left = Math.round(100f * (capacity(stack) - l.wear()) / capacity(stack));
		out.accept(Component.translatable("tooltip.matriochka.layers", l.count(), max(stack), left).withStyle(ChatFormatting.YELLOW));
	}
}
