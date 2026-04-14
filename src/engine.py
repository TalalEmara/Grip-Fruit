import pygame
from hand import Hand
from item import STILL_IMAGE_PATHS, FruitItem, FRESH_FRUIT, ITEM_SIZE
from levelManager import make_challenge_level, make_warmup_level
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

    level = make_challenge_level()
    level.start()
    hand_y = height - 120
    fruit_rect = pygame.Rect((settings["width"] - ITEM_SIZE) // 2, hand_y - ITEM_SIZE, ITEM_SIZE, ITEM_SIZE)
    hand = Hand(width, height, fruit_rect)
    currentItem = None
    return renderer, clock, score_manager,hand, level, currentItem

# for testing
def create_dummy_item(screen_w, screen_h):
    # Temporary placeholder image until real assets/pipeline are wired.
    dummy_surface = pygame.Surface((ITEM_SIZE, ITEM_SIZE), pygame.SRCALPHA)
    dummy_surface.fill((255, 220, 80))
    hand_y = screen_h - 120
    return FruitItem(FRESH_FRUIT, dummy_surface, screen_w, hand_y, ITEM_SIZE)


if __name__ == "__main__":
    settings = config()
    renderer, clock, score_manager,hand, level, currentItem  = initialize(settings["width"],settings["height"])
    img_data = {name: pygame.image.load(path).convert_alpha() for name, path in STILL_IMAGE_PATHS.items()}
    hand_y = settings["height"] - 120
    running = True
    
    
    # Game loop
    while running:
        squeeze_triggered = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                squeeze_triggered = True

        if squeeze_triggered:
            if currentItem and currentItem.is_on_screen and not currentItem.is_being_squeezed:
                hand.start_squeezing(currentItem.fruit_type)
                currentItem.squeeze()
                compensation_detected = False
                result = score_manager.process_grip(
                    currentItem.fruit_type == FRESH_FRUIT, compensation_detected
                )

        shouldSpawn = level.update(currentItem)
        if shouldSpawn:
            itemType = level.next_item_type()
            currentItem = FruitItem(itemType, img_data[itemType], settings["width"], hand_y, ITEM_SIZE)

        if currentItem:
            currentItem.update_fruit(timeout=level.get_item_timeout())
            if not currentItem.is_on_screen:
                currentItem = None          # clear slot → level.update() counts it and starts spawn timer
        hand.update_hand()
        renderer.render_frame(
            width=settings["width"],
            height=settings["height"],
            score=score_manager.total_score,
            active_items=currentItem,
            hand=hand,
        )
    clock.tick(settings["fps"])
    pygame.quit()

