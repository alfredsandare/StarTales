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
        pos = multiply_vector(camera_pos, -1)
        pos = multiply_vector(pos, zoom)
        pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))
        size = self._get_cb_size(self.star.size, zoom)
        self.star.draw(screen, pos, size)

        for cb in self.celestial_bodies.values():
            pos = multiply_vector(camera_pos, -1)
            pos[0] += cb.sma * math.cos(2 * math.pi * cb.orbit_progress)
            pos[1] -= cb.sma * math.sin(2 * math.pi * cb.orbit_progress)
            pos = multiply_vector(pos, zoom)
            pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))

            size = self._get_cb_size(cb.size, zoom)
            cb.draw(screen, pos, size)
            
    def _get_cb_size(self, size, zoom):
        radius_in_m = size * 400_000
        diameter_in_m = radius_in_m * 2
        diameter_in_au = diameter_in_m / consts.METERS_PER_AU
        diameter_in_pixels = diameter_in_au * zoom  # zoom has unit pixels/au

        SIZE_FACTOR = 1000
        size = diameter_in_pixels * SIZE_FACTOR

        return set_value_in_boundaries(size, 0, 400)