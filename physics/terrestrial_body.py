from graphics.celestial_body_visual import CelestialBodyVisual
from physics.atmosphere import Atmosphere
from physics.district import District
from physics.planetary_body import PlanetaryBody
from society.population import Population


class TerrestrialBody(PlanetaryBody):
    def __init__(self,
                 visual: CelestialBodyVisual,
                 size: float,
                 name: str,
                 id: str,
                 star_system_id: str,
                 orbital_host: str,
                 is_tidally_locked: bool,
                 orbital_velocity: float,  # m/s
                 day_length: int,  # seconds
                 gravity: float,
                 sma: float,  # sma = semi-major axis [AU]
                 districts: list[District],
                 atmosphere: Atmosphere,
                 population: Population,
                 owner: str = None,
                 temperature="moderate"):
        
        super().__init__(visual, 
                         size, 
                         name, 
                         id,
                         star_system_id,
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
        self.temperature = temperature

        self.atmosphere.tb_size = self.size

    def get_total_population(self):
        return self.population.get_total_population()

    def is_settled(self) -> bool:
        return self.get_total_population() > 0
