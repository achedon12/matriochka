package fr.achedon12.matriochka.compat;

import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.loader.api.FabricLoader;

/** Tells the server, on join, whether this client runs one of Xaero's map mods (see MapCompat). */
public final class MapCompatClient {
	private MapCompatClient() {}

	public static void init() {
		ClientPlayConnectionEvents.JOIN.register((handler, sender, mc) -> {
			boolean xaero = FabricLoader.getInstance().isModLoaded("xaerominimap") || FabricLoader.getInstance().isModLoaded("xaerominimapfair")
				|| FabricLoader.getInstance().isModLoaded("xaeroworldmap");
			if (xaero && ClientPlayNetworking.canSend(MapCompat.MapsPayload.TYPE)) ClientPlayNetworking.send(new MapCompat.MapsPayload(true));
		});
	}
}
