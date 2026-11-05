# Matriochka — Document de conception

Nov 4, 2026 · @leo

## Vision

Matriochka est un mod Minecraft de progression, jouable en solo et en multijoueur, où chaque monde est enfermé dans un bloc. Le joueur traverse 10 mondes de plus en plus difficiles, chacun avec ses règles, ses mobs, ses objets, ses machines et son boss.

### Pitch

Chaque bloc peut contenir un monde. Ton monde lui-même n'est peut-être qu'un objet dans un monde plus grand. Fabrique une Graine, fais-la éclore, entre dans le bloc, survis, bats son boss, et descends encore.

### Promesse au joueur

- **Découvrir :** chaque monde change la manière de jouer, pas seulement le décor.
- **Progresser :** chaque boss débloque de nouveaux crafts, de l'équipement et une part de l'histoire.
- **Choisir :** le karma, les classes et les variantes de mondes créent des parties différentes.
- **Fouiller :** poupées cachées, pages codées et monde secret récompensent les joueurs attentifs.
- **Partager :** les combats, trahisons et découvertes créent des moments à vivre entre amis et à diffuser.

### Piliers de conception

| Pilier | Règle | Conséquence |
| --- | --- | --- |
| Tout s'emboîte | Une chose peut toujours en contenir une autre | Mondes, boss, mobs, coffres, armures et vies reprennent cette idée |
| Une règle par monde | Chaque monde apporte une contrainte unique | Le joueur doit changer de méthode à chaque étape |
| Difficulté apprise | La mort doit apprendre quelque chose | Attaques annoncées, schémas lisibles, bonne préparation récompensée |
| Progression logique | Un blocage doit avoir une raison visible | Les ressources et machines se trouvent là où elles ont du sens |
| Immersion totale | Le monde raconte son histoire | Décors, sons, animations et interfaces remplacent les longs textes |

### Inspirations et positionnement

Le modèle de progression s'inspire de RLCraft : contenus personnalisés, crafts limités et avancement lent. La différence principale reste le lien entre les échelles, puisque ce qui se passe dans un bloc modifie le monde extérieur, et inversement.

L'Aether sert de référence pour un monde entièrement transformé, mais le monde 4 doit garder sa propre identité. Aucun équivalent direct n'a été trouvé lors des recherches, sans que cela prouve que le concept soit totalement inédit.

### Concepts écartés

- **Clones temporels :** déjà bien couverts par plusieurs mods.
- **Monde vivant ou colosse géant :** terrain déjà occupé par plusieurs projets.
- **Réseau de mondes connectés :** proposé puis abandonné.
- **Lois physiques secrètes par monde :** intéressantes, mais non retenues pour Matriochka.

## Boucle de jeu et échelles

La boucle principale consiste à préparer une Graine, conquérir son monde, récupérer le noyau du boss, puis ouvrir le monde suivant. Le lien entre l'intérieur et l'extérieur du bloc rend cette boucle propre à Matriochka.

### Boucle principale

1. Le joueur réunit les ingrédients de la Graine suivante.
2. Il fabrique la Graine sur l'Établi matriciel.
3. Il la pose, puis la nourrit jusqu'à l'ouverture du bloc-monde.
4. Il entre avec un équipement insuffisant et découvre la règle du monde.
5. Il apprend à survivre face aux mobs et à l'environnement.
6. Il récolte les ressources et fabrique l'équipement adapté.
7. Il explore le monde et trouve les pages, poupées et secrets.
8. Il affronte le boss, puis récupère son noyau.
9. Le noyau débloque de nouveaux crafts et modifie la base du joueur.
10. Le noyau devient l'ingrédient clé de la Graine suivante.

### Rythme des récompenses

| Durée | Le joueur obtient |
| --- | --- |
| Quelques minutes | Un nouveau matériau, un mob découvert, un indice |
| Une session | Une machine, une armure, un objet ou une amélioration de classe |
| Un monde | Un boss vaincu, un noyau, une révélation et une nouvelle Graine |
| Toute la partie | Le karma, les poupées cachées, le monde 0 et une fin |

La durée cible est de 60 à 80 heures pour une première partie, à ajuster pendant les tests.

### Effets entre les échelles

Un bloc-monde n'est pas un simple portail : il garde un lien permanent avec ce qui l'entoure.

| Sens | Exemple | Effet |
| --- | --- | --- |
| De l'intérieur vers l'extérieur | Volcan actif | Le bloc chauffe et peut enflammer les environs |
| De l'intérieur vers l'extérieur | Grande rivière | Le bloc fuit et mouille la zone autour |
| De l'intérieur vers l'extérieur | Combat de boss | Le bloc tremble et se fissure à la surface |
| De l'extérieur vers l'intérieur | Bloc déplacé | Un séisme frappe le monde miniature |
| De l'extérieur vers l'intérieur | Bloc chauffé ou refroidi | La température intérieure change |
| De l'extérieur vers l'intérieur | Bloc alimenté en redstone | Certaines machines intérieures réagissent |

### Choix d'emplacement

Comme le monde reste lié à son bloc, l'emplacement de la Graine devient une vraie décision. Une Graine chaude peut alimenter une forge, mais aussi mettre le feu à une base. Une Graine aquatique peut irriguer des cultures, mais aussi noyer un atelier.

### Variantes de mondes

Chaque Graine peut créer une variante selon ce que le joueur lui donne pendant son éclosion. Une version plus dangereuse peut offrir de meilleures ressources. Le karma peut aussi influencer ces variantes.

## Début de partie

Le joueur reçoit un Parchemin illustré dès sa première connexion, puis trouve le Gardien du bloc pour lancer la progression. Les 30 premières minutes doivent lui faire comprendre le concept sans long tutoriel.

### Parchemin de l'artisan

Le Parchemin arrive dans l'inventaire à la première connexion, et son écran s'ouvre automatiquement une seule fois. En multijoueur, chaque nouveau joueur reçoit le sien.

| Page | Sujet | Contenu |
| --- | --- | --- |
| 1 | Le principe | Chaque bloc peut contenir un monde |
| 2 | Ton objectif | Trouver le Gardien, obtenir son noyau et ouvrir le monde 1 |
| 3 | La progression | Fabriquer une Graine, entrer, battre le boss, recommencer |
| 4 | La survie | Mort, poupée de vie et Berceau d'âme |
| 5 | Les choix | Karma et classes, sans tout révéler |

- **Style :** il est écrit à la main par l'artisan et illustré de dessins.
- **Fermeture :** le joueur peut le quitter à tout moment et le rouvrir depuis son inventaire.
- **Perte :** il se refabrique avec du papier, pour un coût très faible.
- **Évolution :** il devient le Journal de l'artisan après la victoire contre le Gardien.
- **Objectif :** une ligne indique toujours la prochaine étape, sans donner la solution.

### Déroulé des 30 premières minutes

1. Le joueur lit le Parchemin, qui contient une carte esquissée.
2. Il récolte ses premières ressources, avec une progression limitée au fer.
3. Il suit la carte jusqu'au Sanctuaire du Gardien, généré à environ 200 blocs du point d'apparition.
4. Il active le sanctuaire, puis affronte le Gardien du bloc, boss d'introduction.
5. Le Gardien laisse son noyau et les plans de l'Établi matriciel.
6. Le Parchemin devient le Journal, et le livre de quêtes facultatif s'ouvre.
7. Le joueur prépare la Graine du monde 1.

### Gardien du bloc

Le Gardien est volontairement simple, pour apprendre la structure annonce, exécution et ouverture. Il possède 300 points de vie, inflige 12 points de dégâts avec ses attaques fortes et ne reçoit aucun multiplicateur de monde.

## Graines et déblocage des mondes

Chaque monde s'ouvre avec une Graine fabriquée à partir du noyau du boss précédent. Le joueur ne peut donc pas accéder directement au monde 5 sans avoir vaincu les mondes 1 à 4.

### Ordre de progression

