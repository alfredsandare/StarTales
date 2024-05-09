import pygame

class CelestialBody:
    def __init__(self, visual):
        self.visual = visual

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.visual.draw(screen, pos, size)
