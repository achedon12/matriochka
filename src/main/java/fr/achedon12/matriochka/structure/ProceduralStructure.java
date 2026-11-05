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
		return onTopOfChunkCenter(context, Heightmap.Types.WORLD_SURFACE_WG, b -> {
			var cp = context.chunkPos();
			int y = context.chunkGenerator().getFirstOccupiedHeight(cp.getMiddleBlockX(), cp.getMiddleBlockZ(), Heightmap.Types.WORLD_SURFACE_WG,
				context.heightAccessor(), context.randomState());
			if (world == 4 && y <= context.heightAccessor().getMinY() + 4) y = 90;
			if (world == 7) y = Math.max(context.heightAccessor().getMinY() + 10, y);
			BlockPos pos = new BlockPos(cp.getMiddleBlockX(), y, cp.getMiddleBlockZ());
			b.addPiece(new ProceduralPiece(this, pos, context.random()));
		});
	}

	@Override
	public StructureType<?> type() {
		return TYPE;
	}
}
