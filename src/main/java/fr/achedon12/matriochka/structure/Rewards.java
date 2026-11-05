package fr.achedon12.matriochka.structure;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.tags.EnchantmentTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LadderBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.LecternBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.entity.SpawnerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Rewards by role, placed at the anchors the builders marked: a guarded loot room for combat, two to four hidden
 * chests for exploration, a reading room with the Journal page for story, the hidden doll behind a puzzle for secret,
 * the world's people for utility. Loot comes in three tiers drawn from the world's own items plus vanilla goods.
 */
public final class Rewards {
	public static final int COMMON = 0, RARE = 1, VAULT = 2;

	private Rewards() {}

	public static void apply(Kit k) {
		// every draw from the piece random happens here, unconditionally, so all chunks agree
		int n = 2 + k.r.nextInt(3);
		List<Kit.Mark> pool = new ArrayList<>(k.hidden);
		List<Kit.Mark> chosen = new ArrayList<>();
		while (!pool.isEmpty() && chosen.size() < n) chosen.add(pool.remove(k.r.nextInt(pool.size())));
		switch (k.role) {
			case "combat" -> {
				Kit.Mark g = k.guard != null ? k.guard : new Kit.Mark(k.o.above(), Direction.SOUTH, false);
				chest(k, g.pos(), g.facing(), g.flipped(), k.large() ? VAULT : RARE, false, false);
				if (!k.small()) {
					Direction side = g.facing().getClockWise();
					chest(k, g.pos().relative(side, 1), g.facing(), g.flipped(), COMMON, false, false);
				}
				List<Kit.Mark> sp = new ArrayList<>(k.spawners);
				if (sp.isEmpty()) {
					Direction side = g.facing().getClockWise();
					sp.add(new Kit.Mark(g.pos().relative(side, 3), g.facing(), g.flipped()));
					sp.add(new Kit.Mark(g.pos().relative(side, -3), g.facing(), g.flipped()));
				}
				int max = 1 + k.scale();
				for (int i = 0; i < sp.size() && i < max; i++) spawner(k, sp.get(i).pos());
				if (!chosen.isEmpty()) chest(k, chosen.get(0).pos(), chosen.get(0).facing(), chosen.get(0).flipped(), COMMON, false, false);
			}
			case "exploration" -> {
				for (int i = 0; i < chosen.size(); i++) {
					Kit.Mark m = chosen.get(i);
					int tier = (i == 0 && !k.small()) || (i == 1 && k.large()) ? RARE : COMMON;
					chest(k, m.pos(), m.facing(), m.flipped(), tier, false, false);
				}
				if (chosen.isEmpty()) chest(k, k.o.above(), Direction.SOUTH, false, RARE, false, false);
			}
			case "story" -> {
				Kit.Mark m = k.reading != null ? k.reading : new Kit.Mark(k.o.above(), Direction.SOUTH, false);
				readingNook(k, m);
				chest(k, m.pos(), m.facing(), m.flipped(), RARE, true, false);
				if (!chosen.isEmpty()) chest(k, chosen.get(0).pos(), chosen.get(0).facing(), chosen.get(0).flipped(), COMMON, false, false);
			}
			case "utility" -> {
				Kit.Mark m = k.npc != null ? k.npc : new Kit.Mark(k.o.offset(1, 1, 1), Direction.SOUTH, false);
				npc(k, m.pos());
				if (!chosen.isEmpty()) chest(k, chosen.get(0).pos(), chosen.get(0).facing(), chosen.get(0).flipped(), COMMON, false, false);
			}
			case "secret" -> {
				Kit.Mark m = k.secret;
				if (m == null) m = hiddenCellar(k, k.o);
				chest(k, m.pos(), m.facing(), m.flipped(), VAULT, true, true);
				if (!chosen.isEmpty()) chest(k, chosen.get(0).pos(), chosen.get(0).facing(), chosen.get(0).flipped(), COMMON, false, false);
			}
			default -> {}
		}
	}

	// ---------------------------------------------------------------- rooms placed by the rewards
	private static void putM(Kit k, BlockPos pos, BlockState s, boolean flipped) {
		k.put(pos, k.wet(flipped ? Kit.flipState(s) : s));
	}

