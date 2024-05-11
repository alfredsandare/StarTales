import math
from star import Star
from util import multiply_vector
from PhoenixGUI.util import sum_two_vectors


class StarSystem:
    def __init__(self, name: str, star: Star, celestial_bodies: dict):
        self.name = name
        self.celestial_bodies = celestial_bodies
        self.star = star

    def render_and_draw(self, screen, camera_pos, zoom):
        self._render_object(self.star, screen, camera_pos, zoom)

        for cb in self.celestial_bodies.values():
            pos = multiply_vector(camera_pos, -1)
            pos[0] += cb.sma * math.cos(2 * math.pi * cb.orbit_progress)
            pos[1] -= cb.sma * math.sin(2 * math.pi * cb.orbit_progress)
            pos = multiply_vector(pos, zoom)
            pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))
            cb.draw(screen, pos, 100)
            
    def _render_object(self, obj, screen, camera_pos, zoom):
        pos = multiply_vector(camera_pos, -1)
        pos = multiply_vector(pos, zoom)
        pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))
        obj.draw(screen, pos, 100)