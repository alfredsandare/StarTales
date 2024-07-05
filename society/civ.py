# 'civ' is used as a shorthand for 'civilization'

from physics.star_system import StarSystem
from physics.terrestrial_body import TerrestrialBody
from society.modifier import Modifier
from society.modifiers_handler import ModifiersHandler
from society.species import Species


class Civ:
    def __init__(self, name, star_systems: dict[str, StarSystem], 
                 species: dict[str, Species], 
                 owned_cb_ids: list[list[str, str]] = None):

        self.name = name

        # These are depency injected
        self.star_systems = star_systems
        self.species = species

        # list of tuples of the form (star_system_id, cb_id)
        self.owned_cb_ids = owned_cb_ids if owned_cb_ids is not None else []

        self.modifiers_handler = ModifiersHandler(self.star_systems, 
                                                  self.species, 
                                                  self.owned_cb_ids)
        self.create_all_modifiers()

    def __str__(self):
        return f"Civilization: {self.name}"

    def __repr__(self):
        return f"{self.name}"

    def create_all_modifiers(self):
        for (star_system_id, cb_id) in self.owned_cb_ids:
            cb = self.star_systems[star_system_id].get_all_cbs_dict()[cb_id]
            if isinstance(cb, TerrestrialBody) and cb.is_settled():
                self.create_settled_tb_modifiers(star_system_id, cb_id)

    def create_settled_tb_modifiers(self, star_system_id, tb_id):
        # Creates all the modifiers listed in docs/modifiers.md for a terrestrial body.

        tb: TerrestrialBody = self.star_systems[star_system_id].get_all_cbs_dict()[tb_id]

        for species_id in tb.population.get_species_ids():

            for i, sub_population in enumerate(tb.population.sub_populations):
                # Species District Habitability
                id_ = f"species_district_habitability@{star_system_id}@{tb_id}@{i}@{species_id}"
                func = lambda: sub_population.get_species_population(species_id)
                species_name = self.species[species_id].name

                modifier = Modifier(f"District {i} {species_name} Habitability", 0,
                                    id=id_, get_base_value_func=func)
                self.modifiers_handler.add_modifier(modifier)
