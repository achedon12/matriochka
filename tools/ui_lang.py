"""Hand-written interface strings (English / French). Merged into the lang files by gen.py."""
import json, os
U = {
 "hud.matriochka.world": ("World %s", "Monde %s"),
 "hud.matriochka.souls": ("%s souls", "%s âmes"),
 "journal.matriochka.previous": ("Back", "Retour"),
 "journal.matriochka.next": ("Next", "Suite"),
 "journal.matriochka.doll_short": ("Doll of Life", "Poupée de vie"),
 "tooltip.matriochka.world": ("World %s", "Monde %s"),
 "tooltip.matriochka.class": ("Class: %s (level %s)", "Classe : %s (niveau %s)"),
 "item.matriochka.journal_page.n": ("Journal Page — World %s, page %s", "Page du Journal — monde %s, page %s"),
 "hud.matriochka.souls_karma": ("%s souls · karma %s", "%s âmes · karma %s"),
 "journal.matriochka.tab.objective": ("Objective", "Objectif"), "journal.matriochka.tab.quests": ("Quests", "Quêtes"),
 "journal.matriochka.tab.karma": ("Karma", "Karma"), "journal.matriochka.tab.worlds": ("Worlds", "Mondes"), "journal.matriochka.tab.scroll": ("Scroll", "Parchemin"),
 "journal.matriochka.objective.guardian": ("Follow the sketch: the Guardian's Sanctuary lies a few hundred blocks from where you woke. Use its altar.", "Suis le croquis : le Sanctuaire du Gardien se trouve à quelques centaines de blocs de ton réveil. Active son autel."),
 "journal.matriochka.objective.next": ("Craft the way into World %s at the Matrix Workbench and perform its rite: its description says where it goes and what it waits for.", "Fabrique de quoi ouvrir le monde %s à l'Établi matriciel et accomplis son rite : sa description dit où le poser et ce qu'il attend."),
 "journal.matriochka.hint.guardian.1": ("A hint: the Sanctuary is a ring of stone pillars round an altar, on open ground. Climb a hill and look for the pillars; the Scroll's sketch shows its shape.", "Un indice : le Sanctuaire est un cercle de piliers de pierre autour d'un autel, en terrain découvert. Monte sur une colline et cherche les piliers ; le croquis du Parchemin en montre la forme."),
 "journal.matriochka.hint.guardian.2": ("Still lost? Walk in a widening spiral from where you woke: it is never more than a few hundred blocks away. On a server, an operator can find it with /locate structure matriochka:guardian_sanctuary.", "Toujours perdu ? Marche en spirale qui s'élargit depuis ton réveil : il n'est jamais à plus de quelques centaines de blocs. Sur un serveur, un opérateur peut le trouver avec /locate structure matriochka:guardian_sanctuary."),
 "journal.matriochka.hint.rite": ("A hint for World %s: %s", "Un indice pour le monde %s : %s"),
 "journal.matriochka.hint.recipe": ("At the Matrix Workbench, the way into World %s takes: %s.", "À l'Établi matriciel, l'ouverture du monde %s demande : %s."),
 "journal.matriochka.card.craft": ("Made at the %s", "Fabriqué à : %s"),
 "journal.matriochka.card.drop": ("Dropped by the %s", "Lâché par : %s"),
 "journal.matriochka.card.rare_drop": ("Rarely dropped by the %s", "Lâché rarement par : %s"),
 "journal.matriochka.card.boss": ("Left by %s", "Laissé par : %s"),
 "journal.matriochka.card.ore": ("Mined from %s", "Extrait de : %s"),
 "journal.matriochka.card.chest.common": ("Found in the world's chests", "Trouvé dans les coffres du monde"),
 "journal.matriochka.card.chest.rare": ("Found in the world's rare chests", "Trouvé dans les coffres rares du monde"),
 "journal.matriochka.card.chest.vault": ("Found in the world's vault chests", "Trouvé dans les coffres au trésor du monde"),
 "journal.matriochka.card.other": ("Given by the world's story or quests", "Donné par l'histoire ou les quêtes du monde"),
 "journal.matriochka.card.back": ("Worlds", "Mondes"),
 "journal.matriochka.card.hint": ("Click a world for its card: every item and how to get it.", "Clique un monde pour sa fiche : chaque objet et comment l'obtenir."),
 "journal.matriochka.card.wonder_key": ("Found in %s, the world's wonder", "Trouvée dans %s, la merveille du monde"),
 "journal.matriochka.card.reliquary": ("Sealed in the reliquary of %s: the cross key of World %s opens it", "Scellée dans le reliquaire de %s : la clé croisée du monde %s l'ouvre"),
 "message.matriochka.reliquary.needs": ("Sealed. The cross key of World %s opens it.", "Scellé. La clé croisée du monde %s l'ouvre."),
 "message.matriochka.reliquary.empty": ("You have already taken this reliquary's relic.", "Tu as déjà pris la relique de ce reliquaire."),
 "message.matriochka.reliquary.opened": ("The reliquary opens: %s.", "Le reliquaire s'ouvre : %s."),
 "message.matriochka.relic.known": ("You already carry this relic's strength.", "Tu portes déjà la force de cette relique."),
 "message.matriochka.relic.taken": ("One more heart and the gift of its world, for good. Relics taken in: %s / 10.", "Un cœur de plus et le don de son monde, pour toujours. Reliques intégrées : %s / 10."),
 "message.matriochka.relic.all": ("The ten relics are yours: every wonder has given up its secret, and together they guard you (+4 armour).", "Les dix reliques sont à toi : chaque merveille a livré son secret, et ensemble elles te protègent (+4 armure)."),
 "journal.matriochka.objective.end": ("The ten prisons are open. The Unfinished is gone, or is it you?", "Les dix prisons sont ouvertes. L'Inachevée a disparu, ou est-ce toi ?"),
 "journal.matriochka.doll": ("Doll of Life: %s / %s layers", "Poupée de vie : %s / %s couches"),
 "journal.matriochka.group": ("Group: %s player(s)", "Groupe : %s joueur(s)"),
 "journal.matriochka.pages": ("Journal pages found: %s / 50", "Pages du Journal trouvées : %s / 50"),
 "journal.matriochka.surface": ("The Surface", "La Surface"),
 "journal.matriochka.locked": ("Open the previous world first.", "Ouvre d'abord le monde précédent."),
 "journal.matriochka.help": ("Help", "Aider"), "journal.matriochka.betray": ("Betray", "Trahir"),
 "journal.matriochka.karma": ("Karma: %s", "Karma : %s"), "journal.matriochka.souls": ("Souls: %s", "Âmes : %s"),
 "journal.matriochka.karma.light2": ("The peoples welcome you. Mutual-help quests open up and the brighter world variants answer you.", "Les peuples t'accueillent. Les quêtes d'entraide s'ouvrent et les variantes lumineuses des mondes te répondent."),
 "journal.matriochka.karma.light1": ("Prices are 10% lower. People trust you.", "Les prix baissent de 10 %. On te fait confiance."),
 "journal.matriochka.karma.neutral": ("Neither saint nor devourer. Every choice still counts.", "Ni saint ni dévoreur. Chaque choix compte encore."),
 "journal.matriochka.karma.dark1": ("Prices are 10% higher, but the first black market opens to you.", "Les prix montent de 10 %, mais le premier marché clandestin s'ouvre à toi."),
 "journal.matriochka.karma.dark2": ("Some villages turn hostile. Pact quests and forbidden loot await.", "Certains villages deviennent hostiles. Quêtes de pacte et butins interdits t'attendent."),
 "station.matriochka.grid.fill": ("Pick a drawer, or lay it out", "Choisis un tiroir ou pose les objets"),
 "station.matriochka.grid.take": ("Take it", "Prends-le"),
 "station.matriochka.ready": ("Ready", "Prête"), "station.matriochka.not_ready": ("Not ready", "Pas prête"),
 "station.matriochka.purify": ("Purify (+karma)", "Purifier (+karma)"), "station.matriochka.devour": ("Devour (-karma)", "Dévorer (-karma)"),
 "station.matriochka.recharge": ("Rebuild a layer", "Refaire une couche"),
 "station.matriochka.upgrade": ("Upgrade class", "Améliorer la classe"), "station.matriochka.reroll": ("Reroll (Chance Doll)", "Relancer (Poupée du hasard)"),
 "station.matriochka.soul_altar.help": ("Place an item. Purify it to free its soul and gain karma, or devour it to absorb its soul and lose karma. Both choices are final. A Doll of Life layer costs 50 souls and 4 rare resources of the current world.", "Pose un objet. Purifie-le pour libérer son âme et gagner du karma, ou dévore-le pour absorber son âme et perdre du karma. Les deux choix sont définitifs. Une couche de Poupée de vie coûte 50 âmes et 4 ressources rares du monde en cours."),
 "station.matriochka.class_table.help": ("Place a weapon, tool or armor piece. Level 2: 10 souls, 3: 30, 4: 90, 5: 270, and 1, 1, 2, 2 Shell Shards. Your progression caps the level. Armor takes Lacquer Layers.", "Pose une arme, un outil ou une pièce d'armure. Niveau 2 : 10 âmes, 3 : 30, 4 : 90, 5 : 270, et 1, 1, 2, 2 Éclats d'enveloppe. Ta progression limite le niveau. L'armure reçoit des Couches laquées."),
 "station.matriochka.layer": ("Add a layer", "Ajouter une couche"),
 "tooltip.matriochka.layers": ("Layers: %s / %s (outer %s%%)", "Couches : %s / %s (extérieure %s %%)"),
 "message.matriochka.layer.need": ("You need a Lacquer Layer.", "Il te faut une Couche laquée."),
 "message.matriochka.layer.not_armor": ("Only armor can take layers.", "Seule une armure peut recevoir des couches."),
 "message.matriochka.layer.full": ("This piece holds no more layers. Its class level or a Guardian class would let it hold more.", "Cette pièce ne peut plus recevoir de couche. Un niveau de classe plus haut ou la classe Gardien lui en permettrait davantage."),
 "message.matriochka.layer.broke": ("A layer of your armor breaks. %s left beneath.", "Une couche de ton armure se brise. Il en reste %s dessous."),
 "message.matriochka.layer.last": ("The last layer breaks: the armor itself takes the blows now.", "La dernière couche se brise : l'armure encaisse elle-même les coups désormais."),
 "message.matriochka.class.need_shard": ("This upgrade also needs Shell Shards, left by fallen bosses.", "Cette amélioration demande aussi des Éclats d'enveloppe, laissés par les boss vaincus."),
 "message.matriochka.dodge": ("Dodged", "Esquivé"),
 "message.matriochka.no_beds": ("Beds do not work inside a world. Use a Soul Cradle.", "Les lits ne fonctionnent pas dans un monde. Utilise un Berceau d'âme."),
 "message.matriochka.no_dimension": ("This world could not be loaded.", "Ce monde n'a pas pu être chargé."),
 "message.matriochka.entered": ("You shrink into %s.", "Tu rétrécis dans %s."),
 "message.matriochka.not_in_world": ("You are not inside a world.", "Tu n'es pas dans un monde."),
 "message.matriochka.wrong_soil": ("This Seed needs tilled World Soil %s.", "Cette Graine demande une Terre de monde %s bêchée."),
 "message.matriochka.not_unlocked": ("Your group has not defeated the boss of world %s yet.", "Ton groupe n'a pas encore vaincu le boss du monde %s."),
 "message.matriochka.not_your_world": ("This world belongs to another group.", "Ce monde appartient à un autre groupe."),
 "message.matriochka.cradle_set": ("Soul Cradle set: %s charges.", "Berceau d'âme posé : %s charges."),
 "message.matriochka.cradle_charges": ("Soul Cradle: %s charges.", "Berceau d'âme : %s charges."),
 "message.matriochka.cradle_boss": ("A boss is awake near your cradle: it stays shut.", "Un boss est éveillé près de ton berceau : il reste fermé."),
 "message.matriochka.not_yours": ("This belongs to another group.", "Ceci appartient à un autre groupe."),
 "message.matriochka.world_exists": ("Your group already has a World Block for world %s: break it first.", "Ton groupe a déjà un Bloc-monde pour le monde %s : casse-le d'abord."),
 "message.matriochka.cradle_used": ("The cradle's doll opens. %s charges left.", "La poupée du berceau s'ouvre. Il reste %s charges."),
 "message.matriochka.death_chest": ("Your belongings wait in a death chest at %s %s %s.", "Tes affaires t'attendent dans un coffre de mort en %s %s %s."),
 "message.matriochka.doll_broke": ("A layer of your doll breaks. %s left.", "Une couche de ta poupée se brise. Il en reste %s."),
 "message.matriochka.boss_already": ("A boss is already awake here.", "Un boss est déjà éveillé ici."),
 "message.matriochka.guardian_done": ("The Guardian was already defeated. Sneak to wake it anyway.", "Le Gardien est déjà vaincu. Accroupis-toi pour le réveiller quand même."),
 "message.matriochka.offering.needed": ("The altar stays cold. It wants an offering to wake its boss (%s): %s.", "L'autel reste froid. Il réclame une offrande pour réveiller son boss (%s) : %s."),
 "message.matriochka.offering.accepted": ("The altar takes your %s. The ritual begins...", "L'autel prend ton offrande : %s. Le rituel commence..."),
 "message.matriochka.offering.busy": ("The ritual is already under way.", "Le rituel est déjà en cours."),
 "message.matriochka.lair.wake": ("%s awakens in its lair.", "%s s'éveille dans son antre."),
 "message.matriochka.lair.quiet": ("The lair is quiet. It stirs again in %s min.", "L'antre est calme. Il s'éveillera de nouveau dans %s min."),
 "message.matriochka.lair.treasure": ("The seal of the treasure alcove breaks open.", "Le sceau de l'alcôve au trésor se brise."),
 "message.matriochka.lair.sealed": ("The portcullis falls behind you.", "La herse tombe derrière toi."),
 "message.matriochka.lair.rearmed": ("Something stirs again in the lair.", "Quelque chose remue de nouveau dans l'antre."),
 "command.matriochka.lair.rearmed": ("Lair heart re-armed at %s %s %s.", "Cœur d'antre réarmé en %s %s %s."),
 "command.matriochka.lair.none": ("No lair in this parcel.", "Aucun antre dans cette parcelle."),
 "message.matriochka.quest_done":("Quest complete: %s", "Quête terminée : %s"),
 "message.matriochka.page_found": ("Journal page found: world %s, page %s.", "Page du Journal trouvée : monde %s, page %s."),
 "message.matriochka.border": ("The edge of your parcel. The doll holds you back.", "Le bord de ta parcelle. La poupée te retient."),
 "message.matriochka.npc_hostile": ("They turn away from you. Your karma precedes you.", "On se détourne de toi. Ton karma te précède."),
 "message.matriochka.shell": ("Shell %s breaks: it wears the face of %s.", "L'enveloppe %s se brise : elle prend le visage de %s."),
 "message.matriochka.map.none": ("No unexplored structure nearby.", "Aucune structure inexplorée à proximité."),
 "message.matriochka.map.found": ("%s, %s blocks to the %s.", "%s, à %s blocs vers %s."),
 "message.matriochka.dir.north": ("north", "le nord"), "message.matriochka.dir.south": ("south", "le sud"),
 "message.matriochka.dir.east": ("east", "l'est"), "message.matriochka.dir.west": ("west", "l'ouest"),
 "message.matriochka.gate.enchant": ("The runes stay silent. Finish World 2 first.", "Les runes restent muettes. Termine d'abord le monde 2."),
 "message.matriochka.gate.nether": ("The portal rejects you. The Nether opens after World 2.", "Le portail te rejette. Le Nether s'ouvre après le monde 2."),
 "message.matriochka.gate.end": ("The portal rejects you. The End opens after World 8.", "Le portail te rejette. L'End s'ouvre après le monde 8."),
 "message.matriochka.rule.halls": ("The halls are about to move...", "Les salles vont bouger..."),
 "message.matriochka.rule.gust": ("A gust is coming. Crouch or take shelter.", "Une rafale arrive. Accroupis-toi ou abrite-toi."),
 "message.matriochka.rule.lightning": ("Lightning is gathering near you.", "La foudre se concentre près de toi."),
 "message.matriochka.rule.gravity": ("Gravity is about to flip.", "La gravité va s'inverser."),
 "message.matriochka.rule.pressure": ("The pressure crushes you. Climb, or dive with a diving suit and a stronger snorkel helmet.", "La pression t'écrase. Remonte, ou plonge avec un scaphandre et un casque-tuba plus solide."),
 # World 7: snorkel helmets
 "hud.matriochka.tank": ("Tank", "Réserve"),
 "tooltip.matriochka.tank": ("Tank: %s:%s of %s min (%s%%)", "Réserve : %s:%s sur %s min (%s %%)"),
 "tooltip.matriochka.snorkel_tier": ("Tier %s · dives %s blocks deeper", "Rang %s · plonge %s blocs plus bas"),
 "station.matriochka.refill": ("Refill", "Remplir"),
 "message.matriochka.snorkel.low": ("Your helmet's tank is running low.", "La réserve de ton casque s'épuise."),
 "message.matriochka.snorkel.empty": ("Your helmet's tank is empty. Hold your breath and find air.", "La réserve de ton casque est vide. Retiens ton souffle et trouve de l'air."),
 "message.matriochka.snorkel.cracked": ("Your snorkel helmet is cracking.", "Ton casque-tuba se fissure."),
 "message.matriochka.snorkel.refilled": ("The press fills your helmet's tank.", "La presse remplit la réserve de ton casque."),
 "message.matriochka.snorkel.none": ("You carry no snorkel helmet to refill.", "Tu ne portes aucun casque-tuba à remplir."),
 "message.matriochka.snorkel.full": ("Your helmet's tank is already full.", "La réserve de ton casque est déjà pleine."),
 "message.matriochka.rule.tremor": ("The ground is about to move.", "Le sol va bouger."),
 "message.matriochka.rule.halls_moved": ("The halls have moved around you.", "Les salles ont bougé autour de toi."),
 "message.matriochka.rule.burnout": ("A light you brought gutters out. Here only the Solar Lantern and the Deep's own glow last.",
                                     "Une lumière que tu as apportée s'éteint. Ici, seules la Lanterne solaire et la lueur des profondeurs durent."),
 "message.matriochka.rule.flipped": ("Up is down here. You fall toward the sky.", "Ici, le haut est en bas. Tu tombes vers le ciel."),
 "message.matriochka.rule.ground_moved": ("The ground carries you along.", "Le sol t'emporte avec lui."),
 "message.matriochka.rule.ground_held": ("Your anchor holds the ground still.", "Ton ancre retient le sol."),
 "message.matriochka.station.unknown": ("Unknown recipe.", "Recette inconnue."),
 "message.matriochka.station.locked": ("Defeat the previous boss to unlock this recipe.", "Bats le boss précédent pour débloquer cette recette."),
 "message.matriochka.station.missing": ("Missing ingredients.", "Ingrédients manquants."),
 "message.matriochka.station.ferment": ("The vat needs one more minute of fermentation.", "La cuve doit encore fermenter une minute."),
 "message.matriochka.altar.empty": ("Place an item on the altar.", "Pose un objet sur l'autel."),
 "message.matriochka.altar.refuse": ("Cores and dolls cannot be purified or devoured.", "Les noyaux et les poupées ne peuvent être ni purifiés ni dévorés."),
 "message.matriochka.altar.purified": ("Purified: %s souls freed. Karma %s.", "Purifié : %s âmes libérées. Karma %s."),
 "message.matriochka.altar.devoured": ("Devoured: %s souls absorbed. Karma %s.", "Dévoré : %s âmes absorbées. Karma %s."),
 "message.matriochka.altar.no_doll": ("You do not carry a Doll of Life yet.", "Tu ne portes pas encore de Poupée de vie."),
 "message.matriochka.altar.doll_full": ("Your doll is whole.", "Ta poupée est intacte."),
 "message.matriochka.altar.no_souls": ("Not enough souls.", "Pas assez d'âmes."),
 "message.matriochka.class.no_class": ("This item cannot hold a class.", "Cet objet ne peut pas recevoir de classe."),
 "message.matriochka.class.max": ("Maximum level reached.", "Niveau maximal atteint."),
 "message.matriochka.class.progress": ("Your progression does not allow a higher level yet.", "Ta progression ne permet pas encore un niveau supérieur."),
 "message.matriochka.class.single": ("Tools have a single class; there is nothing to reroll.", "Les outils n'ont qu'une classe : rien à relancer."),
 "message.matriochka.class.need_doll": ("You need a Chance Doll.", "Il te faut une Poupée du hasard."),
 "message.matriochka.refuge.locked": ("The doll stays shut. It opens once your group has beaten the Grand Jailer.", "La poupée reste fermée. Elle s'ouvre quand ton groupe a vaincu le Grand Geôlier."),
 "message.matriochka.refuge.boss": ("A boss is awake nearby: the refuge doll will not open.", "Un boss est éveillé tout près : la poupée-refuge ne s'ouvre pas."),
 "message.matriochka.refuge.entered": ("You slip inside the refuge doll.", "Tu te glisses dans la poupée-refuge."),
 "message.matriochka.refuge.grown": ("Your refuge has grown: the walls moved back to make room.", "Ton refuge a grandi : les murs ont reculé pour faire de la place."),
 "message.matriochka.nesting.rule": ("This chest now sorts: %s", "Ce coffre trie désormais : %s"),
 "tooltip.matriochka.nesting.holds": ("%s / %s stacks inside", "%s / %s piles à l'intérieur"),
 "tooltip.matriochka.nesting.rule": ("Sorts: %s", "Trie : %s"),
 "nesting.matriochka.rule.any": ("nothing (holds anything)", "rien (accepte tout)"),
 "nesting.matriochka.rule.blocks": ("blocks", "les blocs"),
 "nesting.matriochka.rule.gear": ("tools, weapons and armor", "outils, armes et armures"),
 "nesting.matriochka.rule.food": ("food", "la nourriture"),
 "nesting.matriochka.rule.resources": ("resources", "les ressources"),
 "message.matriochka.drill.empty": ("The drill is out of Blazing Rock: it mines one block at a time.", "La foreuse n'a plus de Roche ardente : elle mine un bloc à la fois."),
 "tooltip.matriochka.drill.fuel": ("Fuel: %s / %s squares (1 Blazing Rock fills it)", "Combustible : %s / %s carrés (1 Roche ardente le remplit)"),
 "tooltip.matriochka.drill.sneak": ("Sneak to mine a single block.", "Accroupis-toi pour miner un seul bloc."),
 "station.matriochka.invert": ("Invert", "Inverser"),
 "jei.matriochka.requires": ("Opens after %s", "Débloquée après %s"),
 "station.matriochka.inverter.help": ("Two pieces of the same kind trade class, level and enchantments. Each loses a quarter of its durability.", "Deux pièces du même type échangent classe, niveau et enchantements. Chacune perd un quart de sa durabilité."),
 "station.matriochka.ferment.fresh": ("Fresh", "Jeune"), "station.matriochka.ferment.ripe": ("Ripe", "Mûre"), "station.matriochka.ferment.aged": ("Aged", "Vieillie"),
 "message.matriochka.station.vat_bonus": ("The brew had time to ferment: %s more.", "La cuvée a eu le temps de fermenter : %s de plus."),
 "message.matriochka.station.forge_fed": ("The essence crackles into the forge. Charge: %s.", "L'essence crépite dans la forge. Charge : %s."),
 "message.matriochka.inverter.empty": ("Place two pieces of gear in the sockets.", "Pose deux pièces d'équipement dans les emplacements."),
 "message.matriochka.inverter.mismatch": ("Both pieces must be of the same kind: two armor pieces, two weapons or two tools.", "Les deux pièces doivent être du même type : deux armures, deux armes ou deux outils."),
 "message.matriochka.inverter.done": ("The pieces trade places in the mirror. Each paid a quarter of its durability.", "Les pièces échangent leur reflet. Chacune a payé un quart de sa durabilité."),
 "message.matriochka.inverter.done_lost": ("The pieces trade places in the mirror, but %s enchantment(s) found no hold and faded.", "Les pièces échangent leur reflet, mais %s enchantement(s) n'ont pas trouvé prise et se sont effacés."),
 "journal.matriochka.karma_paths": ("Karma Paths", "Voies de karma"),
 "journal.matriochka.locked_help": ("Opens at karma +50: the peoples ask for your help.", "S'ouvre à karma +50 : les peuples te demandent de l'aide."),
 "journal.matriochka.locked_pact": ("Opens at karma -50: someone in the dark offers a pact.", "S'ouvre à karma -50 : quelqu'un dans l'ombre te propose un pacte."),
 "message.matriochka.black_market": ("Under the counter, other goods wait for you.", "Sous le comptoir, d'autres marchandises t'attendent."),
 "message.matriochka.station.take_part": ("Your group beat this world's boss without you. Take part in its next fight to earn this gear.", "Ton groupe a vaincu le boss de ce monde sans toi. Participe à son prochain combat pour mériter cet équipement."),
 'command.matriochka.group.members': ('Members: %s. Leader: %s.', 'Membres : %s. Chef : %s.'),
 'command.matriochka.group.leader': ("Your group's leader is %s.", 'Le chef de ton groupe est %s.'),
 'command.matriochka.group.not_leader': ("Only the group's leader can do that.", 'Seul le chef du groupe peut faire cela.'),
 'command.matriochka.group.not_member': ('%s is not in your group.', "%s n'est pas dans ton groupe."),
 'command.matriochka.group.kicked': ('%s is no longer in the group.', '%s ne fait plus partie du groupe.'),
 'command.matriochka.group.kicked_you': ("%s sent you out of the group. You keep your gear, quests and achievements, not the group's worlds.", "%s t'a exclu du groupe. Tu gardes ton équipement, tes quêtes et tes succès, pas les mondes du groupe."),
 'command.matriochka.group.transferred': ('%s now leads the group.', '%s dirige désormais le groupe.'),
 'command.matriochka.group.lead_given': ('You now lead your group.', 'Tu diriges désormais ton groupe.'),
 'command.matriochka.group.disbanded': ('The group is disbanded. Its worlds are kept for 30 days.', 'Le groupe est dissous. Ses mondes sont conservés 30 jours.'),
 'command.matriochka.progression.show': ('%s: highest boss beaten %s (bits %s).', '%s : plus haut boss vaincu %s (bits %s).'),
 'command.matriochka.world.none': ('No world has been opened yet.', "Aucun monde n'a encore été ouvert."),
 'command.matriochka.world.group': ('Group %s, leader %s, %s member(s), %s, parcel %s', 'Groupe %s, chef %s, %s membre(s), %s, parcelle %s'),
 'command.matriochka.world.state.active': ('active', 'actif'),
 'command.matriochka.world.state.disbanded': ('disbanded', 'dissous'),
 'command.matriochka.world.state.expired': ('disbanded over 30 days ago, may be reset', 'dissous depuis plus de 30 jours, réinitialisable'),
 'command.matriochka.world.entry': ('  World %s: block %s, parcel %s, %s', '  Monde %s : bloc %s, parcelle %s, %s'),
 'command.matriochka.world.beaten': ('boss beaten', 'boss vaincu'),
 'command.matriochka.world.not_beaten': ('boss standing', 'boss invaincu'),
 'command.matriochka.world.repaired': ('World %s: Threshold and boss stage rebuilt.', 'Monde %s : Seuil et scène du boss reconstruits.'),
 'command.matriochka.world.unknown': ('That group has never entered world %s.', "Ce groupe n'est jamais entré dans le monde %s."),
 'command.matriochka.world.moved': ('World %s: its World Block now stands at %s %s %s.', 'Monde %s : son Bloc-monde se trouve désormais en %s %s %s.'),
 'command.matriochka.world.reset': ('World %s reset: a new parcel waits for the next opening.', 'Monde %s réinitialisé : une nouvelle parcelle attend la prochaine ouverture.'),
 'command.matriochka.boss.reset': ('The boss of world %s can be fought again.', 'Le boss du monde %s peut de nouveau être combattu.'),
 'message.matriochka.hardcore_dead': ('Hardcore: your death is final. You watch the worlds as a spectator now.', 'Hardcore : ta mort est définitive. Tu observes désormais les mondes en spectateur.'),
 'message.matriochka.world_deleted': ('Hardcore: World %s broke with its block. It is gone for your group; its rite would open a new one.', "Hardcore : le monde %s s'est brisé avec son bloc. Il est perdu pour ton groupe ; son rite en ouvrirait un nouveau."),
 "command.matriochka.group.info": ("Group: %s member(s), defeated bosses: %s", "Groupe : %s membre(s), boss vaincus : %s"),
 "command.matriochka.group.invited": ("%s invites you to their group. /matriochka group join", "%s t'invite dans son groupe. /matriochka group join"),
 "command.matriochka.group.invite_sent": ("Invitation sent to %s.", "Invitation envoyée à %s."),
 "command.matriochka.group.no_invite": ("No pending invitation.", "Aucune invitation en attente."),
 "command.matriochka.group.joined": ("You joined the group.", "Tu as rejoint le groupe."),
 "command.matriochka.group.full": ("That group is full.", "Ce groupe est complet."),
 "command.matriochka.group.left": ("You left the group.", "Tu as quitté le groupe."),
 "command.matriochka.progression.set": ("Progression set up to world %s.", "Progression réglée jusqu'au monde %s."),
 "command.matriochka.boss.unknown": ("Unknown boss: %s", "Boss inconnu : %s"),
 "command.matriochka.karma.show": ("Karma %s, souls %s.", "Karma %s, âmes %s."),
 "command.matriochka.debug": ("World %s, parcel %s, gauges %s, doll layers %s", "Monde %s, parcelle %s, jauges %s, couches %s"),
 # world variants, boss mutations
 "message.matriochka.variant.lean_calm": ("The world leans calm (%s).", "Le monde penche vers le calme (%s)."),
 "message.matriochka.variant.lean_wild": ("The world leans wild (%s).", "Le monde penche vers la sauvagerie (%s)."),
 "message.matriochka.variant.lean_none": ("The world hesitates.", "Le monde hésite."),
 "message.matriochka.variant.hatched": ("%s hatched as: %s.", "%s a éclos en : %s."),
 "journal.matriochka.variant": ("Variant: %s", "Variante : %s"),
 "boss.matriochka.mutated": ("%s — %s", "%s — %s"),
 "message.matriochka.mutation.woke": ("It wakes mutated. %s", "Il s'éveille muté. %s"),
 "message.matriochka.mutation.bonus": ("The mutated boss sheds a Mutated Scale.", "Le boss muté laisse une Écaille mutée."),
 # the Maquette on the Titanic Workbench
 "message.matriochka.maquette": ("On the Titanic Workbench stands a scale model of your own base. Here, it is only a toy.", "Sur l'Établi titanesque se dresse une maquette de ta propre base. Ici, ce n'est qu'un jouet."),
 # effects between the inside and the outside of a World Block
 "message.matriochka.link.damp": ("Water around your World Block soaks the jungle: the toxin rises half as fast for 5 minutes.", "L'eau autour de ton bloc-monde détrempe la jungle : la toxine monte deux fois moins vite pendant 5 minutes."),
 "message.matriochka.link.cool": ("Ice around your World Block cools the veins: the heat rises half as fast for 5 minutes.", "La glace autour de ton bloc-monde refroidit les filons : la chaleur monte deux fois moins vite pendant 5 minutes."),
 "message.matriochka.link.unlocked": ("A redstone signal reaches your World Block: sealed doors open by hand for 1 minute.", "Un signal de redstone atteint ton bloc-monde : les portes scellées s'ouvrent à la main pendant 1 minute."),
 "message.matriochka.link.storm": ("A storm rages over your World Block: the gusts grow stronger here.", "Un orage gronde au-dessus de ton bloc-monde : les rafales forcissent ici."),
 "message.matriochka.link.lit": ("Lights around your World Block feed your lantern: 5 more minutes.", "Les lumières autour de ton bloc-monde nourrissent ta lanterne : 5 minutes de plus."),
 "message.matriochka.link.dry": ("The ground around your World Block is dry: the pressure eases for 5 minutes.", "Le sol autour de ton bloc-monde est sec : la pression se relâche pendant 5 minutes."),
 "message.matriochka.link.calm": ("Anchors around your World Block hold the ground still for 5 minutes.", "Des ancres autour de ton bloc-monde tiennent le sol immobile pendant 5 minutes."),
 "message.matriochka.link.quake": ("Your World Block was moved: the whole world quakes!", "Ton bloc-monde a été déplacé : le monde entier tremble !"),
 "message.matriochka.link.boss": ("Your World Block shakes and cracks: a boss fight rages inside.", "Ton bloc-monde tremble et se fissure : un combat de boss fait rage à l'intérieur."),
 # quest steps
 "message.matriochka.quest.step": ("%s: %s / %s", "%s : %s / %s"),
 "message.matriochka.quest.handed": ("You hand %s %s to %s.", "Tu remets %s %s à %s."),
 "message.matriochka.quest.too_late": ("Night is falling. It is too late for today.", "La nuit tombe. C'est trop tard pour aujourd'hui."),
 "message.matriochka.quest.already": ("You already did it here. Find another one.", "Tu l'as déjà fait ici. Trouves-en un autre."),
 "message.matriochka.quest.book": ("You find one of the library's books.", "Tu retrouves un des livres de la bibliothèque."),
 "message.matriochka.quest.found.wreck_crew": ("Among the wreckage, a crew plate. You bring it up with you.", "Parmi les débris, une plaque d'équipage. Tu la remontes avec toi."),
 # station automation
 "station.matriochka.auto.pick": ("Automate this recipe", "Automatiser cette recette"),
 "station.matriochka.auto.on": ("Automated: click to stop", "Automatisée : clique pour arrêter"),
 "station.matriochka.auto.how": ("Hoppers feed the ingredients from the top and the sides; the result comes out below. A comparator reads how full the station is. Crafting a recipe by hand also picks it.", "Les entonnoirs versent les ingrédients par le dessus et les côtés ; le résultat sort par le dessous. Un comparateur lit le remplissage de la station. Fabriquer une recette à la main la choisit aussi."),
 "station.matriochka.auto.cond.ash_foundry": ("Works only while the heat is in the green.", "Ne marche que si la chaleur est dans le vert."),
 "station.matriochka.auto.cond.lightning_forge": ("Spends a charge per craft. Storm Essence fed by a hopper charges it.", "Dépense une charge par fabrication. L'Essence de tempête versée par un entonnoir la recharge."),
 "station.matriochka.auto.cond.dark_altar": ("Works only in complete darkness.", "Ne marche que dans le noir complet."),
 "station.matriochka.auto.cond.abyssal_press": ("Works only deep under water.", "Ne marche que sous l'eau profonde."),
 "station.matriochka.auto.cond.time_workshop": ("Works only at dawn and dusk.", "Ne marche qu'à l'aube et au crépuscule."),
 "station.matriochka.auto.cond.jailer_table": ("Makes one batch each time the lock pattern is entered.", "Fait une fournée chaque fois que le motif de la serrure est reproduit."),
 "station.matriochka.auto.cond.spore_vat": ("Waits until the brew is ripe (1 minute), then brews.", "Attend que la cuvée soit mûre (1 minute), puis brasse."),
 "message.matriochka.station.auto_on": ("The station will keep making %s from its hoppers.", "La station fabriquera %s à partir de ses entonnoirs."),
 "message.matriochka.station.auto_off": ("Automation stopped.", "Automatisation arrêtée."),
 # shaking a World Block on purpose
 "message.matriochka.shake.helped": ("You shake the block gently: those inside find their footing, the creatures lose theirs.", "Tu secoues doucement le bloc : ceux de l'intérieur gardent pied, les créatures le perdent."),
 "message.matriochka.shake.hindered": ("You strike the block: the world inside quakes.", "Tu frappes le bloc : le monde à l'intérieur tremble."),
 "message.matriochka.shake.not_yours": ("This World Block belongs to another group.", "Ce bloc-monde appartient à un autre groupe."),
 "message.matriochka.shake.cooldown": ("The world inside is still settling. Wait a little before shaking it again.", "Le monde à l'intérieur se tasse encore. Attends un peu avant de le secouer de nouveau."),
 "message.matriochka.shake.empty": ("The block rattles, but nobody of your group is inside.", "Le bloc tremble, mais personne de ton groupe n'est à l'intérieur."),
 "message.matriochka.shake.help": ("%s shakes your World Block from outside: the creatures around you stagger.", "%s secoue ton bloc-monde de l'extérieur : les créatures autour de toi chancellent."),
 "message.matriochka.shake.hinder": ("%s strikes your World Block from outside: the world quakes and the ceiling gives way!", "%s frappe ton bloc-monde de l'extérieur : le monde tremble et le plafond cède !"),
 # Doll of Life rebuilt at the Soul Altar
 "station.matriochka.recharge.tip": ("Rebuilds one Doll of Life layer for %s souls and %s rare resources of %s, in any mix:", "Refait une couche de la Poupée de vie pour %s âmes et %s ressources rares de %s, dans n'importe quel mélange :"),
 "station.matriochka.recharge.have": ("You carry %s of them and %s souls.", "Tu en portes %s et %s âmes."),
 "message.matriochka.souls_freed": ("%s souls freed (%s in all).", "%s âmes libérées (%s en tout)."),
 "message.matriochka.altar.soul_item": ("Use it instead: its souls are freed without moving your karma.", "Utilise-le plutôt : ses âmes se libèrent sans toucher à ton karma."),
 "message.matriochka.altar.no_rares": ("A layer also costs %s rare resources of %s.", "Une couche coûte aussi %s ressources rares de %s."),
}
cond = {"ash_foundry": ("The foundry needs 1 to 3 heat sources around it (lava, magma, fire).", "La fonderie demande 1 à 3 sources de chaleur autour d'elle (lave, magma, feu)."),
        "lightning_forge": ("The forge has no charge. Wait for lightning under open sky, or feed it Storm Essence.", "La forge n'a pas de charge. Attends la foudre à ciel ouvert, ou nourris-la d'Essence de tempête."),
        "dark_altar": ("The altar only works in complete darkness.", "L'autel ne fonctionne que dans le noir complet."),
        "abyssal_press": ("The press must be deep under water.", "La presse doit être sous l'eau profonde."),
        "time_workshop": ("The workshop only accepts recipes at dawn and dusk.", "L'atelier n'accepte les recettes qu'à l'aube et au crépuscule."),
        "jailer_table": ("Reproduce the lock pattern with the pins first.", "Reproduis d'abord le motif de la serrure avec les goupilles.")}
