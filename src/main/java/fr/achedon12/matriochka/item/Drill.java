package fr.achedon12.matriochka.item;

import com.mojang.serialization.Codec;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The World 2 Drill mines a 3 x 3 square across the face it looks at, and every square burns a little Blazing Rock:
 * one rock feeds eight squares, taken from the inventory when the tank runs dry. Without fuel, or when sneaking, it
 * mines one block like a pickaxe.
 */
public final class Drill {
	public static final int FUEL_PER_ROCK = 8;
	public static final DataComponentType<Integer> FUEL = Registry.register(BuiltInRegistries.DATA_COMPONENT_TYPE, Matriochka.id("drill_fuel"),
		DataComponentType.<Integer>builder().persistent(Codec.intRange(0, FUEL_PER_ROCK)).networkSynchronized(ByteBufCodecs.VAR_INT).build());
	private static boolean busy;

	private Drill() {}

	public static void init() {
		PlayerBlockBreakEvents.AFTER.register((level, player, pos, state, be) -> {
			if (busy || !(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl)) return;
			ItemStack drill = sp.getMainHandItem();
			if (!drill.is(ModContent.item("drill")) || sp.isSecondaryUseActive()) return;
			burst(sl, sp, drill, pos, state);
		});
	}

	public static boolean isDrill(ItemStack stack) {
		return stack.is(ModContent.item("drill"));
	}

	public static int fuel(ItemStack stack) {
		return Math.max(0, stack.getOrDefault(FUEL, 0));
	}

	/** Takes one charge, burning a Blazing Rock from the inventory when the tank is empty. False when there is nothing to burn. */
	public static boolean burn(ServerPlayer player, ItemStack drill) {
		int fuel = fuel(drill);
		if (fuel <= 0 && !player.isCreative()) {
			Inventory inv = player.getInventory();
			var rock = ModContent.item("blazing_rock");
			for (int i = 0; i < inv.getContainerSize() && fuel <= 0; i++) {
				ItemStack s = inv.getItem(i);
				if (s.is(rock)) {
					s.shrink(1);
					fuel = FUEL_PER_ROCK;
					player.level().playSound(null, player.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 0.5f, 1.4f);
				}
			}
			if (fuel <= 0) return false;
		}
		if (!player.isCreative()) drill.set(FUEL, Math.max(0, fuel - 1));
		return true;
	}

	/** The square of blocks around a mined one, across the face the player is looking at. */
	public static BlockPos[] square(ServerPlayer player, BlockPos center) {
		Direction.Axis axis;
		if (Math.abs(player.getXRot()) > 50) axis = Direction.Axis.Y;
		else axis = player.getDirection().getAxis();
		BlockPos[] out = new BlockPos[8];
		int k = 0;
		for (int a = -1; a <= 1; a++) {
			for (int b = -1; b <= 1; b++) {
				if (a == 0 && b == 0) continue;
				out[k++] = switch (axis) {
					case Y -> center.offset(a, 0, b);
					case X -> center.offset(0, a, b);
					default -> center.offset(a, b, 0);
				};
			}
		}
		return out;
	}

	private static void burst(ServerLevel level, ServerPlayer player, ItemStack drill, BlockPos center, BlockState mined) {
		BlockPos[] around = square(player, center);
		boolean any = false;
		for (BlockPos p : around) any |= mineable(level, player, drill, p);
		if (!any) return;
		if (!burn(player, drill)) {
			if (level.getGameTime() % 40 < 20) player.sendOverlayMessage(Component.translatable("message.matriochka.drill.empty").withStyle(ChatFormatting.GOLD));
			return;
		}
		busy = true;
		try {
			for (BlockPos p : around) {
				if (!isDrill(player.getMainHandItem())) break;
				if (mineable(level, player, drill, p)) player.gameMode.destroyBlock(p);
			}
		} finally {
			busy = false;
		}
	}

	/** Blocks the drill takes along: breakable, mined correctly by it, never a block entity of the mod. */
	private static boolean mineable(ServerLevel level, ServerPlayer player, ItemStack drill, BlockPos p) {
		BlockState s = level.getBlockState(p);
		if (s.isAir() || !s.getFluidState().isEmpty() && s.getBlock() instanceof net.minecraft.world.level.block.LiquidBlock) return false;
		float hardness = s.getDestroySpeed(level, p);
		if (hardness < 0 || hardness > 50) return false;
		if (level.getBlockEntity(p) instanceof fr.achedon12.matriochka.block.DataBlockEntity) return false;
		if (s.requiresCorrectToolForDrops() && !drill.isCorrectToolForDrops(s)) return false;
		return player.mayInteract(level, p);
	}

	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		out.accept(Component.translatable("tooltip.matriochka.drill.fuel", fuel(stack), FUEL_PER_ROCK).withStyle(ChatFormatting.GOLD));
		out.accept(Component.translatable("tooltip.matriochka.drill.sneak").withStyle(ChatFormatting.DARK_GRAY));
	}
}
