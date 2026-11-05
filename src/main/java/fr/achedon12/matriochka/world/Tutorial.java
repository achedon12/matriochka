package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Blocks2;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.function.Predicate;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The first-steps guide of the design's first half hour: read the Scroll, find the Guardian's Sanctuary, wake and
 * defeat the Guardian, place the Matrix Workbench, craft the World 1 Seed, till World Soil, plant it by water, wait
 * for it to hatch and enter. Every step is detected from what really happened in the world, checked once a second;
 * a later step seen first skips the ones before it (a returning player or a group mate who did the work).
 * <p>
 * Per player, in the player state (synced to the client, which draws the card): {@code tut_step} (0..DONE),
 * {@code f_tut_read}, {@code f_tut_hide}, and the sanctuary found for the compass, {@code tut_sx}/{@code tut_sz}
 * ({@code f_tut_lost} when none was found nearby).
 */
public final class Tutorial {
	public static final String[] STEPS = {"read", "sanctuary", "wake", "defeat", "workbench", "seed", "till", "plant", "hatch", "enter"};
	public static final int DONE = STEPS.length;
	/** Close enough to the sanctuary's centre to count as found, in blocks (the sanctuary is about 40 wide). */
	private static final int FOUND_RANGE = 28;
	/** Search radius of the sanctuary, in placement cells (24 chunks each). */
	private static final int SEARCH_CELLS = 4;

	private Tutorial() {}

	public static void init() {
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (server.overworld().getGameTime() % 20 != 11) return;
			for (ServerPlayer p : server.getPlayerList().getPlayers()) tick(p);
		});
	}

	public static int step(PlayerState ps) {
		return Math.max(0, Math.min(DONE, ps.tag().getIntOr("tut_step", 0)));
	}

	/** A message from the client: the Scroll was read up to the objective, or the card hidden / shown again. */
	public static void action(ServerPlayer p, String action) {
		PlayerState ps = PlayerState.of(p);
		switch (action) {
			case "read" -> ps.set("tut_read", true);
			case "hide" -> ps.set("tut_hide", true);
			case "show" -> ps.set("tut_hide", false);
			default -> { return; }
		}
		tick(p);
		ps.sync();
	}

	public static void tick(ServerPlayer p) {
		if (p.isSpectator()) return;
		PlayerState ps = PlayerState.of(p);
		int s = step(ps);
		if (s >= DONE) return;
		int reached = s;
		for (int i = DONE - 1; i >= s; i--) {
			if (met(p, ps, i)) {
				reached = i + 1;
				break;
			}
		}
		if (reached > s) {
			ps.tag().putInt("tut_step", reached);
			s = reached;
			ps.sync();
		}
		if (s == 1 && !ps.tag().contains("tut_sx") && !ps.has("tut_lost") && p.level().dimension() == Level.OVERWORLD) {
			locate(p, ps);
			ps.sync();
		}
	}

	/** True once the action of step i (or something only possible after it) has been seen. */
	static boolean met(ServerPlayer p, PlayerState ps, int i) {
		MatrioData data = MatrioData.get(p.level().getServer());
		String group = data.groupOf(p.getUUID());
		ServerLevel level = (ServerLevel) p.level();
		return switch (STEPS[i]) {
			case "read" -> ps.has("tut_read");
			case "sanctuary" -> nearSanctuary(p, ps);
			case "wake" -> !level.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(64),
				b -> b.getType() == ModContent.entity("block_guardian")).isEmpty();
			case "defeat" -> data.defeated(group, 0);
			case "workbench" -> near(level, p.blockPosition(), 6, st -> st.is(ModContent.block("matrix_workbench")));
			case "seed" -> Stations.count(p.getInventory(), ModContent.item("seed_1")) > 0;
			case "till" -> near(level, p.blockPosition(), 6, st -> st.is(ModContent.block("world_soil_0")) && st.getValue(Blocks2.WorldSoil.TILLED));
			case "plant" -> plantedNear(level, p.blockPosition());
			case "hatch" -> data.hasWorldBlock(level.getServer(), group, 1);
			case "enter" -> Worlds.number(level) == 1 || data.defeated(group, 1);
			default -> false;
		};
	}

	private static boolean nearSanctuary(ServerPlayer p, PlayerState ps) {
		if (p.level().dimension() != Level.OVERWORLD) return false;
		if (ps.tag().contains("tut_sx")) {
			double dx = p.getX() - ps.tag().getIntOr("tut_sx", 0), dz = p.getZ() - ps.tag().getIntOr("tut_sz", 0);
			if (dx * dx + dz * dz <= FOUND_RANGE * FOUND_RANGE) return true;
		}
		// any sanctuary counts, not only the one the needle points at
		ServerLevel level = (ServerLevel) p.level();
		var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id("guardian_sanctuary")));
		return holder.isPresent() && level.structureManager().getStructureWithPieceAt(p.blockPosition(), HolderSet.direct(holder.get())).isValid();
	}

	/** Finds the nearest Guardian's Sanctuary once, for the compass (as /locate does, a few cells around the player). */
	static void locate(ServerPlayer p, PlayerState ps) {
		ServerLevel level = (ServerLevel) p.level();
		var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id("guardian_sanctuary")));
		var found = holder.isEmpty() ? null
			: level.getChunkSource().getGenerator().findNearestMapStructure(level, HolderSet.direct(holder.get()), p.blockPosition(), SEARCH_CELLS, false);
		if (found == null) {
			ps.set("tut_lost", true);
			return;
		}
		ps.tag().putInt("tut_sx", found.getFirst().getX());
		ps.tag().putInt("tut_sz", found.getFirst().getZ());
	}

	private static boolean near(ServerLevel level, BlockPos c, int r, Predicate<BlockState> test) {
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-r, -3, -r), c.offset(r, 3, r))) {
			if (test.test(level.getBlockState(q))) return true;
		}
		return false;
	}

	private static boolean plantedNear(ServerLevel level, BlockPos c) {
		for (BlockPos q : BlockPos.betweenClosed(c.offset(-8, -3, -8), c.offset(8, 3, 8))) {
			if (level.getBlockState(q).is(ModContent.block("planted_seed")) && level.getBlockEntity(q) instanceof DataBlockEntity be
				&& be.data().getIntOr("world", 0) == 1) return true;
		}
		return false;
	}
}
