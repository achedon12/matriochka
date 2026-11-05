package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CopperBulbBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Building materials of one world: the mod's own blocks for the body of every structure, with fitting vanilla blocks
 * for everything that needs a shape (stairs, slabs, walls, fences, panes, lanterns).
 */
public final class Palette {
	/** Main wall, secondary wall (bands, quoins), plinth and cornice block, column shaft, capital. */
	public BlockState base, alt, trim, pillar, cap;
	/** Floor, the two inlay colours, foundation fill. */
	public BlockState floor, inlay, inlay2, found;
	/** Roof body, roof stairs and slabs, general stairs and slabs, wall blocks (parapets, balusters). */
	public BlockState roof, roofStair, roofSlab, stair, slab, wall;
	/** Woodwork: fence, planks, log, wood stairs and slabs, trapdoor, door. */
	public BlockState fence, plank, log, woodStair, woodSlab, trapdoor, door, plate;
	/** Lighting: full light block, hanging lantern, chain, glowing accent of the world. */
	public BlockState light, lantern, chain, accent;
	/** Openings: window pane, bars, full glass. */
	public BlockState pane, bars, glass;
	/** Decay variants of the base and alt blocks, a growth that creeps on old walls, top soil and leaves. */
	public BlockState cracked, mossy, growth, soil, leaves;
	/** What fills empty space (air, or water in the Pressure Ocean) and what pools hold. */
	public BlockState fill, liquid;
	/** Small plants scattered in gardens and cracks. */
	public BlockState[] plants;
	public DyeColor colA, colB;
	public boolean underwater;

	private static BlockState b(Block block) {
		return block.defaultBlockState();
	}

	private static BlockState m(String id) {
		return ModContent.block(id).defaultBlockState();
	}

	private static BlockState leaves(Block block) {
		BlockState s = block.defaultBlockState();
		return s.hasProperty(LeavesBlock.PERSISTENT) ? s.setValue(LeavesBlock.PERSISTENT, true) : s;
	}

	private static BlockState up(Block block) {
		BlockState s = block.defaultBlockState();
		return s.hasProperty(RotatedPillarBlock.AXIS) ? s.setValue(RotatedPillarBlock.AXIS, Direction.Axis.Y) : s;
	}

