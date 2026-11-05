package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/**
 * The New Cycle: once an ending has been reached, a group can close every world again and replay them, harder.
 * <p>
 * The group keeps a cycle number ("cycle" in its tag, 0 for the first playthrough). Beginning a cycle resets the
 * group's progression (defeated bosses), gives it a fresh parcel in every world (so the prisons are new and whole)
 * and invalidates the World Blocks of older cycles. Each player keeps souls, karma, Journal pages, quests, titles,
 * endings and gear (with its classes); they lose the cores, Seeds, World Soils, offerings and keys that opened the
 * old worlds, and the layers of their Doll of Life. Every creature and boss of a cycle gets
 * {@link #healthFactor(int)} health and {@link #damageFactor(int)} damage.
 */
public final class Cycles {
	private Cycles() {}

	public static int of(MatrioData data, String group) {
		return data.group(group).getIntOr("cycle", 0);
	}

	public static int of(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		return of(data, data.groupOf(p.getUUID()));
	}

	/** Creature and boss health in a cycle: +50% per cycle. */
	public static float healthFactor(int cycle) {
		return 1f + 0.5f * Math.max(0, cycle);
	}

	/** Creature and boss damage in a cycle: +25% per cycle. */
	public static float damageFactor(int cycle) {
		return 1f + 0.25f * Math.max(0, cycle);
	}

	/**
	 * The cycle that applies at a place: in a world, the cycle of the group whose parcel it is; on the Surface (or a
	 * parcel nobody owns), the cycle of the nearest player's group.
	 */
	public static int at(ServerLevel level, BlockPos pos) {
		MatrioData data = MatrioData.get(level.getServer());
		if (Worlds.isModWorld(level)) {
			String g = data.groupOfParcel(Worlds.parcelOf(pos));
			if (g != null) return of(data, g);
		}
		Player near = level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 96, false);
		return near == null ? 0 : of(data, data.groupOf(near.getUUID()));
	}

	public static boolean canBegin(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		return Endings.any(PlayerState.of(p)) && data.defeated(data.groupOf(p.getUUID()), 10);
	}

	/** Begins the next cycle for the player's whole group. */
	public static void begin(ServerPlayer p) {
		if (!canBegin(p)) {
			p.sendSystemMessage(Component.translatable("message.matriochka.cycle.locked"));
			return;
		}
		var server = p.level().getServer();
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		var g = data.group(group);
		int cycle = of(data, group) + 1;
		g.putInt("cycle", cycle);
		g.putInt("done", 0);
		g.remove("parcel");
		g.remove("worlds");
		data.changed();
		for (UUID id : data.members(group)) {
			ServerPlayer m = server.getPlayerList().getPlayer(id);
			if (m != null) catchUp(m);
		}
	}

	/** Brings a player to the cycle of their group (at once, or at their next login if they were away). */
	public static void catchUp(ServerPlayer p) {
		PlayerState ps = PlayerState.of(p);
		int cycle = of(p);
		if (ps.tag().getIntOr("cycle", 0) >= cycle) return;
		if (Worlds.isModWorld(p.level())) Travel.leave(p);
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (!s.isEmpty() && oldKey(ModContent.idOf(s.getItem()))) inv.setItem(i, ItemStack.EMPTY);
		}
		ps.setDoll(0, 0);
		for (int w = 0; w <= Worlds.ZERO; w++) {
			ps.set("boss_" + w, false);
			ps.tag().remove("cradle_" + w);
		}
		ps.tag().remove("return");
		ps.tag().putInt("cycle", cycle);
		Achievements.grantId(p, "endings/new_cycle");
		p.sendSystemMessage(Component.translatable("message.matriochka.cycle.begun", cycle + 1).withStyle(ChatFormatting.GOLD));
		ps.sync();
	}

	/** The items that opened the worlds of the previous cycle. */
	private static boolean oldKey(String id) {
		if (id.isEmpty()) return false;
		if (id.startsWith("world_soil_") || id.equals("last_doll_key") || id.equals("cracked_doll")) return true;
		Defs.ItemDef d = ModContent.def(id);
		return d != null && (d.kind().equals("core") || d.kind().equals("seed") || d.kind().equals("offering"));
	}
}