1. Le joueur commence sur la Surface, avec une progression limitée au fer.
2. Il affronte le Gardien du bloc pour obtenir son noyau et l'Établi matriciel.
3. Il fabrique la Graine du monde 1.
4. Chaque noyau suivant permet de fabriquer la Graine du monde suivant.
5. Le noyau du monde 9 permet de créer la Graine du monde 10.

### Recettes

Les recettes sont des propositions à équilibrer. Le joueur doit toujours voir la prochaine Graine, avec les ingrédients manquants affichés en silhouette.

| Graine | Noyau requis | Ressources |
| --- | --- | --- |
| Monde 1 | Gardien du bloc | Fer, bûches |
| Monde 2 | Boss du monde 1 | Nouveau minerai du monde 1, spores |
| Monde 3 | Boss du monde 2 | Lingot de cendre, roche ardente |
| Monde 4 | Boss du monde 3 | Clé de donjon, fragment scellé |
| Monde 5 | Boss du monde 4 | Essence de tempête, cristal céleste |
| Monde 6 | Boss du monde 5 | Éclat d'ombre, fragment de diamant |
| Monde 7 | Boss du monde 6 | Alliage instable, cristal inversé |
| Monde 8 | Boss du monde 7 | Perle de pression, sel des profondeurs |
| Monde 9 | Boss du monde 8 | Sable temporel, fragment de saison |
| Monde 10 | Boss du monde 9 | Cœur de terrain, Clé de la dernière poupée |

### Ouverture d'une Graine

1. Le joueur bêche une Terre de monde à l'endroit choisi, puis y plante la Graine.
2. La Graine demande une condition liée à son monde, comme de l'eau, de la chaleur ou de la redstone.
3. Elle éclot après un court rituel accompagné d'animations et de sons.
4. Le bloc-monde apparaît et son monde devient accessible.

### Terre de monde

Une Graine se plante n'importe où, à condition d'être sur une Terre de monde bêchée. Cette terre a les mêmes propriétés que la terre de base de Minecraft.

- **Origine :** le Gardien du bloc donne la première Terre de monde, puis chaque monde fournit la sienne.
- **Correspondance :** la Graine d'un monde se plante sur la Terre du monde précédent.
- **Transport :** la terre se ramasse et se pose où le joueur veut, sauf dans une arène de boss.
- **Propriétés :** elle se bêche à la houe, s'hydrate près de l'eau et redevient de la terre si elle sèche ou si elle est piétinée.
- **Éclosion interrompue :** si la terre cesse d'être bêchée, la Graine retombe en objet, sans être perdue.
- **Après l'éclosion :** le bloc-monde remplace la Graine et ne dépend plus de l'état de la terre.
- **Déplacement :** une Poupée fêlée réparée se repose sans Terre de monde, pour rester peu punitive.

### Vérifications obligatoires

Le craft ne suffit pas à garantir la progression, car un ami pourrait donner sa Graine. Le mod doit donc vérifier :

- que le groupe a bien vaincu le boss précédent ;
- que le monde demandé correspond à la progression débloquée ;
- que les commandes de triche et les objets échangés ne contournent pas ces règles en mode survie.

### Blocages de contenu

Les blocages doivent paraître logiques. Le diamant, par exemple, n'est pas interdit par un message : ses ressources n'apparaissent qu'à partir du monde 5.

| Contenu | Déblocage proposé |
| --- | --- |
| Fer | Surface |
| Établi matriciel | Boss de la Surface |
| Enchantements | Après le monde 2 |
| Nether | Après le monde 2 |
| Diamant | Monde 5 |
| Vol et déplacements avancés | Monde 4 |
| Automatisation des stations | Tardivement, selon chaque machine |

## Mort, réapparition et bloc-monde

Un joueur mort réapparaît hors du monde, sauf s'il a activé un Berceau d'âme. Un bloc-monde cassé expulse ses occupants, mais le monde reste conservé et récupérable.

### Ordre de résolution d'une mort

1. Si la poupée de vie a encore une couche, elle se brise et le joueur revient à la vie sur place.
2. Sinon, il meurt et un coffre de mort conserve son inventaire à l'endroit de sa mort.
3. S'il a un Berceau d'âme chargé dans ce monde, il y réapparaît.
4. Sinon, il réapparaît hors du monde, à son point de réapparition habituel.

Le coffre de mort ne disparaît pas. Dans une arène de boss, il est placé à l'entrée de l'arène pour rester accessible.

### Berceau d'âme

Le Berceau d'âme permet de réapparaître à l'intérieur d'un monde. Il prend la forme d'un petit berceau en bois peint, dont la poupée s'ouvre quand le joueur revient. Il reste abordable, car il sert à fluidifier les expéditions et non à ralentir le joueur.

| Élément | Règle proposée |
| --- | --- |
| Fabrication | Établi matriciel, 4 planches, 2 ressources du monde, 1 fil de laine, 10 âmes |
| Charges | 3 réapparitions |
| Recharge | 1 ressource du monde et 5 âmes par charge |
| Limite | 1 Berceau actif par joueur et par monde |
| Restriction | Inutilisable dans une arène de boss |
| Vol | Seul son propriétaire ou son groupe peut le casser |

### Entrer et sortir d'un monde

Le joueur entre en utilisant le bloc-monde. Il arrive sur un Seuil, une plateforme de retour reconnaissable. Il peut repartir en y revenant, ou en utilisant un Fil de retour, un consommable simple qui le ramène au bloc-monde.

### Bloc-monde cassé

1. Tous les joueurs présents à l'intérieur sont expulsés, sans mourir ni perdre leur inventaire.
2. Le bloc donne une Poupée fêlée, liée à ce monde précis.
3. Le joueur la répare avec quelques ressources, puis la repose.
4. Le monde revient avec ses bases, ses coffres et ses boss déjà vaincus.
5. Il reste instable pendant 20 minutes, avec 50 % de mobs en plus.

Si la Poupée fêlée est perdue, le joueur refabrique la Graine, qui rouvre le même monde. L'ancienne poupée devient alors inutilisable. Il ne peut jamais exister deux accès au même monde, ce qui empêche les duplications.

Casser, puis reposer le bloc est aussi la façon normale de le déplacer. Le séisme prévu dans la section sur les échelles se déclenche alors à l'intérieur.

### Cas particuliers

| Situation | Résultat |
| --- | --- |
| Explosion, feu, lave | Le bloc-monde n'est pas endommagé |
| Piston ou gravité | Le bloc-monde ne bouge pas |
| Joueur extérieur au groupe | Il ne peut ni casser ni utiliser le bloc, sauf invitation |
| Joueur déconnecté à l'intérieur | Il est ramené près du bloc à sa reconnexion si le monde a été déplacé |
| Poupée fêlée détruite | Le monde reste conservé et se récupère avec la Graine |
| Mode hardcore | Une option peut supprimer définitivement le monde cassé |

Ces règles s'appliquent par défaut et doivent rester configurables par l'administrateur d'un serveur.

## Les 10 mondes

Les 10 mondes gardent des numéros en attendant leurs noms définitifs, et chacun apporte sa spécificité, ses mobs, ses objets et sa station de craft. Les noms restent provisoires. Les fiches citent les éléments principaux, et les onglets Bestiaire et Objets donnent le détail complet.

| Monde | Spécificité | Défi principal | Palier |
| --- | --- | --- | --- |
| 1 | Jungle toxique | Gérer une jauge de survie | Apprentissage |
| 2 | Minerais géants et chaleur | Gérer la température et l'équipement | Apprentissage |
| 3 | Uniquement des donjons, sans ciel | Pièges et ressources limitées | Apprentissage |
| 4 | Îles flottantes et tempêtes | Chute et vent | Maîtrise |
| 5 | Obscurité totale | Vision réduite | Maîtrise |
| 6 | Gravité instable | Combat en trois dimensions | Maîtrise |
| 7 | Océan sous pression | Oxygène, pression, menaces de tous côtés | Expertise |
| 8 | Temps accéléré | Jour, nuit et saisons changent en quelques minutes | Expertise |
| 9 | Terrain hostile | Le sol bouge, aucune base n'est sûre | Expertise |
| 10 | Monde géant | Toutes les règles précédentes | Examen final |