for k, v in cond.items():
    U[f"message.matriochka.station.condition.{k}"] = v
for w in range(0, 11):
    U[f"message.matriochka.boss_down.{w}"] = {
        0: ("The Guardian falls. Its core, the Matrix Workbench plans and the first World Soil are yours. Your Scroll becomes the Journal.", "Le Gardien tombe. Son noyau, les plans de l'Établi matriciel et la première Terre de monde sont à toi. Ton Parchemin devient le Journal."),
        1: ("The Spore Queen withers. A first layer grows on your Doll of Life. The worlds were made.", "La Reine des spores se fane. Une première couche pousse sur ta Poupée de vie. Les mondes ont été fabriqués."),
        2: ("The Ash Titan cools down. Enchanting and the Nether answer you now. Each world holds something.", "Le Titan de cendre refroidit. Les enchantements et le Nether te répondent désormais. Chaque monde enferme quelque chose."),
        3: ("The Grand Jailer's cell is empty. A refuge doll is yours. An old artisan left plans.", "La cellule du Grand Geôlier est vide. Une poupée-refuge est à toi. Un ancien artisan a laissé des plans."),
        4: ("The Storm King falls from the sky. The Artisan tried to stop his work.", "Le Roi des tempêtes tombe du ciel. L'Artisan a voulu arrêter son œuvre."),
        5: ("The Light Eater starves. A second layer grows on your doll. Diamonds return. Something is watching you.", "Le Mangeur de lumière s'éteint de faim. Une deuxième couche pousse sur ta poupée. Le diamant revient. Une présence t'observe."),
        6: ("Your Double shatters. The bosses are linked to one another.", "Ton Double se brise. Les boss sont liés entre eux."),
        7: ("The Leviathan sinks. Every prison was made for a single creature.", "Le Léviathan sombre. Toutes les prisons enferment une seule créature."),
        8: ("The Master of Seasons stops. A third layer grows on your doll. The End opens. Someone came this way before.", "Le Maître des saisons s'arrête. Une troisième couche pousse sur ta poupée. L'End s'ouvre. Quelqu'un est déjà passé par là."),
        9: ("The Heart of the Terrain stops beating. You hold the Key of the Last Doll. That traveler was you.", "Le Cœur du terrain cesse de battre. Tu tiens la Clé de la dernière poupée. Ce voyageur, c'était toi."),
        10: ("The Unfinished comes apart, shell after shell. Breaking the prisons, you set it free.", "L'Inachevée se défait, enveloppe après enveloppe. En brisant les prisons, tu l'as libérée."),
    }[w]
