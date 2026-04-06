import pygame
import random
from hand import Hand, STILL, HAND_SIZE

pygame.init()

FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP = "fresh_fruit", "rotten_fruit", "ketchup"
POINTS = {FRESH_FRUIT: 10, ROTTEN_FRUIT: -10, KETCHUP: -5}

STILL_IMAGE_PATHS = {
    FRESH_FRUIT:  r"E:\pygame\Grip-Fruit\src\assets\images\lemon.png",
    ROTTEN_FRUIT: r"E:\pygame\Grip-Fruit\src\assets\images\lemon rotten.png",
    KETCHUP:      r"E:\pygame\Grip-Fruit\src\assets\images\ketchup.png",
}

ITEM_SIZE = 150

class FruitItem:
    def __init__(self, fruit_type, fruit_still_image, screen_w, hand_y, size=150):
        self.fruit_type = fruit_type
        self.points = POINTS[fruit_type]
        self.size = size
        self.fruit_still_image = pygame.transform.scale(fruit_still_image, (self.size, self.size))
        
        self.x = (screen_w - self.size) // 2
        self.y = hand_y - self.size
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        self.is_on_screen = True
        self.is_being_squeezed = False
        self.timer = 0

    def squeeze(self):
        if not self.is_on_screen or self.is_being_squeezed: 
            return 0
        self.is_being_squeezed = True
        return self.points

    def update_fruit(self):
        if not self.is_on_screen: 
            return
        if self.is_being_squeezed:
            self.is_on_screen = False
        else:
            self.timer += 1
            if self.timer >= 100:
                self.is_on_screen = False

    def draw(self, screen):
        if not self.is_on_screen or self.is_being_squeezed: 
            return
        screen.blit(self.fruit_still_image, self.rect)

#Test

# if __name__ == "__main__":
#     WIDTH, HEIGHT = 600, 700
#     screen = pygame.display.set_mode((WIDTH, HEIGHT))
#     clock = pygame.time.Clock()
#     font = pygame.font.SysFont("Arial", 25)

#     img_data = {name: pygame.image.load(path).convert_alpha() for name, path in STILL_IMAGE_PATHS.items()}

#     hand_y = HEIGHT - HAND_SIZE
#     fruit_rect = pygame.Rect((WIDTH - ITEM_SIZE) // 2, hand_y - ITEM_SIZE, ITEM_SIZE, ITEM_SIZE)
#     hand = Hand(WIDTH, HEIGHT, fruit_rect=fruit_rect)

#     def create_new_fruit():
#         item_type = random.choice([FRESH_FRUIT, ROTTEN_FRUIT, KETCHUP])
#         return FruitItem(item_type, img_data[item_type], WIDTH, hand_y, ITEM_SIZE)

#     current_item = create_new_fruit()
#     score = 0
#     wait_time = 0

#     running = True
#     while running:
#         screen.fill((255, 255, 255))

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT: 
#                 running = False
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
#                 if current_item and current_item.is_on_screen and not current_item.is_being_squeezed:
#                     score += current_item.squeeze()
#                     hand.start_squeezing(current_item.fruit_type)

#         if current_item:
#             current_item.update_fruit()
#             current_item.draw(screen)
#             if not current_item.is_on_screen:
#                 if hand.state == STILL:
#                     current_item = None
#                     wait_time = 60
#         else:
#             wait_time -= 1
#             if wait_time <= 0:
#                 current_item = create_new_fruit()

#         hand.update_hand()
#         hand.draw(screen)

#         score_text = font.render(f"Score: {score}", True, (0, 0, 0))
#         screen.blit(score_text, (10, 10))
        
#         pygame.display.flip()
#         clock.tick(60)

#     pygame.quit()