	/** Lectern, two bookshelf stacks, candles and a stool around the page chest; the chest stands against the wall. */
	static void readingNook(Kit k, Kit.Mark m) {
		Direction f = m.facing(), side = f.getClockWise();
		Direction up = m.flipped() ? Direction.DOWN : Direction.UP;
		BlockPos c = m.pos();
		for (int s : new int[] {-1, 1}) {
			BlockPos sh = c.relative(side, s);
			putM(k, sh, Blocks.BOOKSHELF.defaultBlockState(), m.flipped());
			putM(k, sh.relative(up), Blocks.CHISELED_BOOKSHELF.defaultBlockState().setValue(net.minecraft.world.level.block.ChiseledBookShelfBlock.FACING, f), m.flipped());
			candlesAt(k, sh.relative(up, 2), m.flipped());
		}
		putM(k, c.relative(up), k.p.light, m.flipped());
		BlockPos lec = c.relative(f, 2);
		putM(k, lec, Blocks.LECTERN.defaultBlockState().setValue(LecternBlock.FACING, f), m.flipped());
		putM(k, lec.relative(side, 1), Kit.stairOf(k.p.woodStair, side, false), m.flipped());
		putM(k, lec.relative(side, -1), k.p.fence, m.flipped());
		putM(k, lec.relative(side, -1).relative(up), Kit.slabOf(k.p.woodSlab, false), m.flipped());
		candlesAt(k, lec.relative(side, -1).relative(up, 2), m.flipped());
		BlockPos ceil = c.relative(f, 1).relative(up, 3);
		if (k.inside(ceil) && k.lvl.getBlockState(ceil.relative(up)).isSolid()) {
			BlockState l = k.p.lantern.hasProperty(LanternBlock.HANGING) ? k.p.lantern.setValue(LanternBlock.HANGING, true) : k.p.lantern;
			putM(k, ceil, l, m.flipped());
		}
	}

	private static void candlesAt(Kit k, BlockPos pos, boolean flipped) {
		if (k.p.underwater) {
			putM(k, pos, Blocks.SEA_PICKLE.defaultBlockState(), flipped);
			return;
		}
		putM(k, pos, Blocks.CANDLE.defaultBlockState().setValue(net.minecraft.world.level.block.CandleBlock.CANDLES, 3)
			.setValue(net.minecraft.world.level.block.CandleBlock.LIT, true), flipped);
	}

	/**
	 * Fallback secret: a sealed chamber under the floor, entered by breaking the one odd tile in a rosette of inlay.
	 * Returns the chest anchor.
	 */
	static Kit.Mark hiddenCellar(Kit k, BlockPos floor) {
		BlockPos c = floor.below(5);
		for (int dx = -3; dx <= 3; dx++)
			for (int dz = -3; dz <= 3; dz++)
				for (int dy = -1; dy <= 3; dy++) {
					BlockPos q = c.offset(dx, dy, dz);
					boolean edge = Math.abs(dx) == 3 || Math.abs(dz) == 3 || dy == -1 || dy == 3;
					k.put(q, edge ? (dy == -1 ? k.p.inlay : k.p.alt) : k.p.fill);
				}
		for (int dy = 4; dy >= 0; dy--) k.put(floor.offset(2, -dy, 2), Blocks.LADDER.defaultBlockState().setValue(LadderBlock.FACING, Direction.NORTH));
		k.put(floor.offset(2, 0, 3), k.p.alt);
		for (int dx = 1; dx <= 3; dx++)
			for (int dz = 1; dz <= 3; dz++) k.put(floor.offset(dx, 0, dz), (dx == 2 && dz == 2) ? k.p.cracked : k.p.inlay2);
		k.put(c.offset(-2, 0, -2), k.p.light);
		k.put(c.offset(2, 0, -2), k.p.light);
		k.put(c.offset(0, 0, -2), k.p.cap);
		k.put(c.offset(0, 1, -2), k.p.accent);
		return new Kit.Mark(c, Direction.SOUTH, false);
	}

	// ---------------------------------------------------------------- spawners, people
	static void spawner(Kit k, BlockPos p) {
		if (!k.inside(p)) return;
		var mobs = Content.MOBS.stream().filter(m -> m.world() == k.world && !m.elite()).toList();
		if (mobs.isEmpty()) return;
		RandomSource rr = RandomSource.create(k.hash(p.getX(), p.getY(), p.getZ(), 101));
		k.lvl.setBlock(p, Blocks.SPAWNER.defaultBlockState(), 2);
		if (k.lvl.getBlockEntity(p) instanceof SpawnerBlockEntity sp) sp.setEntityId(ModContent.entity(mobs.get(rr.nextInt(mobs.size())).id()), rr);
	}

	static void npc(Kit k, BlockPos p) {
		for (Defs.NpcDef d : Content.PEOPLES) {
			if (d.world() != k.world) continue;
			if (!k.inside(p)) return;
			var e = ModContent.entity(d.id()).create(k.lvl.getLevel(), EntitySpawnReason.STRUCTURE);
			if (e != null) {
				e.setPos(p.getX() + 0.5, p.getY(), p.getZ() + 0.5);
				if (e instanceof net.minecraft.world.entity.Mob m) m.setPersistenceRequired();
				k.lvl.addFreshEntity(e);
			}
		}
	}

