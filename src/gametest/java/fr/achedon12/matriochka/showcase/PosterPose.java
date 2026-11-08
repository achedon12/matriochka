package fr.achedon12.matriochka.showcase;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.core.registries.BuiltInRegistries;

/**
 * The key art hero's action pose (PosterCapture), applied by mixin.HeroPoseMixin to every mannequin while active:
 * a mannequin has a player's skin but only whole-body poses, so its limbs are set here, in radians, model space
 * (a negative xRot lifts an arm forward and up; zRot swings it out to the side).
 */
public final class PosterPose {
	private PosterPose() {}

	public static volatile boolean active;
	/** head, body, right arm, left arm, right leg, left leg: x, y, z rotations. */
	public static volatile float[][] parts = {
		{-0.12f, 0.20f, 0.05f},  // head a little up, turned toward the raised hand
		{0.03f, 0.10f, 0.03f},   // body twisted a little
		{-3.00f, 0.0f, -0.50f},  // right arm raised high and out (a raised arm swings out with a negative zRot)
		{0.30f, 0f, -0.95f},     // left arm thrown down and out
		{-0.30f, 0.0f, 0.40f},   // right leg out to the side: a leap
		{0.35f, 0.0f, -0.30f},   // left leg back and out
	};

	public static void apply(HumanoidModel<?> m, HumanoidRenderState s) {
		if (s.entityType == null) return;
		var key = BuiltInRegistries.ENTITY_TYPE.getKey(s.entityType);
		if (key == null || !key.getPath().equals("mannequin")) return;
		ModelPart[] ps = {m.head, m.body, m.rightArm, m.leftArm, m.rightLeg, m.leftLeg};
		float[][] p = parts;
		for (int i = 0; i < ps.length; i++) {
			ps[i].xRot = p[i][0];
			ps[i].yRot = p[i][1];
			ps[i].zRot = p[i][2];
		}
	}
}
