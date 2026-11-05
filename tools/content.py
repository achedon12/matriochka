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
item("shell_shard", "Shell Shard", "Éclat d'enveloppe", 0, "resource", "epic", "shard",
     "Left by a fallen boss. Every class upgrade needs some.", "Laissé par un boss vaincu. Chaque amélioration de classe en demande.")
item("mutated_scale", "Mutated Scale", "Écaille mutée", 0, "gem", "epic", "gem",
     "Shed by a mutated boss. Rich in soul.", "Perdue par un boss muté. Riche en âme.", pal=("6a2a8a", "c84ad8", "f0c050", "1a0a24"))
item("doll_mallet", "Doll Mallet", "Maillet de poupée", 0, "tool", "rare", "hammer",
     "Strike a World Block of your group with it: the world inside quakes and loose blocks fall on those in it. Sneak and use the block with empty hands to help them instead.",
     "Frappe un bloc-monde de ton groupe avec : le monde à l'intérieur tremble et des blocs se détachent sur ceux qui s'y trouvent. Accroupis-toi et utilise le bloc à mains nues pour plutôt les aider.",
     pal=("8a5a3a", "c8342a", "e8c050", "3a2416"))
# Souls kept in structure chests (the design budgets about 100 souls per world from them): use one to free its
# souls, sneak to free the whole stack. Neutral souls: they do not move karma. Values in item/SoulVessels.java.
item("soul_shard", "Soul Shard", "Éclat d'âme", 0, "soul", "common", "shard",
     "Holds 5 souls. Use it to free them (sneak: the whole stack).", "Contient 5 âmes. Utilise-le pour les libérer (accroupi : toute la pile).",
     pal=("4a8ad8", "9ad0ff", "e8f6ff", "142a4a"))
item("soul_vessel", "Soul Vessel", "Fiole d'âme", 0, "soul", "rare", "potion",
     "Holds 20 souls. Use it to free them (sneak: the whole stack).", "Contient 20 âmes. Utilise-la pour les libérer (accroupi : toute la pile).",
     pal=("4a8ad8", "9ad0ff", "7ac8ff", "142a4a"))

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
item("refuge_doll", "Refuge Doll", "Poupée-refuge", 3, "doll", "legendary", "doll",
     "A pocket base for your group. Use it to enter, use it again to leave.",
     "Une base de poche pour ton groupe. Utilise-la pour entrer, puis de nouveau pour sortir.")
# World 4
item("ray_membrane", "Ray Membrane", "Membrane de raie", 4, "resource", "common", "membrane", "Glider cloth.", "Toile du planeur.")
item("storm_essence", "Storm Essence", "Essence de tempête", 4, "resource", "rare", "orb", "Energy of the Lightning Forge.", "Énergie de la Forge à foudre.")
item("celestial_crystal", "Celestial Crystal", "Cristal céleste", 4, "gem", "rare", "crystal", "Gear and World 5 Seed.", "Équipement et Graine du monde 5.")
item("glider", "Glider", "Planeur", 4, "glider", "epic", "glider", "Glide between islands.", "Plane entre les îles.")
item("grappling_hook", "Grappling Hook", "Grappin", 4, "hook", "rare", "hook", "Pulls you toward a surface.", "Te tire vers une surface.")
item("lightning_lance", "Lightning Lance", "Lance de foudre", 4, "weapon", "rare", "spear")
item("celestial", "", "", 4, "armorset", "rare", "armor", set_en="Celestial", set_fr="céleste")
item("armor_layer", "Lacquer Layer", "Couche laquée", 4, "layer", "rare", "plate",
     "Laid on armor at the Class Table. When the outer layer breaks, the next takes over.",
     "Se pose sur une armure à la Table de classe. Quand la couche extérieure casse, la suivante prend le relais.")
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

# Hidden dolls. They nest in the order the Artisan carved them, which is not the order the worlds open in:
# NEST_ORDER lists the worlds of the dolls from the smallest (innermost) to the largest (outermost). Three hints
# point to it: the notches under each doll (its rank), the coded page 4 of each world (which doll holds it) and
# the people of each world (which doll it holds), see DOLL_LINES.
NEST_ORDER = [6, 3, 9, 1, 5, 8, 2, 10, 4, 7]
_NOTCH_EN = ["One notch is", "Two notches are", "Three notches are", "Four notches are", "Five notches are",
             "Six notches are", "Seven notches are", "Eight notches are", "Nine notches are", "Ten notches are"]
_NOTCH_FR = ["Une encoche est gravée", "Deux encoches sont gravées", "Trois encoches sont gravées", "Quatre encoches sont gravées",
             "Cinq encoches sont gravées", "Six encoches sont gravées", "Sept encoches sont gravées", "Huit encoches sont gravées",
             "Neuf encoches sont gravées", "Dix encoches sont gravées"]
for w in range(1, 11):
    rank = NEST_ORDER.index(w)
    item(f"hidden_doll_{w}", f"Hidden Doll {w}", f"Poupée cachée {w}", w, "secret", "none", "doll_small",
         f"{_NOTCH_EN[rank]} carved under its base. Nest the ten dolls in order...",
         f"{_NOTCH_FR[rank]} sous sa base. Emboîte les dix poupées dans l'ordre...")
item("nested_dolls", "Nested Dolls", "Poupées emboîtées", 0, "secret", "none", "doll_small",
     "Hold it in your main hand and the next hidden doll in the other, then use it.",
     "Tiens-la en main principale et la poupée cachée suivante dans l'autre main, puis utilise-la.")
item("whole_matryoshka", "The Whole Matryoshka", "La Matriochka entière", 0, "secret", "legendary", "doll",
     "Ten dolls, one inside the other. Open it once the Unfinished has fallen: World 0 sleeps inside.",
     "Dix poupées, l'une dans l'autre. Ouvre-la une fois l'Inachevée tombée : le monde 0 dort dedans.")
item("blank_scroll", "Blank Scroll", "Parchemin blanc", 0, "secret", "none", "scroll",
     "Nothing is written on it. Nothing is left to finish.", "Rien n'y est écrit. Il ne reste rien à finir.")

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
block("nesting_chest", "Nesting Chest", "Coffre gigogne", 2, "nesting_chest", "wood",
      note_en="Holds the smaller nesting chests. Sneak and use it to set what it sorts.",
      note_fr="Contient les coffres gigognes plus petits. Accroupis-toi et utilise-le pour choisir ce qu'il trie.")
block("nesting_chest_medium", "Middle Nesting Chest", "Coffre gigogne moyen", 2, "nesting_chest", "wood", inset=2,
      note_en="Two rows. Fits in a Nesting Chest, holds a Little one.", note_fr="Deux rangées. Tient dans un Coffre gigogne, contient un petit.")
block("nesting_chest_little", "Little Nesting Chest", "Petit coffre gigogne", 2, "nesting_chest", "wood", inset=4,
      note_en="One row. Fits in the larger nesting chests.", note_fr="Une rangée. Tient dans les coffres gigognes plus grands.")
block("sanctuary_altar", "Guardian's Altar", "Autel du Gardien", 0, "boss_altar", "stone_rune", boss="block_guardian")
block("arena_altar", "Arena Altar", "Autel d'arène", 0, "boss_altar", "stone_rune")
block("lair_heart", "Lair Heart", "Cœur d'antre", 0, "lair_heart", "lair_heart",
      note_en="Wakes the boss of its lair when someone comes close.", note_fr="Réveille le boss de son antre quand on s'approche.")
