package fr.achedon12.matriochka.mc;

import net.minecraft.world.entity.Display;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.animal.golem.IronGolem;
import net.minecraft.world.entity.monster.zombie.Husk;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.entity.npc.villager.Villager;

/** The vanilla entity types the mod spawns (versions/<mc>/): 26.2 and later list them in EntityTypes, 26.1 in EntityType. */
public final class McEntities {
	private McEntities() {}

	public static final EntityType<Husk> HUSK = net.minecraft.world.entity.EntityType.HUSK;
	public static final EntityType<IronGolem> IRON_GOLEM = net.minecraft.world.entity.EntityType.IRON_GOLEM;
	public static final EntityType<Display.ItemDisplay> ITEM_DISPLAY = net.minecraft.world.entity.EntityType.ITEM_DISPLAY;
	public static final EntityType<LightningBolt> LIGHTNING_BOLT = net.minecraft.world.entity.EntityType.LIGHTNING_BOLT;
	public static final EntityType<Display.TextDisplay> TEXT_DISPLAY = net.minecraft.world.entity.EntityType.TEXT_DISPLAY;
	public static final EntityType<Villager> VILLAGER = net.minecraft.world.entity.EntityType.VILLAGER;
	public static final EntityType<Zombie> ZOMBIE = net.minecraft.world.entity.EntityType.ZOMBIE;
}
