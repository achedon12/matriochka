package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.rules.PlayerState;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;

/**
 * How the Surface answers karma, and the diamond gate on villager trades. Villagers lower their prices by 10% from
 * karma +25 and raise them from -25, as the peoples of the worlds do; from -50 one villager in three turns the player
 * away. Killing an innocent (a villager or one of the peoples) costs karma. Until the group has beaten World 5, villager
 * offers that involve diamonds are put aside, and they come back once it has.
 */
public final class Karma {
	public static final int TIER1 = 25, TIER2 = 50;
	/** Diamond offers a villager keeps aside until a player who has finished World 5 trades with it. */
	public static final AttachmentType<MerchantOffers> HELD = AttachmentRegistry.<MerchantOffers>builder()
		.persistent(MerchantOffers.CODEC)
		.buildAndRegister(Matriochka.id("held_offers"));

	private Karma() {}

	public static void init() {
		UseEntityCallback.EVENT.register((player, level, hand, entity, hit) -> {
			if (!(player instanceof ServerPlayer sp) || !(entity instanceof AbstractVillager v) || entity instanceof MatrioNpc) return InteractionResult.PASS;
			if (v.isBaby() || !v.isAlive() || v.isTrading()) return InteractionResult.PASS;
			gateDiamonds(sp, v);
			return react(sp, v) ? InteractionResult.PASS : InteractionResult.FAIL;
		});
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (!(source.getEntity() instanceof ServerPlayer p) || !(entity instanceof AbstractVillager)) return;
			innocentKilled(p);
		});
	}

	/** Price change, as a fraction of the base cost, for a player's karma. */
	public static int priceShift(int karma, int baseCost) {
		int step = Math.max(1, baseCost / 10);
		if (karma >= TIER1) return -step;
		if (karma <= -TIER1) return step;
		return 0;
	}

	/** Called after a villager computes its special prices for a trading player. */
	public static void adjustPrices(Villager villager, Player player) {
		if (!(player instanceof ServerPlayer sp)) return;
		int karma = PlayerState.of(sp).karma();
		for (MerchantOffer o : villager.getOffers()) {
			int d = priceShift(karma, o.getBaseCostA().getCount());
			if (d != 0) o.addToSpecialPriceDiff(d);
		}
	}

	/** One villager in three turns away a player of karma -50 or lower; the others look on, warmly or not. */
	public static boolean react(ServerPlayer p, AbstractVillager v) {
		int karma = PlayerState.of(p).karma();
		ServerLevel level = (ServerLevel) p.level();
		if (karma <= -TIER2 && hostile(v)) {
			level.sendParticles(ParticleTypes.ANGRY_VILLAGER, v.getX(), v.getEyeY() + 0.3, v.getZ(), 4, 0.3, 0.2, 0.3, 0);
			level.playSound(null, v.blockPosition(), SoundEvents.VILLAGER_NO, SoundSource.NEUTRAL, 1f, 1f);
			p.sendSystemMessage(Component.translatable("message.matriochka.npc_hostile").withStyle(ChatFormatting.GRAY));
			return false;
		}
		if (karma >= TIER2) level.sendParticles(ParticleTypes.HAPPY_VILLAGER, v.getX(), v.getEyeY() + 0.3, v.getZ(), 5, 0.3, 0.2, 0.3, 0);
		else if (karma <= -TIER1) level.sendParticles(ParticleTypes.SMOKE, v.getX(), v.getEyeY() + 0.3, v.getZ(), 3, 0.2, 0.1, 0.2, 0);
		return true;
	}

	/** The same villagers always refuse: a third of them, picked by their identity. */
	public static boolean hostile(AbstractVillager v) {
		return Math.floorMod(v.getUUID().getLeastSignificantBits(), 3) == 0;
	}

	public static boolean involvesDiamond(MerchantOffer o) {
		return diamond(o.getResult()) || diamond(o.getCostA()) || o.getItemCostB().map(c -> diamond(new ItemStack(c.item()))).orElse(false);
	}

	private static boolean diamond(ItemStack s) {
		return !s.isEmpty() && BuiltInRegistries.ITEM.getKey(s.getItem()).getPath().contains("diamond");
	}

	/** Puts diamond offers aside for players whose group has not beaten World 5, and gives them back afterwards. */
	public static void gateDiamonds(ServerPlayer p, AbstractVillager v) {
		MerchantOffers offers = v.getOffers();
		MerchantOffers held = v.getAttached(HELD);
		boolean open = !Config.gates() || p.isCreative() || MatrioData.get(p.level().getServer()).defeated(p, 5);
		if (open) {
			if (held != null && !held.isEmpty()) {
				offers.addAll(held);
				v.removeAttached(HELD);
			}
			return;
		}
		MerchantOffers moved = held == null ? new MerchantOffers() : held;
		boolean changed = offers.removeIf(o -> {
			if (!involvesDiamond(o)) return false;
			moved.add(o);
			return true;
		});
		if (changed) v.setAttached(HELD, moved);
	}

	/** Killing a villager or one of the peoples of the worlds: -5 karma, less when it becomes a habit. */
	public static void innocentKilled(ServerPlayer p) {
		PlayerState ps = PlayerState.of(p);
		int n = ps.counter("innocents");
		ps.addCounter("innocents", 1);
		ps.addKarma(-Math.max(1, 5 - n / 4));
		ps.progress("kill", "innocent", 1);
	}
}
