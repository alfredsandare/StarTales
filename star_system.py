import math
from star import Star
from util import multiply_vector, set_value_in_boundaries
from PhoenixGUI.util import sum_two_vectors
import data.consts as consts


class StarSystem:
    def __init__(self, name: str, star: Star, celestial_bodies: dict):
        self.name = name
        self.celestial_bodies = celestial_bodies
        self.star = star

    def render_and_draw(self, screen, camera_pos, zoom):
        cb_sizes = [self.star.size, *(cb.size for cb in self.celestial_bodies.values())]
        cb_pixel_sizes = [self._get_cb_pixel_size(size, zoom) for size in cb_sizes]
        cb_pixel_sizes = self._adjust_sizes(cb_pixel_sizes, zoom)

        pos = multiply_vector(camera_pos, -1)
        pos = multiply_vector(pos, zoom)
        pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))
        #size = self._get_cb_pixel_size(self.star.size, zoom)
        size = cb_pixel_sizes[0]
        self.star.draw(screen, pos, size)

        for i, cb in enumerate(self.celestial_bodies.values()):
            pos = multiply_vector(camera_pos, -1)
            pos[0] += cb.sma * math.cos(2 * math.pi * cb.orbit_progress)
            pos[1] -= cb.sma * math.sin(2 * math.pi * cb.orbit_progress)
            pos = multiply_vector(pos, zoom)
            pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))

            #size = self._get_cb_pixel_size(cb.size, zoom)
            size = cb_pixel_sizes[i+1]
            cb.draw(screen, pos, size)
            
    def _get_cb_pixel_size(self, size, zoom):
        radius_in_m = size * 400_000
        diameter_in_m = radius_in_m * 2
        diameter_in_au = diameter_in_m / consts.METERS_PER_AU
        diameter_in_pixels = diameter_in_au * zoom  # zoom has unit pixels/au

        SIZE_FACTOR = 1#1000
        size = diameter_in_pixels * SIZE_FACTOR

        return set_value_in_boundaries(size, 0, 400)
    
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

        MAX_SIZE_HARD_LIMIT = 400

        return [set_value_in_boundaries(size_factor * size ** exponent, 0, MAX_SIZE_HARD_LIMIT) for size in sizes]

    def _find_smallest_sma_diff(self, smas):
        if len(smas) == 1:
            return smas[0]

        # Sort the list
        sorted_smas = sorted(smas)

        # Initialize smallest difference to be the difference between the first two elements
        smallest_diff = sorted_smas[1] - sorted_smas[0]

        # Iterate over the sorted list
        for i in range(1, len(sorted_smas) - 1):
            # Calculate the difference between current and next element
            diff = sorted_smas[i+1] - sorted_smas[i]

            # If this difference is smaller than the current smallest difference, update smallest difference
            if diff < smallest_diff:
                smallest_diff = diff

        return smallest_diff