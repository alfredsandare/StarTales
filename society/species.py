import pygame


class Species:
    def __init__(self, 
                 name: str, 
                 characteristics: dict[str, int], 
                 portrait: pygame.Surface,
                 environment: str):
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
