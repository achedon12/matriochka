package fr.achedon12.matriochka.world;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.net.Net;
import fr.achedon12.matriochka.rules.PlayerState;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;

/**
 * The three endings. After the Unfinished falls, karma decides: Seal (zero or more) locks the creature away again,
 * Absorb (negative) takes its hunger. The third, Set Down the Tools, comes from World 0 ({@link WorldZero}).
 * Each ending is a persistent player flag ("end_seal", "end_absorb", "end_tools"), an advancement, a lasting
 * consequence and a crawl on the client ({@code EndingScreen}).
 */
public final class Endings {
	public static final String SEAL = "seal", ABSORB = "absorb", TOOLS = "tools";
	private static final Identifier SEAL_HEALTH = Matriochka.id("ending_seal_health");
	private static final Identifier ABSORB_DAMAGE = Matriochka.id("ending_absorb_damage");

	private Endings() {}

	/** The Unfinished has fallen with this player beside it. */
	public static void afterUnfinished(ServerPlayer p) {
		play(p, PlayerState.of(p).karma() >= 0 ? SEAL : ABSORB);
	}

	public static boolean seen(PlayerState ps, String kind) {
		return ps.has("end_" + kind);
	}

	public static boolean any(PlayerState ps) {
		return seen(ps, SEAL) || seen(ps, ABSORB) || seen(ps, TOOLS);
	}

	public static void play(ServerPlayer p, String kind) {
		PlayerState ps = PlayerState.of(p);
		boolean first = !seen(ps, kind);
		ps.set("end_" + kind, true);
		switch (kind) {
			case SEAL -> Achievements.grantId(p, "endings/seal");
			case ABSORB -> {
				Achievements.grantId(p, "endings/absorb");
				// the creature's hunger leaves no room for kindness: karma falls to the bottom and stays there
				ps.addKarma(-200);
			}
			case TOOLS -> {
				Achievements.grant(p, "third_end");
				ItemStack scroll = new ItemStack(ModContent.item("blank_scroll"));
				if (first && !p.getInventory().add(scroll)) p.spawnAtLocation((net.minecraft.server.level.ServerLevel) p.level(), scroll);
			}
			default -> {}
		}
		applyLasting(p);
		p.sendSystemMessage(Component.translatable("ending.matriochka." + kind + ".lasting").withStyle(ChatFormatting.GOLD));
		p.sendSystemMessage(Component.translatable("ending.matriochka.cycle_hint").withStyle(ChatFormatting.GRAY));
		ps.sync();
		Net.playEnding(p, kind);
	}

	/** The lasting consequences, put back on the player after every respawn and login. */
	public static void applyLasting(ServerPlayer p) {
		PlayerState ps = PlayerState.of(p);
		var health = p.getAttribute(Attributes.MAX_HEALTH);
		if (health != null && seen(ps, SEAL) && !health.hasModifier(SEAL_HEALTH)) {
			health.addPermanentModifier(new AttributeModifier(SEAL_HEALTH, 4, AttributeModifier.Operation.ADD_VALUE));
		}
		var damage = p.getAttribute(Attributes.ATTACK_DAMAGE);
		if (damage != null && seen(ps, ABSORB) && !damage.hasModifier(ABSORB_DAMAGE)) {
			damage.addPermanentModifier(new AttributeModifier(ABSORB_DAMAGE, 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
		}
	}
}
