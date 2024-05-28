from physics.celestial_body import CelestialBody


class Star(CelestialBody):
    def __init__(self, visual, size, name, id, star_class):
        super().__init__(visual, size, name, id)
        self.star_class = star_class

        self.type = "star"
