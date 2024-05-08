import pygame
from planet_visual import PlanetVisual


class Planet:
    def __init__(self, visual):
        self.visual: PlanetVisual = visual

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.visual.draw(screen, pos, size)
