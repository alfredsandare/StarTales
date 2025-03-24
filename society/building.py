import json
from util import get_path_from_file_name


PATH = get_path_from_file_name(__file__)

class Building:
    def __init__(self, building_template_id, level=1):
        self.building_template_id = building_template_id
        self.base_name = ""
        self.level_names = []
        self.produces = {}
        self.upkeep = {}
        self.image_id = ""
        self.level = level

        with open(PATH + "data/buildings.json") as file:
            this_building_data: dict = json.load(file)[building_template_id]
            for key, item in this_building_data.items():
                setattr(self, key, item)

    def get_upkeep_ids(self) -> list[str]:
        return self.upkeep.keys()

    def get_upkeep(self, upkeep_id) -> float:
        base = self.upkeep[upkeep_id]["base"]
        level_multiplier = self.upkeep[upkeep_id]["level_multiplier"]
        return base * level_multiplier ** (self.level-1)

    def get_produce_ids(self) -> list[str]:
        return self.produces.keys()

    def get_produce(self, produce_id) -> float:
        base = self.produces[produce_id]["base"]
        level_multiplier = self.produces[produce_id]["level_multiplier"]
        return base * level_multiplier ** (self.level-1)