block("sealed_door", "Sealed Door", "Porte scellée", 3, "sealed_door", "brick")
block("painted_wood", "Painted Wood", "Bois peint", 0, "deco", "wood")
block("lacquer_block", "Lacquer Block", "Bloc laqué", 0, "deco", "lacquer")
block("spent_glow", "Spent Glow", "Lueur éteinte", 5, "deco", "stone",
      note_en="What a glowing block becomes once the Lightless Deep has drunk its light.",
      note_fr="Ce que devient un bloc lumineux une fois que la Profondeur sans lumière a bu sa lumière.")

# stations
STATIONS = [
    ("matrix_workbench", "Matrix Workbench", "Établi matriciel", 0, "Crafts Seeds; recipes unlock with cores.", "Fabrique les Graines ; recettes débloquées par les noyaux."),
    ("class_table", "Class Table", "Table de classe", 0, "Upgrades an item's class.", "Améliore la classe d'un objet."),
    ("soul_altar", "Soul Altar", "Autel des âmes", 0, "Purify or devour an item. Rebuilds a Doll of Life layer for 50 souls and 4 rare resources of the current world.",
     "Purifie ou dévore un objet. Refait une couche de Poupée de vie pour 50 âmes et 4 ressources rares du monde en cours."),
    ("spore_vat", "Spore Vat", "Cuve de spores", 1, "Ripe brews (1 min) give more, aged ones (5 min) twice as much.", "Une cuvée mûre (1 min) donne plus, vieillie (5 min) deux fois plus."),
    ("ash_foundry", "Ash Foundry", "Fonderie de cendre", 2, "Keep the temperature in the green.", "Garde la température dans le vert."),
    ("jailer_table", "Jailer's Table", "Table du Geôlier", 3, "Reproduce the lock pattern.", "Reproduis le motif de la serrure."),
    ("lightning_forge", "Lightning Forge", "Forge à foudre", 4, "Needs a lightning strike or storm essence.", "Demande un éclair ou de l'essence de tempête."),
    ("dark_altar", "Dark Altar", "Autel obscur", 5, "Works only in complete darkness.", "Fonctionne seulement dans le noir complet."),
    ("inverter", "Inverter", "Inverseur", 6, "Swaps the properties of two items. Every gain comes with a flaw.", "Échange les propriétés de deux objets. Chaque gain s'accompagne d'un défaut."),
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

# ---------------------------------------------------------------- World 10 at doll scale
# The Giant Workshop is the Artisan's workshop seen by a doll: giant sewing and carpentry things lie on its felt
# floor. They are scenery only (no chest, no page), so they stay out of STRUCTURES and of the "visit 10 structures"
# achievements. Builders live in structure/Workshop.java. (id, en, fr, archetype, spacing, separation in chunks)
WORKSHOP_PROPS = [
    ("giant_spool", "Giant Spool", "Bobine géante", "prop_spool", 11, 4),
    ("giant_nail", "Giant Nail", "Clou géant", "prop_nail", 8, 3),
    ("giant_pin", "Giant Pin", "Épingle géante", "prop_pin", 9, 3),
    ("giant_button", "Giant Button", "Bouton géant", "prop_button", 12, 5),
    ("giant_thimble", "Giant Thimble", "Dé à coudre géant", "prop_thimble", 16, 6),
    ("wood_offcuts", "Wood Offcuts", "Chutes de bois", "prop_offcut", 7, 2),
    ("giant_scissors", "Giant Scissors", "Ciseaux géants", "prop_scissors", 18, 7),
    ("giant_pencil", "Giant Pencil", "Crayon géant", "prop_pencil", 14, 5),
]

# ---------------------------------------------------------------- world variants
# A Seed hatches into a variant of its world, chosen while it hatches (world/Variants.java). Feeding the planted Seed
# (use an item on it) and what lies around it lean it calm or wild; the planter's karma at +100 or -100 overrides
# both. A variant never changes the terrain: it changes the creatures (how many come, their health and damage), the
# strength of the world's rule and the drops. Stored per group and world.
# (id, rule strength, danger, extra drop chance, spawn rate, en, fr, description en, description fr)
VARIANT_KINDS = [
    ("plain", 1.0, 1.0, 0.0, 1.0, "Plain", "Ordinaire",
     "The world as the Artisan made it.", "Le monde tel que l'artisan l'a fait."),
    ("calm", 0.75, 0.85, 0.0, 0.7, "Calm", "Apaisée",
     "Fewer and weaker creatures, a gentler rule, plainer loot.", "Moins de créatures, plus faibles, une règle plus douce, un butin ordinaire."),
    ("wild", 1.25, 1.25, 0.5, 1.5, "Wild", "Sauvage",
     "More and stronger creatures, a harsher rule, richer drops.", "Plus de créatures, plus fortes, une règle plus rude, un butin plus riche."),
    ("blessed", 0.8, 1.0, 0.35, 0.85, "Hallowed", "Bénie",
     "Karma +100: a kinder rule and richer drops; its boss shines.", "Karma +100 : une règle plus clémente, un butin plus riche ; son boss rayonne."),
    ("cursed", 1.3, 1.4, 1.0, 1.6, "Cursed", "Maudite",
     "Karma -100: a crushing rule, swarms of strong creatures and the richest drops.", "Karma -100 : une règle écrasante, des nuées de créatures fortes et le meilleur butin."),
]
# What each world calls its calm and wild variants: ((calm en, calm fr), (wild en, wild fr))
VARIANT_NAMES = {
    1: (("Withered Jungle", "Jungle flétrie"), ("Overgrown Jungle", "Jungle débordante")),
    2: (("Cooling Veins", "Filons refroidis"), ("Erupting Veins", "Filons en éruption")),
    3: (("Drowsy Dungeon", "Donjon assoupi"), ("Grinding Dungeon", "Donjon grinçant")),
    4: (("Becalmed Archipelago", "Archipel apaisé"), ("Thundering Archipelago", "Archipel tonnant")),
    5: (("Glimmering Deep", "Profondeur scintillante"), ("Starving Deep", "Profondeur affamée")),
    6: (("Steady Realm", "Royaume stable"), ("Spinning Realm", "Royaume tournoyant")),
    7: (("Slack-Tide Ocean", "Océan étale"), ("Crushing Ocean", "Océan écrasant")),
    8: (("Lingering Seasons", "Saisons lentes"), ("Racing Seasons", "Saisons folles")),
    9: (("Dozing Ground", "Terre assoupie"), ("Heaving Ground", "Terre soulevée")),
    10: (("Tidy Workshop", "Atelier rangé"), ("Cluttered Workshop", "Atelier encombré")),
}
# What leans a hatching Seed: items fed to it, and blocks within 3 blocks of it ("#" = a tag).
VARIANT_FEED = {
    "calm": ["#minecraft:flowers", "minecraft:honey_bottle", "minecraft:sweet_berries", "minecraft:glow_berries", "minecraft:moss_block"],
    "wild": ["minecraft:gunpowder", "minecraft:blaze_powder", "minecraft:rotten_flesh", "minecraft:bone", "minecraft:spider_eye", "minecraft:magma_cream"],
}
VARIANT_GROUND = {
    "calm": ["#minecraft:flowers", "#minecraft:leaves", "minecraft:moss_block", "minecraft:water"],
    "wild": ["minecraft:fire", "minecraft:soul_fire", "minecraft:soul_sand", "minecraft:soul_soil", "minecraft:wither_rose", "minecraft:lava"],
}
# Points needed (fed + ground, wild minus calm) to lean a Seed one way.
VARIANT_LEAN = 2

# ---------------------------------------------------------------- boss mutations
# From World 6 on, a boss whose world hatched wild, hallowed or cursed wakes mutated: one more attack, an element
# or a phase change on top of its fight (entity/Mutations.java). Its name in the boss bar says so, and it sheds a
# Mutated Scale and more Shell Shards.
MUTATION_FROM = 6
MUTATIONS = [
    ("searing", "Searing Mutation", "Mutation ardente",
     "Its blows set you on fire; a ring of flames follows every big attack.", "Ses coups t'enflamment ; un cercle de flammes suit chaque grande attaque."),
    ("frenzied", "Frenzied Mutation", "Mutation frénétique",
     "Below half health it heals a little, then speeds up and attacks faster.", "Sous la moitié de sa vie, il se soigne un peu, puis accélère et attaque plus vite."),
    ("echoing", "Echoing Mutation", "Mutation en écho",
     "Every big attack is followed by an echo: a second shockwave.", "Chaque grande attaque est suivie d'un écho : une seconde onde de choc."),
    ("radiant", "Radiant Mutation", "Mutation radieuse",
     "A pulse of light every 15 seconds blinds and slows those near it.", "Toutes les 15 secondes, une impulsion de lumière aveugle et ralentit ceux qui l'entourent."),
    ("hollow", "Hollow Mutation", "Mutation creuse",
     "Every 20 seconds it calls creatures of its world out of its shell.", "Toutes les 20 secondes, il fait sortir de sa coquille des créatures de son monde."),
]
# The mutation of a wild world's boss; the hallowed variant gives "radiant", the cursed one "hollow".
WILD_MUTATION = {6: "echoing", 7: "frenzied", 8: "searing", 9: "echoing", 10: "frenzied"}

# ---------------------------------------------------------------- quests (64, plus the karma paths)
# type: guide | npc | karma | challenge | help | pact ; obj: (kind, target, count)
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

# Karma paths: a chapter of its own (world 11 in the table). Mutual-help quests open at karma +50, pact quests at -50;
# each one completed moves the karma a little further along its path.
KARMA_CHAPTER = 11
_KARMA_PATHS = [
    ("light_for_others", "help", ("purify", "souls", 100), "A Light for Others", "Une lumière pour les autres", "Free 100 souls at the Soul Altar.", "Libérer 100 âmes à l'Autel des âmes.", ("item", "chance_doll", 1)),
    ("many_hands", "help", ("trade", "any", 10), "Many Hands", "Mille mains", "Trade 10 times with the peoples of the worlds.", "Commercer 10 fois avec les peuples des mondes.", ("souls", "", 40)),
    ("warm_hearth", "help", ("deliver", "wool_thread", 16), "A Warm Hearth", "Un foyer chaud", "Gather 16 wool threads for the cradles of the lost.", "Réunir 16 fils de laine pour les berceaux des égarés.", ("item", "soul_cradle", 1)),
    ("hunger", "pact", ("devour", "souls", 100), "Hunger", "La faim", "Absorb 100 souls at the Soul Altar.", "Absorber 100 âmes à l'Autel des âmes.", ("souls", "", 60)),
    ("price_of_silence", "pact", ("contraband", "any", 3), "The Price of Silence", "Le prix du silence", "Buy 3 goods on a black market.", "Acheter 3 marchandises au marché clandestin.", ("item", "shell_shard", 2)),
    ("no_witnesses", "pact", ("kill", "innocent", 3), "No Witnesses", "Pas de témoins", "Silence 3 innocents, on the Surface or in the worlds.", "Faire taire 3 innocents, sur la Surface ou dans les mondes.", ("item", "diamond_fragment", 2)),
]
for (qid, t, obj, en, fr, den, dfr, rew) in _KARMA_PATHS:
    QUESTS.append((qid, KARMA_CHAPTER, t, obj, en, fr, den, dfr, rew))

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
         ("hidden", "Set Down the Tools", "Poser les outils", "Leave the work unfinished in World 0.", "Laisser l'œuvre inachevée dans le monde 0.", ("custom", "third_end"))],
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