for w in range(1, 11):
    U[f"message.matriochka.seed_planted.{w}"] = {
        1: ("The seed wants water nearby.", "La graine réclame de l'eau à proximité."),
        2: ("The seed wants heat: lava, magma or a campfire.", "La graine réclame de la chaleur : lave, magma ou feu de camp."),
        3: ("The seed wants a redstone signal.", "La graine réclame un signal de redstone."),
        4: ("The seed wants the open sky.", "La graine réclame le ciel ouvert."),
        5: ("The seed wants darkness.", "La graine réclame l'obscurité."),
        6: ("The seed wants height (above y 100).", "La graine réclame de la hauteur (au-dessus de y 100)."),
        7: ("The seed wants water nearby.", "La graine réclame de l'eau à proximité."),
        8: ("The seed hatches at dawn or dusk.", "La graine éclot à l'aube ou au crépuscule."),
        9: ("The seed wants a redstone signal.", "La graine réclame un signal de redstone."),
        10: ("The seed is ready. It only waits for you.", "La graine est prête. Elle n'attend que toi."),
    }[w]
pages = [
 (("Every block can hold a world", "Look closely at a block of earth. Inside, there may be a forest, a forge, a prison. I built ten of them, one inside the other."),
  ("Chaque bloc peut contenir un monde", "Regarde de près un bloc de terre. À l'intérieur, il peut y avoir une forêt, une forge, une prison. J'en ai construit dix, l'un dans l'autre.")),
 (("Your objective", "Find the Guardian's Sanctuary, wake it at its altar and take its core. With it, the first world can open."),
  ("Ton objectif", "Trouve le Sanctuaire du Gardien, réveille-le à son autel et prends son noyau. Grâce à lui, le premier monde pourra s'ouvrir.")),
 (("The way down", "The first world grows from a Seed planted on World Soil. Each world after it opens its own way: a heart thrown near lava, a key in a door, a rod in a storm. Enter the block, defeat its boss, take its core. Again."),
  ("Le chemin vers le bas", "Le premier monde pousse d'une Graine plantée sur une Terre de monde. Chaque monde suivant s'ouvre à sa façon : un cœur près de la lave, une clé dans une porte, un paratonnerre sous l'orage. Entre dans le bloc, bats son boss, prends son noyau. Recommence.")),
 (("Surviving", "Death sends you back outside. A Doll of Life breaks a layer instead. A Soul Cradle lets you wake inside a world. A death chest keeps what you carried."),
  ("Survivre", "La mort te renvoie dehors. Une Poupée de vie brise une couche à sa place. Un Berceau d'âme te permet de te réveiller dans un monde. Un coffre de mort garde ce que tu portais.")),
 (("Choices", "Every item holds a soul. Purify it, or devour it. Every piece of gear gets a class when it is made. I will not tell you more. I wrote this for you."),
  ("Les choix", "Chaque objet porte une âme. Purifie-la, ou dévore-la. Chaque pièce d'équipement reçoit une classe à sa fabrication. Je ne t'en dirai pas plus. J'ai écrit ceci pour toi.")),
]
for i, ((te, be), (tf, bf)) in enumerate(pages):
    U[f"scroll.matriochka.p{i}.title"] = (te, tf)
    U[f"scroll.matriochka.p{i}"] = (be, bf)
