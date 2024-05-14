import math
from star import Star
from util import multiply_vector, set_value_in_boundaries
from PhoenixGUI.util import sum_two_vectors
import data.consts as consts
from PhoenixGUI.hitbox import Hitbox

MAX_CB_SIZE_HARD_LIMIT = 400

class StarSystem:
    def __init__(self, name: str, star: Star, celestial_bodies: dict):
        self.name = name
        self.celestial_bodies = celestial_bodies
        self.star = star
        self.allow_zoom_in = True
        self.allow_zoom_out = True

    def render_and_draw(self, screen, camera_pos, zoom):
        self.allow_zoom_in = True
        self.allow_zoom_out = True

        cb_sizes = [self.star.size, 
                    *(cb.size for cb in self.celestial_bodies.values())]
        
        cb_pixel_sizes = [self._get_cb_pixel_size(size, zoom) for size in cb_sizes]
        cb_pixel_sizes = self._adjust_sizes(cb_pixel_sizes, zoom)

        if max(cb_pixel_sizes) < 10:
            self.allow_zoom_out = False

        # pos can be declared here that the loop below uses as a base pos.

        base_pos = self._get_base_pos(screen.get_size(), camera_pos, zoom)

        size = cb_pixel_sizes[0]
        self._draw_object(screen, self.star, base_pos, size)

        for i, cb in enumerate(self.celestial_bodies.values()):
            planet_pos = (zoom * cb.sma * math.cos(2 * math.pi * cb.orbit_progress),
                          -1 * zoom * cb.sma * math.sin(2 * math.pi * cb.orbit_progress))
            
            pos = sum_two_vectors(base_pos, planet_pos)
            size = cb_pixel_sizes[i+1]
            self._draw_object(screen, cb, pos, size)

    def _draw_object(self, screen, obj, pos, size):
        obj.draw(screen, pos, size)

        screen_size = screen.get_size()
        screen_hitbox = Hitbox(-size/2, -size/2, 
                               screen_size[0]+size/2, screen_size[1]+size/2)
        
        if size == MAX_CB_SIZE_HARD_LIMIT and screen_hitbox.is_pos_inside(*pos):
            self.allow_zoom_in = False
            
    def _get_cb_pixel_size(self, size, zoom):
        radius_in_m = size * 400_000
        diameter_in_m = radius_in_m * 2
        diameter_in_au = diameter_in_m / consts.METERS_PER_AU
        diameter_in_pixels = diameter_in_au * zoom  # zoom has unit pixels/au

        return set_value_in_boundaries(diameter_in_pixels, 0, 400)
    
    def _adjust_sizes(self, sizes, zoom):
        # sizes here are in pixels
        max_size = set_value_in_boundaries(max(sizes), lower_boundary=1e-6)
        min_size = set_value_in_boundaries(min(sizes), lower_boundary=1e-5)

        # how much larger the largest is allowed to be than the smallest
        MAX_SIZE_QUOTIENT = 10
        size_quotient = set_value_in_boundaries(max_size/min_size, 
                                                upper_boundary=MAX_SIZE_QUOTIENT)

        exponent = math.log(size_quotient) / math.log(max_size/min_size)

        smas_in_pixels = [cb.sma * zoom for cb in self.celestial_bodies.values()]
        smallest_sma_diff = self._find_smallest_sma_diff(smas_in_pixels)

        MAX_SIZE_DIVIDENT = 2
        max_cb_size = smallest_sma_diff / MAX_SIZE_DIVIDENT

        size_factor = max_cb_size / max_size

        return [set_value_in_boundaries(size_factor * size ** exponent, 
                                        0, 
                                        MAX_CB_SIZE_HARD_LIMIT) 
                                        for size in sizes]

    def _find_smallest_sma_diff(self, smas):
        if len(smas) == 1:
            return smas[0]

        sorted_smas = sorted(smas)
        smallest_diff = sorted_smas[1] - sorted_smas[0]

        for i in range(1, len(sorted_smas) - 1):
            diff = sorted_smas[i+1] - sorted_smas[i]

            if diff < smallest_diff:
                smallest_diff = diff

        return smallest_diff
    
    def _get_base_pos(self, screen_size, camera_pos, zoom):
        pos = multiply_vector(camera_pos, -1)
        pos = multiply_vector(pos, zoom)
        return sum_two_vectors(pos, multiply_vector(screen_size, 0.5))