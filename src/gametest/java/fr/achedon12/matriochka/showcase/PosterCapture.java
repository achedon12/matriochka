package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.screenshot.TestScreenshotOptions;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Locale;

/**
 * The key art (media/poster, PLAN.md): ./gradlew runClientGameTest -Pposter [-Ppreview=1] [-Pshots=poster,square,yt,wide].
 *
 * Builds, high in the sky above the spawn, a staged scene and photographs it from one camera per format:
 * - the hero, a mannequin in the full Matriarch Armour leaping in mid-air in the foreground, the Matriochkite Ingot
 *   raised (its limbs posed by PosterPose through mixin.HeroPoseMixin, as a mannequin only has whole-body poses);
 * - behind it a giant matryoshka: its lower half a bowl with smaller nested shells rising inside, its upper half thrown
 *   open on a hinge and leaning to the side, face to the camera;
 * - a spiral of ten floating islands, one per world (its top, stone and glow blocks, ringed in lacquer like a doll
 *   half), from World 1, large and near at the lower right, under the doll and up the left side to World 10, small
 *   and far: laid out on the poster camera's frame and sent back into the world through it (project);
 * - three bosses in the air round the hero, held in the windup of an attack (MatrioBoss.rehearse, then no AI);
 * - a sea of block clouds far below and a few block clouds in the sky for depth.
 * Noon light, vanilla clouds off: media/poster/compose.py replaces the sky (found as the smooth region joined to the
 * top edge, or the saturated noon blue) with a painted golden-hour sky, grades the frame and adds the title.
 *
 * Local coordinates: a is the depth away from the camera (the cameras look toward -X, west), s is to the right
 * (-Z), y is absolute; the doll stands at a = 0, s = 0 on y = Y0. Shots: poster_<format>.png (poster_<format>_pre.png,
 * 1280 wide, with -Ppreview=1). Minecraft 26.1 to 26.3 (only vanilla ids and the version-stable API are used).
 */
final class PosterCapture {
	private PosterCapture() {}

	private static final Logger LOG = LoggerFactory.getLogger("matriochka");
	static final int X0 = 0, Z0 = 0, Y0 = 200;
	/** The doll's lathe profile (tools/cradle_geo.py PROFILE, a height of 16) and its scale to blocks. */
	private static final double[][] PROFILE = {{0, 3.6}, {0.8, 4.9}, {2.2, 5.6}, {4.4, 5.85}, {7.4, 5.6}, {8.4, 5.1}, {9.4, 4.4},
		{10.2, 4.05}, {12.2, 4.0}, {14.2, 3.55}, {15.2, 2.7}, {15.8, 1.4}, {16, 0.2}};
	private static final double K = 2.75, WAIST = 7.4 * K, TOP = 16 * K;
	/** The lid's hinge (local s, y) and its opening angle. */
	private static final double HINGE_S = r(WAIST) + 0.5, HINGE_Y = Y0 + WAIST, LID_ANGLE = Math.toRadians(84);
	/** The hero's feet (local a, y, s). */
	static final double HERO_A = -62, HERO_Y = Y0 + 8, HERO_S = 0;

	/** Cameras: eye (a, y, s), target (a, y, s), size, FOV. */
	private record Cam(String name, double a, double y, double s, double ta, double ty, double ts, int w, int h, int fov) {}

	private static final Cam[] CAMS = {
		new Cam("poster", HERO_A - 5.2, HERO_Y + 1.0, -0.5, 0, Y0 + 14, -0.5, 3840, 2160, 60),
		new Cam("square", HERO_A - 5.6, HERO_Y + 0.9, -0.5, 0, Y0 + 17, -0.5, 2048, 2048, 74),
		new Cam("yt", HERO_A - 6.2, HERO_Y + 1.0, -0.5, 0, Y0 + 13, -20, 2560, 1440, 60),
		new Cam("wide", HERO_A - 7.5, HERO_Y + 1.0, -0.5, 0, Y0 + 12, -24, 3840, 960, 36),
	};
	/** The player's eye stands this far above the position a teleport gives. */
	private static final double EYE = 1.62;

	static double wx(double a) { return X0 - a; }

	static double wz(double s) { return Z0 - s; }

	static BlockPos at(double a, double y, double s) {
		return BlockPos.containing(wx(a), y, wz(s));
	}

