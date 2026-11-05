package fr.achedon12.matriochka.client;

import fr.achedon12.matriochka.content.Particles;
import net.fabricmc.fabric.api.client.particle.v1.ParticleProviderRegistry;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;

/**
 * Every Matriochka particle (tools/particles.py): a camera-facing sprite that falls or rises, sways, spins, fades and
 * steps through its frames over its life. Glowing ones are drawn at full brightness, so they light up in the dark
 * and keep their glow with shader packs that read the vanilla light value.
 */
public class MatrioParticle extends SingleQuadParticle {
	private final SpriteSet sprites;
	private final Particles.Style style;
	private final float spin;
	private final float phase;

	protected MatrioParticle(ClientLevel level, double x, double y, double z, double xa, double ya, double za, SpriteSet sprites, Particles.Style style) {
		super(level, x, y, z, sprites.first());
		this.sprites = sprites;
		this.style = style;
		this.xd = xa + (random.nextFloat() - 0.5f) * 0.01f;
		this.yd = ya;
		this.zd = za + (random.nextFloat() - 0.5f) * 0.01f;
		this.friction = style.friction();
		this.gravity = 0f;
		this.hasPhysics = style.gravity() > 0.02f;
		this.lifetime = style.lifeMin() + random.nextInt(Math.max(1, style.lifeMax() - style.lifeMin() + 1));
		this.quadSize = style.size() * (0.75f + random.nextFloat() * 0.5f);
		this.spin = style.spin() * (random.nextBoolean() ? 1 : -1) * (0.5f + random.nextFloat());
		this.phase = random.nextFloat() * Mth.TWO_PI;
		this.roll = random.nextFloat() * Mth.TWO_PI * (style.spin() > 0 ? 1 : 0);
		this.oRoll = this.roll;
		this.alpha = style.alpha();
		setSpriteFromAge(sprites);
	}

	@Override
	public void tick() {
		xo = x;
		yo = y;
		zo = z;
		oRoll = roll;
		if (age++ >= lifetime) {
			remove();
			return;
		}
		yd -= style.gravity();
		if (style.sway() > 0) {
			float t = age * 0.12f + phase;
			xd += Mth.cos(t) * style.sway() * 0.1f;
			zd += Mth.sin(t * 0.8f) * style.sway() * 0.1f;
		}
		move(xd, yd, zd);
		xd *= friction;
		yd *= friction;
		zd *= friction;
		roll += spin;
		float life = (float) age / lifetime;
		// fade in over the first tenth of the life, out over the last third
		float fade = life < 0.1f ? life / 0.1f : life > 0.66f ? (1 - life) / 0.34f : 1f;
		alpha = style.alpha() * Mth.clamp(fade, 0f, 1f);
		if (style.frames() > 1) setSpriteFromAge(sprites);
	}

	@Override
	protected SingleQuadParticle.Layer getLayer() {
		return SingleQuadParticle.Layer.TRANSLUCENT;
	}

	@Override
	public int getLightCoords(float a) {
		return style.glow() ? 0xF000F0 : super.getLightCoords(a);
	}

	/** Registers the client side of every particle type of the mod. */
	public static void register() {
		for (var e : Particles.STYLES.entrySet()) {
			SimpleParticleType type = e.getKey();
			Particles.Style style = e.getValue();
			ParticleProviderRegistry.getInstance().register(type,
				sprites -> (options, level, x, y, z, xa, ya, za, random) -> new MatrioParticle(level, x, y, z, xa, ya, za, sprites, style));
		}
	}
}
