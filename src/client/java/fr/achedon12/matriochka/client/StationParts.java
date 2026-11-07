package fr.achedon12.matriochka.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import fr.achedon12.matriochka.Matriochka;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.Direction;
import net.minecraft.resources.Identifier;
import net.minecraft.util.LightCoordsUtil;

/**
 * The moving parts of the sculpted stations, drawn over their block models: the matrix spinning over the workbench,
 * the soul wisps round the altar bowl, the press ram, the pendulum, the loom shuttle... Units are sixteenths in the
 * model's own frame (front to the north); the pose is turned to the station's facing first.
 * <p>
 * Each part is a handful of boxes with one of the station materials (textures/block/station/), so a station costs a
 * few dozen quads, and only within 24 blocks.
 */
final class StationParts {
	private StationParts() {}

	private static Identifier mat(String name) {
		return Matriochka.id("textures/block/station/" + name + ".png");
	}

	private static RenderType solid(String name) {
		return RenderTypes.entitySolid(mat(name));
	}

	private static RenderType lit(String name) {
		return RenderTypes.entityTranslucentEmissive(mat(name));
	}

	static boolean animated(String station) {
		return switch (station) {
			case "ash_foundry" -> false;
			default -> true;
		};
	}

	/**
	 * Draws the moving parts of `station`. `t` is in ticks (with the partial tick), `value` the station's live reading
	 * (forge charge 0..8, vat ferment seconds...).
	 */
	static void submit(String station, int world, Direction facing, float t, int value, PoseStack pose, SubmitNodeCollector out, int light) {
		pose.pushPose();
		pose.translate(0.5f, 0, 0.5f);
		pose.rotateDegrees(Axis.YP, -facing.toYRot() + 180f);
		pose.translate(-0.5f, 0, -0.5f);
		pose.scale(1 / 16f, 1 / 16f, 1 / 16f);
		int full = LightCoordsUtil.FULL_BRIGHT;
		String glow = "glow_" + world;
		switch (station) {
			case "matrix_workbench" -> {
				// a gilded frame cube with a lit heart, spinning and bobbing over the dais
				pose.pushPose();
				pose.translate(8, 16.2f + (float) Math.sin(t / 14.0) * 0.6f, 8);
				pose.rotateDegrees(Axis.YP, t * 2.2f);
				pose.rotateDegrees(Axis.XP, 35.26f);
				pose.rotateDegrees(Axis.ZP, 45f);
				frameCube(pose, out, solid("gold"), 2.2f, 0.45f, light);
				box(pose, out, lit(glow), -1.1f, -1.1f, -1.1f, 1.1f, 1.1f, 1.1f, 0xFFFFFFFF, full);
				pose.popPose();
			}
			case "class_table" -> {
				// the rank medal turns over the open book
				pose.pushPose();
				pose.translate(8, 16.5f + (float) Math.sin(t / 18.0) * 0.4f, 9);
				pose.rotateDegrees(Axis.YP, t * 1.6f);
				box(pose, out, solid("gold"), -1.6f, -1.6f, -0.25f, 1.6f, 1.6f, 0.25f, 0xFFFFFFFF, light);
				box(pose, out, lit(glow), -0.8f, -0.8f, -0.4f, 0.8f, 0.8f, 0.4f, 0xFFFFFFFF, full);
				pose.popPose();
			}
			case "soul_altar" -> {
				// three wisps circling the bowl, rising and sinking out of step
				for (int i = 0; i < 3; i++) {
					double a = t / 22.0 + i * Math.PI * 2 / 3;
					float x = 8 + (float) Math.cos(a) * 4.2f, z = 8 + (float) Math.sin(a) * 4.2f;
					float y = 13.5f + (float) Math.sin(t / 11.0 + i * 2) * 1.2f;
					box(pose, out, lit("soul"), x - 0.6f, y - 0.6f, z - 0.6f, x + 0.6f, y + 0.6f, z + 0.6f, 0xE0FFFFFF, full);
				}
			}
			case "spore_vat" -> {
				// bubbles rise from the brew and burst; an aged brew boils harder
				int n = value >= 300 ? 5 : value >= 60 ? 3 : 2;
				for (int i = 0; i < n; i++) {
					float p = ((t + i * 37) % 60) / 60f;
					float x = 5 + ((i * 53) % 7), z = 5 + ((i * 31) % 6);
					float y = 12.6f + p * 3.5f, s = 0.35f + p * 0.4f;
					int a = (int) (220 * (1 - p));
					box(pose, out, lit(glow), x - s, y - s, z - s, x + s, y + s, z + s, (a << 24) | 0xFFFFFF, full);
				}
			}
			case "jailer_table" -> {
				// the key in the lock plate turns back and forth
				pose.pushPose();
				pose.translate(8, 16f, 8);
				pose.rotateDegrees(Axis.YP, (float) Math.sin(t / 16.0) * 70f);
				box(pose, out, solid("iron"), -0.4f, 0, -0.4f, 0.4f, 2.4f, 0.4f, 0xFFFFFFFF, light);
				box(pose, out, solid("gold"), -1.4f, 2.4f, -0.35f, 1.4f, 3.6f, 0.35f, 0xFFFFFFFF, light);
				pose.popPose();
			}
			case "lightning_forge" -> {
				// an arc jumps between the coil tips while the forge holds charge
				if (value > 0 || ((int) t / 7) % 9 == 0) {
					int seed = (int) (t / 2);
					float px = 1.75f, py = 15.3f;
					for (int k = 1; k <= 10; k++) {
						float x = 1.75f + k * 1.25f;
						float y = 15.3f + 1.4f * (float) Math.sin(k * Math.PI / 11) + (float) (hash(seed + k) - 0.5) * 1.2f;
						segment(pose, out, lit(glow), px, py, 13.75f, x, y, 13.75f, full);
						px = x;
						py = y;
					}
				}
			}
			case "dark_altar" -> {
				// the dark crystal hangs over the slab, turning, its heart lit
				pose.pushPose();
				pose.translate(8, 13.5f + (float) Math.sin(t / 20.0) * 0.8f, 8);
				pose.rotateDegrees(Axis.YP, t * 0.9f);
				pose.rotateDegrees(Axis.XP, 45f);
				pose.rotateDegrees(Axis.ZP, 45f);
				box(pose, out, solid("obsidian"), -1.8f, -1.8f, -1.8f, 1.8f, 1.8f, 1.8f, 0xFFFFFFFF, light);
				box(pose, out, lit(glow), -1.0f, -1.0f, -1.0f, 1.0f, 1.0f, 1.0f, 0xFFFFFFFF, full);
				pose.popPose();
			}
			case "inverter" -> {
				// a gilded ring turns round the waist of the hourglass, flipping over every few seconds
				pose.pushPose();
				pose.translate(8, 8, 8);
				pose.rotateDegrees(Axis.YP, t * 1.2f);
				float flip = (float) Math.max(0, Math.sin(t / 40.0)) * 180f;
				pose.rotateDegrees(Axis.XP, flip);
				ring(pose, out, solid("gold"), 5.2f, 0.45f, light);
				pose.popPose();
			}
			case "abyssal_press" -> {
				// the ram: pressed down slowly, released quickly
				float c = (t % 80) / 80f;
				float down = c < 0.7f ? c / 0.7f : 1 - (c - 0.7f) / 0.3f;
				float y = 12.5f - down * 7.5f;
				box(pose, out, solid("copper"), 7, y + 1.2f, 7, 9, 13, 9, 0xFFFFFFFF, light);
				box(pose, out, solid("iron"), 3.6f, y, 5.4f, 12.4f, y + 1.2f, 10.6f, 0xFFFFFFFF, light);
				if (down > 0.95f) box(pose, out, lit(glow), 4, 4.02f, 5.8f, 12, 4.3f, 10.2f, 0xC0FFFFFF, full);
			}
			case "time_workshop" -> {
				// the pendulum behind the glass, and the hands on the face
				pose.pushPose();
				pose.translate(8, 7.2f, 4.4f);
				pose.rotateDegrees(Axis.ZP, (float) Math.sin(t / 10.0) * 22f);
				box(pose, out, solid("gold"), -0.2f, -4f, -0.15f, 0.2f, 0, 0.15f, 0xFFFFFFFF, light);
				box(pose, out, solid("gold"), -0.9f, -4.9f, -0.3f, 0.9f, -3.6f, 0.3f, 0xFFFFFFFF, light);
				pose.popPose();
				long day = (long) t;
				hand(pose, out, (day % 24000) / 24000f * 720f, 2.4f, 0.35f, light);
				hand(pose, out, (day % 1000) / 1000f * 360f, 3.4f, 0.25f, light);
			}
			case "terrain_anchor" -> {
				// eight stones orbit the pylon, rising and falling like a slow wave
				for (int i = 0; i < 8; i++) {
					double a = t / 30.0 + i * Math.PI / 4;
					float x = 8 + (float) Math.cos(a) * 6f, z = 8 + (float) Math.sin(a) * 6f;
					float y = 11 + (float) Math.sin(t / 15.0 + i) * 1.4f;
					box(pose, out, solid("stone_" + world), x - 0.8f, y - 0.8f, z - 0.8f, x + 0.8f, y + 0.8f, z + 0.8f, 0xFFFFFFFF, light);
				}
				box(pose, out, lit(glow), 7.6f, 16f, 7.6f, 8.4f, 17.5f + (float) Math.sin(t / 8.0) * 0.4f, 8.4f, 0xFFFFFFFF, full);
			}
			case "final_loom" -> {
				// the shuttle runs across the warp, and the beater swings after it
				float s = (float) Math.sin(t / 12.0);
				float x = 8 + s * 4.6f;
				box(pose, out, solid("dark_wood"), x - 1.6f, 9.5f, 5.2f, x + 1.6f, 10.4f, 6.2f, 0xFFFFFFFF, light);
				box(pose, out, solid("gold"), x - 0.5f, 10.4f, 5.4f, x + 0.5f, 10.7f, 6.0f, 0xFFFFFFFF, light);
			}
			default -> {}
		}
		pose.popPose();
	}

