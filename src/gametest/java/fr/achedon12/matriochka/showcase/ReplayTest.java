package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.item.ReplayGear;
import fr.achedon12.matriochka.item.ReplayProjectile;
import fr.achedon12.matriochka.replay.Talents;
import fr.achedon12.matriochka.replay.Trials;
import fr.achedon12.matriochka.replay.WorldEvents;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.zombie.Husk;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * Checks the replay content in a real world: ./gradlew runClientGameTest -Preplay. The trials (start, clock, record,
 * rewards), the three world events, the new structures, a talent bought and applied, and every new weapon. Anything
 * that ticks is given real game ticks. Fails the run when a check fails.
 */
final class ReplayTest {
	private ReplayTest() {}

	private static final List<String> OUT = new ArrayList<>();
	private static final List<Entity> SPAWNED = new ArrayList<>();
	private static long clockA;
	private static int soulsBefore, doneBefore;

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule advance_weather false");
			// rain puts out the fire the javelin's lightning lights, which the check reads once the bolt is gone
			server.runCommand("weather clear");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("gamemode survival @a");
			server.runCommand("difficulty normal");
			ctx.waitTicks(40);

			// ---- talents and gear, on the Surface
			server.runOnServer(ReplayTest::talents);
			ctx.waitTicks(30);
			server.runOnServer(ReplayTest::talentsApplied);
			server.runOnServer(ReplayTest::meleeGear);
			// a struck creature shrugs off blows for half a second: the flail's three blows come a real swing apart
			for (int blow = 1; blow < 3; blow++) {
				ctx.waitTicks(12);
				server.runOnServer(ReplayTest::flailBlow);
			}
			server.runOnServer(ReplayTest::whipBlow);
			ctx.waitTicks(4);
			server.runOnServer(ReplayTest::meleeChecked);
			server.runOnServer(ReplayTest::throwJavelin);
			ctx.waitTicks(60);
			server.runOnServer(ReplayTest::javelinBack);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::shootSporeBow);
			ctx.waitTicks(30);
			server.runOnServer(ReplayTest::sporeCloud);
			server.runOnServer(ReplayTest::raiseShield);
			ctx.waitTicks(12);
			server.runOnServer(ReplayTest::shieldFlare);
			server.runOnServer(ReplayTest::quakePick);
			ctx.waitTicks(4);
			server.runOnServer(ReplayTest::clearSpawned);

			// ---- the World 1 trial, fought for real: every stage is cleared by the test, the clock runs on game ticks
			server.runOnServer(ReplayTest::startTrial);
			ctx.waitTicks(130);
			server.runOnServer(ReplayTest::trialRunning);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::trialClock);
			for (int stage = 0; stage < 3; stage++) {
				server.runOnServer(ReplayTest::clearStage);
				ctx.waitTicks(stage < 2 ? 90 : 30);
			}
			server.runOnServer(ReplayTest::trialRecorded);
			ctx.waitTicks(120);
			server.runOnServer(ReplayTest::trialHome);

			// ---- World 1: the events and the new structures
			server.runCommand("execute as @p run matriochka progression set 1");
			server.runCommand("execute as @p run matriochka world enter 1");
			ctx.waitTicks(120);
			server.runOnServer(ReplayTest::startInvasion);
			ctx.waitTicks(30);
			for (int wave = 0; wave < ReplayContent.INVASION_WAVES; wave++) {
				server.runOnServer(ReplayTest::clearInvasion);
				ctx.waitTicks(30);
			}
			server.runOnServer(ReplayTest::invasionWon);
			server.runOnServer(ReplayTest::startSurge);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::surgeLive);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::surgeOver);
			server.runOnServer(ReplayTest::startMerchant);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::merchantGone);
			// "place structure" wants every chunk under the structure loaded: hold the sites loaded first
			server.runOnServer(ReplayTest::loadStructureSites);
			ctx.waitTicks(40);
			server.runOnServer(ReplayTest::placeStructures);
			ctx.waitTicks(20);
			server.runOnServer(ReplayTest::structuresBuilt);

			for (String line : OUT) Matriochka.LOG.info("[replay] {}", line);
			long failed = OUT.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " replay check(s) failed: " + OUT);
		}
	}

	// ---------------------------------------------------------------- helpers
	private static void check(boolean ok, String what) {
		OUT.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static ServerPlayer player(MinecraftServer server) {
		return server.getPlayerList().getPlayers().get(0);
	}

	private static void section(String name, Runnable r) {
		try {
			r.run();
		} catch (Throwable t) {
			OUT.add("FAIL " + name + ": exception " + t);
			Matriochka.LOG.error("[replay] {}", name, t);
		}
	}

	/**
	 * A still zombie at an offset from the player, on the ground at the player's level (the clearing's floor): the
	 * column's top can be a tree trunk or a ledge high over the clearing, out of reach of what is checked.
	 */
	private static Husk dummy(ServerPlayer p, double dx, double dz) {
		ServerLevel level = (ServerLevel) p.level();
		Husk z = net.minecraft.world.entity.EntityTypes.HUSK.create(level, EntitySpawnReason.COMMAND);
		BlockPos at = BlockPos.containing(p.getX() + dx, p.getY(), p.getZ() + dz);
		while (!level.getBlockState(at).isAir() && at.getY() < level.getMaxY()) at = at.above();
		while (level.getBlockState(at.below()).isAir() && at.getY() > level.getMinY()) at = at.below();
		z.setPos(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
		z.setNoAi(true);
		z.setPersistenceRequired();
		level.addFreshEntity(z);
		SPAWNED.add(z);
		return z;
	}

	/** A flat clearing around the player, so throws and arrows meet nothing on the way. */
	private static void clearing(ServerPlayer p) {
		ServerLevel level = (ServerLevel) p.level();
		BlockPos c = p.blockPosition();
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-12, 0, -12), c.offset(12, 6, 12))) level.setBlock(q, Blocks.AIR.defaultBlockState(), 2);
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-12, -1, -12), c.offset(12, -1, 12))) level.setBlock(q, Blocks.STONE.defaultBlockState(), 2);
		p.teleportTo(level, c.getX() + 0.5, c.getY(), c.getZ() + 0.5, java.util.Set.of(), 0f, 0f, true);
	}

	// ---------------------------------------------------------------- talents
	private static void talents(MinecraftServer server) {
		section("talents", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			clearing(p);
			MatrioData data = MatrioData.get(server);
			String group = data.groupOf(p.getUUID());
			for (int w = 0; w <= 10; w++) data.markDefeated(group, w);
			PlayerState ps = PlayerState.of(p);
			ps.addSouls(2000);
			p.getInventory().add(new ItemStack(ModContent.item("shell_shard"), 16));
			check(Talents.learn(p, "guardian_stout") != null, "a talent is refused away from a Class Table");
			level.setBlock(p.blockPosition().offset(2, 0, 0), ModContent.block("class_table").defaultBlockState(), 3);
			check(Talents.learn(p, "guardian_unbroken") != null, "a talent is refused before the one above it");
			int souls = ps.souls();
			check(Talents.learn(p, "guardian_stout") == null, "Stout is learnt at the Class Table");
			check(Talents.learnt(ps, "guardian_stout") && ps.souls() == souls - Talents.def("guardian_stout").souls(), "Stout is stored on the player and its souls are spent");
			check(Talents.learn(p, "berserker_heavy_hand") == null, "Heavy Hand is learnt too");
			// a Guardian chestplate wakes the Guardian's talents, not the Berserker's
			ItemStack chest = new ItemStack(ModContent.item("chitin_chestplate"));
			GearClasses.apply(chest, new GearClasses.Gear("guardian", 1, 0));
			p.setItemSlot(EquipmentSlot.CHEST, chest);
		});
	}

	private static void talentsApplied(MinecraftServer server) {
		section("talents applied", () -> {
			ServerPlayer p = player(server);
			var armor = p.getAttribute(Attributes.ARMOR).getModifier(Matriochka.id("talent_armor"));
			check(armor != null && armor.amount() == 1.0, "Stout adds one armor while Guardian gear is worn (" + (armor == null ? "none" : armor.amount()) + ")");
			check(p.getAttribute(Attributes.ATTACK_DAMAGE).getModifier(Matriochka.id("talent_damage")) == null, "Heavy Hand sleeps without Berserker gear");
			PlayerState ps = PlayerState.of(p);
			int souls = ps.souls();
			check(Talents.reset(p) == null && !Talents.learnt(ps, "guardian_stout") && ps.souls() > souls, "forgetting the talents gives souls back");
			check(Talents.learn(p, "guardian_stout") == null, "Stout is learnt again");
		});
	}

	// ---------------------------------------------------------------- melee gear
	private static Husk flailA, flailB, whipped;

	private static void meleeGear(MinecraftServer server) {
		section("melee gear", () -> {
			ServerPlayer p = player(server);
			flailA = dummy(p, 0, 2);
			flailB = dummy(p, 1.2, 2.5);
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("magma_flail")));
			flailBlow(server);
		});
	}

	/** One blow of the Magma Flail on the first dummy, kept alive for the next. */
	private static void flailBlow(MinecraftServer server) {
		section("flail blow", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			flailA.setHealth(flailA.getMaxHealth());
			check(flailA.hurtServer(level, level.damageSources().playerAttack(p), 2f), "a Magma Flail blow lands");
		});
	}

	private static void whipBlow(MinecraftServer server) {
		section("whip", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			whipped = dummy(p, -6, 0);
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("key_chain_whip")));
			whipped.hurtServer(level, level.damageSources().playerAttack(p), 1f);
		});
	}

	private static void meleeChecked(MinecraftServer server) {
		section("melee checked", () -> {
			ServerPlayer p = player(server);
			check(flailA.getRemainingFireTicks() > 0, "the Magma Flail sets its target ablaze");
			check(flailB.getRemainingFireTicks() > 0, "its third blow bursts into a ring of flame");
			check(whipped.hasEffect(MobEffects.SLOWNESS), "the Key Chain Whip slows what it lashes");
			Vec3 toPlayer = p.position().subtract(whipped.position()).normalize();
			check(whipped.getDeltaMovement().dot(toPlayer) > 0.2 || whipped.distanceTo(p) < 5.5, "the whip drags its target toward the player");
			double reach = p.getAttributeValue(Attributes.ENTITY_INTERACTION_RANGE);
			check(reach > 5, "the whip reaches farther (" + reach + ")");
		});
	}

	// ---------------------------------------------------------------- thrown gear
	private static Husk javelinTarget;

	private static void throwJavelin(MinecraftServer server) {
		section("javelin", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			// the melee dummies stand between the player and the target: out of the way first
			for (Entity e : SPAWNED) e.discard();
			SPAWNED.clear();
			javelinTarget = dummy(p, 0, 7);
			p.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, javelinTarget.position().add(0, 1, 0));
			p.getInventory().clearContent();
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("storm_javelin")));
			p.getItemInHand(InteractionHand.MAIN_HAND).use(level, p, InteractionHand.MAIN_HAND);
			check(p.getMainHandItem().isEmpty(), "the Storm Javelin leaves the hand when thrown");
			check(!level.getEntitiesOfClass(ReplayProjectile.class, p.getBoundingBox().inflate(6)).isEmpty(), "a thrown javelin flies");
		});
	}

	private static void javelinBack(MinecraftServer server) {
		section("javelin back", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			boolean back = fr.achedon12.matriochka.block.Stations.count(p.getInventory(), ModContent.item("storm_javelin")) > 0;
			check(back, "the javelin flies back to its thrower");
			check(javelinTarget.getHealth() < javelinTarget.getMaxHealth() || !javelinTarget.isAlive(), "the javelin hurt its target");
			check(!level.getEntitiesOfClass(net.minecraft.world.entity.LightningBolt.class, p.getBoundingBox().inflate(16)).isEmpty() || javelinTarget.getRemainingFireTicks() > 0 || !javelinTarget.isAlive(),
				"lightning fell where it struck");
			// the harpoon pulls its catch home
			Husk fish = dummy(p, 0, -7);
			p.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, fish.position().add(0, 1, 0));
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("tide_harpoon")));
			p.getItemInHand(InteractionHand.MAIN_HAND).use(level, p, InteractionHand.MAIN_HAND);
			check(p.getMainHandItem().isEmpty(), "the Tide Harpoon is thrown");
			harpooned = fish;
		});
	}

	private static Husk harpooned;

	// ---------------------------------------------------------------- the spore bow
	private static void shootSporeBow(MinecraftServer server) {
		section("spore bow", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(fr.achedon12.matriochka.block.Stations.count(p.getInventory(), ModContent.item("tide_harpoon")) > 0, "the harpoon came back");
			check(harpooned.getHealth() < harpooned.getMaxHealth() || !harpooned.isAlive(), "the harpoon struck its catch");
			ItemStack bow = new ItemStack(ModContent.item("spore_bow"));
			p.setItemInHand(InteractionHand.MAIN_HAND, bow);
			p.getInventory().add(new ItemStack(Items.ARROW, 8));
			p.setXRot(60f);
			bow.releaseUsing(level, p, bow.getUseDuration(p) - 30);
			check(level.getEntitiesOfClass(net.minecraft.world.entity.projectile.arrow.AbstractArrow.class, p.getBoundingBox().inflate(8),
				a -> a.entityTags().contains("matriochka_spore")).size() > 0, "the Spore Bow looses a spore arrow");
		});
	}

	private static void sporeCloud(MinecraftServer server) {
		section("spore cloud", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(!level.getEntitiesOfClass(AreaEffectCloud.class, p.getBoundingBox().inflate(24)).isEmpty(), "a spore cloud bursts where the arrow lands");
		});
	}

	// ---------------------------------------------------------------- the lantern shield
	private static Husk striker;

	private static void raiseShield(MinecraftServer server) {
		section("shield", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			striker = dummy(p, 0, 2);
			p.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, striker.position().add(0, 1.5, 0));
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("lantern_shield")));
			p.getItemInHand(InteractionHand.MAIN_HAND).use(level, p, InteractionHand.MAIN_HAND);
		});
	}

	private static void shieldFlare(MinecraftServer server) {
		section("shield flare", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(p.isBlocking(), "the Lantern Shield is raised");
			p.hurtServer(level, level.damageSources().mobAttack(striker), 4f);
			check(striker.hasEffect(MobEffects.BLINDNESS) && striker.hasEffect(MobEffects.GLOWING), "a blocked blow flares: the attacker is blinded and marked");
			p.stopUsingItem();
		});
	}

	// ---------------------------------------------------------------- the quake pick
	private static void quakePick(MinecraftServer server) {
		section("quake pick", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			BlockPos col = p.blockPosition().offset(3, 0, 3);
			for (int y = 0; y < 3; y++) level.setBlock(col.above(y), Blocks.STONE.defaultBlockState(), 3);
			ItemStack pick = new ItemStack(ModContent.item("quake_pick"));
			p.setItemInHand(InteractionHand.MAIN_HAND, pick);
			p.gameMode.destroyBlock(col.above());
			check(level.getBlockState(col).isAir() && level.getBlockState(col.above(2)).isAir(), "the Quake Pick mines a column of three");
			Husk z = dummy(p, -2, 2);
			ReplayGear.tremor(level, p, p.blockPosition().below());
			check(z.hasEffect(MobEffects.SLOWNESS), "its tremor staggers the creatures around");
		});
	}

	private static void clearSpawned(MinecraftServer server) {
		for (Entity e : SPAWNED) e.discard();
		SPAWNED.clear();
		ServerPlayer p = player(server);
		p.getInventory().clearContent();
		p.setHealth(p.getMaxHealth());
	}

	// ---------------------------------------------------------------- the trial
	private static void startTrial(MinecraftServer server) {
		section("trial start", () -> {
			ServerPlayer p = player(server);
			PlayerState ps = PlayerState.of(p);
			check(Trials.start(p, "w1") != null, "the Trials stay shut before an ending");
			ps.set("end_seal", true);
			String err = Trials.start(p, "w1");
			check(err == null, "the World 1 trial begins (" + err + ")");
			check(p.level().dimension() == Worlds.REFUGE, "the player stands on the trial stage");
			soulsBefore = ps.souls();
			MatrioData data = MatrioData.get(server);
			doneBefore = data.group(data.groupOf(p.getUUID())).getIntOr("done", 0);
		});
	}

	private static void trialRunning(MinecraftServer server) {
		section("trial running", () -> {
			ServerPlayer p = player(server);
			var t = PlayerState.of(p).tag().getCompoundOrEmpty("trial");
			check(t.getStringOr("phase", "").equals("fight"), "the countdown ends and the fight begins (" + t.getStringOr("phase", "") + ")");
			check(!Trials.foes(p).isEmpty(), "the first wave stands on the stage (" + Trials.foes(p).size() + ")");
			clockA = t.getLongOr("elapsed", 0L);
		});
	}

	private static void trialClock(MinecraftServer server) {
		section("trial clock", () -> {
			long b = PlayerState.of(player(server)).tag().getCompoundOrEmpty("trial").getLongOr("elapsed", 0L);
			check(b > clockA && b - clockA >= 20, "the clock runs on game ticks (" + clockA + " then " + b + ")");
		});
	}

	private static void clearStage(MinecraftServer server) {
		section("trial stage", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			List<Entity> foes = Trials.foes(p);
			boolean boss = foes.stream().anyMatch(e -> e instanceof MatrioBoss);
			if (boss) {
				MatrioBoss b = (MatrioBoss) foes.stream().filter(e -> e instanceof MatrioBoss).findFirst().get();
				check(!b.mutation().isEmpty() && b.getMaxHealth() > MatrioBoss.byWorld(1).hp(), "the trial boss is stronger and mutated (" + b.mutation() + ", " + b.getMaxHealth() + ")");
			}
			for (Entity e : foes) {
				if (e instanceof LivingEntity le) le.die(level.damageSources().playerAttack(p));
				e.discard();
			}
			OUT.add("info cleared " + foes.size() + " foe(s)" + (boss ? " with the boss" : ""));
		});
	}

	private static void trialRecorded(MinecraftServer server) {
		section("trial recorded", () -> {
			ServerPlayer p = player(server);
			PlayerState ps = PlayerState.of(p);
			int best = ps.tag().getIntOr("trial_best_w1", 0);
			check(best > 0, "the player's best time is kept (" + best + " ticks)");
			MatrioData data = MatrioData.get(server);
			int group = data.group(data.groupOf(p.getUUID())).getCompoundOrEmpty("trial_best").getIntOr("w1", 0);
			check(group == best, "the group's best time is kept (" + group + ")");
			check(!data.root().getCompoundOrEmpty("trials").getListOrEmpty("w1").isEmpty(), "the server board lists the run");
			check(!Trials.top(server, "w1").isEmpty(), "the board command has a line");
			check(fr.achedon12.matriochka.block.Stations.count(p.getInventory(), ModContent.item("trophy_doll_1")) == 1, "the first clear gives the trophy doll");
			check(ps.has("title_" + Trials.def("w1").title()), "and the World 1 title");
			check(ps.souls() > soulsBefore, "a clear pays souls");
			check(data.group(data.groupOf(p.getUUID())).getIntOr("done", 0) == doneBefore, "the trial boss changed no progression");
		});
	}

	private static void trialHome(MinecraftServer server) {
		section("trial home", () -> {
			ServerPlayer p = player(server);
			check(p.level().dimension() != Worlds.REFUGE, "the player is carried home after the trial");
			check(!PlayerState.of(p).tag().contains("trial"), "the clock is gone from the HUD state");
		});
	}

	// ---------------------------------------------------------------- events
	private static void startInvasion(MinecraftServer server) {
		section("invasion", () -> {
			ServerPlayer p = player(server);
			check(Worlds.number(p.level()) == 1, "the player is in World 1");
			clearing(p);
			check(WorldEvents.start(p, WorldEvents.INVASION), "an invasion is announced");
			check(WorldEvents.current(p).equals("invasion:warning"), "it begins with a warning");
			WorldEvents.hurry(p);
			soulsBefore = PlayerState.of(p).souls();
		});
	}

	private static void clearInvasion(MinecraftServer server) {
		section("invasion wave", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			List<Entity> foes = WorldEvents.foes(p);
			boolean warlord = foes.stream().anyMatch(e -> e.entityTags().contains(WorldEvents.TAG + "_warlord"));
			OUT.add("info invasion wave of " + foes.size() + (warlord ? " led by a warlord" : ""));
			if (warlord) check(true, "the last wave is led by a warlord");
			for (Entity e : foes) {
				if (e instanceof LivingEntity le) le.die(level.damageSources().playerAttack(p));
				e.discard();
			}
		});
	}

	private static void invasionWon(MinecraftServer server) {
		section("invasion won", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(WorldEvents.current(p).isEmpty(), "the invasion is over (" + WorldEvents.current(p) + ")");
			BlockPos chest = WorldEvents.lastChest(p);
			check(chest != null && level.getBlockEntity(chest) instanceof ChestBlockEntity c && !c.isEmpty(), "a reward chest stands where it ended (" + chest + ")");
			check(PlayerState.of(p).souls() > soulsBefore, "beating it pays souls");
		});
	}

	private static void startSurge(MinecraftServer server) {
		section("surge", () -> {
			ServerPlayer p = player(server);
			check(WorldEvents.start(p, WorldEvents.SURGE), "a surge is announced");
			check(WorldEvents.surge(p) == 1f, "the rule is still plain during the warning");
			WorldEvents.hurry(p);
		});
	}

	private static void surgeLive(MinecraftServer server) {
		section("surge live", () -> {
			ServerPlayer p = player(server);
			check(WorldEvents.surge(p) == ReplayContent.SURGE_STRENGTH, "the surge doubles the World 1 rule (" + WorldEvents.surge(p) + ")");
			soulsBefore = PlayerState.of(p).souls();
			WorldEvents.hurry(p);
		});
	}

	private static void surgeOver(MinecraftServer server) {
		section("surge over", () -> {
			ServerPlayer p = player(server);
			check(WorldEvents.surge(p) == 1f && WorldEvents.current(p).isEmpty(), "the surge passes");
			check(PlayerState.of(p).souls() >= soulsBefore + ReplayContent.SURGE_SOULS, "weathering it pays souls");
		});
	}

	private static void startMerchant(MinecraftServer server) {
		section("merchant", () -> {
			ServerPlayer p = player(server);
			// the quiet spell after an event is skipped here: the checks start each event by hand
			check(WorldEvents.start(p, WorldEvents.MERCHANT), "a travelling merchant comes by");
			ServerLevel level = (ServerLevel) p.level();
			var npcs = level.getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(24), n -> n.entityTags().contains(WorldEvents.MERCHANT_TAG));
			check(npcs.size() == 1, "the merchant stands near the player");
			boolean bow = !npcs.isEmpty() && npcs.getFirst().getOffers().stream().anyMatch(o -> o.getResult().is(ModContent.item("spore_bow")));
			check(bow, "it sells the world's new gear");
			WorldEvents.hurry(p);
		});
	}

	private static void merchantGone(MinecraftServer server) {
		section("merchant gone", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			check(level.getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(24), n -> n.entityTags().contains(WorldEvents.MERCHANT_TAG)).isEmpty(), "the merchant moves on");
		});
	}

	// ---------------------------------------------------------------- structures
	private static final List<BlockPos> PLACED = new ArrayList<>();
	private static final List<net.minecraft.world.level.ChunkPos> FORCED = new ArrayList<>();

	/** Where each new structure goes: ten sites, south of the player in World 1. */
	private static List<BlockPos> sites(ServerPlayer p) {
		List<BlockPos> out = new ArrayList<>();
		for (int i = 0; i < 10; i++) out.add(new BlockPos(p.getBlockX() + (i % 4 - 2) * 40 + 20, 0, p.getBlockZ() + (i / 4 - 1) * 48 + 60));
		return out;
	}

	private static void loadStructureSites(MinecraftServer server) {
		section("structure sites", () -> {
			ServerLevel level = (ServerLevel) player(server).level();
			for (BlockPos at : sites(player(server))) {
				for (int cx = (at.getX() >> 4) - 2; cx <= (at.getX() >> 4) + 2; cx++)
					for (int cz = (at.getZ() >> 4) - 2; cz <= (at.getZ() >> 4) + 2; cz++) {
						if (level.setChunkForced(cx, cz, true)) FORCED.add(new net.minecraft.world.level.ChunkPos(cx, cz));
					}
			}
		});
	}

	private static void placeStructures(MinecraftServer server) {
		section("structures", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			int i = 0;
			for (var s : fr.achedon12.matriochka.content.Content.STRUCTURES) {
				if (!List.of("caravan", "circle", "outpost", "bastion").contains(s.archetype())) continue;
				int x = sites(p).get(i).getX(), z = sites(p).get(i).getZ();
				int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
				var src = server.createCommandSourceStack().withLevel(level).withPosition(new Vec3(x, y, z)).withSuppressedOutput();
				int r;
				try {
					r = server.getCommands().getDispatcher().execute("place structure matriochka:" + s.id() + " " + x + " " + y + " " + z, src);
				} catch (Exception e) {
					r = -1;
					Matriochka.LOG.warn("[replay] place {} failed: {}", s.id(), e.getMessage());
				}
				check(r > 0, s.id() + " (" + s.archetype() + ", World " + s.world() + ") places");
				PLACED.add(new BlockPos(x, y, z));
				i++;
			}
			check(i == 10, "ten new structures, one per world (" + i + ")");
		});
	}

	private static void structuresBuilt(MinecraftServer server) {
		section("structures built", () -> {
			ServerPlayer p = player(server);
			ServerLevel level = (ServerLevel) p.level();
			int withChest = 0;
			// the ceiling worlds' structures sit in the rock below the surface: look through the whole height
			for (BlockPos at : PLACED) {
				boolean chest = false;
				for (int cx = (at.getX() - 26) >> 4; cx <= (at.getX() + 26) >> 4 && !chest; cx++)
					for (int cz = (at.getZ() - 26) >> 4; cz <= (at.getZ() + 26) >> 4 && !chest; cz++)
						for (var be : level.getChunk(cx, cz).getBlockEntities().values()) {
							if (be instanceof ChestBlockEntity && Math.abs(be.getBlockPos().getX() - at.getX()) <= 26 && Math.abs(be.getBlockPos().getZ() - at.getZ()) <= 26) {
								chest = true;
								break;
							}
						}
				if (chest) withChest++;
			}
			check(withChest == PLACED.size(), "every new structure holds loot (" + withChest + "/" + PLACED.size() + ")");
			for (var c : FORCED) level.setChunkForced(c.x(), c.z(), false);
			FORCED.clear();
		});
	}
}