	/** Radius of the doll at a height above its foot, in blocks. */
	static double r(double h) {
		double u = h / K;
		if (u <= 0) return PROFILE[0][1] * K;
		for (int i = 1; i < PROFILE.length; i++) {
			if (u <= PROFILE[i][0]) {
				double t = (u - PROFILE[i - 1][0]) / (PROFILE[i][0] - PROFILE[i - 1][0]);
				return (PROFILE[i - 1][1] + (PROFILE[i][1] - PROFILE[i - 1][1]) * t) * K;
			}
		}
		return 0;
	}

	private static BlockState b(String id) {
		return ModContent.block(id).defaultBlockState();
	}

	private static final java.util.Map<String, BlockState> VANILLA = new java.util.HashMap<>();

	/** A vanilla block by its id: the coloured blocks are not constants of Blocks on every version. */
	private static BlockState v(String id) {
		return VANILLA.computeIfAbsent(id, k -> {
			for (var bl : net.minecraft.core.registries.BuiltInRegistries.BLOCK) {
				var key = net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(bl);
				if (key != null && key.getNamespace().equals("minecraft") && key.getPath().equals(k)) return bl.defaultBlockState();
			}
			throw new IllegalArgumentException("no block " + k);
		});
	}

	private static void set(ServerLevel lvl, BlockPos p, BlockState st) {
		lvl.setBlock(p, st, 2 | 16);
	}

	private static double hash(int x, int y, int z) {
		long h = x * 374761393L + y * 668265263L + z * 2147483647L;
		h = (h ^ (h >>> 13)) * 1274126177L;
		return ((h ^ (h >>> 16)) & 0xFFFFFF) / (double) 0xFFFFFF;
	}

	// ---------------------------------------------------------------- the doll

	/** The pattern on the doll's outer skin, from the arc position u (blocks, 0 facing the camera) and height v. */
	private static BlockState skin(double u, double v, boolean lid) {
		// lacquer_block mipmaps to brown at a distance: the body is red concrete, the lacquer blocks make bands
		BlockState lac = v("red_concrete"), gold = Blocks.GOLD_BLOCK.defaultBlockState(), band = b("lacquer_block");
		double rim = lid ? v - WAIST : WAIST - v;
		if (rim >= 0 && rim < 2) return gold;
		if (rim >= 2 && rim < 3.5) return band;
		if (!lid && v >= 2 && v < 3.5) return band;
		if (!lid && v < 2) return gold;
		if (!lid) {
			// the belly: a black oval framed in gold holding a glowing block, like the mod's icon
			double e = Math.pow(u / 5.2, 2) + Math.pow((v - 10) / 4.6, 2);
			if (e < 0.22) return b("matriochkite_block");
			if (e < 1) return v("black_concrete");
			if (e < 1.32) return gold;
			// khokhloma flowers on the sides: black discs, red petals, a gold heart, green leaves
			for (double fu : new double[]{-16, 16}) {
				double d = Math.hypot(u - fu, (v - 11) * 1.1);
				if (d < 1.2) return gold;
				if (d < 3.2) return v("red_concrete");
				if (d < 4.4) return v("black_concrete");
				if (d < 5.4 && Math.abs(v - 11) < 1.5) return v("green_concrete");
			}
			// a ring of gold leaves round the belly
			double ring = Math.pow(u / 7.0, 2) + Math.pow((v - 10) / 6.3, 2);
			if (ring > 0.92 && ring < 1.08 && ((int) Math.floor(Math.atan2(v - 10, u) * 6 / Math.PI + 12) % 2 == 0)) return gold;
		}
		return lac;
	}

	/** The face on the lid's head (local coordinates of the lid before it opens: x to the right, y up from Y0). */
	private static BlockState face(double x, double v) {
		double fy = 12.0 * K, ex = x / 6.8, ey = (v - fy) / 6.2;
		double e = ex * ex + ey * ey;
		if (e < 1) {
			if (ey > 0.25 - 0.55 * ex * ex && ey > -0.1) return v("black_concrete");
			if (Math.abs(Math.abs(x) - 2.6) < 1.0 && Math.abs(v - (fy - 0.6)) < 1.0) return v("black_concrete");
			if (Math.abs(Math.abs(x) - 4.3) < 1.0 && Math.abs(v - (fy - 3.0)) < 0.7) return v("pink_concrete");
			if (Math.abs(x) < 0.9 && Math.abs(v - (fy - 4.3)) < 0.6) return v("red_concrete");
			return v("white_terracotta");
		}
		if (e < 1.35) return Blocks.GOLD_BLOCK.defaultBlockState();
		return null;
	}

