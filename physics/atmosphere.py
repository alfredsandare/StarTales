# Earth's atmosphere's thickness is ~39, it consists of ~8k nitrogen and ~2k oxygen.
# Earth is the reference point, all other planets are assigned total amount of composition
# so that their thickness is correct relatively to Earth.

class Atmosphere:
    def __init__(self, composition: dict[str: int]):
        self.composition = composition

    def get_thickness(self, cb_size):
        return sum(self.composition.values()) / cb_size**2
