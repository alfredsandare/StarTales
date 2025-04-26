from physics.atmosphere import Atmosphere
from physics.district import District
from data.consts import TEMPERATURES
from society.species import Species


# A subpopulation is located in one district while a population is located on a planet
class SubPopulation:
    def __init__(self, species_population: dict[str, float], 
                 district: District):

        # key: species name, value: amount of people
        self.species_population = species_population

        # district where this subpopulation is located
        # this is dependecy injection
        self.district = district

        self.habitabilites = None

    def __repr__(self):
        habitabilites_text = ", ".join([f"[{species_id}: {round(100*habitability)}%]" 
                                        for species_id, habitability in self.habitabilites.items()])
        return f"SubPopulation: {self.species_population}, District Climate: {self.district.climate}, Habitabilites: {habitabilites_text}"

    def get_total_population(self) -> float:
        return sum(self.species_population.values())

    def calculate_habitabilites(self, species: dict[str, Species], 
                                atmosphere: Atmosphere, 
                                temperature: float):

        self.habitabilites = {}

        for species_id in species.keys():
            habitability = 1

            habitability -= self.district.climate \
                .get_habitability_penalty(species[species_id])

            habitability -= atmosphere.get_habitability_penalty(species[species_id])

            pref_temp = species[species_id].habitat_preferences["temperature"]
            habitability -= 0.01 * abs(pref_temp - temperature)

            if habitability < 0:
                habitability = 0

            self.habitabilites[species_id] = habitability

    def get_species_ids(self) -> list[str]:
        return list(self.species_population.keys())

    def get_species_habitability(self, species_id: str) -> float:
        return self.habitabilites[species_id]

    def get_species_population(self, species_id: str) -> float:
        return self.species_population[species_id]
    
    def get_population_dict(self) -> dict[str, float]:
        return self.species_population