Chaque monde contient au minimum une règle unique, 5 mobs, un minerai ou une ressource clé, une armure, un outil ou une arme, une station, 10 types de structures, un boss, son noyau et sa poupée cachée.

### Monde 1

- **Spécificité :** une jungle dense où l'air devient toxique.
- **Règle :** une jauge de toxine monte selon les zones et les attaques subies.
- **Mobs :** Sporelins, rampeurs de racines, fleurs-pièges.
- **Ressources :** nouveau minerai, spores, racines.
- **Équipement :** masque filtrant, armure de chitine.
- **Station :** Cuve de spores.
- **Boss :** Reine des spores.
- **Déblocage :** poupée de vie à 1 couche.

### Monde 2

- **Spécificité :** des filons géants traversent le paysage et les minerais sont amplifiés.
- **Règle :** la chaleur augmente avec la profondeur et les grandes zones de minage.
- **Mobs :** Mineurs de cendre, filons vivants, salamandres de roche. Les premiers mobs gigognes apparaissent ici.
- **Ressources :** roche ardente, lingot de cendre, minerais géants.
- **Équipement :** foreuse, combinaison thermique.
- **Station :** Fonderie de cendre.
- **Boss :** Titan de cendre.
- **Déblocages :** coffres gigognes, enchantements et accès au Nether.

### Monde 3

- **Spécificité :** le monde est composé uniquement de donjons, sans surface ni ciel.
- **Règle :** les zones s'ouvrent avec des clés, et certaines salles se réorganisent.
- **Mobs :** Geôliers, sentinelles, serrures vivantes.
- **Ressources :** clés, cartes, fragments scellés.
- **Équipement :** kit de crochetage, armure de Geôlier.
- **Station :** Table du Geôlier.
- **Boss :** Grand Geôlier.
- **Déblocage :** poupée-refuge.

### Monde 4

- **Spécificité :** un archipel d'îles flottantes parcouru par des tempêtes.
- **Règle :** le vent modifie les déplacements et la foudre frappe les zones exposées.
- **Mobs :** Raies du vent, oiseaux-tempête, gardiens d'île.
- **Ressources :** essence de tempête, cristal céleste.
- **Équipement :** planeur, grappin, armure céleste.
- **Station :** Forge à foudre.
- **Boss :** Roi des tempêtes.
- **Déblocage :** armures à couches.

### Monde 5

- **Spécificité :** un monde plongé dans l'obscurité totale.
- **Règle :** la lumière s'épuise vite et attire certaines créatures.
- **Mobs :** Rôdeurs aveugles, dévoreurs de lueur, échos.
- **Ressources :** éclat d'ombre, diamant.
- **Équipement :** lanterne solaire alimentée par l'essence de tempête, sonar.
- **Station :** Autel obscur.
- **Boss :** Mangeur de lumière.
- **Déblocage :** poupée de vie à 2 couches.

### Monde 6

- **Spécificité :** la gravité change selon les zones et les événements.
- **Règle :** le haut, le bas et les chutes ne sont plus fiables.
- **Mobs :** Reflets, marcheurs de plafond, sphères instables.
- **Ressources :** alliage instable, cristal inversé.
- **Équipement :** bottes de gravité, armure miroir.
- **Station :** Inverseur.
- **Boss :** Ton Double.
- **Déblocage :** première mutation de boss.

### Monde 7

- **Spécificité :** un océan immense, profond et sous pression.
- **Règle :** l'oxygène et la pression limitent chaque expédition.
- **Mobs :** chasseurs abyssaux, bancs de lames, méduses de pression.
- **Ressources :** perle de pression, sel des profondeurs.
- **Équipement :** scaphandre, propulseur.
- **Station :** Presse abyssale, qui comprime des matériaux sous l'eau profonde.
- **Boss :** Léviathan de pression.
- **Déblocage :** agrandissement de la poupée-refuge.

### Monde 8

- **Spécificité :** le temps passe beaucoup plus vite.
- **Règle :** le jour, la nuit et les saisons changent en quelques minutes, avec des ennemis et ressources différents.
- **Mobs :** créatures saisonnières, vieillards du sablier, ombres du crépuscule.
- **Ressources :** sable temporel, fragment de saison.
- **Équipement :** sablier, armure saisonnière.
- **Station :** Atelier du temps, utilisable seulement à certains moments.
- **Boss :** Maître des saisons.
- **Déblocage :** poupée de vie à 3 couches.

### Monde 9

- **Spécificité :** le terrain lui-même est hostile.
- **Règle :** le sol se déplace, se referme et détruit les constructions non ancrées.
- **Mobs :** blocs rampants, mimiques, dévoreurs de fondations.
- **Ressources :** cœur de terrain.
- **Équipement :** ancres, bottes d'accroche, armure de roche vivante.
- **Station :** Ancre de terrain, qui stabilise une zone limitée.
- **Boss :** Cœur du terrain.
- **Déblocage :** Clé de la dernière poupée.

### Monde 10

- **Spécificité :** le joueur sort du dernier bloc et découvre un monde géant, où sa base devient un simple objet.
- **Règle :** les zones reprennent les règles des mondes précédents, et chaque ancien équipement sert au moins une fois.
- **Mobs :** versions géantes et mutées des créatures précédentes.
- **Ressources :** matériaux finaux liés aux dix enveloppes du boss.
- **Équipement :** équipement final choisi selon la classe et le karma.
- **Station :** Métier final, qui assemble les matériaux des anciens mondes.
- **Boss :** boss final gigogne à dix enveloppes.
- **Déblocage :** première fin du jeu et accès au dernier secret si les poupées sont réunies.

### Structures par monde

Chaque monde possède 10 types de structures différents, soit 100 types au total sur l'ensemble du jeu. L'onglet Structures donne le rôle, la taille, la rareté et le contenu de chacun. Chaque type a son architecture, ses mobs, ses récompenses et sa raison d'exister. Les noms ci-dessous restent provisoires.

| Monde | 10 types de structures |
| --- | --- |
| 1 | Ruche de spores, arbre creux, temple racinaire, serre abandonnée, nid de Sporelins, clairière purifiée, puits de toxine, village de cueilleurs, cocon géant, sanctuaire de l'artisan |
| 2 | Mine effondrée, forge abandonnée, camp de mineurs, puits de lave, sanctuaire du filon, rail suspendu, fournaise géante, cristallerie, caverne de salamandres, atelier de l'artisan |
| 3 | Prison, salle des clés, labyrinthe de pièges, cour des Geôliers, bibliothèque scellée, arène, crypte, salle mobile, trésorerie, cellule de l'artisan |
| 4 | Phare des tempêtes, temple céleste, pont brisé, nid de raies, ruine suspendue, observatoire, paratonnerre géant, village flottant, épave volante, jardin des nuages |
| 5 | Tour éteinte, sanctuaire aveugle, mine sans fond, village silencieux, nid de rôdeurs, puits de lumière, cimetière d'échos, galerie de fresques, cathédrale noire, abri de l'artisan |
| 6 | Tour inversée, cité au plafond, laboratoire de gravité, salle des miroirs, escalier impossible, cage suspendue, jardin flottant, bassin renversé, noyau instable, refuge des Reflets |
| 7 | Épave, cité engloutie, cloche de plongée, récif mort, temple abyssal, station de pression, fosse des chasseurs, phare sous-marin, grotte à air, coffre-fort des profondeurs |
| 8 | Horloge géante, ville accélérée, serre des saisons, ruine vieillissante, camp éphémère, observatoire solaire, bibliothèque des siècles, jardin figé, tombeau temporel, marché du crépuscule |
| 9 | Fort ancré, ruine mouvante, gouffre vivant, tour qui marche, nid de mimiques, forteresse mobile, village enseveli, sanctuaire stable, veine battante, arène de terrain |
| 10 | Établi titanesque, poupée effondrée, coffre géant, atelier géant de l'artisan, cité des géants, tour d'aiguilles, bibliothèque colossale, porte de bloc, forge colossale, trône de la créature |

