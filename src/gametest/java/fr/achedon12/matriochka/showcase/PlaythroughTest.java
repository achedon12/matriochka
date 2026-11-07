package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Blocks2;
import fr.achedon12.matriochka.block.Blocks3;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Lairs;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Rituals;
import fr.achedon12.matriochka.world.WorldZero;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.function.Predicate;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.commands.arguments.EntityAnchorArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The whole game, played the way a player would, in real game ticks: ./gradlew runClientGameTest -Pplaythrough.
 *
 * <p>The Block Guardian is woken at its sanctuary altar and beaten with real blows (ServerPlayer.attack, one per full
 * swing); its Matrix Workbench is placed, then for every world the Seed is crafted at the workbench from the previous
 * boss's core, planted on tilled World Soil beside what it needs (water, magma, redstone, sky, darkness, height,
 * twilight) and left to hatch; the World Block is used to enter, the boss is woken at its lair heart or at its arena
 * altar with its offering, fought, and its core and soil are picked up; the Threshold leads back. After World 10 the
 * ten hidden dolls are nested, World 0 is opened, its three chambers are cleared and the tools are set down.
 *
 * <p>What is sped up, never skipped: the player is teleported instead of walking, is given the resources a Seed asks
 * for besides its core (what would be farmed), the offerings and the hidden dolls, and fights with strong gear (a
 * sword whose damage brings each boss down in about thirty blows, Resistance V so the world rules cannot end the run).
 * Natural spawning is off so the run stays deterministic. Every step is asserted and timed; the run fails on the
 * first step that cannot go on, and at the end if any check failed.
 */
final class PlaythroughTest {
	private PlaythroughTest() {}

	private static final List<String> OUT = new ArrayList<>();
	private static final int SWING = 14;
	private static long wall0, game0;
	/** The base on the Surface: the top of the platform, the workbench and the plots. */
	private static BlockPos base, bench;

