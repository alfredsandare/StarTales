# A modifier is a value in a civ. It can affect other values in the civ, and be affected by other values in the civ.

# Modifier is a modifier global for a civilization
class Modifier:
    def __init__(self, name, base_value, affects: list[list[str, float, bool]] = None, 
                 affected_by: list[str] = None, id: str = None, 
                 get_base_value_func: callable = None, is_base: bool = False):

        self.name = name
        self.base_value = base_value

        # list of tuples of the form (affected_modifier, multiplier, is_percentage)
        # if is_percentage is True, the value will be multiplied by the multiplier
        # if is_percentage is False, the value will be multiplied by the multiplier before added to the affected modifer
        self.affects = affects if affects is not None else []
        self.affected_by = affected_by if affected_by is not None else []
        self.id = id
        self.get_base_value_func = get_base_value_func
        self.is_base = is_base

        self.added_value = 0
        self.added_percentage = 0  # this is a fraction, not an actual percentage
        self.value = 0

    def __str__(self):
        return f"Global Modifier - id: {self.id}, name: {self.name}, value: {self.value}"
    
    def __repr__(self):
        return f"{self.name}: {self.value}"

    def calculate_value(self):
        if self.get_base_value_func is not None:
            self.base_value = self.get_base_value_func()

        self.value = (self.base_value + self.added_value) * (1 + self.added_percentage)

        # Reset the added values for the next calculation
        self.added_value = 0
        self.added_percentage = 0


# LocalModifier is a modifier that is local to a specific cb or species
class LocalModifier(Modifier):
    def __init__(self, name, base_value, place_type, place, 
                 affects: list[str] = None, affected_by: list[str] = None,
                 id=None, get_base_value_func: callable = None, 
                 is_base: bool = False):

        super().__init__(name, base_value, affects, affected_by, 
                         id, get_base_value_func, is_base)
        self.place_type = place_type  # 'cb' or 'species'
        self.place = place  # species id or cb id

    def __str__(self):
        return f"Local Modifier - id: {self.id}, name: {self.name}, value: {self.value}"
