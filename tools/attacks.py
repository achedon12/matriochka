"""Signature attacks: every creature has its own, none is shared.

Each attack is built from a delivery (how it reaches you) and its own numbers, effects, particles and sound.
The delivery is only the engine underneath (MobMoves.java); names, numbers, afflictions and animations are
specific to the creature. Descriptions are written from the numbers, so they always match the game.

Keys: m damage multiplier, r reach or radius, n hits, iv ticks between hits, kb knockback, up lift,
fx effects on the victim [(effect, ticks, level)], g gauges [(gauge, delta)], fire seconds of fire,
self effects on the creature, heal share of max health, summon entity id, count, p particle, s sound,
hit wind-up tick, end total ticks, cd cooldown in seconds, min/max range.
"""
import zlib

D = {  # delivery defaults
    "melee": dict(m=1.0, r=3.0, n=1, iv=4, hit=8, end=14, cd=4, min=0, max=3.2),
    "leap": dict(m=1.2, up=0.42, hit=9, end=24, cd=4.5, min=3, max=9),
    "ring": dict(m=1.0, r=3.5, up=0.5, hit=14, end=22, cd=5.5, min=0, max=4),
    "cone": dict(m=0.9, r=4.0, kb=1.0, hit=10, end=16, cd=4, min=0, max=4),
    "bolt": dict(m=0.8, r=16, n=1, iv=3, hit=12, end=18, cd=4, min=3.5, max=16),
    "beam": dict(m=0.3, r=12, n=6, iv=4, hit=10, end=36, cd=7, min=2, max=12),
    "pull": dict(m=0.5, r=12, kb=1.2, hit=10, end=18, cd=5, min=3, max=12),
    "blink": dict(m=1.0, hit=8, end=14, cd=6.5, min=3, max=14),
    "spin": dict(m=0.4, r=2.2, n=4, iv=4, hit=4, end=22, cd=5, min=0, max=2.6),
    "grab": dict(m=0.5, r=2.4, hold=40, hit=8, end=16, cd=6, min=0, max=2.6),
    "rain": dict(m=1.2, r=2.5, hit=24, end=30, cd=7, min=2, max=14),
    "trail": dict(r=2.0, dur=100, hit=6, end=12, cd=8, min=0, max=10),
    "dash": dict(m=1.0, kb=0.8, hit=10, end=22, cd=5.5, min=3, max=12),
    "quake": dict(m=0.8, r=6, n=3, iv=5, hit=12, end=28, cd=7, min=0, max=7),
    "summon": dict(count=2, hit=16, end=24, cd=16, min=0, max=16),
    "ward": dict(hit=10, end=18, cd=12, min=0, max=16),
    "roar": dict(r=8, hit=12, end=24, cd=11, min=0, max=10),
}

