package fr.achedon12.matriochka.compat.jade;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Blocks2;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.client.JournalScreen;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import snownee.jade.api.BlockAccessor;
import snownee.jade.api.IBlockComponentProvider;
import snownee.jade.api.ITooltip;
import snownee.jade.api.IWailaClientRegistration;
import snownee.jade.api.IWailaPlugin;
import snownee.jade.api.WailaPlugin;
import snownee.jade.api.config.IPluginConfig;

/**
 * Jade support: looking at a World Block names the world inside, its variant and its cycle; looking at a planted Seed
 * or a rite site names the world it will open. Everything is read from the block data the server already sends.
 * Jade loads this class through the "jade" entrypoint, so without Jade it is never touched.
 */
@WailaPlugin
public class MatrioJadePlugin implements IWailaPlugin {
	@Override
	public void registerClient(IWailaClientRegistration registration) {
		registration.registerBlockComponent(WorldBlockInfo.INSTANCE, Blocks2.WorldBlock.class);
		registration.registerBlockComponent(SeedInfo.INSTANCE, Blocks2.PlantedSeed.class);
	}

	private static CompoundTag data(BlockAccessor a) {
		return a.getBlockEntity() instanceof DataBlockEntity be ? be.data() : new CompoundTag();
	}

	private static Component world(int n) {
		return Component.translatable("jade.matriochka.world", n, Component.translatable("world.matriochka." + n)).withStyle(ChatFormatting.GOLD);
	}

	enum WorldBlockInfo implements IBlockComponentProvider {
		INSTANCE;

		@Override
		public void appendTooltip(ITooltip tooltip, BlockAccessor accessor, IPluginConfig config) {
			CompoundTag d = data(accessor);
			int n = d.getIntOr("world", 0);
			if (n <= 0) return;
			tooltip.add(world(n));
			String variant = d.getStringOr("variant", "");
			if (!variant.isEmpty()) tooltip.add(Component.translatable("journal.matriochka.variant", Component.translatable(JournalScreen.variantKey(variant, n))).withStyle(ChatFormatting.GRAY));
			int cycle = d.getIntOr("cycle", 0);
			if (cycle > 0) tooltip.add(Component.translatable("command.matriochka.cycle.show", cycle + 1).withStyle(ChatFormatting.GRAY));
		}

		@Override
		public Identifier getUid() {
			return Matriochka.id("world_block");
		}
	}

	enum SeedInfo implements IBlockComponentProvider {
		INSTANCE;

		@Override
		public void appendTooltip(ITooltip tooltip, BlockAccessor accessor, IPluginConfig config) {
			int n = accessor.getBlockState().getValue(Blocks2.PlantedSeed.WORLD);
			tooltip.add(Component.translatable("jade.matriochka.opens", world(n)));
		}

		@Override
		public Identifier getUid() {
			return Matriochka.id("seed");
		}
	}
}