#### Rôle des structures

Chaque monde peut suivre cette répartition, à ajuster selon sa règle :

| Rôle | Types par monde | Exemple de contenu |
| --- | --- | --- |
| Combat | 3 | Vagues de mobs, mini-boss, défis d'arène |
| Exploration et butin | 3 | Coffres, ressources rares, pièges |
| Histoire | 2 | Fresques, pages du journal, révélations |
| Utilité | 1 | Point de repos, marchand, station ou recette |
| Secret | 1 | Poupée cachée, salle dissimulée, énigme |

#### Règles de conception

- Deux types du même monde ne doivent pas se jouer de la même façon.
- Chaque structure reprend la règle de son monde. Par exemple, une structure du monde 5 demande de gérer sa lumière.
- Les plus grandes structures sont rares, tandis que les petites rythment l'exploration.
- Chaque type peut avoir plusieurs variantes pour éviter les répétitions.
- Les poupées cachées et les pages du journal se trouvent principalement dans les structures.

## Boss et combats

Chaque boss doit proposer un combat reconnaissable, avec ses propres attaques, phases, sons et animations. Le joueur progresse en lisant les schémas, pas uniquement en augmentant ses statistiques.

### Structure d'une attaque

1. **Annonce :** une animation et un son préviennent le joueur.
2. **Exécution :** l'attaque est rapide, dangereuse et lisible.
3. **Ouverture :** le boss reste vulnérable pendant un court instant.

Le boss choisit ses attaques selon la distance, sa phase, son environnement et ses actions récentes. Il évite de répéter le même schéma, sans devenir imprévisible au point d'être injuste.

### Boss par monde

| Monde | Boss | Principe | Attaques | Phase finale |
| --- | --- | --- | --- | --- |
| Surface | Gardien du bloc | Ondes de choc et terrain | Frappes au sol, blocs arrachés, fissures | Il se reconstruit avec les blocs de l'arène |
| 1 | Reine des spores | Poison et contrôle du terrain | Racines sous les pieds, nuages toxiques, invocation de Sporelins | Elle s'enferme dans un cocon protégé par des nœuds |
| 2 | Titan de cendre | Force et lave | Coups massifs, projections de cendre, lave montante | Son armure fond et laisse son cœur exposé |
| 3 | Grand Geôlier | Pièges et enfermement | Chaînes, cages, murs mobiles, clés à récupérer | L'arène devient une cellule qui se referme |
| 4 | Roi des tempêtes | Vent et foudre | Bourrasques, éclairs annoncés, îlots détruits | Le combat se poursuit sur des débris en mouvement |
| 5 | Mangeur de lumière | Peur et obscurité | Éteint les lumières, frappe depuis le noir | Le joueur se repère au son et à ses dernières lumières |
| 6 | Ton Double | Miroir du joueur | Copie les armes, l'armure et les attaques | La gravité change et le Double adopte ton style de jeu |
| 7 | Léviathan de pression | Combat sous-marin | Aspirations, charges, zones de pression | La profondeur augmente et réduit l'oxygène |
| 8 | Maître des saisons | Changement de rythme | Attaques liées à l'heure et à la saison | Les cycles s'accélèrent jusqu'à se superposer |
| 9 | Cœur du terrain | Arène hostile | Vagues de sol, murs vivants, gouffres | Le sol disparaît par sections et le cœur se déplace |
| 10 | Boss final gigogne | Synthèse | Une enveloppe par monde, avec ses anciennes attaques | Sa dernière forme est minuscule et redoutable |

Les attaques des boss des mondes 7 à 9 sont des propositions à valider.

### Le boss final

Le boss du monde 10 possède dix enveloppes. Chaque enveloppe brisée change sa forme et reprend les attaques d'un ancien boss. Ce combat doit vérifier ce que le joueur a appris pendant toute la partie.

### Mutations de boss

À partir du monde 6, certains boss peuvent recevoir une mutation selon le karma ou la variante du monde. Une mutation ajoute une nouvelle attaque ou modifie une phase, sans remplacer le combat de base.

### Immersion en combat

- Tremblements, ralentis et impacts restent brefs et lisibles.
- La musique évolue selon la phase.
- L'arène réagit aux attaques et aux choix du joueur.
- Le bloc tremble à la surface pendant un combat à l'intérieur.
- Une personne restée dehors voit les dégâts et peut intervenir.

### Critères de validation d'un boss

- Il possède un modèle, des textures et des animations uniques.
- Le joueur peut reconnaître chaque attaque avant de la subir.
- Les phases modifient vraiment la façon de combattre.
- Il dispose d'au moins une attaque liée à la règle de son monde.
- Une mort permet de comprendre ce qu'il fallait changer.

## Difficulté et multiplicateurs

La vie, les dégâts et la vitesse d'attaque des mobs augmentent à chaque monde. Ces valeurs servent de base de travail et seront ajustées pendant les tests.

&#91;embedded content: calculé avec les formules de ce document · mondes 1 à 10\]

### Formules

- **Vie :** `base × 1,35^(monde - 1)`
- **Dégâts :** `base × 1,20^(monde - 1)`
- **Vitesse d'attaque :** `base × (1 + 0,06 × (monde - 1))`

Ces multiplicateurs s'appliquent aux mobs et aux boss. Ils doivent rester configurables pour simplifier l'équilibrage.

### Paliers de difficulté

| Mondes | Palier | Attentes |
| --- | --- | --- |
| 1 à 3 | Apprentissage | Un danger principal, annonces d'attaque longues, mort peu punitive |
| 4 à 6 | Maîtrise | Deux dangers à la fois, mobs en groupe, boss plus rapides |
| 7 à 9 | Expertise | Combats longs, arènes changeantes, erreurs coûteuses |
| 10 | Examen final | Toutes les compétences acquises pendant la partie |

### Ce qui évolue avec les chiffres

Les multiplicateurs ne suffisent pas à rendre un combat intéressant. La difficulté doit aussi passer par le nombre d'attaques, leurs schémas, la pression de l'environnement et l'intelligence des mobs.

Le joueur gagne en puissance à chaque monde, mais les ennemis progressent un peu plus vite que lui. L'équipement, les classes et les connaissances doivent compenser cet écart.

### Équilibrage du joueur

Les classes et leurs améliorations équilibrent le joueur, à condition que chaque monde apporte aussi un nouvel équipement. Avec les classes seules, un mob de référence demanderait 28 coups au monde 10.

&#91;embedded content: calcul sur un mob de 20 PV de base et une arme de 7 dégâts · mondes 1 à 10\]

Les classes restent donc un bonus de spécialisation. L'équipement de base du monde compense la montée de la vie et des dégâts adverses.

| Monde | Arme, dégâts | Armure | Robustesse | PV bonus | Bonus de classe max |
| --- | --- | --- | --- | --- | --- |
| 1 | 7 | 16 | 1 | 0 | 0 % |
| 2 | 9 | 17 | 2 | 0 | 0 % |
| 3 | 11 | 18 | 3 | 2 | +10 % |
| 4 | 13 | 19 | 4 | 4 | +10 % |
| 5 | 16 | 20 | 6 | 6 | +20 % |
| 6 | 19 | 22 | 8 | 8 | +20 % |
| 7 | 23 | 24 | 10 | 12 | +35 % |
| 8 | 28 | 26 | 12 | 16 | +35 % |
| 9 | 33 | 28 | 14 | 20 | +50 % |
| 10 | 40 | 30 | 16 | 24 | +50 % |

Ces valeurs correspondent à un joueur bien équipé en arrivant dans chaque monde. Le joueur garde sa base de 20 PV.

