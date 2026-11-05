"""Matriochka master content table.

Single source of truth for worlds, items, blocks, mobs, bosses, structures,
quests and achievements. `gen.py` turns it into textures, models, lang files,
data packs and the generated Java definitions.

Names are provisional, as in the design document.
"""

# ---------------------------------------------------------------- worlds
# palette: (primary, secondary, accent, dark) as hex
WORLDS = [
    dict(n=1, en="Toxic Jungle", fr="Jungle toxique", rule="toxin",
         pal=("3f6b2a", "6b3f8a", "b7e04a", "1c2a14"), fog="5a7a3a", sky="6f8f4f", water="3f6b4a",
         tier="learning", gen="overworld", light=1.0, ceiling=False),
    dict(n=2, en="Giant Veins", fr="Filons géants", rule="heat",
         pal=("2b2220", "e0661c", "ffb347", "120c0a"), fog="5a2a14", sky="7a3a1a", water="7a4a2a",
         tier="learning", gen="caves", light=0.6, ceiling=False),
    dict(n=3, en="Endless Dungeon", fr="Donjon sans fin", rule="locks",
         pal=("5a5a62", "8a8f9a", "7fd3ff", "1e1e24"), fog="2a2a33", sky="2a2a33", water="3a4a5a",
         tier="learning", gen="ceiling", light=0.15, ceiling=True),
    dict(n=4, en="Storm Archipelago", fr="Archipel des tempêtes", rule="wind",
         pal=("d8e8f8", "3a7ac8", "ffe14a", "2a3a5a"), fog="b8d0f0", sky="7ab0ff", water="4a8ad8",
         tier="mastery", gen="floating", light=1.0, ceiling=False),
    dict(n=5, en="Lightless Deep", fr="Profondeur sans lumière", rule="darkness",
         pal=("15151f", "1f2a4a", "6a8aff", "05050a"), fog="05050a", sky="000000", water="0a0f2a",
         tier="mastery", gen="ceiling", light=0.0, ceiling=True),
    dict(n=6, en="Upside Realm", fr="Royaume inversé", rule="gravity",
         pal=("c84ad8", "4ad8c8", "f0f0f0", "2a0a3a"), fog="d0a0e0", sky="40e0d0", water="a04ad8",
         tier="mastery", gen="amplified", light=1.0, ceiling=False),
    dict(n=7, en="Pressure Ocean", fr="Océan sous pression", rule="pressure",
         pal=("0a3a5a", "1ab0b0", "9af0ff", "021018"), fog="0a2a4a", sky="1a5a8a", water="0a3a6a",
         tier="expertise", gen="ocean", light=0.8, ceiling=False),
    dict(n=8, en="Hastened Seasons", fr="Saisons accélérées", rule="time",
         pal=("c8a040", "d86a2a", "f0f0ff", "3a2a14"), fog="d8c890", sky="90b8e8", water="5a8ab8",
         tier="expertise", gen="overworld", light=1.0, ceiling=False),
    dict(n=9, en="Restless Ground", fr="Terre agitée", rule="ground",
         pal=("6a3a2a", "a84a3a", "e8a070", "2a140e"), fog="7a4a3a", sky="a86a5a", water="6a4a3a",
         tier="expertise", gen="amplified", light=0.9, ceiling=False),
    dict(n=10, en="The Giant Workshop", fr="L'Atelier géant", rule="synthesis",
         pal=("b0402a", "e8c070", "3a6ab8", "2a1408"), fog="c8a878", sky="e8d0a0", water="4a7ab8",
         tier="final", gen="giant", light=1.0, ceiling=False),
]

RULES = {
    "toxin":     dict(en="Toxin", fr="Toxine"),
    "heat":      dict(en="Heat", fr="Chaleur"),
    "locks":     dict(en="Locks", fr="Verrous"),
    "wind":      dict(en="Wind", fr="Vent"),
    "darkness":  dict(en="Noise", fr="Bruit"),
    "gravity":   dict(en="Gravity", fr="Gravité"),
    "pressure":  dict(en="Oxygen", fr="Oxygène"),
    "time":      dict(en="Season", fr="Saison"),
    "ground":    dict(en="Tremor", fr="Secousse"),
    "synthesis": dict(en="Synthesis", fr="Synthèse"),
}

RARITY_SOUL = {"none": 0, "common": 1, "rare": 10, "epic": 30, "legendary": 100}

# ---------------------------------------------------------------- equipment table
# world: (weapon dmg, armor total, toughness, bonus hp)
GEAR = {1: (7, 16, 1, 0), 2: (9, 17, 2, 0), 3: (11, 18, 3, 2), 4: (13, 19, 4, 4), 5: (16, 20, 6, 6),
        6: (19, 22, 8, 8), 7: (23, 24, 10, 12), 8: (28, 26, 12, 16), 9: (33, 28, 14, 20), 10: (40, 30, 16, 24)}

# ---------------------------------------------------------------- items
# kind: resource | gem | ingot | dust | consumable | tool | weapon | armor | core | seed | guide | doll
#       | key | food | mask | boots | thread | page
# shape is used by the texture painter.
ITEMS = []


def item(id, en, fr, world, kind, rarity, shape, effect_en="", effect_fr="", **kw):
    ITEMS.append(dict(id=id, en=en, fr=fr, world=world, kind=kind, rarity=rarity, shape=shape,
                      effect_en=effect_en, effect_fr=effect_fr, **kw))


# Surface / common
item("artisan_scroll", "Artisan's Scroll", "Parchemin de l'artisan", 0, "guide", "none", "scroll",
     "Explains the mod. Becomes the Journal.", "Explique le mod, puis devient le Journal.")
item("artisan_journal", "Artisan's Journal", "Journal de l'artisan", 0, "guide", "none", "book",
     "Story, objectives, quests and karma.", "Histoire, objectifs, quêtes et karma.")
item("guardian_core", "Guardian Core", "Noyau du Gardien", 0, "core", "legendary", "core",
     "Opens the World 1 Seed.", "Ouvre la Graine du monde 1.")
item("life_doll", "Life Doll", "Poupée de vie", 0, "doll", "legendary", "doll",
     "Breaks a layer instead of letting you die.", "Brise une couche au lieu de te laisser mourir.")
item("return_thread", "Return Thread", "Fil de retour", 0, "consumable", "common", "thread",
     "Brings you back to the world block.", "Te ramène au bloc-monde.")
item("chance_doll", "Chance Doll", "Poupée du hasard", 0, "consumable", "rare", "doll_small",
     "Rerolls the class of an item.", "Change aléatoirement la classe d'un objet.")
item("cracked_doll", "Cracked Doll", "Poupée fêlée", 0, "doll", "none", "doll_cracked",
     "Holds the access to a broken world.", "Conserve l'accès à un monde cassé.")
item("journal_page", "Journal Page", "Page du Journal", 0, "page", "none", "page",
     "A lost page of the Artisan's Journal.", "Une page perdue du Journal de l'artisan.")
item("wool_thread", "Wool Thread", "Fil de laine", 0, "resource", "common", "thread",
     "Used for cradles and threads.", "Sert aux berceaux et aux fils.")

# World 1
item("spores", "Spores", "Spores", 1, "resource", "common", "dust", "Base of antidotes.", "Base des antidotes.")
item("roots", "Roots", "Racines", 1, "resource", "common", "stick", "Living wood.", "Bois vivant.")
item("sporite", "Sporite", "Sporite", 1, "gem", "rare", "gem", "World 1 ore.", "Minerai du monde 1.")
item("chitin", "Chitin", "Chitine", 1, "resource", "rare", "plate", "Armor of the world.", "Armure du monde.")
item("antidote", "Antidote", "Antidote", 1, "consumable", "common", "potion", "Reduces toxin by 50.", "Réduit la toxine de 50.")
item("filter_mask", "Filter Mask", "Masque filtrant", 1, "mask", "rare", "mask", "Halves toxin gain.", "Divise par 2 la montée de toxine.")
item("sporite_sword", "Sporite Sword", "Épée de sporite", 1, "weapon", "rare", "sword", "", "")
item("chitin", "", "", 1, "armorset", "rare", "armor", set_en="Chitin", set_fr="de chitine")
# World 2
item("blazing_rock", "Blazing Rock", "Roche ardente", 2, "resource", "common", "rock", "Powerful fuel.", "Combustible puissant.")
item("giant_ore", "Giant Ore", "Minerai géant", 2, "resource", "rare", "chunk", "A whole vein in one block.", "Un filon entier en un bloc.")
item("ash_ingot", "Ash Ingot", "Lingot de cendre", 2, "ingot", "rare", "ingot", "Base of World 2 gear.", "Base de l'équipement du monde 2.")
item("cooling_water", "Cooling Water", "Eau de refroidissement", 2, "consumable", "common", "potion", "Reduces heat by 50.", "Réduit la chaleur de 50.")
item("drill", "Drill", "Foreuse", 2, "drill", "epic", "drill", "Mines 3x3, burns Blazing Rock.", "Mine en 3x3 et brûle de la Roche ardente.")
item("ash_hammer", "Ash Hammer", "Marteau de cendre", 2, "weapon", "rare", "hammer")
item("thermal", "", "", 2, "armorset", "rare", "armor", set_en="Thermal", set_fr="thermique", effect_en="Halves heat gain.", effect_fr="Divise par 2 la chaleur.")
# World 3
item("dungeon_key", "Dungeon Key", "Clé de donjon", 3, "key", "rare", "key", "Opens a sealed door once.", "Ouvre une porte scellée, une fois.")
item("sealed_fragment", "Sealed Fragment", "Fragment scellé", 3, "resource", "rare", "shard", "Traps and gear.", "Pièges et équipement.")
item("labyrinth_map", "Labyrinth Map", "Carte du labyrinthe", 3, "tool", "common", "map", "Reveals nearby structures.", "Révèle les structures proches.")
item("lockpick_kit", "Lockpick Kit", "Kit de crochetage", 3, "tool", "common", "pick", "Opens an ordinary lock.", "Ouvre une serrure ordinaire.")
item("portable_trap", "Portable Trap", "Piège portatif", 3, "consumable", "common", "trap", "Immobilizes a mob.", "Immobilise un mob.")
item("jailer_blade", "Jailer's Blade", "Lame du Geôlier", 3, "weapon", "rare", "sword")
item("jailer", "", "", 3, "armorset", "rare", "armor", set_en="Jailer", set_fr="de Geôlier")
# World 4
item("ray_membrane", "Ray Membrane", "Membrane de raie", 4, "resource", "common", "membrane", "Glider cloth.", "Toile du planeur.")
item("storm_essence", "Storm Essence", "Essence de tempête", 4, "resource", "rare", "orb", "Energy of the Lightning Forge.", "Énergie de la Forge à foudre.")
item("celestial_crystal", "Celestial Crystal", "Cristal céleste", 4, "gem", "rare", "crystal", "Gear and World 5 Seed.", "Équipement et Graine du monde 5.")
item("glider", "Glider", "Planeur", 4, "glider", "epic", "glider", "Glide between islands.", "Plane entre les îles.")
item("grappling_hook", "Grappling Hook", "Grappin", 4, "hook", "rare", "hook", "Pulls you toward a surface.", "Te tire vers une surface.")
item("lightning_lance", "Lightning Lance", "Lance de foudre", 4, "weapon", "rare", "spear")
item("celestial", "", "", 4, "armorset", "rare", "armor", set_en="Celestial", set_fr="céleste")
# World 5
item("shadow_shard", "Shadow Shard", "Éclat d'ombre", 5, "resource", "rare", "shard", "Base of World 5 gear.", "Base de l'équipement du monde 5.")
item("diamond_fragment", "Diamond Fragment", "Fragment de diamant", 5, "gem", "epic", "fragment", "4 fragments make 1 diamond.", "4 fragments donnent 1 diamant.")
item("solar_lantern", "Solar Lantern", "Lanterne solaire", 5, "lantern", "epic", "lantern", "20 minutes of light.", "20 minutes de lumière.")
item("sonar", "Sonar", "Sonar", 5, "sonar", "rare", "sonar", "Reveals nearby creatures.", "Révèle les créatures proches.")
item("silence_balm", "Silence Balm", "Baume de silence", 5, "consumable", "common", "jar", "Clears your noise.", "Efface ton bruit.")
item("shadow_blade", "Shadow Blade", "Lame d'ombre", 5, "weapon", "epic", "sword")
item("nocturnal", "", "", 5, "armorset", "epic", "armor", set_en="Nocturnal", set_fr="nocturne")
# World 6
item("unstable_alloy", "Unstable Alloy", "Alliage instable", 6, "ingot", "rare", "ingot", "Base of World 6 gear.", "Base de l'équipement du monde 6.")
item("inverted_crystal", "Inverted Crystal", "Cristal inversé", 6, "gem", "epic", "crystal", "Inverter and World 7 Seed.", "Inverseur et Graine du monde 7.")
item("gravity_boots", "Gravity Boots", "Bottes de gravité", 6, "boots", "epic", "boots", "Ignore gravity flips.", "Ignorent les inversions de gravité.")
item("stabilizer", "Stabilizer", "Stabilisateur", 6, "consumable", "common", "orb_small", "Cancels an inversion.", "Annule une inversion.")
item("mirror_blade", "Mirror Blade", "Lame miroir", 6, "weapon", "epic", "sword")
item("mirror", "", "", 6, "armorset", "epic", "armor", set_en="Mirror", set_fr="miroir")
# World 7: everything happens under water. The four ores each give one tier of snorkel helmet (see SNORKELS).
item("abyssal_salt", "Abyssal Salt", "Sel des profondeurs", 7, "dust", "rare", "dust", "Salt Snorkel Helmet and World 8 Seed.", "Casque-tuba de sel et Graine du monde 8.")
item("nacre", "Nacre", "Nacre", 7, "gem", "rare", "shard", "Mined from reef veins. Nacre Snorkel Helmet.", "Extraite des filons des récifs. Casque-tuba de nacre.",
     pal=("e8d0e0", "a8e0e0", "f4e4ee", "6a5a70"))
