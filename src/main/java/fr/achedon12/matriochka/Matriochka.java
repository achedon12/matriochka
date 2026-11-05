package fr.achedon12.matriochka;

import fr.achedon12.matriochka.command.MatrioCommand;
import fr.achedon12.matriochka.content.ModContent;
import fr.achedon12.matriochka.gear.GearClasses;
import fr.achedon12.matriochka.net.Net;
import fr.achedon12.matriochka.rules.PlayerState;
import fr.achedon12.matriochka.structure.ProceduralStructure;
import fr.achedon12.matriochka.world.Config;
import fr.achedon12.matriochka.world.Events;
import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Matriochka: every block can hold a world. */
public class Matriochka implements ModInitializer {
	public static final String MOD_ID = "matriochka";
	public static final Logger LOG = LoggerFactory.getLogger(MOD_ID);

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}

	@Override
	public void onInitialize() {
		Config.load();
		fr.achedon12.matriochka.content.Sounds.init();
		fr.achedon12.matriochka.content.Particles.init();
		GearClasses.init();
		fr.achedon12.matriochka.rules.Snorkel.init();
		PlayerState.init();
		ModContent.register();
		ProceduralStructure.init();
		Net.init();
		fr.achedon12.matriochka.net.Cues.init();
		Events.init();
		MatrioCommand.init();
		fr.achedon12.matriochka.rules.MovingWorlds.init();
		fr.achedon12.matriochka.world.Refuge.init();
		fr.achedon12.matriochka.item.Drill.init();
		fr.achedon12.matriochka.world.Karma.init();
		fr.achedon12.matriochka.world.QuestHooks.init();
		fr.achedon12.matriochka.world.Tutorial.init();
		fr.achedon12.matriochka.compat.MapCompat.init();
		fr.achedon12.matriochka.replay.Replay.init();
		LOG.info("Matriochka loaded: 10 worlds, {} creatures, {} bosses.", fr.achedon12.matriochka.content.Content.MOBS.size(), fr.achedon12.matriochka.content.Content.BOSSES.size());
	}
}
