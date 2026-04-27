import pygame
import json
from datetime import datetime, timezone
from pathlib import Path
from random import choice
from hand import Hand
from item import STILL_IMAGE_PATHS, FruitItem, FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP, ITEM_SIZE
from levelManager import LevelManager, make_challenge_level, make_standard_level, make_warmup_level
from renderer import Renderer
from scoreManger import ScoreManager
from inputHandler import InputHandler
from startScreen import StartScreen
from EndScreen import show_end_screen
from experimentPickerScreen import ExperimentPickerScreen
from compensationDetection import compensationDetection


def config():
    configuration = {
        "width": 1200,
        "height": 700,
        "fps": 60
    }
    return configuration


def initialize(width, height, level_difficulty):
    pygame.init()
    renderer = Renderer(width, height)
    clock = pygame.time.Clock()

    score_manager = ScoreManager()

    if level_difficulty["name"] == "EASY":
        level = make_warmup_level()
    elif level_difficulty["name"] == "MEDIUM":
        level = make_standard_level()
    elif level_difficulty["name"] == "HARD":
        level = make_challenge_level()
    elif level_difficulty["name"] == "CUSTOM":
        level = LevelManager(
            level_id=4,
            level_name="Custom",
            item_timeout=level_difficulty["item_timeout"],
            spawn_delay=level_difficulty["spawn_delay"],
            total_items=level_difficulty["total_items"],
        )
    else:
        level = make_standard_level()

    level.start()
    renderer._start_ticks = pygame.time.get_ticks()
    hand_y = height - 120
    fruit_rect = pygame.Rect((width - ITEM_SIZE) // 2, hand_y - ITEM_SIZE, ITEM_SIZE, ITEM_SIZE)
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


def game_loop(settings, level_difficulty):
    renderer, clock, score_manager,hand, level, currentItem  = initialize(settings["width"],settings["height"], level_difficulty)
    input_handler = InputHandler(serial_port='COM3', baudrate=9600)

    # Compensation detection — camera opened once for the whole session
    comp_detector = compensationDetection(camera_index=0)

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
        # Grab a camera frame every tick (non-blocking) so check_for_compensation
        # always has a fresh frame ready the moment a squeeze fires.
        comp_detector.update_feed()

        # InputHandler handles both keyboard Space and serial squeeze input.
        input_handler.update()
        if not input_handler.running:
            running = False
            
        squeeze_triggered = input_handler.squeeze_triggered

        if squeeze_triggered:
            if currentItem and currentItem.is_on_screen and not currentItem.is_being_squeezed:
                hand.start_squeezing(currentItem.fruit_type)
                currentItem.squeeze()
                # Check compensation only at the moment of the squeeze
                compensation_detected = comp_detector.check_for_compensation()
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
            # Reset detector state now that the item has been passed/expired
            comp_detector.compensation_detected = False

        if level.is_complete and currentItem is None:
            running = False
            continue
        
        
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
    comp_detector.cleanup()
    return score_manager.get_clinical_summary()


def save_summary_json(summary, level_difficulty):
    experiments_dir = Path(__file__).resolve().parent.parent / "data" / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = experiments_dir / f"exp-{timestamp}.json"
    suffix = 1
    while file_path.exists():
        file_path = experiments_dir / f"exp-{timestamp}-{suffix}.json"
        suffix += 1

    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "difficulty": level_difficulty,
        "summary": summary,
    }
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(file_path)


if __name__ == "__main__":
    settings = config()
    
    while True:
        pygame.init()
        picker = ExperimentPickerScreen(settings["width"], settings["height"])
        selection_type, selected_summary = picker.run()
        pygame.quit()

        if selection_type == "quit":
            break

        if selection_type == "saved":
            pygame.init()
            screen = pygame.display.set_mode((settings["width"], settings["height"]))
            action = show_end_screen(screen, selected_summary)
            pygame.quit()
            if action == "quit":
                break
            continue

        start_screen = StartScreen()
        level_difficulty = start_screen.run()
        if not level_difficulty:
            continue

        summary = game_loop(settings, level_difficulty)
        saved_path = save_summary_json(summary, level_difficulty)
        print(f"Experiment summary saved to: {saved_path}")

        screen = pygame.display.set_mode((settings["width"], settings["height"]))
        action = show_end_screen(screen, summary)
        if action == "quit":
            break
    
    pygame.quit()


