package fr.achedon12.matriochka.rules;

import fr.achedon12.matriochka.Matriochka;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.clock.ServerClockManager;
import net.minecraft.world.clock.WorldClock;

/** World 8 runs on its own world clock, advanced 1.5 extra ticks per tick (a day lasts 8 minutes). Seasons last 2 minutes. */
public final class HastenedClock {
	public static final ResourceKey<WorldClock> KEY = ResourceKey.create(Registries.WORLD_CLOCK, Matriochka.id("hastened"));

	private HastenedClock() {}

	/** The clock of World 8's season timeline (light tint and season particles, see tools/atmosphere.py). */
	public static final ResourceKey<WorldClock> SEASONS = ResourceKey.create(Registries.WORLD_CLOCK, Matriochka.id("seasons"));

	public static void tick(ServerLevel level) {
		// keep the season clock on the game time, which is what season() reads: a resync only when it drifts
		if (level.getGameTime() % 100 == 0 && level.clockManager() instanceof ServerClockManager clocks) {
			level.registryAccess().lookupOrThrow(Registries.WORLD_CLOCK).get(SEASONS).ifPresent(h -> {
				long want = level.getGameTime() % 9600;
				if (Math.abs(clocks.getInstance(h).totalTicks() % 9600 - want) > 40) clocks.setTotalTicks(h, want);
			});
		}
		var holder = level.registryAccess().lookupOrThrow(Registries.WORLD_CLOCK).get(KEY);
		if (holder.isEmpty()) return;
		if (level.clockManager() instanceof ServerClockManager mgr) {
			boolean slowed = false;
			for (var p : level.players()) if (PlayerState.of(p).flagActive("hourglass", level.getGameTime())) slowed = true;
			// 1.5 extra ticks per tick on average: the clock runs 2.5 times as fast and a day lasts 8 minutes
			if (!slowed) mgr.addTicks(holder.get(), level.getGameTime() % 2 == 0 ? 2 : 1);
		}
	}

	/** 0 spring, 1 summer, 2 autumn, 3 winter. */
	public static int season(ServerLevel level) {
		return (int) ((level.getGameTime() / 2400) % 4);
	}
}
