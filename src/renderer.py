import pygame
class Renderer:
    def __init__(self , width, height):
        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Grip Fruit")

        self.colors = [(40,200,155),(0,0,0)]

        self.font = pygame.font.SysFont(None , 48)

    def drawBackground(self, width , height):
        # self.screen.fill(self.colors[0])
        # Or if using an image:
        background = pygame.image.load("..\\assets\images\Background.png").convert()
        background = pygame.transform.scale(background, (width,height))
        self.screen.blit(background, (0, 0))
    def drawItems(self, items):
        pass
    def drawUi(self, score):
        scoreLabel=self.font.render(str(score), True , self.colors[1])
        self.screen.blit(scoreLabel, (150, 150))
        pass
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