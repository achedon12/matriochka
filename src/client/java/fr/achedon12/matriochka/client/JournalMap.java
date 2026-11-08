package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.net.Net;
import fr.achedon12.matriochka.world.Atlas;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;

/**
 * The Journal's map of a world, drawn on its parchment like a surveyor's sheet: the ground walked through as ink
 * washes in the world's colour with a darker line where it meets the unknown, the rest left blank, the structures
 * found as small pixel icons per role, and the player as a little doll. The server keeps the data (world/Atlas) and
 * sends one world at a time when the Journal asks for it.
 */
public final class JournalMap {
	private JournalMap() {}

	/** A structure found: its id, role and the block it stands round. */
	public record Found(String id, String role, int x, int z) {}

	/** One world's map as the server sent it, with its cells unpacked. */
	public record Data(int world, Set<Long> cells, List<Found> found, int minX, int minZ, int maxX, int maxZ) {}

	private static final Map<Integer, Data> CACHE = new HashMap<>();
	public static final String[] ROLES = {"utility", "combat", "exploration", "story", "secret", "wonder"};

	public static void receive(CompoundTag t) {
		int world = t.getIntOr("world", -1);
		if (world < 0) return;
		int ox = t.getIntOr("ox", 0), oz = t.getIntOr("oz", 0);
		Set<Long> cells = new HashSet<>();
		int minX = Integer.MAX_VALUE, minZ = Integer.MAX_VALUE, maxX = Integer.MIN_VALUE, maxZ = Integer.MIN_VALUE;
		for (int c : t.getIntArray("cells").orElse(new int[0])) {
			int cx = ox + (c >> 16), cz = oz + (short) c;
			cells.add(key(cx, cz));
			minX = Math.min(minX, cx);
			minZ = Math.min(minZ, cz);
			maxX = Math.max(maxX, cx);
			maxZ = Math.max(maxZ, cz);
		}
		List<Found> found = new ArrayList<>();
		for (Tag e : t.getListOrEmpty("found")) {
			if (!(e instanceof CompoundTag c)) continue;
			String id = c.getStringOr("id", "");
			found.add(new Found(id, role(id), c.getIntOr("x", 0), c.getIntOr("z", 0)));
		}
		CACHE.put(world, new Data(world, cells, found, minX, minZ, maxX, maxZ));
	}

	/** Asks the server for a world's map (it answers at most once a second). */
	public static void request(int world) {
		if (ClientPlayNetworking.canSend(Net.MapRequestPayload.TYPE)) ClientPlayNetworking.send(new Net.MapRequestPayload(world));
	}

	public static Data of(int world) {
		return CACHE.get(world);
	}

	/** Forgets every map (on leaving a server). */
	public static void clear() {
		CACHE.clear();
	}

	private static long key(int cx, int cz) {
		return (long) cx << 32 | cz & 0xFFFFFFFFL;
	}

	/** The role of a structure: from the structure table, the Surface's Sanctuary being the story's first place. */
	public static String role(String id) {
		for (Defs.StructureDef s : Content.STRUCTURES) if (s.id().equals(id)) return s.role();
		return "story";
	}

	/** The world the player stands in as the map counts it, or -1. */
	public static int here() {
		Minecraft mc = Minecraft.getInstance();
		return mc.level == null ? -1 : Atlas.mapped(mc.level);
	}

	// ---------------------------------------------------------------- pixel art
	// '#' ink outline, 'o' the role's colour, 'g' gold, 'l' light; 7 x 7 each
	private static final Map<String, String[]> ICONS = Map.of(
		"utility", new String[]{
			"...#...",
			"..#o#..",
			".#ooo#.",
			"#######",
			".#lol#.",
			".#o#o#.",
			".#####."},
		"combat", new String[]{
			"#.....#",
			"l#...#l",
			".l#.#l.",
			"..l#l..",
			".o#.#o.",
			"o#...#o",
			"#.....#"},
		"exploration", new String[]{
			"...#...",
			"..#l#..",
			"..#o#..",
			"#lo#oo#",
			"..#o#..",
			"..#o#..",
			"...#..."},
		"story", new String[]{
			".......",
			".##.##.",
			"#ll#oo#",
			"#ll#oo#",
			"#ll#oo#",
			"###.###",
			"...#..."},
		"secret", new String[]{
			"..###..",
			".#...#.",
			".#...#.",
			"#######",
			"#oo#oo#",
			"#oo#oo#",
			"#######"},
		"wonder", new String[]{
			"g..g..g",
			"#..#..#",
			"##.#.##",
			"#o#g#o#",
			"#ooooo#",
			"#######",
			"......."});
	private static final String[] DOLL = {
		".###.",
		"#ooo#",
		"#olo#",
		".#o#.",
		"#ooo#",
		"#ogo#",
		"#ooo#",
		".###."};
	private static final int HALO = 0xFFF4E4C0, ICON_INK = 0xFF2A1A10;

