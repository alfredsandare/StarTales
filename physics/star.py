from data.consts import STELLAR_LUM_LIMITS, SUN_LUMINOSITY
from physics.celestial_body import CelestialBody


class Star(CelestialBody):
    def __init__(self, visual, size, name, id, star_system_id: str, star_class: str, owner=None):
        super().__init__(visual, size, name, id, star_system_id, owner)
        # Star class uses Harvard spectral classification
        self.star_class = star_class

        self.type = "star"

    def get_luminosity(self):
        spectral_class = self.star_class[0]
        sub_class = int(self.star_class[1])
        lower, upper = STELLAR_LUM_LIMITS[spectral_class]
        return SUN_LUMINOSITY * (upper - (upper-lower)*sub_class*0.1)
