package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.block.BedBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CandleBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.LecternBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BedPart;
import net.minecraft.world.level.portal.TeleportTransition;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * World 0, the smallest doll (dimension {@code matriochka:world_zero}, internal number {@link Worlds#ZERO}).
 * <p>
 * Layout, built once per group at the centre of its parcel, all of it sealed in unbreakable brick and dressed in
 * painted wood and lacquer: an entry hall with the Threshold, three chambers that replay the prisons three by three
 * (worlds 1-3, 4-6, 7-9) and each hold their elite guards behind a sealed gate, then the Artisan's room: his bed,
 * his bench, the first Scroll on a lectern, an empty doll his size, and on a table a cracked doll holding a tiny
 * Surface (the reveal: the Surface was one more doll).
 * <p>
 * Rule, Obsession (the synthesis of the ten laws): every finished gesture feeds the creature. Holding something
 * raises the gauge, every strike raises it more, only empty hands lower it. Past half it slows your hands, past
 * three quarters it weakens them, full it hurts and heals the Shadow.
 * <p>
 * Encounter: the Artisan's Shadow wakes in the room. It cannot be finished: brought near death it stitches itself
 * back. Once it has, kneeling (sneaking) empty-handed on the carpet before the bench for ten seconds calms it and
 * plays the third ending, Set Down the Tools; the kneel stills the creatures it called in too, which unravel.
 */
public final class WorldZero {
	/** Height of the floor of every room. */
	public static final int Y = 64;
	// interiors, relative to the origin (the centre of the entry hall's threshold wall), inclusive ranges
	private static final int[] HALL = {-6, 6, 0, 7, 0, 12};
	private static final int[] CONNECT = {-2, 2, 0, 4, 13, 13};
	private static final int CH_Z0 = 14, CH_STEP = 22, CH_LEN = 19, CH_X = 9, CH_H = 10;
	private static final int ROOM_Z0 = 80, ROOM_Z1 = 104, ROOM_X = 12, ROOM_H = 12;
	private static final int KNEEL_Z = 95;
	private static final BlockPos DIORAMA = new BlockPos(-7, 0, 90);
	private static final BlockPos SHADOW_AT = new BlockPos(0, 0, 87);
	private static final String[][] GUARDS = {
		{"chitin_guard", "slag_golem", "executioner"},
		{"island_warden", "shadow_mother", "broken_mirror"},
		{"bell_crab", "hour_keeper", "walking_column"}};
	private static final int KNEEL_SECONDS = 10;

	private WorldZero() {}

	public static void init() {
		// every strike in World 0 feeds the Obsession
		ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, base, taken, blocked) -> {
			if (source.getEntity() instanceof ServerPlayer p && Worlds.number(p.level()) == Worlds.ZERO) PlayerState.of(p).addGauge("obsession", 3);
		});
	}

	private static int chamberZ(int k) {
		return CH_Z0 + k * CH_STEP;
	}

	/** First z of the corridor (and gate) that leaves chamber k. */
	private static int gateZ(int k) {
		return chamberZ(k) + CH_LEN;
	}

	private static List<int[]> spaces() {
		List<int[]> out = new ArrayList<>();
		out.add(HALL);
		out.add(CONNECT);
		for (int k = 0; k < 3; k++) {
			out.add(new int[]{-CH_X, CH_X, 0, CH_H, chamberZ(k), chamberZ(k) + CH_LEN - 1});
			out.add(new int[]{-2, 2, 0, 4, gateZ(k), gateZ(k) + 2});
		}
		out.add(new int[]{-ROOM_X, ROOM_X, 0, ROOM_H, ROOM_Z0, ROOM_Z1});
		return out;
	}

	/** The middle of the gate that closes chamber k (used by the story check). */
	public static BlockPos gateCenter(BlockPos o, int k) {
		return o.offset(0, 2, gateZ(k) + 1);
	}

	public static BlockPos chamberCenter(BlockPos o, int k) {
		return o.offset(0, 0, chamberZ(k) + CH_LEN / 2);
	}

	/** Where to kneel before the bench. */
	public static BlockPos kneelSpot(BlockPos o) {
		return o.offset(0, 0, KNEEL_Z);
	}

	private static AABB complex(BlockPos o) {
		return new AABB(o.getX() - ROOM_X - 3, o.getY() - 3, o.getZ() - 3, o.getX() + ROOM_X + 3, o.getY() + ROOM_H + 3, o.getZ() + ROOM_Z1 + 3);
	}

	private static AABB chamber(BlockPos o, int k) {
		return new AABB(o.getX() - CH_X, o.getY(), o.getZ() + chamberZ(k), o.getX() + CH_X + 1, o.getY() + CH_H + 1, o.getZ() + chamberZ(k) + CH_LEN);
	}

	private static AABB room(BlockPos o) {
		return new AABB(o.getX() - ROOM_X, o.getY(), o.getZ() + ROOM_Z0, o.getX() + ROOM_X + 1, o.getY() + ROOM_H + 1, o.getZ() + ROOM_Z1 + 1);
	}

	// ---------------------------------------------------------------- entering
	/** Opens the Whole Matryoshka: the player shrinks into World 0, inside the smallest doll. */
	public static void enter(ServerPlayer p) {
		MinecraftServer server = p.level().getServer();
		ServerLevel level = server.getLevel(Worlds.WORLD_ZERO);
		if (level == null) {
			p.sendSystemMessage(Component.translatable("message.matriochka.no_dimension"));
			return;
		}
		if (Worlds.number(p.level()) != Worlds.ZERO) {
			CompoundTag ret = new CompoundTag();
			ret.putString("dim", p.level().dimension().identifier().toString());
			ret.putInt("x", p.getBlockX());
			ret.putInt("y", p.getBlockY());
			ret.putInt("z", p.getBlockZ());
			PlayerState.of(p).tag().put("return", ret);
		}
		MatrioData data = MatrioData.get(server);
		BlockPos o = origin(data, data.groupOf(p.getUUID()), level);
		p.teleport(new TeleportTransition(level, Vec3.atBottomCenterOf(o.offset(0, 0, 5)), Vec3.ZERO, 0f, 0f, Set.of(), TeleportTransition.PLAY_PORTAL_SOUND));
		level.playSound(null, o, fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, SoundSource.PLAYERS, 1.2f, 0.6f);
		p.sendSystemMessage(Component.translatable("message.matriochka.zero.enter").withStyle(ChatFormatting.GOLD));
		p.sendSystemMessage(Component.translatable("message.matriochka.entered", Component.translatable(Worlds.dimensionKey(Worlds.ZERO))));
		Achievements.grantId(p, "endings/world_zero");
	}

	/** The origin of a group's World 0, building it the first time. */
	public static BlockPos origin(MatrioData data, String group, ServerLevel level) {
		CompoundTag e = data.worldEntry(group, Worlds.ZERO);
		BlockPos c = Worlds.parcelCenter(data.parcel(group));
		BlockPos o = new BlockPos(c.getX(), Y, c.getZ());
		if (!e.getBooleanOr("built", false)) {
			build(level, o);
			e.putBoolean("built", true);
			data.changed();
		}
		return o;
	}

	// ---------------------------------------------------------------- building
	private static BlockState b(String id) {
		return ModContent.block(id).defaultBlockState();
	}

	private static void set(ServerLevel level, BlockPos o, int x, int y, int z, BlockState s) {
		level.setBlock(o.offset(x, y, z), s, 2);
	}

	static void build(ServerLevel level, BlockPos o) {
		BlockState shell = b("sealed_brick");
		// 1. one sealed block of brick around the whole complex
		for (int x = -ROOM_X - 2; x <= ROOM_X + 2; x++)
			for (int y = -2; y <= ROOM_H + 2; y++)
				for (int z = -2; z <= ROOM_Z1 + 2; z++) set(level, o, x, y, z, shell);
		List<int[]> spaces = spaces();
		// 2. the painted skin of every space (floor, walls, ceiling), 3. then every interior carved out
		for (int i = 0; i < spaces.size(); i++) skin(level, o, spaces.get(i), i);
		for (int[] s : spaces)
			for (int x = s[0]; x <= s[1]; x++)
				for (int y = s[2]; y <= s[3]; y++)
					for (int z = s[4]; z <= s[5]; z++) set(level, o, x, y, z, Blocks.AIR.defaultBlockState());
		// gates, the Threshold, lights and the room
		for (int k = 0; k < 3; k++) gate(level, o, k, true);
		set(level, o, 0, 0, 1, b("threshold"));
		hallDressing(level, o);
		for (int k = 0; k < 3; k++) chamberDressing(level, o, k);
		roomDressing(level, o);
	}

	/** Index of a space in {@link #spaces()}: 0 hall, 1 connector, 2/4/6 chambers, 3/5/7 corridors, 8 room. */
	private static void skin(ServerLevel level, BlockPos o, int[] s, int index) {
		// the gated corridors keep their bare brick, so that nobody digs around a gate
		if (index == 3 || index == 5 || index == 7) return;
		boolean chamberSpace = index >= 2 && index <= 7 && index % 2 == 0;
		int k = (index - 2) / 2;
		for (int x = s[0] - 1; x <= s[1] + 1; x++)
			for (int y = s[2] - 1; y <= s[3] + 1; y++)
				for (int z = s[4] - 1; z <= s[5] + 1; z++) {
					boolean floor = y == s[2] - 1, ceil = y == s[3] + 1;
					BlockState st;
					if (chamberSpace) {
						int theme = 1 + k * 3 + Math.min(2, (x - s[0]) * 3 / (s[1] - s[0] + 1));
						if (floor) st = (Math.floorMod(x + z, 4) == 0) ? Arenas.trimFor(theme) : Arenas.floorFor(theme);
						else if (ceil) st = Math.floorMod(x, 5) == 0 && Math.floorMod(z, 5) == 0 && k != 1 ? Arenas.accentFor(theme) : Arenas.floorFor(theme);
						else st = y == s[2] + 3 ? Arenas.accentFor(theme) : Arenas.trimFor(theme);
					} else if (index == 8) {
						if (floor) st = Math.floorMod(x, 6) == 0 || Math.floorMod(z, 6) == 0 ? b("lacquer_block") : b("giant_plank");
						else if (ceil) st = Math.floorMod(x, 4) == 0 && Math.floorMod(z, 4) == 0 ? b("lacquer_glow") : b("lacquer_block");
						else st = y == s[2] + 4 ? b("lacquer_block") : b("painted_wood");
					} else {
						if (floor) st = index == 0 ? b("workshop_felt") : b("lacquer_block");
						else if (ceil) st = b("lacquer_block");
						else st = b("painted_wood");
					}
					set(level, o, x, y, z, st);
				}
	}

	/** The gate that closes the corridor after chamber k: five by five of unbreakable sealed brick. */
	private static void gate(ServerLevel level, BlockPos o, int k, boolean closed) {
		int z = gateZ(k) + 1;
		for (int x = -2; x <= 2; x++)
			for (int y = 0; y <= 4; y++) set(level, o, x, y, z, closed ? b("sealed_brick") : Blocks.AIR.defaultBlockState());
		if (!closed) level.playSound(null, o.offset(0, 1, z), SoundEvents.IRON_DOOR_OPEN, SoundSource.BLOCKS, 1.5f, 0.5f);
	}

	private static BlockState hanging() {
		return Blocks.LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, true);
	}

	private static void hallDressing(ServerLevel level, BlockPos o) {
		for (int z = 3; z <= 11; z += 4) {
			set(level, o, -3, HALL[3], z, hanging());
			set(level, o, 3, HALL[3], z, hanging());
		}
		for (int x = -1; x <= 1; x++) for (int z = 2; z <= 12; z++) set(level, o, x, -1, z, b("lacquer_block"));
		for (int[] p : new int[][]{{-6, 2}, {6, 2}, {-6, 10}, {6, 10}}) {
			for (int y = 0; y <= 3; y++) set(level, o, p[0], y, p[1], y == 3 ? b("lacquer_glow") : b("giant_plank"));
		}
	}

	private static void chamberDressing(ServerLevel level, BlockPos o, int k) {
		int z0 = chamberZ(k);
		// four pillars in the chamber's three laws, and a few lights low enough to see by
		for (int[] p : new int[][]{{-5, 5}, {5, 5}, {-5, 13}, {5, 13}}) {
			int theme = 1 + k * 3 + (p[0] < 0 ? 0 : 2);
			for (int y = 0; y <= CH_H; y++) set(level, o, p[0], y, z0 + p[1], y % 4 == 3 ? Arenas.accentFor(theme) : Arenas.trimFor(theme));
		}
		if (k == 1) {
			// the dark chamber: only two faint lights
			set(level, o, 0, 0, z0 + 9, b("faint_glow"));
			set(level, o, 0, CH_H, z0 + 9, b("faint_glow"));
		} else if (k == 2) {
			// the wet chamber: shallow pools in the floor
			for (int[] p : new int[][]{{-3, 3}, {4, 8}, {-6, 15}, {2, 14}}) {
				for (int dx = 0; dx <= 1; dx++) for (int dz = 0; dz <= 1; dz++) set(level, o, p[0] + dx, -1, z0 + p[1] + dz, Blocks.WATER.defaultBlockState());
			}
		} else {
			for (int[] p : new int[][]{{-8, 9}, {8, 9}}) set(level, o, p[0], 0, z0 + p[1], Blocks.CAMPFIRE.defaultBlockState());
		}
	}

	private static void roomDressing(ServerLevel level, BlockPos o) {
		// lanterns hang over the room
		for (int x = -8; x <= 8; x += 8) for (int z = ROOM_Z0 + 3; z <= ROOM_Z1 - 3; z += 7) set(level, o, x, ROOM_H, z, hanging());
		// bookshelves along both walls
		for (int z = ROOM_Z0 + 5; z <= ROOM_Z0 + 13; z++)
			for (int y = 0; y <= 2; y++) {
				set(level, o, -ROOM_X, y, z, Blocks.BOOKSHELF.defaultBlockState());
				set(level, o, ROOM_X, y, z, Blocks.BOOKSHELF.defaultBlockState());
			}
		// his bed
		BlockState bed = fr.achedon12.matriochka.mc.McBlocks.BED.red().defaultBlockState().setValue(BedBlock.FACING, Direction.SOUTH);
		set(level, o, 9, 0, ROOM_Z0 + 2, bed.setValue(BedBlock.PART, BedPart.FOOT));
		set(level, o, 9, 0, ROOM_Z0 + 3, bed.setValue(BedBlock.PART, BedPart.HEAD));
		set(level, o, 10, 0, ROOM_Z0 + 3, Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.LIT, true));
		// the kneeling carpet before the bench
		for (int x = -1; x <= 1; x++) for (int z = KNEEL_Z - 1; z <= KNEEL_Z; z++) set(level, o, x, 0, z, fr.achedon12.matriochka.mc.McBlocks.CARPET.red().defaultBlockState());
		// the bench, the first Scroll on its lectern, candles at both ends
		for (int x = -4; x <= 4; x++) for (int z = KNEEL_Z + 2; z <= KNEEL_Z + 3; z++) set(level, o, x, 0, z, b("giant_plank"));
		set(level, o, 0, 1, KNEEL_Z + 2, Blocks.LECTERN.defaultBlockState().setValue(LecternBlock.FACING, Direction.NORTH));
		for (int x : new int[]{-4, 4}) set(level, o, x, 1, KNEEL_Z + 2, Blocks.CANDLE.defaultBlockState().setValue(CandleBlock.CANDLES, 3).setValue(CandleBlock.LIT, true));
		set(level, o, -2, 1, KNEEL_Z + 3, Blocks.CHISELED_BOOKSHELF.defaultBlockState());
		set(level, o, 2, 1, KNEEL_Z + 3, b("lacquer_block"));
		// an empty doll his size against the back wall, open at the front
		int dz0 = KNEEL_Z + 5;
		for (int x = -2; x <= 2; x++)
			for (int z = dz0; z <= dz0 + 4; z++)
				for (int y = 0; y <= 7; y++) {
					boolean upper = y >= 4;
					int r = upper ? 1 : 2, cz = dz0 + 2;
					if (Math.abs(x) > r || Math.abs(z - cz) > r) continue;
					boolean edge = Math.abs(x) == r || Math.abs(z - cz) == r || y == 7;
					boolean door = z == cz - r && Math.abs(x) <= 1 && y <= 2;
					if (!edge || door) continue;
					BlockState st = y == 3 ? Blocks.GOLD_BLOCK.defaultBlockState() : upper && z == cz - r && y == 5 ? Blocks.SMOOTH_QUARTZ.defaultBlockState() : b("lacquer_block");
					set(level, o, x, y, z, st);
				}
		// the diorama: a cracked doll on a table, holding a tiny Surface
		int tx = DIORAMA.getX(), tz = DIORAMA.getZ();
		for (int x = -2; x <= 2; x++)
			for (int z = -2; z <= 2; z++) {
				set(level, o, tx + x, 0, tz + z, b("painted_wood"));
				boolean rim = Math.abs(x) == 2 || Math.abs(z) == 2;
				set(level, o, tx + x, 1, tz + z, rim ? b("lacquer_block") : Blocks.GRASS_BLOCK.defaultBlockState());
				// the upper half of the doll lies broken: only one side of its rim is left
				if (rim && x + z < 0) set(level, o, tx + x, 2, tz + z, b("lacquer_block"));
			}
		set(level, o, tx - 1, 2, tz - 1, Blocks.OAK_SAPLING.defaultBlockState());
		set(level, o, tx + 1, 2, tz - 1, Blocks.POPPY.defaultBlockState());
		set(level, o, tx - 1, 2, tz + 1, Blocks.OAK_PLANKS.defaultBlockState());
		set(level, o, tx - 1, 3, tz + 1, Blocks.OAK_SLAB.defaultBlockState());
		set(level, o, tx + 1, 2, tz + 1, Blocks.CHISELED_STONE_BRICKS.defaultBlockState());
		set(level, o, tx, 1, tz, Blocks.DIRT_PATH.defaultBlockState());
	}

	// ---------------------------------------------------------------- the rule and the encounter, once per second
	public static void tick(MinecraftServer server) {
		if (server.overworld().getGameTime() % 20 != 0) return;
		ServerLevel level = server.getLevel(Worlds.WORLD_ZERO);
		MatrioData data = MatrioData.get(server);
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			PlayerState ps = PlayerState.of(p);
			if (p.level() != level || level == null) {
				if (ps.gauge("obsession") > 0) ps.setGauge("obsession", 0);
				continue;
			}
			if (p.isSpectator()) continue;
			String group = data.groupOf(p.getUUID());
			CompoundTag e = data.worldEntry(group, Worlds.ZERO);
			BlockPos o = origin(data, group, level);
			obsession(p, ps, level, o);
			progress(p, ps, level, data, e, o);
		}
	}

	private static void obsession(ServerPlayer p, PlayerState ps, ServerLevel level, BlockPos o) {
		boolean main = !p.getMainHandItem().isEmpty(), off = !p.getOffhandItem().isEmpty();
		ps.addGauge("obsession", !main && !off ? -6f : (main ? 1.5f : 0) + (off ? 0.5f : 0));
		float v = ps.gauge("obsession");
		if (v >= 50) p.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 40, 0, true, false));
		if (v >= 75) p.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 40, 0, true, false));
		if (v >= 100) {
			p.hurtServer(level, level.damageSources().magic(), 2f);
			if (level.getGameTime() % 200 == 0) p.sendOverlayMessage(Component.translatable("message.matriochka.zero.obsession").withStyle(ChatFormatting.DARK_RED));
			MatrioBoss shadow = shadow(level, o);
			if (shadow != null) shadow.heal(shadow.getMaxHealth() * 0.01f);
		}
	}

	private static MatrioBoss shadow(ServerLevel level, BlockPos o) {
		List<MatrioBoss> l = level.getEntitiesOfClass(MatrioBoss.class, complex(o), b -> b.def.world() == Worlds.ZERO);
		return l.isEmpty() ? null : l.getFirst();
	}

	private static void progress(ServerPlayer p, PlayerState ps, ServerLevel level, MatrioData data, CompoundTag e, BlockPos o) {
		int rz = p.getBlockZ() - o.getZ();
		// the chambers: guards wake when you step in, the gate opens when they are gone
		for (int k = 0; k < 3; k++) {
			if (chamber(o, k).contains(p.position()) && !e.getBooleanOr("spawned_" + k, false)) {
				e.putBoolean("spawned_" + k, true);
				data.changed();
				spawnGuards(level, o, k, p);
				p.sendSystemMessage(Component.translatable("message.matriochka.zero.chamber." + k).withStyle(ChatFormatting.GRAY));
			}
			String guard = "zero_" + k;
			if (e.getBooleanOr("spawned_" + k, false) && !e.getBooleanOr("open_" + k, false)
				&& level.getEntitiesOfClass(MatrioMob.class, complex(o), m -> m.entityTags().contains(guard)).isEmpty()) {
				e.putBoolean("open_" + k, true);
				data.changed();
				gate(level, o, k, false);
				p.sendSystemMessage(Component.translatable("message.matriochka.zero.cleared").withStyle(ChatFormatting.GOLD));
			}
		}
		if (!room(o).contains(p.position())) return;
		if (!ps.has("zero_room")) {
			ps.set("zero_room", true);
			p.sendSystemMessage(Component.translatable("message.matriochka.zero.room").withStyle(ChatFormatting.GOLD));
		}
		if (!ps.has("zero_diorama") && p.position().distanceTo(Vec3.atCenterOf(o.offset(DIORAMA))) < 4) {
			ps.set("zero_diorama", true);
			p.sendSystemMessage(Component.translatable("message.matriochka.zero.diorama").withStyle(ChatFormatting.LIGHT_PURPLE));
		}
		if (e.getBooleanOr("ended", false)) return;
		MatrioBoss shadow = shadow(level, o);
		if (shadow == null) {
			shadow = MatrioBoss.summon(level, "artisan_shadow", o.offset(SHADOW_AT), p);
			if (shadow != null) p.sendSystemMessage(Component.translatable("message.matriochka.zero.wake").withStyle(ChatFormatting.DARK_RED));
			return;
		}
		// the creatures a kneel froze a second ago fall back into thread, whether the player still kneels or not
		quiet(level, o, false);
		// setting down the tools: kneel empty-handed on the carpet, once the Shadow has shown it cannot be finished
		boolean kneels = e.getBooleanOr("stitched", false) && p.isShiftKeyDown() && p.getMainHandItem().isEmpty() && p.getOffhandItem().isEmpty()
			&& p.position().distanceTo(Vec3.atBottomCenterOf(o.offset(0, 0, KNEEL_Z))) < 2.2 && rz >= ROOM_Z0;
		if (!kneels) {
			if (ps.counter("zero_kneel") != 0) ps.addCounter("zero_kneel", -ps.counter("zero_kneel"));
			return;
		}
		ps.addCounter("zero_kneel", 1);
		shadow.calm(40);
		calmRoom(level, o);
		level.sendParticles(ParticleTypes.ENCHANT, p.getX(), p.getY() + 1, p.getZ(), 20, 0.6, 0.6, 0.6, 0.5);
		if (ps.counter("zero_kneel") == 1) p.sendSystemMessage(Component.translatable("message.matriochka.zero.kneel").withStyle(ChatFormatting.GOLD));
		if (ps.counter("zero_kneel") >= KNEEL_SECONDS) finish(level, data, e, o, shadow);
	}

	/** Tag of the creatures a kneeling player has stilled; they unravel on the next second. */
	private static final String STILLED = "zero_stilled";

	/**
	 * Kneeling quiets the whole room, not only the Shadow: the creatures it called in with the attacks it borrows from
	 * the worlds (sporelings, Shadow Mothers...) let go of the player and freeze where they stand, in a ring of loose
	 * thread, and the blows already thrown at the player (arrows, fireballs, toxic clouds) fade.
	 */
	private static void calmRoom(ServerLevel level, BlockPos o) {
		for (Mob m : level.getEntitiesOfClass(Mob.class, complex(o), WorldZero::shadowCreature)) {
			if (m.entityTags().contains(STILLED)) continue;
			m.addTag(STILLED);
			m.setTarget(null);
			m.setAggressive(false);
			m.getNavigation().stop();
			m.setDeltaMovement(Vec3.ZERO);
			m.setNoAi(true);
			double h = m.getBbHeight();
			level.sendParticles(fr.achedon12.matriochka.content.Particles.THREAD_SCRAP, m.getX(), m.getY() + h * 0.5, m.getZ(), 14, m.getBbWidth() * 0.6, h * 0.4, m.getBbWidth() * 0.6, 0.01);
			level.sendParticles(ParticleTypes.ENCHANT, m.getX(), m.getY() + h + 0.3, m.getZ(), 12, 0.3, 0.2, 0.3, 0.6);
			level.playSound(null, m.blockPosition(), SoundEvents.WOOL_BREAK, SoundSource.HOSTILE, 0.7f, 0.6f);
		}
		for (net.minecraft.world.entity.Entity e : level.getEntitiesOfClass(net.minecraft.world.entity.Entity.class, complex(o),
			e -> (e instanceof net.minecraft.world.entity.projectile.Projectile pr && !(pr.getOwner() instanceof ServerPlayer))
				|| (e instanceof net.minecraft.world.entity.AreaEffectCloud c && !(c.getOwner() instanceof ServerPlayer)))) {
			level.sendParticles(fr.achedon12.matriochka.content.Particles.GOLD_MOTE, e.getX(), e.getY() + 0.2, e.getZ(), 6, 0.2, 0.2, 0.2, 0.01);
			e.discard();
		}
	}

	/**
	 * The stilled creatures unravel: they come apart into thread scraps and gold dust and are gone (all of them and every
	 * creature of the room once the tools are set down).
	 */
	private static void quiet(ServerLevel level, BlockPos o, boolean all) {
		for (Mob m : level.getEntitiesOfClass(Mob.class, complex(o), m -> shadowCreature(m) && (all || m.entityTags().contains(STILLED)))) {
			double h = m.getBbHeight(), w = m.getBbWidth();
			level.sendParticles(fr.achedon12.matriochka.content.Particles.THREAD_SCRAP, m.getX(), m.getY() + h * 0.5, m.getZ(), 26, w * 0.5, h * 0.45, w * 0.5, 0.03);
			level.sendParticles(fr.achedon12.matriochka.content.Particles.GOLD_MOTE, m.getX(), m.getY() + h * 0.5, m.getZ(), 18, w * 0.5, h * 0.45, w * 0.5, 0.02);
			level.playSound(null, m.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.HOSTILE, 0.6f, 1.4f);
			m.discard();
		}
	}

	/** A creature of the room the Shadow could set on the player: every Matriochka creature or hostile mob, not the Shadow. */
	private static boolean shadowCreature(Mob m) {
		return m.isAlive() && !(m instanceof MatrioBoss) && (m instanceof MatrioMob || m instanceof net.minecraft.world.entity.monster.Enemy);
	}

	private static void spawnGuards(ServerLevel level, BlockPos o, int k, ServerPlayer target) {
		int z0 = chamberZ(k);
		List<String> ids = new ArrayList<>(List.of(GUARDS[k]));
		for (int t = 1; t <= 3; t++) {
			int theme = 1 + k * 3 + t - 1;
			for (Defs.MobDef m : Content.MOBS) {
				if (m.world() == theme && !m.elite() && !m.flying() && !m.aquatic()) {
					ids.add(m.id());
					break;
				}
			}
		}
		int[][] at = {{-4, 9}, {4, 9}, {0, 14}, {-6, 4}, {6, 4}, {0, 4}};
		for (int i = 0; i < ids.size(); i++) {
			var e = ModContent.entity(ids.get(i)).create(level, EntitySpawnReason.EVENT);
			if (!(e instanceof MatrioMob mob)) continue;
			int[] p = at[i % at.length];
			mob.setPos(o.getX() + p[0] + 0.5, o.getY(), o.getZ() + z0 + p[1] + 0.5);
			mob.setPersistenceRequired();
			mob.addTag("zero_" + k);
			mob.addTag("zero_guard");
			mob.setTarget(target);
			level.addFreshEntity(mob);
			level.sendParticles(ParticleTypes.POOF, mob.getX(), mob.getY() + 1, mob.getZ(), 12, 0.4, 0.6, 0.4, 0.02);
		}
		level.playSound(null, o.offset(0, 1, z0 + 9), SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 0.5f, 1.4f);
	}

	/** The Shadow, brought near death, stitches itself back: from then on, it can be set down. */
	public static void onStitch(ServerLevel level, MatrioBoss shadow) {
		MatrioData data = MatrioData.get(level.getServer());
		String group = data.groupOfParcel(Worlds.parcelOf(shadow.blockPosition()));
		if (group != null) {
			data.worldEntry(group, Worlds.ZERO).putBoolean("stitched", true);
			data.changed();
		}
		level.sendParticles(ParticleTypes.WAX_ON, shadow.getX(), shadow.getY() + 1.5, shadow.getZ(), 60, 1, 1.5, 1, 0.2);
		level.playSound(null, shadow.blockPosition(), SoundEvents.ARMOR_EQUIP_LEATHER.value(), SoundSource.HOSTILE, 2f, 0.5f);
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, shadow.getBoundingBox().inflate(40))) {
			p.sendSystemMessage(Component.translatable("message.matriochka.zero.stitch").withStyle(ChatFormatting.DARK_RED));
			PlayerState.of(p).addGauge("obsession", 15);
		}
	}

	private static void finish(ServerLevel level, MatrioData data, CompoundTag e, BlockPos o, MatrioBoss shadow) {
		e.putBoolean("ended", true);
		data.changed();
		level.sendParticles(ParticleTypes.TOTEM_OF_UNDYING, shadow.getX(), shadow.getY() + 1.5, shadow.getZ(), 120, 1, 1.5, 1, 0.4);
		level.playSound(null, shadow.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.HOSTILE, 1.5f, 0.6f);
		shadow.discard();
		quiet(level, o, true);
		set(level, o, 3, 0, KNEEL_Z - 3, b("threshold"));
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, complex(o))) {
			PlayerState.of(p).setGauge("obsession", 0);
			PlayerState.of(p).addCounter("zero_kneel", -PlayerState.of(p).counter("zero_kneel"));
			p.sendSystemMessage(Component.translatable("message.matriochka.zero.done").withStyle(ChatFormatting.GOLD));
			Endings.play(p, Endings.TOOLS);
		}
	}
}