	private static double hash(int n) {
		n = (n << 13) ^ n;
		return ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 2147483647.0;
	}

	private static void hand(PoseStack pose, SubmitNodeCollector out, float deg, float len, float w, int light) {
		pose.pushPose();
		pose.translate(8, 11, 3.35f);
		pose.rotateDegrees(Axis.ZP, -deg);
		box(pose, out, solid("iron"), -w, 0, -0.1f, w, len, 0.1f, 0xFF202020, light);
		pose.popPose();
	}

	/** A thin lit bar from one point to another in the x-y plane. */
	private static void segment(PoseStack pose, SubmitNodeCollector out, RenderType rt, float x0, float y0, float z, float x1, float y1, float z1, int light) {
		float dx = x1 - x0, dy = y1 - y0;
		float len = (float) Math.sqrt(dx * dx + dy * dy);
		pose.pushPose();
		pose.translate(x0, y0, z);
		pose.rotateDegrees(Axis.ZP, (float) Math.toDegrees(Math.atan2(dy, dx)));
		box(pose, out, rt, 0, -0.18f, -0.18f, len, 0.18f, 0.18f, 0xFFFFFFFF, light);
		pose.popPose();
	}

	private static void frameCube(PoseStack pose, SubmitNodeCollector out, RenderType rt, float r, float b, int light) {
		// twelve edges of a cube of half-size r, each bar b thick
		for (int i = -1; i <= 1; i += 2)
			for (int j = -1; j <= 1; j += 2) {
				float u = i * (r - b / 2), v = j * (r - b / 2);
				box(pose, out, rt, -r, u - b / 2, v - b / 2, r, u + b / 2, v + b / 2, 0xFFFFFFFF, light);
				box(pose, out, rt, u - b / 2, -r, v - b / 2, u + b / 2, r, v + b / 2, 0xFFFFFFFF, light);
				box(pose, out, rt, u - b / 2, v - b / 2, -r, u + b / 2, v + b / 2, r, 0xFFFFFFFF, light);
			}
	}

