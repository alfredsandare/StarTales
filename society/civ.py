# 'civ' is used as a shorthand for 'civilization'

from society.modifiers_handler import ModifiersHandler


class Civ:
    def __init__(self, name):
        self.name = name
        self.total_population = 0
        self.modifiers_handler = ModifiersHandler()

    def __str__(self):
        return f"Civilization: {self.name}"
