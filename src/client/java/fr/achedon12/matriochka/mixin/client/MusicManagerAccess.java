package fr.achedon12.matriochka.mixin.client;

import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.client.sounds.MusicManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Lets the adaptive music fade the game's own track out quickly and bring the world theme back soon after. */
@Mixin(MusicManager.class)
public interface MusicManagerAccess {
	@Accessor("currentMusic")
	SoundInstance matriochka$current();

	@Accessor("currentGain")
	void matriochka$setGain(float gain);

	@Accessor("nextSongDelay")
	int matriochka$delay();

	@Accessor("nextSongDelay")
	void matriochka$setDelay(int ticks);
}
