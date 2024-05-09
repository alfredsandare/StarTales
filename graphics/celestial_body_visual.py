import pygame
import graphics.celestial_body_visual_generator as cbvg
from graphics.terrestrial_body_style import TerrestrialBodyStyle
from graphics.star_visual_style import StarVisualStyle


class CelestialBodyVisual:
    def __init__(self, style, surface_speed, cloud_speed=None):
        self.style = style

        self.surface_size = (314, 100)

        self.planet_surface = None
        self.cloud_surface = None

        if type(style) is TerrestrialBodyStyle:
            self.planet_surface = cbvg.generate_planet_surface(self.surface_size, style)
            self.cloud_surface = None
            if cloud_speed is not None:
                self.cloud_surface = cbvg.generate_cloud_surface(self.surface_size, style)

        elif type(style) is StarVisualStyle:
            self.planet_surface = cbvg.generate_star_surface(self.surface_size, style)

        # elif type(style) is 

        self.surface_speed = surface_speed
        self.cloud_speed = cloud_speed
        self.rotation_progress = 0  # 0 - 1
        self.cloud_rotation_progress = 0  # 0 - 1
        

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):

        diameter = self.surface_size[1]
        
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        self.rotation_progress += self.surface_speed
        if self.rotation_progress > 1:
            self.rotation_progress -= 1

        surface.blit(self.planet_surface, (0, 0), 
                    (self.rotation_progress * self.surface_size[0], 0, 
                     self.surface_size[1], self.surface_size[1]))
        
        if self.cloud_surface is not None:
            self.cloud_rotation_progress += self.cloud_speed
            if self.cloud_rotation_progress > 1:
                self.cloud_rotation_progress -= 1

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