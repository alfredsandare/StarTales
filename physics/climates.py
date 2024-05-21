import math


class Climate:
    def __init__(self, name: str, image: str, is_fluid: bool, temperature: float, toxic: bool):
        self.name = name
        self.image = image

        # These factors are only used for calculating cost of changes a district's climate.
        self.is_fluid = is_fluid  # whether or not this district is covered in a fluid (such as water or methane).
        self.temperature = temperature  # scale between 0 and 1.
        self.toxic = toxic  # whether or not this district is toxic to life

    def get_switch_cost(self, to):
        cost = 10

        if self.is_fluid != to.is_fluid:
            cost += 5

        cost += 5 * math.abs(self.temperature - to.temperature)

        if self.toxic != to.toxic:
            cost += 5

        return cost


WATER_OCEAN = Climate("Water Ocean", "ocean1", True, 0.3, False)
RAINFOREST = Climate("Rainforest", "forest1", False, 0.35, False)
ARID = Climate("Arid", "barren5", False, 0.4, False)
DESERT = Climate("Desert", "desert1", False, 0.5, False)
COLD_DESERT = Climate("Cold Desert", "barren3", False, 0.2, True)
TOXIC = Climate("Toxic", "molten1", False, 0.6, True)
