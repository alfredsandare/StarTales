from graphics.celestial_body_visual import CelestialBodyVisual
from physics.planetary_body import PlanetaryBody


class GasGiant(PlanetaryBody):
    def __init__(self,
                 visual: CelestialBodyVisual,
                 size: float,
                 name: str,
                 id: str,
                 star_system_id: str,
                 orbital_host: str,
                 is_tidally_locked: bool,
                 orbital_velocity: float,  # m/s
                 sma: float,
                 owner: str = None):
        
        super().__init__(visual,
                         size,
                         name,
                         id,
                         star_system_id,
                         orbital_host,
                         is_tidally_locked,
                         orbital_velocity,
                         sma,
                         owner)

        self.type = "gas_giant"
