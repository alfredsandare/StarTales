METERS_PER_AU = 149_597_870_700

# One year = 365.25 days.
# One week = 365.25 / 52 = 7.02404 days.
# Seconds in a week = 7.02404 * 86_400 
SECONDS_PER_WEEK = 606_877

MS_PER_IN_GAME_WEEK_STATES = [
    2000,
    1000,
    500,
    250,
    125
]

CELESTIAL_BODY_TYPES_NAMES = {
    "star": "Star", 
    "terrestrial_body": "Terrestrial World", 
    "gas_giant": "Gas Giant"
}

TEMPERATURES = ["extremely cold", "very cold", "cold", 
                "moderate", "hot", "very hot", "extremely hot"]

PLANETARY_RESOURCES = [
    "energy",
    "minerals"
]

PLANETARY_MODIFIERS = [
    "mining_capacity",
    "storage_capacity",
    "industrial_capacity",
    "housing"
]

RESOURCE_NAMES = {
    "energy": "Energy",
    "minerals": "Minerals",
    "mining_capacity": "Mining Capacity",
    "storage_capacity": "Storage Capacity",
    "industrial_capacity": "Industrial Capacity",
    "housing": "Housing"
}

TEXT_COLOR_ORANGE = "255 150 0"
TEXT_COLOR_GREEN = "0 255 0"
TEXT_COLOR_RED = "255 0 0"

# In units of Sun luminosity
STELLAR_LUM_LIMITS = {
    "O": (30000, 1000000),
    "B": (25, 30000),
    "A": (5, 25),
    "F": (1.1, 5),
    "G": (0.6, 1.1),
    "K": (0.08, 0.6),
    "M": (0, 0.08)
}

SUN_LUMINOSITY = 3.828 * 10**26

# Keys are lower limits.
TEMPERATURES_ADJECTIVES = {
    150: "Extremely hot",
    65: "Scorching",
    50: "Warm",
    41: "Lukewarm",
    35: "Moderate",
    31: "Chilly",
    25: "Cold",
    20: "Freezing",
    0: "Cryogenic"
}
