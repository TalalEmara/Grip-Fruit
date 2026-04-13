import pygame
from item import STILL_IMAGE_PATHS, FruitItem, FRESH_FRUIT, ITEM_SIZE
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


def create_dummy_item(screen_w, screen_h):
    # Temporary placeholder image until real assets/pipeline are wired.
    img_data = {name: pygame.image.load(path).convert_alpha() for name, path in STILL_IMAGE_PATHS.items()}
    
    dummy_surface = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
    dummy_surface.fill((255, 220, 80))
    hand_y = screen_h - 120
    return FruitItem(FRESH_FRUIT, img_data[FRESH_FRUIT], screen_w, hand_y, ITEM_SIZE)


if __name__ == "__main__":
    settings = config()

    
    renderer, clock, score_manager = initialize(settings["width"],settings["height"])
    running = True
    
    currentItem = create_dummy_item(settings["width"], settings["height"])
    
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
            if currentItem and currentItem.is_on_screen and not currentItem.is_being_squeezed:                
                currentItem.squeeze()

                compensation_detected = False
                result = score_manager.process_grip(currentItem.fruit_type == FRESH_FRUIT, compensation_detected)
                
                

            # Note: You also need to trigger the hand.start_squeezing() animation here!
        currentItem.update_fruit()

        renderer.render_frame(
            width=settings["width"],
            height=settings["height"],
            score=score_manager.total_score,
            active_items=currentItem,
        )
        clock.tick(settings["fps"])
    
    pygame.quit()

