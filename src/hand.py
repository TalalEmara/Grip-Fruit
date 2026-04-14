import pygame
import os

HAND_SIZE = 350

SQUEEZE_FRAME_DIRS = {
    "fresh_fruit":  r"src\assets\frames\lemon frames",
    "rotten_fruit": r"src\assets\frames\rotten frames",
    "ketchup":      r"src\assets\frames\ketchup frames",
}

STILL = "still"
SQUEEZING = "squeezing"

class Hand:
    def __init__(self, screen_w, screen_h, fruit_rect=None):
        self.size = HAND_SIZE
        self.all_squeeze_frames = {
            fruit_type: self._load_frames(folder, (self.size, self.size))
            for fruit_type, folder in SQUEEZE_FRAME_DIRS.items()
        }

        self.rect = pygame.Rect((screen_w - self.size) // 2, screen_h - self.size, self.size, self.size)

        self.squeeze_frames = []
        self.current_frame = 0
        self.state = STILL
        self.current_fruit_type = list(SQUEEZE_FRAME_DIRS.keys())[0]  # default to first

    def _load_frames(self, folder_path, size):
        frames = []
        files = sorted(
            f for f in os.listdir(folder_path)
            if f.lower().endswith(".png")
        )
        for filename in files:
            img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
        return frames

    def set_fruit(self, fruit_type):
        self.current_fruit_type = fruit_type

    def start_squeezing(self, fruit_type):
        if self.state != STILL: 
            return
        self.squeeze_frames = self.all_squeeze_frames[fruit_type][1:]  # skip frame 0
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
            screen.blit(frame, self.rect)
        else:
            still_frame = self.all_squeeze_frames[self.current_fruit_type][0]
            screen.blit(still_frame, self.rect)