import math

from society.species import Species


class Climate:
    def __init__(self, name: str, image: str, is_fluid: bool, 
                 toxic: bool, main_fluid: str = None):
        self.name = name
        self.image = image

        # These factors are only used for calculating cost of changes a district's climate.
        self.is_fluid = is_fluid  # whether or not this district is covered in a fluid (such as water or methane).
        self.toxic = toxic  # whether or not this district is toxic to life
        self.main_fluid = main_fluid  # the main fluid in this district

    def __repr__(self) -> str:
        return self.name

    def get_switch_cost(self, to):
        cost = 10

        if self.is_fluid != to.is_fluid:
            cost += 5

        if self.toxic != to.toxic:
            cost += 5

        return cost

    def get_habitability_penalty(self, species: Species) -> float:
        penalty = 0

        if species.habitat_preferences["main_fluid"] != self.main_fluid:
            penalty += 0.5

        return penalty


WATER_OCEAN = Climate("Water Ocean", "ocean2", True, False, "water")
RAINFOREST = Climate("Rainforest", "forest1", False, False, "water")
ARID = Climate("Arid", "barren5", False, False, "water")
DESERT = Climate("Desert", "desert1", False, False, "water")
COLD_DESERT = Climate("Cold Desert", "barren3", False, True, "water")
TOXIC = Climate("Toxic", "molten1", False, True, "water")
