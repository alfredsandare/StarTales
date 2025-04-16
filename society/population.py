from physics.atmosphere import Atmosphere
from physics.district import District
from society.species import Species
from society.sub_population import SubPopulation


# A population is located on a planet while a subpopulation is located in a district
class Population:
    def __init__(self, population_data: list[dict[str, float]], 
                 districts: list[District], 
                 atmosphere: Atmosphere,
                 jobs_data: dict):

        self.sub_populations = [SubPopulation(population_data[i], district) 
                                for i, district in enumerate(districts)]

        # atmosphere of the planet
        # this is dependency injection
        self.atmosphere = atmosphere

        # Keys are tuples of (species_id, job_id)
        self.jobs_data = jobs_data
        self.jobs = {}
        for species_id in self.get_species_ids():
            for job_id in self.jobs_data.keys():
                self.jobs[(species_id, job_id)] = 0

    def get_total_population(self) -> float:
        return sum([sub_population.get_total_population() 
                    for sub_population in self.sub_populations])

    def calculate_habitabilites(self, species: dict[str, Species], 
                                temperature: str):

        for sub_population in self.sub_populations:
            sub_population.calculate_habitabilites(species,
                                                   self.atmosphere,
                                                   temperature)

    def get_species_ids(self) -> list[str]:
        return list(set([species_id 
                         for sub_population in self.sub_populations 
                         for species_id in sub_population.get_species_ids()]))
    
    def get_sub_population(self, i: int) -> SubPopulation:
        return self.sub_populations[i]

    def get_total_population_dict(self) -> dict[str, float]:
        population_dict = {}
        for sub_population in self.sub_populations:
            for species_id, population in \
                sub_population.get_population_dict().items():

                if species_id in population_dict:
                    population_dict[species_id] += population
                else:
                    population_dict[species_id] = population

        return population_dict

    def get_species_population(self, species_id: str) -> float:
        return self.get_total_population_dict()[species_id]

    def calculate_jobs(self):
        total_population = self.get_total_population_dict()
        for species_id in self.get_species_ids():
            for job_id in self.jobs_data.keys():
                self.jobs[(species_id, job_id)] = \
                    total_population[species_id] / len(self.jobs_data.keys())

    def get_jobs_dict(self):
        return self.jobs

    def get_job_amount(self, species_id, job_id):
        return self.jobs[(species_id, job_id)]

    def get_total_jobs_production(self, resource_id) -> float:
        total_production = 0
        for job_id, job_data in self.jobs_data.items():
            if resource_id in job_data["produces"].keys():
                for species_id in self.get_species_ids():
                    total_production += job_data["produces"][resource_id] \
                        * self.jobs[(species_id, job_id)]

        return total_production
