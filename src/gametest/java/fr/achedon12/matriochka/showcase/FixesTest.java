package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.structure.Rewards;
import fr.achedon12.matriochka.world.Events;
import fr.achedon12.matriochka.world.MatrioData;
import java.util.ArrayList;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;

/** Checks the 0.2 fixes in a real world: ./gradlew runClientGameTest -Pfixes. Fails the run on the first broken check. */
final class FixesTest {
	private FixesTest() {}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			sp.getConnection().waitForChunksRender();
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			ctx.waitTicks(40);
			List<String> report = new java.util.ArrayList<>(server.computeOnServer(FixesTest::checks));
			ctx.waitTicks(60);
			report.addAll(server.computeOnServer(FixesTest::mimicMoved));
			for (String line : report) Matriochka.LOG.info("[fixes] {}", line);
			long failed = report.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " fix check(s) failed: " + report);
		}
	}

	private static net.minecraft.world.entity.Entity MIMIC;

	private static List<String> mimicMoved(net.minecraft.server.MinecraftServer server) {
		List<String> out = new ArrayList<>();
		double speed = MIMIC instanceof LivingEntity le ? le.getAttributeBaseValue(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED) : -1;
		check(out, speed > 0, "an unmasked Mimic can move (speed " + speed + ", id " + (MIMIC == null ? -1 : MIMIC.getId()) + ")");
		if (MIMIC != null) MIMIC.discard();
		return out;
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static boolean achieved(ServerPlayer p, String customKey) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) {
			if (!a.arg().equals(customKey)) continue;
			var h = p.level().getServer().getAdvancements().get(Matriochka.id(a.id()));
			return h != null && p.getAdvancements().getOrStartProgress(h).isDone();
		}
		return false;
	}

	private static List<String> checks(net.minecraft.server.MinecraftServer server) {
		List<String> out = new ArrayList<>();
		ServerPlayer p = server.getPlayerList().getPlayers().get(0);
		ServerLevel level = (ServerLevel) p.level();
		try {
			// journal pages: the five pages of world 1 are spread over its structures
			java.util.Set<Integer> pages = new java.util.HashSet<>();
			for (Defs.StructureDef s : Content.STRUCTURES) {
				if (s.world() == 1 && (s.role().equals("exploration") || s.role().equals("story"))) pages.add(Rewards.pageIndex(1, s.id(), 0));
			}
			check(out, pages.size() == 5, "world 1 structures hold pages " + pages);

			// a world dish sets its flag
			ItemStack broth = new ItemStack(ModContent.item("root_broth"));
			broth.finishUsingItem(level, p);
			check(out, PlayerState.of(p).flagActive("root_broth", level.getGameTime()), "Root Broth slows the toxin");

			// the Grappling Hook pulls a creature toward the player
			p.teleportTo(level, p.getX(), p.getY(), p.getZ(), java.util.Set.of(), 0f, 0f, false);
			Vec3 front = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(8));
			// a clear line between the player and the zombie, whatever the terrain
			BlockPos from = BlockPos.containing(p.getEyePosition()), to = BlockPos.containing(front.x, p.getEyeY(), front.z);
			for (BlockPos q : BlockPos.betweenClosed(Math.min(from.getX(), to.getX()) - 1, from.getY() - 1, Math.min(from.getZ(), to.getZ()) - 1,
				Math.max(from.getX(), to.getX()) + 1, from.getY() + 1, Math.max(from.getZ(), to.getZ()) + 1)) {
				level.setBlock(q, Blocks.AIR.defaultBlockState(), 3);
			}
			var zombie = net.minecraft.world.entity.EntityTypes.ZOMBIE.create(level, EntitySpawnReason.COMMAND);
			zombie.setNoAi(true);
			zombie.setPos(front.x, p.getEyeY() - 1.0, front.z);
			level.addFreshEntity(zombie);
			p.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, zombie.position().add(0, 1, 0));
			p.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(ModContent.item("grappling_hook")));
			p.getItemInHand(InteractionHand.MAIN_HAND).use(level, p, InteractionHand.MAIN_HAND);
			Vec3 toPlayer = p.position().subtract(zombie.position()).normalize();
			check(out, zombie.getDeltaMovement().dot(toPlayer) > 0.5, "the hook pulls a zombie (" + zombie.getDeltaMovement() + ")");
			zombie.discard();
			p.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);

			// a boss challenge: the Queen beaten without a mask
			BlockPos at = p.blockPosition().offset(0, 0, 12);
			MatrioBoss queen = MatrioBoss.summon(level, "spore_queen", at, p);
			for (int i = 0; i < 3; i++) queen.tick();
			queen.die(level.damageSources().playerAttack(p));
			queen.discard();
			check(out, achieved(p, "queen_no_mask"), "Short of Breath granted after the Queen without a mask");
			check(out, !achieved(p, "titan_no_lava"), "Molten Armor not granted by another boss");

			// the Doll Peddler turns up near a player
			for (int i = 0; i < 60 && level.getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(128)).isEmpty(); i++) Events.peddler(level);
			check(out, !level.getEntitiesOfClass(MatrioNpc.class, p.getBoundingBox().inflate(128), e -> e.getType() == ModContent.entity("doll_peddler")).isEmpty(), "the Doll Peddler wanders in");

			// one World Block per world and group
			MatrioData data = MatrioData.get(server);
			String group = data.groupOf(p.getUUID());
			BlockPos wb = p.blockPosition().offset(3, 0, 0);
			level.setBlock(wb, ModContent.block("world_block").defaultBlockState(), 3);
			data.setWorldBlock(group, 1, level, wb);
			boolean has = data.hasWorldBlock(server, group, 1);
			level.setBlock(wb, Blocks.AIR.defaultBlockState(), 3);
			boolean gone = !data.hasWorldBlock(server, group, 1);
			check(out, has && gone, "the group's World Block is tracked (" + has + ", " + gone + ")");

			// no diamonds in vanilla chests
			LootTable table = server.reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE, Identifier.withDefaultNamespace("chests/buried_treasure")));
			int diamonds = 0;
			for (int i = 0; i < 300; i++) {
				LootParams params = new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN, p.position()).create(LootContextParamSets.CHEST);
				for (ItemStack s : table.getRandomItems(params)) if (s.is(Items.DIAMOND)) diamonds++;
			}
			check(out, diamonds == 0, "no diamond in 300 buried treasures (" + diamonds + ")");

			// a mimic next to the player: it is unmasked on its next real ticks (checked in mimicMoved)
			var mimic = ModContent.entity("mimic").create(level, EntitySpawnReason.COMMAND);
			mimic.setPos(p.getX() + 1.5, p.getY(), p.getZ());
			mimic.setNoGravity(true);
			level.addFreshEntity(mimic);
			MIMIC = mimic;
		} catch (Throwable t) {
			out.add("FAIL exception " + t);
			Matriochka.LOG.error("[fixes]", t);
		}
		return out;
	}
}
