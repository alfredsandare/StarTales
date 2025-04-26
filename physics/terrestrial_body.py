import math
from data.consts import METERS_PER_AU, SB_CONSTANT
from graphics.celestial_body_visual import CelestialBodyVisual
from physics.atmosphere import GASES_GREENHOUSE_CONSTS, Atmosphere, GASES
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
                         owner),

        self.day_length = day_length
        self.gravity = gravity

        self.type = "terrestrial_body"

        self.districts = districts
        self.atmosphere = atmosphere
        self.population = population
        self.temperature = 0

        self.atmosphere.tb_size = self.size

    def get_total_population(self):
        return self.population.get_total_population()

    def is_settled(self) -> bool:
        return self.get_total_population() > 0

    def get_all_buildings_dict(self) -> dict:
        # Returns a dict with (building_template_id, building_level) as keys
        # and the (amount of every such building, base_name) as values
        all_buildings = {}
        for district in self.districts:
            for building in district.buildings:
                key = (building.building_template_id, building.level)
                if key in all_buildings.keys():
                    all_buildings[key][0] += 1
                else:
                    all_buildings[key] = [1, building.base_name]

        # Sort by alphabetical order on the template ids
        sorted_keys = sorted(all_buildings, key=lambda k: k[0])
        return {key: all_buildings[key] for key in sorted_keys}

    def calculate_temperature(self, host_lum, sma):

        # Table of values, how this scale works
        # Temperature in celsius, temperature in this scale
        #  -60  23
        #  -23  31
        #   14  38
        # ~500 330

        ALBEDO = 0.3  # Constant
        SCALE = 0.2
        OFFSET = 100
        GREENHOUSE_BASE_CONST = 0.3

        # Formula for planetary equilibrium temperature
        equilibrium_temp = ((host_lum*(1-ALBEDO))
                            /(16*math.pi*SB_CONSTANT*(sma*METERS_PER_AU)**2))**0.25
        temperature = SCALE * (equilibrium_temp - OFFSET)
        temperature = temperature if temperature > 0 else 0

        for gas, share in self.atmosphere.get_composition_shares().items():
            temperature += (share * self.atmosphere.get_thickness())**0.5 \
                * GASES_GREENHOUSE_CONSTS[gas] * GREENHOUSE_BASE_CONST

        self.temperature = temperature