# (slug, EN name, FR name, delivery, params)
A = {
    # ---------------------------------------------------------------- World 1, Toxic Jungle
    "sporeling": [
        ("nip", "Spore Nip", "Morsure de spores", "melee", dict(n=2, iv=4, m=0.6, g=[("toxin", 3)], p="matriochka:spore", s="entity.fox.bite")),
        ("pop", "Puffball Pop", "Vesse-de-loup", "ring", dict(r=2.5, m=0.6, up=0.2, g=[("toxin", 8)], p="falling_spore_blossom", s="entity.puffer_fish.blow_up", hit=10, end=16)),
        ("scatter", "Scatter Hop", "Saut d'essaim", "leap", dict(m=0.9, up=0.55, min=2, max=7, p="matriochka:spore", s="entity.slime.jump")),
    ],
    "root_creeper": [
        ("tangle", "Root Tangle", "Entrave de racines", "grab", dict(hold=60, m=0.4, fx=[("slowness", 60, 4)], p="mycelium", s="block.rooted_dirt.break")),
        ("lash", "Vine Lash", "Fouet de liane", "cone", dict(r=4.5, m=0.8, kb=0.6, p="happy_villager", s="entity.player.attack.sweep")),
        ("creep", "Undergrowth", "Sous-bois rampant", "trail", dict(r=2.5, dur=120, fx=[("slowness", 40, 1)], p="mycelium", s="block.moss.place")),
    ],
    "snare_flower": [
        ("spit", "Nectar Spit", "Crachat de nectar", "bolt", dict(m=0.7, g=[("toxin", 6)], fx=[("nausea", 60, 0)], p="falling_spore_blossom", s="entity.llama.spit")),
        ("bloom", "Carnivore Bloom", "Floraison carnivore", "ring", dict(r=3.0, m=1.1, up=0.1, fx=[("poison", 60, 1)], p="matriochka:spore", s="block.big_dripleaf.tilt_down")),
        ("reel", "Pollen Reel", "Ressac de pollen", "pull", dict(r=10, kb=0.9, m=0.6, g=[("toxin", 4)], p="falling_spore_blossom", s="entity.fishing_bobber.retrieve")),
    ],
    "spore_bearer": [
        ("cough", "Spore Cough", "Toux de spores", "bolt", dict(n=3, iv=3, m=0.35, g=[("toxin", 3)], p="matriochka:spore", s="entity.panda.sneeze")),
        ("veil", "Choking Veil", "Voile étouffant", "trail", dict(r=3.0, dur=140, fx=[("poison", 60, 0), ("blindness", 40, 0)], p="falling_spore_blossom", s="block.fungus.break")),
        ("burst", "Sac Burst", "Éclatement du sac", "ring", dict(r=4.0, m=0.5, up=0.3, fx=[("weakness", 100, 0)], p="crimson_spore", s="entity.slime.squish")),
    ],
    "chitin_guard": [
        ("bash", "Carapace Bash", "Coup de carapace", "dash", dict(m=1.1, kb=1.4, p="crit", s="entity.ravager.attack")),
        ("pincer", "Pincer Clamp", "Étau de pinces", "grab", dict(hold=30, m=0.8, fx=[("slowness", 30, 6)], p="crit", s="entity.player.attack.crit")),
        ("harden", "Harden Shell", "Durcir la coque", "ward", dict(self=[("resistance", 100, 2)], p="wax_on", s="item.armor.equip_netherite")),
        ("stomp", "Hive Stomp", "Piétinement de ruche", "quake", dict(r=5, m=0.6, n=2, p="matriochka:spore", s="entity.iron_golem.attack")),
    ],
    # ---------------------------------------------------------------- World 2, Giant Veins
    "ash_miner": [
        ("pick", "Pick Swing", "Coup de pioche", "melee", dict(m=1.1, r=3.2, fx=[("mining_fatigue", 80, 0)], p="crit", s="block.stone.break")),
        ("lamp", "Lamp Flare", "Éclat de lampe", "bolt", dict(m=0.6, fire=3, p="flame", s="entity.blaze.shoot")),
        ("cave", "Cave-In", "Éboulement", "rain", dict(r=2.5, m=1.3, p="matriochka:grit", s="block.pointed_dripstone.land")),
    ],
    "living_vein": [
        ("pulse", "Molten Pulse", "Pulsation en fusion", "ring", dict(r=3.0, m=0.9, g=[("heat", 8)], p="lava", s="block.lava.pop")),
        ("whip", "Vein Whip", "Fouet de veine", "cone", dict(r=5.0, m=0.9, kb=0.8, fire=2, p="dripping_lava", s="entity.player.attack.sweep")),
        ("seep", "Magma Seep", "Suintement de magma", "trail", dict(r=2.0, dur=100, g=[("heat", 2)], fire=2, p="dripping_lava", s="block.lava.ambient")),
    ],
    "rock_salamander": [
        ("tongue", "Searing Tongue", "Langue brûlante", "pull", dict(r=8, kb=1.0, m=0.7, fire=3, p="flame", s="entity.frog.tongue")),
        ("roll", "Ember Roll", "Roulade de braises", "dash", dict(m=0.9, kb=0.6, g=[("heat", 5)], p="matriochka:ember", s="entity.blaze.burn")),
        ("tailflick", "Tail Flick", "Coup de queue", "spin", dict(n=2, m=0.6, r=2.4, fire=2, p="flame", s="entity.player.attack.sweep")),
    ],
    "dead_smith": [
        ("hammer", "Anvil Blow", "Coup d'enclume", "melee", dict(m=1.4, r=3.0, fx=[("slowness", 40, 1)], p="crit", s="block.anvil.land", hit=12, end=18)),
        ("sparks", "Forge Sparks", "Gerbe d'étincelles", "cone", dict(r=4.0, m=0.6, fire=4, kb=0.3, p="matriochka:ember", s="block.grindstone.use")),
        ("tongs", "Red-Hot Tongs", "Tenailles rougies", "grab", dict(hold=30, m=0.7, fire=3, p="small_flame", s="block.smithing_table.use")),
    ],
    "slag_golem": [
        ("fist", "Slag Fist", "Poing de scories", "melee", dict(m=1.3, r=3.4, kb=1.0, g=[("heat", 6)], p="lava", s="entity.iron_golem.attack")),
        ("spill", "Slag Spill", "Coulée de scories", "trail", dict(r=3.0, dur=120, g=[("heat", 3)], fire=3, p="lava", s="block.lava.extinguish")),
        ("crust", "Cooling Crust", "Croûte refroidie", "ward", dict(self=[("resistance", 120, 1), ("absorption", 200, 1)], p="large_smoke", s="block.lava.extinguish")),
        ("erupt", "Eruption", "Éruption", "quake", dict(r=6, n=3, m=0.7, fire=3, p="lava", s="entity.generic.explode")),
    ],
    # ---------------------------------------------------------------- World 3, Endless Dungeon
    "jailer_mob": [
        ("baton", "Baton Strike", "Coup de matraque", "melee", dict(m=1.0, fx=[("slowness", 40, 2)], p="crit", s="entity.player.attack.knockback")),
        ("shackle", "Thrown Shackle", "Menottes lancées", "bolt", dict(m=0.5, fx=[("slowness", 60, 3)], p="matriochka:chain_glint", s="block.chain.place")),
        ("lockdown", "Lockdown", "Confinement", "roar", dict(r=10, fx=[("slowness", 80, 1), ("mining_fatigue", 80, 1)], p="angry_villager", s="block.bell.use")),
    ],
    "sentinel": [
        ("gaze", "Watchful Gaze", "Regard de guet", "beam", dict(m=0.25, n=8, iv=4, fx=[("glowing", 100, 0)], p="enchanted_hit", s="entity.guardian.attack")),
        ("flare", "Alarm Flare", "Fusée d'alarme", "roar", dict(r=16, fx=[("glowing", 160, 0)], p="end_rod", s="block.bell.resonate")),
        ("headbutt", "Iron Brow", "Front de fer", "dash", dict(m=0.8, kb=1.2, p="crit", s="entity.zombie.attack_iron_door")),
    ],
    "living_lock": [
        ("snap", "Tumbler Snap", "Claquement de gorge", "melee", dict(m=1.2, r=2.6, p="crit", s="block.iron_trapdoor.close")),
        ("keyhole", "Keyhole Draw", "Appel de la serrure", "pull", dict(r=7, kb=1.4, m=0.4, p="matriochka:chain_glint", s="block.iron_door.open")),
        ("seal", "Seal Shut", "Scellé", "grab", dict(hold=50, m=0.3, fx=[("weakness", 80, 1)], p="wax_on", s="block.chest.locked")),
    ],
    "dungeon_rat": [
        ("gnaw", "Gnaw", "Rongement", "melee", dict(n=3, iv=3, m=0.35, fx=[("hunger", 80, 0)], p="crit", s="entity.silverfish.hurt")),
        ("skitter", "Skitter", "Détalade", "leap", dict(m=0.8, up=0.3, min=2, max=6, p="matriochka:cold_dust", s="entity.silverfish.step")),
        ("plague", "Plague Squeak", "Couinement de peste", "roar", dict(r=6, fx=[("hunger", 120, 1)], p="mycelium", s="entity.bat.ambient")),
    ],
    "executioner": [
        ("axe", "Headsman's Axe", "Hache du bourreau", "melee", dict(m=1.6, r=3.4, hit=14, end=20, p="sweep_attack", s="item.axe.strip")),
        ("verdict", "Verdict", "Verdict", "rain", dict(r=2.0, m=1.6, p="crit", s="block.anvil.land")),
        ("cleave", "Cleave", "Fendoir", "cone", dict(r=4.0, m=1.1, kb=1.2, p="sweep_attack", s="entity.player.attack.sweep")),
        ("hood", "Black Hood", "Cagoule noire", "roar", dict(r=8, fx=[("blindness", 60, 0), ("slowness", 60, 1)], p="large_smoke", s="entity.evoker.prepare_wololo")),
    ],
    # ---------------------------------------------------------------- World 4, Storm Archipelago
    "wind_ray": [
        ("gust", "Gust Wing", "Aile de rafale", "cone", dict(r=6.0, m=0.5, kb=2.0, up=0.5, p="cloud", s="entity.breeze.wind_burst")),
        ("glide", "Glide Cut", "Coupe planée", "dash", dict(m=0.9, kb=0.6, p="cloud", s="entity.phantom.swoop")),
        ("updraft", "Updraft", "Courant ascendant", "ring", dict(r=4.0, m=0.3, up=1.0, fx=[("levitation", 20, 0)], p="cloud", s="entity.breeze.shoot")),
    ],
    "storm_bird": [
        ("dive", "Thunder Dive", "Piqué tonnerre", "leap", dict(m=1.3, up=0.1, p="electric_spark", s="entity.phantom.swoop")),
        ("static", "Static Feathers", "Plumes statiques", "bolt", dict(n=3, iv=2, m=0.35, fx=[("slowness", 20, 1)], p="matriochka:storm_spark", s="entity.breeze.shoot")),
        ("screech", "Storm Screech", "Cri d'orage", "roar", dict(r=9, fx=[("nausea", 80, 0)], p="electric_spark", s="entity.parrot.imitate.phantom")),
    ],
    "island_warden": [
        ("boulder", "Boulder Toss", "Jet de rocher", "rain", dict(r=3.0, m=1.2, up=0.4, p="cloud", s="block.stone.break")),
        ("anchor", "Anchor Fist", "Poing d'ancre", "melee", dict(m=1.2, r=3.4, fx=[("slow_falling", 1, 0)], up=-0.4, p="crit", s="entity.iron_golem.attack")),
        ("stand", "Stand Firm", "Pied ferme", "ward", dict(self=[("resistance", 100, 1)], p="cloud", s="block.basalt.place")),
    ],
    "cloud_mine": [
        ("drift", "Drift Charge", "Dérive chargée", "dash", dict(m=0.7, kb=1.0, p="electric_spark", s="entity.creeper.primed")),
        ("arc", "Static Arc", "Arc statique", "beam", dict(m=0.2, n=5, iv=4, r=6, p="matriochka:storm_spark", s="entity.guardian.attack")),
        ("puff", "Thunderhead", "Cumulonimbus", "ring", dict(r=3.0, m=0.6, up=0.8, fx=[("levitation", 15, 1)], p="cloud", s="entity.breeze.wind_burst")),
    ],
    "sky_harpooner": [
        ("harpoon", "Barbed Harpoon", "Harpon barbelé", "bolt", dict(m=1.0, fx=[("slowness", 40, 2)], p="crit", s="item.trident.throw")),
        ("reel", "Line Reel", "Ressac de ligne", "pull", dict(r=14, kb=1.6, m=0.6, p="crit", s="item.trident.return")),
        ("deck", "Deck Sweep", "Balayage de pont", "cone", dict(r=4.0, m=0.9, kb=1.6, p="sweep_attack", s="entity.player.attack.sweep")),
        ("storm", "Harpoon Storm", "Tempête de harpons", "rain", dict(r=3.5, m=1.0, p="matriochka:storm_spark", s="item.trident.thunder")),
    ],
    # ---------------------------------------------------------------- World 5, Lightless Deep
    "blind_prowler": [
        ("maul", "Blind Maul", "Mutilation aveugle", "melee", dict(n=2, iv=5, m=0.8, p="squid_ink", s="entity.warden.attack_impact")),
        ("hunt", "Echo Hunt", "Chasse à l'écho", "leap", dict(m=1.2, min=3, max=10, p="matriochka:shadow_wisp", s="entity.warden.sniff")),
        ("howl", "Lightless Howl", "Hurlement sans lumière", "roar", dict(r=10, fx=[("darkness", 120, 0)], p="sculk_soul", s="entity.warden.roar")),
    ],
    "glow_devourer": [
        ("slurp", "Glow Slurp", "Lampée de lueur", "pull", dict(r=8, kb=1.0, m=0.5, fx=[("blindness", 40, 0)], p="matriochka:deep_mote", s="entity.generic.drink")),
        ("gulp", "Lantern Gulp", "Gorgée de lanterne", "grab", dict(hold=40, m=0.6, heal=0.1, p="glow", s="entity.generic.eat")),
        ("ink", "Ink Burst", "Jet d'encre", "ring", dict(r=4.0, m=0.4, up=0.1, fx=[("blindness", 80, 0)], p="squid_ink", s="entity.glow_squid.squirt")),
    ],
    "echo": [
        ("mimic", "Borrowed Cry", "Cri emprunté", "blink", dict(m=0.9, p="sculk_soul", s="entity.player.hurt")),
        ("reverb", "Reverb", "Réverbération", "quake", dict(r=7, n=3, m=0.4, fx=[("nausea", 60, 0)], p="sonic_boom", s="entity.warden.sonic_charge")),
        ("whisper", "Whisper", "Murmure", "bolt", dict(m=0.6, fx=[("darkness", 60, 0)], p="matriochka:shadow_wisp", s="entity.allay.ambient_without_item")),
    ],
    "eyeless_watcher": [
        ("stare", "Eyeless Stare", "Regard sans yeux", "beam", dict(m=0.25, n=6, iv=5, r=10, fx=[("darkness", 40, 0)], p="soul", s="entity.elder_guardian.curse")),
        ("grasp", "Cold Grasp", "Étreinte froide", "grab", dict(hold=40, m=0.5, fx=[("weakness", 60, 1)], p="matriochka:shadow_wisp", s="entity.vex.charge")),
        ("snuff", "Snuff Out", "Mouchage", "roar", dict(r=8, fx=[("blindness", 60, 0)], p="large_smoke", s="block.candle.extinguish")),
    ],
    "shadow_mother": [
        ("rend", "Rend", "Lacération", "melee", dict(n=3, iv=4, m=0.6, p="squid_ink", s="entity.ravager.attack")),
        ("brood", "Call the Brood", "Appel de la nichée", "summon", dict(summon="blind_prowler", count=1, p="squid_ink", s="entity.warden.emerge")),
        ("pounce", "Night Pounce", "Bond nocturne", "leap", dict(m=1.4, up=0.5, min=3, max=10, p="matriochka:shadow_wisp", s="entity.warden.attack_impact")),
        ("smother", "Smother", "Étouffement", "ring", dict(r=4.0, m=0.8, fx=[("darkness", 100, 0), ("slowness", 60, 1)], p="matriochka:shadow_wisp", s="entity.warden.heartbeat")),
    ],
    # ---------------------------------------------------------------- World 6, Upside Realm
    "reflection": [
        ("mirror", "Mirror Strike", "Frappe miroir", "blink", dict(m=1.1, p="reverse_portal", s="entity.illusioner.mirror_move")),
        ("shards", "Glass Shards", "Éclats de verre", "bolt", dict(n=4, iv=2, m=0.3, p="matriochka:mirror_shard", s="block.glass.break")),
        ("parry", "Reversed Parry", "Parade inversée", "ward", dict(self=[("resistance", 60, 3)], p="reverse_portal", s="item.shield.block")),
    ],
    "ceiling_walker": [
        ("drop", "Ceiling Drop", "Chute du plafond", "rain", dict(r=2.0, m=1.4, p="reverse_portal", s="entity.spider.ambient")),
        ("web", "Upside Web", "Toile renversée", "bolt", dict(m=0.4, fx=[("slowness", 80, 3)], p="poof", s="entity.spider.hurt")),
        ("bite", "Hanging Bite", "Morsure suspendue", "melee", dict(n=2, iv=4, m=0.7, fx=[("poison", 40, 0)], p="crit", s="entity.spider.step")),
    ],
    "unstable_sphere": [
        ("flip", "Gravity Flip", "Renversement", "ring", dict(r=4.0, m=0.4, fx=[("levitation", 30, 2)], p="reverse_portal", s="entity.shulker.shoot")),
        ("orbit", "Orbit Lash", "Fouet d'orbite", "spin", dict(r=3.0, n=4, m=0.35, p="portal", s="block.respawn_anchor.charge")),
        ("well", "Gravity Well", "Puits de gravité", "pull", dict(r=9, kb=1.1, m=0.3, fx=[("slow_falling", 60, 0)], p="reverse_portal", s="block.beacon.power_select")),
    ],
    "inverted_strider": [
        ("stilt", "Stilt Kick", "Coup d'échasse", "melee", dict(m=1.1, r=4.2, kb=1.2, p="crit", s="entity.horse.angry")),
        ("vault", "Inverted Vault", "Saut renversé", "leap", dict(m=1.0, up=0.8, min=3, max=9, p="reverse_portal", s="entity.goat.long_jump")),
        ("stride", "Long Stride", "Grande enjambée", "dash", dict(m=1.0, kb=1.0, p="poof", s="entity.strider.step")),
    ],
    "broken_mirror": [
        ("splinter", "Splinter Storm", "Tempête d'éclats", "ring", dict(r=4.0, m=0.7, up=0.1, p="matriochka:mirror_shard", s="block.glass.break")),
        ("refract", "Refraction Beam", "Rayon réfracté", "beam", dict(m=0.3, n=6, iv=4, r=12, fx=[("nausea", 60, 0)], p="end_rod", s="block.amethyst_block.resonate")),
        ("twin", "Shattered Twin", "Jumeau brisé", "summon", dict(summon="reflection", count=1, p="reverse_portal", s="entity.illusioner.prepare_mirror")),
        ("shard", "Crack Shard", "Fêlure", "cone", dict(r=4.0, m=1.0, kb=0.6, fx=[("weakness", 60, 0)], p="matriochka:mirror_shard", s="block.glass.break")),
    ],
    # ---------------------------------------------------------------- World 7, Pressure Ocean
    "abyssal_hunter": [
        ("lunge", "Abyss Lunge", "Bond des abysses", "leap", dict(m=1.3, up=0.0, min=3, max=12, p="bubble", s="entity.guardian.attack")),
        ("jaws", "Pressure Jaws", "Mâchoires de pression", "melee", dict(m=1.2, g=[("oxygen", -4)], p="bubble_pop", s="entity.drowned.hurt_water")),
        ("wake", "Hunting Wake", "Sillage de chasse", "spin", dict(r=2.6, n=3, m=0.4, g=[("oxygen", -2)], p="bubble", s="entity.dolphin.swim")),
    ],
    "blade_school": [
        ("swarm", "Blade Swarm", "Essaim de lames", "spin", dict(r=2.4, n=5, iv=3, m=0.3, p="bubble", s="entity.tropical_fish.flop")),
        ("pierce", "Pierce Line", "Ligne perçante", "dash", dict(m=0.9, kb=0.3, g=[("oxygen", -2)], p="bubble_pop", s="entity.player.attack.strong")),
        ("scatter", "Silver Scatter", "Dispersion argentée", "bolt", dict(n=4, iv=2, m=0.25, p="bubble", s="entity.fish.swim")),
    ],
    "pressure_jelly": [
        ("sting", "Pressure Sting", "Piqûre de pression", "melee", dict(m=0.8, fx=[("poison", 60, 1)], g=[("oxygen", -2)], p="glow", s="entity.glow_squid.hurt")),
        ("drift", "Crushing Drift", "Dérive écrasante", "ring", dict(r=3.5, m=0.5, fx=[("mining_fatigue", 80, 1)], g=[("oxygen", -3)], p="bubble_pop", s="block.conduit.ambient.short")),
        ("veil", "Tentacle Veil", "Voile de tentacules", "trail", dict(r=2.5, dur=120, fx=[("poison", 40, 0)], p="glow", s="entity.glow_squid.squirt")),
    ],
    "bell_crab": [
        ("clang", "Bell Clang", "Coup de cloche", "ring", dict(r=3.5, m=0.6, fx=[("nausea", 60, 0)], p="note", s="block.bell.use")),
        ("snip", "Claw Snip", "Coup de pince", "melee", dict(n=2, iv=4, m=0.7, p="crit", s="entity.player.attack.crit")),
        ("scuttle", "Sideways Scuttle", "Course de côté", "dash", dict(m=0.8, kb=1.2, p="bubble", s="entity.turtle.shamble")),
    ],
    "trench_eel": [
        ("coil", "Constrict", "Constriction", "grab", dict(hold=60, m=0.6, g=[("oxygen", -4)], p="bubble", s="entity.guardian.flop")),
        ("shock", "Trench Shock", "Choc des fosses", "ring", dict(r=4.0, m=0.8, fx=[("slowness", 40, 2)], p="electric_spark", s="entity.guardian.attack")),
        ("strike", "Eel Strike", "Frappe d'anguille", "leap", dict(m=1.2, up=0.0, min=3, max=10, p="bubble_pop", s="entity.drowned.shoot")),
        ("current", "Undertow", "Contre-courant", "pull", dict(r=12, kb=1.3, m=0.4, g=[("oxygen", -3)], p="bubble", s="block.bubble_column.whirlpool_inside")),
    ],
    # ---------------------------------------------------------------- World 8, Hastened Seasons
    "seasonal_creature": [
        ("thaw", "Spring Thaw", "Dégel printanier", "trail", dict(r=2.5, dur=100, fx=[("poison", 40, 0)], p="matriochka:petal", s="block.azalea_leaves.break")),
        ("heat", "Summer Charge", "Charge estivale", "dash", dict(m=1.0, fire=3, p="small_flame", s="entity.ravager.step")),
        ("fall", "Leaf Fall", "Chute des feuilles", "rain", dict(r=3.0, m=1.0, fx=[("weakness", 60, 0)], p="matriochka:autumn_leaf", s="block.cherry_leaves.break")),
    ],
    "hourglass_elder": [
        ("sand", "Sand of Hours", "Sable des heures", "beam", dict(m=0.2, n=8, iv=4, r=10, fx=[("slowness", 40, 1)], p="white_ash", s="block.sand.fall")),
        ("stop", "Stopped Minute", "Minute arrêtée", "roar", dict(r=7, fx=[("slowness", 60, 4), ("mining_fatigue", 60, 2)], p="end_rod", s="block.amethyst_block.chime")),
        ("turn", "Turn the Glass", "Retourner le sablier", "ward", dict(self=[("regeneration", 80, 1)], heal=0.15, p="white_ash", s="block.respawn_anchor.set_spawn")),
    ],
    "dusk_shade": [
        ("fade", "Dusk Fade", "Fondu du crépuscule", "blink", dict(m=1.1, p="large_smoke", s="entity.phantom.flap")),
        ("cut", "Twilight Cut", "Taille crépusculaire", "melee", dict(n=2, iv=5, m=0.7, fx=[("darkness", 40, 0)], p="matriochka:shadow_wisp", s="entity.player.attack.sweep")),
        ("nightfall", "Nightfall", "Tombée de la nuit", "ring", dict(r=4.0, m=0.6, fx=[("blindness", 60, 0)], p="large_smoke", s="entity.phantom.swoop")),
    ],
    "minute_child": [
        ("tantrum", "Tantrum", "Caprice", "spin", dict(r=2.2, n=4, m=0.35, p="angry_villager", s="entity.villager.no")),
        ("growth", "Growth Spurt", "Poussée de croissance", "ward", dict(self=[("strength", 100, 0), ("speed", 100, 0)], p="happy_villager", s="block.bone_block.place")),
        ("toss", "Toy Toss", "Jouet lancé", "bolt", dict(m=0.6, fx=[("nausea", 40, 0)], p="crit", s="entity.witch.throw")),
    ],
    "hour_keeper": [
        ("toll", "Hour Toll", "Glas de l'heure", "quake", dict(r=7, n=3, iv=6, m=0.7, p="note", s="block.bell.use")),
        ("hand", "Clock Hand", "Aiguille d'horloge", "cone", dict(r=5.0, m=1.0, kb=1.0, p="sweep_attack", s="block.grindstone.use")),
        ("gears", "Grinding Gears", "Engrenages", "grab", dict(hold=40, m=0.6, fx=[("slowness", 40, 4)], p="crit", s="block.piston.extend")),
        ("rewind", "Rewind", "Rembobinage", "ward", dict(heal=0.2, self=[("resistance", 60, 1)], p="end_rod", s="block.beacon.activate")),
    ],
    # ---------------------------------------------------------------- World 9, Restless Ground
    "crawling_block": [
        ("slam", "Block Slam", "Écrasement de bloc", "rain", dict(r=1.8, m=1.5, p="matriochka:grit", s="block.stone.place")),
        ("tumble", "Tumble", "Culbute", "dash", dict(m=1.0, kb=1.0, p="crit", s="block.stone.step")),
        ("bury", "Bury", "Enfouissement", "grab", dict(hold=40, m=0.5, fx=[("slowness", 40, 5)], p="crimson_spore", s="block.rooted_dirt.place")),
    ],
    "mimic": [
        ("lid", "Lid Chomp", "Coup de couvercle", "melee", dict(m=1.3, r=2.6, p="crit", s="block.chest.close")),
        ("tongue", "Chest Tongue", "Langue de coffre", "pull", dict(r=8, kb=1.4, m=0.6, p="crimson_spore", s="block.chest.open")),
        ("loot", "False Loot", "Faux butin", "bolt", dict(n=3, iv=3, m=0.3, fx=[("hunger", 60, 1)], p="wax_on", s="entity.item.pickup")),
    ],
    "foundation_eater": [
        ("burrow", "Burrow Strike", "Frappe enfouie", "blink", dict(m=1.2, p="crimson_spore", s="block.rooted_dirt.break")),
        ("tremor", "Tremor", "Secousse", "quake", dict(r=6, n=3, m=0.6, fx=[("mining_fatigue", 60, 1)], p="matriochka:grit", s="block.gravel.break")),
        ("swallow", "Swallow", "Engloutissement", "grab", dict(hold=50, m=0.6, fx=[("blindness", 40, 0)], p="crimson_spore", s="entity.generic.eat")),
    ],
    "earth_hand": [
        ("crush", "Earthen Grip", "Poigne de terre", "grab", dict(hold=50, m=0.8, fx=[("slowness", 50, 6)], p="matriochka:grit", s="block.rooted_dirt.break")),
        ("slap", "Palm Slap", "Gifle", "cone", dict(r=4.0, m=0.9, kb=1.8, up=0.4, p="poof", s="entity.player.attack.knockback")),
        ("rise", "Rising Fingers", "Doigts surgissants", "rain", dict(r=2.5, m=1.1, up=0.7, p="crimson_spore", s="block.gravel.place")),
    ],
    "walking_column": [
        ("topple", "Topple", "Basculement", "cone", dict(r=5.5, m=1.3, kb=0.6, hit=16, end=24, p="poof", s="block.stone.fall")),
        ("pillar", "Pillar Strike", "Frappe de pilier", "rain", dict(r=2.5, m=1.4, up=0.5, p="matriochka:grit", s="block.basalt.break")),
        ("hold", "Load-Bearing", "Porte-charge", "ward", dict(self=[("resistance", 120, 2)], p="poof", s="block.stone.place")),
        ("rubble", "Rubble Rain", "Pluie de gravats", "quake", dict(r=7, n=3, m=0.6, p="matriochka:grit", s="block.gravel.break")),
    ],
    # ---------------------------------------------------------------- World 10, The Giant Workshop
    "giant_sporeling": [
        ("stomp", "Giant Stomp", "Piétinement géant", "ring", dict(r=4.0, m=1.0, up=0.6, g=[("toxin", 6)], p="matriochka:spore", s="entity.ravager.step")),
        ("sneeze", "Spore Sneeze", "Éternuement de spores", "cone", dict(r=6.0, m=0.6, kb=1.2, g=[("toxin", 8)], p="sneeze", s="entity.panda.sneeze")),
        ("bud", "Budding", "Bourgeonnement", "summon", dict(summon="sporeling", count=2, p="falling_spore_blossom", s="block.fungus.place")),
    ],
    "ash_titanid": [
        ("forge", "Forge Hammer", "Marteau de forge", "melee", dict(m=1.5, r=3.4, fire=4, hit=12, end=18, p="lava", s="block.anvil.land")),
        ("cinder", "Cinder Rain", "Pluie de cendres", "rain", dict(r=3.5, m=1.0, fire=4, p="lava", s="entity.blaze.shoot")),
        ("bellows", "Bellows", "Soufflet", "cone", dict(r=6.0, m=0.5, kb=1.6, g=[("heat", 8)], p="flame", s="entity.blaze.burn")),
    ],
    "colossal_jailer": [
        ("gavel", "Iron Gavel", "Marteau de fer", "quake", dict(r=7, n=3, m=0.7, fx=[("slowness", 60, 2)], p="crit", s="block.anvil.land")),
        ("chains", "Chain Volley", "Volée de chaînes", "bolt", dict(n=3, iv=3, m=0.4, fx=[("slowness", 60, 2)], p="matriochka:chain_glint", s="block.chain.place")),
        ("warden", "Call the Wardens", "Appel des geôliers", "summon", dict(summon="jailer_mob", count=2, p="angry_villager", s="block.bell.use")),
    ],
    "titan_ray": [
        ("eclipse", "Eclipse Glide", "Planée d'éclipse", "dash", dict(m=1.2, kb=1.0, fx=[("darkness", 40, 0)], p="cloud", s="entity.phantom.swoop")),
        ("tempest", "Tempest Wing", "Aile de tempête", "cone", dict(r=7.0, m=0.6, kb=2.2, up=0.6, p="matriochka:storm_spark", s="entity.breeze.wind_burst")),
        ("downpour", "Downpour", "Averse", "rain", dict(r=4.0, m=1.1, fx=[("slowness", 60, 1)], p="splash", s="weather.rain.above")),
    ],
    "colossus_prowler": [
        ("quake", "Colossal Pounce", "Bond colossal", "leap", dict(m=1.5, up=0.6, min=3, max=12, p="sculk_soul", s="entity.warden.attack_impact")),
        ("dark", "Swallowed Light", "Lumière avalée", "roar", dict(r=12, fx=[("darkness", 160, 0)], p="sculk_soul", s="entity.warden.roar")),
        ("maul", "Colossal Maul", "Mutilation colossale", "melee", dict(n=3, iv=5, m=0.7, p="squid_ink", s="entity.ravager.attack")),
        ("tremor", "Pad Tremor", "Secousse de pattes", "quake", dict(r=8, n=3, m=0.6, p="sculk_soul", s="entity.warden.step")),
    ],
}

