package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Achievements;
import fr.achedon12.matriochka.world.MatrioData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/** Station logic shared by every station: conditions, ticking, crafting and the altar / class-table actions. */
public final class Stations {
	private Stations() {}

	public static Item resolve(String id) {
		if (id.contains(":")) return BuiltInRegistries.ITEM.getValue(Identifier.parse(id));
		return ModContent.item(id);
	}

	public static int count(Inventory inv, Item item) {
		int n = 0;
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(item)) n += s.getCount();
		}
		return n;
	}

	private static void take(Inventory inv, Item item, int n) {
		for (int i = 0; i < inv.getContainerSize() && n > 0; i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(item)) {
				int k = Math.min(n, s.getCount());
				s.shrink(k);
				n -= k;
			}
		}
	}

	/** Machine condition as shown in the screen: 1 = ready, 0 = not ready. Some stations also report a value. */
	public static int condition(ServerLevel level, BlockPos pos, String station, DataBlockEntity be) {
		return switch (station) {
			case "ash_foundry" -> { int h = heat(level, pos); yield h >= 1 && h <= 3 ? 1 : 0; }
			case "lightning_forge" -> be.data().getIntOr("charge", 0) > 0 ? 1 : 0;
			case "dark_altar" -> level.getMaxLocalRawBrightness(pos.above()) == 0 ? 1 : 0;
			case "abyssal_press" -> level.getFluidState(pos.above()).is(FluidTags.WATER) && level.getFluidState(pos.above(8)).is(FluidTags.WATER) ? 1 : 0;
			case "time_workshop" -> { long t = level.getDefaultClockTime() % 24000; yield (t > 22500 || t < 1500 || (t > 11500 && t < 13500)) ? 1 : 0; }
			case "spore_vat" -> 1;
			case "jailer_table" -> be.data().getIntOr("entered", 0) == 3 ? 1 : 0;
			default -> 1;
		};
	}

	/** Number of heat sources around the foundry (lava, magma, fire). */
	public static int heat(ServerLevel level, BlockPos pos) {
		int n = 0;
		for (Direction d : Direction.values()) {
			BlockState s = level.getBlockState(pos.relative(d));
			if (s.getFluidState().is(FluidTags.LAVA) || s.is(Blocks.MAGMA_BLOCK) || s.is(Blocks.FIRE) || s.is(Blocks.CAMPFIRE) || s.is(Blocks.SOUL_FIRE)) n++;
		}
		return n;
	}

	public static void tick(ServerLevel level, BlockPos pos, String station, DataBlockEntity be) {
		long t = level.getGameTime();
		if (station.equals("lightning_forge") && t % 200 == 0 && level.isThundering() && level.canSeeSky(pos.above())) {
			be.data().putInt("charge", Math.min(8, be.data().getIntOr("charge", 0) + 1));
			be.setChanged();
		}
		if (station.equals("spore_vat") && t % 20 == 0) {
			be.data().putInt("ferment", Math.min(600, be.data().getIntOr("ferment", 0) + 1));
			be.setChanged();
		}
		if (station.equals("jailer_table") && !be.data().contains("code0")) newCode(level, be);
	}

	public static void newCode(ServerLevel level, DataBlockEntity be) {
		for (int i = 0; i < 3; i++) be.data().putInt("code" + i, level.getRandom().nextInt(4));
		be.data().putInt("entered", 0);
		be.setChanged();
	}

	public static boolean canSeeRecipe(ServerPlayer player, Recipes.Recipe r) {
		return r.requiresDefeated() < 0 || MatrioData.get(player.level().getServer()).defeated(player, r.requiresDefeated()) || player.isCreative();
	}

	/** Attempts to craft recipe #index. Returns a message key on failure, null on success. */
	public static String craft(ServerPlayer player, ServerLevel level, BlockPos pos, String station, DataBlockEntity be, int index) {
		var list = Recipes.of(station);
		if (index < 0 || index >= list.size()) return "message.matriochka.station.unknown";
		Recipes.Recipe r = list.get(index);
		if (!canSeeRecipe(player, r)) return "message.matriochka.station.locked";
		if (condition(level, pos, station, be) == 0 && !player.isCreative()) return "message.matriochka.station.condition." + station;
		if (station.equals("spore_vat") && r.output().equals("filter_mask") && be.data().getIntOr("ferment", 0) < 60) return "message.matriochka.station.ferment";
		Inventory inv = player.getInventory();
		for (Recipes.Ing ing : r.inputs()) {
			if (count(inv, resolve(ing.id())) < ing.count() && !player.isCreative()) return "message.matriochka.station.missing";
		}
		if (!player.isCreative()) for (Recipes.Ing ing : r.inputs()) take(inv, resolve(ing.id()), ing.count());
		ItemStack out = new ItemStack(resolve(r.output()), r.count());
		GearClasses.roll(out, level.getRandom());
		if (station.equals("inverter") && out.isDamageableItem()) out.setDamageValue(out.getMaxDamage() / 4);
		if (!inv.add(out)) net.minecraft.world.level.block.Block.popResource(player.level(), player.blockPosition(), out);
		// station side effects
		switch (station) {
			case "lightning_forge" -> { be.data().putInt("charge", Math.max(0, be.data().getIntOr("charge", 0) - 1)); level.playSound(null, pos, SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.BLOCKS, 0.5f, 1.6f); }
			case "jailer_table" -> newCode(level, be);
			case "spore_vat" -> be.data().putInt("ferment", 0);
			case "ash_foundry" -> {
				if (heat(level, pos) >= 3 && level.getRandom().nextInt(4) == 0) {
					level.removeBlock(pos, false);
					level.explode(null, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 2.5f, net.minecraft.world.level.Level.ExplosionInteraction.BLOCK);
					Achievements.grant(player, "foundry_boom");
				}
			}
			default -> {}
		}
		be.setChanged();
		level.playSound(null, pos, SoundEvents.SMITHING_TABLE_USE, SoundSource.BLOCKS, 0.8f, 1.1f);
		PlayerState.of(player).progress("craft", r.output(), r.count());
		return null;
	}

	/** Jailer's table: pressing a pin (0..3). */
	public static void pin(ServerLevel level, DataBlockEntity be, int pin) {
		int entered = be.data().getIntOr("entered", 0);
		if (entered >= 3) return;
		if (be.data().getIntOr("code" + entered, -1) == pin) {
			be.data().putInt("entered", entered + 1);
			level.playSound(null, be.getBlockPos(), SoundEvents.TRIPWIRE_CLICK_ON, SoundSource.BLOCKS, 1f, 1.2f + entered * 0.2f);
		} else {
			be.data().putInt("entered", 0);
			level.playSound(null, be.getBlockPos(), SoundEvents.CHAIN_BREAK, SoundSource.BLOCKS, 1f, 0.7f);
		}
		be.setChanged();
	}

	/** Soul altar: purify (+karma) or devour (-karma) the item in the slot. */
	public static String soulAltar(ServerPlayer player, ItemStack stack, boolean purify) {
		if (stack.isEmpty()) return "message.matriochka.altar.empty";
		Defs.ItemDef def = ModContent.def(ModContent.idOf(stack.getItem()));
		int value;
		if (def != null) {
			if (def.kind().equals("core") || def.kind().equals("secret")) return "message.matriochka.altar.refuse";
			value = Defs.soulValue(def.rarity());
		} else {
			value = switch (stack.getRarity()) {
				case EPIC -> 30;
				case RARE -> 10;
				case UNCOMMON -> 3;
				default -> 1;
			};
		}
		value *= stack.getCount();
		PlayerState ps = PlayerState.of(player);
		String key = "altar_" + BuiltInRegistries.ITEM.getKey(stack.getItem());
		int repeats = ps.counter(key);
		ps.addCounter(key, 1);
		int karma = Math.max(0, (value / 10) - repeats / 4);
		if (value >= 10 && karma == 0 && repeats < 4) karma = 1;
		ps.addSouls(value);
		ps.addKarma(purify ? karma : -karma);
		stack.setCount(0);
		player.level().playSound(null, player.blockPosition(), purify ? SoundEvents.AMETHYST_BLOCK_RESONATE : SoundEvents.SCULK_SHRIEKER_SHRIEK, SoundSource.PLAYERS, 0.8f, purify ? 1.4f : 0.6f);
		player.sendSystemMessage(Component.translatable(purify ? "message.matriochka.altar.purified" : "message.matriochka.altar.devoured", value, ps.karma()));
		return null;
	}

	/** Soul altar: recharge one life-doll layer for 50 souls. */
	public static String rechargeDoll(ServerPlayer player) {
		PlayerState ps = PlayerState.of(player);
		if (ps.dollMax() == 0) return "message.matriochka.altar.no_doll";
		if (ps.dollLayers() >= ps.dollMax()) return "message.matriochka.altar.doll_full";
		if (!ps.spendSouls(50)) return "message.matriochka.altar.no_souls";
		ps.setDoll(ps.dollLayers() + 1, ps.dollMax());
		return null;
	}

	/** Class table: upgrade the class level of the item in the slot. */
	public static String upgrade(ServerPlayer player, ItemStack stack) {
		GearClasses.Gear g = stack.get(GearClasses.GEAR);
		if (g == null) {
			if (GearClasses.kind(stack) == GearClasses.Kind.NONE) return "message.matriochka.class.no_class";
			GearClasses.roll(stack, player.getRandom());
			return null;
		}
		int max = GearClasses.maxLevel(MatrioData.get(player.level().getServer()).highestDefeated(MatrioData.get(player.level().getServer()).groupOf(player.getUUID())));
		if (g.level() >= 5) return "message.matriochka.class.max";
		if (g.level() >= max && !player.isCreative()) return "message.matriochka.class.progress";
		int cost = GearClasses.UPGRADE_COST[g.level() + 1];
		// every upgrade also asks for a boss material: Shell Shards, left by fallen bosses
		int shards = GearClasses.SHARD_COST[g.level() + 1];
		Item shard = ModContent.item("shell_shard");
		if (!player.isCreative() && count(player.getInventory(), shard) < shards) return "message.matriochka.class.need_shard";
		if (PlayerState.of(player).souls() < cost && !player.isCreative()) return "message.matriochka.altar.no_souls";
		if (!player.isCreative()) {
			PlayerState.of(player).spendSouls(cost);
			take(player.getInventory(), shard, shards);
		}
		GearClasses.apply(stack, new GearClasses.Gear(g.cls(), g.level() + 1, g.changes()));
		player.level().playSound(null, player.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 0.7f, 1.3f);
		return null;
	}

	/** Class table: lays a Lacquer Layer on the armor piece in the slot. */
	public static String addLayer(ServerPlayer player, ItemStack stack) {
		if (stack.isEmpty()) return "message.matriochka.altar.empty";
		Item layer = ModContent.item("armor_layer");
		if (count(player.getInventory(), layer) < 1 && !player.isCreative()) return "message.matriochka.layer.need";
		String err = fr.achedon12.matriochka.gear.ArmorLayers.add(stack);
		if (err != null) return err;
		if (!player.isCreative()) take(player.getInventory(), layer, 1);
		player.level().playSound(null, player.blockPosition(), SoundEvents.HONEYCOMB_WAX_ON, SoundSource.PLAYERS, 0.9f, 0.9f);
		return null;
	}

	public static String reroll(ServerPlayer player, ItemStack stack) {
		if (!stack.has(GearClasses.GEAR)) return "message.matriochka.class.no_class";
		if (GearClasses.pool(GearClasses.kind(stack)).length < 2) return "message.matriochka.class.single";
		Item doll = ModContent.item("chance_doll");
		if (count(player.getInventory(), doll) < 1 && !player.isCreative()) return "message.matriochka.class.need_doll";
		int cost = GearClasses.rerollCost(stack);
		if (!PlayerState.of(player).spendSouls(cost) && !player.isCreative()) return "message.matriochka.altar.no_souls";
		if (!player.isCreative()) take(player.getInventory(), doll, 1);
		GearClasses.reroll(stack, player.getRandom());
		player.level().playSound(null, player.blockPosition(), SoundEvents.CHEST_OPEN, SoundSource.PLAYERS, 0.7f, 1.6f);
		return null;
	}
}
