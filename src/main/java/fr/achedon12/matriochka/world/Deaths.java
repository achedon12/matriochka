package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.block.ContainerTags;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;

/**
 * What the difficulty modes do to a death. Story keeps the inventory and the experience (they wait in the player's
 * state between the death and the respawn, so a server stop in between loses nothing). Hardcore is permanent: the
 * player comes back as a spectator.
 */
public final class Deaths {
	private static final String KEPT = "kept_inventory";

	private Deaths() {}

	/** Story mode: takes the inventory off the dying player so nothing drops, to give it back on respawn. */
	public static void keepInventory(ServerPlayer player) {
		Inventory inv = player.getInventory();
		NonNullList<ItemStack> items = NonNullList.withSize(inv.getContainerSize(), ItemStack.EMPTY);
		for (int i = 0; i < inv.getContainerSize(); i++) {
			items.set(i, inv.getItem(i).copy());
			inv.setItem(i, ItemStack.EMPTY);
		}
		CompoundTag t = new CompoundTag();
		ContainerTags.save(t, player.level().registryAccess(), items);
		t.putInt("size", items.size());
		t.putInt("xp_level", player.experienceLevel);
		t.putFloat("xp_progress", player.experienceProgress);
		t.putInt("xp_total", player.totalExperience);
		player.experienceLevel = 0;
		player.experienceProgress = 0;
		player.totalExperience = 0;
		PlayerState.of(player).tag().put(KEPT, t);
	}

	/** Gives back what keepInventory took; returns true when there was something to give. */
	public static boolean restore(ServerPlayer player) {
		CompoundTag state = PlayerState.of(player).tag();
		if (!state.contains(KEPT)) return false;
		CompoundTag t = state.getCompoundOrEmpty(KEPT);
		state.remove(KEPT);
		Inventory inv = player.getInventory();
		NonNullList<ItemStack> items = ContainerTags.load(t, player.level().registryAccess(), t.getIntOr("size", inv.getContainerSize()));
		for (int i = 0; i < items.size(); i++) {
			ItemStack s = items.get(i);
			if (s.isEmpty()) continue;
			ItemStack cur = i < inv.getContainerSize() ? inv.getItem(i) : ItemStack.EMPTY;
			if (i < inv.getContainerSize() && cur.isEmpty()) inv.setItem(i, s);
			else if (!inv.add(s)) net.minecraft.world.level.block.Block.popResource(player.level(), player.blockPosition(), s);
		}
		player.experienceLevel = t.getIntOr("xp_level", 0);
		player.experienceProgress = t.getFloatOr("xp_progress", 0);
		player.totalExperience = t.getIntOr("xp_total", 0);
		return true;
	}

	/** Called after every respawn. */
	public static void afterRespawn(ServerPlayer player, boolean alive) {
		if (alive) return;
		restore(player);
		if (Config.hardcore() && !player.isCreative()) {
			player.setGameMode(GameType.SPECTATOR);
			PlayerState.of(player).set("perma_dead", true);
			player.sendSystemMessage(Component.translatable("message.matriochka.hardcore_dead").withStyle(ChatFormatting.DARK_RED));
		}
	}
}
