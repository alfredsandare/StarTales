from physics.celestial_body import CelestialBody


class Star(CelestialBody):
    def __init__(self, visual, size, name, id, star_system_id: str, star_class, owner=None):
        super().__init__(visual, size, name, id, star_system_id, owner)
        self.star_class = star_class

        self.type = "star"