	static void run(ClientGameTestContext ctx) {
		OUT.clear();
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			TestServerContext server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			for (String c : new String[]{"gamerule advance_time false", "gamerule advance_weather false", "gamerule spawn_monsters false",
				"gamerule announce_advancements false", "gamerule keep_inventory true", "time set 6000", "weather clear", "difficulty normal",
				"gamemode survival @a", "effect give @a resistance infinite 4 true", "effect give @a regeneration infinite 2 true",
				"effect give @a saturation infinite 0 true", "effect give @a water_breathing infinite 0 true",
				"effect give @a fire_resistance infinite 0 true", "effect give @a night_vision infinite 0 true"}) {
				server.runCommand(c);
			}
			ctx.waitTicks(40);
			ctx.setScreen(() -> null);
			wall0 = System.nanoTime();
			game0 = server.computeOnServer(s -> s.overworld().getGameTime());
			try {
				step(ctx, server, "base", () -> server.computeOnServer(PlaythroughTest::buildBase));
				guardian(ctx, server);
				step(ctx, server, "workbench", () -> server.computeOnServer(PlaythroughTest::placeWorkbench));
				for (int w = 1; w <= 10; w++) world(ctx, server, w);
				endgame(ctx, server);
			} catch (Abort a) {
				OUT.add("FAIL " + a.getMessage());
			} catch (Throwable t) {
				OUT.add("FAIL exception " + t);
				Matriochka.LOG.error("[playthrough]", t);
			}
			ctx.runOnClient(mc -> mc.options.keyShift.setDown(false));
			for (String line : OUT) Matriochka.LOG.info("[playthrough] {}", line);
			long failed = OUT.stream().filter(l -> l.startsWith("FAIL")).count();
			Matriochka.LOG.info("[playthrough] {} checks, {} failed, {} s, {} game ticks", OUT.size(), failed,
				(System.nanoTime() - wall0) / 1_000_000_000L, server.computeOnServer(s -> s.overworld().getGameTime()) - game0);
			if (failed > 0) throw new AssertionError(failed + " playthrough check(s) failed: " + OUT.stream().filter(l -> l.startsWith("FAIL")).toList());
		}
	}

	// ---------------------------------------------------------------- bookkeeping
	/** Thrown when a step cannot go on: the rest of the game depends on it. */
	private static final class Abort extends RuntimeException {
		Abort(String m) {
			super(m);
		}
	}

	@FunctionalInterface
	private interface Body {
		List<String> run() throws Throwable;
	}

	/** Runs a step, records its checks and its time; aborts the run when one of its checks failed. */
	private static void step(ClientGameTestContext ctx, TestServerContext server, String name, Body body) {
		long w = System.nanoTime(), g = server.computeOnServer(s -> s.overworld().getGameTime());
		List<String> lines;
		try {
			lines = body.run();
		} catch (Abort a) {
			throw a;
		} catch (Throwable t) {
			Matriochka.LOG.error("[playthrough] " + name, t);
			throw new Abort(name + ": exception " + t);
		}
		long dg = server.computeOnServer(s -> s.overworld().getGameTime()) - g;
		OUT.addAll(lines);
		OUT.add(String.format("time %-24s %6d ticks %6.1f s", name, dg, (System.nanoTime() - w) / 1e9));
		Matriochka.LOG.info("[playthrough] {}: {} ticks, {} check(s)", name, dg, lines.size());
		for (String l : lines) if (l.startsWith("FAIL")) throw new Abort(name + ": " + l.substring(5));
	}

	private static List<String> checks(Object... pairs) {
		List<String> out = new ArrayList<>();
		for (int i = 0; i < pairs.length; i += 2) out.add(((Boolean) pairs[i] ? "ok   " : "FAIL ") + pairs[i + 1]);
		return out;
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().getFirst();
	}

	private static String group(ServerPlayer p) {
		return MatrioData.get(p.level().getServer()).groupOf(p.getUUID());
	}

	private static boolean achieved(ServerPlayer p, String id) {
		var h = p.level().getServer().getAdvancements().get(Matriochka.id(id));
		return h != null && p.getAdvancements().getOrStartProgress(h).isDone();
	}

	private static boolean customAchieved(ServerPlayer p, String key) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) if (a.trigger().equals("custom") && a.arg().equals(key)) return achieved(p, a.id());
		return false;
	}

	/** The advancement for beating a boss, when there is one ("" otherwise). */
	private static String killAdvancement(String boss) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) if (a.trigger().equals("kill") && a.arg().equals(boss)) return a.id();
		return "";
	}

	// ---------------------------------------------------------------- inventory and hands
	private static Item item(String id) {
		return Stations.resolve(id);
	}

	private static int count(ServerPlayer p, String id) {
		return Stations.count(p.getInventory(), item(id));
	}

	private static void give(ServerPlayer p, String id, int n) {
		ItemStack s = new ItemStack(item(id), n);
		if (!p.getInventory().add(s)) throw new Abort("inventory full while giving " + id);
	}

	/** Puts a stack of that item in the main hand (the hand's stack goes where it was), as a player picking it in the hotbar. */
	private static boolean hold(ServerPlayer p, String id) {
		var inv = p.getInventory();
		Item it = item(id);
		if (p.getMainHandItem().is(it)) return true;
		for (int i = 0; i < inv.getContainerSize(); i++) {
			if (inv.getItem(i).is(it)) {
				ItemStack taken = inv.getItem(i).copy();
				inv.setItem(i, p.getMainHandItem().copy());
				p.setItemInHand(InteractionHand.MAIN_HAND, taken);
				return true;
			}
		}
		return false;
	}

	/** Empties the main hand into the inventory. */
	private static void emptyHand(ServerPlayer p) {
		ItemStack s = p.getMainHandItem().copy();
		if (s.isEmpty()) return;
		p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
		// into another free slot: Inventory.add fills the first free slot, which can be the hand just emptied
		var inv = p.getInventory();
		for (int i = 0; i < inv.getNonEquipmentItems().size(); i++) {
			if (i != inv.getSelectedSlot() && inv.getItem(i).isEmpty()) {
				inv.setItem(i, s);
				return;
			}
		}
		net.minecraft.world.level.block.Block.popResource(p.level(), p.blockPosition(), s);
	}

	/** Right-click on a block face with the main hand, through the server's own interaction path. */
	private static void useOn(ServerPlayer p, BlockPos pos, Direction face) {
		ServerLevel level = (ServerLevel) p.level();
		Vec3 hit = Vec3.atCenterOf(pos).add(face.getStepX() * 0.5, face.getStepY() * 0.5, face.getStepZ() * 0.5);
		p.lookAt(EntityAnchorArgument.Anchor.EYES, hit);
		p.gameMode.useItemOn(p, level, p.getMainHandItem(), InteractionHand.MAIN_HAND, new BlockHitResult(hit, face, pos, false));
	}

	private static void tp(ServerPlayer p, ServerLevel level, double x, double y, double z) {
		p.teleportTo(level, x, y, z, Set.of(), p.getYRot(), p.getXRot(), false);
		p.fallDistance = 0;
	}

	private static void tp(ServerPlayer p, BlockPos at) {
		tp(p, (ServerLevel) p.level(), at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
	}

	/** A sword strong enough to end a fight of that much health in about thirty blows, at the vanilla swing speed. */
	private static ItemStack sword(float health) {
		ItemStack s = new ItemStack(Items.NETHERITE_SWORD);
		double dmg = Math.max(40, Math.ceil(health / 30 / 0.75));
		ItemAttributeModifiers mods = ItemAttributeModifiers.builder()
			.add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Matriochka.id("playthrough_damage"), dmg, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
			.add(Attributes.ATTACK_SPEED, new AttributeModifier(Matriochka.id("playthrough_speed"), -2.4, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
			.build();
		s.set(DataComponents.ATTRIBUTE_MODIFIERS, mods);
		s.set(DataComponents.CUSTOM_NAME, net.minecraft.network.chat.Component.literal("Playthrough Blade"));
		return s;
	}

	private static void arm(ServerPlayer p, float health) {
		// the last fight's sword is the test's own tool: swapped for this one's, not hoarded (eleven of them, with what
		// the fights knock loose, filled the inventory before the hidden dolls)
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) if (inv.getItem(i).is(Items.NETHERITE_SWORD)) inv.setItem(i, ItemStack.EMPTY);
		emptyHand(p);
		p.setItemInHand(InteractionHand.MAIN_HAND, sword(health));
	}

	private static void wear(ServerPlayer p, boolean snorkel) {
		p.setItemSlot(EquipmentSlot.HEAD, snorkel ? new ItemStack(ModContent.item("pearl_snorkel")) : new ItemStack(Items.NETHERITE_HELMET));
		p.setItemSlot(EquipmentSlot.CHEST, new ItemStack(Items.NETHERITE_CHESTPLATE));
		p.setItemSlot(EquipmentSlot.LEGS, new ItemStack(Items.NETHERITE_LEGGINGS));
		p.setItemSlot(EquipmentSlot.FEET, new ItemStack(Items.NETHERITE_BOOTS));
	}

	// ---------------------------------------------------------------- the base
	private static BlockPos plot(int world) {
		// four blocks apart: the water basin or magma two blocks east of a plot never touches the next one
		return base.offset(-21 + world * 4, 1, 6);
	}

	/** A stone platform around the spawn, cleared above: where the player builds and plants. */
	private static List<String> buildBase(MinecraftServer s) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		BlockPos at = p.blockPosition();
		int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.getX(), at.getZ()) - 1;
		base = new BlockPos(at.getX(), y, at.getZ());
		for (int dx = -22; dx <= 22; dx++) {
			for (int dz = -8; dz <= 16; dz++) {
				level.setBlock(base.offset(dx, 0, dz), Blocks.STONE_BRICKS.defaultBlockState(), 3);
				level.setBlock(base.offset(dx, -1, dz), Blocks.STONE.defaultBlockState(), 3);
				for (int dy = 1; dy <= 10; dy++) level.setBlock(base.offset(dx, dy, dz), Blocks.AIR.defaultBlockState(), 3);
			}
		}
		tp(p, base.above());
		give(p, "minecraft:diamond_hoe", 1);
		wear(p, false);
		return checks(level.getBlockState(base).is(Blocks.STONE_BRICKS), "the base platform stands at " + base.toShortString());
	}

	private static List<String> placeWorkbench(MinecraftServer s) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		bench = base.offset(0, 1, 2);
		tp(p, base.offset(0, 1, -1));
		boolean held = hold(p, "matrix_workbench");
		if (held) useOn(p, base.offset(0, 0, 2), Direction.UP);
		boolean placed = level.getBlockState(bench).is(ModContent.block("matrix_workbench")) && level.getBlockEntity(bench) instanceof DataBlockEntity;
		return checks(held, "the Guardian's Matrix Workbench is in the inventory", placed, "the workbench is placed on the base");
	}

	// ---------------------------------------------------------------- fights
	/** One full-strength blow at the nearest living target the filter accepts; returns how many are left. */
	private static int strike(MinecraftServer s, Predicate<LivingEntity> filter, double radius) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		AABB box = p.getBoundingBox().inflate(radius);
		List<LivingEntity> targets = level.getEntitiesOfClass(LivingEntity.class, box, e -> e != p && e.isAlive() && filter.test(e));
		if (targets.isEmpty()) return 0;
		// the Spore Queen hides behind her nodes: those come first
		LivingEntity t = targets.stream().filter(e -> e.entityTags().contains("boss_node")).findFirst()
			.orElse(targets.stream().min(Comparator.comparingDouble(e -> e.distanceToSqr(p))).orElseThrow());
		Vec3 c = t.position();
		Vec3 away = p.position().subtract(c).multiply(1, 0, 1);
		away = away.lengthSqr() < 1e-4 ? new Vec3(0, 0, -1) : away.normalize();
		double reach = t.getBbWidth() / 2 + 1.8;
		tp(p, level, c.x + away.x * reach, c.y, c.z + away.z * reach);
		p.lookAt(EntityAnchorArgument.Anchor.EYES, c.add(0, t.getBbHeight() / 2, 0));
		p.attack(t);
		return targets.size();
	}

	/** Strikes at every full swing until nothing the filter accepts is left; returns the blows struck. */
	private static int fight(ClientGameTestContext ctx, TestServerContext server, Predicate<LivingEntity> filter, double radius, int maxBlows) {
		int blows = 0;
		while (blows < maxBlows) {
			ctx.waitTicks(SWING);
			int left = server.computeOnServer(s -> strike(s, filter, radius));
			if (left == 0) return blows;
			blows++;
		}
		throw new Abort("still fighting after " + maxBlows + " blows");
	}

	/** Walks over every item lying around (picking them up), for a few seconds. */
	private static void pickUp(ClientGameTestContext ctx, TestServerContext server, Vec3 around) {
		for (int i = 0; i < 40; i++) {
			ctx.waitTicks(4);
			boolean any = server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				ServerLevel level = (ServerLevel) p.level();
				List<ItemEntity> items = level.getEntitiesOfClass(ItemEntity.class, new AABB(around, around).inflate(40, 64, 40), ItemEntity::isAlive);
				if (items.isEmpty()) return false;
				ItemEntity e = items.stream().min(Comparator.comparingDouble(x -> x.distanceToSqr(p))).orElseThrow();
				tp(p, level, e.getX(), e.getY(), e.getZ());
				return true;
			});
			if (!any) return;
		}
	}

	private static boolean bossAlive(MinecraftServer s, String id) {
		ServerPlayer p = player(s);
		return !p.level().getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(128), b -> b.def.id().equals(id) && b.isAlive()).isEmpty();
	}

	/** Waits until the boss is up (ritual or awakening), at most that many ticks. */
	private static boolean awaitBoss(ClientGameTestContext ctx, TestServerContext server, String id, int ticks) {
		for (int t = 0; t < ticks; t += 10) {
			ctx.waitTicks(10);
			if (server.computeOnServer(s -> bossAlive(s, id))) return true;
		}
		return false;
	}

	/** Fights a boss down with real blows, then picks up what it left. */
	private static Vec3 defeat(ClientGameTestContext ctx, TestServerContext server, Defs.BossDef boss) {
		server.runOnServer(s -> {
			ServerPlayer p = player(s);
			List<MatrioBoss> b = p.level().getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(128), x -> x.def.id().equals(boss.id()));
			arm(p, b.isEmpty() ? boss.hp() : b.getFirst().getMaxHealth());
		});
		Vec3[] last = {Vec3.ZERO};
		int blows = fight(ctx, server, e -> {
			if (e instanceof MatrioBoss b && b.def.id().equals(boss.id())) {
				last[0] = b.position();
				return true;
			}
			return e instanceof MatrioMob m && m.entityTags().contains("boss_node");
		}, 128, 900);
		OUT.add("info " + boss.id() + " fell after " + blows + " blows");
		ctx.waitTicks(10);
		pickUp(ctx, server, last[0]);
		return last[0];
	}

	// ---------------------------------------------------------------- the Guardian
	private static void guardian(ClientGameTestContext ctx, TestServerContext server) {
		BlockPos[] altar = {null};
		step(ctx, server, "guardian sanctuary", () -> server.computeOnServer(s -> {
			ServerPlayer p = player(s);
			ServerLevel level = (ServerLevel) p.level();
			// the sanctuary sits on the ground 48 blocks north, which can be far below or above the base on a hilly
			// spawn: search and land around that ground, not around the base's height
			BlockPos north = base.offset(0, 0, -48);
			BlockPos at = north.atY(level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, north.getX(), north.getZ()));
			tp(p, at.offset(0, 4, 8));
			var src = s.createCommandSourceStack().withLevel(level).withPosition(Vec3.atCenterOf(at)).withSuppressedOutput();
			int placed;
			try {
				placed = s.getCommands().getDispatcher().execute("place structure matriochka:guardian_sanctuary " + at.getX() + " " + at.getY() + " " + at.getZ(), src);
			} catch (Exception e) {
				placed = 0;
			}
			for (BlockPos q : BlockPos.betweenClosed(at.offset(-40, -16, -40), at.offset(40, 24, 40))) {
				if (level.getBlockState(q).is(ModContent.block("sanctuary_altar"))) {
					altar[0] = q.immutable();
					break;
				}
			}
			return checks(placed > 0, "the Guardian's sanctuary is placed (" + placed + ")", altar[0] != null, "its altar is found");
		}));
		step(ctx, server, "wake the Guardian", () -> {
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				tp(p, altar[0].north(2));
				emptyHand(p);
				useOn(p, altar[0], Direction.UP);
			});
			return checks(awaitBoss(ctx, server, "block_guardian", 60), "using the altar wakes the Block Guardian");
		});
		step(ctx, server, "defeat the Guardian", () -> {
			defeat(ctx, server, ModContent.bossForWorld(0));
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				MatrioData data = MatrioData.get(s);
				return checks(data.defeated(group(p), 0), "the group has beaten the Guardian",
					count(p, "guardian_core") >= 1, "the Guardian Core is picked up",
					count(p, "matrix_workbench") >= 1, "the Matrix Workbench is picked up",
					count(p, "world_soil_0") >= 1, "World Soil 0 is picked up",
					count(p, "shell_shard") >= fr.achedon12.matriochka.entity.MatrioBoss.SHELL_SHARDS, "Shell Shards are given",
					count(p, "artisan_scroll") == 0, "the Scroll has become the Journal (" + count(p, "artisan_journal") + " Journal)");
			});
		});
	}

	// ---------------------------------------------------------------- a world
	private static void world(ClientGameTestContext ctx, TestServerContext server, int w) {
		Defs.BossDef boss = ModContent.bossForWorld(w);
		step(ctx, server, "W" + w + " craft the Seed", () -> server.computeOnServer(s -> craftSeed(s, w)));
		// a player tick sends the inventory change that opens the world's advancement tab, before the Seed is planted
		ctx.waitTicks(2);
		step(ctx, server, "W" + w + " plant the Seed", () -> server.computeOnServer(s -> plant(s, w)));
		step(ctx, server, "W" + w + " hatch", () -> {
			boolean formed = false;
			for (int t = 0; t < 600 && !formed; t += 20) {
				ctx.waitTicks(20);
				formed = server.computeOnServer(s -> player(s).level().getBlockState(plotSeed(w)).is(ModContent.block("world_block")));
			}
			boolean f = formed;
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				boolean tracked = MatrioData.get(s).hasWorldBlock(s, group(p), w);
				unblock(s, w);
				return checks(f, "the Seed hatches into the World " + w + " Block", tracked, "the group's World Block is tracked");
			});
		});
		step(ctx, server, "W" + w + " enter", () -> {
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				if (w == 7) wear(p, true);
				tp(p, plotSeed(w).north(2).below());
				emptyHand(p);
				useOn(p, plotSeed(w), Direction.NORTH);
			});
			ctx.waitTicks(100);
			ctx.setScreen(() -> null);
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				return checks(Worlds.number(p.level()) == w, "using the World Block enters World " + w + " (in " + p.level().dimension().identifier() + ")",
					achieved(p, "world_" + w + "/a0"), "the world's first advancement is granted");
			});
		});
		step(ctx, server, "W" + w + " wake " + boss.id(), () -> {
			String how = server.computeOnServer(s -> approach(s, w, boss));
			ctx.waitTicks(80);
			String how2 = server.computeOnServer(s -> boss.lair() ? how : offer(s, w, boss));
			boolean up = awaitBoss(ctx, server, boss.id(), 400);
			return checks(up, how2);
		});
		step(ctx, server, "W" + w + " defeat " + boss.id(), () -> {
			defeat(ctx, server, boss);
			ctx.setScreen(() -> null);
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				List<String> out = checks(MatrioData.get(s).defeated(group(p), w), "the group has beaten " + boss.id(),
					PlayerState.of(p).has("boss_" + w), "the player took part (boss_" + w + ")",
					count(p, boss.core()) >= 1, "the " + boss.core() + " is picked up");
				String adv = killAdvancement(boss.id());
				if (!adv.isEmpty()) out.addAll(checks(achieved(p, adv), "its advancement " + adv + " is granted"));
				if (w < 10 && count(p, "world_soil_" + w) == 0) {
					// lost to lava or the void: World Soil can be made at the workbench too
					out.add("info World Soil " + w + " was not picked up, it will be crafted");
				}
				if (w == 9) out.addAll(checks(count(p, "last_doll_key") >= 1, "the Key of the Last Doll is picked up"));
				if (w == 10) out.addAll(checks(PlayerState.of(p).has("end_seal") || PlayerState.of(p).has("end_absorb"),
					"the Unfinished's fall plays an ending (karma " + PlayerState.of(p).karma() + ")"));
				return out;
			});
		});
		step(ctx, server, "W" + w + " leave", () -> {
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				CompoundTag e = MatrioData.get(s).worldEntry(group(p), w);
				BlockPos seuil = new BlockPos(e.getIntOr("seuil_x", 0), e.getIntOr("seuil_y", 64), e.getIntOr("seuil_z", 0));
				tp(p, seuil.north().above());
				emptyHand(p);
				useOn(p, seuil, Direction.UP);
			});
			ctx.waitTicks(60);
			ctx.setScreen(() -> null);
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				if (w == 7) wear(p, false);
				return checks(Worlds.number(p.level()) == 0, "the Threshold leads back to the Surface");
			});
		});
	}

	private static BlockPos plotSeed(int w) {
		// the Seismic Stake is driven into stone below y 40
		if (w == 1) return plot(w).above();
		// the rites of Worlds 2 to 10 are built in their own row, well away from the workbench and the World 1 plot
		BlockPos r = base.offset(40 + (w - 2) * 14, 2, 40);
		return w == 9 ? r.atY(30) : r;
	}

	private static List<String> craftSeed(MinecraftServer s, int w) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		tp(p, bench.north(2));
		var list = Recipes.of("matrix_workbench");
		int idx = -1;
		for (int i = 0; i < list.size(); i++) if (list.get(i).output().equals("seed_" + w)) idx = i;
		if (idx < 0) throw new Abort("no recipe for seed_" + w);
		Recipes.Recipe r = list.get(idx);
		List<String> out = new ArrayList<>();
		for (Recipes.Ing ing : r.inputs()) {
			boolean fromBoss = ing.id().endsWith("_core") || ing.id().equals("last_doll_key");
			if (fromBoss) {
				out.addAll(checks(count(p, ing.id()) >= ing.count(), "the " + ing.id() + " won from the boss is at hand"));
			} else {
				// the resources a player farms in the world before: given
				int missing = ing.count() - count(p, ing.id());
				if (missing > 0) give(p, ing.id(), missing);
			}
		}
		if (w == 1 && count(p, "world_soil_0") == 0) {
			// the soil fell where it could not be picked up: craft it (dirt and a pinch of spores)
			for (int i = 0; i < list.size(); i++) {
				if (!list.get(i).output().equals("world_soil_0")) continue;
				for (Recipes.Ing ing : list.get(i).inputs()) give(p, ing.id(), ing.count());
				String err = Stations.craft(p, level, bench, "matrix_workbench", (DataBlockEntity) level.getBlockEntity(bench), i);
				out.addAll(checks(err == null, "World Soil 0 is crafted at the workbench (" + err + ")"));
			}
		}
		int before = count(p, "seed_" + w);
		String err = Stations.craft(p, level, bench, "matrix_workbench", (DataBlockEntity) level.getBlockEntity(bench), idx);
		out.addAll(checks(err == null && count(p, "seed_" + w) == before + 1, "the World " + w + " Seed is crafted at the Matrix Workbench (" + err + ")"));
		return out;
	}

	/**
	 * Opens the way into a world: World 1's Seed on tilled World Soil, every other world through its own rite, built
	 * as the player would (RitesTest.scene) and performed with the player's right click.
	 */
	private static List<String> plant(MinecraftServer s, int w) {
		if (w >= 2) return rite(s, w);
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		BlockPos seed = plotSeed(w), soil = seed.below();
		// the plot: a pad under the soil (World 6 wants height), the column above cleared to the sky
		BlockPos pad = soil.below();
		for (int dx = -2; dx <= 2; dx++) for (int dz = -3; dz <= 2; dz++) if (!level.getBlockState(pad.offset(dx, 0, dz)).isSolid()) level.setBlock(pad.offset(dx, 0, dz), Blocks.STONE_BRICKS.defaultBlockState(), 3);
		for (int y = soil.getY(); y <= soil.getY() + 80; y++) level.setBlock(new BlockPos(seed.getX(), y, seed.getZ()), Blocks.AIR.defaultBlockState(), 3);
		tp(p, soil.north(2));
		String soilId = "world_soil_" + (w - 1);
		boolean held = hold(p, soilId);
		if (held) useOn(p, pad, Direction.UP);
		boolean laid = level.getBlockState(soil).getBlock() instanceof Blocks2.WorldSoil;
		hold(p, "minecraft:diamond_hoe");
		useOn(p, soil, Direction.UP);
		boolean tilled = laid && level.getBlockState(soil).getValue(Blocks2.WorldSoil.TILLED);
		// what this world's Seed needs nearby
		BlockPos side = soil.east(2);
		switch (w) {
			case 1, 7 -> {
				for (Direction d : Direction.Plane.HORIZONTAL) level.setBlock(side.relative(d), Blocks.STONE_BRICKS.defaultBlockState(), 3);
				level.setBlock(side, Blocks.WATER.defaultBlockState(), 3);
			}
			case 2 -> level.setBlock(side, Blocks.MAGMA_BLOCK.defaultBlockState(), 3);
			case 3, 9 -> level.setBlock(soil.east(), Blocks.REDSTONE_BLOCK.defaultBlockState(), 3);
			case 8 -> s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput(), "time set 23000");
			default -> {}
		}
		hold(p, "seed_" + w);
		useOn(p, soil, Direction.UP);
		boolean planted = level.getBlockState(seed).is(ModContent.block("planted_seed"));
		if (w == 5) {
			// the Lightless Deep only hatches in the dark: wall the Seed in
			for (Direction d : Direction.Plane.HORIZONTAL) level.setBlock(seed.relative(d), Blocks.STONE.defaultBlockState(), 3);
			level.setBlock(seed.above(), Blocks.STONE.defaultBlockState(), 3);
		}
		return checks(achieved(p, "world_" + w + "/root"), "holding the Seed opens the World " + w + " advancement tab",
			held && laid, "World Soil " + (w - 1) + " is laid", tilled, "the hoe tills it", planted, "the World " + w + " Seed is planted");
	}

	private static List<String> rite(MinecraftServer s, int w) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		BlockPos seed = plotSeed(w);
		// the Storm Rod sits on a lightning rod, so its site is one block above the rod
		BlockPos click = RitesTest.scene(level, w, w == 4 ? seed.below() : seed);
		// the Storm Rod needs the open sky over it: clear the column up to the sky
		if (w == 4) for (int y = seed.getY() + 1; y <= seed.getY() + 120; y++) level.setBlock(new BlockPos(seed.getX(), y, seed.getZ()), Blocks.AIR.defaultBlockState(), 3);
		tp(p, seed.north(2));
		boolean held = hold(p, "seed_" + w);
		useOn(p, click, Direction.UP);
		boolean placed = level.getBlockState(seed).is(ModContent.block("planted_seed"));
		if (w == 4 && placed) {
			// no storm on call: a Storm Essence opens it
			give(p, "storm_essence", 1);
			hold(p, "storm_essence");
			useOn(p, seed, Direction.NORTH);
		}
		if (w == 8) s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput(), "time set 23000");
		return checks(achieved(p, "world_" + w + "/root"), "holding the World " + w + " object opens its advancement tab",
			held, "the World " + w + " object is at hand", placed, "the World " + w + " rite is set down");
	}

	/** After hatching: opens what walled the Seed in and sets the time back. */
	private static void unblock(MinecraftServer s, int w) {
		ServerLevel level = (ServerLevel) player(s).level();
		BlockPos seed = plotSeed(w);
		if (w == 5) {
			for (Direction d : Direction.Plane.HORIZONTAL) level.setBlock(seed.relative(d), Blocks.AIR.defaultBlockState(), 3);
			level.setBlock(seed.above(), Blocks.AIR.defaultBlockState(), 3);
		}
		if (w == 8) s.getCommands().performPrefixedCommand(s.createCommandSourceStack().withSuppressedOutput(), "time set 6000");
	}

	/** Goes to the boss's stage: next to the lair heart (which wakes the boss) or to the arena altar. */
	private static String approach(MinecraftServer s, int w, Defs.BossDef boss) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		CompoundTag e = MatrioData.get(s).worldEntry(group(p), w);
		BlockPos seuil = new BlockPos(e.getIntOr("seuil_x", 0), e.getIntOr("seuil_y", 64), e.getIntOr("seuil_z", 0));
		BlockPos center = seuil.offset(0, 0, Worlds.ARENA_OFFSET);
		level.getChunk(center);
		if (boss.lair()) {
			BlockPos heart = Lairs.heart(w, center);
			tp(p, heart.offset(0, 1, -6));
			return "walking up to the lair heart wakes " + boss.id();
		}
		tp(p, center.above(2));
		return "the arena of " + boss.id();
	}

	/** At an arena altar: holds the offering and uses the altar, which starts the ritual. */
	private static String offer(MinecraftServer s, int w, Defs.BossDef boss) {
		ServerPlayer p = player(s);
		ServerLevel level = (ServerLevel) p.level();
		CompoundTag e = MatrioData.get(s).worldEntry(group(p), w);
		BlockPos center = new BlockPos(e.getIntOr("seuil_x", 0), e.getIntOr("seuil_y", 64), e.getIntOr("seuil_z", 0)).offset(0, 0, Worlds.ARENA_OFFSET);
		BlockPos altar = null;
		for (BlockPos q : BlockPos.betweenClosed(center.offset(-20, -12, -20), center.offset(20, 12, 20))) {
			if (level.getBlockState(q).getBlock() instanceof Blocks3.BossAltar) {
				altar = q.immutable();
				break;
			}
		}
		if (altar == null) throw new Abort("no arena altar around " + center.toShortString() + " in World " + w);
		// the offering is crafted at the world's station from what the world gives: given here
		give(p, boss.offering(), 1);
		tp(p, altar.north(2));
		hold(p, boss.offering());
		useOn(p, altar, Direction.UP);
		boolean ritual = Rituals.busy(level, altar);
		if (!ritual) throw new Abort("the altar of World " + w + " did not take the " + boss.offering());
		return "holding the " + boss.offering() + " at the altar starts the ritual that wakes " + boss.id();
	}

	// ---------------------------------------------------------------- the end
	private static void endgame(ClientGameTestContext ctx, TestServerContext server) {
		step(ctx, server, "nest the hidden dolls", () -> server.computeOnServer(s -> {
			ServerPlayer p = player(s);
			emptyHand(p);
			int[] order = Content.NEST_ORDER;
			// found in the worlds' structures: given here
			for (int w = 1; w <= 10; w++) give(p, "hidden_doll_" + w, 1);
			hold(p, "hidden_doll_" + order[0]);
			boolean ok = true;
			for (int k = 1; k < 10; k++) {
				int slot = -1;
				var inv = p.getInventory();
				for (int i = 0; i < inv.getContainerSize(); i++) if (inv.getItem(i).is(item("hidden_doll_" + order[k]))) slot = i;
				if (slot < 0) return checks(false, "hidden doll " + order[k] + " in the inventory");
				p.setItemInHand(InteractionHand.OFF_HAND, inv.getItem(slot).copy());
				inv.setItem(slot, ItemStack.EMPTY);
				p.gameMode.useItem(p, p.level(), p.getMainHandItem(), InteractionHand.MAIN_HAND);
				if (!p.getOffhandItem().isEmpty()) ok = false;
			}
			return checks(ok && p.getMainHandItem().is(item("whole_matryoshka")), "the ten dolls nest into the Whole Matryoshka",
				customAchieved(p, "all_dolls"), "Every Doll is granted");
		}));
		step(ctx, server, "open World 0", () -> {
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				p.gameMode.useItem(p, p.level(), p.getMainHandItem(), InteractionHand.MAIN_HAND);
			});
			ctx.waitTicks(60);
			ctx.setScreen(() -> null);
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				return checks(Worlds.number(p.level()) == Worlds.ZERO, "the Whole Matryoshka opens World 0", achieved(p, "endings/world_zero"), "The Smallest Doll is granted");
			});
		});
		for (int k = 0; k < 3; k++) {
			int chamber = k;
			step(ctx, server, "World 0 chamber " + k, () -> {
				server.runOnServer(s -> {
					ServerPlayer p = player(s);
					MatrioData data = MatrioData.get(s);
					BlockPos o = WorldZero.origin(data, group(p), (ServerLevel) p.level());
					tp(p, WorldZero.chamberCenter(o, chamber));
				});
				ctx.waitTicks(60);
				String tag = "zero_" + chamber;
				int guards = server.computeOnServer(s -> player(s).level().getEntitiesOfClass(MatrioMob.class, player(s).getBoundingBox().inflate(48), m -> m.entityTags().contains(tag)).size());
				server.runOnServer(s -> arm(player(s), 4000));
				int blows = fight(ctx, server, e -> e instanceof MatrioMob m && m.entityTags().contains(tag), 64, 400);
				ctx.waitTicks(60);
				return server.computeOnServer(s -> {
					ServerPlayer p = player(s);
					BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), (ServerLevel) p.level());
					return checks(guards >= 3, "the chamber's guards wake (" + guards + ", " + blows + " blows)",
						p.level().getBlockState(WorldZero.gateCenter(o, chamber)).isAir(), "its gate opens once they are down");
				});
			});
		}
		step(ctx, server, "the Artisan's Shadow", () -> {
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), (ServerLevel) p.level());
				tp(p, WorldZero.kneelSpot(o));
			});
			ctx.waitTicks(60);
			boolean shadow = server.computeOnServer(s -> bossAlive(s, "artisan_shadow"));
			server.runOnServer(s -> arm(player(s), 4000));
			boolean stitched = false;
			for (int i = 0; i < 40 && !stitched; i++) {
				ctx.waitTicks(SWING);
				server.computeOnServer(s -> strike(s, e -> e instanceof MatrioBoss b && b.def.id().equals("artisan_shadow"), 64));
				stitched = server.computeOnServer(s -> MatrioData.get(s).worldEntry(group(player(s)), Worlds.ZERO).getBooleanOr("stitched", false));
			}
			return checks(shadow, "the Shadow wakes in the Artisan's room", stitched, "brought near death, it stitches itself back");
		});
		step(ctx, server, "set down the tools", () -> {
			// the creatures the Shadow called in with the attacks it borrows from the worlds stay in the room: kneeling
			// must still them too, or their blows knock the player off the carpet. Two more are set on the player, so the
			// check always has some to calm
			int minions = server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				ServerLevel level = (ServerLevel) p.level();
				BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), level);
				BlockPos k = WorldZero.kneelSpot(o);
				for (int i = 0; i < 2; i++) {
					var e = fr.achedon12.matriochka.content.ModContent.entity("sporeling").create(level, net.minecraft.world.entity.EntitySpawnReason.MOB_SUMMONED);
					if (e instanceof MatrioMob m) {
						m.setPos(k.getX() + 0.5 + (i == 0 ? 3 : -3), k.getY(), k.getZ() + 0.5);
						m.setTarget(p);
						m.addTag("matrio_child");
						level.addFreshEntity(m);
					}
				}
				return level.getEntitiesOfClass(MatrioMob.class, new AABB(k).inflate(48), MatrioMob::isAlive).size();
			});
			OUT.add("info " + minions + " creature(s) of the Shadow in the room before kneeling");
			server.runOnServer(s -> {
				ServerPlayer p = player(s);
				BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), (ServerLevel) p.level());
				emptyHand(p);
				p.setItemInHand(InteractionHand.OFF_HAND, ItemStack.EMPTY);
				tp(p, WorldZero.kneelSpot(o));
			});
			ctx.runOnClient(mc -> mc.options.keyShift.setDown(true));
			boolean done = false;
			int[] knocked = {0};
			for (int t = 0; t < 600 && !done; t += 20) {
				ctx.waitTicks(20);
				final int second = t / 20;
				done = server.computeOnServer(s -> {
					ServerPlayer p = player(s);
					BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), (ServerLevel) p.level());
					if (p.position().distanceTo(Vec3.atBottomCenterOf(WorldZero.kneelSpot(o))) > 1) {
						// once the kneel has stilled the room (its first second), nothing may push the player off the carpet
						if (second >= 2) knocked[0]++;
						tp(p, WorldZero.kneelSpot(o));
					}
					p.setShiftKeyDown(true);
					return PlayerState.of(p).has("end_tools");
				});
			}
			ctx.runOnClient(mc -> mc.options.keyShift.setDown(false));
			ctx.waitTicks(40);
			ctx.setScreen(() -> null);
			return server.computeOnServer(s -> {
				ServerPlayer p = player(s);
				PlayerState ps = PlayerState.of(p);
				BlockPos o = WorldZero.origin(MatrioData.get(s), group(p), (ServerLevel) p.level());
				int left = p.level().getEntitiesOfClass(MatrioMob.class, new AABB(WorldZero.kneelSpot(o)).inflate(48), MatrioMob::isAlive).size();
				return checks(minions >= 2 && left == 0, "kneeling stills the Shadow's creatures and they unravel (" + minions + " before, " + left + " after)",
					knocked[0] == 0, "nothing knocks the kneeling player off the carpet (" + knocked[0] + ")",
					ps.has("end_tools"), "kneeling empty-handed sets the tools down",
					customAchieved(p, "third_end"), "Set Down the Tools is granted",
					count(p, "blank_scroll") >= 1, "the Blank Scroll is given",
					achieved(p, ps.has("end_seal") ? "endings/seal" : "endings/absorb"), "the Unfinished's ending advancement is granted");
			});
		});
	}
}
