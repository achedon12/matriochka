package fr.achedon12.matriochka.item;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;

/**
 * Souls kept in structure chests. The design counts about 100 souls per world from structure chests (10 chests of 10
 * souls): a common chest holds one or two Soul Shards (5 souls each), a rare one two or three, a vault a Soul Vessel
 * (20 souls) and now and then a shard more, a little more often in the deeper worlds. Using one frees its souls, neutral
 * ones that do not move karma (only the Soul Altar does).
 */
public final class SoulVessels {
	public static final int SHARD = 5, VESSEL = 20;

	private SoulVessels() {}

	/** Souls one item holds; 0 for anything else. */
	public static int souls(ItemStack stack) {
		String id = ModContent.idOf(stack.getItem());
		return switch (id) {
			case "soul_shard" -> SHARD;
			case "soul_vessel" -> VESSEL;
			default -> 0;
		};
	}

	public static boolean is(ItemStack stack) {
		return souls(stack) > 0;
	}

	/** World factor of the chest souls: 0.84 in World 1, 1.2 in World 10. */
	public static float worldFactor(int world) {
		return 0.8f + 0.04f * Math.max(1, Math.min(10, world));
	}

	/** The soul items of one structure chest of a tier (0 common, 1 rare, 2 vault) in a world. Empty on the Surface. */
	public static java.util.List<ItemStack> loot(int world, int tier, RandomSource r) {
		java.util.List<ItemStack> out = new java.util.ArrayList<>();
		if (world < 1 || world > 10) return out;
		float f = worldFactor(world);
		int shards = switch (tier) {
			case 0 -> 1 + (r.nextFloat() < 0.4f * f ? 1 : 0);
			case 1 -> 2 + (r.nextFloat() < 0.5f * f ? 1 : 0);
			default -> r.nextFloat() < f - 0.5f ? 1 : 0;
		};
		if (tier >= 2) out.add(new ItemStack(ModContent.item("soul_vessel")));
		if (shards > 0) out.add(new ItemStack(ModContent.item("soul_shard"), shards));
		return out;
	}

	/** Frees the souls of one item, or of the whole stack when sneaking. */
	public static void release(ServerPlayer player, ItemStack stack) {
		int each = souls(stack);
		if (each <= 0 || stack.isEmpty()) return;
		int n = player.isShiftKeyDown() ? stack.getCount() : 1;
		int souls = each * n;
		PlayerState ps = PlayerState.of(player);
		ps.addSouls(souls);
		stack.consume(n, player);
		ServerLevel level = (ServerLevel) player.level();
		level.sendParticles(ParticleTypes.SOUL, player.getX(), player.getY() + 1, player.getZ(), 6 + Math.min(24, souls / 2), 0.4, 0.5, 0.4, 0.03);
		level.playSound(null, player.blockPosition(), fr.achedon12.matriochka.content.Sounds.STATION_SOUL_ALTAR, SoundSource.PLAYERS, 0.6f, 1.4f);
		player.sendOverlayMessage(Component.translatable("message.matriochka.souls_freed", souls, ps.souls()).withStyle(ChatFormatting.AQUA));
		ps.sync();
	}
}
