package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.Arenas;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Builds one procedural structure from its archetype, chunk by chunk (every placement is clipped to the chunk box). */
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

	// ---------------------------------------------------------------- palette
	private BlockState floor() { return Arenas.floorFor(world); }
	private BlockState wall() {
		return switch (world) {
			case 0 -> Blocks.STONE_BRICKS.defaultBlockState();
			case 3 -> ModContent.block("sealed_brick").defaultBlockState();
			case 6 -> ModContent.block("mirror_glass").defaultBlockState();
			case 10 -> ModContent.block("painted_wood").defaultBlockState();
			default -> ModContent.block(world == 4 ? "cloudstone" : world == 7 ? "trench_rock" : "dungeon_brick").defaultBlockState();
		};
	}
	private BlockState accent() {
		String id = switch (world) {
			case 1 -> "spore_bloom"; case 2 -> "ember_stone"; case 3 -> "cold_lamp"; case 4 -> "storm_glass"; case 5 -> "faint_glow";
			case 6 -> "prism_moss"; case 7 -> "pressure_coral"; case 8 -> "temporal_sand_block"; case 9 -> "pulse_vein"; case 10 -> "lacquer_glow";
			default -> "lacquer_block";
		};
		return ModContent.block(id).defaultBlockState();
	}
	private BlockState roof() { return world == 0 ? Blocks.DEEPSLATE_TILES.defaultBlockState() : ModContent.block("lacquer_block").defaultBlockState(); }

	// ---------------------------------------------------------------- drawing helpers (clipped)
	private WorldGenLevel lvl;
	private BoundingBox clip;
	private BlockPos o;

	private void set(int x, int y, int z, BlockState s) {
		BlockPos p = o.offset(x, y, z);
		if (clip.isInside(p)) lvl.setBlock(p, s, 2);
	}

	private void cuboid(int x0, int y0, int z0, int x1, int y1, int z1, BlockState s, boolean hollow) {
		for (int x = x0; x <= x1; x++)
			for (int y = y0; y <= y1; y++)
				for (int z = z0; z <= z1; z++) {
					boolean edge = x == x0 || x == x1 || y == y0 || y == y1 || z == z0 || z == z1;
					set(x, y, z, hollow && !edge ? Blocks.AIR.defaultBlockState() : s);
				}
	}

	private void cylinder(int r, int y0, int y1, BlockState s, boolean hollow) {
		for (int x = -r; x <= r; x++)
			for (int z = -r; z <= r; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > r + 0.5) continue;
				for (int y = y0; y <= y1; y++) set(x, y, z, hollow && d < r - 0.5 && y > y0 ? Blocks.AIR.defaultBlockState() : s);
			}
	}

	private void sphere(int r, int cy, BlockState s, boolean hollow) {
		for (int x = -r; x <= r; x++)
			for (int y = -r; y <= r; y++)
				for (int z = -r; z <= r; z++) {
					double d = Math.sqrt(x * x + y * y + z * z);
					if (d <= r + 0.3) set(x, cy + y, z, hollow && d < r - 1 ? Blocks.AIR.defaultBlockState() : s);
				}
	}

	private void foundation(int r) {
		for (int x = -r; x <= r; x++)
			for (int z = -r; z <= r; z++)
				for (int y = -1; y >= -8; y--) {
					BlockPos p = o.offset(x, y, z);
					if (!clip.isInside(p)) continue;
					BlockState st = lvl.getBlockState(p);
					if (st.isAir() || !st.getFluidState().isEmpty()) lvl.setBlock(p, floor(), 2); else break;
				}
	}

	// ---------------------------------------------------------------- build
	@Override
	public void postProcess(WorldGenLevel level, StructureManager sm, ChunkGenerator gen, RandomSource random, BoundingBox chunkBB, ChunkPos chunkPos, BlockPos ref) {
		this.lvl = level;
		this.clip = chunkBB;
		this.o = new BlockPos(boundingBox.getCenter().getX(), boundingBox.minY() + 14, boundingBox.getCenter().getZ());
		RandomSource r = RandomSource.create(seed);
		int R = radius, H = height;
		BlockState air = Blocks.AIR.defaultBlockState();
		if (world != 4 && world != 7) foundation(Math.min(R, 12));
		switch (archetype) {
			case "tower", "lighthouse", "clock" -> {
				int tr = Math.max(3, R / 2);
				cylinder(tr, 0, H, wall(), true);
				for (int y = 5; y < H; y += 5) cylinder(tr - 1, y, y, floor(), false);
				cylinder(tr + 1, H, H, roof(), false);
				if (!archetype.equals("tower")) cylinder(1, H + 1, H + 3, accent(), false);
				for (int y = 1; y < H; y++) set(0, y, 0, Blocks.LADDER.defaultBlockState());
				door(tr);
			}
			case "hive", "cocoon", "nest" -> {
				int sr = archetype.equals("nest") ? Math.max(4, R / 2) : Math.max(4, R * 2 / 3);
				sphere(sr, archetype.equals("nest") ? 0 : sr / 2, archetype.equals("hive") ? accent() : wall(), true);
				cylinder(sr - 1, 0, 0, floor(), false);
				door(sr);
			}
			case "well", "chasm" -> {
				cylinder(3, 0, 2, wall(), true);
				for (int y = -1; y >= -12; y--) cylinder(2, y, y, y < -9 ? (world == 2 ? Blocks.LAVA.defaultBlockState() : Blocks.WATER.defaultBlockState()) : air, false);
				cylinder(4, 3, 3, roof(), false);
			}
			case "temple", "cathedral", "throne" -> {
				for (int s = 0; s < 4; s++) cuboid(-R + s * 2, s * 2, -R + s * 2, R - s * 2, s * 2 + 1, R - s * 2, wall(), false);
				cuboid(-R / 2, 1, -R / 2, R / 2, H, R / 2, wall(), true);
				cuboid(-R / 2 - 1, H, -R / 2 - 1, R / 2 + 1, H, R / 2 + 1, roof(), false);
				for (int x = -R / 2 + 1; x < R / 2; x += 3) set(x, 4, -R / 2, accent());
				door(R / 2);
			}
			case "village", "camp", "market", "city" -> {
				int huts = archetype.equals("camp") ? 3 : 5;
				for (int i = 0; i < huts; i++) {
					double a = i * Math.PI * 2 / huts;
					int hx = (int) (Math.cos(a) * R * 0.6), hz = (int) (Math.sin(a) * R * 0.6);
					cuboid(hx - 2, 0, hz - 2, hx + 2, 4, hz + 2, wall(), true);
					cuboid(hx - 3, 5, hz - 3, hx + 3, 5, hz + 3, roof(), false);
					set(hx, 1, hz - 2, air);
					set(hx, 2, hz - 2, air);
					set(hx, 3, hz, accent());
				}
				set(0, 0, 0, Blocks.CAMPFIRE.defaultBlockState());
			}
			case "arena", "fort" -> {
				cylinder(R, 0, 0, floor(), false);
				for (int i = 0; i < 8; i++) {
					double a = i * Math.PI / 4;
					int px = (int) (Math.cos(a) * (R - 1)), pz = (int) (Math.sin(a) * (R - 1));
					for (int y = 1; y <= 5; y++) set(px, y, pz, wall());
					set(px, 6, pz, accent());
				}
				if (archetype.equals("fort")) {
					cylinder(R, 1, 4, wall(), true);
					for (int y = 1; y <= 3; y++) set(0, y, -R, air);
				}
			}
			case "maze", "cell", "crypt", "vault", "library", "lab" -> {
				boolean under = archetype.equals("vault") || archetype.equals("crypt");
				int yb = under ? -8 : 0;
				cuboid(-R, yb, -R, R, yb + 6, R, wall(), true);
				for (int x = -R + 4; x < R; x += 5) {
					for (int y = yb + 1; y < yb + 6; y++)
						for (int z = -R + 1; z < R; z++) if ((z + x) % 7 != 0) set(x, y, z, wall());
				}
				for (int x = -R + 2; x < R; x += 5) set(x, yb + 5, 0, accent());
				if (archetype.equals("library")) for (int z = -R + 1; z < R; z += 2) set(-R + 1, yb + 2, z, Blocks.BOOKSHELF.defaultBlockState());
				if (world == 3) set(0, yb + 1, -R, ModContent.block("sealed_door").defaultBlockState());
				if (under) for (int y = yb + 1; y <= 0; y++) set(R - 1, y, R - 1, Blocks.LADDER.defaultBlockState());
				else door(R);
			}
			case "garden", "shrine" -> {
				cylinder(R, 0, 0, floor(), false);
				for (int i = 0; i < 18; i++) {
					int x = r.nextInt(R * 2 + 1) - R, z = r.nextInt(R * 2 + 1) - R;
					if (x * x + z * z < R * R) set(x, 1, z, world == 1 ? Blocks.FERN.defaultBlockState() : Blocks.FLOWERING_AZALEA.defaultBlockState());
				}
				if (archetype.equals("garden")) cylinder(R, 1, 5, ModContent.block("mirror_glass").defaultBlockState(), true);
				cylinder(1, 1, 3, accent(), false);
			}
			case "bridge", "rail" -> {
				cuboid(-R, 0, -1, R, 0, 1, floor(), false);
				for (int x = -R; x <= R; x += 3) {
					set(x, 1, -2, wall());
					set(x, 1, 2, wall());
				}
				if (archetype.equals("rail")) for (int x = -R; x <= R; x++) set(x, 1, 0, Blocks.RAIL.defaultBlockState());
			}
			case "wreck", "bell" -> {
				for (int x = -R; x <= R; x++) {
					int w = (int) (Math.sqrt(Math.max(0, R * R - x * x)) / 2);
					cuboid(x, 0, -w, x, 3, w, Blocks.DARK_OAK_PLANKS.defaultBlockState(), false);
					cuboid(x, 1, -w + 1, x, 3, w - 1, air, false);
				}
				for (int y = 1; y < 9; y++) set(0, y, 0, Blocks.DARK_OAK_FENCE.defaultBlockState());
			}
			case "mine", "forge" -> {
				cuboid(-R / 2, -6, -R / 2, R / 2, 0, R / 2, wall(), true);
				for (int y = -5; y <= 0; y++) set(0, y, -R / 2, air);
				for (int x = -R / 2 + 1; x < R / 2; x += 3) set(x, -5, 0, archetype.equals("forge") ? Blocks.BLAST_FURNACE.defaultBlockState() : accent());
			}
			case "stair", "island" -> {
				for (int s = 0; s < H; s++) {
					double a = s * 0.6;
					int x = (int) (Math.cos(a) * 4), z = (int) (Math.sin(a) * 4);
					cuboid(x - 1, s, z - 1, x + 1, s, z + 1, floor(), false);
				}
			}
			case "sanctuary" -> {
				// Surface: the Guardian's sanctuary
				cylinder(9, 0, 0, Blocks.POLISHED_DEEPSLATE.defaultBlockState(), false);
				for (int i = 0; i < 8; i++) {
					double a = i * Math.PI / 4;
					int px = (int) (Math.cos(a) * 8), pz = (int) (Math.sin(a) * 8);
					for (int y = 1; y <= 4; y++) set(px, y, pz, Blocks.CHISELED_STONE_BRICKS.defaultBlockState());
					set(px, 5, pz, ModContent.block("lacquer_block").defaultBlockState());
				}
				set(0, 1, 0, ModContent.block("sanctuary_altar").defaultBlockState());
				cylinder(2, 0, 0, ModContent.block("painted_wood").defaultBlockState(), false);
				return;
			}
			default -> {
				for (int i = 0; i < 6; i++) {
					int x = r.nextInt(R * 2) - R, z = r.nextInt(R * 2) - R;
					cuboid(x, 0, z, x + 2, 1 + r.nextInt(4), z, wall(), false);
				}
				cylinder(R / 2, 0, 0, floor(), false);
			}
		}
		contents(level, r);
	}

	private void door(int dist) {
		for (int y = 1; y <= 2; y++) set(0, y, -dist, Blocks.AIR.defaultBlockState());
	}

	private void contents(WorldGenLevel level, RandomSource r) {
		int yb = archetype.equals("vault") || archetype.equals("crypt") ? -7 : archetype.equals("mine") || archetype.equals("forge") ? -5 : 1;
		switch (role) {
			case "combat" -> {
				spawner(level, 1, yb, 1, r);
				chest(level, -1, yb, 2, r, false, false);
			}
			case "exploration" -> {
				chest(level, 2, yb, -1, r, false, false);
				chest(level, -2, yb, 1, r, false, false);
			}
			case "story" -> {
				chest(level, 0, yb, 2, r, true, false);
				for (int x = -2; x <= 2; x++) set(x, yb + 2, 3, (x & 1) == 0 ? ModContent.block("lacquer_block").defaultBlockState() : ModContent.block("painted_wood").defaultBlockState());
			}
			case "utility" -> npc(level, r);
			case "secret" -> chest(level, 0, yb, 0, r, true, true);
			default -> {}
		}
	}

	private void spawner(WorldGenLevel level, int x, int y, int z, RandomSource r) {
		BlockPos p = o.offset(x, y, z);
		if (!clip.isInside(p)) return;
		var mobs = Content.MOBS.stream().filter(m -> m.world() == world && !m.elite()).toList();
		if (mobs.isEmpty()) return;
		level.setBlock(p, Blocks.SPAWNER.defaultBlockState(), 2);
		if (level.getBlockEntity(p) instanceof SpawnerBlockEntity sp) sp.setEntityId(ModContent.entity(mobs.get(r.nextInt(mobs.size())).id()), r);
	}

	private void chest(WorldGenLevel level, int x, int y, int z, RandomSource r, boolean page, boolean doll) {
		BlockPos p = o.offset(x, y, z);
		if (!clip.isInside(p)) return;
		level.setBlock(p, Blocks.CHEST.defaultBlockState(), 2);
		if (!(level.getBlockEntity(p) instanceof ChestBlockEntity chest)) return;
		var res = Content.ITEMS.stream().filter(i -> i.world() == world && (i.kind().equals("resource") || i.kind().equals("gem") || i.kind().equals("ingot")
			|| i.kind().equals("dust") || i.kind().equals("consumable") || i.kind().equals("food"))).toList();
		int n = 2 + r.nextInt(3);
		for (int i = 0; i < n && !res.isEmpty(); i++) {
			Defs.ItemDef d = res.get(r.nextInt(res.size()));
			chest.setItem(r.nextInt(27), new ItemStack(ModContent.item(d.id()), 1 + r.nextInt(d.rarity().equals("common") ? 6 : 2)));
		}
		if (world == 0) chest.setItem(4, new ItemStack(net.minecraft.world.item.Items.IRON_INGOT, 3 + r.nextInt(5)));
		if (page && world > 0) {
			ItemStack pg = new ItemStack(ModContent.item("journal_page"));
			CompoundTag t = new CompoundTag();
			t.putInt("world", world);
			int idx = Math.floorMod((int) (seed ^ (seed >>> 32)), 5);
			t.putInt("index", idx);
			pg.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
			pg.set(DataComponents.CUSTOM_NAME, net.minecraft.network.chat.Component.translatable("item.matriochka.journal_page.n", world, idx + 1));
			chest.setItem(13, pg);
		}
		if (doll && world > 0) chest.setItem(22, new ItemStack(ModContent.item("hidden_doll_" + world)));
	}

	private void npc(WorldGenLevel level, RandomSource r) {
		for (Defs.NpcDef d : Content.PEOPLES) {
			if (d.world() != world) continue;
			BlockPos p = o.offset(1, 1, 1);
			if (!clip.isInside(p)) return;
			var e = ModContent.entity(d.id()).create(level.getLevel(), EntitySpawnReason.STRUCTURE);
			if (e != null) {
				e.setPos(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
				if (e instanceof net.minecraft.world.entity.Mob m) m.setPersistenceRequired();
				level.addFreshEntity(e);
			}
		}
	}
}
