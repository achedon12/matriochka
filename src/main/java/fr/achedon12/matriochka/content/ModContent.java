package fr.achedon12.matriochka.content;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Blocks2;
import fr.achedon12.matriochka.block.Blocks3;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.StationBlock;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioCritter;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.item.MatrioItem;
import fr.achedon12.matriochka.net.StationMenu;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.fabricmc.fabric.api.menu.v1.ExtendedMenuType;
import net.fabricmc.fabric.api.object.builder.v1.block.entity.FabricBlockEntityTypeBuilder;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricEntityType;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

/** Registers every block, item, entity, block entity, menu and creative tab from the generated {@link Content}. */
public final class ModContent {
	private static final Map<String, Block> BLOCKS = new LinkedHashMap<>();
	private static final Map<String, Item> ITEMS = new LinkedHashMap<>();
	private static final Map<Item, String> IDS = new HashMap<>();
	private static final Map<String, Defs.ItemDef> DEFS = new HashMap<>();
	private static final Map<String, EntityType<?>> ENTITIES = new LinkedHashMap<>();
	public static BlockEntityType<DataBlockEntity> BE_DATA;
	/** The Nesting Cradle's own block entity: an animated GeckoLib model (block/CradleBlockEntity). */
	public static BlockEntityType<fr.achedon12.matriochka.block.CradleBlockEntity> BE_CRADLE;
	public static final MenuType<StationMenu> STATION_MENU = Registry.register(BuiltInRegistries.MENU, Matriochka.id("station"),
		new ExtendedMenuType<>(StationMenu::new, StationMenu.Data.CODEC));

	private ModContent() {}

	public static Block block(String id) {
		Block b = BLOCKS.get(id);
		if (b == null) throw new IllegalArgumentException("Unknown Matriochka block " + id);
		return b;
	}

	public static Item item(String id) {
		Item i = ITEMS.get(id);
		if (i == null) throw new IllegalArgumentException("Unknown Matriochka item " + id);
		return i;
	}

	public static Item itemOrNull(String id) {
		return ITEMS.get(id);
	}

	public static String idOf(Item item) {
		return IDS.getOrDefault(item, "");
	}

	public static Defs.ItemDef def(String id) {
		return DEFS.get(id);
	}

	public static EntityType<?> entity(String id) {
		return ENTITIES.get(id);
	}

	public static Map<String, EntityType<?>> entities() {
		return ENTITIES;
	}

	public static Defs.BossDef bossForWorld(int world) {
		return MatrioBoss.byWorld(world);
	}

	private static ResourceKey<Block> bkey(String id) {
		return ResourceKey.create(Registries.BLOCK, Matriochka.id(id));
	}

	private static ResourceKey<Item> ikey(String id) {
		return ResourceKey.create(Registries.ITEM, Matriochka.id(id));
	}

