import math
from hkb_diamondsquare import DiamondSquare as DS
import pygame


class Planet:
    def __init__(self):
        self.planet_surface_color_limits = {
            50: (0, 0, 255),
            65: (0, 255, 0),
            100: (150, 150, 150)
        }

        self.surface_size = (314, 100)

        self.planet_surface = self._render_planet_surface()
        self.cloud_surface = self._render_cloud_surface()

        self.rotation_progress = 0  # 0 - 1
        self.cloud_rotation_progress = 0  # 0 - 1
        
    def _render_planet_surface(self):
        height_map = DS.diamond_square(shape=self.surface_size, 
                          min_height=1, 
                          max_height=100,
                          roughness=0.65,
                          as_ndarray=False)
        
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        for x in range(self.surface_size[0]):
            for y in range(self.surface_size[1]):
                height = height_map[x][y]
                color = ()
                for limit, color in self.planet_surface_color_limits.items():
                    if height <= limit:
                        color = color
                        break
                surface.set_at((x, y), color)

        return self._repeat_surface(surface, 2)
    
    def _render_cloud_surface(self):
        height_map = DS.diamond_square(shape=self.surface_size, 
                          min_height=1, 
                          max_height=100,
                          roughness=0.7,
                          as_ndarray=False)
        
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        for x in range(self.surface_size[0]):
            for y in range(self.surface_size[1]):
                height = height_map[x][y]
                color = ()
                if height < 40:
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 255, 255, 0)
                surface.set_at((x, y), color)

        return self._repeat_surface(surface, 3)

    def _repeat_surface(self, surface, num_of_blits):
        new_surface = pygame.Surface((num_of_blits*self.surface_size[0], self.surface_size[1]), pygame.SRCALPHA)

        for i in range(num_of_blits):
            new_surface.blit(surface, (i*self.surface_size[0], 0))

        return new_surface
    
    def draw(self, screen, speed, cloud_speed):

        diameter = self.surface_size[1]

        self.rotation_progress += speed
        if self.rotation_progress > 1:
            self.rotation_progress -= 1

        self.cloud_rotation_progress += cloud_speed
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
        pygame.draw.circle(mask, (255, 255, 255), (diameter//2, diameter//2), diameter//2)
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(surface, (0, 0))