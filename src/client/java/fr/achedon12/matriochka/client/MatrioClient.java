package fr.achedon12.matriochka.client;

import com.geckolib.model.DefaultedEntityGeoModel;
import com.geckolib.renderer.GeoEntityRenderer;
import com.geckolib.renderer.layer.builtin.AutoGlowingGeoLayer;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.net.Net;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;

/** Client entry point: GeckoLib renderers, HUD gauges, Journal and station screens. */
public class MatrioClient implements ClientModInitializer {
	public static CompoundTag state = new CompoundTag();

	@Override
	@SuppressWarnings({"unchecked", "rawtypes"})
	public void onInitializeClient() {
		for (Defs.MobDef d : Content.MOBS) registerBoss(d.id(), d.scale());
		for (Defs.BossDef d : Content.BOSSES) registerBoss(d.id(), d.scale());
		for (Defs.CritterDef d : Content.CRITTERS) registerBoss(d.id(), 1f);
		for (Defs.NpcDef d : Content.PEOPLES) register(d.id(), 1f);
		MenuScreens.register(ModContent.STATION_MENU, StationScreen::new);
		// the miniature world over every World Block (the renderer skips the other blocks sharing this entity type)
		net.fabricmc.fabric.api.client.rendering.v1.BlockEntityRendererRegistry.register(ModContent.BE_DATA, WorldBlockRenderer::new);
		HudElementRegistry.addLast(Matriochka.id("gauges"), new Hud());
		ClientPlayNetworking.registerGlobalReceiver(Net.StatePayload.TYPE, (p, ctx) -> state = p.tag());
		// class and armor layers on gear from outside the mod (Matriochka items write their own tooltip)
		net.fabricmc.fabric.api.client.item.v1.ItemTooltipCallback.EVENT.register((stack, ctx, flag, lines) -> {
			if (!(stack.getItem() instanceof fr.achedon12.matriochka.item.MatrioItem)) fr.achedon12.matriochka.gear.GearClasses.appendTooltip(stack, lines::add);
		});
		ClientPlayNetworking.registerGlobalReceiver(Net.OpenJournalPayload.TYPE, (p, ctx) -> Minecraft.getInstance().setScreenAndShow(new JournalScreen(p.scroll())));
		net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents.END_CLIENT_TICK.register(MusicThemes::tick);
		ClientPlayNetworking.registerGlobalReceiver(Net.EndingPayload.TYPE, (p, ctx) -> Minecraft.getInstance().setScreenAndShow(new EndingScreen(p.kind())));
		ReplayClient.init();
	}

	@SuppressWarnings({"unchecked", "rawtypes"})
	private static void register(String id, float scale) {
		EntityType type = ModContent.entity(id);
		EntityRendererRegistry.register(type, ctx -> new GeoEntityRenderer(ctx, new DefaultedEntityGeoModel(Matriochka.id(id))).withScale(scale));
	}

	@SuppressWarnings({"unchecked", "rawtypes"})
	private static void registerBoss(String id, float scale) {
		EntityType type = ModContent.entity(id);
		EntityRendererRegistry.register(type, ctx -> {
			GeoEntityRenderer r = new GeoEntityRenderer(ctx, new DefaultedEntityGeoModel(Matriochka.id(id))).withScale(scale);
			r.withRenderLayer(new AutoGlowingGeoLayer(r));
			return r;
		});
	}

	static Entity unused() {
		return null;
	}
}
