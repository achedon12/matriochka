package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.Level;

/**
 * Dimension keys and parcel geometry. Each group owns a 3000 x 3000 parcel per world, parcels are 13000 blocks apart.
 * <p>
 * Numbering: 0 is the Surface (the overworld and any foreign dimension), 1 to 10 are the ten worlds
 * ({@code matriochka:world_1} to {@code world_10}). The hidden world the story calls "World 0", inside the smallest
 * doll, cannot use 0 since that number already means the Surface: it is the dimension {@code matriochka:world_zero}
 * with the internal number {@link #ZERO} (11). Players only ever see it named "World 0".
 */
public final class Worlds {
	public static final int PARCEL_SIZE = 3000;
	public static final int PARCEL_STRIDE = 13000;
	public static final int ARENA_OFFSET = 160;
	/** Internal number of the hidden World 0 (the smallest doll). */
	public static final int ZERO = 11;

	@SuppressWarnings("unchecked")
	private static final ResourceKey<Level>[] KEYS = new ResourceKey[12];
	public static final ResourceKey<Level> REFUGE = ResourceKey.create(Registries.DIMENSION, Matriochka.id("refuge"));
	public static final ResourceKey<Level> WORLD_ZERO = ResourceKey.create(Registries.DIMENSION, Matriochka.id("world_zero"));

	static {
		for (int i = 1; i <= 10; i++) KEYS[i] = ResourceKey.create(Registries.DIMENSION, Matriochka.id("world_" + i));
		KEYS[ZERO] = WORLD_ZERO;
	}

	private Worlds() {}

	public static ResourceKey<Level> key(int world) {
		return KEYS[world];
	}

	/** World number of a level: 0 for the surface (and any foreign dimension), 1 to 10, or {@link #ZERO} for World 0. */
	public static int number(Level level) {
		return number(level.dimension());
	}

	public static int number(ResourceKey<Level> key) {
		if (!key.identifier().getNamespace().equals(Matriochka.MOD_ID)) return 0;
		String p = key.identifier().getPath();
		if (p.equals("world_zero")) return ZERO;
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
		return world == 3 || world == 5 || world == ZERO;
	}

	/** The translation key of a world's dimension name, World 0 included. */
	public static String dimensionKey(int world) {
		return world == ZERO ? "dimension.matriochka.world_zero" : "dimension.matriochka.world_" + world;
	}
}
