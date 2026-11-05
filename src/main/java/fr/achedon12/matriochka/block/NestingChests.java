package fr.achedon12.matriochka.block;

import fr.achedon12.matriochka.content.ModContent;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.ContainerUser;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemContainerContents;
import net.minecraft.world.level.block.Block;

/**
 * Nesting chests come in three sizes, three rows, two rows and one row, and each one holds the smaller ones with their
 * contents. A chest can be given a sorting rule (sneak and use it with an empty hand): when its owner closes a chest,
 * every item that matches the rule of a smaller chest inside it slides into that chest, and on down the nest.
 */
public final class NestingChests {
	/** Sorting rules, in the order sneaking cycles through them. */
	public static final String[] RULES = {"any", "blocks", "gear", "food", "resources"};
	private static final Map<DataBlockEntity, SimpleContainer> OPEN = new WeakHashMap<>();

	private NestingChests() {}

	/** Rows of a nesting chest block or item, 0 for anything else. */
	public static int rows(Block block) {
		if (block == ModContent.block("nesting_chest")) return 3;
		if (block == ModContent.block("nesting_chest_medium")) return 2;
		if (block == ModContent.block("nesting_chest_little")) return 1;
		return 0;
	}

	public static int rows(ItemStack stack) {
		return stack.getItem() instanceof BlockItem bi ? rows(bi.getBlock()) : 0;
	}

	/** The sorting category of an item. */
	public static String category(ItemStack stack) {
		if (stack.has(DataComponents.FOOD)) return "food";
		if (stack.getMaxStackSize() == 1 && (stack.isDamageableItem() || stack.has(DataComponents.EQUIPPABLE) || stack.has(DataComponents.TOOL) || stack.has(DataComponents.WEAPON))) return "gear";
		if (stack.getItem() instanceof BlockItem) return "blocks";
		return "resources";
	}

	public static String rule(CompoundTag data) {
		return data.getStringOr("sort", "any");
	}

	public static String rule(ItemStack stack) {
		CustomData cd = stack.get(DataComponents.CUSTOM_DATA);
		return cd == null ? "any" : cd.copyTag().getStringOr("sort", "any");
	}

	/** A chest of this many rows may hold that stack: anything but a nesting chest as large as itself or larger. */
	public static boolean mayHold(int rows, ItemStack stack) {
		int r = rows(stack);
		return r == 0 || r < rows;
	}

