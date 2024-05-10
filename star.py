from celestial_body import CelestialBody


class Star(CelestialBody):
    def __init__(self, visual, size, star_class):
        super().__init__(visual, size)
        self.star_class = star_class