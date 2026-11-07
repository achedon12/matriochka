package fr.achedon12.matriochka.showcase;

import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

/** The test calls that differ between the Fabric API versions of each Minecraft version (versions/<mc>/). */
final class McTest {
	private McTest() {}

	/** Waits until the chunks around the player are drawn. */
	static void waitForChunks(TestSingleplayerContext sp) {
		sp.getClientLevel().waitForChunksRender();
	}
}
