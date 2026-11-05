package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.BaseModel;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.ScaleLinks;
import fr.achedon12.matriochka.world.Variants;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;

/**
 * Checks the links between the scales, server side: world variants chosen while a Seed hatches, boss mutations,
 * the effects between the inside and the outside of a World Block, the Maquette of the base and the World 10 props.
 * Run with ./gradlew runClientGameTest -Pscale. Every check is reported; the run fails if one fails.
 */
final class ScaleTest {
	private ScaleTest() {}

	/** Where the giant spool was placed, and where the player stood when the World 10 pieces were placed. */
	private static BlockPos spoolAt = BlockPos.ZERO, placedFrom = BlockPos.ZERO;

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			server.runCommand("difficulty normal");
			ctx.waitTicks(40);
			List<String> report = new ArrayList<>(server.computeOnServer(ScaleTest::checks));
			// World 10: into the group's parcel, then the workbench and a prop are placed next to the player
			server.runCommand("execute as @p run matriochka progression set 10");
			server.runCommand("execute as @p run matriochka world enter 10");
			ctx.waitTicks(100);
			report.addAll(server.computeOnServer(ScaleTest::prepareWorkshop));
			ctx.waitTicks(100);
			report.addAll(server.computeOnServer(ScaleTest::workshop));
			for (String line : report) Matriochka.LOG.info("[scale] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " scale check(s) failed: " + report);
		}
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static void section(List<String> out, String name, Runnable r) {
		try {
			r.run();
		} catch (Throwable t) {
			out.add("FAIL " + name + ": exception " + t);
			Matriochka.LOG.error("[scale] {}", name, t);
		}
	}

	private static List<String> checks(MinecraftServer server) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		ServerLevel level = (ServerLevel) p.level();
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		data.parcel(group);
		Variants.forget();

		section(out, "variant rules", () -> {
			check(out, Variants.choose(100, -5).equals("blessed") && Variants.choose(-100, 5).equals("cursed"), "karma +100 / -100 picks the hallowed / cursed variant");
			check(out, Variants.choose(0, 2).equals("wild") && Variants.choose(0, -2).equals("calm") && Variants.choose(0, 1).equals("plain"), "the lean picks wild, calm or plain");
			check(out, Variants.mutation("wild", 6).equals(Content.WILD_MUTATION[6]) && Variants.mutation("wild", 5).isEmpty()
				&& Variants.mutation("cursed", 9).equals("hollow"), "mutations come from World 6 on");
		});

		section(out, "variant at hatching", () -> {
			// a World 6 Seed, fed two wild offerings, hatches high in the sky (its condition)
			BlockPos soil = new BlockPos(p.getBlockX() + 6, 140, p.getBlockZ());
			level.setBlock(soil, ModContent.block("world_soil_5").defaultBlockState().setValue(fr.achedon12.matriochka.block.Blocks2.WorldSoil.TILLED, true), 3);
			BlockPos seed = soil.above();
			level.setBlock(seed, ModContent.block("planted_seed").defaultBlockState(), 3);
			DataBlockEntity be = (DataBlockEntity) level.getBlockEntity(seed);
			be.data().putInt("world", 6);
			be.data().putString("owner", p.getUUID().toString());
			PlayerState.of(p).addKarma(-PlayerState.of(p).karma());
			for (int i = 0; i < 2; i++) Variants.feed(level, seed, be.data(), new ItemStack(Items.GUNPOWDER, 1), p);
			check(out, be.data().getIntOr("lean", 0) == 2, "two wild offerings lean the Seed by 2");
			be.data().putInt("t", 199);
			BlockState st = level.getBlockState(seed);
			var ticker = ((EntityBlock) st.getBlock()).getTicker(level, st, ModContent.BE_DATA);
			ticker.tick(level, seed, st, be);
			check(out, level.getBlockState(seed).is(ModContent.block("world_block")), "the Seed hatched into a World Block");
			check(out, Variants.of(data, group, 6).equals("wild"), "the wild variant is stored for the group's World 6 (" + Variants.of(data, group, 6) + ")");
			check(out, level.getBlockEntity(seed) instanceof DataBlockEntity wb && wb.data().getStringOr("variant", "").equals("wild"), "the World Block carries its variant");
			check(out, Variants.summary(data, group).getStringOr("6", "").equals("wild"), "the Journal summary lists it");
		});

