package fr.achedon12.matriochka.mc;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Block;

/**
 * The coloured and copper block families the mod builds with (versions/<mc>/): 26.1 has them one block per field, so this
 * gives them the collections' shape (26.2: ColorCollection, WeatheringCopperCollection), looked up by id.
 */
public final class McBlocks {
	private McBlocks() {}

	private static Block id(String path) {
		return BuiltInRegistries.BLOCK.getValue(Identifier.withDefaultNamespace(path));
	}

	/** One block per dye colour, "<colour>_<base>". */
	public record Colors(String base) {
		public Block pick(DyeColor c) {
			return id(c.getName() + "_" + base);
		}
		public Block white() {
			return id("white_" + base);
		}
		public Block orange() {
			return id("orange_" + base);
		}
		public Block magenta() {
			return id("magenta_" + base);
		}
		public Block lightBlue() {
			return id("light_blue_" + base);
		}
		public Block yellow() {
			return id("yellow_" + base);
		}
		public Block lime() {
			return id("lime_" + base);
		}
		public Block pink() {
			return id("pink_" + base);
		}
		public Block gray() {
			return id("gray_" + base);
		}
		public Block lightGray() {
			return id("light_gray_" + base);
		}
		public Block cyan() {
			return id("cyan_" + base);
		}
		public Block purple() {
			return id("purple_" + base);
		}
		public Block blue() {
			return id("blue_" + base);
		}
		public Block brown() {
			return id("brown_" + base);
		}
		public Block green() {
			return id("green_" + base);
		}
		public Block red() {
			return id("red_" + base);
		}
		public Block black() {
			return id("black_" + base);
		}
	}

	/** The four weathering states of one copper block, waxed or not. */
	public record ByState(String prefix, String base) {
		private Block at(String state) {
			// the plain copper block is "copper_block" unweathered and "<state>_copper" after
			String b = base.equals("copper_block") && !state.isEmpty() ? "copper" : base;
			return id(prefix + state + b);
		}
		public Block unaffected() { return at(""); }
		public Block exposed() { return at("exposed_"); }
		public Block weathered() { return at("weathered_"); }
		public Block oxidized() { return at("oxidized_"); }
	}

	public record Copper(String base) {
		public ByState waxed() { return new ByState("waxed_", base); }
		public ByState weathering() { return new ByState("", base); }
	}

	public static final Colors WOOL = new Colors("wool");
	public static final Colors STAINED_GLASS = new Colors("stained_glass");
	public static final Colors STAINED_GLASS_PANE = new Colors("stained_glass_pane");
	public static final Colors CONCRETE = new Colors("concrete");
	public static final Colors CARPET = new Colors("carpet");
	public static final Colors BED = new Colors("bed");
	public static final Colors BANNER = new Colors("banner");
	public static final Colors WALL_BANNER = new Colors("wall_banner");
	public static final Colors DYED_TERRACOTTA = new Colors("terracotta");
	public static final Colors DYED_CANDLE = new Colors("candle");
	public static final Copper CUT_COPPER = new Copper("cut_copper");
	public static final Copper LIGHTNING_ROD = new Copper("lightning_rod");
	public static final Copper COPPER_BULB = new Copper("copper_bulb");
	public static final Copper CUT_COPPER_STAIRS = new Copper("cut_copper_stairs");
	public static final Copper COPPER_TRAPDOOR = new Copper("copper_trapdoor");
	public static final Copper COPPER_LANTERN = new Copper("copper_lantern");
	public static final Copper COPPER_CHAIN = new Copper("copper_chain");
	public static final Copper COPPER_BLOCK = new Copper("copper_block");
	public static final Copper COPPER_BARS = new Copper("copper_bars");
	public static final Copper CUT_COPPER_SLAB = new Copper("cut_copper_slab");
	public static final Copper COPPER_GRATE = new Copper("copper_grate");
	public static final Copper COPPER_DOOR = new Copper("copper_door");
}
