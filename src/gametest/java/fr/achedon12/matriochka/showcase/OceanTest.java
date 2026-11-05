package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.Recipes;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.Snorkel;
import fr.achedon12.matriochka.world.Lairs;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Ocean;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;

/**
 * Checks the Pressure Ocean in a real world: ./gradlew runClientGameTest -Pocean. Enters World 7, checks the safe
 * arrival in the diving chamber, that the world is sea from its floor to y 240 with no dry land, that a snorkel helmet
 * drains under water and refills in air, over a vent, with a capsule and at the Abyssal Press, that hits wear it, that
 * the sea creatures swim without drowning and that the Leviathan's lair is under water. Fails on the first broken run.
 */
final class OceanTest {
	private OceanTest() {}

	/** Shared between the server steps. */
	private static BlockPos threshold, deep;

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			ctx.waitTicks(40);
			List<String> report = new ArrayList<>();
			report.addAll(server.computeOnServer(OceanTest::arrive));
			ctx.waitTicks(60);
			report.addAll(server.computeOnServer(OceanTest::afterArrival));
			report.addAll(server.computeOnServer(OceanTest::dive));
			ctx.waitTicks(120);
			report.addAll(server.computeOnServer(OceanTest::afterDive));
			ctx.waitTicks(80);
			report.addAll(server.computeOnServer(OceanTest::afterAir));
			ctx.waitTicks(80);
			report.addAll(server.computeOnServer(OceanTest::afterVent));
			ctx.waitTicks(120);
			report.addAll(server.computeOnServer(OceanTest::afterHolding));
			report.addAll(server.computeOnServer(OceanTest::creatures));
			ctx.waitTicks(100);
			report.addAll(server.computeOnServer(OceanTest::afterCreatures));
			for (String line : report) Matriochka.LOG.info("[ocean] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " ocean check(s) failed: " + report);
		}
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static ServerPlayer player(MinecraftServer server) {
		return server.getPlayerList().getPlayers().get(0);
	}

	private static ItemStack helmet(ServerPlayer p) {
		return p.getItemBySlot(EquipmentSlot.HEAD);
	}

	private static List<String> guard(MinecraftServer server, java.util.function.Function<ServerPlayer, List<String>> step) {
		try {
			return step.apply(player(server));
		} catch (Throwable t) {
			Matriochka.LOG.error("[ocean]", t);
			return List.of("FAIL exception " + t);
		}
	}

