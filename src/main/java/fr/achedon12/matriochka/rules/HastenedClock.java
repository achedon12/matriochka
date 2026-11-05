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

	public static void tick(ServerLevel level) {
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
