import json
from PhoenixGUI import *
import pygame
from PhoenixGUI.util import update_pos_by_anchor, sum_two_vectors
from graphics.star_visual_style import StarVisualStyle
import graphics.star_visual_style as star_visual_style
from graphics.celestial_body_visual import CelestialBodyVisual
from graphics.terrestrial_body_style import TerrestrialBodyStyle
import graphics.terrestrial_body_style as terrestrial_body_style
from physics.star import Star
from physics.star_system import StarSystem
from physics.terrestrial_body import TerrestrialBody
from graphics import initialize_menues

PATH = __file__[:-7]


class Game:
    def __init__(self):
        self.frame_size = (1280, 720)
        self.screen = pygame.display.set_mode(self.frame_size)
        self.menu_handler = MenuHandler()

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, None)
        self.menu_handler.add_font_path(PATH + "data\\fonts\\")

        self.game_settings = self.load_game_settings()

        self.system_view_zoom = 200  # unit is pixels/AU
        self.system_view_pos = [0, 0]  # unit is AU

        self.view = "main"

        style = StarVisualStyle(star_visual_style.CLASS_G)
        visual = CelestialBodyVisual(style, 1/600)
        self.star = Star(visual, 1740, "Sun", "sun", "G2V")

        style = TerrestrialBodyStyle(*terrestrial_body_style.EARTHLY2)
        visual = CelestialBodyVisual(style, 1/500, 1/300)
        self.planet = TerrestrialBody(visual, 15.9, "Earth", "earth", "sun", False, 10, 24, 10, 1)

        style = TerrestrialBodyStyle(*terrestrial_body_style.GRAY)
        visual = CelestialBodyVisual(style, 1/500, 1/300)
        self.moon = TerrestrialBody(visual, 4.34, "Moon", "moon", "earth", False, 1, 24, 1, 0.00257)

        self.star_systems: dict[str, StarSystem] = {}
        self.star_systems["sol"] = StarSystem("sol", self.star, {"earth": self.planet, "moon": self.moon})

        self.current_star_system_key = "sol"
        self.current_star_system = self.star_systems["sol"]

    def main(self):
        self.menu_handler.menues["main_menu"].activate()
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))

            key_state = pygame.key.get_pressed()

            if self.view == "system":
                self.current_star_system.render_and_draw(self.screen,
                                                         self.system_view_pos,
                                                         self.system_view_zoom)
                self._update_star_system_pos(key_state)

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen, clock.get_time())

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                elif (event.type == pygame.KEYDOWN 
                      and event.key == pygame.K_ESCAPE
                      and self.view == "system"):
                    self.menu_handler.menues["escape_menu"].activate()

                elif event.type == pygame.MOUSEWHEEL:
                    SENSITIVITY = 0.1
                    change = self.system_view_zoom * event.y * SENSITIVITY

                    if change > 0 and self.current_star_system.allow_zoom_in:
                        self._adjust_system_position(
                            pygame.mouse.get_pos(),
                            self.system_view_zoom + change,
                            self.system_view_zoom)
                        self.system_view_zoom += change

                    elif change < 0 and self.current_star_system.allow_zoom_out:
                        self.system_view_zoom += change

            # self.planet.orbit_progress += 0.005

            pygame.display.flip()
            clock.tick(60)
            # print("FPS:", round(clock.get_fps()))

    def _adjust_system_position(self, mouse_pos, zoom, prev_zoom):
        # this functions makes adjusts the system_view_pos so that the cursor
        # has the same relative position as it had before zooming.

        # scale between -1 and 1
        mouse_pos = [2*mouse_pos[0]/self.frame_size[0]-1, 
                     2*mouse_pos[1]/self.frame_size[1]-1]
        
        # the length and height of the part of the system that is displayed on the screen
        old_window_size = [self.frame_size[0] / prev_zoom, 
                           self.frame_size[1] / prev_zoom]
        
        new_window_size = [self.frame_size[0] / zoom, 
                           self.frame_size[1] / zoom]
            
        camera_diff = [(old_window_size[0] - new_window_size[0])/2 * mouse_pos[0], 
                       (old_window_size[1] - new_window_size[1])/2 * mouse_pos[1]]
        
        self.system_view_pos[0] += camera_diff[0]
        self.system_view_pos[1] += camera_diff[1]

    def load_game_settings(self):
        with open(PATH + "data/game_settings.json") as file:
            return json.load(file)

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

                if obj["type"] == "button" and "command" in obj.keys():
                    loaded_data[menu_key]["objects"][obj_key]["command"] = \
                        (self.invoke_command, [obj["command"]], {})

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
        id_, *args = input_.split()

        if id_ == "frame_size":
            pos = update_pos_by_anchor([0, 0], self.frame_size, args[0])
            pos = [-1*pos[0] + int(args[1]), -1*pos[1] + int(args[2])]
            return pos

        elif id_ == "default_font":
            font = "rajdhani-regular"
            if "bold" in args:
                font = "rajdhani-bold"

            if "skip_quotes" in args:
                return font
            return f'"{font}"'
            
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

    def _switch_menues(self, to_activate, to_deactivate):
        if type(to_activate) in (tuple, list):
            for menu in to_activate:
                self.menu_handler.menues[menu].activate()
        else:
            self.menu_handler.menues[to_activate].activate()

        if type(to_deactivate) in (tuple, list):
            for menu in to_deactivate:
                self.menu_handler.menues[menu].deactivate()
        else:
            self.menu_handler.menues[to_deactivate].deactivate()

    def invoke_command(self, command):
        if command == "":
            return
        
        command, *args = command.split()

        if command == "quit":
            pygame.quit()
        
        elif command == "switch_menues":
            self._switch_menues(args[0], args[1])

        elif command == "deactivate_menu":
            self.menu_handler.menues[args[0]].deactivate()
            
        elif command == "activate_menu":
            self.menu_handler.menues[args[0]].activate()
            
        elif command == "enter_system_view":
            self.view = "system"
            self.menu_handler.menues["play_menu"].deactivate()
            self.menu_handler.menues["outliner"].activate()
            initialize_menues.outliner(self.menu_handler,
                                       self.current_star_system.get_all_cbs(),
                                       self.current_star_system.star.id,
                                       self.game_settings["show_moons_in_outliner"],
                                       self.get_values("default_font bold skip_quotes"),
                                       self.invoke_command)

        elif command == "exit_system_view":
            self.view = "main"
            self.menu_handler.deactivate_all_menues()
            self.menu_handler.menues["main_menu"].activate()

        elif command == "open_cb_menu":
            cb = self.current_star_system.celestial_bodies[args[0]]
            host_cb = self.current_star_system.celestial_bodies[cb.id]
            initialize_menues.cb_menu(self.menu_handler, 
                                      cb, 
                                      host_cb, 
                                      self.get_values("default_font bold skip_quotes"))
            self.menu_handler.menues["cb_menu"].activate()

    def _switch_system(self, new_system_key):
        self.current_star_system_key = new_system_key
        self.current_star_system = self.star_systems[new_system_key]

if __name__ == "__main__":
    game = Game()
    game.main()