	public static int roleColor(String role) {
		return switch (role) {
			case "utility" -> 0xFF3F6E2C;
			case "combat" -> 0xFFB3261E;
			case "exploration" -> 0xFF2E5E8A;
			case "story" -> 0xFF7A4A8A;
			case "secret" -> 0xFF5A4A3A;
			case "wonder" -> 0xFFE0A830;
			default -> Ui.INK_SOFT;
		};
	}

	/** A pixel bitmap, its top-left at (x, y), with a one-pixel parchment halo so it reads over the washes. */
	private static void bitmap(GuiGraphicsExtractor g, String[] rows, int x, int y, int fill) {
		for (int r = 0; r < rows.length; r++)
			for (int c = 0; c < rows[r].length(); c++)
				if (rows[r].charAt(c) != '.') g.fill(x + c - 1, y + r - 1, x + c + 2, y + r + 2, HALO);
		for (int r = 0; r < rows.length; r++) {
			for (int c = 0; c < rows[r].length(); c++) {
				int col = switch (rows[r].charAt(c)) {
					case '#' -> ICON_INK;
					case 'o' -> fill;
					case 'g' -> Ui.GOLD;
					case 'l' -> 0xFFFFF4D8;
					default -> 0;
				};
				if (col != 0) g.fill(x + c, y + r, x + c + 1, y + r + 1, col);
			}
		}
	}

	/** A role's icon centred on (cx, cy). */
	public static void icon(GuiGraphicsExtractor g, String role, int cx, int cy) {
		String[] rows = ICONS.getOrDefault(role, ICONS.get("story"));
		bitmap(g, rows, cx - 3, cy - 3, roleColor(role));
	}

	private static int mix(int a, int b, float t) {
		int r = Math.round((a >> 16 & 255) * (1 - t) + (b >> 16 & 255) * t);
		int gg = Math.round((a >> 8 & 255) * (1 - t) + (b >> 8 & 255) * t);
		int bl = Math.round((a & 255) * (1 - t) + (b & 255) * t);
		return 0xFF000000 | r << 16 | gg << 8 | bl;
	}

	private static int hash(int x, int z) {
		int h = x * 0x45D9F3B ^ z * 0x119DE1F3;
		h ^= h >>> 15;
		h *= 0x2C1B3C6D;
		return h ^ h >>> 13;
	}

