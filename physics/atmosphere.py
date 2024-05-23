# Thickness is the atmospheric pressure at the surface in kPa.
# Use the calculator in utils to calculate total amount of units.

class Atmosphere:
    def __init__(self, composition: dict[str: int]):
        self.composition = composition

    def get_thickness(self, cb_size):
        return sum(self.composition.values()) / cb_size**2