| Mesure | Monde 1 | Monde 5 | Monde 10 |
| --- | --- | --- | --- |
| Coups pour tuer un mob de référence | 2,9 | 3,5 | 5 |
| Coups de mob avant la mort | 8,9 | 7,9 | 8,5 |
| Coups forts de boss avant la mort | 2,9 | 2,2 | 3,3 |

Les coups forts restent très dangereux à tous les niveaux, ce qui rend les annonces d'attaque essentielles. Ces calculs supposent une armure complète, une arme de classe Berserker et la formule d'armure de Minecraft. Ils devront être confirmés en jeu.

### Mob et boss de référence

- **Mob de référence :** 20 PV et 5 de dégâts avant multiplicateurs.
- **Boss de référence :** 500 PV et 12 de dégâts pour un coup fort, avant multiplicateurs.
- **Boss final :** 1 000 PV de base, soit 14 894 PV répartis entre 10 enveloppes.

### Boss en multijoueur

| Joueurs | Vie du boss | Vitesse d'attaque |
| --- | --- | --- |
| 1 | ×1 | ×1 |
| 2 | ×1,6 | ×1,05 |
| 4 | ×2,8 | ×1,15 |
| 8 | ×5,2 | ×1,35 |

Les formules sont `1 + 0,6 × (joueurs - 1)` pour la vie et `1 + 0,05 × (joueurs - 1)` pour la vitesse.

### Budget d'âme

Monter une pièce au niveau 5 coûte 400 âmes, soit 2 400 âmes pour 6 pièces. Un objectif d'environ 300 âmes par monde permet de finir un ensemble complet vers le monde 8, ce qui correspond à la limite de niveau 5.

## Stations de craft

Chaque monde ajoute une station avec une mécanique propre, afin d'éviter de simples copies du four ou de l'établi. Le joueur doit comprendre ce qui rend chaque bloc différent dès sa première utilisation.

| Origine | Bloc | Rôle | Mécanique |
| --- | --- | --- | --- |
| Base | Établi matriciel | Fabrique les Graines | Les recettes se débloquent avec les noyaux |
| Base | Table de classe | Améliore les équipements | Augmente le niveau de classe |
| Base | Autel des âmes | Gère l'âme et le karma | Purifie ou dévore les objets |
| Monde 1 | Cuve de spores | Crée antidotes et cultures | Le résultat dépend du temps de fermentation |
| Monde 2 | Fonderie de cendre | Fond les minerais géants | Il faut maintenir la bonne température |
| Monde 3 | Table du Geôlier | Crée clés, pièges et cartes | Il faut reproduire le motif d'une serrure |
| Monde 4 | Forge à foudre | Charge l'équipement | La machine doit recevoir un éclair |
| Monde 5 | Autel obscur | Enchante et transforme | Il fonctionne seulement dans le noir complet |
| Monde 6 | Inverseur | Échange les propriétés de deux objets | Le gain s'accompagne toujours d'un défaut |
| Monde 7 | Presse abyssale | Comprime les matériaux | Elle demande une profondeur minimale |
| Monde 8 | Atelier du temps | Accélère ou fige certains crafts | Il n'accepte des recettes qu'à certains moments |
| Monde 9 | Ancre de terrain | Stabilise une zone | Elle protège une petite zone contre le terrain mobile |
| Monde 10 | Métier final | Assemble l'équipement final | Il utilise les matériaux de plusieurs mondes |

Les stations des mondes 7 à 10 sont des propositions à valider. Le Berceau d'âme n'est pas une station de craft : il est décrit dans la section sur la mort.

### Règles de conception

- **Une mécanique par bloc :** chaque machine doit pouvoir s'expliquer en une phrase.
- **Dépendance entre les stations :** une pièce de la Fonderie peut servir à fabriquer la Forge à foudre.
- **Ancrage dans le monde :** une machine peut exiger les conditions de son monde, ou une amélioration qui permet de l'utiliser ailleurs.
- **Immersion :** chaque station possède ses animations, ses sons et son interface.
- **État visible :** le joueur peut voir l'état d'une machine sans ouvrir son menu.
- **Automatisation tardive :** les premiers crafts se font à la main pour préserver l'intérêt de la mécanique.

### Hiérarchie des objets

Chaque nouvel objet doit répondre à un problème du monde actuel ou préparer le suivant. La lanterne solaire, par exemple, utilise l'énergie des tempêtes du monde 4 pour survivre dans le monde 5.

## Puissance d'âme et karma

Chaque objet possède une valeur d'âme selon sa rareté, et le joueur décide s'il la purifie ou la dévore. Ce choix fait évoluer son karma entre -100 et +100.

### Valeur d'âme

| Rareté | Âme |
| --- | --- |
| Commun | 1 |
| Rare | 10 |
| Épique | 30 |
| Légendaire | 100 |

### Autel des âmes

Le joueur dépose un objet sur l'Autel des âmes et effectue un choix définitif :

- **Purifier l'objet :** son âme est libérée et le joueur gagne du karma positif.
- **Dévorer l'objet :** son âme est absorbée et le joueur gagne du karma négatif.

L'objet utilisé est consommé. L'âme obtenue sert aussi aux améliorations d'équipement.

### Actions qui modifient le karma

| Action | Karma |
| --- | --- |
| Purifier un objet | +1 par tranche de 10 âmes |
| Dévorer un objet | -1 par tranche de 10 âmes |
| Sauver un PNJ | +5 |
| Épargner une créature prévue par une quête | +3 |
| Tuer un innocent | -5 |
| Accomplir un rituel interdit | -10 |

Les valeurs sont des points de départ à ajuster pendant les tests. Le rendement baisse quand le joueur répète la même action.

### Voies de karma

| Voie | Effets | Prix à payer |
| --- | --- | --- |
| Positive | PNJ accueillants, prix réduits, quêtes d'entraide | Rituels interdits et marchés clandestins fermés |
| Négative | Quêtes de pacte, marchés clandestins, butins interdits | PNJ méfiants, prix élevés, certains villages hostiles |

### Paliers

| Palier | Voie positive | Voie négative |
| --- | --- | --- |
| ±25 | Prix réduits de 10 % | Prix augmentés de 10 %, premier marché clandestin |
| ±50 | Quêtes d'entraide supplémentaires | Quêtes de pacte supplémentaires, villages méfiants |
| ±100 | Variantes de mondes liées à la voie positive | Variantes de mondes liées à la voie négative |

Les pouvoirs sont retirés pour le moment. Le karma agit donc sur le monde, les PNJ, les quêtes, les variantes et les fins, sans donner de sorts au joueur.

### Influence sur le jeu

- Le karma peut modifier les boss.
- Il peut changer certaines variantes de mondes.
- Il influence les réactions des PNJ.
- Il détermine une partie de la fin du jeu.

### Protections contre le farm

- **Objets renouvelables :** l'âme des objets issus de fermes doit être limitée.
- **Crafts :** un objet fabriqué ne peut pas valoir plus d'âme que ses ingrédients.
- **Rendement :** les objets répétés peuvent donner de moins en moins de karma.
- **Équilibre :** le système ne doit pas présenter une voie comme simplement bonne ou mauvaise.

## Classes d'équipement

Chaque arme, outil ou pièce d'armure reçoit une classe aléatoire lorsqu'elle est fabriquée. La Table de classe améliore ensuite cette classe, tandis qu'une Poupée du hasard permet d'en changer aléatoirement, pour un coût de plus en plus élevé.

### Classes de départ

| Classe | Attributs | Objets concernés |
| --- | --- | --- |
| Gardien | Armure, résistance au recul | Armures |
| Berserker | Dégâts, vitesse d'attaque | Armes, armures |
| Rôdeur | Vitesse de déplacement, esquive | Armures, armes légères |
| Moissonneur | Vol de vie, gain d'âme | Armes, armures |
| Survivant | Résistance aux effets des mondes, récupération après un coup | Armes, armures |
| Prospecteur | Vitesse de minage, chance de minerai | Outils |

