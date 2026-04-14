import pygame
class Renderer:
    def __init__(self , width, height):
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grip Fruit")

        self.colors = [(40,200,155),(0,0,0),(0,0,50)]
        self.font_score = pygame.font.SysFont("impact", 58)
        self.font_label = pygame.font.SysFont("arial",  16, bold=True)
 

    def drawBackground(self, width , height):
        # self.screen.fill(self.colors[0])
        # Or if using an image:
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
    def showPopUp(self, text, type):
        pass
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
        
        pygame.display.flip()