import pygame
from renderer import Renderer
from scoreManger import ScoreManager


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

    score_manager = ScoreManager()
    return renderer, clock, score_manager


if __name__ == "__main__":
    settings = config()

    
    renderer, clock, score_manager = initialize(settings["width"],settings["height"])
    running = True
    
    # Game loop
    while running:
        squeeze_triggered = False
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                squeeze_triggered = True
        
        if squeeze_triggered:
            # TODO: Get actual game state (e.g., is current_item fresh_fruit?)
            is_correct_target = True 
            
            # TODO: Pull this from compensationDetection.py
            compensation_detected = False 
            
            result = score_manager.process_grip(is_correct_target, compensation_detected)
            

            # Note: You also need to trigger the hand.start_squeezing() animation here!
        
        renderer.render_frame(width=settings["width"],height=settings["height"], score=score_manager.total_score)
        clock.tick(settings["fps"])
    
    pygame.quit()