titles = {"painted_cape": ("Painted Cape", "Cape peinte"), "iron_lungs": ("Iron Lungs", "Poumons de fer"), "ash_skin": ("Ash Skin", "Peau de cendre"),
          "wall_walker": ("Wall Walker", "Passe-muraille"), "wind_child": ("Child of the Wind", "Fils du vent"), "glow": ("Glow", "Lueur"),
          "closed_eyes": ("Closed Eyes", "Yeux fermés"), "head_down": ("Head Down", "Tête en bas"), "cold_blood": ("Cold Blood", "Sang-froid"),
          "out_of_time": ("Out of Time", "Hors du temps"), "untethered": ("Untethered", "Sans attache"), "apprentice": ("Apprentice", "Apprenti"), "seamless": ("Seamless", "Sans couture")}
for k, v in titles.items():
    U[f"title.matriochka.{k}"] = v
# ------------------------------------------------------------------ server limits, comfort, cinematics, adaptive music
U["message.matriochka.server_full"] = ("The server holds as many worlds as it allows. This opening waits until another group frees its parcel.",
                                       "Le serveur contient autant de mondes qu'il le permet. Cette ouverture attend qu'un autre groupe libère sa parcelle.")
comfort = {
    "title": ("Comfort", "Confort"),
    "open": ("Comfort", "Confort"),
    "defaults": ("Defaults", "Par défaut"),
    "on": ("On", "Oui"), "off": ("Off", "Non"),
    "page.screen": ("Screen", "Écran"),
    "page.hud": ("HUD and music", "Interface et musique"),
    "shake": ("Screen shake", "Tremblements"),
    "shake.desc": ("How much heavy blows, quakes and trembling World Blocks shake the camera. 0% turns it off.",
                   "À quel point les coups lourds, les séismes et les bloc-mondes qui tremblent secouent la caméra. 0 % les coupe."),
    "flashes": ("Flashes", "Flashs"),
    "flashes.desc": ("The white flash of a boss phase break and the red glow before a signature attack. Off, a soft darkening stands in.",
                     "Le flash blanc d'un changement de phase et la lueur rouge avant une attaque signature. Désactivés, un léger assombrissement les remplace."),
    "soft_effects": ("Soft effects", "Effets adoucis"),
    "soft_effects.desc": ("No Nausea and no Darkness pulses: the server skips them for you and a gentle tint shows how long they would have lasted.",
                          "Ni Nausée ni pulsations d'Obscurité : le serveur te les épargne et une teinte douce montre combien de temps elles auraient duré."),
    "cinematics": ("Cinematics", "Cinématiques"),
    "cinematics.desc": ("Boss introductions (bars, title card, the camera turning to the boss), world title cards and the phase freeze-frame.",
                        "Présentations des boss (bandes, carton-titre, caméra tournée vers le boss), cartons des mondes et arrêt sur image des phases."),
    "subtitles": ("Attack subtitles", "Sous-titres d'attaque"),
    "subtitles.desc": ("Names the attack a boss winds up in large letters, with the time left before it lands.",
                       "Nomme en grandes lettres l'attaque qu'un boss prépare, avec le temps restant avant l'impact."),
    "particles": ("Fewer particles", "Moins de particules"),
    "particles.desc": ("Skips two particles out of three inside the worlds and during boss fights.",
                       "Retire deux particules sur trois dans les mondes et pendant les combats de boss."),
    "patterns": ("Gauge patterns", "Motifs des jauges"),
    "patterns.desc": ("The rule's icons above the hunger bar carry stripes past half and crosshatching in danger, and the boss bars show the health in figures, so you can read them without the colours.",
                      "Les icônes de la règle au-dessus de la faim portent des rayures passé la moitié et des hachures en danger, et les barres de boss affichent la vie en chiffres : tout se lit sans les couleurs."),
    "hud_scale": ("HUD size", "Taille de l'interface"),
    "hud_scale.desc": ("Size of the souls' count and of the armour's doll beside the hearts.",
                       "Taille du compte des âmes et de la poupée de l'armure près des cœurs."),
    "world_label": ("World label", "Nom du monde"),
    "souls_bar": ("Souls bar", "Barre d'âmes"),
    "souls_bar.desc": ("The souls bar above the experience bar, with the hearts and the hunger raised over it. Off puts them back in their usual place.",
                       "La barre d'âmes au-dessus de la barre d'expérience, les cœurs et la faim remontés au-dessus. Désactivée, ils retrouvent leur place habituelle."),
    "world_label.desc": ("A small label with the world you are in, kept in a corner of the screen.",
                         "Une petite étiquette du monde où tu es, gardée dans un coin de l'écran."),
    "hud_corner": ("Plaque corner", "Coin du cartouche"),
    "hud_corner.desc": ("The corner of the screen the plaque sits in.", "Le coin de l'écran où se place le cartouche."),
    "corner.top_left": ("Top left", "Haut gauche"), "corner.top_right": ("Top right", "Haut droite"),
    "corner.bottom_left": ("Bottom left", "Bas gauche"), "corner.bottom_right": ("Bottom right", "Bas droite"),
    "music_explore": ("World themes", "Thèmes des mondes"),
    "music_explore.desc": ("Volume of each world's theme while you explore, as a share of the game's music slider.",
                           "Volume du thème de chaque monde pendant l'exploration, en part du curseur de musique du jeu."),
    "music_danger": ("Danger", "Danger"),
    "music_danger.desc": ("Volume of the tense theme that takes over while creatures hunt you.",
                          "Volume du thème tendu qui prend le relais quand des créatures te traquent."),
    "music_boss": ("Boss fights", "Combats de boss"),
    "music_boss.desc": ("Volume of the boss themes.", "Volume des thèmes de boss."),
    "music_layers": ("Heartbeat", "Battements"),
    "music_layers.desc": ("Volume of the heartbeat that rises when your health or your breath runs low.",
                          "Volume des battements de cœur qui montent quand ta santé ou ton souffle baisse."),
    "music_stings": ("Stings", "Ponctuations"),
    "music_stings.desc": ("Volume of the short phrases that mark a place found, a Journal page or a quest done.",
                          "Volume des courtes phrases qui marquent un lieu trouvé, une page du Journal ou une quête accomplie."),
}
for k, v in comfort.items():
    U[f"comfort.matriochka.{k}"] = v
