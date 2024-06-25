class TerraformProject:
    def __init__(self, name, weekly_amount, total_time, icon) -> None:
        self.name = name
        self.weekly_amount = weekly_amount
        self.total_time = total_time
        self.progress = 0
        self.icon = icon


class AtmosphereChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, icon, gas) -> None:
        super().__init__(name, weekly_amount, total_time, icon)
        self.gas = gas


VALID_PROPERTIES = ["sma", "orbital_velocity", "day_length"]

class PropertyChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, icon, property) -> None:
        super().__init__(name, weekly_amount, total_time, icon)

        if property not in VALID_PROPERTIES:
            raise ValueError(f"Invalid property: {property}")
        self.property = property


# These projects are the ones displayed in available/active projects.
# However, in the backend, only the above classes are used.

PROJECTS = {
    "add_gas": {
        "name": "Add Gas",
        "class": AtmosphereChange,
        "window": "change_gas",
        "icon": "add_gas.jpeg"
    },
    "remove_gas": {
        "name": "Remove Gas",
        "class": AtmosphereChange,
        "window": "change_gas",
        "icon": "remove_gas.jpeg"
    },
    "change_day_length": {
        "name": "Change Day Length",
        "class": PropertyChange,
        "property": "day_length",
        "window": "change_property",
        "icon": "change_day_length.jpeg"
    },
    "change_orbital_velocity": {
        "name": "Change Orbital Velocity",
        "class": PropertyChange,
        "property": "orbital_velocity",
        "window": "change_property",
        "icon": "change_day_length.jpeg"
    },
    "change_sma": {
        "name": "Change Semi-Major Axis",
        "class": PropertyChange,
        "property": "sma",
        "window": "change_property",
        "icon": "change_day_length.jpeg"
    }
}
