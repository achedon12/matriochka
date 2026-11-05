package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.content.ReplayContent;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.replay.ReplayNet;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;

/**
 * The talents, in the Class Table's lacquered cabinet. The wooden panel holds the chosen class's tree: three branches
 * of four dolls, gilded once learnt, joined by a gold thread as you go down a branch. The red panel tells the talent
 * under the cursor (or the one picked) and learns it. The six classes wait on plates in the lower drawer, a glow
 * behind those whose gear you wear right now; the arched niches keep your souls and Shell Shards.
 */
public class TalentScreen extends Screen {
	private static final int W = 256, H = 222;
	private static final int TREE_X = 12, TREE_Y = 22, TREE_W = 130, BR_W = 43, NODE_Y = 44, NODE_STEP = 19;
	private final Ui.Buttons buttons = new Ui.Buttons();
	private final Ui.Motion motion = new Ui.Motion(300, 160);
	private int cls;
	private String picked;
	private final float[] glow = new float[24];
	private long last = Ui.now(), learntAt = -1;
	private String learntId = "";

	public TalentScreen() {
		super(Component.translatable("talents.matriochka.title"));
		// open on the class of the gear in hand, if any
		var held = net.minecraft.client.Minecraft.getInstance().player.getMainHandItem().get(GearClasses.GEAR);
		if (held != null) for (int i = 0; i < ReplayContent.CLASSES.length; i++) if (ReplayContent.CLASSES[i].equals(held.cls())) cls = i;
	}

	private int left() { return (width - W) / 2; }
	private int top() { return (height - H) / 2; }

	private String className() {
		return ReplayContent.CLASSES[cls];
	}

	private static boolean learnt(String id) {
		return MatrioClient.state.getBooleanOr("f_talent_" + id, false);
	}

	private List<ReplayContent.TalentDef> tree() {
		List<ReplayContent.TalentDef> out = new ArrayList<>();
		for (ReplayContent.TalentDef d : ReplayContent.TALENTS) if (d.cls().equals(className())) out.add(d);
		return out;
	}

	private List<String> branches() {
		List<String> out = new ArrayList<>();
		for (ReplayContent.TalentDef d : tree()) if (!out.contains(d.branch())) out.add(d.branch());
		return out;
	}

	private static ReplayContent.TalentDef def(String id) {
		for (ReplayContent.TalentDef d : ReplayContent.TALENTS) if (d.id().equals(id)) return d;
		return null;
	}

	private static ReplayContent.TalentDef previous(ReplayContent.TalentDef d) {
		for (ReplayContent.TalentDef o : ReplayContent.TALENTS) if (o.cls().equals(d.cls()) && o.branch().equals(d.branch()) && o.tier() == d.tier() - 1) return o;
		return null;
	}

	private static int highest() {
		int done = MatrioClient.state.getIntOr("done", 0), best = -1;
		for (int i = 0; i <= 10; i++) if ((done & (1 << i)) != 0) best = i;
		return best;
	}

	private int shards() {
		return fr.achedon12.matriochka.block.Stations.count(minecraft.player.getInventory(), ModContent.item("shell_shard"));
	}

	/** Why a talent cannot be learnt yet, or null when it can. */
	private String blocker(ReplayContent.TalentDef d) {
		if (learnt(d.id())) return "talents.matriochka.learnt";
		boolean creative = minecraft.player.isCreative();
		ReplayContent.TalentDef prev = previous(d);
		if (prev != null && !learnt(prev.id())) return "talents.matriochka.need_previous";
		if (!creative && highest() < d.gate()) return "talents.matriochka.need_boss";
		if (!creative && MatrioClient.state.getIntOr("souls", 0) < d.souls()) return "talents.matriochka.need_souls";
		if (!creative && shards() < d.shards()) return "talents.matriochka.need_shards";
		return null;
	}

	/** Classes whose gear the player wears or holds right now (a tool for the Prospector), as the server counts them. */
	private Set<String> active() {
		Set<String> out = new HashSet<>();
		for (EquipmentSlot slot : EquipmentSlot.values()) {
			ItemStack s = minecraft.player.getItemBySlot(slot);
			var g = s.get(GearClasses.GEAR);
			if (g != null) out.add(g.cls());
			if ((slot == EquipmentSlot.MAINHAND || slot == EquipmentSlot.OFFHAND) && GearClasses.kind(s) == GearClasses.Kind.TOOL) out.add("prospector");
		}
		return out;
	}

