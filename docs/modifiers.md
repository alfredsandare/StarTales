Woow, documentation.

Modifiers can be pretty incomprehensible I think, so here's how they work.

A modifier is a value in a civ, and modifiers can affect other modifiers, that's why they exist in the first place. For example, a planet can generate science gain every week, which affects the civ's total science gain each week. Perhaps the civ has some modifier that gives +10% science gain (a base, percentage modifier with a multiplication factor of 1.1), which will automatically be calculated.

Many values are not only a modifier, they also exist in other places in the code. For example population. Every TerrestrialBody has a Population object, which stores data about how many people of each species live there. But the civ that owns the planet also has modifiers for population, whose base values are retrieved from the tb's population. When values like science gain are retrieved every week, they are retrieved from the civ's ModifierHandler.

## List of modifiers

To keep track of all modifiers, I have listed them here. This is useful because when certain events occur (like settling a new planet), modifiers may need to be added or removed.

### Modifiers for every settled TerrestrialBody
- Species District Habitability. There should be one modifier per species per district per planet per star system. Id: `species_district_habitability@{star_system_id}@{tb_id}@{district_id}@{species_id}`

- Species Planet Happiness. There should be one modifier per species per planet per star system. Id: `species_tb_happiness@{star_system_id}@{tb_id}@{species_id}`

- Species District Population. There should be one modifier per species per district per planet per star system. Id: `species_tb_population@{star_system_id}@{tb_id}@{district_id}@{species_id}`. Affects: Species Planet Population, not percentage, factor 1.

- Species Planet Population. There should be one modifier per species per planet per star system. Id: `species_tb_population@{star_system_id}@{tb_id}@{species_id}`. Affects: Planet population, not percentage, factor 1.

- Planet Population. There should be one modifier per planet per star system. Id: `tb_population@{star_system_id}@{tb_id}`. Affects: Civ population, not percentage, factor 1.

- Planet Housing. The should be one modifier per planet per star system. Id: `tb_housing@{star_system_id}@{tb_id}`.

<!-- - Jobs for every species and job combination. That is, how many individuals of a species are working a job. Id: `jobs@{star_system_id}@{tb_id}@{species_id}@{job_id}`. Affects: Jobs resource production, not percentage, factor 1. -->

- Job-Species resource production. How much of a resource a job and species combination are producing. There should be one modifier per resource produced per job per species per tb. Id: `jobs@{star_system_id}@{tb_id}@{species_id}@{job_id}@{resource_id}`.

- Species resource production (from jobs). How much of a resource a species is producing

- Resource production from jobs, one modifier for every resource. `jobs_production@{star_system_id}@{tb_id}@{resource_id}`

#### Notes about jobs modifiers.
The main problem is that there may be base modifiers that affect a species job resource production, regardless of job, and then there may be modifiers that affect a job resource output, regardless of species

### Modifiers for every civ

- Civ Population. There should be one modifer per civ. Id: `civ_population`.

### Modifiers for every building

Resources are: `energy`, `mining_capacity`, `storage_capaity`, `production_capacity`, `housing`
A building only has the modifiers of the resources it produces and needs for upkeep.

- Upkeep. There should be one modifier per building per resource. Id: `building_upkeep@{star_system_id}@{tb_id}@{district_id}@{building_id}@{resource_id}`.

- Produce. There should be one modifier per building per resource. Id: `building_produce@{star_system_id}@{tb_id}@{district_id}@{building_id}@{product_id}`.
