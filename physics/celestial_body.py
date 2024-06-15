import pygame

from graphics.celestial_body_visual import CelestialBodyVisual
from physics.terraformprojects import AtmosphereChange, PropertyChange, TerraformProject

class CelestialBody:
    def __init__(self, visual: CelestialBodyVisual, size: float, name: str, id: str):
        self.visual = visual

        # float that should be rounded to three value figures.
        # Should be the value of the celestial body's radius divided by 400.
        self.size = size
        self.name = name
        self.id = id

        # overridden in subclasses
        self.type = None

        self.terraform_projects: list[TerraformProject] = []

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.visual.draw(screen, pos, size)

    def apply_terraform_projects(self):
        deleted = 0
        for i, terraform_project in enumerate(self.terraform_projects):
            is_finished = self.apply_terraform_project(terraform_project)
            if is_finished:
                del self.terraform_projects[i-deleted]
                deleted += 1

    def apply_terraform_project(self, terraform_project) -> bool:
        if isinstance(terraform_project, AtmosphereChange):
            # self is TerrestrialBody
            self.atmosphere.composition[terraform_project.gas] += \
                terraform_project.weekly_amount

            if self.atmosphere.composition[terraform_project.gas] < 0:
                del self.atmosphere.composition[terraform_project.gas]
                return True
            
        elif isinstance(terraform_project, PropertyChange):
            property = getattr(self, terraform_project.property)
            new_value = property + terraform_project.weekly_amount
            setattr(self, terraform_project.property, new_value)

        terraform_project.progress += 1
        if terraform_project.progress >= terraform_project.total_time:
            return True
        return False
