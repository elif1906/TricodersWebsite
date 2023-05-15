import pygame
import sys
from settings import *
from choose import Loading
from choose import Choose
import ui


class Menu1:
    def __init__(self1, surface):
        self1.surface = surface
      
        
        self1.choose = Loading()
        
        self1.click_sound = pygame.mixer.Sound(f"Assets/Sounds/slap.wav")


    def draw(self1):
        
       
        self1.choose.draw(self1.surface)
       
        # draw title
        ui.draw_text(self1.surface, GAME_TITLE, (SCREEN_WIDTH//2, 120), COLORS["title"], font=FONTS["big"],
                    shadow=True, shadow_color=(255,255,255), pos_mode="center")
        
    def update(self1):

        self1.draw()
       
         
       