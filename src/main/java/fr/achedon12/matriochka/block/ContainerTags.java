package fr.achedon12.matriochka.block;

import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.RegistryOps;
import net.minecraft.world.item.ItemStack;

/** Item list (de)serialisation into a compound tag, via the ItemStack codec. */
public final class ContainerTags {
	private ContainerTags() {}

	public static void save(CompoundTag tag, HolderLookup.Provider regs, NonNullList<ItemStack> items) {
		ListTag list = new ListTag();
		RegistryOps<Tag> ops = regs.createSerializationContext(net.minecraft.nbt.NbtOps.INSTANCE);
		for (int i = 0; i < items.size(); i++) {
			ItemStack s = items.get(i);
			if (s.isEmpty()) continue;
			int slot = i;
			ItemStack.CODEC.encodeStart(ops, s).result().ifPresent(t -> {
				CompoundTag e = new CompoundTag();
				e.putInt("slot", slot);
				e.put("stack", t);
				list.add(e);
			});
		}
		tag.put("items", list);
	}

	public static NonNullList<ItemStack> load(CompoundTag tag, HolderLookup.Provider regs, int size) {
		NonNullList<ItemStack> items = NonNullList.withSize(size, ItemStack.EMPTY);
		RegistryOps<Tag> ops = regs.createSerializationContext(net.minecraft.nbt.NbtOps.INSTANCE);
		for (Tag t : tag.getListOrEmpty("items")) {
			if (!(t instanceof CompoundTag e)) continue;
			int slot = e.getIntOr("slot", 0);
			Tag st = e.get("stack");
			if (st == null || slot < 0 || slot >= size) continue;
			ItemStack.CODEC.parse(ops, st).result().ifPresent(s -> items.set(slot, s));
		}
		return items;
	}
}
