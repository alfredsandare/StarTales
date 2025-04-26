# Thickness is the atmospheric pressure at the surface in kPa.
# Use the calculator in utils to calculate total amount of units.

# Gases are nitrogen, oxygen, carbon-dioxide, methane

from society.species import Species


class Atmosphere:
    def __init__(self, composition: dict[str: int], tb_size: float):
        self.composition = composition
        self.tb_size = tb_size

        for gas in composition.keys():
            if gas not in GASES:
                raise ValueError(f"Gas {gas} not in composition.")

    def get_composition_sum(self):
        return sum(self.composition.values())

    def get_thickness(self):
        return self.get_composition_sum() / self.tb_size**2

    def get_composition_shares(self, use_all_gases=False) -> dict[str, float]:
        composition =  {key: value/self.get_composition_sum() 
                        for key, value in self.composition.items()}

        if use_all_gases:
            for gas in GASES:
                if gas not in composition:
                    composition[gas] = 0

        return composition

    def get_habitability_penalty(self, species: Species):
        penalty = 0

        thickness = self.get_thickness()
        pref = species.habitat_preferences['atmospheric_pressure']
        penalty += 0.4 * abs(pref - thickness) / max(thickness, pref)

        composition_shares = self.get_composition_shares(use_all_gases=True)
        atm_preferences: dict[str, float] = \
            species.habitat_preferences['atmospheric_composition']

        for gas_preference, value in atm_preferences.items():
            min_or_max, gas = gas_preference.split("_")
            if min_or_max == "min" and composition_shares[gas] < value:
                penalty += 0.1
            elif min_or_max == "max" and composition_shares[gas] > value:
                penalty += 0.1

        return penalty

GASES = [
    'nitrogen',
    'oxygen',
    'carbon-dioxide',
    'methane',
    "water_vapor"
]

GASES_NAMES = {
    'nitrogen': 'Nitrogen',
    'oxygen': 'Oxygen',
    'carbon-dioxide': 'Carbon Dioxide',
    'methane': 'Methane',
    "water_vapor": "Water Vapor"
}

GASES_GREENHOUSE_CONSTS = {
    'nitrogen': 1,
    'oxygen': 1,
    'carbon-dioxide': 10,
    'methane': 40,
    "water_vapor": 10
}
