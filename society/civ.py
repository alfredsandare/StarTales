# 'civ' is used as a shorthand for 'civilization'

from data.consts import PLANETARY_RESOURCES, PLANETARY_MODIFIERS, RESOURCE_NAMES
from physics.star_system import StarSystem
from physics.terrestrial_body import TerrestrialBody
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

        self.modifiers_handler = ModifiersHandler()
        self.create_all_modifiers()

    def __str__(self):
        return f"Civilization: {self.name}"

    def __repr__(self):
        return f"{self.name}"

    def create_all_modifiers(self):
        for job_id, job_data in self.jobs_data.items():
            for resource_id, amount in job_data["upkeep"].items():
                self.create_modifier_1100(job_id, resource_id, amount)
            for resource_id, amount in job_data["produces"].items():
                self.create_modifier_1103(job_id, resource_id, amount)

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

        # Planetary resources, 1300
        for resource in PLANETARY_RESOURCES:
            id_ = f"resource@{star_system_id}@{tb_id}@{resource}"
            modifier = Modifier(RESOURCE_NAMES[resource], 0, id=id_,
                                type_id=1300)
            self.modifiers_handler.add_modifier(modifier)

        # Buildings: 1200, 1201
        for district_id, district in enumerate(tb.districts):
            for building_id, building in enumerate(district.buildings):
                self.create_building_modifiers(star_system_id, tb_id,
                                               district_id, building_id)

        for species_id, job_id in tb.population.get_jobs_dict().keys():
            for resource_id in self.jobs_data[job_id]["upkeep"].keys():
                self.create_modifier_1101(star_system_id, tb, species_id,
                                          job_id, resource_id)
            for resource_id in self.jobs_data[job_id]["produces"].keys():
                self.create_modifier_1104(star_system_id, tb, species_id,
                                          job_id, resource_id)

        for resource_id in PLANETARY_RESOURCES:
            self.create_modifier_1102(star_system_id, tb, resource_id)
            self.create_modifier_1105(star_system_id, tb, resource_id)

        # Planetary modifiers, 14xx
        self.create_modifiers_14xx(star_system_id, tb_id)

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

        # Create upkeep modifiers, 1201
        for upkeep_id in building.get_upkeep_ids():
            id_ = f"building_upkeep@{star_system_id}@{tb_id}@" \
                f"{district_id}@{building_id}@{upkeep_id}"
            func = lambda uid=upkeep_id: building.get_upkeep(uid)
            name = f"{RESOURCE_NAMES[upkeep_id]}"

            affects = []
            if upkeep_id in PLANETARY_RESOURCES:
                affects = [(f"resource@{star_system_id}@{tb_id}@{upkeep_id}",
                            1, False)]
            else:  # Upkeep in PLANETARY_MODIFIERS
                affects = [(f"{upkeep_id}@{star_system_id}@{tb_id}", 1, False)]

            modifier = Modifier(name, 0, id=id_, get_base_value_func=func,
                                affects=affects, type_id=1201)
            self.modifiers_handler.add_modifier(modifier)
            building.upkeep_modifiers_ids.append(id_)

        # Create produce modifiers, 1200
        for produce_id in building.get_produce_ids():
            id_ = f"building_produce@{star_system_id}@{tb_id}@" \
                f"{district_id}@{building_id}@{produce_id}"
            func = lambda uid=produce_id: building.get_produce(uid)
            name = RESOURCE_NAMES[produce_id]

            affects = []
            if produce_id in PLANETARY_RESOURCES:
                affects = [(f"resource@{star_system_id}@{tb_id}@{produce_id}",
                            1, False)]
            else:  # Upkeep in PLANETARY_MODIFIERS
                affects = [(f"{produce_id}@{star_system_id}@{tb_id}", 1, False)]

            modifier = Modifier(name, 0, id=id_, get_base_value_func=func,
                                affects=affects, type_id=1200)
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

    def get_1100_and_1103_multiplier_func(self, job_id):
        return lambda id_, job_id=job_id: \
            self.star_systems[id_.split("@")[1]] \
            .get_all_cbs_dict()[id_.split("@")[2]] \
            .population.get_jobs_dict()[(id_.split("@")[3], job_id)]

    def create_modifier_1100(self, job_id, resource_id, amount):
        id_ = f"job_base_resource_upkeep@{job_id}@{resource_id}"
        name = f"{RESOURCE_NAMES[resource_id]} upkeep per " \
            f"{self.jobs_data[job_id]["name"]}"

        req = ["job_resource_upkeep", None, None, None, job_id, resource_id]
        get_ids_func = lambda req=req: \
            self.modifiers_handler.get_modifiers_ids(req)

        multiplier_func = self.get_1100_and_1103_multiplier_func(job_id)
        affects_generators = [(get_ids_func, multiplier_func, False)]
        modifier = Modifier(name, amount, id=id_, type_id=1100,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifier_1101(self, star_system_id, tb, species_id,
                             job_id, resource_id):
        id_ = f"job_species_resource_upkeep@{star_system_id}@{tb.id}" \
            f"@{species_id}@{job_id}@{resource_id}"
        name = f"{self.jobs_data[job_id]["name"]}" \
            f"{RESOURCE_NAMES[resource_id]} upkeep"

        req = ["resource_upkeep_from_jobs", star_system_id, tb.id, resource_id]
        get_ids_func = lambda req=req: \
            self.modifiers_handler.get_modifiers_ids(req)

        affects_generators = [(get_ids_func, 1, False)]
        modifier = Modifier(name, 0, id=id_, type_id=1101,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifier_1102(self, star_system_id, tb, resource_id):
        id_ = f"resource_upkeep_from_jobs@{star_system_id}@" \
            f"{tb.id}@{resource_id}"
        name = f"{RESOURCE_NAMES[resource_id]} upkeep from jobs"

        req1 = ["resource", star_system_id, tb.id, resource_id]  # Resources
        req2 = [resource_id, star_system_id, tb.id]  # Planetary modifiers
        get_ids_func = lambda req1=req1, req2=req2: \
            self.modifiers_handler.get_modifiers_ids(req1) \
            + self.modifiers_handler.get_modifiers_ids(req2)

        affects_generators = [(get_ids_func, -1, False)]
        modifier = Modifier(name, 0, id=id_, type_id=1102,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifier_1103(self, job_id, resource_id, amount):
        id_ = f"job_base_resource_production@{job_id}@{resource_id}"
        name = f"{RESOURCE_NAMES[resource_id]} output per " \
            f"{self.jobs_data[job_id]["name"]}"

        req = ["job_resource_production", None, None, None, job_id, resource_id]
        get_ids_func = lambda req=req: \
            self.modifiers_handler.get_modifiers_ids(req)

        multiplier_func = self.get_1100_and_1103_multiplier_func(job_id)
        affects_generators = [(get_ids_func, multiplier_func, False)]
        modifier = Modifier(name, amount, id=id_, type_id=1103,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifier_1104(self, star_system_id, tb, species_id,
                             job_id, resource_id):
        id_ = f"job_resource_production@{star_system_id}@{tb.id}@" \
            f"{species_id}@{job_id}@{resource_id}"
        name = f"{self.jobs_data[job_id]["name"]}" \
            f"{RESOURCE_NAMES[resource_id]} production"

        req = ["resource_production_from_jobs", star_system_id,
               tb.id, resource_id]
        get_ids_func = lambda req=req: \
            self.modifiers_handler.get_modifiers_ids(req)

        affects_generators = [(get_ids_func, 1, False)]
        modifier = Modifier(name, 0, id=id_, type_id=1104,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifier_1105(self, star_system_id, tb, resource_id):
        id_ = f"resource_production_from_jobs@{star_system_id}@" \
            f"{tb.id}@{resource_id}"
        name = f"{RESOURCE_NAMES[resource_id]} upkeep from jobs"

        req1 = ["resource", star_system_id, tb.id, resource_id]  # Resources
        req2 = [resource_id, star_system_id, tb.id]  # Planetary modifiers
        get_ids_func = lambda req1=req1, req2=req2: \
            self.modifiers_handler.get_modifiers_ids(req1) \
            + self.modifiers_handler.get_modifiers_ids(req2)

        affects_generators = [(get_ids_func, 1, False)]
        modifier = Modifier(name, 0, id=id_, type_id=1105,
                            affects_generators=affects_generators)
        self.modifiers_handler.add_modifier(modifier)

    def create_modifiers_14xx(self, star_system_id, tb_id):
        for modifier in PLANETARY_MODIFIERS:
            id_ = f"{modifier}@{star_system_id}@{tb_id}"
            name = RESOURCE_NAMES[modifier]
            modifier = Modifier(name, 0, id=id_)
            self.modifiers_handler.add_modifier(modifier)
