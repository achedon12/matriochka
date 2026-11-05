package fr.achedon12.matriochka.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Lairs;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.Travel;
import fr.achedon12.matriochka.world.WorldAdmin;
import fr.achedon12.matriochka.world.Worlds;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

/** /matriochka: groups (leader, kicks, disband), progression, worlds (list, repair, move, reset), bosses, karma and debug. */
public final class MatrioCommand {
	private MatrioCommand() {}

	public static void init() {
		CommandRegistrationCallback.EVENT.register((d, ctx, env) -> register(d));
	}

	/** The lair heart of the player's group in the world they stand in, if that world has a lair. */
	private static BlockPos lairHeart(ServerPlayer p) {
		int world = Worlds.number(p.level());
		if (world == 0 || !ModContent.bossForWorld(world).lair()) return null;
		MatrioData data = MatrioData.get(p.level().getServer());
		var entry = data.worldEntry(data.groupOf(p.getUUID()), world);
		if (!entry.contains("seuil_y")) return null;
		BlockPos seuil = new BlockPos(entry.getIntOr("seuil_x", 0), entry.getIntOr("seuil_y", 64), entry.getIntOr("seuil_z", 0));
		return Lairs.heart(world, seuil.offset(0, 0, Worlds.ARENA_OFFSET));
	}

