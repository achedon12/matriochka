package fr.achedon12.matriochka.client;

import com.geckolib.animatable.GeoAnimatable;
import com.geckolib.constant.dataticket.DataTicket;
import com.geckolib.renderer.base.GeoRenderState;
import com.geckolib.renderer.base.GeoRenderer;
import com.geckolib.renderer.layer.builtin.AutoGlowingGeoLayer;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.entity.MatrioBoss;
import net.minecraft.resources.Identifier;

/**
 * A boss breaking: after its first phase change glowing cracks of its world's colour run over its body, many more
 * after the second (textures/entity/<boss>_cracks_<1|2>, by tools/cracks.py), drawn full-bright like its glow mask.
 */
public class BossCracksLayer<T extends GeoAnimatable, O, R extends GeoRenderState> extends AutoGlowingGeoLayer<T, O, R> {
	private static final DataTicket<Integer> SHELL = DataTicket.create("matriochka_shell", Integer.class);
	private static final Identifier NONE = Matriochka.id("textures/entity/boss_cracks_none.png");
	private final String id;

	public BossCracksLayer(GeoRenderer<T, O, R> renderer, String id) {
		super(renderer);
		this.id = id;
	}

	@Override
	public void addRenderData(T animatable, O related, R state, float partialTick) {
		super.addRenderData(animatable, related, state, partialTick);
		state.addGeckolibData(SHELL, animatable instanceof MatrioBoss b ? b.shell() : 0);
	}

	@Override
	protected Identifier getTextureResource(R state) {
		int shell = state.getOrDefaultGeckolibData(SHELL, 0);
		return shell <= 0 ? NONE : Matriochka.id("textures/entity/" + id + "_cracks_" + Math.min(2, shell) + ".png");
	}
}
