import json
import os
from PhoenixGUI import *
import pygame
from PhoenixGUI.util import update_pos_by_anchor
from data.consts import MS_PER_IN_GAME_WEEK_STATES
import graphics.star_visual_style as star_visual_style
from graphics.celestial_body_visual import CelestialBodyVisual
import graphics.terrestrial_body_style as terrestrial_body_style
from physics.atmosphere import Atmosphere
import physics.climates as climates
from physics.district import District
from physics.gas_giant import GasGiant
from physics.star import Star
from physics.star_system import StarSystem
from physics.terraformprojects import AtmosphereChange, PropertyChange
from physics.terrestrial_body import TerrestrialBody
from graphics import initialize_menues
from util import convert_weeks_to_years, is_valid_image
from graphics import gas_giant_visual_style

PATH = __file__[:-7]

pygame.init()


class Game:
    def __init__(self):
        self.frame_size = (1280, 720)
        self.screen = pygame.display.set_mode(self.frame_size)
        self.menu_handler = MenuHandler()
        self.menu_handler.set_scroll_strength_multiplier(8)
        
        self.images = self._get_images_in_directory(PATH+"graphics\\", PATH+"graphics\\")

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, self.images)
        self.menu_handler.add_font_path(PATH + "data\\fonts\\")

        self.game_settings = self.load_game_settings()

        self.view = "main"

        self.star_systems: dict[str, StarSystem] = {}

        self._load_star_system_data()

        self.current_star_system_key = "sol"
        self.current_star_system = self.star_systems["sol"]

        self.climate_images = self._get_climate_images()

        self.time = 104001  # number of weeks after year 0. 104000 weeks is 2000 years
        self.ms_per_in_game_week = 250
        self.game_time_since_last_time_tick = 0
        self.game_time_is_active = False

        self.menu_settings = {
            "atmosphere_menu_mode": "units",  # "percentage" or "units"
            "cb_menu_mode": "overview"  # "overview" or "terraforming"
        }

        self.cb_menu_cb_id = None

    def main(self):
        self.menu_handler.menues["main_menu"].activate()
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))

            key_state = pygame.key.get_pressed()

            hitboxes = {}

            if self.view == "system":
                self.current_star_system.update_camera_pos_by_cb_movement()

                hitboxes = self.current_star_system.render_and_draw(
                    self.screen,
                    self.get_values("default_font bold skip_quotes"),
                    self.images["other/planet_nameplate.png"]
                )
                self.current_star_system.update_camera_pos_by_key_state(key_state)

            self._perform_time_tick_logic(clock.get_time())
            self._perform_visual_orbit_progress_calculations(clock.get_fps())

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen, clock.get_time())

            for event in events:
                self._handle_event(event, hitboxes)
                

            pygame.display.flip()
            clock.tick(60)
            # print("FPS:", round(clock.get_fps()))

    def _time_tick(self):
        self.time += 1

        for star_system in self.star_systems.values():
            for pb in star_system.get_pbs_list():
                pb.orbit_progress += pb.get_progress_per_week()

                if pb.orbit_progress >= 1:
                    pb.orbit_progress -= 1
                    pb.visual_orbit_progress -= 1

            for cb in star_system.get_all_cbs():
                cb.apply_terraform_projects()

        self._update_time_menu_text()

    def _update_time_menu_text(self):
        self.menu_handler.menues["time_menu"].objects["time_text"] \
            .change_property("text", convert_weeks_to_years(self.time, format="date"))

    def _perform_time_tick_logic(self, time_per_tick):
        if self.game_time_is_active:
            self.game_time_since_last_time_tick += time_per_tick
            if self.game_time_since_last_time_tick >= self.ms_per_in_game_week:
                self._time_tick()
                self.game_time_since_last_time_tick -= self.ms_per_in_game_week
        else:
            self.game_time_since_last_time_tick = 0

    def _act_on_esc_press(self):
        order_of_menues = [
            "escape_menu",
            "cb_menu",
            "small_planet_menu"
        ]

        for menu_id in order_of_menues:
            if self.menu_handler.menues[menu_id].active:
                self.menu_handler.menues[menu_id].deactivate()
                if menu_id == "small_planet_menu":
                    self.current_star_system.selected_cb_id = None
                return

        self.menu_handler.menues["escape_menu"].activate()

    def _handle_event(self, event, hitboxes):
        if event.type == pygame.QUIT:
            pygame.quit()
            return

        elif (event.type == pygame.KEYDOWN 
              and event.key == pygame.K_ESCAPE
              and self.view == "system"):
            self._act_on_esc_press()

        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
              and self.view == "system"):
            self.invoke_command("change_time")

        elif event.type == pygame.MOUSEWHEEL and \
            not self.menu_handler.is_mouse_inside_menu():
            SENSITIVITY = 0.1
            zoom = self.current_star_system.zoom
            change = zoom * event.y * SENSITIVITY

            if change > 0 and self.current_star_system.allow_zoom_in:
                self.current_star_system.update_camera_pos_by_zoom(
                    pygame.mouse.get_pos(), zoom + change, 
                    zoom, self.frame_size)
                self.current_star_system.zoom += change

            elif change < 0 and self.current_star_system.allow_zoom_out:
                self.current_star_system.zoom += change

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 \
            and not self.menu_handler.is_mouse_inside_menu():
            for id, hitbox in hitboxes:
                if hitbox.is_pos_inside(*pygame.mouse.get_pos()):
                    self._open_small_planet_menu(id)
                    self.current_star_system.selected_cb_id = id
                    break

    def _perform_visual_orbit_progress_calculations(self, fps):
        time_speed_in_s = self.ms_per_in_game_week / 1000  # in seconds
        time_ticks_per_s = 1 / time_speed_in_s

        for pb in self.current_star_system.get_pbs_list():
            if pb.visual_orbit_progress < pb.orbit_progress:

                progress = pb.get_progress_per_week()

                progress_per_s = progress * time_ticks_per_s
                progress_per_frame = progress_per_s / fps

                pb.visual_orbit_progress += progress_per_frame

                if pb.visual_orbit_progress > pb.orbit_progress:
                    pb.orbit_progress = pb.visual_orbit_progress

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
                    
                if obj["type"] == "text_input" and "validity_check" in obj.keys():
                    validity_check = getattr(text_input.validity_check, 
                                             obj["validity_check"])
                    loaded_data[menu_key]["objects"][obj_key]["validity_check"] = \
                        validity_check

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
            for arg in args:
                self.menu_handler.menues[arg].deactivate()
            
        elif command == "activate_menu":
            for arg in args:
                self.menu_handler.menues[arg].activate()
            
        elif command == "enter_system_view":
            self.view = "system"
            self.menu_handler.menues["play_menu"].deactivate()
            self.menu_handler.menues["outliner"].activate()
            self.menu_handler.menues["outliner_scroll"].activate()
            self.menu_handler.menues["time_menu"].activate()
            initialize_menues.outliner(self.menu_handler,
                                       self.current_star_system.get_all_cbs(),
                                       self.current_star_system.star.id,
                                       self.game_settings["show_moons_in_outliner"],
                                       self.get_values("default_font bold skip_quotes"),
                                       self.invoke_command)

            self._update_time_menu_text()

        elif command == "exit_system_view":
            self.view = "main"
            self.menu_handler.deactivate_all_menues()
            self.menu_handler.menues["main_menu"].activate()

        elif command == "open_cb_menu":
            self.cb_menu_cb_id = args[0]
            self._init_cb_menu_wrapper()
            self.menu_handler.menues["cb_menu"].activate()
            self.menu_handler.menues["cb_submenu_moons"].activate()

        elif command == "change_time":
            time_button = self.menu_handler.menues["time_menu"].objects["time_button"]
            if self.game_time_is_active:
                time_button.change_property("image", self.images["buttons/play_icon.png"])
                time_button.change_property("hover_image", self.images["buttons/play_icon_hover.png"])
                time_button.change_property("click_image", self.images["buttons/play_icon_hover.png"])
            else:
                time_button.change_property("image", self.images["buttons/pause_icon.png"])
                time_button.change_property("hover_image", self.images["buttons/pause_icon_hover.png"])
                time_button.change_property("click_image", self.images["buttons/pause_icon_hover.png"])

            self.game_time_is_active = not self.game_time_is_active

        elif command == "increase_time_speed":
            state_index = MS_PER_IN_GAME_WEEK_STATES \
                .index(self.ms_per_in_game_week)
            
            if state_index < 4:
                self.ms_per_in_game_week = \
                    MS_PER_IN_GAME_WEEK_STATES[state_index + 1]
                
                self.menu_handler.menues["time_menu"].objects["time_speed_text"] \
                    .change_property("text", str(state_index + 2))
            
        elif command == "decrease_time_speed":
            state_index = MS_PER_IN_GAME_WEEK_STATES \
                .index(self.ms_per_in_game_week)

            if state_index > 0:
                self.ms_per_in_game_week = \
                    MS_PER_IN_GAME_WEEK_STATES[state_index - 1]
                
                self.menu_handler.menues["time_menu"].objects["time_speed_text"] \
                    .change_property("text", str(state_index))

        elif command == "deselect_cb":
            self.menu_handler.menues["small_planet_menu"].deactivate()
            self.current_star_system.selected_cb_id = None

        elif command == "open_cb_menu_from_small_planet_menu":
            self.invoke_command("open_cb_menu "
                                + self.current_star_system.selected_cb_id)
            
        elif command == "set_cb_menu_mode":
            self.menu_settings["cb_menu_mode"] = args[0]
            self._init_cb_menu_wrapper()

    def _switch_system(self, new_system_key):
        self.current_star_system_key = new_system_key
        self.current_star_system = self.star_systems[new_system_key]
        
    def _get_climate_images(self):
        IMAGE_SIZE = 70

        images = {}
        path = PATH+"graphics\\climates\\"

        os.chdir(path)
        files = os.listdir(os.getcwd())

        for file in files:
            image = pygame.image.load(path+file).convert_alpha()

            # crop it to make it a square
            size = image.get_size()
            surface = pygame.Surface((min(size), min(size)), pygame.SRCALPHA)
            surface.blit(image, (0, 0))

            surface = pygame.transform.scale(surface, (IMAGE_SIZE, IMAGE_SIZE))

            file_name = file.split(".")[0]
            images[file_name] = surface

        return images

    def _get_images_in_directory(self, path, original_path):
        os.chdir(path)
        files = os.listdir(os.getcwd())

        images = {}
        for file in files:
            path_here = path+file

            if not os.path.isfile(path_here):
                images.update(self._get_images_in_directory(path_here+"\\", original_path))
                continue

            if is_valid_image(path_here):
                relative_path = path_here[len(original_path):]
                id_ = "/".join(relative_path.split("\\"))
                images[id_] = pygame.image.load(path_here).convert_alpha()

        return images

    def _load_star_system_data(self):
        with open(PATH + "data/star_systems.json") as file:
            star_system_data = json.load(file)

            for id, star_system in star_system_data.items():

                style = getattr(star_visual_style, 
                                star_system["star"]["visual_style"])

                visual = CelestialBodyVisual("star", style)

                kwargs = {key: value for key, value in star_system["star"].items()
                          if key != "visual_style"}
                star = Star(visual, **kwargs)

                pbs = {}
                for pb_data in star_system["planetary_bodies"].values():
                    pbs[pb_data["id"]] = self._create_pb_from_data(pb_data)

                self.star_systems[id] = StarSystem(star_system["name"], star, pbs)

    def _create_pb_from_data(self, pb_data):
        if pb_data["type"] == "terrestrial_world":
            style = getattr(terrestrial_body_style, pb_data["visual_style"])
            
            visual = CelestialBodyVisual("terrestrial", style)

            blacklist = ["visual_style", "type", "districts", "atmosphere"]
            kwargs = {key: value for key, value in pb_data.items() 
                      if key not in blacklist}

            districts = [District(getattr(climates, district_type))
                         for district_type in pb_data["districts"]]

            atmosphere = Atmosphere(pb_data["atmosphere"])

            return TerrestrialBody(visual, **kwargs, 
                                   districts=districts, 
                                   atmosphere=atmosphere)

        elif pb_data["type"] == "gas_giant":
            style = getattr(gas_giant_visual_style, pb_data["visual_style"])

            visual = CelestialBodyVisual("gas_giant", style)

            blacklist = ["visual_style", "type"]
            kwargs = {key: value for key, value in pb_data.items() 
                      if key not in blacklist}

            return GasGiant(visual, **kwargs)

        raise Exception(f"Invalid pb type: {pb_data['type']}")
    
    def _open_small_planet_menu(self, id):
        self.menu_handler.menues["small_planet_menu"].activate()
        initialize_menues.small_planet_menu(self.menu_handler, id, 
                                            self.current_star_system)
        
    def _init_cb_menu_wrapper(self):
        cbs = self.current_star_system.get_all_cbs_dict()
        cb = cbs[self.cb_menu_cb_id]
        host_cb = None
        if not isinstance(cb, Star):
            host_cb = cbs[cb.orbital_host]

        initialize_menues.cb_menu(self.menu_handler, 
                                    cb, 
                                    host_cb,
                                    list(cbs.values()),
                                    self.get_values("default_font bold skip_quotes"),
                                    self.climate_images,
                                    self.invoke_command,
                                    self.game_settings,
                                    self.menu_settings,
                                    self.images,
                                    self.switch_atm_menu_mode)

    def switch_atm_menu_mode(self):
        if self.menu_settings["atmosphere_menu_mode"] == "units":
            self.menu_settings["atmosphere_menu_mode"] = "percentage"
        else:
            self.menu_settings["atmosphere_menu_mode"] = "units"

        self._init_cb_menu_wrapper()
        


if __name__ == "__main__":
    game = Game()
    game.main()
