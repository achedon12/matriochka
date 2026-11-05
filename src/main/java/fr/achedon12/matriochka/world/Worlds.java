package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;

/** Dimension keys and parcel geometry. Each group owns a 3000 x 3000 parcel per world, parcels are 13000 blocks apart. */
public final class Worlds {
	public static final int PARCEL_SIZE = 3000;
	public static final int PARCEL_STRIDE = 13000;
	public static final int ARENA_OFFSET = 160;

	@SuppressWarnings("unchecked")
	private static final ResourceKey<Level>[] KEYS = new ResourceKey[11];
	public static final ResourceKey<Level> REFUGE = ResourceKey.create(Registries.DIMENSION, Matriochka.id("refuge"));

	static {
		for (int i = 1; i <= 10; i++) KEYS[i] = ResourceKey.create(Registries.DIMENSION, Matriochka.id("world_" + i));
	}

	private Worlds() {}

	public static ResourceKey<Level> key(int world) {
		return KEYS[world];
	}

	/** World number of a level, 0 for the surface (and any foreign dimension). */
	public static int number(Level level) {
		return number(level.dimension());
	}

	public static int number(ResourceKey<Level> key) {
		if (!key.identifier().getNamespace().equals(Matriochka.MOD_ID)) return 0;
		String p = key.identifier().getPath();
		if (!p.startsWith("world_")) return 0;
		try {
			return Integer.parseInt(p.substring(6));
		} catch (NumberFormatException e) {
			return 0;
		}
	}

	public static boolean isModWorld(Level level) {
		return number(level) > 0;
	}

	public static BlockPos parcelCenter(int parcel) {
		return new BlockPos(parcel * PARCEL_STRIDE, 0, 0);
	}

	public static int parcelOf(BlockPos pos) {
		return Math.floorDiv(pos.getX() + PARCEL_STRIDE / 2, PARCEL_STRIDE);
	}

	public static boolean ceiling(int world) {
		return world == 3 || world == 5;
	}
}
