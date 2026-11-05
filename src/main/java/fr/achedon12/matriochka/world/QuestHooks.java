package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.rules.PlayerState;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.Vec3;

/**
 * What the quests watch beyond kills, crafts and trades, so each one checks what its description says.
 * <p>
 * Objective kinds (content.py QUESTS, "kind:target" counters in PlayerState):
 * read (distinct Scroll pages), craft (a "+" target needs every part), brew (a ripe Spore Vat brew), station (any craft
 * at that station), deliver (hand the items to a person of the quest's world, "@day" by day only), mine (break that
 * block), mapped (reach the place a Labyrinth Map named), courier (carry the item into that many structure types of
 * the world), glide (glides of 24 blocks in World 4), use_in / use_each ("structure/item": use the item inside such a
 * structure, use_each once per structure), spot (hostile creatures revealed by the sonar), meet (talk to that many
 * different people), summit / bottom (top or bottom of a structure), visit_each (that many different structures of a
 * type), visit (structure types of a world visited), seasons (seasons lived in World 8), search (shelves and lecterns
 * of a structure), find (the Maquette on the Titanic Workbench), tools (worlds whose gear you used), and kill with an
 * "@condition": no_mask, no_armor, near_people, no_layer (no Doll of Life layer lost during the boss fight).
 */
public final class QuestHooks {
	private QuestHooks() {}

	/** Gear kinds that count as "a tool of the world" for Every Tool. */
	private static final Set<String> TOOL_KINDS = Set.of("weapon", "drill", "tool", "glider", "hook", "lantern", "sonar", "hourglass", "thruster", "anchor");
	/** Horizontal length of a glide that counts as crossing an island. */
	public static final double GLIDE = 24;
	private static final Map<UUID, Vec3> GLIDES = new HashMap<>();