	// ---------------------------------------------------------------- the sheet
	/**
	 * The map in the box (x, y, w, h). Returns false when nothing was drawn (no ground walked yet), so the page can
	 * say so instead.
	 */
	public static boolean draw(GuiGraphicsExtractor g, Font font, int world, int x, int y, int w, int h, int mx, int my) {
		Data d = of(world);
		Minecraft mc = Minecraft.getInstance();
		boolean here = here() == world && mc.player != null;
		int pcx = here ? (int) Math.floor(mc.player.getX()) >> Atlas.CELL_SHIFT : 0, pcz = here ? (int) Math.floor(mc.player.getZ()) >> Atlas.CELL_SHIFT : 0;
		boolean any = d != null && !d.cells().isEmpty();
		if (!any && !here) return false;
		// the area to show: what was walked, what was found, and the player
		int minX = any ? d.minX() : pcx, minZ = any ? d.minZ() : pcz, maxX = any ? d.maxX() : pcx, maxZ = any ? d.maxZ() : pcz;
		if (d != null) for (Found f : d.found()) {
			minX = Math.min(minX, f.x() >> Atlas.CELL_SHIFT);
			minZ = Math.min(minZ, f.z() >> Atlas.CELL_SHIFT);
			maxX = Math.max(maxX, f.x() >> Atlas.CELL_SHIFT);
			maxZ = Math.max(maxZ, f.z() >> Atlas.CELL_SHIFT);
		}
		if (here) {
			minX = Math.min(minX, pcx);
			minZ = Math.min(minZ, pcz);
			maxX = Math.max(maxX, pcx);
			maxZ = Math.max(maxZ, pcz);
		}
		int side = Math.min(w, h);
		int span = Math.max(maxX - minX, maxZ - minZ) + 3;
		// whole pixels per cell, from 2 (a parcel and more) to 8 (a first walk)
		int s = Math.max(2, Math.min(8, side / Math.max(1, span)));
		int n = side / s;
		// centred on what is known; too wide to fit, centred on the player (or the middle of the known ground)
		int ccx = (minX + maxX) / 2, ccz = (minZ + maxZ) / 2;
		if (span > n && here) {
			ccx = pcx;
			ccz = pcz;
		}
		int vx = ccx - n / 2, vz = ccz - n / 2;
		int bx = x + (w - n * s) / 2, by = y + (h - n * s) / 2, bw = n * s;

		// the neatline: a double ink rule with gilded corners
		g.fill(bx - 3, by - 3, bx + bw + 3, by - 2, Ui.INK_SOFT);
		g.fill(bx - 3, by + bw + 2, bx + bw + 3, by + bw + 3, Ui.INK_SOFT);
		g.fill(bx - 3, by - 2, bx - 2, by + bw + 2, Ui.INK_SOFT);
		g.fill(bx + bw + 2, by - 2, bx + bw + 3, by + bw + 2, Ui.INK_SOFT);
		g.fill(bx - 1, by - 1, bx + bw + 1, by, 0x806E4E36);
		g.fill(bx - 1, by + bw, bx + bw + 1, by + bw + 1, 0x806E4E36);
		g.fill(bx - 1, by, bx, by + bw, 0x806E4E36);
		g.fill(bx + bw, by, bx + bw + 1, by + bw, 0x806E4E36);
		for (int[] c : new int[][]{{bx - 3, by - 3}, {bx + bw + 1, by - 3}, {bx - 3, by + bw + 1}, {bx + bw + 1, by + bw + 1}}) g.fill(c[0], c[1], c[0] + 2, c[1] + 2, Ui.GOLD_DARK);
		// surveyor's dots every four cells, faint, on the blank paper
		for (int i = 0; i <= n; i++) {
			if (Math.floorMod(vx + i, 4) != 0) continue;
			for (int j = 0; j <= n; j++) if (Math.floorMod(vz + j, 4) == 0) g.fill(bx + i * s, by + j * s, bx + i * s + 1, by + j * s + 1, 0x283A2416);
		}

		int col = Ui.worldColor(world);
		int light = mix(col, 0xFFF6E8CC, 0.25f), deep = mix(col, Ui.INK, 0.45f), edge = mix(col, Ui.INK, 0.6f);
		if (d != null) {
			for (int i = 0; i < n; i++) {
				for (int j = 0; j < n; j++) {
					int cx = vx + i, cz = vz + j;
					if (!d.cells().contains(key(cx, cz))) continue;
					int px = bx + i * s, py = by + j * s;
					int hsh = hash(cx, cz);
					// two strengths of wash, as a brush laid twice in places
					g.fill(px, py, px + s, py + s, Ui.alpha((hsh & 3) == 0 ? deep : light, (hsh & 3) == 0 ? 0.42f : 0.5f));
					if (s >= 4) {
						// a few grains of pigment in the wash
						for (int k = 0; k < s / 2; k++) {
							int gx = (hsh >>> (k * 4)) & (s - 1), gz = (hsh >>> (k * 4 + 2)) & (s - 1);
							g.fill(px + gx % s, py + gz % s, px + gx % s + 1, py + gz % s + 1, Ui.alpha(deep, 0.35f));
						}
					}
					// the line where the walked ground meets the unknown
					int ea = Ui.alpha(edge, 0.85f);
					if (!d.cells().contains(key(cx, cz - 1))) g.fill(px, py, px + s, py + 1, ea);
					if (!d.cells().contains(key(cx, cz + 1))) g.fill(px, py + s - 1, px + s, py + s, ea);
					if (!d.cells().contains(key(cx - 1, cz))) g.fill(px, py, px + 1, py + s, ea);
					if (!d.cells().contains(key(cx + 1, cz))) g.fill(px + s - 1, py, px + s, py + s, ea);
				}
			}
		}
		// the north mark, top right
		int nx = bx + bw - 7, ny = by + 2;
		g.fill(nx + 2, ny, nx + 3, ny + 1, Ui.RED_INK);
		g.fill(nx + 1, ny + 1, nx + 4, ny + 2, Ui.RED_INK);
		g.fill(nx + 2, ny + 2, nx + 3, ny + 5, Ui.INK_SOFT);
		g.text(font, "N", nx - 6, ny, Ui.alpha(Ui.INK_SOFT, 0.9f), false);

		Component tip = null;
		if (d != null) {
			for (Found f : d.found()) {
				int ix = bx + Math.round((f.x() / 64f - vx) * s), iz = by + Math.round((f.z() / 64f - vz) * s);
				if (ix < bx + 3 || iz < by + 3 || ix > bx + bw - 4 || iz > by + bw - 4) continue;
				icon(g, f.role(), ix, iz);
				if (mx >= ix - 4 && mx <= ix + 4 && my >= iz - 4 && my <= iz + 4)
					tip = Component.translatable("structure.matriochka." + f.id()).append("\n")
						.append(Component.translatable("journal.matriochka.map.role." + f.role()).withStyle(net.minecraft.ChatFormatting.GRAY));
			}
		}
		if (here) {
			int dx = bx + Math.round(((float) mc.player.getX() / 64f - vx) * s), dz = by + Math.round(((float) mc.player.getZ() / 64f - vz) * s);
			dx = Math.max(bx + 3, Math.min(bx + bw - 3, dx));
			dz = Math.max(by + 4, Math.min(by + bw - 4, dz));
			// a soft gold ring that breathes, so the eye finds the doll
			if ((Ui.now() / 600) % 2 == 0) {
				g.fill(dx - 4, dz - 6, dx + 5, dz - 5, Ui.alpha(Ui.GOLD, 0.7f));
				g.fill(dx - 4, dz + 5, dx + 5, dz + 6, Ui.alpha(Ui.GOLD, 0.7f));
				g.fill(dx - 5, dz - 5, dx - 4, dz + 5, Ui.alpha(Ui.GOLD, 0.7f));
				g.fill(dx + 5, dz - 5, dx + 6, dz + 5, Ui.alpha(Ui.GOLD, 0.7f));
			}
			bitmap(g, DOLL, dx - 2, dz - 4, Ui.RED);
			if (mx >= dx - 4 && mx <= dx + 4 && my >= dz - 5 && my <= dz + 5) tip = Component.translatable("journal.matriochka.map.you");
		}
		if (tip != null) g.setTooltipForNextFrame(font, font.split(tip, 170), mx, my);
		return true;
	}

