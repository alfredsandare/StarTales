import pygame

from graphics.celestial_body_visual import CelestialBodyVisual

class CelestialBody:
    def __init__(self, visual: CelestialBodyVisual, size: float, name: str, id: str):
        self.visual = visual

        # float that should be rounded to three value figures.
        # Should be the value of the celestial body's radius divided by 400.
        self.size = size
        self.name = name
        self.id = id

        self.orbit_progress = 0  # 0 - 1. 

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.visual.draw(screen, pos, size)