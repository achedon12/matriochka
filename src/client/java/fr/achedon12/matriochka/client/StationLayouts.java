package fr.achedon12.matriochka.client;

/**
 * Where each station lays out its recipes in its cabinet (panel coordinates): jars on the vat's two shelves, crucibles
 * under the foundry's heat, key tags on the jailer's two chains, plates in two arcs over the forge's anvil, runes in
 * the dark altar's two circles, mirrored rows, a honeycomb of portholes, medallions round the workshop's gear, a grid
 * of strata, banners on the loom's beam. The Matrix Workbench keeps its drawers (it has far more recipes).
 * <p>
 * Every layout holds all of its station's recipes (up to the counts below), so none of them scrolls. The sprites are
 * tile_<station> (one piece, a _ready twin when the player carries everything) over decor_<station>, 180 x 88 at
 * (12, 22). Keep the sizes in step with tools/gui_stations.py TILES.
 */
final class StationLayouts {
	private StationLayouts() {}

	static final int DECOR_X = 12, DECOR_Y = 22, DECOR_W = 180, DECOR_H = 88;
	/** The bar under the pieces that shows the recipe under the cursor, in the station's own row material. */
	static final int BAR_X = 12, BAR_Y = 112;

	static boolean has(String station) {
		return size(station) != null;
	}

	/** Size of one recipe piece, or null when the station keeps the drawers. */
	static int[] size(String station) {
		return switch (station) {
			case "spore_vat" -> new int[]{26, 38};
			case "ash_foundry" -> new int[]{30, 36};
			case "jailer_table" -> new int[]{22, 38};
			case "lightning_forge" -> new int[]{26, 26};
			case "dark_altar" -> new int[]{22, 22};
			case "inverter" -> new int[]{84, 20};
			case "abyssal_press" -> new int[]{24, 24};
			case "time_workshop" -> new int[]{24, 24};
			case "terrain_anchor" -> new int[]{56, 26};
			case "final_loom" -> new int[]{22, 58};
			default -> null;
		};
	}

	/** Pieces in a row of two-row layouts: the first row takes the extra one. */
	private static int[] row(int i, int n) {
		int first = (n + 1) / 2;
		return i < first ? new int[]{0, i, first} : new int[]{1, i - first, n - first};
	}

	private static int centred(int count, int w, int gap) {
		return 12 + (180 - (count * w + (count - 1) * gap)) / 2;
	}

	/** Top-left corner of recipe i of n, panel coordinates. */
	static int[] at(String station, int i, int n) {
		switch (station) {
			case "spore_vat": {
				int[] r = row(i, n);
				return new int[]{centred(r[2], 26, 8) + r[1] * 34, r[0] == 0 ? 26 : 68};
			}
			case "ash_foundry": {
				int[] r = row(i, n);
				return new int[]{centred(r[2], 30, 6) + r[1] * 36, r[0] == 0 ? 26 : 70};
			}
			case "jailer_table": {
				int[] r = row(i, n);
				return new int[]{centred(r[2], 22, 6) + r[1] * 28, (r[0] == 0 ? 26 : 70) + (r[1] % 2) * 3};
			}
			case "lightning_forge": {
				// two arcs over the anvil: seven plates outside, the rest inside
				int outer = Math.min(n, 7), k = i < outer ? i : i - outer, m = i < outer ? outer : n - outer;
				double from = i < outer ? 1.07 : 1.15, span = i < outer ? 0.86 : 0.7, radius = i < outer ? 70 : 42;
				double a = Math.PI * (from + span * (m == 1 ? 0.5 : k / (double) (m - 1)));
				return new int[]{102 + (int) Math.round(Math.cos(a) * radius) - 13, 106 + (int) Math.round(Math.sin(a) * radius) - 13};
			}
			case "dark_altar": {
				// eight runes on the outer circle, the rest on the inner one
				int outer = Math.min(n, 8), k = i < outer ? i : i - outer, m = i < outer ? outer : n - outer;
				double radius = i < outer ? 35 : 15;
				double a = -Math.PI / 2 + (k + (i < outer ? 0.5 : 0)) * Math.PI * 2 / m;
				return new int[]{102 + (int) Math.round(Math.cos(a) * radius) - 11, 69 + (int) Math.round(Math.sin(a) * radius) - 11};
			}
			case "inverter":
				return new int[]{14 + (i / 4) * 92, 26 + (i % 4) * 21};
			case "abyssal_press": {
				// a honeycomb: rows of five and four
				int r = i < 5 ? 0 : i < 9 ? 1 : 2, k = i < 5 ? i : i < 9 ? i - 5 : i - 9;
				int count = r == 0 ? Math.min(5, n) : r == 1 ? Math.min(4, n - 5) : n - 9;
				return new int[]{102 - (count * 30 - 6) / 2 + k * 30, 28 + r * 28};
			}
			case "time_workshop": {
				// eight on the gear's ring, a ninth at its hub
				if (i == 8) return new int[]{102 - 12, 66 - 12};
				int m = Math.min(n, 8);
				double a = -Math.PI / 2 + i * Math.PI * 2 / m;
				return new int[]{102 + (int) Math.round(Math.cos(a) * 32) - 12, 66 + (int) Math.round(Math.sin(a) * 32) - 12};
			}
			case "terrain_anchor":
				return new int[]{14 + (i % 3) * 59, 26 + (i / 3) * 28};
			case "final_loom":
				return new int[]{centred(n, 22, 3) + i * 25, 34};
			default:
				return new int[]{0, 0};
		}
	}

	/** Where the result's item sits inside a piece (from its top-left corner). */
	static int[] itemAt(String station) {
		return switch (station) {
			case "spore_vat" -> new int[]{5, 17};
			case "ash_foundry" -> new int[]{7, 7};
			case "jailer_table" -> new int[]{3, 11};
			case "inverter" -> new int[]{4, 2};
			case "terrain_anchor" -> new int[]{4, 5};
			case "final_loom" -> new int[]{3, 22};
			default -> {
				int[] s = size(station);
				yield new int[]{s[0] / 2 - 8, s[1] / 2 - 8};
			}
		};
	}
}
