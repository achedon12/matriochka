package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * World variants. While a Seed hatches, what it is fed and what lies around it lean it calm or wild; the planter's
 * karma at +100 or -100 makes it hallowed or cursed instead. The variant is stored in the group's world entry
 * ("variant") and changes the creatures, the strength of the rule and the drops of that parcel, never its terrain.
 */
public final class Variants {
	private Variants() {}

	public static final String PLAIN = "plain";
	/** Parcel owners per world, rebuilt every few seconds: spawn checks ask for them very often. */
	private static final Map<Long, String> OWNERS = new HashMap<>();
	private static long ownersAt = Long.MIN_VALUE, missedAt = Long.MIN_VALUE;

	public static Defs.VariantDef def(String id) {
		for (Defs.VariantDef v : Content.VARIANTS) if (v.id().equals(id)) return v;
		return Content.VARIANTS.getFirst();
	}

	/** The stored variant of a group's world ("plain" when none was chosen). */
	public static String of(MatrioData data, String group, int world) {
		String v = data.worldEntry(group, world).getStringOr("variant", PLAIN);
		return v.isEmpty() ? PLAIN : v;
	}

	public static void set(MatrioData data, String group, int world, String variant) {
		data.worldEntry(group, world).putString("variant", variant);
		data.changed();
	}

	/** The group whose parcel holds this position of a mod world, or null. */
	public static String groupAt(ServerLevel level, BlockPos pos) {
		int world = Worlds.number(level);
		if (world <= 0 || world > 10) return null;
		MinecraftServer server = level.getServer();
		long now = server.overworld().getGameTime();
		if (now - ownersAt > 100 || now < ownersAt) owners(server, now);
		String g = OWNERS.get(key(world, Worlds.parcelOf(pos)));
		// a parcel handed out since the last pass: look again, at most once a tick
		if (g == null && missedAt != now && ownersAt != now) {
			missedAt = now;
			owners(server, now);
			g = OWNERS.get(key(world, Worlds.parcelOf(pos)));
		}
		return g;
	}

	private static void owners(MinecraftServer server, long now) {
		OWNERS.clear();
		ownersAt = now;
		MatrioData data = MatrioData.get(server);
		for (String g : data.groups()) {
			CompoundTag grp = data.group(g);
			if (!grp.contains("parcel")) continue;
			for (int w = 1; w <= 10; w++) OWNERS.put(key(w, data.parcel(g, w)), g);
		}
	}

	/** Forgets the parcel owners (after a parcel changed hands). */
	public static void forget() {
		ownersAt = Long.MIN_VALUE;
	}

	private static long key(int world, int parcel) {
		return ((long) world << 32) | (parcel & 0xFFFFFFFFL);
	}

	/** The variant in force at a position (the parcel's), plain on the Surface and in parcels nobody owns. */
	public static Defs.VariantDef at(ServerLevel level, BlockPos pos) {
		String g = groupAt(level, pos);
		if (g == null) return Content.VARIANTS.getFirst();
		return def(of(MatrioData.get(level.getServer()), g, Worlds.number(level)));
	}

	/** The variant a player lives under: the one of their group's world they stand in. */
	public static Defs.VariantDef of(ServerPlayer p) {
		int world = Worlds.number(p.level());
		if (world <= 0 || world > 10) return Content.VARIANTS.getFirst();
		MatrioData data = MatrioData.get(p.level().getServer());
		return def(of(data, data.groupOf(p.getUUID()), world));
	}

	/** The translation key of a variant's name in a world: calm and wild have a name of their own in every world. */
	public static String nameKey(String variant, int world) {
		if ((variant.equals("calm") || variant.equals("wild")) && world >= 1 && world <= 10) return "variant.matriochka." + world + "." + variant;
		return "variant.matriochka." + variant;
	}

	// ---------------------------------------------------------------- choosing the variant while a Seed hatches
	private static boolean matches(List<String> ids, BlockState s) {
		for (String id : ids) {
			if (id.equals("minecraft:water") && s.getFluidState().is(net.minecraft.tags.FluidTags.WATER)) return true;
			if (id.equals("minecraft:lava") && s.getFluidState().is(net.minecraft.tags.FluidTags.LAVA)) return true;
			if (id.startsWith("#")) {
				if (s.is(TagKey.create(Registries.BLOCK, Identifier.parse(id.substring(1))))) return true;
			} else if (BuiltInRegistries.BLOCK.getKey(s.getBlock()).toString().equals(id)) {
				return true;
			}
		}
		return false;
	}

	private static boolean matches(List<String> ids, ItemStack stack) {
		for (String id : ids) {
			if (id.startsWith("#")) {
				if (stack.is(TagKey.create(Registries.ITEM, Identifier.parse(id.substring(1))))) return true;
			} else if (BuiltInRegistries.ITEM.getKey(stack.getItem()).toString().equals(id)) {
				return true;
			}
		}
		return false;
	}