boss_titles = {
    "block_guardian": ("Keeper of the First Doll", "Gardien de la première poupée"),
    "spore_queen": ("Mother of the Rot", "Mère de la pourriture"),
    "ash_titan": ("The Forge That Walks", "La forge qui marche"),
    "grand_jailer": ("Warden of Every Lock", "Gardien de toutes les serrures"),
    "storm_king": ("Crowned by Lightning", "Couronné par la foudre"),
    "light_eater": ("Hunger in the Dark", "La faim dans le noir"),
    "your_double": ("Everything You Carry", "Tout ce que tu portes"),
    "pressure_leviathan": ("The Weight of the Deep", "Le poids des profondeurs"),
    "seasons_master": ("Who Turns the Year", "Celui qui tourne l'année"),
    "terrain_heart_boss": ("The Ground's Own Pulse", "Le pouls même du sol"),
    "the_unfinished": ("Shell upon Shell", "Enveloppe sur enveloppe"),
    "artisan_shadow": ("What the Artisan Left Behind", "Ce que l'Artisan a laissé"),
}
for k, v in boss_titles.items():
    U[f"cine.matriochka.boss.{k}"] = v
U["cine.matriochka.defeat"] = ("Sealed back in its doll", "Refermé dans sa poupée")
world_lines = {
    1: ("The air is spores: keep the Toxin low.", "L'air n'est que spores : garde la Toxine basse."),
    2: ("The rock is hot: mind the Heat.", "La roche est brûlante : surveille la Chaleur."),
    3: ("Every way is locked: find the keys.", "Chaque passage est verrouillé : trouve les clés."),
    4: ("The wind never rests: crouch when it gusts.", "Le vent ne se repose jamais : accroupis-toi quand il souffle."),
    5: ("No light lasts: every sound is heard.", "Aucune lumière ne dure : chaque bruit s'entend."),
    6: ("Up and down trade places.", "Le haut et le bas échangent leur place."),
    7: ("The sea presses down: watch your breath.", "La mer pèse : surveille ton souffle."),
    8: ("The days fly by, and the seasons with them.", "Les jours filent, et les saisons avec eux."),
    9: ("The ground walks, and carries you.", "Le sol marche, et il t'emporte."),
    10: ("Every law at once, at doll scale.", "Toutes les lois à la fois, à l'échelle d'une poupée."),
    11: ("Nothing moves here. Do not stay still.", "Rien ne bouge ici. Ne reste pas immobile."),
}
for k, v in world_lines.items():
    U[f"cine.matriochka.world.{k}"] = v
# the first-steps guide: one HUD card per step of the first half hour (world/Tutorial, client/TutorialCard)
tutorial = {
    "read": (("Read the Artisan's Scroll", "Use the Scroll and turn to the page \"Your objective\"."),
             ("Lis le Parchemin de l'artisan", "Utilise le Parchemin et tourne jusqu'à la page « Ton objectif ».")),
    "sanctuary": (("Find the Guardian's Sanctuary", "Follow the needle to a ring of great pillars round an altar."),
                  ("Trouve le Sanctuaire du Gardien", "Suis l'aiguille jusqu'à un cercle de grands piliers autour d'un autel.")),
    "wake": (("Wake the Guardian", "Use the altar at the heart of the sanctuary."),
             ("Réveille le Gardien", "Active l'autel au cœur du sanctuaire.")),
    "defeat": (("Defeat the Guardian", "Its strong blows glow first: step aside, then strike."),
               ("Bats le Gardien", "Ses coups forts s'illuminent d'abord : écarte-toi, puis frappe.")),
    "workbench": (("Place the Matrix Workbench", "The Guardian left it with its core. Set it down anywhere."),
                  ("Pose l'Établi matriciel", "Le Gardien l'a laissé avec son noyau. Pose-le où tu veux.")),
    "seed": (("Craft the World 1 Seed", "At the Workbench: the Guardian's core, 16 iron ingots and 16 oak logs."),
             ("Fabrique la Graine du monde 1", "À l'Établi : le noyau du Gardien, 16 lingots de fer et 16 bûches de chêne.")),
    "till": (("Till World Soil", "Place a World Soil from the Guardian, then use a hoe on it."),
             ("Bêche une Terre de monde", "Pose une Terre de monde du Gardien, puis utilise une houe dessus.")),
    "plant": (("Plant the Seed by water", "Plant it on the tilled soil, with water within four blocks."),
              ("Plante la Graine près de l'eau", "Plante-la sur la terre bêchée, avec de l'eau à moins de quatre blocs.")),
    "hatch": (("Wait for it to hatch", "Stay close: the Seed grows into a World Block in a few seconds."),
              ("Attends l'éclosion", "Reste près d'elle : la Graine devient un Bloc-monde en quelques secondes.")),
    "enter": (("Enter World 1", "Use the World Block to step inside the Toxic Jungle."),
              ("Entre dans le monde 1", "Utilise le Bloc-monde pour entrer dans la Jungle toxique.")),
}
for k, ((te, he), (tf, hf)) in tutorial.items():
    U[f"tutorial.matriochka.{k}"] = (te, tf)
    U[f"tutorial.matriochka.{k}.hint"] = (he, hf)
