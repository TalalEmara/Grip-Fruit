import cv2
import pygame

HAND_IMAGE_PATH = r"E:\pygame\Grip-Fruit\src\assets\images\hand.png"
HAND_SIZE = 150

SQUEEZE_VIDEO_PATHS = {
    "fresh_fruit":  r"E:\pygame\Grip-Fruit\src\assets\animated videos\animated lemon.mp4",
    "rotten_fruit": r"E:\pygame\Grip-Fruit\src\assets\animated videos\animated rotten fruit.mp4",
    "ketchup":      r"E:\pygame\Grip-Fruit\src\assets\animated videos\animated ketchup.mp4",
}

STILL = "still"
SQUEEZING = "squeezing"

class Hand:
    def __init__(self, screen_w, screen_h, fruit_rect):
        self.size = HAND_SIZE
        self.still_image = pygame.transform.scale(
            pygame.image.load(HAND_IMAGE_PATH).convert_alpha(), (self.size, self.size)
        )

        self.all_squeeze_frames = {
            fruit_type: self._load_frames(path, (self.size, self.size))
            for fruit_type, path in SQUEEZE_VIDEO_PATHS.items()
        }

        self.fruit_rect = fruit_rect
        self.rect = pygame.Rect((screen_w - self.size) // 2, screen_h - self.size, self.size, self.size)

        self.squeeze_frames = []
        self.current_frame = 0
        self.state = STILL

    def _load_frames(self, video_path, size):
        cap = cv2.VideoCapture(video_path)
        frames = []
        while True:
            success, frame = cap.read()
            if not success: 
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, size)
            surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            surface.set_colorkey((0, 0, 0))
            frames.append(surface.convert_alpha())
        cap.release()
        return frames

    def start_squeezing(self, fruit_type):
        if self.state != STILL: 
            return
        self.squeeze_frames = self.all_squeeze_frames[fruit_type]
        self.current_frame = 0
        self.state = SQUEEZING

    def update_hand(self):
        if self.state != SQUEEZING: 
            return
        self.current_frame += 1
        if self.current_frame >= len(self.squeeze_frames):
            self.state = STILL
            self.current_frame = 0

    def draw(self, screen):
        if self.state == SQUEEZING:
            frame = self.squeeze_frames[min(self.current_frame, len(self.squeeze_frames) - 1)]
            screen.blit(frame, self.fruit_rect)
        else:
            screen.blit(self.still_image, self.rect)