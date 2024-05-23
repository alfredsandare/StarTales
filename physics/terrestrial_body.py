from graphics.celestial_body_visual import CelestialBodyVisual
from physics.atmosphere import Atmosphere
from physics.celestial_body import CelestialBody
from physics.district import Disctrict


class TerrestrialBody(CelestialBody):
    def __init__(self,
                 visual: CelestialBodyVisual,
                 size: float,
                 name: str,
                 id: str,
                 orbital_host: str,
                 is_tidally_locked: bool,
                 orbital_velocity: float,  # m/s
                 day_length: int,  # seconds
                 gravity: float,
                 sma: float,  # sma = semi-major axis [AU]
                 districts: list[Disctrict],
                 atmosphere: Atmosphere):
        
        super().__init__(visual, size, name, id)
        self.orbital_host = orbital_host
        self.is_tidally_locked = is_tidally_locked
        self.orbital_velocity = orbital_velocity
        self.day_length = day_length
        self.gravity = gravity
        self.sma = sma
        self.districts = districts
        self.atmosphere = atmosphere
