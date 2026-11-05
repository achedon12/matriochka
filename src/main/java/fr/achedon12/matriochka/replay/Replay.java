package fr.achedon12.matriochka.replay;

import com.mojang.brigadier.arguments.StringArgumentType;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;

/**
 * Replay value, wired in one place: the Trials, the world events, the talents and the new gear. Called once from the
 * mod initializer, after the content is registered.
 */
public final class Replay {
	private Replay() {}

	public static void init() {
		ReplayNet.init();
		fr.achedon12.matriochka.item.ReplayGear.register();
		Talents.init();
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			Trials.tick(server);
			WorldEvents.tick(server);
			Talents.tick(server);
		});
		ServerLifecycleEvents.SERVER_STOPPED.register(server -> {
			Trials.stopAll();
			WorldEvents.stopAll();
		});
		// a blow that would kill someone in a trial carries them out instead, before the Doll of Life is spent
		Identifier early = Matriochka.id("trials_first");
		ServerPlayerEvents.ALLOW_DEATH.addPhaseOrdering(early, net.fabricmc.fabric.api.event.Event.DEFAULT_PHASE);
		ServerPlayerEvents.ALLOW_DEATH.register(early, (player, source, amount) -> Trials.allowDeath(player));
		ServerPlayerEvents.JOIN.register(Trials::onJoin);
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> Talents.forget(handler.player.getUUID()));
		// the Trial Altar opens the Trials
		UseBlockCallback.EVENT.register((player, level, hand, hit) -> {
			if (!(player instanceof ServerPlayer sp) || !level.getBlockState(hit.getBlockPos()).is(ModContent.block("trial_altar"))) return InteractionResult.PASS;
			if (!Trials.unlocked(sp)) {
				sp.sendOverlayMessage(Component.translatable("message.matriochka.trial.locked").withStyle(ChatFormatting.GRAY));
				return InteractionResult.SUCCESS;
			}
			ReplayNet.sendBoard(sp, true);
			return InteractionResult.SUCCESS;
		});
		CommandRegistrationCallback.EVENT.register((d, ctx, env) -> d.register(Commands.literal("matriochka").then(Commands.literal("trials")
			.then(Commands.literal("start").then(Commands.argument("trial", StringArgumentType.word())
				.suggests((c, b) -> SharedSuggestionProvider.suggest(ReplayContent.TRIALS.stream().map(ReplayContent.TrialDef::key), b))
				.executes(c -> {
					String err = Trials.start(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "trial"));
					if (err != null) c.getSource().sendFailure(Component.translatable(err));
					return err == null ? 1 : 0;
				})))
			.then(Commands.literal("leave").executes(c -> {
				Trials.leave(c.getSource().getPlayerOrException());
				return 1;
			}))
			.then(Commands.literal("top").then(Commands.argument("trial", StringArgumentType.word())
				.suggests((c, b) -> SharedSuggestionProvider.suggest(ReplayContent.TRIALS.stream().map(ReplayContent.TrialDef::key), b))
				.executes(c -> top(c.getSource(), StringArgumentType.getString(c, "trial"))))))
			.then(Commands.literal("event").requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
				.then(Commands.argument("kind", StringArgumentType.word())
					.suggests((c, b) -> SharedSuggestionProvider.suggest(new String[]{WorldEvents.INVASION, WorldEvents.SURGE, WorldEvents.MERCHANT}, b))
					.executes(c -> {
						boolean ok = WorldEvents.start(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "kind"));
						c.getSource().sendSuccess(() -> Component.translatable(ok ? "command.matriochka.event.started" : "command.matriochka.event.refused"), false);
						return ok ? 1 : 0;
					})))));
	}

	private static int top(CommandSourceStack s, String key) {
		if (Trials.def(key) == null) {
			s.sendFailure(Component.translatable("message.matriochka.trial.unknown"));
			return 0;
		}
		var rows = Trials.top(s.getServer(), key);
		s.sendSuccess(() -> Component.translatable("command.matriochka.trial.top", Component.translatable("trial.matriochka." + key)).withStyle(ChatFormatting.GOLD), false);
		if (rows.isEmpty()) s.sendSuccess(() -> Component.translatable("command.matriochka.trial.empty").withStyle(ChatFormatting.GRAY), false);
		for (Component row : rows) s.sendSuccess(() -> row, false);
		return rows.size();
	}
}
