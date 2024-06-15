from physics.celestial_body import CelestialBody
from physics.terrestrial_body import TerrestrialBody


class TerraformProject:
    def __init__(self, name, weekly_amount, total_time) -> None:
        self.name = name
        self.weekly_amount = weekly_amount
        self.total_time = total_time
        self.progress = 0

    def apply(self, cb: CelestialBody) -> bool:
        self.progress += 1
        if self.progress >= self.total_time:
            return True
        return False


class AtmosphereChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, gas) -> None:
        super().__init__(name, weekly_amount, total_time)
        self.gas = gas

    def apply(self, tb: TerrestrialBody) -> bool:
        tb.atmosphere.composition[self.gas] += self.weekly_amount
        return super().apply(tb)


class PropertyChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, property) -> None:
        super().__init__(name, weekly_amount, total_time)
        self.property = property

        self.VALID_PROPERTIES = ["sma", "orbital_velocity", "day_length"]

    def apply(self, cb: CelestialBody) -> bool:
        property = getattr(cb, self.property)
        property += self.weekly_amount

        return super().apply(cb)
