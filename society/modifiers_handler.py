from collections import deque
import json
from society.modifier import LocalModifier, Modifier
from util import get_path_from_file_name

PATH = get_path_from_file_name(__file__)


class ModifiersHandler:
    def __init__(self):
        self.modifiers: dict[str, Modifier] = {}
        self._load_data()

    def _load_data(self):
        with open(f"{PATH}/data/modifiers.json", "r") as file:
            data = dict(json.load(file))

        for modifier_name, modifier_data in data.items():
            class_ = Modifier if modifier_data["type"] == "global" else LocalModifier
            del modifier_data["type"]
            self.modifiers[modifier_name] = class_(**modifier_data)

        self._add_affected_by()
        self.sort_modifiers()
        print()
        print(self.modifiers)
        print()

    def _add_affected_by(self):
        for key, modifier in self.modifiers.items():
            for affected in modifier.affects:
                affected_modifier = self.modifiers[affected[0]]
                # if affected[0] not in affected_modifier.affected_by:
                affected_modifier.affected_by.append(key)

    def sort_modifiers(self):
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
        pass
