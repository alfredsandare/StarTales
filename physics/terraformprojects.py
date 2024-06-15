class TerraformProject:
    def __init__(self, name, weekly_amount, total_time) -> None:
        self.name = name
        self.weekly_amount = weekly_amount
        self.total_time = total_time
        self.progress = 0


class AtmosphereChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, gas) -> None:
        super().__init__(name, weekly_amount, total_time)
        self.gas = gas


VALID_PROPERTIES = ["sma", "orbital_velocity", "day_length"]

class PropertyChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, property) -> None:
        super().__init__(name, weekly_amount, total_time)

        if property not in VALID_PROPERTIES:
            raise ValueError(f"Invalid property: {property}")
        self.property = property
