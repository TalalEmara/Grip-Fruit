import pygame
from random import choice
from hand import Hand
from item import STILL_IMAGE_PATHS, FruitItem, FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP, ITEM_SIZE
from levelManager import make_challenge_level, make_standard_level, make_warmup_level
from renderer import Renderer
from scoreManger import ScoreManager
from inputHandler import InputHandler

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

    level = make_standard_level()
    level.start()
    renderer._start_ticks = pygame.time.get_ticks()
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
    input_handler = InputHandler(serial_port='COM10', baudrate=9600)

    # img_data = {name: pygame.image.load(path).convert_alpha() for name, path in STILL_IMAGE_PATHS.items()}
    img_data = {FRESH_FRUIT: None, ROTTEN_FRUIT: None, KETCHUP: None}
    hand_y = settings["height"] - 120
    running = True
    
    pygame.mixer.init()
    pygame.mixer.music.load(r"src\assets\sound effects\grip fruit background music.mp3")
    pygame.mixer.music.set_volume(0.4) #sound level
    pygame.mixer.music.play(-1) #always in loop

    # Game loop
    while running:
        squeeze_triggered = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                squeeze_triggered = True

        input_handler.update()
        if not input_handler.running:
            running = False
            
        squeeze_triggered = input_handler.squeeze_triggered

        if squeeze_triggered:
            if currentItem and currentItem.is_on_screen and not currentItem.is_being_squeezed:
                hand.start_squeezing(currentItem.fruit_type)
                currentItem.squeeze()
                compensation_detected = False
                result = score_manager.process_grip(
                    currentItem.fruit_type == FRESH_FRUIT, compensation_detected
                )

                event_to_popup = {
                    "score_perfect":        "good",
                    "score_perfect_streak": "perfect",
                    "score_compensated":    "motivate",
                    "penalty_wrong_object": "penalty",
                }
                popup_type = event_to_popup.get(result["event_type"], "good")
 
                renderer.showPopUp(
                    x=settings["width"]  * 2 // 3,
                    y=settings["height"] * 4 // 5,
                    popup_type=popup_type,
                )
        
        if currentItem:
            currentItem.update_fruit(timeout=level.get_item_timeout())
        
        shouldSpawn = level.update(currentItem)

        if currentItem and not currentItem.is_on_screen:
            currentItem = None          # clear slot after level.update() counts it
        
        
        if shouldSpawn:
            itemType = level.next_item_type()
            currentItem = FruitItem(itemType, img_data[itemType], settings["width"], hand_y, ITEM_SIZE)
            hand.set_fruit(itemType)

        hand.update_hand()
        renderer.render_frame(
            width=settings["width"],
            height=settings["height"],
            score=score_manager.total_score,
            active_items=currentItem,
            hand=hand,
            level=level,
        )
    clock.tick(settings["fps"])
    input_handler.close()
    pygame.quit()

