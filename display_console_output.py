import pygame
import threading
import sys
import io
import pyte

from credits import run_credits

class StreamInterceptor(io.TextIOBase):
    def __init__(self, screen):
        super().__init__()
        self.stream = pyte.Stream(screen)

    def write(self, data):
        self.stream.feed(data)

    def flush(self):
        pass

def run_in_thread(writer):
    sys.stdout = writer
    try:
        run_credits()
    finally:
        sys.stdout = sys.__stdout__

def main():
    rows, cols = 40, 80
    screen = pyte.Screen(cols, rows)
    stream_writer = StreamInterceptor(screen)

    thread = threading.Thread(target=run_in_thread, args=(stream_writer,))
    thread.start()

    pygame.init()
    font = pygame.font.Font(pygame.font.match_font('monospace'), 16)
    screen_size = (font.size("#" * cols)[0], font.get_linesize() * rows)
    screen_surface = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Pyte + Pygame Terminal")

    clock = pygame.time.Clock()

    running = True
    while running:
        screen_surface.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simple ANSI 16-color map (adjust as needed)
        COLOR_MAP = {
            "black": (0, 0, 0),
            "red": (170, 0, 0),
            "green": (0, 170, 0),
            "yellow": (170, 85, 0),
            "blue": (0, 0, 170),
            "magenta": (170, 0, 170),
            "cyan": (0, 170, 170),
            "white": (170, 170, 170),
        
            "bright_black": (85, 85, 85),
            "bright_red": (255, 85, 85),
            "bright_green": (85, 255, 85),
            "bright_yellow": (255, 255, 85),
            "bright_blue": (85, 85, 255),
            "bright_magenta": (255, 85, 255),
            "bright_cyan": (85, 255, 255),
            "bright_white": (255, 255, 255),
        }
        
        for y in range(rows):
            row = screen.buffer.get(y, {})
            for x in range(cols):
                cell = row.get(x)
                if cell:
                    char = cell.data
                    fg_color = COLOR_MAP.get(cell.fg, (255, 255, 255))
                    if cell.bold:
                        fg_color = tuple(min(255, int(c * 1.4)) for c in fg_color)
        
                    # Optional: implement background color fill
                    # bg_color = COLOR_MAP.get(cell.bg, (0, 0, 0))
                    # pygame.draw.rect(screen_surface, bg_color, ...)
        
                    surface = font.render(char, True, fg_color)
                    screen_surface.blit(
                        surface,
                        (x * font.size(" ")[0], y * font.get_linesize())
                    )
        


        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
