package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import java.text.Normalizer;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/**
 * What the client knows of the Artisan's Journal pages (found bits synced in the player state "pages_N"), the
 * Artisan's cipher of the coded pages, and the endings the player has reached.
 */
final class JournalPages {
	/** The page of every world written in the Artisan's cipher (the fourth, content.py JOURNAL_CODED). */
	static final int CODED = fr.achedon12.matriochka.content.Content.JOURNAL_CODED;

	private JournalPages() {}

	/** Bits of the pages found in a world (bit i = page i + 1). */
	static int found(int world) {
		return MatrioClient.state.getIntOr("pages_" + world, 0);
	}

	static int total() {
		int n = 0;
		for (int w = 1; w <= 10; w++) n += Integer.bitCount(found(w));
		return n;
	}

	static boolean coded(int index) {
		return index == CODED;
	}

	/** A page can be read when it is plain, or when its world's boss fell to the group, or when its core is carried. */
	static boolean readable(int world, int index) {
		if (!coded(index)) return true;
		if ((MatrioClient.state.getIntOr("done", 0) & (1 << world)) != 0) return true;
		return carries(MatrioBoss.byWorld(world).core());
	}

	/** Whether the local player carries an item of the mod. */
	static boolean carries(String id) {
		var player = Minecraft.getInstance().player;
		var item = ModContent.itemOrNull(id);
		if (player == null || item == null) return false;
		var inv = player.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (s.is(item)) return true;
		}
		return false;
	}

	/** The first page found, as {world, index}, or null. */
	static int[] first() {
		for (int w = 1; w <= 10; w++)
			for (int i = 0; i < 5; i++) if ((found(w) & (1 << i)) != 0) return new int[]{w, i};
		return null;
	}

	/** The next (dir 1) or previous (dir -1) page found after {world, index}, or null. */
	static int[] step(int world, int index, int dir) {
		int at = (world - 1) * 5 + index;
		for (int k = at + dir; k >= 0 && k < 50; k += dir) {
			int w = k / 5 + 1, i = k % 5;
			if ((found(w) & (1 << i)) != 0) return new int[]{w, i};
		}
		return null;
	}

	/**
	 * The Artisan's cipher: letters are mirrored through the alphabet and shifted by the world number (a reversed
	 * Caesar), accents dropped, everything else kept. Readable by hand for the patient, decoded by the Journal once the
	 * world's core is carried.
	 */
	static String cipher(String plain, int world) {
		String s = Normalizer.normalize(plain, Normalizer.Form.NFD).replaceAll("\\p{M}", "");
		StringBuilder b = new StringBuilder(s.length());
		for (char c : s.toCharArray()) {
			if (c >= 'a' && c <= 'z') b.append((char) ('a' + Math.floorMod(25 - (c - 'a') + world, 26)));
			else if (c >= 'A' && c <= 'Z') b.append((char) ('A' + Math.floorMod(25 - (c - 'A') + world, 26)));
			else b.append(c);
		}
		return b.toString();
	}

	static boolean ending(String kind) {
		return MatrioClient.state.getBooleanOr("f_end_" + kind, false);
	}

	static int endingsSeen() {
		int n = 0;
		for (String k : new String[]{"seal", "absorb", "tools"}) if (ending(k)) n++;
		return n;
	}

	/** "Sealed, Set Down the Tools"... or null when no ending was reached. */
	static Component endingNames() {
		Component out = null;
		for (String k : new String[]{"seal", "absorb", "tools"}) {
			if (!ending(k)) continue;
			Component name = Component.translatable("ending.matriochka." + k);
			out = out == null ? name.copy() : out.copy().append(", ").append(name);
		}
		return out;
	}
}