item("abyssal_cobalt", "Abyssal Cobalt", "Cobalt abyssal", 7, "ingot", "rare", "ingot", "Cobalt Snorkel Helmet and the diving suit.", "Casque-tuba de cobalt et scaphandre.",
     pal=("1a3a8a", "3a7ae0", "4a7ae8", "0a1438"))
item("pressure_pearl", "Pressure Pearl", "Perle de pression", 7, "gem", "epic", "pearl", "Pearl Snorkel Helmet and World 8 Seed.", "Casque-tuba de perle et Graine du monde 8.")
item("oxygen_capsule", "Oxygen Capsule", "Capsule d'oxygène", 7, "consumable", "common", "capsule", "Refills half of a snorkel helmet's tank, or your breath.", "Remplit à moitié la réserve d'un casque-tuba, ou ton souffle.")
item("thruster", "Thruster", "Propulseur", 7, "thruster", "epic", "thruster", "Speeds you up underwater.", "Accélère sous l'eau.")
item("trench_trident", "Trench Trident", "Trident des fosses", 7, "weapon", "epic", "trident")
item("diving", "", "", 7, "armorset", "epic", "armor", set_en="Diving", set_fr="de plongée", pieces=("chestplate", "leggings", "boots"),
     effect_en="Resists pressure. Wear it with a snorkel helmet.", effect_fr="Résiste à la pression. Se porte avec un casque-tuba.")
# World 8
item("temporal_sand", "Temporal Sand", "Sable temporel", 8, "dust", "rare", "dust", "Base of World 8 gear.", "Base de l'équipement du monde 8.")
item("season_fragment", "Season Fragment", "Fragment de saison", 8, "gem", "epic", "leaf", "World 9 Seed.", "Graine du monde 9.")
item("hourglass", "Hourglass", "Sablier", 8, "hourglass", "epic", "hourglass", "Slows the world cycle.", "Ralentit le cycle du monde.")
item("season_preserve", "Season Preserve", "Conserve de saison", 8, "consumable", "common", "jar", "Protects from the current season.", "Protège de la saison en cours.")
item("season_scythe", "Scythe of Seasons", "Faux des saisons", 8, "weapon", "epic", "scythe")
item("seasonal", "", "", 8, "armorset", "epic", "armor", set_en="Seasonal", set_fr="saisonnière")
# World 9
item("terrain_fragment", "Terrain Fragment", "Fragment de terrain", 9, "resource", "rare", "rock", "Base of World 9 gear.", "Base de l'équipement du monde 9.")
item("terrain_heart", "Terrain Heart", "Cœur de terrain", 9, "resource", "legendary", "heart", "World 10 Seed.", "Graine du monde 10.")
item("anchor", "Anchor", "Ancre", 9, "anchor", "rare", "anchor", "Calms the ground (radius 4).", "Calme le sol (rayon 4).")
item("grip_boots", "Grip Boots", "Bottes d'accroche", 9, "boots", "epic", "boots", "No falls from moving ground.", "Plus de chutes dues au sol.")
item("seismic_mace", "Seismic Mace", "Masse sismique", 9, "weapon", "legendary", "mace")
item("living_rock", "", "", 9, "armorset", "legendary", "armor", set_en="Living Rock", set_fr="de roche vivante")
item("last_doll_key", "Key of the Last Doll", "Clé de la dernière poupée", 9, "key", "none", "key_gold", "World 10 Seed.", "Graine du monde 10.")
# World 10
item("artisan_thread", "Artisan's Thread", "Fil d'Artisan", 10, "thread", "rare", "thread", "Base of the final gear.", "Base de l'équipement final.")
item("artisan_shard", "Artisan's Shard", "Éclat d'Artisan", 10, "gem", "legendary", "shard", "Upgrades the final gear.", "Améliore l'équipement final.")
item("artisan_blade", "Artisan's Blade", "Lame de l'Artisan", 10, "weapon", "legendary", "sword")
item("artisan", "", "", 10, "armorset", "legendary", "armor", set_en="Artisan", set_fr="de l'Artisan")

# Cores
CORES = [
    ("queen_core", "Queen Core", "Noyau de la Reine", 1),
    ("titan_core", "Titan Core", "Noyau du Titan", 2),
    ("jailer_core", "Jailer Core", "Noyau du Geôlier", 3),
    ("storm_king_core", "Storm King Core", "Noyau du Roi", 4),
    ("light_eater_core", "Light Eater Core", "Noyau du Mangeur", 5),
    ("double_core", "Double Core", "Noyau du Double", 6),
    ("leviathan_core", "Leviathan Core", "Noyau du Léviathan", 7),
    ("seasons_core", "Seasons Core", "Noyau du Maître", 8),
    ("terrain_core", "Terrain Core", "Noyau du Terrain", 9),
    ("unfinished_core", "Unfinished Core", "Noyau de l'Inachevée", 10),
]
for cid, en, fr, w in CORES:
    nxt = w + 1
    item(cid, en, fr, w, "core", "legendary", "core",
         f"Opens the World {nxt} Seed." if nxt <= 10 else "The heart of the creature.",
         f"Ouvre la Graine du monde {nxt}." if nxt <= 10 else "Le cœur de la créature.")

# Seeds
for w in range(1, 11):
    item(f"seed_{w}", f"World {w} Seed", f"Graine du monde {w}", w, "seed", "epic", "seed",
         f"Plant on tilled World Soil {w - 1} to grow World {w}.",
         f"Se plante sur la Terre de monde {w - 1} bêchée pour faire éclore le monde {w}.")

# Hidden dolls
for w in range(1, 11):
    item(f"hidden_doll_{w}", f"Hidden Doll {w}", f"Poupée cachée {w}", w, "secret", "none", "doll_small",
         "Nest the ten dolls in order...", "Emboîte les dix poupées dans l'ordre...")

# Boss offerings: held at the arena altar, they start the ritual that wakes an altar boss (one per fight)
OFFERINGS = [
    ("sealed_shackle", "Sealed Shackle", "Entrave scellée", 3, "shackle", "grand_jailer",
     "Held at the arena altar, it wakes the Grand Jailer.", "Tenue à l'autel d'arène, elle réveille le Grand Geôlier."),
    ("storm_censer", "Storm Censer", "Encensoir d'orage", 4, "censer", "storm_king",
     "Held at the arena altar, it wakes the Storm King.", "Tenu à l'autel d'arène, il réveille le Roi des tempêtes."),
    ("wreath_of_seasons", "Wreath of Seasons", "Couronne des saisons", 8, "wreath", "seasons_master",
     "Held at the arena altar, it wakes the Master of Seasons.", "Tenue à l'autel d'arène, elle réveille le Maître des saisons."),
    ("unfinished_effigy", "Unfinished Effigy", "Effigie inachevée", 10, "effigy", "the_unfinished",
     "Held at the arena altar, it wakes the Unfinished.", "Tenue à l'autel d'arène, elle réveille l'Inachevée."),
]
for oid, en, fr, w, shape, _boss, een, efr in OFFERINGS:
    item(oid, en, fr, w, "offering", "epic", shape, een, efr)

# Foods (one dish per world)
FOODS = [
    ("root_broth", "Root Broth", "Bouillie de racines", 1, "Slows toxin for 5 minutes.", "Toxine ralentie pendant 5 minutes."),
    ("ice_bread", "Ice Bread", "Pain de glace", 2, "Slows heat for 5 minutes.", "Chaleur ralentie pendant 5 minutes."),
    ("cell_ration", "Cell Ration", "Ration de cellule", 3, "Long-lasting saturation.", "Satiété durable."),
    ("cloud_fruit", "Cloud Fruit", "Fruit de nuage", 4, "Slow falling for 3 minutes.", "Chutes réduites pendant 3 minutes."),
    ("mute_mushroom", "Mute Mushroom", "Champignon muet", 5, "Noise reduced for 5 minutes.", "Bruit réduit pendant 5 minutes."),
    ("flipped_apple", "Flipped Apple", "Pomme retournée", 6, "Stability for 30 seconds.", "Stabilité pendant 30 secondes."),
    ("apnea_kelp", "Apnea Kelp", "Algue d'apnée", 7, "Oxygen lasts twice as long for 5 minutes.", "L'oxygène dure deux fois plus longtemps pendant 5 minutes."),
    ("season_jam", "Season Jam", "Conserve de saison sucrée", 8, "Protection from the season for 3 minutes.", "Protège de la saison pendant 3 minutes."),
    ("anchor_bread", "Anchor Bread", "Pain d'ancrage", 9, "Steady footing for 5 minutes.", "Pied ferme pendant 5 minutes."),
    ("workshop_feast", "Workshop Feast", "Festin de l'atelier", 10, "Every dish's effect for 2 minutes.", "Les effets de tous les plats pendant 2 minutes."),
]
for fid, en, fr, w, een, efr in FOODS:
    item(fid, en, fr, w, "food", "common", "food", een, efr)

