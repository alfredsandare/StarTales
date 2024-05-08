from planet_visual import PlanetVisual


class Planet:
    def __init__(self, visual):
        self.visual: PlanetVisual = visual

    def draw(self, screen):
        self.visual.draw(screen)
