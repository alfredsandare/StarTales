import json
from PhoenixGUI import *
import pygame

PATH = __file__[:-7]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 800))
        self.menu_handler = MenuHandler(self.screen, 1)

        with open(PATH + "data/menues.json") as file:
            data = json.load(file)
            print(data)

    def main(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 0))

            events = pygame.event.get()
            self.menu_handler.update(events, self.screen)
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.main()