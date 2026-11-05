package fr.achedon12.matriochka.net;

import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

/**
 * Menu shared by all stations. Recipes are crafted from the player's inventory (button ids 0..99); the soul altar and
 * the class table use the single item slot. Synced data: condition, charge/heat, lock code (3), pins entered, ferment.
 */
public class StationMenu extends AbstractContainerMenu {
	public record Data(BlockPos pos, String station) {
		public static final StreamCodec<RegistryFriendlyByteBuf, Data> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Data::pos, ByteBufCodecs.STRING_UTF8, Data::station, Data::new);
	}

	public static final int PANEL_W = 256, PANEL_H = 222;
	/** The two Inverter sockets, in the niche on the right of the cabinet. */
	public static final int INVERTER_A_X = 204, INVERTER_B_X = 226, INVERTER_Y = 30;
	public final Data data;
	public final SimpleContainer slot = new SimpleContainer(2);
	public final ContainerData sync;
	private final Player player;

	public StationMenu(int id, Inventory inv, Data data) {
		super(ModContent.STATION_MENU, id);
		this.data = data;
		this.player = inv.player;
		this.sync = new SimpleContainerData(8);
		boolean hasSlot = data.station().equals("soul_altar") || data.station().equals("class_table");
		if (hasSlot) addSlot(new Slot(slot, 0, 120, 70));
		if (data.station().equals("inverter")) {
			addSlot(new Slot(slot, 0, INVERTER_A_X, INVERTER_Y));
			addSlot(new Slot(slot, 1, INVERTER_B_X, INVERTER_Y));
		}
		for (int r = 0; r < 3; r++)
			for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c + r * 9 + 9, 48 + c * 18, 140 + r * 18));
		for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, 48 + c * 18, 198));
		addDataSlots(sync);
	}

	private DataBlockEntity be() {
		if (player.level() instanceof ServerLevel sl && sl.getBlockEntity(data.pos()) instanceof DataBlockEntity be) return be;
		return null;
	}

	@Override
	public void broadcastChanges() {
		DataBlockEntity be = be();
		if (be != null && player.level() instanceof ServerLevel sl) {
			int cond = Stations.condition(sl, data.pos(), data.station(), be);
			// the forge also counts as ready when the player carries a Storm Essence to feed it
			if (cond == 0 && data.station().equals("lightning_forge") && Stations.count(player.getInventory(), ModContent.item("storm_essence")) > 0) cond = 1;
			sync.set(0, cond);
			sync.set(1, data.station().equals("ash_foundry") ? Stations.heat(sl, data.pos()) : be.data().getIntOr("charge", 0));
			for (int i = 0; i < 3; i++) sync.set(2 + i, be.data().getIntOr("code" + i, 0));
			sync.set(5, be.data().getIntOr("entered", 0));
			sync.set(6, be.data().getIntOr("ferment", 0));
		}
		super.broadcastChanges();
	}

	@Override
	public boolean clickMenuButton(Player p, int id) {
		if (!(p instanceof ServerPlayer sp)) return true;
		DataBlockEntity be = be();
		if (be == null) return false;
		ServerLevel sl = (ServerLevel) sp.level();
		String err = null;
		if (id < 100) {
			err = Stations.craft(sp, sl, data.pos(), data.station(), be, id);
		} else if (id < 104) {
			Stations.pin(sl, be, id - 100);
		} else if (id == 200 || id == 201) {
			err = Stations.soulAltar(sp, slot.getItem(0), id == 200);
		} else if (id == 202) {
			err = Stations.rechargeDoll(sp);
		} else if (id == 210) {
			err = Stations.upgrade(sp, slot.getItem(0));
		} else if (id == 211) {
			err = Stations.reroll(sp, slot.getItem(0));
		} else if (id == 220 && data.station().equals("abyssal_press")) {
			err = Stations.refillSnorkel(sp, sl, data.pos(), be);
		} else if (id == 212) {
			err = Stations.addLayer(sp, slot.getItem(0));
		} else if (id == 220) {
			err = Stations.invert(sp, slot.getItem(0), slot.getItem(1));
		}
		if (err != null && !err.isEmpty()) sp.sendSystemMessage(Component.translatable(err));
		broadcastChanges();
		return true;
	}

	@Override
	public ItemStack quickMoveStack(Player p, int index) {
		return ItemStack.EMPTY;
	}

	@Override
	public boolean stillValid(Player p) {
		return p.distanceToSqr(data.pos().getX() + 0.5, data.pos().getY() + 0.5, data.pos().getZ() + 0.5) < 64;
	}

	@Override
	public void removed(Player p) {
		super.removed(p);
		if (p instanceof ServerPlayer) clearContainer(p, slot);
	}
}