EFFECT_EN = {"slowness": "Slowness", "poison": "Poison", "weakness": "Weakness", "blindness": "Blindness", "darkness": "Darkness",
             "nausea": "Nausea", "levitation": "Levitation", "mining_fatigue": "Mining Fatigue", "hunger": "Hunger", "glowing": "Glowing",
             "slow_falling": "Slow Falling", "resistance": "Resistance", "absorption": "Absorption", "strength": "Strength",
             "speed": "Speed", "regeneration": "Regeneration", "wither": "Wither"}
EFFECT_FR = {"slowness": "Lenteur", "poison": "Poison", "weakness": "Faiblesse", "blindness": "Cécité", "darkness": "Obscurité",
             "nausea": "Nausée", "levitation": "Lévitation", "mining_fatigue": "Fatigue de minage", "hunger": "Faim", "glowing": "Surbrillance",
             "slow_falling": "Chute lente", "resistance": "Résistance", "absorption": "Absorption", "strength": "Force",
             "speed": "Vitesse", "regeneration": "Régénération", "wither": "Wither"}
GAUGE = {"toxin": ("toxin", "toxine"), "heat": ("heat", "chaleur"), "oxygen": ("oxygen", "oxygène")}
ROMAN = ["", " II", " III", " IV", " V", " VI", " VII", " VIII", " IX", " X"]


