package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import fr.achedon12.matriochka.entity.MatrioMob;
import fr.achedon12.matriochka.entity.MatrioNpc;
import fr.achedon12.matriochka.item.Nesting;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.world.Cycles;
import fr.achedon12.matriochka.world.Endings;
import fr.achedon12.matriochka.world.MatrioData;
import fr.achedon12.matriochka.world.WorldZero;
import fr.achedon12.matriochka.world.Worlds;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.locale.Language;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;

/**
 * Checks the story and the endgame in a real world, server side: ./gradlew runClientGameTest -Pstory.
 * Journal texts, the nesting of the hidden dolls and its hints, World 0 (gate, layout, Obsession, chambers, the
 * Shadow and the kneeling), the three endings and the New Cycle. Fails the run when a check fails.
 */
final class StoryTest {
	private StoryTest() {}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var server = sp.getServer();
			McTest.waitForChunks(sp);
			server.runCommand("gamerule advance_time false");
			server.runCommand("gamerule spawn_monsters false");
			server.runCommand("gamemode survival @a");
			ctx.waitTicks(40);
			List<String> out = new ArrayList<>();
			step(server, out, StoryTest::texts);
			step(server, out, StoryTest::nesting);
			step(server, out, StoryTest::enterZero);
			ctx.setScreen(() -> null);
			ctx.waitTicks(60);
			step(server, out, StoryTest::obsessionAndChamber);
			ctx.waitTicks(60);
			step(server, out, StoryTest::gateOpens);
			ctx.waitTicks(60);
			step(server, out, StoryTest::toRoom);
			ctx.waitTicks(60);
			step(server, out, StoryTest::shadowStitches);
			ctx.runOnClient(mc -> mc.options.keyShift.setDown(true));
			step(server, out, StoryTest::kneel);
			ctx.waitTicks(260);
			ctx.runOnClient(mc -> mc.options.keyShift.setDown(false));
			step(server, out, StoryTest::setDown);
			ctx.setScreen(() -> null);
			ctx.waitTicks(20);
			step(server, out, StoryTest::endings);
			ctx.setScreen(() -> null);
			ctx.waitTicks(20);
			step(server, out, StoryTest::newCycle);
			ctx.setScreen(() -> null);
			for (String line : out) Matriochka.LOG.info("[story] {}", line);
			long failed = out.stream().filter(l -> l.startsWith("FAIL")).count();
			if (failed > 0) throw new AssertionError(failed + " story check(s) failed: " + out);
		}
	}

	private static void step(net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext server, List<String> out, Consumer2 body) {
		List<String> lines = server.computeOnServer(s -> {
			List<String> l = new ArrayList<>();
			try {
				body.accept(s, s.getPlayerList().getPlayers().get(0), l);
			} catch (Throwable t) {
				l.add("FAIL exception " + t);
				Matriochka.LOG.error("[story]", t);
			}
			return l;
		});
		out.addAll(lines);
	}

	@FunctionalInterface
	private interface Consumer2 {
		void accept(MinecraftServer server, ServerPlayer p, List<String> out);
	}

	private static void check(List<String> out, boolean ok, String what) {
		out.add((ok ? "ok   " : "FAIL ") + what);
	}

	private static boolean achieved(ServerPlayer p, String id) {
		var h = p.level().getServer().getAdvancements().get(Matriochka.id(id));
		return h != null && p.getAdvancements().getOrStartProgress(h).isDone();
	}

	private static boolean custom(ServerPlayer p, String key) {
		for (Defs.AchDef a : Content.ACHIEVEMENTS) if (a.trigger().equals("custom") && a.arg().equals(key)) return achieved(p, a.id());
		return false;
	}

	private static BlockPos origin(ServerPlayer p) {
		MatrioData data = MatrioData.get(p.level().getServer());
		return WorldZero.origin(data, data.groupOf(p.getUUID()), p.level().getServer().getLevel(Worlds.WORLD_ZERO));
	}

	// ---------------------------------------------------------------- steps
	private static void texts(MinecraftServer server, ServerPlayer p, List<String> out) {
		Language lang = Language.getInstance();
		int missing = 0;
		for (int w = 1; w <= 10; w++)
			for (int i = 0; i < 5; i++) {
				if (!lang.has("journal.matriochka.page." + w + "." + i) || !lang.has("journal.matriochka.page." + w + "." + i + ".title")) missing++;
			}
		check(out, missing == 0, "the 50 Journal pages have a title and a text (" + missing + " missing)");
		check(out, Content.JOURNAL_CODED == 3, "page 4 of every world is the coded one");
		int lines = 0;
		for (String k : new String[]{"seal", "absorb", "tools"}) {
			if (lang.has("ending.matriochka." + k + ".0") && lang.has("ending.matriochka." + k + ".lasting")) lines++;
		}
		check(out, lines == 3, "the three endings have a crawl and a lasting line");
		int hints = 0;
		for (int w = 1; w <= 10; w++) if (lang.has("message.matriochka.doll_line." + w) && lang.has("item.matriochka.hidden_doll_" + w + ".desc")) hints++;
		check(out, hints == 10, "every hidden doll has its notches and its people's line (" + hints + ")");
		java.util.Set<Integer> order = new java.util.HashSet<>();
		for (int w : Content.NEST_ORDER) order.add(w);
		check(out, order.size() == 10 && order.containsAll(List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)), "the nesting order holds the ten dolls once each");
	}

	private static void hold(ServerPlayer p, ItemStack main, ItemStack off) {
		p.setItemInHand(InteractionHand.MAIN_HAND, main);
		p.setItemInHand(InteractionHand.OFF_HAND, off);
	}

	private static ItemStack doll(int world) {
		return new ItemStack(ModContent.item("hidden_doll_" + world));
	}

	private static void nesting(MinecraftServer server, ServerPlayer p, List<String> out) {
		int[] order = Content.NEST_ORDER;
		// a wrong doll rattles and is refused
		hold(p, doll(order[0]), doll(order[2]));
		Nesting.use(p, InteractionHand.MAIN_HAND);
		check(out, Nesting.rank(p.getMainHandItem()) == 0 && Nesting.rank(p.getOffhandItem()) == 2, "a doll out of order rattles and stays apart");
		// the largest doll cannot start the nest either
		hold(p, doll(order[9]), doll(order[8]));
		Nesting.use(p, InteractionHand.MAIN_HAND);
		check(out, Nesting.depth(p.getMainHandItem()) == 0 && !p.getOffhandItem().isEmpty(), "the dolls do not nest from the outside in");
		// the right order closes them one inside the other
		hold(p, doll(order[0]), ItemStack.EMPTY);
		boolean ok = true;
		for (int k = 1; k < 10; k++) {
			p.setItemInHand(InteractionHand.OFF_HAND, doll(order[k]));
			Nesting.use(p, InteractionHand.MAIN_HAND);
			if (Nesting.depth(p.getMainHandItem()) != k + 1 || !p.getOffhandItem().isEmpty()) ok = false;
		}
		check(out, ok && p.getMainHandItem().is(ModContent.item("whole_matryoshka")), "the ten dolls nest into the Whole Matryoshka");
		check(out, custom(p, "all_dolls"), "Every Doll is granted when the tenth closes");
		// the Peddler speaks of dolls instead of trading
		var peddler = ModContent.entity("doll_peddler").create((ServerLevel) p.level(), EntitySpawnReason.COMMAND);
		peddler.setPos(p.getX() + 1, p.getY(), p.getZ());
		p.level().addFreshEntity(peddler);
		p.setItemInHand(InteractionHand.MAIN_HAND, doll(order[3]));
		((MatrioNpc) peddler).mobInteract(p, InteractionHand.MAIN_HAND);
		check(out, ((MatrioNpc) peddler).getTradingPlayer() == null, "the Peddler talks about the doll instead of trading");
		peddler.discard();
		// the structure hint
		check(out, fr.achedon12.matriochka.structure.Rewards.carverNote().is(Items.PAPER), "a Carver's Note waits beside every hidden doll");
	}

	private static void enterZero(MinecraftServer server, ServerPlayer p, List<String> out) {
		hold(p, new ItemStack(ModContent.item("whole_matryoshka")), ItemStack.EMPTY);
		Nesting.use(p, InteractionHand.MAIN_HAND);
		check(out, Worlds.number(p.level()) == 0, "the Whole Matryoshka stays shut before the Unfinished falls");
		MatrioData data = MatrioData.get(server);
		for (int w = 0; w <= 10; w++) data.markDefeated(data.groupOf(p.getUUID()), w);
		Nesting.use(p, InteractionHand.MAIN_HAND);
		check(out, Worlds.number(p.level()) == Worlds.ZERO, "it opens onto World 0 afterwards (now in " + p.level().dimension().identifier() + ")");
		BlockPos o = origin(p);
		ServerLevel z = (ServerLevel) p.level();
		check(out, z.getBlockState(o.offset(0, 0, 1)).is(ModContent.block("threshold")), "the entry hall holds the Threshold");
		check(out, z.getBlockState(WorldZero.gateCenter(o, 0)).is(ModContent.block("sealed_brick")), "the first chamber is shut by its gate");
		check(out, z.getBlockState(WorldZero.kneelSpot(o)).is(fr.achedon12.matriochka.mc.McBlocks.CARPET.red()), "the kneeling carpet lies before the bench");
		check(out, achieved(p, "endings/world_zero"), "The Smallest Doll is granted on entering");
	}

	private static void obsessionAndChamber(MinecraftServer server, ServerPlayer p, List<String> out) {
		PlayerState ps = PlayerState.of(p);
		check(out, ps.gauge("obsession") > 0, "holding something raises the Obsession (" + ps.gauge("obsession") + ")");
		p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);
		BlockPos c = WorldZero.chamberCenter(origin(p), 0);
		p.teleportTo(c.getX() + 0.5, c.getY(), c.getZ() + 0.5);
	}

	private static void gateOpens(MinecraftServer server, ServerPlayer p, List<String> out) {
		ServerLevel z = (ServerLevel) p.level();
		List<MatrioMob> guards = z.getEntitiesOfClass(MatrioMob.class, p.getBoundingBox().inflate(40), m -> m.entityTags().contains("zero_0"));
		check(out, guards.size() >= 3, "the first chamber's guards wake (" + guards.size() + ")");
		boolean scaled = !guards.isEmpty() && guards.getFirst().getMaxHealth() > guards.getFirst().def().hp() * 1.2f;
		check(out, scaled, "World 0 creatures are stronger than their kin");
		for (MatrioMob m : guards) m.discard();
	}

	private static void toRoom(MinecraftServer server, ServerPlayer p, List<String> out) {
		ServerLevel z = (ServerLevel) p.level();
		BlockPos o = origin(p);
		check(out, z.getBlockState(WorldZero.gateCenter(o, 0)).isAir(), "the gate opens once the guards are gone");
		// to the Artisan's room: the Shadow wakes
		BlockPos k = WorldZero.kneelSpot(o);
		p.teleportTo(k.getX() + 0.5, k.getY(), k.getZ() + 0.5);
	}

	private static void shadowStitches(MinecraftServer server, ServerPlayer p, List<String> out) {
		ServerLevel z = (ServerLevel) p.level();
		List<MatrioBoss> sh = z.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(40), b -> b.def.id().equals("artisan_shadow"));
		check(out, sh.size() == 1, "the Artisan's Shadow wakes in the room (" + sh.size() + ")");
		if (sh.isEmpty()) return;
		MatrioBoss shadow = sh.getFirst();
		shadow.hurtServer(z, z.damageSources().playerAttack(p), shadow.getMaxHealth() * 4);
		check(out, shadow.isAlive() && shadow.getHealth() >= shadow.getMaxHealth() * 0.99f, "brought near death, the Shadow stitches itself back");
		var e = MatrioData.get(server).worldEntry(MatrioData.get(server).groupOf(p.getUUID()), Worlds.ZERO);
		check(out, e.getBooleanOr("stitched", false), "the stitch is remembered");
	}

	private static void kneel(MinecraftServer server, ServerPlayer p, List<String> out) {
		hold(p, ItemStack.EMPTY, ItemStack.EMPTY);
		BlockPos k = WorldZero.kneelSpot(origin(p));
		p.teleportTo(k.getX() + 0.5, k.getY(), k.getZ() + 0.5);
		p.setShiftKeyDown(true);
	}

	private static void setDown(MinecraftServer server, ServerPlayer p, List<String> out) {
		PlayerState ps = PlayerState.of(p);
		check(out, ps.has("end_tools"), "kneeling empty-handed sets the tools down");
		check(out, custom(p, "third_end"), "Set Down the Tools (third_end) is granted by the third ending");
		boolean scroll = false;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) if (p.getInventory().getItem(i).is(ModContent.item("blank_scroll"))) scroll = true;
		check(out, scroll, "the Blank Scroll is given");
		ServerLevel z = (ServerLevel) p.level();
		check(out, z.getEntitiesOfClass(MatrioBoss.class, p.getBoundingBox().inflate(40), b -> b.def.id().equals("artisan_shadow")).isEmpty(), "the Shadow is gone");
		check(out, ps.gauge("obsession") < 50, "empty hands calm the Obsession (" + ps.gauge("obsession") + ")");
		fr.achedon12.matriochka.world.Travel.leave(p);
		check(out, Worlds.number(p.level()) == 0, "the Threshold leads back to the Surface");
	}

	private static void endings(MinecraftServer server, ServerPlayer p, List<String> out) {
		PlayerState ps = PlayerState.of(p);
		ps.tag().putInt("karma", 20);
		double hp0 = p.getAttributeValue(Attributes.MAX_HEALTH);
		Endings.afterUnfinished(p);
		check(out, ps.has("end_seal") && !ps.has("end_absorb"), "positive karma seals the Unfinished");
		check(out, p.getAttributeValue(Attributes.MAX_HEALTH) >= hp0 + 4 - 0.01, "Sealed lasts: two more hearts");
		check(out, achieved(p, "endings/seal"), "the Sealed advancement is granted");
		ps.tag().putInt("karma", -20);
		double dmg0 = p.getAttributeValue(Attributes.ATTACK_DAMAGE);
		Endings.afterUnfinished(p);
		check(out, ps.has("end_absorb"), "negative karma absorbs the Unfinished");
		check(out, p.getAttributeValue(Attributes.ATTACK_DAMAGE) > dmg0, "Absorbed lasts: stronger strikes");
		ps.addKarma(30);
		check(out, ps.karma() == -100, "Absorbed lasts: karma can no longer rise (" + ps.karma() + ")");
	}

	private static void newCycle(MinecraftServer server, ServerPlayer p, List<String> out) {
		MatrioData data = MatrioData.get(server);
		String group = data.groupOf(p.getUUID());
		int parcel = data.parcel(group);
		ServerLevel level = (ServerLevel) p.level();
		// an old World Block, of the first cycle
		BlockPos wb = p.blockPosition().offset(2, 0, 0);
		level.setBlock(wb, ModContent.block("world_block").defaultBlockState(), 3);
		if (level.getBlockEntity(wb) instanceof fr.achedon12.matriochka.block.DataBlockEntity be) {
			be.data().putInt("world", 1);
			be.data().putString("owner", p.getUUID().toString());
			be.changed();
		}
		p.getInventory().add(new ItemStack(ModContent.item("queen_core")));
		Cycles.begin(p);
		check(out, Cycles.of(data, group) == 1, "the New Cycle begins (cycle " + Cycles.of(data, group) + ")");
		check(out, !data.defeated(group, 0) && !data.defeated(group, 10), "the group's progression is reset");
		check(out, data.parcel(group) != parcel, "the group gets fresh worlds (parcel " + parcel + " -> " + data.parcel(group) + ")");
		boolean core = false;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) if (p.getInventory().getItem(i).is(ModContent.item("queen_core"))) core = true;
		check(out, !core, "the cores of the old cycle are taken back");
		check(out, PlayerState.of(p).has("end_seal") && PlayerState.of(p).has("end_tools"), "the endings are kept");
		check(out, achieved(p, "endings/new_cycle"), "Once More is granted");
		level.getBlockState(wb).useWithoutItem(level, p, new net.minecraft.world.phys.BlockHitResult(Vec3.atCenterOf(wb), net.minecraft.core.Direction.UP, wb, false));
		check(out, !level.getBlockState(wb).is(ModContent.block("world_block")), "a World Block of the old cycle crumbles");
		MatrioBoss boss = MatrioBoss.summon(level, "spore_queen", p.blockPosition().offset(0, 0, 14), p);
		Defs.BossDef def = boss.def;
		check(out, boss.getMaxHealth() >= def.hp() * 1.5f * 0.99f, "bosses of cycle 2 have 50% more health (" + boss.getMaxHealth() + " / " + def.hp() + ")");
		check(out, Math.abs(Cycles.damageFactor(1) - 1.25f) < 1e-4, "and 25% more damage");
		boss.discard();
	}

}