	/**
	 * Feeds a hatching Seed: a calm or a wild offering moves its lean by one (kept in the seed's data as "lean",
	 * wild positive). Returns false when the item is neither.
	 */
	public static boolean feed(ServerLevel level, BlockPos pos, CompoundTag seed, ItemStack stack, ServerPlayer by) {
		int d = matches(Content.VARIANT_FEED_CALM, stack) ? -1 : matches(Content.VARIANT_FEED_WILD, stack) ? 1 : 0;
		if (d == 0) return false;
		int lean = Math.max(-6, Math.min(6, seed.getIntOr("lean", 0) + d));
		seed.putInt("lean", lean);
		stack.consume(1, by);
		level.sendParticles(d < 0 ? ParticleTypes.HAPPY_VILLAGER : ParticleTypes.SOUL_FIRE_FLAME, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5, 10, 0.3, 0.3, 0.3, 0.02);
		level.playSound(null, pos, d < 0 ? SoundEvents.AMETHYST_BLOCK_CHIME : SoundEvents.SOUL_ESCAPE.value(), SoundSource.BLOCKS, 0.8f, d < 0 ? 1.3f : 0.7f);
		by.sendOverlayMessage(Component.translatable(lean < 0 ? "message.matriochka.variant.lean_calm" : lean > 0 ? "message.matriochka.variant.lean_wild" : "message.matriochka.variant.lean_none", Math.abs(lean))
			.withStyle(lean < 0 ? ChatFormatting.GREEN : lean > 0 ? ChatFormatting.RED : ChatFormatting.GRAY));
		return true;
	}

	/** What the ground within 3 blocks says: one point per matching block, at most three each way (wild positive). */
	public static int groundLean(Level level, BlockPos pos) {
		int calm = 0, wild = 0;
		for (BlockPos q : BlockPos.betweenClosed(pos.offset(-3, -1, -3), pos.offset(3, 2, 3))) {
			BlockState s = level.getBlockState(q);
			if (s.isAir()) continue;
			if (calm < 3 && matches(Content.VARIANT_GROUND_CALM, s)) calm++;
			else if (wild < 3 && matches(Content.VARIANT_GROUND_WILD, s)) wild++;
		}
		return wild - calm;
	}

	/** The variant a Seed hatches into: karma first, then its lean (fed + ground). */
	public static String choose(int karma, int lean) {
		if (karma >= 100) return "blessed";
		if (karma <= -100) return "cursed";
		if (lean >= Content.VARIANT_LEAN) return "wild";
		if (lean <= -Content.VARIANT_LEAN) return "calm";
		return PLAIN;
	}

	/** Called when a Seed becomes a World Block: picks, stores and announces the variant. */
	public static String hatch(ServerLevel level, BlockPos pos, CompoundTag seed, String group, int world, String owner) {
		MatrioData data = MatrioData.get(level.getServer());
		int karma = seed.getIntOr("karma", 0);
		ServerPlayer planter = null;
		try {
			planter = owner.isEmpty() ? null : level.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(owner));
		} catch (IllegalArgumentException ignored) {
			// an old seed without a valid owner
		}
		if (planter != null) karma = PlayerState.of(planter).karma();
		int lean = seed.getIntOr("lean", 0) + groundLean(level, pos);
		String v = choose(karma, lean);
		if (group != null && !group.isEmpty()) set(data, group, world, v);
		if (!v.equals(PLAIN)) {
			Component name = Component.translatable(nameKey(v, world));
			for (ServerPlayer p : level.getServer().getPlayerList().getPlayers()) {
				if (group != null && data.groupOf(p.getUUID()).equals(group) && (p == planter || p.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(pos)) < 64 * 64)) {
					p.sendSystemMessage(Component.translatable("message.matriochka.variant.hatched", Component.translatable(Worlds.dimensionKey(world)), name)
						.withStyle(v.equals("calm") || v.equals("blessed") ? ChatFormatting.GREEN : ChatFormatting.RED));
				}
			}
		}
		return v;
	}

	/** Every variant of a group's worlds, for the Journal: world number to variant id (plain ones left out). */
	public static CompoundTag summary(MatrioData data, String group) {
		CompoundTag t = new CompoundTag();
		for (int w = 1; w <= 10; w++) {
			String v = of(data, group, w);
			if (!v.equals(PLAIN)) t.putString(Integer.toString(w), v);
		}
		return t;
	}

	/** The mutation a boss of this world wakes with under this variant ("" for none). */
	public static String mutation(String variant, int world) {
		if (world < Content.MUTATION_FROM || world > 10) return "";
		return switch (variant) {
			case "wild" -> Content.WILD_MUTATION[world];
			case "blessed" -> "radiant";
			case "cursed" -> "hollow";
			default -> "";
		};
	}
}
