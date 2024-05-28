from graphics.celestial_body_visual import CelestialBodyVisual
from physics.celestial_body import CelestialBody
from physics.planetary_body import PlanetaryBody


class GasGiant(PlanetaryBody):
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
                 sma: float):
        
        super().__init__(visual,
                         size,
                         name,
                         id,
                         orbital_host,
                         is_tidally_locked,
                         orbital_velocity,
                         day_length,
                         gravity,
                         sma)

        self.type = "gas_giant"