def full(mob_id):
    """The creature's attacks with every default filled in."""
    out = []
    for slug, en, fr, kind, p in A[mob_id]:
        d = dict(D[kind])
        d.update(p)
        d.update(id=f"{mob_id}.{slug}", slug=slug, en=en, fr=fr, kind=kind)
        d.setdefault("fx", [])
        d.setdefault("g", [])
        d.setdefault("self", [])
        d.setdefault("p", "crit")
        d.setdefault("s", "entity.player.attack.sweep")
        out.append(d)
    return out


def _n(x):
    return ("%.1f" % x).rstrip("0").rstrip(".")


def _pct(m):
    return f"{int(round(m * 100))}%"


def _after(a, lang):
    bits = []
    for e, t, lv in a["fx"]:
        name = (EFFECT_EN if lang == "en" else EFFECT_FR)[e] + ROMAN[lv]
        bits.append(f"{name} {_n(t / 20)} s")
    for g, v in a["g"]:
        nm = GAUGE[g][0 if lang == "en" else 1]
        bits.append(f"{nm} {'+' if v > 0 else ''}{v}")
    if a.get("fire"):
        bits.append(f"{a['fire']} s of fire" if lang == "en" else f"{a['fire']} s de feu")
    if not bits:
        return ""
    return (", then " if lang == "en" else ", puis ") + ", ".join(bits)


