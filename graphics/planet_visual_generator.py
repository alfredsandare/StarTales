import pygame
from hkb_diamondsquare import DiamondSquare as DS


def generate_planet_surface(surface_size, style):
    height_map = DS.diamond_square(shape=surface_size, 
                                   min_height=1, 
                                   max_height=100,
                                   roughness=0.65,
                                   as_ndarray=False)
    
    surface = pygame.Surface(surface_size, pygame.SRCALPHA)
    for x in range(surface_size[0]):
        for y in range(surface_size[1]):
            height = height_map[x][y]
            color = ()
            for limit, color in style.color_limits.items():
                if height <= limit:
                    color = color
                    break
            surface.set_at((x, y), color)

    return _repeat_surface(surface, 2, surface_size)

def generate_cloud_surface(surface_size, style):
    height_map = DS.diamond_square(shape=surface_size, 
                                   min_height=1, 
                                   max_height=100,
                                   roughness=0.7,
                                   as_ndarray=False)
    
    surface = pygame.Surface(surface_size, pygame.SRCALPHA)
    for x in range(surface_size[0]):
        for y in range(surface_size[1]):
            height = height_map[x][y]
            color = ()
            if height < 40:
                color = style.cloud_color
            else:
                color = (0, 0, 0, 0)
            surface.set_at((x, y), color)

    return _repeat_surface(surface, 3, surface_size)

def _repeat_surface(surface, num_of_blits, surface_size):
    size = (num_of_blits*surface_size[0], surface_size[1])
    new_surface = pygame.Surface(size, pygame.SRCALPHA)

    for i in range(num_of_blits):
        new_surface.blit(surface, (i*surface_size[0], 0))

    return new_surface


# def create_alpha_gradient(self, surface):
#     # Create a new array with the same shape as the surface's alpha channel
#     alpha = np.zeros(surface.get_size(), np.uint8)

#     # Create a gradient in the x and y directions
#     gradient = np.repeat(np.linspace(0, 255, surface.get_width()), surface.get_height()).reshape(surface.get_size())

#     # Apply the gradient to the alpha channel
#     alpha[:, :] = gradient

#     # Create a new surface with the alpha channel
#     mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
#     mask.fill((255, 255, 255, 0))
#     pygame.surfarray.pixels_alpha(mask)[:] = alpha

#     return mask