Les bonus peuvent varier selon la pièce, pour éviter une armure complète trop simple à optimiser.

### Améliorer une classe

| Niveau visé | Bonus total | Coût en âme |
| --- | --- | --- |
| 2 | +10 % | 10 |
| 3 | +20 % | 30 |
| 4 | +35 % | 90 |
| 5 | +50 % | 270 |

Atteindre le niveau 5 depuis le niveau 1 coûte 400 âmes. Chaque amélioration demande aussi un matériau de boss, pour éviter qu'un seul farm permette de tout monter au maximum.

### Changer de classe

La Poupée du hasard est un consommable fabriqué à l'Établi matriciel. Elle tire une nouvelle classe au hasard, toujours différente de la classe actuelle et compatible avec l'objet. Le premier changement coûte aussi 20 âmes, puis ce prix double à chaque changement sur le même objet.

| Changement | Coût en âme |
| --- | --- |
| 1 | 20 |
| 2 | 40 |
| 3 | 80 |
| 4 | 160 |

Changer de classe conserve le niveau de classe, car le résultat est déjà aléatoire. Le coût qui double limite les relances.

### Limites selon la progression

| Progression | Niveau de classe maximal |
| --- | --- |
| Monde 2 terminé | 2 |
| Monde 4 terminé | 3 |
| Monde 6 terminé | 4 |
| Monde 8 terminé | 5 |

Les étapes des mondes 4 et 6 complètent les limites déjà prévues pour les mondes 2 et 8.

### Règles d'équilibre

- Le karma peut modifier légèrement les coûts, mais ne verrouille aucune classe.
- L'enclume et la réparation ne doivent pas permettre de contourner les coûts.
- Les doublons ne doivent pas se combiner pour créer gratuitement un meilleur objet.
- Le niveau de classe, la classe et le nombre de changements restent attachés à l'objet.

### Exigences techniques

Les attributs sont calculés côté serveur et affichés dans l'infobulle de l'objet. L'objet stocke sa classe, son niveau et son nombre de changements.

## Systèmes gigognes

Les contenus transversaux reprennent l'idée centrale du nom : quelque chose en contient toujours un autre. Ils se débloquent au fil de l'histoire et rendent le mod reconnaissable dès les premières minutes.

| Système | Effet | Déblocage |
| --- | --- | --- |
| Poupée de vie | Chaque couche permet de survivre à une mort | Mondes 1, 5 et 8 |
| Coffres gigognes | Un coffre peut en contenir un plus petit | Monde 2 |
| Mobs gigognes | Un mob vaincu en libère un plus petit | Monde 2 |
| Poupée-refuge | Une petite dimension sert de base de poche | Monde 3 |
| Armures à couches | Une couche protège la suivante | Monde 4 |
| Boss final gigogne | Dix enveloppes reprennent les anciens boss | Monde 10 |

### Poupée de vie

Le joueur porte une poupée à plusieurs couches. À sa mort, une couche se brise et il revient à la vie. Une fois la dernière couche brisée, il meurt et son inventaire reste sur place dans un coffre de mort récupérable.

- 1 couche après le monde 1
- 2 couches après le monde 5
- 3 couches après le monde 8

Ce système doit éviter qu'une erreur tardive annule des heures de progression, surtout à partir du monde 7.

### Poupée-refuge

La poupée-refuge est une base de poche conservée dans l'inventaire. Le joueur peut y entrer, stocker ses objets et installer ses machines. Elle s'agrandit au fil de la progression et reste inutilisable pendant les combats de boss.

### Mobs gigognes

À sa mort, un mob s'ouvre et libère une version plus petite et plus rapide. Certains peuvent contenir un objet rare ou une mauvaise surprise. Leur présence augmente à mesure que les mondes deviennent dangereux.

### Armures à couches

Une armure peut recevoir plusieurs couches de protection. Quand l'une casse, la suivante prend le relais. Ce système s'intègre aux classes et à leurs niveaux.

### Coffres gigognes

Chaque coffre peut en contenir un plus petit, avec des règles de tri par type d'objet. Ce système apporte une solution de stockage simple et immédiatement utile.

## PNJ, quêtes et succès

Les PNJ regroupent les villageois de la Surface et un nouveau peuple dans chaque monde. Les quêtes restent facultatives, et chaque monde propose 10 succès. Le détail complet se trouve dans les onglets dédiés.

### PNJ

- **Surface :** les villageois de Minecraft restent présents et réagissent au karma, avec en plus un Colporteur de poupées itinérant.
- **Mondes 1 à 10 :** chaque monde possède son propre peuple, ses villages, ses marchands et ses donneurs de quêtes.
- **Karma :** il modifie les prix, les quêtes disponibles et l'attitude des PNJ.

### Quêtes

- **Interface :** un onglet du Journal affiche les chapitres, les objectifs et les récompenses.
- **Facultatif :** aucune quête n'est nécessaire pour ouvrir un monde ou terminer le jeu.
- **Contenu :** 4 quêtes sur la Surface et 6 par monde, soit 64 quêtes au total.
- **Récompenses :** âme, ressources, recettes pratiques et cosmétiques, jamais d'objet indispensable.
- **Multijoueur :** une quête de groupe avance pour tous, et chacun récupère sa récompense.

### Succès

- **Volume :** un onglet par monde, avec 10 succès chacun, soit 100 au total.
- **Répartition :** 3 de progression, 3 d'exploration, 2 de combat ou de défi, 2 cachés.
- **Récompenses :** titres, cosmétiques ou un peu d'âme, pour que personne ne soit obligé de tout faire.

## Histoire, secrets et fins

L'histoire se révèle progressivement à travers les mondes, les pages du journal et les décors. Le joueur croit ouvrir une série de mondes, alors qu'il brise les prisons d'une créature.

### Révélations par monde

| Monde | Déblocage narratif | Ce que le joueur découvre |
| --- | --- | --- |
| 1 | Poupée de vie à 1 couche | Les mondes ont été fabriqués |
| 2 | Coffres gigognes | Chacun enferme quelque chose |
| 3 | Poupée-refuge | Un ancien artisan a laissé des plans |
| 4 | Armures à couches | L'artisan a voulu arrêter son œuvre |
| 5 | Poupée de vie à 2 couches | Une présence observe le joueur |
| 6 | Première mutation de boss | Les boss sont liés entre eux |
| 7 | Agrandissement du refuge | Les prisons servent à enfermer une seule créature |
| 8 | Poupée de vie à 3 couches | Quelqu'un est déjà passé par là |
| 9 | Clé de la dernière poupée | Ce voyageur, c'était toi |
| 10 | Boss final gigogne | En brisant les prisons, tu libères la créature |

### Narration dans le décor

Des ruines, fresques, ateliers abandonnés et objets disposés dans le monde racontent l'histoire sans longs textes. Les informations importantes doivent rester compréhensibles même sans lire toutes les pages.

### Journal de l'artisan

Le Parchemin de départ devient ce journal après le Gardien du bloc. Les pages sont dispersées dans les dix mondes, et certaines sont codées. Une fois réunies, elles racontent les événements passés et révèlent le chemin vers le monde 0.

### Poupées cachées

Dix poupées secrètes sont réparties dans les dix mondes. Certaines ne sont accessibles qu'avec des objets obtenus plus tard, ce qui encourage le joueur à revenir dans les anciens mondes.

Les poupées doivent être emboîtées dans le bon ordre pour ouvrir le monde 0. Chaque secret possède au moins trois indices, afin qu'il reste difficile sans dépendre uniquement d'un wiki.

### Monde 0

Le monde 0 est le plus petit, le plus dangereux et le mieux caché. Il pourrait révéler que le monde de départ n'était lui-même qu'une poupée de plus.

### Fins

| Fin | Condition | Résultat |
| --- | --- | --- |
| Sceller | Karma positif | Le joueur enferme de nouveau la créature |
| Absorber | Karma négatif | Le joueur absorbe son pouvoir |
| Troisième fin | Monde 0 terminé | Le joueur découvre la vérité finale |

