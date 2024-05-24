import pygame
import graphics.celestial_body_visual_generator as cbvg


class CelestialBodyVisual:
    def __init__(self, type_, style):
        self.type_ = type_
        self.style = style

        self.surface_speed = 1/600
        self.cloud_speed = 1.5 * self.surface_speed

        self.surface_size = (314, 100)

        self.planet_surface = None
        self.cloud_surface = None

        if self.type_ == "terrestrial":
            self.planet_surface = cbvg.generate_planet_surface(self.surface_size, style)
            self.cloud_surface = None
            if self.cloud_speed is not None:
                self.cloud_surface = cbvg.generate_cloud_surface(self.surface_size, style)

        elif self.type_ == "star":
            self.planet_surface = cbvg.generate_star_surface(self.surface_size, style)

        elif self.type_ == "gas_giant":
            self.planet_surface = cbvg.generate_gas_giant_surface(self.surface_size, style)

        self.rotation_progress = 0  # 0 - 1
        self.cloud_rotation_progress = 0  # 0 - 1
        
    def get_surface(self, size: int, rotation_progress: float = 0, cloud_rotation_progress: float = 0):

        diameter = self.surface_size[1]
        
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        surface.blit(self.planet_surface, (0, 0), 
                    (rotation_progress * self.surface_size[0], 0, 
                     self.surface_size[1], self.surface_size[1]))
        
        if self.cloud_surface is not None:
            surface.blit(self.cloud_surface, (0, 0), 
                         (cloud_rotation_progress * self.surface_size[0], 0, 
                         self.surface_size[1], self.surface_size[1]))
        
        surface = pygame.transform.scale(surface, (size, size))
        
        # Masks the part of the surface that is not in the circle
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255), 
                           (size//2, size//2), size//2)
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        #mask = self.create_alpha_gradient(surface)
        #surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return surface

    def draw(self, screen: pygame.Surface, pos: tuple[int, int], size: int):
        self.rotation_progress += self.surface_speed
        if self.rotation_progress > 1:
            self.rotation_progress -= 1

        if self.cloud_surface is not None:
            self.cloud_rotation_progress += self.cloud_speed
            if self.cloud_rotation_progress > 1:
                self.cloud_rotation_progress -= 1

        surface = self.get_surface(size, self.rotation_progress, 
                                   self.cloud_rotation_progress)

        pos = [pos[0]-size/2, pos[1]-size/2]
        screen.blit(surface, pos)
