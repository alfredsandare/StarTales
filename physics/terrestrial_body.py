from graphics.celestial_body_visual import CelestialBodyVisual
from physics.atmosphere import Atmosphere
from physics.district import District
from physics.planetary_body import PlanetaryBody


class TerrestrialBody(PlanetaryBody):
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
                 districts: list[District],
                 atmosphere: Atmosphere,
                 population: int = 0,
                 owner: str = None):
        
        super().__init__(visual, 
                         size, 
                         name, 
                         id,
                         orbital_host,
                         is_tidally_locked,
                         orbital_velocity,
                         sma,
                         owner),

        self.day_length = day_length
        self.gravity = gravity

        self.type = "terrestrial_body"

        self.districts = districts
        self.atmosphere = atmosphere
        self.population = population

    def get_total_population(self):
        return self.population