import pygame

class CelestialBody:
    def __init__(self, visual, size: float):
        self.visual = visual

        # float that should be rounded to three value figures.
        # Should be the value of the celestial body's radius divided by 400.
        self.size = size

        self.orbit_progress = 0  # 0 - 1. 

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.visual.draw(screen, pos, size)
