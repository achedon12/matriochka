package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.NestingChests;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.gear.ArmorLayers;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.item.Drill;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Config;
import fr.achedon12.matriochka.world.Karma;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Refuge;
import fr.achedon12.matriochka.world.WorldAdmin;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;

/**
 * Checks the nesting systems, stations, karma, gear classes, groups, admin commands and difficulty modes in a real
 * world, server side: ./gradlew runClientGameTest -Psystems. Every check is reported; the run fails if one fails.
 */
final class SystemsTest {
	private SystemsTest() {}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			server.runCommand("difficulty normal");
			ctx.waitTicks(40);
			List<String> report = server.computeOnServer(SystemsTest::checks);
			for (String line : report) Matriochka.LOG.info("[systems] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " system check(s) failed: " + report);
		}
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	/** Runs one group of checks; an exception fails that group only. */
	private static void section(List<String> out, String name, Runnable r) {
		try {
			r.run();
		} catch (Throwable t) {
			out.add("FAIL " + name + ": exception " + t);
			Matriochka.LOG.error("[systems] {}", name, t);
		}
	}

	private static int command(MinecraftServer server, net.minecraft.commands.CommandSourceStack src, String cmd) {
		try {
			return server.getCommands().getDispatcher().execute(cmd, src);
		} catch (Exception e) {
			Matriochka.LOG.warn("[systems] /{} failed: {}", cmd, e.getMessage());
			return -1;
		}
	}

	private static List<String> checks(MinecraftServer server) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		ServerLevel level = (ServerLevel) p.level();
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		PlayerState ps = PlayerState.of(p);
		ps.setDoll(0, 0);

		section(out, "refuge", () -> {
			BlockPos from = p.blockPosition();
			check(out, !Refuge.use(p) && !Refuge.inRefuge(p.level()), "the refuge doll stays shut before World 3");
			data.markDefeated(group, 3);
			MatrioBoss boss = MatrioBoss.summon(level, "spore_queen", from.offset(0, 0, 10), p);
			check(out, !Refuge.use(p) && !Refuge.inRefuge(p.level()), "the refuge doll stays shut with a boss awake nearby");
			boss.discard();
			check(out, Refuge.use(p) && Refuge.inRefuge(p.level()), "the refuge doll takes the player into the refuge");
			ServerLevel refuge = (ServerLevel) p.level();
			check(out, refuge.getBlockState(p.blockPosition().below()).is(ModContent.block("threshold")), "the player stands on the refuge Threshold");
			BlockPos c = Refuge.center(data.parcel(group));
			check(out, refuge.getBlockState(c.offset(Refuge.radius(1) + 1, 1, 0)).is(ModContent.block("painted_wood"))
				|| refuge.getBlockState(c.offset(Refuge.radius(1) + 1, 1, 0)).is(ModContent.block("lacquer_block")), "the refuge room has lacquered walls");
			data.markDefeated(group, 7);
			Refuge.ensureBuilt(refuge, data, group, Refuge.tier(data.highestDefeated(group)));
			check(out, Refuge.builtTier(data, group) == 3 && refuge.getBlockState(c.offset(Refuge.radius(3) + 1, 1, 0)).isSolid()
				&& refuge.getBlockState(c.offset(Refuge.radius(1) + 1, 1, 0)).isAir(), "the refuge grows after World 7");
			Refuge.use(p);
			check(out, p.level().dimension() == level.dimension() && p.blockPosition().distManhattan(from) <= 2, "using the doll again brings the player back (" + p.blockPosition() + ")");
			data.unmarkDefeated(group, 7);
		});