# ---------------------------------------------------------------- the Artisan's Journal (50 pages)
# Five pages per world, as in design/lore.txt: 1 site note (why the world exists), 2 portrait of the apprentice who
# became its boss, 3 observation (a survival or combat tip), 4 coded page (a piece of the way to World 0, written
# in the Artisan's cipher), 5 letter to the traveller (the world's revelation). The coded page is shown enciphered
# until the player carries the world's core or the group has beaten its boss.
# Each entry: (title_en, body_en, title_fr, body_fr).
JOURNAL_CODED = 3
JOURNAL = {
    1: [
        ("Site note: the green prison",
         "The first prison had to be alive. A forest that grows faster than anything can eat it, and air thick enough to choke a hunger. I planted it, then I planted the people who would tend it without ever knowing why.",
         "Note de chantier : la prison verte",
         "La première prison devait être vivante. Une forêt qui pousse plus vite que tout ce qui la dévore, un air assez épais pour étouffer une faim. Je l'ai plantée, puis j'y ai planté ceux qui l'entretiendraient sans jamais savoir pourquoi."),
        ("Portrait: my gardener",
         "She grafted roses onto oaks to make me laugh. When I asked one apprentice to stay with the forest forever, she said yes before I finished. The spores took her slowly. She still hums when the cocoons split.",
         "Portrait : ma jardinière",
         "Elle greffait des roses sur des chênes pour me faire rire. Quand j'ai demandé à un apprenti de rester pour toujours avec la forêt, elle a dit oui avant que j'aie fini. Les spores l'ont prise lentement. Elle fredonne encore quand les cocons se fendent."),
        ("Observation: breathe",
         "Rain and water wash the toxin out of you. A filter mask halves what you breathe in, and root broth slows it more. Never fight the Queen in still air: the clouds she sows linger where no wind moves them.",
         "Observation : respirer",
         "La pluie et l'eau te lavent de la toxine. Un masque filtrant divise par deux ce que tu respires, la bouillie de racines la ralentit encore. Ne combats jamais la Reine dans l'air immobile : ses nuages restent là où aucun vent ne les chasse."),
        ("Cipher, first leaf",
         "There is an eleventh doll, smaller than all the others. To reach it, close the ten hidden dolls one inside the next. The doll of this forest sleeps inside the doll of the Lightless Deep.",
         "Chiffre, premier feuillet",
         "Il existe une onzième poupée, plus petite que toutes les autres. Pour l'atteindre, referme les dix poupées cachées l'une dans l'autre. La poupée de cette forêt dort dans celle de la Profondeur sans lumière."),
        ("To whoever opens this",
         "If you are reading this, you came through a block of earth. Nothing here grew by itself: not the trees, not the sky, not the ground under your feet. These worlds were made, by a hand, one by one. Mine.",
         "À qui ouvrira ceci",
         "Si tu lis ceci, tu es passé par un bloc de terre. Rien ici n'a poussé seul : ni les arbres, ni le ciel, ni le sol sous tes pieds. Ces mondes ont été fabriqués, à la main, un par un. La mienne."),
    ],
    2: [
        ("Site note: the forge below",
         "Every prison needs heat to keep its seams shut. I dug a forge so deep that its fire runs through the walls of all the others. The veins you mine are the rivets of the whole work.",
         "Note de chantier : la forge d'en bas",
         "Chaque prison a besoin de chaleur pour garder ses coutures fermées. J'ai creusé une forge si profonde que son feu court dans les murs de toutes les autres. Les filons que tu mines sont les rivets de l'œuvre entière."),
        ("Portrait: my master smith",
         "He never let me hold the hammer. He said the Artisan should draw and the smith should strike. He took the furnace as his post and his skin turned to ash around a heart that never cools.",
         "Portrait : mon maître forgeron",
         "Il ne m'a jamais laissé tenir le marteau. Il disait que l'Artisan dessine et que le forgeron frappe. Il a pris la fournaise pour poste, et sa peau est devenue cendre autour d'un cœur qui ne refroidit jamais."),
        ("Observation: keep cool",
         "Heat climbs with depth and near lava, and falls when you rise into the open. Cooling water halves it at once. When the Titan's armor melts, his heart is bare: that is the moment, not before.",
         "Observation : garder la tête froide",
         "La chaleur monte avec la profondeur et près de la lave, et redescend quand tu remontes à l'air libre. L'eau de refroidissement la divise aussitôt par deux. Quand l'armure du Titan fond, son cœur est nu : c'est le moment, pas avant."),
        ("Cipher, second leaf",
         "Hold the smallest doll in your hand and the next one in your other hand, then press them together. The doll of the forge sleeps inside the doll of the Giant Workshop.",
         "Chiffre, deuxième feuillet",
         "Tiens la plus petite poupée dans ta main et la suivante dans l'autre main, puis presse-les l'une contre l'autre. La poupée de la forge dort dans celle de l'Atelier géant."),
        ("To the traveller, again",
         "You will have noticed: every world is shut like a box. A forest around something. A forge around something. Each of them locks something away. I will not write its name yet. Names wake things.",
         "Au voyageur, encore",
         "Tu l'auras remarqué : chaque monde est fermé comme une boîte. Une forêt autour de quelque chose. Une forge autour de quelque chose. Chacun enferme quelque chose. Je n'écrirai pas encore son nom. Les noms réveillent les choses."),
    ],
    3: [
        ("Site note: the locks",
         "No sky, no surface, only keys. A prison made of nothing but doors, so that whatever walks it never finds the same corridor twice. The halls move on their own; I built them restless on purpose.",
         "Note de chantier : les verrous",
         "Ni ciel ni surface, seulement des clés. Une prison faite de portes et rien d'autre, pour que ce qui l'arpente ne retrouve jamais deux fois le même couloir. Les salles bougent seules ; je les ai voulues inquiètes."),
        ("Portrait: the one who guards",
         "My most careful apprentice counted every key twice. I gave him the locks and asked him to guard what slept behind them. Centuries later, he still guards. He no longer remembers what. He only remembers to stay.",
         "Portrait : celui qui garde",
         "Mon apprenti le plus soigneux comptait chaque clé deux fois. Je lui ai confié les verrous et demandé de garder ce qui dormait derrière. Des siècles plus tard, il garde encore. Il ne se souvient plus de quoi. Il se souvient seulement de rester."),
        ("Observation: doors and chains",
         "A sealed door opens once to a dungeon key. A lockpick opens ordinary locks, never the living ones: those bite. When the Jailer turns his arena into a cell, break out before the walls close in.",
         "Observation : portes et chaînes",
         "Une porte scellée s'ouvre une fois avec une clé de donjon. Le kit de crochetage ouvre les serrures ordinaires, jamais les vivantes : celles-là mordent. Quand le Geôlier change son arène en cellule, sors avant que les murs se referment."),
        ("Cipher, third leaf",
         "A doll that does not belong will rattle and refuse to close. Start again from the smallest. The doll of the locks sleeps inside the doll of the Restless Ground.",
         "Chiffre, troisième feuillet",
         "Une poupée qui n'est pas à sa place cliquette et refuse de se fermer. Recommence depuis la plus petite. La poupée des verrous dort dans celle de la Terre agitée."),
        ("Plans, for you",
         "I leave my plans in every cell, folded small. You will find my workshops hidden in the worlds, my tools still on the benches. An old artisan lived here before you. Read his plans. They are meant for you.",
         "Des plans, pour toi",
         "Je laisse mes plans dans chaque cellule, pliés petit. Tu trouveras mes ateliers cachés dans les mondes, mes outils encore sur les établis. Un vieil artisan a vécu ici avant toi. Lis ses plans. Ils te sont destinés."),
    ],
    4: [
        ("Site note: nothing settles",
         "Here I made a wind that never stops, so that nothing could rest, nothing could take root, nothing could gather strength. The islands drift because what I lock cannot stand still without growing.",
         "Note de chantier : rien ne se pose",
         "Ici j'ai fait un vent qui ne s'arrête jamais, pour que rien ne se repose, rien ne prenne racine, rien ne reprenne des forces. Les îles dérivent parce que ce que j'enferme ne peut pas rester immobile sans grandir."),
        ("Portrait: my messenger",
         "He ran between the worlds with my letters before the doors were sealed. When the last door closed, he stayed on the wind, crowned by the storm. He still carries a letter he can no longer deliver.",
         "Portrait : mon messager",
         "Il courait entre les mondes avec mes lettres avant qu'on scelle les portes. Quand la dernière porte s'est fermée, il est resté sur le vent, couronné par l'orage. Il porte encore une lettre qu'il ne peut plus remettre."),
        ("Observation: crouch",
         "When a gust is coming, crouch or put a wall at your back. Lightning gathers where you stand in the open: move when the air crackles. A glider forgives a fall, a grappling hook forgives a mistake.",
         "Observation : s'accroupir",
         "Quand une rafale arrive, accroupis-toi ou mets un mur dans ton dos. La foudre se concentre là où tu restes à découvert : bouge quand l'air crépite. Le planeur pardonne une chute, le grappin pardonne une erreur."),
        ("Cipher, fourth leaf",
         "The ten dolls closed together become one, and that one will open onto the eleventh. The doll of the storms sleeps inside the doll of the Pressure Ocean.",
         "Chiffre, quatrième feuillet",
         "Les dix poupées refermées ensemble n'en font plus qu'une, et celle-là s'ouvrira sur la onzième. La poupée des tempêtes dort dans celle de l'Océan sous pression."),
        ("Stop",
         "Stop here. Please. I tried to stop the work myself and I could not; I broke my tools and made new ones the next morning. If you keep opening these worlds, you finish what I could not bear to finish. Turn back.",
         "Arrête",
         "Arrête-toi ici. Je t'en prie. J'ai voulu arrêter l'œuvre moi-même et je n'ai pas pu ; j'ai brisé mes outils et j'en ai fait de neufs le lendemain. Si tu continues d'ouvrir ces mondes, tu achèves ce que je n'ai pas supporté d'achever. Fais demi-tour."),
    ],
    5: [
        ("Site note: no light",
         "It fed on light. So I made a prison where light does not last: lanterns starve, torches fail, and the only sense left is hearing. The Silent Ones learned to speak with their hands.",
         "Note de chantier : sans lumière",
         "Elle se nourrissait de lumière. Alors j'ai fait une prison où la lumière ne dure pas : les lanternes s'affament, les torches faiblissent, et il ne reste que l'ouïe. Les Silencieux ont appris à parler avec leurs mains."),
        ("Portrait: the one who swallowed",
         "She volunteered to eat every glow there was, so that nothing would be left for the creature. She is still hungry. She will always be hungry. That was the price, and she paid it smiling, in the dark.",
         "Portrait : celle qui a tout avalé",
         "Elle s'est proposée pour manger toutes les lueurs, pour qu'il n'en reste rien à la créature. Elle a encore faim. Elle aura toujours faim. C'était le prix, et elle l'a payé en souriant, dans le noir."),
        ("Observation: be quiet",
         "Every step makes noise; sneaking makes almost none. The prowlers hunt by sound, not by sight. A silence balm wipes your noise away. Against the Eater, listen: it charges where you were, not where you are.",
         "Observation : se taire",
         "Chaque pas fait du bruit ; s'accroupir n'en fait presque pas. Les rôdeurs chassent au son, pas à la vue. Un baume de silence efface ton bruit. Contre le Mangeur, écoute : il charge là où tu étais, pas là où tu es."),
        ("Cipher, fifth leaf",
         "Each hidden doll bears notches under its base. Count them: the fewer the notches, the deeper it sleeps. The doll of the dark sleeps inside the doll of the Hastened Seasons.",
         "Chiffre, cinquième feuillet",
         "Chaque poupée cachée porte des encoches sous sa base. Compte-les : moins il y a d'encoches, plus elle dort profond. La poupée du noir dort dans celle des Saisons accélérées."),
        ("Someone is watching",
         "You feel it too, now. In the dark, between two steps, something that is not a prowler is looking at you. It has been looking since the first world. It is patient. It is what all of this was built around.",
         "Quelqu'un regarde",
         "Tu le sens aussi, maintenant. Dans le noir, entre deux pas, quelque chose qui n'est pas un rôdeur te regarde. Il te regarde depuis le premier monde. Il est patient. C'est autour de lui que tout ceci a été construit."),
    ],
    6: [
        ("Site note: the mirror",
         "An inverted prison sends every gesture back. Strike, and you are struck. Push, and you are pushed. Whatever tries to break out of it only breaks itself. Up and down are a courtesy here, not a law.",
         "Note de chantier : le miroir",
         "Une prison inversée renvoie chaque geste. Frappe, et tu es frappé. Pousse, et tu es poussé. Ce qui tente d'en sortir ne brise que lui-même. Le haut et le bas sont une politesse ici, pas une loi."),
        ("Portrait: no apprentice",
         "No apprentice guards this world. I put my own reflection here, with my memories, all of them, so that I could forget. If you meet it, it will fight like you, because it is what you were before you forgot.",
         "Portrait : aucun apprenti",
         "Aucun apprenti ne garde ce monde. J'y ai mis mon propre reflet, avec mes souvenirs, tous, pour pouvoir oublier. Si tu le rencontres, il se battra comme toi, parce qu'il est ce que tu étais avant d'oublier."),
        ("Observation: which way is down",
         "Gravity flips without warning, but the air shivers just before. Gravity boots ignore the flips, a stabilizer cancels one. Your Double copies your weapon and your habits: change both between its phases.",
         "Observation : où est le bas",
         "La gravité s'inverse sans prévenir, mais l'air frémit juste avant. Les bottes de gravité ignorent les inversions, un stabilisateur en annule une. Ton Double copie ton arme et tes habitudes : change les deux entre ses phases."),
        ("Cipher, sixth leaf",
         "This is the smallest of the ten. Nothing sleeps inside it but what I chose to forget. Hold it first, in your main hand, and bring the doll of the Endless Dungeon to it.",
         "Chiffre, sixième feuillet",
         "C'est la plus petite des dix. Rien ne dort en elle, sauf ce que j'ai choisi d'oublier. Tiens-la en premier, dans ta main principale, et approche-lui la poupée du Donjon sans fin."),
        ("They are linked",
         "Look at the bosses side by side: the gardener, the smith, the jailer, the messenger, the hungry one, the reflection. One hand made them, one thread binds them. Break one, and all the others feel it.",
         "Ils sont liés",
         "Regarde les boss côte à côte : la jardinière, le forgeron, le geôlier, le messager, l'affamée, le reflet. Une seule main les a faits, un seul fil les relie. Brise-en un, et tous les autres le sentent."),
    ],
    7: [
        ("Site note: the weight of the sea",
         "Pressure crushes what tries to grow. I drowned this world under so much water that nothing swells, nothing rises, nothing spreads. The deeper you go, the closer you come to what it presses down on.",
         "Note de chantier : le poids de la mer",
         "La pression écrase ce qui cherche à grandir. J'ai noyé ce monde sous tant d'eau que rien n'enfle, rien ne monte, rien ne s'étend. Plus tu descends, plus tu approches de ce qu'elle écrase."),
        ("Portrait: the diver",
         "He was the best of the Divers, the one who went down to check the seals. One day he did not come back up. The sea kept him and made him long, and heavy, and patient. He still checks the seals.",
         "Portrait : le plongeur",
         "C'était le meilleur des Plongeurs, celui qui descendait vérifier les scellés. Un jour il n'est pas remonté. La mer l'a gardé et l'a rendu long, et lourd, et patient. Il vérifie encore les scellés."),
        ("Observation: one breath",
         "Oxygen runs out under water and the pressure bites below the surface layers. A diving suit resists it, capsules and apnea kelp buy time. When the Leviathan pulls, swim across the current, never against it.",
         "Observation : un seul souffle",
         "L'oxygène s'épuise sous l'eau et la pression mord sous les couches de surface. Le scaphandre y résiste, les capsules et l'algue d'apnée font gagner du temps. Quand le Léviathan aspire, nage en travers du courant, jamais contre lui."),
        ("Cipher, seventh leaf",
         "The doll of the sea sleeps inside no other: it holds the nine. Close it last, around all of them, and the whole will be a single doll.",
         "Chiffre, septième feuillet",
         "La poupée de la mer ne dort dans aucune autre : elle contient les neuf. Referme-la en dernier, autour de toutes, et l'ensemble ne sera plus qu'une seule poupée."),
        ("One creature",
         "Ten worlds, ten prisons, and one prisoner. The cores you carry are not trophies: they are the keys of its cells. With each one you take, it breathes a little easier. All of this was made to hold a single creature.",
         "Une seule créature",
         "Dix mondes, dix prisons, et un seul prisonnier. Les noyaux que tu portes ne sont pas des trophées : ce sont les clés de ses cellules. À chaque noyau que tu prends, elle respire un peu mieux. Tout ceci a été fait pour enfermer une seule créature."),
    ],
    8: [
        ("Site note: worn by time",
         "If it cannot be killed, it can be worn down. I made a world where days pass in minutes and seasons in an hour, so that time would grind at it without rest, the way a river grinds a stone.",
         "Note de chantier : usée par le temps",
         "Si on ne peut pas la tuer, on peut l'user. J'ai fait un monde où les jours passent en minutes et les saisons en une heure, pour que le temps la ronge sans repos, comme une rivière use une pierre."),
        ("Portrait: the one who counts",
         "My eldest apprentice kept the calendar. He watched every season of this world turn, and then every cycle of mine. He has seen me come through here more times than he will say. Ask him. He will not answer.",
         "Portrait : celui qui compte",
         "Mon plus vieil apprenti tenait le calendrier. Il a vu tourner chaque saison de ce monde, puis chaque cycle du mien. Il m'a vu passer ici plus de fois qu'il ne le dira. Demande-lui. Il ne répondra pas."),
        ("Observation: right on time",
         "The Time Workshop only accepts recipes at dawn and dusk. Each season changes the creatures and what they drop; a season preserve shields you from the current one. Strike the Master in every season.",
         "Observation : pile à l'heure",
         "L'Atelier du temps n'accepte les recettes qu'à l'aube et au crépuscule. Chaque saison change les créatures et leurs butins ; une conserve de saison te protège de la saison en cours. Frappe le Maître à chaque saison."),
        ("Cipher, eighth leaf",
         "Do not trust the order of the worlds: I did not make the dolls in the order you open them. The doll of the seasons sleeps inside the doll of the Giant Veins.",
         "Chiffre, huitième feuillet",
         "Ne te fie pas à l'ordre des mondes : je n'ai pas fait les poupées dans l'ordre où tu les ouvres. La poupée des saisons dort dans celle des Filons géants."),
        ("Footprints",
         "The dust in the Library of Ages has footprints in it, older than the Ephemerals can count. Someone has already walked every road you walked, opened every block, beaten every boss. Someone came this way before.",
         "Des empreintes",
         "La poussière de la Bibliothèque des siècles porte des empreintes, plus vieilles que ce que les Éphémères savent compter. Quelqu'un a déjà suivi chaque route que tu as suivie, ouvert chaque bloc, battu chaque boss. Quelqu'un est déjà passé par là."),
    ],
    9: [
        ("Site note: the last lock",
         "The last lock cannot be picked because it never stays in one place. The ground itself moves, closes, swallows what is not anchored. Its heart beats. It is the lock, and the lock is alive.",
         "Note de chantier : le dernier verrou",
         "Le dernier verrou ne se crochète pas, parce qu'il ne reste jamais au même endroit. Le sol lui-même bouge, se referme, avale ce qui n'est pas ancré. Son cœur bat. C'est le verrou, et le verrou est vivant."),
        ("Portrait: the body of the lock",
         "No apprentice could become a lock, so I gave this one no face. The Heart of the Terrain does not guard the lock: it is the lock's own body. When it stops beating, only one door is left.",
         "Portrait : le corps du verrou",
         "Aucun apprenti ne pouvait devenir un verrou, alors je n'ai pas donné de visage à celui-ci. Le Cœur du terrain ne garde pas le verrou : il en est le corps. Quand il cesse de battre, il ne reste qu'une porte."),
        ("Observation: anchor",
         "Anchors calm the ground around them and a Terrain Anchor stabilizes a whole camp. Grip boots keep you standing on moving rock. Beware chests and ore that breathe: mimics wait for your hand.",
         "Observation : s'ancrer",
         "Les ancres calment le sol autour d'elles et l'Ancre de terrain stabilise tout un camp. Les bottes d'accroche te gardent debout sur la roche qui bouge. Méfie-toi des coffres et des minerais qui respirent : les mimiques attendent ta main."),
        ("Cipher, ninth leaf",
         "When the ten are one, open it only once the Unfinished has fallen, or it will stay shut. The doll of the moving ground sleeps inside the doll of the Toxic Jungle.",
         "Chiffre, neuvième feuillet",
         "Quand les dix n'en font plus qu'une, ne l'ouvre qu'une fois l'Inachevée tombée, sinon elle restera fermée. La poupée du sol mouvant dort dans celle de la Jungle toxique."),
        ("Look at the handwriting",
         "Put this page next to the Scroll you woke up with. Same hand. Same crossed sevens. Same blot where the pen always slips. The traveller who came before you was you. I am you. I wrote all of this for myself.",
         "Regarde l'écriture",
         "Pose cette page à côté du Parchemin avec lequel tu t'es réveillé. Même main. Mêmes sept barrés. Même tache là où la plume glisse toujours. Le voyageur qui est passé avant toi, c'était toi. Je suis toi. J'ai écrit tout ceci pour moi-même."),
    ],
    10: [
        ("Site note: my workshop",
         "This is where I worked, kept at the size it had for me: you are a crumb on my bench now. Every zone replays one of the nine laws, because the last prison had to hold them all at once.",
         "Note de chantier : mon atelier",
         "C'est ici que je travaillais, gardé à la taille qu'il avait pour moi : tu es une miette sur mon établi. Chaque zone rejoue l'une des neuf lois, parce que la dernière prison devait toutes les tenir à la fois."),
        ("Portrait: the Unfinished",
         "Before the worlds, there was a hunger with no edge, and it ate everything that was. It wears my ten prisons now like ten dresses. Each shell you break shows the face of a world you already crossed.",
         "Portrait : l'Inachevée",
         "Avant les mondes, il y avait une faim sans bord, et elle dévorait tout ce qui existait. Elle porte maintenant mes dix prisons comme dix robes. Chaque enveloppe que tu brises montre le visage d'un monde que tu as déjà traversé."),
        ("Observation: every tool",
         "Each shell fights with the rules of a former world: bring what each world taught you. Light, air, cold, weight, footing. When the last shell breaks, what is left is very small. Do not look away.",
         "Observation : tous les outils",
         "Chaque enveloppe se bat avec les règles d'un ancien monde : apporte ce que chaque monde t'a appris. Lumière, air, froid, poids, appui. Quand la dernière enveloppe se brise, ce qui reste est tout petit. Ne détourne pas les yeux."),
        ("Cipher, last leaf",
         "Inside the smallest doll is my room, as I left it. When the work refuses to end in there, put down what you hold, kneel, and let it stay unfinished. The doll of the workshop sleeps inside the doll of the Storm Archipelago.",
         "Chiffre, dernier feuillet",
         "Dans la plus petite poupée se trouve ma chambre, telle que je l'ai laissée. Quand l'œuvre refuse de finir, là-dedans, pose ce que tu tiens, agenouille-toi, et laisse-la inachevée. La poupée de l'atelier dort dans celle de l'Archipel des tempêtes."),
        ("You set it free",
         "Every core you took was a lock you opened. You did not climb out of ten worlds: you broke ten prisons, and what they held is awake now. Seal it again, or take its hunger for yourself. Or find the smallest doll.",
         "Tu l'as libérée",
         "Chaque noyau que tu as pris était un verrou que tu ouvrais. Tu n'es pas sorti de dix mondes : tu as brisé dix prisons, et ce qu'elles tenaient est éveillé. Scelle-la de nouveau, ou prends sa faim pour toi. Ou trouve la plus petite poupée."),
    ],
}

