package fr.achedon12.matriochka.structure;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import fr.achedon12.matriochka.Matriochka;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;

/** Data-driven procedural structure: one structure type, 101 structures (archetype + world palette + role). */
public class ProceduralStructure extends Structure {
	public static final MapCodec<ProceduralStructure> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
		settingsCodec(i),
		Codec.INT.fieldOf("world").forGetter(s -> s.world),
		Codec.STRING.fieldOf("archetype").forGetter(s -> s.archetype),
		Codec.STRING.fieldOf("role").forGetter(s -> s.role),
		Codec.STRING.fieldOf("size").forGetter(s -> s.size),
		Codec.STRING.fieldOf("structure_id").forGetter(s -> s.id)
	).apply(i, ProceduralStructure::new));

	public static final StructureType<ProceduralStructure> TYPE = Registry.register(BuiltInRegistries.STRUCTURE_TYPE, Matriochka.id("procedural"), () -> CODEC);
	public static final StructurePieceType PIECE = Registry.register(BuiltInRegistries.STRUCTURE_PIECE, Matriochka.id("procedural_piece"),
		(StructurePieceType.ContextlessType) ProceduralPiece::new);

	public final int world;
	public final String archetype, role, size, id;

	public ProceduralStructure(StructureSettings settings, int world, String archetype, String role, String size, String id) {
		super(settings);
		this.world = world;
		this.archetype = archetype;
		this.role = role;
		this.size = size;
		this.id = id;
	}

	public static void init() {}

	@Override
	protected Optional<GenerationStub> findGenerationPoint(GenerationContext context) {
		boolean ceiling = world == 3 || world == 5;
		if (ceiling) {
			var cp = context.chunkPos();
			int y = 30 + (int) (Math.floorMod(cp.x() * 31 + cp.z() * 17, 40));
			BlockPos pos = new BlockPos(cp.getMiddleBlockX(), y, cp.getMiddleBlockZ());
			return Optional.of(new GenerationStub(pos, b -> b.addPiece(new ProceduralPiece(this, pos, context.random()))));
		}
		if (world == 2) {
			// the Ember Veins are a cave under a rock roof that reaches the top of the world: the heightmap would stop on
			// the roof, where nothing can be built. The structures stand on the highest cave floor with room over it
			var cp = context.chunkPos();
			int x = cp.getMiddleBlockX(), z = cp.getMiddleBlockZ();
			var col = context.chunkGenerator().getBaseColumn(x, z, context.heightAccessor(), context.randomState());
			int min = context.heightAccessor().getMinY(), max = context.heightAccessor().getMaxY();
			int y = caveFloor(col, Math.max(min + 8, context.chunkGenerator().getSeaLevel() + 4), max - CAVE_HEADROOM);
			// no open floor in this column: the structure carves its own cavern in the rock, as in the ceiling worlds
			if (y < 0) y = 40 + Math.floorMod(cp.x() * 31 + cp.z() * 17, 30);
			BlockPos pos = new BlockPos(x, y, z);
			return Optional.of(new GenerationStub(pos, b -> b.addPiece(new ProceduralPiece(this, pos, context.random()))));
		}
		// the outposts, caravans, circles and bastions are land camps: over a sea or a lake they would stand on a pillar
		// of foundation rising out of the water. They skip a site whose centre or rim is under water (but World 4's
		// islands and World 7's sea floor)
		if (OUTDOOR.contains(archetype) && world != 4 && world != 7 && overWater(context)) return Optional.empty();
		// in the Pressure Ocean the ground is the sea floor: the water surface would leave the structures floating
		Heightmap.Types ground = world == 7 ? Heightmap.Types.OCEAN_FLOOR_WG : Heightmap.Types.WORLD_SURFACE_WG;
		return onTopOfChunkCenter(context, ground, b -> {
			var cp = context.chunkPos();
			int y = context.chunkGenerator().getFirstOccupiedHeight(cp.getMiddleBlockX(), cp.getMiddleBlockZ(), ground,
				context.heightAccessor(), context.randomState());
			if (world == 4 && y <= context.heightAccessor().getMinY() + 4) y = 90;
			// keep them on the floor, under the surface (a sunken lighthouse still stays under water)
			if (world == 7) y = Math.max(context.heightAccessor().getMinY() + 10, Math.min(y, fr.achedon12.matriochka.world.Ocean.SEA_LEVEL - 40));
			BlockPos pos = new BlockPos(cp.getMiddleBlockX(), y, cp.getMiddleBlockZ());
			b.addPiece(new ProceduralPiece(this, pos, context.random()));
		});
	}

	private static final java.util.Set<String> OUTDOOR = java.util.Set.of("caravan", "circle", "outpost", "bastion");

	/** True when the middle of the chunk or a point 10 blocks out lies under water. */
	private static boolean overWater(GenerationContext context) {
		var cp = context.chunkPos();
		int x = cp.getMiddleBlockX(), z = cp.getMiddleBlockZ();
		for (int[] d : new int[][]{{0, 0}, {10, 0}, {-10, 0}, {0, 10}, {0, -10}}) {
			int top = context.chunkGenerator().getFirstOccupiedHeight(x + d[0], z + d[1], Heightmap.Types.WORLD_SURFACE_WG, context.heightAccessor(), context.randomState());
			var col = context.chunkGenerator().getBaseColumn(x + d[0], z + d[1], context.heightAccessor(), context.randomState());
			if (!col.getBlock(top - 1).getFluidState().isEmpty()) return true;
		}
		return false;
	}

	/** Room kept over a cave floor for a structure (World 2). */
	private static final int CAVE_HEADROOM = 18;

	/** The highest floor of a column, between low and high, with solid rock under it and four blocks of air over it; -1 if none. */
	static int caveFloor(net.minecraft.world.level.NoiseColumn col, int low, int high) {
		for (int y = high; y > low; y--) {
			var below = col.getBlock(y - 1);
			if (below.isAir() || !below.getFluidState().isEmpty()) continue;
			boolean open = true;
			for (int dy = 0; dy <= 3 && open; dy++) open = col.getBlock(y + dy).isAir();
			if (open) return y;
		}
		return -1;
	}

	@Override
	public StructureType<?> type() {
		return TYPE;
	}
}
