# 'civ' is used as a shorthand for 'civilization'

from physics.star_system import StarSystem
from society.modifiers_handler import ModifiersHandler
from society.species import Species


class Civ:
    def __init__(self, name, star_systems: dict[str, StarSystem], species: dict[str, Species], 
                 owned_cb_ids: list[list[str, str]] = None):

        self.name = name

        # list of tuples of the form (star_system_id, cb_id)
        self.owned_cb_ids = owned_cb_ids if owned_cb_ids is not None else []

        self.modifiers_handler = ModifiersHandler(star_systems, species, owned_cb_ids)

    def __str__(self):
        return f"Civilization: {self.name}"
