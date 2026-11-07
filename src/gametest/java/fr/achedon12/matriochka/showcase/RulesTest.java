package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.Burnout;
import fr.achedon12.matriochka.rules.DungeonShift;
import fr.achedon12.matriochka.rules.GravityZones;
import fr.achedon12.matriochka.rules.PlacedBlocks;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.rules.ShiftingGround;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;

/**
 * Checks the real mechanics of worlds 3, 5, 6 and 9 in a real world: ./gradlew runClientGameTest -Prules. Each world
 * forces its mechanic (the triggers are called directly) and checks the result. Fails the run if any check fails.
 */
final class RulesTest {
	private RulesTest() {}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			McTest.waitForChunks(sp);
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamerule announce_advancements false");
			server.runCommand("execute as @p run matriochka progression set 10");
			server.runCommand("gamemode survival @a");
			ctx.waitTicks(40);
			List<String> report = new ArrayList<>();
			for (int w : new int[]{3, 5, 6, 9}) {
				server.runCommand("execute as @p run matriochka world enter " + w);
				ctx.waitTicks(100);
				final int world = w;
				report.addAll(server.computeOnServer(s -> checks(s, world)));
				ctx.waitTicks(20);
				server.runCommand("execute as @p run matriochka world leave");
				ctx.waitTicks(60);
			}
			for (String line : report) Matriochka.LOG.info("[rules] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " rule check(s) failed: " + report);
		}
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static boolean achieved(ServerPlayer p, String customKey) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) {
			if (!a.arg().equals(customKey)) continue;
			var h = p.level().getServer().getAdvancements().get(Matriochka.id(a.id()));
			return h != null && p.getAdvancements().getOrStartProgress(h).isDone();
		}
		return false;
	}

	private static List<String> checks(MinecraftServer server, int world) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		ServerLevel level = (ServerLevel) p.level();
		try {
			check(out, Worlds.number(level) == world, "world " + world + ": the player is in it (" + level.dimension().identifier() + ")");
			if (Worlds.number(level) != world) return out;
			BlockPos c = Worlds.parcelCenter(Worlds.parcelOf(p.blockPosition()));
			switch (world) {
				case 3 -> halls(out, level, p, c);
				case 5 -> lights(out, level, p, c);
				case 6 -> gravity(out, level, p, c);
				case 9 -> ground(out, level, p, c);
				default -> {}
			}
		} catch (Throwable t) {
			out.add("FAIL world " + world + ": exception " + t);
			Matriochka.LOG.error("[rules]", t);
		}
		return out;
	}

	/** Loads the chunks around a point (synchronously, on the server thread). */
	private static void load(ServerLevel level, int x, int z, int radius) {
		int cx = SectionPos.blockToSectionCoord(x), cz = SectionPos.blockToSectionCoord(z);
		for (int dx = -radius; dx <= radius; dx++) for (int dz = -radius; dz <= radius; dz++) level.getChunk(cx + dx, cz + dz);
	}

	private static void moveTo(ServerPlayer p, ServerLevel level, BlockPos at) {
		p.teleportTo(level, at.getX() + 0.5, at.getY(), at.getZ() + 0.5, Set.of(), 0f, 0f, false);
	}

	// ---------------------------------------------------------------- World 3

	private static void halls(List<String> out, ServerLevel level, ServerPlayer p, BlockPos c) {
		int x = c.getX() + 160, z = c.getZ() + 40;
		load(level, x, z, 6);
		// a free spot in the caverns
		BlockPos spot = null;
		for (int y = 20; y < 110 && spot == null; y++) {
			BlockPos q = new BlockPos(x, y, z);
			if (level.getBlockState(q).isAir() && level.getBlockState(q.above()).isAir() && level.getBlockState(q.below()).isSolid()) spot = q;
		}
		if (spot == null) spot = new BlockPos(x, 64, z);
		moveTo(p, level, spot);
		List<DungeonShift.Move> plan = DungeonShift.plan(level, p);
		check(out, !plan.isEmpty(), "world 3: hall sections picked around the player (" + plan.size() + ")");
		int changed = 0, moved = 0;
		List<DungeonShift.Move> shifted = new java.util.ArrayList<>();
		boolean playerSafe = true;
		BlockPos protectedAt = null;
		for (int i = 0; i < plan.size(); i++) {
			DungeonShift.Move m = plan.get(i);
			if (i == 0 && m.b() != null) {
				// a chest in a section keeps it in place
				protectedAt = m.a().offset(3, 0, 3);
				level.setBlock(protectedAt, Blocks.CHEST.defaultBlockState(), 3);
				boolean done = DungeonShift.perform(level, m);
				check(out, !done, "world 3: a section holding a chest does not move");
				level.setBlock(protectedAt, Blocks.AIR.defaultBlockState(), 3);
				// a block a player placed protects it too
				level.setBlock(protectedAt, Blocks.COBBLESTONE.defaultBlockState(), 3);
				PlacedBlocks.onPlaced(level, protectedAt);
				check(out, !DungeonShift.perform(level, m), "world 3: a section holding a player's block does not move");
				level.setBlock(protectedAt, Blocks.AIR.defaultBlockState(), 3);
				PlacedBlocks.anyIn(level, DungeonShift.box(m.a()));
			}
			List<BlockState> before = snapshot(level, m);
			if (DungeonShift.perform(level, m)) {
				shifted.add(m);
				moved++;
				List<BlockState> after = snapshot(level, m);
				for (int k = 0; k < before.size(); k++) if (before.get(k) != after.get(k)) changed++;
			}
		}
		// what the game does right after a shift: anyone left inside a wall is moved to a free spot
		DungeonShift.settle(level, shifted);
		playerSafe = level.noCollision(p);
		check(out, moved > 0 && changed > 0, "world 3: the halls moved (" + moved + " moves, " + changed + " blocks changed)");
		check(out, playerSafe, "world 3: the player is not inside a wall after the shift");
		DungeonShift.clearAll();
	}

	private static List<BlockState> snapshot(ServerLevel level, DungeonShift.Move m) {
		List<BlockState> out = new ArrayList<>();
		for (BlockPos o : m.b() == null ? new BlockPos[]{m.a()} : new BlockPos[]{m.a(), m.b()}) {
			for (BlockPos q : BlockPos.betweenClosed(o, o.offset(DungeonShift.SIZE - 1, DungeonShift.HEIGHT - 1, DungeonShift.SIZE - 1))) out.add(level.getBlockState(q));
		}
		return out;
	}

	// ---------------------------------------------------------------- World 5

	private static void lights(List<String> out, ServerLevel level, ServerPlayer p, BlockPos c) {
		int x = c.getX() + 120, z = c.getZ() + 30;
		load(level, x, z, 4);
		BlockPos base = new BlockPos(x, 90, z);
		// a little platform in the air, out of the way of the terrain
		for (int dx = -3; dx <= 3; dx++) for (int dz = -3; dz <= 3; dz++) {
			level.setBlock(base.offset(dx, -1, dz), Blocks.STONE.defaultBlockState(), 3);
			for (int dy = 0; dy <= 3; dy++) level.setBlock(base.offset(dx, dy, dz), Blocks.AIR.defaultBlockState(), 3);
		}
		moveTo(p, level, base);
		long now = level.getGameTime();
		BlockPos torch = base.offset(2, 0, 0), glow = base.offset(-2, 0, 0), fire = base.offset(0, 0, 2), deep = base.offset(0, 0, -2);
		level.setBlock(torch, Blocks.TORCH.defaultBlockState(), 3);
		level.setBlock(glow, Blocks.GLOWSTONE.defaultBlockState(), 3);
		level.setBlock(fire, Blocks.CAMPFIRE.defaultBlockState(), 3);
		level.setBlock(deep, ModContent.block("faint_glow").defaultBlockState(), 3);
		for (BlockPos q : new BlockPos[]{torch, glow, fire, deep}) PlacedBlocks.onPlaced(level, q);
		var marks = PlacedBlocks.marks(level, SectionPos.blockToSectionCoord(x), SectionPos.blockToSectionCoord(z));
		check(out, marks != null && marks.lights().containsKey(torch.asLong()), "world 5: a placed torch is recorded as a brought light");
		check(out, marks != null && !marks.lights().containsKey(deep.asLong()), "world 5: the Deep's own Faint Glow is not a brought light");
		Burnout.scan(level, p, now + 20);
		check(out, level.getBlockState(torch).is(Blocks.TORCH), "world 5: a fresh torch still burns");
		Burnout.scan(level, p, now + Burnout.LIFE + 1);
		check(out, !level.getBlockState(torch).is(Blocks.TORCH), "world 5: the torch burnt out after a minute (" + level.getBlockState(torch) + ")");
		boolean stick = !level.getEntitiesOfClass(ItemEntity.class, new AABB(torch).inflate(2), e -> e.getItem().is(Items.STICK)).isEmpty();
		check(out, stick, "world 5: the burnt torch left a stick");
		check(out, level.getBlockState(glow).is(ModContent.block("spent_glow")), "world 5: glowstone turned to Spent Glow");
		check(out, level.getBlockState(fire).is(Blocks.CAMPFIRE) && !level.getBlockState(fire).getValue(BlockStateProperties.LIT), "world 5: the campfire was snuffed");
		check(out, level.getBlockState(deep).is(ModContent.block("faint_glow")), "world 5: the Faint Glow still glows");
		// the Solar Lantern carries its light
		PlayerState.of(p).setFlagTime("lantern", level.getGameTime() + 2000);
		Burnout.tickGlows(server(p), q -> true);
		BlockPos at = Burnout.glowOf(p);
		check(out, at != null && level.getBlockState(at).is(Blocks.LIGHT), "world 5: a lit Solar Lantern carries a light (" + at + ")");
		PlayerState.of(p).setFlagTime("lantern", 0);
		Burnout.tickGlows(server(p), q -> true);
		check(out, Burnout.glowOf(p) == null && (at == null || !level.getBlockState(at).is(Blocks.LIGHT)), "world 5: the glow goes away with the lantern");
	}

	private static MinecraftServer server(ServerPlayer p) {
		return p.level().getServer();
	}

	// ---------------------------------------------------------------- World 6

	private static void gravity(List<String> out, ServerLevel level, ServerPlayer p, BlockPos c) {
		long t = level.getGameTime();
		long ep = GravityZones.epoch(t);
		int zx = 0, zz = 0;
		boolean found = false;
		for (int r = 4; r < 20 && !found; r++) {
			for (int i = -r; i <= r && !found; i++) {
				int ax = Math.floorDiv(c.getX(), GravityZones.ZONE) + r, az = Math.floorDiv(c.getZ(), GravityZones.ZONE) + i;
				if (GravityZones.flippedZone(level, ax, az, ep)) {
					zx = ax;
					zz = az;
					found = true;
				}
			}
		}
		check(out, found, "world 6: a flipped zone exists this epoch");
		if (!found) return;
		int x = zx * GravityZones.ZONE + GravityZones.ZONE / 2, z = zz * GravityZones.ZONE + GravityZones.ZONE / 2;
		load(level, x, z, 3);
		int ground = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
		moveTo(p, level, new BlockPos(x, ground + 4, z));
		p.setOnGround(false);
		GravityZones.tickPlayer(level, p, t);
		check(out, GravityZones.isFlipped(p) && p.getGravity() < 0, "world 6: a player in a flipped zone falls upward (gravity " + p.getGravity() + ")");
		check(out, p.hasEffect(MobEffects.LEVITATION), "world 6: the player gets an upward pull in open air");
		check(out, achieved(p, "flipped"), "world 6: Ceiling Walk granted");
		for (int i = 0; i < 205; i++) GravityZones.tickPlayer(level, p, t);
		check(out, achieved(p, "fall_up"), "world 6: Vertigo granted after 10 seconds of falling up");
		// a creature in the zone rises
		Zombie zombie = fr.achedon12.matriochka.mc.McEntities.ZOMBIE.create(level, EntitySpawnReason.COMMAND);
		zombie.setPos(x + 2.5, ground + 3, z + 2.5);
		level.addFreshEntity(zombie);
		GravityZones.tickMob(level, zombie, t);
		double y0 = zombie.getY();
		for (int i = 0; i < 10; i++) zombie.tick();
		check(out, GravityZones.isFlipped(zombie) && zombie.getY() > y0, "world 6: a zombie in the zone falls upward (" + y0 + " -> " + zombie.getY() + ")");
		zombie.discard();
		// a Stabilizer keeps the player's gravity
		PlayerState.of(p).setFlagTime("stable", t + 600);
		GravityZones.tickPlayer(level, p, t);
		check(out, !GravityZones.isFlipped(p) && p.getGravity() > 0, "world 6: the Stabilizer keeps gravity normal");
		// back to normal outside the zone
		PlayerState.of(p).setFlagTime("stable", 0);
		moveTo(p, level, c.above(2));
		GravityZones.tickPlayer(level, p, t);
		check(out, !GravityZones.isFlipped(p), "world 6: normal gravity at the Threshold");
		p.removeEffect(MobEffects.LEVITATION);
		p.removeEffect(MobEffects.SLOW_FALLING);
	}

	// ---------------------------------------------------------------- World 9

	private static void ground(List<String> out, ServerLevel level, ServerPlayer p, BlockPos c) {
		int x = c.getX() + 200, z = c.getZ() + 40;
		load(level, x, z, 7);
		int pcx = SectionPos.blockToSectionCoord(x), pcz = SectionPos.blockToSectionCoord(z);
		int[] free = null, other = null;
		for (int r = 0; r <= 5 && (free == null || other == null); r++) {
			for (int dx = -r; dx <= r; dx++) {
				for (int dz = -r; dz <= r; dz++) {
					if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
					int cx = pcx + dx, cz = pcz + dz;
					if (!ShiftingGround.movable(level, cx, cz)) continue;
					if (free == null) free = new int[]{cx, cz};
					else if (other == null && Math.max(Math.abs(cx - free[0]), Math.abs(cz - free[1])) >= 3) other = new int[]{cx, cz};
				}
			}
		}
		check(out, free != null && other != null, "world 9: two free zones found");
		if (free == null || other == null) return;
		int fx = free[0] * 16 + 8, fz = free[1] * 16 + 8;
		int top = level.getHeight(Heightmap.Types.WORLD_SURFACE, fx, fz);
		// a player's block on the zone, and the player standing on it
		BlockPos build = new BlockPos(fx + 2, level.getHeight(Heightmap.Types.WORLD_SURFACE, fx + 2, fz), fz);
		level.setBlock(build, Blocks.OAK_PLANKS.defaultBlockState(), 3);
		PlacedBlocks.onPlaced(level, build);
		moveTo(p, level, new BlockPos(fx, top, fz));
		double py = p.getY();
		boolean moved = ShiftingGround.perform(level, new ShiftingGround.Shift(free[0], free[1], ShiftingGround.Kind.RISE, 2));
		int top2 = level.getHeight(Heightmap.Types.WORLD_SURFACE, fx, fz);
		check(out, moved && top2 == top + 2, "world 9: the zone rose by 2 (" + top + " -> " + top2 + ")");
		check(out, level.getBlockState(build.above(2)).is(Blocks.OAK_PLANKS), "world 9: the player's block rode the ground");
		check(out, p.getY() >= py + 1.9, "world 9: the player rode the ground (" + py + " -> " + p.getY() + ")");
		check(out, level.noCollision(p), "world 9: the player is not inside the ground");
		check(out, achieved(p, "base_moved"), "world 9: My Base Walks granted");
		// a Terrain Anchor holds another zone
		int ox = other[0] * 16 + 8, oz = other[1] * 16 + 8;
		int otop = level.getHeight(Heightmap.Types.WORLD_SURFACE, ox, oz);
		BlockPos anchor = new BlockPos(ox + 20, level.getHeight(Heightmap.Types.WORLD_SURFACE, ox + 20, oz) + 1, oz);
		level.setBlock(anchor, ModContent.block("terrain_anchor").defaultBlockState(), 3);
		check(out, ShiftingGround.anchored(level, other[0], other[1]), "world 9: a Terrain Anchor 13 blocks away holds the zone");
		boolean movedAnchored = ShiftingGround.perform(level, new ShiftingGround.Shift(other[0], other[1], ShiftingGround.Kind.SINK, 2));
		check(out, !movedAnchored && level.getHeight(Heightmap.Types.WORLD_SURFACE, ox, oz) == otop, "world 9: the anchored zone did not move");
		level.setBlock(anchor, Blocks.AIR.defaultBlockState(), 3);
		// an Anchor used by the player holds the zone under them
		PlayerState.of(p).setFlagTime("anchor", level.getGameTime() + 600);
		check(out, ShiftingGround.anchored(level, free[0], free[1]), "world 9: an Anchor holds the zone under the player");
		PlayerState.of(p).setFlagTime("anchor", 0);
		// a slide moves the ground sideways and the player with it
		double px = p.getX();
		boolean slid = ShiftingGround.perform(level, new ShiftingGround.Shift(free[0], free[1], ShiftingGround.Kind.SLIDE_X, 1));
		check(out, slid && level.noCollision(p), "world 9: the zone slid without burying the player (x " + px + " -> " + p.getX() + ")");
	}
}