# Snorkel helmets (World 7): head armor that works as a mask and a snorkel. You breathe from its tank while it holds
# oxygen; it drains under water and refills in air pockets, bubble columns, over air vents, at the Abyssal Press or
# with an Oxygen Capsule. They break easily: every hit wears them a little more, and the depths grind them down.
# (id, en, fr, ore item, tier, tank in seconds, durability multiplier (x11), armor, toughness, extra wear per damage
#  point, depth bonus in blocks, rarity, palette)
SNORKELS = [
    ("salt_snorkel", "Salt Snorkel Helmet", "Casque-tuba de sel", "abyssal_salt", 1, 180, 4, 2, 0.0, 0.5, 0, "rare",
     ("d8dcd4", "9ab0b4", "eef2ea", "4a5458")),
    ("nacre_snorkel", "Nacre Snorkel Helmet", "Casque-tuba de nacre", "nacre", 2, 300, 6, 3, 1.0, 0.35, 6, "rare",
     ("e8d0e0", "a8e0e0", "f4e4ee", "6a5a70")),
    ("cobalt_snorkel", "Cobalt Snorkel Helmet", "Casque-tuba de cobalt", "abyssal_cobalt", 3, 480, 10, 3, 2.0, 0.25, 12, "epic",
     ("1a3a8a", "3a7ae0", "2a5ac8", "0a1438")),
    ("pearl_snorkel", "Pearl Snorkel Helmet", "Casque-tuba de perle", "pressure_pearl", 4, 720, 14, 4, 3.0, 0.15, 18, "epic",
     ("9af0ff", "1ab0b0", "c8f8ff", "0a3a5a")),
]
for sid, en, fr, ore, tier, tank, dur, arm, tough, wear, depth, rar, _pal in SNORKELS:
    item(sid, en, fr, 7, "snorkel", rar, "snorkel",
         "Breathe under water while its tank holds air (%d min). Fragile: hits wear it fast." % (tank // 60),
         "Permet de respirer sous l'eau tant que sa réserve tient (%d min). Fragile : les coups l'usent vite." % (tank // 60))

# ---------------------------------------------------------------- blocks
# style drives the procedural texture: soil, stone, ore, moss, brick, crystal, wood, glass, lacquer,
# station, special.
BLOCKS = []


def block(id, en, fr, world, kind, style, **kw):
    BLOCKS.append(dict(id=id, en=en, fr=fr, world=world, kind=kind, style=style, **kw))


for w in range(0, 10):
    block(f"world_soil_{w}", f"World Soil {w}", f"Terre de monde {w}", w, "soil", "soil",
          note_en=f"Till it to plant the World {w + 1} Seed.", note_fr=f"Se bêche pour planter la Graine du monde {w + 1}.")
block("world_block", "World Block", "Bloc-monde", 0, "world_block", "lacquer")
block("planted_seed", "Planted Seed", "Graine plantée", 0, "planted_seed", "special")
block("threshold", "Threshold", "Seuil", 0, "threshold", "lacquer")
block("soul_cradle", "Soul Cradle", "Berceau d'âme", 0, "cradle", "wood")
block("death_chest", "Death Chest", "Coffre de mort", 0, "death_chest", "wood")
block("nesting_chest", "Nesting Chest", "Coffre gigogne", 2, "nesting_chest", "wood")
block("sanctuary_altar", "Guardian's Altar", "Autel du Gardien", 0, "boss_altar", "stone_rune", boss="block_guardian")
block("arena_altar", "Arena Altar", "Autel d'arène", 0, "boss_altar", "stone_rune")
block("lair_heart", "Lair Heart", "Cœur d'antre", 0, "lair_heart", "lair_heart",
      note_en="Wakes the boss of its lair when someone comes close.", note_fr="Réveille le boss de son antre quand on s'approche.")
block("sealed_door", "Sealed Door", "Porte scellée", 3, "sealed_door", "brick")
block("painted_wood", "Painted Wood", "Bois peint", 0, "deco", "wood")
block("lacquer_block", "Lacquer Block", "Bloc laqué", 0, "deco", "lacquer")

# stations
STATIONS = [
    ("matrix_workbench", "Matrix Workbench", "Établi matriciel", 0, "Crafts Seeds; recipes unlock with cores.", "Fabrique les Graines ; recettes débloquées par les noyaux."),
    ("class_table", "Class Table", "Table de classe", 0, "Upgrades an item's class.", "Améliore la classe d'un objet."),
    ("soul_altar", "Soul Altar", "Autel des âmes", 0, "Purify or devour an item.", "Purifie ou dévore un objet."),
    ("spore_vat", "Spore Vat", "Cuve de spores", 1, "Result depends on fermentation time.", "Le résultat dépend du temps de fermentation."),
    ("ash_foundry", "Ash Foundry", "Fonderie de cendre", 2, "Keep the temperature in the green.", "Garde la température dans le vert."),
    ("jailer_table", "Jailer's Table", "Table du Geôlier", 3, "Reproduce the lock pattern.", "Reproduis le motif de la serrure."),
    ("lightning_forge", "Lightning Forge", "Forge à foudre", 4, "Needs a lightning strike or storm essence.", "Demande un éclair ou de l'essence de tempête."),
    ("dark_altar", "Dark Altar", "Autel obscur", 5, "Works only in complete darkness.", "Fonctionne seulement dans le noir complet."),
    ("inverter", "Inverter", "Inverseur", 6, "Every gain comes with a flaw.", "Chaque gain s'accompagne d'un défaut."),
    ("abyssal_press", "Abyssal Press", "Presse abyssale", 7, "Must be deep underwater. Also refills a snorkel helmet.", "Doit être sous l'eau profonde. Remplit aussi un casque-tuba."),
    ("time_workshop", "Time Workshop", "Atelier du temps", 8, "Accepts recipes at dawn and dusk.", "Accepte les recettes à l'aube et au crépuscule."),
    ("terrain_anchor", "Terrain Anchor", "Ancre de terrain", 9, "Stabilizes the ground (radius 16).", "Stabilise le sol (rayon 16)."),
    ("final_loom", "Final Loom", "Métier final", 10, "Weaves materials from every world.", "Tisse les matériaux de tous les mondes."),
]
for sid, en, fr, w, nen, nfr in STATIONS:
    block(sid, en, fr, w, "station", "station", note_en=nen, note_fr=nfr)

# terrain blocks per world: (id, en, fr, style, light)
TERRAIN = {
    1: [("spore_moss", "Spore Moss", "Mousse à spores", "moss"), ("rootstone", "Rootstone", "Pierre-racine", "stone"),
        ("spore_bloom", "Spore Bloom", "Floraison de spores", "glow"), ("sporite_ore", "Sporite Ore", "Minerai de sporite", "ore")],
    2: [("ashrock", "Ashrock", "Roche de cendre", "stone"), ("ember_stone", "Ember Stone", "Pierre de braise", "glow"),
        ("giant_ore_block", "Giant Vein", "Filon géant", "ore_big"), ("blazing_rock_ore", "Blazing Rock Ore", "Minerai de roche ardente", "ore")],
    3: [("dungeon_brick", "Dungeon Brick", "Brique de donjon", "brick"), ("sealed_brick", "Sealed Brick", "Brique scellée", "brick_unbreakable"),
        ("cold_lamp", "Cold Lamp", "Lampe froide", "glow"), ("sealed_fragment_ore", "Sealed Ore", "Minerai scellé", "ore")],
    4: [("skygrass", "Skygrass", "Herbe céleste", "moss"), ("cloudstone", "Cloudstone", "Pierre de nuage", "stone"),
        ("storm_glass", "Storm Glass", "Verre d'orage", "glow"), ("celestial_crystal_ore", "Celestial Crystal Ore", "Minerai de cristal céleste", "ore")],
    5: [("umbral_stone", "Umbral Stone", "Pierre ombrale", "stone"), ("umbral_moss", "Umbral Moss", "Mousse ombrale", "moss"),
        ("faint_glow", "Faint Glow", "Lueur faible", "glow"), ("diamond_fragment_ore", "Diamond Fragment Ore", "Minerai de fragments de diamant", "ore")],
    6: [("inverted_stone", "Inverted Stone", "Pierre inversée", "stone"), ("mirror_glass", "Mirror Glass", "Verre miroir", "glass"),
        ("prism_moss", "Prism Moss", "Mousse prismatique", "moss"), ("unstable_alloy_ore", "Unstable Alloy Ore", "Minerai d'alliage instable", "ore")],
    7: [("abyssal_sand", "Abyssal Sand", "Sable abyssal", "sand"), ("trench_rock", "Trench Rock", "Roche des fosses", "stone"),
        ("pressure_coral", "Pressure Coral", "Corail de pression", "glow"), ("abyssal_salt_ore", "Abyssal Salt Ore", "Minerai de sel", "ore"),
        ("nacre_ore", "Nacre Vein", "Filon de nacre", "ore"), ("abyssal_cobalt_ore", "Abyssal Cobalt Ore", "Minerai de cobalt abyssal", "ore"),
        ("pearl_bed", "Pearl Bed", "Banc de perles", "ore")],
    8: [("chrono_grass", "Chrono Grass", "Herbe chrono", "moss"), ("hourstone", "Hourstone", "Pierre des heures", "stone"),
        ("temporal_sand_block", "Temporal Sand Block", "Bloc de sable temporel", "sand"), ("season_ore", "Season Ore", "Minerai de saison", "ore")],
    9: [("living_rock", "Living Rock", "Roche vivante", "stone"), ("flesh_stone", "Flesh Stone", "Pierre de chair", "moss"),
        ("pulse_vein", "Pulse Vein", "Veine battante", "glow"), ("terrain_ore", "Terrain Ore", "Minerai de terrain", "ore")],
    10: [("giant_plank", "Giant Plank", "Planche géante", "wood"), ("workshop_felt", "Workshop Felt", "Feutre d'atelier", "moss"),
         ("lacquer_glow", "Lacquer Glow", "Laque lumineuse", "glow"), ("artisan_thread_ore", "Thread Spool", "Bobine de fil", "ore")],
}
ORE_DROPS = {"sporite_ore": "sporite", "blazing_rock_ore": "blazing_rock", "giant_ore_block": "giant_ore",
             "sealed_fragment_ore": "sealed_fragment", "celestial_crystal_ore": "celestial_crystal",
             "diamond_fragment_ore": "diamond_fragment", "unstable_alloy_ore": "unstable_alloy",
             "abyssal_salt_ore": "abyssal_salt", "season_ore": "season_fragment", "terrain_ore": "terrain_fragment",
             "artisan_thread_ore": "artisan_thread", "nacre_ore": "nacre", "abyssal_cobalt_ore": "abyssal_cobalt",
             "pearl_bed": "pressure_pearl"}
# Ore placement when it differs from the default (size 9, 14 per chunk, the whole height, in the world's stone):
# (vein size, veins per chunk, lowest y, highest y, extra blocks it can replace)
ORE_PAL = {  # ores painted in their own colors rather than the world's accent: (stone, -, flecks, -)
    "nacre_ore": ("0a3a5a", "a8e0e0", "f4dcee", "021018"),
    "abyssal_cobalt_ore": ("0a3a5a", "3a7ae0", "3a64e8", "021018"),
    "pearl_bed": ("0a3a5a", "1ab0b0", "fbfdff", "021018"),
}
ORE_GEN = {
    "abyssal_salt_ore": (9, 14, -50, 200, ()),
    "nacre_ore": (7, 10, 110, 220, ()),
    "abyssal_cobalt_ore": (8, 9, -20, 110, ()),
    "pearl_bed": (4, 5, -50, 60, ("abyssal_sand",)),
}
for w, lst in TERRAIN.items():
    for (bid, en, fr, style) in lst:
        block(bid, en, fr, w, "terrain", style)
# World 7: a crack in the sea floor breathing out air; it refills snorkel helmets swimming over it
block("air_vent", "Air Vent", "Évent d'air", 7, "vent", "vent",
      note_en="Breathes out air. Swim over it to refill a snorkel helmet.", note_fr="Souffle de l'air. Nage au-dessus pour remplir un casque-tuba.")

# ---------------------------------------------------------------- mobs
# behavior keys are implemented in Java (MobBehavior). body = model plan for gen.
MOBS = []


def mob(id, en, fr, world, hp, dmg, behavior, body, size, drop, rare_drop=None, elite=False, nesting=False,
        flying=False, aquatic=False, desc_en="", desc_fr=""):
    MOBS.append(dict(id=id, en=en, fr=fr, world=world, hp=hp, dmg=dmg, behavior=behavior, body=body, size=size,
                     drop=drop, rare_drop=rare_drop, elite=elite, nesting=nesting, flying=flying, aquatic=aquatic,
                     desc_en=desc_en, desc_fr=desc_fr))


mob("sporeling", "Sporeling", "Sporelin", 1, 16, 3, "swarm_toxin", "imp", 0.6, "spores",
    desc_en="Attacks in groups and adds toxin.", desc_fr="Attaque en groupe et ajoute de la toxine.")
mob("root_creeper", "Root Creeper", "Rampeur de racines", 1, 24, 4, "ambush_root", "crawler", 0.9, "roots",
    desc_en="Waits underground, then roots you.", desc_fr="Attend sous terre, puis immobilise le joueur.")
mob("snare_flower", "Snare Flower", "Fleur-piège", 1, 30, 5, "puller", "plant", 1.1, "spores", "roots",
    desc_en="Immobile, pulls you toward it.", desc_fr="Immobile, tire le joueur vers elle.")
mob("spore_bearer", "Spore Bearer", "Porte-spores", 1, 20, 3, "flee_cloud", "blob", 0.9, "spores",
    desc_en="Flees and leaves toxic clouds.", desc_fr="Fuit et laisse des nuages toxiques.")
mob("chitin_guard", "Chitin Guard", "Gardien de chitine", 1, 40, 6, "shielded", "beetle", 1.3, "chitin", elite=True,
    desc_en="Elite. A shield you must break from behind.", desc_fr="Élite, garde un bouclier à briser de dos.")

mob("ash_miner", "Ash Miner", "Mineur de cendre", 2, 30, 6, "digger", "biped_short", 0.9, "ash_ingot",
    desc_en="Digs to reach you.", desc_fr="Creuse pour rejoindre le joueur.")
mob("living_vein", "Living Vein", "Filon vivant", 2, 49, 6, "melee", "golem", 1.1, "giant_ore", nesting=True,
    desc_en="Nesting: splits into shards.", desc_fr="Gigogne, se fend en éclats.")
mob("rock_salamander", "Rock Salamander", "Salamandre de roche", 2, 27, 7.2, "lava_heat", "lizard", 1.0, "blazing_rock",
    desc_en="Crosses lava and raises your heat.", desc_fr="Traverse la lave et augmente la chaleur.")
mob("dead_smith", "Dead Smith", "Forgeron éteint", 2, 40, 7.2, "charger", "biped", 1.0, "ash_ingot",
    desc_en="Heats its hammer before striking.", desc_fr="Chauffe son marteau avant de frapper.")
mob("slag_golem", "Slag Golem", "Golem de scories", 2, 61, 8.4, "hardening", "golem", 1.6, "blazing_rock", elite=True,
    desc_en="Elite. Hardens when it cools down.", desc_fr="Élite, durcit quand il refroidit.")

mob("jailer_mob", "Jailer", "Geôlier", 3, 51, 7.2, "caller", "robed", 1.0, "dungeon_key",
    desc_en="Calls allies and closes doors.", desc_fr="Appelle ses alliés et ferme les portes.")
mob("sentinel", "Sentinel", "Sentinelle", 3, 55, 7.2, "chain_ranged", "floating_head", 1.0, "sealed_fragment",
    desc_en="Throws chains from above.", desc_fr="Tire des chaînes depuis les hauteurs.")
mob("living_lock", "Living Lock", "Serrure vivante", 3, 44, 5.8, "mimic", "block", 1.0, "dungeon_key",
    desc_en="Pretends to be a locked door.", desc_fr="Imite une porte verrouillée.")
mob("dungeon_rat", "Dungeon Rat", "Rat de cachot", 3, 18, 4.3, "swarm", "rat", 0.5, "sealed_fragment",
    desc_en="Slips under bars, attacks in swarms.", desc_fr="Passe sous les grilles, attaque en nuée.")
mob("executioner", "Executioner", "Bourreau", 3, 82, 11.5, "charger_cage", "brute", 1.4, "sealed_fragment", elite=True,
    desc_en="Elite. Charges and cages you.", desc_fr="Élite, charge et enferme le joueur.")

mob("wind_ray", "Wind Ray", "Raie du vent", 4, 44, 8.6, "flyer_push", "ray", 1.4, "ray_membrane", flying=True,
    desc_en="Glides and pushes you off the islands.", desc_fr="Plane et repousse le joueur hors des îles.")
mob("storm_bird", "Storm Bird", "Oiseau-tempête", 4, 39, 8.6, "diver", "bird", 0.9, "storm_essence", flying=True,
    desc_en="Dives during storms.", desc_fr="Plonge pendant les orages.")
mob("island_warden", "Island Warden", "Gardien d'île", 4, 98, 10.4, "area_slam", "golem", 1.5, "celestial_crystal",
    desc_en="Guards a crystal and slams the area.", desc_fr="Protège un cristal et frappe en zone.")
mob("cloud_mine", "Cloud Mine", "Nuage-mine", 4, 34, 12.1, "exploder", "orb", 1.0, "storm_essence", flying=True,
    desc_en="Floats, then explodes near you.", desc_fr="Flotte puis explose près du joueur.")
mob("sky_harpooner", "Sky Harpooner", "Harponneur céleste", 4, 59, 8.6, "harpoon", "biped", 1.1, "celestial_crystal", elite=True,
    desc_en="Elite. Drags you toward the void.", desc_fr="Élite, attire le joueur vers le vide.")

mob("blind_prowler", "Blind Prowler", "Rôdeur aveugle", 5, 86, 14.5, "sound_hunter", "quad", 1.2, "shadow_shard",
    desc_en="Hunts by sound. Sneak.", desc_fr="Chasse au son. Accroupis-toi.")
mob("glow_devourer", "Glow Devourer", "Dévoreur de lueur", 5, 73, 8.3, "light_eater", "blob", 1.0, "shadow_shard",
    desc_en="Snuffs out your lights.", desc_fr="Éteint les lumières du joueur.")
mob("echo", "Echo", "Écho", 5, 53, 10.4, "lurer", "wisp", 0.9, "diamond_fragment",
    desc_en="Mimics sounds to lure you.", desc_fr="Imite les sons pour attirer le joueur.")
mob("eyeless_watcher", "Eyeless Watcher", "Veilleur sans yeux", 5, 100, 12.4, "statue", "robed", 1.6, "diamond_fragment",
    desc_en="Still while you are silent.", desc_fr="Immobile tant que le joueur est silencieux.")
mob("shadow_mother", "Shadow Mother", "Mère des ombres", 5, 146, 14.5, "melee", "quad", 1.6, "shadow_shard", elite=True, nesting=True,
    desc_en="Elite, nesting: releases shadows.", desc_fr="Élite, gigogne, libère plusieurs ombres.")

mob("reflection", "Reflection", "Reflet", 6, 90, 14.9, "copycat", "biped", 1.0, "inverted_crystal",
    desc_en="Copies your last attack.", desc_fr="Copie la dernière attaque du joueur.")
mob("ceiling_walker", "Ceiling Walker", "Marcheur de plafond", 6, 117, 12.4, "wall_crawler", "spider", 1.2, "unstable_alloy",
    desc_en="Walks on every surface.", desc_fr="Se déplace sur toutes les surfaces.")
mob("unstable_sphere", "Unstable Sphere", "Sphère instable", 6, 63, 19.9, "gravity_orb", "orb", 1.0, "unstable_alloy", flying=True,
    desc_en="Flips gravity around it when it dies.", desc_fr="Inverse la gravité autour d'elle à sa mort.")
mob("inverted_strider", "Inverted Strider", "Arpenteur inversé", 6, 135, 14.9, "melee_reach", "tall", 1.4, "inverted_crystal",
    desc_en="Fights upside down, strikes through platforms.", desc_fr="Combat la tête en bas et frappe à travers les plateformes.")
mob("broken_mirror", "Broken Mirror", "Miroir brisé", 6, 179, 17.4, "reflect", "block", 1.4, "inverted_crystal", elite=True, nesting=True,
    desc_en="Elite, nesting: reflects damage.", desc_fr="Élite, gigogne, renvoie une partie des dégâts.")

mob("abyssal_hunter", "Abyssal Hunter", "Chasseur abyssal", 7, 157, 20.9, "swimmer", "fish", 1.5, "abyssal_salt", aquatic=True,
    desc_en="Circles, then charges from below.", desc_fr="Encercle, puis charge par le bas.")
mob("blade_school", "Blade School", "Banc de lames", 7, 73, 11.9, "swimmer_oxygen", "fish_small", 0.6, "abyssal_salt", aquatic=True,
    desc_en="Fast swarm, drains oxygen.", desc_fr="Essaim rapide, consomme l'oxygène.")
mob("pressure_jelly", "Pressure Jelly", "Méduse de pression", 7, 121, 14.9, "pressure_aura", "jelly", 1.2, "pressure_pearl", aquatic=True,
    desc_en="Raises pressure around it.", desc_fr="Augmente la pression autour d'elle.")
mob("bell_crab", "Bell Crab", "Crabe-cloche", 7, 242, 17.9, "melee", "crab", 1.4, "pressure_pearl", nesting=True, aquatic=True,
    desc_en="Nesting: shelters smaller crabs.", desc_fr="Gigogne, abrite des crabes plus petits.")
mob("trench_eel", "Trench Eel", "Murène des fosses", 7, 182, 23.9, "grabber", "eel", 1.6, "pressure_pearl", elite=True, aquatic=True,
    desc_en="Elite. Bursts from walls and grabs you.", desc_fr="Élite, surgit des parois et saisit le joueur.")

mob("seasonal_creature", "Seasonal Creature", "Créature saisonnière", 8, 180, 21.5, "seasonal", "quad", 1.2, "season_fragment",
    desc_en="Changes attacks with the season.", desc_fr="Change d'attaques selon la saison.")
mob("hourglass_elder", "Hourglass Elder", "Vieillard du sablier", 8, 245, 17.9, "slowing_aura", "robed", 1.1, "temporal_sand",
    desc_en="Slows everything around it.", desc_fr="Ralentit les actions autour de lui.")
mob("dusk_shade", "Dusk Shade", "Ombre du crépuscule", 8, 196, 25.1, "melee", "wisp", 1.3, "temporal_sand",
    desc_en="Appears only when day turns to night.", desc_fr="N'apparaît qu'au changement jour et nuit.")
mob("minute_child", "Child of Minutes", "Enfant des minutes", 8, 114, 14.3, "grower", "imp", 0.7, "season_fragment",
    desc_en="Grows stronger during the fight.", desc_fr="Grandit et se renforce pendant le combat.")
mob("hour_keeper", "Hour Keeper", "Gardien de l'heure", 8, 368, 28.7, "cycle", "golem", 1.6, "temporal_sand", elite=True,
    desc_en="Elite. Repeats its strikes on a cycle.", desc_fr="Élite, répète ses coups selon un cycle.")

mob("crawling_block", "Crawling Block", "Bloc rampant", 9, 331, 25.8, "mimic", "block", 1.0, "terrain_fragment",
    desc_en="Disguises itself as terrain.", desc_fr="Se déguise en terrain et se déplace.")
mob("mimic", "Mimic", "Mimique", 9, 287, 30.1, "mimic", "chest", 1.0, "terrain_fragment",
    desc_en="Pretends to be a chest, an ore or a door.", desc_fr="Imite un coffre, un minerai ou une porte.")
mob("foundation_eater", "Foundation Eater", "Dévoreur de fondations", 9, 309, 21.5, "block_eater", "worm", 1.3, "terrain_fragment",
    desc_en="Eats unanchored blocks.", desc_fr="Mange les blocs non ancrés.")
mob("earth_hand", "Earth Hand", "Main de terre", 9, 265, 34.4, "grabber", "hand", 1.4, "terrain_fragment",
    desc_en="Bursts from the ground and grabs you.", desc_fr="Surgit du sol et attrape le joueur.")
mob("walking_column", "Walking Column", "Colonne marcheuse", 9, 496, 34.4, "area_slam", "column", 1.8, "terrain_fragment", "terrain_heart", elite=True, nesting=True,
    desc_en="Elite, nesting: falls and opens chasms.", desc_fr="Élite, gigogne, tombe et crée des gouffres.")

mob("giant_sporeling", "Giant Sporeling", "Sporelin géant", 10, 447, 36.1, "splitter", "imp", 2.2, "artisan_thread",
    desc_en="Splits into groups of Sporelings.", desc_fr="Se sépare en groupes de Sporelins.")
mob("ash_titanid", "Ash Titanid", "Titanide de cendre", 10, 536, 31, "lava_heat", "biped", 2.4, "artisan_thread",
    desc_en="Raises the heat of the area.", desc_fr="Fait monter la chaleur de la zone.")
mob("colossal_jailer", "Colossal Jailer", "Geôlier colossal", 10, 596, 36.1, "caller", "robed", 2.6, "artisan_thread",
    desc_en="Locks whole sections of the workshop.", desc_fr="Ferme des pans entiers de l'atelier.")
mob("titan_ray", "Titan Ray", "Raie-titan", 10, 417, 41.3, "flyer_push", "ray", 3.0, "artisan_thread", flying=True,
    desc_en="Pushes you with huge gusts.", desc_fr="Pousse le joueur par de grandes rafales.")
mob("colossus_prowler", "Colossus Prowler", "Rôdeur-colosse", 10, 745, 41.3, "sound_hunter", "quad", 2.6, "artisan_shard", elite=True,
    desc_en="Elite. Hunts by sound in the dark.", desc_fr="Élite, chasse au son dans le noir.")

# NPC peoples (one per world) + the Peddler
PEOPLES = [
    ("doll_peddler", "Doll Peddler", "Colporteur de poupées", 0),
    ("gatherer", "Gatherer", "Cueilleur", 1), ("free_miner", "Free Miner", "Mineur libre", 2),
    ("prisoner", "Prisoner", "Prisonnier", 3), ("lighthouse_keeper", "Lighthouse Folk", "Gens du phare", 4),
    ("silent_one", "Silent One", "Silencieux", 5), ("free_reflection", "Free Reflection", "Reflet libre", 6),
    ("diver", "Diver", "Plongeur", 7), ("ephemeral", "Ephemeral", "Éphémère", 8),
    ("anchored", "Anchored", "Ancré", 9), ("old_apprentice", "Old Apprentice", "Ancien apprenti", 10),
]

# Harmless wildlife: no attacks, it only fills the world. behavior: "shoal" (a darting school that flees players),
# "drift" (a slow glowing drifter). Models come from tools/mobs_hd like the creatures'.
CRITTERS = [
    dict(id="lantern_shoal", en="Lantern Shoal", fr="Banc de lanternes", world=7, hp=6, behavior="shoal", drop="minecraft:cod",
         desc_en="A school of tiny glowing fish. Harmless, it darts away from swimmers.",
         desc_fr="Un banc de petits poissons lumineux. Inoffensif, il file devant les nageurs."),
    dict(id="glow_jelly", en="Glow Jelly", fr="Méduse lumineuse", world=7, hp=8, behavior="drift", drop="minecraft:glow_ink_sac",
         desc_en="A small jellyfish that lights the deep as it drifts. Harmless.",
         desc_fr="Une petite méduse qui éclaire les profondeurs en dérivant. Inoffensive."),
]

# ---------------------------------------------------------------- bosses
# attacks: light, medium, signature, final phase
# meet: "altar" (woken at the arena altar with its offering; the Guardian needs none) or "lair" (woken by the
# lair heart at the centre of its lair). wake: the chat line of the lair awakening.
BOSSES = [
    dict(id="block_guardian", meet="altar", offering="",
         en="Block Guardian", fr="Gardien du bloc", world=0, hp=300, dmg=12, body="guardian", size=2.2,
         core="guardian_core", phases=(0.5,),
         atk=[("Punch", "Coup de poing"), ("Shockwave", "Onde de choc"), ("Torn Block", "Bloc arraché et lancé"), ("Rebuilds itself from the arena", "Se reconstruit avec l'arène")]),
    dict(id="spore_queen", meet="lair", wake=("The cocoons split and the hive hums: the Spore Queen awakens.", "Les cocons se fendent et la ruche bourdonne : la Reine des spores s'éveille."),
         en="Spore Queen", fr="Reine des spores", world=1, hp=500, dmg=12, body="queen", size=2.4,
         core="queen_core", phases=(0.66, 0.33),
         atk=[("Root Snare", "Racine sous les pieds"), ("Toxic Cloud", "Nuage toxique"), ("Call of Sporelings", "Appel de Sporelins"), ("Cocoon guarded by nodes", "Cocon à briser par ses nœuds")]),
    dict(id="ash_titan", meet="lair", wake=("The great furnace roars back to life: the Ash Titan rises from the embers.", "La grande fournaise reprend vie : le Titan de cendre se relève des braises."),
         en="Ash Titan", fr="Titan de cendre", world=2, hp=675, dmg=14.4, body="titan", size=3.0,
         core="titan_core", phases=(0.66, 0.33),
         atk=[("Hammer Blow", "Coup de marteau"), ("Ash Spray", "Projection de cendre"), ("Rising Lava", "Lave montante"), ("Molten armor, exposed heart", "Armure fondue, cœur exposé")]),
    dict(id="grand_jailer", meet="altar", offering="sealed_shackle",
         en="Grand Jailer", fr="Grand Geôlier", world=3, hp=911, dmg=17.3, body="jailer", size=2.6,
         core="jailer_core", phases=(0.66, 0.33),
         atk=[("Chain Pull", "Chaîne tirée"), ("Floor Cage", "Cage au sol"), ("Moving Walls", "Murs mobiles"), ("The arena becomes a cell", "L'arène devient une cellule")]),
    dict(id="storm_king", meet="altar", offering="storm_censer",
         en="Storm King", fr="Roi des tempêtes", world=4, hp=1230, dmg=20.7, body="storm_king", size=2.6,
         core="storm_king_core", phases=(0.66, 0.33), flying=True,
         atk=[("Gust", "Bourrasque"), ("Called Lightning", "Éclair annoncé"), ("Shattered Islet", "Îlot détruit"), ("Fight on drifting debris", "Combat sur des débris")]),
    dict(id="light_eater", meet="lair", wake=("The last glimmer goes out. Something at the bottom of the pit was waiting: the Light Eater wakes.", "La dernière lueur s'éteint. Quelque chose attendait au fond du puits : le Mangeur de lumière s'éveille."),
         en="Light Eater", fr="Mangeur de lumière", world=5, hp=1661, dmg=24.9, body="light_eater", size=2.6,
         core="light_eater_core", phases=(0.66, 0.33),
         atk=[("Claw in the Dark", "Griffe dans le noir"), ("Lights Out", "Extinction de lumières"), ("Silent Charge", "Charge silencieuse"), ("Track it by sound only", "Repérage au son seulement")]),
    dict(id="your_double", meet="lair", wake=("Every mirror cracks at once and one reflection steps out: Your Double.", "Tous les miroirs se fêlent d'un coup et un reflet en sort : Ton Double."),
         en="Your Double", fr="Ton Double", world=6, hp=2242, dmg=29.9, body="double", size=1.0,
         core="double_core", phases=(0.66, 0.33),
         atk=[("Copied Strike", "Copie de ton coup"), ("Copied Weapon", "Copie de ton arme"), ("Gravity Flip", "Inversion de gravité"), ("It adopts your play style", "Il adopte ton style de jeu")]),
    dict(id="pressure_leviathan", meet="lair", wake=("The trench groans under the weight of the sea: the Pressure Leviathan uncoils.", "La fosse gémit sous le poids de la mer : le Léviathan de pression se déroule."),
         en="Pressure Leviathan", fr="Léviathan de pression", world=7, hp=3027, dmg=35.8, body="leviathan", size=3.2,
         core="leviathan_core", phases=(0.66, 0.33), aquatic=True,
         atk=[("Tail Lash", "Coup de queue"), ("Charge", "Charge"), ("Abyssal Pull", "Aspiration"), ("Depth and oxygen worsen", "Profondeur et oxygène aggravés")]),
    dict(id="seasons_master", meet="altar", offering="wreath_of_seasons",
         en="Master of Seasons", fr="Maître des saisons", world=8, hp=4086, dmg=43, body="seasons", size=2.8,
         core="seasons_core", phases=(0.66, 0.33),
         atk=[("Seasonal Strike", "Coup saisonnier"), ("Seasonal Ground", "Terrain saisonnier"), ("Season Shift", "Changement de saison"), ("Overlapping seasons", "Saisons superposées")]),
    dict(id="terrain_heart_boss", meet="lair", wake=("The veins of the cavern start to beat: the Heart of the Terrain awakens.", "Les veines de la caverne se mettent à battre : le Cœur du terrain s'éveille."),
         en="Heart of the Terrain", fr="Cœur du terrain", world=9, hp=5516, dmg=51.6, body="heart", size=3.0,
         core="terrain_core", phases=(0.66, 0.33),
         atk=[("Ground Wave", "Vague de sol"), ("Living Wall", "Mur vivant"), ("Chasm", "Gouffre"), ("The floor vanishes in sections", "Le sol disparaît par sections")]),
    dict(id="the_unfinished", meet="altar", offering="unfinished_effigy",
         en="The Unfinished", fr="L'Inachevée", world=10, hp=14894, dmg=61.9, body="unfinished", size=3.4,
         core="unfinished_core", phases=tuple(round(1 - i / 10, 2) for i in range(1, 10)),
         atk=[("Shell Attack", "Attaque de l'enveloppe"), ("Shell Attack", "Attaque de l'enveloppe"), ("Shell Attack", "Attaque de l'enveloppe"), ("A tiny final form", "Dernière forme minuscule")]),
]

# ---------------------------------------------------------------- structures (10 per world)
# archetype implemented in Java StructureBuilder: hive, nest, well, tower, ruin, temple, village, shrine,
# cocoon, mine, rail, forge, camp, arena, maze, vault, crypt, library, cell, island, bridge, lighthouse,
# wreck, cathedral, garden, lab, stair, bell, city, clock, market, fort, chasm, throne
STRUCTURES = {
    1: [("spore_hive", "Spore Hive", "Ruche de spores", "combat", "medium", "common", "hive"),
        ("sporeling_nest", "Sporeling Nest", "Nid de Sporelins", "combat", "small", "common", "nest"),
        ("toxin_well", "Toxin Well", "Puits de toxine", "combat", "medium", "rare", "well"),
        ("hollow_tree", "Hollow Tree", "Arbre creux", "exploration", "small", "common", "tower"),
        ("abandoned_greenhouse", "Abandoned Greenhouse", "Serre abandonnée", "exploration", "medium", "rare", "garden"),
        ("giant_cocoon", "Giant Cocoon", "Cocon géant", "exploration", "medium", "rare", "cocoon"),
        ("root_temple", "Root Temple", "Temple racinaire", "story", "large", "unique", "temple"),
        ("purified_clearing", "Purified Clearing", "Clairière purifiée", "story", "medium", "unique", "shrine"),
        ("gatherer_village", "Gatherer Village", "Village de cueilleurs", "utility", "large", "rare", "village"),
        ("artisan_sanctuary", "Artisan's Sanctuary", "Sanctuaire de l'artisan", "secret", "small", "unique", "vault")],
    2: [("salamander_cavern", "Salamander Cavern", "Caverne de salamandres", "combat", "medium", "common", "nest"),
        ("giant_furnace", "Giant Furnace", "Fournaise géante", "combat", "large", "rare", "forge"),
        ("lava_well", "Lava Well", "Puits de lave", "combat", "medium", "common", "well"),
        ("collapsed_mine", "Collapsed Mine", "Mine effondrée", "exploration", "medium", "common", "mine"),
        ("hanging_rail", "Hanging Rail", "Rail suspendu", "exploration", "medium", "common", "rail"),
        ("crystal_works", "Crystal Works", "Cristallerie", "exploration", "medium", "rare", "garden"),
        ("abandoned_forge", "Abandoned Forge", "Forge abandonnée", "story", "medium", "rare", "forge"),
        ("vein_sanctuary", "Vein Sanctuary", "Sanctuaire du filon", "story", "large", "unique", "temple"),
        ("miner_camp", "Miners' Camp", "Camp de mineurs", "utility", "medium", "rare", "camp"),
        ("artisan_workshop", "Artisan's Workshop", "Atelier de l'artisan", "secret", "small", "unique", "vault")],
    3: [("arena", "Arena", "Arène", "combat", "medium", "common", "arena"),
        ("jailer_court", "Jailers' Court", "Cour des Geôliers", "combat", "medium", "common", "arena"),
        ("moving_hall", "Moving Hall", "Salle mobile", "combat", "medium", "common", "maze"),
        ("trap_maze", "Trap Labyrinth", "Labyrinthe de pièges", "exploration", "large", "rare", "maze"),
        ("treasury", "Treasury", "Trésorerie", "exploration", "medium", "rare", "vault"),
        ("crypt", "Crypt", "Crypte", "exploration", "medium", "common", "crypt"),
        ("sealed_library", "Sealed Library", "Bibliothèque scellée", "story", "medium", "unique", "library"),
        ("key_hall", "Hall of Keys", "Salle des clés", "story", "medium", "unique", "shrine"),
        ("prison", "Prison", "Prison", "utility", "large", "rare", "cell"),
        ("artisan_cell", "Artisan's Cell", "Cellule de l'artisan", "secret", "small", "unique", "vault")],
    4: [("ray_nest", "Ray Nest", "Nid de raies", "combat", "medium", "common", "nest"),
        ("giant_lightning_rod", "Giant Lightning Rod", "Paratonnerre géant", "combat", "large", "rare", "tower"),
        ("flying_wreck", "Flying Wreck", "Épave volante", "combat", "medium", "rare", "wreck"),
        ("hanging_ruin", "Hanging Ruin", "Ruine suspendue", "exploration", "medium", "common", "ruin"),
        ("broken_bridge", "Broken Bridge", "Pont brisé", "exploration", "large", "common", "bridge"),
        ("storm_lighthouse", "Storm Lighthouse", "Phare des tempêtes", "exploration", "medium", "common", "lighthouse"),
        ("celestial_temple", "Celestial Temple", "Temple céleste", "story", "large", "unique", "temple"),
        ("observatory", "Observatory", "Observatoire", "story", "medium", "rare", "tower"),
        ("floating_village", "Floating Village", "Village flottant", "utility", "large", "rare", "village"),
        ("cloud_garden", "Cloud Garden", "Jardin des nuages", "secret", "small", "unique", "garden")],
    5: [("prowler_nest", "Prowler Nest", "Nid de rôdeurs", "combat", "medium", "common", "nest"),
        ("echo_cemetery", "Echo Cemetery", "Cimetière d'échos", "combat", "medium", "common", "crypt"),
        ("black_cathedral", "Black Cathedral", "Cathédrale noire", "combat", "large", "rare", "cathedral"),
        ("dark_tower", "Dark Tower", "Tour éteinte", "exploration", "medium", "common", "tower"),
        ("bottomless_mine", "Bottomless Mine", "Mine sans fond", "exploration", "large", "rare", "mine"),
        ("light_well", "Light Well", "Puits de lumière", "exploration", "medium", "rare", "well"),
        ("blind_sanctuary", "Blind Sanctuary", "Sanctuaire aveugle", "story", "medium", "unique", "shrine"),
        ("fresco_gallery", "Fresco Gallery", "Galerie de fresques", "story", "medium", "unique", "library"),
        ("silent_village", "Silent Village", "Village silencieux", "utility", "large", "rare", "village"),
        ("artisan_shelter", "Artisan's Shelter", "Abri de l'artisan", "secret", "small", "unique", "vault")],
    6: [("mirror_hall", "Hall of Mirrors", "Salle des miroirs", "combat", "medium", "common", "arena"),
        ("hanging_cage", "Hanging Cage", "Cage suspendue", "combat", "small", "common", "cell"),
        ("unstable_core", "Unstable Core", "Noyau instable", "combat", "large", "rare", "cocoon"),
        ("inverted_tower", "Inverted Tower", "Tour inversée", "exploration", "large", "rare", "tower"),
        ("ceiling_city", "Ceiling City", "Cité au plafond", "exploration", "large", "rare", "city"),
        ("upturned_pool", "Upturned Pool", "Bassin renversé", "exploration", "medium", "common", "well"),
        ("gravity_lab", "Gravity Lab", "Laboratoire de gravité", "story", "medium", "unique", "lab"),
        ("impossible_stair", "Impossible Stair", "Escalier impossible", "story", "medium", "unique", "stair"),
        ("reflection_refuge", "Reflection Refuge", "Refuge des Reflets", "utility", "medium", "rare", "village"),
        ("floating_garden", "Floating Garden", "Jardin flottant", "secret", "small", "unique", "garden")],
    7: [("hunter_trench", "Hunters' Trench", "Fosse des chasseurs", "combat", "large", "common", "chasm"),
        ("dead_reef", "Dead Reef", "Récif mort", "combat", "medium", "common", "ruin"),
        ("sunken_city", "Sunken City", "Cité engloutie", "combat", "large", "rare", "city"),
        ("wreck", "Wreck", "Épave", "exploration", "medium", "common", "wreck"),
        ("diving_bell", "Diving Bell", "Cloche de plongée", "exploration", "small", "common", "bell"),
        ("air_grotto", "Air Grotto", "Grotte à air", "exploration", "medium", "common", "cocoon"),
        ("abyssal_temple", "Abyssal Temple", "Temple abyssal", "story", "large", "unique", "temple"),
        ("sunken_lighthouse", "Sunken Lighthouse", "Phare sous-marin", "story", "medium", "unique", "lighthouse"),
        ("pressure_station", "Pressure Station", "Station de pression", "utility", "large", "rare", "lab"),
        ("deep_vault", "Vault of the Deep", "Coffre-fort des profondeurs", "secret", "small", "unique", "vault")],
    8: [("hastened_town", "Hastened Town", "Ville accélérée", "combat", "large", "rare", "city"),
        ("aging_ruin", "Aging Ruin", "Ruine vieillissante", "combat", "medium", "common", "ruin"),
        ("giant_clock", "Giant Clock", "Horloge géante", "combat", "large", "rare", "clock"),
        ("season_greenhouse", "Greenhouse of Seasons", "Serre des saisons", "exploration", "medium", "common", "garden"),
        ("frozen_garden", "Frozen Garden", "Jardin figé", "exploration", "medium", "common", "shrine"),
        ("ephemeral_camp", "Ephemeral Camp", "Camp éphémère", "exploration", "small", "common", "camp"),
        ("solar_observatory", "Solar Observatory", "Observatoire solaire", "story", "medium", "unique", "tower"),
        ("library_of_ages", "Library of Ages", "Bibliothèque des siècles", "story", "large", "unique", "library"),
        ("dusk_market", "Dusk Market", "Marché du crépuscule", "utility", "large", "rare", "market"),
        ("time_tomb", "Time Tomb", "Tombeau temporel", "secret", "small", "unique", "vault")],
    9: [("walking_tower", "Walking Tower", "Tour qui marche", "combat", "large", "rare", "tower"),
        ("mobile_fortress", "Mobile Fortress", "Forteresse mobile", "combat", "large", "rare", "fort"),
        ("terrain_arena", "Terrain Arena", "Arène de terrain", "combat", "medium", "common", "arena"),
        ("moving_ruin", "Moving Ruin", "Ruine mouvante", "exploration", "medium", "common", "ruin"),
        ("living_chasm", "Living Chasm", "Gouffre vivant", "exploration", "large", "rare", "chasm"),
        ("mimic_nest", "Mimic Nest", "Nid de mimiques", "exploration", "medium", "common", "nest"),
        ("buried_village", "Buried Village", "Village enseveli", "story", "medium", "unique", "village"),
        ("beating_vein", "Beating Vein", "Veine battante", "story", "medium", "unique", "shrine"),
        ("anchored_fort", "Anchored Fort", "Fort ancré", "utility", "large", "rare", "fort"),
        ("stable_sanctuary", "Stable Sanctuary", "Sanctuaire stable", "secret", "small", "unique", "vault")],
    10: [("needle_tower", "Needle Tower", "Tour d'aiguilles", "combat", "large", "rare", "tower"),
         ("colossal_forge", "Colossal Forge", "Forge colossale", "combat", "large", "rare", "forge"),
         ("collapsed_doll", "Collapsed Doll", "Poupée effondrée", "combat", "large", "rare", "cocoon"),
         ("giant_chest", "Giant Chest", "Coffre géant", "exploration", "large", "rare", "vault"),
         ("colossal_library", "Colossal Library", "Bibliothèque colossale", "exploration", "large", "unique", "library"),
         ("titanic_workbench", "Titanic Workbench", "Établi titanesque", "exploration", "large", "unique", "arena"),
         ("artisan_giant_workshop", "Artisan's Giant Workshop", "Atelier géant de l'artisan", "story", "large", "unique", "temple"),
         ("block_gate", "Block Gate", "Porte de bloc", "story", "medium", "unique", "shrine"),
         ("city_of_giants", "City of Giants", "Cité des géants", "utility", "large", "rare", "city"),
         ("creature_throne", "Throne of the Creature", "Trône de la créature", "secret", "medium", "unique", "throne")],
}

# ---------------------------------------------------------------- quests (64)
# type: guide | npc | karma | challenge ; obj: (kind, target, count)
QUESTS = [
    # Surface
    ("read_between_lines", 0, "guide", ("read", "artisan_scroll", 5), "Read Between the Lines", "Lire entre les lignes", "Read the 5 pages of the Scroll.", "Lire les 5 pages du Parchemin.", ("item", "return_thread", 5)),
    ("first_guardian", 0, "guide", ("kill", "block_guardian", 1), "The First Guardian", "Le premier Gardien", "Defeat the Block Guardian.", "Vaincre le Gardien du bloc.", ("souls", "", 10)),
    ("fingers_in_the_doll", 0, "guide", ("craft", "seed_1", 1), "Fingers in the Doll", "Les doigts dans la poupée", "Craft the Matrix Workbench and a Seed.", "Fabriquer l'Établi matriciel et une Graine.", ("item", "soul_cradle", 1)),
    ("the_peddler", 0, "npc", ("trade", "doll_peddler", 1), "The Peddler", "Le Colporteur", "Find the Peddler and trade with him.", "Trouver le Colporteur et commercer avec lui.", ("title", "painted_cape", 1)),
]
_Q = {
    1: [("breathe_to_begin", "guide", ("craft", "filter_mask", 1), "Breathe to Begin", "Respirer pour commencer", "Craft a Filter Mask.", "Fabriquer un masque filtrant.", ("item", "antidote", 3)),
        ("the_vat", "guide", ("craft", "antidote", 1), "The Vat", "La Cuve", "Ferment a first recipe.", "Fermenter une première recette.", ("souls", "", 10)),
        ("hard_harvest", "npc", ("deliver", "spores", 16), "Hard Harvest", "Récolte difficile", "Bring 16 spores to the herbalist.", "Rapporter 16 spores à l'herboriste.", ("item", "antidote", 5)),
        ("lost_scouts", "npc", ("kill", "sporeling", 10), "The Lost Scouts", "Les éclaireurs perdus", "Clear the jungle of 10 Sporelings.", "Débarrasser la jungle de 10 Sporelins.", ("item", "labyrinth_map", 1)),
        ("the_clearing", "karma", ("choice", "", 5), "The Clearing", "La clairière", "Purify the clearing (+5) or burn it for loot (-5).", "Purifier la clairière (+5) ou la brûler pour son butin (-5).", ("souls", "", 20)),
        ("no_filter", "challenge", ("kill", "chitin_guard", 1), "No Filter", "Sans filtre", "Kill a Chitin Guard without a mask.", "Tuer un Gardien de chitine sans masque.", ("title", "iron_lungs", 1))],
    2: [("under_control", "guide", ("craft", "ash_ingot", 1), "Under Control", "Sous contrôle", "Keep the Foundry at the right temperature.", "Maintenir la Fonderie à la bonne température.", ("item", "blazing_rock", 16)),
        ("first_vein", "guide", ("obtain", "giant_ore", 1), "The First Vein", "Le premier filon", "Extract a whole giant ore.", "Extraire un minerai géant entier.", ("item", "cooling_water", 4)),
        ("miners_pay", "npc", ("deliver", "ash_ingot", 8), "The Miners' Pay", "La paie des mineurs", "Bring 8 ash ingots to the foreman.", "Rapporter 8 lingots de cendre au contremaître.", ("souls", "", 20)),
        ("flooded_shaft", "npc", ("kill", "rock_salamander", 8), "Flooded Shaft", "Puits inondé de lave", "Rescue a stuck team (8 salamanders).", "Secourir une équipe bloquée (8 salamandres).", ("item", "cooling_water", 8)),
        ("the_strike", "karma", ("choice", "", 5), "The Strike", "La grève", "Support the miners (+5) or sell their plans (-5).", "Soutenir les mineurs (+5) ou vendre leurs plans (-5).", ("souls", "", 30)),
        ("bare_hands", "challenge", ("kill", "slag_golem", 1), "Bare Hands", "Mains nues", "Kill a Slag Golem without armor.", "Tuer un Golem de scories sans armure.", ("title", "ash_skin", 1))],
    3: [("turn_the_key", "guide", ("use", "dungeon_key", 3), "Turn the Key", "Tourner la clé", "Open 3 doors with keys.", "Ouvrir 3 zones avec des clés.", ("item", "lockpick_kit", 5)),
        ("read_the_plan", "guide", ("craft", "labyrinth_map", 1), "Read the Plan", "Lire le plan", "Complete a labyrinth map.", "Compléter une carte du labyrinthe.", ("souls", "", 20)),
        ("the_locksmith", "npc", ("kill", "living_lock", 5), "The Locksmith", "Le serrurier", "Defeat 5 living locks.", "Rapporter 5 serrures vivantes vaincues.", ("souls", "", 20)),
        ("last_message", "npc", ("deliver", "journal_page", 1), "Last Message", "Dernier message", "Carry a letter from cell to cell.", "Porter une lettre de cellule en cellule.", ("item", "journal_page", 1)),
        ("the_escape", "karma", ("choice", "", 10), "The Escape", "L'évasion", "Free the prisoners (+10) or claim the bounty (-10).", "Libérer les prisonniers (+10) ou réclamer la prime (-10).", ("souls", "", 40)),
        ("keyless", "challenge", ("kill", "executioner", 1), "Keyless", "Sans clé", "Defeat an Executioner.", "Vaincre un Bourreau.", ("title", "wall_walker", 1))],
    4: [("first_flight", "guide", ("craft", "glider", 1), "First Flight", "Le premier vol", "Craft a glider and cross three islands.", "Fabriquer un planeur et traverser trois îles.", ("item", "ray_membrane", 16)),
        ("catch_lightning", "guide", ("craft", "lightning_lance", 1), "Catch the Lightning", "Attraper la foudre", "Charge an item at the Forge.", "Charger un objet à la Forge.", ("souls", "", 30)),
        ("light_the_lighthouse", "npc", ("deliver", "storm_essence", 3), "Light the Lighthouse", "Allumer le phare", "Rekindle 3 lighthouses.", "Rallumer 3 phares.", ("item", "grappling_hook", 1)),
        ("cartographer_road", "npc", ("kill", "wind_ray", 6), "The Cartographer's Road", "La route du cartographe", "Clear the routes of 6 wind rays.", "Dégager les routes de 6 raies du vent.", ("souls", "", 30)),
        ("the_wreck", "karma", ("choice", "", 5), "The Wreck", "L'épave", "Return the cargo (+5) or keep it (-5).", "Rendre la cargaison (+5) ou la garder (-5).", ("souls", "", 30)),
        ("perfect_storm", "challenge", ("kill", "sky_harpooner", 1), "Perfect Storm", "Tempête parfaite", "Defeat a Sky Harpooner.", "Vaincre un Harponneur céleste.", ("title", "wind_child", 1))],
    5: [("lasting_light", "guide", ("craft", "solar_lantern", 1), "A Lasting Light", "Une lumière qui dure", "Craft a Solar Lantern.", "Fabriquer une lanterne solaire.", ("item", "silence_balm", 16)),
        ("hear_the_danger", "guide", ("use", "sonar", 3), "Hear the Danger", "Entendre le danger", "Spot 3 mobs with the sonar.", "Repérer 3 mobs avec le sonar.", ("souls", "", 30)),
        ("the_signs", "npc", ("deliver", "shadow_shard", 5), "The Signs", "Les signes", "Learn 5 signs of the Silent Ones.", "Apprendre 5 signes des Silencieux.", ("souls", "", 30)),
        ("the_night_light", "npc", ("kill", "glow_devourer", 6), "The Night Light", "La veilleuse", "Escort the keeper (6 Glow Devourers).", "Accompagner la veilleuse (6 Dévoreurs de lueur).", ("title", "glow", 1)),
        ("last_fire", "karma", ("choice", "", 5), "The Last Fire", "Le dernier feu", "Relight the village (+5) or steal its flame (-5).", "Rallumer le village (+5) ou voler sa flamme (-5).", ("souls", "", 50)),
        ("pitch_black", "challenge", ("kill", "shadow_mother", 1), "Pitch Black", "Noir complet", "Defeat a Shadow Mother.", "Vaincre une Mère des ombres.", ("title", "closed_eyes", 1))],
    6: [("fall_upward", "guide", ("craft", "gravity_boots", 1), "Fall Upward", "Tomber vers le haut", "Craft gravity boots.", "Fabriquer les bottes de gravité.", ("item", "stabilizer", 8)),
        ("double_meaning", "guide", ("craft", "mirror_blade", 1), "Double Meaning", "Le double sens", "Use the Inverter.", "Utiliser l'Inverseur.", ("souls", "", 30)),
        ("lost_reflection", "npc", ("kill", "reflection", 5), "Lost Reflection", "Reflet perdu", "Bring back an NPC's double.", "Ramener le double d'un PNJ.", ("souls", "", 30)),
        ("impossible_stair", "npc", ("deliver", "inverted_crystal", 2), "The Impossible Stair", "L'escalier impossible", "Reach the top of the stair.", "Atteindre le sommet de l'escalier.", ("item", "journal_page", 1)),
        ("who_is_real", "karma", ("choice", "", 5), "Who Is Real?", "Qui est le vrai ?", "Free the Reflection (+5) or take its place (-5).", "Libérer le Reflet (+5) ou prendre sa place (-5).", ("souls", "", 50)),
        ("upside_down", "challenge", ("kill", "broken_mirror", 1), "Upside Down", "Sens dessus dessous", "Defeat a Broken Mirror.", "Vaincre un Miroir brisé.", ("title", "head_down", 1))],
    7: [("under_pressure", "guide", ("craft", "salt_snorkel", 1), "Under Pressure", "Sous pression", "Craft a Salt Snorkel Helmet at the Abyssal Press.", "Fabriquer un casque-tuba de sel à la Presse abyssale.", ("item", "oxygen_capsule", 8)),
        ("compress", "guide", ("craft", "pressure_pearl", 1), "Compress", "Comprimer", "Press something at the Abyssal Press.", "Comprimer à la Presse abyssale.", ("souls", "", 40)),
        ("silent_station", "npc", ("deliver", "abyssal_salt", 6), "The Silent Station", "La station se tait", "Repair 3 station cables.", "Réparer 3 câbles de la station.", ("item", "thruster", 1)),
        ("wreck_crew", "npc", ("kill", "blade_school", 10), "The Wreck's Crew", "L'équipage de l'épave", "Recover 3 crew plates.", "Remonter 3 plaques d'équipage.", ("souls", "", 40)),
        ("the_signal", "karma", ("choice", "", 10), "The Signal", "Le signal", "Rescue the castaways (+10) or divert their oxygen (-10).", "Secourir les naufragés (+10) ou détourner leur oxygène (-10).", ("souls", "", 60)),
        ("one_breath", "challenge", ("kill", "trench_eel", 1), "One Breath", "Un souffle", "Defeat a Trench Eel.", "Vaincre une Murène des fosses.", ("title", "cold_blood", 1))],
    8: [("four_seasons", "guide", ("obtain", "season_fragment", 4), "Four Seasons", "Quatre saisons", "Live through a full cycle.", "Traverser un cycle complet.", ("item", "season_preserve", 8)),
        ("stop_the_instant", "guide", ("use", "hourglass", 1), "Stop the Instant", "Arrêter l'instant", "Use an hourglass.", "Utiliser un sablier.", ("souls", "", 40)),
        ("life_in_a_day", "npc", ("deliver", "temporal_sand", 8), "A Life in a Day", "Une vie en un jour", "Help an Ephemeral before nightfall.", "Aider un Éphémère avant la nuit.", ("item", "season_fragment", 1)),
        ("the_archives", "npc", ("deliver", "journal_page", 1), "The Archives", "Les archives", "Find 5 books of the library.", "Retrouver 5 livres de la bibliothèque.", ("item", "journal_page", 1)),
        ("hour_seller", "karma", ("choice", "", 5), "The Hour Seller", "Le vendeur d'heures", "Give an Ephemeral its time back (+5) or buy it (-5).", "Rendre son temps à un Éphémère (+5) ou le lui acheter (-5).", ("souls", "", 50)),
        ("out_of_season", "challenge", ("kill", "hour_keeper", 1), "Out of Season", "Hors saison", "Defeat an Hour Keeper.", "Battre un Gardien de l'heure.", ("title", "out_of_time", 1))],
    9: [("keep_footing", "guide", ("craft", "terrain_anchor", 1), "Keep Your Footing", "Garder pied", "Craft a Terrain Anchor.", "Fabriquer une Ancre de terrain.", ("item", "anchor", 16)),
        ("ground_plan", "guide", ("obtain", "terrain_fragment", 16), "The Ground Plan", "Le plan du sol", "Discover 5 zones.", "Découvrir 5 zones.", ("souls", "", 50)),
        ("drifting_fort", "npc", ("deliver", "anchor", 3), "The Drifting Fort", "Le fort dérive", "Stabilize 3 walls of the fort.", "Stabiliser 3 murs du fort.", ("item", "grip_boots", 1)),
        ("the_surveyor", "npc", ("kill", "foundation_eater", 5), "The Surveyor", "Le géomètre", "Measure a living chasm.", "Mesurer un gouffre vivant.", ("souls", "", 50)),
        ("the_vein", "karma", ("choice", "", 10), "The Vein", "La veine", "Heal the beating vein (+10) or drain it (-10).", "Soigner la veine battante (+10) ou la vider (-10).", ("souls", "", 80)),
        ("unanchored", "challenge", ("kill", "walking_column", 1), "Unanchored", "Sans ancre", "Defeat a Walking Column.", "Vaincre une Colonne marcheuse.", ("title", "untethered", 1))],
    10: [("looking_down", "guide", ("enter", "world_10", 1), "Looking Down", "Le regard d'en bas", "Find your base, now a mere object.", "Trouver sa base, devenue un simple objet.", ("souls", "", 50)),
         ("the_workshop", "guide", ("craft", "artisan_blade", 1), "The Workshop", "L'atelier", "Craft at the Final Loom.", "Fabriquer au Métier final.", ("item", "artisan_shard", 1)),
         ("the_apprentices", "npc", ("deliver", "artisan_thread", 16), "The Apprentices", "Les apprentis", "Find 5 old apprentices.", "Retrouver 5 anciens apprentis.", ("title", "apprentice", 1)),
         ("every_tool", "npc", ("kill", "colossus_prowler", 1), "Every Tool", "Tous les outils", "Use a tool from every world.", "Utiliser un outil de chaque monde.", ("item", "journal_page", 1)),
         ("last_pardon", "karma", ("choice", "", 10), "The Last Pardon", "Le dernier pardon", "Spare an apprentice (+10) or take their core (-10).", "Épargner un apprenti (+10) ou prendre son noyau (-10).", ("souls", "", 100)),
         ("all_at_once", "challenge", ("kill", "the_unfinished", 1), "All at Once", "Tout d'un coup", "Defeat the Unfinished without losing a layer.", "Vaincre l'Inachevée sans perdre de couche.", ("title", "seamless", 1))],
}
for w, lst in _Q.items():
    for (qid, t, obj, en, fr, den, dfr, rew) in lst:
        QUESTS.append((qid, w, t, obj, en, fr, den, dfr, rew))

# ---------------------------------------------------------------- achievements (100)
# type: progress | explore | combat | hidden; trigger: (kind, arg) evaluated by gen / java
ACH = {
    1: [("progress", "First Seed", "Première Graine", "Open World 1.", "Ouvrir le monde 1.", ("enter", 1)),
        ("progress", "Breathe Anyway", "Respirer malgré tout", "Craft a filter mask.", "Fabriquer un masque filtrant.", ("item", "filter_mask")),
        ("progress", "Fallen Queen", "Reine déchue", "Defeat the Spore Queen.", "Vaincre la Reine des spores.", ("kill", "spore_queen")),
        ("explore", "Living Frescoes", "Fresques vivantes", "Find a fresco of the world.", "Trouver une fresque du monde.", ("structure", "root_temple")),
        ("explore", "Botanist", "Botaniste", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 1)),
        ("explore", "Every Page", "Toutes les pages", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 1)),
        ("combat", "Broken Shield", "Bouclier brisé", "Defeat a Chitin Guard.", "Vaincre un Gardien de chitine.", ("kill", "chitin_guard")),
        ("combat", "Short of Breath", "Le souffle court", "Beat the Queen without a mask.", "Battre la Reine sans masque.", ("custom", "queen_no_mask")),
        ("hidden", "Friend of Flowers", "Ami des fleurs", "Get caught by a Snare Flower.", "Se faire attraper par une fleur-piège.", ("custom", "snared")),
        ("hidden", "First Doll", "Première poupée", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_1"))],
    2: [("progress", "Rising Heat", "Chaleur tournante", "Open World 2.", "Ouvrir le monde 2.", ("enter", 2)),
        ("progress", "The Right Fire", "Le bon feu", "Smelt an ash ingot.", "Fondre un lingot de cendre.", ("item", "ash_ingot")),
        ("progress", "Titan Snuffed", "Titan éteint", "Defeat the Ash Titan.", "Vaincre le Titan de cendre.", ("kill", "ash_titan")),
        ("explore", "Deep Miner", "Mineur de fond", "Mine a giant vein.", "Miner un filon géant.", ("item", "giant_ore")),
        ("explore", "Total Prospecting", "Prospection totale", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 2)),
        ("explore", "Site Notebooks", "Carnets de chantier", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 2)),
        ("combat", "No Cooling", "Sans refroidir", "Defeat a Slag Golem.", "Vaincre un Golem de scories.", ("kill", "slag_golem")),
        ("combat", "Molten Armor", "Armure fondue", "Beat the Titan without touching lava.", "Battre le Titan sans toucher la lave.", ("custom", "titan_no_lava")),
        ("hidden", "Too Greedy", "Trop gourmand", "Overheat a Foundry.", "Faire exploser une Fonderie par surchauffe.", ("custom", "foundry_boom")),
        ("hidden", "Ash Doll", "Poupée de cendre", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_2"))],
    3: [("progress", "Under Lock", "Sous les verrous", "Open World 3.", "Ouvrir le monde 3.", ("enter", 3)),
        ("progress", "The Right Key", "La bonne clé", "Open a first sealed door.", "Ouvrir une première zone.", ("custom", "door_opened")),
        ("progress", "Empty Cell", "Cellule vide", "Defeat the Grand Jailer.", "Vaincre le Grand Geôlier.", ("kill", "grand_jailer")),
        ("explore", "Full Plan", "Plan complet", "Craft a labyrinth map.", "Compléter une carte du labyrinthe.", ("item", "labyrinth_map")),
        ("explore", "Guided Tour", "Visite guidée", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 3)),
        ("explore", "Prison Register", "Registre d'écrou", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 3)),
        ("combat", "Trap Returned", "Piège retourné", "Trap a mob with a portable trap.", "Piéger un mob avec un piège portatif.", ("custom", "trapped")),
        ("combat", "Open Cell", "Cellule ouverte", "Defeat an Executioner.", "Battre un Bourreau.", ("kill", "executioner")),
        ("hidden", "It Won't Open", "Ça n'ouvre pas", "Try a key on a living lock.", "Essayer une clé sur une serrure vivante.", ("custom", "key_on_lock")),
        ("hidden", "Captive Doll", "Poupée captive", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_3"))],
    4: [("progress", "Open Sky", "Le ciel ouvert", "Open World 4.", "Ouvrir le monde 4.", ("enter", 4)),
        ("progress", "No Net", "Sans filet", "Craft a glider.", "Faire un premier vol en planeur.", ("item", "glider")),
        ("progress", "Fallen King", "Roi tombé", "Defeat the Storm King.", "Vaincre le Roi des tempêtes.", ("kill", "storm_king")),
        ("explore", "Wind Mapper", "Cartographe des vents", "Find the Storm Lighthouse.", "Découvrir le phare des tempêtes.", ("structure", "storm_lighthouse")),
        ("explore", "View from Above", "Vue d'en haut", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 4)),
        ("explore", "Flying Paper", "Papier volé", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 4)),
        ("combat", "Misplaced", "Mal placé", "Pull a mob into the void with the hook.", "Envoyer un mob dans le vide au grappin.", ("custom", "hook_void")),
        ("combat", "Under the Lightning", "Sous la foudre", "Beat the King without being struck.", "Battre le Roi sans être foudroyé.", ("custom", "king_no_bolt")),
        ("hidden", "One Way", "Aller simple", "Fall from the highest island.", "Tomber de l'île la plus haute.", ("custom", "high_fall")),
        ("hidden", "Cloud Doll", "Poupée de nuage", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_4"))],
    5: [("progress", "Pitch Darkness", "Le noir complet", "Open World 5.", "Ouvrir le monde 5.", ("enter", 5)),
        ("progress", "A Glimmer", "Une lueur", "Craft a Solar Lantern.", "Fabriquer une lanterne solaire.", ("item", "solar_lantern")),
        ("progress", "End of the Feast", "Fin du festin", "Defeat the Light Eater.", "Vaincre le Mangeur de lumière.", ("kill", "light_eater")),
        ("explore", "First Glint", "Première lueur", "Find a diamond fragment.", "Trouver un fragment de diamant.", ("item", "diamond_fragment")),
        ("explore", "Groping Around", "À tâtons", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 5)),
        ("explore", "Written in the Dark", "Écrit dans le noir", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 5)),
        ("combat", "Total Silence", "Silence total", "Kill a Blind Prowler without being spotted.", "Tuer un Rôdeur aveugle sans être repéré.", ("custom", "silent_kill")),
        ("combat", "Flameless", "Sans flamme", "Beat the Eater without artificial light.", "Battre le Mangeur sans lumière artificielle.", ("custom", "eater_no_light")),
        ("hidden", "It Was You", "C'était toi", "Get lured by an Echo.", "Être attiré par un Écho.", ("custom", "lured")),
        ("hidden", "Shadow Doll", "Poupée d'ombre", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_5"))],
    6: [("progress", "Upside Down", "L'envers", "Open World 6.", "Ouvrir le monde 6.", ("enter", 6)),
        ("progress", "Feet on the Ground", "Pieds sur terre", "Craft gravity boots.", "Fabriquer les bottes de gravité.", ("item", "gravity_boots")),
        ("progress", "Face to Face", "Face à toi", "Defeat Your Double.", "Vaincre Ton Double.", ("kill", "your_double")),
        ("explore", "Ceiling Walk", "Marcher au plafond", "Live through a gravity flip.", "Traverser une inversion de gravité.", ("custom", "flipped")),
        ("explore", "Impossible Geometry", "Géométrie impossible", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 6)),
        ("explore", "Reading Backwards", "Lire à l'envers", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 6)),
        ("combat", "Return to Sender", "Renvoi", "Kill a Reflection.", "Tuer un Reflet.", ("kill", "reflection")),
        ("combat", "No Copy", "Sans copie", "Beat the Double with different gear each phase.", "Battre le Double avec un équipement différent à chaque phase.", ("custom", "double_swap")),
        ("hidden", "Vertigo", "Vertige", "Fall upward for 10 seconds.", "Tomber vers le haut pendant 10 secondes.", ("custom", "fall_up")),
        ("hidden", "Flipped Doll", "Poupée retournée", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_6"))],
    7: [("progress", "Great Depth", "Grande profondeur", "Open World 7.", "Ouvrir le monde 7.", ("enter", 7)),
        ("progress", "Pressurized", "Sous pression", "Breathe through a snorkel helmet.", "Respirer par un casque-tuba.", ("custom", "snorkel")),
        ("progress", "Silence of the Trenches", "Le silence des fosses", "Defeat the Leviathan.", "Vaincre le Léviathan.", ("kill", "pressure_leviathan")),
        ("explore", "Extreme Dive", "Plongée extrême", "Reach the deepest trench.", "Atteindre la fosse la plus profonde.", ("custom", "deep_dive")),
        ("explore", "Open Sea", "Grand large", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 7)),
        ("explore", "Wet Paper", "Papier mouillé", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 7)),
        ("combat", "School Scattered", "Banc dispersé", "Kill 5 Blade Schools.", "Éliminer un banc de lames entier.", ("kill", "blade_school")),
        ("combat", "Last Breath", "Dernier souffle", "Beat the Leviathan with under 5% oxygen left in your helmet or your lungs.", "Battre le Léviathan avec moins de 5 % d'oxygène dans ton casque ou tes poumons.", ("custom", "levi_low_o2")),
        ("hidden", "Forgotten Plate", "Plaque oubliée", "Search a sunken wreck.", "Fouiller une épave engloutie.", ("structure", "wreck")),
        ("hidden", "Drowned Doll", "Poupée noyée", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_7"))],
    8: [("progress", "Counted Time", "Temps compté", "Open World 8.", "Ouvrir le monde 8.", ("enter", 8)),
        ("progress", "Suspended Instant", "Instant suspendu", "Use an hourglass.", "Utiliser un sablier.", ("custom", "hourglass")),
        ("progress", "End of Season", "Fin de saison", "Defeat the Master of Seasons.", "Vaincre le Maître des saisons.", ("kill", "seasons_master")),
        ("explore", "Every Season", "Toutes les saisons", "See the 4 seasons.", "Voir les 4 saisons.", ("custom", "four_seasons")),
        ("explore", "Lost Hours", "Heures perdues", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 8)),
        ("explore", "Old Papers", "Vieux papiers", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 8)),
        ("combat", "Right on Time", "Pile à l'heure", "Defeat an Hour Keeper.", "Vaincre un Gardien de l'heure.", ("kill", "hour_keeper")),
        ("combat", "Four Times Victor", "Quatre fois vainqueur", "Hit the Master in every season.", "Battre le Maître en le frappant à chaque saison.", ("custom", "master_four")),
        ("hidden", "Grandpa", "Grand-père", "Watch a Child of Minutes grow old.", "Voir un Enfant des minutes vieillir complètement.", ("custom", "child_old")),
        ("hidden", "Faded Doll", "Poupée fanée", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_8"))],
    9: [("progress", "Slippery Ground", "Terrain glissant", "Open World 9.", "Ouvrir le monde 9.", ("enter", 9)),
        ("progress", "Fixed Point", "Point fixe", "Craft a Terrain Anchor.", "Fabriquer une Ancre de terrain.", ("item", "terrain_anchor")),
        ("progress", "That Traveler Was You", "Ce voyageur, c'était toi", "Defeat the Heart of the Terrain.", "Vaincre le Cœur du terrain.", ("kill", "terrain_heart_boss")),
        ("explore", "Surveyor", "Géomètre", "Find a living chasm.", "Découvrir un gouffre vivant.", ("structure", "living_chasm")),
        ("explore", "Unstable Ground", "Sol instable", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 9)),
        ("explore", "Displaced Page", "Page déplacée", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 9)),
        ("combat", "Mimic Unmasked", "Mimique démasquée", "Kill a Mimic.", "Repérer et tuer une mimique.", ("kill", "mimic")),
        ("combat", "Anchorless", "Sans ancre", "Beat the Heart without placing an anchor.", "Battre le Cœur sans poser d'ancre.", ("custom", "heart_no_anchor")),
        ("hidden", "My Base Walks", "Ma base marche", "See a building moved by the ground.", "Voir une construction déplacée par le terrain.", ("custom", "base_moved")),
        ("hidden", "Moving Doll", "Poupée mouvante", "Find the hidden doll of the world.", "Trouver la poupée cachée du monde.", ("item", "hidden_doll_9"))],
    10: [("progress", "All the Way Up", "Tout en haut", "Open World 10.", "Ouvrir le monde 10.", ("enter", 10)),
         ("progress", "Final Loom", "Métier final", "Craft an item at the Final Loom.", "Fabriquer un objet au Métier final.", ("item", "artisan_blade")),
         ("progress", "Last Thread", "Dernier fil", "Defeat the Unfinished.", "Vaincre l'Inachevée.", ("kill", "the_unfinished")),
         ("explore", "A Crumb", "Une miette", "Climb onto the Titanic Workbench.", "Grimper sur l'Établi titanesque.", ("structure", "titanic_workbench")),
         ("explore", "Full Workshop", "Atelier complet", "Visit the 10 structure types.", "Visiter les 10 types de structures.", ("structures", 10)),
         ("explore", "Last Letter", "Dernière lettre", "Find the 5 Journal pages.", "Trouver les 5 pages du Journal.", ("pages", 10)),
         ("combat", "Ten Shells", "Dix enveloppes", "Break the 10 shells in one attempt.", "Briser les 10 enveloppes en un seul essai.", ("custom", "ten_shells")),
         ("combat", "All the Way", "Tout le chemin", "Use gear from every world against the Unfinished.", "Utiliser un équipement de chaque monde contre l'Inachevée.", ("custom", "all_gear")),
         ("hidden", "Every Doll", "Toutes les poupées", "Gather the 10 hidden dolls.", "Réunir les 10 poupées cachées.", ("custom", "all_dolls")),
         ("hidden", "Set Down the Tools", "Poser les outils", "Defeat the Unfinished with the 10 hidden dolls on you.", "Vaincre l'Inachevée avec les 10 poupées cachées sur soi.", ("custom", "third_end"))],
}

# ---------------------------------------------------------------- classes
CLASSES = [
    ("guardian", "Guardian", "Gardien", "armor", "Armor, knockback resistance", "Armure, résistance au recul"),
    ("berserker", "Berserker", "Berserker", "weapon_armor", "Damage, attack speed", "Dégâts, vitesse d'attaque"),
    ("prowler", "Prowler", "Rôdeur", "armor_weapon", "Movement speed, dodge", "Vitesse de déplacement, esquive"),
    ("reaper", "Reaper", "Moissonneur", "weapon_armor", "Life steal, soul gain", "Vol de vie, gain d'âme"),
    ("survivor", "Survivor", "Survivant", "weapon_armor", "World effect resistance, recovery", "Résistance aux effets des mondes, récupération"),
    ("prospector", "Prospector", "Prospecteur", "tool", "Mining speed, ore luck", "Vitesse de minage, chance de minerai"),
]
