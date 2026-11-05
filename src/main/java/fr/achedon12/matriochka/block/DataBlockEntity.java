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

	public DataBlockEntity(BlockEntityType<?> type, BlockPos pos, BlockState state) {
		super(type, pos, state);
	}

	public CompoundTag data() {
		return data;
	}

	public void changed() {
		setChanged();
		if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
	}

	@Override
	protected void loadAdditional(ValueInput input) {
		super.loadAdditional(input);
		data = input.read("mdata", CompoundTag.CODEC).orElseGet(CompoundTag::new);
	}

	@Override
	protected void saveAdditional(ValueOutput output) {
		super.saveAdditional(output);
		output.store("mdata", CompoundTag.CODEC, data);
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