	/** The left page beside a map: the places found, role by role, and how much ground is inked. */
	public static void legend(GuiGraphicsExtractor g, Font font, int world, int x, int y, int w) {
		Data d = of(world);
		Component head = Component.translatable("journal.matriochka.map.legend");
		g.text(font, head, x + w / 2 - font.width(head) / 2, y, Ui.INK, false);
		int yy = y + 14;
		for (String role : ROLES) {
			int total = 0, have = 0;
			if (world == 0) total = role.equals("story") ? 1 : 0;
			else for (Defs.StructureDef s : Content.STRUCTURES) if (s.world() == world && s.role().equals(role)) total++;
			if (total == 0) continue;
			if (d != null) {
				Set<String> kinds = new HashSet<>();
				for (Found f : d.found()) if (f.role().equals(role)) kinds.add(f.id());
				have = Math.min(total, kinds.size());
			}
			icon(g, role, x + 6, yy + 3);
			g.text(font, Component.translatable("journal.matriochka.map.role." + role), x + 15, yy, have > 0 ? Ui.INK : 0xFF9A8A6E, false);
			String count = have + "/" + total;
			g.text(font, count, x + w - font.width(count), yy, have >= total ? Ui.GREEN : Ui.RED_INK, false);
			yy += 14;
		}
		yy += 4;
		g.fill(x + w / 2 - 30, yy, x + w / 2 + 30, yy + 1, 0xFFB0782A);
		yy += 7;
		Component inked = Component.translatable("journal.matriochka.map.explored", d == null ? 0 : d.cells().size());
		g.text(font, inked, x + w / 2 - font.width(inked) / 2, yy, Ui.INK_SOFT, false);
		if (here() != world) {
			yy += 14;
			Ui.wrap(g, font, Component.translatable("journal.matriochka.map.elsewhere"), x + 2, yy, w - 4, 0xFF9A8A6E);
		}
	}
}
