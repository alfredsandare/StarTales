from physics.celestial_body import CelestialBody


class TerrestrialBody(CelestialBody):
    def __init__(self,
                 visual,
                 size,
                 name,
                 id,
                 orbital_host,
                 is_tidally_locked,
                 orbital_velocity,  # m/s
                 day_length,  # seconds
                 gravity,
                 sma):  # sma = semi-major axis [AU]
        
        super().__init__(visual, size, name, id)
        self.orbital_host = orbital_host
        self.is_tidally_locked = is_tidally_locked
        self.orbital_velocity = orbital_velocity
        self.day_length = day_length
        self.gravity = gravity
        self.sma = sma
