import pygame
from pygame import Surface
from colorama import Fore, Style
from CLIRender.dat import Vector2

CHAR_WIDTH, CHAR_HEIGHT = 12, 20
FONT_NAME = "Courier New"  #monospace font

COLOR_MAP = {
    Fore.BLACK: (0, 0, 0),
    Fore.RED: (255, 0, 0),
    Fore.GREEN: (0, 255, 0),
    Fore.YELLOW: (255, 255, 0),
    Fore.BLUE: (0, 0, 255),
    Fore.MAGENTA: (255, 0, 255),
    Fore.CYAN: (0, 255, 255),
    Fore.WHITE: (255, 255, 255),
}

class PygameCanvas:
    def __init__(self, dimensions, layers=1, _unused=None):
        pygame.init()
        self.dimensions = dimensions  # Vector2(40, 24)
        self.screen_width, self.screen_height = pygame.display.get_desktop_sizes()[0]
        self.surface = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.layers = [{} for _ in range(layers)]
        self.bg_color = (0, 0, 0)

        # Calculate char size dynamically
        self.char_w = self.screen_width // self.dimensions.x
        self.char_h = self.screen_height // self.dimensions.y

        # Use nearest multiple of 2 for size (optional)
        font_size = min(self.char_w, self.char_h)
        self.font = pygame.font.SysFont("Courier New", font_size, bold=True)


    def clear_layer(self, layer):
        self.layers[layer] = {}

    def set_char(self, layer, location, char, col):
        self.layers[layer][(location.x, location.y)] = (char, col)

    def set_string(self, layer, location, string, col):
        for i, char in enumerate(string):
            self.set_char(layer, Vector2(location.x + i, location.y), char, col)

    def render_blank(self):
        self.surface.fill(self.bg_color)
        for layer in self.layers:
            for (x, y), (char, col) in layer.items():
                self.draw_char(x, y, char, col)
        pygame.display.flip()
        self.clock.tick(60)

    def draw_char(self, x, y, char, col):
        raw_color = (255, 255, 255)
        for fg in COLOR_MAP:
            if fg in col:
                raw_color = COLOR_MAP[fg]
    
        text = self.font.render(char, True, raw_color)
        self.surface.blit(text, (x * self.char_w, y * self.char_h))
    
    def render_all(self):
        self.render_blank()