# ---------------------------------------------------------------- hints: what each people says of its hidden doll
# Spoken when the player shows the people of world w its hidden doll: which doll sleeps inside it (NEST_ORDER).
DOLL_LINES = {
    1: ("That doll grew in our forest. The elders say a doll of moving earth sleeps in its belly.",
        "Cette poupée a poussé dans notre forêt. Les anciens disent qu'une poupée de terre mouvante dort dans son ventre."),
    2: ("Knock on it: hollow. My father swore a doll of hurried seasons sleeps inside ours.",
        "Frappe dessus : creuse. Mon père jurait qu'une poupée des saisons pressées dort dans la nôtre."),
    3: ("Our doll is a cell too. The one locked inside is the doll of the upside-down world.",
        "Notre poupée est une cellule, elle aussi. Celle qu'on y a enfermée, c'est la poupée du monde à l'envers."),
    4: ("The wind brought this one to us. The keepers say the doll of the giant workshop sleeps inside it.",
        "C'est le vent qui nous l'a apportée. Les gardiens disent que la poupée de l'atelier géant dort dedans."),
    5: ("(The Silent One signs slowly: in its belly, the doll of the green jungle.)",
        "(Le Silencieux signe lentement : dans son ventre, la poupée de la jungle verte.)"),
    6: ("Ours holds nothing. It is the smallest of all. It only holds what someone wanted to forget.",
        "La nôtre ne contient rien. C'est la plus petite de toutes. Elle ne garde que ce que quelqu'un a voulu oublier."),
    7: ("The sea's doll holds the doll of the storms, and every other one inside that.",
        "La poupée de la mer contient la poupée des tempêtes, et toutes les autres là-dedans."),
    8: ("Quick, before nightfall: the doll of the dark sleeps inside ours. That is all I know.",
        "Vite, avant la nuit : la poupée du noir dort dans la nôtre. C'est tout ce que je sais."),
    9: ("Ours swallowed the doll of the locks and never gave it back.",
        "La nôtre a avalé la poupée des verrous et ne l'a jamais rendue."),
    10: ("The Master carved this one around the doll of the forge. I held the lamp.",
         "Le Maître a sculpté celle-ci autour de la poupée de la forge. Je tenais la lampe."),
}