		section(out, "armor layers", () -> {
			ItemStack chest = new ItemStack(ModContent.item("chitin_chestplate"));
			GearClasses.apply(chest, new GearClasses.Gear("guardian", 1, 0));
			check(out, ArmorLayers.add(chest) == null && ArmorLayers.add(chest) == null && ArmorLayers.count(chest) == 2, "two layers laid on a Guardian chestplate");
			int cap = ArmorLayers.capacity(chest);
			chest.hurtAndBreak(cap, level, p, i -> {});
			check(out, chest.getDamageValue() == 0 && ArmorLayers.count(chest) == 1, "the outer layer breaks, the next takes over, the armor is untouched");
			chest.hurtAndBreak(cap + 5, level, p, i -> {});
			chest.hurtAndBreak(5, level, p, i -> {});
			check(out, ArmorLayers.count(chest) == 0 && chest.getDamageValue() > 0, "with no layer left the armor wears (" + chest.getDamageValue() + ")");
		});

		section(out, "nesting chests", () -> {
			BlockPos at = p.blockPosition().offset(4, 0, 0);
			level.setBlock(at, ModContent.block("nesting_chest_medium").defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(at);
			NonNullList<ItemStack> inner = NonNullList.withSize(18, ItemStack.EMPTY);
			inner.set(0, new ItemStack(Items.IRON_INGOT, 7));
			fr.achedon12.matriochka.block.ContainerTags.save(be.data(), level.registryAccess(), inner);
			be.data().putString("sort", "food");
			List<ItemStack> drops = net.minecraft.world.level.block.Block.getDrops(level.getBlockState(at), level, at, be, p, ItemStack.EMPTY);
			level.setBlock(at, Blocks.AIR.defaultBlockState(), 3);
			ItemStack box = drops.isEmpty() ? ItemStack.EMPTY : drops.getFirst();
			check(out, NestingChests.rows(box) == 2 && NestingChests.contents(box, 18).get(0).getCount() == 7 && NestingChests.rule(box).equals("food"),
				"a broken Middle Nesting Chest keeps its items and its rule");
			check(out, NestingChests.mayHold(3, box) && !NestingChests.mayHold(2, box) && !NestingChests.mayHold(1, box), "only a larger chest takes it");
			List<ItemStack> outer = new ArrayList<>(List.of(box, new ItemStack(Items.BREAD, 5), new ItemStack(Items.STONE, 3)));
			NestingChests.sort(outer);
			ItemStack after = outer.getFirst();
			NonNullList<ItemStack> held = NestingChests.contents(after, 18);
			boolean bread = held.stream().anyMatch(s -> s.is(Items.BREAD) && s.getCount() == 5);
			check(out, bread && outer.get(1).isEmpty() && outer.get(2).getCount() == 3 && held.get(0).getCount() == 7,
				"a chest inside a chest keeps its items and sorts food into itself");
			BlockPos at2 = p.blockPosition().offset(-4, 0, 0);
			level.setBlock(at2, ModContent.block("nesting_chest").defaultBlockState(), 3);
			level.getBlockState(at2).getBlock().setPlacedBy(level, at2, level.getBlockState(at2), p, after);
			DataBlockEntity be2 = (DataBlockEntity) level.getBlockEntity(at2);
			check(out, NestingChests.contents(NestingChests.toItem(ModContent.block("nesting_chest"), be2.data(), level.registryAccess()), 27).get(0).getCount() == 7,
				"placing a chest item restores its contents");
			level.setBlock(at2, Blocks.AIR.defaultBlockState(), 3);
		});

		section(out, "drill", () -> {
			p.setGameMode(GameType.SURVIVAL);
			p.snapTo(p.getX(), p.getY(), p.getZ(), 0f, 0f);
			BlockPos center = p.blockPosition().offset(0, 1, 3);
			for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) level.setBlock(center.offset(a, b, 0), Blocks.STONE.defaultBlockState(), 3);
			ItemStack drill = new ItemStack(ModContent.item("drill"));
			p.setItemInHand(InteractionHand.MAIN_HAND, drill);
			p.getInventory().add(new ItemStack(ModContent.item("blazing_rock"), 2));
			p.gameMode.destroyBlock(center);
			int left = 0;
			for (int a = -1; a <= 1; a++) for (int b = -1; b <= 1; b++) if (!level.getBlockState(center.offset(a, b, 0)).isAir()) left++;
			check(out, left == 0, "the drill mines a 3x3 square (" + left + " left)");
			check(out, Stations.count(p.getInventory(), ModContent.item("blazing_rock")) == 1 && Drill.fuel(p.getMainHandItem()) == Drill.FUEL_PER_ROCK - 1,
				"the drill burns a Blazing Rock (fuel " + Drill.fuel(p.getMainHandItem()) + ")");
			p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
			p.getInventory().clearContent();
		});