U.update({
    "tutorial.matriochka.header": ("First steps %s / %s", "Premiers pas %s / %s"),
    "tutorial.matriochka.distance": ("%s blocks", "%s blocs"),
    "tutorial.matriochka.surface": ("Back to the Surface first.", "Reviens d'abord à la Surface."),
    "tutorial.matriochka.lost": ("No sanctuary found nearby: explore the Surface.", "Aucun sanctuaire à proximité : explore la Surface."),
    "tutorial.matriochka.done": ("The first doll is open", "La première poupée est ouverte"),
    "tutorial.matriochka.done.hint": ("The Journal shows every next step from here.", "Le Journal t'indique chaque étape à partir d'ici."),
    "tutorial.matriochka.toggle": ("Guide", "Guide"),
    "tutorial.matriochka.toggle.tip": ("Show or hide the first-steps card", "Afficher ou masquer la carte des premiers pas"),
    # Mod Menu entry and the info screen it opens
    "modmenu.summaryTranslation.matriochka": ("Every block can hold a world.", "Chaque bloc peut contenir un monde."),
    "modmenu.descriptionTranslation.matriochka": ("Every block can hold a world. Ten nested worlds, ten bosses, one Artisan.",
                                                  "Chaque bloc peut contenir un monde. Dix mondes gigognes, dix boss, un artisan."),
    "screen.matriochka.info.title": ("Matriochka", "Matriochka"),
    "screen.matriochka.info.version": ("Version %s", "Version %s"),
    "screen.matriochka.info.body": ("Ten nested worlds, one inside the other. Find the Guardian's Sanctuary, take its core and plant the first Seed. The Artisan's Scroll and its first-steps card guide you through the first half hour; the Journal takes over after.",
                                    "Dix mondes gigognes, l'un dans l'autre. Trouve le Sanctuaire du Gardien, prends son noyau et plante la première Graine. Le Parchemin de l'artisan et sa carte des premiers pas te guident pendant la première demi-heure ; le Journal prend le relais ensuite."),
    "screen.matriochka.info.config": ("Server rules live in config/matriochka.json.", "Les règles du serveur se trouvent dans config/matriochka.json."),
    "screen.matriochka.info.wiki": ("Wiki", "Wiki"),
    "screen.matriochka.info.site": ("Website", "Site"),
    "screen.matriochka.info.done": ("Done", "Terminé"),
    # map mods (compat/MapCompat): World 5 turns off a map's cave view and radar
    "message.matriochka.maps.dark": ("In the Lightless Deep, your map sees no further than you do.", "Dans la Profondeur sans lumière, ta carte ne voit pas plus loin que toi."),
    "message.matriochka.maps.clear": ("Your map can see in the dark again.", "Ta carte voit de nouveau dans le noir."),
})
# ---- replay value: the Trials, world events and talents
U.update({
 "trials.matriochka.title": ("Trials", "Épreuves"),
 "trials.matriochka.gauntlet": ("The Gauntlet", "Les onze"),
 "trials.matriochka.back": ("Back", "Retour"), "trials.matriochka.titles": ("Titles", "Titres"),
 "trials.matriochka.wear": ("Wear", "Porter"), "trials.matriochka.begin": ("Begin", "Commencer"), "trials.matriochka.leave": ("Leave", "Quitter"),
 "trials.matriochka.locked": ("The Trials open once you have seen an ending.", "Les Épreuves s'ouvrent une fois une fin vue."),
 "trials.matriochka.desc.world": ("Two waves of the creatures of %s, the second led by its elites, then its boss, stronger and mutated. The clock runs from the first wave to the last blow.", "Deux vagues des créatures du monde %s, la seconde menée par ses élites, puis son boss, plus fort et muté. Le chrono court de la première vague au dernier coup."),
 "trials.matriochka.desc.gauntlet": ("The eleven bosses, from the Guardian to the Unfinished, one after the other on a stage painted for each world.", "Les onze boss, du Gardien à l'Inachevée, l'un après l'autre sur une scène peinte pour chaque monde."),
 "trials.matriochka.par": ("Par", "Temps de référence"), "trials.matriochka.mine": ("Your best", "Ton record"), "trials.matriochka.group": ("Your group's best", "Record du groupe"),
 "trials.matriochka.board": ("Board", "Classement"), "trials.matriochka.board.empty": ("No one has finished it yet.", "Personne ne l'a encore finie."),
 "trials.matriochka.titles.none": ("No title yet. Win a trial, or a quest that gives one.", "Aucun titre pour l'instant. Gagne une épreuve, ou une quête qui en donne un."),
 "hud.matriochka.trial.stage": ("Stage %s/%s", "Étape %s/%s"), "hud.matriochka.trial.best": ("Best %s", "Record %s"), "hud.matriochka.trial.par": ("Par %s", "Référence %s"),
 "message.matriochka.trial.unknown": ("No such trial.", "Cette épreuve n'existe pas."),
 "message.matriochka.trial.locked": ("The Trials open once you have seen an ending.", "Les Épreuves s'ouvrent une fois une fin vue."),
 "message.matriochka.trial.already": ("You are already in a trial.", "Tu es déjà dans une épreuve."),
 "message.matriochka.trial.peaceful": ("No trial in peaceful difficulty.", "Pas d'épreuve en difficulté paisible."),
 "message.matriochka.trial.busy": ("Every stage is taken. Try again in a moment.", "Toutes les scènes sont prises. Réessaie dans un instant."),
 "message.matriochka.trial.begin": ("%s begins: %s stages. Falling carries you out.", "%s commence : %s étapes. Tomber te fait sortir."),
 "message.matriochka.trial.stage": ("Stage %s/%s: %s", "Étape %s/%s : %s"),
 "message.matriochka.trial.wave": ("the creatures of %s", "les créatures du monde %s"),
 "message.matriochka.trial.wave_elites": ("the elites of %s", "les élites du monde %s"),
 "message.matriochka.trial.cleared": ("Stage %s of %s cleared.", "Étape %s sur %s franchie."),
 "message.matriochka.trial.done": ("%s won in %s.", "%s gagnée en %s."),
 "message.matriochka.trial.personal": ("A personal best.", "Un record personnel."),
 "message.matriochka.trial.rank": ("Your group stands number %s on the board.", "Ton groupe est numéro %s au classement."),
 "message.matriochka.trial.title": ("New title: %s.", "Nouveau titre : %s."),
 "message.matriochka.trial.left": ("You leave the trial.", "Tu quittes l'épreuve."),
 "message.matriochka.trial.fallen": ("You fall, and the doll lets you out of the trial.", "Tu tombes, et la poupée te laisse sortir de l'épreuve."),
 "command.matriochka.trial.top": ("Board of %s:", "Classement de %s :"), "command.matriochka.trial.empty": ("No one yet.", "Personne pour l'instant."),
 "command.matriochka.trial.row": ("%s. %s  %s", "%s. %s  %s"),
 "command.matriochka.event.started": ("Event started.", "Événement lancé."),
 "command.matriochka.event.refused": ("No event here: stand in a world, with no other event going on.", "Pas d'événement ici : tiens-toi dans un monde, sans autre événement en cours."),
 "event.matriochka.invasion.coming": ("Invasion coming: %s", "Invasion imminente : %s"),
 "event.matriochka.invasion.wave": ("Invasion of %s: wave %s/%s", "Invasion du monde %s : vague %s/%s"),
 "event.matriochka.surge.coming": ("%s is coming", "%s approche"), "event.matriochka.surge.live": ("%s", "%s"),
 "event.matriochka.warlord": ("Warlord %s", "Seigneur de guerre %s"),
 "message.matriochka.event.invasion": ("The creatures of %s gather. They are coming for you.", "Les créatures du monde %s se rassemblent. Elles viennent pour toi."),
 "message.matriochka.event.invasion.next": ("Wave %s of %s!", "Vague %s sur %s !"),
 "message.matriochka.event.invasion.warlord": ("Wave %s of %s: their warlord leads it!", "Vague %s sur %s : leur seigneur de guerre la mène !"),
 "message.matriochka.event.invasion.won": ("The invasion is broken. Their spoils wait in a chest at %s %s %s.", "L'invasion est brisée. Leur butin attend dans un coffre en %s %s %s."),
 "message.matriochka.event.invasion.withdraw": ("The invaders withdraw into the world.", "Les envahisseurs se retirent dans le monde."),
 "message.matriochka.event.surge": ("%s: %s", "%s : %s"),
 "message.matriochka.event.surge.over": ("%s passes. You weathered it: +%s souls.", "%s s'apaise. Tu as tenu bon : +%s âmes."),
 "message.matriochka.event.merchant": ("Travelling merchant: %s. Rare wares, for a little while.", "Marchand itinérant : %s. Des marchandises rares, pour peu de temps."),
 "message.matriochka.event.merchant.gone": ("%s moves on.", "%s reprend la route."),
 "talents.matriochka.title": ("Talents", "Talents"), "talents.matriochka.open": ("Talents", "Talents"),
 "talents.matriochka.learn": ("Learn", "Apprendre"), "talents.matriochka.reset": ("Forget", "Oublier"),
 "talents.matriochka.learnt": ("Learnt.", "Appris."),
 "talents.matriochka.need_previous": ("Learn the talent above it first.", "Apprends d'abord le talent du dessus."),
 "talents.matriochka.need_boss": ("Opens once your group has beaten %s.", "S'ouvre quand ton groupe a battu %s."),
 "talents.matriochka.need_souls": ("Not enough souls.", "Pas assez d'âmes."),
 "talents.matriochka.need_shards": ("Not enough Shell Shards.", "Pas assez d'Éclats d'enveloppe."),
 "talents.matriochka.help": ("Pick a doll in the %s tree. Each branch is learnt from the top down, with souls, then Shell Shards. Forget gives back half the souls spent.", "Choisis une poupée dans l'arbre %s. Chaque branche s'apprend de haut en bas, avec des âmes, puis des Éclats d'enveloppe. Oublier rend la moitié des âmes dépensées."),
 "talents.matriochka.cost": ("Costs %s souls", "Coûte %s âmes"),
 "talents.matriochka.cost_shards": ("Costs %s souls and %s Shell Shards", "Coûte %s âmes et %s Éclats d'enveloppe"),
 "talents.matriochka.tier": ("Tier %s of the %s branch", "Rang %s de la branche %s"),
 "talents.matriochka.gate": ("Needs %s beaten", "Demande %s vaincu"),
 "talents.matriochka.active_rule": ("Acts while you wear or hold %s gear", "Agit tant que tu portes ou tiens de l'équipement %s"),
 "message.matriochka.talent.unknown": ("No such talent.", "Ce talent n'existe pas."),
 "message.matriochka.talent.known": ("You already know this talent.", "Tu connais déjà ce talent."),
 "message.matriochka.talent.table": ("Talents are learnt at a Class Table.", "Les talents s'apprennent à une Table de classe."),
 "message.matriochka.talent.previous": ("Learn the talent above it first.", "Apprends d'abord le talent du dessus."),
 "message.matriochka.talent.progress": ("Your group has not gone far enough for this talent.", "Ton groupe n'est pas encore allé assez loin pour ce talent."),
 "message.matriochka.talent.learnt": ("Talent learnt: %s", "Talent appris : %s"),
 "message.matriochka.talent.reset": ("Your talents are forgotten. %s souls come back to you.", "Tes talents sont oubliés. %s âmes te reviennent."),
 "message.matriochka.talent.none": ("You know no talent yet.", "Tu ne connais encore aucun talent."),
 "stall.matriochka.wares": ("Wares", "Marchandises"),
 "stall.matriochka.empty": ("Nothing to trade today.", "Rien à échanger aujourd'hui."),
 "stall.matriochka.under_counter": ("Under the counter", "Sous le comptoir"),
 "stall.matriochka.sold_out": ("Sold out", "Épuisé"),
 "stall.matriochka.sold_out.long": ("Sold out: the trader has no more", "Épuisé : le marchand n'en a plus"),
 "stall.matriochka.stock": ("In stock: %s of %s", "En stock : %s sur %s"),
 "stall.matriochka.world": ("World %s · %s", "Monde %s · %s"),
 "stall.matriochka.kind.people": ("Trader of this world", "Marchand de ce monde"),
 "stall.matriochka.kind.peddler": ("Doll trader of the Surface", "Marchand de poupées de la Surface"),
 "stall.matriochka.kind.travelling": ("Travelling merchant", "Marchand itinérant"),
 "stall.matriochka.kind.travelling_left": ("Travelling merchant · leaves in %s", "Marchand itinérant · repart dans %s"),
 "stall.matriochka.kind.black_market": ("Black market · forbidden goods: %s", "Marché clandestin · marchandises interdites : %s"),
 "stall.matriochka.karma.kind": ("Karma %s · kind prices, -10%%", "Karma %s · prix doux, -10 %%"),
 "stall.matriochka.karma.fair": ("Karma %s · fair prices", "Karma %s · prix justes"),
 "stall.matriochka.karma.dear": ("Karma %s · dear prices, +10%%", "Karma %s · prix forts, +10 %%"),
 "stall.matriochka.tip.gives": ("Gives %s × %s", "Donne %s × %s"),
 "stall.matriochka.tip.price": ("Costs %s × %s", "Coûte %s × %s"),
 "stall.matriochka.tip.price2": ("%s and %s × %s", "%s et %s × %s"),
 "stall.matriochka.tip.discount": ("Your karma lowers the price (it was %s)", "Ton karma baisse le prix (il était de %s)"),
 "stall.matriochka.tip.markup": ("Your karma raises the price (it was %s)", "Ton karma monte le prix (il était de %s)"),
 "stall.matriochka.tip.short": ("You carry %s of the %s needed", "Tu en portes %s sur les %s demandés"),
 "stall.matriochka.tip.contraband": ("Black-market goods, sold only to the dark-hearted", "Marchandise clandestine, vendue aux seuls cœurs sombres"),
 "recap.matriochka.title": ("End of the cycle", "Fin du cycle"),
 "recap.matriochka.clean": ("Hide (F1)", "Masquer (F1)"),
 "recap.matriochka.continue": ("Continue", "Continuer"),
 "recap.matriochka.back": ("Back", "Retour"),
 "recap.matriochka.sub": ("Cycle %s · played alone", "Cycle %s · en solitaire"),
 "recap.matriochka.sub_group": ("Cycle %s · a group of %s", "Cycle %s · un groupe de %s"),
 "recap.matriochka.line.seal": ("The last doll closed over the Unfinished. The worlds sleep, sealed, and its hunger with them.", "La dernière poupée s'est refermée sur l'Inachevée. Les mondes dorment, scellés, et sa faim avec eux."),
 "recap.matriochka.line.absorb": ("You took the Unfinished's hunger for your own. Every world you opened now knows your name.", "Tu as fait tienne la faim de l'Inachevée. Chaque monde que tu as ouvert connaît désormais ton nom."),
 "recap.matriochka.line.tools": ("You set down the tools. The last Scroll stays blank, and the dolls rest, unpainted.", "Tu as posé les outils. Le dernier Parchemin reste blanc, et les poupées se reposent, sans peinture."),
 "recap.matriochka.boss.beaten": ("Beaten this cycle", "Vaincu pendant ce cycle"),
 "recap.matriochka.boss.standing": ("Not beaten this cycle", "Pas vaincu pendant ce cycle"),
 "recap.matriochka.stat.worlds": ("Worlds opened", "Mondes ouverts"),
 "recap.matriochka.stat.bosses": ("Bosses beaten", "Boss vaincus"),
 "recap.matriochka.stat.deaths": ("Deaths", "Morts"),
 "recap.matriochka.stat.layers": ("Layers lost / rebuilt", "Couches perdues/refaites"),
 "recap.matriochka.stat.souls": ("Souls gathered", "Âmes récoltées"),
 "recap.matriochka.stat.time": ("Time played", "Temps de jeu"),
 "recap.matriochka.stat.dolls": ("Hidden dolls", "Poupées cachées"),
 "recap.matriochka.stat.pages": ("Journal pages", "Pages du Journal"),
 "recap.matriochka.stat.quests": ("Quests done", "Quêtes faites"),
 "recap.matriochka.stat.karma": ("Karma", "Karma"),
 "recap.matriochka.stat.class": ("Class", "Classe"),
 "recap.matriochka.stat.trial": ("Best trial", "Épreuve"),
 "recap.matriochka.of_total": ("+%s (%s/%s)", "+%s (%s/%s)"),
 "recap.matriochka.karma_value": ("%s · %s", "%s · %s"),
 "recap.matriochka.karma.light2": ("Beloved", "Aimé"),
 "recap.matriochka.karma.light1": ("Trusted", "Estimé"),
 "recap.matriochka.karma.neutral": ("Neutral", "Neutre"),
 "recap.matriochka.karma.dark1": ("Feared", "Craint"),
 "recap.matriochka.karma.dark2": ("Devourer", "Dévoreur"),
 "recap.matriochka.no_class": ("No class gear", "Sans équipement de classe"),
 "recap.matriochka.class_value": ("%s · level %s", "%s · niveau %s"),
 "recap.matriochka.none": ("None", "Aucune"),
 "recap.matriochka.trial_value": ("%s · %s", "%s · %s"),
 "journal.matriochka.last_cycle": ("Last cycle", "Dernier cycle"),
})
# the rites that open Worlds 2 to 10 (tools/content.py RITES): what each one still waits for, and where it goes
from content import RITES  # noqa: E402
for _w, _en, _fr, _he, _hf, _we, _wf in RITES:
    U[f"message.matriochka.rite.wait.{_w}"] = (_we, _wf)
