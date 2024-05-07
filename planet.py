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
        self.surface = self._render_total_surface()
        # self.surface = pygame.transform.scale(self.surface, (2*self.surface_size[0], 2*self.surface_size[1]))
        self.frames = self._render_frames()
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

        return surface
    
    def _render_cloud_surface(self):
        height_map = DS.diamond_square(shape=self.surface_size, 
                          min_height=1, 
                          max_height=100,
                          roughness=0.7,
                          as_ndarray=False)
        
        surface = pygame.Surface((314, 100), pygame.SRCALPHA)
        for x in range(self.surface_size[0]):
            for y in range(self.surface_size[1]):
                height = height_map[x][y]
                color = ()
                if height < 40:
                    color = (255, 255, 255, 255)
                else:
                    color = (255, 255, 255, 0)
                surface.set_at((x, y), color)

        return surface

    def _render_total_surface(self):
        surface = pygame.Surface(self.surface_size, pygame.SRCALPHA)
        surface.blit(self.planet_surface, (0, 0))
        surface.blit(self.cloud_surface, (0, 0))
        return surface
    
    def _render_frames(self):
        frames = []
        for i in range(self.surface_size[0]):

            upper_limit = 100 if i+100 < self.surface_size[0] else self.surface_size[0]-i

            print(i, upper_limit, upper_limit<100)

            frames.append(self.surface.subsurface((i, 0, upper_limit, self.surface_size[1])).copy())

            if upper_limit < 100:
                surface = self.surface.subsurface((0, 0, 100-upper_limit, self.surface_size[1])).copy()
                frames[-1].blit(surface, (upper_limit, 0))
                
        return frames
    
    def get_frame(self):
        self.current_frame_index += 1
        if self.current_frame_index == len(self.frames):
            self.current_frame_index = 0
        return self.frames[self.current_frame_index]

        
    def flatten_list(self, l):
        return [item for sublist in l for item in sublist]