### Identité des secrets

- Une poupée cachée par monde
- Des pages de journal à déchiffrer
- Des variantes liées au karma
- Une troisième fin réservée aux joueurs les plus attentifs

## Solo, multijoueur et hors ligne

Matriochka doit offrir la même progression en solo et sur serveur, sans service en ligne obligatoire. Le contenu reste identique, mais le multijoueur ajoute la coopération entre les échelles.

| Sujet | Solo | Multijoueur |
| --- | --- | --- |
| Exploration | Le joueur prépare seul ses expéditions | Le groupe peut se répartir entre l'intérieur et l'extérieur |
| Combats | Boss adapté à un joueur | Vie et attaques ajustées au nombre de joueurs |
| Mondes | Progression personnelle | Une Graine ouvre le monde à tout le groupe |
| Récompenses | Récompense personnelle | Participation au boss requise pour l'équipement du monde suivant |
| Histoire | Pages conservées par le joueur | Pages partagées, révélations personnelles réservées à chacun |

### Coopération entre les échelles

Un joueur peut rester géant pour protéger le bloc pendant que ses amis explorent l'intérieur. Il voit les dégâts à la surface et peut réagir. Il peut aussi secouer le bloc volontairement pour les aider, les gêner ou les trahir.

### Progression du groupe

La progression d'un monde est liée au groupe, pour éviter de refaire tous les boss. Un nouveau joueur doit toutefois participer au dernier boss pour obtenir l'équipement du monde suivant.

### Serveur et client

- Le serveur décide des attaques, des dégâts, de la progression et des récompenses.
- Le client affiche les animations, les effets, les sons et les interfaces.
- Le mod est installé sur le serveur et sur chaque client.

### Hors ligne

Toute la progression fonctionne sans connexion en solo. Le mod ne nécessite ni compte externe, ni backend, ni réseau de mondes.

## Direction artistique et immersion

Chaque monde doit être reconnaissable en une seule capture d'écran, tout en restant relié au style de la poupée gigogne. L'immersion passe par la cohérence des modèles, textures, sons et interfaces.

### Identité commune

- **Matières :** bois peint, laque, fissures et mécanismes d'emboîtement.
- **Motifs :** ornements peints sur les interfaces, noyaux, machines et poupées.
- **Sons :** ouverture, fermeture et craquement de poupée.
- **Interfaces :** cadres décorés, lisibles et cohérents avec chaque station.
- **Transitions :** ouverture du bloc, rétrécissement et entrée dans un monde.

### Identité par monde

| Monde | Palette | Particules | Ambiance sonore |
| --- | --- | --- | --- |
| 1 | Verts sombres, violets toxiques | Spores | Respiration végétale, insectes |
| 2 | Noirs, oranges, rouges | Braises, cendres | Marteaux, roche, chaleur |
| 3 | Pierre, métal, lueurs froides | Poussière | Chaînes, portes, échos |
| 4 | Bleus, blancs, jaunes | Vent, éclairs | Rafales, tonnerre |
| 5 | Noirs, bleus profonds | Rares lueurs | Silence, souffles, pas proches |
| 6 | Couleurs inversées | Fragments suspendus | Sons déformés |
| 7 | Bleus denses, turquoises | Bulles, sédiments | Pression, grondements lointains |
| 8 | Palette changeante | Feuilles, neige, sable | Tic-tac, cycles musicaux |
| 9 | Terre, chair minérale, rouges | Gravats | Battements, roche en mouvement |
| 10 | Mélange des mondes | Particules de tous les mondes | Thèmes précédents réunis |

Ces palettes servent de point de départ à la direction artistique.

### Immersion

- Le monde réagit aux actions du joueur.
- Les machines montrent leur état sans ouvrir de menu.
- Les mobs ont des animations et comportements propres.
- Les fresques et ruines font comprendre ce qui s'est passé.
- La musique dépend du monde, de la tension et de la phase du boss.
- Chaque déblocage est accompagné d'un effet visuel et sonore.

### Qualité attendue

Le premier boss sert de référence pour tout le mod. Une direction artistique précise doit être validée avant de produire les contenus suivants, afin d'obtenir le même niveau de qualité partout.

## Architecture technique

Le même mod fonctionne en solo et sur serveur, car toute la logique du jeu tourne côté serveur. Le client se charge de l'affichage, des interfaces, des sons et des effets.

&#91;embedded content: architecture du mod · serveur, client et ressources\]

En solo, cette logique tourne sur le serveur intégré de Minecraft. Il n'y a donc qu'une seule base de code à maintenir.

### Outils

| Besoin | Outil |
| --- | --- |
| Modèles, textures, animations | Blockbench |
| Animations complexes en jeu | GeckoLib |
| Affichage des recettes | EMI ou JEI |
| Code du mod | Java, Fabric et Fabric API |

Le mod vise la dernière version stable de Minecraft, soit la 26.3 au 5 novembre 2026, avec Fabric. La version 26.4 est encore en snapshots. Le mod passera dessus quand elle sera stable, si Fabric, GeckoLib et Lunar Client la prennent en charge. Fabric est retenu parce que le mod doit fonctionner sur Lunar Client, dont le chargement de mods documenté repose sur Fabric. La compatibilité de Fabric, GeckoLib et Lunar Client en 26.3 doit être confirmée lors du premier prototype.

### Systèmes réutilisables

- **Définition d'un monde :** règle, mobs, ressources, structures, boss, noyau, Graine et station.
- **Système d'attaques :** annonce, exécution, ouverture, phase et conditions de choix.
- **Système de machines :** bloc, stockage, progression, recette, interface et animation.
- **Multiplicateurs :** statistiques calculées selon le monde et le nombre de joueurs.
- **Attributs d'objets :** classe, niveau et nombre de changements.

### Données à stocker

| Donnée | Emplacement | Contenu |
| --- | --- | --- |
| Monde | Sauvegarde du serveur | Identifiant, parcelle, groupe, bloc parent, variante, état du boss |
| Progression | Groupe ou joueur | Noyaux, mondes terminés, participation aux boss, quêtes, succès |
| Karma | Joueur | Valeur de -100 à +100, paliers atteints |
| Équipement | Objet | Classe, niveau, nombre de changements |
| Histoire | Joueur ou groupe | Pages trouvées, révélations, poupées cachées |

### Bloc-mondes et dimensions

Le mod utilise 10 dimensions fixes, une par monde, plutôt que des dimensions créées à la volée. Chaque groupe reçoit une parcelle de 3 000 × 3 000 blocs par monde, séparée des autres par 10 000 blocs. Une limite infranchissable entoure la parcelle, et les chunks ne sont générés que lorsqu'ils sont visités. Chaque bloc-monde possède un identifiant unique relié à sa parcelle. Un groupe possède au maximum un monde de chaque numéro, soit 10 parcelles. Les variantes changent les mobs, les butins et les règles de la parcelle, mais pas la génération de base. Si le bloc est déplacé, le lien doit être conservé sans créer de duplication.

L'affichage d'un monde complet dans un bloc est coûteux. Le P0 peut utiliser une représentation simple, puis la version P2 ajoutera l'aperçu miniature.

### Maquette du monde 10

La base du joueur apparaît comme une Maquette posée sur l'Établi titanesque du monde 10. À l'ouverture du monde, le mod capture une zone de 64 × 32 × 64 blocs autour du premier bloc-monde. Le client l'affiche comme un seul modèle fixe à l'échelle 1/4, ce qui évite de construire des milliers de blocs. Si le prototype est trop coûteux, la solution de repli est une fresque générée depuis une vue de dessus.

### Groupes

Un joueur seul forme automatiquement un groupe d'une personne. Les mondes, leur progression et leurs permissions appartiennent au groupe.