	private static void ring(PoseStack pose, SubmitNodeCollector out, RenderType rt, float r, float b, int light) {
		for (int k = 0; k < 16; k++) {
			pose.pushPose();
			pose.rotateDegrees(Axis.YP, k * 22.5f);
			float half = (float) (r * Math.tan(Math.PI / 16)) + 0.05f;
			box(pose, out, rt, -half, -b, r - b, half, b, r + b, 0xFFFFFFFF, light);
			pose.popPose();
		}
	}

	private static void box(PoseStack pose, SubmitNodeCollector out, RenderType rt, float x0, float y0, float z0, float x1, float y1, float z1, int color, int light) {
		out.submitCustomGeometry(pose, rt, (p, vc) -> cube(vc, p, x0, y0, z0, x1, y1, z1, color, light));
	}

	private static void cube(VertexConsumer vc, PoseStack.Pose p, float x0, float y0, float z0, float x1, float y1, float z1, int color, int light) {
		// each face takes the part of the texture its size covers (sixteenths), like a block model face
		quad(vc, p, x0, y1, z0, x0, y1, z1, x1, y1, z1, x1, y1, z0, 0, 1, 0, color, light, x1 - x0, z1 - z0);
		quad(vc, p, x0, y0, z1, x0, y0, z0, x1, y0, z0, x1, y0, z1, 0, -1, 0, color, light, x1 - x0, z1 - z0);
		quad(vc, p, x1, y1, z0, x1, y0, z0, x0, y0, z0, x0, y1, z0, 0, 0, -1, color, light, x1 - x0, y1 - y0);
		quad(vc, p, x0, y1, z1, x0, y0, z1, x1, y0, z1, x1, y1, z1, 0, 0, 1, color, light, x1 - x0, y1 - y0);
		quad(vc, p, x0, y1, z0, x0, y0, z0, x0, y0, z1, x0, y1, z1, -1, 0, 0, color, light, z1 - z0, y1 - y0);
		quad(vc, p, x1, y1, z1, x1, y0, z1, x1, y0, z0, x1, y1, z0, 1, 0, 0, color, light, z1 - z0, y1 - y0);
	}

	private static void quad(VertexConsumer vc, PoseStack.Pose p, float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz,
		float dx, float dy, float dz, float nx, float ny, float nz, int color, int light, float w, float h) {
		float u = Math.min(1, Math.abs(w) / 16f), v = Math.min(1, Math.abs(h) / 16f);
		int ov = OverlayTexture.NO_OVERLAY;
		vc.addVertex(p, ax, ay, az).setColor(color).setUv(0, 0).setOverlay(ov).setLight(light).setNormal(p, nx, ny, nz);
		vc.addVertex(p, bx, by, bz).setColor(color).setUv(0, v).setOverlay(ov).setLight(light).setNormal(p, nx, ny, nz);
		vc.addVertex(p, cx, cy, cz).setColor(color).setUv(u, v).setOverlay(ov).setLight(light).setNormal(p, nx, ny, nz);
		vc.addVertex(p, dx, dy, dz).setColor(color).setUv(u, 0).setOverlay(ov).setLight(light).setNormal(p, nx, ny, nz);
	}
}