	/** Lower half: a 2-block shell from the foot to the waist, its rim gold, nested shells rising inside it. */
	private static void dollLower(ServerLevel lvl) {
		BlockState inner = b("painted_wood");
		int R = (int) Math.ceil(r(4.4 * K)) + 1;
		for (int y = 0; y < (int) WAIST; y++) {
			double rr = r(y + 0.5);
			for (int ia = -R; ia <= R; ia++) for (int is = -R; is <= R; is++) {
				double d = Math.hypot(ia + 0.5, is + 0.5);
				if (d > rr) continue;
				BlockPos p = at(ia, Y0 + y, is);
				if (y == 0) { set(lvl, p, inner); continue; }
				if (d > rr - 1.1) {
					double u = Math.atan2(is + 0.5, -(ia + 0.5)) * rr;
					set(lvl, p, skin(u, y + 0.5, false));
				} else if (d > rr - 2.3) set(lvl, p, inner);
			}
		}
		// the nested shells: each smaller, taller, of another lacquer, a gold lip, a glow at the heart
		String[] mats = {"lacquer_block", "painted_wood", "lacquer_block"};
		double base = r(WAIST) - 2.3;
		for (int k = 1; k <= 3; k++) {
			double rk = base - 3.4 * k;
			int top = (int) WAIST - 3 + 3 * k;
			for (int y = 1; y <= top; y++) for (int ia = -(int) rk - 1; ia <= rk + 1; ia++) for (int is = -(int) rk - 1; is <= rk + 1; is++) {
				double d = Math.hypot(ia + 0.5, is + 0.5);
				if (d > rk || d < rk - 1.2) continue;
				set(lvl, at(ia, Y0 + y, is), y >= top - 1 ? Blocks.GOLD_BLOCK.defaultBlockState() : b(mats[k - 1]));
			}
		}
		for (int y = 1; y <= (int) WAIST + 8; y++) for (int ia = -1; ia <= 0; ia++) for (int is = -1; is <= 0; is++)
			set(lvl, at(ia, Y0 + y, is), y > WAIST + 5 ? b("matriochkite_block") : b("lacquer_glow"));
	}

	/** Upper half: voxelized already turned, LID_ANGLE about the hinge at the right of the waist, face to the camera. */
	private static void dollLid(ServerLevel lvl) {
		BlockState inner = b("painted_wood");
		double c = Math.cos(LID_ANGLE), sn = Math.sin(LID_ANGLE);
		int R = (int) Math.ceil(r(WAIST)) + 2;
		for (int ws = -R; ws <= (int) (HINGE_S + TOP); ws++) for (int wy = (int) HINGE_Y - R; wy <= (int) (HINGE_Y + TOP); wy++) {
			// back to the lid's own frame: rotate counter-clockwise about the hinge (the lid opened clockwise, top to the right)
			double px = ws + 0.5 - HINGE_S, py = wy + 0.5 - HINGE_Y;
			double lx = px * c - py * sn + HINGE_S, ly = px * sn + py * c + HINGE_Y;
			double v = ly - Y0;
			if (v < WAIST || v > TOP) continue;
			double rr = r(v);
			for (int ia = -R; ia <= R; ia++) {
				double d = Math.hypot(ia + 0.5, lx);
				boolean cap = v > TOP - 1.5 && d <= rr + 0.5;
				if (d > rr + 0.3 && !cap) continue;
				if (d < rr - 2.3 && !cap) continue;
				BlockPos p = at(ia, wy, ws);
				if (d > rr - 1.2 || cap) {
					BlockState st = null;
					if (ia + 0.5 < 0) st = face(lx, v);
					if (st == null) st = skin(Math.atan2(lx, -(ia + 0.5)) * rr, v, true);
					set(lvl, p, st);
				} else set(lvl, p, inner);
			}
		}
	}

	// ---------------------------------------------------------------- the islands

