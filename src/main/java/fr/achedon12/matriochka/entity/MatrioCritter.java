package fr.achedon12.matriochka.entity;

import com.geckolib.animatable.GeoEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.constant.DefaultAnimations;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.Defs;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomSwimmingGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.animal.fish.WaterAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;

/**
 * Harmless wildlife of the Pressure Ocean: Lantern Shoals dart about and flee swimmers, Glow Jellies drift slowly and
 * light the deep. They never attack. Models come from tools/mobs_hd like the creatures'.
 */
public class MatrioCritter extends WaterAnimal implements GeoEntity {
	public static final java.util.Map<EntityType<?>, Defs.CritterDef> DEFS = new java.util.HashMap<>();
	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	public MatrioCritter(EntityType<? extends WaterAnimal> type, Level level) {
		super(type, level);
		boolean drift = drift();
		this.moveControl = fr.achedon12.matriochka.mc.Mc.smoothSwim(this, drift ? 20 : 85, drift ? 4 : 10, drift ? 0.02f : 0.06f, 0.1f, false);
		this.lookControl = new SmoothSwimmingLookControl(this, 10);
	}

	public static AttributeSupplier.Builder attributes(Defs.CritterDef def) {
		return WaterAnimal.createMobAttributes()
			.add(Attributes.MAX_HEALTH, def.hp())
			.add(Attributes.MOVEMENT_SPEED, def.behavior().equals("drift") ? 0.4 : 0.5);
	}

	public Defs.CritterDef def() {
		return DEFS.get(getType());
	}

	private boolean drift() {
		Defs.CritterDef d = DEFS.get(getType());
		return d != null && d.behavior().equals("drift");
	}

	@Override
	protected PathNavigation createNavigation(Level level) {
		return new WaterBoundPathNavigation(this, level);
	}

	@Override
	protected void registerGoals() {
		if (!drift()) {
			goalSelector.addGoal(0, new PanicGoal(this, 1.25));
			goalSelector.addGoal(2, new AvoidEntityGoal<>(this, Player.class, 6f, 1.4, 1.6));
		}
		goalSelector.addGoal(4, new RandomSwimmingGoal(this, 1.0, drift() ? 60 : 10));
	}

	/** Spawns in open water at any depth of the World 7 sea. */
	public static boolean checkSpawn(EntityType<MatrioCritter> type, ServerLevelAccessor level, EntitySpawnReason reason, BlockPos pos, RandomSource random) {
		return level.getFluidState(pos).is(FluidTags.WATER) && level.getFluidState(pos.above()).is(FluidTags.WATER);
	}

	@Override
	protected void travelInWater(Vec3 input, double gravity, boolean falling, double y) {
		moveRelative(getSpeed(), input);
		move(MoverType.SELF, getDeltaMovement());
		setDeltaMovement(getDeltaMovement().scale(0.9));
		// a jelly that is not going anywhere pulses gently up and sinks back
		if (drift() && getNavigation().isDone()) setDeltaMovement(getDeltaMovement().add(0, Math.sin(tickCount * 0.08) * 0.003, 0));
	}

	@Override
	public boolean removeWhenFarAway(double distSqr) {
		return distSqr > 64 * 64;
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(DefaultAnimations.genericWalkIdleController());
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}
}