	public static Palette of(int world) {
		Palette p = new Palette();
		p.fill = b(Blocks.AIR);
		p.liquid = b(Blocks.WATER);
		p.chain = b(Blocks.IRON_CHAIN);
		p.bars = b(Blocks.IRON_BARS);
		p.lantern = b(Blocks.LANTERN);
		p.growth = b(Blocks.COBWEB);
		p.plants = new BlockState[] {b(Blocks.SHORT_GRASS), b(Blocks.FERN)};
		switch (world) {
			case 1 -> {
				p.base = m("rootstone"); p.alt = b(Blocks.MOSSY_STONE_BRICKS); p.trim = b(Blocks.MUD_BRICKS);
				p.pillar = up(Blocks.STRIPPED_JUNGLE_LOG); p.cap = b(Blocks.CHISELED_STONE_BRICKS);
				p.floor = m("rootstone"); p.inlay = m("spore_moss"); p.inlay2 = b(Blocks.MOSS_BLOCK); p.found = m("rootstone");
				p.roof = b(Blocks.JUNGLE_PLANKS); p.roofStair = b(Blocks.JUNGLE_STAIRS); p.roofSlab = b(Blocks.JUNGLE_SLAB);
				p.stair = b(Blocks.MOSSY_STONE_BRICK_STAIRS); p.slab = b(Blocks.MOSSY_STONE_BRICK_SLAB); p.wall = b(Blocks.MOSSY_STONE_BRICK_WALL);
				wood(p, Blocks.JUNGLE_FENCE, Blocks.JUNGLE_PLANKS, Blocks.JUNGLE_LOG, Blocks.JUNGLE_STAIRS, Blocks.JUNGLE_SLAB, Blocks.JUNGLE_TRAPDOOR, Blocks.JUNGLE_DOOR, Blocks.JUNGLE_PRESSURE_PLATE);
				p.light = m("spore_bloom"); p.accent = b(Blocks.VERDANT_FROGLIGHT);
				p.pane = b(Blocks.STAINED_GLASS_PANE.green()); p.glass = b(Blocks.STAINED_GLASS.lime());
				p.cracked = b(Blocks.CRACKED_STONE_BRICKS); p.mossy = b(Blocks.MOSS_BLOCK); p.growth = b(Blocks.VINE);
				p.soil = b(Blocks.ROOTED_DIRT); p.leaves = leaves(Blocks.JUNGLE_LEAVES);
				p.plants = new BlockState[] {b(Blocks.FERN), b(Blocks.AZALEA), b(Blocks.SHORT_GRASS), b(Blocks.FLOWERING_AZALEA), b(Blocks.RED_MUSHROOM)};
				p.colA = DyeColor.GREEN; p.colB = DyeColor.PURPLE;
			}
			case 2 -> {
				p.base = m("ashrock"); p.alt = b(Blocks.POLISHED_BLACKSTONE_BRICKS); p.trim = b(Blocks.POLISHED_BLACKSTONE);
				p.pillar = up(Blocks.POLISHED_BASALT); p.cap = b(Blocks.CHISELED_POLISHED_BLACKSTONE);
				p.floor = m("ashrock"); p.inlay = b(Blocks.GILDED_BLACKSTONE); p.inlay2 = m("ember_stone"); p.found = b(Blocks.BLACKSTONE);
				p.roof = b(Blocks.BLACKSTONE); p.roofStair = b(Blocks.BLACKSTONE_STAIRS); p.roofSlab = b(Blocks.BLACKSTONE_SLAB);
				p.stair = b(Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS); p.slab = b(Blocks.POLISHED_BLACKSTONE_BRICK_SLAB); p.wall = b(Blocks.POLISHED_BLACKSTONE_BRICK_WALL);
				wood(p, Blocks.DARK_OAK_FENCE, Blocks.DARK_OAK_PLANKS, Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_STAIRS, Blocks.DARK_OAK_SLAB, Blocks.DARK_OAK_TRAPDOOR, Blocks.DARK_OAK_DOOR, Blocks.DARK_OAK_PRESSURE_PLATE);
				p.light = m("ember_stone"); p.accent = b(Blocks.MAGMA_BLOCK);
				p.pane = b(Blocks.STAINED_GLASS_PANE.orange()); p.glass = b(Blocks.STAINED_GLASS.orange());
				p.cracked = b(Blocks.CRACKED_POLISHED_BLACKSTONE_BRICKS); p.mossy = b(Blocks.BLACKSTONE);
				p.soil = b(Blocks.BLACKSTONE); p.leaves = b(Blocks.BASALT);
				p.plants = new BlockState[] {b(Blocks.DEAD_BUSH), b(Blocks.POINTED_DRIPSTONE)};
				p.liquid = b(Blocks.LAVA);
				p.colA = DyeColor.ORANGE; p.colB = DyeColor.BLACK;
			}
			case 3 -> {
				p.base = m("dungeon_brick"); p.alt = b(Blocks.STONE_BRICKS); p.trim = b(Blocks.CHISELED_STONE_BRICKS);
				p.pillar = b(Blocks.SMOOTH_STONE); p.cap = b(Blocks.CHISELED_STONE_BRICKS);
				p.floor = m("dungeon_brick"); p.inlay = b(Blocks.POLISHED_ANDESITE); p.inlay2 = m("cold_lamp"); p.found = m("dungeon_brick");
				p.roof = b(Blocks.STONE_BRICKS); p.roofStair = b(Blocks.STONE_BRICK_STAIRS); p.roofSlab = b(Blocks.STONE_BRICK_SLAB);
				p.stair = b(Blocks.STONE_BRICK_STAIRS); p.slab = b(Blocks.STONE_BRICK_SLAB); p.wall = b(Blocks.STONE_BRICK_WALL);
				wood(p, Blocks.SPRUCE_FENCE, Blocks.SPRUCE_PLANKS, Blocks.SPRUCE_LOG, Blocks.SPRUCE_STAIRS, Blocks.SPRUCE_SLAB, Blocks.IRON_TRAPDOOR, Blocks.IRON_DOOR, Blocks.SPRUCE_PRESSURE_PLATE);
				p.light = m("cold_lamp"); p.accent = m("cold_lamp"); p.lantern = b(Blocks.SOUL_LANTERN);
				p.pane = b(Blocks.IRON_BARS); p.glass = b(Blocks.GLASS);
				p.cracked = b(Blocks.CRACKED_STONE_BRICKS); p.mossy = b(Blocks.MOSSY_STONE_BRICKS);
				p.soil = b(Blocks.GRAVEL); p.leaves = b(Blocks.COBWEB);
				p.plants = new BlockState[] {b(Blocks.BROWN_MUSHROOM), b(Blocks.COBWEB)};
				p.colA = DyeColor.GRAY; p.colB = DyeColor.LIGHT_BLUE;
			}
			case 4 -> {
				p.base = m("cloudstone"); p.alt = b(Blocks.QUARTZ_BRICKS); p.trim = b(Blocks.SMOOTH_QUARTZ);
				p.pillar = up(Blocks.QUARTZ_PILLAR); p.cap = b(Blocks.CHISELED_QUARTZ_BLOCK);
				p.floor = m("cloudstone"); p.inlay = b(Blocks.POLISHED_DIORITE); p.inlay2 = b(Blocks.CUT_COPPER.waxed().exposed()); p.found = m("cloudstone");
				p.roof = b(Blocks.CUT_COPPER.waxed().weathered()); p.roofStair = b(Blocks.CUT_COPPER_STAIRS.waxed().weathered()); p.roofSlab = b(Blocks.CUT_COPPER_SLAB.waxed().weathered());
				p.stair = b(Blocks.SMOOTH_QUARTZ_STAIRS); p.slab = b(Blocks.SMOOTH_QUARTZ_SLAB); p.wall = b(Blocks.DIORITE_WALL);
				wood(p, Blocks.BIRCH_FENCE, Blocks.BIRCH_PLANKS, Blocks.BIRCH_LOG, Blocks.BIRCH_STAIRS, Blocks.BIRCH_SLAB, Blocks.COPPER_TRAPDOOR.waxed().exposed(), Blocks.COPPER_DOOR.waxed().exposed(), Blocks.BIRCH_PRESSURE_PLATE);
				p.light = m("storm_glass"); p.accent = m("storm_glass");
				p.lantern = b(Blocks.COPPER_LANTERN.waxed().unaffected()); p.chain = b(Blocks.COPPER_CHAIN.waxed().exposed());
				p.pane = b(Blocks.STAINED_GLASS_PANE.lightBlue()); p.bars = b(Blocks.COPPER_BARS.waxed().exposed()); p.glass = b(Blocks.STAINED_GLASS.white());
				p.cracked = b(Blocks.CALCITE); p.mossy = m("skygrass"); p.growth = b(Blocks.AIR);
				p.soil = m("skygrass"); p.leaves = leaves(Blocks.BIRCH_LEAVES);
				p.plants = new BlockState[] {b(Blocks.SHORT_GRASS), b(Blocks.OXEYE_DAISY), b(Blocks.CORNFLOWER), b(Blocks.LILY_OF_THE_VALLEY)};
				p.colA = DyeColor.WHITE; p.colB = DyeColor.BLUE;
			}
			case 5 -> {
				p.base = m("umbral_stone"); p.alt = b(Blocks.DEEPSLATE_BRICKS); p.trim = b(Blocks.POLISHED_DEEPSLATE);
				p.pillar = up(Blocks.DEEPSLATE); p.cap = b(Blocks.CHISELED_DEEPSLATE);
				p.floor = m("umbral_stone"); p.inlay = b(Blocks.DEEPSLATE_TILES); p.inlay2 = b(Blocks.SCULK); p.found = b(Blocks.COBBLED_DEEPSLATE);
				p.roof = b(Blocks.DEEPSLATE_TILES); p.roofStair = b(Blocks.DEEPSLATE_TILE_STAIRS); p.roofSlab = b(Blocks.DEEPSLATE_TILE_SLAB);
				p.stair = b(Blocks.DEEPSLATE_BRICK_STAIRS); p.slab = b(Blocks.DEEPSLATE_BRICK_SLAB); p.wall = b(Blocks.DEEPSLATE_BRICK_WALL);
				wood(p, Blocks.DARK_OAK_FENCE, Blocks.DARK_OAK_PLANKS, Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_STAIRS, Blocks.DARK_OAK_SLAB, Blocks.DARK_OAK_TRAPDOOR, Blocks.DARK_OAK_DOOR, Blocks.DARK_OAK_PRESSURE_PLATE);
				p.light = m("faint_glow"); p.accent = m("faint_glow"); p.lantern = b(Blocks.SOUL_LANTERN);
				p.pane = b(Blocks.STAINED_GLASS_PANE.black()); p.glass = b(Blocks.TINTED_GLASS);
				p.cracked = b(Blocks.CRACKED_DEEPSLATE_BRICKS); p.mossy = m("umbral_moss"); p.growth = b(Blocks.SCULK_VEIN);
				p.soil = m("umbral_moss"); p.leaves = b(Blocks.SCULK);
				p.plants = new BlockState[] {b(Blocks.SCULK_VEIN), b(Blocks.SHORT_GRASS)};
				p.colA = DyeColor.BLACK; p.colB = DyeColor.BLUE;
			}
			case 6 -> {
				p.base = m("inverted_stone"); p.alt = b(Blocks.PURPUR_BLOCK); p.trim = b(Blocks.END_STONE_BRICKS);
				p.pillar = up(Blocks.PURPUR_PILLAR); p.cap = b(Blocks.AMETHYST_BLOCK);
				p.floor = m("inverted_stone"); p.inlay = m("prism_moss"); p.inlay2 = b(Blocks.AMETHYST_BLOCK); p.found = b(Blocks.END_STONE);
				p.roof = b(Blocks.PURPUR_BLOCK); p.roofStair = b(Blocks.PURPUR_STAIRS); p.roofSlab = b(Blocks.PURPUR_SLAB);
				p.stair = b(Blocks.END_STONE_BRICK_STAIRS); p.slab = b(Blocks.END_STONE_BRICK_SLAB); p.wall = b(Blocks.END_STONE_BRICK_WALL);
				wood(p, Blocks.CHERRY_FENCE, Blocks.CHERRY_PLANKS, Blocks.CHERRY_LOG, Blocks.CHERRY_STAIRS, Blocks.CHERRY_SLAB, Blocks.CHERRY_TRAPDOOR, Blocks.CHERRY_DOOR, Blocks.CHERRY_PRESSURE_PLATE);
				p.light = b(Blocks.PEARLESCENT_FROGLIGHT); p.accent = m("mirror_glass"); p.lantern = b(Blocks.SOUL_LANTERN);
				p.pane = b(Blocks.STAINED_GLASS_PANE.magenta()); p.glass = m("mirror_glass");
				p.cracked = b(Blocks.END_STONE); p.mossy = m("prism_moss"); p.growth = b(Blocks.AMETHYST_CLUSTER);
				p.soil = m("prism_moss"); p.leaves = leaves(Blocks.CHERRY_LEAVES);
				p.plants = new BlockState[] {b(Blocks.SMALL_AMETHYST_BUD), b(Blocks.MEDIUM_AMETHYST_BUD), b(Blocks.ALLIUM)};
				p.colA = DyeColor.MAGENTA; p.colB = DyeColor.CYAN;
			}
			case 7 -> {
				p.base = m("trench_rock"); p.alt = b(Blocks.PRISMARINE_BRICKS); p.trim = b(Blocks.DARK_PRISMARINE);
				p.pillar = b(Blocks.PRISMARINE); p.cap = b(Blocks.DARK_PRISMARINE);
				p.floor = m("trench_rock"); p.inlay = b(Blocks.PRISMARINE); p.inlay2 = b(Blocks.SEA_LANTERN); p.found = m("abyssal_sand");
				p.roof = b(Blocks.DARK_PRISMARINE); p.roofStair = b(Blocks.DARK_PRISMARINE_STAIRS); p.roofSlab = b(Blocks.DARK_PRISMARINE_SLAB);
				p.stair = b(Blocks.PRISMARINE_BRICK_STAIRS); p.slab = b(Blocks.PRISMARINE_BRICK_SLAB); p.wall = b(Blocks.PRISMARINE_WALL);
				wood(p, Blocks.DARK_OAK_FENCE, Blocks.DARK_OAK_PLANKS, Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_STAIRS, Blocks.DARK_OAK_SLAB, Blocks.DARK_OAK_TRAPDOOR, Blocks.DARK_OAK_DOOR, Blocks.DARK_OAK_PRESSURE_PLATE);
				p.light = b(Blocks.SEA_LANTERN); p.accent = m("pressure_coral");
				p.pane = b(Blocks.STAINED_GLASS_PANE.cyan()); p.glass = b(Blocks.GLASS);
				p.cracked = b(Blocks.PRISMARINE); p.mossy = b(Blocks.DEAD_BRAIN_CORAL_BLOCK); p.growth = b(Blocks.TUBE_CORAL_FAN);
				p.soil = m("abyssal_sand"); p.leaves = b(Blocks.HORN_CORAL_BLOCK);
				p.plants = new BlockState[] {b(Blocks.SEAGRASS), b(Blocks.TUBE_CORAL), b(Blocks.BRAIN_CORAL), b(Blocks.HORN_CORAL), b(Blocks.SEA_PICKLE), b(Blocks.FIRE_CORAL)};
				p.fill = b(Blocks.WATER);
				p.underwater = true;
				p.colA = DyeColor.CYAN; p.colB = DyeColor.BLUE;
			}
			case 8 -> {
				p.base = m("hourstone"); p.alt = b(Blocks.TUFF_BRICKS); p.trim = b(Blocks.POLISHED_TUFF);
				p.pillar = up(Blocks.STRIPPED_CHERRY_LOG); p.cap = b(Blocks.CHISELED_TUFF_BRICKS);
				p.floor = m("hourstone"); p.inlay = m("temporal_sand_block"); p.inlay2 = b(Blocks.CUT_COPPER.waxed().exposed()); p.found = b(Blocks.TUFF);
				p.roof = b(Blocks.CHERRY_PLANKS); p.roofStair = b(Blocks.CHERRY_STAIRS); p.roofSlab = b(Blocks.CHERRY_SLAB);
				p.stair = b(Blocks.TUFF_BRICK_STAIRS); p.slab = b(Blocks.TUFF_BRICK_SLAB); p.wall = b(Blocks.TUFF_BRICK_WALL);
				wood(p, Blocks.OAK_FENCE, Blocks.OAK_PLANKS, Blocks.OAK_LOG, Blocks.OAK_STAIRS, Blocks.OAK_SLAB, Blocks.COPPER_TRAPDOOR.waxed().weathered(), Blocks.OAK_DOOR, Blocks.OAK_PRESSURE_PLATE);
				p.light = b(Blocks.OCHRE_FROGLIGHT);
				p.accent = b(Blocks.COPPER_BULB.waxed().exposed()).setValue(CopperBulbBlock.LIT, true);
				p.lantern = b(Blocks.COPPER_LANTERN.waxed().exposed()); p.chain = b(Blocks.COPPER_CHAIN.waxed().exposed());
				p.pane = b(Blocks.STAINED_GLASS_PANE.yellow()); p.bars = b(Blocks.COPPER_BARS.waxed().weathered()); p.glass = b(Blocks.STAINED_GLASS.orange());
				p.cracked = b(Blocks.TUFF); p.mossy = b(Blocks.MOSSY_COBBLESTONE); p.growth = b(Blocks.VINE);
				p.soil = m("chrono_grass"); p.leaves = leaves(Blocks.CHERRY_LEAVES);
				p.plants = new BlockState[] {b(Blocks.PINK_PETALS), b(Blocks.POPPY), b(Blocks.DANDELION), b(Blocks.LEAF_LITTER), b(Blocks.SNOW), b(Blocks.SHORT_GRASS)};
				p.colA = DyeColor.YELLOW; p.colB = DyeColor.ORANGE;
			}
			case 9 -> {
				p.base = m("living_rock"); p.alt = b(Blocks.MUD_BRICKS); p.trim = b(Blocks.PACKED_MUD);
				p.pillar = up(Blocks.STRIPPED_MANGROVE_LOG); p.cap = m("flesh_stone");
				p.floor = m("living_rock"); p.inlay = b(Blocks.ROOTED_DIRT); p.inlay2 = m("pulse_vein"); p.found = m("living_rock");
				p.roof = b(Blocks.MANGROVE_PLANKS); p.roofStair = b(Blocks.MANGROVE_STAIRS); p.roofSlab = b(Blocks.MANGROVE_SLAB);
				p.stair = b(Blocks.MUD_BRICK_STAIRS); p.slab = b(Blocks.MUD_BRICK_SLAB); p.wall = b(Blocks.MUD_BRICK_WALL);
				wood(p, Blocks.MANGROVE_FENCE, Blocks.MANGROVE_PLANKS, Blocks.MANGROVE_LOG, Blocks.MANGROVE_STAIRS, Blocks.MANGROVE_SLAB, Blocks.MANGROVE_TRAPDOOR, Blocks.MANGROVE_DOOR, Blocks.MANGROVE_PRESSURE_PLATE);
				p.light = m("pulse_vein"); p.accent = m("pulse_vein");
				p.pane = b(Blocks.STAINED_GLASS_PANE.red()); p.glass = b(Blocks.STAINED_GLASS.brown());
				p.cracked = b(Blocks.PACKED_MUD); p.mossy = b(Blocks.ROOTED_DIRT); p.growth = b(Blocks.HANGING_ROOTS);
				p.soil = b(Blocks.ROOTED_DIRT); p.leaves = b(Blocks.MANGROVE_ROOTS);
				p.plants = new BlockState[] {b(Blocks.DEAD_BUSH), b(Blocks.SHORT_GRASS), b(Blocks.BROWN_MUSHROOM)};
				p.colA = DyeColor.RED; p.colB = DyeColor.BROWN;
			}
			case 10 -> {
				p.base = m("painted_wood"); p.alt = m("giant_plank"); p.trim = m("lacquer_block");
				p.pillar = up(Blocks.STRIPPED_SPRUCE_LOG); p.cap = b(Blocks.GOLD_BLOCK);
				p.floor = m("giant_plank"); p.inlay = m("workshop_felt"); p.inlay2 = m("lacquer_block"); p.found = m("giant_plank");
				p.roof = m("lacquer_block"); p.roofStair = b(Blocks.MANGROVE_STAIRS); p.roofSlab = b(Blocks.MANGROVE_SLAB);
				p.stair = b(Blocks.SPRUCE_STAIRS); p.slab = b(Blocks.SPRUCE_SLAB); p.wall = b(Blocks.BRICK_WALL);
				wood(p, Blocks.SPRUCE_FENCE, Blocks.SPRUCE_PLANKS, Blocks.SPRUCE_LOG, Blocks.SPRUCE_STAIRS, Blocks.SPRUCE_SLAB, Blocks.SPRUCE_TRAPDOOR, Blocks.SPRUCE_DOOR, Blocks.SPRUCE_PRESSURE_PLATE);
				p.light = m("lacquer_glow"); p.accent = b(Blocks.GOLD_BLOCK);
				p.pane = b(Blocks.GLASS_PANE); p.glass = b(Blocks.GLASS);
				p.cracked = m("giant_plank"); p.mossy = m("workshop_felt");
				p.soil = m("workshop_felt"); p.leaves = b(Blocks.WOOL.red());
				p.plants = new BlockState[] {b(Blocks.CARPET.red()), b(Blocks.CARPET.yellow()), b(Blocks.CARPET.white())};
				p.colA = DyeColor.RED; p.colB = DyeColor.YELLOW;
			}
			default -> {
				p.base = b(Blocks.STONE_BRICKS); p.alt = b(Blocks.DEEPSLATE_TILES); p.trim = b(Blocks.POLISHED_DEEPSLATE);
				p.pillar = up(Blocks.QUARTZ_PILLAR); p.cap = b(Blocks.CHISELED_STONE_BRICKS);
				p.floor = b(Blocks.POLISHED_DEEPSLATE); p.inlay = m("lacquer_block"); p.inlay2 = m("painted_wood"); p.found = b(Blocks.STONE);
				p.roof = b(Blocks.DEEPSLATE_TILES); p.roofStair = b(Blocks.DEEPSLATE_TILE_STAIRS); p.roofSlab = b(Blocks.DEEPSLATE_TILE_SLAB);
				p.stair = b(Blocks.STONE_BRICK_STAIRS); p.slab = b(Blocks.STONE_BRICK_SLAB); p.wall = b(Blocks.STONE_BRICK_WALL);
				wood(p, Blocks.DARK_OAK_FENCE, Blocks.DARK_OAK_PLANKS, Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_STAIRS, Blocks.DARK_OAK_SLAB, Blocks.DARK_OAK_TRAPDOOR, Blocks.DARK_OAK_DOOR, Blocks.DARK_OAK_PRESSURE_PLATE);
				p.light = b(Blocks.GLOWSTONE); p.accent = m("lacquer_block");
				p.pane = b(Blocks.GLASS_PANE); p.glass = b(Blocks.GLASS);
				p.cracked = b(Blocks.CRACKED_STONE_BRICKS); p.mossy = b(Blocks.MOSSY_STONE_BRICKS); p.growth = b(Blocks.VINE);
				p.soil = b(Blocks.GRASS_BLOCK); p.leaves = leaves(Blocks.OAK_LEAVES);
				p.plants = new BlockState[] {b(Blocks.POPPY), b(Blocks.DANDELION), b(Blocks.SHORT_GRASS)};
				p.colA = DyeColor.RED; p.colB = DyeColor.YELLOW;
			}
		}
		return p;
	}

	private static void wood(Palette p, Block fence, Block plank, Block log, Block stair, Block slab, Block trapdoor, Block door, Block plate) {
		p.plate = b(plate);
		p.fence = b(fence);
		p.plank = b(plank);
		p.log = up(log);
		p.woodStair = b(stair);
		p.woodSlab = b(slab);
		p.trapdoor = b(trapdoor);
		p.door = b(door);
	}
}
