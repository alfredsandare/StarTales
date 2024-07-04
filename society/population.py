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
