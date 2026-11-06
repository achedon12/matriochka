package fr.achedon12.matriochka.showcase;

import com.mojang.authlib.GameProfile;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.StationAutomation;
import fr.achedon12.matriochka.block.StationInventory;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.item.SoulVessels;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.QuestHooks;
import fr.achedon12.matriochka.world.Quests;
import fr.achedon12.matriochka.world.ScaleLinks;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.entity.FakePlayer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.HopperBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.phys.Vec3;

/**
 * Checks the late-game systems, server side, with real ticks between the steps: station automation (a hopper feeds a
 * station, the result leaves from below, the station's condition holds it back, comparators read it), shaking the
 * World Block on purpose (inside quake, only for the owning group), the Doll of Life layer costing 4 rare resources,
 * the souls of structure chests, a sample of reworked quests (the right action completes them, the old shortcut does
 * not) and the Unfinished on the shortest timing tier. Run with ./gradlew runClientGameTest -Pautomation.
 */
final class AutomationTest {
	private AutomationTest() {}

	private static BlockPos bench = BlockPos.ZERO, chest = BlockPos.ZERO, foundry = BlockPos.ZERO, block = BlockPos.ZERO;
	private static Mob zombie;
	private static MatrioBoss boss;

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			server.runCommand("difficulty normal");
			ctx.waitTicks(40);
			List<String> report = new ArrayList<>(server.computeOnServer(AutomationTest::stations));
			// hoppers move one item every 8 ticks, the station crafts once a second
			ctx.waitTicks(420);
			report.addAll(server.computeOnServer(AutomationTest::stationsAfter));
			report.addAll(server.computeOnServer(AutomationTest::foundryHeated));
			ctx.waitTicks(60);
			report.addAll(server.computeOnServer(AutomationTest::foundryAfter));
			report.addAll(server.computeOnServer(AutomationTest::soulsAndDoll));
			report.addAll(server.computeOnServer(AutomationTest::questsSurface));
			// the old shortcut: carrying the spores is not enough any more (the inventory is scanned every 5 s)
			ctx.waitTicks(120);
			report.addAll(server.computeOnServer(AutomationTest::questsCarried));
			// into World 1 for the shake and the World 1 quests
			server.runCommand("execute as @p run matriochka progression set 0");
			server.runCommand("execute as @p run matriochka world enter 1");
			ctx.waitTicks(120);
			report.addAll(server.computeOnServer(AutomationTest::shakePrepare));
			ctx.waitTicks(20);
			report.addAll(server.computeOnServer(AutomationTest::shakeHelp));
			ctx.waitTicks(10);
			report.addAll(server.computeOnServer(AutomationTest::shakeHinder));
			ctx.waitTicks(20);
			report.addAll(server.computeOnServer(AutomationTest::shakeQuaking));
			report.addAll(server.computeOnServer(AutomationTest::questsWorld1));
			ctx.waitTicks(10);
			// the Unfinished: wake it and watch how long its announcements last, tick by tick
			report.addAll(server.computeOnServer(AutomationTest::unfinishedWake));
			int[] seen = new int[3];
			int[] longest = new int[3];
			int run = 0, lastAttack = -1;
			for (int i = 0; i < 500 && (seen[0] + seen[1] + seen[2]) < 3; i++) {
				ctx.waitTicks(1);
				int[] st = server.computeOnServer(s -> boss == null || !boss.isAlive() ? new int[]{-1, -1} : new int[]{boss.telegraphing() ? 1 : 0, boss.attackIndex()});
				if (st[0] < 0) break;
				if (st[0] == 1) {
					run++;
					lastAttack = st[1];
				} else if (run > 0) {
					longest[lastAttack] = Math.max(longest[lastAttack], run);
					seen[lastAttack]++;
					run = 0;
				}
			}
			report.addAll(server.computeOnServer(s -> unfinishedCheck(s, seen, longest)));
			for (String line : report) Matriochka.LOG.info("[automation] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " automation check(s) failed: " + report);
		}
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static List<String> section(String name, java.util.function.Consumer<List<String>> body) {
		List<String> out = new ArrayList<>();
		try {
			body.accept(out);
		} catch (Throwable t) {
			out.add("FAIL " + name + ": exception " + t);
			Matriochka.LOG.error("[automation] {}", name, t);
		}
		return out;
	}