		section(out, "stations", () -> {
			BlockPos forge = p.blockPosition().offset(2, 0, -3);
			level.setBlock(forge, ModContent.block("lightning_forge").defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(forge);
			p.getInventory().add(new ItemStack(Items.APPLE, 2));
			p.getInventory().add(new ItemStack(ModContent.item("storm_essence"), 2));
			int idx = indexOf("lightning_forge", "cloud_fruit");
			String err = Stations.craft(p, level, forge, "lightning_forge", be, idx);
			check(out, err == null && Stations.count(p.getInventory(), ModContent.item("cloud_fruit")) == 2
				&& Stations.count(p.getInventory(), ModContent.item("storm_essence")) == 0, "Storm Essence charges the Lightning Forge instead of lightning (" + err + ")");
			level.setBlock(forge, Blocks.AIR.defaultBlockState(), 3);
			p.getInventory().clearContent();

			BlockPos vat = p.blockPosition().offset(-2, 0, -3);
			level.setBlock(vat, ModContent.block("spore_vat").defaultBlockState(), 3);
			DataBlockEntity vbe = (DataBlockEntity) level.getBlockEntity(vat);
			vbe.data().putInt("ferment", 300);
			p.getInventory().add(new ItemStack(ModContent.item("spores"), 4));
			p.getInventory().add(new ItemStack(Items.GLASS_BOTTLE, 2));
			String verr = Stations.craft(p, level, vat, "spore_vat", vbe, indexOf("spore_vat", "antidote"));
			check(out, verr == null && Stations.count(p.getInventory(), ModContent.item("antidote")) == 4, "an aged Spore Vat brew yields twice as much");
			level.setBlock(vat, Blocks.AIR.defaultBlockState(), 3);
			p.getInventory().clearContent();

			ItemStack a = new ItemStack(ModContent.item("chitin_helmet")), b = new ItemStack(ModContent.item("thermal_helmet"));
			GearClasses.apply(a, new GearClasses.Gear("guardian", 3, 0));
			GearClasses.apply(b, new GearClasses.Gear("prowler", 1, 0));
			String ierr = Stations.invert(p, a, b);
			GearClasses.Gear ga = a.get(GearClasses.GEAR), gb = b.get(GearClasses.GEAR);
			check(out, ierr == null && ga.cls().equals("prowler") && gb.cls().equals("guardian") && gb.level() == 3 && a.getDamageValue() > 0,
				"the Inverter swaps the classes of two helmets, at a cost in durability");
		});

		section(out, "karma", () -> {
			var npc = (MatrioNpc) ModContent.entity("prisoner").create(level, EntitySpawnReason.COMMAND);
			npc.setPos(p.getX() + 2, p.getY(), p.getZ());
			level.addFreshEntity(npc);
			var shackle = ModContent.item("sealed_shackle");
			ps.addKarma(-30 - ps.karma());
			npc.mobInteract(p, InteractionHand.MAIN_HAND);
			boolean dark = npc.getOffers().stream().anyMatch(o -> o.getResult().is(shackle));
			p.closeContainer();
			npc.setTradingPlayer(null);
			ps.addKarma(-ps.karma());
			npc.mobInteract(p, InteractionHand.MAIN_HAND);
			boolean neutral = npc.getOffers().stream().anyMatch(o -> o.getResult().is(shackle));
			int base = npc.getOffers().getFirst().getCostA().getCount();
			p.closeContainer();
			npc.setTradingPlayer(null);
			ps.addKarma(30);
			npc.mobInteract(p, InteractionHand.MAIN_HAND);
			int kind = npc.getOffers().getFirst().getCostA().getCount();
			p.closeContainer();
			npc.setTradingPlayer(null);
			npc.discard();
			check(out, dark && !neutral, "karma -30 opens the black market, karma 0 closes it");
			check(out, kind < base, "karma +30 lowers a price (" + base + " -> " + kind + ")");
			ps.addKarma(-ps.karma());

			var villager = net.minecraft.world.entity.EntityTypes.VILLAGER.create(level, EntitySpawnReason.COMMAND);
			villager.setPos(p.getX() - 2, p.getY(), p.getZ());
			level.addFreshEntity(villager);
			villager.getOffers().add(new MerchantOffer(new ItemCost(Items.EMERALD, 10), new ItemStack(Items.DIAMOND), 12, 1, 0.05f));
			villager.getOffers().add(new MerchantOffer(new ItemCost(Items.EMERALD, 10), new ItemStack(Items.BREAD, 3), 12, 1, 0.05f));
			data.unmarkDefeated(group, 5);
			Karma.gateDiamonds(p, villager);
			boolean hidden = villager.getOffers().stream().noneMatch(Karma::involvesDiamond) && villager.getOffers().size() == 1;
			data.markDefeated(group, 5);
			Karma.gateDiamonds(p, villager);
			boolean back = villager.getOffers().stream().anyMatch(Karma::involvesDiamond);
			data.unmarkDefeated(group, 5);
			villager.discard();
			check(out, hidden && back, "villager diamond offers are set aside before World 5 and come back after");
			check(out, Karma.priceShift(-30, 10) > 0 && Karma.priceShift(30, 10) < 0 && Karma.priceShift(0, 10) == 0, "Surface prices follow karma");
		});

		section(out, "gear classes", () -> {
			ItemStack chest = new ItemStack(ModContent.item("chitin_chestplate"));
			GearClasses.apply(chest, new GearClasses.Gear("reaper", 5, 0));
			p.setItemSlot(EquipmentSlot.CHEST, chest);
			int souls = GearClasses.reapSouls(p, 100, p.getRandom());
			check(out, GearClasses.soulGain(p) > 0 && souls > 100, "Reaper gear harvests more souls (" + souls + " for 100)");
			for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
				String piece = switch (s) { case HEAD -> "helmet"; case CHEST -> "chestplate"; case LEGS -> "leggings"; default -> "boots"; };
				ItemStack it = new ItemStack(ModContent.item("chitin_" + piece));
				GearClasses.apply(it, new GearClasses.Gear("prowler", 5, 0));
				p.setItemSlot(s, it);
			}
			var zombie = net.minecraft.world.entity.EntityTypes.ZOMBIE.create(level, EntitySpawnReason.COMMAND);
			zombie.setPos(p.getX(), p.getY(), p.getZ() + 2);
			int dodged = 0;
			for (int i = 0; i < 200; i++) {
				if (GearClasses.dodges(p, level.damageSources().mobAttack(zombie))) dodged++;
			}
			check(out, GearClasses.dodgeChance(p) > 0 && dodged > 0 && dodged < 200, "Prowler gear dodges some blows (" + dodged + " of 200)");
			for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) p.setItemSlot(s, ItemStack.EMPTY);
			p.setHealth(p.getMaxHealth());
		});

		section(out, "groups", () -> {
			var root = server.getCommands().getDispatcher().getRoot().getChild("matriochka").getChild("group");
			check(out, root.getChild("kick") != null && root.getChild("transfer") != null && root.getChild("disband") != null && root.getChild("leader") != null,
				"group leader, kick, transfer and disband commands exist");
			String g = data.groupOf(p.getUUID());
			UUID mate = UUID.randomUUID();
			data.join(mate, g);
			check(out, data.members(g).size() == 2 && command(server, p.createCommandSourceStack(), "matriochka group leader") == 1, "a second member joins; /matriochka group leader answers");
			data.transfer(g, mate);
			check(out, !data.isLeader(p.getUUID()) && data.isLeader(mate), "the lead is handed over");
			WorldAdmin.kick(server, mate);
			check(out, data.members(g).size() == 1 && data.isLeader(p.getUUID()) && !data.groupOf(mate).equals(g), "a kicked leader leaves, the oldest member leads");
			data.join(mate, g);
			WorldAdmin.disband(server, g);
			String now = data.groupOf(p.getUUID());
			check(out, !now.equals(g) && data.members(g).isEmpty() && data.members(now).size() == 1 && data.group(g).contains("disbanded_at"),
				"a disbanded group sends everyone back to a group of one and keeps its worlds dated");
		});

		section(out, "admin", () -> {
			String g = data.groupOf(p.getUUID());
			String name = p.getGameProfile().name();
			var src = server.createCommandSourceStack();
			BlockPos wb = p.blockPosition().offset(3, 0, 3);
			level.setBlock(wb, ModContent.block("world_block").defaultBlockState(), 3);
			data.setWorldBlock(g, 2, level, wb);
			check(out, command(server, src, "matriochka world list") > 0, "/matriochka world list lists the worlds");
			BlockPos to = wb.offset(2, 0, 0);
			command(server, src.withPosition(net.minecraft.world.phys.Vec3.atBottomCenterOf(to)), "matriochka world move " + name + " 2");
			check(out, level.getBlockState(to).is(ModContent.block("world_block")) && level.getBlockState(wb).isAir() && data.hasWorldBlock(server, g, 2),
				"/matriochka world move moves the World Block");
			int parcel = data.parcel(g, 2);
			data.markDefeated(g, 2);
			command(server, src, "matriochka world reset " + name + " 2");
			check(out, data.parcel(g, 2) != parcel && !data.defeated(g, 2) && level.getBlockState(to).isAir(), "/matriochka world reset gives the world a new parcel");
			data.markDefeated(g, 4);
			command(server, src, "matriochka boss reset " + name + " 4");
			check(out, !data.defeated(g, 4), "/matriochka boss reset forgets a beaten boss");
			check(out, Worlds.parcelOf(Worlds.parcelCenter(data.parcel(g, 2))) == data.parcel(g, 2), "the new parcel is consistent");
		});

		section(out, "difficulty", () -> {
			String before = Config.get().difficulty;
			try {
				Config.get().difficulty = "story";
				ps.setDoll(0, 0);
				p.getInventory().clearContent();
				p.getInventory().setItem(5, new ItemStack(Items.IRON_INGOT, 12));
				boolean allowed = ServerPlayerEvents.ALLOW_DEATH.invoker().allowDeath(p, level.damageSources().generic(), 100f);
				boolean emptied = p.getInventory().getItem(5).isEmpty();
				ServerPlayerEvents.AFTER_RESPAWN.invoker().afterRespawn(p, p, false);
				check(out, allowed && emptied && p.getInventory().getItem(5).getCount() == 12, "story mode keeps the inventory on death");
				Config.get().difficulty = "hardcore";
				ServerPlayerEvents.AFTER_RESPAWN.invoker().afterRespawn(p, p, false);
				check(out, p.gameMode() == GameType.SPECTATOR, "hardcore death is permanent (spectator)");
			} finally {
				Config.get().difficulty = before;
				p.setGameMode(GameType.SURVIVAL);
				ps.set("perma_dead", false);
				p.getInventory().clearContent();
			}
		});
		return out;
	}

	private static int indexOf(String station, String output) {
		var list = Recipes.of(station);
		for (int i = 0; i < list.size(); i++) if (list.get(i).output().equals(output)) return i;
		throw new IllegalStateException("no recipe " + output + " at " + station);
	}
}
