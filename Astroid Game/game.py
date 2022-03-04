import pygame
from pygame import joystick
from StateManager import Stage_Manger
from pygame.constants import DOUBLEBUF, HWSURFACE, RESIZABLE
import play
import os



pygame.init()
pygame.font.init()
pygame.display.init()
pygame.joystick.init()

joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]


#Camera position
  


WIDTH, HEIGHT = 512, 288
FPS = 60
high_score = 0

camera_x = 0 
camera_y = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE|DOUBLEBUF|RESIZABLE)
fake_screen = screen.copy()
pic = pygame.surface.Surface((50, 50)) 
pic.fill((255, 100, 200))

#State management

sm = Stage_Manger()
file = open('scores.txt', 'r')


#For timing

lastTime = 0
deltaTime = 0

#Assets

SPRITE_SHEET = pygame.image.load(os.path.join('Assets', 'Sprite Sheet.png')).convert_alpha()
BACKGROUND = pygame.image.load(os.path.join('Assets', 'Space_bg.png')).convert_alpha()
EXPLOSION = pygame.image.load(os.path.join('Assets', 'Explosion2.png')).convert_alpha()

explosion_sfx = pygame.mixer.Sound(os.path.join('Assets', 'Explosion.wav'))
shoot_sfx = pygame.mixer.Sound(os.path.join('Assets', 'Shoot_FX.wav'))

pygame.mixer.music.load(os.path.join('Assets', 'Chill Menu.mp3'))
pygame.mixer.music.set_volume(0.4)

#Initialize everything 

def init():
    sm.set_state(play.Menu(sm))


#Load score

def load_score():

    global high_score
    high_score = int(file.read())
    print("Hey, just loaded")

#update everything here

def update(dt):
    sm.update(dt)

#draw everything here
def draw(surf):
    sm.render(surf)


def main():

    is_game_running = True
    global screen, fake_screen, lastTime, deltaTime

    clock = pygame.time.Clock()
    lastTime = pygame.time.get_ticks()

    init()
    load_score()
  

    while (is_game_running):

        clock.tick(FPS)
        for event in pygame.event.get():

            if(event.type == pygame.QUIT):
                is_game_running = False


            if(event.type == pygame.JOYBUTTONDOWN):
                print("Joystick Pressed!")

            sm.processInput(event)

            if(event.type == pygame.VIDEORESIZE):
                screen = pygame.display.set_mode((event.w, event.h), HWSURFACE|DOUBLEBUF|RESIZABLE)
    

        #Time processing

        
        deltaTime = (pygame.time.get_ticks() - lastTime)/1000
        deltaTime *= FPS
        lastTime = pygame.time.get_ticks()



        fake_screen.fill((0 , 0, 64), pygame.Rect(0, 0, screen.get_width(), screen.get_height()))
      

        #Draw and update the game 
        update(deltaTime)
        draw(fake_screen)
     


        #Draw the surface on the screen
        screen.blit( pygame.transform.scale(fake_screen, (screen.get_width(), screen.get_height())), (0, 0))
        pygame.display.flip()
        
if __name__ == "__main__":
    main()
