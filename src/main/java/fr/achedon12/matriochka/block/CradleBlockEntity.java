package fr.achedon12.matriochka.block;

import com.geckolib.animatable.GeoBlockEntity;
import com.geckolib.animatable.instance.AnimatableInstanceCache;
import com.geckolib.animatable.manager.AnimatableManager;
import com.geckolib.animation.AnimationController;
import com.geckolib.animation.RawAnimation;
import com.geckolib.util.GeckoLibUtil;
import fr.achedon12.matriochka.content.ModContent;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The Nesting Cradle's block entity: its state is the cradle's data (the ores set, when the ritual began, see
 * {@link NestingCradle}), sent to the clients, and its picture a GeckoLib model animated from that state
 * (tools/cradle_geo.py): the idle doll, or the ritual from its start tick; and for every world a socket on the
 * ring, dark while empty, lit in the world's colour once its ore is set (with a rise the first time).
 */
public class CradleBlockEntity extends DataBlockEntity implements GeoBlockEntity {
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("idle");
	private static final RawAnimation RITUAL = RawAnimation.begin().thenPlayAndHold("ritual");
	private static final RawAnimation[] ON = new RawAnimation[11], LIT = new RawAnimation[11], OFF = new RawAnimation[11];

	static {
		for (int w = 1; w <= 10; w++) {
			ON[w] = RawAnimation.begin().thenPlay("slot." + w + ".on").thenLoop("slot." + w + ".lit");
			LIT[w] = RawAnimation.begin().thenLoop("slot." + w + ".lit");
			OFF[w] = RawAnimation.begin().thenLoop("slot." + w + ".off");
		}
	}

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

	public CradleBlockEntity(BlockPos pos, BlockState state) {
		super(ModContent.BE_CRADLE, pos, state);
	}

	/** Whether the ritual is under way here, on whichever side asks. */
	public boolean ritualRunning() {
		long start = NestingCradle.start(this);
		return start > 0 && level != null && level.getGameTime() >= start;
	}

	private boolean filled(int w) {
		for (int o : NestingCradle.ores(this)) if (o == w) return true;
		return false;
	}

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<CradleBlockEntity>("main", 2, test -> test.setAndContinue(test.animatable().ritualRunning() ? RITUAL : IDLE)));
		for (int w = 1; w <= 10; w++) {
			final int slot = w;
			controllers.add(new AnimationController<CradleBlockEntity>("slot" + w, 0, test -> {
				CradleBlockEntity be = test.animatable();
				if (!be.filled(slot)) return test.setAndContinue(OFF[slot]);
				// an ore just set rises into its socket; one found already set (a chunk loaded) is simply lit
				if (test.isCurrentAnimation(ON[slot])) return test.setAndContinue(ON[slot]);
				long set = be.data().getLongOr("set_" + slot, 0L);
				boolean fresh = be.level != null && be.level.getGameTime() - set < NestingCradle.RISE;
				return test.setAndContinue(fresh ? ON[slot] : LIT[slot]);
			}));
		}
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return cache;
	}

	/** The cradle's state goes to the clients, for its animation. */
	@Override
	public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getUpdatePacket() {
		return net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket.create(this);
	}

	@Override
	public CompoundTag getUpdateTag(net.minecraft.core.HolderLookup.Provider registries) {
		CompoundTag out = new CompoundTag();
		out.put("mdata", data.copy());
		return out;
	}
}
