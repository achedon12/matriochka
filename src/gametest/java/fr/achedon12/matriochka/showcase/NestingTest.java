package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.NestingCradle;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.gear.Matriarch;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.WorldOres;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.CameraType;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/**
 * The ten world ores, the Nesting Cradle and the Matriarch Armour (0.9.0): ./gradlew runClientGameTest -Pnesting, and
 * at the end of -Ppolish. Checks in game how each ore is had where the server can tell (the ember with and without
 * heat, the silent stone with and without noise, the blooms near water, the ore that falls upwards, the fulgurite a
 * bolt leaves, the brine crystal's odds, the Time Seed ripening, the heartstones), runs the cradle's ritual from the
 * ten ores to the ingot, and wears the Matriarch Armour: its stats, its halved gauges and the Nested Shell's one save
 * before the Doll of Life. Shots: nesting_*.png.
 */
final class NestingTest {
	private NestingTest() {}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of("nesting_" + name).withSize(1600, 900).disableCounterPrefix());
	}

	private static ServerPlayer player(MinecraftServer s) {
		return s.getPlayerList().getPlayers().get(0);
	}

	/** A failed check, kept so every one is reported before the run fails. */
	private static final List<String> FAILED = new ArrayList<>();

	private static void check(boolean ok, String what) {
		Matriochka.LOG.info("[nesting] {} {}", ok ? "ok  " : "FAIL", what);
		if (!ok) FAILED.add(what);
	}

	private static int count(ServerLevel l, BlockPos at, String id) {
		int n = 0;
		for (ItemEntity e : l.getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(2.5), e -> e.getItem().is(ModContent.item(id)))) n += e.getItem().getCount();
		return n;
	}

	private static void clearItems(ServerLevel l, BlockPos at) {
		for (ItemEntity e : l.getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(6))) e.discard();
	}

	/** Breaks a block as the player would, with the tool in hand (the real path: loot, events, the ore rules). */
	private static void mine(ServerPlayer p, ServerLevel l, BlockPos at, net.minecraft.world.level.block.state.BlockState state) {
		l.setBlock(at, state, 3);
		p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.NETHERITE_PICKAXE));
		p.gameMode.destroyBlock(at);
	}

	private static void use(ServerPlayer p, ServerLevel l, BlockPos at, ItemStack stack) {
		p.setItemInHand(InteractionHand.MAIN_HAND, stack);
		p.gameMode.useItemOn(p, l, stack, InteractionHand.MAIN_HAND, new BlockHitResult(Vec3.atCenterOf(at).add(0, 0.4, 0), Direction.UP, at, false));
	}

	static void run(ClientGameTestContext ctx) {
		FAILED.clear();
		ctx.getInput().resizeWindow(1600, 900);
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			McTest.waitForChunks(sp);
			for (String c : List.of("gamerule advance_time false", "time set 6000", "gamerule spawn_monsters false", "gamerule advance_weather false",
				"weather clear", "gamemode survival @a", "gamerule spawn_mobs false")) s.runCommand(c);
			ctx.setScreen(() -> null);
			// a stage in the open sky: a floor of painted wood at y 149, the player on it
			BlockPos origin = s.computeOnServer(server -> {
				ServerPlayer p = player(server);
				ServerLevel l = server.overworld();
				BlockPos o = new BlockPos(p.getBlockX(), 149, p.getBlockZ());
				for (int dx = -8; dx <= 8; dx++)
					for (int dz = -8; dz <= 8; dz++) {
						l.setBlock(o.offset(dx, 0, dz), (dx + dz) % 2 == 0 ? ModContent.block("painted_wood").defaultBlockState() : ModContent.block("lacquer_block").defaultBlockState(), 3);
						for (int dy = 1; dy <= 6; dy++) l.setBlock(o.offset(dx, dy, dz), Blocks.AIR.defaultBlockState(), 3);
					}
				p.connection.teleport(o.getX() + 0.5, o.getY() + 1, o.getZ() + 4.5, 180, 8);
				p.getAbilities().invulnerable = false;
				return o;
			});
			ctx.waitTicks(40);
			McTest.waitForChunks(sp);
			oreRules(s, origin);
			itemsShot(ctx, s, origin);
			cradle(ctx, s, origin);
			armour(ctx, s, origin);
			journal(ctx, s);
			if (!FAILED.isEmpty()) throw new AssertionError("nesting: " + FAILED);
			Matriochka.LOG.info("[nesting] ok");
		}
	}

	// ---------------------------------------------------------------- (a) the ores
	private static void oreRules(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, BlockPos origin) {
		String out = s.computeOnServer(server -> {
			ServerPlayer p = player(server);
			ServerLevel l = server.overworld();
			PlayerState ps = PlayerState.of(p);
			BlockPos at = origin.offset(-5, 1, -5);
			StringBuilder sb = new StringBuilder();
			// the Living Ember: ash with a cold hand, the ember with a hot one
			clearItems(l, at);
			ps.setGauge("heat", 20);
			mine(p, l, at, ModContent.block("living_ember_ore").defaultBlockState());
			int ash = count(l, at, "ashrock"), cold = count(l, at, "living_ember");
			clearItems(l, at);
			ps.setGauge("heat", 85);
			mine(p, l, at, ModContent.block("living_ember_ore").defaultBlockState());
			int hot = count(l, at, "living_ember");
			sb.append("ember cold ash=").append(ash).append(" ember=").append(cold).append(", hot ember=").append(hot).append("; ");
			check(ash == 1 && cold == 0 && hot == 1, "Living Ember: ash at Heat 20 (" + ash + "/" + cold + "), the ember at Heat 85 (" + hot + ")");
			// the Silent Stone: nothing with noise, the stone in silence
			clearItems(l, at);
			ps.setGauge("noise", 30);
			mine(p, l, at, ModContent.block("silent_stone_ore").defaultBlockState());
			int loud = l.getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(2.5)).size();
			clearItems(l, at);
			ps.setGauge("noise", 0);
			mine(p, l, at, ModContent.block("silent_stone_ore").defaultBlockState());
			int quiet = count(l, at, "silent_stone");
			check(loud == 0 && quiet == 1, "Silent Stone: shatters with Noise 30 (" + loud + " drops), gives itself at Noise 0 (" + quiet + ")");
			// the Spore Crystal: only from blooms near water (one in about seven)
			clearItems(l, at);
			int dry = 0, wet = 0;
			for (int i = 0; i < 40; i++) {
				mine(p, l, at, ModContent.block("spore_bloom").defaultBlockState());
				dry += count(l, at, "spore_crystal");
				clearItems(l, at);
			}
			l.setBlock(at.offset(2, 0, 0), Blocks.WATER.defaultBlockState(), 3);
			for (int i = 0; i < 80; i++) {
				mine(p, l, at, ModContent.block("spore_bloom").defaultBlockState());
				wet += count(l, at, "spore_crystal");
				clearItems(l, at);
			}
			l.setBlock(at.offset(2, 0, 0), Blocks.AIR.defaultBlockState(), 3);
			check(dry == 0 && wet >= 3 && wet <= 30, "Spore Crystal: " + dry + " from 40 dry blooms, " + wet + " from 80 blooms near water");
			// the Inverted Ore falls upwards
			clearItems(l, at);
			mine(p, l, at, ModContent.block("hanging_ore").defaultBlockState());
			var up = l.getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(2.5), e -> e.getItem().is(ModContent.item("inverted_ore")));
			check(up.size() == 1 && up.getFirst().isNoGravity() && up.getFirst().getDeltaMovement().y > 0, "Inverted Ore: one drop, falling upwards");
			clearItems(l, at);
			// the Fulgurite: a bolt on cloudstone fuses it, the crust gives the ore
			l.setBlock(at, ModContent.block("cloudstone").defaultBlockState(), 3);
			boolean fused = WorldOres.fuse(l, Vec3.atBottomCenterOf(at.above())) && l.getBlockState(at).is(ModContent.block("fulgurite_ore"));
			mine(p, l, at, ModContent.block("fulgurite_ore").defaultBlockState());
			int fulg = count(l, at, "fulgurite");
			check(fused && fulg >= 1, "Fulgurite: the bolt fuses cloudstone (" + fused + "), the crust gives " + fulg);
			clearItems(l, at);
			// the Brine Crystal: one in twenty-five from World 7's creatures only
			check(WorldOres.brine(7, 0.03f) && !WorldOres.brine(7, 0.05f) && !WorldOres.brine(1, 0.0f) && Content.ORE_BRINE_CHANCE == 0.04f,
				"Brine Crystal: 4 % from World 7's creatures, never elsewhere");
			// the Heartstones: two or three
			int lo = 9, hi = 0;
			for (int i = 0; i < 60; i++) {
				int n = WorldOres.heartstones(l.getRandom());
				lo = Math.min(lo, n);
				hi = Math.max(hi, n);
			}
			check(lo == 2 && hi == 3, "Heartstones: " + lo + " to " + hi);
			// the Time Seed: refused outside World 8; planted, it ripens stage by stage into the Chrono Shard
			BlockPos soil = origin.offset(5, 1, -5);
			l.setBlock(soil, Blocks.GRASS_BLOCK.defaultBlockState(), 3);
			ItemStack seed = new ItemStack(ModContent.item("time_seed"));
			boolean refused = !WorldOres.plant(l, p, soil, seed) && seed.getCount() == 1;
			l.setBlock(soil.above(), ModContent.block("time_sprout").defaultBlockState(), 3);
			boolean scheduled = l.getBlockTicks().hasScheduledTick(soil.above(), ModContent.block("time_sprout"));
			for (int i = 0; i < 3; i++) {
				var st = l.getBlockState(soil.above());
				st.tick(l, soil.above(), l.getRandom());
			}
			int age = l.getBlockState(soil.above()).getValue(fr.achedon12.matriochka.block.TimeSprout.AGE);
			clearItems(l, soil);
			p.gameMode.destroyBlock(soil.above());
			int shard = count(l, soil.above(), "chrono_shard");
			check(refused && scheduled && age == 3 && shard == 1 && Content.ORE_SPROUT_STAGE_TICKS * 3 <= 2400 + 600,
				"Time Seed: refused outside World 8 (" + refused + "), growing on its clock (" + scheduled + "), ripe after 3 stages of "
					+ Content.ORE_SPROUT_STAGE_TICKS + " ticks (age " + age + "), gives the Chrono Shard (" + shard + ")");
			clearItems(l, soil);
			l.setBlock(soil, Blocks.AIR.defaultBlockState(), 3);
			ps.setGauge("heat", 0);
			return sb.toString();
		});
		Matriochka.LOG.info("[nesting] ores: {}", out);
	}

	// ---------------------------------------------------------------- the ores and the ingot, as items
	private static void itemsShot(ClientGameTestContext ctx, net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, BlockPos origin) {
		s.runOnServer(server -> {
			ServerLevel l = server.overworld();
			ServerPlayer p = player(server);
			p.connection.teleport(origin.getX() + 0.5, origin.getY() + 1, origin.getZ() + 4.5, 180, 4);
			for (int w = 1; w <= 10; w++) {
				int i = w - 1;
				double x = origin.getX() + 0.5 + (i % 5 - 2) * 1.0, y = origin.getY() + 2.1 + (i < 5 ? 0.62 : -0.2), z = origin.getZ() + 1.6;
				showcase(l, WorldOres.ore(w), new Vec3(x, y, z), 0.75f);
			}
			showcase(l, new ItemStack(ModContent.item("matriochkite_ingot")), new Vec3(origin.getX() + 0.5, origin.getY() + 3.4, origin.getZ() + 1.6), 1.1f);
			showcase(l, new ItemStack(ModContent.item("matriochkite_nugget")), new Vec3(origin.getX() - 0.8, origin.getY() + 3.4, origin.getZ() + 1.6), 0.8f);
			showcase(l, new ItemStack(ModContent.item("matriochkite_block")), new Vec3(origin.getX() + 1.8, origin.getY() + 3.4, origin.getZ() + 1.6), 0.6f);
		});
		Film.hud(ctx, false);
		ctx.waitTicks(30);
		shot(ctx, "items");
		s.runCommand("kill @e[type=minecraft:item_display,tag=nesting_showcase]");
		// the block, placed: three of them as a little plinth under a beacon's light
		s.runOnServer(server -> {
			ServerLevel l = server.overworld();
			for (int dx = -1; dx <= 1; dx++) l.setBlock(origin.offset(dx, 1, 1), ModContent.block("matriochkite_block").defaultBlockState(), 3);
			l.setBlock(origin.offset(0, 2, 1), ModContent.block("matriochkite_block").defaultBlockState(), 3);
			player(server).connection.teleport(origin.getX() + 0.5, origin.getY() + 1, origin.getZ() + 4.2, 180, 22);
		});
		ctx.waitTicks(20);
		shot(ctx, "block_placed");
		boolean recipes = s.computeOnServer(server -> {
			for (String r : List.of("matriochkite_block", "matriochkite_ingot", "matriochkite_ingot_from_matriochkite_block", "matriochkite_nugget_from_matriochkite_ingot"))
				if (server.getRecipeManager().byKey(net.minecraft.resources.ResourceKey.create(net.minecraft.core.registries.Registries.RECIPE, Matriochka.id(r))).isEmpty()) return false;
			ServerLevel l = server.overworld();
			for (int dx = -1; dx <= 1; dx++) l.setBlock(origin.offset(dx, 1, 1), Blocks.AIR.defaultBlockState(), 3);
			l.setBlock(origin.offset(0, 2, 1), Blocks.AIR.defaultBlockState(), 3);
			return l.getBlockState(origin.above()).isAir() && ModContent.block("matriochkite_block").defaultBlockState().is(net.minecraft.tags.BlockTags.BEACON_BASE_BLOCKS);
		});
		check(recipes, "the Matriochkite's crafting recipes (nuggets, ingot, block) load, and the block bears a beacon");
		Film.hud(ctx, true);
	}

	private static void showcase(ServerLevel l, ItemStack stack, Vec3 at, float scale) {
		var d = fr.achedon12.matriochka.mc.McEntities.ITEM_DISPLAY.create(l, net.minecraft.world.entity.EntitySpawnReason.COMMAND);
		if (d == null) return;
		((fr.achedon12.matriochka.mixin.ItemDisplayAccess) d).matriochka$setItem(stack);
		((fr.achedon12.matriochka.mixin.DisplayAccess) d).matriochka$setTransformation(new com.mojang.math.Transformation(null, null, new org.joml.Vector3f(scale, scale, scale), null));
		((fr.achedon12.matriochka.mixin.DisplayAccess) d).matriochka$setBrightness(new net.minecraft.util.Brightness(15, 15));
		d.addTag("nesting_showcase");
		d.setPos(at.x, at.y, at.z);
		d.setYRot(180);
		l.addFreshEntity(d);
	}

	// ---------------------------------------------------------------- (b) the cradle and its ritual
	private static long cradleTime(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, BlockPos at) {
		return s.computeOnServer(server -> server.overworld().getBlockEntity(at) instanceof DataBlockEntity be ? NestingCradle.start(be) - server.overworld().getGameTime() : 0L);
	}

	private static void cradle(ClientGameTestContext ctx, net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, BlockPos origin) {
		BlockPos at = origin.above();
		// take-back and breaking first, on a cradle of their own
		String early = s.computeOnServer(server -> {
			ServerLevel l = server.overworld();
			ServerPlayer p = player(server);
			BlockPos c = origin.offset(4, 1, -4);
			l.setBlock(c, ModContent.block("nesting_cradle").defaultBlockState(), 3);
			use(p, l, c, WorldOres.ore(1));
			use(p, l, c, WorldOres.ore(2));
			use(p, l, c, WorldOres.ore(2).copy());
			int twice = l.getBlockEntity(c) instanceof DataBlockEntity be ? NestingCradle.ores(be).length : -1;
			use(p, l, c, ItemStack.EMPTY);
			int after = l.getBlockEntity(c) instanceof DataBlockEntity be ? NestingCradle.ores(be).length : -1;
			boolean back = fr.achedon12.matriochka.block.Stations.count(p.getInventory(), ModContent.item(Content.WORLD_ORES[2])) >= 1;
			use(p, l, c, WorldOres.ore(3));
			use(p, l, c, WorldOres.ore(4));
			clearItems(l, c);
			l.destroyBlock(c, false);
			int spilled = count(l, c, Content.WORLD_ORES[1]) + count(l, c, Content.WORLD_ORES[3]) + count(l, c, Content.WORLD_ORES[4]);
			clearItems(l, c);
			p.getInventory().clearContent();
			return "the same world's ore twice keeps " + twice + ", an empty hand takes the last back (" + after + ", " + back + "), broken it gives back " + spilled;
		});
		check(early.equals("the same world's ore twice keeps 2, an empty hand takes the last back (1, true), broken it gives back 3"), "cradle: " + early);
		// the cradle on the stage, its face to the camera, five ores on its ring
		s.runOnServer(server -> {
			ServerLevel l = server.overworld();
			ServerPlayer p = player(server);
			l.setBlock(at, ModContent.block("nesting_cradle").defaultBlockState().setValue(NestingCradle.FACING, Direction.SOUTH), 3);
			for (int w = 1; w <= 5; w++) use(p, l, at, WorldOres.ore(w));
			p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
		});
		// the camera: a spectator a little above and in front, the cradle and the whole height of the shells in frame
		s.runCommand("gamemode spectator @a");
		s.runOnServer(server -> player(server).connection.teleport(at.getX() + 0.5, at.getY() + 0.55, at.getZ() + 4.3, 180, 4));
		ctx.runOnClient(mc -> mc.options.fov().set(55));
		// at dusk, so the gold and the worlds' lights glow against the sky
		s.runCommand("time set 11900");
		Film.hud(ctx, false);
		ctx.waitTicks(50);
		shot(ctx, "cradle_five");
		// the other five: the ritual runs by itself
		s.runOnServer(server -> {
			ServerLevel l = server.overworld();
			ServerPlayer p = player(server);
			p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
			for (int w = 6; w <= 10; w++) use(p, l, at, WorldOres.ore(w));
			p.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
			p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
		});
		long until = cradleTime(s, at);
		check(until > 0, "the tenth ore starts the ritual (in " + until + " ticks)");
		// three moments of the ritual and the ingot: the ring tightening, the shells closing, the flash, the ingot
		// the whole sequence, frame by frame: the ring spinning up and drawing in, the doll thrown open, the nest rising
		// and fanning out, the dolls closing one over the next, the last sinking in, the slam and the flash, the jump,
		// the ingot rising and hovering
		int[] frames = {8, 30, 44, 56, 70, 82, 96, 108, 120, 129, 133, 142, 152};
		for (int i = 0; i < frames.length; i++) {
			long wait = cradleTime(s, at) + frames[i];
			if (wait > 0) ctx.waitTicks((int) wait);
			shot(ctx, String.format("ritual_%02d_t%03d", i + 1, frames[i]));
		}
		ctx.waitTicks(NestingCradle.DURATION - frames[frames.length - 1] + 6);
		Film.hud(ctx, true);
		ctx.runOnClient(mc -> mc.options.fov().set(70));
		s.runCommand("time set 6000");
		s.runCommand("gamemode survival @a");
		String result = s.computeOnServer(server -> {
			ServerLevel l = server.overworld();
			int ingots = 0;
			for (ItemEntity e : l.getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(8), e -> e.getItem().is(ModContent.item("matriochkite_ingot")))) ingots += e.getItem().getCount();
			for (ServerPlayer p : server.getPlayerList().getPlayers()) ingots += fr.achedon12.matriochka.block.Stations.count(p.getInventory(), ModContent.item("matriochkite_ingot"));
			boolean empty = l.getBlockEntity(at) instanceof DataBlockEntity be && NestingCradle.ores(be).length == 0 && !NestingCradle.running(be);
			int left = l.getEntitiesOfClass(net.minecraft.world.entity.Display.ItemDisplay.class, new AABB(at).inflate(4)).size();
			return "ingots " + ingots + ", cradle empty " + empty + ", displays left " + left;
		});
		check(result.equals("ingots 1, cradle empty true, displays left 0"), "ritual: " + result);
		s.runOnServer(server -> {
			for (ItemEntity e : server.overworld().getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(8))) e.discard();
			player(server).getInventory().clearContent();
		});
	}

	// ---------------------------------------------------------------- (c) the Matriarch Armour
	private static void armour(ClientGameTestContext ctx, net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s, BlockPos origin) {
		String[] pieces = {"helmet", "chestplate", "leggings", "boots"};
		EquipmentSlot[] slots = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
		BlockPos c = origin.offset(-4, 0, -5);
		float easedBefore = s.computeOnServer(server -> {
			ServerPlayer p = player(server);
			ServerLevel l = server.overworld();
			// on a floor of pale stone, away from the cradle, so the lacquer and the gold read on their own
			for (int dx = -3; dx <= 3; dx++)
				for (int dz = -3; dz <= 3; dz++) l.setBlock(c.offset(dx, 0, dz), Blocks.SMOOTH_QUARTZ.defaultBlockState(), 3);
			p.connection.teleport(c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, 0, 0);
			float before = Matriarch.ease(p);
			for (int i = 0; i < 4; i++) p.setItemSlot(slots[i], new ItemStack(ModContent.item("matriarch_" + pieces[i])));
			return before;
		});
		// the worn pieces lay their attributes on at the player's next tick
		ctx.waitTicks(3);
		String stats = s.computeOnServer(server -> {
			ServerPlayer p = player(server);
			double armour = p.getAttributeValue(Attributes.ARMOR), tough = p.getAttributeValue(Attributes.ARMOR_TOUGHNESS);
			double kb = p.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), health = p.getMaxHealth();
			// the pieces' own armour, before the attribute's cap of 30
			int sum = 0;
			for (int i = 0; i < 4; i++) {
				var mods = p.getItemBySlot(slots[i]).get(net.minecraft.core.component.DataComponents.ATTRIBUTE_MODIFIERS);
				if (mods != null) for (var e : mods.modifiers()) if (e.attribute().equals(Attributes.ARMOR)) sum += (int) e.modifier().amount();
			}
			float eased = Matriarch.ease(p);
			// the gauges: a gain of 10 toxin builds 5
			PlayerState ps = PlayerState.of(p);
			ps.setGauge("toxin", 0);
			ps.addGauge("toxin", 10f * eased);
			float toxin = ps.gauge("toxin");
			ps.setGauge("toxin", 0);
			p.setHealth(p.getMaxHealth());
			return String.format(java.util.Locale.ROOT, "armour %.0f (pieces %d), toughness %.0f, knockback %.2f, health %.0f, gauge x%.1f (without %.1f), toxin +%.0f",
				armour, sum, tough, kb, health, eased, easedBefore, toxin);
		});
		check(stats.equals("armour 30 (pieces 32), toughness 18, knockback 0.90, health 53, gauge x0.5 (without 1.0), toxin +5"), "Matriarch: " + stats);
		// worn, third person on the stage: front, back, side, the crown and the chest up close
		Film.hud(ctx, false);
		String[][] views = {{"armour_front", "front", "0", "0", "44"}, {"armour_back", "back", "0", "0", "44"}, {"armour_side", "front", "90", "0", "44"},
			{"armour_crown", "front", "0", "-8", "30"}, {"armour_chest", "front", "0", "26", "30"}};
		for (String[] v : views) {
			float yaw = Float.parseFloat(v[2]), pitch = Float.parseFloat(v[3]);
			int fov = Integer.parseInt(v[4]);
			s.runOnServer(server -> player(server).connection.teleport(c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, yaw, pitch));
			ctx.runOnClient(mc -> {
				mc.options.setCameraType(v[1].equals("back") ? CameraType.THIRD_PERSON_BACK : CameraType.THIRD_PERSON_FRONT);
				mc.options.fov().set(fov);
			});
			ctx.waitTicks(30);
			ctx.runOnClient(mc -> mc.particleEngine.clearParticles());
			ctx.waitTicks(2);
			shot(ctx, v[0]);
		}
		ctx.runOnClient(mc -> {
			mc.options.setCameraType(CameraType.FIRST_PERSON);
			mc.options.fov().set(70);
		});
		Film.hud(ctx, true);
		// the HUD: the doll beside the hearts, whole while the shell is ready
		s.runOnServer(server -> player(server).connection.teleport(c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, 0, 30));
		ctx.waitTicks(20);
		boolean hudReady = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.MatriarchTip.secondsLeft() == 0 && fr.achedon12.matriochka.client.MatriarchTip.worn(mc.player) == 4);
		check(hudReady, "the HUD shows the Nested Shell ready with the whole set worn");
		shot(ctx, "hud_ready");
		// the Nested Shell: a deadly blow leaves 6 health, the Doll of Life kept, and the screen cracks gold; the next
		// blow within five minutes is the Doll of Life's
		String save = s.computeOnServer(server -> {
			ServerPlayer p = player(server);
			ServerLevel l = server.overworld();
			PlayerState ps = PlayerState.of(p);
			ps.setDoll(1, 3);
			p.setHealth(p.getMaxHealth());
			fr.achedon12.matriochka.mc.Mc.clearInvulnerable(p);
			p.hurtServer(l, l.damageSources().generic(), 5000f);
			return String.format(java.util.Locale.ROOT, "first blow alive %s at %.0f with the doll kept %s", p.isAlive(), p.getHealth(), ps.dollLayers() == 1);
		});
		ctx.waitTicks(3);
		shot(ctx, "save_effect");
		String second = s.computeOnServer(server -> {
			ServerPlayer p = player(server);
			ServerLevel l = server.overworld();
			PlayerState ps = PlayerState.of(p);
			fr.achedon12.matriochka.mc.Mc.clearInvulnerable(p);
			p.removeAllEffects();
			p.hurtServer(l, l.damageSources().generic(), 5000f);
			boolean doll = ps.dollLayers() == 0;
			boolean mending = l.getGameTime() < Matriarch.mendingUntil(p);
			p.removeAllEffects();
			p.setHealth(p.getMaxHealth());
			return "second blow takes the doll " + doll + ", mending " + mending;
		});
		check(save.equals("first blow alive true at 6 with the doll kept true") && second.equals("second blow takes the doll true, mending true"), "Nested Shell: " + save + ", " + second);
		// mending: the doll empties and fills back up over five minutes
		ctx.waitTicks(40);
		long left = ctx.computeOnClient(mc -> fr.achedon12.matriochka.client.MatriarchTip.secondsLeft());
		check(left > 250 && left <= 300, "the HUD counts the shell mending (" + left + " s left)");
		shot(ctx, "hud_mending");
		// the tooltip: the set as a checklist, the bonus in two lines, the shell's state
		s.runOnServer(server -> player(server).getInventory().setItem(0, new ItemStack(ModContent.item("matriarch_chestplate"))));
		ctx.setScreen(() -> new InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
		ctx.waitTicks(10);
		double[] slot = ctx.computeOnClient(mc -> {
			int gw = mc.getWindow().getGuiScaledWidth(), gh = mc.getWindow().getGuiScaledHeight();
			double sc = mc.getWindow().getGuiScale();
			return new double[]{((gw - 176) / 2 + 8 + 8) * sc, ((gh - 166) / 2 + 142 + 8) * sc};
		});
		ctx.getInput().setCursorPos(slot[0], slot[1]);
		ctx.waitTicks(6);
		shot(ctx, "armour_tooltip");
		ctx.setScreen(() -> null);
	}

	// ---------------------------------------------------------------- the Journal's card of a world, with its ore
	private static void journal(ClientGameTestContext ctx, net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext s) {
		int[] row = new int[1];
		ctx.setScreen(() -> {
			JournalScreen j = new JournalScreen(false).tab(3);
			j.openCard(2);
			row[0] = j.cardShow("living_ember");
			return j;
		});
		ctx.waitTicks(20);
		check(row[0] >= 0, "the Living Ember is on World 2's card (row " + row[0] + ")");
		ctx.getInput().setCursorPos(4, 4);
		ctx.waitTicks(10);
		shot(ctx, "journal_card_2");
		// World 10's card opens on the chain the Matriarch Armour is made by
		ctx.setScreen(() -> {
			JournalScreen j = new JournalScreen(false).tab(3);
			j.openCard(10);
			return j;
		});
		ctx.waitTicks(20);
		shot(ctx, "journal_card_10");
		ctx.setScreen(() -> null);
	}
}
