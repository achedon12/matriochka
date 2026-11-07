package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.mixin.DisplayAccess;
import fr.achedon12.matriochka.mixin.ItemDisplayAccess;
import fr.achedon12.matriochka.rules.PlayerState;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.item.ItemStack;

/**
 * A trophy doll won in the Trials can ride on its owner's shoulder, as a parrot would: using it sets it there (it
 * stays in the inventory), using it again takes it down. Everyone sees it. It is an item display riding the player,
 * turned with them every tick; it comes back after a teleport or a change of world, and never stays behind alone.
 */
public final class Shoulder {
	private Shoulder() {}

	private static final String TAG = "matriochka.shoulder";
	/** The doll each player wears now: a display that follows them (a player cannot carry a passenger). */
	private static final java.util.Map<java.util.UUID, Display.ItemDisplay> DOLLS = new java.util.HashMap<>();

	public static void init() {
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			for (ServerPlayer p : server.getPlayerList().getPlayers()) tick(p);
			DOLLS.entrySet().removeIf(e -> server.getPlayerList().getPlayer(e.getKey()) == null && discard(e.getValue()));
		});
		// one left behind (its player gone, a save reloaded): it goes at once
		ServerEntityEvents.ENTITY_LOAD.register((e, level) -> {
			if (e.entityTags().contains(TAG) && !DOLLS.containsValue(e)) e.discard();
		});
		ServerPlayConnectionEvents.DISCONNECT.register((h, server) -> remove(h.player));
	}

	private static boolean discard(Entity e) {
		if (e != null) e.discard();
		return true;
	}

	/** Sets the doll on the shoulder, or takes it down if it is already there. */
	public static void toggle(ServerPlayer p, ItemStack stack) {
		PlayerState ps = PlayerState.of(p);
		String id = ModContent.idOf(stack.getItem());
		boolean down = id.equals(ps.tag().getStringOr("shoulder", ""));
		ps.tag().putString("shoulder", down ? "" : id);
		ps.save();
		remove(p);
		p.sendOverlayMessage(Component.translatable("message.matriochka.shoulder." + (down ? "off" : "on"), stack.getHoverName()).withStyle(ChatFormatting.GOLD));
		p.level().playSound(null, p.blockPosition(), down ? SoundEvents.ARMOR_EQUIP_LEATHER.value() : SoundEvents.ARMOR_EQUIP_GENERIC.value(), SoundSource.PLAYERS, 0.8f, 1.3f);
	}

	private static void tick(ServerPlayer p) {
		String id = PlayerState.of(p).tag().getStringOr("shoulder", "");
		Display.ItemDisplay doll = DOLLS.get(p.getUUID());
		boolean wanted = !id.isEmpty() && p.isAlive() && !p.isSpectator() && !p.isInvisible() && ModContent.itemOrNull(id) != null;
		if (!wanted) {
			if (doll != null) remove(p);
			return;
		}
		if (!(p.level() instanceof ServerLevel level)) return;
		if (doll != null && (doll.isRemoved() || doll.level() != level)) {
			doll.discard();
			doll = null;
		}
		// on the right shoulder, turned with the body, a little lower while sneaking
		double yaw = Math.toRadians(p.yBodyRot);
		// right of the head, a hand's width forward
		double x = p.getX() - Math.cos(yaw) * 0.52 - Math.sin(yaw) * 0.18, z = p.getZ() - Math.sin(yaw) * 0.52 + Math.cos(yaw) * 0.18;
		double y = p.getY() + (p.isCrouching() ? 1.2 : 1.5);
		if (doll == null) {
			doll = fr.achedon12.matriochka.mc.McEntities.ITEM_DISPLAY.create(level, EntitySpawnReason.EVENT);
			if (doll == null) return;
			((ItemDisplayAccess) doll).matriochka$setItem(new ItemStack(ModContent.item(id)));
			((DisplayAccess) doll).matriochka$setTransformation(new com.mojang.math.Transformation(
				null, null, new org.joml.Vector3f(0.5f, 0.5f, 0.5f), null));
			((DisplayAccess) doll).matriochka$setPosRotInterpolation(2);
			doll.addTag(TAG);
			doll.setPos(x, y, z);
			DOLLS.put(p.getUUID(), doll);
			level.addFreshEntity(doll);
		}
		doll.setPos(x, y, z);
		doll.setYRot(p.yBodyRot + 90);
	}

	private static void remove(ServerPlayer p) {
		discard(DOLLS.remove(p.getUUID()));
	}
}