# ---------------------------------------------------------------- World 0: the smallest doll
# In the code, world number 0 is the Surface. The hidden world is the dimension matriochka:world_zero, internal
# number 11 (Worlds.ZERO). It opens with the Whole Matryoshka once the Unfinished has fallen. Its rule, Obsession,
# is the synthesis the world reveals: every finished gesture (holding a tool, striking) feeds the creature, and only
# empty hands calm it. Its encounter, the Artisan's Shadow, cannot be finished: it stitches itself back. The way out
# is to set down the tools and kneel at the Artisan's bench, which is the third ending.
WORLD_ZERO = dict(n=11, key="world_zero", en="The Smallest Doll", fr="La plus petite poupée", rule="stillness",
                  pal=("8a1c14", "e8c070", "f6ecd8", "2a0c08"), fog="3a140c", sky="1a0806", water="5a1a10")
RULES["stillness"] = dict(en="Obsession", fr="Obsession")
WORLD_ZERO_BOSS = dict(id="artisan_shadow", meet="world_zero", offering="",
                       en="The Artisan's Shadow", fr="L'Ombre de l'Artisan", world=11, hp=9000, dmg=55, body="artisan", size=1.25,
                       core="", phases=(0.66, 0.33),
                       atk=[("Unfinished Stroke", "Trait inachevé"), ("Borrowed Law", "Loi empruntée"),
                            ("Ten Prisons at Once", "Dix prisons à la fois"), ("Every seam gives way", "Toutes ses coutures cèdent")])