	/** A floating island of a world: its top over its stone, glow veins, a lacquer and gold ring; flipped for World 6. */
	private static void island(ServerLevel lvl, Defs.WorldDef w, double ca, double cy, double cs, double R) {
		BlockState top = b(w.top()), stone = b(w.stone()), glow = b(w.glow());
		boolean flip = w.n() == 6;
		int n = (int) Math.ceil(R) + 2;
		int seed = w.n() * 97;
		for (int ia = -n; ia <= n; ia++) for (int is = -n; is <= n; is++) {
			double ang = Math.atan2(is, ia);
			double re = R * (0.86 + 0.14 * Math.sin(ang * 3 + seed) * Math.cos(ang * 2 - seed * 0.3));
			double d = Math.hypot(ia, is);
			if (d > re + 1.0) continue;
			int depth = (int) Math.round((R * 1.15) * Math.pow(Math.max(0, 1 - (d / re) * (d / re)), 0.7)) + 1;
			int mound = d < re * 0.45 ? (int) Math.round(1.5 * (1 - d / (re * 0.45)) + hash(ia, seed, is)) : 0;
			int fy = flip ? -1 : 1;
			if (d > re) {
				// the ring round the island, a doll half: lacquer with a gold lip
				for (int k = 0; k <= 1; k++)
					set(lvl, at(ca + ia, cy + fy * k, cs + is), k == 1 || (Math.round(ang * 8) % 3 == 0) ? Blocks.GOLD_BLOCK.defaultBlockState() : b("lacquer_block"));
				set(lvl, at(ca + ia, cy - fy, cs + is), b("lacquer_block"));
				continue;
			}
			for (int k = -depth; k <= mound; k++) {
				BlockState st = k == mound ? top : (k < -1 && k > -depth && hash(ia * 3, k, is * 5 + seed) < 0.10) ? glow : stone;
				set(lvl, at(ca + ia, cy + fy * k, cs + is), st);
			}
		}
		// a few glow pillars on top, and the World 7 pool
		for (int i = 0; i < 3 + (int) R / 2; i++) {
			double an = hash(i, seed, 1) * Math.PI * 2, dd = R * (0.3 + 0.45 * hash(seed, i, 2));
			int ia = (int) Math.round(Math.cos(an) * dd), is = (int) Math.round(Math.sin(an) * dd);
			int hgt = 1 + (int) (hash(i, 7, seed) * 3);
			int fy = flip ? -1 : 1;
			for (int k = 1; k <= hgt; k++) set(lvl, at(ca + ia, cy + fy * (k + 1), cs + is), k == hgt ? glow : stone);
		}
		if (w.n() == 7) for (int ia = -2; ia <= 2; ia++) for (int is = -2; is <= 2; is++)
			if (ia * ia + is * is <= 5) set(lvl, at(ca + ia, cy + 1, cs + is), Blocks.WATER.defaultBlockState());
	}