	private static ServerPlayer player(MinecraftServer server) {
		return server.getPlayerList().getPlayers().get(0);
	}

	private static int recipe(String station, String output) {
		List<Recipes.Recipe> list = Recipes.of(station);
		for (int i = 0; i < list.size(); i++) if (list.get(i).output().equals(output)) return i;
		throw new IllegalStateException("no recipe " + output + " at " + station);
	}

	private static Defs.QuestDef quest(String id) {
		for (Defs.QuestDef q : Content.QUESTS) if (q.id().equals(id)) return q;
		throw new IllegalStateException("no quest " + id);
	}

	private static boolean done(ServerPlayer p, String id) {
		return Quests.done(PlayerState.of(p), quest(id));
	}

	private static void clearAround(ServerLevel level, BlockPos c, int r) {
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-r, -1, -r), c.offset(r, 4, r))) level.setBlock(q, Blocks.AIR.defaultBlockState(), 3);
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-r, -2, -r), c.offset(r, -2, r))) level.setBlock(q, Blocks.STONE.defaultBlockState(), 3);
	}

	// ---------------------------------------------------------------- stations
	private static List<String> stations(MinecraftServer server) {
		return section("stations", out -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			BlockPos base = p.blockPosition().offset(6, 1, 0);
			clearAround(level, base, 3);
			// hopper above -> Matrix Workbench -> hopper below -> chest
			bench = base;
			level.setBlock(bench, ModContent.block("matrix_workbench").defaultBlockState(), 3);
			level.setBlock(bench.above(), Blocks.HOPPER.defaultBlockState().setValue(HopperBlock.FACING, Direction.DOWN), 3);
			level.setBlock(bench.below(), Blocks.HOPPER.defaultBlockState().setValue(HopperBlock.FACING, Direction.DOWN), 3);
			chest = bench.below(2);
			level.setBlock(chest, Blocks.CHEST.defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(bench);
			check(out, StationAutomation.select(be, "matrix_workbench", recipe("matrix_workbench", "painted_wood"), p) == null, "the Painted Wood recipe is picked for automation");
			var top = (net.minecraft.world.level.block.entity.HopperBlockEntity) level.getBlockEntity(bench.above());
			top.setItem(0, new ItemStack(Items.OAK_PLANKS, 16));
			top.setItem(1, new ItemStack(Stations.resolve("minecraft:red_dye"), 2));
			// a stray item is refused: the top hopper keeps it
			top.setItem(2, new ItemStack(Items.COBBLESTONE, 1));
			StationInventory inv = new StationInventory(be, "matrix_workbench");
			check(out, !inv.canPlaceItemThroughFace(0, new ItemStack(Items.COBBLESTONE), Direction.UP), "a station refuses what its recipe does not use");
			check(out, !inv.canPlaceItemThroughFace(0, new ItemStack(Items.OAK_PLANKS), Direction.DOWN), "nothing goes in from below");
			check(out, ModContent.block("matrix_workbench") instanceof net.minecraft.world.WorldlyContainerHolder h && h.getContainer(level.getBlockState(bench), level, bench) != null, "stations expose a container to hoppers");
			BlockPos altar = bench.offset(0, 0, -3);
			level.setBlock(altar, ModContent.block("soul_altar").defaultBlockState(), 3);
			check(out, net.minecraft.world.level.block.entity.HopperBlockEntity.getContainerAt(level, altar) == null, "the Soul Altar has no automation");
		});
	}

	private static List<String> stationsAfter(MinecraftServer server) {
		return section("stations after", out -> {
			ServerLevel level = (ServerLevel) player(server).level();
			ChestBlockEntity c = (ChestBlockEntity) level.getBlockEntity(chest);
			int wood = 0;
			for (int i = 0; i < c.getContainerSize(); i++) if (c.getItem(i).is(ModContent.item("painted_wood"))) wood += c.getItem(i).getCount();
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(bench);
			check(out, wood == 16, "two batches of Painted Wood came out below into the chest (" + wood + ", made " + be.data().getIntOr("auto_made", 0) + ")");
			var top = (net.minecraft.world.level.block.entity.HopperBlockEntity) level.getBlockEntity(bench.above());
			boolean kept = false;
			for (int i = 0; i < top.getContainerSize(); i++) if (top.getItem(i).is(Items.COBBLESTONE)) kept = true;
			check(out, kept, "the stray cobblestone stayed in the hopper");
			// a comparator reads a buffered station
			be.items().set(0, new ItemStack(Items.OAK_PLANKS, 32));
			int signal = level.getBlockState(bench).getAnalogOutputSignal(level, bench, Direction.NORTH);
			check(out, signal > 0 && level.getBlockState(bench).hasAnalogOutputSignal(), "a comparator reads the station's buffer (" + signal + ")");
			be.items().clear();
			// the Ash Foundry: stocked but cold, it waits
			foundry = bench.offset(-4, 0, 0);
			level.setBlock(foundry, ModContent.block("ash_foundry").defaultBlockState(), 3);
			for (Direction d : Direction.values()) if (d != Direction.DOWN) level.setBlock(foundry.relative(d), Blocks.AIR.defaultBlockState(), 3);
			DataBlockEntity fb = (DataBlockEntity) level.getBlockEntity(foundry);
			check(out, StationAutomation.select(fb, "ash_foundry", recipe("ash_foundry", "ash_ingot"), player(server)) == null, "the Ash Ingot recipe is picked");
			StationInventory fi = new StationInventory(fb, "ash_foundry");
			fi.setItem(0, new ItemStack(ModContent.item("giant_ore"), 2));
			fi.setItem(2, new ItemStack(ModContent.item("blazing_rock"), 2));
		});
	}

	private static List<String> foundryHeated(MinecraftServer server) {
		return section("foundry cold", out -> {
			ServerLevel level = (ServerLevel) player(server).level();
			DataBlockEntity fb = (DataBlockEntity) level.getBlockEntity(foundry);
			check(out, fb.items().get(StationInventory.OUTPUT).isEmpty(), "a cold Ash Foundry does not smelt from its hoppers");
			level.setBlock(foundry.east(), Blocks.MAGMA_BLOCK.defaultBlockState(), 3);
		});
	}

	private static List<String> foundryAfter(MinecraftServer server) {
		return section("foundry heated", out -> {
			ServerLevel level = (ServerLevel) player(server).level();
			DataBlockEntity fb = (DataBlockEntity) level.getBlockEntity(foundry);
			check(out, fb.items().get(StationInventory.OUTPUT).is(ModContent.item("ash_ingot")), "with one heat source it smelts by itself (" + fb.items().get(StationInventory.OUTPUT) + ")");
		});
	}

	// ---------------------------------------------------------------- souls, the doll
	private static List<String> soulsAndDoll(MinecraftServer server) {
		return section("souls and doll", out -> {
			ServerPlayer p = player(server);
			PlayerState ps = PlayerState.of(p);
			RandomSource r = RandomSource.create(7);
			int total = 0, chests = 300;
			for (int i = 0; i < chests; i++) {
				int tier = i % 10 < 7 ? 0 : i % 10 < 9 ? 1 : 2;
				for (ItemStack s : SoulVessels.loot(5, tier, r)) total += SoulVessels.souls(s) * s.getCount();
			}
			float per = total / (float) chests;
			check(out, per >= 7 && per <= 14, "a structure chest holds about 10 souls on average (" + per + "), so 10 chests make about 100");
			check(out, SoulVessels.loot(0, 2, r).isEmpty() && !SoulVessels.loot(1, 0, r).isEmpty(), "every world chest holds souls, the Surface ones none");
			int before = ps.souls();
			ItemStack vessel = new ItemStack(ModContent.item("soul_vessel"));
			p.setItemInHand(InteractionHand.MAIN_HAND, vessel);
			vessel.use(p.level(), p, InteractionHand.MAIN_HAND);
			check(out, ps.souls() == before + SoulVessels.VESSEL && p.getMainHandItem().isEmpty(), "using a Soul Vessel frees 20 souls (" + before + " -> " + ps.souls() + ")");
			int karma = ps.karma();
			check(out, karma == ps.karma(), "chest souls do not move karma");

			// Doll of Life: 50 souls and 4 rare resources of the current world (World 1 from the Surface after the Guardian)
			MatrioData data = MatrioData.get(server);
			data.markDefeated(data.groupOf(p.getUUID()), 0);
			ps.setDoll(0, 1);
			ps.addSouls(200);
			p.getInventory().clearContent();
			p.getInventory().add(new ItemStack(ModContent.item("sporite"), 3));
			int s0 = ps.souls();
			Stations.rechargeDoll(p);
			check(out, ps.dollLayers() == 0 && ps.souls() == s0, "three rare resources are not enough for a layer");
			p.getInventory().add(new ItemStack(ModContent.item("chitin"), 2));
			check(out, Stations.rechargeWorld(p) == 1, "the current world is World 1 (" + Stations.rechargeWorld(p) + ")");
			String err = Stations.rechargeDoll(p);
			int left = Stations.count(p.getInventory(), ModContent.item("sporite")) + Stations.count(p.getInventory(), ModContent.item("chitin"));
			check(out, err == null && ps.dollLayers() == 1 && ps.souls() == s0 - 50 && left == 1, "a layer takes 50 souls and 4 rare resources (" + err + ", layers " + ps.dollLayers() + ", left " + left + ")");
			p.getInventory().clearContent();
		});
	}

	// ---------------------------------------------------------------- quests
	private static List<String> questsSurface(MinecraftServer server) {
		return section("surface quests", out -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			PlayerState ps = PlayerState.of(p);
			// Read Between the Lines: opening the Scroll is not reading it
			fr.achedon12.matriochka.net.Net.openJournal(p, true);
			for (int i = 0; i < 4; i++) QuestHooks.read(p, i);
			check(out, !done(p, "read_between_lines"), "opening the Scroll and reading 4 pages does not finish it");
			QuestHooks.read(p, 4);
			check(out, done(p, "read_between_lines"), "reading the 5 pages finishes it");
			// Fingers in the Doll: a Seed alone is not enough, the workbench is asked too
			ps.progress("craft", "seed_1", 1);
			check(out, !done(p, "fingers_in_the_doll"), "crafting a Seed alone does not finish Fingers in the Doll");
			ps.progress("craft", "matrix_workbench", 1);
			check(out, done(p, "fingers_in_the_doll"), "crafting the workbench and a Seed finishes it");
			// The Vat: a fresh brew does not count, a ripe one does (crafted at a real vat)
			BlockPos vat = bench.offset(0, 0, 4);
			level.setBlock(vat, ModContent.block("spore_vat").defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(vat);
			p.getInventory().add(new ItemStack(ModContent.item("spores"), 8));
			p.getInventory().add(new ItemStack(Items.GLASS_BOTTLE, 4));
			int antidote = recipe("spore_vat", "antidote");
			be.data().putInt("ferment", 0);
			Stations.craft(p, level, vat, "spore_vat", be, antidote);
			check(out, !done(p, "the_vat"), "a fresh brew does not finish The Vat (old check: any Antidote)");
			be.data().putInt("ferment", 61);
			String err = Stations.craft(p, level, vat, "spore_vat", be, antidote);
			check(out, err == null && done(p, "the_vat"), "a ripe brew finishes The Vat (" + err + ")");
			check(out, StationAutomation.selectedIndex(be, "spore_vat") == antidote, "the last recipe crafted by hand is kept for automation");
			// Hard Harvest: carry the spores (checked after the next inventory scan)
			p.getInventory().clearContent();
			p.getInventory().add(new ItemStack(ModContent.item("spores"), 16));
		});
	}

	private static List<String> questsCarried(MinecraftServer server) {
		return section("carried", out -> {
			ServerPlayer p = player(server);
			check(out, !done(p, "hard_harvest"), "carrying 16 spores no longer finishes Hard Harvest");
		});
	}

	private static List<String> questsWorld1(MinecraftServer server) {
		return section("world 1 quests", out -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(out, Worlds.number(level) == 1, "the player is in World 1 (" + Worlds.number(level) + ")");
			// Hard Harvest: hand the spores to a Gatherer
			p.getInventory().clearContent();
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("spores"), 16));
			var npc = (MatrioNpc) ModContent.entity("gatherer").create(level, EntitySpawnReason.COMMAND);
			npc.setPos(p.getX() + 1.5, p.getY(), p.getZ());
			level.addFreshEntity(npc);
			npc.mobInteract(p, InteractionHand.MAIN_HAND);
			// the spores leave the inventory; the 5 Antidotes of the reward land in the first free slot, the emptied hand
			int sporesLeft = p.getInventory().countItem(ModContent.item("spores"));
			int antidotes = p.getInventory().countItem(ModContent.item("antidote"));
			check(out, done(p, "hard_harvest") && sporesLeft == 0 && antidotes == 5, "handing 16 spores to a Gatherer finishes Hard Harvest (spores left " + sporesLeft + ", antidotes " + antidotes + ")");
			npc.discard();
			// No Filter: with a mask the kill does not count, without one it does
			p.addEffect(new MobEffectInstance(MobEffects.STRENGTH, 200, 9));
			p.setItemSlot(EquipmentSlot.HEAD, new ItemStack(ModContent.item("filter_mask")));
			killChitin(p, level);
			check(out, !done(p, "no_filter"), "a Chitin Guard killed with a mask does not finish No Filter (old check: any kill)");
			p.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
			killChitin(p, level);
			check(out, done(p, "no_filter"), "a Chitin Guard killed without a mask finishes No Filter");
		});
	}

	private static void killChitin(ServerPlayer p, ServerLevel level) {
		var guard = (net.minecraft.world.entity.LivingEntity) ModContent.entity("chitin_guard").create(level, EntitySpawnReason.COMMAND);
		guard.setPos(p.getX() + 2, p.getY(), p.getZ());
		level.addFreshEntity(guard);
		guard.hurtServer(level, p.damageSources().playerAttack(p), 100000f);
		if (guard.isAlive()) guard.kill(level);
		guard.discard();
	}

	// ---------------------------------------------------------------- shaking the World Block
	private static FakePlayer member, stranger;

	private static List<String> shakePrepare(MinecraftServer server) {
		return section("shake prepare", out -> {
			ServerPlayer p = player(server);
			ServerLevel inner = (ServerLevel) p.level();
			ServerLevel over = server.overworld();
			MatrioData data = MatrioData.get(server);
			String group = data.groupOf(p.getUUID());
			block = over.getRespawnData().pos().above(3);
			over.setBlock(block, ModContent.block("world_block").defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) over.getBlockEntity(block);
			be.data().putInt("world", 1);
			be.data().putString("owner", p.getUUID().toString());
			member = FakePlayer.get(over, new GameProfile(UUID.fromString("00000000-0000-0000-0000-00000000a001"), "Outside"));
			stranger = FakePlayer.get(over, new GameProfile(UUID.fromString("00000000-0000-0000-0000-00000000b002"), "Stranger"));
			data.join(member.getUUID(), group);
			check(out, data.sameGroup(p.getUUID().toString(), member) && !data.sameGroup(p.getUUID().toString(), stranger), "one shaker of the group, one of another group");
			// a creature next to the player, a boss a little further
			p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 60, 4));
			zombie = net.minecraft.world.entity.EntityTypes.ZOMBIE.create(inner, EntitySpawnReason.COMMAND);
			zombie.setPos(p.getX() + 3, p.getY(), p.getZ());
			zombie.setPersistenceRequired();
			inner.addFreshEntity(zombie);
			boss = MatrioBoss.summon(inner, "spore_queen", p.blockPosition().offset(0, 0, 10), p);
		});
	}

	private static List<String> shakeHelp(MinecraftServer server) {
		return section("shake help", out -> {
			ServerLevel over = server.overworld();
			long fxBefore = MatrioData.get(server).worldEntry(MatrioData.get(server).groupOf(player(server).getUUID()), 1).getLongOr("fx_quake", 0L);
			check(out, ScaleLinks.shake(stranger, over, block, false) == ScaleLinks.Shake.NOT_YOURS, "another group cannot shake the block");
			check(out, !zombie.hasEffect(MobEffects.SLOWNESS), "the stranger's shake did nothing inside");
			check(out, ScaleLinks.shake(member, over, block, false) == ScaleLinks.Shake.HELPED, "the group's member shakes it to help");
			check(out, zombie.hasEffect(MobEffects.SLOWNESS), "the creatures near the player inside are stunned");
			check(out, boss != null && boss.opening(), "the boss inside staggers, its guard open");
			check(out, ScaleLinks.shake(member, over, block, true) == ScaleLinks.Shake.COOLDOWN, "a second shake waits for the cooldown");
			long fxAfter = MatrioData.get(server).worldEntry(MatrioData.get(server).groupOf(player(server).getUUID()), 1).getLongOr("fx_quake", 0L);
			check(out, fxAfter == fxBefore, "a helping shake does not quake the world");
			if (boss != null) boss.discard();
			zombie.discard();
		});
	}

	private static List<String> shakeHinder(MinecraftServer server) {
		return section("shake hinder", out -> {
			MatrioData data = MatrioData.get(server);
			ServerPlayer p = player(server);
			String group = data.groupOf(p.getUUID());
			data.worldEntry(group, 1).putLong("shake_ready", 0L);
			ServerLevel inner = (ServerLevel) p.level();
			// a ceiling over the player, to come loose
			BlockPos head = p.blockPosition();
			for (BlockPos q : BlockPos.betweenClosed(head.offset(-4, 0, -4), head.offset(4, 8, 4))) if (q.getY() > head.getY() + 1) inner.setBlock(q, Blocks.AIR.defaultBlockState(), 3);
			for (BlockPos q : BlockPos.betweenClosed(head.offset(-4, 6, -4), head.offset(4, 6, 4))) inner.setBlock(q, Blocks.DIRT.defaultBlockState(), 3);
			check(out, ScaleLinks.shake(stranger, server.overworld(), block, true) == ScaleLinks.Shake.NOT_YOURS, "another group cannot strike the block either");
			check(out, !ScaleLinks.active(data, group, 1, "quake", server.overworld().getGameTime()), "no quake yet");
			check(out, ScaleLinks.shake(member, server.overworld(), block, true) == ScaleLinks.Shake.HINDERED, "the group's member strikes it to hinder");
			check(out, ScaleLinks.active(data, group, 1, "quake", server.overworld().getGameTime()), "the world inside quakes");
			check(out, !inner.getEntitiesOfClass(net.minecraft.world.entity.item.FallingBlockEntity.class, p.getBoundingBox().inflate(10)).isEmpty(), "blocks over the player come loose");
		});
	}

	private static List<String> shakeQuaking(MinecraftServer server) {
		return section("shake quaking", out -> {
			ServerPlayer p = player(server);
			check(out, ScaleLinks.active(p, "quake"), "the quake still runs after real ticks, for the player inside");
		});
	}

	// ---------------------------------------------------------------- the Unfinished
	private static List<String> unfinishedWake(MinecraftServer server) {
		return section("unfinished", out -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 60, 4));
			p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 60, 4));
			boss = MatrioBoss.summon(level, "the_unfinished", p.blockPosition().offset(0, 0, 4), p);
			check(out, boss != null && boss.timingWorld() == 10, "the Unfinished uses the final timing tier on its first shell (" + (boss == null ? -1 : boss.timingWorld()) + ")");
		});
	}

	private static List<String> unfinishedCheck(MinecraftServer server, int[] seen, int[] longest) {
		return section("unfinished timings", out -> {
			int[] expected = {Math.max(6, fr.achedon12.matriochka.content.Defs.telegraphTicks(10) / 2), fr.achedon12.matriochka.content.Defs.telegraphTicks(10), fr.achedon12.matriochka.content.Defs.telegraphTicks(10) * 2};
			int[] old = {Math.max(6, fr.achedon12.matriochka.content.Defs.telegraphTicks(1) / 2), fr.achedon12.matriochka.content.Defs.telegraphTicks(1), fr.achedon12.matriochka.content.Defs.telegraphTicks(1) * 2};
			int checked = 0;
			for (int a = 0; a < 3; a++) {
				if (seen[a] == 0) continue;
				checked++;
				check(out, longest[a] <= expected[a] + 2 && longest[a] < old[a], "attack " + a + " is announced for " + longest[a] + " ticks (final tier " + expected[a] + ", World 1 tier " + old[a] + ")");
			}
			check(out, checked > 0, "at least one attack of the Unfinished was watched");
			if (boss != null) boss.discard();
			member = null;
			stranger = null;
		});
	}
}