# ---------------------------------------------------------------- endings
# seal: positive karma (or zero) after the Unfinished; absorb: negative karma; tools: finishing World 0.
# Each crawl is shown by the ending screen, then the credits.
ENDINGS = {
    "seal": dict(en="Sealed", fr="Scellée", lines=[
        ("The last shell closes.", "La dernière enveloppe se referme."),
        ("You press the ten cores back into their locks, one by one.", "Tu remets les dix noyaux dans leurs serrures, un par un."),
        ("The forest grows over the forge. The doors find their keys. The wind rises again.", "La forêt repousse sur la forge. Les portes retrouvent leurs clés. Le vent se lève de nouveau."),
        ("Somewhere very small, the Unfinished curls up and sleeps.", "Quelque part, tout petit, l'Inachevée se replie et s'endort."),
        ("Peace returns to the worlds. The peoples will never know why.", "La paix revient dans les mondes. Les peuples ne sauront jamais pourquoi."),
        ("You lie down on the Surface, under a sky you no longer trust.", "Tu t'allonges sur la Surface, sous un ciel auquel tu ne crois plus."),
        ("One day you will wake up with a Scroll in your hands, and you will not remember writing it.", "Un jour tu te réveilleras avec un Parchemin entre les mains, et tu ne te souviendras pas de l'avoir écrit."),
    ], lasting=("Lasting: two more hearts. The peoples will remember you.", "Durable : deux cœurs de plus. Les peuples se souviendront de toi.")),
    "absorb": dict(en="Absorbed", fr="Absorbée", lines=[
        ("The last shell breaks, and you do not let what is inside get away.", "La dernière enveloppe se brise, et tu ne laisses pas s'échapper ce qu'elle contenait."),
        ("You breathe it in. It has no edge, and neither do you, now.", "Tu l'inspires. Elle n'a pas de bord, et toi non plus, désormais."),
        ("The worlds feel you inside them like a new law.", "Les mondes te sentent en eux comme une loi nouvelle."),
        ("The apprentices kneel. The peoples close their doors.", "Les apprentis s'agenouillent. Les peuples ferment leurs portes."),
        ("You were the Artisan. You are the creature now.", "Tu étais l'Artisan. Tu es la créature, maintenant."),
        ("Somewhere, a traveller wakes up on the Surface with a Scroll in their hands.", "Quelque part, un voyageur se réveille sur la Surface avec un Parchemin entre les mains."),
        ("They will come for you.", "Il viendra te chercher."),
    ], lasting=("Lasting: your strikes hit a quarter harder. Your karma can no longer rise.", "Durable : tes coups frappent un quart plus fort. Ton karma ne peut plus remonter.")),
    "tools": dict(en="Set Down the Tools", fr="Poser les outils", lines=[
        ("You set the hammer down. Then the chisel. Then the last doll, still open.", "Tu poses le marteau. Puis le ciseau. Puis la dernière poupée, encore ouverte."),
        ("The Shadow waits for the stroke that will finish it. It never comes.", "L'Ombre attend le coup qui l'achèvera. Il ne vient jamais."),
        ("It kneels beside you. It has your hands.", "Elle s'agenouille à côté de toi. Elle a tes mains."),
        ("The Unfinished was never a creature from before the worlds.", "L'Inachevée n'a jamais été une créature d'avant les mondes."),
        ("It was the part of you that could not stop.", "C'était la part de toi qui ne savait pas s'arrêter."),
        ("Above this room, the Surface: one more doll, painted by the same hand.", "Au-dessus de cette chambre, la Surface : une poupée de plus, peinte par la même main."),
        ("You leave the work unfinished. The cycle stops.", "Tu laisses l'œuvre inachevée. Le cycle s'arrête."),
        ("The last Scroll is blank.", "Le dernier Parchemin est blanc."),
    ], lasting=("Lasting: the Blank Scroll. Nothing is left to finish.", "Durable : le Parchemin blanc. Il ne reste rien à finir.")),
}
# Advancements of the Endings tab: (id, icon item, title_en, title_fr, desc_en, desc_fr). The third ending itself is
# the existing hidden achievement "Set Down the Tools" (custom key third_end) of World 10.
ENDING_ADVANCEMENTS = [
    ("seal", "unfinished_core", "Sealed", "Scellée", "Lock the Unfinished away again.", "Enfermer de nouveau l'Inachevée."),
    ("absorb", "unfinished_core", "Absorbed", "Absorbée", "Take the Unfinished's hunger for yourself.", "Prendre pour soi la faim de l'Inachevée."),
    ("world_zero", "whole_matryoshka", "The Smallest Doll", "La plus petite poupée", "Open the Whole Matryoshka and enter World 0.", "Ouvrir la Matriochka entière et entrer dans le monde 0."),
    ("new_cycle", "artisan_scroll", "Once More", "Encore une fois", "Begin a New Cycle.", "Commencer un Nouveau Cycle."),
]
CREDITS = [("Matriochka", "Matriochka"), ("A mod by achedon12", "Un mod d'achedon12"), ("Thank you for playing.", "Merci d'avoir joué.")]

