import json
from PhoenixGUI import *
import pygame
from PhoenixGUI.util import update_pos_by_anchor
from planet import Planet

PATH = __file__[:-7]

class Game:
    def __init__(self):
        self.frame_size = (800, 800)
        self.screen = pygame.display.set_mode(self.frame_size)
        self.menu_handler = MenuHandler()

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, None)
        self.menu_handler.add_font_path(PATH + "data\\fonts\\")

        self.planet = Planet()

    def main(self):
        #self.menu_handler.menues["main_menu"].activate()
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.planet.surface, (0, 110))
            self.screen.blit(self.planet.get_frame(), (0, 0))

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen)
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

if __name__ == "__main__":
    game = Game()
    game.main()