	@Override
	protected void init() {
		if (Ui.now() - motion.openedAt() < 100) Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_OPEN, 1.1f, 0.6f);
		rebuild();
	}

	private void rebuild() {
		buttons.clear();
		int l = left(), t = top();
		buttons.add(l + 154, t + 102, 88, 16, Component.translatable("talents.matriochka.learn"), () -> {
			if (picked == null) return;
			ClientPlayNetworking.send(new ReplayNet.LearnTalent(picked));
			learntId = picked;
			learntAt = Ui.now();
		}, () -> picked != null && blocker(def(picked)) == null);
		buttons.add(l + 172, t + 198, 34, 13, Component.translatable("talents.matriochka.reset"), () -> ClientPlayNetworking.send(new ReplayNet.LearnTalent("reset")));
	}

	@Override
	public void tick() {
		super.tick();
		motion.tick();
	}

	@Override
	public void onClose() {
		if (motion.closing()) return;
		Ui.sound(fr.achedon12.matriochka.content.Sounds.DOLL_CLOSE, 1.05f, 0.55f);
		motion.close(super::onClose);
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	// ---------------------------------------------------------------- drawing
	@Override
	public void extractBackground(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractBackground(g, mx, my, a);
		int l = left(), t = top();
		motion.push(g, l + W / 2f, t + H / 2f);
		Ui.sprite(g, "station_class_table", l, t, W, H);
		Ui.plate(g, font, title, l + W / 2, t + 1, 0, l * 7L);
		Ui.wanderingGlint(g, new int[][]{{l + 3, t + 3}, {l + W - 4, t + 3}, {l + 3, t + H - 4}, {l + W - 4, t + H - 4}}, 1500, 61);
		motion.pop(g);
	}

	@Override
	public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float a) {
		super.extractRenderState(g, mx, my, a);
		long now = Ui.now();
		float dt = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		int l = left(), t = top();
		motion.push(g, l + W / 2f, t + H / 2f);
		String hover = treeAt(mx, my);
		drawTree(g, l, t, hover, dt);
		String shown = hover != null ? hover : picked;
		detail(g, l + 152, t + 24, 92, shown);
		classes(g, l, t, mx, my);
		niches(g, l, t);
		buttons.draw(g, font, mx, my);
		motion.pop(g);
		if (hover != null) tooltip(g, hover, mx, my);
	}

	private int nodeX(int branch) {
		return left() + TREE_X + 6 + branch * BR_W + BR_W / 2 - 8;
	}

	private int nodeY(int tier) {
		return top() + NODE_Y + tier * NODE_STEP;
	}

	/** The wooden panel: three branches of four dolls, a gold thread down each branch as far as it is learnt. */
	private void drawTree(GuiGraphicsExtractor g, int l, int t, String hover, float dt) {
		Component name = Component.translatable("class.matriochka." + className());
		boolean on = active().contains(className());
		Ui.embossed(g, font, name, l + TREE_X + TREE_W / 2 - font.width(name) / 2, t + 25, on ? Ui.GOLD : Ui.MUTED);
		List<String> br = branches();
		for (int b = 0; b < br.size(); b++) {
			Component bn = Component.translatable("talent.matriochka.branch." + className() + "." + br.get(b));
			int bx = nodeX(b) + 8;
			String s = font.plainSubstrByWidth(bn.getString(), BR_W - 2);
			g.text(font, Component.literal(s), bx - font.width(s) / 2, t + 35, Ui.LIGHT, false);
		}
		int i = 0;
		for (ReplayContent.TalentDef d : tree()) {
			int b = br.indexOf(d.branch());
			int x = nodeX(b), y = nodeY(d.tier());
			boolean have = learnt(d.id());
			// the thread from the doll above
			if (d.tier() > 0) {
				boolean linked = have;
				g.fill(x + 7, y - NODE_STEP + 17, x + 9, y + 1, linked ? 0xFFEFCB72 : 0x803A2416);
				if (linked) g.fill(x + 7, y - NODE_STEP + 17, x + 8, y + 1, 0xFFFFF0B0);
			}
			boolean ready = !have && blocker(d) == null;
			glow[i] = Ui.approach(glow[i], d.id().equals(hover) || d.id().equals(picked) ? 1 : ready ? 0.45f : 0, 10, dt);
			if (glow[i] > 0.02f) Ui.sprite(g, "glow", x - 4, y - 4, 24, 24, Ui.white(glow[i] * (ready ? 0.9f : 0.6f)));
			Ui.sprite(g, "slot", x - 1, y - 1, 18, 18);
			Ui.sprite(g, have ? "doll_small_full" : "doll_small_empty", x + 4, y + 2, 8, 11, have ? 0xFFFFFFFF : ready ? 0xFFFFFFFF : 0x90FFFFFF);
			if (d.id().equals(picked)) g.outline(x - 2, y - 2, 20, 20, 0xFFF4D27A);
			if (d.id().equals(learntId) && learntAt >= 0 && have) {
				float since = Ui.since(learntAt, 900);
				if (since < 1) Ui.glint(g, x + 8, y + 8, since, 16);
			}
			// tier marks: one notch per tier on the slot's foot
			for (int k = 0; k <= d.tier(); k++) g.fill(x + 2 + k * 3, y + 15, x + 4 + k * 3, y + 16, have ? 0xFFEFCB72 : 0xFF6E4E36);
			i++;
		}
	}

	private String treeAt(double mx, double my) {
		List<String> br = branches();
		for (ReplayContent.TalentDef d : tree()) {
			int x = nodeX(br.indexOf(d.branch())), y = nodeY(d.tier());
			if (mx >= x - 2 && mx < x + 18 && my >= y - 2 && my < y + 18) return d.id();
		}
		return null;
	}

	/** The red panel: the talent's name, what it does, what it costs and whether it can be learnt. */
	private void detail(GuiGraphicsExtractor g, int x, int y, int w, String id) {
		if (id == null) {
			g.textWithWordWrap(font, Component.translatable("talents.matriochka.help", Component.translatable("class.matriochka." + className())), x, y, w, Ui.MUTED, false);
			return;
		}
		ReplayContent.TalentDef d = def(id);
		int yy = y + g.textWithWordWrap(font, Component.translatable("talent.matriochka." + id), x, y, w, Ui.GOLD, false);
		g.fill(x, yy + 1, x + Math.min(w, 50), yy + 2, 0xFFB0782A);
		yy += 5;
		yy += g.textWithWordWrap(font, Component.translatable("talent.matriochka." + id + ".desc"), x, yy, w, Ui.LIGHT, false) + 3;
		Component cost = d.shards() > 0 ? Component.translatable("talents.matriochka.cost_shards", d.souls(), d.shards()) : Component.translatable("talents.matriochka.cost", d.souls());
		yy += g.textWithWordWrap(font, cost, x, yy, w, Ui.MUTED, false) + 2;
		String block = blocker(d);
		if (block != null) {
			Component why = block.equals("talents.matriochka.need_boss") ? Component.translatable(block, bossName(d.gate())) : Component.translatable(block);
			g.textWithWordWrap(font, why, x, yy, w, block.equals("talents.matriochka.learnt") ? Ui.OK : Ui.WARN, false);
		}
	}

	private static Component bossName(int world) {
		return Component.translatable("entity.matriochka." + fr.achedon12.matriochka.entity.MatrioBoss.byWorld(world).id());
	}

	private void tooltip(GuiGraphicsExtractor g, String id, int mx, int my) {
		ReplayContent.TalentDef d = def(id);
		List<Component> lines = new ArrayList<>();
		lines.add(Component.translatable("talent.matriochka." + id).withStyle(ChatFormatting.GOLD));
		lines.add(Component.translatable("talent.matriochka." + id + ".desc").withStyle(ChatFormatting.WHITE));
		lines.add(Component.translatable("talents.matriochka.tier", d.tier() + 1, Component.translatable("talent.matriochka.branch." + d.cls() + "." + d.branch())).withStyle(ChatFormatting.GRAY));
		lines.add((d.shards() > 0 ? Component.translatable("talents.matriochka.cost_shards", d.souls(), d.shards()) : Component.translatable("talents.matriochka.cost", d.souls())).withStyle(ChatFormatting.DARK_AQUA));
		if (d.gate() > 0) lines.add(Component.translatable("talents.matriochka.gate", bossName(d.gate())).withStyle(ChatFormatting.DARK_GRAY));
		lines.add(Component.translatable("talents.matriochka.active_rule", Component.translatable("class.matriochka." + d.cls())).withStyle(ChatFormatting.DARK_PURPLE));
		List<net.minecraft.util.FormattedCharSequence> seq = new ArrayList<>();
		for (Component c : lines) seq.addAll(font.split(c, 180));
		g.setTooltipForNextFrame(font, seq, mx, my);
	}

	/** The lower drawer: one plate per class, glowing behind the classes your gear wakes. */
	private void classes(GuiGraphicsExtractor g, int l, int t, int mx, int my) {
		Set<String> on = active();
		for (int i = 0; i < ReplayContent.CLASSES.length; i++) {
			String c = ReplayContent.CLASSES[i];
			int px = l + 50 + (i % 3) * 52, py = t + 142 + (i / 3) * 24;
			boolean sel = i == cls, over = mx >= px && mx < px + 50 && my >= py && my < py + 20;
			if (on.contains(c)) Ui.sprite(g, "glow", px + 5, py - 10, 40, 40, Ui.white(0.35f + 0.1f * (float) Math.sin(Ui.now() / 500.0 + i)));
			Ui.sprite(g, sel ? "btn_pressed" : over ? "btn_hover" : "btn", px, py, 50, 20);
			Component name = Component.translatable("class.matriochka." + c);
			String s = font.plainSubstrByWidth(name.getString(), 46);
			Ui.embossed(g, font, Component.literal(s), px + 25 - font.width(s) / 2, py + 3, sel ? 0xFFFFF4D8 : Ui.LIGHT);
			int n = 0;
			for (ReplayContent.TalentDef d : ReplayContent.TALENTS) if (d.cls().equals(c) && learnt(d.id())) n++;
			Component count = Component.literal(n + "/12");
			g.text(font, count, px + 25 - font.width(count) / 2, py + 12, n > 0 ? Ui.GOLD : Ui.MUTED, false);
		}
		Component rule = Component.translatable("talents.matriochka.active_rule", Component.translatable("class.matriochka." + className()));
		String s = font.plainSubstrByWidth(rule.getString(), 118);
		g.text(font, Component.literal(s), l + 50, t + 200, Ui.MUTED, false);
	}

	/** The niches: souls by a lantern on the left, Shell Shards on the right. */
	private void niches(GuiGraphicsExtractor g, int l, int t) {
		Ui.sprite(g, "lantern", l + 20, t + 156, 9, 13);
		JournalScreen.lanternFlame(g, l + 20, t + 156, 1f);
		Component souls = Component.literal(Integer.toString(MatrioClient.state.getIntOr("souls", 0)));
		Ui.embossed(g, font, souls, l + 25 - font.width(souls) / 2, t + 174, Ui.GOLD);
		ItemStack shard = new ItemStack(ModContent.item("shell_shard"));
		g.item(shard, l + 222, t + 154);
		Component n = Component.literal(Integer.toString(shards()));
		Ui.embossed(g, font, n, l + 230 - font.width(n) / 2, t + 174, Ui.GOLD);
	}

	@Override
	public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
		if (motion.closing()) return true;
		if (buttons.click(event.x(), event.y())) return true;
		String at = treeAt(event.x(), event.y());
		if (at != null) {
			picked = at;
			Ui.click();
			return true;
		}
		int l = left(), t = top();
		for (int i = 0; i < ReplayContent.CLASSES.length; i++) {
			int px = l + 50 + (i % 3) * 52, py = t + 142 + (i / 3) * 24;
			if (event.x() >= px && event.x() < px + 50 && event.y() >= py && event.y() < py + 20) {
				if (cls != i) {
					cls = i;
					picked = null;
					Ui.pageTurn();
				}
				return true;
			}
		}
		return super.mouseClicked(event, doubleClick);
	}
}
