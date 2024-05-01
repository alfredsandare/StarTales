import json
from PhoenixGUI import *
import pygame
from PhoenixGUI.util import update_pos_by_anchor

PATH = __file__[:-7]

class Game:
    def __init__(self):
        self.frame_size = (800, 800)
        self.screen = pygame.display.set_mode(self.frame_size)
        self.menu_handler = MenuHandler(self.screen, 1)

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, None)
        self.menu_handler.add_font_path(PATH + "data\\fonts\\")

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

        return json.loads(final_data)

    def main(self):
        self.menu_handler.menues["main_menu"].activate()
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen)
            pygame.display.flip()
            clock.tick(60)

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