	// ---------------------------------------------------------------- blocks
	private static Block makeBlock(Defs.BlockDef d, BlockBehaviour.Properties p) {
		return switch (d.kind()) {
			case "soil" -> new Blocks2.WorldSoil(Integer.parseInt(d.id().substring("world_soil_".length())), p.strength(0.6f).sound(SoundType.GRAVEL).randomTicks());
			case "planted_seed" -> new Blocks2.PlantedSeed(p.strength(0.2f).noOcclusion().noCollision().sound(SoundType.CROP));
			case "world_block" -> new Blocks2.WorldBlock(p.strength(3f, 3600000f).sound(SoundType.WOOD).lightLevel(s -> 9).pushReaction(fr.achedon12.matriochka.mc.Mc.immovable()));
			case "threshold" -> new Blocks2.Threshold(p.strength(-1f, 3600000f).lightLevel(s -> 12).noLootTable());
			case "cradle" -> new Blocks3.SoulCradle(p.strength(1.5f).sound(SoundType.WOOD).noOcclusion());
			case "death_chest" -> new Blocks3.DeathChest(p.strength(-1f, 3600000f).sound(SoundType.WOOD).noLootTable());
			case "nesting_chest" -> {
				int rows = d.id().endsWith("_little") ? 1 : d.id().endsWith("_medium") ? 2 : 3;
				yield new Blocks3.NestingChest(rows == 3 ? p.strength(2f).sound(SoundType.WOOD) : p.strength(1.5f).sound(SoundType.WOOD).noOcclusion(), rows);
			}
			case "boss_altar" -> new Blocks3.BossAltar(p.strength(-1f, 3600000f).lightLevel(s -> 10).noLootTable());
			case "reliquary" -> new fr.achedon12.matriochka.block.Reliquary(p.strength(-1f, 3600000f).sound(SoundType.WOOD).lightLevel(s -> 7).noLootTable());
			case "lair_heart" -> new Blocks3.LairHeart(p.strength(-1f, 3600000f).sound(SoundType.SCULK_CATALYST).lightLevel(s -> 5).noLootTable());
			case "sealed_door" -> new Blocks3.SealedDoor(p.strength(-1f, 3600000f).sound(SoundType.STONE));
			case "station" -> new StationBlock(d.id(), p.strength(2.5f).sound(SoundType.WOOD).lightLevel(s -> 4).noOcclusion());
			case "world_ore" -> {
				// the drops of the Living Ember, the Silent Stone and the Hanging Vein follow their rules (world/WorldOres)
				BlockBehaviour.Properties q = p.strength(3.5f, 3f).requiresCorrectToolForDrops();
				q = switch (d.id()) {
					case "living_ember_ore" -> q.lightLevel(s -> 7).noLootTable();
					case "hanging_ore" -> q.lightLevel(s -> 5).noLootTable();
					case "silent_stone_ore" -> q.sound(SoundType.DEEPSLATE).noLootTable();
					case "fulgurite_ore" -> q.sound(SoundType.GLASS).lightLevel(s -> 3);
					default -> q;
				};
				yield new Block(q);
			}
			case "matriochkite_block" -> new Block(p.strength(5f, 6f).sound(SoundType.METAL).requiresCorrectToolForDrops().lightLevel(s -> 5).mapColor(MapColor.COLOR_RED));
			case "time_sprout" -> new fr.achedon12.matriochka.block.TimeSprout(p.noCollision().instabreak().sound(SoundType.CROP).noOcclusion());
			case "nesting_cradle" -> new fr.achedon12.matriochka.block.NestingCradle(p.strength(2f).sound(SoundType.WOOD).noOcclusion().lightLevel(s -> 6));
			case "vent" -> new fr.achedon12.matriochka.block.AirVent(p.strength(1.8f, 6f).sound(SoundType.BASALT).lightLevel(s -> 6).requiresCorrectToolForDrops());
			default -> {
				BlockBehaviour.Properties q = switch (d.style()) {
					case "moss" -> p.strength(0.6f).sound(SoundType.MOSS);
					case "sand" -> p.strength(0.5f).sound(SoundType.SAND);
					case "glow" -> p.strength(0.4f).sound(SoundType.GLASS).lightLevel(s -> 13);
					case "glass" -> p.strength(0.4f).sound(SoundType.GLASS).noOcclusion();
					case "wood" -> p.strength(2f).sound(SoundType.WOOD);
					case "brick_unbreakable" -> p.strength(-1f, 3600000f);
					case "ore", "ore_big" -> p.strength(3.5f, 3f).requiresCorrectToolForDrops();
					case "lacquer" -> p.strength(1.5f).sound(SoundType.WOOD);
					default -> p.strength(1.8f, 6f).requiresCorrectToolForDrops();
				};
				yield new Block(q);
			}
		};
	}

	// ---------------------------------------------------------------- items
	private static final Map<String, ArmorMaterial> MATERIALS = new HashMap<>();

	private static ArmorMaterial material(Defs.ItemDef d) {
		if (d.set().equals("matriarch")) return MATERIALS.computeIfAbsent(d.set(), s -> matriarchMaterial());
		return MATERIALS.computeIfAbsent(d.set(), s -> {
			float[] g = Defs.GEAR[d.world()];
			int total = (int) g[1];
			int helmet = Math.round(total * 0.18f), chest = Math.round(total * 0.38f), boots = Math.round(total * 0.16f);
			int legs = total - helmet - chest - boots;
			Map<ArmorType, Integer> def = new EnumMap<>(ArmorType.class);
			def.put(ArmorType.HELMET, helmet);
			def.put(ArmorType.CHESTPLATE, chest);
			def.put(ArmorType.LEGGINGS, legs);
			def.put(ArmorType.BOOTS, boots);
			def.put(ArmorType.BODY, chest);
			ResourceKey<EquipmentAsset> asset = ResourceKey.create(EquipmentAssets.ROOT_ID, Matriochka.id(s));
			return new ArmorMaterial(20 + d.world() * 6, def, 12, SoundEvents.ARMOR_EQUIP_NETHERITE, g[2] / 4f, 0.02f * d.world(),
				TagKey.create(Registries.ITEM, Matriochka.id("repairs/" + s)), asset);
		});
	}

