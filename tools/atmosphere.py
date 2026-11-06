"""The light, fog, sky and floating particles of every world, as 26.3 environment attributes.

gen.py lays these over the biome of each world (biome attributes win over the dimension type's; World 8's season
timeline then tints them and swaps the particles). Only attributes that exist in 26.3 are used
(net.minecraft.world.attribute.EnvironmentAttributes): visual/fog_color, fog_start_distance, fog_end_distance,
sky_fog_end_distance, sky_color, cloud_color, cloud_height, sunrise_sunset_color, sky_light_color,
sky_light_factor, block_light_tint, ambient_light_color, water_fog_color, water_fog_start_distance,
water_fog_end_distance and ambient_particles (a list of {particle, probability}; the probability is tried for every
random block the client animates around the player, so it stays well under 0.01).
"""

NS = "matriochka"


def _p(pid, prob):
    ptype = pid if ":" in pid else f"{NS}:{pid}"
    return {"particle": {"type": ptype}, "probability": prob}


V = "minecraft:visual/"

# world: attributes laid over its biome
WORLD = {
    # spore haze: a green-gold murk that closes in at 90 blocks, spores drifting everywhere, sunlight filtered green
    1: {"fog_color": "#6a8a44", "fog_start_distance": 0.0, "fog_end_distance": 90.0, "sky_fog_end_distance": 120.0,
        "sky_color": "#7a9a56", "cloud_color": "#cc9ab870", "sky_light_color": "#e4f4c0", "block_light_tint": "#f0e8a0",
        "ambient_particles": [_p("spore", 0.006), _p("minecraft:spore_blossom_air", 0.0015)]},
    # heat: an orange haze, embers falling, ash in the air, every light runs hot
    2: {"fog_color": "#6a2c14", "fog_start_distance": 2.0, "fog_end_distance": 64.0, "sky_color": "#8a3a1a",
        "sky_light_color": "#ffc89a", "block_light_tint": "#ffa050", "ambient_light_color": "#2a1006",
        "ambient_particles": [_p("ember", 0.004), _p("minecraft:ash", 0.006)]},
    # cold stone: blue-grey fog, cold dust settling, lamps burn white-blue, chains glint in the dark; murky, but the
    # stone carries a cold light of its own and the fog is darker than it, so the halls read at a corridor's length
    3: {"fog_color": "#1a1d26", "fog_start_distance": 12.0, "fog_end_distance": 110.0, "block_light_tint": "#c4dcff",
        "ambient_light_color": "#4a5468", "ambient_particles": [_p("cold_dust", 0.004), _p("chain_glint", 0.0003)]},
    # the storm: slate sky, low dark clouds, a grey-blue light, sparks crackling in the air
    4: {"fog_color": "#8a9ab4", "fog_start_distance": 8.0, "fog_end_distance": 150.0, "sky_color": "#5a6a8c",
        "cloud_color": "#f04a5268", "cloud_height": 150.0, "sky_light_color": "#c0cce4", "sky_light_factor": 0.85,
        "sunrise_sunset_color": "#66ffe14a", "ambient_particles": [_p("storm_spark", 0.0006), _p("minecraft:white_ash", 0.002)]},
    # near black: no light of its own, and the fog swallows everything past a stone's throw; a lantern still reads
    # across a cavern (the fog only closes in from 4 blocks, gone by 30), its light running cold, rare motes and wisps
    5: {"fog_color": "#05050c", "fog_start_distance": 4.0, "fog_end_distance": 30.0, "block_light_tint": "#b4c0ff",
        "ambient_light_color": "#000000", "ambient_particles": [_p("deep_mote", 0.001), _p("shadow_wisp", 0.0005)]},
    # inverted pastel: a mint sky over pink fog, lilac clouds, mirror shards falling upward
    6: {"fog_color": "#f2cdee", "fog_start_distance": 10.0, "fog_end_distance": 180.0, "sky_color": "#aef0e6",
        "cloud_color": "#ffe8b4f2", "sunrise_sunset_color": "#cc40e0d0", "sky_light_color": "#ffe6ff",
        "block_light_tint": "#ffd0f8", "ambient_particles": [_p("mirror_shard", 0.0012), _p("minecraft:end_rod", 0.0002)]},
    # the deep sea: blue water fog closing in at 40 blocks, bubbles rising from everywhere
    7: {"water_fog_color": "#0a2c5e", "water_fog_start_distance": -6.0, "water_fog_end_distance": 40.0,
        "fog_color": "#1a4a7a", "sky_light_color": "#a8d8ff", "block_light_tint": "#a8f0ff",
        "ambient_particles": [_p("bubble", 0.004), _p("minecraft:underwater", 0.004)]},
    # the seasons: the timeline (SEASONS) tints this light and changes the particles every two minutes
    8: {"fog_color": "#d8c890", "fog_start_distance": 12.0, "fog_end_distance": 160.0, "sky_light_color": "#fff4dc"},
    # rust haze: a red-brown dust hanging in the air, grit falling off the moving ground
    9: {"fog_color": "#8a5440", "fog_start_distance": 6.0, "fog_end_distance": 110.0, "sky_color": "#b07a62",
        "cloud_color": "#ccc09080", "sky_light_color": "#ffd8c0", "sunrise_sunset_color": "#99ff7040",
        "ambient_particles": [_p("rust_mote", 0.005), _p("grit", 0.0008)]},
    # the workshop: warm lamp light, honey haze, wool fluff and thread scraps floating down
    10: {"fog_color": "#d8b884", "fog_start_distance": 16.0, "fog_end_distance": 170.0, "sky_color": "#ecd4a4",
         "cloud_color": "#ccfff0d0", "sky_light_color": "#fff0d0", "block_light_tint": "#ffc070", "ambient_light_color": "#1a1008",
         "ambient_particles": [_p("fluff", 0.004), _p("thread_scrap", 0.0006)]},
    # World 0, the smallest doll: lantern light on red lacquer, gold dust in the air. A warm red dusk, never a wall:
    # the lacquer glows on its own (well above the Nether's ambient, or it sinks into the haze) and the haze closes in
    # from 12 blocks to 112, so the inside of the doll reads at a normal distance
    11: {"fog_color": "#2c0e08", "fog_start_distance": 12.0, "fog_end_distance": 112.0, "block_light_tint": "#ffb060",
         "ambient_light_color": "#b8805a", "ambient_particles": [_p("gold_mote", 0.002)]},
}


