from hkb_diamondsquare import DiamondSquare as DS
import pygame
import numpy as np

from graphics.planet_visual_style import PlanetVisualStyle


class PlanetVisual:
    def __init__(self, style, surface_speed, cloud_speed):
        self.style: PlanetVisualStyle = style

        self.surface_size = (314, 100)

        self.planet_surface = self._render_planet_surface()
        self.cloud_surface = self._render_cloud_surface()

        self.surface_speed = surface_speed
        self.cloud_speed = cloud_speed
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
                for limit, color in self.style.color_limits.items():
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
                    color = self.style.cloud_color
                else:
                    color = (0, 0, 0, 0)
                surface.set_at((x, y), color)

        return self._repeat_surface(surface, 3)

    def _repeat_surface(self, surface, num_of_blits):
        size = (num_of_blits*self.surface_size[0], self.surface_size[1])
        new_surface = pygame.Surface(size, pygame.SRCALPHA)

        for i in range(num_of_blits):
            new_surface.blit(surface, (i*self.surface_size[0], 0))

        return new_surface
    
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

    def create_alpha_gradient(self, surface):
        # Create a new array with the same shape as the surface's alpha channel
        alpha = np.zeros(surface.get_size(), np.uint8)

        # Create a gradient in the x and y directions
        gradient = np.repeat(np.linspace(0, 255, surface.get_width()), surface.get_height()).reshape(surface.get_size())

        # Apply the gradient to the alpha channel
        alpha[:, :] = gradient

        # Create a new surface with the alpha channel
        mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        mask.fill((255, 255, 255, 0))
        pygame.surfarray.pixels_alpha(mask)[:] = alpha

        return mask