package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.client.JournalScreen;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.world.MatrioData;
import java.util.List;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.world.item.ItemStack;

/**
 * The finish of the interface: ./gradlew runClientGameTest -Ppolish. Photographs an item's tooltip with its strip of
 * icons (world, rarity, souls), a Matriochka advancement on the mod's own card, and the nested worlds on the
 * Journal's Worlds page, and a person's greeting bubble. Shots: polish_*.png.
 */
final class PolishTest {
	private PolishTest() {}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of("polish_" + name).withSize(1600, 900).disableCounterPrefix());
	}

	static void run(ClientGameTestContext ctx) {
		// the title screen and its row of dolls
		ctx.getInput().resizeWindow(1600, 900);
		ctx.setScreen(() -> new net.minecraft.client.gui.screens.TitleScreen());
		ctx.waitTicks(40);
		shot(ctx, "title");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			McTest.waitForChunks(sp);
			for (String c : List.of("gamerule advance_time false", "time set 6000", "gamerule spawn_monsters false", "gamemode survival @a")) s.runCommand(c);
			ctx.setScreen(() -> null);
			// a few worlds beaten, so the Journal's map shows painted, open and bare dolls
			s.runOnServer(srv -> {
				var p = srv.getPlayerList().getPlayers().get(0);
				MatrioData md = MatrioData.get(srv);
				for (int w = 0; w <= 3; w++) md.markDefeated(md.groupOf(p.getUUID()), w);
				fr.achedon12.matriochka.rules.PlayerState.of(p).sync();
				p.getInventory().setItem(0, new ItemStack(ModContent.item("ash_hammer")));
				p.getInventory().setItem(1, new ItemStack(ModContent.item("lightning_lance")));
			});
			ctx.waitTicks(20);
			// the tooltip of a weapon of World 2, the cursor over the first hotbar slot
			ctx.setScreen(() -> new InventoryScreen(net.minecraft.client.Minecraft.getInstance().player));
			ctx.waitTicks(10);
			for (int slot = 0; slot < 2; slot++) {
				final int k = slot;
				double[] at = ctx.computeOnClient(mc -> {
					int gw = mc.getWindow().getGuiScaledWidth(), gh = mc.getWindow().getGuiScaledHeight();
					double sc = mc.getWindow().getGuiScale();
					return new double[]{((gw - 176) / 2 + 8 + k * 18 + 8) * sc, ((gh - 166) / 2 + 142 + 8) * sc};
				});
				ctx.getInput().setCursorPos(at[0], at[1]);
				ctx.waitTicks(6);
				shot(ctx, "tooltip_" + slot);
			}
			ctx.setScreen(() -> null);
			// an advancement of World 2 and a challenge, on the mod's own cards
			s.runCommand("advancement grant @a only matriochka:world_2/a0");
			ctx.waitTicks(25);
			shot(ctx, "toast");
			// a person of the worlds greets the player who comes near, in a bubble over its head
			s.runOnServer(srv -> {
				var p = srv.getPlayerList().getPlayers().get(0);
				p.teleportTo(p.getX(), p.getY(), p.getZ());
				p.setYRot(180);
				p.setXRot(10);
				p.connection.teleport(p.getX(), p.getY(), p.getZ(), 180, 10);
			});
			s.runCommand("execute as @p at @s run summon matriochka:doll_peddler ^ ^ ^3 {NoAI:1b}");
			ctx.waitTicks(50);
			shot(ctx, "bubble");
			s.runCommand("kill @e[type=matriochka:doll_peddler]");
			// a trophy doll on the player's shoulder, seen from the front
			s.runOnServer(srv -> {
				var p = srv.getPlayerList().getPlayers().get(0);
				// on a pillar in the open sky, so the camera has room
				var l = srv.overworld();
				net.minecraft.core.BlockPos at = net.minecraft.core.BlockPos.containing(p.getX(), 150, p.getZ());
				l.setBlock(at, net.minecraft.world.level.block.Blocks.SMOOTH_QUARTZ.defaultBlockState(), 3);
				p.connection.teleport(at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 150, 0);
				fr.achedon12.matriochka.world.Shoulder.toggle(p, new ItemStack(ModContent.item("trophy_doll_4")));
			});
			ctx.runOnClient(mc -> mc.options.setCameraType(net.minecraft.client.CameraType.THIRD_PERSON_FRONT));
			ctx.runOnClient(mc -> mc.particleEngine.clearParticles());
			ctx.waitTicks(40);
			s.runOnServer(srv -> {
				var p = srv.getPlayerList().getPlayers().get(0);
				for (var e : p.getPassengers()) Matriochka.LOG.info("[polish] rides the player: {} {} at {}", e.getType(), e.entityTags(), e.position());
				Matriochka.LOG.info("[polish] player at {}", p.position());
			});
			shot(ctx, "shoulder");
			ctx.runOnClient(mc -> mc.options.setCameraType(net.minecraft.client.CameraType.FIRST_PERSON));
			// the Journal's Worlds page
			ctx.setScreen(() -> new JournalScreen(false).tab(3));
			ctx.waitTicks(30);
			shot(ctx, "journal_worlds");
			// the objective page after a long time stuck on it: both hints are out
			ctx.runOnClient(mc -> fr.achedon12.matriochka.client.Hints.setTicks(40 * 60 * 20));
			ctx.setScreen(() -> new JournalScreen(false).tab(0));
			ctx.waitTicks(30);
			shot(ctx, "journal_hints");
			ctx.runOnClient(mc -> fr.achedon12.matriochka.client.Hints.setTicks(0));
			ctx.setScreen(() -> null);
			// World 6's sky at noon, looking up: the sun has gone under, the stars are out
			s.runCommand("execute in matriochka:world_6 run tp @a 0 200 0 0 -70");
			s.runCommand("gamemode spectator @a");
			ctx.waitTicks(60);
			McTest.waitForChunks(sp);
			ctx.waitTicks(20);
			shot(ctx, "sky_6_noon");
			// the Surface's new places, set down in a row on the overworld and seen from above, three quarters
			s.runCommand("execute in minecraft:overworld run tp @a 200 120 200");
			ctx.waitTicks(40);
			String[] places = {"artisan_cabin", "peddler_stall", "fallen_doll"};
			for (int i = 0; i < places.length; i++) {
				int x = 200 + i * 60;
				s.runCommand("execute in minecraft:overworld positioned " + x + " 0 200 run place structure matriochka:" + places[i] + " ~ ~ ~");
				s.runCommand("execute in minecraft:overworld positioned " + x + " 0 200 run tp @a ~ ~ ~");
				s.runCommand("execute in minecraft:overworld at @a run tp @a ~-14 ~ ~-14 -45 35");
				ctx.waitTicks(30);
				McTest.waitForChunks(sp);
				s.runCommand("execute in minecraft:overworld positioned " + x + " 0 200 positioned over world_surface run tp @a ~-14 ~14 ~-14 -45 35");
				ctx.waitTicks(40);
				McTest.waitForChunks(sp);
				ctx.waitTicks(20);
				shot(ctx, "surface_" + places[i]);
			}
			// a world card in the Journal: World 1's items and how each is had
			s.runCommand("gamemode survival @a");
			ctx.setScreen(() -> {
				JournalScreen j = new JournalScreen(false).tab(3);
				j.openCard(1);
				return j;
			});
			ctx.waitTicks(30);
			shot(ctx, "journal_card_1");
			ctx.setScreen(() -> null);
			Matriochka.LOG.info("[polish] ok");
		}
	}
}
