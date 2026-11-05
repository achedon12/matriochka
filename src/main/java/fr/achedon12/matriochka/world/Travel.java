package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/** Entering and leaving worlds: thresholds, return points, boss arenas. */
public final class Travel {
	private Travel() {}

	public static void enter(ServerPlayer player, int world, BlockPos worldBlock) {
		MatrioData data = MatrioData.get(player.level().getServer());
		String group = data.groupOf(player.getUUID());
		ServerLevel target = player.level().getServer().getLevel(Worlds.key(world));
		if (target == null) {
			player.sendSystemMessage(Component.translatable("message.matriochka.no_dimension"));
			return;
		}
		CompoundTag ret = new CompoundTag();
		ret.putString("dim", player.level().dimension().identifier().toString());
		ret.putInt("x", worldBlock.getX());
		ret.putInt("y", worldBlock.getY());
		ret.putInt("z", worldBlock.getZ());
		fr.achedon12.matriochka.rules.PlayerState.of(player).tag().put("return", ret);
		BlockPos seuil = threshold(data, group, world, target);
		player.teleport(new TeleportTransition(target, Vec3.atBottomCenterOf(seuil.above()), Vec3.ZERO, player.getYRot(), player.getXRot(),
			Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		target.playSound(null, seuil, SoundEvents.CHEST_OPEN, SoundSource.PLAYERS, 1f, 0.6f);
		player.sendSystemMessage(Component.translatable("message.matriochka.entered", Component.translatable("dimension.matriochka.world_" + world)));
	}

	/** Builds (once) and returns the threshold platform of a group's parcel. */
	public static BlockPos threshold(MatrioData data, String group, int world, ServerLevel level) {
		CompoundTag entry = data.worldEntry(group, world);
		if (entry.contains("seuil_y")) {
			return new BlockPos(entry.getIntOr("seuil_x", 0), entry.getIntOr("seuil_y", 64), entry.getIntOr("seuil_z", 0));
		}
		BlockPos c = Worlds.parcelCenter(data.parcel(group));
		level.getChunk(c);
		int y;
		if (Worlds.ceiling(world)) {
			y = 48;
		} else if (world == Ocean.WORLD) {
			// the Pressure Ocean has no dry land: the Threshold stands in a diving chamber on the sea floor
			y = Ocean.thresholdY(level, c);
		} else {
			y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, c.getX(), c.getZ());
			if (world == 4 && y <= level.getMinY() + 2) y = 120;
		}
		BlockPos base = new BlockPos(c.getX(), y, c.getZ());
		if (world == Ocean.WORLD) {
			Ocean.buildChamber(level, base);
			level.setBlock(base, ModContent.block("threshold").defaultBlockState(), 3);
		} else {
			buildPlatform(level, base, world);
		}
		entry.putInt("seuil_x", base.getX());
		entry.putInt("seuil_y", base.getY());
		entry.putInt("seuil_z", base.getZ());
		data.changed();
		Arenas.build(level, world, base.offset(0, 0, Worlds.ARENA_OFFSET));
		return base;
	}

	private static void buildPlatform(ServerLevel level, BlockPos base, int world) {
		BlockState lacquer = ModContent.block("lacquer_block").defaultBlockState();
		BlockState wood = ModContent.block("painted_wood").defaultBlockState();
		for (int dx = -3; dx <= 3; dx++) {
			for (int dz = -3; dz <= 3; dz++) {
				boolean edge = Math.abs(dx) == 3 || Math.abs(dz) == 3;
				level.setBlock(base.offset(dx, -1, dz), edge ? wood : lacquer, 3);
				for (int dy = 0; dy <= 4; dy++) {
					BlockPos p = base.offset(dx, dy, dz);
					if (!level.getBlockState(p).isAir()) level.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
				}
				if (Worlds.ceiling(world)) level.setBlock(base.offset(dx, 5, dz), wood, 3);
			}
		}
		level.setBlock(base, ModContent.block("threshold").defaultBlockState(), 3);
		for (int[] o : new int[][]{{3, 3}, {-3, 3}, {3, -3}, {-3, -3}}) {
			level.setBlock(base.offset(o[0], 0, o[1]), Blocks.LANTERN.defaultBlockState(), 3);
		}
	}

	/** Leaves the current world through the stored return point (the world block outside). */
	public static boolean leave(ServerPlayer player) {
		CompoundTag ret = fr.achedon12.matriochka.rules.PlayerState.of(player).tag().getCompoundOrEmpty("return");
		ServerLevel target = null;
		BlockPos pos;
		if (ret.contains("dim")) {
			target = player.level().getServer().getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(ret.getStringOr("dim", "minecraft:overworld"))));
			pos = new BlockPos(ret.getIntOr("x", 0), ret.getIntOr("y", 64), ret.getIntOr("z", 0));
		} else {
			pos = null;
		}
		if (target == null) {
			target = player.level().getServer().overworld();
			pos = target.getRespawnData().pos();
		}
		BlockPos safe = findSafe(target, pos);
		player.teleport(new TeleportTransition(target, Vec3.atBottomCenterOf(safe), Vec3.ZERO, player.getYRot(), player.getXRot(),
			Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		return true;
	}

	public static boolean returnToWorldBlock(ServerPlayer player) {
		if (Worlds.number(player.level()) == 0) {
			player.sendSystemMessage(Component.translatable("message.matriochka.not_in_world"));
			return false;
		}
		return leave(player);
	}

	public static BlockPos findSafe(Level level, BlockPos near) {
		for (int r = 1; r <= 3; r++) {
			for (int dx = -r; dx <= r; dx++) {
				for (int dz = -r; dz <= r; dz++) {
					BlockPos p = near.offset(dx, 0, dz);
					for (int dy = -1; dy <= 3; dy++) {
						BlockPos q = p.above(dy);
						if (level.getBlockState(q).isAir() && level.getBlockState(q.above()).isAir() && !level.getBlockState(q.below()).isAir()) {
							return q;
						}
					}
				}
			}
		}
		return near.above();
	}
}
