from random import choice

import pygame

POPUP_STYLES = {
            "perfect":  ((0,   230, 118), (0,   51,  32)),
            "good":     ((255, 214,   0), (61,  46,   0)),
            "motivate": ((255, 109,   0), (61,  26,   0)),
            "penalty":  ((255,  23,  68), (61,   0,  16)),
        }


POPUP_PHRASES = {
    "perfect":  [
        "Perfect!", 
        "Beautiful movement!", 
        "Excellent control!", 
        "Spot on!", 
        "Outstanding!", 
        "Just right!"
    ],
    "good":     [
        "Good job!", 
        "Nice work!", 
        "Well done!", 
        "Keep it up!", 
        "Great effort!", 
        "That's the way!"
    ],
    "motivate": [
        "Take your time.", 
        "You're doing great!", 
        "Keep going!", 
        "Every squeeze helps!", 
        "You've got this!"
    ],
    "penalty":  [
        "Oops, let's try again!", 
        "Careful there!", 
        "Wait for the fresh fruit!", 
        "Not quite!", 
        "Almost!"
    ],
}
class Renderer:
    def __init__(self , width, height):
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grip Fruit")

        self.colors = [(40,200,155),(0,0,0),(0,0,50)]
        self.font_score = pygame.font.SysFont("impact", 58)
        self.font_label = pygame.font.SysFont("arial",  16, bold=True)
        self.font_popup = pygame.font.SysFont("arial", 32, bold=True)
        
        self._popups = []   # list of [x, y, text, type, frames_left]

        

    def drawBackground(self, width , height):
        # self.screen.fill(self.colors[0])

        background = pygame.image.load("assets\images\Background.png").convert()
        background = pygame.transform.scale(background, (width,height))
        self.screen.blit(background, (0, 0))
    def drawItems(self, items):
        pass
    def drawUi(self, score):
        card_x, card_y = 30, 24
        card_w, card_h = 200, 100
 
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, self.colors[0], (0, 0, card_w, card_h), border_radius=16)
        # Border
        pygame.draw.rect(card_surf, self.colors[1],  (0, 0, card_w, card_h), border_radius=16, width=2)
        self.screen.blit(card_surf, (card_x, card_y))
 
        # "SCORE" label
        label = self.font_label.render("SCORE", True, self.colors[2])
        self.screen.blit(label, (card_x + 14, card_y + 10))
 
        # Score number
        score_surf = self.font_score.render(str(score), True, self.colors[2])
        nx = card_x + (card_w - score_surf.get_width()) // 2
        ny = card_y + 30
        self.screen.blit(score_surf, (nx, ny))

    def showPopUp(self, x, y, popup_type):
        text = choice(POPUP_PHRASES.get(popup_type, ["..."]))
        self._popups.append([x, y, text, popup_type, 20])  # 90 frames duration

    def _draw_popups(self):
        # p is [x, y, text, type, frames_left]
        for p in self._popups:
            backG, labelcolor = POPUP_STYLES.get(p[3], POPUP_STYLES["good"])
            surf = self.font_popup.render(p[2], True, labelcolor)
            pad, r = 12, 10
            rect = pygame.Rect(p[0] - surf.get_width()//2 - pad, p[1] - surf.get_height()//2 - pad,
                            surf.get_width() + pad*2, surf.get_height() + pad*2)
            pygame.draw.rect(self.screen, backG, rect, border_radius=r)
            self.screen.blit(surf, (rect.x + pad, rect.y + pad))
            p[4] -= 1
        self._popups = [p for p in self._popups if p[4] > 0]



    def showCameraFeed(self):
        pass


    def render_frame(self,width, height, score = 0,  hand = None, active_items = None, level =None):
        """
        The master method.
        """
        self.drawBackground(width=width, height=height)
        if hand:
            hand.draw(self.screen)
        if active_items:
            active_items.draw(self.screen)
        
        self.drawUi(score)
        self._draw_popups()
        pygame.display.flip()