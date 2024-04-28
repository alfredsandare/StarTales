import json
from PhoenixGUI import *
import pygame

PATH = __file__[:-7]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 800))
        self.menu_handler = MenuHandler(self.screen, 1)

        menues_data = self.load_menues_data()
        self.menu_handler.load_data_from_dict(menues_data, None)

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
            return [100, 100]
        
        return ""

if __name__ == "__main__":
    game = Game()
    game.main()