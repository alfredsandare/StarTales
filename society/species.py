import pygame

CHARACTERISTICS = ['intelligence', 'physical_strength', 'unruliness']
CHARACTERISTICS_NAMES = {
    'intelligence': 'Intelligence',
    'physical_strength': 'Physical Strength',
    'unruliness': 'Unruliness'
}

ENVIRONMENTS = ['land', 'sea', 'air']
ENVIRONMENTS_NAMES = {
    'land': 'Land',
    'sea': 'Sea',
    'air': 'Air'
}


class Species:
    def __init__(self, 
                 name: str, 
                 characteristics: dict[str, int], 
                 portrait: pygame.Surface,
                 environment: str,
                 habitat_preferences: dict[str, any]):

        self.name = name

        # characteristics are on a scale of 0-10
        # valid characteristics are:
        # - intelligence
        # - physical_strength
        # - unruliness
        self.characteristics = characteristics

        self.portrait = portrait

        # 'land', 'sea', or 'air'
        self.environment = environment

        # a dictionary of habitat preferences
        #
        self.habitat_preferences = habitat_preferences
