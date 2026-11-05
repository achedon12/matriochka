package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.Set;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.Vec3;

/**
 * The refuge doll: a pocket base in the matriochka:refuge dimension, one room per group. The room is a lacquered
 * cabinet that opens after the World 3 boss and grows after the bosses of worlds 5, 7 and 9. It cannot be entered
 * while a boss is awake nearby.
 */
public final class Refuge {
	/** Rooms are this far apart along x, one per group parcel. */
	public static final int STRIDE = 256;
	/** Floor level of every room: players stand at this height. */
	public static final int FLOOR_Y = 64;
	/** Half-width and height of the room per size tier (0 = no room yet). */
	private static final int[] RADIUS = {0, 4, 6, 8, 10};
	private static final int[] HEIGHT = {0, 4, 5, 6, 7};
	public static final int BOSS_RANGE = 64;

	private Refuge() {}

	public static void init() {
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (server.overworld().getGameTime() % 20 == 7) catchFalling(server);
		});
	}

	/** Size tier of a group's room, from its progression: World 3 opens it, worlds 5, 7 and 9 enlarge it. */
	public static int tier(int highestDefeated) {
		if (highestDefeated >= 9) return 4;
		if (highestDefeated >= 7) return 3;
		if (highestDefeated >= 5) return 2;
		if (highestDefeated >= 3) return 1;
		return 0;
	}

	public static int radius(int tier) {
		return RADIUS[Math.max(0, Math.min(4, tier))];
	}

	public static int height(int tier) {
		return HEIGHT[Math.max(0, Math.min(4, tier))];
	}

	public static boolean inRefuge(Level level) {
		return level.dimension() == Worlds.REFUGE;
	}

	public static BlockPos center(int parcel) {
		return new BlockPos(parcel * STRIDE, FLOOR_Y, 0);
	}

	/** The parcel a refuge position belongs to. */
	public static int parcelOf(BlockPos pos) {
		return Math.floorDiv(pos.getX() + STRIDE / 2, STRIDE);
	}

	/** True when a boss is awake within reach of the player: the doll stays shut during boss fights. */
	public static boolean bossNearby(ServerPlayer player) {
		return !player.level().getEntitiesOfClass(MatrioBoss.class, player.getBoundingBox().inflate(BOSS_RANGE), MatrioBoss::isAlive).isEmpty();
	}

	/** Using the refuge doll: in, or back out when already inside. */
	public static boolean use(ServerPlayer player) {
		if (inRefuge(player.level())) {
			leave(player);
			return true;
		}
		return enter(player);
	}

	public static boolean enter(ServerPlayer player) {
		MinecraftServer server = player.level().getServer();
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(player.getUUID());
		int tier = tier(data.highestDefeated(group));
		if (tier == 0 && !player.isCreative()) {
			player.sendSystemMessage(Component.translatable("message.matriochka.refuge.locked").withStyle(ChatFormatting.GRAY));
			return false;
		}
		if (bossNearby(player)) {
			player.sendOverlayMessage(Component.translatable("message.matriochka.refuge.boss").withStyle(ChatFormatting.RED));
			return false;
		}
		ServerLevel level = server.getLevel(Worlds.REFUGE);
		if (level == null) {
			player.sendSystemMessage(Component.translatable("message.matriochka.no_dimension"));
			return false;
		}
		int before = builtTier(data, group);
		BlockPos spawn = ensureBuilt(level, data, group, Math.max(1, tier));
		CompoundTag ret = new CompoundTag();
		ret.putString("dim", player.level().dimension().identifier().toString());
		ret.putDouble("x", player.getX());
		ret.putDouble("y", player.getY());
		ret.putDouble("z", player.getZ());
		ret.putFloat("yaw", player.getYRot());
		PlayerState.of(player).tag().put("refuge_return", ret);
		player.teleport(new TeleportTransition(level, Vec3.atBottomCenterOf(spawn), Vec3.ZERO, 180f, 0f, Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		level.playSound(null, spawn, SoundEvents.CHEST_OPEN, SoundSource.PLAYERS, 1f, 0.7f);
		player.sendOverlayMessage(Component.translatable("message.matriochka.refuge.entered").withStyle(ChatFormatting.GOLD));
		if (before > 0 && builtTier(data, group) > before) player.sendSystemMessage(Component.translatable("message.matriochka.refuge.grown").withStyle(ChatFormatting.GOLD));
		return true;
	}

	/** Back to where the player stood when they opened the doll (the overworld spawn if that place is gone). */
	public static void leave(ServerPlayer player) {
		MinecraftServer server = player.level().getServer();
		CompoundTag ret = PlayerState.of(player).tag().getCompoundOrEmpty("refuge_return");
		ServerLevel target = null;
		Vec3 at = null;
		float yaw = player.getYRot();
		if (ret.contains("dim")) {
			target = server.getLevel(ResourceKey.create(Registries.DIMENSION, Identifier.parse(ret.getStringOr("dim", "minecraft:overworld"))));
			at = new Vec3(ret.getDoubleOr("x", 0), ret.getDoubleOr("y", 64), ret.getDoubleOr("z", 0));
			yaw = ret.getFloatOr("yaw", yaw);
		}
		if (target == null || target.dimension() == Worlds.REFUGE) {
			target = server.overworld();
			at = Vec3.atBottomCenterOf(Travel.findSafe(target, target.getRespawnData().pos()));
		}
		PlayerState.of(player).tag().remove("refuge_return");
		player.teleport(new TeleportTransition(target, at, Vec3.ZERO, yaw, player.getXRot(), Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		target.playSound(null, BlockPos.containing(at), SoundEvents.CHEST_CLOSE, SoundSource.PLAYERS, 1f, 0.7f);
	}

	/** Sends out every online member of a group standing in that group's room (after a kick or a disband). */
	public static void expel(ServerPlayer player, int parcel) {
		if (inRefuge(player.level()) && parcelOf(player.blockPosition()) == parcel) leave(player);
	}

	/** Builds the room the first time, grows it when the group reached a bigger tier, and returns where to stand. */
	public static BlockPos ensureBuilt(ServerLevel level, MatrioData data, String group, int tier) {
		CompoundTag g = data.group(group);
		CompoundTag r = g.getCompoundOrEmpty("refuge");
		int parcel = data.parcel(group);
		BlockPos c = center(parcel);
		int built = r.getIntOr("tier", 0);
		level.getChunk(c);
		if (built < tier) {
			if (built == 0) {
				build(level, c, tier);
				furnish(level, c, tier);
			} else {
				grow(level, c, built, tier);
			}
			r.putInt("tier", tier);
			g.put("refuge", r);
			data.changed();
			if (built > 0) {
				level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, 40, 2, 1, 2, 0.3);
			}
		}
		return spawn(c);
	}

	/** The players arrive on the Threshold by the south wall of the first room. */
	public static BlockPos spawn(BlockPos c) {
		return c.offset(0, 0, radius(1) - 1);
	}

	/** Group data of a room's size, for the checks and the admin listing. */
	public static int builtTier(MatrioData data, String group) {
		return data.group(group).getCompoundOrEmpty("refuge").getIntOr("tier", 0);
	}

	// ---------------------------------------------------------------- building
	private static BlockState wood() {
		return ModContent.block("painted_wood").defaultBlockState();
	}

	private static BlockState lacquer() {
		return ModContent.block("lacquer_block").defaultBlockState();
	}

	/** Floor, walls and ceiling of a room of this tier, around c (c is the floor level the players stand on). */
	private static void build(ServerLevel level, BlockPos c, int tier) {
		int r = radius(tier), h = height(tier);
		for (int dx = -r - 1; dx <= r + 1; dx++) {
			for (int dz = -r - 1; dz <= r + 1; dz++) {
				boolean wall = Math.abs(dx) == r + 1 || Math.abs(dz) == r + 1;
				BlockPos floor = c.offset(dx, -1, dz);
				if (wall || level.getBlockState(floor).isAir()) level.setBlock(floor, floorAt(dx, dz, r), 3);
				level.setBlock(c.offset(dx, h, dz), ceilingAt(dx, dz, r), 3);
				if (wall) {
					for (int y = 0; y < h; y++) level.setBlock(c.offset(dx, y, dz), wallAt(dx, y, dz, r, h), 3);
				}
			}
		}
		// lanterns hang from the ceiling, one in each corner and one over the middle
		BlockState lantern = Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, true);
		int k = Math.max(1, r - 1);
		for (int[] o : new int[][]{{k, k}, {-k, k}, {k, -k}, {-k, -k}, {0, 0}}) {
			BlockPos p = c.offset(o[0], h - 1, o[1]);
			if (level.getBlockState(p).isAir()) level.setBlock(p, lantern, 3);
		}
	}

	/** Lacquer border and a lacquer cross through the middle, painted wood elsewhere. */
	private static BlockState floorAt(int dx, int dz, int r) {
		boolean edge = Math.abs(dx) >= r || Math.abs(dz) >= r;
		boolean cross = dx == 0 || dz == 0;
		return edge || cross ? lacquer() : wood();
	}

	/** Lacquer beams every three blocks across a painted ceiling. */
	private static BlockState ceilingAt(int dx, int dz, int r) {
		return Math.floorMod(dx, 3) == 0 || Math.abs(dz) >= r + 1 ? lacquer() : wood();
	}

	/** Lacquer pillars at the corners and every four blocks, a lacquer cornice under the ceiling, painted wood between. */
	private static BlockState wallAt(int dx, int y, int dz, int r, int h) {
		int along = Math.abs(dx) == r + 1 ? dz : dx;
		boolean pillar = Math.floorMod(along, 4) == 0 || Math.abs(along) == r + 1;
		return pillar || y == h - 1 ? lacquer() : wood();
	}

	/** First furnishing: the exit Threshold, a carpet, a workbench, chests, shelves and flowers. */
	private static void furnish(ServerLevel level, BlockPos c, int tier) {
		int r = radius(tier);
		level.setBlock(spawn(c).below(), ModContent.block("threshold").defaultBlockState(), 3);
		BlockState carpet = Blocks.CARPET.red().defaultBlockState();
		for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) level.setBlock(c.offset(dx, 0, dz), carpet, 3);
		level.setBlock(c.offset(-2, 0, -r), Blocks.CRAFTING_TABLE.defaultBlockState(), 3);
		level.setBlock(c.offset(0, 0, -r), ModContent.block("nesting_chest").defaultBlockState(), 3);
		level.setBlock(c.offset(2, 0, -r), Blocks.BARREL.defaultBlockState(), 3);
		for (int dz = -1; dz <= 1; dz++) {
			level.setBlock(c.offset(-r, 0, dz), Blocks.BOOKSHELF.defaultBlockState(), 3);
			level.setBlock(c.offset(-r, 1, dz), Blocks.BOOKSHELF.defaultBlockState(), 3);
		}
		level.setBlock(c.offset(r, 0, -r), Blocks.POTTED_POPPY.defaultBlockState(), 3);
		level.setBlock(c.offset(r, 0, r), Blocks.POTTED_POPPY.defaultBlockState(), 3);
	}

	/** Pushes the walls and the ceiling outward: the old shell is taken down, what the players placed stays. */
	private static void grow(ServerLevel level, BlockPos c, int from, int to) {
		int r0 = radius(from), h0 = height(from);
		BlockState air = Blocks.AIR.defaultBlockState();
		for (int dx = -r0 - 1; dx <= r0 + 1; dx++) {
			for (int dz = -r0 - 1; dz <= r0 + 1; dz++) {
				boolean wall = Math.abs(dx) == r0 + 1 || Math.abs(dz) == r0 + 1;
				BlockPos top = c.offset(dx, h0, dz);
				if (shell(level.getBlockState(top))) level.setBlock(top, air, 3);
				BlockPos hang = top.below();
				if (level.getBlockState(hang).is(Blocks.LANTERN)) level.setBlock(hang, air, 3);
				if (wall) {
					for (int y = 0; y < h0; y++) {
						BlockPos p = c.offset(dx, y, dz);
						if (shell(level.getBlockState(p))) level.setBlock(p, air, 3);
					}
					level.setBlock(c.offset(dx, -1, dz), floorAt(dx, dz, radius(to)), 3);
				}
			}
		}
		build(level, c, to);
	}

	private static boolean shell(BlockState s) {
		return s.is(ModContent.block("painted_wood")) || s.is(ModContent.block("lacquer_block"));
	}

	/** Anyone who digs through the floor of a room falls back onto its Threshold. */
	private static void catchFalling(MinecraftServer server) {
		ServerLevel level = server.getLevel(Worlds.REFUGE);
		if (level == null) return;
		for (ServerPlayer p : level.players()) {
			if (p.getY() > FLOOR_Y - 24 || p.isSpectator()) continue;
			BlockPos c = center(parcelOf(p.blockPosition()));
			BlockPos s = spawn(c);
			p.teleportTo(level, s.getX() + 0.5, s.getY(), s.getZ() + 0.5, Set.of(), p.getYRot(), p.getXRot(), true);
			p.fallDistance = 0;
		}
	}
}