		section(out, "mutation", () -> {
			ServerLevel w6 = server.getLevel(Worlds.key(6));
			BlockPos c = Worlds.parcelCenter(data.parcel(group, 6)).offset(0, 120, 40);
			w6.getChunk(c);
			Variants.forget();
			check(out, Variants.at(w6, c).id().equals("wild"), "the parcel of World 6 is wild");
			MatrioBoss boss = MatrioBoss.summon(w6, MatrioBoss.byWorld(6).id(), c, p);
			check(out, boss != null && boss.mutation().equals(Content.WILD_MUTATION[6]), "the World 6 boss woke mutated (" + (boss == null ? "none" : boss.mutation()) + ")");
			if (boss != null) {
				boss.die(w6.damageSources().generic());
				boolean scale = !w6.getEntitiesOfClass(ItemEntity.class, new AABB(c).inflate(8), e -> e.getItem().is(ModContent.item("mutated_scale"))).isEmpty();
				check(out, scale, "a mutated boss drops a Mutated Scale");
				for (ItemEntity e : w6.getEntitiesOfClass(ItemEntity.class, new AABB(c).inflate(8))) e.discard();
				boss.discard();
				data.unmarkDefeated(group, 6);
			}
			Variants.set(data, group, 6, "calm");
			MatrioBoss calm = MatrioBoss.summon(w6, MatrioBoss.byWorld(6).id(), c, p);
			check(out, calm != null && calm.mutation().isEmpty(), "a calm world's boss is not mutated");
			if (calm != null) calm.discard();
		});

