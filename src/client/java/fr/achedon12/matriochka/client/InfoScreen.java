package fr.achedon12.matriochka.client;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.ConfirmLinkScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;

/**
 * A small parchment in a lacquer frame about the mod, opened from Mod Menu: version, what the mod is, where the
 * server rules live, and links to the wiki and the website. The mod has no client options of its own yet.
 */
public class InfoScreen extends Screen {
	private static final int W = 260, H = 170;
	private static final String WIKI = "https://github.com/achedon12/matriochka/wiki", SITE = "https://achedon12.github.io/matriochka/";
	private final Screen parent;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(320, 170);

	public InfoScreen(Screen parent) {
		super(Component.translatable("screen.matriochka.info.title"));
		this.parent = parent;
	}

	private int left() { return (width - W) / 2; }
	private int top() { return (height - H) / 2; }

	@Override
	protected void init() {
		buttons.clear();
		int l = left(), t = top(), y = t + H - 28;
		buttons.add(l + 16, y, 64, 16, Component.translatable("screen.matriochka.info.wiki"), () -> ConfirmLinkScreen.confirmLinkNow(this, java.net.URI.create(WIKI)));
		buttons.add(l + 98, y, 64, 16, Component.translatable("screen.matriochka.info.site"), () -> ConfirmLinkScreen.confirmLinkNow(this, java.net.URI.create(SITE)));
		buttons.add(l + W - 80, y, 64, 16, Component.translatable("screen.matriochka.info.done"), this::onClose);
	}

	private static String version() {
		return FabricLoader.getInstance().getModContainer("matriochka").map(c -> c.getMetadata().getVersion().getFriendlyString()).orElse("?");
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		int l = left(), t = top();
		motion.push(g, l + W / 2f, t + H / 2f);
		Ui.frame(g, l, t, W, H);
		Ui.paper(g, l + 8, t + 22, W - 16, H - 56);
		Ui.plate(g, font, title, l + W / 2, t + 4, 0, 0);
		int y = t + 30;
		g.text(font, Component.translatable("screen.matriochka.info.version", version()), l + 16, y, Ui.RED_INK, false);
		y += 13;
		y += g.textWithWordWrap(font, Component.translatable("screen.matriochka.info.body"), l + 16, y, W - 32, Ui.INK, false) + 6;
		g.textWithWordWrap(font, Component.translatable("screen.matriochka.info.config"), l + 16, y, W - 32, Ui.INK_SOFT, false);
		buttons.draw(g, font, mx, my);
		motion.pop(g);
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (buttons.click(event.x(), event.y())) return true;
		return super.mouseClicked(event, doubleClick);
	}

	@Override
	public void tick() {
		super.tick();
		motion.tick();
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		motion.close(() -> minecraft.setScreenAndShow(parent));
	}
}
