package fr.achedon12.matriochka.item;

import net.minecraft.world.inventory.tooltip.TooltipComponent;

/**
 * The strip of icons under a Matriochka item's name (drawn by client/ItemTipClient): the world it comes from, its
 * rarity and the souls it is worth (or holds, for a soul vessel). world 0: none.
 */
public record ItemTip(int world, String rarity, int souls, boolean holds) implements TooltipComponent {}
