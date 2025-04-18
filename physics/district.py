from physics.climates import Climate
from society.building import Building


class District:
    def __init__(self, climate: Climate, buildings: list[Building] = None):
        self.climate = climate
        self.buildings = [] if buildings is None else buildings

    def create_building(self, building_template_id: str,
                        buildings_data: dict,level=1):
        building = Building(building_template_id, buildings_data, level=level)
        self.buildings.append(building)
