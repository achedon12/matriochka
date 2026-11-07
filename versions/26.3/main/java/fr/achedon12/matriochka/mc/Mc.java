package fr.achedon12.matriochka.mc;

import net.minecraft.core.Holder;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.clock.ServerClockManager;
import net.minecraft.world.clock.WorldClock;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.component.ItemContainerContents;
import net.minecraft.world.level.material.PushReaction;

/**
 * The few calls that differ between the Minecraft versions the mod is built for (versions/<mc>/): this is 26.3's.
 * Every version has a class of this name with the same methods.
 */
public final class Mc {
	private Mc() {}

	public static final String VERSION = "26.3";

	public static long clockTicks(ServerClockManager clocks, Holder<WorldClock> clock) {
		return clocks.getInstance(clock).totalTicks();
	}

	public static void clearInvulnerable(LivingEntity e) {
		e.setInvulnerableTime(0);
	}

	/** Never pushed nor pulled by pistons. */
	public static PushReaction immovable() {
		return PushReaction.IMMOVEABLE;
	}

	public static int slots(ItemContainerContents c) {
		return c.size();
	}

	public static SoundEvent hoeTill() {
		return SoundEvents.HOE_TILL.value();
	}

	/** The swimming move control of fish-like mobs (generic from 26.2). */
	public static net.minecraft.world.entity.ai.control.MoveControl smoothSwim(net.minecraft.world.entity.Mob mob, int maxTurnX, int maxTurnY,
			float inWater, float outOfWater, boolean gravity) {
		return new net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl<>(mob, maxTurnX, maxTurnY, inWater, outOfWater, gravity);
	}
}