# ---------------------------------------------------------------- story strings (pages, nesting, World 0, endings, cycles)
STORY_UI = {
    "journal.matriochka.tab.pages": ("Pages", "Pages"),
    "journal.matriochka.pages.index": ("Found pages", "Pages trouvées"),
    "journal.matriochka.pages.none": ("No page found yet. They wait in the structures of every world.", "Aucune page trouvée. Elles attendent dans les structures de chaque monde."),
    "journal.matriochka.pages.missing": ("This page is still lost somewhere in World %s.", "Cette page est encore perdue quelque part dans le monde %s."),
    "journal.matriochka.pages.coded": ("Coded. Carry this world's core or defeat its boss to read it.", "Chiffrée. Porte le noyau de ce monde ou bats son boss pour la lire."),
    "journal.matriochka.pages.decoded": ("Deciphered", "Déchiffrée"),
    "journal.matriochka.pages.label": ("World %s, page %s", "Monde %s, page %s"),
    "journal.matriochka.cycle": ("Cycle %s", "Cycle %s"),
    "journal.matriochka.endings": ("Endings seen: %s", "Fins vues : %s"),
    "journal.matriochka.new_cycle": ("New Cycle", "Nouveau Cycle"),
    "journal.matriochka.new_cycle.confirm": ("Sure?", "Sûr ?"),
    "journal.matriochka.new_cycle.help": ("A New Cycle closes every world again, stronger. You keep your souls, karma, pages and gear; your group starts over from the Guardian.", "Un Nouveau Cycle referme tous les mondes, plus forts. Tu gardes tes âmes, ton karma, tes pages et ton équipement ; ton groupe repart du Gardien."),
    "journal.matriochka.objective.zero": ("The Whole Matryoshka is in your hands. Open it: World 0 sleeps inside.", "La Matriochka entière est entre tes mains. Ouvre-la : le monde 0 dort dedans."),
    "message.matriochka.nest.hollow": ("Hollow. A smaller doll fits inside, or it fits inside a bigger one. Hold the next one in your other hand.", "Creuse. Une poupée plus petite tient dedans, ou elle tient dans une plus grande. Tiens la suivante dans ton autre main."),
    "message.matriochka.nest.rattle": ("It rattles and will not close: that doll does not belong around this one.", "Ça cliquette et ne se ferme pas : cette poupée n'a pas sa place autour de celle-ci."),
    "message.matriochka.nest.closed": ("Click. %s dolls now sleep one inside the other.", "Clic. %s poupées dorment maintenant l'une dans l'autre."),
    "message.matriochka.nest.whole": ("The tenth doll closes around the nine. They are one now. Something very small knocks from inside.", "La dixième poupée se referme sur les neuf. Elles ne font plus qu'une. Quelque chose de tout petit frappe de l'intérieur."),
    "message.matriochka.nest.sealed": ("It will not open while the Unfinished still wears its shells.", "Elle ne s'ouvrira pas tant que l'Inachevée porte encore ses enveloppes."),
    "item.matriochka.nested_dolls.n": ("Nested Dolls (%s / 10)", "Poupées emboîtées (%s / 10)"),
    "item.matriochka.carver_note": ("Carver's Note", "Note du sculpteur"),
    "item.matriochka.carver_note.lore": ("Count the notches. The fewest sleeps deepest.", "Compte les encoches. La moins marquée dort au plus profond."),
    "message.matriochka.peddler.dolls": ("Dolls? I sell them, I never open them. But I know the rule: the smallest in your main hand, the next in the other. A wrong one rattles.", "Des poupées ? J'en vends, je n'en ouvre jamais. Mais je connais la règle : la plus petite en main principale, la suivante dans l'autre. Une mauvaise, ça cliquette."),
    "message.matriochka.peddler.cycle": ("Back already? Last time you swore it was the end, too.", "Déjà de retour ? La dernière fois aussi, tu jurais que c'était la fin."),
    "message.matriochka.apprentice.whole": ("Ten in one. Open it only after she has fallen. His room is inside. Do not finish anything in there, Master.", "Dix en une. Ne l'ouvre qu'après sa chute. Sa chambre est dedans. N'y termine rien, Maître."),
    "message.matriochka.zero.enter": ("The doll opens, and you are inside the smallest of them all.", "La poupée s'ouvre, et tu es dans la plus petite de toutes."),
    "message.matriochka.zero.chamber.0": ("The first chamber smells of spores, ash and old keys.", "La première chambre sent les spores, la cendre et les vieilles clés."),
    "message.matriochka.zero.chamber.1": ("The second chamber is windy, dark and upside down.", "La deuxième chambre est venteuse, sombre et à l'envers."),
    "message.matriochka.zero.chamber.2": ("The third chamber is wet, old, and it moves.", "La troisième chambre est humide, vieille, et elle bouge."),
    "message.matriochka.zero.cleared": ("The sealed gate sinks into the floor.", "La porte scellée s'enfonce dans le sol."),
    "message.matriochka.zero.room": ("A bed, a bench, a Scroll. A doll your size, empty. You know this room.", "Un lit, un établi, un Parchemin. Une poupée à ta taille, vide. Tu connais cette chambre."),
    "message.matriochka.zero.diorama": ("On the bench, a cracked doll holds a tiny meadow, a tiny village, a tiny sanctuary. The Surface. It was one more doll.", "Sur l'établi, une poupée fêlée contient une prairie minuscule, un village minuscule, un sanctuaire minuscule. La Surface. Ce n'était qu'une poupée de plus."),
    "message.matriochka.zero.wake": ("Your shadow rises from the bench, a chisel in each hand.", "Ton ombre se lève de l'établi, un ciseau dans chaque main."),
    "message.matriochka.zero.stitch": ("The Shadow stitches itself back together. \"I am never finished. Neither are you.\"", "L'Ombre se recoud. « Je ne suis jamais finie. Toi non plus. »"),
    "message.matriochka.zero.kneel": ("Empty hands, on your knees at the bench... the Shadow slows.", "Les mains vides, à genoux devant l'établi... l'Ombre ralentit."),
    "message.matriochka.zero.obsession": ("Your hands will not stop. The work feeds on you.", "Tes mains ne s'arrêtent pas. L'œuvre se nourrit de toi."),
    "message.matriochka.zero.done": ("The room is quiet. Nothing in it is finished, and nothing needs to be.", "La chambre est calme. Rien n'y est fini, et rien n'a besoin de l'être."),
    "message.matriochka.cycle.begun": ("Cycle %s begins. The worlds close again, harder than before.", "Le cycle %s commence. Les mondes se referment, plus durs qu'avant."),
    "message.matriochka.cycle.locked": ("Reach an ending first.", "Atteins d'abord une fin."),
    "message.matriochka.cycle.old_block": ("This World Block belongs to an older cycle. It crumbles into painted dust.", "Ce Bloc-monde appartient à un cycle plus ancien. Il s'effrite en poussière peinte."),
    "message.matriochka.blank_scroll": ("The Scroll is blank. You smile.", "Le Parchemin est blanc. Tu souris."),
    "ending.matriochka.close": ("Press Escape to close", "Échap pour fermer"),
    "ending.matriochka.cycle_hint": ("The Journal can begin a New Cycle.", "Le Journal peut commencer un Nouveau Cycle."),
    "command.matriochka.ending.done": ("Ending played: %s", "Fin jouée : %s"),
    "command.matriochka.cycle.show": ("Cycle %s", "Cycle %s"),
}
