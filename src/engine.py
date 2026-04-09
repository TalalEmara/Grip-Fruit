import pygame
from renderer import Renderer


def config():
    configuration = {
        "width": 1200,
        "height": 700,
        "fps": 60
    }
    return configuration


def initialize(width, height):
    pygame.init()
    renderer = Renderer(width, height)
    clock = pygame.time.Clock()
    return renderer, clock


if __name__ == "__main__":
    settings = config()

    
    renderer, clock = initialize(settings["width"],settings["height"])
    running = True
    
    # Game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Update game state here
        
        renderer.render_frame(width=settings["width"],height=settings["height"], score=15)
        clock.tick(settings["fps"])
    
    pygame.quit()

