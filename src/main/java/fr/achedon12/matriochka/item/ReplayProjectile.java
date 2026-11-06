package fr.achedon12.matriochka.item;

import fr.achedon12.matriochka.content.Defs;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.entity.MatrioBoss;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * A thrown Storm Javelin or Tide Harpoon. The javelin calls lightning where it strikes; the harpoon drags what it hits
 * back to the thrower, harder under water. Either way the weapon comes home to its thrower's inventory, one point worse.
 */
public class ReplayProjectile extends ThrowableItemProjectile {
	public ReplayProjectile(EntityType<? extends ReplayProjectile> type, Level level) {
		super(type, level);
	}

	public ReplayProjectile(Level level, LivingEntity owner, ItemStack stack) {
		super(ReplayGear.THROWN, owner, level, stack);
	}

	@Override
	protected Item getDefaultItem() {
		return ModContent.item("storm_javelin");
	}

	private boolean harpoon() {
		return getItem().is(ModContent.item("tide_harpoon"));
	}

	private float damage() {
		var def = ModContent.def(ModContent.idOf(getItem().getItem()));
		return def == null ? 8f : Defs.GEAR[Math.max(1, Math.min(10, def.world()))][0];
	}

	@Override
	public void tick() {
		super.tick();
		if (level() instanceof ServerLevel sl) {
			// the trail starts a little way out, not in the thrower's face
			if (tickCount > 2) {
				if (!harpoon()) sl.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY(), getZ(), 2, 0.05, 0.05, 0.05, 0);
				else if (isInWater()) sl.sendParticles(ParticleTypes.BUBBLE, getX(), getY(), getZ(), 2, 0.05, 0.05, 0.05, 0);
				else sl.sendParticles(ParticleTypes.SPLASH, getX(), getY(), getZ(), 2, 0.05, 0.05, 0.05, 0);
			}
			if (harpoon() && tickCount % 2 == 0 && getOwner() != null) line(sl, getOwner(), position(), 0.7);
			// lost in the void or flown too far: it comes back anyway
			if (tickCount > 200 || getY() < level().getMinY()) home(sl, position());
		}
	}

	@Override
	protected void onHitEntity(EntityHitResult hit) {
		super.onHitEntity(hit);
		if (!(level() instanceof ServerLevel sl)) return;
		Entity target = hit.getEntity();
		Entity owner = getOwner();
		if (target == owner) return;
		target.hurtServer(sl, damageSources().thrown(this, owner), damage());
		if (harpoon()) {
			if (owner != null && target instanceof LivingEntity le && !(le instanceof MatrioBoss)) {
				double pull = le.isInWater() ? 1.8 : 1.1;
				le.setDeltaMovement(owner.position().subtract(le.position()).normalize().scale(pull).add(0, 0.3, 0));
				le.needsSync = true;
				if (owner instanceof ServerPlayer sp) Hooked.mark(le, sp, sl.getGameTime());
			}
			if (owner != null) line(sl, owner, target.position().add(0, target.getBbHeight() * 0.6, 0), 0.4);
			sl.playSound(null, blockPosition(), SoundEvents.FISHING_BOBBER_RETRIEVE, SoundSource.PLAYERS, 1f, 0.7f);
		} else {
			bolt(sl, target.position());
		}
	}

	@Override
	protected void onHitBlock(BlockHitResult hit) {
		super.onHitBlock(hit);
		if (level() instanceof ServerLevel sl && !harpoon()) bolt(sl, hit.getLocation());
	}

	@Override
	protected void onHit(HitResult hit) {
		super.onHit(hit);
		if (level() instanceof ServerLevel sl && hit.getType() != HitResult.Type.MISS) home(sl, hit.getLocation());
	}

	/** The harpoon's line: pale cord from the thrower's hand to a point, one fleck every step blocks. */
	private static void line(ServerLevel level, Entity owner, Vec3 to, double step) {
		Vec3 from = owner.getEyePosition().add(0, -0.45, 0).add(owner.getLookAngle().scale(0.6));
		Vec3 d = to.subtract(from);
		double len = d.length();
		if (len < 1.2) return;
		var cord = new net.minecraft.core.particles.DustParticleOptions(0xD9CBA3, 0.55f);
		// the first stretch stays clear of the thrower's view
		for (double k = 1.0; k < len; k += step) {
			Vec3 at = from.add(d.scale(k / len));
			level.sendParticles(cord, at.x, at.y, at.z, 1, 0, 0, 0, 0);
		}
	}

	private void bolt(ServerLevel level, Vec3 at) {
		LightningBolt bolt = net.minecraft.world.entity.EntityTypes.LIGHTNING_BOLT.create(level, EntitySpawnReason.TRIGGERED);
		if (bolt == null) return;
		bolt.setPos(at);
		if (getOwner() instanceof ServerPlayer sp) bolt.setCause(sp);
		level.addFreshEntity(bolt);
	}

	/** Back to the thrower: into their inventory, at their feet if it is full, where it fell if they are gone. */
	private void home(ServerLevel level, Vec3 at) {
		if (isRemoved()) return;
		ItemStack stack = getItem().copy();
		discard();
		if (stack.isEmpty()) return;
		if (stack.isDamageableItem()) {
			stack.setDamageValue(stack.getDamageValue() + 1);
			if (stack.getDamageValue() >= stack.getMaxDamage()) {
				level.playSound(null, blockPosition(), SoundEvents.ITEM_BREAK.value(), SoundSource.PLAYERS, 1f, 1f);
				return;
			}
		}
		if (getOwner() instanceof ServerPlayer sp && sp.isAlive() && sp.level() == level) {
			level.playSound(null, sp.blockPosition(), SoundEvents.TRIDENT_RETURN, SoundSource.PLAYERS, 1f, harpoon() ? 0.8f : 1.2f);
			if (!sp.getInventory().add(stack)) sp.spawnAtLocation(level, stack);
			return;
		}
		level.addFreshEntity(new ItemEntity(level, at.x, at.y, at.z, stack));
	}
}
