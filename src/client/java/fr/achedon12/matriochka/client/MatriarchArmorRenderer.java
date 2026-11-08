package fr.achedon12.matriochka.client;

import com.geckolib.constant.dataticket.DataTicket;
import com.geckolib.model.DefaultedItemGeoModel;
import com.geckolib.renderer.GeoArmorRenderer;
import com.geckolib.renderer.base.BoneSnapshots;
import com.geckolib.renderer.base.GeoRenderState;
import com.geckolib.renderer.base.RenderPassInfo;
import com.geckolib.renderer.layer.builtin.AutoGlowingGeoLayer;
import fr.achedon12.matriochka.Matriochka;
import fr.achedon12.matriochka.item.MatriarchArmor;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import net.minecraft.world.entity.LivingEntity;

/**
 * The Matriarch Armour worn (tools/matriarch_geo.py): its gold and its pearls lit, and the gem on the breast lit while
 * the wearer's Nested Shell is ready, dark while it mends (what the client knows: the player's own shell; another
 * player's always reads ready).
 */
public class MatriarchArmorRenderer<R extends HumanoidRenderState & GeoRenderState> extends GeoArmorRenderer<MatriarchArmor, R> {
	private static final DataTicket<Boolean> READY = DataTicket.create("matriochka_nested_shell_ready", Boolean.class);

	public MatriarchArmorRenderer() {
		super(new DefaultedItemGeoModel<>(Matriochka.id("armor/matriarch")));
		withRenderLayer(new AutoGlowingGeoLayer<>(this));
	}

	@Override
	public void addRenderData(MatriarchArmor animatable, GeoArmorRenderer.RenderData data, R state, float partialTick) {
		super.addRenderData(animatable, data, state, partialTick);
		state.addGeckolibData(READY, ready(data.entity()));
	}

	@Override
	public void adjustModelBonesForRender(RenderPassInfo<R> info, BoneSnapshots snapshots) {
		super.adjustModelBonesForRender(info, snapshots);
		boolean ready = info.getOrDefaultGeckolibData(READY, true);
		snapshots.ifPresent("gem_lit", b -> b.skipRender(!ready));
		snapshots.ifPresent("gem_dim", b -> b.skipRender(ready));
	}

	private static boolean ready(LivingEntity e) {
		Minecraft mc = Minecraft.getInstance();
		if (e == null || mc.player == null || e != mc.player) return true;
		return MatriarchTip.secondsLeft() <= 0;
	}
}
