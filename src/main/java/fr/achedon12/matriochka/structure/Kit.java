package fr.achedon12.matriochka.structure;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.AmethystClusterBlock;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.level.block.CrossCollisionBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.MultifaceBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SeaPickleBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.VineBlock;
import net.minecraft.world.level.block.WallBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.AttachFace;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.block.state.properties.BellAttachType;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DoubleBlockHalf;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/**
 * Building vocabulary for the procedural structures. Builders work in local coordinates around the structure origin
 * (floor at y = 0, entrance towards -z); the kit applies the piece's rotation, the Upside Realm flip and the Restless
 * Ground sink and lean, and clips every placement to the chunk being generated and to the piece box. All randomness
 * is either drawn from the piece seed in a fixed order or hashed from the local position, so every chunk rebuilds
 * exactly the same structure.
 */
public final class Kit {
	public final WorldGenLevel lvl;
	private final BoundingBox clip, box;
	public final BlockPos o;
	public final Palette p;
	public final RandomSource r;
	public final long seed;
	public final int world, R, H;
	public final String id, role, size, archetype;
	/** Stable per-structure number from the structure id: drives the variants of an archetype. */
	public final int variant;

	public Rotation rot = Rotation.NONE;
	public boolean flip;
	public int flipY, sink;
	public double shear;

	private final List<BlockPos> shapes = new ArrayList<>();

	/** A reward anchor, captured in world space when the builder marks it. */
	public record Mark(BlockPos pos, Direction facing, boolean flipped) {}

	public Mark guard, reading, secret, npc;
	public final List<Mark> hidden = new ArrayList<>();
	public final List<Mark> spawners = new ArrayList<>();

	public Kit(WorldGenLevel lvl, BoundingBox clip, BoundingBox box, BlockPos o, long seed, int world, int R, int H,
			String id, String role, String size, String archetype) {
		this.lvl = lvl;
		this.clip = clip;
		this.box = box;
		this.o = o;
		this.seed = seed;
		this.r = RandomSource.create(seed);
		this.world = world;
		this.R = R;
		this.H = H;
		this.id = id;
		this.role = role;
		this.size = size;
		this.archetype = archetype;
		this.variant = Math.floorMod(id.hashCode() * 31 + world, 9973);
		this.p = Palette.of(world);
	}

	public boolean large() { return size.equals("large"); }
	public boolean small() { return size.equals("small"); }
	public boolean combat() { return role.equals("combat"); }
	/** 0 small, 1 medium, 2 large. */
	public int scale() { return small() ? 0 : large() ? 2 : 1; }

	// ---------------------------------------------------------------- randomness
	public int ri(int lo, int hi) { return hi <= lo ? lo : lo + r.nextInt(hi - lo + 1); }
	public boolean coin(double pr) { return r.nextDouble() < pr; }
	public <T> T pick(T[] a) { return a[r.nextInt(a.length)]; }

	public long hash(int x, int y, int z, int salt) {
		long h = seed ^ (x * 0x9E3779B97F4A7C15L) ^ (y * 0xC2B2AE3D27D4EB4FL) ^ (z * 0x165667B19E3779F9L) ^ (salt * 0x27D4EB2F165667C5L);
		h ^= h >>> 33;
		h *= 0xFF51AFD7ED558CCDL;
		h ^= h >>> 33;
		h *= 0xC4CEB9FE1A85EC53L;
		h ^= h >>> 33;
		return h;
	}

	/** Position-hashed chance: independent from the order of placement, so chunk-safe. */
	public boolean hc(int x, int y, int z, int salt, double pr) {
		return (hash(x, y, z, salt) >>> 11) * 0x1.0p-53 < pr;
	}

	public int hi(int x, int y, int z, int salt, int n) {
		return (int) Math.floorMod(hash(x, y, z, salt), (long) n);
	}

	// ---------------------------------------------------------------- transform and placement
	public BlockPos at(int x, int y, int z) {
		int rx, rz;
		switch (rot) {
			case CLOCKWISE_90 -> { rx = -z; rz = x; }
			case CLOCKWISE_180 -> { rx = -x; rz = -z; }
			case COUNTERCLOCKWISE_90 -> { rx = z; rz = -x; }
			default -> { rx = x; rz = z; }
		}
		int ry = flip ? flipY - y : y;
		ry -= sink + (int) Math.floor((rx + R + 1) * shear);
		return o.offset(rx, ry, rz);
	}

	public Direction dir(Direction local) {
		if (local.getAxis() == Direction.Axis.Y) return flip ? local.getOpposite() : local;
		return rot.rotate(local);
	}

	public BlockState orient(BlockState s) {
		if (rot != Rotation.NONE) s = s.rotate(rot);
		if (flip) s = flipState(s);
		return s;
	}

	/** Kept for callers that prepare a state before {@link #put}; waterlogging itself is decided in put. */
	BlockState wet(BlockState s) {
		return s;
	}

	static BlockState flipState(BlockState s) {
		if (s.hasProperty(BlockStateProperties.HALF)) s = s.setValue(BlockStateProperties.HALF, s.getValue(BlockStateProperties.HALF) == Half.TOP ? Half.BOTTOM : Half.TOP);
		if (s.hasProperty(BlockStateProperties.SLAB_TYPE)) {
			SlabType t = s.getValue(BlockStateProperties.SLAB_TYPE);
			if (t != SlabType.DOUBLE) s = s.setValue(BlockStateProperties.SLAB_TYPE, t == SlabType.TOP ? SlabType.BOTTOM : SlabType.TOP);
		}
		if (s.hasProperty(BlockStateProperties.HANGING)) s = s.setValue(BlockStateProperties.HANGING, !s.getValue(BlockStateProperties.HANGING));
		if (s.hasProperty(BlockStateProperties.FACING)) {
			Direction d = s.getValue(BlockStateProperties.FACING);
			if (d.getAxis() == Direction.Axis.Y) s = s.setValue(BlockStateProperties.FACING, d.getOpposite());
		}
		if (s.hasProperty(BlockStateProperties.VERTICAL_DIRECTION)) s = s.setValue(BlockStateProperties.VERTICAL_DIRECTION, s.getValue(BlockStateProperties.VERTICAL_DIRECTION).getOpposite());
		if (s.hasProperty(BlockStateProperties.DOUBLE_BLOCK_HALF)) {
			DoubleBlockHalf h = s.getValue(BlockStateProperties.DOUBLE_BLOCK_HALF);
			s = s.setValue(BlockStateProperties.DOUBLE_BLOCK_HALF, h == DoubleBlockHalf.UPPER ? DoubleBlockHalf.LOWER : DoubleBlockHalf.UPPER);
		}
		if (s.hasProperty(BlockStateProperties.ATTACH_FACE)) {
			AttachFace f = s.getValue(BlockStateProperties.ATTACH_FACE);
			if (f != AttachFace.WALL) s = s.setValue(BlockStateProperties.ATTACH_FACE, f == AttachFace.FLOOR ? AttachFace.CEILING : AttachFace.FLOOR);
		}
		if (s.hasProperty(BlockStateProperties.BELL_ATTACHMENT)) {
			BellAttachType b = s.getValue(BlockStateProperties.BELL_ATTACHMENT);
			if (b == BellAttachType.FLOOR) s = s.setValue(BlockStateProperties.BELL_ATTACHMENT, BellAttachType.CEILING);
			else if (b == BellAttachType.CEILING) s = s.setValue(BlockStateProperties.BELL_ATTACHMENT, BellAttachType.FLOOR);
		}
		return s;
	}