	/**
	 * The Matriarch Armour's material: just above the Artisan's (tools/content.py MATRIARCH), the same share of the
	 * armour per piece, more toughness and a little more knockback resistance.
	 */
	private static ArmorMaterial matriarchMaterial() {
		int total = Content.MATRIARCH_ARMOR;
		int helmet = Math.round(total * 0.18f), chest = Math.round(total * 0.38f), boots = Math.round(total * 0.16f);
		Map<ArmorType, Integer> def = new EnumMap<>(ArmorType.class);
		def.put(ArmorType.HELMET, helmet);
		def.put(ArmorType.CHESTPLATE, chest);
		def.put(ArmorType.LEGGINGS, total - helmet - chest - boots);
		def.put(ArmorType.BOOTS, boots);
		def.put(ArmorType.BODY, chest);
		return new ArmorMaterial(Content.MATRIARCH_DURABILITY, def, Content.MATRIARCH_ENCHANT, SoundEvents.ARMOR_EQUIP_GOLD,
			Content.MATRIARCH_TOUGHNESS / 4f, Content.MATRIARCH_KNOCKBACK,
			TagKey.create(Registries.ITEM, Matriochka.id("repairs/matriarch")), ResourceKey.create(EquipmentAssets.ROOT_ID, Matriochka.id("matriarch")));
	}

	/** A snorkel helmet's material: little durability (it breaks easily), the tier's armor and toughness. */
	private static ArmorMaterial snorkelMaterial(String id) {
		Defs.SnorkelDef s = fr.achedon12.matriochka.rules.Snorkel.def(id);
		Map<ArmorType, Integer> def = new EnumMap<>(ArmorType.class);
		for (ArmorType t : ArmorType.values()) def.put(t, s.armor());
		return new ArmorMaterial(s.durability(), def, 10, SoundEvents.ARMOR_EQUIP_TURTLE, s.toughness(), 0f,
			TagKey.create(Registries.ITEM, Matriochka.id("repairs/" + id)), ResourceKey.create(EquipmentAssets.ROOT_ID, Matriochka.id(id)));
	}

	private static ToolMaterial tool(int world) {
		return new ToolMaterial(world >= 5 ? BlockTags.INCORRECT_FOR_NETHERITE_TOOL : BlockTags.INCORRECT_FOR_IRON_TOOL,
			300 + world * 180, 7f + world * 0.6f, 0f, 12, TagKey.create(Registries.ITEM, Matriochka.id("repairs/world_" + world)));
	}