	private static String groupOf(com.mojang.brigadier.context.CommandContext<CommandSourceStack> c, String arg) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		return MatrioData.get(c.getSource().getServer()).groupOf(EntityArgument.getPlayer(c, arg).getUUID());
	}

	/** Only the leader invites, kicks, hands over the lead or disbands. */
	private static boolean leads(CommandSourceStack s, ServerPlayer p) {
		if (MatrioData.get(s.getServer()).isLeader(p.getUUID())) return true;
		s.sendFailure(Component.translatable("command.matriochka.group.not_leader"));
		return false;
	}

	private static String name(CommandSourceStack s, String uuid) {
		try {
			ServerPlayer p = s.getServer().getPlayerList().getPlayer(java.util.UUID.fromString(uuid));
			if (p != null) return p.getGameProfile().name();
		} catch (IllegalArgumentException ignored) {
			// no leader recorded
		}
		return uuid.length() > 8 ? uuid.substring(0, 8) : uuid;
	}

	private static String names(CommandSourceStack s, java.util.List<java.util.UUID> ids) {
		StringBuilder b = new StringBuilder();
		for (java.util.UUID u : ids) {
			if (!b.isEmpty()) b.append(", ");
			b.append(name(s, u.toString()));
		}
		return b.toString();
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
					msg(c.getSource(), "command.matriochka.group.info", data.members(g).size(), Integer.toBinaryString(data.group(g).getIntOr("done", 0)));
					return msg(c.getSource(), "command.matriochka.group.members", names(c.getSource(), data.members(g)), name(c.getSource(), data.leader(g)));
				}))
				.then(Commands.literal("leader").executes(c -> {
					MatrioData data = MatrioData.get(c.getSource().getServer());
					String g = data.groupOf(c.getSource().getPlayerOrException().getUUID());
					return msg(c.getSource(), "command.matriochka.group.leader", name(c.getSource(), data.leader(g)));
				}))
				.then(Commands.literal("invite").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					if (!leads(c.getSource(), p)) return 0;
					ServerPlayer t = EntityArgument.getPlayer(c, "player");
					PlayerState.of(t).tag().putString("invite", MatrioData.get(c.getSource().getServer()).groupOf(p.getUUID()));
					t.sendSystemMessage(Component.translatable("command.matriochka.group.invited", p.getDisplayName()));
					return msg(c.getSource(), "command.matriochka.group.invite_sent", t.getDisplayName());
				})))
				.then(Commands.literal("join").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					String inv = PlayerState.of(p).tag().getStringOr("invite", "");
					if (inv.isEmpty()) return msg(c.getSource(), "command.matriochka.group.no_invite");
					MatrioData data = MatrioData.get(c.getSource().getServer());
					String old = data.groupOf(p.getUUID());
					boolean ok = data.join(p.getUUID(), inv);
					if (ok) {
						PlayerState.of(p).tag().remove("invite");
						WorldAdmin.expel(c.getSource().getServer(), p.getUUID(), old);
					}
					return msg(c.getSource(), ok ? "command.matriochka.group.joined" : "command.matriochka.group.full");
				}))
				.then(Commands.literal("leave").executes(c -> {
					WorldAdmin.kick(c.getSource().getServer(), c.getSource().getPlayerOrException().getUUID());
					return msg(c.getSource(), "command.matriochka.group.left");
				}))
				.then(Commands.literal("kick").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					if (!leads(c.getSource(), p)) return 0;
					ServerPlayer t = EntityArgument.getPlayer(c, "player");
					MatrioData data = MatrioData.get(c.getSource().getServer());
					if (t == p || !data.groupOf(t.getUUID()).equals(data.groupOf(p.getUUID()))) return msg(c.getSource(), "command.matriochka.group.not_member", t.getDisplayName());
					WorldAdmin.kick(c.getSource().getServer(), t.getUUID());
					t.sendSystemMessage(Component.translatable("command.matriochka.group.kicked_you", p.getDisplayName()));
					return msg(c.getSource(), "command.matriochka.group.kicked", t.getDisplayName());
				})))
				.then(Commands.literal("transfer").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					if (!leads(c.getSource(), p)) return 0;
					ServerPlayer t = EntityArgument.getPlayer(c, "player");
					MatrioData data = MatrioData.get(c.getSource().getServer());
					if (!data.transfer(data.groupOf(p.getUUID()), t.getUUID())) return msg(c.getSource(), "command.matriochka.group.not_member", t.getDisplayName());
					t.sendSystemMessage(Component.translatable("command.matriochka.group.lead_given"));
					return msg(c.getSource(), "command.matriochka.group.transferred", t.getDisplayName());
				})))
				.then(Commands.literal("disband").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					if (!leads(c.getSource(), p)) return 0;
					MatrioData data = MatrioData.get(c.getSource().getServer());
					var was = WorldAdmin.disband(c.getSource().getServer(), data.groupOf(p.getUUID()));
					for (var u : was) {
						ServerPlayer m = c.getSource().getServer().getPlayerList().getPlayer(u);
						if (m != null && m != p) m.sendSystemMessage(Component.translatable("command.matriochka.group.disbanded"));
					}
					return msg(c.getSource(), "command.matriochka.group.disbanded");
				})))
			.then(Commands.literal("progression").requires(op)
				.then(Commands.literal("show").then(Commands.argument("player", EntityArgument.player()).executes(c -> {
					ServerPlayer t = EntityArgument.getPlayer(c, "player");
					MatrioData data = MatrioData.get(c.getSource().getServer());
					String g = data.groupOf(t.getUUID());
					return msg(c.getSource(), "command.matriochka.progression.show", t.getDisplayName(), data.highestDefeated(g), Integer.toBinaryString(data.group(g).getIntOr("done", 0)));
				})))
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
				.then(Commands.literal("zero").executes(c -> {
					fr.achedon12.matriochka.world.WorldZero.enter(c.getSource().getPlayerOrException());
					return 1;
				}))
				.then(Commands.literal("leave").executes(c -> Travel.leave(c.getSource().getPlayerOrException()) ? 1 : 0))
				.then(Commands.literal("list").executes(c -> {
					var lines = WorldAdmin.list(c.getSource().getServer());
					if (lines.isEmpty()) return msg(c.getSource(), "command.matriochka.world.none");
					for (Component line : lines) c.getSource().sendSuccess(() -> line, false);
					return lines.size();
				}))
				.then(Commands.literal("repair").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("world", IntegerArgumentType.integer(1, 10)).executes(c -> {
					String g = groupOf(c, "player");
					int w = IntegerArgumentType.getInteger(c, "world");
					return WorldAdmin.repair(c.getSource().getServer(), g, w) ? msg(c.getSource(), "command.matriochka.world.repaired", w) : msg(c.getSource(), "command.matriochka.world.unknown", w);
				}))))
				.then(Commands.literal("move").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("world", IntegerArgumentType.integer(1, 10)).executes(c -> {
					String g = groupOf(c, "player");
					int w = IntegerArgumentType.getInteger(c, "world");
					BlockPos at = BlockPos.containing(c.getSource().getPosition());
					WorldAdmin.move(c.getSource().getServer(), g, w, c.getSource().getLevel(), at);
					return msg(c.getSource(), "command.matriochka.world.moved", w, at.getX(), at.getY(), at.getZ());
				}))))
				.then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("world", IntegerArgumentType.integer(1, 10)).executes(c -> {
					String g = groupOf(c, "player");
					int w = IntegerArgumentType.getInteger(c, "world");
					WorldAdmin.reset(c.getSource().getServer(), g, w);
					return msg(c.getSource(), "command.matriochka.world.reset", w);
				})))))
			.then(Commands.literal("boss").requires(op)
				.then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player()).then(Commands.argument("world", IntegerArgumentType.integer(0, 10)).executes(c -> {
					String g = groupOf(c, "player");
					int w = IntegerArgumentType.getInteger(c, "world");
					WorldAdmin.resetBoss(c.getSource().getServer(), g, w);
					return msg(c.getSource(), "command.matriochka.boss.reset", w);
				}))))
				.then(Commands.argument("id", StringArgumentType.word()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					String id = StringArgumentType.getString(c, "id");
					if (ModContent.entity(id) == null) return msg(c.getSource(), "command.matriochka.boss.unknown", id);
					MatrioBoss.summon(c.getSource().getLevel(), id, p.blockPosition().relative(p.getDirection(), 6), p);
					return 1;
				})))
			.then(Commands.literal("lair").requires(op)
				.then(Commands.literal("rearm").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					BlockPos heart = lairHeart(p);
					if (heart == null || !Lairs.rearm((ServerLevel) p.level(), heart)) return msg(c.getSource(), "command.matriochka.lair.none");
					return msg(c.getSource(), "command.matriochka.lair.rearmed", heart.getX(), heart.getY(), heart.getZ());
				}))
				.then(Commands.literal("tp").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					BlockPos heart = lairHeart(p);
					if (heart == null) return msg(c.getSource(), "command.matriochka.lair.none");
					BlockPos at = Lairs.forecourt(Worlds.number(p.level()), heart);
					p.teleportTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
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
			.then(Commands.literal("ending").requires(op).then(Commands.argument("kind", StringArgumentType.word())
				.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(new String[]{"seal", "absorb", "tools"}, b)).executes(c -> {
					String kind = StringArgumentType.getString(c, "kind");
					if (!kind.equals("seal") && !kind.equals("absorb") && !kind.equals("tools")) return 0;
					fr.achedon12.matriochka.world.Endings.play(c.getSource().getPlayerOrException(), kind);
					return msg(c.getSource(), "command.matriochka.ending.done", kind);
				})))
			.then(Commands.literal("cycle")
				.then(Commands.literal("show").executes(c -> msg(c.getSource(), "command.matriochka.cycle.show",
					fr.achedon12.matriochka.world.Cycles.of(c.getSource().getPlayerOrException()) + 1)))
				.then(Commands.literal("begin").requires(op).executes(c -> {
					fr.achedon12.matriochka.world.Cycles.begin(c.getSource().getPlayerOrException());
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
