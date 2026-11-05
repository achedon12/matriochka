package fr.achedon12.matriochka.item;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.arrow.AbstractArrow;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.BlocksAttacks;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.item.component.Weapon;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The replay gear (tools/content.py REPLAY_GEAR) and the trophy dolls: their item properties and behaviour.
 * <ul>
 * <li>Spore Bow: its arrows burst into a cloud of toxic spores where they land.</li>
 * <li>Magma Flail: slow and heavy; sets foes ablaze and every third blow bursts in a ring of flame.</li>
 * <li>Key Chain Whip: long reach; every lash drags the foe toward you and slows it.</li>
 * <li>Storm Javelin and Tide Harpoon: thrown with use, see {@link ReplayProjectile}.</li>
 * <li>Lantern Shield: blocks like a shield; a blocked blow flares, blinding, marking and throwing back the attacker.</li>
 * <li>Quake Pick: mines a column of three; used on the ground, a tremor staggers the creatures around.</li>
 * </ul>
 */
public final class ReplayGear {
	public static EntityType<ReplayProjectile> THROWN;
	private static final Map<UUID, Integer> FLAIL_SWINGS = new HashMap<>();
	private static final List<AbstractArrow> SPORE_ARROWS = new ArrayList<>();
	private static boolean busy;

	private ReplayGear() {}

	private static ToolMaterial tool(int world) {
		return new ToolMaterial(world >= 5 ? BlockTags.INCORRECT_FOR_NETHERITE_TOOL : BlockTags.INCORRECT_FOR_IRON_TOOL,
			300 + world * 180, 7f + world * 0.6f, 0f, 12, TagKey.create(Registries.ITEM, Matriochka.id("repairs/world_" + world)));
	}

