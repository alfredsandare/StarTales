from collections import deque
import json
from data.consts import TEXT_COLOR_GREEN, TEXT_COLOR_RED
from physics.star_system import StarSystem
from society.modifier import LocalModifier, Modifier
from society.species import Species
from util import get_path_from_file_name, round_and_add_suffix

PATH = get_path_from_file_name(__file__)


class ModifiersHandler:
    def __init__(self, star_systems: dict[str, StarSystem], 
                 species: dict[str, Species], 
                 owned_cb_ids: list[list[str, str]] = None):

        self.modifiers: dict[str, Modifier] = {}
        self._load_data(star_systems, species, owned_cb_ids)
        self.calculate_modifiers()

    def _load_data(self, star_systems: dict[str, StarSystem], 
                   species: dict[str, Species], 
                   owned_cb_ids: list[list[str, str]] = None):

        with open(f"{PATH}/data/modifiers.json", "r") as file:
            data = dict(json.load(file))

        for modifier_name, modifier_data in data.items():
            class_ = Modifier if modifier_data["type"] == "global" else LocalModifier
            del modifier_data["type"]
            self.modifiers[modifier_name] = class_(**modifier_data, id=modifier_name)

        self._add_local_cb_modifiers(star_systems, owned_cb_ids)
        self._add_local_species_modifiers(species)
        self._calculate_affected_by()

    def _calculate_affected_by(self):
        for key, modifier in self.modifiers.items():
            modifier.affected_by = []
            for affected in modifier.affects:
                affected_modifier = self.modifiers[affected[0]]
                # if affected[0] not in affected_modifier.affected_by:
                affected_modifier.affected_by.append(key)

    def _sort_modifiers(self):
        graph = {key: [] for key in self.modifiers.keys()}
        in_degree = {key: 0 for key in self.modifiers.keys()}

        # Build the graph and in-degree dictionary
        for modifier_name, modifier in self.modifiers.items():
            for affected in modifier.affects:
                affected_name = affected[0]
                graph[modifier_name].append(affected_name)
                in_degree[affected_name] += 1

        # Find all nodes with in-degree of 0
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        sorted_modifiers = []

        # Topological sort
        while queue:
            node = queue.popleft()
            sorted_modifiers.append(node)
            for affected in graph[node]:
                in_degree[affected] -= 1
                if in_degree[affected] == 0:
                    queue.append(affected)

        # Update self.modifiers to reflect the sorted order
        self.modifiers = {name: self.modifiers[name] for name in sorted_modifiers}

    def get_modifier(self, modifier_name: str) -> Modifier:
        return self.modifiers[modifier_name]
    
    def calculate_modifiers(self):
        for modifier in self.modifiers.values():
            modifier.calculate_affects()

        self._calculate_affected_by()
        self._sort_modifiers()

        for modifier in self.modifiers.values():
            modifier.calculate_value()

            for affected in modifier.affects:
                affected_id, multiplier, is_percentage, _ = affected
                affected_modifier = self.modifiers[affected_id]

                if is_percentage:
                    affected_modifier.added_percentage += modifier.value * multiplier
                else:
                    affected_modifier.added_value += modifier.value * multiplier

    def print_modifiers(self):
        for modifier in self.modifiers.values():
            print(modifier)

    def _add_local_cb_modifiers(self, star_systems: dict[str, StarSystem],
                                owned_cb_ids: list[list[str, str]]):

        '''
        Local tb modifiers are:
        - population
        '''

        for star_system_id, star_system in star_systems.items():
            for tb in star_system.get_all_tbs():
                if [star_system_id, tb.id] in owned_cb_ids:
                    id = f"{star_system_id}_{tb.id}_population"
                    self.modifiers[id] = \
                        LocalModifier("Population", tb.get_total_population(), "cb", 
                                      tb.id, affects=[["civ_population", 1, False]], id=id)

    def _add_local_species_modifiers(self, species: dict[str, Species]):
        pass

    def add_modifier(self, modifier: Modifier):
        self.modifiers[modifier.id] = modifier
        for affects in modifier.affects:
            self.modifiers[affects[0]].affected_by.append(modifier.id)

    def get_affected_by_text(self, modifier_id: str, positive_is_green=True):
        # If positive_is_green is True, positive affection will be in green and
        # negative affection in red. If False, vice versa.

        modifier = self.modifiers[modifier_id]
        base_value = round_and_add_suffix(modifier.base_value, 3)
        value = round_and_add_suffix(modifier.value, 3)
        text = f"{modifier.name}: {value}\n    Base: {base_value}\n"

        for affected_by_modifier_id in modifier.affected_by:
            affected_by_modifier = self.modifiers[affected_by_modifier_id]
            list_id = affected_by_modifier \
                .get_affect_modifier_list_id(modifier_id)
            affect = affected_by_modifier.value \
                * affected_by_modifier.affects[list_id][1]

            is_percentage = affected_by_modifier.affects[list_id][2]
            affect *= 100 if is_percentage else 1

            # Backslash is to not end the color zone.
            percentage_text = "\\%" if is_percentage else ""
            sign = "+" if affect > 0 else ""  # Minus sign is automatically included
            color = TEXT_COLOR_GREEN if not (positive_is_green ^ (affect>0)) \
                else TEXT_COLOR_RED
            text += f"    {affected_by_modifier.name}: %%{color}%{sign}" \
                f"{affect}{percentage_text}%\n"

        return text

    def get_modifiers_startswith(self, startswith: str):
        return {key: modifier for key, modifier in self.modifiers.items() \
                if key.startswith(startswith)}

    def get_modifiers_ids(self, req: list) -> list[str]:
        # req is a list of requirements. Each element must equal each element
        # in a modifier's id split by @. Put a None in req to indicate that
        # position does not matter.
        ids = []
        for id_ in self.modifiers.keys():
            split = id_.split("@")
            if len(split) > len(req):
                split = split[:len(req)]
            elif len(split) < len(req):
                continue

            if all([split==req or req==None for split, req in zip(split, req)]):
                ids.append(id_)

        return ids
