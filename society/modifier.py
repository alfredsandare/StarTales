# A modifier is a value in a civ. It can affect other values in the civ, and be affected by other values in the civ.

# Modifier is a modifier global for a civilization
class Modifier:
    def __init__(self, name, base_value, affects: list[list[str, float, bool]] = None, 
                 affected_by: list[str] = None):

        self.name = name
        self.base_value = base_value

        # list of tuples of the form (affected_modifier, multiplier, is_percentage)
        # if is_percentage is True, the value will be multiplied by the multiplier
        # if is_percentage is False, the value will be multiplied by the multiplier before added to the affected modifer
        self.affects = affects
        self.affected_by = affected_by if affected_by is not None else []

    def __str__(self):
        return f"{self.name}: {self.base_value}"
    
    def __repr__(self):
        return f"{self.name}: {self.base_value}"


# LocalModifier is a modifier that is local to a specific cb or species
class LocalModifier(Modifier):
    def __init__(self, name, base_value, place_type, place, 
                 affects: list[str] = None, affected_by: list[str] = None):

        super().__init__(name, base_value, affects, affected_by)
        self.place_type = place_type  # 'cb' or 'species'
        self.place = place  # species id or cb id
