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
 * the class table use the single item slot. Synced data: condition, charge/heat, lock code (3), pins entered, ferment,
 * and the recipe kept for automation (index + 1, 0 for none). Buttons 300 + index pick that recipe, 299 clears it.
 * <p>
 * The Matrix Workbench is a crafting table: its recipes are patterns on a 3 x 3 grid ({@link WorkbenchPatterns}),
 * the result shows in its own slot and is taken like any crafted item. Its drawers are a recipe book: a button fills
 * the grid from the player's inventory.
 */
public class StationMenu extends AbstractContainerMenu {
	public record Data(BlockPos pos, String station) {
		public static final StreamCodec<RegistryFriendlyByteBuf, Data> CODEC = StreamCodec.composite(
			BlockPos.STREAM_CODEC, Data::pos, ByteBufCodecs.STRING_UTF8, Data::station, Data::new);
	}

	public static final int PANEL_W = 256, PANEL_H = 222;
	/** The two Inverter sockets, in the niche on the right of the cabinet. */
	public static final int INVERTER_A_X = 204, INVERTER_B_X = 226, INVERTER_Y = 30;
	/** The workbench grid (top-left slot) and its result slot, in the niche on the right. */
	public static final int GRID_X = 196, GRID_Y = 24, RESULT_X = 214, RESULT_Y = 90;
	public final SimpleContainer grid = new SimpleContainer(9) {
		@Override
		public void setChanged() {
			super.setChanged();
			slotsChanged(this);
		}
	};
	public final SimpleContainer result = new SimpleContainer(1);
	/** Index of the result slot in {@link #slots}, or -1 outside the workbench. */
	public int resultSlot = -1;
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
		if (workbench()) {
			for (int i = 0; i < 9; i++) addSlot(new Slot(grid, i, GRID_X + (i % 3) * 18, GRID_Y + (i / 3) * 18));
			resultSlot = slots.size();
			addSlot(new ResultSlot());
		}
		for (int r = 0; r < 3; r++)
			for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c + r * 9 + 9, 48 + c * 18, 140 + r * 18));
		for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, 48 + c * 18, 198));
		addDataSlots(sync);
	}

	public boolean workbench() {
		return data.station().equals("matrix_workbench");
	}

	/** The recipe the grid spells out now, if the player may make it. */
	private fr.achedon12.matriochka.content.Recipes.Recipe gridRecipe() {
		var r = fr.achedon12.matriochka.block.WorkbenchPatterns.match(grid.getItems());
		if (r == null || !(player instanceof ServerPlayer sp)) return r;
		return Stations.canSeeRecipe(sp, r) && Stations.tookPart(sp, r) ? r : null;
	}

	@Override
	public void slotsChanged(net.minecraft.world.Container c) {
		super.slotsChanged(c);
		if (c == grid && !player.level().isClientSide()) {
			var r = gridRecipe();
			result.setItem(0, r == null ? ItemStack.EMPTY : new ItemStack(Stations.resolve(r.output()), r.count()));
		}
	}

	/** Takes what one craft costs out of the grid, then rolls the result's class and counts the craft. */
	private void crafted(ServerPlayer sp, ItemStack out) {
		var r = fr.achedon12.matriochka.block.WorkbenchPatterns.match(grid.getItems());
		if (r == null) return;
		var p = fr.achedon12.matriochka.block.WorkbenchPatterns.of(r.output());
		for (int i = 0; i < 9; i++) if (p[i] != null) grid.getItem(i).shrink(p[i].count());
		fr.achedon12.matriochka.gear.GearClasses.roll(out, sp.level().getRandom());
		DataBlockEntity be = be();
		if (be != null) {
			Stations.afterCraft((ServerLevel) sp.level(), data.pos(), data.station(), be);
			fr.achedon12.matriochka.block.StationAutomation.select(be, data.station(), fr.achedon12.matriochka.content.Recipes.of(data.station()).indexOf(r), sp);
		}
		var ps = fr.achedon12.matriochka.rules.PlayerState.of(sp);
		ps.progress("craft", r.output(), out.getCount());
		ps.progress("station", data.station(), 1);
		grid.setChanged();
		slotsChanged(grid);
	}

	/** The workbench's result: shown while the grid spells a recipe, taken like a crafted item. */
	private class ResultSlot extends Slot {
		ResultSlot() {
			super(result, 0, RESULT_X, RESULT_Y);
		}

		@Override
		public boolean mayPlace(ItemStack stack) {
			return false;
		}

		@Override
		public void onTake(Player p, ItemStack stack) {
			if (p instanceof ServerPlayer sp) crafted(sp, stack);
			super.onTake(p, stack);
		}
	}

	/**
	 * A drawer pressed at the workbench: what is on the grid goes back to the inventory, then the grid is laid out with
	 * the recipe's pattern from the inventory. Nothing moves when an ingredient is missing.
	 */
	private String fillGrid(ServerPlayer sp, int index) {
		var list = fr.achedon12.matriochka.content.Recipes.of(data.station());
		if (index < 0 || index >= list.size()) return "message.matriochka.station.unknown";
		var r = list.get(index);
		if (!Stations.canSeeRecipe(sp, r)) return "message.matriochka.station.locked";
		if (!Stations.tookPart(sp, r)) return "message.matriochka.station.take_part";
		var p = fr.achedon12.matriochka.block.WorkbenchPatterns.of(r.output());
		if (p == null) return "message.matriochka.station.unknown";
		for (int i = 0; i < 9; i++) {
			ItemStack back = grid.removeItemNoUpdate(i);
			if (!back.isEmpty() && !sp.getInventory().add(back)) sp.spawnAtLocation((ServerLevel) sp.level(), back);
		}
		Inventory inv = sp.getInventory();
		if (!sp.isCreative()) for (var ing : r.inputs()) if (Stations.count(inv, Stations.resolve(ing.id())) < ing.count()) {
			slotsChanged(grid);
			return "message.matriochka.station.missing";
		}
		for (int i = 0; i < 9; i++) {
			if (p[i] == null) continue;
			var item = Stations.resolve(p[i].id());
			if (!sp.isCreative()) Stations.takeFrom(inv, item, p[i].count());
			grid.setItem(i, new ItemStack(item, p[i].count()));
		}
		grid.setChanged();
		slotsChanged(grid);
		return null;
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
			sync.set(7, fr.achedon12.matriochka.block.StationAutomation.selectedIndex(be, data.station()) + 1);
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
		if (id < 100 && workbench()) {
			err = fillGrid(sp, id);
		} else if (id < 100) {
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
		} else if (id == 299) {
			fr.achedon12.matriochka.block.StationAutomation.clear(be);
			sp.sendOverlayMessage(Component.translatable("message.matriochka.station.auto_off"));
		} else if (id >= 300 && id < 400 && fr.achedon12.matriochka.block.StationAutomation.automatable(data.station())) {
			err = fr.achedon12.matriochka.block.StationAutomation.select(be, data.station(), id - 300, sp);
			if (err == null) sp.sendOverlayMessage(Component.translatable("message.matriochka.station.auto_on",
				new ItemStack(Stations.resolve(fr.achedon12.matriochka.content.Recipes.of(data.station()).get(id - 300).output())).getHoverName()));
		}
		if (err != null && !err.isEmpty()) sp.sendSystemMessage(Component.translatable(err));
		broadcastChanges();
		return true;
	}

	@Override
	public ItemStack quickMoveStack(Player p, int index) {
		// at the workbench: a shift-click on the result crafts once into the inventory, one on the grid sends it back
		if (!workbench() || index < 0 || index >= slots.size()) return ItemStack.EMPTY;
		Slot s = slots.get(index);
		if (!s.hasItem()) return ItemStack.EMPTY;
		int invStart = resultSlot + 1, invEnd = slots.size();
		ItemStack stack = s.getItem();
		ItemStack copy = stack.copy();
		if (index == resultSlot) {
			if (!(p instanceof ServerPlayer sp)) return ItemStack.EMPTY;
			result.setItem(0, ItemStack.EMPTY);
			crafted(sp, copy);
			if (!moveItemStackTo(copy, invStart, invEnd, true) && !copy.isEmpty()) sp.spawnAtLocation((ServerLevel) sp.level(), copy);
			return ItemStack.EMPTY;
		}
		if (index < resultSlot && index >= resultSlot - 9) {
			if (!moveItemStackTo(stack, invStart, invEnd, false)) return ItemStack.EMPTY;
			s.setChanged();
			return ItemStack.EMPTY;
		}
		return ItemStack.EMPTY;
	}

	@Override
	public boolean stillValid(Player p) {
		return p.distanceToSqr(data.pos().getX() + 0.5, data.pos().getY() + 0.5, data.pos().getZ() + 0.5) < 64;
	}

	@Override
	public void removed(Player p) {
		super.removed(p);
		if (p instanceof ServerPlayer) {
			clearContainer(p, slot);
			clearContainer(p, grid);
		}
	}
}