| Action | Règle |
| --- | --- |
| Créer ou inviter | Depuis le Journal ou avec `/matriochka groupe` |
| Taille | 8 joueurs par défaut, configurable |
| Chef | Il invite, exclut et gère les permissions |
| Départ du chef | Le rôle passe au membre le plus ancien |
| Quitter | Le joueur garde son équipement, ses quêtes et ses succès, mais perd l'accès aux mondes du groupe |
| Rejoindre | Le joueur rejoint les mondes du groupe, mais doit participer au dernier boss pour l'équipement suivant |
| Dissolution | Les mondes sont conservés pendant 30 jours, puis supprimables par un administrateur |

### Pipeline Blockbench

1. Définir la silhouette du boss et ses attaques principales.
2. Créer le modèle et les textures dans Blockbench.
3. Animer le repos, le déplacement, chaque attaque, la mort et les transitions de phase.
4. Exporter les fichiers pour GeckoLib.
5. Relier les moments clés des animations aux dégâts, sons et effets.
6. Tester la lisibilité du combat en jeu.

Blockbench ne gère ni le comportement ni le son. L'IA, les attaques, les phases et les dégâts sont codés dans le mod.

### Stations de craft

Chaque station demande généralement un `BlockEntity`, une interface, un type de recette et une intégration à EMI ou JEI. Un socle commun évite de tout recoder.

### Configuration

- Multiplicateurs de difficulté
- Blocages de crafts et de contenus
- Nombre maximal de groupes et de parcelles actives
- Options de karma et d'âme
- Effets d'écran, comme les tremblements et ralentis

### Mod et modpack

RLCraft est un modpack, c'est-à-dire un ensemble de mods configurés pour fonctionner ensemble. Le cœur de Matriochka doit rester un mod autonome. Une version difficile pourra ensuite être publiée en modpack.

## Feuille de route

Le développement avance par priorités, car le monde 1 doit prouver que le concept est amusant avant toute production massive. Le P0 sert de test, le P1 de socle et le P2 de finition du jeu complet.

&#91;embedded content: feuille de route · 3 priorités et 2 jalons\]

### P0 : prouver le concept

Objectif : fabriquer une Graine, entrer dans le monde 1, battre son boss et récupérer son noyau, en solo et sur serveur.

- [ ] Créer les 10 dimensions, les parcelles, les groupes et le bloc-monde, puis tester Fabric et GeckoLib en 26.3 sur Lunar Client.
- [ ] Ajouter les effets entre les échelles.
- [ ] Créer l'Établi matriciel, la Terre de monde et la Graine du monde 1.
- [ ] Créer la Cuve de spores.
- [ ] Créer deux mobs, un minerai, une armure et les 10 types de structures du monde 1.
- [ ] Créer la Reine des spores avec son modèle, ses textures, huit animations, trois phases et ses sons.
- [ ] Ajouter son noyau et le système de progression.
- [ ] Ajouter les multiplicateurs par monde.
- [ ] Ajouter les valeurs d'âme et le karma de base.
- [ ] Ajouter les classes aléatoires Gardien, Berserker et Prospecteur.
- [ ] Ajouter le Parchemin, le Gardien du bloc, la poupée de vie, le Berceau d'âme, le coffre de mort et les règles du bloc-monde cassé.
- [ ] Ajouter le journal, les indices, les 10 premières quêtes et les 10 succès du monde 1.

### P1 : bâtir les systèmes

Objectif : vérifier que les règles varient vraiment et que le contenu peut être produit plus vite.

- [ ] Créer les mondes 2 à 4, leurs 30 types de structures et une première courbe de difficulté.
- [ ] Créer le système d'attaques réutilisable.
- [ ] Créer le socle commun des machines.
- [ ] Ajouter la Fonderie de cendre et la Table du Geôlier.
- [ ] Ajouter les blocages de progression et un prototype de la Maquette du monde 10.
- [ ] Ajouter l'Autel des âmes et les effets de karma à ±25 et ±50.
- [ ] Ajouter la Table de classe, ses améliorations et la Poupée du hasard.
- [ ] Ajouter la poupée-refuge et les mobs gigognes.
- [ ] Ajouter l'histoire, les PNJ, les quêtes et les succès des mondes 2 à 4, ainsi que les poupées cachées.

### P2 : finir le jeu

Objectif : terminer tout le contenu, puis ajuster la durée et la difficulté.

- [ ] Créer les mondes 5 à 10, leurs 60 types de structures et finaliser l'équilibrage.
- [ ] Créer les stations restantes et l'automatisation.
- [ ] Ajouter le boss final gigogne et les mutations de boss.
- [ ] Ajouter les révélations finales, le monde 0 et les trois fins.
- [ ] Ajouter le palier ±100 et les variantes liées au karma.
- [ ] Ajouter les classes restantes et les limites par monde.
- [ ] Ajouter les armures à couches et les coffres gigognes.
- [ ] Ajouter l'aperçu du monde miniature, la Maquette finale, le Nouveau Cycle, les modes de difficulté et l'accessibilité.
- [ ] Ajouter les cinématiques, la musique dynamique et les effets avancés.
- [ ] Ajouter les quêtes et succès des mondes 5 à 10, puis préparer la version modpack.

La version publique 1.0 contient les 10 mondes. Les mondes 1 à 3 servent d'abord à une alpha privée, puis les mondes 4 à 10 à une bêta fermée. Les coffres gigognes et les armures à couches apparaissent tôt dans l'histoire, mais leur développement peut attendre le P2.

## Risques et équilibrage

Le principal risque est l'ampleur du projet : 10 mondes reviennent à créer 10 mini-mods. Le premier monde doit donc valider le plaisir de jeu avant toute production massive.

| Risque | Conséquence | Réponse |
| --- | --- | --- |
| Portée trop grande | Projet jamais terminé | Terminer le monde 1 avant de produire les suivants |
| Rendu du monde miniature | Mauvaises performances | Reporter l'affichage miniature au P2 et tester tôt un prototype |
| Blocs déplacés avec leur monde | Pertes de données ou duplications | Lier chaque dimension à un identifiant unique et n'autoriser qu'un seul accès |
| Dimensions nombreuses | Surcharge serveur et sauvegardes lourdes | Limiter les mondes actifs et charger seulement ce qui est utilisé |
| Ralentissement artificiel | Frustration | Récompenser fréquemment et rendre chaque blocage logique |
| Statistiques seules | Combats longs et répétitifs | Faire évoluer les schémas et l'environnement avec la vie et les dégâts |
| Farm d'âme | Économie cassée | Limiter les objets renouvelables et contrôler la valeur des crafts |
| Voie de karma dominante | Choix illusoire | Équilibrer les effets et les prix à payer de chaque voie |
| Secrets introuvables | Frustration | Prévoir au moins trois indices par secret |
| Blocages en cas de mort | Abandon | Utiliser les poupées de vie, le Berceau d'âme et le coffre de mort |
| Compatibilité avec d'autres mods | Crafts ou progressions contournés | Tester les mods populaires et prévoir une configuration |
| 100 types de structures | Production très longue et contenu répétitif | Créer d'abord les 10 types du monde 1 et utiliser des modules réutilisables |

### Méthode de test

- Tester chaque boss sans en expliquer le fonctionnement au joueur.
- Noter où le joueur meurt, abandonne ou ne comprend pas.
- Mesurer le temps passé dans chaque monde.
- Vérifier que chaque session apporte au moins un déblocage.
- Tester en solo, puis à 2, 4 et 8 joueurs.

## Décisions à prendre

Les règles P0, P1 et P2 sont validées, et il reste uniquement à traiter les points suivants.

- [x] Valider l'ensemble des règles par défaut de l'onglet Règles détaillées.
- [ ] Valider les mondes 7 à 10, leurs mobs, stations et boss.
- [ ] Trouver les noms définitifs des mondes, boss, mobs et objets.
- [ ] Valider le style visuel du premier monde et de la Reine des spores.
- [ ] Faire une vérification formelle du nom Matriochka avant la publication.