	public static void init() {
		PlayerBlockBreakEvents.AFTER.register((level, player, pos, state, be) -> {
			if (!(player instanceof ServerPlayer sp)) return;
			var key = BuiltInRegistries.BLOCK.getKey(state.getBlock());
			if (key.getNamespace().equals(Matriochka.MOD_ID) && !open(sp, "mine").isEmpty()) PlayerState.of(sp).progress("mine", key.getPath(), 1);
			toolUsed(sp, sp.getMainHandItem());
		});
		UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
			if (player instanceof ServerPlayer sp && level instanceof ServerLevel sl) search(sp, sl, hit.getBlockPos());
			return InteractionResult.PASS;
		});
		ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, base, taken, blocked) -> {
			if (source.getEntity() instanceof ServerPlayer p && source.getDirectEntity() == p && taken > 0) toolUsed(p, p.getMainHandItem());
		});
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (source.getEntity() instanceof ServerPlayer p && entity instanceof MatrioMob mob && !(entity instanceof MatrioBoss)) killed(p, mob, mob.def().id(), Set.of());
		});
	}

	// ---------------------------------------------------------------- helpers
	/** The quests of a kind this player could progress right now: available, not done. */
	public static List<Defs.QuestDef> open(ServerPlayer p, String kind) {
		List<Defs.QuestDef> out = new ArrayList<>();
		PlayerState ps = PlayerState.of(p);
		for (Defs.QuestDef q : Content.QUESTS) {
			if (q.objKind().equals(kind) && !Quests.done(ps, q) && Quests.available(p, q)) out.add(q);
		}
		return out;
	}

	/** Raises a counter to an exact value (distinct things counted elsewhere), completing the quest when it is reached. */
	public static void setProgress(ServerPlayer p, String kind, String target, int value) {
		PlayerState ps = PlayerState.of(p);
		int now = ps.counter(kind + ":" + target);
		if (value > now) ps.progress(kind, target, value - now);
	}

	/** One step of a quest done: "Quest: 2 / 5" over the hotbar (the last step is told by the completion message). */
	private static void step(ServerPlayer p, Defs.QuestDef q) {
		int n = Quests.progress(PlayerState.of(p), q);
		if (n >= q.objCount()) return;
		p.sendOverlayMessage(Component.translatable("message.matriochka.quest.step", Component.translatable("quest.matriochka." + q.id()), n, q.objCount()).withStyle(ChatFormatting.GOLD));
	}

	private static String item(String target) {
		int at = target.indexOf('@');
		return at < 0 ? target : target.substring(0, at);
	}

	private static String condition(String target) {
		int at = target.indexOf('@');
		return at < 0 ? "" : target.substring(at + 1);
	}

	/** The start of a structure of this id containing the position, or null. */
	public static StructureStart startAt(ServerLevel level, BlockPos pos, String id) {
		var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).get(ResourceKey.create(Registries.STRUCTURE, Matriochka.id(id)));
		if (holder.isEmpty()) return null;
		StructureStart start = level.structureManager().getStructureAt(pos, holder.get().value());
		return start.isValid() ? start : null;
	}

	// ---------------------------------------------------------------- kills
	/** A creature fell to a player: the kill quests that ask for a condition. Bosses pass the flags of their fight. */
	public static void killed(ServerPlayer p, LivingEntity victim, String id, Set<String> fightFlags) {
		for (Defs.QuestDef q : open(p, "kill")) {
			if (!item(q.objTarget()).equals(id) || condition(q.objTarget()).isEmpty()) continue;
			if (holds(p, victim, condition(q.objTarget()), fightFlags)) PlayerState.of(p).progress("kill", q.objTarget(), 1);
		}
	}

	private static boolean holds(ServerPlayer p, LivingEntity victim, String cond, Set<String> fightFlags) {
		return switch (cond) {
			case "no_mask" -> {
				ItemStack head = p.getItemBySlot(EquipmentSlot.HEAD);
				yield !head.is(ModContent.item("filter_mask")) && !fr.achedon12.matriochka.rules.Snorkel.is(head);
			}
			case "no_armor" -> p.getItemBySlot(EquipmentSlot.HEAD).isEmpty() && p.getItemBySlot(EquipmentSlot.CHEST).isEmpty()
				&& p.getItemBySlot(EquipmentSlot.LEGS).isEmpty() && p.getItemBySlot(EquipmentSlot.FEET).isEmpty();
			case "near_people" -> !victim.level().getEntitiesOfClass(MatrioNpc.class, victim.getBoundingBox().inflate(16), n -> n.def.world() > 0).isEmpty();
			case "no_layer" -> !fightFlags.contains("layer") && !fightFlags.contains("died");
			default -> false;
		};
	}

	// ---------------------------------------------------------------- people
	/**
	 * A player uses one of the peoples: hands over the items a delivery quest of that world asks for (the Karma Paths
	 * take them from any people of the worlds). Returns true when something was handed over (no trade then).
	 */
	public static boolean deliver(ServerPlayer p, MatrioNpc npc) {
		ItemStack held = p.getMainHandItem();
		if (held.isEmpty()) return false;
		String id = ModContent.idOf(held.getItem());
		int world = npc.def.world();
		for (Defs.QuestDef q : open(p, "deliver")) {
			if (!item(q.objTarget()).equals(id)) continue;
			if (q.world() == Quests.KARMA_CHAPTER ? world <= 0 : q.world() != world) continue;
			if (condition(q.objTarget()).equals("day") && p.level().getDefaultClockTime() % 24000 >= 12000) {
				p.sendSystemMessage(npc.getDisplayName().copy().withStyle(ChatFormatting.GOLD).append(": ")
					.append(Component.translatable("message.matriochka.quest.too_late").withStyle(ChatFormatting.ITALIC, ChatFormatting.GRAY)));
				return true;
			}
			int left = q.objCount() - Quests.progress(PlayerState.of(p), q);
			int give = Math.min(left, held.getCount());
			if (give <= 0) continue;
			held.shrink(give);
			p.level().playSound(null, npc.blockPosition(), SoundEvents.VILLAGER_YES, SoundSource.NEUTRAL, 0.8f, 1f);
			p.sendSystemMessage(Component.translatable("message.matriochka.quest.handed", give, Component.translatable("item.matriochka." + id), npc.getDisplayName()).withStyle(ChatFormatting.GRAY));
			PlayerState.of(p).progress("deliver", q.objTarget(), give);
			step(p, q);
			return true;
		}
		return false;
	}

	/** A player talks with one of the peoples: "meet" quests count different persons. */
	public static void meet(ServerPlayer p, MatrioNpc npc) {
		for (Defs.QuestDef q : open(p, "meet")) {
			if (!q.objTarget().equals(npc.def.id())) continue;
			PlayerState ps = PlayerState.of(p);
			String key = "met_" + npc.getUUID();
			if (ps.has(key)) continue;
			ps.set(key, true);
			ps.progress("meet", q.objTarget(), 1);
			step(p, q);
		}
	}

	// ---------------------------------------------------------------- items
	/** The sonar revealed these hostile creatures. */
	public static void spot(ServerPlayer p, int hostile) {
		if (hostile > 0 && !open(p, "spot").isEmpty()) PlayerState.of(p).progress("spot", "sonar", hostile);
	}

	/**
	 * Called every tick a glider is carried: a glide starts when the glider holds the player up and ends on landing;
	 * in World 4, one of at least 24 blocks counts as crossing an island.
	 */
	public static void glide(ServerPlayer p, boolean gliding) {
		Vec3 from = GLIDES.get(p.getUUID());
		if (gliding && from == null) {
			GLIDES.put(p.getUUID(), p.position());
			toolUsed(p, p.getMainHandItem().is(ModContent.item("glider")) ? p.getMainHandItem() : p.getOffhandItem());
			return;
		}
		if (from == null || !(p.onGround() || p.isInWater())) return;
		GLIDES.remove(p.getUUID());
		double dx = p.getX() - from.x, dz = p.getZ() - from.z;
		if (Worlds.number(p.level()) != 4 || dx * dx + dz * dz < GLIDE * GLIDE) return;
		for (Defs.QuestDef q : open(p, "glide")) {
			PlayerState.of(p).progress("glide", q.objTarget(), 1);
			step(p, q);
		}
	}

	/**
	 * A player uses an item: the "use_in" and "use_each" quests ("structure/item") count it inside such a structure, and
	 * the item is spent when consume is true (items with their own use spend themselves). Returns true when it counted.
	 */
	public static boolean useIn(ServerPlayer p, ItemStack stack, String itemId, boolean consume) {
		if (!(p.level() instanceof ServerLevel level)) return false;
		boolean counted = false;
		for (String kind : new String[]{"use_in", "use_each"}) {
			for (Defs.QuestDef q : open(p, kind)) {
				String[] parts = q.objTarget().split("/");
				if (parts.length != 2 || !parts[1].equals(itemId)) continue;
				StructureStart start = startAt(level, p.blockPosition(), parts[0]);
				if (start == null) continue;
				PlayerState ps = PlayerState.of(p);
				if (kind.equals("use_each")) {
					String key = "used_" + q.id() + "_" + start.getChunkPos().pack();
					if (ps.has(key)) {
						p.sendOverlayMessage(Component.translatable("message.matriochka.quest.already").withStyle(ChatFormatting.GRAY));
						continue;
					}
					ps.set(key, true);
				}
				if (consume && !counted) stack.consume(1, p);
				counted = true;
				ps.progress(kind, q.objTarget(), 1);
				level.sendParticles(kind.equals("use_each") ? ParticleTypes.ELECTRIC_SPARK : ParticleTypes.WAX_ON, p.getX(), p.getY() + 1.2, p.getZ(), 24, 0.6, 0.6, 0.6, 0.15);
				level.playSound(null, p.blockPosition(), kind.equals("use_each") ? SoundEvents.TRIDENT_THUNDER.value() : SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 0.6f, 1.4f);
				step(p, q);
			}
		}
		return counted;
	}

	/** Every Tool: the player used gear from a world (struck, mined or used with it). */
	public static void toolUsed(ServerPlayer p, ItemStack stack) {
		if (stack.isEmpty()) return;
		Defs.ItemDef d = ModContent.def(ModContent.idOf(stack.getItem()));
		if (d == null || d.world() < 1 || d.world() > 10 || !TOOL_KINDS.contains(d.kind())) return;
		if (open(p, "tools").isEmpty()) return;
		PlayerState ps = PlayerState.of(p);
		int bits = ps.tag().getIntOr("tool_worlds", 0) | (1 << d.world());
		if (bits == ps.tag().getIntOr("tool_worlds", 0)) return;
		ps.tag().putInt("tool_worlds", bits);
		setProgress(p, "tools", "worlds", Integer.bitCount(bits));
		for (Defs.QuestDef q : open(p, "tools")) step(p, q);
	}

	/** The Scroll's page the player is reading (from the client). */
	public static void read(ServerPlayer p, int page) {
		if (page < 0 || page >= 5) return;
		PlayerState ps = PlayerState.of(p);
		int bits = ps.tag().getIntOr("scroll_read", 0) | (1 << page);
		ps.tag().putInt("scroll_read", bits);
		setProgress(p, "read", "artisan_scroll", Integer.bitCount(bits));
	}

	/** The Archives: a shelf or a lectern searched inside the structure, each one once. */
	private static void search(ServerPlayer p, ServerLevel level, BlockPos pos) {
		BlockState s = level.getBlockState(pos);
		if (!(s.is(Blocks.BOOKSHELF) || s.is(Blocks.CHISELED_BOOKSHELF) || s.is(Blocks.LECTERN))) return;
		for (Defs.QuestDef q : open(p, "search")) {
			if (startAt(level, pos, q.objTarget()) == null) continue;
			PlayerState ps = PlayerState.of(p);
			String key = "searched_" + pos.asLong();
			if (ps.has(key)) continue;
			ps.set(key, true);
			ps.progress("search", q.objTarget(), 1);
			level.playSound(null, pos, SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1f, 0.8f);
			p.sendOverlayMessage(Component.translatable("message.matriochka.quest.book").withStyle(ChatFormatting.GOLD));
			step(p, q);
		}
	}

	// ---------------------------------------------------------------- places, every five seconds (StructureTracker)
	public static void placesTick(ServerPlayer p, ServerLevel level, int world) {
		PlayerState ps = PlayerState.of(p);
		BlockPos pos = p.blockPosition();
		for (Defs.QuestDef q : open(p, "summit")) {
			StructureStart s = startAt(level, pos, q.objTarget());
			if (s != null && p.getY() >= s.getBoundingBox().maxY() - 5) ps.progress("summit", q.objTarget(), 1);
		}
		for (Defs.QuestDef q : open(p, "bottom")) {
			StructureStart s = startAt(level, pos, q.objTarget());
			if (s != null && p.getY() <= s.getBoundingBox().minY() + 6) ps.progress("bottom", q.objTarget(), 1);
		}
		for (Defs.QuestDef q : open(p, "visit_each")) {
			StructureStart s = startAt(level, pos, q.objTarget());
			if (s == null) continue;
			String key = "seen_" + q.id() + "_" + s.getChunkPos().pack();
			if (ps.has(key)) continue;
			ps.set(key, true);
			ps.progress("visit_each", q.objTarget(), 1);
			p.sendSystemMessage(Component.translatable("message.matriochka.quest.found." + q.id()).withStyle(ChatFormatting.GOLD));
			step(p, q);
		}
		for (Defs.QuestDef q : open(p, "courier")) {
			var carried = ModContent.itemOrNull(q.objTarget());
			if (carried == null || q.world() != world || fr.achedon12.matriochka.block.Stations.count(p.getInventory(), carried) <= 0) continue;
			for (Defs.StructureDef st : Content.STRUCTURES) {
				if (st.world() != world) continue;
				String key = "courier_" + q.id() + "_" + st.id();
				if (ps.has(key) || startAt(level, pos, st.id()) == null) continue;
				ps.set(key, true);
				ps.progress("courier", q.objTarget(), 1);
				step(p, q);
			}
		}
		for (Defs.QuestDef q : open(p, "visit")) {
			int w = Integer.parseInt(q.objTarget().substring("world_".length()));
			int n = 0;
			for (Defs.StructureDef st : Content.STRUCTURES) if (st.world() == w && ps.has("visited_" + st.id())) n++;
			setProgress(p, "visit", q.objTarget(), n);
		}
		if (world == 8) {
			for (Defs.QuestDef q : open(p, "seasons")) {
				int bits = ps.tag().getIntOr("seasons_seen", 0) | (1 << fr.achedon12.matriochka.rules.HastenedClock.season(level));
				ps.tag().putInt("seasons_seen", bits);
				setProgress(p, "seasons", q.objTarget(), Integer.bitCount(bits));
			}
		}
		if (world == 10) {
			for (Defs.QuestDef q : open(p, "find")) {
				StructureStart s = startAt(level, pos, BaseModel.STRUCTURE);
				if (s == null || s.getPieces().isEmpty()) continue;
				BlockPos c = BaseModel.corner(BaseModel.origin(s.getPieces().getFirst().getBoundingBox())).offset(BaseModel.SX / 2, 0, BaseModel.SZ / 2);
				if (p.blockPosition().closerThan(c, 14)) ps.progress("find", q.objTarget(), 1);
			}
		}
	}

	/** The Labyrinth Map named a place: reaching it completes the map. */
	public static void mapTarget(ServerPlayer p, String structure) {
		PlayerState.of(p).tag().putString("map_target", structure);
	}

	public static void visited(ServerPlayer p, String structure) {
		PlayerState ps = PlayerState.of(p);
		if (!structure.equals(ps.tag().getStringOr("map_target", ""))) return;
		ps.tag().remove("map_target");
		for (Defs.QuestDef q : open(p, "mapped")) ps.progress("mapped", q.objTarget(), 1);
	}
}
