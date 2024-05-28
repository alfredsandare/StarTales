import math
import pygame
from physics.celestial_body import CelestialBody
from physics.planetary_body import PlanetaryBody
from physics.star import Star
from util import check_rect_overlap, multiply_vector, set_value_in_boundaries
from PhoenixGUI.util import sum_two_vectors, get_font
import data.consts as consts
from PhoenixGUI.hitbox import Hitbox

MAX_CB_SIZE_HARD_LIMIT = 400
NAMEPLATE_Y_OFFSET = 10  # amount of pixels between cb and nameplate
NAMEPLATE_SIZE = (120, 20)
SPACE_BETWEEN_NAMEPLATES = 5

class StarSystem:
    def __init__(self, name: str, star: Star, planetary_bodies: dict[str, PlanetaryBody]):
        self.name = name
        self.planetary_bodies = planetary_bodies
        self.star = star
        self.allow_zoom_in = True
        self.allow_zoom_out = True
        self.selected_cb_id = None

    def render_and_draw(self, screen, camera_pos, zoom, font_name,
                        nameplate_image) -> list[tuple[str, Hitbox]]:

        self.allow_zoom_in = True
        self.allow_zoom_out = True

        cb_sizes = [self.star.size, 
                    *(pb.size for pb in self.planetary_bodies.values())]
        
        cb_pixel_sizes = [self._get_cb_pixel_size(size, zoom) for size in cb_sizes]
        cb_pixel_sizes = self._adjust_sizes(cb_pixel_sizes, zoom)

        if max(cb_pixel_sizes) < 10:
            self.allow_zoom_out = False

        positions = {}
        nameplate_positions = {}

        positions[self.star.id] = self._get_base_pos(screen.get_size(), 
                                                     camera_pos, zoom)
        
        nameplate_offset = (0, cb_pixel_sizes[0]/2+NAMEPLATE_Y_OFFSET)
        nameplate_positions[self.star.id] = sum_two_vectors(positions[self.star.id],
                                                            nameplate_offset)

        size = cb_pixel_sizes[0]
        self._draw_object(screen, self.star, positions[self.star.id], size)

        borders = (*sum_two_vectors(positions[self.star.id], (-size/2, -size/2)),
                   *sum_two_vectors(positions[self.star.id], (size/2, size/2)))
        hitboxes = [(self.star.id, Hitbox(*borders))]

        for i, pb in enumerate(self.planetary_bodies.values()):
            host_pos = positions[pb.orbital_host]

            sma_in_pixels = pb.sma * zoom

            vop = pb.visual_orbit_progress
            planet_pos = (sma_in_pixels * math.cos(2 * math.pi * vop),
                          -1 * sma_in_pixels * math.sin(2 * math.pi * vop))
            
            pos = sum_two_vectors(host_pos, planet_pos)
            size = cb_pixel_sizes[i+1]
            
            pygame.draw.circle(screen, (100, 100, 100), host_pos, 
                               int(sma_in_pixels), 1)
            
            self._draw_object(screen, pb, pos, size)

            positions[pb.id] = pos
            
            nameplate_offset = (0, cb_pixel_sizes[i+1]/2+NAMEPLATE_Y_OFFSET)
            nameplate_positions[pb.id] = sum_two_vectors(pos, nameplate_offset)

            borders = (*sum_two_vectors(pos, (-size/2, -size/2)), 
                       *sum_two_vectors(pos, (size/2, size/2)))
            hitboxes.append((pb.id, Hitbox(*borders)))

        self._resolve_nameplate_overlaps(nameplate_positions)
        hitboxes.extend(self._draw_nameplates(screen, nameplate_positions, 
                                              font_name, nameplate_image))
        
        return hitboxes

    def _resolve_nameplate_overlaps(self, nameplate_positions):
        for id1, pos1 in nameplate_positions.items():
            for id2, pos2 in nameplate_positions.items():
                if id1 != id2 and check_rect_overlap(*pos1, *NAMEPLATE_SIZE, 
                                                     *pos2, *NAMEPLATE_SIZE):

                    offset = NAMEPLATE_SIZE[1]+SPACE_BETWEEN_NAMEPLATES
                    nameplate_positions[id2] = sum_two_vectors(pos1, (0, offset))
                    self._resolve_nameplate_overlaps(nameplate_positions)

    def _draw_nameplates(self, screen, positions, font_name, 
                         nameplate_image) -> list[tuple[str, Hitbox]]:

        path = "\\".join(__file__.split("\\")[:-2]) + "\\data\\fonts\\"
        font = get_font(path, font_name, 18)

        hitboxes = []

        for cb in self.get_all_cbs():
            pos = sum_two_vectors(positions[cb.id], (-NAMEPLATE_SIZE[0]/2, 0))
            screen.blit(nameplate_image, pos)
            hitboxes.append((cb.id, Hitbox(*pos, *sum_two_vectors(pos, NAMEPLATE_SIZE))))

            text = font.render(cb.name, True, (255, 255, 255))
            pos = sum_two_vectors(positions[cb.id], (-text.get_width()/2, 1))
            screen.blit(text, pos)

        return hitboxes
    
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

        smas_in_pixels = [cb.sma * zoom for cb in self.planetary_bodies.values()]
        smallest_sma_diff = self._find_smallest_sma_diff(smas_in_pixels)

        MAX_SIZE_DIVIDENT = 4
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
    
    def get_all_cbs(self) -> list[CelestialBody]:
        # returns a list of all celestial bodies in the system
        return [self.star, *self.planetary_bodies.values()]
    
    def get_all_cbs_dict(self) -> dict[str, CelestialBody]:
        # returns a dict of all celestial bodies in the system
        cbs = {id_: cb for id_, cb in self.planetary_bodies.items()}
        cbs[self.star.id] = self.star
        return cbs

    def get_pbs_list(self) -> list[PlanetaryBody]:
        return list(self.planetary_bodies.values())

    def get_child_pbs(self, host_id) -> list[PlanetaryBody]:
        pbs = [pb for pb in self.planetary_bodies.values() 
               if pb.orbital_host == host_id]

        pbs.sort(key=lambda pb: pb.sma)

        return pbs

    def get_camera_pos(self):
        if self.selected_cb_id is None:
            return

        selected_cb = self.get_all_cbs_dict()[self.selected_cb_id]

        pos = [0, 0]
        if selected_cb.type == "star":
            return pos

        vop = selected_cb.visual_orbit_progress
        pos = [selected_cb.sma * math.cos(2 * math.pi * vop),
               -1 * selected_cb.sma * math.sin(2 * math.pi * vop)]

        if selected_cb.orbital_host == self.star.id:
            return pos

        # now the selected cb must be a moon
        host = self.planetary_bodies[selected_cb.orbital_host]
        vop = host.visual_orbit_progress
        host_pos = [host.sma * math.cos(2 * math.pi * vop),
                    -1 * host.sma * math.sin(2 * math.pi * vop)]

        return sum_two_vectors(pos, host_pos)