# what the people of the worlds say when a player comes near (entity/MatrioNpc greet)
U["npc.matriochka.doll_peddler.0"] = ("Dolls inside dolls, traveller. The big one by the altar is only the first.", "Des poupées dans des poupées, voyageur. La grande près de l'autel n'est que la première.")
U["npc.matriochka.doll_peddler.1"] = ("You woke the Guardian and lived. The Seed will want soil, and patience.", "Tu as réveillé le Gardien et tu as survécu. La Graine voudra de la terre, et de la patience.")
U["npc.matriochka.doll_peddler.2"] = ("Halfway down, and still the dolls get smaller. Mind what you bring back up.", "À mi-chemin, et les poupées rapetissent encore. Fais attention à ce que tu remontes.")
U["npc.matriochka.doll_peddler.3"] = ("There is only the Workshop left. Whoever carved all this is waiting there.", "Il ne reste que l'Atelier. Celui qui a sculpté tout ça t'y attend.")
U["npc.matriochka.gatherer.before"] = ("The Queen's spores are in everything here. Breathe slow, and keep the Toxin down.", "Les spores de la Reine sont partout ici. Respire lentement, et garde la Toxine basse.")
U["npc.matriochka.gatherer.after"] = ("The air is lighter since the Queen fell. The jungle hums a different song.", "L'air est plus léger depuis la chute de la Reine. La jungle fredonne autrement.")
U["npc.matriochka.free_miner.before"] = ("The Titan still walks the veins. You hear its hammer before you see it.", "Le Titan arpente encore les veines. On entend son marteau avant de le voir.")
U["npc.matriochka.free_miner.after"] = ("The forge has gone quiet. Strange, how much I miss the noise.", "La forge s'est tue. Étrange, comme le bruit me manque.")
U["npc.matriochka.prisoner.before"] = ("Every door here has a key, and the Jailer wears them all.", "Chaque porte ici a sa clé, et le Geôlier les porte toutes.")
U["npc.matriochka.prisoner.after"] = ("The locks still turn, but nobody is watching them now.", "Les serrures tournent encore, mais plus personne ne les surveille.")
U["npc.matriochka.lighthouse_keeper.before"] = ("Keep low when it gusts. The King throws the wind like a spear.", "Baisse-toi quand ça souffle. Le Roi lance le vent comme une lance.")
U["npc.matriochka.lighthouse_keeper.after"] = ("The storms still come, but they have lost their crown.", "Les orages reviennent encore, mais ils ont perdu leur couronne.")
U["npc.matriochka.silent_one.before"] = ("(points down into the dark, then at your lantern, and shakes their head)", "(montre le noir en contrebas, puis ta lanterne, et secoue la tête)")
U["npc.matriochka.silent_one.after"] = ("(holds up a hand to the dark, and smiles for the first time)", "(tend la main vers le noir, et sourit pour la première fois)")
U["npc.matriochka.free_reflection.before"] = ("Your double knows every move you know. Try one you do not.", "Ton double connaît chaque geste que tu connais. Essaie-en un que tu ignores.")
U["npc.matriochka.free_reflection.after"] = ("Up is up again, for you at least. I am still getting used to it.", "Le haut est redevenu le haut, pour toi du moins. Je m'y habitue encore.")
U["npc.matriochka.diver.before"] = ("Watch your breath. The Leviathan waits where the pressure is worst.", "Surveille ton souffle. Le Léviathan attend là où la pression est la pire.")
U["npc.matriochka.diver.after"] = ("The deep is just deep now. I can dive without counting.", "Les profondeurs ne sont plus que profondes. Je plonge sans compter.")
U["npc.matriochka.ephemeral.before"] = ("A year passes every few minutes here. The Master keeps the clock.", "Une année passe en quelques minutes ici. Le Maître tient l'horloge.")
U["npc.matriochka.ephemeral.after"] = ("The seasons still turn, but slower. I may even see the spring twice.", "Les saisons tournent encore, mais plus lentement. Je verrai peut-être deux printemps.")
U["npc.matriochka.anchored.before"] = ("Hold on to something. The ground walks, and its heart leads it.", "Accroche-toi à quelque chose. Le sol marche, et son cœur le mène.")
U["npc.matriochka.anchored.after"] = ("The ground has settled. I keep my anchor anyway, out of habit.", "Le sol s'est apaisé. Je garde mon ancre quand même, par habitude.")
U["npc.matriochka.old_apprentice.before"] = ("Every law of every world, at doll scale. The Unfinished is still being made.", "Toutes les lois de tous les mondes, à l'échelle d'une poupée. L'Inachevée est encore en train de se faire.")
U["npc.matriochka.old_apprentice.after"] = ("The bench is clear at last. The master would have liked to see this.", "L'établi est enfin dégagé. Le maître aurait aimé voir ça.")
# the Journal's collection, on the Worlds page
U["journal.matriochka.collection"] = ("Gathered: %s%%", "Rassemblé : %s %%")
U["journal.matriochka.col.boss.beaten"] = ("Boss: beaten", "Boss : vaincu")
U["journal.matriochka.col.boss.standing"] = ("Boss: still standing", "Boss : toujours debout")
U["journal.matriochka.col.pages"] = ("Journal pages: %s/5", "Pages du journal : %s/5")
U["journal.matriochka.col.doll.found"] = ("Hidden doll: found", "Poupée cachée : trouvée")
U["journal.matriochka.col.doll.missing"] = ("Hidden doll: not found yet", "Poupée cachée : pas encore trouvée")
U["journal.matriochka.col.rite.done"] = ("Way in: opened", "Accès : ouvert")
U["journal.matriochka.col.rite.unknown"] = ("Way in: not opened yet", "Accès : pas encore ouvert")
# a trophy doll on its owner's shoulder (world/Shoulder)
U["message.matriochka.shoulder.on"] = ("%s climbs onto your shoulder.", "%s grimpe sur ton épaule.")
U["message.matriochka.shoulder.off"] = ("%s climbs down from your shoulder.", "%s descend de ton épaule.")
U["tooltip.matriochka.trophy_shoulder"] = ("Use it to set it on your shoulder.", "Utilise-la pour la poser sur ton épaule.")
U["message.matriochka.rite.no_room"] = ("There is no room for it here.", "Il n'y a pas la place ici.")
U["message.matriochka.rite.place.4"] = ("The Storm Rod goes on top of a lightning rod.", "Le Paratonnerre d'orage se pose au sommet d'un paratonnerre.")
U["message.matriochka.rite.place.7"] = ("The Abyssal Pearl must go into the water.", "La Perle abyssale doit aller dans l'eau.")
U["message.matriochka.rite.place.8"] = ("The Sapling of the Four Seasons is planted on grass or dirt.", "L'Arbrisseau des quatre saisons se plante sur de l'herbe ou de la terre.")
U["message.matriochka.rite.place.9"] = ("The Seismic Stake is driven into stone, below y 40.", "Le Pieu sismique s'enfonce dans la pierre, sous y 40.")
# ---------------------------------------------------------------- the wonders' rumours (world/Rumors.java)
U["rumor.matriochka.dir.north"] = ("north", "au nord")
U["rumor.matriochka.dir.north_east"] = ("north-east", "au nord-est")
U["rumor.matriochka.dir.east"] = ("east", "à l'est")
U["rumor.matriochka.dir.south_east"] = ("south-east", "au sud-est")
U["rumor.matriochka.dir.south"] = ("south", "au sud")
U["rumor.matriochka.dir.south_west"] = ("south-west", "au sud-ouest")
U["rumor.matriochka.dir.west"] = ("west", "à l'ouest")
U["rumor.matriochka.dir.north_west"] = ("north-west", "au nord-ouest")
U["rumor.matriochka.dist.near"] = ("Not far at all", "Pas loin du tout")
U["rumor.matriochka.dist.far"] = ("A good walk", "Une bonne marche")
U["rumor.matriochka.dist.very_far"] = ("A long way", "Très loin")
U["npc.matriochka.rumor.1"] = ("Go %s and look up: a tree taller than the spores, hollow at its foot. %s.", "Va %s et lève les yeux : un arbre plus haut que les spores, creux à son pied. %s.")
U["npc.matriochka.rumor.2"] = ("The rock beats somewhere %s, like a heart in the lava. %s.", "La roche bat quelque part %s, comme un cœur dans la lave. %s.")
U["npc.matriochka.rumor.3"] = ("There is a hall to the %s where they hang the keys nobody came back for. %s.", "Il y a une salle %s où l'on pend les clés que personne n'est revenu chercher. %s.")
U["npc.matriochka.rumor.4"] = ("Somewhere %s the wind goes quiet, inside a ring of pillars that stand on nothing. %s.", "Quelque part %s, le vent se tait, dans un cercle de piliers posés sur rien. %s.")
U["npc.matriochka.rumor.5"] = ("One candle still burns to the %s. The Deep has not drunk it yet. %s.", "Une bougie brûle encore, %s. Les Profondeurs ne l'ont pas encore bue. %s.")
U["npc.matriochka.rumor.6"] = ("Look %s: a spire hangs point down from a rock in the sky. %s.", "Regarde %s : une flèche pend la pointe en bas d'un rocher dans le ciel. %s.")
U["npc.matriochka.rumor.7"] = ("Under the water to the %s, a bell rings that nobody rings. %s.", "Sous l'eau, %s, une cloche sonne sans que personne ne la sonne. %s.")
U["npc.matriochka.rumor.8"] = ("Out %s stands a clock that stopped when the seasons started running. %s.", "Là-bas, %s, se dresse une horloge arrêtée quand les saisons se sont mises à courir. %s.")
U["npc.matriochka.rumor.9"] = ("The ground sleeps out %s. Something huge breathes under it. %s.", "Le sol dort, là-bas %s. Quelque chose d'énorme respire dessous. %s.")
U["npc.matriochka.rumor.10"] = ("The Artisan's own desk stands to the %s, as big as a hill. %s.", "Le bureau de l'Artisan lui-même se dresse %s, grand comme une colline. %s.")
U["journal.matriochka.card.rumor"] = ("Its people say the wonder stands near %s, %s.", "Ses habitants disent que la merveille se dresse vers %s, %s.")
U["journal.matriochka.card.rumor_none"] = ("Ask the world's people where its wonder stands.", "Demande aux habitants du monde où se dresse sa merveille.")
U["message.matriochka.reliquary.shared"] = ("%s opened the reliquary for the group: %s is yours too.", "%s a ouvert le reliquaire pour le groupe : %s est à toi aussi.")
# the Journal's map, from a world card (client/JournalMap, world/Atlas)
U["journal.matriochka.map.open"] = ("Map", "Carte")
U["journal.matriochka.map.items"] = ("Items", "Objets")
U["journal.matriochka.map.title"] = ("Map of %s", "Carte : %s")
U["journal.matriochka.map.empty"] = ("Not a step taken here yet. Walk this world and the Journal inks in the ground you cross.", "Pas encore un pas ici. Parcours ce monde et le Journal encre le terrain que tu traverses.")
U["journal.matriochka.map.you"] = ("You are here", "Tu es ici")
U["journal.matriochka.map.explored"] = ("%s regions inked", "%s régions encrées")
U["journal.matriochka.map.legend"] = ("Places found", "Lieux trouvés")
U["journal.matriochka.map.elsewhere"] = ("Another world: this map waits for you.", "Autre monde : cette carte t'attend.")
U["journal.matriochka.map.role.utility"] = ("People", "Peuples")
U["journal.matriochka.map.role.combat"] = ("Combat", "Combat")
U["journal.matriochka.map.role.exploration"] = ("Exploration", "Exploration")
U["journal.matriochka.map.role.story"] = ("Story", "Histoire")
U["journal.matriochka.map.role.secret"] = ("Secret", "Secret")
U["journal.matriochka.map.role.wonder"] = ("Wonder", "Merveille")
# the ten world ores, the Nesting Cradle and the Matriarch Armour (world/WorldOres, block/NestingCradle, gear/Matriarch)
U["message.matriochka.ember.out"] = ("The ember goes out in your cold hands: only ash is left. Mine it with your Heat at 70 or more.", "La braise s'éteint dans tes mains froides : il ne reste que de la cendre. Mine-la avec ta Chaleur à 70 ou plus.")
U["message.matriochka.silent.shattered"] = ("The stone heard you and shattered. Mine it in silence: sneak until your Noise is 0.", "La pierre t'a entendu et s'est brisée. Mine-la en silence : accroupis-toi jusqu'à un Bruit de 0.")
U["message.matriochka.inverted.rises"] = ("The ore falls upwards: catch it!", "Le minerai tombe vers le haut : attrape-le !")
U["message.matriochka.fulgurite.formed"] = ("The lightning fused the ground into fulgurite.", "La foudre a fondu le sol en fulgurite.")
U["message.matriochka.time_seed.world"] = ("A Time Seed only takes root in the Hastened Seasons, World 8.", "Une Graine du temps ne prend racine que dans les Saisons accélérées, au monde 8.")
U["message.matriochka.time_seed.soil"] = ("Plant it on grass or dirt, with room above.", "Plante-la sur de l'herbe ou de la terre, avec de la place au-dessus.")
U["message.matriochka.cradle.not_ore"] = ("The cradle only takes the ores of the ten worlds, one of each.", "Le berceau ne prend que les minerais des dix mondes, un de chaque.")
U["message.matriochka.cradle.has"] = ("The cradle already holds the ore of World %s.", "Le berceau tient déjà le minerai du monde %s.")
U["message.matriochka.cradle.set"] = ("%s takes its place on the ring (%s / 10).", "%s prend sa place sur l'anneau (%s / 10).")
U["message.matriochka.cradle.busy"] = ("The dolls are closing: wait for them.", "Les poupées se referment : attends-les.")
U["message.matriochka.cradle.taken"] = ("You take back %s.", "Tu reprends %s.")
U["message.matriochka.cradle.born"] = ("The ten dolls have closed: a Matriochkite Ingot is born.", "Les dix poupées se sont refermées : un Lingot de matriochkite est né.")
U["message.matriochka.matriarch.cracked"] = ("The outer doll cracks: the Nested Shell took the blow.", "La poupée extérieure se fend : la Coquille gigogne a pris le coup.")
U["tooltip.matriochka.matriarch.bonus1"] = ("Whole set: every world's gauge builds half as fast.", "Toute l'armure : les jauges des mondes montent deux fois moins vite.")
U["tooltip.matriochka.matriarch.bonus2"] = ("Every 5 min, a deadly blow leaves you at 3 hearts.", "Toutes les 5 min, un coup mortel te laisse à 3 cœurs.")
U["tooltip.matriochka.matriarch.set"] = ("Matriarch Armour, %s of 4 worn:", "Armure de la Matriarche, %s sur 4 portées :")
U["tooltip.matriochka.matriarch.ready"] = ("Nested Shell: ready", "Coquille gigogne : prête")
U["tooltip.matriochka.matriarch.mending"] = ("Nested Shell: mending, %s", "Coquille gigogne : se reforme, %s")
U["tooltip.matriochka.matriarch.idle"] = ("Nested Shell: wear the whole set", "Coquille gigogne : porte toute l'armure")
U["tooltip.matriochka.chain"] = ("Ten ores \u2192 Nesting Cradle \u2192 Matriochkite \u2192 Matriarch Armour", "Dix minerais \u2192 Berceau gigogne \u2192 Matriochkite \u2192 Armure de la Matriarche")
U["journal.matriochka.card.chain"] = ("Ten ores, one of each world \u2192 the Nesting Cradle \u2192 a Matriochkite Ingot \u2192 the Matriarch Armour", "Dix minerais, un par monde \u2192 le Berceau gigogne \u2192 un Lingot de matriochkite \u2192 l'Armure de la Matriarche")
# where you are, without a corner plaque (client/WorldTitle)
U["hud.matriochka.world_rule"] = ("Rule: %s", "Règle : %s")
U["hud.matriochka.world_label"] = ("World %s \u00b7 %s", "Monde %s \u00b7 %s")
U["options.matriochka.button"] = ("Matriochka...", "Matriochka...")
U["debug.matriochka.world"] = ("Matriochka: World %s - %s", "Matriochka : monde %s - %s")
en = {k: v[0] for k, v in U.items()}
fr = {k: v[1] for k, v in U.items()}
d = os.path.join(os.path.dirname(__file__), "lang")
json.dump(en, open(os.path.join(d, "en_us.json"), "w"), indent=1, ensure_ascii=False)
json.dump(fr, open(os.path.join(d, "fr_fr.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(U))
