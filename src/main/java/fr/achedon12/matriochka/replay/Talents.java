package fr.achedon12.matriochka.replay;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.Stations;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * Talent trees, learnt at the Class Table: three branches of four talents per class (tools/content.py TALENTS), each
 * talent bought in order with souls and, for the last two, Shell Shards. A class's talents act while the player wears
 * or holds at least one item of that class (any tool for the Prospector). Learnt talents are player flags
 * ("talent_<id>"); attribute talents become transient modifiers on the player, the others are hooks on damage, kills
 * and mining, and the Reaper and Survivor ones add to {@link GearClasses#soulGain} and {@link GearClasses#survivorResistance}.
 */
public final class Talents {
	public static final Map<String, ReplayContent.TalentDef> BY_ID = new LinkedHashMap<>();
	/** Sum of every active talent's value by effect, per player, refreshed every second. */
	private static final Map<UUID, Map<String, Float>> SUMS = new HashMap<>();
	private static final Map<UUID, Long> LAST_HURT = new HashMap<>();
	private static boolean striking;

	static {
		for (ReplayContent.TalentDef d : ReplayContent.TALENTS) BY_ID.put(d.id(), d);
	}

	private record Attr(Holder<Attribute> attr, AttributeModifier.Operation op, float sign) {}

	private static final Map<String, Attr> ATTRS = new LinkedHashMap<>();

	static {
		var add = AttributeModifier.Operation.ADD_VALUE;
		var pct = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;
		ATTRS.put("armor", new Attr(Attributes.ARMOR, add, 1));
		ATTRS.put("toughness", new Attr(Attributes.ARMOR_TOUGHNESS, add, 1));
		ATTRS.put("knockback", new Attr(Attributes.KNOCKBACK_RESISTANCE, add, 1));
		ATTRS.put("max_health", new Attr(Attributes.MAX_HEALTH, add, 1));
		ATTRS.put("damage", new Attr(Attributes.ATTACK_DAMAGE, pct, 1));
		ATTRS.put("attack_speed", new Attr(Attributes.ATTACK_SPEED, pct, 1));
		ATTRS.put("speed", new Attr(Attributes.MOVEMENT_SPEED, pct, 1));
		ATTRS.put("luck", new Attr(Attributes.LUCK, add, 1));
		ATTRS.put("mining", new Attr(Attributes.MINING_EFFICIENCY, add, 1));
		ATTRS.put("break_speed", new Attr(Attributes.BLOCK_BREAK_SPEED, pct, 1));
		ATTRS.put("reach", new Attr(Attributes.BLOCK_INTERACTION_RANGE, add, 1));
		ATTRS.put("step", new Attr(Attributes.STEP_HEIGHT, add, 1));
		ATTRS.put("safe_fall", new Attr(Attributes.SAFE_FALL_DISTANCE, add, 1));
		ATTRS.put("jump", new Attr(Attributes.JUMP_STRENGTH, pct, 1));
		ATTRS.put("oxygen", new Attr(Attributes.OXYGEN_BONUS, add, 1));
		ATTRS.put("burn", new Attr(Attributes.BURNING_TIME, pct, -1));
		ATTRS.put("submerged", new Attr(Attributes.SUBMERGED_MINING_SPEED, pct, 1));
		// absorption needs room to live in
		ATTRS.put("absorb", new Attr(Attributes.MAX_ABSORPTION, add, 1));
	}

	private Talents() {}

	public static ReplayContent.TalentDef def(String id) {
		return BY_ID.get(id);
	}

	public static boolean learnt(PlayerState ps, String id) {
		return ps.has("talent_" + id);
	}

	/** The classes whose talents act right now: those of the worn and held gear; any tool wakes the Prospector's. */
	public static Set<String> activeClasses(LivingEntity e) {
		Set<String> out = new HashSet<>();
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			ItemStack s = e.getItemBySlot(slot);
			GearClasses.Gear g = s.get(GearClasses.GEAR);
			if (g != null) out.add(g.cls());
			if ((slot == EquipmentSlot.MAINHAND || slot == EquipmentSlot.OFFHAND) && GearClasses.kind(s) == GearClasses.Kind.TOOL) out.add("prospector");
		}
		return out;
	}

	/** The summed value of an effect over the player's active talents (0 for anyone else). */
	public static float sum(LivingEntity e, String effect) {
		if (!(e instanceof ServerPlayer)) return 0f;
		Map<String, Float> m = SUMS.get(e.getUUID());
		return m == null ? 0f : m.getOrDefault(effect, 0f);
	}

	private static Map<String, Float> compute(ServerPlayer p) {
		PlayerState ps = PlayerState.of(p);
		Set<String> active = activeClasses(p);
		Map<String, Float> m = new HashMap<>();
		for (ReplayContent.TalentDef d : ReplayContent.TALENTS) {
			if (active.contains(d.cls()) && learnt(ps, d.id())) m.merge(d.effect(), d.value(), Float::sum);
		}
		return m;
	}

	// ---------------------------------------------------------------- learning
	/** Learns a talent; returns an error key or null. The player must stand at a Class Table. */
	public static String learn(ServerPlayer p, String id) {
		ReplayContent.TalentDef d = def(id);
		if (d == null) return "message.matriochka.talent.unknown";
		PlayerState ps = PlayerState.of(p);
		if (learnt(ps, id)) return "message.matriochka.talent.known";
		if (!nearTable(p)) return "message.matriochka.talent.table";
		boolean free = p.isCreative();
		if (d.tier() > 0) {
			ReplayContent.TalentDef prev = previous(d);
			if (prev != null && !learnt(ps, prev.id())) return "message.matriochka.talent.previous";
		}
		MatrioData data = MatrioData.get(p.level().getServer());
		if (!free && data.highestDefeated(data.groupOf(p.getUUID())) < d.gate()) return "message.matriochka.talent.progress";
		Item shard = ModContent.item("shell_shard");
		if (!free && Stations.count(p.getInventory(), shard) < d.shards()) return "message.matriochka.class.need_shard";
		if (!free && ps.souls() < d.souls()) return "message.matriochka.altar.no_souls";
		if (!free) {
			ps.spendSouls(d.souls());
			take(p.getInventory(), shard, d.shards());
			ps.addCounter("talent_spent", d.souls());
		}
		ps.set("talent_" + id, true);
		refresh(p);
		ps.sync();
		if (p.level() instanceof ServerLevel l) {
			l.playSound(null, p.blockPosition(), fr.achedon12.matriochka.content.Sounds.STATION_CLASS_TABLE, SoundSource.PLAYERS, 1f, 1.2f);
			l.sendParticles(ParticleTypes.ENCHANT, p.getX(), p.getY() + 1.2, p.getZ(), 30, 0.5, 0.6, 0.5, 0.4);
		}
		p.sendOverlayMessage(Component.translatable("message.matriochka.talent.learnt", Component.translatable("talent.matriochka." + id)).withStyle(ChatFormatting.GOLD));
		return null;
	}

	/** Unlearns every talent, giving back part of the souls spent (never the shards). */
	public static String reset(ServerPlayer p) {
		if (!nearTable(p)) return "message.matriochka.talent.table";
		PlayerState ps = PlayerState.of(p);
		int n = 0;
		for (String id : BY_ID.keySet()) {
			if (learnt(ps, id)) {
				ps.set("talent_" + id, false);
				n++;
			}
		}
		if (n == 0) return "message.matriochka.talent.none";
		int back = Math.round(ps.counter("talent_spent") * ReplayContent.TALENT_REFUND);
		ps.addCounter("talent_spent", -ps.counter("talent_spent"));
		// a refund of souls already spent: not a gain, so not scaled by the server's soulGainMultiplier
		ps.setSouls(ps.souls() + back);
		refresh(p);
		ps.sync();
		p.sendSystemMessage(Component.translatable("message.matriochka.talent.reset", back).withStyle(ChatFormatting.GOLD));
		return null;
	}

	/** The talent before this one in its branch. */
	public static ReplayContent.TalentDef previous(ReplayContent.TalentDef d) {
		for (ReplayContent.TalentDef o : ReplayContent.TALENTS) {
			if (o.cls().equals(d.cls()) && o.branch().equals(d.branch()) && o.tier() == d.tier() - 1) return o;
		}
		return null;
	}

	private static boolean nearTable(ServerPlayer p) {
		Block table = ModContent.block("class_table");
		for (BlockPos q : BlockPos.betweenClosed(p.blockPosition().offset(-6, -3, -6), p.blockPosition().offset(6, 3, 6))) {
			if (p.level().getBlockState(q).is(table)) return true;
		}
		return false;
	}

	private static void take(Inventory inv, Item item, int n) {
		for (int i = 0; i < inv.getContainerSize() && n > 0; i++) {
			ItemStack s = inv.getItem(i);
			if (!s.is(item)) continue;
			int k = Math.min(n, s.getCount());
			s.shrink(k);
			n -= k;
		}
	}

	// ---------------------------------------------------------------- applying
	/** Recomputes the active talents of a player and their attribute modifiers. */
	public static void refresh(ServerPlayer p) {
		Map<String, Float> m = compute(p);
		SUMS.put(p.getUUID(), m);
		for (Map.Entry<String, Attr> e : ATTRS.entrySet()) {
			AttributeInstance inst = p.getAttribute(e.getValue().attr());
			if (inst == null) continue;
			Identifier id = Matriochka.id("talent_" + e.getKey());
			double want = m.getOrDefault(e.getKey(), 0f) * e.getValue().sign();
			AttributeModifier had = inst.getModifier(id);
			if (had != null && Math.abs(had.amount() - want) < 1e-6) continue;
			if (had != null) inst.removeModifier(id);
			if (want != 0) inst.addTransientModifier(new AttributeModifier(id, want, e.getValue().op()));
		}
		if (p.getHealth() > p.getMaxHealth()) p.setHealth(p.getMaxHealth());
	}

	static void tick(MinecraftServer server) {
		long t = server.getTickCount();
		if (t % 20 != 0) return;
		for (ServerPlayer p : server.getPlayerList().getPlayers()) {
			if (p.isSpectator() || !p.isAlive()) continue;
			refresh(p);
			Map<String, Float> m = SUMS.get(p.getUUID());
			if (m.isEmpty()) continue;
			float regen = m.getOrDefault("regen", 0f);
			if (regen > 0 && t % 40 == 0 && t - LAST_HURT.getOrDefault(p.getUUID(), 0L) > 100) p.heal(regen);
			float absorb = m.getOrDefault("absorb", 0f);
			if (absorb > 0 && t % 600 == 0 && p.getAbsorptionAmount() < absorb) p.setAbsorptionAmount(absorb);
			float haste = m.getOrDefault("haste", 0f);
			if (haste > 0 && GearClasses.kind(p.getMainHandItem()) == GearClasses.Kind.TOOL) {
				p.addEffect(new MobEffectInstance(MobEffects.HASTE, 50, Math.max(0, Math.round(haste) - 1), true, false, true));
			}
		}
	}

	static void forget(UUID id) {
		SUMS.remove(id);
		LAST_HURT.remove(id);
	}

	// ---------------------------------------------------------------- hooks
	static void init() {
		ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) -> {
			if (!(entity instanceof ServerPlayer p) || source.getEntity() == null || source.getEntity() == p) return true;
			if (source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return true;
			float dodge = Math.min(0.3f, sum(p, "dodge"));
			if (dodge <= 0 || p.getRandom().nextFloat() >= dodge) return true;
			if (p.level() instanceof ServerLevel l) {
				l.sendParticles(ParticleTypes.CLOUD, p.getX(), p.getY() + 0.8, p.getZ(), 8, 0.3, 0.4, 0.3, 0.02);
				l.playSound(null, p.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 0.6f, 1.8f);
			}
			p.sendOverlayMessage(Component.translatable("message.matriochka.dodge").withStyle(ChatFormatting.AQUA));
			return false;
		});
		ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, base, taken, blocked) -> {
			if (striking || taken <= 0 || !(entity.level() instanceof ServerLevel level)) return;
			if (entity instanceof ServerPlayer hurt) {
				LAST_HURT.put(hurt.getUUID(), (long) level.getServer().getTickCount());
				float last = sum(hurt, "laststand");
				if (last > 0 && hurt.isAlive() && hurt.getHealth() < hurt.getMaxHealth() * 0.3f) hurt.heal(taken * Math.min(0.6f, last));
				float thorns = sum(hurt, "thorns");
				if (thorns > 0 && source.getEntity() instanceof LivingEntity attacker && attacker != hurt) strike(level, hurt, attacker, taken * thorns);
			}
			if (source.getEntity() instanceof ServerPlayer p && entity != p) {
				LAST_HURT.put(p.getUUID(), (long) level.getServer().getTickCount());
				float extra = 0;
				if (p.getHealth() < p.getMaxHealth() * 0.5f) extra += sum(p, "rage");
				if (entity instanceof MatrioBoss) extra += sum(p, "boss");
				if (!entity.entityTags().contains("matrio_struck")) {
					extra += sum(p, "crit");
					entity.addTag("matrio_struck");
				}
				if (entity.getHealth() < entity.getMaxHealth() * 0.25f) extra += sum(p, "execute");
				if (p.isShiftKeyDown()) extra += sum(p, "sneak");
				if (extra > 0 && entity.isAlive()) strike(level, p, entity, taken * extra);
				float steal = sum(p, "lifesteal");
				if (steal > 0) p.heal(taken * steal);
				float wither = sum(p, "wither");
				if (wither > 0 && entity.isAlive()) entity.addEffect(new MobEffectInstance(MobEffects.WITHER, Math.round(wither * 20), 0));
			}
		});
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (!(entity.level() instanceof ServerLevel level)) return;
			if (source.getEntity() instanceof ServerPlayer p) {
				float speed = sum(p, "killspeed");
				if (speed > 0) p.addEffect(new MobEffectInstance(MobEffects.SPEED, Math.round(speed * 20), 0));
				float heal = sum(p, "killheal");
				if (heal > 0) p.heal(heal);
				float ghost = sum(p, "ghost");
				if (ghost > 0) p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, Math.round(ghost * 20), 0));
			}
			// a Shell Gatherer picks up one more shard from a story boss
			if (entity instanceof MatrioBoss boss && !boss.entityTags().contains(Trials.TAG)) {
				for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, boss.getBoundingBox().inflate(64))) {
					float c = sum(p, "shards");
					if (c > 0 && p.getRandom().nextFloat() < c) {
						ItemStack shard = new ItemStack(ModContent.item("shell_shard"));
						if (!p.getInventory().add(shard)) p.spawnAtLocation(level, shard);
					}
				}
			}
		});
		PlayerBlockBreakEvents.AFTER.register((level, player, pos, state, be) -> {
			if (!(player instanceof ServerPlayer p) || !(level instanceof ServerLevel sl) || p.isCreative()) return;
			float c = sum(p, "orebonus");
			if (c <= 0 || !ore(state) || p.getRandom().nextFloat() >= c) return;
			Block.dropResources(state, sl, pos, be, p, p.getMainHandItem());
			sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0);
		});
	}

	/** An ore: a vanilla one or a Matriochka ore block. */
	private static boolean ore(BlockState state) {
		if (state.is(net.fabricmc.fabric.api.tag.convention.v2.ConventionalBlockTags.ORES)) return true;
		String id = ModContent.idOf(state.getBlock().asItem());
		var def = fr.achedon12.matriochka.content.Content.BLOCKS.stream().filter(b -> b.id().equals(id)).findFirst();
		return def.isPresent() && def.get().style().startsWith("ore");
	}

	/** Extra damage from a talent, without setting off the talents again. */
	private static void strike(ServerLevel level, ServerPlayer from, LivingEntity to, float amount) {
		if (amount <= 0.01f) return;
		striking = true;
		try {
			fr.achedon12.matriochka.mc.Mc.clearInvulnerable(to);
			to.hurtServer(level, level.damageSources().playerAttack(from), amount);
		} finally {
			striking = false;
		}
	}
}