	/**
	 * A point of the poster camera's frame sent back into the world: px, py in units of the frame's half height (py up,
	 * px right, the frame's edges at +-16/9 and +-1), at a depth D along the view. Returns local (a, y, s).
	 */
	static double[] project(double px, double py, double D) {
		Cam c = CAMS[0];
		double[] C = {c.a(), c.y(), c.s()}, f = {c.ta() - c.a(), c.ty() - c.y(), c.ts() - c.s()};
		double n = Math.sqrt(f[0] * f[0] + f[1] * f[1] + f[2] * f[2]);
		for (int k = 0; k < 3; k++) f[k] /= n;
		double rn = Math.hypot(f[0], f[2]);
		double[] r = {-f[2] / rn, 0, f[0] / rn};
		double[] u = {r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]};
		double tan = Math.tan(Math.toRadians(c.fov() / 2.0));
		double[] p = new double[3];
		for (int k = 0; k < 3; k++) p[k] = C[k] + D * (f[k] + px * tan * r[k] + py * tan * u[k]);
		return p;
	}

	/**
	 * The ten worlds, World 1 first, placed on the poster frame (px, py, depth, radius): a spiral that starts large and
	 * near at the lower right, passes under the doll, climbs the left side and curls inward, each world farther away
	 * and smaller than the last, so it opens into the depth past the doll's shoulder.
	 */
	private static final double[][] SPIRAL = {
		{1.25, -0.52, 38, 8.5}, {0.40, -0.70, 50, 8.0}, {-0.55, -0.64, 62, 7.5}, {-1.25, -0.40, 75, 7.0}, {-1.55, 0.04, 88, 6.5},
		{-1.45, 0.42, 102, 6.0}, {-1.05, 0.30, 118, 5.5}, {-0.82, 0.06, 135, 5.0}, {-0.64, -0.14, 152, 4.5}, {-0.50, -0.02, 172, 4.0},
	};

	static double[][] spiral() {
		double[][] out = new double[10][];
		for (int i = 0; i < 10; i++) {
			double[] p = project(SPIRAL[i][0], SPIRAL[i][1], SPIRAL[i][2]);
			out[i] = new double[]{p[0], p[1], p[2], SPIRAL[i][3]};
		}
		return out;
	}

	/** Loose blocks trailing from one island to the next, the worlds spilling out. */
	private static void debris(ServerLevel lvl, double[] p, double[] q, Defs.WorldDef w) {
		int n = 7;
		for (int i = 1; i < n; i++) {
			double t = i / (double) n;
			double a = p[0] + (q[0] - p[0]) * t + (hash(i, w.n(), 3) - 0.5) * 3;
			double y = p[1] + (q[1] - p[1]) * t + (hash(i, w.n(), 4) - 0.5) * 3 - Math.sin(t * Math.PI) * 4;
			double s = p[2] + (q[2] - p[2]) * t + (hash(i, w.n(), 5) - 0.5) * 3;
			set(lvl, at(a, y, s), b(hash(i, w.n(), 6) < 0.5 ? w.top() : w.stone()));
		}
	}

	/** A flat block cloud: white top, pinkish underside. */
	private static void cloud(ServerLevel lvl, double ca, double cy, double cs, int len, int wid) {
		for (int i = -len / 2; i <= len / 2; i++) for (int j = -wid / 2; j <= wid / 2; j++) {
			double e = Math.pow(i / (len / 2.0), 2) + Math.pow(j / (wid / 2.0), 2);
			if (e > 1 + 0.25 * (hash(i / 3, j / 3, 9) - 0.5)) continue;
			set(lvl, at(ca + j, cy, cs + i), v("white_concrete"));
			set(lvl, at(ca + j, cy - 1, cs + i), v("white_terracotta"));
			if (e < 0.35) set(lvl, at(ca + j, cy + 1, cs + i), v("white_concrete"));
		}
	}

	/** A sea of block clouds under the stage, the doll standing in it: white tops, a pinkish layer under. */
	private static void cloudSea(ServerLevel lvl) {
		BlockState w = v("white_concrete"), u = v("white_terracotta");
		for (int ia = -66; ia <= 190; ia++) for (int is = -95; is <= 95; is++) {
			// blocky banks far under the stage: noise on a coarse grid, gaps between them
			double n = hash(Math.floorDiv(ia, 15), 5, Math.floorDiv(is, 15)) * 0.6 + hash(Math.floorDiv(ia, 6), 6, Math.floorDiv(is, 6)) * 0.4;
			if (n < 0.40) continue;
			int y = Y0 - 30 - (n > 0.75 ? 0 : 1);
			set(lvl, at(ia, y, is), w);
			set(lvl, at(ia, y - 1, is), u);
			if (n > 0.8) set(lvl, at(ia, y + 1, is), w);
		}
	}

	static void build(ServerLevel lvl) {
		long t0 = System.nanoTime();
		dollLower(lvl);
		dollLid(lvl);
		double[][] sp = spiral();
		for (int i = 0; i < 10; i++) {
			Defs.WorldDef w = Content.WORLDS.get(i);
			island(lvl, w, sp[i][0], sp[i][1], sp[i][2], sp[i][3]);
			BlockPos cpos = at(sp[i][0], sp[i][1], sp[i][2]);
			LOG.info("[poster] island W{} at a={} y={} s={} r={} -> {} {}", w.n(), Math.round(sp[i][0]), Math.round(sp[i][1]), Math.round(sp[i][2]),
				Math.round(sp[i][3]), cpos, lvl.getBlockState(cpos.below()));
			if (i > 0) debris(lvl, sp[i - 1], sp[i], Content.WORLDS.get(i - 1));
		}
		cloud(lvl, 120, Y0 + 18, -70, 46, 20);
		cloud(lvl, 90, Y0 + 58, 64, 36, 16);
		cloud(lvl, 165, Y0 + 44, 20, 50, 22);
		cloudSea(lvl);
		LOG.info("[poster] stage built in {} ms", (System.nanoTime() - t0) / 1_000_000);
	}

	// ---------------------------------------------------------------- actors

	/** The bosses in the air, placed on the poster frame: id, px, py (their feet), depth, attack to rehearse. */
	private static final Object[][] BOSSES = {
		{"storm_king", -1.05, 0.12, 28.0, 1},
		{"pressure_leviathan", 0.90, -0.30, 30.0, 2},
		{"ash_titan", 1.22, 0.20, 46.0, 2},
	};

	private static void hero(TestServerContext s) {
		double x = wx(HERO_A) + 0.5, z = wz(HERO_S) + 0.5;
		// facing the camera (east), turned a little toward the doll's side
		String eq = "head:{id:\"matriochka:matriarch_helmet\",count:1},chest:{id:\"matriochka:matriarch_chestplate\",count:1},"
			+ "legs:{id:\"matriochka:matriarch_leggings\",count:1},feet:{id:\"matriochka:matriarch_boots\",count:1},"
			+ "mainhand:{id:\"matriochka:matriochkite_ingot\",count:1}";
		s.runCommand(String.format(Locale.ROOT, "summon minecraft:mannequin %.2f %.2f %.2f {Rotation:[-100f,0f],hide_description:1b,immovable:1b,NoGravity:1b,"
			+ "Invulnerable:1b,Tags:[\"poster_hero\"],equipment:{%s}}", x, HERO_Y, z, eq));
	}

	private static void bosses(TestServerContext s) {
		s.runOnServer(server -> {
			ServerLevel lvl = server.overworld();
			for (Object[] bo : BOSSES) {
				String id = (String) bo[0];
				Entity e = ModContent.entity(id).create(lvl, EntitySpawnReason.COMMAND);
				if (!(e instanceof MatrioBoss boss)) continue;
				double[] lp = project((double) bo[1], (double) bo[2], (double) bo[3]);
				double x = wx(lp[0]), y = lp[1], z = wz(lp[2]);
				double hx = wx(HERO_A), hz = wz(HERO_S);
				float yaw = (float) Math.toDegrees(Math.atan2(-(hx - x), hz - z));
				boss.snapTo(x, y, z, yaw, 0);
				boss.setYHeadRot(yaw);
				boss.setYBodyRot(yaw);
				boss.setNoGravity(true);
				boss.setPersistenceRequired();
				boss.addTag("poster_boss");
				boolean ok = lvl.addFreshEntity(boss);
				boss.calm(100000);
				LOG.info("[poster] boss {} at {} {} {} added {}", id, Math.round(x), Math.round(y), Math.round(z), ok);
			}
		});
	}

	/** Starts every boss's windup (their attack poses) toward the hero, then holds them there. */
	private static void windups(ClientGameTestContext ctx, TestServerContext s) {
		s.runOnServer(server -> {
			ServerLevel lvl = server.overworld();
			LivingEntity target = null;
			for (Entity e : lvl.getAllEntities()) if (e instanceof LivingEntity le && e.entityTags().contains("poster_hero")) target = le;
			if (target == null) return;
			for (Entity e : lvl.getAllEntities()) {
				if (!(e instanceof MatrioBoss boss) || !e.entityTags().contains("poster_boss")) continue;
				int atk = 1;
				for (Object[] bo : BOSSES) if (ModContent.entity((String) bo[0]) == boss.getType()) atk = (int) bo[4];
				boss.rehearse(atk, target);
			}
		});
		ctx.waitTicks(14);
		// the bosses stop where the windup has brought them: no strike, no move
		s.runOnServer(server -> {
			for (Entity e : server.overworld().getAllEntities())
				if (e instanceof MatrioBoss boss && e.entityTags().contains("poster_boss")) {
					boss.setNoAi(true);
					boss.setDeltaMovement(0, 0, 0);
				}
		});
	}

	private static void shoot(ClientGameTestContext ctx, TestServerContext s, Cam c, boolean preview) {
		s.runCommand(String.format(Locale.ROOT, "tp @p %.2f %.2f %.2f facing %.2f %.2f %.2f", wx(c.a()), c.y() - EYE, wz(c.s()), wx(c.ta()), c.ty(), wz(c.ts())));
		ctx.runOnClient(mc -> mc.options.fov().set(c.fov()));
		ctx.waitTicks(6);
		int w = preview ? 1280 : c.w(), h = preview ? (int) Math.round(1280.0 * c.h() / c.w()) : c.h();
		ctx.takeScreenshot(TestScreenshotOptions.of("poster_" + c.name() + (preview ? "_pre" : "")).withSize(w, h).disableCounterPrefix());
		LOG.info("[poster] shot {} {}x{}", c.name(), w, h);
	}

	static void run(ClientGameTestContext ctx) {
		boolean preview = !System.getProperty("matriochka.preview", "").isEmpty();
		String only = System.getProperty("matriochka.shots", "");
		try (TestSingleplayerContext sp = ctx.worldBuilder().setUseConsistentSettings(false).adjustSettings(c -> c.setSeed("matriochka")).create()) {
			var s = sp.getServer();
			try { McTest.waitForChunks(sp); } catch (AssertionError e) { ctx.waitTicks(40); }
			ctx.setScreen(() -> null);
			ctx.runOnClient(mc -> {
				var o = mc.options;
				o.renderDistance().set(16);
				o.simulationDistance().set(10);
				o.entityDistanceScaling().set(5.0);
				o.bobView().set(false);
				o.cloudStatus().set(net.minecraft.client.CloudStatus.OFF);
				o.chatVisibility().set(net.minecraft.world.entity.player.ChatVisiblity.HIDDEN);
				if (!fr.achedon12.matriochka.client.mc.McClient.hudHidden(mc)) fr.achedon12.matriochka.client.mc.McClient.toggleHud(mc);
				// the server sends chunks only as far as the client asks for: tell it the new render distance
				o.broadcastOptions();
			});
			for (String c : new String[]{"gamerule advance_time false", "gamerule advance_weather false", "weather clear", "gamerule spawn_monsters false",
				"gamerule announce_advancements false", "gamerule send_command_feedback false", "gamerule show_death_messages false",
				"gamerule fire_spread_radius_around_player 0", "time set 6000", "difficulty normal", "gamemode spectator @a"}) s.runCommand(c);
			s.runOnServer(server -> fr.achedon12.matriochka.world.Config.get().worldEvents = false);
			// the integrated server keeps a short view distance in tests: the stage reaches 190 blocks away
			s.runOnServer(server -> server.getPlayerList().setViewDistance(16));
			// stand at the poster camera so the stage's chunks load around it, then build
			Cam c0 = CAMS[0];
			s.runCommand(String.format(Locale.ROOT, "tp @p %.2f %.2f %.2f", wx(c0.a()), c0.y(), wz(c0.s())));
			// in two halves: one forceload is limited to 256 chunks
			s.runCommand("forceload add " + (X0 - 200) + " " + (Z0 - 100) + " " + (X0 - 60) + " " + (Z0 + 100));
			s.runCommand("forceload add " + (X0 - 59) + " " + (Z0 - 100) + " " + (X0 + 90) + " " + (Z0 + 100));
			ctx.waitTicks(60);
			s.runOnServer(server -> build(server.overworld()));
			hero(s);
			PosterPose.active = true;
			bosses(s);
			ctx.waitTicks(60);
			windups(ctx, s);
			try { McTest.waitForChunks(sp); } catch (AssertionError e) { ctx.waitTicks(60); }
			ctx.waitTicks(20);
			int rd = ctx.computeOnClient(mc -> mc.options.getEffectiveRenderDistance());
			LOG.info("[poster] client render distance {}", rd);
			// the server sends chunks a few at a time: wait until the client holds every island (and the far clouds)
			java.util.List<BlockPos> probes = new java.util.ArrayList<>();
			for (double[] isl : spiral()) probes.add(at(isl[0], isl[1], isl[2]).below());
			int waited = 0;
			for (; waited < 1200; waited += 20) {
				boolean all = ctx.computeOnClient(mc -> {
					for (BlockPos q : probes) if (mc.level.getBlockState(q).isAir()) return false;
					return true;
				});
				if (all) break;
				ctx.waitTicks(20);
			}
			LOG.info("[poster] islands on the client after {} ticks", waited);
			s.runOnServer(server -> {
				for (Entity e : server.overworld().getAllEntities())
					if (e.entityTags().contains("poster_boss") || e.entityTags().contains("poster_hero"))
						LOG.info("[poster] actor {} alive {} at {}", e.getType(), e.isAlive(), e.blockPosition());
			});
			try { McTest.waitForChunks(sp); } catch (AssertionError e) { ctx.waitTicks(40); }
			ctx.waitTicks(40);
			for (Cam c : CAMS) {
				if (!only.isEmpty() && !("," + only + ",").contains("," + c.name() + ",")) continue;
				shoot(ctx, s, c, preview);
			}
			PosterPose.active = false;
			s.runOnServer(server -> fr.achedon12.matriochka.world.Config.get().worldEvents = true);
		}
	}
}