	/** Weapon attributes: damage, speed and, for the whip, a longer reach. */
	private static ItemAttributeModifiers weapon(float damage, float speed, float reach) {
		var b = ItemAttributeModifiers.builder()
			.add(Attributes.ATTACK_DAMAGE, new AttributeModifier(Item.BASE_ATTACK_DAMAGE_ID, damage - 1f, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND)
			.add(Attributes.ATTACK_SPEED, new AttributeModifier(Item.BASE_ATTACK_SPEED_ID, speed, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		if (reach > 0) b.add(Attributes.ENTITY_INTERACTION_RANGE, new AttributeModifier(Matriochka.id("whip_reach"), reach, AttributeModifier.Operation.ADD_VALUE), EquipmentSlotGroup.MAINHAND);
		return b.build();
	}

	/** The item of a replay gear or trophy id, or null for every other item (ModContent makes those). */
	public static Item make(Defs.ItemDef d, Item.Properties p) {
		if (d.kind().equals("trophy")) return new MatrioItem(d, p.stacksTo(1).fireResistant());
		float dmg = Defs.GEAR[Math.max(1, Math.min(10, d.world()))][0];
		return switch (d.id()) {
			case "spore_bow" -> new SporeBow(d, p.durability(480).enchantable(1).component(DataComponents.WEAPON, new Weapon(1)));
			case "magma_flail" -> new Gear(d, p.sword(tool(2), dmg - 1f, -2.4f).attributes(weapon(dmg + 2f, -3.0f, 0)));
			case "key_chain_whip" -> new Gear(d, p.sword(tool(3), dmg - 1f, -2.4f).attributes(weapon(dmg - 2f, -2.2f, 2.5f)));
			case "storm_javelin" -> new Gear(d, p.sword(tool(4), dmg - 1f, -2.4f).attributes(weapon(dmg - 1f, -2.6f, 0)));
			case "tide_harpoon" -> new Gear(d, p.sword(tool(7), dmg - 1f, -2.4f).attributes(weapon(dmg - 2f, -2.6f, 0)));
			case "quake_pick" -> new Gear(d, p.pickaxe(tool(9), 2f, -2.9f));
			case "lantern_shield" -> new Gear(d, p.durability(560).enchantable(1).delayedComponent(DataComponents.BLOCKS_ATTACKS, ctx -> new BlocksAttacks(0.2f, 1f,
				List.of(new BlocksAttacks.DamageReduction(90f, Optional.empty(), 0f, 1f)), new BlocksAttacks.ItemDamageFunction(3f, 1f, 1f),
				Optional.of(ctx.getOrThrow(DamageTypeTags.BYPASSES_SHIELD)), Optional.of(SoundEvents.SHIELD_BLOCK), Optional.of(SoundEvents.SHIELD_BREAK))));
			default -> null;
		};
	}

	// ---------------------------------------------------------------- items
	/** The replay weapons and tools: Matriochka items whose use throws, blocks or quakes. */
	public static class Gear extends MatrioItem {
		public Gear(Defs.ItemDef def, Properties properties) {
			super(def, properties);
		}

		@Override
		public InteractionResult use(Level level, Player player, InteractionHand hand) {
			ItemStack stack = player.getItemInHand(hand);
			switch (def.id()) {
				case "lantern_shield" -> {
					player.startUsingItem(hand);
					return InteractionResult.CONSUME;
				}
				case "storm_javelin", "tide_harpoon" -> {
					if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.FAIL;
					if (level instanceof ServerLevel sl) {
						ReplayProjectile thrown = new ReplayProjectile(sl, player, stack.copyWithCount(1));
						thrown.shootFromRotation(player, player.getXRot(), player.getYRot(), 0f, def.id().equals("tide_harpoon") && player.isInWater() ? 2.4f : 2.0f, 0.5f);
						sl.addFreshEntity(thrown);
						sl.playSound(null, player.blockPosition(), SoundEvents.TRIDENT_THROW.value(), SoundSource.PLAYERS, 1f, def.id().equals("tide_harpoon") ? 0.8f : 1.1f);
						if (!player.getAbilities().instabuild) player.setItemInHand(hand, ItemStack.EMPTY);
						player.getCooldowns().addCooldown(stack, 20);
					}
					return InteractionResult.SUCCESS;
				}
				default -> {
					return super.use(level, player, hand);
				}
			}
		}

		@Override
		public InteractionResult useOn(UseOnContext ctx) {
			if (!def.id().equals("quake_pick") || ctx.getClickedFace() != Direction.UP || ctx.getPlayer() == null) return super.useOn(ctx);
			Player player = ctx.getPlayer();
			ItemStack stack = ctx.getItemInHand();
			if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.FAIL;
			if (ctx.getLevel() instanceof ServerLevel sl) {
				tremor(sl, player, ctx.getClickedPos());
				player.getCooldowns().addCooldown(stack, 100);
				if (player instanceof ServerPlayer sp) stack.hurtAndBreak(2, sp, ctx.getHand());
			}
			return InteractionResult.SUCCESS;
		}
	}

	/** The Spore Bow: a bow whose arrows carry spores. */
	public static class SporeBow extends BowItem {
		public final Defs.ItemDef def;

		public SporeBow(Defs.ItemDef def, Properties properties) {
			super(properties);
			this.def = def;
		}

		@Override
		protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack weapon, ItemStack projectile, boolean isCrit) {
			Projectile p = super.createProjectile(level, shooter, weapon, projectile, isCrit);
			if (p instanceof AbstractArrow arrow && !level.isClientSide()) {
				arrow.addTag("matriochka_spore");
				SPORE_ARROWS.add(arrow);
			}
			return p;
		}

		@Override
		public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
			// the class line is added by the client for every item that is not a MatrioItem
			out.accept(Component.translatable("item.matriochka." + def.id() + ".desc").withStyle(net.minecraft.ChatFormatting.GRAY));
			out.accept(Component.translatable("rarity.matriochka." + def.rarity()).withStyle(net.minecraft.ChatFormatting.AQUA));
			out.accept(Component.translatable("tooltip.matriochka.world", def.world()).withStyle(net.minecraft.ChatFormatting.DARK_GRAY));
		}
	}

	// ---------------------------------------------------------------- behaviour
	public static void register() {
		ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, Matriochka.id("thrown_gear"));
		THROWN = Registry.register(BuiltInRegistries.ENTITY_TYPE, key, EntityType.Builder.<ReplayProjectile>of(ReplayProjectile::new, MobCategory.MISC)
			.sized(0.4f, 0.4f).clientTrackingRange(6).updateInterval(10).build(key));

		ServerLivingEntityEvents.AFTER_DAMAGE.register((entity, source, base, taken, blocked) -> {
			if (busy || !(entity.level() instanceof ServerLevel level)) return;
			// the Lantern Shield flares when it stops a blow
			if (blocked && entity instanceof ServerPlayer p && p.getUseItem().is(ModContent.item("lantern_shield")) && source.getEntity() instanceof LivingEntity attacker) {
				attacker.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0));
				attacker.addEffect(new MobEffectInstance(MobEffects.GLOWING, 120, 0));
				attacker.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40, 1));
				if (!(attacker instanceof MatrioBoss)) {
					attacker.setDeltaMovement(attacker.position().subtract(p.position()).normalize().scale(1.1).add(0, 0.35, 0));
					attacker.needsSync = true;
				}
				level.sendParticles(ParticleTypes.END_ROD, p.getX(), p.getY() + 1.2, p.getZ(), 24, 0.6, 0.6, 0.6, 0.15);
				level.playSound(null, p.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 0.8f, 1.8f);
			}
			// spore arrows burst on what they hit
			if (source.getDirectEntity() instanceof AbstractArrow arrow && arrow.entityTags().contains("matriochka_spore")) {
				spores(level, entity.position(), arrow.getOwner());
				arrow.removeTag("matriochka_spore");
			}
			if (!(source.getEntity() instanceof ServerPlayer p) || source.getDirectEntity() != p || entity == p) return;
			ItemStack held = p.getMainHandItem();
			if (held.is(ModContent.item("magma_flail"))) {
				entity.igniteForSeconds(4);
				int swings = FLAIL_SWINGS.merge(p.getUUID(), 1, Integer::sum);
				if (swings % 3 == 0) flameRing(level, p, entity, taken);
				if (Worlds.number(level) == 2) PlayerState.of(p).addGauge("heat", 2f);
			} else if (held.is(ModContent.item("key_chain_whip"))) {
				entity.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 50, 1));
				if (!(entity instanceof MatrioBoss) && entity.distanceTo(p) > 2.2) {
					entity.setDeltaMovement(p.position().subtract(entity.position()).normalize().scale(0.7).add(0, 0.25, 0));
					entity.needsSync = true;
				}
				level.playSound(null, entity.blockPosition(), SoundEvents.CHAIN_HIT, SoundSource.PLAYERS, 1f, 1.3f);
			}
		});

		// the Quake Pick takes the blocks above and below the one it mines
		PlayerBlockBreakEvents.AFTER.register((level, player, pos, state, be) -> {
			if (busy || !(player instanceof ServerPlayer sp) || !(level instanceof ServerLevel sl)) return;
			ItemStack pick = sp.getMainHandItem();
			if (!pick.is(ModContent.item("quake_pick")) || sp.isSecondaryUseActive()) return;
			busy = true;
			try {
				for (BlockPos q : new BlockPos[]{pos.above(), pos.below()}) {
					BlockState s = sl.getBlockState(q);
					float hardness = s.getDestroySpeed(sl, q);
					if (s.isAir() || hardness < 0 || hardness > 50 || !pick.isCorrectToolForDrops(s)) continue;
					if (sl.getBlockEntity(q) != null) continue;
					sp.gameMode.destroyBlock(q);
				}
			} finally {
				busy = false;
			}
		});

		// spore arrows that land in the ground burst there
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (SPORE_ARROWS.isEmpty()) return;
			SPORE_ARROWS.removeIf(a -> {
				if (a.isRemoved() || !a.entityTags().contains("matriochka_spore")) return true;
				if (a.tickCount > 2 && a.getDeltaMovement().lengthSqr() < 1e-4 && a.level() instanceof ServerLevel l) {
					spores(l, a.position(), a.getOwner());
					a.removeTag("matriochka_spore");
					return true;
				}
				return a.tickCount > 600;
			});
		});
	}

	private static void spores(ServerLevel level, net.minecraft.world.phys.Vec3 at, Entity owner) {
		AreaEffectCloud c = new AreaEffectCloud(level, at.x, at.y, at.z);
		c.setRadius(2.8f);
		c.setRadiusPerTick(-0.01f);
		c.setDuration(100);
		c.setWaitTime(4);
		c.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 1));
		if (owner instanceof LivingEntity le) c.setOwner(le);
		level.addFreshEntity(c);
		level.sendParticles(ParticleTypes.SPORE_BLOSSOM_AIR, at.x, at.y + 0.5, at.z, 30, 1.2, 0.5, 1.2, 0.02);
		level.playSound(null, BlockPos.containing(at), SoundEvents.PUFFER_FISH_BLOW_UP, SoundSource.PLAYERS, 0.8f, 0.7f);
	}

	private static void flameRing(ServerLevel level, ServerPlayer p, LivingEntity hit, float taken) {
		for (int i = 0; i < 24; i++) {
			double a = i * Math.PI / 12;
			level.sendParticles(ParticleTypes.FLAME, hit.getX() + Math.cos(a) * 3, hit.getY() + 0.3, hit.getZ() + Math.sin(a) * 3, 2, 0.05, 0.1, 0.05, 0.01);
		}
		level.playSound(null, hit.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 1f, 0.6f);
		busy = true;
		try {
			for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, hit.getBoundingBox().inflate(3), e -> e != p && !(e instanceof Player))) {
				e.igniteForSeconds(3);
				if (e != hit) e.hurtServer(level, level.damageSources().playerAttack(p), Math.max(2f, taken * 0.4f));
			}
		} finally {
			busy = false;
		}
	}

	/** The Quake Pick's tremor: creatures around stagger, slowed, lifted and hurt. */
	public static void tremor(ServerLevel level, Player player, BlockPos at) {
		level.sendParticles(ParticleTypes.EXPLOSION, at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 6, 2, 0.1, 2, 0);
		level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 30, 3, 0.1, 3, 0.01);
		level.playSound(null, at, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 0.8f, 0.5f);
		for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(6), e -> e != player && !(e instanceof Player) && e.onGround())) {
			e.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 2));
			e.hurtServer(level, player instanceof ServerPlayer sp ? level.damageSources().playerAttack(sp) : level.damageSources().generic(), 4f);
			if (!(e instanceof MatrioBoss)) {
				e.push(0, 0.45, 0);
				e.needsSync = true;
			}
		}
	}
}
