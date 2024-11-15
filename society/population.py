from physics.atmosphere import Atmosphere
from physics.district import District
from society.species import Species
from society.sub_population import SubPopulation


# A population is located on a planet while a subpopulation is located in a district
class Population:
    def __init__(self, population_data: list[dict[str, float]], 
                 districts: list[District], 
                 atmosphere: Atmosphere):

        self.sub_populations = [SubPopulation(population_data[i], district) 
                                for i, district in enumerate(districts)]

        # atmosphere of the planet
        # this is dependecy injection
        self.atmosphere = atmosphere

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
