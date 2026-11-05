package fr.achedon12.matriochka.item;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.Config;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.WorldZero;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

/**
 * Nesting the ten hidden dolls. Hold the smallest one (or the dolls already nested) in the main hand and the next
 * doll in the other hand, then use: if it is the right one, it closes around the others. A doll that does not belong
 * rattles and is refused. The order is {@link Content#NEST_ORDER}; once the tenth closes, the Nested Dolls become the
 * Whole Matryoshka, which opens onto World 0 after the Unfinished has fallen.
 */
public final class Nesting {
	private Nesting() {}

	/** Rank of a hidden doll in the nesting order (0 = the smallest), or -1. */
	public static int rank(ItemStack s) {
		String id = ModContent.idOf(s.getItem());
		if (!id.startsWith("hidden_doll_")) return -1;
		int w = Integer.parseInt(id.substring("hidden_doll_".length()));
		for (int i = 0; i < Content.NEST_ORDER.length; i++) if (Content.NEST_ORDER[i] == w) return i;
		return -1;
	}

	/** How many dolls a stack holds nested: 1 for the smallest hidden doll, k for Nested Dolls, 10 for the whole; else 0. */
	public static int depth(ItemStack s) {
		if (s.isEmpty()) return 0;
		String id = ModContent.idOf(s.getItem());
		if (id.equals("whole_matryoshka")) return 10;
		if (id.equals("nested_dolls")) {
			var cd = s.get(DataComponents.CUSTOM_DATA);
			return cd == null ? 0 : cd.copyTag().getIntOr("depth", 0);
		}
		return rank(s) == 0 ? 1 : 0;
	}

	public static ItemStack nested(int depth) {
		if (depth >= 10) return new ItemStack(ModContent.item("whole_matryoshka"));
		ItemStack s = new ItemStack(ModContent.item("nested_dolls"));
		CompoundTag t = new CompoundTag();
		t.putInt("depth", depth);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		s.set(DataComponents.CUSTOM_NAME, Component.translatable("item.matriochka.nested_dolls.n", depth));
		return s;
	}

	/** Using a hidden doll, the Nested Dolls or the Whole Matryoshka. */
	public static void use(ServerPlayer p, InteractionHand hand) {
		ServerLevel level = (ServerLevel) p.level();
		ItemStack main = p.getMainHandItem(), off = p.getOffhandItem();
		if (hand == InteractionHand.MAIN_HAND && ModContent.idOf(main.getItem()).equals("whole_matryoshka")) {
			open(p);
			return;
		}
		boolean offIsDoll = rank(off) >= 0;
		if (hand == InteractionHand.OFF_HAND || !offIsDoll) {
			p.sendOverlayMessage(Component.translatable("message.matriochka.nest.hollow"));
			level.playSound(null, p.blockPosition(), SoundEvents.WOOD_HIT, SoundSource.PLAYERS, 0.7f, 1.4f);
			return;
		}
		int depth = depth(main);
		if (depth <= 0 || rank(off) != depth) {
			rattle(p, level);
			return;
		}
		int next = depth + 1;
		off.shrink(1);
		main.shrink(1);
		p.setItemInHand(InteractionHand.MAIN_HAND, nested(next));
		level.playSound(null, p.blockPosition(), SoundEvents.CHEST_CLOSE, SoundSource.PLAYERS, 0.8f, 1.8f - next * 0.08f);
		level.sendParticles(ParticleTypes.WAX_ON, p.getX(), p.getY() + 1.2, p.getZ(), 10, 0.3, 0.3, 0.3, 0.05);
		if (next >= 10) {
			p.sendSystemMessage(Component.translatable("message.matriochka.nest.whole").withStyle(ChatFormatting.GOLD));
			level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 0.5f);
			fr.achedon12.matriochka.world.Achievements.grant(p, "all_dolls");
		} else {
			p.sendOverlayMessage(Component.translatable("message.matriochka.nest.closed", next).withStyle(ChatFormatting.YELLOW));
		}
	}

	private static void rattle(ServerPlayer p, ServerLevel level) {
		p.sendOverlayMessage(Component.translatable("message.matriochka.nest.rattle").withStyle(ChatFormatting.RED));
		for (int i = 0; i < 3; i++) level.playSound(null, p.blockPosition(), SoundEvents.CHAIN_PLACE, SoundSource.PLAYERS, 0.6f, 1.6f + i * 0.2f);
		p.getCooldowns().addCooldown(p.getMainHandItem(), 20);
	}

	/** The Whole Matryoshka opens onto World 0 once the group has beaten the Unfinished. */
	private static void open(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		if (Config.gates() && !p.isCreative() && !data.defeated(p, 10)) {
			p.sendOverlayMessage(Component.translatable("message.matriochka.nest.sealed").withStyle(ChatFormatting.RED));
			((ServerLevel) p.level()).playSound(null, p.blockPosition(), SoundEvents.CHEST_LOCKED, SoundSource.PLAYERS, 1f, 0.6f);
			return;
		}
		WorldZero.enter(p);
	}
}
