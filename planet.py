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
        cloud_surface = self._render_cloud_surface()

        self.frames = self._render_frames(self.planet_surface, cloud_surface)
        self.current_frame_index = 0
        
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
    
    def _render_frames(self, planet_surface, cloud_surface):
        diameter = self.surface_size[1]
        frames = []
        for i in range(self.surface_size[0]):

            upper_limit = diameter
            frame = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

            rect = (i, 0, upper_limit, diameter)
            frame.blit(planet_surface.subsurface(rect).copy(), (0, 0))

            rect = (math.floor(2*i), 0, upper_limit, diameter)
            frame.blit(cloud_surface.subsurface(rect).copy(), (0, 0))

            frames.append(frame)
                
        return frames
    
    def _repeat_surface(self, surface, num_of_blits):
        new_surface = pygame.Surface((num_of_blits*self.surface_size[0], self.surface_size[1]), pygame.SRCALPHA)

        for i in range(num_of_blits):
            new_surface.blit(surface, (i*self.surface_size[0], 0))

        return new_surface
    
    def get_frame(self, speed=1):
        self.current_frame_index += speed
        if self.current_frame_index >= len(self.frames):
            self.current_frame_index = 0
        return self.frames[math.floor(self.current_frame_index)]

    def flatten_list(self, l):
        return [item for sublist in l for item in sublist]