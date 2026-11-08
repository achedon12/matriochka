package fr.achedon12.matriochka.item;

import com.geckolib.animatable.GeoItem;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.Defs;
import java.util.function.Consumer;
import net.minecraft.world.item.ItemStack;

/**
 * A piece of the Matriarch Armour: worn, it is drawn by a GeckoLib armour model (tools/matriarch_geo.py,
 * client/MatriarchArmorRenderer) with a glint running along its gold; in the inventory it keeps its painted icon. Its
 * tooltip lists the set and the Nested Shell's state (client/MatriarchTip).
 */
public class MatriarchArmor extends MatrioItem implements GeoItem {
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
	/**
	 * Its render provider (a GeckoLib GeoRenderProvider giving the armour renderer), made by the client
	 * (client/MatriarchTip) and handed to GeckoLib through getRenderProvider; none on a server.
	 */
	public static Object PROVIDER;

	/** The tooltip's set checklist and shell state, drawn by the client (client/MatriarchTip). */
	public static java.util.function.BiConsumer<ItemStack, Consumer<net.minecraft.network.chat.Component>> TIP = (s, out) -> {};

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	public MatriarchArmor(Defs.ItemDef def, Properties properties) {
		super(def, properties);
	}

	@Override
	public void appendHoverText(ItemStack stack, TooltipContext context, net.minecraft.world.item.component.TooltipDisplay display,
			Consumer<net.minecraft.network.chat.Component> out, net.minecraft.world.item.TooltipFlag flag) {
		super.appendHoverText(stack, context, display, out, flag);
		TIP.accept(stack, out);
	}

	@Override
	public Object getRenderProvider() {
		return PROVIDER;
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<MatriarchArmor>("idle", 0, test -> test.setAndContinue(IDLE)));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}
}
