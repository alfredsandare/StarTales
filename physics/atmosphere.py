# Thickness is the atmospheric pressure at the surface in kPa.
# Use the calculator in utils to calculate total amount of units.

# Gases are nitrogen, oxygen, carbon-dioxide, methane

class Atmosphere:
    def __init__(self, composition: dict[str: int]):
        self.composition = composition

    def get_composition_sum(self):
        return sum(self.composition.values())

    def get_thickness(self, tb_size):
        return self.get_composition_sum() / tb_size**2

    def get_composition_shares(self) -> dict[str, float]:
        return {key: value/self.get_composition_sum() 
                for key, value in self.composition.items()}
