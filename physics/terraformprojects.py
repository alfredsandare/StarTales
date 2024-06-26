from physics.atmosphere import GASES_NAMES
from util import round_to_significant_figures


class TerraformProject:
    def __init__(self, name, weekly_amount, total_time, icon) -> None:
        self.name = name
        self.weekly_amount = weekly_amount
        self.total_time = total_time
        self.progress = 0
        self.icon = icon

    def get_info_text(self) -> str:
        progress = round_to_significant_figures(100*self.progress/self.total_time,
                                                3, make_int=True, make_zero=True)
        weeks_left = int(self.total_time - self.progress)
        return f"{self.name}\n{progress}% completed, {weeks_left} weeks left"


class AtmosphereChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, icon, gas) -> None:
        super().__init__(name, weekly_amount, total_time, icon)
        self.gas = gas

    def get_info_text(self) -> str:
        return super().get_info_text() \
            + f"\n{self.weekly_amount} units of {GASES_NAMES[self.gas]} per week"


VALID_PROPERTIES = ["sma", "orbital_velocity", "day_length"]

# these are frontend units
PROPERTY_UNITS = {
    "sma": "AU",
    "orbital_velocity": "km/s",
    "day_length": "hours"
}


class PropertyChange(TerraformProject):
    def __init__(self, name, weekly_amount, total_time, icon, property) -> None:
        super().__init__(name, weekly_amount, total_time, icon)

        if property not in VALID_PROPERTIES:
            raise ValueError(f"Invalid property: {property}")
        self.property = property

    def get_info_text(self) -> str:
        base = super().get_info_text()
        amount = self.weekly_amount/get_amount_modifier(self.property)
        amount_text = round_to_significant_figures(amount, 3, make_int=True)
        return f"{base}\n{amount_text} {PROPERTY_UNITS[self.property]} per week"


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

def get_amount_modifier(property):
    # Used for converting frontend input to backend values.
    if property == "day_length":
        return 3600  # Convert hours to seconds
    elif property == "orbital_velocity":
        return 1000  # Convert km/s to m/s
    elif property == "sma":
        return 1  # Already in AU
