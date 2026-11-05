package fr.achedon12.matriochka.item;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Travel;
import java.util.function.Consumer;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/** Generic Matriochka item: rarity/soul tooltip, plus the special behaviour of tools and consumables, keyed by id. */
public class MatrioItem extends Item {
	public final Defs.ItemDef def;

	public MatrioItem(Defs.ItemDef def, Properties properties) {
		super(properties);
		this.def = def;
	}

	@Override
	public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
		appendInfo(def, stack, out);
	}

	public static void appendInfo(Defs.ItemDef def, ItemStack stack, Consumer<Component> out) {
		String key = "item.matriochka." + def.id() + ".desc";
		if (net.minecraft.locale.Language.getInstance().has(key)) {
			out.accept(Component.translatable(key).withStyle(ChatFormatting.GRAY));
		}
		int soul = Defs.soulValue(def.rarity());
		ChatFormatting color = switch (def.rarity()) {
			case "rare" -> ChatFormatting.AQUA;
			case "epic" -> ChatFormatting.LIGHT_PURPLE;
			case "legendary" -> ChatFormatting.GOLD;
			default -> ChatFormatting.WHITE;
		};
		Component rarity = Component.translatable("rarity.matriochka." + def.rarity()).withStyle(color);
		if (soul > 0 && !"core".equals(def.kind())) {
			out.accept(Component.translatable("tooltip.matriochka.soul", rarity, soul).withStyle(ChatFormatting.DARK_GRAY));
		} else {
			out.accept(rarity);
		}
		if (def.world() > 0) out.accept(Component.translatable("tooltip.matriochka.world", def.world()).withStyle(ChatFormatting.DARK_GRAY));
		if (def.id().equals("drill")) Drill.appendTooltip(stack, out);
		GearClasses.appendTooltip(stack, out);
	}

	/** The world dishes: each one eases its world's rule for a while. */
	@Override
	public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
		if (entity instanceof ServerPlayer sp && "food".equals(def.kind())) eat(sp, def.id(), level.getGameTime());
		return super.finishUsingItem(stack, level, entity);
	}

	private static void eat(ServerPlayer sp, String id, long now) {
		PlayerState ps = PlayerState.of(sp);
		int min = 20 * 60;
		switch (id) {
			case "root_broth" -> ps.setFlagTime("root_broth", now + 5 * min);
			case "ice_bread" -> ps.setFlagTime("ice_bread", now + 5 * min);
			case "cell_ration" -> sp.addEffect(new MobEffectInstance(MobEffects.SATURATION, 40, 0));
			case "cloud_fruit" -> sp.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 3 * min, 0));
			case "mute_mushroom" -> ps.setFlagTime("mute", now + 5 * min);
			case "flipped_apple" -> ps.setFlagTime("flipped_apple", now + 20 * 30);
			case "apnea_kelp" -> { ps.setFlagTime("apnea", now + 5 * min); ps.addGauge("oxygen", 30); }
			case "season_jam" -> ps.setFlagTime("preserve", now + 3 * min);
			case "anchor_bread" -> ps.setFlagTime("anchor", now + 5 * min);
			case "workshop_feast" -> {
				for (String f : new String[]{"root_broth", "ice_bread", "mute", "apnea", "preserve", "anchor"}) ps.setFlagTime(f, now + 2 * min);
				sp.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 2 * min, 0));
			}
			default -> {}
		}
		ps.sync();
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (!(player instanceof ServerPlayer sp)) return special(def.id()) ? InteractionResult.SUCCESS : InteractionResult.PASS;
		ServerLevel sl = (ServerLevel) level;
		PlayerState ps = PlayerState.of(sp);
		boolean consume = false;
		switch (def.id()) {
			case "antidote" -> { ps.addGauge("toxin", -50); consume = true; }
			case "cooling_water" -> { ps.addGauge("heat", -50); consume = true; }
			case "silence_balm" -> { ps.addGauge("noise", -100); consume = true; }
			case "oxygen_capsule" -> { ps.addGauge("oxygen", 60); consume = true; }
			case "stabilizer" -> { ps.setFlagTime("stable", sl.getGameTime() + 20 * 30); consume = true; }
			case "season_preserve" -> { ps.setFlagTime("preserve", sl.getGameTime() + 20 * 120); consume = true; }
			case "silence", "anchor" -> { ps.setFlagTime("anchor", sl.getGameTime() + 20 * 600); consume = true; }
			case "return_thread" -> { if (Travel.returnToWorldBlock(sp)) consume = true; }
			case "refuge_doll" -> {
				if (fr.achedon12.matriochka.world.Refuge.use(sp)) sp.getCooldowns().addCooldown(stack, 40);
			}
			case "solar_lantern" -> {
				sp.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 20 * 60 * 20, 0, false, false, true));
				ps.setFlagTime("lantern", sl.getGameTime() + 20 * 60 * 20);
				sp.getCooldowns().addCooldown(stack, 20 * 60);
			}
			case "sonar" -> {
				for (LivingEntity e : sl.getEntitiesOfClass(LivingEntity.class, sp.getBoundingBox().inflate(32), e -> e != sp)) {
					e.addEffect(new MobEffectInstance(MobEffects.GLOWING, 20 * 8, 0, false, false));
				}
				sl.playSound(null, sp.blockPosition(), SoundEvents.WARDEN_SONIC_CHARGE, SoundSource.PLAYERS, 0.6f, 1.6f);
				sp.getCooldowns().addCooldown(stack, 20 * 10);
				ps.progress("use", "sonar", 1);
			}
			case "hourglass" -> {
				ps.setFlagTime("hourglass", sl.getGameTime() + 20 * 90);
				sp.getCooldowns().addCooldown(stack, 20 * 300);
				ps.progress("use", "hourglass", 1);
				fr.achedon12.matriochka.world.Achievements.grant(sp, "hourglass");
			}
			case "grappling_hook" -> {
				Vec3 eye = sp.getEyePosition();
				Vec3 end = eye.add(sp.getLookAngle().scale(32));
				BlockHitResult hit = sl.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, sp));
				// a creature in the line of the hook is pulled to you instead
				Vec3 reach = hit.getType() == HitResult.Type.BLOCK ? hit.getLocation() : end;
				var mob = net.minecraft.world.entity.projectile.ProjectileUtil.getEntityHitResult(sp, eye, reach,
					sp.getBoundingBox().expandTowards(reach.subtract(eye)).inflate(1), e -> e instanceof net.minecraft.world.entity.LivingEntity && e.isPickable() && !e.isSpectator(),
					eye.distanceToSqr(reach));
				if (mob != null && mob.getEntity() instanceof net.minecraft.world.entity.LivingEntity le && !(le instanceof fr.achedon12.matriochka.entity.MatrioBoss)) {
					Vec3 pull = sp.position().subtract(le.position()).normalize().scale(1.6).add(0, 0.35, 0);
					le.setDeltaMovement(pull);
					le.needsSync = true;
					Hooked.mark(le, sp, sl.getGameTime());
					sl.playSound(null, sp.blockPosition(), SoundEvents.FISHING_BOBBER_RETRIEVE, SoundSource.PLAYERS, 1f, 1.1f);
					sp.getCooldowns().addCooldown(stack, 30);
				} else if (hit.getType() == HitResult.Type.BLOCK) {
					Vec3 pull = hit.getLocation().subtract(sp.position()).normalize().scale(1.8).add(0, 0.4, 0);
					sp.setDeltaMovement(pull);
					sp.needsSync = true;
					sp.fallDistance = 0;
					sl.playSound(null, sp.blockPosition(), SoundEvents.FISHING_BOBBER_RETRIEVE, SoundSource.PLAYERS, 1f, 0.8f);
					sp.getCooldowns().addCooldown(stack, 20);
				}
			}
			case "thruster" -> {
				if (sp.isInWater()) {
					sp.setDeltaMovement(sp.getLookAngle().scale(1.4));
					sp.needsSync = true;
					sp.getCooldowns().addCooldown(stack, 15);
				}
			}
			case "labyrinth_map" -> {
				fr.achedon12.matriochka.structure.StructureTracker.describeNearby(sp);
				sp.getCooldowns().addCooldown(stack, 40);
			}
			case "artisan_scroll", "artisan_journal" -> {
				fr.achedon12.matriochka.net.Net.openJournal(sp, def.id().equals("artisan_scroll"));
				return InteractionResult.SUCCESS;
			}
			default -> {
				return InteractionResult.PASS;
			}
		}
		if (consume) {
			stack.consume(1, sp);
			sl.playSound(null, sp.blockPosition(), SoundEvents.BOTTLE_EMPTY, SoundSource.PLAYERS, 0.8f, 1.2f);
			ps.sync();
		}
		return InteractionResult.SUCCESS;
	}

	private static boolean special(String id) {
		return switch (id) {
			case "antidote", "cooling_water", "silence_balm", "oxygen_capsule", "stabilizer", "season_preserve", "anchor", "return_thread", "refuge_doll",
				 "solar_lantern", "sonar", "hourglass", "grappling_hook", "thruster", "labyrinth_map", "artisan_scroll", "artisan_journal" -> true;
			default -> false;
		};
	}

	@Override
	public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
		if (def.id().equals("portable_trap") && player instanceof ServerPlayer sp && target instanceof Mob) {
			target.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 20 * 8, 10));
			target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 20 * 8, 2));
			stack.consume(1, sp);
			fr.achedon12.matriochka.world.Achievements.grant(sp, "trapped");
			return InteractionResult.SUCCESS;
		}
		return InteractionResult.PASS;
	}

	@Override
	public void inventoryTick(ItemStack stack, ServerLevel level, Entity owner, EquipmentSlot slot) {
		if (!(owner instanceof ServerPlayer sp)) return;
		if (def.id().equals("glider") && (sp.getMainHandItem() == stack || sp.getOffhandItem() == stack)
			&& !sp.onGround() && sp.getDeltaMovement().y < -0.15 && !sp.isInWater()) {
			Vec3 v = sp.getDeltaMovement();
			Vec3 look = sp.getLookAngle();
			sp.setDeltaMovement(look.x * 0.6, Math.max(v.y, -0.12), look.z * 0.6);
			sp.needsSync = true;
			sp.fallDistance = 0;
		}
	}

	@Override
	public boolean isFoil(ItemStack stack) {
		return "core".equals(def.kind()) || super.isFoil(stack);
	}

	public static BlockPos below(BlockPos p) {
		return p.below();
	}
}