def biome(n):
    """The environment attributes of world n's biome (11 is World 0)."""
    return {V + k: v for k, v in WORLD.get(n, {}).items()}


# World 8: one season every 2400 game ticks, on the matriochka:seasons clock kept in step with the game time
# (rules/HastenedClock.java). Light and fog are multiplied by the season's tint; particles cross-fade.
SEASON_TICKS = 2400
SEASONS = [  # (sky light tint, fog tint, particles)
    ("#ffe8f0", "#ffe0e8", [_p("petal", 0.004)]),
    ("#fff4c8", "#fff0c0", [_p("pollen", 0.004)]),
    ("#ffcc98", "#ffc890", [_p("autumn_leaf", 0.004)]),
    ("#d8e6ff", "#e4ecff", [_p("snowflake", 0.006)]),
]


def season_timeline():
    period = SEASON_TICKS * len(SEASONS)
    tracks = {V + "sky_light_color": [], V + "fog_color": [], V + "ambient_particles": []}
    for i, (light, fog, parts) in enumerate(SEASONS):
        for t in (i * SEASON_TICKS + 200, (i + 1) * SEASON_TICKS - 200):
            tracks[V + "sky_light_color"].append({"ticks": t, "value": light})
            tracks[V + "fog_color"].append({"ticks": t, "value": fog})
            tracks[V + "ambient_particles"].append({"ticks": t, "value": parts})
    return {"clock": f"{NS}:seasons", "period_ticks": period, "tracks": {
        V + "sky_light_color": {"modifier": "multiply", "keyframes": tracks[V + "sky_light_color"]},
        V + "fog_color": {"modifier": "multiply", "keyframes": tracks[V + "fog_color"]},
        V + "ambient_particles": {"keyframes": tracks[V + "ambient_particles"]},
    }}
