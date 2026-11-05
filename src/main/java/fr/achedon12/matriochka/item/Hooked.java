package fr.achedon12.matriochka.item;

import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;

/** Creatures recently pulled by a Grappling Hook, and by whom: a fall into the void soon after counts for that player. */
public final class Hooked {
	private Hooked() {}

	private record Pull(UUID player, long time) {}

	private static final Map<LivingEntity, Pull> PULLS = new WeakHashMap<>();

	static void mark(LivingEntity e, ServerPlayer by, long time) {
		PULLS.put(e, new Pull(by.getUUID(), time));
	}

	/** The player who hooked this creature within the last ten seconds, or null. */
	public static UUID by(LivingEntity e, long now) {
		Pull p = PULLS.remove(e);
		return p != null && now - p.time() <= 200 ? p.player() : null;
	}
}
