# 'civ' is used as a shorthand for 'civilization'

from data.consts import PLANETARY_RESOURCES, RESOURCE_NAMES
from physics.star_system import StarSystem
from physics.terrestrial_body import TerrestrialBody
from society.building import Building
from society.modifier import Modifier
from society.modifiers_handler import ModifiersHandler
from society.species import Species
from society.sub_population import SubPopulation


class Civ:
    def __init__(self, name, star_systems: dict[str, StarSystem], 
                 species: dict[str, Species],
                 buildings_data: dict,
                 jobs_data: dict,
                 owned_cb_ids: list[list[str, str]] = None):

        self.name = name

        # These are dependency injected
        self.star_systems = star_systems
        self.species: dict[str, Species] = species
        self.buildings_data = buildings_data
        self.jobs_data = jobs_data

        # list of tuples of the form (star_system_id, cb_id)
        self.owned_cb_ids = owned_cb_ids if owned_cb_ids is not None else []

        self.modifiers_handler = ModifiersHandler(self.star_systems, 
                                                  self.species, 
                                                  self.owned_cb_ids)
        self.create_all_modifiers()
        self.modifiers_handler.calculate_modifiers()

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

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]

        for species_id in tb.population.get_species_ids():
            for i, sub_population in enumerate(tb.population.sub_populations):
                # Species District Habitability
                id_ = f"species_district_habitability@{star_system_id}" \
                    f"@{tb_id}@{i}@{species_id}"
                func = lambda sp=sub_population: \
                    sp.get_species_habitability(species_id)
                species_name = self.species[species_id].name

                modifier = Modifier(f"District {i} {species_name} Habitability",
                                    0, id=id_, get_base_value_func=func)
                self.modifiers_handler.add_modifier(modifier)

        # Planetary resources
        for resource in PLANETARY_RESOURCES:
            id_ = f"{resource}@{star_system_id}@{tb_id}"
            modifier = Modifier(RESOURCE_NAMES[resource], 0, id=id_)
            self.modifiers_handler.add_modifier(modifier)

        for district_id, district in enumerate(tb.districts):
            for building_id, building in enumerate(district.buildings):
                self.create_building_modifiers(star_system_id, tb_id,
                                               district_id, building_id)

        # Amount of every species working a job
        for species_id, job_id in tb.population.get_jobs_dict().keys():
            id_ = f"jobs@{star_system_id}@{tb_id}@{species_id}@{job_id}"
            name = f"{self.species[species_id].name} {self.jobs_data[job_id]["name"]}"
            func = lambda p=tb.population, si=species_id, j=job_id: \
                p.get_job_amount(si, j)

            affects = []
            for resource_id, multiplier in self.jobs_data[job_id]["produces"].items():
                affected_id = f"jobs_production@{star_system_id}@{tb_id}@{resource_id}"
                affects.append((affected_id, multiplier, False))

            for resource_id, multiplier in self.jobs_data[job_id]["upkeep"].items():
                affected_id = f"jobs_upkeep@{star_system_id}@{tb_id}@{resource_id}"
                affects.append((affected_id, multiplier, False))

            modifier = Modifier(name, 0, id=id_, get_base_value_func=func)
            self.modifiers_handler.add_modifier(modifier)

        # Resource production and upkeep from jobs
        for resource_id in PLANETARY_RESOURCES:
            id_ = f"jobs_production@{star_system_id}@{tb_id}@{resource_id}"
            name = f"Jobs {RESOURCE_NAMES[resource_id]} Production"
            modifier = Modifier(name, 0, id=id_)
            self.modifiers_handler.add_modifier(modifier)

            id_ = f"jobs_upkeep@{star_system_id}@{tb_id}@{resource_id}"
            name = f"Jobs {RESOURCE_NAMES[resource_id]} Upkeep"
            modifier = Modifier(name, 0, id=id_)
            self.modifiers_handler.add_modifier(modifier)


    def time_tick(self):
        self.modifiers_handler.calculate_modifiers()

    def create_building_and_modifiers(self, building_template_id: str,
                                      star_system_id: str, tb_id: str,
                                      district_id: int, level=1):

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]
        tb.districts[district_id].create_building(building_template_id,
                                                  self.buildings_data,
                                                  level=level)
        building_id = len(tb.districts[district_id].buildings) - 1
        self.create_building_modifiers(star_system_id, tb_id, district_id,
                                       building_id)

    def create_building_modifiers(self, star_system_id: str, tb_id: str,
                                  district_id: int, building_id: int):

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]
        building = tb.districts[district_id].buildings[building_id]

        # Create upkeep modifiers
        for upkeep_id in building.get_upkeep_ids():
            id_ = f"building_upkeep@{star_system_id}@{tb_id}@" \
                f"{district_id}@{building_id}@{upkeep_id}"
            func = lambda uid=upkeep_id: building.get_upkeep(uid)
            name = f"{RESOURCE_NAMES[upkeep_id]}"
            affects = [(f"{upkeep_id}@{star_system_id}@{tb_id}", 1, False)]
            modifier = Modifier(name, 0, id=id_, get_base_value_func=func,
                                affects=affects)
            self.modifiers_handler.add_modifier(modifier)
            building.upkeep_modifiers_ids.append(id_)

        # Create produce modifiers
        for produce_id in building.get_produce_ids():
            id_ = f"building_produce@{star_system_id}@{tb_id}@" \
                f"{district_id}@{building_id}@{produce_id}"
            func = lambda uid=produce_id: building.get_produce(uid)
            name = RESOURCE_NAMES[produce_id]
            affects = [(f"{produce_id}@{star_system_id}@{tb_id}", 1, False)]
            modifier = Modifier(name, 0, id=id_, get_base_value_func=func,
                                affects=affects)
            self.modifiers_handler.add_modifier(modifier)
            building.produce_modifiers_ids.append(id_)

    def get_average_species_tb_habitability(self, star_system_id: str,
                                            tb_id: str, species_id: str):
        # Returns the average habitability of a species on a terrestrial body.
        # This is the average of all the districts' habitability
        # where this species is present.

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]
        habitability_sum = 0
        count = 0
        for i, sub_population in enumerate(tb.population.sub_populations):
            if species_id in sub_population.get_species_ids():

                modifier_id = f"species_district_habitability@"\
                    +f"{tb.star_system_id}@{tb.id}@{i}@{species_id}"

                habitability_sum += self.modifiers_handler.get_modifier(\
                    modifier_id).get_value()

                count += 1

        return habitability_sum / count if count > 0 else 0

    def get_total_average_species_tb_habitability(self, star_system_id: str,
                                                  tb_id: str):
        # Returns the average habitability of all species on a terrestrial body.
        # This accounts for the population of each species,
        # so a species with a larger population will have a
        # larger impact on the average.

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]

        if tb.population.get_total_population() == 0:
            return 0

        present_species_ids = tb.population.get_species_ids()
        averages = [self.get_average_species_tb_habitability(star_system_id,
                                                             tb_id, species_id)
                    * tb.population.get_species_population(species_id)
                    for species_id in present_species_ids]

        return sum(averages) / tb.population.get_total_population()

    def get_species_district_habitability(self, star_system_id: str, tb_id: str,
                                          district_id: int, species_id: str):
        # Returns the habitability of a species in a district

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]
        sub_population = tb.population.sub_populations[district_id]

        if species_id in sub_population.get_species_ids():

            modifier_id = f"species_district_habitability@"\
                +f"{tb.star_system_id}@{tb.id}@{district_id}@{species_id}"

            return self.modifiers_handler.get_modifier(modifier_id).get_value()

    def get_average_species_district_habitability(self, star_system_id: str,
                                                  tb_id: str, district_id: str):
        # Returns the average habitability of all species in a district

        tb: TerrestrialBody = self.star_systems[star_system_id] \
            .get_all_cbs_dict()[tb_id]
        sub_population: SubPopulation = \
            tb.population.sub_populations[district_id]

        present_species_ids = sub_population.get_species_ids()
        habitabilities = [self.get_species_district_habitability(
                              star_system_id, tb_id, district_id, species_id)
                          * sub_population.get_species_population(species_id)
                          for species_id in present_species_ids]

        return sum(habitabilities) / sub_population.get_total_population()
