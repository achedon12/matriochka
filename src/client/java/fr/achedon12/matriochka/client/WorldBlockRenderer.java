package fr.achedon12.matriochka.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.block.DataBlockEntity;
import fr.achedon12.matriochka.content.Content;
import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.blockentity.state.BlockEntityRenderState;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.LightCoordsUtil;
import net.minecraft.world.phys.Vec3;

/**
 * The miniature world above a World Block: a slowly turning island of its world's own blocks (surface on top,
 * ground under it), a little sun of its light block circling in its sky colour, a lid of rock over the ceiling
 * worlds and water over the ocean. Hallowed and calm worlds look greener, wild and cursed ones redder, and the
 * island shakes while the world inside quakes or holds a boss fight.
 * <p>
 * Kept cheap on purpose: at most a hundred little cubes drawn with three textures, and only within 24 blocks.
 */
public class WorldBlockRenderer implements BlockEntityRenderer<DataBlockEntity, WorldBlockRenderer.State> {
	private static final int N = 5;
	private static final float CELL = 0.11f;

	public static class State extends BlockEntityRenderState {
		boolean show;
		int world;
		String variant = "plain";
		float time;
		boolean shaking;
	}

	public WorldBlockRenderer(BlockEntityRendererProvider.Context ctx) {}

	@Override
	public State createRenderState() {
		return new State();
	}

	@Override
	public void extractRenderState(DataBlockEntity be, State st, float partial, Vec3 camera, ModelFeatureRenderer.CrumblingOverlay crumbling) {
		BlockEntityRenderState.extractBase(be, st, crumbling);
		st.show = be.getLevel() != null && be.getBlockState().is(ModContent.block("world_block"));
		if (!st.show) return;
		st.world = Math.max(1, Math.min(10, be.data().getIntOr("world", 1)));
		st.variant = be.data().getStringOr("variant", "plain");
		long now = be.getLevel().getGameTime();
		st.time = (now % 24000L) + partial;
		st.shaking = be.data().getLongOr("quake", 0L) > now;
		// the block itself is opaque: light the island with the air above it
		st.lightCoords = LightCoordsUtil.getLightCoords(be.getLevel(), be.getBlockPos().above());
	}

	@Override
	public boolean shouldRender(DataBlockEntity be, Vec3 camera) {
		return be.getBlockState().is(ModContent.block("world_block")) && Vec3.atCenterOf(be.getBlockPos()).closerThan(camera, 24);
	}

	@Override
	public void submit(State st, PoseStack pose, SubmitNodeCollector out, CameraRenderState camera) {
		if (!st.show) return;
		Defs.WorldDef w = Content.WORLDS.get(st.world - 1);
		int tint = switch (st.variant) {
			case "calm", "blessed" -> 0xFFD8F4D0;
			case "wild", "cursed" -> 0xFFF4C8C0;
			default -> 0xFFFFFFFF;
		};
		int light = st.lightCoords;
		pose.pushPose();
		float bob = (float) Math.sin(st.time / 20.0) * 0.025f;
		float jx = 0, jz = 0;
		if (st.shaking) {
			jx = (float) Math.sin(st.time * 3.1) * 0.02f;
			jz = (float) Math.cos(st.time * 2.7) * 0.02f;
		}
		pose.translate(0.5f + jx, 1.06f + bob, 0.5f + jz);
		pose.rotateDegrees(Axis.YP, st.time * 0.6f);
		float half = N * CELL / 2f;
		int world = st.world;
		// the island: one column per cell, its height from the world number, lower at the rim
		out.submitCustomGeometry(pose, RenderTypes.entitySolid(tex(w.stone())), (p, vc) -> {
			for (int i = 0; i < N; i++)
				for (int j = 0; j < N; j++) {
					int h = height(world, i, j);
					for (int y = 0; y < h - 1; y++) cube(vc, p, -half + i * CELL, y * CELL - 0.1f, -half + j * CELL, CELL, tint, light);
				}
			if (Content.WORLDS.get(world - 1).ceiling()) {
				// a lid of rock over the ceiling worlds, a few stalactites hanging from it
				for (int i = 0; i < N; i++)
					for (int j = 0; j < N; j++) {
						if ((i + j * 3 + world) % 4 == 0) continue;
						cube(vc, p, -half + i * CELL, 0.42f, -half + j * CELL, CELL, tint, light);
						if ((i * 7 + j + world) % 5 == 0) cube(vc, p, -half + i * CELL + CELL / 4, 0.42f - CELL / 2, -half + j * CELL + CELL / 4, CELL / 2, tint, light);
					}
			}
		});
		out.submitCustomGeometry(pose, RenderTypes.entitySolid(tex(w.top())), (p, vc) -> {
			for (int i = 0; i < N; i++)
				for (int j = 0; j < N; j++) cube(vc, p, -half + i * CELL, (height(world, i, j) - 1) * CELL - 0.1f, -half + j * CELL, CELL, tint, light);
		});
		// the sun: the world's light block, circling in its sky colour
		float a = st.time / 30f;
		float sx = (float) Math.cos(a) * 0.3f, sz = (float) Math.sin(a) * 0.3f;
		int sky = 0xFF000000 | w.sky();
		if (w.sky() == 0) sky = 0xFF6A8AFF;
		final int sun = sky;
		out.submitCustomGeometry(pose, RenderTypes.entityTranslucentEmissive(tex(w.glow())), (p, vc) -> cube(vc, p, sx - 0.04f, 0.32f, sz - 0.04f, 0.08f, sun, LightCoordsUtil.FULL_BRIGHT));
		if (world == 7) {
			// the Pressure Ocean: a sheet of water over everything
			out.submitCustomGeometry(pose, RenderTypes.entityTranslucent(Identifier.withDefaultNamespace("textures/block/water_still.png")),
				(p, vc) -> box(vc, p, -half, -0.1f, -half, half, 0.28f, half, 0xA03A7AD0, light, 1f / 32f));
		}
		pose.popPose();
	}

