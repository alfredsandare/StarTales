import pygame
import graphics.planet_visual_generator as pvg

from graphics.planet_visual_style import PlanetVisualStyle


class PlanetVisual:
    def __init__(self, style, surface_speed, cloud_speed):
        self.style: PlanetVisualStyle = style

        self.surface_size = (314, 100)

        self.planet_surface = pvg.generate_planet_surface(self.surface_size, style)
        self.cloud_surface = pvg.generate_cloud_surface(self.surface_size, style)

        self.surface_speed = surface_speed
        self.cloud_speed = cloud_speed
        self.rotation_progress = 0  # 0 - 1
        self.cloud_rotation_progress = 0  # 0 - 1
        

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):

        diameter = self.surface_size[1]

        self.rotation_progress += self.surface_speed
        if self.rotation_progress > 1:
            self.rotation_progress -= 1

        self.cloud_rotation_progress += self.cloud_speed
        if self.cloud_rotation_progress > 1:
            self.cloud_rotation_progress -= 1

        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        surface.blit(self.planet_surface, (0, 0), 
                    (self.rotation_progress * self.surface_size[0], 0, 
                     self.surface_size[1], self.surface_size[1]))
        
        surface.blit(self.cloud_surface, (0, 0), 
                    (self.cloud_rotation_progress * self.surface_size[0], 0, 
                     self.surface_size[1], self.surface_size[1]))
        
        # Masks the part of the surface that is not in the circle
        mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255), 
                           (diameter//2, diameter//2), diameter//2)
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface = pygame.transform.scale(surface, (size, size))

        #mask = self.create_alpha_gradient(surface)
        #surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(surface, pos)

