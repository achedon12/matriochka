package fr.achedon12.matriochka.entity;

import com.geckolib.animatable.GeoEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.constant.DefaultAnimations;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.Level;
import org.jspecify.annotations.Nullable;

/** The people of each world (and the Doll Peddler of the surface). Prices follow the trading player's karma. */
public class MatrioNpc extends AbstractVillager implements GeoEntity {
	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
	public final Defs.NpcDef def;

	public MatrioNpc(EntityType<? extends AbstractVillager> type, Level level, Defs.NpcDef def) {
		super(type, level);
		this.def = def;
	}

	public static AttributeSupplier.Builder attributes() {
		return net.minecraft.world.entity.Mob.createMobAttributes().add(Attributes.MAX_HEALTH, 30).add(Attributes.MOVEMENT_SPEED, 0.45);
	}

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(1, new PanicGoal(this, 0.6));
		goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.35));
		goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8f));
	}

	private static String[][] tradesFor(int world) {
		// {cost item, cost count, result item, result count}
		return switch (world) {
			case 0 -> new String[][]{{"minecraft:emerald", "6", "chance_doll", "1"}, {"minecraft:emerald", "3", "return_thread", "2"}, {"minecraft:emerald", "2", "wool_thread", "4"}, {"minecraft:gold_ingot", "4", "painted_wood", "16"}};
			case 1 -> new String[][]{{"spores", "8", "antidote", "2"}, {"roots", "6", "root_broth", "2"}, {"chitin", "2", "filter_mask", "1"}};
			case 2 -> new String[][]{{"blazing_rock", "8", "cooling_water", "3"}, {"ash_ingot", "3", "minecraft:redstone", "8"}, {"giant_ore", "2", "ash_ingot", "3"}};
			case 3 -> new String[][]{{"sealed_fragment", "3", "lockpick_kit", "2"}, {"sealed_fragment", "6", "dungeon_key", "1"}, {"minecraft:bread", "4", "labyrinth_map", "1"}};
			case 4 -> new String[][]{{"ray_membrane", "6", "cloud_fruit", "3"}, {"storm_essence", "2", "minecraft:lightning_rod", "1"}};
			case 5 -> new String[][]{{"shadow_shard", "2", "silence_balm", "3"}, {"minecraft:torch", "16", "mute_mushroom", "2"}};
			case 6 -> new String[][]{{"unstable_alloy", "2", "stabilizer", "3"}, {"inverted_crystal", "1", "flipped_apple", "3"}};
			case 7 -> new String[][]{{"abyssal_salt", "3", "oxygen_capsule", "3"}, {"pressure_pearl", "1", "apnea_kelp", "4"}};
			case 8 -> new String[][]{{"temporal_sand", "4", "season_preserve", "2"}, {"season_fragment", "1", "season_jam", "3"}};
			case 9 -> new String[][]{{"terrain_fragment", "3", "anchor", "2"}, {"terrain_fragment", "5", "anchor_bread", "3"}};
			default -> new String[][]{{"artisan_thread", "4", "journal_page", "1"}, {"artisan_thread", "6", "workshop_feast", "1"}};
		};
	}

	@Override
	protected void updateTrades(ServerLevel level) {
		MerchantOffers offers = getOffers();
		for (String[] t : tradesFor(def.world())) {
			var cost = fr.achedon12.matriochka.block.Stations.resolve(t[0]);
			var res = fr.achedon12.matriochka.block.Stations.resolve(t[2]);
			offers.add(new MerchantOffer(new ItemCost(cost, Integer.parseInt(t[1])), new ItemStack(res, Integer.parseInt(t[3])), 12, 2, 0.05f));
		}
	}

	@Override
	public InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (!isAlive() || isTrading()) return super.mobInteract(player, hand);
		if (player instanceof ServerPlayer sp) {
			if (speakOfDolls(sp)) return InteractionResult.SUCCESS;
			if (getOffers().isEmpty()) return InteractionResult.CONSUME;
			int karma = PlayerState.of(sp).karma();
			for (MerchantOffer o : getOffers()) {
				o.resetSpecialPriceDiff();
				int base = o.getBaseCostA().getCount();
				if (karma >= 25) o.addToSpecialPriceDiff(-Math.max(1, base / 10));
				else if (karma <= -25) o.addToSpecialPriceDiff(Math.max(1, base / 10));
			}
			if (karma <= -50 && def.world() > 0 && random.nextInt(3) == 0) {
				sp.sendSystemMessage(Component.translatable("message.matriochka.npc_hostile"));
				return InteractionResult.FAIL;
			}
			setTradingPlayer(sp);
			openTradingScreen(sp, getDisplayName(), 1);
			PlayerState.of(sp).progress("trade", def.id(), 1);
		}
		return InteractionResult.SUCCESS;
	}

	/**
	 * Show a people its hidden doll and it tells which doll sleeps inside it; the Peddler knows how dolls nest, the
	 * Old Apprentices know what the whole one opens, and the Peddler remembers the previous cycle. Returns true when
	 * the line replaces the trade.
	 */
	private boolean speakOfDolls(ServerPlayer sp) {
		var held = sp.getMainHandItem();
		String id = fr.achedon12.matriochka.content.ModContent.idOf(held.getItem());
		String line = null;
		if (def.world() > 0 && def.world() <= 10 && id.equals("hidden_doll_" + def.world())) line = "message.matriochka.doll_line." + def.world();
		else if (def.world() == 0 && (fr.achedon12.matriochka.item.Nesting.rank(held) >= 0 || id.equals("nested_dolls"))) line = "message.matriochka.peddler.dolls";
		else if (def.world() == 10 && (id.equals("whole_matryoshka") || id.equals("nested_dolls"))) line = "message.matriochka.apprentice.whole";
		boolean remembers = line == null && def.world() == 0 && fr.achedon12.matriochka.world.Endings.any(PlayerState.of(sp)) && random.nextInt(3) == 0;
		if (remembers) line = "message.matriochka.peddler.cycle";
		if (line == null) return false;
		sp.sendSystemMessage(getDisplayName().copy().withStyle(net.minecraft.ChatFormatting.GOLD).append(": ")
			.append(Component.translatable(line).withStyle(net.minecraft.ChatFormatting.ITALIC, net.minecraft.ChatFormatting.GRAY)));
		playSound(net.minecraft.sounds.SoundEvents.VILLAGER_AMBIENT, 0.8f, 0.9f);
		return !remembers;
	}

	@Override
	protected void rewardTradeXp(MerchantOffer offer) {}

	@Override
	public @Nullable AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
		return null;
	}

	@Override
	public boolean removeWhenFarAway(double d) {
		return false;
	}

	@Override
	public void tick() {
		super.tick();
		// a wandering Peddler moves on after two days
		if (!level().isClientSide() && tickCount > 48000 && entityTags().contains("wanderer")) discard();
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(DefaultAnimations.genericWalkIdleController());
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}
}
