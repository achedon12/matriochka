package fr.achedon12.matriochka.rules;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.minecraft.server.MinecraftServer;

/**
 * The per-tick side of the four worlds that physically change: World 3's moving halls, World 5's burning lights and
 * lantern glow, World 6's gravity columns and World 9's shifting ground. The once-per-second side lives in
 * {@link WorldRules}.
 */
public final class MovingWorlds {
	private MovingWorlds() {}

	public static void init() {
		PlacedBlocks.init();
		ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
			DungeonShift.clearAll();
			ShiftingGround.clearAll();
			GravityZones.clearAll();
			Burnout.clearAll();
		});
	}

	static void tick(MinecraftServer server, long t) {
		DungeonShift.tick(server);
		ShiftingGround.tick(server);
		GravityZones.tick(server, p -> WorldRules.rule(p) == 6);
		if (t % 4 == 0) Burnout.tickGlows(server, p -> WorldRules.rule(p) == 5);
	}
}
