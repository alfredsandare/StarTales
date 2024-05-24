from physics.gas_giant import GasGiant
from physics.star import Star
from physics.terrestrial_body import TerrestrialBody


METERS_PER_AU = 149_597_870_700

# One year = 365.25 days.
# One week = 365.35 / 52 = 7.02404 days.
# Seconds in a week = 7.02404 * 86_400 
SECONDS_PER_WEEK = 606_877


CELESTIAL_BODY_TYPES_NAMES = {
    Star: "Star", 
    TerrestrialBody: "Terrestrial World", 
    GasGiant: "Gas Giant"
}
