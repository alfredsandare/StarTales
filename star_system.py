from star import Star
from util import multiply_vector
from PhoenixGUI.util import sum_two_vectors


class StarSystem:
    def __init__(self, name, star, planets):
        self.name = name
        self.planets = planets
        self.star = star

    def render_and_draw(self, screen, camera_pos, zoom):
        pos = multiply_vector(camera_pos, -1)
        print(pos, end="")
        pos = sum_two_vectors(pos, multiply_vector(screen.get_size(), 0.5))
        print(pos)
        self.star.draw(screen, pos, 100)