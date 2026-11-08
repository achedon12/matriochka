package fr.achedon12.matriochka.structure;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/**
 * Builds one procedural structure from its archetype, chunk by chunk. The drawing is done by a {@link Kit} that clips
 * every placement to the chunk being generated, so each chunk replays the whole deterministic build and keeps only
 * its own blocks.
 */
public class ProceduralPiece extends StructurePiece {
	private final int world, radius, height;
	private final String archetype, role, id;
	private final long seed;

	public ProceduralPiece(ProceduralStructure s, BlockPos origin, RandomSource random) {
		super(ProceduralStructure.PIECE, 0, box(origin, s.size));
		this.world = s.world;
		this.archetype = s.archetype;
		this.role = s.role;
		this.id = s.id;
		this.radius = radius(s.size);
		this.height = height(s.size, s.archetype);
		this.seed = random.nextLong();
	}

	public ProceduralPiece(CompoundTag tag) {
		super(ProceduralStructure.PIECE, tag);
		this.world = tag.getIntOr("world", 1);
		this.archetype = tag.getStringOr("arch", "ruin");
		this.role = tag.getStringOr("role", "exploration");
		this.id = tag.getStringOr("sid", "");
		this.radius = tag.getIntOr("r", 8);
		this.height = tag.getIntOr("h", 8);
		this.seed = tag.getLongOr("seed", 0L);
	}

	private static int radius(String size) {
		return switch (size) {
			case "small" -> 6;
			case "large" -> 18;
			default -> 11;
		};
	}

	private static int height(String size, String arch) {
		int base = switch (size) { case "small" -> 7; case "large" -> 16; default -> 10; };
		if (arch.equals("tower") || arch.equals("lighthouse") || arch.equals("clock")) base *= 2;
		return base;
	}

	private static BoundingBox box(BlockPos o, String size) {
		int r = radius(size);
		return new BoundingBox(o.getX() - r - 1, o.getY() - 14, o.getZ() - r - 1, o.getX() + r + 1, o.getY() + 40, o.getZ() + r + 1);
	}

	@Override
	protected void addAdditionalSaveData(StructurePieceSerializationContext context, CompoundTag tag) {
		tag.putInt("world", world);
		tag.putString("arch", archetype);
		tag.putString("role", role);
		tag.putString("sid", id);
		tag.putInt("r", radius);
		tag.putInt("h", height);
		tag.putLong("seed", seed);
	}

	@Override
	public void postProcess(WorldGenLevel level, StructureManager sm, ChunkGenerator gen, RandomSource random, BoundingBox chunkBB, ChunkPos chunkPos, BlockPos ref) {
		BlockPos o = new BlockPos(boundingBox.getCenter().getX(), boundingBox.minY() + 14, boundingBox.getCenter().getZ());
		String size = radius <= 6 ? "small" : radius >= 18 ? "large" : "medium";
		Kit k = new Kit(level, chunkBB, boundingBox, o, seed, world, radius, height, id, role, size, archetype);
		if (!archetype.equals("sanctuary")) k.rot = Rotation.values()[(int) Math.floorMod(seed >>> 7, 4L)];
		if (world == 6 && (archetype.equals("tower") || archetype.equals("city") || archetype.equals("well"))) k.flip = true;
		if (world == 9 && !archetype.equals("vault")) {
			k.sink = 1 + (int) Math.floorMod(seed >>> 13, 3L);
			if (archetype.equals("ruin") || archetype.equals("village") || archetype.equals("tower")) k.shear = 0.08;
		}
		build(k);
		// the Guardian's sanctuary keeps no chest: its reward is the boss behind the altar
		if (!archetype.equals("sanctuary") && !role.equals("decor")) Rewards.apply(k);
		k.finish();
	}

	private static void build(Kit k) {
		switch (k.archetype) {
			case "tower" -> Towers.tower(k);
			case "lighthouse" -> Towers.lighthouse(k);
			case "clock" -> Towers.clock(k);
			case "temple" -> Halls.temple(k);
			case "cathedral" -> Halls.cathedral(k);
			case "throne" -> Halls.throne(k);
			case "library" -> Halls.library(k);
			case "lab" -> Halls.lab(k);
			case "shrine" -> Halls.shrine(k);
			case "sanctuary" -> Halls.sanctuary(k);
			case "artisan_cabin" -> Surface.workshop(k);
			case "peddler_stall" -> Surface.stall(k);
			case "fallen_doll" -> Surface.fallenDoll(k);
			case "wonder" -> Wonders.build(k);
			case "village" -> Settlements.village(k);
			case "camp" -> Settlements.camp(k);
			case "market" -> Settlements.market(k);
			case "city" -> Settlements.city(k);
			case "fort" -> Settlements.fort(k);
			case "arena" -> Settlements.arena(k);
			case "garden" -> Settlements.garden(k);
			case "bridge" -> Settlements.bridge(k);
			case "rail" -> Settlements.rail(k);
			case "stair" -> Settlements.stair(k);
			case "vault" -> Depths.vault(k);
			case "crypt" -> Depths.crypt(k);
			case "cell" -> Depths.cell(k);
			case "maze" -> Depths.maze(k);
			case "mine" -> Depths.mine(k);
			case "forge" -> Depths.forge(k);
			case "well" -> Depths.well(k);
			case "chasm" -> Depths.chasm(k);
			case "nest" -> Depths.nest(k);
			case "hive" -> Depths.hive(k);
			case "cocoon" -> Depths.cocoon(k);
			case "wreck" -> Depths.wreck(k);
			case "bell" -> Depths.bell(k);
			case "prop_spool", "prop_nail", "prop_pin", "prop_button", "prop_thimble", "prop_offcut", "prop_scissors", "prop_pencil" -> Workshop.prop(k);
			case "bastion", "circle", "outpost", "caravan" -> Outposts.build(k);
			default -> Settlements.ruin(k);
		}
	}
}