	private static Item makeItem(Defs.ItemDef d, Item.Properties p) {
		Rarity r = switch (d.rarity()) {
			case "rare" -> Rarity.UNCOMMON;
			case "epic" -> Rarity.RARE;
			case "legendary" -> Rarity.EPIC;
			default -> Rarity.COMMON;
		};
		p.rarity(r);
		switch (d.kind()) {
			case "weapon" -> {
				float dmg = Defs.GEAR[d.world()][0];
				p.sword(tool(d.world()), dmg - 1f, -2.4f);
			}
			case "armor" -> {
				ArmorType t = switch (d.piece()) {
					case "helmet" -> ArmorType.HELMET;
					case "chestplate" -> ArmorType.CHESTPLATE;
					case "leggings" -> ArmorType.LEGGINGS;
					default -> ArmorType.BOOTS;
				};
				ArmorMaterial m = material(d);
				p.humanoidArmor(m, t);
				float hp = Defs.GEAR[d.world()][3];
				float share = switch (t) { case CHESTPLATE -> 0.4f; case LEGGINGS -> 0.3f; case HELMET -> 0.15f; default -> 0.15f; };
				// the Matriarch: one more heart per piece than the Artisan's set
				float extra = d.set().equals("matriarch") ? Content.MATRIARCH_EXTRA_HEALTH : 0f;
				if (hp > 0) {
					ItemAttributeModifiers mods = m.createAttributes(t).withModifierAdded(Attributes.MAX_HEALTH,
						new AttributeModifier(Matriochka.id("armor_health_" + d.piece()), Math.round(hp * share) + extra, AttributeModifier.Operation.ADD_VALUE),
						EquipmentSlotGroup.bySlot(t.getSlot()));
					p.attributes(mods);
				}
			}
			case "drill" -> p.pickaxe(tool(2), 1f, -2.8f);
			case "snorkel" -> p.humanoidArmor(snorkelMaterial(d.id()), ArmorType.HELMET);
			case "mask" -> p.stacksTo(1).component(DataComponents.EQUIPPABLE, Equippable.builder(EquipmentSlot.HEAD)
				.setAsset(ResourceKey.create(EquipmentAssets.ROOT_ID, Matriochka.id(d.id()))).setEquipSound(SoundEvents.ARMOR_EQUIP_LEATHER).build());
			case "boots" -> p.stacksTo(1).component(DataComponents.EQUIPPABLE, Equippable.builder(EquipmentSlot.FEET)
				.setAsset(ResourceKey.create(EquipmentAssets.ROOT_ID, Matriochka.id(d.id()))).setEquipSound(SoundEvents.ARMOR_EQUIP_IRON).build());
			case "food" -> p.food(new FoodProperties.Builder().nutrition(6).saturationModifier(0.8f).alwaysEdible().build());
			case "core" -> p.stacksTo(1).fireResistant();
			case "offering" -> p.stacksTo(16).fireResistant();
			case "seed" -> p.stacksTo(16).fireResistant();
			case "doll", "guide", "secret", "glider", "hook", "lantern", "sonar", "hourglass", "thruster", "tool" -> p.stacksTo(1);
			case "consumable", "anchor" -> p.stacksTo(16);
			default -> {}
		}
		if (d.id().equals("cracked_doll") || d.id().equals("last_doll_key")) p.fireResistant();
		if (d.kind().equals("armor") && d.set().equals("matriarch")) return new fr.achedon12.matriochka.item.MatriarchArmor(d, p);
		Item replay = fr.achedon12.matriochka.item.ReplayGear.make(d, p);
		if (replay != null) return replay;
		return new MatrioItem(d, p);
	}

	public static void register() {
		for (Defs.BlockDef d : Content.BLOCKS) {
			BlockBehaviour.Properties p = BlockBehaviour.Properties.of().setId(bkey(d.id())).mapColor(MapColor.COLOR_RED);
			Block b = Registry.register(BuiltInRegistries.BLOCK, bkey(d.id()), makeBlock(d, p));
			BLOCKS.put(d.id(), b);
			if (!d.kind().equals("planted_seed") && !d.kind().equals("time_sprout")) {
				Item.Properties ip = new Item.Properties().setId(ikey(d.id())).useBlockDescriptionPrefix();
				Item item = Registry.register(BuiltInRegistries.ITEM, ikey(d.id()), new BlockItem(b, ip) {
					@Override
					public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay disp, Consumer<Component> out, net.minecraft.world.item.TooltipFlag flag) {
						String key = "block.matriochka." + d.id() + ".desc";
						if (net.minecraft.locale.Language.getInstance().has(key))
							for (String line : MatrioItem.wrap(net.minecraft.locale.Language.getInstance().getOrDefault(key), MatrioItem.WRAP))
								out.accept(Component.literal(line).withStyle(net.minecraft.ChatFormatting.GRAY));
						if (d.kind().equals("nesting_chest")) fr.achedon12.matriochka.block.NestingChests.appendTooltip(stack, out);
					}
				});
				ITEMS.put(d.id(), item);
				IDS.put(item, d.id());
			}
		}
		for (Defs.ItemDef d : Content.ITEMS) {
			Item item = Registry.register(BuiltInRegistries.ITEM, ikey(d.id()), makeItem(d, new Item.Properties().setId(ikey(d.id()))));
			ITEMS.put(d.id(), item);
			IDS.put(item, d.id());
			DEFS.put(d.id(), d);
		}
		BE_DATA = Registry.register(BuiltInRegistries.BLOCK_ENTITY_TYPE, Matriochka.id("data"),
			FabricBlockEntityTypeBuilder.<DataBlockEntity>create((pos, state) -> new DataBlockEntity(BE_DATA, pos, state), BLOCKS.values().toArray(new Block[0])).build());
		BE_CRADLE = Registry.register(BuiltInRegistries.BLOCK_ENTITY_TYPE, Matriochka.id("nesting_cradle"),
			FabricBlockEntityTypeBuilder.create(fr.achedon12.matriochka.block.CradleBlockEntity::new, block("nesting_cradle")).build());