	// ---------------------------------------------------------------- block <-> item
	/** The chest as an item, carrying its contents and its sorting rule. */
	public static ItemStack toItem(Block block, CompoundTag data, HolderLookup.Provider regs) {
		ItemStack stack = new ItemStack(block);
		int size = rows(block) * 9;
		NonNullList<ItemStack> items = ContainerTags.load(data, regs, size);
		boolean any = false;
		for (ItemStack s : items) any |= !s.isEmpty();
		if (any) stack.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(items));
		String rule = rule(data);
		if (!rule.equals("any")) {
			CompoundTag t = new CompoundTag();
			t.putString("sort", rule);
			stack.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		}
		return stack;
	}

	/** Restores the contents and the sorting rule of a placed chest from its item. */
	public static void fromItem(ItemStack stack, CompoundTag data, HolderLookup.Provider regs, int rows) {
		NonNullList<ItemStack> items = contents(stack, rows * 9);
		ContainerTags.save(data, regs, items);
		String rule = rule(stack);
		if (rule.equals("any")) data.remove("sort");
		else data.putString("sort", rule);
	}

	public static NonNullList<ItemStack> contents(ItemStack stack, int size) {
		NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
		ItemContainerContents c = stack.get(DataComponents.CONTAINER);
		if (c != null) {
			NonNullList<ItemStack> all = NonNullList.withSize(Math.max(size, c.size()), ItemStack.EMPTY);
			c.copyInto(all);
			for (int i = 0; i < size; i++) items.set(i, all.get(i));
		}
		return items;
	}

	private static void setContents(ItemStack stack, List<ItemStack> items) {
		boolean any = false;
		for (ItemStack s : items) any |= !s.isEmpty();
		if (any) stack.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(items));
		else stack.remove(DataComponents.CONTAINER);
	}

	// ---------------------------------------------------------------- sorting
	/**
	 * Moves every item that matches the rule of a smaller chest among these slots into that chest, then sorts inside the
	 * smaller chests too. Returns the number of items moved.
	 */
	public static int sort(List<ItemStack> slots) {
		int moved = 0;
		List<ItemStack> chests = new ArrayList<>();
		for (ItemStack s : slots) if (rows(s) > 0) chests.add(s);
		if (chests.isEmpty()) return 0;
		for (ItemStack chest : chests) {
			String rule = rule(chest);
			int size = rows(chest) * 9;
			NonNullList<ItemStack> inner = contents(chest, size);
			if (!rule.equals("any")) {
				for (int i = 0; i < slots.size(); i++) {
					ItemStack s = slots.get(i);
					if (s.isEmpty() || rows(s) > 0 || !category(s).equals(rule)) continue;
					int before = s.getCount();
					insert(inner, s);
					moved += before - s.getCount();
				}
			}
			moved += sort(inner);
			setContents(chest, inner);
		}
		return moved;
	}

	/** Merges a stack into a list of slots, shrinking it by what fits. */
	private static void insert(List<ItemStack> slots, ItemStack s) {
		for (int i = 0; i < slots.size() && !s.isEmpty(); i++) {
			ItemStack t = slots.get(i);
			if (!t.isEmpty() && ItemStack.isSameItemSameComponents(t, s) && t.getCount() < t.getMaxStackSize()) {
				int k = Math.min(s.getCount(), t.getMaxStackSize() - t.getCount());
				t.grow(k);
				s.shrink(k);
			}
		}
		for (int i = 0; i < slots.size() && !s.isEmpty(); i++) {
			if (slots.get(i).isEmpty()) {
				slots.set(i, s.copy());
				s.setCount(0);
			}
		}
	}

	// ---------------------------------------------------------------- opening
	/** Opens a placed chest. Everyone looking into the same chest shares one container, saved on every change. */
	public static void open(ServerPlayer player, ServerLevel level, DataBlockEntity be, int rows) {
		SimpleContainer c = OPEN.computeIfAbsent(be, k -> container(level, be, rows));
		MenuType<ChestMenu> type = rows == 1 ? MenuType.GENERIC_9x1 : rows == 2 ? MenuType.GENERIC_9x2 : MenuType.GENERIC_9x3;
		player.openMenu(new SimpleMenuProvider((id, inv, p) -> new Menu(type, id, inv, c, rows), be.getBlockState().getBlock().getName()));
		level.playSound(null, be.getBlockPos(), SoundEvents.CHEST_OPEN, SoundSource.BLOCKS, 0.8f, 1.1f + (3 - rows) * 0.15f);
	}

	private static SimpleContainer container(ServerLevel level, DataBlockEntity be, int rows) {
		int size = rows * 9;
		SimpleContainer c = new SimpleContainer(size) {
			private int viewers;

			@Override
			public void setChanged() {
				super.setChanged();
				save(this);
			}

			private void save(Container self) {
				NonNullList<ItemStack> l = NonNullList.withSize(size, ItemStack.EMPTY);
				for (int i = 0; i < size; i++) l.set(i, self.getItem(i));
				ContainerTags.save(be.data(), level.registryAccess(), l);
				be.setChanged();
			}

			@Override
			public boolean stillValid(Player player) {
				return !be.isRemoved() && level.getBlockEntity(be.getBlockPos()) == be && Container.stillValidBlockEntity(be, player);
			}

			@Override
			public void startOpen(ContainerUser user) {
				viewers++;
			}

			@Override
			public void stopOpen(ContainerUser user) {
				viewers = Math.max(0, viewers - 1);
				// closing the chest sorts it into the smaller chests it holds
				List<ItemStack> l = new ArrayList<>();
				for (int i = 0; i < size; i++) l.add(getItem(i));
				if (sort(l) > 0) {
					for (int i = 0; i < size; i++) setItem(i, l.get(i).isEmpty() ? ItemStack.EMPTY : l.get(i));
					level.playSound(null, be.getBlockPos(), SoundEvents.BUNDLE_INSERT, SoundSource.BLOCKS, 0.8f, 1f);
				}
				save(this);
				if (viewers == 0) OPEN.remove(be);
			}
		};
		NonNullList<ItemStack> items = ContainerTags.load(be.data(), level.registryAccess(), size);
		for (int i = 0; i < size; i++) c.setItem(i, items.get(i));
		return c;
	}

	/** Drops the open container of a chest that is being broken, so nobody keeps taking items out of it. */
	public static void forget(DataBlockEntity be) {
		OPEN.remove(be);
	}

	/** Sneaking with an empty hand: the next sorting rule. */
	public static void cycleRule(ServerPlayer player, DataBlockEntity be) {
		String cur = rule(be.data());
		int i = 0;
		for (int k = 0; k < RULES.length; k++) if (RULES[k].equals(cur)) i = k;
		String next = RULES[(i + 1) % RULES.length];
		if (next.equals("any")) be.data().remove("sort");
		else be.data().putString("sort", next);
		be.changed();
		player.sendOverlayMessage(Component.translatable("message.matriochka.nesting.rule", Component.translatable("nesting.matriochka.rule." + next)).withStyle(ChatFormatting.GOLD));
		player.level().playSound(null, be.getBlockPos(), SoundEvents.WOODEN_BUTTON_CLICK_ON, SoundSource.BLOCKS, 0.8f, 1.2f);
	}

	public static void appendTooltip(ItemStack stack, Consumer<Component> out) {
		int rows = rows(stack);
		if (rows == 0) return;
		int n = 0;
		ItemContainerContents c = stack.get(DataComponents.CONTAINER);
		if (c != null) for (Object ignored : c.nonEmptyItems()) n++;
		out.accept(Component.translatable("tooltip.matriochka.nesting.holds", n, rows * 9).withStyle(ChatFormatting.DARK_GRAY));
		String rule = rule(stack);
		out.accept(Component.translatable("tooltip.matriochka.nesting.rule", Component.translatable("nesting.matriochka.rule." + rule)).withStyle(ChatFormatting.DARK_AQUA));
	}

	/** The chest menu, whose slots refuse a nesting chest as large as the one they are in. */
	public static final class Menu extends ChestMenu {
		public Menu(MenuType<?> type, int id, Inventory inv, Container c, int rows) {
			super(type, id, inv, c, rows);
			for (int i = 0; i < rows * 9; i++) {
				Slot old = slots.get(i);
				Slot s = new Slot(c, old.getContainerSlot(), old.x, old.y) {
					@Override
					public boolean mayPlace(ItemStack stack) {
						return mayHold(rows, stack);
					}
				};
				s.index = i;
				slots.set(i, s);
			}
		}
	}
}
