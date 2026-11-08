package fr.achedon12.matriochka.block;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/** Block entity that keeps its whole state in one compound tag. Simple and robust across versions. */
public class DataBlockEntity extends BlockEntity {
	protected CompoundTag data = new CompoundTag();
	/** The automation buffer of a station (inputs and output, see StationInventory); null until something goes in. */
	private net.minecraft.core.NonNullList<net.minecraft.world.item.ItemStack> items;

	public DataBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
		super(type, pos, state);
	}

	public CompoundTag data() {
		return data;
	}

	/** The station buffer, created on first use. */
	public net.minecraft.core.NonNullList<net.minecraft.world.item.ItemStack> items() {
		if (items == null) items = net.minecraft.core.NonNullList.withSize(StationInventory.SIZE, net.minecraft.world.item.ItemStack.EMPTY);
		return items;
	}

	public boolean hasItems() {
		if (items == null) return false;
		for (var s : items) if (!s.isEmpty()) return true;
		return false;
	}

	/** A broken station spills its buffer. */
	@Override
	public void preRemoveSideEffects(BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
		super.preRemoveSideEffects(pos, state);
		if (level != null && hasItems()) net.minecraft.world.Containers.dropContents(level, pos, items);
		// a Nesting Cradle broken mid-way gives its ores back
		if (level instanceof net.minecraft.server.level.ServerLevel sl && state.getBlock() instanceof NestingCradle) NestingCradle.spill(sl, pos, this);
	}

	public void changed() {
		setChanged();
		if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
	}

	@Override
	protected void loadAdditional(ValueInput input) {
		super.loadAdditional(input);
		data = input.read("mdata", CompoundTag.CODEC).orElseGet(CompoundTag::new);
		items = null;
		for (var it : input.listOrEmpty("station_items", net.minecraft.world.ItemStackWithSlot.CODEC)) {
			if (it.isValidInContainer(StationInventory.SIZE)) items().set(it.slot(), it.stack());
		}
	}

	@Override
	protected void saveAdditional(ValueOutput output) {
		super.saveAdditional(output);
		output.store("mdata", CompoundTag.CODEC, data);
		if (hasItems()) {
			var list = output.list("station_items", net.minecraft.world.ItemStackWithSlot.CODEC);
			for (int i = 0; i < items.size(); i++) if (!items.get(i).isEmpty()) list.add(new net.minecraft.world.ItemStackWithSlot(i, items.get(i)));
		}
	}

	/** World Blocks tell the client which world they hold and its variant, for the miniature preview. Nothing else leaves the server. */
	private boolean preview() {
		return getBlockState().is(fr.achedon12.matriochka.content.ModContent.block("world_block"));
	}

	@Override
	public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getUpdatePacket() {
		return preview() ? net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(this) : null;
	}

	@Override
	public CompoundTag getUpdateTag(net.minecraft.core.HolderLookup.Provider registries) {
		CompoundTag out = new CompoundTag();
		if (!preview()) return out;
		CompoundTag shown = new CompoundTag();
		shown.putInt("world", data.getIntOr("world", 1));
		shown.putString("variant", data.getStringOr("variant", "plain"));
		shown.putLong("quake", data.getLongOr("quake", 0L));
		shown.putLong("heat", data.getLongOr("heat", 0L));
		out.put("mdata", shown);
		return out;
	}
}