	// ---------------------------------------------------------------- chests
	private static final Set<String> COMMON_KINDS = Set.of("resource", "food", "consumable");
	private static final Set<String> RARE_KINDS = Set.of("resource", "gem", "ingot", "dust", "consumable", "key", "tool", "thread");
	private static final Set<String> GEAR_KINDS = Set.of("weapon", "armor", "boots", "mask", "glider", "hook", "lantern", "sonar", "drill",
		"thruster", "anchor", "hourglass");

	static void chest(Kit k, BlockPos p, Direction f, boolean flipped, int tier, boolean page, boolean doll) {
		if (!k.inside(p)) return;
		BlockState st = Kit.facing(Blocks.CHEST.defaultBlockState(), f);
		k.put(p, st);
		if (!(k.lvl.getBlockEntity(p) instanceof ChestBlockEntity chest)) return;
		RandomSource r = RandomSource.create(k.hash(p.getX(), p.getY(), p.getZ(), 97));
		fill(k, chest, tier, r);
		int world = k.world;
		long seed = k.seed;
		if (world == 0) chest.setItem(4, new ItemStack(Items.IRON_INGOT, 3 + r.nextInt(5)));
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

	private static List<Defs.ItemDef> items(int world, Set<String> kinds, boolean rare) {
		return Content.ITEMS.stream().filter(i -> i.world() == world && kinds.contains(i.kind())
			&& (rare ? !i.rarity().equals("common") && !i.rarity().equals("none") : i.rarity().equals("common"))).toList();
	}

	private static void add(ChestBlockEntity c, RandomSource r, ItemStack s) {
		if (s.isEmpty()) return;
		s.setCount(Math.max(1, Math.min(s.getCount(), s.getMaxStackSize())));
		for (int tries = 0; tries < 40; tries++) {
			int slot = r.nextInt(27);
			if (slot == 13 || slot == 22 || slot == 4) continue;
			if (c.getItem(slot).isEmpty()) {
				c.setItem(slot, s);
				return;
			}
		}
	}

	private static ItemStack mod(Defs.ItemDef d, int n) {
		return new ItemStack(ModContent.item(d.id()), n);
	}

	private static int between(RandomSource r, int lo, int hi) {
		return lo + r.nextInt(Math.max(1, hi - lo + 1));
	}

	static void fill(Kit k, ChestBlockEntity c, int tier, RandomSource r) {
		int w = k.world;
		double mult = 1.0 + w / 5.0;
		List<Defs.ItemDef> common = items(w, COMMON_KINDS, false);
		List<Defs.ItemDef> rare = items(w, RARE_KINDS, true);
		List<Defs.ItemDef> gear = Content.ITEMS.stream().filter(i -> i.world() == w && GEAR_KINDS.contains(i.kind()) && !i.rarity().equals("legendary")).toList();
		if (rare.isEmpty()) rare = common;

		int nc = tier == COMMON ? between(r, 3, 5) : tier == RARE ? 2 : between(r, 1, 2);
		for (int i = 0; i < nc && !common.isEmpty(); i++) {
			Defs.ItemDef d = common.get(r.nextInt(common.size()));
			add(c, r, mod(d, d.kind().equals("resource") ? between(r, 3, 10) : between(r, 1, 4)));
		}
		int nr = tier == COMMON ? (r.nextFloat() < 0.35f ? 1 : 0) : tier == RARE ? between(r, 2, 3) : between(r, 3, 5);
		for (int i = 0; i < nr && !rare.isEmpty(); i++) {
			Defs.ItemDef d = rare.get(r.nextInt(rare.size()));
			int n = d.kind().equals("key") || d.kind().equals("tool") ? 1 : tier == VAULT ? between(r, 2, 5) : between(r, 1, 3);
			add(c, r, mod(d, n));
		}
		// vanilla goods
		add(c, r, new ItemStack(food(w), between(r, 2, 6)));
		switch (tier) {
			case COMMON -> {
				add(c, r, new ItemStack(Items.IRON_NUGGET, between(r, 3, 12)));
				Item misc = w == 7 ? Items.PRISMARINE_SHARD : r.nextBoolean() ? Items.TORCH : Items.COAL;
				add(c, r, new ItemStack(misc, between(r, 3, 10)));
				if (r.nextFloat() < 0.4f) add(c, r, new ItemStack(r.nextBoolean() ? Items.ARROW : Items.STRING, between(r, 4, 12)));
				if (r.nextFloat() < 0.3f) add(c, r, new ItemStack(Items.IRON_INGOT, between(r, 1, 3)));
			}
			case RARE -> {
				add(c, r, new ItemStack(Items.IRON_INGOT, (int) (between(r, 2, 6) * mult)));
				add(c, r, new ItemStack(Items.GOLD_INGOT, (int) (between(r, 1, 4) * mult)));
				if (r.nextFloat() < 0.6f) add(c, r, new ItemStack(Items.EMERALD, (int) (between(r, 1, 4) * mult)));
				if (r.nextFloat() < 0.45f) add(c, r, book(k, r, between(r, 8, 18)));
				if (r.nextFloat() < 0.35f) add(c, r, new ItemStack(Items.EXPERIENCE_BOTTLE, between(r, 2, 6)));
				if (r.nextFloat() < 0.3f) add(c, r, new ItemStack(Items.GOLDEN_CARROT, between(r, 2, 5)));
				add(c, r, flavour(w, r, false));
			}
			default -> {
				add(c, r, new ItemStack(Items.GOLD_INGOT, (int) (between(r, 4, 9) * mult)));
				add(c, r, new ItemStack(Items.EMERALD, (int) (between(r, 3, 8) * mult)));
				add(c, r, new ItemStack(Items.DIAMOND, between(r, 1, 2 + w / 4)));
				add(c, r, book(k, r, between(r, 20, 30)));
				if (r.nextFloat() < 0.5f) add(c, r, book(k, r, between(r, 15, 30)));
				add(c, r, new ItemStack(Items.GOLDEN_APPLE, between(r, 1, 2)));
				add(c, r, new ItemStack(Items.EXPERIENCE_BOTTLE, between(r, 4, 10)));
				add(c, r, flavour(w, r, true));
				if (!gear.isEmpty() && r.nextFloat() < 0.3f) add(c, r, new ItemStack(ModContent.item(gear.get(r.nextInt(gear.size())).id())));
				if (w >= 7 && r.nextFloat() < 0.08f) add(c, r, new ItemStack(Items.ENCHANTED_GOLDEN_APPLE));
			}
		}
	}

	private static Item food(int w) {
		return switch (w) {
			case 1 -> Items.GLOW_BERRIES;
			case 2 -> Items.BAKED_POTATO;
			case 3 -> Items.BREAD;
			case 4 -> Items.APPLE;
			case 5 -> Items.MUSHROOM_STEW;
			case 6 -> Items.CHORUS_FRUIT;
			case 7 -> Items.COOKED_COD;
			case 8 -> Items.PUMPKIN_PIE;
			case 9 -> Items.COOKED_BEEF;
			case 10 -> Items.COOKIE;
			default -> Items.BREAD;
		};
	}

	/** One item that belongs to the world's theme. */
	private static ItemStack flavour(int w, RandomSource r, boolean vault) {
		return switch (w) {
			case 1 -> new ItemStack(vault ? Items.EMERALD : Items.SWEET_BERRIES, between(r, 2, 6));
			case 2 -> new ItemStack(vault ? Items.NETHERITE_SCRAP : Items.BLAZE_POWDER, vault ? 1 : between(r, 2, 5));
			case 3 -> new ItemStack(vault ? Items.NAME_TAG : Items.ARROW, vault ? 1 : between(r, 8, 16));
			case 4 -> new ItemStack(vault ? Items.SPYGLASS : Items.COPPER_INGOT, vault ? 1 : between(r, 4, 10));
			case 5 -> new ItemStack(vault ? Items.ECHO_SHARD : Items.GLOWSTONE_DUST, between(r, 2, 6));
			case 6 -> new ItemStack(vault ? Items.SHULKER_SHELL : Items.ENDER_PEARL, between(r, 1, 3));
			case 7 -> new ItemStack(vault ? (r.nextFloat() < 0.25f ? Items.HEART_OF_THE_SEA : Items.NAUTILUS_SHELL) : Items.PRISMARINE_CRYSTALS, vault ? 1 : between(r, 3, 8));
			case 8 -> new ItemStack(vault ? Items.CLOCK : Items.HONEY_BOTTLE, vault ? 1 : between(r, 1, 3));
			case 9 -> new ItemStack(vault ? Items.TOTEM_OF_UNDYING : Items.LEAD, 1);
			case 10 -> new ItemStack(vault ? Items.GOLD_BLOCK : Items.GOLD_NUGGET, vault ? between(r, 1, 3) : between(r, 6, 18));
			default -> new ItemStack(Items.IRON_INGOT, 2);
		};
	}

	private static ItemStack book(Kit k, RandomSource r, int cost) {
		try {
			var reg = k.lvl.registryAccess().lookupOrThrow(Registries.ENCHANTMENT);
			return EnchantmentHelper.enchantItem(r, new ItemStack(Items.BOOK), cost, k.lvl.registryAccess(), reg.get(EnchantmentTags.ON_RANDOM_LOOT));
		} catch (RuntimeException e) {
			return new ItemStack(Items.BOOK, 2);
		}
	}
}