	// ---------------------------------------------------------------- arrival
	private static List<String> arrive(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			MatrioData data = MatrioData.get(server);
			for (int i = 0; i <= 6; i++) data.markDefeated(data.groupOf(p.getUUID()), i);
			p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 120, 4, true, false));
			fr.achedon12.matriochka.world.Travel.enter(p, Ocean.WORLD, p.blockPosition());
			check(out, Worlds.number(p.level()) == Ocean.WORLD, "the player is in World 7");
			ServerLevel level = (ServerLevel) p.level();
			threshold = p.blockPosition().below();
			check(out, level.getBlockState(threshold).is(ModContent.block("threshold")), "the player stands on the Threshold (" + threshold + ")");
			check(out, !p.isUnderWater() && level.getBlockState(BlockPos.containing(p.getEyePosition())).isAir(), "the player arrives in air, not in water");
			check(out, threshold.getY() >= Ocean.THRESHOLD_MIN && threshold.getY() <= Ocean.THRESHOLD_MAX, "the chamber sits on the sea floor (y " + threshold.getY() + ")");
			// the dome is closed: every cell inside is air, the shell has no water in it
			int wet = 0;
			for (BlockPos q : BlockPos.betweenClosed(threshold.offset(-4, 1, -4), threshold.offset(4, 4, 4))) {
				if (q.distSqr(threshold) < 25 && !level.getFluidState(q).isEmpty()) wet++;
			}
			check(out, wet == 0, "the diving chamber is dry inside (" + wet + " wet cells)");
			return out;
		});
	}

	private static List<String> afterArrival(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			ServerLevel level = (ServerLevel) p.level();
			check(out, p.isAlive() && !p.isUnderWater(), "three seconds later the player still breathes in the chamber");
			check(out, PlayerState.of(p).gauge("oxygen") >= 99f, "breath stays full in the chamber (" + PlayerState.of(p).gauge("oxygen") + ")");
			// the sea: water from the floor up to the surface, air above it, no dry land around
			int columns = 0, flooded = 0, land = 0;
			for (int dx = -96; dx <= 96; dx += 32) {
				for (int dz = -96; dz <= 96; dz += 32) {
					if (Math.abs(dx) < 16 && Math.abs(dz) < 16) continue;
					int x = threshold.getX() + dx, z = threshold.getZ() + dz;
					level.getChunk(x >> 4, z >> 4);
					int floor = seaFloor(level, x, z);
					if (floor >= Ocean.SEA_LEVEL) land++;
					columns++;
					int wetCells = 0, cells = 0;
					for (int y = floor; y < Ocean.SEA_LEVEL; y++) {
						cells++;
						if (level.getFluidState(new BlockPos(x, y, z)).is(FluidTags.WATER)) wetCells++;
					}
					if (cells == 0 || wetCells >= cells * 0.95) flooded++;
				}
			}
			check(out, land == 0, "no dry land in " + columns + " columns around the Threshold");
			// a structure's dry pocket may sit in one or two of the sampled columns
			check(out, flooded >= columns - 2, flooded + " / " + columns + " columns are sea from the floor to y " + Ocean.SEA_LEVEL);
			BlockPos above = new BlockPos(threshold.getX() + 40, Ocean.SEA_LEVEL + 2, threshold.getZ() + 40);
			check(out, level.getBlockState(above).isAir() && level.getFluidState(above.below(3)).is(FluidTags.WATER), "the surface is at y " + Ocean.SEA_LEVEL);
			// the Leviathan's lair: its heart sits in water at the bottom of its trench
			BlockPos heart = Lairs.heart(Ocean.WORLD, threshold.offset(0, 0, Worlds.ARENA_OFFSET));
			check(out, level.getBlockState(heart).is(ModContent.block("lair_heart")), "the lair heart is in place (" + heart + ")");
			check(out, level.getFluidState(heart.above(4)).is(FluidTags.WATER) && level.getFluidState(heart.offset(0, 4, -Lairs.GATE - 4)).is(FluidTags.WATER),
				"the temple and its forecourt are under water");
			// the station recipes: one snorkel helmet per ore of the world
			long helmets = Recipes.of("abyssal_press").stream().filter(r -> Snorkel.def(r.output()) != null).count();
			check(out, helmets == Content.SNORKELS.size() && helmets >= 3, helmets + " snorkel helmets at the Abyssal Press");
			for (Defs.SnorkelDef s : Content.SNORKELS) {
				check(out, Content.BLOCKS.stream().anyMatch(b -> b.world() == 7 && b.drop().equals(s.ore())), s.id() + " is made of an ore of the world (" + s.ore() + ")");
			}
			return out;
		});
	}

	/** The sea floor under a column: the first block that is not water, going down from the surface. */
	private static int seaFloor(ServerLevel level, int x, int z) {
		int y = Ocean.SEA_LEVEL - 1;
		while (y > level.getMinY() && level.getFluidState(new BlockPos(x, y, z)).is(FluidTags.WATER)) y--;
		return y + 1;
	}

	// ---------------------------------------------------------------- the helmet
	private static List<String> dive(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			ServerLevel level = (ServerLevel) p.level();
			// open water a little away from the chamber, well above the floor
			int x = threshold.getX() + 24, z = threshold.getZ() - 24;
			int floor = seaFloor(level, x, z);
			deep = new BlockPos(x, floor + 12, z);
			for (BlockPos q : BlockPos.betweenClosed(deep.offset(-2, -2, -2), deep.offset(2, 3, 2))) level.setBlock(q, Blocks.WATER.defaultBlockState(), 3);
			ItemStack h = new ItemStack(ModContent.item("salt_snorkel"));
			Snorkel.setTank(h, 100f);
			p.setItemSlot(EquipmentSlot.HEAD, h);
			PlayerState.of(p).setGauge("oxygen", 70f);
			p.teleportTo(level, deep.getX() + 0.5, deep.getY(), deep.getZ() + 0.5, java.util.Set.of(), 0f, 0f, false);
			p.setNoGravity(true);
			check(out, p.isUnderWater() || level.getFluidState(BlockPos.containing(p.getEyePosition())).is(FluidTags.WATER), "the player is under water at " + deep);
			return out;
		});
	}

	private static List<String> afterDive(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			ItemStack h = helmet(p);
			float tank = Snorkel.tank(h);
			check(out, Snorkel.is(h), "the helmet is still on");
			check(out, tank < 100f && tank > 60f, "the tank drains under water (" + tank + " s left of 100)");
			check(out, PlayerState.of(p).gauge("oxygen") > 90f, "the helmet tops the breath up (" + PlayerState.of(p).gauge("oxygen") + ")");
			check(out, p.getAirSupply() >= p.getMaxAirSupply() - 20, "no vanilla drowning under the helmet (" + p.getAirSupply() + ")");
			// a hit wears the helmet much faster than plain armor (vanilla: 1 point for 6 damage)
			int before = h.getDamageValue();
			p.removeEffect(MobEffects.RESISTANCE);
			p.hurtServer((ServerLevel) p.level(), p.damageSources().generic(), 6f);
			p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 120, 4, true, false));
			int worn = helmet(p).getDamageValue() - before;
			check(out, worn >= 2, "a hit of 6 wears the helmet by " + worn + " (plain armor: 1)");
			// an oxygen capsule fills half the tank
			float t0 = Snorkel.tank(helmet(p));
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("oxygen_capsule")));
			p.getItemInHand(InteractionHand.MAIN_HAND).use(p.level(), p, InteractionHand.MAIN_HAND);
			float t1 = Snorkel.tank(helmet(p));
			check(out, t1 >= Math.min(Snorkel.capacity(helmet(p)), t0 + Snorkel.capacity(helmet(p)) * 0.5f) - 1, "a capsule refills the tank (" + t0 + " -> " + t1 + ")");
			// the Abyssal Press refills it, deep under water
			BlockPos press = deep.offset(0, -2, 0);
			ServerLevel level = (ServerLevel) p.level();
			level.setBlock(press, ModContent.block("abyssal_press").defaultBlockState(), 3);
			Snorkel.setTank(helmet(p), 10f);
			String err = level.getBlockEntity(press) instanceof DataBlockEntity be ? Stations.refillSnorkel(p, level, press, be) : "no block entity";
			check(out, err == null && Snorkel.fraction(helmet(p)) >= 1f, "the Abyssal Press refills the tank (" + err + ")");
			level.setBlock(press, Blocks.WATER.defaultBlockState(), 3);
			// now into the air of the chamber with a half tank
			Snorkel.setTank(helmet(p), 60f);
			p.setNoGravity(false);
			p.teleportTo(level, threshold.getX() + 0.5, threshold.getY() + 1, threshold.getZ() + 0.5, java.util.Set.of(), 0f, 0f, false);
			return out;
		});
	}

	private static List<String> afterAir(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			float tank = Snorkel.tank(helmet(p));
			check(out, tank > 60f, "the tank refills in the chamber's air (" + tank + ")");
			// then over an air vent, under water
			ServerLevel level = (ServerLevel) p.level();
			Snorkel.setTank(helmet(p), 30f);
			level.setBlock(deep.below(2), ModContent.block("air_vent").defaultBlockState(), 3);
			p.setNoGravity(true);
			p.teleportTo(level, deep.getX() + 0.5, deep.getY(), deep.getZ() + 0.5, java.util.Set.of(), 0f, 0f, false);
			return out;
		});
	}

	private static List<String> afterVent(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			float tank = Snorkel.tank(helmet(p));
			check(out, tank > 30f, "the tank refills over an air vent (" + tank + ")");
			// without a helmet the breath runs out
			((ServerLevel) p.level()).setBlock(deep.below(2), Blocks.WATER.defaultBlockState(), 3);
			p.setItemSlot(EquipmentSlot.HEAD, ItemStack.EMPTY);
			PlayerState.of(p).setGauge("oxygen", 100f);
			return out;
		});
	}

	private static List<String> afterHolding(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			float o2 = PlayerState.of(p).gauge("oxygen");
			check(out, o2 < 90f && o2 > 60f, "without a helmet the breath drains (" + o2 + " after 6 s)");
			return out;
		});
	}

	// ---------------------------------------------------------------- creatures
	private static final List<MatrioMob> MOBS = new ArrayList<>();

	private static List<String> creatures(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			ServerLevel level = (ServerLevel) p.level();
			p.setNoGravity(false);
			p.teleportTo(level, threshold.getX() + 0.5, threshold.getY() + 1, threshold.getZ() + 0.5, java.util.Set.of(), 0f, 0f, false);
			MOBS.clear();
			int i = 0;
			for (Defs.MobDef d : Content.MOBS) {
				if (d.world() != Ocean.WORLD) continue;
				check(out, d.aquatic(), d.id() + " is a sea creature");
				if (ModContent.entity(d.id()).create(level, EntitySpawnReason.COMMAND) instanceof MatrioMob m) {
					m.setPos(deep.getX() + 0.5 + (i++ - 2) * 1.5, deep.getY(), deep.getZ() + 0.5);
					level.addFreshEntity(m);
					check(out, m.getNavigation() instanceof WaterBoundPathNavigation, d.id() + " paths through water");
					MOBS.add(m);
				}
			}
			for (Defs.CritterDef d : Content.CRITTERS) {
				var e = ModContent.entity(d.id()).create(level, EntitySpawnReason.COMMAND);
				check(out, e != null, "the wildlife " + d.id() + " exists");
				if (e != null) e.discard();
			}
			return out;
		});
	}

	private static List<String> afterCreatures(MinecraftServer server) {
		return guard(server, p -> {
			List<String> out = new ArrayList<>();
			for (MatrioMob m : MOBS) {
				check(out, m.isAlive() && m.getHealth() >= m.getMaxHealth() - 0.01f, m.def().id() + " does not drown (" + m.getHealth() + " / " + m.getMaxHealth() + ")");
				check(out, m.isInWater() && m.getY() < Ocean.SEA_LEVEL - 2, m.def().id() + " stays under water (y " + Math.round(m.getY()) + ")");
				m.discard();
			}
			return out;
		});
	}
}
