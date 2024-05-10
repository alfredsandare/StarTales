from celestial_body import CelestialBody


class TerrestrialBody(CelestialBody):
    def __init__(self,
                 visual,
                 size,
                 orbital_host,
                 tidally_locked,
                 orbital_velocity,
                 day_length,
                 gravity):
        
        super().__init__(visual, size)
        self.orbital_host = orbital_host
        self.tidally_locked = tidally_locked
        self.orbital_velocity = orbital_velocity
        self.day_length = day_length
        self.gravity = gravity