	public boolean inside(BlockPos pos) {
		return clip.isInside(pos) && box.isInside(pos);
	}

	/** Places an already oriented state at a world position. */
	public boolean put(BlockPos pos, BlockState s) {
		if (!inside(pos)) return false;
		// under water, shaped blocks take the water they replace, so dry pockets (domes, bells, grottoes) stay dry
		if (p.underwater && s.hasProperty(BlockStateProperties.WATERLOGGED))
			s = s.setValue(BlockStateProperties.WATERLOGGED, lvl.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER));
		lvl.setBlock(pos, s, 2);
		Block b = s.getBlock();
		if (b instanceof CrossCollisionBlock || b instanceof WallBlock || b instanceof StairBlock) shapes.add(pos.immutable());
		return true;
	}

	public boolean set(int x, int y, int z, BlockState s) {
		return put(at(x, y, z), orient(s));
	}

	/** Empties a cell: air, or water in the Pressure Ocean. */
	public void air(int x, int y, int z) {
		put(at(x, y, z), p.fill);
	}

	public void air(int x0, int y0, int z0, int x1, int y1, int z1) {
		box(x0, y0, z0, x1, y1, z1, p.fill);
	}

	/** True air even under water (habitats, air pockets). */
	public void dry(int x0, int y0, int z0, int x1, int y1, int z1) {
		box(x0, y0, z0, x1, y1, z1, Blocks.AIR.defaultBlockState());
	}

	public BlockState get(int x, int y, int z) {
		BlockPos pos = at(x, y, z);
		return inside(pos) ? lvl.getBlockState(pos) : null;
	}

	public boolean solidAt(int x, int y, int z) {
		BlockState s = get(x, y, z);
		return s != null && s.isSolid();
	}

	public boolean emptyAt(int x, int y, int z) {
		BlockState s = get(x, y, z);
		return s != null && (s.isAir() || s.is(Blocks.WATER));
	}

	public void mark(String what, int x, int y, int z, Direction f) {
		Mark m = new Mark(at(x, y, z), dir(f), flip);
		switch (what) {
			case "guard" -> guard = m;
			case "reading" -> reading = m;
			case "secret" -> secret = m;
			case "npc" -> npc = m;
			case "spawner" -> spawners.add(m);
			default -> hidden.add(m);
		}
	}

	/** Fixes fence, pane, wall and stair connections once the chunk is built. */
	public void finish() {
		for (BlockPos pos : shapes) {
			BlockState s = lvl.getBlockState(pos);
			BlockState n = Block.updateFromNeighbourShapes(s, lvl, pos);
			if (n != s && !n.isAir()) lvl.setBlock(pos, n, 2);
		}
		shapes.clear();
	}

	// ---------------------------------------------------------------- state helpers
	public static BlockState facing(BlockState s, Direction d) {
		if (s.hasProperty(BlockStateProperties.HORIZONTAL_FACING) && d.getAxis() != Direction.Axis.Y) return s.setValue(BlockStateProperties.HORIZONTAL_FACING, d);
		if (s.hasProperty(BlockStateProperties.FACING)) return s.setValue(BlockStateProperties.FACING, d);
		return s;
	}

	public static BlockState axis(BlockState s, Direction.Axis a) {
		return s.hasProperty(RotatedPillarBlock.AXIS) ? s.setValue(RotatedPillarBlock.AXIS, a) : s;
	}

	public static BlockState stairOf(BlockState s, Direction f, boolean top) {
		if (!s.hasProperty(StairBlock.FACING)) return s;
		return s.setValue(StairBlock.FACING, f).setValue(StairBlock.HALF, top ? Half.TOP : Half.BOTTOM);
	}

	public static BlockState slabOf(BlockState s, boolean top) {
		return s.hasProperty(SlabBlock.TYPE) ? s.setValue(SlabBlock.TYPE, top ? SlabType.TOP : SlabType.BOTTOM) : s;
	}

	public static BlockState b(Block block) {
		return block.defaultBlockState();
	}

	// ---------------------------------------------------------------- volumes
	public void box(int x0, int y0, int z0, int x1, int y1, int z1, BlockState s) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++)
			for (int y = Math.min(y0, y1); y <= Math.max(y0, y1); y++)
				for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) set(x, y, z, s);
	}

	/** Hollow box: solid faces, emptied inside. */
	public void shell(int x0, int y0, int z0, int x1, int y1, int z1, BlockState s) {
		for (int x = x0; x <= x1; x++)
			for (int y = y0; y <= y1; y++)
				for (int z = z0; z <= z1; z++) {
					boolean edge = x == x0 || x == x1 || y == y0 || y == y1 || z == z0 || z == z1;
					if (edge) set(x, y, z, s); else air(x, y, z);
				}
	}

	public void disc(int cx, int y, int cz, double rad, BlockState s) {
		int ir = (int) Math.ceil(rad);
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) if (x * x + z * z <= rad * rad + rad) set(cx + x, y, cz + z, s);
	}

	public void ring(int cx, int y, int cz, double rad, BlockState s) {
		int ir = (int) Math.ceil(rad) + 1;
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad - 0.5 && d <= rad + 0.5) set(cx + x, y, cz + z, s);
			}
	}

	public boolean onRing(int x, int z, double rad) {
		double d = Math.sqrt(x * x + z * z);
		return d > rad - 0.5 && d <= rad + 0.5;
	}

	public void cyl(int cx, int cz, double rad, int y0, int y1, BlockState s) {
		for (int y = y0; y <= y1; y++) disc(cx, y, cz, rad, s);
	}

	/** Round tower body: ring walls, emptied inside. */
	public void tube(int cx, int cz, double rad, int y0, int y1, BlockState s) {
		int ir = (int) Math.ceil(rad) + 1;
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad + 0.5) continue;
				for (int y = y0; y <= y1; y++) {
					if (d > rad - 0.5) set(cx + x, y, cz + z, s); else air(cx + x, y, cz + z);
				}
			}
	}

	public void ellipsoid(int cx, int cy, int cz, double rx, double ry, double rz, BlockState s, double shell) {
		int ix = (int) Math.ceil(rx), iy = (int) Math.ceil(ry), iz = (int) Math.ceil(rz);
		for (int x = -ix; x <= ix; x++)
			for (int y = -iy; y <= iy; y++)
				for (int z = -iz; z <= iz; z++) {
					double d = Math.sqrt((x * x) / (rx * rx) + (y * y) / (ry * ry) + (z * z) / (rz * rz));
					if (d > 1.0) continue;
					double inner = 1.0 - shell / Math.min(rx, Math.min(ry, rz));
					if (shell > 0 && d < inner) air(cx + x, cy + y, cz + z); else set(cx + x, cy + y, cz + z, s);
				}
	}

	// ---------------------------------------------------------------- shapes
	public void stair(int x, int y, int z, BlockState base, Direction f, boolean top) {
		set(x, y, z, stairOf(base, f, top));
	}

	public void stair(int x, int y, int z, Direction f, boolean top) {
		stair(x, y, z, p.stair, f, top);
	}

	public void slab(int x, int y, int z, BlockState base, boolean top) {
		set(x, y, z, slabOf(base, top));
	}

	public void slab(int x, int y, int z, boolean top) {
		slab(x, y, z, p.slab, top);
	}

	/** Direction pointing from (x,z) towards the closer axis of the origin, used to face stairs inwards. */
	public static Direction inward(int x, int z) {
		if (Math.abs(x) >= Math.abs(z)) return x > 0 ? Direction.WEST : Direction.EAST;
		return z > 0 ? Direction.NORTH : Direction.SOUTH;
	}

	// ---------------------------------------------------------------- architecture
	/**
	 * A straight wall run from (x0,z0) to (x1,z1) (axis-aligned), rows y0..y0+h-1: a trim plinth, a body with a frieze
	 * band under the top, pilasters every {@code bay} blocks standing proud on the {@code out} side with a stair base
	 * and a capital, a cornice of upside-down stairs on top, and windows centred between pilasters.
	 */
	public void wallRun(int x0, int z0, int x1, int z1, int y0, int h, Direction out, int bay, int window) {
		int dx = Integer.signum(x1 - x0), dz = Integer.signum(z1 - z0);
		int len = Math.max(Math.abs(x1 - x0), Math.abs(z1 - z0));
		int ox = out.getStepX(), oz = out.getStepZ();
		Direction in = out.getOpposite();
		for (int i = 0; i <= len; i++) {
			int x = x0 + dx * i, z = z0 + dz * i;
			boolean pil = bay > 0 && (i % bay == 0);
			boolean mid = bay > 1 && (i % bay == bay / 2) && i > 0 && i < len;
			for (int k = 0; k < h; k++) {
				int y = y0 + k;
				BlockState s = k == 0 ? p.trim : (k == h - 1 ? p.alt : p.base);
				if (pil) s = k == 0 ? p.trim : k == h - 1 ? p.cap : p.pillar;
				if (!pil && window > 0 && mid && k >= 2 && k < 2 + window && k < h - 1) s = p.pane;
				set(x, y, z, s);
			}
			if (!pil && window > 0 && mid && h > 3) {
				stair(x + ox, y0 + 1, z + oz, in, true);
				set(x, y0 + 2 + Math.min(window, h - 3), z, p.trim);
			}
			if (pil && h > 3) {
				stair(x + ox, y0, z + oz, in, false);
				for (int k = 1; k < h - 1; k++) set(x + ox, y0 + k, z + oz, p.pillar);
				set(x + ox, y0 + h - 1, z + oz, p.cap);
			}
			stair(x + ox, y0 + h, z + oz, in, true);
			set(x, y0 + h, z, p.trim);
		}
	}

	/** Rectangular room: patterned floor, emptied inside, four wall runs, flat ceiling of {@code ceil}. */
	public void room(int x0, int z0, int x1, int z1, int y0, int h, int bay, int window, BlockState ceil) {
		floor(x0, z0, x1, z1, y0, variant % 4);
		air(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y0 + h, z1 - 1);
		wallRun(x0, z0, x1, z0, y0, h, Direction.NORTH, bay, window);
		wallRun(x0, z1, x1, z1, y0, h, Direction.SOUTH, bay, window);
		wallRun(x0, z0, x0, z1, y0, h, Direction.WEST, bay, window);
		wallRun(x1, z0, x1, z1, y0, h, Direction.EAST, bay, window);
		for (int[] c : new int[][] {{x0, z0}, {x1, z0}, {x0, z1}, {x1, z1}}) {
			for (int y = y0; y < y0 + h; y++) set(c[0], y, c[1], y == y0 ? p.trim : p.pillar);
			set(c[0], y0 + h, c[1], p.cap);
		}
		if (ceil != null) box(x0 + 1, y0 + h, z0 + 1, x1 - 1, y0 + h, z1 - 1, ceil);
	}

	/** Patterned floor: 0 checker, 1 border and cross, 2 concentric rings, 3 stripes. */
	public void floor(int x0, int z0, int x1, int z1, int y, int style) {
		int cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
		for (int x = x0; x <= x1; x++)
			for (int z = z0; z <= z1; z++) {
				boolean border = x == x0 + 1 || x == x1 - 1 || z == z0 + 1 || z == z1 - 1;
				BlockState s = switch (style) {
					case 0 -> ((x + z) & 1) == 0 ? p.floor : p.inlay;
					case 1 -> border ? p.inlay : (x == cx || z == cz) ? p.inlay2 : p.floor;
					case 2 -> {
						int d = Math.max(Math.abs(x - cx), Math.abs(z - cz));
						yield d % 3 == 0 ? p.inlay : d % 3 == 1 ? p.floor : p.trim;
					}
					default -> (x - x0) % 4 == 0 ? p.inlay : ((z - z0) % 6 == 0 ? p.inlay2 : p.floor);
				};
				set(x, y, z, s);
			}
	}

	/** Round patterned floor centred on (cx, cz). */
	public void roundFloor(int cx, int y, int cz, double rad) {
		int ir = (int) Math.ceil(rad);
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad + 0.5) continue;
				int ring = (int) Math.round(d);
				BlockState s = ring % 4 == 0 ? p.inlay : ring % 4 == 2 ? p.trim : p.floor;
				if (ring > 1 && (x == 0 || z == 0 || Math.abs(x) == Math.abs(z)) && ring % 4 != 0) s = p.inlay2;
				set(cx + x, y, cz + z, s);
			}
	}

	/** Column: trim base, shaft, capital; a fat column also gets stairs around its foot and head. */
	public void pillar(int x, int y, int z, int h, boolean fat) {
		set(x, y, z, p.trim);
		for (int k = 1; k < h - 1; k++) set(x, y + k, z, p.pillar);
		set(x, y + h - 1, z, p.cap);
		if (fat) {
			for (Direction d : Direction.Plane.HORIZONTAL) {
				stair(x + d.getStepX(), y, z + d.getStepZ(), d.getOpposite(), false);
				stair(x + d.getStepX(), y + h - 1, z + d.getStepZ(), d.getOpposite(), true);
			}
		}
	}

	/**
	 * Gable roof whose ridge runs along X (alongX) or Z, over the walls x0..x1 / z0..z1 at height y, with one block of
	 * overhang. Gable ends are filled with {@code gableFill}. Returns the ridge height.
	 */
	public int gable(int x0, int z0, int x1, int z1, int y, boolean alongX, BlockState gableFill) {
		int a0 = alongX ? z0 - 1 : x0 - 1, a1 = alongX ? z1 + 1 : x1 + 1;
		int b0 = alongX ? x0 - 1 : z0 - 1, b1 = alongX ? x1 + 1 : z1 + 1;
		int i = 0;
		while (a0 + i <= a1 - i) {
			int lo = a0 + i, hiC = a1 - i, yy = y + i;
			for (int bb = b0; bb <= b1; bb++) {
				if (lo == hiC) {
					setAB(alongX, bb, yy, lo, p.roof);
					setAB(alongX, bb, yy + 1, lo, slabOf(p.roofSlab, false));
				} else {
					setAB(alongX, bb, yy, lo, stairOf(p.roofStair, alongX ? Direction.SOUTH : Direction.EAST, false));
					setAB(alongX, bb, yy, hiC, stairOf(p.roofStair, alongX ? Direction.NORTH : Direction.WEST, false));
					if (i > 0) {
						setAB(alongX, bb, yy - 1, lo, stairOf(p.roofStair, alongX ? Direction.NORTH : Direction.WEST, true));
						setAB(alongX, bb, yy - 1, hiC, stairOf(p.roofStair, alongX ? Direction.SOUTH : Direction.EAST, true));
					}
				}
				boolean end = bb == b0 + 1 || bb == b1 - 1;
				for (int c = lo + 1; c < hiC; c++) {
					if (end && gableFill != null) setAB(alongX, bb, yy, c, gableFill);
					else if (bb > b0 + 1 && bb < b1 - 1) setAB(alongX, bb, yy, c, p.fill);
				}
			}
			i++;
		}
		return y + i;
	}

	private void setAB(boolean alongX, int along, int y, int across, BlockState s) {
		if (alongX) set(along, y, across, s); else set(across, y, along, s);
	}

	/** Hipped roof (pyramid when square) over x0..x1 / z0..z1 at height y, with overhang. Returns the top height. */
	public int hip(int x0, int z0, int x1, int z1, int y, int overhang) {
		int i = 0;
		while (true) {
			int ax = x0 - overhang + i, bx = x1 + overhang - i, az = z0 - overhang + i, bz = z1 + overhang - i;
			if (ax > bx || az > bz) break;
			int yy = y + i;
			if (ax == bx || az == bz) {
				box(ax, yy, az, bx, yy, bz, p.roof);
				box(ax, yy + 1, az, bx, yy + 1, bz, slabOf(p.roofSlab, false));
				return yy + 1;
			}
			for (int x = ax; x <= bx; x++) {
				stair(x, yy, az, p.roofStair, Direction.SOUTH, false);
				stair(x, yy, bz, p.roofStair, Direction.NORTH, false);
			}
			for (int z = az + 1; z < bz; z++) {
				stair(ax, yy, z, p.roofStair, Direction.EAST, false);
				stair(bx, yy, z, p.roofStair, Direction.WEST, false);
			}
			if (i == 0) {
				for (int x = ax + 1; x < bx; x++) {
					stair(x, yy - 1, az, p.roofStair, Direction.NORTH, true);
					stair(x, yy - 1, bz, p.roofStair, Direction.SOUTH, true);
				}
			}
			i++;
		}
		return y + i;
	}

	/** Conical spire over a round tower of radius rad, from height y; returns the tip height. */
	public int cone(int cx, int y, int cz, double rad, double steep) {
		int layers = (int) Math.ceil(rad * steep) + 1;
		for (int k = 0; k < layers; k++) {
			double rr = rad + 1 - k / steep;
			if (rr < 0.6) {
				set(cx, y + k, cz, p.roof);
				return y + k;
			}
			int ir = (int) Math.ceil(rr) + 1;
			for (int x = -ir; x <= ir; x++)
				for (int z = -ir; z <= ir; z++) {
					double d = Math.sqrt(x * x + z * z);
					if (d > rr + 0.5) continue;
					if (d > rr - 0.6) stair(cx + x, y + k, cz + z, p.roofStair, inward(x, z), false);
					else if (d > rr - 1.6) set(cx + x, y + k, cz + z, p.roof);
				}
		}
		return y + layers;
	}

	/** Hemispherical dome of {@code s}, with a band of the accent at its foot. */
	public void dome(int cx, int y, int cz, double rad, BlockState s) {
		int ir = (int) Math.ceil(rad);
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++)
				for (int k = 0; k <= ir; k++) {
					double d = Math.sqrt(x * x + z * z + k * k);
					if (d > rad + 0.5) continue;
					if (d > rad - 0.7) set(cx + x, y + k, cz + z, k == 0 ? p.trim : s);
					else air(cx + x, y + k, cz + z);
				}
		set(cx, y + ir + 1, cz, p.cap);
	}

	/** Semicircular arch spanning a0..a1 along X (alongX) or Z at plane c, springing from height y. */
	public void arch(int a0, int a1, int y, int c, boolean alongX, int thick) {
		double mid = (a0 + a1) / 2.0, rad = (a1 - a0) / 2.0;
		int top = y + (int) Math.ceil(rad) + 1;
		for (int a = a0; a <= a1; a++) {
			double dd = Math.abs(a - mid);
			int curve = y + (int) Math.floor(Math.sqrt(Math.max(0, rad * rad - dd * dd)));
			for (int t = 0; t < thick; t++) {
				int cc = c + t;
				for (int yy = y; yy <= top; yy++) {
					if (yy < curve) setAB(alongX, a, yy, cc, p.fill);
					else if (yy == curve && a != a0 && a != a1 && dd > 0.6) {
						Direction toward = a < mid ? (alongX ? Direction.WEST : Direction.NORTH) : (alongX ? Direction.EAST : Direction.SOUTH);
						setAB(alongX, a, yy, cc, stairOf(p.stair, toward, true));
					} else setAB(alongX, a, yy, cc, yy == top ? p.trim : p.base);
				}
			}
		}
	}

	/** Doorway opening of width w (odd) and height h in a wall facing {@code out}, centred at (x, z); frame and step. */
	public void doorway(int x, int y, int z, Direction out, int w, int h) {
		Direction side = out.getClockWise();
		int half = w / 2;
		for (int s = -half; s <= half; s++)
			for (int k = 0; k < h; k++) air(x + side.getStepX() * s, y + k, z + side.getStepZ() * s);
		for (int s = -half - 1; s <= half + 1; s++) set(x + side.getStepX() * s, y + h, z + side.getStepZ() * s, p.trim);
		for (int k = 0; k < h; k++) {
			set(x + side.getStepX() * (half + 1), y + k, z + side.getStepZ() * (half + 1), p.pillar);
			set(x - side.getStepX() * (half + 1), y + k, z - side.getStepZ() * (half + 1), p.pillar);
		}
		if (w >= 3) {
			stair(x + side.getStepX() * half, y + h - 1, z + side.getStepZ() * half, side, true);
			stair(x - side.getStepX() * half, y + h - 1, z - side.getStepZ() * half, side.getOpposite(), true);
		}
		for (int s = -half; s <= half; s++) {
			int ex = x + side.getStepX() * s + out.getStepX(), ez = z + side.getStepZ() * s + out.getStepZ();
			if (!solidAt(ex, y - 1, ez)) stair(ex, y - 1, ez, out.getOpposite(), false);
		}
	}

	/** Wooden door (two blocks) facing out of a room. */
	public void door(int x, int y, int z, Direction out) {
		BlockState d = facing(p.door, out.getOpposite());
		set(x, y, z, d.setValue(DoorBlock.HALF, DoubleBlockHalf.LOWER));
		set(x, y + 1, z, d.setValue(DoorBlock.HALF, DoubleBlockHalf.UPPER));
	}

	/** Spiral staircase around a newel at (cx, cz) climbing from y0 to y1; its 3x3 well is emptied. */
	public void spiral(int cx, int cz, int y0, int y1) {
		int[][] cells = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}};
		Direction[] dirs = {Direction.SOUTH, Direction.WEST, Direction.WEST, Direction.NORTH, Direction.NORTH, Direction.EAST, Direction.EAST, Direction.SOUTH};
		for (int y = y0; y <= y1; y++) {
			for (int[] c : cells) air(cx + c[0], y, cz + c[1]);
			set(cx, y, cz, p.pillar);
		}
		for (int y = y0; y <= y1; y++) {
			int i = Math.floorMod(y - y0, 8);
			int[] c = cells[i];
			stair(cx + c[0], y, cz + c[1], p.stair, dirs[i], false);
			// a top slab under every step closes the underside without stealing headroom
			if (y > y0) slab(cx + c[0], y - 1, cz + c[1], p.slab, true);
		}
	}

	public void ladder(int x, int y0, int y1, int z, Direction facing) {
		for (int y = y0; y <= y1; y++) set(x, y, z, facing(b(Blocks.LADDER), facing));
	}

	// ---------------------------------------------------------------- lighting
	/** Chain of {@code len} hanging from the block above yTop, a lantern at its end. */
	public void hang(int x, int yTop, int z, int len, BlockState lantern) {
		for (int k = 0; k < len; k++) set(x, yTop - k, z, axis(p.chain, Direction.Axis.Y));
		BlockState l = lantern.hasProperty(LanternBlock.HANGING) ? lantern.setValue(LanternBlock.HANGING, true) : lantern;
		set(x, yTop - len, z, l);
	}

	public void hang(int x, int yTop, int z, int len) {
		hang(x, yTop, z, len, p.lantern);
	}

	/** Chandelier: chain, a fence cross and four lanterns or candles. */
	public void chandelier(int x, int yTop, int z, int len) {
		for (int k = 0; k < len; k++) set(x, yTop - k, z, axis(p.chain, Direction.Axis.Y));
		int y = yTop - len;
		set(x, y, z, p.light);
		for (Direction d : Direction.Plane.HORIZONTAL) {
			set(x + d.getStepX(), y, z + d.getStepZ(), p.fence);
			set(x + d.getStepX() * 2, y, z + d.getStepZ() * 2, p.fence);
			BlockState l = p.lantern.hasProperty(LanternBlock.HANGING) ? p.lantern.setValue(LanternBlock.HANGING, true) : p.lantern;
			set(x + d.getStepX() * 2, y - 1, z + d.getStepZ() * 2, l);
		}
	}

	public void lanternOn(int x, int y, int z) {
		set(x, y, z, p.lantern.hasProperty(LanternBlock.HANGING) ? p.lantern.setValue(LanternBlock.HANGING, false) : p.lantern);
	}

	/** Lit candles (sea pickles under water). */
	public void candles(int x, int y, int z, int n) {
		n = Math.max(1, Math.min(4, n));
		if (p.underwater) {
			set(x, y, z, b(Blocks.SEA_PICKLE).setValue(SeaPickleBlock.PICKLES, n));
			return;
		}
		BlockState c = world == 5 ? b(Blocks.DYED_CANDLE.black()) : world == 3 ? b(Blocks.DYED_CANDLE.lightBlue()) : b(Blocks.DYED_CANDLE.pick(p.colA));
		if (world == 0 || world == 10) c = b(Blocks.CANDLE);
		set(x, y, z, c.setValue(CandleBlock.CANDLES, n).setValue(CandleBlock.LIT, true));
	}

	/** Light block flush in a ceiling or floor, hidden behind an open trapdoor grid. */
	public void glowTrap(int x, int y, int z, boolean ceiling) {
		set(x, y, z, p.light);
		BlockState t = p.trapdoor.setValue(TrapDoorBlock.HALF, ceiling ? Half.TOP : Half.BOTTOM);
		int yy = ceiling ? y - 1 : y + 1;
		set(x, yy, z, t);
	}

	/** Lamp post: wall-block post, cap and lantern on top. */
	public void lampPost(int x, int y, int z, int h) {
		set(x, y, z, p.trim);
		for (int k = 1; k < h; k++) set(x, y + k, z, p.wall);
		set(x, y + h, z, p.cap);
		lanternOn(x, y + h + 1, z);
	}

	/** Brazier: a cauldron-like bowl with fire on it (sea lantern under water). */
	public void brazier(int x, int y, int z) {
		set(x, y, z, p.trim);
		if (p.underwater) set(x, y + 1, z, b(Blocks.SEA_LANTERN));
		else if (world == 3 || world == 5 || world == 6) set(x, y + 1, z, b(Blocks.SOUL_CAMPFIRE));
		else set(x, y + 1, z, b(Blocks.CAMPFIRE));
	}

	// ---------------------------------------------------------------- furniture
	public void table(int x, int y, int z) {
		set(x, y, z, p.fence);
		set(x, y + 1, z, p.underwater ? slabOf(p.woodSlab, false) : p.plate);
	}

	/** Chair facing {@code toward} (the stair's back is on the other side). */
	public void chair(int x, int y, int z, Direction toward) {
		stair(x, y, z, p.woodStair, toward.getOpposite(), false);
	}

	/** Long table with chairs on both sides, along X (alongX) or Z, centred on (x, z). */
	public void banquet(int x, int y, int z, int len, boolean alongX) {
		for (int i = -len / 2; i <= len / 2; i++) {
			int tx = alongX ? x + i : x, tz = alongX ? z : z + i;
			set(tx, y, tz, p.fence);
			set(tx, y + 1, tz, slabOf(p.woodSlab, false));
			if (i % 2 == 0) {
				if (alongX) {
					chair(tx, y, tz - 1, Direction.SOUTH);
					chair(tx, y, tz + 1, Direction.NORTH);
				} else {
					chair(tx - 1, y, tz, Direction.EAST);
					chair(tx + 1, y, tz, Direction.WEST);
				}
			}
			if (i % 3 == 0) candles(tx, y + 2, tz, 1 + hi(tx, y, tz, 7, 3));
		}
	}

	/** Bed with its foot at (x, z) and its head towards {@code head}. */
	public void bed(int x, int y, int z, Direction head, DyeColor color) {
		BlockState s = facing(b(Blocks.BED.pick(color)), head);
		set(x, y, z, s.setValue(BedBlock.PART, BedPart.FOOT));
		set(x + head.getStepX(), y, z + head.getStepZ(), s.setValue(BedBlock.PART, BedPart.HEAD));
	}

	public void shelves(int x0, int z0, int x1, int z1, int y, int h) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++)
			for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++)
				for (int k = 0; k < h; k++)
					set(x, y + k, z, hc(x, y + k, z, 3, 0.15) ? b(Blocks.CHISELED_BOOKSHELF) : b(Blocks.BOOKSHELF));
	}

	public void banner(int x, int y, int z, Direction facing, DyeColor c) {
		if (p.underwater) return;
		set(x, y, z, facing(b(Blocks.WALL_BANNER.pick(c)), facing));
	}

	public void standingBanner(int x, int y, int z, DyeColor c) {
		if (p.underwater) return;
		set(x, y, z, b(Blocks.BANNER.pick(c)));
	}

	public void carpet(int x, int y, int z, DyeColor c) {
		if (p.underwater) return;
		set(x, y, z, b(Blocks.CARPET.pick(c)));
	}

	/** Carpet runner with a border, from (x0,z0) to (x1,z1). */
	public void runner(int x0, int z0, int x1, int z1, int y) {
		for (int x = Math.min(x0, x1); x <= Math.max(x0, x1); x++)
			for (int z = Math.min(z0, z1); z <= Math.max(z0, z1); z++) {
				boolean edge = x == Math.min(x0, x1) || x == Math.max(x0, x1) || z == Math.min(z0, z1) || z == Math.max(z0, z1);
				carpet(x, y, z, edge ? p.colB : p.colA);
			}
	}

	private static final Block[] POTS = {Blocks.POTTED_FERN, Blocks.POTTED_AZALEA, Blocks.POTTED_RED_TULIP, Blocks.POTTED_POPPY,
		Blocks.POTTED_BLUE_ORCHID, Blocks.POTTED_FLOWERING_AZALEA, Blocks.POTTED_DEAD_BUSH, Blocks.POTTED_CACTUS};

	public void pot(int x, int y, int z) {
		if (p.underwater) {
			set(x, y, z, b(Blocks.SEA_PICKLE));
			return;
		}
		Block b = world == 2 || world == 9 ? Blocks.POTTED_DEAD_BUSH : world == 5 ? Blocks.POTTED_WITHER_ROSE : POTS[hi(x, y, z, 11, POTS.length)];
		set(x, y, z, b(b));
	}

	public void plant(int x, int y, int z) {
		set(x, y, z, p.plants[hi(x, y, z, 13, p.plants.length)]);
	}

	public void barrel(int x, int y, int z, Direction f) {
		set(x, y, z, facing(b(Blocks.BARREL), f));
	}

	/** Stack of crates: barrels and plank blocks, hash-shaped. */
	public void crates(int x, int y, int z) {
		barrel(x, y, z, Direction.UP);
		if (hc(x, y, z, 17, 0.5)) barrel(x, y + 1, z, Direction.NORTH);
		if (hc(x, y, z, 18, 0.5)) set(x + 1, y, z, p.plank);
		if (hc(x, y, z, 19, 0.5)) barrel(x, y, z + 1, Direction.EAST);
	}

	/** Storage alcove: barrels, a cauldron, a crafting corner; returns nothing, purely decorative. */
	public void workbench(int x, int y, int z, Direction f) {
		set(x, y, z, b(Blocks.CRAFTING_TABLE));
		Direction s = f.getClockWise();
		set(x + s.getStepX(), y, z + s.getStepZ(), facing(b(world == 2 || world == 10 ? Blocks.BLAST_FURNACE : Blocks.FURNACE), f));
		set(x - s.getStepX(), y, z - s.getStepZ(), facing(b(Blocks.BARREL), Direction.UP));
		set(x - s.getStepX(), y + 1, z - s.getStepZ(), p.lantern.hasProperty(LanternBlock.HANGING) ? p.lantern.setValue(LanternBlock.HANGING, false) : p.lantern);
	}

	public void ladderOrVine(int x, int y0, int y1, int z, Direction facing) {
		ladder(x, y0, y1, z, facing);
	}

	// ---------------------------------------------------------------- site
	/**
	 * Prepares the ground under and above a footprint of radius rad: fills holes under it with the world's
	 * foundation, clears the space above up to {@code top}, carves a cavern in the cave worlds and grows a floating
	 * island under the Storm Archipelago structures. Works in untransformed coordinates.
	 */
	public void site(int rad, int top) {
		// the ceiling worlds, and World 2 whose structures stand on cave floors under its roof
		boolean cave = world == 2 || world == 3 || world == 5;
		for (int x = -rad - 1; x <= rad + 1; x++)
			for (int z = -rad - 1; z <= rad + 1; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad + 1.2) continue;
				int ceil = top;
				if (cave) ceil = Math.max(5, (int) ((top + 4) * Math.sqrt(Math.max(0, 1 - Math.pow(d / (rad + 2.0), 2)))));
				for (int y = 1; y <= ceil; y++) {
					BlockPos pos = o.offset(x, y, z);
					if (!inside(pos)) continue;
					BlockState s = lvl.getBlockState(pos);
					if (!s.isAir() && !s.equals(p.fill)) lvl.setBlock(pos, p.fill, 2);
				}
				BlockPos g = o.offset(x, 0, z);
				if (inside(g)) {
					BlockState s = lvl.getBlockState(g);
					if (s.isAir() || !s.getFluidState().isEmpty() || s.canBeReplaced()) lvl.setBlock(g, p.soil, 2);
				}
				// the restless ground swallowed the structure: it sits in a hollow as deep as it sank, rim sloping
				int hollow = sink > 0 && d < rad + 0.5 ? (d < rad - 1.5 ? sink : Math.max(0, sink - (int) Math.ceil(d - (rad - 1.5)))) : 0;
				if (hollow > 0) {
					for (int y = 1 - hollow; y <= 0; y++) {
						BlockPos q = o.offset(x, y, z);
						if (inside(q)) lvl.setBlock(q, p.fill, 2);
					}
					BlockPos f = o.offset(x, -hollow, z);
					if (inside(f)) lvl.setBlock(f, p.soil, 2);
				}
				int depth = world == 4 ? (int) ((rad + 1.5 - d) * 0.9) + 2 + hi(x, 0, z, 23, 3) : 11;
				for (int y = -1 - hollow; y >= -Math.min(13, depth + hollow); y--) {
					BlockPos pos = o.offset(x, y, z);
					if (!inside(pos)) continue;
					BlockState s = lvl.getBlockState(pos);
					if (s.isAir() || !s.getFluidState().isEmpty() || s.canBeReplaced()) lvl.setBlock(pos, y > -3 && world == 4 ? p.base : p.found, 2);
					else if (world != 4) break;
				}
			}
	}

	/** Clears the space above a footprint without touching the ground (untransformed coordinates). */
	public void siteClear(int rad, int top) {
		for (int x = -rad - 1; x <= rad + 1; x++)
			for (int z = -rad - 1; z <= rad + 1; z++) {
				if (x * x + z * z > (rad + 1.2) * (rad + 1.2)) continue;
				for (int y = 1; y <= top; y++) {
					BlockPos pos = o.offset(x, y, z);
					if (!inside(pos)) continue;
					BlockState s = lvl.getBlockState(pos);
					if (!s.isAir() && !s.equals(p.fill)) lvl.setBlock(pos, p.fill, 2);
				}
			}
	}

	/** Small floating island (local coordinates): soil top at y, a rocky cone under it. */
	public void island(int cx, int y, int cz, double rad, int depth) {
		int ir = (int) Math.ceil(rad);
		for (int x = -ir; x <= ir; x++)
			for (int z = -ir; z <= ir; z++) {
				double d = Math.sqrt(x * x + z * z);
				if (d > rad + 0.3) continue;
				int dep = (int) ((rad + 0.5 - d) / (rad + 0.5) * depth) + 1 + hi(cx + x, y, cz + z, 61, 2);
				set(cx + x, y, cz + z, p.soil);
				for (int k = 1; k <= dep; k++) set(cx + x, y - k, cz + z, k < 3 ? p.base : p.found);
			}
	}

	// ---------------------------------------------------------------- decay
	/**
	 * Ages a volume: cracked and mossy variants, missing blocks along the top edges, cobwebs in corners and the
	 * world's growth creeping on the walls (vines, sculk, roots, amethyst, coral). {@code amount} 0..1.
	 */
	public void decay(int x0, int y0, int z0, int x1, int y1, int z1, double amount) {
		if (amount <= 0) return;
		for (int x = x0; x <= x1; x++)
			for (int z = z0; z <= z1; z++)
				for (int y = y0; y <= y1; y++) {
					BlockPos pos = at(x, y, z);
					if (!inside(pos)) continue;
					BlockState s = lvl.getBlockState(pos);
					if (s.isAir() || s.is(Blocks.WATER)) {
						growth(x, y, z, pos, amount);
						continue;
					}
					if (s.hasBlockEntity()) continue;
					BlockState aged = aged(s, x, y, z);
					if (aged != null && hc(x, y, z, 29, amount * 0.4)) lvl.setBlock(pos, aged, 2);
					if (y > y0 + 1 && hc(x, y, z, 31, amount * 0.10) && emptyAt(x, y + 1, z) && isBuilt(s) && !(p.underwater && besideAir(pos))) lvl.setBlock(pos, p.fill, 2);
				}
	}

	/** Under water, a wall next to a dry pocket must not break open, or the sea would flood the refuge. */
	private boolean besideAir(BlockPos pos) {
		for (Direction d : Direction.values()) if (lvl.getBlockState(pos.relative(d)).isAir()) return true;
		return false;
	}

	private boolean isBuilt(BlockState s) {
		Block b = s.getBlock();
		return b == p.base.getBlock() || b == p.alt.getBlock() || b == p.trim.getBlock() || b == p.roof.getBlock() || b instanceof StairBlock
			|| b instanceof SlabBlock || b instanceof WallBlock || b == p.plank.getBlock();
	}

	private BlockState aged(BlockState s, int x, int y, int z) {
		Block b = s.getBlock();
		boolean alt = hc(x, y, z, 37, 0.5);
		if (b == p.base.getBlock()) return alt ? p.cracked : p.mossy;
		if (b == Blocks.STONE_BRICKS) return alt ? b(Blocks.CRACKED_STONE_BRICKS) : b(Blocks.MOSSY_STONE_BRICKS);
		if (b == Blocks.POLISHED_BLACKSTONE_BRICKS) return b(Blocks.CRACKED_POLISHED_BLACKSTONE_BRICKS);
		if (b == Blocks.DEEPSLATE_BRICKS) return b(Blocks.CRACKED_DEEPSLATE_BRICKS);
		if (b == Blocks.DEEPSLATE_TILES) return b(Blocks.CRACKED_DEEPSLATE_TILES);
		if (b == Blocks.COBBLESTONE) return b(Blocks.MOSSY_COBBLESTONE);
		if (b == Blocks.PRISMARINE_BRICKS) return b(Blocks.PRISMARINE);
		if (b == Blocks.NETHER_BRICKS) return b(Blocks.CRACKED_NETHER_BRICKS);
		if (b == Blocks.STONE_BRICK_STAIRS) return Blocks.MOSSY_STONE_BRICK_STAIRS.withPropertiesOf(s);
		if (b == Blocks.STONE_BRICK_SLAB) return Blocks.MOSSY_STONE_BRICK_SLAB.withPropertiesOf(s);
		if (b == Blocks.STONE_BRICK_WALL) return Blocks.MOSSY_STONE_BRICK_WALL.withPropertiesOf(s);
		if (b == Blocks.COBBLESTONE_STAIRS) return Blocks.MOSSY_COBBLESTONE_STAIRS.withPropertiesOf(s);
		if (b == p.alt.getBlock() && p.mossy.getBlock() != b) return p.mossy;
		return null;
	}

	private void growth(int x, int y, int z, BlockPos pos, double amount) {
		if (!hc(x, y, z, 41, amount * 0.22)) return;
		BlockState above = get(x, y + 1, z);
		boolean roofed = above != null && above.isSolid();
		Block g = p.growth.getBlock();
		if (g == Blocks.AIR) return;
		if (g == Blocks.HANGING_ROOTS) {
			if (roofed) put(pos, p.growth);
			return;
		}
		if (g == Blocks.COBWEB) {
			if (roofed && !p.underwater) put(pos, p.growth);
			return;
		}
		for (Direction d : Direction.Plane.HORIZONTAL) {
			Direction wd = dir(d);
			BlockState n = lvl.getBlockState(pos.relative(wd));
			if (!inside(pos.relative(wd)) || !n.isSolid() || !n.isCollisionShapeFullBlock(lvl, pos.relative(wd))) continue;
			BlockState s;
			if (g instanceof VineBlock) s = p.growth.setValue(VineBlock.PROPERTY_BY_DIRECTION.get(wd), true);
			else if (g instanceof MultifaceBlock) s = p.growth.setValue(MultifaceBlock.getFaceProperty(wd), true);
			else if (g instanceof AmethystClusterBlock) s = p.growth.setValue(AmethystClusterBlock.FACING, wd.getOpposite());
			else if (p.underwater) s = b(Blocks.TUBE_CORAL_WALL_FAN).setValue(BlockStateProperties.HORIZONTAL_FACING, wd.getOpposite());
			else return;
			put(pos, s);
			return;
		}
		if (roofed && !p.underwater && hc(x, y, z, 43, 0.3)) put(pos, b(Blocks.COBWEB));
	}

	/** Scatter of rubble (slabs, stairs, broken blocks) on the ground of a zone. */
	public void rubble(int x0, int z0, int x1, int z1, int y, double amount) {
		for (int x = x0; x <= x1; x++)
			for (int z = z0; z <= z1; z++) {
				if (!hc(x, y, z, 47, amount)) continue;
				if (!emptyAt(x, y, z) || !solidAt(x, y - 1, z)) continue;
				int k = hi(x, y, z, 53, 5);
				switch (k) {
					case 0 -> set(x, y, z, p.cracked);
					case 1 -> slab(x, y, z, false);
					case 2 -> stair(x, y, z, Direction.from2DDataValue(hi(x, y, z, 59, 4)), false);
					case 3 -> plant(x, y, z);
					default -> set(x, y, z, p.mossy);
				}
			}
	}

	/** Ladder helper constant so builders can refer to the ladder block facing a wall. */
	public static BlockState ladderFacing(Direction f) {
		return Blocks.LADDER.defaultBlockState().setValue(LadderBlock.FACING, f);
	}
}