		for (Defs.MobDef d : Content.MOBS) {
			ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Matriochka.id(d.id()));
			// sea creatures spawn in open water rather than on the ground
			EntityType.Builder<MatrioMob> b = (d.aquatic()
				? FabricEntityType.Builder.<MatrioMob>createMob((t, l) -> new MatrioMob(t, l, d), MobCategory.MONSTER,
					m -> m.spawnPlacement(SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, MatrioMob::checkAquaticSpawn))
				: EntityType.Builder.<MatrioMob>of((t, l) -> new MatrioMob(t, l, d), MobCategory.MONSTER))
				.sized(Math.min(2.5f, d.width() * d.scale()), Math.min(5f, d.height() * d.scale())).clientTrackingRange(8);
			if (d.world() == 2 || d.behavior().equals("lava_heat")) b = b.fireImmune();
			EntityType<MatrioMob> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, key, b.build(key));
			FabricDefaultAttributeRegistry.register(type, MatrioMob.attributes(d));
			MatrioMob.DEFS.put(type, d);
			ENTITIES.put(d.id(), type);
		}
		for (Defs.BossDef d : Content.BOSSES) {
			ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Matriochka.id(d.id()));
			EntityType<MatrioBoss> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, key,
				EntityType.Builder.<MatrioBoss>of((t, l) -> new MatrioBoss(t, l, d), MobCategory.MONSTER)
					.sized(Math.min(4f, d.width() * d.scale()), Math.min(8f, d.height() * d.scale())).fireImmune().clientTrackingRange(12).build(key));
			FabricDefaultAttributeRegistry.register(type, MatrioBoss.attributes(d));
			ENTITIES.put(d.id(), type);
		}
		for (Defs.CritterDef d : Content.CRITTERS) {
			ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Matriochka.id(d.id()));
			EntityType<MatrioCritter> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, key,
				FabricEntityType.Builder.<MatrioCritter>createMob(MatrioCritter::new, MobCategory.WATER_AMBIENT,
						m -> m.spawnPlacement(SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, MatrioCritter::checkSpawn))
					.sized(d.width(), Math.max(0.3f, d.height())).clientTrackingRange(6).build(key));
			MatrioCritter.DEFS.put(type, d);
			FabricDefaultAttributeRegistry.register(type, MatrioCritter.attributes(d));
			ENTITIES.put(d.id(), type);
		}
		for (Defs.NpcDef d : Content.PEOPLES) {
			ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Matriochka.id(d.id()));
			EntityType<MatrioNpc> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, key,
				EntityType.Builder.<MatrioNpc>of((t, l) -> new MatrioNpc(t, l, d), MobCategory.CREATURE).sized(0.6f, 1.95f).clientTrackingRange(10).build(key));
			FabricDefaultAttributeRegistry.register(type, MatrioNpc.attributes());
			ENTITIES.put(d.id(), type);
		}

		Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, Matriochka.id("main"), FabricCreativeModeTab.builder()
			.title(Component.translatable("itemGroup.matriochka.main"))
			.icon(() -> new ItemStack(item("life_doll")))
			.displayItems((params, out) -> {
				for (Defs.ItemDef d : Content.ITEMS) if (d.world() == 0 || d.kind().equals("core") || d.kind().equals("seed")) out.accept(item(d.id()));
				for (Defs.BlockDef d : Content.BLOCKS) if (d.world() == 0 && ITEMS.containsKey(d.id())) out.accept(item(d.id()));
			}).build());
		Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, Matriochka.id("worlds"), FabricCreativeModeTab.builder()
			.title(Component.translatable("itemGroup.matriochka.worlds"))
			.icon(() -> new ItemStack(item("seed_1")))
			.displayItems((params, out) -> {
				for (int w = 1; w <= 10; w++) {
					for (Defs.BlockDef d : Content.BLOCKS) if (d.world() == w && ITEMS.containsKey(d.id())) out.accept(item(d.id()));
					for (Defs.ItemDef d : Content.ITEMS) if (d.world() == w && !d.kind().equals("core") && !d.kind().equals("seed")) out.accept(item(d.id()));
				}
			}).build());
	}
}
