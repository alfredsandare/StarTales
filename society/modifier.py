

# Modifier is a modifier global for a civilization
class Modifier:
    def __init__(self, name, base_value, affects: list[str] = None, 
                 affected_by: list[str] = None):

        self.name = name
        self.value = base_value
        self.affects = affects
        self.affected_by = affected_by

    def __str__(self):
        return f"{self.name}: {self.value}"


# LocalModifier is a modifier that is applied to a specific cb or species
class LocalModifier(Modifier):
    def __init__(self, name, base_value, place_type, place, 
                 affects: list[str] = None, affected_by: list[str] = None):

        super().__init__(name, base_value, affects, affected_by)
        self.place_type = place_type  # 'cb' or 'species'
        self.place = place  # species id or cb id