		section(out, "links", () -> {
			long now = server.overworld().getGameTime();
			BlockPos b = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition().offset(-12, 0, 6)).above(2);
			// World 2 with ice around: the heat inside is halved
			level.setBlock(b, ModContent.block("world_block").defaultBlockState(), 3);
			for (BlockPos q : new BlockPos[] {b.east(), b.west(), b.north()}) level.setBlock(q, Blocks.PACKED_ICE.defaultBlockState(), 3);
			ScaleLinks.link(level, b, data, group, 2, now);
			check(out, ScaleLinks.active(data, group, 2, "cool", now), "ice around a World 2 block cools the veins inside");
			// World 3 with a redstone signal: the sealed doors open by hand
			level.setBlock(b.east(), Blocks.REDSTONE_BLOCK.defaultBlockState(), 3);
			ScaleLinks.link(level, b, data, group, 3, now);
			check(out, ScaleLinks.active(data, group, 3, "unlocked", now), "a redstone signal on a World 3 block unlocks its doors");
			// World 7 leaks: dry farmland around it is soaked
			BlockPos farm = b.offset(2, -1, 2);
			level.setBlock(farm, Blocks.FARMLAND.defaultBlockState(), 3);
			ScaleLinks.link(level, b, data, group, 7, now);
			check(out, level.getBlockState(farm).getValue(BlockStateProperties.MOISTURE) == 7, "a World 7 block leaks onto the farmland");
			// World 9 with a Terrain Anchor around: its ground holds still
			level.setBlock(b.west(), ModContent.block("terrain_anchor").defaultBlockState(), 3);
			ScaleLinks.link(level, b, data, group, 9, now);
			check(out, ScaleLinks.active(data, group, 9, "calm", now), "a Terrain Anchor around a World 9 block calms its ground");
			// moving a World Block makes its world quake
			data.setWorldBlock(group, 4, level, b);
			data.setWorldBlock(group, 4, level, b.above(3));
			check(out, ScaleLinks.active(data, group, 4, "quake", now), "moving a World Block shakes the world inside");
			data.clearWorldBlock(group, 4, b.above(3));
			for (BlockPos q : new BlockPos[] {b, b.east(), b.west(), b.north(), farm}) level.setBlock(q, Blocks.AIR.defaultBlockState(), 3);
		});

		section(out, "maquette", () -> {
			// a little stone hut, sampled at a quarter scale and built again far above
			BlockPos base = p.blockPosition().offset(0, 60, -30);
			for (int x = -6; x <= 6; x++) for (int y = 0; y <= 8; y++) for (int z = -6; z <= 6; z++) {
				boolean wall = Math.abs(x) == 6 || Math.abs(z) == 6 || y == 0 || y == 8;
				level.setBlock(base.offset(x, y, z), wall ? Blocks.STONE_BRICKS.defaultBlockState() : Blocks.AIR.defaultBlockState(), 2);
			}
			var model = BaseModel.sample(level, base.above(4));
			int cells = 0;
			for (int v : model.getIntArray("cells").orElse(new int[0])) if (v > 0) cells++;
			check(out, cells > 0 && model.getListOrEmpty("palette").size() >= 1, "the base is sampled into a model (" + cells + " cells)");
			BlockPos origin = base.offset(0, 30, 0);
			int placed = BaseModel.build(level, origin, model);
			BlockPos c = BaseModel.corner(origin);
			boolean bricks = false;
			for (BlockPos q : BlockPos.betweenClosed(c, c.offset(BaseModel.SX - 1, BaseModel.SY - 1, BaseModel.SZ - 1))) if (level.getBlockState(q).is(Blocks.STONE_BRICKS)) bricks = true;
			check(out, placed == cells && bricks, "the model is built with real blocks (" + placed + ")");
		});
		return out;
	}

	/** Places the Titanic Workbench and a giant spool next to the player in World 10. */
	private static List<String> prepareWorkshop(MinecraftServer server) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		check(out, Worlds.number(p.level()) == 10, "the player is in World 10");
		ServerLevel w10 = (ServerLevel) p.level();
		placedFrom = p.blockPosition();
		for (String[] s : new String[][] {{"titanic_workbench", "40"}, {"giant_spool", "-40"}}) {
			int x = p.getBlockX() + Integer.parseInt(s[1]), z = p.getBlockZ() + 40;
			int y = w10.getHeight(Heightmap.Types.WORLD_SURFACE, x, z);
			var src = server.createCommandSourceStack().withLevel(w10).withPosition(new net.minecraft.world.phys.Vec3(x, y, z)).withSuppressedOutput();
			if (s[0].equals("giant_spool")) spoolAt = new BlockPos(x, y, z);
			int r;
			try {
				r = server.getCommands().getDispatcher().execute("place structure matriochka:" + s[0] + " " + x + " " + y + " " + z, src);
			} catch (Exception e) {
				r = -1;
				Matriochka.LOG.warn("[scale] place {} failed: {}", s[0], e.getMessage());
			}
			check(out, r > 0, s[0] + " placed in World 10");
		}
		return out;
	}

	private static List<String> workshop(MinecraftServer server) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		ServerLevel w10 = (ServerLevel) p.level();
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		section(out, "workbench", () -> {
			var reg = w10.registryAccess().lookupOrThrow(Registries.STRUCTURE);
			var holder = reg.get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(BaseModel.STRUCTURE))).orElseThrow();
			BlockPos near = placedFrom.offset(40, 0, 40);
			var start = w10.structureManager().getStructureAt(w10.getHeightmapPos(Heightmap.Types.WORLD_SURFACE, near), holder.value());
			if (!start.isValid()) {
				// the structure snaps to its chunk: look in the chunks around
				for (int dx = -32; dx <= 32 && !start.isValid(); dx += 8)
					for (int dz = -32; dz <= 32 && !start.isValid(); dz += 8)
						start = w10.structureManager().getStructureAt(w10.getHeightmapPos(Heightmap.Types.WORLD_SURFACE, near.offset(dx, 0, dz)), holder.value());
			}
			check(out, start.isValid(), "the Titanic Workbench stands in World 10");
			if (!start.isValid()) return;
			BlockPos origin = BaseModel.origin(start.getPieces().getFirst().getBoundingBox());
			p.teleportTo(w10, origin.getX() + 0.5, origin.getY() + 2, origin.getZ() + 0.5, java.util.Set.of(), 0f, 0f, false);
			data.worldEntry(group, 10).remove("model_at");
			BaseModel.tick(p);
			check(out, data.worldEntry(group, 10).getLongOr("model_at", 0L) == origin.asLong(), "the Maquette was set on this workbench");
			BlockPos c = BaseModel.corner(origin);
			int blocks = 0;
			for (BlockPos q : BlockPos.betweenClosed(c, c.offset(BaseModel.SX - 1, BaseModel.SY - 1, BaseModel.SZ - 1))) if (!w10.getBlockState(q).isAir()) blocks++;
			check(out, blocks > 0, "the Maquette stands on the board (" + blocks + " blocks)");
			check(out, w10.getBlockState(c.offset(-1, -1, -1)).is(Blocks.GOLD_BLOCK) || w10.getBlockState(c.offset(BaseModel.SX, -1, BaseModel.SZ)).is(Blocks.GOLD_BLOCK),
				"the board is framed in gold at the top of the bench");
		});
		section(out, "props", () -> {
			int wool = 0;
			for (BlockPos q : BlockPos.betweenClosed(spoolAt.offset(-28, -16, -28), spoolAt.offset(28, 24, 28))) {
				if (w10.isLoaded(q) && w10.getBlockState(q).is(net.minecraft.tags.BlockTags.WOOL)) {
					wool++;
					if (wool > 20) break;
				}
			}
			check(out, wool > 20, "a giant spool wound with thread lies on the workshop floor");
		});
		return out;
	}
}
