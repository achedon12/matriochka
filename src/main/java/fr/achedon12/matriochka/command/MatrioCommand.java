package fr.achedon12.matriochka.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.Worlds;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

/** /matriochka — groups, progression, worlds, bosses, karma and debug. */
public final class MatrioCommand {
	private MatrioCommand() {}

	public static void init() {
		CommandRegistrationCallback.EVENT.register((d, ctx, env) -> register(d));
	}

	private static int msg(CommandSourceStack s, String key, Object... args) {
		s.sendSuccess(() -> Component.translatable(key, args), false);
		return 1;
	}

	private static void register(CommandDispatcher<CommandSourceStack> d) {
		java.util.function.Predicate<CommandSourceStack> op = Commands.hasPermission(Commands.LEVEL_GAMEMASTERS);
		d.register(Commands.literal("matriochka")
			.then(Commands.literal("group")
				.then(Commands.literal("info").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					MatrioData data = MatrioData.get(c.getSource().getServer());
					String g = data.groupOf(p.getUUID());
					return msg(c.getSource(), "command.matriochka.group.info", data.members(g).size(), Integer.toBinaryString(data.group(g).getIntOr("done", 0)));
				}))
				.then(Commands.literal("invite").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					ServerPlayer t = EntityArgument.getPlayer(c, "player");
					PlayerState.of(t).tag().putString("invite", MatrioData.get(c.getSource().getServer()).groupOf(p.getUUID()));
					t.sendSystemMessage(Component.translatable("command.matriochka.group.invited", p.getDisplayName()));
					return msg(c.getSource(), "command.matriochka.group.invite_sent", t.getDisplayName());
				})))
				.then(Commands.literal("join").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					String inv = PlayerState.of(p).tag().getStringOr("invite", "");
					if (inv.isEmpty()) return msg(c.getSource(), "command.matriochka.group.no_invite");
					boolean ok = MatrioData.get(c.getSource().getServer()).join(p.getUUID(), inv);
					return msg(c.getSource(), ok ? "command.matriochka.group.joined" : "command.matriochka.group.full");
				}))
				.then(Commands.literal("leave").executes(c -> {
					MatrioData.get(c.getSource().getServer()).leave(c.getSource().getPlayerOrException().getUUID());
					return msg(c.getSource(), "command.matriochka.group.left");
				})))
			.then(Commands.literal("progression").requires(op)
				.then(Commands.literal("set").then(Commands.argument("world", IntegerArgumentType.integer(0, 10)).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					MatrioData data = MatrioData.get(c.getSource().getServer());
					int w = IntegerArgumentType.getInteger(c, "world");
					for (int i = 0; i <= w; i++) data.markDefeated(data.groupOf(p.getUUID()), i);
					PlayerState.of(p).sync();
					return msg(c.getSource(), "command.matriochka.progression.set", w);
				}))))
			.then(Commands.literal("world").requires(op)
				.then(Commands.literal("enter").then(Commands.argument("world", IntegerArgumentType.integer(1, 10)).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Travel.enter(p, IntegerArgumentType.getInteger(c, "world"), p.blockPosition());
					return 1;
				})))
				.then(Commands.literal("leave").executes(c -> Travel.leave(c.getSource().getPlayerOrException()) ? 1 : 0)))
			.then(Commands.literal("boss").requires(op)
				.then(Commands.argument("id", StringArgumentType.word()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					String id = StringArgumentType.getString(c, "id");
					if (ModContent.entity(id) == null) return msg(c.getSource(), "command.matriochka.boss.unknown", id);
					MatrioBoss.summon(c.getSource().getLevel(), id, p.blockPosition().relative(p.getDirection(), 6), p);
					return 1;
				})))
			.then(Commands.literal("karma")
				.then(Commands.literal("show").executes(c -> {
					PlayerState ps = PlayerState.of(c.getSource().getPlayerOrException());
					return msg(c.getSource(), "command.matriochka.karma.show", ps.karma(), ps.souls());
				}))
				.then(Commands.literal("add").requires(op).then(Commands.argument("player", EntityArgument.player())
					.then(Commands.argument("amount", IntegerArgumentType.integer(-200, 200)).executes(c -> {
						PlayerState.of(EntityArgument.getPlayer(c, "player")).addKarma(IntegerArgumentType.getInteger(c, "amount"));
						return 1;
					}))))
				.then(Commands.literal("soul").requires(op).then(Commands.argument("player", EntityArgument.player())
					.then(Commands.argument("amount", IntegerArgumentType.integer(0, 100000)).executes(c -> {
						PlayerState.of(EntityArgument.getPlayer(c, "player")).addSouls(IntegerArgumentType.getInteger(c, "amount"));
						return 1;
					})))))
			.then(Commands.literal("station").requires(op).then(Commands.argument("id", StringArgumentType.word()).executes(c -> {
				ServerPlayer p = c.getSource().getPlayerOrException();
				String id = StringArgumentType.getString(c, "id");
				var pos = p.blockPosition().relative(p.getDirection(), 2);
				p.level().setBlock(pos, ModContent.block(id).defaultBlockState(), 3);
				var state = p.level().getBlockState(pos);
				state.useWithoutItem(p.level(), p, new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(pos), net.minecraft.core.Direction.UP, pos, false));
				return 1;
			})))
			.then(Commands.literal("debug").requires(op).executes(c -> {
				ServerPlayer p = c.getSource().getPlayerOrException();
				PlayerState ps = PlayerState.of(p);
				return msg(c.getSource(), "command.matriochka.debug", Worlds.number(p.level()), Worlds.parcelOf(p.blockPosition()),
					String.format("%.0f/%.0f/%.0f/%.0f", ps.gauge("toxin"), ps.gauge("heat"), ps.gauge("noise"), ps.gauge("oxygen")), ps.dollLayers());
			})));
	}
}