	private static Identifier tex(String block) {
		return Matriochka.id("textures/block/" + block + ".png");
	}

	/** Column height (in cells) of the island: a mound, higher in the middle, varied by the world. */
	private static int height(int world, int i, int j) {
		int d = Math.max(Math.abs(i - N / 2), Math.abs(j - N / 2));
		int bump = Math.floorMod(i * 73 + j * 31 + world * 17, 3) == 0 ? 1 : 0;
		return Math.max(1, 3 - d + bump);
	}

	private static void cube(VertexConsumer vc, PoseStack.Pose p, float x, float y, float z, float s, int color, int light) {
		box(vc, p, x, y, z, x + s, y + s, z + s, color, light, 1f);
	}

	/** An axis-aligned box with the whole texture on every face (v scaled by vmax for strip textures). */
	private static void box(VertexConsumer vc, PoseStack.Pose p, float x0, float y0, float z0, float x1, float y1, float z1, int color, int light, float vmax) {
		int ov = OverlayTexture.NO_OVERLAY;
		// top and bottom
		quad(vc, p, x0, y1, z0, x0, y1, z1, x1, y1, z1, x1, y1, z0, 0, 1, 0, color, light, ov, vmax);
		quad(vc, p, x0, y0, z1, x0, y0, z0, x1, y0, z0, x1, y0, z1, 0, -1, 0, color, light, ov, vmax);
		// north and south
		quad(vc, p, x1, y1, z0, x1, y0, z0, x0, y0, z0, x0, y1, z0, 0, 0, -1, color, light, ov, vmax);
		quad(vc, p, x0, y1, z1, x0, y0, z1, x1, y0, z1, x1, y1, z1, 0, 0, 1, color, light, ov, vmax);
		// west and east
		quad(vc, p, x0, y1, z0, x0, y0, z0, x0, y0, z1, x0, y1, z1, -1, 0, 0, color, light, ov, vmax);
		quad(vc, p, x1, y1, z1, x1, y0, z1, x1, y0, z0, x1, y1, z0, 1, 0, 0, color, light, ov, vmax);
	}

	private static void quad(VertexConsumer vc, PoseStack.Pose p, float ax, float ay, float az, float bx, float by, float bz, float cx, float cy, float cz,
		float dx, float dy, float dz, float nx, float ny, float nz, int color, int light, int ov, float vmax) {
		vertex(vc, p, ax, ay, az, 0, 0, nx, ny, nz, color, light, ov);
		vertex(vc, p, bx, by, bz, 0, vmax, nx, ny, nz, color, light, ov);
		vertex(vc, p, cx, cy, cz, 1, vmax, nx, ny, nz, color, light, ov);
		vertex(vc, p, dx, dy, dz, 1, 0, nx, ny, nz, color, light, ov);
	}

	private static void vertex(VertexConsumer vc, PoseStack.Pose p, float x, float y, float z, float u, float v, float nx, float ny, float nz, int color, int light, int ov) {
		vc.addVertex(p, x, y, z).setColor(color).setUv(u, v).setOverlay(ov).setLight(light).setNormal(p, nx, ny, nz);
	}
}
