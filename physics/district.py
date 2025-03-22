from physics.climates import Climate
from society.building import Building


class District:
    def __init__(self, climate: Climate, buildings: list[Building] = None):
        self.climate = climate
        self.buildings = [] if buildings is None else buildings