def describe(a, lang):
    k = a["kind"]
    m, after = _pct(a.get("m", 0)), _after(a, lang)
    en = lang == "en"
    if k == "melee":
        hits = a["n"]
        if en:
            s = f"{'A blow' if hits == 1 else f'{hits} quick blows'} at {_n(a['r'])} blocks, {m} damage{' each' if hits > 1 else ''}"
        else:
            s = f"{'Un coup' if hits == 1 else f'{hits} coups rapides'} à {_n(a['r'])} blocs, {m} des dégâts{' chacun' if hits > 1 else ''}"
    elif k == "leap":
        s = (f"Crouches, then leaps from {_n(a['min'])} to {_n(a['max'])} blocks away: {m} damage on contact" if en else
             f"S'accroupit puis bondit de {_n(a['min'])} à {_n(a['max'])} blocs : {m} des dégâts au contact")
    elif k == "ring":
        s = (f"Strikes everything within {_n(a['r'])} blocks around it, {m} damage" if en else
             f"Frappe tout ce qui est à {_n(a['r'])} blocs autour d'elle, {m} des dégâts")
    elif k == "cone":
        s = (f"Hits everything in front of it within {_n(a['r'])} blocks, {m} damage and thrown back" if en else
             f"Touche tout ce qui est devant elle à {_n(a['r'])} blocs, {m} des dégâts et repoussé")
    elif k == "bolt":
        n = a["n"]
        s = (f"{'Fires a bolt' if n == 1 else f'Fires {n} bolts'} in a straight line up to {_n(a['r'])} blocks, {m} damage{' each' if n > 1 else ''}. Breaking line of sight dodges it" if en else
             f"{'Lance un trait' if n == 1 else f'Lance {n} traits'} en ligne droite jusqu'à {_n(a['r'])} blocs, {m} des dégâts{' chacun' if n > 1 else ''}. Couper la ligne de vue l'esquive")
    elif k == "beam":
        s = (f"Holds a beam on you up to {_n(a['r'])} blocks: {a['n']} pulses of {m} damage while it sees you" if en else
             f"Garde un rayon sur toi jusqu'à {_n(a['r'])} blocs : {a['n']} impulsions de {m} des dégâts tant qu'elle te voit")
    elif k == "pull":
        s = (f"Yanks you toward it from up to {_n(a['r'])} blocks, then {m} damage if you land close" if en else
             f"T'attire vers elle jusqu'à {_n(a['r'])} blocs, puis {m} des dégâts si tu arrives près d'elle")
    elif k == "blink":
        s = (f"Vanishes and reappears behind you, then strikes for {m} damage" if en else
             f"Disparaît et réapparaît derrière toi, puis frappe pour {m} des dégâts")
    elif k == "spin":
        s = (f"Whirls, hitting everything within {_n(a['r'])} blocks {a['n']} times at {m} damage" if en else
             f"Tourbillonne et touche {a['n']} fois tout ce qui est à {_n(a['r'])} blocs, à {m} des dégâts")
    elif k == "grab":
        s = (f"Seizes you at arm's reach: held for {_n(a['hold'] / 20)} s and {m} damage" if en else
             f"T'attrape à portée de bras : immobilisé {_n(a['hold'] / 20)} s et {m} des dégâts")
    elif k == "rain":
        s = (f"Marks the ground under you, and {_n(a['hit'] / 20)} s later it strikes there: {m} damage within {_n(a['r'])} blocks. Step out of the circle" if en else
             f"Marque le sol sous tes pieds, et {_n(a['hit'] / 20)} s plus tard frappe à cet endroit : {m} des dégâts à {_n(a['r'])} blocs. Sors du cercle")
    elif k == "trail":
        s = (f"Leaves a patch {_n(a['r'])} blocks wide for {_n(a['dur'] / 20)} s at its feet" if en else
             f"Laisse une flaque de {_n(a['r'])} blocs pendant {_n(a['dur'] / 20)} s à ses pieds")
        after = after.replace(", then ", " that inflicts ").replace(", puis ", " qui inflige ") if after else after
    elif k == "dash":
        s = (f"Charges in a straight line through you, {m} damage and knocked aside" if en else
             f"Charge en ligne droite à travers toi, {m} des dégâts et projeté sur le côté")
    elif k == "quake":
        s = (f"Sends {a['n']} shockwaves rolling out to {_n(a['r'])} blocks, {m} damage each. Jump to clear them" if en else
             f"Envoie {a['n']} ondes de choc jusqu'à {_n(a['r'])} blocs, {m} des dégâts chacune. Saute pour les éviter")
    elif k == "summon":
        from content import MOBS
        nm = next(x for x in MOBS if x["id"] == a["summon"])["en" if en else "fr"]
        s = (f"Calls {a['count']} {nm}{'s' if a['count'] > 1 and not nm.endswith('s') else ''} to its side" if en else
             f"Appelle {a['count']} {nm} à ses côtés")
    elif k == "ward":
        bits = [(EFFECT_EN if en else EFFECT_FR)[e] + ROMAN[lv] + f" {_n(t / 20)} s" for e, t, lv in a["self"]]
        if a.get("heal"):
            bits.append((f"heals {_pct(a['heal'])} of its health" if en else f"regagne {_pct(a['heal'])} de sa vie"))
        s = ("Braces itself: " if en else "Se protège : ") + ", ".join(bits)
    elif k == "roar":
        s = (f"Lets out a cry that reaches {_n(a['r'])} blocks" if en else f"Pousse un cri qui porte à {_n(a['r'])} blocs")
        after = after.replace(", then ", ": ").replace(", puis ", " : ") if after else after
    else:
        s = k
    if k == "grab" and a.get("heal"):
        s += (f", and it heals {_pct(a['heal'])} of its health" if en else f", et elle regagne {_pct(a['heal'])} de sa vie")
    out = s + after + "."
    if not en:
        import re
        out = re.sub(r"(\d)\.(\d)", r"\1,\2", out)
        out = re.sub(r"(\d)%", "\\1\u202f%", out)
    return out


def check():
    from content import MOBS
    ids = {m["id"] for m in MOBS}
    assert ids == set(A), (ids ^ set(A))
    names = [a[1] for v in A.values() for a in v]
    assert len(names) == len(set(names)), "attack names must be unique"
    for mid, lst in A.items():
        elite = next(m for m in MOBS if m["id"] == mid)["elite"]
        assert len(lst) == (4 if elite else 3), (mid, len(lst))
    return sum(len(v) for v in A.values())


def anim_seed(a):
    return zlib.crc32(a["id"].encode())


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    print(check(), "attacks")
    for mid in ("sporeling", "executioner"):
        for a in full(mid):
            print(a["en"], "|", describe(a, "en"))
            print("   ", a["fr"], "|", describe(a, "fr"))
