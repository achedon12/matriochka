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
 * Journal's Worlds page. Shots: polish_*.png.
 */
final class PolishTest {
	private PolishTest() {}

	private static void shot(ClientGameTestContext ctx, String name) {
		ctx.takeScreenshot(TestScreenshotOptions.of("polish_" + name).withSize(1600, 900).disableCounterPrefix());
	}

	static void run(ClientGameTestContext ctx) {
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			ctx.getInput().resizeWindow(1600, 900);
			sp.getConnection().waitForChunksRender();
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
			// the Journal's Worlds page
			ctx.setScreen(() -> new JournalScreen(false).tab(3));
			ctx.waitTicks(30);
			shot(ctx, "journal_worlds");
			ctx.setScreen(() -> null);
			Matriochka.LOG.info("[polish] ok");
		}
	}
}
