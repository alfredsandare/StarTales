import json
from PhoenixGUI import *
import pygame
from PhoenixGUI.util import update_pos_by_anchor
from graphics.star_visual_style import StarVisualStyle
import graphics.star_visual_style as star_visual_style
from celestial_body import CelestialBody
from graphics.celestial_body_visual import CelestialBodyVisual
from graphics.terrestrial_body_style import TerrestrialBodyStyle
import graphics.terrestrial_body_style as terrestrial_body_style
from star import Star
from star_system import StarSystem
from terrestrial_body import TerrestrialBody

PATH = __file__[:-7]


class Game:
    def __init__(self):
        self.frame_size = (800, 800)
        self.screen = pygame.display.set_mode(self.frame_size)
        self.menu_handler = MenuHandler()

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, None)
        self.menu_handler.add_font_path(PATH + "data\\fonts\\")

        self.system_view_zoom = 200  # unit is pixels/AU
        self.system_view_pos = [0, 0]  # unit is AU

        style = TerrestrialBodyStyle(*terrestrial_body_style.EARTHLY2)
        visual = CelestialBodyVisual(style, 1/500, 1/300)
        self.planet = TerrestrialBody(visual, 15.9, "Earth", "sun", False, 10, 24, 10, 1)

        style = StarVisualStyle(star_visual_style.CLASS_G)
        visual = CelestialBodyVisual(style, 1/600)
        self.star = Star(visual, 1740, "G2V")

        self.star_system = StarSystem("sol", self.star, {"earth": self.planet})

    def main(self):
        #self.menu_handler.menues["main_menu"].activate()
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            #self.screen.blit(self.planet.planet_surface, (0, 110))
            #self.planet.draw(self.screen, (300, 300), 200)

            self.star_system.render_and_draw(self.screen, 
                                             self.system_view_pos, 
                                             self.system_view_zoom)
            
            key_state = pygame.key.get_pressed()
            self._update_star_system_pos(key_state)

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen)

            for event in events:
                if event.type == pygame.MOUSEWHEEL:
                    SENSITIVITY = 0.1
                    change = self.system_view_zoom * event.y * SENSITIVITY
                    if ((change > 0 and self.star_system.allow_zoom_in)
                        or (change < 0 and self.star_system.allow_zoom_out)):
                        self.system_view_zoom += self.system_view_zoom * event.y * SENSITIVITY


            # self.planet.orbit_progress += 0.005

            pygame.display.flip()
            clock.tick(60)

    def load_menues_data(self):
        with open(PATH + "data/menues.json") as file:
            data = json.load(file)
            data = json.dumps(data)  # make it a string
            values = data.split('"@get ')

            final_data = values.pop(0)
            for value in values:
                split = value.split('@"')
                final_data += (str(self.get_values(split[0])) 
                               + ("" if len(split) == 1 else split[1]))

        loaded_data = json.loads(final_data)

        for menu_key, menu in loaded_data.items():
            for obj_key, obj in menu["objects"].items():
                if obj["type"] == "button" and "color_theme" in obj.keys():
                    loaded_data[menu_key]["objects"][obj_key].update( \
                        self._get_button_color_theme(obj["color_theme"]))
                    
                    del loaded_data[menu_key]["objects"][obj_key]["color_theme"]

        return loaded_data
    
    def _get_button_color_theme(self, theme):
        if theme == "default":
            return {
                "rect_color": [35, 43, 133],
                "rect_hover_color": [35, 43, 133],
                "rect_click_color": [27, 32, 99],
                "rect_outline_color": [255, 255, 255],
                "rect_outline_hover_color": [254, 180, 5],
                "rect_outline_click_color": [254, 180, 5]
            } 
        
        return {}

    def get_values(self, input_):
        id_ = input_.split()[0]
        args = input_.split()[1:]

        if id_ == "frame_size":
            pos = update_pos_by_anchor([0, 0], self.frame_size, args[0])
            pos = [-1*pos[0] + int(args[1]), -1*pos[1] + int(args[2])]
            return pos

        elif id_ == "default_font":
            if "bold" in args:
                return '"rajdhani-bold"'
            return '"rajdhani-regular"'
            
        return ""
    
    def _update_star_system_pos(self, key_state):
        MOVEMENT_SPEED = 5  # pixels per frame
        movement = MOVEMENT_SPEED / self.system_view_zoom
        if key_state[pygame.K_d]:
            self.system_view_pos[0] += movement
        if key_state[pygame.K_a]:
            self.system_view_pos[0] -= movement
        if key_state[pygame.K_s]:
            self.system_view_pos[1] += movement
        if key_state[pygame.K_w]:
            self.system_view_pos[1] -= movement

if __name__ == "__main__":
    game = Game()
    game.main()